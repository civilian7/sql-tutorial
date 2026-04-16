# Understanding Normalization

#### :material-database: Tables


`orders` — Orders (status, amount, date)<br>

`order_items` — Order items (qty, unit price)<br>

`products` — Products (name, price, stock, brand)<br>

`customers` — Customers (grade, points, channel)<br>

`categories` — Categories (parent-child hierarchy)<br>

`wishlists` — Wishlists (customer-product)<br>

`customer_addresses` — Addresses (address, default flag)<br>



**:material-book-open-variant: Concepts:** `1NF`, `2NF`, `3NF`, `Denormalization`, `Self-Reference`, `M:N`, `Recursive CTE`


---


### 1. Denormalization Problem - Redundant Data


What problems would arise if customer name and email were stored directly in the orders table?


**Hint 1:** Check with `COUNT(*)` how many rows would need updating if a customer with hundreds of orders changed their name.



??? success "Answer"
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


### 2. 1NF - Atomic Values and Eliminating Repeating Groups


What problems would occur if products were stored as comma-separated values instead of in order_items?


**Hint 1:** To search for a specific product in comma-separated values, you can only use `LIKE`.
In a normalized design, `WHERE product_id = ?` is sufficient.



??? success "Answer"
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


### 3. 2NF - Eliminating Partial Dependencies


What problems would arise if product_name and category were stored directly in order_items?


**Hint 1:** In composite key `(order_id, product_id)`, `product_name` depends only on `product_id`.
This is a partial dependency (2NF violation).



??? success "Answer"
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


### 4. 3NF - Eliminating Transitive Dependencies


What problems would arise if customer grade and points were stored directly in orders?


**Hint 1:** The chain `order -> customer_id -> customer_grade` is a transitive dependency.
Grade should only be managed in the customers table.



??? success "Answer"
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


### 5. Intentional Denormalization - order_items.unit_price


order_items.unit_price is a copy of products.price. Is this a normalization violation?


**Hint 1:** Product prices change over time. Think about whether the order-time price should be preserved.



??? success "Answer"
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


### 6. Normalizing M:N Relationships


Analyze how the many-to-many relationship between customers and products (wishlists) is implemented.


**Hint 1:** M:N relationships are decomposed with junction tables.
Check the `wishlists` table structure from `sqlite_master`.



??? success "Answer"
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


### 7. Self-Reference and Hierarchical Structure


Analyze the self-referencing design of the categories table.
Build full category paths using a recursive CTE.


**Hint 1:** `parent_id` references `id` in the same table.
Use `WITH RECURSIVE` CTE to build full paths.



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


Choose the correct design for this scenario and explain with SQL.
Scenario: You want to store multiple phone numbers per customer.
A) Add phone2, phone3 columns to customers table
B) Create a separate customer_phones table


**Hint 1:** Think about the 1NF "eliminate repeating groups" principle.
The `customer_addresses` table already uses this pattern.



??? success "Answer"
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
