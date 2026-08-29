"""
Abstract base contract for Commerce Integration Adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.schemas.commerce import (
    CommerceCustomerDTO,
    CommerceOrderDTO,
    CommercePaymentDTO,
    CommerceShipmentDTO,
    CommerceReturnDTO,
    CommerceRefundDTO,
    CommerceGraphDTO,
)


class CommerceAdapter(ABC):
    """
    Abstract contract defining the integration layer between the Support Platform
    and the external E-Commerce Order/Payment/Inventory/Shipping systems.
    """

    @abstractmethod
    async def get_customer(self, external_customer_id: str) -> Optional[CommerceCustomerDTO]:
        """Fetch customer profile and summary metrics from commerce system."""
        pass

    @abstractmethod
    async def get_customer_orders(self, external_customer_id: str, limit: int = 10) -> List[CommerceOrderDTO]:
        """Fetch historical orders for a given customer."""
        pass

    @abstractmethod
    async def get_order(self, order_id: str) -> Optional[CommerceOrderDTO]:
        """Fetch detailed order by ID or order number."""
        pass

    @abstractmethod
    async def get_payment(self, payment_id: str) -> Optional[CommercePaymentDTO]:
        """Fetch payment details and transaction status."""
        pass

    @abstractmethod
    async def get_shipment(self, shipment_id: str) -> Optional[CommerceShipmentDTO]:
        """Fetch shipment tracking status and carrier milestones."""
        pass

    @abstractmethod
    async def get_return(self, return_id: str) -> Optional[CommerceReturnDTO]:
        """Fetch return status and warehouse receipt status."""
        pass

    @abstractmethod
    async def get_refund(self, refund_id: str) -> Optional[CommerceRefundDTO]:
        """Fetch refund transaction ledger record."""
        pass

    @abstractmethod
    async def create_return_authorization(
        self,
        order_id: str,
        items: List[Dict[str, Any]],
        reason: str,
    ) -> CommerceReturnDTO:
        """Issue an authorized RMA in the commerce system."""
        pass

    @abstractmethod
    async def execute_refund(
        self,
        payment_id: str,
        amount_cents: int,
        reason: str,
        idempotency_key: str,
    ) -> CommerceRefundDTO:
        """Execute a refund against the payment gateway with idempotency."""
        pass

    @abstractmethod
    async def create_replacement_order(
        self,
        original_order_id: str,
        items: List[Dict[str, Any]],
        shipping_address: Optional[Dict[str, Any]] = None,
    ) -> CommerceOrderDTO:
        """Dispatch a zero-cost replacement order in the commerce system."""
        pass

    @abstractmethod
    async def get_commerce_graph(
        self,
        external_customer_id: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> CommerceGraphDTO:
        """Build the full 360-degree connected commerce context graph."""
        pass
