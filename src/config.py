import re
from typing import Dict, List
from pydantic import BaseModel

class EmailCategory(BaseModel):
    name: str
    description: str

class AppConfig:
    # Categories definition
    CATEGORIES: Dict[str, str] = {
        "💰_Finance": "Strictly banking statements, credit card monthly bills, and official financial reports.",
        "🛒_Shopping_Checkout": "Order confirmations, payment results (Naver Pay/Kakao Pay checkout), delivery tracking, and receipts.",
        "🛒_Shopping_Promo": "Shopping ads, discount coupons, sale alerts, and promotional newsletters.",
        "🏥_Medical_Work": "Hospital notices, clinical data, pharmaceutical journals, and medical education.",
        "💻_Dev_Tech": "GitHub, AWS, technical tools, API notices, and developer newsletters.",
        "🚗_Car_Life": "Car maintenance, inspection reports, parking updates, Hi-pass, and vehicle services.",
        "🏢_Notice_Privacy": "Privacy policy updates, personal data usage notices, and legal terms of service changes.",
        "🔒_Auth_System": "Verification codes, 2FA, and security alerts (excluding simple login notices).",
        "🏠_Personal_Life": "Family, travel bookings, golf, and simple login notifications.",
        "🚫_Spam": "Social media junk (Facebook suggestions) and persistent marketing fluff.",
    }

    # Hard Rules (Regex) for Layer 1
    # Key: Category, Value: List of regex patterns to match against Sender or Subject
    # Priority: First match wins (Top categories have higher priority)
    HARD_RULES: Dict[str, List[str]] = {
        "💰_Finance": [
            r"신용카드", r"은행", r"국세청", r"보험", r"증권", r"입출금", r"대출",
            r"bank", r"creditcard", r"tax", r"holding"
        ],
        "🛒_Shopping_Checkout": [
            r"결제", r"주문", r"배송", r"승인", r"영수증", r"naverpay", r"kakaopay", r"checkout", r"receipt", r"order confirmation"
        ],
        "💻_Dev_Tech": [
            r"github", r"aws", r"vercel", r"sentry", r"python", r"django", 
            r"docker", r"kubernetes", r"\bapi\b", r"dev", r"코드리뷰", r"pull request", r"cursor"
        ],
        "🏥_Medical_Work": [
            r"medscape", r"hira", r"심평원", r"hospital", r"clinic", r"medical", r"학회", r"제약", r"환자", r"임상", r"clinical", r"therapy"
        ],
        "🚗_Car_Life": [
            r"bmw", r"hyundai", r"kia", r"benz", r"audi", r"genesis", r"차량", r"자동차", r"점검", r"정비", r"주차", r"하이패스", r"교통", r"내차"
        ],
        "🔒_Auth_System": [
            r"verify", r"code", r"auth", r"password", r"2fa", r"signin", r"인증", r"비밀번호", r"OTP", r"회원가입", r"sign-up"
        ],
        "🛒_Shopping_Promo": [
            r"promo", r"sale", r"advertisement", r"광고", r"쿠폰", r"혜택", r"할인", r"특가", r"이벤트", r"G마켓", r"11번가", r"옥션", r"티몬", r"위메프"
        ],
        "🏢_Notice_Privacy": [
            r"개인정보", r"이용내역", r"통지", r"수신동의", r"개정", r"이용약관", r"약관", r"가격 변경", r"동의", r"변경", r"privacy policy", r"terms of service"
        ],
        "🏠_Personal_Life": [
            r"새로운 기기", r"new device", r"로그인 알림", r"로그인 안내", r"login notification", r"보안 알림", r"security alert", r"Share Request", r"Apple Music", r"무료 체험", r"종료", r"여행", r"숙소", r"항공", r"예약"
        ],
        "🚫_Spam": [
            r"facebook", r"알 수도 있는 사람", r"친구 추천", r"suggested for you"
        ]
    }

    # Model for LLM
    LLM_MODEL = "gemini-1.5-flash"
    
    # Dry Run Settings
    FETCH_LIMIT = 50
