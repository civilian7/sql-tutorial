# 그룹화와 필터

!!! info "사용 테이블"

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `reviews` — 리뷰 (평점, 내용)  

    `payments` — 결제 (방법, 금액, 상태)  

    `complaints` — 고객 불만 (유형, 우선순위)  



!!! abstract "학습 범위"

    `GROUP BY`, `HAVING`, `Aggregate functions`, `Multi-column grouping`



### 1. 브랜드(brand)별로 등록된 상품이 몇 개인지 조회하세요. 상품 수가 많은 순으로 정렬합니다.


브랜드(brand)별로 등록된 상품이 몇 개인지 조회하세요. 상품 수가 많은 순으로 정렬합니다.


**힌트 1:** GROUP BY brand와 COUNT(*)를 사용하세요


??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    ORDER BY product_count DESC;
    ```


    **실행 결과** (총 55행 중 상위 7행)

    | brand | product_count |
    |---|---|
    | ASUS | 26 |
    | 삼성전자 | 25 |
    | 로지텍 | 17 |
    | MSI | 13 |
    | TP-Link | 11 |
    | LG전자 | 11 |
    | ASRock | 11 |


---


### 2. 고객 등급(grade)별 고객 수를 조회하세요.


고객 등급(grade)별 고객 수를 조회하세요.


**힌트 1:** GROUP BY grade와 COUNT(*)를 사용하세요


??? success "정답"
    ```sql
    SELECT grade, COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade
    ORDER BY customer_count DESC;
    ```


    **실행 결과** (4행)

    | grade | customer_count |
    |---|---|
    | BRONZE | 3859 |
    | GOLD | 524 |
    | SILVER | 479 |
    | VIP | 368 |


---


### 3. 주문 상태(status)별로 주문 건수와 총 매출(total_amount 합계)을 조회하세요.


주문 상태(status)별로 주문 건수와 총 매출(total_amount 합계)을 조회하세요.


**힌트 1:** GROUP BY status, COUNT(*), SUM(total_amount)를 함께 사용하세요


??? success "정답"
    ```sql
    SELECT
        status,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 0) AS total_revenue
    FROM orders
    GROUP BY status
    ORDER BY total_revenue DESC;
    ```


    **실행 결과** (총 9행 중 상위 7행)

    | status | order_count | total_revenue |
    |---|---|---|
    | confirmed | 34,393 | 34,386,590,179.00 |
    | cancelled | 1859 | 1,943,134,782.00 |
    | return_requested | 507 | 811,487,700.00 |
    | returned | 493 | 659,444,574.00 |
    | delivered | 125 | 195,768,235.00 |
    | pending | 82 | 87,230,243.00 |
    | shipped | 51 | 74,070,546.00 |


---


### 4. 별점(rating) 1~5점별로 리뷰가 몇 건인지 조회하세요. 별점순으로 정렬합니다.


별점(rating) 1~5점별로 리뷰가 몇 건인지 조회하세요. 별점순으로 정렬합니다.


**힌트 1:** GROUP BY rating과 COUNT(*)를 사용하세요


??? success "정답"
    ```sql
    SELECT rating, COUNT(*) AS review_count
    FROM reviews
    GROUP BY rating
    ORDER BY rating;
    ```


    **실행 결과** (5행)

    | rating | review_count |
    |---|---|
    | 1 | 434 |
    | 2 | 839 |
    | 3 | 1265 |
    | 4 | 2575 |
    | 5 | 3433 |


---


### 5. 결제 수단(method)별로 결제 건수와 총 금액(amount 합계)을 조회하세요. 총 금액이 큰 순으로 정


결제 수단(method)별로 결제 건수와 총 금액(amount 합계)을 조회하세요. 총 금액이 큰 순으로 정렬합니다.


**힌트 1:** GROUP BY method와 SUM(amount)를 사용하세요


??? success "정답"
    ```sql
    SELECT
        method,
        COUNT(*) AS payment_count,
        ROUND(SUM(amount), 0) AS total_amount
    FROM payments
    GROUP BY method
    ORDER BY total_amount DESC;
    ```


    **실행 결과** (6행)

    | method | payment_count | total_amount |
    |---|---|---|
    | card | 16,841 | 17,004,951,634.00 |
    | kakao_pay | 7486 | 7,563,829,668.00 |
    | naver_pay | 5715 | 5,998,835,720.00 |
    | bank_transfer | 3718 | 3,753,149,013.00 |
    | point | 1921 | 1,951,369,604.00 |
    | virtual_account | 1876 | 1,911,359,424.00 |


---


### 6. 불만 접수 채널(channel)별로 접수 건수를 조회하세요. 건수가 많은 순으로 정렬합니다.


불만 접수 채널(channel)별로 접수 건수를 조회하세요. 건수가 많은 순으로 정렬합니다.


**힌트 1:** complaints 테이블의 channel 컬럼을 GROUP BY로 그룹화하세요


??? success "정답"
    ```sql
    SELECT channel, COUNT(*) AS complaint_count
    FROM complaints
    GROUP BY channel
    ORDER BY complaint_count DESC;
    ```


    **실행 결과** (5행)

    | channel | complaint_count |
    |---|---|
    | website | 1341 |
    | phone | 913 |
    | email | 796 |
    | chat | 583 |
    | kakao | 180 |


---


### 7. 가입 경로(acquisition_channel)별로 고객 수와 평균 포인트 잔액(point_balance)을


가입 경로(acquisition_channel)별로 고객 수와 평균 포인트 잔액(point_balance)을 조회하세요.


**힌트 1:** GROUP BY acquisition_channel과 AVG(point_balance)를 사용하세요. acquisition_channel이 NULL인 경우도 하나의 그룹으로 표시됩니다


??? success "정답"
    ```sql
    SELECT
        acquisition_channel,
        COUNT(*) AS customer_count,
        ROUND(AVG(point_balance), 0) AS avg_points
    FROM customers
    GROUP BY acquisition_channel
    ORDER BY avg_points DESC;
    ```


    **실행 결과** (5행)

    | acquisition_channel | customer_count | avg_points |
    |---|---|---|
    | organic | 1146 | 76,371.00 |
    | direct | 408 | 70,562.00 |
    | referral | 708 | 66,944.00 |
    | search_ad | 1543 | 62,449.00 |
    | social | 1425 | 54,311.00 |


---


### 8. 주문일(ordered_at)에서 연도를 추출하여 연도별 주문 건수와 총 매출을 조회하세요.


주문일(ordered_at)에서 연도를 추출하여 연도별 주문 건수와 총 매출을 조회하세요.


**힌트 1:** SUBSTR(ordered_at, 1, 4)로 연도를 추출하고 GROUP BY로 그룹화하세요


??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 0) AS total_revenue
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | year | order_count | total_revenue |
    |---|---|---|
    | 2016 | 416 | 331,746,909.00 |
    | 2017 | 709 | 653,085,068.00 |
    | 2018 | 1319 | 1,249,197,907.00 |
    | 2019 | 2589 | 2,620,111,601.00 |
    | 2020 | 4319 | 4,468,755,264.00 |
    | 2021 | 5841 | 6,044,718,738.00 |
    | 2022 | 5203 | 5,302,071,035.00 |


---


### 9. 브랜드(brand)별로 평균 판매 가격(price)과 평균 원가(cost_price)를 조회하세요. 평균 가


브랜드(brand)별로 평균 판매 가격(price)과 평균 원가(cost_price)를 조회하세요. 평균 가격이 높은 순으로 정렬합니다.


**힌트 1:** GROUP BY brand와 AVG(price), AVG(cost_price)를 함께 사용하세요


??? success "정답"
    ```sql
    SELECT
        brand,
        ROUND(AVG(price), 0) AS avg_price,
        ROUND(AVG(cost_price), 0) AS avg_cost
    FROM products
    GROUP BY brand
    ORDER BY avg_price DESC;
    ```


    **실행 결과** (총 55행 중 상위 7행)

    | brand | avg_price | avg_cost |
    |---|---|---|
    | Apple | 2,815,400.00 | 1,645,500.00 |
    | Razer | 1,764,889.00 | 1,518,700.00 |
    | ASUS | 1,683,631.00 | 1,225,488.00 |
    | 레노버 | 1,597,760.00 | 1,370,820.00 |
    | HP | 1,479,017.00 | 1,110,600.00 |
    | BenQ | 1,476,300.00 | 1,312,500.00 |
    | 주연테크 | 1,413,550.00 | 1,073,525.00 |


---


### 10. 불만 카테고리(category)별로 접수 건수와 평균 응대 횟수(response_count)를 조회하세요.


불만 카테고리(category)별로 접수 건수와 평균 응대 횟수(response_count)를 조회하세요.


**힌트 1:** GROUP BY category와 AVG(response_count)를 사용하세요


??? success "정답"
    ```sql
    SELECT
        category,
        COUNT(*) AS complaint_count,
        ROUND(AVG(response_count), 1) AS avg_responses
    FROM complaints
    GROUP BY category
    ORDER BY complaint_count DESC;
    ```


    **실행 결과** (7행)

    | category | complaint_count | avg_responses |
    |---|---|---|
    | general_inquiry | 1232 | 1.70 |
    | delivery_issue | 708 | 1.70 |
    | refund_request | 522 | 2.90 |
    | product_defect | 460 | 2.90 |
    | price_inquiry | 439 | 1.60 |
    | wrong_item | 240 | 2.80 |
    | exchange_request | 212 | 2.90 |


---


### 11. 브랜드별 상품 수를 구한 후, 상품이 10개 이상 등록된 브랜드만 조회하세요.


브랜드별 상품 수를 구한 후, 상품이 10개 이상 등록된 브랜드만 조회하세요.


**힌트 1:** GROUP BY 이후 그룹을 필터링할 때는 WHERE가 아니라 HAVING을 사용합니다


??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY product_count DESC;
    ```


    **실행 결과** (7행)

    | brand | product_count |
    |---|---|
    | ASUS | 26 |
    | 삼성전자 | 25 |
    | 로지텍 | 17 |
    | MSI | 13 |
    | TP-Link | 11 |
    | LG전자 | 11 |
    | ASRock | 11 |


