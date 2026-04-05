"""직원 데이터 생성"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.generators.base import BaseGenerator


class StaffGenerator(BaseGenerator):

    ROLES = ["admin", "manager", "staff"]

    def generate_staff(self) -> list[dict]:
        """직원 목록을 생성한다 (~50명)."""
        count = max(5, int(50 * self.scale))
        if count > 200:
            count = 200  # large 규모에서도 직원 수는 제한
        staff = []
        departments = self.locale["staff"]["departments"]
        domain = self.locale["email"]["staff_domain"]

        for i in range(1, count + 1):
            name = self.fake.name()
            hired_year = self.rng.randint(self.start_year, self.end_year)
            hired = datetime(hired_year, self.rng.randint(1, 12), self.rng.randint(1, 28))
            created = hired

            # 경영진은 소수
            if i <= 3:
                role = "admin"
                dept = departments[-1]  # Management/경영 is last
            elif i <= 10:
                role = "manager"
                dept = self.rng.choice(departments)
            else:
                role = "staff"
                dept = self.rng.choice(departments)

            is_active = 1
            if self.rng.random() < 0.1 and hired_year < self.end_year - 1:
                is_active = 0

            staff.append({
                "id": i,
                "email": f"staff{i}@{domain}",
                "name": name,
                "phone": self.generate_phone(),
                "department": dept,
                "role": role,
                "is_active": is_active,
                "hired_at": self.fmt_date(hired),
                "created_at": self.fmt_dt(created),
            })

        return staff
