# 서브쿼리와 데이터 변환

!!! info "사용 테이블"

    `categories` — 카테고리 (부모-자식 계층)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `payments` — 결제 (방법, 금액, 상태)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `reviews` — 리뷰 (평점, 내용)  

    `returns` — 반품/교환 (사유, 상태)  

    `wishlists` — 위시리스트 (고객-상품)  



!!! abstract "학습 범위"

    `scalar subquery`, `correlated subquery`, `CTE`, `CASE WHEN`, `NOT EXISTS`, `UNION ALL`, `window functions`



### 1. 전체 평균 가격보다 비싼 상품의 이름과 가격을 조회하세요.


전체 평균 가격보다 비싼 상품의 이름과 가격을 조회하세요.


**힌트 1:** `WHERE price > (SELECT AVG(price) FROM products)` 형태의 스칼라 서브쿼리 사용.


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


### 2. 판매 수량 1위 상품의 이름, 카테고리, 총 판매량, 총 매출을 구하세요.


판매 수량 1위 상품의 이름, 카테고리, 총 판매량, 총 매출을 구하세요.


**힌트 1:** `order_items`를 `products`, `categories`와 JOIN 후 `GROUP BY`로 상품별 집계. `ORDER BY total_sold DESC LIMIT 1`.


??? success "정답"
    ```sql
    SELECT
        p.name,
        cat.name AS category,
        SUM(oi.quantity) AS total_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN orders AS o ON oi.order_id = o.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY p.id, p.name, cat.name
    ORDER BY total_sold DESC
    LIMIT 1;
    ```


    **실행 결과** (1행)

    | name | category | total_sold | total_revenue |
    |---|---|---|---|
    | Crucial T700 2TB 실버 | SSD | 1439 | 369,823,000.00 |


---


### 3. 각 상품이 속한 카테고리의 평균 가격보다 비싼 상품만 조회하세요.


각 상품이 속한 카테고리의 평균 가격보다 비싼 상품만 조회하세요.


**힌트 1:** 카테고리별 평균 가격을 서브쿼리(인라인 뷰)로 구한 뒤, `JOIN`으로 연결하여 `WHERE p.price > cat_avg.avg_price`.


??? success "정답"
    ```sql
    SELECT p.name, p.price, cat.name AS category, cat_avg.avg_price
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN (
        SELECT category_id, ROUND(AVG(price), 2) AS avg_price
        FROM products
        GROUP BY category_id
    ) AS cat_avg ON p.category_id = cat_avg.category_id
    WHERE p.price > cat_avg.avg_price
    ORDER BY p.price DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | name | price | category | avg_price |
    |---|---|---|---|
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 | NVIDIA | 2,406,500.00 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 | NVIDIA | 2,406,500.00 |
    | Razer Blade 18 블랙 | 4,353,100.00 | 게이밍 노트북 | 2,684,477.78 |
    | Razer Blade 16 실버 | 3,702,900.00 | 게이밍 노트북 | 2,684,477.78 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 | 조립PC | 1,719,809.09 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 | 게이밍 노트북 | 2,684,477.78 |
    | ASUS ROG Strix GT35 | 3,296,800.00 | 조립PC | 1,719,809.09 |


---


### 4. 평균 평점 4.5 이상이지만 총 매출이 하위 50%인 상품을 찾으세요.


평균 평점 4.5 이상이지만 총 매출이 하위 50%인 상품을 찾으세요.


**힌트 1:** CTE로 상품별 평균 평점과 매출을 구한 뒤, 평점 필터 + 매출이 전체 평균 미만인 조건으로 필터링.


??? success "정답"
    ```sql
    WITH product_stats AS (
        SELECT
            p.id,
            p.name,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM products AS p
        LEFT JOIN reviews AS r ON p.id = r.product_id
        LEFT JOIN order_items AS oi ON p.id = oi.product_id
        GROUP BY p.id, p.name
        HAVING COUNT(r.id) >= 3
    )
    SELECT name, avg_rating, ROUND(revenue, 2) AS revenue
    FROM product_stats
    WHERE avg_rating >= 4.5
      AND revenue < (SELECT AVG(revenue) FROM product_stats)
    ORDER BY avg_rating DESC;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | avg_rating | revenue |
    |---|---|---|
    | be quiet! Dark Power 13 1000W | 5.00 | 22,268,000.00 |
    | 삼성 DM500TDA 실버 | 4.80 | 254,851,000.00 |
    | LG 27UQ85R 화이트 | 4.60 | 669,675,000.00 |
    | LG 32UN880 에르고 화이트 | 4.56 | 2,101,132,800.00 |
    | WD Elements 2TB 블랙 | 4.53 | 863,861,600.00 |
    | Windows 11 Home 블랙 | 4.52 | 994,396,200.00 |
    | ASUS ExpertCenter PN65 실버 | 4.50 | 73,654,200.00 |


