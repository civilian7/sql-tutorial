# CTE 활용

!!! info "사용 테이블"
    `categories` — 카테고리 (부모-자식 계층)  
    `staff` — 직원 (부서, 역할, 관리자)  
    `orders` — 주문 (상태, 금액, 일시)  
    `customers` — 고객 (등급, 포인트, 가입채널)  
    `order_items` — 주문 상세 (수량, 단가)  
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `calendar` — 날짜 차원 (요일, 공휴일)  

!!! abstract "학습 범위"
    `WITH`, 재귀 CTE(`WITH RECURSIVE`), 다중 CTE 체이닝, CTE + 집계/JOIN/윈도우 함수

## 기초 (1~5)

단일 CTE와 CTE + JOIN/집계를 연습합니다.

---

### 문제 1

**2024년 월별 매출을 CTE로 구하고, 전체 평균 매출 이상인 월만 조회하세요.**

??? tip "힌트"
    CTE에서 월별 매출을 집계한 뒤, 외부 쿼리에서 `WHERE revenue >= (SELECT AVG(revenue) FROM cte명)`으로
    필터링합니다. CTE는 여러 번 참조할 수 있습니다.

??? success "정답"
    ```sql
    WITH monthly_revenue AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            ROUND(SUM(total_amount), 0) AS revenue,
            COUNT(*) AS order_count
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        revenue,
        order_count,
        (SELECT ROUND(AVG(revenue), 0) FROM monthly_revenue) AS avg_revenue,
        CASE
            WHEN revenue >= (SELECT AVG(revenue) FROM monthly_revenue) THEN '평균 이상'
            ELSE '평균 미만'
        END AS status
    FROM monthly_revenue
    WHERE revenue >= (SELECT AVG(revenue) FROM monthly_revenue)
    ORDER BY revenue DESC;
    ```

    **결과 예시:**

    | year_month | revenue | order_count | avg_revenue | status |
    | ---------- | ----------: | ----------: | ----------: | ---------- |
    | 2024-12 | 7171062836.0 | 6919 | 4993798863.0 | 평균 이상 |
    | 2024-11 | 6557769842.0 | 6240 | 4993798863.0 | 평균 이상 |
    | 2024-09 | 5398216952.0 | 5124 | 4993798863.0 | 평균 이상 |
    | 2024-10 | 5035863629.0 | 5068 | 4993798863.0 | 평균 이상 |

---

### 문제 2

**고객별 총 구매 금액을 CTE로 구한 뒤, 등급별 상위 5명씩 추출하세요.**

CTE와 `ROW_NUMBER` 윈도우 함수를 조합합니다.

??? tip "힌트"
    첫 번째 CTE에서 고객별 총 구매 금액을 집계하고,
    두 번째 CTE에서 `ROW_NUMBER() OVER (PARTITION BY grade ORDER BY total_spent DESC)`를 적용합니다.

??? success "정답"
    ```sql
    WITH customer_totals AS (
        SELECT
            c.id,
            c.name,
            c.grade,
            ROUND(SUM(o.total_amount), 0) AS total_spent,
            COUNT(*) AS order_count
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
        rn AS rank_in_grade,
        name,
        order_count,
        total_spent
    FROM ranked
    WHERE rn <= 5
    ORDER BY
        CASE grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
        END,
        rn;
    ```

    **결과 예시 (일부):**

    | grade | rank_in_grade | name | order_count | total_spent |
    |---|---|---|---|---|
    | VIP | 1 | 김... | 35 | 12500000 |
    | VIP | 2 | 박... | 28 | 10800000 |
    | ... | ... | ... | ... | ... |
    | BRONZE | 5 | 한... | 3 | 450000 |

---

### 문제 3

**CTE를 이용해 상품별 매출과 리뷰 요약을 한 번에 조회하세요.**

2024년 매출 상위 10개 상품의 매출액, 판매량, 리뷰 수, 평균 평점을 표시합니다.

??? tip "힌트"
    매출 CTE와 리뷰 CTE를 별도로 만든 뒤, 외부 쿼리에서 `LEFT JOIN`으로 합칩니다.
    리뷰가 없는 상품도 포함되어야 합니다.

