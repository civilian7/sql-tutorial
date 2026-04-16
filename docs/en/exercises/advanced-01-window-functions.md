# Window Functions Practice

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `customers` — Customers (grade, points, channel)  

    `reviews` — Reviews (rating, content)  

    `payments` — Payments (method, amount, status)  

    `categories` — Categories (parent-child hierarchy)  



!!! abstract "Concepts"

    `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `LAG`, `LEAD`, `SUM OVER`, `AVG OVER`, `FIRST_VALUE`, `LAST_VALUE`, `ROWS BETWEEN`



### 1. Sort each customer's orders in chronological order and number the orders for each customer.


Displays customer ID, customer name, order number, order date, order amount, and order number (`order_seq`) within the customer.
Print only the top 20 rows.


**Hint 1:** Use `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`.
Group by customer with `PARTITION BY customer_id` and sort chronologically with `ORDER BY ordered_at`.



??? success "Answer"
    ```sql
    SELECT
        c.id             AS customer_id,
        c.name           AS customer_name,
        o.order_number,
        o.ordered_at,
        o.total_amount,
        ROW_NUMBER() OVER (
            PARTITION BY c.id
            ORDER BY o.ordered_at
        ) AS order_seq
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY c.id, order_seq
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | customer_id | customer_name | order_number | ordered_at | total_amount | order_seq |
    |---|---|---|---|---|---|
    | 2 | Danny Johnson | ORD-20160807-00243 | 2016-08-17 23:29:34 | 2,413,300.00 | 1 |
    | 2 | Danny Johnson | ORD-20160802-00236 | 2016-08-19 22:29:34 | 298,500.00 | 2 |
    | 2 | Danny Johnson | ORD-20160830-00269 | 2016-08-30 10:49:39 | 445,700.00 | 3 |
    | 2 | Danny Johnson | ORD-20160904-00274 | 2016-09-04 08:47:04 | 597,000.00 | 4 |
    | 2 | Danny Johnson | ORD-20160915-00287 | 2016-09-15 20:07:17 | 1,760,400.00 | 5 |
    | 2 | Danny Johnson | ORD-20161024-00334 | 2016-10-24 12:13:06 | 131,500.00 | 6 |
    | 2 | Danny Johnson | ORD-20161101-00343 | 2016-11-01 10:44:08 | 323,500.00 | 7 |


---


### 2. Ranking monthly sales for 2024. If the sales are the same, the same ranking is given.


Total sales for each month, display both `RANK` and `DENSE_RANK` values ​​to compare the differences.


**Hint 1:** First, create a subquery (or CTE) that aggregates monthly sales with `SUBSTR(ordered_at, 1, 7)`,
Apply `RANK() OVER (ORDER BY revenue DESC)` and `DENSE_RANK()` to the result.



??? success "Answer"
    ```sql
    WITH monthly_revenue AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        RANK()       OVER (ORDER BY revenue DESC) AS rank_val,
        DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank_val
    FROM monthly_revenue
    ORDER BY year_month;
    ```


    **Result** (top 7 of 12 rows)

    | year_month | revenue | rank_val | dense_rank_val |
    |---|---|---|---|
    | 2024-01 | 288,908,320.00 | 12 | 12 |
    | 2024-02 | 403,127,749.00 | 9 | 9 |
    | 2024-03 | 519,844,502.00 | 3 | 3 |
    | 2024-04 | 451,877,581.00 | 4 | 4 |
    | 2024-05 | 425,264,478.00 | 5 | 5 |
    | 2024-06 | 362,715,211.00 | 10 | 10 |
    | 2024-07 | 343,929,897.00 | 11 | 11 |


---


### 3. In addition to the total sales for each product, find the percentage of sales within that category.


As of 2024, the top 15 products are displayed in descending order of sales.


**Hint 1:** Find the total sales of the category with `SUM(revenue) OVER (PARTITION BY category_id)`,
Divide individual product sales by category sales to get the ratio.



