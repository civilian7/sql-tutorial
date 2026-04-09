"""Review data generation"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


class ReviewGenerator(BaseGenerator):

    def generate_reviews(
        self, orders: list[dict], order_items: list[dict], products: list[dict],
    ) -> list[dict]:
        """Generate reviews for a portion of confirmed orders."""
        reviews = []
        review_id = 0
        write_rate = self.config["review"]["write_rate"]
        rating_dist = self.config["review"]["rating_distribution"]
        ratings = list(rating_dist.keys())
        weights = list(rating_dist.values())

        # Product ID -> brand mapping
        prod_brand = {p["id"]: p["brand"] for p in products}

        # order_id -> items mapping
        items_by_order: dict[int, list[dict]] = {}
        for it in order_items:
            items_by_order.setdefault(it["order_id"], []).append(it)

        confirmed = [o for o in orders if o["status"] == "confirmed"]

        for order in confirmed:
            if self.rng.random() >= write_rate:
                continue

            items = items_by_order.get(order["id"], [])
            if not items:
                continue

            item = self.rng.choice(items)
            review_id += 1

            rating = self.rng.choices(ratings, weights=weights, k=1)[0]
            if isinstance(rating, str):
                rating = int(rating)

            ordered_at = datetime.strptime(order["ordered_at"], "%Y-%m-%d %H:%M:%S")
            created = ordered_at + timedelta(days=self.rng.randint(3, 30))

            review_locale = self.locale["review"]
            titles_by_rating = review_locale["titles"]
            title = self.rng.choice(titles_by_rating[str(rating)]) if self.rng.random() < 0.8 else None

            # Generate dynamic review body
            brand = prod_brand.get(item["product_id"], "")
            content = self._make_content(rating, brand)

            reviews.append({
                "id": review_id,
                "product_id": item["product_id"],
                "customer_id": order["customer_id"],
                "order_id": order["id"],
                "rating": rating,
                "title": title,
                "content": content,
                "is_verified": 1,
                "created_at": self.fmt_dt(created),
                "updated_at": self.fmt_dt(created),
            })

        return reviews

    def _make_content(self, rating: int, brand: str) -> str | None:
        # ~10% chance of no content
        if self.rng.random() < 0.10:
            return None

        review_locale = self.locale["review"]
        templates_by_rating = review_locale["templates"]
        templates = templates_by_rating.get(str(rating), templates_by_rating["3"])
        tmpl = self.rng.choice(templates)
        return tmpl.format(
            brand=brand,
            period=self.rng.choice(review_locale["periods"]),
            minor_issue=self.rng.choice(review_locale["minor_issues"]),
        )
