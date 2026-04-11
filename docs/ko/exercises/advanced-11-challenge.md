# 도전 문제

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `customers` — 고객<br>
    `orders` — 주문<br>
    `order_items` — 주문 상세<br>
    `products` — 상품<br>
    `product_prices` — 가격 변경 이력<br>
    `point_transactions` — 포인트 적립/사용<br>
    `calendar` — 날짜 참조<br>
    `staff` — 직원

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    원장 검증<br>
    가격 변경 영향 분석<br>
    장바구니 분석(연관 규칙)<br>
    재고 최적화<br>
    고객 이탈 예측 — 미니 프로젝트급 종합 문제

</div>

각 문제는 여러 단계의 분석을 요구하는 미니 프로젝트입니다.
실무에서 마주치는 복잡한 시나리오를 재현하며, 모든 SQL 개념을 종합적으로 활용합니다.

---


### 문제 1. 포인트 잔액 재구성 (원장 검증)


`point_transactions` 테이블의 거래 이력만으로 각 고객의 **포인트 잔액을 재구성**하고,
`customers.point_balance`와 비교하여 **불일치하는 고객**을 찾으세요.
각 고객의 적립/사용/만료 내역 요약도 함께 표시합니다.

| customer_name | earn_total | use_total | expire_total | calculated_balance | actual_balance | difference |
|-------------|-----------|---------|------------|------------------|--------------|-----------|


??? tip "힌트"
    - `point_transactions.amount`에서 `type`별로 합산: earn(+), use(-), expire(-)
    - 계산된 잔액: `SUM(amount)` (amount가 이미 +/-로 구분되어 있음)
    - `customers.point_balance`와 비교하여 `HAVING calculated != actual`


??? success "정답"
    ```sql
    WITH point_summary AS (
        SELECT
            pt.customer_id,
            SUM(CASE WHEN pt.type = 'earn' THEN pt.amount ELSE 0 END) AS earn_total,
            SUM(CASE WHEN pt.type = 'use' THEN ABS(pt.amount) ELSE 0 END) AS use_total,
            SUM(CASE WHEN pt.type = 'expire' THEN ABS(pt.amount) ELSE 0 END) AS expire_total,
            SUM(pt.amount) AS calculated_balance
        FROM point_transactions AS pt
        GROUP BY pt.customer_id
    )
    SELECT
        c.name AS customer_name,
        ps.earn_total,
        ps.use_total,
        ps.expire_total,
        ps.calculated_balance,
        c.point_balance AS actual_balance,
        ps.calculated_balance - c.point_balance AS difference
    FROM point_summary AS ps
    JOIN customers AS c ON ps.customer_id = c.id
    WHERE ps.calculated_balance != c.point_balance
    ORDER BY ABS(ps.calculated_balance - c.point_balance) DESC;
    ```


---


### 문제 2. 가격 탄력성 분석


`product_prices` 이력을 활용하여, 가격 변동이 판매량에 미치는 영향을 분석하세요.
**가격이 10% 이상 변동한 시점** 전후 30일의 일평균 판매량을 비교하고,
가격 탄력성(판매량 변화율 / 가격 변화율)을 계산합니다.

| product_name | price_change_date | old_price | new_price | price_change_pct | before_daily_avg | after_daily_avg | qty_change_pct | elasticity |
|-------------|-----------------|---------|---------|-----------------|----------------|---------------|---------------|-----------|


??? tip "힌트"
    - `product_prices`에서 `LAG(price)` 로 이전 가격과 비교 → 10% 이상 변동 필터
    - 전/후 30일: `ordered_at BETWEEN DATE(변동일, '-30 days') AND DATE(변동일, '-1 day')` vs `+1 day ~ +30 days`
    - 탄력성 = (판매량 변화율 / 가격 변화율)


??? success "정답"
    ```sql
    WITH price_changes AS (
        SELECT
            pp.product_id,
            pp.started_at AS change_date,
            LAG(pp.price) OVER (PARTITION BY pp.product_id ORDER BY pp.started_at) AS old_price,
            pp.price AS new_price
        FROM product_prices AS pp
    ),
    significant_changes AS (
        SELECT *,
            ROUND(100.0 * (new_price - old_price) / old_price, 1) AS price_change_pct
        FROM price_changes
        WHERE old_price IS NOT NULL
          AND ABS(100.0 * (new_price - old_price) / old_price) >= 10
    ),
    before_sales AS (
        SELECT
            sc.product_id,
            sc.change_date,
            1.0 * COALESCE(SUM(oi.quantity), 0)
                / MAX(1, CAST(julianday(sc.change_date) - julianday(DATE(sc.change_date, '-30 days')) AS INTEGER))
                AS before_daily_avg
        FROM significant_changes AS sc
        LEFT JOIN order_items AS oi ON oi.product_id = sc.product_id
        LEFT JOIN orders AS o ON oi.order_id = o.id
            AND o.ordered_at >= DATE(sc.change_date, '-30 days')
            AND o.ordered_at <  sc.change_date
            AND o.status NOT IN ('cancelled')
        GROUP BY sc.product_id, sc.change_date
    ),
    after_sales AS (
        SELECT
            sc.product_id,
            sc.change_date,
            1.0 * COALESCE(SUM(oi.quantity), 0)
                / MAX(1, 30)
                AS after_daily_avg
        FROM significant_changes AS sc
        LEFT JOIN order_items AS oi ON oi.product_id = sc.product_id
        LEFT JOIN orders AS o ON oi.order_id = o.id
            AND o.ordered_at > sc.change_date
            AND o.ordered_at <= DATE(sc.change_date, '+30 days')
            AND o.status NOT IN ('cancelled')
        GROUP BY sc.product_id, sc.change_date
    )
    SELECT
        p.name AS product_name,
        sc.change_date AS price_change_date,
        CAST(sc.old_price AS INTEGER) AS old_price,
        CAST(sc.new_price AS INTEGER) AS new_price,
        sc.price_change_pct,
        ROUND(bs.before_daily_avg, 2) AS before_daily_avg,
        ROUND(afs.after_daily_avg, 2) AS after_daily_avg,
        ROUND(100.0 * (afs.after_daily_avg - bs.before_daily_avg)
            / NULLIF(bs.before_daily_avg, 0), 1) AS qty_change_pct,
        ROUND(
            (100.0 * (afs.after_daily_avg - bs.before_daily_avg) / NULLIF(bs.before_daily_avg, 0))
            / NULLIF(sc.price_change_pct, 0),
        2) AS elasticity
    FROM significant_changes AS sc
    JOIN products     AS p   ON sc.product_id = p.id
    JOIN before_sales AS bs  ON sc.product_id = bs.product_id AND sc.change_date = bs.change_date
    JOIN after_sales  AS afs ON sc.product_id = afs.product_id AND sc.change_date = afs.change_date
    WHERE bs.before_daily_avg > 0
    ORDER BY ABS(elasticity) DESC
    LIMIT 20;
    ```


