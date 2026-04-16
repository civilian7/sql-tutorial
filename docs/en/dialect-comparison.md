# SQL Differences by Database — Cheat Sheet

The SQL in this tutorial is written for SQLite. Each lesson covers DB-specific differences using MySQL/PostgreSQL tabs, so this page serves as a **quick-reference summary table**.

> Rather than writing SQL that works across all databases, it's more efficient to **leverage each DB's native syntax**.

## Lesson-by-Lesson DB Difference Guide

These are topics covered in detail with SQLite/MySQL/PostgreSQL tabs in each lesson. Refer to the respective lessons.

| Topic | Lesson | Key Difference |
|-------|--------|----------------|
| Paging | [Lesson 03](beginner/03-sort-limit.md) | LIMIT vs FETCH FIRST (ANSI) |
| NULL Handling | [Lesson 06](beginner/06-null.md) | COALESCE (standard) vs IFNULL vs ISNULL vs NVL |
| CASE Expressions | [Lesson 07](beginner/07-case.md) | IIF (SQLite) vs IF (MySQL) vs CASE (PG) |
| JOIN | [Lessons 08-09](intermediate/08-inner-join.md) | Syntax identical, FULL OUTER JOIN support varies |
| Subqueries | [Lesson 10](intermediate/10-subqueries.md) | Syntax nearly identical |
| Date/Time | [Lesson 11](intermediate/11-datetime.md) | SUBSTR vs YEAR() vs EXTRACT(), julianday vs DATEDIFF |
| Strings | [Lesson 12](intermediate/12-string.md) | `\|\|` vs CONCAT(), INSTR vs LOCATE vs POSITION |
| Numeric/Conversion/Conditional | [Lesson 13](intermediate/13-utility-functions.md) | RANDOM vs RAND(), GREATEST/LEAST support varies |
| UNION/INTERSECT/EXCEPT | [Lesson 14](intermediate/14-union.md) | Syntax identical, EXCEPT vs MINUS (Oracle) |
| DML (UPSERT) | [Lesson 15](intermediate/15-dml.md) | ON CONFLICT vs ON DUPLICATE KEY |
| DDL | [Lesson 16](intermediate/16-ddl.md) | AUTOINCREMENT vs AUTO_INCREMENT vs GENERATED |
| Transactions | [Lesson 17](intermediate/17-transactions.md) | BEGIN vs START TRANSACTION |
| Window Functions | [Lesson 18](advanced/18-window.md) | Syntax identical, minimum version differences |
| CTE | [Lesson 19](advanced/19-cte.md) | WITH RECURSIVE (SQLite/MySQL/PG) vs WITH only (MSSQL/Oracle) |
| Views | [Lesson 22](advanced/22-views.md) | CREATE OR REPLACE support varies |
| Indexes | [Lesson 23](advanced/23-indexes.md) | EXPLAIN syntax, partial index support |
| Triggers | [Lesson 24](advanced/24-triggers.md) | SQLite: BEGIN...END, PG: function + trigger separation |
| JSON | [Lesson 25](advanced/25-json.md) | json_extract vs ->>, JSONB (PG) |
| Stored Procedures | [Lesson 26](advanced/26-stored-procedures.md) | SQLite unsupported, DELIMITER (MySQL), PL/pgSQL (PG) |

---

## Data Type Comparison

| Purpose | SQLite | MySQL | PostgreSQL | SQL Server | Oracle |
|---------|--------|-------|------------|------------|--------|
| Integer | INTEGER | INT | INTEGER | INT | NUMBER(10) |
| Fixed-point | REAL | DECIMAL(12,2) | NUMERIC(12,2) | DECIMAL(12,2) | NUMBER(12,2) |
| Floating-point | REAL | DOUBLE | DOUBLE PRECISION | FLOAT | BINARY_DOUBLE |
| Short string | TEXT | VARCHAR(200) | VARCHAR(200) | NVARCHAR(200) | VARCHAR2(200) |
| Long text | TEXT | TEXT | TEXT | NVARCHAR(MAX) | CLOB |
| Date/Time | TEXT (ISO 8601) | DATETIME | TIMESTAMP | DATETIME2 | TIMESTAMP |
| Boolean | INTEGER (0/1) | TINYINT(1) | BOOLEAN | BIT | NUMBER(1) |
| JSON | TEXT + json functions | JSON | JSONB | NVARCHAR(MAX) | CLOB |
| Binary | BLOB | BLOB | BYTEA | VARBINARY(MAX) | BLOB |
| UUID | TEXT | CHAR(36) | UUID | UNIQUEIDENTIFIER | RAW(16) |

> SQLite uses a dynamic type system. The type names above represent "type affinity" — in practice, any value can be stored.

---

## Identifier Quoting

When wrapping identifiers that contain reserved words or spaces:

| DB | Syntax | Example |
|----|--------|---------|
| SQLite | Double quotes or backticks | `"order"` or `` `order` `` |
| MySQL | Backticks (default) | `` `order` `` |
| PostgreSQL | Double quotes | `"order"` (enables case sensitivity) |
| SQL Server | Square brackets | `[order]` |
| Oracle | Double quotes | `"ORDER"` (note case sensitivity) |

!!! tip "Recommendation"
    Avoid using reserved words as identifiers when possible. Using plural forms like `orders` instead of `order`, or `users` instead of `user`, is safe without quoting.

---

## Auto-Increment Comparison

