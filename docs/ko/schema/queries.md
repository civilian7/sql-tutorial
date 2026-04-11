# 05. 스키마 조회 쿼리

데이터베이스의 구조(테이블, 뷰, 인덱스, 트리거 등)를 SQL로 조회하는 방법입니다. 스키마 문서를 보지 않아도, 이 쿼리들로 데이터베이스의 전체 구조를 파악할 수 있습니다.

DB마다 메타데이터를 조회하는 방식이 다릅니다. 같은 정보를 얻는 쿼리를 DB별 탭으로 비교해보세요.

---

## 테이블 목록 조회

데이터베이스에 어떤 테이블이 있는지 확인합니다. 새로운 데이터베이스를 처음 접할 때 가장 먼저 실행하는 쿼리입니다.

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

**결과 예시 (일부):**

| name |
|------|
| calendar |
| cart_items |
| carts |
| categories |
| complaints |
| ... (총 30개) |

DDL(CREATE TABLE 문)도 함께 보려면:

=== "SQLite"

    ```sql
    SELECT name, sql FROM sqlite_master
    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
    ORDER BY name;
    ```

    **결과 예시 (일부):**

    | name | sql |
    |------|-----|
    | customers | CREATE TABLE customers ( id INTEGER PRIMARY KEY AUTOINCREMENT, ... |
    | orders | CREATE TABLE orders ( id INTEGER PRIMARY KEY AUTOINCREMENT, ... |
    | products | CREATE TABLE products ( id INTEGER PRIMARY KEY AUTOINCREMENT, ... |

=== "MySQL"

    ```sql
    SHOW CREATE TABLE orders;
    ```

    **결과 예시:**

    | Table | Create Table |
    |-------|-------------|
    | orders | CREATE TABLE `orders` ( `id` INT NOT NULL AUTO_INCREMENT, ... |

=== "PostgreSQL"

    ```bash
    # 터미널에서
    pg_dump -U postgres -t orders --schema-only ecommerce
    ```

    DDL 전체가 터미널에 출력됩니다. SQL에서 조회하려면:

    ```sql
    SELECT pg_get_tabledef('orders'::regclass);
    ```

---

## 칼럼 정보 조회

특정 테이블의 칼럼 이름, 타입, NULL 허용 여부를 확인합니다.

=== "SQLite"

    ```sql
    PRAGMA table_info('orders');
    ```

=== "MySQL"

    ```sql
    DESCRIBE orders;
    ```

    또는 더 상세하게:

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

**결과 예시** (`orders` 테이블, SQLite 기준):

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

## 뷰 목록 조회

데이터베이스에 정의된 뷰를 확인합니다.

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
    -- 일반 뷰
    SELECT viewname FROM pg_views
    WHERE schemaname = 'public'
    ORDER BY viewname;

    -- Materialized View
    SELECT matviewname FROM pg_matviews
    WHERE schemaname = 'public'
    ORDER BY matviewname;
    ```

**결과 예시 (일부):**

| name |
|------|
| v_cart_abandonment |
| v_category_tree |
| v_coupon_effectiveness |
| v_customer_rfm |
| v_customer_summary |
| ... (총 18개) |

뷰의 SQL 정의를 보려면:

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

## 인덱스 목록 조회

테이블에 설정된 인덱스를 확인합니다. 쿼리 성능 분석(22강)에서 유용합니다.

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

**결과 예시 (일부):**

| name | tbl_name |
|------|----------|
| idx_calendar_year_month | calendar |
| idx_cart_items_cart_id | cart_items |
| idx_carts_customer_id | carts |
| idx_categories_parent | categories |
| idx_complaints_customer | complaints |
| ... (총 61개) |

특정 테이블의 인덱스만 보려면:

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

## 트리거 목록 조회

데이터베이스에 정의된 트리거를 확인합니다.

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

**결과 예시** (SQLite):

| name | tbl_name |
|------|----------|
| trg_customers_updated_at | customers |
| trg_orders_updated_at | orders |
| trg_product_price_history | products |
| trg_products_updated_at | products |
| trg_reviews_updated_at | reviews |

트리거의 SQL 정의를 보려면:

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

## 저장 프로시저/함수 목록 조회

=== "MySQL"

    ```sql
    SELECT ROUTINE_NAME, ROUTINE_TYPE
    FROM INFORMATION_SCHEMA.ROUTINES
    WHERE ROUTINE_SCHEMA = DATABASE()
    ORDER BY ROUTINE_TYPE, ROUTINE_NAME;
    ```

    **결과 예시:**

    | ROUTINE_NAME | ROUTINE_TYPE |
    |-------------|-------------|
    | sp_cancel_order | PROCEDURE |
    | sp_cleanup_abandoned_carts | PROCEDURE |
    | sp_place_order | PROCEDURE |
    | ... (총 14개) | |

=== "PostgreSQL"

    ```sql
    SELECT routine_name, routine_type
    FROM information_schema.routines
    WHERE routine_schema = 'public'
    ORDER BY routine_type, routine_name;
    ```

    **결과 예시:**

    | routine_name | routine_type |
    |-------------|-------------|
    | refresh_materialized_views | FUNCTION |
    | sp_cancel_order | FUNCTION |
    | sp_place_order | FUNCTION |
    | ... (총 15개) | |

SQLite는 저장 프로시저를 지원하지 않습니다.

---

## 외래 키 관계 조회

테이블 간 FK 관계를 확인합니다. ERD를 직접 파악할 때 유용합니다.

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

**결과 예시** (`orders` 테이블, SQLite 기준):

| id | seq | table | from | to |
|---:|----:|-------|------|----|
| 0 | 0 | staff | staff_id | id |
| 1 | 0 | customer_addresses | address_id | id |
| 2 | 0 | customers | customer_id | id |

---

## 테이블/칼럼 코멘트

테이블이나 칼럼에 설명(코멘트)을 달아두면, 나중에 다른 사람이 스키마를 파악할 때 큰 도움이 됩니다. DBeaver 같은 GUI 도구에서도 코멘트가 표시됩니다.

### 코멘트 작성

=== "MySQL"

    ```sql
    -- 테이블 코멘트
    ALTER TABLE orders COMMENT = '주문 테이블';

    -- 칼럼 코멘트 (칼럼 정의를 함께 써야 함)
    ALTER TABLE orders
    MODIFY COLUMN status ENUM('pending','paid','preparing','shipped',
        'delivered','confirmed','cancelled','return_requested','returned')
        NOT NULL COMMENT '주문 상태';
    ```

=== "PostgreSQL"

    ```sql
    -- 테이블 코멘트
    COMMENT ON TABLE orders IS '주문 테이블';

    -- 칼럼 코멘트
    COMMENT ON COLUMN orders.status IS '주문 상태';
    COMMENT ON COLUMN orders.total_amount IS '주문 총액 (원)';
    COMMENT ON COLUMN customers.grade IS '고객 등급: BRONZE/SILVER/GOLD/VIP';
    ```

SQLite는 코멘트 기능을 지원하지 않습니다. DDL의 `--` 주석으로 대체합니다.

### 코멘트 조회

=== "MySQL"

    ```sql
    -- 테이블 코멘트
    SELECT TABLE_NAME, TABLE_COMMENT
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_COMMENT != ''
    ORDER BY TABLE_NAME;

    -- 칼럼 코멘트
    SELECT TABLE_NAME, COLUMN_NAME, COLUMN_COMMENT
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND COLUMN_COMMENT != ''
    ORDER BY TABLE_NAME, ORDINAL_POSITION;
    ```

    **결과 예시:**

    | TABLE_NAME | COLUMN_NAME | COLUMN_COMMENT |
    |-----------|-------------|----------------|
    | orders | status | 주문 상태 |
    | orders | total_amount | 주문 총액 (원) |
    | customers | grade | 고객 등급: BRONZE/SILVER/GOLD/VIP |

=== "PostgreSQL"

    ```sql
    -- 테이블 코멘트
    SELECT c.relname AS table_name,
           d.description AS comment
    FROM pg_class c
    JOIN pg_description d ON c.oid = d.objoid AND d.objsubid = 0
    WHERE c.relkind = 'r'
    ORDER BY c.relname;

    -- 칼럼 코멘트
    SELECT c.relname AS table_name,
           a.attname AS column_name,
           d.description AS comment
    FROM pg_class c
    JOIN pg_attribute a ON c.oid = a.attrelid
    JOIN pg_description d ON c.oid = d.objoid AND a.attnum = d.objsubid
    WHERE c.relkind = 'r' AND a.attnum > 0
    ORDER BY c.relname, a.attnum;
    ```

!!! tip "실무에서의 코멘트"
    - 테이블과 칼럼에 코멘트를 다는 것은 좋은 습관입니다
    - 특히 `status`, `type`, `grade` 같은 코드성 칼럼에는 **허용 값 목록**을 코멘트로 남기면 유용합니다
    - 팀 작업 시 DDL에 코멘트를 포함하는 것을 규칙으로 정하는 경우가 많습니다

---

## 테이블별 행 수 조회

전체 테이블의 데이터 규모를 한번에 확인합니다.

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

    !!! info "TABLE_ROWS는 추정치"
        InnoDB의 `TABLE_ROWS`는 정확한 값이 아닌 추정치입니다. 정확한 값이 필요하면 `SELECT COUNT(*)`를 사용하세요.

=== "PostgreSQL"

    ```sql
    SELECT relname AS table_name,
           n_live_tup AS estimated_rows
    FROM pg_stat_user_tables
    ORDER BY n_live_tup DESC;
    ```

    정확한 값이 필요하면:

    ```sql
    SELECT COUNT(*) FROM orders;
    ```

**결과 예시** (small 기준, 주요 테이블):

| tbl | cnt |
|-----|----:|
| orders | 34,908 |
| payments | 34,908 |
| customers | 5,230 |
| reviews | 7,945 |
| products | 280 |
