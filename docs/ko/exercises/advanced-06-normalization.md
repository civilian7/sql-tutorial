# 정규화 이해


### 1. 비정규화의 문제 - 중복 데이터


만약 orders 테이블에 고객 이름과 이메일을 직접 저장했다면 어떤 문제가 생길까요?


**힌트 1:** 한 고객이 수백 건 주문했을 때, 이름 변경 시 몇 행을 수정해야 하는지 `COUNT(*)`로 확인해 보세요.



??? success "정답"
    ```sql
    -- 현재 설계: orders는 customer_id만 저장 (정규화됨)
    SELECT o.id, o.customer_id, c.name, c.email
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    LIMIT 5;
    
    -- 한 고객의 주문이 몇 건인지 확인
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    ORDER BY order_count DESC
    LIMIT 5;
    ```


---


### 2. 1NF - 원자값과 반복 그룹 제거


order_items가 없고 주문에 상품을 쉼표로 나열했다면 어떤 문제가 생길까요?


**힌트 1:** 쉼표로 구분된 값에서 특정 상품을 검색하려면 `LIKE`밖에 쓸 수 없습니다.
정규화된 설계에서는 `WHERE product_id = ?`로 끝납니다.



??? success "정답"
    ```sql
    -- 현재 설계: 1NF 준수 - order_items로 분리
    SELECT o.order_number, p.name, oi.quantity, oi.unit_price
    FROM order_items AS oi
    INNER JOIN orders AS o ON oi.order_id = o.id
    INNER JOIN products AS p ON oi.product_id = p.id
    WHERE o.id = 1;
    
    -- 정규화된 설계에서 특정 상품 검색은 간단
    SELECT COUNT(DISTINCT order_id) AS orders_with_product
    FROM order_items
    WHERE product_id = 1;
    ```


---


### 3. 2NF - 부분 종속 제거


order_items에 상품명과 카테고리를 직접 저장했다면 어떤 문제가 생길까요?


**힌트 1:** 복합키 `(order_id, product_id)` 중 `product_name`은 `product_id`에만 종속됩니다.
이것이 부분 종속(2NF 위반)입니다.



??? success "정답"
    ```sql
    -- 현재 설계: order_items는 product_id만 저장 (2NF 준수)
    SELECT oi.order_id, oi.product_id, p.name, p.brand
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    LIMIT 5;
    
    -- 한 상품이 몇 개의 주문에 포함되었는지 확인
    SELECT product_id, COUNT(*) AS appearances
    FROM order_items
    GROUP BY product_id
    ORDER BY appearances DESC
    LIMIT 5;
    ```


---


### 4. 3NF - 이행 종속 제거


orders에 고객 등급과 적립금을 직접 저장했다면 어떤 문제가 생길까요?


**힌트 1:** `order -> customer_id -> customer_grade` 체인이 이행 종속입니다.
등급은 고객 테이블에서만 관리해야 합니다.



??? success "정답"
    ```sql
    -- 현재 설계: orders -> customers -> grade (3NF 준수)
    SELECT o.order_number, c.name, c.grade, c.point_balance
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    LIMIT 5;
    
    -- 한 고객의 주문 수 (등급 변경 시 이 모든 행이 영향)
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    HAVING order_count > 10
    LIMIT 5;
    ```


---


### 5. 의도적 비정규화 - order_items.unit_price


order_items.unit_price는 products.price의 복사본입니다. 이것은 정규화 위반일까요?


**힌트 1:** 상품 가격은 시간에 따라 변합니다. 주문 시점의 가격을 보존해야 하는지 생각해 보세요.



??? success "정답"
    ```sql
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


---


### 6. M:N 관계의 정규화


고객과 상품의 다대다 관계(위시리스트)가 어떻게 구현되었는지 분석하세요.


**힌트 1:** M:N 관계는 연결 테이블(junction table)로 분해합니다.
`wishlists` 테이블의 구조를 `sqlite_master`에서 확인해 보세요.



??? success "정답"
    ```sql
    -- wishlists = 연결 테이블 (junction table)
    SELECT
        c.name AS customer,
        p.name AS product,
        w.created_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products AS p ON w.product_id = p.id
    LIMIT 10;
    
    -- 연결 테이블 구조 확인
    SELECT sql FROM sqlite_master WHERE name = 'wishlists';
    ```


---


### 7. 자기 참조와 계층 구조


categories 테이블의 자기 참조 설계를 분석하세요.
재귀 CTE로 전체 카테고리 경로를 구성해 보세요.


**힌트 1:** `parent_id`가 같은 테이블의 `id`를 참조합니다.
전체 경로를 구하려면 `WITH RECURSIVE` CTE가 필요합니다.



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
시나리오: 고객에게 여러 개의 전화번호를 저장하고 싶다.
A) customers 테이블에 phone2, phone3 컬럼 추가
B) 별도의 customer_phones 테이블 생성


**힌트 1:** 1NF의 "반복 그룹 제거" 원칙을 떠올리세요.
`customer_addresses` 테이블이 같은 패턴으로 이미 구현되어 있습니다.



??? success "정답"
    ```sql
    -- B가 정답 - 1NF 원칙 (반복 그룹 제거)
    -- customer_addresses: 고객당 여러 배송지 (1:N)
    SELECT customer_id, COUNT(*) AS address_count
    FROM customer_addresses
    GROUP BY customer_id
    ORDER BY address_count DESC
    LIMIT 5;
    ```


---
