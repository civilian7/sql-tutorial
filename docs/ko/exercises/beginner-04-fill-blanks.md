# 빈칸 채우기

!!! info "사용 테이블"

    `categories` — 카테고리 (부모-자식 계층)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `payments` — 결제 (방법, 금액, 상태)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `shipping` — 배송 (택배사, 추적번호, 상태)  



!!! abstract "학습 범위"

    `WHERE`, `ORDER BY`, `COUNT`, `HAVING`, `JOIN`, `LEFT JOIN`, `IS NULL`, `BETWEEN`, `CASE WHEN`, `COALESCE`, `subquery`, `GROUP BY`, `LIKE`, `SUBSTR`, `IN`



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


    **실행 결과** (총 368행 중 상위 7행)

    | name | email | grade |
    |---|---|---|
    | 강경숙 | user3645@testmail.kr | VIP |
    | 강명자 | user162@testmail.kr | VIP |
    | 강민석 | user824@testmail.kr | VIP |
    | 강민재 | user1516@testmail.kr | VIP |
    | 강상철 | user1613@testmail.kr | VIP |
    | 강순옥 | user3678@testmail.kr | VIP |
    | 강옥순 | user2454@testmail.kr | VIP |


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


    **실행 결과** (총 10행 중 상위 7행)

    | name | price |
    |---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 |
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 |
    | Razer Blade 18 블랙 | 4,353,100.00 |
    | Razer Blade 16 실버 | 3,702,900.00 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 |


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


    **실행 결과** (총 40행 중 상위 7행)

    | category_id | product_count |
    |---|---|
    | 2 | 5 |
    | 3 | 11 |
    | 4 | 2 |
    | 6 | 10 |
    | 7 | 9 |
    | 8 | 9 |
    | 9 | 1 |


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


    **실행 결과** (총 953행 중 상위 7행)

    | customer_id | order_count |
    |---|---|
    | 2 | 77 |
    | 3 | 161 |
    | 4 | 95 |
    | 5 | 114 |
    | 8 | 38 |
    | 10 | 29 |
    | 12 | 41 |


---


### 5. 상품과 카테고리를 연결합니다.


상품과 카테고리를 연결합니다.

```sql
SELECT p.name, cat.name AS category
FROM products AS p
INNER JOIN categories AS cat ON ___
LIMIT 10;
```


**힌트 1:** 빈칸에는 두 테이블의 연결 조건이 들어갑니다. products의 외래 키와 categories의 기본 키를 매칭


