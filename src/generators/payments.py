"""결제 데이터 생성"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from src.generators.base import BaseGenerator


# 할부 개월 분포 (금액대별 차등)
INSTALLMENT_MONTHS = {
    "low":  {"0": 0.90, "2": 0.05, "3": 0.05},                                     # ~30만
    "mid":  {"0": 0.40, "2": 0.15, "3": 0.20, "6": 0.15, "10": 0.07, "12": 0.03},  # 30~100만
    "high": {"0": 0.15, "3": 0.15, "6": 0.25, "10": 0.20, "12": 0.15, "24": 0.10}, # 100만+
}



class PaymentGenerator(BaseGenerator):

    def generate_payments(self, orders: list[dict]) -> list[dict]:
        """주문별 결제 데이터를 생성한다."""
        payments = []
        payment_id = 0
        methods = self.config["payment_methods"]

        card_issuers_data = self.locale["payment"]["card_issuers"]
        card_issuers = list(card_issuers_data.keys())
        card_issuer_w = list(card_issuers_data.values())
        banks_data = self.locale["payment"]["banks"]
        banks = list(banks_data.keys())
        bank_w = list(banks_data.values())
        easy_pay_data = self.locale["payment"]["easy_pay"]
        receipt_types = self.locale["payment"]["receipt_types"]

        for order in orders:
            payment_id += 1
            method = self.weighted_choice(methods)
            ordered_at = datetime.strptime(order["ordered_at"], "%Y-%m-%d %H:%M:%S")
            amount = order["total_amount"]

            # 결제 상태 결정
            if order["status"] == "cancelled" and order["cancelled_at"]:
                if self.rng.random() < 0.5:
                    status = "failed"
                    paid_at = None
                    refunded_at = None
                else:
                    status = "refunded"
                    paid_at = self.fmt_dt(ordered_at + timedelta(minutes=self.rng.randint(1, 30)))
                    refunded_at = order["cancelled_at"]
            elif order["status"] in ("return_requested", "returned"):
                status = "refunded"
                paid_at = self.fmt_dt(ordered_at + timedelta(minutes=self.rng.randint(1, 30)))
                refunded_at = self.fmt_dt(ordered_at + timedelta(days=self.rng.randint(7, 21)))
            elif order["status"] == "pending":
                status = "pending"
                paid_at = None
                refunded_at = None
            else:
                status = "completed"
                paid_at = self.fmt_dt(ordered_at + timedelta(minutes=self.rng.randint(1, 30)))
                refunded_at = None

            # PG 거래번호
            pg_tid = None
            if method != "point" and status in ("completed", "refunded"):
                pg_tid = f"PG-{uuid.UUID(int=self.rng.getrandbits(128)).hex[:16].upper()}"

            # 결제 수단별 상세 정보
            card_issuer = None
            card_approval_no = None
            installment_months = None
            bank_name = None
            account_no = None
            depositor_name = None
            easy_pay_method = None
            receipt_type = None
            receipt_no = None

            if method == "card":
                card_issuer = self.rng.choices(card_issuers, weights=card_issuer_w, k=1)[0]
                if status in ("completed", "refunded"):
                    card_approval_no = f"{self.rng.randint(10000000, 99999999)}"

                # 할부 (금액대별)
                if amount < 300000:
                    tier = "low"
                elif amount < 1000000:
                    tier = "mid"
                else:
                    tier = "high"
                inst_map = INSTALLMENT_MONTHS[tier]
                installment_months = int(self.rng.choices(
                    list(inst_map.keys()), weights=list(inst_map.values()), k=1,
                )[0])

            elif method == "bank_transfer":
                bank_name = self.rng.choices(banks, weights=bank_w, k=1)[0]
                if status in ("completed", "refunded"):
                    depositor_name = order.get("_customer_name")  # 나중에 매핑
                    if not depositor_name:
                        depositor_name = None  # generate.py에서 후처리

            elif method == "virtual_account":
                bank_name = self.rng.choices(banks, weights=bank_w, k=1)[0]
                account_no = f"{self.rng.randint(100, 999)}-{self.rng.randint(100000, 999999)}-{self.rng.randint(10, 99)}-{self.rng.randint(100, 999)}"

            elif method in ("kakao_pay", "naver_pay"):
                ep_methods = easy_pay_data[method]
                easy_pay_method = self.rng.choices(
                    list(ep_methods.keys()), weights=list(ep_methods.values()), k=1,
                )[0]

            # 현금영수증 (계좌이체/가상계좌: 70%, 카카오/네이버: 20%)
            if method in ("bank_transfer", "virtual_account") and status == "completed":
                if self.rng.random() < 0.70:
                    receipt_type = self.rng.choice(receipt_types)
                    receipt_no = f"CR-{self.rng.randint(10000000, 99999999)}"
            elif method in ("kakao_pay", "naver_pay") and status == "completed":
                if self.rng.random() < 0.20:
                    receipt_type = receipt_types[0]
                    receipt_no = f"CR-{self.rng.randint(10000000, 99999999)}"

            payments.append({
                "id": payment_id,
                "order_id": order["id"],
                "method": method,
                "amount": amount,
                "status": status,
                "pg_transaction_id": pg_tid,
                "card_issuer": card_issuer,
                "card_approval_no": card_approval_no,
                "installment_months": installment_months,
                "bank_name": bank_name,
                "account_no": account_no,
                "depositor_name": depositor_name,
                "easy_pay_method": easy_pay_method,
                "receipt_type": receipt_type,
                "receipt_no": receipt_no,
                "paid_at": paid_at,
                "refunded_at": refunded_at,
                "created_at": order["created_at"],
            })

        return payments
