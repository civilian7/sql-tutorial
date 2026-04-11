# 날짜와 시간 분석

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `orders` — 주문 (상태, 금액, 일시)<br>
    `customers` — 고객 (등급, 포인트, 가입채널)<br>
    `shipping` — 배송 (택배사, 추적번호)<br>
    `reviews` — 리뷰 (평점, 내용)<br>
    `returns` — 반품/교환<br>
    `calendar` — 날짜 참조 (공휴일, 주말)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    `SUBSTR` 날짜 추출<br>
    `DATE()`<br>
    `STRFTIME()`<br>
    `JULIANDAY()`<br>
    날짜 연산<br>
    시간대 분석<br>
    calendar JOIN

</div>

!!! info "시작하기 전에"
    이 연습은 **중급 11강**(날짜/시간 함수)에서 배운 내용을 실전에 적용합니다.
    SQLite의 날짜는 TEXT(`'2024-03-15 14:30:00'`)로 저장되므로, `SUBSTR`과 `JULIANDAY` 등으로 처리합니다.

---

## 기초 (1~7)

SUBSTR 날짜 추출과 DATE 범위 필터를 연습합니다.

---

### 문제 1

**2025년 월별 주문 수와 매출을 구하세요. 취소 주문 제외.**

??? tip "힌트"
    `SUBSTR(ordered_at, 1, 7)`로 `'2025-01'` 형태의 월을 추출합니다. `WHERE ordered_at LIKE '2025%'`로 연도 필터링.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```

    **결과 (상위 5행):**

    | month | orders | revenue |
    |-------|--------|---------|
    | 2025-01 | 3245 | 1234560000 |
    | 2025-02 | 2987 | 1098760000 |
    | 2025-03 | 3456 | 1345670000 |
    | 2025-04 | 3123 | 1213450000 |
    | 2025-05 | 3345 | 1289670000 |

    > 실제 데이터에 따라 수치가 달라집니다. 12개 행이 반환됩니다.

---

### 문제 2

**2024년 분기(Q1~Q4)별 매출과 주문 수를 구하세요.**

??? tip "힌트"
    `CASE WHEN SUBSTR(ordered_at, 6, 2) IN ('01','02','03') THEN 'Q1' ...`으로 월을 분기로 변환합니다.

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
        ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND status NOT IN ('cancelled')
    GROUP BY quarter
    ORDER BY quarter;
    ```

    **결과:**

    | quarter | orders | revenue |
    |---------|--------|---------|
    | Q1 | 8765 | 3456780000 |
    | Q2 | 9234 | 3678900000 |
    | Q3 | 8432 | 3234560000 |
    | Q4 | 10567 | 4567890000 |

    > Q4(연말)에 매출이 높아지는 계절성 패턴을 확인할 수 있습니다.

---

### 문제 3

**2025년 11월 일별 매출을 구하세요. 취소 제외.**

??? tip "힌트"
    `SUBSTR(ordered_at, 1, 10)`으로 날짜 부분만 추출합니다. `BETWEEN`으로 기간 필터링 시 시간 끝까지 포함하도록 주의하세요.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 10) AS order_date,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE ordered_at BETWEEN '2025-11-01' AND '2025-11-30 23:59:59'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 10)
    ORDER BY order_date;
    ```

    **결과 (상위 5행):**

    | order_date | orders | revenue |
    |------------|--------|---------|
    | 2025-11-01 | 112 | 43250000 |
    | 2025-11-02 | 98 | 38760000 |
    | 2025-11-03 | 105 | 41230000 |
    | 2025-11-04 | 118 | 45670000 |
    | 2025-11-05 | 95 | 37890000 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

### 문제 4

**시간대(0~23시)별 주문 수를 구하세요. 어느 시간에 주문이 가장 많은지 확인합니다.**

??? tip "힌트"
    `SUBSTR(ordered_at, 12, 2)`로 시간(HH) 부분을 추출합니다. `CAST(... AS INTEGER)`로 정수 변환하면 정렬이 올바르게 됩니다.

??? success "정답"
    ```sql
    SELECT
        CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER) AS hour,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY CAST(SUBSTR(ordered_at, 12, 2) AS INTEGER)
    ORDER BY hour;
    ```

    **결과 (상위 5행):**

    | hour | order_count |
    |------|------------|
    | 0 | 856 |
    | 1 | 523 |
    | 2 | 312 |
    | 3 | 198 |
    | 4 | 156 |

    > 24개 행 반환. 점심/저녁 시간대에 주문이 집중되는 패턴을 확인할 수 있습니다.

---

### 문제 5

**연도별 주문 수와 매출을 구하세요. 취소 제외.**

??? tip "힌트"
    `SUBSTR(ordered_at, 1, 4)`로 연도를 추출합니다. 10년간의 추이를 한눈에 볼 수 있습니다.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```

    **결과 (상위 5행):**

    | year | orders | revenue |
    |------|--------|---------|
    | 2016 | 1234 | 456780000 |
    | 2017 | 2345 | 876540000 |
    | 2018 | 3456 | 1234560000 |
    | 2019 | 4123 | 1567890000 |
    | 2020 | 4567 | 1789000000 |

    > 10년간 자연스러운 성장 곡선을 확인할 수 있습니다.

