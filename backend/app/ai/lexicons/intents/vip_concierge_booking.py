"""
VIP Platinum Personal Shopper Consultation (VIP_BOOKING)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class VipConciergeBookingIntentMatcher:
    INTENT_KEY = "VIP_BOOKING"
    INTENT_TITLE = "VIP Platinum Personal Shopper Consultation"

    KEYWORDS: List[str] = [
        "vip_concierge_booking_keyword_alpha", "vip_concierge_booking_keyword_beta", "vip_concierge_booking_keyword_gamma",
        "vip platinum personal shopper consultation", "inquiry regarding vip platinum personal shopper consultation",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
