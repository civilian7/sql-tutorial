# 고객/운영 분석

!!! info "사용 테이블"

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `categories` — 카테고리 (부모-자식 계층)  

    `inventory_transactions` — 재고 입출고 (유형, 수량)  

    `customer_grade_history` — 등급 이력 (변경 전후)  

    `complaints` — 고객 불만 (유형, 우선순위)  

    `staff` — 직원 (부서, 역할, 관리자)  



!!! abstract "학습 범위"

    `RFM Analysis`, `Cohort`, `LTV`, `Inventory ABC Analysis`, `Safety Stock`, `CS Performance`, `CTE + Window Function`



### 1. RFM 기초 — 고객별 핵심 지표 산출


마케팅팀이 고객 세분화를 위해 각 고객의 RFM 지표를 요청했습니다.
고객별 마지막 주문일(Recency), 총 주문 횟수(Frequency), 총 구매 금액(Monetary)을 구하세요.
취소/반품 주문은 제외합니다. 상위 20명만 표시합니다.


**힌트 1:** - Recency: `MAX(ordered_at)`
- Frequency: `COUNT(*)`
- Monetary: `SUM(total_amount)`
- `customers` + `orders` JOIN



??? success "정답"
    ```sql
    SELECT
        c.id            AS customer_id,
        c.name          AS customer_name,
        c.grade,
        MAX(o.ordered_at)           AS last_order_date,
        COUNT(*)                    AS order_count,
        ROUND(SUM(o.total_amount))  AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer_id | customer_name | grade | last_order_date | order_count | total_spent |
    |---|---|---|---|---|---|
    | 226 | 박정수 | VIP | 2025-12-21 21:52:24 | 303 | 403,448,758.00 |
    | 97 | 김병철 | VIP | 2025-12-28 11:37:58 | 342 | 366,385,931.00 |
    | 162 | 강명자 | VIP | 2025-12-20 10:21:05 | 249 | 253,180,338.00 |
    | 356 | 정유진 | VIP | 2025-10-24 16:44:53 | 223 | 244,604,910.00 |
    | 549 | 이미정 | VIP | 2025-12-04 12:11:17 | 219 | 235,775,349.00 |
    | 227 | 김성민 | VIP | 2025-12-19 22:54:22 | 230 | 234,708,853.00 |
    | 98 | 이영자 | VIP | 2025-11-29 11:04:23 | 275 | 230,165,991.00 |


---


### 2. RFM 4분위 세그먼트


RFM 지표를 기반으로 고객을 4분위(Q1~Q4)로 나누세요.
Recency는 최근일수록 높은 점수(4), Frequency와 Monetary는 클수록 높은 점수(4)입니다.
각 고객의 R/F/M 점수와 총점을 표시합니다.


**힌트 1:** - `NTILE(4)`로 각 지표를 4등분
- Recency: `ORDER BY last_order_date ASC` → NTILE 4가 가장 최근
- Frequency/Monetary: `ORDER BY ... ASC` → NTILE 4가 가장 큼
- 총점 = R + F + M (최대 12점)



??? success "정답"
    ```sql
    WITH rfm_raw AS (
        SELECT
            c.id AS customer_id,
            c.name,
            c.grade,
            MAX(o.ordered_at)           AS last_order_date,
            COUNT(*)                    AS frequency,
            ROUND(SUM(o.total_amount))  AS monetary
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    ),
    rfm_scored AS (
        SELECT
            customer_id,
            name,
            grade,
            last_order_date,
            frequency,
            monetary,
            NTILE(4) OVER (ORDER BY last_order_date ASC)  AS r_score,
            NTILE(4) OVER (ORDER BY frequency ASC)         AS f_score,
            NTILE(4) OVER (ORDER BY monetary ASC)          AS m_score
        FROM rfm_raw
    )
    SELECT
        customer_id,
        name,
        grade,
        r_score,
        f_score,
        m_score,
        r_score + f_score + m_score AS rfm_total,
        CASE
            WHEN r_score + f_score + m_score >= 10 THEN 'Champion'
            WHEN r_score + f_score + m_score >= 7  THEN 'Loyal'
            WHEN r_score >= 3 AND f_score <= 2     THEN 'New Customer'
            WHEN r_score <= 2 AND f_score >= 3     THEN 'At Risk'
            ELSE 'Regular'
        END AS segment
    FROM rfm_scored
    ORDER BY rfm_total DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | customer_id | name | grade | r_score | f_score | m_score | rfm_total | segment |
    |---|---|---|---|---|---|---|---|
    | 486 | 김성호 | GOLD | 4 | 4 | 4 | 12 | Champion |
    | 10 | 박지훈 | GOLD | 4 | 4 | 4 | 12 | Champion |
    | 1490 | 이은영 | VIP | 4 | 4 | 4 | 12 | Champion |
    | 647 | 김영희 | VIP | 4 | 4 | 4 | 12 | Champion |
    | 1241 | 김정수 | BRONZE | 4 | 4 | 4 | 12 | Champion |
    | 256 | 박준호 | GOLD | 4 | 4 | 4 | 12 | Champion |
    | 2328 | 서성민 | VIP | 4 | 4 | 4 | 12 | Champion |


---


### 3. 코호트 리텐션 분석


2023년에 첫 구매한 고객의 월별 리텐션(재구매율)을 코호트 분석으로 구하세요.
가입 후 0개월(첫 구매), 1개월, 2개월, ... 6개월까지의 리텐션율을 계산합니다.


**힌트 1:** - 코호트 = 첫 구매 월이 같은 고객 그룹
- 월 차이 = 주문 월 - 첫 구매 월 (개월 수)
- 리텐션율 = 해당 월에 주문한 코호트 고객 수 / 코호트 전체 고객 수