---


### 12. 주문 상태(status)별 평균 주문 금액을 구하고, 평균이 300,000원 이상인 상태만 조회하세요.


주문 상태(status)별 평균 주문 금액을 구하고, 평균이 300,000원 이상인 상태만 조회하세요.


**힌트 1:** HAVING AVG(total_amount) >= 300000 으로 필터링하세요


??? success "정답"
    ```sql
    SELECT
        status,
        COUNT(*) AS order_count,
        ROUND(AVG(total_amount), 0) AS avg_amount
    FROM orders
    GROUP BY status
    HAVING AVG(total_amount) >= 300000
    ORDER BY avg_amount DESC;
    ```


    **실행 결과** (총 9행 중 상위 7행)

    | status | order_count | avg_amount |
    |---|---|---|
    | return_requested | 507 | 1,600,567.00 |
    | delivered | 125 | 1,566,146.00 |
    | shipped | 51 | 1,452,364.00 |
    | returned | 493 | 1,337,616.00 |
    | pending | 82 | 1,063,783.00 |
    | cancelled | 1859 | 1,045,258.00 |
    | confirmed | 34,393 | 999,814.00 |


---


### 13. 2024년 월별 주문 건수를 집계하고, 주문이 3,000건 이상인 월만 조회하세요.


2024년 월별 주문 건수를 집계하고, 주문이 3,000건 이상인 월만 조회하세요.


