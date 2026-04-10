# Getting Started

You can generate the database and run your first query in 5 minutes.

## 1. Download the Project

=== "Git"
    ```bash
    git clone https://github.com/civilian7/sql-tutorial.git
    cd sql-tutorial
    ```

=== "ZIP Download"
    [Download ZIP from GitHub](https://github.com/civilian7/sql-tutorial/archive/refs/heads/main.zip), extract it, and open the folder.

## 2. Install Python

Python 3.10 or higher is required. Skip this step if already installed.

=== "Windows"
    Download from [python.org](https://www.python.org/downloads/) and install.

    !!! warning "Important during installation"
        Check **"Add Python to PATH"** on the first screen. Without this, `python` won't work in the terminal.

    After installing, open **Command Prompt** (search `cmd` in Start menu) and verify:
    ```
    python --version
    ```

=== "macOS"
    Open **Terminal** (search `Terminal` in Spotlight):
    ```bash
    brew install python@3.12
    python3 --version
    ```

=== "Linux (Ubuntu/Debian)"
    ```bash
    sudo apt update && sudo apt install python3 python3-pip python3-venv
    python3 --version
    ```

## 3. Generate the Database

Navigate to the project folder in your terminal, then run:

```bash
pip install -r requirements.txt
python generate.py --size small
```

This creates `output/ecommerce.db` (~80MB, 687K rows). Takes about 20 seconds.

!!! tip "If you get errors"
    - `pip: command not found` → try `pip3` instead
    - `Permission denied` → use a virtual environment:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate      # Windows
    source .venv/bin/activate   # macOS/Linux
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

## 4. Open in a SQL Tool

Open the generated `output/ecommerce.db` in a SQL tool. **If this is your first time, we recommend DB Browser for SQLite** — it's free and easy to install.

| Tool | Install | Open File |
|------|---------|-----------|
| **DB Browser for SQLite** (recommended) | [sqlitebrowser.org](https://sqlitebrowser.org/dl/) | Open Database > ecommerce.db |
| DBeaver | [dbeaver.io](https://dbeaver.io/download/) | New Connection > SQLite > select file |
| Command line | (no install needed) | `sqlite3 output/ecommerce.db` |

## 5. Run Your First Queries

Verify the database was created correctly. Type the following in your SQL tool and execute.

```sql
-- Check table list
SELECT name FROM sqlite_master
WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
ORDER BY name;
```

You should see 30 tables:

| name |
|------|
| calendar |
| cart_items |
| carts |
| categories |
| ... (30 total) |

```sql
-- Sample customer data
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
| Step 1 | Beginner 00–06 | SELECT, WHERE, sorting, aggregates, GROUP BY, NULL |
| Step 2 | Intermediate 07–17 | JOINs, subqueries, CASE, date/string, DML, DDL, transactions, SELF/CROSS JOIN |
| Step 3 | Advanced 18–25 | Window functions, CTE, EXISTS, views, indexes, triggers, JSON, stored procedures |

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
