# Query Optimization

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `reviews` — Reviews (rating, content)  



!!! abstract "Concepts"

    `EXPLAIN`, `Index`, `Covering Index`, `Correlated Subquery`, `IN vs EXISTS`



### 1. Reading EXPLAIN


Check the execution plan of the query below.
What is the difference between SCAN TABLE and SEARCH TABLE?


**Hint 1:** `SCAN TABLE` reads the entire table.
`SEARCH TABLE ... USING INDEX` finds only needed rows via index.



??? success "Answer"
    ```sql
    -- 실행 계획 확인
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 100;
    
    -- 인덱스 확인
    SELECT name, sql FROM sqlite_master
    WHERE type = 'index' AND tbl_name = 'orders';
    ```


---


### 2. Index Effect Comparison


Compare execution plans with and without indexes.


**Hint 1:** Run `EXPLAIN QUERY PLAN` for an indexed column (`customer_id`)
and a non-indexed column (`notes`) to compare.



??? success "Answer"
    ```sql
    -- 1) 인덱스가 있는 칼럼으로 검색
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 100;
    
    -- 2) 인덱스가 없는 칼럼으로 검색
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE notes LIKE '%배송%';
    
    -- 3) 현재 인덱스 목록
    SELECT name, tbl_name, sql
    FROM sqlite_master
    WHERE type = 'index'
    ORDER BY tbl_name;
    ```


---


### 3. Subquery to JOIN Conversion


Improve performance by converting correlated subqueries to JOINs.


**Hint 1:** Correlated subqueries execute once per row.
Pre-aggregated subqueries with `LEFT JOIN` execute only once.



??? success "Answer"
    ```sql
    -- 개선: JOIN으로 한 번에 처리
    SELECT
        p.name,
        p.price,
        COALESCE(oi_stats.order_count, 0) AS order_count,
        r_stats.avg_rating
    FROM products p
    LEFT JOIN (
        SELECT product_id, COUNT(*) AS order_count
        FROM order_items GROUP BY product_id
    ) oi_stats ON p.id = oi_stats.product_id
    LEFT JOIN (
        SELECT product_id, ROUND(AVG(rating), 2) AS avg_rating
        FROM reviews GROUP BY product_id
    ) r_stats ON p.id = r_stats.product_id
    WHERE p.is_active = 1;
    ```


    **Result** (top 7 of 218 rows)

    | name | price | order_count | avg_rating |
    |---|---|---|---|
    | Razer Blade 18 Black | 2,987,500.00 | 310 | 3.92 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | 392 | 4.12 |
    | Samsung DDR4 32GB PC4-25600 | 43,500.00 | 871 | 3.94 |
    | Dell U2724D | 894,100.00 | 261 | 4.19 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 167,000.00 | 743 | 3.61 |
    | MSI Radeon RX 9070 VENTUS 3X White | 383,100.00 | 532 | 4.08 |
    | Samsung DDR5 32GB PC5-38400 | 211,800.00 | 669 | 3.97 |


---


### 4. Eliminating SELECT *


Improve queries by specifying only needed columns.


**Hint 1:** Listing only needed columns instead of `SELECT *` reduces disk I/O.



??? success "Answer"
    ```sql
    -- 개선: 필요한 칼럼만
    SELECT order_number, customer_id, total_amount, status, ordered_at
    FROM orders
    WHERE ordered_at LIKE '2024-12%'
    ORDER BY total_amount DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_number | customer_id | total_amount | status | ordered_at |
    |---|---|---|---|---|
    | ORD-20241213-30931 | 1982 | 17,655,465.00 | confirmed | 2024-12-13 07:50:22 |
    | ORD-20241218-31013 | 1910 | 10,836,900.00 | confirmed | 2024-12-18 12:38:50 |
    | ORD-20241207-30840 | 1906 | 5,858,600.00 | confirmed | 2024-12-07 13:56:37 |
    | ORD-20241224-31105 | 1775 | 5,734,000.00 | confirmed | 2024-12-24 22:55:06 |
    | ORD-20241219-31036 | 3516 | 5,414,100.00 | confirmed | 2024-12-19 14:27:47 |
    | ORD-20241219-31034 | 2306 | 5,008,700.00 | confirmed | 2024-12-19 21:12:07 |
    | ORD-20241227-31152 | 3647 | 4,859,300.00 | confirmed | 2024-12-27 21:46:34 |


---


### 5. LIKE Patterns and Indexes


Which of these two queries can use an index?
A) WHERE name LIKE 'Samsung%'
B) WHERE name LIKE '%Samsung%'


**Hint 1:** Indexes use B-Tree structure. Fixed prefix 'Samsung%' allows range search,
but '%Samsung%' cannot determine start position, requiring full scan.



??? success "Answer"
    ```sql
    EXPLAIN QUERY PLAN
    SELECT * FROM products WHERE name LIKE 'Samsung%';
    
    EXPLAIN QUERY PLAN
    SELECT * FROM products WHERE name LIKE '%Samsung%';
    ```


---


### 6. IN vs EXISTS Comparison


Compare execution plans of three methods to find "products with reviews".


**Hint 1:** Compare `IN`, `EXISTS`, `INNER JOIN` with `EXPLAIN QUERY PLAN`.
`EXISTS` returns immediately on first match.



??? success "Answer"
    ```sql
    -- 방법 1: IN
    EXPLAIN QUERY PLAN
    SELECT name, price FROM products
    WHERE id IN (SELECT DISTINCT product_id FROM reviews);
    
    -- 방법 2: EXISTS
    EXPLAIN QUERY PLAN
    SELECT name, price FROM products p
    WHERE EXISTS (SELECT 1 FROM reviews r WHERE r.product_id = p.id);
    
    -- 방법 3: JOIN
    EXPLAIN QUERY PLAN
    SELECT DISTINCT p.name, p.price
    FROM products p
    INNER JOIN reviews r ON p.id = r.product_id;
    ```


---


### 7. Covering Index


Design a covering index for a frequently executed query.


**Hint 1:** Include all columns used in WHERE, ORDER BY, and SELECT in the index.
The query can then return results from the index alone without reading the table.



??? success "Answer"
    ```sql
    -- 현재 실행 계획
    EXPLAIN QUERY PLAN
    SELECT customer_id, status, total_amount
    FROM orders
    WHERE status = 'pending'
    ORDER BY ordered_at DESC;
    
    -- 커버링 인덱스 생성
    CREATE INDEX idx_orders_status_covering
    ON orders(status, ordered_at DESC, customer_id, total_amount);
    
    -- 개선된 실행 계획 확인
    EXPLAIN QUERY PLAN
    SELECT customer_id, status, total_amount
    FROM orders
    WHERE status = 'pending'
    ORDER BY ordered_at DESC;
    ```


---


### 8. Compound Condition Optimization


Improve a query by converting multiple OR conditions to IN.


**Hint 1:** Converting multiple `OR` conditions to `IN (...)` helps the optimizer
use indexes more efficiently.



??? success "Answer"
    ```sql
    -- 개선: IN 사용
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE status IN ('pending', 'paid', 'preparing');
    
    -- 실행 계획 비교
    EXPLAIN QUERY PLAN
    SELECT order_number FROM orders
    WHERE status = 'pending' OR status = 'paid' OR status = 'preparing';
    
    EXPLAIN QUERY PLAN
    SELECT order_number FROM orders
    WHERE status IN ('pending', 'paid', 'preparing');
    ```


---
