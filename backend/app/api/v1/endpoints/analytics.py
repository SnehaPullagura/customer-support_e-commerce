"""
Analytics and Executive Dashboard endpoints.
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_roles
from app.core.security import Role
from app.schemas.analytics import (
    OperationalMetricsResponse,
    AgentPerformanceResponse,
    ExecutiveDashboardResponse,
)
from app.schemas.common import StandardResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/operational", response_model=StandardResponse[OperationalMetricsResponse])
async def get_operational_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    metrics = await AnalyticsService.get_operational_metrics(db)
    return StandardResponse(data=metrics)


@router.get("/agents", response_model=StandardResponse[List[AgentPerformanceResponse]])
async def get_agent_performances(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    perf = await AnalyticsService.get_agent_performances(db)
    return StandardResponse(data=perf)


@router.get("/executive-dashboard", response_model=StandardResponse[ExecutiveDashboardResponse])
async def get_executive_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    dash = await AnalyticsService.get_executive_dashboard(db)
    return StandardResponse(data=dash)
