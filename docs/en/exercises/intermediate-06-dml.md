# DML Practice (INSERT, UPDATE, DELETE)

!!! info "Tables"
    `products` — Products (name, price, stock, brand)  
    `customers` — Customers (grade, points, channel)  
    `orders` — Orders (status, amount, date)  
    `order_items` — Order items (qty, unit price)  

!!! abstract "Concepts"
    `INSERT INTO`, `UPDATE SET`, `DELETE FROM`, `INSERT INTO ... SELECT`, Subquery-based DML

!!! warning "Caution"
    DML statements modify data. In these exercises, create **temporary tables** for practice and drop them when done.
    Do not directly modify the original tables.

---


## Basic (1-7): INSERT, UPDATE, DELETE Basics

### Problem 1. Create a practice product table and insert one product.

First create a `temp_products` table, then add data with an INSERT statement.

??? tip "Hint"
    `CREATE TABLE temp_products AS SELECT * FROM products WHERE 1=0` — creates an empty table copying only the structure. Then `INSERT INTO ... VALUES (...)`.

??? success "Answer"
    ```sql
    -- Step 1: Create empty table with copied structure
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;

    -- Step 2: Insert one product
    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (9001, 1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01');

    -- Verify
    SELECT * FROM temp_products;

    -- Cleanup
    DROP TABLE temp_products;
    ```


---


### Problem 2. Insert multiple rows into the practice product table at once.

Add multiple rows in a single INSERT by separating VALUES with commas.

??? tip "Hint"
    `INSERT INTO ... VALUES (...), (...), (...)` — SQLite supports multiple VALUES rows in one INSERT statement.

??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;

    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES
        (9001, 1, 1, '테스트 마우스', 'TEST-MS-001', 'TestBrand', 35000, 18000, 200, 1, '2025-01-01', '2025-01-01'),
        (9002, 1, 1, '테스트 패드', 'TEST-PD-001', 'TestBrand', 15000, 7000, 500, 1, '2025-01-01', '2025-01-01'),
        (9003, 2, 1, '테스트 모니터', 'TEST-MN-001', 'TestBrand', 350000, 200000, 50, 1, '2025-01-01', '2025-01-01');

    -- Verify
    SELECT id, name, price FROM temp_products;

    DROP TABLE temp_products;
    ```

    | id | name | price |
    |----|------|-------|
    | 9001 | 테스트 마우스 | 35000 |
    | 9002 | 테스트 패드 | 15000 |
    | 9003 | 테스트 모니터 | 350000 |


---


### Problem 3. Update the price of a specific product in the practice table.

Use UPDATE + WHERE to modify only specific rows. Be careful: UPDATE without WHERE changes all rows.

??? tip "Hint"
    `UPDATE temp_products SET price = ... WHERE id = ...` — always include a WHERE clause.

??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;

    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES
        (9001, 1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01'),
        (9002, 1, 1, '테스트 마우스', 'TEST-MS-001', 'TestBrand', 35000, 18000, 200, 1, '2025-01-01', '2025-01-01');

    -- Update price
    UPDATE temp_products
    SET price = 79000, updated_at = '2025-06-01'
    WHERE id = 9001;

    -- Verify
    SELECT id, name, price, updated_at FROM temp_products;

    DROP TABLE temp_products;
    ```


---


### Problem 4. Delete a specific product from the practice table.

Use DELETE + WHERE to delete only specific rows.

??? tip "Hint"
    `DELETE FROM temp_products WHERE id = ...` — running without WHERE deletes all data, so always specify a condition.

