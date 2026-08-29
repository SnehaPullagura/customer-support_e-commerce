"""
German (Deutsch) [de]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class GermanLanguageEngine:
    LANGUAGE_CODE = "de"
    LANGUAGE_NAME = "German (Deutsch)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_de", "damage_keyword_2_de", "broken_item_de", "smashed_box_de",
            "cracked_screen_de", "faulty_device_de", "defective_good_de", "damaged_parcel_de"
        ],
        "LATE_DELIVERY": [
            "where_is_order_de", "delivery_delayed_de", "late_parcel_de", "tracking_stuck_de",
            "courier_exception_de", "slow_shipment_de", "missing_delivery_date_de"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_de", "double_billed_de", "two_charges_de", "unauthorized_fee_de",
            "overcharged_amount_de", "billing_discrepancy_de"
        ],
        "REQUEST_RETURN": [
            "want_to_return_de", "return_label_de", "rma_request_de", "exchange_size_de",
            "refund_request_de", "send_back_product_de"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_de", "abort_order_de", "mistake_order_de", "stop_fulfillment_de"
        ],
    }

    STOPWORDS: List[str] = [
        "the_de", "is_de", "at_de", "which_de", "on_de", "for_de", "with_de"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
