"""
Software License Incompatible OS Return (SOFTWARE_INCOMPAT)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class SoftwareIncompatibleOsIntentMatcher:
    INTENT_KEY = "SOFTWARE_INCOMPAT"
    INTENT_TITLE = "Software License Incompatible OS Return"

    KEYWORDS: List[str] = [
        "software_incompatible_os_keyword_alpha", "software_incompatible_os_keyword_beta", "software_incompatible_os_keyword_gamma",
        "software license incompatible os return", "inquiry regarding software license incompatible os return",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
