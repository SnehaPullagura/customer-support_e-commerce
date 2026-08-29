"""
Return and Replacement Support schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field

from app.schemas.common import BaseSchema


class ReturnItemCreate(BaseSchema):
    product_id: str
    product_name: str
    sku: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    condition: str = "UNOPENED"


class ReturnItemResponse(BaseSchema):
    id: str
    product_id: str
    product_name: str
    sku: Optional[str] = None
    quantity: int
    condition: str


class ReturnRequestCreate(BaseSchema):
    case_id: Optional[str] = None
    customer_id: str
    order_id: str
    reason: str
    items: List[ReturnItemCreate]


class ReturnStatusUpdate(BaseSchema):
    status: str
    carrier_tracking_number: Optional[str] = None
    inspection_notes: Optional[str] = None


class ReturnRequestResponse(BaseSchema):
    id: str
    case_id: Optional[str] = None
    customer_id: str
    order_id: str
    rma_number: str
    status: str
    reason: str
    carrier_tracking_number: Optional[str] = None
    shipping_label_url: Optional[str] = None
    inspection_notes: Optional[str] = None
    items: List[ReturnItemResponse] = []
    created_at: datetime
    updated_at: datetime


class ReplacementOrderResponse(BaseSchema):
    id: str
    case_id: str
    original_order_id: str
    replacement_order_number: str
    status: str
    items_json: List[dict]
    tracking_number: Optional[str] = None
    created_at: datetime
