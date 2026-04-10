# 강의 21: 뷰(Views)

**뷰(View)**는 데이터베이스에 이름이 붙은 객체로 저장된 쿼리입니다. 뷰를 조회하는 방식은 테이블 조회와 동일하지만, 내부적으로는 쿼리가 매번 실행됩니다. 뷰는 복잡한 쿼리를 단순화하고, 일관된 비즈니스 로직을 강제하며, 원시 테이블의 세부 내용을 숨겨 보안 계층을 제공합니다.

```mermaid
flowchart LR
    subgraph "Physical Tables"
        T1["customers"]
        T2["orders"]
        T3["order_items"]
    end
    subgraph "View (virtual)"
        V["v_customer_summary\n= stored query"]
    end
    T1 --> V
    T2 --> V
    T3 --> V
    V --> Q["SELECT * FROM\nv_customer_summary\nWHERE ..."]
```

> 뷰는 저장된 쿼리입니다. 물리적 테이블이 아니라 실행할 때마다 원본 테이블에서 데이터를 가져옵니다.

## 뷰 생성

```sql
CREATE VIEW view_name AS
SELECT ...;
```

생성 후에는 테이블처럼 조회할 수 있습니다:

```sql
SELECT * FROM view_name WHERE ...;
```

## 쇼핑몰 기본 제공 뷰

이 데이터베이스에는 18개의 뷰가 미리 제공됩니다. 다음 쿼리로 목록을 확인하세요:

=== "SQLite"
    ```sql
    -- 데이터베이스의 모든 뷰 목록
    SELECT name, sql
    FROM sqlite_master
    WHERE type = 'view'
    ORDER BY name;
    ```

=== "MySQL"
    ```sql
    -- 데이터베이스의 모든 뷰 목록
    SELECT TABLE_NAME, VIEW_DEFINITION
    FROM INFORMATION_SCHEMA.VIEWS
    WHERE TABLE_SCHEMA = DATABASE()
    ORDER BY TABLE_NAME;
    ```

=== "PostgreSQL"
    ```sql
    -- 데이터베이스의 모든 뷰 목록
    SELECT viewname, definition
    FROM pg_views
    WHERE schemaname = 'public'
    ORDER BY viewname;
    ```

주요 뷰 목록:

| 뷰 | 설명 |
|------|-------------|
| `v_order_summary` | 고객명과 결제수단이 포함된 주문 정보 |
| `v_product_sales` | 상품별 판매 수량, 매출, 리뷰 통계 |
| `v_customer_stats` | 고객별 주문 수, LTV, 평균 주문 금액 |
| `v_monthly_revenue` | 월별 매출 및 주문 수 |
| `v_category_performance` | 카테고리별 매출 및 판매 수량 |
| `v_top_customers` | LTV 기준 상위 100명 고객 |
| `v_inventory_status` | 재고 수준 분류를 포함한 상품 정보 |
## 뷰 조회하기

```sql
-- v_order_summary를 테이블처럼 사용
SELECT customer_name, order_number, total_amount, payment_method
FROM v_order_summary
WHERE order_status = 'confirmed'
  AND ordered_at LIKE '2024-12%'
ORDER BY total_amount DESC
LIMIT 5;
```

**결과:**

| customer_name | order_number | total_amount | payment_method |
|---------------|--------------|-------------:|----------------|
| 최수아 | ORD-20241231-09842 | 2349.00 | card |
| 박지훈 | ORD-20241228-09831 | 1899.00 | card |
| 이지은 | ORD-20241226-09820 | 1299.99 | kakao_pay |
| ... | | | |

```sql
-- 기본 제공 뷰로 월별 매출 추이 확인
SELECT year_month, revenue, order_count
FROM v_monthly_revenue
WHERE year_month BETWEEN '2022-01' AND '2024-12'
ORDER BY year_month;
```

```sql
-- 뷰로 재고 현황 확인
SELECT product_name, price, stock_qty, stock_status
FROM v_inventory_status
WHERE stock_status IN ('품절', '재고 부족')
ORDER BY stock_qty ASC;
```

## 뷰 정의 확인하기

