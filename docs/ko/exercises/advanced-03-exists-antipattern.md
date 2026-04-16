# EXISTS와 안티 패턴

!!! info "사용 테이블"
    `customers` — 고객 (등급, 포인트, 가입채널)  
    `orders` — 주문 (상태, 금액, 일시)  
    `order_items` — 주문 상세 (수량, 단가)  
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `reviews` — 리뷰 (평점, 내용)  
    `wishlists` — 위시리스트 (고객-상품)  
    `complaints` — 고객 불만 (유형, 우선순위)  
    `categories` — 카테고리 (부모-자식 계층)  
    `payments` — 결제 (방법, 금액, 상태)  

!!! abstract "학습 범위"
    `EXISTS`, `NOT EXISTS`, 상관 서브쿼리, 안티 조인 패턴, 전칭 한정(Universal Quantification)

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
    | ----------: | ---------- | ---------- | ---------- |
    | 2 | 김경수 | BRONZE | 2016-08-17 12:29:34 |
    | 3 | 김민재 | VIP | 2016-02-11 19:59:38 |
    | 4 | 진정자 | GOLD | 2016-09-18 15:29:45 |
    | 5 | 이정수 | BRONZE | 2016-02-28 11:34:16 |
    | 8 | 성민석 | VIP | 2016-09-24 06:49:22 |
    | 10 | 박지훈 | GOLD | 2016-12-20 04:06:43 |
    | 12 | 장준서 | SILVER | 2016-12-30 06:48:08 |
    | 14 | 윤순옥 | BRONZE | 2016-06-05 10:37:50 |
    | ... | ... | ... | ... |

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
    | ----------: | ---------- | ---------- | ---------- | ----------: |
    | 133 | 성미숙 | BRONZE | 2016-01-01 00:53:24 | 3652.0 |
    | 584 | 오진호 | BRONZE | 2016-01-01 03:10:41 | 3652.0 |
    | 387 | 노지민 | BRONZE | 2016-01-01 10:17:05 | 3652.0 |
    | 84 | 양영진 | BRONZE | 2016-01-03 19:49:46 | 3649.0 |
    | 707 | 김지아 | BRONZE | 2016-01-05 08:33:42 | 3648.0 |
    | 641 | 김민준 | BRONZE | 2016-01-05 21:52:07 | 3647.0 |
    | 516 | 최유진 | BRONZE | 2016-01-06 00:09:48 | 3647.0 |
    | 951 | 이미정 | BRONZE | 2016-01-06 05:24:42 | 3647.0 |
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
    | ----------: | ---------- | ---------- | ----------: |
    | 27069 | 김예준 | VIP | 25 |
    | 31228 | 고영희 | GOLD | 20 |
    | 1342 | 노광수 | SILVER | 18 |
    | 15336 | 조영식 | GOLD | 18 |
    | 1676 | 하서연 | BRONZE | 17 |
    | 17111 | 나은서 | BRONZE | 16 |
    | 29619 | 김준영 | SILVER | 16 |
    | 2268 | 강현준 | SILVER | 15 |
    | ... | ... | ... | ... |

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
    | ----------: | ---------- | ---------- | ----------: | ----------: |
    | 12486 | 민민재 | GOLD | 52 | 110159678.0 |
    | 3059 | 윤유진 | BRONZE | 5 | 73560400.0 |
    | 35583 | 고광수 | GOLD | 18 | 70057482.0 |
    | 26131 | 손준호 | VIP | 27 | 65757868.0 |
    | 41328 | 최순옥 | VIP | 12 | 64954495.0 |
    | 19776 | 박수빈 | BRONZE | 26 | 63290909.0 |
    | 13716 | 주경숙 | VIP | 18 | 62181751.0 |
    | 24264 | 권성진 | VIP | 47 | 61953072.0 |
    | ... | ... | ... | ... | ... |

