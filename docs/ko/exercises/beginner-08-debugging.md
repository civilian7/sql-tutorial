# SQL 오류 찾기 -- 초급

!!! info "사용 테이블"

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `reviews` — 리뷰 (평점, 내용)  

    `payments` — 결제 (방법, 금액, 상태)  



!!! abstract "학습 범위"

    `Syntax errors`, `Logic errors`, `NULL comparison`, `WHERE vs HAVING`, `GROUP BY rules`, `CASE order`



### 1. 다음 쿼리의 오류를 찾고 수정하세요.


다음 쿼리의 오류를 찾고 수정하세요.


**힌트 1:** SELECT 절에서 칼럼을 나열할 때 필요한 구분 기호를 확인하세요.


??? success "정답"
    ```sql
    SELECT name, price, brand
    FROM products
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | price | brand |
    |---|---|---|
    | Razer Blade 18 블랙 | 2,987,500.00 | Razer |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | MSI |
    | 삼성 DDR4 32GB PC4-25600 | 43,500.00 | 삼성전자 |
    | Dell U2724D | 894,100.00 | Dell |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 167,000.00 | G.SKILL |


---


### 2. 다음 쿼리의 오류를 찾고 수정하세요.


다음 쿼리의 오류를 찾고 수정하세요.


**힌트 1:** SQL 표준에서 문자열 리터럴에 사용하는 따옴표 종류를 확인하세요. SQLite에서는 동작할 수 있지만 표준 SQL 관점에서 문제가 있습니다.


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE brand = 'ASUS';
    ```


    **실행 결과** (총 26행 중 상위 7행)

    | name | price |
    |---|---|
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 |
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 |
    | ASUS ROG Strix Scar 16 실버 | 1,598,100.00 |
    | ASUS ExpertBook B5 [특별 한정판 에디션] 저소음 설... | 2,041,000.00 |
    | ASUS PCE-BE92BT | 47,200.00 |
    | ASUS Dual RTX 4060 Ti 블랙 | 2,674,800.00 |
    | ASUS Dual RX 9070 실버 | 1,344,800.00 |


---


### 3. 다음 쿼리의 오류를 찾고 수정하세요.


다음 쿼리의 오류를 찾고 수정하세요.


**힌트 1:** SQL 키워드의 철자를 확인하세요.


??? success "정답"
    ```sql
    SELECT name, email
    FROM customers
    WHERE grade = 'VIP';
    ```


    **실행 결과** (총 368행 중 상위 7행)

    | name | email |
    |---|---|
    | 김민재 | user3@testmail.kr |
    | 김예원 | user16@testmail.kr |
    | 이영철 | user33@testmail.kr |
    | 한승민 | user96@testmail.kr |
    | 김병철 | user97@testmail.kr |
    | 이영자 | user98@testmail.kr |
    | 이영일 | user130@testmail.kr |


---


### 4. 다음 쿼리의 오류를 찾고 수정하세요.


다음 쿼리의 오류를 찾고 수정하세요.


**힌트 1:** 이 쿼리는 사실 문법적으로 올바릅니다. `ORDER BY price`의 기본 정렬 방향을 생각해보세요. 의도가 "비싼 순"이라면?


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE price BETWEEN 100000 AND 500000
    ORDER BY price DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | price |
    |---|---|
    | 캐논 imageCLASS MF655Cdw 화이트 | 490,800.00 |
    | MSI MAG Z890 TOMAHAWK WIFI 블랙 | 481,700.00 |
    | 소니 WH-CH720N 실버 | 445,700.00 |
    | 필립스 275E2FAE 실버 | 427,600.00 |
    | MSI MAG X870E TOMAHAWK WIFI 화이트 | 425,400.00 |
    | 삼성 ViewFinity S8 | 423,300.00 |
    | Windows 11 Pro 실버 | 423,000.00 |


---


### 5. 다음 쿼리의 오류를 찾고 수정하세요.


다음 쿼리의 오류를 찾고 수정하세요.


**힌트 1:** 정렬에 사용하는 키워드를 정확히 확인하세요.


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


### 6. 다음 쿼리의 오류를 찾고 수정하세요.


다음 쿼리의 오류를 찾고 수정하세요.