시스템 카탈로그를 사용하면 뷰의 SQL 정의를 살펴볼 수 있습니다:

=== "SQLite"
    ```sql
    -- v_product_sales 뷰를 정의하는 SQL 확인
    SELECT sql
    FROM sqlite_master
    WHERE type = 'view'
      AND name = 'v_product_sales';
    ```

=== "MySQL"
    ```sql
    -- v_product_sales 뷰를 정의하는 SQL 확인
    SELECT VIEW_DEFINITION
    FROM INFORMATION_SCHEMA.VIEWS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'v_product_sales';
    ```

=== "PostgreSQL"
    ```sql
    -- v_product_sales 뷰를 정의하는 SQL 확인
    SELECT definition
    FROM pg_views
    WHERE schemaname = 'public'
      AND viewname = 'v_product_sales';
    ```

**결과 (요약):**

```sql
CREATE VIEW v_product_sales AS
SELECT
    p.id            AS product_id,
    p.name          AS product_name,
    cat.name        AS category,
    p.price,
    COALESCE(SUM(oi.quantity), 0)             AS units_sold,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
    COUNT(DISTINCT r.id)                      AS review_count,
    ROUND(AVG(r.rating), 2)                   AS avg_rating
FROM products AS p
INNER JOIN categories AS cat ON p.category_id = cat.id
LEFT  JOIN order_items AS oi ON oi.product_id = p.id
LEFT  JOIN reviews     AS r  ON r.product_id  = p.id
GROUP BY p.id, p.name, cat.name, p.price
```

## 뷰 위에 뷰 만들기

```sql
-- 뷰를 일반 테이블처럼 필터링할 수 있음
SELECT *
FROM v_customer_stats
WHERE order_count >= 10
  AND avg_order_value > 500
ORDER BY lifetime_value DESC
LIMIT 10;
```

## 직접 뷰 만들기

```sql
-- 고객 서비스 대시보드용 뷰
CREATE VIEW v_cs_watchlist AS
SELECT
    c.id            AS customer_id,
    c.name,
    c.email,
    c.grade,
    COUNT(DISTINCT comp.id)  AS open_complaints,
    COUNT(DISTINCT r.id)     AS pending_returns,
    MAX(o.ordered_at)        AS last_order_date
FROM customers AS c
LEFT JOIN complaints AS comp ON comp.customer_id = c.id
    AND comp.status = 'open'
LEFT JOIN orders AS o ON o.customer_id = c.id
LEFT JOIN returns AS r ON r.order_id = o.id
    AND r.status = 'pending'
GROUP BY c.id, c.name, c.email, c.grade
HAVING open_complaints > 0 OR pending_returns > 0;
```

## 뷰 삭제

```sql
DROP VIEW IF EXISTS v_cs_watchlist;
```

## 구체화된 뷰 (Materialized View)

지금까지 배운 일반 뷰는 조회할 때마다 내부 쿼리가 실행됩니다. **구체화된 뷰(Materialized View)**는 쿼리 결과를 물리적으로 저장하여, 복잡한 집계 쿼리의 조회 속도를 크게 향상시킵니다.

### 일반 뷰 vs 구체화된 뷰

| 항목 | View | Materialized View |
|------|------|-------------------|
| 데이터 저장 | 아니오 (쿼리만 저장) | 예 (결과 저장) |
| 조회 속도 | 매번 쿼리 실행 | 미리 계산된 결과 |
| 데이터 신선도 | 항상 최신 | REFRESH 필요 |
| 디스크 사용 | 없음 | 결과 크기만큼 |
| 인덱스 생성 | 불가 | 가능 (PostgreSQL) |

**장점:** 복잡한 집계 쿼리를 미리 계산해 두므로 조회가 빠릅니다.

**단점:** 원본 데이터가 변경되어도 자동으로 반영되지 않습니다. 수동으로 갱신(REFRESH)해야 합니다.

### DB별 지원

구체화된 뷰의 지원 수준은 데이터베이스마다 크게 다릅니다.

