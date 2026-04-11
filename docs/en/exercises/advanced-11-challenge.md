# Challenge Problems

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `customers` — Customer<br>
    `orders` — Order<br>
    `order_items` — Order Details<br>
    `products` — Product<br>
    `product_prices` — Price change history<br>
    `point_transactions` — Earn/use points<br>
    `calendar` — Date reference<br>
    `staff` — Employee

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    Ledger verification<br>
    Price change impact analysis<br>
    Market Basket Analysis (Association Rules)<br>
    Inventory Optimization<br>
    Predicting Customer Churn — A Comprehensive Mini-Project Problem

</div>

Each problem is a mini-project that requires several stages of analysis.
It reproduces complex scenarios encountered in practice and comprehensively utilizes all SQL concepts.

---


### Problem 1. Point balance reconstruction (ledger verification)


Reconstruct each customer's **point balance** based solely on the transaction history in the `point_transactions` table,
Compare to `customers.point_balance` and find **mismatching customers**.
A summary of each customer's accumulation/use/expiration history is also displayed.

| customer_name | earn_total | use_total | expire_total | calculated_balance | actual_balance | difference |
|-------------|-----------|---------|------------|------------------|--------------|-----------|


??? tip "Hint"
    - Summation from `point_transactions.amount` to `type`: earn(+), use(-), expire(-)
    - Calculated balance: `SUM(amount)` (amount is already separated by +/-)
    - `HAVING calculated != actual` compared to `customers.point_balance`


??? success "Answer"
    ```sql
    WITH point_summary AS (
        SELECT
            pt.customer_id,
            SUM(CASE WHEN pt.type = 'earn' THEN pt.amount ELSE 0 END) AS earn_total,
            SUM(CASE WHEN pt.type = 'use' THEN ABS(pt.amount) ELSE 0 END) AS use_total,
            SUM(CASE WHEN pt.type = 'expire' THEN ABS(pt.amount) ELSE 0 END) AS expire_total,
            SUM(pt.amount) AS calculated_balance
        FROM point_transactions AS pt
        GROUP BY pt.customer_id
    )
    SELECT
        c.name AS customer_name,
        ps.earn_total,
        ps.use_total,
        ps.expire_total,
        ps.calculated_balance,
        c.point_balance AS actual_balance,
        ps.calculated_balance - c.point_balance AS difference
    FROM point_summary AS ps
    JOIN customers AS c ON ps.customer_id = c.id
    WHERE ps.calculated_balance != c.point_balance
    ORDER BY ABS(ps.calculated_balance - c.point_balance) DESC;
    ```


---


### Problem 2. Price elasticity analysis


`product_prices` Use history to analyze the impact of price changes on sales volume.
**When the price fluctuates more than 10%** Compare the average daily sales volume for the 30 days before and after**
Calculate price elasticity (% change in sales / % change in price).

| product_name | price_change_date | old_price | new_price | price_change_pct | before_daily_avg | after_daily_avg | qty_change_pct | elasticity |
|-------------|-----------------|---------|---------|-----------------|----------------|---------------|---------------|-----------|


??? tip "Hint"
    - Compare with previous price from `product_prices` to `LAG(price)` → Filter for changes of more than 10%
    - 30 days before/after: `ordered_at BETWEEN DATE(change_date, '-30 days') AND DATE(change_date, '-1 day')` vs `+1 day ~ +30 days`
    - Elasticity = (rate of change in sales / rate of change in price)


??? success "Answer"
    ```sql
    WITH price_changes AS (
        SELECT
            pp.product_id,
            pp.started_at AS change_date,
            LAG(pp.price) OVER (PARTITION BY pp.product_id ORDER BY pp.started_at) AS old_price,
            pp.price AS new_price
        FROM product_prices AS pp
    ),
    significant_changes AS (
        SELECT *,
            ROUND(100.0 * (new_price - old_price) / old_price, 1) AS price_change_pct
        FROM price_changes
        WHERE old_price IS NOT NULL
          AND ABS(100.0 * (new_price - old_price) / old_price) >= 10
    ),
    before_sales AS (
        SELECT
            sc.product_id,
            sc.change_date,
            1.0 * COALESCE(SUM(oi.quantity), 0)
                / MAX(1, CAST(julianday(sc.change_date) - julianday(DATE(sc.change_date, '-30 days')) AS INTEGER))
                AS before_daily_avg
        FROM significant_changes AS sc
        LEFT JOIN order_items AS oi ON oi.product_id = sc.product_id
        LEFT JOIN orders AS o ON oi.order_id = o.id
            AND o.ordered_at >= DATE(sc.change_date, '-30 days')
            AND o.ordered_at <  sc.change_date
            AND o.status NOT IN ('cancelled')
        GROUP BY sc.product_id, sc.change_date
    ),
    after_sales AS (
        SELECT
            sc.product_id,
            sc.change_date,
            1.0 * COALESCE(SUM(oi.quantity), 0)
                / MAX(1, 30)
                AS after_daily_avg
        FROM significant_changes AS sc
        LEFT JOIN order_items AS oi ON oi.product_id = sc.product_id
        LEFT JOIN orders AS o ON oi.order_id = o.id
            AND o.ordered_at > sc.change_date
            AND o.ordered_at <= DATE(sc.change_date, '+30 days')
            AND o.status NOT IN ('cancelled')
        GROUP BY sc.product_id, sc.change_date
    )
    SELECT
        p.name AS product_name,
        sc.change_date AS price_change_date,
        CAST(sc.old_price AS INTEGER) AS old_price,
        CAST(sc.new_price AS INTEGER) AS new_price,
        sc.price_change_pct,
        ROUND(bs.before_daily_avg, 2) AS before_daily_avg,
        ROUND(afs.after_daily_avg, 2) AS after_daily_avg,
        ROUND(100.0 * (afs.after_daily_avg - bs.before_daily_avg)
            / NULLIF(bs.before_daily_avg, 0), 1) AS qty_change_pct,
        ROUND(
            (100.0 * (afs.after_daily_avg - bs.before_daily_avg) / NULLIF(bs.before_daily_avg, 0))
            / NULLIF(sc.price_change_pct, 0),
        2) AS elasticity
    FROM significant_changes AS sc
    JOIN products     AS p   ON sc.product_id = p.id
    JOIN before_sales AS bs  ON sc.product_id = bs.product_id AND sc.change_date = bs.change_date
    JOIN after_sales  AS afs ON sc.product_id = afs.product_id AND sc.change_date = afs.change_date
    WHERE bs.before_daily_avg > 0
    ORDER BY ABS(elasticity) DESC
    LIMIT 20;
    ```


