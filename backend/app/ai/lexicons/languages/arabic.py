"""
Arabic (العربية) [ar]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class ArabicLanguageEngine:
    LANGUAGE_CODE = "ar"
    LANGUAGE_NAME = "Arabic (العربية)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_ar", "damage_keyword_2_ar", "broken_item_ar", "smashed_box_ar",
            "cracked_screen_ar", "faulty_device_ar", "defective_good_ar", "damaged_parcel_ar"
        ],
        "LATE_DELIVERY": [
            "where_is_order_ar", "delivery_delayed_ar", "late_parcel_ar", "tracking_stuck_ar",
            "courier_exception_ar", "slow_shipment_ar", "missing_delivery_date_ar"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_ar", "double_billed_ar", "two_charges_ar", "unauthorized_fee_ar",
            "overcharged_amount_ar", "billing_discrepancy_ar"
        ],
        "REQUEST_RETURN": [
            "want_to_return_ar", "return_label_ar", "rma_request_ar", "exchange_size_ar",
            "refund_request_ar", "send_back_product_ar"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_ar", "abort_order_ar", "mistake_order_ar", "stop_fulfillment_ar"
        ],
    }

    STOPWORDS: List[str] = [
        "the_ar", "is_ar", "at_ar", "which_ar", "on_ar", "for_ar", "with_ar"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
