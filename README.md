**[한국어](README.ko.md)** | English

# E-Commerce Test Database Generator

A Python tool that generates **realistic test databases** for an online computer & peripherals store. Designed for SQL learners who want to practice with well-structured, production-like data.

> **Why this project?** One of the biggest challenges for beginner/intermediate developers learning databases is the lack of access to well-designed, realistic databases. This generator creates a complete e-commerce database with 10 years of business data, realistic patterns, and proper schema design.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
```

### Generate with Korean Data

```bash
# Small (230K rows, ~29MB, ~9 sec)
python generate.py --size small

# Medium (2M rows, ~250MB, ~2 min) — default
python generate.py --size medium

# Large (10M rows, ~1.2GB, ~10 min)
python generate.py --size large
```

### Generate with English Data

```bash
# Small
python generate.py --size small --locale en

# Medium
python generate.py --size medium --locale en

# Large
python generate.py --size large --locale en
```

Output: `output/tutorial.db` (SQLite)

### Browse the Tutorial Docs

The tutorial documentation is built with MkDocs Material and can be previewed locally.

```bash
# Korean tutorial (http://localhost:8001)
serve.bat

# English tutorial
serve.bat en
```

Or run directly:

```bash
cd docs
mkdocs serve -f mkdocs-en.yml -a localhost:8001
```

Changes to files are auto-reloaded in the browser.

### Tutorial Contents

**Lessons (21)**

| Level | # | Topic |
|-------|---|-------|
| Beginner | 01 | SELECT Basics |
| | 02 | Filtering with WHERE |
| | 03 | Sorting & Limiting |
| | 04 | Aggregate Functions |
| | 05 | GROUP BY & HAVING |
| | 06 | NULL Handling |
| Intermediate | 07 | INNER JOIN |
| | 08 | LEFT JOIN & Outer Joins |
| | 09 | Subqueries |
| | 10 | CASE Expressions |
| | 11 | Date & Time Functions |
| | 12 | String Functions |
| | 13 | UNION & Set Operations |
| | 14 | INSERT, UPDATE, DELETE |
| | 21 | SELF JOIN & CROSS JOIN |
| Advanced | 15 | Window Functions |
| | 16 | CTE & Recursive CTE |
| | 17 | EXISTS & Correlated Subqueries |
| | 18 | Views |
| | 19 | Indexes & Performance |
| | 20 | Triggers |

**Exercises (136 problems)**

| Level | Exercise | Problems |
|-------|----------|----------|
| Beginner | Product Exploration | 15 |
| | Customer Analysis | 15 |
| | Order Basics | 15 |
| Intermediate | JOIN Master | 12 |
| | Date & Time Analysis | 12 |
| | Subqueries & Transformation | 12 |
| | Constraints in Action | 10 |
| | Transactions | 7 |
| Advanced | Sales Analysis | 6 |
| | Customer Segmentation | 6 |
| | Inventory Management | 6 |
| | CS Performance | 6 |
| | Real-World SQL Patterns | 6 |
| | Understanding Normalization | 8 |

**Reference**

- DB Dialect Comparison (SQLite / MySQL / PostgreSQL / SQL Server / Oracle)

## Features

- **21 tables** with proper foreign keys, CHECK constraints, and indexes
- **18 views** demonstrating real-world SQL patterns (window functions, CTEs, RFM analysis, etc.)
- **5 triggers** for automatic timestamp updates and price history tracking
- **Stored procedures** for MySQL and PostgreSQL (in `sql/` directory)
- **Multi-locale support**: Korean (`ko`) and English (`en`), extensible to other languages
- **Realistic data patterns**:
  - 10-year business growth curve (2016-2025)
  - Seasonal order patterns (Black Friday peaks, summer lows)
  - Time-of-day order distribution (evening peaks, dawn lows)
  - Pareto customer distribution (top 20% = 60% of orders)
  - Dormant/churned customer modeling
  - Price-weighted product selection (cheaper items sell more)

## Command Line Options

```
python generate.py [OPTIONS]

--size {small,medium,large}    Data scale (default: medium)
--locale {ko,en}               Data language (default: ko)
--seed NUMBER                  Random seed for reproducibility (default: 42)
--target {sqlite,...}          Target database (default: sqlite)
--all                          Generate for all database targets
--download-images              Download real product photos via Pexels API
--pexels-key KEY               Pexels API key (or set PEXELS_API_KEY env var)
--config PATH                  Config file path (default: config.yaml)
```

## Data Scale Profiles

| Profile | Scale | Total Rows | File Size | Generation Time | Use Case |
|---------|-------|------------|-----------|-----------------|----------|
| small | 0.1x | ~230K | ~29 MB | ~9 sec | Quick testing, CI |
| medium | 1.0x | ~2M | ~250 MB | ~2 min | General development (default) |
| large | 5.0x | ~10M | ~1.2 GB | ~10 min | Performance testing |

## Schema Overview

### Entity Relationship Diagram

```
categories ──┐
             ├── products ──┬── product_images
