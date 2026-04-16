# 집계 함수

!!! info "사용 테이블"

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `reviews` — 리뷰 (평점, 내용)  

    `payments` — 결제 (방법, 금액, 상태)  



!!! abstract "학습 범위"

    `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `ROUND`, `COUNT DISTINCT`



### 1. 상품 테이블에 등록된 전체 상품 수를 조회하세요.


상품 테이블에 등록된 전체 상품 수를 조회하세요.


**힌트 1:** COUNT(*)는 테이블의 전체 행 수를 셉니다


??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_products
    FROM products;
    ```


    **실행 결과** (1행)

    | total_products |
    |---|
    | 280 |


---


### 2. 판매 중인(`is_active = 1`) 상품 수를 조회하세요.


판매 중인(`is_active = 1`) 상품 수를 조회하세요.


**힌트 1:** WHERE로 조건을 걸고 COUNT(*)로 세면 조건에 맞는 행만 집계됩니다


??? success "정답"
    ```sql
    SELECT COUNT(*) AS active_count
    FROM products
    WHERE is_active = 1;
    ```


    **실행 결과** (1행)

    | active_count |
    |---|
    | 218 |


---


### 3. 단종일(`discontinued_at`)이 기록된 상품은 몇 개인지 조회하세요.


단종일(`discontinued_at`)이 기록된 상품은 몇 개인지 조회하세요.


**힌트 1:** COUNT(칼럼명)은 해당 칼럼이 NULL이 아닌 행만 셉니다. COUNT(*)와의 차이를 기억하세요


??? success "정답"
    ```sql
    SELECT COUNT(discontinued_at) AS discontinued_count
    FROM products;
    ```


    **실행 결과** (1행)

    | discontinued_count |
    |---|
    | 62 |


---


### 4. 전체 상품의 재고 수량 합계를 구하세요.


전체 상품의 재고 수량 합계를 구하세요.


**힌트 1:** SUM(칼럼명)은 해당 칼럼의 모든 값을 더합니다


??? success "정답"
    ```sql
    SELECT SUM(stock_qty) AS total_stock
    FROM products;
    ```


    **실행 결과** (1행)

    | total_stock |
    |---|
    | 76,887 |


---


### 5. 전체 상품의 평균 가격을 조회하세요.


전체 상품의 평균 가격을 조회하세요.


**힌트 1:** AVG(칼럼명)은 해당 칼럼의 평균을 계산합니다


??? success "정답"
    ```sql
    SELECT AVG(price) AS avg_price
    FROM products;
    ```


    **실행 결과** (1행)

    | avg_price |
    |---|
    | 649,272.50 |


---


### 6. 가장 비싼 상품의 가격을 조회하세요.


가장 비싼 상품의 가격을 조회하세요.


**힌트 1:** MAX(칼럼명)은 해당 칼럼의 최댓값을 반환합니다


??? success "정답"
    ```sql
    SELECT MAX(price) AS max_price
    FROM products;
    ```


    **실행 결과** (1행)

    | max_price |
    |---|
    | 5,481,100.00 |


---


### 7. 가장 저렴한 상품의 가격을 조회하세요.


가장 저렴한 상품의 가격을 조회하세요.


**힌트 1:** MIN(칼럼명)은 해당 칼럼의 최솟값을 반환합니다


??? success "정답"
    ```sql
    SELECT MIN(price) AS min_price
    FROM products;
    ```


    **실행 결과** (1행)

    | min_price |
    |---|
    | 18,500.00 |


---


### 8. 전체 주문의 총 매출(`total_amount` 합계)을 구하세요.


전체 주문의 총 매출(`total_amount` 합계)을 구하세요.


**힌트 1:** orders 테이블의 total_amount 칼럼에 SUM을 적용합니다


??? success "정답"
    ```sql
    SELECT SUM(total_amount) AS total_revenue
    FROM orders;
    ```


    **실행 결과** (1행)

    | total_revenue |
    |---|
    | 38,183,495,063.00 |


---


### 9. 리뷰의 평균 평점을 조회하세요.


리뷰의 평균 평점을 조회하세요.


**힌트 1:** reviews 테이블의 rating 칼럼에 AVG를 적용합니다


??? success "정답"
    ```sql
    SELECT AVG(rating) AS avg_rating
    FROM reviews;
    ```


    **실행 결과** (1행)

    | avg_rating |
    |---|
    | 3.90 |


---


### 10. 고객 중 가장 많은 적립금을 보유한 금액을 조회하세요.


