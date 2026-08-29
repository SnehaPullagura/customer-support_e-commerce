"""
Resolution Engine & Customer Feedback endpoints.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser, require_roles
from app.core.security import Role
from app.models.resolution import Resolution
from app.schemas.common import StandardResponse
from app.schemas.resolution import (
    ResolutionCreate,
    ResolutionResponse,
    ApprovalDecisionRequest,
    FeedbackCreate,
    FeedbackResponse,
)
from app.services.resolution_service import ResolutionService

router = APIRouter()


@router.post("", response_model=StandardResponse[ResolutionResponse], status_code=status.HTTP_201_CREATED)
async def propose_resolution(
    data: ResolutionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    res = await ResolutionService.propose_resolution(db, data, actor_id=current_user.user_id)
    return StandardResponse(message="Resolution proposed", data=ResolutionResponse.model_validate(res))


@router.post("/{resolution_id}/approval", response_model=StandardResponse[ResolutionResponse])
async def decide_resolution_approval(
    resolution_id: str,
    data: ApprovalDecisionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.MANAGEMENT))],
):
    res = await ResolutionService.decide_approval(db, resolution_id, data, approver_id=current_user.user_id)
    return StandardResponse(message=f"Resolution {data.status.lower()}", data=ResolutionResponse.model_validate(res))


@router.post("/{resolution_id}/execute", response_model=StandardResponse[ResolutionResponse])
async def execute_resolution_action(
    resolution_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    res = await ResolutionService.execute_resolution_action(db, resolution_id, actor_id=current_user.user_id)
    return StandardResponse(message="Resolution executed successfully", data=ResolutionResponse.model_validate(res))


@router.post("/case/{case_id}/feedback", response_model=StandardResponse[FeedbackResponse], status_code=status.HTTP_201_CREATED)
async def submit_case_feedback(
    case_id: str,
    data: FeedbackCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    fb = await ResolutionService.record_feedback(db, case_id, data)
    return StandardResponse(message="Feedback submitted. Thank you!", data=FeedbackResponse.model_validate(fb))
