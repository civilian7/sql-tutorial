# SQL 면접 대비

!!! info "사용 테이블"

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `categories` — 카테고리 (부모-자식 계층)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `reviews` — 리뷰 (평점, 내용)  

    `product_views` — 조회 로그 (고객, 상품, 일시)  

    `calendar` — 날짜 차원 (요일, 공휴일)  

    `staff` — 직원 (부서, 역할, 관리자)  



!!! abstract "학습 범위"

    `DENSE_RANK`, `Consecutive N Days`, `Median`, `Session Analysis`, `MoM Growth Rate`, `Percentile`, `Working Days`, `Organization Chart Recursion`



### 1. 두 번째로 높은 매출 상품 ★★★


전체 상품 중 **총 매출이 두 번째로 높은** 상품을 구하세요.
매출이 가장 높은 상품과 동일 매출인 상품이 여러 개일 수 있으므로 `DENSE_RANK`를 사용합니다.

> **출제 빈도**: ★★★ (매우 높음) — Amazon, LeetCode #176 변형

| product_name | category | total_revenue | revenue_rank |
|-------------|----------|-------------|-------------|
| ... | ... | ... | 2 |


**힌트 1:** - `DENSE_RANK() OVER (ORDER BY total_revenue DESC)`: 동률 허용 순위
- CTE에서 상품별 매출 합산 → 순위 부여 → `WHERE rank = 2`



??? success "정답"
    ```sql
    WITH product_revenue AS (
        SELECT
            p.id,
            p.name AS product_name,
            cat.name AS category,
            SUM(oi.quantity * oi.unit_price) AS total_revenue
        FROM order_items AS oi
        JOIN orders     AS o   ON oi.order_id   = o.id
        JOIN products   AS p   ON oi.product_id = p.id
        JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY p.id, p.name, cat.name
    ),
    ranked AS (
        SELECT *,
            DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
        FROM product_revenue
    )
    SELECT product_name, category,
           CAST(total_revenue AS INTEGER) AS total_revenue,
           revenue_rank
    FROM ranked
    WHERE revenue_rank = 2;
    ```


    **실행 결과** (1행)

    | product_name | category | total_revenue | revenue_rank |
    |---|---|---|---|
    | Razer Blade 16 실버 | 게이밍 노트북 | 907,210,500 | 2 |


---


### 2. 누적 합계 (Running Total) ★★★


2024년 **월별 매출**과 **연초부터의 누적 매출(YTD)**을 구하세요.

> **출제 빈도**: ★★★ (매우 높음) — Google, Meta 빈출

| month | monthly_revenue | ytd_revenue |
|-------|----------------|------------|
| 2024-01 | ... | ... |


**힌트 1:** - `SUM(월별매출) OVER (ORDER BY month)` = 누적 합계
- 윈도우 함수의 기본 프레임은 `UNBOUNDED PRECEDING ~ CURRENT ROW`



??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        CAST(SUM(total_amount) AS INTEGER) AS monthly_revenue,
        CAST(SUM(SUM(total_amount)) OVER (ORDER BY SUBSTR(ordered_at, 1, 7)) AS INTEGER) AS ytd_revenue
    FROM orders
    WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | month | monthly_revenue | ytd_revenue |
    |---|---|---|
    | 2024-01 | 301,075,320 | 301,075,320 |
    | 2024-02 | 426,177,449 | 727,252,769 |
    | 2024-03 | 536,322,767 | 1,263,575,536 |
    | 2024-04 | 470,154,081 | 1,733,729,617 |
    | 2024-05 | 459,724,596 | 2,193,454,213 |
    | 2024-06 | 377,040,302 | 2,570,494,515 |
    | 2024-07 | 363,944,597 | 2,934,439,112 |


---


### 3. 중복 데이터 식별 ★★★


**동일 고객이 동일 상품에 같은 날 주문한** 건(중복 의심)을 찾으세요.
가장 최근 주문만 유효로 표시하고 나머지는 중복으로 플래그합니다.

> **출제 빈도**: ★★★ (매우 높음) — LeetCode #196 변형, 카카오

| order_id | customer_name | product_name | ordered_at | is_duplicate |
|---------|-------------|-------------|-----------|-------------|


**힌트 1:** - `ROW_NUMBER() OVER (PARTITION BY customer_id, product_id, DATE(ordered_at) ORDER BY ordered_at DESC)`
- `rn = 1`이면 유효, `rn > 1`이면 중복



??? success "정답"
    ```sql
    WITH order_detail AS (
        SELECT
            o.id AS order_id,
            o.customer_id,
            oi.product_id,
            o.ordered_at,
            ROW_NUMBER() OVER (
                PARTITION BY o.customer_id, oi.product_id, DATE(o.ordered_at)
                ORDER BY o.ordered_at DESC
            ) AS rn
        FROM orders AS o
        JOIN order_items AS oi ON o.id = oi.order_id
        WHERE o.status NOT IN ('cancelled')
    )
    SELECT
        od.order_id,
        c.name AS customer_name,
        p.name AS product_name,
        od.ordered_at,
        CASE WHEN od.rn > 1 THEN 'Y' ELSE 'N' END AS is_duplicate
    FROM order_detail AS od
    JOIN customers AS c ON od.customer_id = c.id
    JOIN products  AS p ON od.product_id  = p.id
    WHERE od.rn <= 2
    ORDER BY od.customer_id, od.product_id, DATE(od.ordered_at), od.rn;
    ```


    **실행 결과** (총 86,611행 중 상위 7행)

    | order_id | customer_name | product_name | ordered_at | is_duplicate |
    |---|---|---|---|---|
    | 1049 | 김경수 | Razer Blade 18 블랙 | 2017-12-04 15:52:09 | N |
    | 31,251 | 김경수 | Razer Blade 18 블랙 | 2025-01-02 18:41:57 | N |
    | 243 | 김경수 | MSI GeForce RTX 4070 Ti Super GAMING X | 2016-08-17 23:29:34 | N |
    | 17,814 | 김경수 | MSI GeForce RTX 4070 Ti Super GAMING X | 2022-07-18 12:29:51 | N |
    | 21,134 | 김경수 | MSI GeForce RTX 4070 Ti Super GAMING X | 2023-03-04 08:54:35 | N |
    | 5736 | 김경수 | Dell U2724D | 2020-03-09 16:09:46 | N |
    | 236 | 김경수 | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 2016-08-19 22:29:34 | N |