---


### Problem 3. Product-related network (Market Basket)


Analyze the frequency of product pairs purchased together in the same order.
Calculate the top 20 frequently purchased product combinations, **support**, and **confidence**.

| product_a | product_b | co_purchase_count | support_pct | confidence_a_to_b | confidence_b_to_a |
|----------|----------|------------------|-----------|-------------------|-------------------|


??? tip "Hint"
    - Self-Join: `order_items AS a JOIN order_items AS b ON a.order_id = b.order_id AND a.product_id < b.product_id`
    - Support = Number of simultaneous purchase orders / Total number of orders
    - Reliability (A→B) = Number of simultaneous purchases / Number of A purchases


??? success "Answer"
    ```sql
    WITH valid_orders AS (
        SELECT DISTINCT id FROM orders WHERE status NOT IN ('cancelled')
    ),
    total AS (
        SELECT COUNT(*) AS total_orders FROM valid_orders
    ),
    pairs AS (
        SELECT
            a.product_id AS pid_a,
            b.product_id AS pid_b,
            COUNT(DISTINCT a.order_id) AS co_count
        FROM order_items AS a
        JOIN order_items AS b
            ON a.order_id = b.order_id
           AND a.product_id < b.product_id
        JOIN valid_orders AS vo ON a.order_id = vo.id
        GROUP BY a.product_id, b.product_id
        HAVING COUNT(DISTINCT a.order_id) >= 5
    ),
    product_counts AS (
        SELECT product_id, COUNT(DISTINCT order_id) AS order_count
        FROM order_items
        JOIN valid_orders ON order_items.order_id = valid_orders.id
        GROUP BY product_id
    )
    SELECT
        pa.name AS product_a,
        pb.name AS product_b,
        pr.co_count AS co_purchase_count,
        ROUND(100.0 * pr.co_count / t.total_orders, 3) AS support_pct,
        ROUND(100.0 * pr.co_count / pca.order_count, 1) AS confidence_a_to_b,
        ROUND(100.0 * pr.co_count / pcb.order_count, 1) AS confidence_b_to_a
    FROM pairs AS pr
    CROSS JOIN total AS t
    JOIN products       AS pa  ON pr.pid_a = pa.id
    JOIN products       AS pb  ON pr.pid_b = pb.id
    JOIN product_counts AS pca ON pr.pid_a = pca.product_id
    JOIN product_counts AS pcb ON pr.pid_b = pcb.product_id
    ORDER BY pr.co_count DESC
    LIMIT 20;
    ```


---


### Problem 4. Inventory turnover and appropriate inventory analysis


Find **Inventory Turnover** and **Days of Inventory** for each product.
Based on the sales speed of the last 90 days, we determine **appropriate inventory level** and current inventory excess or shortage.

| product_name | current_stock | avg_daily_sales_90d | days_of_inventory | turnover_rate | optimal_stock_30d | stock_status |
|-------------|-------------|-------------------|------------------|-------------|-----------------|-------------|


??? tip "Hint"
    - 90-day average daily sales: `SUM(quantity) / 90` (based on orders from the last 90 days)
    - Number of inventory days: `current_stock / avg_daily_sales`
    - Turnover: `(annual_sales * product_cost) / current_inventory_cost`
    - Appropriate inventory (30 days): `daily_avg * 30`
    - Status: surplus (>60 days), adequate (15-60 days), shortage (<15 days), sold out (0)


??? success "Answer"
    ```sql
    WITH recent_sales AS (
        SELECT
            oi.product_id,
            SUM(oi.quantity) AS qty_90d,
            ROUND(1.0 * SUM(oi.quantity) / 90, 2) AS avg_daily_sales
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('2025-06-30', '-90 days')
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY oi.product_id
    ),
    annual_sales AS (
        SELECT
            oi.product_id,
            SUM(oi.quantity) AS qty_annual
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('2025-06-30', '-365 days')
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    )
    SELECT
        p.name AS product_name,
        p.stock_qty AS current_stock,
        COALESCE(rs.avg_daily_sales, 0) AS avg_daily_sales_90d,
        CASE
            WHEN COALESCE(rs.avg_daily_sales, 0) = 0 THEN 9999
            ELSE CAST(p.stock_qty / rs.avg_daily_sales AS INTEGER)
        END AS days_of_inventory,
        ROUND(COALESCE(ans.qty_annual, 0) * p.cost_price
            / NULLIF(p.stock_qty * p.cost_price, 0), 1) AS turnover_rate,
        CAST(COALESCE(rs.avg_daily_sales, 0) * 30 AS INTEGER) AS optimal_stock_30d,
        CASE
            WHEN p.stock_qty = 0 THEN 'OUT_OF_STOCK'
            WHEN COALESCE(rs.avg_daily_sales, 0) = 0 THEN 'DEAD_STOCK'
            WHEN p.stock_qty / rs.avg_daily_sales > 60 THEN 'OVERSTOCK'
            WHEN p.stock_qty / rs.avg_daily_sales < 15 THEN 'LOW_STOCK'
            ELSE 'OPTIMAL'
        END AS stock_status
    FROM products AS p
    LEFT JOIN recent_sales AS rs ON p.id = rs.product_id
    LEFT JOIN annual_sales AS ans ON p.id = ans.product_id
    WHERE p.is_active = 1
    ORDER BY
        CASE
            WHEN p.stock_qty = 0 THEN 1
            WHEN COALESCE(rs.avg_daily_sales, 0) = 0 THEN 5
            WHEN p.stock_qty / rs.avg_daily_sales < 15 THEN 2
            WHEN p.stock_qty / rs.avg_daily_sales > 60 THEN 4
            ELSE 3
        END,
        rs.avg_daily_sales DESC;
    ```