??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;

    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES
        (9001, 1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01'),
        (9002, 1, 1, '테스트 마우스', 'TEST-MS-001', 'TestBrand', 35000, 18000, 200, 1, '2025-01-01', '2025-01-01'),
        (9003, 1, 1, '테스트 패드', 'TEST-PD-001', 'TestBrand', 15000, 7000, 500, 1, '2025-01-01', '2025-01-01');

    -- Delete
    DELETE FROM temp_products WHERE id = 9002;

    -- Verify (2 rows remain)
    SELECT id, name FROM temp_products;

    DROP TABLE temp_products;
    ```


---


### Problem 5. Create a practice customer table and bulk-change all 'BRONZE' grades to 'SILVER'.

Use WHERE to UPDATE multiple rows at once.

??? tip "Hint"
    `UPDATE temp_customers SET grade = 'SILVER' WHERE grade = 'BRONZE'` — all matching rows are changed.

??? success "Answer"
    ```sql
    -- Copy some existing data to create a practice table
    CREATE TABLE temp_customers AS
    SELECT id, name, email, grade, point_balance
    FROM customers
    LIMIT 50;

    -- Check before change
    SELECT grade, COUNT(*) AS cnt FROM temp_customers GROUP BY grade;

    -- Bulk change BRONZE -> SILVER
    UPDATE temp_customers
    SET grade = 'SILVER'
    WHERE grade = 'BRONZE';

    -- Check after change
    SELECT grade, COUNT(*) AS cnt FROM temp_customers GROUP BY grade;

    DROP TABLE temp_customers;
    ```


---


### Problem 6. Delete all customers with zero points from the practice table. Compare counts before and after deletion.

Use DELETE + WHERE for conditional deletion, then verify the count.

??? tip "Hint"
    Run `SELECT COUNT(*)` before deletion, execute DELETE, then run `SELECT COUNT(*)` after.

??? success "Answer"
    ```sql
    CREATE TABLE temp_customers AS
    SELECT id, name, email, grade, point_balance
    FROM customers
    LIMIT 100;

    -- Count before deletion
    SELECT COUNT(*) AS before_count FROM temp_customers;

    -- Delete customers with zero points
    DELETE FROM temp_customers WHERE point_balance = 0;

    -- Count after deletion
    SELECT COUNT(*) AS after_count FROM temp_customers;

    DROP TABLE temp_customers;
    ```


---


### Problem 7. Increase all product prices by 10% in the practice table.

UPDATE without WHERE applies to all rows. This is an intentional bulk modification.

??? tip "Hint"
    `UPDATE temp_products SET price = ROUND(price * 1.1, 2)` — use ROUND to clean up decimal places.

??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT id, name, price
    FROM products
    WHERE is_active = 1
    LIMIT 20;

    -- Before increase
    SELECT name, price FROM temp_products ORDER BY price DESC LIMIT 5;

    -- 10% price increase for all
    UPDATE temp_products
    SET price = ROUND(price * 1.1, 2);

    -- After increase
    SELECT name, price FROM temp_products ORDER BY price DESC LIMIT 5;

    DROP TABLE temp_products;
    ```


---


## Applied (8-14): UPSERT, Conditional UPDATE, INSERT...SELECT

### Problem 8. Use INSERT OR REPLACE (UPSERT) to insert a product, updating price if it already exists.

SQLite's `INSERT OR REPLACE` deletes the existing row and inserts a new one when a UNIQUE constraint is violated.

??? tip "Hint"
    The table needs a UNIQUE constraint. Create `CREATE TABLE temp_products (..., UNIQUE(sku))` then use `INSERT OR REPLACE`.

??? success "Answer"
    ```sql
    CREATE TABLE temp_products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        sku TEXT NOT NULL UNIQUE,
        price REAL NOT NULL
    );

    -- Initial insert
    INSERT INTO temp_products VALUES (1, '무선 마우스', 'WM-001', 35000);
    INSERT INTO temp_products VALUES (2, '기계식 키보드', 'MK-001', 89000);

    -- Verify
    SELECT * FROM temp_products;

    -- UPSERT: sku 'WM-001' already exists, so it gets replaced
    INSERT OR REPLACE INTO temp_products VALUES (1, '무선 마우스 v2', 'WM-001', 39000);

    -- Verify (name and price changed)
    SELECT * FROM temp_products;

    DROP TABLE temp_products;
    ```


---


### Problem 9. Write a more precise UPSERT using ON CONFLICT. Only update the price on conflict.

`INSERT ... ON CONFLICT(column) DO UPDATE SET ...` updates only specific columns on conflict. More precise than INSERT OR REPLACE.

??? tip "Hint"
    `ON CONFLICT(sku) DO UPDATE SET price = excluded.price` — `excluded` is a special keyword referencing the new values being inserted.

??? success "Answer"
    ```sql
    CREATE TABLE temp_products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        sku TEXT NOT NULL UNIQUE,
        price REAL NOT NULL,
        updated_at TEXT
    );

    INSERT INTO temp_products VALUES (1, '무선 마우스', 'WM-001', 35000, '2025-01-01');
    INSERT INTO temp_products VALUES (2, '기계식 키보드', 'MK-001', 89000, '2025-01-01');

    -- ON CONFLICT: on sku collision, update only price and updated_at (name preserved)
    INSERT INTO temp_products (id, name, sku, price, updated_at)
    VALUES (1, '무선 마우스 NEW', 'WM-001', 42000, '2025-06-01')
    ON CONFLICT(sku) DO UPDATE SET
        price = excluded.price,
        updated_at = excluded.updated_at;

    -- Verify: name remains '무선 마우스', price updated to 42000
    SELECT * FROM temp_products;

    DROP TABLE temp_products;
    ```

    | id | name | sku | price | updated_at |
    |----|------|-----|-------|------------|
    | 1 | 무선 마우스 | WM-001 | 42000 | 2025-06-01 |
    | 2 | 기계식 키보드 | MK-001 | 89000 | 2025-01-01 |


---


### Problem 10. Conditional UPDATE: Increase prices by 5% only for products with stock below 10.

Use WHERE to selectively UPDATE only rows matching a specific condition.

??? tip "Hint"
    `UPDATE ... SET price = ROUND(price * 1.05, 2) WHERE stock_qty < 10` — price increase only for low-stock products.

??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT id, name, price, stock_qty
    FROM products
    WHERE is_active = 1
    LIMIT 30;

    -- Before: check products with stock < 10
    SELECT name, price, stock_qty
    FROM temp_products
    WHERE stock_qty < 10
    ORDER BY stock_qty;

    -- Conditional price increase
    UPDATE temp_products
    SET price = ROUND(price * 1.05, 2)
    WHERE stock_qty < 10;

    -- After: verify
    SELECT name, price, stock_qty
    FROM temp_products
    WHERE stock_qty < 10
    ORDER BY stock_qty;

    DROP TABLE temp_products;
    ```


---


### Problem 11. Use INSERT...SELECT to copy VIP customers into a separate table.

Use the result of a SELECT directly as input for INSERT. Useful for data migration and backups.

??? tip "Hint"
    `INSERT INTO temp_vip SELECT ... FROM customers WHERE grade = 'VIP'` — use SELECT instead of VALUES.

??? success "Answer"
    ```sql
    -- Create empty table
    CREATE TABLE temp_vip (
        id INTEGER,
        name TEXT,
        email TEXT,
        grade TEXT,
        point_balance INTEGER
    );

    -- Copy VIP customers
    INSERT INTO temp_vip
    SELECT id, name, email, grade, point_balance
    FROM customers
    WHERE grade = 'VIP';

    -- Verify
    SELECT COUNT(*) AS vip_count FROM temp_vip;
    SELECT name, point_balance FROM temp_vip ORDER BY point_balance DESC LIMIT 10;

    DROP TABLE temp_vip;
    ```


---


### Problem 12. Use INSERT...SELECT to create a 2025 monthly revenue summary table.

Save the result of an aggregation query into a new table. Useful for creating reporting tables.

??? tip "Hint"
    `CREATE TABLE temp_monthly_sales AS SELECT ...` — CREATE TABLE AS SELECT creates the table and inserts data simultaneously.

??? success "Answer"
    ```sql
    CREATE TABLE temp_monthly_sales AS
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS order_count,
        COUNT(DISTINCT customer_id) AS customer_count,
        ROUND(SUM(total_amount), 2) AS revenue,
        ROUND(AVG(total_amount), 2) AS avg_order
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7);

    -- Verify
    SELECT * FROM temp_monthly_sales ORDER BY month;

    DROP TABLE temp_monthly_sales;
    ```


---


### Problem 13. Use CASE in a conditional UPDATE: award bonus points by grade.

Use a CASE expression in the SET clause to apply different values based on conditions.

??? tip "Hint"
    `SET point_balance = point_balance + CASE WHEN grade = 'VIP' THEN 5000 WHEN grade = 'GOLD' THEN 3000 ... END` — tiered bonus by grade.

??? success "Answer"
    ```sql
    CREATE TABLE temp_customers AS
    SELECT id, name, grade, point_balance
    FROM customers
    LIMIT 50;

    -- Average points by grade before change
    SELECT grade, ROUND(AVG(point_balance)) AS avg_point
    FROM temp_customers
    GROUP BY grade;

    -- Award tiered bonus points by grade
    UPDATE temp_customers
    SET point_balance = point_balance +
        CASE grade
            WHEN 'VIP'    THEN 5000
            WHEN 'GOLD'   THEN 3000
            WHEN 'SILVER' THEN 1000
            ELSE 500
        END;

    -- Average points by grade after change
    SELECT grade, ROUND(AVG(point_balance)) AS avg_point
    FROM temp_customers
    GROUP BY grade;

    DROP TABLE temp_customers;
    ```


---


### Problem 14. Use a subquery in UPDATE: deduct stock based on order quantities.

Use a subquery in the SET clause to apply aggregated values from another table.

??? tip "Hint"
    `SET stock_qty = stock_qty - (SELECT SUM(quantity) FROM order_items WHERE product_id = temp_products.id)` — compute total order quantity via subquery and deduct. Use COALESCE for NULL handling.

??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT id, name, stock_qty
    FROM products
    WHERE is_active = 1
    LIMIT 20;

    -- Before
    SELECT name, stock_qty FROM temp_products ORDER BY name LIMIT 5;

    -- Deduct stock by order quantities
    UPDATE temp_products
    SET stock_qty = stock_qty - COALESCE(
        (SELECT SUM(oi.quantity)
         FROM order_items AS oi
         INNER JOIN orders AS o ON oi.order_id = o.id
         WHERE oi.product_id = temp_products.id
           AND o.status NOT IN ('cancelled')
           AND o.ordered_at LIKE '2025%'),
        0
    );

    -- After
    SELECT name, stock_qty FROM temp_products ORDER BY name LIMIT 5;

    DROP TABLE temp_products;
    ```


