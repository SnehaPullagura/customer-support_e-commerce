"""
Operational, SLA, Agent Performance, and Business Analytics schemas.
"""

from datetime import datetime
from typing import Dict, List, Optional
from app.schemas.common import BaseSchema


class OperationalMetricsResponse(BaseSchema):
    period_start: datetime
    period_end: datetime
    total_cases_created: int
    total_cases_resolved: int
    total_tickets_closed: int
    avg_first_response_time_mins: float
    avg_resolution_time_hours: float
    sla_compliance_rate_percent: float
    escalation_rate_percent: float
    reopen_rate_percent: float
    csat_average: float
    deflection_rate_percent: float


class AgentPerformanceResponse(BaseSchema):
    agent_id: str
    display_name: str
    team_name: Optional[str] = None
    status: str
    cases_handled_count: int
    cases_resolved_count: int
    avg_response_time_mins: float
    avg_resolution_time_hours: float
    sla_compliance_percent: float
    csat_score: float


class SLAAnalyticsResponse(BaseSchema):
    total_evaluated_cases: int
    total_breaches: int
    first_response_compliance_percent: float
    resolution_compliance_percent: float
    breaches_by_priority: Dict[str, int]
    breaches_by_team: Dict[str, int]


class ExecutiveDashboardResponse(BaseSchema):
    metrics: OperationalMetricsResponse
    active_cases_by_status: Dict[str, int]
    active_cases_by_priority: Dict[str, int]
    top_complaint_categories: Dict[str, int]
    recent_breaches_count: int
    top_performing_agents: List[AgentPerformanceResponse]
