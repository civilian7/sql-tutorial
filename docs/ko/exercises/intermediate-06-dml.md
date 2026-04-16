# DML 실습 (INSERT, UPDATE, DELETE)

!!! info "사용 테이블"

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  



!!! abstract "학습 범위"

    `INSERT INTO`, `UPDATE SET`, `DELETE FROM`, `INSERT INTO SELECT`, `subquery DML`, `UPSERT`, `ON CONFLICT`



### 1. 연습용 상품 테이블을 만들고, 상품 1건을 삽입하세요.


연습용 상품 테이블을 만들고, 상품 1건을 삽입하세요.


**힌트 1:** `CREATE TABLE temp_products AS SELECT * FROM products WHERE 1=0` — 구조만 복사하는 빈 테이블을 만듭니다.


??? success "정답"
    ```sql
    CREATE TABLE temp_products AS
    SELECT * FROM products WHERE 1 = 0;
    
    INSERT INTO temp_products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (9001, 1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01');
    
    SELECT * FROM temp_products;
    
    DROP TABLE temp_products;
    ```


---


### 2. 연습용 상품 테이블에 여러 건을 한 번에 삽입하세요.


연습용 상품 테이블에 여러 건을 한 번에 삽입하세요.


**힌트 1:** `INSERT INTO ... VALUES (...), (...), (...)` — SQLite는 한 INSERT 문에 여러 VALUES 행을 지원합니다.


??? success "정답"
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


### 3. 연습용 테이블에서 특정 상품의 가격을 수정하세요.


연습용 테이블에서 특정 상품의 가격을 수정하세요.


**힌트 1:** `UPDATE temp_products SET price = ... WHERE id = ...` — WHERE 절을 반드시 포함하세요.


??? success "정답"
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


### 4. 연습용 테이블에서 특정 상품을 삭제하세요.


연습용 테이블에서 특정 상품을 삭제하세요.


**힌트 1:** `DELETE FROM temp_products WHERE id = ...` — WHERE 절 없이 실행하면 전체 데이터가 삭제됩니다.


??? success "정답"
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


### 5. 연습용 고객 테이블을 만들고, 등급이 'BRONZE'인 고객의 등급을 'SILVER'로 일괄 변경하세요.


연습용 고객 테이블을 만들고, 등급이 'BRONZE'인 고객의 등급을 'SILVER'로 일괄 변경하세요.


**힌트 1:** `UPDATE temp_customers SET grade = 'SILVER' WHERE grade = 'BRONZE'` — 조건에 맞는 모든 행이 변경됩니다.


??? success "정답"
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


### 6. 연습용 테이블에서 포인트가 0인 고객을 모두 삭제하세요. 삭제 전/후 건수를 비교하세요.


연습용 테이블에서 포인트가 0인 고객을 모두 삭제하세요. 삭제 전/후 건수를 비교하세요.


**힌트 1:** 삭제 전 `SELECT COUNT(*)`, DELETE 실행, 삭제 후 `SELECT COUNT(*)` 순서로 실행하세요.


??? success "정답"
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


### 7. 연습용 상품 테이블에서 전체 상품의 가격을 10% 인상하세요.


연습용 상품 테이블에서 전체 상품의 가격을 10% 인상하세요.


**힌트 1:** `UPDATE temp_products SET price = ROUND(price * 1.1, 2)` — 소수점은 ROUND로 정리합니다.


??? success "정답"
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


### 8. INSERT OR REPLACE (UPSERT)로 상품을 삽입하되, 이미 존재하면 가격만 갱신하세요.


INSERT OR REPLACE (UPSERT)로 상품을 삽입하되, 이미 존재하면 가격만 갱신하세요.


**힌트 1:** 테이블에 UNIQUE 제약이 있어야 합니다. `CREATE TABLE temp_products (..., UNIQUE(sku))` 후 `INSERT OR REPLACE`를 사용합니다.


??? success "정답"
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


### 9. ON CONFLICT 구문으로 더 세밀한 UPSERT를 작성하세요. 충돌 시 가격만 갱신하세요.


ON CONFLICT 구문으로 더 세밀한 UPSERT를 작성하세요. 충돌 시 가격만 갱신하세요.


