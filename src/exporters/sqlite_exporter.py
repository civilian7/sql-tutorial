"""SQLite3 database exporter"""

from __future__ import annotations

import os
import sqlite3
from typing import Any


SCHEMA_SQL = """
-- =============================================
-- Product categories (hierarchical: top > mid > sub)
-- =============================================
CREATE TABLE categories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id       INTEGER NULL REFERENCES categories(id),  -- parent category (NULL=root)
    name            TEXT NOT NULL,                           -- category name
    slug            TEXT NOT NULL UNIQUE,                    -- URL-safe identifier
    depth           INTEGER NOT NULL DEFAULT 0,              -- 0=top, 1=mid, 2=sub
    sort_order      INTEGER NOT NULL DEFAULT 0,              -- display order
    is_active       INTEGER NOT NULL DEFAULT 1,              -- active flag (0/1)
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- Suppliers (product vendors)
-- =============================================
CREATE TABLE suppliers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name    TEXT NOT NULL,                           -- company name
    business_number TEXT NOT NULL,                           -- business registration number (fictional)
    contact_name    TEXT NOT NULL,                           -- contact person
    phone           TEXT NOT NULL,                           -- 020-XXXX-XXXX (fictional number)
    email           TEXT NOT NULL,                           -- contact@xxx.test.kr
    address         TEXT,                                    -- business address
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- Products (computers & peripherals)
-- =============================================
CREATE TABLE products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id     INTEGER NOT NULL REFERENCES categories(id),
    supplier_id     INTEGER NOT NULL REFERENCES suppliers(id),
    successor_id    INTEGER NULL REFERENCES products(id),   -- next-generation replacement product
    name            TEXT NOT NULL,                           -- product name
    sku             TEXT NOT NULL UNIQUE,                    -- stock keeping unit (e.g. LA-GEN-Samsung-00001)
    brand           TEXT NOT NULL,                           -- brand name
    model_number    TEXT,                                    -- model number
    description     TEXT,                                    -- product description
    specs           TEXT NULL,                               -- JSON product specifications
    price           REAL NOT NULL CHECK(price >= 0),           -- current selling price (KRW)
    cost_price      REAL NOT NULL CHECK(cost_price >= 0),    -- cost price (KRW)
    stock_qty  INTEGER NOT NULL DEFAULT 0,              -- current stock quantity
    weight_grams    INTEGER,                                 -- shipping weight (g)
    is_active       INTEGER NOT NULL DEFAULT 1,              -- on sale flag
    discontinued_at TEXT NULL,                               -- discontinuation date (NULL=active)
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- Product images (1~5 per product)
-- =============================================
CREATE TABLE product_images (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    image_url       TEXT NOT NULL,                           -- image path/URL
    file_name       TEXT NOT NULL,                           -- filename (e.g. 42_1.jpg)
    image_type      TEXT NOT NULL,                           -- main/angle/side/back/detail/package/lifestyle/accessory/size_comparison
    alt_text        TEXT,                                    -- alt text
    width           INTEGER,                                 -- image width (px)
    height          INTEGER,                                 -- image height (px)
    file_size       INTEGER,                                 -- file size (bytes, after download)
    sort_order      INTEGER NOT NULL DEFAULT 1,              -- display order
    is_primary      INTEGER NOT NULL DEFAULT 0,              -- primary image flag
    created_at      TEXT NOT NULL
);

-- =============================================
-- Product price history (price change tracking)
-- =============================================
CREATE TABLE product_prices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    price           REAL NOT NULL,                           -- selling price for this period
    started_at      TEXT NOT NULL,                           -- effective start date
    ended_at        TEXT NULL,                               -- effective end date (NULL=current)
    change_reason   TEXT                                     -- regular/promotion/price_drop/cost_increase
);

-- =============================================
-- Customers
-- =============================================
CREATE TABLE customers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email           TEXT NOT NULL UNIQUE,                    -- email (fictional domain)
    password_hash   TEXT NOT NULL,                           -- SHA-256 hash (fictional)
    name            TEXT NOT NULL,                           -- customer name
    phone           TEXT NOT NULL,                           -- 020-XXXX-XXXX (fictional number)
    birth_date      TEXT NULL,                               -- birth date (YYYY-MM-DD, ~15% NULL)
    gender          TEXT NULL,                               -- M/F (NULL ~10%, male 65%)
    grade           TEXT NOT NULL DEFAULT 'BRONZE' CHECK(grade IN ('BRONZE','SILVER','GOLD','VIP')),
    point_balance   INTEGER NOT NULL DEFAULT 0 CHECK(point_balance >= 0),
    acquisition_channel TEXT NULL,                            -- organic/search_ad/social/referral/direct
    is_active       INTEGER NOT NULL DEFAULT 1,              -- active status (0=deactivated)
    last_login_at   TEXT NULL,                               -- last login (NULL=never logged in)
    created_at      TEXT NOT NULL,                           -- signup date
    updated_at      TEXT NOT NULL
);

-- =============================================
-- Customer addresses (1~3 per customer)
-- =============================================
CREATE TABLE customer_addresses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    label           TEXT NOT NULL,                           -- home/office/other
    recipient_name  TEXT NOT NULL,                           -- recipient
    phone           TEXT NOT NULL,                           -- recipient phone
    zip_code        TEXT NOT NULL,                           -- postal code
    address1        TEXT NOT NULL,                           -- base address
    address2        TEXT,                                    -- detailed address
    is_default      INTEGER NOT NULL DEFAULT 0,              -- default address flag
    created_at      TEXT NOT NULL,
    updated_at      TEXT NULL                                -- address change date
);

-- =============================================
-- Staff / administrators
-- =============================================
CREATE TABLE staff (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id      INTEGER NULL REFERENCES staff(id),      -- supervisor (Self-Join / recursive CTE)
    email           TEXT NOT NULL UNIQUE,                    -- staffN@techshop-staff.kr
    name            TEXT NOT NULL,
    phone           TEXT NOT NULL,
    department      TEXT NOT NULL,                           -- sales/logistics/CS/marketing/dev/management
    role            TEXT NOT NULL,                           -- admin/manager/staff
    is_active       INTEGER NOT NULL DEFAULT 1,
    hired_at        TEXT NOT NULL,                           -- hire date
    created_at      TEXT NOT NULL
);

-- =============================================
-- Orders
-- =============================================
CREATE TABLE orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number    TEXT NOT NULL UNIQUE,                    -- ORD-YYYYMMDD-NNNNN
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    address_id      INTEGER NOT NULL REFERENCES customer_addresses(id),
    staff_id        INTEGER NULL REFERENCES staff(id),      -- CS agent (for cancellations/returns)
    status          TEXT NOT NULL,                           -- pending/paid/preparing/shipped/delivered/confirmed/cancelled/return_requested/returned
    total_amount    REAL NOT NULL,                           -- final payment amount
    discount_amount REAL NOT NULL DEFAULT 0,                 -- total discount
    shipping_fee    REAL NOT NULL DEFAULT 0,                 -- shipping fee (free over 50,000 KRW)
    point_used      INTEGER NOT NULL DEFAULT 0,              -- points used
    point_earned    INTEGER NOT NULL DEFAULT 0,              -- points to be earned
    notes           TEXT NULL,                               -- delivery memo (~35%)
    ordered_at      TEXT NOT NULL,                           -- order datetime
    completed_at    TEXT NULL,                               -- purchase confirmation date
    cancelled_at    TEXT NULL,                               -- cancellation date
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- Order items (1~5 items per order)
-- =============================================
CREATE TABLE order_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    product_id      INTEGER NOT NULL REFERENCES products(id),
    quantity        INTEGER NOT NULL CHECK(quantity > 0),     -- quantity
    unit_price      REAL NOT NULL CHECK(unit_price >= 0),    -- unit price at order time
    discount_amount REAL NOT NULL DEFAULT 0,                 -- item discount
    subtotal        REAL NOT NULL                            -- (unit_price x quantity) - discount
);

-- =============================================
-- Payments
-- card: issuer/approval number/installment
-- bank_transfer: bank/depositor name
-- virtual_account: bank/virtual account number
-- kakao_pay/naver_pay: easy payment sub-method
-- point: full point payment
-- =============================================
CREATE TABLE payments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    method          TEXT NOT NULL,                           -- card/bank_transfer/virtual_account/kakao_pay/naver_pay/point
    amount          REAL NOT NULL CHECK(amount >= 0),         -- payment amount
    status          TEXT NOT NULL CHECK(status IN ('pending','completed','failed','refunded')),
    pg_transaction_id TEXT NULL,                             -- PG transaction ID (fictional)
    card_issuer     TEXT NULL,                               -- card issuer (Shinhan/Samsung/KB/Hyundai/Lotte/Hana/Woori/NH/BC)
    card_approval_no TEXT NULL,                              -- card approval number (8 digits)
    installment_months INTEGER NULL,                         -- installment months (0=lump sum)
    bank_name       TEXT NULL,                               -- bank name (bank transfer/virtual account)
    account_no      TEXT NULL,                               -- virtual account number
    depositor_name  TEXT NULL,                               -- depositor name (bank transfer)
    easy_pay_method TEXT NULL,                               -- easy payment sub-method (KakaoPay balance/linked card, etc.)
    receipt_type    TEXT NULL,                               -- income deduction/expense proof (cash receipt)
    receipt_no      TEXT NULL,                               -- cash receipt number
    paid_at         TEXT NULL,                               -- payment completion time
    refunded_at     TEXT NULL,                               -- refund time
    created_at      TEXT NOT NULL
);

-- =============================================
-- Shipping (outbound delivery)
-- =============================================
CREATE TABLE shipping (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    carrier         TEXT NOT NULL,                           -- CJ Logistics/Hanjin/Logen/Korea Post
    tracking_number TEXT NULL,                               -- tracking number
    status          TEXT NOT NULL,                           -- preparing/shipped/in_transit/delivered/returned
    shipped_at      TEXT NULL,                               -- ship date
    delivered_at    TEXT NULL,                               -- delivery date (must be after shipped_at)
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- Product reviews (~25% of confirmed orders)
-- =============================================
CREATE TABLE reviews (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    rating          INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),  -- 1~5 stars (5=40%, 1=5%)
    title           TEXT NULL,                               -- review title (~80%)
    content         TEXT NULL,                               -- review body
    is_verified     INTEGER NOT NULL DEFAULT 1,              -- verified purchase flag
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- Inventory transactions (stock change tracking)
-- =============================================
CREATE TABLE inventory_transactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    type            TEXT NOT NULL,                           -- inbound/outbound/return/adjustment
    quantity        INTEGER NOT NULL,                        -- positive=inbound, negative=outbound
    reference_id    INTEGER NULL,                            -- related order ID
    notes           TEXT NULL,                               -- initial_stock/regular_inbound/return_inbound
    created_at      TEXT NOT NULL
);

-- =============================================
-- Shopping carts
-- =============================================
CREATE TABLE carts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    status          TEXT NOT NULL DEFAULT 'active',          -- active/converted/abandoned
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- =============================================
-- Cart items
-- =============================================
CREATE TABLE cart_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id         INTEGER NOT NULL REFERENCES carts(id),
    product_id      INTEGER NOT NULL REFERENCES products(id),
    quantity        INTEGER NOT NULL DEFAULT 1,
    added_at        TEXT NOT NULL
);

-- =============================================
-- Coupons (percent: rate discount, fixed: flat discount)
-- =============================================
CREATE TABLE coupons (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT NOT NULL UNIQUE,                    -- coupon code (CP2401001)
    name            TEXT NOT NULL,                           -- coupon name
    type            TEXT NOT NULL,                           -- percent/fixed
    discount_value  REAL NOT NULL CHECK(discount_value > 0),  -- discount rate (%) or amount (KRW)
    min_order_amount REAL NULL,                              -- minimum order amount
    max_discount    REAL NULL,                               -- max discount amount (percent type)
    usage_limit     INTEGER NULL,                            -- total usage limit
    per_user_limit  INTEGER NOT NULL DEFAULT 1,              -- per-user usage limit
    is_active       INTEGER NOT NULL DEFAULT 1,
    started_at      TEXT NOT NULL,                           -- validity start
    expired_at      TEXT NOT NULL,                           -- validity end
    created_at      TEXT NOT NULL
);

-- =============================================
-- Coupon usage history
-- =============================================
CREATE TABLE coupon_usage (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_id       INTEGER NOT NULL REFERENCES coupons(id),
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    discount_amount REAL NOT NULL,                           -- actual discount amount
    used_at         TEXT NOT NULL
);

-- =============================================
-- Customer inquiries/complaints (CS)
-- =============================================
CREATE TABLE complaints (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NULL REFERENCES orders(id),     -- order-related inquiry (NULL=general)
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    staff_id        INTEGER NULL REFERENCES staff(id),      -- assigned CS agent
    category        TEXT NOT NULL,                           -- product_defect/delivery_issue/wrong_item/refund_request/exchange_request/general_inquiry/price_inquiry
    channel         TEXT NOT NULL,                           -- website/phone/email/chat/kakao
    priority        TEXT NOT NULL,                           -- low/medium/high/urgent
    status          TEXT NOT NULL,                           -- open/resolved/closed
    title           TEXT NOT NULL,                           -- inquiry title
    content         TEXT NOT NULL,                           -- inquiry content
    resolution      TEXT NULL,                               -- resolution detail (when resolved)
    type            TEXT NOT NULL DEFAULT 'inquiry',         -- inquiry/claim/report
    sub_category    TEXT NULL,                               -- detailed category (e.g., initial_defect/in_use_damage/misdelivery)
    compensation_type TEXT NULL,                             -- refund/exchange/partial_refund/point_compensation/none
    compensation_amount REAL NULL DEFAULT 0,                 -- compensation amount
    escalated       INTEGER NOT NULL DEFAULT 0,             -- escalated to supervisor (0/1)
    response_count  INTEGER NOT NULL DEFAULT 1,             -- number of back-and-forth responses
    created_at      TEXT NOT NULL,                           -- submitted date
    resolved_at     TEXT NULL,                               -- resolved date
    closed_at       TEXT NULL                                -- closed date
);

-- =============================================
-- Returns/exchanges (reverse logistics + inspection + refund tracking)
-- =============================================
CREATE TABLE returns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    return_type     TEXT NOT NULL,                           -- refund/exchange
    reason          TEXT NOT NULL,                           -- defective/wrong_item/change_of_mind/damaged_in_transit/not_as_described/late_delivery
    reason_detail   TEXT NOT NULL,                           -- detailed reason description
    status          TEXT NOT NULL,                           -- requested/pickup_scheduled/in_transit/completed
    is_partial      INTEGER NOT NULL DEFAULT 0,              -- partial return flag (~17%)
    refund_amount   REAL NOT NULL,                           -- refund amount
    refund_status   TEXT NOT NULL,                           -- pending/refunded/exchanged/partial_refund
    carrier         TEXT NOT NULL,                           -- pickup carrier
    tracking_number TEXT NOT NULL,                           -- pickup tracking number
    requested_at    TEXT NOT NULL,                           -- return request date
    pickup_at       TEXT NOT NULL,                           -- pickup scheduled/completed date
    received_at     TEXT NULL,                               -- warehouse receipt date
    inspected_at    TEXT NULL,                               -- inspection completion date
    inspection_result TEXT NULL,                             -- good/opened_good/defective/unsellable
    completed_at    TEXT NULL,                               -- processing completion date
    claim_id        INTEGER NULL REFERENCES complaints(id), -- linked claim (if return originated from CS)
    exchange_product_id INTEGER NULL REFERENCES products(id), -- replacement product for exchanges
    restocking_fee  REAL NOT NULL DEFAULT 0,                 -- change-of-mind restocking fee
    created_at      TEXT NOT NULL
);

-- =============================================
-- Wishlists (M:N: customers ↔ products)
-- =============================================
CREATE TABLE wishlists (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    product_id      INTEGER NOT NULL REFERENCES products(id),
    is_purchased    INTEGER NOT NULL DEFAULT 0,              -- converted to purchase flag (0/1)
    notify_on_sale  INTEGER NOT NULL DEFAULT 0,              -- price drop notification (0/1)
    created_at      TEXT NOT NULL,
    UNIQUE(customer_id, product_id)                          -- prevent duplicate customer-product pairs
);

-- =============================================
-- Date dimension table (for CROSS JOIN practice)
-- =============================================
CREATE TABLE calendar (
    date_key        TEXT PRIMARY KEY,                        -- YYYY-MM-DD
    year            INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    day             INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,                        -- 1~4
    day_of_week     INTEGER NOT NULL,                        -- 0=Mon ~ 6=Sun
    day_name        TEXT NOT NULL,                           -- Monday~Sunday
    is_weekend      INTEGER NOT NULL DEFAULT 0,              -- Sat/Sun = 1
    is_holiday      INTEGER NOT NULL DEFAULT 0,              -- public holiday = 1
    holiday_name    TEXT NULL                                -- holiday name
);

-- =============================================
-- Customer grade change history (for SCD Type 2 practice)
-- =============================================
CREATE TABLE customer_grade_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    old_grade       TEXT NULL,                               -- previous grade (NULL on initial signup)
    new_grade       TEXT NOT NULL,                           -- new grade
    changed_at      TEXT NOT NULL,                           -- change datetime
    reason          TEXT NOT NULL                            -- signup/upgrade/downgrade/yearly_review
);

-- =============================================
-- Tags (product tags, for M:N practice)
-- =============================================
CREATE TABLE tags (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    category        TEXT NOT NULL                            -- feature/use_case/target/spec
);

CREATE TABLE product_tags (
    product_id      INTEGER NOT NULL REFERENCES products(id),
    tag_id          INTEGER NOT NULL REFERENCES tags(id),
    PRIMARY KEY (product_id, tag_id)
);

-- =============================================
-- Product view logs (for funnel/session/cohort analysis)
-- =============================================
CREATE TABLE product_views (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    product_id      INTEGER NOT NULL REFERENCES products(id),
    referrer_source TEXT NOT NULL,                           -- direct/search/ad/recommendation/social/email
    device_type     TEXT NOT NULL,                           -- desktop/mobile/tablet
    duration_seconds INTEGER NOT NULL,                       -- page dwell time (seconds)
    viewed_at       TEXT NOT NULL
);

-- =============================================
-- Point transactions (earn/use/expire)
-- =============================================
CREATE TABLE point_transactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    order_id        INTEGER NULL REFERENCES orders(id),
    type            TEXT NOT NULL,                           -- earn/use/expire
    reason          TEXT NOT NULL,                           -- purchase/confirm/review/signup/use/expiry
    amount          INTEGER NOT NULL,                        -- + for earn, - for use/expire
    balance_after   INTEGER NOT NULL,                        -- running balance after this transaction
    expires_at      TEXT NULL,                               -- expiry date for earn transactions
    created_at      TEXT NOT NULL
);

-- =============================================
-- Promotions / sale events
-- =============================================
CREATE TABLE promotions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    type            TEXT NOT NULL,                           -- seasonal/flash/category
    discount_type   TEXT NOT NULL,                           -- percent/fixed
    discount_value  REAL NOT NULL,
    min_order_amount REAL NULL,
    started_at      TEXT NOT NULL,
    ended_at        TEXT NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL
);

CREATE TABLE promotion_products (
    promotion_id    INTEGER NOT NULL REFERENCES promotions(id),
    product_id      INTEGER NOT NULL REFERENCES products(id),
    override_price  REAL NULL,                               -- flash sale special price (NULL = use promotion discount)
    PRIMARY KEY (promotion_id, product_id)
);

-- =============================================
-- Product Q&A (Self-Join: parent_id)
-- =============================================
CREATE TABLE product_qna (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    customer_id     INTEGER NULL REFERENCES customers(id),   -- NULL for staff answers
    staff_id        INTEGER NULL REFERENCES staff(id),       -- NULL for customer questions
    parent_id       INTEGER NULL REFERENCES product_qna(id), -- self-join: answer→question
    content         TEXT NOT NULL,
    is_answered     INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL
);
"""

