#!/usr/bin/env python3
"""전자상거래 테스트 데이터베이스 생성기"""

from __future__ import annotations

import argparse
import os
import sys
import time

import yaml

from src.generators.products import ProductGenerator
from src.generators.customers import CustomerGenerator
from src.generators.staff import StaffGenerator
from src.generators.orders import OrderGenerator
from src.generators.payments import PaymentGenerator
from src.generators.shipping import ShippingGenerator
from src.generators.reviews import ReviewGenerator
from src.generators.inventory import InventoryGenerator
from src.generators.images import ImageGenerator, download_images
from src.generators.wishlists import WishlistGenerator
from src.generators.returns import ReturnGenerator
from src.generators.complaints import ComplaintGenerator
from src.generators.carts import CartGenerator
from src.generators.coupons import CouponGenerator
from src.exporters.sqlite_exporter import SQLiteExporter


def load_config(path: str = "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="전자상거래 테스트 DB 생성기")
    parser.add_argument("--size", choices=["small", "medium", "large"], help="데이터 규모")
    parser.add_argument("--seed", type=int, help="랜덤 시드 (기본: 42)")
    parser.add_argument("--target", choices=["sqlite", "mysql", "postgresql", "sqlserver", "oracle", "all"],
                        help="출력 대상 DB")
    parser.add_argument("--all", action="store_true", help="모든 DB 포맷 생성")
    parser.add_argument("--locale", choices=["ko", "en"], help="데이터 언어 (ko/en, 기본: ko)")
    parser.add_argument("--download-images", action="store_true", help="Pexels API로 실제 이미지 다운로드")
    parser.add_argument("--pexels-key", help="Pexels API 키 (또는 PEXELS_API_KEY 환경변수)")
    parser.add_argument("--config", default="config.yaml", help="설정 파일 경로")
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)

    if args.size:
        config["size"] = args.size
    if args.seed is not None:
        config["seed"] = args.seed
    if args.locale:
        config["locale"] = f"{args.locale}_{'KR' if args.locale == 'ko' else 'US'}"
    if args.all:
        config["targets"] = ["sqlite", "mysql", "postgresql", "sqlserver", "oracle"]
    elif args.target:
        config["targets"] = [args.target]

    seed = config["seed"]
    size = config["size"]
    scale = config["profiles"][size]["scale"]
    output_dir = config.get("output_dir", "./output")

    print(f"=== 전자상거래 테스트 DB 생성기 ===")
    print(f"규모: {size} (배율: {scale}x)")
    print(f"시드: {seed}")
    print(f"대상: {', '.join(config['targets'])}")
    print()

    t0 = time.time()

    # 1. 카테고리 / 공급업체 / 상품
    print("[1/13] 카테고리, 공급업체, 상품 생성...")
    prod_gen = ProductGenerator(config, seed)
    categories = prod_gen.generate_categories()
    suppliers = prod_gen.generate_suppliers()
    products = prod_gen.generate_products()
    print(f"  카테고리: {len(categories)}개, 공급업체: {len(suppliers)}개, 상품: {len(products)}개")

    # 2. 가격 이력
    print("[2/13] 가격 이력 생성...")
    product_prices = prod_gen.generate_product_prices(products)
    print(f"  가격 이력: {len(product_prices)}건")

    # 3. 상품 이미지
    print("[3/13] 상품 이미지 생성...")
    img_gen = ImageGenerator(config, seed + 12)
    product_images = img_gen.generate_product_images(products, categories)
    print(f"  이미지: {len(product_images)}건")

    # 4. 직원
    print("[4/13] 직원 생성...")
    staff_gen = StaffGenerator(config, seed + 1)
    staff = staff_gen.generate_staff()
    print(f"  직원: {len(staff)}명")

    # 4. 고객 / 배송지
    print("[5/13] 고객, 배송지 생성...")
    cust_gen = CustomerGenerator(config, seed + 2)
    customers = cust_gen.generate_customers()
    addresses = cust_gen.generate_addresses(customers)
    print(f"  고객: {len(customers)}명, 배송지: {len(addresses)}건")

    # 5. 쿠폰
    print("[6/13] 쿠폰 생성...")
    coupon_gen = CouponGenerator(config, seed + 3)
    coupons = coupon_gen.generate_coupons()
    print(f"  쿠폰: {len(coupons)}개")

    # 6. 주문 / 주문 상세
    print("[7/13] 주문, 주문 상세 생성...")
    order_gen = OrderGenerator(config, seed + 4)
    orders, order_items = order_gen.generate_orders(customers, addresses, products, staff)
    print(f"  주문: {len(orders)}건, 주문 상세: {len(order_items)}건")

    # 7. 결제
    print("[8/13] 결제 생성...")
    pay_gen = PaymentGenerator(config, seed + 5)
    payments = pay_gen.generate_payments(orders)
    # 입금자명 후처리 (계좌이체: 고객 이름 매핑)
    cust_name_map = {c["id"]: c["name"] for c in customers}
    order_cust_map = {o["id"]: o["customer_id"] for o in orders}
    for p in payments:
        if p["method"] == "bank_transfer" and p["depositor_name"] is None and p["status"] == "completed":
            cid = order_cust_map.get(p["order_id"])
            if cid:
                p["depositor_name"] = cust_name_map.get(cid)
    print(f"  결제: {len(payments)}건")

    # 8. 배송
    print("[9/13] 배송 생성...")
    ship_gen = ShippingGenerator(config, seed + 6)
    shipping = ship_gen.generate_shipping(orders)
    print(f"  배송: {len(shipping)}건")

    # 9. 리뷰
    print("[10/13] 리뷰 생성...")
    review_gen = ReviewGenerator(config, seed + 7)
    reviews = review_gen.generate_reviews(orders, order_items, products)
    print(f"  리뷰: {len(reviews)}건")

    # 10. 재고 / 장바구니 / 쿠폰 사용
    print("[11/13] 재고, 장바구니, 쿠폰 사용 이력 생성...")
    inv_gen = InventoryGenerator(config, seed + 8)
    inventory = inv_gen.generate_inventory(products, orders, order_items)

    cart_gen = CartGenerator(config, seed + 9)
    carts, cart_items = cart_gen.generate_carts(customers, products)

    coupon_usage = coupon_gen.generate_coupon_usage(coupons, orders)

    wish_gen = WishlistGenerator(config, seed + 13)
    wishlists = wish_gen.generate_wishlists(customers, products, orders, order_items)
    print(f"  재고: {len(inventory)}건, 장바구니: {len(carts)}건/{len(cart_items)}아이템, 쿠폰: {len(coupon_usage)}건, 찜: {len(wishlists)}건")

    # 11. 반품/교환
    print("[12/13] 반품/교환 생성...")
    return_gen = ReturnGenerator(config, seed + 10)
    returns = return_gen.generate_returns(orders, order_items, shipping)
    print(f"  반품: {len(returns)}건")

    # 12. 고객 문의/불만
    print("[13/13] 고객 문의/불만 생성...")
    complaint_gen = ComplaintGenerator(config, seed + 11)
    complaints = complaint_gen.generate_complaints(orders, customers, staff)
    print(f"  문의: {len(complaints)}건")

    # 고객 등급 업데이트
    _update_customer_grades(customers, orders, order_items, config)

    # 전체 데이터
    all_data = {
        "categories": categories,
        "suppliers": suppliers,
        "products": products,
        "product_images": product_images,
        "product_prices": product_prices,
        "customers": customers,
        "customer_addresses": addresses,
        "staff": staff,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
        "shipping": shipping,
        "reviews": reviews,
        "inventory_transactions": inventory,
        "carts": carts,
        "cart_items": cart_items,
        "coupons": coupons,
        "coupon_usage": coupon_usage,
        "wishlists": wishlists,
        "returns": returns,
        "complaints": complaints,
    }

    total_rows = sum(len(v) for v in all_data.values())
    gen_time = time.time() - t0
    print(f"\n데이터 생성 완료: 총 {total_rows:,}건 ({gen_time:.1f}초)")

    # 이미지 다운로드 (선택)
    if args.download_images:
        pexels_key = args.pexels_key or os.environ.get("PEXELS_API_KEY", "")
        if not pexels_key:
            print("\n[경고] --pexels-key 또는 PEXELS_API_KEY 환경변수가 필요합니다.")
            print("  무료 API 키: https://www.pexels.com/api/")
        else:
            print(f"\nPexels API로 이미지 다운로드 중...")
            product_images = download_images(
                products, categories, product_images,
                output_dir, pexels_key,
            )
            all_data["product_images"] = product_images

    # 내보내기
    t1 = time.time()
    for target in config["targets"]:
        if target == "sqlite":
            print(f"\nSQLite 내보내기...")
            exporter = SQLiteExporter(output_dir)
            db_path = exporter.export(all_data)
            file_size = os.path.getsize(db_path) / (1024 * 1024)
            print(f"  -> {db_path} ({file_size:.1f} MB)")
        else:
            print(f"\n{target} 내보내기는 아직 구현되지 않았습니다.")

    export_time = time.time() - t1
    total_time = time.time() - t0
    print(f"\n내보내기 완료 ({export_time:.1f}초)")
    print(f"전체 소요 시간: {total_time:.1f}초")


