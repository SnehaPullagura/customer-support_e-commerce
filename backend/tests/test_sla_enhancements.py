import pytest
from datetime import datetime, timedelta, timezone
from app.services.sla_service import SLAService


def test_sla_status_and_business_hours():
    now = datetime.now(timezone.utc)

    # 1. Healthy SLA (created 10 mins ago, due in 50 mins = ~16% elapsed)
    healthy = SLAService.calculate_sla_status(
        due_at=now + timedelta(minutes=50),
        created_at=now - timedelta(minutes=10),
    )
    assert healthy["status"] == "HEALTHY"
    assert healthy["is_breached"] is False

    # 2. Critical SLA (created 55 mins ago, due in 5 mins = ~91% elapsed)
    critical = SLAService.calculate_sla_status(
        due_at=now + timedelta(minutes=5),
        created_at=now - timedelta(minutes=55),
    )
    assert critical["status"] == "CRITICAL"

    # 3. Breached SLA
    breached = SLAService.calculate_sla_status(
        due_at=now - timedelta(minutes=10),
        created_at=now - timedelta(hours=2),
    )
    assert breached["status"] == "BREACHED"
    assert breached["is_breached"] is True

    # 4. Business hours calculation: Friday 4:00 PM (16:00) + 4 business hours -> Monday 12:00 PM (12:00)
    friday_4pm = datetime(2026, 8, 28, 16, 0, 0, tzinfo=timezone.utc)  # Friday
    monday_deadline = SLAService.calculate_business_hours_deadline(
        start_time=friday_4pm, duration_hours=4.0, work_start_hour=9, work_end_hour=17
    )
    assert monday_deadline.weekday() == 0  # Monday
    assert monday_deadline.hour == 12
