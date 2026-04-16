# Customer Segmentation

!!! info "Tables"

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `reviews` — Reviews (rating, content)  



!!! abstract "Concepts"

    `RFM`, `NTILE`, `Window Functions`, `CTE`, `Cohort Analysis`, `JULIANDAY`



### 1. RFM Basics: Customer Key Metrics


The marketing team needs RFM (Recency, Frequency, Monetary) metrics for customer segmentation.
Calculate last order date, total order count, and total spend per customer.
Exclude cancelled/returned orders.


**Hint 1:** - Use `MAX(ordered_at)` for Recency
- `COUNT(*)` for Frequency, `SUM(total_amount)` for Monetary
- Sort by total spend descending



??? success "Answer"
    ```sql
    SELECT
        c.id            AS customer_id,
        c.name          AS customer_name,
        c.grade,
        MAX(o.ordered_at)   AS last_order_date,
        COUNT(*)            AS order_count,
        ROUND(SUM(o.total_amount), 2) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | customer_id | customer_name | grade | last_order_date | order_count | total_spent |
    |---|---|---|---|---|---|
    | 226 | Allen Snyder | VIP | 2025-12-21 21:52:24 | 303 | 403,448,758.00 |
    | 97 | Jason Rivera | VIP | 2025-12-28 11:37:58 | 342 | 366,385,931.00 |
    | 162 | Brenda Garcia | VIP | 2025-12-20 10:21:05 | 249 | 253,180,338.00 |
    | 356 | Courtney Huff | VIP | 2025-10-24 16:44:53 | 223 | 244,604,910.00 |
    | 549 | Ronald Arellano | VIP | 2025-12-04 12:11:17 | 219 | 235,775,349.00 |
    | 227 | James Banks | VIP | 2025-12-19 22:54:22 | 230 | 234,708,853.00 |
    | 98 | Gabriel Walters | VIP | 2025-11-29 11:04:23 | 275 | 230,165,991.00 |


---


### 2. RFM Quartile Segments


Divide customers into quartiles based on RFM metrics.
Recency: higher score for more recent. Frequency and Monetary: higher score for larger values.


**Hint 1:** - Use `NTILE(4)` to divide each metric into quartiles
- Recency: `ORDER BY last_order_date ASC` (NTILE 4 = most recent)
- Frequency, Monetary: `ORDER BY ... ASC` (NTILE 4 = largest)
- Use CTEs step-by-step



??? success "Answer"
    ```sql
    WITH rfm_raw AS (
        SELECT
            c.id AS customer_id,
            c.name,
            c.grade,
            MAX(o.ordered_at)       AS last_order_date,
            COUNT(*)                AS frequency,
            ROUND(SUM(o.total_amount), 2) AS monetary
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    ),
    rfm_scored AS (
        SELECT
            customer_id, name, grade,
            last_order_date, frequency, monetary,
            NTILE(4) OVER (ORDER BY last_order_date ASC)  AS r_score,
            NTILE(4) OVER (ORDER BY frequency ASC)        AS f_score,
            NTILE(4) OVER (ORDER BY monetary ASC)         AS m_score
        FROM rfm_raw
    )
    SELECT
        customer_id, name, grade,
        last_order_date, frequency, monetary,
        r_score, f_score, m_score,
        r_score + f_score + m_score AS rfm_total
    FROM rfm_scored
    ORDER BY rfm_total DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | customer_id | name | grade | last_order_date | frequency | monetary | r_score | f_score | m_score | rfm_total |
    |---|---|---|---|---|---|---|---|---|---|
    | 486 | Hannah Norton | GOLD | 2025-11-13 20:04:57 | 37 | 51,239,619.00 | 4 | 4 | 4 | 12 |
    | 10 | John Stark | GOLD | 2025-11-14 12:11:23 | 26 | 29,486,071.00 | 4 | 4 | 4 | 12 |
    | 1490 | April Lopez | VIP | 2025-11-14 14:54:42 | 50 | 36,214,359.00 | 4 | 4 | 4 | 12 |
    | 647 | Leslie Mccoy | VIP | 2025-11-14 19:43:56 | 33 | 29,875,991.00 | 4 | 4 | 4 | 12 |
    | 1241 | Cheryl Garcia | BRONZE | 2025-11-15 09:53:27 | 18 | 13,800,255.00 | 4 | 4 | 4 | 12 |
    | 256 | Jessica Craig | GOLD | 2025-11-15 11:09:38 | 22 | 26,613,941.00 | 4 | 4 | 4 | 12 |
    | 2328 | Julie Hamilton | VIP | 2025-11-15 22:09:51 | 24 | 26,820,326.00 | 4 | 4 | 4 | 12 |


---


### 3. Churn Risk Detection


The CRM team requests a list of high churn-risk customers.
Find customers with 5+ past orders whose last order was over 1 year ago.
Show last order date, total orders, total spend, and days since last order.


