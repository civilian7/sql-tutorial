# 02. 뷰

## 뷰(View)란?

뷰는 **자주 사용하는 SELECT 쿼리를 이름을 붙여 저장**한 것입니다. 테이블처럼 `SELECT * FROM v_monthly_sales`로 조회할 수 있지만, 데이터를 직접 저장하지는 않습니다. 뷰를 조회할 때마다 내부의 SQL이 실행됩니다.

**뷰를 사용하는 이유:**

- **편의성** — 5개 테이블을 JOIN하는 복잡한 쿼리를 매번 작성하지 않아도 됩니다
- **일관성** — "월별 매출"의 계산 방식이 뷰에 한 번만 정의되므로, 누가 조회해도 같은 결과
- **보안** — 원본 테이블 대신 뷰만 접근 권한을 부여하면, 민감한 칼럼(이메일, 전화번호 등)을 노출하지 않을 수 있습니다
- **추상화** — 테이블 구조가 변경되어도 뷰의 인터페이스를 유지하면 기존 쿼리가 깨지지 않습니다

뷰에 대한 상세 학습은 [21. 뷰(Views)](../advanced/21-views.md) 레슨에서 다룹니다.

## 뷰 목록

18개의 사전 정의 뷰로 복잡한 분석 쿼리를 즉시 실행할 수 있습니다.

| 뷰 | 설명 | SQL 패턴 |
|-----|------|----------|
| v_monthly_sales | 월별 매출 요약 | GROUP BY + 날짜 함수 |
| v_daily_orders | 일별 주문 현황 | GROUP BY + CASE 피벗 |
| v_hourly_pattern | 시간대별 주문 패턴 | 시간 추출 + CASE 분류 |
| v_revenue_growth | 월별 매출 성장률 | LAG 윈도우 함수 |
| v_yearly_kpi | 연도별 핵심 KPI | 다중 서브쿼리 LEFT JOIN |
| v_customer_rfm | 고객 RFM 분석 | NTILE 윈도우 + CTE + CASE |
| v_customer_summary | 고객 종합 프로필 | 다중 LEFT JOIN + COALESCE |
| v_order_detail | 주문 상세 조인 | 5테이블 비정규화 JOIN |
| v_product_performance | 상품 성과 지표 | 다중 LEFT JOIN + 마진 계산 |
| v_product_abc | 상품 ABC 분석 | 누적 SUM OVER + CASE 분류 |
| v_top_products_by_category | 카테고리별 Top 상품 | ROW_NUMBER PARTITION BY |
| v_category_tree | 카테고리 트리 | 재귀 CTE + 경로 문자열 |
| v_payment_summary | 결제 수단 요약 | 비율 계산 (스칼라 서브쿼리) |
| v_supplier_performance | 공급업체 성과 | 다중 LEFT JOIN + 반품률 |
| v_staff_workload | CS 직원 업무량 | LEFT JOIN + 평균 처리시간 |
| v_coupon_effectiveness | 쿠폰 효과 분석 | ROI 계산 (매출/할인) |
| v_return_analysis | 반품 분석 | GROUP BY + CASE 피벗 + 평균 |
| v_cart_abandonment | 장바구니 이탈 분석 | JOIN + GROUP_CONCAT/STRING_AGG |

**패턴별 요약**

| 그룹 | 뷰 | 핵심 패턴 |
|------|-----|----------|
| 매출/시계열 | v_monthly_sales, v_daily_orders, v_hourly_pattern, v_revenue_growth, v_yearly_kpi | GROUP BY, LAG, 다중 서브쿼리 |
| 고객 분석 | v_customer_rfm, v_customer_summary | NTILE, CTE, 다중 LEFT JOIN |
| 주문/상품 | v_order_detail, v_product_performance, v_product_abc, v_top_products_by_category | 비정규화 JOIN, SUM OVER, ROW_NUMBER |
| 계층/참조 | v_category_tree, v_payment_summary | 재귀 CTE, 스칼라 서브쿼리 |
| 운영/분석 | v_supplier_performance, v_staff_workload, v_coupon_effectiveness, v_return_analysis, v_cart_abandonment | 반품률, ROI, GROUP_CONCAT |

!!! info "DB별 뷰 지원"
    18개 뷰는 SQLite, MySQL, PostgreSQL 모두에서 동일하게 제공됩니다.

    PostgreSQL에서는 `v_monthly_sales`와 `v_product_performance`가 **Materialized View**(`mv_` 접두어)로도 제공됩니다.
    Materialized View는 쿼리 결과를 물리적으로 저장하여 매번 재계산하지 않으므로, 대용량 집계 뷰에서 성능이 크게 향상됩니다.

    | DB | Materialized View | 비고 |
    |----|:-:|------|
    | PostgreSQL | `CREATE MATERIALIZED VIEW` + `REFRESH` | 네이티브 지원 |
    | MySQL | 미지원 | 테이블 + 이벤트 스케줄러로 수동 구현 가능 |
    | SQLite | 미지원 | 트리거 + 별도 테이블로 수동 구현 가능 |


### v_cart_abandonment — 장바구니 이탈 분석

미전환 장바구니의 고객 정보, 상품 수, 잠재 매출을 분석합니다.

```mermaid
flowchart LR
    A["carts
    status='abandoned'"] --> D["JOIN"]
    B["customers"] --> D
    C["cart_items + products"] --> D
    D --> E["GROUP BY cart
    COUNT, SUM, GROUP_CONCAT"]
    E --> F["결과: 고객, 상품수,
    잠재매출, 상품목록"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_cart_abandonment AS
    SELECT
        c.id AS cart_id,
        cust.name AS customer_name,
        cust.email,
        c.status,
        c.created_at,
        COUNT(ci.id) AS item_count,
        CAST(SUM(p.price * ci.quantity) AS INTEGER) AS potential_revenue,
        GROUP_CONCAT(p.name, ', ') AS products
    FROM carts c
    JOIN customers cust ON c.customer_id = cust.id
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.status = 'abandoned'
    GROUP BY c.id
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_cart_abandonment AS
    SELECT
        c.id AS cart_id,
        cust.name AS customer_name,
        cust.email,
        c.status,
        c.created_at,
        COUNT(ci.id) AS item_count,
        CAST(SUM(p.price * ci.quantity) AS SIGNED) AS potential_revenue,
        GROUP_CONCAT(p.name SEPARATOR ', ') AS products
    FROM carts c
    JOIN customers cust ON c.customer_id = cust.id
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.status = 'abandoned'
    GROUP BY c.id, cust.name, cust.email, c.status, c.created_at;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_cart_abandonment AS
    SELECT
        c.id AS cart_id,
        cust.name AS customer_name,
        cust.email,
        c.status,
        c.created_at,
        COUNT(ci.id) AS item_count,
        SUM(p.price * ci.quantity)::BIGINT AS potential_revenue,
        STRING_AGG(p.name, ', ') AS products
    FROM carts c
    JOIN customers cust ON c.customer_id = cust.id
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.status = 'abandoned'
    GROUP BY c.id, cust.name, cust.email, c.status, c.created_at;
    ```

### v_category_tree — 카테고리 트리

재귀 CTE로 계층 구조 경로(대분류 > 중분류 > 소분류)와 상품 수를 조회합니다.

