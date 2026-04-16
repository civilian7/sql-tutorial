# 데이터 품질 점검

!!! info "사용 테이블"
    `customers` — 고객 (등급, 포인트, 가입채널)  
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `orders` — 주문 (상태, 금액, 일시)  
    `order_items` — 주문 상세 (수량, 단가)  
    `payments` — 결제 (방법, 금액, 상태)  
    `shipping` — 배송 (택배사, 추적번호, 상태)  
    `reviews` — 리뷰 (평점, 내용)  
    `returns` — 반품/교환 (사유, 상태)  
    `customer_addresses` — 배송지 (주소, 기본 여부)  
    `coupons` — 쿠폰 (할인율, 유효기간)  
    `coupon_usage` — 쿠폰 사용 내역  
    `product_prices` — 가격 이력 (변경 사유)  

!!! abstract "학습 범위"
    NULL/중복/범위 점검, 참조 무결성 검증, 날짜 역전 탐지, 이상치 발견, 종합 품질 대시보드

!!! info "시작하기 전에"
    데이터는 완벽하지 않습니다. NULL, 중복, 참조 무결성 위반, 날짜 역전, 이상치 등
    **현실 데이터에서 흔히 발생하는 품질 문제**를 SQL로 탐지하는 연습입니다.
    전체 30개 테이블을 교차 검증하는 실전 쿼리를 작성합니다.

---

## 기초 (1~7): NULL, 중복, 값 범위

### 문제 1

고객 테이블에서 각 칼럼의 NULL 비율을 계산하세요. `birth_date`, `gender`, `last_login_at` 세 칼럼에 대해 NULL 건수와 비율(%)을 구하세요.

??? tip "힌트"
    `SUM(CASE WHEN 칼럼 IS NULL THEN 1 ELSE 0 END)`로 NULL 건수를, `COUNT(*)`로 전체 건수를 구해 비율을 계산합니다.

