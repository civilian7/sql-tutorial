# Customer/Operations Analysis

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `customers` — Customer<br>
    `orders` — Order<br>
    `order_items` — Order Details<br>
    `products` — Product<br>
    `categories` — Category<br>
    `inventory_transactions` — Incoming/outgoing history<br>
    `customer_grade_history` — Grade change history<br>
    `complaints` — File a complaint<br>
    `staff` — Employee

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    RFM Analysis<br>
    Cohort<br>
    LTV<br>
    Inventory ABC Analysis<br>
    Safety stock<br>
    CS Performance — CTE + Window Function + Multiple JOIN

</div>

This is a customer analysis and operational analysis problem that comprehensively utilizes CTE, window functions, multiple JOINs, and aggregate functions.
It covers analysis scenarios frequently encountered in practice, including customer segmentation, inventory management, CS performance, and comprehensive dashboards.

---

## Customer Analysis (1~7)


### Problem 1. RFM basics — calculation of key indicators for each customer

The marketing team requested RFM metrics for each customer for customer segmentation.
Find the last order date (Recency), total number of orders (Frequency), and total purchase amount (Monetary) for each customer.
Excludes canceled/returned orders. Only the top 20 are shown.


??? tip "Hint"
    - Recency: `MAX(ordered_at)`
    - Frequency: `COUNT(*)`
    - Monetary: `SUM(total_amount)`
    - `customers` + `orders` JOIN

??? success "Answer"
    ```sql
    SELECT
        c.id            AS customer_id,
        c.name          AS customer_name,
        c.grade,
        MAX(o.ordered_at)           AS last_order_date,
        COUNT(*)                    AS order_count,
        ROUND(SUM(o.total_amount))  AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 20;
    ```

    | customer_id | customer_name | grade | last_order_date | order_count | total_spent |
    |---|---|---|---|---|---|
    | 42 | 김민수 | VIP | 2025-03-15 10:23:45 | 45 | 52000000 |
    | 128 | 이서연 | VIP | 2025-03-12 14:55:20 | 38 | 48000000 |
    | ... | ... | ... | ... | ... | ... |


---


### Problem 2. RFM quartile segment

Divide your customers into quartiles (Q1 to Q4) based on RFM metrics.
The more recent the Recency, the higher the score (4), and the larger the Frequency and Monetary, the higher the score (4).
Displays each customer's R/F/M score and total score.


??? tip "Hint"
    - Divide each indicator into 4 equal parts with `NTILE(4)`
    - Recency: `ORDER BY last_order_date ASC` → NTILE 4 is the most recent
    - Frequency/Monetary: `ORDER BY ... ASC` → NTILE 4 is the largest
    - Total score = R + F + M (maximum 12 points)

??? success "Answer"
    ```sql
    WITH rfm_raw AS (
        SELECT
            c.id AS customer_id,
            c.name,
            c.grade,
            MAX(o.ordered_at)           AS last_order_date,
            COUNT(*)                    AS frequency,
            ROUND(SUM(o.total_amount))  AS monetary
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    ),
    rfm_scored AS (
        SELECT
            customer_id,
            name,
            grade,
            last_order_date,
            frequency,
            monetary,
            NTILE(4) OVER (ORDER BY last_order_date ASC)  AS r_score,
            NTILE(4) OVER (ORDER BY frequency ASC)         AS f_score,
            NTILE(4) OVER (ORDER BY monetary ASC)          AS m_score
        FROM rfm_raw
    )
    SELECT
        customer_id,
        name,
        grade,
        r_score,
        f_score,
        m_score,
        r_score + f_score + m_score AS rfm_total,
        CASE
            WHEN r_score + f_score + m_score >= 10 THEN 'Champion'
            WHEN r_score + f_score + m_score >= 7  THEN 'Loyal'
            WHEN r_score >= 3 AND f_score <= 2     THEN 'New Customer'
            WHEN r_score <= 2 AND f_score >= 3     THEN 'At Risk'
            ELSE 'Regular'
        END AS segment
    FROM rfm_scored
    ORDER BY rfm_total DESC
    LIMIT 20;
    ```

    | customer_id | name | grade | r_score | f_score | m_score | rfm_total | segment |
    |---|---|---|---|---|---|---|---|
    | 42 | 김민수 | VIP | 4 | 4 | 4 | 12 | Champion |
    | 128 | 이서연 | VIP | 4 | 4 | 4 | 12 | Champion |
    | ... | ... | ... | ... | ... | ... | ... | ... |


---


### Problem 3. Cohort retention analysis

Find the monthly retention (repurchase rate) of customers who made their first purchase in 2023 through cohort analysis.
Calculate the retention rate for 0 months (first purchase), 1 month, 2 months, ... 6 months after signing up.


??? tip "Hint"
    - Cohort = group of customers with the same first purchase month
    - Month Difference = Order Month - First Purchase Month (in months)
    - Retention rate = Number of cohort customers who ordered in that month / Total number of cohort customers

