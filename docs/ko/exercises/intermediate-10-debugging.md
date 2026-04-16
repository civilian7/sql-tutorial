# SQL 디버깅 — 중급

!!! info "사용 테이블"
    `customers` — 고객 (등급, 포인트, 가입채널)  
    `orders` — 주문 (상태, 금액, 일시)  
    `order_items` — 주문 상세 (수량, 단가)  
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `categories` — 카테고리 (부모-자식 계층)  
    `suppliers` — 공급업체 (업체명, 연락처)  
    `reviews` — 리뷰 (평점, 내용)  
    `shipping` — 배송 (택배사, 추적번호, 상태)  
    `payments` — 결제 (방법, 금액, 상태)  

!!! abstract "학습 범위"
    JOIN, 서브쿼리, 날짜 함수, 집계, UNION, DML 등 중급 문법(08~17강)에서 발생하는 오류 진단 및 수정

!!! info "시작하기 전에"
    실무에서 SQL을 작성하다 보면 문법 에러보다 **논리적 오류**가 더 흔합니다.
    쿼리가 실행은 되지만 결과가 틀리거나, 예상치 못한 에러가 발생하는 경우를 다룹니다.

---

## 기초 (1~8): JOIN과 테이블 별칭 오류

### 문제 1

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT name, order_number, total_amount
FROM customers
INNER JOIN orders ON customer_id = id;
```

??? tip "힌트"
    두 테이블 모두 `id` 칼럼이 있습니다. `customer_id = id`가 어느 테이블의 `id`인지 모호합니다.

??? success "정답"
    **오류:** JOIN 조건에서 칼럼 소속 테이블이 모호합니다. `customer_id`와 `id`가 각각 어느 테이블의 칼럼인지 명시하지 않았습니다.

    **수정:**

    ```sql
    SELECT c.name, o.order_number, o.total_amount
    FROM customers AS c
    INNER JOIN orders AS o ON o.customer_id = c.id;
    ```

---

### 문제 2

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT c.name, o.order_number, oi.quantity
FROM customers AS c
INNER JOIN order_items AS oi ON o.id = oi.order_id
INNER JOIN orders AS o ON c.id = o.customer_id
LIMIT 10;
```

??? tip "힌트"
    SQL에서 테이블 별칭은 `FROM`/`JOIN` 절에 나타난 순서대로 정의됩니다. `o`를 사용하기 전에 정의해야 합니다.

??? success "정답"
    **오류:** `orders AS o`가 두 번째 JOIN에서 정의되는데, 첫 번째 JOIN에서 이미 `o.id`를 참조합니다. 별칭이 아직 존재하지 않습니다.

    **수정:**

    ```sql
    SELECT c.name, o.order_number, oi.quantity
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    LIMIT 10;
    ```

---

### 문제 3

다음 쿼리의 오류를 찾고 수정하세요. 주문이 없는 고객도 포함하려 했습니다.

```sql
SELECT c.name, COUNT(o.id) AS order_count
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
GROUP BY c.id, c.name
ORDER BY order_count DESC;
```

??? tip "힌트"
    INNER JOIN은 양쪽 모두에 매칭이 있는 행만 반환합니다. 주문이 없는 고객을 포함하려면 어떤 JOIN을 써야 할까요?

??? success "정답"
    **오류:** `INNER JOIN`은 주문이 있는 고객만 반환합니다. 주문이 없는 고객은 결과에서 제외됩니다.

    **수정:**

    ```sql
    SELECT c.name, COUNT(o.id) AS order_count
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name
    ORDER BY order_count ASC
    LIMIT 20;
    ```

---

