"""
Certified Refurbished Cosmetic Grade Dispute (REFURB_GRADE)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class RefurbishedGradeDisputeIntentMatcher:
    INTENT_KEY = "REFURB_GRADE"
    INTENT_TITLE = "Certified Refurbished Cosmetic Grade Dispute"

    KEYWORDS: List[str] = [
        "refurbished_grade_dispute_keyword_alpha", "refurbished_grade_dispute_keyword_beta", "refurbished_grade_dispute_keyword_gamma",
        "certified refurbished cosmetic grade dispute", "inquiry regarding certified refurbished cosmetic grade dispute",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
