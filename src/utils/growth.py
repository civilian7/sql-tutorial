"""연도별 성장 곡선 계산"""

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
    """해당 연/월의 일 주문 수를 계산한다."""
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
    """해당 연도의 신규 고객 수를 반환한다."""
    return max(1, int(yearly_growth[year]["new_customers"] * scale))


def get_yearly_active_products(
    year: int,
    yearly_growth: dict[int, dict[str, Any]],
    scale: float,
) -> int:
    """해당 연도의 활성 상품 수를 반환한다."""
    return max(1, int(yearly_growth[year]["active_products"] * scale))
