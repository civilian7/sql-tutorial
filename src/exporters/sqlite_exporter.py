"""SQLite3 데이터베이스 익스포터"""

from __future__ import annotations

import os
import sqlite3
from typing import Any


SCHEMA_SQL = """
-- =============================================
-- 상품 카테고리 (계층형: 대분류 > 중분류 > 소분류)
-- =============================================
CREATE TABLE categories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id       INTEGER NULL REFERENCES categories(id),  -- 상위 카테고리 (NULL=최상위)
    name            TEXT NOT NULL,                           -- 카테고리명
    slug            TEXT NOT NULL UNIQUE,                    -- URL용 식별자
    depth           INTEGER NOT NULL DEFAULT 0,              -- 0=대분류, 1=중분류, 2=소분류
    sort_order      INTEGER NOT NULL DEFAULT 0,              -- 정렬 순서
    is_active       INTEGER NOT NULL DEFAULT 1,              -- 활성 여부 (0/1)
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- 공급업체 (상품 납품처)
-- =============================================
CREATE TABLE suppliers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name    TEXT NOT NULL,                           -- 회사명
    business_number TEXT NOT NULL,                           -- 사업자등록번호 (가상)
    contact_name    TEXT NOT NULL,                           -- 담당자명
    phone           TEXT NOT NULL,                           -- 020-XXXX-XXXX (가상번호)
    email           TEXT NOT NULL,                           -- contact@xxx.test.kr
    address         TEXT,                                    -- 사업장 주소
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- 상품 (컴퓨터/주변기기)
-- =============================================
CREATE TABLE products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id     INTEGER NOT NULL REFERENCES categories(id),
    supplier_id     INTEGER NOT NULL REFERENCES suppliers(id),
    name            TEXT NOT NULL,                           -- 상품명
    sku             TEXT NOT NULL UNIQUE,                    -- 재고관리코드 (예: LA-GEN-삼성-00001)
    brand           TEXT NOT NULL,                           -- 브랜드명
    model_number    TEXT,                                    -- 모델번호
    description     TEXT,                                    -- 상품 설명
    price           REAL NOT NULL CHECK(price >= 0),           -- 현재 판매가 (원)
    cost_price      REAL NOT NULL CHECK(cost_price >= 0),    -- 원가 (원)
    stock_qty  INTEGER NOT NULL DEFAULT 0,              -- 현재 재고 수량
    weight_grams    INTEGER,                                 -- 배송 무게 (g)
    is_active       INTEGER NOT NULL DEFAULT 1,              -- 판매 중 여부
    discontinued_at TEXT NULL,                               -- 단종일 (NULL=판매중)
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- 상품 이미지 (상품당 1~5장)
-- =============================================
CREATE TABLE product_images (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    image_url       TEXT NOT NULL,                           -- 이미지 경로/URL
    file_name       TEXT NOT NULL,                           -- 파일명 (예: 42_1.jpg)
    image_type      TEXT NOT NULL,                           -- main/angle/side/back/detail/package/lifestyle/accessory/size_comparison
    alt_text        TEXT,                                    -- 대체 텍스트
    width           INTEGER,                                 -- 이미지 너비 (px)
    height          INTEGER,                                 -- 이미지 높이 (px)
    file_size       INTEGER,                                 -- 파일 크기 (bytes, 다운로드 후)
    sort_order      INTEGER NOT NULL DEFAULT 1,              -- 표시 순서
    is_primary      INTEGER NOT NULL DEFAULT 0,              -- 대표 이미지 여부
    created_at      TEXT NOT NULL
);

-- =============================================
-- 상품 가격 이력 (가격 변동 추적)
-- =============================================
CREATE TABLE product_prices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    price           REAL NOT NULL,                           -- 해당 기간 판매가
    started_at      TEXT NOT NULL,                           -- 적용 시작일
    ended_at        TEXT NULL,                               -- 적용 종료일 (NULL=현재가)
    change_reason   TEXT                                     -- regular/promotion/price_drop/cost_increase
);

-- =============================================
-- 고객
-- =============================================
CREATE TABLE customers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email           TEXT NOT NULL UNIQUE,                    -- 이메일 (가상 도메인)
    password_hash   TEXT NOT NULL,                           -- SHA-256 해시 (가상)
    name            TEXT NOT NULL,                           -- 고객명
    phone           TEXT NOT NULL,                           -- 020-XXXX-XXXX (가상번호)
    birth_date      TEXT NULL,                               -- 생년월일 (YYYY-MM-DD, ~15% NULL)
    gender          TEXT NULL,                               -- M/F (NULL ~10%, 남성 65%)
    grade           TEXT NOT NULL DEFAULT 'BRONZE' CHECK(grade IN ('BRONZE','SILVER','GOLD','VIP')),
    point_balance   INTEGER NOT NULL DEFAULT 0 CHECK(point_balance >= 0),
    is_active       INTEGER NOT NULL DEFAULT 1,              -- 활성 여부 (0=탈퇴)
    last_login_at   TEXT NULL,                               -- 마지막 로그인 (NULL=미접속)
    created_at      TEXT NOT NULL,                           -- 가입일
    updated_at      TEXT NOT NULL
);

-- =============================================
-- 고객 배송지 (1인당 1~3개)
-- =============================================
CREATE TABLE customer_addresses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    label           TEXT NOT NULL,                           -- 자택/회사/기타
    recipient_name  TEXT NOT NULL,                           -- 수령인
    phone           TEXT NOT NULL,                           -- 수령인 연락처
    zip_code        TEXT NOT NULL,                           -- 우편번호
    address1        TEXT NOT NULL,                           -- 기본 주소
    address2        TEXT,                                    -- 상세 주소
    is_default      INTEGER NOT NULL DEFAULT 0,              -- 기본 배송지 여부
    created_at      TEXT NOT NULL
);

-- =============================================
-- 직원/관리자
-- =============================================
CREATE TABLE staff (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email           TEXT NOT NULL UNIQUE,                    -- staffN@techshop-staff.kr
    name            TEXT NOT NULL,
    phone           TEXT NOT NULL,
    department      TEXT NOT NULL,                           -- 영업/물류/CS/마케팅/개발/경영
    role            TEXT NOT NULL,                           -- admin/manager/staff
    is_active       INTEGER NOT NULL DEFAULT 1,
    hired_at        TEXT NOT NULL,                           -- 입사일
    created_at      TEXT NOT NULL
);

-- =============================================
-- 주문
-- =============================================
CREATE TABLE orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number    TEXT NOT NULL UNIQUE,                    -- ORD-YYYYMMDD-NNNNN
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    address_id      INTEGER NOT NULL REFERENCES customer_addresses(id),
    staff_id        INTEGER NULL REFERENCES staff(id),      -- CS 담당자 (취소/반품 시)
    status          TEXT NOT NULL,                           -- pending/paid/preparing/shipped/delivered/confirmed/cancelled/return_requested/returned
    total_amount    REAL NOT NULL,                           -- 최종 결제 금액
    discount_amount REAL NOT NULL DEFAULT 0,                 -- 할인 합계
    shipping_fee    REAL NOT NULL DEFAULT 0,                 -- 배송비 (5만원 이상 무료)
    point_used      INTEGER NOT NULL DEFAULT 0,              -- 사용 적립금
    point_earned    INTEGER NOT NULL DEFAULT 0,              -- 적립 예정 포인트
    notes           TEXT NULL,                               -- 배송 메모 (~35%)
    ordered_at      TEXT NOT NULL,                           -- 주문일시
    completed_at    TEXT NULL,                               -- 구매확정일
    cancelled_at    TEXT NULL,                               -- 취소일
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- 주문 상세 (주문당 1~5개 아이템)
-- =============================================
CREATE TABLE order_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    product_id      INTEGER NOT NULL REFERENCES products(id),
    quantity        INTEGER NOT NULL CHECK(quantity > 0),     -- 수량
    unit_price      REAL NOT NULL CHECK(unit_price >= 0),    -- 주문 시점 단가
    discount_amount REAL NOT NULL DEFAULT 0,                 -- 아이템 할인
    subtotal        REAL NOT NULL                            -- (단가 x 수량) - 할인
);

-- =============================================
-- 결제
-- card: 카드사/승인번호/할부
-- bank_transfer: 은행/입금자명
-- virtual_account: 은행/가상계좌번호
-- kakao_pay/naver_pay: 간편결제 내부 수단
-- point: 포인트 전액 결제
-- =============================================
CREATE TABLE payments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    method          TEXT NOT NULL,                           -- card/bank_transfer/virtual_account/kakao_pay/naver_pay/point
    amount          REAL NOT NULL CHECK(amount >= 0),         -- 결제 금액
    status          TEXT NOT NULL CHECK(status IN ('pending','completed','failed','refunded')),
    pg_transaction_id TEXT NULL,                             -- PG사 거래번호 (가상)
    card_issuer     TEXT NULL,                               -- 카드사 (신한/삼성/KB국민/현대/롯데/하나/우리/NH농협/BC)
    card_approval_no TEXT NULL,                              -- 카드 승인번호 (8자리)
    installment_months INTEGER NULL,                         -- 할부 개월 (0=일시불)
    bank_name       TEXT NULL,                               -- 은행명 (계좌이체/가상계좌)
    account_no      TEXT NULL,                               -- 가상계좌 번호
    depositor_name  TEXT NULL,                               -- 입금자명 (계좌이체)
    easy_pay_method TEXT NULL,                               -- 간편결제 내부 수단 (카카오페이머니/연결카드 등)
    receipt_type    TEXT NULL,                               -- 소득공제/지출증빙 (현금영수증)
    receipt_no      TEXT NULL,                               -- 현금영수증 번호
    paid_at         TEXT NULL,                               -- 결제 완료 시각
    refunded_at     TEXT NULL,                               -- 환불 시각
    created_at      TEXT NOT NULL
);

-- =============================================
-- 배송 (정방향 배송)
-- =============================================
CREATE TABLE shipping (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    carrier         TEXT NOT NULL,                           -- CJ대한통운/한진택배/로젠택배/우체국택배
    tracking_number TEXT NULL,                               -- 운송장 번호
    status          TEXT NOT NULL,                           -- preparing/shipped/in_transit/delivered/returned
    shipped_at      TEXT NULL,                               -- 출고일
    delivered_at    TEXT NULL,                               -- 배송완료일 (반드시 shipped_at 이후)
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- 상품 리뷰 (구매확정 주문의 ~25%)
-- =============================================
CREATE TABLE reviews (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    rating          INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),  -- 1~5점 (5점 40%, 1점 5%)
    title           TEXT NULL,                               -- 리뷰 제목 (~80%)
    content         TEXT NULL,                               -- 리뷰 본문
    is_verified     INTEGER NOT NULL DEFAULT 1,              -- 구매 인증 여부
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- 입출고 이력 (재고 변동 추적)
-- =============================================
CREATE TABLE inventory_transactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    type            TEXT NOT NULL,                           -- inbound/outbound/return/adjustment
    quantity        INTEGER NOT NULL,                        -- 양수=입고, 음수=출고
    reference_id    INTEGER NULL,                            -- 관련 주문 ID
    notes           TEXT NULL,                               -- 초기입고/정기입고/반품입고
    created_at      TEXT NOT NULL
);

-- =============================================
-- 장바구니
-- =============================================
CREATE TABLE carts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    status          TEXT NOT NULL DEFAULT 'active',          -- active/converted/abandoned
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- 장바구니 상세
-- =============================================
CREATE TABLE cart_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id         INTEGER NOT NULL REFERENCES carts(id),
    product_id      INTEGER NOT NULL REFERENCES products(id),
    quantity        INTEGER NOT NULL DEFAULT 1,
    added_at        TEXT NOT NULL
);

-- =============================================
-- 쿠폰 (percent: 할인율, fixed: 고정금액)
-- =============================================
CREATE TABLE coupons (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT NOT NULL UNIQUE,                    -- 쿠폰 코드 (CP2401001)
    name            TEXT NOT NULL,                           -- 쿠폰명
    type            TEXT NOT NULL,                           -- percent/fixed
    discount_value  REAL NOT NULL CHECK(discount_value > 0),  -- 할인율(%) 또는 할인금액(원)
    min_order_amount REAL NULL,                              -- 최소 주문금액
    max_discount    REAL NULL,                               -- 최대 할인금액 (percent 타입)
    usage_limit     INTEGER NULL,                            -- 전체 사용 한도
    per_user_limit  INTEGER NOT NULL DEFAULT 1,              -- 1인당 사용 한도
    is_active       INTEGER NOT NULL DEFAULT 1,
    started_at      TEXT NOT NULL,                           -- 유효기간 시작
    expired_at      TEXT NOT NULL,                           -- 유효기간 종료
    created_at      TEXT NOT NULL
);

-- =============================================
-- 쿠폰 사용 이력
-- =============================================
CREATE TABLE coupon_usage (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_id       INTEGER NOT NULL REFERENCES coupons(id),
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    discount_amount REAL NOT NULL,                           -- 실제 할인 금액
    used_at         TEXT NOT NULL
);

-- =============================================
-- 반품/교환 (역물류 + 검수 + 환불 추적)
-- =============================================
CREATE TABLE returns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    return_type     TEXT NOT NULL,                           -- refund/exchange
    reason          TEXT NOT NULL,                           -- defective/wrong_item/change_of_mind/damaged_in_transit/not_as_described/late_delivery
    reason_detail   TEXT NOT NULL,                           -- 상세 사유 설명
    status          TEXT NOT NULL,                           -- requested/pickup_scheduled/in_transit/completed
    is_partial      INTEGER NOT NULL DEFAULT 0,              -- 부분반품 여부 (~17%)
    refund_amount   REAL NOT NULL,                           -- 환불 금액
    refund_status   TEXT NOT NULL,                           -- pending/refunded/exchanged/partial_refund
    carrier         TEXT NOT NULL,                           -- 수거 택배사
    tracking_number TEXT NOT NULL,                           -- 수거 운송장 번호
    requested_at    TEXT NOT NULL,                           -- 반품 요청일
    pickup_at       TEXT NOT NULL,                           -- 수거 예정/완료일
    received_at     TEXT NULL,                               -- 물류센터 입고일
    inspected_at    TEXT NULL,                               -- 검수 완료일
    inspection_result TEXT NULL,                             -- good/opened_good/defective/unsellable
    completed_at    TEXT NULL,                               -- 처리 완료일
    created_at      TEXT NOT NULL
);

-- =============================================
-- 위시리스트/찜 (M:N: customers ↔ products)
-- =============================================
CREATE TABLE wishlists (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    product_id      INTEGER NOT NULL REFERENCES products(id),
    notify_on_sale  INTEGER NOT NULL DEFAULT 0,              -- 가격 하락 알림 (0/1)
    created_at      TEXT NOT NULL,
    UNIQUE(customer_id, product_id)                          -- 동일 고객-상품 중복 방지
);

-- =============================================
-- 고객 문의/불만 (CS)
-- =============================================
CREATE TABLE complaints (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NULL REFERENCES orders(id),     -- 주문 연관 문의 (NULL=일반문의)
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    staff_id        INTEGER NULL REFERENCES staff(id),      -- 담당 CS 직원
    category        TEXT NOT NULL,                           -- product_defect/delivery_issue/wrong_item/refund_request/exchange_request/general_inquiry/price_inquiry
    channel         TEXT NOT NULL,                           -- website/phone/email/chat/kakao
    priority        TEXT NOT NULL,                           -- low/medium/high/urgent
    status          TEXT NOT NULL,                           -- open/resolved/closed
    title           TEXT NOT NULL,                           -- 문의 제목
    content         TEXT NOT NULL,                           -- 문의 내용
    resolution      TEXT NULL,                               -- 처리 결과 (해결 시)
    created_at      TEXT NOT NULL,                           -- 접수일
    resolved_at     TEXT NULL,                               -- 해결일
    closed_at       TEXT NULL                                -- 종료일
);
"""

