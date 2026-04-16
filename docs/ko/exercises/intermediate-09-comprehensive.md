# 중급 종합 문제

!!! info "사용 테이블"

    `orders` — 주문 (상태, 금액, 일시)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `categories` — 카테고리 (부모-자식 계층)  

    `payments` — 결제 (방법, 금액, 상태)  

    `reviews` — 리뷰 (평점, 내용)  

    `shipping` — 배송 (택배사, 추적번호, 상태)  

    `complaints` — 고객 불만 (유형, 우선순위)  

    `wishlists` — 위시리스트 (고객-상품)  

    `suppliers` — 공급업체 (업체명, 연락처)  

    `returns` — 반품/교환 (사유, 상태)  

    `coupon_usage` — 쿠폰 사용 내역  



!!! abstract "학습 범위"

    `JOIN`, `subquery`, `date functions`, `string functions`, `CASE`, `UNION`, `GROUP BY`, `HAVING`, `aggregate functions`, `LAG`, `window functions`



### 1. JOIN + GROUP BY: 카테고리별 판매 중인 상품 수와 평균 가격을 조회하세요. 상품 수가 많은 순으


JOIN + GROUP BY: 카테고리별 판매 중인 상품 수와 평균 가격을 조회하세요. 상품 수가 많은 순으로 10개만.


**힌트 1:** `products JOIN categories`로 연결 후 `GROUP BY`로 카테고리별 집계. `WHERE is_active = 1`로 판매 중만 필터링.


??? success "정답"
    ```sql
    SELECT
        cat.name AS category,
        COUNT(*) AS product_count,
        ROUND(AVG(p.price)) AS avg_price
    FROM products p
    INNER JOIN categories cat ON p.category_id = cat.id
    WHERE p.is_active = 1
    GROUP BY cat.id, cat.name
    ORDER BY product_count DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | category | product_count | avg_price |
    |---|---|---|
    | 파워서플라이(PSU) | 11 | 234,645.00 |
    | 게이밍 모니터 | 10 | 1,123,150.00 |
    | Intel 소켓 | 10 | 527,080.00 |
    | 케이스 | 10 | 159,930.00 |
    | 조립PC | 9 | 1,836,467.00 |
    | AMD 소켓 | 9 | 511,056.00 |
    | 스피커/헤드셋 | 9 | 274,056.00 |


---


### 2. JOIN + CASE: 각 주문의 주문번호, 고객명, 결제 방법을 조회하세요. 결제 방법은 한글로 변환. 최


JOIN + CASE: 각 주문의 주문번호, 고객명, 결제 방법을 조회하세요. 결제 방법은 한글로 변환. 최근 10건.


**힌트 1:** `orders JOIN customers JOIN payments`로 3개 테이블 연결. `CASE payments.method WHEN ... THEN ...`으로 한글 변환.


??? success "정답"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer_name,
        CASE pay.method
            WHEN 'card' THEN '카드'
            WHEN 'bank_transfer' THEN '계좌이체'
            WHEN 'kakao_pay' THEN '카카오페이'
            WHEN 'naver_pay' THEN '네이버페이'
            WHEN 'virtual_account' THEN '가상계좌'
            WHEN 'point' THEN '포인트'
            ELSE '기타'
        END AS payment_method_kr,
        o.total_amount
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    INNER JOIN payments pay ON o.id = pay.order_id
    ORDER BY o.ordered_at DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | customer_name | payment_method_kr | total_amount |
    |---|---|---|---|
    | ORD-20251231-37555 | 송지영 | 카드 | 74,800.00 |
    | ORD-20251231-37543 | 박민서 | 카카오페이 | 134,100.00 |
    | ORD-20251231-37552 | 강미경 | 카드 | 254,300.00 |
    | ORD-20251231-37548 | 윤영희 | 계좌이체 | 187,700.00 |
    | ORD-20251231-37542 | 문도현 | 카카오페이 | 155,700.00 |
    | ORD-20251231-37546 | 박상호 | 네이버페이 | 198,300.00 |
    | ORD-20251231-37547 | 강서준 | 계좌이체 | 335,000.00 |


---


### 3. 서브쿼리 + 날짜: 2024년에 가장 많이 주문한 고객 TOP 5의 이름, 주문 건수, 총 결제금액을 조회하


서브쿼리 + 날짜: 2024년에 가장 많이 주문한 고객 TOP 5의 이름, 주문 건수, 총 결제금액을 조회하세요.


**힌트 1:** `orders`에서 `ordered_at LIKE '2024%'`로 필터링 후 `GROUP BY customer_id`로 집계.


??? success "정답"
    ```sql
    SELECT
        c.name,
        sub.order_count,
        sub.total_spent
    FROM (
        SELECT customer_id, COUNT(*) AS order_count, SUM(total_amount) AS total_spent
        FROM orders
        WHERE ordered_at LIKE '2024%'
        GROUP BY customer_id
        ORDER BY order_count DESC
        LIMIT 5
    ) sub
    INNER JOIN customers c ON sub.customer_id = c.id
    ORDER BY sub.order_count DESC;
    ```


    **실행 결과** (5행)

    | name | order_count | total_spent |
    |---|---|---|
    | 신은정 | 25 | 25,706,293.00 |
    | 심승현 | 25 | 24,330,429.00 |
    | 이수빈 | 24 | 28,684,563.00 |
    | 이민지 | 23 | 24,524,212.00 |
    | 김명숙 | 23 | 20,979,498.00 |


---


### 4. 문자열 함수 + GROUP BY: 고객 이메일 도메인별 고객 수를 집계하세요.


문자열 함수 + GROUP BY: 고객 이메일 도메인별 고객 수를 집계하세요.


**힌트 1:** `SUBSTR(email, INSTR(email, '@') + 1)`로 도메인을 추출합니다.


??? success "정답"
    ```sql
    SELECT
        SUBSTR(email, INSTR(email, '@') + 1) AS domain,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY domain
    ORDER BY customer_count DESC;
    ```


    **실행 결과** (1행)

    | domain | customer_count |
    |---|---|
    | testmail.kr | 5230 |


---


### 5. JOIN + HAVING: 리뷰를 5건 이상 작성한 고객의 이름과 평균 평점을 조회하세요. 상위 10명.


JOIN + HAVING: 리뷰를 5건 이상 작성한 고객의 이름과 평균 평점을 조회하세요. 상위 10명.


**힌트 1:** `reviews JOIN customers`로 연결 후 `GROUP BY customer_id` + `HAVING COUNT(*) >= 5`.


??? success "정답"
    ```sql
    SELECT
        c.name,
        COUNT(*) AS review_count,
        ROUND(AVG(r.rating), 1) AS avg_rating
    FROM reviews r
    INNER JOIN customers c ON r.customer_id = c.id
    GROUP BY r.customer_id, c.name
    HAVING COUNT(*) >= 5
    ORDER BY review_count DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | review_count | avg_rating |
    |---|---|---|
    | 김병철 | 72 | 3.80 |
    | 박정수 | 63 | 3.80 |
    | 정유진 | 63 | 4.10 |
    | 이영자 | 62 | 4.00 |
    | 강명자 | 62 | 3.80 |
    | 이미정 | 60 | 3.60 |
    | 김성민 | 59 | 4.20 |


