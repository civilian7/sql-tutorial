"""Oracle database exporter

Generates DDL, INSERT data, and stored procedures for Oracle 19c+.
Uses IDENTITY columns (12c+), VARCHAR2, NUMBER, CLOB, TIMESTAMP,
and CHECK constraints instead of ENUM.
"""

from __future__ import annotations

import os
from typing import Any


SCHEMA_SQL = """\
-- =============================================
-- E-commerce Test Database - Oracle 19c+
-- =============================================
-- Run as a DBA user (e.g. SYSTEM) or create a dedicated schema:
--   CREATE USER ecommerce IDENTIFIED BY ecommerce
--       DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;
--   GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE SEQUENCE,
--         CREATE PROCEDURE, CREATE TRIGGER TO ecommerce;
--   ALTER SESSION SET CURRENT_SCHEMA = ecommerce;

ALTER SESSION SET NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS';
ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD';

-- =============================================
-- Product categories (hierarchical: top > mid > sub)
-- =============================================
CREATE TABLE categories (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    parent_id       NUMBER NULL,
    name            VARCHAR2(100) NOT NULL,
    slug            VARCHAR2(100) NOT NULL UNIQUE,
    depth           NUMBER DEFAULT 0 NOT NULL,
    sort_order      NUMBER DEFAULT 0 NOT NULL,
    is_active       NUMBER(1) DEFAULT 1 NOT NULL CHECK (is_active IN (0, 1)),
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL,
    CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories(id)
);

-- =============================================
-- Suppliers
-- =============================================
CREATE TABLE suppliers (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_name    VARCHAR2(200) NOT NULL,
    business_number VARCHAR2(20) NOT NULL,
    contact_name    VARCHAR2(100) NOT NULL,
    phone           VARCHAR2(20) NOT NULL,
    email           VARCHAR2(200) NOT NULL,
    address         VARCHAR2(500) NULL,
    is_active       NUMBER(1) DEFAULT 1 NOT NULL CHECK (is_active IN (0, 1)),
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Products
-- =============================================
CREATE TABLE products (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id     NUMBER NOT NULL,
    supplier_id     NUMBER NOT NULL,
    successor_id    NUMBER NULL,
    name            VARCHAR2(500) NOT NULL,
    sku             VARCHAR2(50) NOT NULL UNIQUE,
    brand           VARCHAR2(100) NOT NULL,
    model_number    VARCHAR2(50) NULL,
    description     CLOB NULL,
    specs           CLOB NULL CONSTRAINT chk_products_specs CHECK (specs IS JSON),
    price           NUMBER(12,2) NOT NULL CHECK (price >= 0),
    cost_price      NUMBER(12,2) NOT NULL CHECK (cost_price >= 0),
    stock_qty       NUMBER DEFAULT 0 NOT NULL,
    weight_grams    NUMBER NULL,
    is_active       NUMBER(1) DEFAULT 1 NOT NULL CHECK (is_active IN (0, 1)),
    discontinued_at TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL,
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id),
    CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    CONSTRAINT fk_products_successor FOREIGN KEY (successor_id) REFERENCES products(id)
);

-- =============================================
-- Product images (1-5 per product)
-- =============================================
CREATE TABLE product_images (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      NUMBER NOT NULL,
    image_url       VARCHAR2(500) NOT NULL,
    file_name       VARCHAR2(200) NOT NULL,
    image_type      VARCHAR2(20) NOT NULL CHECK (image_type IN ('main','angle','side','back','detail','package','lifestyle','accessory','size_comparison')),
    alt_text        VARCHAR2(500) NULL,
    width           NUMBER NULL,
    height          NUMBER NULL,
    file_size       NUMBER NULL,
    sort_order      NUMBER DEFAULT 1 NOT NULL,
    is_primary      NUMBER(1) DEFAULT 0 NOT NULL CHECK (is_primary IN (0, 1)),
    created_at      TIMESTAMP NOT NULL,
    CONSTRAINT fk_product_images_product FOREIGN KEY (product_id) REFERENCES products(id)
);

-- =============================================
-- Product price history
-- =============================================
CREATE TABLE product_prices (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      NUMBER NOT NULL,
    price           NUMBER(12,2) NOT NULL,
    started_at      TIMESTAMP NOT NULL,
    ended_at        TIMESTAMP NULL,
    change_reason   VARCHAR2(20) NULL CHECK (change_reason IN ('regular','promotion','price_drop','cost_increase')),
    CONSTRAINT fk_product_prices_product FOREIGN KEY (product_id) REFERENCES products(id)
);

-- =============================================
-- Customers
-- =============================================
CREATE TABLE customers (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email           VARCHAR2(200) NOT NULL UNIQUE,
    password_hash   VARCHAR2(64) NOT NULL,
    name            VARCHAR2(100) NOT NULL,
    phone           VARCHAR2(20) NOT NULL,
    birth_date      DATE NULL,
    gender          VARCHAR2(1) NULL CHECK (gender IN ('M','F')),
    grade           VARCHAR2(10) DEFAULT 'BRONZE' NOT NULL CHECK (grade IN ('BRONZE','SILVER','GOLD','VIP')),
    point_balance   NUMBER DEFAULT 0 NOT NULL CHECK (point_balance >= 0),
    acquisition_channel VARCHAR2(20) NULL CHECK (acquisition_channel IN ('organic','search_ad','social','referral','direct')),
    is_active       NUMBER(1) DEFAULT 1 NOT NULL CHECK (is_active IN (0, 1)),
    last_login_at   TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Customer addresses (1-3 per customer)
-- =============================================
CREATE TABLE customer_addresses (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     NUMBER NOT NULL,
    label           VARCHAR2(50) NOT NULL,
    recipient_name  VARCHAR2(100) NOT NULL,
    phone           VARCHAR2(20) NOT NULL,
    zip_code        VARCHAR2(10) NOT NULL,
    address1        VARCHAR2(300) NOT NULL,
    address2        VARCHAR2(300) NULL,
    is_default      NUMBER(1) DEFAULT 0 NOT NULL CHECK (is_default IN (0, 1)),
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NULL,
    CONSTRAINT fk_customer_addresses_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- =============================================
-- Staff
-- =============================================
CREATE TABLE staff (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    manager_id      NUMBER NULL,
    email           VARCHAR2(200) NOT NULL UNIQUE,
    name            VARCHAR2(100) NOT NULL,
    phone           VARCHAR2(20) NOT NULL,
    department      VARCHAR2(50) NOT NULL,
    role            VARCHAR2(10) NOT NULL CHECK (role IN ('admin','manager','staff')),
    is_active       NUMBER(1) DEFAULT 1 NOT NULL CHECK (is_active IN (0, 1)),
    hired_at        TIMESTAMP NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    CONSTRAINT fk_staff_manager FOREIGN KEY (manager_id) REFERENCES staff(id)
);

-- =============================================
-- Orders (partitioned by year on ordered_at)
-- =============================================
CREATE TABLE orders (
    id              NUMBER GENERATED ALWAYS AS IDENTITY,
    order_number    VARCHAR2(30) NOT NULL,
    customer_id     NUMBER NOT NULL,
    address_id      NUMBER NOT NULL,
    staff_id        NUMBER NULL,
    status          VARCHAR2(20) NOT NULL CHECK (status IN ('pending','paid','preparing','shipped','delivered','confirmed','cancelled','return_requested','returned')),
    total_amount    NUMBER(12,2) NOT NULL,
    discount_amount NUMBER(12,2) DEFAULT 0 NOT NULL,
    shipping_fee    NUMBER(12,2) DEFAULT 0 NOT NULL,
    point_used      NUMBER DEFAULT 0 NOT NULL,
    point_earned    NUMBER DEFAULT 0 NOT NULL,
    notes           CLOB NULL,
    ordered_at      TIMESTAMP NOT NULL,
    completed_at    TIMESTAMP NULL,
    cancelled_at    TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL,
    CONSTRAINT pk_orders PRIMARY KEY (id, ordered_at),
    CONSTRAINT uq_order_number UNIQUE (order_number, ordered_at)
)
PARTITION BY RANGE (ordered_at) (
    PARTITION p2015 VALUES LESS THAN (TIMESTAMP '2016-01-01 00:00:00'),
    PARTITION p2016 VALUES LESS THAN (TIMESTAMP '2017-01-01 00:00:00'),
    PARTITION p2017 VALUES LESS THAN (TIMESTAMP '2018-01-01 00:00:00'),
    PARTITION p2018 VALUES LESS THAN (TIMESTAMP '2019-01-01 00:00:00'),
    PARTITION p2019 VALUES LESS THAN (TIMESTAMP '2020-01-01 00:00:00'),
    PARTITION p2020 VALUES LESS THAN (TIMESTAMP '2021-01-01 00:00:00'),
    PARTITION p2021 VALUES LESS THAN (TIMESTAMP '2022-01-01 00:00:00'),
    PARTITION p2022 VALUES LESS THAN (TIMESTAMP '2023-01-01 00:00:00'),
    PARTITION p2023 VALUES LESS THAN (TIMESTAMP '2024-01-01 00:00:00'),
    PARTITION p2024 VALUES LESS THAN (TIMESTAMP '2025-01-01 00:00:00'),
    PARTITION p2025 VALUES LESS THAN (TIMESTAMP '2026-01-01 00:00:00'),
    PARTITION pmax VALUES LESS THAN (MAXVALUE)
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_ordered_at ON orders(ordered_at);

-- =============================================
-- Order items (1-5 items per order)
-- =============================================
CREATE TABLE order_items (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        NUMBER NOT NULL,
    product_id      NUMBER NOT NULL,
    quantity        NUMBER NOT NULL CHECK (quantity > 0),
    unit_price      NUMBER(12,2) NOT NULL CHECK (unit_price >= 0),
    discount_amount NUMBER(12,2) DEFAULT 0 NOT NULL,
    subtotal        NUMBER(12,2) NOT NULL,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- =============================================
-- Payments
-- =============================================
CREATE TABLE payments (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        NUMBER NOT NULL,
    method          VARCHAR2(20) NOT NULL CHECK (method IN ('card','bank_transfer','virtual_account','kakao_pay','naver_pay','point')),
    amount          NUMBER(12,2) NOT NULL CHECK (amount >= 0),
    status          VARCHAR2(10) NOT NULL CHECK (status IN ('pending','completed','failed','refunded')),
    pg_transaction_id VARCHAR2(100) NULL,
    card_issuer     VARCHAR2(50) NULL,
    card_approval_no VARCHAR2(20) NULL,
    installment_months NUMBER NULL,
    bank_name       VARCHAR2(50) NULL,
    account_no      VARCHAR2(50) NULL,
    depositor_name  VARCHAR2(100) NULL,
    easy_pay_method VARCHAR2(50) NULL,
    receipt_type    VARCHAR2(20) NULL,
    receipt_no      VARCHAR2(50) NULL,
    paid_at         TIMESTAMP NULL,
    refunded_at     TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL
);

CREATE INDEX idx_payments_order ON payments(order_id);

-- =============================================
-- Shipping
-- =============================================
CREATE TABLE shipping (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        NUMBER NOT NULL,
    carrier         VARCHAR2(50) NOT NULL,
    tracking_number VARCHAR2(50) NULL,
    status          VARCHAR2(15) NOT NULL CHECK (status IN ('preparing','shipped','in_transit','delivered','returned')),
    shipped_at      TIMESTAMP NULL,
    delivered_at    TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

CREATE INDEX idx_shipping_order ON shipping(order_id);

-- =============================================
-- Reviews
-- =============================================
CREATE TABLE reviews (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      NUMBER NOT NULL,
    customer_id     NUMBER NOT NULL,
    order_id        NUMBER NOT NULL,
    rating          NUMBER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title           VARCHAR2(200) NULL,
    content         CLOB NULL,
    is_verified     NUMBER(1) DEFAULT 1 NOT NULL CHECK (is_verified IN (0, 1)),
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL,
    CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_reviews_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_customer ON reviews(customer_id);

-- =============================================
-- Inventory transactions
-- =============================================
CREATE TABLE inventory_transactions (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      NUMBER NOT NULL,
    type            VARCHAR2(15) NOT NULL CHECK (type IN ('inbound','outbound','return','adjustment')),
    quantity        NUMBER NOT NULL,
    reference_id    NUMBER NULL,
    notes           VARCHAR2(500) NULL,
    created_at      TIMESTAMP NOT NULL,
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products(id)
);

-- =============================================
-- Carts
-- =============================================
CREATE TABLE carts (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     NUMBER NOT NULL,
    status          VARCHAR2(15) DEFAULT 'active' NOT NULL CHECK (status IN ('active','converted','abandoned')),
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL,
    CONSTRAINT fk_carts_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- =============================================
-- Cart items
-- =============================================
CREATE TABLE cart_items (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cart_id         NUMBER NOT NULL,
    product_id      NUMBER NOT NULL,
    quantity        NUMBER DEFAULT 1 NOT NULL,
    added_at        TIMESTAMP NOT NULL,
    CONSTRAINT fk_cart_items_cart FOREIGN KEY (cart_id) REFERENCES carts(id),
    CONSTRAINT fk_cart_items_product FOREIGN KEY (product_id) REFERENCES products(id)
);

-- =============================================
-- Coupons
-- =============================================
CREATE TABLE coupons (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            VARCHAR2(30) NOT NULL UNIQUE,
    name            VARCHAR2(200) NOT NULL,
    type            VARCHAR2(10) NOT NULL CHECK (type IN ('percent','fixed')),
    discount_value  NUMBER(12,2) NOT NULL CHECK (discount_value > 0),
    min_order_amount NUMBER(12,2) NULL,
    max_discount    NUMBER(12,2) NULL,
    usage_limit     NUMBER NULL,
    per_user_limit  NUMBER DEFAULT 1 NOT NULL,
    is_active       NUMBER(1) DEFAULT 1 NOT NULL CHECK (is_active IN (0, 1)),
    started_at      TIMESTAMP NOT NULL,
    expired_at      TIMESTAMP NOT NULL,
    created_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Coupon usage
-- =============================================
CREATE TABLE coupon_usage (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    coupon_id       NUMBER NOT NULL,
    customer_id     NUMBER NOT NULL,
    order_id        NUMBER NOT NULL,
    discount_amount NUMBER(12,2) NOT NULL,
    used_at         TIMESTAMP NOT NULL,
    CONSTRAINT fk_coupon_usage_coupon FOREIGN KEY (coupon_id) REFERENCES coupons(id),
    CONSTRAINT fk_coupon_usage_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- =============================================
-- Customer complaints
-- =============================================
CREATE TABLE complaints (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        NUMBER NULL,
    customer_id     NUMBER NOT NULL,
    staff_id        NUMBER NULL,
    category        VARCHAR2(20) NOT NULL CHECK (category IN ('product_defect','delivery_issue','wrong_item','refund_request','exchange_request','general_inquiry','price_inquiry')),
    channel         VARCHAR2(10) NOT NULL CHECK (channel IN ('website','phone','email','chat','kakao')),
    priority        VARCHAR2(10) NOT NULL CHECK (priority IN ('low','medium','high','urgent')),
    status          VARCHAR2(10) NOT NULL CHECK (status IN ('open','resolved','closed')),
    title           VARCHAR2(300) NOT NULL,
    content         CLOB NOT NULL,
    resolution      CLOB NULL,
    type            VARCHAR2(10) DEFAULT 'inquiry' NOT NULL CHECK (type IN ('inquiry','claim','report')),
    sub_category    VARCHAR2(100) NULL,
    compensation_type VARCHAR2(20) NULL CHECK (compensation_type IN ('refund','exchange','partial_refund','point_compensation','none')),
    compensation_amount NUMBER(12,2) DEFAULT 0 NULL,
    escalated       NUMBER(1) DEFAULT 0 NOT NULL CHECK (escalated IN (0, 1)),
    response_count  NUMBER DEFAULT 1 NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    resolved_at     TIMESTAMP NULL,
    closed_at       TIMESTAMP NULL,
    CONSTRAINT fk_complaints_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_complaints_staff FOREIGN KEY (staff_id) REFERENCES staff(id)
);

CREATE INDEX idx_complaints_customer ON complaints(customer_id);
CREATE INDEX idx_complaints_status ON complaints(status);

-- =============================================
-- Returns/exchanges
-- =============================================
CREATE TABLE returns (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        NUMBER NOT NULL,
    customer_id     NUMBER NOT NULL,
    return_type     VARCHAR2(10) NOT NULL CHECK (return_type IN ('refund','exchange')),
    reason          VARCHAR2(25) NOT NULL CHECK (reason IN ('defective','wrong_item','change_of_mind','damaged_in_transit','not_as_described','late_delivery')),
    reason_detail   CLOB NOT NULL,
    status          VARCHAR2(20) NOT NULL CHECK (status IN ('requested','pickup_scheduled','in_transit','completed')),
    is_partial      NUMBER(1) DEFAULT 0 NOT NULL CHECK (is_partial IN (0, 1)),
    refund_amount   NUMBER(12,2) NOT NULL,
    refund_status   VARCHAR2(20) NOT NULL CHECK (refund_status IN ('pending','refunded','exchanged','partial_refund')),
    carrier         VARCHAR2(50) NOT NULL,
    tracking_number VARCHAR2(50) NOT NULL,
    requested_at    TIMESTAMP NOT NULL,
    pickup_at       TIMESTAMP NOT NULL,
    received_at     TIMESTAMP NULL,
    inspected_at    TIMESTAMP NULL,
    inspection_result VARCHAR2(15) NULL CHECK (inspection_result IN ('good','opened_good','defective','unsellable')),
    completed_at    TIMESTAMP NULL,
    claim_id        NUMBER NULL,
    exchange_product_id NUMBER NULL,
    restocking_fee  NUMBER(12,2) DEFAULT 0 NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    CONSTRAINT fk_returns_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_returns_claim FOREIGN KEY (claim_id) REFERENCES complaints(id),
    CONSTRAINT fk_returns_exchange_product FOREIGN KEY (exchange_product_id) REFERENCES products(id)
);

CREATE INDEX idx_returns_order ON returns(order_id);
CREATE INDEX idx_returns_customer ON returns(customer_id);

-- =============================================
-- Wishlists (M:N: customers <-> products)
-- =============================================
CREATE TABLE wishlists (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     NUMBER NOT NULL,
    product_id      NUMBER NOT NULL,
    is_purchased    NUMBER(1) DEFAULT 0 NOT NULL CHECK (is_purchased IN (0, 1)),
    notify_on_sale  NUMBER(1) DEFAULT 0 NOT NULL CHECK (notify_on_sale IN (0, 1)),
    created_at      TIMESTAMP NOT NULL,
    CONSTRAINT uq_wishlist UNIQUE (customer_id, product_id),
    CONSTRAINT fk_wishlists_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_wishlists_product FOREIGN KEY (product_id) REFERENCES products(id)
);

-- =============================================
-- Calendar dimension (for CROSS JOIN exercises)
-- =============================================
CREATE TABLE calendar (
    date_key        DATE NOT NULL PRIMARY KEY,
    year            NUMBER NOT NULL,
    month           NUMBER NOT NULL,
    day             NUMBER NOT NULL,
    quarter         NUMBER NOT NULL,
    day_of_week     NUMBER NOT NULL,
    day_name        VARCHAR2(20) NOT NULL,
    is_weekend      NUMBER(1) DEFAULT 0 NOT NULL CHECK (is_weekend IN (0, 1)),
    is_holiday      NUMBER(1) DEFAULT 0 NOT NULL CHECK (is_holiday IN (0, 1)),
    holiday_name    VARCHAR2(100) NULL
);

CREATE INDEX idx_calendar_year_month ON calendar(year, month);

-- =============================================
-- Customer grade history (SCD Type 2)
-- =============================================
CREATE TABLE customer_grade_history (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     NUMBER NOT NULL,
    old_grade       VARCHAR2(10) NULL CHECK (old_grade IN ('BRONZE','SILVER','GOLD','VIP')),
    new_grade       VARCHAR2(10) NOT NULL CHECK (new_grade IN ('BRONZE','SILVER','GOLD','VIP')),
    changed_at      TIMESTAMP NOT NULL,
    reason          VARCHAR2(20) NOT NULL CHECK (reason IN ('signup','upgrade','downgrade','yearly_review')),
    CONSTRAINT fk_grade_history_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE INDEX idx_grade_history_customer ON customer_grade_history(customer_id);

-- =============================================
-- Tags (M:N learning)
-- =============================================
CREATE TABLE tags (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            VARCHAR2(100) NOT NULL UNIQUE,
    category        VARCHAR2(50) NOT NULL
);

CREATE TABLE product_tags (
    product_id      NUMBER NOT NULL,
    tag_id          NUMBER NOT NULL,
    CONSTRAINT pk_product_tags PRIMARY KEY (product_id, tag_id),
    CONSTRAINT fk_product_tags_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_product_tags_tag FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- =============================================
-- Product views (partitioned by year)
-- =============================================
CREATE TABLE product_views (
    id              NUMBER GENERATED ALWAYS AS IDENTITY,
    customer_id     NUMBER NOT NULL,
    product_id      NUMBER NOT NULL,
    referrer_source VARCHAR2(20) NOT NULL CHECK (referrer_source IN ('direct','search','ad','recommendation','social','email')),
    device_type     VARCHAR2(10) NOT NULL CHECK (device_type IN ('desktop','mobile','tablet')),
    duration_seconds NUMBER NOT NULL,
    viewed_at       TIMESTAMP NOT NULL,
    CONSTRAINT pk_product_views PRIMARY KEY (id, viewed_at)
)
PARTITION BY RANGE (viewed_at) (
    PARTITION p2015 VALUES LESS THAN (TIMESTAMP '2016-01-01 00:00:00'),
    PARTITION p2016 VALUES LESS THAN (TIMESTAMP '2017-01-01 00:00:00'),
    PARTITION p2017 VALUES LESS THAN (TIMESTAMP '2018-01-01 00:00:00'),
    PARTITION p2018 VALUES LESS THAN (TIMESTAMP '2019-01-01 00:00:00'),
    PARTITION p2019 VALUES LESS THAN (TIMESTAMP '2020-01-01 00:00:00'),
    PARTITION p2020 VALUES LESS THAN (TIMESTAMP '2021-01-01 00:00:00'),
    PARTITION p2021 VALUES LESS THAN (TIMESTAMP '2022-01-01 00:00:00'),
    PARTITION p2022 VALUES LESS THAN (TIMESTAMP '2023-01-01 00:00:00'),
    PARTITION p2023 VALUES LESS THAN (TIMESTAMP '2024-01-01 00:00:00'),
    PARTITION p2024 VALUES LESS THAN (TIMESTAMP '2025-01-01 00:00:00'),
    PARTITION p2025 VALUES LESS THAN (TIMESTAMP '2026-01-01 00:00:00'),
    PARTITION pmax VALUES LESS THAN (MAXVALUE)
);

CREATE INDEX idx_views_customer ON product_views(customer_id);
CREATE INDEX idx_views_product ON product_views(product_id);
CREATE INDEX idx_views_viewed_at ON product_views(viewed_at);

-- =============================================
-- Point transactions
-- =============================================
CREATE TABLE point_transactions (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     NUMBER NOT NULL,
    order_id        NUMBER NULL,
    type            VARCHAR2(10) NOT NULL CHECK (type IN ('earn','use','expire')),
    reason          VARCHAR2(10) NOT NULL CHECK (reason IN ('purchase','confirm','review','signup','use','expiry')),
    amount          NUMBER NOT NULL,
    balance_after   NUMBER NOT NULL,
    expires_at      TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL,
    CONSTRAINT fk_point_tx_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE INDEX idx_point_tx_customer ON point_transactions(customer_id);
CREATE INDEX idx_point_tx_type ON point_transactions(type);

-- =============================================
-- Promotions
-- =============================================
CREATE TABLE promotions (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            VARCHAR2(200) NOT NULL,
    type            VARCHAR2(10) NOT NULL CHECK (type IN ('seasonal','flash','category')),
    discount_type   VARCHAR2(10) NOT NULL CHECK (discount_type IN ('percent','fixed')),
    discount_value  NUMBER(12,2) NOT NULL,
    min_order_amount NUMBER(12,2) NULL,
    started_at      TIMESTAMP NOT NULL,
    ended_at        TIMESTAMP NOT NULL,
    is_active       NUMBER(1) DEFAULT 1 NOT NULL CHECK (is_active IN (0, 1)),
    created_at      TIMESTAMP NOT NULL
);

CREATE TABLE promotion_products (
    promotion_id    NUMBER NOT NULL,
    product_id      NUMBER NOT NULL,
    override_price  NUMBER(12,2) NULL,
    CONSTRAINT pk_promotion_products PRIMARY KEY (promotion_id, product_id),
    CONSTRAINT fk_promo_products_promo FOREIGN KEY (promotion_id) REFERENCES promotions(id),
    CONSTRAINT fk_promo_products_product FOREIGN KEY (product_id) REFERENCES products(id)
);

-- =============================================
-- Product Q&A (self-join)
-- =============================================
CREATE TABLE product_qna (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      NUMBER NOT NULL,
    customer_id     NUMBER NULL,
    staff_id        NUMBER NULL,
    parent_id       NUMBER NULL,
    content         CLOB NOT NULL,
    is_answered     NUMBER(1) DEFAULT 0 NOT NULL CHECK (is_answered IN (0, 1)),
    created_at      TIMESTAMP NOT NULL,
    CONSTRAINT fk_qna_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_qna_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_qna_staff FOREIGN KEY (staff_id) REFERENCES staff(id),
    CONSTRAINT fk_qna_parent FOREIGN KEY (parent_id) REFERENCES product_qna(id)
);

CREATE INDEX idx_qna_product ON product_qna(product_id);

-- =============================================
-- Views
-- =============================================

CREATE OR REPLACE VIEW v_monthly_sales AS
SELECT
    TO_CHAR(o.ordered_at, 'YYYY-MM') AS month,
    COUNT(DISTINCT o.id) AS order_count,
    COUNT(DISTINCT o.customer_id) AS customer_count,
    CAST(SUM(o.total_amount) AS NUMBER(18,0)) AS revenue,
    CAST(AVG(o.total_amount) AS NUMBER(18,0)) AS avg_order,
    SUM(o.discount_amount) AS total_discount
FROM orders o
WHERE o.status != 'cancelled'
GROUP BY TO_CHAR(o.ordered_at, 'YYYY-MM')
ORDER BY month;

CREATE OR REPLACE VIEW v_customer_summary AS
SELECT
    c.id,
    c.name,
    c.email,
    c.grade,
    c.gender,
    CASE
        WHEN c.birth_date IS NULL THEN NULL
        ELSE TRUNC(MONTHS_BETWEEN(DATE '2025-06-30', c.birth_date) / 12)
    END AS age,
    c.created_at AS joined_at,
    NVL(os.order_count, 0) AS total_orders,
    NVL(os.total_spent, 0) AS total_spent,
    NVL(TO_CHAR(os.first_order, 'YYYY-MM-DD HH24:MI:SS'), '') AS first_order_at,
    NVL(TO_CHAR(os.last_order, 'YYYY-MM-DD HH24:MI:SS'), '') AS last_order_at,
    NVL(rv.review_count, 0) AS review_count,
    NVL(rv.avg_rating, 0) AS avg_rating_given,
    NVL(ws.wishlist_count, 0) AS wishlist_count,
    c.is_active,
    c.last_login_at,
    CASE
        WHEN c.is_active = 0 THEN 'inactive'
        WHEN c.last_login_at IS NULL THEN 'never_logged_in'
        WHEN c.last_login_at < (DATE '2025-06-30' - 365) THEN 'dormant'
        ELSE 'active'
    END AS activity_status
FROM customers c
LEFT JOIN (
    SELECT customer_id,
           COUNT(*) AS order_count,
           CAST(SUM(total_amount) AS NUMBER(18,0)) AS total_spent,
           MIN(ordered_at) AS first_order,
           MAX(ordered_at) AS last_order
    FROM orders
    WHERE status != 'cancelled'
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

CREATE OR REPLACE VIEW v_product_performance AS
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
    NVL(s.total_sold, 0) AS total_sold,
    NVL(s.total_revenue, 0) AS total_revenue,
    NVL(s.order_count, 0) AS order_count,
    NVL(rv.review_count, 0) AS review_count,
    NVL(rv.avg_rating, 0) AS avg_rating,
    NVL(ws.wishlist_count, 0) AS wishlist_count,
    NVL(rt.return_count, 0) AS return_count
FROM products p
JOIN categories c ON p.category_id = c.id
LEFT JOIN (
    SELECT oi.product_id,
           SUM(oi.quantity) AS total_sold,
           CAST(SUM(oi.subtotal) AS NUMBER(18,0)) AS total_revenue,
           COUNT(DISTINCT oi.order_id) AS order_count
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE o.status != 'cancelled'
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

CREATE OR REPLACE VIEW v_category_tree AS
WITH tree (id, name, parent_id, depth, full_path, sort_key) AS (
    SELECT id, name, parent_id, depth,
           CAST(name AS VARCHAR2(4000)) AS full_path,
           LPAD(sort_order, 4, '0') AS sort_key
    FROM categories
    WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, c.depth,
           tree.full_path || ' > ' || c.name,
           tree.sort_key || '.' || LPAD(c.sort_order, 4, '0')
    FROM categories c
    JOIN tree ON c.parent_id = tree.id
)
SELECT t.id, t.name, t.parent_id, t.depth, t.full_path,
       NVL(p.product_count, 0) AS product_count
FROM tree t
LEFT JOIN (
    SELECT category_id, COUNT(*) AS product_count
    FROM products
    GROUP BY category_id
) p ON t.id = p.category_id
ORDER BY t.sort_key;

CREATE OR REPLACE VIEW v_daily_orders AS
SELECT
    TRUNC(ordered_at) AS order_date,
    TO_CHAR(ordered_at, 'DY') AS day_of_week,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returned,
    CAST(SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS NUMBER(18,0)) AS revenue,
    CAST(AVG(CASE WHEN status != 'cancelled' THEN total_amount END) AS NUMBER(18,0)) AS avg_order_amount
FROM orders
GROUP BY TRUNC(ordered_at), TO_CHAR(ordered_at, 'DY')
ORDER BY order_date;

CREATE OR REPLACE VIEW v_payment_summary AS
SELECT
    method,
    COUNT(*) AS payment_count,
    CAST(SUM(amount) AS NUMBER(18,0)) AS total_amount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM payments), 1) AS pct,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) AS refunded,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed
FROM payments
GROUP BY method
ORDER BY payment_count DESC;

CREATE OR REPLACE VIEW v_order_detail AS
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
    ca.address1 || ' ' || NVL(ca.address2, '') AS delivery_address
FROM orders o
JOIN customers c ON o.customer_id = c.id
LEFT JOIN payments p ON o.id = p.order_id
LEFT JOIN shipping s ON o.id = s.order_id
LEFT JOIN customer_addresses ca ON o.address_id = ca.id;

CREATE OR REPLACE VIEW v_revenue_growth AS
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
        TO_CHAR(ordered_at, 'YYYY-MM') AS month,
        CAST(SUM(total_amount) AS NUMBER(18,0)) AS revenue,
        LAG(CAST(SUM(total_amount) AS NUMBER(18,0))) OVER (ORDER BY TO_CHAR(ordered_at, 'YYYY-MM')) AS prev_revenue
    FROM orders
    WHERE status != 'cancelled'
    GROUP BY TO_CHAR(ordered_at, 'YYYY-MM')
) sub
ORDER BY month;

CREATE OR REPLACE VIEW v_top_products_by_category AS
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
        NVL(SUM(oi.subtotal), 0) AS total_revenue,
        NVL(SUM(oi.quantity), 0) AS total_sold,
        ROW_NUMBER() OVER (
            PARTITION BY p.category_id
            ORDER BY NVL(SUM(oi.subtotal), 0) DESC
        ) AS rank_in_category
    FROM products p
    JOIN categories cat ON p.category_id = cat.id
    LEFT JOIN order_items oi ON p.id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.id AND o.status != 'cancelled'
    GROUP BY p.id, cat.name, p.name, p.brand, p.category_id
) sub
WHERE rank_in_category <= 5;

CREATE OR REPLACE VIEW v_customer_rfm AS
WITH rfm_raw AS (
    SELECT
        c.id AS customer_id,
        c.name,
        c.grade,
        TRUNC(DATE '2025-06-30' - CAST(MAX(o.ordered_at) AS DATE)) AS recency_days,
        COUNT(o.id) AS frequency,
        CAST(SUM(o.total_amount) AS NUMBER(18,0)) AS monetary
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    WHERE o.status != 'cancelled'
    GROUP BY c.id, c.name, c.grade
),
rfm_scored AS (
    SELECT r.*,
        NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
    FROM rfm_raw r
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

CREATE OR REPLACE VIEW v_cart_abandonment AS
SELECT
    c.id AS cart_id,
    cust.name AS customer_name,
    cust.email,
    c.status,
    c.created_at,
    COUNT(ci.id) AS item_count,
    CAST(SUM(p.price * ci.quantity) AS NUMBER(18,0)) AS potential_revenue,
    LISTAGG(p.name, ', ') WITHIN GROUP (ORDER BY p.name) AS products
FROM carts c
JOIN customers cust ON c.customer_id = cust.id
JOIN cart_items ci ON c.id = ci.cart_id
JOIN products p ON ci.product_id = p.id
WHERE c.status = 'abandoned'
GROUP BY c.id, cust.name, cust.email, c.status, c.created_at;

CREATE OR REPLACE VIEW v_supplier_performance AS
SELECT
    s.id AS supplier_id,
    s.company_name,
    COUNT(DISTINCT p.id) AS product_count,
    SUM(CASE WHEN p.is_active = 1 THEN 1 ELSE 0 END) AS active_products,
    NVL(sales.total_revenue, 0) AS total_revenue,
    NVL(sales.total_sold, 0) AS total_sold,
    NVL(ret.return_count, 0) AS return_count,
    CASE
        WHEN NVL(sales.total_sold, 0) > 0
        THEN ROUND(NVL(ret.return_count, 0) * 100.0 / sales.total_sold, 2)
        ELSE 0
    END AS return_rate_pct
FROM suppliers s
LEFT JOIN products p ON s.id = p.supplier_id
LEFT JOIN (
    SELECT p2.supplier_id,
           CAST(SUM(oi.subtotal) AS NUMBER(18,0)) AS total_revenue,
           SUM(oi.quantity) AS total_sold
    FROM order_items oi
    JOIN products p2 ON oi.product_id = p2.id
    JOIN orders o ON oi.order_id = o.id
    WHERE o.status != 'cancelled'
    GROUP BY p2.supplier_id
) sales ON s.id = sales.supplier_id
LEFT JOIN (
    SELECT p3.supplier_id, COUNT(*) AS return_count
    FROM returns r
    JOIN order_items oi ON r.order_id = oi.order_id
    JOIN products p3 ON oi.product_id = p3.id
    GROUP BY p3.supplier_id
) ret ON s.id = ret.supplier_id
GROUP BY s.id, s.company_name, sales.total_revenue, sales.total_sold, ret.return_count;

CREATE OR REPLACE VIEW v_hourly_pattern AS
SELECT
    EXTRACT(HOUR FROM ordered_at) AS hour,
    COUNT(*) AS order_count,
    CAST(AVG(total_amount) AS NUMBER(18,0)) AS avg_amount,
    CASE
        WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 0 AND 5 THEN 'dawn'
        WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 6 AND 11 THEN 'morning'
        WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 12 AND 17 THEN 'afternoon'
        ELSE 'evening'
    END AS time_slot
FROM orders
WHERE status != 'cancelled'
GROUP BY EXTRACT(HOUR FROM ordered_at),
    CASE
        WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 0 AND 5 THEN 'dawn'
        WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 6 AND 11 THEN 'morning'
        WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 12 AND 17 THEN 'afternoon'
        ELSE 'evening'
    END
ORDER BY hour;

CREATE OR REPLACE VIEW v_product_abc AS
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
            CAST(NVL(SUM(oi.subtotal), 0) AS NUMBER(18,0)) AS total_revenue
        FROM products p
        LEFT JOIN order_items oi ON p.id = oi.product_id
        LEFT JOIN orders o ON oi.order_id = o.id AND o.status != 'cancelled'
        GROUP BY p.id, p.name, p.brand
    ) base
) ranked
ORDER BY total_revenue DESC;

CREATE OR REPLACE VIEW v_staff_workload AS
SELECT
    s.id AS staff_id,
    s.name,
    s.department,
    NVL(comp.complaint_count, 0) AS complaint_count,
    NVL(comp.resolved_count, 0) AS resolved_count,
    NVL(comp.avg_resolve_hours, 0) AS avg_resolve_hours,
    NVL(ord.cs_order_count, 0) AS cs_order_count
FROM staff s
LEFT JOIN (
    SELECT
        staff_id,
        COUNT(*) AS complaint_count,
        SUM(CASE WHEN status IN ('resolved','closed') THEN 1 ELSE 0 END) AS resolved_count,
        CAST(AVG(
            CASE WHEN resolved_at IS NOT NULL
            THEN EXTRACT(HOUR FROM (resolved_at - created_at))
                 + EXTRACT(DAY FROM (resolved_at - created_at)) * 24
            END
        ) AS NUMBER(18,0)) AS avg_resolve_hours
    FROM complaints
    GROUP BY staff_id
) comp ON s.id = comp.staff_id
LEFT JOIN (
    SELECT staff_id, COUNT(*) AS cs_order_count
    FROM orders WHERE staff_id IS NOT NULL
    GROUP BY staff_id
) ord ON s.id = ord.staff_id
WHERE s.department = 'CS' OR comp.complaint_count > 0;

CREATE OR REPLACE VIEW v_coupon_effectiveness AS
SELECT
    cp.id AS coupon_id,
    cp.code,
    cp.name,
    cp.type,
    cp.discount_value,
    cp.is_active,
    NVL(u.usage_count, 0) AS usage_count,
    cp.usage_limit,
    NVL(u.total_discount, 0) AS total_discount_given,
    NVL(u.total_order_revenue, 0) AS total_order_revenue,
    CASE
        WHEN NVL(u.total_discount, 0) > 0
        THEN ROUND(u.total_order_revenue / u.total_discount, 1)
        ELSE 0
    END AS roi_ratio
FROM coupons cp
LEFT JOIN (
    SELECT
        cu.coupon_id,
        COUNT(*) AS usage_count,
        CAST(SUM(cu.discount_amount) AS NUMBER(18,0)) AS total_discount,
        CAST(SUM(o.total_amount) AS NUMBER(18,0)) AS total_order_revenue
    FROM coupon_usage cu
    JOIN orders o ON cu.order_id = o.id
    GROUP BY cu.coupon_id
) u ON cp.id = u.coupon_id
ORDER BY NVL(u.usage_count, 0) DESC;

CREATE OR REPLACE VIEW v_return_analysis AS
SELECT
    reason,
    COUNT(*) AS total_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM returns), 1) AS pct,
    SUM(CASE WHEN return_type = 'refund' THEN 1 ELSE 0 END) AS refund_count,
    SUM(CASE WHEN return_type = 'exchange' THEN 1 ELSE 0 END) AS exchange_count,
    CAST(AVG(refund_amount) AS NUMBER(18,0)) AS avg_refund_amount,
    SUM(CASE WHEN inspection_result = 'defective' THEN 1 ELSE 0 END) AS defective_count,
    SUM(CASE WHEN inspection_result = 'good' THEN 1 ELSE 0 END) AS good_count,
    CAST(AVG(
        CASE WHEN completed_at IS NOT NULL
        THEN CAST(completed_at AS DATE) - CAST(requested_at AS DATE)
        END
    ) AS NUMBER(18,0)) AS avg_process_days
FROM returns
GROUP BY reason
ORDER BY total_count DESC;

CREATE OR REPLACE VIEW v_yearly_kpi AS
SELECT
    o_stats.yr AS year,
    o_stats.total_revenue,
    o_stats.order_count,
    o_stats.customer_count,
    CAST(o_stats.total_revenue / o_stats.order_count AS NUMBER(18,0)) AS avg_order_value,
    CAST(o_stats.total_revenue / o_stats.customer_count AS NUMBER(18,0)) AS revenue_per_customer,
    NVL(c.new_customers, 0) AS new_customers,
    o_stats.cancel_count,
    ROUND(o_stats.cancel_count * 100.0 / o_stats.order_count, 1) AS cancel_rate_pct,
    o_stats.return_count,
    ROUND(o_stats.return_count * 100.0 / o_stats.order_count, 1) AS return_rate_pct,
    NVL(r.review_count, 0) AS review_count,
    NVL(comp.complaint_count, 0) AS complaint_count
FROM (
    SELECT
        EXTRACT(YEAR FROM o.ordered_at) AS yr,
        CAST(SUM(CASE WHEN o.status != 'cancelled' THEN o.total_amount ELSE 0 END) AS NUMBER(18,0)) AS total_revenue,
        COUNT(*) AS order_count,
        COUNT(DISTINCT o.customer_id) AS customer_count,
        SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) AS cancel_count,
        SUM(CASE WHEN o.status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS return_count
    FROM orders o
    GROUP BY EXTRACT(YEAR FROM o.ordered_at)
) o_stats
LEFT JOIN (
    SELECT EXTRACT(YEAR FROM created_at) AS yr, COUNT(*) AS new_customers
    FROM customers GROUP BY EXTRACT(YEAR FROM created_at)
) c ON o_stats.yr = c.yr
LEFT JOIN (
    SELECT EXTRACT(YEAR FROM created_at) AS yr, COUNT(*) AS review_count
    FROM reviews GROUP BY EXTRACT(YEAR FROM created_at)
) r ON o_stats.yr = r.yr
LEFT JOIN (
    SELECT EXTRACT(YEAR FROM created_at) AS yr, COUNT(*) AS complaint_count
    FROM complaints GROUP BY EXTRACT(YEAR FROM created_at)
) comp ON o_stats.yr = comp.yr
ORDER BY o_stats.yr;

-- =============================================
-- Access control examples (commented out)
-- =============================================
-- CREATE USER reader IDENTIFIED BY readonly_password;
-- CREATE USER admin_user IDENTIFIED BY admin_password;
-- GRANT CREATE SESSION TO reader;
-- GRANT SELECT ANY TABLE TO reader;
-- GRANT CREATE SESSION, DBA TO admin_user;
-- REVOKE DROP ANY TABLE FROM reader;
"""


