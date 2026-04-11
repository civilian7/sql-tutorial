# 04. Data Generation Options

If you've learned the basic execution in [03. Generate Data](03-generate.md), this page covers detailed options including data size, language, date range, noise, and configuration files.

## Full List of Command-Line Options

| Option | Default | Description | Example |
|--------|---------|-------------|---------|
| `--size` | `medium` (config) | Data size (`small`, `medium`, `large`) | `--size large` |
| `--seed` | `42` (config) | Random seed (ensures reproducibility) | `--seed 123` |
| `--start-date` | `2016-01-01` | Data start date | `--start-date 2023-01-01` |
| `--end-date` | `2025-12-31` | Data end date | `--end-date 2024-12-31` |
| `--locale` | `ko` | Data language (`ko`, `en`) | `--locale en` |
| `--target` | `sqlite` | Target DB format | `--target postgresql` |
| `--all` | - | Generate for all DB formats | `--all` |
| `--dirty-data` | - | Add 5-10% noise | `--dirty-data` |
| `--config` | `config.yaml` | Config file path | `--config my_config.yaml` |
| `--apply` | - | Apply generated SQL directly to DB | `--apply` |
| `--host` | `localhost` | DB server host | `--host db.example.com` |
| `--port` | auto | DB server port | `--port 5433` |
| `--user` | auto | DB username | `--user admin` |
| `--password` | - | DB password | `--password secret` |
| `--ask-password` | - | Enter password interactively | `--ask-password` |
| `--database` | `ecommerce_test` | Target database name | `--database mydb` |
| `--download-images` | - | Download product images via Pexels API | `--download-images` |
| `--pexels-key` | env var | Pexels API key | `--pexels-key YOUR_KEY` |

---

## Data Size

| Item | small | medium | large |
|------|-------|--------|-------|
| **Scale** | 0.1x | 1.0x (baseline) | 5.0x |
| **Total Rows** | ~690K | ~6.97M | ~34.8M |
| **SQLite File Size** | ~80 MB | ~800 MB | ~4 GB |
| **Generation Time** | ~20 sec | ~3 min | ~15 min |
| **Use Case** | SQL learning, quick testing | Performance testing, EXPLAIN practice | DB benchmarks, large-scale processing |

```bash
python generate.py --size small     # For learning (recommended)
python generate.py --size medium    # Performance testing
python generate.py --size large     # Large-scale benchmarks
```

---

## Date Range

Default is 2016-01-01 to 2025-12-31 (10 years).

```bash
# Generate only a specific year
python generate.py --start-date 2024-01-01 --end-date 2024-12-31

# Only a specific quarter
python generate.py --start-date 2024-07-01 --end-date 2024-09-30
```

If you specify a year not defined in `config.yaml`'s `yearly_growth`, it automatically interpolates based on the nearest year with a 5% annual growth rate.

!!! warning "Caution"
    Data generation volume increases proportionally with longer date ranges. Use with `--size small` to quickly generate even long periods.

---

## Locale Settings

```bash
python generate.py --locale ko    # Korean (default)
python generate.py --locale en    # English
```

### Differences by Language

| Item | Korean (`ko`) | English (`en`) |
|------|---------------|----------------|
| Category names | Desktop PC, Laptop, ... | Desktop PC, Laptop, ... |
| Customer names | Faker(ko_KR) | Faker(en_US) |
| Addresses | Based on Korean administrative regions | US address format |
| Phone numbers | `020-XXXX-XXXX` | `555-XXXX-XXXX` |
| Shipping carriers | CJ Logistics, Hanjin Express, ... | FedEx, UPS, ... |
| Reviews/inquiries | Korean templates | English templates |
| Holidays | Korean holidays (fictional) | English-speaking holidays (fictional) |

### Adding a New Language

1. Copy `data/locale/ko.json` to create `ja.json`
2. Translate each section to the target language
3. Run `python generate.py --locale ja`

Below is a practical example of adding Japanese (`ja.json`). Just translate all values while keeping the structure identical:

```json
{
  "faker_locale": "ja_JP",
  "phone": {
    "format": "090-{0:04d}-{1:04d}",
    "description": "日本の仮想携帯番号"
  },
  "email": {
    "customer_domains": [
      ["testmail.jp", 0.30],
      ["fakemail.jp", 0.20],
      ["example.co.jp", 0.15]
    ],
    "staff_domain": "techshop-staff.jp",
    "supplier_domain": "test.jp"
  },
  "categories": {
    "desktop-prebuilt": "デスクトップPC",
    "laptop-general": "ノートパソコン",
    "monitor-general": "モニター",
    "keyboard-mechanical": "メカニカルキーボード"
  },
  "shipping": {
    "carriers": {
      "ヤマト運輸": 0.40,
      "佐川急便": 0.30,
      "日本郵便": 0.20,
      "西濃運輸": 0.10
    }
  },
  "holidays": {
    "01-01": "元日",
    "01-13": "成人の日",
    "02-11": "建国記念の日",
    "03-21": "春分の日",
    "05-03": "憲法記念日"
  },
  "coupon": {
    "names": [
      "新規登録クーポン",
      "お誕生日クーポン",
      "リピーター限定割引"
    ]
  }
}
```

