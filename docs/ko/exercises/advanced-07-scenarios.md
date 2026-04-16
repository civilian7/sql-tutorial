# 비즈니스 시나리오

#### :material-database: 사용 테이블


`orders` — 주문 (상태, 금액, 일시)<br>

`order_items` — 주문 상세 (수량, 단가)<br>

`products` — 상품 (이름, 가격, 재고, 브랜드)<br>

`categories` — 카테고리 (부모-자식 계층)<br>

`customers` — 고객 (등급, 포인트, 가입채널)<br>

`complaints` — 고객 불만 (유형, 우선순위)<br>

`returns` — 반품/교환 (사유, 상태)<br>

`shipping` — 배송 (택배사, 추적번호, 상태)<br>

`reviews` — 리뷰 (평점, 내용)<br>

`payments` — 결제 (방법, 금액, 상태)<br>

`suppliers` — 공급업체 (업체명, 연락처)<br>

`staff` — 직원 (부서, 역할, 관리자)<br>



**:material-book-open-variant: 학습 범위:** `CTE`, `Scalar Subquery`, `CASE`, `JULIANDAY`, `Business Reporting`


---


### 1. 시나리오 1: CEO 주간 보고


역할: 데이터 분석가. CEO가 월요일 아침 회의에서 볼 주간 요약을 요청했습니다.
지난 주(2024-12-16 ~ 2024-12-22) 기준으로 주문 수, 매출, 평균 주문 금액,
신규 가입 고객 수, 전주 대비 매출 증감률을 한 번에 보여주세요.


**힌트 1:** 이번 주/지난 주/신규 고객을 각각 CTE로 계산한 뒤
`FROM this_week, last_week, new_customers`로 한 행에 합칩니다.



??? success "정답"
    ```sql
    WITH this_week AS (
        SELECT
            COUNT(*) AS orders,
            ROUND(SUM(total_amount), 0) AS revenue,
            ROUND(AVG(total_amount), 0) AS avg_order
        FROM orders
        WHERE ordered_at BETWEEN '2024-12-16' AND '2024-12-22 23:59:59'
          AND status NOT IN ('cancelled')
    ),
    last_week AS (
        SELECT ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at BETWEEN '2024-12-09' AND '2024-12-15 23:59:59'
          AND status NOT IN ('cancelled')
    ),
    new_customers AS (
        SELECT COUNT(*) AS signups
        FROM customers
        WHERE created_at BETWEEN '2024-12-16' AND '2024-12-22 23:59:59'
    )
    SELECT
        tw.orders,
        tw.revenue,
        tw.avg_order,
        nc.signups AS new_customers,
        ROUND(100.0 * (tw.revenue - lw.revenue) / NULLIF(lw.revenue, 0), 1) AS wow_growth_pct
    FROM this_week tw, last_week lw, new_customers nc;
    ```


---


### 2. 시나리오 2: MD팀 상품 리뷰


역할: MD(상품기획)팀 담당자.
2024년 매출 상위 20개 상품에 대해 상품명, 카테고리, 매출, 판매 수량,
평균 평점, 반품 건수를 보여주세요. 평점/반품 경고 플래그도 포함합니다.


**힌트 1:** 매출 Top 20을 CTE로 먼저 뽑고, `reviews`와 `returns`를 `LEFT JOIN`으로 붙이세요.
`CASE`로 경고 플래그를 추가합니다.



