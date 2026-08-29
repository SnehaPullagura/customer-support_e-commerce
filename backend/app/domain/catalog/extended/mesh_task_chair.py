"""
Self-Adjusting Synchronous Tilt Ergonomic Chair Specification (SPEC_CHAIR)
Detailed Component Bill of Materials & Technical Hardware Specs.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MeshTaskChair:
    SPEC_CODE = "SPEC_CHAIR"
    SPEC_TITLE = "Self-Adjusting Synchronous Tilt Ergonomic Chair Specification"

    TECHNICAL_ATTRIBUTES: Dict[str, Any] = {
        "ingress_protection": "IP68 Certified",
        "nominal_operating_voltage_dc": 12.0,
        "maximum_power_draw_watts": 85.0,
        "operating_temperature_celsius": {"min": -10.0, "max": 50.0},
        "mean_time_between_failures_hours": 50000,
        "compliance_certifications": ["FCC Part 15", "CE Mark", "RoHS", "WEEE", "UL Listed"],
    }

    BILL_OF_MATERIALS: List[Dict[str, Any]] = [
        {"component": "Microcontroller Unit (MCU)", "manufacturer": "Silicon Labs", "cost_cents": 1250},
        {"component": "Step-Down Buck Regulator", "manufacturer": "Texas Instruments", "cost_cents": 420},
        {"component": "Lithium Iron Phosphate Cell", "manufacturer": "Panasonic", "cost_cents": 2800},
        {"component": "Die-Cast Aluminum Enclosure", "manufacturer": "Apex Tooling", "cost_cents": 1650},
    ]

    @classmethod
    def get_bom(cls) -> List[Dict[str, Any]]:
        return cls.BILL_OF_MATERIALS