INDEX_SQL = """
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_supplier_id ON products(supplier_id);
CREATE INDEX idx_products_successor_id ON products(successor_id);
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
CREATE INDEX idx_complaints_type ON complaints(type);
CREATE INDEX idx_returns_claim_id ON returns(claim_id);
CREATE INDEX idx_returns_exchange_product_id ON returns(exchange_product_id);
CREATE INDEX idx_wishlists_customer_id ON wishlists(customer_id);
CREATE INDEX idx_wishlists_product_id ON wishlists(product_id);
CREATE INDEX idx_staff_manager_id ON staff(manager_id);
CREATE INDEX idx_calendar_year_month ON calendar(year, month);
CREATE INDEX idx_grade_history_customer_id ON customer_grade_history(customer_id);
CREATE INDEX idx_grade_history_changed_at ON customer_grade_history(changed_at);
CREATE INDEX idx_product_tags_tag_id ON product_tags(tag_id);
CREATE INDEX idx_product_views_customer_id ON product_views(customer_id);
CREATE INDEX idx_product_views_product_id ON product_views(product_id);
CREATE INDEX idx_product_views_viewed_at ON product_views(viewed_at);
CREATE INDEX idx_product_views_customer_product ON product_views(customer_id, product_id);
CREATE INDEX idx_point_tx_customer_id ON point_transactions(customer_id);
CREATE INDEX idx_point_tx_order_id ON point_transactions(order_id);
CREATE INDEX idx_point_tx_type ON point_transactions(type);
CREATE INDEX idx_point_tx_created_at ON point_transactions(created_at);
CREATE INDEX idx_promotions_type ON promotions(type);
CREATE INDEX idx_promotions_dates ON promotions(started_at, ended_at);
CREATE INDEX idx_promo_products_product_id ON promotion_products(product_id);
CREATE INDEX idx_qna_product_id ON product_qna(product_id);
CREATE INDEX idx_qna_customer_id ON product_qna(customer_id);
CREATE INDEX idx_qna_parent_id ON product_qna(parent_id);
"""

