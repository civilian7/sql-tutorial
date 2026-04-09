"""Common base class for generators"""

from __future__ import annotations

import json
import os
import random
from datetime import datetime, timedelta
from typing import Any

from faker import Faker


def load_locale(locale_code: str) -> dict:
    """Load a locale data file."""
    # ko_KR → ko, en_US → en
    short = locale_code.split("_")[0]
    locale_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "locale")
    path = os.path.join(locale_dir, f"{short}.json")
    if not os.path.exists(path):
        path = os.path.join(locale_dir, "en.json")  # fallback
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class BaseGenerator:
    """Base class for all generators."""

    def __init__(self, config: dict[str, Any], seed: int = 42):
        self.config = config
        self.seed = seed
        self.rng = random.Random(seed)
        self.scale = config["profiles"][config["size"]]["scale"]
        self.start_year = config["start_year"]
        self.end_year = config["end_year"]
        # Day-level date range (set by _resolve_date_range in generate.py)
        self.start_date = config.get("_start_dt", datetime(self.start_year, 1, 1))
        self.end_date = config.get("_end_dt", datetime(self.end_year, 12, 31))

        # Load locale
        locale_code = config.get("locale", "ko_KR")
        self.locale = load_locale(locale_code)
        faker_locale = self.locale.get("faker_locale", locale_code)
        self.fake = Faker(faker_locale)
        Faker.seed(seed)

    def detail(self, key: str, default=None):
        """Read a value from config with dot-path support.

        Lookup order: config (top-level merged with detailed).
        Example: self.detail("customer.dormancy_rates.under_1year", 0.05)
        """
        parts = key.split(".")
        node = self.config
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return default
        return node

    def random_datetime(self, start: datetime, end: datetime) -> datetime:
        """Return a random datetime between start and end."""
        delta = end - start
        seconds = int(delta.total_seconds())
        if seconds <= 0:
            return start
        return start + timedelta(seconds=self.rng.randint(0, seconds))

    def random_date_in_year(self, year: int) -> datetime:
        """Return a random date within the given year."""
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31, 23, 59, 59)
        if year == self.end_year:
            end = min(end, datetime(year, 12, 31))
        return self.random_datetime(start, end)

    def weighted_choice(self, weights: dict[str, float]) -> str:
        """Randomly select from a weighted dictionary."""
        keys = list(weights.keys())
        vals = list(weights.values())
        return self.rng.choices(keys, weights=vals, k=1)[0]

    def fmt_dt(self, dt: datetime) -> str:
        """Convert a datetime to an ISO format string."""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def fmt_date(self, dt: datetime) -> str:
        """Convert a datetime to a date string."""
        return dt.strftime("%Y-%m-%d")

    def generate_phone(self) -> str:
        """Generate a fake phone number matching the locale."""
        fmt = self.locale["phone"]["format"]
        return fmt.format(self.rng.randint(0, 9999), self.rng.randint(0, 9999))