**힌트 1:** LIKE 패턴의 따옴표 위치를 확인하세요. `%`가 문자열 안에 있어야 합니다.


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%게이밍%';
    ```


---


### 7. 다음 쿼리의 오류를 찾고 수정하세요.


다음 쿼리의 오류를 찾고 수정하세요.


**힌트 1:** SQL 절의 순서를 확인하세요. WHERE는 어디에 위치해야 하나요?


??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE price > 100000
      AND stock_qty > 0
      AND is_active = 1
    ORDER BY price DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | price | stock_qty |
    |---|---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 | 346 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 | 434 |
    | Razer Blade 18 블랙 | 4,353,100.00 | 287 |
    | Razer Blade 16 실버 | 3,702,900.00 | 323 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 | 201 |
    | ASUS ROG Strix GT35 | 3,296,800.00 | 455 |
    | Razer Blade 18 블랙 | 2,987,500.00 | 107 |


---


### 8. 다음 쿼리의 오류를 찾고 수정하세요.


다음 쿼리의 오류를 찾고 수정하세요.


**힌트 1:** SELECT 절에서 칼럼 별칭을 지정할 때도 칼럼 사이에 필요한 것이 있습니다.


??? success "정답"
    ```sql
    SELECT name AS 상품명, price AS 가격
    FROM products
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | 상품명 | 가격 |
    |---|---|
    | Razer Blade 18 블랙 | 2,987,500.00 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 |
    | 삼성 DDR4 32GB PC4-25600 | 43,500.00 |
    | Dell U2724D | 894,100.00 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 167,000.00 |


---


### 9. 다음 쿼리의 오류를 찾고 수정하세요.


다음 쿼리의 오류를 찾고 수정하세요.


**힌트 1:** `IN` 목록 안의 값 구분 기호를 확인하세요.


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE brand IN ('ASUS', 'MSI', 'Dell');
    ```


    **실행 결과** (총 42행 중 상위 7행)

    | name | price |
    |---|---|
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 |
    | Dell U2724D | 894,100.00 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 383,100.00 |
    | MSI MAG X870E TOMAHAWK WIFI 화이트 | 425,400.00 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 |
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트 | 1,517,600.00 |


---


### 10. 다음 쿼리의 오류를 찾고 수정하세요.


다음 쿼리의 오류를 찾고 수정하세요.


**힌트 1:** SELECT 목록의 칼럼 사이를 확인하세요.


??? success "정답"
    ```sql
    SELECT COUNT(*) AS total,
           AVG(price) AS avg_price,
           SUM(price) AS total_price
    FROM products;
    ```


    **실행 결과** (1행)

    | total | avg_price | total_price |
    |---|---|---|
    | 280 | 649,272.50 | 181,796,300.00 |


---


### 11. 다음 쿼리는 생년월일이 없는 고객을 찾으려 합니다. 결과가 0행입니다. 왜일까요?


다음 쿼리는 생년월일이 없는 고객을 찾으려 합니다. 결과가 0행입니다. 왜일까요?


**힌트 1:** SQL에서 NULL은 "알 수 없는 값"입니다. `=` 연산자로 비교하면 항상 어떤 결과가 나올까요?


??? success "정답"
    ```sql
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


### 12. 다음 쿼리는 브랜드별 상품 수를 구하려 합니다. 에러가 납니다.


다음 쿼리는 브랜드별 상품 수를 구하려 합니다. 에러가 납니다.


**힌트 1:** 집계 함수와 비집계 칼럼을 함께 SELECT할 때 필요한 절이 있습니다.


??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand;
    ```


    **실행 결과** (총 55행 중 상위 7행)

    | brand | product_count |
    |---|---|
    | AMD | 2 |
    | APC | 1 |
    | ASRock | 11 |
    | ASUS | 26 |
    | Adobe | 1 |
    | Apple | 2 |
    | Arctic | 6 |


---


### 13. 다음 쿼리는 상품 수가 10개 이상인 브랜드만 조회하려 합니다. 에러가 납니다.


다음 쿼리는 상품 수가 10개 이상인 브랜드만 조회하려 합니다. 에러가 납니다.


**힌트 1:** `WHERE`절에서 집계 함수를 사용할 수 있을까요?


??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10;
    ```


    **실행 결과** (7행)

    | brand | product_count |
    |---|---|
    | ASRock | 11 |
    | ASUS | 26 |
    | LG전자 | 11 |
    | MSI | 13 |
    | TP-Link | 11 |
    | 로지텍 | 17 |
    | 삼성전자 | 25 |


