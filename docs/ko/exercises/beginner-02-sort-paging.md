# 정렬과 페이징

!!! info "사용 테이블"

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `reviews` — 리뷰 (평점, 내용)  

    `payments` — 결제 (방법, 금액, 상태)  



!!! abstract "학습 범위"

    `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `OFFSET`, `DISTINCT`, `AS`, `arithmetic operations`



### 1. 상품을 가격이 비싼 순서대로 정렬하여 이름(`name`)과 가격(`price`)을 조회하세요.


상품을 가격이 비싼 순서대로 정렬하여 이름(`name`)과 가격(`price`)을 조회하세요.


**힌트 1:** ORDER BY price DESC를 사용하면 내림차순 정렬입니다


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC;
    ```


    **실행 결과** (총 280행 중 상위 7행)

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


### 2. 상품을 가격이 저렴한 순서대로 정렬하여 이름, 브랜드(`brand`), 가격을 조회하세요.


상품을 가격이 저렴한 순서대로 정렬하여 이름, 브랜드(`brand`), 가격을 조회하세요.


**힌트 1:** ORDER BY price ASC 또는 ORDER BY price만 써도 오름차순(기본값)입니다


??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    ORDER BY price ASC;
    ```


    **실행 결과** (총 280행 중 상위 7행)

    | name | brand | price |
    |---|---|---|
    | TP-Link TG-3468 블랙 | TP-Link | 18,500.00 |
    | 삼성 SPA-KFG0BUB 실버 | 삼성전자 | 21,900.00 |
    | Arctic Freezer 36 A-RGB 화이트 | Arctic | 23,000.00 |
    | Arctic Freezer 36 A-RGB 화이트 | Arctic | 29,900.00 |
    | TP-Link Archer TBE400E 화이트 | TP-Link | 30,200.00 |
    | 삼성 SPA-KFG0BUB | 삼성전자 | 30,700.00 |
    | 로지텍 MK470 블랙 | 로지텍 | 31,800.00 |


---


### 3. 가장 비싼 상품 5개의 이름과 가격을 조회하세요.


가장 비싼 상품 5개의 이름과 가격을 조회하세요.


**힌트 1:** ORDER BY로 정렬한 뒤 LIMIT으로 상위 N개만 가져옵니다


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | price |
    |---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 |
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 |
    | Razer Blade 18 블랙 | 4,353,100.00 |
    | Razer Blade 16 실버 | 3,702,900.00 |


---


### 4. 재고 수량(`stock_qty`)이 가장 적은 상품 5개의 이름, 가격, 재고 수량을 조회하세요.


재고 수량(`stock_qty`)이 가장 적은 상품 5개의 이름, 가격, 재고 수량을 조회하세요.


**힌트 1:** ORDER BY stock_qty ASC로 오름차순 정렬하면 재고가 적은 순서입니다


??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    ORDER BY stock_qty ASC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | price | stock_qty |
    |---|---|---|
    | Arctic Freezer 36 A-RGB 화이트 | 23,000.00 | 0 |
    | 삼성 SPA-KFG0BUB | 30,700.00 | 4 |
    | 삼성 DDR4 32GB PC4-25600 | 91,000.00 | 6 |
    | Norton AntiVirus Plus | 69,700.00 | 8 |
    | 로지텍 G502 HERO 실버 | 71,100.00 | 8 |


---


### 5. 고객을 가입일(`created_at`) 순서대로 정렬하여 가장 먼저 가입한 고객 5명의 이름, 이메일, 등급


고객을 가입일(`created_at`) 순서대로 정렬하여 가장 먼저 가입한 고객 5명의 이름, 이메일, 등급(`grade`), 가입일을 조회하세요.


**힌트 1:** 가장 오래된 가입일이 먼저 나오려면 ORDER BY created_at ASC를 사용합니다


??? success "정답"
    ```sql
    SELECT name, email, grade, created_at
    FROM customers
    ORDER BY created_at ASC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | email | grade | created_at |
    |---|---|---|---|
    | 양영진 | user84@testmail.kr | BRONZE | 2016-01-03 19:49:46 |
    | 이승민 | user61@testmail.kr | BRONZE | 2016-01-04 14:11:21 |
    | 유현지 | user90@testmail.kr | GOLD | 2016-01-05 22:02:29 |
    | 이영자 | user98@testmail.kr | VIP | 2016-01-09 06:08:34 |
    | 강은서 | user15@testmail.kr | BRONZE | 2016-01-14 06:39:08 |


