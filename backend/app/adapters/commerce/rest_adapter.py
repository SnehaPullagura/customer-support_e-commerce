"""
REST HTTP Adapter for connecting to external E-Commerce APIs via HTTP/JSON.
"""

from typing import Any, Dict, List, Optional
import httpx

from app.adapters.commerce.base import CommerceAdapter
from app.core.config import settings
from app.core.exceptions import CommerceIntegrationError
from app.schemas.commerce import (
    CommerceCustomerDTO,
    CommerceOrderDTO,
    CommercePaymentDTO,
    CommerceShipmentDTO,
    CommerceReturnDTO,
    CommerceRefundDTO,
    CommerceGraphDTO,
)


class RestCommerceAdapter(CommerceAdapter):
    """
    Adapter communicating with external e-commerce REST services (e.g., Shopify, Custom ERP).
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or settings.COMMERCE_API_BASE_URL or "http://localhost:9000"
        self.api_key = api_key or settings.COMMERCE_API_KEY or ""
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"{settings.PROJECT_NAME}/{settings.VERSION}",
        }

    async def _request(self, method: str, endpoint: str, json_data: Optional[dict] = None) -> Any:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.request(method, url, headers=self.headers, json=json_data)
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise CommerceIntegrationError(
                    method,
                    endpoint,
                    f"Remote API responded with status {e.response.status_code}: {e.response.text}",
                    status_code=502,
                )
            except Exception as e:
                raise CommerceIntegrationError(
                    method,
                    endpoint,
                    f"Connection failed: {str(e)}",
                    status_code=503,
                )

    async def get_customer(self, external_customer_id: str) -> Optional[CommerceCustomerDTO]:
        data = await self._request("GET", f"/api/customers/{external_customer_id}")
        return CommerceCustomerDTO(**data) if data else None

    async def get_customer_orders(self, external_customer_id: str, limit: int = 10) -> List[CommerceOrderDTO]:
        data = await self._request("GET", f"/api/customers/{external_customer_id}/orders?limit={limit}")
        return [CommerceOrderDTO(**item) for item in data] if data else []

    async def get_order(self, order_id: str) -> Optional[CommerceOrderDTO]:
        data = await self._request("GET", f"/api/orders/{order_id}")
        return CommerceOrderDTO(**data) if data else None

    async def get_payment(self, payment_id: str) -> Optional[CommercePaymentDTO]:
        data = await self._request("GET", f"/api/payments/{payment_id}")
        return CommercePaymentDTO(**data) if data else None

    async def get_shipment(self, shipment_id: str) -> Optional[CommerceShipmentDTO]:
        data = await self._request("GET", f"/api/shipments/{shipment_id}")
        return CommerceShipmentDTO(**data) if data else None

    async def get_return(self, return_id: str) -> Optional[CommerceReturnDTO]:
        data = await self._request("GET", f"/api/returns/{return_id}")
        return CommerceReturnDTO(**data) if data else None

    async def get_refund(self, refund_id: str) -> Optional[CommerceRefundDTO]:
        data = await self._request("GET", f"/api/refunds/{refund_id}")
        return CommerceRefundDTO(**data) if data else None

    async def create_return_authorization(
        self,
        order_id: str,
        items: List[Dict[str, Any]],
        reason: str,
    ) -> CommerceReturnDTO:
        payload = {"items": items, "reason": reason}
        data = await self._request("POST", f"/api/orders/{order_id}/returns", json_data=payload)
        return CommerceReturnDTO(**data)

    async def execute_refund(
        self,
        payment_id: str,
        amount_cents: int,
        reason: str,
        idempotency_key: str,
    ) -> CommerceRefundDTO:
        payload = {
            "amount_cents": amount_cents,
            "reason": reason,
            "idempotency_key": idempotency_key,
        }
        data = await self._request("POST", f"/api/payments/{payment_id}/refunds", json_data=payload)
        return CommerceRefundDTO(**data)

    async def create_replacement_order(
        self,
        original_order_id: str,
        items: List[Dict[str, Any]],
        shipping_address: Optional[Dict[str, Any]] = None,
    ) -> CommerceOrderDTO:
        payload = {
            "original_order_id": original_order_id,
            "items": items,
            "shipping_address": shipping_address,
        }
        data = await self._request("POST", "/api/orders/replacement", json_data=payload)
        return CommerceOrderDTO(**data)

    async def get_commerce_graph(
        self,
        external_customer_id: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> CommerceGraphDTO:
        params = []
        if external_customer_id:
            params.append(f"customer_id={external_customer_id}")
        if order_id:
            params.append(f"order_id={order_id}")
        query = "&".join(params)
        data = await self._request("GET", f"/api/graph?{query}")
        return CommerceGraphDTO(**data) if data else CommerceGraphDTO()
