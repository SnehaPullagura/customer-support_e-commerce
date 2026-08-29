"""
AI NLP Intent Classifier, Sentiment Analyzer, and Priority Estimator.
"""

import re
import time
from typing import Dict, Tuple

from app.schemas.ai import AIClassificationResponse

INTENT_KEYWORDS = {
    "DAMAGED_PRODUCT": ["damaged", "broken", "cracked", "shattered", "defect", "scratched", "smashed", "dented"],
    "LATE_DELIVERY": ["late", "delayed", "where is", "not arrived", "tracking", "still waiting", "overdue", "lost"],
    "WRONG_PRODUCT": ["wrong item", "wrong product", "incorrect", "received something else", "different color"],
    "PAYMENT_ISSUE": ["charge", "double charged", "payment failed", "decline", "refund missing", "billing", "unauthorized"],
    "RETURN_REQUEST": ["return", "send back", "exchange", "refund my money", "rma", "money back"],
    "ACCOUNT_PROBLEM": ["login", "password", "locked out", "cant access", "change email", "reset"],
}

CATEGORY_MAP = {
    "DAMAGED_PRODUCT": ("PRODUCT", "DAMAGED_ITEM", "DAMAGED_PRODUCT_PLAYBOOK"),
    "LATE_DELIVERY": ("DELIVERY", "LATE_SHIPMENT", "LATE_DELIVERY_PLAYBOOK"),
    "WRONG_PRODUCT": ("PRODUCT", "WRONG_ITEM", "DAMAGED_PRODUCT_PLAYBOOK"),
    "PAYMENT_ISSUE": ("PAYMENT", "PAYMENT_FAILED", "PAYMENT_FAILURE_PLAYBOOK"),
    "RETURN_REQUEST": ("RETURNS", "CUSTOMER_RETURN", "DAMAGED_PRODUCT_PLAYBOOK"),
    "ACCOUNT_PROBLEM": ("ACCOUNT", "LOGIN_ISSUE", None),
}

FRUSTRATION_WORDS = ["angry", "terrible", "worst", "unacceptable", "furious", "lawyer", "sue", "horrible", "dispute", "rip off", "scam", "disaster"]
POSITIVE_WORDS = ["thank", "thanks", "great", "awesome", "helpful", "appreciate", "good", "fast", "love"]


class AIClassifier:
    @staticmethod
    def classify_text(text: str, customer_tier: str = "STANDARD") -> AIClassificationResponse:
        start_time = time.time()
        lower_text = text.lower()

        # 1. Intent Detection
        scores: Dict[str, int] = {intent: 0 for intent in INTENT_KEYWORDS}
        for intent, keywords in INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in lower_text:
                    scores[intent] += 2

        detected_intent = max(scores, key=scores.get)
        max_score = scores[detected_intent]
        confidence = min(0.95, 0.60 + (max_score * 0.08)) if max_score > 0 else 0.50

        category, subcategory, playbook_code = CATEGORY_MAP.get(
            detected_intent, ("GENERAL", "GENERAL_INQUIRY", None)
        )

        # 2. Sentiment Calculation
        damage_hits = sum(1 for w in ["damaged", "broken", "cracked", "shattered", "defect", "crushed"] if w in lower_text)
        frustration_hits = sum(1 for w in FRUSTRATION_WORDS if w in lower_text) + (1 if damage_hits > 0 else 0)
        positive_hits = sum(1 for w in POSITIVE_WORDS if w in lower_text)
        exclamation_count = text.count("!")

        sentiment_score = 0.0
        if frustration_hits > 0 or exclamation_count > 2:
            sentiment_score = max(-1.0, -0.3 * frustration_hits - (0.1 * exclamation_count))
            sentiment_label = "HIGHLY_FRUSTRATED" if sentiment_score < -0.6 else "NEGATIVE"
        elif positive_hits > 0:
            sentiment_score = min(1.0, 0.3 * positive_hits)
            sentiment_label = "POSITIVE"
        else:
            sentiment_score = 0.0
            sentiment_label = "NEUTRAL"

        # 3. Priority Recommendation
        priority = "MEDIUM"
        if customer_tier in ["VIP", "PLATINUM"] or sentiment_score < -0.6 or detected_intent == "PAYMENT_ISSUE":
            priority = "HIGH"
        if sentiment_score < -0.8 or (customer_tier == "VIP" and sentiment_score < -0.4):
            priority = "CRITICAL"
        if sentiment_score >= 0.0 and detected_intent in ["GENERAL", "RETURN_REQUEST"]:
            priority = "LOW" if customer_tier == "STANDARD" else "MEDIUM"

        summary = f"Customer reports {detected_intent.replace('_', ' ').lower()}: '{text[:120]}...'"

        return AIClassificationResponse(
            intent=detected_intent,
            suggested_category=category,
            suggested_subcategory=subcategory,
            suggested_priority=priority,
            sentiment_score=round(sentiment_score, 2),
            sentiment_label=sentiment_label,
            confidence_score=round(confidence, 2),
            summary=summary,
            recommended_playbook_code=playbook_code,
        )
