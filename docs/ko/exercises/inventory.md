# 연습 문제: 재고 관리

재고 데이터를 분석하여 운영팀이 활용할 수 있는 인사이트를 도출합니다. 재고 회전율, 발주 시점 계산, ABC 분석, 공급업체 평가 등 SCM(공급망 관리) 관점의 다섯 가지 질문에 도전해 보세요.

---

## 질문 1 — 현재 재고 현황과 재고 부족 상품

**비즈니스 질문:** 물류팀이 현재 재고가 부족한 상품 목록을 요청했습니다. 재고 수량이 10개 이하인 활성 상품을 찾아, 상품명, 카테고리, 현재 재고, 가격, 공급업체를 표시하세요. 재고가 0인 상품은 "품절"로 표시합니다.

**힌트:**

- `products.stock_qty`로 현재 재고 확인
- `products` → `categories`, `products` → `suppliers` JOIN
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

    **예상 인사이트:** 고가 상품(노트북, 모니터)이 재고 부족 목록에 포함되면 매출 손실이 큽니다. 품절 상품 중 활성 상태인 것은 긴급 발주가 필요합니다.

---

## 질문 2 — 재고 입출고 흐름 분석

**비즈니스 질문:** 지난 1년(2025년)간 상품별 입고량과 출고량을 비교하여 재고 흐름을 파악하세요. 입고(in) 합계, 출고(out) 합계, 순변동(입고-출고), 현재 재고를 함께 표시합니다. 순변동이 마이너스인 상품만 보여주세요.

**힌트:**

- `inventory_transactions`의 `type` 컬럼: 'inbound' (입고), 'outbound' (출고)
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

    **예상 인사이트:** 출고가 입고를 초과하는 상품은 재고가 계속 감소하고 있으므로 발주 계획을 세워야 합니다.

---

## 질문 3 — 상품 ABC 분석 (파레토 80/20)

**비즈니스 질문:** 경영진이 매출 기여도에 따라 상품을 A/B/C 등급으로 분류하고 싶어합니다. 전체 매출의 80%를 차지하는 상품을 A등급, 다음 15%를 B등급, 나머지를 C등급으로 분류하세요.

**힌트:**

- 상품별 매출을 계산한 후 내림차순 정렬
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

    **예상 인사이트:** A등급 상품은 전체의 약 20%이지만 매출의 80%를 차지합니다. 이들의 재고를 최우선으로 관리해야 합니다.

---

## 질문 4 — 공급업체 성과 평가

**비즈니스 질문:** 구매팀이 공급업체별 성과를 평가하고 싶어합니다. 각 공급업체의 공급 상품 수, 총 매출, 반품률, 평균 고객 평점을 산출하세요. 반품률이 높은 공급업체를 식별합니다.

**힌트:**

- `suppliers` → `products` → `order_items` → `orders` 순으로 JOIN
- 반품률: 반품 수 / 전체 판매 수
- `reviews`는 LEFT JOIN으로 평점 포함
- 공급업체별 GROUP BY

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

    **예상 인사이트:** 반품률이 5%를 초과하는 공급업체는 품질 관리 회의가 필요합니다. 반품률이 높지만 평점이 괜찮은 경우 배송 문제일 가능성이 높습니다.

---

## 질문 5 — 월별 재고 회전율 추이

**비즈니스 질문:** 재무팀이 2024년 월별 재고 회전율을 보고 싶어합니다. 재고 회전율 = 해당 월 출고 수량 합계 / 월말 평균 재고. 전체 상품 평균으로 계산하세요.

**힌트:**

- 월별 출고량: `inventory_transactions`에서 `type='outbound'` 필터
- 평균 재고 추정: 월별 입고와 출고를 누적 계산하여 근사
- 윈도우 함수로 누적 재고 계산 가능
- 단순화를 위해 `products.stock_qty`를 기준 재고로 활용하는 방법도 가능

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

    **예상 인사이트:** 11~12월은 출고가 급증하여 회전율이 높아지고, 1~2월은 재고가 쌓여 회전율이 낮아집니다. 연간 평균 회전율이 1 미만이면 과다 재고 위험이 있습니다.

---

## 보너스 도전 과제

질문 3의 ABC 분석을 **카테고리 단위**로 수행하세요. 각 카테고리의 ABC 등급과 함께, 해당 카테고리 내 상품 수, 재고 부족(stock_qty ≤ 10) 상품 비율을 표시합니다. A등급 카테고리에서 재고 부족 비율이 높다면 즉각적인 발주가 필요합니다.

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