**힌트 1:** WHERE로 2024년을 먼저 필터링하고, GROUP BY로 월별 집계 후, HAVING으로 건수를 필터링하세요


??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS order_count
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    HAVING COUNT(*) >= 3000
    ORDER BY month;
    ```


---


### 14. 불만의 우선순위(priority)와 상태(status) 조합별로 건수를 조회하세요.


불만의 우선순위(priority)와 상태(status) 조합별로 건수를 조회하세요.


**힌트 1:** GROUP BY에 여러 컬럼을 쉼표로 나열할 수 있습니다: GROUP BY priority, status


??? success "정답"
    ```sql
    SELECT
        priority,
        status,
        COUNT(*) AS cnt
    FROM complaints
    GROUP BY priority, status
    ORDER BY priority, status;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | priority | status | cnt |
    |---|---|---|
    | high | closed | 773 |
    | high | open | 51 |
    | high | resolved | 134 |
    | low | closed | 1021 |
    | low | open | 66 |
    | low | resolved | 183 |
    | medium | closed | 1002 |


---


### 15. 성별(gender)과 등급(grade) 조합별로 고객 수를 조회하세요. 고객 수가 많은 순으로 정렬합니다.


성별(gender)과 등급(grade) 조합별로 고객 수를 조회하세요. 고객 수가 많은 순으로 정렬합니다.


