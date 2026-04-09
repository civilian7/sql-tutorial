# 빈칸 채우기

쿼리의 핵심 부분이 ___로 비어 있습니다. 올바른 SQL을 채워 넣으세요.

---


### 1. VIP 등급 고객만 조회합니다.


VIP 등급 고객만 조회합니다.

```sql
SELECT name, email, grade
FROM customers
WHERE ___
ORDER BY name;
```


**힌트 1:** 빈칸에는 grade 칼럼과 'VIP' 값을 비교하는 등호 조건이 들어갑니다


??? success "정답"
    ```sql
    SELECT name, email, grade
    FROM customers
    WHERE grade = 'VIP'
    ORDER BY name;
    ```


---


### 2. 상품을 가격이 높은 순으로 정렬합니다.


상품을 가격이 높은 순으로 정렬합니다.

```sql
SELECT name, price
FROM products
ORDER BY ___
LIMIT 10;
```


**힌트 1:** 빈칸에는 정렬 기준 칼럼과 내림차순 키워드(DESC)가 들어갑니다


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 10;
    ```


---


### 3. 카테고리별 상품 수를 구합니다.


카테고리별 상품 수를 구합니다.

```sql
SELECT category_id, ___ AS product_count
FROM products
GROUP BY category_id;
```


**힌트 1:** 빈칸에는 행의 수를 세는 집계 함수가 들어갑니다


??? success "정답"
    ```sql
    SELECT category_id, COUNT(*) AS product_count
    FROM products
    GROUP BY category_id;
    ```


---


### 4. 주문이 10건 이상인 고객만 필터링합니다.


주문이 10건 이상인 고객만 필터링합니다.

```sql
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
___ ;
```


**힌트 1:** 빈칸에는 그룹화된 결과를 필터링하는 HAVING 절이 들어갑니다. WHERE는 그룹화 전, HAVING은 그룹화 후 필터링


??? success "정답"
    ```sql
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    HAVING COUNT(*) >= 10;
    ```


---


### 5. 상품과 카테고리를 연결합니다.


상품과 카테고리를 연결합니다.

```sql
SELECT p.name, cat.name AS category
FROM products AS p
INNER JOIN categories AS cat ON ___
LIMIT 10;
```


**힌트 1:** 빈칸에는 두 테이블의 연결 조건이 들어갑니다. products의 외래키와 categories의 기본키를 매칭


??? success "정답"
    ```sql
    SELECT p.name, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LIMIT 10;
    ```


---


### 6. 주문이 없는 고객을 찾습니다.


주문이 없는 고객을 찾습니다.

```sql
SELECT c.name, c.email
FROM customers AS c
LEFT JOIN orders AS o ON c.id = o.customer_id
WHERE ___ ;
```


**힌트 1:** LEFT JOIN 후 매칭되지 않은 행은 오른쪽 테이블 칼럼이 NULL. IS NULL로 확인


??? success "정답"
    ```sql
    SELECT c.name, c.email
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL;
    ```


---


### 7. 2024년 1분기(1~3월) 주문을 조회합니다.


2024년 1분기(1~3월) 주문을 조회합니다.

```sql
SELECT order_number, total_amount, ordered_at
FROM orders
WHERE ordered_at ___ ;
```


**힌트 1:** 빈칸에는 BETWEEN '시작일' AND '종료일'로 날짜 범위를 지정하세요


??? success "정답"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE ordered_at BETWEEN '2024-01-01' AND '2024-03-31 23:59:59';
    ```


---


### 8. 재고 상태를 분류합니다.


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


**힌트 1:** WHEN stock_qty = 0 THEN '품절' 식으로 구간별 조건을 나열하세요. 마지막은 ELSE


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


### 9. 생년월일이 없으면 '미입력'으로 표시합니다.


생년월일이 없으면 '미입력'으로 표시합니다.

```sql
SELECT
    name,
    ___ AS birth_date
FROM customers
LIMIT 10;
```


**힌트 1:** COALESCE(칼럼, 기본값) 함수는 NULL일 때 대체값을 반환합니다


??? success "정답"
    ```sql
    SELECT
        name,
        COALESCE(birth_date, '미입력') AS birth_date
    FROM customers
    LIMIT 10;
    ```


---


### 10. 평균 가격보다 비싼 상품을 조회합니다.


평균 가격보다 비싼 상품을 조회합니다.

```sql
SELECT name, price
FROM products
WHERE price > ___
ORDER BY price DESC;
```


**힌트 1:** 빈칸에는 평균 가격을 구하는 서브쿼리 (SELECT AVG(price) FROM products)가 들어갑니다


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC;
    ```


---


### 11. 등급별 고객 수, 평균 적립금, 최대 적립금을 구합니다.


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


**힌트 1:** 세 빈칸에는 각각 COUNT(*), ROUND(AVG(...), 0), MAX(...) 집계 함수가 들어갑니다


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


### 12. 이메일이 testmail.kr 도메인인 고객을 찾습니다.


이메일이 testmail.kr 도메인인 고객을 찾습니다.

```sql
SELECT name, email
FROM customers
WHERE email LIKE ___
LIMIT 10;
```


**힌트 1:** LIKE 패턴에서 %는 임의 문자열. @testmail.kr로 끝나는 패턴을 만드세요


??? success "정답"
    ```sql
    SELECT name, email
    FROM customers
    WHERE email LIKE '%@testmail.kr'
    LIMIT 10;
    ```


---


### 13. 주문의 연도와 월을 추출합니다.


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


**힌트 1:** SUBSTR(ordered_at, 시작위치, 길이)로 문자열을 잘라냅니다. 연도는 1~4자리, 월은 6~2자리


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


### 14. 결제 상태가 completed 또는 refunded인 건만 조회합니다.


결제 상태가 completed 또는 refunded인 건만 조회합니다.

```sql
SELECT id, order_id, method, amount, status
FROM payments
WHERE status ___ ;
```


**힌트 1:** 여러 값 중 하나와 일치하는지 확인할 때 IN ('값1', '값2') 연산자를 사용하세요


??? success "정답"
    ```sql
    SELECT id, order_id, method, amount, status
    FROM payments
    WHERE status IN ('completed', 'refunded');
    ```


---


### 15. 주문번호, 고객명, 결제 금액, 배송 상태를 한 번에 조회합니다.


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


**힌트 1:** 각 빈칸에는 외래키 관계가 들어갑니다. o.customer_id = c.id, o.id = p.order_id, o.id = sh.order_id 패턴


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


---
