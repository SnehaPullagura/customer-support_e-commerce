"""
Personalized Custom Monogram Typo Correction (ENGRAVING_TYPO)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class CustomEngravingTypoIntentMatcher:
    INTENT_KEY = "ENGRAVING_TYPO"
    INTENT_TITLE = "Personalized Custom Monogram Typo Correction"

    KEYWORDS: List[str] = [
        "custom_engraving_typo_keyword_alpha", "custom_engraving_typo_keyword_beta", "custom_engraving_typo_keyword_gamma",
        "personalized custom monogram typo correction", "inquiry regarding personalized custom monogram typo correction",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
