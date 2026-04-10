# Lesson 19: Common Table Expressions (WITH)

A Common Table Expression (CTE) is a named, temporary result set defined with the `WITH` keyword before the main query. CTEs make complex queries dramatically easier to read, debug, and reuse — each CTE is like a named subquery you can reference multiple times.

```mermaid
flowchart TD
    subgraph "CTE Pipeline"
        CTE1["WITH sales AS (\n  SELECT ...\n)"] --> CTE2["monthly AS (\n  SELECT ... FROM sales\n)"] --> FQ["SELECT *\nFROM monthly\nWHERE ..."]
    end
```

```mermaid
flowchart TD
    B["Base Case\n(WHERE parent_id IS NULL)"] --> |"Level 0"| N1["Desktop PC"]
    N1 --> |"Level 1"| N2["Pre-built"]
    N1 --> |"Level 1"| N3["Custom"]
    N2 --> |"Level 2"| N4["Samsung"]
    N2 --> |"Level 2"| N5["LG"]
```

> CTEs break queries into steps connected like a pipeline. Recursive CTEs traverse tree structures.

## Basic CTE

=== "SQLite"
    ```sql
    WITH monthly_revenue AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            SUM(total_amount)        AS revenue,
            COUNT(*)                 AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        order_count,
        ROUND(revenue / order_count, 2) AS avg_order_value
    FROM monthly_revenue
    WHERE year_month LIKE '2024%'
    ORDER BY year_month;
    ```

=== "MySQL"
    ```sql
    WITH monthly_revenue AS (
        SELECT
            DATE_FORMAT(ordered_at, '%Y-%m') AS year_month,
            SUM(total_amount)                AS revenue,
            COUNT(*)                         AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned')
        GROUP BY DATE_FORMAT(ordered_at, '%Y-%m')
    )
    SELECT
        year_month,
        revenue,
        order_count,
        ROUND(revenue / order_count, 2) AS avg_order_value
    FROM monthly_revenue
    WHERE year_month LIKE '2024%'
    ORDER BY year_month;
    ```

=== "PostgreSQL"
    ```sql
    WITH monthly_revenue AS (
        SELECT
            TO_CHAR(ordered_at, 'YYYY-MM') AS year_month,
            SUM(total_amount)              AS revenue,
            COUNT(*)                       AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned')
        GROUP BY TO_CHAR(ordered_at, 'YYYY-MM')
    )
    SELECT
        year_month,
        revenue,
        order_count,
        ROUND(revenue / order_count, 2) AS avg_order_value
    FROM monthly_revenue
    WHERE year_month LIKE '2024%'
    ORDER BY year_month;
    ```

**Result:**

| year_month | revenue | order_count | avg_order_value |
|------------|--------:|------------:|----------------:|
| 2024-01 | 147832.40 | 270 | 547.53 |
| 2024-02 | 136290.10 | 251 | 542.99 |
| 2024-03 | 204123.70 | 347 | 588.25 |
| ... | | | |

The CTE `monthly_revenue` reads like a named step — first we compute monthly totals, then we query them. No nested subquery nesting needed.

## Multiple CTEs

Chain CTEs with commas. Each CTE can reference any CTE defined before it.

```sql
-- Customer lifetime value segmentation
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(*)          AS order_count,
        SUM(total_amount) AS lifetime_value
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned')
    GROUP BY customer_id
),
customer_segments AS (
    SELECT
        co.customer_id,
        c.name,
        c.grade,
        co.order_count,
        co.lifetime_value,
        CASE
            WHEN co.lifetime_value >= 5000 THEN 'Champion'
            WHEN co.lifetime_value >= 2000 THEN 'Loyal'
            WHEN co.lifetime_value >= 500  THEN 'Regular'
            ELSE 'Occasional'
        END AS segment
    FROM customer_orders AS co
    INNER JOIN customers AS c ON co.customer_id = c.id
)
SELECT
    segment,
    COUNT(*)                    AS customer_count,
    ROUND(AVG(lifetime_value), 2) AS avg_ltv,
    ROUND(AVG(order_count), 1)    AS avg_orders
FROM customer_segments
GROUP BY segment
ORDER BY avg_ltv DESC;
```

**Result:**

