"""쿠폰 및 쿠폰 사용 이력 데이터 생성"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator




class CouponGenerator(BaseGenerator):

    def generate_coupons(self) -> list[dict]:
        """쿠폰 목록을 생성한다 (~200개)."""
        count = max(20, int(200 * self.scale))
        if count > 500:
            count = 500
        coupons = []

        for i in range(1, count + 1):
            coupon_type = self.rng.choice(["percent", "fixed"])
            if coupon_type == "percent":
                discount_value = self.rng.choice([5, 10, 15, 20, 30])
                max_discount = self.rng.choice([10000, 30000, 50000, 100000])
            else:
                discount_value = self.rng.choice([3000, 5000, 10000, 20000, 50000])
                max_discount = None

            min_order = self.rng.choice([None, 30000, 50000, 100000, 200000, 500000])

            start_year = self.rng.randint(self.start_year, self.end_year)
            started_at = self.random_date_in_year(start_year)
            duration = self.rng.choice([30, 60, 90, 180, 365])
            expired_at = started_at + timedelta(days=duration)

            name = self.rng.choice(self.locale["coupon"]["names"])
            code = f"CP{start_year % 100:02d}{i:04d}"

            coupons.append({
                "id": i,
                "code": code,
                "name": name,
                "type": coupon_type,
                "discount_value": discount_value,
                "min_order_amount": min_order,
                "max_discount": max_discount,
                "usage_limit": self.rng.choice([None, 100, 500, 1000, 5000]),
                "per_user_limit": self.rng.choice([1, 1, 1, 2, 3]),
                "is_active": 1 if expired_at > datetime(self.end_year, 6, 1) else 0,
                "started_at": self.fmt_dt(started_at),
                "expired_at": self.fmt_dt(expired_at),
                "created_at": self.fmt_dt(started_at - timedelta(days=self.rng.randint(1, 7))),
            })

        return coupons

    def generate_coupon_usage(
        self, coupons: list[dict], orders: list[dict],
    ) -> list[dict]:
        """쿠폰 사용 이력을 생성한다."""
        rows = []
        usage_id = 0
        target_count = max(100, int(50000 * self.scale))

        confirmed_orders = [o for o in orders if o["status"] in ("confirmed", "delivered")]
        if not confirmed_orders or not coupons:
            return rows

        for _ in range(min(target_count, len(confirmed_orders))):
            order = self.rng.choice(confirmed_orders)
            coupon = self.rng.choice(coupons)

            ordered_at = datetime.strptime(order["ordered_at"], "%Y-%m-%d %H:%M:%S")
            coupon_start = datetime.strptime(coupon["started_at"], "%Y-%m-%d %H:%M:%S")
            coupon_end = datetime.strptime(coupon["expired_at"], "%Y-%m-%d %H:%M:%S")

            if not (coupon_start <= ordered_at <= coupon_end):
                continue

            usage_id += 1
            if coupon["type"] == "percent":
                disc = order["total_amount"] * coupon["discount_value"] / 100
                if coupon["max_discount"]:
                    disc = min(disc, coupon["max_discount"])
            else:
                disc = coupon["discount_value"]
            disc = min(disc, order["total_amount"])

            rows.append({
                "id": usage_id,
                "coupon_id": coupon["id"],
                "customer_id": order["customer_id"],
                "order_id": order["id"],
                "discount_amount": round(disc, 2),
                "used_at": order["ordered_at"],
            })

        return rows
