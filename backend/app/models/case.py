"""
Case Management core entities, status state machines, linking, and audit timeline.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class Case(BaseEntity):
    __tablename__ = "cases"

    case_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Status & Workflow
    status: Mapped[str] = mapped_column(String(50), default="NEW", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), default="GENERAL", nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="WEB_PORTAL", nullable=False)

    # Workforce Assignment
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id", ondelete="SET NULL"), index=True, nullable=True)
    assigned_team_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("teams.id", ondelete="SET NULL"), index=True, nullable=True)

    # Commerce Context References (Loose References, NOT Duplicated Commerce Backend)
    order_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    product_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    payment_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    shipment_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    return_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    refund_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)

    # AI & Customer Intelligence
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)  # -1.0 to +1.0
    frustration_score: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)  # 0.0 to 100.0
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_suggested_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ai_suggested_priority: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Operational Milestones
    first_response_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    first_responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reopened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_escalated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="cases")
    assigned_agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="assigned_cases")
    assigned_team: Mapped[Optional["Team"]] = relationship("Team", back_populates="cases")
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="case", cascade="all, delete-orphan")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="case", cascade="all, delete-orphan")
    timeline_events: Mapped[List["CaseTimelineEvent"]] = relationship("CaseTimelineEvent", back_populates="case", cascade="all, delete-orphan")
    sla_trackers: Mapped[List["SLATracker"]] = relationship("SLATracker", back_populates="case", cascade="all, delete-orphan")
    escalation_events: Mapped[List["EscalationEvent"]] = relationship("EscalationEvent", back_populates="case", cascade="all, delete-orphan")
    resolutions: Mapped[List["Resolution"]] = relationship("Resolution", back_populates="case", cascade="all, delete-orphan")
    outgoing_links: Mapped[List["CaseLink"]] = relationship("CaseLink", foreign_keys="CaseLink.source_case_id", back_populates="source_case", cascade="all, delete-orphan")
    incoming_links: Mapped[List["CaseLink"]] = relationship("CaseLink", foreign_keys="CaseLink.target_case_id", back_populates="target_case", cascade="all, delete-orphan")


class CaseLink(BaseEntity):
    __tablename__ = "case_links"

    source_case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    target_case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    link_type: Mapped[str] = mapped_column(String(50), nullable=False)  # RELATES_TO, DUPLICATE_OF, MERGED_INTO, SPLIT_FROM, PARENT_OF, CHILD_OF
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source_case: Mapped["Case"] = relationship("Case", foreign_keys=[source_case_id], back_populates="outgoing_links")
    target_case: Mapped["Case"] = relationship("Case", foreign_keys=[target_case_id], back_populates="incoming_links")


class CaseTimelineEvent(BaseEntity):
    __tablename__ = "case_timeline_events"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(50), default="SYSTEM", nullable=False)  # SYSTEM, AGENT, CUSTOMER, AI
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # CREATED, STATUS_CHANGED, ASSIGNED, ESCALATED, RESOLVED, etc.
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    previous_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    case: Mapped["Case"] = relationship("Case", back_populates="timeline_events")
