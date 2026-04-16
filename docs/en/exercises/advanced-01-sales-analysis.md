# Sales Analysis

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `categories` — Categories (parent-child hierarchy)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `Aggregation`, `GROUP BY`, `Window Functions`, `CTE`, `YoY Growth`, `Pivot`



### 1. Monthly Revenue Trend (2022-2024)


The CEO has requested a monthly revenue report for the past 3 years.
Show each month's revenue, order count, and average order value.
Exclude cancelled and returned orders.


**Hint 1:** - Use `SUBSTR(ordered_at, 1, 7)` to extract year-month
- Use `SUM`, `COUNT`, `AVG`
- Use `BETWEEN` or `LIKE` for year range filtering



??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7)        AS year_month,
        COUNT(*)                         AS order_count,
        ROUND(SUM(total_amount), 2)      AS revenue,
        ROUND(AVG(total_amount), 2)      AS avg_order_value
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
      AND ordered_at BETWEEN '2022-01-01' AND '2024-12-31 23:59:59'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY year_month;
    ```


    **Result** (top 7 of 36 rows)

    | year_month | order_count | revenue | avg_order_value |
    |---|---|---|---|
    | 2022-01 | 340 | 387,797,263.00 | 1,140,580.19 |
    | 2022-02 | 343 | 349,125,148.00 | 1,017,857.57 |
    | 2022-03 | 397 | 392,750,666.00 | 989,296.39 |
    | 2022-04 | 337 | 313,546,744.00 | 930,405.77 |
    | 2022-05 | 448 | 445,361,972.00 | 994,111.54 |
    | 2022-06 | 348 | 353,057,024.00 | 1,014,531.68 |
    | 2022-07 | 386 | 418,258,615.00 | 1,083,571.54 |


---


### 2. Top 10 Products by Revenue in 2024


The MD team wants to know which products generated the most revenue in 2024.
Include product name, category, units sold, total revenue, and average customer rating.


**Hint 1:** - JOIN `order_items` -> `orders` -> `products` -> `categories`
- Use `LEFT JOIN` for `reviews` to include products with no reviews
- Filter for 2024 non-cancelled orders



??? success "Answer"
    ```sql
    SELECT
        p.name                                  AS product_name,
        cat.name                                AS category,
        SUM(oi.quantity)                        AS units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
        COUNT(DISTINCT r.id)                    AS review_count,
        ROUND(AVG(r.rating), 2)                 AS avg_rating
    FROM order_items AS oi
    INNER JOIN orders     AS o   ON oi.order_id   = o.id
    INNER JOIN products   AS p   ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LEFT  JOIN reviews    AS r   ON r.product_id  = p.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY p.id, p.name, cat.name
    ORDER BY total_revenue DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | product_name | category | units_sold | total_revenue | review_count | avg_rating |
    |---|---|---|---|---|---|
    | AMD Ryzen 9 9900X | AMD | 15,535 | 5,215,099,500.00 | 65 | 3.86 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | NVIDIA | 2058 | 3,589,152,000.00 | 42 | 4.12 |
    | Razer Blade 18 Black | Gaming Laptop | 760 | 3,308,356,000.00 | 20 | 4.10 |
    | Crucial T700 2TB Silver | SSD | 12,551 | 3,225,607,000.00 | 77 | 4.21 |
    | Intel Core Ultra 7 265K White | Intel | 18,914 | 3,219,162,800.00 | 49 | 3.98 |
    | Razer Blade 16 Silver | Gaming Laptop | 703 | 2,603,138,700.00 | 19 | 3.95 |
    | SteelSeries Arctis Nova 1 Silver | Speakers/Headsets | 6210 | 2,509,461,000.00 | 45 | 3.87 |


---


### 3. Seasonality Pattern Analysis


Does this shopping mall have seasonal revenue patterns?
Calculate the average monthly revenue by calendar month (Jan-Dec) across all years.
Identify the highest and lowest months.


**Hint 1:** - Use `SUBSTR(ordered_at, 6, 2)` to extract month number
- Use a derived table to calculate the average of yearly SUMs
- Use `CASE` to convert month numbers to names



