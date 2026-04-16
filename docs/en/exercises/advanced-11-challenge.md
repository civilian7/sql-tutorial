# Challenge Problems

#### :material-database: Tables


`categories` — Categories (parent-child hierarchy)<br>

`customers` — Customers (grade, points, channel)<br>

`orders` — Orders (status, amount, date)<br>

`order_items` — Order items (qty, unit price)<br>

`products` — Products (name, price, stock, brand)<br>

`reviews` — Reviews (rating, content)<br>

`shipping` — Shipping (carrier, tracking, status)<br>

`point_transactions` — Points (earn, use, expire)<br>

`product_views` — View log (customer, product, date)<br>

`inventory_transactions` — Inventory (type, quantity)<br>

`wishlists` — Wishlists (customer-product)<br>

`calendar` — Calendar (weekday, holiday)<br>



**:material-book-open-variant: Concepts:** `Window`, `Analytics`, `CTE`, `consecutive`, `median`, `retention`


---


### 1. Duplicate Review Detection


Find customers who reviewed the same product more than once.
Show customer name, product name, and review count.


**Hint 1:** - JOIN `reviews` with `customers` and `products`
- `GROUP BY customer_id, product_id` then `HAVING COUNT(*) >= 2`



??? success "Answer"
    ```sql
    SELECT
        c.name AS customer_name,
        p.name AS product_name,
        COUNT(*) AS review_count
    FROM reviews AS r
    INNER JOIN customers AS c ON r.customer_id = c.id
    INNER JOIN products AS p ON r.product_id = p.id
    GROUP BY r.customer_id, r.product_id, c.name, p.name
    HAVING COUNT(*) >= 2
    ORDER BY review_count DESC;
    ```


---


### 2. Weekday vs Weekend Average Order Amount


Using the calendar table, compare average order amounts on weekdays vs weekends.
Show weekday/weekend label, order count, average order value, and total revenue.


**Hint 1:** - Use `calendar.is_weekend` column
- JOIN `orders` with `calendar` on date



??? success "Answer"
    ```sql
    SELECT
        CASE cal.is_weekend
            WHEN 1 THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type,
        COUNT(*) AS order_count,
        ROUND(AVG(o.total_amount), 2) AS avg_order_value,
        ROUND(SUM(o.total_amount), 2) AS total_revenue
    FROM orders AS o
    INNER JOIN calendar AS cal
        ON SUBSTR(o.ordered_at, 1, 10) = cal.date_key
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY cal.is_weekend
    ORDER BY cal.is_weekend;
    ```


---


### 3. Daily Order Count vs Previous Day


Calculate daily order counts for December 2024.
Use LAG to show only days where the count increased vs the previous day.


**Hint 1:** - Extract date with `SUBSTR(ordered_at, 1, 10)`
- Use `LAG(order_count) OVER (ORDER BY order_date)` for previous day



??? success "Answer"
    ```sql
    WITH daily AS (
        SELECT
            SUBSTR(ordered_at, 1, 10) AS order_date,
            COUNT(*) AS order_count
        FROM orders
        WHERE ordered_at LIKE '2024-12%'
          AND status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 10)
    ),
    with_prev AS (
        SELECT
            order_date,
            order_count,
            LAG(order_count) OVER (ORDER BY order_date) AS prev_count
        FROM daily
    )
    SELECT
        order_date,
        order_count,
        prev_count,
        order_count - prev_count AS diff
    FROM with_prev
    WHERE order_count > prev_count
    ORDER BY order_date;
    ```


---


### 4. 3rd Most Expensive Product per Category


Find the 3rd most expensive product in each category.
Show category name, product name, price, and rank.


**Hint 1:** - `ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY price DESC)`
- Filter `WHERE rn = 3`



??? success "Answer"
    ```sql
    WITH ranked AS (
        SELECT
            cat.name AS category,
            p.name AS product_name,
            p.price,
            ROW_NUMBER() OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
            ) AS rn
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
    )
    SELECT category, product_name, price, rn AS rank
    FROM ranked
    WHERE rn = 3
    ORDER BY price DESC;
    ```


---


### 5. A/B Bucket Split


Split customers into A/B groups using MOD(id, 2).
Compare customer count, average order value, and average order count per group.


**Hint 1:** - `CASE WHEN c.id % 2 = 0 THEN 'A' ELSE 'B' END`
- JOIN `customers` with `orders`, aggregate by group



??? success "Answer"
    ```sql
    SELECT
        CASE WHEN c.id % 2 = 0 THEN 'A' ELSE 'B' END AS bucket,
        COUNT(DISTINCT c.id) AS customer_count,
        COUNT(o.id) AS total_orders,
        ROUND(AVG(o.total_amount), 2) AS avg_order_value,
        ROUND(1.0 * COUNT(o.id) / COUNT(DISTINCT c.id), 1) AS avg_orders_per_customer
    FROM customers AS c
    LEFT JOIN orders AS o
        ON c.id = o.customer_id
       AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY CASE WHEN c.id % 2 = 0 THEN 'A' ELSE 'B' END
    ORDER BY bucket;
    ```


---


### 6. Tree Node Type Classification


Classify each category as root / inner / leaf.
Root: parent_id IS NULL. Inner: non-root with children. Leaf: no children.


**Hint 1:** - `LEFT JOIN categories AS child ON cat.id = child.parent_id`
- Use `CASE` based on parent_id and child existence



??? success "Answer"
    ```sql
    SELECT
        cat.id,
        cat.name,
        cat.parent_id,
        cat.depth,
        CASE
            WHEN cat.parent_id IS NULL THEN 'root'
            WHEN EXISTS (SELECT 1 FROM categories c2 WHERE c2.parent_id = cat.id) THEN 'inner'
            ELSE 'leaf'
        END AS node_type
    FROM categories AS cat
    ORDER BY cat.depth, cat.sort_order;
    ```


---


### 7. Daily Order Cancellation Rate (Last 30 Days)


For the last 30 days (based on 2025-12-01 to 2025-12-31),
calculate daily total orders, cancelled orders, and cancellation rate.


**Hint 1:** - Calculate ratio of `status = 'cancelled'` orders
- `SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END)`



