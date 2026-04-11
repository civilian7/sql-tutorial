# 데이터베이스별 SQL 차이

이 튜토리얼의 SQL은 SQLite 기준으로 작성되었습니다. 다른 데이터베이스에서 같은 쿼리를 실행하려면 아래 차이점을 참고하세요.

> 모든 DB에서 동작하는 SQL을 작성하는 것보다, **각 DB의 네이티브 문법**을 활용하는 것이 더 효율적입니다.

---

## 페이징 (행 제한)

가장 자주 부딪히는 차이입니다.

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

    -- Oracle 11g 이하
    SELECT * FROM (
        SELECT t.*, ROWNUM AS rn
        FROM (SELECT * FROM products ORDER BY price DESC) t
        WHERE ROWNUM <= 30
    ) WHERE rn > 20;
    ```

---

## 자동 증가 (Primary Key)

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
    -- 방법 1: GENERATED (SQL 표준)
    CREATE TABLE products (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name VARCHAR(200) NOT NULL
    );

    -- 방법 2: SERIAL (PG 전통)
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

    -- Oracle 11g 이하: SEQUENCE + TRIGGER
    CREATE SEQUENCE seq_products START WITH 1;
    ```

---

## 날짜/시간 함수

### 현재 날짜/시간

| DB | 현재 날짜 | 현재 시각 |
|----|-----------|-----------|
| SQLite | `DATE('now')` | `DATETIME('now')` |
| MySQL | `CURDATE()` | `NOW()` |
| PostgreSQL | `CURRENT_DATE` | `NOW()` 또는 `CURRENT_TIMESTAMP` |
| SQL Server | `CAST(GETDATE() AS DATE)` | `GETDATE()` |
| Oracle | `SYSDATE` | `SYSTIMESTAMP` |

### 연/월/일 추출

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

### 날짜 연산

=== "SQLite"

    ```sql
    -- 30일 후
    SELECT DATE('now', '+30 days');
    -- 두 날짜 사이 일수
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

## 문자열 함수

### 연결 (Concatenation)

| DB | 문법 |
|----|------|
| SQLite / PostgreSQL / Oracle | `'Hello' \|\| ' ' \|\| 'World'` |
| MySQL | `CONCAT('Hello', ' ', 'World')` |
| SQL Server | `CONCAT('Hello', ' ', 'World')` 또는 `'Hello' + ' ' + 'World'` |

### 부분 문자열

| DB | 문법 |
|----|------|
| SQLite / PostgreSQL / Oracle | `SUBSTR(name, 1, 5)` |
| MySQL | `SUBSTRING(name, 1, 5)` 또는 `SUBSTR(name, 1, 5)` |
| SQL Server | `SUBSTRING(name, 1, 5)` |

### 그룹 내 문자열 합치기

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

## NULL 처리

### 기본값 대체

| DB | 문법 | 예시 |
|----|------|------|
| 모든 DB | `COALESCE(x, y)` | `COALESCE(notes, '없음')` |
| SQLite | `IFNULL(x, y)` | `IFNULL(notes, '없음')` |
| MySQL | `IFNULL(x, y)` | `IFNULL(notes, '없음')` |
| SQL Server | `ISNULL(x, y)` | `ISNULL(notes, '없음')` |
| Oracle | `NVL(x, y)` | `NVL(notes, '없음')` |

> **권장:** `COALESCE`는 SQL 표준이며 모든 DB에서 동작합니다. 이식성이 중요하면 `COALESCE`를 사용하세요.

---

## 데이터 타입 대응표

| 용도 | SQLite | MySQL | PostgreSQL | SQL Server | Oracle |
|------|--------|-------|------------|------------|--------|
| 정수 | INTEGER | INT | INTEGER | INT | NUMBER(10) |
| 실수 | REAL | DECIMAL(12,2) | NUMERIC(12,2) | DECIMAL(12,2) | NUMBER(12,2) |
| 짧은 문자열 | TEXT | VARCHAR(200) | VARCHAR(200) | NVARCHAR(200) | VARCHAR2(200) |
| 긴 텍스트 | TEXT | TEXT | TEXT | NVARCHAR(MAX) | CLOB |
| 날짜/시간 | TEXT (ISO 8601) | DATETIME | TIMESTAMP | DATETIME2 | DATE / TIMESTAMP |
| 불리언 | INTEGER (0/1) | TINYINT(1) | BOOLEAN | BIT | NUMBER(1) |

---

## 식별자 인용 (Quoting)

예약어나 공백이 포함된 식별자를 감쌀 때:

| DB | 문법 | 예시 |
|----|------|------|
| SQLite / MySQL | 백틱 또는 큰따옴표 | `` `order` `` 또는 `"order"` |
| PostgreSQL | 큰따옴표 | `"order"` |
| SQL Server | 대괄호 또는 큰따옴표 | `[order]` 또는 `"order"` |
| Oracle | 큰따옴표 | `"ORDER"` (대소문자 구분 주의) |

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

## 윈도우 함수 지원

| 기능 | SQLite | MySQL | PostgreSQL | SQL Server | Oracle |
|------|--------|-------|------------|------------|--------|
| ROW_NUMBER | 3.25+ | 8.0+ | 8.4+ | 2005+ | 8i+ |
| RANK / DENSE_RANK | 3.25+ | 8.0+ | 8.4+ | 2005+ | 8i+ |
| LAG / LEAD | 3.25+ | 8.0+ | 8.4+ | 2012+ | 8i+ |
| NTILE | 3.25+ | 8.0+ | 8.4+ | 2005+ | 8i+ |
| SUM/AVG OVER | 3.25+ | 8.0+ | 8.4+ | 2005+ | 8i+ |

> 이 튜토리얼의 모든 윈도우 함수 쿼리는 위 최소 버전 이상에서 동작합니다.

---

## CTE와 재귀 CTE

| 기능 | SQLite | MySQL | PostgreSQL | SQL Server | Oracle |
|------|--------|-------|------------|------------|--------|
| WITH (CTE) | 3.8.3+ | 8.0+ | 8.4+ | 2005+ | 11gR2+ |
| WITH RECURSIVE | 3.8.3+ | 8.0+ | 8.4+ | 2005+ | 11gR2+ |

**재귀 키워드 차이:**

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
    -- RECURSIVE 키워드 불필요
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

## JSON 쿼리

각 데이터베이스는 JSON 데이터를 다루는 고유한 함수를 제공합니다.

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
    -- 또는: specs->'$.cpu'
    ```