---


### 6. UNION + CASE: 최근 1년간 신규 고객 수와 신규 상품 수를 하나의 결과로 합쳐서 보세요.


UNION + CASE: 최근 1년간 신규 고객 수와 신규 상품 수를 하나의 결과로 합쳐서 보세요.


**힌트 1:** 각 테이블에서 2024년 데이터를 COUNT하고 UNION ALL로 합칩니다.


??? success "정답"
    ```sql
    SELECT '신규 고객' AS category, COUNT(*) AS count_2024
    FROM customers
    WHERE created_at LIKE '2024%'
    UNION ALL
    SELECT '신규 상품' AS category, COUNT(*) AS count_2024
    FROM products
    WHERE created_at LIKE '2024%';
    ```


    **실행 결과** (2행)

    | category | count_2024 |
    |---|---|
    | 신규 고객 | 700 |
    | 신규 상품 | 30 |


---


### 7. 날짜 함수 + JOIN: 주문 후 배송 완료까지 걸린 평균 일수를 택배사별로 조회하세요.


날짜 함수 + JOIN: 주문 후 배송 완료까지 걸린 평균 일수를 택배사별로 조회하세요.


**힌트 1:** `julianday(delivered_at) - julianday(ordered_at)`로 일수 계산.


??? success "정답"
    ```sql
    SELECT
        s.carrier,
        COUNT(*) AS delivered_count,
        ROUND(AVG(julianday(s.delivered_at) - julianday(o.ordered_at)), 1) AS avg_days
    FROM shipping s
    INNER JOIN orders o ON s.order_id = o.id
    WHERE s.status = 'delivered' AND s.delivered_at IS NOT NULL
    GROUP BY s.carrier
    ORDER BY avg_days;
    ```


    **실행 결과** (4행)

    | carrier | delivered_count | avg_days |
    |---|---|---|
    | CJ대한통운 | 13,671 | 4.50 |
    | 로젠택배 | 6939 | 4.50 |
    | 우체국택배 | 5207 | 4.50 |
    | 한진택배 | 8701 | 4.50 |


---


### 8. 서브쿼리 + CASE: 각 상품의 카테고리 평균 가격 대비 고가/저가/평균 수준을 표시하세요. 상위 15개.


서브쿼리 + CASE: 각 상품의 카테고리 평균 가격 대비 고가/저가/평균 수준을 표시하세요. 상위 15개.


**힌트 1:** 서브쿼리로 카테고리별 평균 가격을 구한 뒤 JOIN. `CASE WHEN price > avg_price * 1.2 THEN '고가'...`


