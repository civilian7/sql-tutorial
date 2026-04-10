**[한국어](README.ko.md)** | English

# SQL Tutorial — E-Commerce Database <small>v2.0</small>

[![Verify Tutorial](https://github.com/civilian7/sql-tutorial/actions/workflows/verify.yml/badge.svg)](https://github.com/civilian7/sql-tutorial/actions/workflows/verify.yml)

[**Live Tutorial**](https://civilian7.github.io/sql-tutorial/) | [Changelog](#changelog) | [GitHub](https://github.com/civilian7/sql-tutorial)

A Python tool that generates **realistic test databases** for an online computer & peripherals store, bundled with a comprehensive **SQL tutorial** (22 lessons, 208 exercises).

> **Why this project?** Most SQL textbooks have exercises but no data — you write queries but can't run them. This project gives you **687,000 rows of realistic data** + full tutorial + exercises you can actually execute.

## Quick Start

```bash
pip install -r requirements.txt
python generate.py --size small
# Output: output/ecommerce.db (~80MB, 697K rows)
```

Open `output/ecommerce.db` in any SQL tool and start learning.

## What's Included

| Component | Details |
|-----------|---------|
| **Database Generator** | 30 tables, 18 views, 5 triggers, 61 indexes |
| **Tutorial** | 22 lessons (beginner → intermediate → advanced), bilingual (ko/en) |
| **Exercises** | 208 in-lesson review problems + separate exercise sets, with answers |
| **Stored Procedures** | 25 procedures + 5 functions (MySQL & PostgreSQL) |
| **3 Databases** | SQLite (default), MySQL, PostgreSQL |
| **Dirty Data Mode** | `--dirty-data` for data cleaning practice |
| **Visual Diagrams** | Mermaid diagrams in every lesson |
| **DB-specific SQL** | SQLite / MySQL / PostgreSQL tabs where syntax differs |

## Command Line Options

```
python generate.py [OPTIONS]

--size {small,medium,large}    Data scale (default: medium)
--locale {ko,en}               Data language (default: ko)
--seed NUMBER                  Random seed (default: 42)
--start-date YYYY-MM-DD        Start date (default: 2016-01-01)
--end-date YYYY-MM-DD          End date (default: 2025-06-30)
--target {sqlite,mysql,postgresql}  Target DB (default: sqlite)
--all                          Generate all DB formats
--dirty-data                   Add 5-10% noise
--apply                        Apply SQL directly to target DB
--host / --port / --user       DB connection options
--password / --ask-password    DB password
--database NAME                Database name (default: ecommerce_test)
--config PATH                  Config file (default: config.yaml)
```

## Data Scale

| Scale | Rows | SQLite | Time | Use |
|-------|-----:|-------:|-----:|-----|
| small | ~697K | ~80 MB | ~20s | Learning, CI |
| medium | ~7M | ~800 MB | ~3 min | Development |
| large | ~35M | ~4 GB | ~15 min | Performance testing |

## Tutorial

22 lessons with visual diagrams, DB-specific SQL tabs, and review exercises.

| Level | Lessons | Topics |
|-------|---------|--------|
| Beginner | 01–06 | SELECT, WHERE, ORDER BY, Aggregates, GROUP BY, NULL |
| Intermediate | 07–16 | JOINs, Subqueries, CASE, Date/String, DML, DDL, Self/Cross JOIN |
| Advanced | 17–22 | Window Functions, CTE, EXISTS, Views, Indexes, Triggers |

## Exercises (270 problems)

| Level | Problems | Examples |
|:-----:|:--------:|----------|
| ⭐ | 38 | Single table SELECT, WHERE |
| ⭐⭐ | 92 | JOIN, GROUP BY, dates, strings |
| ⭐⭐⭐ | 78 | Subquery, CTE, CASE, complex JOIN |
| ⭐⭐⭐⭐ | 47 | Window functions, retention, moving average |
| ⭐⭐⭐⭐⭐ | 15 | Consecutive patterns, sessions, median, Pareto |

Problem types: `SELECT`, `JOIN/UNION`, `Aggregate`, `String/Date`, `Subquery/CTE`, `Window`, `CASE/IF`, `Analytics`

Exercises are authored in YAML and compiled to both mkdocs pages and `exercise.db`:

```bash
python compile_exercises.py    # YAML → exercise.db + mkdocs markdown
```

## Database (30 Tables)

### Core Commerce (12)

| Table | Rows | Description |
|-------|-----:|-------------|
| `categories` | 53 | Hierarchical categories (self-ref) |
| `suppliers` | 60 | Vendors |
| `products` | 280 | Hardware & peripherals (JSON specs, successor) |
| `product_images` | 748 | Product photos |
| `product_prices` | 829 | Price history |
| `customers` | 5,230 | Users (grade, acquisition channel) |
| `customer_addresses` | 8,554 | Shipping addresses |
| `staff` | 5 | Employees (org hierarchy) |
| `orders` | 34,908 | Orders (9-stage status) |
| `order_items` | 84,270 | Line items |
| `payments` | 34,908 | Payments |
| `shipping` | 33,107 | Delivery tracking |

### Engagement (7)

| Table | Rows | Description |
|-------|-----:|-------------|
| `reviews` | 7,945 | Ratings & reviews |
| `wishlists` | 1,999 | Favorites (M:N) |
| `carts` / `cart_items` | 3,000 / 9,037 | Shopping carts |
| `complaints` | 3,477 | CS claims (escalation, compensation) |
| `returns` | 936 | Returns (claim link, exchange, fee) |
| `product_qna` | 946 | Q&A (self-ref threads) |

### Analytics (11)

| Table | Rows | Description |
|-------|-----:|-------------|
| `point_transactions` | 130,149 | Point earn/use/expire ledger |
| `product_views` | 299,792 | Browsing log |
| `promotions` / `promotion_products` | 129 / 6,871 | Sales events |
| `customer_grade_history` | 10,273 | Grade audit (SCD Type 2) |
| `calendar` | 3,469 | Date dimension |
| `tags` / `product_tags` | 46 / 1,288 | Product tags (M:N) |
| `inventory_transactions` | 14,331 | Stock ledger |
| `coupons` / `coupon_usage` | 20 / 111 | Coupons |

## MySQL / PostgreSQL

```bash
# SQL files only (no DB needed)
python generate.py --target mysql --size small

# Direct apply
pip install mysql-connector-python   # or psycopg2-binary for PG
python generate.py --target mysql --size small --apply --ask-password
```

Each includes: proper types (DECIMAL, TIMESTAMP, BOOLEAN, ENUM), 25 stored procedures + 5 functions, table partitioning, and GRANT examples.

PostgreSQL additionally includes: JSONB, custom ENUM types, materialized views.

## Configuration

| File | Purpose |
|------|---------|
| `config.yaml` | Core settings (dates, scale, growth, rates) |
| `config_detailed.yaml` | 120+ tunable parameters (all have defaults) |

## Viewing the Tutorial (MkDocs)

The tutorial is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/). Install prerequisites first:

```bash
pip install -r requirements.txt    # includes mkdocs + mkdocs-material
```

### Both languages (static)

```bash
serve.bat
# http://localhost:8001/ko/  (Korean)
# http://localhost:8001/en/  (English)
```

Use the **language switcher** in the toolbar to switch between Korean and English. Changes require re-running `serve.bat`.

### Single language with live reload

```bash
serve.bat ko     # Korean at http://localhost:8001 (auto-reload on file change)
serve.bat en     # English at http://localhost:8001
```

### Static build only

```bash
cd docs
mkdocs build -f mkdocs-ko.yml     # → output/docs/ko/
mkdocs build -f mkdocs-en.yml     # → output/docs/en/
```

### PDF export

```bash
pdf.bat          # Both languages
pdf.bat ko       # Korean only
pdf.bat en       # English only
```

Output: `output/docs/{ko,en}/pdf/sql-tutorial-{ko,en}.pdf`

First run automatically installs Playwright + Chromium (~200MB). PDF rendering uses a headless browser, so tabs, Mermaid diagrams, and Material admonitions are fully rendered.

## Project Structure

```
├── generate.py              # Database generator
├── compile_exercises.py     # YAML exercises → exercise.db + mkdocs
├── check_integrity.py       # Data integrity checker
├── config.yaml              # Core config
├── config_detailed.yaml     # Detailed config (120+ params)
├── data/                    # Categories, products, suppliers, locale
├── exercises/               # Exercise YAML (beginner/intermediate/advanced)
├── docs/                    # MkDocs tutorial (ko + en)
├── src/
│   ├── generators/          # 18 data generators
│   └── exporters/           # SQLite, MySQL, PostgreSQL exporters
├── serve.bat                # Local tutorial server
├── pdf.bat                  # PDF export (mkdocs-exporter + Chromium)
└── output/                  # Generated files
```

## License

**Dual license:**

- **Code** (generator, scripts): [MIT License](LICENSE)
- **Content** (tutorials, exercises, docs): [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

Free for personal learning and non-commercial education. For commercial use: civilian7@gmail.com

## Changelog

### v2.0.0 (2026-04-09)

**Database**: 21 → 30 tables, 25 stored procedures + 5 functions per RDBMS, JSON specs, date-based range

**Data Realism**: Product bundles, gender/age preferences, point rewards, promotions, category return rates, product popularity decay, supplier deactivation

**Tutorial**: 22 lessons with Mermaid diagrams, DB-specific SQL tabs, 208 in-lesson review exercises, exercise compiler (YAML → DB + mkdocs)

**Features**: `--start-date`/`--end-date`, `--dirty-data`, `--apply` (direct DB), `config_detailed.yaml` (120+ params), MySQL/PostgreSQL exporters, bilingual content (ko/en)

### v1.0.0

Initial release: 21 tables, 18 views, 5 triggers, SQLite only, 201 exercises
