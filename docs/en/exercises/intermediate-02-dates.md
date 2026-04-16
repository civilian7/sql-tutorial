# Date and Time Analysis

!!! info "Tables"

    `calendar` — Calendar (weekday, holiday)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `products` — Products (name, price, stock, brand)  

    `promotions` — Promotions (period, discount)  

    `returns` — Returns (reason, status)  

    `shipping` — Shipping (carrier, tracking, status)  



!!! abstract "Concepts"

    `SUBSTR`, `JULIANDAY`, `STRFTIME`, `date arithmetic`, `LAG`, `CTE`, `window functions`



### 1. Find the number of orders and revenue per month in 2025. Exc


Find the number of orders and revenue per month in 2025. Exclude cancelled orders.


**Hint 1:** Extract the month with `SUBSTR(ordered_at, 1, 7)` and filter the year with `WHERE ordered_at LIKE '2025%'`.


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```


    **Result** (top 7 of 12 rows)

    | month | orders | revenue |
    |---|---|---|
    | 2025-01 | 461 | 491,947,609.00 |
    | 2025-02 | 428 | 422,980,126.00 |
    | 2025-03 | 619 | 656,638,842.00 |
    | 2025-04 | 467 | 517,070,656.00 |
    | 2025-05 | 466 | 514,287,052.00 |
    | 2025-06 | 436 | 457,780,698.00 |
    | 2025-07 | 402 | 404,813,220.00 |


---


### 2. Find the revenue and order count per quarter (Q1-Q4) in 2024


Find the revenue and order count per quarter (Q1-Q4) in 2024.


**Hint 1:** Convert months to quarters with `CASE WHEN SUBSTR(ordered_at, 6, 2) IN ('01','02','03') THEN 'Q1' ...`.


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
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND status NOT IN ('cancelled')
    GROUP BY quarter
    ORDER BY quarter;
    ```


    **Result** (4 rows)

    | quarter | orders | revenue |
    |---|---|---|
    | Q1 | 1330 | 1,263,575,536.00 |
    | Q2 | 1271 | 1,306,918,979.00 |
    | Q3 | 1355 | 1,340,721,817.00 |
    | Q4 | 1518 | 1,435,560,379.00 |


---


### 3. Find the average number of days from signup to first order a


Find the average number of days from signup to first order across all customers.


**Hint 1:** Get the first order date with `MIN(ordered_at)` in a subquery, then calculate the day difference with `JULIANDAY`.


??? success "Answer"

    === "SQLite"
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

    === "MySQL"
        ```sql
        SELECT
            ROUND(AVG(DATEDIFF(first_order, join_date)), 1) AS avg_days_to_first_order
        FROM (
            SELECT
                c.id,
                c.created_at AS join_date,
                MIN(o.ordered_at) AS first_order
            FROM customers AS c
            INNER JOIN orders AS o ON c.id = o.customer_id
            GROUP BY c.id, c.created_at
        ) AS sub;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            ROUND(AVG(first_order::date - join_date::date), 1) AS avg_days_to_first_order
        FROM (
            SELECT
                c.id,
                c.created_at AS join_date,
                MIN(o.ordered_at) AS first_order
            FROM customers AS c
            INNER JOIN orders AS o ON c.id = o.customer_id
            GROUP BY c.id, c.created_at
        ) AS sub;
        ```

    === "Oracle"
        ```sql
        SELECT
            ROUND(AVG(CAST(first_order AS DATE) - CAST(join_date AS DATE)), 1) AS avg_days_to_first_order
        FROM (
            SELECT
                c.id,
                c.created_at AS join_date,
                MIN(o.ordered_at) AS first_order
            FROM customers c
            INNER JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id, c.created_at
        );
        ```

    === "SQL Server"
        ```sql
        SELECT
            ROUND(AVG(CAST(DATEDIFF(DAY, join_date, first_order) AS FLOAT)), 1) AS avg_days_to_first_order
        FROM (
            SELECT
                c.id,
                c.created_at AS join_date,
                MIN(o.ordered_at) AS first_order
            FROM customers AS c
            INNER JOIN orders AS o ON c.id = o.customer_id
            GROUP BY c.id, c.created_at
        ) AS sub;
        ```


    **Result** (1 rows)

    | avg_days_to_first_order |
    |---|
    | 164.10 |


