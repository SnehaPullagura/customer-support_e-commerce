"""
Return & Replacement Support endpoints.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser, require_roles
from app.core.security import Role
from app.models.returns import ReturnRequest
from app.schemas.common import StandardResponse
from app.schemas.returns import (
    ReturnRequestCreate,
    ReturnRequestResponse,
    ReturnStatusUpdate,
)
from app.services.returns_service import ReturnsService

router = APIRouter()


@router.post("", response_model=StandardResponse[ReturnRequestResponse], status_code=status.HTTP_201_CREATED)
async def create_return_request(
    data: ReturnRequestCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    ret = await ReturnsService.create_return_request(db, data, actor_id=current_user.user_id)
    return StandardResponse(message="Return request authorized", data=ReturnRequestResponse.model_validate(ret))


@router.get("", response_model=StandardResponse[List[ReturnRequestResponse]])
async def list_returns(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    query = select(ReturnRequest)
    if current_user.is_customer():
        query = query.where(ReturnRequest.customer_id == current_user.customer_id)
    res = await db.scalars(query.order_by(ReturnRequest.created_at.desc()))
    return StandardResponse(data=[ReturnRequestResponse.model_validate(r) for r in res.all()])


@router.get("/{return_id}", response_model=StandardResponse[ReturnRequestResponse])
async def get_return(
    return_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    ret = await ReturnsService.get_return(db, return_id)
    return StandardResponse(data=ReturnRequestResponse.model_validate(ret))


@router.patch("/{return_id}/status", response_model=StandardResponse[ReturnRequestResponse])
async def update_return_status(
    return_id: str,
    data: ReturnStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    ret = await ReturnsService.update_status(db, return_id, data, actor_id=current_user.user_id)
    return StandardResponse(message="Return status updated", data=ReturnRequestResponse.model_validate(ret))