??? success "Answer"
    ```sql
    WITH first_purchase AS (
        SELECT
            customer_id,
            SUBSTR(MIN(ordered_at), 1, 7) AS cohort_month
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
        HAVING cohort_month LIKE '2023%'
    ),
    monthly_activity AS (
        SELECT DISTINCT
            fp.customer_id,
            fp.cohort_month,
            SUBSTR(o.ordered_at, 1, 7) AS activity_month,
            (CAST(SUBSTR(o.ordered_at, 1, 4) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 1, 4) AS INTEGER)) * 12
            + CAST(SUBSTR(o.ordered_at, 6, 2) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 6, 2) AS INTEGER)
                AS month_offset
        FROM first_purchase AS fp
        INNER JOIN orders AS o ON fp.customer_id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    cohort_size AS (
        SELECT cohort_month, COUNT(DISTINCT customer_id) AS total_customers
        FROM first_purchase
        GROUP BY cohort_month
    )
    SELECT
        ma.cohort_month,
        cs.total_customers,
        ma.month_offset,
        COUNT(DISTINCT ma.customer_id) AS active_customers,
        ROUND(100.0 * COUNT(DISTINCT ma.customer_id) / cs.total_customers, 1) AS retention_pct
    FROM monthly_activity AS ma
    INNER JOIN cohort_size AS cs ON ma.cohort_month = cs.cohort_month
    WHERE ma.month_offset BETWEEN 0 AND 6
    GROUP BY ma.cohort_month, cs.total_customers, ma.month_offset
    ORDER BY ma.cohort_month, ma.month_offset;
    ```

    | cohort_month | total_customers | month_offset | active_customers | retention_pct |
    |---|---|---|---|---|
    | 2023-01 | 120 | 0 | 120 | 100.0 |
    | 2023-01 | 120 | 1 | 42 | 35.0 |
    | 2023-01 | 120 | 2 | 35 | 29.2 |
    | 2023-01 | 120 | 3 | 30 | 25.0 |
    | ... | ... | ... | ... | ... |


---


### Problem 4. Detecting Churning Customers

Classify customers who haven't made a purchase in more than six months since their last order as "churn risk."
Find the distribution of churned customers by grade and the average purchase amount before churning.
(Base date: 2025-03-31)


??? tip "Hint"
    - Exit criteria: `JULIANDAY('2025-03-31') - JULIANDAY(MAX(ordered_at)) > 180`
    - GROUP BY by grade
    - Also displays comparison between churned and active customers

??? success "Answer"
    ```sql
    WITH customer_activity AS (
        SELECT
            c.id            AS customer_id,
            c.name,
            c.grade,
            MAX(o.ordered_at)           AS last_order_date,
            COUNT(*)                    AS order_count,
            ROUND(AVG(o.total_amount))  AS avg_order_value,
            ROUND(JULIANDAY('2025-03-31') - JULIANDAY(MAX(o.ordered_at))) AS days_since_last
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    )
    SELECT
        grade,
        CASE WHEN days_since_last > 180 THEN 'At risk' ELSE 'Active' END AS status,
        COUNT(*) AS customer_count,
        ROUND(AVG(avg_order_value)) AS avg_order_value,
        ROUND(AVG(order_count), 1)  AS avg_orders,
        ROUND(AVG(days_since_last)) AS avg_days_inactive
    FROM customer_activity
    GROUP BY grade,
        CASE WHEN days_since_last > 180 THEN 'At risk' ELSE 'Active' END
    ORDER BY
        CASE grade WHEN 'VIP' THEN 1 WHEN 'GOLD' THEN 2 WHEN 'SILVER' THEN 3 ELSE 4 END,
        status;
    ```

    | grade | status | customer_count | avg_order_value | avg_orders | avg_days_inactive |
    |---|---|---|---|---|---|
    | VIP | Active | 85 | 1200000 | 15.2 | 25 |
    | VIP | At risk | 12 | 980000 | 8.5 | 245 |
    | GOLD | Active | 320 | 850000 | 10.1 | 35 |
    | GOLD | At risk | 45 | 720000 | 5.2 | 220 |
    | ... | ... | ... | ... | ... | ... |


---


### Problem 5. Estimating customer lifetime value (LTV)

Estimate the average Life Time Value (LTV) for each customer tier.
LTV = average order value x number of orders per year x average duration of activity (years)


??? tip "Hint"
    - Activity period = (last order date - first order date) / 365. Processed as a minimum of 1 year
    - Number of orders per year = Total number of orders / Activity period
    - Aggregation by grade

??? success "Answer"
    ```sql
    WITH customer_ltv AS (
        SELECT
            c.id,
            c.grade,
            COUNT(*) AS total_orders,
            AVG(o.total_amount) AS avg_order_value,
            MAX(JULIANDAY(o.ordered_at) - JULIANDAY(MIN(o.ordered_at)) OVER (PARTITION BY c.id))
                / 365.0 AS active_years_raw
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.grade
    ),
    ltv_calc AS (
        SELECT
            id,
            grade,
            total_orders,
            avg_order_value,
            MAX(active_years_raw, 1.0) AS active_years,
            total_orders / MAX(active_years_raw, 1.0) AS orders_per_year,
            avg_order_value * (total_orders / MAX(active_years_raw, 1.0)) * MAX(active_years_raw, 1.0)
                AS ltv
        FROM customer_ltv
    )
    SELECT
        grade,
        COUNT(*) AS customer_count,
        ROUND(AVG(avg_order_value))  AS avg_order_value,
        ROUND(AVG(orders_per_year), 1) AS avg_annual_orders,
        ROUND(AVG(active_years), 1)    AS avg_active_years,
        ROUND(AVG(ltv))                AS avg_ltv
    FROM ltv_calc
    GROUP BY grade
    ORDER BY avg_ltv DESC;
    ```

    | grade | customer_count | avg_order_value | avg_annual_orders | avg_active_years | avg_ltv |
    |---|---|---|---|---|---|
    | VIP | 97 | 1150000 | 8.5 | 5.2 | 50830000 |
    | GOLD | 365 | 820000 | 5.2 | 4.1 | 17472800 |
    | SILVER | 1200 | 580000 | 3.1 | 3.0 | 5394000 |
    | BRONZE | 3500 | 380000 | 1.8 | 2.2 | 1504800 |


---


### Problem 6. Comparison of customer quality by subscription channel

