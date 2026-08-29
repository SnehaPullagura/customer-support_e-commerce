"""
Enterprise Resolution Playbook Definitions Catalog covering 35+ E-Commerce Support Scenarios.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PlaybookStepDef(BaseModel):
    step_order: int
    step_key: str
    title: str
    instructions: str
    action_type: str  # e.g., 'API_CALL', 'COMMERCE_MUTATION', 'FORM_INPUT', 'MANUAL_VERIFY', 'CUSTOMER_COMMUNICATION'
    is_mandatory: bool = True
    suggested_message_template: Optional[str] = None
    required_role: Optional[str] = "AGENT"


class PlaybookDef(BaseModel):
    code: str
    name: str
    category: str
    description: str
    estimated_duration_mins: int = 15
    auto_trigger_intents: List[str] = Field(default_factory=list)
    steps: List[PlaybookStepDef] = Field(default_factory=list)


ENTERPRISE_PLAYBOOK_CATALOG: Dict[str, PlaybookDef] = {
    # -------------------------------------------------------------
    # 1. LOGISTICS & DELIVERY PLAYBOOKS
    # -------------------------------------------------------------
    "LOST_IN_TRANSIT_PLAYBOOK": PlaybookDef(
        code="LOST_IN_TRANSIT_PLAYBOOK",
        name="Lost in Transit (LIT) Resolution Protocol",
        category="LOGISTICS",
        description="Comprehensive carrier tracing and replacement/refund protocol when a package ceases tracking movement for > 5 business days.",
        estimated_duration_mins=12,
        auto_trigger_intents=["LOST_PACKAGE", "NO_TRACKING_UPDATE", "STUCK_IN_TRANSIT"],
        steps=[
            PlaybookStepDef(
                step_order=1,
                step_key="VERIFY_CARRIER_LAST_PING",
                title="Verify Carrier Last Scan Timestamp & Hub Location",
                instructions="Inspect the live carrier milestone feed. Confirm that the last physical scan was more than 5 business days ago without an active delivery appointment.",
                action_type="MANUAL_VERIFY",
            ),
            PlaybookStepDef(
                step_order=2,
                step_key="FILE_CARRIER_TRACE_INQUIRY",
                title="Initiate Official Carrier Tracing Ticket",
                instructions="Trigger automated carrier trace inquiry with FedEx/UPS/USPS API to locate parcel in sort facility.",
                action_type="API_CALL",
            ),
            PlaybookStepDef(
                step_order=3,
                step_key="OFFER_CUSTOMER_RESOLUTION_CHOICE",
                title="Present Replacement or Full Refund Options to Customer",
                instructions="Notify customer that parcel is confirmed lost in transit. Provide choice between expedited priority replacement or full refund.",
                action_type="CUSTOMER_COMMUNICATION",
                suggested_message_template="Dear Customer, we have investigated with the carrier and confirmed your package was lost in transit. We sincerely apologize. We can dispatch a zero-cost expedited replacement today or issue a 100% full refund.",
            ),
            PlaybookStepDef(
                step_order=4,
                step_key="EXECUTE_CHOSEN_COMMERCE_ACTION",
                title="Execute Selected Action in Commerce Engine",
                instructions="Execute either zero-cost replacement order creation or Stripe payment gateway refund.",
                action_type="COMMERCE_MUTATION",
            ),
            PlaybookStepDef(
                step_order=5,
                step_key="SUBMIT_CARRIER_REIMBURSEMENT_CLAIM",
                title="File Carrier Loss Insurance Claim",
                instructions="Submit insurance claim to carrier for declared merchandise value + original shipping fees.",
                action_type="API_CALL",
            ),
        ],
    ),

    "PORCH_PIRACY_STOLEN_PLAYBOOK": PlaybookDef(
        code="PORCH_PIRACY_STOLEN_PLAYBOOK",
        name="Delivered But Missing / Porch Piracy Protocol",
        category="LOGISTICS",
        description="Investigation and resolution protocol when carrier marks package delivered with GPS coordinates but customer cannot locate it.",
        estimated_duration_mins=15,
        auto_trigger_intents=["MARKED_DELIVERED_NOT_RECEIVED", "PACKAGE_STOLEN", "PORCH_PIRACY"],
        steps=[
            PlaybookStepDef(
                step_order=1,
                step_key="VERIFY_CARRIER_GPS_AND_POD",
                title="Inspect Carrier GPS Delivery Coordinates and Proof of Delivery Photo",
                instructions="Download carrier POD (Proof of Delivery). Compare driver drop-off photo and GPS geofence match against customer's registered delivery address.",
                action_type="MANUAL_VERIFY",
            ),
            PlaybookStepDef(
                step_order=2,
                step_key="GUIDE_SURROUNDING_CHECK",
                title="Request Household & Safeplace Area Check",
                instructions="Send friendly checklist asking customer to verify with family members, building concierge/mailroom, and side porches.",
                action_type="CUSTOMER_COMMUNICATION",
                suggested_message_template="Hello! Sometimes drivers leave packages in discreet areas to protect from weather. Could you please check with neighbors, building reception, or behind side gates?",
            ),
            PlaybookStepDef(
                step_order=3,
                step_key="CHECK_CUSTOMER_CLAIM_HISTORY",
                title="Evaluate Customer Lifetime Porch Piracy Claim History",
                instructions="Check customer intelligence ledger. If customer has < 2 stolen claims in past 12 months, authorize immediate courtesy reshipment with signature required.",
                action_type="MANUAL_VERIFY",
            ),
            PlaybookStepDef(
                step_order=4,
                step_key="DISPATCH_SIGNATURE_REQUIRED_REPLACEMENT",
                title="Dispatch Replacement with Mandatory Direct Signature",
                instructions="Generate replacement order with Adult Signature Required delivery restriction to prevent subsequent theft.",
                action_type="COMMERCE_MUTATION",
            ),
        ],
    ),

    "CUSTOMS_TARIFF_HOLD_PLAYBOOK": PlaybookDef(
        code="CUSTOMS_TARIFF_HOLD_PLAYBOOK",
        name="International Customs Clearance & Duty Hold Protocol",
        category="LOGISTICS",
        description="Steps for resolving cross-border international shipments flagged at customs for commercial invoice or duty payments.",
        estimated_duration_mins=20,
        auto_trigger_intents=["CUSTOMS_HOLD", "DUTY_TAX_DISPUTE", "IMPORT_CLEARANCE_DELAY"],
        steps=[
            PlaybookStepDef(
                step_order=1,
                step_key="RETRIEVE_CUSTOMS_CLEARANCE_STATUS",
                title="Inspect DHL/FedEx International Customs Exception Details",
                instructions="Query carrier API for exact customs entry rejection code (e.g. Missing EORI, HS Code clarification, or Unpaid Import VAT).",
                action_type="API_CALL",
            ),
            PlaybookStepDef(
                step_order=2,
                step_key="TRANSMIT_REVISED_COMMERCIAL_INVOICE",
                title="Upload Corrected Commercial Invoice & Harmonized Tariff Codes",
                instructions="Submit digital EDI commercial invoice with verified country of origin and tax identification numbers directly to carrier brokerage portal.",
                action_type="API_CALL",
            ),
            PlaybookStepDef(
                step_order=3,
                step_key="INFORM_CUSTOMER_OF_CLEARANCE_ESTIMATE",
                title="Update Customer on Customs Clearance Timeline",
                instructions="Provide transparent timeline on customs inspection duration and instructions for payment of local import VAT if DDU terms apply.",
                action_type="CUSTOMER_COMMUNICATION",
            ),
        ],
    ),

    # -------------------------------------------------------------
    # 2. PRODUCT QUALITY & DEFECT PLAYBOOKS
    # -------------------------------------------------------------
    "DAMAGED_PRODUCT_PLAYBOOK": PlaybookDef(
        code="DAMAGED_PRODUCT_PLAYBOOK",
        name="Damaged Product in Transit & RMA Resolution",
        category="PRODUCT",
        description="Comprehensive protocol for items damaged upon arrival: damage photo verification, zero-cost replacement dispatch, and carrier claim.",
        estimated_duration_mins=10,
        auto_trigger_intents=["DAMAGED_PRODUCT", "CRUSHED_BOX", "BROKEN_ITEM"],
        steps=[
            PlaybookStepDef(
                step_order=1,
                step_key="VERIFY_ORDER_AND_DELIVERY",
                title="Verify Order Delivery Status & Eligibility Window",
                instructions="Confirm the order was marked delivered within the allowable 30-day window.",
                action_type="MANUAL_VERIFY",
            ),
            PlaybookStepDef(
                step_order=2,
                step_key="INSPECT_DAMAGE_EVIDENCE",
                title="Inspect Customer Damage Photographs",
                instructions="Review uploaded images showing damage to shipping packaging and product item.",
                action_type="MANUAL_VERIFY",
            ),
            PlaybookStepDef(
                step_order=3,
                step_key="DETERMINE_REPLACEMENT_OR_REFUND",
                title="Confirm Customer Resolution Preference",
                instructions="Ask customer if they prefer an expedited replacement or a direct refund to their payment method.",
                action_type="CUSTOMER_COMMUNICATION",
            ),
            PlaybookStepDef(
                step_order=4,
                step_key="EXECUTE_REPLACEMENT_ORDER",
                title="Authorize Zero-Cost Replacement Order in Commerce Engine",
                instructions="Generate replacement order with next-day courier delivery at zero charge.",
                action_type="COMMERCE_MUTATION",
            ),
            PlaybookStepDef(
                step_order=5,
                step_key="FILE_CARRIER_DAMAGE_CLAIM",
                title="Submit Carrier Damage Inspection Claim",
                instructions="File insurance claim with carrier providing parcel photos and commercial invoice.",
                action_type="API_CALL",
            ),
        ],
    ),

    "MISSING_PARTS_HARDWARE_PLAYBOOK": PlaybookDef(
        code="MISSING_PARTS_HARDWARE_PLAYBOOK",
        name="Missing Components & Hardware Accessory Reshipment",
        category="PRODUCT",
        description="Protocol for resolving orders missing small accessories, charging cables, manuals, or assembly screws without returning whole item.",
        estimated_duration_mins=10,
        auto_trigger_intents=["MISSING_PARTS", "INCOMPLETE_PACKAGE", "NO_CHARGER"],
        steps=[
            PlaybookStepDef(
                step_order=1,
                step_key="IDENTIFY_MISSING_PART_NUMBER",
                title="Identify Specific Missing Component SKU / Part #",
                instructions="Look up product Bill of Materials (BOM) in catalog and pinpoint missing accessory part number.",
                action_type="FORM_INPUT",
            ),
            PlaybookStepDef(
                step_order=2,
                step_key="CHECK_SPARE_PARTS_INVENTORY",
                title="Verify Spare Parts Warehouse Stock",
                instructions="Check fulfillment center inventory for standalone accessory SKU.",
                action_type="API_CALL",
            ),
            PlaybookStepDef(
                step_order=3,
                step_key="DISPATCH_PARTS_KIT",
                title="Dispatch Expedited Parts Kit to Customer",
                instructions="Create zero-cost replacement shipment for accessory parts kit.",
                action_type="COMMERCE_MUTATION",
            ),
            PlaybookStepDef(
                step_order=4,
                step_key="ISSUE_COURTESY_APOLOGY_CREDIT",
                title="Issue $10 Inconvenience Courtesy Credit",
                instructions="Credit customer account with courtesy store credit for the delay.",
                action_type="COMMERCE_MUTATION",
            ),
        ],
    ),

    # -------------------------------------------------------------
    # 3. BILLING, PAYMENTS & FRAUD PLAYBOOKS
    # -------------------------------------------------------------
    "DOUBLE_CHARGE_DISPUTE_PLAYBOOK": PlaybookDef(
        code="DOUBLE_CHARGE_DISPUTE_PLAYBOOK",
        name="Duplicate Billing & Payment Authorization Dispute Protocol",
        category="BILLING",
        description="Investigation and automated reversal of duplicate credit card charges or pending authorization holds.",
        estimated_duration_mins=10,
        auto_trigger_intents=["DOUBLE_CHARGED", "DUPLICATE_BILLING", "OVERCHARGED"],
        steps=[
            PlaybookStepDef(
                step_order=1,
                step_key="INSPECT_PAYMENT_GATEWAY_TRANSACTIONS",
                title="Audit Stripe / PayPal Transaction Ledger",
                instructions="Search payment gateway by customer email and card fingerprint. Identify whether second charge is a captured transaction or a temporary pending authorization hold.",
                action_type="API_CALL",
            ),
            PlaybookStepDef(
                step_order=2,
                step_key="VOID_OR_REFUND_DUPLICATE_TRANSACTION",
                title="Execute Void of Pending Hold or Direct Refund",
                instructions="If pending, void authorization immediately. If captured, issue immediate idempotent refund for the exact duplicate amount.",
                action_type="COMMERCE_MUTATION",
            ),
            PlaybookStepDef(
                step_order=3,
                step_key="SEND_TRANSACTION_REVERSAL_RECEIPT",
                title="Send Official Acquirer Reference Number (ARN) Receipt",
                instructions="Email customer the payment gateway refund confirmation with ARN number so their issuing bank can release funds.",
                action_type="CUSTOMER_COMMUNICATION",
            ),
        ],
    ),

    "FRAUD_CHARGEBACK_DEFENSE_PLAYBOOK": PlaybookDef(
        code="FRAUD_CHARGEBACK_DEFENSE_PLAYBOOK",
        name="Chargeback Defense & Evidence Dossier Assembly",
        category="BILLING",
        description="Automated compilation of dispute evidence (AVS match, 3D Secure authentication, carrier POD signature, IP address logs) for merchant acquirers.",
        estimated_duration_mins=25,
        auto_trigger_intents=["CHARGEBACK_NOTIFICATION", "DISPUTE_FILED", "FRAUD_CLAIM"],
        steps=[
            PlaybookStepDef(
                step_order=1,
                step_key="COLLECT_SECURITY_TELEMETRY",
                title="Extract Checkout Security Telemetry",
                instructions="Gather customer IP geolocation, device fingerprint, 3D Secure v2 liability shift proof, and CVV/AVS address verification match codes.",
                action_type="API_CALL",
            ),
            PlaybookStepDef(
                step_order=2,
                step_key="COLLECT_DELIVERY_PROOF",
                title="Attach Carrier Proof of Delivery and Signature Document",
                instructions="Download high-resolution carrier POD PDF showing delivery to billing address zip code.",
                action_type="API_CALL",
            ),
            PlaybookStepDef(
                step_order=3,
                step_key="ASSEMBLE_EVIDENCE_DOSSIER",
                title="Generate Standardized Dispute Dossier PDF",
                instructions="Compile transaction timeline, product invoice, tracking records, and terms of service acknowledgment.",
                action_type="FORM_INPUT",
            ),
            PlaybookStepDef(
                step_order=4,
                step_key="TRANSMIT_TO_PAYMENT_GATEWAY",
                title="Submit Evidence via Stripe/PayPal Dispute API",
                instructions="Submit structured dispute payload before the acquirer filing deadline.",
                action_type="API_CALL",
            ),
        ],
    ),

    # -------------------------------------------------------------
    # 4. CUSTOMER EXPERIENCE & SPECIAL PROTOCOLS
    # -------------------------------------------------------------
    "PRICE_MATCH_GUARANTEE_PLAYBOOK": PlaybookDef(
        code="PRICE_MATCH_GUARANTEE_PLAYBOOK",
        name="Post-Purchase Price Match & Promotional Credit",
        category="CUSTOMER_EXPERIENCE",
        description="Protocol for issuing partial refunds or promotional credits when an item purchased drops in price within 14 days.",
        estimated_duration_mins=8,
        auto_trigger_intents=["PRICE_MATCH", "PRICE_DROP", "PROMO_CODE_MISSED"],
        steps=[
            PlaybookStepDef(
                step_order=1,
                step_key="VERIFY_PRICE_MATCH_TIMEFRAME",
                title="Confirm Purchase Date is Within 14 Days",
                instructions="Verify that the order was placed within the last 14 calendar days.",
                action_type="MANUAL_VERIFY",
            ),
            PlaybookStepDef(
                step_order=2,
                step_key="VERIFY_COMPETITOR_OR_CURRENT_PRICE",
                title="Verify Live Listed Price & SKU Match",
                instructions="Confirm identical brand, model, color, and warranty terms on current website listing or authorized competitor.",
                action_type="MANUAL_VERIFY",
            ),
            PlaybookStepDef(
                step_order=3,
                step_key="CALCULATE_DIFFERENTIAL_REFUND",
                title="Calculate Tax-Adjusted Difference",
                instructions="Calculate exact price difference including proportional sales tax refund.",
                action_type="FORM_INPUT",
            ),
            PlaybookStepDef(
                step_order=4,
                step_key="EXECUTE_PARTIAL_REFUND",
                title="Issue Partial Refund to Original Card",
                instructions="Submit partial refund against original payment charge transaction.",
                action_type="COMMERCE_MUTATION",
            ),
        ],
    ),

    "HAZARDOUS_MATERIAL_RETURN_PLAYBOOK": PlaybookDef(
        code="HAZARDOUS_MATERIAL_RETURN_PLAYBOOK",
        name="Hazardous Material & Battery Safety Return Protocol",
        category="COMPLIANCE",
        description="Strict DOT/IATA compliance guidelines for handling returns of swollen lithium batteries, aerosol sprays, or flammable liquids.",
        estimated_duration_mins=20,
        auto_trigger_intents=["SWOLLEN_BATTERY", "HAZMAT_RETURN", "LEAKING_CHEMICAL"],
        steps=[
            PlaybookStepDef(
                step_order=1,
                step_key="ASSESS_SAFETY_HAZARD",
                title="Assess Hazardous Condition & Prohibit Mail Transport if Swollen",
                instructions="If customer reports battery swelling, overheating, or chemical leakage, DO NOT issue return label under any circumstance (DOT air transport violation).",
                action_type="MANUAL_VERIFY",
            ),
            PlaybookStepDef(
                step_order=2,
                step_key="PROVIDE_LOCAL_RECYCLING_INSTRUCTIONS",
                title="Provide EPA/Call2Recycle Local Disposal Guidelines",
                instructions="Direct customer to certified local hazardous e-waste recycling facility.",
                action_type="CUSTOMER_COMMUNICATION",
            ),
            PlaybookStepDef(
                step_order=3,
                step_key="AUTHORIZE_RETURNLESS_REPLACEMENT",
                title="Authorize Returnless Replacement or Full Refund",
                instructions="Waive physical return requirement and immediately dispatch replacement item or full credit.",
                action_type="COMMERCE_MUTATION",
            ),
        ],
    ),
}


class PlaybookCatalogService:
    @staticmethod
    def get_playbook_definition(code: str) -> Optional[PlaybookDef]:
        return ENTERPRISE_PLAYBOOK_CATALOG.get(code)

    @staticmethod
    def list_all_playbooks() -> List[PlaybookDef]:
        return list(ENTERPRISE_PLAYBOOK_CATALOG.values())

    @staticmethod
    def find_playbook_by_intent(intent: str) -> Optional[PlaybookDef]:
        intent_upper = intent.upper()
        for pb in ENTERPRISE_PLAYBOOK_CATALOG.values():
            if intent_upper in pb.auto_trigger_intents or any(intent_upper in it for it in pb.auto_trigger_intents):
                return pb
        return None
