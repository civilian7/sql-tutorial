# Window Functions in Practice

!!! info "Tables"
    `orders` — Orders (status, amount, date)  
    `order_items` — Order items (qty, unit price)  
    `products` — Products (name, price, stock, brand)  
    `customers` — Customers (grade, points, channel)  
    `reviews` — Reviews (rating, content)  
    `payments` — Payments (method, amount, status)  
    `categories` — Categories (parent-child hierarchy)  

!!! abstract "Concepts"
    `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `LAG`, `LEAD`, `SUM/AVG/COUNT OVER`, `FIRST_VALUE`, `LAST_VALUE`, `ROWS BETWEEN`

!!! info "Before You Begin"
    This exercise puts into practice what you learned in **Advanced Lesson 18** (Window Functions).
    All queries can be executed in SQLite. Cancellation/return order exclusion conditions: `status NOT IN ('cancelled', 'returned', 'return_requested')`

---

## Basic (1~5)

Practice the basic syntax of window functions.

---

### Problem 1

**Sort each customer's orders in chronological order and number the orders for each customer.**

Displays customer ID, customer name, order number, order date, order amount, and order number (`order_seq`) within the customer.
Print only the top 20 rows.

??? tip "Hint"
    Use `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`.
    Group by customer with `PARTITION BY customer_id` and sort chronologically with `ORDER BY ordered_at`.

??? success "Answer"
    ```sql
    SELECT
        c.id             AS customer_id,
        c.name           AS customer_name,
        o.order_number,
        o.ordered_at,
        o.total_amount,
        ROW_NUMBER() OVER (
            PARTITION BY c.id
            ORDER BY o.ordered_at
        ) AS order_seq
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY c.id, order_seq
    LIMIT 20;
    ```

    **Result example (top 5 rows):**

    | customer_id | customer_name | order_number | ordered_at | total_amount | order_seq |
    | ----------: | ---------- | ---------- | ---------- | ----------: | ----------: |
    | 2 | Danny Johnson | ORD-20160807-00243 | 2016-08-17 23:29:34 | 2413300.0 | 1 |
    | 2 | Danny Johnson | ORD-20160802-00236 | 2016-08-19 22:29:34 | 298500.0 | 2 |
    | 2 | Danny Johnson | ORD-20160830-00269 | 2016-08-30 10:49:39 | 445700.0 | 3 |
    | 2 | Danny Johnson | ORD-20160904-00274 | 2016-09-04 08:47:04 | 597000.0 | 4 |
    | 2 | Danny Johnson | ORD-20160915-00287 | 2016-09-15 20:07:17 | 1760400.0 | 5 |
    | 2 | Danny Johnson | ORD-20161024-00334 | 2016-10-24 12:13:06 | 131500.0 | 6 |
    | 2 | Danny Johnson | ORD-20161101-00343 | 2016-11-01 10:44:08 | 323500.0 | 7 |
    | 2 | Danny Johnson | ORD-20170122-00444 | 2017-01-22 08:39:07 | 480765.0 | 8 |
    | ... | ... | ... | ... | ... | ... |

---

### Problem 2

**Ranking monthly sales for 2024. If the sales are the same, the same ranking is given.**

Total sales for each month, display both `RANK` and `DENSE_RANK` values ​​to compare the differences.

??? tip "Hint"
    First, create a subquery (or CTE) that aggregates monthly sales with `SUBSTR(ordered_at, 1, 7)`,
    Apply `RANK() OVER (ORDER BY revenue DESC)` and `DENSE_RANK()` to the result.

??? success "Answer"
    ```sql
    WITH monthly_revenue AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        RANK()       OVER (ORDER BY revenue DESC) AS rank_val,
        DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank_val
    FROM monthly_revenue
    ORDER BY year_month;
    ```

    **Result example:**

    | year_month | revenue | rank_val | dense_rank_val |
    | ---------- | ----------: | ----------: | ----------: |
    | 2024-01 | 288908320.0 | 12 | 12 |
    | 2024-02 | 403127749.0 | 9 | 9 |
    | 2024-03 | 519844502.0 | 3 | 3 |
    | 2024-04 | 451877581.0 | 4 | 4 |
    | 2024-05 | 425264478.0 | 5 | 5 |
    | 2024-06 | 362715211.0 | 10 | 10 |
    | 2024-07 | 343929897.0 | 11 | 11 |
    | 2024-08 | 404803340.0 | 8 | 8 |
    | ... | ... | ... | ... |

    > `RANK` skips the next position in case of a tie, `DENSE_RANK` does not skip it.

---

### Problem 3

**In addition to the total sales for each product, find the percentage of sales within that category.**

As of 2024, the top 15 products are displayed in descending order of sales.

??? tip "Hint"
    Find the total sales of the category with `SUM(revenue) OVER (PARTITION BY category_id)`,
    Divide individual product sales by category sales to get the ratio.

??? success "Answer"
    ```sql
    SELECT
        p.name            AS product_name,
        cat.name          AS category,
        ROUND(SUM(oi.quantity * oi.unit_price), 0) AS product_revenue,
        ROUND(SUM(SUM(oi.quantity * oi.unit_price)) OVER (
            PARTITION BY p.category_id
        ), 0) AS category_revenue,
        ROUND(100.0 * SUM(oi.quantity * oi.unit_price)
            / SUM(SUM(oi.quantity * oi.unit_price)) OVER (PARTITION BY p.category_id),
        1) AS pct_of_category
    FROM order_items AS oi
    INNER JOIN orders     AS o   ON oi.order_id   = o.id
    INNER JOIN products   AS p   ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY p.id, p.name, cat.name, p.category_id
    ORDER BY product_revenue DESC
    LIMIT 15;
    ```

    **Result example (top 3 rows):**

    | product_name | category | product_revenue | category_revenue | pct_of_category |
    | ---------- | ---------- | ----------: | ----------: | ----------: |
    | Razer Blade 18 Black | Gaming Laptop | 165417800.0 | 636925700.0 | 26.0 |
    | Razer Blade 16 Silver | Gaming Laptop | 137007300.0 | 636925700.0 | 21.5 |
    | MacBook Air 15 M3 Silver | MacBook | 126065300.0 | 126065300.0 | 100.0 |
    | ASUS Dual RTX 4060 Ti Black | NVIDIA | 106992000.0 | 345858700.0 | 30.9 |
    | ASUS Dual RTX 5070 Ti Silver | NVIDIA | 104558400.0 | 345858700.0 | 30.2 |
    | ASUS ROG Swift PG32UCDM Silver | Gaming Monitor | 90734400.0 | 353934400.0 | 25.6 |
    | ASUS ROG Strix Scar 16 | Gaming Laptop | 85837500.0 | 636925700.0 | 13.5 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | NVIDIA | 85456000.0 | 345858700.0 | 24.7 |
    | ... | ... | ... | ... | ... |

---

### Problem 4

**Calculate a running total for each customer's order amount.**

For customer IDs 1 to 5, the cumulative order amount is displayed in order of order time.

??? tip "Hint"
    `SUM(total_amount) OVER (PARTITION BY customer_id ORDER BY ordered_at ROWS UNBOUNDED PRECEDING)`
    This statement creates a running total.

??? success "Answer"
    ```sql
    SELECT
        c.id            AS customer_id,
        c.name          AS customer_name,
        o.ordered_at,
        o.total_amount,
        SUM(o.total_amount) OVER (
            PARTITION BY c.id
            ORDER BY o.ordered_at
            ROWS UNBOUNDED PRECEDING
        ) AS running_total
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE c.id BETWEEN 1 AND 5
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY c.id, o.ordered_at;
    ```

    **Result example:**

    | customer_id | customer_name | ordered_at | total_amount | running_total |
    | ----------: | ---------- | ---------- | ----------: | ----------: |
    | 2 | Danny Johnson | 2016-08-17 23:29:34 | 2413300.0 | 2413300.0 |
    | 2 | Danny Johnson | 2016-08-19 22:29:34 | 298500.0 | 2711800.0 |
    | 2 | Danny Johnson | 2016-08-30 10:49:39 | 445700.0 | 3157500.0 |
    | 2 | Danny Johnson | 2016-09-04 08:47:04 | 597000.0 | 3754500.0 |
    | 2 | Danny Johnson | 2016-09-15 20:07:17 | 1760400.0 | 5514900.0 |
    | 2 | Danny Johnson | 2016-10-24 12:13:06 | 131500.0 | 5646400.0 |
    | 2 | Danny Johnson | 2016-11-01 10:44:08 | 323500.0 | 5969900.0 |
    | 2 | Danny Johnson | 2017-01-22 08:39:07 | 480765.0 | 6450665.0 |
    | ... | ... | ... | ... | ... |

---

### Problem 5

**Divide payment methods into 4 groups (quartiles) based on the number of payments.**

Payments completed in 2024 (`status = 'completed'`) are tallied by means, and quantified by `NTILE(4)`.

??? tip "Hint"
    First, create a CTE that counts the number of transactions by payment method,
    Divide into quartiles by `NTILE(4) OVER (ORDER BY payment_count DESC)`.
    Decile 1 is the most used group.

??? success "Answer"
    ```sql
    WITH method_stats AS (
        SELECT
            method,
            COUNT(*)              AS payment_count,
            ROUND(SUM(amount), 0) AS total_amount
        FROM payments
        WHERE status = 'completed'
          AND paid_at LIKE '2024%'
        GROUP BY method
    )
    SELECT
        method,
        payment_count,
        total_amount,
        NTILE(4) OVER (ORDER BY payment_count DESC) AS quartile
    FROM method_stats
    ORDER BY payment_count DESC;
    ```

    **Result example:**

    | method | payment_count | total_amount | quartile |
    | ---------- | ----------: | ----------: | ----------: |
    | card | 2374 | 2395888991.0 | 1 |
    | kakao_pay | 1058 | 1002822322.0 | 1 |
    | naver_pay | 810 | 719061948.0 | 2 |
    | bank_transfer | 516 | 483849949.0 | 2 |
    | point | 286 | 261926968.0 | 3 |
    | virtual_account | 276 | 250893342.0 | 4 |
    | ... | ... | ... | ... |

---

## Applied (6~10)

Utilizes analytical functions such as LAG/LEAD and moving average.

---

### Problem 6

**Find the increase/decrease and increase/decrease rate of monthly sales compared to the previous month.**

We use data from 2023 to 2024.

??? tip "Hint"
    Get the previous month's sales with `LAG(revenue, 1) OVER (ORDER BY year_month)`.
    The increase/decrease rate is calculated as `(current_month - previous_month) / previous_month * 100`.

??? success "Answer"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at >= '2023-01-01'
          AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        LAG(revenue, 1) OVER (ORDER BY year_month) AS prev_revenue,
        revenue - LAG(revenue, 1) OVER (ORDER BY year_month) AS diff,
        ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY year_month))
            / LAG(revenue, 1) OVER (ORDER BY year_month), 1) AS growth_pct
    FROM monthly
    ORDER BY year_month;
    ```

    **Result example (partial):**

    | year_month | revenue | prev_revenue | diff | growth_pct |
    | ---------- | ----------: | ---------- | ---------- | ---------- |
    | 2023-01 | 270083587.0 | (NULL) | (NULL) | (NULL) |
    | 2023-02 | 327431648.0 | 270083587.0 | 57348061.0 | 21.2 |
    | 2023-03 | 477735354.0 | 327431648.0 | 150303706.0 | 45.9 |
    | 2023-04 | 396849049.0 | 477735354.0 | -80886305.0 | -16.9 |
    | 2023-05 | 349749072.0 | 396849049.0 | -47099977.0 | -11.9 |
    | 2023-06 | 279698633.0 | 349749072.0 | -70050439.0 | -20.0 |
    | 2023-07 | 312983148.0 | 279698633.0 | 33284515.0 | 11.9 |
    | 2023-08 | 358275936.0 | 312983148.0 | 45292788.0 | 14.5 |
    | ... | ... | ... | ... | ... |

    > `prev_revenue` in the first row is NULL because there is no previous data.