Number of customers, average number of orders, average purchase amount by subscription channel (`acquisition_channel`),
Compare VIP/GOLD conversion rates.


??? tip "Hint"
    - `customers.acquisition_channel`: organic/search_ad/social/referral/direct
    - VIP/GOLD conversion rate = Number of VIP+GOLD customers in the channel / Total number of customers
    - Including customers without orders (LEFT JOIN)

??? success "Answer"
    ```sql
    WITH channel_stats AS (
        SELECT
            COALESCE(c.acquisition_channel, 'Unknown') AS channel,
            c.id AS customer_id,
            c.grade,
            COUNT(o.id) AS order_count,
            COALESCE(SUM(o.total_amount), 0) AS total_spent
        FROM customers AS c
        LEFT JOIN orders AS o
            ON c.id = o.customer_id
            AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.acquisition_channel, c.id, c.grade
    )
    SELECT
        channel,
        COUNT(*)                        AS customer_count,
        ROUND(AVG(order_count), 1)      AS avg_orders,
        ROUND(AVG(CASE WHEN total_spent > 0 THEN total_spent END)) AS avg_spent,
        ROUND(100.0 * SUM(CASE WHEN grade IN ('VIP', 'GOLD') THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS premium_rate_pct,
        ROUND(100.0 * SUM(CASE WHEN order_count = 0 THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS never_ordered_pct
    FROM channel_stats
    GROUP BY channel
    ORDER BY avg_spent DESC;
    ```

    | channel | customer_count | avg_orders | avg_spent | premium_rate_pct | never_ordered_pct |
    |---|---|---|---|---|---|
    | referral | 800 | 6.2 | 4800000 | 15.2 | 5.0 |
    | organic | 2200 | 4.5 | 3200000 | 10.5 | 8.5 |
    | search_ad | 1500 | 3.8 | 2800000 | 8.2 | 12.0 |
    | social | 1000 | 3.1 | 2200000 | 6.5 | 15.0 |
    | direct | 600 | 2.5 | 1800000 | 5.0 | 18.0 |


---


### Problem 7. Tracking grade changes

Using the `customer_grade_history` table, find the number of customers whose ratings went up and down in 2024.
It also displays the number of cases by grade change path (e.g. SILVER → GOLD).


??? tip "Hint"
    - `customer_grade_history`: `customer_id`, `old_grade`, `new_grade`, `changed_at`
    - Rank order: BRONZE < SILVER < GOLD < VIP
    - Compare after assigning numbers to grades using a CASE statement

??? success "Answer"
    ```sql
    WITH grade_order AS (
        SELECT
            customer_id,
            old_grade,
            new_grade,
            changed_at,
            CASE old_grade WHEN 'BRONZE' THEN 1 WHEN 'SILVER' THEN 2 WHEN 'GOLD' THEN 3 WHEN 'VIP' THEN 4 END AS old_rank,
            CASE new_grade WHEN 'BRONZE' THEN 1 WHEN 'SILVER' THEN 2 WHEN 'GOLD' THEN 3 WHEN 'VIP' THEN 4 END AS new_rank
        FROM customer_grade_history
        WHERE changed_at LIKE '2024%'
    )
    SELECT
        old_grade || ' → ' || new_grade AS grade_change,
        CASE
            WHEN new_rank > old_rank THEN 'Upgraded'
            WHEN new_rank < old_rank THEN 'Downgraded'
            ELSE 'Maintained'
        END AS direction,
        COUNT(*) AS change_count
    FROM grade_order
    GROUP BY old_grade, new_grade, direction
    ORDER BY
        CASE WHEN new_rank > old_rank THEN 1 WHEN new_rank < old_rank THEN 2 ELSE 3 END,
        change_count DESC;
    ```

    | grade_change | direction | change_count |
    |---|---|---|
    | BRONZE → SILVER | Upgraded | 250 |
    | SILVER → GOLD | Upgraded | 120 |
    | GOLD → VIP | Upgraded | 35 |
    | GOLD → SILVER | Downgraded | 45 |
    | SILVER → BRONZE | Downgraded | 80 |
    | VIP → GOLD | Downgraded | 8 |


---

## Inventory Management (8~12)


### Problem 8. ABC inventory classification

Sort products ABC based on current inventory amount (stock_qty x cost_price).
(A: Top 70%, B: 70~90%, C: Rest)
Displays the number of products in each grade and the total inventory amount.


??? tip "Hint"
    - Inventory amount = `stock_qty * cost_price`
    - ABC classification by cumulative ratio (same pattern as ABC in sales analysis)
    - Only active products are eligible

??? success "Answer"
    ```sql
    WITH inventory_value AS (
        SELECT
            p.id,
            p.name,
            p.stock_qty,
            p.cost_price,
            p.stock_qty * p.cost_price AS stock_value
        FROM products AS p
        WHERE p.is_active = 1
          AND p.stock_qty > 0
    ),
    cumulative AS (
        SELECT
            id, name, stock_qty, cost_price, stock_value,
            SUM(stock_value) OVER (ORDER BY stock_value DESC) AS cum_value,
            SUM(stock_value) OVER () AS total_value
        FROM inventory_value
    ),
    classified AS (
        SELECT *,
            CASE
                WHEN 100.0 * cum_value / total_value <= 70 THEN 'A'
                WHEN 100.0 * cum_value / total_value <= 90 THEN 'B'
                ELSE 'C'
            END AS abc_class
        FROM cumulative
    )
    SELECT
        abc_class,
        COUNT(*)                 AS product_count,
        ROUND(SUM(stock_value)) AS total_stock_value,
        ROUND(100.0 * SUM(stock_value) / (SELECT SUM(stock_value) FROM inventory_value), 1) AS value_pct,
        ROUND(AVG(stock_qty))    AS avg_stock_qty
    FROM classified
    GROUP BY abc_class
    ORDER BY abc_class;
    ```

    | abc_class | product_count | total_stock_value | value_pct | avg_stock_qty |
    |---|---|---|---|---|
    | A | 35 | 1200000000 | 68.5 | 85 |
    | B | 60 | 380000000 | 21.7 | 120 |
    | C | 150 | 170000000 | 9.7 | 200 |


