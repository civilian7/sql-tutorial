# Real-World SQL Patterns

!!! info "Tables"

    `orders` — Orders (status, amount, date)  ·  `order_items` — Order items (qty, unit price)  ·  `products` — Products (name, price, stock, brand)  ·  `categories` — Categories (parent-child hierarchy)  ·  `reviews` — Reviews (rating, content)  ·  `carts` — Carts (status)  ·  `cart_items` — Cart items (quantity)  ·  `coupons` — Coupons (discount, validity)  ·  `coupon_usage` — Coupon usage records


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


---
