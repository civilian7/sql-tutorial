# SQL Syntax Across Databases

This tutorial's SQL is written for SQLite. Use this reference when running the same queries on other databases.

> Rather than writing SQL that works on every DB, it's more effective to **use each DB's native syntax**.

---

## Pagination (Row Limiting)

The most frequently encountered difference.

=== "SQLite / MySQL / PostgreSQL"

    ```sql
    SELECT * FROM products
    ORDER BY price DESC
    LIMIT 10 OFFSET 20;
    ```

=== "SQL Server"

    ```sql
    SELECT * FROM products
    ORDER BY price DESC
    OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;
    ```

=== "Oracle"

    ```sql
    -- Oracle 12c+
    SELECT * FROM products
    ORDER BY price DESC
    OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;

    -- Oracle 11g and earlier
    SELECT * FROM (
        SELECT t.*, ROWNUM AS rn
        FROM (SELECT * FROM products ORDER BY price DESC) t
        WHERE ROWNUM <= 30
    ) WHERE rn > 20;
    ```

---

## Auto-Increment (Primary Key)

=== "SQLite"

    ```sql
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    ```

=== "MySQL"

    ```sql
    CREATE TABLE products (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(200) NOT NULL
    ) ENGINE=InnoDB;
    ```

=== "PostgreSQL"

    ```sql
    -- Option 1: GENERATED (SQL standard)
    CREATE TABLE products (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name VARCHAR(200) NOT NULL
    );

    -- Option 2: SERIAL (PG tradition)
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(200) NOT NULL
    );
    ```

=== "SQL Server"

    ```sql
    CREATE TABLE products (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(200) NOT NULL
    );
    ```

=== "Oracle"

    ```sql
    -- Oracle 12c+
    CREATE TABLE products (
        id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name VARCHAR2(200) NOT NULL
    );

    -- Oracle 11g and earlier: SEQUENCE + TRIGGER
    CREATE SEQUENCE seq_products START WITH 1;
    ```

---

## Date/Time Functions

### Current Date/Time

| DB | Current Date | Current Timestamp |
|----|-------------|-------------------|
| SQLite | `DATE('now')` | `DATETIME('now')` |
| MySQL | `CURDATE()` | `NOW()` |
| PostgreSQL | `CURRENT_DATE` | `NOW()` or `CURRENT_TIMESTAMP` |
| SQL Server | `CAST(GETDATE() AS DATE)` | `GETDATE()` |
| Oracle | `SYSDATE` | `SYSTIMESTAMP` |

### Extracting Year/Month/Day