??? success "정답"
    ```sql
    WITH sales AS (
        SELECT
            oi.product_id,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
            SUM(oi.quantity) AS units_sold
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY oi.product_id
    ),
    review_summary AS (
        SELECT
            product_id,
            COUNT(*) AS review_count,
            ROUND(AVG(rating), 2) AS avg_rating
        FROM reviews
        GROUP BY product_id
    )
    SELECT
        p.name          AS product_name,
        cat.name        AS category,
        s.units_sold,
        s.total_revenue,
        COALESCE(r.review_count, 0) AS review_count,
        r.avg_rating
    FROM sales AS s
    INNER JOIN products   AS p   ON s.product_id  = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LEFT  JOIN review_summary AS r ON s.product_id = r.product_id
    ORDER BY s.total_revenue DESC
    LIMIT 10;
    ```

    **결과 예시 (상위 3행):**

    | product_name | category | units_sold | total_revenue | review_count | avg_rating |
    | ---------- | ---------- | ----------: | ----------: | ----------: | ----------: |
    | ASUS Dual RTX 4060 Ti 실버 | NVIDIA | 85 | 364990000.0 | 21 | 3.76 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 블랙 | NVIDIA | 73 | 306205800.0 | 11 | 2.82 |
    | ASUS ROG STRIX RTX 4090 화이트 | NVIDIA | 80 | 294856000.0 | 16 | 3.69 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | NVIDIA | 55 | 268482500.0 | 30 | 3.8 |
    | 기가바이트 RTX 4060 EAGLE OC 실버 | NVIDIA | 60 | 253128000.0 | 21 | 3.62 |
    | ASUS Dual RTX 4060 Ti | NVIDIA | 58 | 244458400.0 | 8 | 4.5 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | NVIDIA | 52 | 240453200.0 | 26 | 3.85 |
    | AMD Ryzen 7 7700X 블랙 | AMD | 215 | 237618000.0 | 77 | 3.88 |
    | ... | ... | ... | ... | ... | ... |

---

### 문제 4

**CTE에서 집계한 결과를 다른 CTE에서 필터링하는 체이닝을 연습하세요.**

월별 신규 가입자 수를 구하고, 전월 대비 증감률이 20% 이상인 "급증" 월을 찾으세요.

??? tip "힌트"
    CTE 1: 월별 신규 가입자 수 집계. CTE 2: `LAG`로 전월 수치를 가져와 증감률 계산.
    외부 쿼리에서 증감률 >= 20인 행만 필터링합니다.

??? success "정답"
    ```sql
    WITH monthly_signups AS (
        SELECT
            SUBSTR(created_at, 1, 7) AS year_month,
            COUNT(*) AS signup_count
        FROM customers
        WHERE created_at >= '2022-01-01'
        GROUP BY SUBSTR(created_at, 1, 7)
    ),
    with_growth AS (
        SELECT
            year_month,
            signup_count,
            LAG(signup_count, 1) OVER (ORDER BY year_month) AS prev_count,
            ROUND(100.0 * (signup_count - LAG(signup_count, 1) OVER (ORDER BY year_month))
                / LAG(signup_count, 1) OVER (ORDER BY year_month), 1) AS growth_pct
        FROM monthly_signups
    )
    SELECT
        year_month,
        signup_count,
        prev_count,
        growth_pct
    FROM with_growth
    WHERE growth_pct >= 20
    ORDER BY growth_pct DESC;
    ```

    **결과 예시:**

    | year_month | signup_count | prev_count | growth_pct |
    | ---------- | ----------: | ----------: | ----------: |
    | 2025-01 | 693 | 577 | 20.1 |

---

### 문제 5

**카테고리별 매출 비중을 CTE로 구하고, 누적 비중(파레토)을 계산하세요.**

2024년 기준 카테고리별 매출을 구하고, 비중 내림차순으로 누적 비중을 표시합니다.

??? tip "힌트"
    CTE에서 카테고리별 매출을 집계한 뒤,
    `SUM(share_pct) OVER (ORDER BY revenue DESC ROWS UNBOUNDED PRECEDING)`으로 누적 비중을 구합니다.

