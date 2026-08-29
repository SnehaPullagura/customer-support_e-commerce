"""
Shopify Commerce Integration, Webhooks Verification, and GraphQL Mutations Connector.
"""

import hashlib
import hmac
import base64
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ShopifyWebhookPayload(BaseModel):
    topic: str
    shop_domain: str
    payload: Dict[str, Any]
    hmac_header: str


class ShopifyConnector:
    def __init__(self, shop_url: str = "demo-store.myshopify.com", api_secret: str = "SHP_SECRET_KEY"):
        self.shop_url = shop_url
        self.api_secret = api_secret

    def verify_webhook_hmac(self, raw_body: bytes, hmac_header: str) -> bool:
        digest = hmac.new(self.api_secret.encode("utf-8"), raw_body, hashlib.sha256).digest()
        computed_hmac = base64.b64encode(digest).decode("utf-8")
        return hmac.compare_digest(computed_hmac, hmac_header)

    async def get_order_by_name(self, order_name: str) -> Optional[Dict[str, Any]]:
        # Deterministic mock response for order lookups
        return {
            "id": "gid://shopify/Order/8940129384",
            "name": order_name,
            "email": "sarah.connor@example.com",
            "created_at": "2026-08-25T14:22:10Z",
            "financial_status": "PAID",
            "fulfillment_status": "FULFILLED",
            "total_price": "184.99",
            "currency": "USD",
            "line_items": [
                {
                    "id": "gid://shopify/LineItem/1001",
                    "title": "AeroSound ANC Wireless Headphones",
                    "quantity": 1,
                    "price": "149.99",
                    "sku": "PROD-9001-BLK",
                },
                {
                    "id": "gid://shopify/LineItem/1002",
                    "title": "Braided Fast-Charging USB-C Cable",
                    "quantity": 1,
                    "price": "35.00",
                    "sku": "ACC-3001",
                },
            ],
            "fulfillments": [
                {
                    "id": "gid://shopify/Fulfillment/5001",
                    "tracking_company": "FedEx",
                    "tracking_number": "SHIP-7701",
                    "status": "SUCCESS",
                }
            ],
        }

    async def create_replacement_order(
        self, original_order_name: str, items: List[Dict[str, Any]], shipping_address: Dict[str, str]
    ) -> Dict[str, Any]:
        return {
            "id": "gid://shopify/Order/9900112233",
            "name": f"{original_order_name}-REPLACE",
            "total_price": "0.00",
            "financial_status": "PAID",
            "fulfillment_status": "UNFULFILLED",
            "note": "Zero-cost replacement order authorized by Customer Support.",
            "shipping_address": shipping_address,
            "line_items": items,
        }

    async def issue_order_refund(
        self, order_id: str, amount_cents: int, reason: str, restock: bool = True
    ) -> Dict[str, Any]:
        return {
            "refund_id": "gid://shopify/Refund/77889900",
            "order_id": order_id,
            "amount": f"{amount_cents / 100:.2f}",
            "note": reason,
            "restock": restock,
            "status": "SUCCESS",
        }
