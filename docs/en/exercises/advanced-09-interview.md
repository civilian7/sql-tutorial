# SQL Interview Preparation

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `categories` — Categories (parent-child hierarchy)  

    `reviews` — Reviews (rating, content)  

    `customers` — Customers (grade, points, channel)  



!!! abstract "Concepts"

    `ROW_NUMBER`, `LAG`, `Running Total`, `Moving Average`, `Recursive CTE`, `NTILE`, `Funnel`



### 1. Top-N per Group


Find the #1 product by revenue in each category. (One per tie)


**Hint 1:** Use `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)`
to rank within groups, then filter `WHERE rn = 1`.



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


    **Result** (top 7 of 40 rows)

    | category | product | revenue |
    |---|---|---|
    | Gaming Laptop | Razer Blade 18 Black | 1,179,690,100.00 |
    | NVIDIA | ASUS Dual RTX 4060 Ti Black | 901,407,600.00 |
    | AMD | MSI Radeon RX 7900 XTX GAMING X White | 602,487,200.00 |
    | 2-in-1 | Lenovo ThinkPad X1 2in1 Silver | 582,223,200.00 |
    | Intel | Intel Core Ultra 5 245KF | 563,595,600.00 |
    | General Laptop | ASUS ExpertBook B5 [Special Limited E... | 555,152,000.00 |
    | Gaming Monitor | Samsung Odyssey G5 27 Black | 538,902,000.00 |


---


### 2. Consecutive Growth Periods


Find periods where monthly revenue increased for 3 consecutive months.


**Hint 1:** Use `LAG(revenue, 1)` and `LAG(revenue, 2)` to get previous 2 months,
then compare current > prev1 > prev2.



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


    **Result** (top 7 of 22 rows)

    | month | revenue | prev_1 | prev_2 |
    |---|---|---|---|
    | 2016-04 | 16,878,372.00 | 14,806,662.00 | 13,115,835.00 |
    | 2016-05 | 31,432,968.00 | 16,878,372.00 | 14,806,662.00 |
    | 2016-10 | 38,989,248.00 | 32,257,785.00 | 19,122,587.00 |
    | 2018-01 | 85,442,344.00 | 83,561,937.00 | 52,363,290.00 |
    | 2018-09 | 134,594,321.00 | 85,713,577.00 | 40,611,909.00 |
    | 2018-12 | 167,642,638.00 | 93,642,089.00 | 63,988,837.00 |
    | 2019-01 | 228,770,158.00 | 167,642,638.00 | 93,642,089.00 |


---


### 3. Running Total


Calculate monthly revenue and cumulative revenue for 2024.


**Hint 1:** Use `SUM(monthly_revenue) OVER (ORDER BY month)` for running total.



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


    **Result** (top 7 of 12 rows)

    | month | monthly_revenue | cumulative_revenue |
    |---|---|---|
    | 2024-01 | 301,075,320.00 | 301,075,320.00 |
    | 2024-02 | 426,177,449.00 | 727,252,769.00 |
    | 2024-03 | 536,322,767.00 | 1,263,575,536.00 |
    | 2024-04 | 470,154,081.00 | 1,733,729,617.00 |
    | 2024-05 | 459,724,596.00 | 2,193,454,213.00 |
    | 2024-06 | 377,040,302.00 | 2,570,494,515.00 |
    | 2024-07 | 363,944,597.00 | 2,934,439,112.00 |


---


### 4. Moving Average


Calculate a 3-month moving average of revenue.


**Hint 1:** `AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`



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


    **Result** (top 7 of 120 rows)

    | month | revenue | moving_avg_3m |
    |---|---|---|
    | 2016-01 | 15,816,169.00 | 15,816,169.00 |
    | 2016-02 | 13,115,835.00 | 14,466,002.00 |
    | 2016-03 | 14,806,662.00 | 14,579,555.00 |
    | 2016-04 | 16,878,372.00 | 14,933,623.00 |
    | 2016-05 | 31,432,968.00 | 21,039,334.00 |
    | 2016-06 | 26,381,091.00 | 24,897,477.00 |
    | 2016-07 | 30,436,884.00 | 29,416,981.00 |


---


### 5. Gap Analysis (Missing Data)


Find dates in 2024 with no orders.


**Hint 1:** Generate all 2024 dates with `WITH RECURSIVE`,
then `LEFT JOIN` with actual order dates and find `NULL` rows.



??? success "Answer"
    ```sql
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


Find the 10th, 25th, 50th (median), 75th, and 90th percentiles of customer total spend.


**Hint 1:** Create percentile groups with `NTILE(100) OVER (ORDER BY total_spent)`,
extract values with `MAX(CASE WHEN percentile = N ...)`.



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


    **Result** (1 rows)

    | p10 | p25 | p50_median | p75 | p90 |
    |---|---|---|---|---|
    | 180,500.00 | 1,183,200.00 | 4,654,232.00 | 13,607,591.00 | 31,606,150.00 |


---


### 7. Yearly Rank Changes


Calculate yearly revenue rank by category and show year-over-year rank changes.


**Hint 1:** Use `RANK() OVER (PARTITION BY year ORDER BY revenue DESC)` for yearly rank,
`LAG(rank) OVER (PARTITION BY category ORDER BY year)` for previous year rank.



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


    **Result** (top 7 of 148 rows)

    | year | category | revenue | rank | prev_rank | rank_change |
    |---|---|---|---|---|---|
    | 2022 | Gaming Laptop | 832,586,500.00 | 1 | NULL | NULL |
    | 2022 | Gaming Monitor | 372,536,900.00 | 2 | NULL | NULL |
    | 2022 | General Laptop | 368,304,500.00 | 3 | NULL | NULL |
    | 2022 | AMD | 360,526,000.00 | 4 | NULL | NULL |
    | 2022 | NVIDIA | 331,064,700.00 | 5 | NULL | NULL |
    | 2022 | AMD Socket | 257,637,700.00 | 6 | NULL | NULL |
    | 2022 | Intel | 217,901,700.00 | 7 | NULL | NULL |


---


### 8. Funnel Analysis


Analyze the customer journey funnel: signup -> first order -> write review -> repeat purchase.
Calculate conversion rates between each step.


**Hint 1:** Calculate unique customer count per step with scalar subqueries,
then `100.0 * next_step / prev_step` for conversion rates.



??? success "Answer"
    ```sql
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


    **Result** (1 rows)

    | step1_signup | step2_first_order | cvr_1_2 | step3_review | cvr_2_3 | step4_repeat | cvr_2_4 |
    |---|---|---|---|---|---|---|
    | 5230 | 2809 | 53.70 | 1899 | 67.60 | 2319 | 82.60 |


---


### 9. Self-Reference Hierarchy Depth Exploration


Find the maximum depth and category count per depth level. Use a recursive CTE.


**Hint 1:** Start recursive CTE from `parent_id IS NULL` (depth=0),
traverse children with `c.parent_id = tree.id`.



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


    **Result** (2 rows)

    | depth | category_count | categories |
    |---|---|---|
    | 0 | 18 | Desktop PC, Laptop, Monitor, CPU, Mot... |
    | 1 | 35 | Barebone, Custom Build, Pre-built, 2-... |


---


### 10. Same Product Repurchase Interval


Calculate the average repurchase interval (days) for customers who bought the same product 2+ times.


**Hint 1:** Use `LAG(ordered_at) OVER (PARTITION BY customer_id, product_id ORDER BY ordered_at)`
to get previous order date for same customer-product, then calculate JULIANDAY difference.



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


    **Result** (1 rows)

    | avg_repurchase_days | min_days | max_days | repurchase_count |
    |---|---|---|---|
    | 370.30 | 0 | 3240 | 22,778 |


---
