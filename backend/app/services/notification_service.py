"""
Omnichannel Notification Dispatch and Jinja2 Template Rendering Service.
"""

from datetime import datetime, timezone
from typing import Optional
from jinja2 import Template
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.models.notification import Notification, NotificationTemplate
from app.schemas.notification import NotificationSendRequest, NotificationTemplateCreate


DEFAULT_NOTIFICATION_TEMPLATES = [
    {
        "code": "CASE_CREATED_CUSTOMER",
        "name": "Case Creation Confirmation for Customer",
        "channel": "EMAIL",
        "subject_template": "Support Request Received: #{{ case_number }} - {{ title }}",
        "body_template": "Hello {{ customer_name }},\n\nWe have received your support request regarding '{{ title }}'. Our support team has assigned case number #{{ case_number }} and is reviewing your issue.\n\nThank you,\nCustomer Support Team",
    },
    {
        "code": "SLA_BREACH_ALERT",
        "name": "SLA Breach Notification for Managers",
        "channel": "EMAIL",
        "subject_template": "[URGENT SLA BREACH] Case #{{ case_number }} (Priority: {{ priority }})",
        "body_template": "Case #{{ case_number }} has breached its {{ breach_type }} SLA milestone.\nAssigned Agent: {{ agent_name }}\nTime Overdue: {{ overdue_mins }} minutes.\nImmediate management intervention is required.",
    },
    {
        "code": "REFUND_PROCESSED_CUSTOMER",
        "name": "Refund Completed Notification",
        "channel": "EMAIL",
        "subject_template": "Refund Processed for Order #{{ order_number }}",
        "body_template": "Hello {{ customer_name }},\n\nA refund of ${{ amount_formatted }} has been successfully issued to your original payment method.\nTransaction Reference: {{ refund_id }}.\n\nThank you for your patience!",
    },
]


class NotificationService:
    @staticmethod
    async def seed_default_templates(session: AsyncSession) -> None:
        for t_data in DEFAULT_NOTIFICATION_TEMPLATES:
            existing = await session.scalar(
                select(NotificationTemplate).where(NotificationTemplate.code == t_data["code"])
            )
            if not existing:
                t = NotificationTemplate(
                    code=t_data["code"],
                    name=t_data["name"],
                    channel=t_data["channel"],
                    subject_template=t_data["subject_template"],
                    body_template=t_data["body_template"],
                    is_active=True,
                )
                session.add(t)
        await session.commit()

    @staticmethod
    async def send_notification(
        session: AsyncSession,
        request: NotificationSendRequest,
        event_bus: Optional[EventBus] = None,
    ) -> Notification:
        subject = request.subject
        body = request.body

        # Render from template if template_code provided
        if request.template_code:
            tmpl = await session.scalar(
                select(NotificationTemplate).where(NotificationTemplate.code == request.template_code)
            )
            if tmpl:
                template_data = request.template_data or {}
                if tmpl.subject_template:
                    subject = Template(tmpl.subject_template).render(**template_data)
                body = Template(tmpl.body_template).render(**template_data)

        notification = Notification(
            recipient_user_id=request.recipient_user_id,
            recipient_email=request.recipient_email,
            recipient_phone=request.recipient_phone,
            channel=request.channel,
            subject=subject,
            body=body,
            status="SENT",
            sent_at=datetime.now(timezone.utc),
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.NOTIFICATION_SENT,
                payload={
                    "notification_id": notification.id,
                    "channel": notification.channel,
                    "recipient": notification.recipient_email or notification.recipient_phone,
                },
            )
        )
        return notification