### 문제 4

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT p.name, cat.name, s.company_name
FROM products AS p
INNER JOIN categories AS cat ON p.id = cat.id
INNER JOIN suppliers AS s ON p.supplier_id = s.id
LIMIT 10;
```

??? tip "힌트"
    `products`와 `categories`를 연결하는 FK 칼럼이 `p.id = cat.id`가 맞는지 확인하세요. 두 테이블의 관계를 나타내는 칼럼은 무엇인가요?

??? success "정답"
    **오류:** JOIN 조건이 잘못되었습니다. `p.id = cat.id`는 상품 ID와 카테고리 ID를 비교하는 것으로, FK 관계가 아닙니다. `products.category_id`가 `categories.id`를 참조합니다.

    **수정:**

    ```sql
    SELECT p.name, cat.name, s.company_name
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    LIMIT 10;
    ```

---

### 문제 5

다음 쿼리의 오류를 찾고 수정하세요. 각 공급업체의 상품 수를 구합니다.

```sql
SELECT company_name, COUNT(*) AS product_count
FROM products AS p
INNER JOIN suppliers AS s ON p.supplier_id = s.id
GROUP BY s.id;
```

??? tip "힌트"
    `GROUP BY`에 포함되지 않은 칼럼이 `SELECT`에 있습니다. SQLite에서는 동작할 수 있지만, 다른 DB에서는 에러가 납니다.

??? success "정답"
    **오류:** `SELECT`에 `company_name`이 있지만 `GROUP BY`에는 `s.id`만 있습니다. `company_name`의 소속 테이블도 명시되지 않았습니다.

    **수정:**

    ```sql
    SELECT s.company_name, COUNT(*) AS product_count
    FROM products AS p
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    GROUP BY s.id, s.company_name;
    ```

---

### 문제 6

다음 쿼리의 오류를 찾고 수정하세요. 고객별 최근 주문일을 구합니다.

```sql
SELECT c.name, c.email, o.ordered_at AS last_order
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
WHERE o.ordered_at = MAX(o.ordered_at)
GROUP BY c.id;
```

??? tip "힌트"
    `WHERE` 절에서는 집계 함수(`MAX`, `SUM` 등)를 사용할 수 없습니다. 집계 결과로 필터링하려면 다른 방법을 써야 합니다.

??? success "정답"
    **오류:** `WHERE`에서 `MAX()`를 직접 사용할 수 없습니다. 또한 고객별 최근 주문을 구하려면 서브쿼리나 GROUP BY 후 MAX를 사용해야 합니다.

    **수정:**

    ```sql
    SELECT c.name, c.email, MAX(o.ordered_at) AS last_order
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.email;
    ```

---

### 문제 7

다음 쿼리의 오류를 찾고 수정하세요. 리뷰가 있는 상품만 보려 합니다.

```sql
SELECT p.name, p.price, r.rating
FROM products AS p, reviews AS r
WHERE p.id = r.product_id
  AND p.price > 100000