---


### 5. 주문을 금액 기준으로 소액(5만 미만), 중액(5~20만), 대액(20~50만), 고액(50만 이상)으로 분


주문을 금액 기준으로 소액(5만 미만), 중액(5~20만), 대액(20~50만), 고액(50만 이상)으로 분류하고 각 등급의 건수와 비율을 구하세요.


**힌트 1:** `CASE WHEN total_amount < 50000 THEN '소액' ...`으로 등급 분류 후 `GROUP BY`. 비율은 윈도우 함수 `SUM(COUNT(*)) OVER ()` 활용.


??? success "정답"
    ```sql
    SELECT
        CASE
            WHEN total_amount < 50000 THEN '소액 (5만 미만)'
            WHEN total_amount < 200000 THEN '중액 (5~20만)'
            WHEN total_amount < 500000 THEN '대액 (20~50만)'
            ELSE '고액 (50만 이상)'
        END AS tier,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
        ROUND(AVG(total_amount), 2) AS avg_amount
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY tier
    ORDER BY MIN(total_amount);
    ```


    **실행 결과** (4행)

    | tier | cnt | pct | avg_amount |
    |---|---|---|---|
    | 소액 (5만 미만) | 2201 | 6.20 | 35,888.07 |
    | 중액 (5~20만) | 9333 | 26.10 | 117,617.99 |
    | 대액 (20~50만) | 7372 | 20.70 | 324,592.77 |
    | 고액 (50만 이상) | 16,792 | 47.00 | 1,945,613.63 |


---


### 6. 위시리스트에 담았지만 한 번도 주문하지 않은 고객-상품 조합을 찾으세요.


위시리스트에 담았지만 한 번도 주문하지 않은 고객-상품 조합을 찾으세요.


**힌트 1:** `NOT EXISTS`로 해당 고객이 해당 상품을 주문한 이력이 있는지 확인하는 상관 서브쿼리 사용.


