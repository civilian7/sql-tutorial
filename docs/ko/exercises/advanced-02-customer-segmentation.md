# 고객 세분화

!!! info "사용 테이블"

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `reviews` — 리뷰 (평점, 내용)  



!!! abstract "학습 범위"

    `RFM`, `NTILE`, `Window Functions`, `CTE`, `Cohort Analysis`, `JULIANDAY`



### 1. RFM 기초: 고객별 핵심 지표 산출


마케팅팀이 고객 세분화를 위해 각 고객의 RFM(Recency, Frequency, Monetary) 지표를 요청했습니다.
고객별로 마지막 주문일, 총 주문 횟수, 총 구매 금액을 구하세요.
취소/반품 주문은 제외합니다.


**힌트 1:** - `MAX(ordered_at)`으로 최근 구매일(Recency) 계산
- `COUNT(*)`로 구매 빈도(Frequency), `SUM(total_amount)`로 구매 금액(Monetary)
- 결과를 총 구매 금액 내림차순으로 정렬



??? success "정답"
    ```sql
    SELECT
        c.id            AS customer_id,
        c.name          AS customer_name,
        c.grade,
        MAX(o.ordered_at)   AS last_order_date,
        COUNT(*)            AS order_count,
        ROUND(SUM(o.total_amount), 2) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 20;
    ```


---


### 2. RFM 4분위 세그먼트


RFM 지표를 기반으로 고객을 4분위(상위 25%, 50%, 75%, 하위)로 나누세요.
Recency는 최근일수록 높은 점수, Frequency와 Monetary는 클수록 높은 점수입니다.


**힌트 1:** - `NTILE(4)`로 각 지표를 4분위로 나누기
- Recency는 `ORDER BY last_order_date ASC` (NTILE 4가 가장 최근)
- Frequency, Monetary는 `ORDER BY ... ASC` (NTILE 4가 가장 큼)
- CTE를 단계적으로 사용



??? success "정답"
    ```sql
    WITH rfm_raw AS (
        SELECT
            c.id AS customer_id,
            c.name,
            c.grade,
            MAX(o.ordered_at)       AS last_order_date,
            COUNT(*)                AS frequency,
            ROUND(SUM(o.total_amount), 2) AS monetary
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    ),
    rfm_scored AS (
        SELECT
            customer_id, name, grade,
            last_order_date, frequency, monetary,
            NTILE(4) OVER (ORDER BY last_order_date ASC)  AS r_score,
            NTILE(4) OVER (ORDER BY frequency ASC)        AS f_score,
            NTILE(4) OVER (ORDER BY monetary ASC)         AS m_score
        FROM rfm_raw
    )
    SELECT
        customer_id, name, grade,
        last_order_date, frequency, monetary,
        r_score, f_score, m_score,
        r_score + f_score + m_score AS rfm_total
    FROM rfm_scored
    ORDER BY rfm_total DESC
    LIMIT 20;
    ```


---


### 3. 이탈 위험 고객 감지


CRM팀이 이탈 위험이 높은 고객 목록을 요청했습니다.
과거 5회 이상 구매했지만, 마지막 주문이 1년 이상 전인 고객을 찾아주세요.
마지막 주문일, 총 구매 횟수, 총 구매 금액, 마지막 주문 이후 경과 일수를 표시합니다.


**힌트 1:** - `JULIANDAY('2025-12-31') - JULIANDAY(MAX(ordered_at))`으로 경과 일수 계산
- `HAVING`으로 주문 횟수 >= 5 필터
- 경과 일수 >= 365 조건 추가



??? success "정답"
    ```sql
    SELECT
        c.id            AS customer_id,
        c.name,
        c.grade,
        c.email,
        MAX(o.ordered_at)   AS last_order_date,
        COUNT(*)            AS order_count,
        ROUND(SUM(o.total_amount), 2) AS total_spent,
        CAST(JULIANDAY('2025-12-31') - JULIANDAY(MAX(o.ordered_at)) AS INTEGER)
            AS days_since_last_order
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY c.id, c.name, c.grade, c.email
    HAVING COUNT(*) >= 5
       AND JULIANDAY('2025-12-31') - JULIANDAY(MAX(o.ordered_at)) >= 365
    ORDER BY total_spent DESC;
    ```


---


### 4. 등급별 행동 패턴 비교


고객 등급(VIP, GOLD, SILVER, BRONZE)별로 구매 행동이 어떻게 다른지 분석하세요.
등급별 평균 주문 금액, 평균 주문 횟수, 리뷰 작성률, 평균 리뷰 평점을 비교합니다.


**힌트 1:** - 주문 통계와 리뷰 통계를 각각 CTE로 준비
- 리뷰 작성률 = 리뷰 작성 고객 수 / 전체 고객 수
- 등급별 `GROUP BY`



