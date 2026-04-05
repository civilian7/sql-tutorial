# 중급 연습: 트랜잭션

BEGIN, COMMIT, ROLLBACK을 사용하여 데이터 일관성을 보장하는 방법을 연습합니다.

> **주의:** 이 연습은 데이터를 변경합니다. `tutorial.db`를 복사한 후 사용하세요.

---

### 1. 기본 트랜잭션 — COMMIT

주문과 결제를 하나의 트랜잭션으로 묶으세요. 둘 다 성공해야 반영됩니다.

**힌트:** `BEGIN TRANSACTION` → INSERT들 → `COMMIT`으로 묶으면 전부 한꺼번에 반영됩니다. `last_insert_rowid()`로 방금 삽입한 id 참조.

??? success "실험"
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

    **핵심:** `BEGIN` ~ `COMMIT` 사이의 모든 변경이 한꺼번에 반영됩니다.

---

### 2. ROLLBACK — 되돌리기

실수로 모든 VIP 고객의 적립금을 0으로 만들었다면? ROLLBACK으로 복구합니다.

**힌트:** `BEGIN` 후 UPDATE를 실행하고 결과를 확인. 잘못되었으면 `ROLLBACK`으로 `BEGIN` 이후 모든 변경을 취소.

??? success "실험"
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

    **핵심:** `ROLLBACK`은 `BEGIN` 이후의 모든 변경을 취소합니다.

---

### 3. 에러 시 ROLLBACK

주문 삽입은 성공했지만 결제 삽입이 실패하면? 트랜잭션으로 원자성을 보장합니다.

**힌트:** 트랜잭션 안에서 하나라도 실패하면 `ROLLBACK`하여 "반쪽짜리 데이터"를 방지합니다.

??? success "실험"
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

    **핵심:** 트랜잭션 안에서 하나라도 실패하면 전체를 ROLLBACK하여 반쪽짜리 데이터를 방지합니다.

---

### 4. SAVEPOINT — 부분 롤백

긴 트랜잭션에서 일부만 되돌리고 싶을 때 SAVEPOINT를 사용합니다.

**힌트:** `SAVEPOINT 이름`으로 체크포인트 생성, `ROLLBACK TO 이름`으로 그 지점까지만 되돌리기. 이전 변경은 유지.

??? success "실험"
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

    **핵심:** `SAVEPOINT`는 트랜잭션 안에 체크포인트를 만들어 부분 롤백을 가능하게 합니다.

---

### 5. 트랜잭션 없이 vs 있을 때 비교

10,000건을 INSERT할 때 트랜잭션 유무에 따른 차이를 이해합니다.

**힌트:** 트랜잭션 없이는 매 INSERT마다 디스크 쓰기가 발생하지만, `BEGIN`~`COMMIT`으로 묶으면 한 번만 쓰기.

??? success "설명"
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

    **핵심:** SQLite에서 대량 INSERT 시 트랜잭션으로 묶으면 수십 배 빨라집니다.

---

### 6. ACID 속성 확인

현재 데이터베이스의 ACID 설정을 확인하세요.

**힌트:** `PRAGMA journal_mode`, `PRAGMA foreign_keys` 등으로 SQLite의 트랜잭션 관련 설정을 조회.

??? success "정답"
    ```sql
    -- SQLite 저널 모드 확인 (WAL이면 동시 읽기 가능)
    PRAGMA journal_mode;

    -- 자동 커밋 모드 확인
    PRAGMA auto_vacuum;

    -- 외래 키 강제 여부
    PRAGMA foreign_keys;
    ```

    **ACID란:**

    | 속성 | 의미 | 예시 |
    |------|------|------|
    | **A**tomicity (원자성) | 전부 성공 아니면 전부 실패 | 주문+결제가 함께 반영 |
    | **C**onsistency (일관성) | 트랜잭션 전후로 제약조건 유지 | 잔액이 음수가 되지 않음 |
    | **I**solation (격리성) | 동시 트랜잭션이 서로 간섭하지 않음 | 두 사용자가 동시 주문 |
    | **D**urability (지속성) | COMMIT 후 장애가 나도 데이터 보존 | 정전 후에도 데이터 유지 |

---

### 7. 재고 차감 트랜잭션

주문 시 재고를 차감하는 트랜잭션을 작성하세요. 재고가 부족하면 ROLLBACK합니다.

**힌트:** `UPDATE ... SET stock_qty = stock_qty - N WHERE stock_qty >= N`으로 재고 부족 시 변경 0행. `changes()` 함수로 확인.

??? success "정답"
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