---


### 4. 중앙값 (Median) 구하기 ★★☆


고객별 주문 금액의 **중앙값(median)**을 구하세요.
SQLite에는 `MEDIAN` 함수가 없으므로 윈도우 함수로 구현합니다.

> **출제 빈도**: ★★☆ — Google, Amazon

| customer_name | order_count | median_amount |
|-------------|------------|-------------|
| ... | ... | ... |


**힌트 1:** - `ROW_NUMBER()`로 순위, `COUNT(*) OVER()`로 전체 건수
- 중앙값 = 전체 건수가 홀수이면 (n+1)/2번째, 짝수이면 n/2와 n/2+1의 평균
- `WHERE rn IN (cnt/2, cnt/2+1, (cnt+1)/2)`로 중앙 행 추출



??? success "정답"
    ```sql
    WITH numbered AS (
        SELECT
            customer_id,
            total_amount,
            ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY total_amount) AS rn,
            COUNT(*) OVER (PARTITION BY customer_id) AS cnt
        FROM orders
        WHERE status NOT IN ('cancelled')
    ),
    median_rows AS (
        SELECT
            customer_id,
            ROUND(AVG(total_amount), 0) AS median_amount,
            MAX(cnt) AS order_count
        FROM numbered
        WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
        GROUP BY customer_id
    )
    SELECT
        c.name AS customer_name,
        m.order_count,
        m.median_amount
    FROM median_rows AS m
    JOIN customers AS c ON m.customer_id = c.id
    WHERE m.order_count >= 5
    ORDER BY m.median_amount DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer_name | order_count | median_amount |
    |---|---|---|
    | 이진호 | 5 | 3,162,000.00 |
    | 박경수 | 5 | 2,741,600.00 |
    | 이민재 | 5 | 2,461,800.00 |
    | 김준영 | 12 | 2,403,150.00 |
    | 류명자 | 6 | 2,282,947.00 |
    | 황채원 | 5 | 2,281,800.00 |
    | 한승민 | 9 | 2,279,500.00 |


---


### 5. 연속 N일 로그인 (Islands) ★★★


`product_views`를 로그인 로그로 간주하여, **3일 이상 연속으로 활동한** 고객을 찾으세요.

> **출제 빈도**: ★★★ (매우 높음) — Meta, 쿠팡, LeetCode #180 변형

| customer_name | streak_days | streak_start | streak_end |
|-------------|-----------|------------|----------|


**힌트 1:** - `DATE(viewed_at)` 중복 제거 후 연속 날짜 그룹 탐지
- `DATE(viewed_at, '-' || (ROW_NUMBER()-1) || ' days')` → 같은 그룹이면 동일 값
- `HAVING COUNT(*) >= 3`



??? success "정답"
    ```sql
    WITH active_days AS (
        SELECT DISTINCT
            customer_id,
            DATE(viewed_at) AS active_date
        FROM product_views
    ),
    grouped AS (
        SELECT
            customer_id,
            active_date,
            DATE(active_date, '-' || (ROW_NUMBER() OVER (
                PARTITION BY customer_id ORDER BY active_date
            ) - 1) || ' days') AS grp
        FROM active_days
    ),
    streaks AS (
        SELECT
            customer_id,
            COUNT(*) AS streak_days,
            MIN(active_date) AS streak_start,
            MAX(active_date) AS streak_end
        FROM grouped
        GROUP BY customer_id, grp
        HAVING COUNT(*) >= 3
    )
    SELECT
        c.name AS customer_name,
        s.streak_days,
        s.streak_start,
        s.streak_end
    FROM streaks AS s
    JOIN customers AS c ON s.customer_id = c.id
    ORDER BY s.streak_days DESC, s.streak_start
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer_name | streak_days | streak_start | streak_end |
    |---|---|---|---|
    | 배춘자 | 46 | 2020-02-28 | 2020-04-13 |
    | 이영자 | 40 | 2016-01-09 | 2016-02-17 |
    | 김성민 | 39 | 2020-05-02 | 2020-06-09 |
    | 김병철 | 27 | 2020-02-28 | 2020-03-25 |
    | 홍옥순 | 26 | 2019-03-13 | 2019-04-07 |
    | 김민재 | 25 | 2016-03-05 | 2016-03-29 |
    | 이영자 | 25 | 2016-04-18 | 2016-05-12 |


---


### 6. 카테고리별 Top-N (그룹 내 순위) ★★★


각 카테고리에서 **리뷰 평점이 가장 높은 상품 2개**를 추출하세요.
리뷰 10건 이상인 상품만 대상으로 합니다. 동점이면 리뷰 수가 많은 상품이 우선합니다.

> **출제 빈도**: ★★★ (매우 높음) — Amazon, 네이버, 카카오

| category | product_name | avg_rating | review_count | rank |
|----------|-------------|-----------|-------------|------|


**힌트 1:** - `HAVING COUNT(*) >= 10`으로 리뷰 수 필터
- `ROW_NUMBER() OVER (PARTITION BY category ORDER BY avg_rating DESC, review_count DESC)`
- `WHERE rn <= 2`



??? success "정답"
    ```sql
    WITH product_ratings AS (
        SELECT
            cat.name AS category,
            p.name   AS product_name,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(*)                AS review_count
        FROM reviews AS r
        JOIN products   AS p   ON r.product_id  = p.id
        JOIN categories AS cat ON p.category_id = cat.id
        GROUP BY cat.name, p.id, p.name
        HAVING COUNT(*) >= 10
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (
                PARTITION BY category
                ORDER BY avg_rating DESC, review_count DESC
            ) AS rn
        FROM product_ratings
    )
    SELECT category, product_name, avg_rating, review_count, rn AS rank
    FROM ranked
    WHERE rn <= 2
    ORDER BY category, rn;
    ```


    **실행 결과** (총 70행 중 상위 7행)

    | category | product_name | avg_rating | review_count | rank |
    |---|---|---|---|---|
    | 2in1 | HP Pavilion x360 14 블랙 | 3.79 | 28 | 1 |
    | 2in1 | 레노버 IdeaPad Flex 5 | 3.75 | 12 | 2 |
    | AMD | MSI Radeon RX 9070 VENTUS 3X 화이트 | 4.08 | 40 | 1 |
    | AMD | AMD Ryzen 9 9900X | 4.08 | 13 | 2 |
    | AMD 소켓 | MSI MAG X870E TOMAHAWK WIFI 화이트 | 4.06 | 32 | 1 |
    | AMD 소켓 | ASRock B850M Pro RS 실버 | 4.04 | 25 | 2 |
    | DDR4 | Kingston FURY Beast DDR4 16GB 블랙 | 4.06 | 52 | 1 |


