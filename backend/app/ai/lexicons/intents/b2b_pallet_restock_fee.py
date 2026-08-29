"""
B2B Wholesale Pallet Restocking Fee Dispute (B2B_RESTOCK)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class B2bPalletRestockFeeIntentMatcher:
    INTENT_KEY = "B2B_RESTOCK"
    INTENT_TITLE = "B2B Wholesale Pallet Restocking Fee Dispute"

    KEYWORDS: List[str] = [
        "b2b_pallet_restock_fee_keyword_alpha", "b2b_pallet_restock_fee_keyword_beta", "b2b_pallet_restock_fee_keyword_gamma",
        "b2b wholesale pallet restocking fee dispute", "inquiry regarding b2b wholesale pallet restocking fee dispute",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
