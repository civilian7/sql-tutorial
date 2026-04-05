# 고급 연습: SQL 면접 대비

실제 기술 면접에서 출제되는 SQL 패턴을 이 데이터베이스로 연습합니다. 10문제입니다.

---

### 1. Top-N per Group

각 카테고리에서 매출 1위 상품을 구하세요. (동률 시 하나만)

??? success "정답"
    ```sql
    WITH ranked AS (
        SELECT
            cat.name AS category,
            p.name AS product,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue,
            ROW_NUMBER() OVER (PARTITION BY cat.id ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS rn
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        INNER JOIN products p ON oi.product_id = p.id
        INNER JOIN categories cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY cat.id, cat.name, p.id, p.name
    )
    SELECT category, product, revenue
    FROM ranked
    WHERE rn = 1
    ORDER BY revenue DESC;
    ```

---

### 2. 연속 증가 구간

월별 매출이 3개월 연속 증가한 구간을 찾으세요.

??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS month,
            SUM(total_amount) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    ),
    with_lag AS (
        SELECT
            month, revenue,
            LAG(revenue, 1) OVER (ORDER BY month) AS prev_1,
            LAG(revenue, 2) OVER (ORDER BY month) AS prev_2
        FROM monthly
    )
    SELECT month, revenue, prev_1, prev_2
    FROM with_lag
    WHERE revenue > prev_1 AND prev_1 > prev_2
    ORDER BY month;
    ```

---

### 3. 누적 합계 (Running Total)

2024년 월별 매출과 누적 매출을 구하세요.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        ROUND(SUM(total_amount), 0) AS monthly_revenue,
        ROUND(SUM(SUM(total_amount)) OVER (ORDER BY SUBSTR(ordered_at, 1, 7)), 0) AS cumulative_revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```

---

### 4. 이동 평균 (Moving Average)

3개월 이동 평균 매출을 구하세요.

