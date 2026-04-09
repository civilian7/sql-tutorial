"""Customer grade change history generation -- for SCD Type 2 practice"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


GRADES = ["BRONZE", "SILVER", "GOLD", "VIP"]


class GradeHistoryGenerator(BaseGenerator):

    def generate_grade_history(
        self, customers: list[dict], orders: list[dict],
    ) -> list[dict]:
        """Generate grade change history for each customer.

        Logic:
        1. BRONZE on signup
        2. Re-evaluate grade on Jan 1 each year based on previous year's spending (yearly_review)
        3. Record upgrade/downgrade when grade changes
        """
        rows = []
        row_id = 0
        thresholds = self.config["customer_grades"]

        # Build per-customer per-year spending totals
        cust_yearly_spending: dict[int, dict[int, float]] = {}
        for o in orders:
            if o["status"] not in ("confirmed", "delivered"):
                continue
            year = int(o["ordered_at"][:4])
            cid = o["customer_id"]
            if cid not in cust_yearly_spending:
                cust_yearly_spending[cid] = {}
            cust_yearly_spending[cid][year] = (
                cust_yearly_spending[cid].get(year, 0) + o["total_amount"]
            )

        for c in customers:
            created = datetime.strptime(c["created_at"], "%Y-%m-%d %H:%M:%S")
            join_year = created.year

            # 1. BRONZE on signup
            row_id += 1
            current_grade = "BRONZE"
            rows.append({
                "id": row_id,
                "customer_id": c["id"],
                "old_grade": None,
                "new_grade": "BRONZE",
                "changed_at": c["created_at"],
                "reason": "signup",
            })

            # 2. Re-evaluate grade on Jan 1 each year
            yearly = cust_yearly_spending.get(c["id"], {})
            for year in range(join_year + 1, self.end_year + 1):
                prev_spending = yearly.get(year - 1, 0)

                if prev_spending >= thresholds["VIP"]:
                    new_grade = "VIP"
                elif prev_spending >= thresholds["GOLD"]:
                    new_grade = "GOLD"
                elif prev_spending >= thresholds["SILVER"]:
                    new_grade = "SILVER"
                else:
                    new_grade = "BRONZE"

                if new_grade != current_grade:
                    row_id += 1
                    old_idx = GRADES.index(current_grade)
                    new_idx = GRADES.index(new_grade)
                    reason = "upgrade" if new_idx > old_idx else "downgrade"

                    rows.append({
                        "id": row_id,
                        "customer_id": c["id"],
                        "old_grade": current_grade,
                        "new_grade": new_grade,
                        "changed_at": f"{year}-01-01 00:00:00",
                        "reason": reason,
                    })
                    current_grade = new_grade

        return rows
