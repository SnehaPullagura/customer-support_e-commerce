"""
FedEx Carrier Connector Adapter with Exception Taxonomy, Milestone Parser, and Claims Engine.
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


FEDEX_EXCEPTION_CODES = {
    "SE001": {"severity": "HIGH", "category": "WEATHER", "description": "Severe weather conditions delaying transportation"},
    "SE002": {"severity": "HIGH", "category": "MECHANICAL", "description": "Mechanical delay with linehaul aircraft/truck"},
    "SE003": {"severity": "CRITICAL", "category": "DAMAGE", "description": "Package damaged in sorting facility; barcode unreadable"},
    "SE004": {"severity": "MEDIUM", "category": "SECURITY", "description": "Delivery address inaccessible or gated without security code"},
    "SE005": {"severity": "MEDIUM", "category": "RECIPIENT", "description": "Recipient not home for adult direct signature"},
    "SE006": {"severity": "LOW", "category": "HOLIDAY", "description": "Local holiday closure; delivery rescheduled"},
    "SE007": {"severity": "CRITICAL", "category": "LOST", "description": "Package missing from container manifest at destination station"},
    "SE008": {"severity": "MEDIUM", "category": "ADDRESS", "description": "Incorrect apartment/suite number; address correction attempted"},
}


class FedExAdapter(BaseCarrierAdapter):
    def __init__(self, api_key: Optional[str] = None, account_id: Optional[str] = None):
        super().__init__(CarrierCode.FEDEX, api_key, account_id)

    async def get_tracking_details(self, tracking_number: str) -> Optional[CarrierShipmentDetails]:
        now = datetime.now(timezone.utc)
        
        # Deterministic simulation based on tracking suffix
        is_delayed = tracking_number.endswith("9")
        is_damaged = tracking_number.endswith("8")
        is_delivered = not (is_delayed or is_damaged)

        history: List[TrackingMilestone] = [
            TrackingMilestone(
                timestamp=now - timedelta(days=3),
                status=ShipmentStatus.LABEL_CREATED,
                carrier_status_code="OC",
                description="Shipment information sent to FedEx",
                location_city="Memphis",
                location_state="TN",
                location_postal_code="38118",
            ),
            TrackingMilestone(
                timestamp=now - timedelta(days=2, hours=18),
                status=ShipmentStatus.PICKED_UP,
                carrier_status_code="PU",
                description="Picked up by FedEx courier",
                location_city="Memphis",
                location_state="TN",
                location_postal_code="38118",
            ),
            TrackingMilestone(
                timestamp=now - timedelta(days=1, hours=8),
                status=ShipmentStatus.IN_TRANSIT,
                carrier_status_code="IT",
                description="Arrived at FedEx hub station",
                location_city="Austin",
                location_state="TX",
                location_postal_code="78744",
            ),
        ]

        if is_delivered:
            history.append(
                TrackingMilestone(
                    timestamp=now - timedelta(hours=4),
                    status=ShipmentStatus.OUT_FOR_DELIVERY,
                    carrier_status_code="OD",
                    description="On FedEx vehicle for delivery",
                    location_city="Austin",
                    location_state="TX",
                    location_postal_code="78701",
                )
            )
            history.append(
                TrackingMilestone(
                    timestamp=now - timedelta(hours=1),
                    status=ShipmentStatus.DELIVERED,
                    carrier_status_code="DL",
                    description="Delivered: Left at front door / porch. Signature not required.",
                    location_city="Austin",
                    location_state="TX",
                    location_postal_code="78701",
                )
            )
            status = ShipmentStatus.DELIVERED
            actual_delivery = now - timedelta(hours=1)
            signed_by = "Front Door"
        elif is_damaged:
            history.append(
                TrackingMilestone(
                    timestamp=now - timedelta(hours=3),
                    status=ShipmentStatus.DAMAGE_REPORTED,
                    carrier_status_code="SE003",
                    description="Damaged parcel inspected at station. Repackaging required.",
                    location_city="Austin",
                    location_state="TX",
                    location_postal_code="78744",
                )
            )
            status = ShipmentStatus.DAMAGE_REPORTED
            actual_delivery = None
            signed_by = None
        else:
            history.append(
                TrackingMilestone(
                    timestamp=now - timedelta(hours=2),
                    status=ShipmentStatus.EXCEPTION,
                    carrier_status_code="SE001",
                    description="Weather delay at local sort facility. Delivery pending next business cycle.",
                    location_city="Austin",
                    location_state="TX",
                    location_postal_code="78744",
                )
            )
            status = ShipmentStatus.EXCEPTION
            actual_delivery = None
            signed_by = None

        return CarrierShipmentDetails(
            tracking_number=tracking_number,
            carrier=CarrierCode.FEDEX,
            service_level="FEDEX_HOME_DELIVERY",
            origin_address={
                "street": "2400 Fulfillment Way",
                "city": "Memphis",
                "state": "TN",
                "zip": "38118",
                "country": "US",
            },
            destination_address={
                "street": "742 Evergreen Terrace",
                "city": "Austin",
                "state": "TX",
                "zip": "78701",
                "country": "US",
            },
            weight_lbs=3.4,
            status=status,
            estimated_delivery=now + timedelta(hours=6) if not is_delivered else now - timedelta(hours=1),
            actual_delivery=actual_delivery,
            signed_by=signed_by,
            proof_of_delivery_url=f"https://images.fedex.com/pod/demo/{tracking_number}.pdf",
            is_delayed=is_delayed,
            delay_reason=FEDEX_EXCEPTION_CODES["SE001"]["description"] if is_delayed else None,
            history=history,
        )

    async def file_claim(self, claim_request: CarrierClaimRequest) -> CarrierClaimResponse:
        claim_id = f"FDX-CLM-{uuid.uuid4().hex[:8].upper()}"
        ref = f"REF-{uuid.uuid4().hex[:6].upper()}"

        # Automatic payout calculation: up to $100 covered standard, declared value otherwise
        payout = min(claim_request.declared_value_cents, 10000) if claim_request.declared_value_cents <= 10000 else claim_request.declared_value_cents

        return CarrierClaimResponse(
            claim_id=claim_id,
            carrier=CarrierCode.FEDEX,
            tracking_number=claim_request.tracking_number,
            status="SUBMITTED_UNDER_REVIEW",
            payout_amount_cents=payout,
            estimated_resolution_days=5,
            carrier_reference=ref,
            notes="FedEx claims team has acknowledged receipt of invoice and packaging photos.",
        )

    async def verify_address(self, address: Dict[str, str]) -> Dict[str, Any]:
        return {
            "is_valid": True,
            "classification": "RESIDENTIAL",
            "standardized_address": {
                "street_line_1": address.get("street", "").upper(),
                "city": address.get("city", "").upper(),
                "state": address.get("state", "").upper(),
                "postal_code": address.get("zip", "").strip()[:5] + "-0001",
                "country": "US",
            },
            "carrier_route": "C004",
            "dpv_match_code": "Y",
        }

    async def estimate_transit_time(
        self, origin_zip: str, dest_zip: str, service_level: str
    ) -> Dict[str, Any]:
        days = 2 if "EXPRESS" in service_level.upper() else 4
        return {
            "origin_zip": origin_zip,
            "dest_zip": dest_zip,
            "service_level": service_level,
            "transit_days": days,
            "guaranteed_delivery": "EXPRESS" in service_level.upper(),
        }
