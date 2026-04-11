# Transactions

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `orders` — Orders<br>
    `products` — Products<br>
    `customers` — Customers<br>
    `payments` — Payments (copied to temp tables for practice)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    `BEGIN`<br>
    `COMMIT`<br>
    `ROLLBACK`<br>
    `SAVEPOINT`<br>
    `RELEASE`<br>
    Atomicity<br>
    Concurrency control

</div>

!!! warning "Before You Begin"
    Transaction exercises **modify actual data**. Use temporary tables for safe practice. All problems in this exercise are designed to not affect original data by using temporary tables or ROLLBACK.

---


## Basic (1~5): BEGIN, COMMIT, ROLLBACK


### Problem 1

**Execute the most basic transaction.** Create a temporary table `temp_account`, INSERT two accounts, and COMMIT.


??? tip "Hint"
    `BEGIN;` -> 2 INSERT statements -> `COMMIT;`. Changes are not visible to other connections until COMMIT.


??? success "Answer"
    ```sql
    -- Setup: temporary table
    CREATE TABLE temp_account (
        id      INTEGER PRIMARY KEY,
        name    TEXT NOT NULL,
        balance INTEGER NOT NULL DEFAULT 0
    );

    -- Begin transaction
    BEGIN;

    INSERT INTO temp_account (id, name, balance) VALUES (1, '김철수', 100000);
    INSERT INTO temp_account (id, name, balance) VALUES (2, '이영희', 200000);

    -- Commit -> permanently saved
    COMMIT;

    SELECT * FROM temp_account;
    ```

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 100000  |
    | 2  | 이영희 | 200000  |


---


### Problem 2

**Use ROLLBACK to undo changes.** Accidentally set 김철수's balance to 0 in `temp_account`, then ROLLBACK to recover.


??? tip "Hint"
    `BEGIN;` -> UPDATE -> verify result -> `ROLLBACK;` -> verify recovery. ROLLBACK undoes all changes since BEGIN.


??? success "Answer"
    ```sql
    -- Check before change
    SELECT * FROM temp_account WHERE id = 1;

    BEGIN;

    -- Mistake! Set balance to 0
    UPDATE temp_account SET balance = 0 WHERE id = 1;

    -- Check damage
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    -- balance = 0

    -- Undo
    ROLLBACK;

    -- Verify recovery
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```

    After ROLLBACK:

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 100000  |


---


### Problem 3

**Verify atomicity.** Simulate a bank transfer: 김철수 -> 이영희, 30,000 won. Wrap withdrawal and deposit in a single transaction and verify both balances after transfer.


??? tip "Hint"
    Two UPDATEs inside a transaction: one `balance - 30000`, the other `balance + 30000`. Both must succeed before COMMIT.


??? success "Answer"
    ```sql
    -- Check balances before transfer
    SELECT id, name, balance FROM temp_account;

    BEGIN;

    -- Withdrawal
    UPDATE temp_account SET balance = balance - 30000 WHERE id = 1;

    -- Deposit
    UPDATE temp_account SET balance = balance + 30000 WHERE id = 2;

    COMMIT;

    -- Check balances after transfer
    SELECT id, name, balance FROM temp_account;
    ```

    Before transfer:

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 100000  |
    | 2  | 이영희 | 200000  |

    After transfer:

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 70000   |
    | 2  | 이영희 | 230000  |


---


### Problem 4