| segment | customer_count | avg_ltv | avg_orders |
|---------|---------------:|--------:|-----------:|
| Champion | 312 | 8942.30 | 38.2 |
| Loyal | 891 | 3124.60 | 18.7 |
| Regular | 2341 | 842.30 | 6.4 |
| Occasional | 1242 | 198.70 | 2.1 |

## CTEs with Window Functions

CTEs and window functions complement each other well. Compute ranked results in a CTE, then filter in the main query.

```sql
-- Top 3 customers by revenue per membership grade
WITH customer_revenue AS (
    SELECT
        c.id,
        c.name,
        c.grade,
        SUM(o.total_amount) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned')
    GROUP BY c.id, c.name, c.grade
),
ranked AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY grade ORDER BY total_spent DESC) AS rnk
    FROM customer_revenue
)
SELECT grade, name, total_spent, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY grade, rnk;
```

**Result:**

| grade  | name | total_spent | rnk |
| ------ | ---- | ----------: | --: |
| BRONZE | 이정남  |   107052173 |   1 |
| BRONZE | 배종수  |    93476435 |   2 |
| BRONZE | 김선영  |    56829558 |   3 |
| GOLD   | 이옥순  |   160926628 |   1 |
| ...    | ...  | ...         | ... |

## Recursive CTE — Category Tree

A recursive CTE references itself. It is the standard SQL way to walk hierarchical data like a category tree, org chart, or bill of materials.

The `categories` table has a `parent_id` column that points to itself.

=== "SQLite / PostgreSQL"
    ```sql
    -- Walk the full category tree and show depth/path
    WITH RECURSIVE category_tree AS (
        -- Base case: root categories (no parent)
        SELECT
            id,
            name,
            parent_id,
            0             AS depth,
            name          AS path
        FROM categories
        WHERE parent_id IS NULL

        UNION ALL

        -- Recursive case: children of already-found nodes
        SELECT
            c.id,
            c.name,
            c.parent_id,
            ct.depth + 1,
            ct.path || ' > ' || c.name
        FROM categories AS c
        INNER JOIN category_tree AS ct ON c.parent_id = ct.id
    )
    SELECT
        SUBSTR('          ', 1, depth * 2) || name AS indented_name,
        depth,
        path
    FROM category_tree
    ORDER BY path;
    ```

=== "MySQL"
    ```sql
    -- Walk the full category tree and show depth/path
    WITH RECURSIVE category_tree AS (
        -- Base case: root categories (no parent)
        SELECT
            id,
            name,
            parent_id,
            0             AS depth,
            name          AS path
        FROM categories
        WHERE parent_id IS NULL

        UNION ALL

        -- Recursive case: children of already-found nodes
        SELECT
            c.id,
            c.name,
            c.parent_id,
            ct.depth + 1,
            CONCAT(ct.path, ' > ', c.name)
        FROM categories AS c
        INNER JOIN category_tree AS ct ON c.parent_id = ct.id
    )
    SELECT
        CONCAT(SUBSTR('          ', 1, depth * 2), name) AS indented_name,
        depth,
        path
    FROM category_tree
    ORDER BY path;
    ```

**Result:**

| indented_name | depth | path |
|---------------|------:|------|
| Electronics | 0 | Electronics |
|   Computers | 1 | Electronics > Computers |
|     Laptops | 2 | Electronics > Computers > Laptops |
|     Desktops | 2 | Electronics > Computers > Desktops |
|   Peripherals | 1 | Electronics > Peripherals |
|     Mice | 2 | Electronics > Peripherals > Mice |
|     Keyboards | 2 | Electronics > Peripherals > Keyboards |
| ... | | |

## More Recursive CTE Examples

### Staff Org Chart (Recursive CTE)

Recursively follow `staff.manager_id` to build the full organizational hierarchy.

=== "SQLite / PostgreSQL"
    ```sql
    WITH RECURSIVE org_chart AS (
        -- Base: CEO (no manager)
        SELECT id, name, role, department, manager_id, 0 AS level,
               name AS path
        FROM staff
        WHERE manager_id IS NULL

        UNION ALL

        -- Recursive: employees under each manager
        SELECT s.id, s.name, s.role, s.department, s.manager_id,
               oc.level + 1,
               oc.path || ' > ' || s.name
        FROM staff s
        JOIN org_chart oc ON s.manager_id = oc.id
    )
    SELECT level, path, role, department
    FROM org_chart
    ORDER BY path;
    ```

