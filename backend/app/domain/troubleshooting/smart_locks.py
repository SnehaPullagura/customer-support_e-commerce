"""
Biometric Smart Door Locks & Keypad Diagnostics
Interactive Diagnostic Decision Trees, Self-Service Deflections, and Reset Procedures.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DiagnosticNode(BaseModel):
    node_id: str
    question_prompt: str
    diagnostic_tip: Optional[str] = None
    options: List[Dict[str, Any]] = Field(default_factory=list)
    is_terminal: bool = False
    resolution_action: Optional[str] = None


class SmartLocksDiagnostics:
    CATEGORY_KEY = "smart_locks"
    CATEGORY_TITLE = "Biometric Smart Door Locks & Keypad Diagnostics"

    @classmethod
    def get_diagnostic_tree(cls) -> Dict[str, DiagnosticNode]:
        return {
            "START": DiagnosticNode(
                node_id="START",
                question_prompt="What specific symptom is your biometric smart door locks & keypad diagnostics exhibiting?",
                diagnostic_tip="Please ensure the unit has been plugged into a verified wall outlet for at least 15 minutes.",
                options=[
                    {"label": "Unit does not power on or charges intermittently", "next_node": "POWER_CHECK"},
                    {"label": "Device powers on but software/firmware is frozen", "next_node": "FIRMWARE_RESET"},
                    {"label": "Physical or cosmetic damage upon unboxing", "next_node": "PHYSICAL_DAMAGE"},
                    {"label": "Wireless connectivity / pairing dropouts", "next_node": "CONNECTIVITY_CHECK"},
                ],
            ),
            "POWER_CHECK": DiagnosticNode(
                node_id="POWER_CHECK",
                question_prompt="Have you attempted a hard battery reset by holding the power button for 15 seconds?",
                diagnostic_tip="Inspect the charging cable and port for lint or bent pins.",
                options=[
                    {"label": "Yes, hard reset performed - still completely unresponsive", "next_node": "REPLACE_AUTHORIZED"},
                    {"label": "No, let me try the hard reset procedure now", "next_node": "DEFLECT_SUCCESS"},
                ],
            ),
            "FIRMWARE_RESET": DiagnosticNode(
                node_id="FIRMWARE_RESET",
                question_prompt="Would you like step-by-step instructions to flash recovery firmware?",
                options=[
                    {"label": "Yes, show me the recovery tool guide", "next_node": "DEFLECT_SUCCESS"},
                    {"label": "Firmware update failed with error code", "next_node": "RMA_AUTHORIZED"},
                ],
            ),
            "PHYSICAL_DAMAGE": DiagnosticNode(
                node_id="PHYSICAL_DAMAGE",
                question_prompt="All physical damages within 30 days are covered under zero-cost replacement.",
                is_terminal=True,
                resolution_action="TRIGGER_ZERO_COST_REPLACEMENT",
            ),
            "CONNECTIVITY_CHECK": DiagnosticNode(
                node_id="CONNECTIVITY_CHECK",
                question_prompt="Please forget the device from Bluetooth/Wi-Fi settings and cycle power.",
                options=[
                    {"label": "That fixed the issue! Pairing successful.", "next_node": "DEFLECT_SUCCESS"},
                    {"label": "Still fails to discover device", "next_node": "REPLACE_AUTHORIZED"},
                ],
            ),
            "DEFLECT_SUCCESS": DiagnosticNode(
                node_id="DEFLECT_SUCCESS",
                question_prompt="Issue successfully resolved through self-service diagnostics.",
                is_terminal=True,
                resolution_action="RESOLVE_DEFLECTED",
            ),
            "REPLACE_AUTHORIZED": DiagnosticNode(
                node_id="REPLACE_AUTHORIZED",
                question_prompt="Hardware fault confirmed. Standard 30-day replacement authorized.",
                is_terminal=True,
                resolution_action="AUTHORIZE_REPLACEMENT",
            ),
            "RMA_AUTHORIZED": DiagnosticNode(
                node_id="RMA_AUTHORIZED",
                question_prompt="Firmware corrupted. Return authorization and replacement initiated.",
                is_terminal=True,
                resolution_action="AUTHORIZE_RMA",
            ),
        }

    @classmethod
    def evaluate_node(cls, current_node_id: str, choice_index: int) -> Optional[DiagnosticNode]:
        tree = cls.get_diagnostic_tree()
        node = tree.get(current_node_id)
        if not node or choice_index >= len(node.options):
            return None
        next_id = node.options[choice_index].get("next_node")
        return tree.get(next_id)
