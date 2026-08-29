"""
Temperature Excursion Biological Hazard Matrix
Enterprise Resolution Decision Rules & Payout Matrix.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PerishableColdChainMatrix:
    MATRIX_KEY = "perishable_cold_chain_matrix"
    MATRIX_TITLE = "Temperature Excursion Biological Hazard Matrix"

    DECISION_TIERS: List[Dict[str, Any]] = [
        {
            "tier_level": "TIER_1_STANDARD",
            "max_payout_cents": 5000,
            "requires_lead_approval": False,
            "action": "AUTO_APPROVE_REFUND_OR_REPLACEMENT",
        },
        {
            "tier_level": "TIER_2_ELEVATED",
            "max_payout_cents": 25000,
            "requires_lead_approval": True,
            "action": "SENIOR_LEAD_REVIEW_REQUIRED",
        },
        {
            "tier_level": "TIER_3_EXECUTIVE",
            "max_payout_cents": 100000,
            "requires_lead_approval": True,
            "action": "DIRECTOR_FINANCIAL_SIGN_OFF",
        },
    ]

    @classmethod
    def evaluate_payout_tier(cls, amount_cents: int) -> Dict[str, Any]:
        for tier in cls.DECISION_TIERS:
            if amount_cents <= tier["max_payout_cents"]:
                return tier
        return cls.DECISION_TIERS[-1]