=== "PostgreSQL"

    ```sql
    SELECT name, specs->>'cpu' AS cpu
    FROM products
    WHERE specs IS NOT NULL;
    ```

---

## 실행 계획 (EXPLAIN)

쿼리 성능을 분석할 때 사용하는 실행 계획 확인 문법입니다.

=== "SQLite"

    ```sql
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 42;
    ```

=== "MySQL"

    ```sql
    EXPLAIN
    SELECT * FROM orders WHERE customer_id = 42;
    -- 또는: EXPLAIN ANALYZE (MySQL 8.0.18+)
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
    -- 또는: SET SHOWPLAN_TEXT ON;
    ```

---

## 저장 프로시저

반복적인 로직을 서버에 저장하여 호출하는 기능입니다. SQLite는 저장 프로시저를 지원하지 않습니다.

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

## 트리거 문법

데이터 변경 시 자동으로 실행되는 트리거의 문법 차이입니다. 자세한 내용은 [레슨 24](advanced/24-triggers.md)을 참고하세요.

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

## 튜토리얼 SQL 변환 체크리스트

이 튜토리얼의 쿼리를 다른 DB에서 실행할 때 확인할 항목:

| # | 확인 사항 | SQLite 원본 | 변환 대상 |
|--:|-----------|-------------|-----------|
| 1 | LIMIT/OFFSET | `LIMIT 10` | MSSQL/Oracle: `FETCH NEXT 10 ROWS ONLY` |
| 2 | 날짜 추출 | `SUBSTR(ordered_at, 1, 7)` | MySQL: `DATE_FORMAT(ordered_at, '%Y-%m')` |
| 3 | 경과 일수 | `JULIANDAY(a) - JULIANDAY(b)` | MySQL: `DATEDIFF(a, b)` |
| 4 | 날짜 연산 | `DATE('now', '+30 days')` | PG: `CURRENT_DATE + INTERVAL '30 days'` |
| 5 | IFNULL | `IFNULL(x, y)` | MSSQL: `ISNULL`, Oracle: `NVL`, 공통: `COALESCE` |
| 6 | 문자열 연결 | `a \|\| b` | MySQL/MSSQL: `CONCAT(a, b)` |
| 7 | 불리언 | `is_active = 1` | PG: `is_active = TRUE` |
| 8 | 타입 캐스팅 | `CAST(x AS INTEGER)` | PG: `x::INTEGER`, Oracle: `TO_NUMBER(x)` |
