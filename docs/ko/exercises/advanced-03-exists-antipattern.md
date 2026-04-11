# EXISTS와 안티 패턴

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `customers`, `orders`, `order_items`, `products`, `reviews`, `wishlists`, `complaints`, `categories`, `payments`

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    `EXISTS`, `NOT EXISTS`, 상관 서브쿼리, 안티 조인 패턴, 전칭 한정(Universal Quantification)

</div>

!!! info "시작하기 전에"
    이 연습은 **고급 20강**(EXISTS)에서 배운 내용을 실전에 적용합니다.
    `EXISTS`는 서브쿼리의 결과가 한 행이라도 있으면 TRUE를 반환합니다.
    `NOT EXISTS`는 그 반대 — 결과가 한 행도 없을 때 TRUE입니다.

---

## 기초 (1~5)

EXISTS와 NOT EXISTS의 기본 사용법을 연습합니다.

---

### 문제 1

**2024년에 주문을 한 적이 있는 고객만 조회하세요.**

고객 ID, 이름, 등급, 가입일을 표시합니다. `EXISTS`를 사용하세요.

??? tip "힌트"
    `WHERE EXISTS (SELECT 1 FROM orders WHERE customer_id = c.id AND ...)`
    서브쿼리에서 외부 쿼리의 `c.id`를 참조하는 것이 상관 서브쿼리입니다.