---


### 문제 3. 상품 연관 네트워크 (Market Basket)


같은 주문에 **함께 구매된 상품 쌍**의 빈도를 분석하세요.
동시 구매 빈도가 높은 상위 20개 상품 조합과 **지지도(support)**, **신뢰도(confidence)**를 계산합니다.

| product_a | product_b | co_purchase_count | support_pct | confidence_a_to_b | confidence_b_to_a |
|----------|----------|------------------|-----------|-------------------|-------------------|


??? tip "힌트"
    - Self-Join: `order_items AS a JOIN order_items AS b ON a.order_id = b.order_id AND a.product_id < b.product_id`
    - 지지도 = 동시 구매 주문 수 / 전체 주문 수
    - 신뢰도(A→B) = 동시 구매 수 / A 구매 수


??? success "정답"
    ```sql
    WITH valid_orders AS (
        SELECT DISTINCT id FROM orders WHERE status NOT IN ('cancelled')
    ),
    total AS (
        SELECT COUNT(*) AS total_orders FROM valid_orders
    ),
    pairs AS (
        SELECT
            a.product_id AS pid_a,
            b.product_id AS pid_b,
            COUNT(DISTINCT a.order_id) AS co_count
        FROM order_items AS a
        JOIN order_items AS b
            ON a.order_id = b.order_id
           AND a.product_id < b.product_id
        JOIN valid_orders AS vo ON a.order_id = vo.id
        GROUP BY a.product_id, b.product_id
        HAVING COUNT(DISTINCT a.order_id) >= 5
    ),
    product_counts AS (
        SELECT product_id, COUNT(DISTINCT order_id) AS order_count
        FROM order_items
        JOIN valid_orders ON order_items.order_id = valid_orders.id
        GROUP BY product_id
    )
    SELECT
        pa.name AS product_a,
        pb.name AS product_b,
        pr.co_count AS co_purchase_count,
        ROUND(100.0 * pr.co_count / t.total_orders, 3) AS support_pct,
        ROUND(100.0 * pr.co_count / pca.order_count, 1) AS confidence_a_to_b,
        ROUND(100.0 * pr.co_count / pcb.order_count, 1) AS confidence_b_to_a
    FROM pairs AS pr
    CROSS JOIN total AS t
    JOIN products       AS pa  ON pr.pid_a = pa.id
    JOIN products       AS pb  ON pr.pid_b = pb.id
    JOIN product_counts AS pca ON pr.pid_a = pca.product_id
    JOIN product_counts AS pcb ON pr.pid_b = pcb.product_id
    ORDER BY pr.co_count DESC
    LIMIT 20;
    ```


---


### 문제 4. 재고 회전율 및 적정 재고 분석


상품별 **재고 회전율(Inventory Turnover)**과 **재고 일수(Days of Inventory)**를 구하세요.
최근 90일 판매 속도 기준으로 **적정 재고량**과 현재 재고 과부족을 판단합니다.

| product_name | current_stock | avg_daily_sales_90d | days_of_inventory | turnover_rate | optimal_stock_30d | stock_status |
|-------------|-------------|-------------------|------------------|-------------|-----------------|-------------|


??? tip "힌트"
    - 90일 평균 일일 판매량: `SUM(quantity) / 90` (최근 90일 주문 기준)
    - 재고일수: `current_stock / 평균 일일 판매량`
    - 회전율: `(연간 판매량 * 상품 원가) / 현재 재고 원가`
    - 적정 재고(30일): `일일 평균 * 30`
    - 상태: 과잉(>60일), 적정(15~60일), 부족(<15일), 품절(0)


??? success "정답"
    ```sql
    WITH recent_sales AS (
        SELECT
            oi.product_id,
            SUM(oi.quantity) AS qty_90d,
            ROUND(1.0 * SUM(oi.quantity) / 90, 2) AS avg_daily_sales
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('2025-06-30', '-90 days')
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY oi.product_id
    ),
    annual_sales AS (
        SELECT
            oi.product_id,
            SUM(oi.quantity) AS qty_annual
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('2025-06-30', '-365 days')
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    )
    SELECT
        p.name AS product_name,
        p.stock_qty AS current_stock,
        COALESCE(rs.avg_daily_sales, 0) AS avg_daily_sales_90d,
        CASE
            WHEN COALESCE(rs.avg_daily_sales, 0) = 0 THEN 9999
            ELSE CAST(p.stock_qty / rs.avg_daily_sales AS INTEGER)
        END AS days_of_inventory,
        ROUND(COALESCE(ans.qty_annual, 0) * p.cost_price
            / NULLIF(p.stock_qty * p.cost_price, 0), 1) AS turnover_rate,
        CAST(COALESCE(rs.avg_daily_sales, 0) * 30 AS INTEGER) AS optimal_stock_30d,
        CASE
            WHEN p.stock_qty = 0 THEN 'OUT_OF_STOCK'
            WHEN COALESCE(rs.avg_daily_sales, 0) = 0 THEN 'DEAD_STOCK'
            WHEN p.stock_qty / rs.avg_daily_sales > 60 THEN 'OVERSTOCK'
            WHEN p.stock_qty / rs.avg_daily_sales < 15 THEN 'LOW_STOCK'
            ELSE 'OPTIMAL'
        END AS stock_status
    FROM products AS p
    LEFT JOIN recent_sales AS rs ON p.id = rs.product_id
    LEFT JOIN annual_sales AS ans ON p.id = ans.product_id
    WHERE p.is_active = 1
    ORDER BY
        CASE
            WHEN p.stock_qty = 0 THEN 1
            WHEN COALESCE(rs.avg_daily_sales, 0) = 0 THEN 5
            WHEN p.stock_qty / rs.avg_daily_sales < 15 THEN 2
            WHEN p.stock_qty / rs.avg_daily_sales > 60 THEN 4
            ELSE 3
        END,
        rs.avg_daily_sales DESC;
    ```