---


### 7. 전년 동기 대비 (YoY) 성장률 ★★★


**분기별 매출**의 전년 동기 대비 성장률(YoY %)을 구하세요.
2023~2025년 데이터를 대상으로 합니다.

> **출제 빈도**: ★★★ (매우 높음) — Google, Meta, 쿠팡

| year | quarter | revenue | prev_year_revenue | yoy_growth_pct |
|------|---------|---------|------------------|---------------|


**힌트 1:** - `LAG(revenue, 4) OVER (ORDER BY year, quarter)`로 전년 동분기 매출 참조 — 분기가 1~4이므로 4개 전이 전년 동기
- 또는 `LAG(revenue, 1) OVER (PARTITION BY quarter ORDER BY year)`



??? success "정답"
    ```sql
    WITH quarterly AS (
        SELECT
            CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER) AS year,
            CASE
                WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) <= 3 THEN 1
                WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) <= 6 THEN 2
                WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) <= 9 THEN 3
                ELSE 4
            END AS quarter,
            SUM(total_amount) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled')
          AND ordered_at >= '2023-01-01'
        GROUP BY 1, 2
    )
    SELECT
        year,
        quarter,
        CAST(revenue AS INTEGER) AS revenue,
        CAST(LAG(revenue) OVER (PARTITION BY quarter ORDER BY year) AS INTEGER) AS prev_year_revenue,
        ROUND(100.0 * (revenue - LAG(revenue) OVER (PARTITION BY quarter ORDER BY year))
            / LAG(revenue) OVER (PARTITION BY quarter ORDER BY year), 1) AS yoy_growth_pct
    FROM quarterly
    ORDER BY year, quarter;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | year | quarter | revenue | prev_year_revenue | yoy_growth_pct |
    |---|---|---|---|---|
    | 2023 | 1 | 1,112,502,647 | NULL | NULL |
    | 2023 | 2 | 1,075,865,258 | NULL | NULL |
    | 2023 | 3 | 1,162,362,566 | NULL | NULL |
    | 2023 | 4 | 1,464,300,253 | NULL | NULL |
    | 2024 | 1 | 1,263,575,536 | 1,112,502,647 | 13.60 |
    | 2024 | 2 | 1,306,918,979 | 1,075,865,258 | 21.50 |
    | 2024 | 3 | 1,340,721,817 | 1,162,362,566 | 15.30 |


---


### 8. 이동 평균 (Moving Average) ★★☆


2024년 **일별 매출의 7일 이동 평균**을 구하세요.
이동 평균은 당일 포함 직전 7일간의 평균입니다.

> **출제 빈도**: ★★☆ — Google, 네이버

| order_date | daily_revenue | ma_7d |
|-----------|-------------|------|


**힌트 1:** - `AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`
- `calendar`와 LEFT JOIN하여 주문이 없는 날도 0으로 포함시키기



??? success "정답"
    ```sql
    WITH daily AS (
        SELECT
            cal.date_key AS order_date,
            COALESCE(SUM(o.total_amount), 0) AS daily_revenue
        FROM calendar AS cal
        LEFT JOIN orders AS o
            ON DATE(o.ordered_at) = cal.date_key
           AND o.status NOT IN ('cancelled')
        WHERE cal.date_key BETWEEN '2024-01-01' AND '2024-12-31'
        GROUP BY cal.date_key
    )
    SELECT
        order_date,
        CAST(daily_revenue AS INTEGER) AS daily_revenue,
        CAST(AVG(daily_revenue) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS INTEGER) AS ma_7d
    FROM daily
    ORDER BY order_date;
    ```


    **실행 결과** (총 366행 중 상위 7행)

    | order_date | daily_revenue | ma_7d |
    |---|---|---|
    | 2024-01-01 | 7,732,372 | 7,732,372 |
    | 2024-01-02 | 14,807,975 | 11,270,173 |
    | 2024-01-03 | 2,825,828 | 8,455,391 |
    | 2024-01-04 | 4,332,900 | 7,424,768 |
    | 2024-01-05 | 8,083,504 | 7,556,515 |
    | 2024-01-06 | 9,182,200 | 7,827,463 |
    | 2024-01-07 | 23,522,036 | 10,069,545 |


---


### 9. 백분위수 (Percentile) ★★☆


고객별 총 구매금액이 **상위 10%, 25%, 50%(중위수), 75%, 90%** 경계에 해당하는 값을 구하세요.

> **출제 빈도**: ★★☆ — Amazon, Google

| percentile | threshold_amount |
|-----------|----------------|
| 10 | ... |
| 25 | ... |


**힌트 1:** - `NTILE(100) OVER (ORDER BY total_spent)`로 백분위 그룹 부여
- 각 백분위 경계값: `WHERE percentile_group IN (10, 25, 50, 75, 90)`에서 MAX 값



??? success "정답"
    ```sql
    WITH customer_spent AS (
        SELECT
            customer_id,
            SUM(total_amount) AS total_spent
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ),
    with_percentile AS (
        SELECT
            total_spent,
            NTILE(100) OVER (ORDER BY total_spent) AS pctl
        FROM customer_spent
    )
    SELECT
        pctl AS percentile,
        CAST(MAX(total_spent) AS INTEGER) AS threshold_amount
    FROM with_percentile
    WHERE pctl IN (10, 25, 50, 75, 90)
    GROUP BY pctl
    ORDER BY pctl;
    ```


    **실행 결과** (5행)

    | percentile | threshold_amount |
    |---|---|
    | 10 | 180,500 |
    | 25 | 1,183,200 |
    | 50 | 4,654,232 |
    | 75 | 13,607,591 |
    | 90 | 31,606,150 |


---


### 10. 전일 대비 변화율 + 7일 이동 변화율 ★★☆


2024년 12월의 일별 주문 수에 대해 **전일 대비 변화율(DoD %)**과
**7일 전 대비 변화율(WoW %)**을 동시에 구하세요.

> **출제 빈도**: ★★☆ — Meta, 쿠팡

| order_date | order_count | prev_day | dod_pct | prev_week | wow_pct |
|-----------|------------|---------|--------|----------|--------|


**힌트 1:** - `LAG(order_count, 1)` = 전일, `LAG(order_count, 7)` = 7일 전
- 변화율 = `(당일 - 이전) / 이전 * 100`
- `calendar` LEFT JOIN으로 빠진 날도 포함



??? success "정답"
    ```sql
    WITH daily AS (
        SELECT
            cal.date_key AS order_date,
            COALESCE(COUNT(o.id), 0) AS order_count
        FROM calendar AS cal
        LEFT JOIN orders AS o
            ON DATE(o.ordered_at) = cal.date_key
           AND o.status NOT IN ('cancelled')
        WHERE cal.date_key BETWEEN '2024-12-01' AND '2024-12-31'
        GROUP BY cal.date_key
    )
    SELECT
        order_date,
        order_count,
        LAG(order_count, 1) OVER (ORDER BY order_date) AS prev_day,
        ROUND(100.0 * (order_count - LAG(order_count, 1) OVER (ORDER BY order_date))
            / NULLIF(LAG(order_count, 1) OVER (ORDER BY order_date), 0), 1) AS dod_pct,
        LAG(order_count, 7) OVER (ORDER BY order_date) AS prev_week,
        ROUND(100.0 * (order_count - LAG(order_count, 7) OVER (ORDER BY order_date))
            / NULLIF(LAG(order_count, 7) OVER (ORDER BY order_date), 0), 1) AS wow_pct
    FROM daily
    ORDER BY order_date;
    ```


    **실행 결과** (총 31행 중 상위 7행)

    | order_date | order_count | prev_day | dod_pct | prev_week | wow_pct |
    |---|---|---|---|---|---|
    | 2024-12-01 | 17 | NULL | NULL | NULL | NULL |
    | 2024-12-02 | 14 | 17 | -17.60 | NULL | NULL |
    | 2024-12-03 | 15 | 14 | 7.10 | NULL | NULL |
    | 2024-12-04 | 14 | 15 | -6.70 | NULL | NULL |
    | 2024-12-05 | 9 | 14 | -35.70 | NULL | NULL |
    | 2024-12-06 | 14 | 9 | 55.60 | NULL | NULL |
    | 2024-12-07 | 15 | 14 | 7.10 | NULL | NULL |


---


### 11. 재귀 CTE: 조직도 트리 ★★★


`staff` 테이블의 `manager_id`를 이용하여 **전체 조직 계층 구조**를 출력하세요.
직급(depth), 상사 이름, 전체 경로(CEO > ... > 본인)를 포함합니다.

> **출제 빈도**: ★★★ (매우 높음) — Amazon, 카카오, 네이버

| name | department | role | depth | manager_name | path |
|------|-----------|------|-------|-------------|------|
| CEO이름 | management | admin | 0 | NULL | CEO이름 |
| ... | ... | ... | 1 | CEO이름 | CEO이름 > ... |


**힌트 1:** - Recursive CTE: `WHERE manager_id IS NULL`이 앵커(루트)
- 재귀 파트에서 `s.manager_id = tree.id`로 조인
- `path || ' > ' || s.name`으로 경로 누적



??? success "정답"
    ```sql
    WITH RECURSIVE org_tree AS (
        -- 앵커: 최상위 관리자 (manager_id IS NULL)
        SELECT
            s.id,
            s.name,
            s.department,
            s.role,
            0 AS depth,
            CAST(NULL AS TEXT) AS manager_name,
            s.name AS path
        FROM staff AS s
        WHERE s.manager_id IS NULL
    
        UNION ALL
    
        -- 재귀: 하위 직원
        SELECT
            s.id,
            s.name,
            s.department,
            s.role,
            t.depth + 1,
            t.name AS manager_name,
            t.path || ' > ' || s.name
        FROM staff AS s
        JOIN org_tree AS t ON s.manager_id = t.id
    )
    SELECT name, department, role, depth, manager_name, path
    FROM org_tree
    ORDER BY path;
    ```


    **실행 결과** (5행)

    | name | department | role | depth | manager_name | path |
    |---|---|---|---|---|---|
    | 한민재 | 경영 | admin | 0 | NULL | 한민재 |
    | 박경수 | 경영 | admin | 1 | 한민재 | 한민재 > 박경수 |
    | 권영희 | 마케팅 | manager | 2 | 박경수 | 한민재 > 박경수 > 권영희 |
    | 이준혁 | 영업 | manager | 1 | 한민재 | 한민재 > 이준혁 |
    | 장주원 | 경영 | admin | 1 | 한민재 | 한민재 > 장주원 |


---


### 12. 재귀 CTE: 날짜 시퀀스 생성 ★★☆


2024년 12월의 **모든 날짜를 재귀 CTE로 생성**하고,
각 날짜의 주문 수와 매출을 구하세요. (주문이 없는 날도 0으로 표시)

> **출제 빈도**: ★★☆ — Google (calendar 테이블 없는 환경에서)

| dt | order_count | revenue |
|----|-----------|---------|
| 2024-12-01 | ... | ... |


**힌트 1:** - 앵커: `SELECT '2024-12-01' AS dt`
- 재귀: `SELECT DATE(dt, '+1 day') FROM dates WHERE dt < '2024-12-31'`
- `LEFT JOIN orders`로 주문 데이터 결합



??? success "정답"
    ```sql
    WITH RECURSIVE dates AS (
        SELECT '2024-12-01' AS dt
        UNION ALL
        SELECT DATE(dt, '+1 day')
        FROM dates
        WHERE dt < '2024-12-31'
    )
    SELECT
        d.dt,
        COUNT(o.id) AS order_count,
        COALESCE(CAST(SUM(o.total_amount) AS INTEGER), 0) AS revenue
    FROM dates AS d
    LEFT JOIN orders AS o
        ON DATE(o.ordered_at) = d.dt
       AND o.status NOT IN ('cancelled')
    GROUP BY d.dt
    ORDER BY d.dt;
    ```


    **실행 결과** (총 31행 중 상위 7행)

    | dt | order_count | revenue |
    |---|---|---|
    | 2024-12-01 | 17 | 12,081,245 |
    | 2024-12-02 | 14 | 12,578,657 |
    | 2024-12-03 | 15 | 11,867,860 |
    | 2024-12-04 | 14 | 11,198,303 |
    | 2024-12-05 | 9 | 5,489,585 |
    | 2024-12-06 | 14 | 16,160,600 |
    | 2024-12-07 | 15 | 16,802,502 |


---


### 13. 코호트 분석 (가입월별 재구매) ★★★


고객의 **가입 월(cohort)** 기준으로, 가입 후 0~3개월 시점의 구매 고객 비율을 구하세요.
2024년 가입 고객 대상입니다.

> **출제 빈도**: ★★★ (매우 높음) — Meta, 쿠팡, 네이버

| cohort | size | m0_pct | m1_pct | m2_pct | m3_pct |
|--------|------|-------|-------|-------|-------|


**힌트 1:** - 코호트: `SUBSTR(created_at, 1, 7)`
- 월 오프셋: `(julianday(주문월-01) - julianday(가입월-01)) / 30`을 정수 변환
- `COUNT(DISTINCT CASE WHEN offset = N THEN customer_id END)` / 코호트 크기



??? success "정답"
    ```sql
    WITH cohort AS (
        SELECT
            id AS customer_id,
            SUBSTR(created_at, 1, 7) AS cohort_month
        FROM customers
        WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
    ),
    order_month AS (
        SELECT DISTINCT
            co.customer_id,
            co.cohort_month,
            CAST(
                (julianday(SUBSTR(o.ordered_at, 1, 7) || '-01')
               - julianday(co.cohort_month || '-01')) / 30
            AS INTEGER) AS month_offset
        FROM cohort AS co
        JOIN orders AS o ON co.customer_id = o.customer_id
        WHERE o.status NOT IN ('cancelled')
    )
    SELECT
        c.cohort_month AS cohort,
        COUNT(DISTINCT c.customer_id) AS size,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN om.month_offset = 0 THEN om.customer_id END)
            / COUNT(DISTINCT c.customer_id), 1) AS m0_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN om.month_offset = 1 THEN om.customer_id END)
            / COUNT(DISTINCT c.customer_id), 1) AS m1_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN om.month_offset = 2 THEN om.customer_id END)
            / COUNT(DISTINCT c.customer_id), 1) AS m2_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN om.month_offset = 3 THEN om.customer_id END)
            / COUNT(DISTINCT c.customer_id), 1) AS m3_pct
    FROM cohort AS c
    LEFT JOIN order_month AS om ON c.customer_id = om.customer_id
        AND c.cohort_month = om.cohort_month
    GROUP BY c.cohort_month
    ORDER BY c.cohort_month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | cohort | size | m0_pct | m1_pct | m2_pct | m3_pct |
    |---|---|---|---|---|---|
    | 2024-01 | 52 | 11.50 | 5.80 | 9.60 | 7.70 |
    | 2024-02 | 48 | 18.80 | 0.0 | 6.30 | 10.40 |
    | 2024-03 | 71 | 16.90 | 14.10 | 15.50 | 2.80 |
    | 2024-04 | 53 | 5.70 | 7.50 | 7.50 | 3.80 |
    | 2024-05 | 43 | 9.30 | 9.30 | 16.30 | 4.70 |
    | 2024-06 | 68 | 10.30 | 5.90 | 5.90 | 8.80 |
    | 2024-07 | 62 | 8.10 | 9.70 | 11.30 | 11.30 |