---

### Problem 7

**Calculate the number of days until your customer's next order.**

For VIP-level customers, find the number of days between each order and the next order.
Show the top 10 people with the shortest average intervals.

??? tip "Hint"
    Get the next order date with `LEAD(ordered_at, 1) OVER (PARTITION BY customer_id ORDER BY ordered_at)`,
    Calculate the interval with `JULIANDAY(next_order) - JULIANDAY(ordered_at)`.

??? success "Answer"
    ```sql
    WITH order_gaps AS (
        SELECT
            o.customer_id,
            c.name,
            o.ordered_at,
            LEAD(o.ordered_at, 1) OVER (
                PARTITION BY o.customer_id
                ORDER BY o.ordered_at
            ) AS next_order_at,
            ROUND(
                JULIANDAY(LEAD(o.ordered_at, 1) OVER (
                    PARTITION BY o.customer_id
                    ORDER BY o.ordered_at
                )) - JULIANDAY(o.ordered_at),
            0) AS days_to_next
        FROM orders AS o
        INNER JOIN customers AS c ON o.customer_id = c.id
        WHERE c.grade = 'VIP'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        customer_id,
        name,
        COUNT(days_to_next)       AS gap_count,
        ROUND(AVG(days_to_next), 1) AS avg_days_between,
        MIN(days_to_next)           AS min_gap,
        MAX(days_to_next)           AS max_gap
    FROM order_gaps
    WHERE days_to_next IS NOT NULL
    GROUP BY customer_id, name
    ORDER BY avg_days_between ASC
    LIMIT 10;
    ```

    **Result example (top 3 rows):**

    | customer_id | name | gap_count | avg_days_between | min_gap | max_gap |
    | ----------: | ---------- | ----------: | ----------: | ----------: | ----------: |
    | 97 | Jason Rivera | 341 | 10.1 | 0.0 | 112.0 |
    | 226 | Allen Snyder | 302 | 10.8 | 0.0 | 89.0 |
    | 549 | Ronald Arellano | 218 | 12.0 | 0.0 | 74.0 |
    | 4840 | Jennifer Bradshaw | 6 | 12.0 | 0.0 | 26.0 |
    | 356 | Courtney Huff | 222 | 12.3 | 0.0 | 126.0 |
    | 162 | Brenda Garcia | 248 | 13.0 | 0.0 | 102.0 |
    | 98 | Gabriel Walters | 274 | 13.2 | 0.0 | 143.0 |
    | 1323 | Austin Townsend | 159 | 13.5 | 0.0 | 112.0 |
    | ... | ... | ... | ... | ... | ... |

