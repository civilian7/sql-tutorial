# 트랜잭션


!!! warning "연습 전 주의사항"
    트랜잭션 연습은 **실제 데이터를 변경**합니다. 안전하게 연습하려면 임시 테이블을 사용하세요. 이 연습의 모든 문제는 임시 테이블이나 ROLLBACK을 활용하여 원본 데이터에 영향을 주지 않도록 설계되어 있습니다.


## 기초 (1~5): BEGIN, COMMIT, ROLLBACK


### 문제 1

**가장 기본적인 트랜잭션을 실행하세요.** 임시 테이블 `temp_account`를 만들고, 두 개의 계좌를 INSERT한 뒤 COMMIT하세요.


??? tip "힌트"
    `BEGIN;` → INSERT 문 2개 → `COMMIT;` 순서입니다. COMMIT 전까지는 다른 연결에서 변경 내용이 보이지 않습니다.


??? success "정답"
    ```sql
    -- 준비: 임시 테이블
    CREATE TABLE temp_account (
        id      INTEGER PRIMARY KEY,
        name    TEXT NOT NULL,
        balance INTEGER NOT NULL DEFAULT 0
    );

    -- 트랜잭션 시작
    BEGIN;

    INSERT INTO temp_account (id, name, balance) VALUES (1, '김철수', 100000);
    INSERT INTO temp_account (id, name, balance) VALUES (2, '이영희', 200000);

    -- 커밋 → 영구 반영
    COMMIT;

    SELECT * FROM temp_account;
    ```

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 100000  |
    | 2  | 이영희 | 200000  |


---


### 문제 2

**ROLLBACK으로 변경을 취소하세요.** `temp_account`에서 김철수의 잔액을 0으로 만드는 실수를 하고, ROLLBACK으로 되돌리세요.


??? tip "힌트"
    `BEGIN;` → UPDATE → 결과 확인 → `ROLLBACK;` → 복구 확인. ROLLBACK은 BEGIN 이후의 모든 변경을 취소합니다.


??? success "정답"
    ```sql
    -- 변경 전 확인
    SELECT * FROM temp_account WHERE id = 1;

    BEGIN;

    -- 실수! 잔액을 0으로
    UPDATE temp_account SET balance = 0 WHERE id = 1;

    -- 피해 확인
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    -- balance = 0

    -- 되돌리기
    ROLLBACK;

    -- 복구 확인
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```

    ROLLBACK 후:

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 100000  |


---


### 문제 3

**원자성(Atomicity)을 확인하세요.** 계좌 이체를 시뮬레이션합니다. 김철수 → 이영희에게 30,000원 이체. 출금과 입금을 하나의 트랜잭션으로 묶고, 이체 후 양쪽 잔액을 확인하세요.


??? tip "힌트"
    트랜잭션 안에서 UPDATE 2번: 한쪽은 `balance - 30000`, 다른 쪽은 `balance + 30000`. 두 UPDATE가 모두 성공해야 COMMIT합니다.


??? success "정답"
    ```sql
    -- 이체 전 잔액 확인
    SELECT id, name, balance FROM temp_account;

    BEGIN;

    -- 출금
    UPDATE temp_account SET balance = balance - 30000 WHERE id = 1;

    -- 입금
    UPDATE temp_account SET balance = balance + 30000 WHERE id = 2;

    COMMIT;

    -- 이체 후 잔액 확인
    SELECT id, name, balance FROM temp_account;
    ```

    이체 전:

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 100000  |
    | 2  | 이영희 | 200000  |

    이체 후:

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 70000   |
    | 2  | 이영희 | 230000  |


---


### 문제 4

**실패 시 ROLLBACK하세요.** 김철수 잔액(70,000)보다 큰 금액(500,000)을 이체하려고 합니다. 잔액 부족을 확인하고 ROLLBACK하세요.


??? tip "힌트"
    출금 UPDATE 후 잔액이 음수인지 SELECT로 확인합니다. 음수라면 ROLLBACK. 실제 앱에서는 프로그램 코드에서 이 판단을 합니다.


