# CTE Applications

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `categories` — Category (parent-child hierarchy)<br>
    `staff` — Employee (Manager Hierarchy)<br>
    `orders` — orders (status, amount, date/time)<br>
    `customers` — customers (tier, points, signup channel)<br>
    `order_items` — Order details (quantity, unit price)<br>
    `products` — products (name, price, stock, brand)<br>
    `calendar` — Date reference (holidays, weekends)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    `WITH`<br>
    Recursive CTE(`WITH RECURSIVE`)<br>
    Multiple CTE Chaining<br>
    CTE + Aggregate/JOIN/Window Function

</div>

!!! info "Before You Begin"
    This exercise puts into practice what you learned in **Advanced Lesson 19** (CTE).
    Recursive CTEs are used in SQLite with the `WITH RECURSIVE` syntax.
    Cancellation/return order exclusion conditions: `status NOT IN ('cancelled', 'returned', 'return_requested')`

---

## Basic (1~5)

Practice single CTE and CTE + JOIN/aggregation.

---

### Problem 1

**Find monthly sales in 2024 in CTE, and view only months with sales above the overall average.**

??? tip "Hint"
    After collecting monthly sales in CTE, use `WHERE revenue >= (SELECT AVG(revenue) FROM cte_name)` in external query.
    Filter. CTE may be referenced multiple times.

??? success "Answer"
    ```sql
    WITH monthly_revenue AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue,
            COUNT(*) AS order_count
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        order_count,
        (SELECT ROUND(AVG(revenue), 0) FROM monthly_revenue) AS avg_revenue,
        CASE
            WHEN revenue >= (SELECT AVG(revenue) FROM monthly_revenue) THEN 'Above average'
            ELSE 'Below average'
        END AS status
    FROM monthly_revenue
    WHERE revenue >= (SELECT AVG(revenue) FROM monthly_revenue)
    ORDER BY revenue DESC;
    ```

    **Result example:**

    | year_month | revenue | order_count | avg_revenue | status |
    | ---------- | ----------: | ----------: | ----------: | ---------- |
    | 2024-12 | 7171062836.0 | 6919 | 4993798863.0 | Above average |
    | 2024-11 | 6557769842.0 | 6240 | 4993798863.0 | Above average |
    | 2024-09 | 5398216952.0 | 5124 | 4993798863.0 | Above average |
    | 2024-10 | 5035863629.0 | 5068 | 4993798863.0 | Above average |

---

### Problem 2

**Find the total purchase amount for each customer in CTE, then extract the top 5 customers by grade.**

Combines CTE and `ROW_NUMBER` window functions.

??? tip "Hint"
    In the first CTE, aggregate the total purchase amount by customer,
    Apply `ROW_NUMBER() OVER (PARTITION BY grade ORDER BY total_spent DESC)` in the second CTE.

??? success "Answer"
    ```sql
    WITH customer_totals AS (
        SELECT
            c.id,
            c.name,
            c.grade,
            ROUND(SUM(o.total_amount), 0) AS total_spent,
            COUNT(*) AS order_count
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
        rn AS rank_in_grade,
        name,
        order_count,
        total_spent
    FROM ranked
    WHERE rn <= 5
    ORDER BY
        CASE grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
        END,
        rn;
    ```

    **Result example (partial):**

    | grade | rank_in_grade | name | order_count | total_spent |
    |---|---|---|---|---|
    | VIP | 1 | 김... | 35 | 12500000 |
    | VIP | 2 | 박... | 28 | 10800000 |
    | ... | ... | ... | ... | ... |
    | BRONZE | 5 | 한... | 3 | 450000 |

---

### Problem 3

**Use CTE to view sales and review summaries for each product at once.**

Displays the sales amount, sales volume, number of reviews, and average rating of the top 10 selling products in 2024.

??? tip "Hint"
    Create the sales CTE and review CTE separately, then combine them into `LEFT JOIN` in the external query.
    Products without reviews should also be included.

