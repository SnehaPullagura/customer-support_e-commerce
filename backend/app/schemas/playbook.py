"""
Resolution Playbooks and Execution Tracking schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field

from app.schemas.common import BaseSchema


class PlaybookStepCreate(BaseSchema):
    step_order: int
    step_key: str
    title: str
    instructions: str
    action_type: str = "MANUAL_CHECK"
    is_mandatory: bool = True
    step_config_json: Optional[dict] = None


class PlaybookStepResponse(BaseSchema):
    id: str
    step_order: int
    step_key: str
    title: str
    instructions: str
    action_type: str
    is_mandatory: bool
    step_config_json: Optional[dict] = None


class PlaybookCreate(BaseSchema):
    code: str
    name: str
    description: Optional[str] = None
    category: str
    estimated_duration_mins: int = 15
    steps: List[PlaybookStepCreate] = []


class PlaybookResponse(BaseSchema):
    id: str
    code: str
    name: str
    description: Optional[str] = None
    category: str
    is_active: bool
    estimated_duration_mins: int
    steps: List[PlaybookStepResponse] = []
    created_at: datetime


class PlaybookExecuteRequest(BaseSchema):
    playbook_id: str


class PlaybookStepExecuteRequest(BaseSchema):
    step_id: str
    status: str = "COMPLETED"  # COMPLETED, SKIPPED, FAILED
    notes: Optional[str] = None
    result_data_json: Optional[dict] = None


class PlaybookStepLogResponse(BaseSchema):
    id: str
    step_id: str
    actor_id: Optional[str] = None
    status: str
    notes: Optional[str] = None
    result_data_json: Optional[dict] = None
    created_at: datetime


class PlaybookExecutionResponse(BaseSchema):
    id: str
    case_id: str
    playbook_id: str
    agent_id: Optional[str] = None
    status: str
    current_step_order: int
    completed_at: Optional[datetime] = None
    playbook: Optional[PlaybookResponse] = None
    step_logs: List[PlaybookStepLogResponse] = []
    created_at: datetime