---


### 14. 카테고리 계층 집계 (Recursive + GROUP BY) ★★☆


`categories` 트리에서 **대분류별 총 매출**을 구하세요.
하위 카테고리(중/소)의 매출을 모두 상위(대)로 롤업합니다.

> **출제 빈도**: ★★☆ — Amazon, 카카오

| top_category | sub_category_count | product_count | total_revenue |
|-------------|-------------------|-------------|-------------|


**힌트 1:** - Recursive CTE로 각 카테고리의 루트(depth=0) 조상 찾기
- 재귀 탐색 후 루트 기준으로 `GROUP BY`



??? success "정답"
    ```sql
    WITH RECURSIVE cat_tree AS (
        SELECT id, id AS root_id, name AS root_name, depth
        FROM categories
        WHERE parent_id IS NULL
    
        UNION ALL
    
        SELECT c.id, ct.root_id, ct.root_name, c.depth
        FROM categories AS c
        JOIN cat_tree AS ct ON c.parent_id = ct.id
    )
    SELECT
        ct.root_name AS top_category,
        COUNT(DISTINCT CASE WHEN ct.depth > 0 THEN ct.id END) AS sub_category_count,
        COUNT(DISTINCT p.id) AS product_count,
        COALESCE(CAST(SUM(oi.quantity * oi.unit_price) AS INTEGER), 0) AS total_revenue
    FROM cat_tree AS ct
    LEFT JOIN products AS p ON p.category_id = ct.id
    LEFT JOIN order_items AS oi ON oi.product_id = p.id
    LEFT JOIN orders AS o ON oi.order_id = o.id
        AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    WHERE ct.root_id = ct.root_id
    GROUP BY ct.root_id, ct.root_name
    ORDER BY total_revenue DESC;
    ```


    **실행 결과** (총 18행 중 상위 7행)

    | top_category | sub_category_count | product_count | total_revenue |
    |---|---|---|---|
    | 노트북 | 4 | 29 | 10,144,187,100 |
    | 그래픽카드 | 2 | 15 | 5,608,961,100 |
    | 모니터 | 3 | 22 | 4,753,611,200 |
    | 메인보드 | 2 | 23 | 3,255,592,700 |
    | CPU | 2 | 7 | 1,877,389,800 |
    | 스피커/헤드셋 | 0 | 12 | 1,561,393,600 |
    | 저장장치 | 3 | 15 | 1,524,801,600 |


