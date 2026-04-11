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
```

=== "SQLite (default)"

    ```bash
    python generate.py --size small
    ```

    Creates `output/ecommerce-en.db` (~80MB, 687K rows). Takes about 20 seconds.

=== "MySQL"

    ```bash
    python generate.py --size small --target mysql
    ```

    Creates `output/mysql/` with `schema.sql`, `data.sql`, and `procedures.sql`.

    To apply directly to a running server:

    ```bash
    python generate.py --size small --target mysql --apply --ask-password
    ```

=== "PostgreSQL"

    ```bash
    python generate.py --size small --target postgresql
    ```

    Creates `output/postgresql/` with `schema.sql`, `data.sql`, and `procedures.sql`.

    To apply directly to a running server:

    ```bash
    python generate.py --size small --target postgresql --apply --ask-password
    ```

=== "All at once"

    ```bash
    python generate.py --size small --all
    ```

    Generates SQLite DB + MySQL SQL + PostgreSQL SQL in one go.

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

??? info "Additional Options"
    ```bash
    python generate.py --size small --locale en    # English data
    python generate.py --size small --dirty-data   # Noisy data for cleaning practice
    python generate.py --size medium               # Large dataset (7M rows)
    ```
    See the [Generator Reference](generator-guide.md) for all options.

## 4. Open in a SQL Tool

=== "SQLite"

    **If this is your first time, we recommend DB Browser for SQLite** — it's free and easy to install.

    | Tool | Install | Open |
    |------|---------|------|
    | **DB Browser for SQLite** (recommended) | [sqlitebrowser.org](https://sqlitebrowser.org/dl/) | Open Database > ecommerce-en.db |
    | DBeaver | [dbeaver.io](https://dbeaver.io/download/) | New Connection > SQLite > select file |
    | Command line | (no install needed) | `sqlite3 output/ecommerce-en.db` |

=== "MySQL"

    Requires MySQL 8.0 or later.

    | Tool | Install | Connect |
    |------|---------|---------|
    | MySQL Workbench | [dev.mysql.com](https://dev.mysql.com/downloads/workbench/) | New Connection > localhost:3306 |
    | DBeaver | [dbeaver.io](https://dbeaver.io/download/) | New Connection > MySQL > enter host/port |
    | Command line | (included with MySQL) | `mysql -u root -p ecommerce` |

    If you generated SQL files without `--apply`, load them manually:

    ```bash
    mysql -u root -p < output/mysql/schema.sql
    mysql -u root -p ecommerce < output/mysql/data.sql
    mysql -u root -p ecommerce < output/mysql/procedures.sql
    ```

=== "PostgreSQL"

    Requires PostgreSQL 14 or later.

    | Tool | Install | Connect |
    |------|---------|---------|
    | pgAdmin | [pgadmin.org](https://www.pgadmin.org/download/) | Add Server > localhost:5432 |
    | DBeaver | [dbeaver.io](https://dbeaver.io/download/) | New Connection > PostgreSQL > enter host/port |
    | Command line | (included with PostgreSQL) | `psql -U postgres ecommerce` |

    If you generated SQL files without `--apply`, load them manually:

    ```bash
    psql -U postgres -f output/postgresql/schema.sql
    psql -U postgres ecommerce -f output/postgresql/data.sql
    psql -U postgres ecommerce -f output/postgresql/procedures.sql
    ```

## 5. Run Your First Queries

Verify the database was created correctly. Type the following in your SQL tool and execute.

**Check the table list:**

=== "SQLite"

    ```sql
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
    ORDER BY name;
    ```

=== "MySQL"

    ```sql
    SHOW TABLES;
    ```

=== "PostgreSQL"

    ```sql
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename;
    ```

You should see the full table list.

**Check the data:** (same across all three databases)

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

---

## Learn More

- [Database Schema](schema/index.md) — Full table and column details
- [Generator Reference](generator-guide.md) — All CLI options, config files
- [DB SQL Differences](dialect-comparison.md) — SQLite vs MySQL vs PostgreSQL syntax

[← Home](index.md){ .md-button }
[Lesson 1: SELECT Basics →](beginner/01-select.md){ .md-button .md-button--primary }
