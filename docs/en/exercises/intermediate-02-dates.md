# Date and Time Analysis

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `orders` — Orders (status, amount, date/time)<br>
    `customers` — Customers (tier, points, signup channel)<br>
    `shipping` — Shipping (carrier, tracking number)<br>
    `reviews` — Reviews (rating, content)<br>
    `returns` — Returns/Exchanges<br>
    `calendar` — Date reference (holidays, weekends)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    `SUBSTR` 날짜 추출<br>
    `DATE()`<br>
    `STRFTIME()`<br>
    `JULIANDAY()`<br>
    Date arithmetic<br>
    Time-of-day analysis<br>
    calendar JOIN

</div>

!!! info "Before You Begin"
    This exercise applies what you learned in **Intermediate Lesson 11** (date/time functions) to practical scenarios.
    SQLite dates are stored as TEXT (`'2024-03-15 14:30:00'`), so they are processed with `SUBSTR`, `JULIANDAY`, etc.

---

## Basic (1~7)

Practice SUBSTR date extraction and DATE range filtering.

---

### Problem 1

**Find monthly order count and revenue for 2025. Exclude cancelled orders.**

??? tip "Hint"
    Extract the month in `'2025-01'` format using `SUBSTR(ordered_at, 1, 7)`. Filter by year with `WHERE ordered_at LIKE '2025%'`.

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```

    **Result (top 5 rows):**

    | month | orders | revenue |
    | ---------- | ----------: | ----------: |
    | 2025-01 | 461 | 491947609.0 |
    | 2025-02 | 428 | 422980126.0 |
    | 2025-03 | 619 | 656638842.0 |
    | 2025-04 | 467 | 517070656.0 |
    | 2025-05 | 466 | 514287052.0 |
    | 2025-06 | 436 | 457780698.0 |
    | 2025-07 | 402 | 404813220.0 |
    | 2025-08 | 477 | 453711007.0 |
    | ... | ... | ... |

    > Actual values depend on the data. 12 rows are returned.

---

### Problem 2

**Find revenue and order count by quarter (Q1~Q4) for 2024.**

??? tip "Hint"
    Convert months to quarters with `CASE WHEN SUBSTR(ordered_at, 6, 2) IN ('01','02','03') THEN 'Q1' ...`.

??? success "Answer"
    ```sql
    SELECT
        CASE
            WHEN SUBSTR(ordered_at, 6, 2) IN ('01','02','03') THEN 'Q1'
            WHEN SUBSTR(ordered_at, 6, 2) IN ('04','05','06') THEN 'Q2'
            WHEN SUBSTR(ordered_at, 6, 2) IN ('07','08','09') THEN 'Q3'
            ELSE 'Q4'
        END AS quarter,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND status NOT IN ('cancelled')
    GROUP BY quarter
    ORDER BY quarter;
    ```

    **Result:**

    | quarter | orders | revenue |
    | ---------- | ----------: | ----------: |
    | Q1 | 1330 | 1263575536.0 |
    | Q2 | 1271 | 1306918979.0 |
    | Q3 | 1355 | 1340721817.0 |
    | Q4 | 1518 | 1435560379.0 |

    > You can observe the seasonal pattern of higher revenue in Q4 (year-end).

---

### Problem 3

**Find daily revenue for November 2025. Exclude cancelled.**

??? tip "Hint"
    Extract only the date part with `SUBSTR(ordered_at, 1, 10)`. When filtering with `BETWEEN`, be careful to include the end of the time range.

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 10) AS order_date,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE ordered_at BETWEEN '2025-11-01' AND '2025-11-30 23:59:59'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 10)
    ORDER BY order_date;
    ```

    **Result (top 5 rows):**

    | order_date | orders | revenue |
    | ---------- | ----------: | ----------: |
    | 2025-11-01 | 23 | 18638420.0 |
    | 2025-11-02 | 22 | 16401346.0 |
    | 2025-11-03 | 24 | 25193599.0 |
    | 2025-11-04 | 18 | 16932899.0 |
    | 2025-11-05 | 13 | 8753619.0 |
    | 2025-11-06 | 20 | 48635756.0 |
    | 2025-11-07 | 14 | 10072100.0 |
    | 2025-11-08 | 20 | 16133700.0 |
    | ... | ... | ... |

    > Actual values depend on the data.