=== "MySQL"
    ```sql
    WITH RECURSIVE org_chart AS (
        -- Base: CEO (no manager)
        SELECT id, name, role, department, manager_id, 0 AS level,
               name AS path
        FROM staff
        WHERE manager_id IS NULL

        UNION ALL

        -- Recursive: employees under each manager
        SELECT s.id, s.name, s.role, s.department, s.manager_id,
               oc.level + 1,
               CONCAT(oc.path, ' > ', s.name)
        FROM staff s
        JOIN org_chart oc ON s.manager_id = oc.id
    )
    SELECT level, path, role, department
    FROM org_chart
    ORDER BY path;
    ```

### Q&A Threads (Recursive CTE)

Recursively trace the question → answer → follow-up chain.

=== "SQLite / PostgreSQL"
    ```sql
    WITH RECURSIVE thread AS (
        SELECT id, content, parent_id, 0 AS depth,
               CAST(id AS TEXT) AS thread_path
        FROM product_qna
        WHERE parent_id IS NULL

        UNION ALL

        SELECT q.id, q.content, q.parent_id, t.depth + 1,
               t.thread_path || '.' || CAST(q.id AS TEXT)
        FROM product_qna q
        JOIN thread t ON q.parent_id = t.id
    )
    SELECT depth, thread_path, SUBSTR('          ', 1, depth * 2) || content AS indented
    FROM thread
    ORDER BY thread_path
    LIMIT 20;
    ```

=== "MySQL"
    ```sql
    WITH RECURSIVE thread AS (
        SELECT id, content, parent_id, 0 AS depth,
               CAST(id AS CHAR) AS thread_path
        FROM product_qna
        WHERE parent_id IS NULL

        UNION ALL

        SELECT q.id, q.content, q.parent_id, t.depth + 1,
               CONCAT(t.thread_path, '.', CAST(q.id AS CHAR))
        FROM product_qna q
        JOIN thread t ON q.parent_id = t.id
    )
    SELECT depth, thread_path, CONCAT(SUBSTR('          ', 1, depth * 2), content) AS indented
    FROM thread
    ORDER BY thread_path
    LIMIT 20;
    ```

!!! note "Lesson Review"
    Quick exercises to check your understanding of this lesson. For comprehensive practice combining multiple concepts, see the [Exercises](../exercises/index.md) section.

## Practice Exercises

### Exercise 1
Using two CTEs, find the monthly revenue for 2024, then compute the month-over-month change in revenue. CTE 1: monthly totals. CTE 2: add `LAG` for previous month. Main query: return all columns plus the computed `mom_change` and `mom_pct`.

??? success "Answer"
    === "SQLite"
        ```sql
        WITH monthly AS (
            SELECT
                SUBSTR(ordered_at, 1, 7) AS year_month,
                SUM(total_amount)        AS revenue
            FROM orders
            WHERE ordered_at LIKE '2024%'
              AND status NOT IN ('cancelled', 'returned')
            GROUP BY SUBSTR(ordered_at, 1, 7)
        ),
        with_lag AS (
            SELECT
                year_month,
                revenue,
                LAG(revenue) OVER (ORDER BY year_month) AS prev_revenue
            FROM monthly
        )
        SELECT
            year_month,
            revenue,
            prev_revenue,
            ROUND(revenue - prev_revenue, 2) AS mom_change,
            ROUND(100.0 * (revenue - prev_revenue) / prev_revenue, 1) AS mom_pct
        FROM with_lag
        ORDER BY year_month;
        ```

    === "MySQL"
        ```sql
        WITH monthly AS (
            SELECT
                DATE_FORMAT(ordered_at, '%Y-%m') AS year_month,
                SUM(total_amount)                AS revenue
            FROM orders
            WHERE ordered_at >= '2024-01-01'
              AND ordered_at <  '2025-01-01'
              AND status NOT IN ('cancelled', 'returned')
            GROUP BY DATE_FORMAT(ordered_at, '%Y-%m')
        ),
        with_lag AS (
            SELECT
                year_month,
                revenue,
                LAG(revenue) OVER (ORDER BY year_month) AS prev_revenue
            FROM monthly
        )
        SELECT
            year_month,
            revenue,
            prev_revenue,
            ROUND(revenue - prev_revenue, 2) AS mom_change,
            ROUND(100.0 * (revenue - prev_revenue) / prev_revenue, 1) AS mom_pct
        FROM with_lag
        ORDER BY year_month;
        ```

    === "PostgreSQL"
        ```sql
        WITH monthly AS (
            SELECT
                TO_CHAR(ordered_at, 'YYYY-MM') AS year_month,
                SUM(total_amount)              AS revenue
            FROM orders
            WHERE ordered_at >= '2024-01-01'
              AND ordered_at <  '2025-01-01'
              AND status NOT IN ('cancelled', 'returned')
            GROUP BY TO_CHAR(ordered_at, 'YYYY-MM')
        ),
        with_lag AS (
            SELECT
                year_month,
                revenue,
                LAG(revenue) OVER (ORDER BY year_month) AS prev_revenue
            FROM monthly
        )
        SELECT
            year_month,
            revenue,
            prev_revenue,
            ROUND(revenue - prev_revenue, 2) AS mom_change,
            ROUND(100.0 * (revenue - prev_revenue) / prev_revenue, 1) AS mom_pct
        FROM with_lag
        ORDER BY year_month;
        ```

