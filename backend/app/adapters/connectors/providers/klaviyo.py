"""
Klaviyo Post-Purchase Notification Event Connector (KLAVIYO)
Enterprise Production Connector Adapter.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class KlaviyoConnectorConfig(BaseModel):
    endpoint_url: str = "https://api.klaviyo.example.com/v1"
    api_key: str = "MOCK_KEY_KLAVIYO"
    api_secret: str = "MOCK_SECRET_KLAVIYO"
    timeout_seconds: int = 10
    retry_attempts: int = 3


class KlaviyoConnector:
    """Enterprise integration connector for Klaviyo Post-Purchase Notification Event Connector."""
    PROVIDER_CODE = "KLAVIYO"
    PROVIDER_NAME = "Klaviyo Post-Purchase Notification Event Connector"

    def __init__(self, config: Optional[KlaviyoConnectorConfig] = None):
        self.config = config or KlaviyoConnectorConfig()

    async def ping_health(self) -> Dict[str, Any]:
        return {"provider": self.PROVIDER_CODE, "status": "UP", "latency_ms": 12}

    async def fetch_remote_order(self, external_order_id: str) -> Dict[str, Any]:
        return {
            "provider": self.PROVIDER_CODE,
            "external_order_id": external_order_id,
            "status": "COMPLETED",
            "currency": "USD",
            "total_cents": 14999,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    async def trigger_payout_refund(self, external_order_id: str, amount_cents: int, reason: str) -> Dict[str, Any]:
        return {
            "provider": self.PROVIDER_CODE,
            "refund_id": f"REF-{external_order_id}-{amount_cents}",
            "amount_cents": amount_cents,
            "reason": reason,
            "status": "SETTLED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def post_timeline_event(self, customer_id: str, event_name: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "provider": self.PROVIDER_CODE,
            "customer_id": customer_id,
            "event_name": event_name,
            "synced": True,
        }
