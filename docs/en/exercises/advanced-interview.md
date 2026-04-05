# Advanced Exercise: SQL Interview Prep

Practice SQL patterns commonly asked in real technical interviews using this database. 10 problems.

---

### 1. Top-N per Group

Find the top revenue product in each category. (Only one in case of a tie)

**Hint:** Assign within-group rankings with `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)`, then filter with `WHERE rn = 1`.

??? success "Answer"
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

### 2. Consecutive Growth Periods

Find periods where monthly revenue increased for 3 consecutive months.

**Hint:** Use `LAG(revenue, 1)` and `LAG(revenue, 2)` to get the previous 2 months' revenue, then compare: current > previous > two months ago.

??? success "Answer"
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

### 3. Running Total

Calculate the monthly revenue and cumulative revenue for 2024.

**Hint:** Calculate the running total with `SUM(monthly_revenue) OVER (ORDER BY month)`. `SUM(SUM(...))` is a pattern that nests a window function inside an aggregate.

??? success "Answer"
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

### 4. Moving Average

Calculate the 3-month moving average revenue.

**Hint:** Use `AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` to average 3 rows including the current one.

??? success "Answer"
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

### 5. Gap Analysis (Missing Data)

Find dates in 2024 with no orders.

**Hint:** Generate all dates in 2024 with `WITH RECURSIVE`, then `LEFT JOIN` with actual order dates and find dates where the result is `NULL`.

??? success "Answer"
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

### 6. Percentile

Calculate the 10th, 25th, 50th (median), 75th, and 90th percentiles of customer purchase amounts.

**Hint:** Create percentile groups with `NTILE(100) OVER (ORDER BY total_spent)`, then extract each point's value with `MAX(CASE WHEN percentile = N ...)`.

??? success "Answer"
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

### 7. Year-over-Year Rank Changes

Calculate the yearly revenue ranking by category and show the rank change compared to the previous year.

**Hint:** Assign yearly rankings with `RANK() OVER (PARTITION BY year ORDER BY revenue DESC)`, then get the previous year's rank with `LAG(rank) OVER (PARTITION BY category ORDER BY year)` and calculate the difference.

??? success "Answer"
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

### 8. Funnel Analysis

Analyze the customer journey funnel: Signup -> First Order -> Write Review -> Repeat Purchase. Calculate the conversion rate at each stage.

**Hint:** Get the unique customer count for each stage using scalar subqueries, then calculate the conversion rate with `100.0 * next_stage / previous_stage`.

??? success "Answer"
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

### 9. Self-Referencing Hierarchy Depth Traversal

Find the maximum depth of the category hierarchy and the number of categories at each depth. Use a recursive CTE.

**Hint:** In `WITH RECURSIVE`, start with `parent_id IS NULL` as the root (depth=0), then recursively traverse children with `c.parent_id = tree.id`.

??? success "Answer"
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

### 10. Same Product Repurchase Interval

Calculate the average repurchase interval (in days) for customers who purchased the same product 2 or more times.

**Hint:** Use `LAG(ordered_at) OVER (PARTITION BY customer_id, product_id ORDER BY ordered_at)` to get the previous order date for the same customer-product pair, then calculate the `JULIANDAY` difference.

??? success "Answer"
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
