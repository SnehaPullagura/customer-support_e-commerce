"""
Product Safety Recall & Hazardous Check (RECALL_QUERY)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class CpscRecallSafetyQueryIntentMatcher:
    INTENT_KEY = "RECALL_QUERY"
    INTENT_TITLE = "Product Safety Recall & Hazardous Check"

    KEYWORDS: List[str] = [
        "cpsc_recall_safety_query_keyword_alpha", "cpsc_recall_safety_query_keyword_beta", "cpsc_recall_safety_query_keyword_gamma",
        "product safety recall & hazardous check", "inquiry regarding product safety recall & hazardous check",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
