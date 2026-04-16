# 트랜잭션

!!! info "사용 테이블"

    `orders` — 주문 (상태, 금액, 일시)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `payments` — 결제 (방법, 금액, 상태)  



!!! abstract "학습 범위"

    `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`, `RELEASE`, `atomicity`, `concurrency control`



### 1. 가장 기본적인 트랜잭션을 실행하세요. temp_account 테이블을 만들고, 두 계좌를 INSERT한 뒤 


가장 기본적인 트랜잭션을 실행하세요. temp_account 테이블을 만들고, 두 계좌를 INSERT한 뒤 COMMIT하세요.


**힌트 1:** `BEGIN;` → INSERT 문 2개 → `COMMIT;` 순서입니다. COMMIT 전까지는 다른 연결에서 변경 내용이 보이지 않습니다.


??? success "정답"
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


### 2. ROLLBACK으로 변경을 취소하세요. 김철수의 잔액을 0으로 만드는 실수를 하고, ROLLBACK으로 되돌


ROLLBACK으로 변경을 취소하세요. 김철수의 잔액을 0으로 만드는 실수를 하고, ROLLBACK으로 되돌리세요.


**힌트 1:** `BEGIN;` → UPDATE → 결과 확인 → `ROLLBACK;` → 복구 확인. ROLLBACK은 BEGIN 이후의 모든 변경을 취소합니다.


??? success "정답"
    ```sql
    SELECT * FROM temp_account WHERE id = 1;
    
    BEGIN;
    UPDATE temp_account SET balance = 0 WHERE id = 1;
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ROLLBACK;
    
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```


---


### 3. 원자성(Atomicity)을 확인하세요. 김철수 → 이영희에게 30,000원 이체. 출금과 입금을 하나의 트


원자성(Atomicity)을 확인하세요. 김철수 → 이영희에게 30,000원 이체. 출금과 입금을 하나의 트랜잭션으로 묶으세요.


**힌트 1:** 트랜잭션 안에서 UPDATE 2번: 한쪽은 `balance - 30000`, 다른 쪽은 `balance + 30000`. 두 UPDATE가 모두 성공해야 COMMIT합니다.


??? success "정답"
    ```sql
    SELECT id, name, balance FROM temp_account;
    
    BEGIN;
    UPDATE temp_account SET balance = balance - 30000 WHERE id = 1;
    UPDATE temp_account SET balance = balance + 30000 WHERE id = 2;
    COMMIT;
    
    SELECT id, name, balance FROM temp_account;
    ```


---


### 4. 실패 시 ROLLBACK하세요. 잔액(70,000)보다 큰 금액(500,000)을 이체하려고 합니다. 잔액 


실패 시 ROLLBACK하세요. 잔액(70,000)보다 큰 금액(500,000)을 이체하려고 합니다. 잔액 부족을 확인하고 ROLLBACK하세요.


**힌트 1:** 출금 UPDATE 후 잔액이 음수인지 SELECT로 확인합니다. 음수라면 ROLLBACK.


??? success "정답"
    ```sql
    BEGIN;
    UPDATE temp_account SET balance = balance - 500000 WHERE id = 1;
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ROLLBACK;
    
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```


---


### 5. 여러 INSERT를 트랜잭션으로 묶어 성능을 확인하세요. temp_log에 여러 건의 로그를 INSERT하세


여러 INSERT를 트랜잭션으로 묶어 성능을 확인하세요. temp_log에 여러 건의 로그를 INSERT하세요.


**힌트 1:** SQLite에서 트랜잭션 없이 INSERT하면 매 건마다 디스크에 쓰기가 발생합니다. `BEGIN`/`COMMIT`으로 묶으면 한 번만 씁니다.


??? success "정답"
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


### 6. SAVEPOINT를 사용하여 부분 롤백하세요. 3번째 삽입만 취소하고 나머지는 유지하세요.


SAVEPOINT를 사용하여 부분 롤백하세요. 3번째 삽입만 취소하고 나머지는 유지하세요.


**힌트 1:** `SAVEPOINT sp1;` → INSERT → `SAVEPOINT sp2;` → INSERT → `ROLLBACK TO sp2;`로 sp2 이후 변경만 취소합니다.


??? success "정답"
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


### 7. 중첩 SAVEPOINT를 사용하세요. 여러 단계의 데이터 수정에서 원하는 지점으로 돌아가세요.