ORDER BY p.price DESC
LIMIT 10;
```

??? tip "힌트"
    쿼리 자체는 동작하지만, 한 상품에 리뷰가 여러 개면 상품이 중복 출력됩니다. 상품당 하나의 결과를 원한다면?

??? success "정답"
    **오류:** 암시적 JOIN(쉼표 구분)을 사용했고, 한 상품에 리뷰가 여러 개면 같은 상품이 반복됩니다.

    **수정:**

    ```sql
    -- 방법 1: 명시적 JOIN + 집계
    SELECT p.name, p.price, ROUND(AVG(r.rating), 1) AS avg_rating
    FROM products AS p
    INNER JOIN reviews AS r ON p.id = r.product_id
    WHERE p.price > 100000
    GROUP BY p.id, p.name, p.price
    ORDER BY p.price DESC
    LIMIT 10;

    -- 방법 2: EXISTS로 존재 여부만 확인
    SELECT p.name, p.price
    FROM products AS p
    WHERE p.price > 100000
      AND EXISTS (SELECT 1 FROM reviews WHERE product_id = p.id)
    ORDER BY p.price DESC
    LIMIT 10;
    ```

---

### 문제 8

다음 쿼리의 오류를 찾고 수정하세요. 배송 중인 주문의 고객 이름을 구합니다.

```sql
SELECT c.name, o.order_number, sh.tracking_number
FROM customers AS c
LEFT JOIN orders AS o ON c.id = o.customer_id
LEFT JOIN shipping AS sh ON o.id = sh.order_id
WHERE sh.status = 'shipped';
```

??? tip "힌트"
    `LEFT JOIN` 후 `WHERE`에서 오른쪽 테이블의 칼럼을 필터링하면, NULL 행이 제거되어 사실상 INNER JOIN과 같아집니다.

??? success "정답"
    **오류:** 배송 중인 주문만 원한다면 LEFT JOIN이 불필요합니다. LEFT JOIN을 쓴 의도가 "주문이 없는 고객도 포함"이라면 WHERE 조건이 그 의도를 무효화합니다.

    **수정:**

    ```sql
    -- 배송 중인 주문의 고객만 필요하므로 INNER JOIN이 적절
    SELECT c.name, o.order_number, sh.tracking_number
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    INNER JOIN shipping AS sh ON o.id = sh.order_id
    WHERE sh.status = 'shipped';
    ```

---

## 응용 (9~16): 카디널리티, 집계, 서브쿼리, 날짜

### 문제 9

다음 쿼리의 오류를 찾고 수정하세요. 상품별 매출과 평균 평점을 함께 구합니다. 그런데 매출이 실제보다 훨씬 크게 나옵니다.

```sql
SELECT
    p.name,
    SUM(oi.quantity * oi.unit_price) AS revenue,
    ROUND(AVG(r.rating), 1) AS avg_rating
FROM products AS p
INNER JOIN order_items AS oi ON p.id = oi.product_id
INNER JOIN reviews AS r ON p.id = r.product_id
GROUP BY p.id, p.name
ORDER BY revenue DESC
LIMIT 10;
```

??? tip "힌트"
    `order_items`와 `reviews`를 동시에 JOIN하면 행이 곱해집니다 (카디널리티 폭발). 주문 3건 x 리뷰 2건 = 6행이 됩니다.

??? success "정답"
    **오류:** 1:N 관계 두 개를 동시에 JOIN하면 M x N 행이 생겨 매출이 부풀어집니다.

    **수정:**

    ```sql
    SELECT
        p.name,
        SUM(oi.quantity * oi.unit_price) AS revenue,
        sub_r.avg_rating
    FROM products AS p
    INNER JOIN order_items AS oi ON p.id = oi.product_id
    LEFT JOIN (
        SELECT product_id, ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews
        GROUP BY product_id
    ) AS sub_r ON p.id = sub_r.product_id
    GROUP BY p.id, p.name, sub_r.avg_rating
    ORDER BY revenue DESC
    LIMIT 10;
    ```

---

### 문제 10

다음 쿼리의 오류를 찾고 수정하세요. 총 주문 금액이 100만원 이상인 고객만 보려 합니다.

```sql
SELECT c.name, SUM(o.total_amount) AS total_spent
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
WHERE SUM(o.total_amount) >= 1000000
GROUP BY c.id, c.name;
```

??? tip "힌트"
    `WHERE` 절에서는 집계 함수를 사용할 수 없습니다. 그룹화 후 필터링에 쓰는 절은 무엇인가요?

??? success "정답"
    **오류:** `WHERE`에서 `SUM()`을 사용했습니다. 집계 결과 필터링은 `HAVING`에서 해야 합니다.

    **수정:**

    ```sql
    SELECT c.name, SUM(o.total_amount) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name
    HAVING SUM(o.total_amount) >= 1000000
    ORDER BY total_spent DESC;
    ```

---

### 문제 11

다음 쿼리의 오류를 찾고 수정하세요. 자기 카테고리 평균보다 비싼 상품을 찾습니다.

```sql
SELECT p.name, p.price
FROM products AS p
WHERE p.price > (
    SELECT AVG(price)
    FROM products
    GROUP BY category_id
);
```

??? tip "힌트"
    `>` 연산자는 단일 값과만 비교할 수 있습니다. 서브쿼리가 `GROUP BY`로 여러 행을 반환하면 에러가 납니다.

??? success "정답"
    **오류:** 서브쿼리가 카테고리별 평균 여러 행을 반환하므로 `>` 비교가 불가능합니다. 상관 서브쿼리로 자기 카테고리의 평균만 구해야 합니다.

    **수정:**

    ```sql
    SELECT p.name, p.price
    FROM products AS p
    WHERE p.price > (
        SELECT AVG(p2.price)
        FROM products AS p2
        WHERE p2.category_id = p.category_id
    )
    ORDER BY p.price DESC;
    ```

---

### 문제 12

다음 쿼리의 오류를 찾고 수정하세요. 2024년 3분기(7~9월) 주문 수를 구합니다. 실제보다 적게 나옵니다.

```sql
SELECT COUNT(*) AS q3_orders
FROM orders
WHERE ordered_at BETWEEN '2024-07-01' AND '2024-09-30';
```

??? tip "힌트"
    `ordered_at`에 시간 정보가 포함되어 있다면, `'2024-09-30'`은 `'2024-09-30 00:00:00'`과 같습니다. 9월 30일 오후 주문이 빠집니다.

??? success "정답"
    **오류:** `BETWEEN`의 끝값이 `'2024-09-30'` (= 00:00:00)이므로 9월 30일의 00:00:00 이후 주문이 누락됩니다.

    **수정:**

    ```sql
    -- 방법 1: 끝값에 시간 끝까지 포함
    SELECT COUNT(*) AS q3_orders
    FROM orders
    WHERE ordered_at BETWEEN '2024-07-01' AND '2024-09-30 23:59:59';

    -- 방법 2: LIKE로 월 패턴 매칭 (더 안전)
    SELECT COUNT(*) AS q3_orders
    FROM orders
    WHERE ordered_at >= '2024-07-01'
      AND ordered_at < '2024-10-01';
    ```

---

### 문제 13

다음 쿼리의 오류를 찾고 수정하세요. 주문일 기준 경과 일수를 구합니다. 결과가 NULL로 나옵니다.

```sql
SELECT
    order_number,
    ordered_at,
    DATEDIFF('2025-01-01', ordered_at) AS days_elapsed