---


## Advanced (15-20): Multi-step DML, Bulk Changes, Safe Delete Patterns

### Problem 15. Product catalog copy and cleanup: perform a 3-step process of copy, mark, delete.

Practice the data cleanup workflow used in real-world scenarios.

??? tip "Hint"
    Step 1: Copy products, Step 2: Mark discontinued products, Step 3: Delete marked products. Verify results after each step.

??? success "Answer"
    ```sql
    -- Step 1: Copy products
    CREATE TABLE temp_products AS
    SELECT id, name, price, is_active, discontinued_at
    FROM products;

    SELECT COUNT(*) AS total FROM temp_products;

    -- Step 2: Deactivate discontinued products
    UPDATE temp_products
    SET is_active = 0
    WHERE discontinued_at IS NOT NULL;

    SELECT
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive
    FROM temp_products;

    -- Step 3: Delete inactive products
    DELETE FROM temp_products WHERE is_active = 0;

    SELECT COUNT(*) AS remaining FROM temp_products;

    DROP TABLE temp_products;
    ```


---


### Problem 16. Safe delete pattern: verify deletion targets before deleting.

In practice, always verify with SELECT before running DELETE.

??? tip "Hint"
    Run a SELECT with the same WHERE condition as your DELETE first to verify the targets and count.