!!! tip "Using AI for Translation"
    You can hand the entire `ko.json` to an AI and ask "Translate this JSON to Japanese. Keep the keys, only translate the values" for quick results.

---

## Dirty Data Mode

Intentionally generates "messy" data commonly encountered in real-world scenarios. Useful for data cleaning practice.

```bash
python generate.py --dirty-data
```

The following noise is added to **5-10%** of the total data:

| Target | Noise Type | Example |
|--------|-----------|---------|
| Customer name | Leading/trailing spaces, double spaces | `"  John Doe"`, `"John  Doe"` |
| Email | Mixed case, space before @ | `"USER@testmail.kr"` |
| Phone number | Hyphens removed, international format | `"02012345678"`, `"+82-20-1234-5678"` |
| Birth date | Empty string, "N/A" | `""` or `"N/A"` instead of NULL |
| Gender | Lowercase, English notation | `"m"`, `"Male"`, `""` |
| Product name | Leading space, special whitespace | `" Samsung SSD"` |

!!! tip "Cleaning Practice Ideas"
    - Remove whitespace with `TRIM()`
    - Normalize case with `LOWER()`/`UPPER()`
    - Normalize inconsistent values with `CASE WHEN`
    - Handle `NULL` vs empty string distinction
    - Unify phone number format with `REPLACE()`

---

## Seeds and Reproducibility { #seeds-and-reproducibility }

**What is a seed?** It's the starting point for a random number generator. A computer's "random" is actually a sequence starting from a seed value, so using the same seed produces **identical** customer names, order dates, amounts, etc. every time.

This tutorial uses **seed 42** as the default. Therefore, if you generate with the same settings, the lesson query examples and result tables will match exactly.

```bash
python generate.py --seed 42     # Always the same data
python generate.py --seed 42     # Byte-for-byte identical to above
python generate.py --seed 100    # Completely different data
```

**What if you change the seed?** The table structure remains the same, but customer names, order counts, amounts, etc. will all differ. The results won't match the lesson examples, but it's useful when you want to practice with your own data.

- If no seed is specified, `config.yaml`'s `seed: 42` is used
- Fixing the seed in CI/CD allows reproducing test results
- You can create multiple datasets with different seeds for comparison exercises

---

## config.yaml Settings

`config.yaml` is the generator's core configuration file. It has lower priority than CLI options and can be overridden by CLI.

### Key Settings

```yaml
seed: 42                          # Random seed
locale: ko_KR                     # Data locale
shop_name: "TechShop"             # Shop name
start_date: "2016-01-01"          # Data start date
end_date: "2025-12-31"            # Data end date
size: medium                      # Default size
```

### Growth Curve

Simulates the shop's growth by year:

```yaml
yearly_growth:
  2016: { new_customers: 1000,  orders_per_day: [15, 25],   active_products: 300 }
  2020: { new_customers: 4500,  orders_per_day: [80, 120],  active_products: 1500 }
  2025: { new_customers: 7500,  orders_per_day: [150, 200], active_products: 2800 }
```

### Seasonality

Monthly order multiplier (1.0 = average):

```yaml
monthly_seasonality:
  1: 0.85     # January slow season
  3: 1.15     # Back to school
  7: 0.85     # Summer slow season
  11: 1.25    # Black Friday
  12: 1.20    # Year-end sale
```

### Order Settings

```yaml
order:
  free_shipping_threshold: 50000   # Free shipping threshold (50,000 KRW)
  default_shipping_fee: 3000       # Default shipping fee
  cancellation_rate: 0.05          # 5% cancellation rate
  return_rate: 0.03                # 3% return rate
  points_earn_rate: 0.01           # 1% of payment amount as points
```

### Payment Method Ratios

```yaml
payment_methods:
  card: 0.45            # Credit card 45%
  kakao_pay: 0.20       # Kakao Pay 20%
  naver_pay: 0.15       # Naver Pay 15%
  bank_transfer: 0.10   # Bank transfer 10%
  virtual_account: 0.05 # Virtual account 5%
  point: 0.05           # Points 5%
```

### Review Settings

```yaml
review:
  write_rate: 0.25               # 25% of confirmed purchases write reviews
  rating_distribution:           # Rating distribution (realistic J-curve)
    5: 0.40
    4: 0.30
    3: 0.15
    2: 0.10
    1: 0.05
```