INDEX_SQL = """
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_supplier_id ON products(supplier_id);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_product_images_product_id ON product_images(product_id);
CREATE INDEX idx_product_prices_product_id ON product_prices(product_id);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customer_addresses_customer_id ON customer_addresses(customer_id);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_ordered_at ON orders(ordered_at);
CREATE INDEX idx_orders_order_number ON orders(order_number);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_customer_status ON orders(customer_id, status);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_order_items_order_product ON order_items(order_id, product_id);
CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_shipping_order_id ON shipping(order_id);
CREATE INDEX idx_reviews_product_id ON reviews(product_id);
CREATE INDEX idx_reviews_customer_id ON reviews(customer_id);
CREATE INDEX idx_reviews_product_rating ON reviews(product_id, rating);
CREATE INDEX idx_inventory_product_id ON inventory_transactions(product_id);
CREATE INDEX idx_carts_customer_id ON carts(customer_id);
CREATE INDEX idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX idx_coupon_usage_coupon_id ON coupon_usage(coupon_id);
CREATE INDEX idx_coupon_usage_customer_id ON coupon_usage(customer_id);
CREATE INDEX idx_coupon_usage_order_id ON coupon_usage(order_id);
CREATE INDEX idx_returns_order_id ON returns(order_id);
CREATE INDEX idx_returns_customer_id ON returns(customer_id);
CREATE INDEX idx_returns_status ON returns(status);
CREATE INDEX idx_returns_reason ON returns(reason);
CREATE INDEX idx_complaints_order_id ON complaints(order_id);
CREATE INDEX idx_complaints_customer_id ON complaints(customer_id);
CREATE INDEX idx_complaints_staff_id ON complaints(staff_id);
CREATE INDEX idx_complaints_category ON complaints(category);
CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_wishlists_customer_id ON wishlists(customer_id);
CREATE INDEX idx_wishlists_product_id ON wishlists(product_id);
"""

