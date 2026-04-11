# Generator Reference

A comprehensive reference for all options and settings of the database generator (`generate.py`). For basic usage, see [Getting Started](getting-started.md).

---

## 1. Installation

### Requirements

- **Python 3.10** or later
- pip (Python package manager)

### Basic Installation

```bash
# Clone the repository and install dependencies
pip install -r requirements.txt
```

`requirements.txt` includes the following packages:

| Package | Purpose |
|---------|---------|
| `Faker>=25.0.0` | Generating fake data in Korean/English |
| `PyYAML>=6.0` | Parsing configuration files |

!!! note "SQLite3"
    SQLite3 is included in the Python standard library, so no additional installation is required.

### Optional Drivers

To apply generated SQL directly to MySQL or PostgreSQL (`--apply`), additional drivers are required:

=== "MySQL/MariaDB"

    ```bash
    pip install mysql-connector-python
    ```

=== "PostgreSQL"

    ```bash
    pip install psycopg2-binary
    ```

---

## 2. Quick Start

### Basic Execution

```bash
# Generate a small dataset quickly
python generate.py --size small
```

### Verify Output

```bash
# Check the SQLite file
ls -lh output/ecommerce-en.db

# List tables
sqlite3 output/ecommerce-en.db ".tables"

# Check row count
sqlite3 output/ecommerce-en.db "SELECT COUNT(*) FROM orders;"
```

!!! tip "First Run"
    Start with `--size small` to generate ~200K rows in under 10 seconds. Once you've verified everything works, scale up to `medium` or `large`.

---

## 3. Command-Line Options

| Option | Default | Description | Example |
|--------|---------|-------------|---------|
| `--size` | `medium` (config) | Data scale (`small`, `medium`, `large`) | `--size large` |
| `--seed` | `42` (config) | Random seed for reproducibility | `--seed 123` |
| `--start-date` | `2016-01-01` (config) | Data start date (YYYY-MM-DD) | `--start-date 2023-01-01` |
| `--end-date` | `2025-06-30` (config) | Data end date (YYYY-MM-DD) | `--end-date 2024-12-31` |
| `--locale` | `ko` (config) | Data locale (`ko`, `en`) | `--locale en` |
| `--target` | `sqlite` (config) | Target DB format | `--target postgresql` |
| `--all` | - | Generate all DB formats | `--all` |
| `--dirty-data` | - | Add 5-10% noise for data cleaning exercises | `--dirty-data` |
| `--config` | `config.yaml` | Configuration file path | `--config my_config.yaml` |
| `--apply` | - | Apply generated SQL directly to target DB | `--apply` |
| `--host` | `localhost` | DB server host | `--host db.example.com` |
| `--port` | Auto (MySQL:3306, PG:5432) | DB server port | `--port 5433` |
| `--user` | Auto (MySQL:`root`, PG:`postgres`) | DB username | `--user admin` |
| `--password` | - | DB password | `--password secret` |
| `--ask-password` | - | Prompt for password interactively | `--ask-password` |
| `--database` | `ecommerce_test` | Target database name | `--database mydb` |
| `--download-images` | - | Download product images via Pexels API | `--download-images` |
| `--pexels-key` | env `PEXELS_API_KEY` | Pexels API key | `--pexels-key YOUR_KEY` |

---

## 4. Data Scale

| Metric | small | medium | large |
|--------|-------|--------|-------|
| **Scale factor** | 0.1x | 1.0x (baseline) | 5.0x |
| **Total rows** | ~200K | ~2M | ~10M |
| **SQLite file size** | ~15 MB | ~150 MB | ~800 MB |
| **Generation time** | ~10s | ~2 min | ~15 min |
| **Use case** | CI/CD, quick tests | Development/learning | Performance testing, DB benchmarks |

!!! info "Scale Calculation"
    Each profile's `scale` value in `config.yaml` proportionally adjusts all quantities -- customer count, order count, product count, and more.

---

## 5. Date Range Configuration