**힌트 1:** GROUP BY gender, grade로 두 컬럼을 함께 그룹화하세요. gender가 NULL인 경우도 하나의 그룹으로 나타납니다


??? success "정답"
    ```sql
    SELECT
        gender,
        grade,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY gender, grade
    ORDER BY customer_count DESC;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | gender | grade | customer_count |
    |---|---|---|
    | M | BRONZE | 2128 |
    | F | BRONZE | 1302 |
    | NULL | BRONZE | 429 |
    | M | GOLD | 343 |
    | M | SILVER | 293 |
    | M | VIP | 268 |
    | F | SILVER | 141 |


---


### 16. 결제 상태가 'completed'인 건만 필터링하고, 결제 수단(method)별 평균 금액이 200,000원


결제 상태가 'completed'인 건만 필터링하고, 결제 수단(method)별 평균 금액이 200,000원 이상인 수단을 조회하세요.


**힌트 1:** WHERE로 status = 'completed'를 먼저 필터링하고, GROUP BY + HAVING으로 평균 금액을 필터링하세요


??? success "정답"
    ```sql
    SELECT
        method,
        COUNT(*) AS payment_count,
        ROUND(AVG(amount), 0) AS avg_amount
    FROM payments
    WHERE status = 'completed'
    GROUP BY method
    HAVING AVG(amount) >= 200000
    ORDER BY avg_amount DESC;
    ```


    **실행 결과** (6행)

    | method | payment_count | avg_amount |
    |---|---|---|
    | naver_pay | 5270 | 1,028,554.00 |
    | bank_transfer | 3429 | 1,008,007.00 |
    | point | 1770 | 1,005,839.00 |
    | virtual_account | 1705 | 1,001,042.00 |
    | card | 15,556 | 998,781.00 |
    | kakao_pay | 6886 | 984,768.00 |


---


### 17. 판매 중(is_active = 1)인 상품만 대상으로, 브랜드별 총 재고(stock_qty 합계)가 100개


판매 중(is_active = 1)인 상품만 대상으로, 브랜드별 총 재고(stock_qty 합계)가 100개 이상인 브랜드를 조회하세요.


**힌트 1:** WHERE is_active = 1로 활성 상품만 필터링한 후, GROUP BY brand + HAVING SUM(stock_qty) >= 100을 적용하세요


??? success "정답"
    ```sql
    SELECT
        brand,
        COUNT(*) AS product_count,
        SUM(stock_qty) AS total_stock
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING SUM(stock_qty) >= 100
    ORDER BY total_stock DESC;
    ```


    **실행 결과** (총 48행 중 상위 7행)

    | brand | product_count | total_stock |
    |---|---|---|
    | 삼성전자 | 21 | 6174 |
    | ASUS | 21 | 5828 |
    | MSI | 12 | 4070 |
    | ASRock | 9 | 3084 |
    | TP-Link | 11 | 3081 |
    | LG전자 | 11 | 2667 |
    | 로지텍 | 11 | 2461 |


---


### 18. 주문일에서 연도를 추출하여 연도와 상태(status) 조합별 주문 건수를 조회하세요.


주문일에서 연도를 추출하여 연도와 상태(status) 조합별 주문 건수를 조회하세요.


**힌트 1:** GROUP BY SUBSTR(ordered_at, 1, 4), status로 두 기준을 함께 그룹화하세요


??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        status,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4), status
    ORDER BY year, order_count DESC;
    ```


    **실행 결과** (총 45행 중 상위 7행)

    | year | status | order_count |
    |---|---|---|
    | 2016 | confirmed | 379 |
    | 2016 | cancelled | 15 |
    | 2016 | returned | 13 |
    | 2016 | return_requested | 9 |
    | 2017 | confirmed | 652 |
    | 2017 | cancelled | 41 |
    | 2017 | returned | 11 |


---


### 19. 상품(product_id)별 리뷰 수를 집계하고, 50건 이상인 상품만 조회하세요.


상품(product_id)별 리뷰 수를 집계하고, 50건 이상인 상품만 조회하세요.


**힌트 1:** GROUP BY product_id + HAVING COUNT(*) >= 50을 사용하세요


