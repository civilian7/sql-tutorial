"""Return/exchange data generation"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


# Weight per return reason
RETURN_REASONS = {
    "defective":          {"weight": 0.25},
    "wrong_item":         {"weight": 0.10},
    "change_of_mind":     {"weight": 0.35},
    "damaged_in_transit": {"weight": 0.15},
    "not_as_described":   {"weight": 0.10},
    "late_delivery":      {"weight": 0.05},
}

# Inspection results
INSPECTION_RESULTS = {
    "defective":          {"defective": 0.80, "good": 0.15, "unsellable": 0.05},
    "wrong_item":         {"good": 0.90, "defective": 0.05, "unsellable": 0.05},
    "change_of_mind":     {"good": 0.85, "opened_good": 0.10, "unsellable": 0.05},
    "damaged_in_transit": {"defective": 0.60, "unsellable": 0.30, "good": 0.10},
    "not_as_described":   {"good": 0.70, "defective": 0.20, "unsellable": 0.10},
    "late_delivery":      {"good": 0.95, "opened_good": 0.05},
}



class ReturnGenerator(BaseGenerator):

    def generate_returns(
        self,
        orders: list[dict],
        order_items: list[dict],
        shipping: list[dict],
        complaints: list[dict] | None = None,
        products: list[dict] | None = None,
    ) -> list[dict]:
        """Generate return/exchange data."""
        returns = []
        return_id = 0

        # order_id → items, shipping mapping
        items_by_order: dict[int, list[dict]] = {}
        for it in order_items:
            items_by_order.setdefault(it["order_id"], []).append(it)

        ship_by_order: dict[int, dict] = {}
        for s in shipping:
            ship_by_order[s["order_id"]] = s

        # Build claim complaints index by order_id for linking
        claims_by_order: dict[int, list[dict]] = {}
        if complaints:
            for c in complaints:
                if c.get("type") == "claim" and c.get("order_id"):
                    claims_by_order.setdefault(c["order_id"], []).append(c)

        # Build products by category for exchange_product_id
        products_by_category: dict[int, list[dict]] = {}
        if products:
            for p in products:
                products_by_category.setdefault(p["category_id"], []).append(p)

        reasons = list(RETURN_REASONS.keys())
        reason_weights = [RETURN_REASONS[r]["weight"] for r in reasons]
        return_carriers_data = self.locale["shipping"]["carriers"]
        carriers = list(return_carriers_data.keys())
        carrier_weights = list(return_carriers_data.values())
        reason_details = self.locale["return"]["reason_details"]

        # Orders eligible for return/exchange
        return_orders = [
            o for o in orders
            if o["status"] in ("return_requested", "returned")
        ]

        for order in return_orders:
            return_id += 1
            ordered_at = datetime.strptime(order["ordered_at"], "%Y-%m-%d %H:%M:%S")
            ship = ship_by_order.get(order["id"])
            items = items_by_order.get(order["id"], [])
            if not items:
                continue

            # Return reason
            reason = self.rng.choices(reasons, weights=reason_weights, k=1)[0]
            reason_detail = self.rng.choice(reason_details[reason])

            # Return type: refund vs exchange
            if reason in ("change_of_mind", "late_delivery"):
                return_type = self.rng.choices(["refund", "exchange"], weights=[0.7, 0.3], k=1)[0]
            elif reason in ("defective", "damaged_in_transit"):
                return_type = self.rng.choices(["refund", "exchange"], weights=[0.5, 0.5], k=1)[0]
            else:
                return_type = self.rng.choices(["refund", "exchange"], weights=[0.6, 0.4], k=1)[0]

            # Return request date: 1~14 days after delivery
            delivered_at = None
            if ship and ship.get("delivered_at"):
                delivered_at = datetime.strptime(ship["delivered_at"], "%Y-%m-%d %H:%M:%S")
            if delivered_at is None:
                delivered_at = ordered_at + timedelta(days=self.rng.randint(3, 7))

            requested_at = delivered_at + timedelta(
                days=self.rng.randint(0, 14),
                hours=self.rng.randint(0, 23),
            )

            # Pickup carrier
            carrier = self.rng.choices(carriers, weights=carrier_weights, k=1)[0]
            tracking = str(self.rng.randint(100000000000, 999999999999))

            # Pickup schedule
            pickup_at = requested_at + timedelta(days=self.rng.randint(1, 3))

            # Return items (full or partial)
            if len(items) == 1 or self.rng.random() < 0.7:
                return_items = items  # Full return
                is_partial = 0
            else:
                return_items = [self.rng.choice(items)]  # Partial return
                is_partial = 1

            refund_amount = sum(it["subtotal"] for it in return_items)

            # Processing status
            if order["status"] == "return_requested":
                # Still in progress
                status = self.rng.choices(
                    ["requested", "pickup_scheduled", "in_transit"],
                    weights=[0.3, 0.4, 0.3], k=1,
                )[0]
                received_at = None
                inspected_at = None
                inspection_result = None
                completed_at = None
                refund_status = "pending"
            else:
                # Completed
                received_at = pickup_at + timedelta(days=self.rng.randint(1, 4))
                inspected_at = received_at + timedelta(hours=self.rng.randint(2, 48))

                # Inspection result
                insp_dist = INSPECTION_RESULTS[reason]
                inspection_result = self.rng.choices(
                    list(insp_dist.keys()),
                    weights=list(insp_dist.values()), k=1,
                )[0]

                completed_at = inspected_at + timedelta(hours=self.rng.randint(1, 24))
                status = "completed"

                # Refund status
                if return_type == "exchange":
                    refund_status = "exchanged"
                elif inspection_result == "unsellable" and reason == "change_of_mind":
                    # Customer-caused damage → partial refund
                    refund_amount = round(refund_amount * 0.8, 2)
                    refund_status = "partial_refund"
                else:
                    refund_status = "refunded"

            # Link to a claim complaint (~40% of returns)
            claim_id = None
            order_claims = claims_by_order.get(order["id"], [])
            if order_claims and self.rng.random() < 0.40:
                claim_id = self.rng.choice(order_claims)["id"]

            # Exchange product: for wrong_item/defective with exchange type, pick from same category
            exchange_product_id = None
            if return_type == "exchange" and reason in ("wrong_item", "defective") and return_items:
                item = return_items[0]
                product_id = item["product_id"]
                # Find the product's category
                cat_id = None
                if products:
                    for p in products:
                        if p["id"] == product_id:
                            cat_id = p["category_id"]
                            break
                if cat_id and cat_id in products_by_category:
                    candidates = [p for p in products_by_category[cat_id] if p["id"] != product_id]
                    if candidates:
                        exchange_product_id = self.rng.choice(candidates)["id"]

            # Restocking fee: for change_of_mind, 10% of item value capped at 50000
            restocking_fee = 0
            if reason == "change_of_mind":
                raw_fee = round(refund_amount * 0.10, 0)
                restocking_fee = min(raw_fee, 50000)

            returns.append({
                "id": return_id,
                "order_id": order["id"],
                "customer_id": order["customer_id"],
                "return_type": return_type,
                "reason": reason,
                "reason_detail": reason_detail,
                "status": status,
                "is_partial": is_partial,
                "refund_amount": round(refund_amount, 2),
                "refund_status": refund_status,
                "carrier": carrier,
                "tracking_number": tracking,
                "requested_at": self.fmt_dt(requested_at),
                "pickup_at": self.fmt_dt(pickup_at),
                "received_at": self.fmt_dt(received_at) if received_at else None,
                "inspected_at": self.fmt_dt(inspected_at) if inspected_at else None,
                "inspection_result": inspection_result,
                "completed_at": self.fmt_dt(completed_at) if completed_at else None,
                "claim_id": claim_id,
                "exchange_product_id": exchange_product_id,
                "restocking_fee": restocking_fee,
                "created_at": self.fmt_dt(requested_at),
            })

        return returns