```mermaid
flowchart LR
    A["categories
    parent_id IS NULL"] --> B["재귀 CTE
    자식 카테고리 탐색"]
    B --> C["full_path 구성
    대분류 > 중분류 > 소분류"]
    C --> D["LEFT JOIN products
    카테고리별 상품 수"]
    D --> E["sort_key 정렬"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_category_tree AS
    WITH RECURSIVE tree AS (
        SELECT id, name, parent_id, depth,
               name AS full_path,
               CAST(printf('%04d', sort_order) AS TEXT) AS sort_key
        FROM categories
        WHERE parent_id IS NULL
        UNION ALL
        SELECT c.id, c.name, c.parent_id, c.depth,
               tree.full_path || ' > ' || c.name,
               tree.sort_key || '.' || printf('%04d', c.sort_order)
        FROM categories c
        JOIN tree ON c.parent_id = tree.id
    )
    SELECT t.id, t.name, t.parent_id, t.depth, t.full_path,
           COALESCE(p.product_count, 0) AS product_count
    FROM tree t
    LEFT JOIN (
        SELECT category_id, COUNT(*) AS product_count
        FROM products
        GROUP BY category_id
    ) p ON t.id = p.category_id
    ORDER BY t.sort_key
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_category_tree AS
    WITH RECURSIVE tree AS (
        SELECT id, name, parent_id, depth,
               name AS full_path,
               LPAD(sort_order, 4, '0') AS sort_key
        FROM categories
        WHERE parent_id IS NULL
        UNION ALL
        SELECT c.id, c.name, c.parent_id, c.depth,
               CONCAT(tree.full_path, ' > ', c.name),
               CONCAT(tree.sort_key, '.', LPAD(c.sort_order, 4, '0'))
        FROM categories c
        JOIN tree ON c.parent_id = tree.id
    )
    SELECT t.id, t.name, t.parent_id, t.depth, t.full_path,
           COALESCE(p.product_count, 0) AS product_count
    FROM tree t
    LEFT JOIN (
        SELECT category_id, COUNT(*) AS product_count
        FROM products
        GROUP BY category_id
    ) p ON t.id = p.category_id
    ORDER BY t.sort_key;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_category_tree AS
    WITH RECURSIVE tree AS (
        SELECT id, name, parent_id, depth,
               name::TEXT AS full_path,
               LPAD(sort_order::TEXT, 4, '0') AS sort_key
        FROM categories
        WHERE parent_id IS NULL
        UNION ALL
        SELECT c.id, c.name, c.parent_id, c.depth,
               tree.full_path || ' > ' || c.name,
               tree.sort_key || '.' || LPAD(c.sort_order::TEXT, 4, '0')
        FROM categories c
        JOIN tree ON c.parent_id = tree.id
    )
    SELECT t.id, t.name, t.parent_id, t.depth, t.full_path,
           COALESCE(p.product_count, 0) AS product_count
    FROM tree t
    LEFT JOIN (
        SELECT category_id, COUNT(*) AS product_count
        FROM products
        GROUP BY category_id
    ) p ON t.id = p.category_id
    ORDER BY t.sort_key;
    ```

### v_coupon_effectiveness — 쿠폰 효과 분석

쿠폰별 사용 수, 총 할인액, ROI를 계산합니다.

```mermaid
flowchart LR
    A["coupons"] --> D["LEFT JOIN"]
    B["coupon_usage
    + orders"] --> D
    D --> E["집계: 사용수,
    총할인, 주문매출"]
    E --> F["ROI = 매출 / 할인액"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_coupon_effectiveness AS
    SELECT
        cp.id AS coupon_id,
        cp.code,
        cp.name,
        cp.type,
        cp.discount_value,
        cp.is_active,
        COALESCE(u.usage_count, 0) AS usage_count,
        cp.usage_limit,
        COALESCE(u.total_discount, 0) AS total_discount_given,
        COALESCE(u.total_order_revenue, 0) AS total_order_revenue,
        CASE
            WHEN COALESCE(u.total_discount, 0) > 0
            THEN ROUND(u.total_order_revenue / u.total_discount, 1)
            ELSE 0
        END AS roi_ratio
    FROM coupons cp
    LEFT JOIN (
        SELECT
            cu.coupon_id,
            COUNT(*) AS usage_count,
            CAST(SUM(cu.discount_amount) AS INTEGER) AS total_discount,
            CAST(SUM(o.total_amount) AS INTEGER) AS total_order_revenue
        FROM coupon_usage cu
        JOIN orders o ON cu.order_id = o.id
        GROUP BY cu.coupon_id
    ) u ON cp.id = u.coupon_id
    ORDER BY COALESCE(u.usage_count, 0) DESC
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_coupon_effectiveness AS
    SELECT
        cp.id AS coupon_id,
        cp.code,
        cp.name,
        cp.type,
        cp.discount_value,
        cp.is_active,
        COALESCE(u.usage_count, 0) AS usage_count,
        cp.usage_limit,
        COALESCE(u.total_discount, 0) AS total_discount_given,
        COALESCE(u.total_order_revenue, 0) AS total_order_revenue,
        CASE
            WHEN COALESCE(u.total_discount, 0) > 0
            THEN ROUND(u.total_order_revenue / u.total_discount, 1)
            ELSE 0
        END AS roi_ratio
    FROM coupons cp
    LEFT JOIN (
        SELECT
            cu.coupon_id,
            COUNT(*) AS usage_count,
            CAST(SUM(cu.discount_amount) AS SIGNED) AS total_discount,
            CAST(SUM(o.total_amount) AS SIGNED) AS total_order_revenue
        FROM coupon_usage cu
        JOIN orders o ON cu.order_id = o.id
        GROUP BY cu.coupon_id
    ) u ON cp.id = u.coupon_id
    ORDER BY COALESCE(u.usage_count, 0) DESC;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_coupon_effectiveness AS
    SELECT
        cp.id AS coupon_id,
        cp.code,
        cp.name,
        cp.type,
        cp.discount_value,
        cp.is_active,
        COALESCE(u.usage_count, 0) AS usage_count,
        cp.usage_limit,
        COALESCE(u.total_discount, 0) AS total_discount_given,
        COALESCE(u.total_order_revenue, 0) AS total_order_revenue,
        CASE
            WHEN COALESCE(u.total_discount, 0) > 0
            THEN ROUND(u.total_order_revenue / u.total_discount, 1)
            ELSE 0
        END AS roi_ratio
    FROM coupons cp
    LEFT JOIN (
        SELECT
            cu.coupon_id,
            COUNT(*) AS usage_count,
            SUM(cu.discount_amount)::BIGINT AS total_discount,
            SUM(o.total_amount)::BIGINT AS total_order_revenue
        FROM coupon_usage cu
        JOIN orders o ON cu.order_id = o.id
        GROUP BY cu.coupon_id
    ) u ON cp.id = u.coupon_id
    ORDER BY COALESCE(u.usage_count, 0) DESC;
    ```

### v_customer_rfm — 고객 RFM 분석

Recency/Frequency/Monetary 점수를 NTILE(5)로 산출하고, Champions/Loyal/At Risk 등 세그먼트를 분류합니다.

```mermaid
flowchart LR
    A["customers"] --> D["JOIN"]
    B["orders
    (취소 제외)"] --> D
    D --> E["집계: recency,
    frequency, monetary"]
    E --> F["NTILE(5)
    R·F·M 점수"]
    F --> G["CASE → 세그먼트
    Champions/Loyal/
    At Risk/Lost/..."]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_customer_rfm AS
    WITH rfm_raw AS (
        SELECT
            c.id AS customer_id,
            c.name,
            c.grade,
            CAST(julianday('2025-06-30') - julianday(MAX(o.ordered_at)) AS INTEGER) AS recency_days,
            COUNT(o.id) AS frequency,
            CAST(SUM(o.total_amount) AS INTEGER) AS monetary
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY c.id
    ),
    rfm_scored AS (
        SELECT *,
            NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,   -- more recent = higher score
            NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
            NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
        FROM rfm_raw
    )
    SELECT
        customer_id, name, grade,
        recency_days, frequency, monetary,
        r_score, f_score, m_score,
        r_score + f_score + m_score AS rfm_total,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Others'
        END AS segment
    FROM rfm_scored
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_customer_rfm AS
    WITH rfm_raw AS (
        SELECT
            c.id AS customer_id,
            c.name,
            c.grade,
            DATEDIFF('2025-06-30', MAX(o.ordered_at)) AS recency_days,
            COUNT(o.id) AS frequency,
            CAST(SUM(o.total_amount) AS SIGNED) AS monetary
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        WHERE o.status != 'cancelled'
        GROUP BY c.id, c.name, c.grade
    ),
    rfm_scored AS (
        SELECT *,
            NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
            NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
            NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
        FROM rfm_raw
    )
    SELECT
        customer_id, name, grade,
        recency_days, frequency, monetary,
        r_score, f_score, m_score,
        r_score + f_score + m_score AS rfm_total,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Others'
        END AS segment
    FROM rfm_scored;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_customer_rfm AS
    WITH rfm_raw AS (
        SELECT
            c.id AS customer_id,
            c.name,
            c.grade,
            ('2025-06-30'::DATE - MAX(ordered_at)::DATE) AS recency_days,
            COUNT(o.id) AS frequency,
            SUM(o.total_amount)::BIGINT AS monetary
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        WHERE o.status != 'cancelled'
        GROUP BY c.id, c.name, c.grade
    ),
    rfm_scored AS (
        SELECT *,
            NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
            NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
            NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
        FROM rfm_raw
    )
    SELECT
        customer_id, name, grade,
        recency_days, frequency, monetary,
        r_score, f_score, m_score,
        r_score + f_score + m_score AS rfm_total,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Others'
        END AS segment
    FROM rfm_scored;
    ```

