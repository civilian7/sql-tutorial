# Sales Analysis

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `categories` — Categories (parent-child hierarchy)  

    `customers` — Customers (grade, points, channel)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `CTE`, `Window Functions`, `Multiple JOIN`, `Aggregation`, `YoY Growth`, `Moving Average`, `ABC Analysis`, `Cohort`



### 1. Monthly sales trend (last 3 years)


Find monthly sales, number of orders, and average order value from 2022 to 2024.


**Hint 1:** - Extract year-month with `SUBSTR(ordered_at, 1, 7)`
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


    **Result** (top 7 of 36 rows)

    | year_month | order_count | revenue | avg_order_value |
    |---|---|---|---|
    | 2022-01 | 340 | 387,797,263.00 | 1,140,580.00 |
    | 2022-02 | 343 | 349,125,148.00 | 1,017,858.00 |
    | 2022-03 | 397 | 392,750,666.00 | 989,296.00 |
    | 2022-04 | 337 | 313,546,744.00 | 930,406.00 |
    | 2022-05 | 448 | 445,361,972.00 | 994,112.00 |
    | 2022-06 | 348 | 353,057,024.00 | 1,014,532.00 |
    | 2022-07 | 386 | 418,258,615.00 | 1,083,572.00 |


---


### 2. Proportion of sales by category


Find the sales of each major category and its proportion (%) compared to the total in 2024.


**Hint 1:** - `categories.depth = 0` is the main category
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


    **Result** (top 7 of 18 rows)

    | top_category | revenue | revenue_pct |
    |---|---|---|
    | Laptop | 1,395,635,900.00 | 27.00 |
    | Monitor | 727,065,300.00 | 14.10 |
    | Graphics Card | 713,579,800.00 | 13.80 |
    | Motherboard | 398,988,900.00 | 7.70 |
    | Speakers/Headsets | 232,144,800.00 | 4.50 |
    | Storage | 205,861,200.00 | 4.00 |
    | Memory (RAM) | 200,423,600.00 | 3.90 |


---


### 3. Top 20 customer sales rankings


Display information about the top 20 customers by total purchase amount for all time periods.
Includes customer name, level, number of orders, total purchase amount, and rank.


**Hint 1:** - Use `RANK()` or `ROW_NUMBER()` window functions
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


    **Result** (top 7 of 20 rows)

    | ranking | customer_name | grade | order_count | total_spent |
    |---|---|---|---|---|
    | 1 | Allen Snyder | VIP | 303 | 403,448,758.00 |
    | 2 | Jason Rivera | VIP | 342 | 366,385,931.00 |
    | 3 | Brenda Garcia | VIP | 249 | 253,180,338.00 |
    | 4 | Courtney Huff | VIP | 223 | 244,604,910.00 |
    | 5 | Ronald Arellano | VIP | 219 | 235,775,349.00 |
    | 6 | James Banks | VIP | 230 | 234,708,853.00 |
    | 7 | Gabriel Walters | VIP | 275 | 230,165,991.00 |


---


### 4. Sales pattern by day of the week


Find the average number of orders and average sales by day of the week (Mon-Sun) from all order data.
Find out which days of the week have the highest sales.


