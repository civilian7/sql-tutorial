# EXPLAIN / Query Plan Analysis

#### :material-database: Tables


`customers` — Customers (grade, points, channel)<br>

`orders` — Orders (status, amount, date)<br>

`order_items` — Order items (qty, unit price)<br>

`products` — Products (name, price, stock, brand)<br>

`point_transactions` — Points (earn, use, expire)<br>

`product_views` — View log (customer, product, date)<br>



**:material-book-open-variant: Concepts:** `EXPLAIN`, `QUERY PLAN`, `index`, `performance`, `optimization`


---


### 1. Check the execution plan for this query. Determine if a full


Check the execution plan for this query. Determine if a full table scan occurs.
```sql
SELECT * FROM orders WHERE total_amount > 1000000;
```


**Hint 1:** Check if there's an index on the total_amount column


??? success "Answer"

    === "SQLite"
        ```sql
        EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE total_amount > 1000000;
        ```

    === "MySQL"
        ```sql
        EXPLAIN
    SELECT * FROM orders WHERE total_amount > 1000000;
        ```

    === "PostgreSQL"
        ```sql
        EXPLAIN ANALYZE
    SELECT * FROM orders WHERE total_amount > 1000000;
        ```

    === "Oracle"
        ```sql
        EXPLAIN PLAN FOR
    SELECT * FROM orders WHERE total_amount > 1000000;
    SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY());
        ```

    === "SQL Server"
        ```sql
        SET SHOWPLAN_ALL ON;
    GO
    SELECT * FROM orders WHERE total_amount > 1000000;
    GO
    SET SHOWPLAN_ALL OFF;
        ```


---


### 2. Compare execution plans when querying orders by customer_id 


Compare execution plans when querying orders by customer_id vs by status.
Which is more efficient?


**Hint 1:** The idx_orders_customer_id index exists


??? success "Answer"

    === "SQLite"
        ```sql
        EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 42;
        ```

    === "MySQL"
        ```sql
        EXPLAIN
    SELECT * FROM orders WHERE customer_id = 42;
        ```

    === "PostgreSQL"
        ```sql
        EXPLAIN ANALYZE
    SELECT * FROM orders WHERE customer_id = 42;
        ```

    === "Oracle"
        ```sql
        EXPLAIN PLAN FOR
    SELECT * FROM orders WHERE customer_id = 42;
    SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY());
        ```

    === "SQL Server"
        ```sql
        SET SHOWPLAN_ALL ON;
    GO
    SELECT * FROM orders WHERE customer_id = 42;
    GO
    SET SHOWPLAN_ALL OFF;
        ```


---


### 3. There's a composite index idx_orders_customer_status(custome


There's a composite index idx_orders_customer_status(customer_id, status).
Which of these queries uses this index?
(A) WHERE customer_id = 42 AND status = 'confirmed'
(B) WHERE status = 'confirmed'


**Hint 1:** A composite index requires the first column in the WHERE clause


??? success "Answer"

    === "SQLite"
        ```sql
        EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 42 AND status = 'confirmed';
        ```

    === "MySQL"
        ```sql
        EXPLAIN
    SELECT * FROM orders WHERE customer_id = 42 AND status = 'confirmed';
        ```

    === "PostgreSQL"
        ```sql
        EXPLAIN ANALYZE
    SELECT * FROM orders WHERE customer_id = 42 AND status = 'confirmed';
        ```

    === "Oracle"
        ```sql
        EXPLAIN PLAN FOR
    SELECT * FROM orders WHERE customer_id = 42 AND status = 'confirmed';
    SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY());
        ```

    === "SQL Server"
        ```sql
        SET SHOWPLAN_ALL ON;
    GO
    SELECT * FROM orders WHERE customer_id = 42 AND status = 'confirmed';
    GO
    SET SHOWPLAN_ALL OFF;
        ```


---


### 4. Compare execution plans of two equivalent queries:


Compare execution plans of two equivalent queries:
(A) Subquery: SELECT * FROM products WHERE id IN (SELECT product_id FROM order_items WHERE order_id = 100)
(B) JOIN: SELECT p.* FROM products p JOIN order_items oi ON p.id = oi.product_id WHERE oi.order_id = 100
Which is more efficient?


**Hint 1:** Run EXPLAIN on both the subquery and JOIN versions


??? success "Answer"

    === "SQLite"
        ```sql
        EXPLAIN QUERY PLAN
    SELECT p.* FROM products p
    JOIN order_items oi ON p.id = oi.product_id
    WHERE oi.order_id = 100;
        ```

    === "MySQL"
        ```sql
        EXPLAIN
    SELECT p.* FROM products p
    JOIN order_items oi ON p.id = oi.product_id
    WHERE oi.order_id = 100;
        ```

    === "PostgreSQL"
        ```sql
        EXPLAIN ANALYZE
    SELECT p.* FROM products p
    JOIN order_items oi ON p.id = oi.product_id
    WHERE oi.order_id = 100;
        ```

    === "Oracle"
        ```sql
        EXPLAIN PLAN FOR
    SELECT p.* FROM products p
    JOIN order_items oi ON p.id = oi.product_id
    WHERE oi.order_id = 100;
    SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY());
        ```

    === "SQL Server"
        ```sql
        SET SHOWPLAN_ALL ON;
    GO
    SELECT p.* FROM products p
    JOIN order_items oi ON p.id = oi.product_id
    WHERE oi.order_id = 100;
    GO
    SET SHOWPLAN_ALL OFF;
        ```