### v_customer_summary — 고객 종합 프로필

고객별 주문 수, 총 구매액, 리뷰 수, 위시리스트, 활동 상태를 요약합니다.

```mermaid
flowchart LR
    A["customers"] --> E["LEFT JOIN"]
    B["orders 집계
    주문수, 총액"] --> E
    C["reviews 집계
    리뷰수, 평점"] --> E
    D["wishlists
    위시리스트 수"] --> E
    E --> F["나이 계산 +
    활동 상태 분류"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_customer_summary AS
    SELECT
        c.id,
        c.name,
        c.email,
        c.grade,
        c.gender,
        CASE
            WHEN c.birth_date IS NULL THEN NULL
            ELSE CAST((julianday('2025-06-30') - julianday(c.birth_date)) / 365.25 AS INTEGER)
        END AS age,
        c.created_at AS joined_at,
        COALESCE(os.order_count, 0) AS total_orders,
        COALESCE(os.total_spent, 0) AS total_spent,
        COALESCE(os.first_order, '') AS first_order_at,
        COALESCE(os.last_order, '') AS last_order_at,
        COALESCE(rv.review_count, 0) AS review_count,
        COALESCE(rv.avg_rating, 0) AS avg_rating_given,
        COALESCE(ws.wishlist_count, 0) AS wishlist_count,
        c.is_active,
        c.last_login_at,
        CASE
            WHEN c.is_active = 0 THEN 'inactive'
            WHEN c.last_login_at IS NULL THEN 'never_logged_in'
            WHEN c.last_login_at < DATE('2025-06-30', '-365 days') THEN 'dormant'
            ELSE 'active'
        END AS activity_status
    FROM customers c
    LEFT JOIN (
        SELECT customer_id,
               COUNT(*) AS order_count,
               CAST(SUM(total_amount) AS INTEGER) AS total_spent,
               MIN(ordered_at) AS first_order,
               MAX(ordered_at) AS last_order
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ) os ON c.id = os.customer_id
    LEFT JOIN (
        SELECT customer_id,
               COUNT(*) AS review_count,
               ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews
        GROUP BY customer_id
    ) rv ON c.id = rv.customer_id
    LEFT JOIN (
        SELECT customer_id, COUNT(*) AS wishlist_count
        FROM wishlists
        GROUP BY customer_id
    ) ws ON c.id = ws.customer_id
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_customer_summary AS
    SELECT
        c.id,
        c.name,
        c.email,
        c.grade,
        c.gender,
        CASE
            WHEN c.birth_date IS NULL THEN NULL
            ELSE TIMESTAMPDIFF(YEAR, c.birth_date, '2025-06-30')
        END AS age,
        c.created_at AS joined_at,
        COALESCE(os.order_count, 0) AS total_orders,
        COALESCE(os.total_spent, 0) AS total_spent,
        COALESCE(os.first_order, '') AS first_order_at,
        COALESCE(os.last_order, '') AS last_order_at,
        COALESCE(rv.review_count, 0) AS review_count,
        COALESCE(rv.avg_rating, 0) AS avg_rating_given,
        COALESCE(ws.wishlist_count, 0) AS wishlist_count,
        c.is_active,
        c.last_login_at,
        CASE
            WHEN c.is_active = 0 THEN 'inactive'
            WHEN c.last_login_at IS NULL THEN 'never_logged_in'
            WHEN c.last_login_at < DATE_SUB('2025-06-30', INTERVAL 365 DAY) THEN 'dormant'
            ELSE 'active'
        END AS activity_status
    FROM customers c
    LEFT JOIN (
        SELECT customer_id,
               COUNT(*) AS order_count,
               CAST(SUM(total_amount) AS SIGNED) AS total_spent,
               MIN(ordered_at) AS first_order,
               MAX(ordered_at) AS last_order
        FROM orders
        WHERE status != 'cancelled'
        GROUP BY customer_id
    ) os ON c.id = os.customer_id
    LEFT JOIN (
        SELECT customer_id,
               COUNT(*) AS review_count,
               ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews
        GROUP BY customer_id
    ) rv ON c.id = rv.customer_id
    LEFT JOIN (
        SELECT customer_id, COUNT(*) AS wishlist_count
        FROM wishlists
        GROUP BY customer_id
    ) ws ON c.id = ws.customer_id;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_customer_summary AS
    SELECT
        c.id,
        c.name,
        c.email,
        c.grade,
        c.gender,
        CASE
            WHEN c.birth_date IS NULL THEN NULL
            ELSE EXTRACT(YEAR FROM AGE('2025-06-30'::DATE, c.birth_date))::INT
        END AS age,
        c.created_at AS joined_at,
        COALESCE(os.order_count, 0) AS total_orders,
        COALESCE(os.total_spent, 0) AS total_spent,
        COALESCE(os.first_order, ''::TEXT) AS first_order_at,
        COALESCE(os.last_order, ''::TEXT) AS last_order_at,
        COALESCE(rv.review_count, 0) AS review_count,
        COALESCE(rv.avg_rating, 0) AS avg_rating_given,
        COALESCE(ws.wishlist_count, 0) AS wishlist_count,
        c.is_active,
        c.last_login_at,
        CASE
            WHEN c.is_active = FALSE THEN 'inactive'
            WHEN c.last_login_at IS NULL THEN 'never_logged_in'
            WHEN c.last_login_at < '2025-06-30'::DATE - INTERVAL '365 days' THEN 'dormant'
            ELSE 'active'
        END AS activity_status
    FROM customers c
    LEFT JOIN (
        SELECT customer_id,
               COUNT(*) AS order_count,
               SUM(total_amount)::BIGINT AS total_spent,
               MIN(ordered_at)::TEXT AS first_order,
               MAX(ordered_at)::TEXT AS last_order
        FROM orders
        WHERE status != 'cancelled'
        GROUP BY customer_id
    ) os ON c.id = os.customer_id
    LEFT JOIN (
        SELECT customer_id,
               COUNT(*) AS review_count,
               ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews
        GROUP BY customer_id
    ) rv ON c.id = rv.customer_id
    LEFT JOIN (
        SELECT customer_id, COUNT(*) AS wishlist_count
        FROM wishlists
        GROUP BY customer_id
    ) ws ON c.id = ws.customer_id;
    ```

### v_daily_orders — 일별 주문 현황

일별 주문 수, 매출, 확인/취소/반품 건수를 집계합니다.

```mermaid
flowchart LR
    A["orders"] --> B["GROUP BY
    DATE(ordered_at)"]
    B --> C["집계: 총주문,
    확인/취소/반품,
    매출, 평균"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_daily_orders AS
    SELECT
        DATE(ordered_at) AS order_date,
        CASE CAST(strftime('%w', ordered_at) AS INTEGER)
            WHEN 0 THEN '일' WHEN 1 THEN '월' WHEN 2 THEN '화'
            WHEN 3 THEN '수' WHEN 4 THEN '목' WHEN 5 THEN '금' WHEN 6 THEN '토'
        END AS day_of_week,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
        SUM(CASE WHEN status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returned,
        CAST(SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS INTEGER) AS revenue,
        CAST(AVG(CASE WHEN status != 'cancelled' THEN total_amount END) AS INTEGER) AS avg_order_amount
    FROM orders
    GROUP BY DATE(ordered_at)
    ORDER BY order_date
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_daily_orders AS
    SELECT
        DATE(ordered_at) AS order_date,
        DAYNAME(ordered_at) AS day_of_week,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
        SUM(CASE WHEN status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returned,
        CAST(SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS SIGNED) AS revenue,
        CAST(AVG(CASE WHEN status != 'cancelled' THEN total_amount END) AS SIGNED) AS avg_order_amount
    FROM orders
    GROUP BY DATE(ordered_at), DAYNAME(ordered_at)
    ORDER BY order_date;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_daily_orders AS
    SELECT
        ordered_at::DATE AS order_date,
        TO_CHAR(ordered_at, 'Day') AS day_of_week,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
        SUM(CASE WHEN status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returned,
        SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END)::BIGINT AS revenue,
        AVG(CASE WHEN status != 'cancelled' THEN total_amount END)::INT AS avg_order_amount
    FROM orders
    GROUP BY ordered_at::DATE, TO_CHAR(ordered_at, 'Day')
    ORDER BY order_date;
    ```

