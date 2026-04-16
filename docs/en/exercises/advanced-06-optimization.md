# Index and Execution Plan

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `EXPLAIN QUERY PLAN`, `CREATE INDEX`, `Composite Index`, `Covering Index`, `Partial Index`, `SCAN vs SEARCH`, `Index Selectivity`, `SARGable`



### 1. EXPLAIN QUERY PLAN Basics — SCAN vs SEARCH


Check the execution plans of the following two queries, and explain the difference between `SCAN TABLE` and `SEARCH TABLE`.

```sql
-- Query A
SELECT * FROM orders WHERE customer_id = 100;

-- Query B
SELECT * FROM orders WHERE notes LIKE '%urgent delivery%';
```


**Hint 1:** - Execute by adding `EXPLAIN QUERY PLAN` in front of each query.
- `SCAN TABLE` = Read entire rows sequentially (Full Table Scan)
- `SEARCH TABLE ... USING INDEX` = Access only required rows by index



??? success "Answer"
    ```sql
    -- 쿼리 A: 인덱스가 있는 customer_id로 검색
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 100;
    -- 결과: SEARCH TABLE orders USING INDEX idx_orders_customer_id (customer_id=?)
    
    -- 쿼리 B: 인덱스가 없는 notes로 LIKE 검색
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE notes LIKE '%급히 배송%';
    -- 결과: SCAN TABLE orders
    ```


---


### 2. Check the existing index list


Check all indexes created in the current database by table.
Displays table name, index name, and creation SQL.


**Hint 1:** - Search for row `type = 'index'` in `sqlite_master` table.
- By grouping with `tbl_name`, you can identify indexes for each table.



??? success "Answer"
    ```sql
    SELECT
        tbl_name  AS table_name,
        name      AS index_name,
        sql       AS create_sql
    FROM sqlite_master
    WHERE type = 'index'
      AND sql IS NOT NULL  -- 자동 생성 인덱스(PK 등) 제외
    ORDER BY tbl_name, name;
    ```


    **Result** (top 7 of 61 rows)

    | table_name | index_name | create_sql |
    |---|---|---|
    | calendar | idx_calendar_year_month | CREATE INDEX idx_calendar_year_month ... |
    | cart_items | idx_cart_items_cart_id | CREATE INDEX idx_cart_items_cart_id O... |
    | carts | idx_carts_customer_id | CREATE INDEX idx_carts_customer_id ON... |
    | complaints | idx_complaints_category | CREATE INDEX idx_complaints_category ... |
    | complaints | idx_complaints_customer_id | CREATE INDEX idx_complaints_customer_... |
    | complaints | idx_complaints_order_id | CREATE INDEX idx_complaints_order_id ... |
    | complaints | idx_complaints_staff_id | CREATE INDEX idx_complaints_staff_id ... |


---


### 3. Summary of index count for each table


Count how many indexes each table has.
Exclude tables with an index of 0.


**Hint 1:** - GROUP BY `tbl_name` `type = 'index'` IN `sqlite_master`
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


    **Result** (top 7 of 26 rows)

    | table_name | index_count |
    |---|---|
    | returns | 6 |
    | complaints | 6 |
    | products | 5 |
    | orders | 5 |
    | product_views | 4 |
    | point_transactions | 4 |
    | reviews | 3 |


---


### 4. Create a simple index and check the effect


Create an index on the `method` column of the `payments` table, and compare the execution plan before and after creation.


**Hint 1:** - First check the current status with `EXPLAIN QUERY PLAN SELECT ... WHERE method = 'card'`
-Run `CREATE INDEX idx_payments_method ON payments(method)`
- Compare by running the same EXPLAIN again



??? success "Answer"
    ```sql
    -- 1) 인덱스 생성 전 실행 계획
    EXPLAIN QUERY PLAN
    SELECT * FROM payments WHERE method = 'card';
    -- 결과: SCAN TABLE payments
    
    -- 2) 인덱스 생성
    CREATE INDEX idx_payments_method ON payments(method);
    
    -- 3) 인덱스 생성 후 실행 계획
    EXPLAIN QUERY PLAN
    SELECT * FROM payments WHERE method = 'card';
    -- 결과: SEARCH TABLE payments USING INDEX idx_payments_method (method=?)
    ```