??? success "정답"
    ```sql
    SELECT
        product_id,
        COUNT(*) AS review_count
    FROM reviews
    GROUP BY product_id
    HAVING COUNT(*) >= 50
    ORDER BY review_count DESC;
    ```


    **실행 결과** (총 52행 중 상위 7행)

    | product_id | review_count |
    |---|---|
    | 100 | 105 |
    | 176 | 102 |
    | 111 | 101 |
    | 45 | 100 |
    | 139 | 89 |
    | 102 | 87 |
    | 124 | 82 |


---


### 20. 등급(grade)과 가입 채널(acquisition_channel) 조합별 고객 수를 구하고, 100명 이상


등급(grade)과 가입 채널(acquisition_channel) 조합별 고객 수를 구하고, 100명 이상인 조합만 조회하세요.


**힌트 1:** GROUP BY grade, acquisition_channel 후 HAVING COUNT(*) >= 100으로 필터링하세요


??? success "정답"
    ```sql
    SELECT
        grade,
        acquisition_channel,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade, acquisition_channel
    HAVING COUNT(*) >= 100
    ORDER BY grade, customer_count DESC;
    ```


    **실행 결과** (총 11행 중 상위 7행)

    | grade | acquisition_channel | customer_count |
    |---|---|---|
    | BRONZE | search_ad | 1118 |
    | BRONZE | social | 1074 |
    | BRONZE | organic | 838 |
    | BRONZE | referral | 528 |
    | BRONZE | direct | 301 |
    | GOLD | search_ad | 151 |
    | GOLD | organic | 137 |


---


### 21. 2024년 주문을 분기별로 나누어 주문 건수, 총 매출, 평균 주문 금액을 조회하세요. 분기는 월을 기준으로


2024년 주문을 분기별로 나누어 주문 건수, 총 매출, 평균 주문 금액을 조회하세요. 분기는 월을 기준으로 구분합니다.


**힌트 1:** SUBSTR(ordered_at, 6, 2)로 월을 추출한 뒤, (월 - 1) / 3 + 1로 분기를 계산할 수 있습니다


??? success "정답"
    ```sql
    SELECT
        (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) - 1) / 3 + 1 AS quarter,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 0) AS total_revenue,
        ROUND(AVG(total_amount), 0) AS avg_amount
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) - 1) / 3 + 1
    ORDER BY quarter;
    ```


    **실행 결과** (4행)

    | quarter | order_count | total_revenue | avg_amount |
    |---|---|---|---|
    | 1 | 1412 | 1,339,538,725.00 | 948,682.00 |
    | 2 | 1336 | 1,368,754,119.00 | 1,024,517.00 |
    | 3 | 1423 | 1,394,047,576.00 | 979,654.00 |
    | 4 | 1614 | 1,520,099,342.00 | 941,821.00 |


---


### 22. 불만 카테고리(category)별로 전체 건수, 에스컬레이션(escalated = 1) 건수, 에스컬레이션 


불만 카테고리(category)별로 전체 건수, 에스컬레이션(escalated = 1) 건수, 에스컬레이션 비율(%)을 구하세요. 비율이 10% 이상인 카테고리만 조회합니다.


**힌트 1:** SUM(escalated)으로 에스컬레이션 건수를 구하고, 100.0 * SUM(escalated) / COUNT(*)로 비율을 계산하세요


??? success "정답"
    ```sql
    SELECT
        category,
        COUNT(*) AS total_count,
        SUM(escalated) AS escalated_count,
        ROUND(100.0 * SUM(escalated) / COUNT(*), 1) AS escalation_rate
    FROM complaints
    GROUP BY category
    HAVING 100.0 * SUM(escalated) / COUNT(*) >= 10
    ORDER BY escalation_rate DESC;
    ```


    **실행 결과** (3행)

    | category | total_count | escalated_count | escalation_rate |
    |---|---|---|---|
    | exchange_request | 212 | 31 | 14.60 |
    | product_defect | 460 | 56 | 12.20 |
    | refund_request | 522 | 58 | 11.10 |


---


### 23. 카드 결제(method = 'card')만 대상으로, 카드 발급사(card_issuer)별 결제 건수와 총 


카드 결제(method = 'card')만 대상으로, 카드 발급사(card_issuer)별 결제 건수와 총 금액을 조회하세요. 총 금액이 큰 순으로 정렬합니다.


**힌트 1:** WHERE method = 'card'로 카드 결제만 필터링한 후, GROUP BY card_issuer로 집계하세요


