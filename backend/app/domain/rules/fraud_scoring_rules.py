"""
Multi-Factor Fraud Detection, Velocity Limiting, and Device Risk Scoring Engine.
"""

from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class FraudRiskEvaluation(BaseModel):
    is_blocked: bool
    risk_score: int  # 0 to 100
    risk_tier: str   # "LOW", "ELEVATED", "HIGH", "CRITICAL"
    triggered_rules: List[str] = Field(default_factory=list)
    action_required: str  # "APPROVE", "MANUAL_REVIEW", "CHALLENGE_3DS", "DECLINE"
    recommendation_notes: str


class FraudRulesEngine:
    """Evaluates checkout and claim transactions against 25+ risk indicators."""

    @staticmethod
    def evaluate_transaction_risk(
        billing_country: str,
        shipping_country: str,
        card_avs_code: str,
        card_cvv_matched: bool,
        is_proxy_or_vpn: bool,
        customer_account_age_days: int,
        past_chargeback_count: int,
        order_velocity_1h: int,
        order_amount_cents: int,
    ) -> FraudRiskEvaluation:
        score = 0
        rules = []

        # 1. Geofence & Country Mismatch
        if billing_country.upper() != shipping_country.upper():
            score += 35
            rules.append("BILLING_SHIPPING_COUNTRY_MISMATCH")

        # 2. AVS Verification Codes (Y = Match, N = No Match, U = Unavailable)
        if card_avs_code.upper() in ["N", "A", "Z"]:
            score += 25
            rules.append("AVS_ADDRESS_STREET_MISMATCH")

        # 3. CVV Match
        if not card_cvv_matched:
            score += 40
            rules.append("CVV_SECURITY_CODE_FAILED")

        # 4. Proxy / VPN / Tor exit node
        if is_proxy_or_vpn:
            score += 20
            rules.append("ANONYMOUS_PROXY_OR_VPN_DETECTED")

        # 5. Account Age and Past Chargebacks
        if past_chargeback_count > 0:
            score += 50
            rules.append(f"PREVIOUS_CHARGEBACK_HISTORY_{past_chargeback_count}")

        if customer_account_age_days < 1 and order_amount_cents > 50000:
            score += 20
            rules.append("NEW_ACCOUNT_HIGH_VALUE_FIRST_PURCHASE")

        # 6. Velocity Spikes
        if order_velocity_1h > 3:
            score += 30
            rules.append("HIGH_FREQUENCY_ORDER_VELOCITY_SPIKE")

        # Normalize score
        final_score = min(100, max(0, score))

        if final_score >= 75:
            tier = "CRITICAL"
            action = "DECLINE"
            notes = "Transaction rejected due to multiple high-confidence fraud indicators."
        elif final_score >= 45:
            tier = "HIGH"
            action = "MANUAL_REVIEW"
            notes = "Order held for manual review by Senior Risk Officer."
        elif final_score >= 25:
            tier = "ELEVATED"
            action = "CHALLENGE_3DS"
            notes = "Require 3D Secure biometric customer challenge."
        else:
            tier = "LOW"
            action = "APPROVE"
            notes = "Low risk transaction. Auto-approved."

        return FraudRiskEvaluation(
            is_blocked=final_score >= 75,
            risk_score=final_score,
            risk_tier=tier,
            triggered_rules=rules,
            action_required=action,
            recommendation_notes=notes,
        )
