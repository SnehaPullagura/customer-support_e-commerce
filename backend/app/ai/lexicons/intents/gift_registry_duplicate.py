"""
Wedding Gift Registry Duplicate Return (GIFT_REG_DUP)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class GiftRegistryDuplicateIntentMatcher:
    INTENT_KEY = "GIFT_REG_DUP"
    INTENT_TITLE = "Wedding Gift Registry Duplicate Return"

    KEYWORDS: List[str] = [
        "gift_registry_duplicate_keyword_alpha", "gift_registry_duplicate_keyword_beta", "gift_registry_duplicate_keyword_gamma",
        "wedding gift registry duplicate return", "inquiry regarding wedding gift registry duplicate return",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