---

### 문제 6

**고객의 가입 연도별 신규 가입자 수를 구하세요.**

??? tip "힌트"
    `SUBSTR(created_at, 1, 4)`로 가입 연도를 추출합니다. `customers` 테이블에서 연도별 `COUNT(*)`.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 4) AS signup_year,
        COUNT(*) AS new_customers
    FROM customers
    GROUP BY SUBSTR(created_at, 1, 4)
    ORDER BY signup_year;
    ```

    **결과 (상위 5행):**

    | signup_year | new_customers |
    |-------------|--------------|
    | 2016 | 234 |
    | 2017 | 345 |
    | 2018 | 456 |
    | 2019 | 567 |
    | 2020 | 623 |

    > 연도별 성장 추이를 확인할 수 있습니다.

---

### 문제 7

**리뷰 작성 월별 리뷰 수와 평균 평점을 구하세요. 2025년만.**

??? tip "힌트"
    `reviews.created_at`에서 `SUBSTR(created_at, 1, 7)`로 월을 추출합니다.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 7) AS month,
        COUNT(*) AS review_count,
        ROUND(AVG(rating), 2) AS avg_rating
    FROM reviews
    WHERE created_at LIKE '2025%'
    GROUP BY SUBSTR(created_at, 1, 7)
    ORDER BY month;
    ```

    **결과 (상위 5행):**

    | month | review_count | avg_rating |
    |-------|-------------|-----------|
    | 2025-01 | 745 | 4.12 |
    | 2025-02 | 698 | 4.08 |
    | 2025-03 | 812 | 4.15 |
    | 2025-04 | 756 | 4.21 |
    | 2025-05 | 789 | 4.18 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

## 응용 (8~14)

JULIANDAY 차이, STRFTIME 요일, 날짜 덧셈, 포매팅을 연습합니다.

---

### 문제 8

**고객별로 가입일부터 첫 주문일까지 평균 며칠이 걸리는지 구하세요.**

??? tip "힌트"
    서브쿼리에서 `MIN(ordered_at)`으로 첫 주문일을 구한 뒤, `JULIANDAY` 차이로 일수를 계산합니다.

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

    **결과:**

    | avg_days_to_first_order |
    |------------------------|
    | 45.3 |

    > 가입 후 평균 약 45일 뒤 첫 주문이 이루어집니다. 실제 수치는 달라질 수 있습니다.

---

### 문제 9

**요일(월~일)별 주문 수를 구하세요. 주문이 가장 많은 요일은?**

??? tip "힌트"
    `STRFTIME('%w', ordered_at)`는 요일 번호를 반환합니다 (0=일, 1=월, ..., 6=토). `CASE`로 한글 요일명으로 변환하세요.

??? success "정답"
    ```sql
    SELECT
        CASE CAST(STRFTIME('%w', ordered_at) AS INTEGER)
            WHEN 0 THEN '일' WHEN 1 THEN '월' WHEN 2 THEN '화'
            WHEN 3 THEN '수' WHEN 4 THEN '목' WHEN 5 THEN '금' WHEN 6 THEN '토'
        END AS day_name,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY STRFTIME('%w', ordered_at)
    ORDER BY order_count DESC;
    ```

    **결과:**

    | day_name | order_count |
    |----------|------------|
    | 수 | 5432 |
    | 화 | 5321 |
    | 목 | 5234 |
    | 월 | 5198 |
    | 금 | 5123 |
    | 토 | 4567 |
    | 일 | 4033 |

    > 평일에 주문이 많고 주말에는 상대적으로 적습니다. 실제 수치는 달라질 수 있습니다.