---


### 14. 다음 쿼리는 'ASUS'가 아닌 상품을 찾으려 합니다. 그런데 brand가 NULL인 상품이 누락됩니다.


다음 쿼리는 'ASUS'가 아닌 상품을 찾으려 합니다. 그런데 brand가 NULL인 상품이 누락됩니다.


**힌트 1:** `NULL != 'ASUS'`의 결과는 TRUE일까요? NULL과의 비교는 항상 NULL(UNKNOWN)입니다.


??? success "정답"
    ```sql
    SELECT name, brand
    FROM products
    WHERE brand != 'ASUS' OR brand IS NULL;
    ```


    **실행 결과** (총 254행 중 상위 7행)

    | name | brand |
    |---|---|
    | Razer Blade 18 블랙 | Razer |
    | MSI GeForce RTX 4070 Ti Super GAMING X | MSI |
    | 삼성 DDR4 32GB PC4-25600 | 삼성전자 |
    | Dell U2724D | Dell |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | G.SKILL |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | MSI |
    | 삼성 DDR5 32GB PC5-38400 | 삼성전자 |


---


### 15. 다음 쿼리는 주문 금액 상위 10건을 구하려 합니다. ORDER BY의 위치가 잘못되었습니다.


다음 쿼리는 주문 금액 상위 10건을 구하려 합니다. ORDER BY의 위치가 잘못되었습니다.


**힌트 1:** SQL 절의 실행 순서를 생각해보세요. LIMIT과 ORDER BY 중 어느 것이 먼저 와야 할까요?