??? success "정답"
    ```sql
    WITH order_stats AS (
        SELECT
            c.grade,
            COUNT(DISTINCT c.id) AS customer_count,
            COUNT(o.id)          AS total_orders,
            ROUND(AVG(o.total_amount), 2)        AS avg_order_value,
            ROUND(1.0 * COUNT(o.id) / COUNT(DISTINCT c.id), 1) AS avg_orders_per_customer
        FROM customers AS c
        LEFT JOIN orders AS o
            ON c.id = o.customer_id
           AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.grade
    ),
    review_stats AS (
        SELECT
            c.grade,
            COUNT(DISTINCT r.customer_id) AS reviewers,
            ROUND(AVG(r.rating), 2)       AS avg_rating
        FROM customers AS c
        LEFT JOIN reviews AS r ON c.id = r.customer_id
        GROUP BY c.grade
    )
    SELECT
        os.grade,
        os.customer_count,
        os.avg_orders_per_customer,
        os.avg_order_value,
        rs.reviewers,
        ROUND(100.0 * rs.reviewers / os.customer_count, 1) AS review_rate_pct,
        rs.avg_rating
    FROM order_stats AS os
    INNER JOIN review_stats AS rs ON os.grade = rs.grade
    ORDER BY
        CASE os.grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
            ELSE 5
        END;
    ```


---


### 5. 코호트 분석: 가입 연도별 잔존율


가입 연도별로 고객 수와, 가입 후 1년/2년 이내에 재구매한 고객 비율을 보여주세요.


**힌트 1:** - 고객별 가입 연도 = `SUBSTR(created_at, 1, 4)`
- 재구매 여부: 가입 연도 이후 1년/2년 이내 주문 존재 여부 확인
- 조건부 집계 `COUNT(DISTINCT CASE WHEN ... THEN customer_id END)`



??? success "정답"
    ```sql
    WITH cohort AS (
        SELECT
            id AS customer_id,
            SUBSTR(created_at, 1, 4) AS join_year,
            created_at
        FROM customers
    ),
    cohort_orders AS (
        SELECT
            co.customer_id,
            co.join_year,
            co.created_at AS join_date,
            o.ordered_at
        FROM cohort AS co
        INNER JOIN orders AS o ON co.customer_id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        join_year,
        COUNT(DISTINCT customer_id) AS cohort_size,
        COUNT(DISTINCT CASE
            WHEN ordered_at <= DATE(join_date, '+1 year') THEN customer_id
        END) AS active_year_1,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN ordered_at <= DATE(join_date, '+1 year') THEN customer_id
        END) / COUNT(DISTINCT customer_id), 1) AS retention_1y_pct,
        COUNT(DISTINCT CASE
            WHEN ordered_at > DATE(join_date, '+1 year')
             AND ordered_at <= DATE(join_date, '+2 years') THEN customer_id
        END) AS active_year_2,
        ROUND(100.0 * COUNT(DISTINCT CASE
            WHEN ordered_at > DATE(join_date, '+1 year')
             AND ordered_at <= DATE(join_date, '+2 years') THEN customer_id
        END) / COUNT(DISTINCT customer_id), 1) AS retention_2y_pct
    FROM cohort_orders
    GROUP BY join_year
    HAVING CAST(join_year AS INTEGER) <= 2023
    ORDER BY join_year;
    ```


---


### 6. 보너스: RFM 마케팅 세그먼트


RFM 점수를 활용하여 고객을 5개 마케팅 세그먼트로 분류하세요:
챔피언(R>=3,F>=3,M>=3), 충성고객(F>=3,M>=3),
잠재충성(R>=3,F<=2), 이탈위험(R<=2,F>=2), 휴면(R=1,F=1).
각 세그먼트의 고객 수와 평균 구매 금액을 구하세요.


**힌트 1:** - 먼저 RFM 점수를 계산하는 CTE 작성
- `CASE` 문으로 세그먼트 분류 (조건 순서 중요)
- 세그먼트별 `GROUP BY`



??? success "정답"
    ```sql
    WITH rfm_raw AS (
        SELECT
            c.id AS customer_id,
            MAX(o.ordered_at)       AS last_order_date,
            COUNT(*)                AS frequency,
            SUM(o.total_amount)     AS monetary
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id
    ),
    rfm_scored AS (
        SELECT
            customer_id, frequency, monetary,
            NTILE(4) OVER (ORDER BY last_order_date ASC)  AS r,
            NTILE(4) OVER (ORDER BY frequency ASC)        AS f,
            NTILE(4) OVER (ORDER BY monetary ASC)         AS m
        FROM rfm_raw
    ),
    segmented AS (
        SELECT *,
            CASE
                WHEN r >= 3 AND f >= 3 AND m >= 3 THEN '챔피언'
                WHEN f >= 3 AND m >= 3             THEN '충성 고객'
                WHEN r >= 3 AND f <= 2             THEN '잠재 충성'
                WHEN r <= 2 AND f >= 2             THEN '이탈 위험'
                WHEN r = 1  AND f = 1              THEN '휴면'
                ELSE '기타'
            END AS segment
        FROM rfm_scored
    )
    SELECT
        segment,
        COUNT(*)                        AS customer_count,
        ROUND(AVG(monetary), 2)         AS avg_monetary,
        ROUND(AVG(frequency), 1)        AS avg_frequency
    FROM segmented
    GROUP BY segment
    ORDER BY avg_monetary DESC;
    ```


---