??? success "정답"
    ```sql
    SELECT
        p.name, p.price, cat_avg.avg_price,
        CASE
            WHEN p.price > cat_avg.avg_price * 1.2 THEN '고가'
            WHEN p.price < cat_avg.avg_price * 0.8 THEN '저가'
            ELSE '평균 수준'
        END AS price_level
    FROM products p
    INNER JOIN (
        SELECT category_id, ROUND(AVG(price)) AS avg_price
        FROM products WHERE is_active = 1
        GROUP BY category_id
    ) cat_avg ON p.category_id = cat_avg.category_id
    WHERE p.is_active = 1
    ORDER BY p.price DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | name | price | avg_price | price_level |
    |---|---|---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 | 5,481,100.00 | 평균 수준 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 | 2,207,600.00 | 고가 |
    | Razer Blade 18 블랙 | 4,353,100.00 | 2,887,583.00 | 고가 |
    | Razer Blade 16 실버 | 3,702,900.00 | 2,887,583.00 | 고가 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 | 1,836,467.00 | 고가 |
    | ASUS ROG Strix GT35 | 3,296,800.00 | 1,836,467.00 | 고가 |
    | Razer Blade 18 블랙 | 2,987,500.00 | 2,887,583.00 | 평균 수준 |


---


### 9. JOIN + GROUP BY + HAVING + 서브쿼리: 전체 평균보다 높은 매출을 올린 브랜드의 이름, 


JOIN + GROUP BY + HAVING + 서브쿼리: 전체 평균보다 높은 매출을 올린 브랜드의 이름, 총 매출, 주문 건수를 조회하세요. 상위 10개.


**힌트 1:** `HAVING SUM(subtotal) > (SELECT AVG(...))`. 전체 평균은 브랜드별 매출의 평균입니다.


??? success "정답"
    ```sql
    SELECT
        p.brand,
        SUM(oi.subtotal) AS total_revenue,
        COUNT(DISTINCT oi.order_id) AS order_count
    FROM order_items oi
    INNER JOIN products p ON oi.product_id = p.id
    GROUP BY p.brand
    HAVING SUM(oi.subtotal) > (
        SELECT AVG(brand_revenue)
        FROM (
            SELECT SUM(oi2.subtotal) AS brand_revenue
            FROM order_items oi2
            INNER JOIN products p2 ON oi2.product_id = p2.id
            GROUP BY p2.brand
        )
    )
    ORDER BY total_revenue DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | brand | total_revenue | order_count |
    |---|---|---|
    | ASUS | 6,181,415,600.00 | 4945 |
    | Razer | 4,167,252,100.00 | 2754 |
    | 삼성전자 | 3,000,828,600.00 | 7169 |
    | MSI | 2,787,039,100.00 | 3531 |
    | LG전자 | 2,221,778,900.00 | 1647 |
    | ASRock | 1,741,420,800.00 | 3435 |
    | Intel | 1,267,419,000.00 | 2579 |


---


### 10. 2024년 월별로 주문 상태 분포를 조회하세요. 완료, 취소, 기타 건수와 취소율을 표시합니다.


2024년 월별로 주문 상태 분포를 조회하세요. 완료, 취소, 기타 건수와 취소율을 표시합니다.


**힌트 1:** `SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END)`로 조건부 집계.


??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
        SUM(CASE WHEN status NOT IN ('confirmed', 'cancelled') THEN 1 ELSE 0 END) AS in_progress,
        ROUND(100.0 * SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1) AS cancel_rate
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | month | total_orders | confirmed | cancelled | in_progress | cancel_rate |
    |---|---|---|---|---|---|
    | 2024-01 | 346 | 314 | 21 | 11 | 6.10 |
    | 2024-02 | 465 | 416 | 32 | 17 | 6.90 |
    | 2024-03 | 601 | 555 | 29 | 17 | 4.80 |
    | 2024-04 | 506 | 466 | 28 | 12 | 5.50 |
    | 2024-05 | 415 | 385 | 19 | 11 | 4.60 |
    | 2024-06 | 415 | 389 | 18 | 8 | 4.30 |
    | 2024-07 | 414 | 381 | 23 | 10 | 5.60 |


---


### 11. VIP 고객이 구매한 상품 중, 리뷰 평점이 4점 이상인 상품의 이름, 브랜드, 평균 평점, VIP 구매 횟


VIP 고객이 구매한 상품 중, 리뷰 평점이 4점 이상인 상품의 이름, 브랜드, 평균 평점, VIP 구매 횟수를 조회하세요. 상위 10개.


**힌트 1:** `customers(grade='VIP') JOIN orders JOIN order_items JOIN products`로 VIP 구매 상품을 파악. 서브쿼리로 리뷰 평균 4점 이상 필터링.


