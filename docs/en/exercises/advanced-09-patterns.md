# Practical SQL Patterns

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `categories` — Categories (parent-child hierarchy)  

    `customers` — Customers (grade, points, channel)  

    `payments` — Payments (method, amount, status)  

    `calendar` — Calendar (weekday, holiday)  

    `product_views` — View log (customer, product, date)  

    `carts` — Carts (status)  

    `cart_items` — Cart items (quantity)  



!!! abstract "Concepts"

    `Top-N per Group`, `Gap Analysis`, `Pivot`, `Session Analysis`, `Pareto 80/20`, `Funnel`, `Consecutive Period Detection`



### 1. Top-3 sales products by category (ROW_NUMBER)


Extract the top 3 selling products in 2024 from each **bottom category** (depth = 2).
In case of identical sales, the product with the highest sales volume takes precedence.

| category | product_name | revenue | units_sold | rank |
|----------|-------------|---------|-----------|------|
| ... | ... | ... | ... | 1 |


**Hint 1:** - `ROW_NUMBER() OVER (PARTITION BY cat.id ORDER BY revenue DESC, units_sold DESC)`
- Rank by CTE and then filter by `WHERE rn <= 3`
- Targets only the lowest category with `categories.depth = 2`



??? success "Answer"
    ```sql
    WITH product_sales AS (
        SELECT
            cat.id   AS cat_id,
            cat.name AS category,
            p.name   AS product_name,
            SUM(oi.quantity * oi.unit_price) AS revenue,
            SUM(oi.quantity)                 AS units_sold
        FROM order_items   AS oi
        JOIN orders         AS o   ON oi.order_id   = o.id
        JOIN products       AS p   ON oi.product_id = p.id
        JOIN categories     AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
          AND o.ordered_at >= '2024-01-01'
          AND o.ordered_at <  '2025-01-01'
          AND cat.depth = 2
        GROUP BY cat.id, cat.name, p.id, p.name
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (
                PARTITION BY cat_id
                ORDER BY revenue DESC, units_sold DESC
            ) AS rn
        FROM product_sales
    )
    SELECT category, product_name,
           ROUND(revenue, 0) AS revenue,
           units_sold,
           rn AS rank
    FROM ranked
    WHERE rn <= 3
    ORDER BY category, rn;
    ```


---


### 2. Finding dates without orders (Gap Analysis)


Using the `calendar` table, find all **dates** in 2024 that did not have a single order.
Weekday/weekend classification and public holidays are also displayed.

| date_key | day_name | is_weekend | is_holiday | holiday_name |
|----------|----------|-----------|-----------|-------------|
| 2024-01-01 | Monday | 0 | 1 | New Year's Day |


**Hint 1:** - Check order availability based on any date with `calendar LEFT JOIN orders`
- Filter days without orders with `WHERE o.id IS NULL`
- `calendar.date_key BETWEEN '2024-01-01' AND '2024-12-31'`



??? success "Answer"
    ```sql
    SELECT
        cal.date_key,
        cal.day_name,
        cal.is_weekend,
        cal.is_holiday,
        cal.holiday_name
    FROM calendar AS cal
    LEFT JOIN orders AS o
        ON DATE(o.ordered_at) = cal.date_key
       AND o.status NOT IN ('cancelled')
    WHERE cal.date_key BETWEEN '2024-01-01' AND '2024-12-31'
      AND o.id IS NULL
    ORDER BY cal.date_key;
    ```


---


### 3. Sales pivot table by day of the week (CASE + SUM)


Display 2024 **month x day of week** sales in pivot format.
The rows are the months (YYYY-MM), and the columns are the seven days of the week (Mon-Sun).

| year_month | mon | tue | wed | thu | fri | sat | sun |
|------------|-----|-----|-----|-----|-----|-----|-----|
| 2024-01 | ... | ... | ... | ... | ... | ... | ... |


**Hint 1:** - `SUM(CASE WHEN STRFTIME('%w', ordered_at) = '1' THEN total_amount ELSE 0 END) AS mon`
- In SQLite’s `%w`, 0=Sun, 1=Mon, ..., 6=Sat
- Extract month: `SUBSTR(ordered_at, 1, 7)`



