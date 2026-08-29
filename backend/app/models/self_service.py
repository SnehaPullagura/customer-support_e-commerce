"""
Customer Self-Service Sessions, Interactive Troubleshooting Flows, and Deflection records.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class TroubleshootingFlow(BaseEntity):
    __tablename__ = "troubleshooting_flows"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    decision_tree_json: Mapped[dict] = mapped_column(JSON, nullable=False)


class SelfServiceSession(BaseEntity):
    __tablename__ = "self_service_sessions"

    customer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    flow_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("troubleshooting_flows.id", ondelete="SET NULL"), nullable=True)
    session_status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, RESOLVED_DEFLECTED, ESCALATED_TO_CASE
    current_node_key: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    steps_taken_json: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)
    resulting_case_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    is_deflected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
