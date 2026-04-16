# 실무 SQL 패턴

!!! info "사용 테이블"

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `categories` — 카테고리 (부모-자식 계층)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `payments` — 결제 (방법, 금액, 상태)  

    `calendar` — 날짜 차원 (요일, 공휴일)  

    `product_views` — 조회 로그 (고객, 상품, 일시)  

    `carts` — 장바구니 (상태)  

    `cart_items` — 장바구니 상품 (수량)  



!!! abstract "학습 범위"

    `Top-N per Group`, `Gap Analysis`, `Pivot`, `Session Analysis`, `Pareto 80/20`, `Funnel`, `Consecutive Period Detection`



### 1. 카테고리별 매출 Top-3 상품 (ROW_NUMBER)


각 **최하위 카테고리**(depth = 2)에서 2024년 매출 상위 3개 상품을 추출하세요.
동일 매출일 경우 판매 수량이 많은 상품이 우선합니다.

| category | product_name | revenue | units_sold | rank |
|----------|-------------|---------|-----------|------|
| ... | ... | ... | ... | 1 |


**힌트 1:** - `ROW_NUMBER() OVER (PARTITION BY cat.id ORDER BY revenue DESC, units_sold DESC)`
- CTE에서 순위를 매긴 후 `WHERE rn <= 3`으로 필터링
- `categories.depth = 2`로 최하위 카테고리만 대상



??? success "정답"
    ```sql
    WITH product_sales AS (
        SELECT
            cat.id   AS cat_id,
            cat.name AS category,
            p.name   AS product_name,
            SUM(oi.quantity * oi.unit_price) AS revenue,
            SUM(oi.quantity)                 AS units_sold
        FROM order_items   AS oi
        JOIN orders         AS o   ON oi.order_id   = o.id
        JOIN products       AS p   ON oi.product_id = p.id
        JOIN categories     AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
          AND o.ordered_at >= '2024-01-01'
          AND o.ordered_at <  '2025-01-01'
          AND cat.depth = 2
        GROUP BY cat.id, cat.name, p.id, p.name
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (
                PARTITION BY cat_id
                ORDER BY revenue DESC, units_sold DESC
            ) AS rn
        FROM product_sales
    )
    SELECT category, product_name,
           ROUND(revenue, 0) AS revenue,
           units_sold,
           rn AS rank
    FROM ranked
    WHERE rn <= 3
    ORDER BY category, rn;
    ```


---


### 2. 주문이 없는 날짜 찾기 (Gap Analysis)


`calendar` 테이블을 활용하여, 2024년 중 **주문이 단 한 건도 없었던 날짜**를 모두 찾으세요.
평일/주말 구분과 공휴일 여부도 함께 표시합니다.

| date_key | day_name | is_weekend | is_holiday | holiday_name |
|----------|----------|-----------|-----------|-------------|
| 2024-01-01 | Monday | 0 | 1 | 신정 |


**힌트 1:** - `calendar LEFT JOIN orders`로 모든 날짜를 기준으로 주문 여부 확인
- `WHERE o.id IS NULL`로 주문이 없는 날 필터링
- `calendar.date_key BETWEEN '2024-01-01' AND '2024-12-31'`



??? success "정답"
    ```sql
    SELECT
        cal.date_key,
        cal.day_name,
        cal.is_weekend,
        cal.is_holiday,
        cal.holiday_name
    FROM calendar AS cal
    LEFT JOIN orders AS o
        ON DATE(o.ordered_at) = cal.date_key
       AND o.status NOT IN ('cancelled')
    WHERE cal.date_key BETWEEN '2024-01-01' AND '2024-12-31'
      AND o.id IS NULL
    ORDER BY cal.date_key;
    ```


---


### 3. 요일별 매출 피벗 테이블 (CASE + SUM)


2024년 **월별 x 요일별** 매출을 피벗 형태로 표시하세요.
행은 월(YYYY-MM), 열은 월~일 7개 요일입니다.

| year_month | mon | tue | wed | thu | fri | sat | sun |
|------------|-----|-----|-----|-----|-----|-----|-----|
| 2024-01 | ... | ... | ... | ... | ... | ... | ... |


**힌트 1:** - `SUM(CASE WHEN STRFTIME('%w', ordered_at) = '1' THEN total_amount ELSE 0 END) AS mon`
- SQLite의 `%w`에서 0=일, 1=월, ..., 6=토
- 월 추출: `SUBSTR(ordered_at, 1, 7)`



