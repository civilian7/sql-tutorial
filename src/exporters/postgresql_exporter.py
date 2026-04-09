"""PostgreSQL database exporter

Generates DDL, INSERT data, stored procedures, and materialized views
for PostgreSQL 15+.
"""

from __future__ import annotations

import os
from typing import Any


SCHEMA_SQL = """\
-- =============================================
-- E-commerce Test Database - PostgreSQL 15+
-- =============================================

-- CREATE DATABASE ecommerce OWNER postgres ENCODING 'UTF8';
-- \\c ecommerce

-- Custom ENUM types
CREATE TYPE order_status AS ENUM (
    'pending','paid','preparing','shipped','delivered','confirmed',
    'cancelled','return_requested','returned'
);
CREATE TYPE payment_method AS ENUM (
    'card','bank_transfer','virtual_account','kakao_pay','naver_pay','point'
);
CREATE TYPE payment_status AS ENUM (
    'pending','completed','failed','refunded'
);
CREATE TYPE shipping_status AS ENUM (
    'preparing','shipped','in_transit','delivered','returned'
);
CREATE TYPE customer_grade AS ENUM (
    'BRONZE','SILVER','GOLD','VIP'
);
CREATE TYPE gender_type AS ENUM ('M','F');
CREATE TYPE coupon_type AS ENUM ('percent','fixed');
CREATE TYPE return_type AS ENUM ('refund','exchange');
CREATE TYPE return_reason AS ENUM (
    'defective','wrong_item','change_of_mind','damaged_in_transit',
    'not_as_described','late_delivery'
);
CREATE TYPE return_status AS ENUM (
    'requested','pickup_scheduled','in_transit','completed'
);
CREATE TYPE refund_status AS ENUM (
    'pending','refunded','exchanged','partial_refund'
);
CREATE TYPE inspection_result AS ENUM (
    'good','opened_good','defective','unsellable'
);
CREATE TYPE image_type AS ENUM (
    'main','angle','side','back','detail','package','lifestyle','accessory','size_comparison'
);
CREATE TYPE referrer_source AS ENUM (
    'direct','search','ad','recommendation','social','email'
);
CREATE TYPE device_type AS ENUM (
    'desktop','mobile','tablet'
);
CREATE TYPE staff_role AS ENUM ('admin','manager','staff');
CREATE TYPE complaint_category AS ENUM (
    'product_defect','delivery_issue','wrong_item','refund_request',
    'exchange_request','general_inquiry','price_inquiry'
);
CREATE TYPE complaint_channel AS ENUM (
    'website','phone','email','chat','kakao'
);
CREATE TYPE priority_level AS ENUM ('low','medium','high','urgent');
CREATE TYPE complaint_status AS ENUM ('open','resolved','closed');
CREATE TYPE complaint_type AS ENUM ('inquiry','claim','report');
CREATE TYPE compensation_type AS ENUM (
    'refund','exchange','partial_refund','point_compensation','none'
);
CREATE TYPE acquisition_channel AS ENUM (
    'organic','search_ad','social','referral','direct'
);
CREATE TYPE cart_status AS ENUM ('active','converted','abandoned');
CREATE TYPE inventory_type AS ENUM ('inbound','outbound','return','adjustment');
CREATE TYPE promo_type AS ENUM ('seasonal','flash','category');
CREATE TYPE change_reason_type AS ENUM (
    'regular','promotion','price_drop','cost_increase'
);
CREATE TYPE grade_change_reason AS ENUM (
    'signup','upgrade','downgrade','yearly_review'
);
CREATE TYPE tag_category AS ENUM ('feature','use_case','target','spec');

-- =============================================
-- Product categories (hierarchical)
-- =============================================
CREATE TABLE categories (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    parent_id       INT NULL REFERENCES categories(id),
    name            VARCHAR(100) NOT NULL,
    slug            VARCHAR(100) NOT NULL UNIQUE,
    depth           INT NOT NULL DEFAULT 0,
    sort_order      INT NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Suppliers
-- =============================================
CREATE TABLE suppliers (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_name    VARCHAR(200) NOT NULL,
    business_number VARCHAR(20) NOT NULL,
    contact_name    VARCHAR(100) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    email           VARCHAR(200) NOT NULL,
    address         VARCHAR(500) NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Products
-- =============================================
CREATE TABLE products (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id     INT NOT NULL REFERENCES categories(id),
    supplier_id     INT NOT NULL REFERENCES suppliers(id),
    successor_id    INT NULL REFERENCES products(id),
    name            VARCHAR(500) NOT NULL,
    sku             VARCHAR(50) NOT NULL UNIQUE,
    brand           VARCHAR(100) NOT NULL,
    model_number    VARCHAR(50) NULL,
    description     TEXT NULL,
    specs           JSONB NULL,
    price           NUMERIC(12,2) NOT NULL CHECK (price >= 0),
    cost_price      NUMERIC(12,2) NOT NULL CHECK (cost_price >= 0),
    stock_qty       INT NOT NULL DEFAULT 0,
    weight_grams    INT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    discontinued_at TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Product images
-- =============================================
CREATE TABLE product_images (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      INT NOT NULL REFERENCES products(id),
    image_url       VARCHAR(500) NOT NULL,
    file_name       VARCHAR(200) NOT NULL,
    image_type      image_type NOT NULL,
    alt_text        VARCHAR(500) NULL,
    width           INT NULL,
    height          INT NULL,
    file_size       INT NULL,
    sort_order      INT NOT NULL DEFAULT 1,
    is_primary      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Product price history
-- =============================================
CREATE TABLE product_prices (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      INT NOT NULL REFERENCES products(id),
    price           NUMERIC(12,2) NOT NULL,
    started_at      TIMESTAMP NOT NULL,
    ended_at        TIMESTAMP NULL,
    change_reason   change_reason_type NULL
);

-- =============================================
-- Customers
-- =============================================
CREATE TABLE customers (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email           VARCHAR(200) NOT NULL UNIQUE,
    password_hash   VARCHAR(64) NOT NULL,
    name            VARCHAR(100) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    birth_date      DATE NULL,
    gender          gender_type NULL,
    grade           customer_grade NOT NULL DEFAULT 'BRONZE',
    point_balance   INT NOT NULL DEFAULT 0 CHECK (point_balance >= 0),
    acquisition_channel acquisition_channel NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at   TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Customer addresses
-- =============================================
CREATE TABLE customer_addresses (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     INT NOT NULL REFERENCES customers(id),
    label           VARCHAR(50) NOT NULL,
    recipient_name  VARCHAR(100) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    zip_code        VARCHAR(10) NOT NULL,
    address1        VARCHAR(300) NOT NULL,
    address2        VARCHAR(300) NULL,
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NULL
);

-- =============================================
-- Staff
-- =============================================
CREATE TABLE staff (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    manager_id      INT NULL REFERENCES staff(id),
    email           VARCHAR(200) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    department      VARCHAR(50) NOT NULL,
    role            staff_role NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    hired_at        TIMESTAMP NOT NULL,
    created_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Orders (partitioned by year on ordered_at)
-- =============================================
CREATE TABLE orders (
    id              INT GENERATED ALWAYS AS IDENTITY,
    order_number    VARCHAR(30) NOT NULL UNIQUE,
    customer_id     INT NOT NULL,
    address_id      INT NOT NULL,
    staff_id        INT NULL,
    status          order_status NOT NULL,
    total_amount    NUMERIC(12,2) NOT NULL,
    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    shipping_fee    NUMERIC(12,2) NOT NULL DEFAULT 0,
    point_used      INT NOT NULL DEFAULT 0,
    point_earned    INT NOT NULL DEFAULT 0,
    notes           TEXT NULL,
    ordered_at      TIMESTAMP NOT NULL,
    completed_at    TIMESTAMP NULL,
    cancelled_at    TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL,
    PRIMARY KEY (id, ordered_at)
) PARTITION BY RANGE (ordered_at);

CREATE TABLE orders_2015 PARTITION OF orders
    FOR VALUES FROM ('2015-01-01') TO ('2016-01-01');
CREATE TABLE orders_2016 PARTITION OF orders
    FOR VALUES FROM ('2016-01-01') TO ('2017-01-01');
CREATE TABLE orders_2017 PARTITION OF orders
    FOR VALUES FROM ('2017-01-01') TO ('2018-01-01');
CREATE TABLE orders_2018 PARTITION OF orders
    FOR VALUES FROM ('2018-01-01') TO ('2019-01-01');
CREATE TABLE orders_2019 PARTITION OF orders
    FOR VALUES FROM ('2019-01-01') TO ('2020-01-01');
CREATE TABLE orders_2020 PARTITION OF orders
    FOR VALUES FROM ('2020-01-01') TO ('2021-01-01');
CREATE TABLE orders_2021 PARTITION OF orders
    FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
CREATE TABLE orders_2022 PARTITION OF orders
    FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');
CREATE TABLE orders_2023 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE orders_2025 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE orders_default PARTITION OF orders DEFAULT;

CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_orders_status ON orders (status);
CREATE INDEX idx_orders_ordered_at ON orders (ordered_at);

-- =============================================
-- Order items
-- =============================================
CREATE TABLE order_items (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        INT NOT NULL,
    product_id      INT NOT NULL REFERENCES products(id),
    quantity        INT NOT NULL CHECK (quantity > 0),
    unit_price      NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    subtotal        NUMERIC(12,2) NOT NULL
);

CREATE INDEX idx_order_items_order ON order_items (order_id);
CREATE INDEX idx_order_items_product ON order_items (product_id);

-- =============================================
-- Payments
-- =============================================
CREATE TABLE payments (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        INT NOT NULL,
    method          payment_method NOT NULL,
    amount          NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    status          payment_status NOT NULL,
    pg_transaction_id VARCHAR(100) NULL,
    card_issuer     VARCHAR(50) NULL,
    card_approval_no VARCHAR(20) NULL,
    installment_months INT NULL,
    bank_name       VARCHAR(50) NULL,
    account_no      VARCHAR(50) NULL,
    depositor_name  VARCHAR(100) NULL,
    easy_pay_method VARCHAR(50) NULL,
    receipt_type    VARCHAR(20) NULL,
    receipt_no      VARCHAR(50) NULL,
    paid_at         TIMESTAMP NULL,
    refunded_at     TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL
);

CREATE INDEX idx_payments_order ON payments (order_id);

-- =============================================
-- Shipping
-- =============================================
CREATE TABLE shipping (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        INT NOT NULL,
    carrier         VARCHAR(50) NOT NULL,
    tracking_number VARCHAR(50) NULL,
    status          shipping_status NOT NULL,
    shipped_at      TIMESTAMP NULL,
    delivered_at    TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

CREATE INDEX idx_shipping_order ON shipping (order_id);

-- =============================================
-- Reviews
-- =============================================
CREATE TABLE reviews (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      INT NOT NULL REFERENCES products(id),
    customer_id     INT NOT NULL REFERENCES customers(id),
    order_id        INT NOT NULL,
    rating          SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title           VARCHAR(200) NULL,
    content         TEXT NULL,
    is_verified     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

CREATE INDEX idx_reviews_product ON reviews (product_id);
CREATE INDEX idx_reviews_customer ON reviews (customer_id);

-- =============================================
-- Inventory transactions
-- =============================================
CREATE TABLE inventory_transactions (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      INT NOT NULL REFERENCES products(id),
    type            inventory_type NOT NULL,
    quantity        INT NOT NULL,
    reference_id    INT NULL,
    notes           VARCHAR(500) NULL,
    created_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Carts
-- =============================================
CREATE TABLE carts (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     INT NOT NULL REFERENCES customers(id),
    status          cart_status NOT NULL DEFAULT 'active',
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Cart items
-- =============================================
CREATE TABLE cart_items (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cart_id         INT NOT NULL REFERENCES carts(id),
    product_id      INT NOT NULL REFERENCES products(id),
    quantity        INT NOT NULL DEFAULT 1,
    added_at        TIMESTAMP NOT NULL
);

-- =============================================
-- Coupons
-- =============================================
CREATE TABLE coupons (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            VARCHAR(30) NOT NULL UNIQUE,
    name            VARCHAR(200) NOT NULL,
    type            coupon_type NOT NULL,
    discount_value  NUMERIC(12,2) NOT NULL CHECK (discount_value > 0),
    min_order_amount NUMERIC(12,2) NULL,
    max_discount    NUMERIC(12,2) NULL,
    usage_limit     INT NULL,
    per_user_limit  INT NOT NULL DEFAULT 1,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    started_at      TIMESTAMP NOT NULL,
    expired_at      TIMESTAMP NOT NULL,
    created_at      TIMESTAMP NOT NULL
);

-- =============================================
-- Coupon usage
-- =============================================
CREATE TABLE coupon_usage (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    coupon_id       INT NOT NULL REFERENCES coupons(id),
    customer_id     INT NOT NULL REFERENCES customers(id),
    order_id        INT NOT NULL,
    discount_amount NUMERIC(12,2) NOT NULL,
    used_at         TIMESTAMP NOT NULL
);

-- =============================================
-- Complaints
-- =============================================
CREATE TABLE complaints (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        INT NULL,
    customer_id     INT NOT NULL REFERENCES customers(id),
    staff_id        INT NULL REFERENCES staff(id),
    category        complaint_category NOT NULL,
    channel         complaint_channel NOT NULL,
    priority        priority_level NOT NULL,
    status          complaint_status NOT NULL,
    title           VARCHAR(300) NOT NULL,
    content         TEXT NOT NULL,
    resolution      TEXT NULL,
    type            complaint_type NOT NULL DEFAULT 'inquiry',
    sub_category    VARCHAR(100) NULL,
    compensation_type compensation_type NULL,
    compensation_amount NUMERIC(12,2) NULL DEFAULT 0,
    escalated       BOOLEAN NOT NULL DEFAULT FALSE,
    response_count  INT NOT NULL DEFAULT 1,
    created_at      TIMESTAMP NOT NULL,
    resolved_at     TIMESTAMP NULL,
    closed_at       TIMESTAMP NULL
);

CREATE INDEX idx_complaints_customer ON complaints (customer_id);
CREATE INDEX idx_complaints_status ON complaints (status);

-- =============================================
-- Returns/exchanges
-- =============================================
CREATE TABLE returns (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        INT NOT NULL,
    customer_id     INT NOT NULL REFERENCES customers(id),
    return_type     return_type NOT NULL,
    reason          return_reason NOT NULL,
    reason_detail   TEXT NOT NULL,
    status          return_status NOT NULL,
    is_partial      BOOLEAN NOT NULL DEFAULT FALSE,
    refund_amount   NUMERIC(12,2) NOT NULL,
    refund_status   refund_status NOT NULL,
    carrier         VARCHAR(50) NOT NULL,
    tracking_number VARCHAR(50) NOT NULL,
    requested_at    TIMESTAMP NOT NULL,
    pickup_at       TIMESTAMP NOT NULL,
    received_at     TIMESTAMP NULL,
    inspected_at    TIMESTAMP NULL,
    inspection_result inspection_result NULL,
    completed_at    TIMESTAMP NULL,
    claim_id        INT NULL REFERENCES complaints(id),
    exchange_product_id INT NULL REFERENCES products(id),
    restocking_fee  NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_at      TIMESTAMP NOT NULL
);

CREATE INDEX idx_returns_order ON returns (order_id);
CREATE INDEX idx_returns_customer ON returns (customer_id);

-- =============================================
-- Wishlists
-- =============================================
CREATE TABLE wishlists (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     INT NOT NULL REFERENCES customers(id),
    product_id      INT NOT NULL REFERENCES products(id),
    is_purchased    BOOLEAN NOT NULL DEFAULT FALSE,
    notify_on_sale  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL,
    UNIQUE (customer_id, product_id)
);

-- =============================================
-- Calendar dimension
-- =============================================
CREATE TABLE calendar (
    date_key        DATE NOT NULL PRIMARY KEY,
    year            INT NOT NULL,
    month           INT NOT NULL,
    day             INT NOT NULL,
    quarter         INT NOT NULL,
    day_of_week     INT NOT NULL,
    day_name        VARCHAR(20) NOT NULL,
    is_weekend      BOOLEAN NOT NULL DEFAULT FALSE,
    is_holiday      BOOLEAN NOT NULL DEFAULT FALSE,
    holiday_name    VARCHAR(100) NULL
);

CREATE INDEX idx_calendar_year_month ON calendar (year, month);

-- =============================================
-- Customer grade history
-- =============================================
CREATE TABLE customer_grade_history (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     INT NOT NULL REFERENCES customers(id),
    old_grade       customer_grade NULL,
    new_grade       customer_grade NOT NULL,
    changed_at      TIMESTAMP NOT NULL,
    reason          grade_change_reason NOT NULL
);

CREATE INDEX idx_grade_history_customer ON customer_grade_history (customer_id);

-- =============================================
-- Tags
-- =============================================
CREATE TABLE tags (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    category        tag_category NOT NULL
);

CREATE TABLE product_tags (
    product_id      INT NOT NULL REFERENCES products(id),
    tag_id          INT NOT NULL REFERENCES tags(id),
    PRIMARY KEY (product_id, tag_id)
);

-- =============================================
-- Product views (partitioned by year)
-- =============================================
CREATE TABLE product_views (
    id              INT GENERATED ALWAYS AS IDENTITY,
    customer_id     INT NOT NULL,
    product_id      INT NOT NULL,
    referrer_source referrer_source NOT NULL,
    device_type     device_type NOT NULL,
    duration_seconds INT NOT NULL,
    viewed_at       TIMESTAMP NOT NULL,
    PRIMARY KEY (id, viewed_at)
) PARTITION BY RANGE (viewed_at);

CREATE TABLE product_views_2015 PARTITION OF product_views
    FOR VALUES FROM ('2015-01-01') TO ('2016-01-01');
CREATE TABLE product_views_2016 PARTITION OF product_views
    FOR VALUES FROM ('2016-01-01') TO ('2017-01-01');
CREATE TABLE product_views_2017 PARTITION OF product_views
    FOR VALUES FROM ('2017-01-01') TO ('2018-01-01');
CREATE TABLE product_views_2018 PARTITION OF product_views
    FOR VALUES FROM ('2018-01-01') TO ('2019-01-01');
CREATE TABLE product_views_2019 PARTITION OF product_views
    FOR VALUES FROM ('2019-01-01') TO ('2020-01-01');
CREATE TABLE product_views_2020 PARTITION OF product_views
    FOR VALUES FROM ('2020-01-01') TO ('2021-01-01');
CREATE TABLE product_views_2021 PARTITION OF product_views
    FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
CREATE TABLE product_views_2022 PARTITION OF product_views
    FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');
CREATE TABLE product_views_2023 PARTITION OF product_views
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
CREATE TABLE product_views_2024 PARTITION OF product_views
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE product_views_2025 PARTITION OF product_views
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE product_views_default PARTITION OF product_views DEFAULT;

CREATE INDEX idx_views_customer ON product_views (customer_id);
CREATE INDEX idx_views_product ON product_views (product_id);
CREATE INDEX idx_views_viewed_at ON product_views (viewed_at);

-- =============================================
-- Point transactions
-- =============================================
CREATE TABLE point_transactions (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     INT NOT NULL REFERENCES customers(id),
    order_id        INT NULL,
    type            VARCHAR(10) NOT NULL CHECK (type IN ('earn','use','expire')),
    reason          VARCHAR(20) NOT NULL CHECK (reason IN ('purchase','confirm','review','signup','use','expiry')),
    amount          INT NOT NULL,
    balance_after   INT NOT NULL,
    expires_at      TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL
);

CREATE INDEX idx_point_tx_customer ON point_transactions (customer_id);
CREATE INDEX idx_point_tx_type ON point_transactions (type);

-- =============================================
-- Promotions
-- =============================================
CREATE TABLE promotions (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    type            promo_type NOT NULL,
    discount_type   coupon_type NOT NULL,
    discount_value  NUMERIC(12,2) NOT NULL,
    min_order_amount NUMERIC(12,2) NULL,
    started_at      TIMESTAMP NOT NULL,
    ended_at        TIMESTAMP NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL
);

CREATE TABLE promotion_products (
    promotion_id    INT NOT NULL REFERENCES promotions(id),
    product_id      INT NOT NULL REFERENCES products(id),
    override_price  NUMERIC(12,2) NULL,
    PRIMARY KEY (promotion_id, product_id)
);

-- =============================================
-- Product Q&A
-- =============================================
CREATE TABLE product_qna (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id      INT NOT NULL REFERENCES products(id),
    customer_id     INT NULL REFERENCES customers(id),
    staff_id        INT NULL REFERENCES staff(id),
    parent_id       INT NULL REFERENCES product_qna(id),
    content         TEXT NOT NULL,
    is_answered     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL
);

CREATE INDEX idx_qna_product ON product_qna (product_id);

-- =============================================
-- Materialized views
-- =============================================

-- Monthly sales summary
CREATE MATERIALIZED VIEW mv_monthly_sales AS
SELECT
    date_trunc('month', o.ordered_at)::DATE AS month,
    COUNT(DISTINCT o.id) AS order_count,
    COUNT(DISTINCT o.customer_id) AS customer_count,
    SUM(o.total_amount)::BIGINT AS revenue,
    AVG(o.total_amount)::INT AS avg_order,
    SUM(o.discount_amount)::BIGINT AS total_discount
FROM orders o
WHERE o.status != 'cancelled'
GROUP BY date_trunc('month', o.ordered_at)
ORDER BY month;

CREATE UNIQUE INDEX idx_mv_monthly_sales_month ON mv_monthly_sales (month);

-- Product performance summary
CREATE MATERIALIZED VIEW mv_product_performance AS
SELECT
    p.id AS product_id,
    p.name,
    p.brand,
    p.sku,
    c.name AS category,
    p.price,
    p.cost_price,
    ROUND((p.price - p.cost_price) / NULLIF(p.price, 0) * 100, 1) AS margin_pct,
    p.stock_qty,
    p.is_active,
    COALESCE(s.total_sold, 0) AS total_sold,
    COALESCE(s.total_revenue, 0)::BIGINT AS total_revenue,
    COALESCE(s.order_count, 0) AS order_count,
    COALESCE(rv.review_count, 0) AS review_count,
    COALESCE(rv.avg_rating, 0) AS avg_rating,
    COALESCE(rt.return_count, 0) AS return_count
FROM products p
JOIN categories c ON p.category_id = c.id
LEFT JOIN (
    SELECT oi.product_id,
           SUM(oi.quantity) AS total_sold,
           SUM(oi.subtotal)::BIGINT AS total_revenue,
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
    SELECT oi.product_id, COUNT(DISTINCT r.id) AS return_count
    FROM returns r
    JOIN order_items oi ON r.order_id = oi.order_id
    GROUP BY oi.product_id
) rt ON p.id = rt.product_id;

CREATE UNIQUE INDEX idx_mv_product_perf_id ON mv_product_performance (product_id);

-- =============================================
-- Access control examples (commented out)
-- =============================================
-- CREATE ROLE reader LOGIN PASSWORD 'readonly_password';
-- CREATE ROLE admin_user LOGIN PASSWORD 'admin_password';
-- GRANT CONNECT ON DATABASE ecommerce TO reader;
-- GRANT USAGE ON SCHEMA public TO reader;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO reader;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_user;
-- REVOKE DROP ON SCHEMA public FROM reader;
"""