??? success "Answer"
    ```sql
    WITH sales AS (
        SELECT
            oi.product_id,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
            SUM(oi.quantity) AS units_sold
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY oi.product_id
    ),
    review_summary AS (
        SELECT
            product_id,
            COUNT(*) AS review_count,
            ROUND(AVG(rating), 2) AS avg_rating
        FROM reviews
        GROUP BY product_id
    )
    SELECT
        p.name          AS product_name,
        cat.name        AS category,
        s.units_sold,
        s.total_revenue,
        COALESCE(r.review_count, 0) AS review_count,
        r.avg_rating
    FROM sales AS s
    INNER JOIN products   AS p   ON s.product_id  = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LEFT  JOIN review_summary AS r ON s.product_id = r.product_id
    ORDER BY s.total_revenue DESC
    LIMIT 10;
    ```

    **Result example (top 3 rows):**

    | product_name | category | units_sold | total_revenue | review_count | avg_rating |
    | ---------- | ---------- | ----------: | ----------: | ----------: | ----------: |
    | ASUS Dual RTX 4060 Ti 실버 | NVIDIA | 85 | 364990000.0 | 21 | 3.76 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 블랙 | NVIDIA | 73 | 306205800.0 | 11 | 2.82 |
    | ASUS ROG STRIX RTX 4090 화이트 | NVIDIA | 80 | 294856000.0 | 16 | 3.69 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | NVIDIA | 55 | 268482500.0 | 30 | 3.8 |
    | 기가바이트 RTX 4060 EAGLE OC 실버 | NVIDIA | 60 | 253128000.0 | 21 | 3.62 |
    | ASUS Dual RTX 4060 Ti | NVIDIA | 58 | 244458400.0 | 8 | 4.5 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | NVIDIA | 52 | 240453200.0 | 26 | 3.85 |
    | AMD Ryzen 7 7700X 블랙 | AMD | 215 | 237618000.0 | 77 | 3.88 |
    | ... | ... | ... | ... | ... | ... |

---

### Problem 4

**Practice chaining, where you aggregate results from one CTE and filter them from another CTE.**

Find the number of new subscribers per month and look for “surge” months, which are month-on-month increases of 20% or more.

??? tip "Hint"
    CTE 1: Counting the number of new subscribers per month. CTE 2: Calculate the change rate by taking the previous month's figures with `LAG`.
    In the outer query, filter only rows with growth rate >= 20.

??? success "Answer"
    ```sql
    WITH monthly_signups AS (
        SELECT
            SUBSTR(created_at, 1, 7) AS year_month,
            COUNT(*) AS signup_count
        FROM customers
        WHERE created_at >= '2022-01-01'
        GROUP BY SUBSTR(created_at, 1, 7)
    ),
    with_growth AS (
        SELECT
            year_month,
            signup_count,
            LAG(signup_count, 1) OVER (ORDER BY year_month) AS prev_count,
            ROUND(100.0 * (signup_count - LAG(signup_count, 1) OVER (ORDER BY year_month))
                / LAG(signup_count, 1) OVER (ORDER BY year_month), 1) AS growth_pct
        FROM monthly_signups
    )
    SELECT
        year_month,
        signup_count,
        prev_count,
        growth_pct
    FROM with_growth
    WHERE growth_pct >= 20
    ORDER BY growth_pct DESC;
    ```

    **Result example:**

    | year_month | signup_count | prev_count | growth_pct |
    | ---------- | ----------: | ----------: | ----------: |
    | 2025-01 | 693 | 577 | 20.1 |

---

### Problem 5

**Find the proportion of sales by category in CTE and calculate the cumulative proportion (Pareto).**

Calculate sales by category as of 2024 and display cumulative proportions in descending order.

??? tip "Hint"
    After counting sales by category in CTE,
    Find the cumulative proportion with `SUM(share_pct) OVER (ORDER BY revenue DESC ROWS UNBOUNDED PRECEDING)`.

