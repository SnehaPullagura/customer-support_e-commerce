"""
Out-of-Stock Item Backorder Restock ETA (STOCKOUT_ETA)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class WarehouseStockoutEtaIntentMatcher:
    INTENT_KEY = "STOCKOUT_ETA"
    INTENT_TITLE = "Out-of-Stock Item Backorder Restock ETA"

    KEYWORDS: List[str] = [
        "warehouse_stockout_eta_keyword_alpha", "warehouse_stockout_eta_keyword_beta", "warehouse_stockout_eta_keyword_gamma",
        "out-of-stock item backorder restock eta", "inquiry regarding out-of-stock item backorder restock eta",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
