# CS Performance Analysis

!!! info "Tables"

    `complaints` — Complaints (type, priority)  

    `staff` — Staff (dept, role, manager)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `returns` — Returns (reason, status)  



!!! abstract "Concepts"

    `JULIANDAY`, `CASE`, `Window Functions`, `CTE`, `Pivot`



### 1. Complaint Category Summary


The CS team lead wants a 2025 complaint summary.
Show count, resolution rate, and average resolution time by category.


**Hint 1:** - Use `complaints.category`, `status`, `created_at`, `resolved_at`
- Resolution rate: count of `status IN ('resolved', 'closed')` / total
- Resolution time: `JULIANDAY(resolved_at) - JULIANDAY(created_at)`



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


    **Result** (7 rows)

    | category | total_count | resolved_count | resolution_rate_pct | avg_resolution_days |
    |---|---|---|---|---|
    | general_inquiry | 378 | 356 | 94.20 | 2.00 |
    | price_inquiry | 140 | 129 | 92.10 | 1.80 |
    | delivery_issue | 135 | 130 | 96.30 | 0.7 |
    | refund_request | 92 | 87 | 94.60 | 0.7 |
    | product_defect | 74 | 70 | 94.60 | 0.7 |
    | wrong_item | 42 | 41 | 97.60 | 0.4 |
    | exchange_request | 34 | 34 | 100.00 | 1.20 |


---


### 2. CS Staff Performance Comparison


Show each staff member's case count, resolution rate, average processing time,
and customer count. Display team averages for comparison.


**Hint 1:** - JOIN `complaints.staff_id` -> `staff`
- Show NULL staff_id as "Unassigned"
- Use window functions to show team averages in each row



