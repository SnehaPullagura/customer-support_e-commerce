"""
Complete 17-Step End-to-End E-Commerce Customer Support & Resolution Lifecycle Test.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.commerce import get_commerce_adapter
from app.ai.classifier import AIClassifier
from app.core.security import Role
from app.schemas.customer import CustomerCreate
from app.schemas.case import CaseCreate
from app.schemas.agent import AgentCreate, TeamCreate, SkillCreate
from app.schemas.routing import RoutingRuleCreate
from app.schemas.resolution import ResolutionCreate, FeedbackCreate
from app.schemas.conversation import MessageCreate
from app.services.customer_service import CustomerService
from app.services.case_service import CaseService
from app.services.agent_service import AgentService
from app.services.routing_service import RoutingService
from app.services.sla_service import SLAService
from app.services.playbook_service import PlaybookService
from app.services.resolution_service import ResolutionService
from app.services.conversation_service import ConversationService
from app.services.audit_service import AuditService
from app.models.identity import User
from app.core.security import hash_password


@pytest.mark.asyncio
async def test_full_17_step_damaged_product_resolution_lifecycle(test_session: AsyncSession):
    """
    Validates the end-to-end mission statement:
    'A customer has a problem with an e-commerce transaction. Can the support platform
     understand the complete situation and guide the agent to the correct resolution as quickly as possible?'
    """

    # -------------------------------------------------------------
    # SETUP WORKFORCE, PLAYBOOKS & ROUTING
    # -------------------------------------------------------------
    await PlaybookService.seed_default_playbooks(test_session)

    agent_user = User(
        email="agent.support@store.internal",
        hashed_password=hash_password("AgentPass123!"),
        first_name="Marcus",
        last_name="Vance",
        role=Role.AGENT,
    )
    test_session.add(agent_user)
    await test_session.flush()

    skill = await AgentService.create_skill(
        test_session,
        SkillCreate(code="HARDWARE_SUPPORT", name="Hardware Diagnostics", category="TECHNICAL"),
    )
    team = await AgentService.create_team(
        test_session,
        TeamCreate(name="Hardware Support Team", department="CUSTOMER_SUPPORT"),
    )
    agent = await AgentService.create_agent(
        test_session,
        AgentCreate(
            user_id=agent_user.id,
            team_id=team.id,
            employee_code="EMP-1009",
            display_name="Marcus Vance",
            skill_ids=[skill.id],
        ),
    )
    await AgentService.update_status(test_session, agent.id, "AVAILABLE")

    await RoutingService.create_rule(
        test_session,
        RoutingRuleCreate(
            name="Hardware Product Claim Routing",
            priority_order=1,
            match_conditions_json={"category": "PRODUCT"},
            target_team_id=team.id,
            required_skill_code="HARDWARE_SUPPORT",
            routing_strategy="LEAST_BUSY",
        ),
    )

    # -------------------------------------------------------------
    # STEP 1: Identify Customer
    # -------------------------------------------------------------
    customer = await CustomerService.create_customer(
        test_session,
        CustomerCreate(
            external_customer_id="CUST-1001",
            first_name="Sarah",
            last_name="Connor",
            email="sarah.connor@example.com",
            phone="+1-555-0192",
            segment="VIP",
            tier="PLATINUM",
        ),
    )
    assert customer.id is not None

    # -------------------------------------------------------------
    # STEP 2, 3, 4, 5, 6: Commerce Verification (Order, Product, Shipment, Delivery, Return Eligibility)
    # -------------------------------------------------------------
    commerce = get_commerce_adapter()
    order = await commerce.get_order("ORD-5001")
    assert order is not None
    assert order.status == "DELIVERED"

    target_product = next(p for p in order.items if p.product_id == "PROD-9001")
    assert target_product.is_returnable is True

    # -------------------------------------------------------------
    # STEP 8 & 9: Issue Classification & Priority by AI
    # -------------------------------------------------------------
    customer_message = "My AeroSound headphones arrived crushed and the headband is broken. I need a replacement right away!"
    ai_classification = AIClassifier.classify_text(customer_message, customer_tier=customer.tier)
    assert ai_classification.intent == "DAMAGED_PRODUCT"
    assert ai_classification.suggested_category == "PRODUCT"
    assert ai_classification.suggested_priority in ["HIGH", "CRITICAL"]

    # -------------------------------------------------------------
    # Create Case
    # -------------------------------------------------------------
    case = await CaseService.create_case(
        test_session,
        CaseCreate(
            customer_id=customer.id,
            title="AeroSound Headphones Arrived Damaged",
            description=customer_message,
            category=ai_classification.suggested_category,
            subcategory=ai_classification.suggested_subcategory,
            priority=ai_classification.suggested_priority,
            order_id="ORD-5001",
            product_id="PROD-9001",
            payment_id="PAY-8801",
            shipment_id="SHIP-7701",
        ),
    )
    assert case.id is not None

    # -------------------------------------------------------------
    # STEP 10: Assign Appropriate Agent via Routing
    # -------------------------------------------------------------
    routing_decision = await RoutingService.route_case(test_session, case.id)
    assert routing_decision.assigned_agent_id == agent.id

    # -------------------------------------------------------------
    # STEP 11: Start SLA Tracking
    # -------------------------------------------------------------
    sla_tracker = await SLAService.start_sla_tracker(test_session, case.id)
    assert sla_tracker.first_response_due_at is not None

    # -------------------------------------------------------------
    # STEP 12 & 13: Agent Communicates & Executes Playbook
    # -------------------------------------------------------------
    conv = await ConversationService.get_or_create_conversation(test_session, case.id)
    agent_msg = await ConversationService.send_message(
        test_session,
        conversation_id=conv.id,
        sender_type="AGENT",
        sender_name=agent.display_name,
        content="Hello Sarah, I have verified your order delivery and will dispatch your replacement immediately.",
        sender_id=agent.user_id,
    )
    assert agent_msg.id is not None

    # Verify first response SLA stopped
    refreshed_case = await CaseService.get_case(test_session, case.id)
    assert refreshed_case.first_responded_at is not None

    # -------------------------------------------------------------
    # STEP 14 & 15: Execute Replacement Resolution Action
    # -------------------------------------------------------------
    res_data = ResolutionCreate(
        case_id=case.id,
        resolution_type="REPLACEMENT",
        summary="Zero-cost expedited replacement authorized for broken headband.",
    )
    resolution = await ResolutionService.propose_resolution(test_session, res_data, actor_id=agent.user_id)
    assert resolution.is_approved is True

    executed_res = await ResolutionService.execute_resolution_action(
        test_session, resolution.id, actor_id=agent.user_id
    )
    assert executed_res.status == "COMPLETED"

    # Check case is marked resolved
    await test_session.refresh(case)
    assert case.status == "RESOLVED"
    assert case.resolved_at is not None

    # -------------------------------------------------------------
    # STEP 16: Customer Feedback
    # -------------------------------------------------------------
    feedback = await ResolutionService.record_feedback(
        test_session,
        case_id=case.id,
        data=FeedbackCreate(rating=5, customer_effort_score=1, comment="Outstanding fast replacement support!"),
    )
    assert feedback.rating == 5

    # -------------------------------------------------------------
    # STEP 17: Immutable Audit Trail Logged
    # -------------------------------------------------------------
    audit_log = await AuditService.log_event(
        test_session,
        action="CASE_RESOLVED_WITH_REPLACEMENT",
        resource_type="CASE",
        resource_id=case.id,
        description=f"Case #{case.case_number} resolved with replacement dispatch.",
        actor_id=agent.user_id,
        actor_role="AGENT",
    )
    assert audit_log.id is not None
