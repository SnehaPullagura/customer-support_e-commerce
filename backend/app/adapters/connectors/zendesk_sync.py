"""
Zendesk & Freshdesk Legacy Ticket Migration and Real-Time Sync Adapter.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ZendeskTicketPayload(BaseModel):
    ticket_id: int
    subject: str
    description: str
    requester_email: str
    status: str
    priority: str
    tags: List[str] = []


class ZendeskSyncAdapter:
    def __init__(self, subdomain: str = "demo-support", api_token: str = "ZD_TOKEN"):
        self.subdomain = subdomain
        self.api_token = api_token

    async def import_ticket(self, zendesk_ticket_id: int) -> Dict[str, Any]:
        return {
            "source_system": "ZENDESK",
            "source_id": str(zendesk_ticket_id),
            "subject": f"Imported Legacy Ticket #{zendesk_ticket_id}",
            "customer_email": "customer.legacy@example.com",
            "status": "RESOLVED",
            "priority": "NORMAL",
            "imported_at": "2026-08-29T10:00:00Z",
        }