??? success "정답"
    ```sql
    SELECT p.name, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | category |
    |---|---|
    | Razer Blade 18 블랙 | 게이밍 노트북 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | NVIDIA |
    | 삼성 DDR4 32GB PC4-25600 | DDR4 |
    | Dell U2724D | 일반 모니터 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | DDR5 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | AMD |
    | 삼성 DDR5 32GB PC5-38400 | DDR5 |


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


    **실행 결과** (총 2,391행 중 상위 7행)

    | name | email |
    |---|---|
    | 정준호 | user1@testmail.kr |
    | 김준혁 | user6@testmail.kr |
    | 김명자 | user7@testmail.kr |
    | 주경희 | user9@testmail.kr |
    | 김상호 | user11@testmail.kr |
    | 김정식 | user13@testmail.kr |
    | 임순자 | user17@testmail.kr |


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


    **실행 결과** (총 1,412행 중 상위 7행)

    | order_number | total_amount | ordered_at |
    |---|---|---|
    | ORD-20240101-25455 | 42,600.00 | 2024-01-01 02:48:53 |
    | ORD-20240101-25453 | 160,400.00 | 2024-01-01 03:38:36 |
    | ORD-20240101-25457 | 616,200.00 | 2024-01-01 06:57:33 |
    | ORD-20240101-25466 | 243,600.00 | 2024-01-01 07:55:46 |
    | ORD-20240101-25465 | 189,100.00 | 2024-01-01 09:35:17 |
    | ORD-20240101-25454 | 117,700.00 | 2024-01-01 10:48:07 |
    | ORD-20240101-25463 | 325,800.00 | 2024-01-01 12:01:21 |


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


    **실행 결과** (총 280행 중 상위 7행)

    | name | stock_qty | stock_status |
    |---|---|---|
    | Razer Blade 18 블랙 | 107 | 충분 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 499 | 충분 |
    | 삼성 DDR4 32GB PC4-25600 | 359 | 충분 |
    | Dell U2724D | 337 | 충분 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 59 | 보통 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 460 | 충분 |
    | 삼성 DDR5 32GB PC5-38400 | 340 | 충분 |


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


    **실행 결과** (총 10행 중 상위 7행)

    | name | birth_date |
    |---|---|
    | 정준호 | 1995-02-06 |
    | 김경수 | 1995-06-12 |
    | 김민재 | 1998-05-02 |
    | 진정자 | 1994-12-02 |
    | 이정수 | 1989-12-22 |
    | 김준혁 | 1991-05-12 |
    | 김명자 | 미입력 |


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


    **실행 결과** (총 83행 중 상위 7행)

    | name | price |
    |---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 |
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 |
    | Razer Blade 18 블랙 | 4,353,100.00 |
    | Razer Blade 16 실버 | 3,702,900.00 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 |


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


    **실행 결과** (4행)

    | grade | customer_count | avg_points | max_points |
    |---|---|---|---|
    | BRONZE | 3859 | 16,779.00 | 956,983 |
    | GOLD | 524 | 147,711.00 | 2,007,717 |
    | SILVER | 479 | 95,042.00 | 1,266,757 |
    | VIP | 368 | 407,015.00 | 3,955,828 |


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


    **실행 결과** (총 10행 중 상위 7행)

    | name | email |
    |---|---|
    | 정준호 | user1@testmail.kr |
    | 김경수 | user2@testmail.kr |
    | 김민재 | user3@testmail.kr |
    | 진정자 | user4@testmail.kr |
    | 이정수 | user5@testmail.kr |
    | 김준혁 | user6@testmail.kr |
    | 김명자 | user7@testmail.kr |


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


    **실행 결과** (총 120행 중 상위 7행)

    | year | month | order_count |
    |---|---|---|
    | 2016 | 01 | 38 |
    | 2016 | 02 | 27 |
    | 2016 | 03 | 34 |
    | 2016 | 04 | 30 |
    | 2016 | 05 | 39 |
    | 2016 | 06 | 34 |
    | 2016 | 07 | 30 |


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


    **실행 결과** (총 36,546행 중 상위 7행)

    | id | order_id | method | amount | status |
    |---|---|---|---|---|
    | 1 | 1 | card | 167,000.00 | completed |
    | 2 | 2 | card | 211,800.00 | completed |
    | 3 | 3 | card | 704,800.00 | completed |
    | 4 | 4 | card | 167,000.00 | completed |
    | 5 | 5 | kakao_pay | 534,490.00 | completed |
    | 6 | 6 | card | 167,000.00 | completed |
    | 7 | 7 | card | 687,400.00 | completed |


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


**힌트 1:** 각 빈칸에는 외래 키 관계가 들어갑니다. o.customer_id = c.id, o.id = p.order_id, o.id = sh.order_id 패턴


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


    **실행 결과** (5행)

    | order_number | customer | paid | shipping_status |
    |---|---|---|---|
    | ORD-20251231-37555 | 송지영 | 74,800.00 | NULL |
    | ORD-20251231-37543 | 박민서 | 134,100.00 | NULL |
    | ORD-20251231-37552 | 강미경 | 254,300.00 | NULL |
    | ORD-20251231-37548 | 윤영희 | 187,700.00 | NULL |
    | ORD-20251231-37542 | 문도현 | 155,700.00 | NULL |


---
