"""Product view (browsing) log generator for funnel/session analysis."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


class ProductViewGenerator(BaseGenerator):

    def generate_product_views(
        self,
        customers: list[dict],
        products: list[dict],
        orders: list[dict],
        order_items: list[dict],
    ) -> list[dict]:
        """Generate product view logs.

        Patterns:
        - Customers browse 5-50x more than they order
        - Views cluster into sessions (multiple views within 30 min)
        - Products that were ordered always have prior views
        - Referrer sources: direct/search/ad/recommendation/social
        """
        rows = []
        view_id = 0

        cfg = self.config.get("product_views", {})
        views_per_order = cfg.get("views_per_order", 8)
        session_gap_minutes = cfg.get("session_gap_minutes", 30)
        target_count = max(500, int(len(orders) * views_per_order))

        referrer_sources = ["direct", "search", "ad", "recommendation", "social", "email"]
        referrer_weights = [0.20, 0.35, 0.15, 0.15, 0.10, 0.05]
        device_types = ["desktop", "mobile", "tablet"]
        device_weights = [0.45, 0.45, 0.10]

        active_customers = [c for c in customers if c["is_active"]]
        active_products = [p for p in products if p["is_active"]]
        if not active_customers or not active_products:
            return rows

        # Pre-build: customer creation dates
        cust_created = {}
        for c in active_customers:
            cust_created[c["id"]] = datetime.strptime(c["created_at"], "%Y-%m-%d %H:%M:%S")

        # Price-based product weights (cheaper = more views)
        prod_weights = []
        for p in active_products:
            if p["price"] <= 100000:
                prod_weights.append(4.0)
            elif p["price"] <= 500000:
                prod_weights.append(3.0)
            elif p["price"] <= 1500000:
                prod_weights.append(2.0)
            else:
                prod_weights.append(1.0)

        # Phase 1: Generate views for actual orders (ensures funnel data)
        items_by_order: dict[int, list[dict]] = {}
        for it in order_items:
            items_by_order.setdefault(it["order_id"], []).append(it)

        for o in orders:
            if o["status"] == "cancelled":
                if self.rng.random() > 0.3:
                    continue
            ordered_at = datetime.strptime(o["ordered_at"], "%Y-%m-%d %H:%M:%S")
            items = items_by_order.get(o["id"], [])

            for it in items:
                # 1-5 views before purchase, spread over 1-14 days before order
                num_pre_views = self.rng.randint(1, 5)
                for v in range(num_pre_views):
                    view_id += 1
                    days_before = self.rng.randint(0, 14)
                    minutes_before = self.rng.randint(0, 1440)
                    viewed_at = ordered_at - timedelta(days=days_before, minutes=minutes_before)
                    cc = cust_created.get(o["customer_id"])
                    if cc and viewed_at < cc:
                        viewed_at = cc + timedelta(minutes=self.rng.randint(1, 60))

                    duration = self.rng.randint(5, 300)

                    rows.append({
                        "id": view_id,
                        "customer_id": o["customer_id"],
                        "product_id": it["product_id"],
                        "referrer_source": self.rng.choices(referrer_sources, weights=referrer_weights, k=1)[0],
                        "device_type": self.rng.choices(device_types, weights=device_weights, k=1)[0],
                        "duration_seconds": duration,
                        "viewed_at": self.fmt_dt(viewed_at),
                    })

            if len(rows) >= target_count:
                break

        # Phase 2: Random browsing (no purchase)
        remaining = target_count - len(rows)
        end_dt = self.end_date

        for _ in range(remaining):
            customer = self.rng.choice(active_customers)
            product = self.rng.choices(active_products, weights=prod_weights, k=1)[0]
            cc = cust_created.get(customer["id"])
            if not cc:
                continue

            viewed_at = self.random_datetime(cc, end_dt)
            view_id += 1

            # Session clustering: 30% chance to add 1-4 more views in same session
            session_views = [viewed_at]
            if self.rng.random() < 0.30:
                extra = self.rng.randint(1, 4)
                for _ in range(extra):
                    gap = timedelta(minutes=self.rng.randint(1, session_gap_minutes))
                    session_views.append(session_views[-1] + gap)

            for sv in session_views:
                if sv > end_dt:
                    break
                if view_id > 1 and sv != session_views[0]:
                    view_id += 1
                    product = self.rng.choices(active_products, weights=prod_weights, k=1)[0]

                duration = self.rng.randint(3, 180)
                rows.append({
                    "id": view_id,
                    "customer_id": customer["id"],
                    "product_id": product["id"],
                    "referrer_source": self.rng.choices(referrer_sources, weights=referrer_weights, k=1)[0],
                    "device_type": self.rng.choices(device_types, weights=device_weights, k=1)[0],
                    "duration_seconds": duration,
                    "viewed_at": self.fmt_dt(sv),
                })

        # Sort by viewed_at for realistic ordering
        rows.sort(key=lambda r: r["viewed_at"])
        # Re-assign sequential IDs
        for i, r in enumerate(rows, start=1):
            r["id"] = i

        return rows
