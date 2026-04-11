# 윈도우 함수 실전

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `orders` — 주문 (상태, 금액, 일시) · `order_items` — 주문 상세 (수량, 단가) · `products` — 상품 (이름, 가격, 재고, 브랜드) · `customers` — 고객 (등급, 포인트, 가입채널) · `reviews` — 리뷰 (평점, 내용) · `payments` — 결제 (방법, 금액, 상태) · `categories` — 카테고리 (부모-자식 계층)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `LAG`, `LEAD`, `SUM/AVG/COUNT OVER`, `FIRST_VALUE`, `LAST_VALUE`, `ROWS BETWEEN`

</div>

!!! info "시작하기 전에"
    이 연습은 **고급 18강**(윈도우 함수)에서 배운 내용을 실전에 적용합니다.
    모든 쿼리는 SQLite에서 실행 가능합니다. 취소/반품 주문 제외 조건: `status NOT IN ('cancelled', 'returned', 'return_requested')`

---

## 기초 (1~5)

윈도우 함수의 기본 구문을 연습합니다.

---

### 문제 1

**각 고객의 주문을 시간순으로 정렬하여, 고객별 주문 순번을 매기세요.**

고객 ID, 고객명, 주문번호, 주문일, 주문금액, 그리고 해당 고객 내에서 몇 번째 주문인지(`order_seq`)를 표시합니다.
상위 20행만 출력하세요.

??? tip "힌트"
    `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`를 사용합니다.
    `PARTITION BY customer_id`로 고객별로 그룹을 나누고, `ORDER BY ordered_at`으로 시간순 정렬합니다.

??? success "정답"
    ```sql
    SELECT
        c.id             AS customer_id,
        c.name           AS customer_name,
        o.order_number,
        o.ordered_at,
        o.total_amount,
        ROW_NUMBER() OVER (
            PARTITION BY c.id
            ORDER BY o.ordered_at
        ) AS order_seq
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY c.id, order_seq
    LIMIT 20;
    ```

    **결과 예시 (상위 5행):**

    | customer_id | customer_name | order_number | ordered_at | total_amount | order_seq |
    |---|---|---|---|---|---|
    | 1 | 김... | ORD-20170523-00001 | 2017-05-23 ... | 125000 | 1 |
    | 1 | 김... | ORD-20180114-00042 | 2018-01-14 ... | 340000 | 2 |
    | 1 | 김... | ORD-20190805-00103 | 2019-08-05 ... | 78000 | 3 |
    | 2 | 이... | ORD-20170801-00005 | 2017-08-01 ... | 560000 | 1 |
    | 2 | 이... | ORD-20180322-00067 | 2018-03-22 ... | 210000 | 2 |

---

### 문제 2

**2024년 월별 매출 순위를 매기세요. 동일 매출이면 같은 순위를 부여합니다.**

각 월의 총 매출, `RANK`와 `DENSE_RANK` 값을 모두 표시하여 차이를 비교하세요.

??? tip "힌트"
    먼저 `SUBSTR(ordered_at, 1, 7)`로 월별 매출을 집계한 서브쿼리(또는 CTE)를 만들고,
    그 결과에 `RANK() OVER (ORDER BY revenue DESC)`와 `DENSE_RANK()`를 적용합니다.

??? success "정답"
    ```sql
    WITH monthly_revenue AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        RANK()       OVER (ORDER BY revenue DESC) AS rank_val,
        DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank_val
    FROM monthly_revenue
    ORDER BY year_month;
    ```

    **결과 예시:**

    | year_month | revenue | rank_val | dense_rank_val |
    |---|---|---|---|
    | 2024-01 | 98500000 | 8 | 8 |
    | 2024-02 | 87200000 | 11 | 11 |
    | 2024-03 | 102300000 | 5 | 5 |
    | ... | ... | ... | ... |
    | 2024-12 | 145600000 | 1 | 1 |

    > `RANK`는 동점 시 다음 순위를 건너뛰고, `DENSE_RANK`는 건너뛰지 않습니다.

---

### 문제 3

**상품별 총 매출과 함께, 해당 카테고리 내에서의 매출 비중(%)을 구하세요.**

2024년 기준, 상위 15개 상품을 매출 내림차순으로 표시합니다.

??? tip "힌트"
    `SUM(매출) OVER (PARTITION BY category_id)`로 카테고리 전체 매출을 구하고,
    개별 상품 매출을 카테고리 매출로 나누면 비중이 됩니다.

