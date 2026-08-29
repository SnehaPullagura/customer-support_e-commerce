"""
SLA Policy & Monitoring endpoints.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_roles
from app.core.security import Role
from app.models.sla import SLAPolicy
from app.schemas.common import StandardResponse
from app.schemas.sla import SLAPolicyCreate, SLAPolicyResponse
from app.services.sla_service import SLAService

router = APIRouter()


@router.post("/policies", response_model=StandardResponse[SLAPolicyResponse], status_code=status.HTTP_201_CREATED)
async def create_sla_policy(
    data: SLAPolicyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.MANAGEMENT))],
):
    policy = await SLAService.create_policy(db, data)
    return StandardResponse(message="SLA policy created", data=SLAPolicyResponse.model_validate(policy))


@router.get("/policies", response_model=StandardResponse[List[SLAPolicyResponse]])
async def list_sla_policies(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    res = await db.scalars(select(SLAPolicy).order_by(SLAPolicy.name))
    return StandardResponse(data=[SLAPolicyResponse.model_validate(p) for p in res.all()])


@router.post("/evaluate", response_model=StandardResponse[dict])
async def evaluate_active_slas(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    result = await SLAService.evaluate_active_slas(db)
    return StandardResponse(message="SLA evaluation run completed", data=result)
