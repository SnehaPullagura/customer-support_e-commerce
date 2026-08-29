"""
Automated Carrier Claims Filing, Evidence Packaging, and Deadlines Engine.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from app.adapters.carriers.base import (
    BaseCarrierAdapter,
    CarrierCode,
    CarrierClaimRequest,
    CarrierClaimResponse,
    CarrierClaimType,
)
from app.adapters.carriers.fedex import FedExAdapter
from app.adapters.carriers.ups import UPSAdapter
from app.adapters.carriers.dhl import DHLAdapter
from app.adapters.carriers.usps import USPSAdapter
from app.adapters.carriers.royal_mail import RoyalMailAdapter
from app.adapters.carriers.regional import RegionalCarrierAdapter


# Carrier filing deadline constraints (days from delivery or expected delivery date)
CARRIER_CLAIM_DEADLINES_DAYS: Dict[CarrierCode, Dict[CarrierClaimType, int]] = {
    CarrierCode.FEDEX: {
        CarrierClaimType.DAMAGED_PACKAGE: 21,
        CarrierClaimType.LOST_PACKAGE: 60,
        CarrierClaimType.LATE_DELIVERY_REFUND: 15,
        CarrierClaimType.MISSING_CONTENTS: 21,
    },
    CarrierCode.UPS: {
        CarrierClaimType.DAMAGED_PACKAGE: 60,
        CarrierClaimType.LOST_PACKAGE: 120,
        CarrierClaimType.LATE_DELIVERY_REFUND: 15,
        CarrierClaimType.MISSING_CONTENTS: 60,
    },
    CarrierCode.USPS: {
        CarrierClaimType.DAMAGED_PACKAGE: 60,
        CarrierClaimType.LOST_PACKAGE: 60,
        CarrierClaimType.LATE_DELIVERY_REFUND: 30,
        CarrierClaimType.MISSING_CONTENTS: 60,
    },
    CarrierCode.DHL: {
        CarrierClaimType.DAMAGED_PACKAGE: 14,
        CarrierClaimType.LOST_PACKAGE: 30,
        CarrierClaimType.LATE_DELIVERY_REFUND: 14,
        CarrierClaimType.MISSING_CONTENTS: 14,
    },
}


class CarrierClaimsEngine:
    @staticmethod
    def get_adapter(carrier_code: CarrierCode) -> BaseCarrierAdapter:
        if carrier_code == CarrierCode.FEDEX:
            return FedExAdapter()
        elif carrier_code == CarrierCode.UPS:
            return UPSAdapter()
        elif carrier_code == CarrierCode.DHL:
            return DHLAdapter()
        elif carrier_code == CarrierCode.USPS:
            return USPSAdapter()
        elif carrier_code == CarrierCode.ROYAL_MAIL:
            return RoyalMailAdapter()
        else:
            return RegionalCarrierAdapter(carrier_code)

    @staticmethod
    def calculate_filing_deadline(
        carrier_code: CarrierCode, claim_type: CarrierClaimType, event_date: datetime
    ) -> datetime:
        carrier_rules = CARRIER_CLAIM_DEADLINES_DAYS.get(carrier_code, {})
        allowed_days = carrier_rules.get(claim_type, 30)
        return event_date + timedelta(days=allowed_days)

    @staticmethod
    def validate_claim_eligibility(
        carrier_code: CarrierCode,
        claim_type: CarrierClaimType,
        event_date: datetime,
        declared_value_cents: int,
    ) -> Tuple[bool, str]:
        deadline = CarrierClaimsEngine.calculate_filing_deadline(carrier_code, claim_type, event_date)
        now = datetime.now(timezone.utc)
        if event_date.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)

        if now > deadline:
            return False, f"Claim deadline expired on {deadline.strftime('%Y-%m-%d')} for carrier {carrier_code.value}."

        if declared_value_cents <= 0:
            return False, "Claim declared value must be greater than zero."

        return True, "Claim is eligible for submission."

    @staticmethod
    async def file_automated_carrier_claim(claim_request: CarrierClaimRequest) -> CarrierClaimResponse:
        adapter = CarrierClaimsEngine.get_adapter(claim_request.carrier)
        return await adapter.file_claim(claim_request)
