"""주문/주문상세 데이터 생성"""

from __future__ import annotations

import calendar
from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator
from src.utils.growth import get_daily_order_count


# 시간대별 주문 가중치 (0~23시) — 새벽 최저, 점심/저녁 피크
HOURLY_WEIGHTS = [
    0.3, 0.2, 0.1, 0.1, 0.1, 0.2,   # 0~5시 (새벽)
    0.4, 0.6, 0.9, 1.2, 1.5, 1.4,   # 6~11시 (오전)
    1.6, 1.5, 1.3, 1.2, 1.1, 1.0,   # 12~17시 (오후)
    1.2, 1.4, 1.8, 2.0, 1.6, 0.8,   # 18~23시 (저녁 피크)
]

# 요일별 주문 가중치 (월~일) — 주말/월요일 높음
WEEKDAY_WEIGHTS = [1.10, 0.95, 0.90, 0.90, 0.95, 1.10, 1.10]



class OrderGenerator(BaseGenerator):

    def generate_orders(
        self,
        customers: list[dict],
        addresses: list[dict],
        products: list[dict],
        staff: list[dict],
    ) -> tuple[list[dict], list[dict]]:
        """주문과 주문 상세를 생성한다."""
        orders = []
        order_items = []
        order_id = 0
        item_id = 0

        # 고객별 주소 매핑
        customer_addrs: dict[int, list[int]] = {}
        for a in addresses:
            customer_addrs.setdefault(a["customer_id"], []).append(a["id"])

        # 고객: 활성 + 로그인 이력 있는 고객만
        eligible_customers = [
            c for c in customers
            if c["is_active"] == 1 and c["last_login_at"] is not None
        ]
        # 고객 생성일/마지막로그인 캐시
        cust_created = {}
        cust_last_login = {}
        for c in eligible_customers:
            cust_created[c["id"]] = datetime.strptime(c["created_at"], "%Y-%m-%d %H:%M:%S")
            cust_last_login[c["id"]] = datetime.strptime(c["last_login_at"], "%Y-%m-%d %H:%M:%S")

        # 고객별 파레토 가중치 (고정, 시드 재현)
        cust_weight = {}
        for c in eligible_customers:
            rs = (hash(c["id"] * 31 + 7) % 1000) / 1000.0
            if rs < 0.05:
                cust_weight[c["id"]] = 10.0
            elif rs < 0.20:
                cust_weight[c["id"]] = 4.0
            elif rs < 0.50:
                cust_weight[c["id"]] = 1.5
            else:
                cust_weight[c["id"]] = 0.5

        # 상품: 활성 상품 (단종일 캐시)
        prod_created = {}
        prod_disc = {}
        for p in products:
            prod_created[p["id"]] = datetime.strptime(p["created_at"], "%Y-%m-%d %H:%M:%S")
            if p["discontinued_at"]:
                prod_disc[p["id"]] = datetime.strptime(p["discontinued_at"], "%Y-%m-%d %H:%M:%S")

        # 상품 가격 가중치
        prod_weight = {}
        for p in products:
            price = p["price"]
            if price <= 50000:
                prod_weight[p["id"]] = 5.0
            elif price <= 200000:
                prod_weight[p["id"]] = 3.0
            elif price <= 500000:
                prod_weight[p["id"]] = 2.0
            elif price <= 1000000:
                prod_weight[p["id"]] = 1.0
            elif price <= 2000000:
                prod_weight[p["id"]] = 0.5
            else:
                prod_weight[p["id"]] = 0.2

        # 월별 고객/상품 풀 사전 구축
        month_custs: dict[tuple[int, int], tuple[list[dict], list[float]]] = {}
        month_prods: dict[tuple[int, int], tuple[list[dict], list[float]]] = {}

        for year in range(self.start_year, self.end_year + 1):
            for month in range(1, 13):
                month_end = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
                # 고객: 해당 월 이전 가입 + 마지막 로그인이 1년 이내
                cutoff = month_end - timedelta(days=365)
                mc = [c for c in eligible_customers
                      if cust_created[c["id"]] <= month_end
                      and cust_last_login[c["id"]] >= cutoff]
                mw = [cust_weight[c["id"]] for c in mc]
                month_custs[(year, month)] = (mc, mw)

                # 상품: 해당 월 이전 등록 + 아직 단종 안 됨
                mp = [p for p in products
                      if prod_created[p["id"]] <= month_end
                      and (p["id"] not in prod_disc or prod_disc[p["id"]] >= month_end)]
                pw = [prod_weight[p["id"]] for p in mp]
                month_prods[(year, month)] = (mp, pw)

        active_staff = [s for s in staff if s["is_active"]]
        cs_staff = [s for s in active_staff if s["department"] == "CS"]

        order_cfg = self.config["order"]
        cancel_rate = order_cfg["cancellation_rate"]
        return_rate = order_cfg["return_rate"]
        free_threshold = order_cfg["free_shipping_threshold"]
        shipping_fee_default = order_cfg["default_shipping_fee"]
        points_rate = order_cfg["points_earn_rate"]
        edge = self.config["edge_cases"]

        yearly_growth = self.config["yearly_growth"]
        monthly_seasonality = self.config["monthly_seasonality"]

        for year in range(self.start_year, self.end_year + 1):
            for month in range(1, 13):
                if year == self.end_year and month > 6:
                    break

                m_custs, m_cust_w = month_custs[(year, month)]
                m_prods, m_prod_w = month_prods[(year, month)]
                if not m_custs or not m_prods:
                    continue

                days_in_month = calendar.monthrange(year, month)[1]
                daily_count = get_daily_order_count(
                    year, month, yearly_growth, monthly_seasonality, self.scale, self.rng
                )

                for day in range(1, days_in_month + 1):
                    weekday = datetime(year, month, day).weekday()
                    adjusted = int(daily_count * WEEKDAY_WEIGHTS[weekday])
                    day_orders = self.rng.randint(
                        max(1, int(adjusted * 0.8)),
                        max(1, int(adjusted * 1.2)),
                    )

                    for _ in range(day_orders):
                        order_id += 1
                        customer = self.rng.choices(m_custs, weights=m_cust_w, k=1)[0]
                        cust_addrs = customer_addrs.get(customer["id"])
                        if not cust_addrs:
                            continue
                        addr_id = self.rng.choice(cust_addrs)

                        hour = self.rng.choices(range(24), weights=HOURLY_WEIGHTS, k=1)[0]
                        ordered_at = datetime(year, month, day, hour,
                                              self.rng.randint(0, 59), self.rng.randint(0, 59))

                        # 주문일은 반드시 고객 가입일 이후
                        c_created = cust_created[customer["id"]]
                        if ordered_at < c_created:
                            ordered_at = c_created + timedelta(
                                hours=self.rng.randint(1, 72)
                            )

                        # 주문 아이템 생성 (동일 상품 중복 방지)
                        is_bulk = self.rng.random() < edge["bulk_order"]
                        if is_bulk:
                            num_items = self.rng.randint(5, min(15, len(m_prods)))
                        else:
                            num_items = self.rng.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5], k=1)[0]
                        num_items = min(num_items, len(m_prods))

                        total = 0.0
                        items = []
                        used_product_ids: set[int] = set()

                        for _ in range(num_items):
                            # 중복 방지: 최대 3회 재시도
                            product = None
                            for _retry in range(3):
                                candidate = self.rng.choices(m_prods, weights=m_prod_w, k=1)[0]
                                if candidate["id"] not in used_product_ids:
                                    product = candidate
                                    break
                            if product is None:
                                continue
                            used_product_ids.add(product["id"])

                            qty = 1 if not is_bulk else self.rng.randint(2, 10)
                            unit_price = product["price"]
                            disc = 0
                            if self.rng.random() < 0.1:
                                disc = round(unit_price * qty * self.rng.uniform(0.03, 0.15), -2)
                            subtotal = unit_price * qty - disc

                            item_id += 1
                            items.append({
                                "id": item_id,
                                "order_id": order_id,
                                "product_id": product["id"],
                                "quantity": qty,
                                "unit_price": unit_price,
                                "discount_amount": disc,
                                "subtotal": subtotal,
                            })
                            total += subtotal

                        if not items:
                            continue

                        shipping_fee = 0 if total >= free_threshold else shipping_fee_default

                        point_used = 0
                        if self.rng.random() < 0.1:
                            point_used = self.rng.randint(100, 5000)
                            point_used = min(point_used, int(total * 0.3))

                        total_amount = total + shipping_fee - point_used
                        point_earned = int(total_amount * points_rate)
                        discount_amount = sum(it["discount_amount"] for it in items)

                        # 상태 결정
                        r = self.rng.random()
                        if r < cancel_rate:
                            status = "cancelled"
                        elif r < cancel_rate + return_rate:
                            status = self.rng.choice(["return_requested", "returned"])
                        else:
                            days_ago = (datetime(self.end_year, 12, 31) - ordered_at).days
                            if days_ago < 3:
                                status = "pending"
                            elif days_ago < 7:
                                status = self.rng.choice(["paid", "preparing", "shipped"])
                            elif days_ago < 14:
                                status = self.rng.choice(["shipped", "delivered", "confirmed"])
                            else:
                                status = "confirmed"

                        completed_at = None
                        cancelled_at = None
                        if status == "confirmed":
                            completed_at = self.fmt_dt(ordered_at + timedelta(days=self.rng.randint(3, 14)))
                        elif status == "cancelled":
                            cancelled_at = self.fmt_dt(ordered_at + timedelta(hours=self.rng.randint(1, 48)))

                        order_number = f"ORD-{year}{month:02d}{day:02d}-{order_id:05d}"

                        staff_id = None
                        if status in ("cancelled", "return_requested", "returned") and cs_staff:
                            staff_id = self.rng.choice(cs_staff)["id"]

                        # 배송 메모 (~35%)
                        notes = None
                        if self.rng.random() < 0.35:
                            notes = self.rng.choice(self.locale["order"]["delivery_notes"])

                        orders.append({
                            "id": order_id,
                            "order_number": order_number,
                            "customer_id": customer["id"],
                            "address_id": addr_id,
                            "staff_id": staff_id,
                            "status": status,
                            "total_amount": round(total_amount, 2),
                            "discount_amount": round(discount_amount, 2),
                            "shipping_fee": shipping_fee,
                            "point_used": point_used,
                            "point_earned": point_earned,
                            "notes": notes,
                            "ordered_at": self.fmt_dt(ordered_at),
                            "completed_at": completed_at,
                            "cancelled_at": cancelled_at,
                            "created_at": self.fmt_dt(ordered_at),
                            "updated_at": self.fmt_dt(ordered_at),
                        })
                        order_items.extend(items)

        return orders, order_items