=== "SQLite"
    SQLite는 구체화된 뷰를 지원하지 않습니다. 대안으로 `CREATE TABLE ... AS SELECT`(CTAS)로 테이블을 생성한 뒤, 갱신이 필요할 때 DROP + 재생성하는 방법을 사용합니다.

    ```sql
    -- 월별 매출 요약 테이블 생성 (구체화된 뷰 대안)
    CREATE TABLE mv_monthly_summary AS
    SELECT
        STRFTIME('%Y-%m', o.ordered_at) AS year_month,
        COUNT(DISTINCT o.id)            AS order_count,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders AS o
    INNER JOIN order_items AS oi ON oi.order_id = o.id
    GROUP BY STRFTIME('%Y-%m', o.ordered_at);

    -- 데이터 갱신이 필요할 때: DROP 후 재생성
    DROP TABLE IF EXISTS mv_monthly_summary;
    CREATE TABLE mv_monthly_summary AS
    SELECT
        STRFTIME('%Y-%m', o.ordered_at) AS year_month,
        COUNT(DISTINCT o.id)            AS order_count,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders AS o
    INNER JOIN order_items AS oi ON oi.order_id = o.id
    GROUP BY STRFTIME('%Y-%m', o.ordered_at);
    ```

=== "MySQL"
    MySQL도 구체화된 뷰를 직접 지원하지 않습니다. CTAS로 테이블을 생성하고, 이벤트 스케줄러로 주기적으로 갱신하는 방법을 사용합니다.

    ```sql
    -- 월별 매출 요약 테이블 생성 (구체화된 뷰 대안)
    CREATE TABLE mv_monthly_summary AS
    SELECT
        DATE_FORMAT(o.ordered_at, '%Y-%m') AS year_month,
        COUNT(DISTINCT o.id)               AS order_count,
        SUM(oi.quantity * oi.unit_price)    AS revenue
    FROM orders AS o
    INNER JOIN order_items AS oi ON oi.order_id = o.id
    GROUP BY DATE_FORMAT(o.ordered_at, '%Y-%m');

    -- 이벤트 스케줄러로 매일 새벽 갱신
    CREATE EVENT refresh_monthly_summary
    ON SCHEDULE EVERY 1 DAY
    STARTS CURRENT_DATE + INTERVAL 3 HOUR
    DO
    BEGIN
        TRUNCATE TABLE mv_monthly_summary;
        INSERT INTO mv_monthly_summary
        SELECT
            DATE_FORMAT(o.ordered_at, '%Y-%m') AS year_month,
            COUNT(DISTINCT o.id)               AS order_count,
            SUM(oi.quantity * oi.unit_price)    AS revenue
        FROM orders AS o
        INNER JOIN order_items AS oi ON oi.order_id = o.id
        GROUP BY DATE_FORMAT(o.ordered_at, '%Y-%m');
    END;
    ```

=== "PostgreSQL"
    PostgreSQL은 구체화된 뷰를 네이티브로 지원합니다.

    ```sql
    -- 월별 매출 요약 구체화된 뷰 생성
    CREATE MATERIALIZED VIEW mv_monthly_summary AS
    SELECT
        TO_CHAR(o.ordered_at, 'YYYY-MM')  AS year_month,
        COUNT(DISTINCT o.id)              AS order_count,
        SUM(oi.quantity * oi.unit_price)   AS revenue
    FROM orders AS o
    INNER JOIN order_items AS oi ON oi.order_id = o.id
    GROUP BY TO_CHAR(o.ordered_at, 'YYYY-MM');

    -- 구체화된 뷰에 인덱스 생성 가능
    CREATE INDEX idx_mv_monthly_year_month
    ON mv_monthly_summary (year_month);

    -- 데이터 갱신
    REFRESH MATERIALIZED VIEW mv_monthly_summary;

    -- 무중단 갱신 (UNIQUE 인덱스 필요)
    CREATE UNIQUE INDEX idx_mv_monthly_unique
    ON mv_monthly_summary (year_month);
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_summary;

    -- 삭제
    DROP MATERIALIZED VIEW IF EXISTS mv_monthly_summary;
    ```

    > `CONCURRENTLY` 옵션은 갱신 중에도 기존 데이터를 조회할 수 있게 해줍니다. 단, UNIQUE 인덱스가 필요합니다.