---


### 문제 5. 고객 생애 가치(CLV) 예측 모델


각 고객의 **현재까지의 CLV**를 계산하고, 과거 구매 패턴을 기반으로
**향후 12개월 예상 CLV**를 추정하세요.
가입 기간, 구매 빈도, 평균 구매 금액, 최근성을 모두 고려합니다.

| customer_name | grade | tenure_months | total_orders | total_spent | avg_order_value | orders_per_month | recency_days | predicted_clv_12m | clv_tier |
|-------------|------|-------------|-----------|----------|---------------|----------------|-------------|-----------------|---------|


??? tip "힌트"
    - 가입 기간(월): `(julianday('2025-06-30') - julianday(created_at)) / 30`
    - 월간 구매 빈도: `주문수 / 가입 개월 수`
    - 예측 CLV = `월간 구매 빈도 * 평균 주문금액 * 12 * 감쇠율`
    - 감쇠율: 최근성 기반 — 최근 90일 내 구매 1.0, 180일 0.7, 365일 0.4, 그 외 0.1


??? success "정답"
    ```sql
    WITH customer_metrics AS (
        SELECT
            c.id AS customer_id,
            c.name AS customer_name,
            c.grade,
            ROUND((julianday('2025-06-30') - julianday(c.created_at)) / 30, 1) AS tenure_months,
            COUNT(o.id) AS total_orders,
            CAST(COALESCE(SUM(o.total_amount), 0) AS INTEGER) AS total_spent,
            ROUND(COALESCE(AVG(o.total_amount), 0), 0) AS avg_order_value,
            CAST(julianday('2025-06-30') - julianday(MAX(o.ordered_at)) AS INTEGER) AS recency_days
        FROM customers AS c
        LEFT JOIN orders AS o
            ON c.id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY c.id, c.name, c.grade, c.created_at
    ),
    with_predictions AS (
        SELECT
            customer_name,
            grade,
            CAST(tenure_months AS INTEGER) AS tenure_months,
            total_orders,
            total_spent,
            CAST(avg_order_value AS INTEGER) AS avg_order_value,
            ROUND(total_orders / NULLIF(tenure_months, 0), 2) AS orders_per_month,
            recency_days,
            CAST(
                (total_orders / NULLIF(tenure_months, 0))
                * avg_order_value
                * 12
                * CASE
                    WHEN recency_days <= 90  THEN 1.0
                    WHEN recency_days <= 180 THEN 0.7
                    WHEN recency_days <= 365 THEN 0.4
                    ELSE 0.1
                  END
            AS INTEGER) AS predicted_clv_12m
        FROM customer_metrics
        WHERE total_orders > 0
    )
    SELECT
        customer_name,
        grade,
        tenure_months,
        total_orders,
        total_spent,
        avg_order_value,
        orders_per_month,
        recency_days,
        predicted_clv_12m,
        CASE
            WHEN predicted_clv_12m >= 5000000 THEN 'Platinum'
            WHEN predicted_clv_12m >= 2000000 THEN 'Gold'
            WHEN predicted_clv_12m >= 500000  THEN 'Silver'
            ELSE 'Bronze'
        END AS clv_tier
    FROM with_predictions
    ORDER BY predicted_clv_12m DESC
    LIMIT 30;
    ```


---


### 문제 6. 뷰 설계: 실시간 상품 대시보드


다음 정보를 제공하는 **뷰(VIEW)**를 CREATE VIEW 문으로 작성하세요:
상품별 현재 가격, 30일/90일 판매량, 평균 평점, 재고 상태, 반품률, 위시리스트 수.
이 뷰 하나로 상품팀이 일상적인 모니터링을 수행할 수 있어야 합니다.

| id | name | brand | category | price | sold_30d | sold_90d | avg_rating | review_count | stock_qty | stock_status | return_rate_pct | wishlist_count |
|----|------|-------|---------|-------|---------|---------|-----------|-------------|----------|-------------|----------------|-------------|


??? tip "힌트"
    - 서브쿼리 3~4개를 `LEFT JOIN`으로 결합
    - 30일/90일 판매: `DATE('now', '-30 days')` 기준
    - 반품률: `returns 건수 / 주문 건수`
    - 재고 상태: stock_qty 기반 분류


??? success "정답"
    ```sql
    CREATE VIEW v_product_dashboard AS
    WITH sales_30d AS (
        SELECT oi.product_id, SUM(oi.quantity) AS sold_30d
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('now', '-30 days')
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    ),
    sales_90d AS (
        SELECT oi.product_id, SUM(oi.quantity) AS sold_90d
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('now', '-90 days')
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    ),
    review_agg AS (
        SELECT product_id,
               ROUND(AVG(rating), 1) AS avg_rating,
               COUNT(*) AS review_count
        FROM reviews
        GROUP BY product_id
    ),
    return_rate AS (
        SELECT
            oi.product_id,
            COUNT(DISTINCT r.id) AS return_count,
            COUNT(DISTINCT o.id) AS order_count
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        LEFT JOIN returns AS r ON o.id = r.order_id
        GROUP BY oi.product_id
    ),
    wish_cnt AS (
        SELECT product_id, COUNT(*) AS wishlist_count
        FROM wishlists
        GROUP BY product_id
    )
    SELECT
        p.id,
        p.name,
        p.brand,
        cat.name AS category,
        p.price,
        COALESCE(s30.sold_30d, 0) AS sold_30d,
        COALESCE(s90.sold_90d, 0) AS sold_90d,
        COALESCE(ra.avg_rating, 0) AS avg_rating,
        COALESCE(ra.review_count, 0) AS review_count,
        p.stock_qty,
        CASE
            WHEN p.stock_qty = 0 THEN 'OUT_OF_STOCK'
            WHEN p.stock_qty < 10 THEN 'LOW'
            WHEN p.stock_qty < 100 THEN 'NORMAL'
            ELSE 'HIGH'
        END AS stock_status,
        ROUND(100.0 * COALESCE(rr.return_count, 0)
            / NULLIF(rr.order_count, 0), 1) AS return_rate_pct,
        COALESCE(wc.wishlist_count, 0) AS wishlist_count
    FROM products AS p
    JOIN categories AS cat ON p.category_id = cat.id
    LEFT JOIN sales_30d   AS s30 ON p.id = s30.product_id
    LEFT JOIN sales_90d   AS s90 ON p.id = s90.product_id
    LEFT JOIN review_agg  AS ra  ON p.id = ra.product_id
    LEFT JOIN return_rate AS rr  ON p.id = rr.product_id
    LEFT JOIN wish_cnt    AS wc  ON p.id = wc.product_id
    WHERE p.is_active = 1
    ORDER BY COALESCE(s30.sold_30d, 0) DESC;

    -- 뷰 사용 예시
    -- SELECT * FROM v_product_dashboard WHERE stock_status = 'LOW' ORDER BY sold_30d DESC;
    ```