---


### 15. Self-Join: 상사보다 급여(매출 처리 건수)가 많은 직원 ★★★


각 직원이 처리한 주문 건수를 구하고, **자신의 상사보다 많은 주문을 처리한** 직원을 찾으세요.
(orders.staff_id 기준)

> **출제 빈도**: ★★★ (매우 높음) — LeetCode #181 변형, 카카오

| staff_name | department | handled_orders | manager_name | manager_orders |
|-----------|-----------|---------------|-------------|---------------|


**힌트 1:** - `staff AS s JOIN staff AS m ON s.manager_id = m.id` (Self-Join)
- 각 직원의 주문 건수: `orders.staff_id`로 카운트
- `WHERE s_count > m_count`



??? success "정답"
    ```sql
    WITH staff_orders AS (
        SELECT
            s.id,
            s.name,
            s.department,
            s.manager_id,
            COUNT(o.id) AS handled_orders
        FROM staff AS s
        LEFT JOIN orders AS o ON s.id = o.staff_id
        GROUP BY s.id, s.name, s.department, s.manager_id
    )
    SELECT
        emp.name       AS staff_name,
        emp.department,
        emp.handled_orders,
        mgr.name       AS manager_name,
        mgr.handled_orders AS manager_orders
    FROM staff_orders AS emp
    JOIN staff_orders AS mgr ON emp.manager_id = mgr.id
    WHERE emp.handled_orders > mgr.handled_orders
    ORDER BY emp.handled_orders DESC;
    ```


