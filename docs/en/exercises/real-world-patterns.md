# Exercise: Real-World SQL Patterns

Analyze the built-in database views and practice advanced SQL patterns commonly used in business intelligence: revenue growth with LAG, Top-N per group with ROW_NUMBER, cart abandonment analysis, coupon ROI, and hourly order patterns.

> **Preparation:** Run `SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;` to see available views.

---

## Question 1 — View Analysis: Revenue Growth (LAG Pattern)

**Business question:** Analyze the `v_revenue_growth` view structure, then recreate it. Calculate monthly revenue and month-over-month growth rate using the `LAG` window function.

**Hints:**

- `LAG(revenue, 1) OVER (ORDER BY year_month)` references the previous month
- Growth = `(current - previous) / previous * 100`
- The first month has no previous data, so it returns NULL

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

    **Key pattern:** `LAG(value, N)` references the value N rows back. For year-over-year (YoY) comparison, use `LAG(revenue, 12)`.

---

## Question 2 — Top N Products per Category (ROW_NUMBER Pattern)

**Business question:** Select the top 3 products by revenue in each category. Write a query that matches the `v_top_products_by_category` view.

**Hints:**

- `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)`
- Rank in a CTE, then filter `WHERE rn <= 3` in the outer query

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

    **Key pattern:** `ROW_NUMBER` picks one per tie; `RANK` gives the same rank to ties. Choose based on your use case.

---

## Question 3 — Cart Abandonment Analysis

**Business question:** Marketing wants to understand "cart abandoners" — customers who added items but never ordered. Analyze total abandoned carts, lost revenue, and the top 10 most-abandoned products.

**Hints:**

- `carts.status = 'abandoned'`
- `cart_items` → `products` for product info
- Lost revenue = quantity × price

??? success "Answer"
    ```sql
    -- Abandonment summary
    SELECT
        COUNT(DISTINCT c.id)    AS abandoned_carts,
        COUNT(ci.id)            AS abandoned_items,
        ROUND(SUM(ci.quantity * p.price), 2) AS lost_revenue
    FROM carts AS c
    INNER JOIN cart_items AS ci ON c.id = ci.cart_id
    INNER JOIN products  AS p  ON ci.product_id = p.id
    WHERE c.status = 'abandoned';
    ```

    ```sql
    -- Top 10 most-abandoned products
    SELECT
        p.name AS product_name,
        cat.name AS category,
        COUNT(*) AS abandon_count,
        ROUND(SUM(ci.quantity * p.price), 2) AS lost_revenue
    FROM carts AS c
    INNER JOIN cart_items  AS ci  ON c.id = ci.cart_id
    INNER JOIN products   AS p   ON ci.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE c.status = 'abandoned'
    GROUP BY p.id, p.name, cat.name
    ORDER BY lost_revenue DESC
    LIMIT 10;
    ```

    **Key pattern:** Abandonment analysis measures "events that didn't happen." JOIN related data and aggregate to quantify the scale.

---

## Question 4 — Coupon Effectiveness Analysis

**Business question:** Compare orders with and without coupons by average order value. Calculate each coupon's usage count, total discount, and ROI (coupon revenue / discount amount).

**Hints:**

- `coupon_usage` → `coupons` for coupon info
- `coupon_usage` → `orders` for order amounts
- Non-coupon orders: orders not in `coupon_usage`

??? success "Answer"
    ```sql
    -- Coupon vs non-coupon orders
    WITH coupon_orders AS (
        SELECT DISTINCT order_id FROM coupon_usage
    )
    SELECT
        CASE WHEN co.order_id IS NOT NULL THEN 'With Coupon' ELSE 'Without Coupon' END AS segment,
        COUNT(*) AS order_count,
        ROUND(AVG(o.total_amount), 2) AS avg_order_value,
        ROUND(SUM(o.total_amount), 2) AS total_revenue
    FROM orders AS o
    LEFT JOIN coupon_orders AS co ON o.id = co.order_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY CASE WHEN co.order_id IS NOT NULL THEN 'With Coupon' ELSE 'Without Coupon' END;
    ```

    ```sql
    -- Per-coupon ROI
    SELECT
        cp.code,
        cp.type,
        cp.discount_value,
        COUNT(cu.id) AS usage_count,
        ROUND(SUM(cu.discount_amount), 2) AS total_discount,
        ROUND(SUM(o.total_amount), 2) AS coupon_revenue,
        ROUND(SUM(o.total_amount) / NULLIF(SUM(cu.discount_amount), 0), 1) AS roi
    FROM coupons AS cp
    INNER JOIN coupon_usage AS cu ON cp.id = cu.coupon_id
    INNER JOIN orders       AS o  ON cu.order_id = o.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY cp.id, cp.code, cp.type, cp.discount_value
    ORDER BY roi DESC;
    ```

    **Key pattern:** A/B comparison (coupon vs no-coupon) and ROI calculation are marketing analytics fundamentals. `LEFT JOIN` + `CASE` splits groups; `NULLIF` prevents division by zero.

---

## Question 5 — Hourly Order Patterns

**Business question:** Operations wants to identify peak ordering hours. Show order count, average order value, and weekend/weekday comparison by hour (0–23).

**Hints:**

- Hour: `CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)`
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

    **Expected insight:** Orders peak at lunch (12–13h) and evening (20–22h). Weekend mornings are quieter; late-night orders (2–5h) have lower average values.

---

## Bonus Challenge

Combine hourly and daily analysis into a **24 (hours) × 7 (days) heatmap matrix**. Each cell shows the order count.

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
