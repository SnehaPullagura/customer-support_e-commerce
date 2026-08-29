"""
SLA Policy Management, Active Timers, Pause History, and Breach Logging models.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class SLAPolicy(BaseEntity):
    __tablename__ = "sla_policies"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW, ALL
    category: Mapped[str] = mapped_column(String(50), default="ALL", nullable=False)  # ALL or specific category
    customer_tier: Mapped[str] = mapped_column(String(50), default="ALL", nullable=False)  # ALL, VIP, PLATINUM, GOLD, etc.
    
    first_response_time_mins: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution_time_hours: Mapped[float] = mapped_column(Float, nullable=False)
    warning_threshold_percent: Mapped[int] = mapped_column(Integer, default=75, nullable=False)  # Warn when 75% elapsed
    
    use_business_hours: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    business_hours_start: Mapped[str] = mapped_column(String(10), default="09:00", nullable=False)
    business_hours_end: Mapped[str] = mapped_column(String(10), default="18:00", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    trackers: Mapped[List["SLATracker"]] = relationship("SLATracker", back_populates="policy")


class SLATracker(BaseEntity):
    __tablename__ = "sla_trackers"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(36), ForeignKey("sla_policies.id", ondelete="CASCADE"), nullable=False)
    
    first_response_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolution_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    first_responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    is_first_response_breached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_resolution_breached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    is_warning_emitted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    total_paused_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="sla_trackers")
    policy: Mapped["SLAPolicy"] = relationship("SLAPolicy", back_populates="trackers")
    pause_logs: Mapped[List["SLAPauseLog"]] = relationship("SLAPauseLog", back_populates="tracker", cascade="all, delete-orphan")
    breach_logs: Mapped[List["SLABreachLog"]] = relationship("SLABreachLog", back_populates="tracker", cascade="all, delete-orphan")


class SLAPauseLog(BaseEntity):
    __tablename__ = "sla_pause_logs"

    tracker_id: Mapped[str] = mapped_column(String(36), ForeignKey("sla_trackers.id", ondelete="CASCADE"), nullable=False, index=True)
    paused_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    pause_reason: Mapped[str] = mapped_column(String(100), nullable=False)  # WAITING_FOR_CUSTOMER, WAITING_FOR_CARRIER, etc.
    paused_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    tracker: Mapped["SLATracker"] = relationship("SLATracker", back_populates="pause_logs")


class SLABreachLog(BaseEntity):
    __tablename__ = "sla_breach_logs"

    tracker_id: Mapped[str] = mapped_column(String(36), ForeignKey("sla_trackers.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    breach_type: Mapped[str] = mapped_column(String(50), nullable=False)  # FIRST_RESPONSE, RESOLUTION
    breached_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    overdue_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    tracker: Mapped["SLATracker"] = relationship("SLATracker", back_populates="breach_logs")


class HolidayCalendar(BaseEntity):
    __tablename__ = "holiday_calendars"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    holiday_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    country_code: Mapped[str] = mapped_column(String(5), default="US", nullable=False)
