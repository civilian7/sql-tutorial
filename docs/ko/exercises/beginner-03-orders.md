# 주문 기초

!!! info "사용 테이블"

    `orders` — 주문 (상태, 금액, 일시)  

    `payments` — 결제 (방법, 금액, 상태)  



!!! abstract "학습 범위"

    `SELECT`, `WHERE`, `GROUP BY`, `COUNT`, `SUM`, `AVG`, `MAX`, `ROUND`, `SUBSTR`, `STRFTIME`, `CASE WHEN`, `LIKE`, `subquery`



### 1. 전체 주문 수와 총 매출을 구하세요.


전체 주문 수와 총 매출을 구하세요.


**힌트 1:** COUNT(*)와 SUM(total_amount)를 함께 사용하세요


??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS total_orders,
        ROUND(SUM(total_amount), 2) AS total_revenue
    FROM orders;
    ```


    **실행 결과** (1행)

    | total_orders | total_revenue |
    |---|---|
    | 37,557 | 38,183,495,063.00 |


---


### 2. 주문 상태(status)별 건수를 구하세요.


주문 상태(status)별 건수를 구하세요.


**힌트 1:** GROUP BY status와 COUNT(*)를 사용하세요


??? success "정답"
    ```sql
    SELECT status, COUNT(*) AS cnt
    FROM orders
    GROUP BY status
    ORDER BY cnt DESC;
    ```


    **실행 결과** (총 9행 중 상위 7행)

    | status | cnt |
    |---|---|
    | confirmed | 34,393 |
    | cancelled | 1859 |
    | return_requested | 507 |
    | returned | 493 |
    | delivered | 125 |
    | pending | 82 |
    | shipped | 51 |


---


### 3. 2024년에 접수된 주문 수와 총 매출을 구하세요.


2024년에 접수된 주문 수와 총 매출을 구하세요.


**힌트 1:** WHERE ordered_at LIKE '2024%'로 2024년 데이터만 필터링하세요


??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%';
    ```


    **실행 결과** (1행)

    | order_count | revenue |
    |---|---|
    | 5785 | 5,622,439,762.00 |


---


### 4. 취소(cancelled) 상태의 주문 수와 취소율(%)을 구하세요.


취소(cancelled) 상태의 주문 수와 취소율(%)을 구하세요.


**힌트 1:** 취소율은 100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders)로 계산. 서브쿼리로 전체 수를 구하세요


