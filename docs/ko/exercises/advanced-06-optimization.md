# 인덱스와 실행 계획

23강 인덱스와 실행 계획에서 배운 내용을 실습합니다.
SQLite의 `EXPLAIN QUERY PLAN`을 사용하여 쿼리의 실행 방식을 분석하고, 인덱스를 생성하여 성능을 개선합니다.

!!! warning "실습 환경 안내"
    인덱스 생성(`CREATE INDEX`)은 데이터베이스를 변경합니다.
    실습용 DB 사본에서 자유롭게 실험하세요.

---


### 문제 1. EXPLAIN QUERY PLAN 기초 — SCAN vs SEARCH

다음 두 쿼리의 실행 계획을 확인하고, `SCAN TABLE`과 `SEARCH TABLE`의 차이를 설명하세요.

```sql
-- 쿼리 A
SELECT * FROM orders WHERE customer_id = 100;

-- 쿼리 B
SELECT * FROM orders WHERE notes LIKE '%급히 배송%';
```


??? tip "힌트"
    - `EXPLAIN QUERY PLAN`을 각 쿼리 앞에 붙여 실행
    - `SCAN TABLE` = 전체 행 순차 읽기 (Full Table Scan)
    - `SEARCH TABLE ... USING INDEX` = 인덱스로 필요한 행만 접근

??? success "정답"
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

    | 구분 | 쿼리 A (customer_id) | 쿼리 B (notes LIKE) |
    |---|---|---|
    | 실행 방식 | SEARCH (인덱스) | SCAN (전체 스캔) |
    | 이유 | idx_orders_customer_id 존재 | LIKE '%...' 패턴은 인덱스 사용 불가 |


---


### 문제 2. 기존 인덱스 목록 확인

현재 데이터베이스에 생성된 모든 인덱스를 테이블별로 확인하세요.
테이블명, 인덱스명, 생성 SQL을 표시합니다.


??? tip "힌트"
    - `sqlite_master` 테이블에서 `type = 'index'`인 행을 조회
    - `tbl_name`으로 그룹핑하면 테이블별 인덱스 파악 가능

??? success "정답"
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

    | table_name | index_name | create_sql |
    |---|---|---|
    | complaints | idx_complaints_category | CREATE INDEX idx_complaints_category ON complaints(category) |
    | complaints | idx_complaints_customer_id | CREATE INDEX idx_complaints_customer_id ON complaints(customer_id) |
    | customers | idx_customers_email | CREATE INDEX idx_customers_email ON customers(email) |
    | orders | idx_orders_customer_id | CREATE INDEX idx_orders_customer_id ON orders(customer_id) |
    | orders | idx_orders_customer_status | CREATE INDEX idx_orders_customer_status ON orders(customer_id, status) |
    | ... | ... | ... |


---


### 문제 3. 테이블별 인덱스 개수 요약

각 테이블에 몇 개의 인덱스가 있는지 집계하세요.
인덱스가 0개인 테이블은 제외합니다.


??? tip "힌트"
    - `sqlite_master`에서 `type = 'index'`를 GROUP BY `tbl_name`
    - `sql IS NOT NULL`로 자동 생성 인덱스 제외

??? success "정답"
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


### 문제 4. 단순 인덱스 생성과 효과 확인

`payments` 테이블의 `method` 칼럼에 인덱스를 생성하고, 생성 전후의 실행 계획을 비교하세요.


??? tip "힌트"
    - 먼저 `EXPLAIN QUERY PLAN SELECT ... WHERE method = 'card'`로 현재 상태 확인
    - `CREATE INDEX idx_payments_method ON payments(method)` 실행
    - 같은 EXPLAIN을 다시 실행하여 비교

??? success "정답"
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

    | 단계 | 실행 방식 |
    |---|---|
    | 인덱스 생성 전 | SCAN TABLE payments |
    | 인덱스 생성 후 | SEARCH TABLE payments USING INDEX idx_payments_method |


