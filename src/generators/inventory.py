"""Inventory and stock movement history data generation"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


class InventoryGenerator(BaseGenerator):

    def generate_inventory(
        self,
        products: list[dict],
        orders: list[dict],
        order_items: list[dict],
    ) -> list[dict]:
        """Generate stock movement history."""
        rows = []
        inv_id = 0

        # Initial stock receipt per product
        for p in products:
            inv_id += 1
            created = datetime.strptime(p["created_at"], "%Y-%m-%d %H:%M:%S")
            initial_qty = self.rng.randint(50, 500)
            rows.append({
                "id": inv_id,
                "product_id": p["id"],
                "type": "inbound",
                "quantity": initial_qty,
                "reference_id": None,
                "notes": "초기 입고",
                "created_at": self.fmt_dt(created),
            })

            # 1~5 additional restocks
            for _ in range(self.rng.randint(1, 5)):
                inv_id += 1
                restock_date = self.random_datetime(
                    created + timedelta(days=30),
                    self.end_date,
                )
                rows.append({
                    "id": inv_id,
                    "product_id": p["id"],
                    "type": "inbound",
                    "quantity": self.rng.randint(20, 300),
                    "reference_id": None,
                    "notes": "정기 입고",
                    "created_at": self.fmt_dt(restock_date),
                })

        # Order-based outbound (sampled -- recording all orders would be too many)
        items_by_order: dict[int, list[dict]] = {}
        for it in order_items:
            items_by_order.setdefault(it["order_id"], []).append(it)

        sampled_orders = self.rng.sample(
            [o for o in orders if o["status"] not in ("pending", "cancelled")],
            k=min(len(orders) // 5, int(50000 * self.scale)),
        )

        for order in sampled_orders:
            items = items_by_order.get(order["id"], [])
            for item in items:
                inv_id += 1
                rows.append({
                    "id": inv_id,
                    "product_id": item["product_id"],
                    "type": "outbound",
                    "quantity": -item["quantity"],
                    "reference_id": order["id"],
                    "notes": None,
                    "created_at": order["ordered_at"],
                })

        # Return inbound
        returned_orders = [o for o in orders if o["status"] == "returned"]
        for order in returned_orders:
            items = items_by_order.get(order["id"], [])
            for item in items:
                inv_id += 1
                ordered = datetime.strptime(order["ordered_at"], "%Y-%m-%d %H:%M:%S")
                rows.append({
                    "id": inv_id,
                    "product_id": item["product_id"],
                    "type": "return",
                    "quantity": item["quantity"],
                    "reference_id": order["id"],
                    "notes": "반품 입고",
                    "created_at": self.fmt_dt(ordered + timedelta(days=self.rng.randint(10, 30))),
                })

        return rows
