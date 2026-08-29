"""
Refund Request, Approval, and Transaction schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field

from app.schemas.common import BaseSchema


class RefundRequestCreate(BaseSchema):
    case_id: str
    customer_id: str
    payment_id: str
    order_id: str
    amount_cents: int = Field(..., gt=0)
    currency: str = "USD"
    reason: str


class RefundApprovalRequest(BaseSchema):
    is_approved: bool
    notes: Optional[str] = None


class RefundTransactionResponse(BaseSchema):
    id: str
    gateway_name: str
    gateway_transaction_id: Optional[str] = None
    amount_cents: int
    currency: str
    status: str
    created_at: datetime


class RefundRequestResponse(BaseSchema):
    id: str
    case_id: str
    customer_id: str
    payment_id: str
    order_id: str
    idempotency_key: str
    amount_cents: int
    currency: str
    reason: str
    status: str
    requires_approval: bool
    approved_by_id: Optional[str] = None
    gateway_refund_id: Optional[str] = None
    failure_reason: Optional[str] = None
    transactions: List[RefundTransactionResponse] = []
    created_at: datetime
    updated_at: datetime