FROM orders
LIMIT 10;
```

??? tip "힌트"
    SQLite에는 `DATEDIFF` 함수가 없습니다. SQLite에서 날짜 차이를 구하는 함수는 무엇인가요?

??? success "정답"
    **오류:** `DATEDIFF`는 MySQL 함수입니다. SQLite에서는 `JULIANDAY()` 함수로 날짜 차이를 계산합니다.

    **수정:**

    ```sql
    SELECT
        order_number,
        ordered_at,
        CAST(JULIANDAY('2025-01-01') - JULIANDAY(ordered_at) AS INTEGER) AS days_elapsed
    FROM orders
    LIMIT 10;
    ```

---

### 문제 14

다음 쿼리의 오류를 찾고 수정하세요. 월별 신규 고객 수를 구합니다. 에러가 납니다.

```sql
SELECT
    STRFTIME('%Y-%m', created_at) AS month,
    COUNT(*) AS new_customers
FROM customers
GROUP BY month
HAVING new_customers > 100
ORDER BY month;
```

??? tip "힌트"
    `HAVING`에서 SELECT 별칭을 사용할 수 있는 DB와 없는 DB가 있습니다. SQLite에서는 동작하지만, 표준 SQL에서는 집계 표현식을 직접 써야 합니다. 이 쿼리의 진짜 문제를 찾아보세요.

??? success "정답"
    **오류:** 이 쿼리는 SQLite에서 실제로 동작합니다. 하지만 `HAVING new_customers > 100` 대신 `HAVING COUNT(*) > 100`이 표준 SQL입니다. 만약 에러가 난다면 `STRFTIME`의 대소문자(`strftime`)나 날짜 형식 문제일 수 있습니다.

    **수정:**

    ```sql
    SELECT
        STRFTIME('%Y-%m', created_at) AS month,
        COUNT(*) AS new_customers
    FROM customers
    GROUP BY STRFTIME('%Y-%m', created_at)
    HAVING COUNT(*) > 100
    ORDER BY month;
    ```

---

### 문제 15

다음 쿼리의 오류를 찾고 수정하세요. 상위 10% 고가 상품을 구합니다.

```sql
SELECT name, price
FROM products
WHERE price > (SELECT AVG(price) * 1.1 FROM products)
ORDER BY price DESC;
```

??? tip "힌트"
    "상위 10%"는 "평균의 110%"가 아닙니다. 상위 10%는 전체 중 가격 순위가 상위 10%에 해당하는 것을 의미합니다.

??? success "정답"
    **오류:** `AVG(price) * 1.1`은 "평균 가격의 110%"이지, "상위 10% 가격"이 아닙니다. 상위 10%는 전체 상품의 90번째 백분위 이상입니다.

    **수정:**

    ```sql
    -- 전체 상품 중 상위 10%
    SELECT name, price
    FROM products
    WHERE price >= (
        SELECT price FROM products
        ORDER BY price DESC
        LIMIT 1 OFFSET (SELECT COUNT(*) / 10 FROM products)
    )
    ORDER BY price DESC;
    ```

---

### 문제 16

다음 쿼리의 오류를 찾고 수정하세요. 카테고리별로 리뷰 평균이 4.0 이상인 카테고리를 구합니다.

```sql
SELECT cat.name, AVG(r.rating) AS avg_rating
FROM categories AS cat
INNER JOIN products AS p ON cat.id = p.category_id
LEFT JOIN reviews AS r ON p.id = r.product_id
GROUP BY cat.id, cat.name
HAVING avg_rating >= 4.0
ORDER BY avg_rating DESC;
```

??? tip "힌트"
    리뷰가 없는 상품은 `r.rating`이 NULL입니다. `AVG`는 NULL을 무시하므로 결과 자체는 맞을 수 있지만, 리뷰가 0건인 카테고리는 `avg_rating`이 NULL이 되어 `>= 4.0` 비교에서 제외됩니다. 이것이 의도한 동작인지 확인하세요.

??? success "정답"
    **오류:** 논리적으로 두 가지 문제가 있습니다. (1) 리뷰가 없는 카테고리는 AVG가 NULL이므로 자동 제외됩니다 — 이는 의도된 동작일 수 있습니다. (2) `HAVING avg_rating`은 SQLite에서는 동작하지만 표준 SQL에서는 `HAVING AVG(r.rating)`으로 써야 합니다. 또한 리뷰가 극소수인 카테고리도 4.0 이상이 될 수 있으므로 최소 리뷰 수 조건을 추가하는 것이 좋습니다.

    **수정:**

    ```sql
    SELECT cat.name,
           ROUND(AVG(r.rating), 2) AS avg_rating,
           COUNT(r.id) AS review_count
    FROM categories AS cat
    INNER JOIN products AS p ON cat.id = p.category_id
    INNER JOIN reviews AS r ON p.id = r.product_id
    GROUP BY cat.id, cat.name
    HAVING AVG(r.rating) >= 4.0
       AND COUNT(r.id) >= 10
    ORDER BY avg_rating DESC;
    ```

---

## 실전 (17~25): UNION, NULL, DML, 복합 진단

### 문제 17

다음 쿼리의 오류를 찾고 수정하세요. 주문 이벤트와 결제 이벤트를 하나로 합칩니다.

```sql
SELECT order_number, total_amount, status, ordered_at
FROM orders
UNION ALL
SELECT order_id, amount, status, paid_at
FROM payments;
```

??? tip "힌트"
    `UNION ALL`은 칼럼 수와 타입이 호환되어야 합니다. `order_number`(TEXT)와 `order_id`(INTEGER)를 합치면 의미가 맞을까요?

??? success "정답"
    **오류:** 칼럼의 의미가 불일치합니다. `order_number`는 문자열이고 `order_id`는 정수입니다. 또한 두 `status` 칼럼의 값 도메인이 다릅니다 (주문 상태 vs 결제 상태).

    **수정:**

    ```sql
    SELECT '주문' AS event_type,
           order_number AS reference,
           total_amount AS amount,
           status,
           ordered_at AS event_at
    FROM orders
    UNION ALL
    SELECT '결제' AS event_type,
           CAST(order_id AS TEXT) AS reference,
           amount,
           status,
           paid_at AS event_at
    FROM payments
    WHERE paid_at IS NOT NULL
    ORDER BY event_at DESC
    LIMIT 20;
    ```

---

### 문제 18

다음 쿼리의 오류를 찾고 수정하세요. LEFT JOIN으로 리뷰가 없는 상품도 포함했는데, 총 리뷰 수 조건을 추가하니 리뷰 없는 상품이 사라졌습니다.

```sql
SELECT p.name, p.price, COUNT(r.id) AS review_count
FROM products AS p
LEFT JOIN reviews AS r ON p.id = r.product_id
WHERE r.rating >= 3 OR r.rating IS NULL
GROUP BY p.id, p.name, p.price
HAVING review_count <= 5
ORDER BY p.price DESC;
```

??? tip "힌트"
    `WHERE r.rating >= 3`은 LEFT JOIN의 NULL 행을 제거합니다. `OR r.rating IS NULL`로 복구하려 했지만, 리뷰가 있으면서 rating < 3인 행은 제외됩니다. 조건 위치를 재고하세요.

??? success "정답"
    **오류:** WHERE에서 오른쪽 테이블 칼럼을 필터링하면 LEFT JOIN 효과가 손상됩니다. 평점 3 이상인 리뷰만 세면서 상품은 모두 포함하려면 조건을 ON 절로 옮겨야 합니다.

    **수정:**

    ```sql
    SELECT p.name, p.price, COUNT(r.id) AS review_count
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id AND r.rating >= 3
    GROUP BY p.id, p.name, p.price
    HAVING COUNT(r.id) <= 5
    ORDER BY p.price DESC
    LIMIT 20;
    ```

---

### 문제 19

다음 쿼리의 오류를 찾고 수정하세요. GROUP BY와 비집계 칼럼이 섞여 있습니다.

```sql
SELECT
    c.name,
    c.email,
    c.grade,
    COUNT(o.id) AS order_count,
    SUM(o.total_amount) AS total_spent
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
GROUP BY c.name;
```

??? tip "힌트"
    `GROUP BY c.name`만 했는데 `SELECT`에 `c.email`, `c.grade`가 있습니다. 동명이인이 있으면 어떤 email/grade를 표시할까요?

??? success "정답"
    **오류:** `GROUP BY`에 `c.name`만 있으므로 동명이인의 `email`과 `grade`가 어떤 값이 나올지 비결정적입니다. 고객을 유일하게 식별하는 `c.id`로 그룹화해야 합니다.

    **수정:**

    ```sql
    SELECT
        c.name,
        c.email,
        c.grade,
        COUNT(o.id) AS order_count,
        SUM(o.total_amount) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.email, c.grade
    ORDER BY total_spent DESC
    LIMIT 20;
    ```

---

### 문제 20

다음 쿼리의 오류를 찾고 수정하세요. 새 상품을 삽입하려 합니다.

```sql
INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, created_at, updated_at)
VALUES (1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000);
```

??? tip "힌트"
    VALUES의 값 개수와 칼럼 목록의 칼럼 수를 하나씩 세어보세요.

??? success "정답"
    **오류:** 칼럼은 9개(`category_id` ~ `updated_at`)인데 VALUES 값은 7개입니다. `created_at`과 `updated_at` 값이 빠져 있습니다.

    **수정:**

    ```sql
    INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01');
    ```

---

### 문제 21

다음 쿼리의 오류를 찾고 수정하세요. 취소된 주문을 제외한 월별 매출을 구합니다.

```sql
SELECT
    SUBSTR(ordered_at, 1, 7) AS month,
    SUM(total_amount) AS revenue,
    COUNT(*) AS order_count