VIEW_SQL = """
-- =============================================
-- VIEW: 월별 매출 요약
-- 학습 포인트: GROUP BY, 날짜 함수, 집계 함수, ORDER BY
-- =============================================
CREATE VIEW v_monthly_sales AS
SELECT
    SUBSTR(o.ordered_at, 1, 7) AS month,               -- YYYY-MM
    COUNT(DISTINCT o.id) AS order_count,                -- 주문 건수
    COUNT(DISTINCT o.customer_id) AS customer_count,    -- 구매 고객 수
    CAST(SUM(o.total_amount) AS INTEGER) AS revenue,    -- 총 매출
    CAST(AVG(o.total_amount) AS INTEGER) AS avg_order,  -- 평균 주문 금액
    SUM(o.discount_amount) AS total_discount            -- 총 할인
FROM orders o
WHERE o.status NOT IN ('cancelled')
GROUP BY SUBSTR(o.ordered_at, 1, 7)
ORDER BY month;

-- =============================================
-- VIEW: 고객 요약 (생애 가치)
-- 학습 포인트: LEFT JOIN, COALESCE, CASE, 서브쿼리, 집계
-- =============================================
CREATE VIEW v_customer_summary AS
SELECT
    c.id,
    c.name,
    c.email,
    c.grade,
    c.gender,
    CASE
        WHEN c.birth_date IS NULL THEN NULL
        ELSE CAST((julianday('2025-06-30') - julianday(c.birth_date)) / 365.25 AS INTEGER)
    END AS age,
    c.created_at AS joined_at,
    COALESCE(os.order_count, 0) AS total_orders,
    COALESCE(os.total_spent, 0) AS total_spent,
    COALESCE(os.first_order, '') AS first_order_at,
    COALESCE(os.last_order, '') AS last_order_at,
    COALESCE(rv.review_count, 0) AS review_count,
    COALESCE(rv.avg_rating, 0) AS avg_rating_given,
    COALESCE(ws.wishlist_count, 0) AS wishlist_count,
    c.is_active,
    c.last_login_at,
    CASE
        WHEN c.is_active = 0 THEN 'inactive'
        WHEN c.last_login_at IS NULL THEN 'never_logged_in'
        WHEN c.last_login_at < DATE('2025-06-30', '-365 days') THEN 'dormant'
        ELSE 'active'
    END AS activity_status
FROM customers c
LEFT JOIN (
    SELECT customer_id,
           COUNT(*) AS order_count,
           CAST(SUM(total_amount) AS INTEGER) AS total_spent,
           MIN(ordered_at) AS first_order,
           MAX(ordered_at) AS last_order
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY customer_id
) os ON c.id = os.customer_id
LEFT JOIN (
    SELECT customer_id,
           COUNT(*) AS review_count,
           ROUND(AVG(rating), 1) AS avg_rating
    FROM reviews
    GROUP BY customer_id
) rv ON c.id = rv.customer_id
LEFT JOIN (
    SELECT customer_id, COUNT(*) AS wishlist_count
    FROM wishlists
    GROUP BY customer_id
) ws ON c.id = ws.customer_id;

-- =============================================
-- VIEW: 상품 실적 (매출, 리뷰, 재고)
-- 학습 포인트: 다중 LEFT JOIN, Window Function 대상 데이터
-- =============================================
CREATE VIEW v_product_performance AS
SELECT
    p.id,
    p.name,
    p.brand,
    p.sku,
    c.name AS category,
    p.price,
    p.cost_price,
    ROUND((p.price - p.cost_price) / p.price * 100, 1) AS margin_pct,
    p.stock_qty,
    p.is_active,
    COALESCE(s.total_sold, 0) AS total_sold,
    COALESCE(s.total_revenue, 0) AS total_revenue,
    COALESCE(s.order_count, 0) AS order_count,
    COALESCE(rv.review_count, 0) AS review_count,
    COALESCE(rv.avg_rating, 0) AS avg_rating,
    COALESCE(ws.wishlist_count, 0) AS wishlist_count,
    COALESCE(rt.return_count, 0) AS return_count
FROM products p
JOIN categories c ON p.category_id = c.id
LEFT JOIN (
    SELECT oi.product_id,
           SUM(oi.quantity) AS total_sold,
           CAST(SUM(oi.subtotal) AS INTEGER) AS total_revenue,
           COUNT(DISTINCT oi.order_id) AS order_count
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY oi.product_id
) s ON p.id = s.product_id
LEFT JOIN (
    SELECT product_id,
           COUNT(*) AS review_count,
           ROUND(AVG(rating), 1) AS avg_rating
    FROM reviews
    GROUP BY product_id
) rv ON p.id = rv.product_id
LEFT JOIN (
    SELECT product_id, COUNT(*) AS wishlist_count
    FROM wishlists
    GROUP BY product_id
) ws ON p.id = ws.product_id
LEFT JOIN (
    SELECT oi.product_id, COUNT(DISTINCT r.id) AS return_count
    FROM returns r
    JOIN order_items oi ON r.order_id = oi.order_id
    GROUP BY oi.product_id
) rt ON p.id = rt.product_id;

-- =============================================
-- VIEW: 카테고리 계층 (재귀 CTE 예시)
-- 학습 포인트: Recursive CTE, 문자열 연결, 계층 탐색
-- =============================================
CREATE VIEW v_category_tree AS
WITH RECURSIVE tree AS (
    SELECT id, name, parent_id, depth,
           name AS full_path,
           CAST(printf('%04d', sort_order) AS TEXT) AS sort_key
    FROM categories
    WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, c.depth,
           tree.full_path || ' > ' || c.name,
           tree.sort_key || '.' || printf('%04d', c.sort_order)
    FROM categories c
    JOIN tree ON c.parent_id = tree.id
)
SELECT t.id, t.name, t.parent_id, t.depth, t.full_path,
       COALESCE(p.product_count, 0) AS product_count
FROM tree t
LEFT JOIN (
    SELECT category_id, COUNT(*) AS product_count
    FROM products
    GROUP BY category_id
) p ON t.id = p.category_id
ORDER BY t.sort_key;

-- =============================================
-- VIEW: 일별 주문 통계
-- 학습 포인트: 날짜 처리, 다중 집계, CASE
-- =============================================
CREATE VIEW v_daily_orders AS
SELECT
    DATE(ordered_at) AS order_date,
    CASE CAST(strftime('%w', ordered_at) AS INTEGER)
        WHEN 0 THEN '일' WHEN 1 THEN '월' WHEN 2 THEN '화'
        WHEN 3 THEN '수' WHEN 4 THEN '목' WHEN 5 THEN '금' WHEN 6 THEN '토'
    END AS day_of_week,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returned,
    CAST(SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS INTEGER) AS revenue,
    CAST(AVG(CASE WHEN status != 'cancelled' THEN total_amount END) AS INTEGER) AS avg_order_amount
FROM orders
GROUP BY DATE(ordered_at)
ORDER BY order_date;

-- =============================================
-- VIEW: 결제 수단별 통계
-- 학습 포인트: CASE 피벗, 비율 계산, 문자열 함수
-- =============================================
CREATE VIEW v_payment_summary AS
SELECT
    method,
    COUNT(*) AS payment_count,
    CAST(SUM(amount) AS INTEGER) AS total_amount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM payments), 1) AS pct,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) AS refunded,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed
FROM payments
GROUP BY method
ORDER BY payment_count DESC;

-- =============================================
-- VIEW: 주문 상세 (비정규화 조회용)
-- 학습 포인트: 다중 JOIN (5개 테이블), NULL 처리
-- =============================================
CREATE VIEW v_order_detail AS
SELECT
    o.id AS order_id,
    o.order_number,
    o.ordered_at,
    o.status AS order_status,
    o.total_amount,
    o.discount_amount,
    o.shipping_fee,
    o.notes,
    c.id AS customer_id,
    c.name AS customer_name,
    c.email AS customer_email,
    c.grade AS customer_grade,
    p.method AS payment_method,
    p.status AS payment_status,
    p.card_issuer,
    p.installment_months,
    s.carrier,
    s.tracking_number,
    s.status AS shipping_status,
    s.delivered_at,
    ca.address1 || ' ' || COALESCE(ca.address2, '') AS delivery_address
FROM orders o
JOIN customers c ON o.customer_id = c.id
LEFT JOIN payments p ON o.id = p.order_id
LEFT JOIN shipping s ON o.id = s.order_id
LEFT JOIN customer_addresses ca ON o.address_id = ca.id;

-- =============================================
-- VIEW: 매출 성장률 (전월 대비)
-- 학습 포인트: LAG 윈도우 함수, ROUND, 비율 계산
-- =============================================
CREATE VIEW v_revenue_growth AS
SELECT
    month,
    revenue,
    prev_revenue,
    CASE
        WHEN prev_revenue > 0
        THEN ROUND((revenue - prev_revenue) * 100.0 / prev_revenue, 1)
        ELSE NULL
    END AS growth_pct
FROM (
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        CAST(SUM(total_amount) AS INTEGER) AS revenue,
        LAG(CAST(SUM(total_amount) AS INTEGER)) OVER (ORDER BY SUBSTR(ordered_at, 1, 7)) AS prev_revenue
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7)
)
ORDER BY month;

-- =============================================
-- VIEW: 카테고리별 상품 매출 순위
-- 학습 포인트: ROW_NUMBER, PARTITION BY, 다중 JOIN
-- =============================================
CREATE VIEW v_top_products_by_category AS
SELECT
    category_name,
    product_name,
    brand,
    total_revenue,
    total_sold,
    rank_in_category
FROM (
    SELECT
        cat.name AS category_name,
        p.name AS product_name,
        p.brand,
        COALESCE(SUM(oi.subtotal), 0) AS total_revenue,
        COALESCE(SUM(oi.quantity), 0) AS total_sold,
        ROW_NUMBER() OVER (
            PARTITION BY p.category_id
            ORDER BY COALESCE(SUM(oi.subtotal), 0) DESC
        ) AS rank_in_category
    FROM products p
    JOIN categories cat ON p.category_id = cat.id
    LEFT JOIN order_items oi ON p.id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.id AND o.status NOT IN ('cancelled')
    GROUP BY p.id
)
WHERE rank_in_category <= 5;

-- =============================================
-- VIEW: 고객 RFM 분석 (마케팅 세분화)
-- 학습 포인트: NTILE 윈도우 함수, CASE, 날짜 계산, CTE
-- Recency(최근성) x Frequency(빈도) x Monetary(금액)
-- =============================================
CREATE VIEW v_customer_rfm AS
WITH rfm_raw AS (
    SELECT
        c.id AS customer_id,
        c.name,
        c.grade,
        CAST(julianday('2025-06-30') - julianday(MAX(o.ordered_at)) AS INTEGER) AS recency_days,
        COUNT(o.id) AS frequency,
        CAST(SUM(o.total_amount) AS INTEGER) AS monetary
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id
),
rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,   -- 최근일수록 높은 점수
        NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
    FROM rfm_raw
)
SELECT
    customer_id, name, grade,
    recency_days, frequency, monetary,
    r_score, f_score, m_score,
    r_score + f_score + m_score AS rfm_total,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
        ELSE 'Others'
    END AS segment
FROM rfm_scored;

-- =============================================
-- VIEW: 장바구니 이탈 분석
-- 학습 포인트: LEFT JOIN + IS NULL, 집계, 잠재 매출 계산
-- =============================================
CREATE VIEW v_cart_abandonment AS
SELECT
    c.id AS cart_id,
    cust.name AS customer_name,
    cust.email,
    c.status,
    c.created_at,
    COUNT(ci.id) AS item_count,
    CAST(SUM(p.price * ci.quantity) AS INTEGER) AS potential_revenue,
    GROUP_CONCAT(p.name, ', ') AS products
FROM carts c
JOIN customers cust ON c.customer_id = cust.id
JOIN cart_items ci ON c.id = ci.cart_id
JOIN products p ON ci.product_id = p.id
WHERE c.status = 'abandoned'
GROUP BY c.id;

-- =============================================
-- VIEW: 공급업체 실적
-- 학습 포인트: 다중 집계, HAVING, 비율 계산
-- =============================================
CREATE VIEW v_supplier_performance AS
SELECT
    s.id AS supplier_id,
    s.company_name,
    COUNT(DISTINCT p.id) AS product_count,
    SUM(CASE WHEN p.is_active = 1 THEN 1 ELSE 0 END) AS active_products,
    COALESCE(sales.total_revenue, 0) AS total_revenue,
    COALESCE(sales.total_sold, 0) AS total_sold,
    COALESCE(ret.return_count, 0) AS return_count,
    CASE
        WHEN COALESCE(sales.total_sold, 0) > 0
        THEN ROUND(COALESCE(ret.return_count, 0) * 100.0 / sales.total_sold, 2)
        ELSE 0
    END AS return_rate_pct
FROM suppliers s
LEFT JOIN products p ON s.id = p.supplier_id
LEFT JOIN (
    SELECT p2.supplier_id,
           CAST(SUM(oi.subtotal) AS INTEGER) AS total_revenue,
           SUM(oi.quantity) AS total_sold
    FROM order_items oi
    JOIN products p2 ON oi.product_id = p2.id
    JOIN orders o ON oi.order_id = o.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY p2.supplier_id
) sales ON s.id = sales.supplier_id
LEFT JOIN (
    SELECT p3.supplier_id, COUNT(*) AS return_count
    FROM returns r
    JOIN order_items oi ON r.order_id = oi.order_id
    JOIN products p3 ON oi.product_id = p3.id
    GROUP BY p3.supplier_id
) ret ON s.id = ret.supplier_id
GROUP BY s.id;

-- =============================================
-- VIEW: 시간대별 주문 패턴
-- 학습 포인트: CAST, 문자열 추출, 피벗 형태 집계
-- =============================================
CREATE VIEW v_hourly_pattern AS
SELECT
    CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
    COUNT(*) AS order_count,
    CAST(AVG(total_amount) AS INTEGER) AS avg_amount,
    CASE
        WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 0 AND 5 THEN 'dawn'
        WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 6 AND 11 THEN 'morning'
        WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 12 AND 17 THEN 'afternoon'
        ELSE 'evening'
    END AS time_slot
FROM orders
WHERE status NOT IN ('cancelled')
GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
ORDER BY hour;

-- =============================================
-- VIEW: 상품 ABC 분석 (파레토/80-20 법칙)
-- 학습 포인트: 누적합(SUM OVER), 비율 계산, CASE 분류
-- =============================================
CREATE VIEW v_product_abc AS
SELECT
    product_id, product_name, brand, total_revenue,
    revenue_pct,
    cumulative_pct,
    CASE
        WHEN cumulative_pct <= 80 THEN 'A'
        WHEN cumulative_pct <= 95 THEN 'B'
        ELSE 'C'
    END AS abc_class
FROM (
    SELECT
        product_id, product_name, brand, total_revenue,
        ROUND(total_revenue * 100.0 / SUM(total_revenue) OVER (), 2) AS revenue_pct,
        ROUND(SUM(total_revenue) OVER (ORDER BY total_revenue DESC) * 100.0
              / SUM(total_revenue) OVER (), 2) AS cumulative_pct
    FROM (
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            p.brand,
            CAST(COALESCE(SUM(oi.subtotal), 0) AS INTEGER) AS total_revenue
        FROM products p
        LEFT JOIN order_items oi ON p.id = oi.product_id
        LEFT JOIN orders o ON oi.order_id = o.id AND o.status NOT IN ('cancelled')
        GROUP BY p.id
    )
)
ORDER BY total_revenue DESC;

-- =============================================
-- VIEW: CS 직원 업무 현황
-- 학습 포인트: 다중 LEFT JOIN, 평균 처리 시간 계산
-- =============================================
CREATE VIEW v_staff_workload AS
SELECT
    s.id AS staff_id,
    s.name,
    s.department,
    COALESCE(comp.complaint_count, 0) AS complaint_count,
    COALESCE(comp.resolved_count, 0) AS resolved_count,
    COALESCE(comp.avg_resolve_hours, 0) AS avg_resolve_hours,
    COALESCE(ord.cs_order_count, 0) AS cs_order_count
FROM staff s
LEFT JOIN (
    SELECT
        staff_id,
        COUNT(*) AS complaint_count,
        SUM(CASE WHEN status IN ('resolved','closed') THEN 1 ELSE 0 END) AS resolved_count,
        CAST(AVG(
            CASE WHEN resolved_at IS NOT NULL
            THEN (julianday(resolved_at) - julianday(created_at)) * 24
            END
        ) AS INTEGER) AS avg_resolve_hours
    FROM complaints
    GROUP BY staff_id
) comp ON s.id = comp.staff_id
LEFT JOIN (
    SELECT staff_id, COUNT(*) AS cs_order_count
    FROM orders WHERE staff_id IS NOT NULL
    GROUP BY staff_id
) ord ON s.id = ord.staff_id
WHERE s.department = 'CS' OR comp.complaint_count > 0;

-- =============================================
-- VIEW: 쿠폰 효과 분석
-- 학습 포인트: JOIN + 집계, ROI 계산, 비율
-- =============================================
CREATE VIEW v_coupon_effectiveness AS
SELECT
    cp.id AS coupon_id,
    cp.code,
    cp.name,
    cp.type,
    cp.discount_value,
    cp.is_active,
    COALESCE(u.usage_count, 0) AS usage_count,
    cp.usage_limit,
    COALESCE(u.total_discount, 0) AS total_discount_given,
    COALESCE(u.total_order_revenue, 0) AS total_order_revenue,
    CASE
        WHEN COALESCE(u.total_discount, 0) > 0
        THEN ROUND(u.total_order_revenue / u.total_discount, 1)
        ELSE 0
    END AS roi_ratio
FROM coupons cp
LEFT JOIN (
    SELECT
        cu.coupon_id,
        COUNT(*) AS usage_count,
        CAST(SUM(cu.discount_amount) AS INTEGER) AS total_discount,
        CAST(SUM(o.total_amount) AS INTEGER) AS total_order_revenue
    FROM coupon_usage cu
    JOIN orders o ON cu.order_id = o.id
    GROUP BY cu.coupon_id
) u ON cp.id = u.coupon_id
ORDER BY COALESCE(u.usage_count, 0) DESC;

-- =============================================
-- VIEW: 반품 사유 분석
-- 학습 포인트: GROUP BY + CASE 피벗, 비율 계산
-- =============================================
CREATE VIEW v_return_analysis AS
SELECT
    reason,
    COUNT(*) AS total_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM returns), 1) AS pct,
    SUM(CASE WHEN return_type = 'refund' THEN 1 ELSE 0 END) AS refund_count,
    SUM(CASE WHEN return_type = 'exchange' THEN 1 ELSE 0 END) AS exchange_count,
    CAST(AVG(refund_amount) AS INTEGER) AS avg_refund_amount,
    SUM(CASE WHEN inspection_result = 'defective' THEN 1 ELSE 0 END) AS defective_count,
    SUM(CASE WHEN inspection_result = 'good' THEN 1 ELSE 0 END) AS good_count,
    CAST(AVG(
        CASE WHEN completed_at IS NOT NULL
        THEN julianday(completed_at) - julianday(requested_at)
        END
    ) AS INTEGER) AS avg_process_days
FROM returns
GROUP BY reason
ORDER BY total_count DESC;

-- =============================================
-- VIEW: 연도별 핵심 KPI 대시보드
-- 학습 포인트: 다중 서브쿼리, 종합 집계, 비즈니스 메트릭
-- =============================================
CREATE VIEW v_yearly_kpi AS
SELECT
    o_stats.yr AS year,
    o_stats.total_revenue,
    o_stats.order_count,
    o_stats.customer_count,
    CAST(o_stats.total_revenue * 1.0 / o_stats.order_count AS INTEGER) AS avg_order_value,
    CAST(o_stats.total_revenue * 1.0 / o_stats.customer_count AS INTEGER) AS revenue_per_customer,
    COALESCE(c.new_customers, 0) AS new_customers,
    o_stats.cancel_count,
    ROUND(o_stats.cancel_count * 100.0 / o_stats.order_count, 1) AS cancel_rate_pct,
    o_stats.return_count,
    ROUND(o_stats.return_count * 100.0 / o_stats.order_count, 1) AS return_rate_pct,
    COALESCE(r.review_count, 0) AS review_count,
    COALESCE(comp.complaint_count, 0) AS complaint_count
FROM (
    SELECT
        SUBSTR(o.ordered_at, 1, 4) AS yr,
        CAST(SUM(CASE WHEN o.status NOT IN ('cancelled') THEN o.total_amount ELSE 0 END) AS INTEGER) AS total_revenue,
        COUNT(*) AS order_count,
        COUNT(DISTINCT o.customer_id) AS customer_count,
        SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) AS cancel_count,
        SUM(CASE WHEN o.status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS return_count
    FROM orders o
    GROUP BY SUBSTR(o.ordered_at, 1, 4)
) o_stats
LEFT JOIN (
    SELECT SUBSTR(created_at, 1, 4) AS yr, COUNT(*) AS new_customers
    FROM customers GROUP BY SUBSTR(created_at, 1, 4)
) c ON o_stats.yr = c.yr
LEFT JOIN (
    SELECT SUBSTR(created_at, 1, 4) AS yr, COUNT(*) AS review_count
    FROM reviews GROUP BY SUBSTR(created_at, 1, 4)
) r ON o_stats.yr = r.yr
LEFT JOIN (
    SELECT SUBSTR(created_at, 1, 4) AS yr, COUNT(*) AS complaint_count
    FROM complaints GROUP BY SUBSTR(created_at, 1, 4)
) comp ON o_stats.yr = comp.yr
ORDER BY o_stats.yr;
"""