---

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
    | ----------: | ---------- | ---------- |
    | 39877 | 강건우 | VIP |
    | 3645 | 강경숙 | VIP |
    | 43164 | 강경숙 | VIP |
    | 9195 | 강경자 | VIP |
    | 15102 | 강경자 | VIP |
    | 37003 | 강경자 | VIP |
    | 37522 | 강경희 | VIP |
    | 49065 | 강광수 | VIP |
    | ... | ... | ... |

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
    | ----------: | ---------- | ----------: | ---------- | ---------- |
    | 350088 | ORD-20241231-350088 | 128500.0 | 2024-12-31 23:56:35 | confirmed |
    | 350011 | ORD-20241231-350011 | 6344900.0 | 2024-12-31 23:37:34 | confirmed |
    | 350033 | ORD-20241231-350033 | 107500.0 | 2024-12-31 23:35:44 | confirmed |
    | 350197 | ORD-20241231-350197 | 122900.0 | 2024-12-31 23:33:09 | confirmed |
    | 350203 | ORD-20241231-350203 | 304800.0 | 2024-12-31 23:32:29 | confirmed |
    | 350178 | ORD-20241231-350178 | 3994300.0 | 2024-12-31 23:25:59 | confirmed |
    | 350092 | ORD-20241231-350092 | 475600.0 | 2024-12-31 22:58:39 | confirmed |
    | 350094 | ORD-20241231-350094 | 3481000.0 | 2024-12-31 22:56:33 | confirmed |
    | ... | ... | ... | ... | ... |

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
    | ----------: | ---------- | ----------: | ----------: |
    | 354 | 소니 WH-1000XM5 화이트 | 344300.0 | 9 |
    | 256 | Microsoft Bluetooth Ergonomic Mouse 화이트 | 88200.0 | 8 |
    | 70 | JBL Pebbles 2 블랙 | 96300.0 | 7 |
    | 131 | SteelSeries Arctis Nova Pro Wireless 실버 | 215500.0 | 7 |
    | 96 | JBL Flip 6 블랙 | 345400.0 | 6 |
    | 122 | SteelSeries Arctis Nova Pro Wireless 화이트 | 150300.0 | 6 |
    | 242 | 로지텍 G PRO X2 Superstrike 블랙 | 151000.0 | 6 |
    | 309 | Razer Basilisk V3 Pro 35K 블랙 | 71900.0 | 6 |
    | ... | ... | ... | ... |

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
    | ----------: | ---------- | ---------- |
    | 26258 | 고숙자 | VIP |
    | 14356 | 김광수 | VIP |
    | 19872 | 김성진 | VIP |
    | 12387 | 김영진 | VIP |
    | 16387 | 류미숙 | VIP |
    | 774 | 박성진 | VIP |
    | 17840 | 박성현 | VIP |
    | 31645 | 서영일 | VIP |
    | ... | ... | ... |

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
    | ----------: | ---------- | ---------- | ---------- | ----------: | ----------: |
    | 40080 | 김민재 | BRONZE | 2024-12-05 21:44:31 | 4 | 48780714.0 |
    | 15138 | 홍현우 | BRONZE | 2024-06-28 20:14:39 | 2 | 36524600.0 |
    | 10379 | 조상호 | BRONZE | 2024-12-23 17:38:51 | 1 | 34017000.0 |
    | 14103 | 박병철 | BRONZE | 2024-10-28 13:30:35 | 2 | 30716888.0 |
    | 28456 | 성현주 | BRONZE | 2024-08-29 17:11:52 | 4 | 26156500.0 |
    | 7439 | 이지현 | BRONZE | 2024-08-02 23:02:56 | 2 | 25655500.0 |
    | 19071 | 김정식 | BRONZE | 2024-11-20 10:22:07 | 4 | 24627600.0 |
    | 18822 | 최영수 | BRONZE | 2024-09-25 16:25:34 | 1 | 24601700.0 |
    | ... | ... | ... | ... | ... | ... |

---

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
    | ----------: | ---------- | ---------- | ----------: | ----------: |
    | 52222 | 백옥자 | VIP | 1 | 23186800.0 |
    | 35894 | 성준영 | VIP | 4 | 17874181.0 |
    | 41858 | 박상현 | VIP | 1 | 15873100.0 |
    | 50823 | 양영자 | VIP | 1 | 15597600.0 |
    | 9029 | 이명자 | VIP | 6 | 13717400.0 |
    | 43150 | 이재현 | BRONZE | 1 | 13294600.0 |
    | 6250 | 이정순 | GOLD | 6 | 13025500.0 |
    | 22631 | 박민준 | BRONZE | 2 | 12257400.0 |
    | ... | ... | ... | ... | ... |

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
    | ----------: | ---------- | ---------- | ----------: | ----------: | ----------: |
    | 45794 | 윤영희 | GOLD | 1 | 4429800.0 | 4429800.0 |
    | 40213 | 민지아 | BRONZE | 1 | 3507900.0 | 3507900.0 |
    | 48896 | 김성수 | GOLD | 1 | 3180600.0 | 3180600.0 |
    | 36900 | 남명숙 | BRONZE | 1 | 3076656.0 | 3076656.0 |
    | 34926 | 강상현 | GOLD | 1 | 2833200.0 | 2833200.0 |
    | 32669 | 박지훈 | BRONZE | 1 | 2360300.0 | 2360300.0 |
    | 37945 | 김지원 | BRONZE | 1 | 2317800.0 | 2317800.0 |
    | 37770 | 김보람 | BRONZE | 1 | 2283400.0 | 2283400.0 |
    | ... | ... | ... | ... | ... | ... |

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
