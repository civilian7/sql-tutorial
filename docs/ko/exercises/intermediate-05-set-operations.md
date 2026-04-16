# 집합 연산

!!! info "사용 테이블"

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `reviews` — 리뷰 (평점, 내용)  

    `complaints` — 고객 불만 (유형, 우선순위)  

    `wishlists` — 위시리스트 (고객-상품)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `payments` — 결제 (방법, 금액, 상태)  

    `returns` — 반품/교환 (사유, 상태)  



!!! abstract "학습 범위"

    `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT`, `set operations with JOIN/GROUP BY`



### 1. 리뷰를 작성한 고객과 불만을 접수한 고객의 이름을 중복 없이 합쳐서 조회하세요. 이름순, 상위 20명.


리뷰를 작성한 고객과 불만을 접수한 고객의 이름을 중복 없이 합쳐서 조회하세요. 이름순, 상위 20명.


**힌트 1:** `SELECT customer_id FROM reviews UNION SELECT customer_id FROM complaints` — 양쪽 모두에 존재하는 고객은 한 번만 나타납니다.


??? success "정답"
    ```sql
    SELECT c.name, c.email
    FROM customers AS c
    WHERE c.id IN (
        SELECT customer_id FROM reviews
        UNION
        SELECT customer_id FROM complaints
    )
    ORDER BY c.name
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | name | email |
    |---|---|
    | 강경숙 | user2384@testmail.kr |
    | 강경숙 | user3645@testmail.kr |
    | 강경자 | user1109@testmail.kr |
    | 강경희 | user2103@testmail.kr |
    | 강도윤 | user1492@testmail.kr |
    | 강동현 | user3882@testmail.kr |
    | 강명숙 | user4238@testmail.kr |


---


### 2. 리뷰를 작성한 고객과 불만을 접수한 고객의 ID를 중복 포함하여 합치고, 전체 건수를 세어보세요.


리뷰를 작성한 고객과 불만을 접수한 고객의 ID를 중복 포함하여 합치고, 전체 건수를 세어보세요.


**힌트 1:** `UNION ALL`로 합친 뒤 `COUNT(*)`로 전체 건수를 구합니다. UNION과 비교하면 건수 차이가 있습니다.


??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_with_dup
    FROM (
        SELECT customer_id FROM reviews
        UNION ALL
        SELECT customer_id FROM complaints
    );
    ```


    **실행 결과** (1행)

    | total_with_dup |
    |---|
    | 12,359 |


---


### 3. 2024년과 2025년 각각의 주문 건수를 하나의 결과로 합쳐서 보세요.


2024년과 2025년 각각의 주문 건수를 하나의 결과로 합쳐서 보세요.


**힌트 1:** `SELECT '2024' AS year, COUNT(*) ... UNION ALL SELECT '2025' AS year, COUNT(*) ...` — 리터럴 컬럼으로 구분합니다.


??? success "정답"
    ```sql
    SELECT '2024' AS year,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND status NOT IN ('cancelled')
    UNION ALL
    SELECT '2025' AS year,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled');
    ```


    **실행 결과** (2행)

    | year | order_count | revenue |
    |---|---|---|
    | 2024 | 5474 | 5,346,776,711.00 |
    | 2025 | 5993 | 6,398,165,081.00 |


---


### 4. 위시리스트에 담긴 상품 ID와 실제 주문된 상품 ID를 중복 없이 합쳐서 총 몇 종류인지 세어보세요.


위시리스트에 담긴 상품 ID와 실제 주문된 상품 ID를 중복 없이 합쳐서 총 몇 종류인지 세어보세요.


**힌트 1:** `SELECT product_id FROM wishlists UNION SELECT product_id FROM order_items` — 합집합의 행 수가 곧 종류 수입니다.


??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_products
    FROM (
        SELECT product_id FROM wishlists
        UNION
        SELECT product_id FROM order_items
    );
    ```


    **실행 결과** (1행)

    | total_products |
    |---|
    | 280 |


---


### 5. 주문 취소 이벤트와 반품 요청 이벤트를 하나의 타임라인으로 합치세요. 최근 20건.


주문 취소 이벤트와 반품 요청 이벤트를 하나의 타임라인으로 합치세요. 최근 20건.


**힌트 1:** 이벤트 유형을 구분하는 리터럴 컬럼을 추가하세요. ORDER BY는 전체 결과에 적용됩니다.


??? success "정답"
    ```sql
    SELECT '취소' AS event_type,
           order_number AS reference,
           cancelled_at AS event_date
    FROM orders
    WHERE status = 'cancelled' AND cancelled_at IS NOT NULL
    UNION ALL
    SELECT '반품' AS event_type,
           CAST(order_id AS TEXT) AS reference,
           requested_at AS event_date
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