### v_hourly_pattern — 시간대별 주문 패턴

시간대별 주문 분포와 새벽/오전/오후/저녁 구간을 분류합니다.

```mermaid
flowchart LR
    A["orders
    (취소 제외)"] --> B["HOUR 추출"]
    B --> C["GROUP BY hour"]
    C --> D["집계: 주문수, 평균액"]
    D --> E["CASE → 시간대
    새벽/오전/오후/저녁"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_hourly_pattern AS
    SELECT
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        COUNT(*) AS order_count,
        CAST(AVG(total_amount) AS INTEGER) AS avg_amount,
        CASE
            WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 0 AND 5 THEN 'dawn'
            WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 6 AND 11 THEN 'morning'
            WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 12 AND 17 THEN 'afternoon'
            ELSE 'evening'
        END AS time_slot
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY hour
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_hourly_pattern AS
    SELECT
        HOUR(ordered_at) AS hour,
        COUNT(*) AS order_count,
        CAST(AVG(total_amount) AS SIGNED) AS avg_amount,
        CASE
            WHEN HOUR(ordered_at) BETWEEN 0 AND 5 THEN 'dawn'
            WHEN HOUR(ordered_at) BETWEEN 6 AND 11 THEN 'morning'
            WHEN HOUR(ordered_at) BETWEEN 12 AND 17 THEN 'afternoon'
            ELSE 'evening'
        END AS time_slot
    FROM orders
    WHERE status != 'cancelled'
    GROUP BY HOUR(ordered_at),
        CASE
            WHEN HOUR(ordered_at) BETWEEN 0 AND 5 THEN 'dawn'
            WHEN HOUR(ordered_at) BETWEEN 6 AND 11 THEN 'morning'
            WHEN HOUR(ordered_at) BETWEEN 12 AND 17 THEN 'afternoon'
            ELSE 'evening'
        END
    ORDER BY hour;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_hourly_pattern AS
    SELECT
        EXTRACT(HOUR FROM ordered_at)::INT AS hour,
        COUNT(*) AS order_count,
        AVG(total_amount)::INT AS avg_amount,
        CASE
            WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 0 AND 5 THEN 'dawn'
            WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 6 AND 11 THEN 'morning'
            WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 12 AND 17 THEN 'afternoon'
            ELSE 'evening'
        END AS time_slot
    FROM orders
    WHERE status != 'cancelled'
    GROUP BY EXTRACT(HOUR FROM ordered_at)::INT,
        CASE
            WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 0 AND 5 THEN 'dawn'
            WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 6 AND 11 THEN 'morning'
            WHEN EXTRACT(HOUR FROM ordered_at) BETWEEN 12 AND 17 THEN 'afternoon'
            ELSE 'evening'
        END
    ORDER BY hour;
    ```

### v_monthly_sales — 월별 매출 요약

월별 주문 수, 고객 수, 매출액, 할인액을 집계합니다.

```mermaid
flowchart LR
    A["orders
    (취소 제외)"] --> B["GROUP BY
    YYYY-MM"]
    B --> C["집계: 주문수,
    고객수, 매출,
    평균, 할인"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_monthly_sales AS
    SELECT
        SUBSTR(o.ordered_at, 1, 7) AS month,               -- YYYY-MM
        COUNT(DISTINCT o.id) AS order_count,                -- number of orders
        COUNT(DISTINCT o.customer_id) AS customer_count,    -- unique buyers
        CAST(SUM(o.total_amount) AS INTEGER) AS revenue,    -- total revenue
        CAST(AVG(o.total_amount) AS INTEGER) AS avg_order,  -- average order value
        SUM(o.discount_amount) AS total_discount            -- total discount
    FROM orders o
    WHERE o.status NOT IN ('cancelled')
    GROUP BY SUBSTR(o.ordered_at, 1, 7)
    ORDER BY month
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_monthly_sales AS
    SELECT
        DATE_FORMAT(o.ordered_at, '%Y-%m') AS month,
        COUNT(DISTINCT o.id) AS order_count,
        COUNT(DISTINCT o.customer_id) AS customer_count,
        CAST(SUM(o.total_amount) AS SIGNED) AS revenue,
        CAST(AVG(o.total_amount) AS SIGNED) AS avg_order,
        SUM(o.discount_amount) AS total_discount
    FROM orders o
    WHERE o.status != 'cancelled'
    GROUP BY DATE_FORMAT(o.ordered_at, '%Y-%m')
    ORDER BY month;
    ```

### v_order_detail — 주문 상세 조인

주문 + 고객 + 결제 + 배송 + 주소를 한 번에 조인한 비정규화 뷰입니다.

```mermaid
flowchart LR
    A["orders"] --> F["JOIN"]
    B["customers"] --> F
    C["payments"] --> F
    D["shipping"] --> F
    E["customer_addresses"] --> F
    F --> G["비정규화 결과:
    주문+고객+결제+
    배송+주소"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_order_detail AS
    SELECT
        o.id AS order_id,
        o.order_number,
        o.ordered_at,
        o.status AS order_status,
        o.total_amount,
        o.discount_amount,
        o.shipping_fee,
        o.notes,
        c.id AS customer_id,
        c.name AS customer_name,
        c.email AS customer_email,
        c.grade AS customer_grade,
        p.method AS payment_method,
        p.status AS payment_status,
        p.card_issuer,
        p.installment_months,
        s.carrier,
        s.tracking_number,
        s.status AS shipping_status,
        s.delivered_at,
        ca.address1 || ' ' || COALESCE(ca.address2, '') AS delivery_address
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    LEFT JOIN payments p ON o.id = p.order_id
    LEFT JOIN shipping s ON o.id = s.order_id
    LEFT JOIN customer_addresses ca ON o.address_id = ca.id
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_order_detail AS
    SELECT
        o.id AS order_id,
        o.order_number,
        o.ordered_at,
        o.status AS order_status,
        o.total_amount,
        o.discount_amount,
        o.shipping_fee,
        o.notes,
        c.id AS customer_id,
        c.name AS customer_name,
        c.email AS customer_email,
        c.grade AS customer_grade,
        p.method AS payment_method,
        p.status AS payment_status,
        p.card_issuer,
        p.installment_months,
        s.carrier,
        s.tracking_number,
        s.status AS shipping_status,
        s.delivered_at,
        CONCAT(ca.address1, ' ', COALESCE(ca.address2, '')) AS delivery_address
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    LEFT JOIN payments p ON o.id = p.order_id
    LEFT JOIN shipping s ON o.id = s.order_id
    LEFT JOIN customer_addresses ca ON o.address_id = ca.id;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_order_detail AS
    SELECT
        o.id AS order_id,
        o.order_number,
        o.ordered_at,
        o.status AS order_status,
        o.total_amount,
        o.discount_amount,
        o.shipping_fee,
        o.notes,
        c.id AS customer_id,
        c.name AS customer_name,
        c.email AS customer_email,
        c.grade AS customer_grade,
        p.method AS payment_method,
        p.status AS payment_status,
        p.card_issuer,
        p.installment_months,
        s.carrier,
        s.tracking_number,
        s.status AS shipping_status,
        s.delivered_at,
        ca.address1 || ' ' || COALESCE(ca.address2, '') AS delivery_address
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    LEFT JOIN payments p ON o.id = p.order_id
    LEFT JOIN shipping s ON o.id = s.order_id
    LEFT JOIN customer_addresses ca ON o.address_id = ca.id;
    ```

### v_payment_summary — 결제 수단 요약

결제 수단별 건수, 완료/환불/실패 비율을 집계합니다.