**힌트 1:** `ON CONFLICT(sku) DO UPDATE SET price = excluded.price` — `excluded`는 삽입하려던 새 값을 참조하는 특수 키워드입니다.


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
    
    INSERT INTO temp_products (id, name, sku, price, updated_at)
    VALUES (1, '무선 마우스 NEW', 'WM-001', 42000, '2025-06-01')
    ON CONFLICT(sku) DO UPDATE SET
        price = excluded.price,
        updated_at = excluded.updated_at;
    
    SELECT * FROM temp_products;
    
    DROP TABLE temp_products;
    ```


---


### 10. 조건부 UPDATE: 재고가 10개 미만인 상품만 가격을 5% 인상하세요.


조건부 UPDATE: 재고가 10개 미만인 상품만 가격을 5% 인상하세요.


**힌트 1:** `UPDATE ... SET price = ROUND(price * 1.05, 2) WHERE stock_qty < 10` — 재고 부족 상품만 가격 인상.


??? success "정답"
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


### 11. INSERT...SELECT로 VIP 고객 목록을 별도 테이블로 복사하세요.


INSERT...SELECT로 VIP 고객 목록을 별도 테이블로 복사하세요.


**힌트 1:** `INSERT INTO temp_vip SELECT ... FROM customers WHERE grade = 'VIP'` — VALUES 대신 SELECT를 사용합니다.


??? success "정답"
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


### 12. INSERT...SELECT로 2025년 월별 매출 요약 테이블을 생성하세요.


INSERT...SELECT로 2025년 월별 매출 요약 테이블을 생성하세요.


**힌트 1:** `CREATE TABLE temp_monthly_sales AS SELECT ...` — CREATE TABLE AS SELECT는 테이블 생성과 데이터 삽입을 동시에 수행합니다.


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
    
    SELECT * FROM temp_monthly_sales ORDER BY month;
    
    DROP TABLE temp_monthly_sales;
    ```


---


### 13. CASE를 사용한 조건부 UPDATE: 등급에 따라 포인트를 차등 지급하세요.


CASE를 사용한 조건부 UPDATE: 등급에 따라 포인트를 차등 지급하세요.


**힌트 1:** `SET point_balance = point_balance + CASE WHEN grade = 'VIP' THEN 5000 ... END` — CASE로 등급별 차등 보너스.


??? success "정답"
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


### 14. 서브쿼리를 활용한 UPDATE: 상품의 재고를 주문 수량 기반으로 차감하세요.


서브쿼리를 활용한 UPDATE: 상품의 재고를 주문 수량 기반으로 차감하세요.


**힌트 1:** `SET stock_qty = stock_qty - (SELECT SUM(quantity) FROM order_items WHERE product_id = temp_products.id)` — COALESCE로 NULL 처리하세요.


??? success "정답"
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


### 15. 상품 카탈로그 복사 후 단종 상품 정리: 복사 → 표시 → 삭제의 3단계를 수행하세요.


상품 카탈로그 복사 후 단종 상품 정리: 복사 → 표시 → 삭제의 3단계를 수행하세요.


**힌트 1:** 1단계: 상품 복사, 2단계: 단종 상품에 표시, 3단계: 표시된 상품 삭제. 각 단계 후 결과를 확인하세요.


??? success "정답"
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


### 16. 안전한 삭제 패턴: 삭제 대상을 먼저 확인한 뒤 삭제하세요.


안전한 삭제 패턴: 삭제 대상을 먼저 확인한 뒤 삭제하세요.


**힌트 1:** DELETE 문의 WHERE 조건과 동일한 SELECT를 먼저 실행하여 삭제 대상과 건수를 확인하세요.


??? success "정답"
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


### 17. INSERT...SELECT + 집계로 고객별 구매 통계 테이블을 생성하세요.


INSERT...SELECT + 집계로 고객별 구매 통계 테이블을 생성하세요.


**힌트 1:** `CREATE TABLE temp_customer_stats AS SELECT customer_id, COUNT(*), SUM(...), AVG(...) FROM orders GROUP BY customer_id` — 집계 결과를 테이블로 물리화합니다.


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
    
    SELECT name, grade, order_count, total_spent, last_order_at
    FROM temp_customer_stats
    ORDER BY total_spent DESC
    LIMIT 10;
    
    DROP TABLE temp_customer_stats;
    ```


---


### 18. 여러 조건을 조합한 일괄 UPDATE: 최근 1년간 주문이 없는 고객을 비활성화하세요.


여러 조건을 조합한 일괄 UPDATE: 최근 1년간 주문이 없는 고객을 비활성화하세요.


**힌트 1:** `WHERE id NOT IN (SELECT customer_id FROM orders WHERE ordered_at >= ...)` — 최근 1년 주문이 없는 고객을 서브쿼리로 찾습니다.


??? success "정답"
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


### 19. 트랜잭션처럼 다단계 DML을 수행하세요: 주문 취소 시 포인트 환불 + 재고 복원.


트랜잭션처럼 다단계 DML을 수행하세요: 주문 취소 시 포인트 환불 + 재고 복원.


**힌트 1:** 1) 주문 상태를 'cancelled'로 변경, 2) 사용 포인트를 고객에게 환불, 3) 주문 상품의 재고를 복원. 세 단계를 순서대로 수행하세요.


??? success "정답"
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


### 20. 데이터 정규화: 비정규 테이블을 정규화된 두 테이블로 분리하세요.


데이터 정규화: 비정규 테이블을 정규화된 두 테이블로 분리하세요.


**힌트 1:** 1) 비정규 테이블을 만들고 샘플 데이터를 넣습니다. 2) 브랜드 마스터 테이블을 DISTINCT로 추출합니다. 3) 상품 테이블에 brand_id를 연결합니다.


??? success "정답"
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
