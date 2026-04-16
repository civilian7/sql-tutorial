# Index and execution plan

!!! info "Tables"
    `orders` — Orders (status, amount, date)  
    `order_items` — Order items (qty, unit price)  
    `products` — Products (name, price, stock, brand)  
    `payments` — Payments (method, amount, status)  

!!! abstract "Concepts"
    `EXPLAIN QUERY PLAN`, `CREATE INDEX`, Composite index, Covering index, SCAN vs SEARCH, Index unusable pattern

Practice what you learned in Lecture 23 index and action plan.
Use SQLite's `EXPLAIN QUERY PLAN` to analyze how queries are executed and create indexes to improve performance.

!!! warning "Practice Environment Note"
    Creating an index (`CREATE INDEX`) changes the database.
    Feel free to experiment with your practice DB copy.

---


### Problem 1. EXPLAIN QUERY PLAN Basics — SCAN vs SEARCH

Check the execution plans of the following two queries, and explain the difference between `SCAN TABLE` and `SEARCH TABLE`.

```sql
-- Query A
SELECT * FROM orders WHERE customer_id = 100;

-- Query B
SELECT * FROM orders WHERE notes LIKE '%urgent delivery%';
```


??? tip "Hint"
    - Execute by adding `EXPLAIN QUERY PLAN` in front of each query.
    - `SCAN TABLE` = Read entire rows sequentially (Full Table Scan)
    - `SEARCH TABLE ... USING INDEX` = Access only required rows by index

??? success "Answer"
    ```sql
    -- Query A: Search by customer_id (indexed)
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 100;
    -- Result: SEARCH TABLE orders USING INDEX idx_orders_customer_id (customer_id=?)

    -- Query B: LIKE search on notes (no index)
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE notes LIKE '%urgent delivery%';
    -- Result: SCAN TABLE orders
    ```

    | Category | Query A (customer_id) | Query B (notes LIKE) |
    |---|---|---|
    | Execution method | SEARCH (index) | SCAN (full scan) |
    | Reason | idx_orders_customer_id exists | LIKE '%...' pattern cannot use index |


---


### Problem 2. Check the existing index list

Check all indexes created in the current database by table.
Displays table name, index name, and creation SQL.


??? tip "Hint"
    - Search for row `type = 'index'` in `sqlite_master` table.
    - By grouping with `tbl_name`, you can identify indexes for each table.

??? success "Answer"
    ```sql
    SELECT
        tbl_name  AS table_name,
        name      AS index_name,
        sql       AS create_sql
    FROM sqlite_master
    WHERE type = 'index'
      AND sql IS NOT NULL  -- Exclude auto-generated indexes (PK, etc.)
    ORDER BY tbl_name, name;
    ```

    | table_name | index_name | create_sql |
    |---|---|---|
    | complaints | idx_complaints_category | CREATE INDEX idx_complaints_category ON complaints(category) |
    | complaints | idx_complaints_customer_id | CREATE INDEX idx_complaints_customer_id ON complaints(customer_id) |
    | customers | idx_customers_email | CREATE INDEX idx_customers_email ON customers(email) |
    | orders | idx_orders_customer_id | CREATE INDEX idx_orders_customer_id ON orders(customer_id) |
    | orders | idx_orders_customer_status | CREATE INDEX idx_orders_customer_status ON orders(customer_id, status) |
    | ... | ... | ... |


---


### Problem 3. Summary of index count for each table

Count how many indexes each table has.
Exclude tables with an index of 0.


??? tip "Hint"
    - GROUP BY `tbl_name` `type = 'index'` IN `sqlite_master`
    - Exclude auto-generated indexes with `sql IS NOT NULL`

??? success "Answer"
    ```sql
    SELECT
        tbl_name       AS table_name,
        COUNT(*)       AS index_count
    FROM sqlite_master
    WHERE type = 'index'
      AND sql IS NOT NULL
    GROUP BY tbl_name
    ORDER BY index_count DESC;
    ```

    | table_name | index_count |
    |---|---|
    | orders | 4 |
    | products | 5 |
    | complaints | 6 |
    | ... | ... |


