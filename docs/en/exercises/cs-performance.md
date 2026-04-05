# Exercise: CS Performance Analysis

Analyze customer service data to measure team performance and identify improvement areas. Tackle five questions covering inquiry trends, staff performance, return patterns, complaint-to-order ratios, and escalation targets.

---

## Question 1 — Inquiry Type Breakdown

**Business question:** The CS team lead wants a snapshot of inquiries for the past year (2025). Show the count, resolution rate (resolved/closed), and average resolution time per inquiry type.

**Hints:**

- Use `complaints` table: `category`, `status`, `created_at`, `resolved_at`
- Resolution rate: count of `status IN ('resolved', 'closed')` / total
- Resolution time: `JULIANDAY(resolved_at) - JULIANDAY(created_at)`
- NULL `resolved_at` means unresolved

??? success "Answer"
    ```sql
    SELECT
        category,
        COUNT(*) AS total_count,
        SUM(CASE WHEN status IN ('resolved', 'closed') THEN 1 ELSE 0 END)
            AS resolved_count,
        ROUND(100.0 * SUM(CASE WHEN status IN ('resolved', 'closed') THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS resolution_rate_pct,
        ROUND(AVG(CASE
            WHEN resolved_at IS NOT NULL
            THEN JULIANDAY(resolved_at) - JULIANDAY(created_at)
        END), 1) AS avg_resolution_days
    FROM complaints
    WHERE created_at LIKE '2025%'
    GROUP BY category
    ORDER BY total_count DESC;
    ```

    **Expected insight:** Shipping inquiries are likely the most common. Refund requests may have the longest resolution time despite lower volume. Low-resolution types need process improvement.

---

## Question 2 — Staff Performance Comparison

**Business question:** HR wants to compare individual CS staff performance. Show each staff member's case count, resolution rate, average resolution time, and unique customers handled. Include team averages for comparison.

**Hints:**

- JOIN `complaints.staff_id` → `staff`
- Show "Unassigned" for NULL `staff_id`
- Use window functions to add team averages in the same row

??? success "Answer"
    ```sql
    WITH staff_metrics AS (
        SELECT
            COALESCE(s.name, 'Unassigned') AS staff_name,
            COUNT(*) AS case_count,
            COUNT(DISTINCT comp.customer_id) AS customer_count,
            SUM(CASE WHEN comp.status IN ('resolved', 'closed') THEN 1 ELSE 0 END)
                AS resolved_count,
            ROUND(100.0 * SUM(CASE WHEN comp.status IN ('resolved', 'closed') THEN 1 ELSE 0 END)
                / COUNT(*), 1) AS resolution_rate,
            ROUND(AVG(CASE
                WHEN comp.resolved_at IS NOT NULL
                THEN JULIANDAY(comp.resolved_at) - JULIANDAY(comp.created_at)
            END), 1) AS avg_days
        FROM complaints AS comp
        LEFT JOIN staff AS s ON comp.staff_id = s.id
        WHERE comp.created_at LIKE '2025%'
        GROUP BY COALESCE(s.name, 'Unassigned')
    )
    SELECT
        staff_name,
        case_count,
        customer_count,
        resolution_rate,
        avg_days,
        ROUND(AVG(case_count) OVER (), 0)       AS team_avg_cases,
        ROUND(AVG(resolution_rate) OVER (), 1)   AS team_avg_rate,
        ROUND(AVG(avg_days) OVER (), 1)          AS team_avg_days
    FROM staff_metrics
    ORDER BY resolution_rate DESC;
    ```

    **Expected insight:** Top performers have high resolution rates and short resolution times. A high number of unassigned cases suggests the need for an auto-assignment system.

---

## Question 3 — Return Reason Analysis

**Business question:** The QA team wants to analyze return reasons to find improvement opportunities. Show the count, percentage, and average refund amount per return reason. Also break down by category.

**Hints:**

- Use `returns.reason` for classification
- JOIN: `returns` → `orders` → `order_items` → `products` → `categories`
- Use `returns.refund_amount` for refund calculations

??? success "Answer"
    **Overall summary:**

    ```sql
    SELECT
        r.reason,
        COUNT(*)                     AS return_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
        ROUND(AVG(r.refund_amount), 2) AS avg_refund
    FROM returns AS r
    GROUP BY r.reason
    ORDER BY return_count DESC;
    ```

    **Category-level detail:**

    ```sql
    SELECT
        cat.name AS category,
        r.reason,
        COUNT(*) AS return_count,
        ROUND(AVG(r.refund_amount), 2) AS avg_refund
    FROM returns AS r
    INNER JOIN orders      AS o   ON r.order_id   = o.id
    INNER JOIN order_items AS oi  ON o.id = oi.order_id
    INNER JOIN products    AS p   ON oi.product_id = p.id
    INNER JOIN categories  AS cat ON p.category_id = cat.id
    GROUP BY cat.name, r.reason
    HAVING return_count >= 3
    ORDER BY cat.name, return_count DESC;
    ```

    **Expected insight:** "Defective" is likely the most common reason. If high-value categories (laptops, monitors) show many "Not as expected" returns, product descriptions need improvement.

---