**Hint 1:** - Use `JULIANDAY('2025-12-31') - JULIANDAY(MAX(ordered_at))` for days elapsed
- Filter with `HAVING` for order count >= 5
- Add condition for days >= 365



??? success "Answer"
    ```sql
    SELECT
        c.id            AS customer_id,
        c.name,
        c.grade,
        c.email,
        MAX(o.ordered_at)   AS last_order_date,
        COUNT(*)            AS order_count,
        ROUND(SUM(o.total_amount), 2) AS total_spent,
        CAST(JULIANDAY('2025-12-31') - JULIANDAY(MAX(o.ordered_at)) AS INTEGER)
            AS days_since_last_order
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY c.id, c.name, c.grade, c.email
    HAVING COUNT(*) >= 5
       AND JULIANDAY('2025-12-31') - JULIANDAY(MAX(o.ordered_at)) >= 365
    ORDER BY total_spent DESC;
    ```


    **Result** (top 7 of 288 rows)

    | customer_id | name | grade | email | last_order_date | order_count | total_spent | days_since_last_order |
    |---|---|---|---|---|---|---|---|
    | 70 | Robert Turner | BRONZE | user70@testmail.kr | 2024-10-26 22:15:57 | 94 | 67,311,037.00 | 430 |
    | 1101 | Alexandra Elliott | BRONZE | user1101@testmail.kr | 2024-12-01 12:26:06 | 52 | 62,415,347.00 | 394 |
    | 514 | Steven Johnson | BRONZE | user514@testmail.kr | 2024-03-28 19:31:36 | 5 | 52,141,700.00 | 642 |
    | 1660 | Thomas Phillips | BRONZE | user1660@testmail.kr | 2024-10-01 22:51:13 | 21 | 48,143,594.00 | 455 |
    | 72 | Michael Hutchinson | BRONZE | user72@testmail.kr | 2024-12-02 16:19:45 | 51 | 46,080,909.00 | 393 |
    | 1322 | Donald Landry | BRONZE | user1322@testmail.kr | 2023-12-31 12:30:32 | 5 | 41,506,100.00 | 730 |
    | 812 | Ryan Perry | BRONZE | user812@testmail.kr | 2024-12-22 14:49:30 | 36 | 40,546,071.00 | 373 |


---


### 4. Behavioral Patterns by Grade


Analyze how purchase behavior differs by customer grade (VIP, GOLD, SILVER, BRONZE).
Compare average order value, average order count, review rate, and average review rating.


**Hint 1:** - Prepare order stats and review stats as separate CTEs
- Review rate = reviewers count / total customer count
- `GROUP BY` grade



??? success "Answer"
    ```sql
    WITH order_stats AS (
        SELECT
            c.grade,
            COUNT(DISTINCT c.id) AS customer_count,
            COUNT(o.id)          AS total_orders,
            ROUND(AVG(o.total_amount), 2)        AS avg_order_value,
            ROUND(1.0 * COUNT(o.id) / COUNT(DISTINCT c.id), 1) AS avg_orders_per_customer
        FROM customers AS c
        LEFT JOIN orders AS o
            ON c.id = o.customer_id
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.grade
    ),
    review_stats AS (
        SELECT
            c.grade,
            COUNT(DISTINCT r.customer_id) AS reviewers,
            ROUND(AVG(r.rating), 2)       AS avg_rating
        FROM customers AS c
        LEFT JOIN reviews AS r ON c.id = r.customer_id
        GROUP BY c.grade
    )
    SELECT
        os.grade,
        os.customer_count,
        os.avg_orders_per_customer,
        os.avg_order_value,
        rs.reviewers,
        ROUND(100.0 * rs.reviewers / os.customer_count, 1) AS review_rate_pct,
        rs.avg_rating
    FROM order_stats AS os
    INNER JOIN review_stats AS rs ON os.grade = rs.grade
    ORDER BY
        CASE os.grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
            ELSE 5
        END;
    ```


    **Result** (4 rows)

    | grade | customer_count | avg_orders_per_customer | avg_order_value | reviewers | review_rate_pct | avg_rating |
    |---|---|---|---|---|---|---|
    | VIP | 368 | 38.20 | 1,093,231.76 | 339 | 92.10 | 3.91 |
    | GOLD | 524 | 15.10 | 1,011,117.46 | 426 | 81.30 | 3.89 |
    | SILVER | 479 | 10.70 | 921,070.65 | 355 | 74.10 | 3.89 |
    | BRONZE | 3859 | 2.00 | 878,974.74 | 779 | 20.20 | 3.93 |


---


### 5. Cohort Analysis: Retention by Signup Year


Show customer count by signup year and the percentage who made repeat purchases
within 1 year and 2 years after signup.


