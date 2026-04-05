# 연습 문제: CS 성과 분석

고객 서비스(CS) 데이터를 분석하여 CS팀의 성과를 측정하고 개선 포인트를 찾습니다. 응대 현황, 직원 성과, 반품 패턴, 고객 만족도 등 CS 운영 관점의 다섯 가지 질문에 도전해 보세요.

---

## 질문 1 — 문의 유형별 현황

**비즈니스 질문:** CS팀장이 최근 1년(2025년) 문의 현황을 파악하고 싶어합니다. 문의 유형(category)별로 건수, 해결률(resolved/closed 비율), 평균 처리 시간(생성~해결)을 보여주세요.

**힌트:**

- `complaints` 테이블의 `category`, `status`, `created_at`, `resolved_at` 사용
- 해결률: `status IN ('resolved', 'closed')` 건수 / 전체 건수
- 처리 시간: `JULIANDAY(resolved_at) - JULIANDAY(created_at)`
- `resolved_at`이 NULL인 경우 미해결

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

    **예상 인사이트:** '배송 문의'가 가장 많고, '환불 요청'은 건수는 적지만 처리 시간이 가장 깁니다. 해결률이 낮은 유형은 프로세스 개선이 필요합니다.

---

## 질문 2 — CS 직원별 성과 비교

**비즈니스 질문:** 인사팀이 CS 직원의 개인별 성과를 비교하고 싶어합니다. 각 직원이 담당한 문의 건수, 해결률, 평균 처리 시간, 담당 고객 수를 보여주세요. 전체 평균과 비교할 수 있도록 표시합니다.

**힌트:**

- `complaints.staff_id` → `staff` JOIN
- `staff_id`가 NULL인 문의는 "미배정"으로 표시
- 윈도우 함수로 전체 평균을 같은 행에 표시 가능

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

    **예상 인사이트:** 해결률이 높고 처리 시간이 짧은 직원이 최고 성과자입니다. 미배정 건이 많다면 자동 배정 시스템 도입을 고려해야 합니다.

---

## 질문 3 — 반품 사유 분석

**비즈니스 질문:** 품질관리팀이 반품 사유를 분석하여 개선 방향을 찾고 싶어합니다. 반품 사유별 건수, 비율, 평균 환불 금액을 보여주세요. 카테고리별로 어떤 사유가 많은지도 분석합니다.

**힌트:**

- `returns.reason`으로 사유 분류
- `returns` → `orders` → `order_items` → `products` → `categories` JOIN
- `returns.refund_amount`로 환불 금액 계산

??? success "정답"
    ```sql
    -- 전체 반품 사유별 요약
    SELECT
        r.reason,
        COUNT(*)                     AS return_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
        ROUND(AVG(r.refund_amount), 2) AS avg_refund
    FROM returns AS r
    GROUP BY r.reason
    ORDER BY return_count DESC;
    ```

    **카테고리별 상세 분석:**

    ```sql
    SELECT
        cat.name AS category,
        r.reason,
        COUNT(*) AS return_count,
        ROUND(AVG(r.refund_amount), 2) AS avg_refund
    FROM returns AS r
    INNER JOIN orders      AS o   ON r.order_id   = o.id
    INNER JOIN order_items AS oi  ON o.id = oi.order_id
    INNER JOIN products    AS p   ON oi.product_id = p.id
    INNER JOIN categories  AS cat ON p.category_id = cat.id
    GROUP BY cat.name, r.reason
    HAVING return_count >= 3
    ORDER BY cat.name, return_count DESC;
    ```

    **예상 인사이트:** "불량/결함"이 가장 흔한 사유일 것이며, 고가 카테고리(노트북, 모니터)에서 "기대와 다름" 사유가 많다면 상품 설명 개선이 필요합니다.

---

## 질문 4 — 월별 CS 트렌드와 주문 대비 문의 비율

**비즈니스 질문:** CS 운영팀이 월별 문의 추이와 주문 대비 문의 비율을 모니터링하고 싶어합니다. 2024년 월별 주문 수, 문의 수, 반품 수, 주문 대비 문의율(%)을 보여주세요.

**힌트:**

- 각 테이블에서 월별 건수를 CTE로 준비
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

    **예상 인사이트:** 문의율이 일정하면 정상 운영이지만, 특정 월에 급증하면 품질 이슈나 배송 지연이 발생했을 가능성이 높습니다. 12월 이후 1~2월에 반품이 증가하는 것은 연말 선물 교환 패턴입니다.

---

## 질문 5 — 반복 문의 고객과 에스컬레이션 대상

**비즈니스 질문:** CS 매니저가 3회 이상 문의한 고객 중 미해결 건이 있는 경우를 에스컬레이션 대상으로 분류하고 싶어합니다. 이 고객들의 총 문의 수, 미해결 건수, 총 구매 금액, 마지막 문의일을 보여주세요.

**힌트:**

- 고객별 문의 통계를 먼저 집계
- 미해결: `status NOT IN ('resolved', 'closed')`
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

    **예상 인사이트:** VIP/GOLD 고객 중 미해결 문의가 있는 경우가 가장 위험합니다. 이들의 이탈은 매출에 큰 영향을 미치므로 우선 처리가 필요합니다.

---

## 보너스 도전 과제

CS 직원별로 **월별 성과 추이**를 피벗 테이블로 만들어 보세요. 2024년 12개월(열) × 직원(행) 형태로, 각 셀에 해결 건수를 표시합니다. 연말에 특정 직원의 성과가 떨어지면 과부하 위험 신호입니다.

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