---


### Problem 9. Dead stock detection

Find active products that haven't sold at all in the last 6 months.
Displays inventory quantity, inventory amount, and last sale date.


??? tip "Hint"
    - Check last 6 months orders in `order_items` + `orders`
    - Product with NULL order after LEFT JOIN = No sale
    - or utilize the NOT EXISTS pattern

??? success "Answer"
    ```sql
    WITH last_sale AS (
        SELECT
            oi.product_id,
            MAX(o.ordered_at) AS last_sold_at
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY oi.product_id
    )
    SELECT
        p.name         AS product_name,
        cat.name       AS category,
        p.stock_qty,
        ROUND(p.stock_qty * p.cost_price) AS stock_value,
        ls.last_sold_at,
        ROUND(JULIANDAY('2025-03-31') - JULIANDAY(ls.last_sold_at)) AS days_since_last_sale
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LEFT JOIN last_sale AS ls ON p.id = ls.product_id
    WHERE p.is_active = 1
      AND p.stock_qty > 0
      AND (ls.last_sold_at IS NULL OR ls.last_sold_at < DATE('2025-03-31', '-6 months'))
    ORDER BY stock_value DESC
    LIMIT 20;
    ```

    | product_name | category | stock_qty | stock_value | last_sold_at | days_since_last_sale |
    |---|---|---|---|---|---|
    | (Legacy Part) | Storage | 45 | 13500000 | 2024-05-10 | 325 |
    | (Soon Discontinued) | Memory | 30 | 9000000 | 2024-06-22 | 282 |
    | ... | ... | ... | ... | ... | ... |


---


### Problem 10. Reorder Point Calculation

Calculate when to reorder based on the average daily shipment volume for each product.
Reorder point = average daily shipment x lead time (7 days) x safety factor (1.5)
Find products that are currently in stock at or below the reorder point.


??? tip "Hint"
    - Last 3 months shipment volume: `inventory_transactions` to `type = 'outbound'`
    - Average daily shipment volume = Total shipment volume for 3 months / 90
    - Re-order time = average daily shipment x 7 x 1.5

??? success "Answer"
    ```sql
    WITH daily_demand AS (
        SELECT
            product_id,
            ABS(SUM(quantity)) / 90.0 AS avg_daily_demand
        FROM inventory_transactions
        WHERE type = 'outbound'
          AND created_at >= DATE('2025-03-31', '-3 months')
        GROUP BY product_id
    ),
    reorder_calc AS (
        SELECT
            p.id,
            p.name,
            p.stock_qty,
            ROUND(dd.avg_daily_demand, 2) AS avg_daily_demand,
            ROUND(dd.avg_daily_demand * 7 * 1.5) AS reorder_point,
            ROUND(p.stock_qty / NULLIF(dd.avg_daily_demand, 0)) AS days_of_stock
        FROM products AS p
        INNER JOIN daily_demand AS dd ON p.id = dd.product_id
        WHERE p.is_active = 1
    )
    SELECT
        name AS product_name,
        stock_qty,
        avg_daily_demand,
        reorder_point,
        days_of_stock,
        CASE
            WHEN stock_qty <= reorder_point THEN 'Order now'
            WHEN days_of_stock <= 14 THEN 'Order soon'
            ELSE 'Sufficient'
        END AS order_status
    FROM reorder_calc
    WHERE stock_qty <= reorder_point
    ORDER BY days_of_stock ASC;
    ```

    | product_name | stock_qty | avg_daily_demand | reorder_point | days_of_stock | order_status |
    |---|---|---|---|---|---|
    | (Popular SSD) | 8 | 2.5 | 26 | 3 | Order now |
    | (Popular Memory) | 12 | 1.8 | 19 | 7 | Order now |
    | ... | ... | ... | ... | ... | ... |


---


### Problem 11. Inventory turnover by category

Calculate inventory turnover by category.
Inventory Turnover = Annual Cost of Goods Sold (COGS) / Average Inventory Amount


??? tip "Hint"
    - Cost of goods sold (COGS): `SUM(oi.quantity * p.cost_price)` (sales in 2024)
    - Average inventory amount: `AVG(stock_qty * cost_price)` (current time)
    - The higher the turnover rate, the faster inventory is sold.

??? success "Answer"
    ```sql
    WITH cogs_2024 AS (
        SELECT
            p.category_id,
            SUM(oi.quantity * p.cost_price) AS annual_cogs
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.category_id
    ),
    avg_inventory AS (
        SELECT
            category_id,
            AVG(stock_qty * cost_price) AS avg_stock_value,
            SUM(stock_qty * cost_price) AS total_stock_value,
            COUNT(*) AS product_count
        FROM products
        WHERE is_active = 1
        GROUP BY category_id
    )
    SELECT
        cat.name AS category,
        ai.product_count,
        ROUND(cg.annual_cogs) AS annual_cogs,
        ROUND(ai.total_stock_value) AS current_stock_value,
        ROUND(cg.annual_cogs / NULLIF(ai.avg_stock_value, 0), 1) AS turnover_rate,
        ROUND(365.0 / NULLIF(cg.annual_cogs / NULLIF(ai.avg_stock_value, 0), 0)) AS days_in_inventory
    FROM avg_inventory AS ai
    INNER JOIN cogs_2024 AS cg ON ai.category_id = cg.category_id
    INNER JOIN categories AS cat ON ai.category_id = cat.id
    ORDER BY turnover_rate DESC;
    ```

    | category | product_count | annual_cogs | current_stock_value | turnover_rate | days_in_inventory |
    |---|---|---|---|---|---|
    | (Popular Category) | 50 | 2500000000 | 350000000 | 7.1 | 51 |
    | (General Category) | 80 | 1800000000 | 500000000 | 3.6 | 101 |
    | ... | ... | ... | ... | ... | ... |


