"""
Immutable Security & Business Operation Audit Event Ledger.
"""

from typing import Optional
from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class AuditEvent(BaseEntity):
    __tablename__ = "audit_events"

    actor_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    actor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    actor_role: Mapped[str] = mapped_column(String(50), default="SYSTEM", nullable=False)
    
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # CASE_CREATED, CASE_ASSIGNED, CASE_ESCALATED, RESOLUTION_APPROVED, REFUND_TRIGGERED, ROLE_CHANGED, SETTING_UPDATED
    
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # CASE, REFUND, USER, SLA, SETTING
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    changes_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {"before": {...}, "after": {...}}