---


### Problem 5. Customer lifetime value (CLV) prediction model


Calculate each customer's **to-date CLV**, based on past purchase patterns
**Estimate your expected CLV for the next 12 months**.
Subscription length, purchase frequency, average purchase amount, and recency are all taken into account.

| customer_name | grade | tenure_months | total_orders | total_spent | avg_order_value | orders_per_month | recency_days | predicted_clv_12m | clv_tier |
|-------------|------|-------------|-----------|----------|---------------|----------------|-------------|-----------------|---------|


??? tip "Hint"
    - Subscription period (months): `(julianday('2025-06-30') - julianday(created_at)) / 30`
    - Monthly purchase frequency: `order_count / months_since_signup`
    - Predicted CLV = `monthly_purchase_frequency * avg_order_amount * 12 * decay_rate`
    - Decay rate: based on recency — 1.0 for purchases in the last 90 days, 0.7 for 180 days, 0.4 for 365 days, 0.1 for others.


??? success "Answer"
    ```sql
    WITH customer_metrics AS (
        SELECT
            c.id AS customer_id,
            c.name AS customer_name,
            c.grade,
            ROUND((julianday('2025-06-30') - julianday(c.created_at)) / 30, 1) AS tenure_months,
            COUNT(o.id) AS total_orders,
            CAST(COALESCE(SUM(o.total_amount), 0) AS INTEGER) AS total_spent,
            ROUND(COALESCE(AVG(o.total_amount), 0), 0) AS avg_order_value,
            CAST(julianday('2025-06-30') - julianday(MAX(o.ordered_at)) AS INTEGER) AS recency_days
        FROM customers AS c
        LEFT JOIN orders AS o
            ON c.id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY c.id, c.name, c.grade, c.created_at
    ),
    with_predictions AS (
        SELECT
            customer_name,
            grade,
            CAST(tenure_months AS INTEGER) AS tenure_months,
            total_orders,
            total_spent,
            CAST(avg_order_value AS INTEGER) AS avg_order_value,
            ROUND(total_orders / NULLIF(tenure_months, 0), 2) AS orders_per_month,
            recency_days,
            CAST(
                (total_orders / NULLIF(tenure_months, 0))
                * avg_order_value
                * 12
                * CASE
                    WHEN recency_days <= 90  THEN 1.0
                    WHEN recency_days <= 180 THEN 0.7
                    WHEN recency_days <= 365 THEN 0.4
                    ELSE 0.1
                  END
            AS INTEGER) AS predicted_clv_12m
        FROM customer_metrics
        WHERE total_orders > 0
    )
    SELECT
        customer_name,
        grade,
        tenure_months,
        total_orders,
        total_spent,
        avg_order_value,
        orders_per_month,
        recency_days,
        predicted_clv_12m,
        CASE
            WHEN predicted_clv_12m >= 5000000 THEN 'Platinum'
            WHEN predicted_clv_12m >= 2000000 THEN 'Gold'
            WHEN predicted_clv_12m >= 500000  THEN 'Silver'
            ELSE 'Bronze'
        END AS clv_tier
    FROM with_predictions
    ORDER BY predicted_clv_12m DESC
    LIMIT 30;
    ```


---


### Problem 6. View design: Real-time product dashboard


Write a `CREATE VIEW` statement that provides the following information:
Current price for each product, 30-day/90-day sales, average rating, inventory status, return rate, number of wishlists.
This single view should enable the product team to perform routine monitoring.

| id | name | brand | category | price | sold_30d | sold_90d | avg_rating | review_count | stock_qty | stock_status | return_rate_pct | wishlist_count |
|----|------|-------|---------|-------|---------|---------|-----------|-------------|----------|-------------|----------------|-------------|


??? tip "Hint"
    - Combine 3~4 subqueries into `LEFT JOIN`
    - 30-day/90-day sales: Based on `DATE('now', '-30 days')`
    - Return rate: `return_count / order_count`
    - Stock status: Sort based on stock_qty


