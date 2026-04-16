# 실행 계획 분석

!!! info "사용 테이블"

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `point_transactions` — 포인트 (적립, 사용, 소멸)  

    `product_views` — 조회 로그 (고객, 상품, 일시)  



!!! abstract "학습 범위"

    `EXPLAIN`, `QUERY PLAN`, `index`, `performance`, `optimization`



### 1. 다음 쿼리의 실행 계획을 확인하세요. 풀 테이블 스캔이 발생하는지 판단하세요.


다음 쿼리의 실행 계획을 확인하세요. 풀 테이블 스캔이 발생하는지 판단하세요.
```sql
SELECT * FROM orders WHERE total_amount > 1000000;
```


**힌트 1:** total_amount 칼럼에 인덱스가 있는지 확인하세요


??? success "정답"

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


    **실행 결과** (1행)

    | id | parent | notused | detail |
    |---|---|---|---|
    | 2 | 0 | 216 | SCAN orders |


---


### 2. customer_id로 주문을 조회할 때와 status로 조회할 때의 실행 계획을 비교하세요.


customer_id로 주문을 조회할 때와 status로 조회할 때의 실행 계획을 비교하세요.
어느 쪽이 더 효율적인가요?


**힌트 1:** idx_orders_customer_id 인덱스가 존재합니다


??? success "정답"

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


    **실행 결과** (1행)

    | id | parent | notused | detail |
    |---|---|---|---|
    | 3 | 0 | 60 | SEARCH orders USING INDEX idx_orders_... |


---


### 3. 복합 인덱스 idx_orders_customer_status(customer_id, status)가 있습니다


복합 인덱스 idx_orders_customer_status(customer_id, status)가 있습니다.
다음 두 쿼리 중 이 인덱스를 활용하는 것은 어느 쪽인가요?
(A) WHERE customer_id = 42 AND status = 'confirmed'
(B) WHERE status = 'confirmed'


**힌트 1:** 복합 인덱스는 첫 번째 칼럼이 조건에 있어야 사용됩니다


??? success "정답"

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


    **실행 결과** (1행)

    | id | parent | notused | detail |
    |---|---|---|---|
    | 3 | 0 | 61 | SEARCH orders USING INDEX idx_orders_... |


---


### 4. 같은 결과를 반환하는 두 쿼리의 실행 계획을 비교하세요.


같은 결과를 반환하는 두 쿼리의 실행 계획을 비교하세요.
(A) 서브쿼리: SELECT * FROM products WHERE id IN (SELECT product_id FROM order_items WHERE order_id = 100)
(B) JOIN: SELECT p.* FROM products p JOIN order_items oi ON p.id = oi.product_id WHERE oi.order_id = 100
어느 쪽이 효율적인가요?


**힌트 1:** 서브쿼리와 JOIN 두 가지 모두 EXPLAIN으로 확인해보세요


??? success "정답"

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


    **실행 결과** (2행)

    | id | parent | notused | detail |
    |---|---|---|---|
    | 3 | 0 | 54 | SEARCH oi USING COVERING INDEX idx_or... |
    | 7 | 0 | 45 | SEARCH p USING INTEGER PRIMARY KEY (r... |


---


### 5. products 테이블에서 brand와 price만 조회할 때,


products 테이블에서 brand와 price만 조회할 때,
인덱스만으로 결과를 반환하는 커버링 인덱스(covering index) 효과를 확인하세요.
idx_products_name 인덱스와 비교하세요.


**힌트 1:** 커버링 인덱스는 테이블 접근 없이 인덱스만으로 결과를 반환합니다


??? success "정답"

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


    **실행 결과** (1행)

    | id | parent | notused | detail |
    |---|---|---|---|
    | 2 | 0 | 216 | SCAN products |


---


### 6. product_views (약 30만 행)에서 특정 고객의 조회 기록을 찾는 쿼리의


product_views (약 30만 행)에서 특정 고객의 조회 기록을 찾는 쿼리의
실행 계획을 분석하세요. 인덱스가 활용되는지 확인하세요.


**힌트 1:** idx_product_views_customer_id 인덱스가 있습니다


??? success "정답"

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


    **실행 결과** (2행)

    | id | parent | notused | detail |
    |---|---|---|---|
    | 4 | 0 | 61 | SEARCH product_views USING INDEX idx_... |
    | 15 | 0 | 0 | USE TEMP B-TREE FOR ORDER BY |


---


### 7. point_transactions (약 13만 행)에서 윈도우 함수를 사용한 러닝 토탈 쿼리의


point_transactions (약 13만 행)에서 윈도우 함수를 사용한 러닝 토탈 쿼리의
실행 계획을 분석하세요. 임시 테이블이나 정렬 작업이 발생하는지 확인하세요.


**힌트 1:** 윈도우 함수는 내부적으로 정렬이 필요합니다


??? success "정답"

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


    **실행 결과** (4행)

    | id | parent | notused | detail |
    |---|---|---|---|
    | 3 | 0 | 0 | CO-ROUTINE (subquery-2) |
    | 7 | 3 | 61 | SEARCH point_transactions USING INDEX... |
    | 28 | 3 | 0 | USE TEMP B-TREE FOR LAST TERM OF ORDE... |
    | 51 | 0 | 49 | SCAN (subquery-2) |


---


### 8. 다음 느린 쿼리의 실행 계획을 분석하고, 더 효율적인 쿼리로 재작성하세요.


다음 느린 쿼리의 실행 계획을 분석하고, 더 효율적인 쿼리로 재작성하세요.
```sql
SELECT c.name, c.email,
       (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) AS order_count,
       (SELECT SUM(total_amount) FROM orders o WHERE o.customer_id = c.id) AS total_spent
FROM customers c
WHERE (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) > 10;
```


**힌트 1:** 상관 서브쿼리 3개를 JOIN + GROUP BY로 대체하면 테이블 스캔 횟수가 줄어듭니다


??? success "정답"
    ```sql
    SELECT c.name, c.email, COUNT(o.id) AS order_count, SUM(o.total_amount) AS total_spent
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.email
    HAVING COUNT(o.id) > 10;
    ```


    **실행 결과** (총 876행 중 상위 7행)

    | name | email | order_count | total_spent |
    |---|---|---|---|
    | 김상현 | user1004@testmail.kr | 22 | 17,676,624.00 |
    | 박상호 | user1005@testmail.kr | 55 | 74,882,199.00 |
    | 박영식 | user1007@testmail.kr | 34 | 32,737,209.00 |
    | 이예원 | user1011@testmail.kr | 29 | 21,353,795.00 |
    | 김준서 | user1012@testmail.kr | 24 | 19,264,630.00 |
    | 김춘자 | user1014@testmail.kr | 20 | 14,743,243.00 |
    | 이영희 | user1023@testmail.kr | 12 | 9,332,530.00 |


---
