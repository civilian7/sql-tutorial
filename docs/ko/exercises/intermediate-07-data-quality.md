# 데이터 품질 점검


### 1. 고객 가입일보다 주문일이 빠른 주문이 있는지 확인하세요.


고객 가입일보다 주문일이 빠른 주문이 있는지 확인하세요.


**힌트 1:** `orders JOIN customers`로 연결 후 `WHERE ordered_at < created_at`으로 시간 역전을 탐지.


??? success "정답"
    ```sql
    SELECT
        o.order_number, o.ordered_at,
        c.name, c.created_at AS signup_date
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    WHERE o.ordered_at < c.created_at;
    ```


---


### 2. 주문이 존재하지 않는 결제 레코드가 있는지 확인하세요.


주문이 존재하지 않는 결제 레코드가 있는지 확인하세요.


**힌트 1:** `payments LEFT JOIN orders` 후 `WHERE o.id IS NULL`로 부모가 없는 고아 레코드를 찾으세요.


??? success "정답"
    ```sql
    SELECT p.id, p.order_id, p.amount
    FROM payments p
    LEFT JOIN orders o ON p.order_id = o.id
    WHERE o.id IS NULL;
    ```


---


### 3. 각 테이블의 NULL이 많은 컬럼을 찾으세요.


각 테이블의 NULL이 많은 컬럼을 찾으세요.


**힌트 1:** `SUM(CASE WHEN 컬럼 IS NULL THEN 1 ELSE 0 END) / COUNT(*)`로 각 컬럼의 NULL 비율을 계산.


??? success "정답"
    ```sql
    -- customers 테이블의 NULL 비율
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN birth_date IS NULL THEN 1 ELSE 0 END) AS null_birthdate,
        ROUND(100.0 * SUM(CASE WHEN birth_date IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_birthdate,
        SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) AS null_gender,
        ROUND(100.0 * SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_gender,
        SUM(CASE WHEN last_login_at IS NULL THEN 1 ELSE 0 END) AS null_login,
        ROUND(100.0 * SUM(CASE WHEN last_login_at IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_login
    FROM customers;
    ```


---


### 4. 배송 완료(delivered)인데 주문 상태가 아직 shipped인 불일치를 찾으세요.


배송 완료(delivered)인데 주문 상태가 아직 shipped인 불일치를 찾으세요.


**힌트 1:** `orders JOIN shipping`으로 연결 후 `shipping.status = 'delivered'`인데 `orders.status`가 배송 완료 상태가 아닌 행을 찾으세요.


??? success "정답"
    ```sql
    SELECT
        o.order_number, o.status AS order_status,
        sh.status AS shipping_status, sh.delivered_at
    FROM orders o
    INNER JOIN shipping sh ON o.id = sh.order_id
    WHERE sh.status = 'delivered'
      AND o.status NOT IN ('delivered', 'confirmed', 'return_requested', 'returned');
    ```


---


### 5. 배송완료일이 출고일보다 빠른 비정상 레코드를 찾으세요.


배송완료일이 출고일보다 빠른 비정상 레코드를 찾으세요.


**힌트 1:** `WHERE delivered_at < shipped_at`으로 날짜 역전을 탐지. 두 컬럼 모두 NOT NULL인 행만 대상.


??? success "정답"
    ```sql
    SELECT
        sh.id, o.order_number,
        sh.shipped_at, sh.delivered_at,
        ROUND(JULIANDAY(sh.delivered_at) - JULIANDAY(sh.shipped_at), 1) AS days
    FROM shipping sh
    INNER JOIN orders o ON sh.order_id = o.id
    WHERE sh.shipped_at IS NOT NULL
      AND sh.delivered_at IS NOT NULL
      AND sh.delivered_at < sh.shipped_at;
    ```


---


### 6. 같은 주문에 같은 상품이 중복 등록되었는지 확인하세요.


같은 주문에 같은 상품이 중복 등록되었는지 확인하세요.


**힌트 1:** `GROUP BY order_id, product_id` 후 `HAVING COUNT(*) > 1`로 동일 조합이 2건 이상인 행을 탐지.


??? success "정답"
    ```sql
    SELECT order_id, product_id, COUNT(*) AS cnt
    FROM order_items
    GROUP BY order_id, product_id
    HAVING COUNT(*) > 1;
    ```


---


### 7. 가격, 수량, 평점 등에서 비정상적으로 큰 값을 찾으세요.


가격, 수량, 평점 등에서 비정상적으로 큰 값을 찾으세요.


