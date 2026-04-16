"""SQL Server database exporter

Generates DDL, INSERT data, and stored procedures for SQL Server 2019+.
"""

from __future__ import annotations

import os
from typing import Any


SCHEMA_SQL = """\
-- =============================================
-- E-commerce Test Database - SQL Server 2019+
-- =============================================

CREATE DATABASE ecommerce COLLATE Korean_CI_AS;
GO

USE ecommerce;
GO

-- =============================================
-- Product categories (hierarchical: top > mid > sub)
-- =============================================
CREATE TABLE categories (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    parent_id       INT NULL,
    name            NVARCHAR(100) NOT NULL,
    slug            NVARCHAR(100) NOT NULL UNIQUE,
    depth           INT NOT NULL DEFAULT 0,
    sort_order      INT NOT NULL DEFAULT 0,
    is_active       BIT NOT NULL DEFAULT 1,
    created_at      DATETIME2 NOT NULL,
    updated_at      DATETIME2 NOT NULL,
    CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories(id)
);
GO

-- =============================================
-- Suppliers
-- =============================================
CREATE TABLE suppliers (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    company_name    NVARCHAR(200) NOT NULL,
    business_number NVARCHAR(20) NOT NULL,
    contact_name    NVARCHAR(100) NOT NULL,
    phone           NVARCHAR(20) NOT NULL,
    email           NVARCHAR(200) NOT NULL,
    address         NVARCHAR(500) NULL,
    is_active       BIT NOT NULL DEFAULT 1,
    created_at      DATETIME2 NOT NULL,
    updated_at      DATETIME2 NOT NULL
);
GO

-- =============================================
-- Products
-- =============================================
CREATE TABLE products (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    category_id     INT NOT NULL,
    supplier_id     INT NOT NULL,
    successor_id    INT NULL,
    name            NVARCHAR(500) NOT NULL,
    sku             NVARCHAR(50) NOT NULL UNIQUE,
    brand           NVARCHAR(100) NOT NULL,
    model_number    NVARCHAR(50) NULL,
    description     NVARCHAR(MAX) NULL,
    specs           NVARCHAR(MAX) NULL,
    price           DECIMAL(12,2) NOT NULL CONSTRAINT chk_products_price CHECK (price >= 0),
    cost_price      DECIMAL(12,2) NOT NULL CONSTRAINT chk_products_cost CHECK (cost_price >= 0),
    stock_qty       INT NOT NULL DEFAULT 0,
    weight_grams    INT NULL,
    is_active       BIT NOT NULL DEFAULT 1,
    discontinued_at DATETIME2 NULL,
    created_at      DATETIME2 NOT NULL,
    updated_at      DATETIME2 NOT NULL,
    CONSTRAINT chk_products_specs_json CHECK (specs IS NULL OR ISJSON(specs) = 1),
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id),
    CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    CONSTRAINT fk_products_successor FOREIGN KEY (successor_id) REFERENCES products(id)
);
GO

-- =============================================
-- Product images (1-5 per product)
-- =============================================
CREATE TABLE product_images (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    product_id      INT NOT NULL,
    image_url       NVARCHAR(500) NOT NULL,
    file_name       NVARCHAR(200) NOT NULL,
    image_type      NVARCHAR(20) NOT NULL CONSTRAINT chk_product_images_type CHECK (image_type IN ('main','angle','side','back','detail','package','lifestyle','accessory','size_comparison')),
    alt_text        NVARCHAR(500) NULL,
    width           INT NULL,
    height          INT NULL,
    file_size       INT NULL,
    sort_order      INT NOT NULL DEFAULT 1,
    is_primary      BIT NOT NULL DEFAULT 0,
    created_at      DATETIME2 NOT NULL,
    CONSTRAINT fk_product_images_product FOREIGN KEY (product_id) REFERENCES products(id)
);
GO

-- =============================================
-- Product price history
-- =============================================
CREATE TABLE product_prices (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    product_id      INT NOT NULL,
    price           DECIMAL(12,2) NOT NULL,
    started_at      DATETIME2 NOT NULL,
    ended_at        DATETIME2 NULL,
    change_reason   NVARCHAR(20) NULL CONSTRAINT chk_product_prices_reason CHECK (change_reason IN ('regular','promotion','price_drop','cost_increase')),
    CONSTRAINT fk_product_prices_product FOREIGN KEY (product_id) REFERENCES products(id)
);
GO

-- =============================================
-- Customers
-- =============================================
CREATE TABLE customers (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    email           NVARCHAR(200) NOT NULL UNIQUE,
    password_hash   NVARCHAR(64) NOT NULL,
    name            NVARCHAR(100) NOT NULL,
    phone           NVARCHAR(20) NOT NULL,
    birth_date      DATE NULL,
    gender          NVARCHAR(1) NULL CONSTRAINT chk_customers_gender CHECK (gender IN ('M','F')),
    grade           NVARCHAR(10) NOT NULL DEFAULT 'BRONZE' CONSTRAINT chk_customers_grade CHECK (grade IN ('BRONZE','SILVER','GOLD','VIP')),
    point_balance   INT NOT NULL DEFAULT 0 CONSTRAINT chk_customers_points CHECK (point_balance >= 0),
    acquisition_channel NVARCHAR(20) NULL CONSTRAINT chk_customers_channel CHECK (acquisition_channel IN ('organic','search_ad','social','referral','direct')),
    is_active       BIT NOT NULL DEFAULT 1,
    last_login_at   DATETIME2 NULL,
    created_at      DATETIME2 NOT NULL,
    updated_at      DATETIME2 NOT NULL
);
GO

-- =============================================
-- Customer addresses (1-3 per customer)
-- =============================================
CREATE TABLE customer_addresses (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    customer_id     INT NOT NULL,
    label           NVARCHAR(50) NOT NULL,
    recipient_name  NVARCHAR(100) NOT NULL,
    phone           NVARCHAR(20) NOT NULL,
    zip_code        NVARCHAR(10) NOT NULL,
    address1        NVARCHAR(300) NOT NULL,
    address2        NVARCHAR(300) NULL,
    is_default      BIT NOT NULL DEFAULT 0,
    created_at      DATETIME2 NOT NULL,
    updated_at      DATETIME2 NULL,
    CONSTRAINT fk_customer_addresses_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);
GO

-- =============================================
-- Staff
-- =============================================
CREATE TABLE staff (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    manager_id      INT NULL,
    email           NVARCHAR(200) NOT NULL UNIQUE,
    name            NVARCHAR(100) NOT NULL,
    phone           NVARCHAR(20) NOT NULL,
    department      NVARCHAR(50) NOT NULL,
    role            NVARCHAR(10) NOT NULL CONSTRAINT chk_staff_role CHECK (role IN ('admin','manager','staff')),
    is_active       BIT NOT NULL DEFAULT 1,
    hired_at        DATETIME2 NOT NULL,
    created_at      DATETIME2 NOT NULL,
    CONSTRAINT fk_staff_manager FOREIGN KEY (manager_id) REFERENCES staff(id)
);
GO

-- =============================================
-- Partition function and scheme for orders
-- =============================================
CREATE PARTITION FUNCTION pf_orders_yearly (DATETIME2)
AS RANGE RIGHT FOR VALUES (
    '2016-01-01','2017-01-01','2018-01-01','2019-01-01','2020-01-01',
    '2021-01-01','2022-01-01','2023-01-01','2024-01-01','2025-01-01','2026-01-01'
);
GO

CREATE PARTITION SCHEME ps_orders_yearly
AS PARTITION pf_orders_yearly ALL TO ([PRIMARY]);
GO

-- =============================================
-- Orders (partitioned by year on ordered_at)
-- =============================================
CREATE TABLE orders (
    id              INT NOT NULL IDENTITY(1,1),
    order_number    NVARCHAR(30) NOT NULL,
    customer_id     INT NOT NULL,
    address_id      INT NOT NULL,
    staff_id        INT NULL,
    status          NVARCHAR(20) NOT NULL CONSTRAINT chk_orders_status CHECK (status IN ('pending','paid','preparing','shipped','delivered','confirmed','cancelled','return_requested','returned')),
    total_amount    DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    shipping_fee    DECIMAL(12,2) NOT NULL DEFAULT 0,
    point_used      INT NOT NULL DEFAULT 0,
    point_earned    INT NOT NULL DEFAULT 0,
    notes           NVARCHAR(MAX) NULL,
    ordered_at      DATETIME2 NOT NULL,
    completed_at    DATETIME2 NULL,
    cancelled_at    DATETIME2 NULL,
    created_at      DATETIME2 NOT NULL,
    updated_at      DATETIME2 NOT NULL,
    CONSTRAINT pk_orders PRIMARY KEY (id, ordered_at),
    CONSTRAINT uq_order_number UNIQUE (order_number, ordered_at)
) ON ps_orders_yearly(ordered_at);
GO

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_ordered_at ON orders(ordered_at);
GO

-- =============================================
-- Order items (1-5 items per order)
-- =============================================
CREATE TABLE order_items (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    order_id        INT NOT NULL,
    product_id      INT NOT NULL,
    quantity        INT NOT NULL CONSTRAINT chk_order_items_qty CHECK (quantity > 0),
    unit_price      DECIMAL(12,2) NOT NULL CONSTRAINT chk_order_items_price CHECK (unit_price >= 0),
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    subtotal        DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id)
);
GO

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
GO

-- =============================================
-- Payments
-- =============================================
CREATE TABLE payments (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    order_id        INT NOT NULL,
    method          NVARCHAR(20) NOT NULL CONSTRAINT chk_payments_method CHECK (method IN ('card','bank_transfer','virtual_account','kakao_pay','naver_pay','point')),
    amount          DECIMAL(12,2) NOT NULL CONSTRAINT chk_payments_amount CHECK (amount >= 0),
    status          NVARCHAR(10) NOT NULL CONSTRAINT chk_payments_status CHECK (status IN ('pending','completed','failed','refunded')),
    pg_transaction_id NVARCHAR(100) NULL,
    card_issuer     NVARCHAR(50) NULL,
    card_approval_no NVARCHAR(20) NULL,
    installment_months INT NULL,
    bank_name       NVARCHAR(50) NULL,
    account_no      NVARCHAR(50) NULL,
    depositor_name  NVARCHAR(100) NULL,
    easy_pay_method NVARCHAR(50) NULL,
    receipt_type    NVARCHAR(20) NULL,
    receipt_no      NVARCHAR(50) NULL,
    paid_at         DATETIME2 NULL,
    refunded_at     DATETIME2 NULL,
    created_at      DATETIME2 NOT NULL
);
GO

CREATE INDEX idx_payments_order ON payments(order_id);
GO

-- =============================================
-- Shipping
-- =============================================
CREATE TABLE shipping (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    order_id        INT NOT NULL,
    carrier         NVARCHAR(50) NOT NULL,
    tracking_number NVARCHAR(50) NULL,
    status          NVARCHAR(15) NOT NULL CONSTRAINT chk_shipping_status CHECK (status IN ('preparing','shipped','in_transit','delivered','returned')),
    shipped_at      DATETIME2 NULL,
    delivered_at    DATETIME2 NULL,
    created_at      DATETIME2 NOT NULL,
    updated_at      DATETIME2 NOT NULL
);
GO

CREATE INDEX idx_shipping_order ON shipping(order_id);
GO

-- =============================================
-- Reviews
-- =============================================
CREATE TABLE reviews (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    product_id      INT NOT NULL,
    customer_id     INT NOT NULL,
    order_id        INT NOT NULL,
    rating          TINYINT NOT NULL CONSTRAINT chk_reviews_rating CHECK (rating BETWEEN 1 AND 5),
    title           NVARCHAR(200) NULL,
    content         NVARCHAR(MAX) NULL,
    is_verified     BIT NOT NULL DEFAULT 1,
    created_at      DATETIME2 NOT NULL,
    updated_at      DATETIME2 NOT NULL,
    CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_reviews_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);
GO

CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_customer ON reviews(customer_id);
GO

-- =============================================
-- Inventory transactions
-- =============================================
CREATE TABLE inventory_transactions (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    product_id      INT NOT NULL,
    type            NVARCHAR(15) NOT NULL CONSTRAINT chk_inv_tx_type CHECK (type IN ('inbound','outbound','return','adjustment')),
    quantity        INT NOT NULL,
    reference_id    INT NULL,
    notes           NVARCHAR(500) NULL,
    created_at      DATETIME2 NOT NULL,
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products(id)
);
GO

-- =============================================
-- Carts
-- =============================================
CREATE TABLE carts (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    customer_id     INT NOT NULL,
    status          NVARCHAR(15) NOT NULL DEFAULT 'active' CONSTRAINT chk_carts_status CHECK (status IN ('active','converted','abandoned')),
    created_at      DATETIME2 NOT NULL,
    updated_at      DATETIME2 NOT NULL,
    CONSTRAINT fk_carts_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);
GO

-- =============================================
-- Cart items
-- =============================================
CREATE TABLE cart_items (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    cart_id         INT NOT NULL,
    product_id      INT NOT NULL,
    quantity        INT NOT NULL DEFAULT 1,
    added_at        DATETIME2 NOT NULL,
    CONSTRAINT fk_cart_items_cart FOREIGN KEY (cart_id) REFERENCES carts(id),
    CONSTRAINT fk_cart_items_product FOREIGN KEY (product_id) REFERENCES products(id)
);
GO

-- =============================================
-- Coupons
-- =============================================
CREATE TABLE coupons (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    code            NVARCHAR(30) NOT NULL UNIQUE,
    name            NVARCHAR(200) NOT NULL,
    type            NVARCHAR(10) NOT NULL CONSTRAINT chk_coupons_type CHECK (type IN ('percent','fixed')),
    discount_value  DECIMAL(12,2) NOT NULL CONSTRAINT chk_coupons_value CHECK (discount_value > 0),
    min_order_amount DECIMAL(12,2) NULL,
    max_discount    DECIMAL(12,2) NULL,
    usage_limit     INT NULL,
    per_user_limit  INT NOT NULL DEFAULT 1,
    is_active       BIT NOT NULL DEFAULT 1,
    started_at      DATETIME2 NOT NULL,
    expired_at      DATETIME2 NOT NULL,
    created_at      DATETIME2 NOT NULL
);
GO

-- =============================================
-- Coupon usage
-- =============================================
CREATE TABLE coupon_usage (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    coupon_id       INT NOT NULL,
    customer_id     INT NOT NULL,
    order_id        INT NOT NULL,
    discount_amount DECIMAL(12,2) NOT NULL,
    used_at         DATETIME2 NOT NULL,
    CONSTRAINT fk_coupon_usage_coupon FOREIGN KEY (coupon_id) REFERENCES coupons(id),
    CONSTRAINT fk_coupon_usage_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);
GO

-- =============================================
-- Customer complaints
-- =============================================
CREATE TABLE complaints (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    order_id        INT NULL,
    customer_id     INT NOT NULL,
    staff_id        INT NULL,
    category        NVARCHAR(30) NOT NULL CONSTRAINT chk_complaints_category CHECK (category IN ('product_defect','delivery_issue','wrong_item','refund_request','exchange_request','general_inquiry','price_inquiry')),
    channel         NVARCHAR(10) NOT NULL CONSTRAINT chk_complaints_channel CHECK (channel IN ('website','phone','email','chat','kakao')),
    priority        NVARCHAR(10) NOT NULL CONSTRAINT chk_complaints_priority CHECK (priority IN ('low','medium','high','urgent')),
    status          NVARCHAR(10) NOT NULL CONSTRAINT chk_complaints_status CHECK (status IN ('open','resolved','closed')),
    title           NVARCHAR(300) NOT NULL,
    content         NVARCHAR(MAX) NOT NULL,
    resolution      NVARCHAR(MAX) NULL,
    type            NVARCHAR(10) NOT NULL DEFAULT 'inquiry' CONSTRAINT chk_complaints_type CHECK (type IN ('inquiry','claim','report')),
    sub_category    NVARCHAR(100) NULL,
    compensation_type NVARCHAR(20) NULL CONSTRAINT chk_complaints_comp CHECK (compensation_type IN ('refund','exchange','partial_refund','point_compensation','none')),
    compensation_amount DECIMAL(12,2) NULL DEFAULT 0,
    escalated       BIT NOT NULL DEFAULT 0,
    response_count  INT NOT NULL DEFAULT 1,
    created_at      DATETIME2 NOT NULL,
    resolved_at     DATETIME2 NULL,
    closed_at       DATETIME2 NULL,
    CONSTRAINT fk_complaints_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_complaints_staff FOREIGN KEY (staff_id) REFERENCES staff(id)
);
GO

CREATE INDEX idx_complaints_customer ON complaints(customer_id);
CREATE INDEX idx_complaints_status ON complaints(status);
GO

-- =============================================
-- Returns/exchanges
-- =============================================
CREATE TABLE returns (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    order_id        INT NOT NULL,
    customer_id     INT NOT NULL,
    return_type     NVARCHAR(10) NOT NULL CONSTRAINT chk_returns_type CHECK (return_type IN ('refund','exchange')),
    reason          NVARCHAR(25) NOT NULL CONSTRAINT chk_returns_reason CHECK (reason IN ('defective','wrong_item','change_of_mind','damaged_in_transit','not_as_described','late_delivery')),
    reason_detail   NVARCHAR(MAX) NOT NULL,
    status          NVARCHAR(20) NOT NULL CONSTRAINT chk_returns_status CHECK (status IN ('requested','pickup_scheduled','in_transit','completed')),
    is_partial      BIT NOT NULL DEFAULT 0,
    refund_amount   DECIMAL(12,2) NOT NULL,
    refund_status   NVARCHAR(20) NOT NULL CONSTRAINT chk_returns_refund CHECK (refund_status IN ('pending','refunded','exchanged','partial_refund')),
    carrier         NVARCHAR(50) NOT NULL,
    tracking_number NVARCHAR(50) NOT NULL,
    requested_at    DATETIME2 NOT NULL,
    pickup_at       DATETIME2 NOT NULL,
    received_at     DATETIME2 NULL,
    inspected_at    DATETIME2 NULL,
    inspection_result NVARCHAR(15) NULL CONSTRAINT chk_returns_inspect CHECK (inspection_result IN ('good','opened_good','defective','unsellable')),
    completed_at    DATETIME2 NULL,
    claim_id        INT NULL,
    exchange_product_id INT NULL,
    restocking_fee  DECIMAL(12,2) NOT NULL DEFAULT 0,
    created_at      DATETIME2 NOT NULL,
    CONSTRAINT fk_returns_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_returns_claim FOREIGN KEY (claim_id) REFERENCES complaints(id),
    CONSTRAINT fk_returns_exchange_product FOREIGN KEY (exchange_product_id) REFERENCES products(id)
);
GO

CREATE INDEX idx_returns_order ON returns(order_id);
CREATE INDEX idx_returns_customer ON returns(customer_id);
GO

-- =============================================
-- Wishlists (M:N: customers <-> products)
-- =============================================
CREATE TABLE wishlists (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    customer_id     INT NOT NULL,
    product_id      INT NOT NULL,
    is_purchased    BIT NOT NULL DEFAULT 0,
    notify_on_sale  BIT NOT NULL DEFAULT 0,
    created_at      DATETIME2 NOT NULL,
    CONSTRAINT uq_wishlist UNIQUE (customer_id, product_id),
    CONSTRAINT fk_wishlists_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_wishlists_product FOREIGN KEY (product_id) REFERENCES products(id)
);
GO

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
    day_name        NVARCHAR(20) NOT NULL,
    is_weekend      BIT NOT NULL DEFAULT 0,
    is_holiday      BIT NOT NULL DEFAULT 0,
    holiday_name    NVARCHAR(100) NULL
);
GO

CREATE INDEX idx_calendar_year_month ON calendar(year, month);
GO

-- =============================================
-- Customer grade history (SCD Type 2)
-- =============================================
CREATE TABLE customer_grade_history (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    customer_id     INT NOT NULL,
    old_grade       NVARCHAR(10) NULL CONSTRAINT chk_grade_hist_old CHECK (old_grade IN ('BRONZE','SILVER','GOLD','VIP')),
    new_grade       NVARCHAR(10) NOT NULL CONSTRAINT chk_grade_hist_new CHECK (new_grade IN ('BRONZE','SILVER','GOLD','VIP')),
    changed_at      DATETIME2 NOT NULL,
    reason          NVARCHAR(20) NOT NULL CONSTRAINT chk_grade_hist_reason CHECK (reason IN ('signup','upgrade','downgrade','yearly_review')),
    CONSTRAINT fk_grade_history_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);
GO

CREATE INDEX idx_grade_history_customer ON customer_grade_history(customer_id);
GO

-- =============================================
-- Tags (M:N learning)
-- =============================================
CREATE TABLE tags (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    name            NVARCHAR(100) NOT NULL UNIQUE,
    category        NVARCHAR(50) NOT NULL
);
GO

CREATE TABLE product_tags (
    product_id      INT NOT NULL,
    tag_id          INT NOT NULL,
    CONSTRAINT pk_product_tags PRIMARY KEY (product_id, tag_id),
    CONSTRAINT fk_product_tags_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_product_tags_tag FOREIGN KEY (tag_id) REFERENCES tags(id)
);
GO

-- =============================================
-- Partition function and scheme for product_views
-- =============================================
CREATE PARTITION FUNCTION pf_views_yearly (DATETIME2)
AS RANGE RIGHT FOR VALUES (
    '2016-01-01','2017-01-01','2018-01-01','2019-01-01','2020-01-01',
    '2021-01-01','2022-01-01','2023-01-01','2024-01-01','2025-01-01','2026-01-01'
);
GO

CREATE PARTITION SCHEME ps_views_yearly
AS PARTITION pf_views_yearly ALL TO ([PRIMARY]);
GO

-- =============================================
-- Product views (partitioned by year)
-- =============================================
CREATE TABLE product_views (
    id              INT NOT NULL IDENTITY(1,1),
    customer_id     INT NOT NULL,
    product_id      INT NOT NULL,
    referrer_source NVARCHAR(20) NOT NULL CONSTRAINT chk_views_referrer CHECK (referrer_source IN ('direct','search','ad','recommendation','social','email')),
    device_type     NVARCHAR(10) NOT NULL CONSTRAINT chk_views_device CHECK (device_type IN ('desktop','mobile','tablet')),
    duration_seconds INT NOT NULL,
    viewed_at       DATETIME2 NOT NULL,
    CONSTRAINT pk_product_views PRIMARY KEY (id, viewed_at)
) ON ps_views_yearly(viewed_at);
GO

CREATE INDEX idx_views_customer ON product_views(customer_id);
CREATE INDEX idx_views_product ON product_views(product_id);
CREATE INDEX idx_views_viewed_at ON product_views(viewed_at);
GO

-- =============================================
-- Point transactions
-- =============================================
CREATE TABLE point_transactions (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    customer_id     INT NOT NULL,
    order_id        INT NULL,
    type            NVARCHAR(10) NOT NULL CONSTRAINT chk_point_tx_type CHECK (type IN ('earn','use','expire')),
    reason          NVARCHAR(10) NOT NULL CONSTRAINT chk_point_tx_reason CHECK (reason IN ('purchase','confirm','review','signup','use','expiry')),
    amount          INT NOT NULL,
    balance_after   INT NOT NULL,
    expires_at      DATETIME2 NULL,
    created_at      DATETIME2 NOT NULL,
    CONSTRAINT fk_point_tx_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);
GO

CREATE INDEX idx_point_tx_customer ON point_transactions(customer_id);
CREATE INDEX idx_point_tx_type ON point_transactions(type);
GO

-- =============================================
-- Promotions
-- =============================================
CREATE TABLE promotions (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    name            NVARCHAR(200) NOT NULL,
    type            NVARCHAR(10) NOT NULL CONSTRAINT chk_promotions_type CHECK (type IN ('seasonal','flash','category')),
    discount_type   NVARCHAR(10) NOT NULL CONSTRAINT chk_promotions_disc CHECK (discount_type IN ('percent','fixed')),
    discount_value  DECIMAL(12,2) NOT NULL,
    min_order_amount DECIMAL(12,2) NULL,
    started_at      DATETIME2 NOT NULL,
    ended_at        DATETIME2 NOT NULL,
    is_active       BIT NOT NULL DEFAULT 1,
    created_at      DATETIME2 NOT NULL
);
GO

CREATE TABLE promotion_products (
    promotion_id    INT NOT NULL,
    product_id      INT NOT NULL,
    override_price  DECIMAL(12,2) NULL,
    CONSTRAINT pk_promotion_products PRIMARY KEY (promotion_id, product_id),
    CONSTRAINT fk_promo_products_promo FOREIGN KEY (promotion_id) REFERENCES promotions(id),
    CONSTRAINT fk_promo_products_product FOREIGN KEY (product_id) REFERENCES products(id)
);
GO

-- =============================================
-- Product Q&A (self-join)
-- =============================================
CREATE TABLE product_qna (
    id              INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    product_id      INT NOT NULL,
    customer_id     INT NULL,
    staff_id        INT NULL,
    parent_id       INT NULL,
    content         NVARCHAR(MAX) NOT NULL,
    is_answered     BIT NOT NULL DEFAULT 0,
    created_at      DATETIME2 NOT NULL,
    CONSTRAINT fk_qna_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_qna_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_qna_staff FOREIGN KEY (staff_id) REFERENCES staff(id),
    CONSTRAINT fk_qna_parent FOREIGN KEY (parent_id) REFERENCES product_qna(id)
);
GO

CREATE INDEX idx_qna_product ON product_qna(product_id);
GO

-- =============================================
-- Views
-- =============================================

CREATE OR ALTER VIEW v_monthly_sales AS
SELECT
    FORMAT(o.ordered_at, 'yyyy-MM') AS month,
    COUNT(DISTINCT o.id) AS order_count,
    COUNT(DISTINCT o.customer_id) AS customer_count,
    CAST(SUM(o.total_amount) AS BIGINT) AS revenue,
    CAST(AVG(o.total_amount) AS BIGINT) AS avg_order,
    SUM(o.discount_amount) AS total_discount
FROM orders o
WHERE o.status != 'cancelled'
GROUP BY FORMAT(o.ordered_at, 'yyyy-MM');
GO

CREATE OR ALTER VIEW v_customer_summary AS
SELECT
    c.id,
    c.name,
    c.email,
    c.grade,
    c.gender,
    CASE
        WHEN c.birth_date IS NULL THEN NULL
        ELSE DATEDIFF(YEAR, c.birth_date, '2025-06-30')
    END AS age,
    c.created_at AS joined_at,
    ISNULL(os.order_count, 0) AS total_orders,
    ISNULL(os.total_spent, 0) AS total_spent,
    ISNULL(CAST(os.first_order AS NVARCHAR(30)), '') AS first_order_at,
    ISNULL(CAST(os.last_order AS NVARCHAR(30)), '') AS last_order_at,
    ISNULL(rv.review_count, 0) AS review_count,
    ISNULL(rv.avg_rating, 0) AS avg_rating_given,
    ISNULL(ws.wishlist_count, 0) AS wishlist_count,
    c.is_active,
    c.last_login_at,
    CASE
        WHEN c.is_active = 0 THEN 'inactive'
        WHEN c.last_login_at IS NULL THEN 'never_logged_in'
        WHEN c.last_login_at < DATEADD(DAY, -365, '2025-06-30') THEN 'dormant'
        ELSE 'active'
    END AS activity_status
FROM customers c
LEFT JOIN (
    SELECT customer_id,
           COUNT(*) AS order_count,
           CAST(SUM(total_amount) AS BIGINT) AS total_spent,
           MIN(ordered_at) AS first_order,
           MAX(ordered_at) AS last_order
    FROM orders
    WHERE status != 'cancelled'
    GROUP BY customer_id
) os ON c.id = os.customer_id
LEFT JOIN (
    SELECT customer_id,
           COUNT(*) AS review_count,
           ROUND(AVG(CAST(rating AS FLOAT)), 1) AS avg_rating
    FROM reviews
    GROUP BY customer_id
) rv ON c.id = rv.customer_id
LEFT JOIN (
    SELECT customer_id, COUNT(*) AS wishlist_count
    FROM wishlists
    GROUP BY customer_id
) ws ON c.id = ws.customer_id;
GO

CREATE OR ALTER VIEW v_product_performance AS
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
    ISNULL(s.total_sold, 0) AS total_sold,
    ISNULL(s.total_revenue, 0) AS total_revenue,
    ISNULL(s.order_count, 0) AS order_count,
    ISNULL(rv.review_count, 0) AS review_count,
    ISNULL(rv.avg_rating, 0) AS avg_rating,
    ISNULL(ws.wishlist_count, 0) AS wishlist_count,
    ISNULL(rt.return_count, 0) AS return_count
FROM products p
JOIN categories c ON p.category_id = c.id
LEFT JOIN (
    SELECT oi.product_id,
           SUM(oi.quantity) AS total_sold,
           CAST(SUM(oi.subtotal) AS BIGINT) AS total_revenue,
           COUNT(DISTINCT oi.order_id) AS order_count
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE o.status != 'cancelled'
    GROUP BY oi.product_id
) s ON p.id = s.product_id
LEFT JOIN (
    SELECT product_id,
           COUNT(*) AS review_count,
           ROUND(AVG(CAST(rating AS FLOAT)), 1) AS avg_rating
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
GO

CREATE OR ALTER VIEW v_category_tree AS
WITH tree AS (
    SELECT id, name, parent_id, depth,
           CAST(name AS NVARCHAR(MAX)) AS full_path,
           RIGHT('0000' + CAST(sort_order AS NVARCHAR(4)), 4) AS sort_key
    FROM categories
    WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, c.depth,
           CAST(tree.full_path + N' > ' + c.name AS NVARCHAR(MAX)),
           CAST(tree.sort_key + '.' + RIGHT('0000' + CAST(c.sort_order AS NVARCHAR(4)), 4) AS NVARCHAR(MAX))
    FROM categories c
    JOIN tree ON c.parent_id = tree.id
)
SELECT t.id, t.name, t.parent_id, t.depth, t.full_path,
       ISNULL(p.product_count, 0) AS product_count
FROM tree t
LEFT JOIN (
    SELECT category_id, COUNT(*) AS product_count
    FROM products
    GROUP BY category_id
) p ON t.id = p.category_id;
GO

CREATE OR ALTER VIEW v_daily_orders AS
SELECT
    CAST(ordered_at AS DATE) AS order_date,
    DATENAME(WEEKDAY, ordered_at) AS day_of_week,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returned,
    CAST(SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS BIGINT) AS revenue,
    CAST(AVG(CASE WHEN status != 'cancelled' THEN total_amount END) AS BIGINT) AS avg_order_amount
FROM orders
GROUP BY CAST(ordered_at AS DATE), DATENAME(WEEKDAY, ordered_at);
GO

CREATE OR ALTER VIEW v_payment_summary AS
SELECT
    method,
    COUNT(*) AS payment_count,
    CAST(SUM(amount) AS BIGINT) AS total_amount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM payments), 1) AS pct,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) AS refunded,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed
FROM payments
GROUP BY method;
GO

CREATE OR ALTER VIEW v_order_detail AS
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
    ca.address1 + N' ' + ISNULL(ca.address2, N'') AS delivery_address
FROM orders o
JOIN customers c ON o.customer_id = c.id
LEFT JOIN payments p ON o.id = p.order_id
LEFT JOIN shipping s ON o.id = s.order_id
LEFT JOIN customer_addresses ca ON o.address_id = ca.id;
GO

CREATE OR ALTER VIEW v_revenue_growth AS
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
        FORMAT(ordered_at, 'yyyy-MM') AS month,
        CAST(SUM(total_amount) AS BIGINT) AS revenue,
        LAG(CAST(SUM(total_amount) AS BIGINT)) OVER (ORDER BY FORMAT(ordered_at, 'yyyy-MM')) AS prev_revenue
    FROM orders
    WHERE status != 'cancelled'
    GROUP BY FORMAT(ordered_at, 'yyyy-MM')
) sub;
GO

CREATE OR ALTER VIEW v_top_products_by_category AS
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
        ISNULL(SUM(oi.subtotal), 0) AS total_revenue,
        ISNULL(SUM(oi.quantity), 0) AS total_sold,
        ROW_NUMBER() OVER (
            PARTITION BY p.category_id
            ORDER BY ISNULL(SUM(oi.subtotal), 0) DESC
        ) AS rank_in_category
    FROM products p
    JOIN categories cat ON p.category_id = cat.id
    LEFT JOIN order_items oi ON p.id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.id AND o.status != 'cancelled'
    GROUP BY p.id, cat.name, p.name, p.brand, p.category_id
) sub
WHERE rank_in_category <= 5;
GO

CREATE OR ALTER VIEW v_customer_rfm AS
WITH rfm_raw AS (
    SELECT
        c.id AS customer_id,
        c.name,
        c.grade,
        DATEDIFF(DAY, MAX(o.ordered_at), '2025-06-30') AS recency_days,
        COUNT(o.id) AS frequency,
        CAST(SUM(o.total_amount) AS BIGINT) AS monetary
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
GO

CREATE OR ALTER VIEW v_cart_abandonment AS
SELECT
    c.id AS cart_id,
    cust.name AS customer_name,
    cust.email,
    c.status,
    c.created_at,
    COUNT(ci.id) AS item_count,
    CAST(SUM(p.price * ci.quantity) AS BIGINT) AS potential_revenue,
    STRING_AGG(p.name, N', ') AS products
FROM carts c
JOIN customers cust ON c.customer_id = cust.id
JOIN cart_items ci ON c.id = ci.cart_id
JOIN products p ON ci.product_id = p.id
WHERE c.status = 'abandoned'
GROUP BY c.id, cust.name, cust.email, c.status, c.created_at;
GO

CREATE OR ALTER VIEW v_supplier_performance AS
SELECT
    s.id AS supplier_id,
    s.company_name,
    COUNT(DISTINCT p.id) AS product_count,
    SUM(CASE WHEN p.is_active = 1 THEN 1 ELSE 0 END) AS active_products,
    ISNULL(sales.total_revenue, 0) AS total_revenue,
    ISNULL(sales.total_sold, 0) AS total_sold,
    ISNULL(ret.return_count, 0) AS return_count,
    CASE
        WHEN ISNULL(sales.total_sold, 0) > 0
        THEN ROUND(ISNULL(ret.return_count, 0) * 100.0 / sales.total_sold, 2)
        ELSE 0
    END AS return_rate_pct
FROM suppliers s
LEFT JOIN products p ON s.id = p.supplier_id
LEFT JOIN (
    SELECT p2.supplier_id,
           CAST(SUM(oi.subtotal) AS BIGINT) AS total_revenue,
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
GO

CREATE OR ALTER VIEW v_hourly_pattern AS
SELECT
    DATEPART(HOUR, ordered_at) AS hour,
    COUNT(*) AS order_count,
    CAST(AVG(total_amount) AS BIGINT) AS avg_amount,
    CASE
        WHEN DATEPART(HOUR, ordered_at) BETWEEN 0 AND 5 THEN 'dawn'
        WHEN DATEPART(HOUR, ordered_at) BETWEEN 6 AND 11 THEN 'morning'
        WHEN DATEPART(HOUR, ordered_at) BETWEEN 12 AND 17 THEN 'afternoon'
        ELSE 'evening'
    END AS time_slot
FROM orders
WHERE status != 'cancelled'
GROUP BY DATEPART(HOUR, ordered_at),
    CASE
        WHEN DATEPART(HOUR, ordered_at) BETWEEN 0 AND 5 THEN 'dawn'
        WHEN DATEPART(HOUR, ordered_at) BETWEEN 6 AND 11 THEN 'morning'
        WHEN DATEPART(HOUR, ordered_at) BETWEEN 12 AND 17 THEN 'afternoon'
        ELSE 'evening'
    END;
GO

CREATE OR ALTER VIEW v_product_abc AS
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
            CAST(ISNULL(SUM(oi.subtotal), 0) AS BIGINT) AS total_revenue
        FROM products p
        LEFT JOIN order_items oi ON p.id = oi.product_id
        LEFT JOIN orders o ON oi.order_id = o.id AND o.status != 'cancelled'
        GROUP BY p.id, p.name, p.brand
    ) base
) ranked;
GO

CREATE OR ALTER VIEW v_staff_workload AS
SELECT
    s.id AS staff_id,
    s.name,
    s.department,
    ISNULL(comp.complaint_count, 0) AS complaint_count,
    ISNULL(comp.resolved_count, 0) AS resolved_count,
    ISNULL(comp.avg_resolve_hours, 0) AS avg_resolve_hours,
    ISNULL(ord.cs_order_count, 0) AS cs_order_count
FROM staff s
LEFT JOIN (
    SELECT
        staff_id,
        COUNT(*) AS complaint_count,
        SUM(CASE WHEN status IN ('resolved','closed') THEN 1 ELSE 0 END) AS resolved_count,
        CAST(AVG(
            CASE WHEN resolved_at IS NOT NULL
            THEN CAST(DATEDIFF(HOUR, created_at, resolved_at) AS FLOAT)
            END
        ) AS INT) AS avg_resolve_hours
    FROM complaints
    GROUP BY staff_id
) comp ON s.id = comp.staff_id
LEFT JOIN (
    SELECT staff_id, COUNT(*) AS cs_order_count
    FROM orders WHERE staff_id IS NOT NULL
    GROUP BY staff_id
) ord ON s.id = ord.staff_id
WHERE s.department = 'CS' OR comp.complaint_count > 0;
GO

CREATE OR ALTER VIEW v_coupon_effectiveness AS
SELECT
    cp.id AS coupon_id,
    cp.code,
    cp.name,
    cp.type,
    cp.discount_value,
    cp.is_active,
    ISNULL(u.usage_count, 0) AS usage_count,
    cp.usage_limit,
    ISNULL(u.total_discount, 0) AS total_discount_given,
    ISNULL(u.total_order_revenue, 0) AS total_order_revenue,
    CASE
        WHEN ISNULL(u.total_discount, 0) > 0
        THEN ROUND(u.total_order_revenue * 1.0 / u.total_discount, 1)
        ELSE 0
    END AS roi_ratio
FROM coupons cp
LEFT JOIN (
    SELECT
        cu.coupon_id,
        COUNT(*) AS usage_count,
        CAST(SUM(cu.discount_amount) AS BIGINT) AS total_discount,
        CAST(SUM(o.total_amount) AS BIGINT) AS total_order_revenue
    FROM coupon_usage cu
    JOIN orders o ON cu.order_id = o.id
    GROUP BY cu.coupon_id
) u ON cp.id = u.coupon_id;
GO

CREATE OR ALTER VIEW v_return_analysis AS
SELECT
    reason,
    COUNT(*) AS total_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM returns), 1) AS pct,
    SUM(CASE WHEN return_type = 'refund' THEN 1 ELSE 0 END) AS refund_count,
    SUM(CASE WHEN return_type = 'exchange' THEN 1 ELSE 0 END) AS exchange_count,
    CAST(AVG(refund_amount) AS BIGINT) AS avg_refund_amount,
    SUM(CASE WHEN inspection_result = 'defective' THEN 1 ELSE 0 END) AS defective_count,
    SUM(CASE WHEN inspection_result = 'good' THEN 1 ELSE 0 END) AS good_count,
    CAST(AVG(
        CASE WHEN completed_at IS NOT NULL
        THEN CAST(DATEDIFF(DAY, requested_at, completed_at) AS FLOAT)
        END
    ) AS INT) AS avg_process_days
FROM returns
GROUP BY reason;
GO

CREATE OR ALTER VIEW v_yearly_kpi AS
SELECT
    o_stats.yr AS year,
    o_stats.total_revenue,
    o_stats.order_count,
    o_stats.customer_count,
    CAST(o_stats.total_revenue / o_stats.order_count AS BIGINT) AS avg_order_value,
    CAST(o_stats.total_revenue / o_stats.customer_count AS BIGINT) AS revenue_per_customer,
    ISNULL(c.new_customers, 0) AS new_customers,
    o_stats.cancel_count,
    ROUND(o_stats.cancel_count * 100.0 / o_stats.order_count, 1) AS cancel_rate_pct,
    o_stats.return_count,
    ROUND(o_stats.return_count * 100.0 / o_stats.order_count, 1) AS return_rate_pct,
    ISNULL(r.review_count, 0) AS review_count,
    ISNULL(comp.complaint_count, 0) AS complaint_count
FROM (
    SELECT
        YEAR(o.ordered_at) AS yr,
        CAST(SUM(CASE WHEN o.status != 'cancelled' THEN o.total_amount ELSE 0 END) AS BIGINT) AS total_revenue,
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
) comp ON o_stats.yr = comp.yr;
GO

-- =============================================
-- Access control examples (commented out)
-- =============================================
-- CREATE LOGIN reader_login WITH PASSWORD = 'readonly_password';
-- CREATE USER reader FOR LOGIN reader_login;
-- CREATE LOGIN admin_login WITH PASSWORD = 'admin_password';
-- CREATE USER admin_user FOR LOGIN admin_login;
-- GRANT SELECT ON SCHEMA::dbo TO reader;
-- GRANT CONTROL ON SCHEMA::dbo TO admin_user;
-- REVOKE DELETE ON SCHEMA::dbo FROM reader;
"""


