# SQL interview preparation

!!! info "Tables"
    `orders` — Orders (status, amount, date)  
    `order_items` — Order items (qty, unit price)  
    `products` — Products (name, price, stock, brand)  
    `categories` — Categories (parent-child hierarchy)  
    `customers` — Customers (grade, points, channel)  
    `reviews` — Reviews (rating, content)  
    `product_views` — View log (customer, product, date)  
    `calendar` — Calendar (weekday, holiday)  
    `staff` — Staff (dept, role, manager)  

!!! abstract "Concepts"
    DENSE_RANK, N days in a row, Median, Session Analysis, Rating by category, MoM growth rate, Percentile, Calculate working days, Organization Chart Recursion

This is a SQL pattern frequently asked in interviews at FAANG (Amazon, Google, Meta) and domestic IT companies (Kakao, Coupang, Naver).
Each question has a **Question Frequency** tag, and we recommend that you practice solving them within the time limit.

---

### Problem 1. Second highest selling product ★★★

Find the product with the **second highest total sales** among all products.
Use `DENSE_RANK` because there may be multiple products with the same sales as the product with the highest sales.

> **Presentation Frequency**: ★★★ (Very High) — Amazon, LeetCode #176 variant

| product_name | category | total_revenue | revenue_rank |
|-------------|----------|-------------|-------------|
| ... | ... | ... | 2 |

??? tip "Hint"
    - `DENSE_RANK() OVER (ORDER BY total_revenue DESC)`: Ranking where ties are allowed
    - Sum up sales by product in CTE → Ranking → `WHERE rank = 2`

??? success "Answer"
    ```sql
    WITH product_revenue AS (
        SELECT
            p.id,
            p.name AS product_name,
            cat.name AS category,
            SUM(oi.quantity * oi.unit_price) AS total_revenue
        FROM order_items AS oi
        JOIN orders     AS o   ON oi.order_id   = o.id
        JOIN products   AS p   ON oi.product_id = p.id
        JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY p.id, p.name, cat.name
    ),
    ranked AS (
        SELECT *,
            DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
        FROM product_revenue
    )
    SELECT product_name, category,
           CAST(total_revenue AS INTEGER) AS total_revenue,
           revenue_rank
    FROM ranked
    WHERE revenue_rank = 2;
    ```

---

### Problem 2. Running Total ★★★

Find the **monthly sales** and **year-to-date (YTD)** for 2024.

> **Question frequency**: ★★★ (very high) — Google, Meta frequently appears

| month | monthly_revenue | ytd_revenue |
|-------|----------------|------------|
| 2024-01 | ... | ... |