### Basic Usage

```bash
# Generate only one year of data
python generate.py --start-date 2024-01-01 --end-date 2024-12-31

# Specific quarter only
python generate.py --start-date 2024-07-01 --end-date 2024-09-30

# Full 10-year range (default)
python generate.py --start-date 2016-01-01 --end-date 2025-06-30
```

### Automatic Growth Interpolation

If you specify years not defined in `yearly_growth`, the generator automatically interpolates values based on the nearest defined year:

- **5% growth/decline** per year of distance from the nearest defined year
- Clamped between 0.3x and 3.0x

```bash
# Specifying 2026-2028 will auto-interpolate from 2025 data
python generate.py --start-date 2026-01-01 --end-date 2028-12-31
```

!!! warning "Note"
    Longer date ranges generate proportionally more data. Combine with `--size small` to keep long ranges fast.

---

## 6. Locale Settings

### Usage

```bash
# Korean data (default)
python generate.py --locale ko

# English data
python generate.py --locale en
```

### What Changes by Locale

| Data | Korean (`ko`) | English (`en`) |
|------|---------------|----------------|
| Category names | 데스크톱 PC, 노트북, ... | Desktop PC, Laptop, ... |
| Brand/product names | Korean suffixes | English suffixes |
| Supplier names | Korean company names | English company names |
| Customer names | Faker(ko_KR) | Faker(en_US) |
| Addresses | Korean administrative regions | US-style addresses |
| Email domains | `testmail.kr`, etc. | `testmail.com`, etc. |
| Phone numbers | `020-XXXX-XXXX` | `555-XXXX-XXXX` |
| Carriers | CJ대한통운, 한진택배, ... | FedEx, UPS, ... |
| Review content | Korean templates | English templates |
| Customer inquiries | Korean templates | English templates |
| Tags | Korean tags | English tags |
| Coupon names | 신규 가입 환영 쿠폰, ... | Welcome Coupon, ... |
| Delivery notes | 문 앞에 놓아주세요, ... | Leave at front door, ... |
| Calendar holidays | Korean holidays | US holidays |

### Adding a New Language

1. Create a new locale file in `data/locale/` (e.g., `ja.json`)
2. Copy `ko.json` or `en.json` and translate all fields
3. Set `faker_locale` to the appropriate locale (e.g., `ja_JP`)
4. Run: `python generate.py --locale ja`

!!! note "Locale File Structure"
    Locale files contain all language-dependent data: categories, review templates, delivery notes, coupon names, complaint templates, and more. See `data/locale/ko.json` for reference.

---

## 7. Target Databases

### SQLite (Default)

```bash
python generate.py --target sqlite
```

- Output: `output/ecommerce-en.db`
- No server required -- single file, ready to use
- Includes views, triggers, and indexes

### MySQL / MariaDB

=== "Generate SQL files only"

    ```bash
    python generate.py --target mysql
    ```
    Output: `output/mysql/schema.sql`, `data.sql`, `procedures.sql`

=== "Apply directly to database"

    ```bash
    python generate.py --target mysql --apply \
        --host localhost --port 3306 \
        --user root --ask-password \
        --database ecommerce_test
    ```

MySQL-specific features:

- `AUTO_INCREMENT` primary keys
- `ENUM` types (status, grade, etc.)
- `JSON` column type
- Stored procedures (sales aggregation, grade updates, etc.)
- `utf8mb4` encoding

### PostgreSQL

=== "Generate SQL files only"

    ```bash
    python generate.py --target postgresql
    ```
    Output: `output/postgresql/schema.sql`, `data.sql`, `procedures.sql`

=== "Apply directly to database"

    ```bash
    python generate.py --target postgresql --apply \
        --host localhost --port 5432 \
        --user postgres --ask-password \
        --database ecommerce_test
    ```

PostgreSQL-specific features:

- `GENERATED ALWAYS AS IDENTITY` primary keys
- `JSONB` column type
- Functions / procedures (`PL/pgSQL`)
- Partitioning, materialized views, etc.