??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        c.created_at AS signup_date
    FROM customers AS c
    WHERE EXISTS (
        SELECT 1
        FROM orders AS o
        WHERE o.customer_id = c.id
          AND o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    ORDER BY c.id
    LIMIT 20;
    ```

    **결과 예시 (상위 5행):**

    | id | name | grade | signup_date |
    |---|---|---|---|
    | 1 | 김... | GOLD | 2017-03-15 ... |
    | 3 | 박... | VIP | 2016-11-22 ... |
    | 5 | 이... | SILVER | 2019-05-08 ... |
    | 7 | 최... | BRONZE | 2022-01-14 ... |
    | 9 | 정... | GOLD | 2020-07-30 ... |

    > `IN` 서브쿼리와 동일한 결과를 반환하지만, 대규모 데이터에서는 `EXISTS`가 더 효율적입니다.

---

### 문제 2

**한 번도 주문한 적이 없는 고객을 찾으세요.**

가입만 하고 주문 이력이 전혀 없는 고객입니다. `NOT EXISTS`를 사용하세요.

??? tip "힌트"
    `WHERE NOT EXISTS (SELECT 1 FROM orders WHERE customer_id = c.id)`
    이때 취소/반품 주문도 "주문한 적 있음"으로 간주합니다 (상태 필터 없음).

??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        c.created_at AS signup_date,
        ROUND(JULIANDAY('2025-12-31') - JULIANDAY(c.created_at), 0) AS days_since_signup
    FROM customers AS c
    WHERE NOT EXISTS (
        SELECT 1
        FROM orders AS o
        WHERE o.customer_id = c.id
    )
    ORDER BY c.created_at
    LIMIT 20;
    ```

    **결과 예시 (상위 5행):**

    | id | name | grade | signup_date | days_since_signup |
    |---|---|---|---|---|
    | 42 | 한... | BRONZE | 2018-06-12 ... | 2759 |
    | 88 | 송... | BRONZE | 2019-02-28 ... | 2498 |
    | 105 | 강... | BRONZE | 2019-09-15 ... | 2299 |
    | ... | ... | ... | ... | ... |

---

### 문제 3

**리뷰를 남기지 않은 구매 확인 고객을 찾으세요.**

주문 상태가 'confirmed'인 주문이 있지만 리뷰를 단 한 건도 작성하지 않은 고객입니다.

??? tip "힌트"
    조건 2개를 조합합니다:
    `EXISTS (... orders WHERE status = 'confirmed')` AND
    `NOT EXISTS (... reviews WHERE customer_id = c.id)`.

??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(o.id) AS confirmed_orders
    FROM customers AS c
    INNER JOIN orders AS o
        ON c.id = o.customer_id
       AND o.status = 'confirmed'
    WHERE NOT EXISTS (
        SELECT 1
        FROM reviews AS r
        WHERE r.customer_id = c.id
    )
    GROUP BY c.id, c.name, c.grade
    ORDER BY confirmed_orders DESC
    LIMIT 15;
    ```

    **결과 예시 (상위 3행):**

    | id | name | grade | confirmed_orders |
    |---|---|---|---|
    | 156 | 김... | SILVER | 12 |
    | 203 | 이... | GOLD | 9 |
    | 78 | 박... | BRONZE | 7 |

    > 리뷰 작성 캠페인의 타겟 고객으로 활용할 수 있습니다.

---

### 문제 4

**위시리스트에 담았지만 아직 구매하지 않은 상품-고객 조합을 찾으세요.**

위시리스트의 `is_purchased = 0`인 항목 중, 해당 고객이 해당 상품을 실제로 주문한 적도 없는 경우입니다.

??? tip "힌트"
    `wishlists`를 기준으로, `NOT EXISTS`로 `order_items`와 `orders`를 결합한 서브쿼리를 만듭니다.
    서브쿼리 조건: 같은 `customer_id`와 같은 `product_id`.

??? success "정답"
    ```sql
    SELECT
        w.customer_id,
        c.name     AS customer_name,
        w.product_id,
        p.name     AS product_name,
        p.price,
        w.created_at AS wishlisted_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products  AS p ON w.product_id  = p.id
    WHERE w.is_purchased = 0
      AND NOT EXISTS (
          SELECT 1
          FROM order_items AS oi
          INNER JOIN orders AS o ON oi.order_id = o.id
          WHERE o.customer_id = w.customer_id
            AND oi.product_id = w.product_id
            AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    ORDER BY w.created_at DESC
    LIMIT 15;
    ```

    **결과 예시 (상위 3행):**

    | customer_id | customer_name | product_id | product_name | price | wishlisted_at |
    |---|---|---|---|---|---|
    | 45 | 한... | 12 | MacBook Air M3 | 1590000 | 2025-11-20 ... |
    | 112 | 송... | 78 | LG 울트라기어 32GP850 | 720000 | 2025-10-15 ... |
    | 203 | 강... | 5 | 삼성 Galaxy Tab S9 | 890000 | 2025-09-08 ... |

    > 마케팅팀이 장바구니 이탈 알림이나 할인 쿠폰을 보낼 대상입니다.

---

### 문제 5

**CS 문의가 접수된 적이 없는 고객 중, 주문 금액 상위 10명을 찾으세요.**

클레임 없이 꾸준히 구매하는 "우량 고객"을 식별합니다.

??? tip "힌트"
    `NOT EXISTS (SELECT 1 FROM complaints WHERE customer_id = c.id)`로 문의 이력이 없는 고객을 필터링하고,
    `SUM(total_amount)`으로 총 구매 금액 상위 10명을 추출합니다.

??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      AND NOT EXISTS (
          SELECT 1
          FROM complaints AS cp
          WHERE cp.customer_id = c.id
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```

    **결과 예시 (상위 3행):**

    | id | name | grade | order_count | total_spent |
    |---|---|---|---|---|
    | 67 | 이... | VIP | 28 | 8950000 |
    | 134 | 최... | GOLD | 22 | 7200000 |
    | 89 | 박... | VIP | 25 | 6800000 |

---

## 응용 (6~10)

상관 서브쿼리와 집계를 결합한 복합 EXISTS 조건을 다룹니다.

---

### 문제 6

**3개 이상의 서로 다른 카테고리에서 상품을 구매한 고객을 찾으세요.**

EXISTS 내부에서 집계를 사용합니다.

??? tip "힌트"
    `EXISTS` 안에서 `GROUP BY customer_id HAVING COUNT(DISTINCT category_id) >= 3`을 사용합니다.
    또는 상관 서브쿼리로 카테고리 수를 세는 방법도 있습니다.

??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade
    FROM customers AS c
    WHERE EXISTS (
        SELECT 1
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.customer_id = c.id
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY o.customer_id
        HAVING COUNT(DISTINCT p.category_id) >= 3
    )
    ORDER BY c.grade DESC, c.name
    LIMIT 20;
    ```

    **결과 예시 (상위 5행):**

    | id | name | grade |
    |---|---|---|
    | 12 | 김... | VIP |
    | 45 | 박... | VIP |
    | 78 | 이... | VIP |
    | 23 | 최... | GOLD |
    | 56 | 정... | GOLD |

    > 다양한 카테고리를 구매하는 고객은 크로스셀링 대상으로 가치가 높습니다.

---

### 문제 7

**모든 결제가 정상 완료된 주문만 조회하세요.**

한 주문에 여러 결제가 있을 수 있습니다. 실패(`failed`)나 환불(`refunded`)된 결제가 하나라도 없는 주문을 찾습니다.

??? tip "힌트"
    "실패/환불이 없다" = `NOT EXISTS (... payments WHERE status IN ('failed', 'refunded') AND order_id = o.id)`.
    추가로 결제가 하나 이상 존재해야 합니다(`EXISTS`).

??? success "정답"
    ```sql
    SELECT
        o.id,
        o.order_number,
        o.total_amount,
        o.ordered_at,
        o.status
    FROM orders AS o
    WHERE EXISTS (
        SELECT 1
        FROM payments AS p
        WHERE p.order_id = o.id
          AND p.status = 'completed'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM payments AS p
        WHERE p.order_id = o.id
          AND p.status IN ('failed', 'refunded')
    )
    AND o.ordered_at LIKE '2024%'
    ORDER BY o.ordered_at DESC
    LIMIT 15;
    ```

    **결과 예시 (상위 3행):**

    | id | order_number | total_amount | ordered_at | status |
    |---|---|---|---|---|
    | 8950 | ORD-20241228-... | 1250000 | 2024-12-28 ... | delivered |
    | 8948 | ORD-20241228-... | 380000 | 2024-12-28 ... | confirmed |
    | 8945 | ORD-20241227-... | 890000 | 2024-12-27 ... | delivered |

---

### 문제 8

**특정 상품(ID=1)과 함께 자주 구매되는 상품을 찾으세요 (동시 구매 분석).**

상품 1을 포함한 주문에서, 상품 1 이외의 다른 상품 중 동시 구매 빈도가 높은 순으로 정렬합니다.

??? tip "힌트"
    외부 쿼리는 `order_items`에서 `product_id != 1`인 항목을 집계합니다.
    `EXISTS`로 "해당 주문에 상품 1이 포함되어 있는지"를 확인합니다.

??? success "정답"
    ```sql
    SELECT
        p.id    AS product_id,
        p.name  AS product_name,
        p.price,
        COUNT(DISTINCT oi.order_id) AS co_purchase_count
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    WHERE oi.product_id != 1
      AND EXISTS (
          SELECT 1
          FROM order_items AS oi2
          WHERE oi2.order_id   = oi.order_id
            AND oi2.product_id = 1
      )
    GROUP BY p.id, p.name, p.price
    ORDER BY co_purchase_count DESC
    LIMIT 10;
    ```

    **결과 예시 (상위 3행):**

    | product_id | product_name | price | co_purchase_count |
    |---|---|---|---|
    | 45 | Logitech MX Master 3S | 119000 | 8 |
    | 23 | 삼성 EVO 970 Plus 1TB | 145000 | 6 |
    | 67 | Dell U2723QE 모니터 | 720000 | 5 |

    > 연관 상품 추천(Cross-selling) 전략의 데이터 근거가 됩니다.

---

### 문제 9

**"매월 빠짐없이 주문한 고객"을 찾으세요 (2024년 12개월).**

2024년의 모든 12개월에 최소 1건의 주문이 있는 고객입니다.

??? tip "힌트"
    `NOT EXISTS`와 재귀 CTE(또는 하드코딩된 월 리스트)를 조합합니다.
    "모든 월에 주문이 있다" = "주문이 없는 월이 존재하지 않는다" (NOT EXISTS).

??? success "정답"
    ```sql
    WITH RECURSIVE months AS (
        SELECT '2024-01' AS ym
        UNION ALL
        SELECT SUBSTR(DATE(ym || '-01', '+1 month'), 1, 7)
        FROM months
        WHERE ym < '2024-12'
    )
    SELECT
        c.id,
        c.name,
        c.grade
    FROM customers AS c
    WHERE NOT EXISTS (
        -- 주문이 없는 월이 하나라도 있으면 제외
        SELECT 1
        FROM months AS m
        WHERE NOT EXISTS (
            SELECT 1
            FROM orders AS o
            WHERE o.customer_id = c.id
              AND SUBSTR(o.ordered_at, 1, 7) = m.ym
              AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        )
    )
    ORDER BY c.grade DESC, c.name;
    ```

    **결과 예시:**

    | id | name | grade |
    |---|---|---|
    | 12 | 김... | VIP |
    | 45 | 박... | VIP |
    | 78 | 이... | GOLD |

    > 이 쿼리는 **이중 부정(Double Negation)** 패턴입니다:
    > "주문이 없는 월이 **존재하지 않는** 고객" = "모든 월에 주문한 고객".
    > 관계 대수의 나눗셈(Division)에 해당하는 SQL 표현입니다.

---

### 문제 10

**2024년에 주문은 했지만 2025년에는 주문하지 않은 "이탈 고객"을 찾으세요.**

두 개의 EXISTS/NOT EXISTS 조건을 결합합니다.

??? tip "힌트"
    `EXISTS (... 2024년 주문)` AND `NOT EXISTS (... 2025년 주문)`.
    이탈 고객의 2024년 마지막 주문일과 총 구매 금액도 표시하면 유용합니다.

??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order_date,
        COUNT(o.id) AS orders_in_2024,
        ROUND(SUM(o.total_amount), 0) AS spent_in_2024
    FROM customers AS c
    INNER JOIN orders AS o
        ON c.id = o.customer_id
       AND o.ordered_at LIKE '2024%'
       AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    WHERE NOT EXISTS (
        SELECT 1
        FROM orders AS o2
        WHERE o2.customer_id = c.id
          AND o2.ordered_at LIKE '2025%'
          AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    GROUP BY c.id, c.name, c.grade
    ORDER BY spent_in_2024 DESC
    LIMIT 15;
    ```

    **결과 예시 (상위 3행):**

    | id | name | grade | last_order_date | orders_in_2024 | spent_in_2024 |
    |---|---|---|---|---|---|
    | 156 | 한... | GOLD | 2024-11-18 ... | 8 | 3200000 |
    | 203 | 송... | SILVER | 2024-10-05 ... | 5 | 1850000 |
    | 89 | 윤... | SILVER | 2024-12-22 ... | 6 | 1540000 |

---

## 실전 (11~15)

전칭 한정, 복합 NOT EXISTS, 안티 패턴 등 고급 시나리오를 다룹니다.

---

### 문제 11

**모든 주문에서 카드로만 결제한 고객을 찾으세요.**

카드 외 결제 수단(kakao_pay, naver_pay, bank_transfer 등)을 한 번도 사용하지 않은 고객입니다.

??? tip "힌트"
    전칭 한정: "모든 결제가 카드" = "카드가 아닌 결제가 **존재하지 않는다**".
    `NOT EXISTS (... payments WHERE method != 'card' ...)`를 사용합니다.
    주문 이력이 있는 고객만 대상으로 합니다.

??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      -- 카드가 아닌 결제가 한 건도 없어야 함
      AND NOT EXISTS (
          SELECT 1
          FROM payments AS p
          INNER JOIN orders AS o2 ON p.order_id = o2.id
          WHERE o2.customer_id = c.id
            AND p.method != 'card'
      )
      -- 결제 이력이 있어야 함
      AND EXISTS (
          SELECT 1
          FROM payments AS p
          INNER JOIN orders AS o3 ON p.order_id = o3.id
          WHERE o3.customer_id = c.id
            AND p.method = 'card'
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 15;
    ```

    **결과 예시 (상위 3행):**

    | id | name | grade | order_count | total_spent |
    |---|---|---|---|---|
    | 34 | 최... | GOLD | 15 | 4800000 |
    | 112 | 김... | SILVER | 10 | 2900000 |
    | 256 | 박... | SILVER | 8 | 2100000 |

---

### 문제 12

**"모든 종류의 문의 카테고리"를 경험한 고객을 찾으세요.**

`complaints` 테이블의 모든 `category` 값에 대해 최소 1건의 문의를 제출한 고객입니다.

??? tip "힌트"
    전칭 한정의 이중 부정 패턴:
    "모든 카테고리에 문의가 있다" = "문의가 없는 카테고리가 **존재하지 않는다**".
    `NOT EXISTS (SELECT category FROM (SELECT DISTINCT category FROM complaints) WHERE NOT EXISTS (... 해당 고객의 해당 카테고리 문의))`.

??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        (SELECT COUNT(DISTINCT cp.category) FROM complaints AS cp WHERE cp.customer_id = c.id) AS category_count
    FROM customers AS c
    WHERE NOT EXISTS (
        -- 문의가 없는 카테고리가 하나라도 있으면 제외
        SELECT DISTINCT cp_all.category
        FROM complaints AS cp_all
        WHERE NOT EXISTS (
            SELECT 1
            FROM complaints AS cp
            WHERE cp.customer_id = c.id
              AND cp.category = cp_all.category
        )
    )
    ORDER BY c.name;
    ```

    **결과 예시:**

    | id | name | grade | category_count |
    |---|---|---|---|
    | 45 | 김... | SILVER | 7 |
    | 203 | 박... | BRONZE | 7 |

    > 모든 카테고리에 문의를 남긴 고객은 매우 드뭅니다. CS팀의 특별 관리 대상일 수 있습니다.

---

### 문제 13

**"가격이 100만원 이상인 상품만 구매한" 고객을 찾으세요.**

저가 상품을 한 번도 구매하지 않은 프리미엄 고객입니다.

??? tip "힌트"
    "100만원 미만 상품 구매가 존재하지 않는다":
    `NOT EXISTS (... order_items JOIN products WHERE price < 1000000 AND customer_id = c.id)`.
    동시에 주문 이력은 있어야 합니다(`EXISTS`).

??? success "정답"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent,
        ROUND(AVG(o.total_amount), 0) AS avg_order_value
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      -- 100만원 미만 상품 구매가 없어야 함
      AND NOT EXISTS (
          SELECT 1
          FROM order_items AS oi
          INNER JOIN orders AS o2 ON oi.order_id = o2.id
          INNER JOIN products AS p ON oi.product_id = p.id
          WHERE o2.customer_id = c.id
            AND p.price < 1000000
            AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```

    **결과 예시 (상위 3행):**

    | id | name | grade | order_count | total_spent | avg_order_value |
    |---|---|---|---|---|---|
    | 67 | 이... | VIP | 8 | 12500000 | 1562500 |
    | 134 | 최... | GOLD | 5 | 7800000 | 1560000 |
    | 89 | 한... | VIP | 6 | 7200000 | 1200000 |

---

### 문제 14

**재구매 상품 쌍을 찾으세요 — 같은 고객이 다른 주문에서 동일 상품을 2번 이상 구매한 경우입니다.**

EXISTS로 "동일 고객, 동일 상품, 다른 주문"을 확인합니다.

??? tip "힌트"
    `order_items`를 기준으로, `EXISTS`에서 같은 `product_id`, 같은 `customer_id`이지만
    다른 `order_id`인 레코드가 있는지 확인합니다.
    고객-상품 조합별로 재구매 횟수를 집계합니다.

??? success "정답"
    ```sql
    SELECT
        c.name     AS customer_name,
        p.name     AS product_name,
        COUNT(DISTINCT oi.order_id) AS purchase_count,
        SUM(oi.quantity) AS total_qty
    FROM order_items AS oi
    INNER JOIN orders    AS o ON oi.order_id   = o.id
    INNER JOIN customers AS c ON o.customer_id = c.id
    INNER JOIN products  AS p ON oi.product_id = p.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      AND EXISTS (
          -- 같은 고객이 같은 상품을 다른 주문에서 구매
          SELECT 1
          FROM order_items AS oi2
          INNER JOIN orders AS o2 ON oi2.order_id = o2.id
          WHERE o2.customer_id = o.customer_id
            AND oi2.product_id = oi.product_id
            AND oi2.order_id   != oi.order_id
            AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    GROUP BY c.id, c.name, p.id, p.name
    ORDER BY purchase_count DESC
    LIMIT 15;
    ```

    **결과 예시 (상위 3행):**

    | customer_name | product_name | purchase_count | total_qty |
    |---|---|---|---|
    | 김... | 삼성 DDR4 32GB | 4 | 8 |
    | 박... | Logitech MX Keys Mini | 3 | 3 |
    | 이... | Samsung EVO 970 Plus 1TB | 3 | 5 |

    > 소모품이나 추가 구매 가능성이 높은 상품이 주로 나타납니다.

---

### 문제 15

**"NOT EXISTS vs LEFT JOIN IS NULL" 안티 조인 패턴을 비교하세요.**

2024년에 리뷰를 남기지 않은 상품을 두 가지 방법으로 조회하고, 결과가 동일한지 확인합니다.

??? tip "힌트"
    방법 1: `NOT EXISTS (SELECT 1 FROM reviews WHERE product_id = p.id AND created_at LIKE '2024%')`.
    방법 2: `LEFT JOIN reviews ON ... WHERE r.id IS NULL`.
    두 쿼리를 `EXCEPT`로 비교하면 차집합이 비어 있어야 합니다.

??? success "정답"
    ```sql
    -- 방법 1: NOT EXISTS
    SELECT p.id, p.name
    FROM products AS p
    WHERE p.is_active = 1
      AND NOT EXISTS (
          SELECT 1
          FROM reviews AS r
          WHERE r.product_id = p.id
            AND r.created_at LIKE '2024%'
      )
    ORDER BY p.id;
    ```

    ```sql
    -- 방법 2: LEFT JOIN ... IS NULL
    SELECT p.id, p.name
    FROM products AS p
    LEFT JOIN reviews AS r
        ON r.product_id = p.id
       AND r.created_at LIKE '2024%'
    WHERE p.is_active = 1
      AND r.id IS NULL
    ORDER BY p.id;
    ```

    ```sql
    -- 동일성 검증: 차집합이 비어야 함
    SELECT p.id, p.name
    FROM products AS p
    WHERE p.is_active = 1
      AND NOT EXISTS (
          SELECT 1 FROM reviews AS r
          WHERE r.product_id = p.id AND r.created_at LIKE '2024%'
      )

    EXCEPT

    SELECT p.id, p.name
    FROM products AS p
    LEFT JOIN reviews AS r
        ON r.product_id = p.id AND r.created_at LIKE '2024%'
    WHERE p.is_active = 1
      AND r.id IS NULL;
    ```

    **검증 결과:**

    | id | name |
    |---|---|
    | *(빈 결과)* | |

    > 두 방법은 논리적으로 동일한 결과를 반환합니다.
    > `NOT EXISTS`는 가독성이 좋고, `LEFT JOIN ... IS NULL`은 추가 칼럼 활용에 유리합니다.
    > 실행 계획(EXPLAIN)을 비교하면 성능 차이를 확인할 수 있습니다.