---


### 6. 상품 이름을 알파벳/가나다 순서대로 정렬하여 처음 5개를 조회하세요.


상품 이름을 알파벳/가나다 순서대로 정렬하여 처음 5개를 조회하세요.


**힌트 1:** ORDER BY name으로 정렬하면 영문 알파벳이 한글보다 먼저 옵니다


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY name
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | price |
    |---|---|
    | AMD Ryzen 9 9900X | 335,700.00 |
    | AMD Ryzen 9 9900X | 591,800.00 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | 516,300.00 |
    | ASRock B850M Pro RS 블랙 | 201,000.00 |
    | ASRock B850M Pro RS 실버 | 665,600.00 |


---


### 7. 가격이 비싼 상품 상위 6~10위를 조회하세요. (즉, 상위 5개를 건너뛰고 다음 5개)


가격이 비싼 상품 상위 6~10위를 조회하세요. (즉, 상위 5개를 건너뛰고 다음 5개)


**힌트 1:** OFFSET은 지정한 행 수만큼 건너뜁니다. LIMIT 5 OFFSET 5로 6번째부터 가져옵니다


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5 OFFSET 5;
    ```


    **실행 결과** (5행)

    | name | price |
    |---|---|
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 |
    | ASUS ROG Strix GT35 | 3,296,800.00 |
    | Razer Blade 18 블랙 | 2,987,500.00 |
    | ASUS Dual RTX 4060 Ti 블랙 | 2,674,800.00 |


---


### 8. 적립금(`point_balance`)이 가장 많은 고객 5명의 이름, 등급, 적립금을 조회하세요.


적립금(`point_balance`)이 가장 많은 고객 5명의 이름, 등급, 적립금을 조회하세요.


**힌트 1:** ORDER BY point_balance DESC로 내림차순 정렬 후 LIMIT 5를 적용합니다


??? success "정답"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    ORDER BY point_balance DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | grade | point_balance |
    |---|---|---|
    | 박정수 | VIP | 3,955,828 |
    | 김병철 | VIP | 3,518,880 |
    | 강명자 | VIP | 2,450,166 |
    | 정유진 | VIP | 2,383,491 |
    | 김성민 | VIP | 2,297,542 |


---


### 9. 주문 금액(`total_amount`)이 가장 큰 주문 5건의 주문번호(`order_number`), 주문 


주문 금액(`total_amount`)이 가장 큰 주문 5건의 주문번호(`order_number`), 주문 금액, 주문일(`ordered_at`)을 조회하세요.


**힌트 1:** orders 테이블에서 ORDER BY total_amount DESC LIMIT 5를 사용합니다


??? success "정답"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | order_number | total_amount | ordered_at |
    |---|---|---|
    | ORD-20201121-08810 | 50,867,500.00 | 2020-11-21 12:04:42 |
    | ORD-20250305-32265 | 46,820,024.00 | 2025-03-05 09:01:08 |
    | ORD-20230523-22331 | 46,094,971.00 | 2023-05-23 08:50:55 |
    | ORD-20200209-05404 | 43,677,500.00 | 2020-02-09 23:36:36 |
    | ORD-20221231-20394 | 43,585,700.00 | 2022-12-31 21:35:59 |


---


### 10. 상품 테이블에 등록된 브랜드 목록을 중복 없이 알파벳 순서대로 조회하세요.


상품 테이블에 등록된 브랜드 목록을 중복 없이 알파벳 순서대로 조회하세요.


**힌트 1:** SELECT DISTINCT brand로 중복을 제거하고, ORDER BY brand로 정렬합니다


??? success "정답"
    ```sql
    SELECT DISTINCT brand
    FROM products
    ORDER BY brand;
    ```


    **실행 결과** (총 55행 중 상위 7행)

    | brand |
    |---|
    | AMD |
    | APC |
    | ASRock |
    | ASUS |
    | Adobe |
    | Apple |
    | Arctic |


---


### 11. 가격이 100만 원 이상인 상품을 비싼 순서대로 정렬하여 이름, 브랜드, 가격을 조회하세요. 상위 5개만 출


가격이 100만 원 이상인 상품을 비싼 순서대로 정렬하여 이름, 브랜드, 가격을 조회하세요. 상위 5개만 출력합니다.


**힌트 1:** WHERE price >= 1000000으로 필터링한 뒤 ORDER BY price DESC LIMIT 5를 적용합니다


??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price >= 1000000
    ORDER BY price DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | brand | price |
    |---|---|---|
    | MacBook Air 15 M3 실버 | Apple | 5,481,100.00 |
    | ASUS TUF Gaming RTX 5080 화이트 | ASUS | 4,526,600.00 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | ASUS | 4,496,700.00 |
    | Razer Blade 18 블랙 | Razer | 4,353,100.00 |
    | Razer Blade 16 실버 | Razer | 3,702,900.00 |


---


### 12. 삼성전자 또는 LG전자 브랜드 상품을 가격 내림차순으로 정렬하여 이름, 브랜드, 가격을 조회하세요. 상위 5


삼성전자 또는 LG전자 브랜드 상품을 가격 내림차순으로 정렬하여 이름, 브랜드, 가격을 조회하세요. 상위 5개만 출력합니다.


**힌트 1:** WHERE brand IN ('삼성전자', 'LG전자')로 두 브랜드를 필터링합니다


??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand IN ('삼성전자', 'LG전자')
    ORDER BY price DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | brand | price |
    |---|---|---|
    | 삼성 오디세이 G5 27 블랙 | 삼성전자 | 1,833,000.00 |
    | LG 27UQ85R | LG전자 | 1,828,800.00 |
    | LG 27UQ85R 화이트 | LG전자 | 1,785,800.00 |
    | 삼성 갤럭시북5 프로 블랙 | 삼성전자 | 1,739,900.00 |
    | LG 그램 14 | LG전자 | 1,734,000.00 |


---


### 13. VIP 등급 고객 중 성이 '김'인 고객을 적립금이 많은 순서대로 정렬하여 이름, 등급, 적립금을 5명만 조


VIP 등급 고객 중 성이 '김'인 고객을 적립금이 많은 순서대로 정렬하여 이름, 등급, 적립금을 5명만 조회하세요.


**힌트 1:** WHERE grade = 'VIP' AND name LIKE '김%'로 두 조건을 동시에 적용합니다


??? success "정답"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    WHERE grade = 'VIP'
      AND name LIKE '김%'
    ORDER BY point_balance DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | grade | point_balance |
    |---|---|---|
    | 김병철 | VIP | 3,518,880 |
    | 김성민 | VIP | 2,297,542 |
    | 김민재 | VIP | 1,564,015 |
    | 김예은 | VIP | 1,312,100 |
    | 김예진 | VIP | 1,097,500 |


---


### 14. 판매 중단된 상품(`discontinued_at`이 NULL이 아닌 상품)을 중단일 기준 최신순으로 정렬하여


판매 중단된 상품(`discontinued_at`이 NULL이 아닌 상품)을 중단일 기준 최신순으로 정렬하여 이름, 가격, 중단일을 5개만 조회하세요.


**힌트 1:** WHERE discontinued_at IS NOT NULL로 판매 중단 상품만 필터링합니다


??? success "정답"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL
    ORDER BY discontinued_at DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | price | discontinued_at |
    |---|---|---|
    | Dell XPS Desktop 8960 실버 | 1,249,400.00 | 2025-11-20 15:30:12 |
    | Kingston FURY Beast DDR4 16GB 화이트 | 91,200.00 | 2025-11-18 04:06:13 |
    | Intel Core Ultra 7 265K | 196,300.00 | 2025-11-16 21:11:33 |
    | 한성 보스몬스터 DX7700 화이트 | 1,579,400.00 | 2025-10-25 03:47:01 |
    | Intel Core Ultra 7 265K 화이트 | 170,200.00 | 2025-08-24 00:34:53 |


---


### 15. 리뷰 평점(`rating`)이 1점인 리뷰를 최신순으로 정렬하여 제목(`title`), 평점, 작성일(`cr


