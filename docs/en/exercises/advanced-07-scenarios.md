# Business Scenarios

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `categories` — Categories (parent-child hierarchy)  

    `customers` — Customers (grade, points, channel)  

    `complaints` — Complaints (type, priority)  

    `returns` — Returns (reason, status)  

    `shipping` — Shipping (carrier, tracking, status)  

    `reviews` — Reviews (rating, content)  

    `payments` — Payments (method, amount, status)  

    `suppliers` — Suppliers (company, contact)  

    `staff` — Staff (dept, role, manager)  



!!! abstract "Concepts"

    `CTE`, `Scalar Subquery`, `CASE`, `JULIANDAY`, `Business Reporting`



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


    **Result** (1 rows)

    | orders | revenue | avg_order | new_customers | wow_growth_pct |
    |---|---|---|---|---|
    | 108 | 92,193,999.00 | 853,648.00 | 15 | -13.00 |


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


    **Result** (top 7 of 20 rows)

    | name | category | revenue | units_sold | avg_rating | reviews | returns | alert |
    |---|---|---|---|---|---|---|---|
    | Razer Blade 18 Black | Gaming Laptop | 169,770,900.00 | 39 | 4.10 | 20 | 23 | High Returns |
    | Razer Blade 16 Silver | Gaming Laptop | 137,007,300.00 | 37 | 3.95 | 19 | 13 | High Returns |
    | MacBook Air 15 M3 Silver | MacBook | 131,546,400.00 | 24 | 3.75 | 4 | 2 |  |
    | ASUS Dual RTX 4060 Ti Black | NVIDIA | 117,691,200.00 | 44 | 3.75 | 16 | 16 | High Returns |
    | ASUS Dual RTX 5070 Ti Silver | NVIDIA | 109,490,400.00 | 111 | 3.65 | 23 | 8 | High Returns |
    | ASUS ROG Swift PG32UCDM Silver | Gaming Monitor | 96,405,300.00 | 51 | 3.67 | 24 | 10 | High Returns |
    | Razer Blade 18 Black | Gaming Laptop | 95,600,000.00 | 32 | 3.92 | 25 | 10 | High Returns |


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


    **Result** (top 7 of 827 rows)

    | name | email | grade | last_order | order_count | total_spent | days_inactive |
    |---|---|---|---|---|---|---|
    | Terri Jones | user33@testmail.kr | VIP | 2025-06-05 17:58:17 | 172 | 174,223,341.00 | 208 |
    | Jenna Thompson | user359@testmail.kr | SILVER | 2025-03-16 15:13:13 | 89 | 99,843,125.00 | 289 |
    | Katie Warner | user551@testmail.kr | BRONZE | 2025-06-01 14:44:44 | 71 | 99,783,432.00 | 212 |
    | Sarah Mendoza | user844@testmail.kr | VIP | 2025-05-28 19:15:41 | 46 | 79,718,969.00 | 216 |
    | Jordan Trujillo | user553@testmail.kr | GOLD | 2025-03-22 19:11:40 | 78 | 77,049,170.00 | 283 |
    | Kevin Sanders | user903@testmail.kr | GOLD | 2025-04-13 09:52:14 | 67 | 75,881,651.00 | 261 |
    | Robert Turner | user70@testmail.kr | BRONZE | 2024-10-26 22:15:57 | 97 | 70,981,337.00 | 430 |


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


    **Result** (6 rows)

    | method | paid_count | paid_amount | refund_count | refund_amount | net_revenue |
    |---|---|---|---|---|---|
    | card | 182 | 153,966,200.00 | 10 | 12,925,184.00 | 141,041,016.00 |
    | kakao_pay | 91 | 89,478,577.00 | 8 | 8,251,931.00 | 81,226,646.00 |
    | naver_pay | 76 | 60,848,112.00 | 4 | 2,169,400.00 | 58,678,712.00 |
    | bank_transfer | 51 | 56,388,551.00 | 1 | 253,200.00 | 56,135,351.00 |
    | point | 23 | 28,788,195.00 | 1 | 555,500.00 | 28,232,695.00 |
    | virtual_account | 36 | 27,679,127.00 | 3 | 5,461,600.00 | 22,217,527.00 |


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


    **Result** (5 rows)

    | carrier | delayed_count | avg_days | max_days |
    |---|---|---|---|
    | FedEx | 5322 | 3.50 | 4 |
    | UPS | 4505 | 3.50 | 4 |
    | USPS | 3573 | 3.50 | 4 |
    | DHL | 2743 | 3.50 | 4 |
    | OnTrac | 1783 | 3.50 | 4 |


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


    **Result** (1 rows)

    | name | sku | stock_qty | avg_daily_sales | days_of_stock | supplier | contact_name | supplier_phone |
    |---|---|---|---|---|---|---|---|
    | Arctic Freezer 36 A-RGB White | CO-AIR-ARC-00049 | 0 | 0.2 | 0 | Arctic Corp. | Valerie Lozano | 555-2200-4333 |


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


    **Result** (top 7 of 98 rows)

    | name | grade | email | title | category | priority | created_at | days_open | total_spent |
    |---|---|---|---|---|---|---|---|---|
    | Thomas Moran | VIP | user614@testmail.kr | When will the refund be processed? | refund_request | urgent | 2020-01-10 11:19:37 | 2181 | 148,203,887.00 |
    | Angel Lewis | VIP | user388@testmail.kr | Requesting a refund | refund_request | urgent | 2020-08-22 12:41:19 | 1956 | 133,207,783.00 |
    | Scott Holt | VIP | user1420@testmail.kr | Wrong color shipped | wrong_item | urgent | 2024-07-11 05:53:51 | 537 | 124,382,602.00 |
    | Emily Mack | VIP | user1097@testmail.kr | Different item was delivered | wrong_item | urgent | 2020-12-15 06:41:56 | 1841 | 85,987,658.00 |
    | Yvonne Fisher | VIP | user1522@testmail.kr | Delivery delay inquiry | delivery_issue | urgent | 2021-04-23 22:21:29 | 1712 | 51,532,028.00 |
    | Stephanie Harris | GOLD | user875@testmail.kr | When will the refund be processed? | refund_request | urgent | 2020-03-04 11:54:29 | 2127 | 49,812,024.00 |
    | Christopher George | VIP | user2227@testmail.kr | Delivered to wrong address | delivery_issue | urgent | 2024-03-17 16:26:20 | 653 | 46,684,135.00 |


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


    **Result** (1 rows)

    | revenue | orders | new_customers | active_customers | avg_order_value | cancel_rate | return_rate |
    |---|---|---|---|---|---|---|
    | 5,346,776,711.00 | 5474 | 700 | 1692 | 976,759.00 | 5.40 | 2.70 |


---
