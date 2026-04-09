"""Wishlist data generation — for M:N relationship learning"""

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
        """Generate wishlists. Some convert to purchases, some remain unbought."""
        rows = []
        wish_id = 0
        used_pairs: set[tuple[int, int]] = set()

        active_customers = [c for c in customers if c["is_active"]]
        active_products = [p for p in products if p["is_active"]]
        if not active_customers or not active_products:
            return rows

        # Order history: purchased products per customer + order date
        # {customer_id: {product_id: earliest_ordered_at}}
        purchased: dict[int, dict[int, datetime]] = {}
        items_by_order: dict[int, list[dict]] = {}
        for it in order_items:
            items_by_order.setdefault(it["order_id"], []).append(it)
        for o in orders:
            if o["status"] in ("confirmed", "delivered"):
                ordered_at = datetime.strptime(o["ordered_at"], "%Y-%m-%d %H:%M:%S")
                cid = o["customer_id"]
                if cid not in purchased:
                    purchased[cid] = {}
                for it in items_by_order.get(o["id"], []):
                    pid = it["product_id"]
                    if pid not in purchased[cid] or ordered_at < purchased[cid][pid]:
                        purchased[cid][pid] = ordered_at

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

            # Purchase conversion — 40% chance to set as wishlisted-before-purchase if order history exists
            cust_purchased = purchased.get(customer["id"], {})
            bought_at = cust_purchased.get(product["id"])
            if bought_at is not None and bought_at > cust_created and self.rng.random() < 0.40:
                # Wishlist-to-purchase case: wishlisted 1~30 days before purchase
                days_before = self.rng.randint(1, 30)
                wished_at = bought_at - timedelta(days=days_before)
                if wished_at < cust_created:
                    wished_at = cust_created + timedelta(hours=self.rng.randint(1, 48))
                is_purchased = 1
            else:
                wished_at = self.random_datetime(
                    cust_created,
                    self.end_date,
                )
                is_purchased = 0

            # Notification setting (price drop alert)
            notify_on_sale = 1 if self.rng.random() < 0.30 else 0

            rows.append({
                "id": wish_id,
                "customer_id": customer["id"],
                "product_id": product["id"],
                "is_purchased": is_purchased,
                "notify_on_sale": notify_on_sale,
                "created_at": self.fmt_dt(wished_at),
            })

        return rows