suppliers ───┘              ├── product_prices
                            ├── order_items ──── orders ──┬── payments
                            ├── reviews                   ├── shipping
                            ├── wishlists                 ├── returns
                            ├── cart_items ── carts        ├── complaints
                            └── inventory_transactions     └── coupon_usage ── coupons

customers ──┬── customer_addresses
            ├── orders
            ├── reviews
            ├── wishlists (M:N with products)
            ├── carts
            ├── complaints
            └── coupon_usage

staff ──┬── orders (CS assignments)
        └── complaints
```

### Tables (21)

| # | Table | Description | Rows (small) | Key Learning Points |
|---|-------|-------------|-------------|---------------------|
| 1 | `categories` | Product categories (hierarchical) | 53 | Self-referencing FK, recursive CTE |
| 2 | `suppliers` | Vendors/distributors | 50 | 1:N with products |
| 3 | `products` | Computer hardware & peripherals | 280 | Multiple FKs, CHECK constraints |
| 4 | `product_images` | Product photos (1~5 per product) | 748 | 1:N, image types |
| 5 | `product_prices` | Price change history | 814 | Temporal data, SCD Type 2 |
| 6 | `customers` | Registered users | 5,230 | NULL handling, grades, dormancy |
| 7 | `customer_addresses` | Shipping addresses (1~3 per customer) | 8,553 | 1:N, default flag |
| 8 | `staff` | Employees/admins | 5 | Departments, roles |
| 9 | `orders` | Purchase orders | 34,689 | Status machine, timestamps |
| 10 | `order_items` | Order line items | 74,513 | Junction-like, quantity × price |
| 11 | `payments` | Payment transactions | 34,689 | Card/bank/e-wallet details |
| 12 | `shipping` | Delivery tracking | 32,942 | Carrier, status transitions |
| 13 | `reviews` | Product reviews (1-5 stars) | 7,947 | Rating distribution, text |
| 14 | `inventory_transactions` | Stock in/out log | 12,935 | Append-only ledger |
| 15 | `carts` | Shopping carts | 3,000 | Active/converted/abandoned |
| 16 | `cart_items` | Cart line items | 9,172 | Cart → product |
| 17 | `coupons` | Discount coupons | 20 | Percent/fixed, validity period |
| 18 | `coupon_usage` | Coupon redemption history | 172 | 3-way junction |
| 19 | `wishlists` | Wishlist / favorites | 1,998 | **M:N** (customer ↔ product), UNIQUE composite |
| 20 | `returns` | Returns & exchanges | 1,022 | Reverse logistics, inspection |
| 21 | `complaints` | Customer service inquiries | 3,481 | Priority, resolution tracking |

### Views (18)

| View | Description | SQL Concepts Demonstrated |
|------|-------------|--------------------------|
| `v_monthly_sales` | Monthly revenue summary | GROUP BY, date functions, aggregation |
| `v_customer_summary` | Customer lifetime value | LEFT JOIN, COALESCE, CASE, subqueries |
| `v_product_performance` | Product sales metrics | Multiple LEFT JOINs, margin calculation |
| `v_category_tree` | Full category path | **Recursive CTE**, string concatenation |
| `v_daily_orders` | Daily order statistics | Date extraction, CASE pivot |
| `v_payment_summary` | Payment method breakdown | Percentage calculation, aggregation |
| `v_order_detail` | Denormalized order view | 5-table JOIN, NULL handling |
| `v_revenue_growth` | Month-over-month growth | **LAG window function** |
| `v_top_products_by_category` | Ranked products per category | **ROW_NUMBER + PARTITION BY** |
| `v_customer_rfm` | RFM marketing segmentation | **NTILE**, CTE, CASE classification |
| `v_cart_abandonment` | Abandoned cart analysis | LEFT JOIN, potential revenue |
| `v_supplier_performance` | Supplier metrics + return rate | Multiple subquery JOINs |
| `v_hourly_pattern` | Order patterns by hour | Time extraction, CASE grouping |
| `v_product_abc` | ABC / Pareto (80/20) analysis | **Cumulative SUM window function** |
| `v_staff_workload` | CS staff performance | Avg resolution time |
| `v_coupon_effectiveness` | Coupon ROI analysis | ROI calculation |
| `v_return_analysis` | Return reason breakdown | CASE pivot, percentage |
| `v_yearly_kpi` | Annual KPI dashboard | Multi-source subquery JOINs |

### Triggers (5, SQLite)

| Trigger | Event | Action |
|---------|-------|--------|
| `trg_orders_updated_at` | UPDATE status ON orders | Auto-update `updated_at` |
| `trg_reviews_updated_at` | UPDATE ON reviews | Auto-update `updated_at` |
| `trg_product_price_history` | UPDATE price ON products | Auto-insert price history record |
| `trg_products_updated_at` | UPDATE ON products | Auto-update `updated_at` |
| `trg_customers_updated_at` | UPDATE ON customers | Auto-update `updated_at` |

### Stored Procedures (MySQL / PostgreSQL)

Located in `sql/` directory:

| Procedure/Function | Description | Key Concepts |
|-------------------|-------------|--------------|
| `sp_update_customer_grades` | Batch update customer grades | CURSOR, transaction |
| `sp_place_order` / `fn_place_order` | Create order with items | IN/OUT params, LAST_INSERT_ID |
| `sp_monthly_report` / `fn_monthly_report` | Monthly sales report | RETURNS TABLE, date functions |
| `sp_low_stock_alert` / `fn_low_stock_alert` | Low inventory alert | Sales velocity calculation |
| `fn_customer_ltv` | Customer lifetime value | Scalar function |
| `fn_product_rating` | Average product rating | Scalar function |
| `fn_update_timestamp` (PG) | Trigger function | RETURNS TRIGGER |

## Relationship Types

This database covers all major relationship patterns:

| Type | Example | Learning Points |
|------|---------|-----------------|
| **1:1** | orders → payments | One payment per order |
| **1:N** | customers → orders | One customer, many orders |
| **M:N** | customers ↔ products (via wishlists) | UNIQUE composite key |
| **Self-referencing** | categories.parent_id | Hierarchical data |
| **Nullable FK** | orders.staff_id | Optional relationship |

## Constraints

- **10 CHECK constraints**: price >= 0, quantity > 0, rating BETWEEN 1 AND 5, grade IN (...), etc.
- **7 UNIQUE constraints**: email, SKU, order_number, coupon code, slug, (customer_id, product_id)
- **38 indexes**: Covering all foreign keys and common query patterns

## Data Realism

### Business Patterns
- **10-year growth curve**: Startup → Growth → COVID boom → Stabilization
- **Seasonal patterns**: Black Friday +25%, Summer -15%, Back-to-school +15%
- **Time-of-day**: Evening peak (8-10 PM), dawn minimum (2-5 AM)
- **Day-of-week**: Mon/Sat/Sun slightly higher than Wed/Thu

### Customer Behavior
- **Pareto distribution**: Top 5% customers = heavy buyers; bottom 50% = occasional
- **Dormancy model**: Older signups have higher dormancy (5+ years = 45%)
- **Demographics**: Male 65% (computer store), age peak at 30s (33%)
- **Non-purchasers**: ~25% sign up but never order (realistic funnel)

### Data Integrity (verified)
- No orders before customer signup date
- No orders for discontinued products
- No duplicate products within same order
- Delivery date always after ship date
- No reviews on cancelled/returned orders
- Product price matches latest price history record

## Locale System

The generator supports multiple languages via `data/locale/{code}.json`:

| Data | Korean (`ko`) | English (`en`) |
|------|--------------|----------------|
| Customer names | 김민수, 이영희 | Justin Maxwell, Lisa Jones |
| Phone format | 020-XXXX-XXXX | 555-XXXX-XXXX |
| Categories | 데스크톱 PC, 노트북 | Desktop PC, Laptop |
| Carriers | CJ대한통운, 한진택배 | FedEx, UPS, DHL |
| Card issuers | 신한카드, 삼성카드 | Visa, Mastercard |
| Banks | KB국민은행, 신한은행 | Chase, Bank of America |
| E-wallets | 카카오페이, 네이버페이 | PayPal, Apple Pay |
| Reviews/complaints | Korean text | English text |

**Adding a new language**: Create `data/locale/{code}.json` following the existing structure.

## Project Structure

```
ecommerce-test-db/
├── generate.py              # Main entry point
├── config.yaml              # Growth curves, ratios, settings
├── requirements.txt         # Python dependencies (Faker, PyYAML)
├── data/
│   ├── categories.json      # 53 product categories (hierarchical)
│   ├── products.json        # 75 product templates (real brands)
│   ├── suppliers.json       # 50 suppliers
│   └── locale/
│       ├── en.json          # English text data
│       └── ko.json          # Korean text data
├── src/
│   ├── generators/          # Data generators (one per domain)
│   │   ├── base.py          # BaseGenerator (locale, RNG, helpers)
│   │   ├── products.py      # Categories, suppliers, products, prices
│   │   ├── customers.py     # Customers, addresses
│   │   ├── staff.py         # Staff/employees
│   │   ├── orders.py        # Orders, order items
│   │   ├── payments.py      # Payment details (card/bank/e-wallet)
│   │   ├── shipping.py      # Delivery tracking
│   │   ├── reviews.py       # Product reviews
│   │   ├── inventory.py     # Stock transactions
│   │   ├── carts.py         # Shopping carts
│   │   ├── coupons.py       # Coupons, usage history
│   │   ├── wishlists.py     # Wishlist (M:N)
│   │   ├── returns.py       # Returns/exchanges
│   │   ├── complaints.py    # CS complaints
│   │   └── images.py        # Product images + Pexels downloader
│   ├── exporters/
│   │   └── sqlite_exporter.py  # SQLite DDL + views + triggers + bulk insert
│   └── utils/
│       ├── fake_phone.py
│       ├── growth.py        # Yearly growth calculations
│       └── seasonality.py   # Monthly seasonality
├── sql/
│   ├── procedures_mysql.sql      # MySQL stored procedures & functions
│   └── procedures_postgresql.sql # PostgreSQL procedures & functions
└── output/                  # Generated files
    └── tutorial.db         # SQLite database
