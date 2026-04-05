# 중급 연습: SQL 디버깅

잘못된 쿼리가 주어집니다. **버그를 찾아 수정**하세요. 실무에서 가장 자주 범하는 실수들입니다.

---

### 1. 매출이 2배로 뻥튀기

아래 쿼리는 2024년 상품별 매출을 구합니다. 그런데 실제보다 매출이 훨씬 크게 나옵니다. 왜일까요?

```sql
-- 버그가 있는 쿼리
SELECT
    p.name,
    SUM(oi.quantity * oi.unit_price) AS revenue,
    AVG(r.rating) AS avg_rating
FROM products AS p
INNER JOIN order_items AS oi ON p.id = oi.product_id
INNER JOIN orders AS o ON oi.order_id = o.id
INNER JOIN reviews AS r ON p.id = r.product_id
WHERE o.ordered_at LIKE '2024%'
GROUP BY p.id, p.name;
```

??? success "정답"
    **원인:** `reviews`와 `order_items`를 동시에 JOIN하면 행이 곱해집니다 (리뷰 3개 × 주문 5개 = 15행).

    ```sql
    -- 수정: 리뷰를 서브쿼리로 분리
    SELECT
        p.name,
        SUM(oi.quantity * oi.unit_price) AS revenue,
        review.avg_rating
    FROM products AS p
    INNER JOIN order_items AS oi ON p.id = oi.product_id
    INNER JOIN orders AS o ON oi.order_id = o.id
    LEFT JOIN (
        SELECT product_id, ROUND(AVG(rating), 2) AS avg_rating
        FROM reviews GROUP BY product_id
    ) AS review ON p.id = review.product_id
    WHERE o.ordered_at LIKE '2024%'
    GROUP BY p.id, p.name, review.avg_rating;
    ```

---

### 2. NULL과 비교

아래 쿼리는 생년월일이 없는 고객을 찾으려 합니다. 결과가 0행입니다. 왜?

```sql
-- 버그가 있는 쿼리
SELECT name, email
FROM customers
WHERE birth_date = NULL;
```

??? success "정답"
    **원인:** NULL은 `=`로 비교할 수 없습니다. `NULL = NULL`도 FALSE입니다.

    ```sql
    -- 수정: IS NULL 사용
    SELECT name, email
    FROM customers
    WHERE birth_date IS NULL;
    ```

---

### 3. LEFT JOIN이 INNER JOIN처럼 동작

리뷰가 없는 상품도 포함하려고 LEFT JOIN을 썼는데, 리뷰 없는 상품이 결과에 없습니다.

```sql
-- 버그가 있는 쿼리
SELECT p.name, p.price, r.rating
FROM products AS p
LEFT JOIN reviews AS r ON p.id = r.product_id
WHERE r.rating >= 3;
```

??? success "정답"
    **원인:** `WHERE r.rating >= 3`이 NULL 행을 제거합니다. LEFT JOIN이 INNER JOIN과 같아집니다.

    ```sql
    -- 수정: 조건을 ON 절로 이동
    SELECT p.name, p.price, r.rating
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id AND r.rating >= 3;
    ```

---

### 4. GROUP BY 누락

아래 쿼리는 카테고리별 상품 수를 구하려 합니다. 에러가 납니다.

```sql
-- 버그가 있는 쿼리
SELECT cat.name, COUNT(*) AS product_count
FROM products AS p
INNER JOIN categories AS cat ON p.category_id = cat.id;
```

??? success "정답"
    **원인:** 집계 함수(COUNT)를 쓰면서 GROUP BY가 없습니다.

    ```sql
    -- 수정: GROUP BY 추가
    SELECT cat.name, COUNT(*) AS product_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    GROUP BY cat.name;
    ```

---

### 5. HAVING vs WHERE 혼동

가격이 10만원 이상인 상품이 5개 이상인 카테고리만 보려 합니다. 에러가 납니다.

```sql
-- 버그가 있는 쿼리
SELECT cat.name, COUNT(*) AS expensive_count
FROM products AS p
INNER JOIN categories AS cat ON p.category_id = cat.id
HAVING p.price >= 100000 AND COUNT(*) >= 5
GROUP BY cat.name;
```

??? success "정답"
    **원인:** 1) 행 필터는 WHERE, 그룹 필터는 HAVING. 2) HAVING은 GROUP BY 뒤에 와야 합니다.

    ```sql
    -- 수정
    SELECT cat.name, COUNT(*) AS expensive_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE p.price >= 100000
    GROUP BY cat.name
    HAVING COUNT(*) >= 5;
    ```

---

### 6. DISTINCT가 필요한 경우

고객별 구매 카테고리 수를 구합니다. 수가 비정상적으로 큽니다.

```sql
-- 버그가 있는 쿼리
SELECT
    c.name,
    COUNT(p.category_id) AS category_count
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
INNER JOIN order_items AS oi ON o.id = oi.order_id
INNER JOIN products AS p ON oi.product_id = p.id
GROUP BY c.id, c.name
ORDER BY category_count DESC
LIMIT 10;
```

??? success "정답"
    **원인:** 같은 카테고리의 상품을 여러 번 사면 중복 카운트됩니다.

    ```sql
    -- 수정: COUNT(DISTINCT ...)
    SELECT
        c.name,
        COUNT(DISTINCT p.category_id) AS category_count
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    GROUP BY c.id, c.name
    ORDER BY category_count DESC
    LIMIT 10;
    ```

---

### 7. 서브쿼리 결과가 여러 행

평균보다 비싼 카테고리의 상품을 찾으려 합니다. 에러가 납니다.

```sql
-- 버그가 있는 쿼리
SELECT name, price
FROM products
WHERE price > (
    SELECT AVG(price) FROM products GROUP BY category_id
);
```