PROCEDURES_SQL = """\
-- =============================================
-- E-commerce Stored Procedures - PostgreSQL (PL/pgSQL)
-- =============================================

-- =============================================
-- sp_place_order: Create a new order and deduct customer points
-- =============================================
CREATE OR REPLACE FUNCTION sp_place_order(
    p_customer_id INT,
    p_address_id INT
) RETURNS TABLE (
    order_id INT,
    order_number VARCHAR,
    total_amount NUMERIC
) AS $$
DECLARE
    v_order_id INT;
    v_total NUMERIC(12,2) := 0;
    v_points INT := 0;
    v_order_number VARCHAR(30);
    v_now TIMESTAMP := NOW();
BEGIN
    -- Generate order number
    v_order_number := 'ORD-' || to_char(v_now, 'YYYYMMDD') || '-' ||
        LPAD((SELECT COALESCE(MAX(o.id), 0) + 1 FROM orders o)::TEXT, 5, '0');

    -- Calculate cart total
    SELECT COALESCE(SUM(p.price * ci.quantity), 0)
    INTO v_total
    FROM carts c
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.customer_id = p_customer_id AND c.status = 'active';

    IF v_total = 0 THEN
        RAISE EXCEPTION 'Cart is empty';
    END IF;

    -- Get customer point balance (with row lock)
    SELECT cu.point_balance INTO v_points
    FROM customers cu WHERE cu.id = p_customer_id FOR UPDATE;

    -- Create order
    INSERT INTO orders (order_number, customer_id, address_id, status,
                        total_amount, discount_amount, shipping_fee,
                        point_used, point_earned, ordered_at, created_at, updated_at)
    VALUES (v_order_number, p_customer_id, p_address_id, 'pending',
            v_total, 0, CASE WHEN v_total >= 50000 THEN 0 ELSE 3000 END,
            0, FLOOR(v_total * 0.01)::INT, v_now, v_now, v_now)
    RETURNING orders.id INTO v_order_id;

    -- Move cart items to order items
    INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_amount, subtotal)
    SELECT v_order_id, ci.product_id, ci.quantity, p.price, 0, p.price * ci.quantity
    FROM carts c
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.customer_id = p_customer_id AND c.status = 'active';

    -- Mark cart as converted
    UPDATE carts SET status = 'converted', updated_at = v_now
    WHERE customer_id = p_customer_id AND status = 'active';

    RETURN QUERY SELECT v_order_id, v_order_number, v_total;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- sp_expire_points: Expire points older than 1 year
-- =============================================
CREATE OR REPLACE FUNCTION sp_expire_points()
RETURNS INT AS $$
DECLARE
    v_now TIMESTAMP := NOW();
    v_expired_count INT := 0;
BEGIN
    -- Insert expiry records for earn transactions past their expiry date
    WITH expired AS (
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
          )
        RETURNING customer_id, amount
    )
    SELECT COUNT(*) INTO v_expired_count FROM expired;

    -- Update customer balances
    UPDATE customers c
    SET point_balance = GREATEST(0, c.point_balance - COALESCE(exp.total_expired, 0))
    FROM (
        SELECT pt.customer_id, SUM(pt.amount) AS total_expired
        FROM point_transactions pt
        WHERE pt.type = 'earn'
          AND pt.expires_at IS NOT NULL
          AND pt.expires_at < v_now
        GROUP BY pt.customer_id
    ) exp
    WHERE c.id = exp.customer_id AND c.point_balance > 0;

    RETURN v_expired_count;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- sp_monthly_settlement: Monthly sales summary report
-- =============================================
CREATE OR REPLACE FUNCTION sp_monthly_settlement(
    p_year INT,
    p_month INT
) RETURNS TABLE (
    total_orders BIGINT,
    unique_customers BIGINT,
    gross_revenue NUMERIC,
    total_discounts NUMERIC,
    total_shipping NUMERIC,
    cancelled_orders BIGINT,
    returned_orders BIGINT,
    avg_order_value NUMERIC
) AS $$
DECLARE
    v_start_date TIMESTAMP;
    v_end_date TIMESTAMP;
BEGIN
    v_start_date := make_timestamp(p_year, p_month, 1, 0, 0, 0);
    v_end_date := v_start_date + INTERVAL '1 month';

    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT AS total_orders,
        COUNT(DISTINCT o.customer_id)::BIGINT AS unique_customers,
        SUM(CASE WHEN o.status != 'cancelled' THEN o.total_amount ELSE 0 END) AS gross_revenue,
        SUM(o.discount_amount) AS total_discounts,
        SUM(o.shipping_fee) AS total_shipping,
        SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END)::BIGINT AS cancelled_orders,
        SUM(CASE WHEN o.status IN ('return_requested','returned') THEN 1 ELSE 0 END)::BIGINT AS returned_orders,
        ROUND(AVG(CASE WHEN o.status != 'cancelled' THEN o.total_amount END), 0) AS avg_order_value
    FROM orders o
    WHERE o.ordered_at >= v_start_date AND o.ordered_at < v_end_date;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- Refresh materialized views (call periodically)
-- =============================================
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_sales;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_product_performance;
END;
$$ LANGUAGE plpgsql;
"""