PROCEDURES_SQL = """\
-- =============================================
-- E-commerce Stored Procedures - SQL Server 2019+
-- =============================================

USE ecommerce;
GO

-- =============================================
-- sp_place_order: Create a new order and deduct customer points
-- Parameters:
--   @p_customer_id  - Customer placing the order
--   @p_address_id   - Delivery address
-- =============================================
CREATE OR ALTER PROCEDURE sp_place_order
    @p_customer_id INT,
    @p_address_id INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_order_id INT;
    DECLARE @v_total DECIMAL(12,2) = 0;
    DECLARE @v_points INT = 0;
    DECLARE @v_order_number NVARCHAR(30);
    DECLARE @v_now DATETIME2 = GETDATE();
    DECLARE @v_max_id INT;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Generate order number
        SELECT @v_max_id = ISNULL(MAX(id), 0) + 1 FROM orders;
        SET @v_order_number = CONCAT(N'ORD-', FORMAT(@v_now, 'yyyyMMdd'), N'-',
            RIGHT('00000' + CAST(@v_max_id AS NVARCHAR(5)), 5));

        -- Calculate cart total
        SELECT @v_total = ISNULL(SUM(p.price * ci.quantity), 0)
        FROM carts c
        JOIN cart_items ci ON c.id = ci.cart_id
        JOIN products p ON ci.product_id = p.id
        WHERE c.customer_id = @p_customer_id AND c.status = 'active';

        IF @v_total = 0
        BEGIN
            RAISERROR('Cart is empty', 16, 1);
        END

        -- Get customer point balance
        SELECT @v_points = point_balance
        FROM customers WITH (UPDLOCK) WHERE id = @p_customer_id;

        -- Create order
        INSERT INTO orders (order_number, customer_id, address_id, status,
                            total_amount, discount_amount, shipping_fee,
                            point_used, point_earned, ordered_at, created_at, updated_at)
        VALUES (@v_order_number, @p_customer_id, @p_address_id, 'pending',
                @v_total, 0, IIF(@v_total >= 50000, 0, 3000),
                0, FLOOR(@v_total * 0.01), @v_now, @v_now, @v_now);

        SET @v_order_id = SCOPE_IDENTITY();

        -- Move cart items to order items
        INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_amount, subtotal)
        SELECT @v_order_id, ci.product_id, ci.quantity, p.price, 0, p.price * ci.quantity
        FROM carts c
        JOIN cart_items ci ON c.id = ci.cart_id
        JOIN products p ON ci.product_id = p.id
        WHERE c.customer_id = @p_customer_id AND c.status = 'active';

        -- Mark cart as converted
        UPDATE carts SET status = 'converted', updated_at = @v_now
        WHERE customer_id = @p_customer_id AND status = 'active';

        COMMIT TRANSACTION;

        SELECT @v_order_id AS order_id, @v_order_number AS order_number, @v_total AS total_amount;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- =============================================
-- sp_expire_points: Expire points older than 1 year
-- =============================================
CREATE OR ALTER PROCEDURE sp_expire_points
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_now DATETIME2 = GETDATE();
    DECLARE @v_expired_count INT = 0;

    BEGIN TRY
        BEGIN TRANSACTION;

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
            @v_now
        FROM point_transactions pt
        JOIN customers c ON pt.customer_id = c.id
        WHERE pt.type = 'earn'
          AND pt.expires_at IS NOT NULL
          AND pt.expires_at < @v_now
          AND NOT EXISTS (
              SELECT 1 FROM point_transactions e
              WHERE e.customer_id = pt.customer_id
                AND e.type = 'expire'
                AND e.order_id = pt.order_id
          );

        SET @v_expired_count = @@ROWCOUNT;

        -- Update customer balances
        UPDATE c
        SET c.point_balance = IIF(c.point_balance - ISNULL(exp_sum.total_exp, 0) < 0, 0,
                                  c.point_balance - ISNULL(exp_sum.total_exp, 0))
        FROM customers c
        JOIN (
            SELECT pt.customer_id, SUM(pt.amount) AS total_exp
            FROM point_transactions pt
            WHERE pt.type = 'earn'
              AND pt.expires_at IS NOT NULL
              AND pt.expires_at < @v_now
              AND NOT EXISTS (
                  SELECT 1 FROM point_transactions e
                  WHERE e.customer_id = pt.customer_id
                    AND e.type = 'expire'
                    AND e.order_id = pt.order_id
                    AND e.created_at < @v_now
              )
            GROUP BY pt.customer_id
        ) exp_sum ON c.id = exp_sum.customer_id
        WHERE c.point_balance > 0;

        COMMIT TRANSACTION;

        SELECT @v_expired_count AS expired_transactions;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- =============================================
-- sp_monthly_settlement: Monthly sales summary report
-- Parameters:
--   @p_year   - Report year
--   @p_month  - Report month
-- =============================================
CREATE OR ALTER PROCEDURE sp_monthly_settlement
    @p_year INT,
    @p_month INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_start_date DATETIME2;
    DECLARE @v_end_date DATETIME2;

    SET @v_start_date = DATEFROMPARTS(@p_year, @p_month, 1);
    SET @v_end_date = DATEADD(MONTH, 1, @v_start_date);

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
    WHERE ordered_at >= @v_start_date AND ordered_at < @v_end_date;

    -- Top 10 products by revenue
    SELECT TOP 10
        p.id AS product_id,
        p.name AS product_name,
        p.brand,
        SUM(oi.quantity) AS total_qty,
        SUM(oi.subtotal) AS total_revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    JOIN products p ON oi.product_id = p.id
    WHERE o.ordered_at >= @v_start_date AND o.ordered_at < @v_end_date
      AND o.status NOT IN ('cancelled')
    GROUP BY p.id, p.name, p.brand
    ORDER BY total_revenue DESC;

    -- Payment method breakdown
    SELECT
        pay.method,
        COUNT(*) AS count,
        SUM(pay.amount) AS total_amount,
        ROUND(COUNT(*) * 100.0 / (
            SELECT COUNT(*) FROM payments pay2
            JOIN orders o2 ON pay2.order_id = o2.id
            WHERE o2.ordered_at >= @v_start_date AND o2.ordered_at < @v_end_date
        ), 1) AS pct
    FROM payments pay
    JOIN orders o ON pay.order_id = o.id
    WHERE o.ordered_at >= @v_start_date AND o.ordered_at < @v_end_date
    GROUP BY pay.method
    ORDER BY total_amount DESC;
END
GO

-- =============================================
-- sp_cancel_order: Cancel an order and restore stock
-- Parameters:
--   @p_order_id   - Order to cancel
--   @p_reason     - Cancellation reason
-- =============================================
CREATE OR ALTER PROCEDURE sp_cancel_order
    @p_order_id INT,
    @p_reason NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_status NVARCHAR(30);
    DECLARE @v_customer_id INT;
    DECLARE @v_point_used INT;
    DECLARE @v_now DATETIME2 = GETDATE();

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Verify order exists and is cancellable
        SELECT @v_status = status, @v_customer_id = customer_id, @v_point_used = point_used
        FROM orders WITH (UPDLOCK) WHERE id = @p_order_id;

        IF @v_status IS NULL
        BEGIN
            RAISERROR('Order not found', 16, 1);
        END

        IF @v_status NOT IN ('pending', 'paid')
        BEGIN
            RAISERROR('Order cannot be cancelled in current status', 16, 1);
        END

        -- Restore stock
        UPDATE p
        SET p.stock_qty = p.stock_qty + oi.quantity
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        WHERE oi.order_id = @p_order_id;

        -- Restore points if used
        IF @v_point_used > 0
        BEGIN
            UPDATE customers SET point_balance = point_balance + @v_point_used
            WHERE id = @v_customer_id;

            INSERT INTO point_transactions (customer_id, order_id, type, reason, amount, balance_after, created_at)
            SELECT @v_customer_id, @p_order_id, 'earn', 'purchase',
                   @v_point_used,
                   point_balance,
                   @v_now
            FROM customers WHERE id = @v_customer_id;
        END

        -- Update order status
        UPDATE orders
        SET status = 'cancelled', cancelled_at = @v_now, updated_at = @v_now,
            notes = CONCAT(ISNULL(notes, N''), NCHAR(10), N'[Cancelled] ', @p_reason)
        WHERE id = @p_order_id;

        -- Refund payment
        UPDATE payments SET status = 'refunded', refunded_at = @v_now
        WHERE order_id = @p_order_id;

        COMMIT TRANSACTION;

        SELECT @p_order_id AS order_id, 'cancelled' AS new_status;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- =============================================
-- sp_update_customer_grades: Recalculate grades based on spending
-- =============================================
CREATE OR ALTER PROCEDURE sp_update_customer_grades
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_now DATETIME2 = GETDATE();
    DECLARE @v_updated INT = 0;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Calculate new grade based on last 12 months spending
        SELECT
            c.id AS customer_id,
            c.grade AS old_grade,
            CASE
                WHEN ISNULL(s.total_spent, 0) >= 5000000 THEN 'VIP'
                WHEN ISNULL(s.total_spent, 0) >= 2000000 THEN 'GOLD'
                WHEN ISNULL(s.total_spent, 0) >= 500000  THEN 'SILVER'
                ELSE 'BRONZE'
            END AS new_grade
        INTO #tmp_new_grades
        FROM customers c
        LEFT JOIN (
            SELECT customer_id, SUM(total_amount) AS total_spent
            FROM orders
            WHERE status NOT IN ('cancelled')
              AND ordered_at >= DATEADD(MONTH, -12, @v_now)
            GROUP BY customer_id
        ) s ON c.id = s.customer_id
        WHERE c.is_active = 1;

        -- Update grades that changed
        UPDATE c
        SET c.grade = t.new_grade, c.updated_at = @v_now
        FROM customers c
        JOIN #tmp_new_grades t ON c.id = t.customer_id
        WHERE c.grade != t.new_grade;

        SET @v_updated = @@ROWCOUNT;

        -- Record grade history
        INSERT INTO customer_grade_history (customer_id, old_grade, new_grade, changed_at, reason)
        SELECT customer_id, old_grade, new_grade, @v_now, 'yearly_review'
        FROM #tmp_new_grades
        WHERE old_grade != new_grade;

        DROP TABLE #tmp_new_grades;

        COMMIT TRANSACTION;

        SELECT @v_updated AS grades_updated;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        IF OBJECT_ID('tempdb..#tmp_new_grades') IS NOT NULL DROP TABLE #tmp_new_grades;
        THROW;
    END CATCH
END
GO

-- =============================================
-- sp_cleanup_abandoned_carts: Remove old abandoned carts
-- Parameters:
--   @p_days_old  - Delete carts older than this many days
-- =============================================
CREATE OR ALTER PROCEDURE sp_cleanup_abandoned_carts
    @p_days_old INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_deleted INT = 0;
    DECLARE @v_cutoff DATETIME2;

    SET @v_cutoff = DATEADD(DAY, -@p_days_old, GETDATE());

    -- Delete cart items first (FK)
    DELETE ci
    FROM cart_items ci
    JOIN carts c ON ci.cart_id = c.id
    WHERE c.status = 'abandoned' AND c.updated_at < @v_cutoff;

    -- Delete abandoned carts
    DELETE FROM carts
    WHERE status = 'abandoned' AND updated_at < @v_cutoff;

    SET @v_deleted = @@ROWCOUNT;

    SELECT @v_deleted AS carts_deleted, @v_cutoff AS cutoff_date;
END
GO

-- =============================================
-- sp_product_restock: Process product restocking
-- Parameters:
--   @p_product_id - Product to restock
--   @p_quantity   - Quantity to add
--   @p_notes      - Restock notes
-- =============================================
CREATE OR ALTER PROCEDURE sp_product_restock
    @p_product_id INT,
    @p_quantity INT,
    @p_notes NVARCHAR(500)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_now DATETIME2 = GETDATE();
    DECLARE @v_new_qty INT;

    IF @p_quantity <= 0
    BEGIN
        RAISERROR('Quantity must be positive', 16, 1);
    END

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Update stock
        UPDATE products
        SET stock_qty = stock_qty + @p_quantity, updated_at = @v_now
        WHERE id = @p_product_id;

        IF @@ROWCOUNT = 0
        BEGIN
            RAISERROR('Product not found', 16, 1);
        END

        SELECT @v_new_qty = stock_qty FROM products WHERE id = @p_product_id;

        -- Record inventory transaction
        INSERT INTO inventory_transactions (product_id, type, quantity, notes, created_at)
        VALUES (@p_product_id, 'inbound', @p_quantity, @p_notes, @v_now);

        COMMIT TRANSACTION;

        SELECT @p_product_id AS product_id, @p_quantity AS added, @v_new_qty AS new_stock_qty;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- =============================================
-- sp_customer_statistics: Return customer stats via OUTPUT params
-- Parameters:
--   @p_customer_id     - Customer ID
--   @p_total_orders    - OUTPUT: total order count
--   @p_total_spent     - OUTPUT: total spending
--   @p_avg_order       - OUTPUT: average order value
--   @p_days_since_last - OUTPUT: days since last order
-- =============================================
CREATE OR ALTER PROCEDURE sp_customer_statistics
    @p_customer_id INT,
    @p_total_orders INT OUTPUT,
    @p_total_spent DECIMAL(12,2) OUTPUT,
    @p_avg_order DECIMAL(12,2) OUTPUT,
    @p_days_since_last INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        @p_total_orders = COUNT(*),
        @p_total_spent = ISNULL(SUM(total_amount), 0),
        @p_avg_order = ISNULL(AVG(total_amount), 0),
        @p_days_since_last = ISNULL(DATEDIFF(DAY, MAX(ordered_at), GETDATE()), -1)
    FROM orders
    WHERE customer_id = @p_customer_id AND status != 'cancelled';
END
GO

-- =============================================
-- sp_daily_summary: Daily KPI summary report
-- Parameters:
--   @p_date - Target date (YYYY-MM-DD)
-- =============================================
CREATE OR ALTER PROCEDURE sp_daily_summary
    @p_date DATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_start DATETIME2;
    DECLARE @v_end DATETIME2;

    SET @v_start = CAST(@p_date AS DATETIME2);
    SET @v_end = DATEADD(DAY, 1, @v_start);

    -- Order KPIs
    SELECT
        @p_date AS report_date,
        COUNT(*) AS total_orders,
        COUNT(DISTINCT customer_id) AS unique_customers,
        SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS revenue,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancellations,
        ROUND(AVG(CASE WHEN status != 'cancelled' THEN total_amount END), 0) AS avg_order_value
    FROM orders
    WHERE ordered_at >= @v_start AND ordered_at < @v_end;

    -- New signups
    SELECT COUNT(*) AS new_customers
    FROM customers
    WHERE created_at >= @v_start AND created_at < @v_end;

    -- Reviews posted
    SELECT COUNT(*) AS new_reviews, ROUND(AVG(CAST(rating AS FLOAT)), 1) AS avg_rating
    FROM reviews
    WHERE created_at >= @v_start AND created_at < @v_end;
END
GO

-- =============================================
-- sp_search_products: Dynamic search with optional filters
-- Parameters:
--   @p_keyword       - Search keyword (name/brand/description)
--   @p_category_id   - Category filter (NULL = all)
--   @p_min_price     - Minimum price (NULL = no limit)
--   @p_max_price     - Maximum price (NULL = no limit)
--   @p_in_stock_only - Only show in-stock items (1/0)
-- =============================================
CREATE OR ALTER PROCEDURE sp_search_products
    @p_keyword NVARCHAR(200),
    @p_category_id INT = NULL,
    @p_min_price DECIMAL(12,2) = NULL,
    @p_max_price DECIMAL(12,2) = NULL,
    @p_in_stock_only BIT = 0
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_sql NVARCHAR(MAX);
    DECLARE @v_params NVARCHAR(500);

    SET @v_sql = N'SELECT TOP 100 p.id, p.name, p.brand, p.price, p.stock_qty, c.name AS category
                   FROM products p
                   JOIN categories c ON p.category_id = c.id
                   WHERE p.is_active = 1';

    IF @p_keyword IS NOT NULL AND @p_keyword != N''
    BEGIN
        SET @v_sql = @v_sql + N' AND (p.name LIKE @kw OR p.brand LIKE @kw OR p.description LIKE @kw)';
    END

    IF @p_category_id IS NOT NULL
        SET @v_sql = @v_sql + N' AND p.category_id = @cat_id';

    IF @p_min_price IS NOT NULL
        SET @v_sql = @v_sql + N' AND p.price >= @min_p';

    IF @p_max_price IS NOT NULL
        SET @v_sql = @v_sql + N' AND p.price <= @max_p';

    IF @p_in_stock_only = 1
        SET @v_sql = @v_sql + N' AND p.stock_qty > 0';

    SET @v_sql = @v_sql + N' ORDER BY p.name';

    SET @v_params = N'@kw NVARCHAR(202), @cat_id INT, @min_p DECIMAL(12,2), @max_p DECIMAL(12,2)';

    EXEC sp_executesql @v_sql, @v_params,
        @kw = N'%' + @p_keyword + N'%',
        @cat_id = @p_category_id,
        @min_p = @p_min_price,
        @max_p = @p_max_price;
END
GO

-- =============================================
-- sp_transfer_points: Transfer points between customers
-- Parameters:
--   @p_from_customer_id - Sender
--   @p_to_customer_id   - Receiver
--   @p_amount           - Points to transfer
-- =============================================
CREATE OR ALTER PROCEDURE sp_transfer_points
    @p_from_customer_id INT,
    @p_to_customer_id INT,
    @p_amount INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_from_balance INT;
    DECLARE @v_to_balance INT;
    DECLARE @v_now DATETIME2 = GETDATE();

    IF @p_amount <= 0
    BEGIN
        RAISERROR('Transfer amount must be positive', 16, 1);
    END

    IF @p_from_customer_id = @p_to_customer_id
    BEGIN
        RAISERROR('Cannot transfer to self', 16, 1);
    END

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Lock both rows in consistent order to prevent deadlock
        SELECT @v_from_balance = point_balance
        FROM customers WITH (UPDLOCK) WHERE id = IIF(@p_from_customer_id < @p_to_customer_id, @p_from_customer_id, @p_to_customer_id);
        SELECT @v_to_balance = point_balance
        FROM customers WITH (UPDLOCK) WHERE id = IIF(@p_from_customer_id < @p_to_customer_id, @p_to_customer_id, @p_from_customer_id);

        -- Re-read actual sender balance
        SELECT @v_from_balance = point_balance FROM customers WHERE id = @p_from_customer_id;

        IF @v_from_balance < @p_amount
        BEGIN
            RAISERROR('Insufficient point balance', 16, 1);
        END

        -- Deduct from sender
        UPDATE customers SET point_balance = point_balance - @p_amount WHERE id = @p_from_customer_id;
        INSERT INTO point_transactions (customer_id, type, reason, amount, balance_after, created_at)
        SELECT @p_from_customer_id, 'use', 'purchase', -@p_amount, point_balance, @v_now
        FROM customers WHERE id = @p_from_customer_id;

        -- Add to receiver
        UPDATE customers SET point_balance = point_balance + @p_amount WHERE id = @p_to_customer_id;
        INSERT INTO point_transactions (customer_id, type, reason, amount, balance_after, created_at)
        SELECT @p_to_customer_id, 'earn', 'purchase', @p_amount, point_balance, @v_now
        FROM customers WHERE id = @p_to_customer_id;

        COMMIT TRANSACTION;

        SELECT @p_from_customer_id AS from_id, @p_to_customer_id AS to_id, @p_amount AS transferred;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- =============================================
-- sp_generate_order_report: Cursor-based order detail report
-- Parameters:
--   @p_year  - Report year
--   @p_month - Report month
-- =============================================
CREATE OR ALTER PROCEDURE sp_generate_order_report
    @p_year INT,
    @p_month INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_order_id INT;
    DECLARE @v_order_number NVARCHAR(30);
    DECLARE @v_total DECIMAL(12,2);
    DECLARE @v_item_count INT;

    CREATE TABLE #tmp_order_report (
        order_number NVARCHAR(30),
        total_amount DECIMAL(12,2),
        item_count INT,
        top_product NVARCHAR(500)
    );

    DECLARE cur CURSOR LOCAL FAST_FORWARD FOR
        SELECT id, order_number, total_amount
        FROM orders
        WHERE YEAR(ordered_at) = @p_year AND MONTH(ordered_at) = @p_month
          AND status != 'cancelled'
        ORDER BY total_amount DESC;

    OPEN cur;
    FETCH NEXT FROM cur INTO @v_order_id, @v_order_number, @v_total;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SELECT @v_item_count = COUNT(*) FROM order_items WHERE order_id = @v_order_id;

        INSERT INTO #tmp_order_report (order_number, total_amount, item_count, top_product)
        SELECT @v_order_number, @v_total, @v_item_count,
               (SELECT TOP 1 p.name FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = @v_order_id
                ORDER BY oi.subtotal DESC);

        FETCH NEXT FROM cur INTO @v_order_id, @v_order_number, @v_total;
    END

    CLOSE cur;
    DEALLOCATE cur;

    SELECT * FROM #tmp_order_report ORDER BY total_amount DESC;
    DROP TABLE #tmp_order_report;
END
GO

-- =============================================
-- sp_bulk_update_prices: Update multiple product prices from JSON
-- Parameters:
--   @p_price_json - JSON array: [{"product_id": 1, "new_price": 99000}, ...]
-- =============================================
CREATE OR ALTER PROCEDURE sp_bulk_update_prices
    @p_price_json NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_count INT = 0;
    DECLARE @v_now DATETIME2 = GETDATE();

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Record old prices in history
        INSERT INTO product_prices (product_id, price, started_at, ended_at, change_reason)
        SELECT p.id, p.price, p.updated_at, @v_now, 'price_drop'
        FROM products p
        JOIN OPENJSON(@p_price_json) WITH (
            product_id INT '$.product_id',
            new_price DECIMAL(12,2) '$.new_price'
        ) j ON p.id = j.product_id
        WHERE p.price != j.new_price;

        -- Update prices
        UPDATE p
        SET p.price = j.new_price, p.updated_at = @v_now
        FROM products p
        JOIN OPENJSON(@p_price_json) WITH (
            product_id INT '$.product_id',
            new_price DECIMAL(12,2) '$.new_price'
        ) j ON p.id = j.product_id
        WHERE p.price != j.new_price;

        SET @v_count = @@ROWCOUNT;

        COMMIT TRANSACTION;

        SELECT @v_count AS products_updated;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- =============================================
-- sp_archive_old_orders: Move old orders to archive concept
-- Parameters:
--   @p_before_date - Archive orders before this date
-- =============================================
CREATE OR ALTER PROCEDURE sp_archive_old_orders
    @p_before_date DATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @v_archived INT = 0;
    DECLARE @v_now DATETIME2 = GETDATE();

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Count target orders
        SELECT @v_archived = COUNT(*)
        FROM orders
        WHERE ordered_at < @p_before_date
          AND status IN ('confirmed', 'returned');

        -- In a real system, INSERT INTO archive_orders SELECT ... would go here.
        -- For this tutorial, we mark them with a note instead of actually moving.
        UPDATE orders
        SET notes = CONCAT(ISNULL(notes, N''), NCHAR(10), N'[Archived] ', CAST(@v_now AS NVARCHAR(30)))
        WHERE ordered_at < @p_before_date
          AND status IN ('confirmed', 'returned')
          AND (notes IS NULL OR notes NOT LIKE N'%[Archived]%');

        SET @v_archived = @@ROWCOUNT;

        COMMIT TRANSACTION;

        SELECT @v_archived AS orders_archived, @p_before_date AS cutoff_date;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO
"""