FROM orders
WHERE status != 'cancelled'
GROUP BY SUBSTR(ordered_at, 1, 7)
ORDER BY month;
```

??? tip "힌트"
    `!= 'cancelled'`로 취소만 제외했지만, 반품(`returned`, `return_requested`)도 매출에서 빠져야 하지 않을까요?

??? success "정답"
    **오류:** `cancelled`만 제외하면 `returned`와 `return_requested` 상태의 주문도 매출에 포함됩니다. 실제 매출로 인정되지 않는 상태를 모두 제외해야 합니다.

    **수정:**

    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        SUM(total_amount) AS revenue,
        COUNT(*) AS order_count
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```

---

### 문제 22

다음 쿼리의 오류를 찾고 수정하세요. 결제 수단별 매출을 구하는데, 합계가 주문 합계와 다릅니다.

```sql
SELECT
    p.method,
    COUNT(*) AS payment_count,
    SUM(p.amount) AS total_amount
FROM payments AS p
GROUP BY p.method
ORDER BY total_amount DESC;
```

??? tip "힌트"
    결제 상태(`status`)를 확인하세요. 실패하거나 환불된 결제도 포함하고 있지 않나요?

??? success "정답"
    **오류:** 결제 상태가 `failed`나 `refunded`인 건까지 포함되어 실제 매출과 차이가 납니다.

    **수정:**

    ```sql
    SELECT
        p.method,
        COUNT(*) AS payment_count,
        SUM(p.amount) AS total_amount
    FROM payments AS p
    WHERE p.status = 'completed'
    GROUP BY p.method
    ORDER BY total_amount DESC;
    ```