??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS year_month,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '1' THEN total_amount ELSE 0 END) AS INTEGER) AS mon,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '2' THEN total_amount ELSE 0 END) AS INTEGER) AS tue,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '3' THEN total_amount ELSE 0 END) AS INTEGER) AS wed,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '4' THEN total_amount ELSE 0 END) AS INTEGER) AS thu,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '5' THEN total_amount ELSE 0 END) AS INTEGER) AS fri,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '6' THEN total_amount ELSE 0 END) AS INTEGER) AS sat,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '0' THEN total_amount ELSE 0 END) AS INTEGER) AS sun
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at <  '2025-01-01'
      AND status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY year_month;
    ```


    **Result** (top 7 of 12 rows)

    | year_month | mon | tue | wed | thu | fri | sat | sun |
    |---|---|---|---|---|---|---|---|
    | 2024-01 | 40,764,141 | 44,602,205 | 26,410,593 | 20,436,018 | 56,605,231 | 43,280,158 | 56,809,974 |
    | 2024-02 | 67,387,251 | 43,032,032 | 60,487,619 | 48,877,254 | 71,804,613 | 54,551,823 | 56,987,157 |
    | 2024-03 | 70,180,297 | 67,897,538 | 62,691,902 | 58,905,080 | 71,182,311 | 76,903,414 | 112,083,960 |
    | 2024-04 | 74,561,175 | 59,707,159 | 69,537,704 | 77,984,882 | 46,198,503 | 57,318,794 | 66,569,364 |
    | 2024-05 | 36,746,395 | 56,164,229 | 70,892,739 | 42,604,957 | 67,015,276 | 62,260,346 | 89,580,536 |
    | 2024-06 | 54,376,757 | 45,870,213 | 38,061,084 | 42,811,574 | 42,127,592 | 64,215,372 | 75,252,619 |
    | 2024-07 | 41,682,991 | 57,833,464 | 28,230,471 | 53,964,486 | 59,101,476 | 65,949,332 | 37,167,677 |


---


### 4. Running Percentage


Find the sales by product in 2024 and calculate the **cumulative sales ratio (%)** in descending order of sales.
It even displays products that account for 80% of total sales.

| product_name | revenue | pct | cumulative_pct |
|-------------|---------|-----|---------------|
| ... | ... | 12.3 | 12.3 |
| ... | ... | 8.5 | 20.8 |


**Hint 1:** - `SUM(revenue) OVER (ORDER BY revenue DESC)` / Calculate cumulative percentage with overall total
- CTE Step 1: Total sales by product
- CTE Step 2: After calculating the cumulative ratio `WHERE cumulative_pct <= 80`



??? success "Answer"
    ```sql
    WITH product_rev AS (
        SELECT
            p.name AS product_name,
            SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items AS oi
        JOIN orders   AS o ON oi.order_id   = o.id
        JOIN products AS p ON oi.product_id = p.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
          AND o.ordered_at >= '2024-01-01'
          AND o.ordered_at <  '2025-01-01'
        GROUP BY p.id, p.name
    ),
    cumulative AS (
        SELECT
            product_name,
            ROUND(revenue, 0) AS revenue,
            ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS pct,
            ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC)
                / SUM(revenue) OVER (), 2) AS cumulative_pct
        FROM product_rev
    )
    SELECT product_name, revenue, pct, cumulative_pct
    FROM cumulative
    WHERE cumulative_pct <= 80
    ORDER BY revenue DESC;
    ```


    **Result** (top 7 of 88 rows)

    | product_name | revenue | pct | cumulative_pct |
    |---|---|---|---|
    | Razer Blade 18 Black | 165,417,800.00 | 3.21 | 3.21 |
    | Razer Blade 16 Silver | 137,007,300.00 | 2.65 | 5.86 |
    | MacBook Air 15 M3 Silver | 126,065,300.00 | 2.44 | 8.30 |
    | ASUS Dual RTX 4060 Ti Black | 106,992,000.00 | 2.07 | 10.38 |
    | ASUS Dual RTX 5070 Ti Silver | 104,558,400.00 | 2.03 | 12.40 |
    | ASUS ROG Swift PG32UCDM Silver | 90,734,400.00 | 1.76 | 14.16 |
    | ASUS ROG Strix Scar 16 | 85,837,500.00 | 1.66 | 15.82 |


---


### 5. Monthly proportion change by payment method


Please show the trend in the percentage of monthly payment amount by **payment method** in 2024.
Calculate the share of your payment method in each month.

| year_month | card_pct | bank_transfer_pct | kakao_pay_pct | naver_pay_pct | other_pct |
|------------|---------|------------------|-------------|-------------|----------|
| 2024-01 | 62.3 | 15.1 | 12.0 | 8.5 | 2.1 |


**Hint 1:** - Total by means with `CASE WHEN method = 'card' THEN amount ELSE 0 END`
- Calculate proportion by dividing the total of each method by the total monthly total
- Minor payment methods (virtual_account, point) are grouped with ‘other’



??? success "Answer"
    ```sql
    SELECT
        SUBSTR(p.paid_at, 1, 7) AS year_month,
        ROUND(100.0 * SUM(CASE WHEN p.method = 'card' THEN p.amount ELSE 0 END)
            / SUM(p.amount), 1) AS card_pct,
        ROUND(100.0 * SUM(CASE WHEN p.method = 'bank_transfer' THEN p.amount ELSE 0 END)
            / SUM(p.amount), 1) AS bank_transfer_pct,
        ROUND(100.0 * SUM(CASE WHEN p.method = 'kakao_pay' THEN p.amount ELSE 0 END)
            / SUM(p.amount), 1) AS kakao_pay_pct,
        ROUND(100.0 * SUM(CASE WHEN p.method = 'naver_pay' THEN p.amount ELSE 0 END)
            / SUM(p.amount), 1) AS naver_pay_pct,
        ROUND(100.0 * SUM(CASE WHEN p.method NOT IN ('card','bank_transfer','kakao_pay','naver_pay')
            THEN p.amount ELSE 0 END) / SUM(p.amount), 1) AS other_pct
    FROM payments AS p
    WHERE p.status = 'completed'
      AND p.paid_at >= '2024-01-01'
      AND p.paid_at <  '2025-01-01'
    GROUP BY SUBSTR(p.paid_at, 1, 7)
    ORDER BY year_month;
    ```


    **Result** (top 7 of 12 rows)

    | year_month | card_pct | bank_transfer_pct | kakao_pay_pct | naver_pay_pct | other_pct |
    |---|---|---|---|---|---|
    | 2024-01 | 51.00 | 8.40 | 18.40 | 11.50 | 10.70 |
    | 2024-02 | 42.10 | 7.00 | 18.60 | 20.00 | 12.30 |
    | 2024-03 | 40.40 | 8.80 | 22.30 | 15.80 | 12.70 |
    | 2024-04 | 46.10 | 10.20 | 22.50 | 11.50 | 9.60 |
    | 2024-05 | 55.20 | 7.40 | 16.80 | 12.60 | 8.00 |
    | 2024-06 | 51.30 | 8.10 | 21.40 | 10.50 | 8.60 |
    | 2024-07 | 54.20 | 10.60 | 16.70 | 10.90 | 7.60 |


---


### 6. Session analysis: based on 30-minute intervals (product_views)


Identify **browsing sessions** by customer in the `product_views` table.
If there is more than 30 minutes between the previous view, it is considered a new session.
Find the number of sessions per customer, average number of views per session, and average session duration in minutes.

| customer_id | total_sessions | avg_views_per_session | avg_session_minutes |
|------------|---------------|----------------------|-------------------|
| ... | ... | ... | ... |


**Hint 1:** - Refer to previous inquiry time with `LAG(viewed_at) OVER (PARTITION BY customer_id ORDER BY viewed_at)`
- If interval > 1800 seconds, start new session (`julianday` difference * 86400)
- Assign session number to `SUM(is_new_session) OVER (PARTITION BY customer_id ORDER BY viewed_at)`



??? success "Answer"
    ```sql
    WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
            CASE
                WHEN (julianday(viewed_at) - julianday(
                    LAG(viewed_at) OVER (PARTITION BY customer_id ORDER BY viewed_at)
                )) * 86400 > 1800
                OR LAG(viewed_at) OVER (PARTITION BY customer_id ORDER BY viewed_at) IS NULL
                THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
    ),
    sessions AS (
        SELECT
            customer_id,
            viewed_at,
            SUM(is_new_session) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS session_id
        FROM view_gaps
    ),
    session_stats AS (
        SELECT
            customer_id,
            session_id,
            COUNT(*) AS view_count,
            ROUND((julianday(MAX(viewed_at)) - julianday(MIN(viewed_at))) * 1440, 1) AS session_minutes
        FROM sessions
        GROUP BY customer_id, session_id
    )
    SELECT
        customer_id,
        COUNT(*) AS total_sessions,
        ROUND(AVG(view_count), 1) AS avg_views_per_session,
        ROUND(AVG(session_minutes), 1) AS avg_session_minutes
    FROM session_stats
    GROUP BY customer_id
    HAVING COUNT(*) >= 3
    ORDER BY total_sessions DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | customer_id | total_sessions | avg_views_per_session | avg_session_minutes |
    |---|---|---|---|
    | 97 | 2613 | 1.00 | 0.5 |
    | 226 | 2300 | 1.00 | 0.5 |
    | 98 | 1838 | 1.10 | 0.5 |
    | 162 | 1788 | 1.00 | 0.6 |
    | 227 | 1730 | 1.10 | 0.6 |
    | 549 | 1725 | 1.00 | 0.7 |
    | 356 | 1695 | 1.10 | 0.6 |


