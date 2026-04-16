# 도전 문제

!!! info "사용 테이블"

    `categories` — 카테고리 (부모-자식 계층)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `reviews` — 리뷰 (평점, 내용)  

    `shipping` — 배송 (택배사, 추적번호, 상태)  

    `point_transactions` — 포인트 (적립, 사용, 소멸)  

    `product_views` — 조회 로그 (고객, 상품, 일시)  

    `inventory_transactions` — 재고 입출고 (유형, 수량)  

    `wishlists` — 위시리스트 (고객-상품)  

    `calendar` — 날짜 차원 (요일, 공휴일)  



!!! abstract "학습 범위"

    `Window`, `Analytics`, `CTE`, `consecutive`, `median`, `retention`



### 1. 중복 리뷰 감지


같은 상품에 2회 이상 리뷰를 작성한 고객을 찾으세요.
고객명, 상품명, 리뷰 횟수를 표시합니다.


**힌트 1:** - `reviews`를 `customers`, `products`와 JOIN
- `GROUP BY customer_id, product_id` 후 `HAVING COUNT(*) >= 2`



??? success "정답"
    ```sql
    SELECT
        c.name AS customer_name,
        p.name AS product_name,
        COUNT(*) AS review_count
    FROM reviews AS r
    INNER JOIN customers AS c ON r.customer_id = c.id
    INNER JOIN products AS p ON r.product_id = p.id
    GROUP BY r.customer_id, r.product_id, c.name, p.name
    HAVING COUNT(*) >= 2
    ORDER BY review_count DESC;
    ```


    **실행 결과** (총 321행 중 상위 7행)

    | customer_name | product_name | review_count |
    |---|---|---|
    | 이영자 | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 5 |
    | 김병철 | SteelSeries Aerox 5 Wireless 실버 | 4 |
    | 이영자 | 삼성 DDR5 32GB PC5-38400 | 4 |
    | 이영자 | 삼성 오디세이 G7 32 화이트 | 4 |
    | 강명자 | ASUS PCE-BE92BT | 4 |
    | 박정수 | 삼성 DDR4 32GB PC4-25600 | 4 |
    | 박정수 | Keychron Q1 Pro 실버 | 4 |


---


### 2. 평일 vs 주말 평균 주문 금액 비교


calendar 테이블을 활용하여 평일과 주말의 평균 주문 금액을 비교하세요.
평일/주말 구분, 주문 수, 평균 주문 금액, 총 매출을 표시합니다.


**힌트 1:** - `calendar.is_weekend` 칼럼 활용
- `orders`와 `calendar`를 날짜로 JOIN



??? success "정답"
    ```sql
    SELECT
        CASE cal.is_weekend
            WHEN 1 THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type,
        COUNT(*) AS order_count,
        ROUND(AVG(o.total_amount), 2) AS avg_order_value,
        ROUND(SUM(o.total_amount), 2) AS total_revenue
    FROM orders AS o
    INNER JOIN calendar AS cal
        ON SUBSTR(o.ordered_at, 1, 10) = cal.date_key
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY cal.is_weekend
    ORDER BY cal.is_weekend;
    ```


    **실행 결과** (2행)

    | day_type | order_count | avg_order_value | total_revenue |
    |---|---|---|---|
    | Weekday | 23,745 | 1,003,330.80 | 23,824,089,843.00 |
    | Weekend | 10,953 | 999,300.48 | 10,945,338,164.00 |


---


### 3. 전일 대비 주문 수 증감


2024년 12월의 일별 주문 수를 구하고,
LAG를 사용하여 전일 대비 주문 수가 증가한 날만 표시하세요.


**힌트 1:** - `SUBSTR(ordered_at, 1, 10)`으로 날짜 추출
- `LAG(order_count) OVER (ORDER BY order_date)`로 전일 값 참조



??? success "정답"
    ```sql
    WITH daily AS (
        SELECT
            SUBSTR(ordered_at, 1, 10) AS order_date,
            COUNT(*) AS order_count
        FROM orders
        WHERE ordered_at LIKE '2024-12%'
          AND status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 10)
    ),
    with_prev AS (
        SELECT
            order_date,
            order_count,
            LAG(order_count) OVER (ORDER BY order_date) AS prev_count
        FROM daily
    )
    SELECT
        order_date,
        order_count,
        prev_count,
        order_count - prev_count AS diff
    FROM with_prev
    WHERE order_count > prev_count
    ORDER BY order_date;
    ```


    **실행 결과** (총 11행 중 상위 7행)

    | order_date | order_count | prev_count | diff |
    |---|---|---|---|
    | 2024-12-03 | 15 | 14 | 1 |
    | 2024-12-06 | 14 | 9 | 5 |
    | 2024-12-07 | 15 | 14 | 1 |
    | 2024-12-08 | 18 | 15 | 3 |
    | 2024-12-14 | 17 | 13 | 4 |
    | 2024-12-17 | 17 | 14 | 3 |
    | 2024-12-20 | 18 | 14 | 4 |


---


### 4. 카테고리별 3번째로 비싼 상품


각 카테고리에서 가격이 3번째로 비싼 상품을 찾으세요.
카테고리명, 상품명, 가격, 순위를 표시합니다.


**힌트 1:** - `ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY price DESC)`
- `WHERE rn = 3`으로 필터



??? success "정답"
    ```sql
    WITH ranked AS (
        SELECT
            cat.name AS category,
            p.name AS product_name,
            p.price,
            ROW_NUMBER() OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
            ) AS rn
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
    )
    SELECT category, product_name, price, rn AS rank
    FROM ranked
    WHERE rn = 3
    ORDER BY price DESC;
    ```


    **실행 결과** (총 32행 중 상위 7행)

    | category | product_name | price | rank |
    |---|---|---|---|
    | 게이밍 노트북 | Razer Blade 18 블랙 | 2,987,500.00 | 3 |
    | 일반 노트북 | ASUS ExpertBook B5 화이트 | 2,068,800.00 | 3 |
    | 조립PC | ASUS ROG Strix G16CH 실버 | 1,879,100.00 | 3 |
    | NVIDIA | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | 3 |
    | 전문가용 모니터 | LG 32EP950 OLED 화이트 | 1,545,700.00 | 3 |
    | 게이밍 모니터 | LG 울트라기어 27GR95QE 화이트 | 1,511,700.00 | 3 |
    | 2in1 | HP Pavilion x360 14 블랙 | 1,479,700.00 | 3 |


---


### 5. A/B 버킷 분할


고객 ID의 홀짝(MOD)으로 A/B 그룹을 나누고,
각 그룹의 고객 수, 평균 주문 금액, 평균 주문 횟수를 비교하세요.


**힌트 1:** - `CASE WHEN c.id % 2 = 0 THEN 'A' ELSE 'B' END`
- `customers`와 `orders` JOIN 후 그룹별 집계



??? success "정답"
    ```sql
    SELECT
        CASE WHEN c.id % 2 = 0 THEN 'A' ELSE 'B' END AS bucket,
        COUNT(DISTINCT c.id) AS customer_count,
        COUNT(o.id) AS total_orders,
        ROUND(AVG(o.total_amount), 2) AS avg_order_value,
        ROUND(1.0 * COUNT(o.id) / COUNT(DISTINCT c.id), 1) AS avg_orders_per_customer
    FROM customers AS c
    LEFT JOIN orders AS o
        ON c.id = o.customer_id
       AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY CASE WHEN c.id % 2 = 0 THEN 'A' ELSE 'B' END
    ORDER BY bucket;
    ```


    **실행 결과** (2행)

    | bucket | customer_count | total_orders | avg_order_value | avg_orders_per_customer |
    |---|---|---|---|---|
    | A | 2615 | 17,147 | 1,010,823.23 | 6.60 |
    | B | 2615 | 17,551 | 993,495.65 | 6.70 |


---


### 6. 트리 노드 타입 분류


categories 테이블에서 각 카테고리를 root / inner / leaf로 분류하세요.
root: parent_id가 NULL, inner: 자식이 있는 비루트, leaf: 자식이 없는 노드.


**힌트 1:** - `LEFT JOIN categories AS child ON cat.id = child.parent_id`
- `CASE`로 parent_id와 child 존재 여부에 따라 분류



??? success "정답"
    ```sql
    SELECT
        cat.id,
        cat.name,
        cat.parent_id,
        cat.depth,
        CASE
            WHEN cat.parent_id IS NULL THEN 'root'
            WHEN EXISTS (SELECT 1 FROM categories c2 WHERE c2.parent_id = cat.id) THEN 'inner'
            ELSE 'leaf'
        END AS node_type
    FROM categories AS cat
    ORDER BY cat.depth, cat.sort_order;
    ```


    **실행 결과** (총 53행 중 상위 7행)

    | id | name | parent_id | depth | node_type |
    |---|---|---|---|---|
    | 1 | 데스크톱 PC | NULL | 0 | root |
    | 5 | 노트북 | NULL | 0 | root |
    | 10 | 모니터 | NULL | 0 | root |
    | 14 | CPU | NULL | 0 | root |
    | 17 | 메인보드 | NULL | 0 | root |
    | 20 | 메모리(RAM) | NULL | 0 | root |
    | 23 | 저장장치 | NULL | 0 | root |


---


### 7. 일별 주문 취소율 (최근 30일)


최근 30일간(2025-12-01 ~ 2025-12-31 기준) 일별 전체 주문 수와
취소된 주문 수, 취소율(%)을 계산하세요.


**힌트 1:** - `status = 'cancelled'`인 주문 비율 계산
- `SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END)`



??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 10) AS order_date,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        ROUND(100.0 * SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END)
            / COUNT(*), 2) AS cancel_rate_pct
    FROM orders
    WHERE ordered_at BETWEEN '2025-12-01' AND '2025-12-31 23:59:59'
    GROUP BY SUBSTR(ordered_at, 1, 10)
    ORDER BY order_date;
    ```


    **실행 결과** (총 31행 중 상위 7행)

    | order_date | total_orders | cancelled_orders | cancel_rate_pct |
    |---|---|---|---|
    | 2025-12-01 | 23 | 2 | 8.70 |
    | 2025-12-02 | 20 | 1 | 5.00 |
    | 2025-12-03 | 21 | 0 | 0.0 |
    | 2025-12-04 | 19 | 1 | 5.26 |
    | 2025-12-05 | 24 | 1 | 4.17 |
    | 2025-12-06 | 22 | 0 | 0.0 |
    | 2025-12-07 | 20 | 0 | 0.0 |


---


### 8. 할부 금액 계산


주문 금액이 500,000원 이상인 주문에 대해
3개월, 6개월, 12개월 할부 시 월 납부액을 계산하세요.
주문번호, 총액, 3/6/12개월 월납부액을 표시합니다.


**힌트 1:** - `ROUND(total_amount / 3, 0)` 등으로 단순 분할
- `WHERE total_amount >= 500000`



??? success "정답"
    ```sql
    SELECT
        order_number,
        total_amount,
        ROUND(total_amount / 3, 0) AS monthly_3m,
        ROUND(total_amount / 6, 0) AS monthly_6m,
        ROUND(total_amount / 12, 0) AS monthly_12m
    FROM orders
    WHERE total_amount >= 500000
      AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY total_amount DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | order_number | total_amount | monthly_3m | monthly_6m | monthly_12m |
    |---|---|---|---|---|
    | ORD-20201121-08810 | 50,867,500.00 | 16,955,833.00 | 8,477,917.00 | 4,238,958.00 |
    | ORD-20250305-32265 | 46,820,024.00 | 15,606,675.00 | 7,803,337.00 | 3,901,669.00 |
    | ORD-20200209-05404 | 43,677,500.00 | 14,559,167.00 | 7,279,583.00 | 3,639,792.00 |
    | ORD-20251218-37240 | 38,626,400.00 | 12,875,467.00 | 6,437,733.00 | 3,218,867.00 |
    | ORD-20220106-15263 | 37,987,600.00 | 12,662,533.00 | 6,331,267.00 | 3,165,633.00 |
    | ORD-20200820-07684 | 37,518,200.00 | 12,506,067.00 | 6,253,033.00 | 3,126,517.00 |
    | ORD-20220224-15869 | 35,397,700.00 | 11,799,233.00 | 5,899,617.00 | 2,949,808.00 |


---


### 9. NULL 생년월일 추정


birth_date가 NULL인 고객에게, 같은 등급(grade) 고객의 평균 출생 연도를 대입하세요.
고객명, 등급, 원래 birth_date, 추정 birth_year를 표시합니다.


**힌트 1:** - `AVG(CAST(SUBSTR(birth_date, 1, 4) AS INTEGER))`로 등급별 평균 출생 연도
- `LEFT JOIN` 또는 스칼라 서브쿼리로 NULL 고객에 적용



