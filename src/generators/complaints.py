"""Customer inquiry/complaint (CS) data generation"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


# Weight per category
CATEGORY_WEIGHTS = {
    "product_defect": 0.15,
    "delivery_issue": 0.25,
    "wrong_item": 0.08,
    "refund_request": 0.15,
    "exchange_request": 0.07,
    "general_inquiry": 0.22,
    "price_inquiry": 0.08,
}

# Submission channels
CHANNELS = {
    "website": 0.35,
    "phone": 0.25,
    "email": 0.20,
    "chat": 0.15,
    "kakao": 0.05,
}

# Sub-categories per complaint category
SUB_CATEGORIES = {
    "product_defect": ["initial_defect", "in_use_damage", "manufacturing_defect", "cosmetic_defect"],
    "delivery_issue": ["misdelivery", "delayed_delivery", "lost_package", "damaged_package"],
    "wrong_item": ["wrong_product", "wrong_quantity", "missing_item"],
    "refund_request": ["unsatisfied", "duplicate_order", "price_difference"],
    "exchange_request": ["size_change", "color_change", "model_change"],
    "general_inquiry": None,
    "price_inquiry": None,
}

# Complaint types: inquiry (general questions), claim (demand resolution), report (issue report)
COMPLAINT_TYPES = {
    "inquiry": 0.70,
    "claim": 0.25,
    "report": 0.05,
}

# Categories that are always claims regardless of random assignment
CLAIM_CATEGORIES = {"product_defect", "wrong_item", "refund_request", "exchange_request"}



class ComplaintGenerator(BaseGenerator):

    def generate_complaints(
        self,
        orders: list[dict],
        customers: list[dict],
        staff: list[dict],
    ) -> list[dict]:
        """Generate customer inquiry/complaint data."""
        complaints = []
        complaint_id = 0

        cs_staff = [s for s in staff if s["department"] == "CS" and s["is_active"]]
        all_staff = [s for s in staff if s["is_active"]]
        if not cs_staff:
            cs_staff = all_staff if all_staff else None
        if not cs_staff:
            return complaints

        categories = list(CATEGORY_WEIGHTS.keys())
        cat_weights = list(CATEGORY_WEIGHTS.values())
        channels = list(CHANNELS.keys())
        ch_weights = list(CHANNELS.values())
        complaint_templates = self.locale["complaint"]["templates"]

        # 1) Order-related inquiries — ~8% of all orders
        for order in orders:
            if self.rng.random() >= 0.08:
                continue

            complaint_id += 1
            ordered_at = datetime.strptime(order["ordered_at"], "%Y-%m-%d %H:%M:%S")

            # Bias complaint category based on order status
            if order["status"] == "cancelled":
                category = self.rng.choices(
                    ["refund_request", "price_inquiry", "general_inquiry"],
                    weights=[0.6, 0.2, 0.2], k=1,
                )[0]
            elif order["status"] in ("return_requested", "returned"):
                category = self.rng.choices(
                    ["product_defect", "wrong_item", "exchange_request", "refund_request"],
                    weights=[0.35, 0.25, 0.15, 0.25], k=1,
                )[0]
            elif order["status"] in ("shipped", "delivered"):
                category = self.rng.choices(
                    ["delivery_issue", "product_defect", "wrong_item", "general_inquiry"],
                    weights=[0.4, 0.25, 0.15, 0.2], k=1,
                )[0]
            else:
                category = self.rng.choices(categories, weights=cat_weights, k=1)[0]

            tmpl = complaint_templates[category]
            created_at = ordered_at + timedelta(
                days=self.rng.randint(0, 14),
                hours=self.rng.randint(0, 23),
            )

            priority = self._assign_priority(category)
            status, resolved_at, closed_at, resolution = self._resolve(
                category, priority, created_at
            )

            assigned_staff = self.rng.choice(cs_staff)
            type_fields = self._assign_type_fields(category, order.get("total_amount"))

            complaint = {
                "id": complaint_id,
                "order_id": order["id"],
                "customer_id": order["customer_id"],
                "staff_id": assigned_staff["id"],
                "category": category,
                "channel": self.rng.choices(channels, weights=ch_weights, k=1)[0],
                "priority": priority,
                "status": status,
                "title": self.rng.choice(tmpl["titles"]),
                "content": self.rng.choice(tmpl["contents"]),
                "resolution": resolution,
                "type": type_fields["type"],
                "sub_category": type_fields["sub_category"],
                "compensation_type": type_fields["compensation_type"],
                "compensation_amount": type_fields["compensation_amount"],
                "escalated": type_fields["escalated"],
                "response_count": type_fields["response_count"],
                "created_at": self.fmt_dt(created_at),
                "resolved_at": resolved_at,
                "closed_at": closed_at,
            }
            complaints.append(complaint)

        # 2) General inquiries (not order-related) — ~20% of total
        order_complaints = len(complaints)
        general_count = max(10, int(order_complaints * 0.25))
        active_customers = [c for c in customers if c["is_active"]]

        for _ in range(general_count):
            complaint_id += 1
            customer = self.rng.choice(active_customers)
            category = self.rng.choices(
                ["general_inquiry", "price_inquiry"],
                weights=[0.75, 0.25], k=1,
            )[0]
            tmpl = complaint_templates[category]

            cust_created = datetime.strptime(customer["created_at"], "%Y-%m-%d %H:%M:%S")
            created_at = self.random_datetime(
                cust_created,
                self.end_date,
            )

            priority = "low"
            status, resolved_at, closed_at, resolution = self._resolve(
                category, priority, created_at
            )

            type_fields = self._assign_type_fields(category)

            complaints.append({
                "id": complaint_id,
                "order_id": None,
                "customer_id": customer["id"],
                "staff_id": self.rng.choice(cs_staff)["id"],
                "category": category,
                "channel": self.rng.choices(channels, weights=ch_weights, k=1)[0],
                "priority": priority,
                "status": status,
                "title": self.rng.choice(tmpl["titles"]),
                "content": self.rng.choice(tmpl["contents"]),
                "resolution": resolution,
                "type": type_fields["type"],
                "sub_category": type_fields["sub_category"],
                "compensation_type": type_fields["compensation_type"],
                "compensation_amount": type_fields["compensation_amount"],
                "escalated": type_fields["escalated"],
                "response_count": type_fields["response_count"],
                "created_at": self.fmt_dt(created_at),
                "resolved_at": resolved_at,
                "closed_at": closed_at,
            })

        return complaints

    def _assign_priority(self, category: str) -> str:
        if category in ("product_defect", "wrong_item"):
            return self.rng.choices(
                ["low", "medium", "high", "urgent"],
                weights=[0.05, 0.30, 0.45, 0.20], k=1,
            )[0]
        elif category in ("refund_request", "delivery_issue"):
            return self.rng.choices(
                ["low", "medium", "high", "urgent"],
                weights=[0.10, 0.40, 0.35, 0.15], k=1,
            )[0]
        else:
            return self.rng.choices(
                ["low", "medium", "high", "urgent"],
                weights=[0.30, 0.45, 0.20, 0.05], k=1,
            )[0]

    def _resolve(
        self, category: str, priority: str, created_at: datetime,
    ) -> tuple[str, str | None, str | None, str | None]:
        """Determine complaint processing status and resolution time."""
        # Resolution rate: 95% (5% unresolved)
        if self.rng.random() < 0.05:
            return "open", None, None, None

        # Response time by priority
        if priority == "urgent":
            hours = self.rng.randint(1, 4)
        elif priority == "high":
            hours = self.rng.randint(2, 12)
        elif priority == "medium":
            hours = self.rng.randint(4, 48)
        else:
            hours = self.rng.randint(12, 96)

        resolved_at = created_at + timedelta(hours=hours)
        resolutions = self.locale["complaint"]["resolutions"]
        resolution = self.rng.choice(resolutions.get(category, ["Processed"]))

        # 0~3 days from resolution to closure
        if self.rng.random() < 0.85:
            closed_at = resolved_at + timedelta(hours=self.rng.randint(0, 72))
            status = "closed"
        else:
            closed_at = None
            status = "resolved"

        return status, self.fmt_dt(resolved_at), self.fmt_dt(closed_at) if closed_at else None, resolution

    def _assign_type_fields(self, category: str, refund_amount: float | None = None) -> dict:
        """Assign type, sub_category, compensation, escalated, and response_count."""
        # Determine complaint type
        if category in CLAIM_CATEGORIES:
            # Product/order issues are mostly claims
            complaint_type = self.rng.choices(
                ["claim", "inquiry", "report"],
                weights=[0.65, 0.25, 0.10], k=1,
            )[0]
        else:
            types = list(COMPLAINT_TYPES.keys())
            type_weights = list(COMPLAINT_TYPES.values())
            complaint_type = self.rng.choices(types, weights=type_weights, k=1)[0]

        # Sub-category
        sub_cats = SUB_CATEGORIES.get(category)
        sub_category = self.rng.choice(sub_cats) if sub_cats else None

        # Compensation (only for claims)
        compensation_type = None
        compensation_amount = 0
        escalated = 0
        response_count = 1

        if complaint_type == "claim":
            # Compensation type distribution
            compensation_type = self.rng.choices(
                ["refund", "partial_refund", "point_compensation", "exchange", "none"],
                weights=[0.25, 0.25, 0.20, 0.15, 0.15], k=1,
            )[0]

            base_amount = refund_amount if refund_amount else self.rng.uniform(10000, 200000)

            if compensation_type == "refund":
                compensation_amount = round(base_amount, 0)
            elif compensation_type == "partial_refund":
                compensation_amount = round(base_amount * self.rng.uniform(0.3, 0.7), 0)
            elif compensation_type == "point_compensation":
                compensation_amount = self.rng.randint(1, 10) * 1000  # 1000~10000 in steps of 1000
            elif compensation_type == "exchange":
                compensation_amount = 0
            else:  # none
                compensation_amount = 0

            # 15% of claims are escalated
            escalated = 1 if self.rng.random() < 0.15 else 0

            # Response count: 2-5 for claims, 3-8 for escalated
            if escalated:
                response_count = self.rng.randint(3, 8)
            else:
                response_count = self.rng.randint(2, 5)
        else:
            # Simple inquiries/reports: 1 response
            response_count = 1

        return {
            "type": complaint_type,
            "sub_category": sub_category,
            "compensation_type": compensation_type,
            "compensation_amount": compensation_amount,
            "escalated": escalated,
            "response_count": response_count,
        }
