# 매출 분석

!!! info "사용 테이블"

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `categories` — 카테고리 (부모-자식 계층)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `payments` — 결제 (방법, 금액, 상태)  



!!! abstract "학습 범위"

    `CTE`, `Window Functions`, `Multiple JOIN`, `Aggregation`, `YoY Growth`, `Moving Average`, `ABC Analysis`, `Cohort`



### 1. 월별 매출 추이 (최근 3년)


2022~2024년 월별 매출, 주문 수, 평균 주문 금액을 구하세요.


**힌트 1:** - `SUBSTR(ordered_at, 1, 7)`로 연-월 추출
- `SUM(total_amount)`, `COUNT(*)`, `AVG(total_amount)`



??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7)   AS year_month,
        COUNT(*)                   AS order_count,
        ROUND(SUM(total_amount))   AS revenue,
        ROUND(AVG(total_amount))   AS avg_order_value
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
      AND ordered_at >= '2022-01-01'
      AND ordered_at < '2025-01-01'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY year_month;
    ```


    **실행 결과** (총 36행 중 상위 7행)

    | year_month | order_count | revenue | avg_order_value |
    |---|---|---|---|
    | 2022-01 | 340 | 387,797,263.00 | 1,140,580.00 |
    | 2022-02 | 343 | 349,125,148.00 | 1,017,858.00 |
    | 2022-03 | 397 | 392,750,666.00 | 989,296.00 |
    | 2022-04 | 337 | 313,546,744.00 | 930,406.00 |
    | 2022-05 | 448 | 445,361,972.00 | 994,112.00 |
    | 2022-06 | 348 | 353,057,024.00 | 1,014,532.00 |
    | 2022-07 | 386 | 418,258,615.00 | 1,083,572.00 |


---


### 2. 카테고리별 매출 비중


2024년 대분류 카테고리별 매출과 전체 대비 비중(%)을 구하세요.


**힌트 1:** - `categories.depth = 0`이 대분류
- 소분류 → 중분류 → 대분류 경로: `categories` 자기 참조를 두 번 JOIN
- 또는 depth=0인 최상위 카테고리를 찾는 서브쿼리 사용



??? success "정답"
    ```sql
    WITH category_revenue AS (
        SELECT
            COALESCE(top_cat.name, mid_cat.name, cat.name) AS top_category,
            SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        LEFT JOIN categories AS mid_cat ON cat.parent_id = mid_cat.id
        LEFT JOIN categories AS top_cat ON mid_cat.parent_id = top_cat.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY COALESCE(top_cat.name, mid_cat.name, cat.name)
    )
    SELECT
        top_category,
        ROUND(revenue) AS revenue,
        ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS revenue_pct
    FROM category_revenue
    ORDER BY revenue DESC;
    ```


    **실행 결과** (총 18행 중 상위 7행)

    | top_category | revenue | revenue_pct |
    |---|---|---|
    | 노트북 | 1,395,635,900.00 | 27.00 |
    | 모니터 | 727,065,300.00 | 14.10 |
    | 그래픽카드 | 713,579,800.00 | 13.80 |
    | 메인보드 | 398,988,900.00 | 7.70 |
    | 스피커/헤드셋 | 232,144,800.00 | 4.50 |
    | 저장장치 | 205,861,200.00 | 4.00 |
    | 메모리(RAM) | 200,423,600.00 | 3.90 |


---


### 3. 상위 20명 고객 매출 순위


전체 기간에서 총 구매 금액 상위 20명의 고객 정보를 표시하세요.
고객명, 등급, 주문 횟수, 총 구매 금액, 순위를 포함합니다.


**힌트 1:** - `RANK()` 또는 `ROW_NUMBER()` 윈도우 함수 사용
- `customers` + `orders` JOIN



??? success "정답"
    ```sql
    SELECT
        RANK() OVER (ORDER BY SUM(o.total_amount) DESC) AS ranking,
        c.name          AS customer_name,
        c.grade,
        COUNT(*)        AS order_count,
        ROUND(SUM(o.total_amount)) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | ranking | customer_name | grade | order_count | total_spent |
    |---|---|---|---|---|
    | 1 | 박정수 | VIP | 303 | 403,448,758.00 |
    | 2 | 김병철 | VIP | 342 | 366,385,931.00 |
    | 3 | 강명자 | VIP | 249 | 253,180,338.00 |
    | 4 | 정유진 | VIP | 223 | 244,604,910.00 |
    | 5 | 이미정 | VIP | 219 | 235,775,349.00 |
    | 6 | 김성민 | VIP | 230 | 234,708,853.00 |
    | 7 | 이영자 | VIP | 275 | 230,165,991.00 |


---


### 4. 요일별 매출 패턴


