"""
Escalation Policy and Event schemas.
"""

from datetime import datetime
from typing import Optional
from app.schemas.common import BaseSchema


class EscalationPolicyCreate(BaseSchema):
    name: str
    description: Optional[str] = None
    trigger_type: str  # SLA_BREACH, TIME_ELAPSED, REPEAT_CONTACT, CUSTOMER_FRUSTRATION, MANUAL
    threshold_value: int = 0
    escalate_to_role: str = "TEAM_LEAD"
    target_team_id: Optional[str] = None
    notify_managers: bool = True
    is_active: bool = True


class EscalationPolicyResponse(BaseSchema):
    id: str
    name: str
    description: Optional[str] = None
    trigger_type: str
    threshold_value: int
    escalate_to_role: str
    target_team_id: Optional[str] = None
    notify_managers: bool
    is_active: bool
    created_at: datetime


class EscalationEventResponse(BaseSchema):
    id: str
    case_id: str
    policy_id: Optional[str] = None
    escalation_reason: str
    escalation_level: int
    escalated_by_id: Optional[str] = None
    escalated_to_id: Optional[str] = None
    notes: Optional[str] = None
    status: str
    created_at: datetime