??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS year_month,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '1' THEN total_amount ELSE 0 END) AS INTEGER) AS mon,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '2' THEN total_amount ELSE 0 END) AS INTEGER) AS tue,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '3' THEN total_amount ELSE 0 END) AS INTEGER) AS wed,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '4' THEN total_amount ELSE 0 END) AS INTEGER) AS thu,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '5' THEN total_amount ELSE 0 END) AS INTEGER) AS fri,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '6' THEN total_amount ELSE 0 END) AS INTEGER) AS sat,
        CAST(SUM(CASE WHEN STRFTIME('%w', ordered_at) = '0' THEN total_amount ELSE 0 END) AS INTEGER) AS sun
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at <  '2025-01-01'
      AND status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY year_month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | year_month | mon | tue | wed | thu | fri | sat | sun |
    |---|---|---|---|---|---|---|---|
    | 2024-01 | 40,764,141 | 44,602,205 | 26,410,593 | 20,436,018 | 56,605,231 | 43,280,158 | 56,809,974 |
    | 2024-02 | 67,387,251 | 43,032,032 | 60,487,619 | 48,877,254 | 71,804,613 | 54,551,823 | 56,987,157 |
    | 2024-03 | 70,180,297 | 67,897,538 | 62,691,902 | 58,905,080 | 71,182,311 | 76,903,414 | 112,083,960 |
    | 2024-04 | 74,561,175 | 59,707,159 | 69,537,704 | 77,984,882 | 46,198,503 | 57,318,794 | 66,569,364 |
    | 2024-05 | 36,746,395 | 56,164,229 | 70,892,739 | 42,604,957 | 67,015,276 | 62,260,346 | 89,580,536 |
    | 2024-06 | 54,376,757 | 45,870,213 | 38,061,084 | 42,811,574 | 42,127,592 | 64,215,372 | 75,252,619 |
    | 2024-07 | 41,682,991 | 57,833,464 | 28,230,471 | 53,964,486 | 59,101,476 | 65,949,332 | 37,167,677 |


---


### 4. 누적 매출 비율 (Running Percentage)


2024년 상품별 매출을 구하고, 매출이 높은 순으로 **누적 매출 비율(%)**을 계산하세요.
전체 매출의 80%를 차지하는 상품까지 표시합니다.

| product_name | revenue | pct | cumulative_pct |
|-------------|---------|-----|---------------|
| ... | ... | 12.3 | 12.3 |
| ... | ... | 8.5 | 20.8 |


**힌트 1:** - `SUM(revenue) OVER (ORDER BY revenue DESC)` / 전체 합계로 누적 비율 계산
- CTE 1단계: 상품별 매출 합계
- CTE 2단계: 누적 비율 계산 후 `WHERE cumulative_pct <= 80`



??? success "정답"
    ```sql
    WITH product_rev AS (
        SELECT
            p.name AS product_name,
            SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items AS oi
        JOIN orders   AS o ON oi.order_id   = o.id
        JOIN products AS p ON oi.product_id = p.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
          AND o.ordered_at >= '2024-01-01'
          AND o.ordered_at <  '2025-01-01'
        GROUP BY p.id, p.name
    ),
    cumulative AS (
        SELECT
            product_name,
            ROUND(revenue, 0) AS revenue,
            ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS pct,
            ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC)
                / SUM(revenue) OVER (), 2) AS cumulative_pct
        FROM product_rev
    )
    SELECT product_name, revenue, pct, cumulative_pct
    FROM cumulative
    WHERE cumulative_pct <= 80
    ORDER BY revenue DESC;
    ```


    **실행 결과** (총 88행 중 상위 7행)

    | product_name | revenue | pct | cumulative_pct |
    |---|---|---|---|
    | Razer Blade 18 블랙 | 165,417,800.00 | 3.21 | 3.21 |
    | Razer Blade 16 실버 | 137,007,300.00 | 2.65 | 5.86 |
    | MacBook Air 15 M3 실버 | 126,065,300.00 | 2.44 | 8.30 |
    | ASUS Dual RTX 4060 Ti 블랙 | 106,992,000.00 | 2.07 | 10.38 |
    | ASUS Dual RTX 5070 Ti 실버 | 104,558,400.00 | 2.03 | 12.40 |
    | ASUS ROG Swift PG32UCDM 실버 | 90,734,400.00 | 1.76 | 14.16 |
    | ASUS ROG Strix Scar 16 | 85,837,500.00 | 1.66 | 15.82 |


---


### 5. 결제 수단별 월별 비중 변화


2024년 **결제 수단(method)**별 월별 결제 금액 비중(%)의 추이를 보여주세요.
각 월에서 결제 수단이 차지하는 비중을 계산합니다.

| year_month | card_pct | bank_transfer_pct | kakao_pay_pct | naver_pay_pct | other_pct |
|------------|---------|------------------|-------------|-------------|----------|
| 2024-01 | 62.3 | 15.1 | 12.0 | 8.5 | 2.1 |


**힌트 1:** - `CASE WHEN method = 'card' THEN amount ELSE 0 END`로 수단별 합계
- 각 수단 합계를 월 전체 합계로 나누어 비중 산출
- 소수 결제 수단(virtual_account, point)은 'other'로 묶기