전체 주문 데이터에서 요일별(월~일) 평균 주문 수와 평균 매출을 구하세요.
어떤 요일에 매출이 가장 높은지 확인합니다.


**힌트 1:** - SQLite: `strftime('%w', ordered_at)` → 0(일)~6(토)
- CASE문으로 요일명 변환
- 먼저 일별 매출을 구한 뒤, 요일별로 평균



??? success "정답"
    ```sql
    WITH daily_stats AS (
        SELECT
            DATE(ordered_at) AS order_date,
            CAST(strftime('%w', ordered_at) AS INTEGER) AS dow,
            COUNT(*)               AS order_count,
            SUM(total_amount)      AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY DATE(ordered_at)
    )
    SELECT
        CASE dow
            WHEN 0 THEN '일요일'
            WHEN 1 THEN '월요일'
            WHEN 2 THEN '화요일'
            WHEN 3 THEN '수요일'
            WHEN 4 THEN '목요일'
            WHEN 5 THEN '금요일'
            WHEN 6 THEN '토요일'
        END AS day_of_week,
        ROUND(AVG(order_count)) AS avg_daily_orders,
        ROUND(AVG(revenue))     AS avg_daily_revenue
    FROM daily_stats
    GROUP BY dow
    ORDER BY dow;
    ```


    **실행 결과** (7행)

    | day_of_week | avg_daily_orders | avg_daily_revenue |
    |---|---|---|
    | 일요일 | 11.00 | 10,702,305.00 |
    | 월요일 | 11.00 | 10,470,017.00 |
    | 화요일 | 9.00 | 9,434,724.00 |
    | 수요일 | 9.00 | 8,818,457.00 |
    | 목요일 | 9.00 | 8,818,498.00 |
    | 금요일 | 9.00 | 9,178,156.00 |
    | 토요일 | 11.00 | 10,550,779.00 |


---


### 5. 분기별 매출과 전분기 대비 성장률


2022~2024년 분기별 매출과 전분기 대비 성장률(%)을 구하세요.


**힌트 1:** - 분기: `(CAST(SUBSTR(ordered_at,6,2) AS INTEGER) + 2) / 3`
- `LAG(revenue, 1)` 윈도우 함수로 전분기 매출 참조
- 성장률 = (당분기 - 전분기) / 전분기 * 100