??? success "정답"
    ```sql
    WITH top_products AS (
        SELECT
            p.id, p.name, cat.name AS category,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        INNER JOIN products p ON oi.product_id = p.id
        INNER JOIN categories cat ON p.category_id = cat.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled')
        GROUP BY p.id, p.name, cat.name
        ORDER BY revenue DESC
        LIMIT 20
    ),
    product_reviews AS (
        SELECT product_id, ROUND(AVG(rating), 2) AS avg_rating, COUNT(*) AS review_count
        FROM reviews GROUP BY product_id
    ),
    product_returns AS (
        SELECT oi.product_id, COUNT(DISTINCT r.id) AS return_count
        FROM returns r
        INNER JOIN order_items oi ON r.order_id = oi.order_id
        GROUP BY oi.product_id
    )
    SELECT
        tp.name, tp.category, tp.revenue, tp.units_sold,
        COALESCE(pr.avg_rating, 0) AS avg_rating,
        COALESCE(pr.review_count, 0) AS reviews,
        COALESCE(ret.return_count, 0) AS returns,
        CASE
            WHEN pr.avg_rating < 3.5 THEN 'Low Rating'
            WHEN ret.return_count > 5 THEN 'High Returns'
            ELSE ''
        END AS alert
    FROM top_products tp
    LEFT JOIN product_reviews pr ON tp.id = pr.product_id
    LEFT JOIN product_returns ret ON tp.id = ret.product_id
    ORDER BY tp.revenue DESC;
    ```


---


### 3. 시나리오 3: 마케팅 캠페인 대상자


역할: 마케팅팀 담당자. 재활성화 이메일 캠페인을 준비합니다.
과거 3회 이상 구매했지만 최근 6개월간 주문이 없는 고객 리스트를 뽑아주세요.


**힌트 1:** `HAVING COUNT(*) >= 3 AND MAX(ordered_at) < DATE('기준일', '-6 months')`



??? success "정답"
    ```sql
    SELECT
        c.name, c.email, c.grade,
        MAX(o.ordered_at) AS last_order,
        COUNT(*) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent,
        CAST(JULIANDAY('2025-12-31') - JULIANDAY(MAX(o.ordered_at)) AS INTEGER) AS days_inactive
    FROM customers c
    INNER JOIN orders o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
      AND c.is_active = 1
    GROUP BY c.id, c.name, c.email, c.grade
    HAVING COUNT(*) >= 3
       AND MAX(o.ordered_at) < DATE('2025-12-31', '-6 months')
    ORDER BY total_spent DESC;
    ```


---


### 4. 시나리오 4: 재무팀 월말 마감


역할: 재무팀 담당자. 2024년 12월 월말 마감 보고서를 준비합니다.
결제 수단별 건수, 총 결제 금액, 환불 건수, 환불 금액, 순매출을 보여주세요.


**힌트 1:** `payments` 테이블에서 `SUM(CASE WHEN status = 'completed' ...)`와
`SUM(CASE WHEN status = 'refunded' ...)`로 조건부 집계합니다.



??? success "정답"
    ```sql
    SELECT
        method,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS paid_count,
        ROUND(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) AS paid_amount,
        SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) AS refund_count,
        ROUND(SUM(CASE WHEN status = 'refunded' THEN amount ELSE 0 END), 0) AS refund_amount,
        ROUND(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END)
            - SUM(CASE WHEN status = 'refunded' THEN amount ELSE 0 END), 0) AS net_revenue
    FROM payments
    WHERE created_at LIKE '2024-12%'
    GROUP BY method
    ORDER BY net_revenue DESC;
    ```


---


### 5. 시나리오 5: 물류팀 배송 지연 보고


역할: 물류팀 담당자.
출고 후 3일 이상 걸린 배송 건을 택배사별로 집계하세요.


**힌트 1:** `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)`로 배송 소요일을 계산하고,
`>= 3` 조건으로 지연 건만 필터링합니다.



??? success "정답"
    ```sql
    SELECT
        sh.carrier,
        COUNT(*) AS delayed_count,
        ROUND(AVG(JULIANDAY(sh.delivered_at) - JULIANDAY(sh.shipped_at)), 1) AS avg_days,
        MAX(CAST(JULIANDAY(sh.delivered_at) - JULIANDAY(sh.shipped_at) AS INTEGER)) AS max_days
    FROM shipping sh
    WHERE sh.delivered_at IS NOT NULL
      AND sh.shipped_at IS NOT NULL
      AND JULIANDAY(sh.delivered_at) - JULIANDAY(sh.shipped_at) >= 3
    GROUP BY sh.carrier
    ORDER BY delayed_count DESC;
    ```


---


### 6. 시나리오 6: 구매팀 발주 제안