### 6. 2025년 월별 매출과 함께 연간 합계 행을 추가하세요.


2025년 월별 매출과 함께 연간 합계 행을 추가하세요.


**힌트 1:** 월별 `GROUP BY` 결과에 `UNION ALL`로 전체 합계 행을 추가합니다.


??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    UNION ALL
    SELECT
        '== 합계 ==' AS month,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled')
    ORDER BY month;
    ```


    **실행 결과** (총 13행 중 상위 7행)

    | month | order_count | revenue |
    |---|---|---|
    | 2025-01 | 461 | 491,947,609.00 |
    | 2025-02 | 428 | 422,980,126.00 |
    | 2025-03 | 619 | 656,638,842.00 |
    | 2025-04 | 467 | 517,070,656.00 |
    | 2025-05 | 466 | 514,287,052.00 |
    | 2025-06 | 436 | 457,780,698.00 |
    | 2025-07 | 402 | 404,813,220.00 |


---


### 7. 결제 수단별 건수를 조회하되, 마지막 행에 전체 합계를 추가하세요.


결제 수단별 건수를 조회하되, 마지막 행에 전체 합계를 추가하세요.


**힌트 1:** `SELECT method, COUNT(*), SUM(amount) FROM payments GROUP BY method UNION ALL SELECT '합계', COUNT(*), SUM(amount) FROM payments` 구조입니다.


??? success "정답"
    ```sql
    SELECT
        method,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS total_amount
    FROM payments
    WHERE status = 'completed'
    GROUP BY method
    UNION ALL
    SELECT
        '== 합계 ==' AS method,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS total_amount
    FROM payments
    WHERE status = 'completed'
    ORDER BY
        CASE WHEN method = '== 합계 ==' THEN 1 ELSE 0 END,
        tx_count DESC;
    ```


---


### 8. 리뷰를 작성하고 불만도 접수한 고객(교집합)을 찾으세요. 이름순, 상위 15명.


리뷰를 작성하고 불만도 접수한 고객(교집합)을 찾으세요. 이름순, 상위 15명.


**힌트 1:** `SELECT customer_id FROM reviews INTERSECT SELECT customer_id FROM complaints` — 양쪽 모두에 존재하는 고객 ID만 반환합니다.


??? success "정답"
    ```sql
    SELECT c.name, c.email, c.grade
    FROM customers AS c
    WHERE c.id IN (
        SELECT customer_id FROM reviews
        INTERSECT
        SELECT customer_id FROM complaints
    )
    ORDER BY c.name
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | name | email | grade |
    |---|---|---|
    | 강경숙 | user2384@testmail.kr | SILVER |
    | 강경자 | user1109@testmail.kr | BRONZE |
    | 강도윤 | user1492@testmail.kr | BRONZE |
    | 강명자 | user162@testmail.kr | VIP |
    | 강명자 | user1782@testmail.kr | BRONZE |
    | 강미영 | user3231@testmail.kr | SILVER |
    | 강민석 | user824@testmail.kr | VIP |


---


### 9. 위시리스트에 담았지만 한 번도 주문하지 않은 상품(차집합)을 찾으세요. 가격 내림차순, 상위 15개.


위시리스트에 담았지만 한 번도 주문하지 않은 상품(차집합)을 찾으세요. 가격 내림차순, 상위 15개.


**힌트 1:** `SELECT product_id FROM wishlists EXCEPT SELECT product_id FROM order_items` — 위시리스트에만 있고 주문에는 없는 상품 ID입니다.