??? success "정답"
    ```sql
    WITH grade_avg_year AS (
        SELECT
            grade,
            ROUND(AVG(CAST(SUBSTR(birth_date, 1, 4) AS INTEGER)), 0) AS avg_birth_year
        FROM customers
        WHERE birth_date IS NOT NULL
        GROUP BY grade
    )
    SELECT
        c.id,
        c.name,
        c.grade,
        c.birth_date,
        gay.avg_birth_year AS estimated_birth_year
    FROM customers AS c
    INNER JOIN grade_avg_year AS gay ON c.grade = gay.grade
    WHERE c.birth_date IS NULL
    ORDER BY c.grade, c.id
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | id | name | grade | birth_date | estimated_birth_year |
    |---|---|---|---|---|
    | 7 | 김명자 | BRONZE | NULL | 1,988.00 |
    | 13 | 김정식 | BRONZE | NULL | 1,988.00 |
    | 14 | 윤순옥 | BRONZE | NULL | 1,988.00 |
    | 24 | 강민석 | BRONZE | NULL | 1,988.00 |
    | 36 | 윤지훈 | BRONZE | NULL | 1,988.00 |
    | 38 | 박준영 | BRONZE | NULL | 1,988.00 |
    | 42 | 최영진 | BRONZE | NULL | 1,988.00 |


---


### 10. 중복 위시리스트 찾기


wishlists 테이블에는 UNIQUE 제약이 있지만,
만약 중복이 있었다면 어떤 SQL로 찾고 가장 오래된 것만 남길 수 있을까요?
ROW_NUMBER로 같은 customer_id + product_id 중 가장 최근 것을 식별하세요.


**힌트 1:** - `ROW_NUMBER() OVER (PARTITION BY customer_id, product_id ORDER BY created_at)`
- `rn > 1`이면 삭제 대상



??? success "정답"
    ```sql
    WITH ranked AS (
        SELECT
            id,
            customer_id,
            product_id,
            created_at,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id, product_id
                ORDER BY created_at ASC
            ) AS rn
        FROM wishlists
    )
    SELECT id, customer_id, product_id, created_at, rn,
           CASE WHEN rn > 1 THEN 'DELETE' ELSE 'KEEP' END AS action
    FROM ranked
    WHERE customer_id IN (
        SELECT customer_id FROM wishlists
        GROUP BY customer_id
        HAVING COUNT(*) > 1
    )
    ORDER BY customer_id, product_id, rn
    LIMIT 30;
    ```


    **실행 결과** (총 30행 중 상위 7행)

    | id | customer_id | product_id | created_at | rn | action |
    |---|---|---|---|---|---|
    | 88 | 3 | 142 | 2020-10-21 05:28:28 | 1 | KEEP |
    | 1202 | 3 | 164 | 2018-12-05 10:45:35 | 1 | KEEP |
    | 1456 | 3 | 234 | 2025-06-24 10:23:47 | 1 | KEEP |
    | 996 | 19 | 4 | 2017-10-28 18:51:00 | 1 | KEEP |
    | 82 | 19 | 144 | 2024-09-29 00:02:22 | 1 | KEEP |
    | 1378 | 81 | 1 | 2017-10-25 09:20:52 | 1 | KEEP |
    | 1997 | 81 | 106 | 2023-02-11 22:00:20 | 1 | KEEP |


---


### 11. 가입 채널별 전환율


acquisition_channel별로 가입 고객 수와 첫 주문까지 도달한 고객 수,
전환율(%)을 계산하세요.


**힌트 1:** - `customers.acquisition_channel`로 그룹화
- `orders`에 1건이라도 있으면 전환된 것



??? success "정답"
    ```sql
    SELECT
        COALESCE(c.acquisition_channel, 'unknown') AS channel,
        COUNT(*) AS signup_count,
        COUNT(DISTINCT o.customer_id) AS converted_count,
        ROUND(100.0 * COUNT(DISTINCT o.customer_id) / COUNT(*), 1) AS conversion_rate_pct
    FROM customers AS c
    LEFT JOIN orders AS o
        ON c.id = o.customer_id
       AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY COALESCE(c.acquisition_channel, 'unknown')
    ORDER BY conversion_rate_pct DESC;
    ```


    **실행 결과** (5행)

    | channel | signup_count | converted_count | conversion_rate_pct |
    |---|---|---|---|
    | social | 8685 | 741 | 8.50 |
    | search_ad | 10,504 | 838 | 8.00 |
    | referral | 5134 | 384 | 7.50 |
    | direct | 3156 | 210 | 6.70 |
    | organic | 9656 | 620 | 6.40 |


---


### 12. Flow vs Stock 비교


상품별 재고 입출고 흐름(flow: 입고-출고 합계)과
현재 재고(stock: products.stock_qty)를 비교하세요.
차이가 있는 상품을 식별합니다.


**힌트 1:** - `inventory_transactions`에서 `SUM(quantity)` (quantity는 입고=양수, 출고=음수)
- `products.stock_qty`와 비교



??? success "정답"
    ```sql
    WITH flow AS (
        SELECT
            product_id,
            SUM(quantity) AS net_flow
        FROM inventory_transactions
        GROUP BY product_id
    )
    SELECT
        p.name AS product_name,
        p.stock_qty AS current_stock,
        f.net_flow AS calculated_stock,
        p.stock_qty - f.net_flow AS discrepancy
    FROM products AS p
    INNER JOIN flow AS f ON p.id = f.product_id
    WHERE p.stock_qty != f.net_flow
    ORDER BY ABS(p.stock_qty - f.net_flow) DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | product_name | current_stock | calculated_stock | discrepancy |
    |---|---|---|---|
    | 넷기어 GS316PP | 104 | 1590 | -1486 |
    | TP-Link TL-SG1016D 실버 | 275 | 1569 | -1294 |
    | LG 27UQ85R 블랙 | 26 | 1280 | -1254 |
    | CORSAIR RM1000x 화이트 | 58 | 1262 | -1204 |
    | 소니 WH-CH720N 실버 | 89 | 1259 | -1170 |
    | Razer Basilisk V3 Pro 35K 화이트 | 99 | 1268 | -1169 |
    | 로지텍 G PRO X SUPERLIGHT 2 화이트 | 152 | 1300 | -1148 |


---


### 13. 연속 동일 상태 주문


고객별로 3건 이상 연속으로 같은 status인 주문을 찾으세요.
LAG를 사용하여 이전 2건의 status와 비교합니다.


**힌트 1:** - `LAG(status, 1)`, `LAG(status, 2)` 사용
- 3건이 모두 같은 status이면 해당 행 표시



??? success "정답"
    ```sql
    WITH order_seq AS (
        SELECT
            customer_id,
            order_number,
            status,
            ordered_at,
            LAG(status, 1) OVER (PARTITION BY customer_id ORDER BY ordered_at) AS prev_1,
            LAG(status, 2) OVER (PARTITION BY customer_id ORDER BY ordered_at) AS prev_2
        FROM orders
    )
    SELECT
        os.customer_id,
        c.name AS customer_name,
        os.order_number,
        os.status,
        os.prev_1,
        os.prev_2,
        os.ordered_at
    FROM order_seq AS os
    INNER JOIN customers AS c ON os.customer_id = c.id
    WHERE os.status = os.prev_1
      AND os.status = os.prev_2
    ORDER BY os.customer_id, os.ordered_at
    LIMIT 30;
    ```


    **실행 결과** (총 30행 중 상위 7행)

    | customer_id | customer_name | order_number | status | prev_1 | prev_2 | ordered_at |
    |---|---|---|---|---|---|---|
    | 2 | 김경수 | ORD-20160830-00269 | confirmed | confirmed | confirmed | 2016-08-30 10:49:39 |
    | 2 | 김경수 | ORD-20160904-00274 | confirmed | confirmed | confirmed | 2016-09-04 08:47:04 |
    | 2 | 김경수 | ORD-20160915-00287 | confirmed | confirmed | confirmed | 2016-09-15 20:07:17 |
    | 2 | 김경수 | ORD-20161024-00334 | confirmed | confirmed | confirmed | 2016-10-24 12:13:06 |
    | 2 | 김경수 | ORD-20161101-00343 | confirmed | confirmed | confirmed | 2016-11-01 10:44:08 |
    | 2 | 김경수 | ORD-20170122-00444 | confirmed | confirmed | confirmed | 2017-01-22 08:39:07 |
    | 2 | 김경수 | ORD-20170305-00501 | confirmed | confirmed | confirmed | 2017-03-05 20:35:01 |


---


### 14. 카테고리별 매출 Top 3 상품


ROW_NUMBER를 사용하여 각 카테고리에서 매출 상위 3개 상품을 구하세요.
카테고리명, 순위, 상품명, 매출을 표시합니다.


**힌트 1:** - `ROW_NUMBER() OVER (PARTITION BY cat.id ORDER BY revenue DESC)`
- `WHERE rn <= 3`



??? success "정답"
    ```sql
    WITH product_revenue AS (
        SELECT
            cat.name AS category,
            cat.id AS category_id,
            p.name AS product_name,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
            ROW_NUMBER() OVER (
                PARTITION BY cat.id
                ORDER BY SUM(oi.quantity * oi.unit_price) DESC
            ) AS rn
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY cat.id, cat.name, p.id, p.name
    )
    SELECT category, rn AS rank, product_name, revenue
    FROM product_revenue
    WHERE rn <= 3
    ORDER BY category, rn;
    ```


    **실행 결과** (총 113행 중 상위 7행)

    | category | rank | product_name | revenue |
    |---|---|---|---|
    | 2in1 | 1 | 레노버 ThinkPad X1 2in1 실버 | 554,231,700.00 |
    | 2in1 | 2 | HP Envy x360 15 실버 | 326,727,400.00 |
    | 2in1 | 3 | HP Pavilion x360 14 블랙 | 319,615,200.00 |
    | AMD | 1 | AMD Ryzen 9 9900X | 452,187,900.00 |
    | AMD | 1 | MSI Radeon RX 7900 XTX GAMING X 화이트 | 585,793,600.00 |
    | AMD | 2 | AMD Ryzen 9 9900X | 149,725,400.00 |
    | AMD | 2 | ASUS Dual RX 9070 실버 | 515,058,400.00 |


---


### 15. 멘토링 페어 매칭


같은 부서 내에서 주니어(role='staff')와 시니어(role='manager')를
멘토-멘티 쌍으로 매칭하세요. 부서명, 멘티명, 멘토명을 표시합니다.


**힌트 1:** - `staff` 테이블을 self-join: `s1.department = s2.department`
- `s1.role = 'staff'` AND `s2.role = 'manager'`



??? success "정답"
    ```sql
    SELECT
        s1.department,
        s1.name AS mentee,
        s1.role AS mentee_role,
        s2.name AS mentor,
        s2.role AS mentor_role
    FROM staff AS s1
    INNER JOIN staff AS s2
        ON s1.department = s2.department
       AND s2.role = 'manager'
    WHERE s1.role = 'staff'
      AND s1.is_active = 1
      AND s2.is_active = 1
    ORDER BY s1.department, s1.name;
    ```


---


### 16. 클래식 리텐션 분석


가입 월(cohort) 기준으로, 가입 후 +1개월, +2개월, +3개월에
다시 주문한 고객 비율을 계산하세요.


**힌트 1:** - 코호트 = `SUBSTR(customers.created_at, 1, 7)`
- 각 주문의 "가입 후 경과 월수" 계산
- 조건부 `COUNT(DISTINCT CASE WHEN ... THEN customer_id END)`