---


### 16. 다단계 분석: 할인 효과 측정 ★★☆


쿠폰을 사용한 고객과 미사용 고객을 비교하여 다음을 구하세요:
(1) 그룹별 평균 주문 금액, (2) 재구매율, (3) 평균 리뷰 평점.

> **출제 빈도**: ★★☆ — 쿠팡, 네이버

| segment | customer_count | avg_order_value | repeat_rate_pct | avg_rating |
|---------|--------------|----------------|----------------|-----------|


**힌트 1:** - 쿠폰 사용 여부: `coupon_usage` 존재 여부로 세그먼트 분류
- 재구매율: 2건 이상 주문한 고객 / 전체 고객
- 3개 테이블(orders, coupon_usage, reviews)을 CTE로 각각 집계 후 합치기



??? success "정답"
    ```sql
    WITH coupon_customers AS (
        SELECT DISTINCT customer_id FROM coupon_usage
    ),
    customer_segment AS (
        SELECT
            c.id AS customer_id,
            CASE WHEN cc.customer_id IS NOT NULL THEN 'Coupon User' ELSE 'Non-Coupon' END AS segment
        FROM customers AS c
        LEFT JOIN coupon_customers AS cc ON c.id = cc.customer_id
        WHERE c.is_active = 1
    ),
    order_stats AS (
        SELECT
            cs.segment,
            cs.customer_id,
            COUNT(o.id) AS order_count,
            AVG(o.total_amount) AS avg_order_value
        FROM customer_segment AS cs
        LEFT JOIN orders AS o ON cs.customer_id = o.customer_id
            AND o.status NOT IN ('cancelled')
        GROUP BY cs.segment, cs.customer_id
    ),
    review_stats AS (
        SELECT
            cs.segment,
            ROUND(AVG(r.rating), 2) AS avg_rating
        FROM customer_segment AS cs
        JOIN reviews AS r ON cs.customer_id = r.customer_id
        GROUP BY cs.segment
    )
    SELECT
        os.segment,
        COUNT(DISTINCT os.customer_id) AS customer_count,
        ROUND(AVG(os.avg_order_value), 0) AS avg_order_value,
        ROUND(100.0 * SUM(CASE WHEN os.order_count >= 2 THEN 1 ELSE 0 END)
            / COUNT(DISTINCT os.customer_id), 1) AS repeat_rate_pct,
        rs.avg_rating
    FROM order_stats AS os
    LEFT JOIN review_stats AS rs ON os.segment = rs.segment
    GROUP BY os.segment, rs.avg_rating
    ORDER BY os.segment;
    ```


    **실행 결과** (2행)

    | segment | customer_count | avg_order_value | repeat_rate_pct | avg_rating |
    |---|---|---|---|---|
    | Coupon User | 888 | 1,030,689.00 | 97.20 | 3.89 |
    | Non-Coupon | 2772 | 843,056.00 | 52.50 | 3.93 |


---


### 17. 데이터 품질 체크: NULL/이상치 탐지 ★★☆


다음 데이터 품질 문제를 한 쿼리로 보고하세요:
(1) 주문 금액이 0 이하, (2) 배송일 < 주문일, (3) 리뷰 평점 범위 밖, (4) 미래 날짜 주문.

> **출제 빈도**: ★★☆ — Amazon (Data Engineer), 카카오

| issue_type | table_name | record_count | sample_ids |
|-----------|-----------|-------------|-----------|


**힌트 1:** - `UNION ALL`로 각 품질 검사 결과를 합치기
- `GROUP_CONCAT(id, ',')`으로 샘플 ID 나열
- 미래 날짜: `ordered_at > '2025-12-31'`



??? success "정답"
    ```sql
    SELECT 'Zero/Negative Amount' AS issue_type,
           'orders' AS table_name,
           COUNT(*) AS record_count,
           GROUP_CONCAT(id, ',') AS sample_ids
    FROM orders
    WHERE total_amount <= 0
    
    UNION ALL
    
    SELECT 'Delivery Before Shipment',
           'shipping',
           COUNT(*),
           GROUP_CONCAT(id, ',')
    FROM shipping
    WHERE delivered_at IS NOT NULL
      AND shipped_at IS NOT NULL
      AND delivered_at < shipped_at
    
    UNION ALL
    
    SELECT 'Rating Out of Range',
           'reviews',
           COUNT(*),
           GROUP_CONCAT(id, ',')
    FROM reviews
    WHERE rating < 1 OR rating > 5
    
    UNION ALL
    
    SELECT 'Future Order Date',
           'orders',
           COUNT(*),
           GROUP_CONCAT(id, ',')
    FROM orders
    WHERE ordered_at > DATE('now', '+1 day');
    ```


    **실행 결과** (4행)

    | issue_type | table_name | record_count | sample_ids |
    |---|---|---|---|
    | Zero/Negative Amount | orders | 0 | NULL |
    | Delivery Before Shipment | shipping | 0 | NULL |
    | Rating Out of Range | reviews | 0 | NULL |
    | Future Order Date | orders | 0 | NULL |


