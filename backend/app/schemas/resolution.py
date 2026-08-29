"""
Resolution Engine, Resolution Actions, Approvals, and Feedback schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field

from app.schemas.common import BaseSchema


class ResolutionCreate(BaseSchema):
    case_id: str
    resolution_type: str
    summary: str
    details: Optional[str] = None
    amount_cents: int = 0
    currency: str = "USD"
    requires_manager_approval: bool = False


class ResolutionActionExecute(BaseSchema):
    action_type: str
    target_system: str = "COMMERCE_ADAPTER"
    action_payload_json: Optional[dict] = None


class ApprovalDecisionRequest(BaseSchema):
    status: str  # APPROVED, REJECTED
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None


class FeedbackCreate(BaseSchema):
    rating: int = Field(..., ge=1, le=5)
    customer_effort_score: int = Field(default=3, ge=1, le=5)
    comment: Optional[str] = None
    feedback_tags: List[str] = []


class FeedbackResponse(BaseSchema):
    id: str
    case_id: str
    resolution_id: Optional[str] = None
    rating: int
    customer_effort_score: int
    comment: Optional[str] = None
    feedback_tags: List[str] = []
    created_at: datetime


class ResolutionActionResponse(BaseSchema):
    id: str
    action_type: str
    target_system: str
    external_reference_id: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime


class ResolutionResponse(BaseSchema):
    id: str
    case_id: str
    resolution_type: str
    status: str
    summary: str
    details: Optional[str] = None
    amount_cents: int
    currency: str
    requires_manager_approval: bool
    is_approved: bool
    approved_by_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    actions: List[ResolutionActionResponse] = []
    created_at: datetime
    updated_at: datetime