??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        month,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 0) AS moving_avg_3m
    FROM monthly
    ORDER BY month;
    ```

---

### 5. 갭 분석 (Missing Data)

2024년에 주문이 없는 날짜를 찾으세요.

??? success "정답"
    ```sql
    -- 2024년 모든 날짜 생성 (재귀 CTE)
    WITH RECURSIVE all_dates AS (
        SELECT '2024-01-01' AS dt
        UNION ALL
        SELECT DATE(dt, '+1 day')
        FROM all_dates
        WHERE dt < '2024-12-31'
    ),
    order_dates AS (
        SELECT DISTINCT SUBSTR(ordered_at, 1, 10) AS dt
        FROM orders
        WHERE ordered_at LIKE '2024%'
    )
    SELECT ad.dt AS missing_date
    FROM all_dates ad
    LEFT JOIN order_dates od ON ad.dt = od.dt
    WHERE od.dt IS NULL
    ORDER BY ad.dt;
    ```

---

### 6. 백분위수 (Percentile)

고객 구매 금액의 상위 10%, 25%, 50%(중앙값), 75%, 90% 지점을 구하세요.

??? success "정답"
    ```sql
    WITH customer_spend AS (
        SELECT
            customer_id,
            SUM(total_amount) AS total_spent
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ),
    ranked AS (
        SELECT
            total_spent,
            NTILE(100) OVER (ORDER BY total_spent) AS percentile
        FROM customer_spend
    )
    SELECT
        MAX(CASE WHEN percentile = 10 THEN total_spent END) AS p10,
        MAX(CASE WHEN percentile = 25 THEN total_spent END) AS p25,
        MAX(CASE WHEN percentile = 50 THEN total_spent END) AS p50_median,
        MAX(CASE WHEN percentile = 75 THEN total_spent END) AS p75,
        MAX(CASE WHEN percentile = 90 THEN total_spent END) AS p90
    FROM ranked;
    ```

---

### 7. 연도별 순위 변동

카테고리별 연도별 매출 순위를 구하고, 전년 대비 순위 변동을 표시하세요.

??? success "정답"
    ```sql
    WITH yearly_category AS (
        SELECT
            SUBSTR(o.ordered_at, 1, 4) AS year,
            cat.name AS category,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        INNER JOIN products p ON oi.product_id = p.id
        INNER JOIN categories cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY SUBSTR(o.ordered_at, 1, 4), cat.name
    ),
    with_rank AS (
        SELECT *,
            RANK() OVER (PARTITION BY year ORDER BY revenue DESC) AS rank
        FROM yearly_category
    )
    SELECT
        wr.year, wr.category, wr.revenue, wr.rank,
        LAG(wr.rank) OVER (PARTITION BY wr.category ORDER BY wr.year) AS prev_rank,
        LAG(wr.rank) OVER (PARTITION BY wr.category ORDER BY wr.year) - wr.rank AS rank_change
    FROM with_rank wr
    WHERE wr.year >= '2022'
    ORDER BY wr.year, wr.rank;
    ```

---

### 8. Funnel 분석 (퍼널)

고객 여정 퍼널을 분석하세요: 가입 → 첫 주문 → 리뷰 작성 → 재구매. 각 단계의 전환율을 구하세요.

??? success "정답"
    ```sql
    SELECT
        (SELECT COUNT(*) FROM customers) AS total_signups,
        (SELECT COUNT(DISTINCT customer_id) FROM orders WHERE status NOT IN ('cancelled')) AS made_order,
        ROUND(100.0 * (SELECT COUNT(DISTINCT customer_id) FROM orders WHERE status NOT IN ('cancelled'))
            / (SELECT COUNT(*) FROM customers), 1) AS order_rate,
        (SELECT COUNT(DISTINCT customer_id) FROM reviews) AS wrote_review,
        ROUND(100.0 * (SELECT COUNT(DISTINCT customer_id) FROM reviews)
            / (SELECT COUNT(DISTINCT customer_id) FROM orders WHERE status NOT IN ('cancelled')), 1) AS review_rate,
        (SELECT COUNT(DISTINCT customer_id) FROM orders WHERE status NOT IN ('cancelled')
         GROUP BY customer_id HAVING COUNT(*) >= 2) AS repeat_buyers;
    ```

    ```sql
    -- 더 정확한 퍼널 (CTE 사용)
    WITH funnel AS (
        SELECT
            (SELECT COUNT(*) FROM customers) AS step1_signup,
            (SELECT COUNT(DISTINCT customer_id) FROM orders
             WHERE status NOT IN ('cancelled')) AS step2_first_order,
            (SELECT COUNT(DISTINCT customer_id) FROM reviews) AS step3_review,
            (SELECT COUNT(*) FROM (
                SELECT customer_id FROM orders
                WHERE status NOT IN ('cancelled')
                GROUP BY customer_id HAVING COUNT(*) >= 2
            )) AS step4_repeat
    )
    SELECT
        step1_signup,
        step2_first_order,
        ROUND(100.0 * step2_first_order / step1_signup, 1) AS cvr_1_2,
        step3_review,
        ROUND(100.0 * step3_review / step2_first_order, 1) AS cvr_2_3,
        step4_repeat,
        ROUND(100.0 * step4_repeat / step2_first_order, 1) AS cvr_2_4
    FROM funnel;
    ```

---

### 9. 자기 참조 계층 깊이 탐색

카테고리 계층의 최대 깊이와 각 깊이별 카테고리 수를 구하세요. 재귀 CTE를 사용하세요.

??? success "정답"
    ```sql
    WITH RECURSIVE tree AS (
        SELECT id, name, parent_id, 0 AS depth
        FROM categories
        WHERE parent_id IS NULL
        UNION ALL
        SELECT c.id, c.name, c.parent_id, t.depth + 1
        FROM categories c
        INNER JOIN tree t ON c.parent_id = t.id
    )
    SELECT
        depth,
        COUNT(*) AS category_count,
        GROUP_CONCAT(name, ', ') AS categories
    FROM tree
    GROUP BY depth
    ORDER BY depth;
    ```

---

### 10. 동일 상품 재구매 간격

같은 상품을 2회 이상 구매한 고객의 평균 재구매 간격(일)을 구하세요.

??? success "정답"
    ```sql
    WITH repeat_purchases AS (
        SELECT
            o.customer_id,
            oi.product_id,
            o.ordered_at,
            LAG(o.ordered_at) OVER (
                PARTITION BY o.customer_id, oi.product_id
                ORDER BY o.ordered_at
            ) AS prev_order_date
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
    )
    SELECT
        ROUND(AVG(JULIANDAY(ordered_at) - JULIANDAY(prev_order_date)), 1) AS avg_repurchase_days,
        MIN(CAST(JULIANDAY(ordered_at) - JULIANDAY(prev_order_date) AS INTEGER)) AS min_days,
        MAX(CAST(JULIANDAY(ordered_at) - JULIANDAY(prev_order_date) AS INTEGER)) AS max_days,
        COUNT(*) AS repurchase_count
    FROM repeat_purchases
    WHERE prev_order_date IS NOT NULL;
    ```