??? success "정답"
    ```sql
    SELECT
        card_issuer,
        COUNT(*) AS payment_count,
        ROUND(SUM(amount), 0) AS total_amount
    FROM payments
    WHERE method = 'card'
    GROUP BY card_issuer
    ORDER BY total_amount DESC;
    ```


    **실행 결과** (총 9행 중 상위 7행)

    | card_issuer | payment_count | total_amount |
    |---|---|---|
    | 신한카드 | 3375 | 3,413,371,940.00 |
    | KB국민카드 | 2412 | 2,636,113,617.00 |
    | 삼성카드 | 2548 | 2,495,651,059.00 |
    | 현대카드 | 1965 | 2,036,767,463.00 |
    | 롯데카드 | 1692 | 1,722,575,229.00 |
    | 하나카드 | 1712 | 1,693,454,625.00 |
    | 우리카드 | 1391 | 1,342,535,328.00 |


---


### 24. 상품별 리뷰 평균 별점을 구하고, 리뷰가 5건 이상이면서 평균 별점이 3.0 미만인 상품을 조회하세요.


상품별 리뷰 평균 별점을 구하고, 리뷰가 5건 이상이면서 평균 별점이 3.0 미만인 상품을 조회하세요.


**힌트 1:** HAVING에 조건을 2개 쓸 수 있습니다: HAVING COUNT(*) >= 5 AND AVG(rating) < 3.0


??? success "정답"
    ```sql
    SELECT
        product_id,
        COUNT(*) AS review_count,
        ROUND(AVG(rating), 2) AS avg_rating
    FROM reviews
    GROUP BY product_id
    HAVING COUNT(*) >= 5 AND AVG(rating) < 3.0
    ORDER BY avg_rating;
    ```


---


### 25. 연도와 월 조합별로 주문 건수를 조회하되, 2023년과 2024년 데이터만 대상으로 하세요. 연도, 월 순으


연도와 월 조합별로 주문 건수를 조회하되, 2023년과 2024년 데이터만 대상으로 하세요. 연도, 월 순으로 정렬합니다.


**힌트 1:** WHERE로 2023년과 2024년을 필터링하고, GROUP BY SUBSTR(ordered_at, 1, 4), SUBSTR(ordered_at, 6, 2)로 연도+월 그룹화하세요


??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        SUBSTR(ordered_at, 6, 2) AS month,
        COUNT(*) AS order_count
    FROM orders
    WHERE SUBSTR(ordered_at, 1, 4) IN ('2023', '2024')
    GROUP BY SUBSTR(ordered_at, 1, 4), SUBSTR(ordered_at, 6, 2)
    ORDER BY year, month;
    ```


    **실행 결과** (총 24행 중 상위 7행)

    | year | month | order_count |
    |---|---|---|
    | 2023 | 01 | 305 |
    | 2023 | 02 | 383 |
    | 2023 | 03 | 504 |
    | 2023 | 04 | 423 |
    | 2023 | 05 | 430 |
    | 2023 | 06 | 332 |
    | 2023 | 07 | 329 |


---


### 26. 등급(grade)과 활성 여부(is_active) 조합별로 고객 수와 평균 포인트 잔액을 조회하세요. 등급순


등급(grade)과 활성 여부(is_active) 조합별로 고객 수와 평균 포인트 잔액을 조회하세요. 등급순, 활성 여부순으로 정렬합니다.


**힌트 1:** GROUP BY grade, is_active로 두 기준을 조합하세요


??? success "정답"
    ```sql
    SELECT
        grade,
        is_active,
        COUNT(*) AS customer_count,
        ROUND(AVG(point_balance), 0) AS avg_points
    FROM customers
    GROUP BY grade, is_active
    ORDER BY grade, is_active DESC;
    ```


    **실행 결과** (5행)

    | grade | is_active | customer_count | avg_points |
    |---|---|---|---|
    | BRONZE | 1 | 2289 | 28,288.00 |
    | BRONZE | 0 | 1570 | 0.0 |
    | GOLD | 1 | 524 | 147,711.00 |
    | SILVER | 1 | 479 | 95,042.00 |
    | VIP | 1 | 368 | 407,015.00 |


---


### 27. 채널(channel)과 우선순위(priority) 조합별로 건수와 평균 응대 횟수를 조회하되, 건수 50건 


채널(channel)과 우선순위(priority) 조합별로 건수와 평균 응대 횟수를 조회하되, 건수 50건 이상이면서 평균 응대 횟수 2회 이상인 조합만 표시하세요.


**힌트 1:** HAVING에 AND로 두 조건을 결합하세요: HAVING COUNT(*) >= 50 AND AVG(response_count) >= 2


??? success "정답"
    ```sql
    SELECT
        channel,
        priority,
        COUNT(*) AS complaint_count,
        ROUND(AVG(response_count), 1) AS avg_responses
    FROM complaints
    GROUP BY channel, priority
    HAVING COUNT(*) >= 50 AND AVG(response_count) >= 2
    ORDER BY avg_responses DESC;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | channel | priority | complaint_count | avg_responses |
    |---|---|---|---|
    | chat | urgent | 59 | 2.60 |
    | email | urgent | 74 | 2.60 |
    | chat | high | 136 | 2.50 |
    | email | high | 212 | 2.40 |
    | phone | urgent | 87 | 2.40 |
    | website | high | 341 | 2.40 |
    | website | urgent | 129 | 2.40 |


