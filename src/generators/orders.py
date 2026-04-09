"""Order and order item data generation.

Key realism features:
- Product bundles (PC build combos, laptop + peripherals)
- Gender/age-based order frequency and category preferences
- First-purchase small amount, repeat-purchase larger
- Product popularity decay over time (newer = more popular)
"""

from __future__ import annotations

import calendar
from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator
from src.utils.growth import get_daily_order_count


# Hourly order weights (0~23h) -- lowest at dawn, peak at lunch/evening
HOURLY_WEIGHTS = [
    0.3, 0.2, 0.1, 0.1, 0.1, 0.2,   # 0~5h (dawn)
    0.4, 0.6, 0.9, 1.2, 1.5, 1.4,   # 6~11h (morning)
    1.6, 1.5, 1.3, 1.2, 1.1, 1.0,   # 12~17h (afternoon)
    1.2, 1.4, 1.8, 2.0, 1.6, 0.8,   # 18~23h (evening peak)
]

# Day-of-week order weights (Mon~Sun) -- higher on weekends/Monday
WEEKDAY_WEIGHTS = [1.10, 0.95, 0.90, 0.90, 0.95, 1.10, 1.10]

# Product bundle definitions: category slug sets that are commonly bought together
# Each bundle has a trigger category and companion categories
BUNDLES = [
    # PC build: CPU + motherboard + RAM + SSD + PSU + case (+ optional GPU, cooler)
    {
        "name": "pc_build",
        "trigger": ["cpu-intel", "cpu-amd"],
        "required": ["mb-intel|mb-amd", "ram-ddr4|ram-ddr5", "storage-ssd", "psu", "case"],
        "optional": ["gpu-nvidia|gpu-amd", "cooling-air|cooling-liquid"],
        "weight": 0.15,  # 15% of multi-item orders
    },
    # Laptop + peripherals
    {
        "name": "laptop_set",
        "trigger": ["laptop-general", "laptop-gaming", "laptop-2in1", "laptop-macbook"],
        "required": [],
        "optional": ["mouse-wireless|mouse-gaming", "keyboard-wireless|keyboard-mechanical", "audio"],
        "weight": 0.20,
    },
    # Monitor + cable/arm (simplified as monitor + keyboard/mouse)
    {
        "name": "monitor_set",
        "trigger": ["monitor-general", "monitor-gaming", "monitor-professional"],
        "required": [],
        "optional": ["keyboard-wireless|keyboard-mechanical|keyboard-membrane", "mouse-wireless|mouse-gaming"],
        "weight": 0.10,
    },
    # Gaming setup: GPU + monitor + mouse + keyboard + headset
    {
        "name": "gaming_set",
        "trigger": ["gpu-nvidia", "gpu-amd"],
        "required": [],
        "optional": ["monitor-gaming", "mouse-gaming", "keyboard-mechanical", "audio"],
        "weight": 0.08,
    },
]

# Gender/age category preference multipliers
# Higher = more likely to order from this category group
DEMOGRAPHIC_PREFS = {
    # (gender, age_bucket) -> {category_prefix: multiplier}
    ("M", "young"):  {"gpu": 2.5, "cpu": 2.0, "mb": 2.0, "ram": 2.0, "cooling": 2.0,
                       "case": 1.8, "keyboard-mechanical": 2.0, "mouse-gaming": 2.5,
                       "laptop-gaming": 2.0, "monitor-gaming": 2.0, "audio": 1.5},
    ("M", "mid"):    {"desktop": 1.5, "monitor": 1.5, "storage": 1.5, "network": 1.5,
                       "printer": 1.3, "ups": 1.5, "software": 1.3},
    ("M", "senior"): {"desktop-prebuilt": 2.0, "printer": 2.0, "monitor-general": 1.5,
                       "software": 1.5, "ups": 1.5, "network-router": 1.5},
    ("F", "young"):  {"laptop-general": 2.0, "laptop-2in1": 2.0, "laptop-macbook": 2.5,
                       "mouse-wireless": 2.0, "keyboard-wireless": 2.0, "audio": 2.0,
                       "monitor-general": 1.5},
    ("F", "mid"):    {"laptop-general": 1.8, "printer": 1.5, "monitor-general": 1.5,
                       "software-office": 2.0, "keyboard-membrane": 1.5},
    ("F", "senior"): {"desktop-prebuilt": 2.0, "laptop-general": 1.5, "printer": 2.5,
                       "software": 1.5, "monitor-general": 1.5},
}

# Gender order frequency multiplier
GENDER_FREQ = {"M": 1.2, "F": 0.8, None: 0.6}

# Age bucket order frequency multiplier
AGE_FREQ = {"young": 1.3, "mid": 1.0, "senior": 0.6}


