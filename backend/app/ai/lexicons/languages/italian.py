"""
Italian (Italiano) [it]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class ItalianLanguageEngine:
    LANGUAGE_CODE = "it"
    LANGUAGE_NAME = "Italian (Italiano)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_it", "damage_keyword_2_it", "broken_item_it", "smashed_box_it",
            "cracked_screen_it", "faulty_device_it", "defective_good_it", "damaged_parcel_it"
        ],
        "LATE_DELIVERY": [
            "where_is_order_it", "delivery_delayed_it", "late_parcel_it", "tracking_stuck_it",
            "courier_exception_it", "slow_shipment_it", "missing_delivery_date_it"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_it", "double_billed_it", "two_charges_it", "unauthorized_fee_it",
            "overcharged_amount_it", "billing_discrepancy_it"
        ],
        "REQUEST_RETURN": [
            "want_to_return_it", "return_label_it", "rma_request_it", "exchange_size_it",
            "refund_request_it", "send_back_product_it"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_it", "abort_order_it", "mistake_order_it", "stop_fulfillment_it"
        ],
    }

    STOPWORDS: List[str] = [
        "the_it", "is_it", "at_it", "which_it", "on_it", "for_it", "with_it"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
