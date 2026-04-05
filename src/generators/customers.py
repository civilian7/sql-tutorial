"""고객 및 배송지 데이터 생성"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator
from src.utils.growth import get_yearly_new_customers

class CustomerGenerator(BaseGenerator):

    def generate_customers(self) -> list[dict]:
        """연도별 성장 곡선에 따라 고객을 생성한다."""
        customers = []
        customer_id = 0
        edge = self.config["edge_cases"]
        email_domains = self.locale["email"]["customer_domains"]
        domains, domain_weights = zip(*email_domains)

        for year in range(self.start_year, self.end_year + 1):
            count = get_yearly_new_customers(year, self.config["yearly_growth"], self.scale)
            for _ in range(count):
                customer_id += 1
                created = self.random_date_in_year(year)

                name = self.fake.name()
                domain = self.rng.choices(domains, weights=domain_weights, k=1)[0]
                email = f"user{customer_id}@{domain}"

                birth_date = None
                if self.rng.random() >= edge["null_birth_date"]:
                    # 컴퓨터 쇼핑몰 연령 분포: 20~30대 집중
                    birth_year = self.rng.choices(
                        range(1960, 2006),
                        weights=[
                            *([0.5] * 5),   # 1960~1964 (60대+): 낮음
                            *([0.8] * 5),   # 1965~1969 (50대후반)
                            *([1.2] * 5),   # 1970~1974 (50대초반)
                            *([2.0] * 5),   # 1975~1979 (40대후반)
                            *([3.0] * 5),   # 1980~1984 (40대초반)
                            *([4.5] * 5),   # 1985~1989 (30대후반)
                            *([5.0] * 5),   # 1990~1994 (30대초반): 피크
                            *([4.5] * 5),   # 1995~1999 (20대후반)
                            *([3.0] * 5),   # 2000~2004 (20대초반)
                            *([1.5] * 1),   # 2005 (10대후반)
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
                    # 컴퓨터/주변기기 쇼핑몰: 남성 비율 약 65%
                    gender = self.rng.choices(["M", "F"], weights=[0.65, 0.35], k=1)[0]

                password_hash = hashlib.sha256(
                    f"user{customer_id}pass".encode()
                ).hexdigest()

                now = datetime(self.end_year, 6, 30)
                years_since_join = (now - created).days / 365.0

                # 휴면/활동 상태 결정 — 가입이 오래될수록 휴면 확률 증가
                #   1년 미만: 5% 휴면
                #   1~3년:  15% 휴면
                #   3~5년:  30% 휴면
                #   5년+:   45% 휴면
                if years_since_join < 1:
                    dormant_prob = 0.05
                elif years_since_join < 3:
                    dormant_prob = 0.15
                elif years_since_join < 5:
                    dormant_prob = 0.30
                else:
                    dormant_prob = 0.45

                is_dormant = self.rng.random() < dormant_prob

                # 탈퇴 (is_active=0): 전체 3%
                is_active = 1
                if self.rng.random() < 0.03:
                    is_active = 0

                # last_login_at 결정
                if is_active == 0:
                    # 탈퇴 고객: 마지막 로그인은 가입 후 일정 기간 내
                    activity_end = min(
                        created + timedelta(days=self.rng.randint(30, 730)),
                        now,
                    )
                    last_login = self.fmt_dt(self.random_datetime(created, activity_end))
                elif is_dormant:
                    # 휴면 고객: 마지막 로그인이 1년 이상 전
                    activity_end = min(
                        created + timedelta(days=self.rng.randint(30, max(31, int(years_since_join * 200)))),
                        now - timedelta(days=365),
                    )
                    if activity_end <= created:
                        activity_end = created + timedelta(days=1)
                    last_login = self.fmt_dt(self.random_datetime(created, activity_end))
                else:
                    # 활성 고객: 최근 6개월 내 로그인
                    recent_start = max(created, now - timedelta(days=180))
                    last_login = self.fmt_dt(self.random_datetime(recent_start, now))

                # 가입만 하고 로그인 안 한 고객: ~5%
                if self.rng.random() < 0.05:
                    last_login = None

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
                    "is_active": is_active,
                    "last_login_at": last_login,
                    "created_at": self.fmt_dt(created),
                    "updated_at": self.fmt_dt(created),
                })

        return customers

    def generate_addresses(self, customers: list[dict]) -> list[dict]:
        """고객별 배송지를 생성한다 (1~3개)."""
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
                })

        return addresses

    def _romanize_simple(self, name: str, uid: int) -> str:
        """한글 이름을 간단한 로마자로 변환한다."""
        # 간단한 매핑 대신 이름 해시 기반 유니크 아이디 사용
        return f"user{uid}"