def _age_bucket(birth_date: str | None) -> str:
    """Classify birth_date into age bucket."""
    if not birth_date:
        return "mid"  # default
    year = int(birth_date[:4])
    if year >= 1990:
        return "young"   # ~35 and younger
    elif year >= 1975:
        return "mid"     # 36~50
    else:
        return "senior"  # 51+


# Return rate multipliers by category slug prefix.
# Complete systems have higher return rates; accessories/consumables lower.
_CATEGORY_RETURN_MULTIPLIERS: list[tuple[str, float]] = [
    ("laptop",   1.8),
    ("desktop",  1.8),
    ("monitor",  1.5),
    ("printer",  1.5),
    ("gpu",      1.2),
    ("cpu",      1.2),
    ("keyboard", 0.7),
    ("mouse",    0.7),
    ("audio",    0.7),
    ("storage",  0.5),
    ("ram",      0.5),
    ("psu",      0.5),
    ("case",     0.5),
    ("cooling",  0.5),
    ("software", 0.3),
    ("ups",      0.3),
    ("network",  0.3),
]


def _category_return_multiplier(slug: str) -> float:
    """Return the return-rate multiplier for a category slug."""
    for prefix, mult in _CATEGORY_RETURN_MULTIPLIERS:
        if slug.startswith(prefix):
            return mult
    return 1.0