---


### Problem 4. Create a simple index and check the effect

Create an index on the `method` column of the `payments` table, and compare the execution plan before and after creation.


??? tip "Hint"
    - First check the current status with `EXPLAIN QUERY PLAN SELECT ... WHERE method = 'card'`
    -Run `CREATE INDEX idx_payments_method ON payments(method)`
    - Compare by running the same EXPLAIN again

??? success "Answer"
    ```sql
    -- 1) Execution plan before index creation
    EXPLAIN QUERY PLAN
    SELECT * FROM payments WHERE method = 'card';
    -- Result: SCAN TABLE payments

    -- 2) Create index
    CREATE INDEX idx_payments_method ON payments(method);

    -- 3) Execution plan after index creation
    EXPLAIN QUERY PLAN
    SELECT * FROM payments WHERE method = 'card';
    -- Result: SEARCH TABLE payments USING INDEX idx_payments_method (method=?)
    ```

    | Step | Execution method |
    |---|---|
    | Before index creation | SCAN TABLE payments |
    | After index creation | SEARCH TABLE payments USING INDEX idx_payments_method |


---


### Problem 5. Analysis of execution plan of JOIN query

Analyze the execution plan of the following query that JOINs orders and order details.
Check which tables are scanned first and which indexes are used.

```sql
SELECT o.order_number, p.name, oi.quantity, oi.unit_price
FROM orders AS o
INNER JOIN order_items AS oi ON o.id = oi.order_id
INNER JOIN products AS p ON oi.product_id = p.id
WHERE o.ordered_at LIKE '2024-12%'
  AND o.status = 'delivered';
```


??? tip "Hint"
    - Execute by adding `EXPLAIN QUERY PLAN` in front of the query
    - SQLite shows access methods for each table in order
    - Distinguish between tables where `USING INDEX` is displayed and tables where it is not.

??? success "Answer"
    ```sql
    EXPLAIN QUERY PLAN
    SELECT o.order_number, p.name, oi.quantity, oi.unit_price
    FROM orders AS o
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    WHERE o.ordered_at LIKE '2024-12%'
      AND o.status = 'delivered';
    ```

    Example execution plan interpretation:

    | id | parent | detail |
    |---|---|---|
    | 2 | 0 | SEARCH TABLE orders AS o USING INDEX idx_orders_ordered_at (ordered_at>? AND ordered_at<?) |
    | 3 | 0 | SEARCH TABLE order_items AS oi USING INDEX idx_order_items_order_id (order_id=?) |
    | 4 | 0 | SEARCH TABLE products AS p USING INTEGER PRIMARY KEY (rowid=?) |

    - orders: Quickly filter 2024-December orders by `idx_orders_ordered_at` index
    - order_items: View detailed items of the order with `idx_order_items_order_id`
    - products: Direct access to product information with PK (rowid)


---


### Problem 6. Creating a Covering Index

Suppose you frequently look up only the order date and amount for a specific customer in your orders table.
Create a covering index to return results using only the index without accessing the table data.

```sql
SELECT ordered_at, total_amount
FROM orders
WHERE customer_id = 100;
```


??? tip "Hint"
    - Covering index: Index that includes both WHERE condition column + SELECT column
    - `CREATE INDEX idx_xxx ON orders(customer_id, ordered_at, total_amount)`
    - Success is achieved when the phrase “COVERING INDEX” appears in EXPLAIN.

??? success "Answer"
    ```sql
    -- Create covering index
    CREATE INDEX idx_orders_cust_date_amount
        ON orders(customer_id, ordered_at, total_amount);

    -- Check execution plan
    EXPLAIN QUERY PLAN
    SELECT ordered_at, total_amount
    FROM orders
    WHERE customer_id = 100;
    -- Result: SEARCH TABLE orders USING COVERING INDEX idx_orders_cust_date_amount (customer_id=?)
    ```

    | Index type | Behavior |
    |---|---|
    | Regular index | Index -> rowid -> table row access (2 steps) |
    | Covering index | Return directly from index (1 step, no table access) |


