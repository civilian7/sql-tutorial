# 종합 문제

!!! info "사용 테이블"

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `reviews` — 리뷰 (평점, 내용)  

    `payments` — 결제 (방법, 금액, 상태)  

    `categories` — 카테고리 (부모-자식 계층)  

    `suppliers` — 공급업체 (업체명, 연락처)  



!!! abstract "학습 범위"

    `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `Aggregate functions`, `GROUP BY`, `HAVING`, `IS NULL`, `COALESCE`, `CASE`



### 1. 판매 중인 상품(`is_active = 1`) 중 가격이 가장 비싼 상위 5개의 이름, 브랜드, 가격을 조회


판매 중인 상품(`is_active = 1`) 중 가격이 가장 비싼 상위 5개의 이름, 브랜드, 가격을 조회하세요.


**힌트 1:** `WHERE`로 필터링 + `ORDER BY DESC` + `LIMIT` 조합입니다.


??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE is_active = 1
    ORDER BY price DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | brand | price |
    |---|---|---|
    | MacBook Air 15 M3 실버 | Apple | 5,481,100.00 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | ASUS | 4,496,700.00 |
    | Razer Blade 18 블랙 | Razer | 4,353,100.00 |
    | Razer Blade 16 실버 | Razer | 3,702,900.00 |
    | ASUS ROG Strix G16CH 화이트 | ASUS | 3,671,500.00 |


---


### 2. VIP 등급 고객 중 마지막 로그인 기록이 있는 고객의 이름과 마지막 로그인일을 최근순으로 10건 조회하세요


VIP 등급 고객 중 마지막 로그인 기록이 있는 고객의 이름과 마지막 로그인일을 최근순으로 10건 조회하세요.


**힌트 1:** `WHERE grade = 'VIP' AND last_login_at IS NOT NULL`로 두 조건을 결합합니다.


??? success "정답"
    ```sql
    SELECT name, last_login_at
    FROM customers
    WHERE grade = 'VIP'
      AND last_login_at IS NOT NULL
    ORDER BY last_login_at DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | last_login_at |
    |---|---|
    | 김영희 | 2025-12-30 20:20:12 |
    | 박은서 | 2025-12-30 17:25:30 |
    | 윤준영 | 2025-12-30 17:24:28 |
    | 노수빈 | 2025-12-30 12:28:17 |
    | 성은주 | 2025-12-30 02:06:50 |
    | 김시우 | 2025-12-30 00:15:41 |
    | 성진우 | 2025-12-29 21:08:21 |


---


### 3. 2024년 취소된 주문의 주문번호, 주문 금액, 취소일을 최근 취소 순으로 10건 조회하세요.


2024년 취소된 주문의 주문번호, 주문 금액, 취소일을 최근 취소 순으로 10건 조회하세요.


**힌트 1:** `WHERE ordered_at LIKE '2024%' AND cancelled_at IS NOT NULL`로 조건을 결합합니다.


??? success "정답"
    ```sql
    SELECT order_number, total_amount, cancelled_at
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND cancelled_at IS NOT NULL
    ORDER BY cancelled_at DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | total_amount | cancelled_at |
    |---|---|---|
    | ORD-20241231-31231 | 1,905,400.00 | 2025-01-01 23:25:27 |
    | ORD-20241229-31194 | 657,900.00 | 2024-12-31 11:37:44 |
    | ORD-20241228-31179 | 68,900.00 | 2024-12-30 00:01:41 |
    | ORD-20241228-31177 | 289,100.00 | 2024-12-28 21:35:05 |
    | ORD-20241226-31148 | 69,400.00 | 2024-12-27 20:44:43 |
    | ORD-20241225-31134 | 2,841,800.00 | 2024-12-26 18:43:50 |
    | ORD-20241223-31096 | 234,768.00 | 2024-12-25 19:56:46 |


---


### 4. 평점 4점 이상인 리뷰 수와 평균 평점을 구하세요. 평균은 소수점 2자리까지 표시합니다.


평점 4점 이상인 리뷰 수와 평균 평점을 구하세요. 평균은 소수점 2자리까지 표시합니다.


**힌트 1:** `WHERE rating >= 4`로 필터링 후 `COUNT(*)`와 `ROUND(AVG(rating), 2)`를 사용합니다.


??? success "정답"
    ```sql
    SELECT COUNT(*) AS high_rating_count,
           ROUND(AVG(rating), 2) AS avg_rating
    FROM reviews
    WHERE rating >= 4;
    ```


    **실행 결과** (1행)

    | high_rating_count | avg_rating |
    |---|---|
    | 6008 | 4.57 |


---


### 5. 브랜드별 판매 중인 상품 수를 구하되, 10개 이상인 브랜드만 상품 수 내림차순으로 조회하세요.


브랜드별 판매 중인 상품 수를 구하되, 10개 이상인 브랜드만 상품 수 내림차순으로 조회하세요.


**힌트 1:** `WHERE is_active = 1` + `GROUP BY brand` + `HAVING COUNT(*) >= 10` 조합입니다.


??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY product_count DESC;
    ```


    **실행 결과** (6행)

    | brand | product_count |
    |---|---|
    | 삼성전자 | 21 |
    | ASUS | 21 |
    | MSI | 12 |
    | 로지텍 | 11 |
    | TP-Link | 11 |
    | LG전자 | 11 |


---


