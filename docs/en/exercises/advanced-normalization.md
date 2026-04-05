# Advanced Exercises: Understanding Normalization

Analyze the design of the current database to understand normalization principles. These 8 problems answer the question: "Why were the tables split this way?"

---

### 1. Problems with Denormalization — Redundant Data

What problems would arise if customer names and emails were stored directly in the `orders` table?

**Hint:** If a single customer has placed hundreds of orders, check with `COUNT(*)` how many rows would need to be updated when they change their name.

??? success "Answer"
    ```sql
    -- 현재 설계: orders는 customer_id만 저장 (정규화됨)
    SELECT o.id, o.customer_id, c.name, c.email
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    LIMIT 5;
    ```

    **Problems with denormalization:**

    ```sql
    -- 만약 이렇게 저장했다면? (가상의 비정규화 테이블)
    -- orders(id, customer_name, customer_email, total_amount, ...)
    --
    -- 문제 1: 고객이 이름을 변경하면 orders의 모든 행을 업데이트해야 함
    -- 문제 2: 같은 이름/이메일이 수만 행에 중복 저장 → 저장 공간 낭비
    -- 문제 3: 한 곳만 업데이트하면 데이터 불일치 발생 (갱신 이상)

    -- 실제로 한 고객의 주문이 몇 건인지 확인
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    ORDER BY order_count DESC
    LIMIT 5;
    -- 이 고객의 이름이 바뀌면 수백 행을 수정해야 합니다
    ```

---

### 2. 1NF — Eliminating Non-Atomic Values and Repeating Groups

What if there were no `order_items` and products were listed as comma-separated values in the order?

**Hint:** Searching for a specific product in comma-separated values requires `LIKE`, which is all you can use. In a normalized design, `WHERE product_id = ?` does the job.

??? success "Answer"
    ```sql
    -- 현재 설계: 1NF 준수 — order_items로 분리
    SELECT o.order_number, p.name, oi.quantity, oi.unit_price
    FROM order_items AS oi
    INNER JOIN orders AS o ON oi.order_id = o.id
    INNER JOIN products AS p ON oi.product_id = p.id
    WHERE o.id = 1;
    ```

    **Problems with violating 1NF:**

    ```sql
    -- 만약 이렇게 저장했다면? (가상)
    -- orders(id, product_names='키보드,마우스,모니터', quantities='2,1,1')
    --
    -- 문제 1: "키보드가 포함된 주문"을 검색하려면 LIKE '%키보드%' → 느리고 부정확
    -- 문제 2: 각 상품의 가격을 계산할 수 없음
    -- 문제 3: 3번째 상품만 삭제하려면 문자열 파싱 필요

    -- 정규화된 설계에서는 간단:
    SELECT COUNT(DISTINCT order_id) AS orders_with_product
    FROM order_items
    WHERE product_id = 1;
    ```

---

### 3. 2NF — Eliminating Partial Dependencies

What if product names and categories were stored directly in `order_items`?

**Hint:** In the composite key `(order_id, product_id)`, `product_name` depends only on `product_id`. This is a partial dependency (2NF violation).

??? success "Answer"
    ```sql
    -- 현재 설계: order_items는 product_id만 저장 (2NF 준수)
    -- 상품명이 필요하면 JOIN
    SELECT oi.order_id, oi.product_id, p.name, p.brand
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    LIMIT 5;
    ```

    **Problems with violating 2NF:**

    ```sql
    -- 만약 order_items(order_id, product_id, product_name, category_name, quantity)
    -- → product_name은 product_id에만 종속 (order_id와 무관)
    -- → 부분 종속 (partial dependency)
    --
    -- 문제: 상품명이 바뀌면 order_items의 모든 관련 행을 수정해야 함

    -- 한 상품이 몇 개의 주문에 포함되었는지 확인
    SELECT product_id, COUNT(*) AS appearances
    FROM order_items
    GROUP BY product_id
    ORDER BY appearances DESC
    LIMIT 5;
    -- 이 모든 행의 product_name을 일일이 수정해야 합니다
    ```

---

### 4. 3NF — Eliminating Transitive Dependencies

What if customer grade and points were stored directly in `orders`?

**Hint:** The chain `order -> customer_id -> customer_grade` is a transitive dependency. Grade should only be managed in the customers table.