class OrderGenerator(BaseGenerator):

    def generate_orders(
        self,
        customers: list[dict],
        addresses: list[dict],
        products: list[dict],
        staff: list[dict],
    ) -> tuple[list[dict], list[dict]]:
        """Generate orders and order items with realistic patterns."""
        orders = []
        order_items = []
        order_id = 0
        item_id = 0

        # Map addresses by customer
        customer_addrs: dict[int, list[int]] = {}
        for a in addresses:
            customer_addrs.setdefault(a["customer_id"], []).append(a["id"])

        # Customers: only active ones with login history
        eligible_customers = [
            c for c in customers
            if c["is_active"] == 1 and c["last_login_at"] is not None
        ]
        cust_created = {}
        cust_last_login = {}
        cust_order_count: dict[int, int] = {}  # track order count per customer
        for c in eligible_customers:
            cust_created[c["id"]] = datetime.strptime(c["created_at"], "%Y-%m-%d %H:%M:%S")
            cust_last_login[c["id"]] = datetime.strptime(c["last_login_at"], "%Y-%m-%d %H:%M:%S")
            cust_order_count[c["id"]] = 0

        # Customer weights: Pareto + gender/age adjustments
        cust_weight = {}
        cust_demo: dict[int, tuple[str | None, str]] = {}  # id -> (gender, age_bucket)
        for c in eligible_customers:
            # Base Pareto weight
            rs = (hash(c["id"] * 31 + 7) % 1000) / 1000.0
            if rs < 0.05:
                base_w = 10.0
            elif rs < 0.20:
                base_w = 4.0
            elif rs < 0.50:
                base_w = 1.5
            else:
                base_w = 0.5

            gender = c.get("gender")
            age_bkt = _age_bucket(c.get("birth_date"))
            cust_demo[c["id"]] = (gender, age_bkt)

            # Apply demographic multipliers
            gender_mult = GENDER_FREQ.get(gender, 0.8)
            age_mult = AGE_FREQ.get(age_bkt, 1.0)
            cust_weight[c["id"]] = base_w * gender_mult * age_mult

        # Products: cache creation/discontinuation dates
        prod_created = {}
        prod_disc = {}
        prod_cat_slug: dict[int, str] = {}  # product_id -> category slug
        cat_slug_map = {}  # category_id -> slug (leaf categories)
        for p in products:
            prod_created[p["id"]] = datetime.strptime(p["created_at"], "%Y-%m-%d %H:%M:%S")
            if p["discontinued_at"]:
                prod_disc[p["id"]] = datetime.strptime(p["discontinued_at"], "%Y-%m-%d %H:%M:%S")

        # Build category slug lookup from products (infer from category_id)
        # We need a proper cat_id -> slug map; build from config or data
        # For now, use a simple approach: read from the categories list if available
        _cats = self.config.get("_categories_cache", [])
        for c in _cats:
            cat_slug_map[c["id"]] = c["slug"]
        for p in products:
            prod_cat_slug[p["id"]] = cat_slug_map.get(p["category_id"], "")

        # Products grouped by category slug for bundle selection
        prods_by_slug: dict[str, list[dict]] = {}
        for p in products:
            slug = prod_cat_slug.get(p["id"], "")
            prods_by_slug.setdefault(slug, []).append(p)

        # Product weight: price-based + time decay (newer products more popular)
        def _prod_weight(p: dict, ref_date: datetime) -> float:
            price = p["price"]
            if price <= 50000:
                w = 5.0
            elif price <= 200000:
                w = 3.0
            elif price <= 500000:
                w = 2.0
            elif price <= 1000000:
                w = 1.0
            elif price <= 2000000:
                w = 0.5
            else:
                w = 0.2
            # Time decay: products lose 50% weight per 3 years
            created = prod_created[p["id"]]
            years_old = max(0, (ref_date - created).days / 365.0)
            decay = max(0.1, 1.0 - years_old * 0.17)
            return w * decay

        # Pre-build monthly customer/product pools
        month_custs: dict[tuple[int, int], tuple[list[dict], list[float]]] = {}
        month_prods: dict[tuple[int, int], tuple[list[dict], list[float]]] = {}

        for year in range(self.start_year, self.end_year + 1):
            for month in range(1, 13):
                month_end = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
                cutoff = month_end - timedelta(days=365)
                mc = [c for c in eligible_customers
                      if cust_created[c["id"]] <= month_end
                      and cust_last_login[c["id"]] >= cutoff]
                mw = [cust_weight[c["id"]] for c in mc]
                month_custs[(year, month)] = (mc, mw)

                mp = [p for p in products
                      if prod_created[p["id"]] <= month_end
                      and (p["id"] not in prod_disc or prod_disc[p["id"]] >= month_end)]
                pw = [_prod_weight(p, month_end) for p in mp]
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
                if datetime(year, month, 1) > self.end_date:
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

                        c_created = cust_created[customer["id"]]
                        if ordered_at < c_created:
                            ordered_at = c_created + timedelta(hours=self.rng.randint(1, 72))

                        # Determine items using bundle or random selection
                        is_bulk = self.rng.random() < edge["bulk_order"]
                        gender, age_bkt = cust_demo.get(customer["id"], (None, "mid"))
                        is_first_order = cust_order_count.get(customer["id"], 0) == 0
                        items, item_id = self._generate_items(
                            m_prods, m_prod_w, prods_by_slug, prod_cat_slug,
                            gender, age_bkt, is_first_order, is_bulk,
                            order_id, item_id, ordered_at, edge,
                        )

                        if not items:
                            continue

                        cust_order_count[customer["id"]] = cust_order_count.get(customer["id"], 0) + 1

                        total = sum(it["subtotal"] for it in items)
                        shipping_fee = 0 if total >= free_threshold else shipping_fee_default

                        point_used = 0
                        if self.rng.random() < 0.1:
                            point_used = self.rng.randint(100, 5000)
                            point_used = min(point_used, int(total * 0.3))

                        total_amount = total + shipping_fee - point_used
                        point_earned = int((total + shipping_fee) * points_rate)
                        discount_amount = sum(it["discount_amount"] for it in items)

                        # Adjust return rate by highest-value item's category
                        best_item = max(items, key=lambda it: it["subtotal"])
                        best_slug = prod_cat_slug.get(best_item["product_id"], "")
                        adj_return_rate = return_rate * _category_return_multiplier(best_slug)

                        # Determine status
                        r = self.rng.random()
                        if r < cancel_rate:
                            status = "cancelled"
                        elif r < cancel_rate + adj_return_rate:
                            status = self.rng.choice(["return_requested", "returned"])
                        else:
                            days_ago = (self.end_date - ordered_at).days
                            if days_ago < 3:
                                status = "pending"
                            elif days_ago < 5:
                                status = self.rng.choice(["paid", "preparing"])
                            elif days_ago < 10:
                                status = self.rng.choice(["shipped", "delivered"])
                            elif days_ago < 21:
                                status = self.rng.choices(
                                    ["delivered", "confirmed"], weights=[0.3, 0.7], k=1
                                )[0]
                            else:
                                status = "confirmed"

                        completed_at = None
                        cancelled_at = None
                        if status == "confirmed":
                            completed_at = self.fmt_dt(ordered_at + timedelta(days=self.rng.randint(8, 21)))
                        elif status == "cancelled":
                            cancelled_at = self.fmt_dt(ordered_at + timedelta(hours=self.rng.randint(1, 48)))

                        order_number = f"ORD-{year}{month:02d}{day:02d}-{order_id:05d}"

                        staff_id = None
                        if status in ("cancelled", "return_requested", "returned") and cs_staff:
                            staff_id = self.rng.choice(cs_staff)["id"]

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

    def _generate_items(
        self,
        m_prods: list[dict],
        m_prod_w: list[float],
        prods_by_slug: dict[str, list[dict]],
        prod_cat_slug: dict[int, str],
        gender: str | None,
        age_bkt: str,
        is_first_order: bool,
        is_bulk: bool,
        order_id: int,
        item_id: int,
        ordered_at: datetime,
        edge: dict,
    ) -> tuple[list[dict], int]:
        """Generate order items with bundle logic and demographic preferences."""
        items = []
        used_product_ids: set[int] = set()

        # Determine order pattern
        if is_bulk and len(m_prods) >= 5:
            num_items = self.rng.randint(5, min(15, len(m_prods)))
        elif is_first_order:
            # First order: usually 1-2 items, peripherals/accessories
            num_items = self.rng.choices([1, 2], weights=[0.7, 0.3], k=1)[0]
        else:
            num_items = self.rng.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5], k=1)[0]
        num_items = min(num_items, len(m_prods))

        # Try bundle selection for multi-item orders
        bundle_items = []
        if num_items >= 2 and not is_bulk:
            bundle_items = self._try_bundle(
                prods_by_slug, prod_cat_slug, m_prods, gender, age_bkt, ordered_at,
            )

        if bundle_items:
            # Use bundle items
            for p in bundle_items:
                if p["id"] in used_product_ids:
                    continue
                used_product_ids.add(p["id"])
                item_id += 1
                unit_price = p["price"]
                disc = 0
                if self.rng.random() < 0.1:
                    disc = round(unit_price * self.rng.uniform(0.03, 0.15), -2)
                items.append({
                    "id": item_id,
                    "order_id": order_id,
                    "product_id": p["id"],
                    "quantity": 1,
                    "unit_price": unit_price,
                    "discount_amount": disc,
                    "subtotal": unit_price - disc,
                })
        else:
            # Apply demographic preference weights
            demo_key = (gender, age_bkt)
            prefs = DEMOGRAPHIC_PREFS.get(demo_key, {})

            adjusted_w = list(m_prod_w)
            if prefs:
                for i, p in enumerate(m_prods):
                    slug = prod_cat_slug.get(p["id"], "")
                    for pref_slug, mult in prefs.items():
                        if slug.startswith(pref_slug) or slug == pref_slug:
                            adjusted_w[i] *= mult
                            break

            # First order: bias toward cheaper items (peripherals)
            if is_first_order:
                for i, p in enumerate(m_prods):
                    if p["price"] <= 200000:
                        adjusted_w[i] *= 2.0
                    elif p["price"] >= 1000000:
                        adjusted_w[i] *= 0.3

            for _ in range(num_items):
                product = None
                for _retry in range(3):
                    candidate = self.rng.choices(m_prods, weights=adjusted_w, k=1)[0]
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

                item_id += 1
                items.append({
                    "id": item_id,
                    "order_id": order_id,
                    "product_id": product["id"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "discount_amount": disc,
                    "subtotal": unit_price * qty - disc,
                })

        return items, item_id

    def _try_bundle(
        self,
        prods_by_slug: dict[str, list[dict]],
        prod_cat_slug: dict[int, str],
        m_prods: list[dict],
        gender: str | None,
        age_bkt: str,
        ordered_at: datetime,
    ) -> list[dict]:
        """Try to generate a product bundle. Returns empty list if no bundle applies."""
        # Select a bundle based on weights
        r = self.rng.random()
        cumulative = 0.0
        chosen_bundle = None
        for b in BUNDLES:
            cumulative += b["weight"]
            if r < cumulative:
                chosen_bundle = b
                break

        if not chosen_bundle:
            return []

        # Check if trigger category products are available
        available_slugs = set(prod_cat_slug[p["id"]] for p in m_prods)
        trigger_available = any(
            slug in available_slugs for slug in chosen_bundle["trigger"]
        )
        if not trigger_available:
            return []

        bundle_products = []

        # Pick trigger product
        trigger_prods = [p for p in m_prods
                         if prod_cat_slug.get(p["id"], "") in chosen_bundle["trigger"]]
        if trigger_prods:
            bundle_products.append(self.rng.choice(trigger_prods))

        # Pick required companions
        for slug_group in chosen_bundle["required"]:
            slugs = slug_group.split("|")
            candidates = [p for p in m_prods if prod_cat_slug.get(p["id"], "") in slugs]
            if candidates:
                bundle_products.append(self.rng.choice(candidates))

        # Pick optional companions (50% chance each)
        for slug_group in chosen_bundle["optional"]:
            if self.rng.random() < 0.5:
                slugs = slug_group.split("|")
                candidates = [p for p in m_prods if prod_cat_slug.get(p["id"], "") in slugs]
                if candidates:
                    bundle_products.append(self.rng.choice(candidates))

        return bundle_products if len(bundle_products) >= 2 else []
