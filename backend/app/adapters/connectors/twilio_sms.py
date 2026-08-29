"""
Twilio SMS and WhatsApp Business Omnichannel Connector Gateway.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel


class InboundMessagePayload(BaseModel):
    message_sid: str
    from_phone: str
    to_phone: str
    body: str
    channel: str = "SMS"  # "SMS" or "WHATSAPP"
    media_url: Optional[str] = None


class TwilioOmnichannelConnector:
    def __init__(self, account_sid: str = "AC_MOCK", auth_token: str = "AUTH_MOCK"):
        self.account_sid = account_sid
        self.auth_token = auth_token

    async def send_sms(self, to_phone: str, message: str, from_phone: str = "+18005550199") -> Dict[str, Any]:
        return {
            "sid": f"SM{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "to": to_phone,
            "from": from_phone,
            "body": message,
            "status": "QUEUED",
            "direction": "OUTBOUND_API",
        }

    async def send_whatsapp(self, to_phone: str, message: str, template_name: Optional[str] = None) -> Dict[str, Any]:
        return {
            "sid": f"WA{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "to": f"whatsapp:{to_phone}",
            "from": "whatsapp:+18005550199",
            "body": message,
            "status": "DELIVERED",
        }
