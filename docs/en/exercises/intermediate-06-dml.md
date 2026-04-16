# DML Practice (INSERT, UPDATE, DELETE)

!!! info "Tables"

    `products` — Products (name, price, stock, brand)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  



!!! abstract "Concepts"

    `INSERT INTO`, `UPDATE SET`, `DELETE FROM`, `INSERT INTO SELECT`, `subquery DML`, `UPSERT`, `ON CONFLICT`



### 1. Create a practice product table and insert one product.


Create a practice product table and insert one product.


**Hint 1:** `CREATE TABLE temp_products AS SELECT * FROM products WHERE 1=0` — creates an empty table copying only the structure.


??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;
    
    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (9001, 1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01');
    
    SELECT * FROM temp_products;
    
    DROP TABLE temp_products;
    ```


---


### 2. Insert multiple rows into the practice product table at once


Insert multiple rows into the practice product table at once.


**Hint 1:** `INSERT INTO ... VALUES (...), (...), (...)` — SQLite supports multiple VALUES rows in one INSERT.


??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;
    
    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES
        (9001, 1, 1, '테스트 마우스', 'TEST-MS-001', 'TestBrand', 35000, 18000, 200, 1, '2025-01-01', '2025-01-01'),
        (9002, 1, 1, '테스트 패드', 'TEST-PD-001', 'TestBrand', 15000, 7000, 500, 1, '2025-01-01', '2025-01-01'),
        (9003, 2, 1, '테스트 모니터', 'TEST-MN-001', 'TestBrand', 350000, 200000, 50, 1, '2025-01-01', '2025-01-01');
    
    SELECT id, name, price FROM temp_products;
    
    DROP TABLE temp_products;
    ```


---


### 3. Update the price of a specific product in the practice table


Update the price of a specific product in the practice table.


**Hint 1:** `UPDATE temp_products SET price = ... WHERE id = ...` — always include a WHERE clause.


??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;
    
    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES
        (9001, 1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01'),
        (9002, 1, 1, '테스트 마우스', 'TEST-MS-001', 'TestBrand', 35000, 18000, 200, 1, '2025-01-01', '2025-01-01');
    
    UPDATE temp_products
    SET price = 79000, updated_at = '2025-06-01'
    WHERE id = 9001;
    
    SELECT id, name, price, updated_at FROM temp_products;
    
    DROP TABLE temp_products;
    ```


---


### 4. Delete a specific product from the practice table.


Delete a specific product from the practice table.


**Hint 1:** `DELETE FROM temp_products WHERE id = ...` — running without WHERE deletes all data.


??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;
    
    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES
        (9001, 1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01'),
        (9002, 1, 1, '테스트 마우스', 'TEST-MS-001', 'TestBrand', 35000, 18000, 200, 1, '2025-01-01', '2025-01-01'),
        (9003, 1, 1, '테스트 패드', 'TEST-PD-001', 'TestBrand', 15000, 7000, 500, 1, '2025-01-01', '2025-01-01');
    
    DELETE FROM temp_products WHERE id = 9002;
    
    SELECT id, name FROM temp_products;
    
    DROP TABLE temp_products;
    ```


---


### 5. Create a practice customer table and bulk-change all 'BRONZE


Create a practice customer table and bulk-change all 'BRONZE' grades to 'SILVER'.


**Hint 1:** `UPDATE temp_customers SET grade = 'SILVER' WHERE grade = 'BRONZE'` — all matching rows are changed.


??? success "Answer"
    ```sql
    CREATE TABLE temp_customers AS
    SELECT id, name, email, grade, point_balance
    FROM customers
    LIMIT 50;
    
    SELECT grade, COUNT(*) AS cnt FROM temp_customers GROUP BY grade;
    
    UPDATE temp_customers
    SET grade = 'SILVER'
    WHERE grade = 'BRONZE';
    
    SELECT grade, COUNT(*) AS cnt FROM temp_customers GROUP BY grade;
    
    DROP TABLE temp_customers;
    ```


---


### 6. Delete all customers with zero points from the practice tabl


Delete all customers with zero points from the practice table. Compare counts before and after deletion.


**Hint 1:** Run `SELECT COUNT(*)` before deletion, execute DELETE, then run `SELECT COUNT(*)` after.


??? success "Answer"
    ```sql
    CREATE TABLE temp_customers AS
    SELECT id, name, email, grade, point_balance
    FROM customers
    LIMIT 100;
    
    SELECT COUNT(*) AS before_count FROM temp_customers;
    
    DELETE FROM temp_customers WHERE point_balance = 0;
    
    SELECT COUNT(*) AS after_count FROM temp_customers;
    
    DROP TABLE temp_customers;
    ```


---


### 7. Increase all product prices by 10% in the practice table.


Increase all product prices by 10% in the practice table.


**Hint 1:** `UPDATE temp_products SET price = ROUND(price * 1.1, 2)` — use ROUND to clean up decimal places.


??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT id, name, price
    FROM products
    WHERE is_active = 1
    LIMIT 20;
    
    SELECT name, price FROM temp_products ORDER BY price DESC LIMIT 5;
    
    UPDATE temp_products
    SET price = ROUND(price * 1.1, 2);
    
    SELECT name, price FROM temp_products ORDER BY price DESC LIMIT 5;
    
    DROP TABLE temp_products;
    ```


---


### 8. Use INSERT OR REPLACE (UPSERT) to insert a product, updating


Use INSERT OR REPLACE (UPSERT) to insert a product, updating price if it already exists.


**Hint 1:** The table needs a UNIQUE constraint. Create with UNIQUE(sku) then use `INSERT OR REPLACE`.


??? success "Answer"
    ```sql
    CREATE TABLE temp_products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        sku TEXT NOT NULL UNIQUE,
        price REAL NOT NULL
    );
    
    INSERT INTO temp_products VALUES (1, '무선 마우스', 'WM-001', 35000);
    INSERT INTO temp_products VALUES (2, '기계식 키보드', 'MK-001', 89000);
    
    SELECT * FROM temp_products;
    
    INSERT OR REPLACE INTO temp_products VALUES (1, '무선 마우스 v2', 'WM-001', 39000);
    
    SELECT * FROM temp_products;
    
    DROP TABLE temp_products;
    ```


---


### 9. Write a more precise UPSERT using ON CONFLICT. Only update t


Write a more precise UPSERT using ON CONFLICT. Only update the price on conflict.


**Hint 1:** `ON CONFLICT(sku) DO UPDATE SET price = excluded.price` — `excluded` references the new values being inserted.


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
    
    INSERT INTO temp_products (id, name, sku, price, updated_at)
    VALUES (1, '무선 마우스 NEW', 'WM-001', 42000, '2025-06-01')
    ON CONFLICT(sku) DO UPDATE SET
        price = excluded.price,
        updated_at = excluded.updated_at;
    
    SELECT * FROM temp_products;
    
    DROP TABLE temp_products;
    ```


---


### 10. Conditional UPDATE: Increase prices by 5% only for products 


Conditional UPDATE: Increase prices by 5% only for products with stock below 10.


**Hint 1:** `UPDATE ... SET price = ROUND(price * 1.05, 2) WHERE stock_qty < 10` — price increase only for low-stock products.


??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT id, name, price, stock_qty
    FROM products
    WHERE is_active = 1
    LIMIT 30;
    
    SELECT name, price, stock_qty
    FROM temp_products
    WHERE stock_qty < 10
    ORDER BY stock_qty;
    
    UPDATE temp_products
    SET price = ROUND(price * 1.05, 2)
    WHERE stock_qty < 10;
    
    SELECT name, price, stock_qty
    FROM temp_products
    WHERE stock_qty < 10
    ORDER BY stock_qty;
    
    DROP TABLE temp_products;
    ```


---


### 11. Use INSERT...SELECT to copy VIP customers into a separate ta


Use INSERT...SELECT to copy VIP customers into a separate table.


**Hint 1:** `INSERT INTO temp_vip SELECT ... FROM customers WHERE grade = 'VIP'` — use SELECT instead of VALUES.


??? success "Answer"
    ```sql
    CREATE TABLE temp_vip (
        id INTEGER,
        name TEXT,
        email TEXT,
        grade TEXT,
        point_balance INTEGER
    );
    
    INSERT INTO temp_vip
    SELECT id, name, email, grade, point_balance
    FROM customers
    WHERE grade = 'VIP';
    
    SELECT COUNT(*) AS vip_count FROM temp_vip;
    SELECT name, point_balance FROM temp_vip ORDER BY point_balance DESC LIMIT 10;
    
    DROP TABLE temp_vip;
    ```


---


### 12. Use INSERT...SELECT to create a 2025 monthly revenue summary


Use INSERT...SELECT to create a 2025 monthly revenue summary table.


**Hint 1:** `CREATE TABLE AS SELECT` creates the table and inserts data simultaneously.


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
    
    SELECT * FROM temp_monthly_sales ORDER BY month;
    
    DROP TABLE temp_monthly_sales;
    ```


---


### 13. Use CASE in a conditional UPDATE: award bonus points by grad


Use CASE in a conditional UPDATE: award bonus points by grade.


**Hint 1:** Use CASE in SET for tiered bonus by grade.


??? success "Answer"
    ```sql
    CREATE TABLE temp_customers AS
    SELECT id, name, grade, point_balance
    FROM customers
    LIMIT 50;
    
    SELECT grade, ROUND(AVG(point_balance)) AS avg_point
    FROM temp_customers
    GROUP BY grade;
    
    UPDATE temp_customers
    SET point_balance = point_balance +
        CASE grade
            WHEN 'VIP'    THEN 5000
            WHEN 'GOLD'   THEN 3000
            WHEN 'SILVER' THEN 1000
            ELSE 500
        END;
    
    SELECT grade, ROUND(AVG(point_balance)) AS avg_point
    FROM temp_customers
    GROUP BY grade;
    
    DROP TABLE temp_customers;
    ```


---


### 14. Use a subquery in UPDATE: deduct stock based on order quanti


Use a subquery in UPDATE: deduct stock based on order quantities.


**Hint 1:** Use COALESCE for NULL handling when the subquery returns no rows.


??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT id, name, stock_qty
    FROM products
    WHERE is_active = 1
    LIMIT 20;
    
    SELECT name, stock_qty FROM temp_products ORDER BY name LIMIT 5;
    
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
    
    SELECT name, stock_qty FROM temp_products ORDER BY name LIMIT 5;
    
    DROP TABLE temp_products;
    ```


---


### 15. Product catalog copy and cleanup: perform a 3-step process o


Product catalog copy and cleanup: perform a 3-step process of copy, mark, delete.


**Hint 1:** Step 1: Copy, Step 2: Mark discontinued, Step 3: Delete marked. Verify after each step.


??? success "Answer"
    ```sql
    CREATE TABLE temp_products AS
    SELECT id, name, price, is_active, discontinued_at
    FROM products;
    
    SELECT COUNT(*) AS total FROM temp_products;
    
    UPDATE temp_products
    SET is_active = 0
    WHERE discontinued_at IS NOT NULL;
    
    SELECT
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive
    FROM temp_products;
    
    DELETE FROM temp_products WHERE is_active = 0;
    
    SELECT COUNT(*) AS remaining FROM temp_products;
    
    DROP TABLE temp_products;
    ```


---


### 16. Safe delete pattern: verify deletion targets before deleting


Safe delete pattern: verify deletion targets before deleting.


**Hint 1:** Run a SELECT with the same WHERE condition as your DELETE first to verify targets and count.


??? success "Answer"
    ```sql
    CREATE TABLE temp_orders AS
    SELECT id, order_number, customer_id, status, total_amount, ordered_at
    FROM orders
    WHERE ordered_at LIKE '2024%'
    LIMIT 200;
    
    SELECT COUNT(*) AS to_delete
    FROM temp_orders
    WHERE status = 'cancelled';
    
    SELECT order_number, total_amount, ordered_at
    FROM temp_orders
    WHERE status = 'cancelled'
    LIMIT 10;
    
    DELETE FROM temp_orders WHERE status = 'cancelled';
    
    SELECT COUNT(*) AS remaining FROM temp_orders;
    SELECT status, COUNT(*) FROM temp_orders GROUP BY status;
    
    DROP TABLE temp_orders;
    ```


---


### 17. Use INSERT...SELECT with aggregation to create a per-custome


Use INSERT...SELECT with aggregation to create a per-customer purchase statistics table.


**Hint 1:** Materialize the aggregation result into a table.


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
    
    SELECT name, grade, order_count, total_spent, last_order_at
    FROM temp_customer_stats
    ORDER BY total_spent DESC
    LIMIT 10;
    
    DROP TABLE temp_customer_stats;
    ```


---


### 18. Combine multiple conditions in a bulk UPDATE: deactivate cus


Combine multiple conditions in a bulk UPDATE: deactivate customers with no orders in the past year.


**Hint 1:** Use a subquery to find customers with no recent orders.


??? success "Answer"
    ```sql
    CREATE TABLE temp_customers AS
    SELECT id, name, grade, is_active, created_at
    FROM customers;
    
    SELECT
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive
    FROM temp_customers;
    
    UPDATE temp_customers
    SET is_active = 0
    WHERE id NOT IN (
        SELECT DISTINCT customer_id
        FROM orders
        WHERE ordered_at >= DATE('now', '-1 year')
          AND status NOT IN ('cancelled')
    );
    
    SELECT
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive
    FROM temp_customers;
    
    DROP TABLE temp_customers;
    ```


---


### 19. Perform multi-step DML like a transaction: refund points and


Perform multi-step DML like a transaction: refund points and restore stock on order cancellation.


**Hint 1:** 1) Change order status to 'cancelled', 2) Refund used points to customer, 3) Restore stock. Perform three steps in order.