??? success "Answer"
    ```sql
    -- 현재 설계: orders → customers → grade (3NF 준수)
    -- 등급은 고객 테이블에서만 관리
    SELECT o.order_number, c.name, c.grade, c.point_balance
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    LIMIT 5;
    ```

    **Problems with violating 3NF:**

    ```sql
    -- 만약 orders(id, customer_id, customer_grade, customer_points, ...)
    -- → customer_grade는 customer_id에 종속, customer_id는 order에 종속
    -- → 이행 종속 (transitive dependency)
    --
    -- 문제: 등급이 변경되면 orders의 과거 모든 행도 수정?
    -- 아니면 과거 행은 옛 등급을 유지? → 의미가 모호해짐

    -- 한 고객의 주문에 서로 다른 등급이 저장될 수 있음 (데이터 불일치)
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    HAVING order_count > 10
    LIMIT 5;
    ```

---

### 5. Intentional Denormalization — order_items.unit_price

`order_items.unit_price` is a copy of `products.price`. Is this a normalization violation?

**Hint:** Product prices change over time. Consider whether the price at the time of order needs to be preserved.

??? success "Answer"
    ```sql
    -- order_items에 unit_price를 별도 저장하는 이유:
    -- 주문 시점의 가격을 보존하기 위해!

    -- 상품의 현재 가격과 과거 주문 가격이 다를 수 있음
    SELECT
        p.name,
        p.price AS current_price,
        oi.unit_price AS order_price,
        o.ordered_at
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN orders AS o ON oi.order_id = o.id
    WHERE p.price <> oi.unit_price
    LIMIT 10;
    ```

    **Key point:** Denormalization is not always bad. When you need to preserve **point-in-time data** (the price at the time of order), intentional denormalization is the right approach. The `product_prices` table exists for the same reason.

---

### 6. Normalizing M:N Relationships

Analyze how the many-to-many relationship between customers and products (wishlists) is implemented.

**Hint:** M:N relationships are decomposed using a junction table. Check the structure of the `wishlists` table in `sqlite_master`.

??? success "Answer"
    ```sql
    -- wishlists = 연결 테이블 (junction table)
    -- 복합 UNIQUE 키로 중복 방지
    SELECT
        c.name AS customer,
        p.name AS product,
        w.created_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products AS p ON w.product_id = p.id
    LIMIT 10;
    ```

    ```sql
    -- 연결 테이블 구조 확인
    SELECT sql FROM sqlite_master WHERE name = 'wishlists';
    ```

    **Key point:** M:N relationships cannot be represented directly, so they are decomposed into two 1:N relationships using a junction table. `coupon_usage` (coupon-customer-order) follows the same pattern.

---

### 7. Self-Reference and Hierarchical Structure

Analyze the self-referencing design of the `categories` table.

**Hint:** `parent_id` references the `id` in the same table. To build the full path, a `WITH RECURSIVE` CTE is needed.

??? success "Answer"
    ```sql
    -- parent_id로 자기 자신을 참조하는 계층 구조
    SELECT
        child.name AS category,
        parent.name AS parent_category,
        child.depth
    FROM categories AS child
    LEFT JOIN categories AS parent ON child.parent_id = parent.id
    ORDER BY child.depth, child.sort_order;
    ```

    ```sql
    -- 이 설계의 장점: 깊이가 유연함
    -- 단점: 전체 경로를 구하려면 재귀 CTE가 필요

    -- 재귀 CTE로 전체 경로 구성
    WITH RECURSIVE tree AS (
        SELECT id, name, parent_id, name AS path, 0 AS depth
        FROM categories WHERE parent_id IS NULL
        UNION ALL
        SELECT c.id, c.name, c.parent_id,
               tree.path || ' > ' || c.name, tree.depth + 1
        FROM categories AS c
        INNER JOIN tree ON c.parent_id = tree.id
    )
    SELECT path, depth FROM tree
    ORDER BY path;
    ```

---

### 8. Schema Design Quiz

Choose the correct design for the following scenario and explain your reasoning with SQL.

**Scenario:** You want to store multiple phone numbers for a customer.

- A) Add `phone2`, `phone3` columns to the `customers` table
- B) Create a separate `customer_phones` table

**Hint:** Recall the 1NF principle of "eliminating repeating groups." The `customer_addresses` table already implements the same pattern.

??? success "Answer"
    **B is correct.** — 1NF principle (eliminating repeating groups)

    The current database already uses the same pattern:

    ```sql
    -- customer_addresses: 고객당 여러 배송지 (1:N)
    SELECT customer_id, COUNT(*) AS address_count
    FROM customer_addresses
    GROUP BY customer_id
    ORDER BY address_count DESC
    LIMIT 5;
    ```

    **Problems with option A:**

    - What if there are 4 or more phone numbers? You'd need to add more columns, requiring schema changes.
    - Most rows would have NULL for phone2 — wasted storage space.
    - To search for "any customer with a phone number starting with 020": `phone LIKE '020%' OR phone2 LIKE '020%' OR phone3 LIKE '020%'` — inefficient.
