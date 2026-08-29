"""
Omnichannel Connectors and Third-Party Integration Suite.
"""

from app.adapters.connectors.shopify import ShopifyConnector, ShopifyWebhookPayload
from app.adapters.connectors.stripe_disputes import StripeDisputeManager, StripeDisputeEvidence
from app.adapters.connectors.twilio_sms import TwilioOmnichannelConnector, InboundMessagePayload
from app.adapters.connectors.zendesk_sync import ZendeskSyncAdapter, ZendeskTicketPayload

__all__ = [
    "ShopifyConnector",
    "ShopifyWebhookPayload",
    "StripeDisputeManager",
    "StripeDisputeEvidence",
    "TwilioOmnichannelConnector",
    "InboundMessagePayload",
    "ZendeskSyncAdapter",
    "ZendeskTicketPayload",
]
