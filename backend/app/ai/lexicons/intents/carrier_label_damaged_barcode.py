"""
Carrier Sorting Facility Damaged Barcode (BARCODE_DAMAGED)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class CarrierLabelDamagedBarcodeIntentMatcher:
    INTENT_KEY = "BARCODE_DAMAGED"
    INTENT_TITLE = "Carrier Sorting Facility Damaged Barcode"

    KEYWORDS: List[str] = [
        "carrier_label_damaged_barcode_keyword_alpha", "carrier_label_damaged_barcode_keyword_beta", "carrier_label_damaged_barcode_keyword_gamma",
        "carrier sorting facility damaged barcode", "inquiry regarding carrier sorting facility damaged barcode",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
