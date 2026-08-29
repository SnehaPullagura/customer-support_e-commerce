"""
Driver Delivery Signature Forgery Dispute (SIG_FORGERY)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class DeliverySignatureForgeryIntentMatcher:
    INTENT_KEY = "SIG_FORGERY"
    INTENT_TITLE = "Driver Delivery Signature Forgery Dispute"

    KEYWORDS: List[str] = [
        "delivery_signature_forgery_keyword_alpha", "delivery_signature_forgery_keyword_beta", "delivery_signature_forgery_keyword_gamma",
        "driver delivery signature forgery dispute", "inquiry regarding driver delivery signature forgery dispute",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
