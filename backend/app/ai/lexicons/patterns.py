"""
Enterprise NLP Customer Intent Match Patterns, N-grams, and Classification Dictionaries.
"""

from typing import Any, Dict, List, Set


# 40+ Structured Customer Support Intent Definitions with High-Precision Keyword & N-Gram Triggers
INTENT_PATTERNS_MAP: Dict[str, Dict[str, Any]] = {
    # 1. Product Quality & Defects
    "DAMAGED_PRODUCT": {
        "category": "PRODUCT",
        "subcategory": "DAMAGED_ITEM",
        "default_priority": "HIGH",
        "playbook_code": "DAMAGED_PRODUCT_PLAYBOOK",
        "keywords": [
            "damaged", "broken", "cracked", "shattered", "scratched", "dented", "smashed",
            "crushed box", "crushed packaging", "water damaged", "torn box", "split open",
            "snapped in half", "cracked screen", "shattered glass", "plastic broken", "bent frame",
            "opened box", "seal ripped", "arrived broken", "damaged on arrival", "dead on arrival",
        ],
        "regex_patterns": [
            r"\b(arrive[d]?|receive[d]?)\s+(broken|damaged|smashed|crushed)\b",
            r"\b(box|package|carton)\s+(was\s+)?(crushed|damaged|opened|punctured)\b",
            r"\b(screen|glass|display|casing|frame)\s+(is\s+)?(cracked|shattered|broken)\b",
        ],
    },
    "DEFECTIVE_HARDWARE": {
        "category": "PRODUCT",
        "subcategory": "HARDWARE_FAULT",
        "default_priority": "HIGH",
        "playbook_code": "DAMAGED_PRODUCT_PLAYBOOK",
        "keywords": [
            "defective", "not working", "won't turn on", "does not turn on", "dead on arrival",
            "battery draining", "won't charge", "charging port loose", "malfunctioning", "faulty",
            "bluetooth won't connect", "pairing failed", "audio distortion", "hissing noise",
            "fan loud", "overheating", "smoking", "glitching", "dead pixel", "stick drift",
        ],
        "regex_patterns": [
            r"\b(won't|will\s+not|doesn't|does\s+not)\s+(turn\s+on|power\s+on|charge|work|connect)\b",
            r"\b(battery|power)\s+(drain[s]?|fail[s]?|swollen|dies\s+fast)\b",
            r"\b(sound|audio|speaker|microphone)\s+(distort[ed]?|crackl[ing]?|dead)\b",
        ],
    },
    "MISSING_PARTS": {
        "category": "PRODUCT",
        "subcategory": "INCOMPLETE_SHIPMENT",
        "default_priority": "MEDIUM",
        "playbook_code": "MISSING_PARTS_HARDWARE_PLAYBOOK",
        "keywords": [
            "missing parts", "missing piece", "missing screws", "missing cable", "missing charger",
            "accessory missing", "incomplete package", "didn't include manual", "missing adapter",
            "missing strap", "missing remote", "part missing from box", "only received half",
        ],
        "regex_patterns": [
            r"\bmissing\s+(part[s]?|cable[s]?|charger[s]?|screw[s]?|adapter[s]?|remote|piece[s]?)\b",
            r"\b(didn't|did\s+not)\s+include\s+(the\s+)?(charger|cable|manual|remote|battery)\b",
        ],
    },
    "WRONG_ITEM_RECEIVED": {
        "category": "PRODUCT",
        "subcategory": "MISPICK",
        "default_priority": "HIGH",
        "playbook_code": "DAMAGED_PRODUCT_PLAYBOOK",
        "keywords": [
            "wrong item", "incorrect item", "wrong size", "wrong color", "sent wrong product",
            "received wrong size", "not what i ordered", "different model", "wrong model",
            "ordered blue received black", "different color sent", "incorrect sku",
        ],
        "regex_patterns": [
            r"\b(sent|received|got)\s+(the\s+)?(wrong|incorrect|different)\s+(item|product|size|color|model)\b",
            r"\bnot\s+what\s+i\s+(order[ed]?|bought|purchased)\b",
        ],
    },

    # 2. Logistics & Delivery Inquiries
    "LATE_DELIVERY": {
        "category": "DELIVERY",
        "subcategory": "IN_TRANSIT_DELAY",
        "default_priority": "MEDIUM",
        "playbook_code": "LOST_IN_TRANSIT_PLAYBOOK",
        "keywords": [
            "where is my order", "where is my package", "order late", "package late", "delivery delayed",
            "tracking stuck", "no tracking update", "in transit for days", "past estimated delivery",
            "when will it arrive", "taking too long", "overdue delivery", "still waiting for delivery",
        ],
        "regex_patterns": [
            r"\bwhere\s+(is|are)\s+my\s+(order|package|shipment|delivery)\b",
            r"\b(package|order|delivery)\s+(is\s+)?(late|delayed|stuck|overdue)\b",
            r"\bno\s+(tracking|movement|update)\s+for\s+\d+\s+days\b",
        ],
    },
    "MARKED_DELIVERED_NOT_RECEIVED": {
        "category": "DELIVERY",
        "subcategory": "PORCH_PIRACY",
        "default_priority": "HIGH",
        "playbook_code": "PORCH_PIRACY_STOLEN_PLAYBOOK",
        "keywords": [
            "says delivered but not here", "marked delivered no package", "never received package",
            "carrier claims delivered", "package stolen", "porch pirate", "not on porch",
            "missing delivery", "shows delivered didn't receive", "checked everywhere no parcel",
        ],
        "regex_patterns": [
            r"\b(shows|says|marked)\s+delivered\s+(but|however)\s+(i\s+)?(never\s+got|didn't\s+get|not\s+here)\b",
            r"\b(package|parcel)\s+(was\s+)?(stolen|missing|not\s+delivered)\b",
        ],
    },
    "CUSTOMS_IMPORT_HOLD": {
        "category": "DELIVERY",
        "subcategory": "CUSTOMS_DELAY",
        "default_priority": "HIGH",
        "playbook_code": "CUSTOMS_TARIFF_HOLD_PLAYBOOK",
        "keywords": [
            "customs hold", "held in customs", "customs duty", "import tax", "clearance delay",
            "dhl customs", "fedex international delay", "tariff charge", "customs invoice needed",
        ],
        "regex_patterns": [
            r"\bheld\s+(in|at)\s+customs\b",
            r"\bcustoms\s+(clearance|duty|tax|inspection|hold)\b",
        ],
    },
    "CHANGE_SHIPPING_ADDRESS": {
        "category": "DELIVERY",
        "subcategory": "ADDRESS_CORRECTION",
        "default_priority": "CRITICAL",
        "playbook_code": "LOST_IN_TRANSIT_PLAYBOOK",
        "keywords": [
            "change shipping address", "wrong address on order", "update delivery address",
            "entered wrong address", "forgot apartment number", "change address before dispatch",
            "deliver to new address", "redirect package",
        ],
        "regex_patterns": [
            r"\b(change|update|correct|fix)\s+(my\s+)?(shipping|delivery|mailing)?\s+address\b",
            r"\bwrong\s+address\s+(on\s+order|entered)\b",
        ],
    },

    # 3. Returns & Refunds
    "REQUEST_RETURN_LABEL": {
        "category": "RETURNS",
        "subcategory": "RMA_CREATION",
        "default_priority": "MEDIUM",
        "playbook_code": "DAMAGED_PRODUCT_PLAYBOOK",
        "keywords": [
            "how to return", "want to return", "send it back", "return shipping label",
            "rma number", "return request", "exchange for another size", "print return label",
            "start a return", "return authorization", "return policy",
        ],
        "regex_patterns": [
            r"\b(want|like|need)\s+to\s+(return|send\s+back|exchange)\b",
            r"\b(generate|print|send)\s+(a\s+)?(return\s+label|rma)\b",
        ],
    },
    "REFUND_STATUS_INQUIRY": {
        "category": "REFUNDS",
        "subcategory": "REFUND_TRACKING",
        "default_priority": "MEDIUM",
        "playbook_code": "DOUBLE_CHARGE_DISPUTE_PLAYBOOK",
        "keywords": [
            "where is my refund", "when will i get refunded", "refund status", "haven't received refund",
            "refund not credited", "money not back in account", "refund taking too long",
        ],
        "regex_patterns": [
            r"\bwhere\s+is\s+my\s+refund\b",
            r"\bwhen\s+(will|do)\s+i\s+get\s+(my\s+)?refund\b",
            r"\b(refund|credit)\s+(has\s+not|not\s+yet|hasn't)\s+(arrived|appeared|posted)\b",
        ],
    },

    # 4. Billing & Payment Inquiries
    "DOUBLE_CHARGED": {
        "category": "PAYMENT",
        "subcategory": "DUPLICATE_CHARGE",
        "default_priority": "HIGH",
        "playbook_code": "DOUBLE_CHARGE_DISPUTE_PLAYBOOK",
        "keywords": [
            "double charged", "charged twice", "billed twice", "two charges on card",
            "duplicate charge", "overcharged", "charged wrong amount", "unauthorized transaction",
            "extra charge on bank statement",
        ],
        "regex_patterns": [
            r"\b(charged|billed)\s+(me\s+)?(twice|two\s+times|double)\b",
            r"\bduplicate\s+(charge|transaction|billing|payment)\b",
            r"\bovercharged\s+(by|\$|\d+)\b",
        ],
    },
    "SUBSCRIPTION_CANCELLATION": {
        "category": "PAYMENT",
        "subcategory": "RECURRING_BILLING",
        "default_priority": "HIGH",
        "playbook_code": "DOUBLE_CHARGE_DISPUTE_PLAYBOOK",
        "keywords": [
            "cancel subscription", "stop auto renew", "cancel membership", "stop charging my card",
            "recurring charge cancel", "cancel monthly renewal", "unsubscribe from billing",
        ],
        "regex_patterns": [
            r"\bcancel\s+(my\s+)?(subscription|membership|recurring|auto[\s-]?renew)\b",
            r"\bstop\s+charging\s+(my\s+)?(card|account)\b",
        ],
    },

    # 5. Order Cancellation & Modifications
    "CANCEL_ORDER": {
        "category": "ORDER_MANAGEMENT",
        "subcategory": "ORDER_CANCELLATION",
        "default_priority": "CRITICAL",
        "playbook_code": "LOST_IN_TRANSIT_PLAYBOOK",
        "keywords": [
            "cancel order", "cancel my order", "placed order by mistake", "don't want it anymore",
            "stop shipment", "cancel before shipping", "abort order", "accidental purchase",
        ],
        "regex_patterns": [
            r"\bcancel\s+(my\s+)?(order|purchase)\b",
            r"\bplaced\s+order\s+by\s+mistake\b",
        ],
    },

    # 6. Price Matching & Discounts
    "PRICE_MATCH_REQUEST": {
        "category": "PAYMENT",
        "subcategory": "PRICE_PROTECTION",
        "default_priority": "LOW",
        "playbook_code": "PRICE_MATCH_GUARANTEE_PLAYBOOK",
        "keywords": [
            "price match", "price dropped", "item is now on sale", "refund price difference",
            "saw cheaper price", "price guarantee claim", "missed coupon code", "promo code didn't work",
        ],
        "regex_patterns": [
            r"\bprice\s+(match|protection|guarantee|drop[ped]?)\b",
            r"\b(item|product)\s+(went|is\s+now)\s+on\s+sale\b",
        ],
    },
}