??? success "정답"
    ```sql
    WITH category_revenue AS (
        SELECT
            cat.name AS category,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM order_items AS oi
        INNER JOIN orders     AS o   ON oi.order_id   = o.id
        INNER JOIN products   AS p   ON oi.product_id = p.id
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY cat.name
    ),
    with_share AS (
        SELECT
            category,
            revenue,
            ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS share_pct
        FROM category_revenue
    )
    SELECT
        category,
        revenue,
        share_pct,
        ROUND(SUM(share_pct) OVER (
            ORDER BY revenue DESC
            ROWS UNBOUNDED PRECEDING
        ), 1) AS cumulative_pct
    FROM with_share
    ORDER BY revenue DESC;
    ```

    **결과 예시 (상위 5행):**

    | category | revenue | share_pct | cumulative_pct |
    | ---------- | ----------: | ----------: | ----------: |
    | 게이밍 노트북 | 7252261700.0 | 12.0 | 12.0 |
    | NVIDIA | 6049128000.0 | 10.0 | 22.0 |
    | AMD | 5055980700.0 | 8.4 | 30.4 |
    | 일반 노트북 | 4852629300.0 | 8.0 | 38.4 |
    | 게이밍 모니터 | 3575676600.0 | 5.9 | 44.3 |
    | 스피커/헤드셋 | 2473846600.0 | 4.1 | 48.4 |
    | Intel 소켓 | 2265205100.0 | 3.7 | 52.1 |
    | 2in1 | 2164737100.0 | 3.6 | 55.7 |
    | ... | ... | ... | ... |

---

## 응용 (6~10)

재귀 CTE와 다중 CTE를 활용합니다.

---

### 문제 6

**카테고리 계층 구조를 재귀 CTE로 전개하세요.**

최상위 카테고리(parent_id IS NULL)부터 하위 카테고리까지, 전체 경로를 표시합니다.

??? tip "힌트"
    `WITH RECURSIVE`를 사용합니다. 앵커 멤버: `WHERE parent_id IS NULL`.
    재귀 멤버: CTE 자신과 `categories`를 `c.parent_id = cte.id`로 JOIN합니다.
    경로는 `parent_path || ' > ' || c.name`으로 연결합니다.

??? success "정답"
    ```sql
    WITH RECURSIVE cat_tree AS (
        -- 앵커: 최상위 카테고리
        SELECT
            id,
            parent_id,
            name,
            name AS full_path,
            depth,
            0 AS level
        FROM categories
        WHERE parent_id IS NULL

        UNION ALL

        -- 재귀: 자식 카테고리
        SELECT
            c.id,
            c.parent_id,
            c.name,
            ct.full_path || ' > ' || c.name,
            c.depth,
            ct.level + 1
        FROM categories AS c
        INNER JOIN cat_tree AS ct ON c.parent_id = ct.id
    )
    SELECT
        id,
        full_path,
        level,
        depth
    FROM cat_tree
    ORDER BY full_path;
    ```

    **결과 예시 (일부):**

    | id | full_path | level | depth |
    | ----------: | ---------- | ----------: | ----------: |
    | 14 | CPU | 0 | 0 |
    | 16 | CPU > AMD | 1 | 1 |
    | 15 | CPU > Intel | 1 | 1 |
    | 49 | UPS/전원 | 0 | 0 |
    | 27 | 그래픽카드 | 0 | 0 |
    | 29 | 그래픽카드 > AMD | 1 | 1 |
    | 28 | 그래픽카드 > NVIDIA | 1 | 1 |
    | 45 | 네트워크 장비 | 0 | 0 |
    | ... | ... | ... | ... |

---

### 문제 7

**직원 조직도를 재귀 CTE로 전개하세요.**

대표(manager_id IS NULL)부터 시작하여 모든 직원의 직속 상관 경로를 표시합니다.

??? tip "힌트"
    `staff` 테이블의 `manager_id`가 자기 참조(Self-Join)입니다.
    앵커: `WHERE manager_id IS NULL` (최상위 관리자).
    재귀: `s.manager_id = tree.id`로 부하 직원을 연결합니다.

