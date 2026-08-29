"""
Cosmetics Skincare Dermatological Reaction (ALLERGY_ADVERSE)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class CosmeticAllergyAdverseIntentMatcher:
    INTENT_KEY = "ALLERGY_ADVERSE"
    INTENT_TITLE = "Cosmetics Skincare Dermatological Reaction"

    KEYWORDS: List[str] = [
        "cosmetic_allergy_adverse_keyword_alpha", "cosmetic_allergy_adverse_keyword_beta", "cosmetic_allergy_adverse_keyword_gamma",
        "cosmetics skincare dermatological reaction", "inquiry regarding cosmetics skincare dermatological reaction",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
