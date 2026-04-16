# Real-World SQL Patterns

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `categories` — Categories (parent-child hierarchy)  

    `reviews` — Reviews (rating, content)  

    `carts` — Carts (status)  

    `cart_items` — Cart items (quantity)  

    `coupons` — Coupons (discount, validity)  

    `coupon_usage` — Coupon usage records  



!!! abstract "Concepts"

    `LAG`, `ROW_NUMBER`, `Cart Abandonment`, `Coupon ROI`, `Time Pattern`



### 1. View Analysis: Revenue Growth (LAG Pattern)


Analyze the v_revenue_growth view structure and recreate it.
Calculate monthly revenue and month-over-month growth rate using LAG window function.


**Hint 1:** - Use `LAG(revenue, 1) OVER (ORDER BY year_month)` for previous month revenue
- Growth = `(current - previous) / previous * 100`
- First month will be NULL (no previous data)



??? success "Answer"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 2) AS revenue,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        order_count,
        LAG(revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
        ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY year_month))
            / LAG(revenue, 1) OVER (ORDER BY year_month), 1) AS mom_growth_pct
    FROM monthly
    ORDER BY year_month;
    ```


    **Result** (top 7 of 120 rows)

    | year_month | revenue | order_count | prev_month_revenue | mom_growth_pct |
    |---|---|---|---|---|
    | 2016-01 | 14,194,769.00 | 34 | NULL | NULL |
    | 2016-02 | 12,984,335.00 | 23 | 14,194,769.00 | -8.50 |
    | 2016-03 | 14,154,562.00 | 29 | 12,984,335.00 | 9.00 |
    | 2016-04 | 16,878,372.00 | 30 | 14,154,562.00 | 19.20 |
    | 2016-05 | 28,570,768.00 | 37 | 16,878,372.00 | 69.30 |
    | 2016-06 | 23,793,991.00 | 30 | 28,570,768.00 | -16.70 |
    | 2016-07 | 29,696,984.00 | 29 | 23,793,991.00 | 24.80 |


---


### 2. Top N Products per Category (ROW_NUMBER Pattern)


Select the top 3 products by revenue in each category.


**Hint 1:** - `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)`
- Rank in CTE, filter `WHERE rn <= 3` in outer query



??? success "Answer"
    ```sql
    WITH product_sales AS (
        SELECT
            cat.name AS category,
            p.name AS product_name,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
            SUM(oi.quantity) AS units_sold
        FROM order_items AS oi
        INNER JOIN orders     AS o   ON oi.order_id   = o.id
        INNER JOIN products   AS p   ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY cat.name, p.name
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn
        FROM product_sales
    )
    SELECT category, product_name, revenue, units_sold, rn AS rank
    FROM ranked
    WHERE rn <= 3
    ORDER BY category, rn;
    ```


    **Result** (top 7 of 109 rows)

    | category | product_name | revenue | units_sold | rank |
    |---|---|---|---|---|
    | 2-in-1 | Lenovo ThinkPad X1 2in1 Silver | 554,231,700.00 | 297 | 1 |
    | 2-in-1 | HP Envy x360 15 Silver | 326,727,400.00 | 269 | 2 |
    | 2-in-1 | HP Pavilion x360 14 Black | 319,615,200.00 | 216 | 3 |
    | AMD | AMD Ryzen 9 9900X | 601,913,300.00 | 1600 | 1 |
    | AMD | MSI Radeon RX 7900 XTX GAMING X White | 585,793,600.00 | 386 | 2 |
    | AMD | ASUS Dual RX 9070 Silver | 515,058,400.00 | 383 | 3 |
    | AMD Socket | ASRock X670E Steel Legend Silver | 370,658,400.00 | 704 | 1 |


---


### 3. Cart Abandonment Analysis


Analyze abandoned carts: total count, lost revenue,
and top 10 most-abandoned products.


**Hint 1:** - Filter `carts.status = 'abandoned'`
- JOIN `cart_items` -> `products` for product info
- Lost revenue = quantity x price



??? success "Answer"
    ```sql
    -- 이탈 장바구니 요약
    SELECT
        COUNT(DISTINCT c.id)    AS abandoned_carts,
        COUNT(ci.id)            AS abandoned_items,
        ROUND(SUM(ci.quantity * p.price), 2) AS lost_revenue
    FROM carts AS c
    INNER JOIN cart_items AS ci ON c.id = ci.cart_id
    INNER JOIN products  AS p  ON ci.product_id = p.id
    WHERE c.status = 'abandoned';
    ```


    **Result** (1 rows)

    | abandoned_carts | abandoned_items | lost_revenue |
    |---|---|---|
    | 899 | 2747 | 2,618,976,000.00 |


---


### 4. Coupon Effectiveness Analysis


Compare average order value between coupon and non-coupon orders.
Calculate usage count, total discount, and ROI per coupon.


**Hint 1:** - JOIN `coupon_usage` -> `coupons` for coupon details
- Non-coupon orders: orders not in `coupon_usage`
- ROI = revenue / discount amount



??? success "Answer"
    ```sql
    -- 쿠폰 사용 vs 미사용 주문 비교
    WITH coupon_orders AS (
        SELECT DISTINCT order_id FROM coupon_usage
    )
    SELECT
        CASE WHEN co.order_id IS NOT NULL THEN '쿠폰 사용' ELSE '쿠폰 미사용' END AS segment,
        COUNT(*) AS order_count,
        ROUND(AVG(o.total_amount), 2) AS avg_order_value,
        ROUND(SUM(o.total_amount), 2) AS total_revenue
    FROM orders AS o
    LEFT JOIN coupon_orders AS co ON o.id = co.order_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY CASE WHEN co.order_id IS NOT NULL THEN '쿠폰 사용' ELSE '쿠폰 미사용' END;
    ```


    **Result** (2 rows)

    | segment | order_count | avg_order_value | total_revenue |
    |---|---|---|---|
    | 쿠폰 미사용 | 33,034 | 981,325.10 | 32,417,093,466.00 |
    | 쿠폰 사용 | 1664 | 1,413,662.58 | 2,352,334,541.00 |


---


### 5. Hourly Order Patterns


Show order count, average order value, and weekend/weekday comparison by hour (0-23).


**Hint 1:** - Extract hour: `CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)`
- Day of week: `CAST(STRFTIME('%w', ordered_at) AS INTEGER)` (0=Sun, 6=Sat)
- Weekend: 0 (Sun) and 6 (Sat)



??? success "Answer"
    ```sql
    SELECT
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        COUNT(*) AS order_count,
        ROUND(AVG(total_amount), 2) AS avg_order_value,
        SUM(CASE WHEN CAST(STRFTIME('%w', ordered_at) AS INTEGER) IN (0, 6)
            THEN 1 ELSE 0 END) AS weekend_orders,
        SUM(CASE WHEN CAST(STRFTIME('%w', ordered_at) AS INTEGER) NOT IN (0, 6)
            THEN 1 ELSE 0 END) AS weekday_orders,
        ROUND(1.0 * SUM(CASE WHEN CAST(STRFTIME('%w', ordered_at) AS INTEGER) IN (0, 6) THEN 1 ELSE 0 END)
            / NULLIF(SUM(CASE WHEN CAST(STRFTIME('%w', ordered_at) AS INTEGER) NOT IN (0, 6) THEN 1 ELSE 0 END), 0), 2)
            AS weekend_weekday_ratio
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY hour;
    ```


    **Result** (top 7 of 24 rows)

    | hour | order_count | avg_order_value | weekend_orders | weekday_orders | weekend_weekday_ratio |
    |---|---|---|---|---|---|
    | 0 | 451 | 987,171.96 | 123 | 328 | 0.38 |
    | 1 | 327 | 1,008,633.48 | 102 | 225 | 0.45 |
    | 2 | 158 | 963,984.31 | 45 | 113 | 0.4 |
    | 3 | 188 | 1,068,912.30 | 52 | 136 | 0.38 |
    | 4 | 185 | 1,076,325.90 | 62 | 123 | 0.5 |
    | 5 | 345 | 1,165,922.99 | 95 | 250 | 0.38 |
    | 6 | 606 | 922,406.57 | 196 | 410 | 0.48 |


---


### 6. Bonus: 24-Hour x 7-Day Heatmap


Create an order count heatmap matrix: 24 hours x 7 days of week.


**Hint 1:** - 24 rows (hours) x 7 columns (days) + total
- `SUM(CASE WHEN STRFTIME('%w', ...) = 'N' THEN 1 ELSE 0 END)`



??? success "Answer"
    ```sql
    SELECT
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '1' THEN 1 ELSE 0 END) AS mon,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '2' THEN 1 ELSE 0 END) AS tue,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '3' THEN 1 ELSE 0 END) AS wed,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '4' THEN 1 ELSE 0 END) AS thu,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '5' THEN 1 ELSE 0 END) AS fri,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '6' THEN 1 ELSE 0 END) AS sat,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '0' THEN 1 ELSE 0 END) AS sun,
        COUNT(*) AS total
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY hour;
    ```


    **Result** (top 7 of 24 rows)

    | hour | mon | tue | wed | thu | fri | sat | sun | total |
    |---|---|---|---|---|---|---|---|---|
    | 0 | 69 | 67 | 60 | 62 | 70 | 66 | 57 | 451 |
    | 1 | 48 | 58 | 38 | 37 | 44 | 51 | 51 | 327 |
    | 2 | 22 | 25 | 17 | 23 | 26 | 25 | 20 | 158 |
    | 3 | 28 | 36 | 21 | 26 | 25 | 27 | 25 | 188 |
    | 4 | 28 | 14 | 27 | 31 | 23 | 26 | 36 | 185 |
    | 5 | 57 | 42 | 49 | 53 | 49 | 56 | 39 | 345 |
    | 6 | 101 | 77 | 70 | 68 | 94 | 90 | 106 | 606 |


---