??? success "정답"
    ```sql
    WITH RECURSIVE org_tree AS (
        -- 앵커: 최고 관리자
        SELECT
            id,
            name,
            department,
            role,
            manager_id,
            name AS chain,
            0 AS depth
        FROM staff
        WHERE manager_id IS NULL

        UNION ALL

        -- 재귀: 부하 직원
        SELECT
            s.id,
            s.name,
            s.department,
            s.role,
            s.manager_id,
            ot.chain || ' > ' || s.name,
            ot.depth + 1
        FROM staff AS s
        INNER JOIN org_tree AS ot ON s.manager_id = ot.id
    )
    SELECT
        id,
        name,
        department,
        role,
        depth,
        chain
    FROM org_tree
    ORDER BY chain;
    ```

    **결과 예시 (일부):**

    | id | name | department | role | depth | chain |
    | ----------: | ---------- | ---------- | ---------- | ----------: | ---------- |
    | 1 | 한민재 | 경영 | admin | 0 | 한민재 |
    | 30 | 고영숙 | 물류 | staff | 1 | 한민재 > 고영숙 |
    | 45 | 김영자 | 물류 | staff | 1 | 한민재 > 김영자 |
    | 47 | 김영환 | 물류 | staff | 1 | 한민재 > 김영환 |
    | 3 | 박경수 | 경영 | admin | 1 | 한민재 > 박경수 |
    | 6 | 고준서 | 영업 | manager | 2 | 한민재 > 박경수 > 고준서 |
    | 12 | 김지혜 | 영업 | staff | 3 | 한민재 > 박경수 > 고준서 > 김지혜 |
    | 5 | 권영희 | 마케팅 | manager | 2 | 한민재 > 박경수 > 권영희 |
    | ... | ... | ... | ... | ... | ... |

---

### 문제 8

**각 관리자 아래의 총 부하 직원 수를 재귀 CTE로 구하세요.**

직접 부하뿐 아니라 간접 부하(부하의 부하)까지 포함하는 전체 팀 크기를 계산합니다.

??? tip "힌트"
    재귀 CTE로 모든 상하 관계를 전개한 뒤, 각 상위 관리자의 `id`를 루트로 기록합니다.
    루트별로 `COUNT(*) - 1` (자기 자신 제외)을 구하면 됩니다.

??? success "정답"
    ```sql
    WITH RECURSIVE subordinates AS (
        -- 앵커: 각 직원을 자기 자신의 루트로 시작
        SELECT
            id AS root_id,
            id AS member_id
        FROM staff
        WHERE is_active = 1

        UNION ALL

        -- 재귀: 부하 직원 추가
        SELECT
            sub.root_id,
            s.id
        FROM staff AS s
        INNER JOIN subordinates AS sub ON s.manager_id = sub.member_id
        WHERE s.is_active = 1
    )
    SELECT
        s.id,
        s.name,
        s.department,
        s.role,
        COUNT(*) - 1 AS total_subordinates
    FROM subordinates AS sub
    INNER JOIN staff AS s ON sub.root_id = s.id
    GROUP BY s.id, s.name, s.department, s.role
    HAVING COUNT(*) > 1
    ORDER BY total_subordinates DESC;
    ```

    **결과 예시:**

    | id | name | department | role | total_subordinates |
    | ----------: | ---------- | ---------- | ---------- | ----------: |
    | 1 | 한민재 | 경영 | admin | 33 |
    | 3 | 박경수 | 경영 | admin | 18 |
    | 5 | 권영희 | 마케팅 | manager | 9 |
    | 4 | 이준혁 | 영업 | manager | 4 |
    | 2 | 장주원 | 경영 | admin | 3 |
    | 8 | 황예준 | 경영 | manager | 2 |
    | 7 | 김영일 | 개발 | manager | 1 |
    | ... | ... | ... | ... | ... |

---

### 문제 9

**다중 CTE로 고객의 RFM(Recency, Frequency, Monetary) 세그먼트를 구축하세요.**

3개의 CTE를 체이닝합니다: (1) RFM 원시 지표, (2) NTILE 점수, (3) 세그먼트 라벨링.

??? tip "힌트"
    CTE 1(`rfm_raw`): `MAX(ordered_at)`, `COUNT(*)`, `SUM(total_amount)`.
    CTE 2(`rfm_scored`): `NTILE(4)` 적용.
    CTE 3 또는 외부 쿼리: R+F+M 합산 점수로 세그먼트(VIP/충성/일반/이탈위험)를 부여합니다.

