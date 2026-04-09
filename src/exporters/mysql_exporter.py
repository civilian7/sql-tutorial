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
    order_number    VARCHAR(30) NOT NULL UNIQUE,
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
