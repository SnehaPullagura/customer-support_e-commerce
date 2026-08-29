"""
Unit & Integration tests for Commerce Adapters, Resolution Actions, and Playbooks.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.commerce import get_commerce_adapter
from app.schemas.customer import CustomerCreate
from app.schemas.case import CaseCreate
from app.schemas.resolution import ResolutionCreate
from app.services.customer_service import CustomerService
from app.services.case_service import CaseService
from app.services.resolution_service import ResolutionService
from app.services.playbook_service import PlaybookService
from app.services.refunds_service import RefundsService
from app.schemas.refunds import RefundRequestCreate


@pytest.mark.asyncio
async def test_mock_commerce_adapter():
    commerce = get_commerce_adapter()
    order = await commerce.get_order("ORD-5001")
    assert order is not None
    assert order.customer_id == "CUST-1001"
    assert len(order.items) == 2
    assert order.status == "DELIVERED"

    # Commerce graph
    graph = await commerce.get_commerce_graph(external_customer_id="CUST-1001", order_id="ORD-5001")
    assert graph.customer is not None
    assert graph.active_order is not None
    assert len(graph.recent_orders) >= 1


@pytest.mark.asyncio
async def test_playbook_execution(test_session: AsyncSession):
    # Seed default playbooks
    await PlaybookService.seed_default_playbooks(test_session)

    customer = await CustomerService.create_customer(
        test_session,
        CustomerCreate(first_name="Wanda", last_name="Maximoff", email="wanda@westview.org"),
    )
    case = await CaseService.create_case(
        test_session,
        CaseCreate(
            customer_id=customer.id,
            title="AeroSound headphones arrived with broken headband",
            description="Item box was crushed and headphone band is broken.",
            category="PRODUCT",
            order_id="ORD-5001",
            product_id="PROD-9001",
        ),
    )

    # Start playbook
    execution = await PlaybookService.start_execution(
        test_session, case_id=case.id, playbook_id="DAMAGED_PRODUCT_PLAYBOOK"
    )
    assert execution.status == "IN_PROGRESS"
    assert execution.current_step_order == 1

    # Execute step 1
    playbook = await PlaybookService.get_playbook(test_session, "DAMAGED_PRODUCT_PLAYBOOK")
    step1 = playbook.steps[0]
    updated_exec = await PlaybookService.execute_step(
        test_session,
        execution_id=execution.id,
        step_id=step1.id,
        status="COMPLETED",
        notes="Order ORD-5001 verified delivered within 3 days.",
    )
    assert updated_exec.current_step_order == 2


@pytest.mark.asyncio
async def test_refund_idempotency_and_ledger(test_session: AsyncSession):
    customer = await CustomerService.create_customer(
        test_session,
        CustomerCreate(first_name="Peter", last_name="Parker", email="peter@dailybugle.com"),
    )
    case = await CaseService.create_case(
        test_session,
        CaseCreate(
            customer_id=customer.id,
            title="Refund request for damaged item",
            description="Item was unusable.",
            category="PAYMENT",
            payment_id="PAY-8801",
            order_id="ORD-5001",
        ),
    )

    refund_data = RefundRequestCreate(
        case_id=case.id,
        customer_id=customer.id,
        payment_id="PAY-8801",
        order_id="ORD-5001",
        amount_cents=4500,  # $45.00 (under $100 threshold, auto-executes)
        currency="USD",
        reason="Damaged item compensation",
    )

    idem_key = "test-idempotency-key-refund-001"

    # First call: executes
    req1 = await RefundsService.create_refund_request(
        test_session, data=refund_data, idempotency_key=idem_key
    )
    assert req1.status == "COMPLETED"
    assert req1.gateway_refund_id is not None

    # Second call with same idempotency key: returns cached / existing without error
    req2 = await RefundsService.create_refund_request(
        test_session, data=refund_data, idempotency_key=idem_key
    )
    assert req2.id == req1.id
    assert req2.gateway_refund_id == req1.gateway_refund_id
