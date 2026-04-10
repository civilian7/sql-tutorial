# SQL Tutorial <small>v2.0</small>

A hands-on SQL tutorial using a realistic **e-commerce database**.

Learn SQL by querying 10 years of business data from **TechShop**, a fictional online store selling computers and peripherals. From basics to advanced — every query runs against real data.

## Why This Tutorial

Most SQL textbooks explain syntax but provide no data to run queries against, or at best a handful of rows. In practice you switch between multiple databases, yet textbooks teach just one dialect.

This tutorial was built to bridge that gap.

| Typical Textbook | This Tutorial |
|------------------|---------------|
| Syntax only, no data | **687,000 rows** of realistic data |
| 10–20 sample rows | 10 years of growth curves, seasonality, behavior patterns |
| Single DB dialect | **SQLite, MySQL, PostgreSQL** side-by-side tabs |
| One language | Data and docs in both **Korean and English** |

## What You'll Learn

26 lessons with 208 practice exercises. Every exercise includes a full solution.

| Level | Topics | Lessons | Exercises |
|-------|--------|:-------:|:---------:|
| **Beginner** | SELECT, WHERE, ORDER BY, Aggregates, GROUP BY, NULL | 7 | 65 |
| **Intermediate** | JOINs, Subqueries, CASE, Date/String, DML, DDL, Self/Cross JOIN | 10 | 93 |
| **Advanced** | Window Functions, CTE, EXISTS, Views, Indexes, Triggers | 6 | 55 |

The database contains 30 tables and 18 views covering every aspect of an online store: customers, products, orders, payments, shipping, reviews, points, promotions, Q&A, and more.

## Get Started

```bash
pip install -r requirements.txt
python generate.py --size small
```

Open the generated `output/ecommerce.db` in your SQL tool and start practicing right away.

[Get Started →](getting-started.md){ .md-button .md-button--primary }
[Schema Reference →](schema.md){ .md-button }

---

## About the Author

**Youngje Ahn** — Developer with 36 years of experience (civilian7@gmail.com)

While building ezQuery (in development), a database query tool, I needed a practical SQL tutorial to ship alongside it. Having experienced the limitations of existing textbooks firsthand, I created this tutorial with one goal: a textbook you can actually *run*.