??? success "정답"
    ```sql
    SELECT
        c.name AS customer,
        p.name AS product,
        w.created_at AS wishlisted_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products AS p ON w.product_id = p.id
    WHERE NOT EXISTS (
        SELECT 1
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.customer_id = w.customer_id
          AND oi.product_id = w.product_id
          AND o.status NOT IN ('cancelled')
    )
    ORDER BY w.created_at DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer | product | wishlisted_at |
    |---|---|---|
    | 박성호 | 주연 리오나인 미니PC | 2025-12-30 19:11:10 |
    | 김영숙 | 삼성 갤럭시북4 360 블랙 | 2025-12-30 17:42:08 |
    | 백지후 | TP-Link TL-SG108 | 2025-12-30 11:47:20 |
    | 이영수 | Seagate IronWolf 4TB 블랙 | 2025-12-30 10:41:18 |
    | 이정순 | SK하이닉스 Platinum P41 2TB 블랙 | 2025-12-30 10:16:54 |
    | 문하은 | TeamGroup T-Force Vulcan DDR5 32GB 52... | 2025-12-30 09:25:54 |
    | 김현주 | APC Back-UPS Pro Gaming BGM1500B 블랙 | 2025-12-30 06:38:37 |


---


### 7. 카드 결제의 발급사(card_issuer)별 건수, 평균 결제 금액, 할부 비율을 구하세요.


카드 결제의 발급사(card_issuer)별 건수, 평균 결제 금액, 할부 비율을 구하세요.


**힌트 1:** `WHERE method = 'card'`로 카드 결제만 필터 후 `GROUP BY card_issuer`. 할부 비율은 `CASE WHEN installment_months > 0` 조건부 집계.


??? success "정답"
    ```sql
    SELECT
        card_issuer,
        COUNT(*) AS tx_count,
        ROUND(AVG(amount), 2) AS avg_amount,
        ROUND(100.0 * SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS installment_pct
    FROM payments
    WHERE method = 'card'
      AND card_issuer IS NOT NULL
    GROUP BY card_issuer
    ORDER BY tx_count DESC;
    ```


    **실행 결과** (총 9행 중 상위 7행)

    | card_issuer | tx_count | avg_amount | installment_pct |
    |---|---|---|---|
    | 신한카드 | 3375 | 1,011,369.46 | 48.80 |
    | 삼성카드 | 2548 | 979,454.89 | 47.80 |
    | KB국민카드 | 2412 | 1,092,916.09 | 47.50 |
    | 현대카드 | 1965 | 1,036,522.88 | 48.20 |
    | 하나카드 | 1712 | 989,167.42 | 49.80 |
    | 롯데카드 | 1692 | 1,018,070.47 | 48.70 |
    | 우리카드 | 1391 | 965,158.40 | 47.90 |


---


### 8. 고객 문의 채널(channel)별 건수, 해결률, 평균 처리 시간을 구하세요.


고객 문의 채널(channel)별 건수, 해결률, 평균 처리 시간을 구하세요.


**힌트 1:** `GROUP BY channel`로 집계. 해결률은 `CASE WHEN status IN ('resolved','closed')`로 조건부 카운트. 처리 시간은 `JULIANDAY` 차이.


??? success "정답"
    ```sql
    SELECT
        channel,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN status IN ('resolved', 'closed') THEN 1 ELSE 0 END) / COUNT(*), 1) AS resolution_pct,
        ROUND(AVG(CASE
            WHEN resolved_at IS NOT NULL
            THEN JULIANDAY(resolved_at) - JULIANDAY(created_at)
        END), 1) AS avg_days
    FROM complaints
    GROUP BY channel
    ORDER BY total DESC;
    ```


    **실행 결과** (5행)

    | channel | total | resolution_pct | avg_days |
    |---|---|---|---|
    | website | 1341 | 94.70 | 1.20 |
    | phone | 913 | 94.10 | 1.20 |
    | email | 796 | 95.40 | 1.20 |
    | chat | 583 | 95.50 | 1.20 |
    | kakao | 180 | 95.00 | 1.20 |


---


### 9. 리뷰도 작성하고 위시리스트에도 상품을 등록한 고객의 이름, 리뷰 수, 위시리스트 수를 구하세요.


리뷰도 작성하고 위시리스트에도 상품을 등록한 고객의 이름, 리뷰 수, 위시리스트 수를 구하세요.


**힌트 1:** 리뷰와 위시리스트를 각각 서브쿼리로 집계한 뒤, 두 서브쿼리를 `INNER JOIN`으로 연결 (양쪽 모두 존재하는 고객만).


??? success "정답"
    ```sql
    SELECT
        c.name,
        r_cnt.review_count,
        w_cnt.wishlist_count
    FROM customers AS c
    INNER JOIN (
        SELECT customer_id, COUNT(*) AS review_count
        FROM reviews GROUP BY customer_id
    ) AS r_cnt ON c.id = r_cnt.customer_id
    INNER JOIN (
        SELECT customer_id, COUNT(*) AS wishlist_count
        FROM wishlists GROUP BY customer_id
    ) AS w_cnt ON c.id = w_cnt.customer_id
    ORDER BY r_cnt.review_count DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | name | review_count | wishlist_count |
    |---|---|---|
    | 김병철 | 72 | 2 |
    | 정유진 | 63 | 1 |
    | 김성민 | 59 | 1 |
    | 최수진 | 45 | 2 |
    | 배춘자 | 43 | 1 |
    | 이예준 | 40 | 1 |
    | 김영길 | 37 | 1 |


