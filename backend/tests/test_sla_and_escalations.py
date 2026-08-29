"""
Unit & Integration tests for SLA tracking, pause/resume, and Escalation matrix.
"""

from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.customer import CustomerCreate
from app.schemas.case import CaseCreate
from app.schemas.sla import SLAPolicyCreate
from app.services.customer_service import CustomerService
from app.services.case_service import CaseService
from app.services.sla_service import SLAService
from app.services.escalation_service import EscalationService


@pytest.mark.asyncio
async def test_sla_lifecycle_and_pause(test_session: AsyncSession):
    # 1. Customer & Case
    customer = await CustomerService.create_customer(
        test_session,
        CustomerCreate(first_name="Clark", last_name="Kent", email="clark@dailyplanet.com"),
    )
    case = await CaseService.create_case(
        test_session,
        CaseCreate(
            customer_id=customer.id,
            title="Express delivery delayed",
            description="Package was not delivered on time.",
            category="DELIVERY",
            priority="CRITICAL",
        ),
    )

    # 2. Start SLA Tracker
    tracker = await SLAService.start_sla_tracker(test_session, case.id)
    assert tracker.is_paused is False
    now_utc = datetime.now(timezone.utc)
    first_due = tracker.first_response_due_at.replace(tzinfo=timezone.utc) if tracker.first_response_due_at.tzinfo is None else tracker.first_response_due_at
    assert first_due > now_utc - timedelta(minutes=1)

    # 3. Status changes to WAITING_FOR_CUSTOMER -> Should Pause
    await CaseService.update_status(test_session, case.id, "WAITING_FOR_CUSTOMER")
    await SLAService.handle_status_change(test_session, case.id, "WAITING_FOR_CUSTOMER")
    await test_session.refresh(tracker)
    assert tracker.is_paused is True
    assert tracker.paused_at is not None

    # 4. Status changes back to IN_PROGRESS -> Should Resume
    await CaseService.update_status(test_session, case.id, "IN_PROGRESS")
    await SLAService.handle_status_change(test_session, case.id, "IN_PROGRESS")
    await test_session.refresh(tracker)
    assert tracker.is_paused is False


@pytest.mark.asyncio
async def test_escalation_flow(test_session: AsyncSession):
    customer = await CustomerService.create_customer(
        test_session,
        CustomerCreate(first_name="Barry", last_name="Allen", email="barry@centralcity.org"),
    )
    case = await CaseService.create_case(
        test_session,
        CaseCreate(
            customer_id=customer.id,
            title="Complex multi-order logistics discrepancy",
            description="Need immediate supervisor review.",
            priority="MEDIUM",
        ),
    )

    # Escalate to Manager
    event = await EscalationService.escalate_case(
        test_session,
        case_id=case.id,
        reason="Customer requested supervisor due to repeated shipping delays",
        escalate_to_role="MANAGER",
        notes="High risk of churn",
    )
    assert event.id is not None
    assert event.escalation_level == 2

    # Verify case status updated to ESCALATED
    await test_session.refresh(case)
    assert case.is_escalated is True
    assert case.status == "ESCALATED"
    assert case.priority == "HIGH"
