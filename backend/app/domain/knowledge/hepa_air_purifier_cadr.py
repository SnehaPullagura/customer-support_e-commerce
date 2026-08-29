"""
Clean Air Delivery Rate (CADR) Laser PM2.5 Sensor Recalibration Guide (KB_CADR_SENSOR)
Interactive Knowledge Base Technical Resolution Guide & Diagnostic Procedures.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HepaAirPurifierCadrArticle(BaseModel):
    article_id: str = "KB_CADR_SENSOR"
    title: str = "Clean Air Delivery Rate (CADR) Laser PM2.5 Sensor Recalibration Guide"
    category: str = "HARDWARE_DIAGNOSTICS"
    estimated_read_time_mins: int = 6
    summary: str = "Step-by-step diagnostic guide for resolution engineers and customer support agents."
    diagnostic_symptoms: List[str] = Field(default_factory=list)
    troubleshooting_steps: List[Dict[str, Any]] = Field(default_factory=list)
    deflection_rate_percentage: float = 42.5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HepaAirPurifierCadr:
    """Knowledge article provider for Clean Air Delivery Rate (CADR) Laser PM2.5 Sensor Recalibration Guide."""
    ARTICLE_CODE = "KB_CADR_SENSOR"
    ARTICLE_TITLE = "Clean Air Delivery Rate (CADR) Laser PM2.5 Sensor Recalibration Guide"

    @classmethod
    def get_article_content(cls) -> HepaAirPurifierCadrArticle:
        return HepaAirPurifierCadrArticle(
            diagnostic_symptoms=[
                "Device fails diagnostic loopback verification test.",
                "Intermittent sensor readouts or communication timeouts.",
                "Subsystem reports degraded operational state code.",
            ],
            troubleshooting_steps=[
                {
                    "step_order": 1,
                    "name": "Visual & Physical Inspection",
                    "instruction": "Inspect hardware ports, solder traces, and physical chassis for damage or liquid ingress.",
                    "verification": "Ensure zero oxidation or mechanical deformation on test points.",
                },
                {
                    "step_order": 2,
                    "name": "Diagnostic Self-Test & Telemetry Readout",
                    "instruction": "Initiate hardware diagnostics routine using standard service tool protocol.",
                    "verification": "Collect register dump and verify all values match factory specifications.",
                },
                {
                    "step_order": 3,
                    "name": "Firmware Reflash & Parameter Calibration",
                    "instruction": "Reflash latest signed production firmware image and calibrate zero-point offsets.",
                    "verification": "Confirm successful non-volatile EEPROM parameter write and verify checksum.",
                },
                {
                    "step_order": 4,
                    "name": "Functional Certification Loop",
                    "instruction": "Execute full 15-minute thermal and operational burn-in test cycle.",
                    "verification": "Verify all telemetry streams report nominal operating temperatures and voltages.",
                },
            ],
        )