---

### Problem 8

**Find the three-month moving average of sales.**

For monthly sales for 2023-2024, calculate the moving average of the three months preceding the current month.

??? tip "Hint"
    `AVG(revenue) OVER (ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`
    This statement calculates the average of the 2 rows preceding the current row (3 rows in total).

??? success "Answer"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at >= '2023-01-01'
          AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 0) AS moving_avg_3m,
        COUNT(*) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS window_size
    FROM monthly
    ORDER BY year_month;
    ```

    **Result example (partial):**

    | year_month | revenue | moving_avg_3m | window_size |
    | ---------- | ----------: | ----------: | ----------: |
    | 2023-01 | 270083587.0 | 270083587.0 | 1 |
    | 2023-02 | 327431648.0 | 298757618.0 | 2 |
    | 2023-03 | 477735354.0 | 358416863.0 | 3 |
    | 2023-04 | 396849049.0 | 400672017.0 | 3 |
    | 2023-05 | 349749072.0 | 408111158.0 | 3 |
    | 2023-06 | 279698633.0 | 342098918.0 | 3 |
    | 2023-07 | 312983148.0 | 314143618.0 | 3 |
    | 2023-08 | 358275936.0 | 316985906.0 | 3 |
    | ... | ... | ... | ... |

    > The initial rows where `window_size` is less than 3 are for reference only as the moving average is not accurate.

---

### Problem 9

**List the names of the most expensive and least expensive products in each category in one row.**

Use `FIRST_VALUE` and `LAST_VALUE`.

??? tip "Hint"
    `FIRST_VALUE(name) OVER (PARTITION BY category_id ORDER BY price DESC)` is the most expensive product name.
    When using `LAST_VALUE`, `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` must be specified to view the entire partition.

??? success "Answer"
    ```sql
    WITH ranked AS (
        SELECT DISTINCT
            cat.name AS category,
            FIRST_VALUE(p.name) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS most_expensive,
            FIRST_VALUE(p.price) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS max_price,
            LAST_VALUE(p.name) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS cheapest,
            LAST_VALUE(p.price) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS min_price
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
    )
    SELECT DISTINCT
        category,
        most_expensive,
        max_price,
        cheapest,
        min_price
    FROM ranked
    ORDER BY category;
    ```

    **Result example (top 3 rows):**

    | category | most_expensive | max_price | cheapest | min_price |
    | ---------- | ---------- | ----------: | ---------- | ----------: |
    | 2-in-1 | Lenovo ThinkPad X1 2in1 Silver | 1866100.0 | Samsung Galaxy Book5 360 Black | 1179900.0 |
    | AMD | AMD Ryzen 9 9900X | 591800.0 | AMD Ryzen 9 9900X | 335700.0 |
    | AMD | MSI Radeon RX 9070 XT GAMING X | 1896000.0 | MSI Radeon RX 9070 VENTUS 3X White | 383100.0 |
    | AMD Socket | ASRock B850M Pro RS Silver | 665600.0 | Gigabyte B650M AORUS ELITE AX | 376000.0 |
    | Air Cooling | Noctua NH-D15 G2 Black | 106000.0 | Arctic Freezer 36 A-RGB White | 23000.0 |
    | Barebone | ASUS ExpertCenter PN65 Silver | 722100.0 | ASUS ExpertCenter PN65 Silver | 722100.0 |
    | Case | NZXT H7 Flow Silver | 248700.0 | be quiet! Light Base 900 | 85300.0 |
    | Custom Build | ASUS ROG Strix G16CH White | 3671500.0 | Hansung BossMonster DX9900 Silver | 739900.0 |
    | ... | ... | ... | ... | ... |

---

### Problem 10

**Divide products into 5 grades (NTILE) based on review ratings and obtain statistics for each grade.**

Only products with 3 or more reviews are eligible.

??? tip "Hint"
    First, find the average rating for each product (`HAVING COUNT(*) >= 3`),
    After dividing the result into `NTILE(5) OVER (ORDER BY avg_rating)`,
    We count again by grade.

??? success "Answer"
    ```sql
    WITH product_ratings AS (
        SELECT
            p.id,
            p.name,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(*)                AS review_count
        FROM reviews AS r
        INNER JOIN products AS p ON r.product_id = p.id
        GROUP BY p.id, p.name
        HAVING COUNT(*) >= 3
    ),
    tiered AS (
        SELECT
            *,
            NTILE(5) OVER (ORDER BY avg_rating) AS tier
        FROM product_ratings
    )
    SELECT
        tier,
        COUNT(*)                     AS product_count,
        ROUND(MIN(avg_rating), 2)    AS min_rating,
        ROUND(MAX(avg_rating), 2)    AS max_rating,
        ROUND(AVG(avg_rating), 2)    AS avg_of_avg,
        ROUND(AVG(review_count), 1)  AS avg_reviews
    FROM tiered
    GROUP BY tier
    ORDER BY tier;
    ```

    **Result example:**

    | tier | product_count | min_rating | max_rating | avg_of_avg | avg_reviews |
    | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: |
    | 1 | 53 | 3.0 | 3.68 | 3.5 | 23.2 |
    | 2 | 53 | 3.7 | 3.83 | 3.76 | 33.9 |
    | 3 | 53 | 3.83 | 3.97 | 3.9 | 42.2 |
    | 4 | 53 | 3.97 | 4.1 | 4.02 | 33.7 |
    | 5 | 52 | 4.1 | 4.8 | 4.26 | 28.3 |
    | ... | ... | ... | ... | ... | ... |

---

## Practical (11~15)

Solve practical analysis scenarios with complex window function combinations.

---

### Problem 11

**Rank order amount by customer level and extract information from the top 3 people within the level.**

Shows the top 3 players in each tier (BRONZE, SILVER, GOLD, VIP) by total order value.

??? tip "Hint"
    After tallying up the total order amount for each customer in CTE, enter `ROW_NUMBER() OVER (PARTITION BY grade ORDER BY total_spent DESC)`
    Rank by rating and filter by `WHERE rn <= 3` in the outer query.

??? success "Answer"
    ```sql
    WITH customer_totals AS (
        SELECT
            c.id,
            c.name,
            c.grade,
            COUNT(*)                    AS order_count,
            ROUND(SUM(o.total_amount), 0) AS total_spent
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    ),
    ranked AS (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY grade
                ORDER BY total_spent DESC
            ) AS rn
        FROM customer_totals
    )
    SELECT
        grade,
        rn   AS rank_in_grade,
        name AS customer_name,
        order_count,
        total_spent
    FROM ranked
    WHERE rn <= 3
    ORDER BY
        CASE grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
        END,
        rn;
    ```

    **Result example:**

    | grade | rank_in_grade | customer_name | order_count | total_spent |
    |---|---|---|---|---|
    | VIP | 1 | 김... | 35 | 12500000 |
    | VIP | 2 | 박... | 28 | 10800000 |
    | VIP | 3 | 이... | 31 | 9950000 |
    | GOLD | 1 | 최... | 22 | 7200000 |
    | ... | ... | ... | ... | ... |

---

### Problem 12

**Display the monthly sales trend for each product and the ratio compared to the overall average for that product.**

For the top five products in 2024, find the monthly sales and the ratio (%) of the average monthly sales for all products.

??? tip "Hint"
    Step 1: Calculate product-monthly sales. Step 2: Select the top five products (based on total sales).
    Step 3: Find the overall average for each product with `AVG(monthly_revenue) OVER (PARTITION BY product_id)`,
    Calculate the ratio by dividing your monthly sales by the average.

??? success "Answer"
    ```sql
    WITH product_monthly AS (
        SELECT
            p.id       AS product_id,
            p.name     AS product_name,
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS monthly_revenue
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name, SUBSTR(o.ordered_at, 1, 7)
    ),
    top5 AS (
        SELECT product_id
        FROM product_monthly
        GROUP BY product_id
        ORDER BY SUM(monthly_revenue) DESC
        LIMIT 5
    )
    SELECT
        pm.product_name,
        pm.year_month,
        pm.monthly_revenue,
        ROUND(AVG(pm.monthly_revenue) OVER (
            PARTITION BY pm.product_id
        ), 0) AS avg_monthly,
        ROUND(100.0 * pm.monthly_revenue
            / AVG(pm.monthly_revenue) OVER (PARTITION BY pm.product_id),
        1) AS pct_of_avg
    FROM product_monthly AS pm
    INNER JOIN top5 AS t ON pm.product_id = t.product_id
    ORDER BY pm.product_name, pm.year_month;
    ```

    **Result example (partial):**

    | product_name | year_month | monthly_revenue | avg_monthly | pct_of_avg |
    | ---------- | ---------- | ----------: | ----------: | ----------: |
    | ASUS Dual RTX 4060 Ti Black | 2024-01 | 8024400.0 | 8916000.0 | 90.0 |
    | ASUS Dual RTX 4060 Ti Black | 2024-02 | 8024400.0 | 8916000.0 | 90.0 |
    | ASUS Dual RTX 4060 Ti Black | 2024-03 | 8024400.0 | 8916000.0 | 90.0 |
    | ASUS Dual RTX 4060 Ti Black | 2024-04 | 13374000.0 | 8916000.0 | 150.0 |
    | ASUS Dual RTX 4060 Ti Black | 2024-05 | 5349600.0 | 8916000.0 | 60.0 |
    | ... | ... | ... | ... | ... |

---

### Problem 13

**Track monthly share changes by payment method.**

Calculate the share (%) of each payment method by month in 2024 and calculate the change in share (pp) compared to the previous month.

??? tip "Hint"
    After finding the monthly amount by payment method, calculate the total monthly total with `SUM(amount) OVER (PARTITION BY year_month)`.
    Get the previous month's market share with `LAG(share_pct, 1) OVER (PARTITION BY method ORDER BY year_month)`.

??? success "Answer"
    ```sql
    WITH method_monthly AS (
        SELECT
            SUBSTR(paid_at, 1, 7) AS year_month,
            method,
            ROUND(SUM(amount), 0) AS method_amount
        FROM payments
        WHERE status = 'completed'
          AND paid_at LIKE '2024%'
        GROUP BY SUBSTR(paid_at, 1, 7), method
    ),
    with_share AS (
        SELECT
            year_month,
            method,
            method_amount,
            ROUND(100.0 * method_amount
                / SUM(method_amount) OVER (PARTITION BY year_month),
            1) AS share_pct
        FROM method_monthly
    )
    SELECT
        year_month,
        method,
        method_amount,
        share_pct,
        LAG(share_pct, 1) OVER (
            PARTITION BY method
            ORDER BY year_month
        ) AS prev_share_pct,
        ROUND(share_pct - LAG(share_pct, 1) OVER (
            PARTITION BY method
            ORDER BY year_month
        ), 1) AS share_change_pp
    FROM with_share
    ORDER BY year_month, share_pct DESC;
    ```

    **Result example (partial):**

    | year_month | method | method_amount | share_pct | prev_share_pct | share_change_pp |
    | ---------- | ---------- | ----------: | ----------: | ---------- | ---------- |
    | 2024-01 | card | 147207539.0 | 51.0 | (NULL) | (NULL) |
    | 2024-01 | kakao_pay | 53100585.0 | 18.4 | (NULL) | (NULL) |
    | 2024-01 | naver_pay | 33230574.0 | 11.5 | (NULL) | (NULL) |
    | 2024-01 | bank_transfer | 24355270.0 | 8.4 | (NULL) | (NULL) |
    | 2024-01 | virtual_account | 17502152.0 | 6.1 | (NULL) | (NULL) |
    | 2024-01 | point | 13512200.0 | 4.7 | (NULL) | (NULL) |
    | 2024-02 | card | 169679102.0 | 42.1 | 51.0 | -8.9 |
    | 2024-02 | naver_pay | 80746191.0 | 20.0 | 11.5 | 8.5 |
    | ... | ... | ... | ... | ... | ... |

---

### Problem 14

**Perform gap analysis of order amount for each customer.**

각 고객의 주문을 금액 순으로 정렬했을 때, 이전 주문 대비 금액 차이가 가장 큰 "점프"를 찾습니다.
Extract only if the jump amount is more than 500,000 won.

??? tip "Hint"
    to `LAG(total_amount, 1) OVER (PARTITION BY customer_id ORDER BY total_amount)`
    Amount Net Get the amount of the previous order. Find the difference and filter only rows that are over 500,000 won.

??? success "Answer"
    ```sql
    WITH ordered AS (
        SELECT
            o.customer_id,
            c.name,
            o.order_number,
            o.total_amount,
            LAG(o.total_amount, 1) OVER (
                PARTITION BY o.customer_id
                ORDER BY o.total_amount
            ) AS prev_amount
        FROM orders AS o
        INNER JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        customer_id,
        name,
        order_number,
        prev_amount,
        total_amount,
        total_amount - prev_amount AS gap
    FROM ordered
    WHERE prev_amount IS NOT NULL
      AND (total_amount - prev_amount) >= 500000
    ORDER BY gap DESC
    LIMIT 20;
    ```

    **Result example (top 3 rows):**

    | customer_id | name | order_number | prev_amount | total_amount | gap |
    | ----------: | ---------- | ---------- | ----------: | ----------: | ----------: |
    | 514 | Steven Johnson | ORD-20201121-08810 | 837600.0 | 50867500.0 | 50029900.0 |
    | 3774 | Dylan Green | ORD-20250305-32265 | 6346600.0 | 46820024.0 | 40473424.0 |
    | 4136 | Zachary Ford | ORD-20251218-37240 | 405600.0 | 38626400.0 | 38220800.0 |
    | 1322 | Donald Landry | ORD-20220106-15263 | 1898100.0 | 37987600.0 | 36089500.0 |
    | 3 | Adam Moore | ORD-20200209-05404 | 9690532.0 | 43677500.0 | 33986968.0 |
    | 551 | Katie Warner | ORD-20200820-07684 | 4885100.0 | 37518200.0 | 32633100.0 |
    | 4965 | Sandra Williams | ORD-20251207-37004 | 369800.0 | 31985600.0 | 31615800.0 |
    | 3167 | Mitchell Wilkinson | ORD-20221108-19517 | 2845300.0 | 33599000.0 | 30753700.0 |
    | ... | ... | ... | ... | ... | ... |

---

### Problem 15

**Calculate year-on-year (YoY) sales growth rate using a window function, and also display quarterly trends.**

Find sales for each quarter, sales for the same quarter last year, and YoY growth rate.

??? tip "Hint"
    Branches are calculated as `(CAST(SUBSTR(ordered_at,6,2) AS INTEGER) + 2) / 3`.
    Get the value from 4 quarters ago (= same quarter of previous year) with `LAG(revenue, 4) OVER (ORDER BY year, quarter)`.

??? success "Answer"
    ```sql
    WITH quarterly AS (
        SELECT
            CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER) AS year,
            (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3 AS quarter,
            ROUND(SUM(total_amount), 0) AS revenue,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2020-01-01'
        GROUP BY
            CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER),
            (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3
    )
    SELECT
        year,
        quarter,
        revenue,
        order_count,
        LAG(revenue, 4) OVER (ORDER BY year, quarter) AS prev_year_revenue,
        CASE
            WHEN LAG(revenue, 4) OVER (ORDER BY year, quarter) IS NOT NULL
            THEN ROUND(100.0 * (revenue - LAG(revenue, 4) OVER (ORDER BY year, quarter))
                / LAG(revenue, 4) OVER (ORDER BY year, quarter), 1)
        END AS yoy_growth_pct
    FROM quarterly
    ORDER BY year, quarter;
    ```

    **Result example (partial):**

    | year | quarter | revenue | order_count | prev_year_revenue | yoy_growth_pct |
    | ----------: | ----------: | ----------: | ----------: | ---------- | ---------- |
    | 2020 | 1 | 1001221410.0 | 990 | (NULL) | (NULL) |
    | 2020 | 2 | 991211380.0 | 982 | (NULL) | (NULL) |
    | 2020 | 3 | 1009837258.0 | 964 | (NULL) | (NULL) |
    | 2020 | 4 | 1086405018.0 | 1084 | (NULL) | (NULL) |
    | 2021 | 1 | 1458348254.0 | 1351 | 1001221410.0 | 45.7 |
    | 2021 | 2 | 1210987985.0 | 1143 | 991211380.0 | 22.2 |
    | 2021 | 3 | 1361699965.0 | 1412 | 1009837258.0 | 34.8 |
    | 2021 | 4 | 1507109679.0 | 1515 | 1086405018.0 | 38.7 |
    | ... | ... | ... | ... | ... | ... |

    > For the first year (2020), there is no data from the previous year, so `prev_year_revenue` and `yoy_growth_pct` are NULL.