리뷰 평점(`rating`)이 1점인 리뷰를 최신순으로 정렬하여 제목(`title`), 평점, 작성일(`created_at`)을 5개 조회하세요.


**힌트 1:** reviews 테이블에서 WHERE rating = 1로 필터링하고 ORDER BY created_at DESC로 정렬합니다


??? success "정답"
    ```sql
    SELECT title, rating, created_at
    FROM reviews
    WHERE rating = 1
    ORDER BY created_at DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | title | rating | created_at |
    |---|---|---|
    | NULL | 1 | 2026-01-05 20:37:52 |
    | NULL | 1 | 2025-12-21 21:52:59 |
    | 다신 안삽니다 | 1 | 2025-12-20 11:53:58 |
    | NULL | 1 | 2025-12-19 08:58:30 |
    | 불량품 | 1 | 2025-12-14 10:07:24 |


---


### 16. 가격이 50만 원 이상 100만 원 이하인 상품을 가격 오름차순으로 정렬하여 이름, 브랜드, 가격을 5개 조


가격이 50만 원 이상 100만 원 이하인 상품을 가격 오름차순으로 정렬하여 이름, 브랜드, 가격을 5개 조회하세요.


**힌트 1:** WHERE price BETWEEN 500000 AND 1000000으로 범위를 지정합니다


??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price BETWEEN 500000 AND 1000000
    ORDER BY price ASC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | brand | price |
    |---|---|---|
    | CyberPower BRG1500AVRLCD 실버 | CyberPower | 508,100.00 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | APC | 516,300.00 |
    | 필립스 27E1N5300AE 화이트 | 필립스 | 518,700.00 |
    | 기가바이트 Z790 AORUS MASTER | 기가바이트 | 520,400.00 |
    | 엡손 L3260 | 엡손 | 525,400.00 |


---


### 17. 카드 결제(`method = 'card'`) 중 할부 개월 수(`installment_months`)가 0보


카드 결제(`method = 'card'`) 중 할부 개월 수(`installment_months`)가 0보다 큰 건을 할부 개월 수 내림차순, 결제 금액(`amount`) 내림차순으로 정렬하여 5건 조회하세요. 주문 ID, 결제 금액, 카드사(`card_issuer`), 할부 개월 수를 출력합니다.


**힌트 1:** ORDER BY 뒤에 칼럼을 쉼표로 구분하면 다중 정렬이 됩니다. 첫 번째 칼럼이 같을 때 두 번째 칼럼으로 정렬합니다


??? success "정답"
    ```sql
    SELECT order_id, amount, card_issuer, installment_months
    FROM payments
    WHERE method = 'card'
      AND installment_months > 0
    ORDER BY installment_months DESC, amount DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | order_id | amount | card_issuer | installment_months |
    |---|---|---|---|
    | 14,056 | 22,995,900.00 | 신한카드 | 24 |
    | 37,522 | 13,678,700.00 | 신한카드 | 24 |
    | 2471 | 13,669,032.00 | KB국민카드 | 24 |
    | 3789 | 9,690,532.00 | 삼성카드 | 24 |
    | 20,271 | 6,484,600.00 | 현대카드 | 24 |