---


### 문제 5. JOIN 쿼리의 실행 계획 분석

주문과 주문 상세를 JOIN하는 다음 쿼리의 실행 계획을 분석하세요.
어떤 테이블이 먼저 스캔되고, 어떤 인덱스가 사용되는지 확인합니다.

```sql
SELECT o.order_number, p.name, oi.quantity, oi.unit_price
FROM orders AS o
INNER JOIN order_items AS oi ON o.id = oi.order_id
INNER JOIN products AS p ON oi.product_id = p.id
WHERE o.ordered_at LIKE '2024-12%'
  AND o.status = 'delivered';
```


??? tip "힌트"
    - `EXPLAIN QUERY PLAN`을 쿼리 앞에 추가하여 실행
    - SQLite는 각 테이블의 접근 방식을 순서대로 보여줍니다
    - `USING INDEX`가 표시되는 테이블과 그렇지 않은 테이블을 구분

??? success "정답"
    ```sql
    EXPLAIN QUERY PLAN
    SELECT o.order_number, p.name, oi.quantity, oi.unit_price
    FROM orders AS o
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    WHERE o.ordered_at LIKE '2024-12%'
      AND o.status = 'delivered';
    ```

    실행 계획 해석 예시:

    | id | parent | detail |
    |---|---|---|
    | 2 | 0 | SEARCH TABLE orders AS o USING INDEX idx_orders_ordered_at (ordered_at>? AND ordered_at<?) |
    | 3 | 0 | SEARCH TABLE order_items AS oi USING INDEX idx_order_items_order_id (order_id=?) |
    | 4 | 0 | SEARCH TABLE products AS p USING INTEGER PRIMARY KEY (rowid=?) |

    - orders: `idx_orders_ordered_at` 인덱스로 2024-12월 주문을 빠르게 필터
    - order_items: `idx_order_items_order_id`로 해당 주문의 상세 항목 조회
    - products: PK(rowid)로 상품 정보 직접 접근


---


### 문제 6. 커버링 인덱스(Covering Index) 생성

주문 테이블에서 특정 고객의 주문 날짜와 금액만 자주 조회한다고 가정합니다.
커버링 인덱스를 만들어, 테이블 데이터에 접근하지 않고 인덱스만으로 결과를 반환하게 하세요.

```sql
SELECT ordered_at, total_amount
FROM orders
WHERE customer_id = 100;
```


??? tip "힌트"
    - 커버링 인덱스: WHERE 조건 칼럼 + SELECT 칼럼을 모두 포함하는 인덱스
    - `CREATE INDEX idx_xxx ON orders(customer_id, ordered_at, total_amount)`
    - EXPLAIN에서 "COVERING INDEX" 문구가 나타나면 성공

??? success "정답"
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

    | 인덱스 유형 | 동작 |
    |---|---|
    | 일반 인덱스 | 인덱스 → rowid → 테이블 행 접근 (2단계) |
    | 커버링 인덱스 | 인덱스에서 직접 반환 (1단계, 테이블 미접근) |


---


### 문제 7. 부분 인덱스(Partial Index) 생성

활성 상품(`is_active = 1`)만을 대상으로 카테고리별 검색이 빈번하다고 가정합니다.
부분 인덱스를 생성하여 비활성 상품을 인덱스에서 제외하세요.


??? tip "힌트"
    - `CREATE INDEX ... WHERE is_active = 1` 구문으로 부분 인덱스 생성
    - 부분 인덱스는 조건에 맞는 행만 인덱스에 포함 → 인덱스 크기 감소, 성능 향상
    - 쿼리의 WHERE 절에 동일한 조건이 있어야 부분 인덱스를 사용합니다

??? success "정답"
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

    | 쿼리 조건 | 사용 인덱스 |
    |---|---|
    | `category_id = 5 AND is_active = 1` | idx_products_active_category (부분 인덱스) |
    | `category_id = 5` (is_active 조건 없음) | idx_products_category_id (일반 인덱스) |


