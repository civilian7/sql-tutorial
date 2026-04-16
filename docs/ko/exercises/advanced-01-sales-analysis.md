# 매출 분석

!!! info "사용 테이블"

    `orders` — 주문 (상태, 금액, 일시)  ·  `order_items` — 주문 상세 (수량, 단가)  ·  `products` — 상품 (이름, 가격, 재고, 브랜드)  ·  `categories` — 카테고리 (부모-자식 계층)  ·  `payments` — 결제 (방법, 금액, 상태)


!!! abstract "학습 범위"

    `Aggregation`, `GROUP BY`, `Window Functions`, `CTE`, `YoY Growth`, `Pivot`



### 1. 월별 매출 추이 (2022-2024)


CEO가 지난 3년간의 월별 매출 보고서를 요청했습니다.
각 월의 매출, 주문 수, 평균 주문 금액을 보여주세요.
취소 및 반품 주문은 제외합니다.


**힌트 1:** - 월 추출에는 `SUBSTR(ordered_at, 1, 7)` 사용
- `SUM`, `COUNT`, `AVG` 활용
- 연도 범위 필터에는 `BETWEEN` 또는 `LIKE` 사용



??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7)        AS year_month,
        COUNT(*)                         AS order_count,
        ROUND(SUM(total_amount), 2)      AS revenue,
        ROUND(AVG(total_amount), 2)      AS avg_order_value
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
      AND ordered_at BETWEEN '2022-01-01' AND '2024-12-31 23:59:59'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY year_month;
    ```


---


### 2. 2024년 매출 상위 10개 상품


MD팀이 2024년에 가장 많은 매출을 올린 상품이 무엇인지 알고 싶어합니다.
상품명, 카테고리, 판매 수량, 총 매출, 평균 고객 평점이 필요합니다.


**힌트 1:** - `order_items` -> `orders` -> `products` -> `categories` 순으로 JOIN
- 리뷰가 없는 상품도 포함되도록 `reviews`는 `LEFT JOIN` 사용
- 2024년 취소되지 않은 주문으로 필터링



??? success "정답"
    ```sql
    SELECT
        p.name                                  AS product_name,
        cat.name                                AS category,
        SUM(oi.quantity)                        AS units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
        COUNT(DISTINCT r.id)                    AS review_count,
        ROUND(AVG(r.rating), 2)                 AS avg_rating
    FROM order_items AS oi
    INNER JOIN orders     AS o   ON oi.order_id   = o.id
    INNER JOIN products   AS p   ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LEFT  JOIN reviews    AS r   ON r.product_id  = p.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY p.id, p.name, cat.name
    ORDER BY total_revenue DESC
    LIMIT 10;
    ```


---


### 3. 계절성 패턴 분석


이 쇼핑몰에 계절성 매출 패턴이 있나요?
전체 연도에 걸쳐 달력 월(1월~12월)별 평균 월 매출을 계산하세요.
가장 높은 달과 가장 낮은 달을 찾아보세요.


**힌트 1:** - 월 번호(01~12) 추출에는 `SUBSTR(ordered_at, 6, 2)` 사용
- 파생 테이블을 이용하여 연도별 `SUM`의 평균 계산
- 월 번호를 이름으로 변환하려면 `CASE` 사용



??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7)  AS year_month,
            SUBSTR(ordered_at, 6, 2)  AS month_num,
            SUM(total_amount)         AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        CASE month_num
            WHEN '01' THEN '1월'  WHEN '02' THEN '2월'
            WHEN '03' THEN '3월'  WHEN '04' THEN '4월'
            WHEN '05' THEN '5월'  WHEN '06' THEN '6월'
            WHEN '07' THEN '7월'  WHEN '08' THEN '8월'
            WHEN '09' THEN '9월'  WHEN '10' THEN '10월'
            WHEN '11' THEN '11월' WHEN '12' THEN '12월'
        END AS month_name,
        month_num,
        COUNT(*) AS years_of_data,
        ROUND(AVG(revenue), 2)  AS avg_monthly_revenue,
        ROUND(MIN(revenue), 2)  AS min_revenue,
        ROUND(MAX(revenue), 2)  AS max_revenue
    FROM monthly
    GROUP BY month_num
    ORDER BY month_num;
    ```


---


### 4. 결제 수단 분석


