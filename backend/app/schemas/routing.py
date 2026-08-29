"""
Routing Rules, SLA Policies, and Escalation Event schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field

from app.schemas.common import BaseSchema


# Routing Schemas
class RoutingRuleCreate(BaseSchema):
    name: str
    description: Optional[str] = None
    priority_order: int = 100
    match_conditions_json: dict
    target_team_id: Optional[str] = None
    required_skill_code: Optional[str] = None
    routing_strategy: str = "LEAST_BUSY"
    is_active: bool = True


class RoutingRuleResponse(BaseSchema):
    id: str
    name: str
    description: Optional[str] = None
    priority_order: int
    match_conditions_json: dict
    target_team_id: Optional[str] = None
    required_skill_code: Optional[str] = None
    routing_strategy: str
    is_active: bool
    created_at: datetime


class RoutingDecisionResponse(BaseSchema):
    case_id: str
    assigned_agent_id: Optional[str] = None
    assigned_team_id: Optional[str] = None
    routing_strategy: str
    decision_reason: str
    matched_rule_id: Optional[str] = None


# SLA Schemas
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


# Escalation Schemas
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