---


### 18. 시계열 이상 탐지: 3-sigma 규칙 ★☆☆


일별 매출의 **평균 +/- 3 표준편차** 범위를 벗어나는 이상치(outlier) 날짜를 찾으세요.

> **출제 빈도**: ★☆☆ — Google (Data Science)

| order_date | daily_revenue | avg_revenue | stddev | z_score |
|-----------|-------------|-----------|-------|--------|


**힌트 1:** - 표준편차: SQLite에서 직접 지원하지 않으므로 수동 계산
- `SQRT(AVG(x*x) - AVG(x)*AVG(x))` = 모표준편차
- Z-score = `(값 - 평균) / 표준편차`, `ABS(z) > 3`이면 이상치



??? success "정답"
    ```sql
    WITH daily AS (
        SELECT
            DATE(ordered_at) AS order_date,
            SUM(total_amount) AS daily_revenue
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY DATE(ordered_at)
    ),
    stats AS (
        SELECT
            AVG(daily_revenue) AS avg_rev,
            SQRT(AVG(daily_revenue * daily_revenue) - AVG(daily_revenue) * AVG(daily_revenue)) AS stddev_rev
        FROM daily
    )
    SELECT
        d.order_date,
        CAST(d.daily_revenue AS INTEGER) AS daily_revenue,
        CAST(s.avg_rev AS INTEGER) AS avg_revenue,
        CAST(s.stddev_rev AS INTEGER) AS stddev,
        ROUND((d.daily_revenue - s.avg_rev) / s.stddev_rev, 2) AS z_score
    FROM daily AS d
    CROSS JOIN stats AS s
    WHERE ABS((d.daily_revenue - s.avg_rev) / s.stddev_rev) > 3
    ORDER BY ABS((d.daily_revenue - s.avg_rev) / s.stddev_rev) DESC;
    ```


    **실행 결과** (총 48행 중 상위 7행)

    | order_date | daily_revenue | avg_revenue | stddev | z_score |
    |---|---|---|---|---|
    | 2025-12-18 | 62,329,008 | 10,077,964 | 8,237,014 | 6.34 |
    | 2025-03-05 | 62,266,624 | 10,077,964 | 8,237,014 | 6.34 |
    | 2020-11-21 | 60,470,134 | 10,077,964 | 8,237,014 | 6.12 |
    | 2025-12-21 | 56,392,485 | 10,077,964 | 8,237,014 | 5.62 |
    | 2020-02-09 | 51,620,600 | 10,077,964 | 8,237,014 | 5.04 |
    | 2025-05-06 | 51,138,521 | 10,077,964 | 8,237,014 | 4.98 |
    | 2022-01-06 | 50,993,500 | 10,077,964 | 8,237,014 | 4.97 |


---


### 19. 복합 분석: RFM 세그먼테이션 ★★★


고객을 **RFM(Recency, Frequency, Monetary)** 기준으로 세그먼트하세요.
각 지표를 1~5 등급으로 나누고, 세그먼트별 고객 수와 평균 매출을 구합니다.

> **출제 빈도**: ★★★ (매우 높음) — 쿠팡, 네이버, Amazon

| rfm_segment | r_score | f_score | m_score | customer_count | avg_monetary |
|------------|--------|--------|--------|--------------|------------|
| Champions | 5 | 5 | 5 | ... | ... |


**힌트 1:** - Recency: 마지막 주문으로부터 경과일 → `NTILE(5)` (최근일수록 높은 점수)
- Frequency: 주문 횟수 → `NTILE(5)`
- Monetary: 총 구매금액 → `NTILE(5)`
- 세그먼트 분류: R+F+M 합이 13~15=Champions, 10~12=Loyal, 7~9=Potential, 4~6=AtRisk, 3=Lost



??? success "정답"
    ```sql
    WITH rfm_raw AS (
        SELECT
            customer_id,
            CAST(julianday('2025-06-30') - julianday(MAX(ordered_at)) AS INTEGER) AS recency,
            COUNT(*) AS frequency,
            CAST(SUM(total_amount) AS INTEGER) AS monetary
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ),
    rfm_scored AS (
        SELECT
            customer_id,
            recency, frequency, monetary,
            NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,
            NTILE(5) OVER (ORDER BY frequency ASC)  AS f_score,
            NTILE(5) OVER (ORDER BY monetary ASC)   AS m_score
        FROM rfm_raw
    ),
    rfm_segmented AS (
        SELECT *,
            r_score + f_score + m_score AS rfm_total,
            CASE
                WHEN r_score + f_score + m_score >= 13 THEN 'Champions'
                WHEN r_score + f_score + m_score >= 10 THEN 'Loyal'
                WHEN r_score + f_score + m_score >= 7  THEN 'Potential'
                WHEN r_score + f_score + m_score >= 4  THEN 'At Risk'
                ELSE 'Lost'
            END AS rfm_segment
        FROM rfm_scored
    )
    SELECT
        rfm_segment,
        ROUND(AVG(r_score), 1) AS r_score,
        ROUND(AVG(f_score), 1) AS f_score,
        ROUND(AVG(m_score), 1) AS m_score,
        COUNT(*) AS customer_count,
        CAST(AVG(monetary) AS INTEGER) AS avg_monetary
    FROM rfm_segmented
    GROUP BY rfm_segment
    ORDER BY AVG(rfm_total) DESC;
    ```


    **실행 결과** (5행)

    | rfm_segment | r_score | f_score | m_score | customer_count | avg_monetary |
    |---|---|---|---|---|---|
    | Champions | 4.40 | 4.80 | 4.80 | 579 | 42,854,633 |
    | Loyal | 3.30 | 3.80 | 3.80 | 655 | 11,437,042 |
    | Potential | 2.80 | 2.60 | 2.60 | 788 | 4,077,164 |
    | At Risk | 2.10 | 1.50 | 1.50 | 653 | 1,071,866 |
    | Lost | 1.00 | 1.00 | 1.00 | 134 | 175,595 |


