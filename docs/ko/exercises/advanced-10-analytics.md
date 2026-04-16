# 고급 분석

<div class="grid" markdown>

<div markdown>
#### :material-database: 사용 테이블

`point_transactions` — 포인트 (적립, 사용, 소멸)<br>

`customer_grade_history` — 등급 이력 (변경 전후)<br>

`product_views` — 조회 로그 (고객, 상품, 일시)<br>

`orders` — 주문 (상태, 금액, 일시)<br>

`order_items` — 주문 상세 (수량, 단가)<br>

`carts` — 장바구니 (상태)<br>

`cart_items` — 장바구니 상품 (수량)<br>

`promotions` — 프로모션 (기간, 할인)<br>

`promotion_products` — 프로모션 대상 상품<br>

`staff` — 직원 (부서, 역할, 관리자)<br>

`product_qna` — 상품 Q&A (질문-답변)<br>

`products` — 상품 (이름, 가격, 재고, 브랜드)<br>

`customers` — 고객 (등급, 포인트, 가입채널)<br>

</div>

<div markdown>
#### :material-book-open-variant: 학습 범위

`Window Functions`

`CTE`

`Funnel`

`Session`

`Cohort`

`Recursive CTE`

`RFM`

</div>

</div>

---


### 1. 포인트 누적 잔액 검증 (Running Total)


point_transactions의 balance_after가 올바른지 SUM() OVER()로 검증하세요.
특정 고객(예: id=100)의 포인트 거래 내역을 시간순으로 나열하고,
누적 합계(calculated_balance)와 balance_after를 비교합니다.


**힌트 1:** - `SUM(amount) OVER (PARTITION BY customer_id ORDER BY created_at, id)` 사용
- `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`
- `balance_after`와 비교하여 차이가 있는 행 확인



??? success "정답"
    ```sql
    SELECT
        id,
        type,
        reason,
        amount,
        balance_after,
        SUM(amount) OVER (
            ORDER BY created_at, id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS calculated_balance,
        balance_after - SUM(amount) OVER (
            ORDER BY created_at, id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS diff,
        created_at
    FROM point_transactions
    WHERE customer_id = 100
    ORDER BY created_at, id;
    ```


---


### 2. 등급 변경 이력 추적 (LAG)


customer_grade_history에서 LAG()를 사용하여 각 변경 이전의 등급을 가져오세요.
old_grade와 LAG 결과가 일치하는지도 확인합니다.


**힌트 1:** - `LAG(new_grade) OVER (PARTITION BY customer_id ORDER BY changed_at)`
- 이전 레코드의 new_grade가 현재 레코드의 old_grade와 일치해야 함



??? success "정답"
    ```sql
    WITH grade_changes AS (
        SELECT
            customer_id,
            old_grade,
            new_grade,
            reason,
            changed_at,
            LAG(new_grade) OVER (
                PARTITION BY customer_id
                ORDER BY changed_at
            ) AS prev_new_grade
        FROM customer_grade_history
    )
    SELECT
        gc.customer_id,
        c.name,
        gc.old_grade,
        gc.new_grade,
        gc.prev_new_grade,
        CASE
            WHEN gc.old_grade = gc.prev_new_grade THEN 'OK'
            WHEN gc.prev_new_grade IS NULL THEN 'FIRST'
            ELSE 'MISMATCH'
        END AS check_status,
        gc.reason,
        gc.changed_at
    FROM grade_changes AS gc
    INNER JOIN customers AS c ON gc.customer_id = c.id
    WHERE gc.prev_new_grade IS NOT NULL
    ORDER BY gc.customer_id, gc.changed_at
    LIMIT 30;
    ```


---


### 3. 퍼널 분석: 조회 -> 장바구니 -> 구매


product_views, cart_items, order_items를 활용하여
상품 조회 -> 장바구니 담기 -> 실제 구매의 전환율을 계산하세요.


**힌트 1:** - 각 단계의 고유 고객-상품 조합 수를 계산
- 퍼널은 반드시 같은 고객이 같은 상품을 봐야 함
- 스칼라 서브쿼리 또는 CTE 사용



