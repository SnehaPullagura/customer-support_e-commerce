"""
Resolution Engine, Resolution Actions, Approvals, and Customer Feedback models.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class Resolution(BaseEntity):
    __tablename__ = "resolutions"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    resolution_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # REFUND, REPLACEMENT, EXCHANGE, STORE_CREDIT, RETURN, DELIVERY_INVESTIGATION, SELLER_ESCALATION, INFORMATION_RESPONSE, ACCOUNT_CORRECTION
    
    status: Mapped[str] = mapped_column(String(50), default="PROPOSED", nullable=False)
    # PROPOSED, PENDING_APPROVAL, APPROVED, EXECUTING, COMPLETED, REJECTED, FAILED
    
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Financial / Quantification
    amount_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    
    requires_manager_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_result_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="resolutions")
    actions: Mapped[List["ResolutionAction"]] = relationship("ResolutionAction", back_populates="resolution", cascade="all, delete-orphan")
    approvals: Mapped[List["ResolutionApproval"]] = relationship("ResolutionApproval", back_populates="resolution", cascade="all, delete-orphan")
    feedbacks: Mapped[List["CustomerFeedback"]] = relationship("CustomerFeedback", back_populates="resolution", cascade="all, delete-orphan")


class ResolutionAction(BaseEntity):
    __tablename__ = "resolution_actions"

    resolution_id: Mapped[str] = mapped_column(String(36), ForeignKey("resolutions.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)  # TRIGGER_REFUND, DISPATCH_REPLACEMENT, CREATE_RMA, ISSUE_CREDIT
    target_system: Mapped[str] = mapped_column(String(50), default="COMMERCE_ADAPTER", nullable=False)
    external_reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING, SUCCESS, FAILED
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action_payload_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    resolution: Mapped["Resolution"] = relationship("Resolution", back_populates="actions")


class ResolutionApproval(BaseEntity):
    __tablename__ = "resolution_approvals"

    resolution_id: Mapped[str] = mapped_column(String(36), ForeignKey("resolutions.id", ondelete="CASCADE"), nullable=False, index=True)
    requested_by_id: Mapped[str] = mapped_column(String(36), nullable=False)
    approver_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING, APPROVED, REJECTED
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    resolution: Mapped["Resolution"] = relationship("Resolution", back_populates="approvals")


class CustomerFeedback(BaseEntity):
    __tablename__ = "customer_feedbacks"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    resolution_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("resolutions.id", ondelete="SET NULL"), nullable=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5 Stars
    customer_effort_score: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1 (Very Easy) to 5 (Very Difficult)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    resolution: Mapped[Optional["Resolution"]] = relationship("Resolution", back_populates="feedbacks")
