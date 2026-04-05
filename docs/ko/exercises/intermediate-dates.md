# 중급 연습: 날짜와 시간 분석

날짜/시간 함수, 기간 계산, 추세 분석을 연습하는 12문제입니다.

---

### 1. 올해 월별 매출

2025년 월별 주문 수와 매출을 구하세요. 취소 제외.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```

---

### 2. 분기별 매출 비교

2024년 분기(Q1~Q4)별 매출과 주문 수를 구하세요.

??? success "정답"
    ```sql
    SELECT
        CASE
            WHEN SUBSTR(ordered_at, 6, 2) IN ('01','02','03') THEN 'Q1'
            WHEN SUBSTR(ordered_at, 6, 2) IN ('04','05','06') THEN 'Q2'
            WHEN SUBSTR(ordered_at, 6, 2) IN ('07','08','09') THEN 'Q3'
            ELSE 'Q4'
        END AS quarter,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND status NOT IN ('cancelled')
    GROUP BY quarter
    ORDER BY quarter;
    ```

---

### 3. 가입 후 첫 주문까지 걸린 일수

고객별로 가입일부터 첫 주문일까지 평균 며칠이 걸리는지 구하세요.

??? success "정답"
    ```sql
    SELECT
        ROUND(AVG(JULIANDAY(first_order) - JULIANDAY(join_date)), 1) AS avg_days_to_first_order
    FROM (
        SELECT
            c.id,
            c.created_at AS join_date,
            MIN(o.ordered_at) AS first_order
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        GROUP BY c.id, c.created_at
    );
    ```

---

### 4. 시간대별 주문 분포

시간대(0~23시)별 주문 수를 구하세요.

??? success "정답"
    ```sql
    SELECT
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY hour;
    ```

---

### 5. 최근 30일 매출

최근 30일간(2025-11-01 ~ 2025-11-30 기준) 일별 매출을 구하세요.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 10) AS order_date,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at BETWEEN '2025-11-01' AND '2025-11-30 23:59:59'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 10)
    ORDER BY order_date;
    ```

---

### 6. 주문에서 배송완료까지 소요일 분포

배송 소요일을 구간별(1일, 2일, 3일, 4일 이상)로 나누어 건수를 구하세요.

??? success "정답"
    ```sql
    SELECT
        CASE
            WHEN days <= 1 THEN '1일 이내'
            WHEN days <= 2 THEN '2일'
            WHEN days <= 3 THEN '3일'
            ELSE '4일 이상'
        END AS delivery_range,
        COUNT(*) AS cnt
    FROM (
        SELECT
            JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at) AS days
        FROM shipping AS sh
        INNER JOIN orders AS o ON sh.order_id = o.id
        WHERE sh.delivered_at IS NOT NULL
    )
    GROUP BY delivery_range
    ORDER BY MIN(days);
    ```

---

### 7. 고객별 마지막 주문 경과일

각 고객의 마지막 주문 후 경과일을 구하세요. 180일 이상인 고객만.

??? success "정답"
    ```sql
    SELECT
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order,
        CAST(JULIANDAY('2025-12-31') - JULIANDAY(MAX(o.ordered_at)) AS INTEGER) AS days_ago
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.grade
    HAVING days_ago >= 180
    ORDER BY days_ago DESC
    LIMIT 20;
    ```

---

### 8. 요일 × 시간 히트맵

요일(월~일)과 시간대(0~23)별 주문 수를 구하세요. 상위 20개 조합만.

??? success "정답"
    ```sql
    SELECT
        CASE CAST(STRFTIME('%w', ordered_at) AS INTEGER)
            WHEN 0 THEN '일' WHEN 1 THEN '월' WHEN 2 THEN '화'
            WHEN 3 THEN '수' WHEN 4 THEN '목' WHEN 5 THEN '금' WHEN 6 THEN '토'
        END AS day_name,
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        COUNT(*) AS orders
    FROM orders
    GROUP BY STRFTIME('%w', ordered_at), CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY orders DESC
    LIMIT 20;
    ```

---

### 9. 연도별 성장률

연도별 매출과 전년 대비 성장률(%)을 구하세요. 취소 제외.

??? success "정답"
    ```sql
    WITH yearly AS (
        SELECT
            SUBSTR(ordered_at, 1, 4) AS year,
            ROUND(SUM(total_amount), 2) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 4)
    )
    SELECT
        year,
        revenue,
        LAG(revenue) OVER (ORDER BY year) AS prev_year,
        ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year))
            / LAG(revenue) OVER (ORDER BY year), 1) AS growth_pct
    FROM yearly
    ORDER BY year;
    ```

---

### 10. 반품 처리 소요일

반품 요청에서 완료까지 평균 소요일을 구하세요. 완료된 건만.

??? success "정답"
    ```sql
    SELECT
        ROUND(AVG(JULIANDAY(completed_at) - JULIANDAY(requested_at)), 1) AS avg_days,
        MIN(CAST(JULIANDAY(completed_at) - JULIANDAY(requested_at) AS INTEGER)) AS min_days,
        MAX(CAST(JULIANDAY(completed_at) - JULIANDAY(requested_at) AS INTEGER)) AS max_days
    FROM returns
    WHERE status = 'completed'
      AND completed_at IS NOT NULL;
    ```

---

### 11. 월별 신규 고객 vs 재구매 고객

2024년 월별로 첫 구매 고객 수와 재구매 고객 수를 구하세요.

??? success "정답"
    ```sql
    WITH first_orders AS (
        SELECT
            customer_id,
            MIN(ordered_at) AS first_order_date
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    )
    SELECT
        SUBSTR(o.ordered_at, 1, 7) AS month,
        SUM(CASE WHEN SUBSTR(o.ordered_at, 1, 7) = SUBSTR(fo.first_order_date, 1, 7)
            THEN 1 ELSE 0 END) AS new_customers,
        SUM(CASE WHEN SUBSTR(o.ordered_at, 1, 7) > SUBSTR(fo.first_order_date, 1, 7)
            THEN 1 ELSE 0 END) AS returning_customers
    FROM orders AS o
    INNER JOIN first_orders AS fo ON o.customer_id = fo.customer_id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled')
    GROUP BY SUBSTR(o.ordered_at, 1, 7)
    ORDER BY month;
    ```

---

### 12. 가격 변경 이력 분석

가격이 2회 이상 변경된 상품의 이름, 변경 횟수, 최초 가격, 현재 가격을 조회하세요.

??? success "정답"
    ```sql
    SELECT
        p.name,
        COUNT(pp.id) AS price_changes,
        (SELECT pp2.price FROM product_prices pp2
         WHERE pp2.product_id = p.id ORDER BY pp2.started_at ASC LIMIT 1) AS first_price,
        p.price AS current_price
    FROM products AS p
    INNER JOIN product_prices AS pp ON p.id = pp.product_id
    GROUP BY p.id, p.name, p.price
    HAVING COUNT(pp.id) >= 2
    ORDER BY price_changes DESC
    LIMIT 15;
    ```
