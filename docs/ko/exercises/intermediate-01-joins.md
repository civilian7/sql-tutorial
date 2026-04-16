# JOIN 마스터

#### :material-database: 사용 테이블


`categories` — 카테고리 (부모-자식 계층)<br>

`customers` — 고객 (등급, 포인트, 가입채널)<br>

`orders` — 주문 (상태, 금액, 일시)<br>

`order_items` — 주문 상세 (수량, 단가)<br>

`products` — 상품 (이름, 가격, 재고, 브랜드)<br>

`reviews` — 리뷰 (평점, 내용)<br>

`shipping` — 배송 (택배사, 추적번호, 상태)<br>

`staff` — 직원 (부서, 역할, 관리자)<br>

`suppliers` — 공급업체 (업체명, 연락처)<br>

`tags` — 태그 (이름, 카테고리)<br>

`product_tags` — 상품-태그 연결<br>



**:material-book-open-variant: 학습 범위:** `INNER JOIN`, `LEFT JOIN`, `multi-table JOIN`, `GROUP BY`, `aggregate functions`


---


### 1. 각 상품의 이름, 가격, 카테고리명을 조회하세요. 가격 내림차순으로 10개만.


각 상품의 이름, 가격, 카테고리명을 조회하세요. 가격 내림차순으로 10개만.


**힌트 1:** `products`와 `categories`를 `category_id`로 `INNER JOIN`하고, `ORDER BY ... DESC LIMIT 10`.


??? success "정답"
    ```sql
    SELECT p.name, p.price, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    ORDER BY p.price DESC
    LIMIT 10;
    ```


---


### 2. 상품명, 카테고리명, 공급업체명을 함께 조회하세요.


상품명, 카테고리명, 공급업체명을 함께 조회하세요.


**힌트 1:** `products`에서 `categories`와 `suppliers` 두 테이블을 각각 `INNER JOIN`으로 연결.


??? success "정답"
    ```sql
    SELECT
        p.name AS product,
        cat.name AS category,
        s.company_name AS supplier
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    ORDER BY p.name
    LIMIT 20;
    ```


---


### 3. 한 번도 리뷰를 받지 않은 상품의 이름과 가격을 조회하세요.


한 번도 리뷰를 받지 않은 상품의 이름과 가격을 조회하세요.


**힌트 1:** `LEFT JOIN reviews` 후 `WHERE r.id IS NULL`로 매칭되지 않는 행을 찾기.


??? success "정답"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id
    WHERE r.id IS NULL
    ORDER BY p.price DESC;
    ```


---


### 4. 한 번도 주문하지 않은 고객의 이름과 가입일을 조회하세요.


한 번도 주문하지 않은 고객의 이름과 가입일을 조회하세요.


**힌트 1:** `customers LEFT JOIN orders` 후 `WHERE o.id IS NULL`로 주문이 없는 고객만 필터링.


??? success "정답"
    ```sql
    SELECT c.name, c.created_at
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL
    ORDER BY c.created_at;
    ```


---


### 5. 각 고객의 이름, 등급, 주문 수, 총 구매 금액을 조회하세요. 주문 수 상위 10명.


각 고객의 이름, 등급, 주문 수, 총 구매 금액을 조회하세요. 주문 수 상위 10명.


**힌트 1:** `customers JOIN orders` 후 `GROUP BY`로 집계. `COUNT`와 `SUM`을 함께 사용.


??? success "정답"
    ```sql
    SELECT
        c.name, c.grade,
        COUNT(o.id) AS order_count,
        ROUND(SUM(o.total_amount), 2) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```


---


### 6. 최근 주문 5건의 주문번호, 고객명, 상품명, 수량, 단가를 조회하세요.


최근 주문 5건의 주문번호, 고객명, 상품명, 수량, 단가를 조회하세요.


**힌트 1:** `orders -> customers`, `orders -> order_items -> products` 4개 테이블을 `INNER JOIN`으로 연결.


??? success "정답"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer,
        p.name AS product,
        oi.quantity,
        oi.unit_price
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    ORDER BY o.ordered_at DESC
    LIMIT 5;
    ```


---


### 7. 카테고리별 총 매출과 판매 수량을 구하세요. 취소 제외.


