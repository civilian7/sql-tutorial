# Advanced Analytics

#### :material-database: Tables


`point_transactions` — Points (earn, use, expire)<br>

`customer_grade_history` — Grade history (before/after)<br>

`product_views` — View log (customer, product, date)<br>

`orders` — Orders (status, amount, date)<br>

`order_items` — Order items (qty, unit price)<br>

`carts` — Carts (status)<br>

`cart_items` — Cart items (quantity)<br>

`promotions` — Promotions (period, discount)<br>

`promotion_products` — Promotion products<br>

`staff` — Staff (dept, role, manager)<br>

`product_qna` — Product Q&A (question-answer)<br>

`products` — Products (name, price, stock, brand)<br>

`customers` — Customers (grade, points, channel)<br>



**:material-book-open-variant: Concepts:** `Window Functions`, `CTE`, `Funnel`, `Session`, `Cohort`, `Recursive CTE`, `RFM`


---


### 1. Point Running Total Verification


Verify point_transactions.balance_after using SUM() OVER().
For a specific customer (e.g., id=100), list point transactions chronologically
and compare calculated running total with balance_after.


**Hint 1:** - Use `SUM(amount) OVER (PARTITION BY customer_id ORDER BY created_at, id)`
- `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`
- Compare with `balance_after` to find discrepancies



??? success "Answer"
    ```sql
    SELECT
        id,
        type,
        reason,
        amount,
        balance_after,
        SUM(amount) OVER (
            ORDER BY created_at, id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS calculated_balance,
        balance_after - SUM(amount) OVER (
            ORDER BY created_at, id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS diff,
        created_at
    FROM point_transactions
    WHERE customer_id = 100
    ORDER BY created_at, id;
    ```


---


### 2. Grade Change History Tracking (LAG)


Use LAG() on customer_grade_history to fetch the previous grade before each change.
Also verify if old_grade matches the LAG result.


**Hint 1:** - `LAG(new_grade) OVER (PARTITION BY customer_id ORDER BY changed_at)`
- Previous record's new_grade should match current record's old_grade



??? success "Answer"
    ```sql
    WITH grade_changes AS (
        SELECT
            customer_id,
            old_grade,
            new_grade,
            reason,
            changed_at,
            LAG(new_grade) OVER (
                PARTITION BY customer_id
                ORDER BY changed_at
            ) AS prev_new_grade
        FROM customer_grade_history
    )
    SELECT
        gc.customer_id,
        c.name,
        gc.old_grade,
        gc.new_grade,
        gc.prev_new_grade,
        CASE
            WHEN gc.old_grade = gc.prev_new_grade THEN 'OK'
            WHEN gc.prev_new_grade IS NULL THEN 'FIRST'
            ELSE 'MISMATCH'
        END AS check_status,
        gc.reason,
        gc.changed_at
    FROM grade_changes AS gc
    INNER JOIN customers AS c ON gc.customer_id = c.id
    WHERE gc.prev_new_grade IS NOT NULL
    ORDER BY gc.customer_id, gc.changed_at
    LIMIT 30;
    ```


---


### 3. Funnel Analysis: View -> Cart -> Purchase


Using product_views, cart_items, and order_items,
calculate conversion rates for the funnel: view -> add to cart -> purchase.


**Hint 1:** - Count unique customer-product pairs at each stage
- The funnel requires the same customer viewing the same product
- Use scalar subqueries or CTEs



??? success "Answer"
    ```sql
    WITH funnel AS (
        SELECT
            (SELECT COUNT(DISTINCT customer_id || '-' || product_id)
             FROM product_views) AS step1_views,
            (SELECT COUNT(DISTINCT c.customer_id || '-' || ci.product_id)
             FROM cart_items ci
             INNER JOIN carts c ON ci.cart_id = c.id) AS step2_cart,
            (SELECT COUNT(DISTINCT o.customer_id || '-' || oi.product_id)
             FROM order_items oi
             INNER JOIN orders o ON oi.order_id = o.id
             WHERE o.status NOT IN ('cancelled')) AS step3_purchase
    )
    SELECT
        step1_views,
        step2_cart,
        ROUND(100.0 * step2_cart / step1_views, 2) AS view_to_cart_pct,
        step3_purchase,
        ROUND(100.0 * step3_purchase / step2_cart, 2) AS cart_to_purchase_pct,
        ROUND(100.0 * step3_purchase / step1_views, 2) AS view_to_purchase_pct
    FROM funnel;
    ```


