"""
International Business Hours SLA Calendar, Holiday Schedules & Timezone Shifts Engine.
"""

from datetime import datetime, time, timedelta, timezone
from typing import Dict, List, Set


# Standard Country Public Holiday Lists (Month, Day)
HOLIDAYS_CALENDAR: Dict[str, Set[str]] = {
    "US": {"01-01", "01-19", "02-16", "05-25", "06-19", "07-04", "09-07", "10-12", "11-11", "11-26", "12-25"},
    "GB": {"01-01", "04-03", "04-06", "05-04", "05-25", "08-31", "12-25", "12-26"},
    "CA": {"01-01", "02-16", "04-03", "05-18", "07-01", "09-07", "10-12", "11-11", "12-25", "12-26"},
    "AU": {"01-01", "01-26", "04-03", "04-06", "04-25", "06-08", "10-05", "12-25", "12-26"},
    "DE": {"01-01", "04-03", "04-06", "05-01", "05-14", "05-25", "10-03", "12-25", "12-26"},
}


class BusinessCalendarEngine:
    BUSINESS_START_HOUR = 8   # 8:00 AM
    BUSINESS_END_HOUR = 18    # 6:00 PM (10 hours per day)

    @staticmethod
    def is_business_day(dt: datetime, country_code: str = "US") -> bool:
        # Weekend check (5 = Saturday, 6 = Sunday)
        if dt.weekday() in (5, 6):
            return False
        
        # Holiday check
        date_str = dt.strftime("%m-%d")
        country_holidays = HOLIDAYS_CALENDAR.get(country_code.upper(), HOLIDAYS_CALENDAR["US"])
        return date_str not in country_holidays

    @staticmethod
    def add_business_hours(start_dt: datetime, business_hours: float, country_code: str = "US") -> datetime:
        """Calculates precise deadline adding only business operating hours."""
        current = start_dt
        remaining_hours = business_hours

        while remaining_hours > 0:
            # Advance to next business day if currently on weekend/holiday
            while not BusinessCalendarEngine.is_business_day(current, country_code):
                current = (current + timedelta(days=1)).replace(hour=BusinessCalendarEngine.BUSINESS_START_HOUR, minute=0, second=0)

            # Check if before opening hour
            if current.hour < BusinessCalendarEngine.BUSINESS_START_HOUR:
                current = current.replace(hour=BusinessCalendarEngine.BUSINESS_START_HOUR, minute=0, second=0)

            # Check if after closing hour
            if current.hour >= BusinessCalendarEngine.BUSINESS_END_HOUR:
                current = (current + timedelta(days=1)).replace(hour=BusinessCalendarEngine.BUSINESS_START_HOUR, minute=0, second=0)
                continue

            # Compute hours remaining in today's window
            closing_time = current.replace(hour=BusinessCalendarEngine.BUSINESS_END_HOUR, minute=0, second=0)
            hours_today = (closing_time - current).total_seconds() / 3600.0

            if remaining_hours <= hours_today:
                current = current + timedelta(hours=remaining_hours)
                remaining_hours = 0
            else:
                remaining_hours -= hours_today
                current = (current + timedelta(days=1)).replace(hour=BusinessCalendarEngine.BUSINESS_START_HOUR, minute=0, second=0)

        return current
