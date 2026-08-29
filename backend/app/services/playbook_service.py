"""
Resolution Playbook Engine and Interactive Structured Workflows.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.core.exceptions import EntityNotFoundError, ValidationError, PlaybookExecutionError
from app.models.case import Case, CaseTimelineEvent
from app.models.playbook import Playbook, PlaybookStep, PlaybookExecution, PlaybookStepLog
from app.schemas.playbook import PlaybookCreate, PlaybookStepCreate


DEFAULT_PLAYBOOKS = [
    {
        "code": "DAMAGED_PRODUCT_PLAYBOOK",
        "name": "Damaged Product Resolution Playbook",
        "category": "PRODUCT",
        "description": "Standard operational workflow for investigating and resolving damaged-in-transit product claims.",
        "steps": [
            {
                "step_order": 1,
                "step_key": "IDENTIFY_ORDER_AND_DELIVERY",
                "title": "Identify Order & Verify Delivery Date",
                "instructions": "Confirm the order number, product SKU, and ensure delivery occurred within the past 30 days.",
                "action_type": "API_VERIFICATION",
                "is_mandatory": True,
            },
            {
                "step_order": 2,
                "step_key": "INSPECT_DAMAGE_EVIDENCE",
                "title": "Inspect Photo / Video Evidence",
                "instructions": "Review damage photo attachment uploaded by the customer or prompt customer for photo.",
                "action_type": "REQUIRE_ATTACHMENT",
                "is_mandatory": True,
            },
            {
                "step_order": 3,
                "step_key": "CHECK_RETURN_POLICY",
                "title": "Evaluate Return & Replacement Eligibility",
                "instructions": "Ensure product is not classified as non-returnable Hazmat/Perishable and customer is in good standing.",
                "action_type": "MANUAL_CHECK",
                "is_mandatory": True,
            },
            {
                "step_order": 4,
                "step_key": "OFFER_RESOLUTION",
                "title": "Offer Replacement or Immediate Refund",
                "instructions": "Propose zero-cost replacement dispatch or full refund to original payment method.",
                "action_type": "EXECUTE_ACTION",
                "is_mandatory": True,
            },
            {
                "step_order": 5,
                "step_key": "DISPATCH_AND_CLOSE",
                "title": "Execute Resolution & Notify Customer",
                "instructions": "Submit authorization to commerce system and send confirmation email to customer.",
                "action_type": "EXECUTE_ACTION",
                "is_mandatory": True,
            },
        ],
    },
    {
        "code": "LATE_DELIVERY_PLAYBOOK",
        "name": "Late Delivery & In-Transit Delay Playbook",
        "category": "DELIVERY",
        "description": "Operational procedure for addressing late shipments, weather holds, and tracking exceptions.",
        "steps": [
            {
                "step_order": 1,
                "step_key": "VERIFY_CARRIER_STATUS",
                "title": "Carrier Tracking Status Check",
                "instructions": "Query FedEx/UPS API to check latest carrier checkpoint and exception code.",
                "action_type": "API_VERIFICATION",
                "is_mandatory": True,
            },
            {
                "step_order": 2,
                "step_key": "CALCULATE_DELAY_SEVERITY",
                "title": "Evaluate Delay Severity & SLA",
                "instructions": "Determine if delay exceeds 3 business days past original guaranteed delivery date.",
                "action_type": "MANUAL_CHECK",
                "is_mandatory": True,
            },
            {
                "step_order": 3,
                "step_key": "COURTESY_CREDIT_OR_RESHIP",
                "title": "Issue Shipping Refund or Courtesy Credit",
                "instructions": "Offer $10 store credit or expedited replacement if package is deemed lost in transit.",
                "action_type": "EXECUTE_ACTION",
                "is_mandatory": True,
            },
        ],
    },
    {
        "code": "PAYMENT_FAILURE_PLAYBOOK",
        "name": "Payment Failure & Billing Discrepancy Playbook",
        "category": "PAYMENT",
        "description": "Workflow for resolving declined cards, duplicate authorizations, or missing refunds.",
        "steps": [
            {
                "step_order": 1,
                "step_key": "GATEWAY_LEDGER_AUDIT",
                "title": "Inspect Gateway Ledger & Error Code",
                "instructions": "Check Stripe/PayPal transaction code for decline reason (e.g., insufficient_funds, fraud_block).",
                "action_type": "API_VERIFICATION",
                "is_mandatory": True,
            },
            {
                "step_order": 2,
                "step_key": "GUIDE_CUSTOMER_REPAYMENT",
                "title": "Send Secure Payment Update Link",
                "instructions": "Advise customer on card error or trigger secure payment re-authentication token.",
                "action_type": "PROMPT_CUSTOMER",
                "is_mandatory": True,
            },
        ],
    },
]


class PlaybookService:
    @staticmethod
    async def seed_default_playbooks(session: AsyncSession) -> None:
        """Seed predefined industry resolution playbooks into database."""
        for pb_data in DEFAULT_PLAYBOOKS:
            existing = await session.scalar(
                select(Playbook).where(Playbook.code == pb_data["code"])
            )
            if not existing:
                pb = Playbook(
                    code=pb_data["code"],
                    name=pb_data["name"],
                    category=pb_data["category"],
                    description=pb_data["description"],
                    is_active=True,
                )
                session.add(pb)
                await session.flush()

                for s in pb_data["steps"]:
                    step = PlaybookStep(
                        playbook_id=pb.id,
                        step_order=s["step_order"],
                        step_key=s["step_key"],
                        title=s["title"],
                        instructions=s["instructions"],
                        action_type=s["action_type"],
                        is_mandatory=s["is_mandatory"],
                    )
                    session.add(step)
        await session.commit()

    @staticmethod
    async def list_playbooks(
        session: AsyncSession, category: Optional[str] = None
    ) -> List[Playbook]:
        query = select(Playbook).options(selectinload(Playbook.steps)).where(Playbook.is_active == True)
        if category:
            query = query.where(Playbook.category == category)
        res = await session.scalars(query.order_by(Playbook.name))
        return list(res.all())

    @staticmethod
    async def get_playbook(session: AsyncSession, playbook_id: str) -> Playbook:
        pb = await session.scalar(
            select(Playbook)
            .options(selectinload(Playbook.steps))
            .where((Playbook.id == playbook_id) | (Playbook.code == playbook_id))
        )
        if not pb:
            raise EntityNotFoundError("Playbook", playbook_id)
        return pb

    @staticmethod
    async def start_execution(
        session: AsyncSession,
        case_id: str,
        playbook_id: str,
        agent_id: Optional[str] = None,
        event_bus: Optional[EventBus] = None,
    ) -> PlaybookExecution:
        case = await session.scalar(select(Case).where(Case.id == case_id))
        if not case:
            raise EntityNotFoundError("Case", case_id)

        pb = await PlaybookService.get_playbook(session, playbook_id)

        execution = PlaybookExecution(
            case_id=case.id,
            playbook_id=pb.id,
            agent_id=agent_id,
            status="IN_PROGRESS",
            current_step_order=1,
        )
        session.add(execution)

        t_event = CaseTimelineEvent(
            case_id=case.id,
            actor_id=agent_id,
            actor_type="AGENT" if agent_id else "SYSTEM",
            event_type="PLAYBOOK_STARTED",
            summary=f"Started resolution playbook: {pb.name}",
        )
        session.add(t_event)
        await session.commit()
        await session.refresh(execution)

        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.PLAYBOOK_STARTED,
                actor={"user_id": agent_id},
                payload={
                    "case_id": case.id,
                    "playbook_id": pb.id,
                    "execution_id": execution.id,
                },
            )
        )
        return execution

    @staticmethod
    async def execute_step(
        session: AsyncSession,
        execution_id: str,
        step_id: str,
        status: str = "COMPLETED",
        notes: Optional[str] = None,
        result_data_json: Optional[dict] = None,
        actor_id: Optional[str] = None,
        event_bus: Optional[EventBus] = None,
    ) -> PlaybookExecution:
        execution = await session.scalar(
            select(PlaybookExecution)
            .options(selectinload(PlaybookExecution.playbook).selectinload(Playbook.steps))
            .where(PlaybookExecution.id == execution_id)
        )
        if not execution:
            raise EntityNotFoundError("PlaybookExecution", execution_id)

        step = await session.scalar(select(PlaybookStep).where(PlaybookStep.id == step_id))
        if not step:
            raise EntityNotFoundError("PlaybookStep", step_id)

        log = PlaybookStepLog(
            execution_id=execution.id,
            step_id=step.id,
            actor_id=actor_id,
            status=status,
            notes=notes,
            result_data_json=result_data_json,
        )
        session.add(log)

        # Advance step
        all_steps = sorted(execution.playbook.steps, key=lambda s: s.step_order)
        current_idx = next((i for i, s in enumerate(all_steps) if s.id == step.id), None)
        if current_idx is not None and current_idx + 1 < len(all_steps):
            execution.current_step_order = all_steps[current_idx + 1].step_order
        else:
            execution.status = "COMPLETED"
            execution.completed_at = datetime.now(timezone.utc)

        await session.commit()
        await session.refresh(execution)

        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.PLAYBOOK_STEP_EXECUTED,
                actor={"user_id": actor_id},
                payload={
                    "execution_id": execution.id,
                    "step_key": step.step_key,
                    "status": status,
                },
            )
        )
        return execution
