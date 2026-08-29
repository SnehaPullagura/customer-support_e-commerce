"""
Return & Replacement Orchestration Service.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.adapters.commerce import get_commerce_adapter
from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.core.exceptions import EntityNotFoundError, ValidationError
from app.models.returns import ReturnRequest, ReturnItem, ReplacementOrder
from app.models.case import Case, CaseTimelineEvent
from app.schemas.returns import ReturnRequestCreate, ReturnStatusUpdate


class ReturnsService:
    @staticmethod
    async def create_return_request(
        session: AsyncSession,
        data: ReturnRequestCreate,
        actor_id: Optional[str] = None,
        event_bus: Optional[EventBus] = None,
    ) -> ReturnRequest:
        commerce = get_commerce_adapter()
        order = await commerce.get_order(data.order_id)
        if not order:
            raise ValidationError(f"Order '{data.order_id}' was not found in commerce system.")

        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        rma_number = f"RMA-{today_str}-{uuid.uuid4().hex[:4].upper()}"

        ret = ReturnRequest(
            case_id=data.case_id,
            customer_id=data.customer_id,
            order_id=data.order_id,
            rma_number=rma_number,
            reason=data.reason,
            status="APPROVED",
            shipping_label_url=f"https://labels.mock-commerce.internal/rma/{rma_number}.pdf",
            carrier_tracking_number=f"FDX-RMA-{uuid.uuid4().hex[:8].upper()}",
        )
        session.add(ret)
        await session.flush()

        for item in data.items:
            ritem = ReturnItem(
                return_request_id=ret.id,
                product_id=item.product_id,
                product_name=item.product_name,
                sku=item.sku,
                quantity=item.quantity,
                condition=item.condition,
            )
            session.add(ritem)

        if data.case_id:
            case = await session.scalar(select(Case).where(Case.id == data.case_id))
            if case:
                case.return_id = ret.id
                t_event = CaseTimelineEvent(
                    case_id=case.id,
                    actor_id=actor_id,
                    actor_type="AGENT" if actor_id else "SYSTEM",
                    event_type="RMA_ISSUED",
                    summary=f"Return authorized with RMA #{rma_number}",
                )
                session.add(t_event)

        await session.commit()
        await session.refresh(ret)

        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.RETURN_APPROVED,
                actor={"user_id": actor_id},
                payload={
                    "return_id": ret.id,
                    "rma_number": ret.rma_number,
                    "order_id": ret.order_id,
                    "customer_id": ret.customer_id,
                },
            )
        )
        return ret

    @staticmethod
    async def get_return(session: AsyncSession, return_id: str) -> ReturnRequest:
        ret = await session.scalar(
            select(ReturnRequest)
            .options(selectinload(ReturnRequest.items))
            .where((ReturnRequest.id == return_id) | (ReturnRequest.rma_number == return_id))
        )
        if not ret:
            raise EntityNotFoundError("ReturnRequest", return_id)
        return ret

    @staticmethod
    async def update_status(
        session: AsyncSession, return_id: str, data: ReturnStatusUpdate, actor_id: Optional[str] = None
    ) -> ReturnRequest:
        ret = await ReturnsService.get_return(session, return_id)
        ret.status = data.status
        if data.carrier_tracking_number:
            ret.carrier_tracking_number = data.carrier_tracking_number
        if data.inspection_notes:
            ret.inspection_notes = data.inspection_notes

        await session.commit()
        await session.refresh(ret)
        return ret