??? success "정답"
    ```sql
    WITH first_purchase AS (
        SELECT
            customer_id,
            SUBSTR(MIN(ordered_at), 1, 7) AS cohort_month
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
        HAVING cohort_month LIKE '2023%'
    ),
    monthly_activity AS (
        SELECT DISTINCT
            fp.customer_id,
            fp.cohort_month,
            SUBSTR(o.ordered_at, 1, 7) AS activity_month,
            (CAST(SUBSTR(o.ordered_at, 1, 4) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 1, 4) AS INTEGER)) * 12
            + CAST(SUBSTR(o.ordered_at, 6, 2) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 6, 2) AS INTEGER)
                AS month_offset
        FROM first_purchase AS fp
        INNER JOIN orders AS o ON fp.customer_id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    cohort_size AS (
        SELECT cohort_month, COUNT(DISTINCT customer_id) AS total_customers
        FROM first_purchase
        GROUP BY cohort_month
    )
    SELECT
        ma.cohort_month,
        cs.total_customers,
        ma.month_offset,
        COUNT(DISTINCT ma.customer_id) AS active_customers,
        ROUND(100.0 * COUNT(DISTINCT ma.customer_id) / cs.total_customers, 1) AS retention_pct
    FROM monthly_activity AS ma
    INNER JOIN cohort_size AS cs ON ma.cohort_month = cs.cohort_month
    WHERE ma.month_offset BETWEEN 0 AND 6
    GROUP BY ma.cohort_month, cs.total_customers, ma.month_offset
    ORDER BY ma.cohort_month, ma.month_offset;
    ```


    **실행 결과** (총 83행 중 상위 7행)

    | cohort_month | total_customers | month_offset | active_customers | retention_pct |
    |---|---|---|---|---|
    | 2023-01 | 21 | 0 | 21 | 100.00 |
    | 2023-01 | 21 | 1 | 2 | 9.50 |
    | 2023-01 | 21 | 2 | 1 | 4.80 |
    | 2023-01 | 21 | 3 | 2 | 9.50 |
    | 2023-01 | 21 | 4 | 5 | 23.80 |
    | 2023-01 | 21 | 5 | 7 | 33.30 |
    | 2023-02 | 31 | 0 | 31 | 100.00 |


---


### 4. 이탈 고객 감지


마지막 주문 후 6개월 이상 구매가 없는 고객을 "이탈 위험"으로 분류하세요.
이탈 고객의 등급별 분포와 이탈 전 평균 구매 금액을 구합니다.
(기준일: 2025-03-31)


**힌트 1:** - 이탈 기준: `JULIANDAY('2025-03-31') - JULIANDAY(MAX(ordered_at)) > 180`
- 등급별 GROUP BY
- 이탈 고객과 활성 고객 비교도 함께 표시



??? success "정답"
    ```sql
    WITH customer_activity AS (
        SELECT
            c.id            AS customer_id,
            c.name,
            c.grade,
            MAX(o.ordered_at)           AS last_order_date,
            COUNT(*)                    AS order_count,
            ROUND(AVG(o.total_amount))  AS avg_order_value,
            ROUND(JULIANDAY('2025-03-31') - JULIANDAY(MAX(o.ordered_at))) AS days_since_last
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    )
    SELECT
        grade,
        CASE WHEN days_since_last > 180 THEN '이탈 위험' ELSE '활성' END AS status,
        COUNT(*) AS customer_count,
        ROUND(AVG(avg_order_value)) AS avg_order_value,
        ROUND(AVG(order_count), 1)  AS avg_orders,
        ROUND(AVG(days_since_last)) AS avg_days_inactive
    FROM customer_activity
    GROUP BY grade,
        CASE WHEN days_since_last > 180 THEN '이탈 위험' ELSE '활성' END
    ORDER BY
        CASE grade WHEN 'VIP' THEN 1 WHEN 'GOLD' THEN 2 WHEN 'SILVER' THEN 3 ELSE 4 END,
        status;
    ```


    **실행 결과** (5행)

    | grade | status | customer_count | avg_order_value | avg_orders | avg_days_inactive |
    |---|---|---|---|---|---|
    | VIP | 활성 | 368 | 1,437,751.00 | 38.20 | -222.00 |
    | GOLD | 활성 | 524 | 1,112,559.00 | 15.10 | -169.00 |
    | SILVER | 활성 | 479 | 877,935.00 | 10.70 | -133.00 |
    | BRONZE | 이탈 위험 | 599 | 840,118.00 | 4.50 | 578.00 |
    | BRONZE | 활성 | 823 | 556,893.00 | 6.00 | -69.00 |


---


### 5. 고객 생애 가치(LTV) 추정


고객 등급별 평균 LTV(Life Time Value)를 추정하세요.
LTV = 평균 주문 금액 x 연간 주문 횟수 x 평균 활동 기간(년)


**힌트 1:** - 활동 기간 = (마지막 주문일 - 첫 주문일) / 365. 최소 1년으로 처리
- 연간 주문 횟수 = 총 주문 횟수 / 활동 기간
- 등급별 집계



??? success "정답"
    ```sql
    WITH customer_ltv AS (
        SELECT
            c.id,
            c.grade,
            COUNT(*) AS total_orders,
            AVG(o.total_amount) AS avg_order_value,
            MAX(JULIANDAY(o.ordered_at) - JULIANDAY(MIN(o.ordered_at)) OVER (PARTITION BY c.id))
                / 365.0 AS active_years_raw
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.grade
    ),
    ltv_calc AS (
        SELECT
            id,
            grade,
            total_orders,
            avg_order_value,
            MAX(active_years_raw, 1.0) AS active_years,
            total_orders / MAX(active_years_raw, 1.0) AS orders_per_year,
            avg_order_value * (total_orders / MAX(active_years_raw, 1.0)) * MAX(active_years_raw, 1.0)
                AS ltv
        FROM customer_ltv
    )
    SELECT
        grade,
        COUNT(*) AS customer_count,
        ROUND(AVG(avg_order_value))  AS avg_order_value,
        ROUND(AVG(orders_per_year), 1) AS avg_annual_orders,
        ROUND(AVG(active_years), 1)    AS avg_active_years,
        ROUND(AVG(ltv))                AS avg_ltv
    FROM ltv_calc
    GROUP BY grade
    ORDER BY avg_ltv DESC;
    ```


---


### 6. 가입 채널별 고객 품질 비교


가입 채널(`acquisition_channel`)별로 고객 수, 평균 주문 횟수, 평균 구매 금액,
VIP/GOLD 전환율을 비교하세요.


