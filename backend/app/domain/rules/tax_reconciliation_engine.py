"""
US State Sales Tax, VAT & Duty Apportionment and Refund Calculations Engine.
"""

from typing import Dict, Tuple


# US State Standard Sales Tax Rates
STATE_SALES_TAX_RATES: Dict[str, float] = {
    "CA": 0.0725, "TX": 0.0625, "NY": 0.0400, "FL": 0.0600, "IL": 0.0625,
    "PA": 0.0600, "OH": 0.0575, "GA": 0.0400, "NC": 0.0475, "MI": 0.0600,
    "NJ": 0.06625, "VA": 0.0530, "WA": 0.0650, "AZ": 0.0560, "MA": 0.0625,
    "TN": 0.0700, "IN": 0.0700, "MO": 0.04225, "MD": 0.0600, "WI": 0.0500,
    "CO": 0.0290, "MN": 0.06875, "SC": 0.0600, "AL": 0.0400, "LA": 0.0445,
    "KY": 0.0600, "OR": 0.0000, "NH": 0.0000, "MT": 0.0000, "DE": 0.0000,
}


class TaxReconciliationEngine:
    @staticmethod
    def get_state_tax_rate(state_code: str) -> float:
        return STATE_SALES_TAX_RATES.get(state_code.upper().strip(), 0.05)

    @staticmethod
    def calculate_item_tax(price_cents: int, state_code: str) -> int:
        rate = TaxReconciliationEngine.get_state_tax_rate(state_code)
        return int(round(price_cents * rate))

    @staticmethod
    def apportion_partial_refund_tax(
        total_order_item_cents: int,
        total_tax_paid_cents: int,
        refund_item_cents: int,
    ) -> Tuple[int, int]:
        """
        Calculates proportional tax refund for partial order returns.
        Returns: (refund_subtotal_cents, refund_tax_cents)
        """
        if total_order_item_cents <= 0:
            return refund_item_cents, 0
        ratio = refund_item_cents / float(total_order_item_cents)
        refund_tax = int(round(total_tax_paid_cents * ratio))
        return refund_item_cents, refund_tax