??? success "Answer"
    ```sql
    CREATE TABLE temp_orders AS
    SELECT id, order_number, customer_id, status, total_amount, ordered_at
    FROM orders
    WHERE ordered_at LIKE '2024%'
    LIMIT 200;

    -- Step 1: Verify deletion targets (preview with SELECT)
    SELECT COUNT(*) AS to_delete
    FROM temp_orders
    WHERE status = 'cancelled';

    SELECT order_number, total_amount, ordered_at
    FROM temp_orders
    WHERE status = 'cancelled'
    LIMIT 10;

    -- Step 2: Delete after verification
    DELETE FROM temp_orders WHERE status = 'cancelled';

    -- Step 3: Verify after deletion
    SELECT COUNT(*) AS remaining FROM temp_orders;
    SELECT status, COUNT(*) FROM temp_orders GROUP BY status;

    DROP TABLE temp_orders;
    ```


---


### Problem 17. Use INSERT...SELECT with aggregation to create a per-customer purchase statistics table.

Save the result of a multi-table JOIN + aggregation into a new table.

??? tip "Hint"
    `CREATE TABLE temp_customer_stats AS SELECT customer_id, COUNT(*), SUM(...), AVG(...) FROM orders GROUP BY customer_id` — materialize the aggregation result into a table.

??? success "Answer"
    ```sql
    CREATE TABLE temp_customer_stats AS
    SELECT
        c.id AS customer_id,
        c.name,
        c.grade,
        COUNT(o.id) AS order_count,
        ROUND(SUM(o.total_amount), 2) AS total_spent,
        ROUND(AVG(o.total_amount), 2) AS avg_order,
        MAX(o.ordered_at) AS last_order_at
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id, c.name, c.grade;

    -- Verify: top spending customers
    SELECT name, grade, order_count, total_spent, last_order_at
    FROM temp_customer_stats
    ORDER BY total_spent DESC
    LIMIT 10;

    DROP TABLE temp_customer_stats;
    ```


---


### Problem 18. Combine multiple conditions in a bulk UPDATE: deactivate customers with no orders in the past year.

A complex UPDATE combining subqueries and date conditions.

??? tip "Hint"
    `WHERE id NOT IN (SELECT customer_id FROM orders WHERE ordered_at >= ...)` — use a subquery to find customers with no recent orders.

