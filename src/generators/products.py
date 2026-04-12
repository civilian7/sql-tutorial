"""Product/category/supplier data generation"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator
from src.utils.growth import get_yearly_active_products


class ProductGenerator(BaseGenerator):

    def __init__(self, config: dict[str, Any], seed: int = 42):
        super().__init__(config, seed)
        data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        with open(os.path.join(data_dir, "categories.json"), encoding="utf-8") as f:
            self.category_data = json.load(f)
        with open(os.path.join(data_dir, "suppliers.json"), encoding="utf-8") as f:
            self.supplier_data = json.load(f)
        with open(os.path.join(data_dir, "products.json"), encoding="utf-8") as f:
            self.product_data = json.load(f)
        self._slug_to_cat = {c["slug"]: c for c in self.category_data}

    def generate_categories(self) -> list[dict]:
        """Return category list (based on data/categories.json)."""
        now = self.fmt_dt(datetime(self.start_year, 1, 1, 0, 0, 0))
        locale_cats = self.locale.get("categories", {})
        rows = []
        for c in self.category_data:
            name = locale_cats.get(str(c["id"]), c["name"])
            rows.append({
                "id": c["id"],
                "parent_id": c["parent_id"],
                "name": name,
                "slug": c["slug"],
                "depth": c["depth"],
                "sort_order": c["sort_order"],
                "is_active": 1,
                "created_at": now,
                "updated_at": now,
            })
        return rows

    def generate_suppliers(self) -> list[dict]:
        """Generate supplier list. ~10% of early suppliers are deactivated."""
        rows = []
        domain = self.locale["email"]["supplier_domain"]
        supplier_map = self.locale.get("suppliers", {})
        deactivation_cutoff = self.end_year - 3
        for s in self.supplier_data:
            created = self.random_datetime(
                datetime(self.start_year, 1, 1),
                datetime(self.start_year, 6, 30),
            )
            company_name = supplier_map.get(s["company_name"], s["company_name"])
            slug = re.sub(r"[^a-z0-9]", "", s["company_name"].lower()[:20]) or f"supplier{s['id']}"

            # ~10% of suppliers created before (end_year - 3) become inactive
            is_active = 1
            if created.year < deactivation_cutoff and self.rng.random() < 0.10:
                is_active = 0

            rows.append({
                "id": s["id"],
                "company_name": company_name,
                "business_number": f"{self.rng.randint(100, 999):03d}-{self.rng.randint(10, 99):02d}-{self.rng.randint(10000, 99999):05d}",
                "contact_name": self.fake.name(),
                "phone": self.generate_phone(),
                "email": f"contact@{slug}.{domain}",
                "address": self.fake.address(),
                "is_active": is_active,
                "created_at": self.fmt_dt(created),
                "updated_at": self.fmt_dt(created),
            })
        return rows

    def generate_products(self, suppliers: list[dict] | None = None) -> list[dict]:
        """Generate product list. Products are added according to yearly growth.

        If suppliers are provided, products from deactivated suppliers will
        also be discontinued.
        """
        templates = self.product_data["templates"]
        products = []
        product_id = 0

        # Build a set of inactive supplier IDs for cross-referencing
        inactive_supplier_ids: set[int] = set()
        if suppliers:
            inactive_supplier_ids = {s["id"] for s in suppliers if s["is_active"] == 0}

        target_by_year = {}
        for year in range(self.start_year, self.end_year + 1):
            target_by_year[year] = get_yearly_active_products(
                year, self.config["yearly_growth"], self.scale
            )

        # Add products as needed for each year
        for year in range(self.start_year, self.end_year + 1):
            target = target_by_year[year]
            needed = target - len(products)
            if needed <= 0:
                continue

            for _ in range(needed):
                tmpl = self.rng.choice(templates)
                product_id += 1
                cat = self._slug_to_cat.get(tmpl["category_slug"])
                if not cat:
                    continue

                name = self.rng.choice(tmpl["names"])
                # Add variants (capacity, color, etc.)
                variants = self.locale.get("product_variants", ["", " Black", " White", " Silver"])
                suffix = self.rng.choice(variants)
                name = name + suffix

                # Translate brand name if locale mapping exists
                brand_map = self.locale.get("brands", {})
                brand = brand_map.get(tmpl["brand"], tmpl["brand"])

                # Replace Korean words in product name with translations
                for ko, en in self.locale.get("product_name_replacements", {}).items():
                    if ko in name:
                        name = name.replace(ko, en)
                # Replace Korean prefixes with translated equivalents
                prefix_map = self.locale.get("product_name_prefixes", {})
                if prefix_map:
                    for ko_prefix, en_prefix in prefix_map.items():
                        if name.startswith(ko_prefix):
                            name = en_prefix + name[len(ko_prefix):]
                            break

                lo, hi = tmpl["price_range"]
                price = round(self.rng.uniform(lo, hi), -2)  # rounded to 100 KRW
                cost = round(price * tmpl["cost_ratio"], -2)

                created = self.random_date_in_year(year)
                sku = self._make_sku(cat["slug"], tmpl["brand"], product_id)
                weight = self.rng.randint(*tmpl["weight_range"]) if tmpl["weight_range"][1] > 0 else None

                # Discontinuation (20~30%)
                discontinued_at = None
                is_active = 1
                if self.rng.random() < 0.25 and year < self.end_year - 1:
                    disc_year = self.rng.randint(year + 1, self.end_year)
                    discontinued_at = self.fmt_dt(self.random_date_in_year(disc_year))
                    is_active = 0

                # Products from deactivated suppliers are also discontinued
                if tmpl["supplier_id"] in inactive_supplier_ids and discontinued_at is None:
                    disc_start = max(year + 1, self.end_year - 2)
                    if disc_start <= self.end_year:
                        disc_year = self.rng.randint(disc_start, self.end_year)
                    else:
                        disc_year = self.end_year
                    discontinued_at = self.fmt_dt(self.random_date_in_year(disc_year))
                    is_active = 0

                # Generate category-specific specs as JSON
                specs = self._generate_specs(cat["slug"], tmpl, product_id)

                # Long product name edge case (1%)
                desc_suffix = self.locale.get("product_desc_suffix", "High performance, latest technology")
                description = f"{brand} {name} - {desc_suffix}"
                if self.rng.random() < self.config["edge_cases"]["long_product_name"]:
                    extras = self.locale.get("product_long_suffix", [
                        "고급 알루미늄 합금 바디 적용, 프리미엄 패키지 구성",
                        "무상 보증 3년 연장 + 전용 파우치 증정 이벤트",
                        "전문가 추천 모델, 업계 최고 성능 인증 획득",
                        "저소음 설계, 에너지 효율 1등급, 친환경 포장",
                        "RGB 라이팅 탑재, 소프트웨어 커스터마이징 지원",
                    ])
                    ltd_label = self.locale.get("product_limited_label", "[Special Limited Edition]")
                    name = name + " " + ltd_label + " " + self.rng.choice(extras)

                products.append({
                    "id": product_id,
                    "category_id": cat["id"],
                    "supplier_id": tmpl["supplier_id"],
                    "successor_id": None,
                    "name": name,
                    "sku": sku,
                    "brand": brand,
                    "model_number": f"{tmpl['brand'][:3].upper()}-{product_id:05d}",
                    "description": description,
                    "specs": specs,
                    "price": price,
                    "cost_price": cost,
                    "stock_qty": self.rng.randint(0, 500),
                    "weight_grams": weight,
                    "is_active": is_active,
                    "discontinued_at": discontinued_at,
                    "created_at": self.fmt_dt(created),
                    "updated_at": self.fmt_dt(created),
                })

        # Assign successor_id: 30% of discontinued products get a successor
        # (a newer, non-discontinued product in the same category)
        by_category: dict[int, list[dict]] = {}
        for p in products:
            by_category.setdefault(p["category_id"], []).append(p)

        for p in products:
            if p["discontinued_at"] is None:
                continue
            if self.rng.random() >= 0.30:
                continue
            candidates = [
                c for c in by_category.get(p["category_id"], [])
                if c["id"] != p["id"]
                and c["discontinued_at"] is None
                and c["created_at"] > p["created_at"]
            ]
            if candidates:
                p["successor_id"] = self.rng.choice(candidates)["id"]

        # Sort by id so self-referencing FK (successor_id) inserts in safe order
        products.sort(key=lambda x: x["id"])

        return products

    def generate_product_prices(self, products: list[dict]) -> list[dict]:
        """Generate price history per product."""
        rows = []
        price_id = 0
        reasons = ["regular", "promotion", "price_drop", "cost_increase"]

        for p in products:
            created = datetime.strptime(p["created_at"], "%Y-%m-%d %H:%M:%S")
            current_price = p["price"]

            # Initial price
            price_id += 1
            rows.append({
                "id": price_id,
                "product_id": p["id"],
                "price": current_price,
                "started_at": p["created_at"],
                "ended_at": None,
                "change_reason": "regular",
            })

            # 1~4 price changes
            changes = self.rng.randint(0, 4)
            prev_start = created
            for i in range(changes):
                change_date = self.random_datetime(
                    prev_start + timedelta(days=30),
                    self.end_date,
                )
                if change_date <= prev_start:
                    break
                # End previous record
                rows[-1]["ended_at"] = self.fmt_dt(change_date)
                # -20% ~ +15% fluctuation
                ratio = self.rng.uniform(0.80, 1.15)
                new_price = round(current_price * ratio, -2)
                current_price = new_price
                price_id += 1
                rows.append({
                    "id": price_id,
                    "product_id": p["id"],
                    "price": new_price,
                    "started_at": self.fmt_dt(change_date),
                    "ended_at": None,
                    "change_reason": self.rng.choice(reasons),
                })
                prev_start = change_date

            # Sync products.price to the latest historical price
            p["price"] = current_price

        return rows

    def _generate_specs(self, slug: str, tmpl: dict, product_id: int) -> str | None:
        """Generate category-specific product specs as a JSON string.

        Returns None for categories without predefined spec templates.
        """
        specs: dict | None = None

        if slug.startswith("laptop"):
            specs = {
                "screen_size": self.rng.choice(["14 inch", "15.6 inch", "16 inch"]),
                "cpu": self.rng.choice([
                    "Intel Core i5-13500H", "Intel Core i7-13700H", "Intel Core i9-13900H",
                    "AMD Ryzen 5 7535HS", "AMD Ryzen 7 7735HS", "AMD Ryzen 9 7945HX",
                    "Apple M3", "Apple M3 Pro", "Apple M3 Max",
                ]),
                "ram": self.rng.choice(["8GB", "16GB", "32GB"]),
                "storage": self.rng.choice(["256GB", "512GB", "1024GB"]),
                "weight_kg": round(self.rng.uniform(1.2, 2.8), 1),
                "battery_hours": self.rng.randint(6, 15),
            }
        elif slug.startswith("desktop"):
            specs = {
                "cpu": self.rng.choice([
                    "Intel Core i5-13600K", "Intel Core i7-13700K", "Intel Core i9-13900K",
                    "AMD Ryzen 5 7600X", "AMD Ryzen 7 7700X", "AMD Ryzen 9 7950X",
                ]),
                "ram": self.rng.choice(["8GB", "16GB", "32GB", "64GB"]),
                "storage": self.rng.choice(["512GB", "1024GB", "2048GB"]),
                "gpu": self.rng.choice([
                    "NVIDIA RTX 4060", "NVIDIA RTX 4070", "NVIDIA RTX 4080",
                    "AMD Radeon RX 7600", "AMD Radeon RX 7800 XT",
                    "Intel Arc A770", "Integrated",
                ]),
            }
        elif slug.startswith("monitor"):
            specs = {
                "screen_size": self.rng.choice(["24 inch", "27 inch", "32 inch"]),
                "resolution": self.rng.choice(["FHD", "QHD", "4K"]),
                "refresh_rate": self.rng.choice([60, 75, 144, 165, 240]),
                "panel": self.rng.choice(["IPS", "VA", "OLED"]),
            }
        elif slug.startswith("gpu"):
            specs = {
                "vram": self.rng.choice(["8GB", "12GB", "16GB", "24GB"]),
                "clock_mhz": self.rng.randint(1500, 2500),
                "tdp_watts": self.rng.randint(150, 450),
            }
        elif slug.startswith("cpu"):
            cores = self.rng.choice([4, 6, 8, 12, 16, 24])
            specs = {
                "cores": cores,
                "threads": cores * 2,
                "base_clock_ghz": round(self.rng.uniform(2.5, 4.0), 1),
                "boost_clock_ghz": round(self.rng.uniform(4.5, 5.8), 1),
            }
        elif slug.startswith("ram"):
            ddr_type = self.rng.choice(["DDR4", "DDR5"])
            if ddr_type == "DDR4":
                speed = self.rng.choice([3200])
            else:
                speed = self.rng.choice([4800, 5600, 6000, 6400])
            specs = {
                "capacity_gb": self.rng.choice([8, 16, 32, 64]),
                "speed_mhz": speed,
                "type": ddr_type,
            }
        elif slug == "storage-ssd":
            interface = self.rng.choice(["NVMe", "SATA"])
            if interface == "NVMe":
                read_speed = self.rng.randint(3000, 7000)
                write_speed = self.rng.randint(2500, 6500)
            else:
                read_speed = self.rng.randint(500, 560)
                write_speed = self.rng.randint(400, 530)
            specs = {
                "capacity_gb": self.rng.choice([256, 512, 1024, 2048]),
                "interface": interface,
                "read_mbps": read_speed,
                "write_mbps": write_speed,
            }

        if specs is None:
            return None
        return json.dumps(specs)

    # Korean brand name -> ASCII code mapping
    _BRAND_CODES = {
        "삼성전자": "SAM", "LG전자": "LGE", "한성컴퓨터": "HSC",
        "주연테크": "JYT", "기가바이트": "GBT", "녹투아": "NOC",
        "레오폴드": "LEO", "시소닉": "SSN", "리안리": "LNL",
        "소니": "SNY", "보스": "BOS", "브라더": "BRO",
        "캐논": "CAN", "엡손": "EPS", "넷기어": "NGR",
        "안랩": "ALB", "카스퍼스키": "KSP", "SK하이닉스": "SKH",
        "한컴오피스": "HWP", "로지텍": "LOG",
    }

    def _make_sku(self, cat_slug: str, brand: str, pid: int) -> str:
        parts = cat_slug.split("-")
        prefix = parts[0][:2].upper() if parts else "XX"
        sub = parts[1][:3].upper() if len(parts) > 1 else ""
        brand_code = self._BRAND_CODES.get(brand, "")
        if not brand_code:
            # Extract ASCII characters only
            ascii_chars = "".join(c for c in brand if ord(c) < 128 and c.isalpha())
            brand_code = ascii_chars[:3].upper() or "ETC"
        return f"{prefix}-{sub}-{brand_code}-{pid:05d}" if sub else f"{prefix}-{brand_code}-{pid:05d}"
