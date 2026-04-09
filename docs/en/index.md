# SQL Tutorial <small>v2.0</small>

A hands-on SQL tutorial using a realistic **e-commerce database**.

Learn SQL by querying 10 years of business data from **TechShop**, a fictional online store selling computers and peripherals. From basics to advanced — every query runs against real data.

!!! tip "What Makes This Different"
    Most SQL textbooks have exercises but no data — you write queries but can't run them.
    This tutorial provides **687,000 rows of realistic data**, so you can execute every query and see actual results.

## Learning Path

| Level | Topics | Lessons | Exercises |
|-------|--------|:-------:|:---------:|
| **Beginner** | SELECT, WHERE, ORDER BY, Aggregates, GROUP BY, NULL | 6 | 60 |
| **Intermediate** | JOINs, Subqueries, CASE, Date/String, DML, Self/Cross JOIN | 9 | 89 |
| **Advanced** | Window Functions, CTE, EXISTS, Views, Indexes, Triggers | 6 | 74 |
| | | **21 lessons** | **223 exercises** |

## Key Features

- **30 tables** — customers, products, orders, payments, shipping, reviews, points, promotions, Q&A
- **18 views** — window functions, CTEs, RFM analysis, and more
- **10 years of realistic data** — growth curves, seasonality, customer behavior patterns
- **3 databases** — SQLite (default), MySQL, PostgreSQL
- **Korean / English** — data and documentation in both languages
- **223 exercises** — beginner to advanced, with DB-specific SQL tabs

## Get Started

```bash
pip install -r requirements.txt
python generate.py --size small
```

Open the generated `output/ecommerce.db` in your SQL tool and follow the [Getting Started](getting-started.md) guide.

[Get Started →](getting-started.md){ .md-button .md-button--primary }
[Schema Reference →](schema.md){ .md-button }
