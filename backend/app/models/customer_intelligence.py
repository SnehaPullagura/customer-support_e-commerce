"""
Customer Intelligence, Frustration Scores, Churn Risk, and Effort metrics models.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class CustomerFrustrationScore(BaseEntity):
    __tablename__ = "customer_frustration_scores"

    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=True, index=True)
    
    frustration_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0 to 100
    sentiment_index: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # -1.0 to +1.0
    repeat_contact_count_7d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unresolved_cases_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sla_breaches_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    risk_level: Mapped[str] = mapped_column(String(50), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    factors_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class CustomerChurnRisk(BaseEntity):
    __tablename__ = "customer_churn_risks"

    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), unique=True, nullable=False)
    churn_probability: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0
    predicted_risk_tier: Mapped[str] = mapped_column(String(50), default="LOW", nullable=False)  # LOW, MODERATE, ELEVATED, SEVERE
    last_evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    mitigation_recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