---


### 4. Session Analysis: Product View Sessions


Group product_views into sessions.
A gap of 30+ minutes between views by the same customer starts a new session.
Calculate average sessions per customer and average views per session.


**Hint 1:** - `LAG(viewed_at) OVER (PARTITION BY customer_id ORDER BY viewed_at)`
- If time gap > 30 minutes, mark as new session
- `SUM(new_session_flag) OVER (...)` to assign session numbers



??? success "Answer"

    === "SQLite"
        ```sql
        WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
            LAG(viewed_at) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS prev_viewed_at,
            CASE
                WHEN LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) IS NULL THEN 1
                WHEN (JULIANDAY(viewed_at) - JULIANDAY(LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ))) * 24 * 60 > 30 THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
        WHERE customer_id <= 1000
    ),
    with_session AS (
        SELECT
            customer_id,
            viewed_at,
            SUM(is_new_session) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS session_id
        FROM view_gaps
    ),
    session_stats AS (
        SELECT
            customer_id,
            session_id,
            COUNT(*) AS views_in_session
        FROM with_session
        GROUP BY customer_id, session_id
    )
    SELECT
        COUNT(DISTINCT customer_id) AS total_customers,
        COUNT(*) AS total_sessions,
        ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 1) AS avg_sessions_per_customer,
        ROUND(AVG(views_in_session), 1) AS avg_views_per_session
    FROM session_stats;
        ```

    === "MySQL"
        ```sql
        WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
            LAG(viewed_at) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS prev_viewed_at,
            CASE
                WHEN LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) IS NULL THEN 1
                WHEN TIMESTAMPDIFF(MINUTE, LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ), viewed_at) > 30 THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
        WHERE customer_id <= 1000
    ),
    with_session AS (
        SELECT
            customer_id,
            viewed_at,
            SUM(is_new_session) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS session_id
        FROM view_gaps
    ),
    session_stats AS (
        SELECT
            customer_id,
            session_id,
            COUNT(*) AS views_in_session
        FROM with_session
        GROUP BY customer_id, session_id
    )
    SELECT
        COUNT(DISTINCT customer_id) AS total_customers,
        COUNT(*) AS total_sessions,
        ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 1) AS avg_sessions_per_customer,
        ROUND(AVG(views_in_session), 1) AS avg_views_per_session
    FROM session_stats;
        ```

    === "PostgreSQL"
        ```sql
        WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
            LAG(viewed_at) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS prev_viewed_at,
            CASE
                WHEN LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) IS NULL THEN 1
                WHEN EXTRACT(EPOCH FROM (viewed_at::timestamp - LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                )::timestamp)) / 60 > 30 THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
        WHERE customer_id <= 1000
    ),
    with_session AS (
        SELECT
            customer_id,
            viewed_at,
            SUM(is_new_session) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS session_id
        FROM view_gaps
    ),
    session_stats AS (
        SELECT
            customer_id,
            session_id,
            COUNT(*) AS views_in_session
        FROM with_session
        GROUP BY customer_id, session_id
    )
    SELECT
        COUNT(DISTINCT customer_id) AS total_customers,
        COUNT(*) AS total_sessions,
        ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 1) AS avg_sessions_per_customer,
        ROUND(AVG(views_in_session), 1) AS avg_views_per_session
    FROM session_stats;
        ```

    === "Oracle"
        ```sql
        WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
            LAG(viewed_at) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS prev_viewed_at,
            CASE
                WHEN LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) IS NULL THEN 1
                WHEN (CAST(viewed_at AS DATE) - CAST(LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) AS DATE)) * 24 * 60 > 30 THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
        WHERE customer_id <= 1000
    ),
    with_session AS (
        SELECT
            customer_id,
            viewed_at,
            SUM(is_new_session) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS session_id
        FROM view_gaps
    ),
    session_stats AS (
        SELECT
            customer_id,
            session_id,
            COUNT(*) AS views_in_session
        FROM with_session
        GROUP BY customer_id, session_id
    )
    SELECT
        COUNT(DISTINCT customer_id) AS total_customers,
        COUNT(*) AS total_sessions,
        ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 1) AS avg_sessions_per_customer,
        ROUND(AVG(views_in_session), 1) AS avg_views_per_session
    FROM session_stats;
        ```

    === "SQL Server"
        ```sql
        WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
            LAG(viewed_at) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS prev_viewed_at,
            CASE
                WHEN LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) IS NULL THEN 1
                WHEN DATEDIFF(MINUTE, LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ), viewed_at) > 30 THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
        WHERE customer_id <= 1000
    ),
    with_session AS (
        SELECT
            customer_id,
            viewed_at,
            SUM(is_new_session) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS session_id
        FROM view_gaps
    ),
    session_stats AS (
        SELECT
            customer_id,
            session_id,
            COUNT(*) AS views_in_session
        FROM with_session
        GROUP BY customer_id, session_id
    )
    SELECT
        COUNT(DISTINCT customer_id) AS total_customers,
        COUNT(*) AS total_sessions,
        ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 1) AS avg_sessions_per_customer,
        ROUND(AVG(views_in_session), 1) AS avg_views_per_session
    FROM session_stats;
        ```


