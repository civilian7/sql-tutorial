# DML 실습 (INSERT, UPDATE, DELETE)

!!! warning "주의사항"
    DML 문은 데이터를 변경합니다. 이 연습에서는 **임시 테이블**을 만들어 실습하고, 끝나면 삭제합니다.
    원본 테이블을 직접 수정하지 마세요.


## 기초 (1-7): INSERT, UPDATE, DELETE 기본

### 문제 1. 연습용 상품 테이블을 만들고, 상품 1건을 삽입하세요.

먼저 `temp_products` 테이블을 생성하고, INSERT 문으로 데이터를 추가합니다.

??? tip "힌트"
    `CREATE TABLE temp_products AS SELECT * FROM products WHERE 1=0` — 구조만 복사하는 빈 테이블을 만듭니다. 그 다음 `INSERT INTO ... VALUES (...)`.

??? success "정답"
    ```sql
    -- 1단계: 구조만 복사한 빈 테이블 생성
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;

    -- 2단계: 상품 1건 삽입
    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (9001, 1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01');

    -- 확인
    SELECT * FROM temp_products;

    -- 정리
    DROP TABLE temp_products;
    ```


---


### 문제 2. 연습용 상품 테이블에 여러 건을 한 번에 삽입하세요.

VALUES 절에 여러 행을 쉼표로 구분하여 한 번의 INSERT로 다수 행을 추가합니다.

??? tip "힌트"
    `INSERT INTO ... VALUES (...), (...), (...)` — SQLite는 한 INSERT 문에 여러 VALUES 행을 지원합니다.

??? success "정답"
    ```sql
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;

    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES
        (9001, 1, 1, '테스트 마우스', 'TEST-MS-001', 'TestBrand', 35000, 18000, 200, 1, '2025-01-01', '2025-01-01'),
        (9002, 1, 1, '테스트 패드', 'TEST-PD-001', 'TestBrand', 15000, 7000, 500, 1, '2025-01-01', '2025-01-01'),
        (9003, 2, 1, '테스트 모니터', 'TEST-MN-001', 'TestBrand', 350000, 200000, 50, 1, '2025-01-01', '2025-01-01');

    -- 확인
    SELECT id, name, price FROM temp_products;

    DROP TABLE temp_products;
    ```

    | id | name | price |
    |----|------|-------|
    | 9001 | 테스트 마우스 | 35000 |
    | 9002 | 테스트 패드 | 15000 |
    | 9003 | 테스트 모니터 | 350000 |


---


### 문제 3. 연습용 테이블에서 특정 상품의 가격을 수정하세요.

UPDATE + WHERE 조건으로 특정 행만 수정합니다. WHERE 없이 UPDATE하면 전체 행이 변경되므로 주의하세요.

??? tip "힌트"
    `UPDATE temp_products SET price = ... WHERE id = ...` — WHERE 절을 반드시 포함하세요.

??? success "정답"
    ```sql
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;

    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES
        (9001, 1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01'),
        (9002, 1, 1, '테스트 마우스', 'TEST-MS-001', 'TestBrand', 35000, 18000, 200, 1, '2025-01-01', '2025-01-01');

    -- 가격 수정
    UPDATE temp_products
    SET price = 79000, updated_at = '2025-06-01'
    WHERE id = 9001;

    -- 확인
    SELECT id, name, price, updated_at FROM temp_products;

    DROP TABLE temp_products;
    ```


---


### 문제 4. 연습용 테이블에서 특정 상품을 삭제하세요.

DELETE + WHERE 조건으로 특정 행만 삭제합니다.

??? tip "힌트"
    `DELETE FROM temp_products WHERE id = ...` — WHERE 절 없이 실행하면 전체 데이터가 삭제되므로 반드시 조건을 지정하세요.

??? success "정답"
    ```sql
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;

    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES
        (9001, 1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01'),
        (9002, 1, 1, '테스트 마우스', 'TEST-MS-001', 'TestBrand', 35000, 18000, 200, 1, '2025-01-01', '2025-01-01'),
        (9003, 1, 1, '테스트 패드', 'TEST-PD-001', 'TestBrand', 15000, 7000, 500, 1, '2025-01-01', '2025-01-01');

    -- 삭제
    DELETE FROM temp_products WHERE id = 9002;

    -- 확인 (2건만 남음)
    SELECT id, name FROM temp_products;

    DROP TABLE temp_products;
    ```


---


### 문제 5. 연습용 고객 테이블을 만들고, 등급이 'BRONZE'인 고객의 등급을 'SILVER'로 일괄 변경하세요.

