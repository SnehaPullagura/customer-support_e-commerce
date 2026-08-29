"""
Reseller Sales Tax Certificate Upload (TAX_EXEMPT_UPLOAD)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class TaxExemptionUploadIntentMatcher:
    INTENT_KEY = "TAX_EXEMPT_UPLOAD"
    INTENT_TITLE = "Reseller Sales Tax Certificate Upload"

    KEYWORDS: List[str] = [
        "tax_exemption_upload_keyword_alpha", "tax_exemption_upload_keyword_beta", "tax_exemption_upload_keyword_gamma",
        "reseller sales tax certificate upload", "inquiry regarding reseller sales tax certificate upload",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
