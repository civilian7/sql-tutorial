# 매출 분석

!!! info "사용 테이블"
    `orders` — 주문 (상태, 금액, 일시)  
    `order_items` — 주문 상세 (수량, 단가)  
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `categories` — 카테고리 (부모-자식 계층)  
    `customers` — 고객 (등급, 포인트, 가입채널)  
    `payments` — 결제 (방법, 금액, 상태)  

!!! abstract "학습 범위"
    CTE, 윈도우 함수, 다중 JOIN, 집계 함수 종합 — 월별/분기별/카테고리별 매출, 성장률, 누적 매출, 코호트

CTE, 윈도우 함수, 다중 JOIN, 집계 함수를 종합 활용하는 비즈니스 매출 분석 문제입니다.
취소(`cancelled`), 반품(`returned`, `return_requested`) 주문은 특별히 명시하지 않는 한 제외합니다.

---

### 문제 1. 월별 매출 추이 (최근 3년)

2022~2024년 월별 매출, 주문 수, 평균 주문 금액을 구하세요.

??? tip "힌트"
    - `SUBSTR(ordered_at, 1, 7)`로 연-월 추출
    - `SUM(total_amount)`, `COUNT(*)`, `AVG(total_amount)`

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7)   AS year_month,
        COUNT(*)                   AS order_count,
        ROUND(SUM(total_amount))   AS revenue,
        ROUND(AVG(total_amount))   AS avg_order_value
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
      AND ordered_at >= '2022-01-01'
      AND ordered_at < '2025-01-01'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY year_month;
    ```

    | year_month | order_count | revenue | avg_order_value |
    |---|---|---|---|
    | 2022-01 | 320 | 198000000 | 618750 |
    | 2022-02 | 285 | 175000000 | 614035 |
    | ... | ... | ... | ... |

---

### 문제 2. 카테고리별 매출 비중

2024년 대분류 카테고리별 매출과 전체 대비 비중(%)을 구하세요.

??? tip "힌트"
    - `categories.depth = 0`이 대분류
    - 소분류 → 중분류 → 대분류 경로: `categories` 자기 참조를 두 번 JOIN
    - 또는 depth=0인 최상위 카테고리를 찾는 서브쿼리 사용

??? success "정답"
    ```sql
    WITH category_revenue AS (
        SELECT
            COALESCE(top_cat.name, mid_cat.name, cat.name) AS top_category,
            SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        LEFT JOIN categories AS mid_cat ON cat.parent_id = mid_cat.id
        LEFT JOIN categories AS top_cat ON mid_cat.parent_id = top_cat.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY COALESCE(top_cat.name, mid_cat.name, cat.name)
    )
    SELECT
        top_category,
        ROUND(revenue) AS revenue,
        ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS revenue_pct
    FROM category_revenue
    ORDER BY revenue DESC;
    ```

    | top_category | revenue | revenue_pct |
    |---|---|---|
    | 컴퓨터 | 5200000000 | 45.2 |
    | 주변기기 | 3100000000 | 26.9 |
    | ... | ... | ... |

---

### 문제 3. 상위 20명 고객 매출 순위

전체 기간에서 총 구매 금액 상위 20명의 고객 정보를 표시하세요.
고객명, 등급, 주문 횟수, 총 구매 금액, 순위를 포함합니다.

??? tip "힌트"
    - `RANK()` 또는 `ROW_NUMBER()` 윈도우 함수 사용
    - `customers` + `orders` JOIN

??? success "정답"
    ```sql
    SELECT
        RANK() OVER (ORDER BY SUM(o.total_amount) DESC) AS ranking,
        c.name          AS customer_name,
        c.grade,
        COUNT(*)        AS order_count,
        ROUND(SUM(o.total_amount)) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 20;
    ```

    | ranking | customer_name | grade | order_count | total_spent |
    |---|---|---|---|---|
    | 1 | 김민수 | VIP | 45 | 52000000 |
    | 2 | 이서연 | VIP | 38 | 48000000 |
    | ... | ... | ... | ... | ... |

---

### 문제 4. 요일별 매출 패턴

전체 주문 데이터에서 요일별(월~일) 평균 주문 수와 평균 매출을 구하세요.
어떤 요일에 매출이 가장 높은지 확인합니다.

??? tip "힌트"
    - SQLite: `strftime('%w', ordered_at)` → 0(일)~6(토)
    - CASE문으로 요일명 변환
    - 먼저 일별 매출을 구한 뒤, 요일별로 평균

??? success "정답"
    ```sql
    WITH daily_stats AS (
        SELECT
            DATE(ordered_at) AS order_date,
            CAST(strftime('%w', ordered_at) AS INTEGER) AS dow,
            COUNT(*)               AS order_count,
            SUM(total_amount)      AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY DATE(ordered_at)
    )
    SELECT
        CASE dow
            WHEN 0 THEN '일요일'
            WHEN 1 THEN '월요일'
            WHEN 2 THEN '화요일'
            WHEN 3 THEN '수요일'
            WHEN 4 THEN '목요일'
            WHEN 5 THEN '금요일'
            WHEN 6 THEN '토요일'
        END AS day_of_week,
        ROUND(AVG(order_count)) AS avg_daily_orders,
        ROUND(AVG(revenue))     AS avg_daily_revenue
    FROM daily_stats
    GROUP BY dow
    ORDER BY dow;
    ```

    | day_of_week | avg_daily_orders | avg_daily_revenue |
    |---|---|---|
    | 일요일 | 12 | 7500000 |
    | 월요일 | 15 | 9200000 |
    | ... | ... | ... |

---

### 문제 5. 분기별 매출과 전분기 대비 성장률

2022~2024년 분기별 매출과 전분기 대비 성장률(%)을 구하세요.

??? tip "힌트"
    - 분기: `(CAST(SUBSTR(ordered_at,6,2) AS INTEGER) + 2) / 3`
    - `LAG(revenue, 1)` 윈도우 함수로 전분기 매출 참조
    - 성장률 = (당분기 - 전분기) / 전분기 * 100

??? success "정답"
    ```sql
    WITH quarterly AS (
        SELECT
            SUBSTR(ordered_at, 1, 4) AS year,
            'Q' || ((CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3) AS quarter,
            SUBSTR(ordered_at, 1, 4) || '-Q' || ((CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3) AS yq,
            ROUND(SUM(total_amount)) AS revenue,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2022-01-01' AND ordered_at < '2025-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 4),
                 (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) + 2) / 3
    )
    SELECT
        yq,
        revenue,
        order_count,
        LAG(revenue, 1) OVER (ORDER BY yq) AS prev_quarter_revenue,
        ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY yq))
            / LAG(revenue, 1) OVER (ORDER BY yq), 1) AS qoq_growth_pct
    FROM quarterly
    ORDER BY yq;
    ```

    | yq | revenue | order_count | prev_quarter_revenue | qoq_growth_pct |
    |---|---|---|---|---|
    | 2022-Q1 | 580000000 | 920 | NULL | NULL |
    | 2022-Q2 | 550000000 | 870 | 580000000 | -5.2 |
    | 2022-Q3 | 490000000 | 780 | 550000000 | -10.9 |
    | 2022-Q4 | 680000000 | 1050 | 490000000 | 38.8 |
    | ... | ... | ... | ... | ... |

---

### 문제 6. 결제 수단별 매출 비중 추이

2024년 월별로 각 결제 수단(card, bank_transfer, kakao_pay 등)의 매출 비중(%)을 구하세요.

??? tip "힌트"
    - `payments.method`로 결제 수단 구분
    - 윈도우 함수 `SUM(revenue) OVER (PARTITION BY year_month)`으로 월 전체 매출
    - 비중 = 결제 수단별 매출 / 월 전체 매출 * 100

??? success "정답"
    ```sql
    WITH monthly_method AS (
        SELECT
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            pm.method,
            ROUND(SUM(pm.amount)) AS revenue
        FROM payments AS pm
        INNER JOIN orders AS o ON pm.order_id = o.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
          AND pm.status = 'paid'
        GROUP BY SUBSTR(o.ordered_at, 1, 7), pm.method
    )
    SELECT
        year_month,
        method,
        revenue,
        ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY year_month), 1) AS method_pct
    FROM monthly_method
    ORDER BY year_month, revenue DESC;
    ```

    | year_month | method | revenue | method_pct |
    |---|---|---|---|
    | 2024-01 | card | 650000000 | 62.5 |
    | 2024-01 | kakao_pay | 180000000 | 17.3 |
    | 2024-01 | bank_transfer | 120000000 | 11.5 |
    | ... | ... | ... | ... |

---

### 문제 7. 카테고리별 상위 3개 상품 (Top-N per Group)

2024년 각 대분류 카테고리에서 매출 상위 3개 상품을 선발하세요.

??? tip "힌트"
    - CTE에서 카테고리별 상품 매출 집계
    - `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)` 순위
    - 외부 쿼리에서 `WHERE rn <= 3` 필터

??? success "정답"
    ```sql
    WITH product_sales AS (
        SELECT
            COALESCE(top_cat.name, mid_cat.name, cat.name) AS top_category,
            p.name AS product_name,
            SUM(oi.quantity)                        AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        LEFT JOIN categories AS mid_cat ON cat.parent_id = mid_cat.id
        LEFT JOIN categories AS top_cat ON mid_cat.parent_id = top_cat.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY COALESCE(top_cat.name, mid_cat.name, cat.name), p.name
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY top_category ORDER BY revenue DESC) AS rn
        FROM product_sales
    )
    SELECT top_category, rn AS rank, product_name, units_sold, revenue
    FROM ranked
    WHERE rn <= 3
    ORDER BY top_category, rn;
    ```

    | top_category | rank | product_name | units_sold | revenue |
    |---|---|---|---|---|
    | 컴퓨터 | 1 | (노트북 A) | 120 | 360000000 |
    | 컴퓨터 | 2 | (데스크톱 B) | 85 | 255000000 |
    | 컴퓨터 | 3 | (노트북 C) | 78 | 234000000 |
    | 주변기기 | 1 | ... | ... | ... |

---

### 문제 8. 전년 동월 대비(YoY) 매출 성장률

2023~2024년 각 월의 매출과 전년 동월 대비 성장률(%)을 구하세요.

??? tip "힌트"
    - `LAG(revenue, 12)` — 12개월 전 매출 참조
    - 또는 CTE에서 연도+월 분리 후, 같은 월의 전년도를 SELF JOIN

??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 4) AS year,
            SUBSTR(ordered_at, 6, 2) AS month,
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount)) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2022-01-01' AND ordered_at < '2025-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        cur.year_month,
        cur.revenue                AS current_revenue,
        prev.revenue               AS prev_year_revenue,
        ROUND(100.0 * (cur.revenue - prev.revenue) / prev.revenue, 1) AS yoy_growth_pct
    FROM monthly AS cur
    INNER JOIN monthly AS prev
        ON cur.month = prev.month
        AND CAST(cur.year AS INTEGER) = CAST(prev.year AS INTEGER) + 1
    WHERE cur.year IN ('2023', '2024')
    ORDER BY cur.year_month;
    ```

    | year_month | current_revenue | prev_year_revenue | yoy_growth_pct |
    |---|---|---|---|
    | 2023-01 | 210000000 | 198000000 | 6.1 |
    | 2023-02 | 195000000 | 175000000 | 11.4 |
    | ... | ... | ... | ... |
    | 2024-01 | 235000000 | 210000000 | 11.9 |
    | ... | ... | ... | ... |

