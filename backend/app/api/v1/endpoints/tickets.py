"""
Ticket Management endpoints.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser, require_roles
from app.core.security import Role
from app.schemas.common import StandardResponse, PaginatedResponse
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketDetailResponse,
)
from app.services.ticket_service import TicketService

router = APIRouter()


@router.post("", response_model=StandardResponse[TicketResponse], status_code=status.HTTP_201_CREATED)
async def create_ticket(
    data: TicketCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    ticket = await TicketService.create_ticket(db, data, actor_id=current_user.user_id)
    return StandardResponse(
        message="Ticket created successfully",
        data=TicketResponse.model_validate(ticket),
    )


@router.get("", response_model=StandardResponse[PaginatedResponse[TicketResponse]])
async def list_tickets(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
    case_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await TicketService.list_tickets(
        db, case_id=case_id, agent_id=agent_id, status=status, page=page, page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    paginated = PaginatedResponse[TicketResponse](
        items=[TicketResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return StandardResponse(data=paginated)


@router.get("/{ticket_id}", response_model=StandardResponse[TicketDetailResponse])
async def get_ticket(
    ticket_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    ticket = await TicketService.get_ticket(db, ticket_id)
    return StandardResponse(data=TicketDetailResponse.model_validate(ticket))


@router.patch("/{ticket_id}", response_model=StandardResponse[TicketResponse])
async def update_ticket(
    ticket_id: str,
    data: TicketUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    ticket = await TicketService.update_ticket(db, ticket_id, data, actor_id=current_user.user_id)
    return StandardResponse(
        message="Ticket updated successfully",
        data=TicketResponse.model_validate(ticket),
    )
