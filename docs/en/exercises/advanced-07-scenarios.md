# Business Scenarios

#### :material-database: Tables


`orders` — Orders (status, amount, date)<br>

`order_items` — Order items (qty, unit price)<br>

`products` — Products (name, price, stock, brand)<br>

`categories` — Categories (parent-child hierarchy)<br>

`customers` — Customers (grade, points, channel)<br>

`complaints` — Complaints (type, priority)<br>

`returns` — Returns (reason, status)<br>

`shipping` — Shipping (carrier, tracking, status)<br>

`reviews` — Reviews (rating, content)<br>

`payments` — Payments (method, amount, status)<br>

`suppliers` — Suppliers (company, contact)<br>

`staff` — Staff (dept, role, manager)<br>



**:material-book-open-variant: Concepts:** `CTE`, `Scalar Subquery`, `CASE`, `JULIANDAY`, `Business Reporting`


---


### 1. Scenario 1: CEO Weekly Report


Role: Data analyst. The CEO needs a weekly summary for Monday morning meeting.
For last week (2024-12-16 to 2024-12-22): order count, revenue, avg order value,
new signups, and week-over-week revenue growth.


**Hint 1:** Calculate this week / last week / new customers as separate CTEs,
then combine with `FROM this_week, last_week, new_customers`.



??? success "Answer"
    ```sql
    WITH this_week AS (
        SELECT
            COUNT(*) AS orders,
            ROUND(SUM(total_amount), 0) AS revenue,
            ROUND(AVG(total_amount), 0) AS avg_order
        FROM orders
        WHERE ordered_at BETWEEN '2024-12-16' AND '2024-12-22 23:59:59'
          AND status NOT IN ('cancelled')
    ),
    last_week AS (
        SELECT ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at BETWEEN '2024-12-09' AND '2024-12-15 23:59:59'
          AND status NOT IN ('cancelled')
    ),
    new_customers AS (
        SELECT COUNT(*) AS signups
        FROM customers
        WHERE created_at BETWEEN '2024-12-16' AND '2024-12-22 23:59:59'
    )
    SELECT
        tw.orders,
        tw.revenue,
        tw.avg_order,
        nc.signups AS new_customers,
        ROUND(100.0 * (tw.revenue - lw.revenue) / NULLIF(lw.revenue, 0), 1) AS wow_growth_pct
    FROM this_week tw, last_week lw, new_customers nc;
    ```


---


### 2. Scenario 2: MD Team Product Review


Role: MD (merchandising) team member.
For top 20 products by 2024 revenue: name, category, revenue, units sold,
avg rating, return count. Include alert flags for low ratings/high returns.


**Hint 1:** Extract top 20 by revenue in a CTE, then LEFT JOIN `reviews` and `returns`.
Add alert flags with `CASE`.



??? success "Answer"
    ```sql
    WITH top_products AS (
        SELECT
            p.id, p.name, cat.name AS category,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        INNER JOIN products p ON oi.product_id = p.id
        INNER JOIN categories cat ON p.category_id = cat.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled')
        GROUP BY p.id, p.name, cat.name
        ORDER BY revenue DESC
        LIMIT 20
    ),
    product_reviews AS (
        SELECT product_id, ROUND(AVG(rating), 2) AS avg_rating, COUNT(*) AS review_count
        FROM reviews GROUP BY product_id
    ),
    product_returns AS (
        SELECT oi.product_id, COUNT(DISTINCT r.id) AS return_count
        FROM returns r
        INNER JOIN order_items oi ON r.order_id = oi.order_id
        GROUP BY oi.product_id
    )
    SELECT
        tp.name, tp.category, tp.revenue, tp.units_sold,
        COALESCE(pr.avg_rating, 0) AS avg_rating,
        COALESCE(pr.review_count, 0) AS reviews,
        COALESCE(ret.return_count, 0) AS returns,
        CASE
            WHEN pr.avg_rating < 3.5 THEN 'Low Rating'
            WHEN ret.return_count > 5 THEN 'High Returns'
            ELSE ''
        END AS alert
    FROM top_products tp
    LEFT JOIN product_reviews pr ON tp.id = pr.product_id
    LEFT JOIN product_returns ret ON tp.id = ret.product_id
    ORDER BY tp.revenue DESC;
    ```


---


### 3. Scenario 3: Marketing Campaign Targets


Role: Marketing team. Prepare a reactivation email campaign.
Find customers with 3+ past purchases but no orders in the last 6 months.


**Hint 1:** `HAVING COUNT(*) >= 3 AND MAX(ordered_at) < DATE('reference_date', '-6 months')`



??? success "Answer"
    ```sql
    SELECT
        c.name, c.email, c.grade,
        MAX(o.ordered_at) AS last_order,
        COUNT(*) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent,
        CAST(JULIANDAY('2025-12-31') - JULIANDAY(MAX(o.ordered_at)) AS INTEGER) AS days_inactive
    FROM customers c
    INNER JOIN orders o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
      AND c.is_active = 1
    GROUP BY c.id, c.name, c.email, c.grade
    HAVING COUNT(*) >= 3
       AND MAX(o.ordered_at) < DATE('2025-12-31', '-6 months')
    ORDER BY total_spent DESC;
    ```


---


### 4. Scenario 4: Finance Month-End Close


Role: Finance team. Prepare December 2024 month-end close report.
Show paid count, paid amount, refund count, refund amount, and net revenue by payment method.


**Hint 1:** Use conditional aggregation in `payments`:
`SUM(CASE WHEN status = 'completed' ...)` and `SUM(CASE WHEN status = 'refunded' ...)`.