**Hint 1:** - SQLite: `strftime('%w', ordered_at)` → 0 (Sun)~6 (Sat)
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
            WHEN 0 THEN '일요일'
            WHEN 1 THEN '월요일'
            WHEN 2 THEN '화요일'
            WHEN 3 THEN '수요일'
            WHEN 4 THEN '목요일'
            WHEN 5 THEN '금요일'
            WHEN 6 THEN '토요일'
        END AS day_of_week,
        ROUND(AVG(order_count)) AS avg_daily_orders,
        ROUND(AVG(revenue))     AS avg_daily_revenue
    FROM daily_stats
    GROUP BY dow
    ORDER BY dow;
    ```


    **Result** (7 rows)

    | day_of_week | avg_daily_orders | avg_daily_revenue |
    |---|---|---|
    | 일요일 | 11.00 | 10,702,305.00 |
    | 월요일 | 11.00 | 10,470,017.00 |
    | 화요일 | 9.00 | 9,434,724.00 |
    | 수요일 | 9.00 | 8,818,457.00 |
    | 목요일 | 9.00 | 8,818,498.00 |
    | 금요일 | 9.00 | 9,178,156.00 |
    | 토요일 | 11.00 | 10,550,779.00 |


---


### 5. Quarterly sales and growth rate compared to the previous quarter


Find quarterly sales from 2022 to 2024 and growth rate (%) compared to the previous quarter.


**Hint 1:** - Branch: `(CAST(SUBSTR(ordered_at,6,2) AS INTEGER) + 2) / 3`
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


    **Result** (top 7 of 12 rows)

    | yq | revenue | order_count | prev_quarter_revenue | qoq_growth_pct |
    |---|---|---|---|---|
    | 2022-Q1 | 1,129,673,077.00 | 1080 | NULL | NULL |
    | 2022-Q2 | 1,111,965,740.00 | 1133 | 1,129,673,077.00 | -1.60 |
    | 2022-Q3 | 1,312,284,718.00 | 1246 | 1,111,965,740.00 | 18.00 |
    | 2022-Q4 | 1,271,192,508.00 | 1359 | 1,312,284,718.00 | -3.10 |
    | 2023-Q1 | 1,075,250,589.00 | 1083 | 1,271,192,508.00 | -15.40 |
    | 2023-Q2 | 1,026,296,754.00 | 1102 | 1,075,250,589.00 | -4.60 |
    | 2023-Q3 | 1,127,278,823.00 | 1094 | 1,026,296,754.00 | 9.80 |


---


### 6. Trend in sales proportion by payment method


Find the sales share (%) of each payment method (card, bank_transfer, kakao_pay, etc.) by month in 2024.


**Hint 1:** - Classify payment method as `payments.method`
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


---


### 7. Top 3 products by category (Top-N per Group)


Select the top three sales products in each major category in 2024.


**Hint 1:** - Count product sales by category in CTE
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


    **Result** (top 7 of 53 rows)

    | top_category | rank | product_name | units_sold | revenue |
    |---|---|---|---|---|
    | CPU | 1 | AMD Ryzen 9 9900X | 239 | 80,232,300.00 |
    | CPU | 2 | Intel Core Ultra 7 265K White | 386 | 65,697,200.00 |
    | Case | 1 | be quiet! Light Base 900 | 215 | 23,054,800.00 |
    | Case | 2 | Fractal Design Define 7 White | 108 | 22,464,000.00 |
    | Case | 3 | CORSAIR iCUE 4000X | 196 | 22,324,400.00 |
    | Cooling | 1 | NZXT Kraken Elite 240 RGB Silver | 174 | 33,876,500.00 |
    | Cooling | 2 | Arctic Liquid Freezer III 240 | 198 | 19,522,800.00 |


---


### 8. Year-on-year (YoY) sales growth rate


Find the sales for each month in 2023 and 2024 and the growth rate (%) compared to the same month of the previous year.


**Hint 1:** - `LAG(revenue, 12)` — See sales 12 months ago
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


    **Result** (top 7 of 24 rows)

    | year_month | current_revenue | prev_year_revenue | yoy_growth_pct |
    |---|---|---|---|
    | 2023-01 | 270,083,587.00 | 387,797,263.00 | -30.40 |
    | 2023-02 | 327,431,648.00 | 349,125,148.00 | -6.20 |
    | 2023-03 | 477,735,354.00 | 392,750,666.00 | 21.60 |
    | 2023-04 | 396,849,049.00 | 313,546,744.00 | 26.60 |
    | 2023-05 | 349,749,072.00 | 445,361,972.00 | -21.50 |
    | 2023-06 | 279,698,633.00 | 353,057,024.00 | -20.80 |
    | 2023-07 | 312,983,148.00 | 418,258,615.00 | -25.20 |


---


### 9. Moving Average — 3-month moving average of sales


Find the three-month moving average of monthly sales.
Moving averages smooth out seasonal fluctuations when identifying trends.


**Hint 1:** - `AVG(revenue) OVER (ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`
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


    **Result** (top 7 of 24 rows)

    | year_month | revenue | moving_avg_3m | moving_avg_6m |
    |---|---|---|---|
    | 2023-01 | 270,083,587.00 | 270,083,587.00 | 270,083,587.00 |
    | 2023-02 | 327,431,648.00 | 298,757,618.00 | 298,757,618.00 |
    | 2023-03 | 477,735,354.00 | 358,416,863.00 | 358,416,863.00 |
    | 2023-04 | 396,849,049.00 | 400,672,017.00 | 368,024,910.00 |
    | 2023-05 | 349,749,072.00 | 408,111,158.00 | 364,369,742.00 |
    | 2023-06 | 279,698,633.00 | 342,098,918.00 | 350,257,891.00 |
    | 2023-07 | 312,983,148.00 | 314,143,618.00 | 357,407,817.00 |


---


### 10. ABC Analysis — Cumulative sales ratio by product


Sort sales by product in descending order in 2024, and assign A/B/C grades based on cumulative sales ratio.
(A: Top 70%, B: 70~90%, C: Rest)


**Hint 1:** - Cumulative ratio: `SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER ()`
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


    **Result** (top 7 of 30 rows)

    | product_name | revenue | cum_pct | abc_class |
    |---|---|---|---|
    | Razer Blade 18 Black | 165,417,800.00 | 3.20 | A |
    | Razer Blade 16 Silver | 137,007,300.00 | 5.90 | A |
    | MacBook Air 15 M3 Silver | 126,065,300.00 | 8.30 | A |
    | ASUS Dual RTX 4060 Ti Black | 106,992,000.00 | 10.40 | A |
    | ASUS Dual RTX 5070 Ti Silver | 104,558,400.00 | 12.40 | A |
    | ASUS ROG Swift PG32UCDM Silver | 90,734,400.00 | 14.20 | A |
    | ASUS ROG Strix Scar 16 | 85,837,500.00 | 15.80 | A |


---


### 11. Comparison of sales from new customers vs. repeat customers


Separate the number of orders and sales from new customers (first order that month) and repeat customers by month in 2024.


**Hint 1:** - Month of first order for each customer: obtained as `MIN(ordered_at)`
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
                WHEN SUBSTR(o.ordered_at, 1, 7) = fo.first_month THEN '신규'
                ELSE '재구매'
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


    **Result** (top 7 of 24 rows)

    | year_month | customer_type | order_count | revenue |
    |---|---|---|---|
    | 2024-01 | 신규 | 32 | 31,865,130.00 |
    | 2024-01 | 재구매 | 282 | 257,043,190.00 |
    | 2024-02 | 신규 | 30 | 8,770,172.00 |
    | 2024-02 | 재구매 | 386 | 394,357,577.00 |
    | 2024-03 | 신규 | 50 | 28,455,371.00 |
    | 2024-03 | 재구매 | 505 | 491,389,131.00 |
    | 2024-04 | 신규 | 34 | 25,112,310.00 |


---


### 12. Trend of average unit price by customer level


Find the average order amount by customer level (BRONZE/SILVER/GOLD/VIP) by month in 2024.


**Hint 1:** - Graded as `customers.grade`
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


    **Result** (top 7 of 48 rows)

    | year_month | grade | order_count | avg_order_value |
    |---|---|---|---|
    | 2024-01 | VIP | 124 | 834,949.00 |
    | 2024-01 | GOLD | 73 | 1,202,930.00 |
    | 2024-01 | SILVER | 56 | 904,820.00 |
    | 2024-01 | BRONZE | 61 | 768,702.00 |
    | 2024-02 | VIP | 178 | 926,721.00 |
    | 2024-02 | GOLD | 97 | 926,946.00 |
    | 2024-02 | SILVER | 40 | 974,420.00 |


---


### 13. Delivery time analysis by shipping company


Find the average delivery days, minimum/maximum lead days, and number of deliveries by carrier in 2024.
Only items that have been delivered are eligible.


**Hint 1:** - Delivery time: `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)`
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


    **Result** (5 rows)

    | carrier | delivery_count | avg_days | min_days | max_days | within_2days_pct |
    |---|---|---|---|---|---|
    | OnTrac | 556 | 2.40 | 1.00 | 4.00 | 53.80 |
    | UPS | 1349 | 2.50 | 1.00 | 4.00 | 52.50 |
    | USPS | 1068 | 2.50 | 1.00 | 4.00 | 50.00 |
    | DHL | 778 | 2.60 | 1.00 | 4.00 | 46.10 |
    | FedEx | 1569 | 2.60 | 1.00 | 4.00 | 47.20 |


---


### 14. Sales impact by discount rate section


Divide the discount rate for orders in 2024 (discount_amount / (total_amount + discount_amount)) into sections,
Analyze the number of orders, average order amount, and total sales for each segment.


**Hint 1:** - Discount rate = `discount_amount / (total_amount + discount_amount) * 100`
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
            WHEN discount_pct = 0    THEN '할인 없음'
            WHEN discount_pct <= 5   THEN '1~5%'
            WHEN discount_pct <= 10  THEN '6~10%'
            WHEN discount_pct <= 20  THEN '11~20%'
            ELSE '20% 초과'
        END AS discount_range,
        COUNT(*)                    AS order_count,
        ROUND(AVG(total_amount))    AS avg_order_value,
        ROUND(SUM(total_amount))    AS total_revenue
    FROM order_discount
    GROUP BY CASE
        WHEN discount_pct = 0    THEN '할인 없음'
        WHEN discount_pct <= 5   THEN '1~5%'
        WHEN discount_pct <= 10  THEN '6~10%'
        WHEN discount_pct <= 20  THEN '11~20%'
        ELSE '20% 초과'
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


    **Result** (4 rows)

    | discount_range | order_count | avg_order_value | total_revenue |
    |---|---|---|---|
    | 할인 없음 | 4152 | 815,975.00 | 3,387,926,737.00 |
    | 1~5% | 811 | 1,783,303.00 | 1,446,258,687.00 |
    | 6~10% | 228 | 848,082.00 | 193,362,738.00 |
    | 11~20% | 129 | 673,607.00 | 86,895,358.00 |


---


### 15. Promotion ROI analysis


Analyze the sales effect (ROI) of each promotion compared to the input discount amount.
During the promotion period, sales and discount amounts for promotional products are counted.


**Hint 1:** - Identify target product with `promotions` + `promotion_products`
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


    **Result** (top 7 of 105 rows)

    | promo_name | promo_type | discount_info | order_count | gross_revenue | total_discount | net_revenue | roi_pct |
    |---|---|---|---|---|---|---|---|
    | Gaming Gear Festa 2023 | category | percent 18.0 | 25 | 16,859,400.00 | 15,600.00 | 16,843,800.00 | 107,973.10 |
    | Black Friday 2022 | seasonal | percent 25.0 | 25 | 17,059,700.00 | 18,500.00 | 17,041,200.00 | 92,114.60 |
    | Gaming Gear Festa 2024 | category | percent 18.0 | 30 | 18,118,000.00 | 27,600.00 | 18,090,400.00 | 65,544.90 |
    | Gaming Gear Festa 2020 | category | percent 18.0 | 33 | 12,592,900.00 | 19,500.00 | 12,573,400.00 | 64,479.00 |
    | Black Friday 2020 | seasonal | percent 25.0 | 35 | 18,172,900.00 | 31,300.00 | 18,141,600.00 | 57,960.40 |
    | Gaming Gear Festa 2016 | category | percent 18.0 | 5 | 5,221,100.00 | 11,300.00 | 5,209,800.00 | 46,104.40 |
    | New Year Sale 2021 | seasonal | percent 10.0 | 35 | 33,039,800.00 | 76,200.00 | 32,963,600.00 | 43,259.30 |


---


### 16. Shopping Cart → Purchase Conversion Rate


Find the percentage of products in your shopping cart that were converted into actual purchases by category.


**Hint 1:** - Number of products contained in `cart_items` vs. number of identical products actually ordered by the same customer
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


    **Result** (top 7 of 38 rows)

    | category | cart_items_total | converted | conversion_rate_pct |
    |---|---|---|---|
    | Gaming | 332 | 49 | 14.80 |
    | Case | 325 | 37 | 11.40 |
    | SSD | 201 | 22 | 10.90 |
    | DDR4 | 197 | 21 | 10.70 |
    | Intel | 158 | 14 | 8.90 |
    | Wireless | 205 | 18 | 8.80 |
    | Speakers/Headsets | 398 | 34 | 8.50 |


---


### 17. Simultaneous purchase patterns (shopping cart analysis)


Find pairs of products purchased together in the same order.
Shows only product pairs with more than 5 simultaneous purchases.


**Hint 1:** - Self-join `order_items` to create different product pairs of the same order
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


    **Result** (top 7 of 20 rows)

    | product_a | product_b | co_purchase_count |
    |---|---|---|
    | AMD Ryzen 9 9900X | Crucial T700 2TB Silver | 430 |
    | AMD Ryzen 9 9900X | SK hynix Platinum P41 2TB Silver | 329 |
    | be quiet! Light Base 900 | Crucial T700 2TB Silver | 294 |
    | Intel Core Ultra 5 245KF | Crucial T700 2TB Silver | 282 |
    | be quiet! Light Base 900 | AMD Ryzen 9 9900X | 249 |
    | Seasonic VERTEX GX-1200 Black | Crucial T700 2TB Silver | 221 |
    | Samsung DDR5 32GB PC5-38400 | Crucial T700 2TB Silver | 217 |


---


### 18. Correlation between review ratings and sales


Analyze the relationship between average review rating and sales for each product.
Calculate average sales by rating range (1~2, 2~3, 3~4, 4~5).


**Hint 1:** - First calculate the average rating and sales for each product
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


    **Result** (2 rows)

    | rating_range | product_count | avg_revenue | avg_reviews | avg_rating_in_range |
    |---|---|---|---|---|
    | 3.0~3.9 | 165 | 3,987,852,901.00 | 33.00 | 3.73 |
    | 4.0~5.0 | 99 | 4,123,862,055.00 | 30.00 | 4.15 |


---


### 19. Analysis of point usage effects


Compare the average order amount and repurchase rate for orders that used points and those that did not.
(As of 2024)


**Hint 1:** - If `orders.point_used > 0`, order using points
- Repurchase rate: The percentage of customers in the group who ordered more than twice
- First aggregate order characteristics for each customer using CTE



??? success "Answer"
    ```sql
    WITH order_classified AS (
        SELECT
            customer_id,
            total_amount,
            CASE WHEN point_used > 0 THEN '포인트 사용' ELSE '미사용' END AS point_type
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


    **Result** (2 rows)

    | point_type | customer_count | avg_order_value | repeat_rate_pct |
    |---|---|---|---|
    | 미사용 | 1607 | 895,789.00 | 57.70 |
    | 포인트 사용 | 396 | 1,033,110.00 | 18.70 |


---


### 20. Comprehensive management dashboard


Create a comprehensive 2024 management dashboard for CEOs with a single query.
Includes total sales, number of orders, number of customers, average unit price, return rate, average delivery date, and average review rating.


**Hint 1:** - Calculate each indicator individually using subquery or CTE and then combine them
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


    **Result** (1 rows)

    | total_revenue | total_orders | unique_customers | avg_order_value | return_rate_pct | avg_delivery_days | avg_rating | review_count |
    |---|---|---|---|---|---|---|---|
    | 5,114,443,520.00 | 5320 | 1669 | 961,362.00 | 2.70 | 2.50 | 3.91 | 1267 |


---