```mermaid
flowchart LR
    A["payments"] --> B["GROUP BY method"]
    B --> C["집계: 건수, 금액,
    비율, 완료/환불/실패"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_payment_summary AS
    SELECT
        method,
        COUNT(*) AS payment_count,
        CAST(SUM(amount) AS INTEGER) AS total_amount,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM payments), 1) AS pct,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
        SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) AS refunded,
        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed
    FROM payments
    GROUP BY method
    ORDER BY payment_count DESC
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_payment_summary AS
    SELECT
        method,
        COUNT(*) AS payment_count,
        CAST(SUM(amount) AS SIGNED) AS total_amount,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM payments), 1) AS pct,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
        SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) AS refunded,
        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed
    FROM payments
    GROUP BY method
    ORDER BY payment_count DESC;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_payment_summary AS
    SELECT
        method,
        COUNT(*) AS payment_count,
        SUM(amount)::BIGINT AS total_amount,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM payments), 1) AS pct,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
        SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) AS refunded,
        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed
    FROM payments
    GROUP BY method
    ORDER BY payment_count DESC;
    ```

### v_product_abc — 상품 ABC 분석

누적 매출 기여도를 기준으로 A(상위 70%)/B(70~90%)/C(90~100%) 등급을 분류합니다.

```mermaid
flowchart LR
    A["products +
    order_items"] --> B["상품별 매출 집계"]
    B --> C["SUM OVER
    누적 매출 비율"]
    C --> D["CASE → ABC 등급
    A≤80% B≤95% C나머지"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_product_abc AS
    SELECT
        product_id, product_name, brand, total_revenue,
        revenue_pct,
        cumulative_pct,
        CASE
            WHEN cumulative_pct <= 80 THEN 'A'
            WHEN cumulative_pct <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM (
        SELECT
            product_id, product_name, brand, total_revenue,
            ROUND(total_revenue * 100.0 / SUM(total_revenue) OVER (), 2) AS revenue_pct,
            ROUND(SUM(total_revenue) OVER (ORDER BY total_revenue DESC) * 100.0
                  / SUM(total_revenue) OVER (), 2) AS cumulative_pct
        FROM (
            SELECT
                p.id AS product_id,
                p.name AS product_name,
                p.brand,
                CAST(COALESCE(SUM(oi.subtotal), 0) AS INTEGER) AS total_revenue
            FROM products p
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id AND o.status NOT IN ('cancelled')
            GROUP BY p.id
        )
    )
    ORDER BY total_revenue DESC
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_product_abc AS
    SELECT
        product_id, product_name, brand, total_revenue,
        revenue_pct,
        cumulative_pct,
        CASE
            WHEN cumulative_pct <= 80 THEN 'A'
            WHEN cumulative_pct <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM (
        SELECT
            product_id, product_name, brand, total_revenue,
            ROUND(total_revenue * 100.0 / SUM(total_revenue) OVER (), 2) AS revenue_pct,
            ROUND(SUM(total_revenue) OVER (ORDER BY total_revenue DESC) * 100.0
                  / SUM(total_revenue) OVER (), 2) AS cumulative_pct
        FROM (
            SELECT
                p.id AS product_id,
                p.name AS product_name,
                p.brand,
                CAST(COALESCE(SUM(oi.subtotal), 0) AS SIGNED) AS total_revenue
            FROM products p
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id AND o.status != 'cancelled'
            GROUP BY p.id, p.name, p.brand
        ) base
    ) ranked
    ORDER BY total_revenue DESC;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_product_abc AS
    SELECT
        product_id, product_name, brand, total_revenue,
        revenue_pct,
        cumulative_pct,
        CASE
            WHEN cumulative_pct <= 80 THEN 'A'
            WHEN cumulative_pct <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM (
        SELECT
            product_id, product_name, brand, total_revenue,
            ROUND(total_revenue * 100.0 / SUM(total_revenue) OVER (), 2) AS revenue_pct,
            ROUND(SUM(total_revenue) OVER (ORDER BY total_revenue DESC) * 100.0
                  / SUM(total_revenue) OVER (), 2) AS cumulative_pct
        FROM (
            SELECT
                p.id AS product_id,
                p.name AS product_name,
                p.brand,
                COALESCE(SUM(oi.subtotal), 0)::BIGINT AS total_revenue
            FROM products p
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id AND o.status != 'cancelled'
            GROUP BY p.id, p.name, p.brand
        ) base
    ) ranked
    ORDER BY total_revenue DESC;
    ```

### v_product_performance — 상품 성과 지표

상품별 판매량, 매출, 마진율, 리뷰 수, 평점, 위시리스트, 반품 수를 집계합니다.

```mermaid
flowchart LR
    A["products +
    categories"] --> F["LEFT JOIN"]
    B["order_items
    판매량, 매출"] --> F
    C["reviews
    리뷰수, 평점"] --> F
    D["wishlists
    위시리스트 수"] --> F
    E["returns
    반품 수"] --> F
    F --> G["마진율 계산
    + 종합 지표"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_product_performance AS
    SELECT
        p.id,
        p.name,
        p.brand,
        p.sku,
        c.name AS category,
        p.price,
        p.cost_price,
        ROUND((p.price - p.cost_price) / p.price * 100, 1) AS margin_pct,
        p.stock_qty,
        p.is_active,
        COALESCE(s.total_sold, 0) AS total_sold,
        COALESCE(s.total_revenue, 0) AS total_revenue,
        COALESCE(s.order_count, 0) AS order_count,
        COALESCE(rv.review_count, 0) AS review_count,
        COALESCE(rv.avg_rating, 0) AS avg_rating,
        COALESCE(ws.wishlist_count, 0) AS wishlist_count,
        COALESCE(rt.return_count, 0) AS return_count
    FROM products p
    JOIN categories c ON p.category_id = c.id
    LEFT JOIN (
        SELECT oi.product_id,
               SUM(oi.quantity) AS total_sold,
               CAST(SUM(oi.subtotal) AS INTEGER) AS total_revenue,
               COUNT(DISTINCT oi.order_id) AS order_count
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    ) s ON p.id = s.product_id
    LEFT JOIN (
        SELECT product_id,
               COUNT(*) AS review_count,
               ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews
        GROUP BY product_id
    ) rv ON p.id = rv.product_id
    LEFT JOIN (
        SELECT product_id, COUNT(*) AS wishlist_count
        FROM wishlists
        GROUP BY product_id
    ) ws ON p.id = ws.product_id
    LEFT JOIN (
        SELECT oi.product_id, COUNT(DISTINCT r.id) AS return_count
        FROM returns r
        JOIN order_items oi ON r.order_id = oi.order_id
        GROUP BY oi.product_id
    ) rt ON p.id = rt.product_id
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_product_performance AS
    SELECT
        p.id,
        p.name,
        p.brand,
        p.sku,
        c.name AS category,
        p.price,
        p.cost_price,
        ROUND((p.price - p.cost_price) / p.price * 100, 1) AS margin_pct,
        p.stock_qty,
        p.is_active,
        COALESCE(s.total_sold, 0) AS total_sold,
        COALESCE(s.total_revenue, 0) AS total_revenue,
        COALESCE(s.order_count, 0) AS order_count,
        COALESCE(rv.review_count, 0) AS review_count,
        COALESCE(rv.avg_rating, 0) AS avg_rating,
        COALESCE(ws.wishlist_count, 0) AS wishlist_count,
        COALESCE(rt.return_count, 0) AS return_count
    FROM products p
    JOIN categories c ON p.category_id = c.id
    LEFT JOIN (
        SELECT oi.product_id,
               SUM(oi.quantity) AS total_sold,
               CAST(SUM(oi.subtotal) AS SIGNED) AS total_revenue,
               COUNT(DISTINCT oi.order_id) AS order_count
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status != 'cancelled'
        GROUP BY oi.product_id
    ) s ON p.id = s.product_id
    LEFT JOIN (
        SELECT product_id,
               COUNT(*) AS review_count,
               ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews
        GROUP BY product_id
    ) rv ON p.id = rv.product_id
    LEFT JOIN (
        SELECT product_id, COUNT(*) AS wishlist_count
        FROM wishlists
        GROUP BY product_id
    ) ws ON p.id = ws.product_id
    LEFT JOIN (
        SELECT oi.product_id, COUNT(DISTINCT r.id) AS return_count
        FROM returns r
        JOIN order_items oi ON r.order_id = oi.order_id
        GROUP BY oi.product_id
    ) rt ON p.id = rt.product_id;
    ```

### v_return_analysis — 반품 분석

반품 사유별 건수, 환불/교환 비율, 검수 결과, 평균 처리일수를 분석합니다.

