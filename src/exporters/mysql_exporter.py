"""MySQL database exporter

Generates DDL, INSERT data, and stored procedures for MySQL 8.0+.
"""

from __future__ import annotations

import os
from typing import Any


SCHEMA_SQL = """\
-- =============================================
-- E-commerce Test Database - MySQL 8.0+
-- =============================================

CREATE DATABASE IF NOT EXISTS ecommerce
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE ecommerce;

-- =============================================
-- Product categories (hierarchical: top > mid > sub)
-- =============================================
CREATE TABLE categories (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    parent_id       INT NULL,
    name            VARCHAR(100) NOT NULL,
    slug            VARCHAR(100) NOT NULL UNIQUE,
    depth           INT NOT NULL DEFAULT 0,
    sort_order      INT NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME NOT NULL,
    CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Suppliers
-- =============================================
CREATE TABLE suppliers (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    company_name    VARCHAR(200) NOT NULL,
    business_number VARCHAR(20) NOT NULL,
    contact_name    VARCHAR(100) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    email           VARCHAR(200) NOT NULL,
    address         VARCHAR(500) NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Products
-- =============================================
CREATE TABLE products (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    category_id     INT NOT NULL,
    supplier_id     INT NOT NULL,
    successor_id    INT NULL,
    name            VARCHAR(500) NOT NULL,
    sku             VARCHAR(50) NOT NULL UNIQUE,
    brand           VARCHAR(100) NOT NULL,
    model_number    VARCHAR(50) NULL,
    description     TEXT NULL,
    specs           JSON NULL COMMENT 'JSON product specifications',
    price           DECIMAL(12,2) NOT NULL CHECK (price >= 0),
    cost_price      DECIMAL(12,2) NOT NULL CHECK (cost_price >= 0),
    stock_qty       INT NOT NULL DEFAULT 0,
    weight_grams    INT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    discontinued_at DATETIME NULL,
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME NOT NULL,
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id),
    CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    CONSTRAINT fk_products_successor FOREIGN KEY (successor_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Product images (1-5 per product)
-- =============================================
CREATE TABLE product_images (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    product_id      INT NOT NULL,
    image_url       VARCHAR(500) NOT NULL,
    file_name       VARCHAR(200) NOT NULL,
    image_type      ENUM('main','angle','side','back','detail','package','lifestyle','accessory','size_comparison') NOT NULL,
    alt_text        VARCHAR(500) NULL,
    width           INT NULL,
    height          INT NULL,
    file_size       INT NULL,
    sort_order      INT NOT NULL DEFAULT 1,
    is_primary      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      DATETIME NOT NULL,
    CONSTRAINT fk_product_images_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Product price history
-- =============================================
CREATE TABLE product_prices (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    product_id      INT NOT NULL,
    price           DECIMAL(12,2) NOT NULL,
    started_at      DATETIME NOT NULL,
    ended_at        DATETIME NULL,
    change_reason   ENUM('regular','promotion','price_drop','cost_increase') NULL,
    CONSTRAINT fk_product_prices_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Customers
-- =============================================
CREATE TABLE customers (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email           VARCHAR(200) NOT NULL UNIQUE,
    password_hash   VARCHAR(64) NOT NULL,
    name            VARCHAR(100) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    birth_date      DATE NULL,
    gender          ENUM('M','F') NULL,
    grade           ENUM('BRONZE','SILVER','GOLD','VIP') NOT NULL DEFAULT 'BRONZE',
    point_balance   INT NOT NULL DEFAULT 0 CHECK (point_balance >= 0),
    acquisition_channel ENUM('organic','search_ad','social','referral','direct') NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at   DATETIME NULL,
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Customer addresses (1-3 per customer)
-- =============================================
CREATE TABLE customer_addresses (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT NOT NULL,
    label           VARCHAR(50) NOT NULL,
    recipient_name  VARCHAR(100) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    zip_code        VARCHAR(10) NOT NULL,
    address1        VARCHAR(300) NOT NULL,
    address2        VARCHAR(300) NULL,
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME NULL,
    CONSTRAINT fk_customer_addresses_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Staff
-- =============================================
CREATE TABLE staff (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    manager_id      INT NULL,
    email           VARCHAR(200) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    department      VARCHAR(50) NOT NULL,
    role            ENUM('admin','manager','staff') NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    hired_at        DATETIME NOT NULL,
    created_at      DATETIME NOT NULL,
    CONSTRAINT fk_staff_manager FOREIGN KEY (manager_id) REFERENCES staff(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Orders (partitioned by year)
-- =============================================
CREATE TABLE orders (
    id              INT NOT NULL AUTO_INCREMENT,
    order_number    VARCHAR(30) NOT NULL,
    customer_id     INT NOT NULL,
    address_id      INT NOT NULL,
    staff_id        INT NULL,
    status          ENUM('pending','paid','preparing','shipped','delivered','confirmed','cancelled','return_requested','returned') NOT NULL,
    total_amount    DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    shipping_fee    DECIMAL(12,2) NOT NULL DEFAULT 0,
    point_used      INT NOT NULL DEFAULT 0,
    point_earned    INT NOT NULL DEFAULT 0,
    notes           TEXT NULL,
    ordered_at      DATETIME NOT NULL,
    completed_at    DATETIME NULL,
    cancelled_at    DATETIME NULL,
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME NOT NULL,
    PRIMARY KEY (id, ordered_at),
    UNIQUE KEY uq_order_number (order_number, ordered_at),
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_ordered_at (ordered_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY RANGE (YEAR(ordered_at)) (
    PARTITION p2015 VALUES LESS THAN (2016),
    PARTITION p2016 VALUES LESS THAN (2017),
    PARTITION p2017 VALUES LESS THAN (2018),
    PARTITION p2018 VALUES LESS THAN (2019),
    PARTITION p2019 VALUES LESS THAN (2020),
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);

-- =============================================
-- Order items (1-5 items per order)
-- =============================================
CREATE TABLE order_items (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL,
    product_id      INT NOT NULL,
    quantity        INT NOT NULL CHECK (quantity > 0),
    unit_price      DECIMAL(12,2) NOT NULL CHECK (unit_price >= 0),
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    subtotal        DECIMAL(12,2) NOT NULL,
    INDEX idx_order_items_order (order_id),
    INDEX idx_order_items_product (product_id),
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Payments
-- =============================================
CREATE TABLE payments (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL,
    method          ENUM('card','bank_transfer','virtual_account','kakao_pay','naver_pay','point') NOT NULL,
    amount          DECIMAL(12,2) NOT NULL CHECK (amount >= 0),
    status          ENUM('pending','completed','failed','refunded') NOT NULL,
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
    paid_at         DATETIME NULL,
    refunded_at     DATETIME NULL,
    created_at      DATETIME NOT NULL,
    INDEX idx_payments_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Shipping
-- =============================================
CREATE TABLE shipping (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL,
    carrier         VARCHAR(50) NOT NULL,
    tracking_number VARCHAR(50) NULL,
    status          ENUM('preparing','shipped','in_transit','delivered','returned') NOT NULL,
    shipped_at      DATETIME NULL,
    delivered_at    DATETIME NULL,
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME NOT NULL,
    INDEX idx_shipping_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Reviews
-- =============================================
CREATE TABLE reviews (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    product_id      INT NOT NULL,
    customer_id     INT NOT NULL,
    order_id        INT NOT NULL,
    rating          TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title           VARCHAR(200) NULL,
    content         TEXT NULL,
    is_verified     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME NOT NULL,
    INDEX idx_reviews_product (product_id),
    INDEX idx_reviews_customer (customer_id),
    CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_reviews_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Inventory transactions
-- =============================================
CREATE TABLE inventory_transactions (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    product_id      INT NOT NULL,
    type            ENUM('inbound','outbound','return','adjustment') NOT NULL,
    quantity        INT NOT NULL,
    reference_id    INT NULL,
    notes           VARCHAR(500) NULL,
    created_at      DATETIME NOT NULL,
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Carts
-- =============================================
CREATE TABLE carts (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT NOT NULL,
    status          ENUM('active','converted','abandoned') NOT NULL DEFAULT 'active',
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME NOT NULL,
    CONSTRAINT fk_carts_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Cart items
-- =============================================
CREATE TABLE cart_items (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    cart_id         INT NOT NULL,
    product_id      INT NOT NULL,
    quantity        INT NOT NULL DEFAULT 1,
    added_at        DATETIME NOT NULL,
    CONSTRAINT fk_cart_items_cart FOREIGN KEY (cart_id) REFERENCES carts(id),
    CONSTRAINT fk_cart_items_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Coupons
-- =============================================
CREATE TABLE coupons (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    code            VARCHAR(30) NOT NULL UNIQUE,
    name            VARCHAR(200) NOT NULL,
    type            ENUM('percent','fixed') NOT NULL,
    discount_value  DECIMAL(12,2) NOT NULL CHECK (discount_value > 0),
    min_order_amount DECIMAL(12,2) NULL,
    max_discount    DECIMAL(12,2) NULL,
    usage_limit     INT NULL,
    per_user_limit  INT NOT NULL DEFAULT 1,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    started_at      DATETIME NOT NULL,
    expired_at      DATETIME NOT NULL,
    created_at      DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Coupon usage
-- =============================================
CREATE TABLE coupon_usage (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    coupon_id       INT NOT NULL,
    customer_id     INT NOT NULL,
    order_id        INT NOT NULL,
    discount_amount DECIMAL(12,2) NOT NULL,
    used_at         DATETIME NOT NULL,
    CONSTRAINT fk_coupon_usage_coupon FOREIGN KEY (coupon_id) REFERENCES coupons(id),
    CONSTRAINT fk_coupon_usage_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Customer complaints
-- =============================================
CREATE TABLE complaints (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NULL,
    customer_id     INT NOT NULL,
    staff_id        INT NULL,
    category        ENUM('product_defect','delivery_issue','wrong_item','refund_request','exchange_request','general_inquiry','price_inquiry') NOT NULL,
    channel         ENUM('website','phone','email','chat','kakao') NOT NULL,
    priority        ENUM('low','medium','high','urgent') NOT NULL,
    status          ENUM('open','resolved','closed') NOT NULL,
    title           VARCHAR(300) NOT NULL,
    content         TEXT NOT NULL,
    resolution      TEXT NULL,
    type            ENUM('inquiry','claim','report') NOT NULL DEFAULT 'inquiry',
    sub_category    VARCHAR(100) NULL,
    compensation_type ENUM('refund','exchange','partial_refund','point_compensation','none') NULL,
    compensation_amount DECIMAL(12,2) NULL DEFAULT 0,
    escalated       BOOLEAN NOT NULL DEFAULT FALSE,
    response_count  INT NOT NULL DEFAULT 1,
    created_at      DATETIME NOT NULL,
    resolved_at     DATETIME NULL,
    closed_at       DATETIME NULL,
    INDEX idx_complaints_customer (customer_id),
    INDEX idx_complaints_status (status),
    CONSTRAINT fk_complaints_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_complaints_staff FOREIGN KEY (staff_id) REFERENCES staff(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Returns/exchanges
-- =============================================
CREATE TABLE returns (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL,
    customer_id     INT NOT NULL,
    return_type     ENUM('refund','exchange') NOT NULL,
    reason          ENUM('defective','wrong_item','change_of_mind','damaged_in_transit','not_as_described','late_delivery') NOT NULL,
    reason_detail   TEXT NOT NULL,
    status          ENUM('requested','pickup_scheduled','in_transit','completed') NOT NULL,
    is_partial      BOOLEAN NOT NULL DEFAULT FALSE,
    refund_amount   DECIMAL(12,2) NOT NULL,
    refund_status   ENUM('pending','refunded','exchanged','partial_refund') NOT NULL,
    carrier         VARCHAR(50) NOT NULL,
    tracking_number VARCHAR(50) NOT NULL,
    requested_at    DATETIME NOT NULL,
    pickup_at       DATETIME NOT NULL,
    received_at     DATETIME NULL,
    inspected_at    DATETIME NULL,
    inspection_result ENUM('good','opened_good','defective','unsellable') NULL,
    completed_at    DATETIME NULL,
    claim_id        INT NULL,
    exchange_product_id INT NULL,
    restocking_fee  DECIMAL(12,2) NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL,
    INDEX idx_returns_order (order_id),
    INDEX idx_returns_customer (customer_id),
    CONSTRAINT fk_returns_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_returns_claim FOREIGN KEY (claim_id) REFERENCES complaints(id),
    CONSTRAINT fk_returns_exchange_product FOREIGN KEY (exchange_product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Wishlists (M:N: customers <-> products)
-- =============================================
CREATE TABLE wishlists (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT NOT NULL,
    product_id      INT NOT NULL,
    is_purchased    BOOLEAN NOT NULL DEFAULT FALSE,
    notify_on_sale  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      DATETIME NOT NULL,
    UNIQUE KEY uq_wishlist (customer_id, product_id),
    CONSTRAINT fk_wishlists_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_wishlists_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Calendar dimension (for CROSS JOIN exercises)
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
    holiday_name    VARCHAR(100) NULL,
    INDEX idx_calendar_year_month (year, month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Customer grade history (SCD Type 2)
-- =============================================
CREATE TABLE customer_grade_history (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT NOT NULL,
    old_grade       ENUM('BRONZE','SILVER','GOLD','VIP') NULL,
    new_grade       ENUM('BRONZE','SILVER','GOLD','VIP') NOT NULL,
    changed_at      DATETIME NOT NULL,
    reason          ENUM('signup','upgrade','downgrade','yearly_review') NOT NULL,
    INDEX idx_grade_history_customer (customer_id),
    CONSTRAINT fk_grade_history_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Tags (M:N learning)
-- =============================================
CREATE TABLE tags (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    category        VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE product_tags (
    product_id      INT NOT NULL,
    tag_id          INT NOT NULL,
    PRIMARY KEY (product_id, tag_id),
    CONSTRAINT fk_product_tags_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_product_tags_tag FOREIGN KEY (tag_id) REFERENCES tags(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Product views (partitioned by year)
-- =============================================
CREATE TABLE product_views (
    id              INT NOT NULL AUTO_INCREMENT,
    customer_id     INT NOT NULL,
    product_id      INT NOT NULL,
    referrer_source ENUM('direct','search','ad','recommendation','social','email') NOT NULL,
    device_type     ENUM('desktop','mobile','tablet') NOT NULL,
    duration_seconds INT NOT NULL,
    viewed_at       DATETIME NOT NULL,
    PRIMARY KEY (id, viewed_at),
    INDEX idx_views_customer (customer_id),
    INDEX idx_views_product (product_id),
    INDEX idx_views_viewed_at (viewed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY RANGE (YEAR(viewed_at)) (
    PARTITION p2015 VALUES LESS THAN (2016),
    PARTITION p2016 VALUES LESS THAN (2017),
    PARTITION p2017 VALUES LESS THAN (2018),
    PARTITION p2018 VALUES LESS THAN (2019),
    PARTITION p2019 VALUES LESS THAN (2020),
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);

-- =============================================
-- Point transactions
-- =============================================
CREATE TABLE point_transactions (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT NOT NULL,
    order_id        INT NULL,
    type            ENUM('earn','use','expire') NOT NULL,
    reason          ENUM('purchase','confirm','review','signup','use','expiry') NOT NULL,
    amount          INT NOT NULL,
    balance_after   INT NOT NULL,
    expires_at      DATETIME NULL,
    created_at      DATETIME NOT NULL,
    INDEX idx_point_tx_customer (customer_id),
    INDEX idx_point_tx_type (type),
    CONSTRAINT fk_point_tx_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Promotions
-- =============================================
CREATE TABLE promotions (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    type            ENUM('seasonal','flash','category') NOT NULL,
    discount_type   ENUM('percent','fixed') NOT NULL,
    discount_value  DECIMAL(12,2) NOT NULL,
    min_order_amount DECIMAL(12,2) NULL,
    started_at      DATETIME NOT NULL,
    ended_at        DATETIME NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE promotion_products (
    promotion_id    INT NOT NULL,
    product_id      INT NOT NULL,
    override_price  DECIMAL(12,2) NULL,
    PRIMARY KEY (promotion_id, product_id),
    CONSTRAINT fk_promo_products_promo FOREIGN KEY (promotion_id) REFERENCES promotions(id),
    CONSTRAINT fk_promo_products_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Product Q&A (self-join)
-- =============================================
CREATE TABLE product_qna (
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    product_id      INT NOT NULL,
    customer_id     INT NULL,
    staff_id        INT NULL,
    parent_id       INT NULL,
    content         TEXT NOT NULL,
    is_answered     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      DATETIME NOT NULL,
    INDEX idx_qna_product (product_id),
    CONSTRAINT fk_qna_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_qna_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_qna_staff FOREIGN KEY (staff_id) REFERENCES staff(id),
    CONSTRAINT fk_qna_parent FOREIGN KEY (parent_id) REFERENCES product_qna(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Views
-- =============================================

CREATE OR REPLACE VIEW v_monthly_sales AS
SELECT
    DATE_FORMAT(o.ordered_at, '%Y-%m') AS month,
    COUNT(DISTINCT o.id) AS order_count,
    COUNT(DISTINCT o.customer_id) AS customer_count,
    CAST(SUM(o.total_amount) AS SIGNED) AS revenue,
    CAST(AVG(o.total_amount) AS SIGNED) AS avg_order,
    SUM(o.discount_amount) AS total_discount
FROM orders o
WHERE o.status != 'cancelled'
GROUP BY DATE_FORMAT(o.ordered_at, '%Y-%m')
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
        ELSE TIMESTAMPDIFF(YEAR, c.birth_date, '2025-06-30')
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
        WHEN c.last_login_at < DATE_SUB('2025-06-30', INTERVAL 365 DAY) THEN 'dormant'
        ELSE 'active'
    END AS activity_status
FROM customers c
LEFT JOIN (
    SELECT customer_id,
           COUNT(*) AS order_count,
           CAST(SUM(total_amount) AS SIGNED) AS total_spent,
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
           CAST(SUM(oi.subtotal) AS SIGNED) AS total_revenue,
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
WITH RECURSIVE tree AS (
    SELECT id, name, parent_id, depth,
           name AS full_path,
           LPAD(sort_order, 4, '0') AS sort_key
    FROM categories
    WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, c.depth,
           CONCAT(tree.full_path, ' > ', c.name),
           CONCAT(tree.sort_key, '.', LPAD(c.sort_order, 4, '0'))
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

CREATE OR REPLACE VIEW v_daily_orders AS
SELECT
    DATE(ordered_at) AS order_date,
    DAYNAME(ordered_at) AS day_of_week,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returned,
    CAST(SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS SIGNED) AS revenue,
    CAST(AVG(CASE WHEN status != 'cancelled' THEN total_amount END) AS SIGNED) AS avg_order_amount
FROM orders
GROUP BY DATE(ordered_at), DAYNAME(ordered_at)
ORDER BY order_date;

CREATE OR REPLACE VIEW v_payment_summary AS
SELECT
    method,
    COUNT(*) AS payment_count,
    CAST(SUM(amount) AS SIGNED) AS total_amount,
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
    CONCAT(ca.address1, ' ', COALESCE(ca.address2, '')) AS delivery_address
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
        DATE_FORMAT(ordered_at, '%Y-%m') AS month,
        CAST(SUM(total_amount) AS SIGNED) AS revenue,
        LAG(CAST(SUM(total_amount) AS SIGNED)) OVER (ORDER BY DATE_FORMAT(ordered_at, '%Y-%m')) AS prev_revenue
    FROM orders
    WHERE status != 'cancelled'
    GROUP BY DATE_FORMAT(ordered_at, '%Y-%m')
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
        COALESCE(SUM(oi.subtotal), 0) AS total_revenue,
        COALESCE(SUM(oi.quantity), 0) AS total_sold,
        ROW_NUMBER() OVER (
            PARTITION BY p.category_id
            ORDER BY COALESCE(SUM(oi.subtotal), 0) DESC
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
        DATEDIFF('2025-06-30', MAX(o.ordered_at)) AS recency_days,
        COUNT(o.id) AS frequency,
        CAST(SUM(o.total_amount) AS SIGNED) AS monetary
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    WHERE o.status != 'cancelled'
    GROUP BY c.id, c.name, c.grade
),
rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
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

CREATE OR REPLACE VIEW v_cart_abandonment AS
SELECT
    c.id AS cart_id,
    cust.name AS customer_name,
    cust.email,
    c.status,
    c.created_at,
    COUNT(ci.id) AS item_count,
    CAST(SUM(p.price * ci.quantity) AS SIGNED) AS potential_revenue,
    GROUP_CONCAT(p.name SEPARATOR ', ') AS products
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
           CAST(SUM(oi.subtotal) AS SIGNED) AS total_revenue,
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
GROUP BY s.id, s.company_name;

CREATE OR REPLACE VIEW v_hourly_pattern AS
SELECT
    HOUR(ordered_at) AS hour,
    COUNT(*) AS order_count,
    CAST(AVG(total_amount) AS SIGNED) AS avg_amount,
    CASE
        WHEN HOUR(ordered_at) BETWEEN 0 AND 5 THEN 'dawn'
        WHEN HOUR(ordered_at) BETWEEN 6 AND 11 THEN 'morning'
        WHEN HOUR(ordered_at) BETWEEN 12 AND 17 THEN 'afternoon'
        ELSE 'evening'
    END AS time_slot
FROM orders
WHERE status != 'cancelled'
GROUP BY HOUR(ordered_at),
    CASE
        WHEN HOUR(ordered_at) BETWEEN 0 AND 5 THEN 'dawn'
        WHEN HOUR(ordered_at) BETWEEN 6 AND 11 THEN 'morning'
        WHEN HOUR(ordered_at) BETWEEN 12 AND 17 THEN 'afternoon'
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
            CAST(COALESCE(SUM(oi.subtotal), 0) AS SIGNED) AS total_revenue
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
            THEN TIMESTAMPDIFF(HOUR, created_at, resolved_at)
            END
        ) AS SIGNED) AS avg_resolve_hours
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
        CAST(SUM(cu.discount_amount) AS SIGNED) AS total_discount,
        CAST(SUM(o.total_amount) AS SIGNED) AS total_order_revenue
    FROM coupon_usage cu
    JOIN orders o ON cu.order_id = o.id
    GROUP BY cu.coupon_id
) u ON cp.id = u.coupon_id
ORDER BY COALESCE(u.usage_count, 0) DESC;

CREATE OR REPLACE VIEW v_return_analysis AS
SELECT
    reason,
    COUNT(*) AS total_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM returns), 1) AS pct,
    SUM(CASE WHEN return_type = 'refund' THEN 1 ELSE 0 END) AS refund_count,
    SUM(CASE WHEN return_type = 'exchange' THEN 1 ELSE 0 END) AS exchange_count,
    CAST(AVG(refund_amount) AS SIGNED) AS avg_refund_amount,
    SUM(CASE WHEN inspection_result = 'defective' THEN 1 ELSE 0 END) AS defective_count,
    SUM(CASE WHEN inspection_result = 'good' THEN 1 ELSE 0 END) AS good_count,
    CAST(AVG(
        CASE WHEN completed_at IS NOT NULL
        THEN DATEDIFF(completed_at, requested_at)
        END
    ) AS SIGNED) AS avg_process_days
FROM returns
GROUP BY reason
ORDER BY total_count DESC;

CREATE OR REPLACE VIEW v_yearly_kpi AS
SELECT
    o_stats.yr AS year,
    o_stats.total_revenue,
    o_stats.order_count,
    o_stats.customer_count,
    CAST(o_stats.total_revenue / o_stats.order_count AS SIGNED) AS avg_order_value,
    CAST(o_stats.total_revenue / o_stats.customer_count AS SIGNED) AS revenue_per_customer,
    COALESCE(c.new_customers, 0) AS new_customers,
    o_stats.cancel_count,
    ROUND(o_stats.cancel_count * 100.0 / o_stats.order_count, 1) AS cancel_rate_pct,
    o_stats.return_count,
    ROUND(o_stats.return_count * 100.0 / o_stats.order_count, 1) AS return_rate_pct,
    COALESCE(r.review_count, 0) AS review_count,
    COALESCE(comp.complaint_count, 0) AS complaint_count
FROM (
    SELECT
        YEAR(o.ordered_at) AS yr,
        CAST(SUM(CASE WHEN o.status != 'cancelled' THEN o.total_amount ELSE 0 END) AS SIGNED) AS total_revenue,
        COUNT(*) AS order_count,
        COUNT(DISTINCT o.customer_id) AS customer_count,
        SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) AS cancel_count,
        SUM(CASE WHEN o.status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS return_count
    FROM orders o
    GROUP BY YEAR(o.ordered_at)
) o_stats
LEFT JOIN (
    SELECT YEAR(created_at) AS yr, COUNT(*) AS new_customers
    FROM customers GROUP BY YEAR(created_at)
) c ON o_stats.yr = c.yr
LEFT JOIN (
    SELECT YEAR(created_at) AS yr, COUNT(*) AS review_count
    FROM reviews GROUP BY YEAR(created_at)
) r ON o_stats.yr = r.yr
LEFT JOIN (
    SELECT YEAR(created_at) AS yr, COUNT(*) AS complaint_count
    FROM complaints GROUP BY YEAR(created_at)
) comp ON o_stats.yr = comp.yr
ORDER BY o_stats.yr;

-- =============================================
-- Access control examples (commented out)
-- =============================================
-- CREATE USER 'reader'@'%' IDENTIFIED BY 'readonly_password';
-- CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin_password';
-- GRANT SELECT ON ecommerce.* TO 'reader'@'%';
-- GRANT ALL ON ecommerce.* TO 'admin'@'localhost';
-- REVOKE DROP ON ecommerce.* FROM 'reader'@'%';
"""


