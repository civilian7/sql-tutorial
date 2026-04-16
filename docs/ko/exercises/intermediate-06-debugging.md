# SQL 디버깅

!!! info "사용 테이블"

    `categories` — 카테고리 (부모-자식 계층)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `reviews` — 리뷰 (평점, 내용)  

    `returns` — 반품/교환 (사유, 상태)  

    `suppliers` — 공급업체 (업체명, 연락처)  



!!! abstract "학습 범위"

    `cardinality explosion`, `NULL comparison`, `LEFT JOIN pitfall`, `GROUP BY`, `HAVING vs WHERE`, `DISTINCT`, `correlated subquery`, `date range`, `NULLIF`, `UNION`



### 1. 아래 쿼리는 2024년 상품별 매출을 구합니다. 그런데 실제보다 매출이 훨씬 크게 나옵니다. 왜일까요?


아래 쿼리는 2024년 상품별 매출을 구합니다. 그런데 실제보다 매출이 훨씬 크게 나옵니다. 왜일까요?

```sql
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


**힌트 1:** 두 개의 1:N 관계를 동시에 JOIN하면 행이 곱해지는 상황(카디널리티 폭발)을 의심해보세요.


??? success "정답"
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


    **실행 결과** (총 217행 중 상위 7행)

    | name | revenue | avg_rating |
    |---|---|---|
    | Razer Blade 18 블랙 | 104,562,500.00 | 3.92 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 94,176,000.00 | 4.12 |
    | 삼성 DDR4 32GB PC4-25600 | 3,088,500.00 | 3.94 |
    | Dell U2724D | 10,729,200.00 | 4.19 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 9,018,000.00 | 3.61 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 21,836,700.00 | 4.08 |
    | 삼성 DDR5 32GB PC5-38400 | 13,767,000.00 | 3.97 |


---


### 2. 아래 쿼리는 생년월일이 없는 고객을 찾으려 합니다. 결과가 0행입니다. 왜?


아래 쿼리는 생년월일이 없는 고객을 찾으려 합니다. 결과가 0행입니다. 왜?

```sql
SELECT name, email
FROM customers
WHERE birth_date = NULL;
```


**힌트 1:** SQL에서 NULL과 `=` 비교는 항상 FALSE입니다. NULL 전용 비교 연산자를 사용하세요.


??? success "정답"
    ```sql
    -- 수정: IS NULL 사용
    SELECT name, email
    FROM customers
    WHERE birth_date IS NULL;
    ```


    **실행 결과** (총 738행 중 상위 7행)

    | name | email |
    |---|---|
    | 김명자 | user7@testmail.kr |
    | 김정식 | user13@testmail.kr |
    | 윤순옥 | user14@testmail.kr |
    | 이서연 | user21@testmail.kr |
    | 강민석 | user24@testmail.kr |
    | 김서준 | user27@testmail.kr |
    | 윤지훈 | user36@testmail.kr |


---


### 3. 리뷰가 없는 상품도 포함하려고 LEFT JOIN을 썼는데, 리뷰 없는 상품이 결과에 없습니다.


리뷰가 없는 상품도 포함하려고 LEFT JOIN을 썼는데, 리뷰 없는 상품이 결과에 없습니다.

```sql
SELECT p.name, p.price, r.rating
FROM products AS p
LEFT JOIN reviews AS r ON p.id = r.product_id
WHERE r.rating >= 3;
```


**힌트 1:** `WHERE` 절에서 RIGHT 테이블의 칼럼을 필터링하면 NULL 행이 제거되어 LEFT JOIN이 INNER JOIN처럼 됩니다. 조건을 `ON` 절로 옮겨보세요.


??? success "정답"
    ```sql
    -- 수정: 조건을 ON 절로 이동
    SELECT p.name, p.price, r.rating
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id AND r.rating >= 3;
    ```


    **실행 결과** (총 7,277행 중 상위 7행)

    | name | price | rating |
    |---|---|---|
    | Razer Blade 18 블랙 | 2,987,500.00 | 3 |
    | Razer Blade 18 블랙 | 2,987,500.00 | 3 |
    | Razer Blade 18 블랙 | 2,987,500.00 | 3 |
    | Razer Blade 18 블랙 | 2,987,500.00 | 4 |
    | Razer Blade 18 블랙 | 2,987,500.00 | 4 |
    | Razer Blade 18 블랙 | 2,987,500.00 | 4 |
    | Razer Blade 18 블랙 | 2,987,500.00 | 4 |


---


### 4. 아래 쿼리는 카테고리별 상품 수를 구하려 합니다. 에러가 납니다.


아래 쿼리는 카테고리별 상품 수를 구하려 합니다. 에러가 납니다.

```sql
SELECT cat.name, COUNT(*) AS product_count
FROM products AS p
INNER JOIN categories AS cat ON p.category_id = cat.id;
```


**힌트 1:** 집계 함수(`COUNT`)를 쓰면서 비집계 칼럼(`cat.name`)이 있으면 반드시 필요한 절이 있습니다.


??? success "정답"
    ```sql
    -- 수정: GROUP BY 추가
    SELECT cat.name, COUNT(*) AS product_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    GROUP BY cat.name;
    ```


    **실행 결과** (총 38행 중 상위 7행)

    | name | product_count |
    |---|---|
    | 2in1 | 9 |
    | AMD | 10 |
    | AMD 소켓 | 10 |
    | DDR4 | 7 |
    | DDR5 | 8 |
    | HDD | 3 |
    | Intel | 5 |


---


### 5. 가격이 10만원 이상인 상품이 5개 이상인 카테고리만 보려 합니다. 에러가 납니다.


가격이 10만원 이상인 상품이 5개 이상인 카테고리만 보려 합니다. 에러가 납니다.

```sql
SELECT cat.name, COUNT(*) AS expensive_count
FROM products AS p
INNER JOIN categories AS cat ON p.category_id = cat.id
HAVING p.price >= 100000 AND COUNT(*) >= 5
GROUP BY cat.name;
```


**힌트 1:** 개별 행 필터(`p.price >= 100000`)는 `WHERE`, 그룹 필터(`COUNT(*) >= 5`)는 `HAVING`. 그리고 절의 순서도 확인하세요.


??? success "정답"
    ```sql
    -- 수정
    SELECT cat.name, COUNT(*) AS expensive_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE p.price >= 100000
    GROUP BY cat.name
    HAVING COUNT(*) >= 5;
    ```


    **실행 결과** (총 27행 중 상위 7행)

    | name | expensive_count |
    |---|---|
    | 2in1 | 9 |
    | AMD | 10 |
    | AMD 소켓 | 10 |
    | DDR5 | 8 |
    | Intel | 5 |
    | Intel 소켓 | 13 |
    | NVIDIA | 7 |


---


### 6. 고객별 구매 카테고리 수를 구합니다. 수가 비정상적으로 큽니다.


고객별 구매 카테고리 수를 구합니다. 수가 비정상적으로 큽니다.

```sql
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


