"""
Integration and Webhook Subscription schemas.
"""

from datetime import datetime
from typing import List, Optional
from app.schemas.common import BaseSchema


class IntegrationConfigCreate(BaseSchema):
    name: str
    provider_type: str  # COMMERCE, PAYMENT, SHIPPING, CRM
    base_url: str
    api_key_encrypted: Optional[str] = None
    settings_json: Optional[dict] = None


class IntegrationConfigResponse(BaseSchema):
    id: str
    name: str
    provider_type: str
    base_url: str
    is_active: bool
    settings_json: Optional[dict] = None
    created_at: datetime


class WebhookSubscriptionCreate(BaseSchema):
    name: str
    target_url: str
    secret_token: str
    subscribed_events: List[str]


class WebhookSubscriptionResponse(BaseSchema):
    id: str
    name: str
    target_url: str
    subscribed_events: List[str]
    is_active: bool
    created_at: datetime