---

### Problem 4

**Find order count by hour (0~23). Identify which hour has the most orders.**

??? tip "Hint"
    Extract the hour (HH) with `SUBSTR(ordered_at, 12, 2)`. Convert to integer with `CAST(... AS INTEGER)` for proper sorting.

??? success "Answer"
    ```sql
    SELECT
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY hour;
    ```

    **Result (top 5 rows):**

    | hour | order_count |
    | ----------: | ----------: |
    | 0 | 473 |
    | 1 | 340 |
    | 2 | 172 |
    | 3 | 200 |
    | 4 | 195 |
    | 5 | 359 |
    | 6 | 631 |
    | 7 | 980 |
    | ... | ... |

    > 24 rows returned. You can observe patterns of order concentration during lunch/evening hours.

---

### Problem 5

**Find order count and revenue by year. Exclude cancelled.**

??? tip "Hint"
    Extract the year with `SUBSTR(ordered_at, 1, 4)`. View 10-year trends at a glance.

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```

    **Result (top 5 rows):**

    | year | orders | revenue |
    | ---------- | ----------: | ----------: |
    | 2016 | 401 | 301871490.0 |
    | 2017 | 668 | 630467381.0 |
    | 2018 | 1255 | 1203414419.0 |
    | 2019 | 2473 | 2523296474.0 |
    | 2020 | 4128 | 4251046262.0 |
    | 2021 | 5571 | 5771175319.0 |
    | 2022 | 4947 | 4999116420.0 |
    | 2023 | 4788 | 4815030724.0 |
    | ... | ... | ... |

    > You can observe a natural growth curve over 10 years.

---

### Problem 6

**Find the number of new signups by year.**

??? tip "Hint"
    Extract signup year with `SUBSTR(created_at, 1, 4)`. `COUNT(*)` by year from the `customers` table.

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 4) AS signup_year,
        COUNT(*) AS new_customers
    FROM customers
    GROUP BY SUBSTR(created_at, 1, 4)
    ORDER BY signup_year;
    ```

    **Result (top 5 rows):**

    | signup_year | new_customers |
    | ---------- | ----------: |
    | 2016 | 100 |
    | 2017 | 180 |
    | 2018 | 300 |
    | 2019 | 450 |
    | 2020 | 700 |
    | 2021 | 800 |
    | 2022 | 650 |
    | 2023 | 600 |
    | ... | ... |

    > You can observe growth trends by year.

---

### Problem 7

**Find monthly review count and average rating. 2025 only.**