**힌트 1:** - `customers.acquisition_channel`: organic/search_ad/social/referral/direct
- VIP/GOLD 전환율 = 해당 채널에서 VIP+GOLD 고객 수 / 전체 고객 수
- 주문이 없는 고객도 포함 (LEFT JOIN)



??? success "정답"
    ```sql
    WITH channel_stats AS (
        SELECT
            COALESCE(c.acquisition_channel, '미확인') AS channel,
            c.id AS customer_id,
            c.grade,
            COUNT(o.id) AS order_count,
            COALESCE(SUM(o.total_amount), 0) AS total_spent
        FROM customers AS c
        LEFT JOIN orders AS o
            ON c.id = o.customer_id
            AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.acquisition_channel, c.id, c.grade
    )
    SELECT
        channel,
        COUNT(*)                        AS customer_count,
        ROUND(AVG(order_count), 1)      AS avg_orders,
        ROUND(AVG(CASE WHEN total_spent > 0 THEN total_spent END)) AS avg_spent,
        ROUND(100.0 * SUM(CASE WHEN grade IN ('VIP', 'GOLD') THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS premium_rate_pct,
        ROUND(100.0 * SUM(CASE WHEN order_count = 0 THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS never_ordered_pct
    FROM channel_stats
    GROUP BY channel
    ORDER BY avg_spent DESC;
    ```


    **실행 결과** (5행)

    | channel | customer_count | avg_orders | avg_spent | premium_rate_pct | never_ordered_pct |
    |---|---|---|---|---|---|
    | organic | 1146 | 8.00 | 14,523,151.00 | 19.00 | 45.90 |
    | direct | 408 | 7.30 | 14,104,863.00 | 16.40 | 48.50 |
    | referral | 708 | 6.80 | 12,712,480.00 | 16.80 | 45.80 |
    | search_ad | 1543 | 6.40 | 11,875,351.00 | 17.30 | 45.70 |
    | social | 1425 | 5.60 | 10,755,623.00 | 15.50 | 48.00 |


---


### 7. 등급 변동 추적


`customer_grade_history` 테이블을 활용하여, 2024년에 등급이 상승한 고객과 하락한 고객의 수를 구하세요.
등급 변동 경로(예: SILVER→GOLD)별 건수도 표시합니다.


**힌트 1:** - `customer_grade_history`: `customer_id`, `old_grade`, `new_grade`, `changed_at`
- 등급 순서: BRONZE < SILVER < GOLD < VIP
- CASE문으로 등급에 숫자 부여 후 비교



??? success "정답"
    ```sql
    WITH grade_order AS (
        SELECT
            customer_id,
            old_grade,
            new_grade,
            changed_at,
            CASE old_grade WHEN 'BRONZE' THEN 1 WHEN 'SILVER' THEN 2 WHEN 'GOLD' THEN 3 WHEN 'VIP' THEN 4 END AS old_rank,
            CASE new_grade WHEN 'BRONZE' THEN 1 WHEN 'SILVER' THEN 2 WHEN 'GOLD' THEN 3 WHEN 'VIP' THEN 4 END AS new_rank
        FROM customer_grade_history
        WHERE changed_at LIKE '2024%'
    )
    SELECT
        old_grade || ' → ' || new_grade AS grade_change,
        CASE
            WHEN new_rank > old_rank THEN '승급'
            WHEN new_rank < old_rank THEN '강등'
            ELSE '유지'
        END AS direction,
        COUNT(*) AS change_count
    FROM grade_order
    GROUP BY old_grade, new_grade, direction
    ORDER BY
        CASE WHEN new_rank > old_rank THEN 1 WHEN new_rank < old_rank THEN 2 ELSE 3 END,
        change_count DESC;
    ```


    **실행 결과** (총 13행 중 상위 7행)

    | grade_change | direction | change_count |
    |---|---|---|
    | BRONZE → GOLD | 승급 | 167 |
    | BRONZE → SILVER | 승급 | 160 |
    | BRONZE → VIP | 승급 | 66 |
    | GOLD → VIP | 승급 | 63 |
    | SILVER → GOLD | 승급 | 52 |
    | SILVER → VIP | 승급 | 37 |
    | SILVER → BRONZE | 강등 | 125 |


---


### 8. ABC 재고 분류


현재 재고 금액(stock_qty x cost_price) 기준으로 상품을 ABC 분류하세요.
(A: 상위 70%, B: 70~90%, C: 나머지)
각 등급의 상품 수와 총 재고 금액을 표시합니다.


**힌트 1:** - 재고 금액 = `stock_qty * cost_price`
- 누적 비율로 ABC 분류 (매출 분석의 ABC와 동일 패턴)
- 활성 상품만 대상



??? success "정답"
    ```sql
    WITH inventory_value AS (
        SELECT
            p.id,
            p.name,
            p.stock_qty,
            p.cost_price,
            p.stock_qty * p.cost_price AS stock_value
        FROM products AS p
        WHERE p.is_active = 1
          AND p.stock_qty > 0
    ),
    cumulative AS (
        SELECT
            id, name, stock_qty, cost_price, stock_value,
            SUM(stock_value) OVER (ORDER BY stock_value DESC) AS cum_value,
            SUM(stock_value) OVER () AS total_value
        FROM inventory_value
    ),
    classified AS (
        SELECT *,
            CASE
                WHEN 100.0 * cum_value / total_value <= 70 THEN 'A'
                WHEN 100.0 * cum_value / total_value <= 90 THEN 'B'
                ELSE 'C'
            END AS abc_class
        FROM cumulative
    )
    SELECT
        abc_class,
        COUNT(*)                 AS product_count,
        ROUND(SUM(stock_value)) AS total_stock_value,
        ROUND(100.0 * SUM(stock_value) / (SELECT SUM(stock_value) FROM inventory_value), 1) AS value_pct,
        ROUND(AVG(stock_qty))    AS avg_stock_qty
    FROM classified
    GROUP BY abc_class
    ORDER BY abc_class;
    ```


    **실행 결과** (3행)

    | abc_class | product_count | total_stock_value | value_pct | avg_stock_qty |
    |---|---|---|---|---|
    | A | 46 | 20,873,678,400.00 | 69.50 | 337.00 |
    | B | 52 | 6,146,023,700.00 | 20.50 | 310.00 |
    | C | 119 | 3,010,558,600.00 | 10.00 | 233.00 |


