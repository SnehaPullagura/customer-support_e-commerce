"""
Smart Home Appliances & Security (HOME_IOT)
Enterprise Product Specifications, Bill of Materials (BOM), and RMA Defect Profiles.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProductSpecification(BaseModel):
    product_id: str
    sku: str
    title: str
    brand: str
    category_code: str = "HOME_IOT"
    retail_price_cents: int
    cost_price_cents: int
    weight_grams: int
    dimensions_cm: Dict[str, float]
    serialized: bool = True
    is_hazmat: bool = False
    warranty_months: int = 24
    bill_of_materials: List[Dict[str, str]] = Field(default_factory=list)
    common_failure_modes: List[Dict[str, Any]] = Field(default_factory=list)
    diagnostic_self_test_steps: List[str] = Field(default_factory=list)


class SmartHomeAppliancesCatalog:
    CATEGORY_NAME = "Smart Home Appliances & Security"
    CATEGORY_PREFIX = "HOME_IOT"

    PRODUCTS: Dict[str, ProductSpecification] = {
        f"PROD-HOME_IOT-001": ProductSpecification(
            product_id=f"PROD-HOME_IOT-001",
            sku=f"SKU-HOME_IOT-PRO-BLK",
            title=f"Flagship Professional Smart Home Appliances & Security Model Alpha",
            brand="Apex Industries",
            retail_price_cents=29999,
            cost_price_cents=11000,
            weight_grams=450,
            dimensions_cm={"length": 22.0, "width": 18.0, "height": 8.0},
            bill_of_materials=[
                {"part_number": "BOM-001", "name": "Main Logic Board", "cost_cents": "4500"},
                {"part_number": "BOM-002", "name": "Lithium Battery Module", "cost_cents": "1800"},
                {"part_number": "BOM-003", "name": "Precision Chassis Assembly", "cost_cents": "2200"},
                {"part_number": "BOM-004", "name": "High-Yield Transducer Subsystem", "cost_cents": "3100"},
            ],
            common_failure_modes=[
                {"code": "FAIL_PWR", "symptom": "No Power / Intermittent Charge", "resolution": "SWAP_LOGIC_BOARD"},
                {"code": "FAIL_RF", "symptom": "Wireless Signal Attenuation", "resolution": "REPLACE_ANTENNA"},
                {"code": "FAIL_MECH", "symptom": "Physical Hinge Fatigue", "resolution": "REPLACE_HOUSING"},
            ],
            diagnostic_self_test_steps=[
                "Verify DC input voltage on diagnostic test pads.",
                "Execute SPI bus loopback verification test.",
                "Inspect solder joint integrity under 20x optical magnification.",
                "Perform 1000-cycle mechanical stress test on articulating joints.",
            ],
        ),
        f"PROD-HOME_IOT-002": ProductSpecification(
            product_id=f"PROD-HOME_IOT-002",
            sku=f"SKU-HOME_IOT-LITE-SLV",
            title=f"Compact Ultra-Portable Smart Home Appliances & Security Edition",
            brand="Apex Industries",
            retail_price_cents=14999,
            cost_price_cents=5200,
            weight_grams=210,
            dimensions_cm={"length": 15.0, "width": 12.0, "height": 5.0},
            bill_of_materials=[
                {"part_number": "BOM-101", "name": "Micro Controller Unit", "cost_cents": "2100"},
                {"part_number": "BOM-102", "name": "Ultralight Polycarbonate Casing", "cost_cents": "1200"},
            ],
            common_failure_modes=[
                {"code": "FAIL_BTN", "symptom": "Tactile Switch Wear", "resolution": "CLEAN_OR_SWAP"},
                {"code": "FAIL_LED", "symptom": "Indicator LED Segment Out", "resolution": "REPLACE_PCB"},
            ],
            diagnostic_self_test_steps=[
                "Measure quiescent standby current draw (< 50 uA expected).",
                "Execute factory hardware reset command sequence.",
            ],
        ),
    }

    @classmethod
    def get_product(cls, product_id: str) -> Optional[ProductSpecification]:
        return cls.PRODUCTS.get(product_id)

    @classmethod
    def list_products(cls) -> List[ProductSpecification]:
        return list(cls.PRODUCTS.values())
