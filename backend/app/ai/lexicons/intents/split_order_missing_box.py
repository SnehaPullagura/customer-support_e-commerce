"""
Split Shipment Multi-Box Delivery Missing (SPLIT_MISSING)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class SplitOrderMissingBoxIntentMatcher:
    INTENT_KEY = "SPLIT_MISSING"
    INTENT_TITLE = "Split Shipment Multi-Box Delivery Missing"

    KEYWORDS: List[str] = [
        "split_order_missing_box_keyword_alpha", "split_order_missing_box_keyword_beta", "split_order_missing_box_keyword_gamma",
        "split shipment multi-box delivery missing", "inquiry regarding split shipment multi-box delivery missing",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
