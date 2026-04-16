# SQL 면접 대비

!!! info "사용 테이블"

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `categories` — 카테고리 (부모-자식 계층)  

    `reviews` — 리뷰 (평점, 내용)  

    `customers` — 고객 (등급, 포인트, 가입채널)  



!!! abstract "학습 범위"

    `ROW_NUMBER`, `LAG`, `Running Total`, `Moving Average`, `Recursive CTE`, `NTILE`, `Funnel`



### 1. Top-N per Group


각 카테고리에서 매출 1위 상품을 구하세요. (동률 시 하나만)


**힌트 1:** `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)`로
그룹 내 순위를 매기고, `WHERE rn = 1`로 필터링합니다.



??? success "정답"
    ```sql
    WITH ranked AS (
        SELECT
            cat.name AS category,
            p.name AS product,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue,
            ROW_NUMBER() OVER (PARTITION BY cat.id ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS rn
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        INNER JOIN products p ON oi.product_id = p.id
        INNER JOIN categories cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY cat.id, cat.name, p.id, p.name
    )
    SELECT category, product, revenue
    FROM ranked
    WHERE rn = 1
    ORDER BY revenue DESC;
    ```


    **실행 결과** (총 40행 중 상위 7행)

    | category | product | revenue |
    |---|---|---|
    | 게이밍 노트북 | Razer Blade 18 블랙 | 1,179,690,100.00 |
    | NVIDIA | ASUS Dual RTX 4060 Ti 블랙 | 901,407,600.00 |
    | AMD | MSI Radeon RX 7900 XTX GAMING X 화이트 | 602,487,200.00 |
    | 2in1 | 레노버 ThinkPad X1 2in1 실버 | 582,223,200.00 |
    | Intel | Intel Core Ultra 5 245KF | 563,595,600.00 |
    | 일반 노트북 | ASUS ExpertBook B5 [특별 한정판 에디션] 저소음 설... | 555,152,000.00 |
    | 게이밍 모니터 | 삼성 오디세이 G5 27 블랙 | 538,902,000.00 |


---


### 2. 연속 증가 구간


월별 매출이 3개월 연속 증가한 구간을 찾으세요.


**힌트 1:** `LAG(revenue, 1)`과 `LAG(revenue, 2)`로 이전 2개월 매출을 가져와서
현재 > 전월 > 전전월 조건 비교.



??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS month,
            SUM(total_amount) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    ),
    with_lag AS (
        SELECT
            month, revenue,
            LAG(revenue, 1) OVER (ORDER BY month) AS prev_1,
            LAG(revenue, 2) OVER (ORDER BY month) AS prev_2
        FROM monthly
    )
    SELECT month, revenue, prev_1, prev_2
    FROM with_lag
    WHERE revenue > prev_1 AND prev_1 > prev_2
    ORDER BY month;
    ```


    **실행 결과** (총 22행 중 상위 7행)

    | month | revenue | prev_1 | prev_2 |
    |---|---|---|---|
    | 2016-04 | 16,878,372.00 | 14,806,662.00 | 13,115,835.00 |
    | 2016-05 | 31,432,968.00 | 16,878,372.00 | 14,806,662.00 |
    | 2016-10 | 38,989,248.00 | 32,257,785.00 | 19,122,587.00 |
    | 2018-01 | 85,442,344.00 | 83,561,937.00 | 52,363,290.00 |
    | 2018-09 | 134,594,321.00 | 85,713,577.00 | 40,611,909.00 |
    | 2018-12 | 167,642,638.00 | 93,642,089.00 | 63,988,837.00 |
    | 2019-01 | 228,770,158.00 | 167,642,638.00 | 93,642,089.00 |


---


### 3. 누적 합계 (Running Total)


2024년 월별 매출과 누적 매출을 구하세요.


**힌트 1:** `SUM(monthly_revenue) OVER (ORDER BY month)`로 누적 합계를 구합니다.



??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        ROUND(SUM(total_amount), 0) AS monthly_revenue,
        ROUND(SUM(SUM(total_amount)) OVER (ORDER BY SUBSTR(ordered_at, 1, 7)), 0) AS cumulative_revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | month | monthly_revenue | cumulative_revenue |
    |---|---|---|
    | 2024-01 | 301,075,320.00 | 301,075,320.00 |
    | 2024-02 | 426,177,449.00 | 727,252,769.00 |
    | 2024-03 | 536,322,767.00 | 1,263,575,536.00 |
    | 2024-04 | 470,154,081.00 | 1,733,729,617.00 |
    | 2024-05 | 459,724,596.00 | 2,193,454,213.00 |
    | 2024-06 | 377,040,302.00 | 2,570,494,515.00 |
    | 2024-07 | 363,944,597.00 | 2,934,439,112.00 |


---


### 4. 이동 평균 (Moving Average)


3개월 이동 평균 매출을 구하세요.


**힌트 1:** `AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`



??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        month,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 0) AS moving_avg_3m
    FROM monthly
    ORDER BY month;
    ```


    **실행 결과** (총 120행 중 상위 7행)

    | month | revenue | moving_avg_3m |
    |---|---|---|
    | 2016-01 | 15,816,169.00 | 15,816,169.00 |
    | 2016-02 | 13,115,835.00 | 14,466,002.00 |
    | 2016-03 | 14,806,662.00 | 14,579,555.00 |
    | 2016-04 | 16,878,372.00 | 14,933,623.00 |
    | 2016-05 | 31,432,968.00 | 21,039,334.00 |
    | 2016-06 | 26,381,091.00 | 24,897,477.00 |
    | 2016-07 | 30,436,884.00 | 29,416,981.00 |