**힌트 1:** `WHERE total_amount > (SELECT AVG(total_amount) * 10 FROM orders)`처럼 평균의 N배를 초과하는 값이나, 음수/0 값을 확인.


??? success "정답"
    ```sql
    -- 주문 금액이 평균의 10배 이상인 이상치
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE total_amount > (SELECT AVG(total_amount) * 10 FROM orders)
    ORDER BY total_amount DESC;
    ```


---


### 8. 취소된 주문에 배송 완료 기록이 있는 불일치를 찾으세요.


취소된 주문에 배송 완료 기록이 있는 불일치를 찾으세요.


**힌트 1:** `orders JOIN shipping`으로 연결 후 `o.status = 'cancelled' AND sh.status = 'delivered'`인 모순 데이터를 탐지.


??? success "정답"
    ```sql
    SELECT
        o.order_number, o.status, o.cancelled_at,
        sh.status AS ship_status, sh.delivered_at
    FROM orders o
    INNER JOIN shipping sh ON o.id = sh.order_id
    WHERE o.status = 'cancelled'
      AND sh.status = 'delivered';
    ```


---


### 9. 단종(discontinued) 또는 비활성(is_active=0) 상품이 최근에 주문되었는지 확인하세요.


단종(discontinued) 또는 비활성(is_active=0) 상품이 최근에 주문되었는지 확인하세요.


**힌트 1:** 비활성 상품의 최근 주문일(`MAX(ordered_at)`)이 단종일 이후인지 `HAVING`으로 확인.


??? success "정답"
    ```sql
    SELECT
        p.name, p.is_active, p.discontinued_at,
        MAX(o.ordered_at) AS last_ordered
    FROM products p
    INNER JOIN order_items oi ON p.id = oi.product_id
    INNER JOIN orders o ON oi.order_id = o.id
    WHERE p.is_active = 0 OR p.discontinued_at IS NOT NULL
    GROUP BY p.id, p.name, p.is_active, p.discontinued_at
    HAVING MAX(o.ordered_at) > COALESCE(p.discontinued_at, '9999-12-31');
    ```


---


### 10. 주문 수와 결제 수가 1:1로 맞는지 확인하세요.


주문 수와 결제 수가 1:1로 맞는지 확인하세요.


**힌트 1:** 양방향 `LEFT JOIN`으로 확인 -- 주문은 있지만 결제가 없는 경우, 결제는 있지만 주문이 없는 경우를 각각 탐지.


??? success "정답"
    ```sql
    -- 주문은 있는데 결제가 없는 경우
    SELECT o.id, o.order_number
    FROM orders o
    LEFT JOIN payments p ON o.id = p.order_id
    WHERE p.id IS NULL;
    ```


---


### 11. 상품의 현재 가격이 가격 이력의 최신 레코드와 일치하는지 확인하세요.


상품의 현재 가격이 가격 이력의 최신 레코드와 일치하는지 확인하세요.


**힌트 1:** `product_prices`에서 `ended_at IS NULL`(현재 유효 가격)인 행의 가격과 `products.price`를 비교하여 불일치 탐지.


??? success "정답"
    ```sql
    SELECT
        p.name, p.price AS current_price,
        pp.price AS latest_history_price
    FROM products p
    INNER JOIN product_prices pp ON p.id = pp.product_id
    WHERE pp.ended_at IS NULL
      AND p.price <> pp.price;
    ```


---


### 12. 한 쿼리로 주요 품질 지표를 요약하세요.


한 쿼리로 주요 품질 지표를 요약하세요.


**힌트 1:** 각 품질 점검을 스칼라 서브쿼리 `(SELECT COUNT(*) FROM ... WHERE 조건)`로 만들어 하나의 SELECT에 나열.


??? success "정답"
    ```sql
    SELECT
        (SELECT COUNT(*) FROM orders o INNER JOIN customers c ON o.customer_id = c.id WHERE o.ordered_at < c.created_at) AS orders_before_signup,
        (SELECT COUNT(*) FROM payments p LEFT JOIN orders o ON p.order_id = o.id WHERE o.id IS NULL) AS orphan_payments,
        (SELECT COUNT(*) FROM shipping WHERE delivered_at < shipped_at) AS invalid_delivery_dates,
        (SELECT COUNT(*) FROM order_items GROUP BY order_id, product_id HAVING COUNT(*) > 1) AS duplicate_items,
        (SELECT COUNT(*) FROM products WHERE stock_qty < 0) AS negative_stock,
        (SELECT COUNT(*) FROM orders WHERE total_amount <= 0 AND status NOT IN ('cancelled')) AS zero_amount_orders;
    ```


---