??? success "정답"
    ```sql
    BEGIN;

    -- 출금 시도 (잔액 초과)
    UPDATE temp_account SET balance = balance - 500000 WHERE id = 1;

    -- 잔액 확인 → 음수!
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    -- balance = -430000

    -- 잔액 부족 → 전체 취소
    ROLLBACK;

    -- 원래 잔액 유지 확인
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```

    ROLLBACK 후:

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 70000   |


---


### 문제 5

**여러 INSERT를 트랜잭션으로 묶어 성능을 확인하세요.** `temp_log` 테이블에 100건의 로그를 INSERT할 때 트랜잭션 유무에 따른 차이를 이해하세요.


??? tip "힌트"
    SQLite에서 트랜잭션 없이 INSERT하면 매 건마다 디스크에 쓰기(fsync)가 발생합니다. `BEGIN`/`COMMIT`으로 묶으면 한 번만 씁니다.


??? success "정답"
    ```sql
    CREATE TABLE temp_log (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        message    TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    -- 트랜잭션으로 묶어서 INSERT (빠름)
    BEGIN;

    INSERT INTO temp_log (message) VALUES ('로그 1');
    INSERT INTO temp_log (message) VALUES ('로그 2');
    INSERT INTO temp_log (message) VALUES ('로그 3');
    -- ... 실제로는 100건을 삽입
    INSERT INTO temp_log (message) VALUES ('로그 100');

    COMMIT;

    SELECT COUNT(*) AS total FROM temp_log;
    ```

    | total |
    |-------|
    | 4     |

    !!! info "왜 트랜잭션이 빠른가?"
        SQLite는 트랜잭션 없이 INSERT하면 매 행마다 WAL/저널에 쓰기+fsync를 수행합니다. 100건이면 100번의 디스크 동기화가 발생합니다. 트랜잭션으로 묶으면 **1번만 동기화**하므로 수십 배 빨라질 수 있습니다.


---


## 응용 (6~10): SAVEPOINT와 다단계 트랜잭션


### 문제 6

**SAVEPOINT를 사용하여 부분 롤백하세요.** 3명의 계좌를 추가하되, 3번째 삽입을 실수로 간주하고 SAVEPOINT로 2번째까지만 유지하세요.


??? tip "힌트"
    `SAVEPOINT sp1;` → INSERT → `SAVEPOINT sp2;` → INSERT → ... `ROLLBACK TO sp2;`로 sp2 이후 변경만 취소합니다.


??? success "정답"
    ```sql
    BEGIN;

    INSERT INTO temp_account (id, name, balance) VALUES (3, '박민수', 150000);

    SAVEPOINT sp_after_park;

    INSERT INTO temp_account (id, name, balance) VALUES (4, '정수연', 80000);

    SAVEPOINT sp_after_jung;

    -- 실수! 잘못된 데이터
    INSERT INTO temp_account (id, name, balance) VALUES (5, '오류데이터', -999);

    -- 3번째 삽입만 취소 (정수연까지는 유지)
    ROLLBACK TO sp_after_jung;

    COMMIT;

    SELECT * FROM temp_account ORDER BY id;
    ```

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 70000   |
    | 2  | 이영희 | 230000  |
    | 3  | 박민수 | 150000  |
    | 4  | 정수연 | 80000   |


---


### 문제 7

**중첩 SAVEPOINT를 사용하세요.** 여러 단계의 데이터 수정에서 원하는 지점으로 돌아가세요.

시나리오:
1. 김철수 잔액 +10,000 → SAVEPOINT A
2. 이영희 잔액 +20,000 → SAVEPOINT B
3. 박민수 잔액 -50,000 (실수) → ROLLBACK TO B
4. 박민수 잔액 +5,000 (정정) → COMMIT


??? tip "힌트"
    SAVEPOINT는 이름으로 구분됩니다. `ROLLBACK TO B`는 B 이후의 변경만 취소하고 A 이후 ~ B까지의 변경은 유지합니다.