??? success "Answer"
    ```sql
    CREATE VIEW v_product_dashboard AS
    WITH sales_30d AS (
        SELECT oi.product_id, SUM(oi.quantity) AS sold_30d
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('now', '-30 days')
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    ),
    sales_90d AS (
        SELECT oi.product_id, SUM(oi.quantity) AS sold_90d
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('now', '-90 days')
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    ),
    review_agg AS (
        SELECT product_id,
               ROUND(AVG(rating), 1) AS avg_rating,
               COUNT(*) AS review_count
        FROM reviews
        GROUP BY product_id
    ),
    return_rate AS (
        SELECT
            oi.product_id,
            COUNT(DISTINCT r.id) AS return_count,
            COUNT(DISTINCT o.id) AS order_count
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        LEFT JOIN returns AS r ON o.id = r.order_id
        GROUP BY oi.product_id
    ),
    wish_cnt AS (
        SELECT product_id, COUNT(*) AS wishlist_count
        FROM wishlists
        GROUP BY product_id
    )
    SELECT
        p.id,
        p.name,
        p.brand,
        cat.name AS category,
        p.price,
        COALESCE(s30.sold_30d, 0) AS sold_30d,
        COALESCE(s90.sold_90d, 0) AS sold_90d,
        COALESCE(ra.avg_rating, 0) AS avg_rating,
        COALESCE(ra.review_count, 0) AS review_count,
        p.stock_qty,
        CASE
            WHEN p.stock_qty = 0 THEN 'OUT_OF_STOCK'
            WHEN p.stock_qty < 10 THEN 'LOW'
            WHEN p.stock_qty < 100 THEN 'NORMAL'
            ELSE 'HIGH'
        END AS stock_status,
        ROUND(100.0 * COALESCE(rr.return_count, 0)
            / NULLIF(rr.order_count, 0), 1) AS return_rate_pct,
        COALESCE(wc.wishlist_count, 0) AS wishlist_count
    FROM products AS p
    JOIN categories AS cat ON p.category_id = cat.id
    LEFT JOIN sales_30d   AS s30 ON p.id = s30.product_id
    LEFT JOIN sales_90d   AS s90 ON p.id = s90.product_id
    LEFT JOIN review_agg  AS ra  ON p.id = ra.product_id
    LEFT JOIN return_rate AS rr  ON p.id = rr.product_id
    LEFT JOIN wish_cnt    AS wc  ON p.id = wc.product_id
    WHERE p.is_active = 1
    ORDER BY COALESCE(s30.sold_30d, 0) DESC;

    -- Example usage of the view
    -- SELECT * FROM v_product_dashboard WHERE stock_status = 'LOW' ORDER BY sold_30d DESC;
    ```


---


### Problem 7. Trigger design: Simulate out-of-stock notification


When an order comes in, if inventory falls below **safe stock (30-day average sales x 1.5)**
Design a **trigger** that automatically inserts a record of type 'alert' into `inventory_transactions`.
(Actual trigger CREATE statement + action verification SELECT statement)

| product_id | product_name | current_stock | safety_stock | alert_needed |
|-----------|-------------|-------------|-------------|-------------|


??? tip "Hint"
    - Safety stock calculation: average daily sales for the past 30 days * 1.5 * 30
    - Must be executed after an existing `trg_deduct_stock` trigger
    - Conditional INSERT after checking inventory in `AFTER INSERT ON order_items`


??? success "Answer"
    ```sql
    -- 1) Trigger DDL
    CREATE TRIGGER trg_low_stock_alert AFTER INSERT ON order_items
    WHEN (
        SELECT stock_qty FROM products WHERE id = NEW.product_id
    ) < (
        SELECT COALESCE(SUM(oi.quantity), 0) * 1.5
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE oi.product_id = NEW.product_id
          AND o.ordered_at >= DATE('now', '-30 days')
          AND o.status NOT IN ('cancelled')
    )
    BEGIN
        INSERT INTO inventory_transactions (product_id, type, quantity, reference_id, notes, created_at)
        VALUES (
            NEW.product_id,
            'alert',
            0,
            NEW.order_id,
            'LOW_STOCK_ALERT: stock below safety level',
            DATETIME('now')
        );
    END;

    -- 2) Query current low-stock products (can verify without trigger)
    WITH daily_avg AS (
        SELECT
            oi.product_id,
            1.0 * SUM(oi.quantity) / 30 AS avg_daily
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('2025-06-30', '-30 days')
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    )
    SELECT
        p.id AS product_id,
        p.name AS product_name,
        p.stock_qty AS current_stock,
        CAST(da.avg_daily * 1.5 * 30 AS INTEGER) AS safety_stock,
        CASE
            WHEN p.stock_qty < da.avg_daily * 1.5 * 30 THEN 'YES'
            ELSE 'NO'
        END AS alert_needed
    FROM products AS p
    JOIN daily_avg AS da ON p.id = da.product_id
    WHERE p.is_active = 1
      AND p.stock_qty < da.avg_daily * 1.5 * 30
    ORDER BY (p.stock_qty - da.avg_daily * 1.5 * 30) ASC;
    ```


---


### Problem 8. Index optimization analysis


Analyze the following slow query with EXPLAIN QUERY PLAN,
Design a suitable **composite index**:
“Total sales of VIP customers who purchased products in a specific category in 2024”

| detail | scan_type | table_name | index_used |
|--------|----------|-----------|-----------|


??? tip "Hint"
    - Check current execution plan with `EXPLAIN QUERY PLAN SELECT ...`
    - Difference between SCAN and SEARCH: SCAN is full search, SEARCH utilizes indexes
    - Composite index: Combines WHERE condition and JOIN key


??? success "Answer"
    ```sql
    -- 1) Check execution plan of original query
    EXPLAIN QUERY PLAN
    SELECT
        c.name, SUM(o.total_amount) AS total_spent
    FROM customers AS c
    JOIN orders AS o ON c.id = o.customer_id
    JOIN order_items AS oi ON o.id = oi.order_id
    JOIN products AS p ON oi.product_id = p.id
    WHERE c.grade = 'VIP'
      AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
      AND o.status NOT IN ('cancelled')
      AND p.category_id = 5
    GROUP BY c.id, c.name;

    -- 2) Add optimization indexes
    -- Customer grade filter + join key
    CREATE INDEX idx_customers_grade ON customers(grade);

    -- Order date + status + customer composite index (covering)
    CREATE INDEX idx_orders_date_status_customer
        ON orders(ordered_at, status, customer_id);

    -- Order items: order -> product join optimization
    -- (idx_order_items_order_product already exists)

    -- Products: category filter
    -- (idx_products_category_id already exists)

    -- 3) Re-check execution plan after optimization
    EXPLAIN QUERY PLAN
    SELECT
        c.name, SUM(o.total_amount) AS total_spent
    FROM customers AS c
    JOIN orders AS o ON c.id = o.customer_id
    JOIN order_items AS oi ON o.id = oi.order_id
    JOIN products AS p ON oi.product_id = p.id
    WHERE c.grade = 'VIP'
      AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
      AND o.status NOT IN ('cancelled')
      AND p.category_id = 5
    GROUP BY c.id, c.name;
    ```


---


