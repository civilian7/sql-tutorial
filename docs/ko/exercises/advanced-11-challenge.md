# 도전 문제

solvesql/LeetCode 스타일의 고난도 문제들입니다.

---


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


---


### 17. 롤링 리텐션 분석


가입 월(cohort) 기준으로, N개월 이후에 "아무 때나" 주문한 고객 비율을 계산하세요.
클래식 리텐션과 달리 정확한 월이 아닌 N개월 이후 어떤 시점이든 포함합니다.


**힌트 1:** - `months_since_signup >= N` 조건으로 "N개월 이후"를 판별
- 클래식과 비교하면 항상 같거나 큰 값



??? success "정답"
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


---


### 23. 구매 주기 분석


고객별 연속 주문 간 평균 일수(구매 주기)를 계산하세요.
LAG로 이전 주문일을 가져와 JULIANDAY 차이를 구합니다.


**힌트 1:** - `LAG(ordered_at) OVER (PARTITION BY customer_id ORDER BY ordered_at)`
- `JULIANDAY(ordered_at) - JULIANDAY(prev_ordered_at)`
- `AVG()`로 고객별 평균 주기



??? success "정답"
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


---


### 24. 첫 구매 후 재구매율


첫 주문 후 30일/60일/90일 이내에 재구매한 고객 비율을 구하세요.


**힌트 1:** - 고객별 첫 주문일 = `MIN(ordered_at)`
- 두 번째 주문이 첫 주문 + N일 이내인지 확인



??? success "정답"
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


---


### 26. 프로모션 리프트 분석


프로모션 기간 중 일평균 매출과 프로모션 외 기간의 일평균 매출을 비교하세요.
프로모션별 리프트(%)를 계산합니다.


**힌트 1:** - `promotions.started_at` ~ `ended_at` 기간의 전체 매출 / 기간 일수
- 비프로모션 기간의 전체 매출 / 기간 일수



??? success "정답"
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


---


### 29. 택배사별 월별 배송 성과 및 추이


택배사별 월별 평균 배송 소요일과 전월 대비 변화를 보여주세요.


**힌트 1:** - `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)` 로 배송일
- `LAG(avg_days) OVER (PARTITION BY carrier ORDER BY month)` 로 전월 비교



??? success "정답"
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


---


### 30. 3일 연속 매출 증가 구간


일별 매출이 3일 연속 증가한 구간을 찾으세요.
시작일, 종료일, 연속 일수를 표시합니다.


**힌트 1:** - LAG로 전일 매출 비교하여 증가 여부 플래그
- 증가 플래그가 끊기는 지점을 그룹 경계로 사용 (island 패턴)
- 그룹별 연속 일수 >= 3 필터



??? success "정답"
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


---


### 31. 연속 월 주문 고객


5개월 이상 연속으로 매월 주문한 고객을 찾으세요.
고객명, 연속 시작월, 연속 종료월, 연속 개월 수를 표시합니다.


**힌트 1:** - 고객별 월별 주문 여부를 먼저 구함
- 연속 월을 감지하려면 "month_number - ROW_NUMBER" 패턴 사용
- 같은 차이값을 가진 행들이 연속 구간



??? success "정답"
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


---


### 32. 세션 정의 (30분 갭)


product_views를 세션으로 그룹화하세요 (같은 고객의 조회 간 30분 이상 간격이면 새 세션).
고객별 세션 수, 세션당 평균 조회 수를 구하세요.


**힌트 1:** - `LAG(viewed_at)`로 이전 조회 시간
- 30분 = `(JULIANDAY(현재) - JULIANDAY(이전)) * 24 * 60 > 30`
- `SUM(is_new_session) OVER (...)`로 세션 번호 부여



??? success "정답"
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


---


### 33. 세션 재정의 (10분 갭)


c11-32와 동일하되 세션 갭을 10분으로 변경하세요.
30분 갭 결과와 비교하여 세션 수가 어떻게 달라지는지 확인합니다.


**힌트 1:** - 30분을 10분으로 변경하기만 하면 됨
- 세션이 더 많이 분할될 것



??? success "정답"
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


---


### 35. 택배사별 배송일 중앙값


택배사별 배송 소요일의 중앙값을 계산하세요.


**힌트 1:** - `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)`로 배송일 계산
- `ROW_NUMBER()`로 순위를 매긴 후 중앙 위치의 값 추출



??? success "정답"
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


---


### 38. 활성일 아일랜드 탐지


고객별 product_views에서 연속 활성일(island)을 찾으세요.
예: 고객이 월/화/수 조회 -> 목 미조회 -> 금/토 조회이면 2개 아일랜드(3일, 2일).


**힌트 1:** - 고객별 조회 날짜를 `DISTINCT`로 추출
- `DATE - ROW_NUMBER` 패턴으로 연속 날짜 그룹화
- 그룹별 MIN/MAX/COUNT



??? success "정답"
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


---