??? success "정답"

    === "SQLite"
        ```sql
        WITH cohort AS (
            SELECT
                id AS customer_id,
                SUBSTR(created_at, 1, 7) AS signup_month,
                created_at
            FROM customers
            WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
        ),
        cohort_orders AS (
            SELECT
                co.signup_month,
                co.customer_id,
                CAST(
                    (CAST(SUBSTR(o.ordered_at, 1, 4) AS INTEGER) * 12
                     + CAST(SUBSTR(o.ordered_at, 6, 2) AS INTEGER))
                  - (CAST(SUBSTR(co.created_at, 1, 4) AS INTEGER) * 12
                     + CAST(SUBSTR(co.created_at, 6, 2) AS INTEGER))
                AS INTEGER) AS months_since_signup
            FROM cohort AS co
            INNER JOIN orders AS o
                ON co.customer_id = o.customer_id
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT
            signup_month,
            COUNT(DISTINCT customer_id) AS cohort_size,
            COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END) AS m1,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS m1_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END) AS m2,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS m2_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END) AS m3,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS m3_pct
        FROM cohort_orders
        GROUP BY signup_month
        ORDER BY signup_month;
        ```

    === "Oracle"
        ```sql
        WITH cohort AS (
            SELECT
                id AS customer_id,
                SUBSTR(created_at, 1, 7) AS signup_month,
                created_at
            FROM customers
            WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
        ),
        cohort_orders AS (
            SELECT
                co.signup_month,
                co.customer_id,
                (CAST(SUBSTR(o.ordered_at, 1, 4) AS NUMBER) * 12
                 + CAST(SUBSTR(o.ordered_at, 6, 2) AS NUMBER))
              - (CAST(SUBSTR(co.created_at, 1, 4) AS NUMBER) * 12
                 + CAST(SUBSTR(co.created_at, 6, 2) AS NUMBER)) AS months_since_signup
            FROM cohort co
            INNER JOIN orders o
                ON co.customer_id = o.customer_id
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT
            signup_month,
            COUNT(DISTINCT customer_id) AS cohort_size,
            COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END) AS m1,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS m1_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END) AS m2,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS m2_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END) AS m3,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS m3_pct
        FROM cohort_orders
        GROUP BY signup_month
        ORDER BY signup_month;
        ```

    === "SQL Server"
        ```sql
        WITH cohort AS (
            SELECT
                id AS customer_id,
                SUBSTRING(created_at, 1, 7) AS signup_month,
                created_at
            FROM customers
            WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
        ),
        cohort_orders AS (
            SELECT
                co.signup_month,
                co.customer_id,
                (CAST(SUBSTRING(o.ordered_at, 1, 4) AS INT) * 12
                 + CAST(SUBSTRING(o.ordered_at, 6, 2) AS INT))
              - (CAST(SUBSTRING(co.created_at, 1, 4) AS INT) * 12
                 + CAST(SUBSTRING(co.created_at, 6, 2) AS INT)) AS months_since_signup
            FROM cohort AS co
            INNER JOIN orders AS o
                ON co.customer_id = o.customer_id
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT
            signup_month,
            COUNT(DISTINCT customer_id) AS cohort_size,
            COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END) AS m1,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS m1_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END) AS m2,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS m2_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END) AS m3,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS m3_pct
        FROM cohort_orders
        GROUP BY signup_month
        ORDER BY signup_month;
        ```


    **실행 결과** (6행)

    | signup_month | cohort_size | m1 | m1_pct | m2 | m2_pct | m3 | m3_pct |
    |---|---|---|---|---|---|---|---|
    | 2024-01 | 28 | 3 | 10.70 | 5 | 17.90 | 4 | 14.30 |
    | 2024-02 | 26 | 7 | 26.90 | 3 | 11.50 | 5 | 19.20 |
    | 2024-03 | 44 | 10 | 22.70 | 11 | 25.00 | 2 | 4.50 |
    | 2024-04 | 26 | 4 | 15.40 | 4 | 15.40 | 2 | 7.70 |
    | 2024-05 | 24 | 4 | 16.70 | 7 | 29.20 | 2 | 8.30 |
    | 2024-06 | 36 | 4 | 11.10 | 4 | 11.10 | 6 | 16.70 |


---


### 17. 롤링 리텐션 분석


가입 월(cohort) 기준으로, N개월 이후에 "아무 때나" 주문한 고객 비율을 계산하세요.
클래식 리텐션과 달리 정확한 월이 아닌 N개월 이후 어떤 시점이든 포함합니다.


**힌트 1:** - `months_since_signup >= N` 조건으로 "N개월 이후"를 판별
- 클래식과 비교하면 항상 같거나 큰 값



??? success "정답"

    === "SQLite"
        ```sql
        WITH cohort AS (
            SELECT
                id AS customer_id,
                SUBSTR(created_at, 1, 7) AS signup_month,
                created_at
            FROM customers
            WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
        ),
        cohort_orders AS (
            SELECT
                co.signup_month,
                co.customer_id,
                CAST(
                    (CAST(SUBSTR(o.ordered_at, 1, 4) AS INTEGER) * 12
                     + CAST(SUBSTR(o.ordered_at, 6, 2) AS INTEGER))
                  - (CAST(SUBSTR(co.created_at, 1, 4) AS INTEGER) * 12
                     + CAST(SUBSTR(co.created_at, 6, 2) AS INTEGER))
                AS INTEGER) AS months_since_signup
            FROM cohort AS co
            INNER JOIN orders AS o
                ON co.customer_id = o.customer_id
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT
            signup_month,
            COUNT(DISTINCT customer_id) AS cohort_size,
            COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END) AS rolling_m1,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS rolling_m1_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END) AS rolling_m2,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS rolling_m2_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END) AS rolling_m3,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS rolling_m3_pct
        FROM cohort_orders
        GROUP BY signup_month
        ORDER BY signup_month;
        ```

    === "Oracle"
        ```sql
        WITH cohort AS (
            SELECT
                id AS customer_id,
                SUBSTR(created_at, 1, 7) AS signup_month,
                created_at
            FROM customers
            WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
        ),
        cohort_orders AS (
            SELECT
                co.signup_month,
                co.customer_id,
                (CAST(SUBSTR(o.ordered_at, 1, 4) AS NUMBER) * 12
                 + CAST(SUBSTR(o.ordered_at, 6, 2) AS NUMBER))
              - (CAST(SUBSTR(co.created_at, 1, 4) AS NUMBER) * 12
                 + CAST(SUBSTR(co.created_at, 6, 2) AS NUMBER)) AS months_since_signup
            FROM cohort co
            INNER JOIN orders o
                ON co.customer_id = o.customer_id
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT
            signup_month,
            COUNT(DISTINCT customer_id) AS cohort_size,
            COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END) AS rolling_m1,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS rolling_m1_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END) AS rolling_m2,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS rolling_m2_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END) AS rolling_m3,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS rolling_m3_pct
        FROM cohort_orders
        GROUP BY signup_month
        ORDER BY signup_month;
        ```

    === "SQL Server"
        ```sql
        WITH cohort AS (
            SELECT
                id AS customer_id,
                SUBSTRING(created_at, 1, 7) AS signup_month,
                created_at
            FROM customers
            WHERE created_at >= '2024-01-01' AND created_at < '2024-07-01'
        ),
        cohort_orders AS (
            SELECT
                co.signup_month,
                co.customer_id,
                (CAST(SUBSTRING(o.ordered_at, 1, 4) AS INT) * 12
                 + CAST(SUBSTRING(o.ordered_at, 6, 2) AS INT))
              - (CAST(SUBSTRING(co.created_at, 1, 4) AS INT) * 12
                 + CAST(SUBSTRING(co.created_at, 6, 2) AS INT)) AS months_since_signup
            FROM cohort AS co
            INNER JOIN orders AS o
                ON co.customer_id = o.customer_id
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT
            signup_month,
            COUNT(DISTINCT customer_id) AS cohort_size,
            COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END) AS rolling_m1,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 1 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS rolling_m1_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END) AS rolling_m2,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 2 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS rolling_m2_pct,
            COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END) AS rolling_m3,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN months_since_signup >= 3 THEN customer_id END)
                / COUNT(DISTINCT customer_id), 1) AS rolling_m3_pct
        FROM cohort_orders
        GROUP BY signup_month
        ORDER BY signup_month;
        ```


    **실행 결과** (6행)

    | signup_month | cohort_size | rolling_m1 | rolling_m1_pct | rolling_m2 | rolling_m2_pct | rolling_m3 | rolling_m3_pct |
    |---|---|---|---|---|---|---|---|
    | 2024-01 | 28 | 28 | 100.00 | 28 | 100.00 | 26 | 92.90 |
    | 2024-02 | 26 | 26 | 100.00 | 26 | 100.00 | 25 | 96.20 |
    | 2024-03 | 44 | 43 | 97.70 | 43 | 97.70 | 42 | 95.50 |
    | 2024-04 | 26 | 26 | 100.00 | 24 | 92.30 | 24 | 92.30 |
    | 2024-05 | 24 | 24 | 100.00 | 24 | 100.00 | 24 | 100.00 |
    | 2024-06 | 36 | 35 | 97.20 | 35 | 97.20 | 33 | 91.70 |


---


### 18. DAU/MAU 고착도


2024년 12월 기준으로 product_views의 일별 활성 고객(DAU)과
월간 활성 고객(MAU) 비율을 계산하세요. DAU/MAU가 고착도(Stickiness)입니다.


**힌트 1:** - DAU = 일별 `COUNT(DISTINCT customer_id)`
- MAU = 해당 월 전체 `COUNT(DISTINCT customer_id)` (서브쿼리)
- Stickiness = DAU / MAU



??? success "정답"
    ```sql
    WITH dau AS (
        SELECT
            SUBSTR(viewed_at, 1, 10) AS view_date,
            COUNT(DISTINCT customer_id) AS daily_active
        FROM product_views
        WHERE viewed_at LIKE '2024-12%'
        GROUP BY SUBSTR(viewed_at, 1, 10)
    ),
    mau AS (
        SELECT COUNT(DISTINCT customer_id) AS monthly_active
        FROM product_views
        WHERE viewed_at LIKE '2024-12%'
    )
    SELECT
        d.view_date,
        d.daily_active AS dau,
        m.monthly_active AS mau,
        ROUND(100.0 * d.daily_active / m.monthly_active, 2) AS stickiness_pct
    FROM dau AS d
    CROSS JOIN mau AS m
    ORDER BY d.view_date;
    ```


    **실행 결과** (총 31행 중 상위 7행)

    | view_date | dau | mau | stickiness_pct |
    |---|---|---|---|
    | 2024-12-01 | 94 | 1056 | 8.90 |
    | 2024-12-02 | 118 | 1056 | 11.17 |
    | 2024-12-03 | 111 | 1056 | 10.51 |
    | 2024-12-04 | 106 | 1056 | 10.04 |
    | 2024-12-05 | 109 | 1056 | 10.32 |
    | 2024-12-06 | 111 | 1056 | 10.51 |
    | 2024-12-07 | 102 | 1056 | 9.66 |


---


### 19. 7일 이동 평균 매출


2024년 12월의 일별 매출과 7일 이동 평균을 계산하세요.
`AVG() OVER (ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`를 사용합니다.


**힌트 1:** - 일별 매출을 먼저 집계
- `AVG(daily_revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`



??? success "정답"
    ```sql
    WITH daily_revenue AS (
        SELECT
            SUBSTR(ordered_at, 1, 10) AS order_date,
            ROUND(SUM(total_amount), 2) AS revenue
        FROM orders
        WHERE ordered_at LIKE '2024-12%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 10)
    )
    SELECT
        order_date,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2) AS moving_avg_7d
    FROM daily_revenue
    ORDER BY order_date;
    ```


    **실행 결과** (총 31행 중 상위 7행)

    | order_date | revenue | moving_avg_7d |
    |---|---|---|
    | 2024-12-01 | 10,287,445.00 | 10,287,445.00 |
    | 2024-12-02 | 11,732,557.00 | 11,010,001.00 |
    | 2024-12-03 | 11,867,860.00 | 11,295,954.00 |
    | 2024-12-04 | 11,198,303.00 | 11,271,541.25 |
    | 2024-12-05 | 5,489,585.00 | 10,115,150.00 |
    | 2024-12-06 | 15,937,500.00 | 11,085,541.67 |
    | 2024-12-07 | 15,895,514.00 | 11,772,680.57 |


---


### 20. 3개월 이동 평균 월매출


월별 매출과 3개월 이동 평균을 계산하세요.
최근 24개월 데이터를 사용합니다.


**힌트 1:** - `AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`



??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2024-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 0) AS moving_avg_3m
    FROM monthly
    ORDER BY year_month;
    ```


    **실행 결과** (총 24행 중 상위 7행)

    | year_month | revenue | moving_avg_3m |
    |---|---|---|
    | 2024-01 | 288,908,320.00 | 288,908,320.00 |
    | 2024-02 | 403,127,749.00 | 346,018,035.00 |
    | 2024-03 | 519,844,502.00 | 403,960,190.00 |
    | 2024-04 | 451,877,581.00 | 458,283,277.00 |
    | 2024-05 | 425,264,478.00 | 465,662,187.00 |
    | 2024-06 | 362,715,211.00 | 413,285,757.00 |
    | 2024-07 | 343,929,897.00 | 377,303,195.00 |


---


### 21. 연도 내 누적 월매출


각 연도별로 월별 매출과 연도 내 누적 매출을 계산하세요.
PARTITION BY year로 연도마다 누적이 리셋됩니다.


**힌트 1:** - `SUM(revenue) OVER (PARTITION BY year ORDER BY month)`



??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        SUBSTR(ordered_at, 1, 7) AS year_month,
        ROUND(SUM(total_amount), 0) AS monthly_revenue,
        ROUND(SUM(SUM(total_amount)) OVER (
            PARTITION BY SUBSTR(ordered_at, 1, 4)
            ORDER BY SUBSTR(ordered_at, 1, 7)
        ), 0) AS cumulative_revenue
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
      AND ordered_at >= '2023-01-01'
    GROUP BY SUBSTR(ordered_at, 1, 4), SUBSTR(ordered_at, 1, 7)
    ORDER BY year_month;
    ```


    **실행 결과** (총 36행 중 상위 7행)

    | year | year_month | monthly_revenue | cumulative_revenue |
    |---|---|---|---|
    | 2023 | 2023-01 | 270,083,587.00 | 270,083,587.00 |
    | 2023 | 2023-02 | 327,431,648.00 | 597,515,235.00 |
    | 2023 | 2023-03 | 477,735,354.00 | 1,075,250,589.00 |
    | 2023 | 2023-04 | 396,849,049.00 | 1,472,099,638.00 |
    | 2023 | 2023-05 | 349,749,072.00 | 1,821,848,710.00 |
    | 2023 | 2023-06 | 279,698,633.00 | 2,101,547,343.00 |
    | 2023 | 2023-07 | 312,983,148.00 | 2,414,530,491.00 |