### Generate All Formats

```bash
python generate.py --all
```

!!! tip "SQL Server / Oracle"
    `--target sqlserver` and `--target oracle` are also supported. Currently implemented up to DDL + INSERT SQL file generation.

---

## 8. config.yaml Reference

`config.yaml` is the primary configuration file for the generator. Here is a section-by-section reference.

### Basic Settings

```yaml
seed: 42                        # Random seed (reproducibility)
locale: ko_KR                   # Data locale
shop_name: "테크샵(TechShop)"   # Shop name
```

### Date Range

```yaml
start_date: "2016-01-01"        # Data start date
end_date: "2025-06-30"          # Data end date
```

Simulates a 10-year-old online shop. Can be overridden with `--start-date` / `--end-date`.

### Size Profiles

```yaml
size: medium                    # Default scale

profiles:
  small:
    scale: 0.1                  # 10% of medium
  medium:
    scale: 1.0                  # Baseline
  large:
    scale: 5.0                  # 500% of medium
```

### Targets

```yaml
targets:
  - sqlite                      # Default: SQLite only
output_dir: ./output
```

### Yearly Growth

Simulates the shop's growth year over year:

```yaml
yearly_growth:
  2016: { new_customers: 1000,  orders_per_day: [15, 25],   active_products: 300 }
  2017: { new_customers: 1800,  orders_per_day: [25, 40],   active_products: 500 }
  # ... (2018-2025)
  2025: { new_customers: 7500,  orders_per_day: [150, 200], active_products: 2800 }
```

| Field | Description |
|-------|-------------|
| `new_customers` | New customer signups for the year |
| `orders_per_day` | Daily order count range [min, max] |
| `active_products` | Number of active (in-stock) products |

### Monthly Seasonality

Monthly order multipliers (1.0 = average):

```yaml
monthly_seasonality:
  1: 0.85     # January - slow season
  3: 1.15     # Back to school
  7: 0.85     # Summer slump
  11: 1.25    # Black Friday
  12: 1.20    # Year-end sales
```

### Phone / Email

```yaml
phone:
  prefix: "020"
  format: "020-{4d}-{4d}"       # Fictional area code

email:
  customer_domain: "testmail.kr"       # Customer email domain
  staff_domain: "techshop-staff.kr"    # Staff email domain
  supplier_domain: "test.kr"           # Supplier email domain
```

!!! info "Fictional Phone Numbers"
    The `020` prefix is an unassigned Korean area code, similar to the US `555` prefix used in movies. In English locale, `555-XXXX-XXXX` is used instead.

### Order Settings

```yaml
order:
  free_shipping_threshold: 50000   # Free shipping threshold (50,000 KRW)
  default_shipping_fee: 3000       # Default shipping fee
  items_per_order:
    min: 1
    max: 5
    avg: 2.3
  cancellation_rate: 0.05          # 5% cancellation rate
  return_rate: 0.03                # 3% return rate
  points_earn_rate: 0.01           # 1% points earned on payment
```

### Payment Method Distribution

```yaml
payment_methods:
  card: 0.45            # Credit card 45%
  kakao_pay: 0.20       # Kakao Pay 20%
  naver_pay: 0.15       # Naver Pay 15%
  bank_transfer: 0.10   # Bank transfer 10%
  virtual_account: 0.05 # Virtual account 5%
  point: 0.05           # Points 5%
```

### Carrier Distribution

```yaml
carriers:
  CJ대한통운: 0.40
  한진택배: 0.25
  로젠택배: 0.20
  우체국택배: 0.15
```

### Review Settings

```yaml
review:
  write_rate: 0.25               # 25% of confirmed orders get a review
  rating_distribution:           # J-curve distribution (realistic)
    5: 0.40
    4: 0.30
    3: 0.15
    2: 0.10
    1: 0.05
```

### Customer Grade Thresholds