??? success "Answer"
    ```sql
    WITH category_revenue AS (
        SELECT
            cat.name AS category,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM order_items AS oi
        INNER JOIN orders     AS o   ON oi.order_id   = o.id
        INNER JOIN products   AS p   ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY cat.name
    ),
    with_share AS (
        SELECT
            category,
            revenue,
            ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS share_pct
        FROM category_revenue
    )
    SELECT
        category,
        revenue,
        share_pct,
        ROUND(SUM(share_pct) OVER (
            ORDER BY revenue DESC
            ROWS UNBOUNDED PRECEDING
        ), 1) AS cumulative_pct
    FROM with_share
    ORDER BY revenue DESC;
    ```

    **Result example (top 5 rows):**

    | category | revenue | share_pct | cumulative_pct |
    | ---------- | ----------: | ----------: | ----------: |
    | 게이밍 노트북 | 7252261700.0 | 12.0 | 12.0 |
    | NVIDIA | 6049128000.0 | 10.0 | 22.0 |
    | AMD | 5055980700.0 | 8.4 | 30.4 |
    | 일반 노트북 | 4852629300.0 | 8.0 | 38.4 |
    | 게이밍 모니터 | 3575676600.0 | 5.9 | 44.3 |
    | 스피커/헤드셋 | 2473846600.0 | 4.1 | 48.4 |
    | Intel 소켓 | 2265205100.0 | 3.7 | 52.1 |
    | 2in1 | 2164737100.0 | 3.6 | 55.7 |
    | ... | ... | ... | ... |

---

## Applied (6~10)

Utilizes recursive CTEs and multiple CTEs.

---

### Problem 6

**Expand your category hierarchy into recursive CTEs.**

Displays the entire path, from the top category (parent_id IS NULL) to subcategories.

??? tip "Hint"
    Use `WITH RECURSIVE`. Anchor member: `WHERE parent_id IS NULL`.
    Recursive member: JOIN CTE itself and `categories` with `c.parent_id = cte.id`.
    The path connects to `parent_path || ' > ' || c.name`.

??? success "Answer"
    ```sql
    WITH RECURSIVE cat_tree AS (
        -- Anchor: top-level categories
        SELECT
            id,
            parent_id,
            name,
            name AS full_path,
            depth,
            0 AS level
        FROM categories
        WHERE parent_id IS NULL

        UNION ALL

        -- Recursive: child categories
        SELECT
            c.id,
            c.parent_id,
            c.name,
            ct.full_path || ' > ' || c.name,
            c.depth,
            ct.level + 1
        FROM categories AS c
        INNER JOIN cat_tree AS ct ON c.parent_id = ct.id
    )
    SELECT
        id,
        full_path,
        level,
        depth
    FROM cat_tree
    ORDER BY full_path;
    ```

    **Result example (partial):**

    | id | full_path | level | depth |
    | ----------: | ---------- | ----------: | ----------: |
    | 14 | CPU | 0 | 0 |
    | 16 | CPU > AMD | 1 | 1 |
    | 15 | CPU > Intel | 1 | 1 |
    | 49 | UPS/전원 | 0 | 0 |
    | 27 | 그래픽카드 | 0 | 0 |
    | 29 | 그래픽카드 > AMD | 1 | 1 |
    | 28 | 그래픽카드 > NVIDIA | 1 | 1 |
    | 45 | 네트워크 장비 | 0 | 0 |
    | ... | ... | ... | ... |

---

### Problem 7

**Expand your employee org chart as a recursive CTE.**

Displays the path to every employee's immediate supervisor, starting with the manager (manager_id IS NULL).

??? tip "Hint"
    `manager_id` in table `staff` is self-referencing (Self-Join).
    Anchor: `WHERE manager_id IS NULL` (top level administrator).
    Recursive: Associate subordinates with `s.manager_id = tree.id`.

