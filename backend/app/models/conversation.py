"""
Omnichannel Conversation, Messaging, Threads, and Internal Notes models.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class Conversation(BaseEntity):
    __tablename__ = "conversations"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(50), default="WEB_CHAT", nullable=False)  # WEB_CHAT, EMAIL, SMS, WHATSAPP, PHONE, INTERNAL
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False)  # OPEN, PAUSED, CLOSED
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    unread_customer_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unread_agent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    participants: Mapped[List["ConversationParticipant"]] = relationship("ConversationParticipant", back_populates="conversation", cascade="all, delete-orphan")


class Message(BaseEntity):
    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CUSTOMER, AGENT, BOT, SYSTEM
    sender_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    sender_name: Mapped[str] = mapped_column(String(100), default="User", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), default="TEXT", nullable=False)  # TEXT, ATTACHMENT, INTERNAL_NOTE, SYSTEM_EVENT, TEMPLATE
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # True if internal note hidden from customer
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    attachments: Mapped[List["MessageAttachment"]] = relationship("MessageAttachment", back_populates="message", cascade="all, delete-orphan")
    read_receipts: Mapped[List["MessageReadReceipt"]] = relationship("MessageReadReceipt", back_populates="message", cascade="all, delete-orphan")


class MessageAttachment(BaseEntity):
    __tablename__ = "message_attachments"

    message_id: Mapped[str] = mapped_column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    message: Mapped["Message"] = relationship("Message", back_populates="attachments")


class MessageReadReceipt(BaseEntity):
    __tablename__ = "message_read_receipts"

    message_id: Mapped[str] = mapped_column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    message: Mapped["Message"] = relationship("Message", back_populates="read_receipts")


class ConversationParticipant(BaseEntity):
    __tablename__ = "conversation_participants"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    participant_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CUSTOMER, AGENT, OBSERVER
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="participants")
