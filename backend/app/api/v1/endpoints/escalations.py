"""
Escalation endpoints.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_roles
from app.core.security import Role
from app.models.escalation import EscalationPolicy, EscalationEvent
from app.schemas.common import StandardResponse
from app.schemas.escalation import (
    EscalationPolicyCreate,
    EscalationPolicyResponse,
    EscalationEventResponse,
)
from app.services.escalation_service import EscalationService

router = APIRouter()


@router.post("/policies", response_model=StandardResponse[EscalationPolicyResponse], status_code=status.HTTP_201_CREATED)
async def create_escalation_policy(
    data: EscalationPolicyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.MANAGEMENT))],
):
    policy = await EscalationService.create_policy(db, data)
    return StandardResponse(message="Escalation policy created", data=EscalationPolicyResponse.model_validate(policy))


@router.get("/policies", response_model=StandardResponse[List[EscalationPolicyResponse]])
async def list_escalation_policies(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    res = await db.scalars(select(EscalationPolicy).order_by(EscalationPolicy.name))
    return StandardResponse(data=[EscalationPolicyResponse.model_validate(p) for p in res.all()])


@router.get("/active-events", response_model=StandardResponse[List[EscalationEventResponse]])
async def list_active_escalations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    res = await db.scalars(
        select(EscalationEvent).where(EscalationEvent.status == "OPEN").order_by(EscalationEvent.created_at.desc())
    )
    return StandardResponse(data=[EscalationEventResponse.model_validate(e) for e in res.all()])
