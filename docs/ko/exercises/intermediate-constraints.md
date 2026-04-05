# 중급 연습: 제약조건 체험

데이터베이스가 잘못된 데이터를 어떻게 거부하는지 직접 체험합니다. 각 문제에서 **의도적으로 제약조건을 위반**하고, 어떤 에러가 발생하는지 확인하세요.

> **주의:** 이 연습은 INSERT/UPDATE 문을 실행합니다. 원본 데이터를 보호하려면 `tutorial.db`를 복사한 후 사용하세요.

---

### 1. PRIMARY KEY 중복

이미 존재하는 id로 상품을 삽입하면 어떻게 될까요?

```sql
-- 먼저 id=1 상품이 존재하는지 확인
SELECT id, name FROM products WHERE id = 1;
```

**힌트:** 이미 존재하는 `id` 값으로 `INSERT`하면 PRIMARY KEY의 고유성 제약이 위반됩니다.

??? success "실험"
    ```sql
    -- PRIMARY KEY 중복 → 에러 발생
    INSERT INTO products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (1, 1, 1, '중복 테스트', 'DUP-001', 'Test', 100, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```

    **결과:** `UNIQUE constraint failed: products.id` — 동일한 PRIMARY KEY가 이미 존재합니다.

---

### 2. UNIQUE 제약조건 (이메일 중복)

이미 등록된 이메일로 고객을 만들면?

```sql
-- 기존 고객 이메일 확인
SELECT email FROM customers LIMIT 1;
```

**힌트:** `UNIQUE` 제약이 걸린 컬럼에 이미 존재하는 값을 넣으면 중복 에러가 발생합니다.

??? success "실험"
    ```sql
    -- 해당 이메일을 복사하여 삽입 시도
    INSERT INTO customers (email, password_hash, name, phone, grade, point_balance, is_active, created_at, updated_at)
    VALUES ('user1@testmail.kr', 'hash123', '테스트', '020-0000-0000', 'BRONZE', 0, 1, '2025-01-01', '2025-01-01');
    ```

    **결과:** `UNIQUE constraint failed: customers.email` — 이메일은 고객마다 고유해야 합니다.

---

### 3. FOREIGN KEY 위반

존재하지 않는 카테고리에 상품을 넣으면?

```sql
-- 카테고리 최대 id 확인
SELECT MAX(id) FROM categories;
```

**힌트:** `FOREIGN KEY`는 부모 테이블에 존재하는 값만 허용합니다. SQLite에서는 `PRAGMA foreign_keys = ON` 필요.

??? success "실험"
    ```sql
    -- 존재하지 않는 category_id 사용
    INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (99999, 1, 'FK 테스트', 'FK-001', 'Test', 100, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```

    **결과:** `FOREIGN KEY constraint failed` — 참조하는 카테고리가 존재하지 않습니다.

    > SQLite에서 FK 체크를 활성화하려면 `PRAGMA foreign_keys = ON;`을 먼저 실행하세요.

---

### 4. CHECK 제약조건 (음수 가격)

가격을 음수로 설정하면?

**힌트:** `CHECK(price >= 0)` 제약이 정의되어 있으면, 음수 값 삽입 시 거부됩니다.

??? success "실험"
    ```sql
    -- price >= 0 CHECK 위반
    INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (2, 1, '음수 가격', 'NEG-001', 'Test', -500, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```

    **결과:** `CHECK constraint failed` — 가격은 0 이상이어야 합니다.

---

### 5. CHECK 제약조건 (잘못된 등급)

고객 등급을 허용되지 않은 값으로 설정하면?

**힌트:** `CHECK(grade IN ('BRONZE','SILVER','GOLD','VIP'))` 같은 허용 목록 제약은 목록에 없는 값을 거부합니다.

??? success "실험"
    ```sql
    -- grade IN ('BRONZE', 'SILVER', 'GOLD', 'VIP') CHECK 위반
    INSERT INTO customers (email, password_hash, name, phone, grade, point_balance, is_active, created_at, updated_at)
    VALUES ('check-test@testmail.kr', 'hash', '등급테스트', '020-0000-0001', 'DIAMOND', 0, 1, '2025-01-01', '2025-01-01');
    ```

    **결과:** `CHECK constraint failed` — 허용된 등급은 BRONZE, SILVER, GOLD, VIP뿐입니다.