---


### 18. GOLD 등급 고객을 이름 가나다순으로 정렬하여 11~15번째 고객의 이름과 이메일을 조회하세요.


GOLD 등급 고객을 이름 가나다순으로 정렬하여 11~15번째 고객의 이름과 이메일을 조회하세요.


**힌트 1:** 11번째부터 시작하려면 OFFSET 10 (10개를 건너뜀), 5명을 가져오려면 LIMIT 5입니다


??? success "정답"
    ```sql
    SELECT name, email
    FROM customers
    WHERE grade = 'GOLD'
    ORDER BY name
    LIMIT 5 OFFSET 10;
    ```


    **실행 결과** (5행)

    | name | email |
    |---|---|
    | 강현준 | user2268@testmail.kr |
    | 강현지 | user1532@testmail.kr |
    | 고경숙 | user1293@testmail.kr |
    | 고성훈 | user4235@testmail.kr |
    | 곽순자 | user2422@testmail.kr |


---


### 19. 결제 수단(`method`)의 종류를 중복 없이 조회하세요.


결제 수단(`method`)의 종류를 중복 없이 조회하세요.


**힌트 1:** SELECT DISTINCT method FROM payments를 사용합니다


??? success "정답"
    ```sql
    SELECT DISTINCT method
    FROM payments
    ORDER BY method;
    ```


    **실행 결과** (6행)

    | method |
    |---|
    | bank_transfer |
    | card |
    | kakao_pay |
    | naver_pay |
    | point |
    | virtual_account |


