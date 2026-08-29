"""
Customer Self-Service and Interactive Guided Troubleshooting schemas.
"""

from typing import List, Optional
from app.schemas.common import BaseSchema


class TroubleshootingFlowCreate(BaseSchema):
    code: str
    title: str
    category: str
    description: Optional[str] = None
    decision_tree_json: dict


class TroubleshootingFlowResponse(BaseSchema):
    id: str
    code: str
    title: str
    category: str
    description: Optional[str] = None
    is_active: bool
    decision_tree_json: dict


class SelfServiceStepRequest(BaseSchema):
    session_id: Optional[str] = None
    flow_code: str
    chosen_option_key: Optional[str] = None
    context_data: Optional[dict] = None


class SelfServiceResponse(BaseSchema):
    session_id: str
    flow_code: str
    current_node: dict
    is_resolved: bool
    is_deflected: bool
    can_escalate_to_case: bool
    suggested_articles: List[dict] = []