---

### 문제 23

다음 쿼리의 오류를 찾고 수정하세요. VIP 고객 중 최근 6개월간 주문이 없는 휴면 고객을 찾습니다.

```sql
SELECT c.name, c.email, c.grade
FROM customers AS c
WHERE c.grade = 'VIP'
  AND c.id NOT IN (
      SELECT customer_id
      FROM orders
      WHERE ordered_at >= DATE('now', '-6 months')
  );
```

??? tip "힌트"
    `NOT IN` 서브쿼리의 결과에 NULL이 포함되면 전체 결과가 빈 집합이 됩니다. `customer_id`가 NULL인 행이 있는지 확인하세요.

??? success "정답"
    **오류:** `NOT IN` 서브쿼리에서 `customer_id`가 NULL인 주문이 하나라도 있으면 결과가 0행이 됩니다. `NOT IN (1, 2, NULL)`은 항상 UNKNOWN이 되기 때문입니다.

    **수정:**

    ```sql
    -- 방법 1: NOT EXISTS 사용 (NULL 안전)
    SELECT c.name, c.email, c.grade
    FROM customers AS c
    WHERE c.grade = 'VIP'
      AND NOT EXISTS (
          SELECT 1 FROM orders AS o
          WHERE o.customer_id = c.id
            AND o.ordered_at >= DATE('now', '-6 months')
      );

    -- 방법 2: NOT IN에서 NULL 제외
    SELECT c.name, c.email, c.grade
    FROM customers AS c
    WHERE c.grade = 'VIP'
      AND c.id NOT IN (
          SELECT customer_id
          FROM orders
          WHERE ordered_at >= DATE('now', '-6 months')
            AND customer_id IS NOT NULL
      );
    ```

