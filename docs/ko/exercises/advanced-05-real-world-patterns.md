# 실무 SQL 패턴

!!! info "사용 테이블"

    `orders` — 주문 (상태, 금액, 일시)  ·  `order_items` — 주문 상세 (수량, 단가)  ·  `products` — 상품 (이름, 가격, 재고, 브랜드)  ·  `categories` — 카테고리 (부모-자식 계층)  ·  `reviews` — 리뷰 (평점, 내용)  ·  `carts` — 장바구니 (상태)  ·  `cart_items` — 장바구니 상품 (수량)  ·  `coupons` — 쿠폰 (할인율, 유효기간)  ·  `coupon_usage` — 쿠폰 사용 내역


!!! abstract "학습 범위"

    `LAG`, `ROW_NUMBER`, `Cart Abandonment`, `Coupon ROI`, `Time Pattern`



### 1. 뷰 분석: 매출 성장률 (LAG 패턴)


v_revenue_growth 뷰의 구조를 분석한 후, 이 뷰를 직접 재현하세요.
월별 매출과 전월 대비 성장률(%)을 계산합니다. LAG 윈도우 함수를 사용합니다.


**힌트 1:** - `LAG(revenue, 1) OVER (ORDER BY year_month)`로 전월 매출 참조
- 성장률 = `(당월 - 전월) / 전월 * 100`
- 첫 번째 월은 전월 데이터가 없으므로 NULL



??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 2) AS revenue,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        order_count,
        LAG(revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
        ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY year_month))
            / LAG(revenue, 1) OVER (ORDER BY year_month), 1) AS mom_growth_pct
    FROM monthly
    ORDER BY year_month;
    ```


---


### 2. 카테고리별 상위 N개 상품 (ROW_NUMBER 패턴)


각 카테고리에서 매출 상위 3개 상품을 선발하세요.


**힌트 1:** - `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)`
- CTE에서 순위를 매긴 후, 외부 쿼리에서 `WHERE rn <= 3` 필터



??? success "정답"
    ```sql
    WITH product_sales AS (
        SELECT
            cat.name AS category,
            p.name AS product_name,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
            SUM(oi.quantity) AS units_sold
        FROM order_items AS oi
        INNER JOIN orders     AS o   ON oi.order_id   = o.id
        INNER JOIN products   AS p   ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY cat.name, p.name
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn
        FROM product_sales
    )
    SELECT category, product_name, revenue, units_sold, rn AS rank
    FROM ranked
    WHERE rn <= 3
    ORDER BY category, rn;
    ```


---


### 3. 장바구니 이탈 분석


장바구니에 상품을 담았지만 주문하지 않은 "이탈 고객"의 규모와 패턴을 파악하세요.
이탈 장바구니의 총 수, 이탈 상품 금액, 가장 많이 이탈된 상품 TOP 10을 분석하세요.


**힌트 1:** - `carts.status`가 'abandoned'인 장바구니
- `cart_items` -> `products`로 상품 정보 포함
- 이탈 금액 = 수량 x 가격



??? success "정답"
    ```sql
    -- 이탈 장바구니 요약
    SELECT
        COUNT(DISTINCT c.id)    AS abandoned_carts,
        COUNT(ci.id)            AS abandoned_items,
        ROUND(SUM(ci.quantity * p.price), 2) AS lost_revenue
    FROM carts AS c
    INNER JOIN cart_items AS ci ON c.id = ci.cart_id
    INNER JOIN products  AS p  ON ci.product_id = p.id
    WHERE c.status = 'abandoned';
    ```


---


### 4. 쿠폰 효과 분석


쿠폰을 사용한 주문과 사용하지 않은 주문의 평균 주문 금액을 비교하세요.
쿠폰별 사용 횟수, 할인 총액, ROI(쿠폰 매출 / 할인액)를 계산합니다.


**힌트 1:** - `coupon_usage` -> `coupons`로 쿠폰 정보
- 비쿠폰 주문: `coupon_usage`에 없는 주문
- ROI = 매출 / 할인액



??? success "정답"
    ```sql
    -- 쿠폰 사용 vs 미사용 주문 비교
    WITH coupon_orders AS (
        SELECT DISTINCT order_id FROM coupon_usage
    )
    SELECT
        CASE WHEN co.order_id IS NOT NULL THEN '쿠폰 사용' ELSE '쿠폰 미사용' END AS segment,
        COUNT(*) AS order_count,
        ROUND(AVG(o.total_amount), 2) AS avg_order_value,
        ROUND(SUM(o.total_amount), 2) AS total_revenue
    FROM orders AS o
    LEFT JOIN coupon_orders AS co ON o.id = co.order_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY CASE WHEN co.order_id IS NOT NULL THEN '쿠폰 사용' ELSE '쿠폰 미사용' END;
    ```


---


### 5. 시간대별 주문 패턴


시간대(0~23시)별 주문 수, 평균 주문 금액, 주말/평일 비교를 보여주세요.


**힌트 1:** - 시간 추출: `CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)`
- 요일: `CAST(STRFTIME('%w', ordered_at) AS INTEGER)` (0=일, 6=토)
- 주말: 0(일)과 6(토)



??? success "정답"
    ```sql
    SELECT
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        COUNT(*) AS order_count,
        ROUND(AVG(total_amount), 2) AS avg_order_value,
        SUM(CASE WHEN CAST(STRFTIME('%w', ordered_at) AS INTEGER) IN (0, 6)
            THEN 1 ELSE 0 END) AS weekend_orders,
        SUM(CASE WHEN CAST(STRFTIME('%w', ordered_at) AS INTEGER) NOT IN (0, 6)
            THEN 1 ELSE 0 END) AS weekday_orders,
        ROUND(1.0 * SUM(CASE WHEN CAST(STRFTIME('%w', ordered_at) AS INTEGER) IN (0, 6) THEN 1 ELSE 0 END)
            / NULLIF(SUM(CASE WHEN CAST(STRFTIME('%w', ordered_at) AS INTEGER) NOT IN (0, 6) THEN 1 ELSE 0 END), 0), 2)
            AS weekend_weekday_ratio
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY hour;
    ```


---


### 6. 보너스: 24시간 x 7요일 히트맵


시간대별 x 요일별 주문 수 히트맵 매트릭스를 만드세요.


**힌트 1:** - 24행(시간) x 7열(요일) + 합계
- `SUM(CASE WHEN STRFTIME('%w', ...) = 'N' THEN 1 ELSE 0 END)`



??? success "정답"
    ```sql
    SELECT
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '1' THEN 1 ELSE 0 END) AS mon,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '2' THEN 1 ELSE 0 END) AS tue,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '3' THEN 1 ELSE 0 END) AS wed,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '4' THEN 1 ELSE 0 END) AS thu,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '5' THEN 1 ELSE 0 END) AS fri,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '6' THEN 1 ELSE 0 END) AS sat,
        SUM(CASE WHEN STRFTIME('%w', ordered_at) = '0' THEN 1 ELSE 0 END) AS sun,
        COUNT(*) AS total
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY hour;
    ```


---
