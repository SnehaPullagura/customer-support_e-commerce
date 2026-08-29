"""
Driver Misdelivery Wrong Street Geofence (GEOFENCE_ERROR)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class GeofenceDriverMisdeliveryIntentMatcher:
    INTENT_KEY = "GEOFENCE_ERROR"
    INTENT_TITLE = "Driver Misdelivery Wrong Street Geofence"

    KEYWORDS: List[str] = [
        "geofence_driver_misdelivery_keyword_alpha", "geofence_driver_misdelivery_keyword_beta", "geofence_driver_misdelivery_keyword_gamma",
        "driver misdelivery wrong street geofence", "inquiry regarding driver misdelivery wrong street geofence",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
