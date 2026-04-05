"""제너레이터 공통 베이스 클래스"""

from __future__ import annotations

import json
import os
import random
from datetime import datetime, timedelta
from typing import Any

from faker import Faker


def load_locale(locale_code: str) -> dict:
    """로케일 데이터 파일을 로드한다."""
    # ko_KR → ko, en_US → en
    short = locale_code.split("_")[0]
    locale_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "locale")
    path = os.path.join(locale_dir, f"{short}.json")
    if not os.path.exists(path):
        path = os.path.join(locale_dir, "en.json")  # fallback
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class BaseGenerator:
    """모든 제너레이터의 베이스 클래스."""

    def __init__(self, config: dict[str, Any], seed: int = 42):
        self.config = config
        self.seed = seed
        self.rng = random.Random(seed)
        self.scale = config["profiles"][config["size"]]["scale"]
        self.start_year = config["start_year"]
        self.end_year = config["end_year"]

        # 로케일 로드
        locale_code = config.get("locale", "ko_KR")
        self.locale = load_locale(locale_code)
        faker_locale = self.locale.get("faker_locale", locale_code)
        self.fake = Faker(faker_locale)
        Faker.seed(seed)

    def random_datetime(self, start: datetime, end: datetime) -> datetime:
        """start ~ end 사이의 랜덤 datetime을 반환한다."""
        delta = end - start
        seconds = int(delta.total_seconds())
        if seconds <= 0:
            return start
        return start + timedelta(seconds=self.rng.randint(0, seconds))

    def random_date_in_year(self, year: int) -> datetime:
        """해당 연도 내 랜덤 날짜를 반환한다."""
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31, 23, 59, 59)
        if year == self.end_year:
            end = min(end, datetime(year, 12, 31))
        return self.random_datetime(start, end)

    def weighted_choice(self, weights: dict[str, float]) -> str:
        """가중치 딕셔너리에서 랜덤 선택한다."""
        keys = list(weights.keys())
        vals = list(weights.values())
        return self.rng.choices(keys, weights=vals, k=1)[0]

    def fmt_dt(self, dt: datetime) -> str:
        """datetime을 ISO 형식 문자열로 변환한다."""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def fmt_date(self, dt: datetime) -> str:
        """datetime을 date 문자열로 변환한다."""
        return dt.strftime("%Y-%m-%d")

    def generate_phone(self) -> str:
        """로케일에 맞는 가상 전화번호를 생성한다."""
        fmt = self.locale["phone"]["format"]
        return fmt.format(self.rng.randint(0, 9999), self.rng.randint(0, 9999))