PROCEDURES_SQL = """\
-- =============================================
-- E-commerce Stored Procedures - Oracle 19c+
-- =============================================

-- =============================================
-- sp_place_order: Create a new order and deduct customer points
-- Parameters:
--   p_customer_id  - Customer placing the order
--   p_address_id   - Delivery address
--   p_order_id     - OUT: created order ID
--   p_order_number - OUT: generated order number
--   p_total_amount - OUT: order total
-- =============================================
CREATE OR REPLACE PROCEDURE sp_place_order(
    p_customer_id   IN  NUMBER,
    p_address_id    IN  NUMBER,
    p_order_id      OUT NUMBER,
    p_order_number  OUT VARCHAR2,
    p_total_amount  OUT NUMBER
)
AS
    v_total         NUMBER(12,2) := 0;
    v_points        NUMBER := 0;
    v_now           TIMESTAMP := SYSTIMESTAMP;
    v_max_id        NUMBER;
BEGIN
    -- Generate order number
    SELECT NVL(MAX(id), 0) + 1 INTO v_max_id FROM orders;
    p_order_number := 'ORD-' || TO_CHAR(v_now, 'YYYYMMDD') || '-' || LPAD(v_max_id, 5, '0');

    -- Calculate cart total
    SELECT NVL(SUM(p.price * ci.quantity), 0)
    INTO v_total
    FROM carts c
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.customer_id = p_customer_id AND c.status = 'active';

    IF v_total = 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Cart is empty');
    END IF;

    p_total_amount := v_total;

    -- Get customer point balance
    SELECT point_balance INTO v_points
    FROM customers WHERE id = p_customer_id FOR UPDATE;

    -- Create order
    INSERT INTO orders (order_number, customer_id, address_id, status,
                        total_amount, discount_amount, shipping_fee,
                        point_used, point_earned, ordered_at, created_at, updated_at)
    VALUES (p_order_number, p_customer_id, p_address_id, 'pending',
            v_total, 0, CASE WHEN v_total >= 50000 THEN 0 ELSE 3000 END,
            0, FLOOR(v_total * 0.01), v_now, v_now, v_now)
    RETURNING id INTO p_order_id;

    -- Move cart items to order items
    INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_amount, subtotal)
    SELECT p_order_id, ci.product_id, ci.quantity, p.price, 0, p.price * ci.quantity
    FROM carts c
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.customer_id = p_customer_id AND c.status = 'active';

    -- Mark cart as converted
    UPDATE carts SET status = 'converted', updated_at = v_now
    WHERE customer_id = p_customer_id AND status = 'active';

    COMMIT;
END;
/

-- =============================================
-- sp_expire_points: Expire points older than 1 year
-- Parameters:
--   p_expired_count - OUT: number of expired transactions
-- =============================================
CREATE OR REPLACE PROCEDURE sp_expire_points(
    p_expired_count OUT NUMBER
)
AS
    v_now TIMESTAMP := SYSTIMESTAMP;
BEGIN
    p_expired_count := 0;

    -- Find unexpired earn transactions past their expiry date
    -- and insert expiry records
    INSERT INTO point_transactions (customer_id, order_id, type, reason, amount, balance_after, expires_at, created_at)
    SELECT
        pt.customer_id,
        pt.order_id,
        'expire',
        'expiry',
        -pt.amount,
        c.point_balance - pt.amount,
        NULL,
        v_now
    FROM point_transactions pt
    JOIN customers c ON pt.customer_id = c.id
    WHERE pt.type = 'earn'
      AND pt.expires_at IS NOT NULL
      AND pt.expires_at < v_now
      AND NOT EXISTS (
          SELECT 1 FROM point_transactions e
          WHERE e.customer_id = pt.customer_id
            AND e.type = 'expire'
            AND e.order_id = pt.order_id
      );

    p_expired_count := SQL%ROWCOUNT;

    -- Update customer balances
    UPDATE customers c
    SET c.point_balance = GREATEST(0, c.point_balance - (
        SELECT NVL(SUM(pt.amount), 0)
        FROM point_transactions pt
        WHERE pt.customer_id = c.id
          AND pt.type = 'earn'
          AND pt.expires_at IS NOT NULL
          AND pt.expires_at < v_now
          AND NOT EXISTS (
              SELECT 1 FROM point_transactions e
              WHERE e.customer_id = pt.customer_id
                AND e.type = 'expire'
                AND e.order_id = pt.order_id
                AND e.created_at < v_now
          )
    ))
    WHERE c.point_balance > 0;

    COMMIT;
END;
/

-- =============================================
-- sp_monthly_settlement: Monthly sales summary report
-- Parameters:
--   p_year   - Report year
--   p_month  - Report month
--   p_cursor - OUT: result cursor
-- =============================================
CREATE OR REPLACE PROCEDURE sp_monthly_settlement(
    p_year   IN  NUMBER,
    p_month  IN  NUMBER,
    p_cursor OUT SYS_REFCURSOR
)
AS
    v_start_date TIMESTAMP;
    v_end_date   TIMESTAMP;
BEGIN
    v_start_date := TO_TIMESTAMP(p_year || '-' || LPAD(p_month, 2, '0') || '-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS');
    v_end_date := ADD_MONTHS(v_start_date, 1);

    -- Order summary
    OPEN p_cursor FOR
    SELECT
        COUNT(*) AS total_orders,
        COUNT(DISTINCT customer_id) AS unique_customers,
        SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS gross_revenue,
        SUM(discount_amount) AS total_discounts,
        SUM(shipping_fee) AS total_shipping,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        SUM(CASE WHEN status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returned_orders,
        ROUND(AVG(CASE WHEN status != 'cancelled' THEN total_amount END), 0) AS avg_order_value
    FROM orders
    WHERE ordered_at >= v_start_date AND ordered_at < v_end_date;
END;
/

-- =============================================
-- sp_monthly_top_products: Top 10 products for a given month
-- Parameters:
--   p_year   - Report year
--   p_month  - Report month
--   p_cursor - OUT: result cursor
-- =============================================
CREATE OR REPLACE PROCEDURE sp_monthly_top_products(
    p_year   IN  NUMBER,
    p_month  IN  NUMBER,
    p_cursor OUT SYS_REFCURSOR
)
AS
    v_start_date TIMESTAMP;
    v_end_date   TIMESTAMP;
BEGIN
    v_start_date := TO_TIMESTAMP(p_year || '-' || LPAD(p_month, 2, '0') || '-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS');
    v_end_date := ADD_MONTHS(v_start_date, 1);

    OPEN p_cursor FOR
    SELECT
        p.id AS product_id,
        p.name AS product_name,
        p.brand,
        SUM(oi.quantity) AS total_qty,
        SUM(oi.subtotal) AS total_revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    JOIN products p ON oi.product_id = p.id
    WHERE o.ordered_at >= v_start_date AND o.ordered_at < v_end_date
      AND o.status != 'cancelled'
    GROUP BY p.id, p.name, p.brand
    ORDER BY total_revenue DESC
    FETCH FIRST 10 ROWS ONLY;
END;
/

-- =============================================
-- sp_monthly_payments: Payment breakdown for a given month
-- Parameters:
--   p_year   - Report year
--   p_month  - Report month
--   p_cursor - OUT: result cursor
-- =============================================
CREATE OR REPLACE PROCEDURE sp_monthly_payments(
    p_year   IN  NUMBER,
    p_month  IN  NUMBER,
    p_cursor OUT SYS_REFCURSOR
)
AS
    v_start_date TIMESTAMP;
    v_end_date   TIMESTAMP;
BEGIN
    v_start_date := TO_TIMESTAMP(p_year || '-' || LPAD(p_month, 2, '0') || '-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS');
    v_end_date := ADD_MONTHS(v_start_date, 1);

    OPEN p_cursor FOR
    SELECT
        pay.method,
        COUNT(*) AS cnt,
        SUM(pay.amount) AS total_amount,
        ROUND(COUNT(*) * 100.0 / (
            SELECT COUNT(*) FROM payments pay2
            JOIN orders o2 ON pay2.order_id = o2.id
            WHERE o2.ordered_at >= v_start_date AND o2.ordered_at < v_end_date
        ), 1) AS pct
    FROM payments pay
    JOIN orders o ON pay.order_id = o.id
    WHERE o.ordered_at >= v_start_date AND o.ordered_at < v_end_date
    GROUP BY pay.method
    ORDER BY total_amount DESC;
END;
/

-- =============================================
-- sp_cancel_order: Cancel an order and restore stock
-- Parameters:
--   p_order_id   - Order to cancel
--   p_reason     - Cancellation reason
-- =============================================
CREATE OR REPLACE PROCEDURE sp_cancel_order(
    p_order_id   IN NUMBER,
    p_reason     IN VARCHAR2
)
AS
    v_status      VARCHAR2(30);
    v_customer_id NUMBER;
    v_point_used  NUMBER;
    v_now         TIMESTAMP := SYSTIMESTAMP;
BEGIN
    -- Verify order exists and is cancellable
    SELECT status, customer_id, point_used
    INTO v_status, v_customer_id, v_point_used
    FROM orders WHERE id = p_order_id FOR UPDATE;

    IF v_status NOT IN ('pending', 'paid') THEN
        RAISE_APPLICATION_ERROR(-20002, 'Order cannot be cancelled in current status');
    END IF;

    -- Restore stock
    MERGE INTO products p
    USING (
        SELECT product_id, quantity
        FROM order_items
        WHERE order_id = p_order_id
    ) oi ON (p.id = oi.product_id)
    WHEN MATCHED THEN
        UPDATE SET p.stock_qty = p.stock_qty + oi.quantity;

    -- Restore points if used
    IF v_point_used > 0 THEN
        UPDATE customers SET point_balance = point_balance + v_point_used
        WHERE id = v_customer_id;

        INSERT INTO point_transactions (customer_id, order_id, type, reason, amount, balance_after, created_at)
        SELECT v_customer_id, p_order_id, 'earn', 'purchase',
               v_point_used,
               point_balance,
               v_now
        FROM customers WHERE id = v_customer_id;
    END IF;

    -- Update order status
    UPDATE orders
    SET status = 'cancelled', cancelled_at = v_now, updated_at = v_now,
        notes = NVL(notes, '') || CHR(10) || '[Cancelled] ' || p_reason
    WHERE id = p_order_id;

    -- Refund payment
    UPDATE payments SET status = 'refunded', refunded_at = v_now
    WHERE order_id = p_order_id;

    COMMIT;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20003, 'Order not found');
END;
/

-- =============================================
-- sp_update_customer_grades: Recalculate grades based on spending
-- Parameters:
--   p_grades_updated - OUT: number of grades changed
-- =============================================
CREATE OR REPLACE PROCEDURE sp_update_customer_grades(
    p_grades_updated OUT NUMBER
)
AS
    v_now TIMESTAMP := SYSTIMESTAMP;
BEGIN
    p_grades_updated := 0;

    -- Use MERGE to update grades and record history in one pass
    -- First, update customer grades
    MERGE INTO customers c
    USING (
        SELECT
            cust.id AS customer_id,
            cust.grade AS old_grade,
            CASE
                WHEN NVL(s.total_spent, 0) >= 5000000 THEN 'VIP'
                WHEN NVL(s.total_spent, 0) >= 2000000 THEN 'GOLD'
                WHEN NVL(s.total_spent, 0) >= 500000  THEN 'SILVER'
                ELSE 'BRONZE'
            END AS new_grade
        FROM customers cust
        LEFT JOIN (
            SELECT customer_id, SUM(total_amount) AS total_spent
            FROM orders
            WHERE status != 'cancelled'
              AND ordered_at >= ADD_MONTHS(v_now, -12)
            GROUP BY customer_id
        ) s ON cust.id = s.customer_id
        WHERE cust.is_active = 1
    ) ng ON (c.id = ng.customer_id)
    WHEN MATCHED THEN
        UPDATE SET c.grade = ng.new_grade, c.updated_at = v_now
        WHERE c.grade != ng.new_grade;

    p_grades_updated := SQL%ROWCOUNT;

    -- Record grade history for changed grades
    INSERT INTO customer_grade_history (customer_id, old_grade, new_grade, changed_at, reason)
    SELECT
        cust.id,
        cust.grade,
        CASE
            WHEN NVL(s.total_spent, 0) >= 5000000 THEN 'VIP'
            WHEN NVL(s.total_spent, 0) >= 2000000 THEN 'GOLD'
            WHEN NVL(s.total_spent, 0) >= 500000  THEN 'SILVER'
            ELSE 'BRONZE'
        END,
        v_now,
        'yearly_review'
    FROM customers cust
    LEFT JOIN (
        SELECT customer_id, SUM(total_amount) AS total_spent
        FROM orders
        WHERE status != 'cancelled'
          AND ordered_at >= ADD_MONTHS(v_now, -12)
        GROUP BY customer_id
    ) s ON cust.id = s.customer_id
    WHERE cust.is_active = 1
      AND cust.grade != CASE
            WHEN NVL(s.total_spent, 0) >= 5000000 THEN 'VIP'
            WHEN NVL(s.total_spent, 0) >= 2000000 THEN 'GOLD'
            WHEN NVL(s.total_spent, 0) >= 500000  THEN 'SILVER'
            ELSE 'BRONZE'
        END;

    COMMIT;
END;
/

-- =============================================
-- sp_cleanup_abandoned_carts: Remove old abandoned carts
-- Parameters:
--   p_days_old     - Delete carts older than this many days
--   p_carts_deleted - OUT: number of deleted carts
-- =============================================
CREATE OR REPLACE PROCEDURE sp_cleanup_abandoned_carts(
    p_days_old      IN  NUMBER,
    p_carts_deleted OUT NUMBER
)
AS
    v_cutoff TIMESTAMP;
BEGIN
    v_cutoff := SYSTIMESTAMP - NUMTODSINTERVAL(p_days_old, 'DAY');

    -- Delete cart items first (FK)
    DELETE FROM cart_items
    WHERE cart_id IN (
        SELECT id FROM carts
        WHERE status = 'abandoned' AND updated_at < v_cutoff
    );

    -- Delete abandoned carts
    DELETE FROM carts
    WHERE status = 'abandoned' AND updated_at < v_cutoff;

    p_carts_deleted := SQL%ROWCOUNT;

    COMMIT;
END;
/

-- =============================================
-- sp_product_restock: Process product restocking
-- Parameters:
--   p_product_id - Product to restock
--   p_quantity   - Quantity to add
--   p_notes      - Restock notes
--   p_new_qty    - OUT: new stock quantity
-- =============================================
CREATE OR REPLACE PROCEDURE sp_product_restock(
    p_product_id IN  NUMBER,
    p_quantity   IN  NUMBER,
    p_notes      IN  VARCHAR2,
    p_new_qty    OUT NUMBER
)
AS
    v_now    TIMESTAMP := SYSTIMESTAMP;
    v_exists NUMBER;
BEGIN
    IF p_quantity <= 0 THEN
        RAISE_APPLICATION_ERROR(-20004, 'Quantity must be positive');
    END IF;

    -- Check product exists
    SELECT COUNT(*) INTO v_exists FROM products WHERE id = p_product_id;
    IF v_exists = 0 THEN
        RAISE_APPLICATION_ERROR(-20005, 'Product not found');
    END IF;

    -- Update stock
    UPDATE products
    SET stock_qty = stock_qty + p_quantity, updated_at = v_now
    WHERE id = p_product_id
    RETURNING stock_qty INTO p_new_qty;

    -- Record inventory transaction
    INSERT INTO inventory_transactions (product_id, type, quantity, notes, created_at)
    VALUES (p_product_id, 'inbound', p_quantity, p_notes, v_now);

    COMMIT;
END;
/

-- =============================================
-- sp_customer_statistics: Return customer stats via OUT params
-- Parameters:
--   p_customer_id     - Customer ID
--   p_total_orders    - OUT: total order count
--   p_total_spent     - OUT: total spending
--   p_avg_order       - OUT: average order value
--   p_days_since_last - OUT: days since last order
-- =============================================
CREATE OR REPLACE PROCEDURE sp_customer_statistics(
    p_customer_id     IN  NUMBER,
    p_total_orders    OUT NUMBER,
    p_total_spent     OUT NUMBER,
    p_avg_order       OUT NUMBER,
    p_days_since_last OUT NUMBER
)
AS
BEGIN
    SELECT
        COUNT(*),
        NVL(SUM(total_amount), 0),
        NVL(AVG(total_amount), 0),
        NVL(TRUNC(SYSDATE - CAST(MAX(ordered_at) AS DATE)), -1)
    INTO p_total_orders, p_total_spent, p_avg_order, p_days_since_last
    FROM orders
    WHERE customer_id = p_customer_id AND status != 'cancelled';
END;
/

-- =============================================
-- sp_daily_summary: Daily KPI summary report
-- Parameters:
--   p_date   - Target date (DATE)
--   p_cursor - OUT: result cursor
-- =============================================
CREATE OR REPLACE PROCEDURE sp_daily_summary(
    p_date   IN  DATE,
    p_cursor OUT SYS_REFCURSOR
)
AS
    v_start TIMESTAMP;
    v_end   TIMESTAMP;
BEGIN
    v_start := CAST(p_date AS TIMESTAMP);
    v_end   := CAST(p_date + 1 AS TIMESTAMP);

    OPEN p_cursor FOR
    SELECT
        p_date AS report_date,
        COUNT(*) AS total_orders,
        COUNT(DISTINCT customer_id) AS unique_customers,
        SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS revenue,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancellations,
        ROUND(AVG(CASE WHEN status != 'cancelled' THEN total_amount END), 0) AS avg_order_value,
        (SELECT COUNT(*) FROM customers WHERE created_at >= v_start AND created_at < v_end) AS new_customers,
        (SELECT COUNT(*) FROM reviews WHERE created_at >= v_start AND created_at < v_end) AS new_reviews,
        (SELECT ROUND(AVG(rating), 1) FROM reviews WHERE created_at >= v_start AND created_at < v_end) AS avg_rating
    FROM orders
    WHERE ordered_at >= v_start AND ordered_at < v_end;
END;
/

-- =============================================
-- sp_search_products: Dynamic search with optional filters
-- Parameters:
--   p_keyword       - Search keyword (name/brand/description)
--   p_category_id   - Category filter (NULL = all)
--   p_min_price     - Minimum price (NULL = no limit)
--   p_max_price     - Maximum price (NULL = no limit)
--   p_in_stock_only - Only show in-stock items (1/0)
--   p_cursor        - OUT: result cursor
-- =============================================
CREATE OR REPLACE PROCEDURE sp_search_products(
    p_keyword       IN  VARCHAR2,
    p_category_id   IN  NUMBER,
    p_min_price     IN  NUMBER,
    p_max_price     IN  NUMBER,
    p_in_stock_only IN  NUMBER,
    p_cursor        OUT SYS_REFCURSOR
)
AS
    v_sql VARCHAR2(4000);
    v_kw  VARCHAR2(200);
BEGIN
    v_sql := 'SELECT p.id, p.name, p.brand, p.price, p.stock_qty, c.name AS category
              FROM products p
              JOIN categories c ON p.category_id = c.id
              WHERE p.is_active = 1';

    IF p_keyword IS NOT NULL AND LENGTH(p_keyword) > 0 THEN
        v_kw := '%' || p_keyword || '%';
        v_sql := v_sql || ' AND (p.name LIKE :kw1 OR p.brand LIKE :kw2 OR p.description LIKE :kw3)';
    END IF;

    IF p_category_id IS NOT NULL THEN
        v_sql := v_sql || ' AND p.category_id = ' || p_category_id;
    END IF;

    IF p_min_price IS NOT NULL THEN
        v_sql := v_sql || ' AND p.price >= ' || p_min_price;
    END IF;

    IF p_max_price IS NOT NULL THEN
        v_sql := v_sql || ' AND p.price <= ' || p_max_price;
    END IF;

    IF p_in_stock_only = 1 THEN
        v_sql := v_sql || ' AND p.stock_qty > 0';
    END IF;

    v_sql := v_sql || ' ORDER BY p.name FETCH FIRST 100 ROWS ONLY';

    IF p_keyword IS NOT NULL AND LENGTH(p_keyword) > 0 THEN
        OPEN p_cursor FOR v_sql USING v_kw, v_kw, v_kw;
    ELSE
        OPEN p_cursor FOR v_sql;
    END IF;
END;
/

-- =============================================
-- sp_transfer_points: Transfer points between customers
-- Parameters:
--   p_from_customer_id - Sender
--   p_to_customer_id   - Receiver
--   p_amount           - Points to transfer
-- =============================================
CREATE OR REPLACE PROCEDURE sp_transfer_points(
    p_from_customer_id IN NUMBER,
    p_to_customer_id   IN NUMBER,
    p_amount           IN NUMBER
)
AS
    v_from_balance NUMBER;
    v_now          TIMESTAMP := SYSTIMESTAMP;
BEGIN
    IF p_amount <= 0 THEN
        RAISE_APPLICATION_ERROR(-20006, 'Transfer amount must be positive');
    END IF;

    IF p_from_customer_id = p_to_customer_id THEN
        RAISE_APPLICATION_ERROR(-20007, 'Cannot transfer to self');
    END IF;

    -- Lock both rows in consistent order to prevent deadlock
    SELECT point_balance INTO v_from_balance
    FROM customers WHERE id = LEAST(p_from_customer_id, p_to_customer_id) FOR UPDATE;
    SELECT point_balance INTO v_from_balance
    FROM customers WHERE id = GREATEST(p_from_customer_id, p_to_customer_id) FOR UPDATE;

    -- Re-read actual sender balance
    SELECT point_balance INTO v_from_balance FROM customers WHERE id = p_from_customer_id;

    IF v_from_balance < p_amount THEN
        RAISE_APPLICATION_ERROR(-20008, 'Insufficient point balance');
    END IF;

    -- Deduct from sender
    UPDATE customers SET point_balance = point_balance - p_amount WHERE id = p_from_customer_id;
    INSERT INTO point_transactions (customer_id, type, reason, amount, balance_after, created_at)
    SELECT p_from_customer_id, 'use', 'purchase', -p_amount, point_balance, v_now
    FROM customers WHERE id = p_from_customer_id;

    -- Add to receiver
    UPDATE customers SET point_balance = point_balance + p_amount WHERE id = p_to_customer_id;
    INSERT INTO point_transactions (customer_id, type, reason, amount, balance_after, created_at)
    SELECT p_to_customer_id, 'earn', 'purchase', p_amount, point_balance, v_now
    FROM customers WHERE id = p_to_customer_id;

    COMMIT;
END;
/

-- =============================================
-- sp_generate_order_report: Cursor-based order detail report
-- Parameters:
--   p_year   - Report year
--   p_month  - Report month
--   p_cursor - OUT: result cursor
-- =============================================
CREATE OR REPLACE PROCEDURE sp_generate_order_report(
    p_year   IN  NUMBER,
    p_month  IN  NUMBER,
    p_cursor OUT SYS_REFCURSOR
)
AS
BEGIN
    OPEN p_cursor FOR
    SELECT
        o.order_number,
        o.total_amount,
        (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) AS item_count,
        (SELECT p.name FROM order_items oi
         JOIN products p ON oi.product_id = p.id
         WHERE oi.order_id = o.id
         ORDER BY oi.subtotal DESC
         FETCH FIRST 1 ROWS ONLY) AS top_product
    FROM orders o
    WHERE EXTRACT(YEAR FROM o.ordered_at) = p_year
      AND EXTRACT(MONTH FROM o.ordered_at) = p_month
      AND o.status != 'cancelled'
    ORDER BY o.total_amount DESC;
END;
/

-- =============================================
-- sp_bulk_update_prices: Update multiple product prices from JSON
-- Parameters:
--   p_price_json    - JSON array: [{"product_id": 1, "new_price": 99000}, ...]
--   p_products_updated - OUT: count of updated products
-- =============================================
CREATE OR REPLACE PROCEDURE sp_bulk_update_prices(
    p_price_json       IN  CLOB,
    p_products_updated OUT NUMBER
)
AS
    v_now TIMESTAMP := SYSTIMESTAMP;
BEGIN
    p_products_updated := 0;

    -- Record old prices in history
    INSERT INTO product_prices (product_id, price, started_at, ended_at, change_reason)
    SELECT p.id, p.price, p.updated_at, v_now, 'price_drop'
    FROM products p
    JOIN (
        SELECT
            TO_NUMBER(j.product_id) AS product_id,
            TO_NUMBER(j.new_price) AS new_price
        FROM JSON_TABLE(p_price_json, '$[*]' COLUMNS (
            product_id VARCHAR2(20) PATH '$.product_id',
            new_price  VARCHAR2(20) PATH '$.new_price'
        )) j
    ) jt ON p.id = jt.product_id
    WHERE p.price != jt.new_price;

    -- Update prices using MERGE
    MERGE INTO products p
    USING (
        SELECT
            TO_NUMBER(j.product_id) AS product_id,
            TO_NUMBER(j.new_price) AS new_price
        FROM JSON_TABLE(p_price_json, '$[*]' COLUMNS (
            product_id VARCHAR2(20) PATH '$.product_id',
            new_price  VARCHAR2(20) PATH '$.new_price'
        )) j
    ) jt ON (p.id = jt.product_id)
    WHEN MATCHED THEN
        UPDATE SET p.price = jt.new_price, p.updated_at = v_now
        WHERE p.price != jt.new_price;

    p_products_updated := SQL%ROWCOUNT;

    COMMIT;
END;
/

-- =============================================
-- sp_archive_old_orders: Move old orders to archive concept
-- Parameters:
--   p_before_date    - Archive orders before this date
--   p_orders_archived - OUT: count of archived orders
-- =============================================
CREATE OR REPLACE PROCEDURE sp_archive_old_orders(
    p_before_date     IN  DATE,
    p_orders_archived OUT NUMBER
)
AS
    v_now TIMESTAMP := SYSTIMESTAMP;
BEGIN
    p_orders_archived := 0;

    -- In a real system, INSERT INTO archive_orders SELECT ... would go here.
    -- For this tutorial, we mark them with a note instead of actually moving.
    UPDATE orders
    SET notes = NVL(notes, '') || CHR(10) || '[Archived] ' || TO_CHAR(v_now, 'YYYY-MM-DD HH24:MI:SS')
    WHERE ordered_at < CAST(p_before_date AS TIMESTAMP)
      AND status IN ('confirmed', 'returned')
      AND (notes IS NULL OR notes NOT LIKE '%[Archived]%');

    p_orders_archived := SQL%ROWCOUNT;

    COMMIT;
END;
/

-- =============================================
-- fn_calculate_shipping_fee: Calculate shipping fee for an order total
-- =============================================
CREATE OR REPLACE FUNCTION fn_calculate_shipping_fee(
    p_total_amount IN NUMBER
) RETURN NUMBER
AS
BEGIN
    IF p_total_amount >= 50000 THEN
        RETURN 0;
    ELSIF p_total_amount >= 30000 THEN
        RETURN 2500;
    ELSE
        RETURN 3000;
    END IF;
END;
/

-- =============================================
-- fn_customer_grade: Determine grade based on total spending
-- =============================================
CREATE OR REPLACE FUNCTION fn_customer_grade(
    p_total_spent IN NUMBER
) RETURN VARCHAR2
AS
BEGIN
    IF p_total_spent >= 5000000 THEN
        RETURN 'VIP';
    ELSIF p_total_spent >= 2000000 THEN
        RETURN 'GOLD';
    ELSIF p_total_spent >= 500000 THEN
        RETURN 'SILVER';
    ELSE
        RETURN 'BRONZE';
    END IF;
END;
/

-- =============================================
-- fn_order_status_label: Convert status code to display label
-- =============================================
CREATE OR REPLACE FUNCTION fn_order_status_label(
    p_status IN VARCHAR2
) RETURN VARCHAR2
AS
BEGIN
    RETURN CASE p_status
        WHEN 'pending'          THEN 'Pending'
        WHEN 'paid'             THEN 'Paid'
        WHEN 'preparing'        THEN 'Preparing'
        WHEN 'shipped'          THEN 'Shipped'
        WHEN 'delivered'        THEN 'Delivered'
        WHEN 'confirmed'        THEN 'Confirmed'
        WHEN 'cancelled'        THEN 'Cancelled'
        WHEN 'return_requested' THEN 'Return Requested'
        WHEN 'returned'         THEN 'Returned'
        ELSE 'Unknown'
    END;
END;
/

-- =============================================
-- fn_format_currency: Format number as currency string
-- =============================================
CREATE OR REPLACE FUNCTION fn_format_currency(
    p_amount IN NUMBER
) RETURN VARCHAR2
AS
BEGIN
    RETURN TO_CHAR(p_amount, 'FM999,999,999,990') || ' won';
END;
/

-- =============================================
-- fn_days_between_timestamps: Days between two timestamps
-- =============================================
CREATE OR REPLACE FUNCTION fn_days_between_timestamps(
    p_start_ts IN TIMESTAMP,
    p_end_ts   IN TIMESTAMP
) RETURN NUMBER
AS
BEGIN
    IF p_start_ts IS NULL OR p_end_ts IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN TRUNC(CAST(p_end_ts AS DATE) - CAST(p_start_ts AS DATE));
END;
/
"""


