import json
import os
import time
import datetime
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from tqdm import tqdm
from peewee import fn

from src.models import Email, db
from src.config import AppConfig

class RuleGenerator:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_rules(self, top_n: Optional[int] = 200) -> Dict[str, Any]:
        """
        1. Query Top N senders from DB with metadata (count, last date).
        2. Merge with existing rules.json (Manual edits override AI).
        3. Call AI for NEW senders.
        4. Save to rules.json.
        """
        # Load existing rules to preserve manual edits
        existing_rules = {}
        if os.path.exists("rules.json"):
            try:
                with open("rules.json", "r", encoding="utf-8") as f:
                    existing_rules = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading rules.json: {e}")

        # 1. Get Senders with metadata
        query = (Email
                 .select(Email.sender, 
                         fn.COUNT(Email.id).alias('count'),
                         fn.MAX(Email.date).alias('last_date'))
                 .group_by(Email.sender)
                 .order_by(fn.COUNT(Email.id).desc()))
        
        if top_n:
            query = query.limit(top_n)
        
        db_senders = {row.sender: {
            "count": row.count,
            "last_date": row.last_date.isoformat() if isinstance(row.last_date, datetime.datetime) else str(row.last_date)
        } for row in query if row.sender}
        
        if not db_senders:
            self.logger.info("No senders found in DB.")
            return {}

        # Identify senders that need AI classification (not in existing_rules or marked as 'AI' and we want to refresh)
        new_senders = []
        final_rules = {}

        for sender, meta in db_senders.items():
            if sender in existing_rules:
                # Keep existing (Manual or previous AI)
                old_rule = existing_rules[sender]
                # Migration: if old rule is just a string (category name), convert to dict
                if isinstance(old_rule, str):
                    final_rules[sender] = {
                        "category": old_rule,
                        "source": "Manual_Migrated"
                    }
                else:
                    final_rules[sender] = old_rule
                
                # Update metadata
                final_rules[sender].update(meta)
            else:
                new_senders.append(sender)
                final_rules[sender] = {
                    "category": "Unclassified",
                    "source": "AI_PENDING",
                    **meta
                }

        if new_senders:
            self.logger.info(f"Asking AI to classify {len(new_senders)} NEW unique senders...")
            ai_results = self._call_ai_batch(new_senders)
            
            for sender, category in ai_results.items():
                if sender in final_rules:
                    final_rules[sender]["category"] = category
                    final_rules[sender]["source"] = "AI_Generated"

        # 3. Save
        with open("rules.json", "w", encoding="utf-8") as f:
            json.dump(final_rules, f, indent=4, ensure_ascii=False)
            
        self.logger.info(f"Rules updated in rules.json ({len(final_rules)} items).")
        return final_rules

    def _call_ai_batch(self, senders: List[str]) -> Dict[str, str]:
        if not self.model or not senders:
            return {}
            
        prompt = f"""
        You are an elite email organization consultant.
        Objective: Classify the provided list of email sender addresses.
        
        Categories:
        {json.dumps(AppConfig.CATEGORIES, indent=2, ensure_ascii=False)}

        Instruction:
        - Return a SINGLE JSON object mapping each sender address to its most appropriate category key.
        - Example: {{"service@paypal.com": "💰_Finance"}}
        - If a sender is highly ambiguous, use "Unclassified".

        Senders to Classify:
        {json.dumps(senders, ensure_ascii=False)}

        IMPORTANT: Return ONLY valid JSON. No conversational text.
        """
        
        try:
            # 4s wait for free tier
            time.sleep(4)
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:

            self.logger.error(f"AI Error: {e}")
            return {}

    def apply_rules(self):
        """Load rules.json and update DB."""
        if not os.path.exists("rules.json"):
            self.logger.warning("rules.json not found.")
            return

        with open("rules.json", "r", encoding="utf-8") as f:
            rules = json.load(f)
            
        self.logger.info("Applying rules to DB...")
        with db.atomic():
            for sender, info in tqdm(rules.items(), desc="Updating DB"):
                category = info.get("category", "Unclassified")
                source = info.get("source", "Manual")
                (Email
                 .update(category=category, is_classified=True, rule_source=source)
                 .where(Email.sender == sender)
                 .execute())
        
        self.logger.info("Rules applied!")