---


### 20. 종합 시나리오: 마케팅 캠페인 효과 분석 ★★★


2024년 진행된 프로모션별로 다음을 분석하세요:
(1) 참여 고객 수, (2) 프로모션 기간 매출 vs 직전 동일 기간 매출(증분 효과),
(3) 프로모션 종료 후 30일간 재구매율, (4) 고객 획득 비용(할인 총액/신규 고객 수).

> **출제 빈도**: ★★★ (매우 높음) — 쿠팡, 네이버, Meta (종합 문제)

| promo_name | promo_type | participants | promo_revenue | pre_revenue | lift_pct | post_repurchase_pct | cac |
|-----------|-----------|------------|-------------|-----------|---------|-------------------|-----|


**힌트 1:** - `promotions`의 `started_at`/`ended_at`으로 기간 설정
- 직전 동일 기간: `DATE(started_at, '-' || (julianday(ended_at)-julianday(started_at)) || ' days')`
- 신규 고객: 프로모션 기간 중 첫 주문인 고객
- CTE 4~5단계로 분리



??? success "정답"
    ```sql
    WITH promo_periods AS (
        SELECT
            pr.id AS promo_id,
            pr.name AS promo_name,
            pr.type AS promo_type,
            pr.started_at,
            pr.ended_at,
            CAST(julianday(pr.ended_at) - julianday(pr.started_at) AS INTEGER) AS duration_days
        FROM promotions AS pr
        WHERE pr.started_at >= '2024-01-01' AND pr.started_at < '2025-01-01'
    ),
    promo_orders AS (
        SELECT
            pp.promo_id, pp.promo_name, pp.promo_type,
            pp.started_at, pp.ended_at, pp.duration_days,
            o.id AS order_id,
            o.customer_id,
            o.total_amount,
            o.discount_amount
        FROM promo_periods AS pp
        JOIN orders AS o
            ON o.ordered_at BETWEEN pp.started_at AND pp.ended_at
           AND o.status NOT IN ('cancelled')
    ),
    pre_period_revenue AS (
        SELECT
            pp.promo_id,
            COALESCE(SUM(o.total_amount), 0) AS pre_revenue
        FROM promo_periods AS pp
        LEFT JOIN orders AS o
            ON o.ordered_at BETWEEN DATE(pp.started_at, '-' || pp.duration_days || ' days')
                                AND DATE(pp.started_at, '-1 day')
           AND o.status NOT IN ('cancelled')
        GROUP BY pp.promo_id
    ),
    post_repurchase AS (
        SELECT
            po.promo_id,
            COUNT(DISTINCT CASE
                WHEN EXISTS (
                    SELECT 1 FROM orders o2
                    WHERE o2.customer_id = po.customer_id
                      AND o2.ordered_at > po.ended_at
                      AND o2.ordered_at <= DATE(po.ended_at, '+30 days')
                      AND o2.status NOT IN ('cancelled')
                )
                THEN po.customer_id
            END) AS repurchase_customers,
            COUNT(DISTINCT po.customer_id) AS total_customers
        FROM promo_orders AS po
        GROUP BY po.promo_id
    )
    SELECT
        po.promo_name,
        po.promo_type,
        COUNT(DISTINCT po.customer_id) AS participants,
        CAST(SUM(po.total_amount) AS INTEGER) AS promo_revenue,
        CAST(pr.pre_revenue AS INTEGER) AS pre_revenue,
        ROUND(100.0 * (SUM(po.total_amount) - pr.pre_revenue)
            / NULLIF(pr.pre_revenue, 0), 1) AS lift_pct,
        ROUND(100.0 * rp.repurchase_customers / NULLIF(rp.total_customers, 0), 1) AS post_repurchase_pct,
        CAST(SUM(po.discount_amount) / NULLIF(
            COUNT(DISTINCT CASE
                WHEN NOT EXISTS (
                    SELECT 1 FROM orders o3
                    WHERE o3.customer_id = po.customer_id
                      AND o3.ordered_at < po.started_at
                      AND o3.status NOT IN ('cancelled')
                )
                THEN po.customer_id
            END), 0) AS INTEGER) AS cac
    FROM promo_orders AS po
    JOIN pre_period_revenue AS pr ON po.promo_id = pr.promo_id
    JOIN post_repurchase AS rp ON po.promo_id = rp.promo_id
    GROUP BY po.promo_id, po.promo_name, po.promo_type,
             pr.pre_revenue, rp.repurchase_customers, rp.total_customers
    ORDER BY promo_revenue DESC;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | promo_name | promo_type | participants | promo_revenue | pre_revenue | lift_pct | post_repurchase_pct | cac |
    |---|---|---|---|---|---|---|---|
    | 신학기 노트북 특가 2024 | category | 317 | 359,327,629 | 356,716,760 | 0.7 | 32.50 | 74,055 |
    | 추석 선물 세일 2024 | seasonal | 171 | 231,954,685 | 142,169,738 | 63.20 | 36.80 | 155,025 |
    | 봄맞이 세일 2024 | seasonal | 226 | 212,486,725 | 217,467,681 | -2.30 | 35.80 | 78,385 |
    | 연말 감사 세일 2024 | seasonal | 186 | 192,873,636 | 188,843,699 | 2.10 | 31.20 | 121,744 |
    | 여름 쿨링 페스티벌 2024 | category | 168 | 191,169,469 | 178,340,805 | 7.20 | 26.20 | 120,630 |
    | 프린터 특가 2024 | category | 121 | 147,372,860 | 158,556,326 | -7.10 | 30.60 | 120,300 |
    | 새해 특가 세일 2024 | seasonal | 68 | 70,486,815 | 54,386,890 | 29.60 | 25.00 | 148,566 |


---
