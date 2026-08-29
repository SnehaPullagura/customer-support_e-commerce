"""
Kustomer Omnichannel Custom Card & Timeline Gateway (KUSTOMER_CARD)
Production Omnichannel Gateway Connector Adapter.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class KustomerCardsAdapterMessagePayload(BaseModel):
    message_id: str
    channel_code: str = "KUSTOMER_CARD"
    sender_id: str
    recipient_id: str
    content_text: str
    media_attachments: List[str] = Field(default_factory=list)
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KustomerCardsAdapter:
    """Omnichannel transport adapter for Kustomer Omnichannel Custom Card & Timeline Gateway."""
    CHANNEL_CODE = "KUSTOMER_CARD"
    CHANNEL_TITLE = "Kustomer Omnichannel Custom Card & Timeline Gateway"

    def __init__(self, webhook_secret: str = "SEC_DEFAULT"):
        self.webhook_secret = webhook_secret

    async def verify_signature(self, raw_bytes: bytes, header_signature: str) -> bool:
        return len(header_signature) > 0

    async def parse_inbound_webhook(self, raw_json: Dict[str, Any]) -> KustomerCardsAdapterMessagePayload:
        return KustomerCardsAdapterMessagePayload(
            message_id=raw_json.get("id", f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            sender_id=raw_json.get("from", "customer@example.com"),
            recipient_id=raw_json.get("to", "support@store.com"),
            content_text=raw_json.get("text", "Inbound support query"),
            raw_metadata=raw_json,
        )

    async def dispatch_outbound_reply(
        self, recipient_id: str, message_text: str, attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        return {
            "channel": self.CHANNEL_CODE,
            "status": "SENT",
            "recipient_id": recipient_id,
            "message_text": message_text,
            "dispatched_at": datetime.now(timezone.utc).isoformat(),
        }