!!! note "레슨 복습 문제"
    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. 여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/index.md) 섹션을 참고하세요.

## 연습 문제
### 연습 1
`v_customer_stats` 뷰를 조회하여 주문 건수가 5건 이상이고 평균 주문 금액이 300 이상인 고객을 `lifetime_value` 내림차순으로 조회하세요.

??? success "정답"
    ```sql
    SELECT *
    FROM v_customer_stats
    WHERE order_count >= 5
      AND avg_order_value >= 300
    ORDER BY lifetime_value DESC;
    ```


### 연습 2
`v_cs_watchlist` 뷰를 삭제한 뒤, 존재하지 않는 뷰를 삭제할 때 에러가 발생하지 않도록 작성하세요.

??? success "정답"
    ```sql
    DROP VIEW IF EXISTS v_cs_watchlist;
    ```


### 연습 3
`v_product_sales`를 조회하여 `total_revenue` 기준 상위 10개 상품을 찾으세요. `product_name`, `category`, `units_sold`, `total_revenue`, `avg_rating`을 반환하고, 리뷰가 5개 이상인 상품만 포함하세요.

??? success "정답"
    ```sql
    SELECT
        product_name,
        category,
        units_sold,
        total_revenue,
        avg_rating
    FROM v_product_sales
    WHERE review_count >= 5
    ORDER BY total_revenue DESC
    LIMIT 10;
    ```


### 연습 4
시스템 카탈로그를 사용하여 18개의 뷰 전체를 알파벳 순으로 나열하세요. 각 뷰의 이름만 표시합니다. 이후 관심 있는 뷰를 하나 골라 정의를 살펴보세요.

??? success "정답"
    === "SQLite"
        ```sql
        -- 1단계: 모든 뷰 목록 조회
        SELECT name
        FROM sqlite_master
        WHERE type = 'view'
        ORDER BY name;

        -- 2단계: 특정 뷰 정의 확인 (예: v_monthly_revenue)
        SELECT sql
        FROM sqlite_master
        WHERE type = 'view'
          AND name = 'v_monthly_revenue';
        ```

    === "MySQL"
        ```sql
        -- 1단계: 모든 뷰 목록 조회
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME;

        -- 2단계: 특정 뷰 정의 확인 (예: v_monthly_revenue)
        SELECT VIEW_DEFINITION
        FROM INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'v_monthly_revenue';
        ```

    === "PostgreSQL"
        ```sql
        -- 1단계: 모든 뷰 목록 조회
        SELECT viewname
        FROM pg_views
        WHERE schemaname = 'public'
        ORDER BY viewname;

        -- 2단계: 특정 뷰 정의 확인 (예: v_monthly_revenue)
        SELECT definition
        FROM pg_views
        WHERE schemaname = 'public'
          AND viewname = 'v_monthly_revenue';
        ```


### 연습 5
`v_supplier_performance` 뷰를 조회하여 반품률이 가장 높은 공급업체를 찾으세요. 이어서, 이 뷰의 정의를 시스템 카탈로그로 확인하세요.

??? success "정답"
    === "SQLite"
        ```sql
        -- 1단계: 반품률이 가장 높은 공급업체
        SELECT *
        FROM v_supplier_performance
        ORDER BY return_rate_pct DESC
        LIMIT 1;

        -- 2단계: 뷰 정의 확인
        SELECT sql
        FROM sqlite_master
        WHERE type = 'view'
          AND name = 'v_supplier_performance';
        ```

    === "MySQL"
        ```sql
        SELECT *
        FROM v_supplier_performance
        ORDER BY return_rate_pct DESC
        LIMIT 1;

        SELECT VIEW_DEFINITION
        FROM INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'v_supplier_performance';
        ```

    === "PostgreSQL"
        ```sql
        SELECT *
        FROM v_supplier_performance
        ORDER BY return_rate_pct DESC
        LIMIT 1;

        SELECT definition
        FROM pg_views
        WHERE schemaname = 'public'
          AND viewname = 'v_supplier_performance';
        ```


### 연습 6
연습 5~7에서 만든 뷰들을 모두 삭제하세요.

