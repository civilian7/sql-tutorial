# 고급 연습: 정규화 이해

현재 데이터베이스의 설계를 분석하면서 정규화 원칙을 이해합니다. "왜 테이블을 이렇게 나눴을까?"에 대한 답을 찾는 8문제입니다.

---

### 1. 비정규화의 문제 — 중복 데이터

만약 `orders` 테이블에 고객 이름과 이메일을 직접 저장했다면 어떤 문제가 생길까요?

??? success "정답"
    ```sql
    -- 현재 설계: orders는 customer_id만 저장 (정규화됨)
    SELECT o.id, o.customer_id, c.name, c.email
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    LIMIT 5;
    ```

    **비정규화 시 문제점:**

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

### 2. 1NF — 원자값과 반복 그룹 제거

`order_items`가 없고 주문에 상품을 쉼표로 나열했다면?

??? success "정답"
    ```sql
    -- 현재 설계: 1NF 준수 — order_items로 분리
    SELECT o.order_number, p.name, oi.quantity, oi.unit_price
    FROM order_items AS oi
    INNER JOIN orders AS o ON oi.order_id = o.id
    INNER JOIN products AS p ON oi.product_id = p.id
    WHERE o.id = 1;
    ```

    **1NF 위반 시 문제점:**

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

### 3. 2NF — 부분 종속 제거

`order_items`에 상품명과 카테고리를 직접 저장했다면?

??? success "정답"
    ```sql
    -- 현재 설계: order_items는 product_id만 저장 (2NF 준수)
    -- 상품명이 필요하면 JOIN
    SELECT oi.order_id, oi.product_id, p.name, p.brand
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    LIMIT 5;
    ```

    **2NF 위반 시 문제점:**

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

### 4. 3NF — 이행 종속 제거

`orders`에 고객 등급과 적립금을 직접 저장했다면?

??? success "정답"
    ```sql
    -- 현재 설계: orders → customers → grade (3NF 준수)
    -- 등급은 고객 테이블에서만 관리
    SELECT o.order_number, c.name, c.grade, c.point_balance
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    LIMIT 5;
    ```

    **3NF 위반 시 문제점:**

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

### 5. 의도적 비정규화 — order_items.unit_price

`order_items.unit_price`는 `products.price`의 복사본입니다. 이것은 정규화 위반일까요?

??? success "정답"
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

    **핵심:** 비정규화가 항상 나쁜 것은 아닙니다. **시점 데이터**(주문 당시 가격)를 보존해야 할 때는 의도적으로 비정규화합니다. `product_prices` 테이블도 같은 이유로 존재합니다.

---

### 6. M:N 관계의 정규화

고객과 상품의 다대다 관계(위시리스트)가 어떻게 구현되었는지 분석하세요.

??? success "정답"
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

    **핵심:** M:N 관계는 직접 표현할 수 없으므로, 연결 테이블로 두 개의 1:N 관계로 분해합니다. `coupon_usage`(쿠폰-고객-주문)도 같은 패턴입니다.

---

### 7. 자기 참조와 계층 구조

`categories` 테이블의 자기 참조 설계를 분석하세요.

??? success "정답"
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

### 8. 스키마 설계 퀴즈

다음 시나리오에서 올바른 설계를 선택하고 그 이유를 SQL로 설명하세요.

**시나리오:** 고객에게 여러 개의 전화번호를 저장하고 싶다.

- A) `customers` 테이블에 `phone2`, `phone3` 컬럼 추가
- B) 별도의 `customer_phones` 테이블 생성

??? success "정답"
    **B가 정답입니다.** — 1NF 원칙 (반복 그룹 제거)

    현재 데이터베이스에서 이미 같은 패턴을 사용하고 있습니다:

    ```sql
    -- customer_addresses: 고객당 여러 배송지 (1:N)
    SELECT customer_id, COUNT(*) AS address_count
    FROM customer_addresses
    GROUP BY customer_id
    ORDER BY address_count DESC
    LIMIT 5;
    ```

    **A의 문제점:**

    - 전화번호가 4개 이상이면? → 또 컬럼 추가 → 스키마 변경 필요
    - phone2가 NULL인 행이 대부분 → 공간 낭비
    - "전화번호 중 하나라도 020으로 시작하는 고객"을 검색하려면 → `phone LIKE '020%' OR phone2 LIKE '020%' OR phone3 LIKE '020%'` → 비효율적
