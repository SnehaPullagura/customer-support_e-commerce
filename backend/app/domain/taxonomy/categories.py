"""
Comprehensive E-Commerce Product Category Taxonomy, Return Windows, and Warranty Matrices.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CategoryPolicy(BaseModel):
    category_code: str
    category_name: str
    department: str
    return_window_days: int = 30
    restocking_fee_percent: float = 0.0
    requires_serial_number: bool = False
    is_hygiene_sensitive: bool = False
    is_hazmat: bool = False
    is_final_sale: bool = False
    requires_original_packaging: bool = True
    standard_warranty_months: int = 12
    extended_warranty_eligible: bool = True
    inspection_checklist: List[str] = Field(default_factory=list)
    common_defect_types: List[str] = Field(default_factory=list)


ENTERPRISE_CATEGORY_TAXONOMY: Dict[str, CategoryPolicy] = {
    # 1. Electronics & Audio
    "ELEC_HEADPHONES": CategoryPolicy(
        category_code="ELEC_HEADPHONES",
        category_name="Wireless & Over-Ear Headphones",
        department="ELECTRONICS",
        return_window_days=30,
        requires_serial_number=True,
        standard_warranty_months=24,
        inspection_checklist=["Check headband crack integrity", "Test Bluetooth pairing", "Inspect USB-C charging port", "Verify acoustic drivers balance"],
        common_defect_types=["BATTERY_DRAIN", "BLUETOOTH_DISCONNECT", "HEADBAND_CRACK", "DRIVER_DISTORTION", "ANC_HISS"],
    ),
    "ELEC_SMARTPHONES": CategoryPolicy(
        category_code="ELEC_SMARTPHONES",
        category_name="Smartphones & Cellular Handsets",
        department="ELECTRONICS",
        return_window_days=15,
        restocking_fee_percent=10.0,
        requires_serial_number=True,
        standard_warranty_months=12,
        inspection_checklist=["Verify IMEI match on box and motherboard", "Check iCloud/Google account unlinked", "Inspect OLED glass for micro-fractures", "Battery health diagnosis"],
        common_defect_types=["SCREEN_FLICKER", "BATTERY_SWELLING", "PORT_LOOSE", "CAMERA_OIS_BLUR", "MODEM_DROPS"],
    ),
    "ELEC_LAPTOPS": CategoryPolicy(
        category_code="ELEC_LAPTOPS",
        category_name="Laptops & Portable Workstations",
        department="ELECTRONICS",
        return_window_days=30,
        restocking_fee_percent=15.0,
        requires_serial_number=True,
        standard_warranty_months=12,
        inspection_checklist=["Serial number BIOS match", "Run memtest diagnostics", "Inspect keyboard keycaps and trackpad", "Verify AC adapter output voltage"],
        common_defect_types=["DEAD_PIXEL", "THERMAL_THROTTLING", "KEYBOARD_STICKING", "FAN_WHINE", "BATTERY_FAIL"],
    ),
    "ELEC_SMARTWATCHES": CategoryPolicy(
        category_code="ELEC_SMARTWATCHES",
        category_name="Smartwatches & Fitness Trackers",
        department="ELECTRONICS",
        return_window_days=30,
        requires_serial_number=True,
        is_hygiene_sensitive=True,
        standard_warranty_months=12,
        inspection_checklist=["Check optical heart rate sensor glass", "Verify water seal integrity", "Test haptic motor", "Sanitize silicone band"],
        common_defect_types=["SENSOR_UNRESPONSIVE", "SCREEN_TOUCH_GHOST", "CHARGING_PINS_CORRODED", "STRAP_SNAP"],
    ),
    "ELEC_CAMERAS": CategoryPolicy(
        category_code="ELEC_CAMERAS",
        category_name="Digital Mirrorless & DSLR Cameras",
        department="ELECTRONICS",
        return_window_days=30,
        requires_serial_number=True,
        standard_warranty_months=24,
        inspection_checklist=["Check sensor dust and shutter actuations count", "Inspect lens mount pins", "Test EVF display", "Verify image stabilization"],
        common_defect_types=["SHUTTER_JAM", "HOT_PIXELS", "IBIS_ERROR", "CARD_SLOT_PINS_BENT"],
    ),
    "ELEC_DRONES": CategoryPolicy(
        category_code="ELEC_DRONES",
        category_name="Quadcopter Drones & Aerial Imaging",
        department="ELECTRONICS",
        return_window_days=14,
        requires_serial_number=True,
        is_hazmat=True, # Lithium polymer flight batteries
        standard_warranty_months=12,
        inspection_checklist=["Flight log telemetry download", "Inspect rotor arm structural integrity", "Gimbal 3-axis calibration test", "LiPo battery cycle inspection"],
        common_defect_types=["GIMBAL_MOTOR_OVERLOAD", "GPS_LOSS", "ESC_BURNOUT", "CRASH_DAMAGE"],
    ),
    "ELEC_GAMING_CONSOLES": CategoryPolicy(
        category_code="ELEC_GAMING_CONSOLES",
        category_name="Gaming Consoles & VR Headsets",
        department="ELECTRONICS",
        return_window_days=30,
        requires_serial_number=True,
        standard_warranty_months=12,
        inspection_checklist=["Check HDMI 2.1 port pins", "Factory reset internal SSD", "Inspect cooling exhaust", "Pair controllers"],
        common_defect_types=["HDMI_NO_SIGNAL", "STICK_DRIFT", "DISC_DRIVE_EJECT_FAIL", "OVERHEATING_SHUTDOWN"],
    ),
    "ELEC_SMART_HOME": CategoryPolicy(
        category_code="ELEC_SMART_HOME",
        category_name="Smart Home Hubs, Cameras & Thermostats",
        department="ELECTRONICS",
        return_window_days=30,
        requires_serial_number=True,
        standard_warranty_months=12,
        inspection_checklist=["Matter/Zigbee pairing reset", "Check night vision IR LEDs", "Inspect backplate wiring terminal", "Verify cloud deregistration"],
        common_defect_types=["WIFI_DISCONNECT", "PIR_FALSE_TRIGGER", "RELAY_CLICK_FAIL", "TWO_WAY_AUDIO_NOISE"],
    ),

    # 2. Apparel, Footwear & Luxury Goods
    "APP_MENS_CLOTHING": CategoryPolicy(
        category_code="APP_MENS_CLOTHING",
        category_name="Men's Apparel & Outerwear",
        department="APPAREL",
        return_window_days=45,
        inspection_checklist=["Verify original tags attached", "Check seams for unraveling", "Inspect for odor/perfume/stains", "Verify zipper and button fasteners"],
        common_defect_types=["STITCHING_TORN", "ZIPPER_BROKEN", "COLOR_FADE", "BUTTON_MISSING", "FABRIC_PILLING"],
    ),
    "APP_WOMENS_CLOTHING": CategoryPolicy(
        category_code="APP_WOMENS_CLOTHING",
        category_name="Women's Apparel & Dresses",
        department="APPAREL",
        return_window_days=45,
        inspection_checklist=["Verify hangtags intact", "Inspect delicate lace/silk weave", "Check hemline integrity", "Verify lining condition"],
        common_defect_types=["SEAM_SPLIT", "ZIPPER_SNAG", "DYE_BLEED", "SIZE_MISMATCH", "LOOSE_BEADING"],
    ),
    "APP_FOOTWEAR": CategoryPolicy(
        category_code="APP_FOOTWEAR",
        category_name="Sneakers, Boots & Athletic Shoes",
        department="APPAREL",
        return_window_days=45,
        inspection_checklist=["Inspect outsoles for outdoor tread wear", "Check insole hygiene", "Verify original shoe box and extra laces present", "Inspect eyelets"],
        common_defect_types=["SOLE_SEPARATION", "AIR_BUBBLE_POP", "EYELET_TEAR", "INCORRECT_SIZE_TAG", "LEATHER_CREASING"],
    ),
    "APP_SWIMWEAR": CategoryPolicy(
        category_code="APP_SWIMWEAR",
        category_name="Swimwear & Intimates",
        department="APPAREL",
        return_window_days=30,
        is_hygiene_sensitive=True,
        inspection_checklist=["Verify hygiene protective liner seal is intact", "Inspect elastic waistbands", "Confirm unworn state with original tags"],
        common_defect_types=["ELASTIC_PERISHED", "LINER_MISSING", "COLOR_RUN", "UNDERWIRE_POKE"],
    ),
    "APP_LUXURY_JEWELRY": CategoryPolicy(
        category_code="APP_LUXURY_JEWELRY",
        category_name="Fine Jewelry & Luxury Watches",
        department="LUXURY",
        return_window_days=14,
        restocking_fee_percent=10.0,
        requires_serial_number=True,
        standard_warranty_months=36,
        inspection_checklist=["Gemologist authenticity validation", "Prong setting tension test", "Microscopic serial number check", "Original certificate inspection"],
        common_defect_types=["STONE_LOOSE", "CLASP_DEFECT", "PLATING_DISCOLORATION", "TIME_DRIFT"],
    ),
    "APP_HANDBAGS": CategoryPolicy(
        category_code="APP_HANDBAGS",
        category_name="Designer Handbags & Leather Goods",
        department="LUXURY",
        return_window_days=30,
        requires_serial_number=True,
        inspection_checklist=["Authenticate RFID microchip/NFC tag", "Check edge paint on handles", "Inspect interior lining for marks", "Confirm dust bag presence"],
        common_defect_types=["EDGE_PAINT_CRACK", "HARDWARE_SCRATCH", "STITCH_DEFECT", "STRAP_BUCKLE_FAIL"],
    ),

    # 3. Home, Furniture & Appliances
    "HOME_LARGE_APPLIANCES": CategoryPolicy(
        category_code="HOME_LARGE_APPLIANCES",
        category_name="Refrigerators, Washers & Ranges",
        department="HOME_APPLIANCES",
        return_window_days=30,
        requires_serial_number=True,
        standard_warranty_months=24,
        inspection_checklist=["Inspect compressor/motor operations", "Check stainless steel panels for dents", "Verify door seal gaskets", "Water line pressure test"],
        common_defect_types=["COMPRESSOR_FAIL", "DRUM_OUT_OF_BALANCE", "DOOR_SEAL_LEAK", "CONTROL_BOARD_ERROR", "FREIGHT_DENT"],
    ),
    "HOME_FURNITURE_FREIGHT": CategoryPolicy(
        category_code="HOME_FURNITURE_FREIGHT",
        category_name="Sofas, Dining Tables & Mattresses",
        department="HOME_FURNITURE",
        return_window_days=30,
        restocking_fee_percent=15.0,
        inspection_checklist=["Check hardwood frame joints", "Inspect fabric/leather upholstery for tears", "Verify hardware bolt pack count", "Cushion foam rebound test"],
        common_defect_types=["FRAME_CRACK", "UPHOLSTERY_TEAR", "MISSING_BOLTS", "WOBBLE_LEGS", "FABRIC_STAIN"],
    ),
    "HOME_POWER_TOOLS": CategoryPolicy(
        category_code="HOME_POWER_TOOLS",
        category_name="Cordless Drills, Saws & Lawn Mowers",
        department="HARDWARE",
        return_window_days=30,
        requires_serial_number=True,
        is_hazmat=True,
        standard_warranty_months=36,
        inspection_checklist=["Check brushless motor torque", "Test battery lock and charger output", "Verify safety blade guards", "Inspect chuck runout"],
        common_defect_types=["CHUCK_WOBBLE", "TRIGGER_SWITCH_BURNOUT", "BATTERY_CELL_DEAD", "OVERLOAD_PROTECTION_TRIP"],
    ),

    # 4. Beauty, Health & Consumables
    "BEAUTY_SKINCARE": CategoryPolicy(
        category_code="BEAUTY_SKINCARE",
        category_name="Cosmetics, Serums & Fragrances",
        department="BEAUTY",
        return_window_days=30,
        is_hygiene_sensitive=True,
        inspection_checklist=["Verify tamper-evident foil seal intact", "Check expiration lot number", "Inspect glass dropper/pump mechanism"],
        common_defect_types=["PUMP_CLOGGED", "SEAL_BROKEN", "EXPIRATION_PASSED", "ALLERGIC_REACTION_CLAIM"],
    ),
    "HEALTH_MEDICAL_DEVICES": CategoryPolicy(
        category_code="HEALTH_MEDICAL_DEVICES",
        category_name="Blood Pressure Monitors & CPAP",
        department="HEALTH",
        return_window_days=30,
        requires_serial_number=True,
        is_hygiene_sensitive=True,
        standard_warranty_months=24,
        inspection_checklist=["FDA medical device tracking calibration", "Check air hose seal", "Verify digital sensor accuracy", "Sanitary intake check"],
        common_defect_types=["CALIBRATION_DRIFT", "PRESSURE_PUMP_FAIL", "LCD_SEGMENT_OUT", "CUFF_LEAK"],
    ),
    "PERISHABLE_GROCERY": CategoryPolicy(
        category_code="PERISHABLE_GROCERY",
        category_name="Gourmet Food, Coffee & Fresh Produce",
        department="GROCERY",
        return_window_days=7,
        is_final_sale=True, # Non-returnable, refund or credit only
        inspection_checklist=["Temperature chain integrity check", "Check best before date", "Packaging puncture inspection"],
        common_defect_types=["SPOILED_IN_TRANSIT", "PACKAGE_LEAK", "EXPIRED", "COLD_CHAIN_BROKEN"],
    ),

    # 5. Digital, Gift Cards & Subscriptions
    "DIGITAL_SOFTWARE": CategoryPolicy(
        category_code="DIGITAL_SOFTWARE",
        category_name="Digital Software License Keys",
        department="DIGITAL",
        return_window_days=0,
        is_final_sale=True,
        requires_original_packaging=False,
        inspection_checklist=["Verify activation server ledger status", "Confirm redemption timestamp"],
        common_defect_types=["KEY_ALREADY_REDEEMED", "REGION_LOCK_ERROR", "INVALID_LICENSE"],
    ),
    "DIGITAL_GIFT_CARDS": CategoryPolicy(
        category_code="DIGITAL_GIFT_CARDS",
        category_name="Electronic Gift Cards & Vouchers",
        department="DIGITAL",
        return_window_days=0,
        is_final_sale=True,
        requires_original_packaging=False,
        inspection_checklist=["Verify gift card balance ledger", "Check activation audit log"],
        common_defect_types=["DELIVERY_EMAIL_BOUNCED", "CODE_DEPLETED", "ACTIVATION_FAILED"],
    ),
}


class CategoryTaxonomyService:
    @staticmethod
    def get_category_policy(category_code: str) -> CategoryPolicy:
        return ENTERPRISE_CATEGORY_TAXONOMY.get(
            category_code,
            CategoryPolicy(
                category_code=category_code,
                category_name="General Merchandise",
                department="GENERAL",
                return_window_days=30,
            ),
        )

    @staticmethod
    def list_all_categories() -> List[CategoryPolicy]:
        return list(ENTERPRISE_CATEGORY_TAXONOMY.values())