??? success "정답"
    ```sql
    SELECT order_number, total_amount
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | total_amount |
    |---|---|
    | ORD-20201121-08810 | 50,867,500.00 |
    | ORD-20250305-32265 | 46,820,024.00 |
    | ORD-20230523-22331 | 46,094,971.00 |
    | ORD-20200209-05404 | 43,677,500.00 |
    | ORD-20221231-20394 | 43,585,700.00 |
    | ORD-20251218-37240 | 38,626,400.00 |
    | ORD-20220106-15263 | 37,987,600.00 |


---


### 16. 다음 쿼리는 등급별 평균 적립금이 높은 순으로 조회합니다. ORDER BY에 별칭을 사용했는데 동작하지 않는


다음 쿼리는 등급별 평균 적립금이 높은 순으로 조회합니다. ORDER BY에 별칭을 사용했는데 동작하지 않는 경우가 있습니다.


**힌트 1:** 이 쿼리는 SQLite에서는 정상 동작합니다. 하지만 일부 DB에서는 `ORDER BY`에서 별칭 사용에 제한이 있습니다. 어떤 대안이 있을까요?


??? success "정답"
    ```sql
    SELECT grade,
           AVG(point_balance) AS avg_points
    FROM customers
    GROUP BY grade
    ORDER BY AVG(point_balance) DESC;
    ```


    **실행 결과** (4행)

    | grade | avg_points |
    |---|---|
    | VIP | 407,014.69 |
    | GOLD | 147,710.69 |
    | SILVER | 95,042.33 |
    | BRONZE | 16,779.46 |


---


### 17. 다음 쿼리는 성별이 NULL이 아닌 고객만 조회하려 합니다. 논리가 잘못되었습니다.


다음 쿼리는 성별이 NULL이 아닌 고객만 조회하려 합니다. 논리가 잘못되었습니다.


**힌트 1:** 문제 11과 같은 원리입니다. NULL과의 `!=` 비교도 결과가 NULL입니다.


??? success "정답"
    ```sql
    SELECT name, gender
    FROM customers
    WHERE gender IS NOT NULL;
    ```


    **실행 결과** (총 4,701행 중 상위 7행)

    | name | gender |
    |---|---|
    | 정준호 | M |
    | 김민재 | M |
    | 진정자 | F |
    | 이정수 | M |
    | 김준혁 | M |
    | 김명자 | F |
    | 성민석 | F |


---


### 18. 다음 쿼리는 주문 상태별 건수를 구하고, HAVING으로 필터링합니다. 하지만 의도와 다릅니다.


다음 쿼리는 주문 상태별 건수를 구하고, HAVING으로 필터링합니다. 하지만 의도와 다릅니다.


**힌트 1:** `HAVING`은 집계 결과를 필터링하는 용도입니다. 단순 칼럼 값 필터링에는 어떤 절을 써야 할까요?


??? success "정답"
    ```sql
    SELECT status, COUNT(*) AS order_count
    FROM orders
    WHERE status = 'confirmed'
    GROUP BY status;
    ```


    **실행 결과** (1행)

    | status | order_count |
    |---|---|
    | confirmed | 34,393 |


---


### 19. 다음 쿼리는 가격이 100만원 이상인 상품의 브랜드별 수를 구합니다. GROUP BY에 문제가 있습니다.


다음 쿼리는 가격이 100만원 이상인 상품의 브랜드별 수를 구합니다. GROUP BY에 문제가 있습니다.


**힌트 1:** SELECT에 있는 비집계 칼럼은 모두 GROUP BY에 포함되어야 합니다. `name`은 어떤가요?


??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS cnt
    FROM products
    WHERE price >= 1000000
    GROUP BY brand;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | brand | cnt |
    |---|---|
    | ASUS | 16 |
    | Apple | 1 |
    | BenQ | 1 |
    | Dell | 1 |
    | HP | 5 |
    | LG전자 | 9 |
    | MSI | 4 |


---


### 20. 다음 쿼리는 연도별 주문 수를 구합니다. 결과가 이상합니다.


다음 쿼리는 연도별 주문 수를 구합니다. 결과가 이상합니다.


**힌트 1:** `ordered_at`에는 날짜와 시간이 함께 저장되어 있습니다. 연도별로 그룹화하려면?


??? success "정답"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 4) AS year, COUNT(*) AS order_count
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | year | order_count |
    |---|---|
    | 2016 | 416 |
    | 2017 | 709 |
    | 2018 | 1319 |
    | 2019 | 2589 |
    | 2020 | 4319 |
    | 2021 | 5841 |
    | 2022 | 5203 |


---


### 21. 다음 쿼리는 상품의 마진율(%)을 구합니다. 일부 상품에서 마진율이 0%로 나옵니다.


다음 쿼리는 상품의 마진율(%)을 구합니다. 일부 상품에서 마진율이 0%로 나옵니다.


**힌트 1:** SQLite에서 정수끼리 나누면 결과가 어떻게 되나요?


??? success "정답"
    ```sql
    SELECT name, price, cost_price,
           ROUND((price - cost_price) * 100.0 / price, 1) AS margin_pct
    FROM products
    WHERE is_active = 1
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | price | cost_price | margin_pct |
    |---|---|---|---|
    | Razer Blade 18 블랙 | 2,987,500.00 | 3,086,700.00 | -3.30 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | 1,360,300.00 | 22.00 |
    | 삼성 DDR4 32GB PC4-25600 | 43,500.00 | 37,900.00 | 12.90 |
    | Dell U2724D | 894,100.00 | 565,700.00 | 36.70 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 167,000.00 | 121,400.00 | 27.30 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 383,100.00 | 431,800.00 | -12.70 |
    | 삼성 DDR5 32GB PC5-38400 | 211,800.00 | 151,900.00 | 28.30 |


---


### 22. 다음 쿼리는 CASE 표현식에서 ELSE가 빠져 있습니다. 어떤 문제가 발생할까요?


다음 쿼리는 CASE 표현식에서 ELSE가 빠져 있습니다. 어떤 문제가 발생할까요?


**힌트 1:** 가격이 100만원 이상인 상품은 어떤 값이 될까요?


??? success "정답"
    ```sql
    SELECT name, price,
           CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier
    FROM products;
    ```


    **실행 결과** (총 280행 중 상위 7행)

    | name | price | price_tier |
    |---|---|---|
    | Razer Blade 18 블랙 | 2,987,500.00 | 고가 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | 고가 |
    | 삼성 DDR4 32GB PC4-25600 | 43,500.00 | 저가 |
    | Dell U2724D | 894,100.00 | 중가 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 167,000.00 | 중저가 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 383,100.00 | 중저가 |
    | 삼성 DDR5 32GB PC5-38400 | 211,800.00 | 중저가 |


