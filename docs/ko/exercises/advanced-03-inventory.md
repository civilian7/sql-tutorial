# 재고 관리

!!! info "사용 테이블"

    `products` — 상품 (이름, 가격, 재고, 브랜드)  ·  `categories` — 카테고리 (부모-자식 계층)  ·  `suppliers` — 공급업체 (업체명, 연락처)  ·  `inventory_transactions` — 재고 입출고 (유형, 수량)  ·  `order_items` — 주문 상세 (수량, 단가)  ·  `orders` — 주문 (상태, 금액, 일시)


!!! abstract "학습 범위"

    `Conditional Aggregation`, `Window Functions`, `ABC Analysis`, `Pareto`, `CTE`



### 1. 현재 재고 현황과 재고 부족 상품


물류팀이 현재 재고가 부족한 상품 목록을 요청했습니다.
재고 수량이 10개 이하인 활성 상품을 찾아, 상품명, 카테고리, 현재 재고, 가격, 공급업체를 표시하세요.
재고가 0인 상품은 "품절"로 표시합니다.


**힌트 1:** - `products.stock_qty`로 현재 재고 확인
- `products` -> `categories`, `products` -> `suppliers` JOIN
- `CASE`로 "품절" 표시
- `products.is_active = 1`로 활성 상품만



??? success "정답"
    ```sql
    SELECT
        p.name          AS product_name,
        cat.name        AS category,
        s.company_name  AS supplier,
        p.stock_qty,
        CASE
            WHEN p.stock_qty = 0 THEN '품절'
            WHEN p.stock_qty <= 5 THEN '긴급'
            ELSE '부족'
        END AS stock_status,
        p.price
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN suppliers  AS s   ON p.supplier_id = s.id
    WHERE p.is_active = 1
      AND p.stock_qty <= 10
    ORDER BY p.stock_qty ASC, p.price DESC;
    ```


---


### 2. 재고 입출고 흐름 분석


지난 1년(2025년)간 상품별 입고량과 출고량을 비교하여 재고 흐름을 파악하세요.
순변동이 마이너스인 상품만 보여주세요.


**힌트 1:** - `inventory_transactions`의 `type` 칼럼: 'inbound' (입고), 'outbound' (출고)
- 조건부 집계: `SUM(CASE WHEN type='inbound' THEN quantity ELSE 0 END)`
- `products`와 JOIN하여 현재 재고 포함



??? success "정답"
    ```sql
    SELECT
        p.name          AS product_name,
        p.stock_qty AS current_stock,
        SUM(CASE WHEN it.type = 'inbound'  THEN it.quantity ELSE 0 END) AS total_in,
        SUM(CASE WHEN it.type = 'outbound' THEN it.quantity ELSE 0 END) AS total_out,
        SUM(CASE WHEN it.type = 'inbound'  THEN it.quantity ELSE 0 END)
      - SUM(CASE WHEN it.type = 'outbound' THEN it.quantity ELSE 0 END) AS net_change
    FROM inventory_transactions AS it
    INNER JOIN products AS p ON it.product_id = p.id
    WHERE it.created_at LIKE '2025%'
    GROUP BY p.id, p.name, p.stock_qty
    HAVING net_change < 0
    ORDER BY net_change ASC;
    ```


---


### 3. 상품 ABC 분석 (파레토 80/20)


매출 기여도에 따라 상품을 A/B/C 등급으로 분류하세요.
전체 매출의 80%를 차지하는 상품을 A등급, 다음 15%를 B등급, 나머지를 C등급으로 분류합니다.


**힌트 1:** - 상품별 매출을 계산한 후 내림차순 정렬
- 누적 비율 계산에 `SUM() OVER (ORDER BY ...)`
- 전체 매출 대비 누적 비율로 A/B/C 분류



??? success "정답"
    ```sql
    WITH product_revenue AS (
        SELECT
            p.id,
            p.name,
            cat.name AS category,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name, cat.name
    ),
    ranked AS (
        SELECT *,
            SUM(revenue) OVER () AS total_revenue,
            SUM(revenue) OVER (ORDER BY revenue DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumulative_revenue
        FROM product_revenue
    )
    SELECT
        name AS product_name,
        category,
        revenue,
        ROUND(100.0 * revenue / total_revenue, 2) AS pct_of_total,
        ROUND(100.0 * cumulative_revenue / total_revenue, 2) AS cumulative_pct,
        CASE
            WHEN 100.0 * cumulative_revenue / total_revenue <= 80 THEN 'A'
            WHEN 100.0 * cumulative_revenue / total_revenue <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM ranked
    ORDER BY revenue DESC
    LIMIT 30;
    ```


---


### 4. 공급업체 성과 평가


각 공급업체의 공급 상품 수, 총 매출, 반품률, 평균 고객 평점을 산출하세요.
반품률이 높은 공급업체를 식별합니다.


**힌트 1:** - `suppliers` -> `products` -> `order_items` -> `orders` 순으로 JOIN
- 반품률: 반품 수 / 전체 판매 수
- `reviews`는 LEFT JOIN으로 평점 포함