```yaml
customer_grades:
  BRONZE: 0          # Default
  SILVER: 500000     # 500K+ KRW in the last year
  GOLD: 2000000      # 2M+ KRW in the last year
  VIP: 5000000       # 5M+ KRW in the last year
```

### Edge Case Rates

```yaml
edge_cases:
  null_birth_date: 0.15          # 15% NULL birth dates
  null_gender: 0.10              # 10% NULL gender
  long_product_name: 0.01        # 1% product names over 200 chars
  zero_payment: 0.01             # 1% full-points payment
  bulk_order: 0.005              # 0.5% bulk corporate purchases
  no_review_products: 0.20       # 20% products with no reviews
```

---

## 9. config_detailed.yaml Reference

`config_detailed.yaml` provides 120+ fine-tuning parameters. Values not defined in `config.yaml` are loaded from this file.

### customer

| Parameter | Default | Description |
|-----------|---------|-------------|
| `gender_ratio` | `[0.65, 0.35]` | Male/female ratio |
| `dormancy_rates.under_1year` | `0.05` | Dormancy rate for <1 year |
| `dormancy_rates.1_to_3_years` | `0.15` | Dormancy rate for 1-3 years |
| `dormancy_rates.3_to_5_years` | `0.30` | Dormancy rate for 3-5 years |
| `dormancy_rates.over_5_years` | `0.45` | Dormancy rate for 5+ years |
| `withdrawal_rate` | `0.03` | Account deactivation rate |
| `never_logged_in_rate` | `0.05` | Rate of signup-only accounts |
| `address_count_weights` | `[0.50, 0.35, 0.15]` | Probability of having 1/2/3 addresses |
| `apartment_probability` | `0.70` | Rate of apartment address detail |

**Example change:** To equalize gender ratio:

```yaml
customer:
  gender_ratio: [0.50, 0.50]
```

### product

| Parameter | Default | Description |
|-----------|---------|-------------|
| `discontinuation_rate` | `0.25` | Product discontinuation rate (25%) |
| `price_history.max_changes` | `4` | Max price changes per product |
| `price_history.change_ratio_range` | `[0.80, 1.15]` | Price change range (-20% to +15%) |
| `images_per_product_weights` | `[15, 35, 30, 15, 5]` | Probability of 1/2/3/4/5 images |

### order

| Parameter | Default | Description |
|-----------|---------|-------------|
| `hourly_weights` | 24 weights | Hourly order frequency (0h-23h) |
| `weekday_weights` | `[1.10, 0.95, ..., 1.10]` | Day-of-week order frequency (Mon-Sun) |
| `daily_variance` | `[0.8, 1.2]` | Daily order count variance |
| `item_count_weights` | `[40, 30, 15, 10, 5]` | Probability of 1/2/3/4/5 items per order |
| `bulk_item_range` | `[5, 15]` | Item count range for bulk orders |
| `bulk_quantity_range` | `[2, 10]` | Quantity range for bulk orders |
| `discount_probability` | `0.10` | Discount application probability |
| `discount_ratio_range` | `[0.03, 0.15]` | Discount range (3%-15%) |
| `points_usage_probability` | `0.10` | Points redemption probability |
| `points_usage_range` | `[100, 5000]` | Points usage amount range |
| `points_max_ratio` | `0.30` | Max points-to-total ratio (30%) |
| `status_timeline_days` | `[3, 5, 10, 21]` | Status transition thresholds (pending/paid/shipped/delivered) |
| `completion_days_range` | `[8, 21]` | Days until order completion |
| `cancellation_hours_range` | `[1, 48]` | Hours until cancellation |
| `delivery_notes_probability` | `0.35` | Delivery note probability |

**Pareto distribution** (top customers order concentration):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `pareto.tiers` | `[0.05, 0.20, 0.50]` | Top 5% / 20% / 50% tiers |
| `pareto.weights` | `[10.0, 4.0, 1.5, 0.5]` | Order weight per tier |

**Price tier browsing weights**:

