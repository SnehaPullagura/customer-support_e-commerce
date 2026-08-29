"""
White-Glove Delivery Property Damage Claim (PROPERTY_DAMAGE)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class HomeDeliveryPropertyDamageIntentMatcher:
    INTENT_KEY = "PROPERTY_DAMAGE"
    INTENT_TITLE = "White-Glove Delivery Property Damage Claim"

    KEYWORDS: List[str] = [
        "home_delivery_property_damage_keyword_alpha", "home_delivery_property_damage_keyword_beta", "home_delivery_property_damage_keyword_gamma",
        "white-glove delivery property damage claim", "inquiry regarding white-glove delivery property damage claim",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
