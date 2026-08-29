import pytest
from datetime import datetime, timedelta, timezone
from app.services.returns_service import ReturnsService


def test_returns_eligibility_and_restocking():
    # 1. Order within 10 days is eligible (max 30 days)
    recent_order_date = datetime.now(timezone.utc) - timedelta(days=10)
    res = ReturnsService.validate_return_eligibility(recent_order_date, max_days=30)
    assert res["is_eligible"] is True
    assert res["remaining_days"] >= 19.0

    # 2. Order past 45 days is ineligible
    old_order_date = datetime.now(timezone.utc) - timedelta(days=45)
    res_old = ReturnsService.validate_return_eligibility(old_order_date, max_days=30)
    assert res_old["is_eligible"] is False
    assert res_old["remaining_days"] == 0.0

    # 3. Restocking fee calculation
    assert ReturnsService.calculate_restocking_fee(100.0, "BRAND_NEW") == 0.0
    assert ReturnsService.calculate_restocking_fee(100.0, "OPEN_BOX") == 10.0
    assert ReturnsService.calculate_restocking_fee(200.0, "MISSING_PARTS") == 80.0