??? success "정답"
    ```sql
    -- 변경 전 확인
    SELECT id, name, balance FROM temp_account ORDER BY id;

    BEGIN;

    -- 1단계: 김철수 +10,000
    UPDATE temp_account SET balance = balance + 10000 WHERE id = 1;
    SAVEPOINT sp_a;

    -- 2단계: 이영희 +20,000
    UPDATE temp_account SET balance = balance + 20000 WHERE id = 2;
    SAVEPOINT sp_b;

    -- 3단계: 실수! 박민수 -50,000
    UPDATE temp_account SET balance = balance - 50000 WHERE id = 3;

    -- 3단계 취소 (sp_b 이후만 롤백)
    ROLLBACK TO sp_b;

    -- 3단계 정정: 박민수 +5,000
    UPDATE temp_account SET balance = balance + 5000 WHERE id = 3;

    COMMIT;

    SELECT id, name, balance FROM temp_account ORDER BY id;
    ```

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 80000   |
    | 2  | 이영희 | 250000  |
    | 3  | 박민수 | 155000  |
    | 4  | 정수연 | 80000   |


---


### 문제 8

**SAVEPOINT를 활용한 일괄 처리를 구현하세요.** 모든 계좌에 이자 1%를 지급하되, 잔액이 100원 미만인 계좌가 있으면 해당 계좌의 이자만 취소하세요.


??? tip "힌트"
    각 계좌마다 SAVEPOINT를 잡고, UPDATE 후 조건을 확인하여 개별 롤백합니다. 여기서는 전체 계좌에 일괄 적용 후 확인하는 방식으로 풀어봅니다.


??? success "정답"
    ```sql
    -- 이자 지급 전 확인
    SELECT id, name, balance FROM temp_account ORDER BY id;

    BEGIN;

    SAVEPOINT sp_before_interest;

    -- 전체 이자 1% 지급 (정수 처리)
    UPDATE temp_account
    SET balance = balance + CAST(balance * 0.01 AS INTEGER);

    -- 결과 확인
    SELECT id, name, balance,
           CAST(balance * 0.01 AS INTEGER) AS interest
    FROM temp_account
    ORDER BY id;

    COMMIT;

    SELECT id, name, balance FROM temp_account ORDER BY id;
    ```

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 80800   |
    | 2  | 이영희 | 252500  |
    | 3  | 박민수 | 156550  |
    | 4  | 정수연 | 80800   |


---


### 문제 9

**RELEASE SAVEPOINT를 이해하세요.** SAVEPOINT를 만들고, 정상 처리가 확인되면 RELEASE하여 해당 SAVEPOINT를 제거하세요.


??? tip "힌트"
    `RELEASE SAVEPOINT sp1;`은 해당 SAVEPOINT를 삭제합니다. 이후 `ROLLBACK TO sp1`은 불가능해집니다. RELEASE는 COMMIT이 아닙니다 — 외부 트랜잭션은 여전히 진행 중입니다.


??? success "정답"
    ```sql
    BEGIN;

    -- 새 계좌 추가
    INSERT INTO temp_account (id, name, balance) VALUES (5, '최지우', 300000);
    SAVEPOINT sp_insert;

    -- 정상 확인 → SAVEPOINT 해제
    RELEASE SAVEPOINT sp_insert;
    -- 이 시점 이후 ROLLBACK TO sp_insert는 에러

    -- 추가 작업
    UPDATE temp_account SET balance = balance + 1000 WHERE id = 5;

    COMMIT;

    SELECT * FROM temp_account WHERE id = 5;
    ```

    | id | name   | balance |
    |----|--------|---------|
    | 5  | 최지우 | 301000  |


---


### 문제 10

**트랜잭션 내에서 DDL의 동작을 확인하세요.** 트랜잭션 안에서 테이블을 만들고 데이터를 넣은 뒤 ROLLBACK하면 어떻게 될까요?

!!! info "참고"
    SQLite에서는 DDL(CREATE TABLE, DROP TABLE)도 트랜잭션에 포함됩니다. MySQL/Oracle에서는 DDL이 암시적 COMMIT을 발생시켜 롤백이 불가능합니다.


??? tip "힌트"
    SQLite에서 `BEGIN` → `CREATE TABLE` → `INSERT` → `ROLLBACK`을 실행하면 테이블 생성 자체가 취소됩니다.