```mermaid
flowchart LR
    A["returns"] --> B["GROUP BY reason"]
    B --> C["집계: 건수, 비율,
    환불/교환, 평균환불액"]
    C --> D["검수결과 집계
    + 평균처리일수"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_return_analysis AS
    SELECT
        reason,
        COUNT(*) AS total_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM returns), 1) AS pct,
        SUM(CASE WHEN return_type = 'refund' THEN 1 ELSE 0 END) AS refund_count,
        SUM(CASE WHEN return_type = 'exchange' THEN 1 ELSE 0 END) AS exchange_count,
        CAST(AVG(refund_amount) AS INTEGER) AS avg_refund_amount,
        SUM(CASE WHEN inspection_result = 'defective' THEN 1 ELSE 0 END) AS defective_count,
        SUM(CASE WHEN inspection_result = 'good' THEN 1 ELSE 0 END) AS good_count,
        CAST(AVG(
            CASE WHEN completed_at IS NOT NULL
            THEN julianday(completed_at) - julianday(requested_at)
            END
        ) AS INTEGER) AS avg_process_days
    FROM returns
    GROUP BY reason
    ORDER BY total_count DESC
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_return_analysis AS
    SELECT
        reason,
        COUNT(*) AS total_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM returns), 1) AS pct,
        SUM(CASE WHEN return_type = 'refund' THEN 1 ELSE 0 END) AS refund_count,
        SUM(CASE WHEN return_type = 'exchange' THEN 1 ELSE 0 END) AS exchange_count,
        CAST(AVG(refund_amount) AS SIGNED) AS avg_refund_amount,
        SUM(CASE WHEN inspection_result = 'defective' THEN 1 ELSE 0 END) AS defective_count,
        SUM(CASE WHEN inspection_result = 'good' THEN 1 ELSE 0 END) AS good_count,
        CAST(AVG(
            CASE WHEN completed_at IS NOT NULL
            THEN DATEDIFF(completed_at, requested_at)
            END
        ) AS SIGNED) AS avg_process_days
    FROM returns
    GROUP BY reason
    ORDER BY total_count DESC;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_return_analysis AS
    SELECT
        reason,
        COUNT(*) AS total_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM returns), 1) AS pct,
        SUM(CASE WHEN return_type = 'refund' THEN 1 ELSE 0 END) AS refund_count,
        SUM(CASE WHEN return_type = 'exchange' THEN 1 ELSE 0 END) AS exchange_count,
        AVG(refund_amount)::INT AS avg_refund_amount,
        SUM(CASE WHEN inspection_result = 'defective' THEN 1 ELSE 0 END) AS defective_count,
        SUM(CASE WHEN inspection_result = 'good' THEN 1 ELSE 0 END) AS good_count,
        (AVG(
            CASE WHEN completed_at IS NOT NULL
            THEN EXTRACT(DAY FROM (completed_at - requested_at))
            END
        ))::INT AS avg_process_days
    FROM returns
    GROUP BY reason
    ORDER BY total_count DESC;
    ```

### v_revenue_growth — 월별 매출 성장률

LAG 윈도우 함수로 전월 대비 매출 성장률(%)을 계산합니다.

```mermaid
flowchart LR
    A["orders
    (취소 제외)"] --> B["GROUP BY 월"]
    B --> C["월별 매출"]
    C --> D["LAG → 전월 매출"]
    D --> E["성장률 %
    (현재-전월)/전월"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_revenue_growth AS
    SELECT
        month,
        revenue,
        prev_revenue,
        CASE
            WHEN prev_revenue > 0
            THEN ROUND((revenue - prev_revenue) * 100.0 / prev_revenue, 1)
            ELSE NULL
        END AS growth_pct
    FROM (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS month,
            CAST(SUM(total_amount) AS INTEGER) AS revenue,
            LAG(CAST(SUM(total_amount) AS INTEGER)) OVER (ORDER BY SUBSTR(ordered_at, 1, 7)) AS prev_revenue
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    ORDER BY month
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_revenue_growth AS
    SELECT
        month,
        revenue,
        prev_revenue,
        CASE
            WHEN prev_revenue > 0
            THEN ROUND((revenue - prev_revenue) * 100.0 / prev_revenue, 1)
            ELSE NULL
        END AS growth_pct
    FROM (
        SELECT
            DATE_FORMAT(ordered_at, '%Y-%m') AS month,
            CAST(SUM(total_amount) AS SIGNED) AS revenue,
            LAG(CAST(SUM(total_amount) AS SIGNED)) OVER (ORDER BY DATE_FORMAT(ordered_at, '%Y-%m')) AS prev_revenue
        FROM orders
        WHERE status != 'cancelled'
        GROUP BY DATE_FORMAT(ordered_at, '%Y-%m')
    ) sub
    ORDER BY month;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_revenue_growth AS
    SELECT
        month,
        revenue,
        prev_revenue,
        CASE
            WHEN prev_revenue > 0
            THEN ROUND((revenue - prev_revenue) * 100.0 / prev_revenue, 1)
            ELSE NULL
        END AS growth_pct
    FROM (
        SELECT
            TO_CHAR(ordered_at, 'YYYY-MM') AS month,
            SUM(total_amount)::BIGINT AS revenue,
            LAG(SUM(total_amount)::BIGINT) OVER (ORDER BY TO_CHAR(ordered_at, 'YYYY-MM')) AS prev_revenue
        FROM orders
        WHERE status != 'cancelled'
        GROUP BY TO_CHAR(ordered_at, 'YYYY-MM')
    ) sub
    ORDER BY month;
    ```

### v_staff_workload — CS 직원 업무량

CS 직원별 문의 처리 수, 해결률, 평균 처리 시간을 집계합니다.

```mermaid
flowchart LR
    A["staff
    (CS 부서)"] --> D["LEFT JOIN"]
    B["complaints 집계
    처리수, 해결수,
    평균처리시간"] --> D
    C["orders 집계
    CS 주문수"] --> D
    D --> E["직원별 업무량"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_staff_workload AS
    SELECT
        s.id AS staff_id,
        s.name,
        s.department,
        COALESCE(comp.complaint_count, 0) AS complaint_count,
        COALESCE(comp.resolved_count, 0) AS resolved_count,
        COALESCE(comp.avg_resolve_hours, 0) AS avg_resolve_hours,
        COALESCE(ord.cs_order_count, 0) AS cs_order_count
    FROM staff s
    LEFT JOIN (
        SELECT
            staff_id,
            COUNT(*) AS complaint_count,
            SUM(CASE WHEN status IN ('resolved','closed') THEN 1 ELSE 0 END) AS resolved_count,
            CAST(AVG(
                CASE WHEN resolved_at IS NOT NULL
                THEN (julianday(resolved_at) - julianday(created_at)) * 24
                END
            ) AS INTEGER) AS avg_resolve_hours
        FROM complaints
        GROUP BY staff_id
    ) comp ON s.id = comp.staff_id
    LEFT JOIN (
        SELECT staff_id, COUNT(*) AS cs_order_count
        FROM orders WHERE staff_id IS NOT NULL
        GROUP BY staff_id
    ) ord ON s.id = ord.staff_id
    WHERE s.department = 'CS' OR comp.complaint_count > 0
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_staff_workload AS
    SELECT
        s.id AS staff_id,
        s.name,
        s.department,
        COALESCE(comp.complaint_count, 0) AS complaint_count,
        COALESCE(comp.resolved_count, 0) AS resolved_count,
        COALESCE(comp.avg_resolve_hours, 0) AS avg_resolve_hours,
        COALESCE(ord.cs_order_count, 0) AS cs_order_count
    FROM staff s
    LEFT JOIN (
        SELECT
            staff_id,
            COUNT(*) AS complaint_count,
            SUM(CASE WHEN status IN ('resolved','closed') THEN 1 ELSE 0 END) AS resolved_count,
            CAST(AVG(
                CASE WHEN resolved_at IS NOT NULL
                THEN TIMESTAMPDIFF(HOUR, created_at, resolved_at)
                END
            ) AS SIGNED) AS avg_resolve_hours
        FROM complaints
        GROUP BY staff_id
    ) comp ON s.id = comp.staff_id
    LEFT JOIN (
        SELECT staff_id, COUNT(*) AS cs_order_count
        FROM orders WHERE staff_id IS NOT NULL
        GROUP BY staff_id
    ) ord ON s.id = ord.staff_id
    WHERE s.department = 'CS' OR comp.complaint_count > 0;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_staff_workload AS
    SELECT
        s.id AS staff_id,
        s.name,
        s.department,
        COALESCE(comp.complaint_count, 0) AS complaint_count,
        COALESCE(comp.resolved_count, 0) AS resolved_count,
        COALESCE(comp.avg_resolve_hours, 0) AS avg_resolve_hours,
        COALESCE(ord.cs_order_count, 0) AS cs_order_count
    FROM staff s
    LEFT JOIN (
        SELECT
            staff_id,
            COUNT(*) AS complaint_count,
            SUM(CASE WHEN status IN ('resolved','closed') THEN 1 ELSE 0 END) AS resolved_count,
            (AVG(
                CASE WHEN resolved_at IS NOT NULL
                THEN EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600
                END
            ))::INT AS avg_resolve_hours
        FROM complaints
        GROUP BY staff_id
    ) comp ON s.id = comp.staff_id
    LEFT JOIN (
        SELECT staff_id, COUNT(*) AS cs_order_count
        FROM orders WHERE staff_id IS NOT NULL
        GROUP BY staff_id
    ) ord ON s.id = ord.staff_id
    WHERE s.department = 'CS' OR comp.complaint_count > 0;
    ```