---

### 문제 9. 이동 평균(Moving Average) — 3개월 이동 평균 매출

월별 매출의 3개월 이동 평균을 구하세요.
이동 평균은 추세를 파악할 때 계절적 변동을 완화해줍니다.

??? tip "힌트"
    - `AVG(revenue) OVER (ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`
    - 처음 2개월은 데이터가 부족하므로 이동 평균이 정확하지 않을 수 있음

??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount)) AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
          AND ordered_at >= '2023-01-01' AND ordered_at < '2025-01-01'
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        )) AS moving_avg_3m,
        ROUND(AVG(revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        )) AS moving_avg_6m
    FROM monthly
    ORDER BY year_month;
    ```

    | year_month | revenue | moving_avg_3m | moving_avg_6m |
    |---|---|---|---|
    | 2023-01 | 210000000 | 210000000 | 210000000 |
    | 2023-02 | 195000000 | 202500000 | 202500000 |
    | 2023-03 | 220000000 | 208333333 | 208333333 |
    | 2023-04 | 205000000 | 206666667 | 207500000 |
    | ... | ... | ... | ... |

---

### 문제 10. ABC 분석 — 상품별 매출 누적 비율

2024년 상품별 매출을 내림차순으로 정렬하고, 누적 매출 비율로 A/B/C 등급을 부여하세요.
(A: 상위 70%, B: 70~90%, C: 나머지)

??? tip "힌트"
    - 누적 비율: `SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER ()`
    - CASE문으로 A/B/C 등급 분류
    - 파레토 법칙(80:20)의 변형

??? success "정답"
    ```sql
    WITH product_revenue AS (
        SELECT
            p.id,
            p.name AS product_name,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS revenue
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name
    ),
    cumulative AS (
        SELECT
            product_name,
            revenue,
            SUM(revenue) OVER (ORDER BY revenue DESC) AS cum_revenue,
            SUM(revenue) OVER () AS total_revenue
        FROM product_revenue
    )
    SELECT
        product_name,
        revenue,
        ROUND(100.0 * cum_revenue / total_revenue, 1) AS cum_pct,
        CASE
            WHEN 100.0 * cum_revenue / total_revenue <= 70 THEN 'A'
            WHEN 100.0 * cum_revenue / total_revenue <= 90 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM cumulative
    ORDER BY revenue DESC
    LIMIT 30;
    ```

    | product_name | revenue | cum_pct | abc_class |
    |---|---|---|---|
    | (고가 노트북) | 360000000 | 3.2 | A |
    | (인기 데스크톱) | 280000000 | 5.7 | A |
    | ... | ... | ... | ... |
    | (보급형 마우스) | 5000000 | 91.2 | C |

---

### 문제 11. 신규 고객 vs 재구매 고객 매출 비교

2024년 월별로 신규 고객(해당 월에 첫 주문)과 재구매 고객의 주문 수, 매출을 분리하세요.

??? tip "힌트"
    - 각 고객의 첫 주문 월: `MIN(ordered_at)` 으로 구함
    - 주문 월 = 첫 주문 월이면 "신규", 아니면 "재구매"
    - CTE로 단계적으로 처리

??? success "정답"
    ```sql
    WITH first_order AS (
        SELECT
            customer_id,
            SUBSTR(MIN(ordered_at), 1, 7) AS first_month
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    classified AS (
        SELECT
            SUBSTR(o.ordered_at, 1, 7) AS year_month,
            CASE
                WHEN SUBSTR(o.ordered_at, 1, 7) = fo.first_month THEN '신규'
                ELSE '재구매'
            END AS customer_type,
            o.total_amount
        FROM orders AS o
        INNER JOIN first_order AS fo ON o.customer_id = fo.customer_id
        WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        year_month,
        customer_type,
        COUNT(*)                  AS order_count,
        ROUND(SUM(total_amount)) AS revenue
    FROM classified
    GROUP BY year_month, customer_type
    ORDER BY year_month, customer_type;
    ```

    | year_month | customer_type | order_count | revenue |
    |---|---|---|---|
    | 2024-01 | 신규 | 85 | 42000000 |
    | 2024-01 | 재구매 | 350 | 193000000 |
    | 2024-02 | 신규 | 72 | 38000000 |
    | 2024-02 | 재구매 | 320 | 180000000 |
    | ... | ... | ... | ... |

---

### 문제 12. 고객 등급별 평균 객단가 추이

2024년 월별로 고객 등급(BRONZE/SILVER/GOLD/VIP)별 평균 주문 금액을 구하세요.

??? tip "힌트"
    - `customers.grade`로 등급 구분
    - `AVG(total_amount)` 그룹별 집계
    - 월 + 등급 두 차원으로 GROUP BY

??? success "정답"
    ```sql
    SELECT
        SUBSTR(o.ordered_at, 1, 7) AS year_month,
        c.grade,
        COUNT(*)                   AS order_count,
        ROUND(AVG(o.total_amount)) AS avg_order_value
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(o.ordered_at, 1, 7), c.grade
    ORDER BY year_month, 
        CASE c.grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
        END;
    ```

    | year_month | grade | order_count | avg_order_value |
    |---|---|---|---|
    | 2024-01 | VIP | 45 | 1200000 |
    | 2024-01 | GOLD | 85 | 850000 |
    | 2024-01 | SILVER | 120 | 620000 |
    | 2024-01 | BRONZE | 185 | 380000 |
    | ... | ... | ... | ... |

---

### 문제 13. 배송사별 배송 소요일 분석

2024년 배송사(carrier)별 평균 배송 소요일, 최소/최대 소요일, 배송 건수를 구하세요.
배송 완료(delivered)된 건만 대상으로 합니다.

??? tip "힌트"
    - 배송 소요일: `JULIANDAY(delivered_at) - JULIANDAY(shipped_at)`
    - `shipping` 테이블의 `status = 'delivered'`
    - `shipped_at`과 `delivered_at`이 모두 NOT NULL인 건만

??? success "정답"
    ```sql
    SELECT
        s.carrier,
        COUNT(*)                                                        AS delivery_count,
        ROUND(AVG(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at)), 1) AS avg_days,
        MIN(ROUND(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at), 1)) AS min_days,
        MAX(ROUND(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at), 1)) AS max_days,
        ROUND(100.0 * SUM(CASE
            WHEN JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at) <= 2 THEN 1
            ELSE 0
        END) / COUNT(*), 1) AS within_2days_pct
    FROM shipping AS s
    INNER JOIN orders AS o ON s.order_id = o.id
    WHERE s.status = 'delivered'
      AND s.shipped_at IS NOT NULL
      AND s.delivered_at IS NOT NULL
      AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
    GROUP BY s.carrier
    ORDER BY avg_days;
    ```

    | carrier | delivery_count | avg_days | min_days | max_days | within_2days_pct |
    |---|---|---|---|---|---|
    | CJ대한통운 | 3200 | 1.8 | 0.5 | 5.2 | 68.5 |
    | 한진택배 | 2800 | 2.1 | 0.5 | 6.0 | 55.2 |
    | ... | ... | ... | ... | ... | ... |

---

### 문제 14. 할인율 구간별 매출 영향

2024년 주문의 할인율(discount_amount / (total_amount + discount_amount))을 구간별로 나누고,
각 구간의 주문 수, 평균 주문 금액, 총 매출을 분석하세요.

??? tip "힌트"
    - 할인율 = `discount_amount / (total_amount + discount_amount) * 100`
    - CASE문으로 0%, 1~5%, 6~10%, 11~20%, 20%+ 구간 분류
    - `discount_amount = 0`이면 할인 없음

??? success "정답"
    ```sql
    WITH order_discount AS (
        SELECT
            id,
            total_amount,
            discount_amount,
            CASE
                WHEN discount_amount = 0 THEN 0
                ELSE ROUND(100.0 * discount_amount / (total_amount + discount_amount), 1)
            END AS discount_pct
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        CASE
            WHEN discount_pct = 0    THEN '할인 없음'
            WHEN discount_pct <= 5   THEN '1~5%'
            WHEN discount_pct <= 10  THEN '6~10%'
            WHEN discount_pct <= 20  THEN '11~20%'
            ELSE '20% 초과'
        END AS discount_range,
        COUNT(*)                    AS order_count,
        ROUND(AVG(total_amount))    AS avg_order_value,
        ROUND(SUM(total_amount))    AS total_revenue
    FROM order_discount
    GROUP BY CASE
        WHEN discount_pct = 0    THEN '할인 없음'
        WHEN discount_pct <= 5   THEN '1~5%'
        WHEN discount_pct <= 10  THEN '6~10%'
        WHEN discount_pct <= 20  THEN '11~20%'
        ELSE '20% 초과'
    END
    ORDER BY
        CASE
            WHEN discount_pct = 0    THEN 1
            WHEN discount_pct <= 5   THEN 2
            WHEN discount_pct <= 10  THEN 3
            WHEN discount_pct <= 20  THEN 4
            ELSE 5
        END;
    ```

    | discount_range | order_count | avg_order_value | total_revenue |
    |---|---|---|---|
    | 할인 없음 | 8500 | 580000 | 4930000000 |
    | 1~5% | 2100 | 620000 | 1302000000 |
    | 6~10% | 1500 | 750000 | 1125000000 |
    | 11~20% | 800 | 900000 | 720000000 |
    | 20% 초과 | 200 | 1100000 | 220000000 |

---

### 문제 15. 프로모션 ROI 분석

각 프로모션의 투입 할인 금액 대비 매출 효과(ROI)를 분석하세요.
프로모션 기간 중 프로모션 대상 상품의 매출과 할인 금액을 집계합니다.

??? tip "힌트"
    - `promotions` + `promotion_products`로 대상 상품 파악
    - 프로모션 기간: `started_at` ~ `ended_at`
    - `order_items`에서 해당 기간 + 해당 상품의 매출 집계
    - ROI = (매출 - 할인 총액) / 할인 총액 * 100

??? success "정답"
    ```sql
    WITH promo_sales AS (
        SELECT
            pr.id           AS promo_id,
            pr.name         AS promo_name,
            pr.type         AS promo_type,
            pr.discount_type,
            pr.discount_value,
            COUNT(DISTINCT o.id) AS order_count,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS gross_revenue,
            ROUND(SUM(oi.discount_amount))          AS total_discount
        FROM promotions AS pr
        INNER JOIN promotion_products AS pp ON pr.id = pp.promotion_id
        INNER JOIN order_items AS oi ON pp.product_id = oi.product_id
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at >= pr.started_at
          AND o.ordered_at <= pr.ended_at
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY pr.id, pr.name, pr.type, pr.discount_type, pr.discount_value
    )
    SELECT
        promo_name,
        promo_type,
        discount_type || ' ' || discount_value AS discount_info,
        order_count,
        gross_revenue,
        total_discount,
        gross_revenue - total_discount AS net_revenue,
        CASE
            WHEN total_discount > 0
            THEN ROUND(100.0 * (gross_revenue - total_discount) / total_discount, 1)
            ELSE NULL
        END AS roi_pct
    FROM promo_sales
    ORDER BY roi_pct DESC;
    ```

    | promo_name | promo_type | discount_info | order_count | gross_revenue | total_discount | net_revenue | roi_pct |
    |---|---|---|---|---|---|---|---|
    | 여름 할인전 | seasonal | percent 15 | 450 | 320000000 | 48000000 | 272000000 | 566.7 |
    | 연말 특가 | flash | fixed 50000 | 280 | 250000000 | 14000000 | 236000000 | 1685.7 |
    | ... | ... | ... | ... | ... | ... | ... | ... |

---

### 문제 16. 장바구니 → 구매 전환율

장바구니에 담긴 상품 중 실제 구매로 전환된 비율을 카테고리별로 구하세요.

??? tip "힌트"
    - `cart_items`에 담긴 상품 수 vs 같은 고객이 실제 주문한 같은 상품 수
    - `carts` + `cart_items` + `order_items` + `orders` JOIN
    - 전환율 = 구매된 장바구니 항목 수 / 전체 장바구니 항목 수 * 100

??? success "정답"
    ```sql
    WITH cart_products AS (
        SELECT
            c.customer_id,
            ci.product_id,
            cat.name AS category
        FROM carts AS c
        INNER JOIN cart_items AS ci ON c.id = ci.cart_id
        INNER JOIN products AS p ON ci.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
    ),
    purchased AS (
        SELECT DISTINCT
            o.customer_id,
            oi.product_id
        FROM orders AS o
        INNER JOIN order_items AS oi ON o.id = oi.order_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    SELECT
        cp.category,
        COUNT(*) AS cart_items_total,
        SUM(CASE WHEN pur.product_id IS NOT NULL THEN 1 ELSE 0 END) AS converted,
        ROUND(100.0 * SUM(CASE WHEN pur.product_id IS NOT NULL THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS conversion_rate_pct
    FROM cart_products AS cp
    LEFT JOIN purchased AS pur
        ON cp.customer_id = pur.customer_id
        AND cp.product_id = pur.product_id
    GROUP BY cp.category
    ORDER BY conversion_rate_pct DESC;
    ```

    | category | cart_items_total | converted | conversion_rate_pct |
    |---|---|---|---|
    | (인기 카테고리) | 1200 | 840 | 70.0 |
    | (일반 카테고리) | 800 | 320 | 40.0 |
    | ... | ... | ... | ... |

---

### 문제 17. 동시 구매 패턴(장바구니 분석)

같은 주문에서 함께 구매된 상품 쌍(pair)을 찾으세요.
동시 구매 빈도가 5회 이상인 상품 쌍만 표시합니다.

??? tip "힌트"
    - `order_items`를 자기 조인(Self JOIN)하여 같은 주문의 서로 다른 상품 쌍 생성
    - 중복 제거: `oi1.product_id < oi2.product_id`
    - `GROUP BY` 상품 쌍으로 동시 구매 횟수 집계

??? success "정답"
    ```sql
    SELECT
        p1.name AS product_a,
        p2.name AS product_b,
        COUNT(*) AS co_purchase_count
    FROM order_items AS oi1
    INNER JOIN order_items AS oi2
        ON oi1.order_id = oi2.order_id
        AND oi1.product_id < oi2.product_id
    INNER JOIN products AS p1 ON oi1.product_id = p1.id
    INNER JOIN products AS p2 ON oi2.product_id = p2.id
    INNER JOIN orders AS o ON oi1.order_id = o.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY oi1.product_id, oi2.product_id, p1.name, p2.name
    HAVING COUNT(*) >= 5
    ORDER BY co_purchase_count DESC
    LIMIT 20;
    ```

    | product_a | product_b | co_purchase_count |
    |---|---|---|
    | (키보드 A) | (마우스 B) | 25 |
    | (SSD C) | (메모리 D) | 18 |
    | ... | ... | ... |

---

### 문제 18. 리뷰 평점과 매출 상관관계

상품별 평균 리뷰 평점과 매출의 관계를 분석하세요.
평점 구간(1~2, 2~3, 3~4, 4~5)별 평균 매출을 구합니다.

??? tip "힌트"
    - 상품별 평균 평점과 매출을 먼저 구한 뒤
    - CASE문으로 평점 구간 분류
    - 리뷰가 없는 상품은 제외

??? success "정답"
    ```sql
    WITH product_metrics AS (
        SELECT
            p.id,
            p.name,
            AVG(r.rating)                          AS avg_rating,
            COUNT(DISTINCT r.id)                    AS review_count,
            ROUND(SUM(oi.quantity * oi.unit_price)) AS revenue
        FROM products AS p
        INNER JOIN reviews AS r ON p.id = r.product_id
        INNER JOIN order_items AS oi ON p.id = oi.product_id
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name
        HAVING COUNT(DISTINCT r.id) >= 3
    )
    SELECT
        CASE
            WHEN avg_rating < 2 THEN '1.0~1.9'
            WHEN avg_rating < 3 THEN '2.0~2.9'
            WHEN avg_rating < 4 THEN '3.0~3.9'
            ELSE '4.0~5.0'
        END AS rating_range,
        COUNT(*)                    AS product_count,
        ROUND(AVG(revenue))         AS avg_revenue,
        ROUND(AVG(review_count))    AS avg_reviews,
        ROUND(AVG(avg_rating), 2)   AS avg_rating_in_range
    FROM product_metrics
    GROUP BY CASE
        WHEN avg_rating < 2 THEN '1.0~1.9'
        WHEN avg_rating < 3 THEN '2.0~2.9'
        WHEN avg_rating < 4 THEN '3.0~3.9'
        ELSE '4.0~5.0'
    END
    ORDER BY rating_range;
    ```

    | rating_range | product_count | avg_revenue | avg_reviews | avg_rating_in_range |
    |---|---|---|---|---|
    | 1.0~1.9 | 5 | 12000000 | 8 | 1.65 |
    | 2.0~2.9 | 15 | 28000000 | 12 | 2.55 |
    | 3.0~3.9 | 80 | 45000000 | 18 | 3.52 |
    | 4.0~5.0 | 120 | 62000000 | 25 | 4.35 |

---

### 문제 19. 포인트 사용 효과 분석

포인트를 사용한 주문과 사용하지 않은 주문의 평균 주문 금액, 재구매율을 비교하세요.
(2024년 기준)

??? tip "힌트"
    - `orders.point_used > 0`이면 포인트 사용 주문
    - 재구매율: 해당 그룹 고객 중 2회 이상 주문한 비율
    - CTE로 고객별 주문 특성을 먼저 집계

??? success "정답"
    ```sql
    WITH order_classified AS (
        SELECT
            customer_id,
            total_amount,
            CASE WHEN point_used > 0 THEN '포인트 사용' ELSE '미사용' END AS point_type
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    customer_stats AS (
        SELECT
            point_type,
            customer_id,
            COUNT(*) AS order_count,
            AVG(total_amount) AS avg_amount
        FROM order_classified
        GROUP BY point_type, customer_id
    )
    SELECT
        point_type,
        COUNT(DISTINCT customer_id)    AS customer_count,
        ROUND(AVG(avg_amount))         AS avg_order_value,
        ROUND(100.0 * SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END)
            / COUNT(*), 1)            AS repeat_rate_pct
    FROM customer_stats
    GROUP BY point_type;
    ```

    | point_type | customer_count | avg_order_value | repeat_rate_pct |
    |---|---|---|---|
    | 포인트 사용 | 2800 | 720000 | 65.3 |
    | 미사용 | 3500 | 550000 | 42.1 |

---

### 문제 20. 종합 경영 대시보드

CEO를 위한 2024년 종합 경영 대시보드를 하나의 쿼리로 생성하세요.
총 매출, 주문 수, 고객 수, 평균 객단가, 반품률, 평균 배송일, 평균 리뷰 평점을 포함합니다.

??? tip "힌트"
    - 각 지표를 서브쿼리 또는 CTE로 개별 계산한 뒤 결합
    - `CROSS JOIN` 또는 스칼라 서브쿼리로 단일 행 결합
    - 반품률 = 반품 주문 수 / 전체 주문 수

??? success "정답"
    ```sql
    WITH sales AS (
        SELECT
            COUNT(*)                            AS total_orders,
            COUNT(DISTINCT customer_id)         AS unique_customers,
            ROUND(SUM(total_amount))            AS total_revenue,
            ROUND(AVG(total_amount))            AS avg_order_value
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    returns_stat AS (
        SELECT
            ROUND(100.0 * COUNT(*) / (
                SELECT COUNT(*) FROM orders
                WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
            ), 1) AS return_rate_pct
        FROM orders
        WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'
          AND status IN ('returned', 'return_requested')
    ),
    shipping_stat AS (
        SELECT
            ROUND(AVG(JULIANDAY(s.delivered_at) - JULIANDAY(s.shipped_at)), 1) AS avg_delivery_days
        FROM shipping AS s
        INNER JOIN orders AS o ON s.order_id = o.id
        WHERE s.status = 'delivered'
          AND s.shipped_at IS NOT NULL
          AND s.delivered_at IS NOT NULL
          AND o.ordered_at >= '2024-01-01' AND o.ordered_at < '2025-01-01'
    ),
    review_stat AS (
        SELECT
            ROUND(AVG(rating), 2) AS avg_rating,
            COUNT(*) AS review_count
        FROM reviews
        WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
    )
    SELECT
        s.total_revenue,
        s.total_orders,
        s.unique_customers,
        s.avg_order_value,
        r.return_rate_pct,
        sh.avg_delivery_days,
        rv.avg_rating,
        rv.review_count
    FROM sales AS s
    CROSS JOIN returns_stat AS r
    CROSS JOIN shipping_stat AS sh
    CROSS JOIN review_stat AS rv;
    ```

    | total_revenue | total_orders | unique_customers | avg_order_value | return_rate_pct | avg_delivery_days | avg_rating | review_count |
    |---|---|---|---|---|---|---|---|
    | 12500000000 | 18500 | 5200 | 675676 | 8.5 | 2.1 | 4.12 | 4800 |
