"""Point transaction history generation.

Generates a full ledger of point earn/use/expire/reward events:
- purchase: earned on order payment (1% of amount)
- confirm: bonus on purchase confirmation (500~1000P)
- review: reward for writing a review (300~500P text, 1000P with content)
- signup: welcome bonus on registration (3000~5000P)
- use: points used in an order (negative amount)
- expiry: unused points expired after 1 year (negative amount)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


class PointTransactionGenerator(BaseGenerator):

    def generate_point_transactions(
        self,
        customers: list[dict],
        orders: list[dict],
        reviews: list[dict],
    ) -> list[dict]:
        """Generate point transaction ledger."""
        rows = []
        tx_id = 0

        cfg = self.config.get("point_transactions", {})
        signup_bonus_range = cfg.get("signup_bonus_range", [3000, 5000])
        confirm_bonus_range = cfg.get("confirm_bonus_range", [500, 1000])
        review_reward_text = cfg.get("review_reward_text", 300)
        review_reward_content = cfg.get("review_reward_content", 500)
        expiry_days = cfg.get("expiry_days", 365)

        # Running balance per customer
        balance: dict[int, int] = {}

        # Collect all events with timestamps, then sort chronologically
        events: list[tuple[str, dict]] = []  # (timestamp, event_dict)

        # 1. Signup bonus for each customer
        for c in customers:
            bonus = self.rng.randint(*signup_bonus_range)
            events.append((c["created_at"], {
                "customer_id": c["id"],
                "order_id": None,
                "type": "earn",
                "reason": "signup",
                "amount": bonus,
                "expires_at": self._add_days(c["created_at"], expiry_days),
            }))

        # 2. Purchase earn + point usage from orders
        for o in orders:
            if o["status"] in ("cancelled",):
                continue

            # Point usage (debit)
            if o["point_used"] > 0:
                events.append((o["ordered_at"], {
                    "customer_id": o["customer_id"],
                    "order_id": o["id"],
                    "type": "use",
                    "reason": "use",
                    "amount": -o["point_used"],
                    "expires_at": None,
                }))

            # Purchase earn (credit)
            if o["point_earned"] > 0 and o["status"] in ("confirmed", "delivered", "shipped"):
                events.append((o["ordered_at"], {
                    "customer_id": o["customer_id"],
                    "order_id": o["id"],
                    "type": "earn",
                    "reason": "purchase",
                    "amount": o["point_earned"],
                    "expires_at": self._add_days(o["ordered_at"], expiry_days),
                }))

            # Confirmation bonus
            if o["status"] == "confirmed" and o["completed_at"]:
                bonus = self.rng.randint(*confirm_bonus_range)
                events.append((o["completed_at"], {
                    "customer_id": o["customer_id"],
                    "order_id": o["id"],
                    "type": "earn",
                    "reason": "confirm",
                    "amount": bonus,
                    "expires_at": self._add_days(o["completed_at"], expiry_days),
                }))

        # 3. Review rewards
        for r in reviews:
            reward = review_reward_content if r.get("content") else review_reward_text
            events.append((r["created_at"], {
                "customer_id": r["customer_id"],
                "order_id": r.get("order_id"),
                "type": "earn",
                "reason": "review",
                "amount": reward,
                "expires_at": self._add_days(r["created_at"], expiry_days),
            }))

        # 4. Point expiry: for each earn event, if 1 year has passed
        #    and balance is positive, generate expiry events
        #    (simplified: expire signup/purchase earns after expiry_days)
        earn_events = [(ts, ev) for ts, ev in events if ev["type"] == "earn"]
        for ts, ev in earn_events:
            expire_date = self._add_days(ts, expiry_days)
            # Only expire if within data range
            end_date = f"{self.end_year}-12-31 23:59:59"
            if expire_date <= end_date:
                # 70% of earned points expire (30% are used before expiry)
                if self.rng.random() < 0.70:
                    expire_amount = int(ev["amount"] * self.rng.uniform(0.3, 0.8))
                    if expire_amount > 0:
                        events.append((expire_date, {
                            "customer_id": ev["customer_id"],
                            "order_id": None,
                            "type": "expire",
                            "reason": "expiry",
                            "amount": -expire_amount,
                            "expires_at": None,
                        }))

        # Sort all events chronologically
        events.sort(key=lambda x: x[0])

        # Build rows with running balance
        for ts, ev in events:
            tx_id += 1
            cid = ev["customer_id"]
            balance[cid] = balance.get(cid, 0) + ev["amount"]
            # Prevent negative balance from expiry
            if balance[cid] < 0:
                ev["amount"] += -balance[cid]  # adjust to make balance 0
                balance[cid] = 0

            rows.append({
                "id": tx_id,
                "customer_id": ev["customer_id"],
                "order_id": ev["order_id"],
                "type": ev["type"],
                "reason": ev["reason"],
                "amount": ev["amount"],
                "balance_after": balance[cid],
                "expires_at": ev["expires_at"],
                "created_at": ts,
            })

        return rows

    def _add_days(self, dt_str: str, days: int) -> str:
        """Add days to a datetime string and return formatted string."""
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return (dt + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
