# Advanced Exercise: Query Optimization

8 problems on analyzing execution plans with EXPLAIN and improving indexes and query structure.

---

### 1. Reading EXPLAIN

Check the execution plan of the query below. What is the difference between `SCAN TABLE` and `SEARCH TABLE`?

```sql
EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE customer_id = 100;
```

**Hint:** `SCAN TABLE` reads the entire table, while `SEARCH TABLE ... USING INDEX` uses an index to find only the needed rows.

??? success "Answer"
    ```sql
    -- 먼저 실행 계획 확인
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 100;

    -- 인덱스 확인
    SELECT name, sql FROM sqlite_master
    WHERE type = 'index' AND tbl_name = 'orders';
    ```

    **Interpretation:**

    - `SCAN TABLE orders` -- Full table scan (no index, slow)
    - `SEARCH TABLE orders USING INDEX idx_orders_customer_id` -- Index used (fast)

    If there is an index on `customer_id`, SEARCH is shown; otherwise, SCAN is shown.

---

### 2. Comparing Index Effect

Compare execution plans with and without an index.

**Hint:** Run `EXPLAIN QUERY PLAN` on a column with an index (`customer_id`) and one without (`notes`) to compare.

??? success "Answer"
    ```sql
    -- 1) 인덱스가 있는 컬럼으로 검색
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 100;

    -- 2) 인덱스가 없는 컬럼으로 검색
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE notes LIKE '%배송%';

    -- 3) 현재 인덱스 목록
    SELECT name, tbl_name, sql
    FROM sqlite_master
    WHERE type = 'index'
    ORDER BY tbl_name;
    ```

    **Key point:** If there is an index on a column frequently used in WHERE conditions, the result is SEARCH (index seek); otherwise, it is SCAN (full scan).

---

### 3. Subquery to JOIN Conversion

Convert a correlated subquery to a JOIN for better performance.

```sql
-- 느린 쿼리: 상관 서브쿼리 (행마다 서브쿼리 실행)
SELECT
    p.name,
    p.price,
    (SELECT COUNT(*) FROM order_items oi WHERE oi.product_id = p.id) AS order_count,
    (SELECT ROUND(AVG(r.rating), 2) FROM reviews r WHERE r.product_id = p.id) AS avg_rating
FROM products p
WHERE p.is_active = 1;
```

**Hint:** Correlated subqueries execute once per row. Pre-aggregate with `GROUP BY` in a subquery and `LEFT JOIN` it instead -- this runs only once.

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

    ```sql
    -- 두 쿼리의 실행 계획 비교
    EXPLAIN QUERY PLAN
    SELECT p.name, (SELECT COUNT(*) FROM order_items oi WHERE oi.product_id = p.id)
    FROM products p;

    EXPLAIN QUERY PLAN
    SELECT p.name, COALESCE(s.cnt, 0)
    FROM products p
    LEFT JOIN (SELECT product_id, COUNT(*) AS cnt FROM order_items GROUP BY product_id) s
    ON p.id = s.product_id;
    ```

---

### 4. Removing SELECT *

Improve the query by specifying only the necessary columns.

**Hint:** Instead of `SELECT *`, list only the columns you actually need (`order_number`, `total_amount`, etc.) to reduce disk I/O.

```sql
-- 느린 쿼리
SELECT * FROM orders
WHERE ordered_at LIKE '2024-12%'
ORDER BY total_amount DESC
LIMIT 10;
```

??? success "Answer"
    ```sql
    -- 개선: 필요한 컬럼만
    SELECT order_number, customer_id, total_amount, status, ordered_at
    FROM orders
    WHERE ordered_at LIKE '2024-12%'
    ORDER BY total_amount DESC
    LIMIT 10;
    ```

    **Reason:** `SELECT *` reads all columns (including long TEXT fields like notes). Specifying only the needed columns reduces disk I/O.

---

### 5. LIKE Patterns and Indexes

Which of the two queries below can utilize an index?

```sql
-- 쿼리 A
SELECT * FROM products WHERE name LIKE 'Samsung%';

-- 쿼리 B
SELECT * FROM products WHERE name LIKE '%Samsung%';
```

**Hint:** Indexes use a B-Tree structure. `'Samsung%'` with a fixed prefix allows a range search, but `'%Samsung%'` with an unknown start requires a full scan.

??? success "Answer"
    ```sql
    EXPLAIN QUERY PLAN
    SELECT * FROM products WHERE name LIKE 'Samsung%';

    EXPLAIN QUERY PLAN
    SELECT * FROM products WHERE name LIKE '%Samsung%';
    ```

    **Answer:** Only Query A (`'Samsung%'`) can utilize an index. When `%` is at the beginning (`'%Samsung%'`), the index cannot be used and a full scan is performed.

---

### 6. IN vs EXISTS Comparison

Compare the execution plans of two approaches for finding "products that have reviews."

**Hint:** Compare `IN`, `EXISTS`, and `INNER JOIN` using `EXPLAIN QUERY PLAN`. `EXISTS` returns immediately upon finding the first match.

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

    **Key point:** In most cases, EXISTS is more efficient than IN. If there is an index on `product_id` in reviews, EXISTS returns immediately upon finding the first match.

---

### 7. Covering Index

Design a covering index for a frequently executed query.

**Hint:** If all columns used in WHERE, ORDER BY, and SELECT are included in the index, results can be returned from the index alone without reading the table.

```sql
-- 이 쿼리가 매우 자주 실행됩니다
SELECT customer_id, status, total_amount
FROM orders
WHERE status = 'pending'
ORDER BY ordered_at DESC;
```

??? success "Answer"
    ```sql
    -- 현재 실행 계획
    EXPLAIN QUERY PLAN
    SELECT customer_id, status, total_amount
    FROM orders
    WHERE status = 'pending'
    ORDER BY ordered_at DESC;

    -- 커버링 인덱스 생성 (쿼리에 필요한 모든 컬럼 포함)
    CREATE INDEX idx_orders_status_covering
    ON orders(status, ordered_at DESC, customer_id, total_amount);

    -- 개선된 실행 계획 확인
    EXPLAIN QUERY PLAN
    SELECT customer_id, status, total_amount
    FROM orders
    WHERE status = 'pending'
    ORDER BY ordered_at DESC;
    ```

    **Covering index:** When all columns needed by the query are included in the index, the result can be returned from the index alone without reading the table.

---

### 8. Compound Condition Optimization

Rewrite the query below more efficiently.

**Hint:** Replacing multiple `OR` conditions with `IN (...)` allows the optimizer to utilize indexes more efficiently.

```sql
-- 비효율적: OR은 인덱스를 잘 활용하지 못함
SELECT order_number, total_amount, ordered_at
FROM orders
WHERE status = 'pending' OR status = 'paid' OR status = 'preparing';
```

??? success "Answer"
    ```sql
    -- 개선: IN 사용 (옵티마이저가 인덱스 활용 가능)
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE status IN ('pending', 'paid', 'preparing');
    ```

    ```sql
    -- 실행 계획 비교
    EXPLAIN QUERY PLAN
    SELECT order_number FROM orders
    WHERE status = 'pending' OR status = 'paid' OR status = 'preparing';

    EXPLAIN QUERY PLAN
    SELECT order_number FROM orders
    WHERE status IN ('pending', 'paid', 'preparing');
    ```
