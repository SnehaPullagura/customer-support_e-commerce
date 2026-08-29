"""
Resolution Engine, Approvals, Commerce Action Execution, and Feedback Service.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.adapters.commerce import get_commerce_adapter
from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.core.exceptions import EntityNotFoundError, ValidationError, AuthorizationError
from app.core.telemetry import MetricsService
from app.models.case import Case, CaseTimelineEvent
from app.models.resolution import (
    Resolution,
    ResolutionAction,
    ResolutionApproval,
    CustomerFeedback,
)
from app.schemas.resolution import ResolutionCreate, ApprovalDecisionRequest, FeedbackCreate


HIGH_VALUE_REFUND_THRESHOLD_CENTS = 10000  # $100.00


class ResolutionService:
    @staticmethod
    async def propose_resolution(
        session: AsyncSession,
        data: ResolutionCreate,
        actor_id: Optional[str] = None,
        event_bus: Optional[EventBus] = None,
    ) -> Resolution:
        case = await session.scalar(select(Case).where(Case.id == data.case_id))
        if not case:
            raise EntityNotFoundError("Case", data.case_id)

        requires_mgr = data.requires_manager_approval
        if data.resolution_type == "REFUND" and data.amount_cents >= HIGH_VALUE_REFUND_THRESHOLD_CENTS:
            requires_mgr = True

        status = "PENDING_APPROVAL" if requires_mgr else "APPROVED"

        resolution = Resolution(
            case_id=case.id,
            resolution_type=data.resolution_type,
            status=status,
            summary=data.summary,
            details=data.details,
            amount_cents=data.amount_cents,
            currency=data.currency,
            requires_manager_approval=requires_mgr,
            is_approved=not requires_mgr,
            approved_by_id=actor_id if not requires_mgr else None,
            approved_at=datetime.now(timezone.utc) if not requires_mgr else None,
        )
        session.add(resolution)
        await session.flush()

        if requires_mgr and actor_id:
            approval = ResolutionApproval(
                resolution_id=resolution.id,
                requested_by_id=actor_id,
                status="PENDING",
            )
            session.add(approval)

        # Timeline event
        t_event = CaseTimelineEvent(
            case_id=case.id,
            actor_id=actor_id,
            actor_type="AGENT" if actor_id else "SYSTEM",
            event_type="RESOLUTION_PROPOSED",
            summary=f"Proposed resolution: {data.resolution_type} ({data.summary})"
            + (" [Pending Manager Approval]" if requires_mgr else " [Approved]"),
        )
        session.add(t_event)
        await session.commit()
        await session.refresh(resolution)

        # Publish Event
        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.RESOLUTION_PROPOSED,
                actor={"user_id": actor_id},
                payload={
                    "case_id": case.id,
                    "resolution_id": resolution.id,
                    "resolution_type": resolution.resolution_type,
                    "requires_approval": requires_mgr,
                },
            )
        )
        return resolution

    @staticmethod
    async def decide_approval(
        session: AsyncSession,
        resolution_id: str,
        decision: ApprovalDecisionRequest,
        approver_id: str,
        event_bus: Optional[EventBus] = None,
    ) -> Resolution:
        resolution = await session.scalar(
            select(Resolution).where(Resolution.id == resolution_id)
        )
        if not resolution:
            raise EntityNotFoundError("Resolution", resolution_id)

        now = datetime.now(timezone.utc)
        approval = await session.scalar(
            select(ResolutionApproval)
            .where(ResolutionApproval.resolution_id == resolution.id)
            .order_by(ResolutionApproval.created_at.desc())
        )
        if approval:
            approval.approver_id = approver_id
            approval.status = decision.status
            approval.rejection_reason = decision.rejection_reason
            approval.notes = decision.notes
            approval.decided_at = now

        if decision.status == "APPROVED":
            resolution.is_approved = True
            resolution.status = "APPROVED"
            resolution.approved_by_id = approver_id
            resolution.approved_at = now
        else:
            resolution.is_approved = False
            resolution.status = "REJECTED"

        await session.commit()
        await session.refresh(resolution)

        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.RESOLUTION_APPROVED if decision.status == "APPROVED" else EventTopic.CASE_UPDATED,
                actor={"user_id": approver_id},
                payload={
                    "resolution_id": resolution.id,
                    "case_id": resolution.case_id,
                    "status": resolution.status,
                },
            )
        )
        return resolution

    @staticmethod
    async def execute_resolution_action(
        session: AsyncSession,
        resolution_id: str,
        actor_id: Optional[str] = None,
        event_bus: Optional[EventBus] = None,
    ) -> Resolution:
        resolution = await session.scalar(
            select(Resolution).where(Resolution.id == resolution_id)
        )
        if not resolution:
            raise EntityNotFoundError("Resolution", resolution_id)

        if not resolution.is_approved:
            raise ValidationError("Resolution is not approved for execution.")

        case = await session.scalar(select(Case).where(Case.id == resolution.case_id))
        if not case:
            raise EntityNotFoundError("Case", resolution.case_id)

        commerce = get_commerce_adapter()
        resolution.status = "EXECUTING"

        action = ResolutionAction(
            resolution_id=resolution.id,
            action_type=f"EXECUTE_{resolution.resolution_type}",
            target_system="COMMERCE_ADAPTER",
            status="PENDING",
        )
        session.add(action)
        await session.flush()

        try:
            if resolution.resolution_type == "REFUND" and case.payment_id:
                ref_res = await commerce.execute_refund(
                    payment_id=case.payment_id,
                    amount_cents=resolution.amount_cents,
                    reason=resolution.summary,
                    idempotency_key=f"res-{resolution.id}",
                )
                action.external_reference_id = ref_res.refund_id
                action.status = "SUCCESS"
                action.action_payload_json = ref_res.model_dump(mode="json")
                case.refund_id = ref_res.refund_id

            elif resolution.resolution_type == "REPLACEMENT" and case.order_id:
                items_to_replace = [{"product_id": case.product_id or "PROD-9001", "quantity": 1}]
                repl_res = await commerce.create_replacement_order(
                    original_order_id=case.order_id,
                    items=items_to_replace,
                )
                action.external_reference_id = repl_res.order_id
                action.status = "SUCCESS"
                action.action_payload_json = repl_res.model_dump(mode="json")

            elif resolution.resolution_type == "RETURN" and case.order_id:
                items_to_return = [{"product_id": case.product_id or "PROD-9001", "quantity": 1}]
                ret_res = await commerce.create_return_authorization(
                    order_id=case.order_id,
                    items=items_to_return,
                    reason=resolution.summary,
                )
                action.external_reference_id = ret_res.rma_number
                action.status = "SUCCESS"
                action.action_payload_json = ret_res.model_dump(mode="json")
                case.return_id = ret_res.return_id
            else:
                action.status = "SUCCESS"
                action.action_payload_json = {"note": "Standard resolution action completed"}

            now = datetime.now(timezone.utc)
            resolution.status = "COMPLETED"
            resolution.executed_at = now
            case.status = "RESOLVED"
            case.resolved_at = now

            # Timeline event
            t_event = CaseTimelineEvent(
                case_id=case.id,
                actor_id=actor_id,
                actor_type="AGENT" if actor_id else "SYSTEM",
                event_type="RESOLVED",
                summary=f"Resolution executed successfully: {resolution.resolution_type}",
                new_value="RESOLVED",
            )
            session.add(t_event)
            await session.commit()
            await session.refresh(resolution)

            # Record telemetry
            MetricsService.record_case_resolved(case.category, resolution.resolution_type)

            # Publish Event
            bus = event_bus or get_event_bus()
            await bus.publish(
                Event(
                    topic=EventTopic.CASE_RESOLVED,
                    actor={"user_id": actor_id},
                    payload={
                        "case_id": case.id,
                        "resolution_id": resolution.id,
                        "resolution_type": resolution.resolution_type,
                        "action_id": action.id,
                    },
                )
            )

        except Exception as e:
            action.status = "FAILED"
            action.error_message = str(e)
            resolution.status = "FAILED"
            await session.commit()
            raise

        return resolution

    @staticmethod
    async def record_feedback(
        session: AsyncSession, case_id: str, data: FeedbackCreate
    ) -> CustomerFeedback:
        case = await session.scalar(select(Case).where(Case.id == case_id))
        if not case:
            raise EntityNotFoundError("Case", case_id)

        feedback = CustomerFeedback(
            case_id=case.id,
            rating=data.rating,
            customer_effort_score=data.customer_effort_score,
            comment=data.comment,
            feedback_tags=data.feedback_tags,
        )
        session.add(feedback)
        await session.commit()
        await session.refresh(feedback)
        return feedback
