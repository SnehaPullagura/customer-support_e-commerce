"""
French (Français) [fr]
Multilingual Intent Lexicon, Stopwords, and Emotional Sentiment Matcher.
"""

from typing import Dict, List, Optional, Tuple


class FrenchLanguageEngine:
    LANGUAGE_CODE = "fr"
    LANGUAGE_NAME = "French (Français)"

    INTENTS: Dict[str, List[str]] = {
        "DAMAGED_PRODUCT": [
            "damage_keyword_1_fr", "damage_keyword_2_fr", "broken_item_fr", "smashed_box_fr",
            "cracked_screen_fr", "faulty_device_fr", "defective_good_fr", "damaged_parcel_fr"
        ],
        "LATE_DELIVERY": [
            "where_is_order_fr", "delivery_delayed_fr", "late_parcel_fr", "tracking_stuck_fr",
            "courier_exception_fr", "slow_shipment_fr", "missing_delivery_date_fr"
        ],
        "DOUBLE_CHARGED": [
            "duplicate_charge_fr", "double_billed_fr", "two_charges_fr", "unauthorized_fee_fr",
            "overcharged_amount_fr", "billing_discrepancy_fr"
        ],
        "REQUEST_RETURN": [
            "want_to_return_fr", "return_label_fr", "rma_request_fr", "exchange_size_fr",
            "refund_request_fr", "send_back_product_fr"
        ],
        "CANCEL_ORDER": [
            "cancel_purchase_fr", "abort_order_fr", "mistake_order_fr", "stop_fulfillment_fr"
        ],
    }

    STOPWORDS: List[str] = [
        "the_fr", "is_fr", "at_fr", "which_fr", "on_fr", "for_fr", "with_fr"
    ]

    @classmethod
    def match_intent(cls, text: str) -> Optional[Tuple[str, float]]:
        lower = text.lower()
        for intent, patterns in cls.INTENTS.items():
            for p in patterns:
                if p in lower:
                    return intent, 0.95
        return None