TRIGGER_SQL = """
-- =============================================
-- TRIGGER: 주문 상태 변경 시 updated_at 자동 갱신
-- 학습 포인트: AFTER UPDATE 트리거, NEW/OLD 참조, datetime 함수
-- =============================================
CREATE TRIGGER trg_orders_updated_at
AFTER UPDATE OF status ON orders
BEGIN
    UPDATE orders SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- =============================================
-- TRIGGER: 리뷰 수정 시 updated_at 자동 갱신
-- =============================================
CREATE TRIGGER trg_reviews_updated_at
AFTER UPDATE OF rating, title, content ON reviews
BEGIN
    UPDATE reviews SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- =============================================
-- TRIGGER: 상품 가격 변경 시 자동 가격 이력 추가
-- 학습 포인트: BEFORE UPDATE, 이력 테이블 자동화
-- =============================================
CREATE TRIGGER trg_product_price_history
AFTER UPDATE OF price ON products
WHEN OLD.price != NEW.price
BEGIN
    -- 기존 이력 종료
    UPDATE product_prices
    SET ended_at = datetime('now')
    WHERE product_id = NEW.id AND ended_at IS NULL;

    -- 새 이력 추가
    INSERT INTO product_prices (product_id, price, started_at, ended_at, change_reason)
    VALUES (NEW.id, NEW.price, datetime('now'), NULL, 'price_update');
END;

-- =============================================
-- TRIGGER: 상품 정보 변경 시 updated_at 갱신
-- =============================================
CREATE TRIGGER trg_products_updated_at
AFTER UPDATE ON products
BEGIN
    UPDATE products SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- =============================================
-- TRIGGER: 고객 정보 변경 시 updated_at 갱신
-- =============================================
CREATE TRIGGER trg_customers_updated_at
AFTER UPDATE ON customers
BEGIN
    UPDATE customers SET updated_at = datetime('now') WHERE id = NEW.id;
END;
"""


