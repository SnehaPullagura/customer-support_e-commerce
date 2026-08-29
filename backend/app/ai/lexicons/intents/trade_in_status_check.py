"""
Trade-In Device Inspection & Payment Status (TRADEIN_STATUS)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class TradeInStatusCheckIntentMatcher:
    INTENT_KEY = "TRADEIN_STATUS"
    INTENT_TITLE = "Trade-In Device Inspection & Payment Status"

    KEYWORDS: List[str] = [
        "trade_in_status_check_keyword_alpha", "trade_in_status_check_keyword_beta", "trade_in_status_check_keyword_gamma",
        "trade-in device inspection & payment status", "inquiry regarding trade-in device inspection & payment status",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
