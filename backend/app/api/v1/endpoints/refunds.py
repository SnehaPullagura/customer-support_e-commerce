"""
Refund Support endpoints.
"""

from typing import Annotated, Optional
import uuid
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser, require_roles
from app.core.security import Role
from app.schemas.common import StandardResponse
from app.schemas.refunds import (
    RefundRequestCreate,
    RefundRequestResponse,
)
from app.services.refunds_service import RefundsService

router = APIRouter()


@router.post("", response_model=StandardResponse[RefundRequestResponse], status_code=status.HTTP_201_CREATED)
async def create_refund(
    data: RefundRequestCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
):
    idem_key = x_idempotency_key or f"refund-{data.payment_id}-{uuid.uuid4().hex[:6]}"
    refund_req = await RefundsService.create_refund_request(
        db, data=data, idempotency_key=idem_key, actor_id=current_user.user_id
    )
    return StandardResponse(
        message="Refund request created",
        data=RefundRequestResponse.model_validate(refund_req),
    )


@router.get("/{refund_id}", response_model=StandardResponse[RefundRequestResponse])
async def get_refund(
    refund_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    refund_req = await RefundsService.get_refund(db, refund_id)
    return StandardResponse(data=RefundRequestResponse.model_validate(refund_req))
