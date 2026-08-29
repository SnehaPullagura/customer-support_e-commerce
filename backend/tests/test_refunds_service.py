import pytest
from app.services.refunds_service import RefundsService
from app.core.exceptions import ValidationError


def test_refunds_store_credit_and_partial_allocation():
    # 1. Store credit calculation with 10% bonus
    res = RefundsService.calculate_store_credit_bonus(10000, bonus_percentage=10.0)
    assert res["original_amount_cents"] == 10000
    assert res["bonus_cents"] == 1000
    assert res["total_store_credit_cents"] == 11000
    assert res["store_credit_display"] == "$110.00"

    # 2. Line-item partial refund allocation
    line_items = [
        {"product_id": "prod_1", "unit_price_cents": 2500, "quantity": 2, "tax_rate": 0.08},
        {"product_id": "prod_2", "unit_price_cents": 1500, "quantity": 1, "tax_rate": 0.08},
    ]
    # subtotal = 5000 + 1500 = 6500, tax = 400 + 120 = 520, total = 7020
    alloc = RefundsService.allocate_partial_refund(order_total_cents=10000, line_items=line_items)
    assert alloc["total_refund_cents"] == 7020
    assert alloc["remaining_order_balance_cents"] == 2980
    assert len(alloc["allocated_items"]) == 2

    # 3. Over-refund raises ValidationError
    with pytest.raises(ValidationError):
        RefundsService.allocate_partial_refund(order_total_cents=5000, line_items=line_items)
