"""
External Integration & Webhook endpoints.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_roles
from app.core.security import Role
from app.models.integration import WebhookSubscription
from app.schemas.common import StandardResponse
from app.schemas.integration import (
    WebhookSubscriptionCreate,
    WebhookSubscriptionResponse,
)
from app.services.integration_service import IntegrationService

router = APIRouter()


@router.post("/webhooks", response_model=StandardResponse[WebhookSubscriptionResponse], status_code=status.HTTP_201_CREATED)
async def create_webhook_subscription(
    data: WebhookSubscriptionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.ADMINISTRATORS))],
):
    sub = await IntegrationService.create_webhook_subscription(db, data)
    return StandardResponse(message="Webhook subscription created", data=WebhookSubscriptionResponse.model_validate(sub))


@router.get("/webhooks", response_model=StandardResponse[List[WebhookSubscriptionResponse]])
async def list_webhook_subscriptions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.ADMINISTRATORS))],
):
    res = await db.scalars(select(WebhookSubscription).order_by(WebhookSubscription.name))
    return StandardResponse(data=[WebhookSubscriptionResponse.model_validate(s) for s in res.all()])
