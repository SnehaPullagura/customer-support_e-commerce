"""
Integration Configurations, Webhook Subscriptions, and Delivery History models.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class IntegrationConfig(BaseEntity):
    __tablename__ = "integration_configs"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False)  # COMMERCE, PAYMENT, SHIPPING, CRM, MESSAGING
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    api_key_encrypted: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    settings_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class WebhookSubscription(BaseEntity):
    __tablename__ = "webhook_subscriptions"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret_token: Mapped[str] = mapped_column(String(255), nullable=False)
    subscribed_events: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    deliveries: Mapped[List["WebhookDeliveryLog"]] = relationship("WebhookDeliveryLog", back_populates="subscription", cascade="all, delete-orphan")


class WebhookDeliveryLog(BaseEntity):
    __tablename__ = "webhook_delivery_logs"

    subscription_id: Mapped[str] = mapped_column(String(36), ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    event_topic: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    response_status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # SUCCESS, FAILED, RETRYING
    attempt_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    subscription: Mapped["WebhookSubscription"] = relationship("WebhookSubscription", back_populates="deliveries")