---


### Problem 12. Monthly trend of inventory arrival and departure

Calculate monthly receipts, shipments, net changes, and month-end cumulative inventory for 2024.
This is based on the sum of all products.


??? tip "Hint"
    - `type` in `inventory_transactions`: inbound (positive), outbound (negative)
    - Separation of receipt/delivery through conditional counting
    - Cumulative sum: `SUM(...) OVER (ORDER BY year_month)`

??? success "Answer"
    ```sql
    WITH monthly_flow AS (
        SELECT
            SUBSTR(created_at, 1, 7) AS year_month,
            SUM(CASE WHEN quantity > 0 THEN quantity ELSE 0 END) AS inbound_qty,
            SUM(CASE WHEN quantity < 0 THEN ABS(quantity) ELSE 0 END) AS outbound_qty,
            SUM(quantity) AS net_change
        FROM inventory_transactions
        WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
        GROUP BY SUBSTR(created_at, 1, 7)
    )
    SELECT
        year_month,
        inbound_qty,
        outbound_qty,
        net_change,
        SUM(net_change) OVER (ORDER BY year_month) AS cumulative_change
    FROM monthly_flow
    ORDER BY year_month;
    ```

    | year_month | inbound_qty | outbound_qty | net_change | cumulative_change |
    |---|---|---|---|---|
    | 2024-01 | 5200 | 4800 | 400 | 400 |
    | 2024-02 | 4800 | 4500 | 300 | 700 |
    | 2024-03 | 5500 | 5100 | 400 | 1100 |
    | ... | ... | ... | ... | ... |


---

## CS Performance Analysis (13~17)


### Problem 13. Inquiry processing time analysis

Find the average processing time, median (approximate), and SLA compliance rate by inquiry type (category) in 2024.
SLA: Resolution within 3 days for general inquiries, 1 day for claims, 0.5 days for emergencies


??? tip "Hint"
    - Processing time: `JULIANDAY(resolved_at) - JULIANDAY(created_at)`
    - Median approximation: 50th percentile → use `NTILE` instead of `PERCENTILE`
    - SLA standards are applied differently depending on `priority`

??? success "Answer"
    ```sql
    WITH resolution_times AS (
        SELECT
            category,
            priority,
            JULIANDAY(resolved_at) - JULIANDAY(created_at) AS resolution_days,
            CASE priority
                WHEN 'urgent' THEN 0.5
                WHEN 'high'   THEN 1.0
                WHEN 'medium' THEN 2.0
                ELSE 3.0
            END AS sla_days
        FROM complaints
        WHERE created_at LIKE '2024%'
          AND resolved_at IS NOT NULL
    )
    SELECT
        category,
        COUNT(*) AS resolved_count,
        ROUND(AVG(resolution_days), 2) AS avg_resolution_days,
        ROUND(MIN(resolution_days), 2) AS min_days,
        ROUND(MAX(resolution_days), 2) AS max_days,
        ROUND(100.0 * SUM(CASE WHEN resolution_days <= sla_days THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS sla_compliance_pct
    FROM resolution_times
    GROUP BY category
    ORDER BY sla_compliance_pct ASC;
    ```

    | category | resolved_count | avg_resolution_days | min_days | max_days | sla_compliance_pct |
    |---|---|---|---|---|---|
    | product_defect | 180 | 2.5 | 0.1 | 12.0 | 55.0 |
    | delivery_issue | 250 | 1.8 | 0.1 | 8.5 | 65.0 |
    | refund_request | 200 | 1.2 | 0.1 | 5.0 | 72.0 |
    | general_inquiry | 350 | 0.8 | 0.0 | 4.0 | 85.0 |
    | ... | ... | ... | ... | ... | ... |


---


### Problem 14. Return reason analysis and trend

Find the number, rate, and average refund amount by return reason in 2024.
We also check quarterly trends.


??? tip "Hint"
    - `returns` table: `reason`, `refund_amount`, `requested_at`
    - Write overall ratio + quarterly trend as a separate query

??? success "Answer"
    ```sql
    -- Overall statistics by reason
    SELECT
        reason,
        COUNT(*)                     AS return_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
        ROUND(AVG(refund_amount))    AS avg_refund,
        ROUND(SUM(refund_amount))    AS total_refund
    FROM returns
    WHERE requested_at >= '2024-01-01' AND requested_at < '2025-01-01'
    GROUP BY reason
    ORDER BY return_count DESC;
    ```

    | reason | return_count | pct | avg_refund | total_refund |
    |---|---|---|---|---|
    | change_of_mind | 320 | 35.2 | 450000 | 144000000 |
    | defective | 220 | 24.2 | 680000 | 149600000 |
    | wrong_item | 150 | 16.5 | 520000 | 78000000 |
    | damaged_in_transit | 120 | 13.2 | 550000 | 66000000 |
    | not_as_described | 80 | 8.8 | 480000 | 38400000 |
    | late_delivery | 18 | 2.0 | 380000 | 6840000 |

    ```sql
    -- Quarterly trend
    SELECT
        'Q' || ((CAST(SUBSTR(requested_at, 6, 2) AS INTEGER) + 2) / 3) AS quarter,
        reason,
        COUNT(*) AS return_count
    FROM returns
    WHERE requested_at >= '2024-01-01' AND requested_at < '2025-01-01'
    GROUP BY (CAST(SUBSTR(requested_at, 6, 2) AS INTEGER) + 2) / 3, reason
    ORDER BY quarter, return_count DESC;
    ```