??? success "정답"
    ```sql
    WITH funnel AS (
        SELECT
            (SELECT COUNT(DISTINCT customer_id || '-' || product_id)
             FROM product_views) AS step1_views,
            (SELECT COUNT(DISTINCT c.customer_id || '-' || ci.product_id)
             FROM cart_items ci
             INNER JOIN carts c ON ci.cart_id = c.id) AS step2_cart,
            (SELECT COUNT(DISTINCT o.customer_id || '-' || oi.product_id)
             FROM order_items oi
             INNER JOIN orders o ON oi.order_id = o.id
             WHERE o.status NOT IN ('cancelled')) AS step3_purchase
    )
    SELECT
        step1_views,
        step2_cart,
        ROUND(100.0 * step2_cart / step1_views, 2) AS view_to_cart_pct,
        step3_purchase,
        ROUND(100.0 * step3_purchase / step2_cart, 2) AS cart_to_purchase_pct,
        ROUND(100.0 * step3_purchase / step1_views, 2) AS view_to_purchase_pct
    FROM funnel;
    ```


---


### 4. 세션 분석: 상품 조회 세션화


product_views를 세션 단위로 그룹화하세요.
같은 고객의 조회 간 30분 이상 간격이 있으면 새 세션으로 판별합니다.
고객별 평균 세션 수와 세션당 평균 조회 수를 구하세요.


**힌트 1:** - `LAG(viewed_at) OVER (PARTITION BY customer_id ORDER BY viewed_at)`
- 이전 조회와의 시간 차이 > 30분이면 새 세션
- `SUM(new_session_flag) OVER (...)` 로 세션 번호 부여



