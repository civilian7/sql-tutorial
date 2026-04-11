# DB Object Design

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `orders` — Order<br>
    `order_items` — Order Details<br>
    `products` — Product<br>
    `customers` — Customer<br>
    `categories` — Category<br>
    `reviews` — Review<br>
    `inventory_transactions` — Incoming/outgoing history<br>
    `staff` — Employee<br>
    `payments` — Payment

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    `CREATE VIEW`<br>
    View query<br>
    `DROP VIEW`<br>
    `CREATE TRIGGER` (AFTER/BEFORE<br>
    INSERT/UPDATE/DELETE<br>
    WHEN<br>
    OLD/NEW)<br>
    Audit Logging<br>
    Stored procedure concepts (MySQL/PG)

</div>

!!! info "Before You Begin"
    This exercise puts into practice what you learned in **Advanced Lesson 22** (Views), **Lecture 24** (Trigger), and **Lecture 26** (Stored Procedures).
    Views and triggers can be run in SQLite.
    Stored procedure questions (15-20) are provided under the MySQL/PostgreSQL tab.

---

## Views (1~7)

Practice creating, using, and managing views.

---

### Problem 1

**Create monthly sales summary views.**

View name: `v_monthly_revenue`. Columns: Year Month, Number of Orders, Total Sales, Average Order Amount.
Excludes canceled/returned orders.

??? tip "Hint"
    Define the view as `CREATE VIEW v_monthly_revenue AS SELECT ...`.
    You can use `GROUP BY` inside a view.

??? success "Answer"
    ```sql
    CREATE VIEW v_monthly_revenue AS
    SELECT
        SUBSTR(ordered_at, 1, 7)   AS year_month,
        COUNT(*)                    AS order_count,
        ROUND(SUM(total_amount), 0) AS total_revenue,
        ROUND(AVG(total_amount), 0) AS avg_order_value
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(ordered_at, 1, 7);
    ```

    ```sql
    -- Using the view
    SELECT *
    FROM v_monthly_revenue
    WHERE year_month LIKE '2024%'
    ORDER BY year_month;
    ```

    **Result example:**

    | year_month | order_count | total_revenue | avg_order_value |
    |---|---|---|---|
    | 2024-01 | 580 | 98500000 | 169828 |
    | 2024-02 | 520 | 87200000 | 167692 |
    | ... | ... | ... | ... |
    | 2024-12 | 890 | 145600000 | 163596 |

---

### Problem 2

**Create a customer dashboard view**

View name: `v_customer_dashboard`. Includes basic information for each customer, total number of orders, total purchase amount, last order date, and number of reviews.

??? tip "Hint"
    Linking orders and reviews with `LEFT JOIN` may cause double counting issues.
    It is safer to aggregate each by subquery or CTE and then join.

??? success "Answer"
    ```sql
    CREATE VIEW v_customer_dashboard AS
    WITH order_stats AS (
        SELECT
            customer_id,
            COUNT(*)              AS order_count,
            ROUND(SUM(total_amount), 0) AS total_spent,
            MAX(ordered_at)       AS last_order_date
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    review_stats AS (
        SELECT
            customer_id,
            COUNT(*) AS review_count
        FROM reviews
        GROUP BY customer_id
    )
    SELECT
        c.id              AS customer_id,
        c.name,
        c.email,
        c.grade,
        c.created_at      AS signup_date,
        COALESCE(os.order_count, 0)   AS order_count,
        COALESCE(os.total_spent, 0)   AS total_spent,
        os.last_order_date,
        COALESCE(rs.review_count, 0)  AS review_count
    FROM customers AS c
    LEFT JOIN order_stats  AS os ON c.id = os.customer_id
    LEFT JOIN review_stats AS rs ON c.id = rs.customer_id;
    ```

    ```sql
    -- Query VIP customers
    SELECT *
    FROM v_customer_dashboard
    WHERE grade = 'VIP'
    ORDER BY total_spent DESC
    LIMIT 10;
    ```

    **Result example (top 3 rows):**

    | customer_id | name | email | grade | signup_date | order_count | total_spent | last_order_date | review_count |
    |---|---|---|---|---|---|---|---|---|
    | 12 | Kim... | user012@testmail.kr | VIP | 2016-08-... | 35 | 12500000 | 2025-11-... | 18 |
    | 45 | Park... | user045@testmail.kr | VIP | 2017-02-... | 28 | 10800000 | 2025-10-... | 12 |
    | 78 | Lee... | user078@testmail.kr | VIP | 2016-12-... | 31 | 9950000 | 2025-12-... | 15 |

---

### Problem 3

**Create product performance views and use them to analyze sales efficiency relative to inventory.**

View name: `v_product_performance`. Includes total sales, revenue, current inventory, and average rating for each product.

??? tip "Hint"
    When creating a view, also include products without reviews as `LEFT JOIN`.
    When querying a view, you can add derived columns such as "Inventory Turnover" (`units_sold / stock_qty`).

??? success "Answer"
    ```sql
    CREATE VIEW v_product_performance AS
    SELECT
        p.id              AS product_id,
        p.name            AS product_name,
        cat.name          AS category,
        p.price,
        p.stock_qty,
        COALESCE(SUM(oi.quantity), 0) AS total_sold,
        COALESCE(ROUND(SUM(oi.quantity * oi.unit_price), 0), 0) AS total_revenue,
        COALESCE(r.review_count, 0)   AS review_count,
        r.avg_rating
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LEFT JOIN order_items AS oi ON p.id = oi.product_id
    LEFT JOIN orders AS o ON oi.order_id = o.id
        AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    LEFT JOIN (
        SELECT
            product_id,
            COUNT(*) AS review_count,
            ROUND(AVG(rating), 2) AS avg_rating
        FROM reviews
        GROUP BY product_id
    ) AS r ON p.id = r.product_id
    WHERE p.is_active = 1
    GROUP BY p.id, p.name, cat.name, p.price, p.stock_qty,
             r.review_count, r.avg_rating;
    ```

    ```sql
    -- Analyze sales efficiency relative to inventory
    SELECT
        product_name,
        category,
        total_sold,
        stock_qty,
        CASE
            WHEN stock_qty > 0
            THEN ROUND(1.0 * total_sold / stock_qty, 2)
            ELSE NULL
        END AS turnover_ratio,
        total_revenue,
        avg_rating
    FROM v_product_performance
    WHERE total_sold > 0
    ORDER BY turnover_ratio DESC
    LIMIT 10;
    ```

    **Result example (top 3 rows):**

    | product_name | category | total_sold | stock_qty | turnover_ratio | total_revenue | avg_rating |
    |---|---|---|---|---|---|---|
    | Samsung DDR4 32GB | RAM | 450 | 35 | 12.86 | 22095000 | 4.52 |
    | Logitech MX Keys | Keyboard | 380 | 42 | 9.05 | 45220000 | 4.68 |
    | ... | ... | ... | ... | ... | ... | ... |

---

### Problem 4

**Nested query using views — Find year-on-year growth rate in monthly sales view.**

Self-join the `v_monthly_revenue` created earlier.

??? tip "Hint"
    It references `v_monthly_revenue` twice.
    JOIN condition: The "month part" of the current month is the same as the "month part" of the previous year, and the year is 1 different.
    Extract the month part with `SUBSTR(year_month, 6, 2)` and the year with `SUBSTR(year_month, 1, 4)`.