??? success "정답"
    ```sql
    SELECT
        p.name, p.brand, review_avg.avg_rating,
        COUNT(*) AS vip_purchase_count
    FROM order_items oi
    INNER JOIN orders o ON oi.order_id = o.id
    INNER JOIN customers c ON o.customer_id = c.id
    INNER JOIN products p ON oi.product_id = p.id
    INNER JOIN (
        SELECT product_id, ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews GROUP BY product_id HAVING AVG(rating) >= 4.0
    ) review_avg ON p.id = review_avg.product_id
    WHERE c.grade = 'VIP'
    GROUP BY p.id, p.name, p.brand, review_avg.avg_rating
    ORDER BY vip_purchase_count DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | brand | avg_rating | vip_purchase_count |
    |---|---|---|---|
    | Crucial T700 2TB 실버 | Crucial | 4.20 | 617 |
    | 로지텍 G502 X PLUS | 로지텍 | 4.20 | 429 |
    | be quiet! Light Base 900 | be quiet! | 4.10 | 338 |
    | Arctic Freezer 36 A-RGB 화이트 | Arctic | 4.00 | 317 |
    | 로지텍 MX Anywhere 3S 블랙 | 로지텍 | 4.00 | 315 |
    | 로지텍 G715 화이트 | 로지텍 | 4.10 | 314 |
    | be quiet! Pure Power 12 M 850W 화이트 | be quiet! | 4.10 | 304 |


---


### 12. LEFT JOIN + COALESCE: 모든 상품의 이름, 가격, 총 판매 수량, 총 리뷰 수를 조회하세요.


LEFT JOIN + COALESCE: 모든 상품의 이름, 가격, 총 판매 수량, 총 리뷰 수를 조회하세요. 없으면 0. 상위 15개.


**힌트 1:** 카디널리티 폭발 방지를 위해 판매 수량과 리뷰 수를 각각 서브쿼리로 집계한 뒤 LEFT JOIN합니다.


??? success "정답"
    ```sql
    SELECT
        p.name, p.price,
        COALESCE(sales.total_qty, 0) AS total_sold,
        COALESCE(rev.review_count, 0) AS review_count
    FROM products p
    LEFT JOIN (
        SELECT product_id, SUM(quantity) AS total_qty
        FROM order_items GROUP BY product_id
    ) sales ON p.id = sales.product_id
    LEFT JOIN (
        SELECT product_id, COUNT(*) AS review_count
        FROM reviews GROUP BY product_id
    ) rev ON p.id = rev.product_id
    WHERE p.is_active = 1
    ORDER BY total_sold DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | name | price | total_sold | review_count |
    |---|---|---|---|
    | Crucial T700 2TB 실버 | 257,000.00 | 1503 | 77 |
    | AMD Ryzen 9 9900X | 335,700.00 | 1447 | 65 |
    | SK하이닉스 Platinum P41 2TB 실버 | 255,500.00 | 1359 | 49 |
    | 로지텍 G502 X PLUS | 97,500.00 | 1087 | 101 |
    | Kingston FURY Beast DDR4 16GB 실버 | 48,000.00 | 1061 | 102 |
    | SteelSeries Prime Wireless 블랙 | 89,800.00 | 1034 | 80 |
    | SteelSeries Aerox 5 Wireless 실버 | 100,000.00 | 1030 | 100 |


---


### 13. UNION + JOIN + GROUP BY: 고객별 "활동 점수"를 계산하세요. 주문=10점, 리뷰=5점, 


UNION + JOIN + GROUP BY: 고객별 "활동 점수"를 계산하세요. 주문=10점, 리뷰=5점, 문의=3점. 상위 10명.


**힌트 1:** 각 활동별 점수를 UNION ALL로 합친 뒤, 외부에서 SUM으로 총점을 구합니다.


