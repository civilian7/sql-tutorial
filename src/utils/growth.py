"""Yearly growth curve calculation"""

from __future__ import annotations

import random
from typing import Any


def get_daily_order_count(
    year: int,
    month: int,
    yearly_growth: dict[int, dict[str, Any]],
    monthly_seasonality: dict[int, float],
    scale: float,
    rng: random.Random,
) -> int:
    """Calculate the daily order count for a given year/month."""
    growth = yearly_growth[year]
    lo, hi = growth["orders_per_day"]
    base = rng.uniform(lo, hi)
    seasonal = monthly_seasonality.get(month, 1.0)
    return max(1, int(base * seasonal * scale))


def get_yearly_new_customers(
    year: int,
    yearly_growth: dict[int, dict[str, Any]],
    scale: float,
) -> int:
    """Return the number of new customers for the given year."""
    return max(1, int(yearly_growth[year]["new_customers"] * scale))


def get_yearly_active_products(
    year: int,
    yearly_growth: dict[int, dict[str, Any]],
    scale: float,
) -> int:
    """Return the number of active products for the given year."""
    return max(1, int(yearly_growth[year]["active_products"] * scale))