??? success "정답"
    ```sql
    SELECT
        p.name            AS product_name,
        cat.name          AS category,
        ROUND(SUM(oi.quantity * oi.unit_price), 0) AS product_revenue,
        ROUND(SUM(SUM(oi.quantity * oi.unit_price)) OVER (
            PARTITION BY p.category_id
        ), 0) AS category_revenue,
        ROUND(100.0 * SUM(oi.quantity * oi.unit_price)
            / SUM(SUM(oi.quantity * oi.unit_price)) OVER (PARTITION BY p.category_id),
        1) AS pct_of_category
    FROM order_items AS oi
    INNER JOIN orders     AS o   ON oi.order_id   = o.id
    INNER JOIN products   AS p   ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY p.id, p.name, cat.name, p.category_id
    ORDER BY product_revenue DESC
    LIMIT 15;
    ```

    **결과 예시 (상위 3행):**

    | product_name | category | product_revenue | category_revenue | pct_of_category |
    |---|---|---|---|---|
    | MacBook Pro 16 M3 | 노트북 | 45200000 | 182500000 | 24.8 |
    | LG 울트라기어 27GP950 | 모니터 | 32100000 | 98700000 | 32.5 |
    | 삼성 Galaxy Book4 Pro | 노트북 | 28900000 | 182500000 | 15.8 |

---

### 문제 4

**각 고객의 주문 금액에 대해 누적 합계(running total)를 계산하세요.**

고객 ID 1~5번에 대해, 주문 시간순으로 누적 주문 금액을 표시합니다.

??? tip "힌트"
    `SUM(total_amount) OVER (PARTITION BY customer_id ORDER BY ordered_at ROWS UNBOUNDED PRECEDING)`
    이 구문이 누적 합계(running total)를 만듭니다.

??? success "정답"
    ```sql
    SELECT
        c.id            AS customer_id,
        c.name          AS customer_name,
        o.ordered_at,
        o.total_amount,
        SUM(o.total_amount) OVER (
            PARTITION BY c.id
            ORDER BY o.ordered_at
            ROWS UNBOUNDED PRECEDING
        ) AS running_total
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE c.id BETWEEN 1 AND 5
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY c.id, o.ordered_at;
    ```

    **결과 예시:**

    | customer_id | customer_name | ordered_at | total_amount | running_total |
    |---|---|---|---|---|
    | 1 | 김... | 2017-05-23 ... | 125000 | 125000 |
    | 1 | 김... | 2018-01-14 ... | 340000 | 465000 |
    | 1 | 김... | 2019-08-05 ... | 78000 | 543000 |
    | 2 | 이... | 2017-08-01 ... | 560000 | 560000 |
    | 2 | 이... | 2018-03-22 ... | 210000 | 770000 |

---

### 문제 5

**결제 건수 기준으로 결제 수단을 4개 그룹(분위)으로 나누세요.**

2024년 완료된 결제(`status = 'completed'`)를 수단별로 집계하고, `NTILE(4)`로 분위를 매깁니다.

??? tip "힌트"
    먼저 결제 수단별 건수를 집계한 CTE를 만들고,
    `NTILE(4) OVER (ORDER BY payment_count DESC)`로 4분위를 나눕니다.
    1분위가 가장 많이 사용된 그룹입니다.

??? success "정답"
    ```sql
    WITH method_stats AS (
        SELECT
            method,
            COUNT(*)              AS payment_count,
            ROUND(SUM(amount), 0) AS total_amount
        FROM payments
        WHERE status = 'completed'
          AND paid_at LIKE '2024%'
        GROUP BY method
    )
    SELECT
        method,
        payment_count,
        total_amount,
        NTILE(4) OVER (ORDER BY payment_count DESC) AS quartile
    FROM method_stats
    ORDER BY payment_count DESC;
    ```

    **결과 예시:**

    | method | payment_count | total_amount | quartile |
    |---|---|---|---|
    | card | 4520 | 582000000 | 1 |
    | kakao_pay | 2310 | 198000000 | 1 |
    | naver_pay | 1890 | 167000000 | 2 |
    | bank_transfer | 980 | 112000000 | 3 |
    | virtual_account | 450 | 56000000 | 3 |
    | point | 120 | 8500000 | 4 |

---

## 응용 (6~10)

LAG/LEAD, 이동 평균 등 분석 함수를 활용합니다.

---

### 문제 6

**월별 매출의 전월 대비 증감액과 증감률을 구하세요.**

2023~2024년 데이터를 사용합니다.