### Exercise 2
Use a CTE to identify "at-risk" customers: those who have placed at least 3 orders but whose most recent order was more than 180 days ago. Return `customer_id`, `name`, `grade`, `order_count`, and `last_order_date`.

??? success "Answer"
    === "SQLite"
        ```sql
        WITH customer_recency AS (
            SELECT
                customer_id,
                COUNT(*)        AS order_count,
                MAX(ordered_at) AS last_order_date
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned')
            GROUP BY customer_id
        )
        SELECT
            c.id    AS customer_id,
            c.name,
            c.grade,
            cr.order_count,
            cr.last_order_date
        FROM customer_recency AS cr
        INNER JOIN customers AS c ON cr.customer_id = c.id
        WHERE cr.order_count >= 3
          AND julianday('now') - julianday(cr.last_order_date) > 180
        ORDER BY cr.last_order_date ASC;
        ```

    === "MySQL"
        ```sql
        WITH customer_recency AS (
            SELECT
                customer_id,
                COUNT(*)        AS order_count,
                MAX(ordered_at) AS last_order_date
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned')
            GROUP BY customer_id
        )
        SELECT
            c.id    AS customer_id,
            c.name,
            c.grade,
            cr.order_count,
            cr.last_order_date
        FROM customer_recency AS cr
        INNER JOIN customers AS c ON cr.customer_id = c.id
        WHERE cr.order_count >= 3
          AND DATEDIFF(NOW(), cr.last_order_date) > 180
        ORDER BY cr.last_order_date ASC;
        ```

    === "PostgreSQL"
        ```sql
        WITH customer_recency AS (
            SELECT
                customer_id,
                COUNT(*)        AS order_count,
                MAX(ordered_at) AS last_order_date
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned')
            GROUP BY customer_id
        )
        SELECT
            c.id    AS customer_id,
            c.name,
            c.grade,
            cr.order_count,
            cr.last_order_date
        FROM customer_recency AS cr
        INNER JOIN customers AS c ON cr.customer_id = c.id
        WHERE cr.order_count >= 3
          AND CURRENT_DATE - cr.last_order_date::date > 180
        ORDER BY cr.last_order_date ASC;
        ```

### Exercise 3
Use a recursive CTE to build the full breadcrumb path for every leaf category (categories with no children). Return `category_id`, `category_name`, and `full_path`.

??? success "Answer"
    === "SQLite / PostgreSQL"
        ```sql
        WITH RECURSIVE category_tree AS (
            SELECT
                id,
                name,
                parent_id,
                name AS full_path
            FROM categories
            WHERE parent_id IS NULL

            UNION ALL

            SELECT
                c.id,
                c.name,
                c.parent_id,
                ct.full_path || ' > ' || c.name
            FROM categories AS c
            INNER JOIN category_tree AS ct ON c.parent_id = ct.id
        )
        SELECT
            ct.id   AS category_id,
            ct.name AS category_name,
            ct.full_path
        FROM category_tree AS ct
        WHERE ct.id NOT IN (SELECT parent_id FROM categories WHERE parent_id IS NOT NULL)
        ORDER BY ct.full_path;
        ```

    === "MySQL"
        ```sql
        WITH RECURSIVE category_tree AS (
            SELECT
                id,
                name,
                parent_id,
                name AS full_path
            FROM categories
            WHERE parent_id IS NULL

            UNION ALL

            SELECT
                c.id,
                c.name,
                c.parent_id,
                CONCAT(ct.full_path, ' > ', c.name)
            FROM categories AS c
            INNER JOIN category_tree AS ct ON c.parent_id = ct.id
        )
        SELECT
            ct.id   AS category_id,
            ct.name AS category_name,
            ct.full_path
        FROM category_tree AS ct
        WHERE ct.id NOT IN (SELECT parent_id FROM categories WHERE parent_id IS NOT NULL)
        ORDER BY ct.full_path;
        ```