??? success "Answer"
    ```sql
    WITH RECURSIVE org_tree AS (
        -- Anchor: top-level manager
        SELECT
            id,
            name,
            department,
            role,
            manager_id,
            name AS chain,
            0 AS depth
        FROM staff
        WHERE manager_id IS NULL

        UNION ALL

        -- Recursive: add subordinates
        SELECT
            s.id,
            s.name,
            s.department,
            s.role,
            s.manager_id,
            ot.chain || ' > ' || s.name,
            ot.depth + 1
        FROM staff AS s
        INNER JOIN org_tree AS ot ON s.manager_id = ot.id
    )
    SELECT
        id,
        name,
        department,
        role,
        depth,
        chain
    FROM org_tree
    ORDER BY chain;
    ```

    **Result example (partial):**

    | id | name | department | role | depth | chain |
    | ----------: | ---------- | ---------- | ---------- | ----------: | ---------- |
    | 1 | 한민재 | 경영 | admin | 0 | 한민재 |
    | 30 | 고영숙 | 물류 | staff | 1 | 한민재 > 고영숙 |
    | 45 | 김영자 | 물류 | staff | 1 | 한민재 > 김영자 |
    | 47 | 김영환 | 물류 | staff | 1 | 한민재 > 김영환 |
    | 3 | 박경수 | 경영 | admin | 1 | 한민재 > 박경수 |
    | 6 | 고준서 | 영업 | manager | 2 | 한민재 > 박경수 > 고준서 |
    | 12 | 김지혜 | 영업 | staff | 3 | 한민재 > 박경수 > 고준서 > 김지혜 |
    | 5 | 권영희 | 마케팅 | manager | 2 | 한민재 > 박경수 > 권영희 |
    | ... | ... | ... | ... | ... | ... |

---

### Problem 8

**Find the total number of subordinates under each manager with recursive CTE.**

Calculate the overall team size, including direct loads as well as indirect loads (loads of direct reports).

??? tip "Hint"
    After expanding all parent-child relationships with a recursive CTE, record each parent manager's `id` as the root.
    You can find `COUNT(*) - 1` (excluding itself) for each root.

??? success "Answer"
    ```sql
    WITH RECURSIVE subordinates AS (
        -- Anchor: start each employee as their own root
        SELECT
            id AS root_id,
            id AS member_id
        FROM staff
        WHERE is_active = 1

        UNION ALL

        -- Recursive: add subordinates
        SELECT
            sub.root_id,
            s.id
        FROM staff AS s
        INNER JOIN subordinates AS sub ON s.manager_id = sub.member_id
        WHERE s.is_active = 1
    )
    SELECT
        s.id,
        s.name,
        s.department,
        s.role,
        COUNT(*) - 1 AS total_subordinates
    FROM subordinates AS sub
    INNER JOIN staff AS s ON sub.root_id = s.id
    GROUP BY s.id, s.name, s.department, s.role
    HAVING COUNT(*) > 1
    ORDER BY total_subordinates DESC;
    ```

    **Result example:**

    | id | name | department | role | total_subordinates |
    | ----------: | ---------- | ---------- | ---------- | ----------: |
    | 1 | 한민재 | 경영 | admin | 33 |
    | 3 | 박경수 | 경영 | admin | 18 |
    | 5 | 권영희 | 마케팅 | manager | 9 |
    | 4 | 이준혁 | 영업 | manager | 4 |
    | 2 | 장주원 | 경영 | admin | 3 |
    | 8 | 황예준 | 경영 | manager | 2 |
    | 7 | 김영일 | 개발 | manager | 1 |
    | ... | ... | ... | ... | ... |

---

### Problem 9

**Build customer RFM (Recency, Frequency, Monetary) segments with multiple CTEs.**

We chain three CTEs: (1) RFM raw metrics, (2) NTILE scores, and (3) segment labeling.

??? tip "Hint"
    CTE 1(`rfm_raw`): `MAX(ordered_at)`, `COUNT(*)`, `SUM(total_amount)`.
    CTE 2(`rfm_scored`): Apply `NTILE(4)`.
    CTE 3 or external query: Segments (VIP/Loyal/General/churn risk) are assigned with a combined score of R+F+M.