??? success "Answer"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7)  AS year_month,
            SUBSTR(ordered_at, 6, 2)  AS month_num,
            SUM(total_amount)         AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        CASE month_num
            WHEN '01' THEN '1월'  WHEN '02' THEN '2월'
            WHEN '03' THEN '3월'  WHEN '04' THEN '4월'
            WHEN '05' THEN '5월'  WHEN '06' THEN '6월'
            WHEN '07' THEN '7월'  WHEN '08' THEN '8월'
            WHEN '09' THEN '9월'  WHEN '10' THEN '10월'
            WHEN '11' THEN '11월' WHEN '12' THEN '12월'
        END AS month_name,
        month_num,
        COUNT(*) AS years_of_data,
        ROUND(AVG(revenue), 2)  AS avg_monthly_revenue,
        ROUND(MIN(revenue), 2)  AS min_revenue,
        ROUND(MAX(revenue), 2)  AS max_revenue
    FROM monthly
    GROUP BY month_num
    ORDER BY month_num;
    ```


    **Result** (top 7 of 12 rows)

    | month_name | month_num | years_of_data | avg_monthly_revenue | min_revenue | max_revenue |
    |---|---|---|---|---|---|
    | 1월 | 01 | 10 | 237,985,009.30 | 14,194,769.00 | 484,529,284.00 |
    | 2월 | 02 | 10 | 245,894,154.40 | 12,984,335.00 | 467,436,635.00 |
    | 3월 | 03 | 10 | 363,549,664.90 | 14,154,562.00 | 641,001,712.00 |
    | 4월 | 04 | 10 | 281,473,593.70 | 16,878,372.00 | 491,756,256.00 |
    | 5월 | 05 | 10 | 281,625,199.50 | 28,570,768.00 | 494,399,878.00 |
    | 6월 | 06 | 10 | 243,521,256.30 | 23,793,991.00 | 435,232,872.00 |
    | 7월 | 07 | 10 | 240,439,598.90 | 29,696,984.00 | 426,063,172.00 |


---


### 4. Payment Method Analysis


The finance team wants to understand customer payment preferences.
Show transaction count, total amount, average transaction amount,
and percentage of total revenue by payment method.


**Hint 1:** - JOIN `payments` with `orders` to include order dates
- Calculate grand total with `SUM(...) OVER ()` or a subquery
- Use `ROUND(..., 1)` for percentages



??? success "Answer"
    ```sql
    WITH payment_totals AS (
        SELECT
            p.method,
            COUNT(*)            AS transaction_count,
            SUM(p.amount)       AS total_collected,
            AVG(p.amount)       AS avg_transaction
        FROM payments AS p
        WHERE p.status = 'completed'
        GROUP BY p.method
    ),
    grand_total AS (
        SELECT SUM(total_collected) AS grand FROM payment_totals
    )
    SELECT
        pt.method,
        pt.transaction_count,
        ROUND(pt.total_collected, 2)  AS total_collected,
        ROUND(pt.avg_transaction, 2)  AS avg_transaction,
        ROUND(100.0 * pt.total_collected / gt.grand, 1) AS pct_of_revenue
    FROM payment_totals AS pt
    CROSS JOIN grand_total AS gt
    ORDER BY pt.total_collected DESC;
    ```


    **Result** (6 rows)

    | method | transaction_count | total_collected | avg_transaction | pct_of_revenue |
    |---|---|---|---|---|
    | card | 15,556 | 15,537,036,997.00 | 998,780.98 | 44.80 |
    | kakao_pay | 6886 | 6,781,114,303.00 | 984,768.27 | 19.60 |
    | naver_pay | 5270 | 5,420,480,093.00 | 1,028,554.10 | 15.60 |
    | bank_transfer | 3429 | 3,456,454,657.00 | 1,008,006.61 | 10.00 |
    | point | 1770 | 1,780,334,619.00 | 1,005,838.77 | 5.10 |
    | virtual_account | 1705 | 1,706,777,095.00 | 1,001,042.28 | 4.90 |


---


### 5. Year-over-Year Revenue Growth by Category


The board wants a YoY growth report by category for 2023 and 2024.
Show each category's revenue for both years and the percentage change.


**Hint 1:** - Use conditional aggregation `SUM(CASE WHEN ... THEN ... END)` for yearly revenue
- YoY% formula: `(2024 - 2023) / 2023 * 100`
- Use `NULLIF` to prevent division by zero



??? success "Answer"
    ```sql
    WITH category_revenue AS (
        SELECT
            cat.name AS category,
            ROUND(SUM(CASE
                WHEN o.ordered_at LIKE '2023%'
                THEN oi.quantity * oi.unit_price ELSE 0
            END), 2) AS revenue_2023,
            ROUND(SUM(CASE
                WHEN o.ordered_at LIKE '2024%'
                THEN oi.quantity * oi.unit_price ELSE 0
            END), 2) AS revenue_2024
        FROM order_items AS oi
        INNER JOIN orders     AS o   ON oi.order_id   = o.id
        INNER JOIN products   AS p   ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
          AND o.ordered_at BETWEEN '2023-01-01' AND '2024-12-31 23:59:59'
        GROUP BY cat.name
    )
    SELECT
        category,
        revenue_2023,
        revenue_2024,
        ROUND(revenue_2024 - revenue_2023, 2) AS absolute_change,
        ROUND(
            100.0 * (revenue_2024 - revenue_2023)
                  / NULLIF(revenue_2023, 0),
            1
        ) AS yoy_growth_pct
    FROM category_revenue
    ORDER BY yoy_growth_pct DESC;
    ```


    **Result** (top 7 of 38 rows)

    | category | revenue_2023 | revenue_2024 | absolute_change | yoy_growth_pct |
    |---|---|---|---|---|
    | Switch/Hub | 4,731,900.00 | 59,553,200.00 | 54,821,300.00 | 1,158.50 |
    | Barebone | 15,435,600.00 | 28,434,000.00 | 12,998,400.00 | 84.20 |
    | DDR5 | 84,235,900.00 | 153,437,900.00 | 69,202,000.00 | 82.20 |
    | Wired | 10,209,900.00 | 18,331,300.00 | 8,121,400.00 | 79.50 |
    | 2-in-1 | 197,301,500.00 | 340,884,400.00 | 143,582,900.00 | 72.80 |
    | Gaming | 67,609,900.00 | 106,257,400.00 | 38,647,500.00 | 57.20 |
    | Professional Monitor | 171,178,100.00 | 254,590,200.00 | 83,412,100.00 | 48.70 |


---


### 6. Bonus: Category x Month Heatmap


Combine questions 3 and 5.
Create a heatmap table with categories (rows) x months (columns) for 2024.
Use conditional aggregation with 12 SUM(CASE WHEN month = 'XX' ...) columns.


**Hint 1:** - Extract month with `SUBSTR(o.ordered_at, 6, 2)`
- Use `SUM(CASE WHEN ... THEN ... ELSE 0 END)` for each of 12 columns
- `GROUP BY cat.name`



??? success "Answer"
    ```sql
    SELECT
        cat.name AS category,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='01' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS jan,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='02' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS feb,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='03' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS mar,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='04' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS apr,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='05' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS may,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='06' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS jun,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='07' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS jul,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='08' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS aug,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='09' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS sep,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='10' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS oct,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='11' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS nov,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='12' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS dec
    FROM order_items AS oi
    INNER JOIN orders     AS o   ON oi.order_id   = o.id
    INNER JOIN products   AS p   ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY cat.name
    ORDER BY cat.name;
    ```


    **Result** (top 7 of 38 rows)

    | category | jan | feb | mar | apr | may | jun | jul | aug | sep | oct | nov | dec |
    |---|---|---|---|---|---|---|---|---|---|---|---|---|
    | 2-in-1 | 2,694,300.00 | 15,691,100.00 | 24,844,800.00 | 26,944,500.00 | 33,723,800.00 | 35,502,100.00 | 17,794,000.00 | 28,980,800.00 | 36,247,900.00 | 34,001,000.00 | 42,408,500.00 | 42,051,600.00 |
    | AMD | 25,993,100.00 | 36,938,800.00 | 51,176,300.00 | 33,566,300.00 | 36,683,100.00 | 37,901,900.00 | 26,040,000.00 | 39,831,400.00 | 47,644,400.00 | 29,625,900.00 | 38,707,700.00 | 43,844,500.00 |
    | AMD Socket | 14,205,600.00 | 14,907,000.00 | 21,330,700.00 | 15,558,700.00 | 25,168,600.00 | 14,107,400.00 | 14,902,300.00 | 19,967,100.00 | 22,741,200.00 | 15,321,700.00 | 30,267,600.00 | 14,576,500.00 |
    | Air Cooling | 1,160,300.00 | 1,497,100.00 | 1,493,700.00 | 1,351,700.00 | 2,123,400.00 | 870,000.00 | 1,635,700.00 | 1,351,400.00 | 1,991,300.00 | 1,573,000.00 | 2,957,300.00 | 1,362,000.00 |
    | Barebone | 2,437,200.00 | 2,437,200.00 | 6,499,200.00 | 2,437,200.00 | 812,400.00 | 1,624,800.00 | 1,624,800.00 | 10,561,200.00 | 0.0 | 0.0 | 0.0 | 0.0 |
    | Case | 8,060,800.00 | 12,859,200.00 | 15,246,000.00 | 12,009,800.00 | 10,449,500.00 | 10,724,000.00 | 9,453,800.00 | 10,652,500.00 | 10,805,700.00 | 12,232,800.00 | 14,946,300.00 | 13,175,500.00 |
    | Custom Build | 5,229,300.00 | 1,800,000.00 | 6,593,600.00 | 4,169,200.00 | 967,600.00 | 0.0 | 3,043,900.00 | 5,229,300.00 | 4,623,300.00 | 1,579,400.00 | 9,096,600.00 | 3,296,800.00 |


---