WHERE 조건으로 여러 행을 한 번에 UPDATE합니다.

??? tip "힌트"
    `UPDATE temp_customers SET grade = 'SILVER' WHERE grade = 'BRONZE'` — 조건에 맞는 모든 행이 변경됩니다.

??? success "정답"
    ```sql
    -- 기존 데이터 일부를 복사하여 연습 테이블 생성
    CREATE TABLE temp_customers AS
    SELECT id, name, email, grade, point_balance
    FROM customers
    LIMIT 50;

    -- 변경 전 확인
    SELECT grade, COUNT(*) AS cnt FROM temp_customers GROUP BY grade;

    -- BRONZE → SILVER 일괄 변경
    UPDATE temp_customers
    SET grade = 'SILVER'
    WHERE grade = 'BRONZE';

    -- 변경 후 확인
    SELECT grade, COUNT(*) AS cnt FROM temp_customers GROUP BY grade;

    DROP TABLE temp_customers;
    ```


---


### 문제 6. 연습용 테이블에서 포인트가 0인 고객을 모두 삭제하세요. 삭제 전/후 건수를 비교하세요.

DELETE + WHERE로 조건부 삭제 후 건수를 확인합니다.

??? tip "힌트"
    삭제 전 `SELECT COUNT(*)`, DELETE 실행, 삭제 후 `SELECT COUNT(*)` 순서로 실행하세요.

??? success "정답"
    ```sql
    CREATE TABLE temp_customers AS
    SELECT id, name, email, grade, point_balance
    FROM customers
    LIMIT 100;

    -- 삭제 전 건수
    SELECT COUNT(*) AS before_count FROM temp_customers;

    -- 포인트 0인 고객 삭제
    DELETE FROM temp_customers WHERE point_balance = 0;

    -- 삭제 후 건수
    SELECT COUNT(*) AS after_count FROM temp_customers;

    DROP TABLE temp_customers;
    ```


---


### 문제 7. 연습용 상품 테이블에서 전체 상품의 가격을 10% 인상하세요.

WHERE 없이 UPDATE하면 전체 행에 적용됩니다. 의도적인 전체 수정입니다.

??? tip "힌트"
    `UPDATE temp_products SET price = ROUND(price * 1.1, 2)` — 소수점은 ROUND로 정리합니다.

??? success "정답"
    ```sql
    CREATE TABLE temp_products AS
    SELECT id, name, price
    FROM products
    WHERE is_active = 1
    LIMIT 20;

    -- 인상 전
    SELECT name, price FROM temp_products ORDER BY price DESC LIMIT 5;

    -- 전체 10% 인상
    UPDATE temp_products
    SET price = ROUND(price * 1.1, 2);

    -- 인상 후
    SELECT name, price FROM temp_products ORDER BY price DESC LIMIT 5;

    DROP TABLE temp_products;
    ```


---


## 응용 (8-14): UPSERT, 조건부 UPDATE, INSERT...SELECT

### 문제 8. INSERT OR REPLACE (UPSERT)로 상품을 삽입하되, 이미 존재하면 가격만 갱신하세요.

SQLite의 `INSERT OR REPLACE`는 UNIQUE 제약 위반 시 기존 행을 삭제하고 새 행을 삽입합니다.

??? tip "힌트"
    테이블에 UNIQUE 제약이 있어야 합니다. `CREATE TABLE temp_products (..., UNIQUE(sku))` 후 `INSERT OR REPLACE`를 사용합니다.

??? success "정답"
    ```sql
    CREATE TABLE temp_products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        sku TEXT NOT NULL UNIQUE,
        price REAL NOT NULL
    );

    -- 최초 삽입
    INSERT INTO temp_products VALUES (1, '무선 마우스', 'WM-001', 35000);
    INSERT INTO temp_products VALUES (2, '기계식 키보드', 'MK-001', 89000);

    -- 확인
    SELECT * FROM temp_products;

    -- UPSERT: sku 'WM-001'이 이미 존재하므로 교체됨
    INSERT OR REPLACE INTO temp_products VALUES (1, '무선 마우스 v2', 'WM-001', 39000);

    -- 확인 (이름과 가격이 변경됨)
    SELECT * FROM temp_products;

    DROP TABLE temp_products;
    ```


---


### 문제 9. ON CONFLICT 구문으로 더 세밀한 UPSERT를 작성하세요. 충돌 시 가격만 갱신하세요.

`INSERT ... ON CONFLICT(column) DO UPDATE SET ...`는 충돌 시 특정 컬럼만 갱신합니다. INSERT OR REPLACE보다 세밀합니다.

