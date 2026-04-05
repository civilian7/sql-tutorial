# Exercise: Customer Segmentation

Analyze customer data to derive actionable segments for the marketing team. Tackle five questions covering RFM analysis, churn risk detection, grade-based behavior differences, and cohort retention.

---

## Question 1 — RFM Basics: Core Metrics per Customer

**Business question:** The marketing team needs each customer's RFM (Recency, Frequency, Monetary) metrics for segmentation. Calculate the last order date, total order count, and total spend per customer. Exclude cancelled/returned orders.

**Hints:**

- `MAX(ordered_at)` for Recency
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

    **Expected insight:** VIP/GOLD customers dominate the top, with a strong correlation between order count and monetary value.

---

## Question 2 — RFM Quartile Segmentation

**Business question:** Using the RFM metrics from Question 1, divide customers into quartiles (top 25%, 50%, 75%, bottom). Higher scores mean more recent, more frequent, and higher spending.

**Hints:**

- Use `NTILE(4)` for each metric
- Recency: `ORDER BY last_order_date ASC` (oldest first → NTILE 1 = least recent)
- Frequency/Monetary: `ORDER BY ... ASC` (lowest first → NTILE 4 = highest)
- Use CTEs step by step

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

    **Expected insight:** Customers with rfm_total 10–12 are your best. You may also discover "hidden VIPs" — low-grade customers with surprisingly high RFM scores.

---

## Question 3 — Churn Risk Detection

**Business question:** The CRM team needs a list of at-risk customers. Find customers who ordered 5+ times in the past but haven't ordered in over a year. Show their last order date, order count, total spend, and days since last order.

**Hints:**

- Use `JULIANDAY('2025-12-31') - JULIANDAY(MAX(ordered_at))` for days elapsed
- `HAVING` for order count ≥ 5
- Filter for days elapsed ≥ 365

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

    **Expected insight:** Many GOLD/SILVER customers appear in the churn risk list. The higher their historical spend, the more valuable a reactivation campaign would be.

---

## Question 4 — Behavior Patterns by Grade

**Business question:** Compare purchasing behavior across customer grades (VIP, GOLD, SILVER, BRONZE). Show average order value, average order count, review writing rate, and average review rating per grade.

**Hints:**

- Prepare order stats and review stats as separate CTEs
- Review rate = reviewers / total customers
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

    **Expected insight:** VIP customers have the highest order frequency and value, but GOLD may have a similar review rate. BRONZE customers tend to give lower ratings (possible dissatisfaction leading to churn).

---

## Question 5 — Cohort Analysis: Retention by Signup Year

**Business question:** Management wants to understand customer retention. Show the cohort size per signup year and the percentage of customers who made purchases within 1 year and 2 years after signup.

**Hints:**

- Signup year = `SUBSTR(created_at, 1, 4)`
- Check if orders exist within 1/2 years of signup date
- Conditional aggregation: `COUNT(DISTINCT CASE WHEN ... THEN customer_id END)`

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

    **Expected insight:** Earlier cohorts (2016–2017) show lower retention, while recent cohorts (2022–2023) have higher first-year retention, reflecting growth and improved customer experience.

---

## Bonus Challenge

Using the RFM scores from Question 2, classify customers into 5 marketing segments:

| Segment | Criteria |
|---------|----------|
| **Champions** | R≥3, F≥3, M≥3 |
| **Loyal** | F≥3, M≥3 (any R) |
| **Potential Loyal** | R≥3, F≤2 |
| **At Risk** | R≤2, F≥2 |
| **Hibernating** | R=1, F=1 |

Show the customer count and average monetary value per segment.

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
                WHEN r >= 3 AND f >= 3 AND m >= 3 THEN 'Champions'
                WHEN f >= 3 AND m >= 3             THEN 'Loyal'
                WHEN r >= 3 AND f <= 2             THEN 'Potential Loyal'
                WHEN r <= 2 AND f >= 2             THEN 'At Risk'
                WHEN r = 1  AND f = 1              THEN 'Hibernating'
                ELSE 'Other'
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