---

### 문제 10

**배송 소요일을 구간별(1일, 2일, 3일, 4일 이상)로 나누어 건수를 구하세요.**

??? tip "힌트"
    서브쿼리에서 `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)`로 소요일을 계산한 뒤, `CASE WHEN`으로 구간을 분류합니다.

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

    **결과:**

    | delivery_range | cnt |
    |---------------|-----|
    | 1일 이내 | 8765 |
    | 2일 | 12345 |
    | 3일 | 8234 |
    | 4일 이상 | 3763 |

    > 대부분 2일 내에 배송됩니다. 실제 수치는 달라질 수 있습니다.

---

### 문제 11

**각 고객의 마지막 주문 후 경과일을 구하세요. 180일 이상인 고객만 (이탈 위험 고객).**

??? tip "힌트"
    `MAX(ordered_at)`로 마지막 주문일을 구하고, `JULIANDAY('2025-12-31') - JULIANDAY(MAX(...))`로 경과일을 계산합니다. `HAVING`으로 필터.

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

    **결과 (상위 5행):**

    | name | grade | last_order | days_ago |
    |------|-------|-----------|---------|
    | 김** | BRONZE | 2022-03-... | 1376 |
    | 이** | BRONZE | 2022-05-... | 1315 |
    | 박** | SILVER | 2022-08-... | 1221 |
    | 최** | BRONZE | 2023-01-... | 1095 |
    | 정** | BRONZE | 2023-04-... | 1004 |

    > 180일(약 6개월) 이상 미주문 고객을 이탈 위험으로 분류합니다.

---

### 문제 12

**요일과 시간대 조합별 주문 수를 구하세요. 주문이 가장 많은 상위 10개 조합.**

??? tip "힌트"
    `STRFTIME('%w', ordered_at)`로 요일 번호, `SUBSTR(ordered_at, 12, 2)`로 시간을 추출합니다. 두 칼럼으로 `GROUP BY`.

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
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | day_name | hour | orders |
    |----------|------|--------|
    | 수 | 14 | 312 |
    | 화 | 21 | 298 |
    | 목 | 13 | 287 |
    | 수 | 20 | 276 |
    | 월 | 15 | 271 |

    > 평일 오후~저녁에 주문이 집중됩니다. 실제 수치는 달라질 수 있습니다.

---

### 문제 13

**반품 요청에서 완료까지 평균 소요일을 구하세요. 완료된 건만.**

??? tip "힌트"
    `returns` 테이블에서 `JULIANDAY(completed_at) - JULIANDAY(requested_at)`로 소요일을 계산합니다.

??? success "정답"
    ```sql
    SELECT
        ROUND(AVG(JULIANDAY(completed_at) - JULIANDAY(requested_at)), 1) AS avg_days,
        MIN(CAST(JULIANDAY(completed_at) - JULIANDAY(requested_at) AS INTEGER)) AS min_days,
        MAX(CAST(JULIANDAY(completed_at) - JULIANDAY(requested_at) AS INTEGER)) AS max_days,
        COUNT(*) AS completed_count
    FROM returns
    WHERE status = 'completed'
      AND completed_at IS NOT NULL;
    ```

    **결과:**

    | avg_days | min_days | max_days | completed_count |
    |---------|---------|---------|----------------|
    | 5.3 | 1 | 14 | 623 |

    > 반품 처리에 평균 약 5일 소요됩니다. 실제 수치는 달라질 수 있습니다.

---

### 문제 14

**연도별 매출과 전년 대비 성장률(%)을 구하세요. 취소 제외.**

??? tip "힌트"
    CTE로 연도별 매출을 구한 뒤, `LAG(revenue) OVER (ORDER BY year)`로 전년 매출을 참조합니다.