??? tip "힌트"
    `LAG(revenue, 1) OVER (ORDER BY year_month)`로 이전 월 매출을 가져옵니다.
    증감률은 `(당월 - 전월) / 전월 * 100`으로 계산합니다.

??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at >= '2023-01-01'
          AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        LAG(revenue, 1) OVER (ORDER BY year_month) AS prev_revenue,
        revenue - LAG(revenue, 1) OVER (ORDER BY year_month) AS diff,
        ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY year_month))
            / LAG(revenue, 1) OVER (ORDER BY year_month), 1) AS growth_pct
    FROM monthly
    ORDER BY year_month;
    ```

    **결과 예시 (일부):**

    | year_month | revenue | prev_revenue | diff | growth_pct |
    |---|---|---|---|---|
    | 2023-01 | 85000000 | NULL | NULL | NULL |
    | 2023-02 | 78000000 | 85000000 | -7000000 | -8.2 |
    | 2023-03 | 95000000 | 78000000 | 17000000 | 21.8 |
    | ... | ... | ... | ... | ... |

    > 첫 번째 행의 `prev_revenue`는 이전 데이터가 없으므로 NULL입니다.

---

### 문제 7

**고객의 다음 주문까지 걸린 일수를 계산하세요.**

VIP 등급 고객에 대해, 각 주문과 다음 주문 사이의 간격(일)을 구합니다.
평균 간격이 가장 짧은 상위 10명을 표시하세요.

??? tip "힌트"
    `LEAD(ordered_at, 1) OVER (PARTITION BY customer_id ORDER BY ordered_at)`로 다음 주문일을 가져오고,
    `JULIANDAY(next_order) - JULIANDAY(ordered_at)`로 간격을 계산합니다.

??? success "정답"
    ```sql
    WITH order_gaps AS (
        SELECT
            o.customer_id,
            c.name,
            o.ordered_at,
            LEAD(o.ordered_at, 1) OVER (
                PARTITION BY o.customer_id
                ORDER BY o.ordered_at
            ) AS next_order_at,
            ROUND(
                JULIANDAY(LEAD(o.ordered_at, 1) OVER (
                    PARTITION BY o.customer_id
                    ORDER BY o.ordered_at
                )) - JULIANDAY(o.ordered_at),
            0) AS days_to_next
        FROM orders AS o
        INNER JOIN customers AS c ON o.customer_id = c.id
        WHERE c.grade = 'VIP'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        customer_id,
        name,
        COUNT(days_to_next)       AS gap_count,
        ROUND(AVG(days_to_next), 1) AS avg_days_between,
        MIN(days_to_next)           AS min_gap,
        MAX(days_to_next)           AS max_gap
    FROM order_gaps
    WHERE days_to_next IS NOT NULL
    GROUP BY customer_id, name
    ORDER BY avg_days_between ASC
    LIMIT 10;
    ```

    **결과 예시 (상위 3행):**

    | customer_id | name | gap_count | avg_days_between | min_gap | max_gap |
    |---|---|---|---|---|---|
    | 142 | 박... | 18 | 42.3 | 5 | 120 |
    | 87 | 최... | 15 | 48.7 | 12 | 95 |
    | 231 | 정... | 22 | 51.2 | 3 | 145 |

---

### 문제 8

**3개월 이동 평균 매출을 구하세요.**

2023~2024년 월별 매출에 대해, 현재 월 포함 직전 3개월의 이동 평균을 계산합니다.

??? tip "힌트"
    `AVG(revenue) OVER (ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`
    이 구문이 현재 행 포함 이전 2행(총 3행)의 평균을 계산합니다.

??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at >= '2023-01-01'
          AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 0) AS moving_avg_3m,
        COUNT(*) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS window_size
    FROM monthly
    ORDER BY year_month;
    ```

    **결과 예시 (일부):**

    | year_month | revenue | moving_avg_3m | window_size |
    |---|---|---|---|
    | 2023-01 | 85000000 | 85000000 | 1 |
    | 2023-02 | 78000000 | 81500000 | 2 |
    | 2023-03 | 95000000 | 86000000 | 3 |
    | 2023-04 | 88000000 | 87000000 | 3 |
    | ... | ... | ... | 3 |

    > `window_size`가 3 미만인 초기 행은 이동 평균이 정확하지 않으니 참고용입니다.

---

### 문제 9

**카테고리별로 가장 비싼 상품과 가장 저렴한 상품의 이름을 한 행에 표시하세요.**

`FIRST_VALUE`와 `LAST_VALUE`를 사용합니다.

??? tip "힌트"
    `FIRST_VALUE(name) OVER (PARTITION BY category_id ORDER BY price DESC)`는 가장 비싼 상품명입니다.
    `LAST_VALUE` 사용 시 반드시 `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`을 명시해야 전체 파티션을 봅니다.

??? success "정답"
    ```sql
    WITH ranked AS (
        SELECT DISTINCT
            cat.name AS category,
            FIRST_VALUE(p.name) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS most_expensive,
            FIRST_VALUE(p.price) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS max_price,
            LAST_VALUE(p.name) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS cheapest,
            LAST_VALUE(p.price) OVER (
                PARTITION BY p.category_id
                ORDER BY p.price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS min_price
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
    )
    SELECT DISTINCT
        category,
        most_expensive,
        max_price,
        cheapest,
        min_price
    FROM ranked
    ORDER BY category;
    ```

    **결과 예시 (상위 3행):**

    | category | most_expensive | max_price | cheapest | min_price |
    |---|---|---|---|---|
    | CPU | AMD Ryzen 9 7950X3D | 789000 | Intel Core i3-13100 | 159000 |
    | GPU | NVIDIA RTX 4090 ... | 2890000 | AMD RX 7600 ... | 379000 |
    | SSD | Samsung 990 PRO 4TB | 650000 | Kingston A400 240GB | 29000 |

---

### 문제 10

**리뷰 평점 기준으로 상품을 5개 등급(NTILE)으로 나누고, 각 등급의 통계를 구하세요.**

리뷰가 3건 이상인 상품만 대상으로 합니다.

??? tip "힌트"
    먼저 상품별 평균 평점을 구하고(`HAVING COUNT(*) >= 3`),
    그 결과에 `NTILE(5) OVER (ORDER BY avg_rating)`로 등급을 나눈 뒤,
    등급별로 다시 집계합니다.

??? success "정답"
    ```sql
    WITH product_ratings AS (
        SELECT
            p.id,
            p.name,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(*)                AS review_count
        FROM reviews AS r
        INNER JOIN products AS p ON r.product_id = p.id
        GROUP BY p.id, p.name
        HAVING COUNT(*) >= 3
    ),
    tiered AS (
        SELECT
            *,
            NTILE(5) OVER (ORDER BY avg_rating) AS tier
        FROM product_ratings
    )
    SELECT
        tier,
        COUNT(*)                     AS product_count,
        ROUND(MIN(avg_rating), 2)    AS min_rating,
        ROUND(MAX(avg_rating), 2)    AS max_rating,
        ROUND(AVG(avg_rating), 2)    AS avg_of_avg,
        ROUND(AVG(review_count), 1)  AS avg_reviews
    FROM tiered
    GROUP BY tier
    ORDER BY tier;
    ```

    **결과 예시:**

    | tier | product_count | min_rating | max_rating | avg_of_avg | avg_reviews |
    |---|---|---|---|---|---|
    | 1 | 22 | 1.50 | 2.80 | 2.35 | 4.8 |
    | 2 | 22 | 2.85 | 3.40 | 3.12 | 5.2 |
    | 3 | 22 | 3.42 | 3.90 | 3.65 | 6.1 |
    | 4 | 22 | 3.92 | 4.30 | 4.10 | 7.3 |
    | 5 | 22 | 4.32 | 5.00 | 4.58 | 8.9 |

---

## 실전 (11~15)

복합적인 윈도우 함수 조합으로 실무 분석 시나리오를 해결합니다.

---

### 문제 11

**고객 등급별로 주문 금액 순위를 매기고, 등급 내 상위 3명의 정보를 추출하세요.**

각 등급(BRONZE, SILVER, GOLD, VIP)에서 총 주문 금액 기준 상위 3명을 보여줍니다.

??? tip "힌트"
    CTE에서 고객별 총 주문 금액을 집계한 뒤, `ROW_NUMBER() OVER (PARTITION BY grade ORDER BY total_spent DESC)`로
    등급별 순위를 매기고, 외부 쿼리에서 `WHERE rn <= 3`으로 필터링합니다.

??? success "정답"
    ```sql
    WITH customer_totals AS (
        SELECT
            c.id,
            c.name,
            c.grade,
            COUNT(*)                    AS order_count,
            ROUND(SUM(o.total_amount), 0) AS total_spent
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    ),
    ranked AS (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY grade
                ORDER BY total_spent DESC
            ) AS rn
        FROM customer_totals
    )
    SELECT
        grade,
        rn   AS rank_in_grade,
        name AS customer_name,
        order_count,
        total_spent
    FROM ranked
    WHERE rn <= 3
    ORDER BY
        CASE grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
        END,
        rn;
    ```

    **결과 예시:**

    | grade | rank_in_grade | customer_name | order_count | total_spent |
    |---|---|---|---|---|
    | VIP | 1 | 김... | 35 | 12500000 |
    | VIP | 2 | 박... | 28 | 10800000 |
    | VIP | 3 | 이... | 31 | 9950000 |
    | GOLD | 1 | 최... | 22 | 7200000 |
    | ... | ... | ... | ... | ... |

---

### 문제 12

**상품별 월간 매출 추이와 함께, 해당 상품의 전체 평균 대비 비율을 표시하세요.**

2024년 상위 5개 상품에 대해, 월별 매출과 해당 상품 전체 월 평균 매출 대비 비율(%)을 구합니다.

??? tip "힌트"
    1단계: 상품-월별 매출 집계. 2단계: 상위 5개 상품 선별(총 매출 기준).
    3단계: `AVG(monthly_revenue) OVER (PARTITION BY product_id)`로 상품별 전체 평균을 구하고,
    월별 매출을 평균으로 나누어 비율을 계산합니다.

??? success "정답"
    ```sql
    WITH product_monthly AS (
        SELECT
            p.id       AS product_id,
            p.name     AS product_name,
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS monthly_revenue
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name, SUBSTR(o.ordered_at, 1, 7)
    ),
    top5 AS (
        SELECT product_id
        FROM product_monthly
        GROUP BY product_id
        ORDER BY SUM(monthly_revenue) DESC
        LIMIT 5
    )
    SELECT
        pm.product_name,
        pm.year_month,
        pm.monthly_revenue,
        ROUND(AVG(pm.monthly_revenue) OVER (
            PARTITION BY pm.product_id
        ), 0) AS avg_monthly,
        ROUND(100.0 * pm.monthly_revenue
            / AVG(pm.monthly_revenue) OVER (PARTITION BY pm.product_id),
        1) AS pct_of_avg
    FROM product_monthly AS pm
    INNER JOIN top5 AS t ON pm.product_id = t.product_id
    ORDER BY pm.product_name, pm.year_month;
    ```

    **결과 예시 (일부):**

    | product_name | year_month | monthly_revenue | avg_monthly | pct_of_avg |
    |---|---|---|---|---|
    | MacBook Pro 16 M3 | 2024-01 | 3800000 | 3770000 | 100.8 |
    | MacBook Pro 16 M3 | 2024-02 | 2900000 | 3770000 | 76.9 |
    | MacBook Pro 16 M3 | 2024-11 | 5200000 | 3770000 | 137.9 |

---

### 문제 13

**결제 수단별 월간 점유율 변화를 추적하세요.**

2024년 월별로 각 결제 수단이 차지하는 비중(%)을 구하고, 전월 대비 점유율 변동(pp)을 계산합니다.

??? tip "힌트"
    월-결제수단별 금액을 구한 뒤, `SUM(amount) OVER (PARTITION BY year_month)`으로 월 전체 합계를 구합니다.
    `LAG(share_pct, 1) OVER (PARTITION BY method ORDER BY year_month)`로 전월 점유율을 가져옵니다.

??? success "정답"
    ```sql
    WITH method_monthly AS (
        SELECT
            SUBSTR(paid_at, 1, 7) AS year_month,
            method,
            ROUND(SUM(amount), 0) AS method_amount
        FROM payments
        WHERE status = 'completed'
          AND paid_at LIKE '2024%'
        GROUP BY SUBSTR(paid_at, 1, 7), method
    ),
    with_share AS (
        SELECT
            year_month,
            method,
            method_amount,
            ROUND(100.0 * method_amount
                / SUM(method_amount) OVER (PARTITION BY year_month),
            1) AS share_pct
        FROM method_monthly
    )
    SELECT
        year_month,
        method,
        method_amount,
        share_pct,
        LAG(share_pct, 1) OVER (
            PARTITION BY method
            ORDER BY year_month
        ) AS prev_share_pct,
        ROUND(share_pct - LAG(share_pct, 1) OVER (
            PARTITION BY method
            ORDER BY year_month
        ), 1) AS share_change_pp
    FROM with_share
    ORDER BY year_month, share_pct DESC;
    ```

    **결과 예시 (일부):**

    | year_month | method | method_amount | share_pct | prev_share_pct | share_change_pp |
    |---|---|---|---|---|---|
    | 2024-01 | card | 48000000 | 55.2 | NULL | NULL |
    | 2024-01 | kakao_pay | 18000000 | 20.7 | NULL | NULL |
    | 2024-02 | card | 42000000 | 53.8 | 55.2 | -1.4 |
    | 2024-02 | kakao_pay | 17500000 | 22.4 | 20.7 | 1.7 |

---

### 문제 14

**고객별 주문 금액의 갭(Gap) 분석을 수행하세요.**

각 고객의 주문을 금액 순으로 정렬했을 때, 이전 주문 대비 금액 차이가 가장 큰 "점프"를 찾습니다.
점프 금액이 50만원 이상인 경우만 추출하세요.

??? tip "힌트"
    `LAG(total_amount, 1) OVER (PARTITION BY customer_id ORDER BY total_amount)`로
    금액 순 이전 주문 금액을 가져옵니다. 차이를 구해 50만원 이상인 행만 필터링합니다.

??? success "정답"
    ```sql
    WITH ordered AS (
        SELECT
            o.customer_id,
            c.name,
            o.order_number,
            o.total_amount,
            LAG(o.total_amount, 1) OVER (
                PARTITION BY o.customer_id
                ORDER BY o.total_amount
            ) AS prev_amount
        FROM orders AS o
        INNER JOIN customers AS c ON o.customer_id = c.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        customer_id,
        name,
        order_number,
        prev_amount,
        total_amount,
        total_amount - prev_amount AS gap
    FROM ordered
    WHERE prev_amount IS NOT NULL
      AND (total_amount - prev_amount) >= 500000
    ORDER BY gap DESC
    LIMIT 20;
    ```

    **결과 예시 (상위 3행):**

    | customer_id | name | order_number | prev_amount | total_amount | gap |
    |---|---|---|---|---|---|
    | 45 | 한... | ORD-20240315-... | 85000 | 2890000 | 2805000 |
    | 112 | 송... | ORD-20231122-... | 120000 | 1950000 | 1830000 |
    | 78 | 윤... | ORD-20240601-... | 250000 | 1780000 | 1530000 |

---

### 문제 15

**연도별(YoY) 매출 성장률을 윈도우 함수로 계산하고, 분기별 추세도 함께 표시하세요.**

각 분기의 매출, 전년 동분기 매출, YoY 성장률을 구합니다.

??? tip "힌트"
    분기는 `(CAST(SUBSTR(ordered_at,6,2) AS INTEGER) + 2) / 3`으로 계산합니다.
    `LAG(revenue, 4) OVER (ORDER BY year, quarter)`로 4분기 전(= 전년 동분기) 값을 가져옵니다.

??? success "정답"
    ```sql
    WITH quarterly AS (
        SELECT
            CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER) AS year,
            (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3 AS quarter,
            ROUND(SUM(total_amount), 0) AS revenue,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2020-01-01'
        GROUP BY
            CAST(SUBSTR(ordered_at, 1, 4) AS INTEGER),
            (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3
    )
    SELECT
        year,
        quarter,
        revenue,
        order_count,
        LAG(revenue, 4) OVER (ORDER BY year, quarter) AS prev_year_revenue,
        CASE
            WHEN LAG(revenue, 4) OVER (ORDER BY year, quarter) IS NOT NULL
            THEN ROUND(100.0 * (revenue - LAG(revenue, 4) OVER (ORDER BY year, quarter))
                / LAG(revenue, 4) OVER (ORDER BY year, quarter), 1)
        END AS yoy_growth_pct
    FROM quarterly
    ORDER BY year, quarter;
    ```

    **결과 예시 (일부):**

    | year | quarter | revenue | order_count | prev_year_revenue | yoy_growth_pct |
    |---|---|---|---|---|---|
    | 2020 | 1 | 52000000 | 320 | NULL | NULL |
    | 2020 | 2 | 48000000 | 290 | NULL | NULL |
    | ... | ... | ... | ... | ... | ... |
    | 2021 | 1 | 68000000 | 410 | 52000000 | 30.8 |
    | 2021 | 2 | 61000000 | 380 | 48000000 | 27.1 |
    | ... | ... | ... | ... | ... | ... |
    | 2024 | 4 | 145000000 | 890 | 118000000 | 22.9 |

    > 첫 해(2020년)는 전년 데이터가 없으므로 `prev_year_revenue`와 `yoy_growth_pct`가 NULL입니다.