---


### 28. 브랜드별 평균 마진율(%)을 구하고, 마진율이 높은 상위 5개 브랜드를 조회하세요. 마진율은 (price -


브랜드별 평균 마진율(%)을 구하고, 마진율이 높은 상위 5개 브랜드를 조회하세요. 마진율은 (price - cost_price) / price * 100으로 계산합니다. 활성 상품(is_active = 1)만 대상으로 하세요.


**힌트 1:** AVG((price - cost_price) / price * 100)으로 브랜드별 평균 마진율을 계산하세요. ORDER BY + LIMIT으로 상위 5개를 추출합니다


??? success "정답"
    ```sql
    SELECT
        brand,
        COUNT(*) AS product_count,
        ROUND(AVG((price - cost_price) / price * 100), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    ORDER BY avg_margin_pct DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | brand | product_count | avg_margin_pct |
    |---|---|---|
    | Norton | 1 | 56.70 |
    | 안랩 | 1 | 48.00 |
    | WD | 1 | 46.00 |
    | 한글과컴퓨터 | 3 | 43.40 |
    | Apple | 2 | 42.20 |


---


### 29. 카드 결제(method = 'card')를 대상으로 할부 개월 수(installment_months)별 결제


카드 결제(method = 'card')를 대상으로 할부 개월 수(installment_months)별 결제 건수와 평균 금액을 구하세요. 100건 이상인 할부 구간만 표시합니다.


**힌트 1:** WHERE method = 'card'로 필터링 후, GROUP BY installment_months + HAVING COUNT(*) >= 100을 적용하세요


??? success "정답"
    ```sql
    SELECT
        installment_months,
        COUNT(*) AS payment_count,
        ROUND(AVG(amount), 0) AS avg_amount
    FROM payments
    WHERE method = 'card'
    GROUP BY installment_months
    HAVING COUNT(*) >= 100
    ORDER BY installment_months;
    ```


    **실행 결과** (7행)

    | installment_months | payment_count | avg_amount |
    |---|---|---|
    | 0 | 8713 | 430,180.00 |
    | 2 | 965 | 395,901.00 |
    | 3 | 2084 | 1,276,668.00 |
    | 6 | 2092 | 1,810,057.00 |
    | 10 | 1419 | 2,061,261.00 |
    | 12 | 968 | 2,200,027.00 |
    | 24 | 600 | 2,288,301.00 |


---


### 30. 고객의 가입일(created_at)에서 연도를 추출하여 연도별 신규 가입자 수를 조회하세요. 가입자가 100


고객의 가입일(created_at)에서 연도를 추출하여 연도별 신규 가입자 수를 조회하세요. 가입자가 100명 이상인 연도만 표시합니다.


**힌트 1:** SUBSTR(created_at, 1, 4)로 연도를 추출하고, GROUP BY + HAVING COUNT(*) >= 100으로 필터링하세요


??? success "정답"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 4) AS year,
        COUNT(*) AS new_customers
    FROM customers
    GROUP BY SUBSTR(created_at, 1, 4)
    HAVING COUNT(*) >= 100
    ORDER BY year;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | year | new_customers |
    |---|---|
    | 2016 | 100 |
    | 2017 | 180 |
    | 2018 | 300 |
    | 2019 | 450 |
    | 2020 | 700 |
    | 2021 | 800 |
    | 2022 | 650 |


---
