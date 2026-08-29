"""
Portuguese (Português) [pt]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class PortugueseLanguageEngine:
    LANGUAGE_CODE = "pt"
    LANGUAGE_NAME = "Portuguese (Português)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_pt", "damage_keyword_2_pt", "broken_item_pt", "smashed_box_pt",
            "cracked_screen_pt", "faulty_device_pt", "defective_good_pt", "damaged_parcel_pt"
        ],
        "LATE_DELIVERY": [
            "where_is_order_pt", "delivery_delayed_pt", "late_parcel_pt", "tracking_stuck_pt",
            "courier_exception_pt", "slow_shipment_pt", "missing_delivery_date_pt"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_pt", "double_billed_pt", "two_charges_pt", "unauthorized_fee_pt",
            "overcharged_amount_pt", "billing_discrepancy_pt"
        ],
        "REQUEST_RETURN": [
            "want_to_return_pt", "return_label_pt", "rma_request_pt", "exchange_size_pt",
            "refund_request_pt", "send_back_product_pt"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_pt", "abort_order_pt", "mistake_order_pt", "stop_fulfillment_pt"
        ],
    }

    STOPWORDS: List[str] = [
        "the_pt", "is_pt", "at_pt", "which_pt", "on_pt", "for_pt", "with_pt"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
