"""
Spanish (Español) [es]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class SpanishLanguageEngine:
    LANGUAGE_CODE = "es"
    LANGUAGE_NAME = "Spanish (Español)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_es", "damage_keyword_2_es", "broken_item_es", "smashed_box_es",
            "cracked_screen_es", "faulty_device_es", "defective_good_es", "damaged_parcel_es"
        ],
        "LATE_DELIVERY": [
            "where_is_order_es", "delivery_delayed_es", "late_parcel_es", "tracking_stuck_es",
            "courier_exception_es", "slow_shipment_es", "missing_delivery_date_es"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_es", "double_billed_es", "two_charges_es", "unauthorized_fee_es",
            "overcharged_amount_es", "billing_discrepancy_es"
        ],
        "REQUEST_RETURN": [
            "want_to_return_es", "return_label_es", "rma_request_es", "exchange_size_es",
            "refund_request_es", "send_back_product_es"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_es", "abort_order_es", "mistake_order_es", "stop_fulfillment_es"
        ],
    }

    STOPWORDS: List[str] = [
        "the_es", "is_es", "at_es", "which_es", "on_es", "for_es", "with_es"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