**힌트 1:** 같은 카테고리의 상품을 여러 번 사면 중복 카운트됩니다. `COUNT`에 중복 제거 키워드를 추가하세요.


??? success "정답"
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


    **실행 결과** (총 10행 중 상위 7행)

    | name | category_count |
    |---|---|
    | 강명자 | 38 |
    | 김성민 | 38 |
    | 정유진 | 38 |
    | 이경숙 | 38 |
    | 최선영 | 38 |
    | 이윤서 | 38 |
    | 박은서 | 38 |


---


### 7. 평균보다 비싼 카테고리의 상품을 찾으려 합니다. 에러가 납니다.


평균보다 비싼 카테고리의 상품을 찾으려 합니다. 에러가 납니다.

```sql
SELECT name, price
FROM products
WHERE price > (
    SELECT AVG(price) FROM products GROUP BY category_id
);
```


**힌트 1:** `>` 연산자는 단일 값만 비교할 수 있는데, 서브쿼리가 여러 행을 반환합니다. `GROUP BY`를 제거하거나 상관 서브쿼리로 바꿔보세요.


??? success "정답"
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


### 8. 2024년 12월 주문을 구하려 합니다. 12월 31일 주문이 빠집니다.


2024년 12월 주문을 구하려 합니다. 12월 31일 주문이 빠집니다.

```sql
SELECT COUNT(*) AS december_orders
FROM orders
WHERE ordered_at BETWEEN '2024-12-01' AND '2024-12-31';
```


