"""
SLA Policy and Tracker schemas.
"""

from datetime import datetime
from typing import Optional
from app.schemas.common import BaseSchema


class SLAPolicyCreate(BaseSchema):
    name: str
    description: Optional[str] = None
    priority: str = "ALL"
    category: str = "ALL"
    customer_tier: str = "ALL"
    first_response_time_mins: int
    resolution_time_hours: float
    warning_threshold_percent: int = 75
    use_business_hours: bool = False
    business_hours_start: str = "09:00"
    business_hours_end: str = "18:00"
    timezone: str = "UTC"
    is_active: bool = True


class SLAPolicyResponse(BaseSchema):
    id: str
    name: str
    description: Optional[str] = None
    priority: str
    category: str
    customer_tier: str
    first_response_time_mins: int
    resolution_time_hours: float
    warning_threshold_percent: int
    use_business_hours: bool
    is_active: bool
    created_at: datetime


class SLATrackerResponse(BaseSchema):
    id: str
    case_id: str
    policy_id: str
    first_response_due_at: datetime
    resolution_due_at: datetime
    first_responded_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    is_first_response_breached: bool
    is_resolution_breached: bool
    is_warning_emitted: bool
    is_paused: bool
    total_paused_seconds: int
    created_at: datetime
