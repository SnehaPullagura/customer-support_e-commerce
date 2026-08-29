"""
UPS Carrier Connector Adapter with Quantum View milestones, signature capture, and claims.
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
    CarrierClaimType,
    ShipmentStatus,
    TrackingMilestone,
)

UPS_STATUS_CODES = {
    "M": "Manifest pickup notice received",
    "P": "Pickup completed at origin",
    "I": "In transit through UPS hub network",
    "O": "Out for delivery by driver",
    "D": "Delivered successfully",
    "X": "Exception encounter (Weather, Damaged, or Address error)",
    "RS": "Returned to shipper",
}


class UPSAdapter(BaseCarrierAdapter):
    def __init__(self, api_key: Optional[str] = None, account_id: Optional[str] = None):
        super().__init__(CarrierCode.UPS, api_key, account_id)

    async def get_tracking_details(self, tracking_number: str) -> Optional[CarrierShipmentDetails]:
        now = datetime.now(timezone.utc)
        history = [
            TrackingMilestone(
                timestamp=now - timedelta(days=2),
                status=ShipmentStatus.LABEL_CREATED,
                carrier_status_code="M",
                description="Shipper created a label, UPS has not received the package yet.",
                location_city="Louisville",
                location_state="KY",
            ),
            TrackingMilestone(
                timestamp=now - timedelta(days=1, hours=12),
                status=ShipmentStatus.PICKED_UP,
                carrier_status_code="P",
                description="Origin scan at UPS Worldport facility.",
                location_city="Louisville",
                location_state="KY",
            ),
            TrackingMilestone(
                timestamp=now - timedelta(hours=6),
                status=ShipmentStatus.OUT_FOR_DELIVERY,
                carrier_status_code="O",
                description="Out For Delivery Today.",
                location_city="Seattle",
                location_state="WA",
            ),
            TrackingMilestone(
                timestamp=now - timedelta(hours=1),
                status=ShipmentStatus.DELIVERED,
                carrier_status_code="D",
                description="Delivered to front door. Signature on file.",
                location_city="Seattle",
                location_state="WA",
            ),
        ]

        return CarrierShipmentDetails(
            tracking_number=tracking_number,
            carrier=CarrierCode.UPS,
            service_level="UPS_GROUND",
            origin_address={"street": "100 Worldport Dr", "city": "Louisville", "state": "KY", "zip": "40221"},
            destination_address={"street": "400 Pine St", "city": "Seattle", "state": "WA", "zip": "98101"},
            status=ShipmentStatus.DELIVERED,
            estimated_delivery=now - timedelta(hours=1),
            actual_delivery=now - timedelta(hours=1),
            signed_by="MCKENZIE",
            history=history,
        )

    async def file_claim(self, claim_request: CarrierClaimRequest) -> CarrierClaimResponse:
        claim_id = f"UPS-CLM-{uuid.uuid4().hex[:8].upper()}"
        return CarrierClaimResponse(
            claim_id=claim_id,
            carrier=CarrierCode.UPS,
            tracking_number=claim_request.tracking_number,
            status="INVESTIGATION_OPENED",
            payout_amount_cents=claim_request.declared_value_cents,
            estimated_resolution_days=8,
            carrier_reference=f"UPS-{uuid.uuid4().hex[:6].upper()}",
            notes="UPS driver follow-up dispatched to delivery route supervisor.",
        )

    async def verify_address(self, address: Dict[str, str]) -> Dict[str, Any]:
        return {"is_valid": True, "classification": "COMMERCIAL", "standardized_address": address}

    async def estimate_transit_time(
        self, origin_zip: str, dest_zip: str, service_level: str
    ) -> Dict[str, Any]:
        return {"transit_days": 3, "guaranteed": True}