---


### Problem 7. Creating a partial index

Assume frequent category searches targeting only the active product (`is_active = 1`).
Create a partial index to exclude inactive products from the index.


??? tip "Hint"
    - Create partial index with `CREATE INDEX ... WHERE is_active = 1` syntax
    - Partial index includes only rows that meet the conditions in the index → ​​Reduces index size and improves performance
    - Use partial indexes only if the same conditions exist in the WHERE clause of the query

??? success "Answer"
    ```sql
    -- Create partial index
    CREATE INDEX idx_products_active_category
        ON products(category_id)
        WHERE is_active = 1;

    -- Query that uses the partial index
    EXPLAIN QUERY PLAN
    SELECT name, price
    FROM products
    WHERE category_id = 5
      AND is_active = 1;
    -- Result: SEARCH TABLE products USING INDEX idx_products_active_category (category_id=?)

    -- Without the condition, partial index is not used
    EXPLAIN QUERY PLAN
    SELECT name, price
    FROM products
    WHERE category_id = 5;
    -- Result: SEARCH TABLE products USING INDEX idx_products_category_id (category_id=?)
    ```

    | Query condition | Index used |
    |---|---|
    | `category_id = 5 AND is_active = 1` | idx_products_active_category (partial index) |
    | `category_id = 5` (no is_active condition) | idx_products_category_id (regular index) |


---


### Problem 8. Importance of composite index column order

Create composite indexes in the `(status, ordered_at)` order and `(ordered_at, status)` order on the `orders` table, respectively.
Check which index is used in the following two queries:

```sql
-- Query A: filter by status, range on ordered_at
SELECT * FROM orders WHERE status = 'delivered' AND ordered_at >= '2024-01-01';

-- Query B: range on ordered_at only
SELECT * FROM orders WHERE ordered_at >= '2024-01-01';
```


??? tip "Hint"
    - Most effective when the **first column** of a composite index is used as an equals condition in the WHERE clause
    - `(status, ordered_at)`: optimal for status = '...' AND ordered_at >= '...'
    - `(ordered_at, status)`: Index can be used only with ordered_at (since it is the first column)

??? success "Answer"
    ```sql
    -- Create indexes
    CREATE INDEX idx_orders_status_date ON orders(status, ordered_at);
    CREATE INDEX idx_orders_date_status ON orders(ordered_at, status);

    -- Query A: status equality + ordered_at range
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE status = 'delivered' AND ordered_at >= '2024-01-01';
    -- SQLite optimizer selects idx_orders_status_date (range scan on ordered_at after status equality)

    -- Query B: ordered_at range only
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE ordered_at >= '2024-01-01';
    -- Uses idx_orders_date_status or idx_orders_ordered_at (ordered_at is the first column)
    ```

    | Query | Optimal index | Reason |
    |---|---|---|
    | status = ? AND ordered_at >= ? | (status, ordered_at) | Equality condition column is leading |
    | ordered_at >= ? | (ordered_at, status) | Range search using only the first column |


---


### Problem 9. Index selectivity analysis

Compare the selectivity of the `status` and `customer_id` columns in the `orders` table.
Determine which column it is more effective to create an index on.


??? tip "Hint"
    - Selectivity = number of unique values ​​/ total number of rows
    - The higher the selectivity (closer to 1), the greater the index effect.
    - Calculated as `COUNT(DISTINCT ...)` / `COUNT(*)`

??? success "Answer"
    ```sql
    SELECT
        COUNT(*)                                           AS total_rows,
        COUNT(DISTINCT status)                             AS distinct_status,
        COUNT(DISTINCT customer_id)                        AS distinct_customer_id,
        ROUND(1.0 * COUNT(DISTINCT status) / COUNT(*), 6) AS selectivity_status,
        ROUND(1.0 * COUNT(DISTINCT customer_id) / COUNT(*), 6) AS selectivity_customer
    FROM orders;
    ```

    | total_rows | distinct_status | distinct_customer_id | selectivity_status | selectivity_customer |
    |---|---|---|---|---|
    | 50000 | 9 | 5000 | 0.000180 | 0.100000 |

    - The selectivity of `customer_id` (0.1) is much higher than `status` (0.00018)
    - customer_id index is more effective: can quickly find only one customer's order
    - The status index returns about 11% of the total (delivered, etc.) → the index effect may be low


