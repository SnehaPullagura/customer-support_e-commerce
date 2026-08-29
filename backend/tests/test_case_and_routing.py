"""
Unit & Integration tests for Case Management, State Transitions, and Intelligent Routing.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.customer import CustomerCreate
from app.schemas.case import CaseCreate, CaseAssignRequest
from app.schemas.agent import AgentCreate, TeamCreate, SkillCreate
from app.schemas.routing import RoutingRuleCreate
from app.services.customer_service import CustomerService
from app.services.case_service import CaseService
from app.services.agent_service import AgentService
from app.services.routing_service import RoutingService
from app.models.identity import User
from app.core.security import hash_password, Role


@pytest.mark.asyncio
async def test_case_creation_and_routing(test_session: AsyncSession):
    # 1. Create customer
    cust_data = CustomerCreate(
        first_name="Bruce",
        last_name="Wayne",
        email="bruce.wayne@waynecorp.com",
        segment="VIP",
        tier="PLATINUM",
    )
    customer = await CustomerService.create_customer(test_session, cust_data)

    # 2. Create User and Agent
    user = User(
        email="agent.diana@support.internal",
        hashed_password=hash_password("Pass123!"),
        first_name="Diana",
        last_name="Prince",
        role=Role.AGENT,
    )
    test_session.add(user)
    await test_session.flush()

    skill = await AgentService.create_skill(
        test_session,
        SkillCreate(code="PAYMENT_DISPUTES", name="Payment Disputes", category="BILLING"),
    )
    team = await AgentService.create_team(
        test_session,
        TeamCreate(name="Finance Operations", department="FINANCE"),
    )
    agent = await AgentService.create_agent(
        test_session,
        AgentCreate(
            user_id=user.id,
            team_id=team.id,
            employee_code="EMP-7001",
            display_name="Diana Prince",
            max_active_cases=5,
            skill_ids=[skill.id],
        ),
    )
    # Set agent available
    await AgentService.update_status(test_session, agent.id, "AVAILABLE")

    # 3. Create Routing Rule
    await RoutingService.create_rule(
        test_session,
        RoutingRuleCreate(
            name="Route VIP Billing",
            priority_order=1,
            match_conditions_json={"category": "PAYMENT"},
            target_team_id=team.id,
            required_skill_code="PAYMENT_DISPUTES",
            routing_strategy="LEAST_BUSY",
        ),
    )

    # 4. Create Case
    case_data = CaseCreate(
        customer_id=customer.id,
        title="Double charged on latest subscription renewal",
        description="I was billed twice on order #ORD-5001 for $289.97.",
        category="PAYMENT",
        priority="HIGH",
        order_id="ORD-5001",
    )
    case = await CaseService.create_case(test_session, case_data)
    assert case.case_number.startswith("CASE-")

    # 5. Execute Routing
    decision = await RoutingService.route_case(test_session, case.id)
    assert decision.assigned_agent_id == agent.id
    assert decision.assigned_team_id == team.id

    # 6. Status transitions
    updated_case = await CaseService.update_status(test_session, case.id, "IN_PROGRESS")
    assert updated_case.status == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_case_api(client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create customer first
    cust_res = await client.post(
        "/api/v1/customers",
        json={"first_name": "Tony", "last_name": "Stark", "email": "tony@stark.com"},
        headers=headers,
    )
    cust_id = cust_res.json()["data"]["id"]

    # Create Case
    case_payload = {
        "customer_id": cust_id,
        "title": "Arc reactor battery arrived scratched",
        "description": "Item was damaged upon opening shipping container.",
        "category": "PRODUCT",
        "priority": "HIGH",
    }
    res = await client.post("/api/v1/cases", json=case_payload, headers=headers)
    assert res.status_code == 201
    case_data = res.json()["data"]
    assert case_data["status"] in ["NEW", "OPEN"]

    # Get Case
    case_id = case_data["id"]
    res_get = await client.get(f"/api/v1/cases/{case_id}", headers=headers)
    assert res_get.status_code == 200
    assert len(res_get.json()["data"]["timeline_events"]) >= 1