**Hint 1:** - Signup year = `SUBSTR(created_at, 1, 4)`
- Check for orders within 1/2 years after signup
- Conditional aggregation `COUNT(DISTINCT CASE WHEN ... THEN customer_id END)`



??? success "Answer"
    ```sql
    WITH cohort AS (
        SELECT
            id AS customer_id,
            SUBSTR(created_at, 1, 4) AS join_year,
            created_at
        FROM customers
    ),
    cohort_orders AS (
        SELECT
            co.customer_id,
            co.join_year,
            co.created_at AS join_date,
            o.ordered_at
        FROM cohort AS co
        INNER JOIN orders AS o ON co.customer_id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        join_year,
        COUNT(DISTINCT customer_id) AS cohort_size,
        COUNT(DISTINCT CASE
            WHEN ordered_at <= DATE(join_date, '+1 year') THEN customer_id
        END) AS active_year_1,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN ordered_at <= DATE(join_date, '+1 year') THEN customer_id
        END) / COUNT(DISTINCT customer_id), 1) AS retention_1y_pct,
        COUNT(DISTINCT CASE
            WHEN ordered_at > DATE(join_date, '+1 year')
             AND ordered_at <= DATE(join_date, '+2 years') THEN customer_id
        END) AS active_year_2,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN ordered_at > DATE(join_date, '+1 year')
             AND ordered_at <= DATE(join_date, '+2 years') THEN customer_id
        END) / COUNT(DISTINCT customer_id), 1) AS retention_2y_pct
    FROM cohort_orders
    GROUP BY join_year
    HAVING CAST(join_year AS INTEGER) <= 2023
    ORDER BY join_year;
    ```


    **Result** (top 7 of 8 rows)

    | join_year | cohort_size | active_year_1 | retention_1y_pct | active_year_2 | retention_2y_pct |
    |---|---|---|---|---|---|
    | 2016 | 52 | 49 | 94.20 | 45 | 86.50 |
    | 2017 | 83 | 75 | 90.40 | 73 | 88.00 |
    | 2018 | 155 | 134 | 86.50 | 138 | 89.00 |
    | 2019 | 217 | 195 | 89.90 | 193 | 88.90 |
    | 2020 | 348 | 311 | 89.40 | 290 | 83.30 |
    | 2021 | 499 | 403 | 80.80 | 348 | 69.70 |
    | 2022 | 386 | 298 | 77.20 | 273 | 70.70 |


---


### 6. Bonus: RFM Marketing Segments


Classify customers into 5 marketing segments using RFM scores:
Champions(R>=3,F>=3,M>=3), Loyal(F>=3,M>=3),
Potential Loyal(R>=3,F<=2), At Risk(R<=2,F>=2), Dormant(R=1,F=1).
Show customer count and average monetary per segment.


**Hint 1:** - First create a CTE calculating RFM scores
- Use `CASE` to classify segments (condition order matters)
- `GROUP BY` segment



??? success "Answer"
    ```sql
    WITH rfm_raw AS (
        SELECT
            c.id AS customer_id,
            MAX(o.ordered_at)       AS last_order_date,
            COUNT(*)                AS frequency,
            SUM(o.total_amount)     AS monetary
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id
    ),
    rfm_scored AS (
        SELECT
            customer_id, frequency, monetary,
            NTILE(4) OVER (ORDER BY last_order_date ASC)  AS r,
            NTILE(4) OVER (ORDER BY frequency ASC)        AS f,
            NTILE(4) OVER (ORDER BY monetary ASC)         AS m
        FROM rfm_raw
    ),
    segmented AS (
        SELECT *,
            CASE
                WHEN r >= 3 AND f >= 3 AND m >= 3 THEN '챔피언'
                WHEN f >= 3 AND m >= 3             THEN '충성 고객'
                WHEN r >= 3 AND f <= 2             THEN '잠재 충성'
                WHEN r <= 2 AND f >= 2             THEN '이탈 위험'
                WHEN r = 1  AND f = 1              THEN '휴면'
                ELSE '기타'
            END AS segment
        FROM rfm_scored
    )
    SELECT
        segment,
        COUNT(*)                        AS customer_count,
        ROUND(AVG(monetary), 2)         AS avg_monetary,
        ROUND(AVG(frequency), 1)        AS avg_frequency
    FROM segmented
    GROUP BY segment
    ORDER BY avg_monetary DESC;
    ```


    **Result** (6 rows)

    | segment | customer_count | avg_monetary | avg_frequency |
    |---|---|---|---|
    | 챔피언 | 787 | 30,627,193.48 | 29.50 |
    | 충성 고객 | 488 | 15,686,318.24 | 15.00 |
    | 이탈 위험 | 465 | 2,994,776.44 | 3.80 |
    | 잠재 충성 | 549 | 2,092,261.26 | 2.50 |
    | 기타 | 258 | 1,280,113.41 | 2.60 |
    | 휴면 | 246 | 566,714.23 | 1.30 |


---
