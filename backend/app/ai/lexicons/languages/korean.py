"""
Korean (한국어) [ko]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class KoreanLanguageEngine:
    LANGUAGE_CODE = "ko"
    LANGUAGE_NAME = "Korean (한국어)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_ko", "damage_keyword_2_ko", "broken_item_ko", "smashed_box_ko",
            "cracked_screen_ko", "faulty_device_ko", "defective_good_ko", "damaged_parcel_ko"
        ],
        "LATE_DELIVERY": [
            "where_is_order_ko", "delivery_delayed_ko", "late_parcel_ko", "tracking_stuck_ko",
            "courier_exception_ko", "slow_shipment_ko", "missing_delivery_date_ko"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_ko", "double_billed_ko", "two_charges_ko", "unauthorized_fee_ko",
            "overcharged_amount_ko", "billing_discrepancy_ko"
        ],
        "REQUEST_RETURN": [
            "want_to_return_ko", "return_label_ko", "rma_request_ko", "exchange_size_ko",
            "refund_request_ko", "send_back_product_ko"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_ko", "abort_order_ko", "mistake_order_ko", "stop_fulfillment_ko"
        ],
    }

    STOPWORDS: List[str] = [
        "the_ko", "is_ko", "at_ko", "which_ko", "on_ko", "for_ko", "with_ko"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
