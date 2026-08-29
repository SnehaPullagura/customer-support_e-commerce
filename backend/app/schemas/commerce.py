"""
Unified Commerce Data Transfer Objects (DTOs) for Orders, Shipments, Payments, and the Commerce Graph.
"""

from datetime import datetime
from typing import List, Optional
from app.schemas.common import BaseSchema


class CommerceCustomerDTO(BaseSchema):
    external_customer_id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    account_created_at: datetime
    total_spent_cents: int
    orders_count: int
    is_vip: bool = False


class CommerceOrderItemDTO(BaseSchema):
    product_id: str
    sku: str
    title: str
    quantity: int
    unit_price_cents: int
    total_price_cents: int
    image_url: Optional[str] = None
    return_eligible_until: Optional[datetime] = None
    is_returnable: bool = True


class CommercePaymentDTO(BaseSchema):
    payment_id: str
    order_id: str
    gateway: str  # STRIPE, PAYPAL, ADYEN, APPLE_PAY
    payment_method: str  # CREDIT_CARD, DEBIT_CARD, WALLET
    amount_cents: int
    currency: str = "USD"
    status: str  # CAPTURED, AUTHORIZED, REFUNDED, PARTIALLY_REFUNDED, FAILED
    last4: Optional[str] = None
    created_at: datetime


class CommerceShipmentTrackingEventDTO(BaseSchema):
    status: str
    description: str
    location: Optional[str] = None
    timestamp: datetime


class CommerceShipmentDTO(BaseSchema):
    shipment_id: str
    order_id: str
    carrier: str  # FEDEX, UPS, DHL, USPS
    tracking_number: str
    tracking_url: Optional[str] = None
    status: str  # LABEL_CREATED, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED, EXCEPTION, RETURNED
    estimated_delivery: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    tracking_history: List[CommerceShipmentTrackingEventDTO] = []


class CommerceReturnDTO(BaseSchema):
    return_id: str
    order_id: str
    rma_number: str
    status: str  # REQUESTED, APPROVED, IN_TRANSIT, RECEIVED, INSPECTED, REFUNDED
    items: List[CommerceOrderItemDTO] = []
    created_at: datetime


class CommerceRefundDTO(BaseSchema):
    refund_id: str
    payment_id: str
    order_id: str
    amount_cents: int
    currency: str = "USD"
    status: str  # SUCCEEDED, PENDING, FAILED
    reason: Optional[str] = None
    created_at: datetime


class CommerceOrderDTO(BaseSchema):
    order_id: str
    order_number: str
    customer_id: str
    status: str  # PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED, RETURNED
    total_amount_cents: int
    tax_amount_cents: int
    shipping_amount_cents: int
    currency: str = "USD"
    placed_at: datetime
    delivered_at: Optional[datetime] = None
    
    items: List[CommerceOrderItemDTO] = []
    payments: List[CommercePaymentDTO] = []
    shipments: List[CommerceShipmentDTO] = []
    returns: List[CommerceReturnDTO] = []
    refunds: List[CommerceRefundDTO] = []


class CommerceGraphDTO(BaseSchema):
    """360-degree aggregated commerce context for a customer or case."""
    customer: Optional[CommerceCustomerDTO] = None
    active_order: Optional[CommerceOrderDTO] = None
    recent_orders: List[CommerceOrderDTO] = []
    recent_shipments: List[CommerceShipmentDTO] = []
    recent_payments: List[CommercePaymentDTO] = []
    recent_returns: List[CommerceReturnDTO] = []
    recent_refunds: List[CommerceRefundDTO] = []
