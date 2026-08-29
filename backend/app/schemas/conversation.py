"""
Conversation, Messaging, and WebSocket event envelope schemas.
"""

from datetime import datetime
from typing import Any, List, Optional
from pydantic import Field

from app.schemas.common import BaseSchema


class MessageAttachmentResponse(BaseSchema):
    id: str
    file_name: str
    file_url: str
    file_size: int
    mime_type: str
    created_at: datetime


class MessageCreate(BaseSchema):
    content: str = Field(..., min_length=1)
    message_type: str = "TEXT"
    is_internal: bool = False
    metadata_json: Optional[dict] = None


class InternalNoteCreate(BaseSchema):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseSchema):
    id: str
    conversation_id: str
    sender_type: str
    sender_id: Optional[str] = None
    sender_name: str
    content: str
    message_type: str
    is_internal: bool
    sentiment_score: Optional[float] = 0.0
    metadata_json: Optional[dict] = None
    attachments: List[MessageAttachmentResponse] = []
    created_at: datetime


class ConversationCreate(BaseSchema):
    case_id: str
    channel: str = "WEB_CHAT"


class ConversationResponse(BaseSchema):
    id: str
    case_id: str
    channel: str
    status: str
    last_message_at: Optional[datetime] = None
    unread_customer_count: int
    unread_agent_count: int
    created_at: datetime
    updated_at: datetime


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse] = []


class WSMessageEnvelope(BaseSchema):
    action: str  # e.g., 'NEW_MESSAGE', 'TYPING_START', 'TYPING_STOP', 'READ_RECEIPT', 'PRESENCE'
    conversation_id: str
    sender_id: str
    sender_name: str
    sender_type: str
    payload: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