---


### Problem 10. Determine when an index is not used

The following queries may not be used even if an index exists.
Check each EXPLAIN result and explain why the index is being ignored.

```sql
-- Query A: function applied
SELECT * FROM orders WHERE SUBSTR(ordered_at, 1, 4) = '2024';

-- Query B: OR condition
SELECT * FROM orders WHERE customer_id = 100 OR status = 'cancelled';

-- Query C: negation condition
SELECT * FROM orders WHERE customer_id != 100;
```


??? tip "Hint"
    - If you apply a function to a column, you cannot use the index (SARGable violation)
    - OR conditions can be inefficient because each condition must use a separate index.
    - Negative conditions (`!=`, `NOT IN`) return most rows, so a full scan is efficient.

??? success "Answer"
    ```sql
    -- Query A: function applied -> index not used
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE SUBSTR(ordered_at, 1, 4) = '2024';
    -- Result: SCAN TABLE orders
    -- Reason: SUBSTR() function applied to column prevents index usage

    -- SARGable alternative:
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01';
    -- Result: SEARCH TABLE orders USING INDEX idx_orders_ordered_at

    -- Query B: OR condition
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 100 OR status = 'cancelled';
    -- Result: SCAN TABLE orders (or MULTI-INDEX OR)
    -- Reason: Two conditions use separate indexes -> optimizer may choose full scan

    -- Query C: negation condition
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id != 100;
    -- Result: SCAN TABLE orders
    -- Reason: Returns nearly all rows -> full scan is more efficient
    ```

    | Pattern | Index used | Reason |
    |---|---|---|
    | `SUBSTR(col, ...) = ?` | X | Function applied to column (Non-SARGable) |
    | `col_a = ? OR col_b = ?` | Limited | OR across different columns |
    | `col != ?` | X | Returns most rows, scan is efficient |


---


### Problem 11. Improve performance by converting subqueries to JOINs

Convert the following correlated subquery to a JOIN and compare the execution plans of the two queries.

```sql
-- Original: correlated subquery (slow)
SELECT
    p.name,
    p.price,
    (SELECT COUNT(*) FROM order_items AS oi WHERE oi.product_id = p.id) AS order_count,
    (SELECT AVG(r.rating) FROM reviews AS r WHERE r.product_id = p.id) AS avg_rating
FROM products AS p
WHERE p.is_active = 1;
```


??? tip "Hint"
    - Correlated subqueries are executed for each row in the outer query.
    - If you use `LEFT JOIN`, the results pre-aggregated with `GROUP BY` will be executed only once.
    - Use `LEFT JOIN` to include products without reviews

??? success "Answer"
    ```sql
    -- Improved: convert to JOIN
    SELECT
        p.name,
        p.price,
        COALESCE(oi_stats.order_count, 0) AS order_count,
        oi_stats.avg_rating
    FROM products AS p
    LEFT JOIN (
        SELECT
            oi.product_id,
            COUNT(*)       AS order_count,
            AVG(r.rating)  AS avg_rating
        FROM order_items AS oi
        LEFT JOIN reviews AS r ON oi.product_id = r.product_id
        GROUP BY oi.product_id
    ) AS oi_stats ON p.id = oi_stats.product_id
    WHERE p.is_active = 1
    ORDER BY order_count DESC
    LIMIT 20;
    ```

    ```sql
    -- Execution plan comparison
    -- Original (subquery): SCAN TABLE products + CORRELATED SCALAR SUBQUERY x2 per row
    -- Improved (JOIN): SCAN TABLE products + SCAN TABLE order_items (once) + LEFT JOIN reviews (once)
    ```

    | Method | Subquery executions | Expected performance |
    |---|---|---|
    | Correlated subquery | Product count x 2 | Slow |
    | JOIN (pre-aggregated) | Once | Fast |


