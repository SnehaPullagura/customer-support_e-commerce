"""
Workforce Management schemas for agents, skills, and teams.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field

from app.schemas.common import BaseSchema


class SkillCreate(BaseSchema):
    code: str = Field(..., min_length=2, max_length=50)
    name: str
    category: str = "TECHNICAL"
    description: Optional[str] = None


class SkillResponse(BaseSchema):
    id: str
    code: str
    name: str
    category: str
    description: Optional[str] = None
    created_at: datetime


class TeamCreate(BaseSchema):
    name: str
    department: str = "SUPPORT"
    description: Optional[str] = None
    lead_agent_id: Optional[str] = None


class TeamResponse(BaseSchema):
    id: str
    name: str
    department: str
    description: Optional[str] = None
    is_active: bool
    lead_agent_id: Optional[str] = None
    created_at: datetime


class AgentSkillResponse(BaseSchema):
    skill_id: str
    skill_code: str
    skill_name: str
    proficiency_level: int


class AgentCreate(BaseSchema):
    user_id: str
    team_id: Optional[str] = None
    employee_code: str
    display_name: str
    tier: str = "TIER_1"
    max_active_cases: int = 5
    languages: List[str] = ["en"]
    skill_ids: List[str] = []


class AgentUpdate(BaseSchema):
    team_id: Optional[str] = None
    display_name: Optional[str] = None
    status: Optional[str] = None
    tier: Optional[str] = None
    max_active_cases: Optional[int] = None
    languages: Optional[List[str]] = None


class AgentStatusUpdateRequest(BaseSchema):
    status: str  # AVAILABLE, BUSY, AWAY, OFFLINE, ON_BREAK


class AgentResponse(BaseSchema):
    id: str
    user_id: str
    team_id: Optional[str] = None
    employee_code: str
    display_name: str
    status: str
    max_active_cases: int
    current_active_cases: int
    tier: str
    languages: List[str]
    csat_score: float
    avg_resolution_mins: float
    total_resolved_cases: int
    created_at: datetime
    updated_at: datetime


class AgentDetailResponse(AgentResponse):
    team: Optional[TeamResponse] = None
    skills: List[AgentSkillResponse] = []