PROCEDURES_SQL = """\
-- =============================================
-- E-commerce Stored Procedures - MySQL 8.0+
-- =============================================

USE ecommerce;

DELIMITER //

-- =============================================
-- sp_place_order: Create a new order and deduct customer points
-- Parameters:
--   p_customer_id  - Customer placing the order
--   p_address_id   - Delivery address
-- =============================================
CREATE PROCEDURE sp_place_order(
    IN p_customer_id INT,
    IN p_address_id INT
)
BEGIN
    DECLARE v_order_id INT;
    DECLARE v_total DECIMAL(12,2) DEFAULT 0;
    DECLARE v_points INT DEFAULT 0;
    DECLARE v_order_number VARCHAR(30);
    DECLARE v_now DATETIME DEFAULT NOW();

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Generate order number
    SET v_order_number = CONCAT('ORD-', DATE_FORMAT(v_now, '%Y%m%d'), '-',
        LPAD((SELECT COALESCE(MAX(id), 0) + 1 FROM orders), 5, '0'));

    -- Calculate cart total
    SELECT COALESCE(SUM(p.price * ci.quantity), 0)
    INTO v_total
    FROM carts c
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.customer_id = p_customer_id AND c.status = 'active';

    IF v_total = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cart is empty';
    END IF;

    -- Get customer point balance
    SELECT point_balance INTO v_points
    FROM customers WHERE id = p_customer_id FOR UPDATE;

    -- Create order
    INSERT INTO orders (order_number, customer_id, address_id, status,
                        total_amount, discount_amount, shipping_fee,
                        point_used, point_earned, ordered_at, created_at, updated_at)
    VALUES (v_order_number, p_customer_id, p_address_id, 'pending',
            v_total, 0, IF(v_total >= 50000, 0, 3000),
            0, FLOOR(v_total * 0.01), v_now, v_now, v_now);

    SET v_order_id = LAST_INSERT_ID();

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

    COMMIT;

    SELECT v_order_id AS order_id, v_order_number AS order_number, v_total AS total_amount;
END //

-- =============================================
-- sp_expire_points: Expire points older than 1 year
-- =============================================
CREATE PROCEDURE sp_expire_points()
BEGIN
    DECLARE v_now DATETIME DEFAULT NOW();
    DECLARE v_expired_count INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

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

    SET v_expired_count = ROW_COUNT();

    -- Update customer balances
    UPDATE customers c
    SET c.point_balance = GREATEST(0, c.point_balance - (
        SELECT COALESCE(SUM(pt.amount), 0)
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

    SELECT v_expired_count AS expired_transactions;
END //

-- =============================================
-- sp_monthly_settlement: Monthly sales summary report
-- Parameters:
--   p_year   - Report year
--   p_month  - Report month
-- =============================================
CREATE PROCEDURE sp_monthly_settlement(
    IN p_year INT,
    IN p_month INT
)
BEGIN
    DECLARE v_start_date DATETIME;
    DECLARE v_end_date DATETIME;

    SET v_start_date = CONCAT(p_year, '-', LPAD(p_month, 2, '0'), '-01 00:00:00');
    SET v_end_date = DATE_ADD(v_start_date, INTERVAL 1 MONTH);

    -- Order summary
    SELECT
        COUNT(*) AS total_orders,
        COUNT(DISTINCT customer_id) AS unique_customers,
        SUM(CASE WHEN status NOT IN ('cancelled') THEN total_amount ELSE 0 END) AS gross_revenue,
        SUM(discount_amount) AS total_discounts,
        SUM(shipping_fee) AS total_shipping,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        SUM(CASE WHEN status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returned_orders,
        ROUND(AVG(CASE WHEN status NOT IN ('cancelled') THEN total_amount END), 0) AS avg_order_value
    FROM orders
    WHERE ordered_at >= v_start_date AND ordered_at < v_end_date;

    -- Top 10 products by revenue
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
      AND o.status NOT IN ('cancelled')
    GROUP BY p.id
    ORDER BY total_revenue DESC
    LIMIT 10;

    -- Payment method breakdown
    SELECT
        pay.method,
        COUNT(*) AS count,
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
END //

-- =============================================
-- sp_cancel_order: Cancel an order and restore stock
-- Parameters:
--   p_order_id   - Order to cancel
--   p_reason     - Cancellation reason
-- =============================================
CREATE PROCEDURE sp_cancel_order(
    IN p_order_id INT,
    IN p_reason TEXT
)
BEGIN
    DECLARE v_status VARCHAR(30);
    DECLARE v_customer_id INT;
    DECLARE v_point_used INT;
    DECLARE v_now DATETIME DEFAULT NOW();

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Verify order exists and is cancellable
    SELECT status, customer_id, point_used
    INTO v_status, v_customer_id, v_point_used
    FROM orders WHERE id = p_order_id FOR UPDATE;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Order not found';
    END IF;

    IF v_status NOT IN ('pending', 'paid') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Order cannot be cancelled in current status';
    END IF;

    -- Restore stock
    UPDATE products p
    JOIN order_items oi ON p.id = oi.product_id
    SET p.stock_qty = p.stock_qty + oi.quantity
    WHERE oi.order_id = p_order_id;

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
        notes = CONCAT(COALESCE(notes, ''), '\n[Cancelled] ', p_reason)
    WHERE id = p_order_id;

    -- Refund payment
    UPDATE payments SET status = 'refunded', refunded_at = v_now
    WHERE order_id = p_order_id;

    COMMIT;

    SELECT p_order_id AS order_id, 'cancelled' AS new_status;
END //

-- =============================================
-- sp_update_customer_grades: Recalculate grades based on spending
-- =============================================
CREATE PROCEDURE sp_update_customer_grades()
BEGIN
    DECLARE v_now DATETIME DEFAULT NOW();
    DECLARE v_updated INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Calculate new grade based on last 12 months spending
    CREATE TEMPORARY TABLE tmp_new_grades AS
    SELECT
        c.id AS customer_id,
        c.grade AS old_grade,
        CASE
            WHEN COALESCE(s.total_spent, 0) >= 5000000 THEN 'VIP'
            WHEN COALESCE(s.total_spent, 0) >= 2000000 THEN 'GOLD'
            WHEN COALESCE(s.total_spent, 0) >= 500000  THEN 'SILVER'
            ELSE 'BRONZE'
        END AS new_grade
    FROM customers c
    LEFT JOIN (
        SELECT customer_id, SUM(total_amount) AS total_spent
        FROM orders
        WHERE status NOT IN ('cancelled')
          AND ordered_at >= DATE_SUB(v_now, INTERVAL 12 MONTH)
        GROUP BY customer_id
    ) s ON c.id = s.customer_id
    WHERE c.is_active = TRUE;

    -- Update grades that changed
    UPDATE customers c
    JOIN tmp_new_grades t ON c.id = t.customer_id
    SET c.grade = t.new_grade, c.updated_at = v_now
    WHERE c.grade != t.new_grade;

    SET v_updated = ROW_COUNT();

    -- Record grade history
    INSERT INTO customer_grade_history (customer_id, old_grade, new_grade, changed_at, reason)
    SELECT customer_id, old_grade, new_grade, v_now, 'yearly_review'
    FROM tmp_new_grades
    WHERE old_grade != new_grade;

    DROP TEMPORARY TABLE tmp_new_grades;

    COMMIT;

    SELECT v_updated AS grades_updated;
END //

-- =============================================
-- sp_cleanup_abandoned_carts: Remove old abandoned carts
-- Parameters:
--   p_days_old  - Delete carts older than this many days
-- =============================================
CREATE PROCEDURE sp_cleanup_abandoned_carts(
    IN p_days_old INT
)
BEGIN
    DECLARE v_deleted INT DEFAULT 0;
    DECLARE v_cutoff DATETIME;

    SET v_cutoff = DATE_SUB(NOW(), INTERVAL p_days_old DAY);

    -- Delete cart items first (FK)
    DELETE ci FROM cart_items ci
    JOIN carts c ON ci.cart_id = c.id
    WHERE c.status = 'abandoned' AND c.updated_at < v_cutoff;

    -- Delete abandoned carts
    DELETE FROM carts
    WHERE status = 'abandoned' AND updated_at < v_cutoff;

    SET v_deleted = ROW_COUNT();

    SELECT v_deleted AS carts_deleted, v_cutoff AS cutoff_date;
END //

-- =============================================
-- sp_product_restock: Process product restocking
-- Parameters:
--   p_product_id - Product to restock
--   p_quantity   - Quantity to add
--   p_notes      - Restock notes
-- =============================================
CREATE PROCEDURE sp_product_restock(
    IN p_product_id INT,
    IN p_quantity INT,
    IN p_notes VARCHAR(500)
)
BEGIN
    DECLARE v_now DATETIME DEFAULT NOW();
    DECLARE v_new_qty INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_quantity <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity must be positive';
    END IF;

    START TRANSACTION;

    -- Update stock
    UPDATE products
    SET stock_qty = stock_qty + p_quantity, updated_at = v_now
    WHERE id = p_product_id;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Product not found';
    END IF;

    SELECT stock_qty INTO v_new_qty FROM products WHERE id = p_product_id;

    -- Record inventory transaction
    INSERT INTO inventory_transactions (product_id, type, quantity, notes, created_at)
    VALUES (p_product_id, 'inbound', p_quantity, p_notes, v_now);

    COMMIT;

    SELECT p_product_id AS product_id, p_quantity AS added, v_new_qty AS new_stock_qty;
END //

-- =============================================
-- sp_customer_statistics: Return customer stats via OUT params
-- Parameters:
--   p_customer_id     - Customer ID
--   p_total_orders    - OUT: total order count
--   p_total_spent     - OUT: total spending
--   p_avg_order       - OUT: average order value
--   p_days_since_last - OUT: days since last order
-- =============================================
CREATE PROCEDURE sp_customer_statistics(
    IN  p_customer_id INT,
    OUT p_total_orders INT,
    OUT p_total_spent DECIMAL(12,2),
    OUT p_avg_order DECIMAL(12,2),
    OUT p_days_since_last INT
)
BEGIN
    SELECT
        COUNT(*),
        COALESCE(SUM(total_amount), 0),
        COALESCE(AVG(total_amount), 0),
        COALESCE(DATEDIFF(NOW(), MAX(ordered_at)), -1)
    INTO p_total_orders, p_total_spent, p_avg_order, p_days_since_last
    FROM orders
    WHERE customer_id = p_customer_id AND status != 'cancelled';
END //

-- =============================================
-- sp_daily_summary: Daily KPI summary report
-- Parameters:
--   p_date - Target date (YYYY-MM-DD)
-- =============================================
CREATE PROCEDURE sp_daily_summary(
    IN p_date DATE
)
BEGIN
    DECLARE v_start DATETIME;
    DECLARE v_end DATETIME;

    SET v_start = p_date;
    SET v_end = DATE_ADD(p_date, INTERVAL 1 DAY);

    -- Order KPIs
    SELECT
        p_date AS report_date,
        COUNT(*) AS total_orders,
        COUNT(DISTINCT customer_id) AS unique_customers,
        SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS revenue,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancellations,
        ROUND(AVG(CASE WHEN status != 'cancelled' THEN total_amount END), 0) AS avg_order_value
    FROM orders
    WHERE ordered_at >= v_start AND ordered_at < v_end;

    -- New signups
    SELECT COUNT(*) AS new_customers
    FROM customers
    WHERE created_at >= v_start AND created_at < v_end;

    -- Reviews posted
    SELECT COUNT(*) AS new_reviews, ROUND(AVG(rating), 1) AS avg_rating
    FROM reviews
    WHERE created_at >= v_start AND created_at < v_end;
END //

-- =============================================
-- sp_search_products: Dynamic search with optional filters
-- Parameters:
--   p_keyword       - Search keyword (name/brand/description)
--   p_category_id   - Category filter (NULL = all)
--   p_min_price     - Minimum price (NULL = no limit)
--   p_max_price     - Maximum price (NULL = no limit)
--   p_in_stock_only - Only show in-stock items (TRUE/FALSE)
-- =============================================
CREATE PROCEDURE sp_search_products(
    IN p_keyword VARCHAR(200),
    IN p_category_id INT,
    IN p_min_price DECIMAL(12,2),
    IN p_max_price DECIMAL(12,2),
    IN p_in_stock_only BOOLEAN
)
BEGIN
    SET @sql = 'SELECT p.id, p.name, p.brand, p.price, p.stock_qty, c.name AS category
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.is_active = TRUE';
    SET @params = '';

    IF p_keyword IS NOT NULL AND p_keyword != '' THEN
        SET @sql = CONCAT(@sql, ' AND (p.name LIKE ? OR p.brand LIKE ? OR p.description LIKE ?)');
        SET @kw = CONCAT('%', p_keyword, '%');
    END IF;

    IF p_category_id IS NOT NULL THEN
        SET @sql = CONCAT(@sql, ' AND p.category_id = ', p_category_id);
    END IF;

    IF p_min_price IS NOT NULL THEN
        SET @sql = CONCAT(@sql, ' AND p.price >= ', p_min_price);
    END IF;

    IF p_max_price IS NOT NULL THEN
        SET @sql = CONCAT(@sql, ' AND p.price <= ', p_max_price);
    END IF;

    IF p_in_stock_only = TRUE THEN
        SET @sql = CONCAT(@sql, ' AND p.stock_qty > 0');
    END IF;

    SET @sql = CONCAT(@sql, ' ORDER BY p.name LIMIT 100');

    IF p_keyword IS NOT NULL AND p_keyword != '' THEN
        PREPARE stmt FROM @sql;
        EXECUTE stmt USING @kw, @kw, @kw;
        DEALLOCATE PREPARE stmt;
    ELSE
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END //

-- =============================================
-- sp_transfer_points: Transfer points between customers
-- Parameters:
--   p_from_customer_id - Sender
--   p_to_customer_id   - Receiver
--   p_amount           - Points to transfer
-- =============================================
CREATE PROCEDURE sp_transfer_points(
    IN p_from_customer_id INT,
    IN p_to_customer_id INT,
    IN p_amount INT
)
BEGIN
    DECLARE v_from_balance INT;
    DECLARE v_to_balance INT;
    DECLARE v_now DATETIME DEFAULT NOW();

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_amount <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transfer amount must be positive';
    END IF;

    IF p_from_customer_id = p_to_customer_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot transfer to self';
    END IF;

    START TRANSACTION;

    -- Lock both rows in consistent order to prevent deadlock
    SELECT point_balance INTO v_from_balance
    FROM customers WHERE id = LEAST(p_from_customer_id, p_to_customer_id) FOR UPDATE;
    SELECT point_balance INTO v_to_balance
    FROM customers WHERE id = GREATEST(p_from_customer_id, p_to_customer_id) FOR UPDATE;

    -- Re-read actual balances
    SELECT point_balance INTO v_from_balance FROM customers WHERE id = p_from_customer_id;

    IF v_from_balance < p_amount THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient point balance';
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

    SELECT p_from_customer_id AS from_id, p_to_customer_id AS to_id, p_amount AS transferred;
END //

-- =============================================
-- sp_generate_order_report: Cursor-based order detail report
-- Parameters:
--   p_year  - Report year
--   p_month - Report month
-- =============================================
CREATE PROCEDURE sp_generate_order_report(
    IN p_year INT,
    IN p_month INT
)
BEGIN
    DECLARE v_order_id INT;
    DECLARE v_order_number VARCHAR(30);
    DECLARE v_total DECIMAL(12,2);
    DECLARE v_item_count INT;
    DECLARE v_done INT DEFAULT FALSE;

    DECLARE cur CURSOR FOR
        SELECT id, order_number, total_amount
        FROM orders
        WHERE YEAR(ordered_at) = p_year AND MONTH(ordered_at) = p_month
          AND status != 'cancelled'
        ORDER BY total_amount DESC;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = TRUE;

    -- Temp table for results
    DROP TEMPORARY TABLE IF EXISTS tmp_order_report;
    CREATE TEMPORARY TABLE tmp_order_report (
        order_number VARCHAR(30),
        total_amount DECIMAL(12,2),
        item_count INT,
        top_product VARCHAR(500)
    );

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_order_id, v_order_number, v_total;
        IF v_done THEN LEAVE read_loop; END IF;

        SELECT COUNT(*) INTO v_item_count FROM order_items WHERE order_id = v_order_id;

        INSERT INTO tmp_order_report
        SELECT v_order_number, v_total, v_item_count,
               (SELECT p.name FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = v_order_id
                ORDER BY oi.subtotal DESC LIMIT 1);
    END LOOP;

    CLOSE cur;

    SELECT * FROM tmp_order_report ORDER BY total_amount DESC;
    DROP TEMPORARY TABLE tmp_order_report;
END //

-- =============================================
-- sp_bulk_update_prices: Update multiple product prices from JSON
-- Parameters:
--   p_price_json - JSON array: [{"product_id": 1, "new_price": 99000}, ...]
-- =============================================
CREATE PROCEDURE sp_bulk_update_prices(
    IN p_price_json JSON
)
BEGIN
    DECLARE v_count INT DEFAULT 0;
    DECLARE v_now DATETIME DEFAULT NOW();

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Record old prices in history
    INSERT INTO product_prices (product_id, price, started_at, ended_at, change_reason)
    SELECT p.id, p.price, p.updated_at, v_now, 'price_drop'
    FROM products p
    JOIN JSON_TABLE(p_price_json, '$[*]' COLUMNS (
        product_id INT PATH '$.product_id',
        new_price DECIMAL(12,2) PATH '$.new_price'
    )) j ON p.id = j.product_id
    WHERE p.price != j.new_price;

    -- Update prices
    UPDATE products p
    JOIN JSON_TABLE(p_price_json, '$[*]' COLUMNS (
        product_id INT PATH '$.product_id',
        new_price DECIMAL(12,2) PATH '$.new_price'
    )) j ON p.id = j.product_id
    SET p.price = j.new_price, p.updated_at = v_now
    WHERE p.price != j.new_price;

    SET v_count = ROW_COUNT();

    COMMIT;

    SELECT v_count AS products_updated;
END //

-- =============================================
-- sp_archive_old_orders: Move old orders to archive concept
-- Parameters:
--   p_before_date - Archive orders before this date
-- =============================================
CREATE PROCEDURE sp_archive_old_orders(
    IN p_before_date DATE
)
BEGIN
    DECLARE v_archived INT DEFAULT 0;
    DECLARE v_now DATETIME DEFAULT NOW();

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Count target orders
    SELECT COUNT(*) INTO v_archived
    FROM orders
    WHERE ordered_at < p_before_date
      AND status IN ('confirmed', 'returned');

    -- In a real system, INSERT INTO archive_orders SELECT ... would go here.
    -- For this tutorial, we mark them with a note instead of actually moving.
    UPDATE orders
    SET notes = CONCAT(COALESCE(notes, ''), '\n[Archived] ', v_now)
    WHERE ordered_at < p_before_date
      AND status IN ('confirmed', 'returned')
      AND (notes IS NULL OR notes NOT LIKE '%[Archived]%');

    SET v_archived = ROW_COUNT();

    COMMIT;

    SELECT v_archived AS orders_archived, p_before_date AS cutoff_date;
END //

DELIMITER ;
"""