재무팀이 고객의 결제 수단을 파악하고 싶어합니다.
결제 수단별로 거래 수, 총 결제금액, 평균 거래금액,
전체 매출에서 차지하는 비율을 보여주세요.


**힌트 1:** - `payments`를 `orders`와 JOIN하여 주문 날짜 포함
- 전체 합계는 `SUM(...) OVER ()` (윈도우 함수) 또는 서브쿼리로 계산
- 비율에는 `ROUND(..., 1)` 사용



??? success "정답"
    ```sql
    WITH payment_totals AS (
        SELECT
            p.method,
            COUNT(*)            AS transaction_count,
            SUM(p.amount)       AS total_collected,
            AVG(p.amount)       AS avg_transaction
        FROM payments AS p
        WHERE p.status = 'completed'
        GROUP BY p.method
    ),
    grand_total AS (
        SELECT SUM(total_collected) AS grand FROM payment_totals
    )
    SELECT
        pt.method,
        pt.transaction_count,
        ROUND(pt.total_collected, 2)  AS total_collected,
        ROUND(pt.avg_transaction, 2)  AS avg_transaction,
        ROUND(100.0 * pt.total_collected / gt.grand, 1) AS pct_of_revenue
    FROM payment_totals AS pt
    CROSS JOIN grand_total AS gt
    ORDER BY pt.total_collected DESC;
    ```


---


### 5. 카테고리별 전년 대비 매출 성장률(YoY)


이사회가 2023년과 2024년의 카테고리별 YoY 성장률 보고서를 원합니다.
각 카테고리의 두 연도 매출과 변화율을 보여주세요.


**힌트 1:** - 연도별 매출에는 조건부 집계 `SUM(CASE WHEN ... THEN ... END)` 사용
- YoY% 계산식: `(2024 - 2023) / 2023 * 100`
- 0으로 나누기 방지에는 `NULLIF` 사용



??? success "정답"
    ```sql
    WITH category_revenue AS (
        SELECT
            cat.name AS category,
            ROUND(SUM(CASE
                WHEN o.ordered_at LIKE '2023%'
                THEN oi.quantity * oi.unit_price ELSE 0
            END), 2) AS revenue_2023,
            ROUND(SUM(CASE
                WHEN o.ordered_at LIKE '2024%'
                THEN oi.quantity * oi.unit_price ELSE 0
            END), 2) AS revenue_2024
        FROM order_items AS oi
        INNER JOIN orders     AS o   ON oi.order_id   = o.id
        INNER JOIN products   AS p   ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
          AND o.ordered_at BETWEEN '2023-01-01' AND '2024-12-31 23:59:59'
        GROUP BY cat.name
    )
    SELECT
        category,
        revenue_2023,
        revenue_2024,
        ROUND(revenue_2024 - revenue_2023, 2) AS absolute_change,
        ROUND(
            100.0 * (revenue_2024 - revenue_2023)
                  / NULLIF(revenue_2023, 0),
            1
        ) AS yoy_growth_pct
    FROM category_revenue
    ORDER BY yoy_growth_pct DESC;
    ```


---


### 6. 보너스: 카테고리 x 월 히트맵


질문 3과 5를 결합하세요.
2024년 카테고리(행) x 월(열) 형태의 히트맵 표를 만들어 보세요.
12개의 SUM(CASE WHEN month = 'XX' ...) 칼럼을 가진 조건부 집계를 사용합니다.


**힌트 1:** - `SUBSTR(o.ordered_at, 6, 2)` 로 월 추출
- 12개 칼럼에 대해 각각 `SUM(CASE WHEN ... THEN ... ELSE 0 END)`
- `GROUP BY cat.name`



??? success "정답"
    ```sql
    SELECT
        cat.name AS category,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='01' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS jan,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='02' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS feb,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='03' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS mar,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='04' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS apr,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='05' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS may,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='06' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS jun,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='07' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS jul,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='08' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS aug,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='09' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS sep,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='10' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS oct,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='11' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS nov,
        ROUND(SUM(CASE WHEN SUBSTR(o.ordered_at,6,2)='12' THEN oi.quantity*oi.unit_price ELSE 0 END),0) AS dec
    FROM order_items AS oi
    INNER JOIN orders     AS o   ON oi.order_id   = o.id
    INNER JOIN products   AS p   ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY cat.name
    ORDER BY cat.name;
    ```


---
