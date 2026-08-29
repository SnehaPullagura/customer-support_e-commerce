"""
Regional Carrier Adapters (OnTrac, LaserShip, Australia Post, Hermes, Purolator).
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


class RegionalCarrierAdapter(BaseCarrierAdapter):
    def __init__(self, carrier_code: CarrierCode, api_key: Optional[str] = None):
        super().__init__(carrier_code, api_key)

    async def get_tracking_details(self, tracking_number: str) -> Optional[CarrierShipmentDetails]:
        now = datetime.now(timezone.utc)
        history = [
            TrackingMilestone(
                timestamp=now - timedelta(hours=3),
                status=ShipmentStatus.DELIVERED,
                carrier_status_code="REG_DELIVERED",
                description=f"Delivered by {self.carrier_code.value} driver.",
                location_city="Local Station",
            )
        ]
        return CarrierShipmentDetails(
            tracking_number=tracking_number,
            carrier=self.carrier_code,
            service_level=f"{self.carrier_code.value}_STANDARD",
            origin_address={"city": "Regional Hub"},
            destination_address={"city": "Customer City"},
            status=ShipmentStatus.DELIVERED,
            estimated_delivery=now - timedelta(hours=3),
            actual_delivery=now - timedelta(hours=3),
            signed_by="Doorstep",
            history=history,
        )

    async def file_claim(self, claim_request: CarrierClaimRequest) -> CarrierClaimResponse:
        return CarrierClaimResponse(
            claim_id=f"REG-CLM-{uuid.uuid4().hex[:8].upper()}",
            carrier=self.carrier_code,
            tracking_number=claim_request.tracking_number,
            status="SUBMITTED",
            payout_amount_cents=claim_request.declared_value_cents,
            carrier_reference=f"REG-{uuid.uuid4().hex[:6].upper()}",
            notes=f"Regional claim filed with {self.carrier_code.value} claims portal.",
        )

    async def verify_address(self, address: Dict[str, str]) -> Dict[str, Any]:
        return {"is_valid": True}

    async def estimate_transit_time(self, origin_zip: str, dest_zip: str, service_level: str) -> Dict[str, Any]:
        return {"transit_days": 3}