??? success "정답"
    ```sql
    WITH rfm_raw AS (
        SELECT
            c.id            AS customer_id,
            c.name,
            c.grade,
            MAX(o.ordered_at) AS last_order_date,
            COUNT(*)          AS frequency,
            ROUND(SUM(o.total_amount), 0) AS monetary
        FROM customers AS c
        INNER JOIN orders AS o ON c.id = o.customer_id
        WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY c.id, c.name, c.grade
    ),
    rfm_scored AS (
        SELECT
            *,
            NTILE(4) OVER (ORDER BY last_order_date ASC) AS r_score,
            NTILE(4) OVER (ORDER BY frequency ASC)       AS f_score,
            NTILE(4) OVER (ORDER BY monetary ASC)         AS m_score
        FROM rfm_raw
    ),
    rfm_segment AS (
        SELECT
            *,
            r_score + f_score + m_score AS total_score,
            CASE
                WHEN r_score + f_score + m_score >= 10 THEN 'Champions'
                WHEN r_score + f_score + m_score >= 8  THEN 'Loyal'
                WHEN r_score + f_score + m_score >= 5  THEN 'Potential'
                ELSE 'At Risk'
            END AS segment
        FROM rfm_scored
    )
    SELECT
        segment,
        COUNT(*)                     AS customer_count,
        ROUND(AVG(frequency), 1)     AS avg_frequency,
        ROUND(AVG(monetary), 0)      AS avg_monetary,
        ROUND(AVG(r_score + f_score + m_score), 1) AS avg_score
    FROM rfm_segment
    GROUP BY segment
    ORDER BY avg_score DESC;
    ```

    **결과 예시:**

    | segment | customer_count | avg_frequency | avg_monetary | avg_score |
    |---|---|---|---|---|
    | Champions | 85 | 18.2 | 5200000 | 10.8 |
    | Loyal | 142 | 12.5 | 3100000 | 8.7 |
    | Potential | 320 | 6.3 | 1200000 | 6.2 |
    | At Risk | 253 | 2.1 | 350000 | 3.4 |

---

### 문제 10

**재귀 CTE로 카테고리 트리를 전개한 뒤, 각 최상위 카테고리별 소속 상품 수와 매출을 집계하세요.**

??? tip "힌트"
    재귀 CTE로 각 카테고리의 최상위 루트를 추적합니다.
    앵커에서 `id AS root_id, name AS root_name`을 기록하고,
    재귀에서 부모의 `root_id`, `root_name`을 그대로 전파합니다.
    결과에 `products`, `order_items`, `orders`를 JOIN하여 루트별 집계합니다.

??? success "정답"
    ```sql
    WITH RECURSIVE cat_root AS (
        -- 앵커: 최상위 카테고리 (자기 자신이 루트)
        SELECT
            id,
            id   AS root_id,
            name AS root_name
        FROM categories
        WHERE parent_id IS NULL

        UNION ALL

        -- 재귀: 자식 카테고리는 부모의 루트를 상속
        SELECT
            c.id,
            cr.root_id,
            cr.root_name
        FROM categories AS c
        INNER JOIN cat_root AS cr ON c.parent_id = cr.id
    )
    SELECT
        cr.root_name                  AS top_category,
        COUNT(DISTINCT p.id)          AS product_count,
        ROUND(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
        SUM(oi.quantity)              AS units_sold
    FROM cat_root AS cr
    INNER JOIN products   AS p  ON p.category_id = cr.id
    INNER JOIN order_items AS oi ON oi.product_id = p.id
    INNER JOIN orders     AS o  ON oi.order_id   = o.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY cr.root_id, cr.root_name
    ORDER BY total_revenue DESC;
    ```

    **결과 예시:**

    | top_category | product_count | total_revenue | units_sold |
    | ---------- | ----------: | ----------: | ----------: |
    | 노트북 | 237 | 16183602000.0 | 7592 |
    | 그래픽카드 | 99 | 10026900600.0 | 6451 |
    | 모니터 | 169 | 6381505300.0 | 7250 |
    | 메인보드 | 149 | 4331432400.0 | 10848 |
    | CPU | 29 | 2972276700.0 | 6313 |
    | 저장장치 | 160 | 2816457800.0 | 13058 |
    | 스피커/헤드셋 | 98 | 2473846600.0 | 10839 |
    | 키보드 | 165 | 2218745800.0 | 16740 |
    | ... | ... | ... | ... |

---

## 실전 (11~15)

3개 이상의 CTE 체인, 재귀 깊이 활용, 날짜 시퀀스 생성 등 고급 패턴을 다룹니다.