### v_supplier_performance — 공급업체 성과

공급업체별 상품 수, 매출, 반품률을 집계합니다.

```mermaid
flowchart LR
    A["suppliers +
    products"] --> D["LEFT JOIN"]
    B["order_items
    매출, 판매량"] --> D
    C["returns
    반품 수"] --> D
    D --> E["반품률 계산
    + 공급업체별 성과"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_supplier_performance AS
    SELECT
        s.id AS supplier_id,
        s.company_name,
        COUNT(DISTINCT p.id) AS product_count,
        SUM(CASE WHEN p.is_active = 1 THEN 1 ELSE 0 END) AS active_products,
        COALESCE(sales.total_revenue, 0) AS total_revenue,
        COALESCE(sales.total_sold, 0) AS total_sold,
        COALESCE(ret.return_count, 0) AS return_count,
        CASE
            WHEN COALESCE(sales.total_sold, 0) > 0
            THEN ROUND(COALESCE(ret.return_count, 0) * 100.0 / sales.total_sold, 2)
            ELSE 0
        END AS return_rate_pct
    FROM suppliers s
    LEFT JOIN products p ON s.id = p.supplier_id
    LEFT JOIN (
        SELECT p2.supplier_id,
               CAST(SUM(oi.subtotal) AS INTEGER) AS total_revenue,
               SUM(oi.quantity) AS total_sold
        FROM order_items oi
        JOIN products p2 ON oi.product_id = p2.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY p2.supplier_id
    ) sales ON s.id = sales.supplier_id
    LEFT JOIN (
        SELECT p3.supplier_id, COUNT(*) AS return_count
        FROM returns r
        JOIN order_items oi ON r.order_id = oi.order_id
        JOIN products p3 ON oi.product_id = p3.id
        GROUP BY p3.supplier_id
    ) ret ON s.id = ret.supplier_id
    GROUP BY s.id
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_supplier_performance AS
    SELECT
        s.id AS supplier_id,
        s.company_name,
        COUNT(DISTINCT p.id) AS product_count,
        SUM(CASE WHEN p.is_active = 1 THEN 1 ELSE 0 END) AS active_products,
        COALESCE(sales.total_revenue, 0) AS total_revenue,
        COALESCE(sales.total_sold, 0) AS total_sold,
        COALESCE(ret.return_count, 0) AS return_count,
        CASE
            WHEN COALESCE(sales.total_sold, 0) > 0
            THEN ROUND(COALESCE(ret.return_count, 0) * 100.0 / sales.total_sold, 2)
            ELSE 0
        END AS return_rate_pct
    FROM suppliers s
    LEFT JOIN products p ON s.id = p.supplier_id
    LEFT JOIN (
        SELECT p2.supplier_id,
               CAST(SUM(oi.subtotal) AS SIGNED) AS total_revenue,
               SUM(oi.quantity) AS total_sold
        FROM order_items oi
        JOIN products p2 ON oi.product_id = p2.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status != 'cancelled'
        GROUP BY p2.supplier_id
    ) sales ON s.id = sales.supplier_id
    LEFT JOIN (
        SELECT p3.supplier_id, COUNT(*) AS return_count
        FROM returns r
        JOIN order_items oi ON r.order_id = oi.order_id
        JOIN products p3 ON oi.product_id = p3.id
        GROUP BY p3.supplier_id
    ) ret ON s.id = ret.supplier_id
    GROUP BY s.id, s.company_name;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_supplier_performance AS
    SELECT
        s.id AS supplier_id,
        s.company_name,
        COUNT(DISTINCT p.id) AS product_count,
        SUM(CASE WHEN p.is_active THEN 1 ELSE 0 END) AS active_products,
        COALESCE(sales.total_revenue, 0) AS total_revenue,
        COALESCE(sales.total_sold, 0) AS total_sold,
        COALESCE(ret.return_count, 0) AS return_count,
        CASE
            WHEN COALESCE(sales.total_sold, 0) > 0
            THEN ROUND(COALESCE(ret.return_count, 0) * 100.0 / sales.total_sold, 2)
            ELSE 0
        END AS return_rate_pct
    FROM suppliers s
    LEFT JOIN products p ON s.id = p.supplier_id
    LEFT JOIN (
        SELECT p2.supplier_id,
               SUM(oi.subtotal)::BIGINT AS total_revenue,
               SUM(oi.quantity) AS total_sold
        FROM order_items oi
        JOIN products p2 ON oi.product_id = p2.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status != 'cancelled'
        GROUP BY p2.supplier_id
    ) sales ON s.id = sales.supplier_id
    LEFT JOIN (
        SELECT p3.supplier_id, COUNT(*) AS return_count
        FROM returns r
        JOIN order_items oi ON r.order_id = oi.order_id
        JOIN products p3 ON oi.product_id = p3.id
        GROUP BY p3.supplier_id
    ) ret ON s.id = ret.supplier_id
    GROUP BY s.id, s.company_name;
    ```

### v_top_products_by_category — 카테고리별 Top 상품

ROW_NUMBER로 카테고리별 매출 상위 5개 상품을 추출합니다.

```mermaid
flowchart LR
    A["products +
    categories"] --> B["LEFT JOIN
    order_items + orders"]
    B --> C["GROUP BY 상품"]
    C --> D["ROW_NUMBER
    PARTITION BY category
    ORDER BY revenue DESC"]
    D --> E["WHERE rank ≤ 5"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_top_products_by_category AS
    SELECT
        category_name,
        product_name,
        brand,
        total_revenue,
        total_sold,
        rank_in_category
    FROM (
        SELECT
            cat.name AS category_name,
            p.name AS product_name,
            p.brand,
            COALESCE(SUM(oi.subtotal), 0) AS total_revenue,
            COALESCE(SUM(oi.quantity), 0) AS total_sold,
            ROW_NUMBER() OVER (
                PARTITION BY p.category_id
                ORDER BY COALESCE(SUM(oi.subtotal), 0) DESC
            ) AS rank_in_category
        FROM products p
        JOIN categories cat ON p.category_id = cat.id
        LEFT JOIN order_items oi ON p.id = oi.product_id
        LEFT JOIN orders o ON oi.order_id = o.id AND o.status NOT IN ('cancelled')
        GROUP BY p.id
    )
    WHERE rank_in_category <= 5
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_top_products_by_category AS
    SELECT
        category_name,
        product_name,
        brand,
        total_revenue,
        total_sold,
        rank_in_category
    FROM (
        SELECT
            cat.name AS category_name,
            p.name AS product_name,
            p.brand,
            COALESCE(SUM(oi.subtotal), 0) AS total_revenue,
            COALESCE(SUM(oi.quantity), 0) AS total_sold,
            ROW_NUMBER() OVER (
                PARTITION BY p.category_id
                ORDER BY COALESCE(SUM(oi.subtotal), 0) DESC
            ) AS rank_in_category
        FROM products p
        JOIN categories cat ON p.category_id = cat.id
        LEFT JOIN order_items oi ON p.id = oi.product_id
        LEFT JOIN orders o ON oi.order_id = o.id AND o.status != 'cancelled'
        GROUP BY p.id, cat.name, p.name, p.brand, p.category_id
    ) sub
    WHERE rank_in_category <= 5;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_top_products_by_category AS
    SELECT
        category_name,
        product_name,
        brand,
        total_revenue,
        total_sold,
        rank_in_category
    FROM (
        SELECT
            cat.name AS category_name,
            p.name AS product_name,
            p.brand,
            COALESCE(SUM(oi.subtotal), 0)::BIGINT AS total_revenue,
            COALESCE(SUM(oi.quantity), 0) AS total_sold,
            ROW_NUMBER() OVER (
                PARTITION BY p.category_id
                ORDER BY COALESCE(SUM(oi.subtotal), 0) DESC
            ) AS rank_in_category
        FROM products p
        JOIN categories cat ON p.category_id = cat.id
        LEFT JOIN order_items oi ON p.id = oi.product_id
        LEFT JOIN orders o ON oi.order_id = o.id AND o.status != 'cancelled'
        GROUP BY p.id, cat.name, p.name, p.brand, p.category_id
    ) sub
    WHERE rank_in_category <= 5;
    ```

