"""
Administration System Settings, Feature Flags, and System Configuration models.
"""

from typing import Optional
from sqlalchemy import Boolean, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class SystemSetting(BaseEntity):
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    value_type: Mapped[str] = mapped_column(String(50), default="STRING", nullable=False)  # STRING, INTEGER, BOOLEAN, JSON
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class FeatureFlag(BaseEntity):
    __tablename__ = "feature_flags"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rollout_percentage: Mapped[int] = mapped_column(default=100, nullable=False)
    target_segments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
