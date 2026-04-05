# 연습 문제: 실무 SQL 패턴

데이터베이스에 내장된 뷰(View)를 분석하고, 실무에서 자주 등장하는 고급 SQL 패턴을 직접 작성해 봅니다. RFM 분석, 파레토 법칙, 매출 성장률, 장바구니 이탈 등 비즈니스 인텔리전스의 핵심 패턴을 다룹니다.

> **사전 준비:** `SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;`을 실행하여 사용 가능한 뷰 목록을 확인하세요.

---

## 질문 1 — 뷰 분석: 매출 성장률 (LAG 패턴)

**비즈니스 질문:** `v_revenue_growth` 뷰의 구조를 분석한 후, 이 뷰를 직접 재현하세요. 월별 매출과 전월 대비 성장률(%)을 계산합니다. `LAG` 윈도우 함수를 사용합니다.

**힌트:**

- `LAG(revenue, 1) OVER (ORDER BY year_month)`로 전월 매출 참조
- 성장률 = `(당월 - 전월) / 전월 * 100`
- 첫 번째 월은 전월 데이터가 없으므로 NULL

??? success "정답"
    ```sql
    -- v_revenue_growth 뷰 재현
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

    **핵심 패턴:** `LAG(값, N)`은 N행 이전의 값을 참조합니다. 전년 동기 대비(YoY)는 `LAG(revenue, 12)`로 구현 가능합니다.

---

## 질문 2 — 카테고리별 상위 N개 상품 (ROW_NUMBER 패턴)

**비즈니스 질문:** 각 카테고리에서 매출 상위 3개 상품을 선발하세요. `v_top_products_by_category` 뷰와 동일한 결과를 내는 쿼리를 작성합니다.

**힌트:**

- `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)`
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

    **핵심 패턴:** `ROW_NUMBER`은 동점 시 하나만 선택하고, `RANK`는 동점을 같은 순위로 처리합니다. 용도에 따라 선택하세요.

---

## 질문 3 — 장바구니 이탈 분석

**비즈니스 질문:** 마케팅팀이 장바구니에 상품을 담았지만 주문하지 않은 "이탈 고객"의 규모와 패턴을 파악하고 싶어합니다. 이탈 장바구니의 총 수, 이탈 상품 금액, 가장 많이 이탈된 상품 TOP 10을 분석하세요.

**힌트:**

- `carts.status`가 'abandoned'인 장바구니
- `cart_items` → `products`로 상품 정보 포함
- 이탈 금액 = 수량 × 가격

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

    ```sql
    -- 이탈이 가장 많은 상품 TOP 10
    SELECT
        p.name AS product_name,
        cat.name AS category,
        COUNT(*) AS abandon_count,
        ROUND(SUM(ci.quantity * p.price), 2) AS lost_revenue
    FROM carts AS c
    INNER JOIN cart_items  AS ci  ON c.id = ci.cart_id
    INNER JOIN products   AS p   ON ci.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE c.status = 'abandoned'
    GROUP BY p.id, p.name, cat.name
    ORDER BY lost_revenue DESC
    LIMIT 10;
    ```

    **핵심 패턴:** 이탈 분석은 "발생하지 않은 이벤트"를 측정합니다. JOIN으로 관련 데이터를 조합하고, 집계로 규모를 파악하는 표준 패턴입니다.

---

## 질문 4 — 쿠폰 효과 분석

**비즈니스 질문:** 쿠폰을 사용한 주문과 사용하지 않은 주문의 평균 주문 금액을 비교하세요. 쿠폰별 사용 횟수, 할인 총액, ROI(쿠폰 매출 / 할인액)를 계산합니다.

**힌트:**

- `coupon_usage` → `coupons`로 쿠폰 정보
- `coupon_usage` → `orders`로 주문 금액
- 비쿠폰 주문: `coupon_usage`에 없는 주문

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

    ```sql
    -- 쿠폰별 ROI
    SELECT
        cp.code,
        cp.type,
        cp.discount_value,
        COUNT(cu.id) AS usage_count,
        ROUND(SUM(cu.discount_amount), 2) AS total_discount,
        ROUND(SUM(o.total_amount), 2) AS coupon_revenue,
        ROUND(SUM(o.total_amount) / NULLIF(SUM(cu.discount_amount), 0), 1) AS roi
    FROM coupons AS cp
    INNER JOIN coupon_usage AS cu ON cp.id = cu.coupon_id
    INNER JOIN orders       AS o  ON cu.order_id = o.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY cp.id, cp.code, cp.type, cp.discount_value
    ORDER BY roi DESC;
    ```

    **핵심 패턴:** A/B 비교(쿠폰 사용 vs 미사용)와 ROI 계산은 마케팅 분석의 기본입니다. `LEFT JOIN` + `CASE`로 두 그룹을 나누고, `NULLIF`로 0 나눗셈을 방지합니다.

---

## 질문 5 — 시간대별 주문 패턴

**비즈니스 질문:** 운영팀이 주문이 집중되는 시간대를 파악하고 싶어합니다. 시간대(0~23시)별 주문 수, 평균 주문 금액, 주말/평일 비교를 보여주세요.

**힌트:**

- 시간 추출: `CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)`
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

    **예상 인사이트:** 점심(12~13시)과 저녁(20~22시)에 주문이 집중됩니다. 주말 오전에는 평일 대비 주문이 적고, 심야(2~5시) 주문은 평균 금액이 낮습니다.

---

## 보너스 도전 과제

위의 시간대별 분석과 요일별 분석을 결합하여 **24(시간) × 7(요일) 히트맵 매트릭스**를 만드세요. 각 셀에 주문 수를 표시합니다.

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