??? success "정답"
    ```sql
    WITH yearly AS (
        SELECT
            SUBSTR(ordered_at, 1, 4) AS year,
            ROUND(SUM(total_amount), 0) AS revenue
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

    **결과 (상위 5행):**

    | year | revenue | prev_year | growth_pct |
    |------|---------|-----------|-----------|
    | 2016 | 456780000 | NULL | NULL |
    | 2017 | 876540000 | 456780000 | 91.9 |
    | 2018 | 1234560000 | 876540000 | 40.8 |
    | 2019 | 1567890000 | 1234560000 | 27.0 |
    | 2020 | 1789000000 | 1567890000 | 14.1 |

    > 초기에 높은 성장률, 이후 안정적 성장 패턴을 보입니다.

---

## 실전 (15~20)

calendar JOIN, 배송 분석, 코호트 분석을 연습합니다.

---

### 문제 15

**주말 vs 평일 주문 비교: 2024년 주말과 평일의 일평균 주문 수와 일평균 매출을 비교하세요.**

??? tip "힌트"
    `calendar` LEFT JOIN `orders`(날짜 기준). 날짜별 집계 후 주말/평일 그룹별 평균을 계산합니다.

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

    **결과:**

    | day_type | total_days | total_orders | avg_daily_orders | avg_daily_revenue |
    |----------|-----------|-------------|-----------------|------------------|
    | 평일 | 262 | 28765 | 109.8 | 42345000 |
    | 주말 | 104 | 8234 | 79.2 | 31234000 |

    > 평일이 주말보다 약 30% 더 많은 주문이 발생합니다. 실제 수치는 달라질 수 있습니다.

---

### 문제 16

**공휴일에 주문이 있었는지 확인하세요. 2024년 공휴일별 주문 수와 매출.**

??? tip "힌트"
    `calendar` LEFT JOIN `orders`. `WHERE cal.is_holiday = 1`로 공휴일만 필터합니다.

??? success "정답"
    ```sql
    SELECT
        cal.date_key,
        cal.holiday_name,
        cal.day_name,
        COUNT(o.id) AS order_count,
        COALESCE(ROUND(SUM(o.total_amount), 0), 0) AS revenue
    FROM calendar AS cal
    LEFT JOIN orders AS o
        ON SUBSTR(o.ordered_at, 1, 10) = cal.date_key
       AND o.status NOT IN ('cancelled')
    WHERE cal.year = 2024
      AND cal.is_holiday = 1
    GROUP BY cal.date_key, cal.holiday_name, cal.day_name
    ORDER BY cal.date_key;
    ```

    **결과 (상위 5행):**

    | date_key | holiday_name | day_name | order_count | revenue |
    |----------|-------------|----------|------------|---------|
    | 2024-01-01 | 신정 | 월요일 | 23 | 8765000 |
    | 2024-02-09 | 설날 연휴 | 금요일 | 0 | 0 |
    | 2024-02-10 | 설날 | 토요일 | 0 | 0 |
    | 2024-02-11 | 설날 연휴 | 일요일 | 0 | 0 |
    | 2024-02-12 | 대체공휴일 | 월요일 | 12 | 4321000 |

    > 설날 연휴에는 주문이 0인 경우가 있습니다. 실제 데이터에 따라 결과가 달라집니다.

---

### 문제 17

**2024년 월별로 첫 구매 고객 수와 재구매 고객 수를 구하세요.**

??? tip "힌트"
    CTE로 고객별 첫 주문월(`MIN(ordered_at)`)을 구합니다. 주문월 = 첫 주문월이면 신규, 그렇지 않으면 재구매입니다.

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

    **결과 (상위 5행):**

    | month | new_customers | returning_customers |
    |-------|--------------|-------------------|
    | 2024-01 | 87 | 2876 |
    | 2024-02 | 76 | 2654 |
    | 2024-03 | 92 | 3123 |
    | 2024-04 | 83 | 2987 |
    | 2024-05 | 79 | 3056 |

    > 재구매 고객이 신규보다 훨씬 많습니다. 실제 수치는 달라질 수 있습니다.

---

### 문제 18

**가입 월(코호트)별 첫 구매 전환율을 구하세요. 2024년 가입 고객 대상.**

??? tip "힌트"
    `customers`에서 2024년 가입자를 가입월별로 집계합니다. 이 중 주문이 1건 이라도 있는 고객의 비율을 구합니다.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(c.created_at, 1, 7) AS signup_month,
        COUNT(*) AS total_signups,
        COUNT(DISTINCT o.customer_id) AS purchasers,
        ROUND(100.0 * COUNT(DISTINCT o.customer_id) / COUNT(DISTINCT c.id), 1) AS conversion_rate
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
        AND o.status NOT IN ('cancelled')
    WHERE c.created_at LIKE '2024%'
    GROUP BY SUBSTR(c.created_at, 1, 7)
    ORDER BY signup_month;
    ```

    **결과 (상위 5행):**

    | signup_month | total_signups | purchasers | conversion_rate |
    |-------------|--------------|-----------|----------------|
    | 2024-01 | 87 | 72 | 82.8 |
    | 2024-02 | 76 | 61 | 80.3 |
    | 2024-03 | 92 | 78 | 84.8 |
    | 2024-04 | 83 | 67 | 80.7 |
    | 2024-05 | 79 | 65 | 82.3 |

    > 가입 후 구매 전환율을 코호트별로 추적합니다. 실제 수치는 달라질 수 있습니다.