def _update_customer_grades(
    customers: list[dict],
    orders: list[dict],
    order_items: list[dict],
    config: dict,
):
    """최근 1년 구매 기준으로 고객 등급을 업데이트한다."""
    from datetime import datetime, timedelta

    grade_thresholds = config["customer_grades"]
    cutoff = datetime(config["end_year"], 6, 1) - timedelta(days=365)

    # 고객별 최근 1년 구매 합계
    spending: dict[int, float] = {}
    for o in orders:
        if o["status"] not in ("confirmed", "delivered"):
            continue
        ordered = datetime.strptime(o["ordered_at"], "%Y-%m-%d %H:%M:%S")
        if ordered >= cutoff:
            spending[o["customer_id"]] = spending.get(o["customer_id"], 0) + o["total_amount"]

    for c in customers:
        total = spending.get(c["id"], 0)
        if total >= grade_thresholds["VIP"]:
            c["grade"] = "VIP"
        elif total >= grade_thresholds["GOLD"]:
            c["grade"] = "GOLD"
        elif total >= grade_thresholds["SILVER"]:
            c["grade"] = "SILVER"
        else:
            c["grade"] = "BRONZE"

        c["point_balance"] = int(total * config["order"]["points_earn_rate"])


if __name__ == "__main__":
    main()