??? success "정답"

    === "SQLite"
        ```sql
        WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
            LAG(viewed_at) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS prev_viewed_at,
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
        WHERE customer_id <= 1000
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

    === "MySQL"
        ```sql
        WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
            LAG(viewed_at) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS prev_viewed_at,
            CASE
                WHEN LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) IS NULL THEN 1
                WHEN TIMESTAMPDIFF(MINUTE, LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ), viewed_at) > 30 THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
        WHERE customer_id <= 1000
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

    === "PostgreSQL"
        ```sql
        WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
            LAG(viewed_at) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS prev_viewed_at,
            CASE
                WHEN LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                ) IS NULL THEN 1
                WHEN EXTRACT(EPOCH FROM (viewed_at::timestamp - LAG(viewed_at) OVER (
                    PARTITION BY customer_id ORDER BY viewed_at
                )::timestamp)) / 60 > 30 THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
        WHERE customer_id <= 1000
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
            LAG(viewed_at) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS prev_viewed_at,
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
        WHERE customer_id <= 1000
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
            LAG(viewed_at) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS prev_viewed_at,
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
        WHERE customer_id <= 1000
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


### 5. 코호트 리텐션: 가입 채널 x 가입월


가입 채널(acquisition_channel)과 가입 월 기준으로
30일/60일/90일 리텐션율을 계산하세요.


**힌트 1:** - 코호트 = 가입 채널 + 가입 월
- 30일 리텐션: 가입 후 30일 이내 주문한 고객 비율
- `DATE(created_at, '+30 days')` 활용



??? success "정답"

    === "SQLite"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            COALESCE(acquisition_channel, 'unknown') AS channel,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at LIKE '2024%'
    ),
    cohort_activity AS (
        SELECT
            co.channel,
            co.signup_month,
            COUNT(DISTINCT co.customer_id) AS cohort_size,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at <= DATE(co.created_at, '+30 days')
                THEN co.customer_id
            END) AS active_30d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATE(co.created_at, '+30 days')
                 AND o.ordered_at <= DATE(co.created_at, '+60 days')
                THEN co.customer_id
            END) AS active_60d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATE(co.created_at, '+60 days')
                 AND o.ordered_at <= DATE(co.created_at, '+90 days')
                THEN co.customer_id
            END) AS active_90d
        FROM cohort AS co
        LEFT JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY co.channel, co.signup_month
    )
    SELECT
        channel,
        signup_month,
        cohort_size,
        active_30d,
        ROUND(100.0 * active_30d / cohort_size, 1) AS retention_30d_pct,
        active_60d,
        ROUND(100.0 * active_60d / cohort_size, 1) AS retention_60d_pct,
        active_90d,
        ROUND(100.0 * active_90d / cohort_size, 1) AS retention_90d_pct
    FROM cohort_activity
    WHERE cohort_size >= 10
    ORDER BY channel, signup_month;
        ```

    === "MySQL"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            COALESCE(acquisition_channel, 'unknown') AS channel,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at LIKE '2024%'
    ),
    cohort_activity AS (
        SELECT
            co.channel,
            co.signup_month,
            COUNT(DISTINCT co.customer_id) AS cohort_size,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at <= DATE_ADD(co.created_at, INTERVAL 30 DAY)
                THEN co.customer_id
            END) AS active_30d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATE_ADD(co.created_at, INTERVAL 30 DAY)
                 AND o.ordered_at <= DATE_ADD(co.created_at, INTERVAL 60 DAY)
                THEN co.customer_id
            END) AS active_60d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATE_ADD(co.created_at, INTERVAL 60 DAY)
                 AND o.ordered_at <= DATE_ADD(co.created_at, INTERVAL 90 DAY)
                THEN co.customer_id
            END) AS active_90d
        FROM cohort AS co
        LEFT JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY co.channel, co.signup_month
    )
    SELECT
        channel,
        signup_month,
        cohort_size,
        active_30d,
        ROUND(100.0 * active_30d / cohort_size, 1) AS retention_30d_pct,
        active_60d,
        ROUND(100.0 * active_60d / cohort_size, 1) AS retention_60d_pct,
        active_90d,
        ROUND(100.0 * active_90d / cohort_size, 1) AS retention_90d_pct
    FROM cohort_activity
    WHERE cohort_size >= 10
    ORDER BY channel, signup_month;
        ```

    === "PostgreSQL"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            COALESCE(acquisition_channel, 'unknown') AS channel,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at LIKE '2024%'
    ),
    cohort_activity AS (
        SELECT
            co.channel,
            co.signup_month,
            COUNT(DISTINCT co.customer_id) AS cohort_size,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at <= (co.created_at::date + INTERVAL '30 days')
                THEN co.customer_id
            END) AS active_30d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > (co.created_at::date + INTERVAL '30 days')
                 AND o.ordered_at <= (co.created_at::date + INTERVAL '60 days')
                THEN co.customer_id
            END) AS active_60d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > (co.created_at::date + INTERVAL '60 days')
                 AND o.ordered_at <= (co.created_at::date + INTERVAL '90 days')
                THEN co.customer_id
            END) AS active_90d
        FROM cohort AS co
        LEFT JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY co.channel, co.signup_month
    )
    SELECT
        channel,
        signup_month,
        cohort_size,
        active_30d,
        ROUND(100.0 * active_30d / cohort_size, 1) AS retention_30d_pct,
        active_60d,
        ROUND(100.0 * active_60d / cohort_size, 1) AS retention_60d_pct,
        active_90d,
        ROUND(100.0 * active_90d / cohort_size, 1) AS retention_90d_pct
    FROM cohort_activity
    WHERE cohort_size >= 10
    ORDER BY channel, signup_month;
        ```

    === "Oracle"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            COALESCE(acquisition_channel, 'unknown') AS channel,
            SUBSTR(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at LIKE '2024%'
    ),
    cohort_activity AS (
        SELECT
            co.channel,
            co.signup_month,
            COUNT(DISTINCT co.customer_id) AS cohort_size,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at <= CAST(co.created_at AS DATE) + 30
                THEN co.customer_id
            END) AS active_30d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > CAST(co.created_at AS DATE) + 30
                 AND o.ordered_at <= CAST(co.created_at AS DATE) + 60
                THEN co.customer_id
            END) AS active_60d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > CAST(co.created_at AS DATE) + 60
                 AND o.ordered_at <= CAST(co.created_at AS DATE) + 90
                THEN co.customer_id
            END) AS active_90d
        FROM cohort co
        LEFT JOIN orders o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY co.channel, co.signup_month
    )
    SELECT
        channel,
        signup_month,
        cohort_size,
        active_30d,
        ROUND(100.0 * active_30d / cohort_size, 1) AS retention_30d_pct,
        active_60d,
        ROUND(100.0 * active_60d / cohort_size, 1) AS retention_60d_pct,
        active_90d,
        ROUND(100.0 * active_90d / cohort_size, 1) AS retention_90d_pct
    FROM cohort_activity
    WHERE cohort_size >= 10
    ORDER BY channel, signup_month;
        ```

    === "SQL Server"
        ```sql
        WITH cohort AS (
        SELECT
            id AS customer_id,
            COALESCE(acquisition_channel, 'unknown') AS channel,
            SUBSTRING(created_at, 1, 7) AS signup_month,
            created_at
        FROM customers
        WHERE created_at LIKE '2024%'
    ),
    cohort_activity AS (
        SELECT
            co.channel,
            co.signup_month,
            COUNT(DISTINCT co.customer_id) AS cohort_size,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at <= DATEADD(DAY, 30, CAST(co.created_at AS DATE))
                THEN co.customer_id
            END) AS active_30d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATEADD(DAY, 30, CAST(co.created_at AS DATE))
                 AND o.ordered_at <= DATEADD(DAY, 60, CAST(co.created_at AS DATE))
                THEN co.customer_id
            END) AS active_60d,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at > DATEADD(DAY, 60, CAST(co.created_at AS DATE))
                 AND o.ordered_at <= DATEADD(DAY, 90, CAST(co.created_at AS DATE))
                THEN co.customer_id
            END) AS active_90d
        FROM cohort AS co
        LEFT JOIN orders AS o
            ON co.customer_id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY co.channel, co.signup_month
    )
    SELECT
        channel,
        signup_month,
        cohort_size,
        active_30d,
        ROUND(100.0 * active_30d / cohort_size, 1) AS retention_30d_pct,
        active_60d,
        ROUND(100.0 * active_60d / cohort_size, 1) AS retention_60d_pct,
        active_90d,
        ROUND(100.0 * active_90d / cohort_size, 1) AS retention_90d_pct
    FROM cohort_activity
    WHERE cohort_size >= 10
    ORDER BY channel, signup_month;
        ```


---


### 6. 프로모션 효과 분석


프로모션 기간 중 대상 상품의 주문 금액과
프로모션 기간 외 주문 금액을 비교하세요.
프로모션별 매출 증감률을 계산합니다.


**힌트 1:** - `promotion_products`에서 대상 상품 목록 확보
- 프로모션 기간: `promotions.started_at` ~ `ended_at`
- 기간 중/외 매출을 CASE로 분리



??? success "정답"

    === "SQLite"
        ```sql
        WITH promo_products AS (
        SELECT
            promo.id AS promo_id,
            promo.name AS promo_name,
            promo.started_at,
            promo.ended_at,
            pp.product_id
        FROM promotions AS promo
        INNER JOIN promotion_products AS pp ON promo.id = pp.promotion_id
        WHERE promo.started_at >= '2024-01-01'
    ),
    promo_revenue AS (
        SELECT
            ppr.promo_id,
            ppr.promo_name,
            ppr.started_at,
            ppr.ended_at,
            SUM(CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS during_revenue,
            SUM(CASE
                WHEN o.ordered_at < ppr.started_at
                 AND o.ordered_at >= DATE(ppr.started_at, '-' || CAST(JULIANDAY(ppr.ended_at) - JULIANDAY(ppr.started_at) AS INTEGER) || ' days')
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS before_revenue,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN o.id
            END) AS during_orders
        FROM promo_products AS ppr
        INNER JOIN order_items AS oi ON ppr.product_id = oi.product_id
        INNER JOIN orders      AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY ppr.promo_id, ppr.promo_name, ppr.started_at, ppr.ended_at
    )
    SELECT
        promo_name,
        started_at,
        ended_at,
        during_orders,
        ROUND(during_revenue, 0) AS during_revenue,
        ROUND(before_revenue, 0) AS before_revenue,
        CASE
            WHEN before_revenue > 0
            THEN ROUND(100.0 * (during_revenue - before_revenue) / before_revenue, 1)
            ELSE NULL
        END AS revenue_change_pct
    FROM promo_revenue
    WHERE during_revenue > 0
    ORDER BY revenue_change_pct DESC
    LIMIT 20;
        ```

    === "MySQL"
        ```sql
        WITH promo_products AS (
        SELECT
            promo.id AS promo_id,
            promo.name AS promo_name,
            promo.started_at,
            promo.ended_at,
            pp.product_id
        FROM promotions AS promo
        INNER JOIN promotion_products AS pp ON promo.id = pp.promotion_id
        WHERE promo.started_at >= '2024-01-01'
    ),
    promo_revenue AS (
        SELECT
            ppr.promo_id,
            ppr.promo_name,
            ppr.started_at,
            ppr.ended_at,
            SUM(CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS during_revenue,
            SUM(CASE
                WHEN o.ordered_at < ppr.started_at
                 AND o.ordered_at >= DATE_SUB(ppr.started_at, INTERVAL DATEDIFF(ppr.ended_at, ppr.started_at) DAY)
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS before_revenue,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN o.id
            END) AS during_orders
        FROM promo_products AS ppr
        INNER JOIN order_items AS oi ON ppr.product_id = oi.product_id
        INNER JOIN orders      AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY ppr.promo_id, ppr.promo_name, ppr.started_at, ppr.ended_at
    )
    SELECT
        promo_name,
        started_at,
        ended_at,
        during_orders,
        ROUND(during_revenue, 0) AS during_revenue,
        ROUND(before_revenue, 0) AS before_revenue,
        CASE
            WHEN before_revenue > 0
            THEN ROUND(100.0 * (during_revenue - before_revenue) / before_revenue, 1)
            ELSE NULL
        END AS revenue_change_pct
    FROM promo_revenue
    WHERE during_revenue > 0
    ORDER BY revenue_change_pct DESC
    LIMIT 20;
        ```

    === "PostgreSQL"
        ```sql
        WITH promo_products AS (
        SELECT
            promo.id AS promo_id,
            promo.name AS promo_name,
            promo.started_at,
            promo.ended_at,
            pp.product_id
        FROM promotions AS promo
        INNER JOIN promotion_products AS pp ON promo.id = pp.promotion_id
        WHERE promo.started_at >= '2024-01-01'
    ),
    promo_revenue AS (
        SELECT
            ppr.promo_id,
            ppr.promo_name,
            ppr.started_at,
            ppr.ended_at,
            SUM(CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS during_revenue,
            SUM(CASE
                WHEN o.ordered_at < ppr.started_at
                 AND o.ordered_at >= (ppr.started_at::date - (ppr.ended_at::date - ppr.started_at::date))
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS before_revenue,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN o.id
            END) AS during_orders
        FROM promo_products AS ppr
        INNER JOIN order_items AS oi ON ppr.product_id = oi.product_id
        INNER JOIN orders      AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY ppr.promo_id, ppr.promo_name, ppr.started_at, ppr.ended_at
    )
    SELECT
        promo_name,
        started_at,
        ended_at,
        during_orders,
        ROUND(during_revenue, 0) AS during_revenue,
        ROUND(before_revenue, 0) AS before_revenue,
        CASE
            WHEN before_revenue > 0
            THEN ROUND(100.0 * (during_revenue - before_revenue) / before_revenue, 1)
            ELSE NULL
        END AS revenue_change_pct
    FROM promo_revenue
    WHERE during_revenue > 0
    ORDER BY revenue_change_pct DESC
    LIMIT 20;
        ```

    === "Oracle"
        ```sql
        WITH promo_products AS (
        SELECT
            promo.id AS promo_id,
            promo.name AS promo_name,
            promo.started_at,
            promo.ended_at,
            pp.product_id
        FROM promotions promo
        INNER JOIN promotion_products pp ON promo.id = pp.promotion_id
        WHERE promo.started_at >= '2024-01-01'
    ),
    promo_revenue AS (
        SELECT
            ppr.promo_id,
            ppr.promo_name,
            ppr.started_at,
            ppr.ended_at,
            SUM(CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS during_revenue,
            SUM(CASE
                WHEN o.ordered_at < ppr.started_at
                 AND o.ordered_at >= (CAST(ppr.started_at AS DATE) - (CAST(ppr.ended_at AS DATE) - CAST(ppr.started_at AS DATE)))
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS before_revenue,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN o.id
            END) AS during_orders
        FROM promo_products ppr
        INNER JOIN order_items oi ON ppr.product_id = oi.product_id
        INNER JOIN orders      o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY ppr.promo_id, ppr.promo_name, ppr.started_at, ppr.ended_at
    )
    SELECT
        promo_name,
        started_at,
        ended_at,
        during_orders,
        ROUND(during_revenue, 0) AS during_revenue,
        ROUND(before_revenue, 0) AS before_revenue,
        CASE
            WHEN before_revenue > 0
            THEN ROUND(100.0 * (during_revenue - before_revenue) / before_revenue, 1)
            ELSE NULL
        END AS revenue_change_pct
    FROM promo_revenue
    WHERE during_revenue > 0
    ORDER BY revenue_change_pct DESC
    FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        WITH promo_products AS (
        SELECT
            promo.id AS promo_id,
            promo.name AS promo_name,
            promo.started_at,
            promo.ended_at,
            pp.product_id
        FROM promotions AS promo
        INNER JOIN promotion_products AS pp ON promo.id = pp.promotion_id
        WHERE promo.started_at >= '2024-01-01'
    ),
    promo_revenue AS (
        SELECT
            ppr.promo_id,
            ppr.promo_name,
            ppr.started_at,
            ppr.ended_at,
            SUM(CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS during_revenue,
            SUM(CASE
                WHEN o.ordered_at < ppr.started_at
                 AND o.ordered_at >= DATEADD(DAY, -DATEDIFF(DAY, ppr.started_at, ppr.ended_at), ppr.started_at)
                THEN oi.quantity * oi.unit_price ELSE 0
            END) AS before_revenue,
            COUNT(DISTINCT CASE
                WHEN o.ordered_at BETWEEN ppr.started_at AND ppr.ended_at
                THEN o.id
            END) AS during_orders
        FROM promo_products AS ppr
        INNER JOIN order_items AS oi ON ppr.product_id = oi.product_id
        INNER JOIN orders      AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY ppr.promo_id, ppr.promo_name, ppr.started_at, ppr.ended_at
    )
    SELECT TOP 20
        promo_name,
        started_at,
        ended_at,
        during_orders,
        ROUND(during_revenue, 0) AS during_revenue,
        ROUND(before_revenue, 0) AS before_revenue,
        CASE
            WHEN before_revenue > 0
            THEN ROUND(100.0 * (during_revenue - before_revenue) / before_revenue, 1)
            ELSE NULL
        END AS revenue_change_pct
    FROM promo_revenue
    WHERE during_revenue > 0
    ORDER BY revenue_change_pct DESC;
        ```


---


### 7. 재귀 조직도: 직원 계층과 레벨


재귀 CTE를 사용하여 전체 직원 조직도를 생성하세요.
각 직원의 계층 레벨, 전체 경로(CEO > 부장 > 과장 > ...)를 표시합니다.


**힌트 1:** - 시작점: `manager_id IS NULL` (최상위 관리자)
- 재귀: `staff.manager_id = tree.id`
- 경로: `tree.path || ' > ' || staff.name`



??? success "정답"
    ```sql
    WITH RECURSIVE org AS (
        SELECT
            id,
            name,
            department,
            role,
            manager_id,
            name AS path,
            0 AS level
        FROM staff
        WHERE manager_id IS NULL
        UNION ALL
        SELECT
            s.id,
            s.name,
            s.department,
            s.role,
            s.manager_id,
            org.path || ' > ' || s.name,
            org.level + 1
        FROM staff AS s
        INNER JOIN org ON s.manager_id = org.id
    )
    SELECT
        level,
        name,
        department,
        role,
        path
    FROM org
    ORDER BY path;
    ```


---


### 8. 재귀 Q&A 트리: 질문 -> 답변 -> 후속


재귀 CTE를 사용하여 Q&A 스레드의 전체 대화 체인을 구성하세요.
질문 -> 답변 -> 추가 질문 -> 추가 답변 순으로 표시합니다.


**힌트 1:** - 시작점: `parent_id IS NULL` (최초 질문)
- 재귀: `product_qna.parent_id = tree.id`
- 들여쓰기나 레벨로 계층 표현



??? success "정답"
    ```sql
    WITH RECURSIVE qna_tree AS (
        SELECT
            q.id,
            q.product_id,
            q.parent_id,
            q.content,
            q.customer_id,
            q.staff_id,
            q.created_at,
            0 AS depth,
            CAST(q.id AS TEXT) AS thread_path
        FROM product_qna AS q
        WHERE q.parent_id IS NULL
          AND q.product_id <= 100
        UNION ALL
        SELECT
            child.id,
            child.product_id,
            child.parent_id,
            child.content,
            child.customer_id,
            child.staff_id,
            child.created_at,
            tree.depth + 1,
            tree.thread_path || '.' || CAST(child.id AS TEXT)
        FROM product_qna AS child
        INNER JOIN qna_tree AS tree ON child.parent_id = tree.id
    )
    SELECT
        qt.product_id,
        p.name AS product_name,
        qt.depth,
        CASE
            WHEN qt.customer_id IS NOT NULL THEN '[Q] ' || COALESCE(c.name, '?')
            WHEN qt.staff_id IS NOT NULL    THEN '[A] ' || COALESCE(s.name, '?')
            ELSE '[?]'
        END AS author,
        SUBSTR(qt.content, 1, 80) AS content_preview,
        qt.created_at
    FROM qna_tree AS qt
    INNER JOIN products AS p ON qt.product_id = p.id
    LEFT JOIN customers AS c ON qt.customer_id = c.id
    LEFT JOIN staff     AS s ON qt.staff_id = s.id
    ORDER BY qt.product_id, qt.thread_path
    LIMIT 50;
    ```


---


### 9. 상품 후속 모델 체인 (Recursive CTE)


재귀 CTE를 사용하여 단종 상품의 전체 후속 모델 체인을 추적하세요.
예: A -> B -> C (A가 단종되어 B로 대체, B도 단종되어 C로 대체)


**힌트 1:** - 시작점: `discontinued_at IS NOT NULL AND successor_id IS NOT NULL`
- 재귀: `products.id = tree.successor_id`
- 체인 길이(depth)도 계산



??? success "정답"
    ```sql
    WITH RECURSIVE successor_chain AS (
        SELECT
            id AS origin_id,
            name AS origin_name,
            id AS current_id,
            name AS current_name,
            price AS current_price,
            successor_id,
            discontinued_at,
            0 AS depth
        FROM products
        WHERE discontinued_at IS NOT NULL
          AND successor_id IS NOT NULL
        UNION ALL
        SELECT
            sc.origin_id,
            sc.origin_name,
            p.id,
            p.name,
            p.price,
            p.successor_id,
            p.discontinued_at,
            sc.depth + 1
        FROM products AS p
        INNER JOIN successor_chain AS sc ON p.id = sc.successor_id
        WHERE sc.depth < 10
    )
    SELECT
        origin_name AS discontinued_product,
        current_name AS final_successor,
        depth AS chain_length,
        current_price AS successor_price,
        CASE
            WHEN successor_id IS NULL THEN 'Current Model'
            WHEN discontinued_at IS NOT NULL THEN 'Also Discontinued'
            ELSE 'Active'
        END AS status
    FROM successor_chain
    WHERE successor_id IS NULL
       OR discontinued_at IS NULL
    ORDER BY chain_length DESC, origin_name
    LIMIT 30;
    ```


---


### 10. RFM + 등급 이력 트렌드 분석


RFM 분석과 등급 변경 이력을 결합하여
등급이 하락한 고객의 RFM 점수 분포를 분석하세요.
등급 하락 고객 vs 유지/상승 고객의 RFM 차이를 비교합니다.


**힌트 1:** - 등급 변경 이력에서 하락(downgrade) 고객 식별
- RFM 점수를 별도 CTE로 계산
- 두 결과를 JOIN하여 그룹별 비교



??? success "정답"
    ```sql
    WITH recent_grade_change AS (
        SELECT
            customer_id,
            reason AS last_change_reason,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY changed_at DESC
            ) AS rn
        FROM customer_grade_history
        WHERE changed_at >= '2024-01-01'
    ),
    customer_trend AS (
        SELECT
            customer_id,
            last_change_reason,
            CASE
                WHEN last_change_reason = 'downgrade' THEN 'Downgraded'
                WHEN last_change_reason = 'upgrade'   THEN 'Upgraded'
                ELSE 'Maintained'
            END AS trend
        FROM recent_grade_change
        WHERE rn = 1
    ),
    rfm AS (
        SELECT
            c.id AS customer_id,
            c.grade,
            MAX(o.ordered_at) AS last_order,
            COUNT(*) AS frequency,
            ROUND(SUM(o.total_amount), 0) AS monetary,
            NTILE(4) OVER (ORDER BY MAX(o.ordered_at) ASC)  AS r_score,
            NTILE(4) OVER (ORDER BY COUNT(*) ASC)            AS f_score,
            NTILE(4) OVER (ORDER BY SUM(o.total_amount) ASC) AS m_score
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.grade
    )
    SELECT
        ct.trend,
        COUNT(*) AS customer_count,
        ROUND(AVG(r.r_score), 2) AS avg_recency,
        ROUND(AVG(r.f_score), 2) AS avg_frequency,
        ROUND(AVG(r.m_score), 2) AS avg_monetary,
        ROUND(AVG(r.r_score + r.f_score + r.m_score), 2) AS avg_rfm_total,
        ROUND(AVG(r.monetary), 0) AS avg_total_spent,
        ROUND(AVG(r.frequency), 1) AS avg_order_count
    FROM customer_trend AS ct
    INNER JOIN rfm AS r ON ct.customer_id = r.customer_id
    GROUP BY ct.trend
    ORDER BY
        CASE ct.trend
            WHEN 'Downgraded' THEN 1
            WHEN 'Maintained' THEN 2
            WHEN 'Upgraded' THEN 3
        END;
    ```


---


### 11. 등급 승격 이력 조회


VIP로 승격된 고객의 이력을 조회하세요.
고객명, 이전 등급, 변경일, 변경 사유를 표시합니다.


**힌트 1:** - `customer_grade_history.new_grade = 'VIP'` 필터
- `customer_grade_history.reason = 'upgrade'` 필터
- `customers` JOIN으로 고객 정보 포함



??? success "정답"
    ```sql
    SELECT
        c.name          AS customer_name,
        c.email,
        cgh.old_grade,
        cgh.new_grade,
        cgh.changed_at,
        cgh.reason
    FROM customer_grade_history AS cgh
    INNER JOIN customers AS c ON cgh.customer_id = c.id
    WHERE cgh.new_grade = 'VIP'
      AND cgh.reason = 'upgrade'
    ORDER BY cgh.changed_at DESC
    LIMIT 20;
    ```


---


### 12. 포인트 잔액 검증


point_transactions의 누적 합계와 customers.point_balance를 비교하여
불일치하는 고객을 찾으세요.


**힌트 1:** - `SUM(amount)`으로 포인트 거래 합계 계산
- `customers.point_balance`와 비교
- `HAVING`으로 불일치 필터



??? success "정답"
    ```sql
    SELECT
        c.id          AS customer_id,
        c.name,
        c.point_balance AS current_balance,
        SUM(pt.amount)  AS calculated_balance,
        c.point_balance - SUM(pt.amount) AS difference
    FROM customers AS c
    INNER JOIN point_transactions AS pt ON c.id = pt.customer_id
    GROUP BY c.id, c.name, c.point_balance
    HAVING ABS(c.point_balance - SUM(pt.amount)) > 0
    ORDER BY ABS(difference) DESC
    LIMIT 20;
    ```


---
