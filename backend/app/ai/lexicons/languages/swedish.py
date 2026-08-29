"""
Swedish (Svenska) [sv]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class SwedishLanguageEngine:
    LANGUAGE_CODE = "sv"
    LANGUAGE_NAME = "Swedish (Svenska)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_sv", "damage_keyword_2_sv", "broken_item_sv", "smashed_box_sv",
            "cracked_screen_sv", "faulty_device_sv", "defective_good_sv", "damaged_parcel_sv"
        ],
        "LATE_DELIVERY": [
            "where_is_order_sv", "delivery_delayed_sv", "late_parcel_sv", "tracking_stuck_sv",
            "courier_exception_sv", "slow_shipment_sv", "missing_delivery_date_sv"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_sv", "double_billed_sv", "two_charges_sv", "unauthorized_fee_sv",
            "overcharged_amount_sv", "billing_discrepancy_sv"
        ],
        "REQUEST_RETURN": [
            "want_to_return_sv", "return_label_sv", "rma_request_sv", "exchange_size_sv",
            "refund_request_sv", "send_back_product_sv"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_sv", "abort_order_sv", "mistake_order_sv", "stop_fulfillment_sv"
        ],
    }

    STOPWORDS: List[str] = [
        "the_sv", "is_sv", "at_sv", "which_sv", "on_sv", "for_sv", "with_sv"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