---


### Problem 15. Comparison of performance by CS employee

Compare the number of inquiries handled by each CS employee, resolution rate, average processing time, and customer satisfaction (rate without compensation).
The difference from the overall average is also displayed.


??? tip "Hint"
    - `complaints.staff_id` → `staff` JOIN
    - Display overall averages in the same row with the window function `AVG(...) OVER ()`
    - Customer satisfaction proxy indicator: Proportion of compensation_type that is NULL or 'none'

??? success "Answer"
    ```sql
    WITH staff_metrics AS (
        SELECT
            s.name AS staff_name,
            COUNT(*) AS case_count,
            SUM(CASE WHEN comp.status IN ('resolved', 'closed') THEN 1 ELSE 0 END) AS resolved_count,
            AVG(CASE
                WHEN comp.resolved_at IS NOT NULL
                THEN JULIANDAY(comp.resolved_at) - JULIANDAY(comp.created_at)
            END) AS avg_resolution_days,
            100.0 * SUM(CASE WHEN COALESCE(comp.compensation_type, 'none') = 'none' THEN 1 ELSE 0 END)
                / COUNT(*) AS no_compensation_pct
        FROM complaints AS comp
        INNER JOIN staff AS s ON comp.staff_id = s.id
        WHERE comp.created_at LIKE '2024%'
        GROUP BY s.id, s.name
    )
    SELECT
        staff_name,
        case_count,
        ROUND(100.0 * resolved_count / case_count, 1) AS resolution_rate,
        ROUND(avg_resolution_days, 2) AS avg_days,
        ROUND(no_compensation_pct, 1) AS satisfaction_proxy_pct,
        ROUND(AVG(case_count) OVER (), 1) AS team_avg_cases,
        ROUND(AVG(avg_resolution_days) OVER (), 2) AS team_avg_days
    FROM staff_metrics
    ORDER BY resolution_rate DESC;
    ```

    | staff_name | case_count | resolution_rate | avg_days | satisfaction_proxy_pct | team_avg_cases | team_avg_days |
    |---|---|---|---|---|---|---|
    | Park Jieun | 85 | 95.3 | 0.8 | 72.5 | 65.0 | 1.5 |
    | Kim Haneul | 72 | 91.7 | 1.2 | 68.0 | 65.0 | 1.5 |
    | ... | ... | ... | ... | ... | ... | ... |


---


### Problem 16. Escalation analysis

Analyze the characteristics of escalated (escalated = 1) inquiries.
Understand which types, channels, and priorities are generating the most escalations.


??? tip "Hint"
    - The thing that is `complaints.escalated = 1`
    - Escalation rate = Number of escalations / Total number of cases
    - Aggregated by category, channel, and priority

??? success "Answer"
    ```sql
    SELECT
        category,
        channel,
        priority,
        COUNT(*) AS total_count,
        SUM(escalated) AS escalated_count,
        ROUND(100.0 * SUM(escalated) / COUNT(*), 1) AS escalation_rate_pct,
        ROUND(AVG(CASE
            WHEN escalated = 1 AND resolved_at IS NOT NULL
            THEN JULIANDAY(resolved_at) - JULIANDAY(created_at)
        END), 2) AS escalated_avg_days
    FROM complaints
    WHERE created_at LIKE '2024%'
    GROUP BY category, channel, priority
    HAVING COUNT(*) >= 5
    ORDER BY escalation_rate_pct DESC
    LIMIT 15;
    ```

    | category | channel | priority | total_count | escalated_count | escalation_rate_pct | escalated_avg_days |
    |---|---|---|---|---|---|---|
    | product_defect | phone | urgent | 15 | 12 | 80.0 | 3.5 |
    | delivery_issue | kakao | high | 25 | 15 | 60.0 | 2.8 |
    | refund_request | email | high | 18 | 9 | 50.0 | 2.2 |
    | ... | ... | ... | ... | ... | ... | ... |


---


### Problem 17. CS incidence rate by product

Find the CS (inquiries + returns) incidence rate of the top 30 products in sales.
Products with a high incidence of CS require quality improvement.


??? tip "Hint"
    - Ratio of inquiries/returns to number of sales
    - Number of sales by product in `order_items`
    - Number of product-related CS cases in `complaints` + `returns`
    - Complaints are connected to order_id → order_items → product_id

??? success "Answer"
    ```sql
    WITH top_products AS (
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            SUM(oi.quantity) AS total_sold
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.status NOT IN ('cancelled')
          AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
        GROUP BY p.id, p.name
        ORDER BY total_sold DESC
        LIMIT 30
    ),
    complaint_counts AS (
        SELECT
            oi.product_id,
            COUNT(DISTINCT comp.id) AS complaint_count
        FROM complaints AS comp
        INNER JOIN orders AS o ON comp.order_id = o.id
        INNER JOIN order_items AS oi ON o.id = oi.order_id
        WHERE comp.created_at LIKE '2024%'
        GROUP BY oi.product_id
    ),
    return_counts AS (
        SELECT
            oi.product_id,
            COUNT(DISTINCT ret.id) AS return_count
        FROM returns AS ret
        INNER JOIN order_items AS oi ON ret.order_id = oi.order_id
        WHERE ret.requested_at LIKE '2024%'
        GROUP BY oi.product_id
    )
    SELECT
        tp.product_name,
        tp.total_sold,
        COALESCE(cc.complaint_count, 0) AS complaints,
        COALESCE(rc.return_count, 0) AS returns,
        COALESCE(cc.complaint_count, 0) + COALESCE(rc.return_count, 0) AS total_cs,
        ROUND(100.0 * (COALESCE(cc.complaint_count, 0) + COALESCE(rc.return_count, 0))
            / tp.total_sold, 1) AS cs_rate_pct
    FROM top_products AS tp
    LEFT JOIN complaint_counts AS cc ON tp.product_id = cc.product_id
    LEFT JOIN return_counts AS rc ON tp.product_id = rc.product_id
    ORDER BY cs_rate_pct DESC;
    ```

    | product_name | total_sold | complaints | returns | total_cs | cs_rate_pct |
    |---|---|---|---|---|---|
    | (Problem Product A) | 120 | 15 | 12 | 27 | 22.5 |
    | (Problem Product B) | 85 | 8 | 10 | 18 | 21.2 |
    | (Normal Product C) | 200 | 5 | 3 | 8 | 4.0 |
    | ... | ... | ... | ... | ... | ... |


