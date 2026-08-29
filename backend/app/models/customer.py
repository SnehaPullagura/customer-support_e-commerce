"""
Customer Profile, Preferences, Tags, Devices, and Activity Timeline models.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class Customer(BaseEntity):
    __tablename__ = "customers"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True)
    external_customer_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, BLOCKED, VIP, AT_RISK
    segment: Mapped[str] = mapped_column(String(50), default="STANDARD", nullable=False)  # VIP, REPEAT, NEW, STANDARD
    tier: Mapped[str] = mapped_column(String(50), default="BRONZE", nullable=False)  # BRONZE, SILVER, GOLD, PLATINUM
    total_orders_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lifetime_value_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    preference: Mapped[Optional["CustomerPreference"]] = relationship("CustomerPreference", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    tags: Mapped[List["CustomerTag"]] = relationship("CustomerTag", back_populates="customer", cascade="all, delete-orphan")
    devices: Mapped[List["CustomerDevice"]] = relationship("CustomerDevice", back_populates="customer", cascade="all, delete-orphan")
    timeline_events: Mapped[List["CustomerTimelineEvent"]] = relationship("CustomerTimelineEvent", back_populates="customer", cascade="all, delete-orphan")
    cases: Mapped[List["Case"]] = relationship("Case", back_populates="customer", cascade="all, delete-orphan")


class CustomerPreference(BaseEntity):
    __tablename__ = "customer_preferences"

    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), unique=True, nullable=False)
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sms_notifications: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    whatsapp_notifications: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    marketing_opt_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preferred_channel: Mapped[str] = mapped_column(String(50), default="EMAIL", nullable=False)  # EMAIL, CHAT, SMS, WHATSAPP

    customer: Mapped["Customer"] = relationship("Customer", back_populates="preference")


class CustomerTag(BaseEntity):
    __tablename__ = "customer_tags"

    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str] = mapped_column(String(20), default="#6B7280", nullable=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="tags")


class CustomerDevice(BaseEntity):
    __tablename__ = "customer_devices"

    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)  # IOS, ANDROID, WEB
    device_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    os_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    app_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="devices")


class CustomerTimelineEvent(BaseEntity):
    __tablename__ = "customer_timeline_events"

    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="timeline_events")