---


### 23. 다음 쿼리는 HAVING에서 별칭을 사용합니다. 에러가 발생할 수 있습니다.


다음 쿼리는 HAVING에서 별칭을 사용합니다. 에러가 발생할 수 있습니다.


**힌트 1:** SQLite에서는 HAVING에서 별칭을 사용할 수 있지만, MySQL, PostgreSQL 등에서는?


??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS cnt
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10;
    ```


    **실행 결과** (7행)

    | brand | cnt |
    |---|---|
    | ASRock | 11 |
    | ASUS | 26 |
    | LG전자 | 11 |
    | MSI | 13 |
    | TP-Link | 11 |
    | 로지텍 | 17 |
    | 삼성전자 | 25 |


---


### 24. 다음 쿼리는 주문에서 할인율을 계산합니다. 0으로 나누는 오류가 발생할 수 있습니다.


다음 쿼리는 주문에서 할인율을 계산합니다. 0으로 나누는 오류가 발생할 수 있습니다.


**힌트 1:** `total_amount`가 0인 주문이 있다면 어떻게 될까요?


??? success "정답"
    ```sql
    SELECT order_number,
           total_amount,
           discount_amount,
           CASE
               WHEN total_amount = 0 THEN 0
               ELSE ROUND(discount_amount * 100.0 / total_amount, 1)
           END AS discount_rate
    FROM orders
    ORDER BY discount_rate DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | total_amount | discount_amount | discount_rate |
    |---|---|---|---|
    | ORD-20240509-27481 | 155,218.00 | 28,100.00 | 18.10 |
    | ORD-20190915-04201 | 84,269.00 | 15,000.00 | 17.80 |
    | ORD-20221108-19511 | 375,878.00 | 66,400.00 | 17.70 |
    | ORD-20230429-21988 | 56,000.00 | 9,900.00 | 17.70 |
    | ORD-20240405-26944 | 737,599.00 | 130,300.00 | 17.70 |
    | ORD-20171114-00993 | 90,300.00 | 15,900.00 | 17.60 |
    | ORD-20200211-05431 | 205,300.00 | 36,100.00 | 17.60 |


---


### 25. 다음 쿼리는 2024년 주문의 월별 통계를 구합니다. 월 정렬이 이상합니다.


다음 쿼리는 2024년 주문의 월별 통계를 구합니다. 월 정렬이 이상합니다.


**힌트 1:** "월별 통계"라면 1월부터 12월까지 시간 순서로 보는 것이 자연스럽습니다. 현재 정렬 기준은?


??? success "정답"
    ```sql
    SELECT SUBSTR(ordered_at, 6, 2) AS month,
           COUNT(*) AS order_count
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | month | order_count |
    |---|---|
    | 01 | 346 |
    | 02 | 465 |
    | 03 | 601 |
    | 04 | 506 |
    | 05 | 415 |
    | 06 | 415 |
    | 07 | 414 |


---


### 26. 다음 쿼리는 고객 등급별 평균 적립금과 총 적립금을 구합니다. ROUND가 한 곳에만 적용되어 있습니다.


다음 쿼리는 고객 등급별 평균 적립금과 총 적립금을 구합니다. ROUND가 한 곳에만 적용되어 있습니다.


**힌트 1:** 같은 값(`AVG(point_balance)`)을 두 번 조회하면서 하나는 ROUND, 하나는 원본입니다. 이것 자체는 오류가 아니지만, `avg_points_raw`에 소수점 이하 긴 숫자가 표시됩니다.


??? success "정답"
    ```sql
    SELECT grade,
           ROUND(AVG(point_balance)) AS avg_points,
           SUM(point_balance) AS total_points,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade;
    ```


    **실행 결과** (4행)

    | grade | avg_points | total_points | customer_count |
    |---|---|---|---|
    | BRONZE | 16,779.00 | 64,751,937 | 3859 |
    | GOLD | 147,711.00 | 77,400,400 | 524 |
    | SILVER | 95,042.00 | 45,525,276 | 479 |
    | VIP | 407,015.00 | 149,781,406 | 368 |


---


### 27. 다음 쿼리는 상품명에 '블랙'이나 '화이트'가 포함된 상품을 찾습니다. 결과가 예상보다 많습니다.


다음 쿼리는 상품명에 '블랙'이나 '화이트'가 포함된 상품을 찾습니다. 결과가 예상보다 많습니다.


**힌트 1:** `AND`와 `OR`의 연산자 우선순위를 확인하세요. `OR`과 `AND` 중 어느 것이 먼저 평가되나요?


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE (name LIKE '%블랙%' OR name LIKE '%화이트%')
      AND price > 500000;
    ```


    **실행 결과** (총 42행 중 상위 7행)

    | name | price |
    |---|---|
    | Razer Blade 18 블랙 | 2,987,500.00 |
    | 넷기어 Nighthawk RS700S 블랙 | 629,300.00 |
    | Razer Blade 18 화이트 | 2,483,600.00 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 |
    | 한성 보스몬스터 DX5800 블랙 | 1,129,400.00 |
    | 삼성 오디세이 G7 32 화이트 | 537,800.00 |
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 |


