# 중급 연습: 서브쿼리와 데이터 변환

서브쿼리, CASE, 문자열 함수, 집합 연산을 연습하는 12문제입니다.

---

### 1. 평균보다 비싼 상품

전체 평균 가격보다 비싼 상품의 이름과 가격을 조회하세요.

**힌트:** `WHERE price > (SELECT AVG(price) FROM products)` 형태의 스칼라 서브쿼리 사용.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC;
    ```

---

### 2. 가장 많이 팔린 상품의 상세 정보

판매 수량 1위 상품의 이름, 카테고리, 총 판매량, 총 매출을 구하세요.

**힌트:** `order_items`를 `products`, `categories`와 JOIN 후 `GROUP BY`로 상품별 집계. `ORDER BY total_sold DESC LIMIT 1`.

??? success "정답"
    ```sql
    SELECT
        p.name,
        cat.name AS category,
        SUM(oi.quantity) AS total_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN orders AS o ON oi.order_id = o.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY p.id, p.name, cat.name
    ORDER BY total_sold DESC
    LIMIT 1;
    ```

---

### 3. 자기 카테고리 평균보다 비싼 상품

각 상품이 속한 카테고리의 평균 가격보다 비싼 상품만 조회하세요.

**힌트:** 카테고리별 평균 가격을 서브쿼리(인라인 뷰)로 구한 뒤, `JOIN`으로 연결하여 `WHERE p.price > cat_avg.avg_price`.

??? success "정답"
    ```sql
    SELECT p.name, p.price, cat.name AS category, cat_avg.avg_price
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN (
        SELECT category_id, ROUND(AVG(price), 2) AS avg_price
        FROM products
        GROUP BY category_id
    ) AS cat_avg ON p.category_id = cat_avg.category_id
    WHERE p.price > cat_avg.avg_price
    ORDER BY p.price DESC
    LIMIT 20;
    ```

---

### 4. 리뷰 평점 높은데 매출 낮은 상품

평균 평점 4.5 이상이지만 총 매출이 하위 50%인 상품을 찾으세요.

**힌트:** CTE로 상품별 평균 평점과 매출을 구한 뒤, 평점 필터 + 매출이 전체 평균 미만인 조건으로 필터링.

??? success "정답"
    ```sql
    WITH product_stats AS (
        SELECT
            p.id,
            p.name,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM products AS p
        LEFT JOIN reviews AS r ON p.id = r.product_id
        LEFT JOIN order_items AS oi ON p.id = oi.product_id
        GROUP BY p.id, p.name
        HAVING COUNT(r.id) >= 3
    )
    SELECT name, avg_rating, ROUND(revenue, 2) AS revenue
    FROM product_stats
    WHERE avg_rating >= 4.5
      AND revenue < (SELECT AVG(revenue) FROM product_stats)
    ORDER BY avg_rating DESC;
    ```

---

### 5. 주문 금액 등급 분류

주문을 금액 기준으로 소액(5만 미만), 중액(5~20만), 대액(20~50만), 고액(50만 이상)으로 분류하고 각 등급의 건수와 비율을 구하세요.

**힌트:** `CASE WHEN total_amount < 50000 THEN '소액' ...`으로 등급 분류 후 `GROUP BY`. 비율은 윈도우 함수 `SUM(COUNT(*)) OVER ()` 활용.

??? success "정답"
    ```sql
    SELECT
        CASE
            WHEN total_amount < 50000 THEN '소액 (5만 미만)'
            WHEN total_amount < 200000 THEN '중액 (5~20만)'
            WHEN total_amount < 500000 THEN '대액 (20~50만)'
            ELSE '고액 (50만 이상)'
        END AS tier,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
        ROUND(AVG(total_amount), 2) AS avg_amount
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY tier
    ORDER BY MIN(total_amount);
    ```

---

### 6. 위시리스트에만 있고 구매하지 않은 상품

위시리스트에 담았지만 한 번도 주문하지 않은 고객-상품 조합을 찾으세요.

**힌트:** `NOT EXISTS`로 해당 고객이 해당 상품을 주문한 이력이 있는지 확인하는 상관 서브쿼리 사용.

??? success "정답"
    ```sql
    SELECT
        c.name AS customer,
        p.name AS product,
        w.created_at AS wishlisted_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products AS p ON w.product_id = p.id
    WHERE NOT EXISTS (
        SELECT 1
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.customer_id = w.customer_id
          AND oi.product_id = w.product_id
          AND o.status NOT IN ('cancelled')
    )
    ORDER BY w.created_at DESC
    LIMIT 20;
    ```

---

### 7. 카드 발급사별 분석

카드 결제의 발급사(card_issuer)별 건수, 평균 결제 금액, 할부 비율을 구하세요.

**힌트:** `WHERE method = 'card'`로 카드 결제만 필터 후 `GROUP BY card_issuer`. 할부 비율은 `CASE WHEN installment_months > 0` 조건부 집계.

??? success "정답"
    ```sql
    SELECT
        card_issuer,
        COUNT(*) AS tx_count,
        ROUND(AVG(amount), 2) AS avg_amount,
        ROUND(100.0 * SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS installment_pct
    FROM payments
    WHERE method = 'card'
      AND card_issuer IS NOT NULL
    GROUP BY card_issuer
    ORDER BY tx_count DESC;
    ```

---

### 8. 문의 채널별 해결률

고객 문의 채널(channel)별 건수, 해결률, 평균 처리 시간을 구하세요.

**힌트:** `GROUP BY channel`로 집계. 해결률은 `CASE WHEN status IN ('resolved','closed')`로 조건부 카운트. 처리 시간은 `JULIANDAY` 차이.

??? success "정답"
    ```sql
    SELECT
        channel,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN status IN ('resolved', 'closed') THEN 1 ELSE 0 END) / COUNT(*), 1) AS resolution_pct,
        ROUND(AVG(CASE
            WHEN resolved_at IS NOT NULL
            THEN JULIANDAY(resolved_at) - JULIANDAY(created_at)
        END), 1) AS avg_days
    FROM complaints
    GROUP BY channel
    ORDER BY total DESC;
    ```

---

### 9. 리뷰와 주문을 모두 한 고객

리뷰도 작성하고 위시리스트에도 상품을 등록한 고객의 이름, 리뷰 수, 위시리스트 수를 구하세요.

**힌트:** 리뷰와 위시리스트를 각각 서브쿼리로 집계한 뒤, 두 서브쿼리를 `INNER JOIN`으로 연결 (양쪽 모두 존재하는 고객만).

??? success "정답"
    ```sql
    SELECT
        c.name,
        r_cnt.review_count,
        w_cnt.wishlist_count
    FROM customers AS c
    INNER JOIN (
        SELECT customer_id, COUNT(*) AS review_count
        FROM reviews GROUP BY customer_id
    ) AS r_cnt ON c.id = r_cnt.customer_id
    INNER JOIN (
        SELECT customer_id, COUNT(*) AS wishlist_count
        FROM wishlists GROUP BY customer_id
    ) AS w_cnt ON c.id = w_cnt.customer_id
    ORDER BY r_cnt.review_count DESC
    LIMIT 15;
    ```

---

### 10. 상품 이미지 분석

상품별 이미지 수를 구하고, 이미지가 없는 상품도 포함하세요.

**힌트:** `products LEFT JOIN product_images`로 이미지 없는 상품도 포함. `COUNT(pi.id)`는 NULL을 세지 않으므로 0이 됨.

??? success "정답"
    ```sql
    SELECT
        p.name,
        COUNT(pi.id) AS image_count,
        SUM(CASE WHEN pi.is_primary = 1 THEN 1 ELSE 0 END) AS has_primary
    FROM products AS p
    LEFT JOIN product_images AS pi ON p.id = pi.product_id
    GROUP BY p.id, p.name
    ORDER BY image_count ASC
    LIMIT 20;
    ```

---

### 11. 장바구니 전환율

장바구니 상태(active/converted/abandoned)별 건수와 비율을 구하세요.

**힌트:** `GROUP BY status`로 집계. 비율은 `100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()`로 전체 대비 비율 계산.

??? success "정답"
    ```sql
    SELECT
        status,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM carts
    GROUP BY status
    ORDER BY cnt DESC;
    ```

---

### 12. 두 테이블 합치기 (UNION)

주문 취소 이벤트와 반품 요청 이벤트를 하나의 타임라인으로 합치세요. 최근 20건.

**힌트:** `UNION ALL`로 두 SELECT를 합치되, 컬럼 수와 의미를 맞춰야 함. 이벤트 유형 구분 컬럼 추가.

??? success "정답"
    ```sql
    SELECT '취소' AS event_type, order_number AS reference, cancelled_at AS event_date
    FROM orders
    WHERE status = 'cancelled' AND cancelled_at IS NOT NULL
    UNION ALL
    SELECT '반품' AS event_type, CAST(order_id AS TEXT), requested_at
    FROM returns
    WHERE requested_at IS NOT NULL
    ORDER BY event_date DESC
    LIMIT 20;
    ```