---


### Problem 12. Improving queries with SARGable conditions

Convert the following queries to SARGable (indexable) format.

```sql
-- Inefficient A: function used for year extraction
SELECT * FROM orders WHERE strftime('%Y', ordered_at) = '2024';

-- Inefficient B: calculation applied
SELECT * FROM products WHERE price * 0.9 > 1000000;

-- Inefficient C: LIKE with leading wildcard
SELECT * FROM customers WHERE name LIKE '%Kim%';
```


??? tip "Hint"
    - You can use an index by moving the function/calculation to the **comparison value** side rather than the column.
    - `LIKE 'Kim%'` (prefix search) can use indexes, `LIKE '%Kim%'` (intermediate search) cannot.
    - Price terms are mathematically converted to both sides.

??? success "Answer"
    ```sql
    -- Improvement A: convert to range condition
    SELECT * FROM orders
    WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01';
    -- Can use idx_orders_ordered_at index

    -- Improvement B: move calculation to comparison value side
    SELECT * FROM products
    WHERE price > 1000000 / 0.9;  -- price > 1111111.11
    -- Can use idx_products_xxx index

    -- Improvement C: change to prefix search (when possible)
    SELECT * FROM customers
    WHERE name LIKE 'Kim%';  -- Customers whose name starts with 'Kim'
    -- Can use idx_customers_name index (prefix LIKE)

    -- If intermediate search is absolutely necessary -> consider FTS (full-text search) or a separate search column
    ```

    | Original | Improved | Index used |
    |---|---|---|
    | `strftime('%Y', ordered_at) = '2024'` | `ordered_at >= '2024-01-01' AND ...` | O |
    | `price * 0.9 > 1000000` | `price > 1111111.11` | O |
    | `name LIKE '%Kim%'` | `name LIKE 'Kim%'` | O (prefix only) |


---


### Problem 13. EXISTS vs IN performance comparison

When obtaining a list of customers who have written reviews, compare the two execution plans: `IN` and `EXISTS`.

```sql
-- Method A: IN
SELECT * FROM customers WHERE id IN (SELECT DISTINCT customer_id FROM reviews);

-- Method B: EXISTS
SELECT * FROM customers AS c
WHERE EXISTS (SELECT 1 FROM reviews AS r WHERE r.customer_id = c.id);
```


??? tip "Hint"
    - Check the execution plan of both queries with `EXPLAIN QUERY PLAN`
    - The SQLite optimizer also automatically converts IN to EXISTS.
    - EXISTS is advantageous when the outer table is small and the inner table has an index.

??? success "Answer"
    ```sql
    -- Method A: IN
    EXPLAIN QUERY PLAN
    SELECT * FROM customers WHERE id IN (SELECT DISTINCT customer_id FROM reviews);

    -- Method B: EXISTS
    EXPLAIN QUERY PLAN
    SELECT * FROM customers AS c
    WHERE EXISTS (SELECT 1 FROM reviews AS r WHERE r.customer_id = c.id);
    ```

    SQLite often produces similar execution plans for both methods:

    | Method | Execution plan | Notes |
    |---|---|---|
    | IN (subquery) | SCAN customers + LIST SUBQUERY (reviews) | Builds temporary list from subquery results |
    | EXISTS | SCAN customers + CORRELATED (reviews USING INDEX) | Checks existence only via index |

    - Since reviews have `idx_reviews_customer_id`, EXISTS utilizes the index to efficiently
    - IN executes the entire subquery first and then compares it, so memory usage increases when the result is large.


---


### Problem 14. Identifying unnecessary indexes

Too many indexes will result in poor INSERT/UPDATE performance.
Analyze whether any of the indexes in the `orders` table are redundant or unnecessary.


??? tip "Hint"
    - If there is a composite index `(customer_id, status)`, the single index `(customer_id)` is redundant.
    - Search is possible using only the first column of the composite index.
    - However, if you often search using only the second column, a separate index is required.

