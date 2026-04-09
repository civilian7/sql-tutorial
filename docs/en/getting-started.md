# Getting Started

You can generate the database and run your first query in 5 minutes.

## 1. Install Python

Python 3.10 or higher is required.

=== "Windows"
    Download from [python.org](https://www.python.org/downloads/) and install.
    Make sure to check **"Add Python to PATH"** during installation.

    ```
    python --version
    ```

=== "macOS"
    ```bash
    brew install python@3.12
    ```

=== "Linux (Ubuntu/Debian)"
    ```bash
    sudo apt update && sudo apt install python3 python3-pip python3-venv
    ```

## 2. Generate the Database

```bash
pip install -r requirements.txt
python generate.py --size small
```

This creates `output/ecommerce.db` (~80MB, 687K rows).

??? info "Virtual Environment (recommended)"
    ```bash
    python -m venv .venv
    source .venv/bin/activate   # macOS/Linux
    .venv\Scripts\activate      # Windows
    pip install -r requirements.txt
    python generate.py --size small
    ```

??? info "Generation Options"
    ```bash
    python generate.py --size small --locale en           # English data
    python generate.py --size small --all                  # Generate MySQL/PG SQL too
    python generate.py --size small --dirty-data           # Noisy data for cleaning practice
    python generate.py --size medium                       # Large dataset (7M rows)
    ```
    See the [Generator Reference](generator-guide.md) for all options.

## 3. Open in a SQL Tool

Open the generated `output/ecommerce.db` in any SQL tool.

| Tool | How |
|------|-----|
| ezQuery (in development) | File > Open DB > ecommerce.db |
| DB Browser for SQLite | Open Database |
| DBeaver | New Connection > SQLite > select file |
| Command line | `sqlite3 output/ecommerce.db` |

## 4. Run Your First Queries

Verify the database was created correctly.

```sql
-- Table list (30 tables = success)
SELECT name FROM sqlite_master
WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
ORDER BY name;
```

```sql
-- Sample 5 customers
SELECT name, email, grade, point_balance
FROM customers
LIMIT 5;
```

```sql
-- Data volume check
SELECT
    (SELECT COUNT(*) FROM customers) AS customers,
    (SELECT COUNT(*) FROM products) AS products,
    (SELECT COUNT(*) FROM orders) AS orders,
    (SELECT COUNT(*) FROM reviews) AS reviews;
```

If you see results, you're ready to go.

[Start Lesson 1: SELECT Basics →](beginner/01-select.md){ .md-button .md-button--primary }

## Learning Guide

### Recommended Path

| Step | Lessons | Topics |
|------|---------|--------|
| Step 1 | Beginner 01–06 | SELECT, WHERE, sorting, aggregates, GROUP BY, NULL |
| Step 2 | Intermediate 07–16 | JOINs, subqueries, CASE, date/string, DML, DDL, SELF/CROSS JOIN |
| Step 3 | Advanced 17–22 | Window functions, CTE, EXISTS, views, indexes, triggers |

Follow lessons **in order**. Each one builds on the previous.

### Tips for Effective Learning

- **Type out** example queries yourself. Don't copy-paste.
- Complete the **review exercises** at the end of each lesson.
- **Modify** queries — change conditions, add columns, break them on purpose.
- Try writing the same result using **different approaches** (subquery, JOIN, CTE).

### Choosing Data Size

| Purpose | Size | Rows |
|---------|------|-----:|
| Learning SQL syntax | `--size small` | 687K |
| Performance / EXPLAIN | `--size medium` | 7M |

`small` is sufficient for most learning. Use `medium` when you want to feel the impact of indexes and execution plans.

### Using MySQL / PostgreSQL

After learning basics with SQLite, try the same queries on other databases.

```bash
python generate.py --size small --target mysql --apply --ask-password
python generate.py --size small --target postgresql --apply --ask-password
```

Where syntax differs, lessons and exercises show **SQLite / MySQL / PostgreSQL tabs** side by side.

---

## Database Summary

| Item | Count | Description |
|------|------:|-------------|
| Tables | 30 | Full e-commerce domain coverage |
| Views | 18 | Window functions, CTEs, RFM analysis |
| Triggers | 5 | Auto-timestamp, price history, point validation |
| Indexes | 61 | Optimized for common query patterns |
| Stored Procedures | 25+5 | MySQL/PostgreSQL only |

## Learn More

- [Database Schema](schema.md) — All 30 tables with full column details
- [Generator Reference](generator-guide.md) — All CLI options, config files
- [DB Dialect Comparison](dialect-comparison.md) — SQLite vs MySQL vs PostgreSQL