---

### 6. NOT NULL 위반

필수 컬럼을 비우면?

**힌트:** `NOT NULL` 제약이 있는 컬럼에 `NULL`을 넣으면 에러가 발생합니다.

??? success "실험"
    ```sql
    -- name은 NOT NULL
    INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (2, 1, NULL, 'NULL-001', 'Test', 100, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```

    **결과:** `NOT NULL constraint failed: products.name` — 상품명은 반드시 있어야 합니다.

---

### 7. 복합 UNIQUE 제약조건

같은 고객이 같은 상품을 위시리스트에 두 번 추가하면?

```sql
-- 기존 위시리스트 항목 확인
SELECT customer_id, product_id FROM wishlists LIMIT 1;
```

**힌트:** `(customer_id, product_id)` 두 컬럼의 조합이 `UNIQUE`면, 같은 조합을 두 번째 삽입할 때 에러가 납니다.

??? success "실험"
    ```sql
    -- (customer_id, product_id) 복합 UNIQUE 위반
    -- 위에서 확인한 값으로 교체하세요
    INSERT INTO wishlists (customer_id, product_id, created_at)
    VALUES (1, 1, '2025-01-01');

    -- 같은 조합을 다시 삽입
    INSERT INTO wishlists (customer_id, product_id, created_at)
    VALUES (1, 1, '2025-01-02');
    ```

    **결과:** 첫 번째는 성공, 두 번째는 `UNIQUE constraint failed` — 같은 고객이 같은 상품을 중복 등록할 수 없습니다.

---

### 8. CHECK 제약조건 (평점 범위)

리뷰 평점을 0점이나 6점으로 주면?

**힌트:** `CHECK(rating BETWEEN 1 AND 5)` 제약은 범위를 벗어나는 값을 거부합니다.

??? success "실험"
    ```sql
    -- rating BETWEEN 1 AND 5 CHECK 위반
    INSERT INTO reviews (product_id, customer_id, order_id, rating, content, is_verified, created_at, updated_at)
    VALUES (1, 1, 1, 0, '별점 0점 테스트', 1, '2025-01-01', '2025-01-01');
    ```

    **결과:** `CHECK constraint failed` — 평점은 1~5 사이여야 합니다.

---

### 9. 현재 제약조건 조회

데이터베이스에 정의된 모든 제약조건을 확인하세요.

**힌트:** `sqlite_master` 테이블에서 `type = 'table'`인 DDL을 조회하면 CHECK/NOT NULL 등을 볼 수 있고, `type = 'index'`에서 UNIQUE 인덱스를 확인.

??? success "정답"
    ```sql
    -- CHECK 제약조건이 포함된 테이블 DDL 확인
    SELECT name, sql FROM sqlite_master
    WHERE type = 'table'
      AND sql LIKE '%CHECK%'
    ORDER BY name;
    ```

    ```sql
    -- UNIQUE 인덱스 목록
    SELECT name, tbl_name, sql FROM sqlite_master
    WHERE type = 'index'
      AND sql LIKE '%UNIQUE%'
    ORDER BY tbl_name;
    ```

---

### 10. ON CONFLICT로 중복 처리

중복 발생 시 에러 대신 업데이트하는 UPSERT를 실습하세요.

**힌트:** `INSERT OR IGNORE`는 중복 시 무시, `INSERT ... ON CONFLICT(id) DO UPDATE SET ...`는 중복 시 기존 행을 업데이트.

??? success "정답"
    ```sql
    -- 위시리스트: 이미 있으면 무시
    INSERT OR IGNORE INTO wishlists (customer_id, product_id, created_at)
    VALUES (1, 1, '2025-06-01');

    -- 상품: 이미 있으면 가격 업데이트
    INSERT INTO products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (1, 2, 1, '업데이트 테스트', 'SKU-0001', 'Test', 999999, 50, 10, 1, '2025-01-01', '2025-01-01')
    ON CONFLICT(id) DO UPDATE SET
        price = excluded.price,
        updated_at = excluded.updated_at;

    -- 변경 확인
    SELECT id, name, price FROM products WHERE id = 1;
    ```
