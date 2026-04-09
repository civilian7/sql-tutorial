"""Product Q&A generation.

Generates customer questions about products and seller answers.
Uses parent_id self-join for question→answer threading.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


class QnAGenerator(BaseGenerator):

    def generate_qna(
        self,
        customers: list[dict],
        products: list[dict],
        staff: list[dict],
    ) -> list[dict]:
        """Generate product Q&A entries (questions + answers)."""
        rows = []
        qna_id = 0

        locale_qna = self.locale.get("qna", {})
        questions = locale_qna.get("questions", [
            "Is this compatible with my system?",
            "What is the warranty period?",
            "When will this be back in stock?",
            "Does this come with cables included?",
            "What is the actual power consumption?",
            "Is there a newer model coming soon?",
            "Can I use this with a Mac?",
            "What is the return policy for this item?",
            "Is this product new or refurbished?",
            "Does this support overclocking?",
            "What are the exact dimensions?",
            "Is the manual available in English?",
            "How loud is the fan under load?",
            "Can I install an additional SSD?",
            "What PSU wattage do you recommend for this?",
        ])
        answers = locale_qna.get("answers", [
            "Yes, it is compatible. Please check the specifications for details.",
            "The warranty period is 1 year from the date of purchase.",
            "We expect restock within 2 weeks. You can set a notification.",
            "Yes, all necessary cables are included in the package.",
            "The actual power consumption is listed in the spec sheet on this page.",
            "We cannot disclose unreleased product information. Please stay tuned.",
            "Yes, it works with both Windows and Mac.",
            "You can return within 7 days of delivery. Please refer to our return policy.",
            "All products sold here are brand new, factory sealed.",
            "Yes, overclocking is supported. Please refer to the BIOS settings guide.",
            "Dimensions are listed in the product specification section below.",
            "Yes, a multilingual manual is included.",
            "Under full load, fan noise is approximately 35dB.",
            "Yes, there is an additional M.2 slot available.",
            "We recommend at least 650W for this configuration.",
        ])

        active_customers = [c for c in customers if c["is_active"]]
        active_products = [p for p in products if p["is_active"]]
        active_staff = [s for s in staff if s["is_active"]]

        if not active_customers or not active_products:
            return rows

        target_count = max(50, int(5000 * self.scale))

        for _ in range(target_count):
            customer = self.rng.choice(active_customers)
            product = self.rng.choice(active_products)

            cust_created = datetime.strptime(customer["created_at"], "%Y-%m-%d %H:%M:%S")
            question_at = self.random_datetime(cust_created, self.end_date)

            # Question
            qna_id += 1
            question_id = qna_id
            rows.append({
                "id": qna_id,
                "product_id": product["id"],
                "customer_id": customer["id"],
                "staff_id": None,
                "parent_id": None,  # top-level question
                "content": self.rng.choice(questions),
                "is_answered": 0,
                "created_at": self.fmt_dt(question_at),
            })

            # Answer (85% response rate, within 1~48 hours)
            if self.rng.random() < 0.85 and active_staff:
                answer_delay = timedelta(hours=self.rng.randint(1, 48))
                answer_at = question_at + answer_delay
                if answer_at <= self.end_date:
                    qna_id += 1
                    staff_member = self.rng.choice(active_staff)
                    rows.append({
                        "id": qna_id,
                        "product_id": product["id"],
                        "customer_id": None,  # staff answers, not customer
                        "staff_id": staff_member["id"],
                        "parent_id": question_id,  # self-join reference
                        "content": self.rng.choice(answers),
                        "is_answered": 1,
                        "created_at": self.fmt_dt(answer_at),
                    })
                    # Mark question as answered
                    rows[-2]["is_answered"] = 1

                    # Follow-up question (15% chance)
                    if self.rng.random() < 0.15:
                        followup_at = answer_at + timedelta(hours=self.rng.randint(1, 72))
                        if followup_at <= self.end_date:
                            qna_id += 1
                            rows.append({
                                "id": qna_id,
                                "product_id": product["id"],
                                "customer_id": customer["id"],
                                "staff_id": None,
                                "parent_id": question_id,  # reply in same thread
                                "content": self.rng.choice(questions),
                                "is_answered": 0,
                                "created_at": self.fmt_dt(followup_at),
                            })

        return rows
