"""
Resolution Playbooks, Structured Workflow Steps, and Execution Audit models.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class Playbook(BaseEntity):
    __tablename__ = "playbooks"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    estimated_duration_mins: Mapped[int] = mapped_column(Integer, default=15, nullable=False)

    # Relationships
    steps: Mapped[List["PlaybookStep"]] = relationship("PlaybookStep", back_populates="playbook", cascade="all, delete-orphan", order_by="PlaybookStep.step_order")
    executions: Mapped[List["PlaybookExecution"]] = relationship("PlaybookExecution", back_populates="playbook", cascade="all, delete-orphan")


class PlaybookStep(BaseEntity):
    __tablename__ = "playbook_steps"

    playbook_id: Mapped[str] = mapped_column(String(36), ForeignKey("playbooks.id", ondelete="CASCADE"), nullable=False, index=True)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_key: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), default="MANUAL_CHECK", nullable=False)
    # MANUAL_CHECK, API_VERIFICATION, REQUIRE_ATTACHMENT, PROMPT_CUSTOMER, EXECUTE_ACTION
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    step_config_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    playbook: Mapped["Playbook"] = relationship("Playbook", back_populates="steps")


class PlaybookExecution(BaseEntity):
    __tablename__ = "playbook_executions"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    playbook_id: Mapped[str] = mapped_column(String(36), ForeignKey("playbooks.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="IN_PROGRESS", nullable=False)  # IN_PROGRESS, COMPLETED, ABORTED
    current_step_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    playbook: Mapped["Playbook"] = relationship("Playbook", back_populates="executions")
    step_logs: Mapped[List["PlaybookStepLog"]] = relationship("PlaybookStepLog", back_populates="execution", cascade="all, delete-orphan")


class PlaybookStepLog(BaseEntity):
    __tablename__ = "playbook_step_logs"

    execution_id: Mapped[str] = mapped_column(String(36), ForeignKey("playbook_executions.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id: Mapped[str] = mapped_column(String(36), ForeignKey("playbook_steps.id", ondelete="CASCADE"), nullable=False)
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED", nullable=False)  # COMPLETED, SKIPPED, FAILED
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result_data_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    execution: Mapped["PlaybookExecution"] = relationship("PlaybookExecution", back_populates="step_logs")
