# 윈도우 함수 실전

!!! info "사용 테이블"

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `reviews` — 리뷰 (평점, 내용)  

    `payments` — 결제 (방법, 금액, 상태)  

    `categories` — 카테고리 (부모-자식 계층)  



!!! abstract "학습 범위"

    `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `LAG`, `LEAD`, `SUM OVER`, `AVG OVER`, `FIRST_VALUE`, `LAST_VALUE`, `ROWS BETWEEN`



### 1. 각 고객의 주문을 시간순으로 정렬하여, 고객별 주문 순번을 매기세요.


고객 ID, 고객명, 주문번호, 주문일, 주문금액, 그리고 해당 고객 내에서 몇 번째 주문인지(`order_seq`)를 표시합니다.
상위 20행만 출력하세요.


**힌트 1:** `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`를 사용합니다.
`PARTITION BY customer_id`로 고객별로 그룹을 나누고, `ORDER BY ordered_at`으로 시간순 정렬합니다.



??? success "정답"
    ```sql
    SELECT
        c.id             AS customer_id,
        c.name           AS customer_name,
        o.order_number,
        o.ordered_at,
        o.total_amount,
        ROW_NUMBER() OVER (
            PARTITION BY c.id
            ORDER BY o.ordered_at
        ) AS order_seq
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY c.id, order_seq
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer_id | customer_name | order_number | ordered_at | total_amount | order_seq |
    |---|---|---|---|---|---|
    | 2 | 김경수 | ORD-20160807-00243 | 2016-08-17 23:29:34 | 2,413,300.00 | 1 |
    | 2 | 김경수 | ORD-20160802-00236 | 2016-08-19 22:29:34 | 298,500.00 | 2 |
    | 2 | 김경수 | ORD-20160830-00269 | 2016-08-30 10:49:39 | 445,700.00 | 3 |
    | 2 | 김경수 | ORD-20160904-00274 | 2016-09-04 08:47:04 | 597,000.00 | 4 |
    | 2 | 김경수 | ORD-20160915-00287 | 2016-09-15 20:07:17 | 1,760,400.00 | 5 |
    | 2 | 김경수 | ORD-20161024-00334 | 2016-10-24 12:13:06 | 131,500.00 | 6 |
    | 2 | 김경수 | ORD-20161101-00343 | 2016-11-01 10:44:08 | 323,500.00 | 7 |


---


### 2. 2024년 월별 매출 순위를 매기세요. 동일 매출이면 같은 순위를 부여합니다.


각 월의 총 매출, `RANK`와 `DENSE_RANK` 값을 모두 표시하여 차이를 비교하세요.


**힌트 1:** 먼저 `SUBSTR(ordered_at, 1, 7)`로 월별 매출을 집계한 서브쿼리(또는 CTE)를 만들고,
그 결과에 `RANK() OVER (ORDER BY revenue DESC)`와 `DENSE_RANK()`를 적용합니다.



