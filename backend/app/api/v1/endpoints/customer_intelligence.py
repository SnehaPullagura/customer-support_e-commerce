"""
Customer Intelligence, Frustration Score, and Churn Risk endpoints.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_roles
from app.core.security import Role
from app.schemas.common import StandardResponse
from app.schemas.customer_intelligence import FrustrationScoreResponse, ChurnRiskResponse
from app.services.customer_intelligence_service import CustomerIntelligenceService

router = APIRouter()


@router.get("/frustration/{customer_id}", response_model=StandardResponse[FrustrationScoreResponse])
async def get_frustration_score(
    customer_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
    case_id: Optional[str] = None,
):
    score_resp = await CustomerIntelligenceService.compute_frustration_score(db, customer_id, case_id=case_id)
    return StandardResponse(data=score_resp)


@router.get("/churn/{customer_id}", response_model=StandardResponse[ChurnRiskResponse])
async def get_churn_risk(
    customer_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    churn_resp = await CustomerIntelligenceService.evaluate_churn_risk(db, customer_id)
    return StandardResponse(data=churn_resp)