| Price Range | Weight | Meaning |
|-------------|-------:|---------|
| Up to 50K | 5.0 | Budget items browsed most |
| Up to 200K | 3.0 | |
| Up to 500K | 2.0 | |
| Up to 1M | 1.0 | |
| Up to 2M | 0.5 | |
| Over 2M | 0.2 | Premium items browsed rarely |

### payment

| Parameter | Default | Description |
|-----------|---------|-------------|
| `cancelled_refund_probability` | `0.50` | Refund probability for cancelled orders |
| `receipt_probability.bank_transfer` | `0.70` | Receipt rate for bank transfers |
| `receipt_probability.easy_pay` | `0.20` | Receipt rate for easy pay |
| `processing_delays.card_minutes` | `[1, 30]` | Card payment processing delay (min) |
| `processing_delays.virtual_account_days` | `[7, 21]` | Virtual account deposit deadline (days) |
| `processing_delays.bank_transfer_minutes` | `[1, 30]` | Bank transfer processing delay (min) |

### shipping

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ship_days_range` | `[1, 3]` | Days from order to shipment |
| `deliver_days_range` | `[1, 4]` | Days from shipment to delivery |

### review

| Parameter | Default | Description |
|-----------|---------|-------------|
| `creation_delay_days` | `[3, 30]` | Days from order to review |
| `title_probability` | `0.80` | Review title probability |
| `empty_content_probability` | `0.10` | Empty review body probability |

### inventory

| Parameter | Default | Description |
|-----------|---------|-------------|
| `initial_stock_range` | `[50, 500]` | Initial stock quantity range |
| `restock_frequency_range` | `[1, 5]` | Restock frequency (times) |
| `restock_quantity_range` | `[20, 300]` | Restock quantity range |

### cart

| Parameter | Default | Description |
|-----------|---------|-------------|
| `target_count_base` | `30000` | Base cart count (multiplied by scale) |
| `status_weights` | `[0.2, 0.5, 0.3]` | Active/abandoned/converted ratio |
| `items_range` | `[1, 5]` | Cart item count range |
| `item_quantity_weights` | `[0.7, 0.2, 0.1]` | Quantity 1/2/3 probability |
| `item_add_time_minutes` | `[0, 120]` | Time between item additions (min) |

### coupon

| Parameter | Default | Description |
|-----------|---------|-------------|
| `target_count_base` | `200` | Base number of coupon types |
| `max_count` | `500` | Maximum coupon types |
| `percent_values` | `[5, 10, 15, 20, 30]` | Percentage discount values |
| `fixed_values` | `[3000, ..., 50000]` | Fixed discount amounts |
| `min_order_amounts` | `[null, 30000, ..., 500000]` | Minimum order thresholds |
| `duration_days` | `[30, 60, 90, 180, 365]` | Validity periods (days) |
| `usage_limits` | `[null, 100, ..., 5000]` | Total usage limits |
| `per_user_limits` | `[1, 1, 1, 2, 3]` | Per-user usage limits |
| `target_usage_base` | `50000` | Base coupon usage count |

### wishlist

| Parameter | Default | Description |
|-----------|---------|-------------|
| `target_count_base` | `20000` | Base wishlist count |
| `purchase_conversion_rate` | `0.40` | Wishlist-to-purchase conversion rate |
| `pre_purchase_days_range` | `[1, 30]` | Days from wishlist to purchase |
| `notify_on_sale_rate` | `0.30` | Sale notification opt-in rate |

### return

| Parameter | Default | Description |
|-----------|---------|-------------|
| `request_delay_days` | `[0, 14]` | Days from order to return request |
| `pickup_days_range` | `[1, 3]` | Days until pickup |
| `full_return_probability` | `0.70` | Full return probability (vs partial) |
| `reception_days_range` | `[1, 4]` | Days until return reception |
| `inspection_hours_range` | `[2, 48]` | Inspection time (hours) |
| `completion_hours_range` | `[1, 24]` | Refund completion time (hours) |

### complaint

| Parameter | Default | Description |
|-----------|---------|-------------|
| `order_complaint_rate` | `0.08` | Complaint rate per order |
| `general_ratio` | `0.25` | General inquiry ratio |
| `unresolved_rate` | `0.05` | Unresolved complaint rate |
| `auto_closure_probability` | `0.85` | Auto-closure probability |
| `response_hours_by_priority` | urgent:1-4h, high:2-12h, ... | Response time by priority |
| `category_weights` | defect:15%, delivery:25%, ... | Complaint category weights |
| `channel_weights` | web:35%, phone:25%, ... | Channel weights |

### staff

| Parameter | Default | Description |
|-----------|---------|-------------|
| `target_count_base` | `50` | Base staff count |
| `max_count` | `200` | Maximum staff count |
| `admin_count` | `3` | Number of admins |
| `manager_threshold` | `10` | Manager role ID threshold |
| `termination_rate` | `0.10` | Staff turnover rate |

### tags

| Parameter | Default | Description |
|-----------|---------|-------------|
| `per_product_range` | `[2, 6]` | Tags per product range |
| `price_thresholds.high_end` | `2000000` | High-end tag threshold |
| `price_thresholds.premium` | `1000000` | Premium tag threshold |
| `price_thresholds.budget` | `100000` | Budget tag threshold |

### product_views

| Parameter | Default | Description |
|-----------|---------|-------------|
| `views_per_order` | `8` | Average views per order |
| `session_gap_minutes` | `30` | Session boundary (minutes) |
| `session_probability` | `0.30` | In-session additional view probability |
| `session_extra_views` | `[1, 4]` | Extra views within a session |
| `pre_purchase_views` | `[1, 5]` | Pre-purchase view count |
| `pre_purchase_days` | `[0, 14]` | Pre-purchase browsing window (days) |
| `referrer_weights` | direct:20%, search:35%, ad:15%, ... | Traffic source distribution |
| `device_weights` | desktop:45%, mobile:45%, tablet:10% | Device distribution |

---

## 10. Dirty Data Mode

### Usage

```bash
python generate.py --dirty-data
```

### Types of Noise

The `--dirty-data` flag injects intentional noise into **5-10%** of the data:

| Target | Noise Type | Example |
|--------|-----------|---------|
| Customer name | Leading/trailing/double spaces | `"  John Doe"`, `"John  Doe"` |
| Email | Mixed case, space before @ | `"USER@testmail.com"`, `"user @testmail.com"` |
| Phone | No hyphens, spaces, intl format | `"02012345678"`, `"+82-20-1234-5678"` |
| Birth date | Empty string, "N/A", "unknown" | `""` or `"N/A"` instead of NULL |
| Gender | Lowercase, full word, empty string | `"m"`, `"Male"`, `""` |
| Product name | Leading space, non-breaking space | `" Samsung SSD"`, `"Samsung\u00a0SSD"` |
| Order notes | Whitespace-only, "N/A", "-" | `" "`, `"N/A"` |
| Review content | Extra newlines | `"Great product.\n"` |

### Data Cleaning Exercise Ideas

!!! example "Practice Exercises"
    1. Use `TRIM()` to remove whitespace
    2. Use `LOWER()`/`UPPER()` to normalize case
    3. Use `CASE WHEN` to standardize inconsistent values
    4. Distinguish `NULL` vs empty string
    5. Use `REPLACE()` to normalize phone formats

---

## 11. Seed and Reproducibility

### Default Behavior

```bash
# Same seed → same data
python generate.py --seed 42
python generate.py --seed 42   # Identical result
```

### How It Works

- The seed value is passed to all generators
- Each generator initializes its own random number generator with `seed + offset`
- Same seed + same configuration = byte-identical database

### Generating Different Data

```bash
# Different seeds produce completely different datasets
python generate.py --seed 100
python generate.py --seed 200
```

!!! tip "Usage Tips"
    - **CI/CD**: Fix the seed to reproduce test results
    - **Multiple datasets**: Change the seed to generate different test data versions
    - **Default seed**: If not specified, `seed: 42` from `config.yaml` is used

---

## 12. Output File Structure

```
output/
├── ecommerce-en.db                 # SQLite database (default)
├── mysql/
│   ├── schema.sql               # Table/index/view DDL
│   ├── data.sql                 # INSERT statements (all data)
│   └── procedures.sql           # Stored procedures
└── postgresql/
    ├── schema.sql               # Table/index/view DDL
    ├── data.sql                 # INSERT statements (all data)
    └── procedures.sql           # Functions/procedures