??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 10) AS order_date,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        ROUND(100.0 * SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END)
            / COUNT(*), 2) AS cancel_rate_pct
    FROM orders
    WHERE ordered_at BETWEEN '2025-12-01' AND '2025-12-31 23:59:59'
    GROUP BY SUBSTR(ordered_at, 1, 10)
    ORDER BY order_date;
    ```


---


### 8. Installment Amount Calculation


For orders over 500,000 KRW, calculate monthly installment amounts
for 3, 6, and 12 months. Show order number, total, and monthly amounts.


**Hint 1:** - Simple division: `ROUND(total_amount / 3, 0)` etc.
- `WHERE total_amount >= 500000`



??? success "Answer"
    ```sql
    SELECT
        order_number,
        total_amount,
        ROUND(total_amount / 3, 0) AS monthly_3m,
        ROUND(total_amount / 6, 0) AS monthly_6m,
        ROUND(total_amount / 12, 0) AS monthly_12m
    FROM orders
    WHERE total_amount >= 500000
      AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY total_amount DESC
    LIMIT 20;
    ```


---


### 9. Estimate NULL Birth Dates


For customers with NULL birth_date, estimate their birth year
using the average birth year of customers in the same grade.
Show name, grade, original birth_date, and estimated birth_year.


**Hint 1:** - `AVG(CAST(SUBSTR(birth_date, 1, 4) AS INTEGER))` for average birth year by grade
- Apply to NULL customers via `LEFT JOIN` or scalar subquery



??? success "Answer"
    ```sql
    WITH grade_avg_year AS (
        SELECT
            grade,
            ROUND(AVG(CAST(SUBSTR(birth_date, 1, 4) AS INTEGER)), 0) AS avg_birth_year
        FROM customers
        WHERE birth_date IS NOT NULL
        GROUP BY grade
    )
    SELECT
        c.id,
        c.name,
        c.grade,
        c.birth_date,
        gay.avg_birth_year AS estimated_birth_year
    FROM customers AS c
    INNER JOIN grade_avg_year AS gay ON c.grade = gay.grade
    WHERE c.birth_date IS NULL
    ORDER BY c.grade, c.id
    LIMIT 20;
    ```


---


### 10. Find Duplicate Wishlists


Although wishlists has a UNIQUE constraint,
write SQL to identify duplicates (same customer_id + product_id)
and mark all but the earliest using ROW_NUMBER.


**Hint 1:** - `ROW_NUMBER() OVER (PARTITION BY customer_id, product_id ORDER BY created_at)`
- `rn > 1` marks records to delete



??? success "Answer"
    ```sql
    WITH ranked AS (
        SELECT
            id,
            customer_id,
            product_id,
            created_at,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id, product_id
                ORDER BY created_at ASC
            ) AS rn
        FROM wishlists
    )
    SELECT id, customer_id, product_id, created_at, rn,
           CASE WHEN rn > 1 THEN 'DELETE' ELSE 'KEEP' END AS action
    FROM ranked
    WHERE customer_id IN (
        SELECT customer_id FROM wishlists
        GROUP BY customer_id
        HAVING COUNT(*) > 1
    )
    ORDER BY customer_id, product_id, rn
    LIMIT 30;
    ```


---


### 11. Signup-to-Order Conversion Rate by Channel


Calculate signup count, first-order count, and conversion rate
by acquisition_channel.


**Hint 1:** - Group by `customers.acquisition_channel`
- Customer is converted if they have at least 1 order



??? success "Answer"
    ```sql
    SELECT
        COALESCE(c.acquisition_channel, 'unknown') AS channel,
        COUNT(*) AS signup_count,
        COUNT(DISTINCT o.customer_id) AS converted_count,
        ROUND(100.0 * COUNT(DISTINCT o.customer_id) / COUNT(*), 1) AS conversion_rate_pct
    FROM customers AS c
    LEFT JOIN orders AS o
        ON c.id = o.customer_id
       AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY COALESCE(c.acquisition_channel, 'unknown')
    ORDER BY conversion_rate_pct DESC;
    ```


---


### 12. Flow vs Stock Comparison


Compare inventory flow (sum of inbound - outbound from transactions)
with current stock (products.stock_qty) per product.
Identify products where they differ.


**Hint 1:** - `SUM(quantity)` from `inventory_transactions` (positive=inbound, negative=outbound)
- Compare with `products.stock_qty`



??? success "Answer"
    ```sql
    WITH flow AS (
        SELECT
            product_id,
            SUM(quantity) AS net_flow
        FROM inventory_transactions
        GROUP BY product_id
    )
    SELECT
        p.name AS product_name,
        p.stock_qty AS current_stock,
        f.net_flow AS calculated_stock,
        p.stock_qty - f.net_flow AS discrepancy
    FROM products AS p
    INNER JOIN flow AS f ON p.id = f.product_id
    WHERE p.stock_qty != f.net_flow
    ORDER BY ABS(p.stock_qty - f.net_flow) DESC
    LIMIT 20;
    ```


---


### 13. Consecutive Same-Status Orders


Find customers with 3+ consecutive orders having the same status.
Use LAG to compare with the previous 2 orders' status.


**Hint 1:** - Use `LAG(status, 1)` and `LAG(status, 2)`
- Show rows where all 3 have the same status



??? success "Answer"
    ```sql
    WITH order_seq AS (
        SELECT
            customer_id,
            order_number,
            status,
            ordered_at,
            LAG(status, 1) OVER (PARTITION BY customer_id ORDER BY ordered_at) AS prev_1,
            LAG(status, 2) OVER (PARTITION BY customer_id ORDER BY ordered_at) AS prev_2
        FROM orders
    )
    SELECT
        os.customer_id,
        c.name AS customer_name,
        os.order_number,
        os.status,
        os.prev_1,
        os.prev_2,
        os.ordered_at
    FROM order_seq AS os
    INNER JOIN customers AS c ON os.customer_id = c.id
    WHERE os.status = os.prev_1
      AND os.status = os.prev_2
    ORDER BY os.customer_id, os.ordered_at
    LIMIT 30;
    ```


---


### 14. Top 3 Products by Revenue per Category


Use ROW_NUMBER to find the top 3 products by revenue per category.
Show category, rank, product name, and revenue.


**Hint 1:** - `ROW_NUMBER() OVER (PARTITION BY cat.id ORDER BY revenue DESC)`
- `WHERE rn <= 3`



??? success "Answer"
    ```sql
    WITH product_revenue AS (
        SELECT
            cat.name AS category,
            cat.id AS category_id,
            p.name AS product_name,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
            ROW_NUMBER() OVER (
                PARTITION BY cat.id
                ORDER BY SUM(oi.quantity * oi.unit_price) DESC
            ) AS rn
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY cat.id, cat.name, p.id, p.name
    )
    SELECT category, rn AS rank, product_name, revenue
    FROM product_revenue
    WHERE rn <= 3
    ORDER BY category, rn;
    ```


---


### 15. Mentoring Pair Matching


Match junior staff (role='staff') with seniors (role='manager')
in the same department as mentor-mentee pairs.
Show department, mentee name, and mentor name.


**Hint 1:** - Self-join `staff`: `s1.department = s2.department`
- `s1.role = 'staff'` AND `s2.role = 'manager'`



??? success "Answer"
    ```sql
    SELECT
        s1.department,
        s1.name AS mentee,
        s1.role AS mentee_role,
        s2.name AS mentor,
        s2.role AS mentor_role
    FROM staff AS s1
    INNER JOIN staff AS s2
        ON s1.department = s2.department
       AND s2.role = 'manager'
    WHERE s1.role = 'staff'
      AND s1.is_active = 1
      AND s2.is_active = 1
    ORDER BY s1.department, s1.name;
    ```


---


### 16. Classic Retention Analysis


By signup month (cohort), calculate the percentage of customers
who ordered again in month+1, month+2, and month+3.


**Hint 1:** - Cohort = `SUBSTR(customers.created_at, 1, 7)`
- Calculate "months since signup" for each order
- Use `COUNT(DISTINCT CASE WHEN ... THEN customer_id END)`



??? success "Answer"

    === "SQLite"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
    ),
    cohort_orders AS (
        SELECT
            co.signup_month,
            co.customer_id,
            CAST(
                (CAST(SUBSTR(o.ordered_at, 1, 4) AS INTEGER) * 12
                 + CAST(SUBSTR(o.ordered_at, 6, 2) AS INTEGER))
              - (CAST(SUBSTR(co.created_at, 1, 4) AS INTEGER) * 12
                 + CAST(SUBSTR(co.created_at, 6, 2) AS INTEGER))
            AS INTEGER) AS months_since_signup
        FROM cohort AS co
        INNER JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        signup_month,
        COUNT(DISTINCT customer_id) AS cohort_size,
        COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END) AS m1,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m1_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END) AS m2,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m2_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END) AS m3,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m3_pct
    FROM cohort_orders
    GROUP BY signup_month
    ORDER BY signup_month;
        ```

    === "Oracle"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
    ),
    cohort_orders AS (
        SELECT
            co.signup_month,
            co.customer_id,
            (CAST(SUBSTR(o.ordered_at, 1, 4) AS NUMBER) * 12
             + CAST(SUBSTR(o.ordered_at, 6, 2) AS NUMBER))
          - (CAST(SUBSTR(co.created_at, 1, 4) AS NUMBER) * 12
             + CAST(SUBSTR(co.created_at, 6, 2) AS NUMBER)) AS months_since_signup
        FROM cohort co
        INNER JOIN orders o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        signup_month,
        COUNT(DISTINCT customer_id) AS cohort_size,
        COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END) AS m1,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m1_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END) AS m2,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m2_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END) AS m3,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m3_pct
    FROM cohort_orders
    GROUP BY signup_month
    ORDER BY signup_month;
        ```

    === "SQL Server"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            SUBSTRING(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
    ),
    cohort_orders AS (
        SELECT
            co.signup_month,
            co.customer_id,
            (CAST(SUBSTRING(o.ordered_at, 1, 4) AS INT) * 12
             + CAST(SUBSTRING(o.ordered_at, 6, 2) AS INT))
          - (CAST(SUBSTRING(co.created_at, 1, 4) AS INT) * 12
             + CAST(SUBSTRING(co.created_at, 6, 2) AS INT)) AS months_since_signup
        FROM cohort AS co
        INNER JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        signup_month,
        COUNT(DISTINCT customer_id) AS cohort_size,
        COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END) AS m1,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m1_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END) AS m2,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m2_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END) AS m3,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m3_pct
    FROM cohort_orders
    GROUP BY signup_month
    ORDER BY signup_month;
        ```