### Exercise 4
Use a CTE to compare each category's average product price against the overall average. Return `category_name`, `avg_price`, `overall_avg`, and `diff_from_overall`. Use one CTE for the overall average and a `CROSS JOIN` in the main query.

??? success "Answer"
    ```sql
    WITH overall AS (
        SELECT ROUND(AVG(price), 2) AS overall_avg
        FROM products
        WHERE is_active = 1
    )
    SELECT
        cat.name AS category_name,
        ROUND(AVG(p.price), 2) AS avg_price,
        o.overall_avg,
        ROUND(AVG(p.price) - o.overall_avg, 2) AS diff_from_overall
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    CROSS JOIN overall AS o
    WHERE p.is_active = 1
    GROUP BY cat.id, cat.name, o.overall_avg
    ORDER BY avg_price DESC;
    ```

### Exercise 5
Use multiple CTEs to find the share of each payment method in monthly revenue for 2024. CTE 1: monthly amount per payment method. CTE 2: monthly total. Main query: return `year_month`, `method`, `amount`, `monthly_total`, and `pct`.

??? success "Answer"
    === "SQLite"
        ```sql
        WITH method_monthly AS (
            SELECT
                SUBSTR(p.paid_at, 1, 7) AS year_month,
                p.method,
                SUM(p.amount) AS amount
            FROM payments AS p
            INNER JOIN orders AS o ON p.order_id = o.id
            WHERE p.paid_at LIKE '2024%'
              AND p.status = 'completed'
            GROUP BY SUBSTR(p.paid_at, 1, 7), p.method
        ),
        monthly_total AS (
            SELECT
                year_month,
                SUM(amount) AS total
            FROM method_monthly
            GROUP BY year_month
        )
        SELECT
            mm.year_month,
            mm.method,
            mm.amount,
            mt.total AS monthly_total,
            ROUND(100.0 * mm.amount / mt.total, 1) AS pct
        FROM method_monthly AS mm
        INNER JOIN monthly_total AS mt ON mm.year_month = mt.year_month
        ORDER BY mm.year_month, mm.amount DESC;
        ```

    === "MySQL"
        ```sql
        WITH method_monthly AS (
            SELECT
                DATE_FORMAT(p.paid_at, '%Y-%m') AS year_month,
                p.method,
                SUM(p.amount) AS amount
            FROM payments AS p
            INNER JOIN orders AS o ON p.order_id = o.id
            WHERE p.paid_at >= '2024-01-01'
              AND p.paid_at <  '2025-01-01'
              AND p.status = 'completed'
            GROUP BY DATE_FORMAT(p.paid_at, '%Y-%m'), p.method
        ),
        monthly_total AS (
            SELECT
                year_month,
                SUM(amount) AS total
            FROM method_monthly
            GROUP BY year_month
        )
        SELECT
            mm.year_month,
            mm.method,
            mm.amount,
            mt.total AS monthly_total,
            ROUND(100.0 * mm.amount / mt.total, 1) AS pct
        FROM method_monthly AS mm
        INNER JOIN monthly_total AS mt ON mm.year_month = mt.year_month
        ORDER BY mm.year_month, mm.amount DESC;
        ```

    === "PostgreSQL"
        ```sql
        WITH method_monthly AS (
            SELECT
                TO_CHAR(p.paid_at, 'YYYY-MM') AS year_month,
                p.method,
                SUM(p.amount) AS amount
            FROM payments AS p
            INNER JOIN orders AS o ON p.order_id = o.id
            WHERE p.paid_at >= '2024-01-01'
              AND p.paid_at <  '2025-01-01'
              AND p.status = 'completed'
            GROUP BY TO_CHAR(p.paid_at, 'YYYY-MM'), p.method
        ),
        monthly_total AS (
            SELECT
                year_month,
                SUM(amount) AS total
            FROM method_monthly
            GROUP BY year_month
        )
        SELECT
            mm.year_month,
            mm.method,
            mm.amount,
            mt.total AS monthly_total,
            ROUND(100.0 * mm.amount / mt.total, 1) AS pct
        FROM method_monthly AS mm
        INNER JOIN monthly_total AS mt ON mm.year_month = mt.year_month
        ORDER BY mm.year_month, mm.amount DESC;
        ```