??? success "정답"
    ```sql
    WITH monthly_revenue AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        RANK()       OVER (ORDER BY revenue DESC) AS rank_val,
        DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank_val
    FROM monthly_revenue
    ORDER BY year_month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | year_month | revenue | rank_val | dense_rank_val |
    |---|---|---|---|
    | 2024-01 | 288,908,320.00 | 12 | 12 |
    | 2024-02 | 403,127,749.00 | 9 | 9 |
    | 2024-03 | 519,844,502.00 | 3 | 3 |
    | 2024-04 | 451,877,581.00 | 4 | 4 |
    | 2024-05 | 425,264,478.00 | 5 | 5 |
    | 2024-06 | 362,715,211.00 | 10 | 10 |
    | 2024-07 | 343,929,897.00 | 11 | 11 |


---


### 3. 상품별 총 매출과 함께, 해당 카테고리 내에서의 매출 비중(%)을 구하세요.


2024년 기준, 상위 15개 상품을 매출 내림차순으로 표시합니다.


**힌트 1:** `SUM(매출) OVER (PARTITION BY category_id)`로 카테고리 전체 매출을 구하고,
개별 상품 매출을 카테고리 매출로 나누면 비중이 됩니다.



??? success "정답"
    ```sql
    SELECT
        p.name            AS product_name,
        cat.name          AS category,
        ROUND(SUM(oi.quantity * oi.unit_price), 0) AS product_revenue,
        ROUND(SUM(SUM(oi.quantity * oi.unit_price)) OVER (
            PARTITION BY p.category_id
        ), 0) AS category_revenue,
        ROUND(100.0 * SUM(oi.quantity * oi.unit_price)
            / SUM(SUM(oi.quantity * oi.unit_price)) OVER (PARTITION BY p.category_id),
        1) AS pct_of_category
    FROM order_items AS oi
    INNER JOIN orders     AS o   ON oi.order_id   = o.id
    INNER JOIN products   AS p   ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY p.id, p.name, cat.name, p.category_id
    ORDER BY product_revenue DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | product_name | category | product_revenue | category_revenue | pct_of_category |
    |---|---|---|---|---|
    | Razer Blade 18 블랙 | 게이밍 노트북 | 165,417,800.00 | 636,925,700.00 | 26.00 |
    | Razer Blade 16 실버 | 게이밍 노트북 | 137,007,300.00 | 636,925,700.00 | 21.50 |
    | MacBook Air 15 M3 실버 | 맥북 | 126,065,300.00 | 126,065,300.00 | 100.00 |
    | ASUS Dual RTX 4060 Ti 블랙 | NVIDIA | 106,992,000.00 | 345,858,700.00 | 30.90 |
    | ASUS Dual RTX 5070 Ti 실버 | NVIDIA | 104,558,400.00 | 345,858,700.00 | 30.20 |
    | ASUS ROG Swift PG32UCDM 실버 | 게이밍 모니터 | 90,734,400.00 | 353,934,400.00 | 25.60 |
    | ASUS ROG Strix Scar 16 | 게이밍 노트북 | 85,837,500.00 | 636,925,700.00 | 13.50 |


---


### 4. 각 고객의 주문 금액에 대해 누적 합계(running total)를 계산하세요.


고객 ID 1~5번에 대해, 주문 시간순으로 누적 주문 금액을 표시합니다.


**힌트 1:** `SUM(total_amount) OVER (PARTITION BY customer_id ORDER BY ordered_at ROWS UNBOUNDED PRECEDING)`
이 구문이 누적 합계(running total)를 만듭니다.



??? success "정답"
    ```sql
    SELECT
        c.id            AS customer_id,
        c.name          AS customer_name,
        o.ordered_at,
        o.total_amount,
        SUM(o.total_amount) OVER (
            PARTITION BY c.id
            ORDER BY o.ordered_at
            ROWS UNBOUNDED PRECEDING
        ) AS running_total
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE c.id BETWEEN 1 AND 5
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY c.id, o.ordered_at;
    ```


    **실행 결과** (총 416행 중 상위 7행)

    | customer_id | customer_name | ordered_at | total_amount | running_total |
    |---|---|---|---|---|
    | 2 | 김경수 | 2016-08-17 23:29:34 | 2,413,300.00 | 2,413,300.00 |
    | 2 | 김경수 | 2016-08-19 22:29:34 | 298,500.00 | 2,711,800.00 |
    | 2 | 김경수 | 2016-08-30 10:49:39 | 445,700.00 | 3,157,500.00 |
    | 2 | 김경수 | 2016-09-04 08:47:04 | 597,000.00 | 3,754,500.00 |
    | 2 | 김경수 | 2016-09-15 20:07:17 | 1,760,400.00 | 5,514,900.00 |
    | 2 | 김경수 | 2016-10-24 12:13:06 | 131,500.00 | 5,646,400.00 |
    | 2 | 김경수 | 2016-11-01 10:44:08 | 323,500.00 | 5,969,900.00 |


---


### 5. 결제 건수 기준으로 결제 수단을 4개 그룹(분위)으로 나누세요.


2024년 완료된 결제(`status = 'completed'`)를 수단별로 집계하고, `NTILE(4)`로 분위를 매깁니다.


**힌트 1:** 먼저 결제 수단별 건수를 집계한 CTE를 만들고,
`NTILE(4) OVER (ORDER BY payment_count DESC)`로 4분위를 나눕니다.
1분위가 가장 많이 사용된 그룹입니다.



