"""
Refund Support models with idempotency tracking and gateway ledger references.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class RefundRequest(BaseEntity):
    __tablename__ = "refund_requests"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    reason: Mapped[str] = mapped_column(String(100), nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), default="PENDING_APPROVAL", nullable=False, index=True)
    # PENDING_APPROVAL, APPROVED, PROCESSING, COMPLETED, REJECTED, FAILED
    
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    gateway_refund_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    transactions: Mapped[List["RefundTransaction"]] = relationship("RefundTransaction", back_populates="refund_request", cascade="all, delete-orphan")


class RefundTransaction(BaseEntity):
    __tablename__ = "refund_transactions"

    refund_request_id: Mapped[str] = mapped_column(String(36), ForeignKey("refund_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    gateway_name: Mapped[str] = mapped_column(String(50), default="STRIPE", nullable=False)
    gateway_transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # SUCCESS, FAILED, PENDING
    gateway_response_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    refund_request: Mapped["RefundRequest"] = relationship("RefundRequest", back_populates="transactions")
