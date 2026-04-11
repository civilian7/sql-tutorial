# Sales Analysis

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `orders` — Order<br>
    `order_items` — Order Details<br>
    `products` — Product<br>
    `categories` — Category<br>
    `customers` — Customer<br>
    `payments` — Payment

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    CTE<br>
    Window functions<br>
    Multiple JOIN<br>
    Aggregation Functions Comprehensive — Sales by Month/Quarter/Category<br>
    Growth rate<br>
    Cumulative sales<br>
    cohort

</div>

This is a business sales analysis problem that comprehensively utilizes CTE, window functions, multiple JOINs, and aggregate functions.
Cancellation (`cancelled`) and return (`returned`, `return_requested`) orders are excluded unless specifically specified.

---


### Problem 1. Monthly sales trend (last 3 years)

Find monthly sales, number of orders, and average order value from 2022 to 2024.


??? tip "Hint"
    - Extract year-month with `SUBSTR(ordered_at, 1, 7)`
    - `SUM(total_amount)`, `COUNT(*)`, `AVG(total_amount)`

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7)   AS year_month,
        COUNT(*)                   AS order_count,
        ROUND(SUM(total_amount))   AS revenue,
        ROUND(AVG(total_amount))   AS avg_order_value
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
      AND ordered_at >= '2022-01-01'
      AND ordered_at < '2025-01-01'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY year_month;
    ```

    | year_month | order_count | revenue | avg_order_value |
    |---|---|---|---|
    | 2022-01 | 320 | 198000000 | 618750 |
    | 2022-02 | 285 | 175000000 | 614035 |
    | ... | ... | ... | ... |


---


### Problem 2. Proportion of sales by category

Find the sales of each major category and its proportion (%) compared to the total in 2024.


??? tip "Hint"
    - `categories.depth = 0` is the main category
    - Subcategory → Middle category → Major category Path: JOIN `categories` self-reference twice
    - Or use a subquery to find the top category with depth=0

??? success "Answer"
    ```sql
    WITH category_revenue AS (
        SELECT
            COALESCE(top_cat.name, mid_cat.name, cat.name) AS top_category,
            SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        LEFT JOIN categories AS mid_cat ON cat.parent_id = mid_cat.id
        LEFT JOIN categories AS top_cat ON mid_cat.parent_id = top_cat.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY COALESCE(top_cat.name, mid_cat.name, cat.name)
    )
    SELECT
        top_category,
        ROUND(revenue) AS revenue,
        ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS revenue_pct
    FROM category_revenue
    ORDER BY revenue DESC;
    ```

    | top_category | revenue | revenue_pct |
    |---|---|---|
    | Computer | 5200000000 | 45.2 |
    | Peripherals | 3100000000 | 26.9 |
    | ... | ... | ... |


---


### Problem 3. Top 20 customer sales rankings

Display information about the top 20 customers by total purchase amount for all time periods.
Includes customer name, level, number of orders, total purchase amount, and rank.


??? tip "Hint"
    - Use `RANK()` or `ROW_NUMBER()` window functions
    - `customers` + `orders` JOIN

??? success "Answer"
    ```sql
    SELECT
        RANK() OVER (ORDER BY SUM(o.total_amount) DESC) AS ranking,
        c.name          AS customer_name,
        c.grade,
        COUNT(*)        AS order_count,
        ROUND(SUM(o.total_amount)) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 20;
    ```

    | ranking | customer_name | grade | order_count | total_spent |
    |---|---|---|---|---|
    | 1 | Kim Minsu | VIP | 45 | 52000000 |
    | 2 | Lee Seoyeon | VIP | 38 | 48000000 |
    | ... | ... | ... | ... | ... |


---


### Problem 4. Sales pattern by day of the week

Find the average number of orders and average sales by day of the week (Mon-Sun) from all order data.
Find out which days of the week have the highest sales.


??? tip "Hint"
    - SQLite: `strftime('%w', ordered_at)` → 0 (Sun)~6 (Sat)
    - Convert day name using CASE statement
    - First, calculate daily sales and then average them for each day of the week.

??? success "Answer"
    ```sql
    WITH daily_stats AS (
        SELECT
            DATE(ordered_at) AS order_date,
            CAST(strftime('%w', ordered_at) AS INTEGER) AS dow,
            COUNT(*)               AS order_count,
            SUM(total_amount)      AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY DATE(ordered_at)
    )
    SELECT
        CASE dow
            WHEN 0 THEN 'Sunday'
            WHEN 1 THEN 'Monday'
            WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday'
            WHEN 4 THEN 'Thursday'
            WHEN 5 THEN 'Friday'
            WHEN 6 THEN 'Saturday'
        END AS day_of_week,
        ROUND(AVG(order_count)) AS avg_daily_orders,
        ROUND(AVG(revenue))     AS avg_daily_revenue
    FROM daily_stats
    GROUP BY dow
    ORDER BY dow;
    ```

    | day_of_week | avg_daily_orders | avg_daily_revenue |
    |---|---|---|
    | Sunday | 12 | 7500000 |
    | Monday | 15 | 9200000 |
    | ... | ... | ... |


---


### Problem 5. Quarterly sales and growth rate compared to the previous quarter

Find quarterly sales from 2022 to 2024 and growth rate (%) compared to the previous quarter.


??? tip "Hint"
    - Branch: `(CAST(SUBSTR(ordered_at,6,2) AS INTEGER) + 2) / 3`
    - Refer to the previous quarter’s sales using the `LAG(revenue, 1)` window function.
    - Growth rate = (current quarter - previous quarter) / previous quarter * 100

??? success "Answer"
    ```sql
    WITH quarterly AS (
        SELECT
            SUBSTR(ordered_at, 1, 4) AS year,
            'Q' || ((CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3) AS quarter,
            SUBSTR(ordered_at, 1, 4) || '-Q' || ((CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3) AS yq,
            ROUND(SUM(total_amount)) AS revenue,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2022-01-01' AND ordered_at < '2025-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 4),
                 (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3
    )
    SELECT
        yq,
        revenue,
        order_count,
        LAG(revenue, 1) OVER (ORDER BY yq) AS prev_quarter_revenue,
        ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY yq))
            / LAG(revenue, 1) OVER (ORDER BY yq), 1) AS qoq_growth_pct
    FROM quarterly
    ORDER BY yq;
    ```

    | yq | revenue | order_count | prev_quarter_revenue | qoq_growth_pct |
    |---|---|---|---|---|
    | 2022-Q1 | 580000000 | 920 | NULL | NULL |
    | 2022-Q2 | 550000000 | 870 | 580000000 | -5.2 |
    | 2022-Q3 | 490000000 | 780 | 550000000 | -10.9 |
    | 2022-Q4 | 680000000 | 1050 | 490000000 | 38.8 |
    | ... | ... | ... | ... | ... |


---


### Problem 6. Trend in sales proportion by payment method

Find the sales share (%) of each payment method (card, bank_transfer, kakao_pay, etc.) by month in 2024.


??? tip "Hint"
    - Classify payment method as `payments.method`
    - Total monthly sales with window function `SUM(revenue) OVER (PARTITION BY year_month)`
    - Proportion = Sales by payment method / Total monthly sales * 100

??? success "Answer"
    ```sql
    WITH monthly_method AS (
        SELECT
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            pm.method,
            ROUND(SUM(pm.amount)) AS revenue
        FROM payments AS pm
        INNER JOIN orders AS o ON pm.order_id = o.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
          AND pm.status = 'paid'
        GROUP BY SUBSTR(o.ordered_at, 1, 7), pm.method
    )
    SELECT
        year_month,
        method,
        revenue,
        ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY year_month), 1) AS method_pct
    FROM monthly_method
    ORDER BY year_month, revenue DESC;
    ```

    | year_month | method | revenue | method_pct |
    |---|---|---|---|
    | 2024-01 | card | 650000000 | 62.5 |
    | 2024-01 | kakao_pay | 180000000 | 17.3 |
    | 2024-01 | bank_transfer | 120000000 | 11.5 |
    | ... | ... | ... | ... |


---


### Problem 7. Top 3 products by category (Top-N per Group)

Select the top three sales products in each major category in 2024.


??? tip "Hint"
    - Count product sales by category in CTE
    - `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)` Ranking
    - `WHERE rn <= 3` filter in outer query

??? success "Answer"
    ```sql
    WITH product_sales AS (
        SELECT
            COALESCE(top_cat.name, mid_cat.name, cat.name) AS top_category,
            p.name AS product_name,
            SUM(oi.quantity)                        AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        LEFT JOIN categories AS mid_cat ON cat.parent_id = mid_cat.id
        LEFT JOIN categories AS top_cat ON mid_cat.parent_id = top_cat.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY COALESCE(top_cat.name, mid_cat.name, cat.name), p.name
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY top_category ORDER BY revenue DESC) AS rn
        FROM product_sales
    )
    SELECT top_category, rn AS rank, product_name, units_sold, revenue
    FROM ranked
    WHERE rn <= 3
    ORDER BY top_category, rn;
    ```

    | top_category | rank | product_name | units_sold | revenue |
    |---|---|---|---|---|
    | Computer | 1 | (Laptop A) | 120 | 360000000 |
    | Computer | 2 | (Desktop B) | 85 | 255000000 |
    | Computer | 3 | (Laptop C) | 78 | 234000000 |
    | Peripherals | 1 | ... | ... | ... |


---


### Problem 8. Year-on-year (YoY) sales growth rate

Find the sales for each month in 2023 and 2024 and the growth rate (%) compared to the same month of the previous year.


??? tip "Hint"
    - `LAG(revenue, 12)` — See sales 12 months ago
    - Or, after separating year + month from CTE, SELF JOIN the previous year of the same month

??? success "Answer"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 4) AS year,
            SUBSTR(ordered_at, 6, 2) AS month,
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount)) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2022-01-01' AND ordered_at < '2025-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        cur.year_month,
        cur.revenue                AS current_revenue,
        prev.revenue               AS prev_year_revenue,
        ROUND(100.0 * (cur.revenue - prev.revenue) / prev.revenue, 1) AS yoy_growth_pct
    FROM monthly AS cur
    INNER JOIN monthly AS prev
        ON cur.month = prev.month
        AND CAST(cur.year AS INTEGER) = CAST(prev.year AS INTEGER) + 1
    WHERE cur.year IN ('2023', '2024')
    ORDER BY cur.year_month;
    ```

    | year_month | current_revenue | prev_year_revenue | yoy_growth_pct |
    |---|---|---|---|
    | 2023-01 | 210000000 | 198000000 | 6.1 |
    | 2023-02 | 195000000 | 175000000 | 11.4 |
    | ... | ... | ... | ... |
    | 2024-01 | 235000000 | 210000000 | 11.9 |
    | ... | ... | ... | ... |


