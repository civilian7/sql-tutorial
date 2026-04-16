# Exploring Constraints

**Tables:** `customers`, `products`, `reviews`, `wishlists`

**Concepts:** PRIMARY KEY, UNIQUE, FOREIGN KEY, CHECK, NOT NULL, ON CONFLICT, UPSERT


---


### 1. What happens if you insert a product with an id that already


What happens if you insert a product with an id that already exists?


**Hint 1:** Inserting with an existing `id` value violates the PRIMARY KEY uniqueness constraint.


??? success "Answer"
    ```sql
    -- PRIMARY KEY 중복 → 에러 발생
    INSERT INTO products (id, category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (1, 1, 1, '중복 테스트', 'DUP-001', 'Test', 100, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```


---


### 2. What happens if you create a customer with an email that's a


What happens if you create a customer with an email that's already registered?


**Hint 1:** Inserting an already-existing value into a column with a `UNIQUE` constraint causes a duplicate error.


??? success "Answer"
    ```sql
    -- 해당 이메일을 복사하여 삽입 시도
    INSERT INTO customers (email, password_hash, name, phone, grade, point_balance, is_active, created_at, updated_at)
    VALUES ('user1@testmail.kr', 'hash123', '테스트', '020-0000-0000', 'BRONZE', 0, 1, '2025-01-01', '2025-01-01');
    ```


---


### 3. What happens if you insert a product into a non-existent cat


What happens if you insert a product into a non-existent category?


**Hint 1:** A `FOREIGN KEY` only allows values that exist in the parent table. In SQLite, `PRAGMA foreign_keys = ON` is required.


??? success "Answer"
    ```sql
    -- 존재하지 않는 category_id 사용
    INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (99999, 1, 'FK 테스트', 'FK-001', 'Test', 100, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```


---


### 4. What happens if you set the price to a negative value?


What happens if you set the price to a negative value?


**Hint 1:** If a `CHECK(price >= 0)` constraint is defined, inserting a negative value will be rejected.


??? success "Answer"
    ```sql
    -- price >= 0 CHECK 위반
    INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (2, 1, '음수 가격', 'NEG-001', 'Test', -500, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```


---


### 5. What happens if you set a customer grade to a value that's n


What happens if you set a customer grade to a value that's not allowed?


**Hint 1:** An allowlist constraint like `CHECK(grade IN ('BRONZE','SILVER','GOLD','VIP'))` rejects values not in the list.


??? success "Answer"
    ```sql
    -- grade IN ('BRONZE', 'SILVER', 'GOLD', 'VIP') CHECK 위반
    INSERT INTO customers (email, password_hash, name, phone, grade, point_balance, is_active, created_at, updated_at)
    VALUES ('check-test@testmail.kr', 'hash', '등급테스트', '020-0000-0001', 'DIAMOND', 0, 1, '2025-01-01', '2025-01-01');
    ```


---


### 6. What happens if you leave a required column empty?


What happens if you leave a required column empty?


**Hint 1:** Inserting `NULL` into a column with a `NOT NULL` constraint causes an error.


??? success "Answer"
    ```sql
    -- name은 NOT NULL
    INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (2, 1, NULL, 'NULL-001', 'Test', 100, 50, 10, 1, '2025-01-01', '2025-01-01');
    ```


---


### 7. What happens if the same customer adds the same product to t


What happens if the same customer adds the same product to their wishlist twice?


**Hint 1:** If the combination of `(customer_id, product_id)` is `UNIQUE`, inserting the same combination a second time causes an error.


??? success "Answer"
    ```sql
    -- (customer_id, product_id) 복합 UNIQUE 위반
    -- 위에서 확인한 값으로 교체하세요
    INSERT INTO wishlists (customer_id, product_id, created_at)
    VALUES (1, 1, '2025-01-01');
    
    -- 같은 조합을 다시 삽입
    INSERT INTO wishlists (customer_id, product_id, created_at)
    VALUES (1, 1, '2025-01-02');
    ```


---


### 8. What happens if you give a review a rating of 0 or 6?


What happens if you give a review a rating of 0 or 6?


**Hint 1:** A `CHECK(rating BETWEEN 1 AND 5)` constraint rejects values outside the range.


??? success "Answer"
    ```sql
    -- rating BETWEEN 1 AND 5 CHECK 위반
    INSERT INTO reviews (product_id, customer_id, order_id, rating, content, is_verified, created_at, updated_at)
    VALUES (1, 1, 1, 0, '별점 0점 테스트', 1, '2025-01-01', '2025-01-01');
    ```


---


### 9. Check all constraints defined in the database.


Check all constraints defined in the database.


**Hint 1:** Query the `sqlite_master` table with `type = 'table'` to see DDL with CHECK/NOT NULL constraints, and `type = 'index'` for UNIQUE indexes.


??? success "Answer"
    ```sql
    -- CHECK 제약조건이 포함된 테이블 DDL 확인
    SELECT name, sql FROM sqlite_master
    WHERE type = 'table'
      AND sql LIKE '%CHECK%'
    ORDER BY name;
    ```


---


### 10. Practice UPSERT -- updating instead of throwing an error whe


Practice UPSERT -- updating instead of throwing an error when a duplicate occurs.


**Hint 1:** `INSERT OR IGNORE` silently skips duplicates, while `INSERT ... ON CONFLICT(id) DO UPDATE SET ...` updates the existing row on conflict.


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


---
