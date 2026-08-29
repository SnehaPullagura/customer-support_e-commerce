"""
Audit Ledger Explorer endpoints.
"""

from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_roles
from app.core.security import Role
from app.schemas.audit import AuditEventResponse, AuditQueryFilter
from app.schemas.common import StandardResponse, PaginatedResponse
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/logs", response_model=StandardResponse[PaginatedResponse[AuditEventResponse]])
async def query_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.ADMINISTRATORS))],
    actor_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    filter_params = AuditQueryFilter(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        correlation_id=correlation_id,
    )
    items, total = await AuditService.query_logs(db, filter_params=filter_params, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    paginated = PaginatedResponse[AuditEventResponse](
        items=[AuditEventResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return StandardResponse(data=paginated)