??? success "정답"
    ```sql
    BEGIN;

    CREATE TABLE temp_will_vanish (
        id   INTEGER PRIMARY KEY,
        data TEXT
    );

    INSERT INTO temp_will_vanish VALUES (1, '사라질 데이터');

    -- 전체 취소 (테이블 생성도 취소)
    ROLLBACK;

    -- 테이블이 존재하지 않음 (에러)
    -- SELECT * FROM temp_will_vanish;

    -- 확인
    SELECT COUNT(*) AS cnt
    FROM sqlite_master
    WHERE name = 'temp_will_vanish';
    ```

    | cnt |
    |-----|
    | 0   |

    !!! warning "DB마다 다른 DDL 트랜잭션 동작"
        | DB | DDL 롤백 가능? |
        |---|---|
        | SQLite | O (완전 지원) |
        | PostgreSQL | O (완전 지원) |
        | MySQL | X (암시적 COMMIT) |
        | Oracle | X (암시적 COMMIT) |
        | SQL Server | O (완전 지원) |


---


## 실전 (11~15): 비즈니스 시나리오


### 문제 11

**주문 처리 트랜잭션을 구현하세요.** 다음을 하나의 트랜잭션으로 처리하세요:

1. `temp_account`에서 김철수(id=1) 잔액에서 50,000원 차감
2. `temp_log`에 거래 기록 삽입
3. 차감 후 잔액이 음수면 전체 ROLLBACK


??? tip "힌트"
    UPDATE → SELECT로 잔액 확인 → 음수면 ROLLBACK, 양수면 INSERT + COMMIT. SQLite에서는 프로그래밍 언어 없이 조건 분기가 어려우므로, 수동으로 확인 후 결정합니다.


??? success "정답"
    ```sql
    -- 현재 잔액 확인
    SELECT balance FROM temp_account WHERE id = 1;
    -- 80800

    BEGIN;

    -- 1) 잔액 차감
    UPDATE temp_account SET balance = balance - 50000 WHERE id = 1;

    -- 2) 잔액 확인
    SELECT balance FROM temp_account WHERE id = 1;
    -- 30800 (양수 → OK)

    -- 3) 거래 기록
    INSERT INTO temp_log (message)
    VALUES ('김철수 50,000원 결제 - 잔액: 30800');

    COMMIT;

    -- 결과 확인
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 30800   |


---


### 문제 12

**포인트 이체 트랜잭션을 구현하세요.** 이영희(id=2)에서 박민수(id=3)에게 50,000 포인트를 이체합니다. SAVEPOINT를 사용하여 이체 기록까지 완료하세요.


??? tip "힌트"
    출금 → SAVEPOINT → 입금 → 이체 기록 → COMMIT. 입금에서 문제가 생기면 SAVEPOINT로 돌아갈 수 있습니다.


??? success "정답"
    ```sql
    BEGIN;

    -- 1) 출금
    UPDATE temp_account SET balance = balance - 50000 WHERE id = 2;
    SAVEPOINT sp_withdrawal;

    -- 2) 잔액 확인 (양수여야 함)
    SELECT balance FROM temp_account WHERE id = 2;
    -- 202500 (양수 → OK)

    -- 3) 입금
    UPDATE temp_account SET balance = balance + 50000 WHERE id = 3;

    -- 4) 이체 기록
    INSERT INTO temp_log (message)
    VALUES ('이영희 → 박민수 50,000 이체');

    COMMIT;

    -- 결과 확인
    SELECT id, name, balance FROM temp_account ORDER BY id;
    ```

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 30800   |
    | 2  | 이영희 | 202500  |
    | 3  | 박민수 | 206550  |
    | 4  | 정수연 | 80800   |
    | 5  | 최지우 | 301000  |


---


### 문제 13

**일괄 등급 업데이트를 트랜잭션으로 처리하세요.** `temp_account`에서 잔액 기준으로 등급을 부여하는 `temp_grade` 테이블을 만들고, 트랜잭션 안에서 일괄 처리하세요.

등급 기준:
- 잔액 200,000 이상: VIP
- 잔액 100,000 이상: GOLD
- 그 외: SILVER


??? tip "힌트"
    먼저 `temp_grade` 테이블을 만들고, `BEGIN` → `DELETE`(기존 데이터 제거) → `INSERT ... SELECT`로 등급 계산 → `COMMIT`.


??? success "정답"
    ```sql
    CREATE TABLE temp_grade (
        account_id INTEGER PRIMARY KEY,
        name       TEXT NOT NULL,
        grade      TEXT NOT NULL,
        balance    INTEGER NOT NULL
    );

    BEGIN;

    -- 기존 등급 제거 (재실행 시)
    DELETE FROM temp_grade;

    -- 잔액 기준 등급 일괄 부여
    INSERT INTO temp_grade (account_id, name, grade, balance)
    SELECT
        id,
        name,
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

    | account_id | name   | grade  | balance |
    |------------|--------|--------|---------|
    | 5          | 최지우 | VIP    | 301000  |
    | 3          | 박민수 | VIP    | 206550  |
    | 2          | 이영희 | VIP    | 202500  |
    | 4          | 정수연 | SILVER | 80800   |
    | 1          | 김철수 | SILVER | 30800   |