??? success "Answer"
    ```sql
    WITH staff_metrics AS (
        SELECT
            COALESCE(s.name, '미배정') AS staff_name,
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
        GROUP BY COALESCE(s.name, '미배정')
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


    **Result** (5 rows)

    | staff_name | case_count | customer_count | resolution_rate | avg_days | team_avg_cases | team_avg_rate | team_avg_days |
    |---|---|---|---|---|---|---|---|
    | Michael Thomas | 178 | 167 | 96.10 | 1.30 | 179.00 | 94.60 | 1.40 |
    | Michael Mcguire | 183 | 178 | 95.60 | 1.50 | 179.00 | 94.60 | 1.40 |
    | Nicole Hamilton | 177 | 174 | 94.90 | 1.60 | 179.00 | 94.60 | 1.40 |
    | Jaime Phelps | 183 | 175 | 93.40 | 1.30 | 179.00 | 94.60 | 1.40 |
    | Jonathan Smith | 174 | 168 | 93.10 | 1.50 | 179.00 | 94.60 | 1.40 |


---


### 3. Return Reason Analysis


Show return count, percentage, and average refund by reason.
Also analyze which reasons are common per product category.


**Hint 1:** - Classify by `returns.reason`
- JOIN chain: `returns` -> `orders` -> `order_items` -> `products` -> `categories`
- Use `returns.refund_amount` for refund amounts



??? success "Answer"
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


    **Result** (6 rows)

    | reason | return_count | pct | avg_refund |
    |---|---|---|---|
    | change_of_mind | 343 | 34.30 | 1,160,924.02 |
    | defective | 263 | 26.30 | 1,278,164.64 |
    | damaged_in_transit | 165 | 16.50 | 1,043,268.48 |
    | wrong_item | 95 | 9.50 | 1,128,795.79 |
    | not_as_described | 88 | 8.80 | 1,290,557.95 |
    | late_delivery | 46 | 4.60 | 741,530.43 |


---


### 4. Monthly CS Trend and Complaint-to-Order Ratio


Show 2024 monthly order count, complaint count, return count,
and complaint-to-order ratio.


**Hint 1:** - Prepare monthly counts from each table as CTEs
- JOIN by month (SUBSTR)
- Complaint rate = complaint count / order count * 100



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


    **Result** (top 7 of 12 rows)

    | year_month | order_count | complaint_count | return_count | complaint_rate_pct | return_rate_pct |
    |---|---|---|---|---|---|
    | 2024-01 | 346 | 43 | 9 | 12.43 | 2.60 |
    | 2024-02 | 465 | 40 | 14 | 8.60 | 3.01 |
    | 2024-03 | 601 | 50 | 23 | 8.32 | 3.83 |
    | 2024-04 | 506 | 61 | 12 | 12.06 | 2.37 |
    | 2024-05 | 415 | 47 | 10 | 11.33 | 2.41 |
    | 2024-06 | 415 | 49 | 11 | 11.81 | 2.65 |
    | 2024-07 | 414 | 49 | 6 | 11.84 | 1.45 |


---


### 5. Repeat Complainers and Escalation Targets


Identify customers with 3+ complaints who still have unresolved cases.
Show total complaints, open count, total spend, and last complaint date.


**Hint 1:** - Aggregate complaint stats per customer first
- Filter with `HAVING` for 3+ complaints and open cases > 0
- JOIN with `orders` for purchase value



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
            WHEN c.grade IN ('VIP', 'GOLD') THEN '우선 처리'
            WHEN cs.open_count >= 3          THEN '긴급'
            ELSE '일반'
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


    **Result** (top 7 of 91 rows)

    | customer_name | grade | email | total_complaints | open_count | last_complaint_date | total_spent | priority |
    |---|---|---|---|---|---|---|---|
    | Brenda Garcia | VIP | user162@testmail.kr | 24 | 1 | 2025-03-25 05:20:31 | 254,525,838.00 | 우선 처리 |
    | Courtney Huff | VIP | user356@testmail.kr | 19 | 2 | 2024-08-28 10:20:59 | 248,498,783.00 | 우선 처리 |
    | Gabriel Walters | VIP | user98@testmail.kr | 29 | 1 | 2024-10-07 08:05:39 | 248,168,491.00 | 우선 처리 |
    | James Banks | VIP | user227@testmail.kr | 13 | 1 | 2025-05-10 11:44:37 | 244,859,844.00 | 우선 처리 |
    | David York | GOLD | user1581@testmail.kr | 11 | 1 | 2025-08-30 11:40:39 | 208,621,108.00 | 우선 처리 |
    | Terri Jones | VIP | user33@testmail.kr | 11 | 1 | 2023-08-06 03:15:06 | 174,223,341.00 | 우선 처리 |
    | Adam Moore | VIP | user3@testmail.kr | 9 | 1 | 2025-12-09 09:46:23 | 164,856,056.00 | 우선 처리 |


---


### 6. Bonus: Staff Monthly Performance Pivot


Create a pivot table of resolved cases per CS staff member for 2024.
Format: 12 months (columns) x staff (rows).


**Hint 1:** - 12 columns with `SUM(CASE WHEN SUBSTR(...) = 'MM' AND status ... THEN 1 ELSE 0 END)`
- `LEFT JOIN staff` to include unassigned



??? success "Answer"
    ```sql
    SELECT
        COALESCE(s.name, '미배정') AS staff_name,
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
    GROUP BY COALESCE(s.name, '미배정')
    ORDER BY total DESC;
    ```


    **Result** (5 rows)

    | staff_name | jan | feb | mar | apr | may | jun | jul | aug | sep | oct | nov | dec | total |
    |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
    | Michael Thomas | 7 | 9 | 11 | 11 | 12 | 6 | 15 | 14 | 8 | 8 | 14 | 9 | 124 |
    | Nicole Hamilton | 9 | 8 | 12 | 12 | 8 | 10 | 8 | 7 | 17 | 13 | 13 | 5 | 122 |
    | Jaime Phelps | 8 | 10 | 6 | 9 | 8 | 11 | 7 | 14 | 13 | 13 | 8 | 10 | 117 |
    | Jonathan Smith | 6 | 10 | 6 | 14 | 7 | 9 | 10 | 10 | 9 | 10 | 12 | 9 | 112 |
    | Michael Mcguire | 12 | 2 | 10 | 13 | 10 | 11 | 8 | 4 | 12 | 6 | 10 | 11 | 109 |


---