---


### 문제 7. 트리거 설계: 재고 부족 알림 시뮬레이션


주문이 들어올 때 재고가 **안전 재고(30일 평균 판매량 x 1.5) 이하**로 떨어지면
`inventory_transactions`에 'alert' 타입의 기록을 자동 삽입하는 **트리거**를 설계하세요.
(실제 트리거 CREATE 문 + 동작 검증 SELECT 문)

| product_id | product_name | current_stock | safety_stock | alert_needed |
|-----------|-------------|-------------|-------------|-------------|


??? tip "힌트"
    - 안전 재고 계산: 최근 30일 평균 일일 판매량 * 1.5 * 30
    - 기존 `trg_deduct_stock` 트리거 이후에 실행되어야 함
    - `AFTER INSERT ON order_items`에서 재고 확인 후 조건부 INSERT


??? success "정답"
    ```sql
    -- 1) 트리거 DDL
    CREATE TRIGGER trg_low_stock_alert AFTER INSERT ON order_items
    WHEN (
        SELECT stock_qty FROM products WHERE id = NEW.product_id
    ) < (
        SELECT COALESCE(SUM(oi.quantity), 0) * 1.5
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE oi.product_id = NEW.product_id
          AND o.ordered_at >= DATE('now', '-30 days')
          AND o.status NOT IN ('cancelled')
    )
    BEGIN
        INSERT INTO inventory_transactions (product_id, type, quantity, reference_id, notes, created_at)
        VALUES (
            NEW.product_id,
            'alert',
            0,
            NEW.order_id,
            'LOW_STOCK_ALERT: stock below safety level',
            DATETIME('now')
        );
    END;

    -- 2) 현재 재고 부족 상품 조회 (트리거 없이도 검증 가능)
    WITH daily_avg AS (
        SELECT
            oi.product_id,
            1.0 * SUM(oi.quantity) / 30 AS avg_daily
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('2025-06-30', '-30 days')
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    )
    SELECT
        p.id AS product_id,
        p.name AS product_name,
        p.stock_qty AS current_stock,
        CAST(da.avg_daily * 1.5 * 30 AS INTEGER) AS safety_stock,
        CASE
            WHEN p.stock_qty < da.avg_daily * 1.5 * 30 THEN 'YES'
            ELSE 'NO'
        END AS alert_needed
    FROM products AS p
    JOIN daily_avg AS da ON p.id = da.product_id
    WHERE p.is_active = 1
      AND p.stock_qty < da.avg_daily * 1.5 * 30
    ORDER BY (p.stock_qty - da.avg_daily * 1.5 * 30) ASC;
    ```


---


### 문제 8. 인덱스 최적화 분석


다음 느린 쿼리를 EXPLAIN QUERY PLAN으로 분석하고,
적절한 **복합 인덱스**를 설계하세요:
"2024년에 특정 카테고리의 상품을 구매한 VIP 고객의 총 매출"

| detail | scan_type | table_name | index_used |
|--------|----------|-----------|-----------|


??? tip "힌트"
    - `EXPLAIN QUERY PLAN SELECT ...`로 현재 실행 계획 확인
    - SCAN vs SEARCH 차이: SCAN은 전체 탐색, SEARCH는 인덱스 활용
    - 복합 인덱스: WHERE 조건과 JOIN 키를 결합


??? success "정답"
    ```sql
    -- 1) 원본 쿼리의 실행 계획 확인
    EXPLAIN QUERY PLAN
    SELECT
        c.name, SUM(o.total_amount) AS total_spent
    FROM customers AS c
    JOIN orders AS o ON c.id = o.customer_id
    JOIN order_items AS oi ON o.id = oi.order_id
    JOIN products AS p ON oi.product_id = p.id
    WHERE c.grade = 'VIP'
      AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
      AND o.status NOT IN ('cancelled')
      AND p.category_id = 5
    GROUP BY c.id, c.name;

    -- 2) 최적화 인덱스 추가
    -- 고객 등급 필터 + 조인키
    CREATE INDEX idx_customers_grade ON customers(grade);

    -- 주문 날짜 + 상태 + 고객 복합 인덱스 (커버링)
    CREATE INDEX idx_orders_date_status_customer
        ON orders(ordered_at, status, customer_id);

    -- 주문 아이템: 주문 → 상품 조인 최적화
    -- (이미 idx_order_items_order_product 존재)

    -- 상품: 카테고리 필터
    -- (이미 idx_products_category_id 존재)

    -- 3) 최적화 후 실행 계획 재확인
    EXPLAIN QUERY PLAN
    SELECT
        c.name, SUM(o.total_amount) AS total_spent
    FROM customers AS c
    JOIN orders AS o ON c.id = o.customer_id
    JOIN order_items AS oi ON o.id = oi.order_id
    JOIN products AS p ON oi.product_id = p.id
    WHERE c.grade = 'VIP'
      AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
      AND o.status NOT IN ('cancelled')
      AND p.category_id = 5
    GROUP BY c.id, c.name;
    ```


