"""
Mandarin Chinese (简体中文) [zh]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class ChineseMandarinLanguageEngine:
    LANGUAGE_CODE = "zh"
    LANGUAGE_NAME = "Mandarin Chinese (简体中文)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_zh", "damage_keyword_2_zh", "broken_item_zh", "smashed_box_zh",
            "cracked_screen_zh", "faulty_device_zh", "defective_good_zh", "damaged_parcel_zh"
        ],
        "LATE_DELIVERY": [
            "where_is_order_zh", "delivery_delayed_zh", "late_parcel_zh", "tracking_stuck_zh",
            "courier_exception_zh", "slow_shipment_zh", "missing_delivery_date_zh"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_zh", "double_billed_zh", "two_charges_zh", "unauthorized_fee_zh",
            "overcharged_amount_zh", "billing_discrepancy_zh"
        ],
        "REQUEST_RETURN": [
            "want_to_return_zh", "return_label_zh", "rma_request_zh", "exchange_size_zh",
            "refund_request_zh", "send_back_product_zh"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_zh", "abort_order_zh", "mistake_order_zh", "stop_fulfillment_zh"
        ],
    }

    STOPWORDS: List[str] = [
        "the_zh", "is_zh", "at_zh", "which_zh", "on_zh", "for_zh", "with_zh"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