### Problem 9. Abnormal transaction detection system


Detect **fraud** with the following rules:
(1) 3 or more orders within 1 hour, (2) order amount exceeding 5 times the customer average,
(3) Orders worth KRW 1 million or more within 24 hours of new registration, (4) Single orders of 5 or more of the same product.
Reports all spells cast by each rule.

| rule | order_id | customer_name | ordered_at | total_amount | detail |
|------|---------|-------------|-----------|-------------|--------|


??? tip "Hint"
    - Rule 1: Count the number of orders within a 1-hour range using a window function
    - Rule 2: Calculate customer average with CTE and compare with individual orders
    - Rule 3: `julianday(ordered_at) - julianday(created_at) < 1`
    - Combine results of 4 rules with `UNION ALL`


??? success "Answer"
    ```sql
    -- Rule 1: 3+ orders within 1 hour
    WITH rule1 AS (
        SELECT
            'Rapid Orders (3+ in 1hr)' AS rule,
            o.id AS order_id,
            c.name AS customer_name,
            o.ordered_at,
            o.total_amount,
            'Orders in window: ' || (
                SELECT COUNT(*)
                FROM orders o2
                WHERE o2.customer_id = o.customer_id
                  AND ABS(julianday(o2.ordered_at) - julianday(o.ordered_at)) * 24 <= 1
            ) AS detail
        FROM orders AS o
        JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled')
          AND (
              SELECT COUNT(*)
              FROM orders o2
              WHERE o2.customer_id = o.customer_id
                AND ABS(julianday(o2.ordered_at) - julianday(o.ordered_at)) * 24 <= 1
          ) >= 3
    ),
    -- Rule 2: Exceeds 5x customer average
    cust_avg AS (
        SELECT customer_id, AVG(total_amount) AS avg_amount
        FROM orders WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
        HAVING COUNT(*) >= 3
    ),
    rule2 AS (
        SELECT
            'Amount > 5x Average' AS rule,
            o.id, c.name, o.ordered_at, o.total_amount,
            'Avg: ' || CAST(ca.avg_amount AS INTEGER) || ', Ratio: '
                || ROUND(o.total_amount / ca.avg_amount, 1) AS detail
        FROM orders AS o
        JOIN customers AS c ON o.customer_id = c.id
        JOIN cust_avg AS ca ON o.customer_id = ca.customer_id
        WHERE o.status NOT IN ('cancelled')
          AND o.total_amount > ca.avg_amount * 5
    ),
    -- Rule 3: 1M+ KRW within 24 hours of signup
    rule3 AS (
        SELECT
            'New User High Value' AS rule,
            o.id, c.name, o.ordered_at, o.total_amount,
            'Hours since signup: ' || CAST((julianday(o.ordered_at) - julianday(c.created_at)) * 24 AS INTEGER) AS detail
        FROM orders AS o
        JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled')
          AND (julianday(o.ordered_at) - julianday(c.created_at)) < 1
          AND o.total_amount >= 1000000
    ),
    -- Rule 4: 5+ of the same product in a single order
    rule4 AS (
        SELECT
            'Bulk Single Item (5+)' AS rule,
            o.id, c.name, o.ordered_at, o.total_amount,
            p.name || ' x ' || oi.quantity AS detail
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        JOIN customers AS c ON o.customer_id = c.id
        JOIN products AS p ON oi.product_id = p.id
        WHERE oi.quantity >= 5
          AND o.status NOT IN ('cancelled')
    )
    SELECT * FROM rule1
    UNION ALL SELECT * FROM rule2
    UNION ALL SELECT * FROM rule3
    UNION ALL SELECT * FROM rule4
    ORDER BY rule, total_amount DESC;
    ```


---


### Problem 10. CS performance + customer satisfaction linkage analysis


Link and analyze **complaint handling performance** and **post-processing customer satisfaction (repurchase/review rating)** for each CS employee.
Number of cases handled by employee, average resolution time, escalation rate, compensation cost,
Then, we obtain the customer's repurchase rate and review rating within 30 days after processing.

| staff_name | department | resolved_count | avg_resolve_hours | escalation_rate | total_compensation | post_repurchase_pct | post_avg_rating |
|-----------|-----------|---------------|------------------|----------------|-------------------|-------------------|----------------|


??? tip "Hint"
    - Associate employee with `complaints.staff_id`
    - Resolution time: `julianday(resolved_at) - julianday(created_at)` * 24
    - Escalation: Rate of `escalated = 1`
    - Repurchase: Whether or not an order exists within 30 days after the complaint is resolved.


