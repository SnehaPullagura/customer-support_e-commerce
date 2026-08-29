"""
Intelligent Routing endpoints.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_roles
from app.core.security import Role
from app.models.routing import RoutingRule
from app.schemas.common import StandardResponse
from app.schemas.routing import RoutingRuleCreate, RoutingRuleResponse, RoutingDecisionResponse
from app.services.routing_service import RoutingService

router = APIRouter()


@router.post("/rules", response_model=StandardResponse[RoutingRuleResponse], status_code=status.HTTP_201_CREATED)
async def create_routing_rule(
    data: RoutingRuleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.MANAGEMENT))],
):
    rule = await RoutingService.create_rule(db, data)
    return StandardResponse(message="Routing rule created", data=RoutingRuleResponse.model_validate(rule))


@router.get("/rules", response_model=StandardResponse[List[RoutingRuleResponse]])
async def list_routing_rules(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    res = await db.scalars(select(RoutingRule).order_by(RoutingRule.priority_order))
    return StandardResponse(data=[RoutingRuleResponse.model_validate(r) for r in res.all()])


@router.post("/route/{case_id}", response_model=StandardResponse[RoutingDecisionResponse])
async def trigger_case_routing(
    case_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    decision = await RoutingService.route_case(db, case_id)
    return StandardResponse(message="Routing decision evaluated", data=decision)