??? success "정답"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    WHERE p.id IN (
        SELECT product_id FROM wishlists
        EXCEPT
        SELECT product_id FROM order_items
    )
    ORDER BY p.price DESC
    LIMIT 15;
    ```


---


### 10. 2024년에는 주문했지만 2025년에는 주문하지 않은 고객을 찾으세요. 이름순, 상위 20명.


2024년에는 주문했지만 2025년에는 주문하지 않은 고객을 찾으세요. 이름순, 상위 20명.


**힌트 1:** `SELECT customer_id FROM orders WHERE ordered_at LIKE '2024%' EXCEPT SELECT customer_id FROM orders WHERE ordered_at LIKE '2025%'` — 2024년 고객에서 2025년 고객을 뺍니다.


??? success "정답"
    ```sql
    SELECT c.name, c.grade, c.email
    FROM customers AS c
    WHERE c.id IN (
        SELECT customer_id
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled')
        EXCEPT
        SELECT customer_id
        FROM orders
        WHERE ordered_at LIKE '2025%'
          AND status NOT IN ('cancelled')
    )
    ORDER BY c.name
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | name | grade | email |
    |---|---|---|
    | 강경희 | BRONZE | user2103@testmail.kr |
    | 강광수 | BRONZE | user3374@testmail.kr |
    | 강병철 | BRONZE | user1870@testmail.kr |
    | 강서윤 | BRONZE | user2738@testmail.kr |
    | 강윤서 | BRONZE | user3638@testmail.kr |
    | 강은서 | BRONZE | user15@testmail.kr |
    | 강종수 | BRONZE | user3902@testmail.kr |


---


### 11. 고객 활동 유형별 건수를 하나의 보고서로 합치세요 (주문, 리뷰, 불만, 위시리스트).


고객 활동 유형별 건수를 하나의 보고서로 합치세요 (주문, 리뷰, 불만, 위시리스트).


**힌트 1:** `SELECT '주문' AS activity, COUNT(*) FROM orders UNION ALL SELECT '리뷰', COUNT(*) FROM reviews UNION ALL ...` — 각 SELECT의 컬럼 이름과 타입을 맞춰야 합니다.


??? success "정답"
    ```sql
    SELECT '주문' AS activity_type, COUNT(*) AS total_count
    FROM orders
    WHERE status NOT IN ('cancelled')
    UNION ALL
    SELECT '리뷰', COUNT(*)
    FROM reviews
    UNION ALL
    SELECT '불만 접수', COUNT(*)
    FROM complaints
    UNION ALL
    SELECT '위시리스트', COUNT(*)
    FROM wishlists
    ORDER BY total_count DESC;
    ```


    **실행 결과** (4행)

    | activity_type | total_count |
    |---|---|
    | 주문 | 35,698 |
    | 리뷰 | 8546 |
    | 불만 접수 | 3813 |
    | 위시리스트 | 1998 |


---


### 12. 2024년과 2025년 모두 주문한 충성 고객의 이름, 등급, 두 해의 주문 건수를 구하세요. 상위 15명.


2024년과 2025년 모두 주문한 충성 고객의 이름, 등급, 두 해의 주문 건수를 구하세요. 상위 15명.


**힌트 1:** 먼저 INTERSECT로 두 해 모두 주문한 고객 ID를 구하고, 그 고객에 대해 연도별 주문 건수를 SELECT 절 스칼라 서브쿼리로 추가합니다.


??? success "정답"
    ```sql
    SELECT
        c.name,
        c.grade,
        (SELECT COUNT(*) FROM orders
         WHERE customer_id = c.id
           AND ordered_at LIKE '2024%'
           AND status NOT IN ('cancelled')) AS orders_2024,
        (SELECT COUNT(*) FROM orders
         WHERE customer_id = c.id
           AND ordered_at LIKE '2025%'
           AND status NOT IN ('cancelled')) AS orders_2025
    FROM customers AS c
    WHERE c.id IN (
        SELECT customer_id FROM orders
        WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')
        INTERSECT
        SELECT customer_id FROM orders
        WHERE ordered_at LIKE '2025%' AND status NOT IN ('cancelled')
    )
    ORDER BY orders_2025 DESC, orders_2024 DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | name | grade | orders_2024 | orders_2025 |
    |---|---|---|---|
    | 박정수 | VIP | 16 | 24 |
    | 김현지 | VIP | 15 | 22 |
    | 이예준 | VIP | 21 | 21 |
    | 박건우 | VIP | 19 | 21 |
    | 이현지 | VIP | 14 | 21 |
    | 박현지 | VIP | 5 | 20 |
    | 한예진 | VIP | 17 | 18 |


---


### 13. 불만이 접수되었지만 반품은 하지 않은 주문의 주문번호와 금액을 구하세요. 최근 15건.


불만이 접수되었지만 반품은 하지 않은 주문의 주문번호와 금액을 구하세요. 최근 15건.


**힌트 1:** `SELECT order_id FROM complaints WHERE order_id IS NOT NULL EXCEPT SELECT order_id FROM returns` — 불만은 있지만 반품까지 이어지지 않은 주문입니다.


??? success "정답"
    ```sql
    SELECT o.order_number, o.total_amount, o.ordered_at
    FROM orders AS o
    WHERE o.id IN (
        SELECT order_id FROM complaints WHERE order_id IS NOT NULL
        EXCEPT
        SELECT order_id FROM returns
    )
    ORDER BY o.ordered_at DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | order_number | total_amount | ordered_at |
    |---|---|---|
    | ORD-20251231-37548 | 187,700.00 | 2025-12-31 18:43:56 |
    | ORD-20251231-37541 | 900,900.00 | 2025-12-31 09:27:26 |
    | ORD-20251230-37523 | 419,600.00 | 2025-12-30 18:22:10 |
    | ORD-20251229-37498 | 1,785,500.00 | 2025-12-29 15:06:38 |
    | ORD-20251228-37479 | 1,758,716.00 | 2025-12-28 22:03:50 |
    | ORD-20251228-37483 | 116,700.00 | 2025-12-28 21:32:28 |
    | ORD-20251228-37467 | 52,600.00 | 2025-12-28 15:56:10 |