---


### 5. Cohort Retention: Acquisition Channel x Signup Month


Calculate 30/60/90 day retention rates
by acquisition channel and signup month.


**Hint 1:** - Cohort = acquisition channel + signup month
- 30-day retention: percentage of customers who ordered within 30 days of signup
- Use `DATE(created_at, '+30 days')`



??? success "Answer"

    === "SQLite"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            COALESCE(acquisition_channel, 'unknown') AS channel,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at LIKE '2024%'
    ),
    cohort_activity AS (
        SELECT
            co.channel,
            co.signup_month,
            COUNT(DISTINCT co.customer_id) AS cohort_size,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at <= DATE(co.created_at, '+30 days')
                THEN co.customer_id
            END) AS active_30d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATE(co.created_at, '+30 days')
                 AND o.ordered_at <= DATE(co.created_at, '+60 days')
                THEN co.customer_id
            END) AS active_60d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATE(co.created_at, '+60 days')
                 AND o.ordered_at <= DATE(co.created_at, '+90 days')
                THEN co.customer_id
            END) AS active_90d
        FROM cohort AS co
        LEFT JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY co.channel, co.signup_month
    )
    SELECT
        channel,
        signup_month,
        cohort_size,
        active_30d,
        ROUND(100.0 * active_30d / cohort_size, 1) AS retention_30d_pct,
        active_60d,
        ROUND(100.0 * active_60d / cohort_size, 1) AS retention_60d_pct,
        active_90d,
        ROUND(100.0 * active_90d / cohort_size, 1) AS retention_90d_pct
    FROM cohort_activity
    WHERE cohort_size >= 10
    ORDER BY channel, signup_month;
        ```

    === "MySQL"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            COALESCE(acquisition_channel, 'unknown') AS channel,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at LIKE '2024%'
    ),
    cohort_activity AS (
        SELECT
            co.channel,
            co.signup_month,
            COUNT(DISTINCT co.customer_id) AS cohort_size,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at <= DATE_ADD(co.created_at, INTERVAL 30 DAY)
                THEN co.customer_id
            END) AS active_30d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATE_ADD(co.created_at, INTERVAL 30 DAY)
                 AND o.ordered_at <= DATE_ADD(co.created_at, INTERVAL 60 DAY)
                THEN co.customer_id
            END) AS active_60d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATE_ADD(co.created_at, INTERVAL 60 DAY)
                 AND o.ordered_at <= DATE_ADD(co.created_at, INTERVAL 90 DAY)
                THEN co.customer_id
            END) AS active_90d
        FROM cohort AS co
        LEFT JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY co.channel, co.signup_month
    )
    SELECT
        channel,
        signup_month,
        cohort_size,
        active_30d,
        ROUND(100.0 * active_30d / cohort_size, 1) AS retention_30d_pct,
        active_60d,
        ROUND(100.0 * active_60d / cohort_size, 1) AS retention_60d_pct,
        active_90d,
        ROUND(100.0 * active_90d / cohort_size, 1) AS retention_90d_pct
    FROM cohort_activity
    WHERE cohort_size >= 10
    ORDER BY channel, signup_month;
        ```

    === "PostgreSQL"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            COALESCE(acquisition_channel, 'unknown') AS channel,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at LIKE '2024%'
    ),
    cohort_activity AS (
        SELECT
            co.channel,
            co.signup_month,
            COUNT(DISTINCT co.customer_id) AS cohort_size,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at <= (co.created_at::date + INTERVAL '30 days')
                THEN co.customer_id
            END) AS active_30d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > (co.created_at::date + INTERVAL '30 days')
                 AND o.ordered_at <= (co.created_at::date + INTERVAL '60 days')
                THEN co.customer_id
            END) AS active_60d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > (co.created_at::date + INTERVAL '60 days')
                 AND o.ordered_at <= (co.created_at::date + INTERVAL '90 days')
                THEN co.customer_id
            END) AS active_90d
        FROM cohort AS co
        LEFT JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY co.channel, co.signup_month
    )
    SELECT
        channel,
        signup_month,
        cohort_size,
        active_30d,
        ROUND(100.0 * active_30d / cohort_size, 1) AS retention_30d_pct,
        active_60d,
        ROUND(100.0 * active_60d / cohort_size, 1) AS retention_60d_pct,
        active_90d,
        ROUND(100.0 * active_90d / cohort_size, 1) AS retention_90d_pct
    FROM cohort_activity
    WHERE cohort_size >= 10
    ORDER BY channel, signup_month;
        ```

    === "Oracle"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            COALESCE(acquisition_channel, 'unknown') AS channel,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at LIKE '2024%'
    ),
    cohort_activity AS (
        SELECT
            co.channel,
            co.signup_month,
            COUNT(DISTINCT co.customer_id) AS cohort_size,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at <= CAST(co.created_at AS DATE) + 30
                THEN co.customer_id
            END) AS active_30d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > CAST(co.created_at AS DATE) + 30
                 AND o.ordered_at <= CAST(co.created_at AS DATE) + 60
                THEN co.customer_id
            END) AS active_60d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > CAST(co.created_at AS DATE) + 60
                 AND o.ordered_at <= CAST(co.created_at AS DATE) + 90
                THEN co.customer_id
            END) AS active_90d
        FROM cohort co
        LEFT JOIN orders o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY co.channel, co.signup_month
    )
    SELECT
        channel,
        signup_month,
        cohort_size,
        active_30d,
        ROUND(100.0 * active_30d / cohort_size, 1) AS retention_30d_pct,
        active_60d,
        ROUND(100.0 * active_60d / cohort_size, 1) AS retention_60d_pct,
        active_90d,
        ROUND(100.0 * active_90d / cohort_size, 1) AS retention_90d_pct
    FROM cohort_activity
    WHERE cohort_size >= 10
    ORDER BY channel, signup_month;
        ```

    === "SQL Server"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            COALESCE(acquisition_channel, 'unknown') AS channel,
            SUBSTRING(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at LIKE '2024%'
    ),
    cohort_activity AS (
        SELECT
            co.channel,
            co.signup_month,
            COUNT(DISTINCT co.customer_id) AS cohort_size,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at <= DATEADD(DAY, 30, CAST(co.created_at AS DATE))
                THEN co.customer_id
            END) AS active_30d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATEADD(DAY, 30, CAST(co.created_at AS DATE))
                 AND o.ordered_at <= DATEADD(DAY, 60, CAST(co.created_at AS DATE))
                THEN co.customer_id
            END) AS active_60d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATEADD(DAY, 60, CAST(co.created_at AS DATE))
                 AND o.ordered_at <= DATEADD(DAY, 90, CAST(co.created_at AS DATE))
                THEN co.customer_id
            END) AS active_90d
        FROM cohort AS co
        LEFT JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY co.channel, co.signup_month
    )
    SELECT
        channel,
        signup_month,
        cohort_size,
        active_30d,
        ROUND(100.0 * active_30d / cohort_size, 1) AS retention_30d_pct,
        active_60d,
        ROUND(100.0 * active_60d / cohort_size, 1) AS retention_60d_pct,
        active_90d,
        ROUND(100.0 * active_90d / cohort_size, 1) AS retention_90d_pct
    FROM cohort_activity
    WHERE cohort_size >= 10
    ORDER BY channel, signup_month;
        ```


---


### 6. Promotion Effectiveness Analysis


Compare order amounts for promotion products during vs outside promotion periods.
Calculate revenue change rate per promotion.


**Hint 1:** - Get target products from `promotion_products`
- Promotion period: `promotions.started_at` to `ended_at`
- Separate during/outside revenue with CASE



??? success "Answer"

    === "SQLite"
        ```sql
        WITH promo_products AS (
        SELECT
            promo.id AS promo_id,
            promo.name AS promo_name,
            promo.started_at,
            promo.ended_at,
            pp.product_id
        FROM promotions AS promo
        INNER JOIN promotion_products AS pp ON promo.id = pp.promotion_id
        WHERE promo.started_at >= '2024-01-01'
    ),
    promo_revenue AS (
        SELECT
            ppr.promo_id,
            ppr.promo_name,
            ppr.started_at,
            ppr.ended_at,
            SUM(CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS during_revenue,
            SUM(CASE
                WHEN o.ordered_at < ppr.started_at
                 AND o.ordered_at >= DATE(ppr.started_at, '-' || CAST(JULIANDAY(ppr.ended_at) - JULIANDAY(ppr.started_at) AS INTEGER) || ' days')
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS before_revenue,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN o.id
            END) AS during_orders
        FROM promo_products AS ppr
        INNER JOIN order_items AS oi ON ppr.product_id = oi.product_id
        INNER JOIN orders      AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY ppr.promo_id, ppr.promo_name, ppr.started_at, ppr.ended_at
    )
    SELECT
        promo_name,
        started_at,
        ended_at,
        during_orders,
        ROUND(during_revenue, 0) AS during_revenue,
        ROUND(before_revenue, 0) AS before_revenue,
        CASE
            WHEN before_revenue > 0
            THEN ROUND(100.0 * (during_revenue - before_revenue) / before_revenue, 1)
            ELSE NULL
        END AS revenue_change_pct
    FROM promo_revenue
    WHERE during_revenue > 0
    ORDER BY revenue_change_pct DESC
    LIMIT 20;
        ```

    === "MySQL"
        ```sql
        WITH promo_products AS (
        SELECT
            promo.id AS promo_id,
            promo.name AS promo_name,
            promo.started_at,
            promo.ended_at,
            pp.product_id
        FROM promotions AS promo
        INNER JOIN promotion_products AS pp ON promo.id = pp.promotion_id
        WHERE promo.started_at >= '2024-01-01'
    ),
    promo_revenue AS (
        SELECT
            ppr.promo_id,
            ppr.promo_name,
            ppr.started_at,
            ppr.ended_at,
            SUM(CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS during_revenue,
            SUM(CASE
                WHEN o.ordered_at < ppr.started_at
                 AND o.ordered_at >= DATE_SUB(ppr.started_at, INTERVAL DATEDIFF(ppr.ended_at, ppr.started_at) DAY)
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS before_revenue,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN o.id
            END) AS during_orders
        FROM promo_products AS ppr
        INNER JOIN order_items AS oi ON ppr.product_id = oi.product_id
        INNER JOIN orders      AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY ppr.promo_id, ppr.promo_name, ppr.started_at, ppr.ended_at
    )
    SELECT
        promo_name,
        started_at,
        ended_at,
        during_orders,
        ROUND(during_revenue, 0) AS during_revenue,
        ROUND(before_revenue, 0) AS before_revenue,
        CASE
            WHEN before_revenue > 0
            THEN ROUND(100.0 * (during_revenue - before_revenue) / before_revenue, 1)
            ELSE NULL
        END AS revenue_change_pct
    FROM promo_revenue
    WHERE during_revenue > 0
    ORDER BY revenue_change_pct DESC
    LIMIT 20;
        ```

    === "PostgreSQL"
        ```sql
        WITH promo_products AS (
        SELECT
            promo.id AS promo_id,
            promo.name AS promo_name,
            promo.started_at,
            promo.ended_at,
            pp.product_id
        FROM promotions AS promo
        INNER JOIN promotion_products AS pp ON promo.id = pp.promotion_id
        WHERE promo.started_at >= '2024-01-01'
    ),
    promo_revenue AS (
        SELECT
            ppr.promo_id,
            ppr.promo_name,
            ppr.started_at,
            ppr.ended_at,
            SUM(CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS during_revenue,
            SUM(CASE
                WHEN o.ordered_at < ppr.started_at
                 AND o.ordered_at >= (ppr.started_at::date - (ppr.ended_at::date - ppr.started_at::date))
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS before_revenue,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN o.id
            END) AS during_orders
        FROM promo_products AS ppr
        INNER JOIN order_items AS oi ON ppr.product_id = oi.product_id
        INNER JOIN orders      AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY ppr.promo_id, ppr.promo_name, ppr.started_at, ppr.ended_at
    )
    SELECT
        promo_name,
        started_at,
        ended_at,
        during_orders,
        ROUND(during_revenue, 0) AS during_revenue,
        ROUND(before_revenue, 0) AS before_revenue,
        CASE
            WHEN before_revenue > 0
            THEN ROUND(100.0 * (during_revenue - before_revenue) / before_revenue, 1)
            ELSE NULL
        END AS revenue_change_pct
    FROM promo_revenue
    WHERE during_revenue > 0
    ORDER BY revenue_change_pct DESC
    LIMIT 20;
        ```

    === "Oracle"
        ```sql
        WITH promo_products AS (
        SELECT
            promo.id AS promo_id,
            promo.name AS promo_name,
            promo.started_at,
            promo.ended_at,
            pp.product_id
        FROM promotions promo
        INNER JOIN promotion_products pp ON promo.id = pp.promotion_id
        WHERE promo.started_at >= '2024-01-01'
    ),
    promo_revenue AS (
        SELECT
            ppr.promo_id,
            ppr.promo_name,
            ppr.started_at,
            ppr.ended_at,
            SUM(CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS during_revenue,
            SUM(CASE
                WHEN o.ordered_at < ppr.started_at
                 AND o.ordered_at >= (CAST(ppr.started_at AS DATE) - (CAST(ppr.ended_at AS DATE) - CAST(ppr.started_at AS DATE)))
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS before_revenue,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN o.id
            END) AS during_orders
        FROM promo_products ppr
        INNER JOIN order_items oi ON ppr.product_id = oi.product_id
        INNER JOIN orders      o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY ppr.promo_id, ppr.promo_name, ppr.started_at, ppr.ended_at
    )
    SELECT
        promo_name,
        started_at,
        ended_at,
        during_orders,
        ROUND(during_revenue, 0) AS during_revenue,
        ROUND(before_revenue, 0) AS before_revenue,
        CASE
            WHEN before_revenue > 0
            THEN ROUND(100.0 * (during_revenue - before_revenue) / before_revenue, 1)
            ELSE NULL
        END AS revenue_change_pct
    FROM promo_revenue
    WHERE during_revenue > 0
    ORDER BY revenue_change_pct DESC
    FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        WITH promo_products AS (
        SELECT
            promo.id AS promo_id,
            promo.name AS promo_name,
            promo.started_at,
            promo.ended_at,
            pp.product_id
        FROM promotions AS promo
        INNER JOIN promotion_products AS pp ON promo.id = pp.promotion_id
        WHERE promo.started_at >= '2024-01-01'
    ),
    promo_revenue AS (
        SELECT
            ppr.promo_id,
            ppr.promo_name,
            ppr.started_at,
            ppr.ended_at,
            SUM(CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS during_revenue,
            SUM(CASE
                WHEN o.ordered_at < ppr.started_at
                 AND o.ordered_at >= DATEADD(DAY, -DATEDIFF(DAY, ppr.started_at, ppr.ended_at), ppr.started_at)
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS before_revenue,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN o.id
            END) AS during_orders
        FROM promo_products AS ppr
        INNER JOIN order_items AS oi ON ppr.product_id = oi.product_id
        INNER JOIN orders      AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY ppr.promo_id, ppr.promo_name, ppr.started_at, ppr.ended_at
    )
    SELECT TOP 20
        promo_name,
        started_at,
        ended_at,
        during_orders,
        ROUND(during_revenue, 0) AS during_revenue,
        ROUND(before_revenue, 0) AS before_revenue,
        CASE
            WHEN before_revenue > 0
            THEN ROUND(100.0 * (during_revenue - before_revenue) / before_revenue, 1)
            ELSE NULL
        END AS revenue_change_pct
    FROM promo_revenue
    WHERE during_revenue > 0
    ORDER BY revenue_change_pct DESC;
        ```


---


### 7. Recursive Org Chart: Staff Hierarchy with Levels


Use a recursive CTE to build the full staff org chart.
Show each staff member's hierarchy level and full path (CEO > Director > Manager > ...).


**Hint 1:** - Start: `manager_id IS NULL` (top-level)
- Recurse: `staff.manager_id = tree.id`
- Path: `tree.path || ' > ' || staff.name`



??? success "Answer"
    ```sql
    WITH RECURSIVE org AS (
        SELECT
            id,
            name,
            department,
            role,
            manager_id,
            name AS path,
            0 AS level
        FROM staff
        WHERE manager_id IS NULL
        UNION ALL
        SELECT
            s.id,
            s.name,
            s.department,
            s.role,
            s.manager_id,
            org.path || ' > ' || s.name,
            org.level + 1
        FROM staff AS s
        INNER JOIN org ON s.manager_id = org.id
    )
    SELECT
        level,
        name,
        department,
        role,
        path
    FROM org
    ORDER BY path;
    ```


---


### 8. Recursive Q&A Tree: Question -> Answer -> Follow-up


Use a recursive CTE to build the full Q&A conversation chain.
Display in order: question -> answer -> follow-up question -> follow-up answer.


**Hint 1:** - Start: `parent_id IS NULL` (root questions)
- Recurse: `product_qna.parent_id = tree.id`
- Use indentation or levels to show hierarchy



??? success "Answer"
    ```sql
    WITH RECURSIVE qna_tree AS (
        SELECT
            q.id,
            q.product_id,
            q.parent_id,
            q.content,
            q.customer_id,
            q.staff_id,
            q.created_at,
            0 AS depth,
            CAST(q.id AS TEXT) AS thread_path
        FROM product_qna AS q
        WHERE q.parent_id IS NULL
          AND q.product_id <= 100
        UNION ALL
        SELECT
            child.id,
            child.product_id,
            child.parent_id,
            child.content,
            child.customer_id,
            child.staff_id,
            child.created_at,
            tree.depth + 1,
            tree.thread_path || '.' || CAST(child.id AS TEXT)
        FROM product_qna AS child
        INNER JOIN qna_tree AS tree ON child.parent_id = tree.id
    )
    SELECT
        qt.product_id,
        p.name AS product_name,
        qt.depth,
        CASE
            WHEN qt.customer_id IS NOT NULL THEN '[Q] ' || COALESCE(c.name, '?')
            WHEN qt.staff_id IS NOT NULL    THEN '[A] ' || COALESCE(s.name, '?')
            ELSE '[?]'
        END AS author,
        SUBSTR(qt.content, 1, 80) AS content_preview,
        qt.created_at
    FROM qna_tree AS qt
    INNER JOIN products AS p ON qt.product_id = p.id
    LEFT JOIN customers AS c ON qt.customer_id = c.id
    LEFT JOIN staff     AS s ON qt.staff_id = s.id
    ORDER BY qt.product_id, qt.thread_path
    LIMIT 50;
    ```


---


### 9. Product Successor Chain (Recursive CTE)


Use a recursive CTE to trace the full product successor chain.
e.g., A -> B -> C (A discontinued, replaced by B, B discontinued, replaced by C)


**Hint 1:** - Start: `discontinued_at IS NOT NULL AND successor_id IS NOT NULL`
- Recurse: `products.id = tree.successor_id`
- Also calculate chain length (depth)



??? success "Answer"
    ```sql
    WITH RECURSIVE successor_chain AS (
        SELECT
            id AS origin_id,
            name AS origin_name,
            id AS current_id,
            name AS current_name,
            price AS current_price,
            successor_id,
            discontinued_at,
            0 AS depth
        FROM products
        WHERE discontinued_at IS NOT NULL
          AND successor_id IS NOT NULL
        UNION ALL
        SELECT
            sc.origin_id,
            sc.origin_name,
            p.id,
            p.name,
            p.price,
            p.successor_id,
            p.discontinued_at,
            sc.depth + 1
        FROM products AS p
        INNER JOIN successor_chain AS sc ON p.id = sc.successor_id
        WHERE sc.depth < 10
    )
    SELECT
        origin_name AS discontinued_product,
        current_name AS final_successor,
        depth AS chain_length,
        current_price AS successor_price,
        CASE
            WHEN successor_id IS NULL THEN 'Current Model'
            WHEN discontinued_at IS NOT NULL THEN 'Also Discontinued'
            ELSE 'Active'
        END AS status
    FROM successor_chain
    WHERE successor_id IS NULL
       OR discontinued_at IS NULL
    ORDER BY chain_length DESC, origin_name
    LIMIT 30;
    ```


---


### 10. RFM with Grade History Trend Analysis


Combine RFM analysis with grade history to analyze
the RFM score distribution of downgraded customers.
Compare RFM differences between downgraded vs maintained/upgraded customers.


**Hint 1:** - Identify downgraded customers from grade history
- Calculate RFM scores in a separate CTE
- JOIN both results for group comparison



??? success "Answer"
    ```sql
    WITH recent_grade_change AS (
        SELECT
            customer_id,
            reason AS last_change_reason,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY changed_at DESC
            ) AS rn
        FROM customer_grade_history
        WHERE changed_at >= '2024-01-01'
    ),
    customer_trend AS (
        SELECT
            customer_id,
            last_change_reason,
            CASE
                WHEN last_change_reason = 'downgrade' THEN 'Downgraded'
                WHEN last_change_reason = 'upgrade'   THEN 'Upgraded'
                ELSE 'Maintained'
            END AS trend
        FROM recent_grade_change
        WHERE rn = 1
    ),
    rfm AS (
        SELECT
            c.id AS customer_id,
            c.grade,
            MAX(o.ordered_at) AS last_order,
            COUNT(*) AS frequency,
            ROUND(SUM(o.total_amount), 0) AS monetary,
            NTILE(4) OVER (ORDER BY MAX(o.ordered_at) ASC)  AS r_score,
            NTILE(4) OVER (ORDER BY COUNT(*) ASC)            AS f_score,
            NTILE(4) OVER (ORDER BY SUM(o.total_amount) ASC) AS m_score
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.grade
    )
    SELECT
        ct.trend,
        COUNT(*) AS customer_count,
        ROUND(AVG(r.r_score), 2) AS avg_recency,
        ROUND(AVG(r.f_score), 2) AS avg_frequency,
        ROUND(AVG(r.m_score), 2) AS avg_monetary,
        ROUND(AVG(r.r_score + r.f_score + r.m_score), 2) AS avg_rfm_total,
        ROUND(AVG(r.monetary), 0) AS avg_total_spent,
        ROUND(AVG(r.frequency), 1) AS avg_order_count
    FROM customer_trend AS ct
    INNER JOIN rfm AS r ON ct.customer_id = r.customer_id
    GROUP BY ct.trend
    ORDER BY
        CASE ct.trend
            WHEN 'Downgraded' THEN 1
            WHEN 'Maintained' THEN 2
            WHEN 'Upgraded' THEN 3
        END;
    ```


---


### 11. Grade Upgrade History


Find customers who were upgraded to VIP.
Show customer name, previous grade, change date, and reason.


**Hint 1:** - Filter `customer_grade_history.new_grade = 'VIP'`
- Filter `customer_grade_history.reason = 'upgrade'`
- JOIN `customers` for customer info



??? success "Answer"
    ```sql
    SELECT
        c.name          AS customer_name,
        c.email,
        cgh.old_grade,
        cgh.new_grade,
        cgh.changed_at,
        cgh.reason
    FROM customer_grade_history AS cgh
    INNER JOIN customers AS c ON cgh.customer_id = c.id
    WHERE cgh.new_grade = 'VIP'
      AND cgh.reason = 'upgrade'
    ORDER BY cgh.changed_at DESC
    LIMIT 20;
    ```


---


### 12. Point Balance Verification


Compare the sum of point_transactions with customers.point_balance
to find customers with mismatches.


**Hint 1:** - Calculate total with `SUM(amount)` from point_transactions
- Compare with `customers.point_balance`
- Use `HAVING` to filter mismatches



??? success "Answer"
    ```sql
    SELECT
        c.id          AS customer_id,
        c.name,
        c.point_balance AS current_balance,
        SUM(pt.amount)  AS calculated_balance,
        c.point_balance - SUM(pt.amount) AS difference
    FROM customers AS c
    INNER JOIN point_transactions AS pt ON c.id = pt.customer_id
    GROUP BY c.id, c.name, c.point_balance
    HAVING ABS(c.point_balance - SUM(pt.amount)) > 0
    ORDER BY ABS(difference) DESC
    LIMIT 20;
    ```


---
