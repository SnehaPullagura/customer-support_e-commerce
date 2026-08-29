"""
Wholesale Net-30 Credit Line Increase (B2B_CREDIT_INC)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class B2bCreditLineIncreaseIntentMatcher:
    INTENT_KEY = "B2B_CREDIT_INC"
    INTENT_TITLE = "Wholesale Net-30 Credit Line Increase"

    KEYWORDS: List[str] = [
        "b2b_credit_line_increase_keyword_alpha", "b2b_credit_line_increase_keyword_beta", "b2b_credit_line_increase_keyword_gamma",
        "wholesale net-30 credit line increase", "inquiry regarding wholesale net-30 credit line increase",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