---


### 문제 9. 이상 거래 탐지 시스템


다음 규칙으로 **이상 거래(fraud)**를 탐지하세요:
(1) 1시간 내 3건 이상 주문, (2) 주문 금액이 고객 평균의 5배 초과,
(3) 신규 가입 24시간 내 100만원 이상 주문, (4) 동일 상품 5개 이상 단일 주문.
각 규칙에 걸린 주문을 모두 보고합니다.

| rule | order_id | customer_name | ordered_at | total_amount | detail |
|------|---------|-------------|-----------|-------------|--------|


??? tip "힌트"
    - 규칙 1: 윈도우 함수로 1시간 범위 내 주문 수 카운트
    - 규칙 2: CTE로 고객 평균 구한 뒤 개별 주문과 비교
    - 규칙 3: `julianday(ordered_at) - julianday(created_at) < 1`
    - `UNION ALL`로 4개 규칙 결과 합치기


??? success "정답"
    ```sql
    -- 규칙 1: 1시간 내 3건 이상 주문
    WITH rule1 AS (
        SELECT
            'Rapid Orders (3+ in 1hr)' AS rule,
            o.id AS order_id,
            c.name AS customer_name,
            o.ordered_at,
            o.total_amount,
            'Orders in window: ' || (
                SELECT COUNT(*)
                FROM orders o2
                WHERE o2.customer_id = o.customer_id
                  AND ABS(julianday(o2.ordered_at) - julianday(o.ordered_at)) * 24 <= 1
            ) AS detail
        FROM orders AS o
        JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled')
          AND (
              SELECT COUNT(*)
              FROM orders o2
              WHERE o2.customer_id = o.customer_id
                AND ABS(julianday(o2.ordered_at) - julianday(o.ordered_at)) * 24 <= 1
          ) >= 3
    ),
    -- 규칙 2: 고객 평균의 5배 초과
    cust_avg AS (
        SELECT customer_id, AVG(total_amount) AS avg_amount
        FROM orders WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
        HAVING COUNT(*) >= 3
    ),
    rule2 AS (
        SELECT
            'Amount > 5x Average' AS rule,
            o.id, c.name, o.ordered_at, o.total_amount,
            'Avg: ' || CAST(ca.avg_amount AS INTEGER) || ', Ratio: '
                || ROUND(o.total_amount / ca.avg_amount, 1) AS detail
        FROM orders AS o
        JOIN customers AS c ON o.customer_id = c.id
        JOIN cust_avg AS ca ON o.customer_id = ca.customer_id
        WHERE o.status NOT IN ('cancelled')
          AND o.total_amount > ca.avg_amount * 5
    ),
    -- 규칙 3: 가입 24시간 내 100만원 이상
    rule3 AS (
        SELECT
            'New User High Value' AS rule,
            o.id, c.name, o.ordered_at, o.total_amount,
            'Hours since signup: ' || CAST((julianday(o.ordered_at) - julianday(c.created_at)) * 24 AS INTEGER) AS detail
        FROM orders AS o
        JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled')
          AND (julianday(o.ordered_at) - julianday(c.created_at)) < 1
          AND o.total_amount >= 1000000
    ),
    -- 규칙 4: 단일 주문 동일 상품 5개 이상
    rule4 AS (
        SELECT
            'Bulk Single Item (5+)' AS rule,
            o.id, c.name, o.ordered_at, o.total_amount,
            p.name || ' x ' || oi.quantity AS detail
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        JOIN customers AS c ON o.customer_id = c.id
        JOIN products AS p ON oi.product_id = p.id
        WHERE oi.quantity >= 5
          AND o.status NOT IN ('cancelled')
    )
    SELECT * FROM rule1
    UNION ALL SELECT * FROM rule2
    UNION ALL SELECT * FROM rule3
    UNION ALL SELECT * FROM rule4
    ORDER BY rule, total_amount DESC;
    ```


---


### 문제 10. CS 성과 + 고객 만족도 연계 분석


CS 직원별 **민원 처리 성과**와 **처리 후 고객 만족도(재구매/리뷰 평점)**를 연계 분석하세요.
직원별 처리 건수, 평균 해결 시간, 에스컬레이션율, 보상 비용,
그리고 처리 후 30일 내 해당 고객의 재구매율과 리뷰 평점을 구합니다.

| staff_name | department | resolved_count | avg_resolve_hours | escalation_rate | total_compensation | post_repurchase_pct | post_avg_rating |
|-----------|-----------|---------------|------------------|----------------|-------------------|-------------------|----------------|


??? tip "힌트"
    - `complaints.staff_id`로 직원 연결
    - 해결 시간: `julianday(resolved_at) - julianday(created_at)` * 24
    - 에스컬레이션: `escalated = 1`인 비율
    - 재구매: 민원 해결 후 30일 내 주문 존재 여부


