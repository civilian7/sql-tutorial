# DDL/제약조건

!!! info "사용 테이블"

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  



!!! abstract "학습 범위"

    `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`, `PRIMARY KEY`, `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`, `FOREIGN KEY`, `ON DELETE CASCADE`, `ON DELETE SET NULL`



### 1. 기본 테이블을 만드세요. id(자동증가 PK), title(TEXT, NOT NULL), content(TE


기본 테이블을 만드세요. id(자동증가 PK), title(TEXT, NOT NULL), content(TEXT), created_at(TEXT, NOT NULL, 기본값 현재시각)인 temp_memo 테이블을 생성하세요.


**힌트 1:** `INTEGER PRIMARY KEY AUTOINCREMENT`로 자동증가 PK를, `DEFAULT CURRENT_TIMESTAMP`로 기본값을 설정합니다.


??? success "정답"
    ```sql
    CREATE TABLE temp_memo (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        title      TEXT NOT NULL,
        content    TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    PRAGMA table_info(temp_memo);
    ```


---


### 2. UNIQUE 제약조건이 있는 temp_tag 테이블을 만드세요. id(자동증가 PK), name(TEXT, 


UNIQUE 제약조건이 있는 temp_tag 테이블을 만드세요. id(자동증가 PK), name(TEXT, NOT NULL, UNIQUE).


**힌트 1:** 칼럼 정의 뒤에 `UNIQUE`를 붙이면 해당 칼럼에 중복 값이 들어갈 수 없습니다.


??? success "정답"
    ```sql
    CREATE TABLE temp_tag (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    
    INSERT INTO temp_tag (name) VALUES ('전자제품');
    INSERT INTO temp_tag (name) VALUES ('주변기기');
    
    SELECT * FROM temp_tag;
    ```


---


### 3. CHECK 제약조건을 사용하세요. temp_product 테이블: id(PK), name(NOT NULL),


CHECK 제약조건을 사용하세요. temp_product 테이블: id(PK), name(NOT NULL), price(NOT NULL, >= 0), stock_qty(NOT NULL, >= 0, 기본값 0).


**힌트 1:** `CHECK(price >= 0)`과 `CHECK(stock_qty >= 0)`으로 음수를 방지합니다.


??? success "정답"
    ```sql
    CREATE TABLE temp_product (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT NOT NULL,
        price     REAL NOT NULL CHECK(price >= 0),
        stock_qty INTEGER NOT NULL DEFAULT 0 CHECK(stock_qty >= 0)
    );
    
    INSERT INTO temp_product (name, price, stock_qty) VALUES ('키보드', 89000, 50);
    
    SELECT * FROM temp_product;
    ```


---


### 4. NOT NULL과 DEFAULT를 조합한 temp_customer 테이블을 만드세요. grade는 기본값 '


NOT NULL과 DEFAULT를 조합한 temp_customer 테이블을 만드세요. grade는 기본값 'BRONZE', CHECK로 허용 목록 제한.


