# DDL/제약조건

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    직접 테이블을 생성/수정/삭제하는 실습 (기존 테이블 참조 없음)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`, 제약조건 (`PRIMARY KEY`, `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`, `FOREIGN KEY`)

</div>

---


## 기초 (1~5): CREATE TABLE과 제약조건


### 문제 1

**기본 테이블을 만드세요.** 아래 요구사항으로 `temp_memo` 테이블을 생성하세요.

- `id`: 정수, 자동증가 기본키
- `title`: 텍스트, NOT NULL
- `content`: 텍스트, NULL 허용
- `created_at`: 텍스트, NOT NULL, 기본값 현재시각


??? tip "힌트"
    `INTEGER PRIMARY KEY AUTOINCREMENT`로 자동증가 PK를, `DEFAULT CURRENT_TIMESTAMP`로 기본값을 설정합니다.


??? success "정답"
    ```sql
    CREATE TABLE temp_memo (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        title      TEXT NOT NULL,
        content    TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    -- 확인
    PRAGMA table_info(temp_memo);
    ```

    | cid | name       | type    | notnull | dflt_value        | pk |
    |-----|------------|---------|---------|-------------------|----|
    | 0   | id         | INTEGER | 0       |                   | 1  |
    | 1   | title      | TEXT    | 1       |                   | 0  |
    | 2   | content    | TEXT    | 0       |                   | 0  |
    | 3   | created_at | TEXT    | 1       | CURRENT_TIMESTAMP | 0  |


---


### 문제 2

**UNIQUE 제약조건이 있는 테이블을 만드세요.** `temp_tag` 테이블을 생성하세요.

- `id`: 정수, 자동증가 기본키
- `name`: 텍스트, NOT NULL, UNIQUE


??? tip "힌트"
    칼럼 정의 뒤에 `UNIQUE`를 붙이면 해당 칼럼에 중복 값이 들어갈 수 없습니다.


??? success "정답"
    ```sql
    CREATE TABLE temp_tag (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );

    -- 삽입 테스트
    INSERT INTO temp_tag (name) VALUES ('전자제품');
    INSERT INTO temp_tag (name) VALUES ('주변기기');

    -- 중복 삽입 시도 → 에러 발생
    -- INSERT INTO temp_tag (name) VALUES ('전자제품');

    SELECT * FROM temp_tag;
    ```

    | id | name     |
    |----|----------|
    | 1  | 전자제품 |
    | 2  | 주변기기 |


---


### 문제 3

**CHECK 제약조건을 사용하세요.** `temp_product` 테이블을 생성하세요.

- `id`: 정수, 자동증가 기본키
- `name`: 텍스트, NOT NULL
- `price`: 실수, NOT NULL, 0 이상
- `stock_qty`: 정수, NOT NULL, 0 이상, 기본값 0


??? tip "힌트"
    `CHECK(price >= 0)`과 `CHECK(stock_qty >= 0)`으로 음수를 방지합니다.


??? success "정답"
    ```sql
    CREATE TABLE temp_product (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT NOT NULL,
        price     REAL NOT NULL CHECK(price >= 0),
        stock_qty INTEGER NOT NULL DEFAULT 0 CHECK(stock_qty >= 0)
    );

    -- 정상 삽입
    INSERT INTO temp_product (name, price, stock_qty) VALUES ('키보드', 89000, 50);

    -- CHECK 위반 테스트 (주석 해제 시 에러)
    -- INSERT INTO temp_product (name, price, stock_qty) VALUES ('마우스', -5000, 10);

    SELECT * FROM temp_product;
    ```

    | id | name   | price | stock_qty |
    |----|--------|-------|-----------|
    | 1  | 키보드 | 89000 | 50        |


---


### 문제 4

**NOT NULL과 DEFAULT를 적절히 조합하세요.** `temp_customer` 테이블을 생성하세요.

- `id`: 정수, 자동증가 기본키
- `name`: 텍스트, NOT NULL
- `email`: 텍스트, NOT NULL, UNIQUE
- `grade`: 텍스트, NOT NULL, 기본값 `'BRONZE'`, `CHECK(grade IN ('BRONZE','SILVER','GOLD','VIP'))`
- `is_active`: 정수, NOT NULL, 기본값 1


??? tip "힌트"
    `DEFAULT 'BRONZE'`와 `CHECK(grade IN (...))`을 함께 사용하면, 값을 생략하면 `'BRONZE'`가 들어가고, 허용 목록 외 값은 거부됩니다.


??? success "정답"
    ```sql
    CREATE TABLE temp_customer (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT NOT NULL,
        email     TEXT NOT NULL UNIQUE,
        grade     TEXT NOT NULL DEFAULT 'BRONZE'
                  CHECK(grade IN ('BRONZE','SILVER','GOLD','VIP')),
        is_active INTEGER NOT NULL DEFAULT 1
    );

    -- grade 생략 → 기본값 BRONZE 자동 적용
    INSERT INTO temp_customer (name, email) VALUES ('김테스트', 'kim@testmail.kr');

    -- grade 명시
    INSERT INTO temp_customer (name, email, grade) VALUES ('이테스트', 'lee@testmail.kr', 'GOLD');

    SELECT * FROM temp_customer;
    ```

    | id | name     | email             | grade  | is_active |
    |----|----------|-------------------|--------|-----------|
    | 1  | 김테스트 | kim@testmail.kr   | BRONZE | 1         |
    | 2  | 이테스트 | lee@testmail.kr   | GOLD   | 1         |


---


### 문제 5

**외래 키(FOREIGN KEY)가 있는 테이블을 만드세요.** `temp_order` 테이블을 생성하세요. `temp_customer`의 `id`를 참조합니다.

- `id`: 정수, 자동증가 기본키
- `customer_id`: 정수, NOT NULL, `temp_customer(id)` 참조
- `total_amount`: 실수, NOT NULL, CHECK >= 0
- `ordered_at`: 텍스트, NOT NULL


??? tip "힌트"
    SQLite에서 FK 검사를 활성화하려면 `PRAGMA foreign_keys = ON;`을 먼저 실행해야 합니다. `REFERENCES 테이블(칼럼)`으로 FK를 정의합니다.


??? success "정답"
    ```sql
    -- FK 활성화 (세션마다 필요)
    PRAGMA foreign_keys = ON;

    CREATE TABLE temp_order (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id  INTEGER NOT NULL REFERENCES temp_customer(id),
        total_amount REAL NOT NULL CHECK(total_amount >= 0),
        ordered_at   TEXT NOT NULL
    );

    -- 정상 삽입 (customer_id=1은 위에서 생성됨)
    INSERT INTO temp_order (customer_id, total_amount, ordered_at)
    VALUES (1, 150000, '2025-01-15');

    -- FK 위반 (존재하지 않는 고객) → 에러
    -- INSERT INTO temp_order (customer_id, total_amount, ordered_at)
    -- VALUES (999, 50000, '2025-01-15');

    SELECT * FROM temp_order;
    ```

    | id | customer_id | total_amount | ordered_at |
    |----|-------------|--------------|------------|
    | 1  | 1           | 150000       | 2025-01-15 |


---


## 응용 (6~10): ALTER TABLE, 복합 키, ON DELETE


### 문제 6

**기존 테이블에 칼럼을 추가하세요.** `temp_product` 테이블에 `brand` 칼럼(TEXT, NOT NULL, 기본값 `'미정'`)과 `weight_grams` 칼럼(INTEGER, NULL 허용)을 추가하세요.


??? tip "힌트"
    SQLite의 `ALTER TABLE ... ADD COLUMN`은 한 번에 칼럼 하나만 추가합니다. 두 번 실행하세요.


??? success "정답"
    ```sql
    ALTER TABLE temp_product ADD COLUMN brand TEXT NOT NULL DEFAULT '미정';
    ALTER TABLE temp_product ADD COLUMN weight_grams INTEGER;

    -- 확인
    PRAGMA table_info(temp_product);
    ```

    | cid | name         | type    | notnull | dflt_value | pk |
    |-----|--------------|---------|---------|------------|----|
    | 0   | id           | INTEGER | 0       |            | 1  |
    | 1   | name         | TEXT    | 1       |            | 0  |
    | 2   | price        | REAL    | 1       |            | 0  |
    | 3   | stock_qty    | INTEGER | 1       | 0          | 0  |
    | 4   | brand        | TEXT    | 1       | '미정'     | 0  |
    | 5   | weight_grams | INTEGER | 0       |            | 0  |


---


### 문제 7

**테이블 이름을 변경하세요.** `temp_memo`를 `temp_note`로 이름을 바꾸세요. 그리고 테이블 목록에서 확인하세요.


??? tip "힌트"
    `ALTER TABLE old_name RENAME TO new_name`을 사용합니다.


??? success "정답"
    ```sql
    ALTER TABLE temp_memo RENAME TO temp_note;

    -- 변경 확인 (temp_memo는 사라지고 temp_note가 생김)
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%'
    ORDER BY name;
    ```

    | name          |
    |---------------|
    | temp_customer |
    | temp_note     |
    | temp_order    |
    | temp_product  |
    | temp_tag      |


---


### 문제 8

**ON DELETE CASCADE를 체험하세요.** `temp_order_item` 테이블을 생성하되, `temp_order`가 삭제되면 관련 아이템도 자동 삭제되도록 설정하세요.

- `id`: 정수, 자동증가 기본키
- `order_id`: 정수, NOT NULL, `temp_order(id)` 참조, ON DELETE CASCADE
- `product_name`: 텍스트, NOT NULL
- `quantity`: 정수, NOT NULL, CHECK > 0


??? tip "힌트"
    `REFERENCES temp_order(id) ON DELETE CASCADE`로 부모 삭제 시 자식 자동 삭제. `PRAGMA foreign_keys = ON`이 필수입니다.


??? success "정답"
    ```sql
    PRAGMA foreign_keys = ON;

    CREATE TABLE temp_order_item (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id     INTEGER NOT NULL
                     REFERENCES temp_order(id) ON DELETE CASCADE,
        product_name TEXT NOT NULL,
        quantity     INTEGER NOT NULL CHECK(quantity > 0)
    );

    -- 데이터 삽입
    INSERT INTO temp_order_item (order_id, product_name, quantity)
    VALUES (1, '키보드', 2);
    INSERT INTO temp_order_item (order_id, product_name, quantity)
    VALUES (1, '마우스', 1);

    -- 삽입 확인
    SELECT * FROM temp_order_item;

    -- 부모 주문 삭제 → 아이템도 자동 삭제
    DELETE FROM temp_order WHERE id = 1;

    -- 삭제 확인 (0행이어야 함)
    SELECT * FROM temp_order_item;
    ```

    삭제 전:

    | id | order_id | product_name | quantity |
    |----|----------|--------------|----------|
    | 1  | 1        | 키보드       | 2        |
    | 2  | 1        | 마우스       | 1        |

    삭제 후: (0행)


---


### 문제 9

**ON DELETE SET NULL을 체험하세요.** `temp_task` 테이블을 생성하세요. 담당자(`assignee_id`)가 삭제되어도 업무 기록은 남기되, 담당자만 NULL로 바뀌도록 설정하세요.

- `id`: 정수, 자동증가 기본키
- `title`: 텍스트, NOT NULL
- `assignee_id`: 정수, NULL 허용, `temp_customer(id)` 참조, ON DELETE SET NULL


??? tip "힌트"
    `ON DELETE SET NULL`은 부모가 삭제되면 자식의 FK 칼럼을 NULL로 변경합니다. FK 칼럼이 `NOT NULL`이면 사용할 수 없습니다.


??? success "정답"
    ```sql
    PRAGMA foreign_keys = ON;

    CREATE TABLE temp_task (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT NOT NULL,
        assignee_id INTEGER
                    REFERENCES temp_customer(id) ON DELETE SET NULL
    );

    -- 데이터 삽입
    INSERT INTO temp_task (title, assignee_id) VALUES ('재고 확인', 1);
    INSERT INTO temp_task (title, assignee_id) VALUES ('배송 처리', 2);

    SELECT t.id, t.title, t.assignee_id, c.name
    FROM temp_task t
    LEFT JOIN temp_customer c ON t.assignee_id = c.id;

    -- 고객 1번 삭제 (연관된 temp_order가 있으면 먼저 삭제)
    DELETE FROM temp_order_item WHERE order_id IN (SELECT id FROM temp_order WHERE customer_id = 1);
    DELETE FROM temp_order WHERE customer_id = 1;
    DELETE FROM temp_customer WHERE id = 1;

    -- assignee_id가 NULL로 변경됨
    SELECT t.id, t.title, t.assignee_id
    FROM temp_task t;
    ```

    삭제 후:

    | id | title     | assignee_id |
    |----|-----------|-------------|
    | 1  | 재고 확인 |             |
    | 2  | 배송 처리 | 2           |


---


### 문제 10

**복합 PRIMARY KEY를 사용하세요.** 상품-태그 관계 테이블 `temp_product_tag`를 생성하세요. (product_id, tag_id) 조합이 PK입니다.

- `product_id`: 정수, NOT NULL
- `tag_id`: 정수, NOT NULL
- PRIMARY KEY는 (product_id, tag_id)


??? tip "힌트"
    `AUTOINCREMENT`가 아닌 복합 PK는 칼럼 정의가 아니라 테이블 제약으로 선언합니다: `PRIMARY KEY (col1, col2)`.


??? success "정답"
    ```sql
    CREATE TABLE temp_product_tag (
        product_id INTEGER NOT NULL,
        tag_id     INTEGER NOT NULL,
        PRIMARY KEY (product_id, tag_id)
    );

    -- 삽입
    INSERT INTO temp_product_tag VALUES (1, 10);
    INSERT INTO temp_product_tag VALUES (1, 20);
    INSERT INTO temp_product_tag VALUES (2, 10);

    -- 동일 조합 중복 삽입 → 에러
    -- INSERT INTO temp_product_tag VALUES (1, 10);

    SELECT * FROM temp_product_tag;
    ```

    | product_id | tag_id |
    |------------|--------|
    | 1          | 10     |
    | 1          | 20     |
    | 2          | 10     |


---


## 실전 (11~15): 설계, CTAS, 오류 수정


### 문제 11

**아래 CREATE TABLE 문에는 오류가 3개 있습니다. 모두 찾아 수정하세요.**

```sql
CREATE TABLE temp_employee (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    salary REAL CHECK(salary > 0),
    department TEXT DEFAULT,
    hired_at TEXT NOT NULL
);
```


??? tip "힌트"
    1. `AUTOINCREMENT`의 위치가 올바른지 확인하세요.
    2. `name`에 NOT NULL이 빠져 있다면 이름 없는 직원이 가능합니다.
    3. `DEFAULT` 뒤에 기본값이 없습니다.


??? success "정답"
    ```sql
    -- 오류 3개:
    -- 1) AUTOINCREMENT는 PRIMARY KEY 뒤에 와야 함
    --    → INTEGER PRIMARY KEY AUTOINCREMENT
    -- 2) name에 NOT NULL 누락 (이름은 필수)
    -- 3) DEFAULT 뒤에 값이 없음 (구문 오류)
    --    → DEFAULT '미배정' 등으로 수정

    CREATE TABLE temp_employee (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        email      TEXT UNIQUE,
        salary     REAL CHECK(salary > 0),
        department TEXT DEFAULT '미배정',
        hired_at   TEXT NOT NULL
    );

    -- 테스트
    INSERT INTO temp_employee (name, hired_at)
    VALUES ('테스트 직원', '2025-01-01');

    SELECT * FROM temp_employee;
    ```

    | id | name        | email | salary | department | hired_at   |
    |----|-------------|-------|--------|------------|------------|
    | 1  | 테스트 직원 |       |        | 미배정     | 2025-01-01 |


---


### 문제 12

**CTAS (CREATE TABLE AS SELECT)로 2024년 주문 요약 테이블을 만드세요.** `orders`에서 고객별 주문 건수, 총 결제금액, 평균 결제금액을 계산한 `temp_order_summary_2024` 테이블을 생성하세요.


??? tip "힌트"
    `CREATE TABLE 이름 AS SELECT ...`는 SELECT 결과를 새 테이블로 저장합니다. `WHERE ordered_at LIKE '2024%'`로 2024년만 필터링하세요.


??? success "정답"
    ```sql
    CREATE TABLE temp_order_summary_2024 AS
    SELECT
        c.id AS customer_id,
        c.name AS customer_name,
        COUNT(o.id) AS order_count,
        SUM(o.total_amount) AS total_spent,
        ROUND(AVG(o.total_amount)) AS avg_order_amount
    FROM customers c
    INNER JOIN orders o ON c.id = o.customer_id
    WHERE o.ordered_at LIKE '2024%'
    GROUP BY c.id, c.name;

    -- 확인 (상위 5건)
    SELECT * FROM temp_order_summary_2024
    ORDER BY total_spent DESC
    LIMIT 5;
    ```

    | customer_id | customer_name | order_count | total_spent | avg_order_amount |
    |-------------|---------------|-------------|-------------|------------------|
    | ...         | ...           | ...         | ...         | ...              |

    !!! note
        CTAS로 만든 테이블에는 PK, FK, CHECK 등 제약조건이 복사되지 않습니다. 필요하면 별도로 추가해야 합니다.


---


### 문제 13

**DELETE vs DROP TABLE vs 테이블 재생성을 비교하세요.** `temp_tag` 테이블의 데이터를 모두 삭제하되, 테이블 구조는 유지하는 방법과 테이블 자체를 삭제하는 방법을 각각 실행하세요.

!!! info "참고"
    SQLite에는 `TRUNCATE TABLE` 명령이 없습니다. 대신 `DELETE FROM`을 사용합니다. MySQL/PostgreSQL에서는 `TRUNCATE TABLE`을 사용할 수 있으며, DELETE보다 빠릅니다 (행 단위 삭제가 아닌 테이블 초기화).


??? tip "힌트"
    - 데이터만 삭제: `DELETE FROM 테이블;`
    - 테이블 삭제: `DROP TABLE 테이블;`
    - 안전 삭제: `DROP TABLE IF EXISTS 테이블;`


??? success "정답"
    ```sql
    -- 1) 데이터만 삭제 (구조 유지)
    DELETE FROM temp_tag;

    -- 테이블은 남아 있음
    SELECT COUNT(*) AS cnt FROM temp_tag;
    -- cnt = 0

    -- 2) 테이블 자체를 삭제
    DROP TABLE temp_tag;

    -- 더 이상 조회 불가 (에러)
    -- SELECT * FROM temp_tag;

    -- 3) 안전한 삭제 (이미 없어도 에러 안 남)
    DROP TABLE IF EXISTS temp_tag;
    ```

    !!! tip "TRUNCATE vs DELETE (다른 DB)"
        | 항목 | DELETE FROM | TRUNCATE TABLE |
        |------|------------|----------------|
        | 속도 | 느림 (행 단위) | 빠름 (테이블 초기화) |
        | WHERE 조건 | 가능 | 불가 |
        | 트랜잭션 롤백 | 가능 | DB마다 다름 |
        | 자동증가 초기화 | 안 됨 | 초기화됨 (MySQL) |
        | SQLite 지원 | O | X |


---


### 문제 14

**요구사항을 보고 테이블을 설계하세요.** 아래 비즈니스 요구사항을 만족하는 `temp_coupon` 테이블을 만드세요.

요구사항:

1. 쿠폰 코드는 유일해야 합니다
2. 쿠폰 유형은 `'percent'` 또는 `'fixed'`만 허용합니다
3. 할인 값은 양수여야 합니다
4. 최소 주문 금액은 선택사항이며, 설정 시 0 이상이어야 합니다
5. 유효기간(시작일, 종료일)은 필수입니다
6. 활성 여부는 기본값 1(활성)입니다


??? tip "힌트"
    각 요구사항을 제약조건으로 매핑하세요: 유일 → `UNIQUE`, 허용 목록 → `CHECK IN`, 양수 → `CHECK > 0`, 선택 → NULL 허용, 필수 → `NOT NULL`, 기본값 → `DEFAULT`.


??? success "정답"
    ```sql
    CREATE TABLE temp_coupon (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        code             TEXT NOT NULL UNIQUE,                          -- 요구1: 유일
        type             TEXT NOT NULL CHECK(type IN ('percent','fixed')), -- 요구2: 허용 유형
        discount_value   REAL NOT NULL CHECK(discount_value > 0),      -- 요구3: 양수
        min_order_amount REAL CHECK(min_order_amount >= 0),            -- 요구4: 선택, 0 이상
        is_active        INTEGER NOT NULL DEFAULT 1,                   -- 요구6: 기본 활성
        started_at       TEXT NOT NULL,                                -- 요구5: 필수
        expired_at       TEXT NOT NULL                                 -- 요구5: 필수
    );

    -- 테스트
    INSERT INTO temp_coupon (code, type, discount_value, min_order_amount, started_at, expired_at)
    VALUES ('WELCOME10', 'percent', 10, 50000, '2025-01-01', '2025-12-31');

    INSERT INTO temp_coupon (code, type, discount_value, started_at, expired_at)
    VALUES ('FLAT5000', 'fixed', 5000, '2025-06-01', '2025-06-30');

    SELECT * FROM temp_coupon;
    ```

    | id | code      | type    | discount_value | min_order_amount | is_active | started_at | expired_at |
    |----|-----------|---------|----------------|------------------|-----------|------------|------------|
    | 1  | WELCOME10 | percent | 10             | 50000            | 1         | 2025-01-01 | 2025-12-31 |
    | 2  | FLAT5000  | fixed   | 5000           |                  | 1         | 2025-06-01 | 2025-06-30 |


---


### 문제 15

**정리: 이번 연습에서 만든 모든 임시 테이블을 삭제하세요.** `sqlite_master`에서 `temp_`로 시작하는 테이블을 조회한 뒤 모두 DROP하세요.


??? tip "힌트"
    먼저 `SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'temp_%'`로 목록을 확인하고, 각각 `DROP TABLE IF EXISTS`로 삭제합니다. FK 참조 순서에 주의하세요 (자식 먼저 삭제).


??? success "정답"
    ```sql
    -- 1) 현재 temp_ 테이블 목록 확인
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%'
    ORDER BY name;

    -- 2) FK 참조 관계를 고려하여 자식 → 부모 순서로 삭제
    DROP TABLE IF EXISTS temp_order_item;
    DROP TABLE IF EXISTS temp_product_tag;
    DROP TABLE IF EXISTS temp_task;
    DROP TABLE IF EXISTS temp_order;
    DROP TABLE IF EXISTS temp_order_summary_2024;
    DROP TABLE IF EXISTS temp_customer;
    DROP TABLE IF EXISTS temp_product;
    DROP TABLE IF EXISTS temp_employee;
    DROP TABLE IF EXISTS temp_coupon;
    DROP TABLE IF EXISTS temp_note;
    DROP TABLE IF EXISTS temp_tag;

    -- 3) 삭제 확인 (0행이어야 함)
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%';
    ```

    !!! tip "PostgreSQL의 SEQUENCE"
        PostgreSQL에서는 `SERIAL`이나 `GENERATED ALWAYS AS IDENTITY`로 자동증가를 구현합니다. 내부적으로 시퀀스(SEQUENCE) 객체가 생성되며, `nextval()`, `currval()`, `setval()`로 직접 제어할 수도 있습니다. SQLite의 `AUTOINCREMENT`와 달리 시퀀스는 독립 객체여서 여러 테이블이 공유할 수도 있습니다.