??? success "Answer"
    ```sql
    WITH rfm_raw AS (
        SELECT
            c.id            AS customer_id,
            c.name,
            c.grade,
            MAX(o.ordered_at) AS last_order_date,
            COUNT(*)          AS frequency,
            ROUND(SUM(o.total_amount), 0) AS monetary
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    ),
    rfm_scored AS (
        SELECT
            *,
            NTILE(4) OVER (ORDER BY last_order_date ASC) AS r_score,
            NTILE(4) OVER (ORDER BY frequency ASC)       AS f_score,
            NTILE(4) OVER (ORDER BY monetary ASC)         AS m_score
        FROM rfm_raw
    ),
    rfm_segment AS (
        SELECT
            *,
            r_score + f_score + m_score AS total_score,
            CASE
                WHEN r_score + f_score + m_score >= 10 THEN 'Champions'
                WHEN r_score + f_score + m_score >= 8  THEN 'Loyal'
                WHEN r_score + f_score + m_score >= 5  THEN 'Potential'
                ELSE 'At Risk'
            END AS segment
        FROM rfm_scored
    )
    SELECT
        segment,
        COUNT(*)                     AS customer_count,
        ROUND(AVG(frequency), 1)     AS avg_frequency,
        ROUND(AVG(monetary), 0)      AS avg_monetary,
        ROUND(AVG(r_score + f_score + m_score), 1) AS avg_score
    FROM rfm_segment
    GROUP BY segment
    ORDER BY avg_score DESC;
    ```

    **Result example:**

    | segment | customer_count | avg_frequency | avg_monetary | avg_score |
    |---|---|---|---|---|
    | Champions | 85 | 18.2 | 5200000 | 10.8 |
    | Loyal | 142 | 12.5 | 3100000 | 8.7 |
    | Potential | 320 | 6.3 | 1200000 | 6.2 |
    | At Risk | 253 | 2.1 | 350000 | 3.4 |

---

### Problem 10

**After developing the category tree with recursive CTE, count the number of products and sales for each top category.**

??? tip "Hint"
    Track the top root of each category with a recursive CTE.
    log `id AS root_id, name AS root_name` in anchor,
    In recursion, it propagates `root_id` and `root_name` from the parent as is.
    Aggregate by root by joining `products`, `order_items`, and `orders` to the results.

??? success "Answer"
    ```sql
    WITH RECURSIVE cat_root AS (
        -- Anchor: top-level categories (self as root)
        SELECT
            id,
            id   AS root_id,
            name AS root_name
        FROM categories
        WHERE parent_id IS NULL

        UNION ALL

        -- Recursive: child categories inherit parent's root
        SELECT
            c.id,
            cr.root_id,
            cr.root_name
        FROM categories AS c
        INNER JOIN cat_root AS cr ON c.parent_id = cr.id
    )
    SELECT
        cr.root_name                  AS top_category,
        COUNT(DISTINCT p.id)          AS product_count,
        ROUND(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
        SUM(oi.quantity)              AS units_sold
    FROM cat_root AS cr
    INNER JOIN products   AS p  ON p.category_id = cr.id
    INNER JOIN order_items AS oi ON oi.product_id = p.id
    INNER JOIN orders     AS o  ON oi.order_id   = o.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY cr.root_id, cr.root_name
    ORDER BY total_revenue DESC;
    ```

    **Result example:**

    | top_category | product_count | total_revenue | units_sold |
    | ---------- | ----------: | ----------: | ----------: |
    | 노트북 | 237 | 16183602000.0 | 7592 |
    | 그래픽카드 | 99 | 10026900600.0 | 6451 |
    | 모니터 | 169 | 6381505300.0 | 7250 |
    | 메인보드 | 149 | 4331432400.0 | 10848 |
    | CPU | 29 | 2972276700.0 | 6313 |
    | 저장장치 | 160 | 2816457800.0 | 13058 |
    | 스피커/헤드셋 | 98 | 2473846600.0 | 10839 |
    | 키보드 | 165 | 2218745800.0 | 16740 |
    | ... | ... | ... | ... |

---

## Practical (11~15)

We cover advanced patterns such as chaining more than 3 CTEs, leveraging recursion depth, and creating date sequences.

