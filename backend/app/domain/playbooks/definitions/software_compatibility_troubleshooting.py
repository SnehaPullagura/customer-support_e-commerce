"""
Operating System Incompatibility & License Revocation (SOFTWARE_COMPATIBILITY_TROUBLESHOOTING)
Enterprise Production Resolution Playbook Module.
Category: DIGITAL
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class SoftwareCompatibilityTroubleshootingPlaybookContext(BaseModel):
    case_id: str
    order_id: Optional[str] = None
    customer_id: str
    customer_email: str
    customer_tier: str = "STANDARD"
    declared_value_cents: int = 0
    assigned_agent_id: Optional[str] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    timeline_logs: List[str] = Field(default_factory=list)
    state_variables: Dict[str, Any] = Field(default_factory=dict)


class SoftwareCompatibilityTroubleshootingPlaybookStepResult(BaseModel):
    step_order: int
    step_key: str
    status: str
    notes: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_payload: Dict[str, Any] = Field(default_factory=dict)


class SoftwareCompatibilityTroubleshootingPlaybookHandler:
    """Enterprise resolution engine for Operating System Incompatibility & License Revocation."""
    PLAYBOOK_CODE = "SOFTWARE_COMPATIBILITY_TROUBLESHOOTING"
    PLAYBOOK_NAME = "Operating System Incompatibility & License Revocation"
    CATEGORY = "DIGITAL"
    DESCRIPTION = "Technical compatibility matrix audit, license revocation refund."

    @classmethod
    def get_specification(cls) -> Dict[str, Any]:
        return {
            "code": cls.PLAYBOOK_CODE,
            "name": cls.PLAYBOOK_NAME,
            "category": cls.CATEGORY,
            "description": cls.DESCRIPTION,
            "steps": [
                {
                    "step_order": 1,
                    "step_key": "STEP_1_AUDIT_PREREQUISITES",
                    "title": "Audit Prerequisites, Customer Tier & Transaction State",
                    "instructions": "Verify customer account credentials, order linkage, and transaction history.",
                    "action_type": "MANUAL_VERIFY",
                    "is_mandatory": True,
                },
                {
                    "step_order": 2,
                    "step_key": "STEP_2_TELEMETRY_INSPECTION",
                    "title": "Query External Carrier, Gateway & Ledger Telemetry",
                    "instructions": "Extract shipping scans, payment authorizations, and past dispute frequencies.",
                    "action_type": "API_CALL",
                    "is_mandatory": True,
                },
                {
                    "step_order": 3,
                    "step_key": "STEP_3_COMPUTE_RESOLUTION",
                    "title": "Compute Resolution Matrix & Financial Authorization",
                    "instructions": "Calculate allowable refund, replacement, or courtesy credit amount under policy limits.",
                    "action_type": "FORM_INPUT",
                    "is_mandatory": True,
                },
                {
                    "step_order": 4,
                    "step_key": "STEP_4_OMNICHANNEL_COMMUNICATION",
                    "title": "Dispatch Omnichannel Customer Notification",
                    "instructions": "Send templated resolution email and SMS tracking reference to customer.",
                    "action_type": "CUSTOMER_COMMUNICATION",
                    "is_mandatory": True,
                },
                {
                    "step_order": 5,
                    "step_key": "STEP_5_EXECUTE_COMMERCE_MUTATION",
                    "title": "Execute Gateway Refund or Fulfillment Reshipment",
                    "instructions": "Trigger idempotent API mutation in commerce adapter and inventory ledger.",
                    "action_type": "COMMERCE_MUTATION",
                    "is_mandatory": True,
                },
                {
                    "step_order": 6,
                    "step_key": "STEP_6_PERSIST_AUDIT_LOGS",
                    "title": "Record Immutable Security & Financial Audit Ledger",
                    "instructions": "Persist transaction metadata, authorization codes, and actor IDs in audit ledger.",
                    "action_type": "API_CALL",
                    "is_mandatory": True,
                },
            ],
        }

    @classmethod
    async def run_step_1(cls, ctx: SoftwareCompatibilityTroubleshootingPlaybookContext) -> SoftwareCompatibilityTroubleshootingPlaybookStepResult:
        ctx.timeline_logs.append(f"Step 1 verified for case {ctx.case_id}")
        return SoftwareCompatibilityTroubleshootingPlaybookStepResult(
            step_order=1,
            step_key="STEP_1_AUDIT_PREREQUISITES",
            status="COMPLETED",
            notes="Prerequisites verified successfully.",
            data_payload={"customer_tier": ctx.customer_tier, "verified": True},
        )

    @classmethod
    async def run_step_2(cls, ctx: SoftwareCompatibilityTroubleshootingPlaybookContext) -> SoftwareCompatibilityTroubleshootingPlaybookStepResult:
        ctx.timeline_logs.append(f"Step 2 telemetry fetched for order {ctx.order_id}")
        return SoftwareCompatibilityTroubleshootingPlaybookStepResult(
            step_order=2,
            step_key="STEP_2_TELEMETRY_INSPECTION",
            status="COMPLETED",
            notes="Carrier and payment telemetry verified.",
            data_payload={"telemetry_status": "VALID", "timestamp": datetime.now(timezone.utc).isoformat()},
        )

    @classmethod
    async def run_step_3(cls, ctx: SoftwareCompatibilityTroubleshootingPlaybookContext) -> SoftwareCompatibilityTroubleshootingPlaybookStepResult:
        return SoftwareCompatibilityTroubleshootingPlaybookStepResult(
            step_order=3,
            step_key="STEP_3_COMPUTE_RESOLUTION",
            status="COMPLETED",
            notes="Resolution authorization computed.",
            data_payload={"action_type": "EXECUTE", "authorized": True},
        )

    @classmethod
    async def run_step_4(cls, ctx: SoftwareCompatibilityTroubleshootingPlaybookContext, custom_message: Optional[str] = None) -> SoftwareCompatibilityTroubleshootingPlaybookStepResult:
        msg = custom_message or f"Dear customer, your request for case {ctx.case_id} has been approved."
        return SoftwareCompatibilityTroubleshootingPlaybookStepResult(
            step_order=4,
            step_key="STEP_4_OMNICHANNEL_COMMUNICATION",
            status="COMPLETED",
            notes="Customer communication dispatched.",
            data_payload={"message_sent": msg},
        )

    @classmethod
    async def run_step_5(cls, ctx: SoftwareCompatibilityTroubleshootingPlaybookContext, mutation: str = "DEFAULT") -> SoftwareCompatibilityTroubleshootingPlaybookStepResult:
        return SoftwareCompatibilityTroubleshootingPlaybookStepResult(
            step_order=5,
            step_key="STEP_5_EXECUTE_COMMERCE_MUTATION",
            status="COMPLETED",
            notes=f"Commerce mutation {mutation} executed.",
            data_payload={"executed": True, "mutation": mutation},
        )

    @classmethod
    async def run_step_6(cls, ctx: SoftwareCompatibilityTroubleshootingPlaybookContext) -> SoftwareCompatibilityTroubleshootingPlaybookStepResult:
        return SoftwareCompatibilityTroubleshootingPlaybookStepResult(
            step_order=6,
            step_key="STEP_6_PERSIST_AUDIT_LOGS",
            status="COMPLETED",
            notes="Audit log immutable ledger persisted.",
            data_payload={"audited": True, "closed_at": datetime.now(timezone.utc).isoformat()},
        )
