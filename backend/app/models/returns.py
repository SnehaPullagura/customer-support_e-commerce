"""
Return & Replacement Support models orchestrating customer RMA and exchange workflows.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class ReturnRequest(BaseEntity):
    __tablename__ = "return_requests"

    case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    rma_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)
    # PENDING, APPROVED, LABEL_GENERATED, SHIPPED_BY_CUSTOMER, RECEIVED_AT_WAREHOUSE, INSPECTED_PASSED, REJECTED, COMPLETED
    
    reason: Mapped[str] = mapped_column(String(100), nullable=False)
    carrier_tracking_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    shipping_label_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    inspection_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items: Mapped[List["ReturnItem"]] = relationship("ReturnItem", back_populates="return_request", cascade="all, delete-orphan")


class ReturnItem(BaseEntity):
    __tablename__ = "return_items"

    return_request_id: Mapped[str] = mapped_column(String(36), ForeignKey("return_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    condition: Mapped[str] = mapped_column(String(50), default="UNOPENED", nullable=False)  # UNOPENED, OPENED_LIKE_NEW, DAMAGED, DEFECTIVE

    return_request: Mapped["ReturnRequest"] = relationship("ReturnRequest", back_populates="items")


class ReplacementOrder(BaseEntity):
    __tablename__ = "replacement_orders"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    original_order_id: Mapped[str] = mapped_column(String(100), nullable=False)
    replacement_order_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING, CREATED_IN_COMMERCE, SHIPPED, DELIVERED
    items_json: Mapped[List[dict]] = mapped_column(JSON, nullable=False)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