**ROLLBACK on failure.** Attempt to transfer 500,000 won (more than 김철수's balance of 70,000). Check for insufficient funds and ROLLBACK.


??? tip "Hint"
    After the UPDATE, check with SELECT if balance is negative. If negative, ROLLBACK. In real applications, this decision is made in program code.


??? success "Answer"
    ```sql
    BEGIN;

    -- Attempt withdrawal (exceeds balance)
    UPDATE temp_account SET balance = balance - 500000 WHERE id = 1;

    -- Check balance -> negative!
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    -- balance = -430000

    -- Insufficient funds -> cancel everything
    ROLLBACK;

    -- Verify original balance maintained
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```

    After ROLLBACK:

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 70000   |


---


### Problem 5

**Bundle multiple INSERTs in a transaction to understand performance.** Understand the difference when INSERTing 100 log records into `temp_log` with and without transactions.


??? tip "Hint"
    In SQLite, INSERT without a transaction triggers disk writes (fsync) for every row. Wrapping with `BEGIN`/`COMMIT` results in only one write.


??? success "Answer"
    ```sql
    CREATE TABLE temp_log (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        message    TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    -- INSERT wrapped in a transaction (fast)
    BEGIN;

    INSERT INTO temp_log (message) VALUES ('Log 1');
    INSERT INTO temp_log (message) VALUES ('Log 2');
    INSERT INTO temp_log (message) VALUES ('Log 3');
    -- ... in practice, insert 100 rows
    INSERT INTO temp_log (message) VALUES ('Log 100');

    COMMIT;

    SELECT COUNT(*) AS total FROM temp_log;
    ```

    | total |
    |-------|
    | 4     |

    !!! info "Why are transactions faster?"
        Without a transaction, SQLite performs a WAL/journal write + fsync for every row. 100 rows means 100 disk syncs. Wrapping in a transaction means **only 1 sync**, which can be dozens of times faster.


---


## Applied (6~10): SAVEPOINT and Multi-step Transactions


### Problem 6

**Use SAVEPOINT for partial rollback.** Add 3 accounts, but treat the 3rd insertion as a mistake and use SAVEPOINT to keep only the first 2.


??? tip "Hint"
    `SAVEPOINT sp1;` -> INSERT -> `SAVEPOINT sp2;` -> INSERT -> ... `ROLLBACK TO sp2;` undoes only changes after sp2.


??? success "Answer"
    ```sql
    BEGIN;

    INSERT INTO temp_account (id, name, balance) VALUES (3, '박민수', 150000);

    SAVEPOINT sp_after_park;

    INSERT INTO temp_account (id, name, balance) VALUES (4, '정수연', 80000);

    SAVEPOINT sp_after_jung;

    -- Mistake! Bad data
    INSERT INTO temp_account (id, name, balance) VALUES (5, '오류데이터', -999);

    -- Undo only the 3rd insert (keep up to 정수연)
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


### Problem 7

**Use nested SAVEPOINTs.** Roll back to a specific point across multiple stages of data modifications.

Scenario:
1. 김철수 balance +10,000 -> SAVEPOINT A
2. 이영희 balance +20,000 -> SAVEPOINT B
3. 박민수 balance -50,000 (mistake) -> ROLLBACK TO B
4. 박민수 balance +5,000 (correction) -> COMMIT


??? tip "Hint"
    SAVEPOINTs are identified by name. `ROLLBACK TO B` undoes only changes after B and preserves changes between A and B.


??? success "Answer"
    ```sql
    -- Check before changes
    SELECT id, name, balance FROM temp_account ORDER BY id;

    BEGIN;

    -- Step 1: 김철수 +10,000
    UPDATE temp_account SET balance = balance + 10000 WHERE id = 1;
    SAVEPOINT sp_a;

    -- Step 2: 이영희 +20,000
    UPDATE temp_account SET balance = balance + 20000 WHERE id = 2;
    SAVEPOINT sp_b;

    -- Step 3: Mistake! 박민수 -50,000
    UPDATE temp_account SET balance = balance - 50000 WHERE id = 3;

    -- Undo step 3 (rollback only after sp_b)
    ROLLBACK TO sp_b;

    -- Step 3 correction: 박민수 +5,000
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


### Problem 8

**Implement batch processing with SAVEPOINTs.** Apply 1% interest to all accounts, but cancel interest for any account with balance under 100 won.


??? tip "Hint"
    Set a SAVEPOINT for each account, UPDATE, then check the condition for individual rollback. Here we apply to all accounts at once then verify.


??? success "Answer"
    ```sql
    -- Check before interest
    SELECT id, name, balance FROM temp_account ORDER BY id;

    BEGIN;

    SAVEPOINT sp_before_interest;

    -- Apply 1% interest to all (integer processing)
    UPDATE temp_account
    SET balance = balance + CAST(balance * 0.01 AS INTEGER);

    -- Verify results
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


### Problem 9

**Understand RELEASE SAVEPOINT.** Create a SAVEPOINT, and once normal processing is confirmed, RELEASE it to remove the savepoint.


??? tip "Hint"
    `RELEASE SAVEPOINT sp1;` removes that SAVEPOINT. After that, `ROLLBACK TO sp1` is no longer possible. RELEASE is not COMMIT -- the outer transaction is still in progress.


??? success "Answer"
    ```sql
    BEGIN;

    -- Add new account
    INSERT INTO temp_account (id, name, balance) VALUES (5, '최지우', 300000);
    SAVEPOINT sp_insert;

    -- Normal confirmed -> release savepoint
    RELEASE SAVEPOINT sp_insert;
    -- After this point, ROLLBACK TO sp_insert would error

    -- Additional work
    UPDATE temp_account SET balance = balance + 1000 WHERE id = 5;

    COMMIT;

    SELECT * FROM temp_account WHERE id = 5;
    ```

    | id | name   | balance |
    |----|--------|---------|
    | 5  | 최지우 | 301000  |


---


### Problem 10

**Verify DDL behavior within transactions.** What happens if you create a table and insert data inside a transaction, then ROLLBACK?

!!! info "Note"
    In SQLite, DDL (CREATE TABLE, DROP TABLE) is included in transactions. In MySQL/Oracle, DDL triggers an implicit COMMIT making rollback impossible.


??? tip "Hint"
    In SQLite, `BEGIN` -> `CREATE TABLE` -> `INSERT` -> `ROLLBACK` cancels the table creation itself.


??? success "Answer"
    ```sql
    BEGIN;

    CREATE TABLE temp_will_vanish (
        id   INTEGER PRIMARY KEY,
        data TEXT
    );

    INSERT INTO temp_will_vanish VALUES (1, '사라질 데이터');

    -- Cancel everything (including table creation)
    ROLLBACK;

    -- Table does not exist (error)
    -- SELECT * FROM temp_will_vanish;

    -- Verify
    SELECT COUNT(*) AS cnt
    FROM sqlite_master
    WHERE name = 'temp_will_vanish';
    ```

    | cnt |
    |-----|
    | 0   |

    !!! warning "DDL Transaction Behavior Varies by DB"
        | DB | DDL Rollback? |
        |---|---|
        | SQLite | Yes (full support) |
        | PostgreSQL | Yes (full support) |
        | MySQL | No (implicit COMMIT) |
        | Oracle | No (implicit COMMIT) |
        | SQL Server | Yes (full support) |


---


## Advanced (11~15): Business Scenarios


### Problem 11

**Implement an order processing transaction.** Process the following as a single transaction:

1. Deduct 50,000 won from 김철수's (id=1) balance in `temp_account`
2. Insert a transaction record into `temp_log`
3. If balance goes negative after deduction, ROLLBACK everything


??? tip "Hint"
    UPDATE -> verify balance with SELECT -> if negative, ROLLBACK; if positive, INSERT + COMMIT. In SQLite without a programming language, conditional branching is difficult, so verify manually.


??? success "Answer"
    ```sql
    -- Check current balance
    SELECT balance FROM temp_account WHERE id = 1;
    -- 80800

    BEGIN;

    -- 1) Deduct balance
    UPDATE temp_account SET balance = balance - 50000 WHERE id = 1;

    -- 2) Check balance
    SELECT balance FROM temp_account WHERE id = 1;
    -- 30800 (positive -> OK)

    -- 3) Transaction record
    INSERT INTO temp_log (message)
    VALUES ('김철수 50,000원 결제 - 잔액: 30800');

    COMMIT;

    -- Verify result
    SELECT id, name, balance FROM temp_account WHERE id = 1;
    ```

    | id | name   | balance |
    |----|--------|---------|
    | 1  | 김철수 | 30800   |


---


### Problem 12

**Implement a point transfer transaction.** Transfer 50,000 points from 이영희 (id=2) to 박민수 (id=3). Use SAVEPOINT to complete the transfer including the record.


??? tip "Hint"
    Withdrawal -> SAVEPOINT -> Deposit -> Transfer record -> COMMIT. If deposit fails, roll back to SAVEPOINT.


??? success "Answer"
    ```sql
    BEGIN;

    -- 1) Withdrawal
    UPDATE temp_account SET balance = balance - 50000 WHERE id = 2;
    SAVEPOINT sp_withdrawal;

    -- 2) Check balance (must be positive)
    SELECT balance FROM temp_account WHERE id = 2;
    -- 202500 (positive -> OK)

    -- 3) Deposit
    UPDATE temp_account SET balance = balance + 50000 WHERE id = 3;

    -- 4) Transfer record
    INSERT INTO temp_log (message)
    VALUES ('이영희 → 박민수 50,000 이체');

    COMMIT;

    -- Verify results
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