??? success "Answer"
    ```sql
    SELECT
        p.name            AS product_name,
        cat.name          AS category,
        ROUND(SUM(oi.quantity * oi.unit_price), 0) AS product_revenue,
        ROUND(SUM(SUM(oi.quantity * oi.unit_price)) OVER (
            PARTITION BY p.category_id
        ), 0) AS category_revenue,
        ROUND(100.0 * SUM(oi.quantity * oi.unit_price)
            / SUM(SUM(oi.quantity * oi.unit_price)) OVER (PARTITION BY p.category_id),
        1) AS pct_of_category
    FROM order_items AS oi
    INNER JOIN orders     AS o   ON oi.order_id   = o.id
    INNER JOIN products   AS p   ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY p.id, p.name, cat.name, p.category_id
    ORDER BY product_revenue DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | product_name | category | product_revenue | category_revenue | pct_of_category |
    |---|---|---|---|---|
    | Razer Blade 18 Black | Gaming Laptop | 165,417,800.00 | 636,925,700.00 | 26.00 |
    | Razer Blade 16 Silver | Gaming Laptop | 137,007,300.00 | 636,925,700.00 | 21.50 |
    | MacBook Air 15 M3 Silver | MacBook | 126,065,300.00 | 126,065,300.00 | 100.00 |
    | ASUS Dual RTX 4060 Ti Black | NVIDIA | 106,992,000.00 | 345,858,700.00 | 30.90 |
    | ASUS Dual RTX 5070 Ti Silver | NVIDIA | 104,558,400.00 | 345,858,700.00 | 30.20 |
    | ASUS ROG Swift PG32UCDM Silver | Gaming Monitor | 90,734,400.00 | 353,934,400.00 | 25.60 |
    | ASUS ROG Strix Scar 16 | Gaming Laptop | 85,837,500.00 | 636,925,700.00 | 13.50 |


---


### 4. Calculate a running total for each customer's order amount.


For customer IDs 1 to 5, the cumulative order amount is displayed in order of order time.


**Hint 1:** `SUM(total_amount) OVER (PARTITION BY customer_id ORDER BY ordered_at ROWS UNBOUNDED PRECEDING)`
This statement creates a running total.



??? success "Answer"
    ```sql
    SELECT
        c.id            AS customer_id,
        c.name          AS customer_name,
        o.ordered_at,
        o.total_amount,
        SUM(o.total_amount) OVER (
            PARTITION BY c.id
            ORDER BY o.ordered_at
            ROWS UNBOUNDED PRECEDING
        ) AS running_total
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE c.id BETWEEN 1 AND 5
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY c.id, o.ordered_at;
    ```


    **Result** (top 7 of 416 rows)

    | customer_id | customer_name | ordered_at | total_amount | running_total |
    |---|---|---|---|---|
    | 2 | Danny Johnson | 2016-08-17 23:29:34 | 2,413,300.00 | 2,413,300.00 |
    | 2 | Danny Johnson | 2016-08-19 22:29:34 | 298,500.00 | 2,711,800.00 |
    | 2 | Danny Johnson | 2016-08-30 10:49:39 | 445,700.00 | 3,157,500.00 |
    | 2 | Danny Johnson | 2016-09-04 08:47:04 | 597,000.00 | 3,754,500.00 |
    | 2 | Danny Johnson | 2016-09-15 20:07:17 | 1,760,400.00 | 5,514,900.00 |
    | 2 | Danny Johnson | 2016-10-24 12:13:06 | 131,500.00 | 5,646,400.00 |
    | 2 | Danny Johnson | 2016-11-01 10:44:08 | 323,500.00 | 5,969,900.00 |


---


### 5. Divide payment methods into 4 groups (quartiles) based on the number of payments.


Payments completed in 2024 (`status = 'completed'`) are tallied by means, and quantified by `NTILE(4)`.


**Hint 1:** First, create a CTE that counts the number of transactions by payment method,
Divide into quartiles by `NTILE(4) OVER (ORDER BY payment_count DESC)`.
Decile 1 is the most used group.



??? success "Answer"
    ```sql
    WITH method_stats AS (
        SELECT
            method,
            COUNT(*)              AS payment_count,
            ROUND(SUM(amount), 0) AS total_amount
        FROM payments
        WHERE status = 'completed'
          AND paid_at LIKE '2024%'
        GROUP BY method
    )
    SELECT
        method,
        payment_count,
        total_amount,
        NTILE(4) OVER (ORDER BY payment_count DESC) AS quartile
    FROM method_stats
    ORDER BY payment_count DESC;
    ```


    **Result** (6 rows)

    | method | payment_count | total_amount | quartile |
    |---|---|---|---|
    | card | 2374 | 2,395,888,991.00 | 1 |
    | kakao_pay | 1058 | 1,002,822,322.00 | 1 |
    | naver_pay | 810 | 719,061,948.00 | 2 |
    | bank_transfer | 516 | 483,849,949.00 | 2 |
    | point | 286 | 261,926,968.00 | 3 |
    | virtual_account | 276 | 250,893,342.00 | 4 |


---


### 6. Find the increase/decrease and increase/decrease rate of monthly sales compared to the previous month.


We use data from 2023 to 2024.


**Hint 1:** Get the previous month's sales with `LAG(revenue, 1) OVER (ORDER BY year_month)`.
The increase/decrease rate is calculated as `(current_month - previous_month) / previous_month * 100`.



??? success "Answer"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at >= '2023-01-01'
          AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        LAG(revenue, 1) OVER (ORDER BY year_month) AS prev_revenue,
        revenue - LAG(revenue, 1) OVER (ORDER BY year_month) AS diff,
        ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY year_month))
            / LAG(revenue, 1) OVER (ORDER BY year_month), 1) AS growth_pct
    FROM monthly
    ORDER BY year_month;
    ```


    **Result** (top 7 of 24 rows)

    | year_month | revenue | prev_revenue | diff | growth_pct |
    |---|---|---|---|---|
    | 2023-01 | 270,083,587.00 | NULL | NULL | NULL |
    | 2023-02 | 327,431,648.00 | 270,083,587.00 | 57,348,061.00 | 21.20 |
    | 2023-03 | 477,735,354.00 | 327,431,648.00 | 150,303,706.00 | 45.90 |
    | 2023-04 | 396,849,049.00 | 477,735,354.00 | -80,886,305.00 | -16.90 |
    | 2023-05 | 349,749,072.00 | 396,849,049.00 | -47,099,977.00 | -11.90 |
    | 2023-06 | 279,698,633.00 | 349,749,072.00 | -70,050,439.00 | -20.00 |
    | 2023-07 | 312,983,148.00 | 279,698,633.00 | 33,284,515.00 | 11.90 |