## Question 4 — Monthly CS Trends and Complaint-to-Order Ratio

**Business question:** The CS operations team wants to monitor monthly complaint and return trends relative to order volume. Show 2024 monthly order count, complaint count, return count, and complaint/return rates.

**Hints:**

- Prepare monthly counts from each table as CTEs
- JOIN by month (SUBSTR)
- Rate = complaints / orders × 100

??? success "Answer"
    ```sql
    WITH monthly_orders AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            COUNT(*) AS order_count
        FROM orders
        WHERE ordered_at LIKE '2024%'
        GROUP BY SUBSTR(ordered_at, 1, 7)
    ),
    monthly_complaints AS (
        SELECT
            SUBSTR(created_at, 1, 7) AS year_month,
            COUNT(*) AS complaint_count
        FROM complaints
        WHERE created_at LIKE '2024%'
        GROUP BY SUBSTR(created_at, 1, 7)
    ),
    monthly_returns AS (
        SELECT
            SUBSTR(requested_at, 1, 7) AS year_month,
            COUNT(*) AS return_count
        FROM returns
        WHERE requested_at LIKE '2024%'
        GROUP BY SUBSTR(requested_at, 1, 7)
    )
    SELECT
        mo.year_month,
        mo.order_count,
        COALESCE(mc.complaint_count, 0) AS complaint_count,
        COALESCE(mr.return_count, 0)    AS return_count,
        ROUND(100.0 * COALESCE(mc.complaint_count, 0) / mo.order_count, 2)
            AS complaint_rate_pct,
        ROUND(100.0 * COALESCE(mr.return_count, 0) / mo.order_count, 2)
            AS return_rate_pct
    FROM monthly_orders AS mo
    LEFT JOIN monthly_complaints AS mc ON mo.year_month = mc.year_month
    LEFT JOIN monthly_returns    AS mr ON mo.year_month = mr.year_month
    ORDER BY mo.year_month;
    ```

    **Expected insight:** A steady complaint rate is normal operations. A spike in a specific month likely indicates quality issues or shipping delays. Returns tend to increase in Jan–Feb due to holiday gift exchanges.

---

## Question 5 — Repeat Complainers and Escalation Targets

**Business question:** The CS manager wants to identify customers with 3+ complaints who still have unresolved cases as escalation targets. Show their total complaints, open cases, total spend, and last complaint date.

**Hints:**

- Aggregate complaint stats per customer first
- Unresolved: `status NOT IN ('resolved', 'closed')`
- `HAVING` for 3+ complaints with open cases
- JOIN `orders` for spend data

??? success "Answer"
    ```sql
    WITH complaint_summary AS (
        SELECT
            customer_id,
            COUNT(*) AS total_complaints,
            SUM(CASE WHEN status NOT IN ('resolved', 'closed') THEN 1 ELSE 0 END)
                AS open_count,
            MAX(created_at) AS last_complaint_date
        FROM complaints
        GROUP BY customer_id
        HAVING COUNT(*) >= 3
           AND SUM(CASE WHEN status NOT IN ('resolved', 'closed') THEN 1 ELSE 0 END) > 0
    ),
    customer_value AS (
        SELECT
            customer_id,
            ROUND(SUM(total_amount), 2) AS total_spent
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    )
    SELECT
        c.name          AS customer_name,
        c.grade,
        c.email,
        cs.total_complaints,
        cs.open_count,
        cs.last_complaint_date,
        COALESCE(cv.total_spent, 0) AS total_spent,
        CASE
            WHEN c.grade IN ('VIP', 'GOLD') THEN 'Priority'
            WHEN cs.open_count >= 3          THEN 'Urgent'
            ELSE 'Normal'
        END AS priority
    FROM complaint_summary AS cs
    INNER JOIN customers     AS c  ON cs.customer_id = c.id
    LEFT  JOIN customer_value AS cv ON cs.customer_id = cv.customer_id
    ORDER BY
        CASE
            WHEN c.grade IN ('VIP', 'GOLD') THEN 1
            WHEN cs.open_count >= 3          THEN 2
            ELSE 3
        END,
        cv.total_spent DESC;
    ```

    **Expected insight:** VIP/GOLD customers with unresolved complaints are the highest risk. Their churn would significantly impact revenue, so they need priority handling.

---

## Bonus Challenge

Create a **monthly performance pivot table** by CS staff for 2024. Rows = staff, columns = 12 months, cells = resolved case count. If a staff member's numbers drop toward year-end, it may signal overload.

??? success "Answer"
    ```sql
    SELECT
        COALESCE(s.name, 'Unassigned') AS staff_name,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='01' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS jan,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='02' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS feb,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='03' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS mar,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='04' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS apr,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='05' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS may,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='06' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS jun,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='07' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS jul,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='08' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS aug,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='09' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS sep,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='10' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS oct,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='11' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS nov,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='12' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS dec,
        SUM(CASE WHEN comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS total
    FROM complaints AS comp
    LEFT JOIN staff AS s ON comp.staff_id = s.id
    WHERE comp.created_at LIKE '2024%'
    GROUP BY COALESCE(s.name, 'Unassigned')
    ORDER BY total DESC;
    ```
