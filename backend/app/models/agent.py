"""
Workforce Management, Agent Profiles, Teams, Skills, Shifts, and Capacity models.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class Team(BaseEntity):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), default="SUPPORT", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    lead_agent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    agents: Mapped[List["Agent"]] = relationship("Agent", back_populates="team")
    cases: Mapped[List["Case"]] = relationship("Case", back_populates="assigned_team")


class Skill(BaseEntity):
    __tablename__ = "skills"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="TECHNICAL", nullable=False)  # TECHNICAL, BILLING, LOGISTICS, VIP, LANGUAGE
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    agent_skills: Mapped[List["AgentSkill"]] = relationship("AgentSkill", back_populates="skill", cascade="all, delete-orphan")


class Agent(BaseEntity):
    __tablename__ = "agents"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    team_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OFFLINE", nullable=False, index=True)  # AVAILABLE, BUSY, AWAY, OFFLINE, ON_BREAK
    max_active_cases: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    current_active_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tier: Mapped[str] = mapped_column(String(50), default="TIER_1", nullable=False)  # TIER_1, TIER_2, TIER_3, ESCALATION_SPECIALIST
    languages: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["en"], nullable=False)
    csat_score: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    avg_resolution_mins: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_resolved_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="agents")
    skills: Mapped[List["AgentSkill"]] = relationship("AgentSkill", back_populates="agent", cascade="all, delete-orphan")
    assigned_cases: Mapped[List["Case"]] = relationship("Case", back_populates="assigned_agent")
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="assigned_agent")
    status_history: Mapped[List["AgentStatusLog"]] = relationship("AgentStatusLog", back_populates="agent", cascade="all, delete-orphan")


class AgentSkill(BaseEntity):
    __tablename__ = "agent_skills"

    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    proficiency_level: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1 (Novice) to 5 (Master)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="agent_skills")


class AgentStatusLog(BaseEntity):
    __tablename__ = "agent_status_logs"

    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_status: Mapped[str] = mapped_column(String(50), nullable=False)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="status_history")