??? success "정답"
    ```sql
    SELECT
        SUBSTR(p.paid_at, 1, 7) AS year_month,
        ROUND(100.0 * SUM(CASE WHEN p.method = 'card' THEN p.amount ELSE 0 END)
            / SUM(p.amount), 1) AS card_pct,
        ROUND(100.0 * SUM(CASE WHEN p.method = 'bank_transfer' THEN p.amount ELSE 0 END)
            / SUM(p.amount), 1) AS bank_transfer_pct,
        ROUND(100.0 * SUM(CASE WHEN p.method = 'kakao_pay' THEN p.amount ELSE 0 END)
            / SUM(p.amount), 1) AS kakao_pay_pct,
        ROUND(100.0 * SUM(CASE WHEN p.method = 'naver_pay' THEN p.amount ELSE 0 END)
            / SUM(p.amount), 1) AS naver_pay_pct,
        ROUND(100.0 * SUM(CASE WHEN p.method NOT IN ('card','bank_transfer','kakao_pay','naver_pay')
            THEN p.amount ELSE 0 END) / SUM(p.amount), 1) AS other_pct
    FROM payments AS p
    WHERE p.status = 'completed'
      AND p.paid_at >= '2024-01-01'
      AND p.paid_at <  '2025-01-01'
    GROUP BY SUBSTR(p.paid_at, 1, 7)
    ORDER BY year_month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | year_month | card_pct | bank_transfer_pct | kakao_pay_pct | naver_pay_pct | other_pct |
    |---|---|---|---|---|---|
    | 2024-01 | 51.00 | 8.40 | 18.40 | 11.50 | 10.70 |
    | 2024-02 | 42.10 | 7.00 | 18.60 | 20.00 | 12.30 |
    | 2024-03 | 40.40 | 8.80 | 22.30 | 15.80 | 12.70 |
    | 2024-04 | 46.10 | 10.20 | 22.50 | 11.50 | 9.60 |
    | 2024-05 | 55.20 | 7.40 | 16.80 | 12.60 | 8.00 |
    | 2024-06 | 51.30 | 8.10 | 21.40 | 10.50 | 8.60 |
    | 2024-07 | 54.20 | 10.60 | 16.70 | 10.90 | 7.60 |


---


### 6. 세션 분석: 30분 간격 기반 (product_views)


`product_views` 테이블에서 고객별 **브라우징 세션**을 식별하세요.
이전 조회와 30분 이상 간격이 있으면 새로운 세션으로 간주합니다.
고객별 세션 수, 세션당 평균 조회 수, 평균 세션 시간(분)을 구하세요.

| customer_id | total_sessions | avg_views_per_session | avg_session_minutes |
|------------|---------------|----------------------|-------------------|
| ... | ... | ... | ... |


**힌트 1:** - `LAG(viewed_at) OVER (PARTITION BY customer_id ORDER BY viewed_at)`로 이전 조회 시각 참조
- 간격 > 1800초이면 새 세션 시작 (`julianday` 차이 * 86400)
- `SUM(is_new_session) OVER (PARTITION BY customer_id ORDER BY viewed_at)`로 세션 번호 부여



??? success "정답"
    ```sql
    WITH view_gaps AS (
        SELECT
            customer_id,
            viewed_at,
            CASE
                WHEN (julianday(viewed_at) - julianday(
                    LAG(viewed_at) OVER (PARTITION BY customer_id ORDER BY viewed_at)
                )) * 86400 > 1800
                OR LAG(viewed_at) OVER (PARTITION BY customer_id ORDER BY viewed_at) IS NULL
                THEN 1
                ELSE 0
            END AS is_new_session
        FROM product_views
    ),
    sessions AS (
        SELECT
            customer_id,
            viewed_at,
            SUM(is_new_session) OVER (
                PARTITION BY customer_id ORDER BY viewed_at
            ) AS session_id
        FROM view_gaps
    ),
    session_stats AS (
        SELECT
            customer_id,
            session_id,
            COUNT(*) AS view_count,
            ROUND((julianday(MAX(viewed_at)) - julianday(MIN(viewed_at))) * 1440, 1) AS session_minutes
        FROM sessions
        GROUP BY customer_id, session_id
    )
    SELECT
        customer_id,
        COUNT(*) AS total_sessions,
        ROUND(AVG(view_count), 1) AS avg_views_per_session,
        ROUND(AVG(session_minutes), 1) AS avg_session_minutes
    FROM session_stats
    GROUP BY customer_id
    HAVING COUNT(*) >= 3
    ORDER BY total_sessions DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer_id | total_sessions | avg_views_per_session | avg_session_minutes |
    |---|---|---|---|
    | 97 | 2613 | 1.00 | 0.5 |
    | 226 | 2300 | 1.00 | 0.5 |
    | 98 | 1838 | 1.10 | 0.5 |
    | 162 | 1788 | 1.00 | 0.6 |
    | 227 | 1730 | 1.10 | 0.6 |
    | 549 | 1725 | 1.00 | 0.7 |
    | 356 | 1695 | 1.10 | 0.6 |


---


### 7. 고객 연속 구매일 (Consecutive Days)


2024년에 **연속으로 주문한 일수**가 가장 긴 고객 Top 10을 찾으세요.
연속 주문이란 날짜가 하루도 빠지지 않고 이어지는 것을 의미합니다.

| customer_name | consecutive_days | streak_start | streak_end |
|-------------|-----------------|------------|----------|
| ... | 5 | 2024-11-25 | 2024-11-29 |


**힌트 1:** - `DATE(ordered_at)`에서 `ROW_NUMBER()`를 빼면 연속 그룹이 동일한 값을 가짐
- `DATE(ordered_at, '-' || ROW_NUMBER() || ' days')` 패턴
- 같은 날 여러 주문이 있을 수 있으므로 `DISTINCT DATE(ordered_at)` 먼저 처리