---

### 문제 11

**재귀 CTE로 월 시퀀스를 생성하고, 매출이 없는 월도 포함한 월별 보고서를 만드세요.**

2024-01 ~ 2024-12의 12개월 시퀀스를 재귀 CTE로 생성하고, 실제 매출 데이터와 LEFT JOIN합니다.

??? tip "힌트"
    재귀 CTE로 '2024-01'부터 시작하여 매월 +1씩 증가하는 시퀀스를 만듭니다.
    `DATE(year_month || '-01', '+1 month')`로 다음 달을 계산하고, `SUBSTR(..., 1, 7)`로 포맷합니다.
    종료 조건: `year_month < '2024-12'`.

??? success "정답"
    ```sql
    WITH RECURSIVE months AS (
        SELECT '2024-01' AS year_month
        UNION ALL
        SELECT SUBSTR(DATE(year_month || '-01', '+1 month'), 1, 7)
        FROM months
        WHERE year_month < '2024-12'
    ),
    actual_revenue AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            COUNT(*)                 AS order_count,
            ROUND(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        m.year_month,
        COALESCE(a.order_count, 0) AS order_count,
        COALESCE(a.revenue, 0)     AS revenue
    FROM months AS m
    LEFT JOIN actual_revenue AS a ON m.year_month = a.year_month
    ORDER BY m.year_month;
    ```

    **결과 (12행):**

    | year_month | order_count | revenue |
    | ---------- | ----------: | ----------: |
    | 2024-01 | 3795 | 3737010508.0 |
    | 2024-02 | 4469 | 4630208028.0 |
    | 2024-03 | 4817 | 4811012761.0 |
    | 2024-04 | 4858 | 4852046384.0 |
    | 2024-05 | 4917 | 4796192371.0 |
    | 2024-06 | 3670 | 3787186898.0 |
    | 2024-07 | 4378 | 4370145415.0 |
    | 2024-08 | 4753 | 4778870727.0 |
    | ... | ... | ... |

    > 모든 월이 빠짐없이 표시됩니다. 데이터가 없는 월은 0으로 채워집니다.

---

### 문제 12

**3단계 CTE 체인으로 상품 성과 등급을 산출하세요.**

CTE 1: 상품별 매출. CTE 2: 매출 기준 NTILE(5) 등급. CTE 3: 등급별 통계.
최종 출력은 등급별 상품 수, 매출 범위, 대표 상품(매출 1위)을 포함합니다.

??? tip "힌트"
    CTE 3에서 `FIRST_VALUE(product_name) OVER (PARTITION BY tier ORDER BY revenue DESC)`로
    각 등급의 대표 상품을 추출합니다.
    `DISTINCT`를 활용하여 등급별 한 행으로 요약합니다.

??? success "정답"
    ```sql
    WITH product_sales AS (
        SELECT
            p.id       AS product_id,
            p.name     AS product_name,
            ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue,
            SUM(oi.quantity) AS units_sold
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY p.id, p.name
    ),
    tiered AS (
        SELECT
            *,
            NTILE(5) OVER (ORDER BY revenue DESC) AS tier
        FROM product_sales
    ),
    tier_summary AS (
        SELECT DISTINCT
            tier,
            COUNT(*) OVER (PARTITION BY tier) AS product_count,
            MIN(revenue) OVER (PARTITION BY tier) AS min_revenue,
            MAX(revenue) OVER (PARTITION BY tier) AS max_revenue,
            ROUND(AVG(revenue) OVER (PARTITION BY tier), 0) AS avg_revenue,
            FIRST_VALUE(product_name) OVER (
                PARTITION BY tier ORDER BY revenue DESC
            ) AS top_product
        FROM tiered
    )
    SELECT
        tier,
        CASE tier
            WHEN 1 THEN 'S (최상위)'
            WHEN 2 THEN 'A (우수)'
            WHEN 3 THEN 'B (보통)'
            WHEN 4 THEN 'C (저조)'
            WHEN 5 THEN 'D (부진)'
        END AS tier_label,
        product_count,
        min_revenue,
        max_revenue,
        avg_revenue,
        top_product
    FROM tier_summary
    ORDER BY tier;
    ```

    **결과 예시:**

    | tier | tier_label | product_count | min_revenue | max_revenue | avg_revenue | top_product |
    |---|---|---|---|---|---|---|
    | 1 | S (최상위) | 20 | 15000000 | 45200000 | 25000000 | MacBook Pro 16 M3 |
    | 2 | A (우수) | 20 | 8000000 | 14800000 | 11000000 | ASUS ROG Strix ... |
    | 3 | B (보통) | 20 | 3500000 | 7900000 | 5500000 | Logitech MX ... |
    | 4 | C (저조) | 20 | 1200000 | 3400000 | 2100000 | ... |
    | 5 | D (부진) | 20 | 50000 | 1100000 | 580000 | ... |

