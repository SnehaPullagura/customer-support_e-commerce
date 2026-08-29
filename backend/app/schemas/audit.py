"""
Audit Event schemas.
"""

from datetime import datetime
from typing import Optional
from app.schemas.common import BaseSchema


class AuditQueryFilter(BaseSchema):
    actor_id: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    correlation_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class AuditEventResponse(BaseSchema):
    id: str
    actor_id: Optional[str] = None
    actor_email: Optional[str] = None
    actor_role: str
    action: str
    resource_type: str
    resource_id: str
    ip_address: Optional[str] = None
    correlation_id: Optional[str] = None
    description: str
    changes_json: Optional[dict] = None
    created_at: datetime
