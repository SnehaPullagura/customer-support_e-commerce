"""
Cross-Border International VAT Rebate (VAT_REBATE)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class TouristVatDrawbackIntentMatcher:
    INTENT_KEY = "VAT_REBATE"
    INTENT_TITLE = "Cross-Border International VAT Rebate"

    KEYWORDS: List[str] = [
        "tourist_vat_drawback_keyword_alpha", "tourist_vat_drawback_keyword_beta", "tourist_vat_drawback_keyword_gamma",
        "cross-border international vat rebate", "inquiry regarding cross-border international vat rebate",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
