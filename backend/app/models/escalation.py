"""
Escalation Policy, Triggers, and Escalation Event models.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class EscalationPolicy(BaseEntity):
    __tablename__ = "escalation_policies"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)  # SLA_BREACH, TIME_ELAPSED, REPEAT_CONTACT, CUSTOMER_FRUSTRATION, MANUAL
    threshold_value: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Minutes, score threshold, or count
    
    escalate_to_role: Mapped[str] = mapped_column(String(50), default="TEAM_LEAD", nullable=False)  # TEAM_LEAD, MANAGER, DIRECTOR, SPECIALIST
    target_team_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    notify_managers: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class EscalationEvent(BaseEntity):
    __tablename__ = "escalation_events"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("escalation_policies.id", ondelete="SET NULL"), nullable=True)
    escalation_reason: Mapped[str] = mapped_column(String(100), nullable=False)
    escalation_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1 (Lead), 2 (Manager), 3 (Exec)
    
    escalated_by_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    escalated_to_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False)  # OPEN, ACKNOWLEDGED, RESOLVED

    case: Mapped["Case"] = relationship("Case", back_populates="escalation_events")
