# 날짜와 시간 분석

!!! info "사용 테이블"

    `calendar` — 날짜 차원 (요일, 공휴일)  ·  `customers` — 고객 (등급, 포인트, 가입채널)  ·  `orders` — 주문 (상태, 금액, 일시)  ·  `products` — 상품 (이름, 가격, 재고, 브랜드)  ·  `promotions` — 프로모션 (기간, 할인)  ·  `returns` — 반품/교환 (사유, 상태)  ·  `shipping` — 배송 (택배사, 추적번호, 상태)


!!! abstract "학습 범위"

    `SUBSTR`, `JULIANDAY`, `STRFTIME`, `date arithmetic`, `LAG`, `CTE`, `window functions`



### 1. 2025년 월별 주문 수와 매출을 구하세요. 취소 제외.


2025년 월별 주문 수와 매출을 구하세요. 취소 제외.


**힌트 1:** `SUBSTR(ordered_at, 1, 7)`로 월을 추출하고, `WHERE ordered_at LIKE '2025%'`로 연도 필터링.


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


### 2. 2024년 분기(Q1~Q4)별 매출과 주문 수를 구하세요.


2024년 분기(Q1~Q4)별 매출과 주문 수를 구하세요.


**힌트 1:** `CASE WHEN SUBSTR(ordered_at, 6, 2) IN ('01','02','03') THEN 'Q1' ...`으로 월을 분기로 변환.


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


### 3. 고객별로 가입일부터 첫 주문일까지 평균 며칠이 걸리는지 구하세요.


고객별로 가입일부터 첫 주문일까지 평균 며칠이 걸리는지 구하세요.


**힌트 1:** 서브쿼리에서 `MIN(ordered_at)`으로 첫 주문일을 구한 뒤, `JULIANDAY` 차이로 일수 계산.


??? success "정답"

    === "SQLite"
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

    === "MySQL"
        ```sql
        SELECT
        ROUND(AVG(DATEDIFF(first_order, join_date)), 1) AS avg_days_to_first_order
    FROM (
        SELECT
            c.id,
            c.created_at AS join_date,
            MIN(o.ordered_at) AS first_order
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        GROUP BY c.id, c.created_at
    ) AS sub;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
        ROUND(AVG(first_order::date - join_date::date), 1) AS avg_days_to_first_order
    FROM (
        SELECT
            c.id,
            c.created_at AS join_date,
            MIN(o.ordered_at) AS first_order
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        GROUP BY c.id, c.created_at
    ) AS sub;
        ```

    === "Oracle"
        ```sql
        SELECT
        ROUND(AVG(CAST(first_order AS DATE) - CAST(join_date AS DATE)), 1) AS avg_days_to_first_order
    FROM (
        SELECT
            c.id,
            c.created_at AS join_date,
            MIN(o.ordered_at) AS first_order
        FROM customers c
        INNER JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.created_at
    );
        ```

    === "SQL Server"
        ```sql
        SELECT
        ROUND(AVG(CAST(DATEDIFF(DAY, join_date, first_order) AS FLOAT)), 1) AS avg_days_to_first_order
    FROM (
        SELECT
            c.id,
            c.created_at AS join_date,
            MIN(o.ordered_at) AS first_order
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        GROUP BY c.id, c.created_at
    ) AS sub;
        ```


---


### 4. 시간대(0~23시)별 주문 수를 구하세요.


시간대(0~23시)별 주문 수를 구하세요.


**힌트 1:** `SUBSTR(ordered_at, 12, 2)`로 시간 부분을 추출. `CAST(... AS INTEGER)`로 정수 변환.


??? success "정답"

    === "SQLite"
        ```sql
        SELECT
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY hour;
        ```

    === "MySQL"
        ```sql
        SELECT
        HOUR(ordered_at) AS hour,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY HOUR(ordered_at)
    ORDER BY hour;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
        EXTRACT(HOUR FROM ordered_at::timestamp)::INTEGER AS hour,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY EXTRACT(HOUR FROM ordered_at::timestamp)
    ORDER BY hour;
        ```

    === "Oracle"
        ```sql
        SELECT
        EXTRACT(HOUR FROM CAST(ordered_at AS TIMESTAMP)) AS hour,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY EXTRACT(HOUR FROM CAST(ordered_at AS TIMESTAMP))
    ORDER BY hour;
        ```

    === "SQL Server"
        ```sql
        SELECT
        DATEPART(HOUR, ordered_at) AS hour,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY DATEPART(HOUR, ordered_at)
    ORDER BY hour;
        ```


---


### 5. 최근 30일간(2025-11-01 ~ 2025-11-30 기준) 일별 매출을 구하세요.


최근 30일간(2025-11-01 ~ 2025-11-30 기준) 일별 매출을 구하세요.


