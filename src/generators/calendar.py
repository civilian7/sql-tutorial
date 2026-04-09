"""Date dimension table generation -- for CROSS JOIN practice.

Holidays are fictional/generic (not country-specific) with locale-based names.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


# Default fictional holidays (used if locale has no "holidays" key)
DEFAULT_HOLIDAYS = {
    "01-01": "New Year's Day",
    "02-14": "Foundation Day",
    "03-21": "Spring Festival",
    "04-05": "Memorial Day",
    "05-01": "Labor Day",
    "05-15": "Children's Day",
    "06-10": "Summer Solstice Day",
    "07-20": "Freedom Day",
    "08-15": "Liberation Day",
    "09-22": "Harvest Festival",
    "10-03": "National Day",
    "10-31": "Remembrance Day",
    "11-15": "Gratitude Day",
    "12-25": "Winter Festival",
    "12-31": "Year End Holiday",
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def generate_calendar(start_date, end_date, locale: dict | None = None) -> list[dict]:
    """Generate a date dimension table for the given date range.

    start_date/end_date can be "YYYY-MM-DD" strings or int years.
    """
    if isinstance(start_date, int):
        start_date = f"{start_date}-01-01"
    if isinstance(end_date, int):
        end_date = f"{end_date}-12-31"

    holidays = DEFAULT_HOLIDAYS
    if locale and "holidays" in locale:
        holidays = locale["holidays"]

    rows = []
    d = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    while d <= end:
        is_weekend = 1 if d.weekday() >= 5 else 0
        key = f"{d.month:02d}-{d.day:02d}"
        holiday_name = holidays.get(key)

        rows.append({
            "date_key": d.isoformat(),
            "year": d.year,
            "month": d.month,
            "day": d.day,
            "quarter": (d.month - 1) // 3 + 1,
            "day_of_week": d.weekday(),
            "day_name": DAY_NAMES[d.weekday()],
            "is_weekend": is_weekend,
            "is_holiday": 1 if holiday_name else 0,
            "holiday_name": holiday_name,
        })
        d += timedelta(days=1)

    return rows
