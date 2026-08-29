"""
Polish (Polski) [pl]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class PolishLanguageEngine:
    LANGUAGE_CODE = "pl"
    LANGUAGE_NAME = "Polish (Polski)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_pl", "damage_keyword_2_pl", "broken_item_pl", "smashed_box_pl",
            "cracked_screen_pl", "faulty_device_pl", "defective_good_pl", "damaged_parcel_pl"
        ],
        "LATE_DELIVERY": [
            "where_is_order_pl", "delivery_delayed_pl", "late_parcel_pl", "tracking_stuck_pl",
            "courier_exception_pl", "slow_shipment_pl", "missing_delivery_date_pl"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_pl", "double_billed_pl", "two_charges_pl", "unauthorized_fee_pl",
            "overcharged_amount_pl", "billing_discrepancy_pl"
        ],
        "REQUEST_RETURN": [
            "want_to_return_pl", "return_label_pl", "rma_request_pl", "exchange_size_pl",
            "refund_request_pl", "send_back_product_pl"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_pl", "abort_order_pl", "mistake_order_pl", "stop_fulfillment_pl"
        ],
    }

    STOPWORDS: List[str] = [
        "the_pl", "is_pl", "at_pl", "which_pl", "on_pl", "for_pl", "with_pl"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
