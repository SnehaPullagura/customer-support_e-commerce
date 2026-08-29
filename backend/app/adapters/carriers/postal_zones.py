"""
Postal Zone Matrix, Dimensional Weight Calculations, and Transit Routing Tables.
"""

from typing import Dict, Tuple, List, Optional


# US Postal 3-Digit Prefix to Major Shipping Zone Mapping (From Memphis / Central Hub)
US_POSTAL_ZONE_MATRIX: Dict[str, int] = {
    # Zone 2: 0-150 miles
    "380": 2, "381": 2, "386": 2, "370": 2, "371": 2, "372": 2, "720": 2, "721": 2, "722": 2,
    # Zone 3: 151-300 miles
    "350": 3, "351": 3, "352": 3, "630": 3, "631": 3, "633": 3, "400": 3, "401": 3, "402": 3,
    # Zone 4: 301-600 miles
    "300": 4, "301": 4, "302": 4, "303": 4, "430": 4, "431": 4, "432": 4, "606": 4, "607": 4,
    "750": 4, "751": 4, "752": 4, "753": 4, "770": 4, "771": 4, "772": 4, "787": 4,
    # Zone 5: 601-1000 miles
    "100": 5, "101": 5, "102": 5, "190": 5, "191": 5, "200": 5, "331": 5, "328": 5, "554": 5,
    # Zone 6: 1001-1400 miles
    "800": 6, "801": 6, "802": 6, "850": 6, "851": 6, "852": 6, "841": 6,
    # Zone 7: 1401-1800 miles
    "900": 7, "901": 7, "902": 7, "941": 7, "942": 7, "981": 7, "982": 7, "972": 7,
    # Zone 8: 1801+ miles (Remote, Hawaii, Alaska)
    "995": 8, "996": 8, "967": 8, "968": 8, "006": 8, "007": 8, "008": 8, "009": 8,
}


class DimensionalWeightCalculator:
    """Calculates carrier dimensional weight using standard commercial divisors."""

    @staticmethod
    def calculate_dim_weight(
        length_in: float, width_in: float, height_in: float, divisor: float = 139.0
    ) -> float:
        """
        Calculates DIM weight in lbs.
        Domestic commercial divisor standard: 139.
        Retail divisor standard: 166.
        """
        volume = length_in * width_in * height_in
        return round(volume / divisor, 2)

    @staticmethod
    def get_billable_weight(
        actual_weight_lbs: float, length_in: float, width_in: float, height_in: float, divisor: float = 139.0
    ) -> float:
        dim_w = DimensionalWeightCalculator.calculate_dim_weight(length_in, width_in, height_in, divisor)
        return max(actual_weight_lbs, dim_w)


class ZoneRouter:
    @staticmethod
    def determine_us_zone(origin_zip: str, destination_zip: str) -> int:
        dest_prefix = destination_zip.strip()[:3]
        return US_POSTAL_ZONE_MATRIX.get(dest_prefix, 5)

    @staticmethod
    def estimate_ground_transit_days(zone: int) -> int:
        if zone <= 2:
            return 1
        elif zone <= 4:
            return 2
        elif zone <= 6:
            return 3
        elif zone == 7:
            return 4
        else:
            return 5