---

### 문제 13

**재귀 CTE로 연속 날짜 시퀀스를 생성하고, 주문이 없는 날(갭)을 찾으세요.**

2024-01-01 ~ 2024-12-31의 연속 날짜를 생성하고, 주문이 0건인 날을 추출합니다.

??? tip "힌트"
    재귀 CTE에서 `DATE(date_val, '+1 day')`로 하루씩 증가합니다.
    `LEFT JOIN`으로 실제 주문일과 연결하고, 주문이 NULL인 날을 필터링합니다.
    또는 `calendar` 테이블이 있다면 그것을 활용해도 됩니다.

??? success "정답"
    ```sql
    WITH RECURSIVE date_seq AS (
        SELECT '2024-01-01' AS date_val
        UNION ALL
        SELECT DATE(date_val, '+1 day')
        FROM date_seq
        WHERE date_val < '2024-12-31'
    ),
    daily_orders AS (
        SELECT
            DATE(ordered_at) AS order_date,
            COUNT(*)         AS order_count
        FROM orders
        WHERE ordered_at >= '2024-01-01'
          AND ordered_at < '2025-01-01'
          AND status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY DATE(ordered_at)
    )
    SELECT
        d.date_val AS gap_date,
        CASE CAST(STRFTIME('%w', d.date_val) AS INTEGER)
            WHEN 0 THEN '일'
            WHEN 1 THEN '월'
            WHEN 2 THEN '화'
            WHEN 3 THEN '수'
            WHEN 4 THEN '목'
            WHEN 5 THEN '금'
            WHEN 6 THEN '토'
        END AS day_name
    FROM date_seq AS d
    LEFT JOIN daily_orders AS o ON d.date_val = o.order_date
    WHERE o.order_count IS NULL
    ORDER BY d.date_val;
    ```

    **결과 예시:**

    | gap_date | day_name |
    |---|---|
    | 2024-01-01 | 월 |
    | 2024-02-10 | 토 |
    | 2024-05-01 | 수 |
    | ... | ... |

    > 공휴일이나 주말에 주문이 없는 날이 주로 나타납니다.

---

### 문제 14

**4단계 CTE 체인으로 "코호트 리텐션" 분석을 수행하세요.**

CTE 1: 고객별 첫 주문 월(코호트). CTE 2: 고객별 주문 월 목록. CTE 3: 코호트-상대월 매핑. CTE 4: 코호트별 리텐션율.

??? tip "힌트"
    상대 월은 `(CAST(SUBSTR(order_month,1,4) AS INTEGER)*12 + CAST(SUBSTR(order_month,6,2) AS INTEGER))
    - (CAST(SUBSTR(cohort_month,1,4) AS INTEGER)*12 + CAST(SUBSTR(cohort_month,6,2) AS INTEGER))`로 계산합니다.
    리텐션율 = 해당 월 활성 고객 / 코호트 총 고객 * 100.

