"""Promotion/sale event generation.

Generates seasonal sales, flash sales, and category-specific promotions
with associated product mappings.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


# Recurring annual promotion templates
ANNUAL_PROMOTIONS = [
    {"name_ko": "새해 특가 세일", "name_en": "New Year Sale",
     "month": 1, "duration": 7, "type": "seasonal", "discount_type": "percent", "discount_value": 10},
    {"name_ko": "봄맞이 세일", "name_en": "Spring Sale",
     "month": 3, "duration": 14, "type": "seasonal", "discount_type": "percent", "discount_value": 15},
    {"name_ko": "신학기 노트북 특가", "name_en": "Back to School Laptop Sale",
     "month": 3, "duration": 21, "type": "category", "discount_type": "percent", "discount_value": 12,
     "categories": ["laptop-general", "laptop-gaming", "laptop-2in1", "laptop-macbook"]},
    {"name_ko": "여름 쿨링 페스티벌", "name_en": "Summer Cooling Festival",
     "month": 7, "duration": 14, "type": "category", "discount_type": "percent", "discount_value": 20,
     "categories": ["cooling-air", "cooling-liquid"]},
    {"name_ko": "추석 선물 세일", "name_en": "Autumn Gift Sale",
     "month": 9, "duration": 10, "type": "seasonal", "discount_type": "percent", "discount_value": 10},
    {"name_ko": "블랙프라이데이", "name_en": "Black Friday",
     "month": 11, "duration": 4, "type": "seasonal", "discount_type": "percent", "discount_value": 25},
    {"name_ko": "사이버먼데이", "name_en": "Cyber Monday",
     "month": 11, "duration": 1, "type": "seasonal", "discount_type": "percent", "discount_value": 30},
    {"name_ko": "연말 감사 세일", "name_en": "Year-End Thank You Sale",
     "month": 12, "duration": 14, "type": "seasonal", "discount_type": "percent", "discount_value": 15},
    {"name_ko": "게이밍 기어 페스타", "name_en": "Gaming Gear Festa",
     "month": 8, "duration": 7, "type": "category", "discount_type": "percent", "discount_value": 18,
     "categories": ["gpu-nvidia", "gpu-amd", "mouse-gaming", "keyboard-mechanical", "monitor-gaming"]},
    {"name_ko": "프린터 특가", "name_en": "Printer Special Deal",
     "month": 5, "duration": 10, "type": "category", "discount_type": "fixed", "discount_value": 30000,
     "categories": ["printer"]},
]


class PromotionGenerator(BaseGenerator):

    def generate_promotions(
        self, products: list[dict], categories: list[dict],
    ) -> tuple[list[dict], list[dict]]:
        """Generate promotions and promotion-product mappings."""
        promotions = []
        promo_products = []
        promo_id = 0

        locale_key = "name_en" if "en" in self.config.get("locale", "ko") else "name_ko"
        cat_slug_map = {c["id"]: c["slug"] for c in categories}

        # Products by category slug
        prods_by_slug: dict[str, list[dict]] = {}
        for p in products:
            slug = cat_slug_map.get(p["category_id"], "")
            prods_by_slug.setdefault(slug, []).append(p)

        all_active = [p for p in products if p["is_active"]]

        for year in range(self.start_year, self.end_year + 1):
            # Annual recurring promotions
            for tmpl in ANNUAL_PROMOTIONS:
                promo_id += 1
                start_day = self.rng.randint(1, 15)
                started_at = datetime(year, tmpl["month"], start_day)
                ended_at = started_at + timedelta(days=tmpl["duration"])

                promotions.append({
                    "id": promo_id,
                    "name": f"{tmpl[locale_key]} {year}",
                    "type": tmpl["type"],
                    "discount_type": tmpl["discount_type"],
                    "discount_value": tmpl["discount_value"],
                    "min_order_amount": 50000 if tmpl["discount_type"] == "fixed" else None,
                    "started_at": self.fmt_dt(started_at),
                    "ended_at": self.fmt_dt(ended_at),
                    "is_active": 1 if ended_at >= self.end_date else 0,
                    "created_at": self.fmt_dt(started_at - timedelta(days=self.rng.randint(3, 14))),
                })

                # Assign products to this promotion
                if tmpl["type"] == "category" and "categories" in tmpl:
                    # Category-specific: all products in target categories
                    target_prods = []
                    for slug in tmpl["categories"]:
                        target_prods.extend(prods_by_slug.get(slug, []))
                    for p in target_prods:
                        promo_products.append({
                            "promotion_id": promo_id,
                            "product_id": p["id"],
                            "override_price": None,
                        })
                else:
                    # Seasonal: random 30~60% of active products
                    count = int(len(all_active) * self.rng.uniform(0.3, 0.6))
                    selected = self.rng.sample(all_active, min(count, len(all_active)))
                    for p in selected:
                        promo_products.append({
                            "promotion_id": promo_id,
                            "product_id": p["id"],
                            "override_price": None,
                        })

            # 2~4 flash sales per year (random products, short duration)
            flash_count = self.rng.randint(2, 4)
            for _ in range(flash_count):
                promo_id += 1
                flash_month = self.rng.randint(1, 12)
                flash_day = self.rng.randint(1, 25)
                started_at = datetime(year, flash_month, flash_day)
                duration_hours = self.rng.choice([24, 48, 72])
                ended_at = started_at + timedelta(hours=duration_hours)

                promotions.append({
                    "id": promo_id,
                    "name": self._flash_sale_name(locale_key),
                    "type": "flash",
                    "discount_type": "percent",
                    "discount_value": self.rng.choice([20, 25, 30, 35, 40]),
                    "min_order_amount": None,
                    "started_at": self.fmt_dt(started_at),
                    "ended_at": self.fmt_dt(ended_at),
                    "is_active": 1 if ended_at >= self.end_date else 0,
                    "created_at": self.fmt_dt(started_at - timedelta(days=1)),
                })

                # Flash sale: 1~5 specific products with override price
                flash_prods = self.rng.sample(all_active, min(self.rng.randint(1, 5), len(all_active)))
                for p in flash_prods:
                    override = round(p["price"] * self.rng.uniform(0.5, 0.75), -2)
                    promo_products.append({
                        "promotion_id": promo_id,
                        "product_id": p["id"],
                        "override_price": override,
                    })

        return promotions, promo_products

    def _flash_sale_name(self, locale_key: str) -> str:
        if "en" in locale_key:
            templates = ["Lightning Deal", "Flash Sale", "Deal of the Day",
                         "Time-Limited Special", "Surprise Deal"]
        else:
            templates = ["번개 특가", "타임딜", "오늘의 특가",
                         "한정 시간 세일", "깜짝 특가"]
        return self.rng.choice(templates)