# Column mapping for SQL Server data types
# Maps table.column -> True if the value should be treated as a boolean (0/1 -> BIT)
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

# Columns that store dates (TEXT in SQLite -> DATE in SQL Server)
_DATE_COLUMNS = {
    "customers.birth_date",
    "calendar.date_key",
}

# Tables with IDENTITY columns (need SET IDENTITY_INSERT ON/OFF)
_IDENTITY_TABLES = {
    "categories", "suppliers", "products", "product_images", "product_prices",
    "customers", "customer_addresses", "staff",
    "orders", "order_items", "payments", "shipping",
    "reviews", "inventory_transactions",
    "carts", "cart_items", "coupons", "coupon_usage",
    "wishlists", "complaints", "returns",
    "customer_grade_history",
    "tags",
    "product_views",
    "point_transactions",
    "promotions",
    "product_qna",
}


COMMENTS_SQL = """\n-- =============================================
-- Table & Column Comments - SQL Server (Extended Properties)
-- =============================================

USE ecommerce;
GO

-- Table comments
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'고객 마스터. 등급(BRONZE/SILVER/GOLD/VIP), 적립금, 가입채널, 활성상태 관리',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'고객 배송지. 고객당 복수 주소, 기본 배송지 지정',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'상품 카테고리. 대/중/소 3단계 계층(self-referencing FK)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'categories';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'공급업체(입점 판매자). 사업자 정보, 담당자 연락처 관리',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'suppliers';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'상품 마스터. SKU, 판매가/원가, 재고, 브랜드/모델, 후속상품 관리',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'상품 이미지. 상품당 복수 이미지(메인/상세/라이프스타일 등)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'상품 가격 이력. 가격 변경 시 트리거 자동 기록',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_prices';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'주문. 주문번호(ORD-YYYYMMDD-NNNNN), 상태 흐름(pending→delivered/cancelled)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'주문 상세 항목. 주문 시점 단가/수량, 아이템별 할인',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'order_items';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'결제. 카드/계좌이체/간편결제, PG 거래번호, 현금영수증',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'배송. 택배사, 운송장번호, 배송 상태 추적',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'shipping';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'반품/교환. 사유, 검수 결과, 환불 상태, 수거 택배 정보',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'상품 리뷰. 1~5점 별점, 구매 인증 여부',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'reviews';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'장바구니. active/converted/abandoned 상태 관리',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'carts';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'장바구니 항목. 담긴 상품과 수량',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'cart_items';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'쿠폰 정의. 정률/정액 할인, 사용 한도, 유효기간',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'쿠폰 사용 이력. 고객-주문-쿠폰 매핑',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupon_usage';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'고객 문의/불만. 카테고리별 분류, 우선순위, CS 담당자 배정, 보상 관리',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'재고 변동 이력. 입고/출고/반품/조정 트랜잭션',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'inventory_transactions';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'내부 직원. 부서(sales/CS/logistics 등), 역할(admin/manager/staff), 조직도',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'staff';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'위시리스트. 고객-상품 UNIQUE, 가격 하락 알림 설정',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'wishlists';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'날짜 차원 테이블. 요일, 공휴일, 분기 등 날짜 속성',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'calendar';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'고객 등급 변경 이력(SCD Type 2). 변경 전후 등급, 변경 사유',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_grade_history';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'포인트 적립/사용/소멸 원장. 거래 유형별 증감, 잔액 추적',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'point_transactions';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'상품 Q&A. 질문-답변 자기참조 스레드',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_qna';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'상품-태그 연결(M:N). 복합 PK',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_tags';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'상품 조회 로그. 유입경로, 기기유형, 체류시간 기록',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_views';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'프로모션 대상 상품. 프로모션-상품 연결(M:N), 특가 설정',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotion_products';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'프로모션/세일 이벤트. 할인율/금액, 기간, 대상 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotions';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'상품 태그 마스터. 태그명, 분류(feature/use_case/target/spec)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'tags';

-- Column comments
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 고객 고유 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'UNIQUE. 이메일 주소. 로그인 ID',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'email';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. SHA-256 비밀번호 해시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'password_hash';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 고객 실명',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 020-XXXX-XXXX 형식. 연락처',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'phone';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD. 생년월일. NULL=미입력(약 15%)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'birth_date';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(M,F). 성별. NULL=미입력(약 10%)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'gender';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(BRONZE,SILVER,GOLD,VIP). 구매 실적 기반 회원 등급. 분기별 재산정',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'grade';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수 ≥0. 보유 적립금',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'point_balance';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 활성=1, 탈퇴=0',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'is_active';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 마지막 로그인 일시. NULL=미접속',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'last_login_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 가입 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 최종 수정 일시. 트리거 자동 갱신',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'updated_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(organic,search_ad,social,referral,direct). 유입 경로. NULL=미확인',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customers',
  @level2type=N'COLUMN', @level2name=N'acquisition_channel';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 상품 고유 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→categories(id). NOT NULL. 소속 카테고리',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'category_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→suppliers(id). NOT NULL. 공급업체',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'supplier_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 상품명',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'UNIQUE. NOT NULL. 재고관리코드',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'sku';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 브랜드명',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'brand';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'제조사 모델번호. NULL=미등록',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'model_number';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'상품 설명. NULL 가능',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'description';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL ≥0. 현재 판매가(원)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'price';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL ≥0. 원가(원)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'cost_price';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 현재 재고 수량. 기본값 0',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'stock_qty';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 배송 무게(그램). NULL 가능',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'weight_grams';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 판매중=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'is_active';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 단종일. NULL=판매중',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'discontinued_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). 후속 상품(단종 시 대체). NULL=없음',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'successor_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'JSON. 상품 상세 스펙. NULL 가능',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'specs';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 등록 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 최종 수정 일시. 트리거 자동 갱신',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'products',
  @level2type=N'COLUMN', @level2name=N'updated_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 주문 고유 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'UNIQUE. ORD-YYYYMMDD-NNNNN 형식. 주문번호',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'order_number';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). NOT NULL. 주문한 고객',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customer_addresses(id). 배송지',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'address_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→staff(id). CS 담당 직원. NULL=미배정(취소/반품 시 배정)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'staff_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(pending,paid,preparing,shipped,delivered,confirmed,cancelled). 주문 상태',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'status';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 최종 결제 금액(원)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'total_amount';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 할인 합계. 기본값 0',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'discount_amount';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 배송비. 5만원 이상 무료',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'shipping_fee';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 사용한 적립금. 기본값 0',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'point_used';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 적립 예정 포인트. 기본값 0',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'point_earned';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'배송 메모. NULL=메모 없음',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'notes';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 주문 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'ordered_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 구매확정일. NULL=미확정',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'completed_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 취소일. NULL=취소 안 됨',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'cancelled_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 레코드 생성 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 최종 수정 일시. 트리거 자동 갱신',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'orders',
  @level2type=N'COLUMN', @level2name=N'updated_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→orders(id). NOT NULL. 소속 주문',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'order_items',
  @level2type=N'COLUMN', @level2name=N'order_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). NOT NULL. 주문 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'order_items',
  @level2type=N'COLUMN', @level2name=N'product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수 ≥1. 주문 수량',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'order_items',
  @level2type=N'COLUMN', @level2name=N'quantity';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 주문 시점 단가(원)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'order_items',
  @level2type=N'COLUMN', @level2name=N'unit_price';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 아이템별 할인 금액. 기본값 0',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'order_items',
  @level2type=N'COLUMN', @level2name=N'discount_amount';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 소계 = (단가 × 수량) - 할인',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'order_items',
  @level2type=N'COLUMN', @level2name=N'subtotal';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 주문 항목 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'order_items',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(card,bank_transfer,kakao_pay,naver_pay,point). 결제 수단',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'method';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 결제 금액(원)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'amount';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(pending,completed,failed,refunded). 결제 상태',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'status';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PG사 거래번호. NULL=미발급',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'pg_transaction_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'카드사(신한/삼성/KB국민/현대 등). NULL=카드 외 결제',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'card_issuer';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 할부 개월수. 0=일시불',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'installment_months';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 결제 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→orders(id). NOT NULL. 소속 주문',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'order_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'8자리. 카드 승인번호. NULL=카드 외 결제',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'card_approval_no';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'은행명. NULL=계좌이체/가상계좌 외',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'bank_name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'가상계좌 번호. NULL=해당 없음',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'account_no';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'입금자명. NULL=계좌이체 외',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'depositor_name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'간편결제 세부수단(카카오페이 잔액/연결카드 등). NULL=간편결제 외',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'easy_pay_method';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'소득공제/지출증빙. 현금영수증 유형. NULL=미발급',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'receipt_type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'현금영수증 번호. NULL=미발급',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'receipt_no';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 결제 완료 일시. NULL=미완료',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'paid_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 환불 일시. NULL=환불 없음',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'refunded_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 결제 레코드 생성 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'payments',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(refund,exchange). 반품 유형',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'return_type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(defective,wrong_item,change_of_mind,damaged_in_transit,not_as_described,late_delivery). 반품 사유',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'reason';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(requested,pickup_scheduled,in_transit,completed). 반품 상태',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'status';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 부분반품=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'is_partial';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(good,opened_good,defective,unsellable). 검수 결과. NULL=미검수',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'inspection_result';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 반품 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→orders(id). NOT NULL. 원 주문',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'order_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). NOT NULL. 반품 요청 고객',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'반품 상세 사유 설명. NULL 가능',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'reason_detail';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 환불 금액(원)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'refund_amount';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(pending,refunded,exchanged,partial_refund). 환불 상태',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'refund_status';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'수거 택배사. NULL=미배정',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'carrier';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'수거 운송장 번호. NULL=미발급',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'tracking_number';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 반품 요청 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'requested_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 수거 예정/완료 일시. NULL=미예약',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'pickup_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 물류센터 입고 일시. NULL=미입고',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'received_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 검수 완료 일시. NULL=미검수',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'inspected_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 처리 완료 일시. NULL=미완료',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'completed_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→complaints(id). 연결 클레임. NULL=CS 미연결',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'claim_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). 교환 상품. NULL=환불 건',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'exchange_product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 변심 반품 재입고 수수료. 기본값 0',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'restocking_fee';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 레코드 생성 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'returns',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'범위 1~5. 별점',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'reviews',
  @level2type=N'COLUMN', @level2name=N'rating';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 구매인증=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'reviews',
  @level2type=N'COLUMN', @level2name=N'is_verified';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 리뷰 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'reviews',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). NOT NULL. 리뷰 대상 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'reviews',
  @level2type=N'COLUMN', @level2name=N'product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). NOT NULL. 작성 고객',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'reviews',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→orders(id). 구매 주문. NULL=비구매 리뷰',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'reviews',
  @level2type=N'COLUMN', @level2name=N'order_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'리뷰 제목. NULL=미작성(약 20%)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'reviews',
  @level2type=N'COLUMN', @level2name=N'title';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'리뷰 본문. NULL 가능',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'reviews',
  @level2type=N'COLUMN', @level2name=N'content';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 작성 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'reviews',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 최종 수정 일시. 트리거 자동 갱신',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'reviews',
  @level2type=N'COLUMN', @level2name=N'updated_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'UNIQUE. 쿠폰 코드',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'code';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(percent,fixed). percent=정률, fixed=정액',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 할인율(%) 또는 할인금액(원)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'discount_value';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 최소 주문금액 조건',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'min_order_amount';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 최대 할인금액(정률 시 상한). NULL=제한 없음',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'max_discount';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 쿠폰 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 쿠폰명',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 전체 사용 한도. NULL=무제한',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'usage_limit';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 1인당 사용 한도. 기본값 1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'per_user_limit';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 활성=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'is_active';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 유효기간 시작일',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'started_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 유효기간 종료일',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'expired_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 등록 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupons',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(product_defect,delivery_issue,wrong_item,refund_request,exchange_request,general_inquiry,price_inquiry). 문의 유형',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'category';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(website,phone,email,chat,kakao). 접수 채널',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'channel';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(low,medium,high,urgent). 우선순위',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'priority';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(open,resolved,closed). 처리 상태',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'status';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 문의/클레임 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→orders(id). 관련 주문. NULL=일반문의',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'order_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). NOT NULL. 문의 고객',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→staff(id). CS 담당 직원. NULL=미배정',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'staff_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 문의 제목',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'title';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 문의 내용',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'content';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'처리 결과 상세. resolved 시 작성. NULL=미해결',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'resolution';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(inquiry,claim,report). 문의 유형. 기본값 inquiry',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'세부 분류(initial_defect/in_use_damage/misdelivery 등). NULL=미지정',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'sub_category';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(refund,exchange,partial_refund,point_compensation,none). 보상 유형',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'compensation_type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 보상 금액(원). 기본값 0',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'compensation_amount';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 상위 관리자 에스컬레이션=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'escalated';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 응대 횟수. 기본값 1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'response_count';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 접수 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 해결 일시. NULL=미해결',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'resolved_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 종료 일시. NULL=미종료',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'complaints',
  @level2type=N'COLUMN', @level2name=N'closed_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(inbound,outbound,return,adjustment). 변동 유형',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'inventory_transactions',
  @level2type=N'COLUMN', @level2name=N'type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 양수=입고, 음수=출고',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'inventory_transactions',
  @level2type=N'COLUMN', @level2name=N'quantity';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 재고 변동 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'inventory_transactions',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). NOT NULL. 대상 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'inventory_transactions',
  @level2type=N'COLUMN', @level2name=N'product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'관련 주문 ID. NULL=초기입고/조정',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'inventory_transactions',
  @level2type=N'COLUMN', @level2name=N'reference_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'비고(initial_stock/regular_inbound/return_inbound 등)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'inventory_transactions',
  @level2type=N'COLUMN', @level2name=N'notes';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 변동 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'inventory_transactions',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→categories(id). 상위 카테고리. NULL=최상위',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'categories',
  @level2type=N'COLUMN', @level2name=N'parent_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'범위 0~2. 0=대분류, 1=중분류, 2=소분류',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'categories',
  @level2type=N'COLUMN', @level2name=N'depth';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'UNIQUE. URL용 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'categories',
  @level2type=N'COLUMN', @level2name=N'slug';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 카테고리 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'categories',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 카테고리명',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'categories',
  @level2type=N'COLUMN', @level2name=N'name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 표시 순서(오름차순)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'categories',
  @level2type=N'COLUMN', @level2name=N'sort_order';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 활성=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'categories',
  @level2type=N'COLUMN', @level2name=N'is_active';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 등록 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'categories',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 최종 수정 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'categories',
  @level2type=N'COLUMN', @level2name=N'updated_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'CJ대한통운/한진택배/로젠택배/우체국택배. 택배사',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'shipping',
  @level2type=N'COLUMN', @level2name=N'carrier';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'운송장 번호. NULL=미발급',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'shipping',
  @level2type=N'COLUMN', @level2name=N'tracking_number';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(preparing,shipped,in_transit,delivered,returned). 배송 상태',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'shipping',
  @level2type=N'COLUMN', @level2name=N'status';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 배송 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'shipping',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→orders(id). NOT NULL. 소속 주문',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'shipping',
  @level2type=N'COLUMN', @level2name=N'order_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 발송 일시. NULL=미발송',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'shipping',
  @level2type=N'COLUMN', @level2name=N'shipped_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 배송완료 일시. NULL=미배송',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'shipping',
  @level2type=N'COLUMN', @level2name=N'delivered_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 레코드 생성 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'shipping',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 최종 수정 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'shipping',
  @level2type=N'COLUMN', @level2name=N'updated_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 가격 하락 알림=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'wishlists',
  @level2type=N'COLUMN', @level2name=N'notify_on_sale';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 위시리스트 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'wishlists',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). UNIQUE(customer_id,product_id). 고객',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'wishlists',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). UNIQUE(customer_id,product_id). 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'wishlists',
  @level2type=N'COLUMN', @level2name=N'product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 구매 전환=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'wishlists',
  @level2type=N'COLUMN', @level2name=N'is_purchased';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 등록 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'wishlists',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. YYYY-MM-DD 형식. 날짜 키',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'calendar',
  @level2type=N'COLUMN', @level2name=N'date_key';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 연도(예: 2024)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'calendar',
  @level2type=N'COLUMN', @level2name=N'year';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'범위 1~12. 월',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'calendar',
  @level2type=N'COLUMN', @level2name=N'month';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'범위 1~31. 일',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'calendar',
  @level2type=N'COLUMN', @level2name=N'day';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'범위 1~4. 분기',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'calendar',
  @level2type=N'COLUMN', @level2name=N'quarter';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'범위 0~6. 0=월요일, 6=일요일',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'calendar',
  @level2type=N'COLUMN', @level2name=N'day_of_week';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'Monday~Sunday. 요일명',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'calendar',
  @level2type=N'COLUMN', @level2name=N'day_name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 주말=1(토/일)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'calendar',
  @level2type=N'COLUMN', @level2name=N'is_weekend';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 공휴일=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'calendar',
  @level2type=N'COLUMN', @level2name=N'is_holiday';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'공휴일명. NULL=공휴일 아님',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'calendar',
  @level2type=N'COLUMN', @level2name=N'holiday_name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 장바구니 항목 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'cart_items',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→carts(id). NOT NULL. 소속 장바구니',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'cart_items',
  @level2type=N'COLUMN', @level2name=N'cart_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). NOT NULL. 담은 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'cart_items',
  @level2type=N'COLUMN', @level2name=N'product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수 ≥1. 담은 수량. 기본값 1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'cart_items',
  @level2type=N'COLUMN', @level2name=N'quantity';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 장바구니 담은 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'cart_items',
  @level2type=N'COLUMN', @level2name=N'added_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 장바구니 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'carts',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). NOT NULL. 소유 고객',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'carts',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(active,converted,abandoned). 장바구니 상태',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'carts',
  @level2type=N'COLUMN', @level2name=N'status';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 생성 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'carts',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 최종 수정 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'carts',
  @level2type=N'COLUMN', @level2name=N'updated_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 쿠폰 사용 이력 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupon_usage',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→coupons(id). NOT NULL. 사용 쿠폰',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupon_usage',
  @level2type=N'COLUMN', @level2name=N'coupon_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). NOT NULL. 사용 고객',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupon_usage',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→orders(id). NOT NULL. 사용 주문',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupon_usage',
  @level2type=N'COLUMN', @level2name=N'order_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 실제 할인 금액(원)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupon_usage',
  @level2type=N'COLUMN', @level2name=N'discount_amount';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 쿠폰 사용 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'coupon_usage',
  @level2type=N'COLUMN', @level2name=N'used_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 배송지 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). NOT NULL. 소유 고객',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(home,office,other). 배송지 구분',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses',
  @level2type=N'COLUMN', @level2name=N'label';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 수령인 이름',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses',
  @level2type=N'COLUMN', @level2name=N'recipient_name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 수령인 연락처',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses',
  @level2type=N'COLUMN', @level2name=N'phone';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 우편번호',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses',
  @level2type=N'COLUMN', @level2name=N'zip_code';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 기본 주소',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses',
  @level2type=N'COLUMN', @level2name=N'address1';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'상세 주소. NULL=미입력',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses',
  @level2type=N'COLUMN', @level2name=N'address2';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 기본 배송지=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses',
  @level2type=N'COLUMN', @level2name=N'is_default';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 등록 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 수정 일시. NULL=미수정',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_addresses',
  @level2type=N'COLUMN', @level2name=N'updated_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 등급 이력 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_grade_history',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). NOT NULL. 대상 고객',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_grade_history',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(BRONZE,SILVER,GOLD,VIP). 변경 전 등급. NULL=최초 가입',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_grade_history',
  @level2type=N'COLUMN', @level2name=N'old_grade';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(BRONZE,SILVER,GOLD,VIP). NOT NULL. 변경 후 등급',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_grade_history',
  @level2type=N'COLUMN', @level2name=N'new_grade';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 등급 변경 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_grade_history',
  @level2type=N'COLUMN', @level2name=N'changed_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(signup,upgrade,downgrade,yearly_review). 변경 사유',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'customer_grade_history',
  @level2type=N'COLUMN', @level2name=N'reason';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 포인트 거래 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'point_transactions',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). NOT NULL. 대상 고객',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'point_transactions',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→orders(id). 관련 주문. NULL=가입/소멸',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'point_transactions',
  @level2type=N'COLUMN', @level2name=N'order_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(earn,use,expire). 거래 유형',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'point_transactions',
  @level2type=N'COLUMN', @level2name=N'type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(purchase,confirm,review,signup,use,expiry). 사유',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'point_transactions',
  @level2type=N'COLUMN', @level2name=N'reason';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 양수=적립, 음수=사용/소멸',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'point_transactions',
  @level2type=N'COLUMN', @level2name=N'amount';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 거래 후 잔여 포인트',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'point_transactions',
  @level2type=N'COLUMN', @level2name=N'balance_after';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 적립 포인트 만료일. NULL=사용/소멸 건',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'point_transactions',
  @level2type=N'COLUMN', @level2name=N'expires_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 거래 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'point_transactions',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 이미지 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). NOT NULL. 소속 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 이미지 경로/URL',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'image_url';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 파일명(예: 42_1.jpg)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'file_name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(main,angle,side,back,detail,package,lifestyle,accessory,size_comparison). 이미지 유형',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'image_type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'대체 텍스트(접근성용). NULL 가능',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'alt_text';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 이미지 가로(px). NULL 가능',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'width';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 이미지 세로(px). NULL 가능',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'height';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 파일 크기(bytes). NULL 가능',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'file_size';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 표시 순서. 기본값 1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'sort_order';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 대표 이미지=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'is_primary';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 등록 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_images',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 가격 이력 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_prices',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). NOT NULL. 대상 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_prices',
  @level2type=N'COLUMN', @level2name=N'product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 해당 기간 판매가(원)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_prices',
  @level2type=N'COLUMN', @level2name=N'price';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 적용 시작일',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_prices',
  @level2type=N'COLUMN', @level2name=N'started_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 적용 종료일. NULL=현재 가격',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_prices',
  @level2type=N'COLUMN', @level2name=N'ended_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(regular,promotion,price_drop,cost_increase). 변경 사유',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_prices',
  @level2type=N'COLUMN', @level2name=N'change_reason';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. Q&A 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_qna',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). NOT NULL. 대상 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_qna',
  @level2type=N'COLUMN', @level2name=N'product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). 질문 고객. NULL=직원 답변',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_qna',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→staff(id). 답변 직원. NULL=고객 질문',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_qna',
  @level2type=N'COLUMN', @level2name=N'staff_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→product_qna(id). 부모 글. NULL=질문, 값 있으면=답변',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_qna',
  @level2type=N'COLUMN', @level2name=N'parent_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 질문 또는 답변 내용',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_qna',
  @level2type=N'COLUMN', @level2name=N'content';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 답변 완료=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_qna',
  @level2type=N'COLUMN', @level2name=N'is_answered';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 작성 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_qna',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). 복합 PK. 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_tags',
  @level2type=N'COLUMN', @level2name=N'product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→tags(id). 복합 PK. 태그',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_tags',
  @level2type=N'COLUMN', @level2name=N'tag_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 조회 로그 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_views',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→customers(id). NOT NULL. 조회 고객',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_views',
  @level2type=N'COLUMN', @level2name=N'customer_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). NOT NULL. 조회 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_views',
  @level2type=N'COLUMN', @level2name=N'product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(direct,search,ad,recommendation,social,email). 유입 경로',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_views',
  @level2type=N'COLUMN', @level2name=N'referrer_source';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(desktop,mobile,tablet). 접속 기기',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_views',
  @level2type=N'COLUMN', @level2name=N'device_type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'정수. 페이지 체류 시간(초)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_views',
  @level2type=N'COLUMN', @level2name=N'duration_seconds';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 조회 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'product_views',
  @level2type=N'COLUMN', @level2name=N'viewed_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→promotions(id). 복합 PK. 프로모션',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotion_products',
  @level2type=N'COLUMN', @level2name=N'promotion_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→products(id). 복합 PK. 상품',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotion_products',
  @level2type=N'COLUMN', @level2name=N'product_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 특가. NULL=프로모션 할인율 적용',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotion_products',
  @level2type=N'COLUMN', @level2name=N'override_price';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 프로모션 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotions',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 프로모션명',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotions',
  @level2type=N'COLUMN', @level2name=N'name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(seasonal,flash,category). 프로모션 유형',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotions',
  @level2type=N'COLUMN', @level2name=N'type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(percent,fixed). percent=정률, fixed=정액',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotions',
  @level2type=N'COLUMN', @level2name=N'discount_type';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 할인율(%) 또는 할인금액(원)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotions',
  @level2type=N'COLUMN', @level2name=N'discount_value';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'DECIMAL. 최소 주문금액 조건. NULL=조건 없음',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotions',
  @level2type=N'COLUMN', @level2name=N'min_order_amount';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 프로모션 시작일',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotions',
  @level2type=N'COLUMN', @level2name=N'started_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 프로모션 종료일',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotions',
  @level2type=N'COLUMN', @level2name=N'ended_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 활성=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotions',
  @level2type=N'COLUMN', @level2name=N'is_active';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 등록 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'promotions',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 직원 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'staff',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'FK→staff(id). 상위 관리자(Self-Join). NULL=최상위',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'staff',
  @level2type=N'COLUMN', @level2name=N'manager_id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'UNIQUE. staffN@techshop-staff.kr 형식. 직원 이메일',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'staff',
  @level2type=N'COLUMN', @level2name=N'email';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 직원 이름',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'staff',
  @level2type=N'COLUMN', @level2name=N'name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 연락처',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'staff',
  @level2type=N'COLUMN', @level2name=N'phone';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(sales,logistics,CS,marketing,dev,management). 부서',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'staff',
  @level2type=N'COLUMN', @level2name=N'department';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(admin,manager,staff). 역할',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'staff',
  @level2type=N'COLUMN', @level2name=N'role';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 재직=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'staff',
  @level2type=N'COLUMN', @level2name=N'is_active';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD. 입사일',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'staff',
  @level2type=N'COLUMN', @level2name=N'hired_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 레코드 생성 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'staff',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 공급업체 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'suppliers',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 회사명',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'suppliers',
  @level2type=N'COLUMN', @level2name=N'company_name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 사업자등록번호(가상 번호)',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'suppliers',
  @level2type=N'COLUMN', @level2name=N'business_number';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 담당자명',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'suppliers',
  @level2type=N'COLUMN', @level2name=N'contact_name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 020-XXXX-XXXX 형식. 연락처',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'suppliers',
  @level2type=N'COLUMN', @level2name=N'phone';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'NOT NULL. 담당자 이메일',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'suppliers',
  @level2type=N'COLUMN', @level2name=N'email';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'사업장 주소. NULL=미등록',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'suppliers',
  @level2type=N'COLUMN', @level2name=N'address';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'0/1. 거래 활성=1',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'suppliers',
  @level2type=N'COLUMN', @level2name=N'is_active';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 등록 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'suppliers',
  @level2type=N'COLUMN', @level2name=N'created_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'YYYY-MM-DD HH:MM:SS. 최종 수정 일시',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'suppliers',
  @level2type=N'COLUMN', @level2name=N'updated_at';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'PK. 자동증가. 태그 식별자',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'tags',
  @level2type=N'COLUMN', @level2name=N'id';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'UNIQUE. NOT NULL. 태그명',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'tags',
  @level2type=N'COLUMN', @level2name=N'name';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'ENUM(feature,use_case,target,spec). 태그 분류',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'tags',
  @level2type=N'COLUMN', @level2name=N'category';
"""