---


### 20. 상품의 이름, 가격, 원가(`cost_price`), 마진(가격 - 원가)을 마진이 큰 순서대로 정렬하여 5


상품의 이름, 가격, 원가(`cost_price`), 마진(가격 - 원가)을 마진이 큰 순서대로 정렬하여 5개 조회하세요. 마진 칼럼에는 `margin`이라는 별칭을 붙이세요.


**힌트 1:** SELECT 절에서 price - cost_price AS margin으로 계산 칼럼을 만들 수 있습니다


??? success "정답"
    ```sql
    SELECT name, price, cost_price, price - cost_price AS margin
    FROM products
    ORDER BY margin DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | price | cost_price | margin |
    |---|---|---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 | 3,205,400.00 | 2,275,700.00 |
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 | 3,037,100.00 | 1,489,500.00 |
    | Razer Blade 18 블랙 | 4,353,100.00 | 3,047,200.00 | 1,305,900.00 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 | 3,296,400.00 | 1,200,300.00 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 | 2,480,900.00 | 1,190,600.00 |


---


### 21. 취소된 주문(`status = 'cancelled'`) 중 주문 금액이 가장 큰 5건의 주문번호, 주문 금액


취소된 주문(`status = 'cancelled'`) 중 주문 금액이 가장 큰 5건의 주문번호, 주문 금액, 취소일(`cancelled_at`)을 조회하세요.


**힌트 1:** WHERE status = 'cancelled'로 필터링하고 ORDER BY total_amount DESC로 정렬합니다


??? success "정답"
    ```sql
    SELECT order_number, total_amount, cancelled_at
    FROM orders
    WHERE status = 'cancelled'
    ORDER BY total_amount DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | order_number | total_amount | cancelled_at |
    |---|---|---|
    | ORD-20230523-22331 | 46,094,971.00 | 2023-05-24 05:50:55 |
    | ORD-20221231-20394 | 43,585,700.00 | 2023-01-02 16:35:59 |
    | ORD-20211112-14229 | 20,640,700.00 | 2021-11-14 07:35:09 |
    | ORD-20250307-32312 | 18,229,600.00 | 2025-03-09 07:13:31 |
    | ORD-20250924-35599 | 14,735,700.00 | 2025-09-25 13:46:38 |


---


### 22. 재고가 10개 이하인 상품을 재고 오름차순, 가격 내림차순으로 정렬하여 이름, 가격, 재고 수량을 조회하세요


재고가 10개 이하인 상품을 재고 오름차순, 가격 내림차순으로 정렬하여 이름, 가격, 재고 수량을 조회하세요.


**힌트 1:** WHERE stock_qty <= 10으로 필터링하고 ORDER BY stock_qty ASC, price DESC로 다중 정렬합니다


??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE stock_qty <= 10
    ORDER BY stock_qty ASC, price DESC;
    ```


    **실행 결과** (5행)

    | name | price | stock_qty |
    |---|---|---|
    | Arctic Freezer 36 A-RGB 화이트 | 23,000.00 | 0 |
    | 삼성 SPA-KFG0BUB | 30,700.00 | 4 |
    | 삼성 DDR4 32GB PC4-25600 | 91,000.00 | 6 |
    | 로지텍 G502 HERO 실버 | 71,100.00 | 8 |
    | Norton AntiVirus Plus | 69,700.00 | 8 |


---


### 23. 한 번도 로그인하지 않은 고객(`last_login_at`이 NULL)을 가입일 순서대로 정렬하여 이름, 이


한 번도 로그인하지 않은 고객(`last_login_at`이 NULL)을 가입일 순서대로 정렬하여 이름, 이메일, 등급을 10명 조회하세요.


**힌트 1:** NULL 여부는 = NULL이 아니라 IS NULL로 확인합니다


??? success "정답"
    ```sql
    SELECT name, email, grade
    FROM customers
    WHERE last_login_at IS NULL
    ORDER BY created_at ASC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | email | grade |
    |---|---|---|
    | 윤준영 | user25@testmail.kr | BRONZE |
    | 이영식 | user43@testmail.kr | BRONZE |
    | 김지우 | user77@testmail.kr | BRONZE |
    | 송서준 | user66@testmail.kr | BRONZE |
    | 박아름 | user80@testmail.kr | BRONZE |
    | 오지후 | user172@testmail.kr | BRONZE |
    | 권지우 | user169@testmail.kr | BRONZE |


