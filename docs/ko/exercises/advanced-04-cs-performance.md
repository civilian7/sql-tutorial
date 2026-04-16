# CS 성과 분석

!!! info "사용 테이블"

    `complaints` — 고객 불만 (유형, 우선순위)  

    `staff` — 직원 (부서, 역할, 관리자)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `returns` — 반품/교환 (사유, 상태)  



!!! abstract "학습 범위"

    `JULIANDAY`, `CASE`, `Window Functions`, `CTE`, `Pivot`



### 1. 문의 유형별 현황


CS팀장이 최근 1년(2025년) 문의 현황을 파악하고 싶어합니다.
문의 유형(category)별로 건수, 해결률, 평균 처리 시간을 보여주세요.


**힌트 1:** - `complaints` 테이블의 `category`, `status`, `created_at`, `resolved_at` 사용
- 해결률: `status IN ('resolved', 'closed')` 건수 / 전체 건수
- 처리 시간: `JULIANDAY(resolved_at) - JULIANDAY(created_at)`



??? success "정답"
    ```sql
    SELECT
        category,
        COUNT(*) AS total_count,
        SUM(CASE WHEN status IN ('resolved', 'closed') THEN 1 ELSE 0 END)
            AS resolved_count,
        ROUND(100.0 * SUM(CASE WHEN status IN ('resolved', 'closed') THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS resolution_rate_pct,
        ROUND(AVG(CASE
            WHEN resolved_at IS NOT NULL
            THEN JULIANDAY(resolved_at) - JULIANDAY(created_at)
        END), 1) AS avg_resolution_days
    FROM complaints
    WHERE created_at LIKE '2025%'
    GROUP BY category
    ORDER BY total_count DESC;
    ```


    **실행 결과** (7행)

    | category | total_count | resolved_count | resolution_rate_pct | avg_resolution_days |
    |---|---|---|---|---|
    | general_inquiry | 378 | 356 | 94.20 | 2.00 |
    | price_inquiry | 140 | 129 | 92.10 | 1.80 |
    | delivery_issue | 135 | 130 | 96.30 | 0.7 |
    | refund_request | 92 | 87 | 94.60 | 0.7 |
    | product_defect | 74 | 70 | 94.60 | 0.7 |
    | wrong_item | 42 | 41 | 97.60 | 0.4 |
    | exchange_request | 34 | 34 | 100.00 | 1.20 |


---


### 2. CS 직원별 성과 비교


각 직원이 담당한 문의 건수, 해결률, 평균 처리 시간, 담당 고객 수를 보여주세요.
전체 평균과 비교할 수 있도록 표시합니다.


**힌트 1:** - `complaints.staff_id` -> `staff` JOIN
- `staff_id`가 NULL인 문의는 "미배정"으로 표시
- 윈도우 함수로 전체 평균을 같은 행에 표시



??? success "정답"
    ```sql
    WITH staff_metrics AS (
        SELECT
            COALESCE(s.name, '미배정') AS staff_name,
            COUNT(*) AS case_count,
            COUNT(DISTINCT comp.customer_id) AS customer_count,
            SUM(CASE WHEN comp.status IN ('resolved', 'closed') THEN 1 ELSE 0 END)
                AS resolved_count,
            ROUND(100.0 * SUM(CASE WHEN comp.status IN ('resolved', 'closed') THEN 1 ELSE 0 END)
                / COUNT(*), 1) AS resolution_rate,
            ROUND(AVG(CASE
                WHEN comp.resolved_at IS NOT NULL
                THEN JULIANDAY(comp.resolved_at) - JULIANDAY(comp.created_at)
            END), 1) AS avg_days
        FROM complaints AS comp
        LEFT JOIN staff AS s ON comp.staff_id = s.id
        WHERE comp.created_at LIKE '2025%'
        GROUP BY COALESCE(s.name, '미배정')
    )
    SELECT
        staff_name,
        case_count,
        customer_count,
        resolution_rate,
        avg_days,
        ROUND(AVG(case_count) OVER (), 0)       AS team_avg_cases,
        ROUND(AVG(resolution_rate) OVER (), 1)   AS team_avg_rate,
        ROUND(AVG(avg_days) OVER (), 1)          AS team_avg_days
    FROM staff_metrics
    ORDER BY resolution_rate DESC;
    ```


    **실행 결과** (5행)

    | staff_name | case_count | customer_count | resolution_rate | avg_days | team_avg_cases | team_avg_rate | team_avg_days |
    |---|---|---|---|---|---|---|---|
    | 한민재 | 178 | 167 | 96.10 | 1.30 | 179.00 | 94.60 | 1.40 |
    | 장주원 | 183 | 178 | 95.60 | 1.50 | 179.00 | 94.60 | 1.40 |
    | 권영희 | 177 | 174 | 94.90 | 1.60 | 179.00 | 94.60 | 1.40 |
    | 이준혁 | 183 | 175 | 93.40 | 1.30 | 179.00 | 94.60 | 1.40 |
    | 박경수 | 174 | 168 | 93.10 | 1.50 | 179.00 | 94.60 | 1.40 |