```

## SQL Concepts Coverage

This database enables practicing virtually every SQL concept:

| Concept | Covered | Where to Practice |
|---------|---------|-------------------|
| SELECT / WHERE / ORDER BY | ✅ | All tables |
| JOIN (INNER, LEFT, RIGHT) | ✅ | 20+ FK relationships |
| GROUP BY / HAVING | ✅ | `v_monthly_sales`, `v_payment_summary` |
| Subqueries (scalar, correlated) | ✅ | Top product per category, above-average customers |
| Window Functions | ✅ | `v_revenue_growth` (LAG), `v_customer_rfm` (NTILE), `v_top_products_by_category` (ROW_NUMBER), `v_product_abc` (cumulative SUM) |
| CTE / Recursive CTE | ✅ | `v_category_tree`, `v_customer_rfm` |
| CASE / COALESCE | ✅ | `v_customer_summary`, `v_daily_orders` |
| EXISTS / NOT EXISTS | ✅ | Wishlist → purchase conversion, no-order customers |
| UNION / UNION ALL | ✅ | Combine complaints + reviews |
| INSERT / UPDATE / DELETE | ✅ | All tables |
| VIEW | ✅ | 18 views |
| INDEX | ✅ | 38 indexes |
| CHECK constraints | ✅ | 10 constraints |
| UNIQUE constraints | ✅ | 7 constraints (including composite) |
| FOREIGN KEY | ✅ | 20+ foreign keys |
| NULL handling | ✅ | birth_date, gender, notes, staff_id |
| Date/time functions | ✅ | julianday, strftime, DATE |
| String functions | ✅ | SUBSTR, LIKE, \|\| concatenation |
| M:N relationships | ✅ | wishlists (UNIQUE composite key) |
| Self JOIN | ✅ | categories hierarchy |
| Aggregate functions | ✅ | COUNT, SUM, AVG, MIN, MAX |
| LIMIT / OFFSET | ✅ | Pagination practice |
| Triggers | ✅ | 5 triggers (auto-timestamp, price history) |
| Stored Procedures | ✅ | MySQL + PostgreSQL files in `sql/` |

## License

This tool generates **fictitious data** using:
- Fake names (via Faker library)
- Fake phone numbers (020-XXXX / 555-XXXX — non-existent area codes)
- Fake email domains (testmail.kr / testmail.com — non-existent)
- Real brand/product names for realism (Samsung, Intel, ASUS, etc.)

All generated data is for **testing and educational purposes only**.

## Call for Contributions

This project was built by a developer who is not a SQL expert. There may be mistakes, oversights, or suboptimal patterns in the schema design, queries, or tutorial content. Feedback and contributions from experienced SQL practitioners are very welcome.

- If you spot unrealistic schema or data patterns, please let me know
- If you know a better way to write a query, please suggest it
- If you have ideas for additional exercises or topics, please share

Issues and Pull Requests are greatly appreciated.

## Author

**Youngje Ahn** — civilian7@gmail.com
