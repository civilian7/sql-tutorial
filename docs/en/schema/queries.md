# 05. Schema Query Reference

This section shows how to query database structure (tables, views, indexes, triggers, etc.) using SQL. Even without reading schema documentation, you can explore the entire database structure with these queries.

Each database has different ways to query metadata. Compare the queries for the same information across DB tabs.

---

## Querying Table List

Check which tables exist in the database. This is the first query you run when encountering a new database.

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

**Sample Result (partial):**

| name |
|------|
| calendar |
| cart_items |
| carts |
| categories |
| complaints |
| ... (30 total) |

To also view DDL (CREATE TABLE statements):

=== "SQLite"

    ```sql
    SELECT name, sql FROM sqlite_master
    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
    ORDER BY name;
    ```

    **Sample Result (partial):**

    | name | sql |
    |------|-----|
    | customers | CREATE TABLE customers ( id INTEGER PRIMARY KEY AUTOINCREMENT, ... |
    | orders | CREATE TABLE orders ( id INTEGER PRIMARY KEY AUTOINCREMENT, ... |
    | products | CREATE TABLE products ( id INTEGER PRIMARY KEY AUTOINCREMENT, ... |

=== "MySQL"

    ```sql
    SHOW CREATE TABLE orders;
    ```

    **Sample Result:**

    | Table | Create Table |
    |-------|-------------|
    | orders | CREATE TABLE `orders` ( `id` INT NOT NULL AUTO_INCREMENT, ... |

=== "PostgreSQL"

    ```bash
    # From terminal
    pg_dump -U postgres -t orders --schema-only ecommerce
    ```

    The full DDL is output to the terminal. To query from SQL:

    ```sql
    SELECT pg_get_tabledef('orders'::regclass);
    ```

---

## Querying Column Information

Check column names, types, and NULL constraints for a specific table.

=== "SQLite"

    ```sql
    PRAGMA table_info('orders');
    ```

=== "MySQL"

    ```sql
    DESCRIBE orders;
    ```

    Or for more detail:

    ```sql
    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'orders'
    ORDER BY ORDINAL_POSITION;
    ```

=== "PostgreSQL"

    ```sql
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'orders'
    ORDER BY ordinal_position;
    ```

**Sample Result** (`orders` table, SQLite):

| cid | name | type | notnull | dflt_value | pk |
|----:|------|------|:-------:|------------|:--:|
| 0 | id | INTEGER | 0 | | 1 |
| 1 | order_number | TEXT | 1 | | 0 |
| 2 | customer_id | INTEGER | 1 | | 0 |
| 3 | address_id | INTEGER | 1 | | 0 |
| 4 | staff_id | INTEGER | 0 | | 0 |
| 5 | status | TEXT | 1 | | 0 |
| 6 | total_amount | REAL | 1 | | 0 |
| 7 | discount_amount | REAL | 1 | 0 | 0 |
| 8 | shipping_fee | REAL | 1 | 0 | 0 |
| ... | | | | | |

---

## Querying View List

Check views defined in the database.

=== "SQLite"

    ```sql
    SELECT name FROM sqlite_master
    WHERE type = 'view'
    ORDER BY name;
    ```

=== "MySQL"

    ```sql
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.VIEWS
    WHERE TABLE_SCHEMA = DATABASE();
    ```

=== "PostgreSQL"

    ```sql
    -- Regular views
    SELECT viewname FROM pg_views
    WHERE schemaname = 'public'
    ORDER BY viewname;

    -- Materialized Views
    SELECT matviewname FROM pg_matviews
    WHERE schemaname = 'public'
    ORDER BY matviewname;
    ```

**Sample Result (partial):**

| name |
|------|
| v_cart_abandonment |
| v_category_tree |
| v_coupon_effectiveness |
| v_customer_rfm |
| v_customer_summary |
| ... (18 total) |

To view a view's SQL definition:

=== "SQLite"

    ```sql
    SELECT name, sql FROM sqlite_master
    WHERE type = 'view' AND name = 'v_monthly_sales';
    ```

=== "MySQL"

    ```sql
    SELECT VIEW_DEFINITION
    FROM INFORMATION_SCHEMA.VIEWS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'v_monthly_sales';
    ```

=== "PostgreSQL"

    ```sql
    SELECT definition FROM pg_views
    WHERE viewname = 'v_monthly_sales';
    ```

---

## Querying Index List

Check indexes set on tables. Useful for query performance analysis (Lesson 22).

=== "SQLite"

    ```sql
    SELECT name, tbl_name
    FROM sqlite_master
    WHERE type = 'index'
    ORDER BY tbl_name, name;
    ```

=== "MySQL"

    ```sql
    SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME, SEQ_IN_INDEX
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
    ```

=== "PostgreSQL"

    ```sql
    SELECT tablename, indexname, indexdef
    FROM pg_indexes
    WHERE schemaname = 'public'
    ORDER BY tablename, indexname;
    ```

**Sample Result (partial):**

| name | tbl_name |
|------|----------|
| idx_calendar_year_month | calendar |
| idx_cart_items_cart_id | cart_items |
| idx_carts_customer_id | carts |
| idx_categories_parent | categories |
| idx_complaints_customer | complaints |
| ... (61 total) |

To view indexes for a specific table only:

=== "SQLite"

    ```sql
    PRAGMA index_list('orders');
    ```

=== "MySQL"

    ```sql
    SHOW INDEX FROM orders;
    ```

=== "PostgreSQL"

    ```sql
    SELECT indexname, indexdef FROM pg_indexes
    WHERE tablename = 'orders';
    ```

---

## Querying Trigger List

Check triggers defined in the database.

=== "SQLite"

    ```sql
    SELECT name, tbl_name FROM sqlite_master
    WHERE type = 'trigger'
    ORDER BY name;
    ```

=== "MySQL"

    ```sql
    SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE,
           EVENT_MANIPULATION, ACTION_TIMING
    FROM INFORMATION_SCHEMA.TRIGGERS
    WHERE TRIGGER_SCHEMA = DATABASE();
    ```

=== "PostgreSQL"

    ```sql
    SELECT tgname AS trigger_name,
           relname AS table_name,
           proname AS function_name
    FROM pg_trigger t
    JOIN pg_class c ON t.tgrelid = c.oid
    JOIN pg_proc p ON t.tgfoid = p.oid
    WHERE NOT t.tgisinternal
    ORDER BY tgname;
    ```

**Sample Result** (SQLite):

| name | tbl_name |
|------|----------|
| trg_customers_updated_at | customers |
| trg_orders_updated_at | orders |
| trg_product_price_history | products |
| trg_products_updated_at | products |
| trg_reviews_updated_at | reviews |

To view a trigger's SQL definition:

=== "SQLite"

    ```sql
    SELECT sql FROM sqlite_master
    WHERE type = 'trigger' AND name = 'trg_orders_updated_at';
    ```

=== "MySQL"

    ```sql
    SHOW CREATE TRIGGER trg_orders_updated_at;
    ```

---

## Querying Stored Procedures/Functions

=== "MySQL"

    ```sql
    SELECT ROUTINE_NAME, ROUTINE_TYPE
    FROM INFORMATION_SCHEMA.ROUTINES
    WHERE ROUTINE_SCHEMA = DATABASE()
    ORDER BY ROUTINE_TYPE, ROUTINE_NAME;
    ```

    **Sample Result:**

    | ROUTINE_NAME | ROUTINE_TYPE |
    |-------------|-------------|
    | sp_cancel_order | PROCEDURE |
    | sp_cleanup_abandoned_carts | PROCEDURE |
    | sp_place_order | PROCEDURE |
    | ... (14 total) | |

=== "PostgreSQL"

    ```sql
    SELECT routine_name, routine_type
    FROM information_schema.routines
    WHERE routine_schema = 'public'
    ORDER BY routine_type, routine_name;
    ```

    **Sample Result:**

    | routine_name | routine_type |
    |-------------|-------------|
    | refresh_materialized_views | FUNCTION |
    | sp_cancel_order | FUNCTION |
    | sp_place_order | FUNCTION |
    | ... (15 total) | |

SQLite does not support stored procedures.

---

## Querying Foreign Key Relationships

Check FK relationships between tables. Useful for understanding the ERD directly.

=== "SQLite"

    ```sql
    PRAGMA foreign_key_list('orders');
    ```

=== "MySQL"

    ```sql
    SELECT TABLE_NAME, COLUMN_NAME,
           REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = DATABASE()
      AND REFERENCED_TABLE_NAME IS NOT NULL
    ORDER BY TABLE_NAME;
    ```

=== "PostgreSQL"

    ```sql
    SELECT
        tc.table_name, kcu.column_name,
        ccu.table_name AS referenced_table,
        ccu.column_name AS referenced_column
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage ccu
        ON tc.constraint_name = ccu.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
    ORDER BY tc.table_name;
    ```

**Sample Result** (`orders` table, SQLite):

| id | seq | table | from | to |
|---:|----:|-------|------|----|
| 0 | 0 | staff | staff_id | id |
| 1 | 0 | customer_addresses | address_id | id |
| 2 | 0 | customers | customer_id | id |

---

## Table/Column Comments

Adding comments to tables or columns greatly helps others understand the schema later. GUI tools like DBeaver also display these comments.

### Writing Comments

=== "MySQL"

    ```sql
    -- Table comment
    ALTER TABLE orders COMMENT = 'Orders table';

    -- Column comment (must include column definition)
    ALTER TABLE orders
    MODIFY COLUMN status ENUM('pending','paid','preparing','shipped',
        'delivered','confirmed','cancelled','return_requested','returned')
        NOT NULL COMMENT 'Order status';
    ```

=== "PostgreSQL"

    ```sql
    -- Table comment
    COMMENT ON TABLE orders IS 'Orders table';

    -- Column comments
    COMMENT ON COLUMN orders.status IS 'Order status';
    COMMENT ON COLUMN orders.total_amount IS 'Order total amount (KRW)';
    COMMENT ON COLUMN customers.grade IS 'Customer grade: BRONZE/SILVER/GOLD/VIP';
    ```

SQLite does not support the comment feature. Use `--` comments in DDL as a substitute.

### Querying Comments

=== "MySQL"

    ```sql
    -- Table comments
    SELECT TABLE_NAME, TABLE_COMMENT
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_COMMENT != ''
    ORDER BY TABLE_NAME;

    -- Column comments
    SELECT TABLE_NAME, COLUMN_NAME, COLUMN_COMMENT
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND COLUMN_COMMENT != ''
    ORDER BY TABLE_NAME, ORDINAL_POSITION;
    ```

    **Sample Result:**

    | TABLE_NAME | COLUMN_NAME | COLUMN_COMMENT |
    |-----------|-------------|----------------|
    | orders | status | Order status |
    | orders | total_amount | Order total amount (KRW) |
    | customers | grade | Customer grade: BRONZE/SILVER/GOLD/VIP |

=== "PostgreSQL"

    ```sql
    -- Table comments
    SELECT c.relname AS table_name,
           d.description AS comment
    FROM pg_class c
    JOIN pg_description d ON c.oid = d.objoid AND d.objsubid = 0
    WHERE c.relkind = 'r'
    ORDER BY c.relname;

    -- Column comments
    SELECT c.relname AS table_name,
           a.attname AS column_name,
           d.description AS comment
    FROM pg_class c
    JOIN pg_attribute a ON c.oid = a.attrelid
    JOIN pg_description d ON c.oid = d.objoid AND a.attnum = d.objsubid
    WHERE c.relkind = 'r' AND a.attnum > 0
    ORDER BY c.relname, a.attnum;
    ```

!!! tip "Comments in Practice"
    - Adding comments to tables and columns is good practice
    - Especially for code-type columns like `status`, `type`, `grade`, including the **list of allowed values** as a comment is very useful
    - Many teams make it a rule to include comments in DDL

---

## Querying Row Counts per Table

Check the data volume of all tables at once.

=== "SQLite"

    ```sql
    SELECT 'customers' AS tbl, COUNT(*) AS cnt FROM customers
    UNION ALL
    SELECT 'orders', COUNT(*) FROM orders
    UNION ALL
    SELECT 'products', COUNT(*) FROM products
    UNION ALL
    SELECT 'reviews', COUNT(*) FROM reviews
    UNION ALL
    SELECT 'payments', COUNT(*) FROM payments
    ORDER BY cnt DESC;
    ```

=== "MySQL"

    ```sql
    SELECT TABLE_NAME, TABLE_ROWS
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_ROWS DESC;
    ```

    !!! info "TABLE_ROWS is an Estimate"
        InnoDB's `TABLE_ROWS` is an estimate, not an exact value. Use `SELECT COUNT(*)` when exact counts are needed.

=== "PostgreSQL"

    ```sql
    SELECT relname AS table_name,
           n_live_tup AS estimated_rows
    FROM pg_stat_user_tables
    ORDER BY n_live_tup DESC;
    ```

    For exact counts:

    ```sql
    SELECT COUNT(*) FROM orders;
    ```

**Sample Result** (small size, key tables):

| tbl | cnt |
|-----|----:|
| orders | 34,908 |
| payments | 34,908 |
| customers | 5,230 |
| reviews | 7,945 |
| products | 280 |
