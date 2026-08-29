"""
Printers & Printhead Nozzle Blockage QC Standard (RMA_PRINT)
Reverse Logistics Quality Control Inspection Protocol & Restocking Standards.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InspectionCheckItem(BaseModel):
    check_id: str
    title: str
    description: str
    is_critical_failure: bool
    acceptable_tolerance: str
    deduction_fee_cents: int = 0


class PrintersTonersQc:
    QC_CODE = "RMA_PRINT"
    QC_TITLE = "Printers & Printhead Nozzle Blockage QC Standard"

    INSPECTION_POINTS: List[InspectionCheckItem] = [
        InspectionCheckItem(
            check_id=f"RMA_PRINT-01",
            title="Packaging Integrity & Original Barcode Labels",
            description="Verify manufacturer retail box is intact with matching serial numbers.",
            is_critical_failure=False,
            acceptable_tolerance="Minor shelf-wear allowed; ripped flaps incur 10% repackaging fee.",
            deduction_fee_cents=1500,
        ),
        InspectionCheckItem(
            check_id=f"RMA_PRINT-02",
            title="Serial Number / IMEI Cloud Lock Audit",
            description="Verify device is completely unlinked from iCloud, Google, or Enterprise MDM.",
            is_critical_failure=True,
            acceptable_tolerance="Zero tolerance. Locked units rejected and returned to customer.",
            deduction_fee_cents=0,
        ),
        InspectionCheckItem(
            check_id=f"RMA_PRINT-03",
            title="Cosmetic Surface & Grade Classification",
            description="Inspect surfaces under 1000 lux illumination for scratches > 2mm.",
            is_critical_failure=False,
            acceptable_tolerance="Grade A: Flawless. Grade B: Minor micro-scratches (< $20 credit).",
            deduction_fee_cents=2000,
        ),
        InspectionCheckItem(
            check_id=f"RMA_PRINT-04",
            title="Complete In-Box Accessories & Manuals Verification",
            description="Confirm power bricks, cables, adapters, and manuals are present.",
            is_critical_failure=False,
            acceptable_tolerance="Missing accessory fee deducted from refund subtotal.",
            deduction_fee_cents=2500,
        ),
        InspectionCheckItem(
            check_id=f"RMA_PRINT-05",
            title="Functional Diagnostic Loopback Pass",
            description="Execute automated automated test jig sequence to certify 100% component health.",
            is_critical_failure=True,
            acceptable_tolerance="Must achieve 100% test pass to be restocked as Certified Open Box.",
            deduction_fee_cents=0,
        ),
    ]

    @classmethod
    def evaluate_inspection(cls, failed_check_ids: List[str]) -> Dict[str, Any]:
        total_deductions = 0
        has_critical_failure = False

        for check in cls.INSPECTION_POINTS:
            if check.check_id in failed_check_ids:
                if check.is_critical_failure:
                    has_critical_failure = True
                total_deductions += check.deduction_fee_cents

        disposition = "REJECT_RETURN_TO_SENDER" if has_critical_failure else "RESTOCK_OPEN_BOX" if total_deductions > 0 else "RESTOCK_NEW"

        return {
            "qc_protocol": cls.QC_CODE,
            "disposition": disposition,
            "total_deduction_cents": total_deductions,
            "restockable": not has_critical_failure,
        }