```

!!! note "SQLite Database Contents"
    `ecommerce-en.db` contains tables, views, triggers, and indexes. See the [Database Schema](schema/index.md) page for full details.

---

## 13. Data Validation

### Running the Integrity Check

```bash
python check_integrity.py
# Or specify a specific DB file
python check_integrity.py output/ecommerce-en.db
```

### What Gets Checked

| Check | Description |
|-------|-------------|
| **Table inventory** | Row counts for all tables |
| **Views/triggers/indexes** | Metadata object counts |
| **Foreign key integrity** | Orphan record check across 23 FK relationships |
| **Temporal integrity** | Order date > signup date, delivery > shipment, etc. |
| **Realism metrics** | Order frequency by gender, first vs repeat order amounts |
| **New tables** | Point transactions, promotions, Q&A, calendar verification |
| **CS data** | Complaint types, escalations, return-claim links |
| **Output files** | Existence and size of SQLite/MySQL/PostgreSQL files |

Example output:

```
==========================================================
COMPREHENSIVE DATA INTEGRITY CHECK
==========================================================
[1] Tables: 30
  categories                         53
  customers                       52,500
  orders                         195,000
  ...
  TOTAL                        2,134,567

[5] FOREIGN KEY INTEGRITY
  OK  orders.customer_id → customers
  OK  order_items.order_id → orders
  ...
  Result: 23/23 passed

