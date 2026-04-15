# 05. Verify and First Query

Verify that the database was generated correctly.

## Open in a SQL Tool

If you want to use multiple DBs in a single tool, we recommend **[DBeaver](https://dbeaver.io/download/)** (free, open source). It supports SQLite, MySQL, PostgreSQL, Oracle, and SQL Server.

!!! tip "ezQuery Coming Soon"
    Once **ezQuery**, currently in development, is released, it will become the official recommended tool for this tutorial. It will include the tutorial database as a built-in sample, allowing you to start practicing immediately after installation.

=== "SQLite"

    | Tool | How to Open |
    |------|-------------|
    | **DBeaver** (recommended) | New Connection > SQLite > Select `output/ecommerce-ko.db` file |
    | DB Browser for SQLite | [sqlitebrowser.org](https://sqlitebrowser.org/dl/) > Open Database > ecommerce-ko.db |
    | Command line | `sqlite3 output/ecommerce-ko.db` |

=== "MySQL"

    | Tool | How to Connect |
    |------|----------------|
    | **DBeaver** (recommended) | New Connection > MySQL > localhost:3306 > ecommerce |
    | MySQL Workbench | [dev.mysql.com](https://dev.mysql.com/downloads/workbench/) > New Connection > localhost:3306 |
    | Command line | `mysql -u root -p ecommerce` |

=== "PostgreSQL"

    | Tool | How to Connect |
    |------|----------------|
    | **DBeaver** (recommended) | New Connection > PostgreSQL > localhost:5432 > ecommerce |
    | pgAdmin | [pgadmin.org](https://www.pgadmin.org/download/) > Add Server > localhost:5432 |
    | Command line | `psql -U postgres ecommerce` |

## Quick Check from the Command Line

You can verify directly from the terminal without opening a GUI tool.

=== "SQLite"

    ```bash
    sqlite3 output/ecommerce-ko.db "SELECT COUNT(*) FROM customers;"
    ```

    If `5230` is displayed, everything is correct.

=== "MySQL"

    ```bash
    mysql -u root -p -e "SELECT COUNT(*) FROM ecommerce.customers;"
    ```

=== "PostgreSQL"

    ```bash
    psql -U postgres -d ecommerce -c "SELECT COUNT(*) FROM customers;"
    ```

## Run Your First Query

Enter and run the following queries in your SQL tool.

### Check Table List

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

If the table list is displayed, everything is working correctly.

### Check Data

The same query works for all three DBs:

```sql
-- Preview customer data
SELECT name, email, grade, point_balance
FROM customers
LIMIT 5;
```

```sql
-- Overall data volume
SELECT
    (SELECT COUNT(*) FROM customers) AS customer_count,
    (SELECT COUNT(*) FROM products) AS product_count,
    (SELECT COUNT(*) FROM orders) AS order_count,
    (SELECT COUNT(*) FROM reviews) AS review_count;
```

If the results display correctly, you're all set.

## Automated Verification Script

Instead of manual checking, you can run the verification script to check connection, tables, views, triggers, row counts, and FK integrity all at once.

=== "SQLite"

    ```bash
    python verify.py
    ```

=== "MySQL"

    ```bash
    python verify.py --target mysql
    ```

=== "PostgreSQL"

    ```bash
    python verify.py --target postgresql
    ```

=== "All"

    ```bash
    python verify.py --all
    ```

If everything is normal, the output will look like this:

```
==================================================
[VERIFY] SQL Tutorial Environment Verification
==================================================
  [OK] Python 3.12.x
  [OK] File exists (80.7 MB)
  [OK] Connection successful
  [OK] 30 tables confirmed
  [OK] 18 views confirmed
  [OK] 5 triggers confirmed
  [OK] customers: 5,230 rows
  [OK] orders: 34,908 rows
  ...
  [OK] FK integrity confirmed (orders → customers)

==================================================
[OK] Verification complete: 13/13 passed
==================================================
```

!!! warning "If Verification Fails"
    If there are `[FAIL]` items, go back to the relevant step:

    - File not found → Run `generate.py` in [03. Generate Data](03-generate.md)
    - Connection failed → Check server status in [02. Install the Database](02-database.md)
    - Missing tables/views → Check if SQL files were applied manually

[← 04. Advanced Generator Options](04-generate-advanced.md){ .md-button }
[Lesson 00: Introduction to SQL →](../beginner/00-introduction.md){ .md-button .md-button--primary }
