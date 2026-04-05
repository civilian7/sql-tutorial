"""상품/카테고리/공급업체 데이터 생성"""

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
        """카테고리 목록을 반환한다 (data/categories.json 기반)."""
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
        """공급업체 목록을 생성한다."""
        rows = []
        domain = self.locale["email"]["supplier_domain"]
        for s in self.supplier_data:
            created = self.random_datetime(
                datetime(self.start_year, 1, 1),
                datetime(self.start_year, 6, 30),
            )
            slug = re.sub(r"[^a-z0-9]", "", s["company_name"].lower()[:20]) or f"supplier{s['id']}"
            rows.append({
                "id": s["id"],
                "company_name": s["company_name"],
                "business_number": f"{self.rng.randint(100, 999):03d}-{self.rng.randint(10, 99):02d}-{self.rng.randint(10000, 99999):05d}",
                "contact_name": self.fake.name(),
                "phone": self.generate_phone(),
                "email": f"contact@{slug}.{domain}",
                "address": self.fake.address(),
                "is_active": 1,
                "created_at": self.fmt_dt(created),
                "updated_at": self.fmt_dt(created),
            })
        return rows

    def generate_products(self) -> list[dict]:
        """상품 목록을 생성한다. 연도별 성장에 맞게 상품을 추가한다."""
        templates = self.product_data["templates"]
        products = []
        product_id = 0

        target_by_year = {}
        for year in range(self.start_year, self.end_year + 1):
            target_by_year[year] = get_yearly_active_products(
                year, self.config["yearly_growth"], self.scale
            )

        # 각 연도에 필요한 만큼 상품 추가
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
                # 변형 추가 (용량, 색상 등)
                variants = ["", " 블랙", " 화이트", " 실버"]
                suffix = self.rng.choice(variants)
                name = name + suffix

                lo, hi = tmpl["price_range"]
                price = round(self.rng.uniform(lo, hi), -2)  # 100원 단위
                cost = round(price * tmpl["cost_ratio"], -2)

                created = self.random_date_in_year(year)
                sku = self._make_sku(cat["slug"], tmpl["brand"], product_id)
                weight = self.rng.randint(*tmpl["weight_range"]) if tmpl["weight_range"][1] > 0 else None

                # 단종 여부 (20~30%)
                discontinued_at = None
                is_active = 1
                if self.rng.random() < 0.25 and year < self.end_year - 1:
                    disc_year = self.rng.randint(year + 1, self.end_year)
                    discontinued_at = self.fmt_dt(self.random_date_in_year(disc_year))
                    is_active = 0

                # 긴 상품명 엣지 케이스 (1%)
                description = f"{tmpl['brand']} {name} - 고성능, 최신 기술 탑재"
                if self.rng.random() < self.config["edge_cases"]["long_product_name"]:
                    name = name + " [특별 한정판 에디션] " + self.fake.text(max_nb_chars=200)

                products.append({
                    "id": product_id,
                    "category_id": cat["id"],
                    "supplier_id": tmpl["supplier_id"],
                    "name": name,
                    "sku": sku,
                    "brand": tmpl["brand"],
                    "model_number": f"{tmpl['brand'][:3].upper()}-{product_id:05d}",
                    "description": description,
                    "price": price,
                    "cost_price": cost,
                    "stock_qty": self.rng.randint(0, 500),
                    "weight_grams": weight,
                    "is_active": is_active,
                    "discontinued_at": discontinued_at,
                    "created_at": self.fmt_dt(created),
                    "updated_at": self.fmt_dt(created),
                })

        return products

    def generate_product_prices(self, products: list[dict]) -> list[dict]:
        """상품별 가격 이력을 생성한다."""
        rows = []
        price_id = 0
        reasons = ["regular", "promotion", "price_drop", "cost_increase"]

        for p in products:
            created = datetime.strptime(p["created_at"], "%Y-%m-%d %H:%M:%S")
            current_price = p["price"]

            # 초기 가격
            price_id += 1
            rows.append({
                "id": price_id,
                "product_id": p["id"],
                "price": current_price,
                "started_at": p["created_at"],
                "ended_at": None,
                "change_reason": "regular",
            })

            # 1~4회 가격 변동
            changes = self.rng.randint(0, 4)
            prev_start = created
            for i in range(changes):
                change_date = self.random_datetime(
                    prev_start + timedelta(days=30),
                    datetime(self.end_year, 12, 31),
                )
                if change_date <= prev_start:
                    break
                # 이전 레코드 종료
                rows[-1]["ended_at"] = self.fmt_dt(change_date)
                # -20% ~ +15% 변동
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

            # products.price를 마지막 이력가로 동기화
            p["price"] = current_price

        return rows

    # 한글 브랜드 → ASCII 코드 매핑
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
            # ASCII 문자만 추출
            ascii_chars = "".join(c for c in brand if ord(c) < 128 and c.isalpha())
            brand_code = ascii_chars[:3].upper() or "ETC"
        return f"{prefix}-{sub}-{brand_code}-{pid:05d}" if sub else f"{prefix}-{brand_code}-{pid:05d}"