class SQLServerExporter:
    """Export generated data to SQL Server-compatible SQL files."""

    def __init__(self, output_dir: str):
        self.output_dir = os.path.join(output_dir, "sqlserver")
        os.makedirs(self.output_dir, exist_ok=True)

    def export(self, data: dict[str, list[dict]]) -> str:
        """Export all data to SQL Server SQL files."""
        schema_path = os.path.join(self.output_dir, "schema.sql")
        data_path = os.path.join(self.output_dir, "data.sql")
        proc_path = os.path.join(self.output_dir, "procedures.sql")

        # Write schema DDL
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write(SCHEMA_SQL)

        # Write data
        with open(data_path, "w", encoding="utf-8") as f:
            f.write("-- =============================================\n")
            f.write("-- E-commerce Test Data - SQL Server\n")
            f.write("-- =============================================\n\n")
            f.write("USE ecommerce;\nGO\n\n")
            f.write("-- Disable FK checks during bulk load\n")
            f.write("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL';\nGO\n\n")

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

            f.write("\n-- Re-enable FK checks\n")
            f.write("EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL';\nGO\n")

        # Write stored procedures
        with open(proc_path, "w", encoding="utf-8") as f:
            f.write(PROCEDURES_SQL)

        # Write comments
        comments_path = os.path.join(self.output_dir, "comments.sql")
        with open(comments_path, "w", encoding="utf-8") as f:
            f.write(COMMENTS_SQL)

        return self.output_dir

    def _write_inserts(self, f, table: str, rows: list[dict]):
        """Write batched INSERT statements (1000 rows per statement)."""
        if not rows:
            return

        columns = list(rows[0].keys())
        col_names = ", ".join(f"[{c}]" for c in columns)
        batch_size = 1000
        has_identity = table in _IDENTITY_TABLES

        f.write(f"-- {table}: {len(rows)} rows\n")

        if has_identity:
            f.write(f"SET IDENTITY_INSERT [{table}] ON;\nGO\n")

        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            f.write(f"INSERT INTO [{table}] ({col_names}) VALUES\n")

            value_lines = []
            for row in batch:
                vals = []
                for col in columns:
                    v = row[col]
                    vals.append(self._format_value(table, col, v))
                value_lines.append(f"({', '.join(vals)})")

            f.write(",\n".join(value_lines))
            f.write(";\nGO\n\n")

        if has_identity:
            f.write(f"SET IDENTITY_INSERT [{table}] OFF;\nGO\n\n")

    def _format_value(self, table: str, column: str, value: Any) -> str:
        """Format a Python value as a SQL Server literal."""
        if value is None:
            return "NULL"

        key = f"{table}.{column}"

        if key in _BOOL_COLUMNS:
            return "1" if value else "0"

        if isinstance(value, bool):
            return "1" if value else "0"

        if isinstance(value, (int, float)):
            return str(value)

        # String value - escape for SQL Server (double single quotes)
        s = str(value)
        s = s.replace("'", "''")
        return f"N'{s}'"
