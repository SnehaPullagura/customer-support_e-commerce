"""
Notification Templates and Dispatch schemas.
"""

from datetime import datetime
from typing import Optional
from app.schemas.common import BaseSchema


class NotificationTemplateCreate(BaseSchema):
    code: str
    name: str
    channel: str = "EMAIL"
    subject_template: Optional[str] = None
    body_template: str


class NotificationTemplateResponse(BaseSchema):
    id: str
    code: str
    name: str
    channel: str
    subject_template: Optional[str] = None
    body_template: str
    is_active: bool
    created_at: datetime


class NotificationSendRequest(BaseSchema):
    recipient_user_id: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    channel: str = "EMAIL"
    subject: Optional[str] = None
    body: str
    template_code: Optional[str] = None
    template_data: Optional[dict] = None


class NotificationResponse(BaseSchema):
    id: str
    recipient_user_id: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    channel: str
    subject: Optional[str] = None
    body: str
    status: str
    retry_count: int
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