역할: 구매팀 담당자.
최근 30일간 일평균 판매량 대비 현재 재고가 14일 미만인 상품 리스트를 만드세요.
공급업체 연락처도 포함합니다.


**힌트 1:** CTE로 30일간 일평균 판매량을 계산한 뒤,
`stock_qty / avg_daily_sales < 14`로 필터링합니다.



??? success "정답"
    ```sql
    WITH daily_sales AS (
        SELECT
            oi.product_id,
            ROUND(1.0 * SUM(oi.quantity) / 30, 2) AS avg_daily_sales
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE('2025-12-31', '-30 days')
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    )
    SELECT
        p.name, p.sku, p.stock_qty,
        ds.avg_daily_sales,
        CASE
            WHEN ds.avg_daily_sales > 0
            THEN CAST(p.stock_qty / ds.avg_daily_sales AS INTEGER)
            ELSE 9999
        END AS days_of_stock,
        s.company_name AS supplier,
        s.contact_name, s.phone AS supplier_phone
    FROM products p
    INNER JOIN daily_sales ds ON p.id = ds.product_id
    INNER JOIN suppliers s ON p.supplier_id = s.id
    WHERE p.is_active = 1
      AND ds.avg_daily_sales > 0
      AND p.stock_qty / ds.avg_daily_sales < 14
    ORDER BY days_of_stock ASC;
    ```


---


### 7. 시나리오 7: CS팀 에스컬레이션


역할: CS팀장.
7일 이상 미해결 문의 중 VIP/GOLD 고객의 건을 우선순위와 함께 보여주세요.


**힌트 1:** `complaints` JOIN `customers`에서 `status = 'open'`과
`grade IN ('VIP', 'GOLD')`로 필터링합니다.



??? success "정답"
    ```sql
    SELECT
        c.name, c.grade, c.email,
        comp.title, comp.category, comp.priority,
        comp.created_at,
        CAST(JULIANDAY('2025-12-31') - JULIANDAY(comp.created_at) AS INTEGER) AS days_open,
        COALESCE(cv.total_spent, 0) AS total_spent
    FROM complaints comp
    INNER JOIN customers c ON comp.customer_id = c.id
    LEFT JOIN (
        SELECT customer_id, ROUND(SUM(total_amount), 0) AS total_spent
        FROM orders WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ) cv ON c.id = cv.customer_id
    WHERE comp.status = 'open'
      AND c.grade IN ('VIP', 'GOLD')
      AND JULIANDAY('2025-12-31') - JULIANDAY(comp.created_at) >= 7
    ORDER BY
        CASE comp.priority
            WHEN 'urgent' THEN 1 WHEN 'high' THEN 2
            WHEN 'medium' THEN 3 ELSE 4
        END,
        cv.total_spent DESC;
    ```


---


### 8. 시나리오 8: 경영진 연간 KPI 대시보드


역할: 데이터 분석가. 연말 경영 회의용 KPI를 준비합니다.
2024년 핵심 지표를 한 행으로 요약하세요:
총 매출, 주문 수, 신규 고객 수, 활성 고객 수, 평균 객단가, 취소율, 반품률.


**힌트 1:** 각 KPI를 스칼라 서브쿼리 `(SELECT ... FROM ...)`로 SELECT 절에 나열하면
한 행으로 출력됩니다.



??? success "정답"
    ```sql
    SELECT
        (SELECT ROUND(SUM(total_amount), 0) FROM orders
         WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')) AS revenue,
        (SELECT COUNT(*) FROM orders
         WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')) AS orders,
        (SELECT COUNT(*) FROM customers
         WHERE created_at LIKE '2024%') AS new_customers,
        (SELECT COUNT(DISTINCT customer_id) FROM orders
         WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')) AS active_customers,
        (SELECT ROUND(AVG(total_amount), 0) FROM orders
         WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')) AS avg_order_value,
        (SELECT ROUND(100.0 * SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1)
         FROM orders WHERE ordered_at LIKE '2024%') AS cancel_rate,
        (SELECT ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders WHERE ordered_at LIKE '2024%'), 1)
         FROM returns WHERE requested_at LIKE '2024%') AS return_rate;
    ```


---