??? tip "힌트"
    `ON CONFLICT(sku) DO UPDATE SET price = excluded.price` — `excluded`는 삽입하려던 새 값을 참조하는 특수 키워드입니다.

??? success "정답"
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

    -- ON CONFLICT: sku 충돌 시 가격과 수정일만 갱신 (이름은 유지)
    INSERT INTO temp_products (id, name, sku, price, updated_at)
    VALUES (1, '무선 마우스 NEW', 'WM-001', 42000, '2025-06-01')
    ON CONFLICT(sku) DO UPDATE SET
        price = excluded.price,
        updated_at = excluded.updated_at;

    -- 확인: 이름은 '무선 마우스'로 유지, 가격은 42000으로 갱신
    SELECT * FROM temp_products;

    DROP TABLE temp_products;
    ```

    | id | name | sku | price | updated_at |
    |----|------|-----|-------|------------|
    | 1 | 무선 마우스 | WM-001 | 42000 | 2025-06-01 |
    | 2 | 기계식 키보드 | MK-001 | 89000 | 2025-01-01 |


---


### 문제 10. 조건부 UPDATE: 재고가 10개 미만인 상품만 가격을 5% 인상하세요.

WHERE 조건으로 특정 조건의 행만 선택적으로 UPDATE합니다.

??? tip "힌트"
    `UPDATE ... SET price = ROUND(price * 1.05, 2) WHERE stock_qty < 10` — 재고 부족 상품만 가격 인상.

??? success "정답"
    ```sql
    CREATE TABLE temp_products AS
    SELECT id, name, price, stock_qty
    FROM products
    WHERE is_active = 1
    LIMIT 30;

    -- 변경 전: 재고 10 미만인 상품 확인
    SELECT name, price, stock_qty
    FROM temp_products
    WHERE stock_qty < 10
    ORDER BY stock_qty;

    -- 조건부 가격 인상
    UPDATE temp_products
    SET price = ROUND(price * 1.05, 2)
    WHERE stock_qty < 10;

    -- 변경 후 확인
    SELECT name, price, stock_qty
    FROM temp_products
    WHERE stock_qty < 10
    ORDER BY stock_qty;

    DROP TABLE temp_products;
    ```


---


### 문제 11. INSERT...SELECT로 VIP 고객 목록을 별도 테이블로 복사하세요.

SELECT의 결과를 바로 INSERT의 입력으로 사용합니다. 데이터 마이그레이션, 백업에 유용합니다.

??? tip "힌트"
    `INSERT INTO temp_vip SELECT ... FROM customers WHERE grade = 'VIP'` — VALUES 대신 SELECT를 사용합니다.

??? success "정답"
    ```sql
    -- 빈 테이블 생성
    CREATE TABLE temp_vip (
        id INTEGER,
        name TEXT,
        email TEXT,
        grade TEXT,
        point_balance INTEGER
    );

    -- VIP 고객 복사
    INSERT INTO temp_vip
    SELECT id, name, email, grade, point_balance
    FROM customers
    WHERE grade = 'VIP';

    -- 확인
    SELECT COUNT(*) AS vip_count FROM temp_vip;
    SELECT name, point_balance FROM temp_vip ORDER BY point_balance DESC LIMIT 10;

    DROP TABLE temp_vip;
    ```


---


### 문제 12. INSERT...SELECT로 2025년 월별 매출 요약 테이블을 생성하세요.

집계 쿼리의 결과를 새 테이블에 저장합니다. 리포팅 테이블 생성에 활용됩니다.

??? tip "힌트"
    `CREATE TABLE temp_monthly_sales AS SELECT ...` — CREATE TABLE AS SELECT는 테이블 생성과 데이터 삽입을 동시에 수행합니다.

??? success "정답"
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

    -- 확인
    SELECT * FROM temp_monthly_sales ORDER BY month;

    DROP TABLE temp_monthly_sales;
    ```


---


### 문제 13. CASE를 사용한 조건부 UPDATE: 등급에 따라 포인트를 차등 지급하세요.

CASE 식을 SET 절에 사용하여 조건별로 다른 값을 적용합니다.

??? tip "힌트"
    `SET point_balance = point_balance + CASE WHEN grade = 'VIP' THEN 5000 WHEN grade = 'GOLD' THEN 3000 ... END` — CASE로 등급별 차등 보너스.