??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS cancelled_count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 2) AS cancel_rate
    FROM orders
    WHERE status = 'cancelled';
    ```


    **실행 결과** (1행)

    | cancelled_count | cancel_rate |
    |---|---|
    | 1859 | 4.95 |


---


### 5. 주문 금액이 가장 큰 상위 10건의 주문번호, 금액, 주문일을 조회하세요.


주문 금액이 가장 큰 상위 10건의 주문번호, 금액, 주문일을 조회하세요.


**힌트 1:** ORDER BY total_amount DESC로 정렬 후 LIMIT 10


??? success "정답"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | total_amount | ordered_at |
    |---|---|---|
    | ORD-20201121-08810 | 50,867,500.00 | 2020-11-21 12:04:42 |
    | ORD-20250305-32265 | 46,820,024.00 | 2025-03-05 09:01:08 |
    | ORD-20230523-22331 | 46,094,971.00 | 2023-05-23 08:50:55 |
    | ORD-20200209-05404 | 43,677,500.00 | 2020-02-09 23:36:36 |
    | ORD-20221231-20394 | 43,585,700.00 | 2022-12-31 21:35:59 |
    | ORD-20251218-37240 | 38,626,400.00 | 2025-12-18 17:09:12 |
    | ORD-20220106-15263 | 37,987,600.00 | 2022-01-06 17:24:14 |


---


### 6. 2024년 월별 주문 수와 매출을 구하세요.


2024년 월별 주문 수와 매출을 구하세요.


**힌트 1:** SUBSTR(ordered_at, 1, 7)로 'YYYY-MM'을 추출하고 GROUP BY로 월별 집계. WHERE로 2024년 필터링


??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | month | orders | revenue |
    |---|---|---|
    | 2024-01 | 346 | 320,292,182.00 |
    | 2024-02 | 465 | 449,447,834.00 |
    | 2024-03 | 601 | 569,798,709.00 |
    | 2024-04 | 506 | 496,023,258.00 |
    | 2024-05 | 415 | 473,243,857.00 |
    | 2024-06 | 415 | 399,487,004.00 |
    | 2024-07 | 414 | 383,398,728.00 |


---


### 7. 전체 평균 주문 금액과 취소 제외 평균을 비교하세요.


전체 평균 주문 금액과 취소 제외 평균을 비교하세요.


**힌트 1:** AVG(total_amount)와 AVG(CASE WHEN status NOT IN ('cancelled') THEN total_amount END)를 한 쿼리에서 비교


??? success "정답"
    ```sql
    SELECT
        ROUND(AVG(total_amount), 2) AS avg_all,
        ROUND(AVG(CASE
            WHEN status NOT IN ('cancelled') THEN total_amount
        END), 2) AS avg_excl_cancelled
    FROM orders;
    ```


    **실행 결과** (1행)

    | avg_all | avg_excl_cancelled |
    |---|---|
    | 1,016,681.18 | 1,015,193.02 |


---


### 8. 배송비(shipping_fee)가 0인 주문의 비율을 구하세요.


배송비(shipping_fee)가 0인 주문의 비율을 구하세요.


**힌트 1:** SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END)로 조건부 카운트. 전체 COUNT(*)로 나눠 비율 계산


??? success "정답"
    ```sql
    SELECT
        SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) AS free_shipping,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct
    FROM orders;
    ```


    **실행 결과** (1행)

    | free_shipping | total | pct |
    |---|---|---|
    | 34,491 | 37,557 | 91.80 |


---


### 9. 적립금(point_used)을 사용한 주문의 수와 평균 사용 금액을 구하세요.


적립금(point_used)을 사용한 주문의 수와 평균 사용 금액을 구하세요.


**힌트 1:** WHERE point_used > 0으로 적립금 사용 주문만 필터링. AVG(point_used)로 평균 계산


??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS orders_with_points,
        ROUND(AVG(point_used), 0) AS avg_points_used,
        MAX(point_used) AS max_points_used
    FROM orders
    WHERE point_used > 0;
    ```


    **실행 결과** (1행)

    | orders_with_points | avg_points_used | max_points_used |
    |---|---|---|
    | 3740 | 2,487.00 | 5000 |


---


### 10. 결제 수단(method)별 건수와 총 결제 금액을 구하세요.


결제 수단(method)별 건수와 총 결제 금액을 구하세요.


**힌트 1:** payments 테이블에서 GROUP BY method로 그룹화. COUNT(*)와 SUM(amount) 사용


??? success "정답"
    ```sql
    SELECT
        method,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS total_amount
    FROM payments
    GROUP BY method
    ORDER BY total_amount DESC;
    ```


    **실행 결과** (6행)

    | method | tx_count | total_amount |
    |---|---|---|
    | card | 16,841 | 17,004,951,634.00 |
    | kakao_pay | 7486 | 7,563,829,668.00 |
    | naver_pay | 5715 | 5,998,835,720.00 |
    | bank_transfer | 3718 | 3,753,149,013.00 |
    | point | 1921 | 1,951,369,604.00 |
    | virtual_account | 1876 | 1,911,359,424.00 |


---


### 11. 카드 결제 중 할부(installment_months > 0) 비율과 평균 할부 개월을 구하세요.


카드 결제 중 할부(installment_months > 0) 비율과 평균 할부 개월을 구하세요.


**힌트 1:** WHERE method = 'card'로 카드 결제만 필터. CASE WHEN으로 할부 건수를 세고, 조건부 AVG로 평균 개월 계산