??? success "Answer"
    ```sql
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
    
    UPDATE temp_orders
    SET status = 'cancelled'
    WHERE id = (SELECT MIN(id) FROM temp_orders);
    
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
    
    UPDATE temp_products
    SET stock_qty = stock_qty + COALESCE(
        (SELECT SUM(oi.quantity)
         FROM order_items AS oi
         WHERE oi.order_id = (SELECT MIN(id) FROM temp_orders WHERE status = 'cancelled')
           AND oi.product_id = temp_products.id),
        0
    );
    
    SELECT '주문' AS table_name, order_number, status FROM temp_orders
    UNION ALL
    SELECT '고객', name, CAST(point_balance AS TEXT) FROM temp_customers LIMIT 3;
    
    DROP TABLE temp_orders;
    DROP TABLE temp_customers;
    DROP TABLE temp_products;
    ```


---


### 20. Data normalization: split a denormalized table into two norm


Data normalization: split a denormalized table into two normalized tables.


**Hint 1:** 1) Create denormalized table with sample data. 2) Extract brand master using DISTINCT. 3) Link product table with brand_id.


??? success "Answer"
    ```sql
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
    
    CREATE TABLE temp_brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    
    INSERT INTO temp_brands (name)
    SELECT DISTINCT brand_name
    FROM temp_raw_products
    ORDER BY brand_name;
    
    SELECT * FROM temp_brands ORDER BY id LIMIT 10;
    
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
    
    SELECT np.id, np.name, b.name AS brand, np.price
    FROM temp_norm_products AS np
    INNER JOIN temp_brands AS b ON np.brand_id = b.id
    ORDER BY b.name, np.name
    LIMIT 10;
    
    DROP TABLE temp_raw_products;
    DROP TABLE temp_brands;
    DROP TABLE temp_norm_products;
    ```


---