---


### 5. Analysis of execution plan of JOIN query


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


**Hint 1:** - Execute by adding `EXPLAIN QUERY PLAN` in front of the query
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


    **Result** (3 rows)

    | id | parent | notused | detail |
    |---|---|---|---|
    | 6 | 0 | 61 | SEARCH o USING INDEX idx_orders_statu... |
    | 14 | 0 | 61 | SEARCH oi USING INDEX idx_order_items... |
    | 19 | 0 | 45 | SEARCH p USING INTEGER PRIMARY KEY (r... |


---


### 6. Creating a Covering Index


Suppose you frequently look up only the order date and amount for a specific customer in your orders table.
Create a covering index to return results using only the index without accessing the table data.

```sql
SELECT ordered_at, total_amount
FROM orders
WHERE customer_id = 100;
```


**Hint 1:** - Covering index: Index that includes both WHERE condition column + SELECT column
- `CREATE INDEX idx_xxx ON orders(customer_id, ordered_at, total_amount)`
- Success is achieved when the phrase “COVERING INDEX” appears in EXPLAIN.



??? success "Answer"
    ```sql
    -- 커버링 인덱스 생성
    CREATE INDEX idx_orders_cust_date_amount
        ON orders(customer_id, ordered_at, total_amount);
    
    -- 실행 계획 확인
    EXPLAIN QUERY PLAN
    SELECT ordered_at, total_amount
    FROM orders
    WHERE customer_id = 100;
    -- 결과: SEARCH TABLE orders USING COVERING INDEX idx_orders_cust_date_amount (customer_id=?)
    ```


---


### 7. Creating a partial index


Assume frequent category searches targeting only the active product (`is_active = 1`).
Create a partial index to exclude inactive products from the index.


**Hint 1:** - Create partial index with `CREATE INDEX ... WHERE is_active = 1` syntax
- Partial index includes only rows that meet the conditions in the index → ​​Reduces index size and improves performance
- Use partial indexes only if the same conditions exist in the WHERE clause of the query



??? success "Answer"
    ```sql
    -- 부분 인덱스 생성
    CREATE INDEX idx_products_active_category
        ON products(category_id)
        WHERE is_active = 1;
    
    -- 부분 인덱스를 사용하는 쿼리
    EXPLAIN QUERY PLAN
    SELECT name, price
    FROM products
    WHERE category_id = 5
      AND is_active = 1;
    -- 결과: SEARCH TABLE products USING INDEX idx_products_active_category (category_id=?)
    
    -- 조건이 없으면 부분 인덱스 미사용
    EXPLAIN QUERY PLAN
    SELECT name, price
    FROM products
    WHERE category_id = 5;
    -- 결과: SEARCH TABLE products USING INDEX idx_products_category_id (category_id=?)
    ```


---


### 8. Importance of composite index column order


Create composite indexes in the `(status, ordered_at)` order and `(ordered_at, status)` order on the `orders` table, respectively.
Check which index is used in the following two queries:

```sql
-- Query A: filter by status, range on ordered_at
SELECT * FROM orders WHERE status = 'delivered' AND ordered_at >= '2024-01-01';

-- Query B: range on ordered_at only
SELECT * FROM orders WHERE ordered_at >= '2024-01-01';
```


**Hint 1:** - Most effective when the **first column** of a composite index is used as an equals condition in the WHERE clause
- `(status, ordered_at)`: optimal for status = '...' AND ordered_at >= '...'
- `(ordered_at, status)`: Index can be used only with ordered_at (since it is the first column)



??? success "Answer"
    ```sql
    -- 인덱스 생성
    CREATE INDEX idx_orders_status_date ON orders(status, ordered_at);
    CREATE INDEX idx_orders_date_status ON orders(ordered_at, status);
    
    -- 쿼리 A: status 등호 + ordered_at 범위
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE status = 'delivered' AND ordered_at >= '2024-01-01';
    -- SQLite 옵티마이저가 idx_orders_status_date를 선택 (status 등호 후 ordered_at 범위 스캔)
    
    -- 쿼리 B: ordered_at 범위만
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE ordered_at >= '2024-01-01';
    -- idx_orders_date_status 또는 idx_orders_ordered_at 사용 (첫 번째 칼럼이 ordered_at)
    ```


---


### 9. Index selectivity analysis


Compare the selectivity of the `status` and `customer_id` columns in the `orders` table.
Determine which column it is more effective to create an index on.


**Hint 1:** - Selectivity = number of unique values ​​/ total number of rows
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


    **Result** (1 rows)

    | total_rows | distinct_status | distinct_customer_id | selectivity_status | selectivity_customer |
    |---|---|---|---|---|
    | 37,557 | 9 | 2839 | 0.00024 | 0.075592 |


---


### 10. Determine when an index is not used


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


**Hint 1:** - If you apply a function to a column, you cannot use the index (SARGable violation)
- OR conditions can be inefficient because each condition must use a separate index.
- Negative conditions (`!=`, `NOT IN`) return most rows, so a full scan is efficient.



??? success "Answer"
    ```sql
    -- 쿼리 A: 함수 적용 → 인덱스 미사용
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE SUBSTR(ordered_at, 1, 4) = '2024';
    -- 결과: SCAN TABLE orders
    -- 이유: SUBSTR() 함수가 칼럼에 적용되어 인덱스 활용 불가
    
    -- SARGable 대안:
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01';
    -- 결과: SEARCH TABLE orders USING INDEX idx_orders_ordered_at
    
    -- 쿼리 B: OR 조건
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 100 OR status = 'cancelled';
    -- 결과: SCAN TABLE orders (또는 MULTI-INDEX OR)
    -- 이유: 두 조건이 별개 인덱스 → 옵티마이저가 전체 스캔 선택 가능
    
    -- 쿼리 C: 부정 조건
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id != 100;
    -- 결과: SCAN TABLE orders
    -- 이유: 거의 모든 행을 반환 → 전체 스캔이 더 효율적
    ```


---


### 11. Improve performance by converting subqueries to JOINs


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


**Hint 1:** - Correlated subqueries are executed for each row in the outer query.
- If you use `LEFT JOIN`, the results pre-aggregated with `GROUP BY` will be executed only once.
- Use `LEFT JOIN` to include products without reviews



??? success "Answer"
    ```sql
    -- 개선: JOIN으로 변환
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
    
    -- 실행 계획 비교
    -- 원본 (서브쿼리): SCAN TABLE products + 행마다 CORRELATED SCALAR SUBQUERY 2회
    -- 개선 (JOIN): SCAN TABLE products + SCAN TABLE order_items (1회) + LEFT JOIN reviews (1회)
    ```


    **Result** (top 7 of 20 rows)

    | name | price | order_count | avg_rating |
    |---|---|---|---|
    | Crucial T700 2TB Silver | 257,000.00 | 113,344 | 4.21 |
    | Logitech G502 X PLUS | 97,500.00 | 98,879 | 4.18 |
    | SteelSeries Aerox 5 Wireless Silver | 100,000.00 | 97,400 | 3.88 |
    | SteelSeries Prime Wireless Silver | 95,900.00 | 96,495 | 3.88 |
    | Kingston FURY Beast DDR4 16GB Silver | 48,000.00 | 93,738 | 3.75 |
    | AMD Ryzen 9 9900X | 335,700.00 | 90,740 | 3.86 |
    | SteelSeries Prime Wireless Black | 89,800.00 | 78,480 | 3.88 |


---


### 12. Improving queries with SARGable conditions


Convert the following queries to SARGable (indexable) format.

```sql
-- Inefficient A: function used for year extraction
SELECT * FROM orders WHERE strftime('%Y', ordered_at) = '2024';

-- Inefficient B: calculation applied
SELECT * FROM products WHERE price * 0.9 > 1000000;

-- Inefficient C: LIKE with leading wildcard
SELECT * FROM customers WHERE name LIKE '%Kim%';
```


**Hint 1:** - You can use an index by moving the function/calculation to the **comparison value** side rather than the column.
- `LIKE 'Kim%'` (prefix search) can use indexes, `LIKE '%Kim%'` (intermediate search) cannot.
- Price terms are mathematically converted to both sides.



??? success "Answer"
    ```sql
    -- 개선 A: 범위 조건으로 변환
    SELECT * FROM orders
    WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01';
    -- idx_orders_ordered_at 인덱스 사용 가능
    
    -- 개선 B: 계산을 비교 값 쪽으로 이동
    SELECT * FROM products
    WHERE price > 1000000 / 0.9;  -- price > 1111111.11
    -- idx_products_xxx 인덱스 사용 가능
    
    -- 개선 C: 접두사 검색으로 변경 (가능한 경우)
    SELECT * FROM customers
    WHERE name LIKE '김%';  -- '김'으로 시작하는 고객
    -- idx_customers_name 인덱스 사용 가능 (접두사 LIKE)
    
    -- 중간 검색이 반드시 필요하면 → FTS(전문 검색)나 별도 검색 칼럼 고려
    ```


---


### 13. EXISTS vs IN performance comparison


When obtaining a list of customers who have written reviews, compare the two execution plans: `IN` and `EXISTS`.

```sql
-- Method A: IN
SELECT * FROM customers WHERE id IN (SELECT DISTINCT customer_id FROM reviews);

-- Method B: EXISTS
SELECT * FROM customers AS c
WHERE EXISTS (SELECT 1 FROM reviews AS r WHERE r.customer_id = c.id);
```


**Hint 1:** - Check the execution plan of both queries with `EXPLAIN QUERY PLAN`
- The SQLite optimizer also automatically converts IN to EXISTS.
- EXISTS is advantageous when the outer table is small and the inner table has an index.



??? success "Answer"
    ```sql
    -- 방식 A: IN
    EXPLAIN QUERY PLAN
    SELECT * FROM customers WHERE id IN (SELECT DISTINCT customer_id FROM reviews);
    
    -- 방식 B: EXISTS
    EXPLAIN QUERY PLAN
    SELECT * FROM customers AS c
    WHERE EXISTS (SELECT 1 FROM reviews AS r WHERE r.customer_id = c.id);
    ```


---


### 14. Identifying unnecessary indexes


Too many indexes will result in poor INSERT/UPDATE performance.
Analyze whether any of the indexes in the `orders` table are redundant or unnecessary.


**Hint 1:** - If there is a composite index `(customer_id, status)`, the single index `(customer_id)` is redundant.
- Search is possible using only the first column of the composite index.
- However, if you often search using only the second column, a separate index is required.



??? success "Answer"
    ```sql
    -- orders 테이블의 인덱스 목록
    SELECT name, sql
    FROM sqlite_master
    WHERE type = 'index'
      AND tbl_name = 'orders'
      AND sql IS NOT NULL
    ORDER BY name;
    ```


    **Result** (5 rows)

    | name | sql |
    |---|---|
    | idx_orders_customer_id | CREATE INDEX idx_orders_customer_id O... |
    | idx_orders_customer_status | CREATE INDEX idx_orders_customer_stat... |
    | idx_orders_order_number | CREATE INDEX idx_orders_order_number ... |
    | idx_orders_ordered_at | CREATE INDEX idx_orders_ordered_at ON... |
    | idx_orders_status | CREATE INDEX idx_orders_status ON ord... |


---


### 15. Summary — Slow Query Optimization Workshop


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


**Hint 1:** 1. `strftime('%Y', ordered_at) = '2024'` → Convert to range condition (SARGable)
2. Convert implicit JOIN (comma) to explicit `INNER JOIN`
3. Identify full scan table with `EXPLAIN QUERY PLAN`
4. Add covering index if necessary



??? success "Answer"
    ```sql
    -- 1) 실행 계획 확인 (원본)
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
    -- 문제점: strftime() 함수로 인해 orders 테이블 풀 스캔
    
    -- 2) 최적화된 쿼리
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
    
    -- 3) 최적화 후 실행 계획 확인
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


---