??? success "정답"
    ```sql
    WITH method_stats AS (
        SELECT
            method,
            COUNT(*)              AS payment_count,
            ROUND(SUM(amount), 0) AS total_amount
        FROM payments
        WHERE status = 'completed'
          AND paid_at LIKE '2024%'
        GROUP BY method
    )
    SELECT
        method,
        payment_count,
        total_amount,
        NTILE(4) OVER (ORDER BY payment_count DESC) AS quartile
    FROM method_stats
    ORDER BY payment_count DESC;
    ```


    **실행 결과** (6행)

    | method | payment_count | total_amount | quartile |
    |---|---|---|---|
    | card | 2374 | 2,395,888,991.00 | 1 |
    | kakao_pay | 1058 | 1,002,822,322.00 | 1 |
    | naver_pay | 810 | 719,061,948.00 | 2 |
    | bank_transfer | 516 | 483,849,949.00 | 2 |
    | point | 286 | 261,926,968.00 | 3 |
    | virtual_account | 276 | 250,893,342.00 | 4 |


---


### 6. 월별 매출의 전월 대비 증감액과 증감률을 구하세요.


2023~2024년 데이터를 사용합니다.


**힌트 1:** `LAG(revenue, 1) OVER (ORDER BY year_month)`로 이전 월 매출을 가져옵니다.
증감률은 `(당월 - 전월) / 전월 * 100`으로 계산합니다.



