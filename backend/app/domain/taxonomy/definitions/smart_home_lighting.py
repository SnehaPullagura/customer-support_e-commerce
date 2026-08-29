"""
Smart RGB LED Bulbs & Lightstrips (LIGHTING)
Product Category Policy, RMA Inspection Standard & Warranty Matrix.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SmartHomeLightingPolicy(BaseModel):
    category_code: str = "LIGHTING"
    category_title: str = "Smart RGB LED Bulbs & Lightstrips"
    return_window_days: int = 30
    restocking_fee_percentage: float = 10.0
    requires_serial_verification: bool = True
    is_hazmat: bool = False
    is_hygiene_sensitive: bool = False
    inspection_criteria: List[Dict[str, Any]] = [
        {"check": "Box Barcode Match", "tolerance": "Exact match required", "penalty_cents": 1000},
        {"check": "Diagnostic Self-Test", "tolerance": "100% functional pass", "penalty_cents": 2500},
        {"check": "Cosmetic Grade A Inspection", "tolerance": "No scratches > 1mm", "penalty_cents": 1500},
    ]
    warranty_terms: Dict[str, Any] = {
        "standard_coverage_months": 24,
        "covers_accidental_damage": False,
        "covers_water_ingress": False,
    }