??? success "Answer"
    ```sql
    -- Index list for the orders table
    SELECT name, sql
    FROM sqlite_master
    WHERE type = 'index'
      AND tbl_name = 'orders'
      AND sql IS NOT NULL
    ORDER BY name;
    ```

    | index_name | Column(s) | Analysis |
    |---|---|---|
    | idx_orders_customer_id | (customer_id) | Possibly redundant -- first column of idx_orders_customer_status |
    | idx_orders_customer_status | (customer_id, status) | Keep -- also covers customer_id-only searches |
    | idx_orders_ordered_at | (ordered_at) | Keep -- essential for date range searches |
    | idx_orders_order_number | (order_number) | Keep -- for UNIQUE lookups |
    | idx_orders_status | (status) | Low selectivity -- candidate for removal |

    **Conclusion**: `idx_orders_customer_id` is included in `idx_orders_customer_status` and is therefore a candidate for removal.
    However, considering the covering index effect (smaller index when status is not needed), it can be maintained.


---


### Problem 15. Summary — Slow Query Optimization Workshop

The following query is a sales report by category that runs monthly.
Analyze the execution plan and optimize it by adding indexes and improving query structure.

```sql
-- Original query (before optimization)
SELECT
    cat.name AS category,
    strftime('%Y-%m', o.ordered_at) AS month,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items AS oi,
     orders AS o,
     products AS p,
     categories AS cat
WHERE oi.order_id = o.id
  AND oi.product_id = p.id
  AND p.category_id = cat.id
  AND strftime('%Y', o.ordered_at) = '2024'
  AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
GROUP BY cat.name, strftime('%Y-%m', o.ordered_at)
ORDER BY cat.name, month;
```


??? tip "Hint"
    1. `strftime('%Y', ordered_at) = '2024'` → Convert to range condition (SARGable)
    2. Convert implicit JOIN (comma) to explicit `INNER JOIN`
    3. Identify full scan table with `EXPLAIN QUERY PLAN`
    4. Add covering index if necessary

??? success "Answer"
    ```sql
    -- 1) Check execution plan (original)
    EXPLAIN QUERY PLAN
    SELECT
        cat.name AS category,
        strftime('%Y-%m', o.ordered_at) AS month,
        COUNT(DISTINCT o.id) AS order_count,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items AS oi,
         orders AS o,
         products AS p,
         categories AS cat
    WHERE oi.order_id = o.id
      AND oi.product_id = p.id
      AND p.category_id = cat.id
      AND strftime('%Y', o.ordered_at) = '2024'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY cat.name, strftime('%Y-%m', o.ordered_at)
    ORDER BY cat.name, month;
    -- Problem: full table scan on orders due to strftime() function

    -- 2) Optimized query
    SELECT
        cat.name AS category,
        SUBSTR(o.ordered_at, 1, 7) AS month,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
    FROM orders AS o
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.ordered_at >= '2024-01-01'
      AND o.ordered_at < '2025-01-01'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY cat.name, SUBSTR(o.ordered_at, 1, 7)
    ORDER BY cat.name, month;

    -- 3) Check execution plan after optimization
    EXPLAIN QUERY PLAN
    SELECT
        cat.name AS category,
        SUBSTR(o.ordered_at, 1, 7) AS month,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
    FROM orders AS o
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.ordered_at >= '2024-01-01'
      AND o.ordered_at < '2025-01-01'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY cat.name, SUBSTR(o.ordered_at, 1, 7)
    ORDER BY cat.name, month;
    ```

    | Improvement | Original | Optimized |
    |---|---|---|
    | Date filter | `strftime(...)` (Non-SARGable) | Range condition (SARGable) |
    | JOIN syntax | Implicit (comma) | Explicit INNER JOIN |
    | Month extraction | `strftime('%Y-%m', ...)` | `SUBSTR(..., 1, 7)` (lighter) |
    | orders access | SCAN TABLE (full scan) | SEARCH USING INDEX idx_orders_ordered_at |