---


### 14. 상품별 "리뷰 건수 + 위시리스트 등록 수"를 UNION ALL 서브쿼리로 합산하세요. 상위 10개.


상품별 "리뷰 건수 + 위시리스트 등록 수"를 UNION ALL 서브쿼리로 합산하세요. 상위 10개.


**힌트 1:** `FROM (SELECT product_id FROM reviews UNION ALL SELECT product_id FROM wishlists) AS combined` — 합친 뒤 `GROUP BY product_id`로 건수를 세면 통합 관심도가 됩니다.


??? success "정답"
    ```sql
    SELECT
        p.name,
        COUNT(*) AS interest_score
    FROM (
        SELECT product_id FROM reviews
        UNION ALL
        SELECT product_id FROM wishlists
    ) AS combined
    INNER JOIN products AS p ON combined.product_id = p.id
    GROUP BY p.id, p.name
    ORDER BY interest_score DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | interest_score |
    |---|---|
    | SteelSeries Prime Wireless 실버 | 112 |
    | Kingston FURY Beast DDR4 16GB 실버 | 110 |
    | SteelSeries Aerox 5 Wireless 실버 | 110 |
    | 로지텍 G502 X PLUS | 102 |
    | 삼성 SPA-KFG0BUB 실버 | 95 |
    | Ducky One 3 TKL 화이트 | 94 |
    | Crucial T700 2TB 실버 | 90 |


---


### 15. 2024년 분기별 신규 고객 수와 주문 고객 수를 각각 구한 뒤 하나의 보고서로 합치세요.


2024년 분기별 신규 고객 수와 주문 고객 수를 각각 구한 뒤 하나의 보고서로 합치세요.


**힌트 1:** `SELECT quarter, '신규가입' AS metric, COUNT(*) ... UNION ALL SELECT quarter, '주문' AS metric, COUNT(DISTINCT customer_id) ...` — metric 컬럼으로 지표를 구분합니다.


??? success "정답"
    ```sql
    SELECT
        'Q' || ((CAST(SUBSTR(created_at, 6, 2) AS INTEGER) - 1) / 3 + 1) AS quarter,
        '신규가입' AS metric,
        COUNT(*) AS value
    FROM customers
    WHERE created_at LIKE '2024%'
    GROUP BY quarter
    UNION ALL
    SELECT
        'Q' || ((CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) - 1) / 3 + 1) AS quarter,
        '주문고객' AS metric,
        COUNT(DISTINCT customer_id) AS value
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND status NOT IN ('cancelled')
    GROUP BY quarter
    ORDER BY quarter, metric;
    ```


    **실행 결과** (총 8행 중 상위 7행)

    | quarter | metric | value |
    |---|---|---|
    | Q1 | 신규가입 | 171 |
    | Q1 | 주문고객 | 767 |
    | Q2 | 신규가입 | 164 |
    | Q2 | 주문고객 | 766 |
    | Q3 | 신규가입 | 176 |
    | Q3 | 주문고객 | 813 |
    | Q4 | 신규가입 | 189 |


---