---

### Problem 11

**Create month sequences with recursive CTEs and create monthly reports, including months with no sales.**

Create a 12-month sequence from 2024-01 to 2024-12 with a recursive CTE and LEFT JOIN it with actual sales data.

??? tip "Hint"
    With a recursive CTE, we create a sequence starting from '2024-01' and incrementing by +1 for each month.
    Calculate the next month as `DATE(year_month || '-01', '+1 month')`, formatted as `SUBSTR(..., 1, 7)`.
    Exit condition: `year_month < '2024-12'`.

??? success "Answer"
    ```sql
    WITH RECURSIVE months AS (
        SELECT '2024-01' AS year_month
        UNION ALL
        SELECT SUBSTR(DATE(year_month || '-01', '+1 month'), 1, 7)
        FROM months
        WHERE year_month < '2024-12'
    ),
    actual_revenue AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            COUNT(*)                 AS order_count,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        m.year_month,
        COALESCE(a.order_count, 0) AS order_count,
        COALESCE(a.revenue, 0)     AS revenue
    FROM months AS m
    LEFT JOIN actual_revenue AS a ON m.year_month = a.year_month
    ORDER BY m.year_month;
    ```

    **Result (line 12):**

    | year_month | order_count | revenue |
    | ---------- | ----------: | ----------: |
    | 2024-01 | 3795 | 3737010508.0 |
    | 2024-02 | 4469 | 4630208028.0 |
    | 2024-03 | 4817 | 4811012761.0 |
    | 2024-04 | 4858 | 4852046384.0 |
    | 2024-05 | 4917 | 4796192371.0 |
    | 2024-06 | 3670 | 3787186898.0 |
    | 2024-07 | 4378 | 4370145415.0 |
    | 2024-08 | 4753 | 4778870727.0 |
    | ... | ... | ... |

    > All months are displayed without exception. Months with no data are filled with 0.

---

### Problem 12

**Calculate product performance ratings with a 3-step CTE chain.**

