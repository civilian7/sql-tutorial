"""Customer and shipping address data generation"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator
from src.utils.growth import get_yearly_new_customers

class CustomerGenerator(BaseGenerator):

    def generate_customers(self) -> list[dict]:
        """Generate customers following a yearly growth curve."""
        customers = []
        customer_id = 0
        edge = self.config["edge_cases"]
        email_domain = self.config["email"]["customer_domain"]

        for year in range(self.start_year, self.end_year + 1):
            count = get_yearly_new_customers(year, self.config["yearly_growth"], self.scale)
            for _ in range(count):
                customer_id += 1
                created = self.random_date_in_year(year)

                name = self.fake.name()
                email = f"user{customer_id}@{email_domain}"

                birth_date = None
                if self.rng.random() >= edge["null_birth_date"]:
                    # Age distribution for a computer store: concentrated in 20s~30s
                    birth_year = self.rng.choices(
                        range(1960, 2006),
                        weights=[
                            *([0.5] * 5),   # 1960~1964 (60s+): low
                            *([0.8] * 5),   # 1965~1969 (late 50s)
                            *([1.2] * 5),   # 1970~1974 (early 50s)
                            *([2.0] * 5),   # 1975~1979 (late 40s)
                            *([3.0] * 5),   # 1980~1984 (early 40s)
                            *([4.5] * 5),   # 1985~1989 (late 30s)
                            *([5.0] * 5),   # 1990~1994 (early 30s): peak
                            *([4.5] * 5),   # 1995~1999 (late 20s)
                            *([3.0] * 5),   # 2000~2004 (early 20s)
                            *([1.5] * 1),   # 2005 (late teens)
                        ],
                        k=1,
                    )[0]
                    birth_date = self.fmt_date(datetime(
                        birth_year,
                        self.rng.randint(1, 12),
                        self.rng.randint(1, 28),
                    ))

                gender = None
                if self.rng.random() >= edge["null_gender"]:
                    # Computer/peripherals store: ~65% male ratio
                    gender = self.rng.choices(["M", "F"], weights=[0.65, 0.35], k=1)[0]

                password_hash = hashlib.sha256(
                    f"user{customer_id}pass".encode()
                ).hexdigest()

                now = self.end_date
                years_since_join = (now - created).days / 365.0

                # Determine dormant/active status -- dormant probability increases with account age
                #   < 1 year:  5% dormant
                #   1~3 years: 15% dormant
                #   3~5 years: 30% dormant
                #   5+ years:  45% dormant
                if years_since_join < 1:
                    dormant_prob = 0.05
                elif years_since_join < 3:
                    dormant_prob = 0.15
                elif years_since_join < 5:
                    dormant_prob = 0.30
                else:
                    dormant_prob = 0.45

                is_dormant = self.rng.random() < dormant_prob

                # Deactivated (3%) or dormant (no login for 1+ year -> auto-dormant)
                is_active = 1
                if self.rng.random() < 0.03:
                    is_active = 0  # deactivated
                elif is_dormant:
                    is_active = 0  # dormant

                # Determine last_login_at
                if is_active == 0:
                    # Deactivated customer: last login within some period after signup
                    activity_end = min(
                        created + timedelta(days=self.rng.randint(30, 730)),
                        now,
                    )
                    last_login = self.fmt_dt(self.random_datetime(created, activity_end))
                elif is_dormant:
                    # Dormant customer: last login was 1+ year ago
                    activity_end = min(
                        created + timedelta(days=self.rng.randint(30, max(31, int(years_since_join * 200)))),
                        now - timedelta(days=365),
                    )
                    if activity_end <= created:
                        activity_end = created + timedelta(days=1)
                    last_login = self.fmt_dt(self.random_datetime(created, activity_end))
                else:
                    # Active customer: logged in within the last 6 months
                    recent_start = max(created, now - timedelta(days=180))
                    last_login = self.fmt_dt(self.random_datetime(recent_start, now))

                # Customers who signed up but never logged in: ~5%
                if self.rng.random() < 0.05:
                    last_login = None

                # Acquisition channel (weighted by year - ads grow over time)
                acq_channels = ["organic", "search_ad", "social", "referral", "direct"]
                base_weights = [0.30, 0.25, 0.20, 0.15, 0.10]
                # Social/ad channels grow over later years
                year_factor = (year - self.start_year) / max(1, self.end_year - self.start_year)
                adj_weights = [
                    base_weights[0] * (1.0 - year_factor * 0.3),  # organic shrinks
                    base_weights[1] * (1.0 + year_factor * 0.5),  # search_ad grows
                    base_weights[2] * (1.0 + year_factor * 0.8),  # social grows most
                    base_weights[3],
                    base_weights[4] * (1.0 - year_factor * 0.2),  # direct shrinks
                ]
                acq = self.rng.choices(acq_channels, weights=adj_weights, k=1)[0]

                customers.append({
                    "id": customer_id,
                    "email": email,
                    "password_hash": password_hash,
                    "name": name,
                    "phone": self.generate_phone(),
                    "birth_date": birth_date,
                    "gender": gender,
                    "grade": "BRONZE",
                    "point_balance": 0,
                    "acquisition_channel": acq,
                    "is_active": is_active,
                    "last_login_at": last_login,
                    "created_at": self.fmt_dt(created),
                    "updated_at": self.fmt_dt(created),
                })

        return customers

    def generate_addresses(self, customers: list[dict]) -> list[dict]:
        """Generate shipping addresses per customer (1~3 each).

        ~20% of addresses older than 1 year get an updated address1/zip_code
        to simulate customers moving.
        """
        addresses = []
        addr_id = 0
        labels = self.locale["customer"]["address_labels"]

        for c in customers:
            created = datetime.strptime(c["created_at"], "%Y-%m-%d %H:%M:%S")
            count = self.rng.choices([1, 2, 3], weights=[0.5, 0.35, 0.15], k=1)[0]
            for i in range(count):
                addr_id += 1
                addr_created = self.random_datetime(
                    created, created + timedelta(days=365)
                )
                addresses.append({
                    "id": addr_id,
                    "customer_id": c["id"],
                    "label": labels[i] if i < len(labels) else labels[-1],
                    "recipient_name": c["name"] if i == 0 else self.fake.name(),
                    "phone": c["phone"] if i == 0 else self.generate_phone(),
                    "zip_code": f"{self.rng.randint(10000, 99999)}",
                    "address1": self.fake.address().split("\n")[0],
                    "address2": f"{self.rng.randint(1, 30)}층 {self.rng.randint(101, 1520)}호" if self.rng.random() < 0.7 else None,
                    "is_default": 1 if i == 0 else 0,
                    "created_at": self.fmt_dt(addr_created),
                    "updated_at": self.fmt_dt(addr_created),
                })

        # Simulate address changes: ~20% of addresses older than 1 year
        now = self.end_date
        one_year_ago = now - timedelta(days=365)
        for addr in addresses:
            addr_created = datetime.strptime(addr["created_at"], "%Y-%m-%d %H:%M:%S")
            if addr_created >= one_year_ago:
                continue
            if self.rng.random() >= 0.20:
                continue

            # Pick a random update date between 1 year after creation and now
            update_start = addr_created + timedelta(days=365)
            if update_start > now:
                continue
            updated_at = self.random_datetime(update_start, now)
            addr["updated_at"] = self.fmt_dt(updated_at)
            addr["address1"] = self.fake.address().split("\n")[0]
            # 50% chance to also change zip_code (moved to a different area)
            if self.rng.random() < 0.50:
                addr["zip_code"] = f"{self.rng.randint(10000, 99999)}"

        return addresses

    def _romanize_simple(self, name: str, uid: int) -> str:
        """Convert a Korean name to a simple romanized form."""
        # Use hash-based unique ID instead of simple character mapping
        return f"user{uid}"