---


### 3. 반품 사유 분석


반품 사유별 건수, 비율, 평균 환불 금액을 보여주세요.
카테고리별로 어떤 사유가 많은지도 분석합니다.


**힌트 1:** - `returns.reason`으로 사유 분류
- `returns` -> `orders` -> `order_items` -> `products` -> `categories` JOIN
- `returns.refund_amount`로 환불 금액 계산



??? success "정답"
    ```sql
    SELECT
        r.reason,
        COUNT(*)                     AS return_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
        ROUND(AVG(r.refund_amount), 2) AS avg_refund
    FROM returns AS r
    GROUP BY r.reason
    ORDER BY return_count DESC;
    ```


    **실행 결과** (6행)

    | reason | return_count | pct | avg_refund |
    |---|---|---|---|
    | change_of_mind | 343 | 34.30 | 1,160,924.02 |
    | defective | 263 | 26.30 | 1,278,164.64 |
    | damaged_in_transit | 165 | 16.50 | 1,043,268.48 |
    | wrong_item | 95 | 9.50 | 1,128,795.79 |
    | not_as_described | 88 | 8.80 | 1,290,557.95 |
    | late_delivery | 46 | 4.60 | 741,530.43 |


---


### 4. 월별 CS 트렌드와 주문 대비 문의 비율


2024년 월별 주문 수, 문의 수, 반품 수, 주문 대비 문의율(%)을 보여주세요.


**힌트 1:** - 각 테이블에서 월별 건수를 CTE로 준비
- 월(SUBSTR)로 JOIN
- 문의율 = 문의 수 / 주문 수 * 100



??? success "정답"
    ```sql
    WITH monthly_orders AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            COUNT(*) AS order_count
        FROM orders
        WHERE ordered_at LIKE '2024%'
        GROUP BY SUBSTR(ordered_at, 1, 7)
    ),
    monthly_complaints AS (
        SELECT
            SUBSTR(created_at, 1, 7) AS year_month,
            COUNT(*) AS complaint_count
        FROM complaints
        WHERE created_at LIKE '2024%'
        GROUP BY SUBSTR(created_at, 1, 7)
    ),
    monthly_returns AS (
        SELECT
            SUBSTR(requested_at, 1, 7) AS year_month,
            COUNT(*) AS return_count
        FROM returns
        WHERE requested_at LIKE '2024%'
        GROUP BY SUBSTR(requested_at, 1, 7)
    )
    SELECT
        mo.year_month,
        mo.order_count,
        COALESCE(mc.complaint_count, 0) AS complaint_count,
        COALESCE(mr.return_count, 0)    AS return_count,
        ROUND(100.0 * COALESCE(mc.complaint_count, 0) / mo.order_count, 2)
            AS complaint_rate_pct,
        ROUND(100.0 * COALESCE(mr.return_count, 0) / mo.order_count, 2)
            AS return_rate_pct
    FROM monthly_orders AS mo
    LEFT JOIN monthly_complaints AS mc ON mo.year_month = mc.year_month
    LEFT JOIN monthly_returns    AS mr ON mo.year_month = mr.year_month
    ORDER BY mo.year_month;
    ```


    **실행 결과** (총 12행 중 상위 7행)

    | year_month | order_count | complaint_count | return_count | complaint_rate_pct | return_rate_pct |
    |---|---|---|---|---|---|
    | 2024-01 | 346 | 43 | 9 | 12.43 | 2.60 |
    | 2024-02 | 465 | 40 | 14 | 8.60 | 3.01 |
    | 2024-03 | 601 | 50 | 23 | 8.32 | 3.83 |
    | 2024-04 | 506 | 61 | 12 | 12.06 | 2.37 |
    | 2024-05 | 415 | 47 | 10 | 11.33 | 2.41 |
    | 2024-06 | 415 | 49 | 11 | 11.81 | 2.65 |
    | 2024-07 | 414 | 49 | 6 | 11.84 | 1.45 |


---


### 5. 반복 문의 고객과 에스컬레이션 대상


3회 이상 문의한 고객 중 미해결 건이 있는 경우를 에스컬레이션 대상으로 분류하세요.
총 문의 수, 미해결 건수, 총 구매 금액, 마지막 문의일을 보여주세요.


**힌트 1:** - 고객별 문의 통계를 먼저 집계
- `HAVING`으로 3회 이상 + 미해결 건 존재 필터
- `orders`와 JOIN하여 구매 금액 포함



