"""
Ticket Management Service.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.exceptions import EntityNotFoundError
from app.models.ticket import Ticket, TicketAttachment, TicketTag, TicketHistory
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketService:
    @staticmethod
    async def create_ticket(session: AsyncSession, data: TicketCreate, actor_id: Optional[str] = None) -> Ticket:
        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        count = await session.scalar(
            select(func.count(Ticket.id)).where(Ticket.ticket_number.like(f"TCK-{today_str}-%"))
        ) or 0
        ticket_number = f"TCK-{today_str}-{count + 1001:04d}"

        ticket = Ticket(
            case_id=data.case_id,
            ticket_number=ticket_number,
            subject=data.subject,
            description=data.description,
            category=data.category,
            priority=data.priority,
            assigned_agent_id=data.assigned_agent_id,
            due_date=data.due_date,
            status="OPEN",
        )
        session.add(ticket)
        await session.flush()

        # Add creation history
        history = TicketHistory(
            ticket_id=ticket.id,
            actor_id=actor_id,
            action="TICKET_CREATED",
            changes_json={"initial_data": data.model_dump(mode="json")},
        )
        session.add(history)
        await session.commit()
        await session.refresh(ticket)
        return ticket

    @staticmethod
    async def get_ticket(session: AsyncSession, ticket_id: str) -> Ticket:
        ticket = await session.scalar(
            select(Ticket)
            .options(
                selectinload(Ticket.attachments),
                selectinload(Ticket.tags),
                selectinload(Ticket.history),
            )
            .where(or_(Ticket.id == ticket_id, Ticket.ticket_number == ticket_id))
        )
        if not ticket:
            raise EntityNotFoundError("Ticket", ticket_id)
        return ticket

    @staticmethod
    async def list_tickets(
        session: AsyncSession,
        case_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Ticket], int]:
        query = select(Ticket)
        if case_id:
            query = query.where(Ticket.case_id == case_id)
        if agent_id:
            query = query.where(Ticket.assigned_agent_id == agent_id)
        if status:
            query = query.where(Ticket.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query) or 0

        offset = (page - 1) * page_size
        results = await session.scalars(
            query.order_by(Ticket.created_at.desc()).offset(offset).limit(page_size)
        )
        return list(results.all()), total

    @staticmethod
    async def update_ticket(
        session: AsyncSession, ticket_id: str, data: TicketUpdate, actor_id: Optional[str] = None
    ) -> Ticket:
        ticket = await TicketService.get_ticket(session, ticket_id)
        update_data = data.model_dump(exclude_unset=True)

        for key, val in update_data.items():
            setattr(ticket, key, val)

        if data.status in ["RESOLVED", "CLOSED"]:
            ticket.closed_at = datetime.now(timezone.utc)

        history = TicketHistory(
            ticket_id=ticket.id,
            actor_id=actor_id,
            action="TICKET_UPDATED",
            changes_json=update_data,
        )
        session.add(history)
        await session.commit()
        await session.refresh(ticket)
        return ticket

    @staticmethod
    async def add_attachment(
        session: AsyncSession,
        ticket_id: str,
        file_name: str,
        file_path: str,
        file_size_bytes: int,
        mime_type: str,
        uploaded_by: Optional[str] = None,
    ) -> TicketAttachment:
        ticket = await TicketService.get_ticket(session, ticket_id)
        attachment = TicketAttachment(
            ticket_id=ticket.id,
            file_name=file_name,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            uploaded_by=uploaded_by,
        )
        session.add(attachment)
        await session.commit()
        await session.refresh(attachment)
        return attachment