=== "SQLite"

    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4)  AS year,
        SUBSTR(ordered_at, 6, 2)  AS month,
        STRFTIME('%w', ordered_at) AS day_of_week
    FROM orders;
    ```

=== "MySQL"

    ```sql
    SELECT
        YEAR(ordered_at)      AS year,
        MONTH(ordered_at)     AS month,
        DAYOFWEEK(ordered_at) AS day_of_week
    FROM orders;
    ```

=== "PostgreSQL"

    ```sql
    SELECT
        EXTRACT(YEAR FROM ordered_at)  AS year,
        EXTRACT(MONTH FROM ordered_at) AS month,
        EXTRACT(DOW FROM ordered_at)   AS day_of_week
    FROM orders;
    ```

=== "SQL Server"

    ```sql
    SELECT
        YEAR(ordered_at)       AS year,
        MONTH(ordered_at)      AS month,
        DATEPART(dw, ordered_at) AS day_of_week
    FROM orders;
    ```

=== "Oracle"

    ```sql
    SELECT
        EXTRACT(YEAR FROM ordered_at)  AS year,
        EXTRACT(MONTH FROM ordered_at) AS month,
        TO_CHAR(ordered_at, 'D')       AS day_of_week
    FROM orders;
    ```

### Date Arithmetic

=== "SQLite"

    ```sql
    -- 30 days from now
    SELECT DATE('now', '+30 days');
    -- Days between two dates
    SELECT JULIANDAY('2025-12-31') - JULIANDAY('2025-01-01');
    ```

=== "MySQL"

    ```sql
    SELECT DATE_ADD(NOW(), INTERVAL 30 DAY);
    SELECT DATEDIFF('2025-12-31', '2025-01-01');
    ```

=== "PostgreSQL"

    ```sql
    SELECT CURRENT_DATE + INTERVAL '30 days';
    SELECT '2025-12-31'::DATE - '2025-01-01'::DATE;
    ```

=== "SQL Server"

    ```sql
    SELECT DATEADD(DAY, 30, GETDATE());
    SELECT DATEDIFF(DAY, '2025-01-01', '2025-12-31');
    ```

=== "Oracle"

    ```sql
    SELECT SYSDATE + 30 FROM DUAL;
    SELECT TO_DATE('2025-12-31') - TO_DATE('2025-01-01') FROM DUAL;
    ```

---

## String Functions

### Concatenation

| DB | Syntax |
|----|--------|
| SQLite / PostgreSQL / Oracle | `'Hello' \|\| ' ' \|\| 'World'` |
| MySQL | `CONCAT('Hello', ' ', 'World')` |
| SQL Server | `CONCAT('Hello', ' ', 'World')` or `'Hello' + ' ' + 'World'` |

### Substring

| DB | Syntax |
|----|--------|
| SQLite / PostgreSQL / Oracle | `SUBSTR(name, 1, 5)` |
| MySQL | `SUBSTRING(name, 1, 5)` or `SUBSTR(name, 1, 5)` |
| SQL Server | `SUBSTRING(name, 1, 5)` |

### String Aggregation (GROUP_CONCAT)

=== "SQLite"

    ```sql
    SELECT category_id, GROUP_CONCAT(name, ', ')
    FROM products
    GROUP BY category_id;
    ```

=== "MySQL"

    ```sql
    SELECT category_id, GROUP_CONCAT(name SEPARATOR ', ')
    FROM products
    GROUP BY category_id;
    ```

=== "PostgreSQL"

    ```sql
    SELECT category_id, STRING_AGG(name, ', ')
    FROM products
    GROUP BY category_id;
    ```

=== "SQL Server"

    ```sql
    SELECT category_id, STRING_AGG(name, ', ')
    FROM products
    GROUP BY category_id;
    ```

=== "Oracle"

    ```sql
    SELECT category_id, LISTAGG(name, ', ') WITHIN GROUP (ORDER BY name)
    FROM products
    GROUP BY category_id;
    ```

---

## NULL Handling

### Default Value Substitution

| DB | Syntax | Example |
|----|--------|---------|
| All DBs | `COALESCE(x, y)` | `COALESCE(notes, 'N/A')` |
| SQLite | `IFNULL(x, y)` | `IFNULL(notes, 'N/A')` |
| MySQL | `IFNULL(x, y)` | `IFNULL(notes, 'N/A')` |
| SQL Server | `ISNULL(x, y)` | `ISNULL(notes, 'N/A')` |
| Oracle | `NVL(x, y)` | `NVL(notes, 'N/A')` |

> **Recommendation:** `COALESCE` is the SQL standard and works on every DB. Use it when portability matters.

---

## Data Type Mapping

| Purpose | SQLite | MySQL | PostgreSQL | SQL Server | Oracle |
|---------|--------|-------|------------|------------|--------|
| Integer | INTEGER | INT | INTEGER | INT | NUMBER(10) |
| Decimal | REAL | DECIMAL(12,2) | NUMERIC(12,2) | DECIMAL(12,2) | NUMBER(12,2) |
| Short string | TEXT | VARCHAR(200) | VARCHAR(200) | NVARCHAR(200) | VARCHAR2(200) |
| Long text | TEXT | TEXT | TEXT | NVARCHAR(MAX) | CLOB |
| Date/Time | TEXT (ISO 8601) | DATETIME | TIMESTAMP | DATETIME2 | DATE / TIMESTAMP |
| Boolean | INTEGER (0/1) | TINYINT(1) | BOOLEAN | BIT | NUMBER(1) |

---

## Identifier Quoting

When identifiers contain reserved words or spaces:

| DB | Syntax | Example |
|----|--------|---------|
| SQLite / MySQL | Backticks or double quotes | `` `order` `` or `"order"` |
| PostgreSQL | Double quotes | `"order"` |
| SQL Server | Brackets or double quotes | `[order]` or `"order"` |
| Oracle | Double quotes | `"ORDER"` (case-sensitive!) |

---

## UPSERT (INSERT or UPDATE)

=== "SQLite"

    ```sql
    INSERT INTO products (id, name, price)
    VALUES (1, 'Keyboard', 89.99)
    ON CONFLICT(id) DO UPDATE SET
        name = excluded.name,
        price = excluded.price;
    ```

=== "MySQL"

    ```sql
    INSERT INTO products (id, name, price)
    VALUES (1, 'Keyboard', 89.99)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        price = VALUES(price);
    ```

=== "PostgreSQL"

    ```sql
    INSERT INTO products (id, name, price)
    VALUES (1, 'Keyboard', 89.99)
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        price = EXCLUDED.price;
    ```

=== "SQL Server"

    ```sql
    MERGE INTO products AS target
    USING (VALUES (1, 'Keyboard', 89.99)) AS source(id, name, price)
    ON target.id = source.id
    WHEN MATCHED THEN
        UPDATE SET name = source.name, price = source.price
    WHEN NOT MATCHED THEN
        INSERT (id, name, price) VALUES (source.id, source.name, source.price);
    ```

=== "Oracle"

    ```sql
    MERGE INTO products target
    USING (SELECT 1 AS id, 'Keyboard' AS name, 89.99 AS price FROM DUAL) source
    ON (target.id = source.id)
    WHEN MATCHED THEN
        UPDATE SET name = source.name, price = source.price
    WHEN NOT MATCHED THEN
        INSERT (id, name, price) VALUES (source.id, source.name, source.price);
    ```

---

## Window Function Support

| Feature | SQLite | MySQL | PostgreSQL | SQL Server | Oracle |
|---------|--------|-------|------------|------------|--------|
| ROW_NUMBER | 3.25+ | 8.0+ | 8.4+ | 2005+ | 8i+ |
| RANK / DENSE_RANK | 3.25+ | 8.0+ | 8.4+ | 2005+ | 8i+ |
| LAG / LEAD | 3.25+ | 8.0+ | 8.4+ | 2012+ | 8i+ |
| NTILE | 3.25+ | 8.0+ | 8.4+ | 2005+ | 8i+ |
| SUM/AVG OVER | 3.25+ | 8.0+ | 8.4+ | 2005+ | 8i+ |

> All window function queries in this tutorial work on the minimum versions listed above.

---

## CTE and Recursive CTE

| Feature | SQLite | MySQL | PostgreSQL | SQL Server | Oracle |
|---------|--------|-------|------------|------------|--------|
| WITH (CTE) | 3.8.3+ | 8.0+ | 8.4+ | 2005+ | 11gR2+ |
| WITH RECURSIVE | 3.8.3+ | 8.0+ | 8.4+ | 2005+ | 11gR2+ |

**RECURSIVE keyword difference:**

=== "SQLite / MySQL / PostgreSQL"

    ```sql
    WITH RECURSIVE category_tree AS (
        SELECT id, name, parent_id, 0 AS depth
        FROM categories WHERE parent_id IS NULL
        UNION ALL
        SELECT c.id, c.name, c.parent_id, ct.depth + 1
        FROM categories c
        INNER JOIN category_tree ct ON c.parent_id = ct.id
    )
    SELECT * FROM category_tree;
    ```

=== "SQL Server / Oracle"

    ```sql
    -- RECURSIVE keyword not needed
    WITH category_tree AS (
        SELECT id, name, parent_id, 0 AS depth
        FROM categories WHERE parent_id IS NULL
        UNION ALL
        SELECT c.id, c.name, c.parent_id, ct.depth + 1
        FROM categories c
        INNER JOIN category_tree ct ON c.parent_id = ct.id
    )
    SELECT * FROM category_tree;
    ```

---

## JSON Queries

Each database provides its own functions for working with JSON data.

=== "SQLite"

    ```sql
    SELECT name, JSON_EXTRACT(specs, '$.cpu') AS cpu
    FROM products
    WHERE specs IS NOT NULL;
    ```

=== "MySQL"

    ```sql
    SELECT name, JSON_EXTRACT(specs, '$.cpu') AS cpu
    FROM products
    WHERE specs IS NOT NULL;
    -- or: specs->'$.cpu'
    ```

=== "PostgreSQL"

    ```sql
    SELECT name, specs->>'cpu' AS cpu
    FROM products
    WHERE specs IS NOT NULL;
    ```

---

## EXPLAIN / Query Plan

Use execution plans to analyze query performance.

=== "SQLite"

    ```sql
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 42;
    ```

=== "MySQL"

    ```sql
    EXPLAIN
    SELECT * FROM orders WHERE customer_id = 42;
    -- or: EXPLAIN ANALYZE (MySQL 8.0.18+)
    ```

=== "PostgreSQL"

    ```sql
    EXPLAIN ANALYZE
    SELECT * FROM orders WHERE customer_id = 42;
    ```

=== "SQL Server"

    ```sql
    SET STATISTICS IO ON;
    SELECT * FROM orders WHERE customer_id = 42;
    -- or: SET SHOWPLAN_TEXT ON;
    ```

---

## Stored Procedures

Store reusable logic on the server and call it by name. SQLite does not support stored procedures.

=== "MySQL"

    ```sql
    DELIMITER //
    CREATE PROCEDURE sp_example(IN p_id INT)
    BEGIN
        SELECT * FROM customers WHERE id = p_id;
    END //
    DELIMITER ;

    CALL sp_example(42);
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE FUNCTION sp_example(p_id INT)
    RETURNS TABLE(name TEXT, email TEXT) AS $$
    BEGIN
        RETURN QUERY SELECT c.name, c.email
        FROM customers c WHERE c.id = p_id;
    END;
    $$ LANGUAGE plpgsql;

    SELECT * FROM sp_example(42);
    ```

=== "SQL Server"

    ```sql
    CREATE PROCEDURE sp_example @p_id INT
    AS
    BEGIN
        SELECT * FROM customers WHERE id = @p_id;
    END;

    EXEC sp_example @p_id = 42;
    ```

---

## Trigger Syntax

Triggers execute automatically when data changes. See [Lesson 22](advanced/22-triggers.md) for details.

=== "SQLite"

    ```sql
    CREATE TRIGGER trg_example AFTER INSERT ON orders
    BEGIN
        UPDATE products SET stock_qty = stock_qty - NEW.quantity WHERE id = NEW.product_id;
    END;
    ```

=== "MySQL"

    ```sql
    DELIMITER //
    CREATE TRIGGER trg_example AFTER INSERT ON order_items
    FOR EACH ROW
    BEGIN
        UPDATE products SET stock_qty = stock_qty - NEW.quantity WHERE id = NEW.product_id;
    END //
    DELIMITER ;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE FUNCTION fn_example() RETURNS TRIGGER AS $$
    BEGIN
        UPDATE products SET stock_qty = stock_qty - NEW.quantity WHERE id = NEW.product_id;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_example AFTER INSERT ON order_items
    FOR EACH ROW EXECUTE FUNCTION fn_example();
    ```

---

## Tutorial SQL Conversion Checklist

When running this tutorial's queries on another DB:

| # | Check | SQLite Original | Convert To |
|--:|-------|----------------|------------|
| 1 | LIMIT/OFFSET | `LIMIT 10` | MSSQL/Oracle: `FETCH NEXT 10 ROWS ONLY` |
| 2 | Date extraction | `SUBSTR(ordered_at, 1, 7)` | MySQL: `DATE_FORMAT(ordered_at, '%Y-%m')` |
| 3 | Days elapsed | `JULIANDAY(a) - JULIANDAY(b)` | MySQL: `DATEDIFF(a, b)` |
| 4 | Date arithmetic | `DATE('now', '+30 days')` | PG: `CURRENT_DATE + INTERVAL '30 days'` |
| 5 | IFNULL | `IFNULL(x, y)` | MSSQL: `ISNULL`, Oracle: `NVL`, Standard: `COALESCE` |
| 6 | String concat | `a \|\| b` | MySQL/MSSQL: `CONCAT(a, b)` |
| 7 | Boolean | `is_active = 1` | PG: `is_active = TRUE` |
| 8 | Type casting | `CAST(x AS INTEGER)` | PG: `x::INTEGER`, Oracle: `TO_NUMBER(x)` |