ALL CHECKS PASSED
==========================================================
```

---

## 14. FAQ

??? question "Q: How long does medium scale take?"
    `--size medium` takes about **2 minutes** (SQLite only). Including MySQL/PostgreSQL SQL file generation, expect 3-4 minutes. Actual time depends on hardware.

??? question "Q: Can I generate specific tables only?"
    Currently, all tables are generated together. Foreign key relationships between tables mean partial generation could cause integrity issues. Generate everything, then `DROP TABLE` any tables you don't need.

??? question "Q: Can I add data to an existing database?"
    Incremental generation is not directly supported. Instead:
    
    1. Generate a new DB with a different `--seed`
    2. Use different date ranges to generate different time periods
    3. Merge with `INSERT INTO ... SELECT FROM` as needed

??? question "Q: Can I change the industry (clothing, food, etc.)?"
    The generator is currently tailored to a computer/peripherals shop. To change the industry:
    
    1. Edit categories, products, and tags in `data/locale/ko.json`
    2. Replace the product master in `data/products.json`
    3. Update suppliers in `data/suppliers.json`
    4. Adjust price ranges, payment method ratios, etc. in `config.yaml`

??? question "Q: Does it work on Windows?"
    Yes, it works on Windows, macOS, and Linux as long as Python 3.10+ is installed.

??? question "Q: Does --all generate SQLite, MySQL, and PostgreSQL?"
    `--all` generates all 5 formats: sqlite, mysql, postgresql, sqlserver, and oracle. Note that sqlserver and oracle may not be fully implemented yet.

??? question "Q: How do I download product images?"
    Using the Pexels API. Get a free API key at [pexels.com/api](https://www.pexels.com/api/), then:
    
    ```bash
    python generate.py --download-images --pexels-key YOUR_API_KEY
    ```
    
    Or set as an environment variable:
    
    ```bash
    export PEXELS_API_KEY=YOUR_API_KEY
    python generate.py --download-images
    ```