고객 중 가장 많은 적립금을 보유한 금액을 조회하세요.


**힌트 1:** customers 테이블의 point_balance에 MAX를 적용합니다


??? success "정답"
    ```sql
    SELECT MAX(point_balance) AS max_points
    FROM customers;
    ```


    **실행 결과** (1행)

    | max_points |
    |---|
    | 3,955,828 |


---


### 11. 판매 중인 상품의 평균 가격을 소수점 둘째 자리까지 반올림하여 조회하세요.


판매 중인 상품의 평균 가격을 소수점 둘째 자리까지 반올림하여 조회하세요.


**힌트 1:** ROUND(값, 자릿수)로 소수점 자릿수를 지정합니다. ROUND(AVG(price), 2)처럼 집계 함수를 감쌀 수 있습니다


??? success "정답"
    ```sql
    SELECT ROUND(AVG(price), 2) AS avg_price
    FROM products
    WHERE is_active = 1;
    ```


    **실행 결과** (1행)

    | avg_price |
    |---|
    | 659,594.50 |


---


### 12. 상품 테이블에 등록된 브랜드가 몇 종류인지 조회하세요.


상품 테이블에 등록된 브랜드가 몇 종류인지 조회하세요.


**힌트 1:** COUNT(DISTINCT 칼럼명)은 중복을 제거한 고유값의 개수를 셉니다


??? success "정답"
    ```sql
    SELECT COUNT(DISTINCT brand) AS brand_count
    FROM products;
    ```


    **실행 결과** (1행)

    | brand_count |
    |---|
    | 55 |


---


### 13. 주문을 한 적 있는 고객이 몇 명인지 조회하세요.


주문을 한 적 있는 고객이 몇 명인지 조회하세요.


**힌트 1:** orders 테이블의 customer_id에 COUNT(DISTINCT ...)를 적용하면 주문한 고유 고객 수를 알 수 있습니다


??? success "정답"
    ```sql
    SELECT COUNT(DISTINCT customer_id) AS ordering_customers
    FROM orders;
    ```


    **실행 결과** (1행)

    | ordering_customers |
    |---|
    | 2839 |


---


### 14. 상품의 최저가, 최고가, 평균가(소수점 없이)를 한 번에 조회하세요.


상품의 최저가, 최고가, 평균가(소수점 없이)를 한 번에 조회하세요.


**힌트 1:** 하나의 SELECT에 여러 집계 함수를 쉼표로 구분하여 나열할 수 있습니다


??? success "정답"
    ```sql
    SELECT MIN(price) AS min_price,
           MAX(price) AS max_price,
           ROUND(AVG(price), 0) AS avg_price
    FROM products;
    ```


    **실행 결과** (1행)

    | min_price | max_price | avg_price |
    |---|---|---|
    | 18,500.00 | 5,481,100.00 | 649,273.00 |


---


### 15. 별점 5점 리뷰는 몇 건인지 조회하세요.


별점 5점 리뷰는 몇 건인지 조회하세요.


**힌트 1:** WHERE rating = 5로 필터링한 후 COUNT(*)를 사용합니다


??? success "정답"
    ```sql
    SELECT COUNT(*) AS five_star_count
    FROM reviews
    WHERE rating = 5;
    ```


    **실행 결과** (1행)

    | five_star_count |
    |---|
    | 3433 |


---


### 16. 리뷰의 평균 평점을 소수점 첫째 자리까지, 최저 평점, 최고 평점을 한 번에 조회하세요.


리뷰의 평균 평점을 소수점 첫째 자리까지, 최저 평점, 최고 평점을 한 번에 조회하세요.


**힌트 1:** ROUND(AVG(...), 1), MIN(...), MAX(...)를 하나의 SELECT에 나열합니다


??? success "정답"
    ```sql
    SELECT ROUND(AVG(rating), 1) AS avg_rating,
           MIN(rating) AS min_rating,
           MAX(rating) AS max_rating
    FROM reviews;
    ```


    **실행 결과** (1행)

    | avg_rating | min_rating | max_rating |
    |---|---|---|
    | 3.90 | 1 | 5 |


---


### 17. 카드(`card`)로 결제한 건수를 조회하세요.


카드(`card`)로 결제한 건수를 조회하세요.


**힌트 1:** payments 테이블에서 method = 'card'로 필터링합니다


??? success "정답"
    ```sql
    SELECT COUNT(*) AS card_count
    FROM payments
    WHERE method = 'card';
    ```


    **실행 결과** (1행)

    | card_count |
    |---|
    | 16,841 |