**힌트 1:** `BETWEEN '2025-11-01' AND '2025-11-30 23:59:59'`로 기간 필터링. 시간 끝까지 포함하도록 주의.


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


### 6. 배송 소요일을 구간별(1일, 2일, 3일, 4일 이상)로 나누어 건수를 구하세요.


배송 소요일을 구간별(1일, 2일, 3일, 4일 이상)로 나누어 건수를 구하세요.


**힌트 1:** 서브쿼리에서 `JULIANDAY` 차이로 소요일을 계산한 뒤, `CASE WHEN days <= 1 THEN ...`으로 구간 분류.


??? success "정답"

    === "SQLite"
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

    === "MySQL"
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
            DATEDIFF(sh.delivered_at, o.ordered_at) AS days
        FROM shipping AS sh
        INNER JOIN orders AS o ON sh.order_id = o.id
        WHERE sh.delivered_at IS NOT NULL
    ) AS sub
    GROUP BY delivery_range
    ORDER BY MIN(days);
        ```

    === "PostgreSQL"
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
            (sh.delivered_at::date - o.ordered_at::date) AS days
        FROM shipping AS sh
        INNER JOIN orders AS o ON sh.order_id = o.id
        WHERE sh.delivered_at IS NOT NULL
    ) AS sub
    GROUP BY delivery_range
    ORDER BY MIN(days);
        ```

    === "Oracle"
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
            CAST(sh.delivered_at AS DATE) - CAST(o.ordered_at AS DATE) AS days
        FROM shipping sh
        INNER JOIN orders o ON sh.order_id = o.id
        WHERE sh.delivered_at IS NOT NULL
    )
    GROUP BY
        CASE
            WHEN days <= 1 THEN '1일 이내'
            WHEN days <= 2 THEN '2일'
            WHEN days <= 3 THEN '3일'
            ELSE '4일 이상'
        END
    ORDER BY MIN(days);
        ```

    === "SQL Server"
        ```sql
        SELECT
        CASE
            WHEN days <= 1 THEN N'1일 이내'
            WHEN days <= 2 THEN N'2일'
            WHEN days <= 3 THEN N'3일'
            ELSE N'4일 이상'
        END AS delivery_range,
        COUNT(*) AS cnt
    FROM (
        SELECT
            DATEDIFF(DAY, o.ordered_at, sh.delivered_at) AS days
        FROM shipping AS sh
        INNER JOIN orders AS o ON sh.order_id = o.id
        WHERE sh.delivered_at IS NOT NULL
    ) AS sub
    GROUP BY
        CASE
            WHEN days <= 1 THEN N'1일 이내'
            WHEN days <= 2 THEN N'2일'
            WHEN days <= 3 THEN N'3일'
            ELSE N'4일 이상'
        END
    ORDER BY MIN(days);
        ```


---


### 7. 각 고객의 마지막 주문 후 경과일을 구하세요. 180일 이상인 고객만.


각 고객의 마지막 주문 후 경과일을 구하세요. 180일 이상인 고객만.


**힌트 1:** `MAX(ordered_at)`로 마지막 주문일을 구하고, `JULIANDAY('기준일') - JULIANDAY(MAX(...))`로 경과일 계산. `HAVING`으로 180일 필터.


??? success "정답"

    === "SQLite"
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

    === "MySQL"
        ```sql
        SELECT
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order,
        DATEDIFF('2025-12-31', MAX(o.ordered_at)) AS days_ago
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.grade
    HAVING days_ago >= 180
    ORDER BY days_ago DESC
    LIMIT 20;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order,
        ('2025-12-31'::date - MAX(o.ordered_at)::date) AS days_ago
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.grade
    HAVING ('2025-12-31'::date - MAX(o.ordered_at)::date) >= 180
    ORDER BY days_ago DESC
    LIMIT 20;
        ```

    === "Oracle"
        ```sql
        SELECT
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order,
        CAST(DATE '2025-12-31' - CAST(MAX(o.ordered_at) AS DATE) AS INTEGER) AS days_ago
    FROM customers c
    INNER JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.grade
    HAVING CAST(DATE '2025-12-31' - CAST(MAX(o.ordered_at) AS DATE) AS INTEGER) >= 180
    ORDER BY days_ago DESC
    FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        SELECT TOP 20
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order,
        DATEDIFF(DAY, MAX(o.ordered_at), '2025-12-31') AS days_ago
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.grade
    HAVING DATEDIFF(DAY, MAX(o.ordered_at), '2025-12-31') >= 180
    ORDER BY days_ago DESC;
        ```


---


### 8. 요일(월~일)과 시간대(0~23)별 주문 수를 구하세요. 상위 20개 조합만.


요일(월~일)과 시간대(0~23)별 주문 수를 구하세요. 상위 20개 조합만.


**힌트 1:** `STRFTIME('%w', ordered_at)`로 요일 번호를 추출하고, `CASE`로 한글 요일명 변환. 두 칼럼으로 `GROUP BY`.


??? success "정답"

    === "SQLite"
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

    === "MySQL"
        ```sql
        SELECT
        CASE DAYOFWEEK(ordered_at)
            WHEN 1 THEN '일' WHEN 2 THEN '월' WHEN 3 THEN '화'
            WHEN 4 THEN '수' WHEN 5 THEN '목' WHEN 6 THEN '금' WHEN 7 THEN '토'
        END AS day_name,
        HOUR(ordered_at) AS hour,
        COUNT(*) AS orders
    FROM orders
    GROUP BY DAYOFWEEK(ordered_at), HOUR(ordered_at)
    ORDER BY orders DESC
    LIMIT 20;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
        CASE EXTRACT(DOW FROM ordered_at::timestamp)::INTEGER
            WHEN 0 THEN '일' WHEN 1 THEN '월' WHEN 2 THEN '화'
            WHEN 3 THEN '수' WHEN 4 THEN '목' WHEN 5 THEN '금' WHEN 6 THEN '토'
        END AS day_name,
        EXTRACT(HOUR FROM ordered_at::timestamp)::INTEGER AS hour,
        COUNT(*) AS orders
    FROM orders
    GROUP BY EXTRACT(DOW FROM ordered_at::timestamp), EXTRACT(HOUR FROM ordered_at::timestamp)
    ORDER BY orders DESC
    LIMIT 20;
        ```

    === "Oracle"
        ```sql
        SELECT
        CASE TO_NUMBER(TO_CHAR(CAST(ordered_at AS DATE), 'D'))
            WHEN 1 THEN '일' WHEN 2 THEN '월' WHEN 3 THEN '화'
            WHEN 4 THEN '수' WHEN 5 THEN '목' WHEN 6 THEN '금' WHEN 7 THEN '토'
        END AS day_name,
        EXTRACT(HOUR FROM CAST(ordered_at AS TIMESTAMP)) AS hour,
        COUNT(*) AS orders
    FROM orders
    GROUP BY TO_NUMBER(TO_CHAR(CAST(ordered_at AS DATE), 'D')),
             EXTRACT(HOUR FROM CAST(ordered_at AS TIMESTAMP))
    ORDER BY orders DESC
    FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        SELECT TOP 20
        CASE DATEPART(WEEKDAY, ordered_at)
            WHEN 1 THEN N'일' WHEN 2 THEN N'월' WHEN 3 THEN N'화'
            WHEN 4 THEN N'수' WHEN 5 THEN N'목' WHEN 6 THEN N'금' WHEN 7 THEN N'토'
        END AS day_name,
        DATEPART(HOUR, ordered_at) AS hour,
        COUNT(*) AS orders
    FROM orders
    GROUP BY DATEPART(WEEKDAY, ordered_at), DATEPART(HOUR, ordered_at)
    ORDER BY orders DESC;
        ```


---


### 9. 연도별 매출과 전년 대비 성장률(%)을 구하세요. 취소 제외.


연도별 매출과 전년 대비 성장률(%)을 구하세요. 취소 제외.


**힌트 1:** CTE로 연도별 매출을 구한 뒤, `LAG(revenue) OVER (ORDER BY year)`로 전년 매출을 참조.


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


### 10. 반품 요청에서 완료까지 평균 소요일을 구하세요. 완료된 건만.


반품 요청에서 완료까지 평균 소요일을 구하세요. 완료된 건만.


**힌트 1:** `returns` 테이블에서 `JULIANDAY(completed_at) - JULIANDAY(requested_at)`로 소요일 계산. `WHERE status = 'completed'`.


??? success "정답"

    === "SQLite"
        ```sql
        SELECT
        ROUND(AVG(JULIANDAY(completed_at) - JULIANDAY(requested_at)), 1) AS avg_days,
        MIN(CAST(JULIANDAY(completed_at) - JULIANDAY(requested_at) AS INTEGER)) AS min_days,
        MAX(CAST(JULIANDAY(completed_at) - JULIANDAY(requested_at) AS INTEGER)) AS max_days
    FROM returns
    WHERE status = 'completed'
      AND completed_at IS NOT NULL;
        ```

    === "MySQL"
        ```sql
        SELECT
        ROUND(AVG(DATEDIFF(completed_at, requested_at)), 1) AS avg_days,
        MIN(DATEDIFF(completed_at, requested_at)) AS min_days,
        MAX(DATEDIFF(completed_at, requested_at)) AS max_days
    FROM returns
    WHERE status = 'completed'
      AND completed_at IS NOT NULL;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
        ROUND(AVG(completed_at::date - requested_at::date), 1) AS avg_days,
        MIN(completed_at::date - requested_at::date) AS min_days,
        MAX(completed_at::date - requested_at::date) AS max_days
    FROM returns
    WHERE status = 'completed'
      AND completed_at IS NOT NULL;
        ```

    === "Oracle"
        ```sql
        SELECT
        ROUND(AVG(CAST(completed_at AS DATE) - CAST(requested_at AS DATE)), 1) AS avg_days,
        MIN(CAST(completed_at AS DATE) - CAST(requested_at AS DATE)) AS min_days,
        MAX(CAST(completed_at AS DATE) - CAST(requested_at AS DATE)) AS max_days
    FROM returns
    WHERE status = 'completed'
      AND completed_at IS NOT NULL;
        ```

    === "SQL Server"
        ```sql
        SELECT
        ROUND(AVG(CAST(DATEDIFF(DAY, requested_at, completed_at) AS FLOAT)), 1) AS avg_days,
        MIN(DATEDIFF(DAY, requested_at, completed_at)) AS min_days,
        MAX(DATEDIFF(DAY, requested_at, completed_at)) AS max_days
    FROM returns
    WHERE status = 'completed'
      AND completed_at IS NOT NULL;
        ```


---


### 11. 2024년 월별로 첫 구매 고객 수와 재구매 고객 수를 구하세요.


2024년 월별로 첫 구매 고객 수와 재구매 고객 수를 구하세요.


**힌트 1:** CTE로 고객별 `MIN(ordered_at)`(첫 주문일)을 구한 뒤, 주문월과 첫 주문월을 비교하여 신규/재구매 구분.


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


### 12. 가격이 2회 이상 변경된 상품의 이름, 변경 횟수, 최초 가격, 현재 가격을 조회하세요.


가격이 2회 이상 변경된 상품의 이름, 변경 횟수, 최초 가격, 현재 가격을 조회하세요.


**힌트 1:** `products JOIN product_prices`로 이력 연결. `HAVING COUNT >= 2`. 최초 가격은 서브쿼리에서 `ORDER BY started_at ASC LIMIT 1`.


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


---


### 13. 주말 vs 평일 주문 비교


calendar 테이블을 orders와 JOIN하여
2024년 주말과 평일의 일평균 주문 수와 일평균 매출을 비교하세요.


**힌트 1:** `calendar.is_weekend` 활용. 날짜별 주문을 먼저 집계한 뒤 주말/평일 그룹별 평균 계산.


??? success "정답"
    ```sql
    WITH daily_orders AS (
        SELECT
            cal.date_key,
            cal.is_weekend,
            COUNT(o.id)         AS order_count,
            COALESCE(SUM(o.total_amount), 0) AS daily_revenue
        FROM calendar AS cal
        LEFT JOIN orders AS o
            ON SUBSTR(o.ordered_at, 1, 10) = cal.date_key
           AND o.status NOT IN ('cancelled')
        WHERE cal.year = 2024
        GROUP BY cal.date_key, cal.is_weekend
    )
    SELECT
        CASE is_weekend WHEN 1 THEN '주말' ELSE '평일' END AS day_type,
        COUNT(*)                     AS total_days,
        SUM(order_count)             AS total_orders,
        ROUND(AVG(order_count), 1)   AS avg_daily_orders,
        ROUND(AVG(daily_revenue), 0) AS avg_daily_revenue
    FROM daily_orders
    GROUP BY is_weekend;
    ```


---


### 14. 프로모션 대상 상품 조회


특정 기간(2024-11-01 ~ 2024-12-31)에 진행 중인 프로모션과
해당 프로모션에 포함된 상품을 조회하세요.


**힌트 1:** 기간 겹침: `promotions.started_at <= '2024-12-31' AND promotions.ended_at >= '2024-11-01'`. `promotion_products` -> `products` JOIN. `override_price`가 있으면 특가 표시.


??? success "정답"
    ```sql
    SELECT
        promo.name       AS promotion_name,
        promo.type       AS promotion_type,
        promo.discount_type,
        promo.discount_value,
        promo.started_at,
        promo.ended_at,
        p.name           AS product_name,
        p.price          AS regular_price,
        pp.override_price AS special_price,
        CASE
            WHEN pp.override_price IS NOT NULL THEN pp.override_price
            WHEN promo.discount_type = 'percent' THEN ROUND(p.price * (1 - promo.discount_value / 100.0), 0)
            ELSE ROUND(p.price - promo.discount_value, 0)
        END AS final_price
    FROM promotions AS promo
    INNER JOIN promotion_products AS pp ON promo.id = pp.promotion_id
    INNER JOIN products           AS p  ON pp.product_id = p.id
    WHERE promo.started_at <= '2024-12-31'
      AND promo.ended_at   >= '2024-11-01'
      AND promo.is_active = 1
    ORDER BY promo.name, p.name
    LIMIT 30;
    ```


---
