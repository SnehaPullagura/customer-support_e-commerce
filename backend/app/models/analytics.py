"""
Analytics, Operational Aggregations, Agent Performance, and Quality Metrics models.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class DailyOperationalMetric(BaseEntity):
    __tablename__ = "daily_operational_metrics"

    metric_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    total_cases_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_cases_resolved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tickets_closed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    avg_first_response_time_mins: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    avg_resolution_time_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sla_compliance_rate_percent: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    
    escalation_rate_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reopen_rate_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    csat_average: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    deflection_rate_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    metrics_breakdown_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class AgentPerformanceSnapshot(BaseEntity):
    __tablename__ = "agent_performance_snapshots"

    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    cases_handled_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cases_resolved_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_response_time_mins: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    avg_resolution_time_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sla_compliance_percent: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    csat_score: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)


class ProductComplaintMetric(BaseEntity):
    __tablename__ = "product_complaint_metrics"

    product_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    complaint_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    top_complaint_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    return_rate_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
