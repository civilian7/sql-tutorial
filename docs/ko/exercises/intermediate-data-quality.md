# 중급 연습: 데이터 품질 점검

실제 데이터에서 이상치, 불일치, 결측 패턴을 탐지하는 12문제입니다. DBA나 데이터 엔지니어의 일상 업무입니다.

---

### 1. 가입 전 주문

고객 가입일보다 주문일이 빠른 주문이 있는지 확인하세요.

??? success "정답"
    ```sql
    SELECT
        o.order_number, o.ordered_at,
        c.name, c.created_at AS signup_date
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    WHERE o.ordered_at < c.created_at;
    ```

    정상적인 데이터라면 0행이어야 합니다.

---

### 2. 고아 레코드 (부모 없는 자식)

주문이 존재하지 않는 결제 레코드가 있는지 확인하세요.

??? success "정답"
    ```sql
    SELECT p.id, p.order_id, p.amount
    FROM payments p
    LEFT JOIN orders o ON p.order_id = o.id
    WHERE o.id IS NULL;
    ```

    ```sql
    -- 다른 테이블도 확인
    SELECT 'order_items' AS tbl, COUNT(*) AS orphans FROM order_items oi LEFT JOIN orders o ON oi.order_id = o.id WHERE o.id IS NULL
    UNION ALL
    SELECT 'shipping', COUNT(*) FROM shipping s LEFT JOIN orders o ON s.order_id = o.id WHERE o.id IS NULL
    UNION ALL
    SELECT 'reviews', COUNT(*) FROM reviews r LEFT JOIN products p ON r.product_id = p.id WHERE p.id IS NULL
    UNION ALL
    SELECT 'cart_items', COUNT(*) FROM cart_items ci LEFT JOIN carts c ON ci.cart_id = c.id WHERE c.id IS NULL;
    ```

---

### 3. NULL 분포 분석

각 테이블의 NULL이 많은 컬럼을 찾으세요.

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

### 4. 상태 일관성 점검

배송 완료(delivered)인데 주문 상태가 아직 shipped인 불일치를 찾으세요.

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

### 5. 날짜 순서 검증

배송완료일이 출고일보다 빠른 비정상 레코드를 찾으세요.

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

### 6. 중복 데이터 탐지

같은 주문에 같은 상품이 중복 등록되었는지 확인하세요.

??? success "정답"
    ```sql
    SELECT order_id, product_id, COUNT(*) AS cnt
    FROM order_items
    GROUP BY order_id, product_id
    HAVING COUNT(*) > 1;
    ```

    ```sql
    -- 고객 이메일 중복도 확인
    SELECT email, COUNT(*) AS cnt
    FROM customers
    GROUP BY email
    HAVING COUNT(*) > 1;
    ```

---

### 7. 범위 이상치 탐지

가격, 수량, 평점 등에서 비정상적으로 큰 값을 찾으세요.

??? success "정답"
    ```sql
    -- 주문 금액이 평균의 10배 이상인 이상치
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE total_amount > (SELECT AVG(total_amount) * 10 FROM orders)
    ORDER BY total_amount DESC;
    ```

    ```sql
    -- 재고가 음수인 상품 (있으면 안 됨)
    SELECT name, stock_qty
    FROM products
    WHERE stock_qty < 0;
    ```

    ```sql
    -- 단가가 0인 주문 상세 (무료 증정?)
    SELECT oi.id, p.name, oi.unit_price, oi.quantity
    FROM order_items oi
    INNER JOIN products p ON oi.product_id = p.id
    WHERE oi.unit_price = 0;
    ```

---

### 8. 취소 주문인데 배송 완료

취소된 주문에 배송 완료 기록이 있는 불일치를 찾으세요.

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

### 9. 비활성 상품의 최근 주문

단종(discontinued) 또는 비활성(is_active=0) 상품이 최근에 주문되었는지 확인하세요.

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

### 10. 테이블 간 건수 정합성

주문 수와 결제 수가 1:1로 맞는지 확인하세요.

??? success "정답"
    ```sql
    -- 주문은 있는데 결제가 없는 경우
    SELECT o.id, o.order_number
    FROM orders o
    LEFT JOIN payments p ON o.id = p.order_id
    WHERE p.id IS NULL;
    ```

    ```sql
    -- 결제는 있는데 주문이 없는 경우
    SELECT p.id, p.order_id
    FROM payments p
    LEFT JOIN orders o ON p.order_id = o.id
    WHERE o.id IS NULL;
    ```

    ```sql
    -- 전체 건수 비교
    SELECT
        (SELECT COUNT(*) FROM orders) AS order_count,
        (SELECT COUNT(*) FROM payments) AS payment_count,
        (SELECT COUNT(*) FROM orders) - (SELECT COUNT(*) FROM payments) AS diff;
    ```

---

### 11. 가격과 가격 이력 일치 여부

상품의 현재 가격이 가격 이력의 최신 레코드와 일치하는지 확인하세요.

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

### 12. 전체 데이터 품질 대시보드

한 쿼리로 주요 품질 지표를 요약하세요.

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