??? success "정답"
    ```sql
    WITH supplier_sales AS (
        SELECT
            s.id AS supplier_id,
            s.company_name AS supplier_name,
            COUNT(DISTINCT p.id) AS product_count,
            SUM(oi.quantity)     AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
        FROM suppliers AS s
        INNER JOIN products   AS p  ON s.id = p.supplier_id
        INNER JOIN order_items AS oi ON p.id = oi.product_id
        INNER JOIN orders     AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY s.id, s.company_name
    ),
    supplier_returns AS (
        SELECT
            s.id AS supplier_id,
            COUNT(ret.id) AS return_count
        FROM suppliers AS s
        INNER JOIN products   AS p   ON s.id = p.supplier_id
        INNER JOIN order_items AS oi ON p.id = oi.product_id
        INNER JOIN orders     AS o2  ON oi.order_id = o2.id
        INNER JOIN returns    AS ret ON ret.order_id = o2.id
        GROUP BY s.id
    ),
    supplier_reviews AS (
        SELECT
            s.id AS supplier_id,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(r.id) AS review_count
        FROM suppliers AS s
        INNER JOIN products AS p ON s.id = p.supplier_id
        INNER JOIN reviews  AS r ON p.id = r.product_id
        GROUP BY s.id
    )
    SELECT
        ss.supplier_name,
        ss.product_count,
        ss.units_sold,
        ss.total_revenue,
        COALESCE(sr.return_count, 0) AS return_count,
        ROUND(100.0 * COALESCE(sr.return_count, 0) / ss.units_sold, 2) AS return_rate_pct,
        COALESCE(srev.avg_rating, 0) AS avg_rating,
        srev.review_count
    FROM supplier_sales AS ss
    LEFT JOIN supplier_returns AS sr   ON ss.supplier_id = sr.supplier_id
    LEFT JOIN supplier_reviews AS srev ON ss.supplier_id = srev.supplier_id
    ORDER BY return_rate_pct DESC;
    ```


---


### 5. 월별 재고 회전율 추이


2024년 월별 재고 회전율을 보여주세요.
재고 회전율 = 해당 월 출고 수량 합계 / 월말 누적 재고.


**힌트 1:** - 월별 출고량: `inventory_transactions`에서 `type='outbound'` 필터
- 윈도우 함수로 누적 재고 계산



??? success "정답"
    ```sql
    WITH monthly_flow AS (
        SELECT
            SUBSTR(created_at, 1, 7) AS year_month,
            SUM(CASE WHEN type = 'outbound' THEN quantity ELSE 0 END) AS total_out,
            SUM(CASE WHEN type = 'inbound'  THEN quantity ELSE 0 END) AS total_in
        FROM inventory_transactions
        WHERE created_at LIKE '2024%'
        GROUP BY SUBSTR(created_at, 1, 7)
    ),
    with_cumulative AS (
        SELECT
            year_month,
            total_out,
            total_in,
            SUM(total_in - total_out) OVER (
                ORDER BY year_month
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumulative_net_stock
        FROM monthly_flow
    )
    SELECT
        year_month,
        total_in,
        total_out,
        cumulative_net_stock,
        CASE
            WHEN cumulative_net_stock > 0
            THEN ROUND(1.0 * total_out / cumulative_net_stock, 2)
            ELSE NULL
        END AS turnover_ratio
    FROM with_cumulative
    ORDER BY year_month;
    ```


---


### 6. 보너스: 카테고리별 ABC 분석과 재고 부족 비율


ABC 분석을 카테고리 단위로 수행하세요.
각 카테고리의 ABC 등급과 함께, 상품 수, 재고 부족(stock_qty <= 10) 상품 비율을 표시합니다.


**힌트 1:** - 카테고리별 매출과 재고 부족 비율을 한 CTE에서 계산
- 누적 매출로 ABC 등급 분류



??? success "정답"
    ```sql
    WITH category_revenue AS (
        SELECT
            cat.id AS category_id,
            cat.name AS category,
            COUNT(DISTINCT p.id) AS product_count,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
            ROUND(100.0 * SUM(CASE WHEN p.stock_qty <= 10 THEN 1 ELSE 0 END)
                        / COUNT(DISTINCT p.id), 1) AS low_stock_pct
        FROM categories AS cat
        INNER JOIN products    AS p  ON cat.id = p.category_id
        INNER JOIN order_items AS oi ON p.id   = oi.product_id
        INNER JOIN orders      AS o  ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY cat.id, cat.name
    ),
    ranked AS (
        SELECT *,
            SUM(revenue) OVER () AS total_revenue,
            SUM(revenue) OVER (ORDER BY revenue DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumulative
        FROM category_revenue
    )
    SELECT
        category,
        product_count,
        revenue,
        ROUND(100.0 * cumulative / total_revenue, 1) AS cumulative_pct,
        CASE
            WHEN 100.0 * cumulative / total_revenue <= 80 THEN 'A'
            WHEN 100.0 * cumulative / total_revenue <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class,
        low_stock_pct
    FROM ranked
    ORDER BY revenue DESC;
    ```


---