### v_yearly_kpi — 연도별 핵심 KPI

연간 매출, 주문 수, 고객 수, 취소율, 반품률 등 핵심 지표를 집계합니다.

```mermaid
flowchart LR
    A["orders
    연도별 집계"] --> E["LEFT JOIN"]
    B["customers
    신규 고객수"] --> E
    C["reviews
    리뷰수"] --> E
    D["complaints
    불만수"] --> E
    E --> F["연간 KPI: 매출,
    주문, 취소율,
    반품률, 리뷰, 불만"]
```

=== "SQLite"

    ```sql
    CREATE VIEW v_yearly_kpi AS
    SELECT
        o_stats.yr AS year,
        o_stats.total_revenue,
        o_stats.order_count,
        o_stats.customer_count,
        CAST(o_stats.total_revenue * 1.0 / o_stats.order_count AS INTEGER) AS avg_order_value,
        CAST(o_stats.total_revenue * 1.0 / o_stats.customer_count AS INTEGER) AS revenue_per_customer,
        COALESCE(c.new_customers, 0) AS new_customers,
        o_stats.cancel_count,
        ROUND(o_stats.cancel_count * 100.0 / o_stats.order_count, 1) AS cancel_rate_pct,
        o_stats.return_count,
        ROUND(o_stats.return_count * 100.0 / o_stats.order_count, 1) AS return_rate_pct,
        COALESCE(r.review_count, 0) AS review_count,
        COALESCE(comp.complaint_count, 0) AS complaint_count
    FROM (
        SELECT
            SUBSTR(o.ordered_at, 1, 4) AS yr,
            CAST(SUM(CASE WHEN o.status NOT IN ('cancelled') THEN o.total_amount ELSE 0 END) AS INTEGER) AS total_revenue,
            COUNT(*) AS order_count,
            COUNT(DISTINCT o.customer_id) AS customer_count,
            SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) AS cancel_count,
            SUM(CASE WHEN o.status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS return_count
        FROM orders o
        GROUP BY SUBSTR(o.ordered_at, 1, 4)
    ) o_stats
    LEFT JOIN (
        SELECT SUBSTR(created_at, 1, 4) AS yr, COUNT(*) AS new_customers
        FROM customers GROUP BY SUBSTR(created_at, 1, 4)
    ) c ON o_stats.yr = c.yr
    LEFT JOIN (
        SELECT SUBSTR(created_at, 1, 4) AS yr, COUNT(*) AS review_count
        FROM reviews GROUP BY SUBSTR(created_at, 1, 4)
    ) r ON o_stats.yr = r.yr
    LEFT JOIN (
        SELECT SUBSTR(created_at, 1, 4) AS yr, COUNT(*) AS complaint_count
        FROM complaints GROUP BY SUBSTR(created_at, 1, 4)
    ) comp ON o_stats.yr = comp.yr
    ORDER BY o_stats.yr
    ```

=== "MySQL"

    ```sql
    CREATE OR REPLACE VIEW v_yearly_kpi AS
    SELECT
        o_stats.yr AS year,
        o_stats.total_revenue,
        o_stats.order_count,
        o_stats.customer_count,
        CAST(o_stats.total_revenue / o_stats.order_count AS SIGNED) AS avg_order_value,
        CAST(o_stats.total_revenue / o_stats.customer_count AS SIGNED) AS revenue_per_customer,
        COALESCE(c.new_customers, 0) AS new_customers,
        o_stats.cancel_count,
        ROUND(o_stats.cancel_count * 100.0 / o_stats.order_count, 1) AS cancel_rate_pct,
        o_stats.return_count,
        ROUND(o_stats.return_count * 100.0 / o_stats.order_count, 1) AS return_rate_pct,
        COALESCE(r.review_count, 0) AS review_count,
        COALESCE(comp.complaint_count, 0) AS complaint_count
    FROM (
        SELECT
            YEAR(o.ordered_at) AS yr,
            CAST(SUM(CASE WHEN o.status != 'cancelled' THEN o.total_amount ELSE 0 END) AS SIGNED) AS total_revenue,
            COUNT(*) AS order_count,
            COUNT(DISTINCT o.customer_id) AS customer_count,
            SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) AS cancel_count,
            SUM(CASE WHEN o.status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS return_count
        FROM orders o
        GROUP BY YEAR(o.ordered_at)
    ) o_stats
    LEFT JOIN (
        SELECT YEAR(created_at) AS yr, COUNT(*) AS new_customers
        FROM customers GROUP BY YEAR(created_at)
    ) c ON o_stats.yr = c.yr
    LEFT JOIN (
        SELECT YEAR(created_at) AS yr, COUNT(*) AS review_count
        FROM reviews GROUP BY YEAR(created_at)
    ) r ON o_stats.yr = r.yr
    LEFT JOIN (
        SELECT YEAR(created_at) AS yr, COUNT(*) AS complaint_count
        FROM complaints GROUP BY YEAR(created_at)
    ) comp ON o_stats.yr = comp.yr
    ORDER BY o_stats.yr;
    ```

=== "PostgreSQL"

    ```sql
    CREATE OR REPLACE VIEW v_yearly_kpi AS
    SELECT
        o_stats.yr AS year,
        o_stats.total_revenue,
        o_stats.order_count,
        o_stats.customer_count,
        (o_stats.total_revenue / o_stats.order_count)::INT AS avg_order_value,
        (o_stats.total_revenue / o_stats.customer_count)::INT AS revenue_per_customer,
        COALESCE(c.new_customers, 0) AS new_customers,
        o_stats.cancel_count,
        ROUND(o_stats.cancel_count * 100.0 / o_stats.order_count, 1) AS cancel_rate_pct,
        o_stats.return_count,
        ROUND(o_stats.return_count * 100.0 / o_stats.order_count, 1) AS return_rate_pct,
        COALESCE(r.review_count, 0) AS review_count,
        COALESCE(comp.complaint_count, 0) AS complaint_count
    FROM (
        SELECT
            EXTRACT(YEAR FROM o.ordered_at)::INT AS yr,
            SUM(CASE WHEN o.status != 'cancelled' THEN o.total_amount ELSE 0 END)::BIGINT AS total_revenue,
            COUNT(*) AS order_count,
            COUNT(DISTINCT o.customer_id) AS customer_count,
            SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) AS cancel_count,
            SUM(CASE WHEN o.status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS return_count
        FROM orders o
        GROUP BY EXTRACT(YEAR FROM o.ordered_at)::INT
    ) o_stats
    LEFT JOIN (
        SELECT EXTRACT(YEAR FROM created_at)::INT AS yr, COUNT(*) AS new_customers
        FROM customers GROUP BY EXTRACT(YEAR FROM created_at)::INT
    ) c ON o_stats.yr = c.yr
    LEFT JOIN (
        SELECT EXTRACT(YEAR FROM created_at)::INT AS yr, COUNT(*) AS review_count
        FROM reviews GROUP BY EXTRACT(YEAR FROM created_at)::INT
    ) r ON o_stats.yr = r.yr
    LEFT JOIN (
        SELECT EXTRACT(YEAR FROM created_at)::INT AS yr, COUNT(*) AS complaint_count
        FROM complaints GROUP BY EXTRACT(YEAR FROM created_at)::INT
    ) comp ON o_stats.yr = comp.yr
    ORDER BY o_stats.yr;
    ```