??? success "정답"
    ```sql
    WITH quarterly AS (
        SELECT
            SUBSTR(ordered_at, 1, 4) AS year,
            'Q' || ((CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3) AS quarter,
            SUBSTR(ordered_at, 1, 4) || '-Q' || ((CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3) AS yq,
            ROUND(SUM(total_amount)) AS revenue,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2022-01-01' AND ordered_at < '2025-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 4),
                 (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3
    )
    SELECT
        yq,
        revenue,
        order_count,
        LAG(revenue, 1) OVER (ORDER BY yq) AS prev_quarter_revenue,
        ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY yq))
            / LAG(revenue, 1) OVER (ORDER BY yq), 1) AS qoq_growth_pct
    FROM quarterly
    ORDER BY yq;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | yq | revenue | order_count | prev_quarter_revenue | qoq_growth_pct |
    |---|---|---|---|---|
    | 2022-Q1 | 1,129,673,077.00 | 1080 | NULL | NULL |
    | 2022-Q2 | 1,111,965,740.00 | 1133 | 1,129,673,077.00 | -1.60 |
    | 2022-Q3 | 1,312,284,718.00 | 1246 | 1,111,965,740.00 | 18.00 |
    | 2022-Q4 | 1,271,192,508.00 | 1359 | 1,312,284,718.00 | -3.10 |
    | 2023-Q1 | 1,075,250,589.00 | 1083 | 1,271,192,508.00 | -15.40 |
    | 2023-Q2 | 1,026,296,754.00 | 1102 | 1,075,250,589.00 | -4.60 |
    | 2023-Q3 | 1,127,278,823.00 | 1094 | 1,026,296,754.00 | 9.80 |


---


### 6. 결제 수단별 매출 비중 추이


2024년 월별로 각 결제 수단(card, bank_transfer, kakao_pay 등)의 매출 비중(%)을 구하세요.


**힌트 1:** - `payments.method`로 결제 수단 구분
- 윈도우 함수 `SUM(revenue) OVER (PARTITION BY year_month)`으로 월 전체 매출
- 비중 = 결제 수단별 매출 / 월 전체 매출 * 100



??? success "정답"
    ```sql
    WITH monthly_method AS (
        SELECT
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            pm.method,
            ROUND(SUM(pm.amount)) AS revenue
        FROM payments AS pm
        INNER JOIN orders AS o ON pm.order_id = o.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
          AND pm.status = 'paid'
        GROUP BY SUBSTR(o.ordered_at, 1, 7), pm.method
    )
    SELECT
        year_month,
        method,
        revenue,
        ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY year_month), 1) AS method_pct
    FROM monthly_method
    ORDER BY year_month, revenue DESC;
    ```


---


### 7. 카테고리별 상위 3개 상품 (Top-N per Group)


2024년 각 대분류 카테고리에서 매출 상위 3개 상품을 선발하세요.


**힌트 1:** - CTE에서 카테고리별 상품 매출 집계
- `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)` 순위
- 외부 쿼리에서 `WHERE rn <= 3` 필터



??? success "정답"
    ```sql
    WITH product_sales AS (
        SELECT
            COALESCE(top_cat.name, mid_cat.name, cat.name) AS top_category,
            p.name AS product_name,
            SUM(oi.quantity)                        AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        LEFT JOIN categories AS mid_cat ON cat.parent_id = mid_cat.id
        LEFT JOIN categories AS top_cat ON mid_cat.parent_id = top_cat.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY COALESCE(top_cat.name, mid_cat.name, cat.name), p.name
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY top_category ORDER BY revenue DESC) AS rn
        FROM product_sales
    )
    SELECT top_category, rn AS rank, product_name, units_sold, revenue
    FROM ranked
    WHERE rn <= 3
    ORDER BY top_category, rn;
    ```


    **실행 결과** (총 53행 중 상위 7행)

    | top_category | rank | product_name | units_sold | revenue |
    |---|---|---|---|---|
    | CPU | 1 | AMD Ryzen 9 9900X | 239 | 80,232,300.00 |
    | CPU | 2 | Intel Core Ultra 7 265K 화이트 | 386 | 65,697,200.00 |
    | UPS/전원 | 1 | CyberPower OR1500LCDRT2U 블랙 | 46 | 11,633,400.00 |
    | UPS/전원 | 2 | APC Back-UPS Pro Gaming BGM1500B 블랙 | 21 | 10,842,300.00 |
    | UPS/전원 | 3 | CyberPower BRG1500AVRLCD 실버 | 13 | 6,605,300.00 |
    | 그래픽카드 | 1 | ASUS Dual RTX 4060 Ti 블랙 | 40 | 106,992,000.00 |
    | 그래픽카드 | 2 | ASUS Dual RTX 5070 Ti 실버 | 106 | 104,558,400.00 |


---


### 8. 전년 동월 대비(YoY) 매출 성장률


2023~2024년 각 월의 매출과 전년 동월 대비 성장률(%)을 구하세요.


**힌트 1:** - `LAG(revenue, 12)` — 12개월 전 매출 참조
- 또는 CTE에서 연도+월 분리 후, 같은 월의 전년도를 SELF JOIN



??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 4) AS year,
            SUBSTR(ordered_at, 6, 2) AS month,
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount)) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2022-01-01' AND ordered_at < '2025-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        cur.year_month,
        cur.revenue                AS current_revenue,
        prev.revenue               AS prev_year_revenue,
        ROUND(100.0 * (cur.revenue - prev.revenue) / prev.revenue, 1) AS yoy_growth_pct
    FROM monthly AS cur
    INNER JOIN monthly AS prev
        ON cur.month = prev.month
        AND CAST(cur.year AS INTEGER) = CAST(prev.year AS INTEGER) + 1
    WHERE cur.year IN ('2023', '2024')
    ORDER BY cur.year_month;
    ```


    **실행 결과** (총 24행 중 상위 7행)

    | year_month | current_revenue | prev_year_revenue | yoy_growth_pct |
    |---|---|---|---|
    | 2023-01 | 270,083,587.00 | 387,797,263.00 | -30.40 |
    | 2023-02 | 327,431,648.00 | 349,125,148.00 | -6.20 |
    | 2023-03 | 477,735,354.00 | 392,750,666.00 | 21.60 |
    | 2023-04 | 396,849,049.00 | 313,546,744.00 | 26.60 |
    | 2023-05 | 349,749,072.00 | 445,361,972.00 | -21.50 |
    | 2023-06 | 279,698,633.00 | 353,057,024.00 | -20.80 |
    | 2023-07 | 312,983,148.00 | 418,258,615.00 | -25.20 |


---


### 9. 이동 평균(Moving Average) — 3개월 이동 평균 매출


월별 매출의 3개월 이동 평균을 구하세요.
이동 평균은 추세를 파악할 때 계절적 변동을 완화해줍니다.


**힌트 1:** - `AVG(revenue) OVER (ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`
- 처음 2개월은 데이터가 부족하므로 이동 평균이 정확하지 않을 수 있음