### 6. 고객 등급별 평균 적립금을 구하되, 등급을 한글로 표시하세요. 평균 적립금이 높은 순으로 정렬합니다.


고객 등급별 평균 적립금을 구하되, 등급을 한글로 표시하세요. 평균 적립금이 높은 순으로 정렬합니다.


**힌트 1:** `CASE`로 등급 변환 + `GROUP BY` + `AVG` + `ORDER BY` 조합입니다.


??? success "정답"
    ```sql
    SELECT CASE grade
               WHEN 'VIP' THEN 'VIP'
               WHEN 'GOLD' THEN '골드'
               WHEN 'SILVER' THEN '실버'
               WHEN 'BRONZE' THEN '브론즈'
           END AS grade_kr,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY grade
    ORDER BY avg_points DESC;
    ```


    **실행 결과** (4행)

    | grade_kr | avg_points |
    |---|---|
    | VIP | 407,015.00 |
    | 골드 | 147,711.00 |
    | 실버 | 95,042.00 |
    | 브론즈 | 16,779.00 |


---


### 7. 결제 수단별 총 결제 금액과 건수를 구하되, 총 금액이 10억 이상인 수단만 조회하세요.


결제 수단별 총 결제 금액과 건수를 구하되, 총 금액이 10억 이상인 수단만 조회하세요.


**힌트 1:** `GROUP BY method` + `HAVING SUM(amount) >= 1000000000` 조합입니다.


