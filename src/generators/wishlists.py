"""위시리스트(찜) 데이터 생성 — M:N 관계 학습용"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


class WishlistGenerator(BaseGenerator):

    def generate_wishlists(
        self,
        customers: list[dict],
        products: list[dict],
        orders: list[dict],
        order_items: list[dict],
    ) -> list[dict]:
        """위시리스트를 생성한다. 일부는 구매 전환, 일부는 미구매 상태."""
        rows = []
        wish_id = 0
        used_pairs: set[tuple[int, int]] = set()

        active_customers = [c for c in customers if c["is_active"]]
        active_products = [p for p in products if p["is_active"]]
        if not active_customers or not active_products:
            return rows

        # 주문 이력: 고객별 구매 상품
        purchased: dict[int, set[int]] = {}
        items_by_order: dict[int, list[dict]] = {}
        for it in order_items:
            items_by_order.setdefault(it["order_id"], []).append(it)
        for o in orders:
            if o["status"] in ("confirmed", "delivered"):
                for it in items_by_order.get(o["id"], []):
                    purchased.setdefault(o["customer_id"], set()).add(it["product_id"])

        target_count = max(100, int(20000 * self.scale))

        for _ in range(target_count):
            customer = self.rng.choice(active_customers)
            product = self.rng.choice(active_products)
            pair = (customer["id"], product["id"])
            if pair in used_pairs:
                continue
            used_pairs.add(pair)

            wish_id += 1
            cust_created = datetime.strptime(customer["created_at"], "%Y-%m-%d %H:%M:%S")
            wished_at = self.random_datetime(
                cust_created,
                datetime(self.end_year, 6, 30),
            )

            # 구매 전환 여부 — 찜한 상품을 실제 구매했는지
            cust_purchased = purchased.get(customer["id"], set())
            if product["id"] in cust_purchased:
                is_purchased = 1
            else:
                # 찜만 하고 안 산 경우가 더 많음 (70%)
                is_purchased = 0

            # 알림 설정 (가격 하락 알림)
            notify_on_sale = 1 if self.rng.random() < 0.30 else 0

            rows.append({
                "id": wish_id,
                "customer_id": customer["id"],
                "product_id": product["id"],
                "notify_on_sale": notify_on_sale,
                "created_at": self.fmt_dt(wished_at),
            })

        return rows