중첩 SAVEPOINT를 사용하세요. 여러 단계의 데이터 수정에서 원하는 지점으로 돌아가세요.


**힌트 1:** SAVEPOINT는 이름으로 구분됩니다. `ROLLBACK TO B`는 B 이후의 변경만 취소하고 A ~ B까지의 변경은 유지합니다.


??? success "정답"
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


### 8. SAVEPOINT를 활용한 일괄 처리: 모든 계좌에 이자 1%를 지급하세요.


SAVEPOINT를 활용한 일괄 처리: 모든 계좌에 이자 1%를 지급하세요.


**힌트 1:** 전체 계좌에 일괄 적용 후 확인하는 방식으로 풀어봅니다.


??? success "정답"
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


### 9. RELEASE SAVEPOINT를 이해하세요. SAVEPOINT를 만들고, 정상 처리가 확인되면 RELEAS


RELEASE SAVEPOINT를 이해하세요. SAVEPOINT를 만들고, 정상 처리가 확인되면 RELEASE하세요.


**힌트 1:** `RELEASE SAVEPOINT sp1;`은 해당 SAVEPOINT를 삭제합니다. 이후 `ROLLBACK TO sp1`은 불가능해집니다. RELEASE는 COMMIT이 아닙니다.


??? success "정답"
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


### 10. 트랜잭션 내에서 DDL의 동작을 확인하세요. CREATE TABLE 후 ROLLBACK하면 테이블이 사라지나


트랜잭션 내에서 DDL의 동작을 확인하세요. CREATE TABLE 후 ROLLBACK하면 테이블이 사라지나요?


**힌트 1:** SQLite에서 `BEGIN` → `CREATE TABLE` → `INSERT` → `ROLLBACK`을 실행하면 테이블 생성 자체가 취소됩니다.


??? success "정답"
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


### 11. 주문 처리 트랜잭션: 잔액 차감 → 잔액 확인 → 거래 기록. 음수면 ROLLBACK.


주문 처리 트랜잭션: 잔액 차감 → 잔액 확인 → 거래 기록. 음수면 ROLLBACK.


**힌트 1:** UPDATE → SELECT로 잔액 확인 → 음수면 ROLLBACK, 양수면 INSERT + COMMIT.


??? success "정답"
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


### 12. 포인트 이체 트랜잭션: 이영희에서 박민수에게 50,000 포인트 이체. SAVEPOINT 사용.


포인트 이체 트랜잭션: 이영희에서 박민수에게 50,000 포인트 이체. SAVEPOINT 사용.


**힌트 1:** 출금 → SAVEPOINT → 입금 → 이체 기록 → COMMIT. 입금에서 문제가 생기면 SAVEPOINT로 돌아갈 수 있습니다.


??? success "정답"
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


### 13. 일괄 등급 업데이트를 트랜잭션으로 처리하세요. 잔액 기준 등급 부여 (200,000+: VIP, 100,00


일괄 등급 업데이트를 트랜잭션으로 처리하세요. 잔액 기준 등급 부여 (200,000+: VIP, 100,000+: GOLD, 그 외: SILVER).


**힌트 1:** `BEGIN` → `DELETE`(기존 데이터 제거) → `INSERT ... SELECT`로 등급 계산 → `COMMIT`.


??? success "정답"
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


### 14. 복잡한 비즈니스 시나리오: 주문 취소 처리. 취소 기록 → 환불 → 완료 기록을 SAVEPOINT로 단계별 


복잡한 비즈니스 시나리오: 주문 취소 처리. 취소 기록 → 환불 → 완료 기록을 SAVEPOINT로 단계별 처리하세요.


**힌트 1:** SAVEPOINT를 단계별로 사용하면 어디서 실패했는지 파악하기 쉽습니다. 최종적으로 문제가 없으면 COMMIT합니다.


??? success "정답"
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


### 15. 정리: 트랜잭션 연습에서 만든 모든 임시 테이블을 삭제하세요. 삭제 자체도 하나의 트랜잭션으로 묶으세요.


정리: 트랜잭션 연습에서 만든 모든 임시 테이블을 삭제하세요. 삭제 자체도 하나의 트랜잭션으로 묶으세요.


**힌트 1:** SQLite에서는 DDL도 트랜잭션에 포함됩니다. `BEGIN` → `DROP TABLE` 여러 번 → `COMMIT`이 가능합니다.


??? success "정답"
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
