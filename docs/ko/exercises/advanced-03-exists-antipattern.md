# EXISTS와 안티 패턴

!!! info "사용 테이블"

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `reviews` — 리뷰 (평점, 내용)  

    `wishlists` — 위시리스트 (고객-상품)  

    `complaints` — 고객 불만 (유형, 우선순위)  

    `categories` — 카테고리 (부모-자식 계층)  

    `payments` — 결제 (방법, 금액, 상태)  



!!! abstract "학습 범위"

    `EXISTS`, `NOT EXISTS`, `Correlated Subquery`, `Anti-join Pattern`, `Universal Quantification`, `Double Negation`



### 1. 2024년에 주문을 한 적이 있는 고객만 조회하세요.


고객 ID, 이름, 등급, 가입일을 표시합니다. `EXISTS`를 사용하세요.


**힌트 1:** `WHERE EXISTS (SELECT 1 FROM orders WHERE customer_id = c.id AND ...)`
서브쿼리에서 외부 쿼리의 `c.id`를 참조하는 것이 상관 서브쿼리입니다.



??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        c.created_at AS signup_date
    FROM customers AS c
    WHERE EXISTS (
        SELECT 1
        FROM orders AS o
        WHERE o.customer_id = c.id
          AND o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    ORDER BY c.id
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | id | name | grade | signup_date |
    |---|---|---|---|
    | 2 | 김경수 | GOLD | 2016-08-17 12:29:34 |
    | 3 | 김민재 | VIP | 2016-02-11 19:59:38 |
    | 4 | 진정자 | GOLD | 2016-09-18 15:29:45 |
    | 5 | 이정수 | SILVER | 2016-02-28 11:34:16 |
    | 8 | 성민석 | SILVER | 2016-09-24 06:49:22 |
    | 10 | 박지훈 | GOLD | 2016-12-20 04:06:43 |
    | 12 | 장준서 | GOLD | 2016-12-30 06:48:08 |


---


### 2. 한 번도 주문한 적이 없는 고객을 찾으세요.


가입만 하고 주문 이력이 전혀 없는 고객입니다. `NOT EXISTS`를 사용하세요.


**힌트 1:** `WHERE NOT EXISTS (SELECT 1 FROM orders WHERE customer_id = c.id)`
이때 취소/반품 주문도 "주문한 적 있음"으로 간주합니다 (상태 필터 없음).



??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        c.created_at AS signup_date,
        ROUND(JULIANDAY('2025-12-31') - JULIANDAY(c.created_at), 0) AS days_since_signup
    FROM customers AS c
    WHERE NOT EXISTS (
        SELECT 1
        FROM orders AS o
        WHERE o.customer_id = c.id
    )
    ORDER BY c.created_at
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | id | name | grade | signup_date | days_since_signup |
    |---|---|---|---|---|
    | 84 | 양영진 | BRONZE | 2016-01-03 19:49:46 | 3,649.00 |
    | 38 | 박준영 | BRONZE | 2016-01-15 19:21:20 | 3,637.00 |
    | 9 | 주경희 | BRONZE | 2016-01-26 09:42:20 | 3,627.00 |
    | 69 | 이경수 | BRONZE | 2016-02-03 03:40:29 | 3,619.00 |
    | 25 | 윤준영 | BRONZE | 2016-02-03 04:18:52 | 3,619.00 |
    | 32 | 박수빈 | BRONZE | 2016-02-09 18:54:54 | 3,612.00 |
    | 7 | 김명자 | BRONZE | 2016-02-17 13:41:08 | 3,604.00 |


---


### 3. 리뷰를 남기지 않은 구매 확인 고객을 찾으세요.


주문 상태가 'confirmed'인 주문이 있지만 리뷰를 단 한 건도 작성하지 않은 고객입니다.


**힌트 1:** 조건 2개를 조합합니다:
`EXISTS (... orders WHERE status = 'confirmed')` AND
`NOT EXISTS (... reviews WHERE customer_id = c.id)`.



??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(o.id) AS confirmed_orders
    FROM customers AS c
    INNER JOIN orders AS o
        ON c.id = o.customer_id
       AND o.status = 'confirmed'
    WHERE NOT EXISTS (
        SELECT 1
        FROM reviews AS r
        WHERE r.customer_id = c.id
    )
    GROUP BY c.id, c.name, c.grade
    ORDER BY confirmed_orders DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | id | name | grade | confirmed_orders |
    |---|---|---|---|
    | 494 | 이지우 | GOLD | 20 |
    | 124 | 김시우 | BRONZE | 13 |
    | 1207 | 김지민 | SILVER | 12 |
    | 1620 | 장정순 | BRONZE | 12 |
    | 2164 | 백중수 | SILVER | 12 |
    | 2236 | 문정식 | BRONZE | 12 |
    | 2487 | 오수민 | BRONZE | 12 |


---


### 4. 위시리스트에 담았지만 아직 구매하지 않은 상품-고객 조합을 찾으세요.


위시리스트의 `is_purchased = 0`인 항목 중, 해당 고객이 해당 상품을 실제로 주문한 적도 없는 경우입니다.


**힌트 1:** `wishlists`를 기준으로, `NOT EXISTS`로 `order_items`와 `orders`를 결합한 서브쿼리를 만듭니다.
서브쿼리 조건: 같은 `customer_id`와 같은 `product_id`.



??? success "정답"
    ```sql
    SELECT
        w.customer_id,
        c.name     AS customer_name,
        w.product_id,
        p.name     AS product_name,
        p.price,
        w.created_at AS wishlisted_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products  AS p ON w.product_id  = p.id
    WHERE w.is_purchased = 0
      AND NOT EXISTS (
          SELECT 1
          FROM order_items AS oi
          INNER JOIN orders AS o ON oi.order_id = o.id
          WHERE o.customer_id = w.customer_id
            AND oi.product_id = w.product_id
            AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    ORDER BY w.created_at DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | customer_id | customer_name | product_id | product_name | price | wishlisted_at |
    |---|---|---|---|---|---|
    | 4853 | 박성호 | 92 | 주연 리오나인 미니PC | 1,194,000.00 | 2025-12-30 19:11:10 |
    | 5229 | 김영숙 | 223 | 삼성 갤럭시북4 360 블랙 | 1,388,600.00 | 2025-12-30 17:42:08 |
    | 4675 | 백지후 | 271 | TP-Link TL-SG108 | 108,500.00 | 2025-12-30 11:47:20 |
    | 4940 | 이영수 | 191 | Seagate IronWolf 4TB 블랙 | 545,400.00 | 2025-12-30 10:41:18 |
    | 3584 | 이정순 | 194 | SK하이닉스 Platinum P41 2TB 블랙 | 237,500.00 | 2025-12-30 10:16:54 |
    | 4546 | 문하은 | 239 | TeamGroup T-Force Vulcan DDR5 32GB 52... | 139,800.00 | 2025-12-30 09:25:54 |
    | 4796 | 김현주 | 171 | APC Back-UPS Pro Gaming BGM1500B 블랙 | 516,300.00 | 2025-12-30 06:38:37 |


---


### 5. CS 문의가 접수된 적이 없는 고객 중, 주문 금액 상위 10명을 찾으세요.


클레임 없이 꾸준히 구매하는 "우량 고객"을 식별합니다.


**힌트 1:** `NOT EXISTS (SELECT 1 FROM complaints WHERE customer_id = c.id)`로 문의 이력이 없는 고객을 필터링하고,
`SUM(total_amount)`으로 총 구매 금액 상위 10명을 추출합니다.



??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      AND NOT EXISTS (
          SELECT 1
          FROM complaints AS cp
          WHERE cp.customer_id = c.id
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | id | name | grade | order_count | total_spent |
    |---|---|---|---|---|
    | 514 | 오현준 | BRONZE | 5 | 52,141,700.00 |
    | 3000 | 허도윤 | GOLD | 47 | 51,674,714.00 |
    | 4065 | 박영자 | VIP | 12 | 43,306,619.00 |
    | 41 | 노상훈 | BRONZE | 34 | 42,490,481.00 |
    | 44 | 김하은 | BRONZE | 45 | 40,153,649.00 |
    | 4136 | 김영미 | VIP | 4 | 39,557,863.00 |
    | 1131 | 이경자 | SILVER | 36 | 39,097,438.00 |


---


### 6. 3개 이상의 서로 다른 카테고리에서 상품을 구매한 고객을 찾으세요.


EXISTS 내부에서 집계를 사용합니다.


**힌트 1:** `EXISTS` 안에서 `GROUP BY customer_id HAVING COUNT(DISTINCT category_id) >= 3`을 사용합니다.
또는 상관 서브쿼리로 카테고리 수를 세는 방법도 있습니다.



??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade
    FROM customers AS c
    WHERE EXISTS (
        SELECT 1
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.customer_id = c.id
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY o.customer_id
        HAVING COUNT(DISTINCT p.category_id) >= 3
    )
    ORDER BY c.grade DESC, c.name
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | id | name | grade |
    |---|---|---|
    | 3645 | 강경숙 | VIP |
    | 162 | 강명자 | VIP |
    | 824 | 강민석 | VIP |
    | 1516 | 강민재 | VIP |
    | 1613 | 강상철 | VIP |
    | 3678 | 강순옥 | VIP |
    | 2454 | 강옥순 | VIP |


---


### 7. 모든 결제가 정상 완료된 주문만 조회하세요.


한 주문에 여러 결제가 있을 수 있습니다. 실패(`failed`)나 환불(`refunded`)된 결제가 하나라도 없는 주문을 찾습니다.


**힌트 1:** "실패/환불이 없다" = `NOT EXISTS (... payments WHERE status IN ('failed', 'refunded') AND order_id = o.id)`.
추가로 결제가 하나 이상 존재해야 합니다(`EXISTS`).



??? success "정답"
    ```sql
    SELECT
        o.id,
        o.order_number,
        o.total_amount,
        o.ordered_at,
        o.status
    FROM orders AS o
    WHERE EXISTS (
        SELECT 1
        FROM payments AS p
        WHERE p.order_id = o.id
          AND p.status = 'completed'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM payments AS p
        WHERE p.order_id = o.id
          AND p.status IN ('failed', 'refunded')
    )
    AND o.ordered_at LIKE '2024%'
    ORDER BY o.ordered_at DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | id | order_number | total_amount | ordered_at | status |
    |---|---|---|---|---|
    | 31,230 | ORD-20241231-31230 | 506,700.00 | 2024-12-31 21:25:24 | confirmed |
    | 31,229 | ORD-20241231-31229 | 425,600.00 | 2024-12-31 20:47:26 | confirmed |
    | 31,228 | ORD-20241231-31228 | 548,900.00 | 2024-12-31 20:17:42 | confirmed |
    | 31,223 | ORD-20241231-31223 | 531,300.00 | 2024-12-31 19:30:18 | confirmed |
    | 31,226 | ORD-20241231-31226 | 500,100.00 | 2024-12-31 19:28:26 | confirmed |
    | 31,238 | ORD-20241231-31238 | 658,500.00 | 2024-12-31 16:08:40 | confirmed |
    | 31,236 | ORD-20241231-31236 | 144,100.00 | 2024-12-31 15:52:45 | confirmed |


---


### 8. 특정 상품(ID=1)과 함께 자주 구매되는 상품을 찾으세요 (동시 구매 분석).


상품 1을 포함한 주문에서, 상품 1 이외의 다른 상품 중 동시 구매 빈도가 높은 순으로 정렬합니다.


**힌트 1:** 외부 쿼리는 `order_items`에서 `product_id != 1`인 항목을 집계합니다.
`EXISTS`로 "해당 주문에 상품 1이 포함되어 있는지"를 확인합니다.



??? success "정답"
    ```sql
    SELECT
        p.id    AS product_id,
        p.name  AS product_name,
        p.price,
        COUNT(DISTINCT oi.order_id) AS co_purchase_count
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    WHERE oi.product_id != 1
      AND EXISTS (
          SELECT 1
          FROM order_items AS oi2
          WHERE oi2.order_id   = oi.order_id
            AND oi2.product_id = 1
      )
    GROUP BY p.id, p.name, p.price
    ORDER BY co_purchase_count DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | product_id | product_name | price | co_purchase_count |
    |---|---|---|---|
    | 45 | SteelSeries Aerox 5 Wireless 실버 | 100,000.00 | 33 |
    | 70 | JBL Pebbles 2 블랙 | 101,500.00 | 31 |
    | 9 | 소니 WH-CH720N 실버 | 445,700.00 | 30 |
    | 28 | Keychron Q1 Pro 실버 | 238,000.00 | 26 |
    | 8 | 로지텍 G715 화이트 | 131,500.00 | 25 |
    | 34 | SteelSeries Prime Wireless 블랙 | 89,800.00 | 25 |
    | 111 | 로지텍 G502 X PLUS | 97,500.00 | 24 |


---


### 9. "매월 빠짐없이 주문한 고객"을 찾으세요 (2024년 12개월).


2024년의 모든 12개월에 최소 1건의 주문이 있는 고객입니다.


**힌트 1:** `NOT EXISTS`와 재귀 CTE(또는 하드코딩된 월 리스트)를 조합합니다.
"모든 월에 주문이 있다" = "주문이 없는 월이 존재하지 않는다" (NOT EXISTS).



??? success "정답"
    ```sql
    WITH RECURSIVE months AS (
        SELECT '2024-01' AS ym
        UNION ALL
        SELECT SUBSTR(DATE(ym || '-01', '+1 month'), 1, 7)
        FROM months
        WHERE ym < '2024-12'
    )
    SELECT
        c.id,
        c.name,
        c.grade
    FROM customers AS c
    WHERE NOT EXISTS (
        -- 주문이 없는 월이 하나라도 있으면 제외
        SELECT 1
        FROM months AS m
        WHERE NOT EXISTS (
            SELECT 1
            FROM orders AS o
            WHERE o.customer_id = c.id
              AND SUBSTR(o.ordered_at, 1, 7) = m.ym
              AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        )
    )
    ORDER BY c.grade DESC, c.name;
    ```


    **실행 결과** (3행)

    | id | name | grade |
    |---|---|---|
    | 3097 | 심승현 | VIP |
    | 2516 | 이정숙 | VIP |
    | 3775 | 황정자 | VIP |


---


### 10. 2024년에 주문은 했지만 2025년에는 주문하지 않은 "이탈 고객"을 찾으세요.


두 개의 EXISTS/NOT EXISTS 조건을 결합합니다.


**힌트 1:** `EXISTS (... 2024년 주문)` AND `NOT EXISTS (... 2025년 주문)`.
이탈 고객의 2024년 마지막 주문일과 총 구매 금액도 표시하면 유용합니다.



??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order_date,
        COUNT(o.id) AS orders_in_2024,
        ROUND(SUM(o.total_amount), 0) AS spent_in_2024
    FROM customers AS c
    INNER JOIN orders AS o
        ON c.id = o.customer_id
       AND o.ordered_at LIKE '2024%'
       AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    WHERE NOT EXISTS (
        SELECT 1
        FROM orders AS o2
        WHERE o2.customer_id = c.id
          AND o2.ordered_at LIKE '2025%'
          AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    GROUP BY c.id, c.name, c.grade
    ORDER BY spent_in_2024 DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | id | name | grade | last_order_date | orders_in_2024 | spent_in_2024 |
    |---|---|---|---|---|---|
    | 2623 | 김서준 | BRONZE | 2024-09-18 20:22:57 | 4 | 17,088,500.00 |
    | 2894 | 한미영 | BRONZE | 2024-05-24 09:44:28 | 1 | 14,204,200.00 |
    | 1724 | 김서연 | BRONZE | 2024-08-03 08:13:36 | 3 | 12,494,600.00 |
    | 3667 | 안예은 | BRONZE | 2024-12-10 12:12:19 | 2 | 12,260,100.00 |
    | 1186 | 박진우 | BRONZE | 2024-10-24 20:05:01 | 3 | 9,588,499.00 |
    | 2814 | 김수민 | BRONZE | 2024-08-26 20:19:31 | 2 | 8,290,525.00 |
    | 2236 | 문정식 | BRONZE | 2024-11-21 11:34:35 | 4 | 7,629,400.00 |


---


### 11. 모든 주문에서 카드로만 결제한 고객을 찾으세요.


카드 외 결제 수단(kakao_pay, naver_pay, bank_transfer 등)을 한 번도 사용하지 않은 고객입니다.


**힌트 1:** 전칭 한정: "모든 결제가 카드" = "카드가 아닌 결제가 **존재하지 않는다**".
`NOT EXISTS (... payments WHERE method != 'card' ...)`를 사용합니다.
주문 이력이 있는 고객만 대상으로 합니다.



??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      -- 카드가 아닌 결제가 한 건도 없어야 함
      AND NOT EXISTS (
          SELECT 1
          FROM payments AS p
          INNER JOIN orders AS o2 ON p.order_id = o2.id
          WHERE o2.customer_id = c.id
            AND p.method != 'card'
      )
      -- 결제 이력이 있어야 함
      AND EXISTS (
          SELECT 1
          FROM payments AS p
          INNER JOIN orders AS o3 ON p.order_id = o3.id
          WHERE o3.customer_id = c.id
            AND p.method = 'card'
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | id | name | grade | order_count | total_spent |
    |---|---|---|---|---|
    | 4213 | 오서윤 | VIP | 1 | 13,895,400.00 |
    | 4179 | 이광수 | VIP | 1 | 8,319,100.00 |
    | 3138 | 김서준 | GOLD | 4 | 6,843,700.00 |
    | 2027 | 이영환 | BRONZE | 2 | 6,285,000.00 |
    | 3785 | 홍명자 | GOLD | 4 | 5,791,400.00 |
    | 1120 | 서상훈 | BRONZE | 5 | 5,519,100.00 |
    | 2119 | 서도윤 | BRONZE | 3 | 5,265,400.00 |


---


### 12. "모든 종류의 문의 카테고리"를 경험한 고객을 찾으세요.


`complaints` 테이블의 모든 `category` 값에 대해 최소 1건의 문의를 제출한 고객입니다.


**힌트 1:** 전칭 한정의 이중 부정 패턴:
"모든 카테고리에 문의가 있다" = "문의가 없는 카테고리가 **존재하지 않는다**".
`NOT EXISTS (SELECT category FROM (SELECT DISTINCT category FROM complaints) WHERE NOT EXISTS (... 해당 고객의 해당 카테고리 문의))`.



??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        (SELECT COUNT(DISTINCT cp.category) FROM complaints AS cp WHERE cp.customer_id = c.id) AS category_count
    FROM customers AS c
    WHERE NOT EXISTS (
        -- 문의가 없는 카테고리가 하나라도 있으면 제외
        SELECT DISTINCT cp_all.category
        FROM complaints AS cp_all
        WHERE NOT EXISTS (
            SELECT 1
            FROM complaints AS cp
            WHERE cp.customer_id = c.id
              AND cp.category = cp_all.category
        )
    )
    ORDER BY c.name;
    ```


    **실행 결과** (총 8행 중 상위 7행)

    | id | name | grade | category_count |
    |---|---|---|---|
    | 258 | 김경희 | GOLD | 7 |
    | 97 | 김병철 | VIP | 7 |
    | 489 | 박경숙 | VIP | 7 |
    | 549 | 이미정 | VIP | 7 |
    | 98 | 이영자 | VIP | 7 |
    | 744 | 이채원 | VIP | 7 |
    | 1388 | 이현지 | VIP | 7 |


---


### 13. "가격이 100만원 이상인 상품만 구매한" 고객을 찾으세요.


저가 상품을 한 번도 구매하지 않은 프리미엄 고객입니다.


**힌트 1:** "100만원 미만 상품 구매가 존재하지 않는다":
`NOT EXISTS (... order_items JOIN products WHERE price < 1000000 AND customer_id = c.id)`.
동시에 주문 이력은 있어야 합니다(`EXISTS`).



??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent,
        ROUND(AVG(o.total_amount), 0) AS avg_order_value
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      -- 100만원 미만 상품 구매가 없어야 함
      AND NOT EXISTS (
          SELECT 1
          FROM order_items AS oi
          INNER JOIN orders AS o2 ON oi.order_id = o2.id
          INNER JOIN products AS p ON oi.product_id = p.id
          WHERE o2.customer_id = c.id
            AND p.price < 1000000
            AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```


    **실행 결과** (2행)

    | id | name | grade | order_count | total_spent | avg_order_value |
    |---|---|---|---|---|---|
    | 4137 | 김재호 | BRONZE | 1 | 4,352,405.00 | 4,352,405.00 |
    | 4973 | 류준호 | SILVER | 1 | 1,204,536.00 | 1,204,536.00 |


---


### 14. 재구매 상품 쌍을 찾으세요 — 같은 고객이 다른 주문에서 동일 상품을 2번 이상 구매한 경우입니다.


EXISTS로 "동일 고객, 동일 상품, 다른 주문"을 확인합니다.


**힌트 1:** `order_items`를 기준으로, `EXISTS`에서 같은 `product_id`, 같은 `customer_id`이지만
다른 `order_id`인 레코드가 있는지 확인합니다.
고객-상품 조합별로 재구매 횟수를 집계합니다.



??? success "정답"
    ```sql
    SELECT
        c.name     AS customer_name,
        p.name     AS product_name,
        COUNT(DISTINCT oi.order_id) AS purchase_count,
        SUM(oi.quantity) AS total_qty
    FROM order_items AS oi
    INNER JOIN orders    AS o ON oi.order_id   = o.id
    INNER JOIN customers AS c ON o.customer_id = c.id
    INNER JOIN products  AS p ON oi.product_id = p.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      AND EXISTS (
          -- 같은 고객이 같은 상품을 다른 주문에서 구매
          SELECT 1
          FROM order_items AS oi2
          INNER JOIN orders AS o2 ON oi2.order_id = o2.id
          WHERE o2.customer_id = o.customer_id
            AND oi2.product_id = oi.product_id
            AND oi2.order_id   != oi.order_id
            AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    GROUP BY c.id, c.name, p.id, p.name
    ORDER BY purchase_count DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | customer_name | product_name | purchase_count | total_qty |
    |---|---|---|---|
    | 이영자 | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 37 | 37 |
    | 이영자 | 삼성 오디세이 G7 32 화이트 | 25 | 25 |
    | 이영자 | 삼성 DDR5 32GB PC5-38400 | 24 | 24 |
    | 김병철 | 삼성 DDR4 32GB PC4-25600 | 23 | 30 |
    | 김병철 | be quiet! Light Base 900 | 22 | 28 |
    | 김병철 | AMD Ryzen 9 9900X | 22 | 22 |
    | 김병철 | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 21 | 21 |


---


### 15. "NOT EXISTS vs LEFT JOIN IS NULL" 안티 조인 패턴을 비교하세요.


2024년에 리뷰를 남기지 않은 상품을 두 가지 방법으로 조회하고, 결과가 동일한지 확인합니다.


**힌트 1:** 방법 1: `NOT EXISTS (SELECT 1 FROM reviews WHERE product_id = p.id AND created_at LIKE '2024%')`.
방법 2: `LEFT JOIN reviews ON ... WHERE r.id IS NULL`.
두 쿼리를 `EXCEPT`로 비교하면 차집합이 비어 있어야 합니다.



??? success "정답"
    ```sql
    -- 방법 1: NOT EXISTS
    SELECT p.id, p.name
    FROM products AS p
    WHERE p.is_active = 1
      AND NOT EXISTS (
          SELECT 1
          FROM reviews AS r
          WHERE r.product_id = p.id
            AND r.created_at LIKE '2024%'
      )
    ORDER BY p.id;
    
    -- 방법 2: LEFT JOIN ... IS NULL
    SELECT p.id, p.name
    FROM products AS p
    LEFT JOIN reviews AS r
        ON r.product_id = p.id
       AND r.created_at LIKE '2024%'
    WHERE p.is_active = 1
      AND r.id IS NULL
    ORDER BY p.id;
    
    -- 동일성 검증: 차집합이 비어야 함
    SELECT p.id, p.name
    FROM products AS p
    WHERE p.is_active = 1
      AND NOT EXISTS (
          SELECT 1 FROM reviews AS r
          WHERE r.product_id = p.id AND r.created_at LIKE '2024%'
      )
    
    EXCEPT
    
    SELECT p.id, p.name
    FROM products AS p
    LEFT JOIN reviews AS r
        ON r.product_id = p.id AND r.created_at LIKE '2024%'
    WHERE p.is_active = 1
      AND r.id IS NULL;
    ```


---