---


### 문제 14

**복잡한 비즈니스 시나리오: 주문 취소 처리를 구현하세요.** 다음을 하나의 트랜잭션으로 처리하세요:

1. `temp_log`에 취소 요청 기록
2. 김철수(id=1)에게 50,000원 환불 (잔액 +50,000)
3. `temp_log`에 환불 완료 기록

중간에 어떤 단계라도 실패하면 전체 취소되어야 합니다.


??? tip "힌트"
    SAVEPOINT를 단계별로 사용하면 어디서 실패했는지 파악하기 쉽습니다. 최종적으로 문제가 없으면 COMMIT합니다.


??? success "정답"
    ```sql
    BEGIN;

    SAVEPOINT sp_step1;

    -- 1단계: 취소 요청 기록
    INSERT INTO temp_log (message) VALUES ('주문 취소 요청 - 고객: 김철수');

    SAVEPOINT sp_step2;

    -- 2단계: 환불 처리
    UPDATE temp_account SET balance = balance + 50000 WHERE id = 1;

    SAVEPOINT sp_step3;

    -- 3단계: 환불 완료 기록
    INSERT INTO temp_log (message) VALUES ('환불 완료 - 김철수 +50,000원');

    -- 전체 정상 → 커밋
    COMMIT;

    -- 결과 확인
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 80800   |

    ```sql
    SELECT id, message, created_at FROM temp_log
    ORDER BY id DESC LIMIT 3;
    ```

    | id  | message                        | created_at          |
    |-----|--------------------------------|---------------------|
    | ... | 환불 완료 - 김철수 +50,000원   | 2025-...            |
    | ... | 주문 취소 요청 - 고객: 김철수  | 2025-...            |
    | ... | 김철수 50,000원 결제 - 잔액... | 2025-...            |


---


### 문제 15

**정리: 트랜잭션 연습에서 만든 모든 임시 테이블을 삭제하세요.** 삭제 자체도 하나의 트랜잭션으로 묶으세요.


??? tip "힌트"
    SQLite에서는 DDL도 트랜잭션에 포함됩니다. `BEGIN` → `DROP TABLE` 여러 번 → `COMMIT`이 가능합니다.


??? success "정답"
    ```sql
    -- 삭제 전 목록 확인
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%'
    ORDER BY name;

    BEGIN;

    DROP TABLE IF EXISTS temp_grade;
    DROP TABLE IF EXISTS temp_log;
    DROP TABLE IF EXISTS temp_account;

    COMMIT;

    -- 삭제 확인
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%';
    ```

    (0행 — 모두 삭제됨)

    !!! tip "트랜잭션 핵심 요약"
        | 명령어 | 역할 |
        |--------|------|
        | `BEGIN` | 트랜잭션 시작 |
        | `COMMIT` | 변경사항 영구 반영 |
        | `ROLLBACK` | 변경사항 전체 취소 |
        | `SAVEPOINT name` | 중간 저장점 생성 |
        | `ROLLBACK TO name` | 해당 저장점까지만 취소 |
        | `RELEASE SAVEPOINT name` | 저장점 해제 (롤백 불가) |