??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at >= '2023-01-01'
          AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        LAG(revenue, 1) OVER (ORDER BY year_month) AS prev_revenue,
        revenue - LAG(revenue, 1) OVER (ORDER BY year_month) AS diff,
        ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY year_month))
            / LAG(revenue, 1) OVER (ORDER BY year_month), 1) AS growth_pct
    FROM monthly
    ORDER BY year_month;
    ```


    **실행 결과** (총 24행 중 상위 7행)

    | year_month | revenue | prev_revenue | diff | growth_pct |
    |---|---|---|---|---|
    | 2023-01 | 270,083,587.00 | NULL | NULL | NULL |
    | 2023-02 | 327,431,648.00 | 270,083,587.00 | 57,348,061.00 | 21.20 |
    | 2023-03 | 477,735,354.00 | 327,431,648.00 | 150,303,706.00 | 45.90 |
    | 2023-04 | 396,849,049.00 | 477,735,354.00 | -80,886,305.00 | -16.90 |
    | 2023-05 | 349,749,072.00 | 396,849,049.00 | -47,099,977.00 | -11.90 |
    | 2023-06 | 279,698,633.00 | 349,749,072.00 | -70,050,439.00 | -20.00 |
    | 2023-07 | 312,983,148.00 | 279,698,633.00 | 33,284,515.00 | 11.90 |


---


### 7. 고객의 다음 주문까지 걸린 일수를 계산하세요.


VIP 등급 고객에 대해, 각 주문과 다음 주문 사이의 간격(일)을 구합니다.
평균 간격이 가장 짧은 상위 10명을 표시하세요.


**힌트 1:** `LEAD(ordered_at, 1) OVER (PARTITION BY customer_id ORDER BY ordered_at)`로 다음 주문일을 가져오고,
`JULIANDAY(next_order) - JULIANDAY(ordered_at)`로 간격을 계산합니다.



??? success "정답"
    ```sql
    WITH order_gaps AS (
        SELECT
            o.customer_id,
            c.name,
            o.ordered_at,
            LEAD(o.ordered_at, 1) OVER (
                PARTITION BY o.customer_id
                ORDER BY o.ordered_at
            ) AS next_order_at,
            ROUND(
                JULIANDAY(LEAD(o.ordered_at, 1) OVER (
                    PARTITION BY o.customer_id
                    ORDER BY o.ordered_at
                )) - JULIANDAY(o.ordered_at),
            0) AS days_to_next
        FROM orders AS o
        INNER JOIN customers AS c ON o.customer_id = c.id
        WHERE c.grade = 'VIP'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        customer_id,
        name,
        COUNT(days_to_next)       AS gap_count,
        ROUND(AVG(days_to_next), 1) AS avg_days_between,
        MIN(days_to_next)           AS min_gap,
        MAX(days_to_next)           AS max_gap
    FROM order_gaps
    WHERE days_to_next IS NOT NULL
    GROUP BY customer_id, name
    ORDER BY avg_days_between ASC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | customer_id | name | gap_count | avg_days_between | min_gap | max_gap |
    |---|---|---|---|---|---|
    | 97 | 김병철 | 341 | 10.10 | 0.0 | 112.00 |
    | 226 | 박정수 | 302 | 10.80 | 0.0 | 89.00 |
    | 549 | 이미정 | 218 | 12.00 | 0.0 | 74.00 |
    | 4840 | 김승현 | 6 | 12.00 | 0.0 | 26.00 |
    | 356 | 정유진 | 222 | 12.30 | 0.0 | 126.00 |
    | 162 | 강명자 | 248 | 13.00 | 0.0 | 102.00 |
    | 98 | 이영자 | 274 | 13.20 | 0.0 | 143.00 |


---


### 8. 3개월 이동 평균 매출을 구하세요.


2023~2024년 월별 매출에 대해, 현재 월 포함 직전 3개월의 이동 평균을 계산합니다.


**힌트 1:** `AVG(revenue) OVER (ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`
이 구문이 현재 행 포함 이전 2행(총 3행)의 평균을 계산합니다.



??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at >= '2023-01-01'
          AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 0) AS moving_avg_3m,
        COUNT(*) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS window_size
    FROM monthly
    ORDER BY year_month;
    ```


    **실행 결과** (총 24행 중 상위 7행)

    | year_month | revenue | moving_avg_3m | window_size |
    |---|---|---|---|
    | 2023-01 | 270,083,587.00 | 270,083,587.00 | 1 |
    | 2023-02 | 327,431,648.00 | 298,757,618.00 | 2 |
    | 2023-03 | 477,735,354.00 | 358,416,863.00 | 3 |
    | 2023-04 | 396,849,049.00 | 400,672,017.00 | 3 |
    | 2023-05 | 349,749,072.00 | 408,111,158.00 | 3 |
    | 2023-06 | 279,698,633.00 | 342,098,918.00 | 3 |
    | 2023-07 | 312,983,148.00 | 314,143,618.00 | 3 |


---


### 9. 카테고리별로 가장 비싼 상품과 가장 저렴한 상품의 이름을 한 행에 표시하세요.


`FIRST_VALUE`와 `LAST_VALUE`를 사용합니다.


**힌트 1:** `FIRST_VALUE(name) OVER (PARTITION BY category_id ORDER BY price DESC)`는 가장 비싼 상품명입니다.
`LAST_VALUE` 사용 시 반드시 `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`을 명시해야 전체 파티션을 봅니다.



??? success "정답"
    ```sql
    WITH ranked AS (
        SELECT DISTINCT
            cat.name AS category,
            FIRST_VALUE(p.name) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS most_expensive,
            FIRST_VALUE(p.price) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS max_price,
            LAST_VALUE(p.name) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS cheapest,
            LAST_VALUE(p.price) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS min_price
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
    )
    SELECT DISTINCT
        category,
        most_expensive,
        max_price,
        cheapest,
        min_price
    FROM ranked
    ORDER BY category;
    ```


    **실행 결과** (총 38행 중 상위 7행)

    | category | most_expensive | max_price | cheapest | min_price |
    |---|---|---|---|---|
    | 2in1 | 레노버 ThinkPad X1 2in1 실버 | 1,866,100.00 | 삼성 갤럭시북5 360 블랙 | 1,179,900.00 |
    | AMD | AMD Ryzen 9 9900X | 591,800.00 | AMD Ryzen 9 9900X | 335,700.00 |
    | AMD | MSI Radeon RX 9070 XT GAMING X | 1,896,000.00 | MSI Radeon RX 9070 VENTUS 3X 화이트 | 383,100.00 |
    | AMD 소켓 | ASRock B850M Pro RS 실버 | 665,600.00 | 기가바이트 B650M AORUS ELITE AX | 376,000.00 |
    | DDR4 | Kingston FURY Beast DDR4 16GB 블랙 | 98,800.00 | 삼성 DDR4 32GB PC4-25600 | 43,500.00 |
    | DDR5 | Kingston FURY Renegade DDR5 32GB 7200... | 282,300.00 | TeamGroup T-Force Vulcan DDR5 32GB 52... | 139,800.00 |
    | HDD | Seagate IronWolf 4TB 블랙 | 545,400.00 | Seagate Exos 16TB 실버 | 303,300.00 |


---


### 10. 리뷰 평점 기준으로 상품을 5개 등급(NTILE)으로 나누고, 각 등급의 통계를 구하세요.


리뷰가 3건 이상인 상품만 대상으로 합니다.


**힌트 1:** 먼저 상품별 평균 평점을 구하고(`HAVING COUNT(*) >= 3`),
그 결과에 `NTILE(5) OVER (ORDER BY avg_rating)`로 등급을 나눈 뒤,
등급별로 다시 집계합니다.



??? success "정답"
    ```sql
    WITH product_ratings AS (
        SELECT
            p.id,
            p.name,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(*)                AS review_count
        FROM reviews AS r
        INNER JOIN products AS p ON r.product_id = p.id
        GROUP BY p.id, p.name
        HAVING COUNT(*) >= 3
    ),
    tiered AS (
        SELECT
            *,
            NTILE(5) OVER (ORDER BY avg_rating) AS tier
        FROM product_ratings
    )
    SELECT
        tier,
        COUNT(*)                     AS product_count,
        ROUND(MIN(avg_rating), 2)    AS min_rating,
        ROUND(MAX(avg_rating), 2)    AS max_rating,
        ROUND(AVG(avg_rating), 2)    AS avg_of_avg,
        ROUND(AVG(review_count), 1)  AS avg_reviews
    FROM tiered
    GROUP BY tier
    ORDER BY tier;
    ```


    **실행 결과** (5행)

    | tier | product_count | min_rating | max_rating | avg_of_avg | avg_reviews |
    |---|---|---|---|---|---|
    | 1 | 53 | 3.00 | 3.68 | 3.50 | 23.20 |
    | 2 | 53 | 3.70 | 3.83 | 3.76 | 33.70 |
    | 3 | 53 | 3.83 | 3.97 | 3.90 | 41.90 |
    | 4 | 53 | 3.97 | 4.10 | 4.02 | 34.20 |
    | 5 | 52 | 4.10 | 4.80 | 4.26 | 28.30 |


---


### 11. 고객 등급별로 주문 금액 순위를 매기고, 등급 내 상위 3명의 정보를 추출하세요.


각 등급(BRONZE, SILVER, GOLD, VIP)에서 총 주문 금액 기준 상위 3명을 보여줍니다.


**힌트 1:** CTE에서 고객별 총 주문 금액을 집계한 뒤, `ROW_NUMBER() OVER (PARTITION BY grade ORDER BY total_spent DESC)`로
등급별 순위를 매기고, 외부 쿼리에서 `WHERE rn <= 3`으로 필터링합니다.



??? success "정답"
    ```sql
    WITH customer_totals AS (
        SELECT
            c.id,
            c.name,
            c.grade,
            COUNT(*)                    AS order_count,
            ROUND(SUM(o.total_amount), 0) AS total_spent
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    ),
    ranked AS (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY grade
                ORDER BY total_spent DESC
            ) AS rn
        FROM customer_totals
    )
    SELECT
        grade,
        rn   AS rank_in_grade,
        name AS customer_name,
        order_count,
        total_spent
    FROM ranked
    WHERE rn <= 3
    ORDER BY
        CASE grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
        END,
        rn;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | grade | rank_in_grade | customer_name | order_count | total_spent |
    |---|---|---|---|---|
    | VIP | 1 | 박정수 | 303 | 403,448,758.00 |
    | VIP | 2 | 김병철 | 342 | 366,385,931.00 |
    | VIP | 3 | 강명자 | 249 | 253,180,338.00 |
    | GOLD | 1 | 김경희 | 171 | 204,611,811.00 |
    | GOLD | 2 | 김영길 | 160 | 199,282,408.00 |
    | GOLD | 3 | 곽재호 | 117 | 116,612,251.00 |
    | SILVER | 1 | 이예준 | 159 | 131,134,943.00 |


