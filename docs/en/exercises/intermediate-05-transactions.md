# Transactions

**Tables:** `customers`, `orders`, `payments`, `products`, `inventory_transactions`

**Concepts:** BEGIN, COMMIT, ROLLBACK, SAVEPOINT, ACID, atomicity, bulk insert


---


### 1. Wrap an order and its payment in a single transaction. Both 


Wrap an order and its payment in a single transaction. Both must succeed for changes to be applied.


**Hint 1:** Wrap with `BEGIN TRANSACTION` -> INSERTs -> `COMMIT` to apply everything at once. Use `last_insert_rowid()` to reference the just-inserted id.


??? success "Answer"
    ```sql
    BEGIN TRANSACTION;
    
    INSERT INTO orders (order_number, customer_id, status, total_amount, shipping_fee, ordered_at, created_at, updated_at)
    VALUES ('ORD-TEST-00001', 1, 'pending', 150000, 0, '2025-12-01', '2025-12-01', '2025-12-01');
    
    INSERT INTO payments (order_id, method, amount, status, created_at)
    VALUES (last_insert_rowid(), 'card', 150000, 'pending', '2025-12-01');
    
    COMMIT;
    
    -- 확인
    SELECT * FROM orders WHERE order_number = 'ORD-TEST-00001';
    ```


---


### 2. What if you accidentally set all VIP customers' points to 0?


What if you accidentally set all VIP customers' points to 0? Use ROLLBACK to recover.


**Hint 1:** After `BEGIN`, execute the UPDATE and check the result. If it's wrong, use `ROLLBACK` to undo all changes since `BEGIN`.


??? success "Answer"
    ```sql
    -- VIP 고객 적립금 현재 상태 확인
    SELECT COUNT(*), SUM(point_balance) FROM customers WHERE grade = 'VIP';
    
    BEGIN TRANSACTION;
    
    -- 실수! 전체 VIP 적립금을 0으로
    UPDATE customers SET point_balance = 0 WHERE grade = 'VIP';
    
    -- 피해 확인
    SELECT COUNT(*), SUM(point_balance) FROM customers WHERE grade = 'VIP';
    
    -- 되돌리기!
    ROLLBACK;
    
    -- 복구 확인
    SELECT COUNT(*), SUM(point_balance) FROM customers WHERE grade = 'VIP';
    ```


---


### 3. What if the order insert succeeds but the payment insert fai


What if the order insert succeeds but the payment insert fails? Transactions guarantee atomicity.


**Hint 1:** If any statement within a transaction fails, `ROLLBACK` to prevent "half-committed" data.


??? success "Answer"
    ```sql
    BEGIN TRANSACTION;
    
    INSERT INTO orders (order_number, customer_id, status, total_amount, shipping_fee, ordered_at, created_at, updated_at)
    VALUES ('ORD-TEST-00002', 1, 'pending', 200000, 0, '2025-12-01', '2025-12-01', '2025-12-01');
    
    -- 의도적으로 잘못된 데이터 삽입 (order_id에 NULL)
    INSERT INTO payments (order_id, method, amount, status, created_at)
    VALUES (NULL, 'card', 200000, 'pending', '2025-12-01');
    
    -- 에러 발생 시 수동으로 ROLLBACK
    ROLLBACK;
    
    -- 주문도 삽입되지 않았음을 확인
    SELECT * FROM orders WHERE order_number = 'ORD-TEST-00002';
    ```


---


### 4. Use SAVEPOINT when you want to undo only part of a long tran


Use SAVEPOINT when you want to undo only part of a long transaction.


**Hint 1:** Create a checkpoint with `SAVEPOINT name`, then roll back to that point with `ROLLBACK TO name`. Earlier changes are preserved.


??? success "Answer"
    ```sql
    BEGIN TRANSACTION;
    
    -- 1단계: 고객 등급 변경
    UPDATE customers SET grade = 'GOLD' WHERE id = 1;
    SAVEPOINT after_grade;
    
    -- 2단계: 적립금 변경 (실수!)
    UPDATE customers SET point_balance = -9999 WHERE id = 1;
    
    -- 2단계만 되돌리기
    ROLLBACK TO after_grade;
    
    -- 1단계(등급 변경)는 유지됨을 확인
    SELECT id, name, grade, point_balance FROM customers WHERE id = 1;
    
    -- 최종 반영 또는 전체 취소
    ROLLBACK;  -- 전체 취소
    ```


---


### 5. Understand the difference when inserting 10,000 records with


Understand the difference when inserting 10,000 records with and without a transaction.


**Hint 1:** Without a transaction, each INSERT triggers a disk write. Wrapping with `BEGIN`~`COMMIT` writes to disk only once.


??? success "Answer"
    ```sql
    -- 트랜잭션 없이: 각 INSERT마다 디스크에 쓰기 (느림)
    INSERT INTO inventory_transactions (product_id, type, quantity, created_at) VALUES (1, 'inbound', 10, '2025-12-01');
    INSERT INTO inventory_transactions (product_id, type, quantity, created_at) VALUES (2, 'inbound', 20, '2025-12-01');
    -- ... 10,000번 반복 → 각각 디스크 I/O
    
    -- 트랜잭션으로 묶기: 마지막 COMMIT 한 번만 디스크에 쓰기 (빠름)
    BEGIN TRANSACTION;
    INSERT INTO inventory_transactions (product_id, type, quantity, created_at) VALUES (1, 'inbound', 10, '2025-12-01');
    INSERT INTO inventory_transactions (product_id, type, quantity, created_at) VALUES (2, 'inbound', 20, '2025-12-01');
    -- ... 10,000번 반복 → 메모리에만 기록
    COMMIT;  -- 한 번에 디스크에 쓰기
    ```


---


### 6. Check the current database's ACID settings.


Check the current database's ACID settings.


**Hint 1:** Use `PRAGMA journal_mode`, `PRAGMA foreign_keys`, etc. to query SQLite's transaction-related settings.


??? success "Answer"
    ```sql
    -- SQLite 저널 모드 확인 (WAL이면 동시 읽기 가능)
    PRAGMA journal_mode;
    
    -- 자동 커밋 모드 확인
    PRAGMA auto_vacuum;
    
    -- 외래 키 강제 여부
    PRAGMA foreign_keys;
    ```


---


### 7. Write a transaction that deducts inventory when an order is 


Write a transaction that deducts inventory when an order is placed. ROLLBACK if stock is insufficient.


**Hint 1:** Use `UPDATE ... SET stock_qty = stock_qty - N WHERE stock_qty >= N` to prevent insufficient stock (0 rows affected). Check with the `changes()` function.


??? success "Answer"
    ```sql
    -- 현재 재고 확인
    SELECT id, name, stock_qty FROM products WHERE id = 1;
    
    BEGIN TRANSACTION;
    
    -- 재고 차감
    UPDATE products
    SET stock_qty = stock_qty - 3,
        updated_at = '2025-12-01'
    WHERE id = 1
      AND stock_qty >= 3;  -- 재고 부족 방지
    
    -- 변경된 행이 0이면 재고 부족 → ROLLBACK
    -- (SQLite에서는 changes() 함수로 확인)
    SELECT CASE
        WHEN changes() = 0 THEN '재고 부족! ROLLBACK 필요'
        ELSE '재고 차감 성공'
    END AS result;
    
    -- 성공 시 COMMIT, 실패 시 ROLLBACK
    COMMIT;
    
    -- 결과 확인
    SELECT id, name, stock_qty FROM products WHERE id = 1;
    ```


---
