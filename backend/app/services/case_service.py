"""
Case Management Core Domain Service.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationError
from app.core.telemetry import MetricsService
from app.models.case import Case, CaseLink, CaseTimelineEvent
from app.models.customer import Customer
from app.models.agent import Agent
from app.schemas.case import CaseCreate, CaseUpdate, CaseAssignRequest, CaseLinkRequest


VALID_STATUS_TRANSITIONS = {
    "NEW": ["OPEN", "IN_PROGRESS", "WAITING_FOR_CUSTOMER", "CLOSED"],
    "OPEN": ["IN_PROGRESS", "WAITING_FOR_CUSTOMER", "WAITING_FOR_EXTERNAL_SYSTEM", "ESCALATED", "RESOLVED", "CLOSED"],
    "IN_PROGRESS": ["WAITING_FOR_CUSTOMER", "WAITING_FOR_EXTERNAL_SYSTEM", "ESCALATED", "RESOLVED", "CLOSED"],
    "WAITING_FOR_CUSTOMER": ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"],
    "WAITING_FOR_EXTERNAL_SYSTEM": ["OPEN", "IN_PROGRESS", "ESCALATED", "RESOLVED", "CLOSED"],
    "ESCALATED": ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"],
    "RESOLVED": ["CLOSED", "REOPENED"],
    "CLOSED": ["REOPENED"],
    "REOPENED": ["OPEN", "IN_PROGRESS", "WAITING_FOR_CUSTOMER", "ESCALATED", "RESOLVED"],
}


class CaseService:
    @staticmethod
    async def generate_case_number(session: AsyncSession) -> str:
        """Generate unique daily sequence: CASE-YYYYMMDD-XXXX."""
        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        count = await session.scalar(
            select(func.count(Case.id)).where(Case.case_number.like(f"CASE-{today_str}-%"))
        ) or 0
        return f"CASE-{today_str}-{count + 1001:04d}"

    @staticmethod
    async def create_case(
        session: AsyncSession,
        data: CaseCreate,
        actor_id: Optional[str] = None,
        event_bus: Optional[EventBus] = None,
    ) -> Case:
        # Verify customer exists
        customer = await session.scalar(select(Customer).where(Customer.id == data.customer_id))
        if not customer:
            raise EntityNotFoundError("Customer", data.customer_id)

        case_number = await CaseService.generate_case_number(session)
        
        case = Case(
            case_number=case_number,
            customer_id=data.customer_id,
            title=data.title,
            description=data.description,
            category=data.category,
            subcategory=data.subcategory,
            priority=data.priority,
            source=data.source,
            status="NEW",
            order_id=data.order_id,
            product_id=data.product_id,
            payment_id=data.payment_id,
            shipment_id=data.shipment_id,
        )
        session.add(case)
        await session.flush()

        # Add initial creation timeline event
        timeline_event = CaseTimelineEvent(
            case_id=case.id,
            actor_id=actor_id,
            actor_type="CUSTOMER" if actor_id == customer.user_id else "AGENT" if actor_id else "SYSTEM",
            event_type="CASE_CREATED",
            summary=f"Case created via {data.source}",
            new_value="NEW",
        )
        session.add(timeline_event)
        await session.commit()
        await session.refresh(case)

        # Record metrics
        MetricsService.record_case_created(case.category, case.priority, case.source)

        # Publish Event
        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.CASE_CREATED,
                actor={"user_id": actor_id},
                payload={
                    "case_id": case.id,
                    "case_number": case.case_number,
                    "customer_id": case.customer_id,
                    "category": case.category,
                    "priority": case.priority,
                    "order_id": case.order_id,
                    "description": case.description,
                },
            )
        )

        return case

    @staticmethod
    async def get_case(session: AsyncSession, case_id: str) -> Case:
        case = await session.scalar(
            select(Case)
            .options(
                selectinload(Case.customer),
                selectinload(Case.timeline_events),
                selectinload(Case.outgoing_links),
                selectinload(Case.incoming_links),
            )
            .where(or_(Case.id == case_id, Case.case_number == case_id))
        )
        if not case:
            raise EntityNotFoundError("Case", case_id)
        return case

    @staticmethod
    async def list_cases(
        session: AsyncSession,
        customer_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Case], int]:
        query = select(Case).options(selectinload(Case.customer))

        if customer_id:
            query = query.where(Case.customer_id == customer_id)
        if agent_id:
            query = query.where(Case.assigned_agent_id == agent_id)
        if team_id:
            query = query.where(Case.assigned_team_id == team_id)
        if status:
            query = query.where(Case.status == status)
        if priority:
            query = query.where(Case.priority == priority)
        if category:
            query = query.where(Case.category == category)
        if search:
            term = f"%{search}%"
            query = query.where(
                or_(
                    Case.case_number.ilike(term),
                    Case.title.ilike(term),
                    Case.description.ilike(term),
                    Case.order_id.ilike(term),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query) or 0

        offset = (page - 1) * page_size
        results = await session.scalars(
            query.order_by(Case.created_at.desc()).offset(offset).limit(page_size)
        )
        return list(results.all()), total

    @staticmethod
    async def update_status(
        session: AsyncSession,
        case_id: str,
        new_status: str,
        actor_id: Optional[str] = None,
        reason: Optional[str] = None,
        event_bus: Optional[EventBus] = None,
    ) -> Case:
        case = await CaseService.get_case(session, case_id)
        prev_status = case.status

        allowed = VALID_STATUS_TRANSITIONS.get(prev_status, [])
        if new_status not in allowed and new_status != prev_status:
            raise ValidationError(
                f"Invalid status transition from {prev_status} to {new_status}. Allowed: {allowed}"
            )

        now = datetime.now(timezone.utc)
        case.status = new_status
        if new_status == "RESOLVED":
            case.resolved_at = now
        elif new_status == "CLOSED":
            case.closed_at = now
        elif new_status == "REOPENED":
            case.reopened_at = now

        # Add timeline log
        event = CaseTimelineEvent(
            case_id=case.id,
            actor_id=actor_id,
            actor_type="AGENT" if actor_id else "SYSTEM",
            event_type="STATUS_CHANGED",
            summary=f"Status changed from {prev_status} to {new_status}" + (f": {reason}" if reason else ""),
            previous_value=prev_status,
            new_value=new_status,
        )
        session.add(event)
        await session.commit()
        await session.refresh(case)

        # Publish Event
        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.CASE_STATUS_CHANGED,
                actor={"user_id": actor_id},
                payload={
                    "case_id": case.id,
                    "case_number": case.case_number,
                    "previous_status": prev_status,
                    "new_status": new_status,
                    "reason": reason,
                },
            )
        )
        return case

    @staticmethod
    async def assign_case(
        session: AsyncSession,
        case_id: str,
        data: CaseAssignRequest,
        actor_id: Optional[str] = None,
        event_bus: Optional[EventBus] = None,
    ) -> Case:
        case = await CaseService.get_case(session, case_id)
        prev_agent = case.assigned_agent_id

        if data.agent_id:
            agent = await session.scalar(select(Agent).where(Agent.id == data.agent_id))
            if not agent:
                raise EntityNotFoundError("Agent", data.agent_id)
            case.assigned_agent_id = agent.id
            case.assigned_team_id = agent.team_id or data.team_id
            if case.status == "NEW":
                case.status = "OPEN"
        elif data.team_id:
            case.assigned_team_id = data.team_id

        # Timeline event
        event = CaseTimelineEvent(
            case_id=case.id,
            actor_id=actor_id,
            actor_type="AGENT" if actor_id else "SYSTEM",
            event_type="ASSIGNED",
            summary=f"Assigned to agent {data.agent_id or 'Queue'}" + (f": {data.reason}" if data.reason else ""),
            previous_value=prev_agent,
            new_value=data.agent_id,
        )
        session.add(event)
        await session.commit()
        await session.refresh(case)

        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.CASE_ASSIGNED,
                actor={"user_id": actor_id},
                payload={
                    "case_id": case.id,
                    "case_number": case.case_number,
                    "assigned_agent_id": case.assigned_agent_id,
                    "assigned_team_id": case.assigned_team_id,
                },
            )
        )
        return case

    @staticmethod
    async def link_cases(
        session: AsyncSession,
        source_case_id: str,
        data: CaseLinkRequest,
        actor_id: Optional[str] = None,
    ) -> CaseLink:
        source = await CaseService.get_case(session, source_case_id)
        target = await CaseService.get_case(session, data.target_case_id)

        if source.id == target.id:
            raise ValidationError("A case cannot be linked to itself.")

        link = CaseLink(
            source_case_id=source.id,
            target_case_id=target.id,
            link_type=data.link_type,
            reason=data.reason,
        )
        session.add(link)

        # Timeline events for both cases
        t1 = CaseTimelineEvent(
            case_id=source.id,
            actor_id=actor_id,
            event_type="CASE_LINKED",
            summary=f"Linked to Case #{target.case_number} as {data.link_type}",
        )
        t2 = CaseTimelineEvent(
            case_id=target.id,
            actor_id=actor_id,
            event_type="CASE_LINKED",
            summary=f"Linked from Case #{source.case_number} as {data.link_type}",
        )
        session.add(t1)
        session.add(t2)

        # If merged, update source case status
        if data.link_type == "MERGED_INTO":
            source.status = "CLOSED"

        await session.commit()
        await session.refresh(link)
        return link