??? success "정답"
    ```sql
    CREATE TABLE temp_customers AS
    SELECT id, name, grade, point_balance
    FROM customers
    LIMIT 50;

    -- 변경 전 등급별 평균 포인트
    SELECT grade, ROUND(AVG(point_balance)) AS avg_point
    FROM temp_customers
    GROUP BY grade;

    -- 등급별 차등 포인트 지급
    UPDATE temp_customers
    SET point_balance = point_balance +
        CASE grade
            WHEN 'VIP'    THEN 5000
            WHEN 'GOLD'   THEN 3000
            WHEN 'SILVER' THEN 1000
            ELSE 500
        END;

    -- 변경 후 등급별 평균 포인트
    SELECT grade, ROUND(AVG(point_balance)) AS avg_point
    FROM temp_customers
    GROUP BY grade;

    DROP TABLE temp_customers;
    ```


---


### 문제 14. 서브쿼리를 활용한 UPDATE: 상품의 재고를 주문 수량 기반으로 차감하세요.

UPDATE의 SET 절에서 서브쿼리를 사용하여 다른 테이블의 집계값을 반영합니다.

??? tip "힌트"
    `SET stock_qty = stock_qty - (SELECT SUM(quantity) FROM order_items WHERE product_id = temp_products.id)` — 서브쿼리로 총 주문 수량을 계산하여 차감합니다. COALESCE로 NULL 처리하세요.

??? success "정답"
    ```sql
    CREATE TABLE temp_products AS
    SELECT id, name, stock_qty
    FROM products
    WHERE is_active = 1
    LIMIT 20;

    -- 변경 전 확인
    SELECT name, stock_qty FROM temp_products ORDER BY name LIMIT 5;

    -- 주문 수량만큼 재고 차감
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

    -- 변경 후 확인
    SELECT name, stock_qty FROM temp_products ORDER BY name LIMIT 5;

    DROP TABLE temp_products;
    ```


---


## 실전 (15-20): 다단계 DML, 일괄 변경, 안전한 삭제 패턴

### 문제 15. 상품 카탈로그 복사 후 단종 상품 정리: 복사 → 표시 → 삭제의 3단계를 수행하세요.

실무에서의 데이터 정리 작업 흐름을 연습합니다.

??? tip "힌트"
    1단계: 상품 복사, 2단계: 단종 상품에 표시, 3단계: 표시된 상품 삭제. 각 단계 후 결과를 확인하세요.

??? success "정답"
    ```sql
    -- 1단계: 상품 복사
    CREATE TABLE temp_products AS
    SELECT id, name, price, is_active, discontinued_at
    FROM products;

    SELECT COUNT(*) AS total FROM temp_products;

    -- 2단계: 단종 상품 비활성화
    UPDATE temp_products
    SET is_active = 0
    WHERE discontinued_at IS NOT NULL;

    SELECT
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive
    FROM temp_products;

    -- 3단계: 비활성 상품 삭제
    DELETE FROM temp_products WHERE is_active = 0;

    SELECT COUNT(*) AS remaining FROM temp_products;

    DROP TABLE temp_products;
    ```


---


### 문제 16. 안전한 삭제 패턴: 삭제 대상을 먼저 확인한 뒤 삭제하세요.

실무에서는 DELETE 전에 반드시 SELECT로 삭제 대상을 확인합니다.

??? tip "힌트"
    DELETE 문의 WHERE 조건과 동일한 SELECT를 먼저 실행하여 삭제 대상과 건수를 확인하세요.

??? success "정답"
    ```sql
    CREATE TABLE temp_orders AS
    SELECT id, order_number, customer_id, status, total_amount, ordered_at
    FROM orders
    WHERE ordered_at LIKE '2024%'
    LIMIT 200;

    -- 1단계: 삭제 대상 확인 (SELECT로 미리 보기)
    SELECT COUNT(*) AS to_delete
    FROM temp_orders
    WHERE status = 'cancelled';

    SELECT order_number, total_amount, ordered_at
    FROM temp_orders
    WHERE status = 'cancelled'
    LIMIT 10;

    -- 2단계: 확인 후 삭제
    DELETE FROM temp_orders WHERE status = 'cancelled';

    -- 3단계: 삭제 후 확인
    SELECT COUNT(*) AS remaining FROM temp_orders;
    SELECT status, COUNT(*) FROM temp_orders GROUP BY status;

    DROP TABLE temp_orders;
    ```


---


### 문제 17. INSERT...SELECT + 집계로 고객별 구매 통계 테이블을 생성하세요.

여러 테이블을 JOIN + 집계한 결과를 새 테이블에 저장합니다.

??? tip "힌트"
    `CREATE TABLE temp_customer_stats AS SELECT customer_id, COUNT(*), SUM(...), AVG(...) FROM orders GROUP BY customer_id` — 집계 결과를 테이블로 물리화합니다.