??? success "정답"
    **원인:** 서브쿼리가 카테고리별로 여러 행을 반환하는데, `>`는 단일 값만 비교합니다.

    ```sql
    -- 수정 방법 1: 전체 평균과 비교
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products);

    -- 수정 방법 2: 자기 카테고리 평균과 비교 (상관 서브쿼리)
    SELECT p.name, p.price
    FROM products AS p
    WHERE p.price > (
        SELECT AVG(p2.price)
        FROM products AS p2
        WHERE p2.category_id = p.category_id
    );
    ```

---

### 8. 날짜 범위 누락

2024년 12월 주문을 구하려 합니다. 12월 31일 주문이 빠집니다.

```sql
-- 버그가 있는 쿼리
SELECT COUNT(*) AS december_orders
FROM orders
WHERE ordered_at BETWEEN '2024-12-01' AND '2024-12-31';
```

??? success "정답"
    **원인:** `ordered_at`에 시간이 포함되어 있으면 `'2024-12-31'`은 `'2024-12-31 00:00:00'`과 같아서 그 이후 시간이 빠집니다.

    ```sql
    -- 수정: 시간 끝까지 포함
    SELECT COUNT(*) AS december_orders
    FROM orders
    WHERE ordered_at BETWEEN '2024-12-01' AND '2024-12-31 23:59:59';

    -- 또는 LIKE 사용
    SELECT COUNT(*) AS december_orders
    FROM orders
    WHERE ordered_at LIKE '2024-12%';
    ```

---

### 9. 취소 주문 포함

월별 매출 보고서인데 취소 주문이 매출에 포함되어 있습니다.

```sql
-- 버그가 있는 쿼리
SELECT
    SUBSTR(ordered_at, 1, 7) AS month,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY SUBSTR(ordered_at, 1, 7)
ORDER BY month;
```

??? success "정답"
    **원인:** 취소(cancelled), 반품(returned) 주문을 제외하지 않았습니다.

    ```sql
    -- 수정: 상태 필터 추가
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        SUM(total_amount) AS revenue
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```

---

### 10. 0으로 나누기

반품률을 계산합니다. 판매가 0인 공급업체에서 에러가 납니다.

```sql
-- 버그가 있는 쿼리
SELECT
    s.company_name,
    COUNT(DISTINCT ret.id) AS return_count,
    COUNT(DISTINCT oi.id) AS sale_count,
    100.0 * COUNT(DISTINCT ret.id) / COUNT(DISTINCT oi.id) AS return_rate
FROM suppliers AS s
LEFT JOIN products AS p ON s.id = p.supplier_id
LEFT JOIN order_items AS oi ON p.id = oi.product_id
LEFT JOIN returns AS ret ON ret.order_id = oi.order_id
GROUP BY s.id, s.company_name;
```

??? success "정답"
    **원인:** `sale_count`가 0이면 0으로 나누기 에러.

    ```sql
    -- 수정: NULLIF로 0 나누기 방지
    SELECT
        s.company_name,
        COUNT(DISTINCT ret.id) AS return_count,
        COUNT(DISTINCT oi.id) AS sale_count,
        ROUND(100.0 * COUNT(DISTINCT ret.id)
            / NULLIF(COUNT(DISTINCT oi.id), 0), 2) AS return_rate
    FROM suppliers AS s
    LEFT JOIN products AS p ON s.id = p.supplier_id
    LEFT JOIN order_items AS oi ON p.id = oi.product_id
    LEFT JOIN returns AS ret ON ret.order_id = oi.order_id
    GROUP BY s.id, s.company_name;
    ```

---

### 11. 별칭을 WHERE에서 사용

가격대별 상품 수를 구한 후 필터링하려 합니다. 에러가 납니다.

```sql
-- 버그가 있는 쿼리
SELECT
    CASE WHEN price < 100000 THEN '저가' ELSE '고가' END AS tier,
    COUNT(*) AS cnt
FROM products
WHERE tier = '저가'
GROUP BY tier;
```

??? success "정답"
    **원인:** WHERE는 SELECT의 별칭을 참조할 수 없습니다 (실행 순서: FROM → WHERE → GROUP BY → SELECT).

    ```sql
    -- 수정: 원래 표현식을 WHERE에 사용
    SELECT
        CASE WHEN price < 100000 THEN '저가' ELSE '고가' END AS tier,
        COUNT(*) AS cnt
    FROM products
    WHERE price < 100000
    GROUP BY tier;

    -- 또는 HAVING 사용 (그룹 필터)
    SELECT
        CASE WHEN price < 100000 THEN '저가' ELSE '고가' END AS tier,
        COUNT(*) AS cnt
    FROM products
    GROUP BY tier
    HAVING tier = '저가';
    ```

---

### 12. UNION 컬럼 불일치

주문 이벤트와 문의 이벤트를 합치려 합니다. 에러가 납니다.

```sql
-- 버그가 있는 쿼리
SELECT order_number, total_amount, ordered_at FROM orders
UNION ALL
SELECT title, category, created_at FROM complaints;
```

??? success "정답"
    **원인:** UNION의 각 SELECT는 같은 수의 컬럼, 호환 가능한 타입이어야 합니다. `total_amount`(REAL)와 `category`(TEXT)는 의미가 다릅니다.

    ```sql
    -- 수정: 동일 구조로 맞추기
    SELECT '주문' AS type, order_number AS reference, ordered_at AS event_date
    FROM orders
    UNION ALL
    SELECT '문의' AS type, title AS reference, created_at AS event_date
    FROM complaints
    ORDER BY event_date DESC
    LIMIT 20;
    ```