??? success "정답"
    ```sql
    WITH staff_perf AS (
        SELECT
            cp.staff_id,
            COUNT(*) AS resolved_count,
            ROUND(AVG((julianday(cp.resolved_at) - julianday(cp.created_at)) * 24), 1) AS avg_resolve_hours,
            ROUND(100.0 * SUM(cp.escalated) / COUNT(*), 1) AS escalation_rate,
            CAST(SUM(COALESCE(cp.compensation_amount, 0)) AS INTEGER) AS total_compensation
        FROM complaints AS cp
        WHERE cp.status IN ('resolved', 'closed')
          AND cp.staff_id IS NOT NULL
        GROUP BY cp.staff_id
    ),
    post_satisfaction AS (
        SELECT
            cp.staff_id,
            COUNT(DISTINCT cp.id) AS resolved_with_customer,
            COUNT(DISTINCT CASE
                WHEN EXISTS (
                    SELECT 1 FROM orders o
                    WHERE o.customer_id = cp.customer_id
                      AND o.ordered_at > cp.resolved_at
                      AND o.ordered_at <= DATE(cp.resolved_at, '+30 days')
                      AND o.status NOT IN ('cancelled')
                )
                THEN cp.customer_id
            END) AS repurchased_customers,
            COUNT(DISTINCT cp.customer_id) AS unique_customers
        FROM complaints AS cp
        WHERE cp.status IN ('resolved', 'closed')
          AND cp.staff_id IS NOT NULL
          AND cp.resolved_at IS NOT NULL
        GROUP BY cp.staff_id
    ),
    post_reviews AS (
        SELECT
            cp.staff_id,
            ROUND(AVG(r.rating), 2) AS post_avg_rating
        FROM complaints AS cp
        JOIN reviews AS r ON cp.customer_id = r.customer_id
            AND r.created_at > cp.resolved_at
            AND r.created_at <= DATE(cp.resolved_at, '+30 days')
        WHERE cp.status IN ('resolved', 'closed')
          AND cp.staff_id IS NOT NULL
        GROUP BY cp.staff_id
    )
    SELECT
        s.name AS staff_name,
        s.department,
        sp.resolved_count,
        sp.avg_resolve_hours,
        sp.escalation_rate,
        sp.total_compensation,
        ROUND(100.0 * ps.repurchased_customers / NULLIF(ps.unique_customers, 0), 1) AS post_repurchase_pct,
        COALESCE(pr.post_avg_rating, 0) AS post_avg_rating
    FROM staff_perf AS sp
    JOIN staff AS s ON sp.staff_id = s.id
    LEFT JOIN post_satisfaction AS ps ON sp.staff_id = ps.staff_id
    LEFT JOIN post_reviews AS pr ON sp.staff_id = pr.staff_id
    ORDER BY sp.resolved_count DESC;
    ```


---


### 문제 11. 월간 경영 보고서 (Executive Summary)


**2024년 12월 경영 보고서**를 단일 쿼리로 생성하세요. 다음 섹션을 포함합니다:
(A) 매출 요약: 총매출, MoM%, YoY%, (B) 상위 5개 상품,
(C) 고객 지표: 신규/재구매/이탈, (D) CS 요약: 총 건수/해결률/평균 해결 시간.
최종 결과는 `key`, `value` 2열의 Key-Value 형태로 출력합니다.

| key | value |
|-----|-------|
| Total Revenue | 123,456,789 |
| MoM Growth | 12.3% |
| ... | ... |


??? tip "힌트"
    - 각 섹션을 CTE로 계산 후, `UNION ALL`로 key-value 쌍으로 합치기
    - 숫자 포맷: `PRINTF('%,d', value)` 또는 `CAST(... AS TEXT)`
    - 20행 이내의 핵심 KPI만 선별


??? success "정답"
    ```sql
    WITH dec_rev AS (
        SELECT SUM(total_amount) AS rev
        FROM orders
        WHERE ordered_at >= '2024-12-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    nov_rev AS (
        SELECT SUM(total_amount) AS rev
        FROM orders
        WHERE ordered_at >= '2024-11-01' AND ordered_at < '2024-12-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    dec_2023_rev AS (
        SELECT SUM(total_amount) AS rev
        FROM orders
        WHERE ordered_at >= '2023-12-01' AND ordered_at < '2024-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    top_products AS (
        SELECT
            p.name,
            CAST(SUM(oi.quantity * oi.unit_price) AS INTEGER) AS rev,
            ROW_NUMBER() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS rn
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at >= '2024-12-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled')
        GROUP BY p.id, p.name
    ),
    customer_metrics AS (
        SELECT
            COUNT(DISTINCT CASE
                WHEN NOT EXISTS (SELECT 1 FROM orders o2 WHERE o2.customer_id = o.customer_id AND o2.ordered_at < '2024-12-01' AND o2.status NOT IN ('cancelled'))
                THEN o.customer_id END) AS new_cust,
            COUNT(DISTINCT CASE
                WHEN EXISTS (SELECT 1 FROM orders o2 WHERE o2.customer_id = o.customer_id AND o2.ordered_at < '2024-12-01' AND o2.status NOT IN ('cancelled'))
                THEN o.customer_id END) AS repeat_cust
        FROM orders AS o
        WHERE o.ordered_at >= '2024-12-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled')
    ),
    cs_metrics AS (
        SELECT
            COUNT(*) AS total_tickets,
            ROUND(100.0 * SUM(CASE WHEN status IN ('resolved','closed') THEN 1 ELSE 0 END) / COUNT(*), 1) AS resolve_rate,
            ROUND(AVG(CASE WHEN resolved_at IS NOT NULL
                THEN (julianday(resolved_at) - julianday(created_at)) * 24 END), 1) AS avg_hours
        FROM complaints
        WHERE created_at >= '2024-12-01' AND created_at < '2025-01-01'
    )
    SELECT '== [A] Sales Summary ==' AS key, '' AS value
    UNION ALL SELECT 'Total Revenue', PRINTF('%,d', CAST((SELECT rev FROM dec_rev) AS INTEGER))
    UNION ALL SELECT 'MoM Growth %', ROUND(100.0 * ((SELECT rev FROM dec_rev) - (SELECT rev FROM nov_rev)) / (SELECT rev FROM nov_rev), 1) || '%'
    UNION ALL SELECT 'YoY Growth %', ROUND(100.0 * ((SELECT rev FROM dec_rev) - (SELECT rev FROM dec_2023_rev)) / NULLIF((SELECT rev FROM dec_2023_rev), 0), 1) || '%'
    UNION ALL SELECT '== [B] Top Products ==', ''
    UNION ALL SELECT '#' || rn || ' ' || name, PRINTF('%,d', rev) FROM top_products WHERE rn <= 5
    UNION ALL SELECT '== [C] Customer Metrics ==', ''
    UNION ALL SELECT 'New Customers', CAST(new_cust AS TEXT) FROM customer_metrics
    UNION ALL SELECT 'Repeat Customers', CAST(repeat_cust AS TEXT) FROM customer_metrics
    UNION ALL SELECT '== [D] CS Summary ==', ''
    UNION ALL SELECT 'Total Tickets', CAST(total_tickets AS TEXT) FROM cs_metrics
    UNION ALL SELECT 'Resolution Rate', resolve_rate || '%' FROM cs_metrics
    UNION ALL SELECT 'Avg Resolve Time', avg_hours || ' hours' FROM cs_metrics;
    ```


---


### 문제 12. 데이터 마이그레이션 검증


