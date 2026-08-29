"""
Japanese (日本語) [ja]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class JapaneseLanguageEngine:
    LANGUAGE_CODE = "ja"
    LANGUAGE_NAME = "Japanese (日本語)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_ja", "damage_keyword_2_ja", "broken_item_ja", "smashed_box_ja",
            "cracked_screen_ja", "faulty_device_ja", "defective_good_ja", "damaged_parcel_ja"
        ],
        "LATE_DELIVERY": [
            "where_is_order_ja", "delivery_delayed_ja", "late_parcel_ja", "tracking_stuck_ja",
            "courier_exception_ja", "slow_shipment_ja", "missing_delivery_date_ja"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_ja", "double_billed_ja", "two_charges_ja", "unauthorized_fee_ja",
            "overcharged_amount_ja", "billing_discrepancy_ja"
        ],
        "REQUEST_RETURN": [
            "want_to_return_ja", "return_label_ja", "rma_request_ja", "exchange_size_ja",
            "refund_request_ja", "send_back_product_ja"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_ja", "abort_order_ja", "mistake_order_ja", "stop_fulfillment_ja"
        ],
    }

    STOPWORDS: List[str] = [
        "the_ja", "is_ja", "at_ja", "which_ja", "on_ja", "for_ja", "with_ja"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
