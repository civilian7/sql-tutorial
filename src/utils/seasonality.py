"""계절성 패턴 유틸리티"""

from __future__ import annotations


DEFAULT_SEASONALITY: dict[int, float] = {
    1: 0.85, 2: 0.90, 3: 1.15, 4: 1.00,
    5: 0.95, 6: 0.90, 7: 0.85, 8: 1.05,
    9: 1.10, 10: 1.05, 11: 1.25, 12: 1.20,
}


def get_seasonality(month: int, config_seasonality: dict[int, float] | None = None) -> float:
    """월별 계절성 계수를 반환한다."""
    s = config_seasonality or DEFAULT_SEASONALITY
    return s.get(month, 1.0)