---

### 문제 24

다음 쿼리의 오류를 찾고 수정하세요. 공급업체별 반품률을 계산합니다. 일부 공급업체에서 에러가 납니다.

```sql
SELECT
    s.company_name,
    COUNT(DISTINCT oi.id) AS total_sales,
    COUNT(DISTINCT ret.id) AS return_count,
    ROUND(100.0 * COUNT(DISTINCT ret.id) / COUNT(DISTINCT oi.id), 2) AS return_rate
FROM suppliers AS s
LEFT JOIN products AS p ON s.id = p.supplier_id
LEFT JOIN order_items AS oi ON p.id = oi.product_id
LEFT JOIN returns AS ret ON ret.order_id = oi.order_id
GROUP BY s.id, s.company_name
ORDER BY return_rate DESC;
```

??? tip "힌트"
    판매 실적이 0인 공급업체에서 `COUNT(DISTINCT oi.id)`가 0이 됩니다. 0으로 나누면 에러가 발생합니다.

??? success "정답"
    **오류:** `total_sales`가 0인 공급업체에서 0으로 나누기 에러가 발생합니다. `NULLIF`로 분모가 0이면 NULL로 바꿔야 합니다.

    **수정:**

    ```sql
    SELECT
        s.company_name,
        COUNT(DISTINCT oi.id) AS total_sales,
        COUNT(DISTINCT ret.id) AS return_count,
        ROUND(100.0 * COUNT(DISTINCT ret.id)
            / NULLIF(COUNT(DISTINCT oi.id), 0), 2) AS return_rate
    FROM suppliers AS s
    LEFT JOIN products AS p ON s.id = p.supplier_id
    LEFT JOIN order_items AS oi ON p.id = oi.product_id
    LEFT JOIN returns AS ret ON ret.order_id = oi.order_id
    GROUP BY s.id, s.company_name
    ORDER BY return_rate DESC;
    ```