---


### 12. 상품별 월간 매출 추이와 함께, 해당 상품의 전체 평균 대비 비율을 표시하세요.


2024년 상위 5개 상품에 대해, 월별 매출과 해당 상품 전체 월 평균 매출 대비 비율(%)을 구합니다.


**힌트 1:** 1단계: 상품-월별 매출 집계. 2단계: 상위 5개 상품 선별(총 매출 기준).
3단계: `AVG(monthly_revenue) OVER (PARTITION BY product_id)`로 상품별 전체 평균을 구하고,
월별 매출을 평균으로 나누어 비율을 계산합니다.



??? success "정답"
    ```sql
    WITH product_monthly AS (
        SELECT
            p.id       AS product_id,
            p.name     AS product_name,
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS monthly_revenue
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name, SUBSTR(o.ordered_at, 1, 7)
    ),
    top5 AS (
        SELECT product_id
        FROM product_monthly
        GROUP BY product_id
        ORDER BY SUM(monthly_revenue) DESC
        LIMIT 5
    )
    SELECT
        pm.product_name,
        pm.year_month,
        pm.monthly_revenue,
        ROUND(AVG(pm.monthly_revenue) OVER (
            PARTITION BY pm.product_id
        ), 0) AS avg_monthly,
        ROUND(100.0 * pm.monthly_revenue
            / AVG(pm.monthly_revenue) OVER (PARTITION BY pm.product_id),
        1) AS pct_of_avg
    FROM product_monthly AS pm
    INNER JOIN top5 AS t ON pm.product_id = t.product_id
    ORDER BY pm.product_name, pm.year_month;
    ```


    **실행 결과** (총 55행 중 상위 7행)

    | product_name | year_month | monthly_revenue | avg_monthly | pct_of_avg |
    |---|---|---|---|---|
    | ASUS Dual RTX 4060 Ti 블랙 | 2024-01 | 8,024,400.00 | 8,916,000.00 | 90.00 |
    | ASUS Dual RTX 4060 Ti 블랙 | 2024-02 | 8,024,400.00 | 8,916,000.00 | 90.00 |
    | ASUS Dual RTX 4060 Ti 블랙 | 2024-03 | 8,024,400.00 | 8,916,000.00 | 90.00 |
    | ASUS Dual RTX 4060 Ti 블랙 | 2024-04 | 13,374,000.00 | 8,916,000.00 | 150.00 |
    | ASUS Dual RTX 4060 Ti 블랙 | 2024-05 | 5,349,600.00 | 8,916,000.00 | 60.00 |
    | ASUS Dual RTX 4060 Ti 블랙 | 2024-06 | 2,674,800.00 | 8,916,000.00 | 30.00 |
    | ASUS Dual RTX 4060 Ti 블랙 | 2024-07 | 2,674,800.00 | 8,916,000.00 | 30.00 |