---


### 24. 상품의 이름, 가격, 부가세 포함 가격을 조회하세요. 부가세 포함 가격은 `price * 1.1`로 계산하고


상품의 이름, 가격, 부가세 포함 가격을 조회하세요. 부가세 포함 가격은 `price * 1.1`로 계산하고 `price_with_tax`라는 별칭을 붙이세요. 부가세 포함 가격이 비싼 순서대로 5개만 출력합니다.


**힌트 1:** ROUND(price * 1.1)로 소수점을 정리하면 깔끔한 결과를 얻을 수 있습니다


??? success "정답"
    ```sql
    SELECT name, price, ROUND(price * 1.1) AS price_with_tax
    FROM products
    ORDER BY price_with_tax DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | price | price_with_tax |
    |---|---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 | 6,029,210.00 |
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 | 4,979,260.00 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 | 4,946,370.00 |
    | Razer Blade 18 블랙 | 4,353,100.00 | 4,788,410.00 |
    | Razer Blade 16 실버 | 3,702,900.00 | 4,073,190.00 |


---


### 25. 2024년에 접수된 주문(`ordered_at`이 2024년) 중 주문 금액이 가장 큰 5건의 주문번호, 주


2024년에 접수된 주문(`ordered_at`이 2024년) 중 주문 금액이 가장 큰 5건의 주문번호, 주문 금액, 주문일을 조회하세요.


**힌트 1:** WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'로 2024년 범위를 지정합니다


??? success "정답"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at < '2025-01-01'
    ORDER BY total_amount DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | order_number | total_amount | ordered_at |
    |---|---|---|
    | ORD-20240519-27622 | 33,762,000.00 | 2024-05-19 22:17:20 |
    | ORD-20240920-29424 | 30,446,100.00 | 2024-09-20 12:04:46 |
    | ORD-20240425-27274 | 25,694,900.00 | 2024-04-25 10:44:48 |
    | ORD-20241101-30141 | 21,201,100.00 | 2024-11-01 20:47:38 |
    | ORD-20240112-25581 | 18,265,900.00 | 2024-01-12 08:33:51 |


---


### 26. 할인 금액(`discount_amount`)이 0보다 큰 주문을 할인 금액이 큰 순서대로 정렬하여 주문번호,


할인 금액(`discount_amount`)이 0보다 큰 주문을 할인 금액이 큰 순서대로 정렬하여 주문번호, 주문 금액, 할인 금액, 주문일을 5건 조회하세요.


**힌트 1:** WHERE discount_amount > 0으로 할인이 적용된 주문만 필터링합니다


??? success "정답"
    ```sql
    SELECT order_number, total_amount, discount_amount, ordered_at
    FROM orders
    WHERE discount_amount > 0
    ORDER BY discount_amount DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | order_number | total_amount | discount_amount | ordered_at |
    |---|---|---|---|
    | ORD-20221108-19517 | 33,599,000.00 | 3,837,300.00 | 2022-11-08 05:28:41 |
    | ORD-20220713-17752 | 32,950,400.00 | 3,126,300.00 | 2022-07-13 16:06:23 |
    | ORD-20180910-01979 | 32,615,814.00 | 2,690,000.00 | 2018-09-10 15:12:37 |
    | ORD-20230930-23961 | 27,295,300.00 | 2,248,800.00 | 2023-09-30 20:13:24 |
    | ORD-20220224-15869 | 35,397,700.00 | 1,924,100.00 | 2022-02-24 23:01:50 |


---


### 27. 카카오페이(`method = 'kakao_pay'`)로 결제된 건을 결제 금액이 큰 순서대로 정렬하여 주문 


카카오페이(`method = 'kakao_pay'`)로 결제된 건을 결제 금액이 큰 순서대로 정렬하여 주문 ID(`order_id`), 결제 금액, 결제일(`paid_at`)을 5건 조회하세요.


**힌트 1:** payments 테이블에서 WHERE method = 'kakao_pay'로 필터링합니다