# Column mapping for Oracle data types
# Maps table.column -> True if the value should be treated as a boolean (0/1)
_BOOL_COLUMNS = {
    "categories.is_active",
    "suppliers.is_active",
    "products.is_active",
    "product_images.is_primary",
    "customers.is_active",
    "customer_addresses.is_default",
    "staff.is_active",
    "coupons.is_active",
    "wishlists.is_purchased",
    "wishlists.notify_on_sale",
    "reviews.is_verified",
    "calendar.is_weekend",
    "calendar.is_holiday",
    "returns.is_partial",
    "complaints.escalated",
    "promotions.is_active",
    "product_qna.is_answered",
}

# Columns that store dates (TEXT in SQLite -> DATE in Oracle)
_DATE_COLUMNS = {
    "customers.birth_date",
    "calendar.date_key",
}

# Columns that store CLOB content (need special handling for long strings)
_CLOB_COLUMNS = {
    "products.description",
    "products.specs",
    "orders.notes",
    "reviews.content",
    "complaints.content",
    "complaints.resolution",
    "returns.reason_detail",
    "product_qna.content",
}

# JSON columns stored as CLOB with IS JSON check
_JSON_COLUMNS = {
    "products.specs",
}

# Tables using GENERATED ALWAYS AS IDENTITY
_IDENTITY_TABLES = {
    "categories", "suppliers", "products", "product_images", "product_prices",
    "customers", "customer_addresses", "staff",
    "orders", "order_items", "payments", "shipping",
    "reviews", "inventory_transactions",
    "carts", "cart_items", "coupons", "coupon_usage",
    "wishlists", "complaints", "returns",
    "customer_grade_history",
    "tags", "product_views", "point_transactions",
    "promotions", "product_qna",
}


