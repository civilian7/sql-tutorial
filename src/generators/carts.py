"""Cart data generation"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


class CartGenerator(BaseGenerator):

    def generate_carts(
        self, customers: list[dict], products: list[dict],
    ) -> tuple[list[dict], list[dict]]:
        """Generate carts and cart items."""
        carts = []
        cart_items = []
        cart_id = 0
        item_id = 0

        target_carts = max(100, int(30000 * self.scale))
        active_customers = [c for c in customers if c["is_active"]]
        if not active_customers or not products:
            return carts, cart_items

        for _ in range(target_carts):
            cart_id += 1
            customer = self.rng.choice(active_customers)
            created = datetime.strptime(customer["created_at"], "%Y-%m-%d %H:%M:%S")
            cart_created = self.random_datetime(
                created, self.end_date
            )

            status = self.rng.choices(
                ["active", "converted", "abandoned"],
                weights=[0.2, 0.5, 0.3],
                k=1,
            )[0]

            carts.append({
                "id": cart_id,
                "customer_id": customer["id"],
                "status": status,
                "created_at": self.fmt_dt(cart_created),
                "updated_at": self.fmt_dt(cart_created + timedelta(hours=self.rng.randint(0, 72))),
            })

            # 1~5 items per cart
            num_items = self.rng.randint(1, 5)
            for _ in range(num_items):
                item_id += 1
                product = self.rng.choice(products)
                cart_items.append({
                    "id": item_id,
                    "cart_id": cart_id,
                    "product_id": product["id"],
                    "quantity": self.rng.choices([1, 2, 3], weights=[0.7, 0.2, 0.1], k=1)[0],
                    "added_at": self.fmt_dt(cart_created + timedelta(minutes=self.rng.randint(0, 120))),
                })

        return carts, cart_items
