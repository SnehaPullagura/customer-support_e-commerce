"""
Case Management schemas for case lifecycle, assignments, timelines, and links.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field

from app.schemas.common import BaseSchema
from app.schemas.customer import CustomerResponse


class CaseCreate(BaseSchema):
    customer_id: str
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    category: str = "GENERAL"
    subcategory: Optional[str] = None
    priority: str = "MEDIUM"
    source: str = "WEB_PORTAL"
    
    # Commerce References
    order_id: Optional[str] = None
    product_id: Optional[str] = None
    payment_id: Optional[str] = None
    shipment_id: Optional[str] = None


class CaseUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    assigned_team_id: Optional[str] = None
    order_id: Optional[str] = None
    product_id: Optional[str] = None
    payment_id: Optional[str] = None
    shipment_id: Optional[str] = None
    return_id: Optional[str] = None
    refund_id: Optional[str] = None


class CaseAssignRequest(BaseSchema):
    agent_id: Optional[str] = None
    team_id: Optional[str] = None
    reason: Optional[str] = None


class CaseEscalateRequest(BaseSchema):
    escalation_reason: str
    escalate_to_role: Optional[str] = "TEAM_LEAD"
    notes: Optional[str] = None


class CaseResolveRequest(BaseSchema):
    resolution_type: str  # REFUND, REPLACEMENT, EXCHANGE, STORE_CREDIT, RETURN, INFORMATION_RESPONSE
    summary: str
    details: Optional[str] = None
    amount_cents: int = 0
    currency: str = "USD"


class CaseLinkRequest(BaseSchema):
    target_case_id: str
    link_type: str  # RELATES_TO, DUPLICATE_OF, MERGED_INTO, SPLIT_FROM
    reason: Optional[str] = None


class CaseTimelineEventResponse(BaseSchema):
    id: str
    actor_id: Optional[str] = None
    actor_type: str
    event_type: str
    summary: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    metadata_json: Optional[dict] = None
    created_at: datetime


class CaseLinkResponse(BaseSchema):
    id: str
    source_case_id: str
    target_case_id: str
    link_type: str
    reason: Optional[str] = None
    created_at: datetime


class CaseResponse(BaseSchema):
    id: str
    case_number: str
    customer_id: str
    title: str
    description: str
    status: str
    priority: str
    category: str
    subcategory: Optional[str] = None
    source: str
    
    assigned_agent_id: Optional[str] = None
    assigned_team_id: Optional[str] = None
    
    order_id: Optional[str] = None
    product_id: Optional[str] = None
    payment_id: Optional[str] = None
    shipment_id: Optional[str] = None
    return_id: Optional[str] = None
    refund_id: Optional[str] = None
    
    sentiment_score: Optional[float] = 0.0
    frustration_score: Optional[float] = 0.0
    ai_summary: Optional[str] = None
    is_escalated: bool = False
    
    first_response_due_at: Optional[datetime] = None
    resolution_due_at: Optional[datetime] = None
    first_responded_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime


class CaseDetailResponse(CaseResponse):
    customer: Optional[CustomerResponse] = None
    timeline_events: List[CaseTimelineEventResponse] = []
    outgoing_links: List[CaseLinkResponse] = []
    incoming_links: List[CaseLinkResponse] = []
