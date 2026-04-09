# Getting Started

You can generate the database and run your first query in 5 minutes.

## 1. Prerequisites

### Install Python

Python 3.10 or higher is required. If not already installed:

=== "Windows"
    Download from [python.org](https://www.python.org/downloads/) and install.

    !!! warning "Important"
        Check **"Add Python to PATH"** during installation.

    Verify:
    ```
    python --version
    ```

=== "macOS"
    ```bash
    # Using Homebrew
    brew install python@3.12

    # Or download from python.org
    ```

=== "Linux (Ubuntu/Debian)"
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv
    ```

### Install Packages

```bash
pip install -r requirements.txt
```

This installs:

| Package | Purpose |
|---------|---------|
| `Faker` | Generate fake names, addresses, phone numbers |
| `PyYAML` | Parse config files (config.yaml) |
| `mkdocs` | Build tutorial documentation (optional) |
| `mkdocs-material` | Documentation theme (optional) |

!!! tip "Virtual Environment Recommended"
    ```bash
    python -m venv .venv
    source .venv/bin/activate   # macOS/Linux
    .venv\Scripts\activate      # Windows
    pip install -r requirements.txt
    ```

## 2. Generate the Database

```bash
python generate.py --size small
```

This creates `output/ecommerce.db` (~80MB, 687K rows).

!!! info "More Options"
    ```bash
    # English data
    python generate.py --size small --locale en

    # Custom date range
    python generate.py --size small --start-date 2020-01-01 --end-date 2025-06-30

    # Generate SQL files for all databases
    python generate.py --size small --all
    ```
    See the [Generator Reference](generator-guide.md) for all options.

## 3. Open the Database

Open `output/ecommerce.db` in your SQL tool:

- **ezQuery** — File > Open DB > select ecommerce.db
- **DB Browser for SQLite** — Open Database
- **DBeaver** — New Connection > SQLite > select file
- **Command line** — `sqlite3 output/ecommerce.db`

## 4. Run Your First Queries

Verify the database was created correctly.

### Check Table List

```sql
SELECT name FROM sqlite_master
WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
ORDER BY name;
```

You should see 30 tables.

### Sample Data

```sql
-- 5 customers
SELECT name, email, grade, point_balance
FROM customers
LIMIT 5;
```

```sql
-- Latest 5 orders
SELECT order_number, customer_id, status, total_amount, ordered_at
FROM orders
ORDER BY ordered_at DESC
LIMIT 5;
```

```sql
-- Product categories
SELECT parent.name AS main_category, child.name AS sub_category
FROM categories child
JOIN categories parent ON child.parent_id = parent.id
WHERE child.depth = 1
ORDER BY parent.sort_order, child.sort_order;
```

### Check Data Volume

```sql
SELECT
    (SELECT COUNT(*) FROM customers) AS customers,
    (SELECT COUNT(*) FROM products) AS products,
    (SELECT COUNT(*) FROM orders) AS orders,
    (SELECT COUNT(*) FROM reviews) AS reviews;
```

## 5. Tutorial Guide

### Recommended Learning Path

```
Step 1: Beginner Lessons (01~06) → Beginner Exercises
Step 2: Intermediate Lessons (07~14, 21) → Intermediate Exercises
Step 3: Advanced Lessons (15~20) → Advanced Exercises
Step 4: Challenge Problems → EXPLAIN Analysis
```

!!! tip "Effective Learning"
    - Follow lessons **in order**. Each one builds on the previous.
    - **Type out** the example queries yourself. Don't copy-paste.
    - Complete the **review exercises** at the end of each lesson.
    - After finishing a level, try the corresponding **exercise set**.
    - **Modify** queries: change conditions, add columns, break them on purpose.

### Choosing the Right Scale

| Purpose | Recommended | Why |
|---------|------------|-----|
| Learning SQL syntax | `--size small` | Fast generation (20s), instant results |
| Complex query practice | `--size small` | Enough data (687K rows) for realistic results |
| Window functions / analytics | `--size small` or higher | Needs time-series data |
| Performance / EXPLAIN | `--size medium` | Need large data (7M rows) to see differences |
| Index effectiveness | `--size medium` or higher | Small data won't show index benefits |

### Getting the Most from the Data

!!! info "Things You Can Do"
    - **Ask business questions**: "Which VIP customers haven't logged in for 3 months?" — create your own queries
    - **Predict results**: Guess the output before running a query, then compare
    - **Try different approaches**: Write the same result using subquery, JOIN, and CTE
    - **Use EXPLAIN**: In advanced lessons, run EXPLAIN on every query to see execution plans

### Exercise Difficulty Guide

| Level | For | Problem Types |
|:-----:|-----|---------------|
| ⭐ | SQL beginners | Single table SELECT, WHERE, ORDER BY |
| ⭐⭐ | Completed basics | JOIN, GROUP BY, basic aggregation, date/string |
| ⭐⭐⭐ | Completed intermediate | Subqueries, CTE, CASE, complex JOINs |
| ⭐⭐⭐⭐ | Job-ready | Window functions, cumulative, retention, moving average |
| ⭐⭐⭐⭐⭐ | Interview/production | Consecutive patterns, sessions, median, Pareto |

### For MySQL / PostgreSQL Users

After learning basic syntax with SQLite, try running the same queries on MySQL or PostgreSQL.

```bash
# Generate MySQL database
python generate.py --size small --target mysql --apply --ask-password

# Generate PostgreSQL database
python generate.py --size small --target postgresql --apply --ask-password
```

Where SQL syntax differs between databases, lessons and exercises show **SQLite / MySQL / PostgreSQL tabs**.

### Practice with Dirty Data

Real-world data is never clean. Generate noisy data with `--dirty-data` for data cleaning practice.

```bash
python generate.py --size small --dirty-data
```

Includes: name whitespace, mixed-case emails, inconsistent phone formats, gender variants (`M`/`Male`/`m`), etc.

[Lesson 1: SELECT Basics →](beginner/01-select.md){ .md-button .md-button--primary }

---

## Database Summary

| Item | Count | Description |
|------|------:|-------------|
| Tables | 30 | Full e-commerce domain coverage |
| Views | 18 | Window functions, CTEs, RFM, and more |
| Triggers | 5 | Auto-timestamp, price history, point validation |
| Indexes | 61 | Optimized for common query patterns |
| Stored Procedures | 25+5 | MySQL/PostgreSQL only |

!!! tip "Learning Approach"
    Don't just read the queries — **type them out yourself**. Modify them, break them on purpose, then fix them. That's real learning.

## Learn More

- [Database Schema](schema.md) — All 30 tables with full column details
- [Generator Reference](generator-guide.md) — All CLI options, config files, MySQL/PostgreSQL setup
- [DB Dialect Comparison](dialect-comparison.md) — SQLite vs MySQL vs PostgreSQL syntax differences
