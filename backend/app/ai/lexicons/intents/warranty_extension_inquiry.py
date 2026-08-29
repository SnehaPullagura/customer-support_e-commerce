"""
Warranty Extension & Protection Plan Inquiry (WARRANTY_EXT)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class WarrantyExtensionInquiryIntentMatcher:
    INTENT_KEY = "WARRANTY_EXT"
    INTENT_TITLE = "Warranty Extension & Protection Plan Inquiry"

    KEYWORDS: List[str] = [
        "warranty_extension_inquiry_keyword_alpha", "warranty_extension_inquiry_keyword_beta", "warranty_extension_inquiry_keyword_gamma",
        "warranty extension & protection plan inquiry", "inquiry regarding warranty extension & protection plan inquiry",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