??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN birth_date IS NULL THEN 1 ELSE 0 END) AS null_birth,
        ROUND(100.0 * SUM(CASE WHEN birth_date IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_birth,
        SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) AS null_gender,
        ROUND(100.0 * SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_gender,
        SUM(CASE WHEN last_login_at IS NULL THEN 1 ELSE 0 END) AS null_login,
        ROUND(100.0 * SUM(CASE WHEN last_login_at IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_login
    FROM customers;
    ```

---

### 문제 2

동일한 이메일을 가진 고객이 있는지 확인하세요. 중복 이메일과 해당 건수를 출력하세요.

??? tip "힌트"
    `GROUP BY email`로 그룹화한 후 `HAVING COUNT(*) > 1`로 중복을 탐지합니다. `email` 칼럼에 UNIQUE 제약이 있어 이론상 0건이어야 합니다.

??? success "정답"
    ```sql
    SELECT email, COUNT(*) AS cnt
    FROM customers
    GROUP BY email
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC;
    ```

---

### 문제 3

상품 가격이 비정상적인 행을 찾으세요. 가격이 0 이하이거나, 원가보다 낮은 상품(역마진)을 출력하세요.

??? tip "힌트"
    `WHERE price <= 0 OR price < cost_price`로 조건을 걸어 비정상 가격을 탐지합니다.

??? success "정답"
    ```sql
    SELECT name, sku, price, cost_price,
           ROUND(price - cost_price, 0) AS margin
    FROM products
    WHERE price <= 0 OR price < cost_price
    ORDER BY margin ASC;
    ```

---

### 문제 4

주문 금액이 0 이하인데 취소 상태가 아닌 주문을 찾으세요.

??? tip "힌트"
    `total_amount <= 0`이면서 `status NOT IN ('cancelled', 'returned')`인 주문은 데이터 오류일 수 있습니다.

??? success "정답"
    ```sql
    SELECT order_number, status, total_amount, ordered_at
    FROM orders
    WHERE total_amount <= 0
      AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY ordered_at DESC;
    ```

---

### 문제 5

리뷰 평점이 허용 범위(1~5)를 벗어나는 행이 있는지 확인하세요.

??? tip "힌트"
    `CHECK(rating BETWEEN 1 AND 5)` 제약이 있으므로 이론상 0건이어야 합니다. `WHERE rating NOT BETWEEN 1 AND 5`로 확인합니다.

??? success "정답"
    ```sql
    SELECT id, product_id, customer_id, rating
    FROM reviews
    WHERE rating < 1 OR rating > 5;
    ```

---

### 문제 6

재고 수량이 음수인 상품을 찾으세요. 상품명, SKU, 재고, 활성 상태를 출력하세요.

??? tip "힌트"
    `CHECK(stock_qty >= 0)` 제약이 있지만, 실제 데이터에서 음수가 존재할 수 있습니다. `WHERE stock_qty < 0`으로 확인합니다.

??? success "정답"
    ```sql
    SELECT name, sku, stock_qty, is_active
    FROM products
    WHERE stock_qty < 0
    ORDER BY stock_qty ASC;
    ```

---

### 문제 7

같은 주문에 같은 상품이 중복 등록되었는지 확인하세요. 중복된 조합과 건수를 출력하세요.

??? tip "힌트"
    `GROUP BY order_id, product_id` 후 `HAVING COUNT(*) > 1`로 동일 조합이 2건 이상인 행을 탐지합니다.

??? success "정답"
    ```sql
    SELECT order_id, product_id, COUNT(*) AS cnt
    FROM order_items
    GROUP BY order_id, product_id
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC;
    ```

---

## 응용 (8~14): FK 무결성, 날짜 역전, 상태 불일치

### 문제 8

주문이 존재하지 않는 결제 레코드(고아 레코드)가 있는지 확인하세요.

??? tip "힌트"
    `payments LEFT JOIN orders`로 연결 후, `orders.id IS NULL`인 결제를 찾으면 부모 없는 고아 레코드입니다.

??? success "정답"
    ```sql
    SELECT p.id AS payment_id, p.order_id, p.method, p.amount
    FROM payments AS p
    LEFT JOIN orders AS o ON p.order_id = o.id
    WHERE o.id IS NULL;
    ```

---

### 문제 9

고객 가입일보다 주문일이 빠른 주문이 있는지 확인하세요. 시간 역전은 데이터 오류의 전형적 사례입니다.

??? tip "힌트"
    `orders JOIN customers`로 연결 후, `ordered_at < created_at`인 행을 찾습니다.

??? success "정답"
    ```sql
    SELECT
        o.order_number,
        o.ordered_at,
        c.name,
        c.created_at AS signup_date,
        ROUND(JULIANDAY(c.created_at) - JULIANDAY(o.ordered_at), 1) AS days_diff
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.ordered_at < c.created_at
    ORDER BY days_diff DESC;
    ```

---

### 문제 10

배송 완료일(`delivered_at`)이 출고일(`shipped_at`)보다 빠른 비정상 레코드를 찾으세요.

??? tip "힌트"
    두 날짜가 모두 NOT NULL인 행 중에서 `delivered_at < shipped_at`인 경우를 찾습니다.

??? success "정답"
    ```sql
    SELECT
        sh.id,
        o.order_number,
        sh.shipped_at,
        sh.delivered_at,
        ROUND(JULIANDAY(sh.delivered_at) - JULIANDAY(sh.shipped_at), 1) AS days_diff
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE sh.shipped_at IS NOT NULL
      AND sh.delivered_at IS NOT NULL
      AND sh.delivered_at < sh.shipped_at;
    ```

---

### 문제 11

배송 완료(`delivered`)인데 주문 상태가 배송 완료 이후 단계로 진행되지 않은 불일치를 찾으세요.

??? tip "힌트"
    배송이 `delivered`이면 주문 상태가 `delivered`, `confirmed`, `return_requested`, `returned` 중 하나여야 합니다. 그 외의 상태는 불일치입니다.

??? success "정답"
    ```sql
    SELECT
        o.order_number,
        o.status AS order_status,
        sh.status AS ship_status,
        sh.delivered_at
    FROM orders AS o
    INNER JOIN shipping AS sh ON o.id = sh.order_id
    WHERE sh.status = 'delivered'
      AND o.status NOT IN ('delivered', 'confirmed', 'return_requested', 'returned');
    ```

---

### 문제 12

취소된 주문인데 배송 완료 기록이 있는 모순 데이터를 찾으세요.

??? tip "힌트"
    `orders.status = 'cancelled'`이면서 `shipping.status = 'delivered'`인 주문은 논리적 모순입니다.

??? success "정답"
    ```sql
    SELECT
        o.order_number,
        o.status AS order_status,
        o.cancelled_at,
        sh.status AS ship_status,
        sh.delivered_at
    FROM orders AS o
    INNER JOIN shipping AS sh ON o.id = sh.order_id
    WHERE o.status = 'cancelled'
      AND sh.status = 'delivered';
    ```

---

### 문제 13

단종된 상품(`discontinued_at IS NOT NULL`)이 단종 이후에 주문된 적이 있는지 확인하세요.

??? tip "힌트"
    단종 상품의 `discontinued_at`과 주문의 `ordered_at`을 비교합니다. 단종일 이후에 주문이 있으면 비정상입니다.

??? success "정답"
    ```sql
    SELECT
        p.name,
        p.discontinued_at,
        o.order_number,
        o.ordered_at
    FROM products AS p
    INNER JOIN order_items AS oi ON p.id = oi.product_id
    INNER JOIN orders AS o ON oi.order_id = o.id
    WHERE p.discontinued_at IS NOT NULL
      AND o.ordered_at > p.discontinued_at
    ORDER BY o.ordered_at DESC
    LIMIT 20;
    ```

---

### 문제 14

상품의 현재 가격(`products.price`)과 가격 이력 테이블의 현재 유효 가격(`product_prices`에서 `ended_at IS NULL`)이 불일치하는 상품을 찾으세요.

??? tip "힌트"
    `product_prices`에서 `ended_at IS NULL`인 행이 현재 적용 중인 가격입니다. 이 값과 `products.price`가 다르면 동기화 오류입니다.

??? success "정답"
    ```sql
    SELECT
        p.name,
        p.price AS current_price,
        pp.price AS history_price,
        ROUND(p.price - pp.price, 0) AS diff
    FROM products AS p
    INNER JOIN product_prices AS pp ON p.id = pp.product_id
    WHERE pp.ended_at IS NULL
      AND p.price <> pp.price
    ORDER BY ABS(p.price - pp.price) DESC;
    ```

---

## 실전 (15~20): 종합 품질 보고서

### 문제 15

결제 금액과 주문 금액이 일치하지 않는 주문을 찾으세요. 완료된 결제(`status = 'completed'`)의 금액 합계와 `orders.total_amount`를 비교하세요.

??? tip "힌트"
    주문별 결제 합계를 서브쿼리로 구한 뒤, `orders.total_amount`와 비교합니다. 소수점 차이가 있을 수 있으므로 `ABS(차이) > 1` 정도로 필터링합니다.

??? success "정답"
    ```sql
    SELECT
        o.order_number,
        o.total_amount AS order_amount,
        pay_sum.paid_total,
        ROUND(o.total_amount - pay_sum.paid_total, 2) AS diff
    FROM orders AS o
    INNER JOIN (
        SELECT order_id, SUM(amount) AS paid_total
        FROM payments
        WHERE status = 'completed'
        GROUP BY order_id
    ) AS pay_sum ON o.id = pay_sum.order_id
    WHERE ABS(o.total_amount - pay_sum.paid_total) > 1
    ORDER BY ABS(diff) DESC
    LIMIT 20;
    ```

---

### 문제 16

고객별 기본 배송지(`is_default = 1`)가 정확히 1개인지 확인하세요. 기본 배송지가 0개이거나 2개 이상인 고객을 찾으세요.

??? tip "힌트"
    `customer_addresses`에서 `is_default = 1`인 행을 고객별로 세어, 1이 아닌 고객을 찾습니다. 주소가 아예 없는 고객은 LEFT JOIN으로 찾습니다.

??? success "정답"
    ```sql
    -- 기본 배송지가 2개 이상인 고객
    SELECT
        c.name,
        c.email,
        COUNT(*) AS default_count
    FROM customers AS c
    INNER JOIN customer_addresses AS ca ON c.id = ca.customer_id
    WHERE ca.is_default = 1
    GROUP BY c.id, c.name, c.email
    HAVING COUNT(*) > 1;
    ```

---

### 문제 17

쿠폰 사용 테이블(`coupon_usage`)에서 `per_user_limit`을 초과하여 사용한 건이 있는지 확인하세요. 고객별/쿠폰별 사용 횟수가 쿠폰의 `per_user_limit`을 넘는 경우를 찾으세요.

??? tip "힌트"
    `coupon_usage`를 `coupon_id, customer_id`로 그룹화하여 사용 횟수를 센 뒤, `coupons.per_user_limit`과 비교합니다.

??? success "정답"
    ```sql
    SELECT
        cp.code AS coupon_code,
        cp.name AS coupon_name,
        c.name AS customer_name,
        COUNT(*) AS usage_count,
        cp.per_user_limit
    FROM coupon_usage AS cu
    INNER JOIN coupons AS cp ON cu.coupon_id = cp.id
    INNER JOIN customers AS c ON cu.customer_id = c.id
    GROUP BY cu.coupon_id, cu.customer_id, cp.code, cp.name, c.name, cp.per_user_limit
    HAVING COUNT(*) > cp.per_user_limit
    ORDER BY usage_count DESC;
    ```

---

### 문제 18

반품 테이블(`returns`)에서 환불 금액 합계가 원래 주문 금액을 초과하는 주문을 찾으세요.

??? tip "힌트"
    주문별 환불 금액 합계를 구한 뒤 `orders.total_amount`와 비교합니다.

??? success "정답"
    ```sql
    SELECT
        o.order_number,
        o.total_amount AS order_amount,
        SUM(ret.refund_amount) AS total_refund,
        ROUND(SUM(ret.refund_amount) - o.total_amount, 2) AS over_refund
    FROM returns AS ret
    INNER JOIN orders AS o ON ret.order_id = o.id
    GROUP BY ret.order_id, o.order_number, o.total_amount
    HAVING SUM(ret.refund_amount) > o.total_amount
    ORDER BY over_refund DESC;
    ```

---

### 문제 19

데이터 완전성 점수를 테이블별로 계산하세요. 각 테이블의 (1) 총 행수, (2) NULL 가능 칼럼의 평균 충족률(non-NULL 비율)을 구하세요. `customers`, `products`, `orders` 세 테이블을 UNION ALL로 합쳐 보고서를 만드세요.

??? tip "힌트"
    각 테이블에서 NULL 가능 칼럼의 non-NULL 비율을 `1 - (NULL 수 / 전체)`로 계산하고, 여러 칼럼의 평균을 구합니다.

??? success "정답"
    ```sql
    SELECT '고객' AS table_name,
           COUNT(*) AS total_rows,
           ROUND(100.0 * (
               (1.0 - 1.0 * SUM(CASE WHEN birth_date IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN last_login_at IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN acquisition_channel IS NULL THEN 1 ELSE 0 END) / COUNT(*))
           ) / 4.0, 1) AS completeness_pct
    FROM customers

    UNION ALL

    SELECT '상품' AS table_name,
           COUNT(*) AS total_rows,
           ROUND(100.0 * (
               (1.0 - 1.0 * SUM(CASE WHEN description IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN specs IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN weight_grams IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN model_number IS NULL THEN 1 ELSE 0 END) / COUNT(*))
           ) / 4.0, 1) AS completeness_pct
    FROM products

    UNION ALL

    SELECT '주문' AS table_name,
           COUNT(*) AS total_rows,
           ROUND(100.0 * (
               (1.0 - 1.0 * SUM(CASE WHEN notes IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN completed_at IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN cancelled_at IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN staff_id IS NULL THEN 1 ELSE 0 END) / COUNT(*))
           ) / 4.0, 1) AS completeness_pct
    FROM orders;
    ```

---

### 문제 20

한 쿼리로 주요 데이터 품질 지표를 요약하세요. 다음 항목을 스칼라 서브쿼리로 한 행에 출력하세요.

- 가입일보다 빠른 주문 수
- 고아 결제 레코드 수
- 배송일 역전 건수
- 주문 상세 중복 건수
- 음수 재고 상품 수
- 취소인데 배송 완료된 주문 수

??? tip "힌트"
    각 품질 점검을 `(SELECT COUNT(*) FROM ... WHERE 조건)` 스칼라 서브쿼리로 만들어 하나의 SELECT에 나열합니다.

??? success "정답"
    ```sql
    SELECT
        (SELECT COUNT(*)
         FROM orders AS o
         INNER JOIN customers AS c ON o.customer_id = c.id
         WHERE o.ordered_at < c.created_at
        ) AS orders_before_signup,

        (SELECT COUNT(*)
         FROM payments AS p
         LEFT JOIN orders AS o ON p.order_id = o.id
         WHERE o.id IS NULL
        ) AS orphan_payments,

        (SELECT COUNT(*)
         FROM shipping
         WHERE shipped_at IS NOT NULL
           AND delivered_at IS NOT NULL
           AND delivered_at < shipped_at
        ) AS date_inversions,

        (SELECT COUNT(*)
         FROM (
             SELECT order_id, product_id
             FROM order_items
             GROUP BY order_id, product_id
             HAVING COUNT(*) > 1
         )
        ) AS duplicate_items,

        (SELECT COUNT(*)
         FROM products
         WHERE stock_qty < 0
        ) AS negative_stock,

        (SELECT COUNT(*)
         FROM orders AS o
         INNER JOIN shipping AS sh ON o.id = sh.order_id
         WHERE o.status = 'cancelled'
           AND sh.status = 'delivered'
        ) AS cancelled_but_delivered;
    ```
