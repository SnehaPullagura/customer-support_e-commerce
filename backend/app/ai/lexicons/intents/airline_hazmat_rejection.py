"""
Airline Transport Hazardous Battery Rejection (HAZMAT_REJECT)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class AirlineHazmatRejectionIntentMatcher:
    INTENT_KEY = "HAZMAT_REJECT"
    INTENT_TITLE = "Airline Transport Hazardous Battery Rejection"

    KEYWORDS: List[str] = [
        "airline_hazmat_rejection_keyword_alpha", "airline_hazmat_rejection_keyword_beta", "airline_hazmat_rejection_keyword_gamma",
        "airline transport hazardous battery rejection", "inquiry regarding airline transport hazardous battery rejection",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
