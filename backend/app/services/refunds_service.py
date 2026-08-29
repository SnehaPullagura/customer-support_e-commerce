"""
Refund Support Service with Distributed Idempotency and Payment Ledger Integration.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.adapters.commerce import get_commerce_adapter
from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationError
from app.core.idempotency import IdempotencyGuard, get_idempotency_guard
from app.models.refunds import RefundRequest, RefundTransaction
from app.models.case import Case, CaseTimelineEvent
from app.schemas.refunds import RefundRequestCreate, RefundApprovalRequest


HIGH_VALUE_THRESHOLD_CENTS = 10000  # $100


class RefundsService:
    @staticmethod
    async def create_refund_request(
        session: AsyncSession,
        data: RefundRequestCreate,
        idempotency_key: str,
        actor_id: Optional[str] = None,
        idempotency_guard: Optional[IdempotencyGuard] = None,
        event_bus: Optional[EventBus] = None,
    ) -> RefundRequest:
        guard = idempotency_guard or get_idempotency_guard()
        is_cached, cached_resp = guard.start_operation(idempotency_key, data.model_dump())
        if is_cached and cached_resp:
            # Replay existing completed refund
            existing = await session.scalar(
                select(RefundRequest)
                .options(selectinload(RefundRequest.transactions))
                .where(RefundRequest.idempotency_key == idempotency_key)
            )
            if existing:
                return existing

        # Check existing in DB
        existing_in_db = await session.scalar(
            select(RefundRequest).where(RefundRequest.idempotency_key == idempotency_key)
        )
        if existing_in_db:
            return existing_in_db

        requires_mgr = data.amount_cents >= HIGH_VALUE_THRESHOLD_CENTS
        status = "PENDING_APPROVAL" if requires_mgr else "PROCESSING"

        refund_req = RefundRequest(
            case_id=data.case_id,
            customer_id=data.customer_id,
            payment_id=data.payment_id,
            order_id=data.order_id,
            idempotency_key=idempotency_key,
            amount_cents=data.amount_cents,
            currency=data.currency,
            reason=data.reason,
            status=status,
            requires_approval=requires_mgr,
        )
        session.add(refund_req)
        await session.flush()

        if not requires_mgr:
            # Auto-execute refund against commerce payment gateway
            try:
                commerce = get_commerce_adapter()
                ref_dto = await commerce.execute_refund(
                    payment_id=data.payment_id,
                    amount_cents=data.amount_cents,
                    reason=data.reason,
                    idempotency_key=idempotency_key,
                )

                refund_req.status = "COMPLETED"
                refund_req.gateway_refund_id = ref_dto.refund_id

                tx = RefundTransaction(
                    refund_request_id=refund_req.id,
                    gateway_name="STRIPE",
                    gateway_transaction_id=ref_dto.refund_id,
                    amount_cents=data.amount_cents,
                    currency=data.currency,
                    status="SUCCESS",
                    gateway_response_json=ref_dto.model_dump(mode="json"),
                )
                session.add(tx)

                # Update case
                case = await session.scalar(select(Case).where(Case.id == data.case_id))
                if case:
                    case.refund_id = ref_dto.refund_id
                    t_event = CaseTimelineEvent(
                        case_id=case.id,
                        actor_id=actor_id,
                        actor_type="AGENT" if actor_id else "SYSTEM",
                        event_type="REFUND_ISSUED",
                        summary=f"Refund of ${(data.amount_cents/100):.2f} processed successfully ({ref_dto.refund_id})",
                    )
                    session.add(t_event)

                guard.complete_operation(idempotency_key, 200, refund_req.to_dict())

            except Exception as e:
                refund_req.status = "FAILED"
                refund_req.failure_reason = str(e)
                guard.fail_operation(idempotency_key)
                await session.commit()
                raise

        await session.commit()
        await session.refresh(refund_req)

        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.REFUND_COMPLETED if refund_req.status == "COMPLETED" else EventTopic.REFUND_REQUESTED,
                actor={"user_id": actor_id},
                payload={
                    "refund_id": refund_req.id,
                    "case_id": refund_req.case_id,
                    "amount_cents": refund_req.amount_cents,
                    "status": refund_req.status,
                },
            )
        )
        return refund_req

    @staticmethod
    async def get_refund(session: AsyncSession, refund_id: str) -> RefundRequest:
        req = await session.scalar(
            select(RefundRequest)
            .options(selectinload(RefundRequest.transactions))
            .where(RefundRequest.id == refund_id)
        )
        if not req:
            raise EntityNotFoundError("RefundRequest", refund_id)
        return req