| DB | Syntax | Notes |
|----|--------|-------|
| SQLite | `INTEGER PRIMARY KEY AUTOINCREMENT` | ROWID-based, AUTOINCREMENT is optional |
| MySQL | `INT AUTO_INCREMENT PRIMARY KEY` | One per table, ENGINE=InnoDB |
| PostgreSQL | `INTEGER GENERATED ALWAYS AS IDENTITY` | SQL standard. SERIAL is legacy |
| SQL Server | `INT IDENTITY(1,1) PRIMARY KEY` | |
| Oracle | `NUMBER GENERATED ALWAYS AS IDENTITY` | 12c+. Previously: SEQUENCE + TRIGGER |

Details: [Lesson 16 DDL](intermediate/16-ddl.md)

---

## MERGE Statement

`MERGE` is an ANSI SQL standard that conditionally performs INSERT/UPDATE/DELETE in a single statement.

| DB | Support | Alternative Syntax |
|----|---------|-------------------|
| SQLite | Not supported | `ON CONFLICT` |
| MySQL | Not supported | `ON DUPLICATE KEY UPDATE` |
| PostgreSQL | 15+ (partial) | `ON CONFLICT` recommended |
| SQL Server | 2008+ | Full support |
| Oracle | 9i+ | Full support |

=== "SQL Server"

    ```sql
    MERGE INTO products AS target
    USING staging_products AS source
    ON target.sku = source.sku
    WHEN MATCHED AND source.is_active = 0 THEN
        DELETE
    WHEN MATCHED THEN
        UPDATE SET name = source.name, price = source.price
    WHEN NOT MATCHED THEN
        INSERT (sku, name, price)
        VALUES (source.sku, source.name, source.price);
    ```

=== "Oracle"

    ```sql
    MERGE INTO products target
    USING staging_products source
    ON (target.sku = source.sku)
    WHEN MATCHED THEN
        UPDATE SET name = source.name, price = source.price
    WHEN NOT MATCHED THEN
        INSERT (sku, name, price)
        VALUES (source.sku, source.name, source.price);
    ```

UPSERT details: [Lesson 15 DML](intermediate/15-dml.md)

---

## Feature Support Version Matrix

| Feature | SQLite | MySQL | PostgreSQL | SQL Server | Oracle |
|---------|--------|-------|------------|------------|--------|
| Window Functions | 3.25+ | 8.0+ | 8.4+ | 2005+ | 8i+ |
| CTE (WITH) | 3.8.3+ | 8.0+ | 8.4+ | 2005+ | 11gR2+ |
| Recursive CTE | 3.8.3+ | 8.0+ | 8.4+ | 2005+ | 11gR2+ |
| JSON Functions | 3.38+ | 5.7+ | 9.2+ | 2016+ | 12c+ |
| FULL OUTER JOIN | 3.39+ | Not supported | Supported | Supported | Supported |
| INTERSECT/EXCEPT | 3.34+ | 8.0.31+ | Supported | Supported | Supported (MINUS) |
| Partial Index | 3.8+ | Not supported | Supported | Supported (filtered) | Not supported |
| UPSERT | 3.24+ | Supported | 9.5+ | MERGE | MERGE |
| Stored Procedures | Not supported | Supported | Supported | Supported | Supported |
| Triggers | Supported | Supported | Supported | Supported | Supported |
| SEQUENCE | Not supported | Not supported | Supported | Supported | Supported |

---

## Tutorial SQL Conversion Checklist

Items to check when running this tutorial's SQLite queries on other databases:

| # | Check Item | SQLite Original | MySQL | PostgreSQL | SQL Server |
|--:|------------|-----------------|-------|------------|------------|
| 1 | Row limit | `LIMIT 10` | Same | Same | `FETCH NEXT 10 ROWS ONLY` |
| 2 | Date extraction | `SUBSTR(col, 1, 7)` | `DATE_FORMAT(col, '%Y-%m')` | `TO_CHAR(col, 'YYYY-MM')` | `FORMAT(col, 'yyyy-MM')` |
| 3 | Days elapsed | `JULIANDAY(a) - JULIANDAY(b)` | `DATEDIFF(a, b)` | `a::date - b::date` | `DATEDIFF(DAY, b, a)` |
| 4 | Date addition | `DATE('now', '+30 days')` | `DATE_ADD(NOW(), INTERVAL 30 DAY)` | `CURRENT_DATE + INTERVAL '30 days'` | `DATEADD(DAY, 30, GETDATE())` |
| 5 | NULL replacement | `IFNULL(x, y)` | `IFNULL(x, y)` | `COALESCE(x, y)` | `ISNULL(x, y)` |
| 6 | String concatenation | `a \|\| b` | `CONCAT(a, b)` | `a \|\| b` | `CONCAT(a, b)` |
| 7 | Boolean | `is_active = 1` | Same | `is_active = TRUE` | Same |
| 8 | Type casting | `CAST(x AS INTEGER)` | `CAST(x AS SIGNED)` | `x::integer` | `CAST(x AS INT)` |
| 9 | Current time | `datetime('now')` | `NOW()` | `NOW()` | `GETDATE()` |
| 10 | AUTOINCREMENT | `INTEGER PRIMARY KEY` | `INT AUTO_INCREMENT` | `GENERATED ALWAYS AS IDENTITY` | `INT IDENTITY(1,1)` |
| 11 | Random | `RANDOM()` | `RAND()` | `RANDOM()` | `NEWID()` |
| 12 | Regex | `GLOB '*[0-9]*'` | `REGEXP '[0-9]'` | `~ '[0-9]'` | `LIKE '%[0-9]%'` |