---


### 22. 파레토 분석 (고객)


매출의 80%를 생성하는 고객이 전체의 몇 %인지 분석하세요.
고객별 매출 누적 비율과 고객 순위를 표시합니다.


**힌트 1:** - 고객별 매출을 내림차순 정렬 후 누적 SUM
- 전체 매출 대비 누적 비율 계산
- 80% 도달 시점의 고객 수 / 전체 고객 수



??? success "정답"
    ```sql
    WITH customer_revenue AS (
        SELECT
            customer_id,
            ROUND(SUM(total_amount), 2) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    ranked AS (
        SELECT
            customer_id,
            revenue,
            SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative_revenue,
            SUM(revenue) OVER () AS total_revenue,
            ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rank,
            COUNT(*) OVER () AS total_customers
        FROM customer_revenue
    )
    SELECT
        rank,
        revenue,
        ROUND(100.0 * cumulative_revenue / total_revenue, 2) AS cumulative_pct,
        ROUND(100.0 * rank / total_customers, 2) AS customer_pct,
        CASE
            WHEN 100.0 * cumulative_revenue / total_revenue <= 80 THEN 'Top 80%'
            ELSE 'Remaining'
        END AS pareto_group
    FROM ranked
    WHERE rank <= 50 OR 100.0 * cumulative_revenue / total_revenue BETWEEN 78 AND 82
    ORDER BY rank;
    ```


    **실행 결과** (총 167행 중 상위 7행)

    | rank | revenue | cumulative_pct | customer_pct | pareto_group |
    |---|---|---|---|---|
    | 1 | 403,448,758.00 | 1.16 | 0.04 | Top 80% |
    | 2 | 366,385,931.00 | 2.21 | 0.07 | Top 80% |
    | 3 | 253,180,338.00 | 2.94 | 0.11 | Top 80% |
    | 4 | 244,604,910.00 | 3.65 | 0.14 | Top 80% |
    | 5 | 235,775,349.00 | 4.32 | 0.18 | Top 80% |
    | 6 | 234,708,853.00 | 5.00 | 0.21 | Top 80% |
    | 7 | 230,165,991.00 | 5.66 | 0.25 | Top 80% |


---


### 23. 구매 주기 분석


고객별 연속 주문 간 평균 일수(구매 주기)를 계산하세요.
LAG로 이전 주문일을 가져와 JULIANDAY 차이를 구합니다.


**힌트 1:** - `LAG(ordered_at) OVER (PARTITION BY customer_id ORDER BY ordered_at)`
- `JULIANDAY(ordered_at) - JULIANDAY(prev_ordered_at)`
- `AVG()`로 고객별 평균 주기



