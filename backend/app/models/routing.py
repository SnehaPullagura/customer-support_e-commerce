"""
Intelligent Routing Rules, Queue Definitions, and Routing Audit models.
"""

from typing import List, Optional
from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class RoutingQueue(BaseEntity):
    __tablename__ = "routing_queues"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1 (Highest) to 10
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RoutingRule(BaseEntity):
    __tablename__ = "routing_rules"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority_order: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # Lowest number evaluates first
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Matching criteria (JSON filter conditions)
    match_conditions_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    # e.g., {"category": "PAYMENT", "customer_segment": "VIP", "language": "en"}
    
    # Target assignments
    target_team_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    required_skill_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    routing_strategy: Mapped[str] = mapped_column(String(50), default="LEAST_BUSY", nullable=False)  # LEAST_BUSY, ROUND_ROBIN, HIGHEST_SKILL, DIRECT_TEAM


class RoutingExecutionLog(BaseEntity):
    __tablename__ = "routing_execution_logs"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    matched_rule_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    assigned_team_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    routing_strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    decision_reason: Mapped[str] = mapped_column(Text, nullable=False)
    evaluated_candidates_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