# Column mapping for MySQL data types
# Maps table.column -> True if the value should be treated as a boolean (0/1 -> TRUE/FALSE)
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

# Columns that store dates (TEXT in SQLite -> DATE in MySQL)
_DATE_COLUMNS = {
    "customers.birth_date",
    "calendar.date_key",
}


class MySQLExporter:
    """Export generated data to MySQL-compatible SQL files."""

    def __init__(self, output_dir: str):
        self.output_dir = os.path.join(output_dir, "mysql")
        os.makedirs(self.output_dir, exist_ok=True)

    def export(self, data: dict[str, list[dict]]) -> str:
        """Export all data to MySQL SQL files."""
        schema_path = os.path.join(self.output_dir, "schema.sql")
        data_path = os.path.join(self.output_dir, "data.sql")
        proc_path = os.path.join(self.output_dir, "procedures.sql")

        # Write schema DDL
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write(SCHEMA_SQL)

        # Write data
        with open(data_path, "w", encoding="utf-8") as f:
            f.write("-- =============================================\n")
            f.write("-- E-commerce Test Data - MySQL\n")
            f.write("-- =============================================\n\n")
            f.write("USE ecommerce;\n\n")
            f.write("SET NAMES utf8mb4;\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

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

            f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")

        # Write stored procedures
        with open(proc_path, "w", encoding="utf-8") as f:
            f.write(PROCEDURES_SQL)

        return self.output_dir

    def _write_inserts(self, f, table: str, rows: list[dict]):
        """Write batched INSERT statements (1000 rows per statement)."""
        if not rows:
            return

        columns = list(rows[0].keys())
        col_names = ", ".join(f"`{c}`" for c in columns)
        batch_size = 1000

        f.write(f"-- {table}: {len(rows)} rows\n")

        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            f.write(f"INSERT INTO `{table}` ({col_names}) VALUES\n")

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
        """Format a Python value as a MySQL literal."""
        if value is None:
            return "NULL"

        key = f"{table}.{column}"

        if key in _BOOL_COLUMNS:
            return "TRUE" if value else "FALSE"

        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"

        if isinstance(value, (int, float)):
            return str(value)

        # String value - escape for MySQL
        s = str(value)
        s = s.replace("\\", "\\\\")
        s = s.replace("'", "\\'")
        s = s.replace("\n", "\\n")
        s = s.replace("\r", "\\r")
        s = s.replace("\0", "\\0")
        return f"'{s}'"
