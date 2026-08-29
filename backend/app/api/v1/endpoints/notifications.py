"""
Notification endpoints.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_roles
from app.core.security import Role
from app.models.notification import NotificationTemplate
from app.schemas.common import StandardResponse
from app.schemas.notification import (
    NotificationSendRequest,
    NotificationResponse,
    NotificationTemplateResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter()


@router.post("/send", response_model=StandardResponse[NotificationResponse], status_code=status.HTTP_201_CREATED)
async def send_notification(
    data: NotificationSendRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    notif = await NotificationService.send_notification(db, data)
    return StandardResponse(message="Notification dispatched", data=NotificationResponse.model_validate(notif))


@router.get("/templates", response_model=StandardResponse[List[NotificationTemplateResponse]])
async def list_templates(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    res = await db.scalars(select(NotificationTemplate).where(NotificationTemplate.is_active == True))
    return StandardResponse(data=[NotificationTemplateResponse.model_validate(t) for t in res.all()])
