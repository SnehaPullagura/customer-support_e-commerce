"""
LTL Freight Pallet Crushed in Transit (FREIGHT_CRUSHED)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class LtlFreightDamagedPalletIntentMatcher:
    INTENT_KEY = "FREIGHT_CRUSHED"
    INTENT_TITLE = "LTL Freight Pallet Crushed in Transit"

    KEYWORDS: List[str] = [
        "ltl_freight_damaged_pallet_keyword_alpha", "ltl_freight_damaged_pallet_keyword_beta", "ltl_freight_damaged_pallet_keyword_gamma",
        "ltl freight pallet crushed in transit", "inquiry regarding ltl freight pallet crushed in transit",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