??? success "정답"
    ```sql
    DROP VIEW IF EXISTS v_product_total_sales;
    DROP VIEW IF EXISTS v_category_monthly_revenue;
    ```


### 연습 7
`products` 테이블과 `order_items` 테이블을 JOIN하여 상품별 총 판매 수량(`total_qty`)과 총 매출(`total_sales`)을 계산하는 `v_product_total_sales` 뷰를 생성하세요. `product_id`, `product_name`, `total_qty`, `total_sales` 칼럼을 포함합니다.

??? success "정답"
    ```sql
    CREATE VIEW v_product_total_sales AS
    SELECT
        p.id          AS product_id,
        p.name        AS product_name,
        COALESCE(SUM(oi.quantity), 0)              AS total_qty,
        COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_sales
    FROM products AS p
    LEFT JOIN order_items AS oi ON oi.product_id = p.id
    GROUP BY p.id, p.name;
    ```


### 연습 8
기존 뷰 `v_product_total_sales`를 수정하여 `category_name` 칼럼을 추가하세요 (categories 테이블 JOIN). SQLite는 `CREATE OR REPLACE`를 지원하지 않으므로 DB별 방법이 다릅니다.

??? success "정답"
    === "SQLite"
        ```sql
        -- SQLite: DROP 후 재생성
        DROP VIEW IF EXISTS v_product_total_sales;

        CREATE VIEW v_product_total_sales AS
        SELECT
            p.id          AS product_id,
            p.name        AS product_name,
            c.name        AS category_name,
            COALESCE(SUM(oi.quantity), 0)              AS total_qty,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_sales
        FROM products AS p
        INNER JOIN categories AS c ON c.id = p.category_id
        LEFT JOIN order_items AS oi ON oi.product_id = p.id
        GROUP BY p.id, p.name, c.name;
        ```

    === "MySQL"
        ```sql
        -- MySQL: CREATE OR REPLACE 지원
        CREATE OR REPLACE VIEW v_product_total_sales AS
        SELECT
            p.id          AS product_id,
            p.name        AS product_name,
            c.name        AS category_name,
            COALESCE(SUM(oi.quantity), 0)              AS total_qty,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_sales
        FROM products AS p
        INNER JOIN categories AS c ON c.id = p.category_id
        LEFT JOIN order_items AS oi ON oi.product_id = p.id
        GROUP BY p.id, p.name, c.name;
        ```

    === "PostgreSQL"
        ```sql
        -- PostgreSQL: CREATE OR REPLACE 지원
        CREATE OR REPLACE VIEW v_product_total_sales AS
        SELECT
            p.id          AS product_id,
            p.name        AS product_name,
            c.name        AS category_name,
            COALESCE(SUM(oi.quantity), 0)              AS total_qty,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_sales
        FROM products AS p
        INNER JOIN categories AS c ON c.id = p.category_id
        LEFT JOIN order_items AS oi ON oi.product_id = p.id
        GROUP BY p.id, p.name, c.name;
        ```


### 연습 9
카테고리별 월간 매출 집계 뷰 `v_category_monthly_revenue`를 만드세요. `category_name`, `year_month` (주문일 기준, 'YYYY-MM' 형식), `revenue`, `order_count` 칼럼을 포함합니다.