??? success "정답"
    ```sql
    WITH cohort AS (
        SELECT
            customer_id,
            SUBSTR(MIN(ordered_at), 1, 7) AS cohort_month
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    order_months AS (
        SELECT DISTINCT
            customer_id,
            SUBSTR(ordered_at, 1, 7) AS order_month
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    ),
    cohort_activity AS (
        SELECT
            co.cohort_month,
            (CAST(SUBSTR(om.order_month, 1, 4) AS INTEGER) * 12
             + CAST(SUBSTR(om.order_month, 6, 2) AS INTEGER))
          - (CAST(SUBSTR(co.cohort_month, 1, 4) AS INTEGER) * 12
             + CAST(SUBSTR(co.cohort_month, 6, 2) AS INTEGER)) AS months_since,
            COUNT(DISTINCT om.customer_id) AS active_customers
        FROM cohort AS co
        INNER JOIN order_months AS om ON co.customer_id = om.customer_id
        GROUP BY co.cohort_month, months_since
    ),
    cohort_size AS (
        SELECT
            cohort_month,
            COUNT(*) AS total_customers
        FROM cohort
        GROUP BY cohort_month
    )
    SELECT
        ca.cohort_month,
        cs.total_customers,
        ca.months_since,
        ca.active_customers,
        ROUND(100.0 * ca.active_customers / cs.total_customers, 1) AS retention_pct
    FROM cohort_activity AS ca
    INNER JOIN cohort_size AS cs ON ca.cohort_month = cs.cohort_month
    WHERE ca.cohort_month >= '2024-01'
      AND ca.months_since <= 6
    ORDER BY ca.cohort_month, ca.months_since;
    ```

    **결과 예시 (일부):**

    | cohort_month | total_customers | months_since | active_customers | retention_pct |
    |---|---|---|---|---|
    | 2024-01 | 45 | 0 | 45 | 100.0 |
    | 2024-01 | 45 | 1 | 18 | 40.0 |
    | 2024-01 | 45 | 2 | 12 | 26.7 |
    | 2024-01 | 45 | 3 | 9 | 20.0 |
    | 2024-02 | 38 | 0 | 38 | 100.0 |
    | 2024-02 | 38 | 1 | 15 | 39.5 |
    | ... | ... | ... | ... | ... |

---

### 문제 15

**재귀 CTE로 카테고리 깊이별 통계를 구하고, 트리 형태로 시각화하세요.**

각 카테고리의 인덴트(depth에 따른 공백)를 포함하여 트리 구조를 텍스트로 표현하고,
각 카테고리의 직속 상품 수와 하위 전체 상품 수를 함께 표시합니다.

??? tip "힌트"
    재귀 CTE로 카테고리 트리를 전개하며, 정렬용 `sort_path`를 만듭니다(예: `'001/003/007'`).
    인덴트는 `REPLACE(SUBSTR('                ', 1, level * 4), ' ', ' ')` 또는
    `CASE level WHEN 0 THEN '' WHEN 1 THEN '  ' WHEN 2 THEN '    ' END` 등으로 표현합니다.

??? success "정답"
    ```sql
    WITH RECURSIVE cat_tree AS (
        SELECT
            id,
            parent_id,
            name,
            depth,
            sort_order,
            PRINTF('%03d', sort_order) AS sort_path,
            0 AS level
        FROM categories
        WHERE parent_id IS NULL

        UNION ALL

        SELECT
            c.id,
            c.parent_id,
            c.name,
            c.depth,
            c.sort_order,
            ct.sort_path || '/' || PRINTF('%03d', c.sort_order),
            ct.level + 1
        FROM categories AS c
        INNER JOIN cat_tree AS ct ON c.parent_id = ct.id
    ),
    direct_products AS (
        SELECT category_id, COUNT(*) AS direct_count
        FROM products
        WHERE is_active = 1
        GROUP BY category_id
    )
    SELECT
        ct.id,
        CASE ct.level
            WHEN 0 THEN ct.name
            WHEN 1 THEN '  ' || ct.name
            WHEN 2 THEN '    ' || ct.name
        END AS tree_display,
        ct.level,
        COALESCE(dp.direct_count, 0) AS direct_products
    FROM cat_tree AS ct
    LEFT JOIN direct_products AS dp ON ct.id = dp.category_id
    ORDER BY ct.sort_path;
    ```

    **결과 예시 (일부):**

    | id | tree_display | level | direct_products |
    |---|---|---|---|
    | 1 | 데스크탑/워크스테이션 | 0 | 0 |
    | 3 |   데스크탑 PC | 1 | 0 |
    | 5 |     게이밍 데스크탑 | 2 | 15 |
    | 6 |     사무용 데스크탑 | 2 | 12 |
    | 2 | 노트북/태블릿 | 0 | 0 |
    | 4 |   노트북 | 1 | 0 |
    | 7 |     게이밍 노트북 | 2 | 18 |
    | 8 |     비즈니스 노트북 | 2 | 14 |

    > 최상위/중간 카테고리는 상품을 직접 갖지 않고, 리프(depth=2) 카테고리만 상품을 보유합니다.