### Exercise 6
Combine a CTE with a window function to find the top 2 highest-rated products per category. Return `category_name`, `product_name`, `avg_rating`, `review_count`, and `rnk`. Only include products with at least 3 reviews.

??? success "Answer"
    ```sql
    WITH product_ratings AS (
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            cat.name AS category_name,
            p.category_id,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(r.id) AS review_count
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        INNER JOIN reviews AS r ON r.product_id = p.id
        GROUP BY p.id, p.name, cat.name, p.category_id
        HAVING COUNT(r.id) >= 3
    ),
    ranked AS (
        SELECT
            category_name,
            product_name,
            avg_rating,
            review_count,
            RANK() OVER (
                PARTITION BY category_id
                ORDER BY avg_rating DESC
            ) AS rnk
        FROM product_ratings
    )
    SELECT category_name, product_name, avg_rating, review_count, rnk
    FROM ranked
    WHERE rnk <= 2
    ORDER BY category_name, rnk;
    ```

### Exercise 7
Use a recursive CTE to generate a sequence of month numbers from 1 to 12, then LEFT JOIN with orders to get the order count for each month of 2024. Months with no orders should show 0. Return `month_num`, `year_month`, and `order_count`.

??? success "Answer"
    === "SQLite"
        ```sql
        WITH RECURSIVE months AS (
            SELECT 1 AS month_num
            UNION ALL
            SELECT month_num + 1
            FROM months
            WHERE month_num < 12
        )
        SELECT
            m.month_num,
            '2024-' || SUBSTR('0' || m.month_num, -2) AS year_month,
            COUNT(o.id) AS order_count
        FROM months AS m
        LEFT JOIN orders AS o
            ON SUBSTR(o.ordered_at, 1, 7) = '2024-' || SUBSTR('0' || m.month_num, -2)
            AND o.status NOT IN ('cancelled', 'returned')
        GROUP BY m.month_num
        ORDER BY m.month_num;
        ```

    === "MySQL"
        ```sql
        WITH RECURSIVE months AS (
            SELECT 1 AS month_num
            UNION ALL
            SELECT month_num + 1
            FROM months
            WHERE month_num < 12
        )
        SELECT
            m.month_num,
            CONCAT('2024-', LPAD(m.month_num, 2, '0')) AS year_month,
            COUNT(o.id) AS order_count
        FROM months AS m
        LEFT JOIN orders AS o
            ON DATE_FORMAT(o.ordered_at, '%Y-%m') = CONCAT('2024-', LPAD(m.month_num, 2, '0'))
            AND o.status NOT IN ('cancelled', 'returned')
        GROUP BY m.month_num
        ORDER BY m.month_num;
        ```

    === "PostgreSQL"
        ```sql
        WITH RECURSIVE months AS (
            SELECT 1 AS month_num
            UNION ALL
            SELECT month_num + 1
            FROM months
            WHERE month_num < 12
        )
        SELECT
            m.month_num,
            '2024-' || LPAD(m.month_num::text, 2, '0') AS year_month,
            COUNT(o.id) AS order_count
        FROM months AS m
        LEFT JOIN orders AS o
            ON TO_CHAR(o.ordered_at, 'YYYY-MM') = '2024-' || LPAD(m.month_num::text, 2, '0')
            AND o.status NOT IN ('cancelled', 'returned')
        GROUP BY m.month_num
        ORDER BY m.month_num;
        ```

### Exercise 8
Use a recursive CTE to walk the staff org chart and find each manager's depth level and direct report count. Return `manager_name`, `level`, and `direct_reports`. Only include staff who have at least one direct report.