---


### 7. Consecutive Days


Find the top 10 customers with the most **number of consecutive days ordering** in 2024.
Consecutive orders mean that the days run consecutively without missing a single day.

| customer_name | consecutive_days | streak_start | streak_end |
|-------------|-----------------|------------|----------|
| ... | 5 | 2024-11-25 | 2024-11-29 |


**Hint 1:** - Subtracting `ROW_NUMBER()` from `DATE(ordered_at)` ensures that consecutive groups have the same value.
- `DATE(ordered_at, '-' || ROW_NUMBER() || ' days')` pattern
- There may be multiple orders on the same day, so process `DISTINCT DATE(ordered_at)` first



??? success "Answer"
    ```sql
    WITH daily_orders AS (
        SELECT DISTINCT
            customer_id,
            DATE(ordered_at) AS order_date
        FROM orders
        WHERE ordered_at >= '2024-01-01'
          AND ordered_at <  '2025-01-01'
          AND status NOT IN ('cancelled')
    ),
    numbered AS (
        SELECT
            customer_id,
            order_date,
            DATE(order_date, '-' || (ROW_NUMBER() OVER (
                PARTITION BY customer_id ORDER BY order_date
            ) - 1) || ' days') AS grp
        FROM daily_orders
    ),
    streaks AS (
        SELECT
            customer_id,
            grp,
            COUNT(*) AS consecutive_days,
            MIN(order_date) AS streak_start,
            MAX(order_date) AS streak_end
        FROM numbered
        GROUP BY customer_id, grp
        HAVING COUNT(*) >= 2
    )
    SELECT
        c.name AS customer_name,
        s.consecutive_days,
        s.streak_start,
        s.streak_end
    FROM streaks AS s
    JOIN customers AS c ON s.customer_id = c.id
    ORDER BY s.consecutive_days DESC, s.streak_start
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | customer_name | consecutive_days | streak_start | streak_end |
    |---|---|---|---|
    | Tiffany Graham | 3 | 2024-02-01 | 2024-02-03 |
    | Stephanie Berry | 3 | 2024-02-22 | 2024-02-24 |
    | Sean Mclean | 3 | 2024-03-25 | 2024-03-27 |
    | Katherine Baker | 3 | 2024-03-27 | 2024-03-29 |
    | Wendy Jones | 3 | 2024-11-24 | 2024-11-26 |
    | Ronald Gallagher | 2 | 2024-01-10 | 2024-01-11 |
    | Christy Tucker | 2 | 2024-01-17 | 2024-01-18 |


---


### 8. Pareto analysis: Proportion of customers generating 80% of sales


Perform a Pareto analysis to determine which **top percent of customers account for 80% of sales**.
Sort customers by sales and get cumulative percentage.

| customer_name | total_spent | pct_of_revenue | cumulative_pct | customer_rank | total_customers | customer_pct |
|-------------|-----------|---------------|---------------|-------------|----------------|-------------|


**Hint 1:** - Total sales by customer → Sort in descending order of sales
- `SUM(total_spent) OVER (ORDER BY total_spent DESC)` / total total
- Customer rank ratio as `ROW_NUMBER()` / `COUNT(*) OVER ()`



??? success "Answer"
    ```sql
    WITH customer_revenue AS (
        SELECT
            c.id,
            c.name AS customer_name,
            SUM(o.total_amount) AS total_spent
        FROM orders AS o
        JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name
    ),
    pareto AS (
        SELECT
            customer_name,
            CAST(total_spent AS INTEGER) AS total_spent,
            ROUND(100.0 * total_spent / SUM(total_spent) OVER (), 2) AS pct_of_revenue,
            ROUND(100.0 * SUM(total_spent) OVER (ORDER BY total_spent DESC)
                / SUM(total_spent) OVER (), 2) AS cumulative_pct,
            ROW_NUMBER() OVER (ORDER BY total_spent DESC) AS customer_rank,
            COUNT(*) OVER () AS total_customers
        FROM customer_revenue
    )
    SELECT
        customer_name,
        total_spent,
        pct_of_revenue,
        cumulative_pct,
        customer_rank,
        total_customers,
        ROUND(100.0 * customer_rank / total_customers, 1) AS customer_pct
    FROM pareto
    WHERE cumulative_pct <= 80
    ORDER BY customer_rank;
    ```


    **Result** (top 7 of 754 rows)

    | customer_name | total_spent | pct_of_revenue | cumulative_pct | customer_rank | total_customers | customer_pct |
    |---|---|---|---|---|---|---|
    | Allen Snyder | 403,448,758 | 1.16 | 1.16 | 1 | 2793 | 0.0 |
    | Jason Rivera | 366,385,931 | 1.05 | 2.21 | 2 | 2793 | 0.1 |
    | Brenda Garcia | 253,180,338 | 0.73 | 2.94 | 3 | 2793 | 0.1 |
    | Courtney Huff | 244,604,910 | 0.7 | 3.65 | 4 | 2793 | 0.1 |
    | Ronald Arellano | 235,775,349 | 0.68 | 4.32 | 5 | 2793 | 0.2 |
    | James Banks | 234,708,853 | 0.68 | 5.00 | 6 | 2793 | 0.2 |
    | Gabriel Walters | 230,165,991 | 0.66 | 5.66 | 7 | 2793 | 0.3 |


---


### 9. Churn rate analysis by grade (Churn)


Find the percentage (churn rate) of **customers who have had no orders within the last 6 months (2025-01-01 ~ 2025-06-30) by customer level.
Displays the total number of customers by level, number of active customers, number of abandoned customers, and bounce rate.

| grade | total_customers | active_customers | churned_customers | churn_rate_pct |
|-------|----------------|-----------------|------------------|---------------|
| VIP | ... | ... | ... | ... |


**Hint 1:** - In `customers LEFT JOIN orders`, classify as active/deactivated based on order date condition.
- Active if there is an order within 6 months, discontinued if not
- Conditional count with `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`



??? success "Answer"
    ```sql
    WITH customer_activity AS (
        SELECT
            c.id,
            c.grade,
            MAX(o.ordered_at) AS last_order_at
        FROM customers AS c
        LEFT JOIN orders AS o
            ON c.id = o.customer_id
           AND o.status NOT IN ('cancelled')
        WHERE c.is_active = 1
        GROUP BY c.id, c.grade
    )
    SELECT
        grade,
        COUNT(*) AS total_customers,
        SUM(CASE WHEN last_order_at >= '2025-01-01' THEN 1 ELSE 0 END) AS active_customers,
        SUM(CASE WHEN last_order_at < '2025-01-01' OR last_order_at IS NULL THEN 1 ELSE 0 END) AS churned_customers,
        ROUND(100.0 * SUM(CASE WHEN last_order_at < '2025-01-01' OR last_order_at IS NULL THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS churn_rate_pct
    FROM customer_activity
    GROUP BY grade
    ORDER BY
        CASE grade WHEN 'VIP' THEN 1 WHEN 'GOLD' THEN 2 WHEN 'SILVER' THEN 3 ELSE 4 END;
    ```


    **Result** (4 rows)

    | grade | total_customers | active_customers | churned_customers | churn_rate_pct |
    |---|---|---|---|---|
    | VIP | 368 | 368 | 0 | 0.0 |
    | GOLD | 524 | 524 | 0 | 0.0 |
    | SILVER | 479 | 477 | 2 | 0.4 |
    | BRONZE | 2289 | 668 | 1621 | 70.80 |


---


### 10. Analysis of shopping cart → order conversion time


For cases where the shopping cart (`carts`) status is 'converted', analyze **the time taken from creating the shopping cart to ordering**.
Find the average/median/min/max conversion time (in hours) and the average conversion time by day of the week.

| day_name | avg_hours | min_hours | max_hours | converted_count |
|----------|----------|----------|----------|----------------|


**Hint 1:** - Match the closest order with `customer_id` and `created_at` in the 'converted' shopping cart.
- Calculate time as `julianday(o.ordered_at) - julianday(c.created_at)` * 24
- Separate days by `STRFTIME('%w', c.created_at)`



??? success "Answer"
    ```sql
    WITH converted_carts AS (
        SELECT
            ca.id AS cart_id,
            ca.customer_id,
            ca.created_at AS cart_created,
            MIN(o.ordered_at) AS first_order_after
        FROM carts AS ca
        JOIN orders AS o
            ON ca.customer_id = o.customer_id
           AND o.ordered_at >= ca.created_at
           AND o.status NOT IN ('cancelled')
        WHERE ca.status = 'converted'
        GROUP BY ca.id, ca.customer_id, ca.created_at
    ),
    hours_calc AS (
        SELECT
            cart_id,
            ROUND((julianday(first_order_after) - julianday(cart_created)) * 24, 1) AS hours_to_convert,
            CASE CAST(STRFTIME('%w', cart_created) AS INTEGER)
                WHEN 0 THEN 'Sun' WHEN 1 THEN 'Mon' WHEN 2 THEN 'Tue'
                WHEN 3 THEN 'Wed' WHEN 4 THEN 'Thu' WHEN 5 THEN 'Fri' WHEN 6 THEN 'Sat'
            END AS day_name,
            CAST(STRFTIME('%w', cart_created) AS INTEGER) AS dow
        FROM converted_carts
    )
    SELECT
        day_name,
        ROUND(AVG(hours_to_convert), 1) AS avg_hours,
        ROUND(MIN(hours_to_convert), 1) AS min_hours,
        ROUND(MAX(hours_to_convert), 1) AS max_hours,
        COUNT(*) AS converted_count
    FROM hours_calc
    GROUP BY day_name, dow
    ORDER BY dow;
    ```


    **Result** (7 rows)

    | day_name | avg_hours | min_hours | max_hours | converted_count |
    |---|---|---|---|---|
    | Sun | 3,439.30 | 9.40 | 24,098.00 | 125 |
    | Mon | 3,719.50 | 0.9 | 34,589.40 | 132 |
    | Tue | 3,623.20 | 26.20 | 20,473.50 | 116 |
    | Wed | 3,547.80 | 11.60 | 30,182.70 | 119 |
    | Thu | 4,071.40 | 2.60 | 28,918.00 | 125 |
    | Fri | 4,224.40 | 14.70 | 27,035.30 | 115 |
    | Sat | 3,862.80 | 3.20 | 38,807.50 | 137 |


---


### 11. Purchase funnel analysis (View → Cart → Order)


Analyze the 3-stage funnel of **Product inquiry → Add to cart → Order**.
Calculate the number of unique customers and conversion rate (%) for each stage based on 2024 data.

| funnel_step | unique_customers | conversion_rate_pct |
|------------|-----------------|-------------------|
| 1. View | 1500 | 100.0 |
| 2. Cart | 800 | 53.3 |
| 3. Order | 600 | 75.0 |


**Hint 1:** - Step 1: Number of unique customers in `product_views`
- Step 2: Number of unique customers in `cart_items → carts`
- Step 3: Number of unique customers in `orders`
- Conversion rate: current step / previous step * 100
- Combine 3 steps into one result with `UNION ALL`



??? success "Answer"
    ```sql
    WITH step_viewers AS (
        SELECT COUNT(DISTINCT customer_id) AS cnt
        FROM product_views
        WHERE viewed_at >= '2024-01-01' AND viewed_at < '2025-01-01'
    ),
    step_carters AS (
        SELECT COUNT(DISTINCT ca.customer_id) AS cnt
        FROM carts AS ca
        JOIN cart_items AS ci ON ca.id = ci.cart_id
        WHERE ci.added_at >= '2024-01-01' AND ci.added_at < '2025-01-01'
          AND ca.customer_id IN (
              SELECT DISTINCT customer_id
              FROM product_views
              WHERE viewed_at >= '2024-01-01' AND viewed_at < '2025-01-01'
          )
    ),
    step_buyers AS (
        SELECT COUNT(DISTINCT o.customer_id) AS cnt
        FROM orders AS o
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled')
          AND o.customer_id IN (
              SELECT DISTINCT ca.customer_id
              FROM carts AS ca
              JOIN cart_items AS ci ON ca.id = ci.cart_id
              WHERE ci.added_at >= '2024-01-01' AND ci.added_at < '2025-01-01'
          )
    ),
    funnel AS (
        SELECT 1 AS step, '1. View' AS funnel_step, cnt FROM step_viewers
        UNION ALL
        SELECT 2, '2. Cart', cnt FROM step_carters
        UNION ALL
        SELECT 3, '3. Order', cnt FROM step_buyers
    )
    SELECT
        funnel_step,
        cnt AS unique_customers,
        ROUND(100.0 * cnt / LAG(cnt) OVER (ORDER BY step), 1) AS conversion_rate_pct
    FROM funnel
    ORDER BY step;
    ```


    **Result** (3 rows)

    | funnel_step | unique_customers | conversion_rate_pct |
    |---|---|---|
    | 1. View | 2809 | NULL |
    | 2. Cart | 517 | 18.40 |
    | 3. Order | 311 | 60.20 |


---


### 12. Deduplication of duplicate data


If the same customer writes multiple reviews for the same product **on the same day**,
Keep only the most recent review and identify the ids of the rest.
(Extracts the list of IDs to be deleted without an actual DELETE.)

| duplicate_review_id | customer_name | product_name | created_at | keep_review_id |
|-------------------|-------------|-------------|-----------|---------------|


**Hint 1:** - Assign `rn = 1` to the latest one with `ROW_NUMBER() OVER (PARTITION BY customer_id, product_id, DATE(created_at) ORDER BY created_at DESC)`
- Rows with `rn > 1` are targeted for deletion.
- Display the ID of the row with `rn = 1` in the same partition as keep_review_id



??? success "Answer"
    ```sql
    WITH ranked_reviews AS (
        SELECT
            r.id,
            r.customer_id,
            r.product_id,
            r.created_at,
            ROW_NUMBER() OVER (
                PARTITION BY r.customer_id, r.product_id, DATE(r.created_at)
                ORDER BY r.created_at DESC
            ) AS rn,
            FIRST_VALUE(r.id) OVER (
                PARTITION BY r.customer_id, r.product_id, DATE(r.created_at)
                ORDER BY r.created_at DESC
            ) AS keep_id
        FROM reviews AS r
    )
    SELECT
        rr.id AS duplicate_review_id,
        c.name AS customer_name,
        p.name AS product_name,
        rr.created_at,
        rr.keep_id AS keep_review_id
    FROM ranked_reviews AS rr
    JOIN customers AS c ON rr.customer_id = c.id
    JOIN products  AS p ON rr.product_id  = p.id
    WHERE rr.rn > 1
    ORDER BY rr.customer_id, rr.product_id, rr.created_at;
    ```


---


### 13. Supplier dependence analysis


Find the proportion of each **supplier** in total sales,
Classify suppliers with more than 10% of sales as **high risk dependent**.
We also analyze the number of products, sales, proportion, and return rate.

| supplier | product_count | revenue | revenue_pct | return_rate_pct | risk_level |
|----------|-------------|---------|-----------|----------------|-----------|
| ... | ... | ... | 15.2 | 3.1 | HIGH |


**Hint 1:** - Sum up sales by supplier with `products → suppliers`
- Return rate: Number of returns/number of orders for the supplier’s products
- `CASE WHEN revenue_pct >= 10 THEN 'HIGH' ... END`



??? success "Answer"
    ```sql
    WITH supplier_sales AS (
        SELECT
            s.id AS supplier_id,
            s.company_name AS supplier,
            COUNT(DISTINCT p.id) AS product_count,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM suppliers AS s
        LEFT JOIN products AS p ON s.id = p.supplier_id
        LEFT JOIN order_items AS oi ON p.id = oi.product_id
        LEFT JOIN orders AS o ON oi.order_id = o.id
            AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY s.id, s.company_name
    ),
    supplier_returns AS (
        SELECT
            p.supplier_id,
            COUNT(DISTINCT r.id) AS return_count,
            COUNT(DISTINCT o.id) AS order_count
        FROM products AS p
        JOIN order_items AS oi ON p.id = oi.product_id
        JOIN orders AS o ON oi.order_id = o.id
        LEFT JOIN returns AS r ON o.id = r.order_id
        GROUP BY p.supplier_id
    )
    SELECT
        ss.supplier,
        ss.product_count,
        CAST(ss.revenue AS INTEGER) AS revenue,
        ROUND(100.0 * ss.revenue / NULLIF(SUM(ss.revenue) OVER (), 0), 1) AS revenue_pct,
        ROUND(100.0 * COALESCE(sr.return_count, 0) / NULLIF(sr.order_count, 0), 1) AS return_rate_pct,
        CASE
            WHEN 100.0 * ss.revenue / NULLIF(SUM(ss.revenue) OVER (), 0) >= 10 THEN 'HIGH'
            WHEN 100.0 * ss.revenue / NULLIF(SUM(ss.revenue) OVER (), 0) >= 5  THEN 'MEDIUM'
            ELSE 'LOW'
        END AS risk_level
    FROM supplier_sales AS ss
    LEFT JOIN supplier_returns AS sr ON ss.supplier_id = sr.supplier_id
    WHERE ss.revenue > 0
    ORDER BY ss.revenue DESC;
    ```


    **Result** (top 7 of 45 rows)

    | supplier | product_count | revenue | revenue_pct | return_rate_pct | risk_level |
    |---|---|---|---|---|---|
    | ASUS Corp. | 26 | 6,239,864,300 | 16.20 | 3.50 | HIGH |
    | Razer Corp. | 9 | 4,203,062,600 | 10.90 | 4.10 | HIGH |
    | Samsung Official Distribution | 25 | 3,028,089,900 | 7.90 | 2.90 | MEDIUM |
    | MSI Corp. | 13 | 2,815,063,400 | 7.30 | 3.50 | MEDIUM |
    | LG Official Distribution | 11 | 2,240,909,900 | 5.80 | 3.60 | MEDIUM |
    | ASRock Corp. | 11 | 1,756,828,300 | 4.60 | 3.30 | LOW |
    | Intel Corp. | 6 | 1,281,251,700 | 3.30 | 3.20 | LOW |


---


### 14. Cohort retention matrix (based on month of subscription)


Cohorts are formed based on the customer’s **subscription month**,
Please show us the percentage of customers who repurchased 1 to 6 months after signing up (retention) in a matrix.
This cohort is eligible for enrollment in the first half of 2024 (January to June).

| cohort | cohort_size | m1_pct | m2_pct | m3_pct | m4_pct | m5_pct | m6_pct |
|--------|-----------|-------|-------|-------|-------|-------|-------|
| 2024-01 | 150 | 45.0 | 32.0 | 28.5 | ... | ... | ... |


**Hint 1:** - Cohort: `SUBSTR(c.created_at, 1, 7)` = joining month
- Active flag: Check if there is an order N months after signing up
- Calculate monthly difference: `CAST((julianday(SUBSTR(o.ordered_at,1,7)||'-01') - julianday(SUBSTR(c.created_at,1,7)||'-01')) / 30 AS INTEGER)`



??? success "Answer"
    ```sql
    WITH cohorts AS (
        SELECT
            c.id AS customer_id,
            SUBSTR(c.created_at, 1, 7) AS cohort
        FROM customers AS c
        WHERE c.created_at >= '2024-01-01'
          AND c.created_at <  '2024-07-01'
    ),
    order_months AS (
        SELECT DISTINCT
            co.customer_id,
            co.cohort,
            CAST(
                (julianday(SUBSTR(o.ordered_at, 1, 7) || '-01')
               - julianday(co.cohort || '-01')) / 30
            AS INTEGER) AS month_offset
        FROM cohorts AS co
        JOIN orders AS o ON co.customer_id = o.customer_id
        WHERE o.status NOT IN ('cancelled')
          AND o.ordered_at >= '2024-01-01'
    )
    SELECT
        cohort,
        COUNT(DISTINCT customer_id) AS cohort_size,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 1 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m1_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 2 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m2_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 3 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m3_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 4 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m4_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 5 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m5_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 6 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m6_pct
    FROM (
        SELECT DISTINCT customer_id, cohort FROM cohorts
    ) AS base
    LEFT JOIN order_months AS om USING (customer_id, cohort)
    GROUP BY cohort
    ORDER BY cohort;
    ```


    **Result** (6 rows)

    | cohort | cohort_size | m1_pct | m2_pct | m3_pct | m4_pct | m5_pct | m6_pct |
    |---|---|---|---|---|---|---|---|
    | 2024-01 | 52 | 5.80 | 9.60 | 7.70 | 3.80 | 3.80 | 3.80 |
    | 2024-02 | 48 | 0.0 | 6.30 | 10.40 | 8.30 | 6.30 | 10.40 |
    | 2024-03 | 71 | 14.10 | 15.50 | 2.80 | 12.70 | 14.10 | 14.10 |
    | 2024-04 | 53 | 7.50 | 7.50 | 3.80 | 17.00 | 11.30 | 18.90 |
    | 2024-05 | 43 | 9.30 | 16.30 | 4.70 | 18.60 | 9.30 | 18.60 |
    | 2024-06 | 68 | 5.90 | 5.90 | 8.80 | 10.30 | 11.80 | 8.80 |


---


### 15. Comprehensive Dashboard: Executive KPI Snapshot


Create a **December 2024 Executive Dashboard** to report to the CEO in a single query.
Print the following KPIs in one line:

- Total sales, growth rate compared to the previous month (%)
- Total number of orders, number of new customers, number of repeat customers
- Average order amount, average delivery time
- Return rate (%), number of CS inquiries

| revenue | mom_growth_pct | order_count | new_customers | repeat_customers | avg_order_value | avg_delivery_days | return_rate_pct | cs_tickets |
|---------|---------------|------------|-------------|-----------------|----------------|------------------|----------------|-----------|


**Hint 1:** - Obtain aggregates from multiple tables using subqueries/CTEs and then combine them into one row with `CROSS JOIN`
- Previous month’s sales are separately CTE as `WHERE ordered_at LIKE '2024-11%'`
- New customers: Customers who place their first order in December 2024
- Repurchase: Customers with an order history before December



??? success "Answer"
    ```sql
    WITH dec_orders AS (
        SELECT *
        FROM orders
        WHERE ordered_at >= '2024-12-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    nov_revenue AS (
        SELECT SUM(total_amount) AS rev
        FROM orders
        WHERE ordered_at >= '2024-11-01' AND ordered_at < '2024-12-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    dec_sales AS (
        SELECT
            SUM(total_amount) AS revenue,
            COUNT(*) AS order_count,
            ROUND(AVG(total_amount), 0) AS avg_order_value
        FROM dec_orders
    ),
    dec_customers AS (
        SELECT
            COUNT(DISTINCT CASE
                WHEN NOT EXISTS (
                    SELECT 1 FROM orders o2
                    WHERE o2.customer_id = d.customer_id
                      AND o2.ordered_at < '2024-12-01'
                      AND o2.status NOT IN ('cancelled')
                )
                THEN d.customer_id
            END) AS new_customers,
            COUNT(DISTINCT CASE
                WHEN EXISTS (
                    SELECT 1 FROM orders o2
                    WHERE o2.customer_id = d.customer_id
                      AND o2.ordered_at < '2024-12-01'
                      AND o2.status NOT IN ('cancelled')
                )
                THEN d.customer_id
            END) AS repeat_customers
        FROM dec_orders AS d
    ),
    dec_shipping AS (
        SELECT ROUND(AVG(julianday(sh.delivered_at) - julianday(sh.shipped_at)), 1) AS avg_delivery_days
        FROM shipping AS sh
        JOIN orders AS o ON sh.order_id = o.id
        WHERE o.ordered_at >= '2024-12-01' AND o.ordered_at < '2025-01-01'
          AND sh.delivered_at IS NOT NULL
    ),
    dec_returns AS (
        SELECT
            ROUND(100.0 * COUNT(DISTINCT r.id) / NULLIF(COUNT(DISTINCT o.id), 0), 1) AS return_rate_pct
        FROM orders AS o
        LEFT JOIN returns AS r ON o.id = r.order_id
        WHERE o.ordered_at >= '2024-12-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled')
    ),
    dec_cs AS (
        SELECT COUNT(*) AS cs_tickets
        FROM complaints
        WHERE created_at >= '2024-12-01' AND created_at < '2025-01-01'
    )
    SELECT
        CAST(ds.revenue AS INTEGER) AS revenue,
        ROUND(100.0 * (ds.revenue - nr.rev) / nr.rev, 1) AS mom_growth_pct,
        ds.order_count,
        dc.new_customers,
        dc.repeat_customers,
        ds.avg_order_value,
        dsh.avg_delivery_days,
        dr.return_rate_pct,
        dcs.cs_tickets
    FROM dec_sales AS ds
    CROSS JOIN nov_revenue AS nr
    CROSS JOIN dec_customers AS dc
    CROSS JOIN dec_shipping AS dsh
    CROSS JOIN dec_returns AS dr
    CROSS JOIN dec_cs AS dcs;
    ```


    **Result** (1 rows)

    | revenue | mom_growth_pct | order_count | new_customers | repeat_customers | avg_order_value | avg_delivery_days | return_rate_pct | cs_tickets |
    |---|---|---|---|---|---|---|---|---|
    | 417,148,762 | -23.20 | 459 | 37 | 342 | 908,821.00 | 2.50 | 3.20 | 48 |


---