??? success "Answer"
    ```sql
    SELECT
        method,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS paid_count,
        ROUND(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) AS paid_amount,
        SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) AS refund_count,
        ROUND(SUM(CASE WHEN status = 'refunded' THEN amount ELSE 0 END), 0) AS refund_amount,
        ROUND(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END)
            - SUM(CASE WHEN status = 'refunded' THEN amount ELSE 0 END), 0) AS net_revenue
    FROM payments
    WHERE created_at LIKE '2024-12%'
    GROUP BY method
    ORDER BY net_revenue DESC;
    ```


---


### 5. Scenario 5: Logistics Shipping Delay Report


Role: Logistics team.
Aggregate deliveries taking 3+ days after shipping, grouped by carrier.


**Hint 1:** Calculate delivery days with `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)`,
filter `>= 3` for delayed deliveries.



??? success "Answer"
    ```sql
    SELECT
        sh.carrier,
        COUNT(*) AS delayed_count,
        ROUND(AVG(JULIANDAY(sh.delivered_at) - JULIANDAY(sh.shipped_at)), 1) AS avg_days,
        MAX(CAST(JULIANDAY(sh.delivered_at) - JULIANDAY(sh.shipped_at) AS INTEGER)) AS max_days
    FROM shipping sh
    WHERE sh.delivered_at IS NOT NULL
      AND sh.shipped_at IS NOT NULL
      AND JULIANDAY(sh.delivered_at) - JULIANDAY(sh.shipped_at) >= 3
    GROUP BY sh.carrier
    ORDER BY delayed_count DESC;
    ```


---


### 6. Scenario 6: Procurement Reorder Suggestion


Role: Procurement team.
List products with less than 14 days of stock based on 30-day average daily sales.
Include supplier contact info.


**Hint 1:** Calculate 30-day avg daily sales in a CTE,
filter `stock_qty / avg_daily_sales < 14`.



??? success "Answer"
    ```sql
    WITH daily_sales AS (
        SELECT
            oi.product_id,
            ROUND(1.0 * SUM(oi.quantity) / 30, 2) AS avg_daily_sales
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('2025-12-31', '-30 days')
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    )
    SELECT
        p.name, p.sku, p.stock_qty,
        ds.avg_daily_sales,
        CASE
            WHEN ds.avg_daily_sales > 0
            THEN CAST(p.stock_qty / ds.avg_daily_sales AS INTEGER)
            ELSE 9999
        END AS days_of_stock,
        s.company_name AS supplier,
        s.contact_name, s.phone AS supplier_phone
    FROM products p
    INNER JOIN daily_sales ds ON p.id = ds.product_id
    INNER JOIN suppliers s ON p.supplier_id = s.id
    WHERE p.is_active = 1
      AND ds.avg_daily_sales > 0
      AND p.stock_qty / ds.avg_daily_sales < 14
    ORDER BY days_of_stock ASC;
    ```


---


### 7. Scenario 7: CS Team Escalation


Role: CS team lead.
Show 7+ day unresolved complaints from VIP/GOLD customers with priority ranking.


**Hint 1:** JOIN `complaints` with `customers`, filter `status = 'open'`
and `grade IN ('VIP', 'GOLD')`.



??? success "Answer"
    ```sql
    SELECT
        c.name, c.grade, c.email,
        comp.title, comp.category, comp.priority,
        comp.created_at,
        CAST(JULIANDAY('2025-12-31') - JULIANDAY(comp.created_at) AS INTEGER) AS days_open,
        COALESCE(cv.total_spent, 0) AS total_spent
    FROM complaints comp
    INNER JOIN customers c ON comp.customer_id = c.id
    LEFT JOIN (
        SELECT customer_id, ROUND(SUM(total_amount), 0) AS total_spent
        FROM orders WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ) cv ON c.id = cv.customer_id
    WHERE comp.status = 'open'
      AND c.grade IN ('VIP', 'GOLD')
      AND JULIANDAY('2025-12-31') - JULIANDAY(comp.created_at) >= 7
    ORDER BY
        CASE comp.priority
            WHEN 'urgent' THEN 1 WHEN 'high' THEN 2
            WHEN 'medium' THEN 3 ELSE 4
        END,
        cv.total_spent DESC;
    ```


---


### 8. Scenario 8: Annual KPI Dashboard


Role: Data analyst. Prepare annual KPI for year-end executive meeting.
Summarize 2024 in one row: total revenue, orders, new customers,
active customers, avg order value, cancellation rate, return rate.


**Hint 1:** List each KPI as a scalar subquery `(SELECT ... FROM ...)` in the SELECT clause
to output a single row.



??? success "Answer"
    ```sql
    SELECT
        (SELECT ROUND(SUM(total_amount), 0) FROM orders
         WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')) AS revenue,
        (SELECT COUNT(*) FROM orders
         WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')) AS orders,
        (SELECT COUNT(*) FROM customers
         WHERE created_at LIKE '2024%') AS new_customers,
        (SELECT COUNT(DISTINCT customer_id) FROM orders
         WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')) AS active_customers,
        (SELECT ROUND(AVG(total_amount), 0) FROM orders
         WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')) AS avg_order_value,
        (SELECT ROUND(100.0 * SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1)
         FROM orders WHERE ordered_at LIKE '2024%') AS cancel_rate,
        (SELECT ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders WHERE ordered_at LIKE '2024%'), 1)
         FROM returns WHERE requested_at LIKE '2024%') AS return_rate;
    ```


---
