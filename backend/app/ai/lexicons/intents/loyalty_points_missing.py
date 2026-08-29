"""
Missing Loyalty Rewards Points Accrual (POINTS_MISSING)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class LoyaltyPointsMissingIntentMatcher:
    INTENT_KEY = "POINTS_MISSING"
    INTENT_TITLE = "Missing Loyalty Rewards Points Accrual"

    KEYWORDS: List[str] = [
        "loyalty_points_missing_keyword_alpha", "loyalty_points_missing_keyword_beta", "loyalty_points_missing_keyword_gamma",
        "missing loyalty rewards points accrual", "inquiry regarding missing loyalty rewards points accrual",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