**힌트 1:** `DEFAULT 'BRONZE'`와 `CHECK(grade IN (...))`을 함께 사용하면, 값을 생략하면 'BRONZE'가 들어가고, 허용 목록 외 값은 거부됩니다.


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
    
    INSERT INTO temp_customer (name, email) VALUES ('김테스트', 'kim@testmail.kr');
    INSERT INTO temp_customer (name, email, grade) VALUES ('이테스트', 'lee@testmail.kr', 'GOLD');
    
    SELECT * FROM temp_customer;
    ```


---


### 5. 외래 키(FOREIGN KEY)가 있는 temp_order 테이블을 만드세요. temp_customer의 i


외래 키(FOREIGN KEY)가 있는 temp_order 테이블을 만드세요. temp_customer의 id를 참조합니다.


**힌트 1:** SQLite에서 FK 검사를 활성화하려면 `PRAGMA foreign_keys = ON;`을 먼저 실행해야 합니다.


??? success "정답"
    ```sql
    PRAGMA foreign_keys = ON;
    
    CREATE TABLE temp_order (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id  INTEGER NOT NULL REFERENCES temp_customer(id),
        total_amount REAL NOT NULL CHECK(total_amount >= 0),
        ordered_at   TEXT NOT NULL
    );
    
    INSERT INTO temp_order (customer_id, total_amount, ordered_at)
    VALUES (1, 150000, '2025-01-15');
    
    SELECT * FROM temp_order;
    ```


---


### 6. 기존 테이블에 칼럼을 추가하세요. temp_product에 brand(TEXT, NOT NULL, 기본값 '


기존 테이블에 칼럼을 추가하세요. temp_product에 brand(TEXT, NOT NULL, 기본값 '미정')와 weight_grams(INTEGER) 추가.


**힌트 1:** SQLite의 `ALTER TABLE ... ADD COLUMN`은 한 번에 칼럼 하나만 추가합니다. 두 번 실행하세요.


??? success "정답"
    ```sql
    ALTER TABLE temp_product ADD COLUMN brand TEXT NOT NULL DEFAULT '미정';
    ALTER TABLE temp_product ADD COLUMN weight_grams INTEGER;
    
    PRAGMA table_info(temp_product);
    ```


---


### 7. 테이블 이름을 변경하세요. temp_memo를 temp_note로 바꾸세요.


테이블 이름을 변경하세요. temp_memo를 temp_note로 바꾸세요.


**힌트 1:** `ALTER TABLE old_name RENAME TO new_name`을 사용합니다.


??? success "정답"
    ```sql
    ALTER TABLE temp_memo RENAME TO temp_note;
    
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%'
    ORDER BY name;
    ```


---


### 8. ON DELETE CASCADE를 체험하세요. temp_order_item 테이블에서 부모 주문 삭제 시 아


ON DELETE CASCADE를 체험하세요. temp_order_item 테이블에서 부모 주문 삭제 시 아이템도 자동 삭제되도록 설정하세요.


**힌트 1:** `REFERENCES temp_order(id) ON DELETE CASCADE`로 부모 삭제 시 자식 자동 삭제. `PRAGMA foreign_keys = ON`이 필수입니다.


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
    
    INSERT INTO temp_order_item (order_id, product_name, quantity)
    VALUES (1, '키보드', 2);
    INSERT INTO temp_order_item (order_id, product_name, quantity)
    VALUES (1, '마우스', 1);
    
    SELECT * FROM temp_order_item;
    
    DELETE FROM temp_order WHERE id = 1;
    
    SELECT * FROM temp_order_item;
    ```


---


### 9. ON DELETE SET NULL을 체험하세요. temp_task 테이블에서 담당자 삭제 시 담당자만 NUL


ON DELETE SET NULL을 체험하세요. temp_task 테이블에서 담당자 삭제 시 담당자만 NULL로 변경되도록 설정하세요.


**힌트 1:** `ON DELETE SET NULL`은 부모가 삭제되면 자식의 FK 칼럼을 NULL로 변경합니다. FK 칼럼이 `NOT NULL`이면 사용할 수 없습니다.


??? success "정답"
    ```sql
    PRAGMA foreign_keys = ON;
    
    CREATE TABLE temp_task (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT NOT NULL,
        assignee_id INTEGER
                    REFERENCES temp_customer(id) ON DELETE SET NULL
    );
    
    INSERT INTO temp_task (title, assignee_id) VALUES ('재고 확인', 1);
    INSERT INTO temp_task (title, assignee_id) VALUES ('배송 처리', 2);
    
    SELECT t.id, t.title, t.assignee_id, c.name
    FROM temp_task t
    LEFT JOIN temp_customer c ON t.assignee_id = c.id;
    
    DELETE FROM temp_order_item WHERE order_id IN (SELECT id FROM temp_order WHERE customer_id = 1);
    DELETE FROM temp_order WHERE customer_id = 1;
    DELETE FROM temp_customer WHERE id = 1;
    
    SELECT t.id, t.title, t.assignee_id
    FROM temp_task t;
    ```


---


### 10. 복합 PRIMARY KEY를 사용하세요. (product_id, tag_id) 조합이 PK인 temp_pro


복합 PRIMARY KEY를 사용하세요. (product_id, tag_id) 조합이 PK인 temp_product_tag 테이블을 생성하세요.


**힌트 1:** `AUTOINCREMENT`가 아닌 복합 PK는 칼럼 정의가 아니라 테이블 제약으로 선언합니다: `PRIMARY KEY (col1, col2)`.


??? success "정답"
    ```sql
    CREATE TABLE temp_product_tag (
        product_id INTEGER NOT NULL,
        tag_id     INTEGER NOT NULL,
        PRIMARY KEY (product_id, tag_id)
    );
    
    INSERT INTO temp_product_tag VALUES (1, 10);
    INSERT INTO temp_product_tag VALUES (1, 20);
    INSERT INTO temp_product_tag VALUES (2, 10);
    
    SELECT * FROM temp_product_tag;
    ```


---


### 11. 아래 CREATE TABLE 문에는 오류가 3개 있습니다. 모두 찾아 수정하세요. (AUTOINCREMENT