---


### 5. 갭 분석 (Missing Data)


2024년에 주문이 없는 날짜를 찾으세요.


**힌트 1:** `WITH RECURSIVE`로 2024년 모든 날짜를 생성한 뒤,
실제 주문 날짜와 `LEFT JOIN`하여 `NULL`인 날을 찾습니다.



??? success "정답"
    ```sql
    WITH RECURSIVE all_dates AS (
        SELECT '2024-01-01' AS dt
        UNION ALL
        SELECT DATE(dt, '+1 day')
        FROM all_dates
        WHERE dt < '2024-12-31'
    ),
    order_dates AS (
        SELECT DISTINCT SUBSTR(ordered_at, 1, 10) AS dt
        FROM orders
        WHERE ordered_at LIKE '2024%'
    )
    SELECT ad.dt AS missing_date
    FROM all_dates ad
    LEFT JOIN order_dates od ON ad.dt = od.dt
    WHERE od.dt IS NULL
    ORDER BY ad.dt;
    ```


---


### 6. 백분위수 (Percentile)


고객 구매 금액의 상위 10%, 25%, 50%(중앙값), 75%, 90% 지점을 구하세요.


**힌트 1:** `NTILE(100) OVER (ORDER BY total_spent)`로 백분위 그룹을 만들고,
`MAX(CASE WHEN percentile = N ...)`로 각 지점의 값을 추출합니다.



??? success "정답"
    ```sql
    WITH customer_spend AS (
        SELECT
            customer_id,
            SUM(total_amount) AS total_spent
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ),
    ranked AS (
        SELECT
            total_spent,
            NTILE(100) OVER (ORDER BY total_spent) AS percentile
        FROM customer_spend
    )
    SELECT
        MAX(CASE WHEN percentile = 10 THEN total_spent END) AS p10,
        MAX(CASE WHEN percentile = 25 THEN total_spent END) AS p25,
        MAX(CASE WHEN percentile = 50 THEN total_spent END) AS p50_median,
        MAX(CASE WHEN percentile = 75 THEN total_spent END) AS p75,
        MAX(CASE WHEN percentile = 90 THEN total_spent END) AS p90
    FROM ranked;
    ```


    **실행 결과** (1행)

    | p10 | p25 | p50_median | p75 | p90 |
    |---|---|---|---|---|
    | 180,500.00 | 1,183,200.00 | 4,654,232.00 | 13,607,591.00 | 31,606,150.00 |


---


### 7. 연도별 순위 변동


카테고리별 연도별 매출 순위를 구하고, 전년 대비 순위 변동을 표시하세요.


**힌트 1:** `RANK() OVER (PARTITION BY year ORDER BY revenue DESC)`로 연도별 순위를 매기고,
`LAG(rank) OVER (PARTITION BY category ORDER BY year)`로 전년 순위를 가져옵니다.



??? success "정답"
    ```sql
    WITH yearly_category AS (
        SELECT
            SUBSTR(o.ordered_at, 1, 4) AS year,
            cat.name AS category,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        INNER JOIN products p ON oi.product_id = p.id
        INNER JOIN categories cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY SUBSTR(o.ordered_at, 1, 4), cat.name
    ),
    with_rank AS (
        SELECT *,
            RANK() OVER (PARTITION BY year ORDER BY revenue DESC) AS rank
        FROM yearly_category
    )
    SELECT
        wr.year, wr.category, wr.revenue, wr.rank,
        LAG(wr.rank) OVER (PARTITION BY wr.category ORDER BY wr.year) AS prev_rank,
        LAG(wr.rank) OVER (PARTITION BY wr.category ORDER BY wr.year) - wr.rank AS rank_change
    FROM with_rank wr
    WHERE wr.year >= '2022'
    ORDER BY wr.year, wr.rank;
    ```


    **실행 결과** (총 148행 중 상위 7행)

    | year | category | revenue | rank | prev_rank | rank_change |
    |---|---|---|---|---|---|
    | 2022 | 게이밍 노트북 | 832,586,500.00 | 1 | NULL | NULL |
    | 2022 | 게이밍 모니터 | 372,536,900.00 | 2 | NULL | NULL |
    | 2022 | 일반 노트북 | 368,304,500.00 | 3 | NULL | NULL |
    | 2022 | AMD | 360,526,000.00 | 4 | NULL | NULL |
    | 2022 | NVIDIA | 331,064,700.00 | 5 | NULL | NULL |
    | 2022 | AMD 소켓 | 257,637,700.00 | 6 | NULL | NULL |
    | 2022 | Intel | 217,901,700.00 | 7 | NULL | NULL |