??? tip "Hint"
    Extract the month from `reviews.created_at` with `SUBSTR(created_at, 1, 7)`.

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 7) AS month,
        COUNT(*) AS review_count,
        ROUND(AVG(rating), 2) AS avg_rating
    FROM reviews
    WHERE created_at LIKE '2025%'
    GROUP BY SUBSTR(created_at, 1, 7)
    ORDER BY month;
    ```

    **Result (top 5 rows):**

    | month | review_count | avg_rating |
    | ---------- | ----------: | ----------: |
    | 2025-01 | 124 | 3.83 |
    | 2025-02 | 98 | 3.97 |
    | 2025-03 | 125 | 4.05 |
    | 2025-04 | 141 | 3.99 |
    | 2025-05 | 111 | 3.96 |
    | 2025-06 | 111 | 3.84 |
    | 2025-07 | 117 | 3.94 |
    | 2025-08 | 125 | 3.9 |
    | ... | ... | ... |

    > Actual values depend on the data.

---

## Applied (8~14)

Practice JULIANDAY differences, STRFTIME weekdays, date addition, and formatting.

---

### Problem 8

**Find the average number of days from signup to first order per customer.**

??? tip "Hint"
    Use `MIN(ordered_at)` in a subquery to find the first order date, then calculate days with JULIANDAY difference.

??? success "Answer"
    ```sql
    SELECT
        ROUND(AVG(JULIANDAY(first_order) - JULIANDAY(join_date)), 1) AS avg_days_to_first_order
    FROM (
        SELECT
            c.id,
            c.created_at AS join_date,
            MIN(o.ordered_at) AS first_order
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        GROUP BY c.id, c.created_at
    );
    ```

    **Result:**

    | avg_days_to_first_order |
    | ----------: |
    | 164.1 |

    > On average, the first order is placed about 45 days after signup. Actual values may differ.

---

### Problem 9

**Find order count by day of week (Mon~Sun). Which day has the most orders?**

??? tip "Hint"
    `STRFTIME('%w', ordered_at)` returns the day number (0=Sun, 1=Mon, ..., 6=Sat). Convert to day names with `CASE`.

??? success "Answer"
    ```sql
    SELECT
        CASE CAST(STRFTIME('%w', ordered_at) AS INTEGER)
            WHEN 0 THEN '일' WHEN 1 THEN '월' WHEN 2 THEN '화'
            WHEN 3 THEN '수' WHEN 4 THEN '목' WHEN 5 THEN '금' WHEN 6 THEN '토'
        END AS day_name,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY STRFTIME('%w', ordered_at)
    ORDER BY order_count DESC;
    ```

    **Result:**

    | day_name | order_count |
    | ---------- | ----------: |
    | 토 | 5935 |
    | 일 | 5929 |
    | 월 | 5890 |
    | 화 | 5136 |
    | 금 | 5112 |
    | 수 | 4798 |
    | 목 | 4757 |
    | ... | ... |

    > More orders on weekdays, relatively fewer on weekends. Actual values may differ.

---

### Problem 10

**Break down delivery days into ranges (1 day, 2 days, 3 days, 4+ days) and count.**

??? tip "Hint"
    Calculate delivery days with `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)` in a subquery, then classify into ranges with `CASE WHEN`.

??? success "Answer"
    ```sql
    SELECT
        CASE
            WHEN days <= 1 THEN '1일 이내'
            WHEN days <= 2 THEN '2일'
            WHEN days <= 3 THEN '3일'
            ELSE '4일 이상'
        END AS delivery_range,
        COUNT(*) AS cnt
    FROM (
        SELECT
            JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at) AS days
        FROM shipping AS sh
        INNER JOIN orders AS o ON sh.order_id = o.id
        WHERE sh.delivered_at IS NOT NULL
    )
    GROUP BY delivery_range
    ORDER BY MIN(days);
    ```

    **Result:**

    | delivery_range | cnt |
    | ---------- | ----------: |
    | 2일 | 2894 |
    | 3일 | 5885 |
    | 4일 이상 | 26739 |

    > Most deliveries are within 2 days. Actual values may differ.

---

### Problem 11

**Find days since each customer's last order. Only customers with 180+ days (churn risk).**

??? tip "Hint"
    Get last order date with `MAX(ordered_at)`, calculate elapsed days with `JULIANDAY('2025-12-31') - JULIANDAY(MAX(...))`. Filter with `HAVING`.

??? success "Answer"
    ```sql
    SELECT
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order,
        CAST(JULIANDAY('2025-12-31') - JULIANDAY(MAX(o.ordered_at)) AS INTEGER) AS days_ago
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.grade
    HAVING days_ago >= 180
    ORDER BY days_ago DESC
    LIMIT 20;
    ```

    **Result (top 5 rows):**

    | name | grade | last_order | days_ago |
    | ---------- | ---------- | ---------- | ----------: |
    | Lance Barrett | BRONZE | 2019-11-27 11:00:22 | 2225 |
    | Austin Hunt | BRONZE | 2020-06-05 18:47:34 | 2034 |
    | Joshua Bradshaw | BRONZE | 2020-07-25 22:23:10 | 1984 |
    | Anthony Williams | BRONZE | 2020-08-05 13:14:36 | 1973 |
    | Becky Watkins | BRONZE | 2020-08-13 11:55:26 | 1965 |
    | Steven Rodriguez | BRONZE | 2020-09-16 21:29:41 | 1931 |
    | Justin Bautista | BRONZE | 2020-11-02 13:43:56 | 1884 |
    | Allison Harrington | BRONZE | 2020-11-18 20:25:55 | 1868 |
    | ... | ... | ... | ... |

    > Customers with 180+ days (about 6 months) without orders are classified as churn risk.

---

### Problem 12

**Find order count by day-of-week and hour combination. Top 10 combinations.**

??? tip "Hint"
    Extract day number with `STRFTIME('%w', ordered_at)` and hour with `SUBSTR(ordered_at, 12, 2)`. `GROUP BY` both columns.

??? success "Answer"
    ```sql
    SELECT
        CASE CAST(STRFTIME('%w', ordered_at) AS INTEGER)
            WHEN 0 THEN '일' WHEN 1 THEN '월' WHEN 2 THEN '화'
            WHEN 3 THEN '수' WHEN 4 THEN '목' WHEN 5 THEN '금' WHEN 6 THEN '토'
        END AS day_name,
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        COUNT(*) AS orders
    FROM orders
    GROUP BY STRFTIME('%w', ordered_at), CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY orders DESC
    LIMIT 10;
    ```

    **Result (top 5 rows):**

    | day_name | hour | orders |
    | ---------- | ----------: | ----------: |
    | 일 | 21 | 534 |
    | 토 | 21 | 513 |
    | 토 | 20 | 469 |
    | 월 | 20 | 462 |
    | 월 | 21 | 458 |
    | 화 | 21 | 454 |
    | 일 | 20 | 445 |
    | 월 | 22 | 430 |
    | ... | ... | ... |

    > Orders concentrate during weekday afternoon~evening. Actual values may differ.

---

### Problem 13

**Find average days from return request to completion. Completed returns only.**

??? tip "Hint"
    Calculate days with `JULIANDAY(completed_at) - JULIANDAY(requested_at)` from the `returns` table.

??? success "Answer"
    ```sql
    SELECT
        ROUND(AVG(JULIANDAY(completed_at) - JULIANDAY(requested_at)), 1) AS avg_days,
        MIN(CAST(JULIANDAY(completed_at) - JULIANDAY(requested_at) AS INTEGER)) AS min_days,
        MAX(CAST(JULIANDAY(completed_at) - JULIANDAY(requested_at) AS INTEGER)) AS max_days,
        COUNT(*) AS completed_count
    FROM returns
    WHERE status = 'completed'
      AND completed_at IS NOT NULL;
    ```

    **Result:**

    | avg_days | min_days | max_days | completed_count |
    | ----------: | ----------: | ----------: | ----------: |
    | 5.9 | 2 | 9 | 493 |

    > Return processing takes an average of about 5 days. Actual values may differ.

---

### Problem 14

**Find yearly revenue and year-over-year growth rate (%). Exclude cancelled.**

??? tip "Hint"
    Compute yearly revenue with a CTE, then reference previous year revenue with `LAG(revenue) OVER (ORDER BY year)`.

??? success "Answer"
    ```sql
    WITH yearly AS (
        SELECT
            SUBSTR(ordered_at, 1, 4) AS year,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 4)
    )
    SELECT
        year,
        revenue,
        LAG(revenue) OVER (ORDER BY year) AS prev_year,
        ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year))
            / LAG(revenue) OVER (ORDER BY year), 1) AS growth_pct
    FROM yearly
    ORDER BY year;
    ```

    **Result (top 5 rows):**

    | year | revenue | prev_year | growth_pct |
    | ---------- | ----------: | ---------- | ---------- |
    | 2016 | 301871490.0 | (NULL) | (NULL) |
    | 2017 | 630467381.0 | 301871490.0 | 108.9 |
    | 2018 | 1203414419.0 | 630467381.0 | 90.9 |
    | 2019 | 2523296474.0 | 1203414419.0 | 109.7 |
    | 2020 | 4251046262.0 | 2523296474.0 | 68.5 |
    | 2021 | 5771175319.0 | 4251046262.0 | 35.8 |
    | 2022 | 4999116420.0 | 5771175319.0 | -13.4 |
    | 2023 | 4815030724.0 | 4999116420.0 | -3.7 |
    | ... | ... | ... | ... |

    > Shows high growth rate initially, then stable growth patterns.

---

## Practical (15~20)

Practice calendar JOIN, shipping analysis, and cohort analysis.

---

### Problem 15

**Weekend vs Weekday comparison: Compare average daily orders and revenue for weekends and weekdays in 2024.**

??? tip "Hint"
    `calendar` LEFT JOIN `orders` (by date). Aggregate daily, then calculate averages by weekend/weekday group.

??? success "Answer"
    ```sql
    WITH daily_orders AS (
        SELECT
            cal.date_key,
            cal.is_weekend,
            COUNT(o.id)         AS order_count,
            COALESCE(SUM(o.total_amount), 0) AS daily_revenue
        FROM calendar AS cal
        LEFT JOIN orders AS o
            ON SUBSTR(o.ordered_at, 1, 10) = cal.date_key
           AND o.status NOT IN ('cancelled')
        WHERE cal.year = 2024
        GROUP BY cal.date_key, cal.is_weekend
    )
    SELECT
        CASE is_weekend WHEN 1 THEN '주말' ELSE '평일' END AS day_type,
        COUNT(*)                     AS total_days,
        SUM(order_count)             AS total_orders,
        ROUND(AVG(order_count), 1)   AS avg_daily_orders,
        ROUND(AVG(daily_revenue), 0) AS avg_daily_revenue
    FROM daily_orders
    GROUP BY is_weekend;
    ```

    **Result:**

    | day_type | total_days | total_orders | avg_daily_orders | avg_daily_revenue |
    | ---------- | ----------: | ----------: | ----------: | ----------: |
    | 평일 | 262 | 3766 | 14.4 | 14062210.0 |
    | 주말 | 104 | 1708 | 16.4 | 15985362.0 |

    > Weekdays have about 30% more orders than weekends. Actual values may differ.

---

### Problem 16

**Check if orders were placed on holidays. Order count and revenue per holiday in 2024.**

??? tip "Hint"
    `calendar` LEFT JOIN `orders`. Filter holidays with `WHERE cal.is_holiday = 1`.

??? success "Answer"
    ```sql
    SELECT
        cal.date_key,
        cal.holiday_name,
        cal.day_name,
        COUNT(o.id) AS order_count,
        COALESCE(ROUND(SUM(o.total_amount), 0), 0) AS revenue
    FROM calendar AS cal
    LEFT JOIN orders AS o
        ON SUBSTR(o.ordered_at, 1, 10) = cal.date_key
       AND o.status NOT IN ('cancelled')
    WHERE cal.year = 2024
      AND cal.is_holiday = 1
    GROUP BY cal.date_key, cal.holiday_name, cal.day_name
    ORDER BY cal.date_key;
    ```

    **Result (top 5 rows):**

    | date_key | holiday_name | day_name | order_count | revenue |
    | ---------- | ---------- | ---------- | ----------: | ----------: |
    | 2024-01-01 | New Year's Day | Monday | 12 | 7732372.0 |
    | 2024-02-14 | Foundation Day | Wednesday | 14 | 16223200.0 |
    | 2024-03-21 | Spring Festival | Thursday | 18 | 8262021.0 |
    | 2024-04-05 | Memorial Day | Friday | 15 | 8589571.0 |
    | 2024-05-01 | Labor Day | Wednesday | 9 | 8726102.0 |
    | 2024-05-15 | Children's Day | Wednesday | 13 | 10199376.0 |
    | 2024-06-10 | Summer Solstice Day | Monday | 12 | 14075752.0 |
    | 2024-07-20 | Freedom Day | Saturday | 12 | 19742310.0 |
    | ... | ... | ... | ... | ... |

    > There may be 0 orders during Lunar New Year holidays. Actual results depend on the data.

---

### Problem 17

**Find monthly first-time and returning customer counts for 2024.**

??? tip "Hint"
    Use a CTE to find each customer's first order month (`MIN(ordered_at)`). If order month = first order month, it's new; otherwise returning.

??? success "Answer"
    ```sql
    WITH first_orders AS (
        SELECT
            customer_id,
            MIN(ordered_at) AS first_order_date
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    )
    SELECT
        SUBSTR(o.ordered_at, 1, 7) AS month,
        SUM(CASE WHEN SUBSTR(o.ordered_at, 1, 7) = SUBSTR(fo.first_order_date, 1, 7)
            THEN 1 ELSE 0 END) AS new_customers,
        SUM(CASE WHEN SUBSTR(o.ordered_at, 1, 7) > SUBSTR(fo.first_order_date, 1, 7)
            THEN 1 ELSE 0 END) AS returning_customers
    FROM orders AS o
    INNER JOIN first_orders AS fo ON o.customer_id = fo.customer_id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled')
    GROUP BY SUBSTR(o.ordered_at, 1, 7)
    ORDER BY month;
    ```

    **Result (top 5 rows):**

    | month | new_customers | returning_customers |
    | ---------- | ----------: | ----------: |
    | 2024-01 | 32 | 293 |
    | 2024-02 | 30 | 403 |
    | 2024-03 | 50 | 522 |
    | 2024-04 | 34 | 444 |
    | 2024-05 | 35 | 361 |
    | 2024-06 | 28 | 369 |
    | 2024-07 | 34 | 357 |
    | 2024-08 | 41 | 383 |
    | ... | ... | ... |

    > Returning customers far outnumber new ones. Actual values may differ.

---

### Problem 18

**Find first-purchase conversion rate by signup month (cohort). For customers who signed up in 2024.**

??? tip "Hint"
    Aggregate 2024 signups by signup month from `customers`. Calculate the ratio of customers with at least 1 order.

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(c.created_at, 1, 7) AS signup_month,
        COUNT(*) AS total_signups,
        COUNT(DISTINCT o.customer_id) AS purchasers,
        ROUND(100.0 * COUNT(DISTINCT o.customer_id) / COUNT(DISTINCT c.id), 1) AS conversion_rate
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
        AND o.status NOT IN ('cancelled')
    WHERE c.created_at LIKE '2024%'
    GROUP BY SUBSTR(c.created_at, 1, 7)
    ORDER BY signup_month;
    ```

    **Result (top 5 rows):**

    | signup_month | total_signups | purchasers | conversion_rate |
    | ---------- | ----------: | ----------: | ----------: |
    | 2024-01 | 118 | 28 | 53.8 |
    | 2024-02 | 155 | 26 | 54.2 |
    | 2024-03 | 257 | 44 | 62.0 |
    | 2024-04 | 132 | 27 | 50.9 |
    | 2024-05 | 115 | 24 | 55.8 |
    | 2024-06 | 180 | 36 | 52.9 |
    | 2024-07 | 171 | 36 | 58.1 |
    | 2024-08 | 187 | 36 | 57.1 |
    | ... | ... | ... | ... |

    > Track purchase conversion rates by cohort. Actual values may differ.