---


### Problem 9. Moving Average — 3-month moving average of sales

Find the three-month moving average of monthly sales.
Moving averages smooth out seasonal fluctuations when identifying trends.


??? tip "Hint"
    - `AVG(revenue) OVER (ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`
    - There is insufficient data in the first 2 months, so moving averages may not be accurate.

??? success "Answer"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount)) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2023-01-01' AND ordered_at < '2025-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        )) AS moving_avg_3m,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        )) AS moving_avg_6m
    FROM monthly
    ORDER BY year_month;
    ```

    | year_month | revenue | moving_avg_3m | moving_avg_6m |
    |---|---|---|---|
    | 2023-01 | 210000000 | 210000000 | 210000000 |
    | 2023-02 | 195000000 | 202500000 | 202500000 |
    | 2023-03 | 220000000 | 208333333 | 208333333 |
    | 2023-04 | 205000000 | 206666667 | 207500000 |
    | ... | ... | ... | ... |


---


### Problem 10. ABC Analysis — Cumulative sales ratio by product

Sort sales by product in descending order in 2024, and assign A/B/C grades based on cumulative sales ratio.
(A: Top 70%, B: 70~90%, C: Rest)


??? tip "Hint"
    - Cumulative ratio: `SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER ()`
    - Classification into A/B/C grades using CASE statement
    - A variation of Pareto's law (80:20)

??? success "Answer"
    ```sql
    WITH product_revenue AS (
        SELECT
            p.id,
            p.name AS product_name,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name
    ),
    cumulative AS (
        SELECT
            product_name,
            revenue,
            SUM(revenue) OVER (ORDER BY revenue DESC) AS cum_revenue,
            SUM(revenue) OVER () AS total_revenue
        FROM product_revenue
    )
    SELECT
        product_name,
        revenue,
        ROUND(100.0 * cum_revenue / total_revenue, 1) AS cum_pct,
        CASE
            WHEN 100.0 * cum_revenue / total_revenue <= 70 THEN 'A'
            WHEN 100.0 * cum_revenue / total_revenue <= 90 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM cumulative
    ORDER BY revenue DESC
    LIMIT 30;
    ```

    | product_name | revenue | cum_pct | abc_class |
    |---|---|---|---|
    | (Premium Laptop) | 360000000 | 3.2 | A |
    | (Popular Desktop) | 280000000 | 5.7 | A |
    | ... | ... | ... | ... |
    | (Budget Mouse) | 5000000 | 91.2 | C |


---


### Problem 11. Comparison of sales from new customers vs. repeat customers

Separate the number of orders and sales from new customers (first order that month) and repeat customers by month in 2024.


??? tip "Hint"
    - Month of first order for each customer: obtained as `MIN(ordered_at)`
    - Order month = “New” if it is the month of first order, otherwise “Repurchase”
    - Step by step treatment with CTE

??? success "Answer"
    ```sql
    WITH first_order AS (
        SELECT
            customer_id,
            SUBSTR(MIN(ordered_at), 1, 7) AS first_month
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    classified AS (
        SELECT
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            CASE
                WHEN SUBSTR(o.ordered_at, 1, 7) = fo.first_month THEN 'New'
                ELSE 'Repeat'
            END AS customer_type,
            o.total_amount
        FROM orders AS o
        INNER JOIN first_order AS fo ON o.customer_id = fo.customer_id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        year_month,
        customer_type,
        COUNT(*)                  AS order_count,
        ROUND(SUM(total_amount)) AS revenue
    FROM classified
    GROUP BY year_month, customer_type
    ORDER BY year_month, customer_type;
    ```

    | year_month | customer_type | order_count | revenue |
    |---|---|---|---|
    | 2024-01 | New | 85 | 42000000 |
    | 2024-01 | Repeat | 350 | 193000000 |
    | 2024-02 | New | 72 | 38000000 |
    | 2024-02 | Repeat | 320 | 180000000 |
    | ... | ... | ... | ... |


---


### Problem 12. Trend of average unit price by customer level

Find the average order amount by customer level (BRONZE/SILVER/GOLD/VIP) by month in 2024.


??? tip "Hint"
    - Graded as `customers.grade`
    - `AVG(total_amount)` Aggregation by group
    - GROUP BY with two dimensions: month + grade

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(o.ordered_at, 1, 7) AS year_month,
        c.grade,
        COUNT(*)                   AS order_count,
        ROUND(AVG(o.total_amount)) AS avg_order_value
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(o.ordered_at, 1, 7), c.grade
    ORDER BY year_month, 
        CASE c.grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
        END;
    ```

    | year_month | grade | order_count | avg_order_value |
    |---|---|---|---|
    | 2024-01 | VIP | 45 | 1200000 |
    | 2024-01 | GOLD | 85 | 850000 |
    | 2024-01 | SILVER | 120 | 620000 |
    | 2024-01 | BRONZE | 185 | 380000 |
    | ... | ... | ... | ... |


---


### Problem 13. Delivery time analysis by shipping company

Find the average delivery days, minimum/maximum lead days, and number of deliveries by carrier in 2024.
Only items that have been delivered are eligible.


??? tip "Hint"
    - Delivery time: `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)`
    - `status = 'delivered'` in table `shipping`
    - Only if both `shipped_at` and `delivered_at` are NOT NULL.

??? success "Answer"
    ```sql
    SELECT
        s.carrier,
        COUNT(*)                                                        AS delivery_count,
        ROUND(AVG(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at)), 1) AS avg_days,
        MIN(ROUND(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at), 1)) AS min_days,
        MAX(ROUND(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at), 1)) AS max_days,
        ROUND(100.0 * SUM(CASE
            WHEN JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at) <= 2 THEN 1
            ELSE 0
        END) / COUNT(*), 1) AS within_2days_pct
    FROM shipping AS s
    INNER JOIN orders AS o ON s.order_id = o.id
    WHERE s.status = 'delivered'
      AND s.shipped_at IS NOT NULL
      AND s.delivered_at IS NOT NULL
      AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
    GROUP BY s.carrier
    ORDER BY avg_days;
    ```

    | carrier | delivery_count | avg_days | min_days | max_days | within_2days_pct |
    |---|---|---|---|---|---|
    | CJ Logistics | 3200 | 1.8 | 0.5 | 5.2 | 68.5 |
    | Hanjin Express | 2800 | 2.1 | 0.5 | 6.0 | 55.2 |
    | ... | ... | ... | ... | ... | ... |


---


### Problem 14. Sales impact by discount rate section

Divide the discount rate for orders in 2024 (discount_amount / (total_amount + discount_amount)) into sections,
Analyze the number of orders, average order amount, and total sales for each segment.


??? tip "Hint"
    - Discount rate = `discount_amount / (total_amount + discount_amount) * 100`
    - Categorize into 0%, 1~5%, 6~10%, 11~20%, 20%+ sections using CASE statement
    - If `discount_amount = 0`, no discount

??? success "Answer"
    ```sql
    WITH order_discount AS (
        SELECT
            id,
            total_amount,
            discount_amount,
            CASE
                WHEN discount_amount = 0 THEN 0
                ELSE ROUND(100.0 * discount_amount / (total_amount + discount_amount), 1)
            END AS discount_pct
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        CASE
            WHEN discount_pct = 0    THEN 'No discount'
            WHEN discount_pct <= 5   THEN '1~5%'
            WHEN discount_pct <= 10  THEN '6~10%'
            WHEN discount_pct <= 20  THEN '11~20%'
            ELSE 'Over 20%'
        END AS discount_range,
        COUNT(*)                    AS order_count,
        ROUND(AVG(total_amount))    AS avg_order_value,
        ROUND(SUM(total_amount))    AS total_revenue
    FROM order_discount
    GROUP BY CASE
        WHEN discount_pct = 0    THEN 'No discount'
        WHEN discount_pct <= 5   THEN '1~5%'
        WHEN discount_pct <= 10  THEN '6~10%'
        WHEN discount_pct <= 20  THEN '11~20%'
        ELSE 'Over 20%'
    END
    ORDER BY
        CASE
            WHEN discount_pct = 0    THEN 1
            WHEN discount_pct <= 5   THEN 2
            WHEN discount_pct <= 10  THEN 3
            WHEN discount_pct <= 20  THEN 4
            ELSE 5
        END;
    ```

    | discount_range | order_count | avg_order_value | total_revenue |
    |---|---|---|---|
    | No discount | 8500 | 580000 | 4930000000 |
    | 1~5% | 2100 | 620000 | 1302000000 |
    | 6~10% | 1500 | 750000 | 1125000000 |
    | 11~20% | 800 | 900000 | 720000000 |
    | Over 20% | 200 | 1100000 | 220000000 |


---


### Problem 15. Promotion ROI analysis

Analyze the sales effect (ROI) of each promotion compared to the input discount amount.
During the promotion period, sales and discount amounts for promotional products are counted.


??? tip "Hint"
    - Identify target product with `promotions` + `promotion_products`
    - Promotion period: `started_at` ~ `ended_at`
    - In `order_items`, sales for the relevant period + the relevant product are tallied.
    - ROI = (Sales - Discount Total) / Discount Total * 100

??? success "Answer"
    ```sql
    WITH promo_sales AS (
        SELECT
            pr.id           AS promo_id,
            pr.name         AS promo_name,
            pr.type         AS promo_type,
            pr.discount_type,
            pr.discount_value,
            COUNT(DISTINCT o.id) AS order_count,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS gross_revenue,
            ROUND(SUM(oi.discount_amount))          AS total_discount
        FROM promotions AS pr
        INNER JOIN promotion_products AS pp ON pr.id = pp.promotion_id
        INNER JOIN order_items AS oi ON pp.product_id = oi.product_id
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= pr.started_at
          AND o.ordered_at <= pr.ended_at
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY pr.id, pr.name, pr.type, pr.discount_type, pr.discount_value
    )
    SELECT
        promo_name,
        promo_type,
        discount_type || ' ' || discount_value AS discount_info,
        order_count,
        gross_revenue,
        total_discount,
        gross_revenue - total_discount AS net_revenue,
        CASE
            WHEN total_discount > 0
            THEN ROUND(100.0 * (gross_revenue - total_discount) / total_discount, 1)
            ELSE NULL
        END AS roi_pct
    FROM promo_sales
    ORDER BY roi_pct DESC;
    ```

    | promo_name | promo_type | discount_info | order_count | gross_revenue | total_discount | net_revenue | roi_pct |
    |---|---|---|---|---|---|---|---|
    | Summer Sale | seasonal | percent 15 | 450 | 320000000 | 48000000 | 272000000 | 566.7 |
    | Year-end Special | flash | fixed 50000 | 280 | 250000000 | 14000000 | 236000000 | 1685.7 |
    | ... | ... | ... | ... | ... | ... | ... | ... |


---


### Problem 16. Shopping Cart → Purchase Conversion Rate

Find the percentage of products in your shopping cart that were converted into actual purchases by category.


??? tip "Hint"
    - Number of products contained in `cart_items` vs. number of identical products actually ordered by the same customer
    - `carts` + `cart_items` + `order_items` + `orders` JOIN
    - Conversion rate = Number of cart items purchased / Total number of cart items * 100

??? success "Answer"
    ```sql
    WITH cart_products AS (
        SELECT
            c.customer_id,
            ci.product_id,
            cat.name AS category
        FROM carts AS c
        INNER JOIN cart_items AS ci ON c.id = ci.cart_id
        INNER JOIN products AS p ON ci.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
    ),
    purchased AS (
        SELECT DISTINCT
            o.customer_id,
            oi.product_id
        FROM orders AS o
        INNER JOIN order_items AS oi ON o.id = oi.order_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        cp.category,
        COUNT(*) AS cart_items_total,
        SUM(CASE WHEN pur.product_id IS NOT NULL THEN 1 ELSE 0 END) AS converted,
        ROUND(100.0 * SUM(CASE WHEN pur.product_id IS NOT NULL THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS conversion_rate_pct
    FROM cart_products AS cp
    LEFT JOIN purchased AS pur
        ON cp.customer_id = pur.customer_id
        AND cp.product_id = pur.product_id
    GROUP BY cp.category
    ORDER BY conversion_rate_pct DESC;
    ```

    | category | cart_items_total | converted | conversion_rate_pct |
    |---|---|---|---|
    | (Popular Category) | 1200 | 840 | 70.0 |
    | (General Category) | 800 | 320 | 40.0 |
    | ... | ... | ... | ... |


---


### Problem 17. Simultaneous purchase patterns (shopping cart analysis)

Find pairs of products purchased together in the same order.
Shows only product pairs with more than 5 simultaneous purchases.


??? tip "Hint"
    - Self-join `order_items` to create different product pairs of the same order
    - Deduplication: `oi1.product_id < oi2.product_id`
    - Count the number of simultaneous purchases by `GROUP BY` product pair

??? success "Answer"
    ```sql
    SELECT
        p1.name AS product_a,
        p2.name AS product_b,
        COUNT(*) AS co_purchase_count
    FROM order_items AS oi1
    INNER JOIN order_items AS oi2
        ON oi1.order_id = oi2.order_id
        AND oi1.product_id < oi2.product_id
    INNER JOIN products AS p1 ON oi1.product_id = p1.id
    INNER JOIN products AS p2 ON oi2.product_id = p2.id
    INNER JOIN orders AS o ON oi1.order_id = o.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY oi1.product_id, oi2.product_id, p1.name, p2.name
    HAVING COUNT(*) >= 5
    ORDER BY co_purchase_count DESC
    LIMIT 20;
    ```

    | product_a | product_b | co_purchase_count |
    |---|---|---|
    | (Keyboard A) | (Mouse B) | 25 |
    | (SSD C) | (Memory D) | 18 |
    | ... | ... | ... |


---


### Problem 18. Correlation between review ratings and sales

Analyze the relationship between average review rating and sales for each product.
Calculate average sales by rating range (1~2, 2~3, 3~4, 4~5).


??? tip "Hint"
    - First calculate the average rating and sales for each product
    - Classification of rating sections using CASE statement
    - Excluding products without reviews

??? success "Answer"
    ```sql
    WITH product_metrics AS (
        SELECT
            p.id,
            p.name,
            AVG(r.rating)                          AS avg_rating,
            COUNT(DISTINCT r.id)                    AS review_count,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS revenue
        FROM products AS p
        INNER JOIN reviews AS r ON p.id = r.product_id
        INNER JOIN order_items AS oi ON p.id = oi.product_id
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name
        HAVING COUNT(DISTINCT r.id) >= 3
    )
    SELECT
        CASE
            WHEN avg_rating < 2 THEN '1.0~1.9'
            WHEN avg_rating < 3 THEN '2.0~2.9'
            WHEN avg_rating < 4 THEN '3.0~3.9'
            ELSE '4.0~5.0'
        END AS rating_range,
        COUNT(*)                    AS product_count,
        ROUND(AVG(revenue))         AS avg_revenue,
        ROUND(AVG(review_count))    AS avg_reviews,
        ROUND(AVG(avg_rating), 2)   AS avg_rating_in_range
    FROM product_metrics
    GROUP BY CASE
        WHEN avg_rating < 2 THEN '1.0~1.9'
        WHEN avg_rating < 3 THEN '2.0~2.9'
        WHEN avg_rating < 4 THEN '3.0~3.9'
        ELSE '4.0~5.0'
    END
    ORDER BY rating_range;
    ```

    | rating_range | product_count | avg_revenue | avg_reviews | avg_rating_in_range |
    |---|---|---|---|---|
    | 1.0~1.9 | 5 | 12000000 | 8 | 1.65 |
    | 2.0~2.9 | 15 | 28000000 | 12 | 2.55 |
    | 3.0~3.9 | 80 | 45000000 | 18 | 3.52 |
    | 4.0~5.0 | 120 | 62000000 | 25 | 4.35 |


---


### Problem 19. Analysis of point usage effects

Compare the average order amount and repurchase rate for orders that used points and those that did not.
(As of 2024)


??? tip "Hint"
    - If `orders.point_used > 0`, order using points
    - Repurchase rate: The percentage of customers in the group who ordered more than twice
    - First aggregate order characteristics for each customer using CTE

??? success "Answer"
    ```sql
    WITH order_classified AS (
        SELECT
            customer_id,
            total_amount,
            CASE WHEN point_used > 0 THEN 'Points used' ELSE 'Not used' END AS point_type
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    customer_stats AS (
        SELECT
            point_type,
            customer_id,
            COUNT(*) AS order_count,
            AVG(total_amount) AS avg_amount
        FROM order_classified
        GROUP BY point_type, customer_id
    )
    SELECT
        point_type,
        COUNT(DISTINCT customer_id)    AS customer_count,
        ROUND(AVG(avg_amount))         AS avg_order_value,
        ROUND(100.0 * SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END)
            / COUNT(*), 1)            AS repeat_rate_pct
    FROM customer_stats
    GROUP BY point_type;
    ```

    | point_type | customer_count | avg_order_value | repeat_rate_pct |
    |---|---|---|---|
    | Points used | 2800 | 720000 | 65.3 |
    | Not used | 3500 | 550000 | 42.1 |


---


### Problem 20. Comprehensive management dashboard

Create a comprehensive 2024 management dashboard for CEOs with a single query.
Includes total sales, number of orders, number of customers, average unit price, return rate, average delivery date, and average review rating.


??? tip "Hint"
    - Calculate each indicator individually using subquery or CTE and then combine them
    - Combine single rows with `CROSS JOIN` or scalar subqueries
    - Return rate = Number of returned orders / Total number of orders

??? success "Answer"
    ```sql
    WITH sales AS (
        SELECT
            COUNT(*)                            AS total_orders,
            COUNT(DISTINCT customer_id)         AS unique_customers,
            ROUND(SUM(total_amount))            AS total_revenue,
            ROUND(AVG(total_amount))            AS avg_order_value
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    returns_stat AS (
        SELECT
            ROUND(100.0 * COUNT(*) / (
                SELECT COUNT(*) FROM orders
                WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
            ), 1) AS return_rate_pct
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status IN ('returned', 'return_requested')
    ),
    shipping_stat AS (
        SELECT
            ROUND(AVG(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at)), 1) AS avg_delivery_days
        FROM shipping AS s
        INNER JOIN orders AS o ON s.order_id = o.id
        WHERE s.status = 'delivered'
          AND s.shipped_at IS NOT NULL
          AND s.delivered_at IS NOT NULL
          AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
    ),
    review_stat AS (
        SELECT
            ROUND(AVG(rating), 2) AS avg_rating,
            COUNT(*) AS review_count
        FROM reviews
        WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
    )
    SELECT
        s.total_revenue,
        s.total_orders,
        s.unique_customers,
        s.avg_order_value,
        r.return_rate_pct,
        sh.avg_delivery_days,
        rv.avg_rating,
        rv.review_count
    FROM sales AS s
    CROSS JOIN returns_stat AS r
    CROSS JOIN shipping_stat AS sh
    CROSS JOIN review_stat AS rv;
    ```

    | total_revenue | total_orders | unique_customers | avg_order_value | return_rate_pct | avg_delivery_days | avg_rating | review_count |
    |---|---|---|---|---|---|---|---|
    | 12500000000 | 18500 | 5200 | 675676 | 8.5 | 2.1 | 4.12 | 4800 |