### Problem 13

**Process a bulk grade update with a transaction.** Create a `temp_grade` table that assigns grades based on balance from `temp_account`, processed within a transaction.

Grade criteria:
- Balance >= 200,000: VIP
- Balance >= 100,000: GOLD
- Otherwise: SILVER


??? tip "Hint"
    First create `temp_grade` table, then `BEGIN` -> `DELETE` (clear existing data) -> `INSERT ... SELECT` for grade calculation -> `COMMIT`.


??? success "Answer"
    ```sql
    CREATE TABLE temp_grade (
        account_id INTEGER PRIMARY KEY,
        name       TEXT NOT NULL,
        grade      TEXT NOT NULL,
        balance    INTEGER NOT NULL
    );

    BEGIN;

    -- Clear existing grades (for re-execution)
    DELETE FROM temp_grade;

    -- Assign grades based on balance
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


### Problem 14

**Complex business scenario: implement order cancellation processing.** Process the following as a single transaction:

1. Record cancellation request in `temp_log`
2. Refund 50,000 won to 김철수 (id=1) (balance +50,000)
3. Record refund completion in `temp_log`

If any step fails, the entire operation must be cancelled.


??? tip "Hint"
    Using SAVEPOINTs at each step makes it easier to identify where failures occurred. COMMIT if everything is fine.


??? success "Answer"
    ```sql
    BEGIN;

    SAVEPOINT sp_step1;

    -- Step 1: Cancellation request record
    INSERT INTO temp_log (message) VALUES ('주문 취소 요청 - 고객: 김철수');

    SAVEPOINT sp_step2;

    -- Step 2: Refund processing
    UPDATE temp_account SET balance = balance + 50000 WHERE id = 1;

    SAVEPOINT sp_step3;

    -- Step 3: Refund completion record
    INSERT INTO temp_log (message) VALUES ('환불 완료 - 김철수 +50,000원');

    -- All normal -> commit
    COMMIT;

    -- Verify results
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


### Problem 15

**Cleanup: Drop all temporary tables created in the transaction exercises.** Wrap the deletion itself in a single transaction.


??? tip "Hint"
    In SQLite, DDL is included in transactions. `BEGIN` -> `DROP TABLE` multiple times -> `COMMIT` is possible.


??? success "Answer"
    ```sql
    -- Check list before deletion
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%'
    ORDER BY name;

    BEGIN;

    DROP TABLE IF EXISTS temp_grade;
    DROP TABLE IF EXISTS temp_log;
    DROP TABLE IF EXISTS temp_account;

    COMMIT;

    -- Verify deletion
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%';
    ```

    (0 rows -- all deleted)

    !!! tip "Transaction Key Summary"
        | Command | Purpose |
        |---------|---------|
        | `BEGIN` | Start transaction |
        | `COMMIT` | Permanently save changes |
        | `ROLLBACK` | Undo all changes |
        | `SAVEPOINT name` | Create intermediate save point |
        | `ROLLBACK TO name` | Undo only to that save point |
        | `RELEASE SAVEPOINT name` | Remove save point (rollback no longer possible) |