??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS card_payments,
        SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) AS installment_count,
        ROUND(100.0 * SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS installment_pct,
        ROUND(AVG(CASE WHEN installment_months > 0 THEN installment_months END), 1) AS avg_months
    FROM payments
    WHERE method = 'card';
    ```


    **실행 결과** (1행)

    | card_payments | installment_count | installment_pct | avg_months |
    |---|---|---|---|
    | 16,841 | 8128 | 48.30 | 7.50 |


---


### 12. 요일별(월~일) 주문 수를 구하세요.


요일별(월~일) 주문 수를 구하세요.


**힌트 1:** STRFTIME('%w', ordered_at)로 요일 번호(0=일, 1=월, ...)를 추출. CASE로 한글 요일명 매핑


??? success "정답"
    ```sql
    SELECT
        CASE CAST(STRFTIME('%w', ordered_at) AS INTEGER)
            WHEN 0 THEN '일'
            WHEN 1 THEN '월'
            WHEN 2 THEN '화'
            WHEN 3 THEN '수'
            WHEN 4 THEN '목'
            WHEN 5 THEN '금'
            WHEN 6 THEN '토'
        END AS day_name,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY STRFTIME('%w', ordered_at)
    ORDER BY STRFTIME('%w', ordered_at);
    ```


    **실행 결과** (7행)

    | day_name | order_count |
    |---|---|
    | 일 | 5929 |
    | 월 | 5890 |
    | 화 | 5136 |
    | 수 | 4798 |
    | 목 | 4757 |
    | 금 | 5112 |
    | 토 | 5935 |


---


### 13. 배송 메모(notes)가 있는 주문의 비율을 구하세요.


배송 메모(notes)가 있는 주문의 비율을 구하세요.


**힌트 1:** CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END로 메모 유무를 판별하고 SUM으로 집계


??? success "정답"
    ```sql
    SELECT
        SUM(CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END) AS with_notes,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct
    FROM orders;
    ```


    **실행 결과** (1행)

    | with_notes | total | pct |
    |---|---|---|
    | 13,219 | 37,557 | 35.20 |


---


### 14. 연도별 주문 수, 총 매출, 평균 주문 금액을 구하세요. 취소 주문은 제외합니다.


연도별 주문 수, 총 매출, 평균 주문 금액을 구하세요. 취소 주문은 제외합니다.


**힌트 1:** WHERE status NOT IN ('cancelled')로 취소 제외. SUBSTR(ordered_at, 1, 4)로 연도 추출 후 GROUP BY


??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 2) AS revenue,
        ROUND(AVG(total_amount), 2) AS avg_order
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | year | orders | revenue | avg_order |
    |---|---|---|---|
    | 2016 | 401 | 301,871,490.00 | 752,796.73 |
    | 2017 | 668 | 630,467,381.00 | 943,813.44 |
    | 2018 | 1255 | 1,203,414,419.00 | 958,895.95 |
    | 2019 | 2473 | 2,523,296,474.00 | 1,020,338.24 |
    | 2020 | 4128 | 4,251,046,262.00 | 1,029,807.72 |
    | 2021 | 5571 | 5,771,175,319.00 | 1,035,931.67 |
    | 2022 | 4947 | 4,999,116,420.00 | 1,010,534.95 |


---


### 15. 환불(refunded) 상태의 결제 건수와 총 환불 금액을 구하세요.


환불(refunded) 상태의 결제 건수와 총 환불 금액을 구하세요.


**힌트 1:** payments 테이블에서 WHERE status = 'refunded'로 필터링. COUNT(*)와 SUM(amount) 사용


??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS refund_count,
        ROUND(SUM(amount), 2) AS total_refunded
    FROM payments
    WHERE status = 'refunded';
    ```


    **실행 결과** (1행)

    | refund_count | total_refunded |
    |---|---|
    | 1930 | 2,357,145,631.00 |


---
