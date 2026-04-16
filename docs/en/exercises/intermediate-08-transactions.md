# Transactions

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `products` — Products (name, price, stock, brand)  

    `customers` — Customers (grade, points, channel)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`, `RELEASE`, `atomicity`, `concurrency control`



### 1. Execute the most basic transaction. Create temp_account, INS


Execute the most basic transaction. Create temp_account, INSERT two accounts, and COMMIT.


**Hint 1:** `BEGIN;` -> 2 INSERT statements -> `COMMIT;`. Changes are not visible to other connections until COMMIT.


??? success "Answer"
    ```sql
    CREATE TABLE temp_account (
        id      INTEGER PRIMARY KEY,
        name    TEXT NOT NULL,
        balance INTEGER NOT NULL DEFAULT 0
    );
    
    BEGIN;
    INSERT INTO temp_account (id, name, balance) VALUES (1, '김철수', 100000);
    INSERT INTO temp_account (id, name, balance) VALUES (2, '이영희', 200000);
    COMMIT;
    
    SELECT * FROM temp_account;
    ```


---


### 2. Use ROLLBACK to undo changes. Accidentally set balance to 0,


Use ROLLBACK to undo changes. Accidentally set balance to 0, then ROLLBACK to recover.


**Hint 1:** `BEGIN;` -> UPDATE -> verify -> `ROLLBACK;` -> verify recovery. ROLLBACK undoes all changes since BEGIN.


??? success "Answer"
    ```sql
    SELECT * FROM temp_account WHERE id = 1;
    
    BEGIN;
    UPDATE temp_account SET balance = 0 WHERE id = 1;
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ROLLBACK;
    
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```


---


### 3. Verify atomicity. Transfer 30,000 won from 김철수 to 이영희. Wrap 


Verify atomicity. Transfer 30,000 won from 김철수 to 이영희. Wrap withdrawal and deposit in a single transaction.


**Hint 1:** Two UPDATEs in a transaction: one `balance - 30000`, the other `balance + 30000`. Both must succeed before COMMIT.


??? success "Answer"
    ```sql
    SELECT id, name, balance FROM temp_account;
    
    BEGIN;
    UPDATE temp_account SET balance = balance - 30000 WHERE id = 1;
    UPDATE temp_account SET balance = balance + 30000 WHERE id = 2;
    COMMIT;
    
    SELECT id, name, balance FROM temp_account;
    ```


---


### 4. ROLLBACK on failure. Attempt to transfer 500,000 (more than 


ROLLBACK on failure. Attempt to transfer 500,000 (more than balance of 70,000). Check insufficient funds and ROLLBACK.


**Hint 1:** After UPDATE, check with SELECT if balance is negative. If negative, ROLLBACK.


??? success "Answer"
    ```sql
    BEGIN;
    UPDATE temp_account SET balance = balance - 500000 WHERE id = 1;
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ROLLBACK;
    
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```


---


### 5. Bundle multiple INSERTs in a transaction for performance. In


Bundle multiple INSERTs in a transaction for performance. Insert multiple log records into temp_log.


**Hint 1:** Without a transaction, SQLite performs disk writes for every row. Wrapping with `BEGIN`/`COMMIT` results in only one write.


??? success "Answer"
    ```sql
    CREATE TABLE temp_log (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        message    TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    BEGIN;
    INSERT INTO temp_log (message) VALUES ('로그 1');
    INSERT INTO temp_log (message) VALUES ('로그 2');
    INSERT INTO temp_log (message) VALUES ('로그 3');
    INSERT INTO temp_log (message) VALUES ('로그 100');
    COMMIT;
    
    SELECT COUNT(*) AS total FROM temp_log;
    ```


---


### 6. Use SAVEPOINT for partial rollback. Undo only the 3rd insert


Use SAVEPOINT for partial rollback. Undo only the 3rd insertion, keep the rest.


**Hint 1:** `ROLLBACK TO sp2;` undoes only changes after sp2.


??? success "Answer"
    ```sql
    BEGIN;
    INSERT INTO temp_account (id, name, balance) VALUES (3, '박민수', 150000);
    SAVEPOINT sp_after_park;
    INSERT INTO temp_account (id, name, balance) VALUES (4, '정수연', 80000);
    SAVEPOINT sp_after_jung;
    INSERT INTO temp_account (id, name, balance) VALUES (5, '오류데이터', -999);
    ROLLBACK TO sp_after_jung;
    COMMIT;
    
    SELECT * FROM temp_account ORDER BY id;
    ```


---


### 7. Use nested SAVEPOINTs. Roll back to a specific point across 


Use nested SAVEPOINTs. Roll back to a specific point across multiple stages of modifications.


**Hint 1:** SAVEPOINTs are identified by name. `ROLLBACK TO B` undoes only changes after B.


??? success "Answer"
    ```sql
    SELECT id, name, balance FROM temp_account ORDER BY id;
    
    BEGIN;
    UPDATE temp_account SET balance = balance + 10000 WHERE id = 1;
    SAVEPOINT sp_a;
    UPDATE temp_account SET balance = balance + 20000 WHERE id = 2;
    SAVEPOINT sp_b;
    UPDATE temp_account SET balance = balance - 50000 WHERE id = 3;
    ROLLBACK TO sp_b;
    UPDATE temp_account SET balance = balance + 5000 WHERE id = 3;
    COMMIT;
    
    SELECT id, name, balance FROM temp_account ORDER BY id;
    ```


---


### 8. Batch processing with SAVEPOINTs: Apply 1% interest to all a


Batch processing with SAVEPOINTs: Apply 1% interest to all accounts.


**Hint 1:** Apply to all accounts at once then verify.


??? success "Answer"
    ```sql
    SELECT id, name, balance FROM temp_account ORDER BY id;
    
    BEGIN;
    SAVEPOINT sp_before_interest;
    UPDATE temp_account
    SET balance = balance + CAST(balance * 0.01 AS INTEGER);
    SELECT id, name, balance,
           CAST(balance * 0.01 AS INTEGER) AS interest
    FROM temp_account ORDER BY id;
    COMMIT;
    
    SELECT id, name, balance FROM temp_account ORDER BY id;
    ```


---


### 9. Understand RELEASE SAVEPOINT. Create a SAVEPOINT, then RELEA


Understand RELEASE SAVEPOINT. Create a SAVEPOINT, then RELEASE it once normal processing is confirmed.


**Hint 1:** `RELEASE SAVEPOINT sp1;` removes that SAVEPOINT. After that, `ROLLBACK TO sp1` would error. RELEASE is not COMMIT.


??? success "Answer"
    ```sql
    BEGIN;
    INSERT INTO temp_account (id, name, balance) VALUES (5, '최지우', 300000);
    SAVEPOINT sp_insert;
    RELEASE SAVEPOINT sp_insert;
    UPDATE temp_account SET balance = balance + 1000 WHERE id = 5;
    COMMIT;
    
    SELECT * FROM temp_account WHERE id = 5;
    ```


---


### 10. Verify DDL behavior within transactions. Does CREATE TABLE g


Verify DDL behavior within transactions. Does CREATE TABLE get rolled back?


**Hint 1:** In SQLite, `BEGIN` -> `CREATE TABLE` -> `INSERT` -> `ROLLBACK` cancels the table creation itself.


??? success "Answer"
    ```sql
    BEGIN;
    CREATE TABLE temp_will_vanish (
        id   INTEGER PRIMARY KEY,
        data TEXT
    );
    INSERT INTO temp_will_vanish VALUES (1, '사라질 데이터');
    ROLLBACK;
    
    SELECT COUNT(*) AS cnt
    FROM sqlite_master
    WHERE name = 'temp_will_vanish';
    ```


---


### 11. Order processing transaction: deduct balance -> verify -> re


Order processing transaction: deduct balance -> verify -> record transaction. ROLLBACK if negative.


**Hint 1:** UPDATE -> SELECT to check balance -> if negative ROLLBACK, if positive INSERT + COMMIT.


??? success "Answer"
    ```sql
    SELECT balance FROM temp_account WHERE id = 1;
    
    BEGIN;
    UPDATE temp_account SET balance = balance - 50000 WHERE id = 1;
    SELECT balance FROM temp_account WHERE id = 1;
    INSERT INTO temp_log (message)
    VALUES ('김철수 50,000원 결제 - 잔액: 30800');
    COMMIT;
    
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```


---


### 12. Point transfer transaction: Transfer 50,000 from 이영희 to 박민수 


Point transfer transaction: Transfer 50,000 from 이영희 to 박민수 using SAVEPOINT.


**Hint 1:** Withdrawal -> SAVEPOINT -> Deposit -> Transfer record -> COMMIT.


??? success "Answer"
    ```sql
    BEGIN;
    UPDATE temp_account SET balance = balance - 50000 WHERE id = 2;
    SAVEPOINT sp_withdrawal;
    SELECT balance FROM temp_account WHERE id = 2;
    UPDATE temp_account SET balance = balance + 50000 WHERE id = 3;
    INSERT INTO temp_log (message)
    VALUES ('이영희 → 박민수 50,000 이체');
    COMMIT;
    
    SELECT id, name, balance FROM temp_account ORDER BY id;
    ```


---


### 13. Process a bulk grade update with a transaction. Assign grade


Process a bulk grade update with a transaction. Assign grades based on balance.


**Hint 1:** `BEGIN` -> `DELETE` (clear existing) -> `INSERT ... SELECT` for grade calculation -> `COMMIT`.


??? success "Answer"
    ```sql
    CREATE TABLE temp_grade (
        account_id INTEGER PRIMARY KEY,
        name       TEXT NOT NULL,
        grade      TEXT NOT NULL,
        balance    INTEGER NOT NULL
    );
    
    BEGIN;
    DELETE FROM temp_grade;
    INSERT INTO temp_grade (account_id, name, grade, balance)
    SELECT
        id, name,
        CASE
            WHEN balance >= 200000 THEN 'VIP'
            WHEN balance >= 100000 THEN 'GOLD'
            ELSE 'SILVER'
        END,
        balance
    FROM temp_account;
    COMMIT;
    
    SELECT * FROM temp_grade ORDER BY balance DESC;
    ```


---


### 14. Complex business scenario: order cancellation. Record cancel


Complex business scenario: order cancellation. Record cancellation -> refund -> record completion with step-by-step SAVEPOINTs.


**Hint 1:** Using SAVEPOINTs at each step makes it easier to identify failures. COMMIT if everything is fine.


??? success "Answer"
    ```sql
    BEGIN;
    SAVEPOINT sp_step1;
    INSERT INTO temp_log (message) VALUES ('주문 취소 요청 - 고객: 김철수');
    SAVEPOINT sp_step2;
    UPDATE temp_account SET balance = balance + 50000 WHERE id = 1;
    SAVEPOINT sp_step3;
    INSERT INTO temp_log (message) VALUES ('환불 완료 - 김철수 +50,000원');
    COMMIT;
    
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    SELECT id, message, created_at FROM temp_log ORDER BY id DESC LIMIT 3;
    ```


---


### 15. Cleanup: Drop all temporary tables. Wrap the deletion in a s


Cleanup: Drop all temporary tables. Wrap the deletion in a single transaction.


**Hint 1:** In SQLite, DDL is included in transactions. `BEGIN` -> multiple `DROP TABLE` -> `COMMIT` is possible.


??? success "Answer"
    ```sql
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%'
    ORDER BY name;
    
    BEGIN;
    DROP TABLE IF EXISTS temp_grade;
    DROP TABLE IF EXISTS temp_log;
    DROP TABLE IF EXISTS temp_account;
    COMMIT;
    
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%';
    ```


---
