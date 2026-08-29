"""
In-Memory Mock E-Commerce Integration Adapter with rich synthetic dataset and deterministic state mutations.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.adapters.commerce.base import CommerceAdapter
from app.core.exceptions import CommerceIntegrationError
from app.schemas.commerce import (
    CommerceCustomerDTO,
    CommerceOrderDTO,
    CommerceOrderItemDTO,
    CommercePaymentDTO,
    CommerceShipmentDTO,
    CommerceShipmentTrackingEventDTO,
    CommerceReturnDTO,
    CommerceRefundDTO,
    CommerceGraphDTO,
)


class MockCommerceAdapter(CommerceAdapter):
    """
    High-fidelity deterministic Mock Commerce Adapter for development,
    demonstration, and end-to-end integration testing.
    """

    def __init__(self) -> None:
        self._customers: Dict[str, CommerceCustomerDTO] = {}
        self._orders: Dict[str, CommerceOrderDTO] = {}
        self._payments: Dict[str, CommercePaymentDTO] = {}
        self._shipments: Dict[str, CommerceShipmentDTO] = {}
        self._returns: Dict[str, CommerceReturnDTO] = {}
        self._refunds: Dict[str, CommerceRefundDTO] = {}
        self._seed_mock_data()

    def _seed_mock_data(self) -> None:
        now = datetime.now(timezone.utc)
        
        # 1. Customers
        c1 = CommerceCustomerDTO(
            external_customer_id="CUST-1001",
            email="sarah.connor@example.com",
            first_name="Sarah",
            last_name="Connor",
            phone="+1-555-0192",
            account_created_at=now - timedelta(days=365),
            total_spent_cents=184990,
            orders_count=12,
            is_vip=True,
        )
        c2 = CommerceCustomerDTO(
            external_customer_id="CUST-1002",
            email="alex.chen@example.com",
            first_name="Alex",
            last_name="Chen",
            phone="+1-555-0144",
            account_created_at=now - timedelta(days=90),
            total_spent_cents=42900,
            orders_count=3,
            is_vip=False,
        )
        self._customers[c1.external_customer_id] = c1
        self._customers[c2.external_customer_id] = c2

        # 2. Orders & Items
        # Order 1: Delivered recently with electronics (Eligible for return/replacement)
        o1_items = [
            CommerceOrderItemDTO(
                product_id="PROD-9001",
                sku="TECH-ANC-HEADPHONES-BLK",
                title="AeroSound Pro Wireless ANC Headphones (Midnight Black)",
                quantity=1,
                unit_price_cents=24999,
                total_price_cents=24999,
                image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
                return_eligible_until=now + timedelta(days=21),
                is_returnable=True,
            ),
            CommerceOrderItemDTO(
                product_id="PROD-9002",
                sku="TECH-USB-C-CABLE-2M",
                title="UltraDura Braided USB-C Fast Charging Cable (2m)",
                quantity=2,
                unit_price_cents=1999,
                total_price_cents=3998,
                image_url="https://images.unsplash.com/photo-1544816155-12df9643f363?w=500",
                return_eligible_until=now + timedelta(days=21),
                is_returnable=True,
            ),
        ]
        
        p1 = CommercePaymentDTO(
            payment_id="PAY-8801",
            order_id="ORD-5001",
            gateway="STRIPE",
            payment_method="CREDIT_CARD",
            amount_cents=28997,
            currency="USD",
            status="CAPTURED",
            last4="4242",
            created_at=now - timedelta(days=5),
        )
        self._payments[p1.payment_id] = p1

        s1 = CommerceShipmentDTO(
            shipment_id="SHIP-7701",
            order_id="ORD-5001",
            carrier="FEDEX",
            tracking_number="FDX992019482US",
            tracking_url="https://www.fedex.com/fedextrack/?trknbr=FDX992019482US",
            status="DELIVERED",
            estimated_delivery=now - timedelta(days=2),
            delivered_at=now - timedelta(days=2),
            tracking_history=[
                CommerceShipmentTrackingEventDTO(
                    status="LABEL_CREATED",
                    description="Shipping label created, package awaiting pickup",
                    location="Memphis, TN Hub",
                    timestamp=now - timedelta(days=5),
                ),
                CommerceShipmentTrackingEventDTO(
                    status="IN_TRANSIT",
                    description="In transit to local distribution center",
                    location="Louisville, KY",
                    timestamp=now - timedelta(days=4),
                ),
                CommerceShipmentTrackingEventDTO(
                    status="OUT_FOR_DELIVERY",
                    description="Out for delivery with FedEx courier",
                    location="Austin, TX",
                    timestamp=now - timedelta(days=2, hours=4),
                ),
                CommerceShipmentTrackingEventDTO(
                    status="DELIVERED",
                    description="Delivered: Left at front porch / gate",
                    location="Austin, TX",
                    timestamp=now - timedelta(days=2),
                ),
            ],
        )
        self._shipments[s1.shipment_id] = s1

        o1 = CommerceOrderDTO(
            order_id="ORD-5001",
            order_number="ORD-5001",
            customer_id="CUST-1001",
            status="DELIVERED",
            total_amount_cents=28997,
            tax_amount_cents=2000,
            shipping_amount_cents=0,
            currency="USD",
            placed_at=now - timedelta(days=5),
            delivered_at=now - timedelta(days=2),
            items=o1_items,
            payments=[p1],
            shipments=[s1],
            returns=[],
            refunds=[],
        )
        self._orders[o1.order_id] = o1

        # Order 2: In-Transit delayed shipment
        o2_items = [
            CommerceOrderItemDTO(
                product_id="PROD-9003",
                sku="HOME-SMART-PLUG-4PK",
                title="WiFi Smart Plug Mini 4-Pack with Energy Monitor",
                quantity=1,
                unit_price_cents=3999,
                total_price_cents=3999,
                image_url="https://images.unsplash.com/photo-1558002038-1055907df827?w=500",
                return_eligible_until=now + timedelta(days=30),
                is_returnable=True,
            )
        ]
        p2 = CommercePaymentDTO(
            payment_id="PAY-8802",
            order_id="ORD-5002",
            gateway="PAYPAL",
            payment_method="WALLET",
            amount_cents=3999,
            currency="USD",
            status="CAPTURED",
            created_at=now - timedelta(days=7),
        )
        self._payments[p2.payment_id] = p2

        s2 = CommerceShipmentDTO(
            shipment_id="SHIP-7702",
            order_id="ORD-5002",
            carrier="USPS",
            tracking_number="9400100000000000000000",
            tracking_url="https://tools.usps.com/go/TrackConfirmAction?tLabels=9400100000000000000000",
            status="EXCEPTION",
            estimated_delivery=now - timedelta(days=1),
            delivered_at=None,
            tracking_history=[
                CommerceShipmentTrackingEventDTO(
                    status="IN_TRANSIT",
                    description="Severe weather delay in Chicago sorting facility",
                    location="Chicago, IL",
                    timestamp=now - timedelta(days=2),
                )
            ],
        )
        self._shipments[s2.shipment_id] = s2

        o2 = CommerceOrderDTO(
            order_id="ORD-5002",
            order_number="ORD-5002",
            customer_id="CUST-1002",
            status="SHIPPED",
            total_amount_cents=3999,
            tax_amount_cents=300,
            shipping_amount_cents=0,
            currency="USD",
            placed_at=now - timedelta(days=7),
            delivered_at=None,
            items=o2_items,
            payments=[p2],
            shipments=[s2],
            returns=[],
            refunds=[],
        )
        self._orders[o2.order_id] = o2

    async def get_customer(self, external_customer_id: str) -> Optional[CommerceCustomerDTO]:
        return self._customers.get(external_customer_id)

    async def get_customer_orders(self, external_customer_id: str, limit: int = 10) -> List[CommerceOrderDTO]:
        matching = [
            order for order in self._orders.values()
            if order.customer_id == external_customer_id
        ]
        return sorted(matching, key=lambda x: x.placed_at, reverse=True)[:limit]

    async def get_order(self, order_id: str) -> Optional[CommerceOrderDTO]:
        if order_id in self._orders:
            return self._orders[order_id]
        # Search by order_number
        for o in self._orders.values():
            if o.order_number.lower() == order_id.lower():
                return o
        return None

    async def get_payment(self, payment_id: str) -> Optional[CommercePaymentDTO]:
        return self._payments.get(payment_id)

    async def get_shipment(self, shipment_id: str) -> Optional[CommerceShipmentDTO]:
        return self._shipments.get(shipment_id)

    async def get_return(self, return_id: str) -> Optional[CommerceReturnDTO]:
        return self._returns.get(return_id)

    async def get_refund(self, refund_id: str) -> Optional[CommerceRefundDTO]:
        return self._refunds.get(refund_id)

    async def create_return_authorization(
        self,
        order_id: str,
        items: List[Dict[str, Any]],
        reason: str,
    ) -> CommerceReturnDTO:
        order = await self.get_order(order_id)
        if not order:
            raise CommerceIntegrationError("create_return_authorization", order_id, "Order not found in commerce system")

        return_id = f"RET-{uuid.uuid4().hex[:8].upper()}"
        rma_number = f"RMA-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        return_items = []
        for it in items:
            prod_id = it.get("product_id", "PROD-UNKNOWN")
            qty = it.get("quantity", 1)
            # Find matching order item
            matched = next((x for x in order.items if x.product_id == prod_id), None)
            if matched:
                return_items.append(
                    CommerceOrderItemDTO(
                        product_id=matched.product_id,
                        sku=matched.sku,
                        title=matched.title,
                        quantity=qty,
                        unit_price_cents=matched.unit_price_cents,
                        total_price_cents=matched.unit_price_cents * qty,
                        image_url=matched.image_url,
                        is_returnable=True,
                    )
                )

        ret_dto = CommerceReturnDTO(
            return_id=return_id,
            order_id=order_id,
            rma_number=rma_number,
            status="APPROVED",
            items=return_items,
            created_at=datetime.now(timezone.utc),
        )
        self._returns[return_id] = ret_dto
        order.returns.append(ret_dto)
        return ret_dto

    async def execute_refund(
        self,
        payment_id: str,
        amount_cents: int,
        reason: str,
        idempotency_key: str,
    ) -> CommerceRefundDTO:
        payment = await self.get_payment(payment_id)
        if not payment:
            # Try to resolve payment from active orders
            for o in self._orders.values():
                for p in o.payments:
                    if p.payment_id == payment_id:
                        payment = p
                        break
        if not payment:
            raise CommerceIntegrationError("execute_refund", payment_id, "Payment ledger record not found")

        if amount_cents > payment.amount_cents:
            raise CommerceIntegrationError(
                "execute_refund",
                payment_id,
                f"Requested refund amount ({amount_cents} cents) exceeds original charge ({payment.amount_cents} cents)",
            )

        refund_id = f"REF-{uuid.uuid4().hex[:8].upper()}"
        ref_dto = CommerceRefundDTO(
            refund_id=refund_id,
            payment_id=payment_id,
            order_id=payment.order_id,
            amount_cents=amount_cents,
            currency=payment.currency,
            status="SUCCEEDED",
            reason=reason,
            created_at=datetime.now(timezone.utc),
        )
        self._refunds[refund_id] = ref_dto

        # Update order refund list
        order = await self.get_order(payment.order_id)
        if order:
            order.refunds.append(ref_dto)
            if amount_cents == payment.amount_cents:
                payment.status = "REFUNDED"
            else:
                payment.status = "PARTIALLY_REFUNDED"

        return ref_dto

    async def create_replacement_order(
        self,
        original_order_id: str,
        items: List[Dict[str, Any]],
        shipping_address: Optional[Dict[str, Any]] = None,
    ) -> CommerceOrderDTO:
        original = await self.get_order(original_order_id)
        if not original:
            raise CommerceIntegrationError("create_replacement_order", original_order_id, "Original order not found")

        now = datetime.now(timezone.utc)
        repl_id = f"ORD-REPL-{uuid.uuid4().hex[:6].upper()}"
        
        replacement_items = []
        for it in items:
            prod_id = it.get("product_id", "")
            qty = it.get("quantity", 1)
            matched = next((x for x in original.items if x.product_id == prod_id), None)
            if matched:
                replacement_items.append(
                    CommerceOrderItemDTO(
                        product_id=matched.product_id,
                        sku=matched.sku,
                        title=f"[Replacement] {matched.title}",
                        quantity=qty,
                        unit_price_cents=0,
                        total_price_cents=0,
                        image_url=matched.image_url,
                        is_returnable=True,
                    )
                )

        new_shipment = CommerceShipmentDTO(
            shipment_id=f"SHIP-REPL-{uuid.uuid4().hex[:6].upper()}",
            order_id=repl_id,
            carrier="FEDEX",
            tracking_number=f"FDX-REPL-{uuid.uuid4().hex[:8].upper()}",
            status="LABEL_CREATED",
            estimated_delivery=now + timedelta(days=3),
            delivered_at=None,
            tracking_history=[
                CommerceShipmentTrackingEventDTO(
                    status="LABEL_CREATED",
                    description="Zero-cost replacement shipment authorized and queued for packaging",
                    location="Main Warehouse Hub",
                    timestamp=now,
                )
            ],
        )
        self._shipments[new_shipment.shipment_id] = new_shipment

        repl_order = CommerceOrderDTO(
            order_id=repl_id,
            order_number=repl_id,
            customer_id=original.customer_id,
            status="PROCESSING",
            total_amount_cents=0,
            tax_amount_cents=0,
            shipping_amount_cents=0,
            currency=original.currency,
            placed_at=now,
            delivered_at=None,
            items=replacement_items,
            payments=[],
            shipments=[new_shipment],
            returns=[],
            refunds=[],
        )
        self._orders[repl_id] = repl_order
        return repl_order

    async def get_commerce_graph(
        self,
        external_customer_id: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> CommerceGraphDTO:
        customer_dto = None
        active_order_dto = None
        recent_orders = []
        recent_shipments = []
        recent_payments = []
        recent_returns = []
        recent_refunds = []

        if order_id:
            active_order_dto = await self.get_order(order_id)
            if active_order_dto and not external_customer_id:
                external_customer_id = active_order_dto.customer_id

        if external_customer_id:
            customer_dto = await self.get_customer(external_customer_id)
            recent_orders = await self.get_customer_orders(external_customer_id)

        for o in recent_orders:
            recent_shipments.extend(o.shipments)
            recent_payments.extend(o.payments)
            recent_returns.extend(o.returns)
            recent_refunds.extend(o.refunds)

        return CommerceGraphDTO(
            customer=customer_dto,
            active_order=active_order_dto,
            recent_orders=recent_orders,
            recent_shipments=recent_shipments,
            recent_payments=recent_payments,
            recent_returns=recent_returns,
            recent_refunds=recent_refunds,
        )
