# Sales Analysis

**Tables:** `orders`, `order_items`, `products`, `categories`, `payments`

**Concepts:** Aggregation, GROUP BY, Window Functions, CTE, YoY Growth, Pivot


---


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


---