??? success "정답"

    === "SQLite"
        ```sql
        WITH order_gaps AS (
            SELECT
                customer_id,
                ordered_at,
                LAG(ordered_at) OVER (
                    PARTITION BY customer_id ORDER BY ordered_at
                ) AS prev_ordered_at
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT
            c.name AS customer_name,
            c.grade,
            COUNT(*) AS gap_count,
            ROUND(AVG(JULIANDAY(og.ordered_at) - JULIANDAY(og.prev_ordered_at)), 1) AS avg_cycle_days,
            MIN(CAST(JULIANDAY(og.ordered_at) - JULIANDAY(og.prev_ordered_at) AS INTEGER)) AS min_days,
            MAX(CAST(JULIANDAY(og.ordered_at) - JULIANDAY(og.prev_ordered_at) AS INTEGER)) AS max_days
        FROM order_gaps AS og
        INNER JOIN customers AS c ON og.customer_id = c.id
        WHERE og.prev_ordered_at IS NOT NULL
        GROUP BY og.customer_id, c.name, c.grade
        HAVING COUNT(*) >= 3
        ORDER BY avg_cycle_days ASC
        LIMIT 20;
        ```

    === "Oracle"
        ```sql
        WITH order_gaps AS (
            SELECT
                customer_id,
                ordered_at,
                LAG(ordered_at) OVER (
                    PARTITION BY customer_id ORDER BY ordered_at
                ) AS prev_ordered_at
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT
            c.name AS customer_name,
            c.grade,
            COUNT(*) AS gap_count,
            ROUND(AVG(CAST(og.ordered_at AS DATE) - CAST(og.prev_ordered_at AS DATE)), 1) AS avg_cycle_days,
            MIN(CAST(og.ordered_at AS DATE) - CAST(og.prev_ordered_at AS DATE)) AS min_days,
            MAX(CAST(og.ordered_at AS DATE) - CAST(og.prev_ordered_at AS DATE)) AS max_days
        FROM order_gaps og
        INNER JOIN customers c ON og.customer_id = c.id
        WHERE og.prev_ordered_at IS NOT NULL
        GROUP BY og.customer_id, c.name, c.grade
        HAVING COUNT(*) >= 3
        ORDER BY avg_cycle_days ASC
        FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        WITH order_gaps AS (
            SELECT
                customer_id,
                ordered_at,
                LAG(ordered_at) OVER (
                    PARTITION BY customer_id ORDER BY ordered_at
                ) AS prev_ordered_at
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT TOP 20
            c.name AS customer_name,
            c.grade,
            COUNT(*) AS gap_count,
            ROUND(AVG(CAST(DATEDIFF(DAY, og.prev_ordered_at, og.ordered_at) AS FLOAT)), 1) AS avg_cycle_days,
            MIN(DATEDIFF(DAY, og.prev_ordered_at, og.ordered_at)) AS min_days,
            MAX(DATEDIFF(DAY, og.prev_ordered_at, og.ordered_at)) AS max_days
        FROM order_gaps AS og
        INNER JOIN customers AS c ON og.customer_id = c.id
        WHERE og.prev_ordered_at IS NOT NULL
        GROUP BY og.customer_id, c.name, c.grade
        HAVING COUNT(*) >= 3
        ORDER BY avg_cycle_days ASC;
        ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer_name | grade | gap_count | avg_cycle_days | min_days | max_days |
    |---|---|---|---|---|---|
    | 김병철 | VIP | 341 | 10.10 | 0 | 112 |
    | 박정수 | VIP | 302 | 10.80 | 0 | 88 |
    | 이미정 | VIP | 218 | 12.00 | 0 | 74 |
    | 김승현 | VIP | 6 | 12.10 | 0 | 26 |
    | 정유진 | VIP | 222 | 12.30 | 0 | 125 |
    | 이지영 | GOLD | 3 | 12.40 | 3 | 20 |
    | 강명자 | VIP | 248 | 12.90 | 0 | 102 |


---


### 24. 첫 구매 후 재구매율


첫 주문 후 30일/60일/90일 이내에 재구매한 고객 비율을 구하세요.


**힌트 1:** - 고객별 첫 주문일 = `MIN(ordered_at)`
- 두 번째 주문이 첫 주문 + N일 이내인지 확인



??? success "정답"

    === "SQLite"
        ```sql
        WITH first_order AS (
            SELECT
                customer_id,
                MIN(ordered_at) AS first_ordered_at
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
            GROUP BY customer_id
        ),
        repeat_order AS (
            SELECT
                fo.customer_id,
                fo.first_ordered_at,
                MIN(o.ordered_at) AS second_ordered_at
            FROM first_order AS fo
            INNER JOIN orders AS o
                ON fo.customer_id = o.customer_id
               AND o.ordered_at > fo.first_ordered_at
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
            GROUP BY fo.customer_id, fo.first_ordered_at
        )
        SELECT
            COUNT(DISTINCT fo.customer_id) AS total_customers,
            COUNT(DISTINCT CASE
                WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 30
                THEN fo.customer_id
            END) AS repurchase_30d,
            ROUND(100.0 * COUNT(DISTINCT CASE
                WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 30
                THEN fo.customer_id
            END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_30d_pct,
            COUNT(DISTINCT CASE
                WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 60
                THEN fo.customer_id
            END) AS repurchase_60d,
            ROUND(100.0 * COUNT(DISTINCT CASE
                WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 60
                THEN fo.customer_id
            END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_60d_pct,
            COUNT(DISTINCT CASE
                WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 90
                THEN fo.customer_id
            END) AS repurchase_90d,
            ROUND(100.0 * COUNT(DISTINCT CASE
                WHEN JULIANDAY(ro.second_ordered_at) - JULIANDAY(fo.first_ordered_at) <= 90
                THEN fo.customer_id
            END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_90d_pct
        FROM first_order AS fo
        LEFT JOIN repeat_order AS ro ON fo.customer_id = ro.customer_id;
        ```

    === "Oracle"
        ```sql
        WITH first_order AS (
            SELECT
                customer_id,
                MIN(ordered_at) AS first_ordered_at
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
            GROUP BY customer_id
        ),
        repeat_order AS (
            SELECT
                fo.customer_id,
                fo.first_ordered_at,
                MIN(o.ordered_at) AS second_ordered_at
            FROM first_order fo
            INNER JOIN orders o
                ON fo.customer_id = o.customer_id
               AND o.ordered_at > fo.first_ordered_at
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
            GROUP BY fo.customer_id, fo.first_ordered_at
        )
        SELECT
            COUNT(DISTINCT fo.customer_id) AS total_customers,
            COUNT(DISTINCT CASE
                WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 30
                THEN fo.customer_id
            END) AS repurchase_30d,
            ROUND(100.0 * COUNT(DISTINCT CASE
                WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 30
                THEN fo.customer_id
            END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_30d_pct,
            COUNT(DISTINCT CASE
                WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 60
                THEN fo.customer_id
            END) AS repurchase_60d,
            ROUND(100.0 * COUNT(DISTINCT CASE
                WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 60
                THEN fo.customer_id
            END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_60d_pct,
            COUNT(DISTINCT CASE
                WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 90
                THEN fo.customer_id
            END) AS repurchase_90d,
            ROUND(100.0 * COUNT(DISTINCT CASE
                WHEN CAST(ro.second_ordered_at AS DATE) - CAST(fo.first_ordered_at AS DATE) <= 90
                THEN fo.customer_id
            END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_90d_pct
        FROM first_order fo
        LEFT JOIN repeat_order ro ON fo.customer_id = ro.customer_id;
        ```

    === "SQL Server"
        ```sql
        WITH first_order AS (
            SELECT
                customer_id,
                MIN(ordered_at) AS first_ordered_at
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
            GROUP BY customer_id
        ),
        repeat_order AS (
            SELECT
                fo.customer_id,
                fo.first_ordered_at,
                MIN(o.ordered_at) AS second_ordered_at
            FROM first_order AS fo
            INNER JOIN orders AS o
                ON fo.customer_id = o.customer_id
               AND o.ordered_at > fo.first_ordered_at
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
            GROUP BY fo.customer_id, fo.first_ordered_at
        )
        SELECT
            COUNT(DISTINCT fo.customer_id) AS total_customers,
            COUNT(DISTINCT CASE
                WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 30
                THEN fo.customer_id
            END) AS repurchase_30d,
            ROUND(100.0 * COUNT(DISTINCT CASE
                WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 30
                THEN fo.customer_id
            END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_30d_pct,
            COUNT(DISTINCT CASE
                WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 60
                THEN fo.customer_id
            END) AS repurchase_60d,
            ROUND(100.0 * COUNT(DISTINCT CASE
                WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 60
                THEN fo.customer_id
            END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_60d_pct,
            COUNT(DISTINCT CASE
                WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 90
                THEN fo.customer_id
            END) AS repurchase_90d,
            ROUND(100.0 * COUNT(DISTINCT CASE
                WHEN DATEDIFF(DAY, fo.first_ordered_at, ro.second_ordered_at) <= 90
                THEN fo.customer_id
            END) / COUNT(DISTINCT fo.customer_id), 1) AS repurchase_90d_pct
        FROM first_order AS fo
        LEFT JOIN repeat_order AS ro ON fo.customer_id = ro.customer_id;
        ```


    **실행 결과** (1행)

    | total_customers | repurchase_30d | repurchase_30d_pct | repurchase_60d | repurchase_60d_pct | repurchase_90d | repurchase_90d_pct |
    |---|---|---|---|---|---|---|
    | 2793 | 704 | 25.20 | 1016 | 36.40 | 1229 | 44.00 |


---


### 25. 포인트 잔액 불일치 탐지


point_transactions의 SUM(amount)과 customers.point_balance가
일치하지 않는 고객을 찾으세요.


**힌트 1:** - `SUM(pt.amount)` 고객별 합계
- `customers.point_balance`와 비교



??? success "정답"
    ```sql
    WITH point_sum AS (
        SELECT
            customer_id,
            SUM(amount) AS calculated_balance
        FROM point_transactions
        GROUP BY customer_id
    )
    SELECT
        c.id AS customer_id,
        c.name,
        c.point_balance AS stored_balance,
        COALESCE(ps.calculated_balance, 0) AS calculated_balance,
        c.point_balance - COALESCE(ps.calculated_balance, 0) AS drift
    FROM customers AS c
    LEFT JOIN point_sum AS ps ON c.id = ps.customer_id
    WHERE c.point_balance != COALESCE(ps.calculated_balance, 0)
    ORDER BY ABS(c.point_balance - COALESCE(ps.calculated_balance, 0)) DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer_id | name | stored_balance | calculated_balance | drift |
    |---|---|---|---|---|
    | 97 | 김병철 | 3,518,880 | 2,332,397 | 1,186,483 |
    | 226 | 박정수 | 3,955,828 | 2,863,301 | 1,092,527 |
    | 162 | 강명자 | 2,450,166 | 1,521,994 | 928,172 |
    | 549 | 이미정 | 2,276,622 | 1,449,259 | 827,363 |
    | 227 | 김성민 | 2,297,542 | 1,516,187 | 781,355 |
    | 3 | 김민재 | 1,564,015 | 859,898 | 704,117 |
    | 98 | 이영자 | 2,218,590 | 1,514,981 | 703,609 |


---


### 26. 프로모션 리프트 분석


프로모션 기간 중 일평균 매출과 프로모션 외 기간의 일평균 매출을 비교하세요.
프로모션별 리프트(%)를 계산합니다.


**힌트 1:** - `promotions.started_at` ~ `ended_at` 기간의 전체 매출 / 기간 일수
- 비프로모션 기간의 전체 매출 / 기간 일수



??? success "정답"

    === "SQLite"
        ```sql
        WITH promo_daily AS (
            SELECT
                pr.id AS promo_id,
                pr.name AS promo_name,
                ROUND(SUM(o.total_amount), 0) AS promo_revenue,
                CAST(JULIANDAY(pr.ended_at) - JULIANDAY(pr.started_at) + 1 AS INTEGER) AS promo_days
            FROM promotions AS pr
            INNER JOIN orders AS o
                ON o.ordered_at BETWEEN pr.started_at AND pr.ended_at
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
            WHERE pr.started_at >= '2024-01-01'
            GROUP BY pr.id, pr.name, pr.started_at, pr.ended_at
        ),
        overall_daily AS (
            SELECT
                ROUND(SUM(total_amount) / 365.0, 0) AS avg_daily_revenue
            FROM orders
            WHERE ordered_at LIKE '2024%'
              AND status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT
            pd.promo_name,
            pd.promo_revenue,
            pd.promo_days,
            ROUND(1.0 * pd.promo_revenue / pd.promo_days, 0) AS promo_avg_daily,
            od.avg_daily_revenue AS baseline_avg_daily,
            ROUND(100.0 * ((1.0 * pd.promo_revenue / pd.promo_days) - od.avg_daily_revenue)
                / od.avg_daily_revenue, 1) AS lift_pct
        FROM promo_daily AS pd
        CROSS JOIN overall_daily AS od
        ORDER BY lift_pct DESC
        LIMIT 15;
        ```

    === "Oracle"
        ```sql
        WITH promo_daily AS (
            SELECT
                pr.id AS promo_id,
                pr.name AS promo_name,
                ROUND(SUM(o.total_amount), 0) AS promo_revenue,
                CAST(pr.ended_at AS DATE) - CAST(pr.started_at AS DATE) + 1 AS promo_days
            FROM promotions pr
            INNER JOIN orders o
                ON o.ordered_at BETWEEN pr.started_at AND pr.ended_at
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
            WHERE pr.started_at >= '2024-01-01'
            GROUP BY pr.id, pr.name, pr.started_at, pr.ended_at
        ),
        overall_daily AS (
            SELECT
                ROUND(SUM(total_amount) / 365.0, 0) AS avg_daily_revenue
            FROM orders
            WHERE ordered_at LIKE '2024%'
              AND status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT
            pd.promo_name,
            pd.promo_revenue,
            pd.promo_days,
            ROUND(1.0 * pd.promo_revenue / pd.promo_days, 0) AS promo_avg_daily,
            od.avg_daily_revenue AS baseline_avg_daily,
            ROUND(100.0 * ((1.0 * pd.promo_revenue / pd.promo_days) - od.avg_daily_revenue)
                / od.avg_daily_revenue, 1) AS lift_pct
        FROM promo_daily pd
        CROSS JOIN overall_daily od
        ORDER BY lift_pct DESC
        FETCH FIRST 15 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        WITH promo_daily AS (
            SELECT
                pr.id AS promo_id,
                pr.name AS promo_name,
                ROUND(SUM(o.total_amount), 0) AS promo_revenue,
                DATEDIFF(DAY, pr.started_at, pr.ended_at) + 1 AS promo_days
            FROM promotions AS pr
            INNER JOIN orders AS o
                ON o.ordered_at BETWEEN pr.started_at AND pr.ended_at
               AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
            WHERE pr.started_at >= '2024-01-01'
            GROUP BY pr.id, pr.name, pr.started_at, pr.ended_at
        ),
        overall_daily AS (
            SELECT
                ROUND(SUM(total_amount) / 365.0, 0) AS avg_daily_revenue
            FROM orders
            WHERE ordered_at LIKE '2024%'
              AND status NOT IN ('cancelled', 'returned', 'return_requested')
        )
        SELECT TOP 15
            pd.promo_name,
            pd.promo_revenue,
            pd.promo_days,
            ROUND(1.0 * pd.promo_revenue / pd.promo_days, 0) AS promo_avg_daily,
            od.avg_daily_revenue AS baseline_avg_daily,
            ROUND(100.0 * ((1.0 * pd.promo_revenue / pd.promo_days) - od.avg_daily_revenue)
                / od.avg_daily_revenue, 1) AS lift_pct
        FROM promo_daily AS pd
        CROSS JOIN overall_daily AS od
        ORDER BY lift_pct DESC;
        ```


    **실행 결과** (총 15행 중 상위 7행)

    | promo_name | promo_revenue | promo_days | promo_avg_daily | baseline_avg_daily | lift_pct |
    |---|---|---|---|---|---|
    | 연말 감사 세일 2025 | 416,811,391.00 | 15 | 27,787,426.00 | 14,012,174.00 | 98.30 |
    | 깜짝 특가 | 74,259,378.00 | 3 | 24,753,126.00 | 14,012,174.00 | 76.70 |
    | 봄맞이 세일 2025 | 311,900,316.00 | 15 | 20,793,354.00 | 14,012,174.00 | 48.40 |
    | 추석 선물 세일 2024 | 225,867,067.00 | 11 | 20,533,370.00 | 14,012,174.00 | 46.50 |
    | 신학기 노트북 특가 2025 | 373,010,414.00 | 22 | 16,955,019.00 | 14,012,174.00 | 21.00 |
    | 게이밍 기어 페스타 2025 | 131,978,627.00 | 8 | 16,497,328.00 | 14,012,174.00 | 17.70 |
    | 신학기 노트북 특가 2024 | 350,818,175.00 | 22 | 15,946,281.00 | 14,012,174.00 | 13.80 |


---


### 27. 카테고리 교차 판매 분석


같은 주문에서 가장 자주 함께 구매되는 카테고리 쌍을 찾으세요.


**힌트 1:** - 주문별 카테고리 목록을 먼저 구한 뒤
- Self-join으로 모든 카테고리 쌍 생성 (c1.id < c2.id로 중복 제거)



??? success "정답"
    ```sql
    WITH order_categories AS (
        SELECT DISTINCT
            oi.order_id,
            p.category_id,
            cat.name AS category_name
        FROM order_items AS oi
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        oc1.category_name AS category_1,
        oc2.category_name AS category_2,
        COUNT(*) AS co_occurrence
    FROM order_categories AS oc1
    INNER JOIN order_categories AS oc2
        ON oc1.order_id = oc2.order_id
       AND oc1.category_id < oc2.category_id
    GROUP BY oc1.category_name, oc2.category_name
    ORDER BY co_occurrence DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | category_1 | category_2 | co_occurrence |
    |---|---|---|
    | 파워서플라이(PSU) | 케이스 | 3139 |
    | SSD | 케이스 | 2999 |
    | SSD | 파워서플라이(PSU) | 2990 |
    | AMD | 케이스 | 2209 |
    | AMD | 파워서플라이(PSU) | 2182 |
    | DDR5 | 케이스 | 1768 |
    | Intel | 케이스 | 1757 |


---


### 28. 등급 하락 궤적 추적


customer_grade_history에서 연속 하락(downgrade)이 2회 이상인 고객을 찾으세요.
예: VIP -> GOLD -> SILVER


**힌트 1:** - `LAG(reason) OVER (PARTITION BY customer_id ORDER BY changed_at)` 사용
- 현재와 이전 모두 'downgrade'인 행을 찾기



??? success "정답"
    ```sql
    WITH grade_seq AS (
        SELECT
            customer_id,
            old_grade,
            new_grade,
            reason,
            changed_at,
            LAG(reason) OVER (
                PARTITION BY customer_id ORDER BY changed_at
            ) AS prev_reason,
            LAG(old_grade) OVER (
                PARTITION BY customer_id ORDER BY changed_at
            ) AS prev_old_grade
        FROM customer_grade_history
    )
    SELECT
        gs.customer_id,
        c.name AS customer_name,
        gs.prev_old_grade AS grade_before,
        gs.old_grade AS grade_mid,
        gs.new_grade AS grade_after,
        gs.changed_at
    FROM grade_seq AS gs
    INNER JOIN customers AS c ON gs.customer_id = c.id
    WHERE gs.reason = 'downgrade'
      AND gs.prev_reason = 'downgrade'
    ORDER BY gs.customer_id, gs.changed_at;
    ```


    **실행 결과** (총 292행 중 상위 7행)

    | customer_id | customer_name | grade_before | grade_mid | grade_after | changed_at |
    |---|---|---|---|---|---|
    | 4 | 진정자 | VIP | GOLD | SILVER | 2024-01-01 00:00:00 |
    | 8 | 성민석 | VIP | GOLD | SILVER | 2022-01-01 00:00:00 |
    | 10 | 박지훈 | GOLD | SILVER | BRONZE | 2021-01-01 00:00:00 |
    | 12 | 장준서 | VIP | GOLD | SILVER | 2023-01-01 00:00:00 |
    | 14 | 윤순옥 | VIP | GOLD | SILVER | 2020-01-01 00:00:00 |
    | 14 | 윤순옥 | GOLD | SILVER | BRONZE | 2021-01-01 00:00:00 |
    | 15 | 강은서 | VIP | GOLD | SILVER | 2023-01-01 00:00:00 |


---


### 29. 택배사별 월별 배송 성과 및 추이


택배사별 월별 평균 배송 소요일과 전월 대비 변화를 보여주세요.


**힌트 1:** - `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)` 로 배송일
- `LAG(avg_days) OVER (PARTITION BY carrier ORDER BY month)` 로 전월 비교



??? success "정답"

    === "SQLite"
        ```sql
        WITH monthly_carrier AS (
            SELECT
                carrier,
                SUBSTR(shipped_at, 1, 7) AS ship_month,
                COUNT(*) AS delivery_count,
                ROUND(AVG(JULIANDAY(delivered_at) - JULIANDAY(shipped_at)), 2) AS avg_days
            FROM shipping
            WHERE delivered_at IS NOT NULL
              AND shipped_at IS NOT NULL
              AND shipped_at >= '2024-01-01'
            GROUP BY carrier, SUBSTR(shipped_at, 1, 7)
        )
        SELECT
            carrier,
            ship_month,
            delivery_count,
            avg_days,
            LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month) AS prev_month_days,
            ROUND(avg_days - LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month), 2) AS mom_change
        FROM monthly_carrier
        ORDER BY carrier, ship_month;
        ```

    === "Oracle"
        ```sql
        WITH monthly_carrier AS (
            SELECT
                carrier,
                SUBSTR(shipped_at, 1, 7) AS ship_month,
                COUNT(*) AS delivery_count,
                ROUND(AVG(CAST(delivered_at AS DATE) - CAST(shipped_at AS DATE)), 2) AS avg_days
            FROM shipping
            WHERE delivered_at IS NOT NULL
              AND shipped_at IS NOT NULL
              AND shipped_at >= '2024-01-01'
            GROUP BY carrier, SUBSTR(shipped_at, 1, 7)
        )
        SELECT
            carrier,
            ship_month,
            delivery_count,
            avg_days,
            LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month) AS prev_month_days,
            ROUND(avg_days - LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month), 2) AS mom_change
        FROM monthly_carrier
        ORDER BY carrier, ship_month;
        ```

    === "SQL Server"
        ```sql
        WITH monthly_carrier AS (
            SELECT
                carrier,
                SUBSTRING(shipped_at, 1, 7) AS ship_month,
                COUNT(*) AS delivery_count,
                ROUND(AVG(CAST(DATEDIFF(DAY, shipped_at, delivered_at) AS FLOAT)), 2) AS avg_days
            FROM shipping
            WHERE delivered_at IS NOT NULL
              AND shipped_at IS NOT NULL
              AND shipped_at >= '2024-01-01'
            GROUP BY carrier, SUBSTRING(shipped_at, 1, 7)
        )
        SELECT
            carrier,
            ship_month,
            delivery_count,
            avg_days,
            LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month) AS prev_month_days,
            ROUND(avg_days - LAG(avg_days) OVER (PARTITION BY carrier ORDER BY ship_month), 2) AS mom_change
        FROM monthly_carrier
        ORDER BY carrier, ship_month;
        ```


    **실행 결과** (총 96행 중 상위 7행)

    | carrier | ship_month | delivery_count | avg_days | prev_month_days | mom_change |
    |---|---|---|---|---|---|
    | CJ대한통운 | 2024-01 | 126 | 2.50 | NULL | NULL |
    | CJ대한통운 | 2024-02 | 172 | 2.55 | 2.50 | 0.05 |
    | CJ대한통운 | 2024-03 | 218 | 2.54 | 2.55 | -0.01 |
    | CJ대한통운 | 2024-04 | 192 | 2.51 | 2.54 | -0.03 |
    | CJ대한통운 | 2024-05 | 171 | 2.33 | 2.51 | -0.18 |
    | CJ대한통운 | 2024-06 | 160 | 2.44 | 2.33 | 0.11 |
    | CJ대한통운 | 2024-07 | 150 | 2.51 | 2.44 | 0.07 |


---


### 30. 3일 연속 매출 증가 구간


일별 매출이 3일 연속 증가한 구간을 찾으세요.
시작일, 종료일, 연속 일수를 표시합니다.


**힌트 1:** - LAG로 전일 매출 비교하여 증가 여부 플래그
- 증가 플래그가 끊기는 지점을 그룹 경계로 사용 (island 패턴)
- 그룹별 연속 일수 >= 3 필터



??? success "정답"

    === "SQLite"
        ```sql
        WITH daily AS (
            SELECT
                SUBSTR(ordered_at, 1, 10) AS order_date,
                ROUND(SUM(total_amount), 2) AS revenue
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
              AND ordered_at >= '2024-01-01'
            GROUP BY SUBSTR(ordered_at, 1, 10)
        ),
        with_flag AS (
            SELECT
                order_date,
                revenue,
                LAG(revenue) OVER (ORDER BY order_date) AS prev_revenue,
                CASE
                    WHEN revenue > LAG(revenue) OVER (ORDER BY order_date) THEN 1
                    ELSE 0
                END AS is_increase
            FROM daily
        ),
        with_group AS (
            SELECT
                order_date,
                revenue,
                is_increase,
                SUM(CASE WHEN is_increase = 0 THEN 1 ELSE 0 END) OVER (
                    ORDER BY order_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS grp
            FROM with_flag
        )
        SELECT
            MIN(order_date) AS start_date,
            MAX(order_date) AS end_date,
            COUNT(*) AS streak_days
        FROM with_group
        WHERE is_increase = 1
        GROUP BY grp
        HAVING COUNT(*) >= 3
        ORDER BY start_date;
        ```

    === "Oracle"
        ```sql
        WITH daily AS (
            SELECT
                SUBSTR(ordered_at, 1, 10) AS order_date,
                ROUND(SUM(total_amount), 2) AS revenue
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
              AND ordered_at >= '2024-01-01'
            GROUP BY SUBSTR(ordered_at, 1, 10)
        ),
        with_flag AS (
            SELECT
                order_date,
                revenue,
                LAG(revenue) OVER (ORDER BY order_date) AS prev_revenue,
                CASE
                    WHEN revenue > LAG(revenue) OVER (ORDER BY order_date) THEN 1
                    ELSE 0
                END AS is_increase
            FROM daily
        ),
        with_group AS (
            SELECT
                order_date,
                revenue,
                is_increase,
                SUM(CASE WHEN is_increase = 0 THEN 1 ELSE 0 END) OVER (
                    ORDER BY order_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS grp
            FROM with_flag
        )
        SELECT
            MIN(order_date) AS start_date,
            MAX(order_date) AS end_date,
            COUNT(*) AS streak_days
        FROM with_group
        WHERE is_increase = 1
        GROUP BY grp
        HAVING COUNT(*) >= 3
        ORDER BY start_date;
        ```

    === "SQL Server"
        ```sql
        WITH daily AS (
            SELECT
                SUBSTRING(ordered_at, 1, 10) AS order_date,
                ROUND(SUM(total_amount), 2) AS revenue
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
              AND ordered_at >= '2024-01-01'
            GROUP BY SUBSTRING(ordered_at, 1, 10)
        ),
        with_flag AS (
            SELECT
                order_date,
                revenue,
                LAG(revenue) OVER (ORDER BY order_date) AS prev_revenue,
                CASE
                    WHEN revenue > LAG(revenue) OVER (ORDER BY order_date) THEN 1
                    ELSE 0
                END AS is_increase
            FROM daily
        ),
        with_group AS (
            SELECT
                order_date,
                revenue,
                is_increase,
                SUM(CASE WHEN is_increase = 0 THEN 1 ELSE 0 END) OVER (
                    ORDER BY order_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS grp
            FROM with_flag
        )
        SELECT
            MIN(order_date) AS start_date,
            MAX(order_date) AS end_date,
            COUNT(*) AS streak_days
        FROM with_group
        WHERE is_increase = 1
        GROUP BY grp
        HAVING COUNT(*) >= 3
        ORDER BY start_date;
        ```


    **실행 결과** (총 25행 중 상위 7행)

    | start_date | end_date | streak_days |
    |---|---|---|
    | 2024-01-04 | 2024-01-07 | 4 |
    | 2024-01-17 | 2024-01-21 | 5 |
    | 2024-01-26 | 2024-01-28 | 3 |
    | 2024-03-04 | 2024-03-06 | 3 |
    | 2024-03-27 | 2024-03-29 | 3 |
    | 2024-05-14 | 2024-05-16 | 3 |
    | 2024-06-20 | 2024-06-23 | 4 |


---


### 31. 연속 월 주문 고객


5개월 이상 연속으로 매월 주문한 고객을 찾으세요.
고객명, 연속 시작월, 연속 종료월, 연속 개월 수를 표시합니다.


**힌트 1:** - 고객별 월별 주문 여부를 먼저 구함
- 연속 월을 감지하려면 "month_number - ROW_NUMBER" 패턴 사용
- 같은 차이값을 가진 행들이 연속 구간



??? success "정답"

    === "SQLite"
        ```sql
        WITH customer_months AS (
            SELECT DISTINCT
                customer_id,
                SUBSTR(ordered_at, 1, 7) AS order_month,
                CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER) * 12
                    + CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) AS month_num
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        ),
        with_rn AS (
            SELECT
                customer_id,
                order_month,
                month_num,
                month_num - ROW_NUMBER() OVER (
                    PARTITION BY customer_id ORDER BY month_num
                ) AS grp
            FROM customer_months
        ),
        streaks AS (
            SELECT
                customer_id,
                MIN(order_month) AS start_month,
                MAX(order_month) AS end_month,
                COUNT(*) AS consecutive_months
            FROM with_rn
            GROUP BY customer_id, grp
            HAVING COUNT(*) >= 5
        )
        SELECT
            c.name AS customer_name,
            c.grade,
            s.start_month,
            s.end_month,
            s.consecutive_months
        FROM streaks AS s
        INNER JOIN customers AS c ON s.customer_id = c.id
        ORDER BY s.consecutive_months DESC, c.name
        LIMIT 20;
        ```

    === "Oracle"
        ```sql
        WITH customer_months AS (
            SELECT DISTINCT
                customer_id,
                SUBSTR(ordered_at, 1, 7) AS order_month,
                CAST(SUBSTR(ordered_at, 1, 4) AS NUMBER) * 12
                    + CAST(SUBSTR(ordered_at, 6, 2) AS NUMBER) AS month_num
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        ),
        with_rn AS (
            SELECT
                customer_id,
                order_month,
                month_num,
                month_num - ROW_NUMBER() OVER (
                    PARTITION BY customer_id ORDER BY month_num
                ) AS grp
            FROM customer_months
        ),
        streaks AS (
            SELECT
                customer_id,
                MIN(order_month) AS start_month,
                MAX(order_month) AS end_month,
                COUNT(*) AS consecutive_months
            FROM with_rn
            GROUP BY customer_id, grp
            HAVING COUNT(*) >= 5
        )
        SELECT
            c.name AS customer_name,
            c.grade,
            s.start_month,
            s.end_month,
            s.consecutive_months
        FROM streaks s
        INNER JOIN customers c ON s.customer_id = c.id
        ORDER BY s.consecutive_months DESC, c.name
        FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        WITH customer_months AS (
            SELECT DISTINCT
                customer_id,
                SUBSTRING(ordered_at, 1, 7) AS order_month,
                CAST(SUBSTRING(ordered_at, 1, 4) AS INT) * 12
                    + CAST(SUBSTRING(ordered_at, 6, 2) AS INT) AS month_num
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        ),
        with_rn AS (
            SELECT
                customer_id,
                order_month,
                month_num,
                month_num - ROW_NUMBER() OVER (
                    PARTITION BY customer_id ORDER BY month_num
                ) AS grp
            FROM customer_months
        ),
        streaks AS (
            SELECT
                customer_id,
                MIN(order_month) AS start_month,
                MAX(order_month) AS end_month,
                COUNT(*) AS consecutive_months
            FROM with_rn
            GROUP BY customer_id, grp
            HAVING COUNT(*) >= 5
        )
        SELECT TOP 20
            c.name AS customer_name,
            c.grade,
            s.start_month,
            s.end_month,
            s.consecutive_months
        FROM streaks AS s
        INNER JOIN customers AS c ON s.customer_id = c.id
        ORDER BY s.consecutive_months DESC, c.name;
        ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer_name | grade | start_month | end_month | consecutive_months |
    |---|---|---|---|---|
    | 김병철 | VIP | 2016-07 | 2022-05 | 71 |
    | 이미정 | VIP | 2018-10 | 2022-07 | 46 |
    | 박정수 | VIP | 2017-01 | 2020-09 | 45 |
    | 김성민 | VIP | 2017-05 | 2020-07 | 39 |
    | 강상철 | VIP | 2020-10 | 2023-11 | 38 |
    | 정유진 | VIP | 2018-04 | 2021-03 | 36 |
    | 김경희 | GOLD | 2017-11 | 2020-09 | 35 |


---


### 32. 세션 정의 (30분 갭)


product_views를 세션으로 그룹화하세요 (같은 고객의 조회 간 30분 이상 간격이면 새 세션).
고객별 세션 수, 세션당 평균 조회 수를 구하세요.


**힌트 1:** - `LAG(viewed_at)`로 이전 조회 시간
- 30분 = `(JULIANDAY(현재) - JULIANDAY(이전)) * 24 * 60 > 30`
- `SUM(is_new_session) OVER (...)`로 세션 번호 부여



??? success "정답"

    === "SQLite"
        ```sql
        WITH view_gaps AS (
            SELECT
                customer_id,
                viewed_at,
                CASE
                    WHEN LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ) IS NULL THEN 1
                    WHEN (JULIANDAY(viewed_at) - JULIANDAY(LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ))) * 24 * 60 > 30 THEN 1
                    ELSE 0
                END AS is_new_session
            FROM product_views
            WHERE customer_id <= 500
        ),
        with_session AS (
            SELECT
                customer_id,
                viewed_at,
                SUM(is_new_session) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS session_id
            FROM view_gaps
        ),
        session_stats AS (
            SELECT
                customer_id,
                session_id,
                COUNT(*) AS views_in_session
            FROM with_session
            GROUP BY customer_id, session_id
        )
        SELECT
            COUNT(DISTINCT customer_id) AS total_customers,
            COUNT(*) AS total_sessions,
            ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 1) AS avg_sessions_per_customer,
            ROUND(AVG(views_in_session), 1) AS avg_views_per_session
        FROM session_stats;
        ```

    === "Oracle"
        ```sql
        WITH view_gaps AS (
            SELECT
                customer_id,
                viewed_at,
                CASE
                    WHEN LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ) IS NULL THEN 1
                    WHEN (CAST(viewed_at AS DATE) - CAST(LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ) AS DATE)) * 24 * 60 > 30 THEN 1
                    ELSE 0
                END AS is_new_session
            FROM product_views
            WHERE customer_id <= 500
        ),
        with_session AS (
            SELECT
                customer_id,
                viewed_at,
                SUM(is_new_session) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS session_id
            FROM view_gaps
        ),
        session_stats AS (
            SELECT
                customer_id,
                session_id,
                COUNT(*) AS views_in_session
            FROM with_session
            GROUP BY customer_id, session_id
        )
        SELECT
            COUNT(DISTINCT customer_id) AS total_customers,
            COUNT(*) AS total_sessions,
            ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 1) AS avg_sessions_per_customer,
            ROUND(AVG(views_in_session), 1) AS avg_views_per_session
        FROM session_stats;
        ```

    === "SQL Server"
        ```sql
        WITH view_gaps AS (
            SELECT
                customer_id,
                viewed_at,
                CASE
                    WHEN LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ) IS NULL THEN 1
                    WHEN DATEDIFF(MINUTE, LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ), viewed_at) > 30 THEN 1
                    ELSE 0
                END AS is_new_session
            FROM product_views
            WHERE customer_id <= 500
        ),
        with_session AS (
            SELECT
                customer_id,
                viewed_at,
                SUM(is_new_session) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS session_id
            FROM view_gaps
        ),
        session_stats AS (
            SELECT
                customer_id,
                session_id,
                COUNT(*) AS views_in_session
            FROM with_session
            GROUP BY customer_id, session_id
        )
        SELECT
            COUNT(DISTINCT customer_id) AS total_customers,
            COUNT(*) AS total_sessions,
            ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 1) AS avg_sessions_per_customer,
            ROUND(AVG(views_in_session), 1) AS avg_views_per_session
        FROM session_stats;
        ```


    **실행 결과** (1행)

    | total_customers | total_sessions | avg_sessions_per_customer | avg_views_per_session |
    |---|---|---|---|
    | 267 | 65,248 | 244.40 | 1.10 |


---


### 33. 세션 재정의 (10분 갭)


c11-32와 동일하되 세션 갭을 10분으로 변경하세요.
30분 갭 결과와 비교하여 세션 수가 어떻게 달라지는지 확인합니다.


**힌트 1:** - 30분을 10분으로 변경하기만 하면 됨
- 세션이 더 많이 분할될 것



??? success "정답"

    === "SQLite"
        ```sql
        WITH view_gaps AS (
            SELECT
                customer_id,
                viewed_at,
                CASE
                    WHEN LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ) IS NULL THEN 1
                    WHEN (JULIANDAY(viewed_at) - JULIANDAY(LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ))) * 24 * 60 > 10 THEN 1
                    ELSE 0
                END AS is_new_session
            FROM product_views
            WHERE customer_id <= 500
        ),
        with_session AS (
            SELECT
                customer_id,
                viewed_at,
                SUM(is_new_session) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS session_id
            FROM view_gaps
        ),
        session_stats AS (
            SELECT
                customer_id,
                session_id,
                COUNT(*) AS views_in_session
            FROM with_session
            GROUP BY customer_id, session_id
        )
        SELECT
            COUNT(DISTINCT customer_id) AS total_customers,
            COUNT(*) AS total_sessions,
            ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 1) AS avg_sessions_per_customer,
            ROUND(AVG(views_in_session), 1) AS avg_views_per_session
        FROM session_stats;
        ```

    === "Oracle"
        ```sql
        WITH view_gaps AS (
            SELECT
                customer_id,
                viewed_at,
                CASE
                    WHEN LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ) IS NULL THEN 1
                    WHEN (CAST(viewed_at AS DATE) - CAST(LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ) AS DATE)) * 24 * 60 > 10 THEN 1
                    ELSE 0
                END AS is_new_session
            FROM product_views
            WHERE customer_id <= 500
        ),
        with_session AS (
            SELECT
                customer_id,
                viewed_at,
                SUM(is_new_session) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS session_id
            FROM view_gaps
        ),
        session_stats AS (
            SELECT
                customer_id,
                session_id,
                COUNT(*) AS views_in_session
            FROM with_session
            GROUP BY customer_id, session_id
        )
        SELECT
            COUNT(DISTINCT customer_id) AS total_customers,
            COUNT(*) AS total_sessions,
            ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 1) AS avg_sessions_per_customer,
            ROUND(AVG(views_in_session), 1) AS avg_views_per_session
        FROM session_stats;
        ```

    === "SQL Server"
        ```sql
        WITH view_gaps AS (
            SELECT
                customer_id,
                viewed_at,
                CASE
                    WHEN LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ) IS NULL THEN 1
                    WHEN DATEDIFF(MINUTE, LAG(viewed_at) OVER (
                        PARTITION BY customer_id ORDER BY viewed_at
                    ), viewed_at) > 10 THEN 1
                    ELSE 0
                END AS is_new_session
            FROM product_views
            WHERE customer_id <= 500
        ),
        with_session AS (
            SELECT
                customer_id,
                viewed_at,
                SUM(is_new_session) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS session_id
            FROM view_gaps
        ),
        session_stats AS (
            SELECT
                customer_id,
                session_id,
                COUNT(*) AS views_in_session
            FROM with_session
            GROUP BY customer_id, session_id
        )
        SELECT
            COUNT(DISTINCT customer_id) AS total_customers,
            COUNT(*) AS total_sessions,
            ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 1) AS avg_sessions_per_customer,
            ROUND(AVG(views_in_session), 1) AS avg_views_per_session
        FROM session_stats;
        ```


    **실행 결과** (1행)

    | total_customers | total_sessions | avg_sessions_per_customer | avg_views_per_session |
    |---|---|---|---|
    | 267 | 67,538 | 253.00 | 1.00 |


---


### 34. 등급별 주문 금액 중앙값


고객 등급별 주문 금액의 중앙값(median)을 계산하세요.
SQLite에는 MEDIAN 함수가 없으므로 NTILE 또는 ROW_NUMBER로 구현합니다.


**힌트 1:** - `ROW_NUMBER()` OVER (PARTITION BY grade ORDER BY total_amount)
- 전체 건수의 절반 위치가 중앙값
- `COUNT(*) OVER (PARTITION BY grade)`로 전체 건수 파악



??? success "정답"
    ```sql
    WITH grade_orders AS (
        SELECT
            c.grade,
            o.total_amount,
            ROW_NUMBER() OVER (PARTITION BY c.grade ORDER BY o.total_amount) AS rn,
            COUNT(*) OVER (PARTITION BY c.grade) AS cnt
        FROM orders AS o
        INNER JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        grade,
        ROUND(AVG(total_amount), 2) AS median_amount
    FROM grade_orders
    WHERE rn IN (cnt / 2, cnt / 2 + 1)
    GROUP BY grade
    ORDER BY
        CASE grade
            WHEN 'VIP' THEN 1 WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3 WHEN 'BRONZE' THEN 4
        END;
    ```


    **실행 결과** (4행)

    | grade | median_amount |
    |---|---|
    | VIP | 481,750.00 |
    | GOLD | 456,200.00 |
    | SILVER | 423,000.00 |
    | BRONZE | 317,400.00 |


---


### 35. 택배사별 배송일 중앙값


택배사별 배송 소요일의 중앙값을 계산하세요.


**힌트 1:** - `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)`로 배송일 계산
- `ROW_NUMBER()`로 순위를 매긴 후 중앙 위치의 값 추출



??? success "정답"

    === "SQLite"
        ```sql
        WITH delivery_days AS (
            SELECT
                carrier,
                ROUND(JULIANDAY(delivered_at) - JULIANDAY(shipped_at), 1) AS days,
                ROW_NUMBER() OVER (PARTITION BY carrier ORDER BY JULIANDAY(delivered_at) - JULIANDAY(shipped_at)) AS rn,
                COUNT(*) OVER (PARTITION BY carrier) AS cnt
            FROM shipping
            WHERE delivered_at IS NOT NULL
              AND shipped_at IS NOT NULL
        )
        SELECT
            carrier,
            ROUND(AVG(days), 2) AS median_days
        FROM delivery_days
        WHERE rn IN (cnt / 2, cnt / 2 + 1)
        GROUP BY carrier
        ORDER BY median_days;
        ```

    === "Oracle"
        ```sql
        WITH delivery_days AS (
            SELECT
                carrier,
                ROUND(CAST(delivered_at AS DATE) - CAST(shipped_at AS DATE), 1) AS days,
                ROW_NUMBER() OVER (PARTITION BY carrier ORDER BY CAST(delivered_at AS DATE) - CAST(shipped_at AS DATE)) AS rn,
                COUNT(*) OVER (PARTITION BY carrier) AS cnt
            FROM shipping
            WHERE delivered_at IS NOT NULL
              AND shipped_at IS NOT NULL
        )
        SELECT
            carrier,
            ROUND(AVG(days), 2) AS median_days
        FROM delivery_days
        WHERE rn IN (TRUNC(cnt / 2), TRUNC(cnt / 2) + 1)
        GROUP BY carrier
        ORDER BY median_days;
        ```

    === "SQL Server"
        ```sql
        WITH delivery_days AS (
            SELECT
                carrier,
                ROUND(CAST(DATEDIFF(DAY, shipped_at, delivered_at) AS FLOAT), 1) AS days,
                ROW_NUMBER() OVER (PARTITION BY carrier ORDER BY DATEDIFF(DAY, shipped_at, delivered_at)) AS rn,
                COUNT(*) OVER (PARTITION BY carrier) AS cnt
            FROM shipping
            WHERE delivered_at IS NOT NULL
              AND shipped_at IS NOT NULL
        )
        SELECT
            carrier,
            ROUND(AVG(days), 2) AS median_days
        FROM delivery_days
        WHERE rn IN (cnt / 2, cnt / 2 + 1)
        GROUP BY carrier
        ORDER BY median_days;
        ```


    **실행 결과** (4행)

    | carrier | median_days |
    |---|---|
    | CJ대한통운 | 3.00 |
    | 로젠택배 | 3.00 |
    | 우체국택배 | 3.00 |
    | 한진택배 | 3.00 |


---


### 36. 디바이스별 퍼널 이탈 분석


device_type(desktop/mobile/tablet)별로
조회 -> 장바구니 -> 구매 퍼널의 각 단계별 전환율과 이탈률을 구하세요.


**힌트 1:** - `product_views.device_type`으로 디바이스 구분
- 각 단계의 고유 고객 수를 device_type별로 집계
- 이탈률 = 1 - 전환율



??? success "정답"
    ```sql
    WITH view_step AS (
        SELECT
            device_type,
            COUNT(DISTINCT customer_id) AS viewers
        FROM product_views
        GROUP BY device_type
    ),
    cart_step AS (
        SELECT
            pv.device_type,
            COUNT(DISTINCT c.customer_id) AS carters
        FROM product_views AS pv
        INNER JOIN carts AS c ON pv.customer_id = c.customer_id
        INNER JOIN cart_items AS ci ON c.id = ci.cart_id AND pv.product_id = ci.product_id
        GROUP BY pv.device_type
    ),
    purchase_step AS (
        SELECT
            pv.device_type,
            COUNT(DISTINCT o.customer_id) AS buyers
        FROM product_views AS pv
        INNER JOIN orders AS o ON pv.customer_id = o.customer_id
        INNER JOIN order_items AS oi ON o.id = oi.order_id AND pv.product_id = oi.product_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY pv.device_type
    )
    SELECT
        vs.device_type,
        vs.viewers,
        COALESCE(cs.carters, 0) AS carters,
        ROUND(100.0 * COALESCE(cs.carters, 0) / vs.viewers, 2) AS view_to_cart_pct,
        COALESCE(ps.buyers, 0) AS buyers,
        ROUND(100.0 * COALESCE(ps.buyers, 0) / NULLIF(COALESCE(cs.carters, 0), 0), 2) AS cart_to_buy_pct,
        ROUND(100.0 * COALESCE(ps.buyers, 0) / vs.viewers, 2) AS view_to_buy_pct
    FROM view_step AS vs
    LEFT JOIN cart_step AS cs ON vs.device_type = cs.device_type
    LEFT JOIN purchase_step AS ps ON vs.device_type = ps.device_type
    ORDER BY vs.device_type;
    ```


    **실행 결과** (3행)

    | device_type | viewers | carters | view_to_cart_pct | buyers | cart_to_buy_pct | view_to_buy_pct |
    |---|---|---|---|---|---|---|
    | desktop | 3658 | 486 | 13.29 | 2710 | 557.61 | 74.08 |
    | mobile | 3660 | 513 | 14.02 | 2707 | 527.68 | 73.96 |
    | tablet | 3385 | 201 | 5.94 | 2301 | 1,144.78 | 67.98 |


---


### 37. 채널 기여도 분석


product_views의 referrer_source별로 조회수와 최종 구매 전환 수를 구하세요.
다중 채널 고객의 경우 마지막 접촉(last-touch) 기준으로 크레딧을 부여합니다.


**힌트 1:** - 고객별 마지막 referrer_source를 먼저 구함 (최근 product_view)
- 해당 채널에 전환 크레딧 부여



??? success "정답"
    ```sql
    WITH last_touch AS (
        SELECT
            pv.customer_id,
            pv.referrer_source,
            ROW_NUMBER() OVER (
                PARTITION BY pv.customer_id
                ORDER BY pv.viewed_at DESC
            ) AS rn
        FROM product_views AS pv
        INNER JOIN orders AS o ON pv.customer_id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    channel_views AS (
        SELECT
            referrer_source,
            COUNT(*) AS total_views,
            COUNT(DISTINCT customer_id) AS unique_viewers
        FROM product_views
        GROUP BY referrer_source
    ),
    channel_conversions AS (
        SELECT
            referrer_source,
            COUNT(DISTINCT customer_id) AS conversions
        FROM last_touch
        WHERE rn = 1
        GROUP BY referrer_source
    )
    SELECT
        cv.referrer_source,
        cv.total_views,
        cv.unique_viewers,
        COALESCE(cc.conversions, 0) AS last_touch_conversions,
        ROUND(100.0 * COALESCE(cc.conversions, 0) / cv.unique_viewers, 2) AS conversion_rate_pct
    FROM channel_views AS cv
    LEFT JOIN channel_conversions AS cc ON cv.referrer_source = cc.referrer_source
    ORDER BY last_touch_conversions DESC;
    ```


    **실행 결과** (6행)

    | referrer_source | total_views | unique_viewers | last_touch_conversions | conversion_rate_pct |
    |---|---|---|---|---|
    | search | 114,520 | 3652 | 995 | 27.25 |
    | direct | 65,716 | 3603 | 541 | 15.02 |
    | ad | 49,030 | 3549 | 411 | 11.58 |
    | recommendation | 49,429 | 3544 | 405 | 11.43 |
    | social | 32,707 | 3402 | 291 | 8.55 |
    | email | 16,469 | 2929 | 150 | 5.12 |


---


### 38. 활성일 아일랜드 탐지


고객별 product_views에서 연속 활성일(island)을 찾으세요.
예: 고객이 월/화/수 조회 -> 목 미조회 -> 금/토 조회이면 2개 아일랜드(3일, 2일).


**힌트 1:** - 고객별 조회 날짜를 `DISTINCT`로 추출
- `DATE - ROW_NUMBER` 패턴으로 연속 날짜 그룹화
- 그룹별 MIN/MAX/COUNT



??? success "정답"

    === "SQLite"
        ```sql
        WITH active_days AS (
            SELECT DISTINCT
                customer_id,
                SUBSTR(viewed_at, 1, 10) AS view_date
            FROM product_views
            WHERE customer_id <= 200
        ),
        with_rn AS (
            SELECT
                customer_id,
                view_date,
                JULIANDAY(view_date) - ROW_NUMBER() OVER (
                    PARTITION BY customer_id ORDER BY view_date
                ) AS grp
            FROM active_days
        ),
        islands AS (
            SELECT
                customer_id,
                MIN(view_date) AS island_start,
                MAX(view_date) AS island_end,
                COUNT(*) AS island_days
            FROM with_rn
            GROUP BY customer_id, grp
            HAVING COUNT(*) >= 3
        )
        SELECT
            c.name AS customer_name,
            i.island_start,
            i.island_end,
            i.island_days
        FROM islands AS i
        INNER JOIN customers AS c ON i.customer_id = c.id
        ORDER BY i.island_days DESC, c.name
        LIMIT 20;
        ```

    === "Oracle"
        ```sql
        WITH active_days AS (
            SELECT DISTINCT
                customer_id,
                SUBSTR(viewed_at, 1, 10) AS view_date
            FROM product_views
            WHERE customer_id <= 200
        ),
        with_rn AS (
            SELECT
                customer_id,
                view_date,
                CAST(view_date AS DATE) - ROW_NUMBER() OVER (
                    PARTITION BY customer_id ORDER BY view_date
                ) AS grp
            FROM active_days
        ),
        islands AS (
            SELECT
                customer_id,
                MIN(view_date) AS island_start,
                MAX(view_date) AS island_end,
                COUNT(*) AS island_days
            FROM with_rn
            GROUP BY customer_id, grp
            HAVING COUNT(*) >= 3
        )
        SELECT
            c.name AS customer_name,
            i.island_start,
            i.island_end,
            i.island_days
        FROM islands i
        INNER JOIN customers c ON i.customer_id = c.id
        ORDER BY i.island_days DESC, c.name
        FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        WITH active_days AS (
            SELECT DISTINCT
                customer_id,
                SUBSTRING(viewed_at, 1, 10) AS view_date
            FROM product_views
            WHERE customer_id <= 200
        ),
        with_rn AS (
            SELECT
                customer_id,
                view_date,
                DATEADD(DAY, -ROW_NUMBER() OVER (
                    PARTITION BY customer_id ORDER BY view_date
                ), CAST(view_date AS DATE)) AS grp
            FROM active_days
        ),
        islands AS (
            SELECT
                customer_id,
                MIN(view_date) AS island_start,
                MAX(view_date) AS island_end,
                COUNT(*) AS island_days
            FROM with_rn
            GROUP BY customer_id, grp
            HAVING COUNT(*) >= 3
        )
        SELECT TOP 20
            c.name AS customer_name,
            i.island_start,
            i.island_end,
            i.island_days
        FROM islands AS i
        INNER JOIN customers AS c ON i.customer_id = c.id
        ORDER BY i.island_days DESC, c.name;
        ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer_name | island_start | island_end | island_days |
    |---|---|---|---|
    | 이영자 | 2016-01-09 | 2016-02-17 | 40 |
    | 김병철 | 2020-02-28 | 2020-03-25 | 27 |
    | 김민재 | 2016-03-05 | 2016-03-29 | 25 |
    | 김병철 | 2017-10-13 | 2017-11-06 | 25 |
    | 이영자 | 2016-04-18 | 2016-05-12 | 25 |
    | 이영철 | 2018-02-19 | 2018-03-15 | 25 |
    | 강명자 | 2021-08-30 | 2021-09-21 | 23 |


---


### 39. 월간 종합 대시보드


한 쿼리로 2024년 월별 종합 대시보드를 만드세요:
매출, 주문 수, 신규 고객 수, 활성 고객 수, 평균 주문 금액,
전월 대비 매출 증감률, 매출 1위 상품명.


**힌트 1:** - 주문/고객/상품 통계를 각각 CTE로 준비
- 월 기준으로 모두 JOIN
- LAG로 전월 대비 증감률
- ROW_NUMBER로 월별 매출 1위 상품



??? success "정답"
    ```sql
    WITH monthly_orders AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            COUNT(*) AS order_count,
            ROUND(SUM(total_amount), 0) AS revenue,
            ROUND(AVG(total_amount), 0) AS avg_order_value,
            COUNT(DISTINCT customer_id) AS active_customers
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    ),
    new_customers AS (
        SELECT
            SUBSTR(created_at, 1, 7) AS year_month,
            COUNT(*) AS new_customer_count
        FROM customers
        WHERE created_at LIKE '2024%'
        GROUP BY SUBSTR(created_at, 1, 7)
    ),
    top_products AS (
        SELECT
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            p.name AS product_name,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS product_revenue,
            ROW_NUMBER() OVER (
                PARTITION BY SUBSTR(o.ordered_at, 1, 7)
                ORDER BY SUM(oi.quantity * oi.unit_price) DESC
            ) AS rn
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(o.ordered_at, 1, 7), p.id, p.name
    ),
    with_growth AS (
        SELECT
            mo.year_month,
            mo.revenue,
            mo.order_count,
            COALESCE(nc.new_customer_count, 0) AS new_customers,
            mo.active_customers,
            mo.avg_order_value,
            LAG(mo.revenue) OVER (ORDER BY mo.year_month) AS prev_revenue,
            ROUND(100.0 * (mo.revenue - LAG(mo.revenue) OVER (ORDER BY mo.year_month))
                / NULLIF(LAG(mo.revenue) OVER (ORDER BY mo.year_month), 0), 1) AS mom_growth_pct,
            tp.product_name AS top_product
        FROM monthly_orders AS mo
        LEFT JOIN new_customers AS nc ON mo.year_month = nc.year_month
        LEFT JOIN top_products AS tp ON mo.year_month = tp.year_month AND tp.rn = 1
    )
    SELECT
        year_month,
        revenue,
        order_count,
        new_customers,
        active_customers,
        avg_order_value,
        mom_growth_pct,
        top_product
    FROM with_growth
    ORDER BY year_month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | year_month | revenue | order_count | new_customers | active_customers | avg_order_value | mom_growth_pct | top_product |
    |---|---|---|---|---|---|---|---|
    | 2024-01 | 288,908,320.00 | 314 | 52 | 269 | 920,090.00 | NULL | Razer Blade 18 블랙 |
    | 2024-02 | 403,127,749.00 | 416 | 48 | 335 | 969,057.00 | 39.50 | Razer Blade 16 실버 |
    | 2024-03 | 519,844,502.00 | 555 | 71 | 421 | 936,657.00 | 29.00 | Razer Blade 16 실버 |
    | 2024-04 | 451,877,581.00 | 466 | 53 | 353 | 969,694.00 | -13.10 | ASUS ROG Swift PG32UCDM 실버 |
    | 2024-05 | 425,264,478.00 | 385 | 43 | 315 | 1,104,583.00 | -5.90 | Razer Blade 18 블랙 |
    | 2024-06 | 362,715,211.00 | 389 | 68 | 324 | 932,430.00 | -14.70 | ASUS ROG Strix Scar 16 |
    | 2024-07 | 343,929,897.00 | 381 | 62 | 311 | 902,703.00 | -5.20 | Razer Blade 18 블랙 |


---


### 40. JSON 스펙 조회


products 테이블의 specs(JSON) 칼럼에서 CPU 정보를 추출하세요.
specs가 NULL이 아닌 상품의 이름과 CPU 정보를 표시합니다.


**힌트 1:** - SQLite: `JSON_EXTRACT(specs, '$.cpu')` 사용
- PostgreSQL: `specs->>'cpu'` 사용
- `WHERE specs IS NOT NULL` 필터



??? success "정답"

    === "SQLite"
        ```sql
        SELECT
            name,
            brand,
            price,
            JSON_EXTRACT(specs, '$.cpu') AS cpu,
            JSON_EXTRACT(specs, '$.ram') AS ram,
            JSON_EXTRACT(specs, '$.storage') AS storage
        FROM products
        WHERE specs IS NOT NULL
          AND JSON_EXTRACT(specs, '$.cpu') IS NOT NULL
        ORDER BY price DESC
        LIMIT 20;
        ```

    === "MySQL"
        ```sql
        SELECT
            name,
            brand,
            price,
            JSON_EXTRACT(specs, '$.cpu') AS cpu,
            JSON_EXTRACT(specs, '$.ram') AS ram,
            JSON_EXTRACT(specs, '$.storage') AS storage
        FROM products
        WHERE specs IS NOT NULL
          AND JSON_EXTRACT(specs, '$.cpu') IS NOT NULL
        ORDER BY price DESC
        LIMIT 20;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            name,
            brand,
            price,
            specs->>'cpu' AS cpu,
            specs->>'ram' AS ram,
            specs->>'storage' AS storage
        FROM products
        WHERE specs IS NOT NULL
          AND specs->>'cpu' IS NOT NULL
        ORDER BY price DESC
        LIMIT 20;
        ```

    === "Oracle"
        ```sql
        SELECT
            name,
            brand,
            price,
            JSON_VALUE(specs, '$.cpu') AS cpu,
            JSON_VALUE(specs, '$.ram') AS ram,
            JSON_VALUE(specs, '$.storage') AS storage
        FROM products
        WHERE specs IS NOT NULL
          AND JSON_VALUE(specs, '$.cpu') IS NOT NULL
        ORDER BY price DESC
        FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        SELECT TOP 20
            name,
            brand,
            price,
            JSON_VALUE(specs, '$.cpu') AS cpu,
            JSON_VALUE(specs, '$.ram') AS ram,
            JSON_VALUE(specs, '$.storage') AS storage
        FROM products
        WHERE specs IS NOT NULL
          AND JSON_VALUE(specs, '$.cpu') IS NOT NULL
        ORDER BY price DESC;
        ```


    **실행 결과** (총 20행 중 상위 7행)

    | name | brand | price | cpu | ram | storage |
    |---|---|---|---|---|---|
    | MacBook Air 15 M3 실버 | Apple | 5,481,100.00 | Intel Core i9-13900H | 8GB | 256GB |
    | Razer Blade 18 블랙 | Razer | 4,353,100.00 | Intel Core i7-13700H | 8GB | 1024GB |
    | Razer Blade 16 실버 | Razer | 3,702,900.00 | AMD Ryzen 9 7945HX | 32GB | 512GB |
    | ASUS ROG Strix G16CH 화이트 | ASUS | 3,671,500.00 | AMD Ryzen 5 7600X | 16GB | 2048GB |
    | ASUS ROG Zephyrus G16 | ASUS | 3,429,900.00 | Apple M3 | 16GB | 512GB |
    | ASUS ROG Strix GT35 | ASUS | 3,296,800.00 | Intel Core i7-13700K | 64GB | 2048GB |
    | Razer Blade 18 블랙 | Razer | 2,987,500.00 | Apple M3 | 8GB | 256GB |


---