---


### 4. Find the number of orders per hour of day (0-23).


Find the number of orders per hour of day (0-23).


**Hint 1:** Extract the hour portion with `SUBSTR(ordered_at, 12, 2)`. Convert to integer with `CAST(... AS INTEGER)`.


??? success "Answer"

    === "SQLite"
        ```sql
        SELECT
            CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
        ORDER BY hour;
        ```

    === "MySQL"
        ```sql
        SELECT
            HOUR(ordered_at) AS hour,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY HOUR(ordered_at)
        ORDER BY hour;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            EXTRACT(HOUR FROM ordered_at::timestamp)::INTEGER AS hour,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY EXTRACT(HOUR FROM ordered_at::timestamp)
        ORDER BY hour;
        ```

    === "Oracle"
        ```sql
        SELECT
            EXTRACT(HOUR FROM CAST(ordered_at AS TIMESTAMP)) AS hour,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY EXTRACT(HOUR FROM CAST(ordered_at AS TIMESTAMP))
        ORDER BY hour;
        ```

    === "SQL Server"
        ```sql
        SELECT
            DATEPART(HOUR, ordered_at) AS hour,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY DATEPART(HOUR, ordered_at)
        ORDER BY hour;
        ```


    **Result** (top 7 of 24 rows)

    | hour | order_count |
    |---|---|
    | 0 | 473 |
    | 1 | 340 |
    | 2 | 172 |
    | 3 | 200 |
    | 4 | 195 |
    | 5 | 359 |
    | 6 | 631 |


---


### 5. Find the daily revenue for the last 30 days (based on 2025-1


Find the daily revenue for the last 30 days (based on 2025-11-01 to 2025-11-30).


**Hint 1:** Filter with `BETWEEN '2025-11-01' AND '2025-11-30 23:59:59'`. Be careful to include up to the end of the last day.


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 10) AS order_date,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at BETWEEN '2025-11-01' AND '2025-11-30 23:59:59'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 10)
    ORDER BY order_date;
    ```


    **Result** (top 7 of 30 rows)

    | order_date | orders | revenue |
    |---|---|---|
    | 2025-11-01 | 23 | 18,638,420.00 |
    | 2025-11-02 | 22 | 16,401,346.00 |
    | 2025-11-03 | 24 | 25,193,599.00 |
    | 2025-11-04 | 18 | 16,932,899.00 |
    | 2025-11-05 | 13 | 8,753,619.00 |
    | 2025-11-06 | 20 | 48,635,756.00 |
    | 2025-11-07 | 14 | 10,072,100.00 |


---


### 6. Divide delivery duration into ranges (within 1 day, 2 days, 


Divide delivery duration into ranges (within 1 day, 2 days, 3 days, 4+ days) and count.


**Hint 1:** Calculate delivery days with `JULIANDAY` difference in a subquery, then classify ranges with `CASE WHEN days <= 1 THEN ...`.


??? success "Answer"

    === "SQLite"
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

    === "MySQL"
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
                DATEDIFF(sh.delivered_at, o.ordered_at) AS days
            FROM shipping AS sh
            INNER JOIN orders AS o ON sh.order_id = o.id
            WHERE sh.delivered_at IS NOT NULL
        ) AS sub
        GROUP BY delivery_range
        ORDER BY MIN(days);
        ```

    === "PostgreSQL"
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
                (sh.delivered_at::date - o.ordered_at::date) AS days
            FROM shipping AS sh
            INNER JOIN orders AS o ON sh.order_id = o.id
            WHERE sh.delivered_at IS NOT NULL
        ) AS sub
        GROUP BY delivery_range
        ORDER BY MIN(days);
        ```

    === "Oracle"
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
                CAST(sh.delivered_at AS DATE) - CAST(o.ordered_at AS DATE) AS days
            FROM shipping sh
            INNER JOIN orders o ON sh.order_id = o.id
            WHERE sh.delivered_at IS NOT NULL
        )
        GROUP BY
            CASE
                WHEN days <= 1 THEN '1일 이내'
                WHEN days <= 2 THEN '2일'
                WHEN days <= 3 THEN '3일'
                ELSE '4일 이상'
            END
        ORDER BY MIN(days);
        ```

    === "SQL Server"
        ```sql
        SELECT
            CASE
                WHEN days <= 1 THEN N'1일 이내'
                WHEN days <= 2 THEN N'2일'
                WHEN days <= 3 THEN N'3일'
                ELSE N'4일 이상'
            END AS delivery_range,
            COUNT(*) AS cnt
        FROM (
            SELECT
                DATEDIFF(DAY, o.ordered_at, sh.delivered_at) AS days
            FROM shipping AS sh
            INNER JOIN orders AS o ON sh.order_id = o.id
            WHERE sh.delivered_at IS NOT NULL
        ) AS sub
        GROUP BY
            CASE
                WHEN days <= 1 THEN N'1일 이내'
                WHEN days <= 2 THEN N'2일'
                WHEN days <= 3 THEN N'3일'
                ELSE N'4일 이상'
            END
        ORDER BY MIN(days);
        ```


    **Result** (3 rows)

    | delivery_range | cnt |
    |---|---|
    | 2일 | 2894 |
    | 3일 | 5885 |
    | 4일 이상 | 26,739 |


