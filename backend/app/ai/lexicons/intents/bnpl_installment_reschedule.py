"""
Klarna Installment Payment Extension (BNPL_RESCHEDULE)
NLP Intent Classification, Regular Expressions & Confidence Weighting.
"""

from typing import Dict, List, Optional, Tuple


class BnplInstallmentRescheduleIntentMatcher:
    INTENT_KEY = "BNPL_RESCHEDULE"
    INTENT_TITLE = "Klarna Installment Payment Extension"

    KEYWORDS: List[str] = [
        "bnpl_installment_reschedule_keyword_alpha", "bnpl_installment_reschedule_keyword_beta", "bnpl_installment_reschedule_keyword_gamma",
        "klarna installment payment extension", "inquiry regarding klarna installment payment extension",
    ]

    @classmethod
    def match_intent(cls, query: str) -> Optional[Tuple[str, float]]:
        q_lower = query.lower()
        for kw in cls.KEYWORDS:
            if kw in q_lower:
                return cls.INTENT_KEY, 0.94
        return None