---

## Comprehensive dashboard (18~20)


### Problem 18. Daily operations dashboard

Create a dashboard that shows your operational status at a glance on a specific date (2024-12-15).
Includes number of same-day orders, sales, new subscribers, completed deliveries, and number of outstanding CS cases.


??? tip "Hint"
    - Calculate each indicator as a scalar subquery or CTE
    - Combine single rows with `CROSS JOIN`
    - It is more useful to include changes compared to the previous day.

??? success "Answer"
    ```sql
    WITH target_day AS (SELECT '2024-12-15' AS d),
    day_orders AS (
        SELECT
            COUNT(*) AS order_count,
            ROUND(SUM(total_amount)) AS revenue
        FROM orders, target_day
        WHERE DATE(ordered_at) = d
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    prev_orders AS (
        SELECT
            COUNT(*) AS order_count,
            ROUND(SUM(total_amount)) AS revenue
        FROM orders, target_day
        WHERE DATE(ordered_at) = DATE(d, '-1 day')
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    new_customers AS (
        SELECT COUNT(*) AS cnt
        FROM customers, target_day
        WHERE DATE(created_at) = d
    ),
    deliveries AS (
        SELECT COUNT(*) AS cnt
        FROM shipping, target_day
        WHERE DATE(delivered_at) = d
    ),
    open_cs AS (
        SELECT COUNT(*) AS cnt
        FROM complaints
        WHERE status = 'open'
    )
    SELECT
        (SELECT d FROM target_day) AS report_date,
        do.order_count AS today_orders,
        do.revenue AS today_revenue,
        po.order_count AS yesterday_orders,
        po.revenue AS yesterday_revenue,
        ROUND(100.0 * (do.revenue - po.revenue) / NULLIF(po.revenue, 0), 1) AS revenue_change_pct,
        nc.cnt AS new_signups,
        dl.cnt AS deliveries_completed,
        oc.cnt AS open_cs_tickets
    FROM day_orders AS do
    CROSS JOIN prev_orders AS po
    CROSS JOIN new_customers AS nc
    CROSS JOIN deliveries AS dl
    CROSS JOIN open_cs AS oc;
    ```

    | report_date | today_orders | today_revenue | yesterday_orders | yesterday_revenue | revenue_change_pct | new_signups | deliveries_completed | open_cs_tickets |
    |---|---|---|---|---|---|---|---|---|
    | 2024-12-15 | 65 | 42000000 | 58 | 38000000 | 10.5 | 12 | 52 | 35 |


---


### Problem 19. Comprehensive evaluation of suppliers

Evaluate each supplier’s overall performance.
Consolidate number of units supplied, total sales, return rate, average review rating, and inventory availability into one report.


??? tip "Hint"
    - `suppliers` → `products` → JOIN various tables
    - Return rate: Number of returns/number of sales of the supplier’s products
    - Inventory adequacy: Proportion of products with excess inventory (more than 180 days) or shortage (7 days or less)

??? success "Answer"
    ```sql
    WITH supplier_products AS (
        SELECT
            s.id AS supplier_id,
            s.company_name,
            COUNT(DISTINCT p.id) AS product_count,
            SUM(p.stock_qty) AS total_stock
        FROM suppliers AS s
        INNER JOIN products AS p ON s.id = p.supplier_id
        WHERE p.is_active = 1
        GROUP BY s.id, s.company_name
    ),
    supplier_sales AS (
        SELECT
            p.supplier_id,
            SUM(oi.quantity) AS total_sold,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS total_revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.supplier_id
    ),
    supplier_returns AS (
        SELECT
            p.supplier_id,
            COUNT(DISTINCT ret.id) AS return_count
        FROM returns AS ret
        INNER JOIN order_items AS oi ON ret.order_id = oi.order_id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE ret.requested_at >= '2024-01-01' AND ret.requested_at < '2025-01-01'
        GROUP BY p.supplier_id
    ),
    supplier_reviews AS (
        SELECT
            p.supplier_id,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(*) AS review_count
        FROM reviews AS r
        INNER JOIN products AS p ON r.product_id = p.id
        GROUP BY p.supplier_id
    )
    SELECT
        sp.company_name,
        sp.product_count,
        COALESCE(ss.total_revenue, 0) AS revenue_2024,
        COALESCE(ss.total_sold, 0) AS units_sold,
        ROUND(100.0 * COALESCE(sr.return_count, 0) / NULLIF(ss.total_sold, 0), 1) AS return_rate_pct,
        COALESCE(srv.avg_rating, 0) AS avg_rating,
        sp.total_stock
    FROM supplier_products AS sp
    LEFT JOIN supplier_sales AS ss ON sp.supplier_id = ss.supplier_id
    LEFT JOIN supplier_returns AS sr ON sp.supplier_id = sr.supplier_id
    LEFT JOIN supplier_reviews AS srv ON sp.supplier_id = srv.supplier_id
    ORDER BY revenue_2024 DESC;
    ```

    | company_name | product_count | revenue_2024 | units_sold | return_rate_pct | avg_rating | total_stock |
    |---|---|---|---|---|---|---|
    | TechSolution Inc. | 45 | 2500000000 | 3200 | 5.5 | 4.2 | 1500 |
    | Digital Partner | 38 | 2100000000 | 2800 | 4.2 | 4.0 | 1200 |
    | ... | ... | ... | ... | ... | ... | ... |


