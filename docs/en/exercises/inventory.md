# Exercise: Inventory Management

Analyze inventory data to derive operational insights. Tackle five questions covering stock shortages, inventory flow, ABC analysis, supplier evaluation, and turnover rates — all from an SCM (Supply Chain Management) perspective.

---

## Question 1 — Current Stock Status and Low-Stock Products

**Business question:** The logistics team needs a list of products running low on stock. Find active products with 10 or fewer units in stock. Show the product name, category, current stock, price, and supplier. Mark zero-stock products as "Out of Stock."

**Hints:**

- Use `products.stock_qty` for current inventory
- JOIN `products` → `categories` and `products` → `suppliers`
- Use `CASE` for status labels
- Filter `products.is_active = 1`

??? success "Answer"
    ```sql
    SELECT
        p.name          AS product_name,
        cat.name        AS category,
        s.company_name  AS supplier,
        p.stock_qty,
        CASE
            WHEN p.stock_qty = 0 THEN 'Out of Stock'
            WHEN p.stock_qty <= 5 THEN 'Critical'
            ELSE 'Low'
        END AS stock_status,
        p.price
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN suppliers  AS s   ON p.supplier_id = s.id
    WHERE p.is_active = 1
      AND p.stock_qty <= 10
    ORDER BY p.stock_qty ASC, p.price DESC;
    ```

    **Expected insight:** High-value items (laptops, monitors) appearing on this list represent significant potential revenue loss. Out-of-stock active products need urgent reordering.

---

## Question 2 — Inventory In/Out Flow Analysis

**Business question:** Compare inbound and outbound quantities per product over the past year (2025). Show total inbound, total outbound, net change (in minus out), and current stock. Only display products with a negative net change.

**Hints:**

- `inventory_transactions` has a `type` column: 'inbound' (inbound), 'outbound' (outbound)
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

    **Expected insight:** Products with outbound exceeding inbound have declining stock and need reorder planning.

---

## Question 3 — Product ABC Analysis (Pareto 80/20)

**Business question:** Management wants to classify products into A/B/C tiers by revenue contribution. A-tier covers the top 80% of revenue, B-tier the next 15%, and C-tier the rest.

**Hints:**

- Calculate revenue per product, sort descending
- Use `SUM() OVER (ORDER BY ...)` for cumulative percentage
- Classify as A/B/C based on cumulative share

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

    **Expected insight:** A-tier products represent roughly 20% of the catalog but 80% of revenue. These must be prioritized for stock management.

---

## Question 4 — Supplier Performance Evaluation

**Business question:** The procurement team wants to evaluate suppliers. Calculate each supplier's product count, total revenue, return rate, and average customer rating. Identify suppliers with high return rates.

**Hints:**

- JOIN chain: `suppliers` → `products` → `order_items` → `orders`
- Return rate = returns / total units sold
- LEFT JOIN `reviews` for ratings
- GROUP BY supplier

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

    **Expected insight:** Suppliers with return rates above 5% need quality review meetings. High returns but decent ratings may indicate shipping issues rather than product quality.

---

## Question 5 — Monthly Inventory Turnover Trend

**Business question:** Finance wants to see the monthly inventory turnover ratio for 2024. Turnover = total outbound quantity / estimated average inventory per month.

**Hints:**

- Monthly outbound: filter `inventory_transactions` where `type='outbound'`
- Estimate inventory using cumulative net stock
- Window functions for running totals

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

    **Expected insight:** Nov–Dec see the highest turnover due to holiday sales spikes. Jan–Feb show lower turnover as inventory accumulates. Annual average turnover below 1 may signal overstocking risk.

---

## Bonus Challenge

Perform the ABC analysis from Question 3 at the **category level**. Show each category's ABC tier alongside its product count and the percentage of products with low stock (stock_qty ≤ 10). If A-tier categories have a high low-stock ratio, immediate reordering is critical.

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
