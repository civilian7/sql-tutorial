"""Staff data generation"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.generators.base import BaseGenerator


class StaffGenerator(BaseGenerator):

    ROLES = ["admin", "manager", "staff"]

    def generate_staff(self) -> list[dict]:
        """Generate staff list (~50 members). Org hierarchy: admin→manager→staff."""
        count = max(5, int(50 * self.scale))
        if count > 200:
            count = 200  # Cap staff count even at large scale
        staff = []
        departments = self.locale["staff"]["departments"]
        domain = self.locale["email"]["staff_domain"]

        # Track manager IDs per department (for manager_id assignment)
        dept_managers: dict[str, list[int]] = {}
        admin_ids: list[int] = []

        for i in range(1, count + 1):
            name = self.fake.name()
            hired_year = self.rng.randint(self.start_year, self.end_year)
            hired = datetime(hired_year, self.rng.randint(1, 12), self.rng.randint(1, 28))
            created = hired

            # Few executives
            if i <= 3:
                role = "admin"
                dept = departments[-1]  # Management/경영 is last
            elif i <= 10:
                role = "manager"
                dept = self.rng.choice(departments)
            else:
                role = "staff"
                dept = self.rng.choice(departments)

            # Assign manager_id (org hierarchy)
            if role == "admin":
                # CEO (id=1) has manager_id=NULL, other admins report to CEO
                manager_id = None if i == 1 else 1
            elif role == "manager":
                # Managers report to one of the admins
                manager_id = self.rng.choice(admin_ids) if admin_ids else None
            else:
                # Staff report to a manager in the same department
                candidates = dept_managers.get(dept, [])
                if candidates:
                    manager_id = self.rng.choice(candidates)
                elif admin_ids:
                    manager_id = self.rng.choice(admin_ids)
                else:
                    manager_id = None

            is_active = 1
            if self.rng.random() < 0.1 and hired_year < self.end_year - 1:
                is_active = 0

            staff.append({
                "id": i,
                "manager_id": manager_id,
                "email": f"staff{i}@{domain}",
                "name": name,
                "phone": self.generate_phone(),
                "department": dept,
                "role": role,
                "is_active": is_active,
                "hired_at": self.fmt_date(hired),
                "created_at": self.fmt_dt(created),
            })

            # Track for hierarchy assignment
            if role == "admin":
                admin_ids.append(i)
            elif role == "manager":
                dept_managers.setdefault(dept, []).append(i)

        return staff
