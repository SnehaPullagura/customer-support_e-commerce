"""
Return & Warranty Eligibility Rules Engine with Condition Audits.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel

from app.domain.taxonomy.categories import CategoryTaxonomyService, CategoryPolicy


class ReturnEligibilityResult(BaseModel):
    is_eligible: bool
    rejection_reason: Optional[str] = None
    days_since_delivery: int
    allowed_return_window_days: int
    restocking_fee_cents: int = 0
    requires_rma_inspection: bool = True
    requires_return_label: bool = True
    is_hazardous_shipping: bool = False
    is_hygiene_sealed: bool = False
    recommended_action: str = "GENERATE_RETURN_LABEL"


class ReturnEligibilityEngine:
    @staticmethod
    def evaluate_return_request(
        category_code: str,
        delivery_date: datetime,
        item_price_cents: int,
        is_opened: bool = False,
        is_hygiene_seal_broken: bool = False,
        is_damaged_by_customer: bool = False,
        is_defective: bool = False,
    ) -> ReturnEligibilityResult:
        now = datetime.now(timezone.utc)
        if delivery_date.tzinfo is None:
            delivery_date = delivery_date.replace(tzinfo=timezone.utc)

        days_since_delivery = max(0, (now - delivery_date).days)
        policy = CategoryTaxonomyService.get_category_policy(category_code)

        # 1. Final Sale Check
        if policy.is_final_sale and not is_defective:
            return ReturnEligibilityResult(
                is_eligible=False,
                rejection_reason=f"Items in category '{policy.category_name}' are marked Final Sale and are non-returnable.",
                days_since_delivery=days_since_delivery,
                allowed_return_window_days=policy.return_window_days,
                recommended_action="REJECT_FINAL_SALE",
            )

        # 2. Return Window Check
        if days_since_delivery > policy.return_window_days:
            # If item is defective and within manufacturer warranty, offer warranty claim instead
            if is_defective:
                return ReturnEligibilityResult(
                    is_eligible=False,
                    rejection_reason=f"Standard {policy.return_window_days}-day return window expired, but item is eligible for Manufacturer Warranty repair or replacement.",
                    days_since_delivery=days_since_delivery,
                    allowed_return_window_days=policy.return_window_days,
                    recommended_action="INITIATE_WARRANTY_CLAIM",
                )
            return ReturnEligibilityResult(
                is_eligible=False,
                rejection_reason=f"Return window expired ({days_since_delivery} days elapsed, policy limit is {policy.return_window_days} days).",
                days_since_delivery=days_since_delivery,
                allowed_return_window_days=policy.return_window_days,
                recommended_action="REJECT_OUT_OF_POLICY",
            )

        # 3. Hygiene Sensitivity Check
        if policy.is_hygiene_sensitive and is_hygiene_seal_broken and not is_defective:
            return ReturnEligibilityResult(
                is_eligible=False,
                rejection_reason=f"Due to health & hygiene safety standards, opened {policy.category_name} with broken seals cannot be returned.",
                days_since_delivery=days_since_delivery,
                allowed_return_window_days=policy.return_window_days,
                is_hygiene_sealed=True,
                recommended_action="REJECT_HYGIENE_VIOLATION",
            )

        # 4. Customer Abuse / Accidental Damage Check
        if is_damaged_by_customer:
            return ReturnEligibilityResult(
                is_eligible=False,
                rejection_reason="Physical damage resulting from accidental drops, liquid submersion, or misuse is not covered under return policy.",
                days_since_delivery=days_since_delivery,
                allowed_return_window_days=policy.return_window_days,
                recommended_action="REJECT_CUSTOMER_DAMAGE",
            )

        # 5. Restocking fee calculation
        restocking_fee = 0
        if policy.restocking_fee_percent > 0 and is_opened and not is_defective:
            restocking_fee = int(item_price_cents * (policy.restocking_fee_percent / 100.0))

        # 6. Low Value Returnless Refund Optimization:
        # If item value < $15.00 and return shipping cost exceeds item value, grant returnless refund
        if item_price_cents < 1500 and is_defective:
            return ReturnEligibilityResult(
                is_eligible=True,
                days_since_delivery=days_since_delivery,
                allowed_return_window_days=policy.return_window_days,
                restocking_fee_cents=0,
                requires_return_label=False,
                requires_rma_inspection=False,
                recommended_action="ISSUE_RETURNLESS_REFUND",
            )

        return ReturnEligibilityResult(
            is_eligible=True,
            days_since_delivery=days_since_delivery,
            allowed_return_window_days=policy.return_window_days,
            restocking_fee_cents=restocking_fee,
            is_hazardous_shipping=policy.is_hazmat,
            requires_return_label=True,
            requires_rma_inspection=policy.requires_serial_number or item_price_cents > 10000,
            recommended_action="AUTHORIZE_RMA_WITH_PREPAID_LABEL",
        )