---


### Problem 20. Monthly Management Comprehensive Report (December 2024)

Create a comprehensive management report for December 2024.
Integrates key KPIs from four areas: sales, customers, inventory, and CS into one query.

| KPI Area | Metrics |
|---|---|
| Sales | Monthly revenue, MoM ratio, YoY same-month ratio |
| Customers | Active customer count, new signups, repeat purchase rate |
| Inventory | Out-of-stock product count, inventory value, low-stock alert count |
| CS | Unresolved cases, avg resolution time, resolution rate |


??? tip "Hint"
    - Write each area as a separate CTE and then CROSS JOIN
    - Calculate comparative period sales using subquery for previous month ratio/previous year same month ratio
    - Repurchase rate: The percentage of customers who ordered previously in that month

??? success "Answer"
    ```sql
    WITH sales_kpi AS (
        SELECT
            ROUND(SUM(CASE WHEN ordered_at LIKE '2024-12%' THEN total_amount ELSE 0 END)) AS dec_revenue,
            ROUND(SUM(CASE WHEN ordered_at LIKE '2024-11%' THEN total_amount ELSE 0 END)) AS nov_revenue,
            ROUND(SUM(CASE WHEN ordered_at LIKE '2023-12%' THEN total_amount ELSE 0 END)) AS dec_2023_revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND (ordered_at LIKE '2024-12%' OR ordered_at LIKE '2024-11%' OR ordered_at LIKE '2023-12%')
    ),
    customer_kpi AS (
        SELECT
            COUNT(DISTINCT CASE WHEN o.ordered_at LIKE '2024-12%' THEN o.customer_id END) AS active_customers,
            (SELECT COUNT(*) FROM customers WHERE created_at LIKE '2024-12%') AS new_signups,
            ROUND(100.0 * COUNT(DISTINCT CASE
                WHEN o.ordered_at LIKE '2024-12%'
                AND o.customer_id IN (
                    SELECT customer_id FROM orders
                    WHERE ordered_at < '2024-12-01'
                      AND status NOT IN ('cancelled', 'returned', 'return_requested')
                )
                THEN o.customer_id
            END) / NULLIF(COUNT(DISTINCT CASE WHEN o.ordered_at LIKE '2024-12%' THEN o.customer_id END), 0), 1)
                AS repeat_rate_pct
        FROM orders AS o
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    inventory_kpi AS (
        SELECT
            SUM(CASE WHEN stock_qty = 0 THEN 1 ELSE 0 END) AS out_of_stock_count,
            ROUND(SUM(stock_qty * cost_price)) AS total_stock_value,
            SUM(CASE WHEN stock_qty > 0 AND stock_qty <= 10 THEN 1 ELSE 0 END) AS low_stock_warning
        FROM products
        WHERE is_active = 1
    ),
    cs_kpi AS (
        SELECT
            SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open_tickets,
            ROUND(AVG(CASE
                WHEN resolved_at IS NOT NULL AND created_at LIKE '2024-12%'
                THEN JULIANDAY(resolved_at) - JULIANDAY(created_at)
            END), 2) AS avg_resolution_days,
            ROUND(100.0 * SUM(CASE
                WHEN created_at LIKE '2024-12%' AND status IN ('resolved', 'closed') THEN 1 ELSE 0 END)
                / NULLIF(SUM(CASE WHEN created_at LIKE '2024-12%' THEN 1 ELSE 0 END), 0), 1)
                AS resolution_rate_pct
        FROM complaints
    )
    SELECT
        '2024-12' AS report_month,
        -- Sales
        sk.dec_revenue,
        ROUND(100.0 * (sk.dec_revenue - sk.nov_revenue) / NULLIF(sk.nov_revenue, 0), 1) AS mom_growth_pct,
        ROUND(100.0 * (sk.dec_revenue - sk.dec_2023_revenue) / NULLIF(sk.dec_2023_revenue, 0), 1) AS yoy_growth_pct,
        -- Customers
        ck.active_customers,
        ck.new_signups,
        ck.repeat_rate_pct,
        -- Inventory
        ik.out_of_stock_count,
        ik.total_stock_value,
        ik.low_stock_warning,
        -- CS
        csk.open_tickets,
        csk.avg_resolution_days,
        csk.resolution_rate_pct
    FROM sales_kpi AS sk
    CROSS JOIN customer_kpi AS ck
    CROSS JOIN inventory_kpi AS ik
    CROSS JOIN cs_kpi AS csk;
    ```

    | report_month | dec_revenue | mom_growth_pct | yoy_growth_pct | active_customers | new_signups | repeat_rate_pct | out_of_stock_count | total_stock_value | low_stock_warning | open_tickets | avg_resolution_days | resolution_rate_pct |
    |---|---|---|---|---|---|---|---|---|---|---|---|---|
    | 2024-12 | 1250000000 | 15.2 | 12.8 | 3200 | 180 | 72.5 | 15 | 1800000000 | 25 | 35 | 1.5 | 82.0 |