---


### 17. Rolling Retention Analysis


By signup month cohort, calculate the % of customers who ordered
in ANY month after N months (not just exactly month N).


**Hint 1:** - Use `months_since_signup >= N` for "any time after N months"
- Always >= classic retention values



??? success "Answer"

    === "SQLite"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
    ),
    cohort_orders AS (
        SELECT
            co.signup_month,
            co.customer_id,
            CAST(
                (CAST(SUBSTR(o.ordered_at, 1, 4) AS INTEGER) * 12
                 + CAST(SUBSTR(o.ordered_at, 6, 2) AS INTEGER))
              - (CAST(SUBSTR(co.created_at, 1, 4) AS INTEGER) * 12
                 + CAST(SUBSTR(co.created_at, 6, 2) AS INTEGER))
            AS INTEGER) AS months_since_signup
        FROM cohort AS co
        INNER JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        signup_month,
        COUNT(DISTINCT customer_id) AS cohort_size,
        COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END) AS rolling_m1,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS rolling_m1_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END) AS rolling_m2,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS rolling_m2_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END) AS rolling_m3,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS rolling_m3_pct
    FROM cohort_orders
    GROUP BY signup_month
    ORDER BY signup_month;
        ```

    === "Oracle"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
    ),
    cohort_orders AS (
        SELECT
            co.signup_month,
            co.customer_id,
            (CAST(SUBSTR(o.ordered_at, 1, 4) AS NUMBER) * 12
             + CAST(SUBSTR(o.ordered_at, 6, 2) AS NUMBER))
          - (CAST(SUBSTR(co.created_at, 1, 4) AS NUMBER) * 12
             + CAST(SUBSTR(co.created_at, 6, 2) AS NUMBER)) AS months_since_signup
        FROM cohort co
        INNER JOIN orders o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        signup_month,
        COUNT(DISTINCT customer_id) AS cohort_size,
        COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END) AS rolling_m1,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS rolling_m1_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END) AS rolling_m2,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS rolling_m2_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END) AS rolling_m3,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS rolling_m3_pct
    FROM cohort_orders
    GROUP BY signup_month
    ORDER BY signup_month;
        ```

    === "SQL Server"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            SUBSTRING(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
    ),
    cohort_orders AS (
        SELECT
            co.signup_month,
            co.customer_id,
            (CAST(SUBSTRING(o.ordered_at, 1, 4) AS INT) * 12
             + CAST(SUBSTRING(o.ordered_at, 6, 2) AS INT))
          - (CAST(SUBSTRING(co.created_at, 1, 4) AS INT) * 12
             + CAST(SUBSTRING(co.created_at, 6, 2) AS INT)) AS months_since_signup
        FROM cohort AS co
        INNER JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        signup_month,
        COUNT(DISTINCT customer_id) AS cohort_size,
        COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END) AS rolling_m1,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS rolling_m1_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END) AS rolling_m2,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS rolling_m2_pct,
        COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END) AS rolling_m3,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS rolling_m3_pct
    FROM cohort_orders
    GROUP BY signup_month
    ORDER BY signup_month;
        ```


---


### 18. DAU/MAU Stickiness Ratio


For December 2024, calculate daily active users (DAU) and monthly active users (MAU)
from product_views. DAU/MAU ratio is the stickiness metric.


**Hint 1:** - DAU = daily `COUNT(DISTINCT customer_id)`
- MAU = monthly `COUNT(DISTINCT customer_id)` (subquery)
- Stickiness = DAU / MAU



??? success "Answer"
    ```sql
    WITH dau AS (
        SELECT
            SUBSTR(viewed_at, 1, 10) AS view_date,
            COUNT(DISTINCT customer_id) AS daily_active
        FROM product_views
        WHERE viewed_at LIKE '2024-12%'
        GROUP BY SUBSTR(viewed_at, 1, 10)
    ),
    mau AS (
        SELECT COUNT(DISTINCT customer_id) AS monthly_active
        FROM product_views
        WHERE viewed_at LIKE '2024-12%'
    )
    SELECT
        d.view_date,
        d.daily_active AS dau,
        m.monthly_active AS mau,
        ROUND(100.0 * d.daily_active / m.monthly_active, 2) AS stickiness_pct
    FROM dau AS d
    CROSS JOIN mau AS m
    ORDER BY d.view_date;
    ```


---


### 19. 7-Day Moving Average Revenue


Calculate daily revenue and 7-day moving average for December 2024.
Use `AVG() OVER (ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`.


**Hint 1:** - Aggregate daily revenue first
- `AVG(daily_revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`



??? success "Answer"
    ```sql
    WITH daily_revenue AS (
        SELECT
            SUBSTR(ordered_at, 1, 10) AS order_date,
            ROUND(SUM(total_amount), 2) AS revenue
        FROM orders
        WHERE ordered_at LIKE '2024-12%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 10)
    )
    SELECT
        order_date,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2) AS moving_avg_7d
    FROM daily_revenue
    ORDER BY order_date;
    ```


---


### 20. 3-Month Moving Average Monthly Revenue


Calculate monthly revenue with a 3-month moving average.
Use the last 24 months of data.


**Hint 1:** - `AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`



??? success "Answer"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2024-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 0) AS moving_avg_3m
    FROM monthly
    ORDER BY year_month;
    ```


---


### 21. Cumulative Monthly Revenue Within Year


Calculate monthly revenue and cumulative revenue within each year.
Use PARTITION BY year so cumulative resets each year.


**Hint 1:** - `SUM(revenue) OVER (PARTITION BY year ORDER BY month)`



??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        SUBSTR(ordered_at, 1, 7) AS year_month,
        ROUND(SUM(total_amount), 0) AS monthly_revenue,
        ROUND(SUM(SUM(total_amount)) OVER (
            PARTITION BY SUBSTR(ordered_at, 1, 4)
            ORDER BY SUBSTR(ordered_at, 1, 7)
        ), 0) AS cumulative_revenue
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
      AND ordered_at >= '2023-01-01'
    GROUP BY SUBSTR(ordered_at, 1, 4), SUBSTR(ordered_at, 1, 7)
    ORDER BY year_month;
    ```


---


### 22. Pareto Analysis (Customers)


Analyze what percentage of customers generate 80% of revenue.
Show cumulative revenue percentage and customer rank.


**Hint 1:** - Sort customer revenue descending, calculate cumulative SUM
- Calculate cumulative % of total revenue
- Find customer count at 80% threshold / total customers



??? success "Answer"
    ```sql
    WITH customer_revenue AS (
        SELECT
            customer_id,
            ROUND(SUM(total_amount), 2) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    ranked AS (
        SELECT
            customer_id,
            revenue,
            SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative_revenue,
            SUM(revenue) OVER () AS total_revenue,
            ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rank,
            COUNT(*) OVER () AS total_customers
        FROM customer_revenue
    )
    SELECT
        rank,
        revenue,
        ROUND(100.0 * cumulative_revenue / total_revenue, 2) AS cumulative_pct,
        ROUND(100.0 * rank / total_customers, 2) AS customer_pct,
        CASE
            WHEN 100.0 * cumulative_revenue / total_revenue <= 80 THEN 'Top 80%'
            ELSE 'Remaining'
        END AS pareto_group
    FROM ranked
    WHERE rank <= 50 OR 100.0 * cumulative_revenue / total_revenue BETWEEN 78 AND 82
    ORDER BY rank;
    ```


---


### 23. Purchase Cycle Analysis


Calculate the average days between consecutive orders per customer.
Use LAG to get previous order date and compute JULIANDAY difference.


**Hint 1:** - `LAG(ordered_at) OVER (PARTITION BY customer_id ORDER BY ordered_at)`
- `JULIANDAY(ordered_at) - JULIANDAY(prev_ordered_at)`
- `AVG()` for average cycle per customer



??? success "Answer"

    === "SQLite"
        ```sql
        WITH order_gaps AS (
        SELECT
            customer_id,
            ordered_at,
            LAG(ordered_at) OVER (
                PARTITION BY customer_id ORDER BY ordered_at
            ) AS prev_ordered_at
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        c.name AS customer_name,
        c.grade,
        COUNT(*) AS gap_count,
        ROUND(AVG(JULIANDAY(og.ordered_at) - JULIANDAY(og.prev_ordered_at)), 1) AS avg_cycle_days,
        MIN(CAST(JULIANDAY(og.ordered_at) - JULIANDAY(og.prev_ordered_at) AS INTEGER)) AS min_days,
        MAX(CAST(JULIANDAY(og.ordered_at) - JULIANDAY(og.prev_ordered_at) AS INTEGER)) AS max_days
    FROM order_gaps AS og
    INNER JOIN customers AS c ON og.customer_id = c.id
    WHERE og.prev_ordered_at IS NOT NULL
    GROUP BY og.customer_id, c.name, c.grade
    HAVING COUNT(*) >= 3
    ORDER BY avg_cycle_days ASC
    LIMIT 20;
        ```

    === "Oracle"
        ```sql
        WITH order_gaps AS (
        SELECT
            customer_id,
            ordered_at,
            LAG(ordered_at) OVER (
                PARTITION BY customer_id ORDER BY ordered_at
            ) AS prev_ordered_at
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        c.name AS customer_name,
        c.grade,
        COUNT(*) AS gap_count,
        ROUND(AVG(CAST(og.ordered_at AS DATE) - CAST(og.prev_ordered_at AS DATE)), 1) AS avg_cycle_days,
        MIN(CAST(og.ordered_at AS DATE) - CAST(og.prev_ordered_at AS DATE)) AS min_days,
        MAX(CAST(og.ordered_at AS DATE) - CAST(og.prev_ordered_at AS DATE)) AS max_days
    FROM order_gaps og
    INNER JOIN customers c ON og.customer_id = c.id
    WHERE og.prev_ordered_at IS NOT NULL
    GROUP BY og.customer_id, c.name, c.grade
    HAVING COUNT(*) >= 3
    ORDER BY avg_cycle_days ASC
    FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        WITH order_gaps AS (
        SELECT
            customer_id,
            ordered_at,
            LAG(ordered_at) OVER (
                PARTITION BY customer_id ORDER BY ordered_at
            ) AS prev_ordered_at
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT TOP 20
        c.name AS customer_name,
        c.grade,
        COUNT(*) AS gap_count,
        ROUND(AVG(CAST(DATEDIFF(DAY, og.prev_ordered_at, og.ordered_at) AS FLOAT)), 1) AS avg_cycle_days,
        MIN(DATEDIFF(DAY, og.prev_ordered_at, og.ordered_at)) AS min_days,
        MAX(DATEDIFF(DAY, og.prev_ordered_at, og.ordered_at)) AS max_days
    FROM order_gaps AS og
    INNER JOIN customers AS c ON og.customer_id = c.id
    WHERE og.prev_ordered_at IS NOT NULL
    GROUP BY og.customer_id, c.name, c.grade
    HAVING COUNT(*) >= 3
    ORDER BY avg_cycle_days ASC;
        ```


---


### 24. First Purchase Repurchase Rate


Calculate the % of customers who repurchased within 30, 60, and 90 days
of their first order.


**Hint 1:** - First order = `MIN(ordered_at)` per customer
- Check if second order is within first_order + N days



??? success "Answer"

    === "SQLite"
        ```sql
        WITH first_order AS (
        SELECT
            customer_id,
            MIN(ordered_at) AS first_ordered_at
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    repeat_order AS (
        SELECT
            fo.customer_id,
            fo.first_ordered_at,
            MIN(o.ordered_at) AS second_ordered_at
        FROM first_order AS fo
        INNER JOIN orders AS o
            ON fo.customer_id = o.customer_id
           AND o.ordered_at > fo.first_ordered_at
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY fo.customer_id, fo.first_ordered_at
    )
    SELECT
        COUNT(DISTINCT fo.customer_id) AS total_customers,
        COUNT(DISTINCT CASE
            WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 30
            THEN fo.customer_id
        END) AS repurchase_30d,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 30
            THEN fo.customer_id
        END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_30d_pct,
        COUNT(DISTINCT CASE
            WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 60
            THEN fo.customer_id
        END) AS repurchase_60d,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 60
            THEN fo.customer_id
        END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_60d_pct,
        COUNT(DISTINCT CASE
            WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 90
            THEN fo.customer_id
        END) AS repurchase_90d,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 90
            THEN fo.customer_id
        END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_90d_pct
    FROM first_order AS fo
    LEFT JOIN repeat_order AS ro ON fo.customer_id = ro.customer_id;
        ```

    === "Oracle"
        ```sql
        WITH first_order AS (
        SELECT
            customer_id,
            MIN(ordered_at) AS first_ordered_at
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    repeat_order AS (
        SELECT
            fo.customer_id,
            fo.first_ordered_at,
            MIN(o.ordered_at) AS second_ordered_at
        FROM first_order fo
        INNER JOIN orders o
            ON fo.customer_id = o.customer_id
           AND o.ordered_at > fo.first_ordered_at
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY fo.customer_id, fo.first_ordered_at
    )
    SELECT
        COUNT(DISTINCT fo.customer_id) AS total_customers,
        COUNT(DISTINCT CASE
            WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 30
            THEN fo.customer_id
        END) AS repurchase_30d,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 30
            THEN fo.customer_id
        END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_30d_pct,
        COUNT(DISTINCT CASE
            WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 60
            THEN fo.customer_id
        END) AS repurchase_60d,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 60
            THEN fo.customer_id
        END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_60d_pct,
        COUNT(DISTINCT CASE
            WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 90
            THEN fo.customer_id
        END) AS repurchase_90d,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 90
            THEN fo.customer_id
        END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_90d_pct
    FROM first_order fo
    LEFT JOIN repeat_order ro ON fo.customer_id = ro.customer_id;
        ```

    === "SQL Server"
        ```sql
        WITH first_order AS (
        SELECT
            customer_id,
            MIN(ordered_at) AS first_ordered_at
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    repeat_order AS (
        SELECT
            fo.customer_id,
            fo.first_ordered_at,
            MIN(o.ordered_at) AS second_ordered_at
        FROM first_order AS fo
        INNER JOIN orders AS o
            ON fo.customer_id = o.customer_id
           AND o.ordered_at > fo.first_ordered_at
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY fo.customer_id, fo.first_ordered_at
    )
    SELECT
        COUNT(DISTINCT fo.customer_id) AS total_customers,
        COUNT(DISTINCT CASE
            WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 30
            THEN fo.customer_id
        END) AS repurchase_30d,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 30
            THEN fo.customer_id
        END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_30d_pct,
        COUNT(DISTINCT CASE
            WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 60
            THEN fo.customer_id
        END) AS repurchase_60d,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 60
            THEN fo.customer_id
        END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_60d_pct,
        COUNT(DISTINCT CASE
            WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 90
            THEN fo.customer_id
        END) AS repurchase_90d,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 90
            THEN fo.customer_id
        END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_90d_pct
    FROM first_order AS fo
    LEFT JOIN repeat_order AS ro ON fo.customer_id = ro.customer_id;
        ```


---


### 25. Point Balance Drift Detection


Find customers where the SUM of point_transactions.amount
does not match customers.point_balance.


**Hint 1:** - `SUM(pt.amount)` per customer
- Compare with `customers.point_balance`



??? success "Answer"
    ```sql
    WITH point_sum AS (
        SELECT
            customer_id,
            SUM(amount) AS calculated_balance
        FROM point_transactions
        GROUP BY customer_id
    )
    SELECT
        c.id AS customer_id,
        c.name,
        c.point_balance AS stored_balance,
        COALESCE(ps.calculated_balance, 0) AS calculated_balance,
        c.point_balance - COALESCE(ps.calculated_balance, 0) AS drift
    FROM customers AS c
    LEFT JOIN point_sum AS ps ON c.id = ps.customer_id
    WHERE c.point_balance != COALESCE(ps.calculated_balance, 0)
    ORDER BY ABS(c.point_balance - COALESCE(ps.calculated_balance, 0)) DESC
    LIMIT 20;
    ```


---


### 26. Promotion Lift Analysis


Compare average daily revenue during promotion periods vs outside.
Calculate lift percentage per promotion.


**Hint 1:** - Total revenue during `started_at` to `ended_at` / number of days
- Same for non-promotion period



??? success "Answer"

    === "SQLite"
        ```sql
        WITH promo_daily AS (
        SELECT
            pr.id AS promo_id,
            pr.name AS promo_name,
            ROUND(SUM(o.total_amount), 0) AS promo_revenue,
            CAST(JULIANDAY(pr.ended_at) - JULIANDAY(pr.started_at) + 1 AS INTEGER) AS promo_days
        FROM promotions AS pr
        INNER JOIN orders AS o
            ON o.ordered_at BETWEEN pr.started_at AND pr.ended_at
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        WHERE pr.started_at >= '2024-01-01'
        GROUP BY pr.id, pr.name, pr.started_at, pr.ended_at
    ),
    overall_daily AS (
        SELECT
            ROUND(SUM(total_amount) / 365.0, 0) AS avg_daily_revenue
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        pd.promo_name,
        pd.promo_revenue,
        pd.promo_days,
        ROUND(1.0 * pd.promo_revenue / pd.promo_days, 0) AS promo_avg_daily,
        od.avg_daily_revenue AS baseline_avg_daily,
        ROUND(100.0 * ((1.0 * pd.promo_revenue / pd.promo_days) - od.avg_daily_revenue)
            / od.avg_daily_revenue, 1) AS lift_pct
    FROM promo_daily AS pd
    CROSS JOIN overall_daily AS od
    ORDER BY lift_pct DESC
    LIMIT 15;
        ```

    === "Oracle"
        ```sql
        WITH promo_daily AS (
        SELECT
            pr.id AS promo_id,
            pr.name AS promo_name,
            ROUND(SUM(o.total_amount), 0) AS promo_revenue,
            CAST(pr.ended_at AS DATE) - CAST(pr.started_at AS DATE) + 1 AS promo_days
        FROM promotions pr
        INNER JOIN orders o
            ON o.ordered_at BETWEEN pr.started_at AND pr.ended_at
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        WHERE pr.started_at >= '2024-01-01'
        GROUP BY pr.id, pr.name, pr.started_at, pr.ended_at
    ),
    overall_daily AS (
        SELECT
            ROUND(SUM(total_amount) / 365.0, 0) AS avg_daily_revenue
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        pd.promo_name,
        pd.promo_revenue,
        pd.promo_days,
        ROUND(1.0 * pd.promo_revenue / pd.promo_days, 0) AS promo_avg_daily,
        od.avg_daily_revenue AS baseline_avg_daily,
        ROUND(100.0 * ((1.0 * pd.promo_revenue / pd.promo_days) - od.avg_daily_revenue)
            / od.avg_daily_revenue, 1) AS lift_pct
    FROM promo_daily pd
    CROSS JOIN overall_daily od
    ORDER BY lift_pct DESC
    FETCH FIRST 15 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        WITH promo_daily AS (
        SELECT
            pr.id AS promo_id,
            pr.name AS promo_name,
            ROUND(SUM(o.total_amount), 0) AS promo_revenue,
            DATEDIFF(DAY, pr.started_at, pr.ended_at) + 1 AS promo_days
        FROM promotions AS pr
        INNER JOIN orders AS o
            ON o.ordered_at BETWEEN pr.started_at AND pr.ended_at
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        WHERE pr.started_at >= '2024-01-01'
        GROUP BY pr.id, pr.name, pr.started_at, pr.ended_at
    ),
    overall_daily AS (
        SELECT
            ROUND(SUM(total_amount) / 365.0, 0) AS avg_daily_revenue
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT TOP 15
        pd.promo_name,
        pd.promo_revenue,
        pd.promo_days,
        ROUND(1.0 * pd.promo_revenue / pd.promo_days, 0) AS promo_avg_daily,
        od.avg_daily_revenue AS baseline_avg_daily,
        ROUND(100.0 * ((1.0 * pd.promo_revenue / pd.promo_days) - od.avg_daily_revenue)
            / od.avg_daily_revenue, 1) AS lift_pct
    FROM promo_daily AS pd
    CROSS JOIN overall_daily AS od
    ORDER BY lift_pct DESC;
        ```


---


### 27. Category Cross-Sell Analysis


Find category pairs most frequently bought together in the same order.


**Hint 1:** - Get category list per order first
- Self-join to generate all pairs (c1.id < c2.id to avoid duplicates)



??? success "Answer"
    ```sql
    WITH order_categories AS (
        SELECT DISTINCT
            oi.order_id,
            p.category_id,
            cat.name AS category_name
        FROM order_items AS oi
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        oc1.category_name AS category_1,
        oc2.category_name AS category_2,
        COUNT(*) AS co_occurrence
    FROM order_categories AS oc1
    INNER JOIN order_categories AS oc2
        ON oc1.order_id = oc2.order_id
       AND oc1.category_id < oc2.category_id
    GROUP BY oc1.category_name, oc2.category_name
    ORDER BY co_occurrence DESC
    LIMIT 15;
    ```


---


### 28. Grade Downgrade Trajectory


Find customers with 2+ consecutive downgrades in grade history.
e.g., VIP -> GOLD -> SILVER


**Hint 1:** - Use `LAG(reason) OVER (PARTITION BY customer_id ORDER BY changed_at)`
- Find rows where both current and previous reason = 'downgrade'



??? success "Answer"
    ```sql
    WITH grade_seq AS (
        SELECT
            customer_id,
            old_grade,
            new_grade,
            reason,
            changed_at,
            LAG(reason) OVER (
                PARTITION BY customer_id ORDER BY changed_at
            ) AS prev_reason,
            LAG(old_grade) OVER (
                PARTITION BY customer_id ORDER BY changed_at
            ) AS prev_old_grade
        FROM customer_grade_history
    )
    SELECT
        gs.customer_id,
        c.name AS customer_name,
        gs.prev_old_grade AS grade_before,
        gs.old_grade AS grade_mid,
        gs.new_grade AS grade_after,
        gs.changed_at
    FROM grade_seq AS gs
    INNER JOIN customers AS c ON gs.customer_id = c.id
    WHERE gs.reason = 'downgrade'
      AND gs.prev_reason = 'downgrade'
    ORDER BY gs.customer_id, gs.changed_at;
    ```


---


### 29. Carrier Monthly Delivery Performance with Trend


Show average delivery days by carrier by month,
with month-over-month change.


**Hint 1:** - Delivery days: `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)`
- Previous month: `LAG(avg_days) OVER (PARTITION BY carrier ORDER BY month)`



??? success "Answer"

    === "SQLite"
        ```sql
        WITH monthly_carrier AS (
        SELECT
            carrier,
            SUBSTR(shipped_at, 1, 7) AS ship_month,
            COUNT(*) AS delivery_count,
            ROUND(AVG(JULIANDAY(delivered_at) - JULIANDAY(shipped_at)), 2) AS avg_days
        FROM shipping
        WHERE delivered_at IS NOT NULL
          AND shipped_at IS NOT NULL
          AND shipped_at >= '2024-01-01'
        GROUP BY carrier, SUBSTR(shipped_at, 1, 7)
    )
    SELECT
        carrier,
        ship_month,
        delivery_count,
        avg_days,
        LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month) AS prev_month_days,
        ROUND(avg_days - LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month), 2) AS mom_change
    FROM monthly_carrier
    ORDER BY carrier, ship_month;
        ```

    === "Oracle"
        ```sql
        WITH monthly_carrier AS (
        SELECT
            carrier,
            SUBSTR(shipped_at, 1, 7) AS ship_month,
            COUNT(*) AS delivery_count,
            ROUND(AVG(CAST(delivered_at AS DATE) - CAST(shipped_at AS DATE)), 2) AS avg_days
        FROM shipping
        WHERE delivered_at IS NOT NULL
          AND shipped_at IS NOT NULL
          AND shipped_at >= '2024-01-01'
        GROUP BY carrier, SUBSTR(shipped_at, 1, 7)
    )
    SELECT
        carrier,
        ship_month,
        delivery_count,
        avg_days,
        LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month) AS prev_month_days,
        ROUND(avg_days - LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month), 2) AS mom_change
    FROM monthly_carrier
    ORDER BY carrier, ship_month;
        ```

    === "SQL Server"
        ```sql
        WITH monthly_carrier AS (
        SELECT
            carrier,
            SUBSTRING(shipped_at, 1, 7) AS ship_month,
            COUNT(*) AS delivery_count,
            ROUND(AVG(CAST(DATEDIFF(DAY, shipped_at, delivered_at) AS FLOAT)), 2) AS avg_days
        FROM shipping
        WHERE delivered_at IS NOT NULL
          AND shipped_at IS NOT NULL
          AND shipped_at >= '2024-01-01'
        GROUP BY carrier, SUBSTRING(shipped_at, 1, 7)
    )
    SELECT
        carrier,
        ship_month,
        delivery_count,
        avg_days,
        LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month) AS prev_month_days,
        ROUND(avg_days - LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month), 2) AS mom_change
    FROM monthly_carrier
    ORDER BY carrier, ship_month;
        ```


---


### 30. 3+ Consecutive Days of Increasing Revenue


Find periods of 3+ consecutive days with increasing daily revenue.
Show start date, end date, and streak length.


**Hint 1:** - Use LAG to flag daily revenue increases
- Use flag breaks as group boundaries (island pattern)
- Filter groups with streak >= 3



??? success "Answer"

    === "SQLite"
        ```sql
        WITH daily AS (
        SELECT
            SUBSTR(ordered_at, 1, 10) AS order_date,
            ROUND(SUM(total_amount), 2) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2024-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 10)
    ),
    with_flag AS (
        SELECT
            order_date,
            revenue,
            LAG(revenue) OVER (ORDER BY order_date) AS prev_revenue,
            CASE
                WHEN revenue > LAG(revenue) OVER (ORDER BY order_date) THEN 1
                ELSE 0
            END AS is_increase
        FROM daily
    ),
    with_group AS (
        SELECT
            order_date,
            revenue,
            is_increase,
            SUM(CASE WHEN is_increase = 0 THEN 1 ELSE 0 END) OVER (
                ORDER BY order_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS grp
        FROM with_flag
    )
    SELECT
        MIN(order_date) AS start_date,
        MAX(order_date) AS end_date,
        COUNT(*) AS streak_days
    FROM with_group
    WHERE is_increase = 1
    GROUP BY grp
    HAVING COUNT(*) >= 3
    ORDER BY start_date;
        ```

    === "Oracle"
        ```sql
        WITH daily AS (
        SELECT
            SUBSTR(ordered_at, 1, 10) AS order_date,
            ROUND(SUM(total_amount), 2) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2024-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 10)
    ),
    with_flag AS (
        SELECT
            order_date,
            revenue,
            LAG(revenue) OVER (ORDER BY order_date) AS prev_revenue,
            CASE
                WHEN revenue > LAG(revenue) OVER (ORDER BY order_date) THEN 1
                ELSE 0
            END AS is_increase
        FROM daily
    ),
    with_group AS (
        SELECT
            order_date,
            revenue,
            is_increase,
            SUM(CASE WHEN is_increase = 0 THEN 1 ELSE 0 END) OVER (
                ORDER BY order_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS grp
        FROM with_flag
    )
    SELECT
        MIN(order_date) AS start_date,
        MAX(order_date) AS end_date,
        COUNT(*) AS streak_days
    FROM with_group
    WHERE is_increase = 1
    GROUP BY grp
    HAVING COUNT(*) >= 3
    ORDER BY start_date;
        ```

    === "SQL Server"
        ```sql
        WITH daily AS (
        SELECT
            SUBSTRING(ordered_at, 1, 10) AS order_date,
            ROUND(SUM(total_amount), 2) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2024-01-01'
        GROUP BY SUBSTRING(ordered_at, 1, 10)
    ),
    with_flag AS (
        SELECT
            order_date,
            revenue,
            LAG(revenue) OVER (ORDER BY order_date) AS prev_revenue,
            CASE
                WHEN revenue > LAG(revenue) OVER (ORDER BY order_date) THEN 1
                ELSE 0
            END AS is_increase
        FROM daily
    ),
    with_group AS (
        SELECT
            order_date,
            revenue,
            is_increase,
            SUM(CASE WHEN is_increase = 0 THEN 1 ELSE 0 END) OVER (
                ORDER BY order_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS grp
        FROM with_flag
    )
    SELECT
        MIN(order_date) AS start_date,
        MAX(order_date) AS end_date,
        COUNT(*) AS streak_days
    FROM with_group
    WHERE is_increase = 1
    GROUP BY grp
    HAVING COUNT(*) >= 3
    ORDER BY start_date;
        ```


---


### 31. Customers with Consecutive Monthly Orders


Find customers who ordered every month for 5+ consecutive months.
Show customer name, streak start month, end month, and duration.


**Hint 1:** - Get monthly order flag per customer first
- Use "month_number - ROW_NUMBER" pattern to detect consecutive months
- Rows with same difference form a consecutive group



??? success "Answer"

    === "SQLite"
        ```sql
        WITH customer_months AS (
        SELECT DISTINCT
            customer_id,
            SUBSTR(ordered_at, 1, 7) AS order_month,
            CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER) * 12
                + CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) AS month_num
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    with_rn AS (
        SELECT
            customer_id,
            order_month,
            month_num,
            month_num - ROW_NUMBER() OVER (
                PARTITION BY customer_id ORDER BY month_num
            ) AS grp
        FROM customer_months
    ),
    streaks AS (
        SELECT
            customer_id,
            MIN(order_month) AS start_month,
            MAX(order_month) AS end_month,
            COUNT(*) AS consecutive_months
        FROM with_rn
        GROUP BY customer_id, grp
        HAVING COUNT(*) >= 5
    )
    SELECT
        c.name AS customer_name,
        c.grade,
        s.start_month,
        s.end_month,
        s.consecutive_months
    FROM streaks AS s
    INNER JOIN customers AS c ON s.customer_id = c.id
    ORDER BY s.consecutive_months DESC, c.name
    LIMIT 20;
        ```

    === "Oracle"
        ```sql
        WITH customer_months AS (
        SELECT DISTINCT
            customer_id,
            SUBSTR(ordered_at, 1, 7) AS order_month,
            CAST(SUBSTR(ordered_at, 1, 4) AS NUMBER) * 12
                + CAST(SUBSTR(ordered_at, 6, 2) AS NUMBER) AS month_num
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    with_rn AS (
        SELECT
            customer_id,
            order_month,
            month_num,
            month_num - ROW_NUMBER() OVER (
                PARTITION BY customer_id ORDER BY month_num
            ) AS grp
        FROM customer_months
    ),
    streaks AS (
        SELECT
            customer_id,
            MIN(order_month) AS start_month,
            MAX(order_month) AS end_month,
            COUNT(*) AS consecutive_months
        FROM with_rn
        GROUP BY customer_id, grp
        HAVING COUNT(*) >= 5
    )
    SELECT
        c.name AS customer_name,
        c.grade,
        s.start_month,
        s.end_month,
        s.consecutive_months
    FROM streaks s
    INNER JOIN customers c ON s.customer_id = c.id
    ORDER BY s.consecutive_months DESC, c.name
    FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        WITH customer_months AS (
        SELECT DISTINCT
            customer_id,
            SUBSTRING(ordered_at, 1, 7) AS order_month,
            CAST(SUBSTRING(ordered_at, 1, 4) AS INT) * 12
                + CAST(SUBSTRING(ordered_at, 6, 2) AS INT) AS month_num
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    with_rn AS (
        SELECT
            customer_id,
            order_month,
            month_num,
            month_num - ROW_NUMBER() OVER (
                PARTITION BY customer_id ORDER BY month_num
            ) AS grp
        FROM customer_months
    ),
    streaks AS (
        SELECT
            customer_id,
            MIN(order_month) AS start_month,
            MAX(order_month) AS end_month,
            COUNT(*) AS consecutive_months
        FROM with_rn
        GROUP BY customer_id, grp
        HAVING COUNT(*) >= 5
    )
    SELECT TOP 20
        c.name AS customer_name,
        c.grade,
        s.start_month,
        s.end_month,
        s.consecutive_months
    FROM streaks AS s
    INNER JOIN customers AS c ON s.customer_id = c.id
    ORDER BY s.consecutive_months DESC, c.name;
        ```


---


### 32. Session Definition (30-min Gap)


Group product_views into sessions (30+ minute gap = new session for same customer).
Calculate sessions per customer and average views per session.


**Hint 1:** - Use `LAG(viewed_at)` for previous view time
- 30 min = `(JULIANDAY(current) - JULIANDAY(prev)) * 24 * 60 > 30`
- `SUM(is_new_session) OVER (...)` to assign session numbers



??? success "Answer"

    === "SQLite"
        ```sql
        WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
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
        WHERE customer_id <= 500
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
        WHERE customer_id <= 500
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
        WHERE customer_id <= 500
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


### 33. Session Redefinition (10-min Gap)


Same as c11-32 but with a 10-minute gap threshold.
Compare session counts with the 30-minute version.


**Hint 1:** - Just change 30 to 10
- Sessions will split more frequently



??? success "Answer"

    === "SQLite"
        ```sql
        WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
            CASE
                WHEN LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) IS NULL THEN 1
                WHEN (JULIANDAY(viewed_at) - JULIANDAY(LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ))) * 24 * 60 > 10 THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
        WHERE customer_id <= 500
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
            CASE
                WHEN LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) IS NULL THEN 1
                WHEN (CAST(viewed_at AS DATE) - CAST(LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) AS DATE)) * 24 * 60 > 10 THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
        WHERE customer_id <= 500
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
            CASE
                WHEN LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) IS NULL THEN 1
                WHEN DATEDIFF(MINUTE, LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ), viewed_at) > 10 THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
        WHERE customer_id <= 500
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


### 34. Median Order Amount by Customer Grade


Calculate the median order amount per customer grade.
SQLite lacks MEDIAN, so implement it using NTILE or ROW_NUMBER.


**Hint 1:** - `ROW_NUMBER()` OVER (PARTITION BY grade ORDER BY total_amount)
- Median is at half of total count
- `COUNT(*) OVER (PARTITION BY grade)` for total count



??? success "Answer"
    ```sql
    WITH grade_orders AS (
        SELECT
            c.grade,
            o.total_amount,
            ROW_NUMBER() OVER (PARTITION BY c.grade ORDER BY o.total_amount) AS rn,
            COUNT(*) OVER (PARTITION BY c.grade) AS cnt
        FROM orders AS o
        INNER JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        grade,
        ROUND(AVG(total_amount), 2) AS median_amount
    FROM grade_orders
    WHERE rn IN (cnt / 2, cnt / 2 + 1)
    GROUP BY grade
    ORDER BY
        CASE grade
            WHEN 'VIP' THEN 1 WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3 WHEN 'BRONZE' THEN 4
        END;
    ```


---


### 35. Median Delivery Days by Carrier


Calculate the median delivery duration (in days) by carrier.


**Hint 1:** - Calculate delivery days: `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)`
- Use `ROW_NUMBER()` and pick the middle value



??? success "Answer"

    === "SQLite"
        ```sql
        WITH delivery_days AS (
        SELECT
            carrier,
            ROUND(JULIANDAY(delivered_at) - JULIANDAY(shipped_at), 1) AS days,
            ROW_NUMBER() OVER (PARTITION BY carrier ORDER BY JULIANDAY(delivered_at) - JULIANDAY(shipped_at)) AS rn,
            COUNT(*) OVER (PARTITION BY carrier) AS cnt
        FROM shipping
        WHERE delivered_at IS NOT NULL
          AND shipped_at IS NOT NULL
    )
    SELECT
        carrier,
        ROUND(AVG(days), 2) AS median_days
    FROM delivery_days
    WHERE rn IN (cnt / 2, cnt / 2 + 1)
    GROUP BY carrier
    ORDER BY median_days;
        ```

    === "Oracle"
        ```sql
        WITH delivery_days AS (
        SELECT
            carrier,
            ROUND(CAST(delivered_at AS DATE) - CAST(shipped_at AS DATE), 1) AS days,
            ROW_NUMBER() OVER (PARTITION BY carrier ORDER BY CAST(delivered_at AS DATE) - CAST(shipped_at AS DATE)) AS rn,
            COUNT(*) OVER (PARTITION BY carrier) AS cnt
        FROM shipping
        WHERE delivered_at IS NOT NULL
          AND shipped_at IS NOT NULL
    )
    SELECT
        carrier,
        ROUND(AVG(days), 2) AS median_days
    FROM delivery_days
    WHERE rn IN (TRUNC(cnt / 2), TRUNC(cnt / 2) + 1)
    GROUP BY carrier
    ORDER BY median_days;
        ```

    === "SQL Server"
        ```sql
        WITH delivery_days AS (
        SELECT
            carrier,
            ROUND(CAST(DATEDIFF(DAY, shipped_at, delivered_at) AS FLOAT), 1) AS days,
            ROW_NUMBER() OVER (PARTITION BY carrier ORDER BY DATEDIFF(DAY, shipped_at, delivered_at)) AS rn,
            COUNT(*) OVER (PARTITION BY carrier) AS cnt
        FROM shipping
        WHERE delivered_at IS NOT NULL
          AND shipped_at IS NOT NULL
    )
    SELECT
        carrier,
        ROUND(AVG(days), 2) AS median_days
    FROM delivery_days
    WHERE rn IN (cnt / 2, cnt / 2 + 1)
    GROUP BY carrier
    ORDER BY median_days;
        ```


---


### 36. Funnel Drop-off by Device Type


By device_type (desktop/mobile/tablet), calculate conversion and drop-off rates
for view -> cart -> purchase funnel.


**Hint 1:** - Group by `product_views.device_type`
- Count distinct customers at each stage by device
- Drop-off rate = 1 - conversion rate



??? success "Answer"
    ```sql
    WITH view_step AS (
        SELECT
            device_type,
            COUNT(DISTINCT customer_id) AS viewers
        FROM product_views
        GROUP BY device_type
    ),
    cart_step AS (
        SELECT
            pv.device_type,
            COUNT(DISTINCT c.customer_id) AS carters
        FROM product_views AS pv
        INNER JOIN carts AS c ON pv.customer_id = c.customer_id
        INNER JOIN cart_items AS ci ON c.id = ci.cart_id AND pv.product_id = ci.product_id
        GROUP BY pv.device_type
    ),
    purchase_step AS (
        SELECT
            pv.device_type,
            COUNT(DISTINCT o.customer_id) AS buyers
        FROM product_views AS pv
        INNER JOIN orders AS o ON pv.customer_id = o.customer_id
        INNER JOIN order_items AS oi ON o.id = oi.order_id AND pv.product_id = oi.product_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY pv.device_type
    )
    SELECT
        vs.device_type,
        vs.viewers,
        COALESCE(cs.carters, 0) AS carters,
        ROUND(100.0 * COALESCE(cs.carters, 0) / vs.viewers, 2) AS view_to_cart_pct,
        COALESCE(ps.buyers, 0) AS buyers,
        ROUND(100.0 * COALESCE(ps.buyers, 0) / NULLIF(COALESCE(cs.carters, 0), 0), 2) AS cart_to_buy_pct,
        ROUND(100.0 * COALESCE(ps.buyers, 0) / vs.viewers, 2) AS view_to_buy_pct
    FROM view_step AS vs
    LEFT JOIN cart_step AS cs ON vs.device_type = cs.device_type
    LEFT JOIN purchase_step AS ps ON vs.device_type = ps.device_type
    ORDER BY vs.device_type;
    ```


---


### 37. Channel Attribution Analysis


Calculate views and purchase conversions by referrer_source.
For multi-channel customers, give credit to the last-touch channel before purchase.


**Hint 1:** - Get last referrer_source per customer (most recent product_view)
- Credit that channel for conversion



??? success "Answer"
    ```sql
    WITH last_touch AS (
        SELECT
            pv.customer_id,
            pv.referrer_source,
            ROW_NUMBER() OVER (
                PARTITION BY pv.customer_id
                ORDER BY pv.viewed_at DESC
            ) AS rn
        FROM product_views AS pv
        INNER JOIN orders AS o ON pv.customer_id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    channel_views AS (
        SELECT
            referrer_source,
            COUNT(*) AS total_views,
            COUNT(DISTINCT customer_id) AS unique_viewers
        FROM product_views
        GROUP BY referrer_source
    ),
    channel_conversions AS (
        SELECT
            referrer_source,
            COUNT(DISTINCT customer_id) AS conversions
        FROM last_touch
        WHERE rn = 1
        GROUP BY referrer_source
    )
    SELECT
        cv.referrer_source,
        cv.total_views,
        cv.unique_viewers,
        COALESCE(cc.conversions, 0) AS last_touch_conversions,
        ROUND(100.0 * COALESCE(cc.conversions, 0) / cv.unique_viewers, 2) AS conversion_rate_pct
    FROM channel_views AS cv
    LEFT JOIN channel_conversions AS cc ON cv.referrer_source = cc.referrer_source
    ORDER BY last_touch_conversions DESC;
    ```


---


### 38. Active Day Island Detection


Find "islands" of consecutive active days per customer in product_views.
e.g., Mon/Tue/Wed views -> Thu gap -> Fri/Sat views = 2 islands (3 days, 2 days).


**Hint 1:** - Extract distinct view dates per customer
- Use `date - ROW_NUMBER` pattern to group consecutive dates
- MIN/MAX/COUNT per group



??? success "Answer"

    === "SQLite"
        ```sql
        WITH active_days AS (
        SELECT DISTINCT
            customer_id,
            SUBSTR(viewed_at, 1, 10) AS view_date
        FROM product_views
        WHERE customer_id <= 200
    ),
    with_rn AS (
        SELECT
            customer_id,
            view_date,
            JULIANDAY(view_date) - ROW_NUMBER() OVER (
                PARTITION BY customer_id ORDER BY view_date
            ) AS grp
        FROM active_days
    ),
    islands AS (
        SELECT
            customer_id,
            MIN(view_date) AS island_start,
            MAX(view_date) AS island_end,
            COUNT(*) AS island_days
        FROM with_rn
        GROUP BY customer_id, grp
        HAVING COUNT(*) >= 3
    )
    SELECT
        c.name AS customer_name,
        i.island_start,
        i.island_end,
        i.island_days
    FROM islands AS i
    INNER JOIN customers AS c ON i.customer_id = c.id
    ORDER BY i.island_days DESC, c.name
    LIMIT 20;
        ```

    === "Oracle"
        ```sql
        WITH active_days AS (
        SELECT DISTINCT
            customer_id,
            SUBSTR(viewed_at, 1, 10) AS view_date
        FROM product_views
        WHERE customer_id <= 200
    ),
    with_rn AS (
        SELECT
            customer_id,
            view_date,
            CAST(view_date AS DATE) - ROW_NUMBER() OVER (
                PARTITION BY customer_id ORDER BY view_date
            ) AS grp
        FROM active_days
    ),
    islands AS (
        SELECT
            customer_id,
            MIN(view_date) AS island_start,
            MAX(view_date) AS island_end,
            COUNT(*) AS island_days
        FROM with_rn
        GROUP BY customer_id, grp
        HAVING COUNT(*) >= 3
    )
    SELECT
        c.name AS customer_name,
        i.island_start,
        i.island_end,
        i.island_days
    FROM islands i
    INNER JOIN customers c ON i.customer_id = c.id
    ORDER BY i.island_days DESC, c.name
    FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        WITH active_days AS (
        SELECT DISTINCT
            customer_id,
            SUBSTRING(viewed_at, 1, 10) AS view_date
        FROM product_views
        WHERE customer_id <= 200
    ),
    with_rn AS (
        SELECT
            customer_id,
            view_date,
            DATEADD(DAY, -ROW_NUMBER() OVER (
                PARTITION BY customer_id ORDER BY view_date
            ), CAST(view_date AS DATE)) AS grp
        FROM active_days
    ),
    islands AS (
        SELECT
            customer_id,
            MIN(view_date) AS island_start,
            MAX(view_date) AS island_end,
            COUNT(*) AS island_days
        FROM with_rn
        GROUP BY customer_id, grp
        HAVING COUNT(*) >= 3
    )
    SELECT TOP 20
        c.name AS customer_name,
        i.island_start,
        i.island_end,
        i.island_days
    FROM islands AS i
    INNER JOIN customers AS c ON i.customer_id = c.id
    ORDER BY i.island_days DESC, c.name;
        ```


---


### 39. Complete Monthly Dashboard


Build a complete monthly dashboard for 2024 in one query:
revenue, orders, new customers, active customers, avg order value,
month-over-month revenue change, and top product by revenue.


**Hint 1:** - Prepare order/customer/product stats in separate CTEs
- JOIN all by month
- LAG for month-over-month change
- ROW_NUMBER for top product per month



??? success "Answer"
    ```sql
    WITH monthly_orders AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            COUNT(*) AS order_count,
            ROUND(SUM(total_amount), 0) AS revenue,
            ROUND(AVG(total_amount), 0) AS avg_order_value,
            COUNT(DISTINCT customer_id) AS active_customers
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    ),
    new_customers AS (
        SELECT
            SUBSTR(created_at, 1, 7) AS year_month,
            COUNT(*) AS new_customer_count
        FROM customers
        WHERE created_at LIKE '2024%'
        GROUP BY SUBSTR(created_at, 1, 7)
    ),
    top_products AS (
        SELECT
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            p.name AS product_name,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS product_revenue,
            ROW_NUMBER() OVER (
                PARTITION BY SUBSTR(o.ordered_at, 1, 7)
                ORDER BY SUM(oi.quantity * oi.unit_price) DESC
            ) AS rn
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(o.ordered_at, 1, 7), p.id, p.name
    ),
    with_growth AS (
        SELECT
            mo.year_month,
            mo.revenue,
            mo.order_count,
            COALESCE(nc.new_customer_count, 0) AS new_customers,
            mo.active_customers,
            mo.avg_order_value,
            LAG(mo.revenue) OVER (ORDER BY mo.year_month) AS prev_revenue,
            ROUND(100.0 * (mo.revenue - LAG(mo.revenue) OVER (ORDER BY mo.year_month))
                / NULLIF(LAG(mo.revenue) OVER (ORDER BY mo.year_month), 0), 1) AS mom_growth_pct,
            tp.product_name AS top_product
        FROM monthly_orders AS mo
        LEFT JOIN new_customers AS nc ON mo.year_month = nc.year_month
        LEFT JOIN top_products AS tp ON mo.year_month = tp.year_month AND tp.rn = 1
    )
    SELECT
        year_month,
        revenue,
        order_count,
        new_customers,
        active_customers,
        avg_order_value,
        mom_growth_pct,
        top_product
    FROM with_growth
    ORDER BY year_month;
    ```


---


### 40. JSON Specs Query


Extract CPU information from the products.specs JSON column.
Show product name and CPU for products where specs is not NULL.


**Hint 1:** - SQLite: use `JSON_EXTRACT(specs, '$.cpu')`
- PostgreSQL: use `specs->>'cpu'`
- Filter `WHERE specs IS NOT NULL`



??? success "Answer"

    === "SQLite"
        ```sql
        SELECT
        name,
        brand,
        price,
        JSON_EXTRACT(specs, '$.cpu') AS cpu,
        JSON_EXTRACT(specs, '$.ram') AS ram,
        JSON_EXTRACT(specs, '$.storage') AS storage
    FROM products
    WHERE specs IS NOT NULL
      AND JSON_EXTRACT(specs, '$.cpu') IS NOT NULL
    ORDER BY price DESC
    LIMIT 20;
        ```

    === "MySQL"
        ```sql
        SELECT
        name,
        brand,
        price,
        JSON_EXTRACT(specs, '$.cpu') AS cpu,
        JSON_EXTRACT(specs, '$.ram') AS ram,
        JSON_EXTRACT(specs, '$.storage') AS storage
    FROM products
    WHERE specs IS NOT NULL
      AND JSON_EXTRACT(specs, '$.cpu') IS NOT NULL
    ORDER BY price DESC
    LIMIT 20;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
        name,
        brand,
        price,
        specs->>'cpu' AS cpu,
        specs->>'ram' AS ram,
        specs->>'storage' AS storage
    FROM products
    WHERE specs IS NOT NULL
      AND specs->>'cpu' IS NOT NULL
    ORDER BY price DESC
    LIMIT 20;
        ```

    === "Oracle"
        ```sql
        SELECT
        name,
        brand,
        price,
        JSON_VALUE(specs, '$.cpu') AS cpu,
        JSON_VALUE(specs, '$.ram') AS ram,
        JSON_VALUE(specs, '$.storage') AS storage
    FROM products
    WHERE specs IS NOT NULL
      AND JSON_VALUE(specs, '$.cpu') IS NOT NULL
    ORDER BY price DESC
    FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        SELECT TOP 20
        name,
        brand,
        price,
        JSON_VALUE(specs, '$.cpu') AS cpu,
        JSON_VALUE(specs, '$.ram') AS ram,
        JSON_VALUE(specs, '$.storage') AS storage
    FROM products
    WHERE specs IS NOT NULL
      AND JSON_VALUE(specs, '$.cpu') IS NOT NULL
    ORDER BY price DESC;
        ```


---