---


### 문제 8. 복합 인덱스 칼럼 순서의 중요성

`orders` 테이블에 `(status, ordered_at)` 순서와 `(ordered_at, status)` 순서의 복합 인덱스를 각각 생성하고,
다음 두 쿼리에서 어떤 인덱스가 사용되는지 확인하세요.

```sql
-- 쿼리 A: status로 필터, ordered_at으로 범위
SELECT * FROM orders WHERE status = 'delivered' AND ordered_at >= '2024-01-01';

-- 쿼리 B: ordered_at으로 범위만
SELECT * FROM orders WHERE ordered_at >= '2024-01-01';
```


??? tip "힌트"
    - 복합 인덱스의 **첫 번째 칼럼**이 WHERE 절에서 등호 조건으로 사용될 때 가장 효과적
    - `(status, ordered_at)`: status = '...' AND ordered_at >= '...' 에 최적
    - `(ordered_at, status)`: ordered_at만으로도 인덱스 활용 가능 (첫 번째 칼럼이므로)

??? success "정답"
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

    | 쿼리 | 최적 인덱스 | 이유 |
    |---|---|---|
    | status = ? AND ordered_at >= ? | (status, ordered_at) | 등호 조건 칼럼이 선행 |
    | ordered_at >= ? | (ordered_at, status) | 첫 번째 칼럼만으로 범위 검색 |


---


### 문제 9. 인덱스 선택도(Selectivity) 분석

`orders` 테이블의 `status` 칼럼과 `customer_id` 칼럼의 선택도를 비교하세요.
어느 칼럼에 인덱스를 생성하는 것이 더 효과적인지 판단합니다.


??? tip "힌트"
    - 선택도 = 고유 값의 수 / 전체 행 수
    - 선택도가 높을수록(1에 가까울수록) 인덱스 효과가 큼
    - `COUNT(DISTINCT ...)` / `COUNT(*)` 로 계산

??? success "정답"
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

    - `customer_id`의 선택도(0.1)가 `status`(0.00018)보다 훨씬 높음
    - customer_id 인덱스가 더 효과적: 한 고객의 주문만 빠르게 찾을 수 있음
    - status 인덱스는 전체의 약 11%(delivered 등)를 반환 → 인덱스 효과가 낮을 수 있음


---


### 문제 10. 인덱스가 사용되지 않는 경우 파악

다음 쿼리들은 인덱스가 존재해도 사용되지 않을 수 있습니다.
각각의 EXPLAIN 결과를 확인하고, 인덱스가 무시되는 이유를 설명하세요.

```sql
-- 쿼리 A: 함수 적용
SELECT * FROM orders WHERE SUBSTR(ordered_at, 1, 4) = '2024';

-- 쿼리 B: OR 조건
SELECT * FROM orders WHERE customer_id = 100 OR status = 'cancelled';

-- 쿼리 C: 부정 조건
SELECT * FROM orders WHERE customer_id != 100;
```


??? tip "힌트"
    - 칼럼에 함수를 적용하면 인덱스를 사용할 수 없습니다 (SARGable 위반)
    - OR 조건은 각 조건이 별개의 인덱스를 사용해야 하므로 비효율적일 수 있습니다
    - 부정 조건(`!=`, `NOT IN`)은 대부분의 행을 반환하므로 전체 스캔이 효율적

??? success "정답"
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

    | 패턴 | 인덱스 사용 | 이유 |
    |---|---|---|
    | `SUBSTR(col, ...) = ?` | X | 칼럼에 함수 적용 (Non-SARGable) |
    | `col_a = ? OR col_b = ?` | 제한적 | 서로 다른 칼럼의 OR |
    | `col != ?` | X | 대다수 행 반환, 스캔이 효율적 |


---


### 문제 11. 서브쿼리를 JOIN으로 변환하여 성능 개선