class OracleExporter:
    """Export generated data to Oracle-compatible SQL files."""

    def __init__(self, output_dir: str):
        self.output_dir = os.path.join(output_dir, "oracle")
        os.makedirs(self.output_dir, exist_ok=True)

    def export(self, data: dict[str, list[dict]]) -> str:
        """Export all data to Oracle SQL files."""
        schema_path = os.path.join(self.output_dir, "schema.sql")
        data_path = os.path.join(self.output_dir, "data.sql")
        proc_path = os.path.join(self.output_dir, "procedures.sql")

        # Write schema DDL
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write(SCHEMA_SQL)

        # Write data
        with open(data_path, "w", encoding="utf-8") as f:
            f.write("-- =============================================\n")
            f.write("-- E-commerce Test Data - Oracle\n")
            f.write("-- =============================================\n\n")
            f.write("ALTER SESSION SET NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS';\n")
            f.write("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD';\n\n")

            table_order = [
                "categories", "suppliers", "products", "product_images", "product_prices",
                "customers", "customer_addresses", "staff",
                "orders", "order_items", "payments", "shipping",
                "reviews", "inventory_transactions",
                "carts", "cart_items", "coupons", "coupon_usage",
                "wishlists", "complaints", "returns",
                "calendar", "customer_grade_history",
                "tags", "product_tags",
                "product_views",
                "point_transactions",
                "promotions", "promotion_products",
                "product_qna",
            ]

            for table in table_order:
                rows = data.get(table, [])
                if not rows:
                    continue
                self._write_inserts(f, table, rows)

            # Reset identity sequences to max(id) + 1
            f.write("\n-- Reset identity sequences after bulk load\n")
            for table in table_order:
                rows = data.get(table, [])
                if not rows or table not in _IDENTITY_TABLES:
                    continue
                max_id = max(r.get("id", 0) for r in rows)
                seq_name = f"ISEQ$$_{table.upper()}"
                f.write(f"-- To reset {table} identity, use:\n")
                f.write(f"-- ALTER TABLE {table} MODIFY id GENERATED ALWAYS AS IDENTITY (START WITH {max_id + 1});\n")

        # Write stored procedures
        with open(proc_path, "w", encoding="utf-8") as f:
            f.write(PROCEDURES_SQL)

        return self.output_dir

    def _write_inserts(self, f, table: str, rows: list[dict]):
        """Write INSERT ALL ... SELECT * FROM DUAL batched statements.

        Oracle does not support multi-row VALUES like MySQL/PG.
        We use INSERT ALL ... INTO ... VALUES ... SELECT * FROM DUAL
        with a maximum batch size of 500 rows.
        """
        if not rows:
            return

        columns = list(rows[0].keys())
        col_names = ", ".join(columns)
        batch_size = 500

        f.write(f"-- {table}: {len(rows)} rows\n")

        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]

            if len(batch) == 1:
                # Single row: plain INSERT
                row = batch[0]
                vals = []
                for col in columns:
                    v = row[col]
                    vals.append(self._format_value(table, col, v))
                f.write(f"INSERT INTO {table} ({col_names}) VALUES ({', '.join(vals)});\n")
            else:
                # Multiple rows: INSERT ALL
                f.write("INSERT ALL\n")
                for row in batch:
                    vals = []
                    for col in columns:
                        v = row[col]
                        vals.append(self._format_value(table, col, v))
                    f.write(f"  INTO {table} ({col_names}) VALUES ({', '.join(vals)})\n")
                f.write("SELECT * FROM DUAL;\n")

            f.write("\n")

    def _format_value(self, table: str, column: str, value: Any) -> str:
        """Format a Python value as an Oracle literal."""
        if value is None:
            return "NULL"

        key = f"{table}.{column}"

        # Boolean columns: Oracle uses NUMBER(1) with 0/1
        if key in _BOOL_COLUMNS:
            return "1" if value else "0"

        if isinstance(value, bool):
            return "1" if value else "0"

        if isinstance(value, (int, float)):
            return str(value)

        s = str(value)

        # DATE columns: use TO_DATE
        if key in _DATE_COLUMNS:
            if not s or s == "None":
                return "NULL"
            # Extract just the date portion
            date_part = s[:10]
            return f"TO_DATE('{date_part}', 'YYYY-MM-DD')"

        # Timestamp columns: use TO_TIMESTAMP for datetime-like strings
        if column.endswith("_at") or column == "ordered_at":
            if not s or s == "None":
                return "NULL"
            # Normalize the timestamp string
            ts = s[:19]  # 'YYYY-MM-DD HH:MI:SS'
            return f"TO_TIMESTAMP('{ts}', 'YYYY-MM-DD HH24:MI:SS')"

        # String value - escape single quotes by doubling them
        s = s.replace("'", "''")
        # Handle newlines (Oracle can handle them in strings with CHR())
        if "\n" in s:
            # Replace newlines with || CHR(10) ||
            parts = s.split("\n")
            escaped_parts = [f"'{p}'" for p in parts]
            return " || CHR(10) || ".join(escaped_parts)
        return f"'{s}'"