아래 CREATE TABLE 문에는 오류가 3개 있습니다. 모두 찾아 수정하세요. (AUTOINCREMENT 위치, name NOT NULL 누락, DEFAULT 값 누락)


**힌트 1:** 1. `AUTOINCREMENT`는 `PRIMARY KEY` 뒤에 와야 합니다. 2. `name`에 NOT NULL이 빠져 있습니다. 3. `DEFAULT` 뒤에 기본값이 없습니다.


??? success "정답"
    ```sql
    CREATE TABLE temp_employee (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        email      TEXT UNIQUE,
        salary     REAL CHECK(salary > 0),
        department TEXT DEFAULT '미배정',
        hired_at   TEXT NOT NULL
    );
    
    INSERT INTO temp_employee (name, hired_at)
    VALUES ('테스트 직원', '2025-01-01');
    
    SELECT * FROM temp_employee;
    ```


---


### 12. CTAS (CREATE TABLE AS SELECT)로 2024년 주문 요약 테이블을 만드세요.


CTAS (CREATE TABLE AS SELECT)로 2024년 주문 요약 테이블을 만드세요.


**힌트 1:** `CREATE TABLE 이름 AS SELECT ...`는 SELECT 결과를 새 테이블로 저장합니다.


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
    
    SELECT * FROM temp_order_summary_2024
    ORDER BY total_spent DESC
    LIMIT 5;
    ```


---


### 13. DELETE vs DROP TABLE vs 테이블 재생성을 비교하세요. temp_tag의 데이터만 삭제하는 


DELETE vs DROP TABLE vs 테이블 재생성을 비교하세요. temp_tag의 데이터만 삭제하는 것과 테이블 자체를 삭제하는 방법을 각각 실행하세요.


**힌트 1:** 데이터만 삭제: `DELETE FROM 테이블;`, 테이블 삭제: `DROP TABLE 테이블;`, 안전 삭제: `DROP TABLE IF EXISTS 테이블;`


??? success "정답"
    ```sql
    DELETE FROM temp_tag;
    
    SELECT COUNT(*) AS cnt FROM temp_tag;
    
    DROP TABLE temp_tag;
    
    DROP TABLE IF EXISTS temp_tag;
    ```


---


### 14. 요구사항을 보고 temp_coupon 테이블을 설계하세요. 쿠폰 코드 유일, 유형은 percent/fixed


요구사항을 보고 temp_coupon 테이블을 설계하세요. 쿠폰 코드 유일, 유형은 percent/fixed만, 할인 값 양수, 최소 주문 금액 선택사항, 유효기간 필수, 활성 기본값 1.


**힌트 1:** 각 요구사항을 제약조건으로 매핑하세요: 유일→UNIQUE, 허용 목록→CHECK IN, 양수→CHECK > 0, 선택→NULL 허용, 필수→NOT NULL, 기본값→DEFAULT.


??? success "정답"
    ```sql
    CREATE TABLE temp_coupon (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        code             TEXT NOT NULL UNIQUE,
        type             TEXT NOT NULL CHECK(type IN ('percent','fixed')),
        discount_value   REAL NOT NULL CHECK(discount_value > 0),
        min_order_amount REAL CHECK(min_order_amount >= 0),
        is_active        INTEGER NOT NULL DEFAULT 1,
        started_at       TEXT NOT NULL,
        expired_at       TEXT NOT NULL
    );
    
    INSERT INTO temp_coupon (code, type, discount_value, min_order_amount, started_at, expired_at)
    VALUES ('WELCOME10', 'percent', 10, 50000, '2025-01-01', '2025-12-31');
    
    INSERT INTO temp_coupon (code, type, discount_value, started_at, expired_at)
    VALUES ('FLAT5000', 'fixed', 5000, '2025-06-01', '2025-06-30');
    
    SELECT * FROM temp_coupon;
    ```


---


### 15. 정리: 이번 연습에서 만든 모든 임시 테이블을 삭제하세요. FK 참조 순서에 주의하여 자식부터 삭제하세요.


정리: 이번 연습에서 만든 모든 임시 테이블을 삭제하세요. FK 참조 순서에 주의하여 자식부터 삭제하세요.


**힌트 1:** 먼저 목록을 확인하고, 각각 `DROP TABLE IF EXISTS`로 삭제합니다. FK 참조 순서에 주의하세요 (자식 먼저 삭제).


??? success "정답"
    ```sql
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%'
    ORDER BY name;
    
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
    
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%';
    ```


---