??? success "Answer"
    ```sql
    WITH staff_perf AS (
        SELECT
            cp.staff_id,
            COUNT(*) AS resolved_count,
            ROUND(AVG((julianday(cp.resolved_at) - julianday(cp.created_at)) * 24), 1) AS avg_resolve_hours,
            ROUND(100.0 * SUM(cp.escalated) / COUNT(*), 1) AS escalation_rate,
            CAST(SUM(COALESCE(cp.compensation_amount, 0)) AS INTEGER) AS total_compensation
        FROM complaints AS cp
        WHERE cp.status IN ('resolved', 'closed')
          AND cp.staff_id IS NOT NULL
        GROUP BY cp.staff_id
    ),
    post_satisfaction AS (
        SELECT
            cp.staff_id,
            COUNT(DISTINCT cp.id) AS resolved_with_customer,
            COUNT(DISTINCT CASE
                WHEN EXISTS (
                    SELECT 1 FROM orders o
                    WHERE o.customer_id = cp.customer_id
                      AND o.ordered_at > cp.resolved_at
                      AND o.ordered_at <= DATE(cp.resolved_at, '+30 days')
                      AND o.status NOT IN ('cancelled')
                )
                THEN cp.customer_id
            END) AS repurchased_customers,
            COUNT(DISTINCT cp.customer_id) AS unique_customers
        FROM complaints AS cp
        WHERE cp.status IN ('resolved', 'closed')
          AND cp.staff_id IS NOT NULL
          AND cp.resolved_at IS NOT NULL
        GROUP BY cp.staff_id
    ),
    post_reviews AS (
        SELECT
            cp.staff_id,
            ROUND(AVG(r.rating), 2) AS post_avg_rating
        FROM complaints AS cp
        JOIN reviews AS r ON cp.customer_id = r.customer_id
            AND r.created_at > cp.resolved_at
            AND r.created_at <= DATE(cp.resolved_at, '+30 days')
        WHERE cp.status IN ('resolved', 'closed')
          AND cp.staff_id IS NOT NULL
        GROUP BY cp.staff_id
    )
    SELECT
        s.name AS staff_name,
        s.department,
        sp.resolved_count,
        sp.avg_resolve_hours,
        sp.escalation_rate,
        sp.total_compensation,
        ROUND(100.0 * ps.repurchased_customers / NULLIF(ps.unique_customers, 0), 1) AS post_repurchase_pct,
        COALESCE(pr.post_avg_rating, 0) AS post_avg_rating
    FROM staff_perf AS sp
    JOIN staff AS s ON sp.staff_id = s.id
    LEFT JOIN post_satisfaction AS ps ON sp.staff_id = ps.staff_id
    LEFT JOIN post_reviews AS pr ON sp.staff_id = pr.staff_id
    ORDER BY sp.resolved_count DESC;
    ```


---


### Problem 11. Monthly Management Report (Executive Summary)


Generate **December 2024 Management Report** with a single query. Includes the following sections:
(A) Sales Summary: Total Sales, MoM%, YoY%, (B) Top 5 Products,
(C) Customer metrics: New/repurchasing/churn, (D) CS summary: Total number of cases/Resolution rate/Average resolution time.
The final result is output in Key-Value format in two columns: `key` and `value`.

| key | value |
|-----|-------|
| Total Revenue | 123,456,789 |
| MoM Growth | 12.3% |
| ... | ... |


??? tip "Hint"
    - Calculate each section as CTE and combine it into key-value pairs with `UNION ALL`
    - Number format: `PRINTF('%,d', value)` or `CAST(... AS TEXT)`
    - Select only key KPIs within 20 lines


??? success "Answer"
    ```sql
    WITH dec_rev AS (
        SELECT SUM(total_amount) AS rev
        FROM orders
        WHERE ordered_at >= '2024-12-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    nov_rev AS (
        SELECT SUM(total_amount) AS rev
        FROM orders
        WHERE ordered_at >= '2024-11-01' AND ordered_at < '2024-12-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    dec_2023_rev AS (
        SELECT SUM(total_amount) AS rev
        FROM orders
        WHERE ordered_at >= '2023-12-01' AND ordered_at < '2024-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    top_products AS (
        SELECT
            p.name,
            CAST(SUM(oi.quantity * oi.unit_price) AS INTEGER) AS rev,
            ROW_NUMBER() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS rn
        FROM order_items AS oi
        JOIN orders AS o ON oi.order_id = o.id
        JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at >= '2024-12-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled')
        GROUP BY p.id, p.name
    ),
    customer_metrics AS (
        SELECT
            COUNT(DISTINCT CASE
                WHEN NOT EXISTS (SELECT 1 FROM orders o2 WHERE o2.customer_id = o.customer_id AND o2.ordered_at < '2024-12-01' AND o2.status NOT IN ('cancelled'))
                THEN o.customer_id END) AS new_cust,
            COUNT(DISTINCT CASE
                WHEN EXISTS (SELECT 1 FROM orders o2 WHERE o2.customer_id = o.customer_id AND o2.ordered_at < '2024-12-01' AND o2.status NOT IN ('cancelled'))
                THEN o.customer_id END) AS repeat_cust
        FROM orders AS o
        WHERE o.ordered_at >= '2024-12-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled')
    ),
    cs_metrics AS (
        SELECT
            COUNT(*) AS total_tickets,
            ROUND(100.0 * SUM(CASE WHEN status IN ('resolved','closed') THEN 1 ELSE 0 END) / COUNT(*), 1) AS resolve_rate,
            ROUND(AVG(CASE WHEN resolved_at IS NOT NULL
                THEN (julianday(resolved_at) - julianday(created_at)) * 24 END), 1) AS avg_hours
        FROM complaints
        WHERE created_at >= '2024-12-01' AND created_at < '2025-01-01'
    )
    SELECT '== [A] Sales Summary ==' AS key, '' AS value
    UNION ALL SELECT 'Total Revenue', PRINTF('%,d', CAST((SELECT rev FROM dec_rev) AS INTEGER))
    UNION ALL SELECT 'MoM Growth %', ROUND(100.0 * ((SELECT rev FROM dec_rev) - (SELECT rev FROM nov_rev)) / (SELECT rev FROM nov_rev), 1) || '%'
    UNION ALL SELECT 'YoY Growth %', ROUND(100.0 * ((SELECT rev FROM dec_rev) - (SELECT rev FROM dec_2023_rev)) / NULLIF((SELECT rev FROM dec_2023_rev), 0), 1) || '%'
    UNION ALL SELECT '== [B] Top Products ==', ''
    UNION ALL SELECT '#' || rn || ' ' || name, PRINTF('%,d', rev) FROM top_products WHERE rn <= 5
    UNION ALL SELECT '== [C] Customer Metrics ==', ''
    UNION ALL SELECT 'New Customers', CAST(new_cust AS TEXT) FROM customer_metrics
    UNION ALL SELECT 'Repeat Customers', CAST(repeat_cust AS TEXT) FROM customer_metrics
    UNION ALL SELECT '== [D] CS Summary ==', ''
    UNION ALL SELECT 'Total Tickets', CAST(total_tickets AS TEXT) FROM cs_metrics
    UNION ALL SELECT 'Resolution Rate', resolve_rate || '%' FROM cs_metrics
    UNION ALL SELECT 'Avg Resolve Time', avg_hours || ' hours' FROM cs_metrics;
    ```