??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount)) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2023-01-01' AND ordered_at < '2025-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        )) AS moving_avg_3m,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        )) AS moving_avg_6m
    FROM monthly
    ORDER BY year_month;
    ```


    **실행 결과** (총 24행 중 상위 7행)

    | year_month | revenue | moving_avg_3m | moving_avg_6m |
    |---|---|---|---|
    | 2023-01 | 270,083,587.00 | 270,083,587.00 | 270,083,587.00 |
    | 2023-02 | 327,431,648.00 | 298,757,618.00 | 298,757,618.00 |
    | 2023-03 | 477,735,354.00 | 358,416,863.00 | 358,416,863.00 |
    | 2023-04 | 396,849,049.00 | 400,672,017.00 | 368,024,910.00 |
    | 2023-05 | 349,749,072.00 | 408,111,158.00 | 364,369,742.00 |
    | 2023-06 | 279,698,633.00 | 342,098,918.00 | 350,257,891.00 |
    | 2023-07 | 312,983,148.00 | 314,143,618.00 | 357,407,817.00 |


---


### 10. ABC 분석 — 상품별 매출 누적 비율


2024년 상품별 매출을 내림차순으로 정렬하고, 누적 매출 비율로 A/B/C 등급을 부여하세요.
(A: 상위 70%, B: 70~90%, C: 나머지)


**힌트 1:** - 누적 비율: `SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER ()`
- CASE문으로 A/B/C 등급 분류
- 파레토 법칙(80:20)의 변형



??? success "정답"
    ```sql
    WITH product_revenue AS (
        SELECT
            p.id,
            p.name AS product_name,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name
    ),
    cumulative AS (
        SELECT
            product_name,
            revenue,
            SUM(revenue) OVER (ORDER BY revenue DESC) AS cum_revenue,
            SUM(revenue) OVER () AS total_revenue
        FROM product_revenue
    )
    SELECT
        product_name,
        revenue,
        ROUND(100.0 * cum_revenue / total_revenue, 1) AS cum_pct,
        CASE
            WHEN 100.0 * cum_revenue / total_revenue <= 70 THEN 'A'
            WHEN 100.0 * cum_revenue / total_revenue <= 90 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM cumulative
    ORDER BY revenue DESC
    LIMIT 30;
    ```


    **실행 결과** (총 30행 중 상위 7행)

    | product_name | revenue | cum_pct | abc_class |
    |---|---|---|---|
    | Razer Blade 18 블랙 | 165,417,800.00 | 3.20 | A |
    | Razer Blade 16 실버 | 137,007,300.00 | 5.90 | A |
    | MacBook Air 15 M3 실버 | 126,065,300.00 | 8.30 | A |
    | ASUS Dual RTX 4060 Ti 블랙 | 106,992,000.00 | 10.40 | A |
    | ASUS Dual RTX 5070 Ti 실버 | 104,558,400.00 | 12.40 | A |
    | ASUS ROG Swift PG32UCDM 실버 | 90,734,400.00 | 14.20 | A |
    | ASUS ROG Strix Scar 16 | 85,837,500.00 | 15.80 | A |


---


### 11. 신규 고객 vs 재구매 고객 매출 비교


2024년 월별로 신규 고객(해당 월에 첫 주문)과 재구매 고객의 주문 수, 매출을 분리하세요.


**힌트 1:** - 각 고객의 첫 주문 월: `MIN(ordered_at)` 으로 구함
- 주문 월 = 첫 주문 월이면 "신규", 아니면 "재구매"
- CTE로 단계적으로 처리



??? success "정답"
    ```sql
    WITH first_order AS (
        SELECT
            customer_id,
            SUBSTR(MIN(ordered_at), 1, 7) AS first_month
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    classified AS (
        SELECT
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            CASE
                WHEN SUBSTR(o.ordered_at, 1, 7) = fo.first_month THEN '신규'
                ELSE '재구매'
            END AS customer_type,
            o.total_amount
        FROM orders AS o
        INNER JOIN first_order AS fo ON o.customer_id = fo.customer_id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        year_month,
        customer_type,
        COUNT(*)                  AS order_count,
        ROUND(SUM(total_amount)) AS revenue
    FROM classified
    GROUP BY year_month, customer_type
    ORDER BY year_month, customer_type;
    ```


    **실행 결과** (총 24행 중 상위 7행)

    | year_month | customer_type | order_count | revenue |
    |---|---|---|---|
    | 2024-01 | 신규 | 32 | 31,865,130.00 |
    | 2024-01 | 재구매 | 282 | 257,043,190.00 |
    | 2024-02 | 신규 | 30 | 8,770,172.00 |
    | 2024-02 | 재구매 | 386 | 394,357,577.00 |
    | 2024-03 | 신규 | 50 | 28,455,371.00 |
    | 2024-03 | 재구매 | 505 | 491,389,131.00 |
    | 2024-04 | 신규 | 34 | 25,112,310.00 |


---


### 12. 고객 등급별 평균 객단가 추이


2024년 월별로 고객 등급(BRONZE/SILVER/GOLD/VIP)별 평균 주문 금액을 구하세요.


**힌트 1:** - `customers.grade`로 등급 구분
- `AVG(total_amount)` 그룹별 집계
- 월 + 등급 두 차원으로 GROUP BY



??? success "정답"
    ```sql
    SELECT
        SUBSTR(o.ordered_at, 1, 7) AS year_month,
        c.grade,
        COUNT(*)                   AS order_count,
        ROUND(AVG(o.total_amount)) AS avg_order_value
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(o.ordered_at, 1, 7), c.grade
    ORDER BY year_month, 
        CASE c.grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
        END;
    ```


    **실행 결과** (총 48행 중 상위 7행)

    | year_month | grade | order_count | avg_order_value |
    |---|---|---|---|
    | 2024-01 | VIP | 124 | 834,949.00 |
    | 2024-01 | GOLD | 73 | 1,202,930.00 |
    | 2024-01 | SILVER | 56 | 904,820.00 |
    | 2024-01 | BRONZE | 61 | 768,702.00 |
    | 2024-02 | VIP | 178 | 926,721.00 |
    | 2024-02 | GOLD | 97 | 926,946.00 |
    | 2024-02 | SILVER | 40 | 974,420.00 |


---


### 13. 배송사별 배송 소요일 분석


2024년 배송사(carrier)별 평균 배송 소요일, 최소/최대 소요일, 배송 건수를 구하세요.
배송 완료(delivered)된 건만 대상으로 합니다.


**힌트 1:** - 배송 소요일: `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)`
- `shipping` 테이블의 `status = 'delivered'`
- `shipped_at`과 `delivered_at`이 모두 NOT NULL인 건만



??? success "정답"
    ```sql
    SELECT
        s.carrier,
        COUNT(*)                                                        AS delivery_count,
        ROUND(AVG(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at)), 1) AS avg_days,
        MIN(ROUND(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at), 1)) AS min_days,
        MAX(ROUND(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at), 1)) AS max_days,
        ROUND(100.0 * SUM(CASE
            WHEN JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at) <= 2 THEN 1
            ELSE 0
        END) / COUNT(*), 1) AS within_2days_pct
    FROM shipping AS s
    INNER JOIN orders AS o ON s.order_id = o.id
    WHERE s.status = 'delivered'
      AND s.shipped_at IS NOT NULL
      AND s.delivered_at IS NOT NULL
      AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
    GROUP BY s.carrier
    ORDER BY avg_days;
    ```


    **실행 결과** (4행)

    | carrier | delivery_count | avg_days | min_days | max_days | within_2days_pct |
    |---|---|---|---|---|---|
    | CJ대한통운 | 2103 | 2.50 | 1.00 | 4.00 | 49.50 |
    | 로젠택배 | 1061 | 2.50 | 1.00 | 4.00 | 48.80 |
    | 우체국택배 | 824 | 2.50 | 1.00 | 4.00 | 50.70 |
    | 한진택배 | 1332 | 2.50 | 1.00 | 4.00 | 49.80 |


---


### 14. 할인율 구간별 매출 영향


2024년 주문의 할인율(discount_amount / (total_amount + discount_amount))을 구간별로 나누고,
각 구간의 주문 수, 평균 주문 금액, 총 매출을 분석하세요.


**힌트 1:** - 할인율 = `discount_amount / (total_amount + discount_amount) * 100`
- CASE문으로 0%, 1~5%, 6~10%, 11~20%, 20%+ 구간 분류
- `discount_amount = 0`이면 할인 없음



??? success "정답"
    ```sql
    WITH order_discount AS (
        SELECT
            id,
            total_amount,
            discount_amount,
            CASE
                WHEN discount_amount = 0 THEN 0
                ELSE ROUND(100.0 * discount_amount / (total_amount + discount_amount), 1)
            END AS discount_pct
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        CASE
            WHEN discount_pct = 0    THEN '할인 없음'
            WHEN discount_pct <= 5   THEN '1~5%'
            WHEN discount_pct <= 10  THEN '6~10%'
            WHEN discount_pct <= 20  THEN '11~20%'
            ELSE '20% 초과'
        END AS discount_range,
        COUNT(*)                    AS order_count,
        ROUND(AVG(total_amount))    AS avg_order_value,
        ROUND(SUM(total_amount))    AS total_revenue
    FROM order_discount
    GROUP BY CASE
        WHEN discount_pct = 0    THEN '할인 없음'
        WHEN discount_pct <= 5   THEN '1~5%'
        WHEN discount_pct <= 10  THEN '6~10%'
        WHEN discount_pct <= 20  THEN '11~20%'
        ELSE '20% 초과'
    END
    ORDER BY
        CASE
            WHEN discount_pct = 0    THEN 1
            WHEN discount_pct <= 5   THEN 2
            WHEN discount_pct <= 10  THEN 3
            WHEN discount_pct <= 20  THEN 4
            ELSE 5
        END;
    ```


    **실행 결과** (4행)

    | discount_range | order_count | avg_order_value | total_revenue |
    |---|---|---|---|
    | 할인 없음 | 4152 | 815,975.00 | 3,387,926,737.00 |
    | 1~5% | 811 | 1,783,303.00 | 1,446,258,687.00 |
    | 6~10% | 228 | 848,082.00 | 193,362,738.00 |
    | 11~20% | 129 | 673,607.00 | 86,895,358.00 |


---


### 15. 프로모션 ROI 분석


각 프로모션의 투입 할인 금액 대비 매출 효과(ROI)를 분석하세요.
프로모션 기간 중 프로모션 대상 상품의 매출과 할인 금액을 집계합니다.


**힌트 1:** - `promotions` + `promotion_products`로 대상 상품 파악
- 프로모션 기간: `started_at` ~ `ended_at`
- `order_items`에서 해당 기간 + 해당 상품의 매출 집계
- ROI = (매출 - 할인 총액) / 할인 총액 * 100



??? success "정답"
    ```sql
    WITH promo_sales AS (
        SELECT
            pr.id           AS promo_id,
            pr.name         AS promo_name,
            pr.type         AS promo_type,
            pr.discount_type,
            pr.discount_value,
            COUNT(DISTINCT o.id) AS order_count,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS gross_revenue,
            ROUND(SUM(oi.discount_amount))          AS total_discount
        FROM promotions AS pr
        INNER JOIN promotion_products AS pp ON pr.id = pp.promotion_id
        INNER JOIN order_items AS oi ON pp.product_id = oi.product_id
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= pr.started_at
          AND o.ordered_at <= pr.ended_at
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY pr.id, pr.name, pr.type, pr.discount_type, pr.discount_value
    )
    SELECT
        promo_name,
        promo_type,
        discount_type || ' ' || discount_value AS discount_info,
        order_count,
        gross_revenue,
        total_discount,
        gross_revenue - total_discount AS net_revenue,
        CASE
            WHEN total_discount > 0
            THEN ROUND(100.0 * (gross_revenue - total_discount) / total_discount, 1)
            ELSE NULL
        END AS roi_pct
    FROM promo_sales
    ORDER BY roi_pct DESC;
    ```


    **실행 결과** (총 105행 중 상위 7행)

    | promo_name | promo_type | discount_info | order_count | gross_revenue | total_discount | net_revenue | roi_pct |
    |---|---|---|---|---|---|---|---|
    | 게이밍 기어 페스타 2023 | category | percent 18.0 | 25 | 16,859,400.00 | 15,600.00 | 16,843,800.00 | 107,973.10 |
    | 블랙프라이데이 2022 | seasonal | percent 25.0 | 25 | 17,059,700.00 | 18,500.00 | 17,041,200.00 | 92,114.60 |
    | 게이밍 기어 페스타 2024 | category | percent 18.0 | 30 | 18,118,000.00 | 27,600.00 | 18,090,400.00 | 65,544.90 |
    | 게이밍 기어 페스타 2020 | category | percent 18.0 | 33 | 12,592,900.00 | 19,500.00 | 12,573,400.00 | 64,479.00 |
    | 블랙프라이데이 2020 | seasonal | percent 25.0 | 35 | 18,172,900.00 | 31,300.00 | 18,141,600.00 | 57,960.40 |
    | 게이밍 기어 페스타 2016 | category | percent 18.0 | 5 | 5,221,100.00 | 11,300.00 | 5,209,800.00 | 46,104.40 |
    | 새해 특가 세일 2021 | seasonal | percent 10.0 | 35 | 33,039,800.00 | 76,200.00 | 32,963,600.00 | 43,259.30 |


---


### 16. 장바구니 → 구매 전환율


장바구니에 담긴 상품 중 실제 구매로 전환된 비율을 카테고리별로 구하세요.


**힌트 1:** - `cart_items`에 담긴 상품 수 vs 같은 고객이 실제 주문한 같은 상품 수
- `carts` + `cart_items` + `order_items` + `orders` JOIN
- 전환율 = 구매된 장바구니 항목 수 / 전체 장바구니 항목 수 * 100



??? success "정답"
    ```sql
    WITH cart_products AS (
        SELECT
            c.customer_id,
            ci.product_id,
            cat.name AS category
        FROM carts AS c
        INNER JOIN cart_items AS ci ON c.id = ci.cart_id
        INNER JOIN products AS p ON ci.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
    ),
    purchased AS (
        SELECT DISTINCT
            o.customer_id,
            oi.product_id
        FROM orders AS o
        INNER JOIN order_items AS oi ON o.id = oi.order_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        cp.category,
        COUNT(*) AS cart_items_total,
        SUM(CASE WHEN pur.product_id IS NOT NULL THEN 1 ELSE 0 END) AS converted,
        ROUND(100.0 * SUM(CASE WHEN pur.product_id IS NOT NULL THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS conversion_rate_pct
    FROM cart_products AS cp
    LEFT JOIN purchased AS pur
        ON cp.customer_id = pur.customer_id
        AND cp.product_id = pur.product_id
    GROUP BY cp.category
    ORDER BY conversion_rate_pct DESC;
    ```


    **실행 결과** (총 38행 중 상위 7행)

    | category | cart_items_total | converted | conversion_rate_pct |
    |---|---|---|---|
    | 게이밍 | 332 | 49 | 14.80 |
    | 케이스 | 325 | 37 | 11.40 |
    | SSD | 201 | 22 | 10.90 |
    | DDR4 | 197 | 21 | 10.70 |
    | Intel | 158 | 14 | 8.90 |
    | 무선 | 205 | 18 | 8.80 |
    | 스피커/헤드셋 | 398 | 34 | 8.50 |


---


### 17. 동시 구매 패턴(장바구니 분석)


같은 주문에서 함께 구매된 상품 쌍(pair)을 찾으세요.
동시 구매 빈도가 5회 이상인 상품 쌍만 표시합니다.


**힌트 1:** - `order_items`를 자기 조인(Self JOIN)하여 같은 주문의 서로 다른 상품 쌍 생성
- 중복 제거: `oi1.product_id < oi2.product_id`
- `GROUP BY` 상품 쌍으로 동시 구매 횟수 집계



??? success "정답"
    ```sql
    SELECT
        p1.name AS product_a,
        p2.name AS product_b,
        COUNT(*) AS co_purchase_count
    FROM order_items AS oi1
    INNER JOIN order_items AS oi2
        ON oi1.order_id = oi2.order_id
        AND oi1.product_id < oi2.product_id
    INNER JOIN products AS p1 ON oi1.product_id = p1.id
    INNER JOIN products AS p2 ON oi2.product_id = p2.id
    INNER JOIN orders AS o ON oi1.order_id = o.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY oi1.product_id, oi2.product_id, p1.name, p2.name
    HAVING COUNT(*) >= 5
    ORDER BY co_purchase_count DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | product_a | product_b | co_purchase_count |
    |---|---|---|
    | AMD Ryzen 9 9900X | Crucial T700 2TB 실버 | 430 |
    | AMD Ryzen 9 9900X | SK하이닉스 Platinum P41 2TB 실버 | 329 |
    | be quiet! Light Base 900 | Crucial T700 2TB 실버 | 294 |
    | Intel Core Ultra 5 245KF | Crucial T700 2TB 실버 | 282 |
    | be quiet! Light Base 900 | AMD Ryzen 9 9900X | 249 |
    | 시소닉 VERTEX GX-1200 블랙 | Crucial T700 2TB 실버 | 221 |
    | 삼성 DDR5 32GB PC5-38400 | Crucial T700 2TB 실버 | 217 |


---


### 18. 리뷰 평점과 매출 상관관계


상품별 평균 리뷰 평점과 매출의 관계를 분석하세요.
평점 구간(1~2, 2~3, 3~4, 4~5)별 평균 매출을 구합니다.


**힌트 1:** - 상품별 평균 평점과 매출을 먼저 구한 뒤
- CASE문으로 평점 구간 분류
- 리뷰가 없는 상품은 제외



??? success "정답"
    ```sql
    WITH product_metrics AS (
        SELECT
            p.id,
            p.name,
            AVG(r.rating)                          AS avg_rating,
            COUNT(DISTINCT r.id)                    AS review_count,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS revenue
        FROM products AS p
        INNER JOIN reviews AS r ON p.id = r.product_id
        INNER JOIN order_items AS oi ON p.id = oi.product_id
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name
        HAVING COUNT(DISTINCT r.id) >= 3
    )
    SELECT
        CASE
            WHEN avg_rating < 2 THEN '1.0~1.9'
            WHEN avg_rating < 3 THEN '2.0~2.9'
            WHEN avg_rating < 4 THEN '3.0~3.9'
            ELSE '4.0~5.0'
        END AS rating_range,
        COUNT(*)                    AS product_count,
        ROUND(AVG(revenue))         AS avg_revenue,
        ROUND(AVG(review_count))    AS avg_reviews,
        ROUND(AVG(avg_rating), 2)   AS avg_rating_in_range
    FROM product_metrics
    GROUP BY CASE
        WHEN avg_rating < 2 THEN '1.0~1.9'
        WHEN avg_rating < 3 THEN '2.0~2.9'
        WHEN avg_rating < 4 THEN '3.0~3.9'
        ELSE '4.0~5.0'
    END
    ORDER BY rating_range;
    ```


    **실행 결과** (2행)

    | rating_range | product_count | avg_revenue | avg_reviews | avg_rating_in_range |
    |---|---|---|---|---|
    | 3.0~3.9 | 165 | 3,987,852,901.00 | 33.00 | 3.73 |
    | 4.0~5.0 | 99 | 4,123,862,055.00 | 30.00 | 4.15 |


---


### 19. 포인트 사용 효과 분석


포인트를 사용한 주문과 사용하지 않은 주문의 평균 주문 금액, 재구매율을 비교하세요.
(2024년 기준)


**힌트 1:** - `orders.point_used > 0`이면 포인트 사용 주문
- 재구매율: 해당 그룹 고객 중 2회 이상 주문한 비율
- CTE로 고객별 주문 특성을 먼저 집계



??? success "정답"
    ```sql
    WITH order_classified AS (
        SELECT
            customer_id,
            total_amount,
            CASE WHEN point_used > 0 THEN '포인트 사용' ELSE '미사용' END AS point_type
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    customer_stats AS (
        SELECT
            point_type,
            customer_id,
            COUNT(*) AS order_count,
            AVG(total_amount) AS avg_amount
        FROM order_classified
        GROUP BY point_type, customer_id
    )
    SELECT
        point_type,
        COUNT(DISTINCT customer_id)    AS customer_count,
        ROUND(AVG(avg_amount))         AS avg_order_value,
        ROUND(100.0 * SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END)
            / COUNT(*), 1)            AS repeat_rate_pct
    FROM customer_stats
    GROUP BY point_type;
    ```


    **실행 결과** (2행)

    | point_type | customer_count | avg_order_value | repeat_rate_pct |
    |---|---|---|---|
    | 미사용 | 1607 | 895,789.00 | 57.70 |
    | 포인트 사용 | 396 | 1,033,110.00 | 18.70 |


---


### 20. 종합 경영 대시보드


CEO를 위한 2024년 종합 경영 대시보드를 하나의 쿼리로 생성하세요.
총 매출, 주문 수, 고객 수, 평균 객단가, 반품률, 평균 배송일, 평균 리뷰 평점을 포함합니다.


**힌트 1:** - 각 지표를 서브쿼리 또는 CTE로 개별 계산한 뒤 결합
- `CROSS JOIN` 또는 스칼라 서브쿼리로 단일 행 결합
- 반품률 = 반품 주문 수 / 전체 주문 수



??? success "정답"
    ```sql
    WITH sales AS (
        SELECT
            COUNT(*)                            AS total_orders,
            COUNT(DISTINCT customer_id)         AS unique_customers,
            ROUND(SUM(total_amount))            AS total_revenue,
            ROUND(AVG(total_amount))            AS avg_order_value
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    returns_stat AS (
        SELECT
            ROUND(100.0 * COUNT(*) / (
                SELECT COUNT(*) FROM orders
                WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
            ), 1) AS return_rate_pct
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status IN ('returned', 'return_requested')
    ),
    shipping_stat AS (
        SELECT
            ROUND(AVG(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at)), 1) AS avg_delivery_days
        FROM shipping AS s
        INNER JOIN orders AS o ON s.order_id = o.id
        WHERE s.status = 'delivered'
          AND s.shipped_at IS NOT NULL
          AND s.delivered_at IS NOT NULL
          AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
    ),
    review_stat AS (
        SELECT
            ROUND(AVG(rating), 2) AS avg_rating,
            COUNT(*) AS review_count
        FROM reviews
        WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
    )
    SELECT
        s.total_revenue,
        s.total_orders,
        s.unique_customers,
        s.avg_order_value,
        r.return_rate_pct,
        sh.avg_delivery_days,
        rv.avg_rating,
        rv.review_count
    FROM sales AS s
    CROSS JOIN returns_stat AS r
    CROSS JOIN shipping_stat AS sh
    CROSS JOIN review_stat AS rv;
    ```


    **실행 결과** (1행)

    | total_revenue | total_orders | unique_customers | avg_order_value | return_rate_pct | avg_delivery_days | avg_rating | review_count |
    |---|---|---|---|---|---|---|---|
    | 5,114,443,520.00 | 5320 | 1669 | 961,362.00 | 2.70 | 2.50 | 3.91 | 1267 |


---