---


### 9. 체류 재고(Dead Stock) 감지


최근 6개월간 한 건도 판매되지 않은 활성 상품을 찾으세요.
재고 수량, 재고 금액, 마지막 판매일을 표시합니다.


**힌트 1:** - `order_items` + `orders`에서 최근 6개월 주문 확인
- LEFT JOIN 후 주문이 NULL인 상품 = 판매 없음
- 또는 NOT EXISTS 패턴 활용



??? success "정답"
    ```sql
    WITH last_sale AS (
        SELECT
            oi.product_id,
            MAX(o.ordered_at) AS last_sold_at
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY oi.product_id
    )
    SELECT
        p.name         AS product_name,
        cat.name       AS category,
        p.stock_qty,
        ROUND(p.stock_qty * p.cost_price) AS stock_value,
        ls.last_sold_at,
        ROUND(JULIANDAY('2025-03-31') - JULIANDAY(ls.last_sold_at)) AS days_since_last_sale
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LEFT JOIN last_sale AS ls ON p.id = ls.product_id
    WHERE p.is_active = 1
      AND p.stock_qty > 0
      AND (ls.last_sold_at IS NULL OR ls.last_sold_at < DATE('2025-03-31', '-6 months'))
    ORDER BY stock_value DESC
    LIMIT 20;
    ```


---


### 10. 재주문 시점(Reorder Point) 계산


상품별 일평균 출고량을 기반으로 재주문 시점을 계산하세요.
재주문 시점 = 일평균 출고량 x 리드타임(7일) x 안전 계수(1.5)
현재 재고가 재주문 시점 이하인 상품을 찾습니다.


**힌트 1:** - 최근 3개월 출고량: `inventory_transactions`에서 `type = 'outbound'`
- 일평균 출고량 = 3개월 총 출고량 / 90
- 재주문 시점 = 일평균 출고량 x 7 x 1.5



??? success "정답"
    ```sql
    WITH daily_demand AS (
        SELECT
            product_id,
            ABS(SUM(quantity)) / 90.0 AS avg_daily_demand
        FROM inventory_transactions
        WHERE type = 'outbound'
          AND created_at >= DATE('2025-03-31', '-3 months')
        GROUP BY product_id
    ),
    reorder_calc AS (
        SELECT
            p.id,
            p.name,
            p.stock_qty,
            ROUND(dd.avg_daily_demand, 2) AS avg_daily_demand,
            ROUND(dd.avg_daily_demand * 7 * 1.5) AS reorder_point,
            ROUND(p.stock_qty / NULLIF(dd.avg_daily_demand, 0)) AS days_of_stock
        FROM products AS p
        INNER JOIN daily_demand AS dd ON p.id = dd.product_id
        WHERE p.is_active = 1
    )
    SELECT
        name AS product_name,
        stock_qty,
        avg_daily_demand,
        reorder_point,
        days_of_stock,
        CASE
            WHEN stock_qty <= reorder_point THEN '즉시 발주'
            WHEN days_of_stock <= 14 THEN '발주 예정'
            ELSE '충분'
        END AS order_status
    FROM reorder_calc
    WHERE stock_qty <= reorder_point
    ORDER BY days_of_stock ASC;
    ```


    **실행 결과** (1행)

    | product_name | stock_qty | avg_daily_demand | reorder_point | days_of_stock | order_status |
    |---|---|---|---|---|---|
    | Arctic Freezer 36 A-RGB 화이트 | 0 | 0.09 | 1.00 | 0.0 | 즉시 발주 |


---


### 11. 카테고리별 재고 회전율


카테고리별 재고 회전율을 계산하세요.
재고 회전율 = 연간 매출원가(COGS) / 평균 재고 금액


**힌트 1:** - 매출원가(COGS): `SUM(oi.quantity * p.cost_price)` (2024년 판매분)
- 평균 재고 금액: `AVG(stock_qty * cost_price)` (현재 시점)
- 회전율이 높을수록 재고가 빠르게 팔림



??? success "정답"
    ```sql
    WITH cogs_2024 AS (
        SELECT
            p.category_id,
            SUM(oi.quantity * p.cost_price) AS annual_cogs
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.category_id
    ),
    avg_inventory AS (
        SELECT
            category_id,
            AVG(stock_qty * cost_price) AS avg_stock_value,
            SUM(stock_qty * cost_price) AS total_stock_value,
            COUNT(*) AS product_count
        FROM products
        WHERE is_active = 1
        GROUP BY category_id
    )
    SELECT
        cat.name AS category,
        ai.product_count,
        ROUND(cg.annual_cogs) AS annual_cogs,
        ROUND(ai.total_stock_value) AS current_stock_value,
        ROUND(cg.annual_cogs / NULLIF(ai.avg_stock_value, 0), 1) AS turnover_rate,
        ROUND(365.0 / NULLIF(cg.annual_cogs / NULLIF(ai.avg_stock_value, 0), 0)) AS days_in_inventory
    FROM avg_inventory AS ai
    INNER JOIN cogs_2024 AS cg ON ai.category_id = cg.category_id
    INNER JOIN categories AS cat ON ai.category_id = cat.id
    ORDER BY turnover_rate DESC;
    ```


    **실행 결과** (총 38행 중 상위 7행)

    | category | product_count | annual_cogs | current_stock_value | turnover_rate | days_in_inventory |
    |---|---|---|---|---|---|
    | 유선 | 2 | 10,751,300.00 | 1,612,200.00 | 13.30 | 27.00 |
    | 케이스 | 10 | 103,892,500.00 | 261,356,300.00 | 4.00 | 92.00 |
    | 스피커/헤드셋 | 9 | 164,632,200.00 | 416,492,100.00 | 3.60 | 103.00 |
    | 게이밍 | 8 | 76,210,600.00 | 187,113,000.00 | 3.30 | 112.00 |
    | DDR5 | 8 | 115,931,100.00 | 308,598,300.00 | 3.00 | 121.00 |
    | DDR4 | 5 | 41,246,500.00 | 69,961,100.00 | 2.90 | 124.00 |
    | SSD | 6 | 122,676,700.00 | 258,240,800.00 | 2.90 | 128.00 |


