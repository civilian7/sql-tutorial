# Window Functions in Practice

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `orders` — orders (status, amount, date/time)<br>
    `order_items` — Order details (quantity, unit price)<br>
    `products` — products (name, price, stock, brand)<br>
    `customers` — customers (tier, points, signup channel)<br>
    `reviews` — reviews (rating, content)<br>
    `payments` — payments (method, amount, status)<br>
    `categories` — Category (parent-child hierarchy)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    `ROW_NUMBER`<br>
    `RANK`<br>
    `DENSE_RANK`<br>
    `NTILE`<br>
    `LAG`<br>
    `LEAD`<br>
    `SUM/AVG/COUNT OVER`<br>
    `FIRST_VALUE`<br>
    `LAST_VALUE`<br>
    `ROWS BETWEEN`

</div>

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
    | 2 | 김경수 | ORD-20160807-04161 | 2016-08-18 09:29:34 | 139200.0 | 1 |
    | 2 | 김경수 | ORD-20160829-04654 | 2016-08-29 19:59:53 | 323700.0 | 2 |
    | 2 | 김경수 | ORD-20160906-04838 | 2016-09-06 20:05:02 | 149200.0 | 3 |
    | 2 | 김경수 | ORD-20160910-04917 | 2016-09-10 14:59:59 | 2501100.0 | 4 |
    | 2 | 김경수 | ORD-20161001-05339 | 2016-10-01 19:40:13 | 166100.0 | 5 |
    | 2 | 김경수 | ORD-20161004-05388 | 2016-10-04 12:18:11 | 520500.0 | 6 |
    | 2 | 김경수 | ORD-20161012-05536 | 2016-10-12 22:54:00 | 1950710.0 | 7 |
    | 2 | 김경수 | ORD-20161101-05925 | 2016-11-01 04:47:42 | 898700.0 | 8 |
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
    | 2024-01 | 3737010508.0 | 12 | 12 |
    | 2024-02 | 4630208028.0 | 9 | 9 |
    | 2024-03 | 4811012761.0 | 6 | 6 |
    | 2024-04 | 4852046384.0 | 5 | 5 |
    | 2024-05 | 4796192371.0 | 7 | 7 |
    | 2024-06 | 3787186898.0 | 11 | 11 |
    | 2024-07 | 4370145415.0 | 10 | 10 |
    | 2024-08 | 4778870727.0 | 8 | 8 |
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
    | ASUS Dual RTX 4060 Ti 실버 | NVIDIA | 364990000.0 | 6049128000.0 | 6.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 블랙 | NVIDIA | 306205800.0 | 6049128000.0 | 5.1 |
    | ASUS ROG STRIX RTX 4090 화이트 | NVIDIA | 294856000.0 | 6049128000.0 | 4.9 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | NVIDIA | 268482500.0 | 6049128000.0 | 4.4 |
    | 기가바이트 RTX 4060 EAGLE OC 실버 | NVIDIA | 253128000.0 | 6049128000.0 | 4.2 |
    | ASUS Dual RTX 4060 Ti | NVIDIA | 244458400.0 | 6049128000.0 | 4.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | NVIDIA | 240453200.0 | 6049128000.0 | 4.0 |
    | AMD Ryzen 7 7700X 블랙 | AMD | 237618000.0 | 1078208100.0 | 22.0 |
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
    | 2 | 김경수 | 2016-08-18 09:29:34 | 139200.0 | 139200.0 |
    | 2 | 김경수 | 2016-08-29 19:59:53 | 323700.0 | 462900.0 |
    | 2 | 김경수 | 2016-09-06 20:05:02 | 149200.0 | 612100.0 |
    | 2 | 김경수 | 2016-09-10 14:59:59 | 2501100.0 | 3113200.0 |
    | 2 | 김경수 | 2016-10-01 19:40:13 | 166100.0 | 3279300.0 |
    | 2 | 김경수 | 2016-10-04 12:18:11 | 520500.0 | 3799800.0 |
    | 2 | 김경수 | 2016-10-12 22:54:00 | 1950710.0 | 5750510.0 |
    | 2 | 김경수 | 2016-11-01 04:47:42 | 898700.0 | 6649210.0 |
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
    | card | 26633 | 27099300084.0 | 1 |
    | kakao_pay | 11705 | 11870784619.0 | 1 |
    | naver_pay | 8885 | 9015902948.0 | 2 |
    | bank_transfer | 5971 | 5967951548.0 | 2 |
    | point | 2928 | 2916576234.0 | 3 |
    | virtual_account | 2890 | 3058991818.0 | 4 |
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
    | 2023-01 | 3194383488.0 | (NULL) | (NULL) | (NULL) |
    | 2023-02 | 3783544299.0 | 3194383488.0 | 589160811.0 | 18.4 |
    | 2023-03 | 4798857428.0 | 3783544299.0 | 1015313129.0 | 26.8 |
    | 2023-04 | 4683448161.0 | 4798857428.0 | -115409267.0 | -2.4 |
    | 2023-05 | 4023692043.0 | 4683448161.0 | -659756118.0 | -14.1 |
    | 2023-06 | 3443896173.0 | 4023692043.0 | -579795870.0 | -14.4 |
    | 2023-07 | 3189823743.0 | 3443896173.0 | -254072430.0 | -7.4 |
    | 2023-08 | 4236240498.0 | 3189823743.0 | 1046416755.0 | 32.8 |
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
    | 45487 | 송유진 | 1 | 0.0 | 0.0 | 0.0 |
    | 49554 | 박서윤 | 2 | 1.5 | 1.0 | 2.0 |
    | 50742 | 이정남 | 4 | 3.5 | 2.0 | 6.0 |
    | 49904 | 류은주 | 4 | 5.3 | 0.0 | 18.0 |
    | 226 | 박정수 | 650 | 5.6 | 0.0 | 63.0 |
    | 356 | 정유진 | 536 | 6.6 | 0.0 | 72.0 |
    | 840 | 문영숙 | 538 | 6.8 | 0.0 | 130.0 |
    | 1000 | 이미정 | 515 | 6.8 | 0.0 | 131.0 |
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
    | 2023-01 | 3194383488.0 | 3194383488.0 | 1 |
    | 2023-02 | 3783544299.0 | 3488963894.0 | 2 |
    | 2023-03 | 4798857428.0 | 3925595072.0 | 3 |
    | 2023-04 | 4683448161.0 | 4421949963.0 | 3 |
    | 2023-05 | 4023692043.0 | 4501999211.0 | 3 |
    | 2023-06 | 3443896173.0 | 4050345459.0 | 3 |
    | 2023-07 | 3189823743.0 | 3552470653.0 | 3 |
    | 2023-08 | 4236240498.0 | 3623320138.0 | 3 |
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
    | 2in1 | 레노버 IdeaPad Flex 5 화이트 | 2914000.0 | HP Pavilion x360 14 | 720800.0 |
    | AMD | AMD Ryzen 7 7700X 블랙 | 1105200.0 | AMD Ryzen 7 9800X3D 실버 [특별 한정판 에디션] RGB 라이팅 탑재, 소프트웨어 커스터마이징 지원 | 182100.0 |
    | AMD | SAPPHIRE PULSE RX 7800 XT 블랙 | 2158800.0 | ASUS ROG STRIX RX 7900 XTX 블랙 | 374500.0 |
    | AMD 소켓 | ASUS ROG STRIX B850-F GAMING 실버 | 924400.0 | MSI MAG X870E TOMAHAWK WIFI | 125900.0 |
    | DDR4 | 삼성 DDR4 8GB PC4-25600 실버 | 136800.0 | SK하이닉스 DDR4 32GB PC4-25600 | 25700.0 |
    | DDR5 | G.SKILL Ripjaws S5 DDR5 32GB 6400MHz 블랙 | 441700.0 | Kingston FURY Beast DDR5 64GB 6000MHz 화이트 | 50800.0 |
    | HDD | Seagate BarraCuda 2TB 화이트 | 611900.0 | WD Gold 12TB 블랙 | 43400.0 |
    | Intel 소켓 | 기가바이트 B760M AORUS ELITE | 975800.0 | ASRock B860M Pro RS 화이트 | 107000.0 |
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
    | 1 | 535 | 2.0 | 3.71 | 3.52 | 26.0 |
    | 2 | 535 | 3.71 | 3.85 | 3.79 | 40.9 |
    | 3 | 535 | 3.85 | 3.97 | 3.91 | 46.0 |
    | 4 | 535 | 3.97 | 4.09 | 4.03 | 39.6 |
    | 5 | 534 | 4.09 | 5.0 | 4.27 | 25.5 |
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
    | ASUS Dual RTX 4060 Ti 실버 | 2024-01 | 21470000.0 | 30415833.0 | 70.6 |
    | ASUS Dual RTX 4060 Ti 실버 | 2024-02 | 30058000.0 | 30415833.0 | 98.8 |
    | ASUS Dual RTX 4060 Ti 실버 | 2024-03 | 21470000.0 | 30415833.0 | 70.6 |
    | ASUS Dual RTX 4060 Ti 실버 | 2024-04 | 21470000.0 | 30415833.0 | 70.6 |
    | ASUS Dual RTX 4060 Ti 실버 | 2024-05 | 51528000.0 | 30415833.0 | 169.4 |
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
    | 2024-01 | card | 1637985623.0 | 43.8 | (NULL) | (NULL) |
    | 2024-01 | kakao_pay | 701582674.0 | 18.8 | (NULL) | (NULL) |
    | 2024-01 | naver_pay | 604077057.0 | 16.1 | (NULL) | (NULL) |
    | 2024-01 | bank_transfer | 397750334.0 | 10.6 | (NULL) | (NULL) |
    | 2024-01 | virtual_account | 209801928.0 | 5.6 | (NULL) | (NULL) |
    | 2024-01 | point | 189862292.0 | 5.1 | (NULL) | (NULL) |
    | 2024-02 | card | 2157466285.0 | 46.6 | 43.8 | 2.8 |
    | 2024-02 | kakao_pay | 794741444.0 | 17.2 | 18.8 | -1.6 |
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
    | 3059 | 윤유진 | ORD-20230408-248697 | 1249400.0 | 71906300.0 | 70656900.0 |
    | 32129 | 김영호 | ORD-20240218-293235 | 6525100.0 | 68948100.0 | 62423000.0 |
    | 15801 | 한예은 | ORD-20230626-259827 | 885200.0 | 61811500.0 | 60926300.0 |
    | 40387 | 이성진 | ORD-20240822-323378 | 5015500.0 | 64332900.0 | 59317400.0 |
    | 942 | 박광수 | ORD-20180516-26809 | 5420400.0 | 63466900.0 | 58046500.0 |
    | 35583 | 고광수 | ORD-20231002-272459 | 2882500.0 | 58539900.0 | 55657400.0 |
    | 6840 | 최경자 | ORD-20200429-82365 | 6392700.0 | 61889000.0 | 55496300.0 |
    | 5657 | 김서영 | ORD-20220731-207855 | 3879200.0 | 57495600.0 | 53616400.0 |
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
    | 2020 | 1 | 10247095614.0 | 9867 | (NULL) | (NULL) |
    | 2020 | 2 | 10474089855.0 | 10049 | (NULL) | (NULL) |
    | 2020 | 3 | 10995490467.0 | 10796 | (NULL) | (NULL) |
    | 2020 | 4 | 12630611449.0 | 12395 | (NULL) | (NULL) |
    | 2021 | 1 | 13795824579.0 | 13513 | 10247095614.0 | 34.6 |
    | 2021 | 2 | 11884721583.0 | 11729 | 10474089855.0 | 13.5 |
    | 2021 | 3 | 12933953963.0 | 12748 | 10995490467.0 | 17.6 |
    | 2021 | 4 | 18183527492.0 | 17641 | 12630611449.0 | 44.0 |
    | ... | ... | ... | ... | ... | ... |

    > For the first year (2020), there is no data from the previous year, so `prev_year_revenue` and `yoy_growth_pct` are NULL.