다음 상관 서브쿼리를 JOIN으로 변환하고, 두 쿼리의 실행 계획을 비교하세요.

```sql
-- 원본: 상관 서브쿼리 (느림)
SELECT
    p.name,
    p.price,
    (SELECT COUNT(*) FROM order_items AS oi WHERE oi.product_id = p.id) AS order_count,
    (SELECT AVG(r.rating) FROM reviews AS r WHERE r.product_id = p.id) AS avg_rating
FROM products AS p
WHERE p.is_active = 1;
```


??? tip "힌트"
    - 상관 서브쿼리는 외부 쿼리의 각 행마다 실행됩니다
    - `GROUP BY`로 미리 집계한 결과를 `LEFT JOIN`하면 한 번만 실행됩니다
    - 리뷰가 없는 상품도 포함하기 위해 `LEFT JOIN` 사용

??? success "정답"
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
    ```

    ```sql
    -- 실행 계획 비교
    -- 원본 (서브쿼리): SCAN TABLE products + 행마다 CORRELATED SCALAR SUBQUERY 2회
    -- 개선 (JOIN): SCAN TABLE products + SCAN TABLE order_items (1회) + LEFT JOIN reviews (1회)
    ```

    | 방식 | 서브쿼리 실행 횟수 | 예상 성능 |
    |---|---|---|
    | 상관 서브쿼리 | 상품 수 x 2 | 느림 |
    | JOIN (사전 집계) | 1회 | 빠름 |


---


### 문제 12. SARGable 조건으로 쿼리 개선

다음 쿼리들을 SARGable(인덱스 활용 가능) 형태로 변환하세요.

```sql
-- 비효율 A: 연도 추출에 함수 사용
SELECT * FROM orders WHERE strftime('%Y', ordered_at) = '2024';

-- 비효율 B: 계산식 적용
SELECT * FROM products WHERE price * 0.9 > 1000000;

-- 비효율 C: LIKE 선행 와일드카드
SELECT * FROM customers WHERE name LIKE '%김%';
```


??? tip "힌트"
    - 함수/계산을 칼럼이 아닌 **비교 값 쪽**으로 옮기면 인덱스를 사용할 수 있습니다
    - `LIKE '김%'`(접두사 검색)은 인덱스 사용 가능, `LIKE '%김%'`(중간 검색)은 불가
    - 가격 조건은 양변을 수학적으로 변환

??? success "정답"
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

    | 원본 | 개선 | 인덱스 사용 |
    |---|---|---|
    | `strftime('%Y', ordered_at) = '2024'` | `ordered_at >= '2024-01-01' AND ...` | O |
    | `price * 0.9 > 1000000` | `price > 1111111.11` | O |
    | `name LIKE '%김%'` | `name LIKE '김%'` | O (접두사만) |


---


### 문제 13. EXISTS vs IN 성능 비교

리뷰를 작성한 고객 목록을 구할 때, `IN`과 `EXISTS` 두 가지 방식의 실행 계획을 비교하세요.

```sql
-- 방식 A: IN
SELECT * FROM customers WHERE id IN (SELECT DISTINCT customer_id FROM reviews);