---


### 28. 다음 쿼리는 NULL을 포함한 칼럼의 합계를 구합니다. 결과가 예상과 다릅니다.


다음 쿼리는 NULL을 포함한 칼럼의 합계를 구합니다. 결과가 예상과 다릅니다.


**힌트 1:** `discount_amount`이나 `shipping_fee`가 NULL인 행이 있다면, `SUM`은 NULL을 무시하지만 `discount_amount + shipping_fee`는?


??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_orders,
           SUM(COALESCE(discount_amount, 0)) + SUM(COALESCE(shipping_fee, 0)) AS extra_charges,
           AVG(COALESCE(discount_amount, 0) + COALESCE(shipping_fee, 0)) AS avg_extra
    FROM orders;
    ```


    **실행 결과** (1행)

    | total_orders | extra_charges | avg_extra |
    |---|---|---|
    | 37,557 | 361,289,400.00 | 9,619.76 |


---


### 29. 다음 쿼리는 가격대별 상품 수를 구합니다. CASE 조건 순서에 문제가 있습니다.


다음 쿼리는 가격대별 상품 수를 구합니다. CASE 조건 순서에 문제가 있습니다.


**힌트 1:** CASE는 위에서 아래로 순서대로 평가되며, 첫 번째로 TRUE인 조건에서 멈춥니다. 모든 상품의 가격은 0 이상입니다.


??? success "정답"
    ```sql
    SELECT CASE
               WHEN price >= 1000000 THEN '고가'
               WHEN price >= 500000 THEN '중가'
               WHEN price >= 100000 THEN '중저가'
               ELSE '저가'
           END AS price_tier,
           COUNT(*) AS cnt
    FROM products
    GROUP BY price_tier;
    ```


    **실행 결과** (4행)

    | price_tier | cnt |
    |---|---|
    | 고가 | 65 |
    | 저가 | 47 |
    | 중가 | 38 |
    | 중저가 | 130 |


---


### 30. 다음 쿼리는 고객의 가입 연도별 데이터를 분석합니다. WHERE와 HAVING이 혼동되어 있습니다.


다음 쿼리는 고객의 가입 연도별 데이터를 분석합니다. WHERE와 HAVING이 혼동되어 있습니다.


**힌트 1:** HAVING이 두 번 사용되었고, SQL 절의 순서도 틀렸습니다. 개별 행 필터링과 그룹 필터링을 구분하세요.


??? success "정답"
    ```sql
    SELECT SUBSTR(created_at, 1, 4) AS join_year,
           grade,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    WHERE grade IN ('GOLD', 'VIP')
    GROUP BY join_year, grade
    HAVING COUNT(*) >= 50
    ORDER BY join_year, grade;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | join_year | grade | customer_count | avg_points |
    |---|---|---|---|
    | 2020 | GOLD | 63 | 243,137.00 |
    | 2021 | GOLD | 101 | 142,592.00 |
    | 2021 | VIP | 60 | 409,715.00 |
    | 2022 | GOLD | 72 | 119,752.00 |
    | 2022 | VIP | 60 | 296,670.00 |
    | 2023 | GOLD | 67 | 73,467.00 |
    | 2023 | VIP | 58 | 203,509.00 |


---