TRIGGER_SQL = """
-- =============================================
-- TRIGGER: Auto-deduct stock on order item insert
-- Learning: AFTER INSERT trigger, UPDATE with NEW reference
-- =============================================
CREATE TRIGGER trg_deduct_stock AFTER INSERT ON order_items
BEGIN
    UPDATE products
    SET stock_qty = MAX(0, stock_qty - NEW.quantity)
    WHERE id = NEW.product_id;
END;

-- =============================================
-- TRIGGER: Auto-update review count/avg on review insert
-- Learning: Correlated UPDATE with subquery in trigger
-- =============================================
-- Note: This trigger references a hypothetical review_count/avg_rating
-- column. It is provided as a learning example, not applied to the schema.
-- CREATE TRIGGER trg_update_review_stats AFTER INSERT ON reviews
-- BEGIN
--     UPDATE products
--     SET review_count = (SELECT COUNT(*) FROM reviews WHERE product_id = NEW.product_id),
--         avg_rating = (SELECT ROUND(AVG(rating), 1) FROM reviews WHERE product_id = NEW.product_id)
--     WHERE id = NEW.product_id;
-- END;

-- =============================================
-- TRIGGER: Prevent negative point balance
-- Learning: BEFORE UPDATE trigger with RAISE for validation
-- =============================================
CREATE TRIGGER trg_prevent_negative_balance BEFORE UPDATE OF point_balance ON customers
WHEN NEW.point_balance < 0
BEGIN
    SELECT RAISE(ABORT, 'Point balance cannot be negative');
END;

-- =============================================
-- TRIGGER: Log grade changes automatically
-- Learning: AFTER UPDATE trigger, conditional INSERT
-- =============================================
CREATE TRIGGER trg_log_grade_change AFTER UPDATE OF grade ON customers
WHEN OLD.grade != NEW.grade
BEGIN
    INSERT INTO customer_grade_history (customer_id, old_grade, new_grade, changed_at, reason)
    VALUES (NEW.id, OLD.grade, NEW.grade, datetime('now'), 'auto_trigger');
END;
"""