class SQLiteExporter:

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.db_path = os.path.join(output_dir, "tutorial.db")

    def export(self, data: dict[str, list[dict]]) -> str:
        """모든 데이터를 SQLite DB로 내보낸다."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=OFF")
        conn.execute("PRAGMA foreign_keys=ON")

        # 스키마 생성
        conn.executescript(SCHEMA_SQL)

        # 데이터 삽입 (테이블 순서대로)
        table_order = [
            "categories", "suppliers", "products", "product_images", "product_prices",
            "customers", "customer_addresses", "staff",
            "orders", "order_items", "payments", "shipping",
            "reviews", "inventory_transactions",
            "carts", "cart_items", "coupons", "coupon_usage",
            "wishlists", "returns", "complaints",
        ]

        for table in table_order:
            rows = data.get(table, [])
            if not rows:
                continue
            self._insert_rows(conn, table, rows)

        # 인덱스 생성
        conn.executescript(INDEX_SQL)

        # 뷰 생성
        conn.executescript(VIEW_SQL)

        # 트리거 생성
        conn.executescript(TRIGGER_SQL)

        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("VACUUM")
        conn.close()

        return self.db_path

    def _insert_rows(self, conn: sqlite3.Connection, table: str, rows: list[dict]):
        """배치 INSERT를 수행한다."""
        if not rows:
            return

        columns = list(rows[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        col_names = ", ".join(columns)
        sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"

        batch_size = 5000
        cursor = conn.cursor()
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            values = [tuple(row[c] for c in columns) for row in batch]
            cursor.executemany(sql, values)
        conn.commit()
