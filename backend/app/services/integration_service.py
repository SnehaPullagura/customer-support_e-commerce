"""
External Integrations and Webhook Delivery Service.
"""

from datetime import datetime, timezone
from typing import List, Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.integration import (
    IntegrationConfig,
    WebhookSubscription,
    WebhookDeliveryLog,
)
from app.schemas.integration import (
    IntegrationConfigCreate,
    WebhookSubscriptionCreate,
)


class IntegrationService:
    @staticmethod
    async def create_webhook_subscription(
        session: AsyncSession, data: WebhookSubscriptionCreate
    ) -> WebhookSubscription:
        sub = WebhookSubscription(
            name=data.name,
            target_url=data.target_url,
            secret_token=data.secret_token,
            subscribed_events=data.subscribed_events,
            is_active=True,
        )
        session.add(sub)
        await session.commit()
        await session.refresh(sub)
        return sub

    @staticmethod
    async def dispatch_webhook_event(
        session: AsyncSession, event_topic: str, payload: dict
    ) -> None:
        subs = await session.scalars(
            select(WebhookSubscription).where(WebhookSubscription.is_active == True)
        )
        all_subs = list(subs.all())

        for sub in all_subs:
            if event_topic in sub.subscribed_events or "*" in sub.subscribed_events:
                # Dispatch async HTTP POST
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        resp = await client.post(
                            sub.target_url,
                            json={"topic": event_topic, "payload": payload},
                            headers={"X-Webhook-Secret": sub.secret_token},
                        )
                        log = WebhookDeliveryLog(
                            subscription_id=sub.id,
                            event_topic=event_topic,
                            payload_json=payload,
                            response_status_code=resp.status_code,
                            status="SUCCESS" if resp.is_success else "FAILED",
                            delivered_at=datetime.now(timezone.utc),
                        )
                        session.add(log)
                except Exception as e:
                    log = WebhookDeliveryLog(
                        subscription_id=sub.id,
                        event_topic=event_topic,
                        payload_json=payload,
                        response_body=str(e),
                        status="FAILED",
                    )
                    session.add(log)

        await session.commit()
