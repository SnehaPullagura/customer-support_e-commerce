"""
E-Commerce Named Entity Recognition (NER) and Diagnostic Slot Extractor.
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExtractedEntities(BaseModel):
    order_ids: List[str] = Field(default_factory=list)
    tracking_numbers: List[str] = Field(default_factory=list)
    monetary_amounts: List[float] = Field(default_factory=list)
    rma_numbers: List[str] = Field(default_factory=list)
    email_addresses: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    sku_codes: List[str] = Field(default_factory=list)
    serial_numbers: List[str] = Field(default_factory=list)


class EntityExtractor:
    # High-precision regular expressions
    ORDER_REGEX = re.compile(r"\b(ORD-\d{4,8}|#[0-9]{4,8}|ORDER[-_]?[0-9]{4,8})\b", re.IGNORECASE)
    TRACKING_REGEX = re.compile(
        r"\b(1Z[0-9A-Z]{16}|94[0-9]{20}|\d{12}|\d{15}|SHIP-\d{4,8}|TBA\d{12})\b", re.IGNORECASE
    )
    MONEY_REGEX = re.compile(r"\$(\d+(?:\.\d{2})?)|\b(\d+(?:\.\d{2})?)\s*(?:dollars|usd|bucks)\b", re.IGNORECASE)
    RMA_REGEX = re.compile(r"\b(RMA-\d{4,8}|RET-\d{4,8})\b", re.IGNORECASE)
    EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    PHONE_REGEX = re.compile(r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b")
    SKU_REGEX = re.compile(r"\b(PROD-\d{4,8}|SKU[-_]?[0-9A-Z]{4,10})\b", re.IGNORECASE)

    @staticmethod
    def extract_all_entities(text: str) -> ExtractedEntities:
        # Order IDs
        orders = [m.group(1).upper() for m in EntityExtractor.ORDER_REGEX.finditer(text)]

        # Tracking numbers
        tracking = [m.group(1).upper() for m in EntityExtractor.TRACKING_REGEX.finditer(text)]

        # Amounts
        amounts = []
        for m in EntityExtractor.MONEY_REGEX.finditer(text):
            amt_str = m.group(1) or m.group(2)
            try:
                amounts.append(float(amt_str))
            except ValueError:
                pass

        # RMAs
        rmas = [m.group(1).upper() for m in EntityExtractor.RMA_REGEX.finditer(text)]

        # Emails
        emails = EntityExtractor.EMAIL_REGEX.findall(text)

        # Phones
        phones = EntityExtractor.PHONE_REGEX.findall(text)

        # SKUs
        skus = [m.group(1).upper() for m in EntityExtractor.SKU_REGEX.finditer(text)]

        return ExtractedEntities(
            order_ids=list(set(orders)),
            tracking_numbers=list(set(tracking)),
            monetary_amounts=amounts,
            rma_numbers=list(set(rmas)),
            email_addresses=list(set(emails)),
            phone_numbers=list(set(phones)),
            sku_codes=list(set(skus)),
        )