??? success "정답"
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

    -- 확인: 상위 구매 고객
    SELECT name, grade, order_count, total_spent, last_order_at
    FROM temp_customer_stats
    ORDER BY total_spent DESC
    LIMIT 10;

    DROP TABLE temp_customer_stats;
    ```


---


### 문제 18. 여러 조건을 조합한 일괄 UPDATE: 최근 1년간 주문이 없는 고객을 비활성화하세요.

서브쿼리와 날짜 조건을 결합한 복합 UPDATE입니다.

??? tip "힌트"
    `WHERE id NOT IN (SELECT customer_id FROM orders WHERE ordered_at >= ...)` — 최근 1년 주문이 없는 고객을 서브쿼리로 찾습니다.

??? success "정답"
    ```sql
    CREATE TABLE temp_customers AS
    SELECT id, name, grade, is_active, created_at
    FROM customers;

    -- 변경 전 활성 고객 수
    SELECT
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive
    FROM temp_customers;

    -- 최근 1년 주문 없는 고객 비활성화
    UPDATE temp_customers
    SET is_active = 0
    WHERE id NOT IN (
        SELECT DISTINCT customer_id
        FROM orders
        WHERE ordered_at >= DATE('now', '-1 year')
          AND status NOT IN ('cancelled')
    );

    -- 변경 후 활성 고객 수
    SELECT
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive
    FROM temp_customers;

    DROP TABLE temp_customers;
    ```


---


### 문제 19. 트랜잭션처럼 다단계 DML을 수행하세요: 주문 취소 시 포인트 환불 + 재고 복원.

실무에서 주문 취소는 여러 테이블을 동시에 수정해야 합니다. 임시 테이블로 이 흐름을 연습합니다.

??? tip "힌트"
    1) 주문 상태를 'cancelled'로 변경, 2) 사용 포인트를 고객에게 환불, 3) 주문 상품의 재고를 복원. 세 단계를 순서대로 수행하세요.

??? success "정답"
    ```sql
    -- 준비: 연습용 테이블 3개
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

    -- 취소할 주문 확인
    SELECT order_number, customer_id, total_amount, point_used
    FROM temp_orders
    LIMIT 1;

    -- 1단계: 첫 번째 주문 취소 처리
    UPDATE temp_orders
    SET status = 'cancelled'
    WHERE id = (SELECT MIN(id) FROM temp_orders);

    -- 2단계: 사용 포인트 환불
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

    -- 3단계: 재고 복원 (해당 주문의 상품 수량만큼)
    UPDATE temp_products
    SET stock_qty = stock_qty + COALESCE(
        (SELECT SUM(oi.quantity)
         FROM order_items AS oi
         WHERE oi.order_id = (SELECT MIN(id) FROM temp_orders WHERE status = 'cancelled')
           AND oi.product_id = temp_products.id),
        0
    );

    -- 결과 확인
    SELECT '주문' AS table_name, order_number, status FROM temp_orders
    UNION ALL
    SELECT '고객', name, CAST(point_balance AS TEXT) FROM temp_customers LIMIT 3;

    DROP TABLE temp_orders;
    DROP TABLE temp_customers;
    DROP TABLE temp_products;
    ```


---


### 문제 20. 데이터 정규화: 비정규 테이블을 정규화된 두 테이블로 분리하세요.

하나의 비정규 테이블에서 INSERT...SELECT로 마스터 테이블과 상세 테이블을 분리합니다.

??? tip "힌트"
    1) 비정규 테이블을 만들고 샘플 데이터를 넣습니다. 2) 브랜드 마스터 테이블을 DISTINCT로 추출합니다. 3) 상품 테이블에 brand_id를 연결합니다.

??? success "정답"
    ```sql
    -- 비정규 테이블 (브랜드명이 상품에 직접 포함)
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

    -- 1단계: 브랜드 마스터 테이블 추출
    CREATE TABLE temp_brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );

    INSERT INTO temp_brands (name)
    SELECT DISTINCT brand_name
    FROM temp_raw_products
    ORDER BY brand_name;

    SELECT * FROM temp_brands ORDER BY id LIMIT 10;

    -- 2단계: 정규화된 상품 테이블 (brand_id 참조)
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

    -- 확인: 정규화된 상품 + 브랜드 JOIN
    SELECT np.id, np.name, b.name AS brand, np.price
    FROM temp_norm_products AS np
    INNER JOIN temp_brands AS b ON np.brand_id = b.id
    ORDER BY b.name, np.name
    LIMIT 10;

    -- 정리
    DROP TABLE temp_raw_products;
    DROP TABLE temp_brands;
    DROP TABLE temp_norm_products;
    ```


---