가상 시나리오: `orders`의 구조가 변경되어 `order_number`의 형식이
`ORD-YYYYMMDD-NNNNN`에서 `ORD/YYYY/MM/NNNNN`으로 바뀌어야 합니다.
(1) 변환 SQL을 작성하고, (2) 변환 전후 데이터 정합성 검증 쿼리를 작성하세요.
(실제 UPDATE 없이 검증만 수행)

| order_id | old_format | new_format | date_match | sequence_match |
|---------|-----------|-----------|-----------|---------------|


??? tip "힌트"
    - 기존 형식 파싱: `SUBSTR(order_number, 5, 8)` = YYYYMMDD, `SUBSTR(order_number, 14)` = NNNNN
    - 새 형식: `'ORD/' || SUBSTR(dt, 1, 4) || '/' || SUBSTR(dt, 5, 2) || '/' || seq`
    - 검증: 변환 후 다시 역변환하여 원본과 일치하는지 확인


??? success "정답"
    ```sql
    WITH migration AS (
        SELECT
            id AS order_id,
            order_number AS old_format,
            'ORD/' ||
                SUBSTR(order_number, 5, 4) || '/' ||
                SUBSTR(order_number, 9, 2) || '/' ||
                SUBSTR(order_number, 14) AS new_format,
            -- 역변환 검증
            SUBSTR(order_number, 5, 4) AS old_year,
            SUBSTR(order_number, 9, 2) AS old_month,
            SUBSTR(order_number, 14) AS old_seq
        FROM orders
    ),
    verification AS (
        SELECT
            order_id,
            old_format,
            new_format,
            -- 새 형식에서 날짜 추출하여 원본과 비교
            CASE
                WHEN SUBSTR(new_format, 5, 4) = old_year
                 AND SUBSTR(new_format, 10, 2) = old_month
                THEN 'OK' ELSE 'MISMATCH'
            END AS date_match,
            -- 새 형식에서 시퀀스 추출하여 원본과 비교
            CASE
                WHEN SUBSTR(new_format, 13) = old_seq
                THEN 'OK' ELSE 'MISMATCH'
            END AS sequence_match
        FROM migration
    )
    -- 검증 요약
    SELECT
        COUNT(*) AS total_records,
        SUM(CASE WHEN date_match = 'OK' THEN 1 ELSE 0 END) AS date_ok,
        SUM(CASE WHEN date_match = 'MISMATCH' THEN 1 ELSE 0 END) AS date_fail,
        SUM(CASE WHEN sequence_match = 'OK' THEN 1 ELSE 0 END) AS seq_ok,
        SUM(CASE WHEN sequence_match = 'MISMATCH' THEN 1 ELSE 0 END) AS seq_fail
    FROM verification;

    -- 불일치 건 상세 (있다면)
    -- SELECT * FROM verification WHERE date_match = 'MISMATCH' OR sequence_match = 'MISMATCH' LIMIT 10;
    ```


---


### 문제 13. 전체 감사 로그 시뮬레이션


`customer_grade_history`, `point_transactions`, `inventory_transactions`를 합쳐
**통합 감사 로그(Unified Audit Log)**를 만드세요.
시간순으로 정렬하며, 각 이벤트의 영향(before/after)을 표시합니다.
2025년 6월 데이터 기준으로 최근 100건을 추출합니다.

| event_time | event_type | entity_type | entity_id | entity_name | before_value | after_value | detail |
|-----------|-----------|-----------|---------|-----------|------------|-----------|--------|


??? tip "힌트"
    - `UNION ALL`로 3개 테이블의 이벤트를 통합
    - 등급 변경: before=old_grade, after=new_grade
    - 포인트: before=balance_after-amount, after=balance_after
    - 재고: type과 quantity 표시
    - `ORDER BY event_time DESC LIMIT 100`


??? success "정답"
    ```sql
    -- 등급 변경 이벤트
    SELECT
        gh.changed_at AS event_time,
        'GRADE_CHANGE' AS event_type,
        'customer' AS entity_type,
        gh.customer_id AS entity_id,
        c.name AS entity_name,
        COALESCE(gh.old_grade, '(none)') AS before_value,
        gh.new_grade AS after_value,
        gh.reason AS detail
    FROM customer_grade_history AS gh
    JOIN customers AS c ON gh.customer_id = c.id
    WHERE gh.changed_at >= '2025-06-01' AND gh.changed_at < '2025-07-01'

    UNION ALL

    -- 포인트 이벤트
    SELECT
        pt.created_at,
        'POINT_' || UPPER(pt.type),
        'customer',
        pt.customer_id,
        c.name,
        CAST(pt.balance_after - pt.amount AS TEXT),
        CAST(pt.balance_after AS TEXT),
        pt.reason || COALESCE(' (order #' || pt.order_id || ')', '')
    FROM point_transactions AS pt
    JOIN customers AS c ON pt.customer_id = c.id
    WHERE pt.created_at >= '2025-06-01' AND pt.created_at < '2025-07-01'

    UNION ALL

    -- 재고 이벤트
    SELECT
        it.created_at,
        'INVENTORY_' || UPPER(it.type),
        'product',
        it.product_id,
        p.name,
        '',
        CASE WHEN it.quantity > 0 THEN '+' ELSE '' END || CAST(it.quantity AS TEXT),
        COALESCE(it.notes, '') || COALESCE(' (ref #' || it.reference_id || ')', '')
    FROM inventory_transactions AS it
    JOIN products AS p ON it.product_id = p.id
    WHERE it.created_at >= '2025-06-01' AND it.created_at < '2025-07-01'

    ORDER BY event_time DESC
    LIMIT 100;
    ```


---


### 문제 14. 상품 후계자 체인 분석 (Successor Chain)


`products.successor_id`를 따라가며 **상품 세대 체인(generation chain)**을 구성하세요.
재귀 CTE로 1세대 → 2세대 → ... → 현역 상품까지의 가격 변화와
세대별 매출 추이를 분석합니다.

| generation | product_name | brand | price | total_revenue | is_current | chain_path |
|-----------|-------------|-------|-------|-------------|-----------|-----------|