??? success "Answer"
    === "SQLite / PostgreSQL"
        ```sql
        WITH RECURSIVE org AS (
            SELECT id, name, manager_id, 0 AS level
            FROM staff
            WHERE manager_id IS NULL

            UNION ALL

            SELECT s.id, s.name, s.manager_id, o.level + 1
            FROM staff AS s
            INNER JOIN org AS o ON s.manager_id = o.id
        )
        SELECT
            m.name AS manager_name,
            m.level,
            COUNT(s.id) AS direct_reports
        FROM org AS m
        LEFT JOIN staff AS s ON s.manager_id = m.id
        GROUP BY m.id, m.name, m.level
        HAVING COUNT(s.id) > 0
        ORDER BY m.level, direct_reports DESC;
        ```

    === "MySQL"
        ```sql
        WITH RECURSIVE org AS (
            SELECT id, name, manager_id, 0 AS level
            FROM staff
            WHERE manager_id IS NULL

            UNION ALL

            SELECT s.id, s.name, s.manager_id, o.level + 1
            FROM staff AS s
            INNER JOIN org AS o ON s.manager_id = o.id
        )
        SELECT
            m.name AS manager_name,
            m.level,
            COUNT(s.id) AS direct_reports
        FROM org AS m
        LEFT JOIN staff AS s ON s.manager_id = m.id
        GROUP BY m.id, m.name, m.level
        HAVING COUNT(s.id) > 0
        ORDER BY m.level, direct_reports DESC;
        ```

### Exercise 9
Chain 3 CTEs to build a "product performance dashboard". CTE 1: total units sold and revenue per product. CTE 2: average review rating per product. CTE 3: JOIN both. Main query: return `product_name`, `units_sold`, `revenue`, and `avg_rating`, showing the top 10 by revenue.

??? success "Answer"
    ```sql
    WITH sales AS (
        SELECT
            oi.product_id,
            SUM(oi.quantity)              AS units_sold,
            SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.status IN ('delivered', 'confirmed')
        GROUP BY oi.product_id
    ),
    ratings AS (
        SELECT
            product_id,
            ROUND(AVG(rating), 2) AS avg_rating
        FROM reviews
        GROUP BY product_id
    ),
    combined AS (
        SELECT
            p.name AS product_name,
            COALESCE(s.units_sold, 0) AS units_sold,
            COALESCE(s.revenue, 0)    AS revenue,
            r.avg_rating
        FROM products AS p
        LEFT JOIN sales   AS s ON p.id = s.product_id
        LEFT JOIN ratings AS r ON p.id = r.product_id
        WHERE p.is_active = 1
    )
    SELECT product_name, units_sold, revenue, avg_rating
    FROM combined
    ORDER BY revenue DESC
    LIMIT 10;
    ```

### Exercise 10
Use a recursive CTE to walk the category tree, then aggregate the number of subcategories and products under each root (top-level) category. Return `root_category`, `subcategory_count`, and `product_count`.

??? success "Answer"
    === "SQLite / PostgreSQL"
        ```sql
        WITH RECURSIVE tree AS (
            SELECT id, name AS root_name, id AS root_id
            FROM categories
            WHERE parent_id IS NULL

            UNION ALL

            SELECT c.id, t.root_name, t.root_id
            FROM categories AS c
            INNER JOIN tree AS t ON c.parent_id = t.id
        )
        SELECT
            t.root_name AS root_category,
            COUNT(DISTINCT t.id) - 1 AS subcategory_count,
            COUNT(DISTINCT p.id)     AS product_count
        FROM tree AS t
        LEFT JOIN products AS p ON p.category_id = t.id
        GROUP BY t.root_id, t.root_name
        ORDER BY product_count DESC;
        ```

    === "MySQL"
        ```sql
        WITH RECURSIVE tree AS (
            SELECT id, name AS root_name, id AS root_id
            FROM categories
            WHERE parent_id IS NULL

            UNION ALL

            SELECT c.id, t.root_name, t.root_id
            FROM categories AS c
            INNER JOIN tree AS t ON c.parent_id = t.id
        )
        SELECT
            t.root_name AS root_category,
            COUNT(DISTINCT t.id) - 1 AS subcategory_count,
            COUNT(DISTINCT p.id)     AS product_count
        FROM tree AS t
        LEFT JOIN products AS p ON p.category_id = t.id
        GROUP BY t.root_id, t.root_name
        ORDER BY product_count DESC;
        ```

---
Next: [Lesson 20: EXISTS and Correlated Subqueries](20-exists.md)
