"""
Ticket Management schemas for discrete sub-tasks and attachments.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field

from app.schemas.common import BaseSchema


class TicketAttachmentResponse(BaseSchema):
    id: str
    file_name: str
    file_path: str
    file_size_bytes: int
    mime_type: str
    uploaded_by: Optional[str] = None
    created_at: datetime


class TicketTagResponse(BaseSchema):
    id: str
    tag: str


class TicketHistoryResponse(BaseSchema):
    id: str
    actor_id: Optional[str] = None
    action: str
    changes_json: Optional[dict] = None
    created_at: datetime


class TicketCreate(BaseSchema):
    case_id: str
    subject: str = Field(..., min_length=3, max_length=255)
    description: str
    category: str = "SUPPORT"
    priority: str = "MEDIUM"
    assigned_agent_id: Optional[str] = None
    due_date: Optional[datetime] = None


class TicketUpdate(BaseSchema):
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    due_date: Optional[datetime] = None


class TicketResponse(BaseSchema):
    id: str
    case_id: str
    ticket_number: str
    subject: str
    description: str
    category: str
    priority: str
    status: str
    assigned_agent_id: Optional[str] = None
    due_date: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TicketDetailResponse(TicketResponse):
    attachments: List[TicketAttachmentResponse] = []
    tags: List[TicketTagResponse] = []
    history: List[TicketHistoryResponse] = []