??? success "정답"
    ```sql
    WITH daily_orders AS (
        SELECT DISTINCT
            customer_id,
            DATE(ordered_at) AS order_date
        FROM orders
        WHERE ordered_at >= '2024-01-01'
          AND ordered_at <  '2025-01-01'
          AND status NOT IN ('cancelled')
    ),
    numbered AS (
        SELECT
            customer_id,
            order_date,
            DATE(order_date, '-' || (ROW_NUMBER() OVER (
                PARTITION BY customer_id ORDER BY order_date
            ) - 1) || ' days') AS grp
        FROM daily_orders
    ),
    streaks AS (
        SELECT
            customer_id,
            grp,
            COUNT(*) AS consecutive_days,
            MIN(order_date) AS streak_start,
            MAX(order_date) AS streak_end
        FROM numbered
        GROUP BY customer_id, grp
        HAVING COUNT(*) >= 2
    )
    SELECT
        c.name AS customer_name,
        s.consecutive_days,
        s.streak_start,
        s.streak_end
    FROM streaks AS s
    JOIN customers AS c ON s.customer_id = c.id
    ORDER BY s.consecutive_days DESC, s.streak_start
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | customer_name | consecutive_days | streak_start | streak_end |
    |---|---|---|---|
    | 김명숙 | 3 | 2024-02-01 | 2024-02-03 |
    | 박건우 | 3 | 2024-02-22 | 2024-02-24 |
    | 최상호 | 3 | 2024-03-25 | 2024-03-27 |
    | 박현정 | 3 | 2024-03-27 | 2024-03-29 |
    | 강순옥 | 3 | 2024-11-24 | 2024-11-26 |
    | 박재호 | 2 | 2024-01-10 | 2024-01-11 |
    | 강춘자 | 2 | 2024-01-17 | 2024-01-18 |


---


### 8. 파레토 분석: 매출 80%를 만드는 고객 비율


전체 고객 중 **상위 몇 %의 고객이 매출의 80%를 차지**하는지 파레토 분석을 수행하세요.
고객을 매출 순으로 정렬하고 누적 비율을 구합니다.

| customer_name | total_spent | pct_of_revenue | cumulative_pct | customer_rank | total_customers | customer_pct |
|-------------|-----------|---------------|---------------|-------------|----------------|-------------|


**힌트 1:** - 고객별 매출 합계 → 매출 내림차순 정렬
- `SUM(total_spent) OVER (ORDER BY total_spent DESC)` / 전체 합계
- `ROW_NUMBER()` / `COUNT(*) OVER ()`로 고객 순위 비율



??? success "정답"
    ```sql
    WITH customer_revenue AS (
        SELECT
            c.id,
            c.name AS customer_name,
            SUM(o.total_amount) AS total_spent
        FROM orders AS o
        JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name
    ),
    pareto AS (
        SELECT
            customer_name,
            CAST(total_spent AS INTEGER) AS total_spent,
            ROUND(100.0 * total_spent / SUM(total_spent) OVER (), 2) AS pct_of_revenue,
            ROUND(100.0 * SUM(total_spent) OVER (ORDER BY total_spent DESC)
                / SUM(total_spent) OVER (), 2) AS cumulative_pct,
            ROW_NUMBER() OVER (ORDER BY total_spent DESC) AS customer_rank,
            COUNT(*) OVER () AS total_customers
        FROM customer_revenue
    )
    SELECT
        customer_name,
        total_spent,
        pct_of_revenue,
        cumulative_pct,
        customer_rank,
        total_customers,
        ROUND(100.0 * customer_rank / total_customers, 1) AS customer_pct
    FROM pareto
    WHERE cumulative_pct <= 80
    ORDER BY customer_rank;
    ```


    **실행 결과** (총 754행 중 상위 7행)

    | customer_name | total_spent | pct_of_revenue | cumulative_pct | customer_rank | total_customers | customer_pct |
    |---|---|---|---|---|---|---|
    | 박정수 | 403,448,758 | 1.16 | 1.16 | 1 | 2793 | 0.0 |
    | 김병철 | 366,385,931 | 1.05 | 2.21 | 2 | 2793 | 0.1 |
    | 강명자 | 253,180,338 | 0.73 | 2.94 | 3 | 2793 | 0.1 |
    | 정유진 | 244,604,910 | 0.7 | 3.65 | 4 | 2793 | 0.1 |
    | 이미정 | 235,775,349 | 0.68 | 4.32 | 5 | 2793 | 0.2 |
    | 김성민 | 234,708,853 | 0.68 | 5.00 | 6 | 2793 | 0.2 |
    | 이영자 | 230,165,991 | 0.66 | 5.66 | 7 | 2793 | 0.3 |


---


### 9. 등급별 이탈률 분석 (Churn)


고객 등급별로 **최근 6개월(2025-01-01 ~ 2025-06-30) 이내 주문이 없는** 고객의 비율(이탈률)을 구하세요.
등급별 전체 고객 수, 활성 고객 수, 이탈 고객 수, 이탈률을 표시합니다.

| grade | total_customers | active_customers | churned_customers | churn_rate_pct |
|-------|----------------|-----------------|------------------|---------------|
| VIP | ... | ... | ... | ... |


**힌트 1:** - `customers LEFT JOIN orders`에서 주문 날짜 조건으로 활성/이탈 구분
- 6개월 이내 주문이 있으면 활성, 없으면 이탈
- `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`로 조건부 카운트



??? success "정답"
    ```sql
    WITH customer_activity AS (
        SELECT
            c.id,
            c.grade,
            MAX(o.ordered_at) AS last_order_at
        FROM customers AS c
        LEFT JOIN orders AS o
            ON c.id = o.customer_id
           AND o.status NOT IN ('cancelled')
        WHERE c.is_active = 1
        GROUP BY c.id, c.grade
    )
    SELECT
        grade,
        COUNT(*) AS total_customers,
        SUM(CASE WHEN last_order_at >= '2025-01-01' THEN 1 ELSE 0 END) AS active_customers,
        SUM(CASE WHEN last_order_at < '2025-01-01' OR last_order_at IS NULL THEN 1 ELSE 0 END) AS churned_customers,
        ROUND(100.0 * SUM(CASE WHEN last_order_at < '2025-01-01' OR last_order_at IS NULL THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS churn_rate_pct
    FROM customer_activity
    GROUP BY grade
    ORDER BY
        CASE grade WHEN 'VIP' THEN 1 WHEN 'GOLD' THEN 2 WHEN 'SILVER' THEN 3 ELSE 4 END;
    ```


    **실행 결과** (4행)

    | grade | total_customers | active_customers | churned_customers | churn_rate_pct |
    |---|---|---|---|---|
    | VIP | 368 | 368 | 0 | 0.0 |
    | GOLD | 524 | 524 | 0 | 0.0 |
    | SILVER | 479 | 477 | 2 | 0.4 |
    | BRONZE | 2289 | 668 | 1621 | 70.80 |


---


### 10. 장바구니 → 주문 전환 시간 분석


장바구니(`carts`) 상태가 'converted'인 건에 대해, **장바구니 생성부터 주문까지 걸린 시간**을 분석하세요.
평균/중위수/최소/최대 전환 시간(시간 단위)과 요일별 평균 전환 시간을 구하세요.

| day_name | avg_hours | min_hours | max_hours | converted_count |
|----------|----------|----------|----------|----------------|


**힌트 1:** - 'converted' 장바구니의 `customer_id`와 `created_at`으로 가장 가까운 주문 매칭
- `julianday(o.ordered_at) - julianday(c.created_at)` * 24로 시간 계산
- `STRFTIME('%w', c.created_at)`로 요일 구분



??? success "정답"
    ```sql
    WITH converted_carts AS (
        SELECT
            ca.id AS cart_id,
            ca.customer_id,
            ca.created_at AS cart_created,
            MIN(o.ordered_at) AS first_order_after
        FROM carts AS ca
        JOIN orders AS o
            ON ca.customer_id = o.customer_id
           AND o.ordered_at >= ca.created_at
           AND o.status NOT IN ('cancelled')
        WHERE ca.status = 'converted'
        GROUP BY ca.id, ca.customer_id, ca.created_at
    ),
    hours_calc AS (
        SELECT
            cart_id,
            ROUND((julianday(first_order_after) - julianday(cart_created)) * 24, 1) AS hours_to_convert,
            CASE CAST(STRFTIME('%w', cart_created) AS INTEGER)
                WHEN 0 THEN 'Sun' WHEN 1 THEN 'Mon' WHEN 2 THEN 'Tue'
                WHEN 3 THEN 'Wed' WHEN 4 THEN 'Thu' WHEN 5 THEN 'Fri' WHEN 6 THEN 'Sat'
            END AS day_name,
            CAST(STRFTIME('%w', cart_created) AS INTEGER) AS dow
        FROM converted_carts
    )
    SELECT
        day_name,
        ROUND(AVG(hours_to_convert), 1) AS avg_hours,
        ROUND(MIN(hours_to_convert), 1) AS min_hours,
        ROUND(MAX(hours_to_convert), 1) AS max_hours,
        COUNT(*) AS converted_count
    FROM hours_calc
    GROUP BY day_name, dow
    ORDER BY dow;
    ```


    **실행 결과** (7행)

    | day_name | avg_hours | min_hours | max_hours | converted_count |
    |---|---|---|---|---|
    | Sun | 3,439.30 | 9.40 | 24,098.00 | 125 |
    | Mon | 3,719.50 | 0.9 | 34,589.40 | 132 |
    | Tue | 3,623.20 | 26.20 | 20,473.50 | 116 |
    | Wed | 3,547.80 | 11.60 | 30,182.70 | 119 |
    | Thu | 4,071.40 | 2.60 | 28,918.00 | 125 |
    | Fri | 4,224.40 | 14.70 | 27,035.30 | 115 |
    | Sat | 3,862.80 | 3.20 | 38,807.50 | 137 |


---


### 11. 구매 퍼널 분석 (View → Cart → Order)


**상품 조회 → 장바구니 담기 → 주문**의 3단계 퍼널을 분석하세요.
2024년 데이터 기준으로 각 단계의 고유 고객 수와 전환율(%)을 계산합니다.

| funnel_step | unique_customers | conversion_rate_pct |
|------------|-----------------|-------------------|
| 1. View | 1500 | 100.0 |
| 2. Cart | 800 | 53.3 |
| 3. Order | 600 | 75.0 |


**힌트 1:** - Step 1: `product_views`에서 고유 고객 수
- Step 2: `cart_items → carts`에서 고유 고객 수
- Step 3: `orders`에서 고유 고객 수
- 전환율: 현재 단계 / 이전 단계 * 100
- `UNION ALL`로 3단계를 하나의 결과로 합치기



??? success "정답"
    ```sql
    WITH step_viewers AS (
        SELECT COUNT(DISTINCT customer_id) AS cnt
        FROM product_views
        WHERE viewed_at >= '2024-01-01' AND viewed_at < '2025-01-01'
    ),
    step_carters AS (
        SELECT COUNT(DISTINCT ca.customer_id) AS cnt
        FROM carts AS ca
        JOIN cart_items AS ci ON ca.id = ci.cart_id
        WHERE ci.added_at >= '2024-01-01' AND ci.added_at < '2025-01-01'
          AND ca.customer_id IN (
              SELECT DISTINCT customer_id
              FROM product_views
              WHERE viewed_at >= '2024-01-01' AND viewed_at < '2025-01-01'
          )
    ),
    step_buyers AS (
        SELECT COUNT(DISTINCT o.customer_id) AS cnt
        FROM orders AS o
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled')
          AND o.customer_id IN (
              SELECT DISTINCT ca.customer_id
              FROM carts AS ca
              JOIN cart_items AS ci ON ca.id = ci.cart_id
              WHERE ci.added_at >= '2024-01-01' AND ci.added_at < '2025-01-01'
          )
    ),
    funnel AS (
        SELECT 1 AS step, '1. View' AS funnel_step, cnt FROM step_viewers
        UNION ALL
        SELECT 2, '2. Cart', cnt FROM step_carters
        UNION ALL
        SELECT 3, '3. Order', cnt FROM step_buyers
    )
    SELECT
        funnel_step,
        cnt AS unique_customers,
        ROUND(100.0 * cnt / LAG(cnt) OVER (ORDER BY step), 1) AS conversion_rate_pct
    FROM funnel
    ORDER BY step;
    ```


    **실행 결과** (3행)

    | funnel_step | unique_customers | conversion_rate_pct |
    |---|---|---|
    | 1. View | 2809 | NULL |
    | 2. Cart | 517 | 18.40 |
    | 3. Order | 311 | 60.20 |


---


### 12. 중복 데이터 정제 (Deduplication)


같은 고객이 같은 상품에 대해 **같은 날** 여러 건의 리뷰를 작성한 경우,
가장 최근 리뷰만 남기고 나머지의 id를 식별하세요.
(실제 DELETE 없이 삭제 대상 id 목록을 추출합니다.)

| duplicate_review_id | customer_name | product_name | created_at | keep_review_id |
|-------------------|-------------|-------------|-----------|---------------|


**힌트 1:** - `ROW_NUMBER() OVER (PARTITION BY customer_id, product_id, DATE(created_at) ORDER BY created_at DESC)` 로 최신 1건에 `rn = 1` 부여
- `rn > 1`인 행이 삭제 대상
- 동일 파티션에서 `rn = 1`인 행의 id를 keep_review_id로 표시



??? success "정답"
    ```sql
    WITH ranked_reviews AS (
        SELECT
            r.id,
            r.customer_id,
            r.product_id,
            r.created_at,
            ROW_NUMBER() OVER (
                PARTITION BY r.customer_id, r.product_id, DATE(r.created_at)
                ORDER BY r.created_at DESC
            ) AS rn,
            FIRST_VALUE(r.id) OVER (
                PARTITION BY r.customer_id, r.product_id, DATE(r.created_at)
                ORDER BY r.created_at DESC
            ) AS keep_id
        FROM reviews AS r
    )
    SELECT
        rr.id AS duplicate_review_id,
        c.name AS customer_name,
        p.name AS product_name,
        rr.created_at,
        rr.keep_id AS keep_review_id
    FROM ranked_reviews AS rr
    JOIN customers AS c ON rr.customer_id = c.id
    JOIN products  AS p ON rr.product_id  = p.id
    WHERE rr.rn > 1
    ORDER BY rr.customer_id, rr.product_id, rr.created_at;
    ```


---


### 13. 공급업체 의존도 분석


각 **공급업체(supplier)**가 전체 매출에서 차지하는 비중을 구하고,
매출 비중 10% 이상인 공급업체를 **고위험 의존** 업체로 분류하세요.
상품 수, 매출, 비중, 반품률도 함께 분석합니다.

| supplier | product_count | revenue | revenue_pct | return_rate_pct | risk_level |
|----------|-------------|---------|-----------|----------------|-----------|
| ... | ... | ... | 15.2 | 3.1 | HIGH |


**힌트 1:** - `products → suppliers`로 공급업체별 매출 합산
- 반품률: 해당 공급업체 상품의 반품 건수 / 주문 건수
- `CASE WHEN revenue_pct >= 10 THEN 'HIGH' ... END`



??? success "정답"
    ```sql
    WITH supplier_sales AS (
        SELECT
            s.id AS supplier_id,
            s.company_name AS supplier,
            COUNT(DISTINCT p.id) AS product_count,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM suppliers AS s
        LEFT JOIN products AS p ON s.id = p.supplier_id
        LEFT JOIN order_items AS oi ON p.id = oi.product_id
        LEFT JOIN orders AS o ON oi.order_id = o.id
            AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY s.id, s.company_name
    ),
    supplier_returns AS (
        SELECT
            p.supplier_id,
            COUNT(DISTINCT r.id) AS return_count,
            COUNT(DISTINCT o.id) AS order_count
        FROM products AS p
        JOIN order_items AS oi ON p.id = oi.product_id
        JOIN orders AS o ON oi.order_id = o.id
        LEFT JOIN returns AS r ON o.id = r.order_id
        GROUP BY p.supplier_id
    )
    SELECT
        ss.supplier,
        ss.product_count,
        CAST(ss.revenue AS INTEGER) AS revenue,
        ROUND(100.0 * ss.revenue / NULLIF(SUM(ss.revenue) OVER (), 0), 1) AS revenue_pct,
        ROUND(100.0 * COALESCE(sr.return_count, 0) / NULLIF(sr.order_count, 0), 1) AS return_rate_pct,
        CASE
            WHEN 100.0 * ss.revenue / NULLIF(SUM(ss.revenue) OVER (), 0) >= 10 THEN 'HIGH'
            WHEN 100.0 * ss.revenue / NULLIF(SUM(ss.revenue) OVER (), 0) >= 5  THEN 'MEDIUM'
            ELSE 'LOW'
        END AS risk_level
    FROM supplier_sales AS ss
    LEFT JOIN supplier_returns AS sr ON ss.supplier_id = sr.supplier_id
    WHERE ss.revenue > 0
    ORDER BY ss.revenue DESC;
    ```


    **실행 결과** (총 45행 중 상위 7행)

    | supplier | product_count | revenue | revenue_pct | return_rate_pct | risk_level |
    |---|---|---|---|---|---|
    | 에이수스코리아 | 26 | 6,239,864,300 | 16.20 | 3.50 | HIGH |
    | 레이저코리아 | 9 | 4,203,062,600 | 10.90 | 4.10 | HIGH |
    | 삼성전자 공식 유통 | 25 | 3,028,089,900 | 7.90 | 2.90 | MEDIUM |
    | MSI코리아 | 13 | 2,815,063,400 | 7.30 | 3.50 | MEDIUM |
    | LG전자 공식 유통 | 11 | 2,240,909,900 | 5.80 | 3.60 | MEDIUM |
    | ASRock코리아 | 11 | 1,756,828,300 | 4.60 | 3.30 | LOW |
    | 인텔코리아 | 6 | 1,281,251,700 | 3.30 | 3.20 | LOW |


---


### 14. 코호트 리텐션 매트릭스 (가입월 기준)


고객의 **가입 월** 기준으로 코호트를 구성하고,
가입 후 1~6개월 시점에 재구매한 고객 비율(리텐션)을 매트릭스로 보여주세요.
2024년 상반기(1~6월) 가입 코호트 대상입니다.

| cohort | cohort_size | m1_pct | m2_pct | m3_pct | m4_pct | m5_pct | m6_pct |
|--------|-----------|-------|-------|-------|-------|-------|-------|
| 2024-01 | 150 | 45.0 | 32.0 | 28.5 | ... | ... | ... |


**힌트 1:** - 코호트: `SUBSTR(c.created_at, 1, 7)` = 가입월
- 활성 여부: 가입 후 N개월 시점에 주문이 있는지 확인
- 월 차이 계산: `CAST((julianday(SUBSTR(o.ordered_at,1,7)||'-01') - julianday(SUBSTR(c.created_at,1,7)||'-01')) / 30 AS INTEGER)`



??? success "정답"
    ```sql
    WITH cohorts AS (
        SELECT
            c.id AS customer_id,
            SUBSTR(c.created_at, 1, 7) AS cohort
        FROM customers AS c
        WHERE c.created_at >= '2024-01-01'
          AND c.created_at <  '2024-07-01'
    ),
    order_months AS (
        SELECT DISTINCT
            co.customer_id,
            co.cohort,
            CAST(
                (julianday(SUBSTR(o.ordered_at, 1, 7) || '-01')
               - julianday(co.cohort || '-01')) / 30
            AS INTEGER) AS month_offset
        FROM cohorts AS co
        JOIN orders AS o ON co.customer_id = o.customer_id
        WHERE o.status NOT IN ('cancelled')
          AND o.ordered_at >= '2024-01-01'
    )
    SELECT
        cohort,
        COUNT(DISTINCT customer_id) AS cohort_size,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 1 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m1_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 2 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m2_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 3 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m3_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 4 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m4_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 5 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m5_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_offset = 6 THEN customer_id END)
            / COUNT(DISTINCT customer_id), 1) AS m6_pct
    FROM (
        SELECT DISTINCT customer_id, cohort FROM cohorts
    ) AS base
    LEFT JOIN order_months AS om USING (customer_id, cohort)
    GROUP BY cohort
    ORDER BY cohort;
    ```


    **실행 결과** (6행)

    | cohort | cohort_size | m1_pct | m2_pct | m3_pct | m4_pct | m5_pct | m6_pct |
    |---|---|---|---|---|---|---|---|
    | 2024-01 | 52 | 5.80 | 9.60 | 7.70 | 3.80 | 3.80 | 3.80 |
    | 2024-02 | 48 | 0.0 | 6.30 | 10.40 | 8.30 | 6.30 | 10.40 |
    | 2024-03 | 71 | 14.10 | 15.50 | 2.80 | 12.70 | 14.10 | 14.10 |
    | 2024-04 | 53 | 7.50 | 7.50 | 3.80 | 17.00 | 11.30 | 18.90 |
    | 2024-05 | 43 | 9.30 | 16.30 | 4.70 | 18.60 | 9.30 | 18.60 |
    | 2024-06 | 68 | 5.90 | 5.90 | 8.80 | 10.30 | 11.80 | 8.80 |


---


### 15. 종합 대시보드: 경영진 KPI 스냅샷


CEO에게 보고할 **2024년 12월 경영 대시보드**를 단일 쿼리로 만드세요.
다음 KPI를 한 행으로 출력합니다:

- 총 매출, 전월 대비 성장률(%)
- 총 주문 수, 신규 고객 수, 재구매 고객 수
- 평균 주문 금액, 평균 배송 소요일
- 반품률(%), CS 문의 건수

| revenue | mom_growth_pct | order_count | new_customers | repeat_customers | avg_order_value | avg_delivery_days | return_rate_pct | cs_tickets |
|---------|---------------|------------|-------------|-----------------|----------------|------------------|----------------|-----------|


**힌트 1:** - 여러 테이블의 집계를 서브쿼리/CTE로 각각 구한 뒤 `CROSS JOIN`으로 한 행에 합치기
- 전월 매출은 `WHERE ordered_at LIKE '2024-11%'`로 별도 CTE
- 신규 고객: 2024년 12월에 첫 주문인 고객
- 재구매: 12월 이전에도 주문 이력이 있는 고객



??? success "정답"
    ```sql
    WITH dec_orders AS (
        SELECT *
        FROM orders
        WHERE ordered_at >= '2024-12-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    nov_revenue AS (
        SELECT SUM(total_amount) AS rev
        FROM orders
        WHERE ordered_at >= '2024-11-01' AND ordered_at < '2024-12-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    dec_sales AS (
        SELECT
            SUM(total_amount) AS revenue,
            COUNT(*) AS order_count,
            ROUND(AVG(total_amount), 0) AS avg_order_value
        FROM dec_orders
    ),
    dec_customers AS (
        SELECT
            COUNT(DISTINCT CASE
                WHEN NOT EXISTS (
                    SELECT 1 FROM orders o2
                    WHERE o2.customer_id = d.customer_id
                      AND o2.ordered_at < '2024-12-01'
                      AND o2.status NOT IN ('cancelled')
                )
                THEN d.customer_id
            END) AS new_customers,
            COUNT(DISTINCT CASE
                WHEN EXISTS (
                    SELECT 1 FROM orders o2
                    WHERE o2.customer_id = d.customer_id
                      AND o2.ordered_at < '2024-12-01'
                      AND o2.status NOT IN ('cancelled')
                )
                THEN d.customer_id
            END) AS repeat_customers
        FROM dec_orders AS d
    ),
    dec_shipping AS (
        SELECT ROUND(AVG(julianday(sh.delivered_at) - julianday(sh.shipped_at)), 1) AS avg_delivery_days
        FROM shipping AS sh
        JOIN orders AS o ON sh.order_id = o.id
        WHERE o.ordered_at >= '2024-12-01' AND o.ordered_at < '2025-01-01'
          AND sh.delivered_at IS NOT NULL
    ),
    dec_returns AS (
        SELECT
            ROUND(100.0 * COUNT(DISTINCT r.id) / NULLIF(COUNT(DISTINCT o.id), 0), 1) AS return_rate_pct
        FROM orders AS o
        LEFT JOIN returns AS r ON o.id = r.order_id
        WHERE o.ordered_at >= '2024-12-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled')
    ),
    dec_cs AS (
        SELECT COUNT(*) AS cs_tickets
        FROM complaints
        WHERE created_at >= '2024-12-01' AND created_at < '2025-01-01'
    )
    SELECT
        CAST(ds.revenue AS INTEGER) AS revenue,
        ROUND(100.0 * (ds.revenue - nr.rev) / nr.rev, 1) AS mom_growth_pct,
        ds.order_count,
        dc.new_customers,
        dc.repeat_customers,
        ds.avg_order_value,
        dsh.avg_delivery_days,
        dr.return_rate_pct,
        dcs.cs_tickets
    FROM dec_sales AS ds
    CROSS JOIN nov_revenue AS nr
    CROSS JOIN dec_customers AS dc
    CROSS JOIN dec_shipping AS dsh
    CROSS JOIN dec_returns AS dr
    CROSS JOIN dec_cs AS dcs;
    ```


    **실행 결과** (1행)

    | revenue | mom_growth_pct | order_count | new_customers | repeat_customers | avg_order_value | avg_delivery_days | return_rate_pct | cs_tickets |
    |---|---|---|---|---|---|---|---|---|
    | 417,148,762 | -23.20 | 459 | 37 | 342 | 908,821.00 | 2.50 | 3.20 | 48 |


---