---


### 13. 결제 수단별 월간 점유율 변화를 추적하세요.


2024년 월별로 각 결제 수단이 차지하는 비중(%)을 구하고, 전월 대비 점유율 변동(pp)을 계산합니다.


**힌트 1:** 월-결제수단별 금액을 구한 뒤, `SUM(amount) OVER (PARTITION BY year_month)`으로 월 전체 합계를 구합니다.
`LAG(share_pct, 1) OVER (PARTITION BY method ORDER BY year_month)`로 전월 점유율을 가져옵니다.



??? success "정답"
    ```sql
    WITH method_monthly AS (
        SELECT
            SUBSTR(paid_at, 1, 7) AS year_month,
            method,
            ROUND(SUM(amount), 0) AS method_amount
        FROM payments
        WHERE status = 'completed'
          AND paid_at LIKE '2024%'
        GROUP BY SUBSTR(paid_at, 1, 7), method
    ),
    with_share AS (
        SELECT
            year_month,
            method,
            method_amount,
            ROUND(100.0 * method_amount
                / SUM(method_amount) OVER (PARTITION BY year_month),
            1) AS share_pct
        FROM method_monthly
    )
    SELECT
        year_month,
        method,
        method_amount,
        share_pct,
        LAG(share_pct, 1) OVER (
            PARTITION BY method
            ORDER BY year_month
        ) AS prev_share_pct,
        ROUND(share_pct - LAG(share_pct, 1) OVER (
            PARTITION BY method
            ORDER BY year_month
        ), 1) AS share_change_pp
    FROM with_share
    ORDER BY year_month, share_pct DESC;
    ```


    **실행 결과** (총 72행 중 상위 7행)

    | year_month | method | method_amount | share_pct | prev_share_pct | share_change_pp |
    |---|---|---|---|---|---|
    | 2024-01 | card | 147,207,539.00 | 51.00 | NULL | NULL |
    | 2024-01 | kakao_pay | 53,100,585.00 | 18.40 | NULL | NULL |
    | 2024-01 | naver_pay | 33,230,574.00 | 11.50 | NULL | NULL |
    | 2024-01 | bank_transfer | 24,355,270.00 | 8.40 | NULL | NULL |
    | 2024-01 | virtual_account | 17,502,152.00 | 6.10 | NULL | NULL |
    | 2024-01 | point | 13,512,200.00 | 4.70 | NULL | NULL |
    | 2024-02 | card | 169,679,102.00 | 42.10 | 51.00 | -8.90 |


---


### 14. 고객별 주문 금액의 갭(Gap) 분석을 수행하세요.


