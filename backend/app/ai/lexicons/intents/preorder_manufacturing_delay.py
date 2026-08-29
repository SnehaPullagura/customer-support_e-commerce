"""
Pre-Order Product Launch Date Delay (PREORDER_DELAY)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class PreorderManufacturingDelayIntentMatcher:
    INTENT_KEY = "PREORDER_DELAY"
    INTENT_TITLE = "Pre-Order Product Launch Date Delay"

    KEYWORDS: List[str] = [
        "preorder_manufacturing_delay_keyword_alpha", "preorder_manufacturing_delay_keyword_beta", "preorder_manufacturing_delay_keyword_gamma",
        "pre-order product launch date delay", "inquiry regarding pre-order product launch date delay",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
