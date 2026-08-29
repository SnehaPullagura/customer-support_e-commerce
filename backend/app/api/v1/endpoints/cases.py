"""
Case Management endpoints.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser, require_roles
from app.core.security import Role
from app.schemas.common import StandardResponse, PaginatedResponse
from app.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseDetailResponse,
    CaseAssignRequest,
    CaseEscalateRequest,
    CaseResolveRequest,
    CaseLinkRequest,
    CaseLinkResponse,
)
from app.schemas.commerce import CommerceGraphDTO
from app.services.case_service import CaseService
from app.services.routing_service import RoutingService
from app.services.sla_service import SLAService
from app.services.escalation_service import EscalationService
from app.services.resolution_service import ResolutionService
from app.services.commerce_context_service import CommerceContextService
from app.services.ai_service import AIService
from app.ai.assistant import AIAssistant
from app.schemas.resolution import ResolutionCreate

router = APIRouter()


@router.post("", response_model=StandardResponse[CaseResponse], status_code=status.HTTP_201_CREATED)
async def create_case(
    data: CaseCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    case = await CaseService.create_case(db, data, actor_id=current_user.user_id)
    
    # Trigger SLA start
    await SLAService.start_sla_tracker(db, case.id)
    
    # Trigger Intelligent Routing
    await RoutingService.route_case(db, case.id)
    
    # Reload case with assignment
    refreshed_case = await CaseService.get_case(db, case.id)

    return StandardResponse(
        message="Case created and routed successfully",
        data=CaseResponse.model_validate(refreshed_case),
    )


@router.get("", response_model=StandardResponse[PaginatedResponse[CaseResponse]])
async def list_cases(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    customer_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    team_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    # If customer role, only return their own cases
    target_cust_id = customer_id
    if current_user.is_customer():
        target_cust_id = current_user.customer_id

    items, total = await CaseService.list_cases(
        db,
        customer_id=target_cust_id,
        agent_id=agent_id,
        team_id=team_id,
        status=status,
        priority=priority,
        category=category,
        search=search,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    paginated = PaginatedResponse[CaseResponse](
        items=[CaseResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return StandardResponse(data=paginated)


@router.get("/{case_id}", response_model=StandardResponse[CaseDetailResponse])
async def get_case(
    case_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    case = await CaseService.get_case(db, case_id)
    return StandardResponse(data=CaseDetailResponse.model_validate(case))


@router.patch("/{case_id}/status", response_model=StandardResponse[CaseResponse])
async def update_status(
    case_id: str,
    new_status: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    reason: Optional[str] = None,
):
    case = await CaseService.update_status(db, case_id, new_status, actor_id=current_user.user_id, reason=reason)
    await SLAService.handle_status_change(db, case_id, new_status, actor_id=current_user.user_id)
    return StandardResponse(
        message=f"Case status updated to {new_status}",
        data=CaseResponse.model_validate(case),
    )


@router.post("/{case_id}/assign", response_model=StandardResponse[CaseResponse])
async def assign_case(
    case_id: str,
    data: CaseAssignRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    case = await CaseService.assign_case(db, case_id, data, actor_id=current_user.user_id)
    return StandardResponse(
        message="Case assigned successfully",
        data=CaseResponse.model_validate(case),
    )


@router.post("/{case_id}/escalate", response_model=StandardResponse[dict])
async def escalate_case(
    case_id: str,
    data: CaseEscalateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    event = await EscalationService.escalate_case(
        db,
        case_id=case_id,
        reason=data.escalation_reason,
        actor_id=current_user.user_id,
        escalate_to_role=data.escalate_to_role or "TEAM_LEAD",
        notes=data.notes,
    )
    return StandardResponse(
        message="Case escalated successfully",
        data={"escalation_id": event.id, "case_id": case_id, "status": event.status},
    )


@router.post("/{case_id}/resolve", response_model=StandardResponse[dict])
async def resolve_case(
    case_id: str,
    data: CaseResolveRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    res_create = ResolutionCreate(
        case_id=case_id,
        resolution_type=data.resolution_type,
        summary=data.summary,
        details=data.details,
        amount_cents=data.amount_cents,
        currency=data.currency,
    )
    resolution = await ResolutionService.propose_resolution(db, res_create, actor_id=current_user.user_id)
    if resolution.is_approved:
        resolution = await ResolutionService.execute_resolution_action(db, resolution.id, actor_id=current_user.user_id)

    return StandardResponse(
        message="Resolution executed and case marked as resolved",
        data={"resolution_id": resolution.id, "status": resolution.status},
    )


@router.post("/{case_id}/link", response_model=StandardResponse[CaseLinkResponse])
async def link_case(
    case_id: str,
    data: CaseLinkRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    link = await CaseService.link_cases(db, source_case_id=case_id, data=data, actor_id=current_user.user_id)
    return StandardResponse(
        message="Cases linked successfully",
        data=CaseLinkResponse.model_validate(link),
    )


@router.get("/{case_id}/commerce-context", response_model=StandardResponse[CommerceGraphDTO])
async def get_case_commerce_context(
    case_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    graph = await CommerceContextService.get_case_commerce_context(db, case_id)
    return StandardResponse(data=graph)


@router.get("/{case_id}/summary", response_model=StandardResponse[str])
async def get_case_summary(
    case_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    summary = await AIAssistant.summarize_case(db, case_id)
    return StandardResponse(data=summary)
