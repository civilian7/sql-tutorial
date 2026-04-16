# CTE Applications

!!! info "Tables"

    `categories` — Categories (parent-child hierarchy)  

    `staff` — Staff (dept, role, manager)  

    `orders` — Orders (status, amount, date)  

    `customers` — Customers (grade, points, channel)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `calendar` — Calendar (weekday, holiday)  



!!! abstract "Concepts"

    `WITH`, `WITH RECURSIVE`, `Multiple CTE Chaining`, `CTE + Aggregate`, `CTE + JOIN`, `CTE + Window Function`



### 1. Monthly Sales vs Average


Find monthly sales in 2024 in CTE, and view only months with sales above the overall average.


**Hint 1:** After collecting monthly sales in CTE, use `WHERE revenue >= (SELECT AVG(revenue) FROM cte_name)` in external query.
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
            WHEN revenue >= (SELECT AVG(revenue) FROM monthly_revenue) THEN '평균 이상'
            ELSE '평균 미만'
        END AS status
    FROM monthly_revenue
    WHERE revenue >= (SELECT AVG(revenue) FROM monthly_revenue)
    ORDER BY revenue DESC;
    ```


    **Result** (4 rows)

    | year_month | revenue | order_count | avg_revenue | status |
    |---|---|---|---|---|
    | 2024-11 | 543,313,372.00 | 547 | 426,203,627.00 | 평균 이상 |
    | 2024-09 | 536,079,841.00 | 523 | 426,203,627.00 | 평균 이상 |
    | 2024-03 | 519,844,502.00 | 555 | 426,203,627.00 | 평균 이상 |
    | 2024-04 | 451,877,581.00 | 466 | 426,203,627.00 | 평균 이상 |


---


### 2. Find the total purchase amount for each customer in CTE, then extract the top 5 customers by grade.


Combines CTE and `ROW_NUMBER` window functions.


**Hint 1:** In the first CTE, aggregate the total purchase amount by customer,
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


    **Result** (top 7 of 20 rows)

    | grade | rank_in_grade | name | order_count | total_spent |
    |---|---|---|---|---|
    | VIP | 1 | Allen Snyder | 303 | 403,448,758.00 |
    | VIP | 2 | Jason Rivera | 342 | 366,385,931.00 |
    | VIP | 3 | Brenda Garcia | 249 | 253,180,338.00 |
    | VIP | 4 | Courtney Huff | 223 | 244,604,910.00 |
    | VIP | 5 | Ronald Arellano | 219 | 235,775,349.00 |
    | GOLD | 1 | Sandra Callahan | 171 | 204,611,811.00 |
    | GOLD | 2 | David York | 160 | 199,282,408.00 |


---


### 3. Use CTE to view sales and review summaries for each product at once.


Displays the sales amount, sales volume, number of reviews, and average rating of the top 10 selling products in 2024.


**Hint 1:** Create the sales CTE and review CTE separately, then combine them into `LEFT JOIN` in the external query.
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


    **Result** (top 7 of 10 rows)

    | product_name | category | units_sold | total_revenue | review_count | avg_rating |
    |---|---|---|---|---|---|
    | Razer Blade 18 Black | Gaming Laptop | 38 | 165,417,800.00 | 20 | 4.10 |
    | Razer Blade 16 Silver | Gaming Laptop | 37 | 137,007,300.00 | 19 | 3.95 |
    | MacBook Air 15 M3 Silver | MacBook | 23 | 126,065,300.00 | 4 | 3.75 |
    | ASUS Dual RTX 4060 Ti Black | NVIDIA | 40 | 106,992,000.00 | 16 | 3.75 |
    | ASUS Dual RTX 5070 Ti Silver | NVIDIA | 106 | 104,558,400.00 | 23 | 3.65 |
    | ASUS ROG Swift PG32UCDM Silver | Gaming Monitor | 48 | 90,734,400.00 | 24 | 3.67 |
    | ASUS ROG Strix Scar 16 | Gaming Laptop | 35 | 85,837,500.00 | 13 | 4.23 |


---


### 4. Practice chaining, where you aggregate results from one CTE and filter them from another CTE.


Find the number of new subscribers per month and look for “surge” months, which are month-on-month increases of 20% or more.


**Hint 1:** CTE 1: Counting the number of new subscribers per month. CTE 2: Calculate the change rate by taking the previous month's figures with `LAG`.
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


    **Result** (6 rows)

    | year_month | signup_count | prev_count | growth_pct |
    |---|---|---|---|
    | 2024-06 | 68 | 43 | 58.10 |
    | 2024-03 | 71 | 48 | 47.90 |
    | 2025-10 | 76 | 54 | 40.70 |
    | 2022-03 | 59 | 42 | 40.50 |
    | 2024-10 | 65 | 51 | 27.50 |
    | 2025-07 | 66 | 55 | 20.00 |


---


### 5. Find the proportion of sales by category in CTE and calculate the cumulative proportion (Pareto).


Calculate sales by category as of 2024 and display cumulative proportions in descending order.


**Hint 1:** After counting sales by category in CTE,
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


    **Result** (top 7 of 38 rows)

    | category | revenue | share_pct | cumulative_pct |
    |---|---|---|---|
    | Gaming Laptop | 636,925,700.00 | 12.30 | 12.30 |
    | AMD | 447,953,400.00 | 8.70 | 21.00 |
    | Gaming Monitor | 353,934,400.00 | 6.90 | 27.90 |
    | NVIDIA | 345,858,700.00 | 6.70 | 34.60 |
    | 2-in-1 | 340,884,400.00 | 6.60 | 41.20 |
    | General Laptop | 291,760,500.00 | 5.70 | 46.90 |
    | Professional Monitor | 254,590,200.00 | 4.90 | 51.80 |


---


### 6. Expand your category hierarchy into recursive CTEs.


Displays the entire path, from the top category (parent_id IS NULL) to subcategories.


**Hint 1:** Use `WITH RECURSIVE`. Anchor member: `WHERE parent_id IS NULL`.
Recursive member: JOIN CTE itself and `categories` with `c.parent_id = cte.id`.
The path connects to `parent_path || ' > ' || c.name`.



??? success "Answer"
    ```sql
    WITH RECURSIVE cat_tree AS (
        -- 앵커: 최상위 카테고리
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
    
        -- 재귀: 자식 카테고리
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


    **Result** (top 7 of 53 rows)

    | id | full_path | level | depth |
    |---|---|---|---|
    | 14 | CPU | 0 | 0 |
    | 16 | CPU > AMD | 1 | 1 |
    | 15 | CPU > Intel | 1 | 1 |
    | 31 | Case | 0 | 0 |
    | 32 | Cooling | 0 | 0 |
    | 33 | Cooling > Air Cooling | 1 | 1 |
    | 34 | Cooling > Liquid Cooling | 1 | 1 |


---


### 7. Expand your employee org chart as a recursive CTE.


Displays the path to every employee's immediate supervisor, starting with the manager (manager_id IS NULL).


**Hint 1:** `manager_id` in table `staff` is self-referencing (Self-Join).
Anchor: `WHERE manager_id IS NULL` (top level administrator).
Recursive: Associate subordinates with `s.manager_id = tree.id`.



??? success "Answer"
    ```sql
    WITH RECURSIVE org_tree AS (
        -- 앵커: 최고 관리자
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
    
        -- 재귀: 부하 직원
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


    **Result** (5 rows)

    | id | name | department | role | depth | chain |
    |---|---|---|---|---|---|
    | 1 | Michael Thomas | Management | admin | 0 | Michael Thomas |
    | 4 | Jaime Phelps | Sales | manager | 1 | Michael Thomas > Jaime Phelps |
    | 3 | Jonathan Smith | Management | admin | 1 | Michael Thomas > Jonathan Smith |
    | 5 | Nicole Hamilton | Marketing | manager | 2 | Michael Thomas > Jonathan Smith > Nic... |
    | 2 | Michael Mcguire | Management | admin | 1 | Michael Thomas > Michael Mcguire |


---


### 8. Find the total number of subordinates under each manager with recursive CTE.


Calculate the overall team size, including direct loads as well as indirect loads (loads of direct reports).


**Hint 1:** After expanding all parent-child relationships with a recursive CTE, record each parent manager's `id` as the root.
You can find `COUNT(*) - 1` (excluding itself) for each root.



??? success "Answer"
    ```sql
    WITH RECURSIVE subordinates AS (
        -- 앵커: 각 직원을 자기 자신의 루트로 시작
        SELECT
            id AS root_id,
            id AS member_id
        FROM staff
        WHERE is_active = 1
    
        UNION ALL
    
        -- 재귀: 부하 직원 추가
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


    **Result** (2 rows)

    | id | name | department | role | total_subordinates |
    |---|---|---|---|---|
    | 1 | Michael Thomas | Management | admin | 4 |
    | 3 | Jonathan Smith | Management | admin | 1 |


---


### 9. Build customer RFM (Recency, Frequency, Monetary) segments with multiple CTEs.


We chain three CTEs: (1) RFM raw metrics, (2) NTILE scores, and (3) segment labeling.


**Hint 1:** CTE 1(`rfm_raw`): `MAX(ordered_at)`, `COUNT(*)`, `SUM(total_amount)`.
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


    **Result** (4 rows)

    | segment | customer_count | avg_frequency | avg_monetary | avg_score |
    |---|---|---|---|---|
    | Champions | 784 | 32.90 | 34,334,528.00 | 11.00 |
    | Loyal | 569 | 8.50 | 8,532,740.00 | 8.40 |
    | Potential | 999 | 3.40 | 2,797,314.00 | 6.00 |
    | At Risk | 441 | 1.50 | 456,944.00 | 3.50 |


---


### 10. Revenue by Category Tree


After developing the category tree with recursive CTE, count the number of products and sales for each top category.


**Hint 1:** Track the top root of each category with a recursive CTE.
log `id AS root_id, name AS root_name` in anchor,
In recursion, it propagates `root_id` and `root_name` from the parent as is.
Aggregate by root by joining `products`, `order_items`, and `orders` to the results.



??? success "Answer"
    ```sql
    WITH RECURSIVE cat_root AS (
        -- 앵커: 최상위 카테고리 (자기 자신이 루트)
        SELECT
            id,
            id   AS root_id,
            name AS root_name
        FROM categories
        WHERE parent_id IS NULL
    
        UNION ALL
    
        -- 재귀: 자식 카테고리는 부모의 루트를 상속
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


    **Result** (top 7 of 18 rows)

    | top_category | product_count | total_revenue | units_sold |
    |---|---|---|---|
    | Laptop | 21 | 1,395,635,900.00 | 660 |
    | Monitor | 19 | 727,065,300.00 | 712 |
    | Graphics Card | 10 | 713,579,800.00 | 580 |
    | Motherboard | 16 | 398,988,900.00 | 920 |
    | Speakers/Headsets | 8 | 232,144,800.00 | 921 |
    | Storage | 13 | 205,861,200.00 | 833 |
    | Memory (RAM) | 14 | 200,423,600.00 | 1354 |


---


### 11. Create month sequences with recursive CTEs and create monthly reports, including months with no sales.


Create a 12-month sequence from 2024-01 to 2024-12 with a recursive CTE and LEFT JOIN it with actual sales data.


**Hint 1:** With a recursive CTE, we create a sequence starting from '2024-01' and incrementing by +1 for each month.
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


    **Result** (top 7 of 12 rows)

    | year_month | order_count | revenue |
    |---|---|---|
    | 2024-01 | 314 | 288,908,320.00 |
    | 2024-02 | 416 | 403,127,749.00 |
    | 2024-03 | 555 | 519,844,502.00 |
    | 2024-04 | 466 | 451,877,581.00 |
    | 2024-05 | 385 | 425,264,478.00 |
    | 2024-06 | 389 | 362,715,211.00 |
    | 2024-07 | 381 | 343,929,897.00 |


---


### 12. Calculate product performance ratings with a 3-step CTE chain.


CTE 1: Sales by product. CTE 2: NTILE(5) rating based on sales. CTE 3: Statistics by grade.
The final output includes the number of products by grade, sales range, and representative products (#1 in sales).


**Hint 1:** CTE 3 to `FIRST_VALUE(product_name) OVER (PARTITION BY tier ORDER BY revenue DESC)`
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
            WHEN 1 THEN 'S (최상위)'
            WHEN 2 THEN 'A (우수)'
            WHEN 3 THEN 'B (보통)'
            WHEN 4 THEN 'C (저조)'
            WHEN 5 THEN 'D (부진)'
        END AS tier_label,
        product_count,
        min_revenue,
        max_revenue,
        avg_revenue,
        top_product
    FROM tier_summary
    ORDER BY tier;
    ```


    **Result** (5 rows)

    | tier | tier_label | product_count | min_revenue | max_revenue | avg_revenue | top_product |
    |---|---|---|---|---|---|---|
    | 1 | S (최상위) | 44 | 39,196,400.00 | 165,417,800.00 | 66,665,918.00 | Razer Blade 18 Black |
    | 2 | A (우수) | 44 | 18,568,800.00 | 38,656,400.00 | 26,834,570.00 | SteelSeries Arctis Nova Pro Wireless ... |
    | 3 | B (보통) | 43 | 10,200,000.00 | 18,087,300.00 | 14,174,188.00 | JBL Flip 6 Black |
    | 4 | C (저조) | 43 | 5,400,000.00 | 10,027,500.00 | 7,904,735.00 | Razer DeathAdder V4 Pro White |
    | 5 | D (부진) | 43 | 159,000.00 | 5,188,800.00 | 2,268,381.00 | Arctic Liquid Freezer III 240 White |


---


### 13. Create a sequence of consecutive days with a recursive CTE and find days (gaps) with no orders.


Generate consecutive dates from 2024-01-01 to 2024-12-31 and extract days with 0 orders.


**Hint 1:** In a recursive CTE, `DATE(date_val, '+1 day')` is incremented by one day.
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
            WHEN 0 THEN '일'
            WHEN 1 THEN '월'
            WHEN 2 THEN '화'
            WHEN 3 THEN '수'
            WHEN 4 THEN '목'
            WHEN 5 THEN '금'
            WHEN 6 THEN '토'
        END AS day_name
    FROM date_seq AS d
    LEFT JOIN daily_orders AS o ON d.date_val = o.order_date
    WHERE o.order_count IS NULL
    ORDER BY d.date_val;
    ```


---


### 14. Perform “Cohort Retention” analysis with a 4-step CTE chain.


CTE 1: First order month (cohort) for each customer. CTE 2: List of order months by customer. CTE 3: Cohort-relative month mapping. CTE 4: Retention rate by cohort.


**Hint 1:** The relative month is `(CAST(SUBSTR(order_month,1,4) AS INTEGER)*12 + CAST(SUBSTR(order_month,6,2) AS INTEGER))
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


    **Result** (top 7 of 147 rows)

    | cohort_month | total_customers | months_since | active_customers | retention_pct |
    |---|---|---|---|---|
    | 2024-01 | 30 | 0 | 30 | 100.00 |
    | 2024-01 | 30 | 1 | 7 | 23.30 |
    | 2024-01 | 30 | 2 | 8 | 26.70 |
    | 2024-01 | 30 | 3 | 12 | 40.00 |
    | 2024-01 | 30 | 4 | 3 | 10.00 |
    | 2024-01 | 30 | 5 | 5 | 16.70 |
    | 2024-01 | 30 | 6 | 4 | 13.30 |


---


### 15. Obtain statistics by category depth with recursive CTE and visualize them in tree form.


The tree structure is expressed as text, including the indentation (space according to depth) of each category,
The number of direct products in each category and the total number of sub-products are displayed together.


**Hint 1:** Unfolds the category tree with a recursive CTE, creating `sort_path` for sorting (e.g. `'001/003/007'`).
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


    **Result** (top 7 of 53 rows)

    | id | tree_display | level | direct_products |
    |---|---|---|---|
    | 1 | Desktop PC | 0 | 0 |
    | 2 |   Pre-built | 1 | 3 |
    | 3 |   Custom Build | 1 | 9 |
    | 4 |   Barebone | 1 | 1 |
    | 5 | Laptop | 0 | 0 |
    | 6 |   General Laptop | 1 | 8 |
    | 7 |   Gaming Laptop | 1 | 6 |


---
