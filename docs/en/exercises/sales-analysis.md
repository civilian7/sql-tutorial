# Exercise: Sales Analysis

Apply everything you have learned to answer five realistic business questions about TechShop's sales performance. Each question builds on the previous one. Try to write the query yourself before revealing the answer.

These exercises are deliberately open-ended — there may be more than one valid approach. Focus on getting correct results first, then consider clarity and efficiency.

---

## Question 1 — Monthly Sales Trend (2022–2024)

**Business question:** The CEO wants a monthly revenue report for the past three years. Show each month's revenue, number of orders, and average order value. Exclude cancelled and returned orders.

**Hints:**
- Use `SUBSTR(ordered_at, 1, 7)` for the month
- Use `SUM`, `COUNT`, and `AVG`
- Filter the year range with `BETWEEN` or `LIKE`

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

    **Expected shape:** 36 rows (one per month), revenue growing over time with peaks in November–December each year.

---

## Question 2 — Top 10 Products by Revenue (2024)

**Business question:** The merchandising team wants to know which products drove the most revenue in 2024. They need the product name, category, units sold, total revenue, and average customer rating.

**Hints:**
- Join `order_items` → `orders` → `products` → `categories`
- Use a `LEFT JOIN` for `reviews` so unreviewed products still appear
- Filter for 2024 non-cancelled orders
- Group by product

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

## Question 3 — Seasonal Patterns

**Business question:** Does TechShop have seasonal sales patterns? Calculate the average monthly revenue for each calendar month (January through December) across all years. Identify the peak and slowest months.

**Hints:**
- Use `SUBSTR(ordered_at, 6, 2)` to extract the month number (01–12)
- Average the `SUM` across years using a derived table
- Use `CASE` to convert month numbers to names

??? success "Answer"
    ```sql
    -- Step 1: Get monthly revenue per year-month
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7)  AS year_month,
            SUBSTR(ordered_at, 6, 2)  AS month_num,
            SUM(total_amount)         AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    -- Step 2: Average across years, grouped by calendar month
    SELECT
        CASE month_num
            WHEN '01' THEN 'January'   WHEN '02' THEN 'February'
            WHEN '03' THEN 'March'     WHEN '04' THEN 'April'
            WHEN '05' THEN 'May'       WHEN '06' THEN 'June'
            WHEN '07' THEN 'July'      WHEN '08' THEN 'August'
            WHEN '09' THEN 'September' WHEN '10' THEN 'October'
            WHEN '11' THEN 'November'  WHEN '12' THEN 'December'
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

    **Expected insight:** November and December should show the highest averages (holiday shopping). July–August may show a slight dip. March shows a secondary peak (spring tech refresh / back-to-school prep).

---

## Question 4 — Payment Method Analysis

**Business question:** The finance team wants to understand how customers pay. For each payment method, show the number of transactions, total collected, average transaction value, and what percentage of total revenue each method represents.

**Hints:**
- Join `payments` to `orders` for the order date
- Use `SUM(...) OVER ()` (a window function) for the grand total, or compute it with a subquery
- `ROUND(..., 1)` for percentages

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

    **Expected insight:** Card payments should dominate. Digital wallets (kakao_pay, naver_pay) should show strong average transaction values. Point-only payments should have very low averages.

---

## Question 5 — Year-over-Year Revenue Growth by Category

**Business question:** The board wants a YoY growth report by product category for 2023 and 2024. Show each category's revenue for both years and the percentage change.

**Hints:**
- Use conditional aggregation (`SUM(CASE WHEN ... THEN ... END)`) for each year's revenue
- Or use two CTEs — one per year — joined on `category_id`
- Compute YoY% as `(2024 - 2023) / 2023 * 100`
- Use `NULLIF` to avoid division by zero

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

    **Expected insight:** Categories tied to AI/productivity hardware (laptops, storage) should show strong growth. Commodity accessories may show flat or negative growth as market saturation increases.

---

## Bonus Challenge

Combine Questions 3 and 5: build a heatmap table showing revenue for each **category** (rows) × each **month** (columns) for 2024 only. Use conditional aggregation with 12 `SUM(CASE WHEN month = 'XX' ...)` columns.

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