??? tip "Hint"
    - `SUM(monthly_revenue) OVER (ORDER BY month)` = running total
    - The basic frame of the window function is `UNBOUNDED PRECEDING ~ CURRENT ROW`

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        CAST(SUM(total_amount) AS INTEGER) AS monthly_revenue,
        CAST(SUM(SUM(total_amount)) OVER (ORDER BY SUBSTR(ordered_at, 1, 7)) AS INTEGER) AS ytd_revenue
    FROM orders
    WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```

---

### Problem 3. Identifying duplicate data ★★★

**Find cases where the same customer ordered the same product on the same day (suspected duplicates).
Only the most recent order is marked as valid and the rest are flagged as duplicates.

> **Question frequency**: ★★★ (very high) — LeetCode #196 variant, Kakao

| order_id | customer_name | product_name | ordered_at | is_duplicate |
|---------|-------------|-------------|-----------|-------------|

??? tip "Hint"
    - `ROW_NUMBER() OVER (PARTITION BY customer_id, product_id, DATE(ordered_at) ORDER BY ordered_at DESC)`
    - Valid if `rn = 1`, duplicate if `rn > 1`

??? success "Answer"
    ```sql
    WITH order_detail AS (
        SELECT
            o.id AS order_id,
            o.customer_id,
            oi.product_id,
            o.ordered_at,
            ROW_NUMBER() OVER (
                PARTITION BY o.customer_id, oi.product_id, DATE(o.ordered_at)
                ORDER BY o.ordered_at DESC
            ) AS rn
        FROM orders AS o
        JOIN order_items AS oi ON o.id = oi.order_id
        WHERE o.status NOT IN ('cancelled')
    )
    SELECT
        od.order_id,
        c.name AS customer_name,
        p.name AS product_name,
        od.ordered_at,
        CASE WHEN od.rn > 1 THEN 'Y' ELSE 'N' END AS is_duplicate
    FROM order_detail AS od
    JOIN customers AS c ON od.customer_id = c.id
    JOIN products  AS p ON od.product_id  = p.id
    WHERE od.rn <= 2
    ORDER BY od.customer_id, od.product_id, DATE(od.ordered_at), od.rn;
    ```

---

### Problem 4. Finding the median ★★☆

Find the **median** of the order amount for each customer.
SQLite does not have a `MEDIAN` function, so it is implemented as a window function.

> **Question frequency**: ★★☆ — Google, Amazon

| customer_name | order_count | median_amount |
|-------------|------------|-------------|
| ... | ... | ... |

??? tip "Hint"
    - Ranking as `ROW_NUMBER()`, total number of cases as `COUNT(*) OVER()`
    - Median = (n+1)/2nd if the total number of cases is odd, average of n/2 and n/2+1 if the total number of cases is even.
    - Extract center row with `WHERE rn IN (cnt/2, cnt/2+1, (cnt+1)/2)`

??? success "Answer"
    ```sql
    WITH numbered AS (
        SELECT
            customer_id,
            total_amount,
            ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY total_amount) AS rn,
            COUNT(*) OVER (PARTITION BY customer_id) AS cnt
        FROM orders
        WHERE status NOT IN ('cancelled')
    ),
    median_rows AS (
        SELECT
            customer_id,
            ROUND(AVG(total_amount), 0) AS median_amount,
            MAX(cnt) AS order_count
        FROM numbered
        WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
        GROUP BY customer_id
    )
    SELECT
        c.name AS customer_name,
        m.order_count,
        m.median_amount
    FROM median_rows AS m
    JOIN customers AS c ON m.customer_id = c.id
    WHERE m.order_count >= 5
    ORDER BY m.median_amount DESC
    LIMIT 20;
    ```

---

### Problem 5. Login for N consecutive days (Islands) ★★★

Consider `product_views` as your login log, and find customers **active for more than 3 consecutive days**.

> **Question frequency**: ★★★ (very high) — Meta, Coupang, LeetCode #180 variant

| customer_name | streak_days | streak_start | streak_end |
|-------------|-----------|------------|----------|

??? tip "Hint"
    - `DATE(viewed_at)` Detect groups of consecutive dates after removing duplicates
    - `DATE(viewed_at, '-' || (ROW_NUMBER()-1) || ' days')` → Same value if in the same group
    - `HAVING COUNT(*) >= 3`

??? success "Answer"
    ```sql
    WITH active_days AS (
        SELECT DISTINCT
            customer_id,
            DATE(viewed_at) AS active_date
        FROM product_views
    ),
    grouped AS (
        SELECT
            customer_id,
            active_date,
            DATE(active_date, '-' || (ROW_NUMBER() OVER (
                PARTITION BY customer_id ORDER BY active_date
            ) - 1) || ' days') AS grp
        FROM active_days
    ),
    streaks AS (
        SELECT
            customer_id,
            COUNT(*) AS streak_days,
            MIN(active_date) AS streak_start,
            MAX(active_date) AS streak_end
        FROM grouped
        GROUP BY customer_id, grp
        HAVING COUNT(*) >= 3
    )
    SELECT
        c.name AS customer_name,
        s.streak_days,
        s.streak_start,
        s.streak_end
    FROM streaks AS s
    JOIN customers AS c ON s.customer_id = c.id
    ORDER BY s.streak_days DESC, s.streak_start
    LIMIT 20;
    ```

---

### Problem 6. Top-N by category (ranking within group) ★★★

Extract the **two products with the highest review ratings** from each category.
Only products with 10 or more reviews are eligible. In case of a tie, the product with the most reviews will take precedence.

> **Question frequency**: ★★★ (very high) — Amazon, Naver, Kakao

| category | product_name | avg_rating | review_count | rank |
|----------|-------------|-----------|-------------|------|

??? tip "Hint"
    - Filter number of reviews by `HAVING COUNT(*) >= 10`
    - `ROW_NUMBER() OVER (PARTITION BY category ORDER BY avg_rating DESC, review_count DESC)`
    - `WHERE rn <= 2`

??? success "Answer"
    ```sql
    WITH product_ratings AS (
        SELECT
            cat.name AS category,
            p.name   AS product_name,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(*)                AS review_count
        FROM reviews AS r
        JOIN products   AS p   ON r.product_id  = p.id
        JOIN categories AS cat ON p.category_id = cat.id
        GROUP BY cat.name, p.id, p.name
        HAVING COUNT(*) >= 10
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (
                PARTITION BY category
                ORDER BY avg_rating DESC, review_count DESC
            ) AS rn
        FROM product_ratings
    )
    SELECT category, product_name, avg_rating, review_count, rn AS rank
    FROM ranked
    WHERE rn <= 2
    ORDER BY category, rn;
    ```

---

### Problem 7. Year-on-year (YoY) growth rate ★★★

Find the year-over-year growth rate (YoY %) of **quarterly sales**.
It covers data from 2023 to 2025.

> **Frequency**: ★★★ (Very High) -- Google, Meta, Coupang

| year | quarter | revenue | prev_year_revenue | yoy_growth_pct |
|------|---------|---------|------------------|---------------|

??? tip "Hint"
    - Refer to sales in the same quarter of the previous year as `LAG(revenue, 4) OVER (ORDER BY year, quarter)` — since quarters are 1 to 4, 4 transitions are the same quarter of the previous year.
    - or `LAG(revenue, 1) OVER (PARTITION BY quarter ORDER BY year)`

??? success "Answer"
    ```sql
    WITH quarterly AS (
        SELECT
            CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER) AS year,
            CASE
                WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) <= 3 THEN 1
                WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) <= 6 THEN 2
                WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) <= 9 THEN 3
                ELSE 4
            END AS quarter,
            SUM(total_amount) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled')
          AND ordered_at >= '2023-01-01'
        GROUP BY 1, 2
    )
    SELECT
        year,
        quarter,
        CAST(revenue AS INTEGER) AS revenue,
        CAST(LAG(revenue) OVER (PARTITION BY quarter ORDER BY year) AS INTEGER) AS prev_year_revenue,
        ROUND(100.0 * (revenue - LAG(revenue) OVER (PARTITION BY quarter ORDER BY year))
            / LAG(revenue) OVER (PARTITION BY quarter ORDER BY year), 1) AS yoy_growth_pct
    FROM quarterly
    ORDER BY year, quarter;
    ```

---

### Problem 8. Moving Average ★★☆

Find the **7-day moving average of daily sales** for 2024.
The moving average is the average of the previous 7 days including the current day.

> **Question frequency**: ★★☆ — Google, Naver

| order_date | daily_revenue | ma_7d |
|-----------|-------------|------|

??? tip "Hint"
    - `AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`
    - LEFT JOIN with `calendar` to include days without orders as 0

??? success "Answer"
    ```sql
    WITH daily AS (
        SELECT
            cal.date_key AS order_date,
            COALESCE(SUM(o.total_amount), 0) AS daily_revenue
        FROM calendar AS cal
        LEFT JOIN orders AS o
            ON DATE(o.ordered_at) = cal.date_key
           AND o.status NOT IN ('cancelled')
        WHERE cal.date_key BETWEEN '2024-01-01' AND '2024-12-31'
        GROUP BY cal.date_key
    )
    SELECT
        order_date,
        CAST(daily_revenue AS INTEGER) AS daily_revenue,
        CAST(AVG(daily_revenue) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS INTEGER) AS ma_7d
    FROM daily
    ORDER BY order_date;
    ```

---

### Problem 9. Percentile ★★☆

Find the values ​​where the total purchase amount for each customer falls within the **top 10%, 25%, 50% (median), 75%, and 90%** boundaries.

> **Question frequency**: ★★☆ — Amazon, Google

| percentile | threshold_amount |
|-----------|----------------|
| 10 | ... |
| 25 | ... |

??? tip "Hint"
    - Assign percentile group to `NTILE(100) OVER (ORDER BY total_spent)`
    - Each percentile boundary value: MAX value in `WHERE percentile_group IN (10, 25, 50, 75, 90)`

??? success "Answer"
    ```sql
    WITH customer_spent AS (
        SELECT
            customer_id,
            SUM(total_amount) AS total_spent
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ),
    with_percentile AS (
        SELECT
            total_spent,
            NTILE(100) OVER (ORDER BY total_spent) AS pctl
        FROM customer_spent
    )
    SELECT
        pctl AS percentile,
        CAST(MAX(total_spent) AS INTEGER) AS threshold_amount
    FROM with_percentile
    WHERE pctl IN (10, 25, 50, 75, 90)
    GROUP BY pctl
    ORDER BY pctl;
    ```

---

### Problem 10. Change rate compared to previous day + 7-day moving change rate ★★☆

**Percent change from previous day (DoD %)** for the number of daily orders in December 2024
Find the **change rate (WoW %) compared to 7 days ago** at the same time.

> **Question frequency**: ★★☆ — Meta, Coupang

| order_date | order_count | prev_day | dod_pct | prev_week | wow_pct |
|-----------|------------|---------|--------|----------|--------|

??? tip "Hint"
    - `LAG(order_count, 1)` = the previous day, `LAG(order_count, 7)` = 7 days ago
    - Rate of change = `(current_day - previous) / previous * 100`
    - `calendar` Includes days missed due to LEFT JOIN

??? success "Answer"
    ```sql
    WITH daily AS (
        SELECT
            cal.date_key AS order_date,
            COALESCE(COUNT(o.id), 0) AS order_count
        FROM calendar AS cal
        LEFT JOIN orders AS o
            ON DATE(o.ordered_at) = cal.date_key
           AND o.status NOT IN ('cancelled')
        WHERE cal.date_key BETWEEN '2024-12-01' AND '2024-12-31'
        GROUP BY cal.date_key
    )
    SELECT
        order_date,
        order_count,
        LAG(order_count, 1) OVER (ORDER BY order_date) AS prev_day,
        ROUND(100.0 * (order_count - LAG(order_count, 1) OVER (ORDER BY order_date))
            / NULLIF(LAG(order_count, 1) OVER (ORDER BY order_date), 0), 1) AS dod_pct,
        LAG(order_count, 7) OVER (ORDER BY order_date) AS prev_week,
        ROUND(100.0 * (order_count - LAG(order_count, 7) OVER (ORDER BY order_date))
            / NULLIF(LAG(order_count, 7) OVER (ORDER BY order_date), 0), 1) AS wow_pct
    FROM daily
    ORDER BY order_date;
    ```

---

### Problem 11. Recursive CTE: Organizational Tree ★★★

Print the **full organizational hierarchy** using `manager_id` in the `staff` table.
Include depth, supervisor name, and full path (CEO > ... > yourself).

> **Question frequency**: ★★★ (very high) — Amazon, Kakao, Naver

| name | department | role | depth | manager_name | path |
|------|-----------|------|-------|-------------|------|
| CEO Name | management | admin | 0 | NULL | CEO Name |
| ... | ... | ... | 1 | CEO Name | CEO Name > ... |

??? tip "Hint"
    - Recursive CTE: `WHERE manager_id IS NULL` is the anchor (root)
    - Join with `s.manager_id = tree.id` in the recursive part
    - Accumulate paths with `path || ' > ' || s.name`

??? success "Answer"
    ```sql
    WITH RECURSIVE org_tree AS (
        -- Anchor: top-level manager (manager_id IS NULL)
        SELECT
            s.id,
            s.name,
            s.department,
            s.role,
            0 AS depth,
            CAST(NULL AS TEXT) AS manager_name,
            s.name AS path
        FROM staff AS s
        WHERE s.manager_id IS NULL

        UNION ALL

        -- Recursive: subordinate employees
        SELECT
            s.id,
            s.name,
            s.department,
            s.role,
            t.depth + 1,
            t.name AS manager_name,
            t.path || ' > ' || s.name
        FROM staff AS s
        JOIN org_tree AS t ON s.manager_id = t.id
    )
    SELECT name, department, role, depth, manager_name, path
    FROM org_tree
    ORDER BY path;
    ```

---

### Problem 12. Recursive CTE: Creating date sequences ★★☆

**Generate all dates in December 2024 as recursive CTEs**,
Find the number of orders and sales for each date. (Days without orders are also displayed as 0)

> **Question frequency**: ★★☆ — Google (in an environment without a calendar table)

| dt | order_count | revenue |
|----|-----------|---------|
| 2024-12-01 | ... | ... |

??? tip "Hint"
    - Anchor: `SELECT '2024-12-01' AS dt`
    - Recursion: `SELECT DATE(dt, '+1 day') FROM dates WHERE dt < '2024-12-31'`
    - Combine order data with `LEFT JOIN orders`

??? success "Answer"
    ```sql
    WITH RECURSIVE dates AS (
        SELECT '2024-12-01' AS dt
        UNION ALL
        SELECT DATE(dt, '+1 day')
        FROM dates
        WHERE dt < '2024-12-31'
    )
    SELECT
        d.dt,
        COUNT(o.id) AS order_count,
        COALESCE(CAST(SUM(o.total_amount) AS INTEGER), 0) AS revenue
    FROM dates AS d
    LEFT JOIN orders AS o
        ON DATE(o.ordered_at) = d.dt
       AND o.status NOT IN ('cancelled')
    GROUP BY d.dt
    ORDER BY d.dt;
    ```

---

### Problem 13. Cohort analysis (repurchase by subscription month) ★★★

Based on the customer's **subscription month (cohort)**, find the percentage of customers purchasing from 0 to 3 months after subscription.
This applies to customers signing up in 2024.

> **Question frequency**: ★★★ (very high) — Meta, Coupang, Naver

| cohort | size | m0_pct | m1_pct | m2_pct | m3_pct |
|--------|------|-------|-------|-------|-------|

??? tip "Hint"
    - Cohort: `SUBSTR(created_at, 1, 7)`
    - Month Offset: Convert `(julianday(order_month-01) - julianday(signup_month-01)) / 30` to integer
    - `COUNT(DISTINCT CASE WHEN offset = N THEN customer_id END)` / cohort size

??? success "Answer"
    ```sql
    WITH cohort AS (
        SELECT
            id AS customer_id,
            SUBSTR(created_at, 1, 7) AS cohort_month
        FROM customers
        WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
    ),
    order_month AS (
        SELECT DISTINCT
            co.customer_id,
            co.cohort_month,
            CAST(
                (julianday(SUBSTR(o.ordered_at, 1, 7) || '-01')
               - julianday(co.cohort_month || '-01')) / 30
            AS INTEGER) AS month_offset
        FROM cohort AS co
        JOIN orders AS o ON co.customer_id = o.customer_id
        WHERE o.status NOT IN ('cancelled')
    )
    SELECT
        c.cohort_month AS cohort,
        COUNT(DISTINCT c.customer_id) AS size,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN om.month_offset = 0 THEN om.customer_id END)
            / COUNT(DISTINCT c.customer_id), 1) AS m0_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN om.month_offset = 1 THEN om.customer_id END)
            / COUNT(DISTINCT c.customer_id), 1) AS m1_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN om.month_offset = 2 THEN om.customer_id END)
            / COUNT(DISTINCT c.customer_id), 1) AS m2_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN om.month_offset = 3 THEN om.customer_id END)
            / COUNT(DISTINCT c.customer_id), 1) AS m3_pct
    FROM cohort AS c
    LEFT JOIN order_month AS om ON c.customer_id = om.customer_id
        AND c.cohort_month = om.cohort_month
    GROUP BY c.cohort_month
    ORDER BY c.cohort_month;
    ```

---

### Problem 14. Category hierarchy aggregation (Recursive + GROUP BY) ★★☆

Find the **total sales by category** from the `categories` tree.
Roll up all sales from the lower category (small/medium) to the upper category (large).

> **Question frequency**: ★★☆ — Amazon, Kakao

| top_category | sub_category_count | product_count | total_revenue |
|-------------|-------------------|-------------|-------------|

??? tip "Hint"
    - Find the root (depth=0) ancestor of each category with recursive CTE
    - After recursive search, base on root `GROUP BY`

??? success "Answer"
    ```sql
    WITH RECURSIVE cat_tree AS (
        SELECT id, id AS root_id, name AS root_name, depth
        FROM categories
        WHERE parent_id IS NULL

        UNION ALL

        SELECT c.id, ct.root_id, ct.root_name, c.depth
        FROM categories AS c
        JOIN cat_tree AS ct ON c.parent_id = ct.id
    )
    SELECT
        ct.root_name AS top_category,
        COUNT(DISTINCT CASE WHEN ct.depth > 0 THEN ct.id END) AS sub_category_count,
        COUNT(DISTINCT p.id) AS product_count,
        COALESCE(CAST(SUM(oi.quantity * oi.unit_price) AS INTEGER), 0) AS total_revenue
    FROM cat_tree AS ct
    LEFT JOIN products AS p ON p.category_id = ct.id
    LEFT JOIN order_items AS oi ON oi.product_id = p.id
    LEFT JOIN orders AS o ON oi.order_id = o.id
        AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    WHERE ct.root_id = ct.root_id
    GROUP BY ct.root_id, ct.root_name
    ORDER BY total_revenue DESC;
    ```

---

### Problem 15. Self-Join: Employee with higher salary (number of sales processed) than boss ★★★

Find the number of orders processed by each employee, and find **the employee who processed more orders than his/her boss**.
(based on orders.staff_id)

> **Question frequency**: ★★★ (very high) — LeetCode #181 variant, Kakao

| staff_name | department | handled_orders | manager_name | manager_orders |
|-----------|-----------|---------------|-------------|---------------|

??? tip "Hint"
    - `staff AS s JOIN staff AS m ON s.manager_id = m.id` (Self-Join)
    - Number of orders for each employee: counted as `orders.staff_id`
    - `WHERE s_count > m_count`

??? success "Answer"
    ```sql
    WITH staff_orders AS (
        SELECT
            s.id,
            s.name,
            s.department,
            s.manager_id,
            COUNT(o.id) AS handled_orders
        FROM staff AS s
        LEFT JOIN orders AS o ON s.id = o.staff_id
        GROUP BY s.id, s.name, s.department, s.manager_id
    )
    SELECT
        emp.name       AS staff_name,
        emp.department,
        emp.handled_orders,
        mgr.name       AS manager_name,
        mgr.handled_orders AS manager_orders
    FROM staff_orders AS emp
    JOIN staff_orders AS mgr ON emp.manager_id = mgr.id
    WHERE emp.handled_orders > mgr.handled_orders
    ORDER BY emp.handled_orders DESC;
    ```

---

### Problem 16. Multi-level analysis: Measuring discount effect ★★☆

Compare customers who used the coupon with those who did not and find:
(1) Average order amount by group, (2) Repurchase rate, (3) Average review rating.

> **Question frequency**: ★★☆ — Coupang, Naver

| segment | customer_count | avg_order_value | repeat_rate_pct | avg_rating |
|---------|--------------|----------------|----------------|-----------|

??? tip "Hint"
    - Coupon usage: Classify segments by presence of `coupon_usage`
    - Repurchase rate: Customers who ordered more than 2 items / All customers
    - Aggregate each of the three tables (orders, coupon_usage, reviews) into CTE and then merge them.

??? success "Answer"
    ```sql
    WITH coupon_customers AS (
        SELECT DISTINCT customer_id FROM coupon_usage
    ),
    customer_segment AS (
        SELECT
            c.id AS customer_id,
            CASE WHEN cc.customer_id IS NOT NULL THEN 'Coupon User' ELSE 'Non-Coupon' END AS segment
        FROM customers AS c
        LEFT JOIN coupon_customers AS cc ON c.id = cc.customer_id
        WHERE c.is_active = 1
    ),
    order_stats AS (
        SELECT
            cs.segment,
            cs.customer_id,
            COUNT(o.id) AS order_count,
            AVG(o.total_amount) AS avg_order_value
        FROM customer_segment AS cs
        LEFT JOIN orders AS o ON cs.customer_id = o.customer_id
            AND o.status NOT IN ('cancelled')
        GROUP BY cs.segment, cs.customer_id
    ),
    review_stats AS (
        SELECT
            cs.segment,
            ROUND(AVG(r.rating), 2) AS avg_rating
        FROM customer_segment AS cs
        JOIN reviews AS r ON cs.customer_id = r.customer_id
        GROUP BY cs.segment
    )
    SELECT
        os.segment,
        COUNT(DISTINCT os.customer_id) AS customer_count,
        ROUND(AVG(os.avg_order_value), 0) AS avg_order_value,
        ROUND(100.0 * SUM(CASE WHEN os.order_count >= 2 THEN 1 ELSE 0 END)
            / COUNT(DISTINCT os.customer_id), 1) AS repeat_rate_pct,
        rs.avg_rating
    FROM order_stats AS os
    LEFT JOIN review_stats AS rs ON os.segment = rs.segment
    GROUP BY os.segment, rs.avg_rating
    ORDER BY os.segment;
    ```

---

### Problem 17. Data quality check: NULL/outlier detection ★★☆

Report the following data quality issues with one query:
(1) Order amount is 0 or less, (2) Delivery date < Order date, (3) Outside review rating range, (4) Order on a future date.

> **Question frequency**: ★★☆ — Amazon (Data Engineer), Kakao

| issue_type | table_name | record_count | sample_ids |
|-----------|-----------|-------------|-----------|

??? tip "Hint"
    - Combine the results of each quality check with `UNION ALL`
    - List sample ID as `GROUP_CONCAT(id, ',')`
    - Future date: `ordered_at > '2025-12-31'`

??? success "Answer"
    ```sql
    SELECT 'Zero/Negative Amount' AS issue_type,
           'orders' AS table_name,
           COUNT(*) AS record_count,
           GROUP_CONCAT(id, ',') AS sample_ids
    FROM orders
    WHERE total_amount <= 0

    UNION ALL

    SELECT 'Delivery Before Shipment',
           'shipping',
           COUNT(*),
           GROUP_CONCAT(id, ',')
    FROM shipping
    WHERE delivered_at IS NOT NULL
      AND shipped_at IS NOT NULL
      AND delivered_at < shipped_at

    UNION ALL

    SELECT 'Rating Out of Range',
           'reviews',
           COUNT(*),
           GROUP_CONCAT(id, ',')
    FROM reviews
    WHERE rating < 1 OR rating > 5

    UNION ALL

    SELECT 'Future Order Date',
           'orders',
           COUNT(*),
           GROUP_CONCAT(id, ',')
    FROM orders
    WHERE ordered_at > DATE('now', '+1 day');
    ```

---

### Problem 18. Time series anomaly detection: 3-sigma rule ★☆☆

Find outlier days that fall outside the **average +/- 3 standard deviations** of your daily sales.

> **Question frequency**: ★☆☆ — Google (Data Science)

| order_date | daily_revenue | avg_revenue | stddev | z_score |
|-----------|-------------|-----------|-------|--------|

??? tip "Hint"
    - Standard deviation: Manual calculation as it is not directly supported by SQLite
    - `SQRT(AVG(x*x) - AVG(x)*AVG(x))` = population standard deviation
    - If Z-score = `(value - mean) / stddev`, `ABS(z) > 3`, it is an outlier.

??? success "Answer"
    ```sql
    WITH daily AS (
        SELECT
            DATE(ordered_at) AS order_date,
            SUM(total_amount) AS daily_revenue
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY DATE(ordered_at)
    ),
    stats AS (
        SELECT
            AVG(daily_revenue) AS avg_rev,
            SQRT(AVG(daily_revenue * daily_revenue) - AVG(daily_revenue) * AVG(daily_revenue)) AS stddev_rev
        FROM daily
    )
    SELECT
        d.order_date,
        CAST(d.daily_revenue AS INTEGER) AS daily_revenue,
        CAST(s.avg_rev AS INTEGER) AS avg_revenue,
        CAST(s.stddev_rev AS INTEGER) AS stddev,
        ROUND((d.daily_revenue - s.avg_rev) / s.stddev_rev, 2) AS z_score
    FROM daily AS d
    CROSS JOIN stats AS s
    WHERE ABS((d.daily_revenue - s.avg_rev) / s.stddev_rev) > 3
    ORDER BY ABS((d.daily_revenue - s.avg_rev) / s.stddev_rev) DESC;
    ```

---

### Problem 19. Complex analysis: RFM segmentation ★★★

Segment your customers by **RFM(Recency, Frequency, Monetary)**.
Divide each indicator into a scale of 1 to 5, and calculate the number of customers and average sales for each segment.

> **Question frequency**: ★★★ (very high) — Coupang, Naver, Amazon

| rfm_segment | r_score | f_score | m_score | customer_count | avg_monetary |
|------------|--------|--------|--------|--------------|------------|
| Champions | 5 | 5 | 5 | ... | ... |

??? tip "Hint"
    - Recency: Days since last order → `NTILE(5)` (the more recent, the higher the score)
    - Frequency: Number of orders → `NTILE(5)`
    - Monetary: Total purchase amount → `NTILE(5)`
    - Segment classification: R+F+M sum is 13~15=Champions, 10~12=Loyal, 7~9=Potential, 4~6=AtRisk, 3=Lost

??? success "Answer"
    ```sql
    WITH rfm_raw AS (
        SELECT
            customer_id,
            CAST(julianday('2025-06-30') - julianday(MAX(ordered_at)) AS INTEGER) AS recency,
            COUNT(*) AS frequency,
            CAST(SUM(total_amount) AS INTEGER) AS monetary
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ),
    rfm_scored AS (
        SELECT
            customer_id,
            recency, frequency, monetary,
            NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,
            NTILE(5) OVER (ORDER BY frequency ASC)  AS f_score,
            NTILE(5) OVER (ORDER BY monetary ASC)   AS m_score
        FROM rfm_raw
    ),
    rfm_segmented AS (
        SELECT *,
            r_score + f_score + m_score AS rfm_total,
            CASE
                WHEN r_score + f_score + m_score >= 13 THEN 'Champions'
                WHEN r_score + f_score + m_score >= 10 THEN 'Loyal'
                WHEN r_score + f_score + m_score >= 7  THEN 'Potential'
                WHEN r_score + f_score + m_score >= 4  THEN 'At Risk'
                ELSE 'Lost'
            END AS rfm_segment
        FROM rfm_scored
    )
    SELECT
        rfm_segment,
        ROUND(AVG(r_score), 1) AS r_score,
        ROUND(AVG(f_score), 1) AS f_score,
        ROUND(AVG(m_score), 1) AS m_score,
        COUNT(*) AS customer_count,
        CAST(AVG(monetary) AS INTEGER) AS avg_monetary
    FROM rfm_segmented
    GROUP BY rfm_segment
    ORDER BY AVG(rfm_total) DESC;
    ```

---

### Problem 20. Comprehensive scenario: Marketing campaign effectiveness analysis ★★★

Break down the following by promotions in 2024:
(1) Number of participating customers, (2) Sales during promotion period vs. sales during the previous same period (incremental effect),
(3) Repurchase rate for 30 days after promotion ends; (4) Customer acquisition cost (total discount/number of new customers).

> **Question frequency**: ★★★ (very high) — Coupang, Naver, Meta (comprehensive questions)

| promo_name | promo_type | participants | promo_revenue | pre_revenue | lift_pct | post_repurchase_pct | cac |
|-----------|-----------|------------|-------------|-----------|---------|-------------------|-----|

??? tip "Hint"
    - Set period to `started_at`/`ended_at` in `promotions`
    - Previous same period: `DATE(started_at, '-' || (julianday(ended_at)-julianday(started_at)) || ' days')`
    - New Customer: Customer who placed their first order during the promotion period.
    - Separated into CTE levels 4-5

??? success "Answer"
    ```sql
    WITH promo_periods AS (
        SELECT
            pr.id AS promo_id,
            pr.name AS promo_name,
            pr.type AS promo_type,
            pr.started_at,
            pr.ended_at,
            CAST(julianday(pr.ended_at) - julianday(pr.started_at) AS INTEGER) AS duration_days
        FROM promotions AS pr
        WHERE pr.started_at >= '2024-01-01' AND pr.started_at < '2025-01-01'
    ),
    promo_orders AS (
        SELECT
            pp.promo_id, pp.promo_name, pp.promo_type,
            pp.started_at, pp.ended_at, pp.duration_days,
            o.id AS order_id,
            o.customer_id,
            o.total_amount,
            o.discount_amount
        FROM promo_periods AS pp
        JOIN orders AS o
            ON o.ordered_at BETWEEN pp.started_at AND pp.ended_at
           AND o.status NOT IN ('cancelled')
    ),
    pre_period_revenue AS (
        SELECT
            pp.promo_id,
            COALESCE(SUM(o.total_amount), 0) AS pre_revenue
        FROM promo_periods AS pp
        LEFT JOIN orders AS o
            ON o.ordered_at BETWEEN DATE(pp.started_at, '-' || pp.duration_days || ' days')
                                AND DATE(pp.started_at, '-1 day')
           AND o.status NOT IN ('cancelled')
        GROUP BY pp.promo_id
    ),
    post_repurchase AS (
        SELECT
            po.promo_id,
            COUNT(DISTINCT CASE
                WHEN EXISTS (
                    SELECT 1 FROM orders o2
                    WHERE o2.customer_id = po.customer_id
                      AND o2.ordered_at > po.ended_at
                      AND o2.ordered_at <= DATE(po.ended_at, '+30 days')
                      AND o2.status NOT IN ('cancelled')
                )
                THEN po.customer_id
            END) AS repurchase_customers,
            COUNT(DISTINCT po.customer_id) AS total_customers
        FROM promo_orders AS po
        GROUP BY po.promo_id
    )
    SELECT
        po.promo_name,
        po.promo_type,
        COUNT(DISTINCT po.customer_id) AS participants,
        CAST(SUM(po.total_amount) AS INTEGER) AS promo_revenue,
        CAST(pr.pre_revenue AS INTEGER) AS pre_revenue,
        ROUND(100.0 * (SUM(po.total_amount) - pr.pre_revenue)
            / NULLIF(pr.pre_revenue, 0), 1) AS lift_pct,
        ROUND(100.0 * rp.repurchase_customers / NULLIF(rp.total_customers, 0), 1) AS post_repurchase_pct,
        CAST(SUM(po.discount_amount) / NULLIF(
            COUNT(DISTINCT CASE
                WHEN NOT EXISTS (
                    SELECT 1 FROM orders o3
                    WHERE o3.customer_id = po.customer_id
                      AND o3.ordered_at < po.started_at
                      AND o3.status NOT IN ('cancelled')
                )
                THEN po.customer_id
            END), 0) AS INTEGER) AS cac
    FROM promo_orders AS po
    JOIN pre_period_revenue AS pr ON po.promo_id = pr.promo_id
    JOIN post_repurchase AS rp ON po.promo_id = rp.promo_id
    GROUP BY po.promo_id, po.promo_name, po.promo_type,
             pr.pre_revenue, rp.repurchase_customers, rp.total_customers
    ORDER BY promo_revenue DESC;
    ```
