# Inventory Management

!!! info "Tables"

    `products` — Products (name, price, stock, brand)  

    `categories` — Categories (parent-child hierarchy)  

    `suppliers` — Suppliers (company, contact)  

    `inventory_transactions` — Inventory (type, quantity)  

    `order_items` — Order items (qty, unit price)  

    `orders` — Orders (status, amount, date)  



!!! abstract "Concepts"

    `Conditional Aggregation`, `Window Functions`, `ABC Analysis`, `Pareto`, `CTE`



### 1. Current Inventory Status and Low-Stock Products


The logistics team needs a list of low-stock products.
Find active products with stock <= 10, showing name, category, stock, price, and supplier.
Mark products with 0 stock as "out of stock".


**Hint 1:** - Check current stock with `products.stock_qty`
- JOIN `products` -> `categories`, `products` -> `suppliers`
- Use `CASE` for stock status labels
- Filter `products.is_active = 1`



??? success "Answer"
    ```sql
    SELECT
        p.name          AS product_name,
        cat.name        AS category,
        s.company_name  AS supplier,
        p.stock_qty,
        CASE
            WHEN p.stock_qty = 0 THEN '품절'
            WHEN p.stock_qty <= 5 THEN '긴급'
            ELSE '부족'
        END AS stock_status,
        p.price
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN suppliers  AS s   ON p.supplier_id = s.id
    WHERE p.is_active = 1
      AND p.stock_qty <= 10
    ORDER BY p.stock_qty ASC, p.price DESC;
    ```


    **Result** (3 rows)

    | product_name | category | supplier | stock_qty | stock_status | price |
    |---|---|---|---|---|---|
    | Arctic Freezer 36 A-RGB White | Air Cooling | Arctic Corp. | 0 | 품절 | 23,000.00 |
    | Samsung SPA-KFG0BUB | Membrane | Samsung Official Distribution | 4 | 긴급 | 30,700.00 |
    | Logitech G502 HERO Silver | Wired | Logitech Corp. | 8 | 부족 | 71,100.00 |


---


### 2. Inventory Inbound/Outbound Flow Analysis


Compare inbound and outbound quantities per product for 2025.
Show only products with negative net change.


**Hint 1:** - `inventory_transactions.type`: 'inbound' or 'outbound'
- Conditional aggregation: `SUM(CASE WHEN type='inbound' THEN quantity ELSE 0 END)`
- JOIN with `products` for current stock



??? success "Answer"
    ```sql
    SELECT
        p.name          AS product_name,
        p.stock_qty AS current_stock,
        SUM(CASE WHEN it.type = 'inbound'  THEN it.quantity ELSE 0 END) AS total_in,
        SUM(CASE WHEN it.type = 'outbound' THEN it.quantity ELSE 0 END) AS total_out,
        SUM(CASE WHEN it.type = 'inbound'  THEN it.quantity ELSE 0 END)
      - SUM(CASE WHEN it.type = 'outbound' THEN it.quantity ELSE 0 END) AS net_change
    FROM inventory_transactions AS it
    INNER JOIN products AS p ON it.product_id = p.id
    WHERE it.created_at LIKE '2025%'
    GROUP BY p.id, p.name, p.stock_qty
    HAVING net_change < 0
    ORDER BY net_change ASC;
    ```


---


### 3. Product ABC Analysis (Pareto 80/20)


Classify products into A/B/C grades by revenue contribution.
A-grade: products making up 80% of total revenue.
B-grade: next 15%. C-grade: remaining.


**Hint 1:** - Calculate revenue per product, sort descending
- Use `SUM() OVER (ORDER BY ...)` for cumulative percentage
- Classify A/B/C by cumulative percentage of total revenue