---


### 18. 결제 수단이 몇 종류인지 조회하세요.


결제 수단이 몇 종류인지 조회하세요.


**힌트 1:** payments 테이블의 method 칼럼에 COUNT(DISTINCT ...)를 적용합니다


??? success "정답"
    ```sql
    SELECT COUNT(DISTINCT method) AS method_count
    FROM payments;
    ```


    **실행 결과** (1행)

    | method_count |
    |---|
    | 6 |


---


### 19. 가장 오래된 주문일과 가장 최근 주문일을 조회하세요.


가장 오래된 주문일과 가장 최근 주문일을 조회하세요.


**힌트 1:** 날짜/시간 문자열에도 MIN과 MAX를 사용할 수 있습니다


??? success "정답"
    ```sql
    SELECT MIN(ordered_at) AS first_order,
           MAX(ordered_at) AS last_order
    FROM orders;
    ```


    **실행 결과** (1행)

    | first_order | last_order |
    |---|---|
    | 2016-01-09 10:20:06 | 2025-12-31 22:25:39 |


---


### 20. 전체 주문에서 할인이 적용된 주문(`discount_amount > 0`)은 몇 건인지 조회하세요.


전체 주문에서 할인이 적용된 주문(`discount_amount > 0`)은 몇 건인지 조회하세요.


**힌트 1:** WHERE discount_amount > 0으로 필터링한 후 COUNT(*)를 사용합니다


??? success "정답"
    ```sql
    SELECT COUNT(*) AS discounted_orders
    FROM orders
    WHERE discount_amount > 0;
    ```


    **실행 결과** (1행)

    | discounted_orders |
    |---|
    | 7917 |


---


### 21. 확정(`confirmed`) 상태 주문의 건수, 총 매출, 평균 주문 금액을 조회하세요. 금액은 소수점 없이


확정(`confirmed`) 상태 주문의 건수, 총 매출, 평균 주문 금액을 조회하세요. 금액은 소수점 없이 반올림합니다.


**힌트 1:** WHERE status = 'confirmed'로 필터링한 후 COUNT, SUM, AVG를 한 번에 사용합니다


??? success "정답"
    ```sql
    SELECT COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 0) AS total_revenue,
           ROUND(AVG(total_amount), 0) AS avg_amount
    FROM orders
    WHERE status = 'confirmed';
    ```


    **실행 결과** (1행)

    | order_count | total_revenue | avg_amount |
    |---|---|---|
    | 34,393 | 34,386,590,179.00 | 999,814.00 |


---


### 22. 리뷰를 작성한 고객이 몇 명인지, 리뷰가 달린 상품이 몇 종류인지 한 번에 조회하세요.


리뷰를 작성한 고객이 몇 명인지, 리뷰가 달린 상품이 몇 종류인지 한 번에 조회하세요.


**힌트 1:** 하나의 SELECT에서 COUNT(DISTINCT customer_id)와 COUNT(DISTINCT product_id)를 함께 사용합니다


??? success "정답"
    ```sql
    SELECT COUNT(DISTINCT customer_id) AS reviewer_count,
           COUNT(DISTINCT product_id) AS reviewed_product_count
    FROM reviews;
    ```


    **실행 결과** (1행)

    | reviewer_count | reviewed_product_count |
    |---|---|
    | 1899 | 278 |


---


### 23. 고객의 적립금 합계와 평균(소수점 없이)을 조회하세요.


고객의 적립금 합계와 평균(소수점 없이)을 조회하세요.


**힌트 1:** customers 테이블의 point_balance에 SUM과 ROUND(AVG(...), 0)를 적용합니다


??? success "정답"
    ```sql
    SELECT SUM(point_balance) AS total_points,
           ROUND(AVG(point_balance), 0) AS avg_points
    FROM customers;
    ```


    **실행 결과** (1행)

    | total_points | avg_points |
    |---|---|
    | 337,459,019 | 64,524.00 |


---


### 24. 2024년에 접수된 주문의 건수와 총 매출(소수점 없이)을 조회하세요.


2024년에 접수된 주문의 건수와 총 매출(소수점 없이)을 조회하세요.


**힌트 1:** ordered_at이 '2024-01-01' 이상이고 '2025-01-01' 미만인 조건을 사용합니다


??? success "정답"
    ```sql
    SELECT COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at < '2025-01-01';
    ```


    **실행 결과** (1행)

    | order_count | revenue |
    |---|---|
    | 5785 | 5,622,439,762.00 |