### Customer Tier Thresholds

```yaml
customer_grades:
  BRONZE: 0          # Default
  SILVER: 500000     # 500K+ KRW in past year
  GOLD: 2000000      # 2M+ KRW in past year
  VIP: 5000000       # 5M+ KRW in past year
```

### Edge Case Ratios

```yaml
edge_cases:
  null_birth_date: 0.15          # 15% NULL birth dates
  null_gender: 0.10              # 10% NULL gender
  long_product_name: 0.01        # 1% product names over 200 chars
  zero_payment: 0.01             # 1% full-points payments
  no_review_products: 0.20       # 20% products with no reviews
```

### config_detailed.yaml Parameters

Values not in `config.yaml` are automatically loaded from `config_detailed.yaml`. Over 120 parameters allow fine-tuning of data characteristics.

**Customer**

| Parameter | Default | Description |
|-----------|---------|-------------|
| gender_ratio | [0.65, 0.35] | Male/female ratio |
| dormancy_rates.under_1year | 0.05 | Dormancy rate for customers < 1 year |
| dormancy_rates.over_5_years | 0.45 | Dormancy rate for customers > 5 years |
| withdrawal_rate | 0.03 | Withdrawal rate |
| never_logged_in_rate | 0.05 | Never-logged-in rate |
| address_count_weights | [0.50, 0.35, 0.15] | Probability of 1/2/3 addresses |
| apartment_probability | 0.70 | Apartment (detailed address) ratio |

**Product**

| Parameter | Default | Description |
|-----------|---------|-------------|
| discontinuation_rate | 0.25 | Discontinuation rate |
| price_history.max_changes | 4 | Max price changes per product |
| price_history.change_ratio_range | [0.80, 1.15] | Price change range (-20% to +15%) |
| images_per_product_weights | [15, 35, 30, 15, 5] | Probability of 1-5 images |

**Order**

| Parameter | Default | Description |
|-----------|---------|-------------|
| hourly_weights | [0.3, 0.2, ..., 0.8] | Hourly order weights (24 values) |
| weekday_weights | [1.10, 0.95, ..., 1.10] | Day-of-week order weights (Mon-Sun) |
| daily_variance | [0.8, 1.2] | Daily order count variation range |
| item_count_weights | [40, 30, 15, 10, 5] | Probability of 1-5 items per order |
| discount_probability | 0.10 | Discount application probability |
| points_usage_probability | 0.10 | Points usage probability |
| points_max_ratio | 0.30 | Max points usage ratio vs order amount |
| status_timeline_days | [3, 5, 10, 21] | Status transition period (days) |
| delivery_notes_probability | 0.35 | Delivery note writing probability |

**Payment**

| Parameter | Default | Description |
|-----------|---------|-------------|
| cancelled_refund_probability | 0.50 | Refund probability on cancellation |
| processing_delays.card_minutes | [1, 30] | Card payment processing time (min) |

**Shipping**

| Parameter | Default | Description |
|-----------|---------|-------------|
| ship_days_range | [1, 3] | Days from order to shipment |
| deliver_days_range | [1, 4] | Days from shipment to delivery |

**Review**

| Parameter | Default | Description |
|-----------|---------|-------------|
| creation_delay_days | [3, 30] | Days from order to review writing |
| title_probability | 0.80 | Title writing probability |
| empty_content_probability | 0.10 | No-content probability |

**Inventory**

| Parameter | Default | Description |
|-----------|---------|-------------|
| initial_stock_range | [50, 500] | Initial stock range |
| restock_frequency_range | [1, 5] | Restocking frequency (per year) |
| restock_quantity_range | [20, 300] | Restocking quantity range |

**Cart**

| Parameter | Default | Description |
|-----------|---------|-------------|
| status_weights | [0.2, 0.5, 0.3] | active/abandoned/converted ratio |
| items_range | [1, 5] | Cart items count range |

**Coupon**

| Parameter | Default | Description |
|-----------|---------|-------------|
| percent_values | [5, 10, 15, 20, 30] | Discount rates (%) |
| fixed_values | [3000, 5000, ..., 50000] | Fixed discount amounts (KRW) |
| duration_days | [30, 60, 90, 180, 365] | Coupon validity period |

**Return**

| Parameter | Default | Description |
|-----------|---------|-------------|
| request_delay_days | [0, 14] | Days from order to return request |
| full_return_probability | 0.70 | Full return probability (vs partial) |
| inspection_hours_range | [2, 48] | Inspection time (hours) |

**Complaint**

| Parameter | Default | Description |
|-----------|---------|-------------|
| order_complaint_rate | 0.08 | Complaint rate per order |
| unresolved_rate | 0.05 | Unresolved rate |
| response_hours_by_priority | urgent: [1,4], low: [12,96] | Response time by priority |