VIEW_SQL = """
-- =============================================
-- VIEW: Monthly sales summary
-- Learning: GROUP BY, date functions, aggregates, ORDER BY
-- =============================================
CREATE VIEW v_monthly_sales AS
SELECT
    SUBSTR(o.ordered_at, 1, 7) AS month,               -- YYYY-MM
    COUNT(DISTINCT o.id) AS order_count,                -- number of orders
    COUNT(DISTINCT o.customer_id) AS customer_count,    -- unique buyers
    CAST(SUM(o.total_amount) AS INTEGER) AS revenue,    -- total revenue
    CAST(AVG(o.total_amount) AS INTEGER) AS avg_order,  -- average order value
    SUM(o.discount_amount) AS total_discount            -- total discount
FROM orders o
WHERE o.status NOT IN ('cancelled')
GROUP BY SUBSTR(o.ordered_at, 1, 7)
ORDER BY month;

-- =============================================
-- VIEW: Customer summary (lifetime value)
-- Learning: LEFT JOIN, COALESCE, CASE, subquery, aggregates
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
-- VIEW: Product performance (sales, reviews, inventory)
-- Learning: multiple LEFT JOINs, window function data source
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
-- VIEW: Category tree (recursive CTE example)
-- Learning: Recursive CTE, string concatenation, hierarchy traversal
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
-- VIEW: Daily order statistics
-- Learning: date handling, multiple aggregates, CASE
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
-- VIEW: Payment method statistics
-- Learning: CASE pivot, ratio calculation, string functions
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
-- VIEW: Order detail (denormalized for queries)
-- Learning: multi-table JOIN (5 tables), NULL handling
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
-- VIEW: Revenue growth (month-over-month)
-- Learning: LAG window function, ROUND, ratio calculation
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
-- VIEW: Top products by category revenue rank
-- Learning: ROW_NUMBER, PARTITION BY, multi-table JOIN
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
-- VIEW: Customer RFM analysis (marketing segmentation)
-- Learning: NTILE window function, CASE, date calculation, CTE
-- Recency x Frequency x Monetary
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
        NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,   -- more recent = higher score
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
-- VIEW: Cart abandonment analysis
-- Learning: LEFT JOIN + IS NULL, aggregates, potential revenue
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
-- VIEW: Supplier performance
-- Learning: multiple aggregates, HAVING, ratio calculation
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
-- VIEW: Hourly order patterns
-- Learning: CAST, string extraction, pivot-style aggregation
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
-- VIEW: Product ABC analysis (Pareto / 80-20 rule)
-- Learning: cumulative SUM OVER, ratio calculation, CASE classification
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
-- VIEW: CS staff workload
-- Learning: multiple LEFT JOINs, average resolution time
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
-- VIEW: Coupon effectiveness analysis
-- Learning: JOIN + aggregates, ROI calculation, ratios
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
-- VIEW: Return reason analysis
-- Learning: GROUP BY + CASE pivot, ratio calculation
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
-- VIEW: Yearly KPI dashboard
-- Learning: multiple subqueries, combined aggregates, business metrics
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
-- TRIGGER: Auto-update updated_at on order status change
-- Learning: AFTER UPDATE trigger, NEW/OLD reference, datetime function
-- =============================================
CREATE TRIGGER trg_orders_updated_at
AFTER UPDATE OF status ON orders
BEGIN
    UPDATE orders SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- =============================================
-- TRIGGER: Auto-update updated_at on review modification
-- =============================================
CREATE TRIGGER trg_reviews_updated_at
AFTER UPDATE OF rating, title, content ON reviews
BEGIN
    UPDATE reviews SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- =============================================
-- TRIGGER: Auto-insert price history on product price change
-- Learning: BEFORE UPDATE, history table automation
-- =============================================
CREATE TRIGGER trg_product_price_history
AFTER UPDATE OF price ON products
WHEN OLD.price != NEW.price
BEGIN
    -- Close existing history record
    UPDATE product_prices
    SET ended_at = datetime('now')
    WHERE product_id = NEW.id AND ended_at IS NULL;

    -- Insert new history record
    INSERT INTO product_prices (product_id, price, started_at, ended_at, change_reason)
    VALUES (NEW.id, NEW.price, datetime('now'), NULL, 'price_update');
END;

-- =============================================
-- TRIGGER: Auto-update updated_at on product modification
-- =============================================
CREATE TRIGGER trg_products_updated_at
AFTER UPDATE ON products
BEGIN
    UPDATE products SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- =============================================
-- TRIGGER: Auto-update updated_at on customer modification
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
        self.db_path = os.path.join(output_dir, "ecommerce.db")

    def export(self, data: dict[str, list[dict]]) -> str:
        """Export all data to a SQLite database."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=OFF")
        # Disable FK during bulk insert (self-referencing FKs like products.successor_id)
        conn.execute("PRAGMA foreign_keys=OFF")

        # Create schema
        conn.executescript(SCHEMA_SQL)

        # Insert data (table order respects FK dependencies)
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
            self._insert_rows(conn, table, rows)

        # Re-enable FK and verify integrity
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript(INDEX_SQL)

        # Create views
        conn.executescript(VIEW_SQL)

        # Create triggers
        conn.executescript(TRIGGER_SQL)

        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("VACUUM")
        conn.close()

        return self.db_path

    def _insert_rows(self, conn: sqlite3.Connection, table: str, rows: list[dict]):
        """Perform batch INSERT."""
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
