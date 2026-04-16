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
    `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT`, 집합 연산 + `JOIN`/`GROUP BY`

---


## 기초 (1-5): UNION, UNION ALL 기본

### 문제 1. 리뷰를 작성한 고객과 불만을 접수한 고객의 이름을 중복 없이 합쳐서 조회하세요.

UNION은 두 SELECT 결과를 합치면서 중복을 자동 제거합니다.

??? tip "힌트"
    `SELECT customer_id FROM reviews UNION SELECT customer_id FROM complaints` — 양쪽 모두에 존재하는 고객은 한 번만 나타납니다.

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


---


### 문제 2. 리뷰를 작성한 고객과 불만을 접수한 고객의 ID를 중복 포함하여 합치고, 전체 건수를 세어보세요.

UNION ALL은 중복을 제거하지 않으므로 한 고객이 양쪽에 모두 있으면 두 번 나타납니다.

??? tip "힌트"
    `UNION ALL`로 합친 뒤 `COUNT(*)`로 전체 건수를 구합니다. UNION과 비교하면 건수 차이가 있습니다.

??? success "정답"
    ```sql
    -- UNION ALL: 중복 포함
    SELECT COUNT(*) AS total_with_dup
    FROM (
        SELECT customer_id FROM reviews
        UNION ALL
        SELECT customer_id FROM complaints
    );
    ```

    참고로 `UNION`(중복 제거)과 비교하면:

    ```sql
    -- UNION: 중복 제거
    SELECT COUNT(*) AS total_without_dup
    FROM (
        SELECT customer_id FROM reviews
        UNION
        SELECT customer_id FROM complaints
    );
    ```

    두 결과의 차이가 "양쪽 모두 활동한 고객 수"입니다.


---


### 문제 3. 2024년과 2025년 각각의 주문 건수를 하나의 결과로 합쳐서 보세요.

각 연도별 집계를 별도 SELECT로 작성한 뒤 UNION ALL로 합칩니다.

??? tip "힌트"
    `SELECT '2024' AS year, COUNT(*) ... UNION ALL SELECT '2025' AS year, COUNT(*) ...` — 리터럴 컬럼으로 구분합니다.

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

    | year | order_count | revenue |
    |------|-------------|---------|
    | 2024 | ... | ... |
    | 2025 | ... | ... |


---


### 문제 4. 위시리스트에 담긴 상품 ID와 실제 주문된 상품 ID를 중복 없이 합쳐서 총 몇 종류인지 세어보세요.

UNION으로 두 집합을 합치면 자동으로 중복이 제거됩니다.

