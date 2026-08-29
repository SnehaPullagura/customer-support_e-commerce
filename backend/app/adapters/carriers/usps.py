"""
USPS & Royal Mail Carrier Adapters with Missing Mail Search and Safeplace verification.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.adapters.carriers.base import (
    BaseCarrierAdapter,
    CarrierCode,
    CarrierShipmentDetails,
    CarrierClaimRequest,
    CarrierClaimResponse,
    ShipmentStatus,
    TrackingMilestone,
)


class USPSAdapter(BaseCarrierAdapter):
    def __init__(self, api_key: Optional[str] = None, account_id: Optional[str] = None):
        super().__init__(CarrierCode.USPS, api_key, account_id)

    async def get_tracking_details(self, tracking_number: str) -> Optional[CarrierShipmentDetails]:
        now = datetime.now(timezone.utc)
        history = [
            TrackingMilestone(
                timestamp=now - timedelta(days=2),
                status=ShipmentStatus.ACCEPTED if hasattr(ShipmentStatus, "ACCEPTED") else ShipmentStatus.PICKED_UP,
                carrier_status_code="USPS_ACCEPT",
                description="Accepted at USPS Origin Sort Facility",
                location_city="Chicago",
                location_state="IL",
            ),
            TrackingMilestone(
                timestamp=now - timedelta(hours=3),
                status=ShipmentStatus.DELIVERED,
                carrier_status_code="USPS_DELIVERED",
                description="Delivered, In/At Mailbox",
                location_city="Denver",
                location_state="CO",
                location_postal_code="80202",
            ),
        ]
        return CarrierShipmentDetails(
            tracking_number=tracking_number,
            carrier=CarrierCode.USPS,
            service_level="USPS_PRIORITY_MAIL",
            origin_address={"city": "Chicago", "state": "IL", "zip": "60601"},
            destination_address={"city": "Denver", "state": "CO", "zip": "80202"},
            status=ShipmentStatus.DELIVERED,
            estimated_delivery=now - timedelta(hours=3),
            actual_delivery=now - timedelta(hours=3),
            signed_by="In/At Mailbox",
            history=history,
        )

    async def file_claim(self, claim_request: CarrierClaimRequest) -> CarrierClaimResponse:
        return CarrierClaimResponse(
            claim_id=f"USPS-CLM-{uuid.uuid4().hex[:8].upper()}",
            carrier=CarrierCode.USPS,
            tracking_number=claim_request.tracking_number,
            status="MISSING_MAIL_SEARCH_ACTIVE",
            payout_amount_cents=min(claim_request.declared_value_cents, 10000),
            carrier_reference=f"MRC-{uuid.uuid4().hex[:6].upper()}",
            notes="Missing Mail Search Request submitted to USPS Mail Recovery Center (MRC).",
        )

    async def verify_address(self, address: Dict[str, str]) -> Dict[str, Any]:
        return {"is_valid": True, "usps_carrier_route": "R002"}

    async def estimate_transit_time(self, origin_zip: str, dest_zip: str, service_level: str) -> Dict[str, Any]:
        return {"transit_days": 2}


class RoyalMailAdapter(BaseCarrierAdapter):
    def __init__(self, api_key: Optional[str] = None, account_id: Optional[str] = None):
        super().__init__(CarrierCode.ROYAL_MAIL, api_key, account_id)

    async def get_tracking_details(self, tracking_number: str) -> Optional[CarrierShipmentDetails]:
        now = datetime.now(timezone.utc)
        history = [
            TrackingMilestone(
                timestamp=now - timedelta(hours=2),
                status=ShipmentStatus.DELIVERED,
                carrier_status_code="RM_DELIVERED",
                description="Delivered by Postie to Safeplace: Behind Porch Planter",
                location_city="London",
                location_postal_code="SW1A 1AA",
                location_country="GB",
            )
        ]
        return CarrierShipmentDetails(
            tracking_number=tracking_number,
            carrier=CarrierCode.ROYAL_MAIL,
            service_level="ROYAL_MAIL_TRACKED_24",
            origin_address={"city": "Manchester", "postal_code": "M1 1AE", "country": "GB"},
            destination_address={"city": "London", "postal_code": "SW1A 1AA", "country": "GB"},
            status=ShipmentStatus.DELIVERED,
            estimated_delivery=now - timedelta(hours=2),
            actual_delivery=now - timedelta(hours=2),
            signed_by="Safeplace Photo Captured",
            history=history,
        )

    async def file_claim(self, claim_request: CarrierClaimRequest) -> CarrierClaimResponse:
        return CarrierClaimResponse(
            claim_id=f"RM-CLM-{uuid.uuid4().hex[:8].upper()}",
            carrier=CarrierCode.ROYAL_MAIL,
            tracking_number=claim_request.tracking_number,
            status="SUBMITTED_TO_CUSTOMER_SERVICE",
            payout_amount_cents=claim_request.declared_value_cents,
            carrier_reference=f"P58-{uuid.uuid4().hex[:6].upper()}",
            notes="Royal Mail P58 loss & damage claim reference assigned.",
        )

    async def verify_address(self, address: Dict[str, str]) -> Dict[str, Any]:
        return {"is_valid": True, "paf_verified": True}

    async def estimate_transit_time(self, origin_zip: str, dest_zip: str, service_level: str) -> Dict[str, Any]:
        return {"transit_days": 1}
