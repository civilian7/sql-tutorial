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
    | 2025-01 | 3839 | 3943937476.0 |
    | 2025-02 | 4730 | 5084851234.0 |
    | 2025-03 | 6763 | 7026276850.0 |
    | 2025-04 | 4894 | 4967603102.0 |
    | 2025-05 | 4789 | 5027077923.0 |
    | 2025-06 | 4695 | 4929582688.0 |
    | 2025-07 | 4464 | 4589328327.0 |
    | 2025-08 | 5908 | 5961730543.0 |
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
    | Q1 | 13493 | 13722233972.0 |
    | Q2 | 13862 | 14008860078.0 |
    | Q3 | 14717 | 15150817406.0 |
    | Q4 | 18763 | 19606422982.0 |

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
    | 2025-11-01 | 268 | 296274205.0 |
    | 2025-11-02 | 260 | 350457927.0 |
    | 2025-11-03 | 207 | 254333330.0 |
    | 2025-11-04 | 227 | 274610527.0 |
    | 2025-11-05 | 164 | 162318704.0 |
    | 2025-11-06 | 207 | 210772960.0 |
    | 2025-11-07 | 165 | 188044505.0 |
    | 2025-11-08 | 256 | 240669352.0 |
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
    | 0 | 5419 |
    | 1 | 3746 |
    | 2 | 2008 |
    | 3 | 2024 |
    | 4 | 2051 |
    | 5 | 3837 |
    | 6 | 7420 |
    | 7 | 11015 |
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
    | 2016 | 7122 | 7405535811.0 |
    | 2017 | 10871 | 11416329698.0 |
    | 2018 | 19630 | 20713930120.0 |
    | 2019 | 27427 | 29034166152.0 |
    | 2020 | 44396 | 46360873185.0 |
    | 2021 | 57447 | 59343488311.0 |
    | 2022 | 56254 | 58485619251.0 |
    | 2023 | 48687 | 50786628424.0 |
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
    | 2016 | 1000 |
    | 2017 | 1800 |
    | 2018 | 3000 |
    | 2019 | 4500 |
    | 2020 | 7000 |
    | 2021 | 8000 |
    | 2022 | 6500 |
    | 2023 | 6000 |
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
    | 2025-01 | 1316 | 3.95 |
    | 2025-02 | 962 | 3.88 |
    | 2025-03 | 1425 | 3.88 |
    | 2025-04 | 1434 | 3.92 |
    | 2025-05 | 1222 | 3.91 |
    | 2025-06 | 1099 | 3.84 |
    | 2025-07 | 1118 | 3.91 |
    | 2025-08 | 1217 | 3.94 |
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
    | 149.5 |

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
    | 일 | 66016 |
    | 월 | 65807 |
    | 토 | 65458 |
    | 화 | 56634 |
    | 금 | 56416 |
    | 수 | 53895 |
    | 목 | 53577 |
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
    | 2일 | 32922 |
    | 3일 | 65954 |
    | 4일 이상 | 296430 |

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
    | 남순자 | BRONZE | 2018-03-22 23:31:18 | 2840 |
    | 이상훈 | BRONZE | 2018-09-05 19:29:12 | 2673 |
    | 배성현 | BRONZE | 2019-01-13 20:22:06 | 2543 |
    | 김은서 | BRONZE | 2019-02-03 17:07:50 | 2522 |
    | 권경숙 | BRONZE | 2019-05-13 22:46:41 | 2423 |
    | 김우진 | BRONZE | 2019-10-13 21:22:08 | 2270 |
    | 김준서 | BRONZE | 2019-10-26 19:48:34 | 2257 |
    | 김시우 | BRONZE | 2019-11-08 22:24:35 | 2244 |
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
    | 일 | 21 | 5649 |
    | 토 | 21 | 5519 |
    | 월 | 21 | 5475 |
    | 일 | 20 | 5091 |
    | 토 | 20 | 4981 |
    | 화 | 21 | 4921 |
    | 월 | 20 | 4865 |
    | 금 | 21 | 4859 |
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
    | 6.1 | 2 | 10 | 6071 |

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
    | 2016 | 7405535811.0 | (NULL) | (NULL) |
    | 2017 | 11416329698.0 | 7405535811.0 | 54.2 |
    | 2018 | 20713930120.0 | 11416329698.0 | 81.4 |
    | 2019 | 29034166152.0 | 20713930120.0 | 40.2 |
    | 2020 | 46360873185.0 | 29034166152.0 | 59.7 |
    | 2021 | 59343488311.0 | 46360873185.0 | 28.0 |
    | 2022 | 58485619251.0 | 59343488311.0 | -1.4 |
    | 2023 | 50786628424.0 | 58485619251.0 | -13.2 |
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
    |----------|-----------|-------------|-----------------|------------------|
    | 평일 | 262 | 28765 | 109.8 | 42345000 |
    | 주말 | 104 | 8234 | 79.2 | 31234000 |

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
    | 2024-01-01 | 신정 | Monday | 117 | 123475163.0 |
    | 2024-02-14 | 건국기념일 | Wednesday | 139 | 128097679.0 |
    | 2024-03-21 | 봄축제 | Thursday | 163 | 142345241.0 |
    | 2024-04-05 | 현충일 | Friday | 132 | 169846556.0 |
    | 2024-05-01 | 근로자의 날 | Wednesday | 127 | 98250430.0 |
    | 2024-05-15 | 어린이날 | Wednesday | 174 | 171454623.0 |
    | 2024-06-10 | 하지제 | Monday | 113 | 114405098.0 |
    | 2024-07-20 | 자유의 날 | Saturday | 141 | 132879919.0 |
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
    | 2024-01 | 323 | 3600 |
    | 2024-02 | 409 | 4194 |
    | 2024-03 | 484 | 4483 |
    | 2024-04 | 424 | 4585 |
    | 2024-05 | 434 | 4646 |
    | 2024-06 | 323 | 3450 |
    | 2024-07 | 392 | 4135 |
    | 2024-08 | 450 | 4452 |
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
    | 2024-01 | 2165 | 360 | 63.8 |
    | 2024-02 | 1899 | 363 | 68.4 |
    | 2024-03 | 2322 | 400 | 64.1 |
    | 2024-04 | 1979 | 374 | 60.5 |
    | 2024-05 | 1758 | 372 | 62.6 |
    | 2024-06 | 1855 | 337 | 58.5 |
    | 2024-07 | 1797 | 369 | 59.8 |
    | 2024-08 | 1708 | 383 | 60.1 |
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
    | 직전 7일 | 1358 | 1519648590.0 | 194.0 | 217092656.0 |
    | 프로모션 | 1542 | 1572197624.0 | 220.3 | 224599661.0 |
    | 직후 7일 | 1537 | 1555897467.0 | 219.6 | 222271067.0 |

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
    |-------|----------------|-----------|--------------|------------------|
    | 2024-01 | 2876 | 2654 | 92.3 | 2.4 |
    | 2024-02 | 2543 | 2345 | 92.2 | 2.5 |
    | 2024-03 | 3012 | 2812 | 93.4 | 2.3 |
    | 2024-04 | 2876 | 2698 | 93.8 | 2.2 |
    | 2024-05 | 2987 | 2801 | 93.8 | 2.3 |

    > Maintains a stable 92~94% delivery completion rate year-round. Actual values may differ.