---


### 5. When querying only brand and price from products,


When querying only brand and price from products,
check if a covering index effect occurs.
Compare with the idx_products_name index.


**Hint 1:** A covering index returns results from the index alone without table access


??? success "Answer"

    === "SQLite"
        ```sql
        EXPLAIN QUERY PLAN
    SELECT brand, price FROM products WHERE brand = 'Samsung';
        ```

    === "MySQL"
        ```sql
        EXPLAIN
    SELECT brand, price FROM products WHERE brand = 'Samsung';
        ```

    === "PostgreSQL"
        ```sql
        EXPLAIN ANALYZE
    SELECT brand, price FROM products WHERE brand = 'Samsung';
        ```

    === "Oracle"
        ```sql
        EXPLAIN PLAN FOR
    SELECT brand, price FROM products WHERE brand = 'Samsung';
    SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY());
        ```

    === "SQL Server"
        ```sql
        SET SHOWPLAN_ALL ON;
    GO
    SELECT brand, price FROM products WHERE brand = 'Samsung';
    GO
    SET SHOWPLAN_ALL OFF;
        ```


---


### 6. Analyze the execution plan for finding a specific customer's


Analyze the execution plan for finding a specific customer's
browsing history in product_views (~300K rows). Check if indexes are used.


**Hint 1:** The idx_product_views_customer_id index exists


??? success "Answer"

    === "SQLite"
        ```sql
        EXPLAIN QUERY PLAN
    SELECT product_id, viewed_at, duration_seconds
    FROM product_views
    WHERE customer_id = 42
    ORDER BY viewed_at DESC;
        ```

    === "MySQL"
        ```sql
        EXPLAIN
    SELECT product_id, viewed_at, duration_seconds
    FROM product_views
    WHERE customer_id = 42
    ORDER BY viewed_at DESC;
        ```

    === "PostgreSQL"
        ```sql
        EXPLAIN ANALYZE
    SELECT product_id, viewed_at, duration_seconds
    FROM product_views
    WHERE customer_id = 42
    ORDER BY viewed_at DESC;
        ```

    === "Oracle"
        ```sql
        EXPLAIN PLAN FOR
    SELECT product_id, viewed_at, duration_seconds
    FROM product_views
    WHERE customer_id = 42
    ORDER BY viewed_at DESC;
    SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY());
        ```

    === "SQL Server"
        ```sql
        SET SHOWPLAN_ALL ON;
    GO
    SELECT product_id, viewed_at, duration_seconds
    FROM product_views
    WHERE customer_id = 42
    ORDER BY viewed_at DESC;
    GO
    SET SHOWPLAN_ALL OFF;
        ```


---


### 7. Analyze the execution plan of a running total query using wi


Analyze the execution plan of a running total query using window functions
on point_transactions (~130K rows). Check for temp tables or sort operations.


**Hint 1:** Window functions require internal sorting


??? success "Answer"

    === "SQLite"
        ```sql
        EXPLAIN QUERY PLAN
    SELECT customer_id, created_at, amount,
           SUM(amount) OVER (PARTITION BY customer_id ORDER BY created_at) AS running_balance
    FROM point_transactions
    WHERE customer_id = 42;
        ```

    === "MySQL"
        ```sql
        EXPLAIN
    SELECT customer_id, created_at, amount,
           SUM(amount) OVER (PARTITION BY customer_id ORDER BY created_at) AS running_balance
    FROM point_transactions
    WHERE customer_id = 42;
        ```

    === "PostgreSQL"
        ```sql
        EXPLAIN ANALYZE
    SELECT customer_id, created_at, amount,
           SUM(amount) OVER (PARTITION BY customer_id ORDER BY created_at) AS running_balance
    FROM point_transactions
    WHERE customer_id = 42;
        ```

    === "Oracle"
        ```sql
        EXPLAIN PLAN FOR
    SELECT customer_id, created_at, amount,
           SUM(amount) OVER (PARTITION BY customer_id ORDER BY created_at) AS running_balance
    FROM point_transactions
    WHERE customer_id = 42;
    SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY());
        ```

    === "SQL Server"
        ```sql
        SET SHOWPLAN_ALL ON;
    GO
    SELECT customer_id, created_at, amount,
           SUM(amount) OVER (PARTITION BY customer_id ORDER BY created_at) AS running_balance
    FROM point_transactions
    WHERE customer_id = 42;
    GO
    SET SHOWPLAN_ALL OFF;
        ```


---


### 8. Analyze this slow query's execution plan and rewrite it more


Analyze this slow query's execution plan and rewrite it more efficiently.
```sql
SELECT c.name, c.email,
       (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) AS order_count,
       (SELECT SUM(total_amount) FROM orders o WHERE o.customer_id = c.id) AS total_spent
FROM customers c
WHERE (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) > 10;
```


**Hint 1:** Replace 3 correlated subqueries with JOIN + GROUP BY to reduce table scans


??? success "Answer"
    ```sql
    SELECT c.name, c.email, COUNT(o.id) AS order_count, SUM(o.total_amount) AS total_spent
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.email
    HAVING COUNT(o.id) > 10;
    ```


---