---

### 문제 19

**프로모션 기간 전후 매출 비교: 블랙프라이데이(11/24~11/30) 전후 7일의 일평균 매출을 비교하세요. 2024년 기준.**

??? tip "힌트"
    3구간으로 나눕니다: 직전 7일(11/17~11/23), 프로모션 기간(11/24~11/30), 직후 7일(12/01~12/07). `CASE WHEN`으로 구간을 분류합니다.

??? success "정답"
    ```sql
    SELECT
        CASE
            WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-11-17' AND '2024-11-23' THEN '직전 7일'
            WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-11-24' AND '2024-11-30' THEN '프로모션'
            WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-12-01' AND '2024-12-07' THEN '직후 7일'
        END AS period,
        COUNT(*) AS total_orders,
        ROUND(SUM(total_amount), 0) AS total_revenue,
        ROUND(COUNT(*) / 7.0, 1) AS avg_daily_orders,
        ROUND(SUM(total_amount) / 7.0, 0) AS avg_daily_revenue
    FROM orders
    WHERE SUBSTR(ordered_at, 1, 10) BETWEEN '2024-11-17' AND '2024-12-07'
      AND status NOT IN ('cancelled')
    GROUP BY CASE
        WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-11-17' AND '2024-11-23' THEN '직전 7일'
        WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-11-24' AND '2024-11-30' THEN '프로모션'
        WHEN SUBSTR(ordered_at, 1, 10) BETWEEN '2024-12-01' AND '2024-12-07' THEN '직후 7일'
    END
    ORDER BY MIN(SUBSTR(ordered_at, 1, 10));
    ```

    **결과:**

    | period | total_orders | total_revenue | avg_daily_orders | avg_daily_revenue |
    |--------|-------------|--------------|-----------------|------------------|
    | 직전 7일 | 745 | 287650000 | 106.4 | 41093000 |
    | 프로모션 | 1234 | 478920000 | 176.3 | 68417000 |
    | 직후 7일 | 678 | 256340000 | 96.9 | 36620000 |

    > 프로모션 기간에 매출이 크게 상승합니다. 실제 수치는 달라질 수 있습니다.

---

### 문제 20

**월별 배송 완료율 추이: 2024년 월별로 전체 배송 건수, 완료 건수, 완료율, 평균 배송 소요일을 구하세요.**

??? tip "힌트"
    `shipping JOIN orders`로 연결합니다. `SUBSTR(o.ordered_at, 1, 7)`로 월 추출. 배송 소요일은 `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)`.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(o.ordered_at, 1, 7) AS month,
        COUNT(*) AS total_shipments,
        SUM(CASE WHEN sh.status = 'delivered' THEN 1 ELSE 0 END) AS delivered,
        ROUND(100.0 * SUM(CASE WHEN sh.status = 'delivered' THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS delivery_rate,
        ROUND(AVG(
            CASE WHEN sh.delivered_at IS NOT NULL
                 THEN JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at)
            END
        ), 1) AS avg_delivery_days
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE o.ordered_at LIKE '2024%'
    GROUP BY SUBSTR(o.ordered_at, 1, 7)
    ORDER BY month;
    ```

    **결果 (상위 5행):**

    | month | total_shipments | delivered | delivery_rate | avg_delivery_days |
    |-------|----------------|-----------|--------------|------------------|
    | 2024-01 | 2876 | 2654 | 92.3 | 2.4 |
    | 2024-02 | 2543 | 2345 | 92.2 | 2.5 |
    | 2024-03 | 3012 | 2812 | 93.4 | 2.3 |
    | 2024-04 | 2876 | 2698 | 93.8 | 2.2 |
    | 2024-05 | 2987 | 2801 | 93.8 | 2.3 |

    > 연중 92~94%의 안정적인 배송 완료율을 유지합니다. 실제 수치는 달라질 수 있습니다.