---


### 7. Find the number of days since each customer's last order. On


Find the number of days since each customer's last order. Only customers with 180+ days.


**Hint 1:** Get the last order date with `MAX(ordered_at)` and calculate elapsed days with `JULIANDAY('reference_date') - JULIANDAY(MAX(...))`. Filter with `HAVING` for 180+ days.


??? success "Answer"

    === "SQLite"
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

    === "MySQL"
        ```sql
        SELECT
            c.name,
            c.grade,
            MAX(o.ordered_at) AS last_order,
            DATEDIFF('2025-12-31', MAX(o.ordered_at)) AS days_ago
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        GROUP BY c.id, c.name, c.grade
        HAVING days_ago >= 180
        ORDER BY days_ago DESC
        LIMIT 20;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            c.name,
            c.grade,
            MAX(o.ordered_at) AS last_order,
            ('2025-12-31'::date - MAX(o.ordered_at)::date) AS days_ago
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        GROUP BY c.id, c.name, c.grade
        HAVING ('2025-12-31'::date - MAX(o.ordered_at)::date) >= 180
        ORDER BY days_ago DESC
        LIMIT 20;
        ```

    === "Oracle"
        ```sql
        SELECT
            c.name,
            c.grade,
            MAX(o.ordered_at) AS last_order,
            CAST(DATE '2025-12-31' - CAST(MAX(o.ordered_at) AS DATE) AS INTEGER) AS days_ago
        FROM customers c
        INNER JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.name, c.grade
        HAVING CAST(DATE '2025-12-31' - CAST(MAX(o.ordered_at) AS DATE) AS INTEGER) >= 180
        ORDER BY days_ago DESC
        FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        SELECT TOP 20
            c.name,
            c.grade,
            MAX(o.ordered_at) AS last_order,
            DATEDIFF(DAY, MAX(o.ordered_at), '2025-12-31') AS days_ago
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        GROUP BY c.id, c.name, c.grade
        HAVING DATEDIFF(DAY, MAX(o.ordered_at), '2025-12-31') >= 180
        ORDER BY days_ago DESC;
        ```


    **Result** (top 7 of 20 rows)

    | name | grade | last_order | days_ago |
    |---|---|---|---|
    | Lance Barrett | BRONZE | 2019-11-27 11:00:22 | 2225 |
    | Austin Hunt | BRONZE | 2020-06-05 18:47:34 | 2034 |
    | Joshua Bradshaw | BRONZE | 2020-07-25 22:23:10 | 1984 |
    | Anthony Williams | BRONZE | 2020-08-05 13:14:36 | 1973 |
    | Becky Watkins | BRONZE | 2020-08-13 11:55:26 | 1965 |
    | Steven Rodriguez | BRONZE | 2020-09-16 21:29:41 | 1931 |
    | Justin Bautista | BRONZE | 2020-11-02 13:43:56 | 1884 |