??? success "Answer"
    ```sql
    WITH product_revenue AS (
        SELECT
            p.id,
            p.name,
            cat.name AS category,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name, cat.name
    ),
    ranked AS (
        SELECT *,
            SUM(revenue) OVER () AS total_revenue,
            SUM(revenue) OVER (ORDER BY revenue DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumulative_revenue
        FROM product_revenue
    )
    SELECT
        name AS product_name,
        category,
        revenue,
        ROUND(100.0 * revenue / total_revenue, 2) AS pct_of_total,
        ROUND(100.0 * cumulative_revenue / total_revenue, 2) AS cumulative_pct,
        CASE
            WHEN 100.0 * cumulative_revenue / total_revenue <= 80 THEN 'A'
            WHEN 100.0 * cumulative_revenue / total_revenue <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM ranked
    ORDER BY revenue DESC
    LIMIT 30;
    ```


    **Result** (top 7 of 30 rows)

    | product_name | category | revenue | pct_of_total | cumulative_pct | abc_class |
    |---|---|---|---|---|---|
    | Razer Blade 18 Black | Gaming Laptop | 1,079,568,800.00 | 3.08 | 3.08 | A |
    | Razer Blade 16 Silver | Gaming Laptop | 859,072,800.00 | 2.45 | 5.52 | A |
    | ASUS Dual RTX 4060 Ti Black | NVIDIA | 858,610,800.00 | 2.45 | 7.97 | A |
    | Razer Blade 18 Black | Gaming Laptop | 839,487,500.00 | 2.39 | 10.36 | A |
    | Razer Blade 18 White | Gaming Laptop | 665,604,800.00 | 1.90 | 12.26 | A |
    | MSI GeForce RTX 4070 Ti Super GAMING X | NVIDIA | 647,024,000.00 | 1.84 | 14.11 | A |
    | MSI Radeon RX 7900 XTX GAMING X White | AMD | 585,793,600.00 | 1.67 | 15.77 | A |


---


### 4. Supplier Performance Evaluation


Calculate each supplier's product count, total revenue, return rate, and average rating.
Identify suppliers with high return rates.


**Hint 1:** - JOIN chain: `suppliers` -> `products` -> `order_items` -> `orders`
- Return rate = return count / total units sold
- LEFT JOIN `reviews` for ratings



??? success "Answer"
    ```sql
    WITH supplier_sales AS (
        SELECT
            s.id AS supplier_id,
            s.company_name AS supplier_name,
            COUNT(DISTINCT p.id) AS product_count,
            SUM(oi.quantity)     AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
        FROM suppliers AS s
        INNER JOIN products   AS p  ON s.id = p.supplier_id
        INNER JOIN order_items AS oi ON p.id = oi.product_id
        INNER JOIN orders     AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY s.id, s.company_name
    ),
    supplier_returns AS (
        SELECT
            s.id AS supplier_id,
            COUNT(ret.id) AS return_count
        FROM suppliers AS s
        INNER JOIN products   AS p   ON s.id = p.supplier_id
        INNER JOIN order_items AS oi ON p.id = oi.product_id
        INNER JOIN orders     AS o2  ON oi.order_id = o2.id
        INNER JOIN returns    AS ret ON ret.order_id = o2.id
        GROUP BY s.id
    ),
    supplier_reviews AS (
        SELECT
            s.id AS supplier_id,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(r.id) AS review_count
        FROM suppliers AS s
        INNER JOIN products AS p ON s.id = p.supplier_id
        INNER JOIN reviews  AS r ON p.id = r.product_id
        GROUP BY s.id
    )
    SELECT
        ss.supplier_name,
        ss.product_count,
        ss.units_sold,
        ss.total_revenue,
        COALESCE(sr.return_count, 0) AS return_count,
        ROUND(100.0 * COALESCE(sr.return_count, 0) / ss.units_sold, 2) AS return_rate_pct,
        COALESCE(srev.avg_rating, 0) AS avg_rating,
        srev.review_count
    FROM supplier_sales AS ss
    LEFT JOIN supplier_returns AS sr   ON ss.supplier_id = sr.supplier_id
    LEFT JOIN supplier_reviews AS srev ON ss.supplier_id = srev.supplier_id
    ORDER BY return_rate_pct DESC;
    ```


    **Result** (top 7 of 45 rows)

    | supplier_name | product_count | units_sold | total_revenue | return_count | return_rate_pct | avg_rating | review_count |
    |---|---|---|---|---|---|---|---|
    | Brother Corp. | 1 | 21 | 4,254,600.00 | 2 | 9.52 | 4.00 | 1 |
    | Hansung Computer | 4 | 295 | 311,361,100.00 | 19 | 6.44 | 3.75 | 32 |
    | Dell Corp. | 3 | 566 | 528,065,100.00 | 27 | 4.77 | 4.21 | 63 |
    | Lenovo Corp. | 5 | 577 | 996,843,200.00 | 25 | 4.33 | 3.58 | 59 |
    | Razer Corp. | 9 | 2958 | 4,004,408,800.00 | 120 | 4.06 | 3.89 | 272 |
    | Canon Corp. | 5 | 892 | 292,499,200.00 | 36 | 4.04 | 3.94 | 97 |
    | Jooyon Tech | 4 | 255 | 357,712,900.00 | 10 | 3.92 | 4.00 | 25 |


---