CTE 1: Sales by product. CTE 2: NTILE(5) rating based on sales. CTE 3: Statistics by grade.
The final output includes the number of products by grade, sales range, and representative products (#1 in sales).

??? tip "Hint"
    CTE 3 to `FIRST_VALUE(product_name) OVER (PARTITION BY tier ORDER BY revenue DESC)`
    Extract representative products from each grade.
    Use `DISTINCT` to summarize each grade into one row.

??? success "Answer"
    ```sql
    WITH product_sales AS (
        SELECT
            p.id       AS product_id,
            p.name     AS product_name,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue,
            SUM(oi.quantity) AS units_sold
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name
    ),
    tiered AS (
        SELECT
            *,
            NTILE(5) OVER (ORDER BY revenue DESC) AS tier
        FROM product_sales
    ),
    tier_summary AS (
        SELECT DISTINCT
            tier,
            COUNT(*) OVER (PARTITION BY tier) AS product_count,
            MIN(revenue) OVER (PARTITION BY tier) AS min_revenue,
            MAX(revenue) OVER (PARTITION BY tier) AS max_revenue,
            ROUND(AVG(revenue) OVER (PARTITION BY tier), 0) AS avg_revenue,
            FIRST_VALUE(product_name) OVER (
                PARTITION BY tier ORDER BY revenue DESC
            ) AS top_product
        FROM tiered
    )
    SELECT
        tier,
        CASE tier
            WHEN 1 THEN 'S (Top)'
            WHEN 2 THEN 'A (Excellent)'
            WHEN 3 THEN 'B (Average)'
            WHEN 4 THEN 'C (Below Average)'
            WHEN 5 THEN 'D (Poor)'
        END AS tier_label,
        product_count,
        min_revenue,
        max_revenue,
        avg_revenue,
        top_product
    FROM tier_summary
    ORDER BY tier;
    ```

    **Result example:**

    | tier | tier_label | product_count | min_revenue | max_revenue | avg_revenue | top_product |
    |---|---|---|---|---|---|---|
    | 1 | S (Top) | 20 | 15000000 | 45200000 | 25000000 | MacBook Pro 16 M3 |
    | 2 | A (Excellent) | 20 | 8000000 | 14800000 | 11000000 | ASUS ROG Strix ... |
    | 3 | B (Average) | 20 | 3500000 | 7900000 | 5500000 | Logitech MX ... |
    | 4 | C (Below Average) | 20 | 1200000 | 3400000 | 2100000 | ... |
    | 5 | D (Poor) | 20 | 50000 | 1100000 | 580000 | ... |

---

### Problem 13

**Create a sequence of consecutive days with a recursive CTE and find days (gaps) with no orders.**

Generate consecutive dates from 2024-01-01 to 2024-12-31 and extract days with 0 orders.

??? tip "Hint"
    In a recursive CTE, `DATE(date_val, '+1 day')` is incremented by one day.
    Connect to the actual order date with `LEFT JOIN` and filter out days where the order is NULL.
    Alternatively, you can use the `calendar` table if you have one.

??? success "Answer"
    ```sql
    WITH RECURSIVE date_seq AS (
        SELECT '2024-01-01' AS date_val
        UNION ALL
        SELECT DATE(date_val, '+1 day')
        FROM date_seq
        WHERE date_val < '2024-12-31'
    ),
    daily_orders AS (
        SELECT
            DATE(ordered_at) AS order_date,
            COUNT(*)         AS order_count
        FROM orders
        WHERE ordered_at >= '2024-01-01'
          AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY DATE(ordered_at)
    )
    SELECT
        d.date_val AS gap_date,
        CASE CAST(STRFTIME('%w', d.date_val) AS INTEGER)
            WHEN 0 THEN 'Sun'
            WHEN 1 THEN 'Mon'
            WHEN 2 THEN 'Tue'
            WHEN 3 THEN 'Wed'
            WHEN 4 THEN 'Thu'
            WHEN 5 THEN 'Fri'
            WHEN 6 THEN 'Sat'
        END AS day_name
    FROM date_seq AS d
    LEFT JOIN daily_orders AS o ON d.date_val = o.order_date
    WHERE o.order_count IS NULL
    ORDER BY d.date_val;
    ```

    **Result example:**

    | gap_date | day_name |
    |---|---|
    | 2024-01-01 | Mon |
    | 2024-02-10 | Sat |
    | 2024-05-01 | Wed |
    | ... | ... |

    > Days without orders usually occur on public holidays or weekends.

---

### Problem 14

**Perform “Cohort Retention” analysis with a 4-step CTE chain.**

CTE 1: First order month (cohort) for each customer. CTE 2: List of order months by customer. CTE 3: Cohort-relative month mapping. CTE 4: Retention rate by cohort.

??? tip "Hint"
    The relative month is `(CAST(SUBSTR(order_month,1,4) AS INTEGER)*12 + CAST(SUBSTR(order_month,6,2) AS INTEGER))
    - Calculated as (CAST(SUBSTR(cohort_month,1,4) AS INTEGER)*12 + CAST(SUBSTR(cohort_month,6,2) AS INTEGER))`.
    Retention rate = Active customers per month / Total customers in the cohort * 100.

??? success "Answer"
    ```sql
    WITH cohort AS (
        SELECT
            customer_id,
            SUBSTR(MIN(ordered_at), 1, 7) AS cohort_month
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    order_months AS (
        SELECT DISTINCT
            customer_id,
            SUBSTR(ordered_at, 1, 7) AS order_month
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    cohort_activity AS (
        SELECT
            co.cohort_month,
            (CAST(SUBSTR(om.order_month, 1, 4) AS INTEGER) * 12
             + CAST(SUBSTR(om.order_month, 6, 2) AS INTEGER))
          - (CAST(SUBSTR(co.cohort_month, 1, 4) AS INTEGER) * 12
             + CAST(SUBSTR(co.cohort_month, 6, 2) AS INTEGER)) AS months_since,
            COUNT(DISTINCT om.customer_id) AS active_customers
        FROM cohort AS co
        INNER JOIN order_months AS om ON co.customer_id = om.customer_id
        GROUP BY co.cohort_month, months_since
    ),
    cohort_size AS (
        SELECT
            cohort_month,
            COUNT(*) AS total_customers
        FROM cohort
        GROUP BY cohort_month
    )
    SELECT
        ca.cohort_month,
        cs.total_customers,
        ca.months_since,
        ca.active_customers,
        ROUND(100.0 * ca.active_customers / cs.total_customers, 1) AS retention_pct
    FROM cohort_activity AS ca
    INNER JOIN cohort_size AS cs ON ca.cohort_month = cs.cohort_month
    WHERE ca.cohort_month >= '2024-01'
      AND ca.months_since <= 6
    ORDER BY ca.cohort_month, ca.months_since;
    ```

    **Result example (partial):**

    | cohort_month | total_customers | months_since | active_customers | retention_pct |
    |---|---|---|---|---|
    | 2024-01 | 45 | 0 | 45 | 100.0 |
    | 2024-01 | 45 | 1 | 18 | 40.0 |
    | 2024-01 | 45 | 2 | 12 | 26.7 |
    | 2024-01 | 45 | 3 | 9 | 20.0 |
    | 2024-02 | 38 | 0 | 38 | 100.0 |
    | 2024-02 | 38 | 1 | 15 | 39.5 |
    | ... | ... | ... | ... | ... |

---

### Problem 15

**Obtain statistics by category depth with recursive CTE and visualize them in tree form.**

The tree structure is expressed as text, including the indentation (space according to depth) of each category,
The number of direct products in each category and the total number of sub-products are displayed together.

??? tip "Hint"
    Unfolds the category tree with a recursive CTE, creating `sort_path` for sorting (e.g. `'001/003/007'`).
    Indent is `REPLACE(SUBSTR('                ', 1, level * 4), ' ', ' ')` or
    Expressed as `CASE level WHEN 0 THEN '' WHEN 1 THEN '  ' WHEN 2 THEN '    ' END`, etc.

??? success "Answer"
    ```sql
    WITH RECURSIVE cat_tree AS (
        SELECT
            id,
            parent_id,
            name,
            depth,
            sort_order,
            PRINTF('%03d', sort_order) AS sort_path,
            0 AS level
        FROM categories
        WHERE parent_id IS NULL

        UNION ALL

        SELECT
            c.id,
            c.parent_id,
            c.name,
            c.depth,
            c.sort_order,
            ct.sort_path || '/' || PRINTF('%03d', c.sort_order),
            ct.level + 1
        FROM categories AS c
        INNER JOIN cat_tree AS ct ON c.parent_id = ct.id
    ),
    direct_products AS (
        SELECT category_id, COUNT(*) AS direct_count
        FROM products
        WHERE is_active = 1
        GROUP BY category_id
    )
    SELECT
        ct.id,
        CASE ct.level
            WHEN 0 THEN ct.name
            WHEN 1 THEN '  ' || ct.name
            WHEN 2 THEN '    ' || ct.name
        END AS tree_display,
        ct.level,
        COALESCE(dp.direct_count, 0) AS direct_products
    FROM cat_tree AS ct
    LEFT JOIN direct_products AS dp ON ct.id = dp.category_id
    ORDER BY ct.sort_path;
    ```

    **Result example (partial):**

    | id | tree_display | level | direct_products |
    |---|---|---|---|
    | 1 | 데스크탑/워크스테이션 | 0 | 0 |
    | 3 |   데스크탑 PC | 1 | 0 |
    | 5 |     게이밍 데스크탑 | 2 | 15 |
    | 6 |     사무용 데스크탑 | 2 | 12 |
    | 2 | 노트북/태블릿 | 0 | 0 |
    | 4 |   노트북 | 1 | 0 |
    | 7 |     게이밍 노트북 | 2 | 18 |
    | 8 |     비즈니스 노트북 | 2 | 14 |

    > Top/middle categories do not have products directly, only leaf (depth=2) categories have products.