??? success "정답"
    === "SQLite"
        ```sql
        CREATE VIEW v_category_monthly_revenue AS
        SELECT
            c.name                                  AS category_name,
            STRFTIME('%Y-%m', o.ordered_at)         AS year_month,
            SUM(oi.quantity * oi.unit_price)         AS revenue,
            COUNT(DISTINCT o.id)                     AS order_count
        FROM categories AS c
        INNER JOIN products    AS p  ON p.category_id = c.id
        INNER JOIN order_items AS oi ON oi.product_id = p.id
        INNER JOIN orders      AS o  ON o.id = oi.order_id
        GROUP BY c.name, STRFTIME('%Y-%m', o.ordered_at);
        ```

    === "MySQL"
        ```sql
        CREATE VIEW v_category_monthly_revenue AS
        SELECT
            c.name                                  AS category_name,
            DATE_FORMAT(o.ordered_at, '%Y-%m')      AS year_month,
            SUM(oi.quantity * oi.unit_price)         AS revenue,
            COUNT(DISTINCT o.id)                     AS order_count
        FROM categories AS c
        INNER JOIN products    AS p  ON p.category_id = c.id
        INNER JOIN order_items AS oi ON oi.product_id = p.id
        INNER JOIN orders      AS o  ON o.id = oi.order_id
        GROUP BY c.name, DATE_FORMAT(o.ordered_at, '%Y-%m');
        ```

    === "PostgreSQL"
        ```sql
        CREATE VIEW v_category_monthly_revenue AS
        SELECT
            c.name                                  AS category_name,
            TO_CHAR(o.ordered_at, 'YYYY-MM')        AS year_month,
            SUM(oi.quantity * oi.unit_price)         AS revenue,
            COUNT(DISTINCT o.id)                     AS order_count
        FROM categories AS c
        INNER JOIN products    AS p  ON p.category_id = c.id
        INNER JOIN order_items AS oi ON oi.product_id = p.id
        INNER JOIN orders      AS o  ON o.id = oi.order_id
        GROUP BY c.name, TO_CHAR(o.ordered_at, 'YYYY-MM');
        ```


### 연습 10
카테고리별 총 매출과 판매 수량을 집계하는 구체화된 뷰 `mv_category_sales`를 생성하세요. `category_name`, `total_revenue`, `total_qty` 칼럼을 포함합니다. DB별로 적절한 방법을 사용하세요.

??? success "정답"
    === "SQLite"
        ```sql
        -- SQLite: CTAS로 테이블 생성 (구체화된 뷰 대안)
        CREATE TABLE mv_category_sales AS
        SELECT
            c.name                                  AS category_name,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
            COALESCE(SUM(oi.quantity), 0)            AS total_qty
        FROM categories AS c
        LEFT JOIN products    AS p  ON p.category_id = c.id
        LEFT JOIN order_items AS oi ON oi.product_id = p.id
        GROUP BY c.name;

        -- 갱신 시: DROP 후 재생성
        DROP TABLE IF EXISTS mv_category_sales;
        CREATE TABLE mv_category_sales AS
        SELECT
            c.name                                  AS category_name,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
            COALESCE(SUM(oi.quantity), 0)            AS total_qty
        FROM categories AS c
        LEFT JOIN products    AS p  ON p.category_id = c.id
        LEFT JOIN order_items AS oi ON oi.product_id = p.id
        GROUP BY c.name;
        ```

    === "MySQL"
        ```sql
        -- MySQL: CTAS로 테이블 생성 (구체화된 뷰 대안)
        CREATE TABLE mv_category_sales AS
        SELECT
            c.name                                  AS category_name,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
            COALESCE(SUM(oi.quantity), 0)            AS total_qty
        FROM categories AS c
        LEFT JOIN products    AS p  ON p.category_id = c.id
        LEFT JOIN order_items AS oi ON oi.product_id = p.id
        GROUP BY c.name;

        -- 갱신 시: TRUNCATE + INSERT
        TRUNCATE TABLE mv_category_sales;
        INSERT INTO mv_category_sales
        SELECT
            c.name                                  AS category_name,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
            COALESCE(SUM(oi.quantity), 0)            AS total_qty
        FROM categories AS c
        LEFT JOIN products    AS p  ON p.category_id = c.id
        LEFT JOIN order_items AS oi ON oi.product_id = p.id
        GROUP BY c.name;
        ```

    === "PostgreSQL"
        ```sql
        -- PostgreSQL: 네이티브 구체화된 뷰
        CREATE MATERIALIZED VIEW mv_category_sales AS
        SELECT
            c.name                                  AS category_name,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
            COALESCE(SUM(oi.quantity), 0)            AS total_qty
        FROM categories AS c
        LEFT JOIN products    AS p  ON p.category_id = c.id
        LEFT JOIN order_items AS oi ON oi.product_id = p.id
        GROUP BY c.name;

        -- 갱신
        REFRESH MATERIALIZED VIEW mv_category_sales;
        ```


---
다음: [강의 22: 인덱스와 쿼리 실행 계획](22-indexes.md)