??? success "Answer"
    ```sql
    SELECT
        curr.year_month,
        curr.total_revenue      AS current_revenue,
        prev.total_revenue      AS prev_year_revenue,
        curr.total_revenue - prev.total_revenue AS diff,
        ROUND(100.0 * (curr.total_revenue - prev.total_revenue)
            / prev.total_revenue, 1) AS yoy_growth_pct
    FROM v_monthly_revenue AS curr
    INNER JOIN v_monthly_revenue AS prev
        ON SUBSTR(curr.year_month, 6, 2) = SUBSTR(prev.year_month, 6, 2)
       AND CAST(SUBSTR(curr.year_month, 1, 4) AS INTEGER)
         = CAST(SUBSTR(prev.year_month, 1, 4) AS INTEGER) + 1
    WHERE curr.year_month LIKE '2024%'
    ORDER BY curr.year_month;
    ```

    **Result example (partial):**

    | year_month | current_revenue | prev_year_revenue | diff | yoy_growth_pct |
    |---|---|---|---|---|
    | 2024-01 | 98500000 | 85000000 | 13500000 | 15.9 |
    | 2024-02 | 87200000 | 78000000 | 9200000 | 11.8 |
    | ... | ... | ... | ... | ... |

---

### Problem 5

**Check the list of all views that currently exist in the DB.**

It uses SQLite's system catalog.

??? tip "Hint"
    In SQLite, all DB object information is stored in the `sqlite_master` table.
    Filter by `type = 'view'`.

