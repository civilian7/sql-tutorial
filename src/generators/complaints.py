"""고객 문의/불만(CS) 데이터 생성"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


# 유형별 비율
CATEGORY_WEIGHTS = {
    "product_defect": 0.15,
    "delivery_issue": 0.25,
    "wrong_item": 0.08,
    "refund_request": 0.15,
    "exchange_request": 0.07,
    "general_inquiry": 0.22,
    "price_inquiry": 0.08,
}

# 접수 채널
CHANNELS = {
    "website": 0.35,
    "phone": 0.25,
    "email": 0.20,
    "chat": 0.15,
    "kakao": 0.05,
}



class ComplaintGenerator(BaseGenerator):

    def generate_complaints(
        self,
        orders: list[dict],
        customers: list[dict],
        staff: list[dict],
    ) -> list[dict]:
        """고객 문의/불만 데이터를 생성한다."""
        complaints = []
        complaint_id = 0

        cs_staff = [s for s in staff if s["department"] == "CS" and s["is_active"]]
        all_staff = [s for s in staff if s["is_active"]]
        if not cs_staff:
            cs_staff = all_staff[:3]

        categories = list(CATEGORY_WEIGHTS.keys())
        cat_weights = list(CATEGORY_WEIGHTS.values())
        channels = list(CHANNELS.keys())
        ch_weights = list(CHANNELS.values())
        complaint_templates = self.locale["complaint"]["templates"]

        # 1) 주문 연관 문의 — 전체 주문의 ~8%
        for order in orders:
            if self.rng.random() >= 0.08:
                continue

            complaint_id += 1
            ordered_at = datetime.strptime(order["ordered_at"], "%Y-%m-%d %H:%M:%S")

            # 주문 상태에 따라 문의 유형 편향
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

            complaints.append({
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
                "created_at": self.fmt_dt(created_at),
                "resolved_at": resolved_at,
                "closed_at": closed_at,
            })

        # 2) 주문 무관 일반 문의 — 전체 문의의 ~20%
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
                datetime(self.end_year, 6, 30),
            )

            priority = "low"
            status, resolved_at, closed_at, resolution = self._resolve(
                category, priority, created_at
            )

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
        """문의 처리 상태와 해결 시간을 결정한다."""
        # 해결률: 95% (미해결 5%)
        if self.rng.random() < 0.05:
            return "open", None, None, None

        # 응답 시간: 우선순위별
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

        # 해결 후 종료까지 0~3일
        if self.rng.random() < 0.85:
            closed_at = resolved_at + timedelta(hours=self.rng.randint(0, 72))
            status = "closed"
        else:
            closed_at = None
            status = "resolved"

        return status, self.fmt_dt(resolved_at), self.fmt_dt(closed_at) if closed_at else None, resolution