-- 방식 B: EXISTS
SELECT * FROM customers AS c
WHERE EXISTS (SELECT 1 FROM reviews AS r WHERE r.customer_id = c.id);
```


??? tip "힌트"
    - `EXPLAIN QUERY PLAN`으로 두 쿼리의 실행 계획을 확인
    - SQLite 옵티마이저는 IN을 EXISTS로 자동 변환하기도 합니다
    - 외부 테이블이 작고 내부 테이블에 인덱스가 있으면 EXISTS가 유리

??? success "정답"
    ```sql
    -- 방식 A: IN
    EXPLAIN QUERY PLAN
    SELECT * FROM customers WHERE id IN (SELECT DISTINCT customer_id FROM reviews);

    -- 방식 B: EXISTS
    EXPLAIN QUERY PLAN
    SELECT * FROM customers AS c
    WHERE EXISTS (SELECT 1 FROM reviews AS r WHERE r.customer_id = c.id);
    ```

    SQLite는 두 방식 모두 유사한 실행 계획을 생성하는 경우가 많습니다:

    | 방식 | 실행 계획 | 비고 |
    |---|---|---|
    | IN (서브쿼리) | SCAN customers + LIST SUBQUERY (reviews) | 서브쿼리 결과를 임시 목록으로 생성 |
    | EXISTS | SCAN customers + CORRELATED (reviews USING INDEX) | 인덱스로 존재 여부만 확인 |

    - reviews에 `idx_reviews_customer_id`가 있으므로, EXISTS가 인덱스를 활용하여 효율적
    - IN은 서브쿼리 전체를 먼저 실행한 뒤 비교하므로, 결과가 클 때 메모리 사용 증가


---


### 문제 14. 불필요한 인덱스 식별

인덱스가 너무 많으면 INSERT/UPDATE 성능이 저하됩니다.
`orders` 테이블의 인덱스 중 중복되거나 불필요한 것이 있는지 분석하세요.


??? tip "힌트"
    - 복합 인덱스 `(customer_id, status)`가 있으면 단일 인덱스 `(customer_id)`는 중복
    - 복합 인덱스의 첫 번째 칼럼만으로도 검색이 가능하기 때문
    - 단, 두 번째 칼럼만으로 검색하는 경우가 많다면 별도 인덱스 필요

??? success "정답"
    ```sql
    -- orders 테이블의 인덱스 목록
    SELECT name, sql
    FROM sqlite_master
    WHERE type = 'index'
      AND tbl_name = 'orders'
      AND sql IS NOT NULL
    ORDER BY name;
    ```

    | index_name | 칼럼 | 분석 |
    |---|---|---|
    | idx_orders_customer_id | (customer_id) | 중복 가능 — idx_orders_customer_status의 첫 번째 칼럼 |
    | idx_orders_customer_status | (customer_id, status) | 유지 — customer_id 단독 검색도 커버 |
    | idx_orders_ordered_at | (ordered_at) | 유지 — 날짜 범위 검색에 필수 |
    | idx_orders_order_number | (order_number) | 유지 — UNIQUE 검색용 |
    | idx_orders_status | (status) | 선택도 낮음 — 제거 검토 가능 |

    **결론**: `idx_orders_customer_id`는 `idx_orders_customer_status`에 포함되므로 제거 후보.
    단, 커버링 인덱스 효과(status 불필요 시 더 작은 인덱스)를 고려하면 유지할 수도 있음.


---


### 문제 15. 종합 — 느린 쿼리 최적화 워크숍

다음 쿼리는 매월 실행되는 카테고리별 매출 리포트입니다.
실행 계획을 분석하고, 인덱스 추가 + 쿼리 구조 개선으로 최적화하세요.

```sql
-- 원본 쿼리 (최적화 전)
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


??? tip "힌트"
    1. `strftime('%Y', ordered_at) = '2024'` → 범위 조건으로 변환 (SARGable)
    2. 암시적 JOIN(쉼표)을 명시적 `INNER JOIN`으로 변환
    3. `EXPLAIN QUERY PLAN`으로 풀 스캔 테이블 파악
    4. 필요시 커버링 인덱스 추가

??? success "정답"
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

    | 개선 항목 | 원본 | 최적화 |
    |---|---|---|
    | 날짜 필터 | `strftime(...)` (Non-SARGable) | 범위 조건 (SARGable) |
    | JOIN 문법 | 암시적 (쉼표) | 명시적 INNER JOIN |
    | 월 추출 | `strftime('%Y-%m', ...)` | `SUBSTR(..., 1, 7)` (더 가벼움) |
    | orders 접근 | SCAN TABLE (풀 스캔) | SEARCH USING INDEX idx_orders_ordered_at |
