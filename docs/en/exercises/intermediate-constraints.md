# Intermediate Exercises: Exploring Constraints

Experience firsthand how a database rejects invalid data. In each problem, **intentionally violate a constraint** and observe what error occurs.

> **Note:** These exercises execute INSERT/UPDATE statements. To protect original data, make a copy of `tutorial.db` before proceeding.

---

### 1. PRIMARY KEY Duplicate

What happens if you insert a product with an id that already exists?

```sql
-- 먼저 id=1 상품이 존재하는지 확인
SELECT id, name FROM products WHERE id = 1;
```

??? success "Try it"
    ```sql
    -- PRIMARY KEY 중복 → 에러 발생
    INSERT INTO products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (1, 1, 1, '중복 테스트', 'DUP-001', 'Test', 100, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```

    **Result:** `UNIQUE constraint failed: products.id` — A record with the same PRIMARY KEY already exists.

---

### 2. UNIQUE Constraint (Duplicate Email)

What happens if you create a customer with an email that's already registered?

```sql
-- 기존 고객 이메일 확인
SELECT email FROM customers LIMIT 1;
```

??? success "Try it"
    ```sql
    -- 해당 이메일을 복사하여 삽입 시도
    INSERT INTO customers (email, password_hash, name, phone, grade, point_balance, is_active, created_at, updated_at)
    VALUES ('user1@testmail.kr', 'hash123', '테스트', '020-0000-0000', 'BRONZE', 0, 1, '2025-01-01', '2025-01-01');
    ```

    **Result:** `UNIQUE constraint failed: customers.email` — Each customer must have a unique email.

---

### 3. FOREIGN KEY Violation

What happens if you insert a product into a non-existent category?

```sql
-- 카테고리 최대 id 확인
SELECT MAX(id) FROM categories;
```

??? success "Try it"
    ```sql
    -- 존재하지 않는 category_id 사용
    INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (99999, 1, 'FK 테스트', 'FK-001', 'Test', 100, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```

    **Result:** `FOREIGN KEY constraint failed` — The referenced category does not exist.

    > To enable FK checks in SQLite, run `PRAGMA foreign_keys = ON;` first.

---

### 4. CHECK Constraint (Negative Price)

What happens if you set the price to a negative value?

??? success "Try it"
    ```sql
    -- price >= 0 CHECK 위반
    INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (2, 1, '음수 가격', 'NEG-001', 'Test', -500, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```

    **Result:** `CHECK constraint failed` — Price must be 0 or greater.

---

### 5. CHECK Constraint (Invalid Grade)

What happens if you set a customer grade to a value that's not allowed?

??? success "Try it"
    ```sql
    -- grade IN ('BRONZE', 'SILVER', 'GOLD', 'VIP') CHECK 위반
    INSERT INTO customers (email, password_hash, name, phone, grade, point_balance, is_active, created_at, updated_at)
    VALUES ('check-test@testmail.kr', 'hash', '등급테스트', '020-0000-0001', 'DIAMOND', 0, 1, '2025-01-01', '2025-01-01');
    ```

    **Result:** `CHECK constraint failed` — The only allowed grades are BRONZE, SILVER, GOLD, and VIP.

---

### 6. NOT NULL Violation

What happens if you leave a required column empty?

??? success "Try it"
    ```sql
    -- name은 NOT NULL
    INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (2, 1, NULL, 'NULL-001', 'Test', 100, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```

    **Result:** `NOT NULL constraint failed: products.name` — The product name is required.

---

### 7. Composite UNIQUE Constraint

What happens if the same customer adds the same product to their wishlist twice?

```sql
-- 기존 위시리스트 항목 확인
SELECT customer_id, product_id FROM wishlists LIMIT 1;
```

??? success "Try it"
    ```sql
    -- (customer_id, product_id) 복합 UNIQUE 위반
    -- 위에서 확인한 값으로 교체하세요
    INSERT INTO wishlists (customer_id, product_id, created_at)
    VALUES (1, 1, '2025-01-01');

    -- 같은 조합을 다시 삽입
    INSERT INTO wishlists (customer_id, product_id, created_at)
    VALUES (1, 1, '2025-01-02');
    ```

    **Result:** The first insert succeeds, the second fails with `UNIQUE constraint failed` — The same customer cannot add the same product twice.

---

### 8. CHECK Constraint (Rating Range)

What happens if you give a review a rating of 0 or 6?

??? success "Try it"
    ```sql
    -- rating BETWEEN 1 AND 5 CHECK 위반
    INSERT INTO reviews (product_id, customer_id, order_id, rating, content, is_verified, created_at, updated_at)
    VALUES (1, 1, 1, 0, '별점 0점 테스트', 1, '2025-01-01', '2025-01-01');
    ```

    **Result:** `CHECK constraint failed` — Rating must be between 1 and 5.

---

### 9. Viewing Current Constraints

Check all constraints defined in the database.

??? success "Answer"
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

### 10. Handling Duplicates with ON CONFLICT

Practice UPSERT — updating instead of throwing an error when a duplicate occurs.

??? success "Answer"
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