---

### 문제 25

다음 쿼리의 오류를 찾고 수정하세요. 고객 등급별 평균 주문 금액, 주문 수, 리뷰 평점을 하나의 보고서로 만듭니다. 주문 금액이 비정상적으로 큽니다.

```sql
SELECT
    c.grade,
    COUNT(o.id) AS order_count,
    ROUND(AVG(o.total_amount), 0) AS avg_order_amount,
    ROUND(AVG(r.rating), 2) AS avg_rating,
    COUNT(r.id) AS review_count
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
INNER JOIN order_items AS oi ON o.id = oi.order_id
LEFT JOIN reviews AS r ON c.id = r.customer_id
GROUP BY c.grade
ORDER BY avg_order_amount DESC;
```

??? tip "힌트"
    `orders` → `order_items`를 JOIN하면 주문 하나가 아이템 수만큼 복제됩니다. 거기에 `reviews`까지 JOIN하면 행이 폭발합니다. `COUNT(o.id)`가 실제 주문 수보다 훨씬 커집니다.

??? success "정답"
    **오류:** 세 가지 문제가 있습니다. (1) `order_items` JOIN으로 주문 행이 아이템 수만큼 복제 (2) `reviews` JOIN으로 추가 카디널리티 폭발 (3) `COUNT(o.id)`가 주문 수가 아닌 복제된 행 수를 셉니다. 각 집계를 서브쿼리로 분리해야 합니다.

    **수정:**

    ```sql
    SELECT
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(o.total_amount) * 1.0 / NULLIF(COUNT(DISTINCT o.id), 0), 0) AS avg_order_amount,
        sub_r.avg_rating,
        sub_r.review_count
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    LEFT JOIN (
        SELECT customer_id,
               ROUND(AVG(rating), 2) AS avg_rating,
               COUNT(*) AS review_count
        FROM reviews
        GROUP BY customer_id
    ) AS sub_r ON c.id = sub_r.customer_id
    GROUP BY c.grade, sub_r.avg_rating, sub_r.review_count
    ORDER BY avg_order_amount DESC;
    ```

    또는 등급별 완전 분리:

    ```sql
    SELECT
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(AVG(DISTINCT o.total_amount), 0) AS avg_order_amount,
        (SELECT ROUND(AVG(r.rating), 2)
         FROM reviews AS r
         INNER JOIN customers AS c2 ON r.customer_id = c2.id
         WHERE c2.grade = c.grade) AS avg_rating
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.grade
    ORDER BY avg_order_amount DESC;
    ```