??? success "정답"
    ```sql
    SELECT order_id, amount, paid_at
    FROM payments
    WHERE method = 'kakao_pay'
    ORDER BY amount DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | order_id | amount | paid_at |
    |---|---|---|
    | 1979 | 32,615,814.00 | 2018-09-10 15:34:37 |
    | 37,004 | 31,985,600.00 | 2025-12-07 23:36:41 |
    | 15,027 | 28,836,100.00 | 2021-12-23 20:02:54 |
    | 25,227 | 27,440,200.00 | 2023-12-15 11:44:54 |
    | 14,074 | 22,470,000.00 | 2021-11-02 15:36:38 |


---


### 28. 2025년에 가입한 고객 중 GOLD 또는 VIP 등급인 고객을 적립금이 많은 순서대로 5명 조회하세요. 이


2025년에 가입한 고객 중 GOLD 또는 VIP 등급인 고객을 적립금이 많은 순서대로 5명 조회하세요. 이름, 등급, 적립금, 가입일을 출력합니다.


**힌트 1:** WHERE created_at >= '2025-01-01' AND grade IN ('GOLD', 'VIP')로 조건을 조합합니다


??? success "정답"
    ```sql
    SELECT name, grade, point_balance, created_at
    FROM customers
    WHERE created_at >= '2025-01-01'
      AND grade IN ('GOLD', 'VIP')
    ORDER BY point_balance DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | grade | point_balance | created_at |
    |---|---|---|---|
    | 성진우 | VIP | 323,554 | 2025-10-24 12:23:58 |
    | 서상철 | VIP | 263,155 | 2025-03-03 21:41:00 |
    | 이미정 | VIP | 126,048 | 2025-03-05 01:34:09 |
    | 이경자 | VIP | 122,578 | 2025-02-07 19:27:08 |
    | 윤정자 | VIP | 109,984 | 2025-03-11 13:39:02 |


---


### 29. ASUS 브랜드가 아닌 상품(`brand != 'ASUS'`) 중 삼성전자, LG전자, MSI도 제외한 상품


ASUS 브랜드가 아닌 상품(`brand != 'ASUS'`) 중 삼성전자, LG전자, MSI도 제외한 상품을 가격 내림차순으로 5개 조회하세요. 이름, 브랜드, 가격을 출력합니다.


**힌트 1:** NOT IN을 사용하면 여러 값을 한꺼번에 제외할 수 있습니다


??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand NOT IN ('ASUS', '삼성전자', 'LG전자', 'MSI')
    ORDER BY price DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | brand | price |
    |---|---|---|
    | MacBook Air 15 M3 실버 | Apple | 5,481,100.00 |
    | Razer Blade 18 블랙 | Razer | 4,353,100.00 |
    | Razer Blade 16 실버 | Razer | 3,702,900.00 |
    | Razer Blade 18 블랙 | Razer | 2,987,500.00 |
    | Razer Blade 18 화이트 | Razer | 2,483,600.00 |


---


### 30. 무게(`weight_grams`)가 기록된 상품 중 가장 무거운 상품 5개의 이름, 무게(그램), 가격을 조


무게(`weight_grams`)가 기록된 상품 중 가장 무거운 상품 5개의 이름, 무게(그램), 가격을 조회하세요. 무게를 킬로그램으로 환산한 `weight_kg` 칼럼도 함께 출력하세요.


**힌트 1:** WHERE weight_grams IS NOT NULL로 무게가 있는 상품만 필터링합니다. weight_grams / 1000.0으로 킬로그램을 계산합니다


??? success "정답"
    ```sql
    SELECT name,
           weight_grams,
           ROUND(weight_grams / 1000.0, 1) AS weight_kg,
           price
    FROM products
    WHERE weight_grams IS NOT NULL
    ORDER BY weight_grams DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | weight_grams | weight_kg | price |
    |---|---|---|---|
    | ASUS ROG Strix GT35 | 19,449 | 19.40 | 3,296,800.00 |
    | 한성 보스몬스터 DX7700 화이트 | 19,250 | 19.30 | 1,579,400.00 |
    | ASUS ROG Strix G16CH 화이트 | 16,624 | 16.60 | 3,671,500.00 |
    | 한성 보스몬스터 DX9900 실버 | 14,892 | 14.90 | 739,900.00 |
    | ASUS ROG Strix G16CH 실버 | 14,308 | 14.30 | 1,879,100.00 |


---
