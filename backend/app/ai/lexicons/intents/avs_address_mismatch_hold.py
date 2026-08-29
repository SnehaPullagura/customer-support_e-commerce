"""
Fraud Risk AVS Address Verification Hold (AVS_HOLD)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class AvsAddressMismatchHoldIntentMatcher:
    INTENT_KEY = "AVS_HOLD"
    INTENT_TITLE = "Fraud Risk AVS Address Verification Hold"

    KEYWORDS: List[str] = [
        "avs_address_mismatch_hold_keyword_alpha", "avs_address_mismatch_hold_keyword_beta", "avs_address_mismatch_hold_keyword_gamma",
        "fraud risk avs address verification hold", "inquiry regarding fraud risk avs address verification hold",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