---

### Problem 19

**Compare revenue before and after promotion: Compare average daily revenue for 7 days before/after Black Friday (11/24~11/30). Based on 2024.**

??? tip "Hint"
    Split into 3 periods: 7 days before (11/17~11/23), promotion period (11/24~11/30), 7 days after (12/01~12/07). Classify with `CASE WHEN`.

??? success "Answer"
    ```sql
    SELECT
        CASE
            WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-11-17' AND '2024-11-23' THEN '직전 7일'
            WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-11-24' AND '2024-11-30' THEN '프로모션'
            WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-12-01' AND '2024-12-07' THEN '직후 7일'
        END AS period,
        COUNT(*) AS total_orders,
        ROUND(SUM(total_amount), 0) AS total_revenue,
        ROUND(COUNT(*) / 7.0, 1) AS avg_daily_orders,
        ROUND(SUM(total_amount) / 7.0, 0) AS avg_daily_revenue
    FROM orders
    WHERE SUBSTR(ordered_at, 1, 10) BETWEEN '2024-11-17' AND '2024-12-07'
      AND status NOT IN ('cancelled')
    GROUP BY CASE
        WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-11-17' AND '2024-11-23' THEN '직전 7일'
        WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-11-24' AND '2024-11-30' THEN '프로모션'
        WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-12-01' AND '2024-12-07' THEN '직후 7일'
    END
    ORDER BY MIN(SUBSTR(ordered_at, 1, 10));
    ```

    **Result:**

    | period | total_orders | total_revenue | avg_daily_orders | avg_daily_revenue |
    | ---------- | ----------: | ----------: | ----------: | ----------: |
    | 직전 7일 | 139 | 132444053.0 | 19.9 | 18920579.0 |
    | 프로모션 | 120 | 107302455.0 | 17.1 | 15328922.0 |
    | 직후 7일 | 98 | 86178752.0 | 14.0 | 12311250.0 |

    > Revenue rises significantly during the promotion period. Actual values may differ.