카테고리별 총 매출과 판매 수량을 구하세요. 취소 제외.


**힌트 1:** `order_items -> products -> categories`를 JOIN하고, `WHERE o.status NOT IN ('cancelled')`로 취소 제외.


??? success "정답"
    ```sql
    SELECT
        cat.name AS category,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
    FROM order_items AS oi
    INNER JOIN orders AS o ON oi.order_id = o.id
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY cat.name
    ORDER BY revenue DESC;
    ```


---


### 8. 리뷰가 5개 이상인 상품의 이름, 평균 평점, 리뷰 수를 구하세요.


리뷰가 5개 이상인 상품의 이름, 평균 평점, 리뷰 수를 구하세요.


**힌트 1:** `products JOIN reviews`로 연결 후 `GROUP BY`와 `HAVING COUNT(r.id) >= 5`로 필터링.


??? success "정답"
    ```sql
    SELECT
        p.name,
        ROUND(AVG(r.rating), 2) AS avg_rating,
        COUNT(r.id) AS review_count
    FROM products AS p
    INNER JOIN reviews AS r ON p.id = r.product_id
    GROUP BY p.id, p.name
    HAVING COUNT(r.id) >= 5
    ORDER BY avg_rating DESC
    LIMIT 15;
    ```


---


### 9. 배송 완료된 주문의 평균 배송 소요일(주문일 -> 배송완료일)을 구하세요.


배송 완료된 주문의 평균 배송 소요일(주문일 -> 배송완료일)을 구하세요.


**힌트 1:** `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)`로 날짜 차이를 계산. `shipping JOIN orders`.


??? success "정답"
    ```sql
    SELECT
        ROUND(AVG(JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at)), 1) AS avg_delivery_days
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE sh.status = 'delivered'
      AND sh.delivered_at IS NOT NULL;
    ```


---


### 10. 택배사(carrier)별 배송 건수, 완료 건수, 완료율을 구하세요.


택배사(carrier)별 배송 건수, 완료 건수, 완료율을 구하세요.


**힌트 1:** `GROUP BY carrier`와 `CASE WHEN status = 'delivered'`로 조건부 집계. 완료율은 `100.0 * 완료/전체`.


??? success "정답"
    ```sql
    SELECT
        carrier,
        COUNT(*) AS total,
        SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered,
        ROUND(100.0 * SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) / COUNT(*), 1) AS delivery_rate
    FROM shipping
    GROUP BY carrier
    ORDER BY total DESC;
    ```


---


### 11. 공급업체별 공급 상품 수, 평균 가격, 최고가를 구하세요.


공급업체별 공급 상품 수, 평균 가격, 최고가를 구하세요.


**힌트 1:** `suppliers JOIN products`로 연결 후 `GROUP BY`로 집계. `COUNT`, `AVG`, `MAX` 함수 사용.


??? success "정답"
    ```sql
    SELECT
        s.company_name,
        COUNT(p.id) AS product_count,
        ROUND(AVG(p.price), 2) AS avg_price,
        ROUND(MAX(p.price), 2) AS max_price
    FROM suppliers AS s
    INNER JOIN products AS p ON s.id = p.supplier_id
    GROUP BY s.id, s.company_name
    ORDER BY product_count DESC;
    ```


---


### 12. 각 고객의 가장 최근 주문일과 주문 금액을 조회하세요. 최근 주문순으로 정렬.


각 고객의 가장 최근 주문일과 주문 금액을 조회하세요. 최근 주문순으로 정렬.


**힌트 1:** `MAX(o.ordered_at)`로 최근 주문일을 구하고, `GROUP BY` 고객별로 집계.


??? success "정답"
    ```sql
    SELECT
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order_date,
        o.total_amount AS last_order_amount
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id, c.name, c.grade
    ORDER BY last_order_date DESC
    LIMIT 15;
    ```


---


### 13. 직원 계층 구조 (Self-JOIN)


모든 직원과 그 상사(매니저)의 이름을 함께 조회하세요.
매니저가 없는 최상위 직원은 상사명을 NULL로 표시합니다.


**힌트 1:** `staff` 테이블을 자기 자신과 LEFT JOIN. `staff AS s LEFT JOIN staff AS m ON s.manager_id = m.id`. 매니저가 없으면 `m.name`이 NULL.