### 5. Monthly Inventory Turnover Trend


Show monthly inventory turnover ratio for 2024.
Turnover ratio = monthly outbound quantity / end-of-month cumulative stock.


**Hint 1:** - Monthly outbound: filter `type='outbound'` from `inventory_transactions`
- Use window functions for cumulative stock calculation



??? success "Answer"
    ```sql
    WITH monthly_flow AS (
        SELECT
            SUBSTR(created_at, 1, 7) AS year_month,
            SUM(CASE WHEN type = 'outbound' THEN quantity ELSE 0 END) AS total_out,
            SUM(CASE WHEN type = 'inbound'  THEN quantity ELSE 0 END) AS total_in
        FROM inventory_transactions
        WHERE created_at LIKE '2024%'
        GROUP BY SUBSTR(created_at, 1, 7)
    ),
    with_cumulative AS (
        SELECT
            year_month,
            total_out,
            total_in,
            SUM(total_in - total_out) OVER (
                ORDER BY year_month
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumulative_net_stock
        FROM monthly_flow
    )
    SELECT
        year_month,
        total_in,
        total_out,
        cumulative_net_stock,
        CASE
            WHEN cumulative_net_stock > 0
            THEN ROUND(1.0 * total_out / cumulative_net_stock, 2)
            ELSE NULL
        END AS turnover_ratio
    FROM with_cumulative
    ORDER BY year_month;
    ```


    **Result** (top 7 of 12 rows)

    | year_month | total_in | total_out | cumulative_net_stock | turnover_ratio |
    |---|---|---|---|---|
    | 2024-01 | 1996 | -199 | 2195 | -0.09 |
    | 2024-02 | 935 | -163 | 3293 | -0.05 |
    | 2024-03 | 3500 | -248 | 7041 | -0.04 |
    | 2024-04 | 3513 | -122 | 10,676 | -0.01 |
    | 2024-05 | 3394 | -253 | 14,323 | -0.02 |
    | 2024-06 | 2671 | -171 | 17,165 | -0.01 |
    | 2024-07 | 2899 | -138 | 20,202 | -0.01 |


---


### 6. Bonus: Category-Level ABC Analysis with Low Stock Rate


Perform ABC analysis at the category level.
Show ABC grade, product count, and low-stock (stock_qty <= 10) product percentage per category.


**Hint 1:** - Calculate category revenue and low-stock rate in one CTE
- Classify ABC by cumulative revenue



??? success "Answer"
    ```sql
    WITH category_revenue AS (
        SELECT
            cat.id AS category_id,
            cat.name AS category,
            COUNT(DISTINCT p.id) AS product_count,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
            ROUND(100.0 * SUM(CASE WHEN p.stock_qty <= 10 THEN 1 ELSE 0 END)
                        / COUNT(DISTINCT p.id), 1) AS low_stock_pct
        FROM categories AS cat
        INNER JOIN products    AS p  ON cat.id = p.category_id
        INNER JOIN order_items AS oi ON p.id   = oi.product_id
        INNER JOIN orders      AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY cat.id, cat.name
    ),
    ranked AS (
        SELECT *,
            SUM(revenue) OVER () AS total_revenue,
            SUM(revenue) OVER (ORDER BY revenue DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumulative
        FROM category_revenue
    )
    SELECT
        category,
        product_count,
        revenue,
        ROUND(100.0 * cumulative / total_revenue, 1) AS cumulative_pct,
        CASE
            WHEN 100.0 * cumulative / total_revenue <= 80 THEN 'A'
            WHEN 100.0 * cumulative / total_revenue <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class,
        low_stock_pct
    FROM ranked
    ORDER BY revenue DESC;
    ```


    **Result** (top 7 of 40 rows)

    | category | product_count | revenue | cumulative_pct | abc_class | low_stock_pct |
    |---|---|---|---|---|---|
    | Gaming Laptop | 9 | 4,684,236,900.00 | 13.30 | A | 0.0 |
    | NVIDIA | 7 | 2,695,883,800.00 | 21.00 | A | 0.0 |
    | Gaming Monitor | 10 | 2,645,570,200.00 | 28.60 | A | 0.0 |
    | AMD | 8 | 2,419,754,300.00 | 35.50 | A | 0.0 |
    | General Laptop | 10 | 2,324,971,800.00 | 42.10 | A | 0.0 |
    | 2-in-1 | 9 | 1,852,395,500.00 | 47.40 | A | 0.0 |
    | Intel Socket | 13 | 1,506,501,500.00 | 51.70 | A | 0.0 |


---
