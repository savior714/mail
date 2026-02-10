import re
import json
import os
from typing import Dict, Any, Optional
import time
import google.generativeai as genai
from pydantic import BaseModel, Field

from src.config import AppConfig
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ClassificationResult(BaseModel):
    category: str
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(description="Brief reason for the classification")

class EmailClassifier:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning(
                "GOOGLE_API_KEY not found in environment variables. LLM layer will fail."
            )
        else:
            genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel('gemini-flash-latest') if api_key else None

    def classify(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifies an email using the 3-layer architecture.
        Returns the original email data enriched with 'category', 'method', and 'reasoning'.
        """
        sender = email_data.get('sender', '')
        subject = email_data.get('subject', '')
        snippet = email_data.get('snippet', '')
        
        # Layer 1: Hard Rules (Regex)
        category_l1 = self._apply_hard_rules(sender, subject)
        if category_l1:
            return {
                **email_data,
                'category': category_l1,
                'method': 'Rule',
                'reasoning': 'Matched static regex rules.'
            }

        # Layer 2: AI Classification (LLM)
        if self.model:
            category_l2 = self._call_llm(sender, subject, snippet)
            if category_l2:
                return {
                    **email_data,
                    'category': category_l2.category,
                    'method': 'AI',
                    'reasoning': category_l2.reasoning
                }
        
        # Layer 3: Fallback
        return {
            **email_data,
            'category': 'Unclassified',
            'method': 'Fallback',
            'reasoning': 'Could not classify via Rules or AI.'
        }

    def _apply_hard_rules(self, sender: str, subject: str) -> Optional[str]:
        """Layer 1: Regex matching."""
        sender_lower = sender.lower()
        subject_lower = subject.lower()

        for category, patterns in AppConfig.HARD_RULES.items():
            for pattern in patterns:
                # Check both sender and subject
                if re.search(pattern, sender_lower) or re.search(pattern, subject_lower):
                    return category
        return None

    def _call_llm(self, sender: str, subject: str, snippet: str) -> Optional[ClassificationResult]:
        """Layer 2: LLM Classification."""
        # Rate Limit for Free Tier: 15 RPM = 1 request per 4 seconds
        time.sleep(4)
        
        try:
            prompt = f"""
            You are an intelligent email classifier. Classify the following email into one of these categories:
            {json.dumps(AppConfig.CATEGORIES, indent=2, ensure_ascii=False)}

            Email Details:
            - Sender: {sender}
            - Subject: {subject}
            - Snippet: {snippet}

            Return ONLY a valid JSON object matching this schema:
            {{
                "category": "One of the category keys",
                "confidence": 0.0 to 1.0,
                "reasoning": "Brief explanation"
            }}
            """

            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            content = response.text
            if not content:
                print(f"Empty response from LLM for email: {subject}")
                return None
            
            data = json.loads(content)
            # Validate category
            category = data.get("category")
            if category not in AppConfig.CATEGORIES:
                # Try to find partial match or fallback
                print(f"Invalid category returned: {category}")
                return None

            return ClassificationResult(**data)

        except Exception as e:
            logger.error("LLM classification failed: %s", e)
            return None