각 고객의 주문을 금액 순으로 정렬했을 때, 이전 주문 대비 금액 차이가 가장 큰 "점프"를 찾습니다.
점프 금액이 50만원 이상인 경우만 추출하세요.


**힌트 1:** `LAG(total_amount, 1) OVER (PARTITION BY customer_id ORDER BY total_amount)`로
금액 순 이전 주문 금액을 가져옵니다. 차이를 구해 50만원 이상인 행만 필터링합니다.



??? success "정답"
    ```sql
    WITH ordered AS (
        SELECT
            o.customer_id,
            c.name,
            o.order_number,
            o.total_amount,
            LAG(o.total_amount, 1) OVER (
                PARTITION BY o.customer_id
                ORDER BY o.total_amount
            ) AS prev_amount
        FROM orders AS o
        INNER JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        customer_id,
        name,
        order_number,
        prev_amount,
        total_amount,
        total_amount - prev_amount AS gap
    FROM ordered
    WHERE prev_amount IS NOT NULL
      AND (total_amount - prev_amount) >= 500000
    ORDER BY gap DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer_id | name | order_number | prev_amount | total_amount | gap |
    |---|---|---|---|---|---|
    | 514 | 오현준 | ORD-20201121-08810 | 837,600.00 | 50,867,500.00 | 50,029,900.00 |
    | 3774 | 김현지 | ORD-20250305-32265 | 6,346,600.00 | 46,820,024.00 | 40,473,424.00 |
    | 4136 | 김영미 | ORD-20251218-37240 | 405,600.00 | 38,626,400.00 | 38,220,800.00 |
    | 1322 | 손정자 | ORD-20220106-15263 | 1,898,100.00 | 37,987,600.00 | 36,089,500.00 |
    | 3 | 김민재 | ORD-20200209-05404 | 9,690,532.00 | 43,677,500.00 | 33,986,968.00 |
    | 551 | 김민재 | ORD-20200820-07684 | 4,885,100.00 | 37,518,200.00 | 32,633,100.00 |
    | 4965 | 성진우 | ORD-20251207-37004 | 369,800.00 | 31,985,600.00 | 31,615,800.00 |


---


### 15. 연도별(YoY) 매출 성장률을 윈도우 함수로 계산하고, 분기별 추세도 함께 표시하세요.


각 분기의 매출, 전년 동분기 매출, YoY 성장률을 구합니다.


**힌트 1:** 분기는 `(CAST(SUBSTR(ordered_at,6,2) AS INTEGER) + 2) / 3`으로 계산합니다.
`LAG(revenue, 4) OVER (ORDER BY year, quarter)`로 4분기 전(= 전년 동분기) 값을 가져옵니다.



??? success "정답"
    ```sql
    WITH quarterly AS (
        SELECT
            CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER) AS year,
            (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3 AS quarter,
            ROUND(SUM(total_amount), 0) AS revenue,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2020-01-01'
        GROUP BY
            CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER),
            (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3
    )
    SELECT
        year,
        quarter,
        revenue,
        order_count,
        LAG(revenue, 4) OVER (ORDER BY year, quarter) AS prev_year_revenue,
        CASE
            WHEN LAG(revenue, 4) OVER (ORDER BY year, quarter) IS NOT NULL
            THEN ROUND(100.0 * (revenue - LAG(revenue, 4) OVER (ORDER BY year, quarter))
                / LAG(revenue, 4) OVER (ORDER BY year, quarter), 1)
        END AS yoy_growth_pct
    FROM quarterly
    ORDER BY year, quarter;
    ```


    **실행 결과** (총 24행 중 상위 7행)

    | year | quarter | revenue | order_count | prev_year_revenue | yoy_growth_pct |
    |---|---|---|---|---|---|
    | 2020 | 1 | 1,001,221,410.00 | 990 | NULL | NULL |
    | 2020 | 2 | 991,211,380.00 | 982 | NULL | NULL |
    | 2020 | 3 | 1,009,837,258.00 | 964 | NULL | NULL |
    | 2020 | 4 | 1,086,405,018.00 | 1084 | NULL | NULL |
    | 2021 | 1 | 1,458,348,254.00 | 1351 | 1,001,221,410.00 | 45.70 |
    | 2021 | 2 | 1,210,987,985.00 | 1143 | 991,211,380.00 | 22.20 |
    | 2021 | 3 | 1,361,699,965.00 | 1412 | 1,009,837,258.00 | 34.80 |


---