??? success "정답"
    ```sql
    SELECT
        c.name, c.grade,
        SUM(activity.score) AS total_score,
        SUM(CASE WHEN activity.type = '주문' THEN 1 ELSE 0 END) AS orders,
        SUM(CASE WHEN activity.type = '리뷰' THEN 1 ELSE 0 END) AS reviews,
        SUM(CASE WHEN activity.type = '문의' THEN 1 ELSE 0 END) AS complaints
    FROM (
        SELECT customer_id, '주문' AS type, 10 AS score FROM orders
        UNION ALL
        SELECT customer_id, '리뷰' AS type, 5 AS score FROM reviews
        UNION ALL
        SELECT customer_id, '문의' AS type, 3 AS score FROM complaints
    ) activity
    INNER JOIN customers c ON activity.customer_id = c.id
    GROUP BY activity.customer_id, c.name, c.grade
    ORDER BY total_score DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | grade | total_score | orders | reviews | complaints |
    |---|---|---|---|---|---|
    | 김병철 | VIP | 4095 | 366 | 72 | 25 |
    | 박정수 | VIP | 3652 | 328 | 63 | 19 |
    | 이영자 | VIP | 3467 | 307 | 62 | 29 |
    | 강명자 | VIP | 3042 | 266 | 62 | 24 |
    | 김성민 | VIP | 2794 | 246 | 59 | 13 |
    | 정유진 | VIP | 2742 | 237 | 63 | 19 |
    | 이미정 | VIP | 2697 | 234 | 60 | 19 |


---


### 14. 서브쿼리 + JOIN + 날짜: 가입 후 30일 이내/31~90일/90일 초과에 첫 주문을 한 고객 수를 비


서브쿼리 + JOIN + 날짜: 가입 후 30일 이내/31~90일/90일 초과에 첫 주문을 한 고객 수를 비교하세요.


**힌트 1:** `MIN(ordered_at)`으로 고객별 첫 주문일을 구한 서브쿼리를 만들고, `julianday` 차이로 일수를 계산합니다.


??? success "정답"
    ```sql
    SELECT
        CASE
            WHEN days_to_first_order <= 30 THEN '30일 이내'
            WHEN days_to_first_order <= 90 THEN '31~90일'
            ELSE '90일 초과'
        END AS segment,
        COUNT(*) AS customer_count,
        ROUND(AVG(days_to_first_order), 1) AS avg_days
    FROM (
        SELECT c.id,
            ROUND(julianday(MIN(o.ordered_at)) - julianday(c.created_at)) AS days_to_first_order
        FROM customers c
        INNER JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.created_at
    )
    GROUP BY segment
    ORDER BY MIN(days_to_first_order);
    ```


    **실행 결과** (3행)

    | segment | customer_count | avg_days |
    |---|---|---|
    | 30일 이내 | 955 | 8.30 |
    | 31~90일 | 596 | 56.10 |
    | 90일 초과 | 1288 | 329.50 |


---


### 15. 결제 방법별, 카드 발급사별 매출 현황을 조회하세요. 카드 아닌 경우 발급사는 '해당없음'. 상위 15개.


결제 방법별, 카드 발급사별 매출 현황을 조회하세요. 카드 아닌 경우 발급사는 '해당없음'. 상위 15개.


**힌트 1:** `COALESCE(card_issuer, '해당없음')`으로 NULL 처리. `GROUP BY method, card_issuer`.


??? success "정답"
    ```sql
    SELECT
        CASE pay.method
            WHEN 'card' THEN '카드'
            WHEN 'bank_transfer' THEN '계좌이체'
            WHEN 'kakao_pay' THEN '카카오페이'
            WHEN 'naver_pay' THEN '네이버페이'
            ELSE pay.method
        END AS method_kr,
        COALESCE(pay.card_issuer, '해당없음') AS issuer,
        COUNT(*) AS payment_count,
        SUM(pay.amount) AS total_amount,
        ROUND(AVG(pay.amount)) AS avg_amount
    FROM payments pay
    WHERE pay.status = 'completed'
    GROUP BY pay.method, pay.card_issuer
    ORDER BY total_amount DESC
    LIMIT 15;
    ```


    **실행 결과** (총 14행 중 상위 7행)

    | method_kr | issuer | payment_count | total_amount | avg_amount |
    |---|---|---|---|---|
    | 카카오페이 | 해당없음 | 6886 | 6,781,114,303.00 | 984,768.00 |
    | 네이버페이 | 해당없음 | 5270 | 5,420,480,093.00 | 1,028,554.00 |
    | 계좌이체 | 해당없음 | 3429 | 3,456,454,657.00 | 1,008,007.00 |
    | 카드 | 신한카드 | 3084 | 3,079,917,150.00 | 998,676.00 |
    | 카드 | KB국민카드 | 2230 | 2,428,560,078.00 | 1,089,040.00 |
    | 카드 | 삼성카드 | 2386 | 2,323,039,558.00 | 973,613.00 |
    | 카드 | 현대카드 | 1815 | 1,834,423,680.00 | 1,010,702.00 |


---


### 16. 고객을 최근 주문일 기준 RFM R등급으로 분류하세요. Active(30일), Warm(90일), Cold(


고객을 최근 주문일 기준 RFM R등급으로 분류하세요. Active(30일), Warm(90일), Cold(180일), Dormant.


**힌트 1:** `LEFT JOIN`으로 주문 없는 고객 포함. `MAX(ordered_at)`으로 최근 주문일 구한 뒤, `julianday('now') - julianday(last_order)`로 경과일 계산.


??? success "정답"
    ```sql
    SELECT
        recency_group,
        COUNT(*) AS customer_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM (
        SELECT c.id,
            CASE
                WHEN MAX(o.ordered_at) IS NULL THEN 'Dormant'
                WHEN julianday('now') - julianday(MAX(o.ordered_at)) <= 30 THEN 'Active'
                WHEN julianday('now') - julianday(MAX(o.ordered_at)) <= 90 THEN 'Warm'
                WHEN julianday('now') - julianday(MAX(o.ordered_at)) <= 180 THEN 'Cold'
                ELSE 'Dormant'
            END AS recency_group
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id
    )
    GROUP BY recency_group
    ORDER BY CASE recency_group WHEN 'Active' THEN 1 WHEN 'Warm' THEN 2 WHEN 'Cold' THEN 3 ELSE 4 END;
    ```


    **실행 결과** (2행)

    | recency_group | customer_count | pct |
    |---|---|---|
    | Cold | 960 | 18.40 |
    | Dormant | 4270 | 81.60 |


---


### 17. 월간 매출 리포트: 2024년 월별 매출, 주문 건수, 고유 고객 수, 건당 평균, 전월 대비 증감율.


월간 매출 리포트: 2024년 월별 매출, 주문 건수, 고유 고객 수, 건당 평균, 전월 대비 증감율.


**힌트 1:** `LAG()` 윈도우 함수로 전월 매출을 가져와 증감율을 계산합니다.


??? success "정답"
    ```sql
    SELECT
        month, total_revenue, order_count, unique_customers,
        ROUND(total_revenue * 1.0 / order_count) AS avg_order_value,
        CASE
            WHEN prev_revenue IS NULL THEN '-'
            ELSE ROUND((total_revenue - prev_revenue) * 100.0 / prev_revenue, 1) || '%'
        END AS growth_rate
    FROM (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS month,
            SUM(total_amount) AS total_revenue,
            COUNT(*) AS order_count,
            COUNT(DISTINCT customer_id) AS unique_customers,
            LAG(SUM(total_amount)) OVER (ORDER BY SUBSTR(ordered_at, 1, 7)) AS prev_revenue
        FROM orders
        WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    ORDER BY month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | month | total_revenue | order_count | unique_customers | avg_order_value | growth_rate |
    |---|---|---|---|---|---|
    | 2024-01 | 301,075,320.00 | 325 | 275 | 926,386.00 | - |
    | 2024-02 | 426,177,449.00 | 433 | 345 | 984,244.00 | 41.6% |
    | 2024-03 | 536,322,767.00 | 572 | 428 | 937,627.00 | 25.8% |
    | 2024-04 | 470,154,081.00 | 478 | 362 | 983,586.00 | -12.3% |
    | 2024-05 | 459,724,596.00 | 396 | 323 | 1,160,921.00 | -2.2% |
    | 2024-06 | 377,040,302.00 | 397 | 327 | 949,724.00 | -18.0% |
    | 2024-07 | 363,944,597.00 | 391 | 320 | 930,805.00 | -3.5% |


---


### 18. 고객 등급별 평균 주문 금액, 평균 리뷰 평점, 반품율을 조회하세요.


고객 등급별 평균 주문 금액, 평균 리뷰 평점, 반품율을 조회하세요.


**힌트 1:** 각 지표를 서브쿼리로 따로 집계한 뒤 `customers`의 `grade`로 GROUP BY.


??? success "정답"
    ```sql
    SELECT
        c.grade,
        COUNT(DISTINCT c.id) AS customer_count,
        ROUND(AVG(order_stats.avg_amount)) AS avg_order_amount,
        ROUND(AVG(review_stats.avg_rating), 2) AS avg_rating,
        ROUND(100.0 * SUM(COALESCE(return_stats.return_count, 0))
            / NULLIF(SUM(COALESCE(order_stats.order_count, 0)), 0), 2) AS return_rate_pct
    FROM customers c
    LEFT JOIN (
        SELECT customer_id, COUNT(*) AS order_count, AVG(total_amount) AS avg_amount
        FROM orders GROUP BY customer_id
    ) order_stats ON c.id = order_stats.customer_id
    LEFT JOIN (
        SELECT customer_id, AVG(rating) AS avg_rating
        FROM reviews GROUP BY customer_id
    ) review_stats ON c.id = review_stats.customer_id
    LEFT JOIN (
        SELECT customer_id, COUNT(*) AS return_count
        FROM returns GROUP BY customer_id
    ) return_stats ON c.id = return_stats.customer_id
    GROUP BY c.grade
    ORDER BY CASE c.grade WHEN 'VIP' THEN 1 WHEN 'GOLD' THEN 2 WHEN 'SILVER' THEN 3 WHEN 'BRONZE' THEN 4 END;
    ```


    **실행 결과** (4행)

    | grade | customer_count | avg_order_amount | avg_rating | return_rate_pct |
    |---|---|---|---|---|
    | VIP | 368 | 1,419,393.00 | 3.88 | 2.56 |
    | GOLD | 524 | 1,119,695.00 | 3.92 | 2.48 |
    | SILVER | 479 | 887,476.00 | 3.90 | 2.68 |
    | BRONZE | 3859 | 699,518.00 | 3.92 | 3.02 |


---


### 19. 재고 위험 상품 점검: 현재 재고가 최근 30일 판매량보다 적은 상품을 찾으세요. 예상 소진일 포함. 상위 


재고 위험 상품 점검: 현재 재고가 최근 30일 판매량보다 적은 상품을 찾으세요. 예상 소진일 포함. 상위 15개.


**힌트 1:** 최근 30일 판매량은 `order_items JOIN orders`에서 `ordered_at >= date('now', '-30 days')`로 계산.


??? success "정답"
    ```sql
    SELECT
        p.name, p.stock_qty AS current_stock,
        COALESCE(sales.qty_30d, 0) AS sold_30d,
        CASE
            WHEN COALESCE(sales.qty_30d, 0) = 0 THEN '판매 없음'
            ELSE CAST(ROUND(p.stock_qty * 30.0 / sales.qty_30d) AS INTEGER) || '일'
        END AS est_days_left
    FROM products p
    LEFT JOIN (
        SELECT oi.product_id, SUM(oi.quantity) AS qty_30d
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        WHERE o.ordered_at >= date('now', '-30 days') AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    ) sales ON p.id = sales.product_id
    WHERE p.is_active = 1 AND p.stock_qty < COALESCE(sales.qty_30d, 0)
    ORDER BY p.stock_qty ASC
    LIMIT 15;
    ```


---


### 20. 카테고리 계층 분석: 대분류(depth=0)별로 소속 상품 수, 총 매출, 평균 리뷰 평점을 조회하세요.


카테고리 계층 분석: 대분류(depth=0)별로 소속 상품 수, 총 매출, 평균 리뷰 평점을 조회하세요.


**힌트 1:** 카테고리의 `parent_id`를 따라 올라가야 합니다. `categories`를 자기 자신과 JOIN하여 대분류를 찾으세요.


??? success "정답"
    ```sql
    SELECT
        top_cat.name AS top_category,
        COUNT(DISTINCT p.id) AS product_count,
        COALESCE(SUM(sales.revenue), 0) AS total_revenue,
        ROUND(AVG(rev.avg_rating), 1) AS avg_rating
    FROM categories top_cat
    LEFT JOIN categories mid_cat ON mid_cat.parent_id = top_cat.id
    LEFT JOIN categories sub_cat ON sub_cat.parent_id = mid_cat.id
    LEFT JOIN products p ON p.category_id IN (top_cat.id, mid_cat.id, sub_cat.id)
    LEFT JOIN (
        SELECT product_id, SUM(subtotal) AS revenue FROM order_items GROUP BY product_id
    ) sales ON p.id = sales.product_id
    LEFT JOIN (
        SELECT product_id, AVG(rating) AS avg_rating FROM reviews GROUP BY product_id
    ) rev ON p.id = rev.product_id
    WHERE top_cat.depth = 0
    GROUP BY top_cat.id, top_cat.name
    ORDER BY total_revenue DESC;
    ```


    **실행 결과** (총 18행 중 상위 7행)

    | top_category | product_count | total_revenue | avg_rating |
    |---|---|---|---|
    | 노트북 | 29 | 10,050,178,200.00 | 3.70 |
    | 그래픽카드 | 15 | 5,559,698,400.00 | 3.90 |
    | 모니터 | 22 | 4,712,362,900.00 | 3.90 |
    | 메인보드 | 23 | 3,225,292,000.00 | 3.70 |
    | CPU | 7 | 1,858,019,600.00 | 3.80 |
    | 스피커/헤드셋 | 12 | 1,546,414,500.00 | 3.90 |
    | 저장장치 | 15 | 1,511,680,300.00 | 3.90 |


---


### 21. 공급업체 성과 비교: 공급업체별 공급 상품 수, 총 매출, 평균 리뷰 평점, 반품률. 매출 상위 10개.


공급업체 성과 비교: 공급업체별 공급 상품 수, 총 매출, 평균 리뷰 평점, 반품률. 매출 상위 10개.


**힌트 1:** 각 지표를 서브쿼리로 분리하면 깔끔합니다.


??? success "정답"
    ```sql
    SELECT
        s.company_name,
        COUNT(DISTINCT p.id) AS product_count,
        COALESCE(SUM(sales.revenue), 0) AS total_revenue,
        ROUND(AVG(rev.avg_rating), 1) AS avg_rating,
        ROUND(100.0 * COALESCE(SUM(ret.return_count), 0)
            / NULLIF(COALESCE(SUM(sales.sold_count), 0), 0), 2) AS return_rate_pct
    FROM suppliers s
    INNER JOIN products p ON p.supplier_id = s.id
    LEFT JOIN (SELECT product_id, SUM(subtotal) AS revenue, COUNT(*) AS sold_count FROM order_items GROUP BY product_id) sales ON p.id = sales.product_id
    LEFT JOIN (SELECT product_id, AVG(rating) AS avg_rating FROM reviews GROUP BY product_id) rev ON p.id = rev.product_id
    LEFT JOIN (SELECT oi.product_id, COUNT(DISTINCT r.id) AS return_count FROM returns r INNER JOIN orders o ON r.order_id = o.id INNER JOIN order_items oi ON o.id = oi.order_id GROUP BY oi.product_id) ret ON p.id = ret.product_id
    GROUP BY s.id, s.company_name
    ORDER BY total_revenue DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | company_name | product_count | total_revenue | avg_rating | return_rate_pct |
    |---|---|---|---|---|
    | 에이수스코리아 | 26 | 6,181,415,600.00 | 3.90 | 3.42 |
    | 레이저코리아 | 9 | 4,167,252,100.00 | 3.90 | 4.17 |
    | 삼성전자 공식 유통 | 26 | 3,000,828,600.00 | 3.80 | 2.96 |
    | MSI코리아 | 13 | 2,787,039,100.00 | 3.90 | 3.50 |
    | LG전자 공식 유통 | 11 | 2,221,778,900.00 | 3.90 | 3.61 |
    | ASRock코리아 | 11 | 1,741,420,800.00 | 3.60 | 3.38 |
    | 인텔코리아 | 6 | 1,267,419,000.00 | 3.80 | 3.21 |


---


### 22. 쿠폰 효과 분석: 쿠폰 사용/미사용 주문의 평균 결제금액, 평균 상품 수, 완료율을 비교하세요.


쿠폰 효과 분석: 쿠폰 사용/미사용 주문의 평균 결제금액, 평균 상품 수, 완료율을 비교하세요.


**힌트 1:** `orders LEFT JOIN coupon_usage`로 연결. `CASE WHEN cu.id IS NOT NULL THEN '사용' ELSE '미사용' END`로 구분.


??? success "정답"
    ```sql
    SELECT
        CASE WHEN cu.id IS NOT NULL THEN '쿠폰 사용' ELSE '쿠폰 미사용' END AS coupon_group,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(AVG(o.total_amount)) AS avg_amount,
        ROUND(AVG(item_stats.item_count), 1) AS avg_items,
        ROUND(100.0 * SUM(CASE WHEN o.status = 'confirmed' THEN 1 ELSE 0 END)
            / COUNT(DISTINCT o.id), 1) AS confirm_rate_pct
    FROM orders o
    LEFT JOIN coupon_usage cu ON o.id = cu.order_id
    LEFT JOIN (SELECT order_id, COUNT(*) AS item_count FROM order_items GROUP BY order_id) item_stats ON o.id = item_stats.order_id
    GROUP BY CASE WHEN cu.id IS NOT NULL THEN '쿠폰 사용' ELSE '쿠폰 미사용' END;
    ```


    **실행 결과** (2행)

    | coupon_group | order_count | avg_amount | avg_items | confirm_rate_pct |
    |---|---|---|---|---|
    | 쿠폰 미사용 | 35,893 | 998,277.00 | 2.40 | 91.20 |
    | 쿠폰 사용 | 1664 | 1,413,663.00 | 2.90 | 100.00 |


---


### 23. 위시리스트 전환 분석: 카테고리별 위시리스트→구매 전환율을 조회하세요. 5건 이상만. 상위 10개.


위시리스트 전환 분석: 카테고리별 위시리스트→구매 전환율을 조회하세요. 5건 이상만. 상위 10개.


**힌트 1:** `wishlists`의 `is_purchased` 칼럼으로 전환 여부를 파악.


??? success "정답"
    ```sql
    SELECT
        cat.name AS category,
        COUNT(*) AS wishlist_count,
        SUM(w.is_purchased) AS purchased_count,
        ROUND(100.0 * SUM(w.is_purchased) / COUNT(*), 1) AS conversion_rate_pct
    FROM wishlists w
    INNER JOIN products p ON w.product_id = p.id
    INNER JOIN categories cat ON p.category_id = cat.id
    GROUP BY cat.id, cat.name
    HAVING COUNT(*) >= 5
    ORDER BY conversion_rate_pct DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | category | wishlist_count | purchased_count | conversion_rate_pct |
    |---|---|---|---|
    | 베어본 | 8 | 1 | 12.50 |
    | 멤브레인 | 81 | 6 | 7.40 |
    | 케이스 | 96 | 7 | 7.30 |
    | Intel 소켓 | 92 | 5 | 5.40 |
    | DDR5 | 64 | 3 | 4.70 |
    | 유선 | 22 | 1 | 4.50 |
    | AMD | 47 | 2 | 4.30 |


---


### 24. 고객 문의 응답 분석: 문의 유형별 평균 해결 시간, 해결률, 에스컬레이션 비율을 조회하세요.


고객 문의 응답 분석: 문의 유형별 평균 해결 시간, 해결률, 에스컬레이션 비율을 조회하세요.


**힌트 1:** `julianday(resolved_at) - julianday(created_at)`로 해결 시간. `SUM(escalated)`로 에스컬레이션 집계.


??? success "정답"
    ```sql
    SELECT
        category,
        COUNT(*) AS total_count,
        ROUND(AVG(CASE WHEN resolved_at IS NOT NULL THEN julianday(resolved_at) - julianday(created_at) END), 1) AS avg_resolve_days,
        ROUND(100.0 * SUM(CASE WHEN resolved_at IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS resolve_rate_pct,
        ROUND(100.0 * SUM(escalated) / COUNT(*), 1) AS escalation_rate_pct
    FROM complaints
    GROUP BY category
    ORDER BY total_count DESC;
    ```


    **실행 결과** (7행)

    | category | total_count | avg_resolve_days | resolve_rate_pct | escalation_rate_pct |
    |---|---|---|---|---|
    | general_inquiry | 1232 | 1.70 | 94.20 | 4.20 |
    | delivery_issue | 708 | 0.7 | 95.60 | 4.90 |
    | refund_request | 522 | 0.8 | 94.40 | 11.10 |
    | product_defect | 460 | 0.6 | 95.00 | 12.20 |
    | price_inquiry | 439 | 1.60 | 95.70 | 3.20 |
    | wrong_item | 240 | 0.6 | 94.20 | 6.70 |
    | exchange_request | 212 | 1.30 | 95.30 | 14.60 |


---


### 25. 종합 대시보드 쿼리: 총 고객 수, 활성 고객 수, 이번 달/지난 달 매출, 평균 주문 금액, 평균 리뷰 평


종합 대시보드 쿼리: 총 고객 수, 활성 고객 수, 이번 달/지난 달 매출, 평균 주문 금액, 평균 리뷰 평점, 미해결 문의 건수를 한 번에 조회하세요.


**힌트 1:** 각 KPI를 `SELECT '지표명' AS metric, 값 AS value` 형태로 만들고 `UNION ALL`로 합칩니다.


??? success "정답"
    ```sql
    SELECT '총 고객 수' AS metric, CAST(COUNT(*) AS TEXT) AS value FROM customers
    UNION ALL
    SELECT '활성 고객 수', CAST(COUNT(*) AS TEXT) FROM customers WHERE is_active = 1
    UNION ALL
    SELECT '이번 달 매출', CAST(COALESCE(SUM(total_amount), 0) AS TEXT) FROM orders WHERE SUBSTR(ordered_at, 1, 7) = strftime('%Y-%m', 'now') AND status NOT IN ('cancelled')
    UNION ALL
    SELECT '지난 달 매출', CAST(COALESCE(SUM(total_amount), 0) AS TEXT) FROM orders WHERE SUBSTR(ordered_at, 1, 7) = strftime('%Y-%m', 'now', '-1 month') AND status NOT IN ('cancelled')
    UNION ALL
    SELECT '평균 주문 금액', CAST(ROUND(AVG(total_amount)) AS TEXT) FROM orders WHERE status NOT IN ('cancelled')
    UNION ALL
    SELECT '평균 리뷰 평점', CAST(ROUND(AVG(rating), 2) AS TEXT) FROM reviews
    UNION ALL
    SELECT '미해결 문의', CAST(COUNT(*) AS TEXT) FROM complaints WHERE status NOT IN ('resolved', 'closed');
    ```


    **실행 결과** (7행)

    | metric | value |
    |---|---|
    | 총 고객 수 | 5230 |
    | 활성 고객 수 | 3660 |
    | 이번 달 매출 | 0 |
    | 지난 달 매출 | 0 |
    | 평균 주문 금액 | 1015193.0 |
    | 평균 리뷰 평점 | 3.9 |
    | 미해결 문의 | 197 |


---