??? tip "힌트"
    - `products.successor_id`가 NULL이면 현역 또는 단종(discontinued_at 확인)
    - 재귀의 시작: `successor_id IS NULL AND discontinued_at IS NULL` (현역 상품)이 아닌, `WHERE NOT EXISTS (SELECT 1 FROM products p2 WHERE p2.successor_id = p.id)` (1세대: 전임자 없는 상품)
    - 재귀 진행: `p.successor_id = chain.id`로 다음 세대 탐색


??? success "정답"
    ```sql
    WITH RECURSIVE chain AS (
        -- 1세대: 자신을 가리키는 전임자가 없는 상품 (체인의 시작)
        SELECT
            p.id,
            p.name,
            p.brand,
            p.price,
            p.successor_id,
            p.is_active,
            p.discontinued_at,
            1 AS generation,
            p.name AS chain_path
        FROM products AS p
        WHERE NOT EXISTS (
            SELECT 1 FROM products p2 WHERE p2.successor_id = p.id
        )
        AND p.successor_id IS NOT NULL  -- 후계자가 있는 시작점만

        UNION ALL

        -- 다음 세대
        SELECT
            p.id,
            p.name,
            p.brand,
            p.price,
            p.successor_id,
            p.is_active,
            p.discontinued_at,
            ch.generation + 1,
            ch.chain_path || ' → ' || p.name
        FROM products AS p
        JOIN chain AS ch ON ch.successor_id = p.id
        WHERE ch.generation < 10  -- 무한 루프 방지
    )
    SELECT
        c.generation,
        c.name AS product_name,
        c.brand,
        CAST(c.price AS INTEGER) AS price,
        COALESCE(CAST(SUM(oi.quantity * oi.unit_price) AS INTEGER), 0) AS total_revenue,
        CASE WHEN c.is_active = 1 AND c.discontinued_at IS NULL THEN 'YES' ELSE 'NO' END AS is_current,
        c.chain_path
    FROM chain AS c
    LEFT JOIN order_items AS oi ON c.id = oi.product_id
    LEFT JOIN orders AS o ON oi.order_id = o.id
        AND o.status NOT IN ('cancelled')
    GROUP BY c.id, c.generation, c.name, c.brand, c.price,
             c.is_active, c.discontinued_at, c.chain_path
    ORDER BY c.chain_path, c.generation;
    ```


---


### 문제 15. 종합 건강 체크: 데이터베이스 무결성 감사


전체 데이터베이스의 **참조 무결성과 비즈니스 규칙 위반**을 한 번에 검사하세요.
다음 10가지 규칙을 모두 검증합니다:

1. 배송완료일 < 출하일인 배송 건
2. 주문일 < 고객 가입일인 주문 건
3. 리뷰 작성일 < 주문일인 리뷰 건
4. 자기 자신이 상사인 직원 (manager_id = id)
5. 포인트 잔액이 음수인 고객
6. 존재하지 않는 parent_id를 참조하는 카테고리
7. 취소된 주문에 배송완료 기록이 있는 건
8. 할인금액이 주문금액보다 큰 주문
9. 활성 상품이지만 재고가 음수인 상품
10. 만료일이 시작일보다 빠른 쿠폰

| rule_no | rule_description | violation_count | sample_ids |
|--------|-----------------|----------------|-----------|


??? tip "힌트"
    - 각 규칙을 `SELECT 규칙번호, 설명, COUNT(*), GROUP_CONCAT(id)` 형태로 작성
    - `UNION ALL`로 10개 합치기
    - `WHERE violation_count > 0`으로 실제 위반만 표시


??? success "정답"
    ```sql
    SELECT 1 AS rule_no,
           'Delivery before shipment' AS rule_description,
           COUNT(*) AS violation_count,
           COALESCE(GROUP_CONCAT(id, ','), '') AS sample_ids
    FROM shipping
    WHERE delivered_at IS NOT NULL AND shipped_at IS NOT NULL AND delivered_at < shipped_at

    UNION ALL
    SELECT 2, 'Order before customer signup',
           COUNT(*), COALESCE(GROUP_CONCAT(o.id, ','), '')
    FROM orders AS o
    JOIN customers AS c ON o.customer_id = c.id
    WHERE o.ordered_at < c.created_at

    UNION ALL
    SELECT 3, 'Review before order date',
           COUNT(*), COALESCE(GROUP_CONCAT(r.id, ','), '')
    FROM reviews AS r
    JOIN orders AS o ON r.order_id = o.id
    WHERE r.created_at < o.ordered_at

    UNION ALL
    SELECT 4, 'Self-referencing manager',
           COUNT(*), COALESCE(GROUP_CONCAT(id, ','), '')
    FROM staff
    WHERE manager_id = id

    UNION ALL
    SELECT 5, 'Negative point balance',
           COUNT(*), COALESCE(GROUP_CONCAT(id, ','), '')
    FROM customers
    WHERE point_balance < 0

    UNION ALL
    SELECT 6, 'Orphan category parent_id',
           COUNT(*), COALESCE(GROUP_CONCAT(c1.id, ','), '')
    FROM categories AS c1
    WHERE c1.parent_id IS NOT NULL
      AND NOT EXISTS (SELECT 1 FROM categories c2 WHERE c2.id = c1.parent_id)

    UNION ALL
    SELECT 7, 'Cancelled order with delivery',
           COUNT(*), COALESCE(GROUP_CONCAT(o.id, ','), '')
    FROM orders AS o
    JOIN shipping AS s ON o.id = s.order_id
    WHERE o.status = 'cancelled' AND s.status = 'delivered'

    UNION ALL
    SELECT 8, 'Discount exceeds order amount',
           COUNT(*), COALESCE(GROUP_CONCAT(id, ','), '')
    FROM orders
    WHERE discount_amount > total_amount + shipping_fee

    UNION ALL
    SELECT 9, 'Active product with negative stock',
           COUNT(*), COALESCE(GROUP_CONCAT(id, ','), '')
    FROM products
    WHERE is_active = 1 AND stock_qty < 0

    UNION ALL
    SELECT 10, 'Coupon expired before start',
           COUNT(*), COALESCE(GROUP_CONCAT(id, ','), '')
    FROM coupons
    WHERE expired_at < started_at

    ORDER BY rule_no;
    ```
