"""
Carrier Adapter Registry.
"""

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
from app.adapters.carriers.fedex import FedExAdapter
from app.adapters.carriers.ups import UPSAdapter
from app.adapters.carriers.dhl import DHLAdapter
from app.adapters.carriers.usps import USPSAdapter
from app.adapters.carriers.royal_mail import RoyalMailAdapter
from app.adapters.carriers.regional import RegionalCarrierAdapter
from app.adapters.carriers.postal_zones import DimensionalWeightCalculator, ZoneRouter
from app.adapters.carriers.claims_engine import CarrierClaimsEngine

__all__ = [
    "BaseCarrierAdapter",
    "CarrierCode",
    "CarrierShipmentDetails",
    "CarrierClaimRequest",
    "CarrierClaimResponse",
    "CarrierClaimType",
    "ShipmentStatus",
    "TrackingMilestone",
    "FedExAdapter",
    "UPSAdapter",
    "DHLAdapter",
    "USPSAdapter",
    "RoyalMailAdapter",
    "RegionalCarrierAdapter",
    "DimensionalWeightCalculator",
    "ZoneRouter",
    "CarrierClaimsEngine",
]