---


### 10. 상품별 이미지 수를 구하고, 이미지가 없는 상품도 포함하세요.


상품별 이미지 수를 구하고, 이미지가 없는 상품도 포함하세요.


**힌트 1:** `products LEFT JOIN product_images`로 이미지 없는 상품도 포함. `COUNT(pi.id)`는 NULL을 세지 않으므로 0이 됨.


??? success "정답"
    ```sql
    SELECT
        p.name,
        COUNT(pi.id) AS image_count,
        SUM(CASE WHEN pi.is_primary = 1 THEN 1 ELSE 0 END) AS has_primary
    FROM products AS p
    LEFT JOIN product_images AS pi ON p.id = pi.product_id
    GROUP BY p.id, p.name
    ORDER BY image_count ASC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | name | image_count | has_primary |
    |---|---|---|
    | ASRock B850M Pro RS 실버 | 1 | 1 |
    | ASRock Z890 Taichi 블랙 | 1 | 1 |
    | ASUS Dual RTX 4060 Ti 블랙 | 1 | 1 |
    | ASUS ROG Strix G16CH 화이트 | 1 | 1 |
    | ASUS ROG Swift OLED PG27AQDM 실버 | 1 | 1 |
    | Arctic Liquid Freezer III 240 | 1 | 1 |
    | Arctic Liquid Freezer III Pro 420 A-R... | 1 | 1 |


---


### 11. 장바구니 상태(active/converted/abandoned)별 건수와 비율을 구하세요.


장바구니 상태(active/converted/abandoned)별 건수와 비율을 구하세요.


**힌트 1:** `GROUP BY status`로 집계. 비율은 `100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()`로 전체 대비 비율 계산.


??? success "정답"
    ```sql
    SELECT
        status,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM carts
    GROUP BY status
    ORDER BY cnt DESC;
    ```


    **실행 결과** (3행)

    | status | cnt | pct |
    |---|---|---|
    | converted | 1486 | 49.50 |
    | abandoned | 899 | 30.00 |
    | active | 615 | 20.50 |


---


### 12. 주문 취소 이벤트와 반품 요청 이벤트를 하나의 타임라인으로 합치세요. 최근 20건.


주문 취소 이벤트와 반품 요청 이벤트를 하나의 타임라인으로 합치세요. 최근 20건.


**힌트 1:** `UNION ALL`로 두 SELECT를 합치되, 칼럼 수와 의미를 맞춰야 함. 이벤트 유형 구분 칼럼 추가.


??? success "정답"
    ```sql
    SELECT '취소' AS event_type, order_number AS reference, cancelled_at AS event_date
    FROM orders
    WHERE status = 'cancelled' AND cancelled_at IS NOT NULL
    UNION ALL
    SELECT '반품' AS event_type, CAST(order_id AS TEXT), requested_at
    FROM returns
    WHERE requested_at IS NOT NULL
    ORDER BY event_date DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | event_type | reference | event_date |
    |---|---|---|
    | 반품 | 37371 | 2026-01-08 07:26:14 |
    | 반품 | 37537 | 2026-01-07 02:35:31 |
    | 반품 | 37409 | 2026-01-05 04:25:32 |
    | 반품 | 37515 | 2026-01-05 01:26:34 |
    | 반품 | 37405 | 2026-01-02 10:13:52 |
    | 취소 | ORD-20251231-37545 | 2026-01-01 23:35:58 |
    | 취소 | ORD-20251230-37531 | 2025-12-31 08:00:28 |


---
