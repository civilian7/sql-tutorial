# 초급 연습: 빈칸 채우기

쿼리의 핵심 부분이 `___`로 비어 있습니다. 올바른 SQL을 채워 넣으세요.

---

### 1. WHERE 조건

VIP 등급 고객만 조회합니다.

```sql
SELECT name, email, grade
FROM customers
WHERE ___
ORDER BY name;
```

??? success "정답"
    ```sql
    SELECT name, email, grade
    FROM customers
    WHERE grade = 'VIP'
    ORDER BY name;
    ```

---

### 2. ORDER BY

상품을 가격이 높은 순으로 정렬합니다.

```sql
SELECT name, price
FROM products
ORDER BY ___
LIMIT 10;
```

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 10;
    ```

---

### 3. 집계 함수

카테고리별 상품 수를 구합니다.

```sql
SELECT category_id, ___ AS product_count
FROM products
GROUP BY category_id;
```

??? success "정답"
    ```sql
    SELECT category_id, COUNT(*) AS product_count
    FROM products
    GROUP BY category_id;
    ```

---

### 4. HAVING

주문이 10건 이상인 고객만 필터링합니다.

```sql
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
___ ;
```

??? success "정답"
    ```sql
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    HAVING COUNT(*) >= 10;
    ```

---

### 5. JOIN 조건

상품과 카테고리를 연결합니다.

```sql
SELECT p.name, cat.name AS category
FROM products AS p
INNER JOIN categories AS cat ON ___
LIMIT 10;
```

??? success "정답"
    ```sql
    SELECT p.name, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LIMIT 10;
    ```

---

### 6. LEFT JOIN + IS NULL

주문이 없는 고객을 찾습니다.

```sql
SELECT c.name, c.email
FROM customers AS c
LEFT JOIN orders AS o ON c.id = o.customer_id
WHERE ___ ;
```

??? success "정답"
    ```sql
    SELECT c.name, c.email
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL;
    ```

---

### 7. BETWEEN

2024년 1분기(1~3월) 주문을 조회합니다.

```sql
SELECT order_number, total_amount, ordered_at
FROM orders
WHERE ordered_at ___ ;
```

??? success "정답"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE ordered_at BETWEEN '2024-01-01' AND '2024-03-31 23:59:59';
    ```

---

### 8. CASE 표현식

재고 상태를 분류합니다.

```sql
SELECT
    name,
    stock_qty,
    CASE
        ___
    END AS stock_status
FROM products;
```

??? success "정답"
    ```sql
    SELECT
        name,
        stock_qty,
        CASE
            WHEN stock_qty = 0 THEN '품절'
            WHEN stock_qty <= 10 THEN '부족'
            WHEN stock_qty <= 100 THEN '보통'
            ELSE '충분'
        END AS stock_status
    FROM products;
    ```

---

### 9. COALESCE

생년월일이 없으면 '미입력'으로 표시합니다.

```sql
SELECT
    name,
    ___ AS birth_date
FROM customers
LIMIT 10;
```

??? success "정답"
    ```sql
    SELECT
        name,
        COALESCE(birth_date, '미입력') AS birth_date
    FROM customers
    LIMIT 10;
    ```

---

### 10. 서브쿼리

평균 가격보다 비싼 상품을 조회합니다.

```sql
SELECT name, price
FROM products
WHERE price > ___
ORDER BY price DESC;
```

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC;
    ```

---

### 11. GROUP BY + 여러 집계

등급별 고객 수, 평균 적립금, 최대 적립금을 구합니다.

```sql
SELECT
    grade,
    ___ AS customer_count,
    ___ AS avg_points,
    ___ AS max_points
FROM customers
GROUP BY grade;
```

??? success "정답"
    ```sql
    SELECT
        grade,
        COUNT(*) AS customer_count,
        ROUND(AVG(point_balance), 0) AS avg_points,
        MAX(point_balance) AS max_points
    FROM customers
    GROUP BY grade;
    ```

---

### 12. LIKE 패턴

이메일이 testmail.kr 도메인인 고객을 찾습니다.

```sql
SELECT name, email
FROM customers
WHERE email LIKE ___
LIMIT 10;
```

??? success "정답"
    ```sql
    SELECT name, email
    FROM customers
    WHERE email LIKE '%@testmail.kr'
    LIMIT 10;
    ```

---

### 13. 날짜 추출

주문의 연도와 월을 추출합니다.

```sql
SELECT
    ___ AS year,
    ___ AS month,
    COUNT(*) AS order_count
FROM orders
GROUP BY year, month
ORDER BY year, month;
```

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        SUBSTR(ordered_at, 6, 2) AS month,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY year, month
    ORDER BY year, month;
    ```

---

### 14. IN 연산자

결제 상태가 completed 또는 refunded인 건만 조회합니다.

```sql
SELECT id, order_id, method, amount, status
FROM payments
WHERE status ___ ;
```

??? success "정답"
    ```sql
    SELECT id, order_id, method, amount, status
    FROM payments
    WHERE status IN ('completed', 'refunded');
    ```

---

### 15. 다중 테이블 JOIN

주문번호, 고객명, 결제 금액, 배송 상태를 한 번에 조회합니다.

```sql
SELECT
    o.order_number,
    c.name AS customer,
    p.amount AS paid,
    sh.status AS shipping_status
FROM orders AS o
INNER JOIN customers AS c ON ___
INNER JOIN payments AS p ON ___
LEFT JOIN shipping AS sh ON ___
ORDER BY o.ordered_at DESC
LIMIT 5;
```

??? success "정답"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer,
        p.amount AS paid,
        sh.status AS shipping_status
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    INNER JOIN payments AS p ON o.id = p.order_id
    LEFT JOIN shipping AS sh ON o.id = sh.order_id
    ORDER BY o.ordered_at DESC
    LIMIT 5;
    ```
