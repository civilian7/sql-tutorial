# 중급 연습: JOIN 마스터

여러 테이블을 결합하는 12문제입니다. INNER JOIN, LEFT JOIN, 다중 JOIN을 연습합니다.

---

### 1. 상품과 카테고리

각 상품의 이름, 가격, 카테고리명을 조회하세요. 가격 내림차순으로 10개만.

**힌트:** `products`와 `categories`를 `category_id`로 `INNER JOIN`하고, `ORDER BY ... DESC LIMIT 10`.

??? success "정답"
    ```sql
    SELECT p.name, p.price, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    ORDER BY p.price DESC
    LIMIT 10;
    ```

---

### 2. 상품 + 카테고리 + 공급업체

상품명, 카테고리명, 공급업체명을 함께 조회하세요.

**힌트:** `products`에서 `categories`와 `suppliers` 두 테이블을 각각 `INNER JOIN`으로 연결.

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

### 3. 리뷰가 없는 상품

한 번도 리뷰를 받지 않은 상품의 이름과 가격을 조회하세요.

**힌트:** `LEFT JOIN reviews` 후 `WHERE r.id IS NULL`로 매칭되지 않는 행을 찾기.

??? success "정답"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id
    WHERE r.id IS NULL
    ORDER BY p.price DESC;
    ```

---

### 4. 주문한 적 없는 고객

한 번도 주문하지 않은 고객의 이름과 가입일을 조회하세요.

**힌트:** `customers LEFT JOIN orders` 후 `WHERE o.id IS NULL`로 주문이 없는 고객만 필터링.

??? success "정답"
    ```sql
    SELECT c.name, c.created_at
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL
    ORDER BY c.created_at;
    ```

---

### 5. 고객별 주문 요약

각 고객의 이름, 등급, 주문 수, 총 구매 금액을 조회하세요. 주문 수 상위 10명.

**힌트:** `customers JOIN orders` 후 `GROUP BY`로 집계. `COUNT`와 `SUM`을 함께 사용.

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

### 6. 주문 상세 (4테이블 JOIN)

최근 주문 5건의 주문번호, 고객명, 상품명, 수량, 단가를 조회하세요.

**힌트:** `orders → customers`, `orders → order_items → products` 4개 테이블을 `INNER JOIN`으로 연결.

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

### 7. 카테고리별 매출

카테고리별 총 매출과 판매 수량을 구하세요. 취소 제외.

**힌트:** `order_items → products → categories`를 JOIN하고, `WHERE o.status NOT IN ('cancelled')`로 취소 제외.

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

### 8. 상품별 평균 평점

리뷰가 5개 이상인 상품의 이름, 평균 평점, 리뷰 수를 구하세요.

**힌트:** `products JOIN reviews`로 연결 후 `GROUP BY`와 `HAVING COUNT(r.id) >= 5`로 필터링.

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

### 9. 배송 완료 평균 소요일

배송 완료된 주문의 평균 배송 소요일(주문일 → 배송완료일)을 구하세요.

**힌트:** `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)`로 날짜 차이를 계산. `shipping JOIN orders`.

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

### 10. 택배사별 배송 현황

택배사(carrier)별 배송 건수, 완료 건수, 완료율을 구하세요.

**힌트:** `GROUP BY carrier`와 `CASE WHEN status = 'delivered'`로 조건부 집계. 완료율은 `100.0 * 완료/전체`.

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

### 11. 공급업체별 상품 수와 평균 가격

공급업체별 공급 상품 수, 평균 가격, 최고가를 구하세요.

**힌트:** `suppliers JOIN products`로 연결 후 `GROUP BY`로 집계. `COUNT`, `AVG`, `MAX` 함수 사용.

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

### 12. 고객의 최근 주문

각 고객의 가장 최근 주문일과 주문 금액을 조회하세요. 최근 주문순으로 정렬.

**힌트:** `MAX(o.ordered_at)`로 최근 주문일을 구하고, `GROUP BY` 고객별로 집계.

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