---


### 12. 재고 입출고 월별 추이


2024년 월별 입고량, 출고량, 순변동량, 월말 누적 재고를 계산하세요.
전체 상품 합산 기준입니다.


**힌트 1:** - `inventory_transactions`의 `type`: inbound(양수), outbound(음수)
- 조건부 집계로 입고/출고 분리
- 누적 합: `SUM(...) OVER (ORDER BY year_month)`



??? success "정답"
    ```sql
    WITH monthly_flow AS (
        SELECT
            SUBSTR(created_at, 1, 7) AS year_month,
            SUM(CASE WHEN quantity > 0 THEN quantity ELSE 0 END) AS inbound_qty,
            SUM(CASE WHEN quantity < 0 THEN ABS(quantity) ELSE 0 END) AS outbound_qty,
            SUM(quantity) AS net_change
        FROM inventory_transactions
        WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
        GROUP BY SUBSTR(created_at, 1, 7)
    )
    SELECT
        year_month,
        inbound_qty,
        outbound_qty,
        net_change,
        SUM(net_change) OVER (ORDER BY year_month) AS cumulative_change
    FROM monthly_flow
    ORDER BY year_month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | year_month | inbound_qty | outbound_qty | net_change | cumulative_change |
    |---|---|---|---|---|
    | 2024-01 | 2007 | 199 | 1808 | 1808 |
    | 2024-02 | 943 | 163 | 780 | 2588 |
    | 2024-03 | 3536 | 248 | 3288 | 5876 |
    | 2024-04 | 3528 | 122 | 3406 | 9282 |
    | 2024-05 | 3408 | 253 | 3155 | 12,437 |
    | 2024-06 | 2688 | 171 | 2517 | 14,954 |
    | 2024-07 | 2900 | 138 | 2762 | 17,716 |


---


### 13. 문의 처리 시간 분석


2024년 문의 유형(category)별 평균 처리 시간, 중간값(근사), SLA 준수율을 구하세요.
SLA: 일반 문의 3일, 클레임 1일, 긴급 0.5일 이내 해결


**힌트 1:** - 처리 시간: `JULIANDAY(resolved_at) - JULIANDAY(created_at)`
- 중간값 근사: 50번째 백분위수 → `PERCENTILE` 대신 `NTILE` 활용
- SLA 기준을 `priority`에 따라 다르게 적용



??? success "정답"
    ```sql
    WITH resolution_times AS (
        SELECT
            category,
            priority,
            JULIANDAY(resolved_at) - JULIANDAY(created_at) AS resolution_days,
            CASE priority
                WHEN 'urgent' THEN 0.5
                WHEN 'high'   THEN 1.0
                WHEN 'medium' THEN 2.0
                ELSE 3.0
            END AS sla_days
        FROM complaints
        WHERE created_at LIKE '2024%'
          AND resolved_at IS NOT NULL
    )
    SELECT
        category,
        COUNT(*) AS resolved_count,
        ROUND(AVG(resolution_days), 2) AS avg_resolution_days,
        ROUND(MIN(resolution_days), 2) AS min_days,
        ROUND(MAX(resolution_days), 2) AS max_days,
        ROUND(100.0 * SUM(CASE WHEN resolution_days <= sla_days THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS sla_compliance_pct
    FROM resolution_times
    GROUP BY category
    ORDER BY sla_compliance_pct ASC;
    ```


    **실행 결과** (7행)

    | category | resolved_count | avg_resolution_days | min_days | max_days | sla_compliance_pct |
    |---|---|---|---|---|---|
    | general_inquiry | 195 | 1.92 | 0.04 | 4.00 | 76.90 |
    | exchange_request | 34 | 1.25 | 0.08 | 3.96 | 88.20 |
    | price_inquiry | 73 | 1.62 | 0.13 | 3.79 | 90.40 |
    | delivery_issue | 109 | 0.73 | 0.04 | 4.00 | 95.40 |
    | refund_request | 64 | 0.91 | 0.04 | 3.46 | 96.90 |
    | wrong_item | 40 | 0.78 | 0.08 | 3.21 | 97.50 |
    | product_defect | 69 | 0.7 | 0.04 | 3.46 | 98.60 |


---


### 14. 반품 사유 분석과 추이


2024년 반품 사유(reason)별 건수, 비율, 평균 환불 금액을 구하세요.
분기별 추이도 함께 확인합니다.


**힌트 1:** - `returns` 테이블: `reason`, `refund_amount`, `requested_at`
- 전체 비율 + 분기별 추이를 별도 쿼리로 작성



??? success "정답"
    ```sql
    -- 사유별 전체 통계
    SELECT
        reason,
        COUNT(*)                     AS return_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
        ROUND(AVG(refund_amount))    AS avg_refund,
        ROUND(SUM(refund_amount))    AS total_refund
    FROM returns
    WHERE requested_at >= '2024-01-01' AND requested_at < '2025-01-01'
    GROUP BY reason
    ORDER BY return_count DESC;
    
    -- 분기별 추이
    SELECT
        'Q' || ((CAST(SUBSTR(requested_at, 6, 2) AS INTEGER) + 2) / 3) AS quarter,
        reason,
        COUNT(*) AS return_count
    FROM returns
    WHERE requested_at >= '2024-01-01' AND requested_at < '2025-01-01'
    GROUP BY (CAST(SUBSTR(requested_at, 6, 2) AS INTEGER) + 2) / 3, reason
    ORDER BY quarter, return_count DESC;
    ```


---


### 15. CS 직원별 성과 비교


각 CS 직원의 담당 문의 건수, 해결률, 평균 처리 시간, 고객 만족도(compensation 없는 비율)를 비교하세요.
전체 평균과의 차이도 함께 표시합니다.


**힌트 1:** - `complaints.staff_id` → `staff` JOIN
- 윈도우 함수 `AVG(...) OVER ()`로 전체 평균을 같은 행에 표시
- 고객 만족도 대리 지표: compensation_type이 NULL 또는 'none'인 비율



??? success "정답"
    ```sql
    WITH staff_metrics AS (
        SELECT
            s.name AS staff_name,
            COUNT(*) AS case_count,
            SUM(CASE WHEN comp.status IN ('resolved', 'closed') THEN 1 ELSE 0 END) AS resolved_count,
            AVG(CASE
                WHEN comp.resolved_at IS NOT NULL
                THEN JULIANDAY(comp.resolved_at) - JULIANDAY(comp.created_at)
            END) AS avg_resolution_days,
            100.0 * SUM(CASE WHEN COALESCE(comp.compensation_type, 'none') = 'none' THEN 1 ELSE 0 END)
                / COUNT(*) AS no_compensation_pct
        FROM complaints AS comp
        INNER JOIN staff AS s ON comp.staff_id = s.id
        WHERE comp.created_at LIKE '2024%'
        GROUP BY s.id, s.name
    )
    SELECT
        staff_name,
        case_count,
        ROUND(100.0 * resolved_count / case_count, 1) AS resolution_rate,
        ROUND(avg_resolution_days, 2) AS avg_days,
        ROUND(no_compensation_pct, 1) AS satisfaction_proxy_pct,
        ROUND(AVG(case_count) OVER (), 1) AS team_avg_cases,
        ROUND(AVG(avg_resolution_days) OVER (), 2) AS team_avg_days
    FROM staff_metrics
    ORDER BY resolution_rate DESC;
    ```


    **실행 결과** (5행)

    | staff_name | case_count | resolution_rate | avg_days | satisfaction_proxy_pct | team_avg_cases | team_avg_days |
    |---|---|---|---|---|---|---|
    | 이준혁 | 123 | 95.10 | 1.36 | 67.50 | 123.20 | 1.29 |
    | 박경수 | 118 | 94.90 | 1.29 | 60.20 | 123.20 | 1.29 |
    | 장주원 | 115 | 94.80 | 1.32 | 63.50 | 123.20 | 1.29 |
    | 한민재 | 131 | 94.70 | 1.19 | 57.30 | 123.20 | 1.29 |
    | 권영희 | 129 | 94.60 | 1.29 | 72.10 | 123.20 | 1.29 |


---


### 16. 에스컬레이션 분석


에스컬레이션(escalated = 1)된 문의의 특성을 분석하세요.
어떤 유형, 채널, 우선순위에서 에스컬레이션이 많이 발생하는지 파악합니다.


**힌트 1:** - `complaints.escalated = 1`인 건
- 에스컬레이션 비율 = 에스컬레이션 건수 / 전체 건수
- 카테고리, 채널, 우선순위별로 각각 집계



??? success "정답"
    ```sql
    SELECT
        category,
        channel,
        priority,
        COUNT(*) AS total_count,
        SUM(escalated) AS escalated_count,
        ROUND(100.0 * SUM(escalated) / COUNT(*), 1) AS escalation_rate_pct,
        ROUND(AVG(CASE
            WHEN escalated = 1 AND resolved_at IS NOT NULL
            THEN JULIANDAY(resolved_at) - JULIANDAY(created_at)
        END), 2) AS escalated_avg_days
    FROM complaints
    WHERE created_at LIKE '2024%'
    GROUP BY category, channel, priority
    HAVING COUNT(*) >= 5
    ORDER BY escalation_rate_pct DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | category | channel | priority | total_count | escalated_count | escalation_rate_pct | escalated_avg_days |
    |---|---|---|---|---|---|---|
    | wrong_item | website | high | 8 | 3 | 37.50 | 0.4 |
    | product_defect | website | medium | 8 | 2 | 25.00 | 0.92 |
    | refund_request | phone | medium | 9 | 2 | 22.20 | 0.6 |
    | product_defect | email | medium | 5 | 1 | 20.00 | 0.33 |
    | product_defect | phone | urgent | 5 | 1 | 20.00 | 0.13 |
    | wrong_item | phone | medium | 5 | 1 | 20.00 | 1.04 |
    | exchange_request | website | medium | 6 | 1 | 16.70 | 1.33 |


---


### 17. 상품별 CS 발생률


매출 상위 30개 상품의 CS(문의+반품) 발생률을 구하세요.
CS 발생률이 높은 상품은 품질 개선이 필요합니다.


**힌트 1:** - 판매 건수 대비 문의/반품 발생 비율
- `order_items`에서 상품별 판매 건수
- `complaints` + `returns`에서 상품 관련 CS 건수
- complaints는 order_id → order_items → product_id로 연결



??? success "정답"
    ```sql
    WITH top_products AS (
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            SUM(oi.quantity) AS total_sold
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.status NOT IN ('cancelled')
          AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
        GROUP BY p.id, p.name
        ORDER BY total_sold DESC
        LIMIT 30
    ),
    complaint_counts AS (
        SELECT
            oi.product_id,
            COUNT(DISTINCT comp.id) AS complaint_count
        FROM complaints AS comp
        INNER JOIN orders AS o ON comp.order_id = o.id
        INNER JOIN order_items AS oi ON o.id = oi.order_id
        WHERE comp.created_at LIKE '2024%'
        GROUP BY oi.product_id
    ),
    return_counts AS (
        SELECT
            oi.product_id,
            COUNT(DISTINCT ret.id) AS return_count
        FROM returns AS ret
        INNER JOIN order_items AS oi ON ret.order_id = oi.order_id
        WHERE ret.requested_at LIKE '2024%'
        GROUP BY oi.product_id
    )
    SELECT
        tp.product_name,
        tp.total_sold,
        COALESCE(cc.complaint_count, 0) AS complaints,
        COALESCE(rc.return_count, 0) AS returns,
        COALESCE(cc.complaint_count, 0) + COALESCE(rc.return_count, 0) AS total_cs,
        ROUND(100.0 * (COALESCE(cc.complaint_count, 0) + COALESCE(rc.return_count, 0))
            / tp.total_sold, 1) AS cs_rate_pct
    FROM top_products AS tp
    LEFT JOIN complaint_counts AS cc ON tp.product_id = cc.product_id
    LEFT JOIN return_counts AS rc ON tp.product_id = rc.product_id
    ORDER BY cs_rate_pct DESC;
    ```


    **실행 결과** (총 30행 중 상위 7행)

    | product_name | total_sold | complaints | returns | total_cs | cs_rate_pct |
    |---|---|---|---|---|---|
    | SK하이닉스 Platinum P41 2TB 실버 | 183 | 22 | 9 | 31 | 16.90 |
    | Crucial T700 2TB 실버 | 173 | 17 | 9 | 26 | 15.00 |
    | Intel Core Ultra 7 265K 화이트 | 405 | 33 | 18 | 51 | 12.60 |
    | 로지텍 G715 | 240 | 21 | 9 | 30 | 12.50 |
    | Kingston FURY Beast DDR4 16GB 실버 | 170 | 15 | 6 | 21 | 12.40 |
    | Kingston FURY Renegade DDR5 32GB 7200... | 131 | 14 | 2 | 16 | 12.20 |
    | AMD Ryzen 9 9900X | 248 | 21 | 9 | 30 | 12.10 |


---


### 18. 일간 운영 대시보드


특정 날짜(2024-12-15)의 운영 현황을 한눈에 보여주는 대시보드를 만드세요.
당일 주문 수, 매출, 신규 가입자, 배송 완료, 미해결 CS 건수를 포함합니다.


**힌트 1:** - 각 지표를 스칼라 서브쿼리 또는 CTE로 계산
- `CROSS JOIN`으로 단일 행 결합
- 전일 대비 변화도 포함하면 더 유용



??? success "정답"
    ```sql
    WITH target_day AS (SELECT '2024-12-15' AS d),
    day_orders AS (
        SELECT
            COUNT(*) AS order_count,
            ROUND(SUM(total_amount)) AS revenue
        FROM orders, target_day
        WHERE DATE(ordered_at) = d
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    prev_orders AS (
        SELECT
            COUNT(*) AS order_count,
            ROUND(SUM(total_amount)) AS revenue
        FROM orders, target_day
        WHERE DATE(ordered_at) = DATE(d, '-1 day')
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    new_customers AS (
        SELECT COUNT(*) AS cnt
        FROM customers, target_day
        WHERE DATE(created_at) = d
    ),
    deliveries AS (
        SELECT COUNT(*) AS cnt
        FROM shipping, target_day
        WHERE DATE(delivered_at) = d
    ),
    open_cs AS (
        SELECT COUNT(*) AS cnt
        FROM complaints
        WHERE status = 'open'
    )
    SELECT
        (SELECT d FROM target_day) AS report_date,
        do.order_count AS today_orders,
        do.revenue AS today_revenue,
        po.order_count AS yesterday_orders,
        po.revenue AS yesterday_revenue,
        ROUND(100.0 * (do.revenue - po.revenue) / NULLIF(po.revenue, 0), 1) AS revenue_change_pct,
        nc.cnt AS new_signups,
        dl.cnt AS deliveries_completed,
        oc.cnt AS open_cs_tickets
    FROM day_orders AS do
    CROSS JOIN prev_orders AS po
    CROSS JOIN new_customers AS nc
    CROSS JOIN deliveries AS dl
    CROSS JOIN open_cs AS oc;
    ```


    **실행 결과** (1행)

    | report_date | today_orders | today_revenue | yesterday_orders | yesterday_revenue | revenue_change_pct | new_signups | deliveries_completed | open_cs_tickets |
    |---|---|---|---|---|---|---|---|---|
    | 2024-12-15 | 17 | 14,671,908.00 | 16 | 8,477,723.00 | 73.10 | 0 | 15 | 197 |


---


### 19. 공급업체 종합 평가


각 공급업체의 종합 성과를 평가하세요.
공급 상품 수, 총 매출, 반품률, 평균 리뷰 평점, 재고 적정성을 하나의 리포트로 통합합니다.


**힌트 1:** - `suppliers` → `products` → 각종 테이블 JOIN
- 반품률: 해당 공급업체 상품의 반품 수 / 판매 수
- 재고 적정성: 재고 과다(180일 이상 분량) 또는 부족(7일 이하)인 상품 비율



??? success "정답"
    ```sql
    WITH supplier_products AS (
        SELECT
            s.id AS supplier_id,
            s.company_name,
            COUNT(DISTINCT p.id) AS product_count,
            SUM(p.stock_qty) AS total_stock
        FROM suppliers AS s
        INNER JOIN products AS p ON s.id = p.supplier_id
        WHERE p.is_active = 1
        GROUP BY s.id, s.company_name
    ),
    supplier_sales AS (
        SELECT
            p.supplier_id,
            SUM(oi.quantity) AS total_sold,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS total_revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.supplier_id
    ),
    supplier_returns AS (
        SELECT
            p.supplier_id,
            COUNT(DISTINCT ret.id) AS return_count
        FROM returns AS ret
        INNER JOIN order_items AS oi ON ret.order_id = oi.order_id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE ret.requested_at >= '2024-01-01' AND ret.requested_at < '2025-01-01'
        GROUP BY p.supplier_id
    ),
    supplier_reviews AS (
        SELECT
            p.supplier_id,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(*) AS review_count
        FROM reviews AS r
        INNER JOIN products AS p ON r.product_id = p.id
        GROUP BY p.supplier_id
    )
    SELECT
        sp.company_name,
        sp.product_count,
        COALESCE(ss.total_revenue, 0) AS revenue_2024,
        COALESCE(ss.total_sold, 0) AS units_sold,
        ROUND(100.0 * COALESCE(sr.return_count, 0) / NULLIF(ss.total_sold, 0), 1) AS return_rate_pct,
        COALESCE(srv.avg_rating, 0) AS avg_rating,
        sp.total_stock
    FROM supplier_products AS sp
    LEFT JOIN supplier_sales AS ss ON sp.supplier_id = ss.supplier_id
    LEFT JOIN supplier_returns AS sr ON sp.supplier_id = sr.supplier_id
    LEFT JOIN supplier_reviews AS srv ON sp.supplier_id = srv.supplier_id
    ORDER BY revenue_2024 DESC;
    ```


    **실행 결과** (총 41행 중 상위 7행)

    | company_name | product_count | revenue_2024 | units_sold | return_rate_pct | avg_rating | total_stock |
    |---|---|---|---|---|---|---|
    | 에이수스코리아 | 21 | 794,354,100.00 | 828 | 4.00 | 3.88 | 5828 |
    | 레이저코리아 | 7 | 482,608,700.00 | 445 | 3.60 | 3.89 | 1742 |
    | LG전자 공식 유통 | 11 | 434,068,900.00 | 389 | 3.90 | 3.91 | 2667 |
    | 삼성전자 공식 유통 | 21 | 427,788,200.00 | 1012 | 3.50 | 3.90 | 6174 |
    | MSI코리아 | 12 | 372,284,800.00 | 632 | 3.00 | 3.97 | 4070 |
    | ASRock코리아 | 9 | 238,530,100.00 | 537 | 3.20 | 3.78 | 3084 |
    | 스틸시리즈코리아 | 7 | 209,711,600.00 | 983 | 3.70 | 3.87 | 1626 |


---


### 20. 월간 경영 종합 리포트 (2024년 12월)


2024년 12월의 경영 종합 리포트를 생성하세요.
매출, 고객, 재고, CS 네 영역의 핵심 KPI를 하나의 쿼리로 통합합니다.

| KPI 영역 | 지표 |
|---|---|
| 매출 | 월 매출, 전월비, 전년 동월비 |
| 고객 | 활성 고객 수, 신규 가입, 재구매율 |
| 재고 | 품절 상품 수, 재고 금액, 재고 부족 경고 수 |
| CS | 미해결 건수, 평균 처리 시간, 해결률 |


**힌트 1:** - 각 영역을 별도 CTE로 작성한 뒤 CROSS JOIN
- 전월비/전년 동월비는 서브쿼리로 비교 기간 매출 계산
- 재구매율: 해당 월 주문 고객 중 이전에도 주문한 고객 비율



??? success "정답"
    ```sql
    WITH sales_kpi AS (
        SELECT
            ROUND(SUM(CASE WHEN ordered_at LIKE '2024-12%' THEN total_amount ELSE 0 END)) AS dec_revenue,
            ROUND(SUM(CASE WHEN ordered_at LIKE '2024-11%' THEN total_amount ELSE 0 END)) AS nov_revenue,
            ROUND(SUM(CASE WHEN ordered_at LIKE '2023-12%' THEN total_amount ELSE 0 END)) AS dec_2023_revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND (ordered_at LIKE '2024-12%' OR ordered_at LIKE '2024-11%' OR ordered_at LIKE '2023-12%')
    ),
    customer_kpi AS (
        SELECT
            COUNT(DISTINCT CASE WHEN o.ordered_at LIKE '2024-12%' THEN o.customer_id END) AS active_customers,
            (SELECT COUNT(*) FROM customers WHERE created_at LIKE '2024-12%') AS new_signups,
            ROUND(100.0 * COUNT(DISTINCT CASE
                WHEN o.ordered_at LIKE '2024-12%'
                AND o.customer_id IN (
                    SELECT customer_id FROM orders
                    WHERE ordered_at < '2024-12-01'
                      AND status NOT IN ('cancelled', 'returned', 'return_requested')
                )
                THEN o.customer_id
            END) / NULLIF(COUNT(DISTINCT CASE WHEN o.ordered_at LIKE '2024-12%' THEN o.customer_id END), 0), 1)
                AS repeat_rate_pct
        FROM orders AS o
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    inventory_kpi AS (
        SELECT
            SUM(CASE WHEN stock_qty = 0 THEN 1 ELSE 0 END) AS out_of_stock_count,
            ROUND(SUM(stock_qty * cost_price)) AS total_stock_value,
            SUM(CASE WHEN stock_qty > 0 AND stock_qty <= 10 THEN 1 ELSE 0 END) AS low_stock_warning
        FROM products
        WHERE is_active = 1
    ),
    cs_kpi AS (
        SELECT
            SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open_tickets,
            ROUND(AVG(CASE
                WHEN resolved_at IS NOT NULL AND created_at LIKE '2024-12%'
                THEN JULIANDAY(resolved_at) - JULIANDAY(created_at)
            END), 2) AS avg_resolution_days,
            ROUND(100.0 * SUM(CASE
                WHEN created_at LIKE '2024-12%' AND status IN ('resolved', 'closed') THEN 1 ELSE 0 END)
                / NULLIF(SUM(CASE WHEN created_at LIKE '2024-12%' THEN 1 ELSE 0 END), 0), 1)
                AS resolution_rate_pct
        FROM complaints
    )
    SELECT
        '2024-12' AS report_month,
        -- 매출
        sk.dec_revenue,
        ROUND(100.0 * (sk.dec_revenue - sk.nov_revenue) / NULLIF(sk.nov_revenue, 0), 1) AS mom_growth_pct,
        ROUND(100.0 * (sk.dec_revenue - sk.dec_2023_revenue) / NULLIF(sk.dec_2023_revenue, 0), 1) AS yoy_growth_pct,
        -- 고객
        ck.active_customers,
        ck.new_signups,
        ck.repeat_rate_pct,
        -- 재고
        ik.out_of_stock_count,
        ik.total_stock_value,
        ik.low_stock_warning,
        -- CS
        csk.open_tickets,
        csk.avg_resolution_days,
        csk.resolution_rate_pct
    FROM sales_kpi AS sk
    CROSS JOIN customer_kpi AS ck
    CROSS JOIN inventory_kpi AS ik
    CROSS JOIN cs_kpi AS csk;
    ```


    **실행 결과** (1행)

    | report_month | dec_revenue | mom_growth_pct | yoy_growth_pct | active_customers | new_signups | repeat_rate_pct | out_of_stock_count | total_stock_value | low_stock_warning | open_tickets | avg_resolution_days | resolution_rate_pct |
    |---|---|---|---|---|---|---|---|---|---|---|---|---|
    | 2024-12 | 417,148,762.00 | -23.20 | 14.90 | 379 | 59 | 90.20 | 1 | 30,030,260,700.00 | 2 | 197 | 1.39 | 91.70 |


---
