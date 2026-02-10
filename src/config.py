import re
from typing import Dict, List
from pydantic import BaseModel

class EmailCategory(BaseModel):
    name: str
    description: str

class AppConfig:
    # Categories definition
    CATEGORIES: Dict[str, str] = {
        "💰_Finance": "Banking, credit card statements, stocks (ETF), tax invoices, year-end settlements",
        "🏥_Medical_Work": "Hospital notices, conferences, journals, pharmaceutical companies, HIRA",
        "💻_Dev_Tech": "GitHub, AWS, Vercel, Sentry, technical newsletters, Python related",
        "🛒_Shopping_Promo": "Coupang, Naver Pay, delivery notifications, ads, promotions",
        "🔒_Auth_System": "Verification codes, password changes, login alerts, 2FA",
        "🏠_Personal_Life": "Family, travel reservations (flights/hotels), golf bookings, personal contacts",
    }

    # Hard Rules (Regex) for Layer 1
    # Key: Category, Value: List of regex patterns to match against Sender or Subject
    HARD_RULES: Dict[str, List[str]] = {
        "🔒_Auth_System": [
            r"verify", r"code", r"auth", r"password", r"login", r"2fa", 
            r"signin", r"security alert", r"인증", r"비밀번호"
        ],
        "🛒_Shopping_Promo": [
            r"noreply", r"do-not-reply", r"no-reply", r"promo", r"sale", 
            r"advertisement", r"광고", r"쿠팡", r"배송", r"주문"
        ],
        "💻_Dev_Tech": [
            r"github", r"aws", r"vercel", r"sentry", r"python", r"django", 
            r"docker", r"kubernetes", r"api", r"dev"
        ],
        "💰_Finance": [
            r"bank", r"card", r"statement", r"tax", r"invoice", r"receipt", 
            r"bill", r"payment", r"결제", r"명세서", r"은행", r"카드"
        ]
    }

    # Model for LLM
    LLM_MODEL = "gemini-1.5-flash"
    
    # Dry Run Settings
    FETCH_LIMIT = 50