# Columns that are boolean in PG (stored as 0/1 integers in the data dicts)
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

# Columns that need DATE type (not TIMESTAMP)
_DATE_COLUMNS = {
    "customers.birth_date",
    "calendar.date_key",
}

# Tables using GENERATED ALWAYS AS IDENTITY - must override id insert
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

# JSON columns stored as JSONB
_JSON_COLUMNS = {
    "products.specs",
}


class PostgreSQLExporter:
    """Export generated data to PostgreSQL-compatible SQL files."""

    def __init__(self, output_dir: str):
        self.output_dir = os.path.join(output_dir, "postgresql")
        os.makedirs(self.output_dir, exist_ok=True)

    def export(self, data: dict[str, list[dict]]) -> str:
        """Export all data to PostgreSQL SQL files."""
        schema_path = os.path.join(self.output_dir, "schema.sql")
        data_path = os.path.join(self.output_dir, "data.sql")
        proc_path = os.path.join(self.output_dir, "procedures.sql")

        # Write schema DDL
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write(SCHEMA_SQL)

        # Write data
        with open(data_path, "w", encoding="utf-8") as f:
            f.write("-- =============================================\n")
            f.write("-- E-commerce Test Data - PostgreSQL\n")
            f.write("-- =============================================\n\n")
            f.write("SET client_encoding = 'UTF8';\n\n")

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

            # Reset sequences for identity columns
            f.write("\n-- Reset identity sequences\n")
            for table in table_order:
                rows = data.get(table, [])
                if not rows or table not in _IDENTITY_TABLES:
                    continue
                max_id = max(r.get("id", 0) for r in rows)
                f.write(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), {max_id});\n")

            # Refresh materialized views
            f.write("\n-- Refresh materialized views after data load\n")
            f.write("REFRESH MATERIALIZED VIEW mv_monthly_sales;\n")
            f.write("REFRESH MATERIALIZED VIEW mv_product_performance;\n")

        # Write stored procedures
        with open(proc_path, "w", encoding="utf-8") as f:
            f.write(PROCEDURES_SQL)

        return self.output_dir

    def _write_inserts(self, f, table: str, rows: list[dict]):
        """Write INSERT statements with OVERRIDING SYSTEM VALUE for identity columns."""
        if not rows:
            return

        columns = list(rows[0].keys())
        col_names = ", ".join(f'"{c}"' for c in columns)
        batch_size = 1000
        use_overriding = table in _IDENTITY_TABLES

        f.write(f"-- {table}: {len(rows)} rows\n")

        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            if use_overriding:
                f.write(f'INSERT INTO "{table}" ({col_names}) OVERRIDING SYSTEM VALUE VALUES\n')
            else:
                f.write(f'INSERT INTO "{table}" ({col_names}) VALUES\n')

            value_lines = []
            for row in batch:
                vals = []
                for col in columns:
                    v = row[col]
                    vals.append(self._format_value(table, col, v))
                value_lines.append(f"({', '.join(vals)})")

            f.write(",\n".join(value_lines))
            f.write(";\n\n")

    def _format_value(self, table: str, column: str, value: Any) -> str:
        """Format a Python value as a PostgreSQL literal."""
        if value is None:
            return "NULL"

        key = f"{table}.{column}"

        if key in _BOOL_COLUMNS:
            return "TRUE" if value else "FALSE"

        if key in _JSON_COLUMNS:
            # JSON string -> cast to jsonb
            s = str(value).replace("'", "''")
            return f"'{s}'::jsonb"

        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"

        if isinstance(value, (int, float)):
            return str(value)

        # String value - escape for PostgreSQL (double single quotes)
        s = str(value)
        # Use dollar-quoting if string contains both single quotes and backslashes
        if "'" in s:
            s = s.replace("'", "''")
        return f"'{s}'"