---


### 25. 환불(`refunded`) 상태 결제의 건수와 총 환불 금액을 조회하세요.


환불(`refunded`) 상태 결제의 건수와 총 환불 금액을 조회하세요.


**힌트 1:** payments 테이블에서 status = 'refunded'로 필터링합니다


??? success "정답"
    ```sql
    SELECT COUNT(*) AS refund_count,
           ROUND(SUM(amount), 0) AS refund_total
    FROM payments
    WHERE status = 'refunded';
    ```


    **실행 결과** (1행)

    | refund_count | refund_total |
    |---|---|
    | 1930 | 2,357,145,631.00 |


---


### 26. 판매 중인 상품의 총 재고 자산 가치(원가 x 재고수량의 합)를 구하세요.


판매 중인 상품의 총 재고 자산 가치(원가 x 재고수량의 합)를 구하세요.


**힌트 1:** SUM 안에서 산술 연산을 사용할 수 있습니다. SUM(cost_price * stock_qty)처럼 칼럼끼리 곱한 값을 합산합니다


??? success "정답"
    ```sql
    SELECT ROUND(SUM(cost_price * stock_qty), 0) AS inventory_value
    FROM products
    WHERE is_active = 1;
    ```


    **실행 결과** (1행)

    | inventory_value |
    |---|
    | 30,030,260,700.00 |


---


### 27. 전체 주문의 순매출(주문 금액 - 할인 금액의 합)을 구하세요.


전체 주문의 순매출(주문 금액 - 할인 금액의 합)을 구하세요.


**힌트 1:** SUM(total_amount - discount_amount)처럼 SUM 안에서 칼럼 간 뺄셈을 할 수 있습니다


??? success "정답"
    ```sql
    SELECT ROUND(SUM(total_amount - discount_amount), 0) AS net_revenue
    FROM orders;
    ```


    **실행 결과** (1행)

    | net_revenue |
    |---|
    | 37,831,403,663.00 |


---


### 28. 별점 1점 리뷰와 별점 5점 리뷰의 건수를 각각 구하세요.


별점 1점 리뷰와 별점 5점 리뷰의 건수를 각각 구하세요.


**힌트 1:** GROUP BY를 아직 배우지 않았으므로, 두 개의 쿼리를 나란히 실행해도 됩니다


??? success "정답"
    ```sql
    SELECT COUNT(*) AS one_star_count
    FROM reviews
    WHERE rating = 1;
    ```


    **실행 결과** (1행)

    | one_star_count |
    |---|
    | 434 |


---


### 29. 판매 중인 상품의 평균 마진율(%)을 구하세요. 마진율은 `(price - cost_price) * 100.


판매 중인 상품의 평균 마진율(%)을 구하세요. 마진율은 `(price - cost_price) * 100.0 / price`이며, 소수점 첫째 자리까지 반올림합니다.


**힌트 1:** AVG 안에 산술식을 넣을 수 있습니다. AVG((price - cost_price) * 100.0 / price)로 각 행의 마진율 평균을 구합니다


??? success "정답"
    ```sql
    SELECT ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1;
    ```


    **실행 결과** (1행)

    | avg_margin_pct |
    |---|
    | 23.90 |


---


### 30. 주문 테이블에서 전체 건수, 총 매출, 평균 주문 금액, 총 할인 금액, 총 배송비, 총 사용 포인트를 한 


주문 테이블에서 전체 건수, 총 매출, 평균 주문 금액, 총 할인 금액, 총 배송비, 총 사용 포인트를 한 번에 조회하세요. 금액은 모두 소수점 없이 반올림합니다.


**힌트 1:** 하나의 SELECT에 6개의 집계 함수를 나열합니다


??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_orders,
           ROUND(SUM(total_amount), 0) AS total_revenue,
           ROUND(AVG(total_amount), 0) AS avg_amount,
           ROUND(SUM(discount_amount), 0) AS total_discount,
           ROUND(SUM(shipping_fee), 0) AS total_shipping,
           SUM(point_used) AS total_point_used
    FROM orders;
    ```


    **실행 결과** (1행)

    | total_orders | total_revenue | avg_amount | total_discount | total_shipping | total_point_used |
    |---|---|---|---|---|---|
    | 37,557 | 38,183,495,063.00 | 1,016,681.00 | 352,091,400.00 | 9,198,000.00 | 9,303,137 |


---