**Product Views**

| Parameter | Default | Description |
|-----------|---------|-------------|
| views_per_order | 8 | Average views per order |
| referrer_weights | direct: 0.20, search: 0.35, ... | Referrer source ratio |
| device_weights | desktop: 0.45, mobile: 0.45, tablet: 0.10 | Device ratio |

---

## Source Code Structure

```
generate.py                 <- Main execution script
verify.py                   <- Environment verification script
config.yaml                 <- Default config file
config_detailed.yaml        <- Detailed parameters (120+)
data/
├── categories.json         <- Product category master (manually curated)
├── products.json           <- Product master (brand, model, price range)
├── suppliers.json          <- Supplier master
└── locale/
    ├── ko.json             <- Korean locale data
    └── en.json             <- English locale data
src/
├── generators/             <- Data generation modules
│   ├── base.py             <- Common generation logic (BaseGenerator)
│   ├── customers.py        <- Customers + addresses
│   ├── products.py         <- Products + categories + suppliers
│   ├── orders.py           <- Orders + order details
│   ├── payments.py         <- Payments
│   ├── shipping.py         <- Shipping
│   ├── reviews.py          <- Reviews
│   ├── inventory.py        <- Inventory in/out
│   ├── staff.py            <- Staff
│   ├── images.py           <- Product images + Pexels download
│   ├── carts.py            <- Carts
│   ├── coupons.py          <- Coupons + usage history
│   ├── complaints.py       <- Inquiries/complaints
│   ├── returns.py          <- Returns/exchanges
│   ├── calendar.py         <- Date dimension table
│   ├── grade_history.py    <- Customer tier history
│   ├── tags.py             <- Product tags
│   ├── views.py            <- Product view logs
│   ├── points.py           <- Point transactions
│   ├── promotions.py       <- Promotions
│   ├── qna.py              <- Product Q&A
│   ├── wishlists.py        <- Wishlists
│   └── dirty.py            <- Dirty data noise injection
├── exporters/              <- DB-specific output modules
│   ├── sqlite_exporter.py  <- SQLite DDL + views + triggers
│   ├── mysql_exporter.py   <- MySQL DDL + views + SP
│   └── postgresql_exporter.py <- PostgreSQL DDL + MV + SP
└── utils/                  <- Utilities
    ├── fake_phone.py       <- Virtual phone number generation
    ├── growth.py           <- Growth curve calculation
    └── seasonality.py      <- Seasonality patterns
```

Each generation module inherits from `BaseGenerator` and independently generates data using `config.yaml` settings and the seed. Exporters use a plugin architecture — to add a new DB, just write one module in the `exporters/` directory.

---

## Output File Structure

```
output/
├── ecommerce-ko.db                 # SQLite database (default)
├── mysql/
│   ├── schema.sql               # Table/index/view DDL
│   ├── data.sql                 # INSERT statements (all data)
│   └── procedures.sql           # Stored procedures
└── postgresql/
    ├── schema.sql               # Table/index/view DDL
    ├── data.sql                 # INSERT statements (all data)
    └── procedures.sql           # Functions/procedures
```

---

## Data Verification

```bash
python verify.py                    # SQLite verification
python verify.py --target mysql     # MySQL verification
python verify.py --target postgresql  # PostgreSQL verification
python verify.py --all              # Full verification
```

Automatically checks table count, views, triggers, row counts, and FK integrity. For details, see [05. Verify and First Query](05-verify.md#automated-verification-script).

---

## FAQ

!!! question "How Long Does Medium Size Take?"
    About **3 minutes** (SQLite). Including MySQL/PostgreSQL SQL file generation, approximately 4-5 minutes.

!!! question "Can I Generate Only Specific Tables?"
    FK relationships between tables cause integrity issues with partial generation. Generate everything first, then remove unnecessary tables with `DROP TABLE`.

!!! question "Can I Add More Data to the Same DB?"
    Incremental generation is not supported. Generate a new DB with a different seed (`--seed`) or date range, then merge with `INSERT INTO ... SELECT FROM`.

!!! question "Can I Use This for Other Domains (Healthcare, Education, etc.)?"
    Yes, by modifying the categories/products/tags in `data/locale/ko.json`, the product master in `data/products.json`, and the price ranges/payment ratios in `config.yaml`.

!!! question "How to Download with Product Images?"
    Get a free key from [Pexels API](https://www.pexels.com/api/), then:
    ```bash
    python generate.py --download-images --pexels-key YOUR_API_KEY
    ```

[← 03. Generate Data](03-generate.md){ .md-button }
[05. Verify and First Query →](05-verify.md){ .md-button .md-button--primary }