---


### 8. Find the order count by day of week (Mon-Sun) and hour (0-23


Find the order count by day of week (Mon-Sun) and hour (0-23). Show top 20 combinations.


**Hint 1:** Extract the day-of-week number with `STRFTIME('%w', ordered_at)` and convert to day names with `CASE`. `GROUP BY` both columns.


??? success "Answer"

    === "SQLite"
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
        LIMIT 20;
        ```

    === "MySQL"
        ```sql
        SELECT
            CASE DAYOFWEEK(ordered_at)
                WHEN 1 THEN '일' WHEN 2 THEN '월' WHEN 3 THEN '화'
                WHEN 4 THEN '수' WHEN 5 THEN '목' WHEN 6 THEN '금' WHEN 7 THEN '토'
            END AS day_name,
            HOUR(ordered_at) AS hour,
            COUNT(*) AS orders
        FROM orders
        GROUP BY DAYOFWEEK(ordered_at), HOUR(ordered_at)
        ORDER BY orders DESC
        LIMIT 20;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            CASE EXTRACT(DOW FROM ordered_at::timestamp)::INTEGER
                WHEN 0 THEN '일' WHEN 1 THEN '월' WHEN 2 THEN '화'
                WHEN 3 THEN '수' WHEN 4 THEN '목' WHEN 5 THEN '금' WHEN 6 THEN '토'
            END AS day_name,
            EXTRACT(HOUR FROM ordered_at::timestamp)::INTEGER AS hour,
            COUNT(*) AS orders
        FROM orders
        GROUP BY EXTRACT(DOW FROM ordered_at::timestamp), EXTRACT(HOUR FROM ordered_at::timestamp)
        ORDER BY orders DESC
        LIMIT 20;
        ```

    === "Oracle"
        ```sql
        SELECT
            CASE TO_NUMBER(TO_CHAR(CAST(ordered_at AS DATE), 'D'))
                WHEN 1 THEN '일' WHEN 2 THEN '월' WHEN 3 THEN '화'
                WHEN 4 THEN '수' WHEN 5 THEN '목' WHEN 6 THEN '금' WHEN 7 THEN '토'
            END AS day_name,
            EXTRACT(HOUR FROM CAST(ordered_at AS TIMESTAMP)) AS hour,
            COUNT(*) AS orders
        FROM orders
        GROUP BY TO_NUMBER(TO_CHAR(CAST(ordered_at AS DATE), 'D')),
                 EXTRACT(HOUR FROM CAST(ordered_at AS TIMESTAMP))
        ORDER BY orders DESC
        FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        SELECT TOP 20
            CASE DATEPART(WEEKDAY, ordered_at)
                WHEN 1 THEN N'일' WHEN 2 THEN N'월' WHEN 3 THEN N'화'
                WHEN 4 THEN N'수' WHEN 5 THEN N'목' WHEN 6 THEN N'금' WHEN 7 THEN N'토'
            END AS day_name,
            DATEPART(HOUR, ordered_at) AS hour,
            COUNT(*) AS orders
        FROM orders
        GROUP BY DATEPART(WEEKDAY, ordered_at), DATEPART(HOUR, ordered_at)
        ORDER BY orders DESC;
        ```


    **Result** (top 7 of 20 rows)

    | day_name | hour | orders |
    |---|---|---|
    | 일 | 21 | 534 |
    | 토 | 21 | 513 |
    | 토 | 20 | 469 |
    | 월 | 20 | 462 |
    | 월 | 21 | 458 |
    | 화 | 21 | 454 |
    | 일 | 20 | 445 |


---


### 9. Find the yearly revenue and year-over-year growth rate (%). 


Find the yearly revenue and year-over-year growth rate (%). Exclude cancelled orders.


**Hint 1:** Calculate yearly revenue in a CTE, then reference the previous year's revenue with `LAG(revenue) OVER (ORDER BY year)`.


??? success "Answer"
    ```sql
    WITH yearly AS (
        SELECT
            SUBSTR(ordered_at, 1, 4) AS year,
            ROUND(SUM(total_amount), 2) AS revenue
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


    **Result** (top 7 of 10 rows)

    | year | revenue | prev_year | growth_pct |
    |---|---|---|---|
    | 2016 | 301,871,490.00 | NULL | NULL |
    | 2017 | 630,467,381.00 | 301,871,490.00 | 108.90 |
    | 2018 | 1,203,414,419.00 | 630,467,381.00 | 90.90 |
    | 2019 | 2,523,296,474.00 | 1,203,414,419.00 | 109.70 |
    | 2020 | 4,251,046,262.00 | 2,523,296,474.00 | 68.50 |
    | 2021 | 5,771,175,319.00 | 4,251,046,262.00 | 35.80 |
    | 2022 | 4,999,116,420.00 | 5,771,175,319.00 | -13.40 |


---


### 10. Find the average number of days from return request to compl


Find the average number of days from return request to completion. Only completed returns.


**Hint 1:** Calculate processing days with `JULIANDAY(completed_at) - JULIANDAY(requested_at)` from the `returns` table. Filter with `WHERE status = 'completed'`.


??? success "Answer"

    === "SQLite"
        ```sql
        SELECT
            ROUND(AVG(JULIANDAY(completed_at) - JULIANDAY(requested_at)), 1) AS avg_days,
            MIN(CAST(JULIANDAY(completed_at) - JULIANDAY(requested_at) AS INTEGER)) AS min_days,
            MAX(CAST(JULIANDAY(completed_at) - JULIANDAY(requested_at) AS INTEGER)) AS max_days
        FROM returns
        WHERE status = 'completed'
          AND completed_at IS NOT NULL;
        ```

    === "MySQL"
        ```sql
        SELECT
            ROUND(AVG(DATEDIFF(completed_at, requested_at)), 1) AS avg_days,
            MIN(DATEDIFF(completed_at, requested_at)) AS min_days,
            MAX(DATEDIFF(completed_at, requested_at)) AS max_days
        FROM returns
        WHERE status = 'completed'
          AND completed_at IS NOT NULL;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            ROUND(AVG(completed_at::date - requested_at::date), 1) AS avg_days,
            MIN(completed_at::date - requested_at::date) AS min_days,
            MAX(completed_at::date - requested_at::date) AS max_days
        FROM returns
        WHERE status = 'completed'
          AND completed_at IS NOT NULL;
        ```

    === "Oracle"
        ```sql
        SELECT
            ROUND(AVG(CAST(completed_at AS DATE) - CAST(requested_at AS DATE)), 1) AS avg_days,
            MIN(CAST(completed_at AS DATE) - CAST(requested_at AS DATE)) AS min_days,
            MAX(CAST(completed_at AS DATE) - CAST(requested_at AS DATE)) AS max_days
        FROM returns
        WHERE status = 'completed'
          AND completed_at IS NOT NULL;
        ```

    === "SQL Server"
        ```sql
        SELECT
            ROUND(AVG(CAST(DATEDIFF(DAY, requested_at, completed_at) AS FLOAT)), 1) AS avg_days,
            MIN(DATEDIFF(DAY, requested_at, completed_at)) AS min_days,
            MAX(DATEDIFF(DAY, requested_at, completed_at)) AS max_days
        FROM returns
        WHERE status = 'completed'
          AND completed_at IS NOT NULL;
        ```


    **Result** (1 rows)

    | avg_days | min_days | max_days |
    |---|---|---|
    | 5.90 | 2 | 9 |


---


### 11. Find the count of first-time buyers and repeat buyers per mo


Find the count of first-time buyers and repeat buyers per month in 2024.


**Hint 1:** Get each customer's first order date with `MIN(ordered_at)` in a CTE, then compare the order month with the first order month to distinguish new vs returning customers.


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


    **Result** (top 7 of 12 rows)

    | month | new_customers | returning_customers |
    |---|---|---|
    | 2024-01 | 32 | 293 |
    | 2024-02 | 30 | 403 |
    | 2024-03 | 50 | 522 |
    | 2024-04 | 34 | 444 |
    | 2024-05 | 35 | 361 |
    | 2024-06 | 28 | 369 |
    | 2024-07 | 34 | 357 |


---


### 12. Find the name, number of changes, first price, and current p


Find the name, number of changes, first price, and current price of products whose price has changed 2 or more times.


**Hint 1:** Join `products` with `product_prices` for history. Filter with `HAVING COUNT >= 2`. Get the first price via a subquery with `ORDER BY started_at ASC LIMIT 1`.


??? success "Answer"
    ```sql
    SELECT
        p.name,
        COUNT(pp.id) AS price_changes,
        (SELECT pp2.price FROM product_prices pp2
         WHERE pp2.product_id = p.id ORDER BY pp2.started_at ASC LIMIT 1) AS first_price,
        p.price AS current_price
    FROM products AS p
    INNER JOIN product_prices AS pp ON p.id = pp.product_id
    GROUP BY p.id, p.name, p.price
    HAVING COUNT(pp.id) >= 2
    ORDER BY price_changes DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | price_changes | first_price | current_price |
    |---|---|---|---|
    | ASRock B850M Pro RS White | 5 | 418,600.00 | 419,600.00 |
    | ASRock B860M Pro RS White | 5 | 538,500.00 | 610,100.00 |
    | ASRock X870E Taichi Silver | 5 | 575,800.00 | 543,100.00 |
    | ASUS Dual RTX 4060 Ti Black | 5 | 2,003,500.00 | 2,674,800.00 |
    | ASUS Dual RTX 5070 Ti Silver | 5 | 1,136,500.00 | 986,400.00 |
    | ASUS ExpertCenter PN65 Silver | 5 | 647,000.00 | 722,100.00 |
    | ASUS ROG MAXIMUS Z890 HERO Black | 5 | 973,100.00 | 1,150,400.00 |


---


### 13. Weekend vs Weekday Order Comparison


JOIN calendar with orders to compare 2024 weekend vs weekday
average daily order count and average daily revenue.


**Hint 1:** Use `calendar.is_weekend`. First aggregate orders per day, then calculate averages by weekend/weekday group.


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


    **Result** (2 rows)

    | day_type | total_days | total_orders | avg_daily_orders | avg_daily_revenue |
    |---|---|---|---|---|
    | 평일 | 262 | 3766 | 14.40 | 14,062,210.00 |
    | 주말 | 104 | 1708 | 16.40 | 15,985,362.00 |


---


### 14. Promotion Products Search


Find promotions active during a specific period (2024-11-01 to 2024-12-31)
and the products included in them.


**Hint 1:** Period overlap: `promotions.started_at <= '2024-12-31' AND promotions.ended_at >= '2024-11-01'`. JOIN `promotion_products` -> `products`. Show override_price as special price if present.


??? success "Answer"
    ```sql
    SELECT
        promo.name       AS promotion_name,
        promo.type       AS promotion_type,
        promo.discount_type,
        promo.discount_value,
        promo.started_at,
        promo.ended_at,
        p.name           AS product_name,
        p.price          AS regular_price,
        pp.override_price AS special_price,
        CASE
            WHEN pp.override_price IS NOT NULL THEN pp.override_price
            WHEN promo.discount_type = 'percent' THEN ROUND(p.price * (1 - promo.discount_value / 100.0), 0)
            ELSE ROUND(p.price - promo.discount_value, 0)
        END AS final_price
    FROM promotions AS promo
    INNER JOIN promotion_products AS pp ON promo.id = pp.promotion_id
    INNER JOIN products           AS p  ON pp.product_id = p.id
    WHERE promo.started_at <= '2024-12-31'
      AND promo.ended_at   >= '2024-11-01'
      AND promo.is_active = 1
    ORDER BY promo.name, p.name
    LIMIT 30;
    ```


---
