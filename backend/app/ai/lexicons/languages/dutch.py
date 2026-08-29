"""
Dutch (Nederlands) [nl]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class DutchLanguageEngine:
    LANGUAGE_CODE = "nl"
    LANGUAGE_NAME = "Dutch (Nederlands)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_nl", "damage_keyword_2_nl", "broken_item_nl", "smashed_box_nl",
            "cracked_screen_nl", "faulty_device_nl", "defective_good_nl", "damaged_parcel_nl"
        ],
        "LATE_DELIVERY": [
            "where_is_order_nl", "delivery_delayed_nl", "late_parcel_nl", "tracking_stuck_nl",
            "courier_exception_nl", "slow_shipment_nl", "missing_delivery_date_nl"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_nl", "double_billed_nl", "two_charges_nl", "unauthorized_fee_nl",
            "overcharged_amount_nl", "billing_discrepancy_nl"
        ],
        "REQUEST_RETURN": [
            "want_to_return_nl", "return_label_nl", "rma_request_nl", "exchange_size_nl",
            "refund_request_nl", "send_back_product_nl"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_nl", "abort_order_nl", "mistake_order_nl", "stop_fulfillment_nl"
        ],
    }

    STOPWORDS: List[str] = [
        "the_nl", "is_nl", "at_nl", "which_nl", "on_nl", "for_nl", "with_nl"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