??? success "정답"
    ```sql
    SELECT
        s.id,
        s.name       AS staff_name,
        s.department,
        s.role,
        m.name       AS manager_name,
        m.department AS manager_department
    FROM staff AS s
    LEFT JOIN staff AS m ON s.manager_id = m.id
    ORDER BY s.department, s.name;
    ```


---


### 14. 상품 후속 모델 체인 (Self-JOIN)


단종된 상품과 그 후속 모델을 함께 조회하세요.
단종 상품명, 단종일, 후속 모델명, 후속 모델 가격을 표시합니다.


**힌트 1:** `products.successor_id`가 같은 테이블의 `id`를 참조. `products AS p JOIN products AS succ ON p.successor_id = succ.id`. `p.discontinued_at IS NOT NULL` 필터.


??? success "정답"
    ```sql
    SELECT
        p.name        AS discontinued_product,
        p.price       AS old_price,
        p.discontinued_at,
        succ.name     AS successor_product,
        succ.price    AS new_price,
        ROUND(succ.price - p.price, 0) AS price_diff
    FROM products AS p
    INNER JOIN products AS succ ON p.successor_id = succ.id
    WHERE p.discontinued_at IS NOT NULL
    ORDER BY p.discontinued_at DESC
    LIMIT 20;
    ```


---


### 15. Q&A 스레드 조회 (Self-JOIN)


상품 Q&A에서 질문과 답변을 한 행에 보여주세요.
질문 내용, 질문 작성자(고객), 답변 내용, 답변 작성자(직원)를 표시합니다.


**힌트 1:** 질문: `parent_id IS NULL`. 답변: `parent_id`가 질문의 `id`를 참조. 질문(`q`) LEFT JOIN 답변(`a`) ON `a.parent_id = q.id`.


??? success "정답"
    ```sql
    SELECT
        p.name        AS product_name,
        q.content     AS question,
        c.name        AS asked_by,
        q.created_at  AS asked_at,
        a.content     AS answer,
        s.name        AS answered_by,
        a.created_at  AS answered_at
    FROM product_qna AS q
    INNER JOIN products AS p ON q.product_id = p.id
    LEFT JOIN customers AS c ON q.customer_id = c.id
    LEFT JOIN product_qna AS a ON a.parent_id = q.id
    LEFT JOIN staff AS s ON a.staff_id = s.id
    WHERE q.parent_id IS NULL
    ORDER BY q.created_at DESC
    LIMIT 20;
    ```


---


### 16. 주문이 없는 날 찾기 (CROSS JOIN)


calendar 테이블을 활용하여 2024년에 주문이 하나도 없는 날짜를 찾으세요.


**힌트 1:** `calendar` LEFT JOIN `orders` (날짜 기준). `orders`의 주문일을 `SUBSTR(ordered_at, 1, 10)`으로 날짜만 추출. `WHERE o.id IS NULL`로 주문 없는 날 필터.


??? success "정답"
    ```sql
    SELECT
        cal.date_key,
        cal.day_name,
        cal.is_weekend,
        cal.is_holiday,
        cal.holiday_name
    FROM calendar AS cal
    LEFT JOIN (
        SELECT DISTINCT SUBSTR(ordered_at, 1, 10) AS order_date
        FROM orders
    ) AS od ON cal.date_key = od.order_date
    WHERE cal.year = 2024
      AND od.order_date IS NULL
    ORDER BY cal.date_key;
    ```


---


### 17. 상품 태그 검색 (M:N JOIN)


"Gaming" 태그가 달린 상품 목록을 조회하세요.
상품명, 브랜드, 가격, 카테고리를 표시합니다.


**힌트 1:** `product_tags` -> `tags` JOIN으로 태그 이름 필터. `product_tags` -> `products` JOIN으로 상품 정보. `tags.name = 'Gaming'`.


??? success "정답"
    ```sql
    SELECT
        p.name   AS product_name,
        p.brand,
        p.price,
        cat.name AS category
    FROM product_tags AS pt
    INNER JOIN tags       AS t   ON pt.tag_id     = t.id
    INNER JOIN products   AS p   ON pt.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE t.name = 'Gaming'
      AND p.is_active = 1
    ORDER BY p.price DESC;
    ```


---
