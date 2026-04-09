"""Shipping data generation"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


class ShippingGenerator(BaseGenerator):

    def generate_shipping(self, orders: list[dict]) -> list[dict]:
        """Generate shipping data per order."""
        rows = []
        ship_id = 0
        carriers = self.locale["shipping"]["carriers"]

        for order in orders:
            if order["status"] in ("pending", "cancelled"):
                continue

            ship_id += 1
            carrier = self.weighted_choice(carriers)
            ordered_at = datetime.strptime(order["ordered_at"], "%Y-%m-%d %H:%M:%S")

            if order["status"] in ("paid", "preparing"):
                status = "preparing"
                shipped_at = None
                delivered_at = None
                tracking = None
            elif order["status"] == "shipped":
                status = "in_transit"
                shipped_at = self.fmt_dt(ordered_at + timedelta(days=self.rng.randint(1, 3)))
                delivered_at = None
                tracking = self._gen_tracking(carrier)
            elif order["status"] in ("delivered", "confirmed"):
                status = "delivered"
                ship_days = self.rng.randint(1, 3)
                ship_dt = ordered_at + timedelta(days=ship_days)
                deliver_days = self.rng.randint(1, 4)  # 1~4 days after dispatch
                shipped_at = self.fmt_dt(ship_dt)
                delivered_at = self.fmt_dt(ship_dt + timedelta(days=deliver_days))
                tracking = self._gen_tracking(carrier)
            elif order["status"] in ("return_requested", "returned"):
                status = "returned"
                ship_days = self.rng.randint(1, 3)
                ship_dt = ordered_at + timedelta(days=ship_days)
                deliver_days = self.rng.randint(1, 4)
                shipped_at = self.fmt_dt(ship_dt)
                delivered_at = self.fmt_dt(ship_dt + timedelta(days=deliver_days))
                tracking = self._gen_tracking(carrier)
            else:
                continue

            rows.append({
                "id": ship_id,
                "order_id": order["id"],
                "carrier": carrier,
                "tracking_number": tracking,
                "status": status,
                "shipped_at": shipped_at,
                "delivered_at": delivered_at,
                "created_at": order["created_at"],
                "updated_at": order["updated_at"],
            })

        return rows

    def _gen_tracking(self, carrier: str) -> str:
        num = self.rng.randint(100000000000, 999999999999)
        return str(num)