??? tip "힌트"
    `SELECT product_id FROM wishlists UNION SELECT product_id FROM order_items` — 합집합의 행 수가 곧 "관심 또는 구매 이력이 있는 상품 종류 수"입니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_products
    FROM (
        SELECT product_id FROM wishlists
        UNION
        SELECT product_id FROM order_items
    );
    ```


---


### 문제 5. 주문 취소 이벤트와 반품 요청 이벤트를 하나의 타임라인으로 합치세요. 최근 20건.

서로 다른 테이블의 이벤트를 UNION ALL로 합쳐 통합 타임라인을 만듭니다. 컬럼 수와 타입을 맞춰야 합니다.

??? tip "힌트"
    이벤트 유형을 구분하는 리터럴 컬럼을 추가하세요. `SELECT '취소' AS event_type, ... UNION ALL SELECT '반품' AS event_type, ...` — ORDER BY는 전체 결과에 적용됩니다.

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

    | event_type | reference | event_date |
    |------------|-----------|------------|
    | 취소 | ORD-... | 2025-... |
    | 반품 | 1234 | 2025-... |
    | ... | ... | ... |


---


## 응용 (6-10): UNION ALL 집계 행, INTERSECT, EXCEPT

### 문제 6. 2025년 월별 매출과 함께 연간 합계 행을 추가하세요.

UNION ALL로 월별 집계와 전체 합계를 하나의 결과로 합칩니다.

??? tip "힌트"
    월별 `GROUP BY` 결과에 `UNION ALL`로 `'합계'`를 month에 넣은 전체 집계 행을 추가합니다.

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


---


### 문제 7. 결제 수단별 건수를 조회하되, 마지막 행에 전체 합계를 추가하세요.

UNION ALL로 GROUP BY 결과와 합계 행을 합칩니다.

??? tip "힌트"
    `SELECT method, COUNT(*), SUM(amount) FROM payments GROUP BY method UNION ALL SELECT '합계', COUNT(*), SUM(amount) FROM payments` 구조입니다.

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


### 문제 8. 리뷰를 작성하고 불만도 접수한 고객(교집합)을 찾으세요.

INTERSECT는 두 SELECT 결과의 교집합을 반환합니다.

??? tip "힌트"
    `SELECT customer_id FROM reviews INTERSECT SELECT customer_id FROM complaints` — 양쪽 모두에 존재하는 고객 ID만 반환합니다.

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


---


### 문제 9. 위시리스트에 담았지만 한 번도 주문하지 않은 상품(차집합)을 찾으세요.

EXCEPT는 첫 번째 SELECT에서 두 번째 SELECT의 결과를 뺀 차집합을 반환합니다.

??? tip "힌트"
    `SELECT product_id FROM wishlists EXCEPT SELECT product_id FROM order_items` — 위시리스트에만 있고 주문에는 없는 상품 ID입니다.

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


### 문제 10. 2024년에는 주문했지만 2025년에는 주문하지 않은 고객을 찾으세요.

EXCEPT로 연도별 고객 집합의 차집합을 구합니다. 이탈 고객 분석에 활용됩니다.

??? tip "힌트"
    `SELECT customer_id FROM orders WHERE ordered_at LIKE '2024%' EXCEPT SELECT customer_id FROM orders WHERE ordered_at LIKE '2025%'` — 2024년 고객에서 2025년 고객을 뺍니다.

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


---


## 실전 (11-15): 서브쿼리 결합, 집합 연산 + 집계

### 문제 11. 고객 활동 유형별 건수를 하나의 보고서로 합치세요 (주문, 리뷰, 불만, 위시리스트).

UNION ALL로 여러 활동 유형의 건수를 합쳐 하나의 요약 테이블을 만듭니다.

??? tip "힌트"
    `SELECT '주문' AS activity, COUNT(*) FROM orders UNION ALL SELECT '리뷰', COUNT(*) FROM reviews UNION ALL ...` — 각 SELECT의 컬럼 이름과 타입을 맞춰야 합니다.

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

    | activity_type | total_count |
    |--------------|-------------|
    | 주문 | ... |
    | 위시리스트 | ... |
    | 리뷰 | ... |
    | 불만 접수 | ... |


---


### 문제 12. 2024년과 2025년 모두 주문한 충성 고객의 이름, 등급, 두 해의 주문 건수를 구하세요.

INTERSECT로 충성 고객을 찾은 뒤, 각 연도 주문 건수를 스칼라 서브쿼리로 구합니다.

??? tip "힌트"
    먼저 INTERSECT로 두 해 모두 주문한 고객 ID를 구하고, 그 고객에 대해 연도별 주문 건수를 SELECT 절 스칼라 서브쿼리로 추가합니다.

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


---


### 문제 13. 불만이 접수되었지만 반품은 하지 않은 주문의 주문번호와 금액을 구하세요.

EXCEPT로 불만 주문 집합에서 반품 주문 집합을 뺍니다.

??? tip "힌트"
    `SELECT order_id FROM complaints WHERE order_id IS NOT NULL EXCEPT SELECT order_id FROM returns` — 불만은 있지만 반품까지 이어지지 않은 주문입니다.

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


---


### 문제 14. 상품별 "리뷰 건수 + 위시리스트 등록 수"를 UNION ALL 서브쿼리로 합산하세요. 상위 10개.

UNION ALL로 두 테이블의 상품 관심도를 합치고, 외부에서 집계합니다.

??? tip "힌트"
    `FROM (SELECT product_id FROM reviews UNION ALL SELECT product_id FROM wishlists) AS combined` — 합친 뒤 `GROUP BY product_id`로 건수를 세면 리뷰+위시리스트 통합 관심도가 됩니다.

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

    | name | interest_score |
    |------|----------------|
    | (인기 상품 1) | 42 |
    | ... | ... |


---


### 문제 15. 2024년 분기별 신규 고객 수와 주문 고객 수를 각각 구한 뒤 하나의 보고서로 합치세요.

서로 다른 기준의 분기별 집계를 UNION ALL로 합쳐 비교 보고서를 만듭니다.

??? tip "힌트"
    `SELECT quarter, '신규가입' AS metric, COUNT(*) ... UNION ALL SELECT quarter, '주문' AS metric, COUNT(DISTINCT customer_id) ...` — metric 컬럼으로 지표를 구분합니다.

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

    | quarter | metric | value |
    |---------|--------|-------|
    | Q1 | 신규가입 | ... |
    | Q1 | 주문고객 | ... |
    | Q2 | 신규가입 | ... |
    | Q2 | 주문고객 | ... |
    | ... | ... | ... |


---