??? success "정답"
    ```sql
    SELECT method,
           COUNT(*) AS payment_count,
           ROUND(SUM(amount)) AS total_amount
    FROM payments
    GROUP BY method
    HAVING SUM(amount) >= 1000000000
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


### 8. 가입 경로가 NULL인 고객의 등급별 수를 구하세요. CASE로 등급 순서를 지정하여 VIP부터 표시합니다.


가입 경로가 NULL인 고객의 등급별 수를 구하세요. CASE로 등급 순서를 지정하여 VIP부터 표시합니다.


**힌트 1:** `WHERE acquisition_channel IS NULL` + `GROUP BY grade` + `ORDER BY CASE` 조합입니다.


??? success "정답"
    ```sql
    SELECT grade, COUNT(*) AS customer_count
    FROM customers
    WHERE acquisition_channel IS NULL
    GROUP BY grade
    ORDER BY CASE grade
                 WHEN 'VIP' THEN 1
                 WHEN 'GOLD' THEN 2
                 WHEN 'SILVER' THEN 3
                 WHEN 'BRONZE' THEN 4
             END;
    ```


---


### 9. 주문 상태별 건수와 평균 주문 금액을 구하되, 배송 요청사항의 입력률(%)도 함께 표시하세요. 건수가 많은 


주문 상태별 건수와 평균 주문 금액을 구하되, 배송 요청사항의 입력률(%)도 함께 표시하세요. 건수가 많은 순으로 정렬합니다.


**힌트 1:** `COUNT(notes) * 100.0 / COUNT(*)`로 입력률을 계산합니다. NULL과 집계 함수의 관계를 활용합니다.


??? success "정답"
    ```sql
    SELECT status,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(COUNT(notes) * 100.0 / COUNT(*), 1) AS notes_rate_pct
    FROM orders
    GROUP BY status
    ORDER BY order_count DESC;
    ```


    **실행 결과** (총 9행 중 상위 7행)

    | status | order_count | avg_amount | notes_rate_pct |
    |---|---|---|---|
    | confirmed | 34,393 | 999,814.00 | 35.30 |
    | cancelled | 1859 | 1,045,258.00 | 34.30 |
    | return_requested | 507 | 1,600,567.00 | 33.10 |
    | returned | 493 | 1,337,616.00 | 34.90 |
    | delivered | 125 | 1,566,146.00 | 28.80 |
    | pending | 82 | 1,063,783.00 | 37.80 |
    | shipped | 51 | 1,452,364.00 | 31.40 |


---


### 10. 상품을 재고 상태(품절/부족/보통/충분)로 분류하고, 각 그룹의 상품 수와 평균 가격을 구하세요. 판매 중인


상품을 재고 상태(품절/부족/보통/충분)로 분류하고, 각 그룹의 상품 수와 평균 가격을 구하세요. 판매 중인 상품만 대상입니다.


**힌트 1:** `WHERE is_active = 1` + `CASE`로 재고 분류 + `GROUP BY` + 집계 함수 조합입니다.


??? success "정답"
    ```sql
    SELECT CASE
               WHEN stock_qty = 0 THEN '품절'
               WHEN stock_qty <= 10 THEN '부족'
               WHEN stock_qty <= 100 THEN '보통'
               ELSE '충분'
           END AS stock_status,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price
    FROM products
    WHERE is_active = 1
    GROUP BY stock_status
    ORDER BY product_count DESC;
    ```


    **실행 결과** (4행)

    | stock_status | product_count | avg_price |
    |---|---|---|
    | 충분 | 181 | 669,318.00 |
    | 보통 | 34 | 662,359.00 |
    | 부족 | 2 | 50,900.00 |
    | 품절 | 1 | 23,000.00 |


---


### 11. 브랜드별 판매 중인 상품 수, 평균 가격, 평균 마진율(%)을 구하세요. 상품 수가 5개 이상인 브랜드만 평


브랜드별 판매 중인 상품 수, 평균 가격, 평균 마진율(%)을 구하세요. 상품 수가 5개 이상인 브랜드만 평균 마진율이 높은 순으로 조회합니다.


**힌트 1:** 마진율 = `(price - cost_price) * 100.0 / price`. `WHERE` + `GROUP BY` + `HAVING` + `ORDER BY` 조합입니다.


??? success "정답"
    ```sql
    SELECT brand,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price,
           ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 5
    ORDER BY avg_margin_pct DESC;
    ```


    **실행 결과** (총 17행 중 상위 7행)

    | brand | product_count | avg_price | avg_margin_pct |
    |---|---|---|---|
    | Microsoft | 5 | 129,260.00 | 38.20 |
    | SteelSeries | 7 | 212,643.00 | 31.60 |
    | TP-Link | 11 | 128,764.00 | 30.30 |
    | NZXT | 5 | 213,100.00 | 29.70 |
    | 로지텍 | 11 | 115,127.00 | 28.00 |
    | ASUS | 21 | 1,589,552.00 | 28.00 |
    | ASRock | 9 | 493,244.00 | 25.60 |


---


### 12. 연도별 주문 건수, 총 매출, 평균 주문 금액, 취소 건수를 구하세요. 취소 건수는 cancelled_at이


연도별 주문 건수, 총 매출, 평균 주문 금액, 취소 건수를 구하세요. 취소 건수는 cancelled_at이 NULL이 아닌 행의 수입니다.


**힌트 1:** `SUBSTR(ordered_at, 1, 4)`로 연도 추출. `COUNT(cancelled_at)`은 NULL이 아닌 행만 셉니다.


??? success "정답"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 4) AS year,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue,
           ROUND(AVG(total_amount)) AS avg_amount,
           COUNT(cancelled_at) AS cancelled_count
    FROM orders
    GROUP BY year
    ORDER BY year;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | year | order_count | total_revenue | avg_amount | cancelled_count |
    |---|---|---|---|---|
    | 2016 | 416 | 331,746,909.00 | 797,469.00 | 15 |
    | 2017 | 709 | 653,085,068.00 | 921,135.00 | 41 |
    | 2018 | 1319 | 1,249,197,907.00 | 947,080.00 | 64 |
    | 2019 | 2589 | 2,620,111,601.00 | 1,012,017.00 | 116 |
    | 2020 | 4319 | 4,468,755,264.00 | 1,034,674.00 | 191 |
    | 2021 | 5841 | 6,044,718,738.00 | 1,034,877.00 | 270 |
    | 2022 | 5203 | 5,302,071,035.00 | 1,019,041.00 | 256 |


---


### 13. 가입 경로별 고객 수, VIP 비율(%), 평균 적립금을 구하세요. 경로가 NULL이면 '미분류'로 표시하고


가입 경로별 고객 수, VIP 비율(%), 평균 적립금을 구하세요. 경로가 NULL이면 '미분류'로 표시하고, 고객 수가 많은 순으로 정렬합니다.


**힌트 1:** `COALESCE`로 NULL 대체 + `SUM(CASE WHEN grade = 'VIP' THEN 1 ELSE 0 END)`로 VIP 수 집계 + `GROUP BY` 조합입니다.


??? success "정답"
    ```sql
    SELECT COALESCE(acquisition_channel, '미분류') AS channel,
           COUNT(*) AS customer_count,
           ROUND(SUM(CASE WHEN grade = 'VIP' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS vip_rate_pct,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY COALESCE(acquisition_channel, '미분류')
    ORDER BY customer_count DESC;
    ```


    **실행 결과** (5행)

    | channel | customer_count | vip_rate_pct | avg_points |
    |---|---|---|---|
    | search_ad | 1543 | 7.50 | 62,449.00 |
    | social | 1425 | 6.20 | 54,311.00 |
    | organic | 1146 | 7.10 | 76,371.00 |
    | referral | 708 | 7.20 | 66,944.00 |
    | direct | 408 | 7.80 | 70,562.00 |


---


### 14. 2024년 월별 주문 건수와 평균 주문 금액을 구하되, 계절(봄/여름/가을/겨울)도 함께 표시하세요.


2024년 월별 주문 건수와 평균 주문 금액을 구하되, 계절(봄/여름/가을/겨울)도 함께 표시하세요.


**힌트 1:** `SUBSTR`로 월 추출 + `CASE`로 계절 분류 + `GROUP BY` + 집계 조합입니다.


??? success "정답"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 7) AS month,
           CASE
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (3, 4, 5) THEN '봄'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (6, 7, 8) THEN '여름'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (9, 10, 11) THEN '가을'
               ELSE '겨울'
           END AS season,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | month | season | order_count | avg_amount |
    |---|---|---|---|
    | 2024-01 | 겨울 | 346 | 925,700.00 |
    | 2024-02 | 겨울 | 465 | 966,554.00 |
    | 2024-03 | 봄 | 601 | 948,084.00 |
    | 2024-04 | 봄 | 506 | 980,283.00 |
    | 2024-05 | 봄 | 415 | 1,140,347.00 |
    | 2024-06 | 여름 | 415 | 962,619.00 |
    | 2024-07 | 여름 | 414 | 926,084.00 |


---


### 15. 리뷰를 평점별로 집계하되, 각 평점의 한글 라벨, 건수, 전체 대비 비율(%), 제목 입력률(%)을 함께 표


리뷰를 평점별로 집계하되, 각 평점의 한글 라벨, 건수, 전체 대비 비율(%), 제목 입력률(%)을 함께 표시하세요. 평점 높은 순으로 정렬합니다.


**힌트 1:** `CASE`로 평점 라벨 + `COUNT(*)` + 비율 계산 + `COUNT(title)` 조합입니다.


??? success "정답"
    ```sql
    SELECT rating,
           CASE rating
               WHEN 5 THEN '최고'
               WHEN 4 THEN '좋음'
               WHEN 3 THEN '보통'
               WHEN 2 THEN '별로'
               WHEN 1 THEN '최악'
           END AS rating_label,
           COUNT(*) AS review_count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct,
           ROUND(COUNT(title) * 100.0 / COUNT(*), 1) AS title_rate_pct
    FROM reviews
    GROUP BY rating
    ORDER BY rating DESC;
    ```


    **실행 결과** (5행)

    | rating | rating_label | review_count | pct | title_rate_pct |
    |---|---|---|---|---|
    | 5 | 최고 | 3433 | 40.20 | 80.80 |
    | 4 | 좋음 | 2575 | 30.10 | 80.50 |
    | 3 | 보통 | 1265 | 14.80 | 80.10 |
    | 2 | 별로 | 839 | 9.80 | 80.30 |
    | 1 | 최악 | 434 | 5.10 | 80.60 |


---


### 16. 상품의 가격대(저가/중저가/중가/고가)별로 상품 수, 평균 재고, 단종률(%)을 구하세요. 단종률은 is_a


상품의 가격대(저가/중저가/중가/고가)별로 상품 수, 평균 재고, 단종률(%)을 구하세요. 단종률은 is_active=0인 비율입니다.


**힌트 1:** `CASE`로 가격대 분류 + `SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END)`로 단종 수 집계 + `GROUP BY` 조합입니다.


??? success "정답"
    ```sql
    SELECT CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier,
           COUNT(*) AS product_count,
           ROUND(AVG(stock_qty)) AS avg_stock,
           ROUND(SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS discontinued_pct
    FROM products
    GROUP BY price_tier
    ORDER BY product_count DESC;
    ```


    **실행 결과** (4행)

    | price_tier | product_count | avg_stock | discontinued_pct |
    |---|---|---|---|
    | 중저가 | 130 | 277.00 | 23.80 |
    | 고가 | 65 | 271.00 | 20.00 |
    | 저가 | 47 | 267.00 | 19.10 |
    | 중가 | 38 | 282.00 | 23.70 |


---


### 17. 등급별 고객 수, 평균 적립금, 성별 입력률(%), 로그인 경험률(%)을 한 번에 조회하세요. 등급 순서는 


등급별 고객 수, 평균 적립금, 성별 입력률(%), 로그인 경험률(%)을 한 번에 조회하세요. 등급 순서는 VIP > GOLD > SILVER > BRONZE입니다.


**힌트 1:** `COUNT(gender)`로 성별 입력 수, `COUNT(last_login_at)`으로 로그인 경험 수를 구합니다. `ORDER BY CASE`로 등급 순서를 지정합니다.


??? success "정답"
    ```sql
    SELECT grade,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points,
           ROUND(COUNT(gender) * 100.0 / COUNT(*), 1) AS gender_rate_pct,
           ROUND(COUNT(last_login_at) * 100.0 / COUNT(*), 1) AS login_rate_pct
    FROM customers
    GROUP BY grade
    ORDER BY CASE grade
                 WHEN 'VIP' THEN 1
                 WHEN 'GOLD' THEN 2
                 WHEN 'SILVER' THEN 3
                 WHEN 'BRONZE' THEN 4
             END;
    ```


    **실행 결과** (4행)

    | grade | customer_count | avg_points | gender_rate_pct | login_rate_pct |
    |---|---|---|---|---|
    | VIP | 368 | 407,015.00 | 96.20 | 100.00 |
    | GOLD | 524 | 147,711.00 | 92.20 | 100.00 |
    | SILVER | 479 | 95,042.00 | 90.60 | 100.00 |
    | BRONZE | 3859 | 16,779.00 | 88.90 | 92.70 |


---


### 18. 주문 상태를 3그룹(처리중/완료/취소반품)으로 분류하고, 각 그룹의 건수, 총 매출, 평균 배송비, 포인트 


주문 상태를 3그룹(처리중/완료/취소반품)으로 분류하고, 각 그룹의 건수, 총 매출, 평균 배송비, 포인트 사용 건수를 구하세요.


**힌트 1:** `CASE WHEN status IN (...)`로 그룹 분류. `SUM(CASE WHEN point_used > 0 THEN 1 ELSE 0 END)`로 포인트 사용 건수를 셉니다.


??? success "정답"
    ```sql
    SELECT CASE
               WHEN status IN ('pending', 'paid', 'preparing') THEN '처리중'
               WHEN status IN ('shipped', 'delivered', 'confirmed') THEN '완료'
               ELSE '취소/반품'
           END AS status_group,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue,
           ROUND(AVG(shipping_fee)) AS avg_shipping,
           SUM(CASE WHEN point_used > 0 THEN 1 ELSE 0 END) AS point_used_count
    FROM orders
    GROUP BY status_group
    ORDER BY order_count DESC;
    ```


    **실행 결과** (3행)

    | status_group | order_count | total_revenue | avg_shipping | point_used_count |
    |---|---|---|---|---|
    | 완료 | 34,569 | 34,656,428,960.00 | 248.00 | 3439 |
    | 취소/반품 | 2859 | 3,414,067,056.00 | 208.00 | 291 |
    | 처리중 | 129 | 112,999,047.00 | 163.00 | 10 |


---


### 19. 카드 결제 중 카드사별 결제 건수, 평균 금액, 할부 이용률(%)을 구하세요. 카드사 정보가 NULL인 건은


카드 결제 중 카드사별 결제 건수, 평균 금액, 할부 이용률(%)을 구하세요. 카드사 정보가 NULL인 건은 제외하고, 건수가 100 이상인 카드사만 조회합니다.


**힌트 1:** `WHERE method = 'card' AND card_issuer IS NOT NULL`로 필터. `SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END)`로 할부 건수를 셉니다.


??? success "정답"
    ```sql
    SELECT card_issuer,
           COUNT(*) AS payment_count,
           ROUND(AVG(amount)) AS avg_amount,
           ROUND(SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS installment_rate_pct
    FROM payments
    WHERE method = 'card'
      AND card_issuer IS NOT NULL
    GROUP BY card_issuer
    HAVING COUNT(*) >= 100
    ORDER BY payment_count DESC;
    ```


    **실행 결과** (총 9행 중 상위 7행)

    | card_issuer | payment_count | avg_amount | installment_rate_pct |
    |---|---|---|---|
    | 신한카드 | 3375 | 1,011,369.00 | 48.80 |
    | 삼성카드 | 2548 | 979,455.00 | 47.80 |
    | KB국민카드 | 2412 | 1,092,916.00 | 47.50 |
    | 현대카드 | 1965 | 1,036,523.00 | 48.20 |
    | 하나카드 | 1712 | 989,167.00 | 49.80 |
    | 롯데카드 | 1692 | 1,018,070.00 | 48.70 |
    | 우리카드 | 1391 | 965,158.00 | 47.90 |


---


### 20. 공급업체별 상품 수와 활성 상품 비율(%)을 구하세요. 상품 수가 3개 이상인 공급업체만 대상이며, 활성 비


공급업체별 상품 수와 활성 상품 비율(%)을 구하세요. 상품 수가 3개 이상인 공급업체만 대상이며, 활성 비율이 높은 순으로 정렬합니다. 공급업체는 supplier_id로 그룹화합니다.


**힌트 1:** `GROUP BY supplier_id` + `HAVING COUNT(*) >= 3` + `SUM(CASE WHEN is_active = 1 ...)`로 활성 비율 계산 + `ORDER BY` 조합입니다.


??? success "정답"
    ```sql
    SELECT supplier_id,
           COUNT(*) AS product_count,
           SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_count,
           ROUND(SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS active_rate_pct
    FROM products
    GROUP BY supplier_id
    HAVING COUNT(*) >= 3
    ORDER BY active_rate_pct DESC;
    ```


    **실행 결과** (총 32행 중 상위 7행)

    | supplier_id | product_count | active_count | active_rate_pct |
    |---|---|---|---|
    | 2 | 11 | 11 | 100.00 |
    | 17 | 6 | 6 | 100.00 |
    | 22 | 3 | 3 | 100.00 |
    | 24 | 5 | 5 | 100.00 |
    | 36 | 11 | 11 | 100.00 |
    | 37 | 5 | 5 | 100.00 |
    | 27 | 13 | 12 | 92.30 |


---


### 21. 브랜드별 활성 상품 수와 평균 가격을 구하되, 평균 가격 100만원 이상인 브랜드만 조회하세요. 가격대 분류


브랜드별 활성 상품 수와 평균 가격을 구하되, 평균 가격 100만원 이상인 브랜드만 조회하세요. 가격대 분류(프리미엄/대중/보급형)도 함께 표시합니다.


**힌트 1:** `WHERE is_active = 1` + `GROUP BY brand` + `HAVING AVG(price) >= 1000000` + `CASE`로 가격대 분류 조합입니다.


??? success "정답"
    ```sql
    SELECT brand,
           COUNT(*) AS active_product_count,
           ROUND(AVG(price)) AS avg_price,
           CASE
               WHEN AVG(price) >= 2000000 THEN '프리미엄'
               WHEN AVG(price) >= 1000000 THEN '대중'
               ELSE '보급형'
           END AS brand_tier
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING AVG(price) >= 1000000
    ORDER BY avg_price DESC;
    ```


    **실행 결과** (총 8행 중 상위 7행)

    | brand | active_product_count | avg_price | brand_tier |
    |---|---|---|---|
    | Apple | 2 | 2,815,400.00 | 프리미엄 |
    | Razer | 7 | 1,996,443.00 | 대중 |
    | 레노버 | 2 | 1,695,450.00 | 대중 |
    | 주연테크 | 3 | 1,614,633.00 | 대중 |
    | ASUS | 21 | 1,589,552.00 | 대중 |
    | BenQ | 1 | 1,476,300.00 | 대중 |
    | HP | 5 | 1,433,140.00 | 대중 |


---


### 22. 2024년 월별 매출 분석: 월별 주문 건수, 총 매출, 평균 주문 금액, 취소율(%), 무료배송 비율(%)


2024년 월별 매출 분석: 월별 주문 건수, 총 매출, 평균 주문 금액, 취소율(%), 무료배송 비율(%)을 구하세요.


**힌트 1:** 다양한 집계를 조합합니다. 취소율 = `COUNT(cancelled_at) / COUNT(*)`. 무료배송 = `shipping_fee = 0`인 건의 비율입니다.


??? success "정답"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 7) AS month,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(COUNT(cancelled_at) * 100.0 / COUNT(*), 1) AS cancel_rate_pct,
           ROUND(SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS free_ship_pct
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | month | order_count | total_revenue | avg_amount | cancel_rate_pct | free_ship_pct |
    |---|---|---|---|---|---|
    | 2024-01 | 346 | 320,292,182.00 | 925,700.00 | 6.10 | 91.30 |
    | 2024-02 | 465 | 449,447,834.00 | 966,554.00 | 6.90 | 92.30 |
    | 2024-03 | 601 | 569,798,709.00 | 948,084.00 | 4.80 | 93.30 |
    | 2024-04 | 506 | 496,023,258.00 | 980,283.00 | 5.50 | 94.50 |
    | 2024-05 | 415 | 473,243,857.00 | 1,140,347.00 | 4.60 | 94.00 |
    | 2024-06 | 415 | 399,487,004.00 | 962,619.00 | 4.30 | 93.70 |
    | 2024-07 | 414 | 383,398,728.00 | 926,084.00 | 5.60 | 93.50 |


---


### 23. 고객 세그먼트 분석: 등급과 활동 상태(활동/휴면/탈퇴)를 조합하여 세그먼트별 고객 수와 평균 적립금을 구하


고객 세그먼트 분석: 등급과 활동 상태(활동/휴면/탈퇴)를 조합하여 세그먼트별 고객 수와 평균 적립금을 구하세요. 고객 수 100명 이상인 세그먼트만 조회합니다.


**힌트 1:** `CASE`로 활동 상태(is_active=0이면 탈퇴, last_login_at IS NULL이면 휴면, 그 외 활동) 분류. `GROUP BY grade, activity_status` 조합입니다.


??? success "정답"
    ```sql
    SELECT grade,
           CASE
               WHEN is_active = 0 THEN '탈퇴'
               WHEN last_login_at IS NULL THEN '휴면'
               ELSE '활동'
           END AS activity_status,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY grade, activity_status
    HAVING COUNT(*) >= 100
    ORDER BY CASE grade
                 WHEN 'VIP' THEN 1
                 WHEN 'GOLD' THEN 2
                 WHEN 'SILVER' THEN 3
                 WHEN 'BRONZE' THEN 4
             END,
             customer_count DESC;
    ```


    **실행 결과** (6행)

    | grade | activity_status | customer_count | avg_points |
    |---|---|---|---|
    | VIP | 활동 | 368 | 407,015.00 |
    | GOLD | 활동 | 524 | 147,711.00 |
    | SILVER | 활동 | 479 | 95,042.00 |
    | BRONZE | 활동 | 2100 | 30,834.00 |
    | BRONZE | 탈퇴 | 1570 | 0.0 |
    | BRONZE | 휴면 | 189 | 0.0 |


---


### 24. 상품 데이터 품질 리포트: 브랜드별로 상품 수, 설명 누락률(%), 사양 누락률(%), 무게 누락률(%)을 


상품 데이터 품질 리포트: 브랜드별로 상품 수, 설명 누락률(%), 사양 누락률(%), 무게 누락률(%)을 구하세요. 상품 수 10개 이상인 브랜드만 대상이며, 전체 누락률(3개 평균)이 높은 순으로 정렬합니다.


**힌트 1:** `(COUNT(*) - COUNT(칼럼)) * 100.0 / COUNT(*)`로 각 칼럼의 누락률을 구합니다. 3개의 누락률 평균으로 정렬합니다.


??? success "정답"
    ```sql
    SELECT brand,
           COUNT(*) AS product_count,
           ROUND((COUNT(*) - COUNT(description)) * 100.0 / COUNT(*), 1) AS desc_missing_pct,
           ROUND((COUNT(*) - COUNT(specs)) * 100.0 / COUNT(*), 1) AS specs_missing_pct,
           ROUND((COUNT(*) - COUNT(weight_grams)) * 100.0 / COUNT(*), 1) AS weight_missing_pct
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY (
        (COUNT(*) - COUNT(description)) +
        (COUNT(*) - COUNT(specs)) +
        (COUNT(*) - COUNT(weight_grams))
    ) * 1.0 / COUNT(*) DESC;
    ```


    **실행 결과** (7행)

    | brand | product_count | desc_missing_pct | specs_missing_pct | weight_missing_pct |
    |---|---|---|---|---|
    | 로지텍 | 17 | 0.0 | 100.00 | 0.0 |
    | TP-Link | 11 | 0.0 | 100.00 | 0.0 |
    | ASRock | 11 | 0.0 | 100.00 | 0.0 |
    | MSI | 13 | 0.0 | 61.50 | 0.0 |
    | ASUS | 26 | 0.0 | 30.80 | 0.0 |
    | 삼성전자 | 25 | 0.0 | 24.00 | 0.0 |
    | LG전자 | 11 | 0.0 | 0.0 | 0.0 |


---


### 25. 연도별 고객 가입 분석: 가입 연도별 고객 수, 성별 비율(남/여/미입력), 평균 적립금을 구하세요.


연도별 고객 가입 분석: 가입 연도별 고객 수, 성별 비율(남/여/미입력), 평균 적립금을 구하세요.


**힌트 1:** `SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)`로 남성 비율을 구합니다. 성별 NULL도 별도 비율로 계산합니다.


??? success "정답"
    ```sql
    SELECT SUBSTR(created_at, 1, 4) AS join_year,
           COUNT(*) AS customer_count,
           ROUND(SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS male_pct,
           ROUND(SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS female_pct,
           ROUND(SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS unknown_pct,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY join_year
    ORDER BY join_year;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | join_year | customer_count | male_pct | female_pct | unknown_pct | avg_points |
    |---|---|---|---|---|---|
    | 2016 | 100 | 53.00 | 29.00 | 18.00 | 212,578.00 |
    | 2017 | 180 | 57.20 | 32.20 | 10.60 | 170,364.00 |
    | 2018 | 300 | 56.30 | 32.00 | 11.70 | 144,012.00 |
    | 2019 | 450 | 56.90 | 32.70 | 10.40 | 99,968.00 |
    | 2020 | 700 | 61.60 | 28.70 | 9.70 | 94,152.00 |
    | 2021 | 800 | 56.30 | 33.00 | 10.80 | 69,793.00 |
    | 2022 | 650 | 60.60 | 30.30 | 9.10 | 53,009.00 |


---


### 26. 할인 분석: 2024년 주문에서 할인 적용 여부(할인있음/할인없음)와 금액 구간(소액/일반/고액/VIP급)을


할인 분석: 2024년 주문에서 할인 적용 여부(할인있음/할인없음)와 금액 구간(소액/일반/고액/VIP급)을 조합하여 건수와 평균 주문 금액을 구하세요.


**힌트 1:** `CASE WHEN discount_amount > 0`로 할인 여부, `CASE WHEN total_amount < 50000`으로 금액 구간을 분류합니다. `GROUP BY`에 두 CASE를 모두 사용합니다.


??? success "정답"
    ```sql
    SELECT CASE WHEN discount_amount > 0 THEN '할인있음' ELSE '할인없음' END AS has_discount,
           CASE
               WHEN total_amount < 50000 THEN '소액'
               WHEN total_amount < 200000 THEN '일반'
               WHEN total_amount < 1000000 THEN '고액'
               ELSE 'VIP급'
           END AS amount_tier,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY has_discount, amount_tier
    ORDER BY has_discount, avg_amount DESC;
    ```


    **실행 결과** (총 8행 중 상위 7행)

    | has_discount | amount_tier | order_count | avg_amount |
    |---|---|---|---|
    | 할인없음 | VIP급 | 1314 | 2,190,896.00 |
    | 할인없음 | 고액 | 1498 | 447,381.00 |
    | 할인없음 | 일반 | 1435 | 121,632.00 |
    | 할인없음 | 소액 | 276 | 36,244.00 |
    | 할인있음 | VIP급 | 652 | 2,567,481.00 |
    | 할인있음 | 고액 | 398 | 481,555.00 |
    | 할인있음 | 일반 | 173 | 125,703.00 |


---


### 27. 카테고리별 상품 현황: category_id별 전체 상품 수, 판매중 수, 단종 수, 품절 수, 평균 가격을


카테고리별 상품 현황: category_id별 전체 상품 수, 판매중 수, 단종 수, 품절 수, 평균 가격을 구하세요. 전체 상품 수가 5개 이상인 카테고리만 대상입니다.


**힌트 1:** `SUM(CASE WHEN 조건 THEN 1 ELSE 0 END)`로 각 상태의 수를 별도 칼럼으로 집계합니다.


??? success "정답"
    ```sql
    SELECT category_id,
           COUNT(*) AS total,
           SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_count,
           SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS discontinued_count,
           SUM(CASE WHEN stock_qty = 0 THEN 1 ELSE 0 END) AS out_of_stock,
           ROUND(AVG(price)) AS avg_price
    FROM products
    GROUP BY category_id
    HAVING COUNT(*) >= 5
    ORDER BY total DESC;
    ```


    **실행 결과** (총 31행 중 상위 7행)

    | category_id | total | active_count | discontinued_count | out_of_stock | avg_price |
    |---|---|---|---|---|---|
    | 18 | 13 | 10 | 3 | 0 | 529,754.00 |
    | 30 | 13 | 11 | 2 | 0 | 219,008.00 |
    | 43 | 12 | 9 | 3 | 0 | 277,150.00 |
    | 3 | 11 | 9 | 2 | 0 | 1,719,809.00 |
    | 31 | 11 | 10 | 1 | 0 | 158,482.00 |
    | 36 | 11 | 8 | 3 | 0 | 158,000.00 |
    | 37 | 11 | 7 | 4 | 0 | 41,064.00 |


---


### 28. 결제 수단 종합 분석: 수단별(한글 표시) 건수, 총 금액, 평균 금액, 환불 건수, 환불률(%)을 구하세요


결제 수단 종합 분석: 수단별(한글 표시) 건수, 총 금액, 평균 금액, 환불 건수, 환불률(%)을 구하세요. 건수가 1,000건 이상인 수단만 대상입니다.


**힌트 1:** `CASE`로 수단 한글화 + `COUNT(refunded_at)`으로 환불 건수 + `HAVING` + `ORDER BY` 조합입니다.


??? success "정답"
    ```sql
    SELECT CASE method
               WHEN 'card' THEN '신용카드'
               WHEN 'bank_transfer' THEN '계좌이체'
               WHEN 'virtual_account' THEN '가상계좌'
               WHEN 'kakao_pay' THEN '카카오페이'
               WHEN 'naver_pay' THEN '네이버페이'
               WHEN 'point' THEN '포인트'
           END AS method_kr,
           COUNT(*) AS payment_count,
           ROUND(SUM(amount)) AS total_amount,
           ROUND(AVG(amount)) AS avg_amount,
           COUNT(refunded_at) AS refund_count,
           ROUND(COUNT(refunded_at) * 100.0 / COUNT(*), 1) AS refund_rate_pct
    FROM payments
    GROUP BY method
    HAVING COUNT(*) >= 1000
    ORDER BY total_amount DESC;
    ```


    **실행 결과** (6행)

    | method_kr | payment_count | total_amount | avg_amount | refund_count | refund_rate_pct |
    |---|---|---|---|---|---|
    | 신용카드 | 16,841 | 17,004,951,634.00 | 1,009,735.00 | 872 | 5.20 |
    | 카카오페이 | 7486 | 7,563,829,668.00 | 1,010,397.00 | 380 | 5.10 |
    | 네이버페이 | 5715 | 5,998,835,720.00 | 1,049,665.00 | 285 | 5.00 |
    | 계좌이체 | 3718 | 3,753,149,013.00 | 1,009,454.00 | 178 | 4.80 |
    | 포인트 | 1921 | 1,951,369,604.00 | 1,015,809.00 | 98 | 5.10 |
    | 가상계좌 | 1876 | 1,911,359,424.00 | 1,018,848.00 | 117 | 6.20 |


---


### 29. 고객 프로필 완성도 분석: 완성도 점수(0~4점)별 고객 수, 비율(%), 평균 적립금, VIP 비율(%)을


고객 프로필 완성도 분석: 완성도 점수(0~4점)별 고객 수, 비율(%), 평균 적립금, VIP 비율(%)을 구하세요. 완성도 = birth_date, gender, last_login_at, acquisition_channel 중 NULL이 아닌 수.


**힌트 1:** `(칼럼 IS NOT NULL)`은 SQLite에서 1 또는 0을 반환합니다. 4개를 더해 완성도 점수를 구합니다.


??? success "정답"
    ```sql
    SELECT (birth_date IS NOT NULL)
         + (gender IS NOT NULL)
         + (last_login_at IS NOT NULL)
         + (acquisition_channel IS NOT NULL) AS completeness,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points,
           ROUND(SUM(CASE WHEN grade = 'VIP' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS vip_rate_pct
    FROM customers
    GROUP BY completeness
    ORDER BY completeness;
    ```


    **실행 결과** (4행)

    | completeness | customer_count | avg_points | vip_rate_pct |
    |---|---|---|---|
    | 1 | 5 | 0.0 | 0.0 |
    | 2 | 143 | 20,877.00 | 0.7 |
    | 3 | 1247 | 45,918.00 | 4.30 |
    | 4 | 3835 | 72,285.00 | 8.20 |


---


### 30. 종합 대시보드: 상품 테이블에서 브랜드별 활성 상품 수, 평균 가격, 평균 마진율(%), 가격대 분류, 재고


종합 대시보드: 상품 테이블에서 브랜드별 활성 상품 수, 평균 가격, 평균 마진율(%), 가격대 분류, 재고 부족 상품 수(stock_qty <= 10)를 구하세요. 활성 상품 5개 이상인 브랜드만 대상이며, 활성 상품 수 내림차순으로 상위 10개만 조회합니다.


**힌트 1:** 여러 집계와 CASE를 동시에 사용합니다. `WHERE is_active = 1` + `GROUP BY brand` + `HAVING` + `ORDER BY` + `LIMIT` 조합입니다.


??? success "정답"
    ```sql
    SELECT brand,
           COUNT(*) AS active_count,
           ROUND(AVG(price)) AS avg_price,
           ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct,
           CASE
               WHEN AVG(price) >= 1000000 THEN '프리미엄'
               WHEN AVG(price) >= 300000 THEN '대중'
               ELSE '보급형'
           END AS brand_tier,
           SUM(CASE WHEN stock_qty <= 10 THEN 1 ELSE 0 END) AS low_stock_count
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 5
    ORDER BY active_count DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | brand | active_count | avg_price | avg_margin_pct | brand_tier | low_stock_count |
    |---|---|---|---|---|---|
    | 삼성전자 | 21 | 641,800.00 | 18.50 | 대중 | 1 |
    | ASUS | 21 | 1,589,552.00 | 28.00 | 프리미엄 | 0 |
    | MSI | 12 | 820,292.00 | 16.80 | 대중 | 0 |
    | 로지텍 | 11 | 115,127.00 | 28.00 | 보급형 | 1 |
    | TP-Link | 11 | 128,764.00 | 30.30 | 보급형 | 0 |
    | LG전자 | 11 | 1,346,836.00 | 21.20 | 프리미엄 | 0 |
    | ASRock | 9 | 493,244.00 | 25.60 | 대중 | 0 |


---