---


### Problem 12. Data migration verification


Hypothetical scenario: The structure of `orders` changes and the format of `order_number` becomes
It should change from `ORD-YYYYMMDD-NNNNN` to `ORD/YYYY/MM/NNNNN`.
(1) Write conversion SQL, and (2) Write data consistency verification queries before and after conversion.
(only verification without actual UPDATE)

| order_id | old_format | new_format | date_match | sequence_match |
|---------|-----------|-----------|-----------|---------------|


??? tip "Hint"
    - Parse existing format: `SUBSTR(order_number, 5, 8)` = YYYYMMDD, `SUBSTR(order_number, 14)` = NNNNN
    - New format: `'ORD/' || SUBSTR(dt, 1, 4) || '/' || SUBSTR(dt, 5, 2) || '/' || seq`
    - Verification: Convert again after conversion to check if it matches the original.


??? success "Answer"
    ```sql
    WITH migration AS (
        SELECT
            id AS order_id,
            order_number AS old_format,
            'ORD/' ||
                SUBSTR(order_number, 5, 4) || '/' ||
                SUBSTR(order_number, 9, 2) || '/' ||
                SUBSTR(order_number, 14) AS new_format,
            -- Reverse conversion verification
            SUBSTR(order_number, 5, 4) AS old_year,
            SUBSTR(order_number, 9, 2) AS old_month,
            SUBSTR(order_number, 14) AS old_seq
        FROM orders
    ),
    verification AS (
        SELECT
            order_id,
            old_format,
            new_format,
            -- Extract date from new format and compare with original
            CASE
                WHEN SUBSTR(new_format, 5, 4) = old_year
                 AND SUBSTR(new_format, 10, 2) = old_month
                THEN 'OK' ELSE 'MISMATCH'
            END AS date_match,
            -- Extract sequence from new format and compare with original
            CASE
                WHEN SUBSTR(new_format, 13) = old_seq
                THEN 'OK' ELSE 'MISMATCH'
            END AS sequence_match
        FROM migration
    )
    -- Verification summary
    SELECT
        COUNT(*) AS total_records,
        SUM(CASE WHEN date_match = 'OK' THEN 1 ELSE 0 END) AS date_ok,
        SUM(CASE WHEN date_match = 'MISMATCH' THEN 1 ELSE 0 END) AS date_fail,
        SUM(CASE WHEN sequence_match = 'OK' THEN 1 ELSE 0 END) AS seq_ok,
        SUM(CASE WHEN sequence_match = 'MISMATCH' THEN 1 ELSE 0 END) AS seq_fail
    FROM verification;

    -- Mismatch details (if any)
    -- SELECT * FROM verification WHERE date_match = 'MISMATCH' OR sequence_match = 'MISMATCH' LIMIT 10;
    ```


---


### Problem 13. Full audit log simulation


Combine `customer_grade_history`, `point_transactions`, and `inventory_transactions`
Create a **Unified Audit Log**.
Sorts chronologically and displays the impact (before/after) of each event.
Based on data from June 2025, we extract the most recent 100 cases.

| event_time | event_type | entity_type | entity_id | entity_name | before_value | after_value | detail |
|-----------|-----------|-----------|---------|-----------|------------|-----------|--------|


??? tip "Hint"
    - Integrate events from 3 tables with `UNION ALL`
    - Grade change: before=old_grade, after=new_grade
    - Points: before=balance_after-amount, after=balance_after
    - Inventory: type and quantity displayed
    - `ORDER BY event_time DESC LIMIT 100`


??? success "Answer"
    ```sql
    -- Grade change events
    SELECT
        gh.changed_at AS event_time,
        'GRADE_CHANGE' AS event_type,
        'customer' AS entity_type,
        gh.customer_id AS entity_id,
        c.name AS entity_name,
        COALESCE(gh.old_grade, '(none)') AS before_value,
        gh.new_grade AS after_value,
        gh.reason AS detail
    FROM customer_grade_history AS gh
    JOIN customers AS c ON gh.customer_id = c.id
    WHERE gh.changed_at >= '2025-06-01' AND gh.changed_at < '2025-07-01'

    UNION ALL

    -- Point events
    SELECT
        pt.created_at,
        'POINT_' || UPPER(pt.type),
        'customer',
        pt.customer_id,
        c.name,
        CAST(pt.balance_after - pt.amount AS TEXT),
        CAST(pt.balance_after AS TEXT),
        pt.reason || COALESCE(' (order #' || pt.order_id || ')', '')
    FROM point_transactions AS pt
    JOIN customers AS c ON pt.customer_id = c.id
    WHERE pt.created_at >= '2025-06-01' AND pt.created_at < '2025-07-01'

    UNION ALL

    -- Inventory events
    SELECT
        it.created_at,
        'INVENTORY_' || UPPER(it.type),
        'product',
        it.product_id,
        p.name,
        '',
        CASE WHEN it.quantity > 0 THEN '+' ELSE '' END || CAST(it.quantity AS TEXT),
        COALESCE(it.notes, '') || COALESCE(' (ref #' || it.reference_id || ')', '')
    FROM inventory_transactions AS it
    JOIN products AS p ON it.product_id = p.id
    WHERE it.created_at >= '2025-06-01' AND it.created_at < '2025-07-01'

    ORDER BY event_time DESC
    LIMIT 100;
    ```


---


### Problem 14. Product Successor Chain Analysis


Follow `products.successor_id` to form the **product generation chain**.
With recursive CTE, price changes from 1st generation → 2nd generation → ... → active products and
Analyze sales trends by generation.

| generation | product_name | brand | price | total_revenue | is_current | chain_path |
|-----------|-------------|-------|-------|-------------|-----------|-----------|


