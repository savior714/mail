import json
import os
import time
import datetime
import logging
from typing import List, Dict, Any, Optional
import re
import google.generativeai as genai
from tqdm import tqdm
from peewee import fn

from src.models import Email, LearnedRule, db
from src.config import AppConfig

class RuleGenerator:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model = None
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.logger.warning("GOOGLE_API_KEY not found. AI classification will be skipped.")

    def generate_rules(self, top_n: Optional[int] = 200, learn: bool = True) -> Dict[str, Any]:
        """
        1. Query Top N senders from DB.
        2. (Optional) Learn/Update Regex patterns from Manual fixes in DB.
        3. Match against Hard Rules and Persistent Learned Rules.
        4. Call AI for NEW senders.
        5. Save to rules.json.
        """
        self.logger.info("🚀 [Learn Rules] Starting Adaptive Learning v2 pipeline...")
        
        # Load existing rules for metadata consistency
        existing_rules = {}
        if os.path.exists("rules.json"):
            try:
                with open("rules.json", "r", encoding="utf-8") as f:
                    existing_rules = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading rules.json: {e}")

        # 1. Adaptive Learning Phase
        if learn:
            self.logger.info("🔍 Step 1: Intelligence Phase - Learning from manual fixes...")
            # GC: Clean up low confidence or stagnant rules first
            deleted = LearnedRule.delete().where(
                (LearnedRule.confidence < 0.3) | 
                (LearnedRule.last_hit_at < datetime.datetime.now() - datetime.timedelta(days=30))
            ).execute()
            if deleted:
                self.logger.info(f"🧹 GC: Removed {deleted} outdated or low-confidence learned rules.")

            new_patterns = self.learn_patterns_from_manual()
            if new_patterns:
                self.logger.info(f"✨ AI generated/optimized {len(new_patterns)} patterns.")
                # Persistence: Update LearnedRule table
                with db.atomic():
                    for pattern, category in new_patterns.items():
                        LearnedRule.get_or_create(
                            pattern=pattern, 
                            defaults={'category': category}
                        )
            
        # Load all learned rules from DB for matching
        persistent_learned_rules = list(LearnedRule.select().where(LearnedRule.confidence > 0.3).order_by(LearnedRule.hit_count.desc()))
        self.logger.info(f"📚 Loaded {len(persistent_learned_rules)} active learned rules from database.")

        # 2. Get Senders with metadata
        self.logger.info(f"📊 Step 2: Fetching top {top_n} senders from database...")
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
            "last_date": row.last_date.isoformat() if isinstance(row.last_date, datetime.datetime) else str(row.last_date),
            "subjects": []
        } for row in query if row.sender}
        
        if not db_senders:
            self.logger.info("❌ No senders found in DB.")
            return {}

        self.logger.info(f"✨ Step 3: Analyzing metadata and sample subjects for {len(db_senders)} unique senders...")
        for sender in db_senders:
            subjects = (Email
                        .select(Email.subject)
                        .where(Email.sender == sender)
                        .order_by(Email.date.desc())
                        .limit(3))
            db_senders[sender]["subjects"] = [s.subject for s in subjects if s.subject]

        final_rules = {}

        for sender, meta in db_senders.items():
            search_text = f"{sender} {' '.join(meta['subjects'])}"
            matched_rule = None

            # Layer 0: Learned Rules (Persistent + DB Backed)
            for lr in persistent_learned_rules:
                if re.search(lr.pattern, search_text, re.I):
                    matched_rule = {
                        "category": lr.category,
                        "reasoning": f"Adaptive Learning Match (Pattern: {lr.pattern})",
                        "source": "Learned"
                    }
                    # Update Lifecycle Stats
                    lr.hit_count += 1
                    lr.last_hit_at = datetime.datetime.now()
                    lr.save()
                    break
            
            if matched_rule:
                final_rules[sender] = {**matched_rule, **meta}
                continue

            # Layer 1: Hard Rules (Regex)
            for category, patterns in AppConfig.HARD_RULES.items():
                matched = False
                for pattern in patterns:
                    if re.search(pattern, search_text, re.I):
                        matched_rule = {
                            "category": category,
                            "reasoning": f"Matched hard rule pattern: {pattern}",
                            "source": "Hard_Rule"
                        }
                        matched = True
                        break
                if matched:
                    break
            
            if matched_rule:
                final_rules[sender] = {**matched_rule, **meta}
            elif sender in existing_rules:
                old_rule = existing_rules[sender]
                if isinstance(old_rule, str):
                    final_rules[sender] = {"category": old_rule, "source": "Manual_Migrated"}
                else:
                    final_rules[sender] = old_rule
                final_rules[sender].update(meta)
            else:
                final_rules[sender] = {"category": "Unclassified", "source": "AI_PENDING", **meta}

        # Identify AI needs
        new_senders = [(s, m["subjects"]) for s, m in final_rules.items() if m.get("source") == "AI_PENDING"]

        if new_senders:
            self.logger.info(f"🤖 Step 4: AI Classification - Requesting analysis for {len(new_senders)} new senders...")
            ai_results = self._call_ai_batch(new_senders)
            
            if not isinstance(ai_results, dict):
                self.logger.error(f"❌ AI returned unexpected format: {type(ai_results)}")
                ai_results = {}

            for sender, result in ai_results.items():
                if sender in final_rules:
                    category = result.get("category", "Unclassified") if isinstance(result, dict) else result
                    reasoning = result.get("reasoning", "") if isinstance(result, dict) else ""
                    final_rules[sender].update({"category": category, "reasoning": reasoning, "source": "AI_Generated"})

        self.logger.info(f"💾 Step 5: Finalizing results and updating rules.json...")
        with open("rules.json", "w", encoding="utf-8") as f:
            json.dump(final_rules, f, indent=4, ensure_ascii=False)
            
        return final_rules

    def learn_patterns_from_manual(self) -> Dict[str, str]:
        """
        Scans DB for manual corrections and asks AI to extract generic regex patterns.
        Uses negative samples for cross-validation to prevent false positives.
        Returns mapping of {regex_pattern: category}.
        """
        # 1. Positive Samples (User corrected to Manual)
        manual_emails = (Email
                        .select(Email.sender, Email.subject, Email.category)
                        .where(Email.rule_source == 'Manual')
                        .order_by(Email.date.desc())
                        .limit(40))
        
        if not manual_emails:
            return {}

        pos_samples = []
        target_categories = set()
        for e in manual_emails:
            target_categories.add(e.category)
            pos_samples.append({
                "sender": e.sender,
                "subject": e.subject,
                "target_category": e.category
            })

        # 2. Negative Samples (Samples from other categories for cross-validation)
        # Fetch a few samples from categories that user ISN'T fixing right now
        neg_emails = (Email
                     .select(Email.sender, Email.subject, Email.category)
                     .where((Email.is_classified == True) & (Email.category.not_in(list(target_categories))))
                     .order_by(fn.Random())
                     .limit(20))
        
        neg_samples = [{"sender": e.sender, "subject": e.subject, "category": e.category} for e in neg_emails]

        prompt = f"""
        You are an elite Regex Pattern Engineer. 
        Objective: Create high-performance, robust python-style regex patterns based on manual email classifications.
        
        [POSITIVE SAMPLES] (Must match these):
        {json.dumps(pos_samples, indent=2, ensure_ascii=False)}

        [NEGATIVE SAMPLES] (Must NOT match these):
        {json.dumps(neg_samples, indent=2, ensure_ascii=False)}
        
        Instruction:
        1. Generalization: If multiple senders share a domain (e.g., portal.gpters.org, mail.gpters.org), generate a domain-wide pattern like 'gpters\\.org'.
        2. Simplification: Favor short, powerful patterns over long specific ones. Prefer domain matches if the sender is reliable.
        3. Cross-Validation: ENSURE your patterns do NOT trigger on any of the provided negative samples.
        4. Negative Feedback: If a keyword is common but context-specific, use negative lookaheads (e.g., '^(?!.*receipt).*promo.*$').
        5. Precision: Use word boundaries \\b for keyword matches.
        
        Output Format:
        Return a JSON object: {{"regex_pattern": "category"}}
        
        IMPORTANT: Return ONLY valid JSON.
        """
        
        try:
            if not self.model: return {}
            time.sleep(2)
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            self.logger.error(f"Intelligence Phase Error: {e}")
            return {}

    def _call_ai_batch(self, senders_with_subjects: List[tuple]) -> Dict[str, Any]:
        if not self.model or not senders_with_subjects:
            return {}
            
        # Refactor: Split into chunks of 25 to avoid JSON truncation errors in response
        chunk_size = 25
        all_results = {}
        
        for i in range(0, len(senders_with_subjects), chunk_size):
            chunk = senders_with_subjects[i:i + chunk_size]
            self.logger.info(f" -> Processing batch {i//chunk_size + 1} ({len(chunk)} senders)...")
            
            # Format: [sender, [subj1, subj2, subj3]]
            formatted_senders = []
            for s, subjs in chunk:
                formatted_senders.append({"sender": s, "sample_subjects": subjs})

            prompt = f"""
            You are an elite email organization consultant.
            Objective: Classify the provided list of email senders, using their addresses and sample subjects for context.
            
            Categories:
            {json.dumps(AppConfig.CATEGORIES, indent=2, ensure_ascii=False)}

            Instruction:
            - Return a SINGLE JSON object where keys are sender addresses and values are objects containing "category" and "reasoning".
            - Example: {{"service@paypal.com": {{"category": "🛒_Shopping_Promo", "reasoning": "Payment notification (Subject: Payment complete)"}}}}
            
            Tuning Rules (CRITICAL):
            1. "🛒_Shopping_Checkout": For ACTUAL TRANSACTIONS (결제, 주문, 배송). This is high priority.
            2. "🛍️_Shopping_Promo": For ADS, DISCOUNTS, or PROMOS (할인, 광고, 특가). Do NOT mix with Checkout.
            3. "🏢_Notice_Privacy": Legal/privacy notices and **Subscription Price Changes/Agreements** (개인정보 이용내역, 약관 개정, 가격 변경 동의). These require user attention, do NOT put in shopping.
            4. "🏠_Personal_Life" now includes **Login Alerts**, **Google Security Alerts**, **Workspace Share Requests**, and **Subscription/Trial Notices** (새로운 기기 로그인, 보안 알림, Share Request, Apple Music 무료 체험 종료). Do NOT put these in Auth System or Shopping.
            11. "🔒_Auth_System" is strictly for **Verification Codes**, **2FA**, **Account Verification**, and **Sign-up Confirmation** (회원가입 인증, 인증 코드). These are high priority and should NEVER be in Promo or Shopping.
            5. "🏥_Medical_Work" is for clinical data, therapies, hospital notices, and medical education (like Medscape). This is YOUR field, do not confuse with Dev.
            6. "💻_Dev_Tech" is for coding tools and infrastructure. This includes GitHub, AWS, and AI IDEs like **Cursor** (cursor.com).
            7. "🚫_Spam" is for social media junk like Facebook friend suggestions or people you may know.
            8. "💰_Finance" should be strictly reserved for monthly statements (명세서) from BANKS, CARD COMPANIES, or GOV.
            9. Ambiguity Handling: If a specific billing keyword (like 명세서, 영수증) appears from a non-financial domain (e.g., hyundai.com, ootd.com) and doesn't clearly fit others, set category to "Unclassified" and explain why in reasoning.
            10. reasoning should be a short, clear explanation in Korean, mentioning if the subject helped or if there was a domain mismatch.

            Senders to Classify (Sender & Sample Subjects):
            {json.dumps(formatted_senders, ensure_ascii=False)}

            IMPORTANT: Return ONLY valid JSON. No conversational text.
            """
            
            try:
                # 4s wait for free tier
                time.sleep(4)
                response = self.model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                raw_res = json.loads(response.text)
                
                # Robustness: AI sometimes returns a list of objects instead of a dict
                if isinstance(raw_res, list):
                    dict_res = {}
                    for item in raw_res:
                        if isinstance(item, dict) and "sender" in item:
                            s = item.pop("sender")
                            dict_res[s] = item
                        elif isinstance(item, dict) and len(item) == 1:
                            k = list(item.keys())[0]
                            dict_res[k] = item[k]
                    all_results.update(dict_res)
                else:
                    all_results.update(raw_res)
                    
            except Exception as e:
                self.logger.error(f"AI Batch Error (Index {i}): {e}")
                # Continue to next batch
                continue
                
        return all_results

    def apply_rules(self):
        """Load rules.json and update DB, showing a summary of classification."""
        if not os.path.exists("rules.json"):
            self.logger.warning("rules.json not found.")
            return

        with open("rules.json", "r", encoding="utf-8") as f:
            rules = json.load(f)
            
        self.logger.info("Applying rules to DB and preparing classification preview...")
        stats = {} # category -> count
        
        with db.atomic():
            for sender, info in rules.items():
                category = info.get("category", "Unclassified")
                source = info.get("source", "Manual")
                reasoning = info.get("reasoning", "")
                
                # Feedback Loop: If user manually corrects a 'Learned' result, penalize the rule
                if source == 'Manual':
                    # Find if there was a previous 'Learned' match for this sender
                    prev_email = Email.get_or_none(Email.sender == sender)
                    if prev_email and prev_email.rule_source == 'Learned' and prev_email.category != category:
                        # Extract the pattern from reasoning (it was stored as "Adaptive Learning Match (Pattern: ...)")
                        pattern_match = re.search(r"Pattern: (.*)\)", prev_email.reasoning or "")
                        if pattern_match:
                            target_pattern = pattern_match.group(1)
                            lr = LearnedRule.get_or_none(LearnedRule.pattern == target_pattern)
                            if lr:
                                self.logger.warning(f"📉 Feedback: Penalizing rule '{target_pattern}' due to manual correction.")
                                lr.correction_count += 1
                                lr.confidence = max(0.0, lr.confidence - 0.4) # Aggressive reduction
                                lr.save()

                # Update: only if category changed or not yet classified
                rows = (Email
                        .update(category=category, 
                                is_classified=True, 
                                rule_source=source, 
                                is_synced=False,
                                reasoning=reasoning)
                        .where((Email.sender == sender) & ((Email.category != category) | (Email.is_classified == False)))
                        .execute())
                
                if rows > 0:
                    stats[category] = stats.get(category, 0) + rows
                    # Always log changes for visibility
                    self.logger.info(f" - [{source}] {sender} -> {category} ({reasoning})")
        
        # Log Summary
        self.logger.info("=== LOCAL CLASSIFICATION SUMMARY ===")
        
        # Fetch current total status from DB
        from peewee import fn
        db_stats = (Email
                   .select(Email.category, fn.COUNT(Email.id).alias('count'))
                   .where(Email.is_classified == True)
                   .group_by(Email.category)
                   .order_by(fn.COUNT(Email.id).desc()))
        
        found_data = False
        for row in db_stats:
            found_data = True
            change_count = stats.get(row.category, 0)
            change_str = f" (+{change_count} new entries/changes)" if change_count > 0 else " (up to date)"
            self.logger.info(f"[{row.category}] - {row.count} emails{change_str}")

        if not found_data:
            self.logger.info("No classified emails found in DB.")
            if not rules:
                self.logger.warning("rules.json is empty. Run 'Learn Rules' first.")
            else:
                self.logger.info("Existing emails in DB don't match any rules in rules.json.")
        
        self.logger.info("======================================")
        self.logger.info("Local classification (DB update) complete! You can now Phase 3 (Cloud Apply).")
