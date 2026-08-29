"""
Antimagnetic Hairspring Demagnetization Procedure
Advanced Hardware Diagnostic Troubleshooting Guide & Step Matrix.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LuxuryWatchMagnetizationGuide:
    GUIDE_KEY = "luxury_watch_magnetization"
    GUIDE_TITLE = "Antimagnetic Hairspring Demagnetization Procedure"

    DIAGNOSTIC_STEPS: List[Dict[str, Any]] = [
        {
            "step_number": 1,
            "action": "Visual & Physical Inspection",
            "instruction": "Inspect device exterior for signs of mechanical impact, water intrusion, or thermal discoloration.",
            "expected_outcome": "No structural cracks or foreign debris in ports.",
        },
        {
            "step_number": 2,
            "action": "Diagnostic Self-Test Execution",
            "instruction": "Trigger onboard hardware self-test routine via factory button combination.",
            "expected_outcome": "Diagnostic LED sequence indicates clean status code.",
        },
        {
            "step_number": 3,
            "action": "Firmware & Calibration Reset",
            "instruction": "Flash latest recovery firmware and perform full zero-point offset calibration.",
            "expected_outcome": "Calibration values successfully stored in non-volatile EEPROM.",
        },
    ]

    @classmethod
    def get_instructions(cls) -> List[Dict[str, Any]]:
        return cls.DIAGNOSTIC_STEPS