??? success "정답"
    ```sql
    WITH complaint_summary AS (
        SELECT
            customer_id,
            COUNT(*) AS total_complaints,
            SUM(CASE WHEN status NOT IN ('resolved', 'closed') THEN 1 ELSE 0 END)
                AS open_count,
            MAX(created_at) AS last_complaint_date
        FROM complaints
        GROUP BY customer_id
        HAVING COUNT(*) >= 3
           AND SUM(CASE WHEN status NOT IN ('resolved', 'closed') THEN 1 ELSE 0 END) > 0
    ),
    customer_value AS (
        SELECT
            customer_id,
            ROUND(SUM(total_amount), 2) AS total_spent
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    )
    SELECT
        c.name          AS customer_name,
        c.grade,
        c.email,
        cs.total_complaints,
        cs.open_count,
        cs.last_complaint_date,
        COALESCE(cv.total_spent, 0) AS total_spent,
        CASE
            WHEN c.grade IN ('VIP', 'GOLD') THEN '우선 처리'
            WHEN cs.open_count >= 3          THEN '긴급'
            ELSE '일반'
        END AS priority
    FROM complaint_summary AS cs
    INNER JOIN customers     AS c  ON cs.customer_id = c.id
    LEFT  JOIN customer_value AS cv ON cs.customer_id = cv.customer_id
    ORDER BY
        CASE
            WHEN c.grade IN ('VIP', 'GOLD') THEN 1
            WHEN cs.open_count >= 3          THEN 2
            ELSE 3
        END,
        cv.total_spent DESC;
    ```


    **실행 결과** (총 91행 중 상위 7행)

    | customer_name | grade | email | total_complaints | open_count | last_complaint_date | total_spent | priority |
    |---|---|---|---|---|---|---|---|
    | 강명자 | VIP | user162@testmail.kr | 24 | 1 | 2025-03-25 05:20:31 | 254,525,838.00 | 우선 처리 |
    | 정유진 | VIP | user356@testmail.kr | 19 | 2 | 2024-08-28 10:20:59 | 248,498,783.00 | 우선 처리 |
    | 이영자 | VIP | user98@testmail.kr | 29 | 1 | 2024-10-07 08:05:39 | 248,168,491.00 | 우선 처리 |
    | 김성민 | VIP | user227@testmail.kr | 13 | 1 | 2025-05-10 11:44:37 | 244,859,844.00 | 우선 처리 |
    | 김영길 | GOLD | user1581@testmail.kr | 11 | 1 | 2025-08-30 11:40:39 | 208,621,108.00 | 우선 처리 |
    | 이영철 | VIP | user33@testmail.kr | 11 | 1 | 2023-08-06 03:15:06 | 174,223,341.00 | 우선 처리 |
    | 김민재 | VIP | user3@testmail.kr | 9 | 1 | 2025-12-09 09:46:23 | 164,856,056.00 | 우선 처리 |


---


### 6. 보너스: CS 직원별 월별 성과 피벗


CS 직원별 2024년 월별 해결 건수를 피벗 테이블로 만드세요.
12개월(열) x 직원(행) 형태입니다.


**힌트 1:** - 12개 `SUM(CASE WHEN SUBSTR(...) = 'MM' AND status ... THEN 1 ELSE 0 END)` 칼럼
- `LEFT JOIN staff`으로 미배정 포함



??? success "정답"
    ```sql
    SELECT
        COALESCE(s.name, '미배정') AS staff_name,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='01' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS jan,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='02' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS feb,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='03' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS mar,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='04' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS apr,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='05' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS may,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='06' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS jun,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='07' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS jul,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='08' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS aug,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='09' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS sep,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='10' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS oct,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='11' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS nov,
        SUM(CASE WHEN SUBSTR(comp.created_at,6,2)='12' AND comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS dec,
        SUM(CASE WHEN comp.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS total
    FROM complaints AS comp
    LEFT JOIN staff AS s ON comp.staff_id = s.id
    WHERE comp.created_at LIKE '2024%'
    GROUP BY COALESCE(s.name, '미배정')
    ORDER BY total DESC;
    ```


    **실행 결과** (5행)

    | staff_name | jan | feb | mar | apr | may | jun | jul | aug | sep | oct | nov | dec | total |
    |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
    | 한민재 | 7 | 9 | 11 | 11 | 12 | 6 | 15 | 14 | 8 | 8 | 14 | 9 | 124 |
    | 권영희 | 9 | 8 | 12 | 12 | 8 | 10 | 8 | 7 | 17 | 13 | 13 | 5 | 122 |
    | 이준혁 | 8 | 10 | 6 | 9 | 8 | 11 | 7 | 14 | 13 | 13 | 8 | 10 | 117 |
    | 박경수 | 6 | 10 | 6 | 14 | 7 | 9 | 10 | 10 | 9 | 10 | 12 | 9 | 112 |
    | 장주원 | 12 | 2 | 10 | 13 | 10 | 11 | 8 | 4 | 12 | 6 | 10 | 11 | 109 |


---