??? tip "Hint"
    - If `products.successor_id` is NULL, active or discontinued (check discontinued_at)
    - Start of recursion: `WHERE NOT EXISTS (SELECT 1 FROM products p2 WHERE p2.successor_id = p.id)` (1st generation: product without predecessor), not `successor_id IS NULL AND discontinued_at IS NULL` (active product)
    - Recursive progression: search for next generation with `p.successor_id = chain.id`


??? success "Answer"
    ```sql
    WITH RECURSIVE chain AS (
        -- Gen 1: Products with no predecessor pointing to them (start of chain)
        SELECT
            p.id,
            p.name,
            p.brand,
            p.price,
            p.successor_id,
            p.is_active,
            p.discontinued_at,
            1 AS generation,
            p.name AS chain_path
        FROM products AS p
        WHERE NOT EXISTS (
            SELECT 1 FROM products p2 WHERE p2.successor_id = p.id
        )
        AND p.successor_id IS NOT NULL  -- Only starting points with a successor

        UNION ALL

        -- Next generation
        SELECT
            p.id,
            p.name,
            p.brand,
            p.price,
            p.successor_id,
            p.is_active,
            p.discontinued_at,
            ch.generation + 1,
            ch.chain_path || ' → ' || p.name
        FROM products AS p
        JOIN chain AS ch ON ch.successor_id = p.id
        WHERE ch.generation < 10  -- Prevent infinite loop
    )
    SELECT
        c.generation,
        c.name AS product_name,
        c.brand,
        CAST(c.price AS INTEGER) AS price,
        COALESCE(CAST(SUM(oi.quantity * oi.unit_price) AS INTEGER), 0) AS total_revenue,
        CASE WHEN c.is_active = 1 AND c.discontinued_at IS NULL THEN 'YES' ELSE 'NO' END AS is_current,
        c.chain_path
    FROM chain AS c
    LEFT JOIN order_items AS oi ON c.id = oi.product_id
    LEFT JOIN orders AS o ON oi.order_id = o.id
        AND o.status NOT IN ('cancelled')
    GROUP BY c.id, c.generation, c.name, c.brand, c.price,
             c.is_active, c.discontinued_at, c.chain_path
    ORDER BY c.chain_path, c.generation;
    ```


---


### Problem 15. Comprehensive health check: database integrity audit


Check your entire database for referential integrity and business rule violations at once.
We verify all 10 rules:

1. Delivery cases with delivery completion date < shipping date
2. Orders with order date < customer subscription date
3. Reviews with review writing date < order date
4. Employees who are their own boss (manager_id = id)
5. Customers with negative point balance
6. Category referencing non-existent parent_id
7. Canceled orders with delivery completion records
8. Orders where the discount amount is greater than the order amount
9. Products that are active but have negative inventory
10. Coupons with an expiration date earlier than the start date

| rule_no | rule_description | violation_count | sample_ids |
|--------|-----------------|----------------|-----------|


??? tip "Hint"
    - Write each rule in `SELECT rule_number, description, COUNT(*), GROUP_CONCAT(id)` format
    - Combine 10 with `UNION ALL`
    - Show only actual violations with `WHERE violation_count > 0`


??? success "Answer"
    ```sql
    SELECT 1 AS rule_no,
           'Delivery before shipment' AS rule_description,
           COUNT(*) AS violation_count,
           COALESCE(GROUP_CONCAT(id, ','), '') AS sample_ids
    FROM shipping
    WHERE delivered_at IS NOT NULL AND shipped_at IS NOT NULL AND delivered_at < shipped_at

    UNION ALL
    SELECT 2, 'Order before customer signup',
           COUNT(*), COALESCE(GROUP_CONCAT(o.id, ','), '')
    FROM orders AS o
    JOIN customers AS c ON o.customer_id = c.id
    WHERE o.ordered_at < c.created_at

    UNION ALL
    SELECT 3, 'Review before order date',
           COUNT(*), COALESCE(GROUP_CONCAT(r.id, ','), '')
    FROM reviews AS r
    JOIN orders AS o ON r.order_id = o.id
    WHERE r.created_at < o.ordered_at

    UNION ALL
    SELECT 4, 'Self-referencing manager',
           COUNT(*), COALESCE(GROUP_CONCAT(id, ','), '')
    FROM staff
    WHERE manager_id = id

    UNION ALL
    SELECT 5, 'Negative point balance',
           COUNT(*), COALESCE(GROUP_CONCAT(id, ','), '')
    FROM customers
    WHERE point_balance < 0

    UNION ALL
    SELECT 6, 'Orphan category parent_id',
           COUNT(*), COALESCE(GROUP_CONCAT(c1.id, ','), '')
    FROM categories AS c1
    WHERE c1.parent_id IS NOT NULL
      AND NOT EXISTS (SELECT 1 FROM categories c2 WHERE c2.id = c1.parent_id)

    UNION ALL
    SELECT 7, 'Cancelled order with delivery',
           COUNT(*), COALESCE(GROUP_CONCAT(o.id, ','), '')
    FROM orders AS o
    JOIN shipping AS s ON o.id = s.order_id
    WHERE o.status = 'cancelled' AND s.status = 'delivered'

    UNION ALL
    SELECT 8, 'Discount exceeds order amount',
           COUNT(*), COALESCE(GROUP_CONCAT(id, ','), '')
    FROM orders
    WHERE discount_amount > total_amount + shipping_fee

    UNION ALL
    SELECT 9, 'Active product with negative stock',
           COUNT(*), COALESCE(GROUP_CONCAT(id, ','), '')
    FROM products
    WHERE is_active = 1 AND stock_qty < 0

    UNION ALL
    SELECT 10, 'Coupon expired before start',
           COUNT(*), COALESCE(GROUP_CONCAT(id, ','), '')
    FROM coupons
    WHERE expired_at < started_at

    ORDER BY rule_no;
    ```