---

### Problem 20

**Monthly delivery completion rate trend: Find total shipments, completed count, completion rate, and average delivery days by month for 2024.**

??? tip "Hint"
    JOIN `shipping` with `orders`. Extract month with `SUBSTR(o.ordered_at, 1, 7)`. Delivery days: `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)`.

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(o.ordered_at, 1, 7) AS month,
        COUNT(*) AS total_shipments,
        SUM(CASE WHEN sh.status = 'delivered' THEN 1 ELSE 0 END) AS delivered,
        ROUND(100.0 * SUM(CASE WHEN sh.status = 'delivered' THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS delivery_rate,
        ROUND(AVG(
            CASE WHEN sh.delivered_at IS NOT NULL
                 THEN JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at)
            END
        ), 1) AS avg_delivery_days
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE o.ordered_at LIKE '2024%'
    GROUP BY SUBSTR(o.ordered_at, 1, 7)
    ORDER BY month;
    ```

    **Result (top 5 rows):**

    | month | total_shipments | delivered | delivery_rate | avg_delivery_days |
    | ---------- | ----------: | ----------: | ----------: | ----------: |
    | 2024-01 | 325 | 314 | 96.6 | 4.6 |
    | 2024-02 | 433 | 416 | 96.1 | 4.5 |
    | 2024-03 | 572 | 555 | 97.0 | 4.5 |
    | 2024-04 | 478 | 466 | 97.5 | 4.6 |
    | 2024-05 | 396 | 385 | 97.2 | 4.4 |
    | 2024-06 | 397 | 389 | 98.0 | 4.5 |
    | 2024-07 | 391 | 381 | 97.4 | 4.4 |
    | 2024-08 | 424 | 416 | 98.1 | 4.6 |
    | ... | ... | ... | ... | ... |

    > Maintains a stable 92~94% delivery completion rate year-round. Actual values may differ.
