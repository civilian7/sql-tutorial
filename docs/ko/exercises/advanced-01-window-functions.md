# 윈도우 함수 실전

!!! info "사용 테이블"
    `orders` — 주문 (상태, 금액, 일시)  
    `order_items` — 주문 상세 (수량, 단가)  
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `customers` — 고객 (등급, 포인트, 가입채널)  
    `reviews` — 리뷰 (평점, 내용)  
    `payments` — 결제 (방법, 금액, 상태)  
    `categories` — 카테고리 (부모-자식 계층)  

!!! abstract "학습 범위"
    `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `LAG`, `LEAD`, `SUM/AVG/COUNT OVER`, `FIRST_VALUE`, `LAST_VALUE`, `ROWS BETWEEN`

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
    | ----------: | ---------- | ---------- | ---------- | ----------: | ----------: |
    | 2 | 김경수 | ORD-20160807-04161 | 2016-08-18 09:29:34 | 139200.0 | 1 |
    | 2 | 김경수 | ORD-20160829-04654 | 2016-08-29 19:59:53 | 323700.0 | 2 |
    | 2 | 김경수 | ORD-20160906-04838 | 2016-09-06 20:05:02 | 149200.0 | 3 |
    | 2 | 김경수 | ORD-20160910-04917 | 2016-09-10 14:59:59 | 2501100.0 | 4 |
    | 2 | 김경수 | ORD-20161001-05339 | 2016-10-01 19:40:13 | 166100.0 | 5 |
    | 2 | 김경수 | ORD-20161004-05388 | 2016-10-04 12:18:11 | 520500.0 | 6 |
    | 2 | 김경수 | ORD-20161012-05536 | 2016-10-12 22:54:00 | 1950710.0 | 7 |
    | 2 | 김경수 | ORD-20161101-05925 | 2016-11-01 04:47:42 | 898700.0 | 8 |
    | ... | ... | ... | ... | ... | ... |

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
    | ---------- | ----------: | ----------: | ----------: |
    | 2024-01 | 3737010508.0 | 12 | 12 |
    | 2024-02 | 4630208028.0 | 9 | 9 |
    | 2024-03 | 4811012761.0 | 6 | 6 |
    | 2024-04 | 4852046384.0 | 5 | 5 |
    | 2024-05 | 4796192371.0 | 7 | 7 |
    | 2024-06 | 3787186898.0 | 11 | 11 |
    | 2024-07 | 4370145415.0 | 10 | 10 |
    | 2024-08 | 4778870727.0 | 8 | 8 |
    | ... | ... | ... | ... |

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
    | ---------- | ---------- | ----------: | ----------: | ----------: |
    | ASUS Dual RTX 4060 Ti 실버 | NVIDIA | 364990000.0 | 6049128000.0 | 6.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 블랙 | NVIDIA | 306205800.0 | 6049128000.0 | 5.1 |
    | ASUS ROG STRIX RTX 4090 화이트 | NVIDIA | 294856000.0 | 6049128000.0 | 4.9 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | NVIDIA | 268482500.0 | 6049128000.0 | 4.4 |
    | 기가바이트 RTX 4060 EAGLE OC 실버 | NVIDIA | 253128000.0 | 6049128000.0 | 4.2 |
    | ASUS Dual RTX 4060 Ti | NVIDIA | 244458400.0 | 6049128000.0 | 4.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | NVIDIA | 240453200.0 | 6049128000.0 | 4.0 |
    | AMD Ryzen 7 7700X 블랙 | AMD | 237618000.0 | 1078208100.0 | 22.0 |
    | ... | ... | ... | ... | ... |

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
    | ----------: | ---------- | ---------- | ----------: | ----------: |
    | 2 | 김경수 | 2016-08-18 09:29:34 | 139200.0 | 139200.0 |
    | 2 | 김경수 | 2016-08-29 19:59:53 | 323700.0 | 462900.0 |
    | 2 | 김경수 | 2016-09-06 20:05:02 | 149200.0 | 612100.0 |
    | 2 | 김경수 | 2016-09-10 14:59:59 | 2501100.0 | 3113200.0 |
    | 2 | 김경수 | 2016-10-01 19:40:13 | 166100.0 | 3279300.0 |
    | 2 | 김경수 | 2016-10-04 12:18:11 | 520500.0 | 3799800.0 |
    | 2 | 김경수 | 2016-10-12 22:54:00 | 1950710.0 | 5750510.0 |
    | 2 | 김경수 | 2016-11-01 04:47:42 | 898700.0 | 6649210.0 |
    | ... | ... | ... | ... | ... |

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
    | ---------- | ----------: | ----------: | ----------: |
    | card | 26633 | 27099300084.0 | 1 |
    | kakao_pay | 11705 | 11870784619.0 | 1 |
    | naver_pay | 8885 | 9015902948.0 | 2 |
    | bank_transfer | 5971 | 5967951548.0 | 2 |
    | point | 2928 | 2916576234.0 | 3 |
    | virtual_account | 2890 | 3058991818.0 | 4 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: | ---------- | ---------- | ---------- |
    | 2023-01 | 3194383488.0 | (NULL) | (NULL) | (NULL) |
    | 2023-02 | 3783544299.0 | 3194383488.0 | 589160811.0 | 18.4 |
    | 2023-03 | 4798857428.0 | 3783544299.0 | 1015313129.0 | 26.8 |
    | 2023-04 | 4683448161.0 | 4798857428.0 | -115409267.0 | -2.4 |
    | 2023-05 | 4023692043.0 | 4683448161.0 | -659756118.0 | -14.1 |
    | 2023-06 | 3443896173.0 | 4023692043.0 | -579795870.0 | -14.4 |
    | 2023-07 | 3189823743.0 | 3443896173.0 | -254072430.0 | -7.4 |
    | 2023-08 | 4236240498.0 | 3189823743.0 | 1046416755.0 | 32.8 |
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
    | ----------: | ---------- | ----------: | ----------: | ----------: | ----------: |
    | 45487 | 송유진 | 1 | 0.0 | 0.0 | 0.0 |
    | 49554 | 박서윤 | 2 | 1.5 | 1.0 | 2.0 |
    | 50742 | 이정남 | 4 | 3.5 | 2.0 | 6.0 |
    | 49904 | 류은주 | 4 | 5.3 | 0.0 | 18.0 |
    | 226 | 박정수 | 650 | 5.6 | 0.0 | 63.0 |
    | 356 | 정유진 | 536 | 6.6 | 0.0 | 72.0 |
    | 840 | 문영숙 | 538 | 6.8 | 0.0 | 130.0 |
    | 1000 | 이미정 | 515 | 6.8 | 0.0 | 131.0 |
    | ... | ... | ... | ... | ... | ... |

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
    | ---------- | ----------: | ----------: | ----------: |
    | 2023-01 | 3194383488.0 | 3194383488.0 | 1 |
    | 2023-02 | 3783544299.0 | 3488963894.0 | 2 |
    | 2023-03 | 4798857428.0 | 3925595072.0 | 3 |
    | 2023-04 | 4683448161.0 | 4421949963.0 | 3 |
    | 2023-05 | 4023692043.0 | 4501999211.0 | 3 |
    | 2023-06 | 3443896173.0 | 4050345459.0 | 3 |
    | 2023-07 | 3189823743.0 | 3552470653.0 | 3 |
    | 2023-08 | 4236240498.0 | 3623320138.0 | 3 |
    | ... | ... | ... | ... |

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
    | ---------- | ---------- | ----------: | ---------- | ----------: |
    | 2in1 | 레노버 IdeaPad Flex 5 화이트 | 2914000.0 | HP Pavilion x360 14 | 720800.0 |
    | AMD | AMD Ryzen 7 7700X 블랙 | 1105200.0 | AMD Ryzen 7 9800X3D 실버 [특별 한정판 에디션] RGB 라이팅 탑재, 소프트웨어 커스터마이징 지원 | 182100.0 |
    | AMD | SAPPHIRE PULSE RX 7800 XT 블랙 | 2158800.0 | ASUS ROG STRIX RX 7900 XTX 블랙 | 374500.0 |
    | AMD 소켓 | ASUS ROG STRIX B850-F GAMING 실버 | 924400.0 | MSI MAG X870E TOMAHAWK WIFI | 125900.0 |
    | DDR4 | 삼성 DDR4 8GB PC4-25600 실버 | 136800.0 | SK하이닉스 DDR4 32GB PC4-25600 | 25700.0 |
    | DDR5 | G.SKILL Ripjaws S5 DDR5 32GB 6400MHz 블랙 | 441700.0 | Kingston FURY Beast DDR5 64GB 6000MHz 화이트 | 50800.0 |
    | HDD | Seagate BarraCuda 2TB 화이트 | 611900.0 | WD Gold 12TB 블랙 | 43400.0 |
    | Intel 소켓 | 기가바이트 B760M AORUS ELITE | 975800.0 | ASRock B860M Pro RS 화이트 | 107000.0 |
    | ... | ... | ... | ... | ... |

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
    | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: |
    | 1 | 535 | 2.0 | 3.71 | 3.52 | 26.0 |
    | 2 | 535 | 3.71 | 3.85 | 3.79 | 40.9 |
    | 3 | 535 | 3.85 | 3.97 | 3.91 | 46.0 |
    | 4 | 535 | 3.97 | 4.09 | 4.03 | 39.6 |
    | 5 | 534 | 4.09 | 5.0 | 4.27 | 25.5 |
    | ... | ... | ... | ... | ... | ... |

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
    | ---------- | ---------- | ----------: | ----------: | ----------: |
    | ASUS Dual RTX 4060 Ti 실버 | 2024-01 | 21470000.0 | 30415833.0 | 70.6 |
    | ASUS Dual RTX 4060 Ti 실버 | 2024-02 | 30058000.0 | 30415833.0 | 98.8 |
    | ASUS Dual RTX 4060 Ti 실버 | 2024-03 | 21470000.0 | 30415833.0 | 70.6 |
    | ASUS Dual RTX 4060 Ti 실버 | 2024-04 | 21470000.0 | 30415833.0 | 70.6 |
    | ASUS Dual RTX 4060 Ti 실버 | 2024-05 | 51528000.0 | 30415833.0 | 169.4 |
    | ... | ... | ... | ... | ... |

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
    | ---------- | ---------- | ----------: | ----------: | ---------- | ---------- |
    | 2024-01 | card | 1637985623.0 | 43.8 | (NULL) | (NULL) |
    | 2024-01 | kakao_pay | 701582674.0 | 18.8 | (NULL) | (NULL) |
    | 2024-01 | naver_pay | 604077057.0 | 16.1 | (NULL) | (NULL) |
    | 2024-01 | bank_transfer | 397750334.0 | 10.6 | (NULL) | (NULL) |
    | 2024-01 | virtual_account | 209801928.0 | 5.6 | (NULL) | (NULL) |
    | 2024-01 | point | 189862292.0 | 5.1 | (NULL) | (NULL) |
    | 2024-02 | card | 2157466285.0 | 46.6 | 43.8 | 2.8 |
    | 2024-02 | kakao_pay | 794741444.0 | 17.2 | 18.8 | -1.6 |
    | ... | ... | ... | ... | ... | ... |

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
    | ----------: | ---------- | ---------- | ----------: | ----------: | ----------: |
    | 3059 | 윤유진 | ORD-20230408-248697 | 1249400.0 | 71906300.0 | 70656900.0 |
    | 32129 | 김영호 | ORD-20240218-293235 | 6525100.0 | 68948100.0 | 62423000.0 |
    | 15801 | 한예은 | ORD-20230626-259827 | 885200.0 | 61811500.0 | 60926300.0 |
    | 40387 | 이성진 | ORD-20240822-323378 | 5015500.0 | 64332900.0 | 59317400.0 |
    | 942 | 박광수 | ORD-20180516-26809 | 5420400.0 | 63466900.0 | 58046500.0 |
    | 35583 | 고광수 | ORD-20231002-272459 | 2882500.0 | 58539900.0 | 55657400.0 |
    | 6840 | 최경자 | ORD-20200429-82365 | 6392700.0 | 61889000.0 | 55496300.0 |
    | 5657 | 김서영 | ORD-20220731-207855 | 3879200.0 | 57495600.0 | 53616400.0 |
    | ... | ... | ... | ... | ... | ... |

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
    | ----------: | ----------: | ----------: | ----------: | ---------- | ---------- |
    | 2020 | 1 | 10247095614.0 | 9867 | (NULL) | (NULL) |
    | 2020 | 2 | 10474089855.0 | 10049 | (NULL) | (NULL) |
    | 2020 | 3 | 10995490467.0 | 10796 | (NULL) | (NULL) |
    | 2020 | 4 | 12630611449.0 | 12395 | (NULL) | (NULL) |
    | 2021 | 1 | 13795824579.0 | 13513 | 10247095614.0 | 34.6 |
    | 2021 | 2 | 11884721583.0 | 11729 | 10474089855.0 | 13.5 |
    | 2021 | 3 | 12933953963.0 | 12748 | 10995490467.0 | 17.6 |
    | 2021 | 4 | 18183527492.0 | 17641 | 12630611449.0 | 44.0 |
    | ... | ... | ... | ... | ... | ... |

    > 첫 해(2020년)는 전년 데이터가 없으므로 `prev_year_revenue`와 `yoy_growth_pct`가 NULL입니다.