??? success "Answer"
    ```sql
    CREATE TABLE temp_customers AS
    SELECT id, name, grade, is_active, created_at
    FROM customers;

    -- Active customer count before
    SELECT
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive
    FROM temp_customers;

    -- Deactivate customers with no orders in the past year
    UPDATE temp_customers
    SET is_active = 0
    WHERE id NOT IN (
        SELECT DISTINCT customer_id
        FROM orders
        WHERE ordered_at >= DATE('now', '-1 year')
          AND status NOT IN ('cancelled')
    );

    -- Active customer count after
    SELECT
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive
    FROM temp_customers;

    DROP TABLE temp_customers;
    ```


---


### Problem 19. Perform multi-step DML like a transaction: refund points and restore stock on order cancellation.

In practice, order cancellation requires modifying multiple tables simultaneously. Practice this flow with temporary tables.

??? tip "Hint"
    1) Change order status to 'cancelled', 2) Refund used points to customer, 3) Restore stock for ordered products. Perform these three steps in order.

??? success "Answer"
    ```sql
    -- Setup: 3 practice tables
    CREATE TABLE temp_orders AS
    SELECT id, order_number, customer_id, status, total_amount, point_used
    FROM orders
    WHERE status = 'paid'
    LIMIT 5;

    CREATE TABLE temp_customers AS
    SELECT id, name, point_balance
    FROM customers
    WHERE id IN (SELECT customer_id FROM temp_orders);

    CREATE TABLE temp_products AS
    SELECT id, name, stock_qty
    FROM products
    WHERE id IN (
        SELECT product_id FROM order_items
        WHERE order_id IN (SELECT id FROM temp_orders)
    );

    -- Check order to cancel
    SELECT order_number, customer_id, total_amount, point_used
    FROM temp_orders
    LIMIT 1;

    -- Step 1: Cancel first order
    UPDATE temp_orders
    SET status = 'cancelled'
    WHERE id = (SELECT MIN(id) FROM temp_orders);

    -- Step 2: Refund used points
    UPDATE temp_customers
    SET point_balance = point_balance + COALESCE(
        (SELECT point_used FROM temp_orders
         WHERE id = (SELECT MIN(id) FROM temp_orders WHERE status = 'cancelled')
           AND status = 'cancelled'),
        0
    )
    WHERE id = (
        SELECT customer_id FROM temp_orders
        WHERE status = 'cancelled' LIMIT 1
    );

    -- Step 3: Restore stock (by order item quantities)
    UPDATE temp_products
    SET stock_qty = stock_qty + COALESCE(
        (SELECT SUM(oi.quantity)
         FROM order_items AS oi
         WHERE oi.order_id = (SELECT MIN(id) FROM temp_orders WHERE status = 'cancelled')
           AND oi.product_id = temp_products.id),
        0
    );

    -- Verify results
    SELECT '주문' AS table_name, order_number, status FROM temp_orders
    UNION ALL
    SELECT '고객', name, CAST(point_balance AS TEXT) FROM temp_customers LIMIT 3;

    DROP TABLE temp_orders;
    DROP TABLE temp_customers;
    DROP TABLE temp_products;
    ```


---


### Problem 20. Data normalization: split a denormalized table into two normalized tables.

Use INSERT...SELECT to extract a master table and a detail table from a single denormalized table.

??? tip "Hint"
    1) Create a denormalized table with sample data. 2) Extract brand master table using DISTINCT. 3) Link product table with brand_id.

??? success "Answer"
    ```sql
    -- Denormalized table (brand name directly in product)
    CREATE TABLE temp_raw_products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        brand_name TEXT,
        price REAL
    );

    INSERT INTO temp_raw_products
    SELECT id, name, brand, price
    FROM products
    LIMIT 30;

    -- Step 1: Extract brand master table
    CREATE TABLE temp_brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );

    INSERT INTO temp_brands (name)
    SELECT DISTINCT brand_name
    FROM temp_raw_products
    ORDER BY brand_name;

    SELECT * FROM temp_brands ORDER BY id LIMIT 10;

    -- Step 2: Normalized product table (referencing brand_id)
    CREATE TABLE temp_norm_products (
        id INTEGER,
        name TEXT,
        brand_id INTEGER,
        price REAL
    );

    INSERT INTO temp_norm_products
    SELECT r.id, r.name, b.id, r.price
    FROM temp_raw_products AS r
    INNER JOIN temp_brands AS b ON r.brand_name = b.name;

    -- Verify: normalized products + brand JOIN
    SELECT np.id, np.name, b.name AS brand, np.price
    FROM temp_norm_products AS np
    INNER JOIN temp_brands AS b ON np.brand_id = b.id
    ORDER BY b.name, np.name
    LIMIT 10;

    -- Cleanup
    DROP TABLE temp_raw_products;
    DROP TABLE temp_brands;
    DROP TABLE temp_norm_products;
    ```


---