---


### 8. Funnel 분석 (퍼널)


고객 여정 퍼널을 분석하세요: 가입 -> 첫 주문 -> 리뷰 작성 -> 재구매.
각 단계의 전환율을 구하세요.


**힌트 1:** 각 단계의 고유 고객 수를 스칼라 서브쿼리로 구하고,
`100.0 * next_step / prev_step`로 전환율을 계산합니다.



??? success "정답"
    ```sql
    WITH funnel AS (
        SELECT
            (SELECT COUNT(*) FROM customers) AS step1_signup,
            (SELECT COUNT(DISTINCT customer_id) FROM orders
             WHERE status NOT IN ('cancelled')) AS step2_first_order,
            (SELECT COUNT(DISTINCT customer_id) FROM reviews) AS step3_review,
            (SELECT COUNT(*) FROM (
                SELECT customer_id FROM orders
                WHERE status NOT IN ('cancelled')
                GROUP BY customer_id HAVING COUNT(*) >= 2
            )) AS step4_repeat
    )
    SELECT
        step1_signup,
        step2_first_order,
        ROUND(100.0 * step2_first_order / step1_signup, 1) AS cvr_1_2,
        step3_review,
        ROUND(100.0 * step3_review / step2_first_order, 1) AS cvr_2_3,
        step4_repeat,
        ROUND(100.0 * step4_repeat / step2_first_order, 1) AS cvr_2_4
    FROM funnel;
    ```


    **실행 결과** (1행)

    | step1_signup | step2_first_order | cvr_1_2 | step3_review | cvr_2_3 | step4_repeat | cvr_2_4 |
    |---|---|---|---|---|---|---|
    | 5230 | 2809 | 53.70 | 1899 | 67.60 | 2319 | 82.60 |


---


### 9. 자기 참조 계층 깊이 탐색


카테고리 계층의 최대 깊이와 각 깊이별 카테고리 수를 구하세요. 재귀 CTE를 사용하세요.


**힌트 1:** `WITH RECURSIVE`에서 `parent_id IS NULL`을 시작점(depth=0)으로,
`c.parent_id = tree.id`로 자식을 재귀 탐색합니다.



??? success "정답"
    ```sql
    WITH RECURSIVE tree AS (
        SELECT id, name, parent_id, 0 AS depth
        FROM categories
        WHERE parent_id IS NULL
        UNION ALL
        SELECT c.id, c.name, c.parent_id, t.depth + 1
        FROM categories c
        INNER JOIN tree t ON c.parent_id = t.id
    )
    SELECT
        depth,
        COUNT(*) AS category_count,
        GROUP_CONCAT(name, ', ') AS categories
    FROM tree
    GROUP BY depth
    ORDER BY depth;
    ```


    **실행 결과** (2행)

    | depth | category_count | categories |
    |---|---|---|
    | 0 | 18 | 데스크톱 PC, 노트북, 모니터, CPU, 메인보드, 메모리(RAM... |
    | 1 | 35 | 베어본, 완제품, 조립PC, 2in1, 게이밍 노트북, 맥북, 일반... |


---


### 10. 동일 상품 재구매 간격


같은 상품을 2회 이상 구매한 고객의 평균 재구매 간격(일)을 구하세요.


**힌트 1:** `LAG(ordered_at) OVER (PARTITION BY customer_id, product_id ORDER BY ordered_at)`로
같은 고객-상품의 이전 주문일을 가져와 JULIANDAY 차이를 계산합니다.



??? success "정답"
    ```sql
    WITH repeat_purchases AS (
        SELECT
            o.customer_id,
            oi.product_id,
            o.ordered_at,
            LAG(o.ordered_at) OVER (
                PARTITION BY o.customer_id, oi.product_id
                ORDER BY o.ordered_at
            ) AS prev_order_date
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
    )
    SELECT
        ROUND(AVG(JULIANDAY(ordered_at) - JULIANDAY(prev_order_date)), 1) AS avg_repurchase_days,
        MIN(CAST(JULIANDAY(ordered_at) - JULIANDAY(prev_order_date) AS INTEGER)) AS min_days,
        MAX(CAST(JULIANDAY(ordered_at) - JULIANDAY(prev_order_date) AS INTEGER)) AS max_days,
        COUNT(*) AS repurchase_count
    FROM repeat_purchases
    WHERE prev_order_date IS NOT NULL;
    ```


    **실행 결과** (1행)

    | avg_repurchase_days | min_days | max_days | repurchase_count |
    |---|---|---|---|
    | 370.30 | 0 | 3240 | 22,778 |


---