??? success "Answer"
    ```sql
    SELECT
        name,
        type,
        sql
    FROM sqlite_master
    WHERE type = 'view'
    ORDER BY name;
    ```

    **Result example:**

    | name | type | sql |
    | ---------- | ---------- | ---------- |
    | v_cart_abandonment | view | CREATE VIEW v_cart_abandonment AS
    SELECT
        c.id AS cart_id,
        cust.name AS customer_name,
        cust.email,
        c.status,
        c.created_at,
        COUNT(ci.id) AS item_count,
        CAST(SUM(p.price * ci.quantity) AS INTEGER) AS potential_revenue,
        GROUP_CONCAT(p.name, ', ') AS products
    FROM carts c
    JOIN customers cust ON c.customer_id = cust.id
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.status = 'abandoned'
    GROUP BY c.id |
    | v_category_tree | view | CREATE VIEW v_category_tree AS
    WITH RECURSIVE tree AS (
        SELECT id, name, parent_id, depth,
               name AS full_path,
               CAST(printf('%04d', sort_order) AS TEXT) AS sort_key
        FROM categories
        WHERE parent_id IS NULL
        UNION ALL
        SELECT c.id, c.name, c.parent_id, c.depth,
               tree.full_path || ' > ' || c.name,
               tree.sort_key || '.' || printf('%04d', c.sort_order)
        FROM categories c
        JOIN tree ON c.parent_id = tree.id
    )
    SELECT t.id, t.name, t.parent_id, t.depth, t.full_path,
           COALESCE(p.product_count, 0) AS product_count
    FROM tree t
    LEFT JOIN (
        SELECT category_id, COUNT(*) AS product_count
        FROM products
        GROUP BY category_id
    ) p ON t.id = p.category_id
    ORDER BY t.sort_key |
    | v_coupon_effectiveness | view | CREATE VIEW v_coupon_effectiveness AS
    SELECT
        cp.id AS coupon_id,
        cp.code,
        cp.name,
        cp.type,
        cp.discount_value,
        cp.is_active,
        COALESCE(u.usage_count, 0) AS usage_count,
        cp.usage_limit,
        COALESCE(u.total_discount, 0) AS total_discount_given,
        COALESCE(u.total_order_revenue, 0) AS total_order_revenue,
        CASE
            WHEN COALESCE(u.total_discount, 0) > 0
            THEN ROUND(u.total_order_revenue / u.total_discount, 1)
            ELSE 0
        END AS roi_ratio
    FROM coupons cp
    LEFT JOIN (
        SELECT
            cu.coupon_id,
            COUNT(*) AS usage_count,
            CAST(SUM(cu.discount_amount) AS INTEGER) AS total_discount,
            CAST(SUM(o.total_amount) AS INTEGER) AS total_order_revenue
        FROM coupon_usage cu
        JOIN orders o ON cu.order_id = o.id
        GROUP BY cu.coupon_id
    ) u ON cp.id = u.coupon_id
    ORDER BY COALESCE(u.usage_count, 0) DESC |
    | v_customer_rfm | view | CREATE VIEW v_customer_rfm AS
    WITH rfm_raw AS (
        SELECT
            c.id AS customer_id,
            c.name,
            c.grade,
            CAST(julianday('2025-06-30') - julianday(MAX(o.ordered_at)) AS INTEGER) AS recency_days,
            COUNT(o.id) AS frequency,
            CAST(SUM(o.total_amount) AS INTEGER) AS monetary
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY c.id
    ),
    rfm_scored AS (
        SELECT *,
            NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,   -- more recent = higher score
            NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
            NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
        FROM rfm_raw
    )
    SELECT
        customer_id, name, grade,
        recency_days, frequency, monetary,
        r_score, f_score, m_score,
        r_score + f_score + m_score AS rfm_total,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Others'
        END AS segment
    FROM rfm_scored |
    | v_customer_summary | view | CREATE VIEW v_customer_summary AS
    SELECT
        c.id,
        c.name,
        c.email,
        c.grade,
        c.gender,
        CASE
            WHEN c.birth_date IS NULL THEN NULL
            ELSE CAST((julianday('2025-06-30') - julianday(c.birth_date)) / 365.25 AS INTEGER)
        END AS age,
        c.created_at AS joined_at,
        COALESCE(os.order_count, 0) AS total_orders,
        COALESCE(os.total_spent, 0) AS total_spent,
        COALESCE(os.first_order, '') AS first_order_at,
        COALESCE(os.last_order, '') AS last_order_at,
        COALESCE(rv.review_count, 0) AS review_count,
        COALESCE(rv.avg_rating, 0) AS avg_rating_given,
        COALESCE(ws.wishlist_count, 0) AS wishlist_count,
        c.is_active,
        c.last_login_at,
        CASE
            WHEN c.is_active = 0 THEN 'inactive'
            WHEN c.last_login_at IS NULL THEN 'never_logged_in'
            WHEN c.last_login_at < DATE('2025-06-30', '-365 days') THEN 'dormant'
            ELSE 'active'
        END AS activity_status
    FROM customers c
    LEFT JOIN (
        SELECT customer_id,
               COUNT(*) AS order_count,
               CAST(SUM(total_amount) AS INTEGER) AS total_spent,
               MIN(ordered_at) AS first_order,
               MAX(ordered_at) AS last_order
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ) os ON c.id = os.customer_id
    LEFT JOIN (
        SELECT customer_id,
               COUNT(*) AS review_count,
               ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews
        GROUP BY customer_id
    ) rv ON c.id = rv.customer_id
    LEFT JOIN (
        SELECT customer_id, COUNT(*) AS wishlist_count
        FROM wishlists
        GROUP BY customer_id
    ) ws ON c.id = ws.customer_id |
    | v_daily_orders | view | CREATE VIEW v_daily_orders AS
    SELECT
        DATE(ordered_at) AS order_date,
        CASE CAST(strftime('%w', ordered_at) AS INTEGER)
            WHEN 0 THEN '일' WHEN 1 THEN '월' WHEN 2 THEN '화'
            WHEN 3 THEN '수' WHEN 4 THEN '목' WHEN 5 THEN '금' WHEN 6 THEN '토'
        END AS day_of_week,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
        SUM(CASE WHEN status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returned,
        CAST(SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS INTEGER) AS revenue,
        CAST(AVG(CASE WHEN status != 'cancelled' THEN total_amount END) AS INTEGER) AS avg_order_amount
    FROM orders
    GROUP BY DATE(ordered_at)
    ORDER BY order_date |
    | v_hourly_pattern | view | CREATE VIEW v_hourly_pattern AS
    SELECT
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        COUNT(*) AS order_count,
        CAST(AVG(total_amount) AS INTEGER) AS avg_amount,
        CASE
            WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 0 AND 5 THEN 'dawn'
            WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 6 AND 11 THEN 'morning'
            WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 12 AND 17 THEN 'afternoon'
            ELSE 'evening'
        END AS time_slot
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY hour |
    | v_monthly_sales | view | CREATE VIEW v_monthly_sales AS
    SELECT
        SUBSTR(o.ordered_at, 1, 7) AS month,               -- YYYY-MM
        COUNT(DISTINCT o.id) AS order_count,                -- number of orders
        COUNT(DISTINCT o.customer_id) AS customer_count,    -- unique buyers
        CAST(SUM(o.total_amount) AS INTEGER) AS revenue,    -- total revenue
        CAST(AVG(o.total_amount) AS INTEGER) AS avg_order,  -- average order value
        SUM(o.discount_amount) AS total_discount            -- total discount
    FROM orders o
    WHERE o.status NOT IN ('cancelled')
    GROUP BY SUBSTR(o.ordered_at, 1, 7)
    ORDER BY month |
    | ... | ... | ... |
    SELECT
        c.id AS cart_id,
        cust.name AS customer_name,
        cust.email,
        c.status,
        c.created_at,
        COUNT(ci.id) AS item_count,
        CAST(SUM(p.price * ci.quantity) AS INTEGER) AS potential_revenue,
        GROUP_CONCAT(p.name, ', ') AS products
    FROM carts c
    JOIN customers cust ON c.customer_id = cust.id
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.status = 'abandoned'
    GROUP BY c.id |
    | v_category_tree | view | CREATE VIEW v_category_tree AS
    WITH RECURSIVE tree AS (
        SELECT id, name, parent_id, depth,
               name AS full_path,
               CAST(printf('%04d', sort_order) AS TEXT) AS sort_key
        FROM categories
        WHERE parent_id IS NULL
        UNION ALL
        SELECT c.id, c.name, c.parent_id, c.depth,
               tree.full_path || ' > ' || c.name,
               tree.sort_key || '.' || printf('%04d', c.sort_order)
        FROM categories c
        JOIN tree ON c.parent_id = tree.id
    )
    SELECT t.id, t.name, t.parent_id, t.depth, t.full_path,
           COALESCE(p.product_count, 0) AS product_count
    FROM tree t
    LEFT JOIN (
        SELECT category_id, COUNT(*) AS product_count
        FROM products
        GROUP BY category_id
    ) p ON t.id = p.category_id
    ORDER BY t.sort_key |
    | v_coupon_effectiveness | view | CREATE VIEW v_coupon_effectiveness AS
    SELECT
        cp.id AS coupon_id,
        cp.code,
        cp.name,
        cp.type,
        cp.discount_value,
        cp.is_active,
        COALESCE(u.usage_count, 0) AS usage_count,
        cp.usage_limit,
        COALESCE(u.total_discount, 0) AS total_discount_given,
        COALESCE(u.total_order_revenue, 0) AS total_order_revenue,
        CASE
            WHEN COALESCE(u.total_discount, 0) > 0
            THEN ROUND(u.total_order_revenue / u.total_discount, 1)
            ELSE 0
        END AS roi_ratio
    FROM coupons cp
    LEFT JOIN (
        SELECT
            cu.coupon_id,
            COUNT(*) AS usage_count,
            CAST(SUM(cu.discount_amount) AS INTEGER) AS total_discount,
            CAST(SUM(o.total_amount) AS INTEGER) AS total_order_revenue
        FROM coupon_usage cu
        JOIN orders o ON cu.order_id = o.id
        GROUP BY cu.coupon_id
    ) u ON cp.id = u.coupon_id
    ORDER BY COALESCE(u.usage_count, 0) DESC |
    | v_customer_rfm | view | CREATE VIEW v_customer_rfm AS
    WITH rfm_raw AS (
        SELECT
            c.id AS customer_id,
            c.name,
            c.grade,
            CAST(julianday('2025-06-30') - julianday(MAX(o.ordered_at)) AS INTEGER) AS recency_days,
            COUNT(o.id) AS frequency,
            CAST(SUM(o.total_amount) AS INTEGER) AS monetary
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY c.id
    ),
    rfm_scored AS (
        SELECT *,
            NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,   -- more recent = higher score
            NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
            NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
        FROM rfm_raw
    )
    SELECT
        customer_id, name, grade,
        recency_days, frequency, monetary,
        r_score, f_score, m_score,
        r_score + f_score + m_score AS rfm_total,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Others'
        END AS segment
    FROM rfm_scored |
    | v_customer_summary | view | CREATE VIEW v_customer_summary AS
    SELECT
        c.id,
        c.name,
        c.email,
        c.grade,
        c.gender,
        CASE
            WHEN c.birth_date IS NULL THEN NULL
            ELSE CAST((julianday('2025-06-30') - julianday(c.birth_date)) / 365.25 AS INTEGER)
        END AS age,
        c.created_at AS joined_at,
        COALESCE(os.order_count, 0) AS total_orders,
        COALESCE(os.total_spent, 0) AS total_spent,
        COALESCE(os.first_order, '') AS first_order_at,
        COALESCE(os.last_order, '') AS last_order_at,
        COALESCE(rv.review_count, 0) AS review_count,
        COALESCE(rv.avg_rating, 0) AS avg_rating_given,
        COALESCE(ws.wishlist_count, 0) AS wishlist_count,
        c.is_active,
        c.last_login_at,
        CASE
            WHEN c.is_active = 0 THEN 'inactive'
            WHEN c.last_login_at IS NULL THEN 'never_logged_in'
            WHEN c.last_login_at < DATE('2025-06-30', '-365 days') THEN 'dormant'
            ELSE 'active'
        END AS activity_status
    FROM customers c
    LEFT JOIN (
        SELECT customer_id,
               COUNT(*) AS order_count,
               CAST(SUM(total_amount) AS INTEGER) AS total_spent,
               MIN(ordered_at) AS first_order,
               MAX(ordered_at) AS last_order
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ) os ON c.id = os.customer_id
    LEFT JOIN (
        SELECT customer_id,
               COUNT(*) AS review_count,
               ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews
        GROUP BY customer_id
    ) rv ON c.id = rv.customer_id
    LEFT JOIN (
        SELECT customer_id, COUNT(*) AS wishlist_count
        FROM wishlists
        GROUP BY customer_id
    ) ws ON c.id = ws.customer_id |
    | v_daily_orders | view | CREATE VIEW v_daily_orders AS
    SELECT
        DATE(ordered_at) AS order_date,
        CASE CAST(strftime('%w', ordered_at) AS INTEGER)
            WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN ‘Wed’ WHEN 4 THEN ‘Thurs’ WHEN 5 THEN ‘Fri’ WHEN 6 THEN ‘Sat’
        END AS day_of_week,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
        SUM(CASE WHEN status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returned,
        CAST(SUM(CASE WHEN status != 'cancelled' THEN total_amount ELSE 0 END) AS INTEGER) AS revenue,
        CAST(AVG(CASE WHEN status != 'cancelled' THEN total_amount END) AS INTEGER) AS avg_order_amount
    FROM orders
    GROUP BY DATE(ordered_at)
    ORDER BY order_date |
    | v_hourly_pattern | view | CREATE VIEW v_hourly_pattern AS
    SELECT
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        COUNT(*) AS order_count,
        CAST(AVG(total_amount) AS INTEGER) AS avg_amount,
        CASE
            WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 0 AND 5 THEN 'dawn'
            WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 6 AND 11 THEN 'morning'
            WHEN CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) BETWEEN 12 AND 17 THEN 'afternoon'
            ELSE 'evening'
        END AS time_slot
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY hour |
    | v_monthly_sales | view | CREATE VIEW v_monthly_sales AS
    SELECT
        SUBSTR(o.ordered_at, 1, 7) AS month,               -- YYYY-MM
        COUNT(DISTINCT o.id) AS order_count,                -- number of orders
        COUNT(DISTINCT o.customer_id) AS customer_count,    -- unique buyers
        CAST(SUM(o.total_amount) AS INTEGER) AS revenue,    -- total revenue
        CAST(AVG(o.total_amount) AS INTEGER) AS avg_order,  -- average order value
        SUM(o.discount_amount) AS total_discount            -- total discount
    FROM orders o
    WHERE o.status NOT IN ('cancelled')
    GROUP BY SUBSTR(o.ordered_at, 1, 7)
    ORDER BY month |
    | ... | ... | ... |

    > The entire definition (DDL) of the view is stored in the `sql` column.

---

### Problem 6

**Drop the view and recreate it (DROP + CREATE).**

Regenerate the `v_monthly_revenue` view by adding a column for increase/decrease compared to the previous month.

??? tip "Hint"
    SQLite does not support `ALTER VIEW`, so delete and recreate it as `DROP VIEW IF EXISTS`.
    You can use the window function `LAG` inside a view definition.

??? success "Answer"
    ```sql
    DROP VIEW IF EXISTS v_monthly_revenue;

    CREATE VIEW v_monthly_revenue AS
    WITH base AS (
        SELECT
            SUBSTR(ordered_at, 1, 7)   AS year_month,
            COUNT(*)                    AS order_count,
            ROUND(SUM(total_amount), 0) AS total_revenue,
            ROUND(AVG(total_amount), 0) AS avg_order_value
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        order_count,
        total_revenue,
        avg_order_value,
        LAG(total_revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
        ROUND(100.0 * (total_revenue - LAG(total_revenue, 1) OVER (ORDER BY year_month))
            / LAG(total_revenue, 1) OVER (ORDER BY year_month), 1) AS mom_growth_pct
    FROM base;
    ```

    ```sql
    -- Check the improved view
    SELECT *
    FROM v_monthly_revenue
    WHERE year_month LIKE '2024%'
    ORDER BY year_month;
    ```

    **Result example (partial):**

    | year_month | order_count | total_revenue | avg_order_value | prev_month_revenue | mom_growth_pct |
    |---|---|---|---|---|---|
    | 2024-01 | 580 | 98500000 | 169828 | 132000000 | -25.4 |
    | 2024-02 | 520 | 87200000 | 167692 | 98500000 | -11.5 |
    | 2024-03 | 680 | 112000000 | 164706 | 87200000 | 28.4 |

---

### Problem 7

**Simulate the Materialized View concept in SQLite.**

A regular view executes the query every time, but a “materialized view” stores the results in a table.
Save statistics for each product as a table and implement an update pattern.

??? tip "Hint"
    Save the results to a table with `CREATE TABLE mv_product_stats AS SELECT ...`.
    On update, run `DROP TABLE IF EXISTS` + `CREATE TABLE AS` again.
    Since SQLite does not support native MATERIALIZED VIEW, this pattern is an alternative.

??? success "Answer"
    ```sql
    -- 1. Create materialized view (stored as table)
    DROP TABLE IF EXISTS mv_product_stats;

    CREATE TABLE mv_product_stats AS
    SELECT
        p.id              AS product_id,
        p.name            AS product_name,
        cat.name          AS category,
        COALESCE(SUM(oi.quantity), 0) AS total_sold,
        COALESCE(ROUND(SUM(oi.quantity * oi.unit_price), 0), 0) AS total_revenue,
        (SELECT COUNT(*) FROM reviews AS r WHERE r.product_id = p.id) AS review_count,
        (SELECT ROUND(AVG(rating), 2) FROM reviews AS r WHERE r.product_id = p.id) AS avg_rating,
        DATETIME('now') AS refreshed_at
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LEFT JOIN order_items AS oi ON p.id = oi.product_id
    LEFT JOIN orders AS o ON oi.order_id = o.id
        AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    WHERE p.is_active = 1
    GROUP BY p.id, p.name, cat.name;
    ```

    ```sql
    -- 2. Use materialized view (can create indexes -- unlike regular views)
    CREATE INDEX idx_mv_product_stats_revenue ON mv_product_stats(total_revenue);

    SELECT *
    FROM mv_product_stats
    ORDER BY total_revenue DESC
    LIMIT 5;
    ```

    **Result example:**

    | product_id | product_name | category | total_sold | total_revenue | review_count | avg_rating | refreshed_at |
    |---|---|---|---|---|---|---|---|
    | 1 | MacBook Pro 16 M3 | Laptop | 85 | 254125000 | 42 | 4.58 | 2025-12-15 10:30:00 |
    | 12 | LG UltraGear 27GP950 | Monitor | 120 | 96000000 | 35 | 4.25 | 2025-12-15 10:30:00 |
    | ... | ... | ... | ... | ... | ... | ... | ... |

    > Materialized views have excellent query performance because complex aggregates are pre-calculated.
    > However, if the original data changes, it must be updated manually. PostgreSQL has native support for `REFRESH MATERIALIZED VIEW`.

---

## Trigger (8~14)

Practice defining, creating, and using triggers.

---

### Problem 8

**Check the list of triggers that currently exist in the DB.**

Displays the trigger name, associated table, and definition (SQL).

??? tip "Hint"
    Filter from `sqlite_master` to `type = 'trigger'`.
    The `tbl_name` column is the table to which the trigger is attached.

??? success "Answer"
    ```sql
    SELECT
        name       AS trigger_name,
        tbl_name   AS table_name,
        sql        AS definition
    FROM sqlite_master
    WHERE type = 'trigger'
    ORDER BY tbl_name, name;
    ```

    **Result example:**

    | trigger_name | table_name | definition |
    | ---------- | ---------- | ---------- |
    | trg_customers_updated_at | customers | CREATE TRIGGER trg_customers_updated_at
    AFTER UPDATE ON customers
    BEGIN
        UPDATE customers SET updated_at = datetime('now') WHERE id = NEW.id;
    END |
    | trg_orders_updated_at | orders | CREATE TRIGGER trg_orders_updated_at
    AFTER UPDATE OF status ON orders
    BEGIN
        UPDATE orders SET updated_at = datetime('now') WHERE id = NEW.id;
    END |
    | trg_product_price_history | products | CREATE TRIGGER trg_product_price_history
    AFTER UPDATE OF price ON products
    WHEN OLD.price != NEW.price
    BEGIN
        -- Close existing history record
        UPDATE product_prices
        SET ended_at = datetime('now')
        WHERE product_id = NEW.id AND ended_at IS NULL;
    
        -- Insert new history record
        INSERT INTO product_prices (product_id, price, started_at, ended_at, change_reason)
        VALUES (NEW.id, NEW.price, datetime('now'), NULL, 'price_update');
    END |
    | trg_products_updated_at | products | CREATE TRIGGER trg_products_updated_at
    AFTER UPDATE ON products
    BEGIN
        UPDATE products SET updated_at = datetime('now') WHERE id = NEW.id;
    END |
    | trg_reviews_updated_at | reviews | CREATE TRIGGER trg_reviews_updated_at
    AFTER UPDATE OF rating, title, content ON reviews
    BEGIN
        UPDATE reviews SET updated_at = datetime('now') WHERE id = NEW.id;
    END |
    | ... | ... | ... |
    AFTER UPDATE ON customers
    BEGIN
        UPDATE customers SET updated_at = datetime('now') WHERE id = NEW.id;
    END |
    | trg_orders_updated_at | orders | CREATE TRIGGER trg_orders_updated_at
    AFTER UPDATE OF status ON orders
    BEGIN
        UPDATE orders SET updated_at = datetime('now') WHERE id = NEW.id;
    END |
    | trg_product_price_history | products | CREATE TRIGGER trg_product_price_history
    AFTER UPDATE OF price ON products
    WHEN OLD.price != NEW.price
    BEGIN
        -- Close existing history record
        UPDATE product_prices
        SET ended_at = datetime('now')
        WHERE product_id = NEW.id AND ended_at IS NULL;
    
        -- Insert new history record
        INSERT INTO product_prices (product_id, price, started_at, ended_at, change_reason)
        VALUES (NEW.id, NEW.price, datetime('now'), NULL, 'price_update');
    END |
    | trg_products_updated_at | products | CREATE TRIGGER trg_products_updated_at
    AFTER UPDATE ON products
    BEGIN
        UPDATE products SET updated_at = datetime('now') WHERE id = NEW.id;
    END |
    | trg_reviews_updated_at | reviews | CREATE TRIGGER trg_reviews_updated_at
    AFTER UPDATE OF rating, title, content ON reviews
    BEGIN
        UPDATE reviews SET updated_at = datetime('now') WHERE id = NEW.id;
    END |
    | ... | ... | ... |

    > The newly created DB may not have triggers. Subsequent problems create triggers.

---

### Problem 9

**Create order status change audit log tables and triggers.**

Automatically logs changes to `status` in the `orders` table.

??? tip "Hint"
    First, create the audit log table as `CREATE TABLE`,
    to `CREATE TRIGGER ... AFTER UPDATE OF status ON orders WHEN OLD.status != NEW.status`
    Record the status before and after the change. `OLD` is the value before the change, and `NEW` is the value after the change.

??? success "Answer"
    ```sql
    -- 1. Create audit log table
    CREATE TABLE IF NOT EXISTS order_status_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id    INTEGER NOT NULL,
        old_status  TEXT NOT NULL,
        new_status  TEXT NOT NULL,
        changed_at  TEXT NOT NULL DEFAULT (DATETIME('now'))
    );

    -- 2. Create trigger
    CREATE TRIGGER trg_order_status_change
    AFTER UPDATE OF status ON orders
    WHEN OLD.status != NEW.status
    BEGIN
        INSERT INTO order_status_log (order_id, old_status, new_status)
        VALUES (NEW.id, OLD.status, NEW.status);
    END;
    ```

    ```sql
    -- 3. Test: change order status
    UPDATE orders SET status = 'shipped' WHERE id = 1 AND status = 'preparing';

    -- 4. Check log
    SELECT * FROM order_status_log ORDER BY id DESC LIMIT 5;
    ```

    **Result example:**

    | id | order_id | old_status | new_status | changed_at |
    |---|---|---|---|---|
    | 1 | 1 | preparing | shipped | 2025-12-15 10:35:00 |

    There is a `WHEN` clause, so the log is only written when the state actually changes.

---

### Problem 10

**Create automatic inventory deduction triggers.**

When a new row is inserted in `order_items`, `stock_qty` for that product is automatically deducted.

??? tip "Hint"
    Use `CREATE TRIGGER ... AFTER INSERT ON order_items`.
    `UPDATE products SET stock_qty = stock_qty - NEW.quantity WHERE id = NEW.product_id;`

??? success "Answer"
    ```sql
    CREATE TRIGGER trg_stock_deduct
    AFTER INSERT ON order_items
    BEGIN
        UPDATE products
        SET stock_qty = stock_qty - NEW.quantity,
            updated_at = DATETIME('now')
        WHERE id = NEW.product_id;
    END;
    ```

    ```sql
    -- Test: check current stock
    SELECT id, name, stock_qty FROM products WHERE id = 1;

    -- Insert into order_items (in production, this occurs within the order process)
    -- INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_amount, subtotal)
    -- VALUES (1, 1, 2, 2987500, 0, 5975000);

    -- Check if stock decreased by 2
    -- SELECT id, name, stock_qty FROM products WHERE id = 1;
    ```

    **Result example (inventory change):**

    | id | name | stock_qty |
    | ----------: | ---------- | ----------: |
    | 1 | Razer Blade 18 Black | 107 |

    > In actual operations, out-of-stock verification must also be implemented.

---

### Problem 11

**Create automatic point accumulation triggers when you write a review.**

When a new review is inserted into `reviews`, you will earn 500 points for that customer.
Applies only to purchase reviews verified by the `WHEN NEW.is_verified = 1` condition.

??? tip "Hint"
    You need to perform two actions:
    1. Increment `point_balance` in table `customers`
    2. Insert accrual record into `point_transactions` table
    Multiple SQL statements can be executed in the trigger body.

??? success "Answer"
    ```sql
    CREATE TRIGGER trg_review_point
    AFTER INSERT ON reviews
    WHEN NEW.is_verified = 1
    BEGIN
        -- 1. Increase point balance
        UPDATE customers
        SET point_balance = point_balance + 500,
            updated_at = DATETIME('now')
        WHERE id = NEW.customer_id;

        -- 2. Record point history
        INSERT INTO point_transactions (
            customer_id, order_id, type, reason, amount,
            balance_after, expires_at, created_at
        )
        VALUES (
            NEW.customer_id,
            NEW.order_id,
            'earn',
            'review',
            500,
            (SELECT point_balance FROM customers WHERE id = NEW.customer_id),
            DATE('now', '+1 year'),
            DATETIME('now')
        );
    END;
    ```

    ```sql
    -- Check trigger
    SELECT name, sql
    FROM sqlite_master
    WHERE type = 'trigger' AND name = 'trg_review_point';
    ```

    **Result example:**

    | name | sql |
    |---|---|
    | trg_review_point | CREATE TRIGGER trg_review_point AFTER INSERT ON reviews WHEN NEW.is_verified = 1 BEGIN ... END |

---

### Problem 12

**Create a trigger to automatically record product price change history.**

When `price` of `products` is changed, the history is automatically recorded in the `product_prices` table.
Updates `ended_at` in the old price record to the current time and inserts a new price record.

??? tip "Hint"
    Use `AFTER UPDATE OF price ON products WHEN OLD.price != NEW.price`.
    Step 1: Update `ended_at` of an existing record (`WHERE product_id = NEW.id AND ended_at IS NULL`).
    Step 2: Insert a new record.

??? success "Answer"
    ```sql
    CREATE TRIGGER trg_price_history
    AFTER UPDATE OF price ON products
    WHEN OLD.price != NEW.price
    BEGIN
        -- 1. Close previous price record
        UPDATE product_prices
        SET ended_at = DATETIME('now')
        WHERE product_id = NEW.id
          AND ended_at IS NULL;

        -- 2. Create new price record
        INSERT INTO product_prices (product_id, price, started_at, change_reason)
        VALUES (NEW.id, NEW.price, DATETIME('now'), 'price_drop');
    END;
    ```

    ```sql
    -- Test: change price
    -- UPDATE products SET price = 2800000, updated_at = DATETIME('now') WHERE id = 1;

    -- Check history
    SELECT *
    FROM product_prices
    WHERE product_id = 1
    ORDER BY started_at DESC
    LIMIT 3;
    ```

    **Result example:**

    | id | product_id | price | started_at | ended_at | change_reason |
    | ----------: | ----------: | ----------: | ---------- | ---------- | ---------- |
    | 3 | 1 | 2987500.0 | 2024-08-26 01:34:11 | (NULL) | price_drop |
    | 2 | 1 | 3561500.0 | 2017-12-25 04:37:06 | 2024-08-26 01:34:11 | promotion |
    | 1 | 1 | 4409600.0 | 2016-11-20 02:59:21 | 2017-12-25 04:37:06 | regular |

---

### Problem 13

**Create a delete protection trigger.**

Confirmed orders (status = 'confirmed' or 'delivered') cannot be deleted.
When attempting to delete, an error occurs with `RAISE(ABORT, ...)`.

??? tip "Hint"
    Use `BEFORE DELETE ON orders`.
    In condition `WHEN OLD.status IN ('confirmed', 'delivered')`
    Run `RAISE(ABORT, 'Confirmed orders cannot be deleted.')`.

??? success "Answer"
    ```sql
    CREATE TRIGGER trg_prevent_order_delete
    BEFORE DELETE ON orders
    WHEN OLD.status IN ('confirmed', 'delivered')
    BEGIN
        SELECT RAISE(ABORT, 'Confirmed/delivered orders cannot be deleted.');
    END;
    ```

    ```sql
    -- Test: attempt to delete a confirmed order
    -- DELETE FROM orders WHERE id = 100 AND status = 'confirmed';
    -- Result: Error: Confirmed/delivered orders cannot be deleted.

    -- Check trigger
    SELECT name, sql
    FROM sqlite_master
    WHERE type = 'trigger' AND name = 'trg_prevent_order_delete';
    ```

    **Error message:**

    ```
    Error: Confirmed/delivered orders cannot be deleted.
    ```

    > Using `RAISE(ABORT, ...)` in a `BEFORE` trigger will break before the actual DELETE is executed.
    > `RAISE(ROLLBACK, ...)`, `RAISE(FAIL, ...)` can also be used, and the transaction processing method is different.

---

### Problem 14

**Practice trigger deletion and conditional regeneration.**

Delete the existing `trg_stock_deduct` trigger and recreate it with an improved version that raises an error when out of stock.

??? tip "Hint"
    Delete with `DROP TRIGGER IF EXISTS trg_stock_deduct;`.
    The improved trigger uses `BEFORE INSERT`,
    If inventory is low, insertion itself is prevented with `RAISE(ABORT, ...)`.

??? success "Answer"
    ```sql
    -- 1. Delete existing trigger
    DROP TRIGGER IF EXISTS trg_stock_deduct;

    -- 2. Stock validation trigger (BEFORE)
    CREATE TRIGGER trg_stock_check
    BEFORE INSERT ON order_items
    WHEN (SELECT stock_qty FROM products WHERE id = NEW.product_id) < NEW.quantity
    BEGIN
        SELECT RAISE(ABORT, 'Insufficient stock.');
    END;

    -- 3. Stock deduction trigger (AFTER)
    CREATE TRIGGER trg_stock_deduct
    AFTER INSERT ON order_items
    BEGIN
        UPDATE products
        SET stock_qty = stock_qty - NEW.quantity,
            updated_at = DATETIME('now')
        WHERE id = NEW.product_id;

        -- Record inventory change history
        INSERT INTO inventory_transactions (
            product_id, type, quantity, reference_id, notes, created_at
        )
        VALUES (
            NEW.product_id, 'outbound', -NEW.quantity,
            NEW.order_id, 'order_deduction', DATETIME('now')
        );
    END;
    ```

    ```sql
    -- Check triggers
    SELECT name, tbl_name, sql
    FROM sqlite_master
    WHERE type = 'trigger'
      AND name IN ('trg_stock_check', 'trg_stock_deduct')
    ORDER BY name;
    ```

    **Result example:**

    | name | tbl_name | sql |
    |---|---|---|
    | trg_stock_check | order_items | CREATE TRIGGER trg_stock_check BEFORE INSERT ... |
    | trg_stock_deduct | order_items | CREATE TRIGGER trg_stock_deduct AFTER INSERT ... |

    > Separating the BEFORE trigger (validation) and AFTER trigger (execution) makes the logic clearer.

---

## Stored procedures (15~20)

Stored procedures are not supported by SQLite. Provided in MySQL/PostgreSQL syntax.

!!! warning "SQLite not supported"
    Stored procedures are supported in MySQL, PostgreSQL, SQL Server, Oracle, etc.
    The problems below are presented under the MySQL/PostgreSQL tab and focus on understanding the concepts.

---

### Problem 15

**Check out stored procedure-like functionality in SQLite.**

Count the number of all tables, views, triggers, and indexes in the current DB from the system catalog.

??? tip "Hint"
    Returns `COUNT(*)` from `sqlite_master` by `type`.
    You can know the number of each type with `GROUP BY type`.

??? success "Answer"
    ```sql
    SELECT
        type,
        COUNT(*) AS object_count
    FROM sqlite_master
    WHERE type IN ('table', 'view', 'trigger', 'index')
    GROUP BY type
    ORDER BY
        CASE type
            WHEN 'table' THEN 1
            WHEN 'view' THEN 2
            WHEN 'index' THEN 3
            WHEN 'trigger' THEN 4
        END;
    ```

    **Result example:**

    | type | object_count |
    | ---------- | ----------: |
    | table | 31 |
    | view | 18 |
    | index | 72 |
    | trigger | 5 |

---

### Problem 16

**Design a customer rating renewal process.**

Customer levels are recalculated based on annual purchase amount:
VIP (5 million won or more), GOLD (3 to 5 million won), SILVER (1 to 3 million won), BRONZE (less than 1 million won).

??? tip "Hint"
    Use `CREATE PROCEDURE` in MySQL and `CREATE OR REPLACE PROCEDURE` in PostgreSQL.
    Update each customer's rating using a cursor or the UPDATE ... FROM pattern.

??? success "Answer"
    === "MySQL"
        ```sql
        DELIMITER //

        CREATE PROCEDURE sp_update_customer_grades(IN p_year INT)
        BEGIN
            -- 1. Update grades based on annual purchase amount
            UPDATE customers AS c
            INNER JOIN (
                SELECT
                    customer_id,
                    SUM(total_amount) AS annual_spent
                FROM orders
                WHERE YEAR(ordered_at) = p_year
                  AND status NOT IN ('cancelled', 'returned', 'return_requested')
                GROUP BY customer_id
            ) AS s ON c.id = s.customer_id
            SET c.grade = CASE
                WHEN s.annual_spent >= 5000000 THEN 'VIP'
                WHEN s.annual_spent >= 3000000 THEN 'GOLD'
                WHEN s.annual_spent >= 1000000 THEN 'SILVER'
                ELSE 'BRONZE'
            END,
            c.updated_at = NOW();

            -- 2. Record grade change history
            INSERT INTO customer_grade_history (customer_id, old_grade, new_grade, changed_at, reason)
            SELECT
                c.id, cgh.prev_grade, c.grade, NOW(), 'yearly_review'
            FROM customers AS c
            INNER JOIN (
                SELECT customer_id, grade AS prev_grade
                FROM customer_grade_history
                WHERE (customer_id, changed_at) IN (
                    SELECT customer_id, MAX(changed_at)
                    FROM customer_grade_history
                    GROUP BY customer_id
                )
            ) AS cgh ON c.id = cgh.customer_id
            WHERE c.grade != cgh.prev_grade;

            SELECT ROW_COUNT() AS updated_count;
        END //

        DELIMITER ;

        -- Execute
        CALL sp_update_customer_grades(2024);
        ```

    === "PostgreSQL"
        ```sql
        CREATE OR REPLACE PROCEDURE sp_update_customer_grades(p_year INT)
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_updated INT;
        BEGIN
            -- 1. Update grades based on annual purchase amount
            UPDATE customers AS c
            SET grade = CASE
                WHEN s.annual_spent >= 5000000 THEN 'VIP'
                WHEN s.annual_spent >= 3000000 THEN 'GOLD'
                WHEN s.annual_spent >= 1000000 THEN 'SILVER'
                ELSE 'BRONZE'
            END,
            updated_at = NOW()
            FROM (
                SELECT
                    customer_id,
                    SUM(total_amount) AS annual_spent
                FROM orders
                WHERE EXTRACT(YEAR FROM ordered_at) = p_year
                  AND status NOT IN ('cancelled', 'returned', 'return_requested')
                GROUP BY customer_id
            ) AS s
            WHERE c.id = s.customer_id;

            GET DIAGNOSTICS v_updated = ROW_COUNT;
            RAISE NOTICE 'Updated customer count: %', v_updated;
        END;
        $$;

        -- Execute
        CALL sp_update_customer_grades(2024);
        ```

---

### Problem 17

**Design a month-end settlement procedure.**

Calculates a sales summary for a specific month and stores it in a settlement table.

??? tip "Hint"
    It takes the year and month (`p_year_month`) as a parameter.
    Aggregate order/payment data and INSERT settlement records.
    An error occurs for months in which settlement has already been completed.

??? success "Answer"
    === "MySQL"
        ```sql
        DELIMITER //

        CREATE PROCEDURE sp_monthly_settlement(IN p_year_month VARCHAR(7))
        BEGIN
            DECLARE v_exists INT;

            -- Check for duplicate settlement
            SELECT COUNT(*) INTO v_exists
            FROM monthly_settlements
            WHERE year_month = p_year_month;

            IF v_exists > 0 THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Settlement already completed for this month.';
            END IF;

            -- Insert settlement data
            INSERT INTO monthly_settlements (
                year_month, order_count, total_revenue,
                total_discount, net_revenue, settled_at
            )
            SELECT
                p_year_month,
                COUNT(*),
                SUM(total_amount),
                SUM(discount_amount),
                SUM(total_amount) - SUM(discount_amount),
                NOW()
            FROM orders
            WHERE DATE_FORMAT(ordered_at, '%Y-%m') = p_year_month
              AND status NOT IN ('cancelled', 'returned', 'return_requested');

            SELECT * FROM monthly_settlements WHERE year_month = p_year_month;
        END //

        DELIMITER ;

        CALL sp_monthly_settlement('2024-12');
        ```

    === "PostgreSQL"
        ```sql
        CREATE OR REPLACE PROCEDURE sp_monthly_settlement(p_year_month TEXT)
        LANGUAGE plpgsql
        AS $$
        BEGIN
            -- Check for duplicate settlement
            IF EXISTS (SELECT 1 FROM monthly_settlements WHERE year_month = p_year_month) THEN
                RAISE EXCEPTION 'Settlement already completed for this month: %', p_year_month;
            END IF;

            -- Insert settlement data
            INSERT INTO monthly_settlements (
                year_month, order_count, total_revenue,
                total_discount, net_revenue, settled_at
            )
            SELECT
                p_year_month,
                COUNT(*),
                SUM(total_amount),
                SUM(discount_amount),
                SUM(total_amount) - SUM(discount_amount),
                NOW()
            FROM orders
            WHERE TO_CHAR(ordered_at, 'YYYY-MM') = p_year_month
              AND status NOT IN ('cancelled', 'returned', 'return_requested');

            RAISE NOTICE 'Settlement completed: %', p_year_month;
        END;
        $$;

        CALL sp_monthly_settlement('2024-12');
        ```

---

### Problem 18

**Design inventory replenishment procedures.**

Find products that are below the safety stock (threshold) and create an automatic order request.

??? tip "Hint"
    It takes the safety stock standard (e.g. 20 units) as a parameter.
    Search for out-of-stock products and INSERT them into the ordering table.
    Replenishment quantity is calculated as “average monthly sales x 2”.

??? success "Answer"
    === "MySQL"
        ```sql
        DELIMITER //

        CREATE PROCEDURE sp_restock_check(IN p_threshold INT)
        BEGIN
            -- Low-stock products + recommended order quantity
            SELECT
                p.id            AS product_id,
                p.name          AS product_name,
                p.stock_qty     AS current_stock,
                p_threshold     AS safety_stock,
                COALESCE(ROUND(AVG(monthly_sold) * 2), 50) AS recommended_qty,
                s.company_name  AS supplier
            FROM products AS p
            INNER JOIN suppliers AS s ON p.supplier_id = s.id
            LEFT JOIN (
                SELECT
                    oi.product_id,
                    DATE_FORMAT(o.ordered_at, '%Y-%m') AS ym,
                    SUM(oi.quantity) AS monthly_sold
                FROM order_items AS oi
                INNER JOIN orders AS o ON oi.order_id = o.id
                WHERE o.ordered_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                  AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
                GROUP BY oi.product_id, DATE_FORMAT(o.ordered_at, '%Y-%m')
            ) AS ms ON p.id = ms.product_id
            WHERE p.is_active = 1
              AND p.stock_qty <= p_threshold
            GROUP BY p.id, p.name, p.stock_qty, s.company_name
            ORDER BY p.stock_qty ASC;
        END //

        DELIMITER ;

        CALL sp_restock_check(20);
        ```

    === "PostgreSQL"
        ```sql
        CREATE OR REPLACE PROCEDURE sp_restock_check(p_threshold INT)
        LANGUAGE plpgsql
        AS $$
        DECLARE
            rec RECORD;
        BEGIN
            FOR rec IN
                SELECT
                    p.id AS product_id,
                    p.name AS product_name,
                    p.stock_qty AS current_stock,
                    COALESCE(ROUND(AVG(ms.monthly_sold) * 2), 50) AS recommended_qty,
                    s.company_name AS supplier
                FROM products AS p
                INNER JOIN suppliers AS s ON p.supplier_id = s.id
                LEFT JOIN (
                    SELECT
                        oi.product_id,
                        TO_CHAR(o.ordered_at, 'YYYY-MM') AS ym,
                        SUM(oi.quantity) AS monthly_sold
                    FROM order_items AS oi
                    INNER JOIN orders AS o ON oi.order_id = o.id
                    WHERE o.ordered_at >= NOW() - INTERVAL '6 months'
                      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
                    GROUP BY oi.product_id, TO_CHAR(o.ordered_at, 'YYYY-MM')
                ) AS ms ON p.id = ms.product_id
                WHERE p.is_active = 1
                  AND p.stock_qty <= p_threshold
                GROUP BY p.id, p.name, p.stock_qty, s.company_name
                ORDER BY p.stock_qty ASC
            LOOP
                RAISE NOTICE 'Reorder needed: % (stock: %, recommended: %)',
                    rec.product_name, rec.current_stock, rec.recommended_qty;
            END LOOP;
        END;
        $$;

        CALL sp_restock_check(20);
        ```

---

### Problem 19

**Design a customer activity summary function.**

Takes a specific customer ID and returns a comprehensive activity summary (orders/reviews/points/CS) for that customer as JSON.

??? tip "Hint"
    Use `CREATE FUNCTION ... RETURNS JSON` in MySQL and `RETURNS JSONB` in PostgreSQL.
    Each indicator is obtained as a subquery and combined into `JSON_OBJECT`/`jsonb_build_object`.

??? success "Answer"
    === "MySQL"
        ```sql
        DELIMITER //

        CREATE FUNCTION fn_customer_summary(p_customer_id INT)
        RETURNS JSON
        DETERMINISTIC
        READS SQL DATA
        BEGIN
            DECLARE v_result JSON;

            SELECT JSON_OBJECT(
                'customer_id', c.id,
                'name', c.name,
                'grade', c.grade,
                'order_count', COALESCE(os.cnt, 0),
                'total_spent', COALESCE(os.total, 0),
                'review_count', COALESCE(rs.cnt, 0),
                'avg_rating_given', COALESCE(rs.avg_r, 0),
                'point_balance', c.point_balance,
                'complaint_count', COALESCE(cs.cnt, 0)
            ) INTO v_result
            FROM customers AS c
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt, SUM(total_amount) AS total
                FROM orders
                WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
                GROUP BY customer_id
            ) AS os ON c.id = os.customer_id
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt, AVG(rating) AS avg_r
                FROM reviews GROUP BY customer_id
            ) AS rs ON c.id = rs.customer_id
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt
                FROM complaints GROUP BY customer_id
            ) AS cs ON c.id = cs.customer_id
            WHERE c.id = p_customer_id;

            RETURN v_result;
        END //

        DELIMITER ;

        SELECT fn_customer_summary(1);
        ```

    === "PostgreSQL"
        ```sql
        CREATE OR REPLACE FUNCTION fn_customer_summary(p_customer_id INT)
        RETURNS JSONB
        LANGUAGE plpgsql
        STABLE
        AS $$
        DECLARE
            v_result JSONB;
        BEGIN
            SELECT jsonb_build_object(
                'customer_id', c.id,
                'name', c.name,
                'grade', c.grade,
                'order_count', COALESCE(os.cnt, 0),
                'total_spent', COALESCE(os.total, 0),
                'review_count', COALESCE(rs.cnt, 0),
                'avg_rating_given', COALESCE(ROUND(rs.avg_r, 2), 0),
                'point_balance', c.point_balance,
                'complaint_count', COALESCE(cs.cnt, 0)
            ) INTO v_result
            FROM customers AS c
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt, SUM(total_amount) AS total
                FROM orders
                WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
                GROUP BY customer_id
            ) AS os ON c.id = os.customer_id
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt, AVG(rating) AS avg_r
                FROM reviews GROUP BY customer_id
            ) AS rs ON c.id = rs.customer_id
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt
                FROM complaints GROUP BY customer_id
            ) AS cs ON c.id = cs.customer_id
            WHERE c.id = p_customer_id;

            RETURN v_result;
        END;
        $$;

        SELECT fn_customer_summary(1);
        ```

    **Result example (JSON):**

    ```json
    {
        "customer_id": 1,
        "name": "Kim...",
        "grade": "GOLD",
        "order_count": 15,
        "total_spent": 4850000,
        "review_count": 8,
        "avg_rating_given": 4.25,
        "point_balance": 12500,
        "complaint_count": 2
    }
    ```

---

### Problem 20

**Design transaction-based order processing procedures.**

The entire process of order creation (Create order record -> Create order item -> Deduct inventory -> Create payment -> Earn points)
Encapsulate it in one procedure. If there is an intermediate failure, there is a full rollback.

??? tip "Hint"
    Use `START TRANSACTION ... COMMIT` in MySQL and `BEGIN ... COMMIT` in PostgreSQL.
    If an error occurs, cancel entirely with `ROLLBACK`.
    Utilizes MySQL's `DECLARE ... HANDLER FOR SQLEXCEPTION` and PostgreSQL's `EXCEPTION WHEN` blocks.

??? success "Answer"
    === "MySQL"
        ```sql
        DELIMITER //

        CREATE PROCEDURE sp_create_order(
            IN p_customer_id INT,
            IN p_product_id INT,
            IN p_quantity INT,
            IN p_payment_method VARCHAR(20)
        )
        BEGIN
            DECLARE v_price REAL;
            DECLARE v_stock INT;
            DECLARE v_order_id INT;
            DECLARE v_total REAL;
            DECLARE v_order_number VARCHAR(20);

            DECLARE EXIT HANDLER FOR SQLEXCEPTION
            BEGIN
                ROLLBACK;
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'An error occurred during order processing.';
            END;

            START TRANSACTION;

            -- 1. Get product info & check stock
            SELECT price, stock_qty INTO v_price, v_stock
            FROM products WHERE id = p_product_id FOR UPDATE;

            IF v_stock < p_quantity THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Insufficient stock.';
            END IF;

            -- 2. Create order
            SET v_total = v_price * p_quantity;
            SET v_order_number = CONCAT('ORD-',
                DATE_FORMAT(NOW(), '%Y%m%d'), '-',
                LPAD(FLOOR(RAND() * 99999), 5, '0'));

            INSERT INTO orders (
                order_number, customer_id, address_id, status,
                total_amount, discount_amount, shipping_fee,
                ordered_at, created_at, updated_at
            ) VALUES (
                v_order_number, p_customer_id,
                (SELECT id FROM customer_addresses
                 WHERE customer_id = p_customer_id AND is_default = 1 LIMIT 1),
                'paid', v_total, 0,
                CASE WHEN v_total >= 50000 THEN 0 ELSE 3000 END,
                NOW(), NOW(), NOW()
            );

            SET v_order_id = LAST_INSERT_ID();

            -- 3. Create order item
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
            VALUES (v_order_id, p_product_id, p_quantity, v_price, v_total);

            -- 4. Deduct stock
            UPDATE products
            SET stock_qty = stock_qty - p_quantity, updated_at = NOW()
            WHERE id = p_product_id;

            -- 5. Create payment
            INSERT INTO payments (order_id, method, amount, status, paid_at, created_at)
            VALUES (v_order_id, p_payment_method, v_total, 'completed', NOW(), NOW());

            COMMIT;

            SELECT v_order_id AS order_id, v_order_number AS order_number,
                   v_total AS total_amount, 'Order completed' AS message;
        END //

        DELIMITER ;

        CALL sp_create_order(1, 10, 2, 'card');
        ```

    === "PostgreSQL"
        ```sql
        CREATE OR REPLACE PROCEDURE sp_create_order(
            p_customer_id INT,
            p_product_id INT,
            p_quantity INT,
            p_payment_method TEXT
        )
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_price NUMERIC;
            v_stock INT;
            v_order_id INT;
            v_total NUMERIC;
            v_order_number TEXT;
        BEGIN
            -- 1. Get product info & check stock (row lock)
            SELECT price, stock_qty INTO v_price, v_stock
            FROM products WHERE id = p_product_id FOR UPDATE;

            IF v_stock < p_quantity THEN
                RAISE EXCEPTION 'Insufficient stock. (current: %, requested: %)', v_stock, p_quantity;
            END IF;

            -- 2. Create order
            v_total := v_price * p_quantity;
            v_order_number := 'ORD-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-'
                || LPAD(FLOOR(RANDOM() * 99999)::TEXT, 5, '0');

            INSERT INTO orders (
                order_number, customer_id, address_id, status,
                total_amount, discount_amount, shipping_fee,
                ordered_at, created_at, updated_at
            ) VALUES (
                v_order_number, p_customer_id,
                (SELECT id FROM customer_addresses
                 WHERE customer_id = p_customer_id AND is_default = TRUE LIMIT 1),
                'paid', v_total, 0,
                CASE WHEN v_total >= 50000 THEN 0 ELSE 3000 END,
                NOW(), NOW(), NOW()
            )
            RETURNING id INTO v_order_id;

            -- 3. Create order item
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
            VALUES (v_order_id, p_product_id, p_quantity, v_price, v_total);

            -- 4. Deduct stock
            UPDATE products
            SET stock_qty = stock_qty - p_quantity, updated_at = NOW()
            WHERE id = p_product_id;

            -- 5. Create payment
            INSERT INTO payments (order_id, method, amount, status, paid_at, created_at)
            VALUES (v_order_id, p_payment_method, v_total, 'completed', NOW(), NOW());

            RAISE NOTICE 'Order completed: % (amount: %)', v_order_number, v_total;
        END;
        $$;

        CALL sp_create_order(1, 10, 2, 'card');
        ```

    **Example of execution result:**

    | order_id | order_number | total_amount | message |
    |---|---|---|---|
    | 9001 | ORD-20251215-38291 | 1590000 | Order completed |

    > This procedure combines the five steps into one transaction, and if any intermediate step fails, the entire process is rolled back.
    > Lock product rows with `FOR UPDATE` to prevent inventory contention (Race Condition) when ordering simultaneously.
