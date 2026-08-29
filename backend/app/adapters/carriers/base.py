"""
Abstract Carrier Integration Interface, Unified Shipment Data Contracts, and Exception Taxonomy.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CarrierCode(str, Enum):
    FEDEX = "FEDEX"
    UPS = "UPS"
    DHL = "DHL"
    USPS = "USPS"
    ROYAL_MAIL = "ROYAL_MAIL"
    AUSTRALIA_POST = "AUSTRALIA_POST"
    HERMES = "HERMES"
    ONTRAC = "ONTRAC"
    LASERSHIP = "LASERSHIP"
    PUROLATOR = "PUROLATOR"
    GENERIC = "GENERIC"


class ShipmentStatus(str, Enum):
    LABEL_CREATED = "LABEL_CREATED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    EXCEPTION = "EXCEPTION"
    FAILED_ATTEMPT = "FAILED_ATTEMPT"
    RETURNED_TO_SENDER = "RETURNED_TO_SENDER"
    HELD_AT_CUSTOMS = "HELD_AT_CUSTOMS"
    LOST_IN_TRANSIT = "LOST_IN_TRANSIT"
    DAMAGE_REPORTED = "DAMAGE_REPORTED"


class ExceptionSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TrackingMilestone(BaseModel):
    timestamp: datetime
    status: ShipmentStatus
    carrier_status_code: str
    description: str
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_postal_code: Optional[str] = None
    location_country: str = "US"
    raw_payload: Optional[Dict[str, Any]] = None


class CarrierShipmentDetails(BaseModel):
    tracking_number: str
    carrier: CarrierCode
    service_level: str
    origin_address: Dict[str, str]
    destination_address: Dict[str, str]
    weight_lbs: float = 1.0
    dimensions_inches: Dict[str, float] = Field(default_factory=lambda: {"length": 10.0, "width": 8.0, "height": 4.0})
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    signed_by: Optional[str] = None
    signature_image_url: Optional[str] = None
    proof_of_delivery_url: Optional[str] = None
    status: ShipmentStatus = ShipmentStatus.IN_TRANSIT
    current_location: Optional[str] = None
    is_delayed: bool = False
    delay_reason: Optional[str] = None
    history: List[TrackingMilestone] = Field(default_factory=list)


class CarrierClaimType(str, Enum):
    LOST_PACKAGE = "LOST_PACKAGE"
    DAMAGED_PACKAGE = "DAMAGED_PACKAGE"
    MISSING_CONTENTS = "MISSING_CONTENTS"
    LATE_DELIVERY_REFUND = "LATE_DELIVERY_REFUND"


class CarrierClaimRequest(BaseModel):
    tracking_number: str
    carrier: CarrierCode
    claim_type: CarrierClaimType
    declared_value_cents: int
    item_description: str
    shipper_account_number: str
    contact_email: str
    contact_phone: str
    evidence_urls: List[str] = Field(default_factory=list)
    invoice_number: Optional[str] = None
    order_id: Optional[str] = None


class CarrierClaimResponse(BaseModel):
    claim_id: str
    carrier: CarrierCode
    tracking_number: str
    status: str
    payout_amount_cents: int = 0
    estimated_resolution_days: int = 7
    carrier_reference: str
    filing_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None


class BaseCarrierAdapter(ABC):
    """Abstract interface that all carrier connector adapters must implement."""

    def __init__(self, carrier_code: CarrierCode, api_key: Optional[str] = None, account_id: Optional[str] = None):
        self.carrier_code = carrier_code
        self.api_key = api_key or "MOCK_KEY"
        self.account_id = account_id or "MOCK_ACCT"

    @abstractmethod
    async def get_tracking_details(self, tracking_number: str) -> Optional[CarrierShipmentDetails]:
        """Fetch real-time tracking milestones and delivery proofs."""
        pass

    @abstractmethod
    async def file_claim(self, claim_request: CarrierClaimRequest) -> CarrierClaimResponse:
        """File a formal damage or loss compensation claim."""
        pass

    @abstractmethod
    async def verify_address(self, address: Dict[str, str]) -> Dict[str, Any]:
        """Verify deliverability and normalize address elements."""
        pass

    @abstractmethod
    async def estimate_transit_time(
        self, origin_zip: str, dest_zip: str, service_level: str
    ) -> Dict[str, Any]:
        """Calculate business-day delivery estimate."""
        pass
