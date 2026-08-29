"""
Customer Schemas for profile, preferences, timeline, and tags.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema


class CustomerCreate(BaseSchema):
    user_id: Optional[str] = None
    external_customer_id: Optional[str] = None
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    preferred_language: str = "en"
    segment: str = "STANDARD"
    tier: str = "BRONZE"
    notes: Optional[str] = None


class CustomerUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = None
    status: Optional[str] = None
    segment: Optional[str] = None
    tier: Optional[str] = None
    notes: Optional[str] = None


class CustomerPreferenceUpdate(BaseSchema):
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    whatsapp_notifications: Optional[bool] = None
    marketing_opt_in: Optional[bool] = None
    preferred_channel: Optional[str] = None


class CustomerPreferenceResponse(BaseSchema):
    email_notifications: bool
    sms_notifications: bool
    whatsapp_notifications: bool
    marketing_opt_in: bool
    preferred_channel: str


class CustomerTagResponse(BaseSchema):
    id: str
    tag_name: str
    color: str


class CustomerTimelineEventResponse(BaseSchema):
    id: str
    event_type: str
    title: str
    description: Optional[str] = None
    reference_id: Optional[str] = None
    metadata_json: Optional[dict] = None
    created_at: datetime


class CustomerResponse(BaseSchema):
    id: str
    user_id: Optional[str] = None
    external_customer_id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    preferred_language: str
    status: str
    segment: str
    tier: str
    total_orders_count: int
    lifetime_value_cents: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CustomerDetailResponse(CustomerResponse):
    preference: Optional[CustomerPreferenceResponse] = None
    tags: List[CustomerTagResponse] = []
    timeline_events: List[CustomerTimelineEventResponse] = []