**힌트 1:** `ordered_at`에 시간 정보가 포함되어 있으면 `'2024-12-31'`은 `'2024-12-31 00:00:00'`으로 비교됩니다. 시간 끝까지 포함시키세요.


??? success "정답"
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


### 9. 월별 매출 보고서인데 취소 주문이 매출에 포함되어 있습니다.


월별 매출 보고서인데 취소 주문이 매출에 포함되어 있습니다.

```sql
SELECT
    SUBSTR(ordered_at, 1, 7) AS month,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY SUBSTR(ordered_at, 1, 7)
ORDER BY month;
```


**힌트 1:** `WHERE` 절에서 취소/반품 상태의 주문을 제외하는 조건이 빠져 있습니다.


??? success "정답"
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


    **실행 결과** (총 120행 중 상위 7행)

    | month | revenue |
    |---|---|
    | 2016-01 | 14,194,769.00 |
    | 2016-02 | 12,984,335.00 |
    | 2016-03 | 14,154,562.00 |
    | 2016-04 | 16,878,372.00 |
    | 2016-05 | 28,570,768.00 |
    | 2016-06 | 23,793,991.00 |
    | 2016-07 | 29,696,984.00 |


---


### 10. 반품률을 계산합니다. 판매가 0인 공급업체에서 에러가 납니다.


반품률을 계산합니다. 판매가 0인 공급업체에서 에러가 납니다.

```sql
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


**힌트 1:** 분모가 0이 될 수 있는 나눗셈입니다. `NULLIF(값, 0)`으로 0을 NULL로 바꾸면 에러 대신 NULL이 됩니다.


??? success "정답"
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


    **실행 결과** (총 60행 중 상위 7행)

    | company_name | return_count | sale_count | return_rate |
    |---|---|---|---|
    | 삼성전자 공식 유통 | 210 | 7542 | 2.78 |
    | LG전자 공식 유통 | 60 | 1661 | 3.61 |
    | 인텔코리아 | 83 | 2582 | 3.21 |
    | AMD코리아 | 48 | 1653 | 2.90 |
    | 엔비디아코리아 | 0 | 0 | NULL |
    | 한성컴퓨터 | 19 | 266 | 7.14 |
    | 주연테크 | 10 | 208 | 4.81 |


---


### 11. 가격대별 상품 수를 구한 후 필터링하려 합니다. 에러가 납니다.


가격대별 상품 수를 구한 후 필터링하려 합니다. 에러가 납니다.

```sql
SELECT
    CASE WHEN price < 100000 THEN '저가' ELSE '고가' END AS tier,
    COUNT(*) AS cnt
FROM products
WHERE tier = '저가'
GROUP BY tier;
```


**힌트 1:** SQL 실행 순서는 FROM -> WHERE -> GROUP BY -> SELECT. `WHERE`에서는 `SELECT`의 별칭을 참조할 수 없습니다.


??? success "정답"
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


### 12. 주문 이벤트와 문의 이벤트를 합치려 합니다. 에러가 납니다.


주문 이벤트와 문의 이벤트를 합치려 합니다. 에러가 납니다.

```sql
SELECT order_number, total_amount, ordered_at FROM orders
UNION ALL
SELECT title, category, created_at FROM complaints;
```


**힌트 1:** `UNION`의 각 SELECT는 칼럼 수와 타입이 호환되어야 합니다. 의미가 다른 칼럼을 통일된 구조로 맞춰보세요.


??? success "정답"
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


    **실행 결과** (총 20행 중 상위 7행)

    | type | reference | event_date |
    |---|---|---|
    | 문의 | 전원이 켜지지 않아요 | 2026-01-13 20:27:26 |
    | 문의 | 제품 사용법 문의 | 2026-01-11 05:32:28 |
    | 문의 | 부분 환불 요청 | 2026-01-10 08:43:56 |
    | 문의 | 화면에 불량 화소가 있습니다 | 2026-01-08 10:26:57 |
    | 문의 | 제품 사용법 문의 | 2026-01-08 08:28:26 |
    | 문의 | 제품 사용법 문의 | 2026-01-05 13:56:10 |
    | 문의 | 사이즈 교환 가능한가요? | 2026-01-04 21:17:27 |


---