---


### 7. Calculate the number of days until your customer's next order.


For VIP-level customers, find the number of days between each order and the next order.
Show the top 10 people with the shortest average intervals.


**Hint 1:** Get the next order date with `LEAD(ordered_at, 1) OVER (PARTITION BY customer_id ORDER BY ordered_at)`,
Calculate the interval with `JULIANDAY(next_order) - JULIANDAY(ordered_at)`.



??? success "Answer"
    ```sql
    WITH order_gaps AS (
        SELECT
            o.customer_id,
            c.name,
            o.ordered_at,
            LEAD(o.ordered_at, 1) OVER (
                PARTITION BY o.customer_id
                ORDER BY o.ordered_at
            ) AS next_order_at,
            ROUND(
                JULIANDAY(LEAD(o.ordered_at, 1) OVER (
                    PARTITION BY o.customer_id
                    ORDER BY o.ordered_at
                )) - JULIANDAY(o.ordered_at),
            0) AS days_to_next
        FROM orders AS o
        INNER JOIN customers AS c ON o.customer_id = c.id
        WHERE c.grade = 'VIP'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        customer_id,
        name,
        COUNT(days_to_next)       AS gap_count,
        ROUND(AVG(days_to_next), 1) AS avg_days_between,
        MIN(days_to_next)           AS min_gap,
        MAX(days_to_next)           AS max_gap
    FROM order_gaps
    WHERE days_to_next IS NOT NULL
    GROUP BY customer_id, name
    ORDER BY avg_days_between ASC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | customer_id | name | gap_count | avg_days_between | min_gap | max_gap |
    |---|---|---|---|---|---|
    | 97 | Jason Rivera | 341 | 10.10 | 0.0 | 112.00 |
    | 226 | Allen Snyder | 302 | 10.80 | 0.0 | 89.00 |
    | 549 | Ronald Arellano | 218 | 12.00 | 0.0 | 74.00 |
    | 4840 | Jennifer Bradshaw | 6 | 12.00 | 0.0 | 26.00 |
    | 356 | Courtney Huff | 222 | 12.30 | 0.0 | 126.00 |
    | 162 | Brenda Garcia | 248 | 13.00 | 0.0 | 102.00 |
    | 98 | Gabriel Walters | 274 | 13.20 | 0.0 | 143.00 |


---


### 8. Find the three-month moving average of sales.


For monthly sales for 2023-2024, calculate the moving average of the three months preceding the current month.


**Hint 1:** `AVG(revenue) OVER (ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`
This statement calculates the average of the 2 rows preceding the current row (3 rows in total).



??? success "Answer"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at >= '2023-01-01'
          AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 0) AS moving_avg_3m,
        COUNT(*) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS window_size
    FROM monthly
    ORDER BY year_month;
    ```


    **Result** (top 7 of 24 rows)

    | year_month | revenue | moving_avg_3m | window_size |
    |---|---|---|---|
    | 2023-01 | 270,083,587.00 | 270,083,587.00 | 1 |
    | 2023-02 | 327,431,648.00 | 298,757,618.00 | 2 |
    | 2023-03 | 477,735,354.00 | 358,416,863.00 | 3 |
    | 2023-04 | 396,849,049.00 | 400,672,017.00 | 3 |
    | 2023-05 | 349,749,072.00 | 408,111,158.00 | 3 |
    | 2023-06 | 279,698,633.00 | 342,098,918.00 | 3 |
    | 2023-07 | 312,983,148.00 | 314,143,618.00 | 3 |


---


### 9. List the names of the most expensive and least expensive products in each category in one row.


Use `FIRST_VALUE` and `LAST_VALUE`.


**Hint 1:** `FIRST_VALUE(name) OVER (PARTITION BY category_id ORDER BY price DESC)` is the most expensive product name.
When using `LAST_VALUE`, `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` must be specified to view the entire partition.



??? success "Answer"
    ```sql
    WITH ranked AS (
        SELECT DISTINCT
            cat.name AS category,
            FIRST_VALUE(p.name) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS most_expensive,
            FIRST_VALUE(p.price) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS max_price,
            LAST_VALUE(p.name) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS cheapest,
            LAST_VALUE(p.price) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS min_price
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
    )
    SELECT DISTINCT
        category,
        most_expensive,
        max_price,
        cheapest,
        min_price
    FROM ranked
    ORDER BY category;
    ```


    **Result** (top 7 of 38 rows)

    | category | most_expensive | max_price | cheapest | min_price |
    |---|---|---|---|---|
    | 2-in-1 | Lenovo ThinkPad X1 2in1 Silver | 1,866,100.00 | Samsung Galaxy Book5 360 Black | 1,179,900.00 |
    | AMD | AMD Ryzen 9 9900X | 591,800.00 | AMD Ryzen 9 9900X | 335,700.00 |
    | AMD | MSI Radeon RX 9070 XT GAMING X | 1,896,000.00 | MSI Radeon RX 9070 VENTUS 3X White | 383,100.00 |
    | AMD Socket | ASRock B850M Pro RS Silver | 665,600.00 | Gigabyte B650M AORUS ELITE AX | 376,000.00 |
    | Air Cooling | Noctua NH-D15 G2 Black | 106,000.00 | Arctic Freezer 36 A-RGB White | 23,000.00 |
    | Barebone | ASUS ExpertCenter PN65 Silver | 722,100.00 | ASUS ExpertCenter PN65 Silver | 722,100.00 |
    | Case | NZXT H7 Flow Silver | 248,700.00 | be quiet! Light Base 900 | 85,300.00 |


---


### 10. Divide products into 5 grades (NTILE) based on review ratings and obtain statistics for each grade.


Only products with 3 or more reviews are eligible.


**Hint 1:** First, find the average rating for each product (`HAVING COUNT(*) >= 3`),
After dividing the result into `NTILE(5) OVER (ORDER BY avg_rating)`,
We count again by grade.



??? success "Answer"
    ```sql
    WITH product_ratings AS (
        SELECT
            p.id,
            p.name,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(*)                AS review_count
        FROM reviews AS r
        INNER JOIN products AS p ON r.product_id = p.id
        GROUP BY p.id, p.name
        HAVING COUNT(*) >= 3
    ),
    tiered AS (
        SELECT
            *,
            NTILE(5) OVER (ORDER BY avg_rating) AS tier
        FROM product_ratings
    )
    SELECT
        tier,
        COUNT(*)                     AS product_count,
        ROUND(MIN(avg_rating), 2)    AS min_rating,
        ROUND(MAX(avg_rating), 2)    AS max_rating,
        ROUND(AVG(avg_rating), 2)    AS avg_of_avg,
        ROUND(AVG(review_count), 1)  AS avg_reviews
    FROM tiered
    GROUP BY tier
    ORDER BY tier;
    ```


    **Result** (5 rows)

    | tier | product_count | min_rating | max_rating | avg_of_avg | avg_reviews |
    |---|---|---|---|---|---|
    | 1 | 53 | 3.00 | 3.68 | 3.50 | 23.20 |
    | 2 | 53 | 3.70 | 3.83 | 3.76 | 33.90 |
    | 3 | 53 | 3.83 | 3.97 | 3.90 | 42.20 |
    | 4 | 53 | 3.97 | 4.10 | 4.02 | 33.70 |
    | 5 | 52 | 4.10 | 4.80 | 4.26 | 28.30 |


---


### 11. Rank order amount by customer level and extract information from the top 3 people within the level.


Shows the top 3 players in each tier (BRONZE, SILVER, GOLD, VIP) by total order value.


**Hint 1:** After tallying up the total order amount for each customer in CTE, enter `ROW_NUMBER() OVER (PARTITION BY grade ORDER BY total_spent DESC)`
Rank by rating and filter by `WHERE rn <= 3` in the outer query.



??? success "Answer"
    ```sql
    WITH customer_totals AS (
        SELECT
            c.id,
            c.name,
            c.grade,
            COUNT(*)                    AS order_count,
            ROUND(SUM(o.total_amount), 0) AS total_spent
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    ),
    ranked AS (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY grade
                ORDER BY total_spent DESC
            ) AS rn
        FROM customer_totals
    )
    SELECT
        grade,
        rn   AS rank_in_grade,
        name AS customer_name,
        order_count,
        total_spent
    FROM ranked
    WHERE rn <= 3
    ORDER BY
        CASE grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
        END,
        rn;
    ```


    **Result** (top 7 of 12 rows)

    | grade | rank_in_grade | customer_name | order_count | total_spent |
    |---|---|---|---|---|
    | VIP | 1 | Allen Snyder | 303 | 403,448,758.00 |
    | VIP | 2 | Jason Rivera | 342 | 366,385,931.00 |
    | VIP | 3 | Brenda Garcia | 249 | 253,180,338.00 |
    | GOLD | 1 | Sandra Callahan | 171 | 204,611,811.00 |
    | GOLD | 2 | David York | 160 | 199,282,408.00 |
    | GOLD | 3 | Robert Williams | 117 | 116,612,251.00 |
    | SILVER | 1 | April Rasmussen | 159 | 131,134,943.00 |


---


### 12. Display the monthly sales trend for each product and the ratio compared to the overall average for that product.


For the top five products in 2024, find the monthly sales and the ratio (%) of the average monthly sales for all products.


**Hint 1:** Step 1: Calculate product-monthly sales. Step 2: Select the top five products (based on total sales).
Step 3: Find the overall average for each product with `AVG(monthly_revenue) OVER (PARTITION BY product_id)`,
Calculate the ratio by dividing your monthly sales by the average.



??? success "Answer"
    ```sql
    WITH product_monthly AS (
        SELECT
            p.id       AS product_id,
            p.name     AS product_name,
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS monthly_revenue
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name, SUBSTR(o.ordered_at, 1, 7)
    ),
    top5 AS (
        SELECT product_id
        FROM product_monthly
        GROUP BY product_id
        ORDER BY SUM(monthly_revenue) DESC
        LIMIT 5
    )
    SELECT
        pm.product_name,
        pm.year_month,
        pm.monthly_revenue,
        ROUND(AVG(pm.monthly_revenue) OVER (
            PARTITION BY pm.product_id
        ), 0) AS avg_monthly,
        ROUND(100.0 * pm.monthly_revenue
            / AVG(pm.monthly_revenue) OVER (PARTITION BY pm.product_id),
        1) AS pct_of_avg
    FROM product_monthly AS pm
    INNER JOIN top5 AS t ON pm.product_id = t.product_id
    ORDER BY pm.product_name, pm.year_month;
    ```


    **Result** (top 7 of 55 rows)

    | product_name | year_month | monthly_revenue | avg_monthly | pct_of_avg |
    |---|---|---|---|---|
    | ASUS Dual RTX 4060 Ti Black | 2024-01 | 8,024,400.00 | 8,916,000.00 | 90.00 |
    | ASUS Dual RTX 4060 Ti Black | 2024-02 | 8,024,400.00 | 8,916,000.00 | 90.00 |
    | ASUS Dual RTX 4060 Ti Black | 2024-03 | 8,024,400.00 | 8,916,000.00 | 90.00 |
    | ASUS Dual RTX 4060 Ti Black | 2024-04 | 13,374,000.00 | 8,916,000.00 | 150.00 |
    | ASUS Dual RTX 4060 Ti Black | 2024-05 | 5,349,600.00 | 8,916,000.00 | 60.00 |
    | ASUS Dual RTX 4060 Ti Black | 2024-06 | 2,674,800.00 | 8,916,000.00 | 30.00 |
    | ASUS Dual RTX 4060 Ti Black | 2024-07 | 2,674,800.00 | 8,916,000.00 | 30.00 |


---


### 13. Track monthly share changes by payment method.


Calculate the share (%) of each payment method by month in 2024 and calculate the change in share (pp) compared to the previous month.


**Hint 1:** After finding the monthly amount by payment method, calculate the total monthly total with `SUM(amount) OVER (PARTITION BY year_month)`.
Get the previous month's market share with `LAG(share_pct, 1) OVER (PARTITION BY method ORDER BY year_month)`.



??? success "Answer"
    ```sql
    WITH method_monthly AS (
        SELECT
            SUBSTR(paid_at, 1, 7) AS year_month,
            method,
            ROUND(SUM(amount), 0) AS method_amount
        FROM payments
        WHERE status = 'completed'
          AND paid_at LIKE '2024%'
        GROUP BY SUBSTR(paid_at, 1, 7), method
    ),
    with_share AS (
        SELECT
            year_month,
            method,
            method_amount,
            ROUND(100.0 * method_amount
                / SUM(method_amount) OVER (PARTITION BY year_month),
            1) AS share_pct
        FROM method_monthly
    )
    SELECT
        year_month,
        method,
        method_amount,
        share_pct,
        LAG(share_pct, 1) OVER (
            PARTITION BY method
            ORDER BY year_month
        ) AS prev_share_pct,
        ROUND(share_pct - LAG(share_pct, 1) OVER (
            PARTITION BY method
            ORDER BY year_month
        ), 1) AS share_change_pp
    FROM with_share
    ORDER BY year_month, share_pct DESC;
    ```


    **Result** (top 7 of 72 rows)

    | year_month | method | method_amount | share_pct | prev_share_pct | share_change_pp |
    |---|---|---|---|---|---|
    | 2024-01 | card | 147,207,539.00 | 51.00 | NULL | NULL |
    | 2024-01 | kakao_pay | 53,100,585.00 | 18.40 | NULL | NULL |
    | 2024-01 | naver_pay | 33,230,574.00 | 11.50 | NULL | NULL |
    | 2024-01 | bank_transfer | 24,355,270.00 | 8.40 | NULL | NULL |
    | 2024-01 | virtual_account | 17,502,152.00 | 6.10 | NULL | NULL |
    | 2024-01 | point | 13,512,200.00 | 4.70 | NULL | NULL |
    | 2024-02 | card | 169,679,102.00 | 42.10 | 51.00 | -8.90 |


---


### 14. Perform gap analysis of order amount for each customer.


각 고객의 주문을 금액 순으로 정렬했을 때, 이전 주문 대비 금액 차이가 가장 큰 "점프"를 찾습니다.
Extract only if the jump amount is more than 500,000 won.


**Hint 1:** to `LAG(total_amount, 1) OVER (PARTITION BY customer_id ORDER BY total_amount)`
Amount Net Get the amount of the previous order. Find the difference and filter only rows that are over 500,000 won.



??? success "Answer"
    ```sql
    WITH ordered AS (
        SELECT
            o.customer_id,
            c.name,
            o.order_number,
            o.total_amount,
            LAG(o.total_amount, 1) OVER (
                PARTITION BY o.customer_id
                ORDER BY o.total_amount
            ) AS prev_amount
        FROM orders AS o
        INNER JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        customer_id,
        name,
        order_number,
        prev_amount,
        total_amount,
        total_amount - prev_amount AS gap
    FROM ordered
    WHERE prev_amount IS NOT NULL
      AND (total_amount - prev_amount) >= 500000
    ORDER BY gap DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | customer_id | name | order_number | prev_amount | total_amount | gap |
    |---|---|---|---|---|---|
    | 514 | Steven Johnson | ORD-20201121-08810 | 837,600.00 | 50,867,500.00 | 50,029,900.00 |
    | 3774 | Dylan Green | ORD-20250305-32265 | 6,346,600.00 | 46,820,024.00 | 40,473,424.00 |
    | 4136 | Zachary Ford | ORD-20251218-37240 | 405,600.00 | 38,626,400.00 | 38,220,800.00 |
    | 1322 | Donald Landry | ORD-20220106-15263 | 1,898,100.00 | 37,987,600.00 | 36,089,500.00 |
    | 3 | Adam Moore | ORD-20200209-05404 | 9,690,532.00 | 43,677,500.00 | 33,986,968.00 |
    | 551 | Katie Warner | ORD-20200820-07684 | 4,885,100.00 | 37,518,200.00 | 32,633,100.00 |
    | 4965 | Sandra Williams | ORD-20251207-37004 | 369,800.00 | 31,985,600.00 | 31,615,800.00 |


---


### 15. Calculate year-on-year (YoY) sales growth rate using a window function, and also display quarterly trends.


Find sales for each quarter, sales for the same quarter last year, and YoY growth rate.


**Hint 1:** Branches are calculated as `(CAST(SUBSTR(ordered_at,6,2) AS INTEGER) + 2) / 3`.
Get the value from 4 quarters ago (= same quarter of previous year) with `LAG(revenue, 4) OVER (ORDER BY year, quarter)`.



??? success "Answer"
    ```sql
    WITH quarterly AS (
        SELECT
            CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER) AS year,
            (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3 AS quarter,
            ROUND(SUM(total_amount), 0) AS revenue,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2020-01-01'
        GROUP BY
            CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER),
            (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3
    )
    SELECT
        year,
        quarter,
        revenue,
        order_count,
        LAG(revenue, 4) OVER (ORDER BY year, quarter) AS prev_year_revenue,
        CASE
            WHEN LAG(revenue, 4) OVER (ORDER BY year, quarter) IS NOT NULL
            THEN ROUND(100.0 * (revenue - LAG(revenue, 4) OVER (ORDER BY year, quarter))
                / LAG(revenue, 4) OVER (ORDER BY year, quarter), 1)
        END AS yoy_growth_pct
    FROM quarterly
    ORDER BY year, quarter;
    ```


    **Result** (top 7 of 24 rows)

    | year | quarter | revenue | order_count | prev_year_revenue | yoy_growth_pct |
    |---|---|---|---|---|---|
    | 2020 | 1 | 1,001,221,410.00 | 990 | NULL | NULL |
    | 2020 | 2 | 991,211,380.00 | 982 | NULL | NULL |
    | 2020 | 3 | 1,009,837,258.00 | 964 | NULL | NULL |
    | 2020 | 4 | 1,086,405,018.00 | 1084 | NULL | NULL |
    | 2021 | 1 | 1,458,348,254.00 | 1351 | 1,001,221,410.00 | 45.70 |
    | 2021 | 2 | 1,210,987,985.00 | 1143 | 991,211,380.00 | 22.20 |
    | 2021 | 3 | 1,361,699,965.00 | 1412 | 1,009,837,258.00 | 34.80 |


---
