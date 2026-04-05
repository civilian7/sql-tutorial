# 고급 연습: 쿼리 최적화

EXPLAIN으로 실행 계획을 분석하고, 인덱스와 쿼리 구조를 개선하는 8문제입니다.

---

### 1. EXPLAIN 읽기

아래 쿼리의 실행 계획을 확인하세요. `SCAN TABLE`과 `SEARCH TABLE`의 차이는 무엇인가요?

```sql
EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE customer_id = 100;
```

**힌트:** `SCAN TABLE`은 전체 테이블을 읽고, `SEARCH TABLE ... USING INDEX`는 인덱스로 필요한 행만 찾습니다.

??? success "정답"
    ```sql
    -- 먼저 실행 계획 확인
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 100;

    -- 인덱스 확인
    SELECT name, sql FROM sqlite_master
    WHERE type = 'index' AND tbl_name = 'orders';
    ```

    **해석:**

    - `SCAN TABLE orders` → 전체 테이블 스캔 (인덱스 없음, 느림)
    - `SEARCH TABLE orders USING INDEX idx_orders_customer_id` → 인덱스 사용 (빠름)

    `customer_id`에 인덱스가 있으면 SEARCH, 없으면 SCAN이 표시됩니다.

---

### 2. 인덱스 효과 비교

인덱스 유무에 따른 실행 계획 차이를 확인하세요.

**힌트:** 인덱스가 있는 컬럼(`customer_id`)과 없는 컬럼(`notes`)에 대해 각각 `EXPLAIN QUERY PLAN`을 실행하여 비교하세요.

??? success "정답"
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

    **핵심:** WHERE 조건에 자주 사용하는 컬럼에 인덱스가 있으면 SEARCH(인덱스 탐색), 없으면 SCAN(전체 스캔)입니다.

---

### 3. 서브쿼리 → JOIN 변환

상관 서브쿼리를 JOIN으로 바꿔 성능을 개선하세요.

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

**힌트:** 상관 서브쿼리는 행마다 실행됩니다. 미리 `GROUP BY`로 집계한 서브쿼리를 `LEFT JOIN`하면 한 번만 실행됩니다.

??? success "정답"
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

### 4. SELECT * 제거

필요한 컬럼만 명시하여 쿼리를 개선하세요.

```sql
-- 느린 쿼리
SELECT * FROM orders
WHERE ordered_at LIKE '2024-12%'
ORDER BY total_amount DESC
LIMIT 10;
```

**힌트:** `SELECT *` 대신 실제 필요한 컬럼(`order_number`, `total_amount` 등)만 나열하면 디스크 I/O가 줄어듭니다.

??? success "정답"
    ```sql
    -- 개선: 필요한 컬럼만
    SELECT order_number, customer_id, total_amount, status, ordered_at
    FROM orders
    WHERE ordered_at LIKE '2024-12%'
    ORDER BY total_amount DESC
    LIMIT 10;
    ```

    **이유:** `SELECT *`는 모든 컬럼(notes 등 긴 TEXT 포함)을 읽습니다. 필요한 컬럼만 지정하면 디스크 I/O가 줄어듭니다.

---

### 5. LIKE 패턴과 인덱스

아래 두 쿼리 중 어느 것이 인덱스를 활용할 수 있나요?

```sql
-- 쿼리 A
SELECT * FROM products WHERE name LIKE 'Samsung%';

-- 쿼리 B
SELECT * FROM products WHERE name LIKE '%Samsung%';
```

**힌트:** 인덱스는 B-Tree 구조입니다. 접두사가 고정된 `'Samsung%'`은 범위 검색이 가능하지만, `'%Samsung%'`은 시작을 알 수 없어 전체 스캔합니다.

??? success "정답"
    ```sql
    EXPLAIN QUERY PLAN
    SELECT * FROM products WHERE name LIKE 'Samsung%';

    EXPLAIN QUERY PLAN
    SELECT * FROM products WHERE name LIKE '%Samsung%';
    ```

    **답:** 쿼리 A(`'Samsung%'`)만 인덱스를 활용할 수 있습니다. 앞에 `%`가 오면(`'%Samsung%'`) 인덱스를 사용할 수 없어 전체 스캔합니다.

---

### 6. IN vs EXISTS 비교

"리뷰가 있는 상품"을 찾는 두 가지 방법의 실행 계획을 비교하세요.

**힌트:** `IN`, `EXISTS`, `INNER JOIN` 세 가지 방법을 `EXPLAIN QUERY PLAN`으로 비교하세요. `EXISTS`는 첫 매치에서 즉시 반환합니다.

??? success "정답"
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

    **핵심:** 대부분의 경우 EXISTS가 IN보다 효율적입니다. reviews에 `product_id` 인덱스가 있으면 EXISTS는 첫 매치에서 바로 반환합니다.

---

### 7. 커버링 인덱스

자주 실행되는 쿼리에 대해 커버링 인덱스를 설계하세요.

```sql
-- 이 쿼리가 매우 자주 실행됩니다
SELECT customer_id, status, total_amount
FROM orders
WHERE status = 'pending'
ORDER BY ordered_at DESC;
```

**힌트:** WHERE, ORDER BY, SELECT에 사용된 모든 컬럼을 인덱스에 포함하면 테이블을 읽지 않고 인덱스만으로 결과를 반환합니다.

??? success "정답"
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

    **커버링 인덱스:** 쿼리에 필요한 모든 컬럼이 인덱스에 포함되면, 테이블을 읽지 않고 인덱스만으로 결과를 반환합니다.

---

### 8. 복합 조건 최적화

아래 쿼리를 더 효율적으로 바꾸세요.

```sql
-- 비효율적: OR은 인덱스를 잘 활용하지 못함
SELECT order_number, total_amount, ordered_at
FROM orders
WHERE status = 'pending' OR status = 'paid' OR status = 'preparing';
```

**힌트:** 여러 `OR` 조건을 `IN (...)` 으로 바꾸면 옵티마이저가 인덱스를 더 효율적으로 활용할 수 있습니다.

??? success "정답"
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
