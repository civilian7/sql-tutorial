# 중급 종합 문제

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `orders` — 주문<br>
    `customers` — 고객<br>
    `order_items` — 주문 상세<br>
    `products` — 상품<br>
    `categories` — 카테고리<br>
    `payments` — 결제<br>
    `reviews` — 리뷰<br>
    `shipping` — 배송<br>
    `complaints` — 불만 접수<br>
    `wishlists` — 위시리스트

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    중급 전체: `JOIN`<br>
    서브쿼리<br>
    날짜 함수<br>
    문자열 함수<br>
    `CASE`<br>
    `UNION`<br>
    `GROUP BY`/`HAVING`<br>
    집계 함수

</div>

!!! info "시작하기 전에"
    이 연습은 **중급 과정(8~17강)에서 배운 모든 개념**을 조합합니다.
    JOIN, 서브쿼리, 날짜 함수, 문자열 함수, CASE, UNION, GROUP BY/HAVING, 집계 함수 등 여러 개념을 함께 사용하는 실전 쿼리를 연습합니다.

---


## 기초 (1~8): 2~3개 개념 조합


### 문제 1

**JOIN + GROUP BY:** 카테고리별 판매 중인 상품 수와 평균 가격을 조회하세요. 상품 수가 많은 순으로 10개만.


??? tip "힌트"
    `products JOIN categories`로 연결 후 `GROUP BY`로 카테고리별 집계. `WHERE is_active = 1`로 판매 중만 필터링.


??? success "정답"
    ```sql
    SELECT
        cat.name AS category,
        COUNT(*) AS product_count,
        ROUND(AVG(p.price)) AS avg_price
    FROM products p
    INNER JOIN categories cat ON p.category_id = cat.id
    WHERE p.is_active = 1
    GROUP BY cat.id, cat.name
    ORDER BY product_count DESC
    LIMIT 10;
    ```

    | category     | product_count | avg_price |
    |--------------|---------------|-----------|
    | ...          | ...           | ...       |


---


### 문제 2

**JOIN + CASE:** 각 주문의 주문번호, 고객명, 결제 방법을 조회하세요. 결제 방법은 한글로 표시합니다 (card→카드, bank_transfer→계좌이체, kakao_pay→카카오페이, 그 외→기타). 최근 주문 10건만.


??? tip "힌트"
    `orders JOIN customers JOIN payments`로 3개 테이블 연결. `CASE payments.method WHEN ... THEN ...`으로 한글 변환.


??? success "정답"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer_name,
        CASE pay.method
            WHEN 'card' THEN '카드'
            WHEN 'bank_transfer' THEN '계좌이체'
            WHEN 'kakao_pay' THEN '카카오페이'
            WHEN 'naver_pay' THEN '네이버페이'
            WHEN 'virtual_account' THEN '가상계좌'
            WHEN 'point' THEN '포인트'
            ELSE '기타'
        END AS payment_method_kr,
        o.total_amount
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    INNER JOIN payments pay ON o.id = pay.order_id
    ORDER BY o.ordered_at DESC
    LIMIT 10;
    ```

    | order_number       | customer_name | payment_method_kr | total_amount |
    |--------------------|---------------|-------------------|--------------|
    | ORD-2025...-...    | ...           | 카드              | ...          |


---


### 문제 3

**서브쿼리 + 날짜 함수:** 2024년에 가장 많이 주문한 고객 TOP 5의 이름, 주문 건수, 총 결제금액을 조회하세요.


??? tip "힌트"
    `orders`에서 `ordered_at LIKE '2024%'`로 필터링 후 `GROUP BY customer_id`로 집계. `customers`와 JOIN하여 이름을 가져옵니다.


??? success "정답"
    ```sql
    SELECT
        c.name,
        sub.order_count,
        sub.total_spent
    FROM (
        SELECT
            customer_id,
            COUNT(*) AS order_count,
            SUM(total_amount) AS total_spent
        FROM orders
        WHERE ordered_at LIKE '2024%'
        GROUP BY customer_id
        ORDER BY order_count DESC
        LIMIT 5
    ) sub
    INNER JOIN customers c ON sub.customer_id = c.id
    ORDER BY sub.order_count DESC;
    ```

    | name   | order_count | total_spent |
    |--------|-------------|-------------|
    | ...    | ...         | ...         |


---


### 문제 4

**문자열 함수 + GROUP BY:** 고객 이메일 도메인별 고객 수를 집계하세요. 이메일에서 `@` 뒤의 도메인을 추출합니다.


??? tip "힌트"
    `SUBSTR(email, INSTR(email, '@') + 1)`로 도메인을 추출합니다. 이것을 `GROUP BY`로 집계하세요.


??? success "정답"
    ```sql
    SELECT
        SUBSTR(email, INSTR(email, '@') + 1) AS domain,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY domain
    ORDER BY customer_count DESC;
    ```

    | domain       | customer_count |
    |--------------|----------------|
    | testmail.kr  | ...            |


---


### 문제 5

**JOIN + HAVING:** 리뷰를 5건 이상 작성한 고객의 이름과 평균 평점을 조회하세요.


??? tip "힌트"
    `reviews JOIN customers`로 연결 후 `GROUP BY customer_id` + `HAVING COUNT(*) >= 5`로 5건 이상만 필터링.


??? success "정답"
    ```sql
    SELECT
        c.name,
        COUNT(*) AS review_count,
        ROUND(AVG(r.rating), 1) AS avg_rating
    FROM reviews r
    INNER JOIN customers c ON r.customer_id = c.id
    GROUP BY r.customer_id, c.name
    HAVING COUNT(*) >= 5
    ORDER BY review_count DESC
    LIMIT 10;
    ```

    | name | review_count | avg_rating |
    |------|--------------|------------|
    | ...  | ...          | ...        |


---


### 문제 6

**UNION + CASE:** 최근 1년간 신규 고객 수와 신규 상품 수를 하나의 결과로 합쳐서 보세요.


??? tip "힌트"
    `SELECT '고객' AS type, COUNT(*)... FROM customers WHERE ...` UNION ALL `SELECT '상품'...FROM products WHERE ...`


??? success "정답"
    ```sql
    SELECT '신규 고객' AS category,
           COUNT(*) AS count_2024
    FROM customers
    WHERE created_at LIKE '2024%'

    UNION ALL

    SELECT '신규 상품' AS category,
           COUNT(*) AS count_2024
    FROM products
    WHERE created_at LIKE '2024%';
    ```

    | category  | count_2024 |
    |-----------|------------|
    | 신규 고객 | ...        |
    | 신규 상품 | ...        |


---


### 문제 7

**날짜 함수 + JOIN:** 주문 후 배송 완료까지 걸린 평균 일수를 택배사별로 조회하세요. 배송 완료된 건만 대상입니다.


??? tip "힌트"
    `shipping JOIN orders`로 연결. `julianday(delivered_at) - julianday(ordered_at)`로 일수 계산. `WHERE shipping.status = 'delivered'` 필터링.


??? success "정답"
    ```sql
    SELECT
        s.carrier,
        COUNT(*) AS delivered_count,
        ROUND(AVG(julianday(s.delivered_at) - julianday(o.ordered_at)), 1) AS avg_days
    FROM shipping s
    INNER JOIN orders o ON s.order_id = o.id
    WHERE s.status = 'delivered'
      AND s.delivered_at IS NOT NULL
    GROUP BY s.carrier
    ORDER BY avg_days;
    ```

    | carrier      | delivered_count | avg_days |
    |--------------|-----------------|----------|
    | ...          | ...             | ...      |


---


### 문제 8

**서브쿼리 + CASE:** 각 상품의 이름, 가격, 그리고 해당 상품의 카테고리 평균 가격 대비 비싼지/싼지를 표시하세요. 상위 15개만.


??? tip "힌트"
    서브쿼리로 카테고리별 평균 가격을 구한 뒤 JOIN. `CASE WHEN price > avg_price THEN '평균 이상'...`으로 비교.


??? success "정답"
    ```sql
    SELECT
        p.name,
        p.price,
        cat_avg.avg_price,
        CASE
            WHEN p.price > cat_avg.avg_price * 1.2 THEN '고가'
            WHEN p.price < cat_avg.avg_price * 0.8 THEN '저가'
            ELSE '평균 수준'
        END AS price_level
    FROM products p
    INNER JOIN (
        SELECT category_id, ROUND(AVG(price)) AS avg_price
        FROM products
        WHERE is_active = 1
        GROUP BY category_id
    ) cat_avg ON p.category_id = cat_avg.category_id
    WHERE p.is_active = 1
    ORDER BY p.price DESC
    LIMIT 15;
    ```

    | name | price   | avg_price | price_level |
    |------|---------|-----------|-------------|
    | ...  | ...     | ...       | 고가        |


---


## 응용 (9~16): 3~4개 개념 조합, 비즈니스 분석


### 문제 9

**JOIN + GROUP BY + HAVING + 서브쿼리:** 전체 평균보다 높은 매출을 올린 브랜드의 이름, 총 매출, 주문 건수를 조회하세요.


??? tip "힌트"
    `order_items JOIN products`로 브랜드별 매출 집계 → `HAVING SUM(subtotal) > (SELECT AVG(...))`. 전체 평균은 브랜드별 매출의 평균입니다.


??? success "정답"
    ```sql
    SELECT
        p.brand,
        SUM(oi.subtotal) AS total_revenue,
        COUNT(DISTINCT oi.order_id) AS order_count
    FROM order_items oi
    INNER JOIN products p ON oi.product_id = p.id
    GROUP BY p.brand
    HAVING SUM(oi.subtotal) > (
        SELECT AVG(brand_revenue)
        FROM (
            SELECT SUM(oi2.subtotal) AS brand_revenue
            FROM order_items oi2
            INNER JOIN products p2 ON oi2.product_id = p2.id
            GROUP BY p2.brand
        )
    )
    ORDER BY total_revenue DESC
    LIMIT 10;
    ```

    | brand  | total_revenue | order_count |
    |--------|---------------|-------------|
    | ...    | ...           | ...         |


---


### 문제 10

**JOIN + 날짜 함수 + CASE + GROUP BY:** 2024년 월별로 주문 상태 분포를 조회하세요. 각 월의 완료(confirmed), 취소(cancelled), 기타 건수를 표시합니다.


??? tip "힌트"
    `SUBSTR(ordered_at, 1, 7)`로 연-월 추출. `SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END)`로 조건부 집계.


??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
        SUM(CASE WHEN status NOT IN ('confirmed', 'cancelled') THEN 1 ELSE 0 END) AS in_progress,
        ROUND(100.0 * SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1) AS cancel_rate
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```

    | month   | total_orders | confirmed | cancelled | in_progress | cancel_rate |
    |---------|--------------|-----------|-----------|-------------|-------------|
    | 2024-01 | ...          | ...       | ...       | ...         | ...         |
    | 2024-02 | ...          | ...       | ...       | ...         | ...         |
    | ...     | ...          | ...       | ...       | ...         | ...         |


---


### 문제 11

**다중 JOIN + 서브쿼리 + 문자열 함수:** VIP 고객이 구매한 상품 중, 리뷰 평점이 4점 이상인 상품의 이름, 브랜드, 평균 평점, VIP 구매 횟수를 조회하세요.


??? tip "힌트"
    `customers(grade='VIP') JOIN orders JOIN order_items JOIN products`로 VIP 구매 상품을 파악. 서브쿼리로 리뷰 평균 4점 이상 필터링.


??? success "정답"
    ```sql
    SELECT
        p.name,
        p.brand,
        review_avg.avg_rating,
        COUNT(*) AS vip_purchase_count
    FROM order_items oi
    INNER JOIN orders o ON oi.order_id = o.id
    INNER JOIN customers c ON o.customer_id = c.id
    INNER JOIN products p ON oi.product_id = p.id
    INNER JOIN (
        SELECT product_id, ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews
        GROUP BY product_id
        HAVING AVG(rating) >= 4.0
    ) review_avg ON p.id = review_avg.product_id
    WHERE c.grade = 'VIP'
    GROUP BY p.id, p.name, p.brand, review_avg.avg_rating
    ORDER BY vip_purchase_count DESC
    LIMIT 10;
    ```

    | name | brand | avg_rating | vip_purchase_count |
    |------|-------|------------|--------------------|
    | ...  | ...   | ...        | ...                |


---


### 문제 12

**LEFT JOIN + COALESCE + GROUP BY:** 모든 상품의 이름, 가격, 총 판매 수량, 총 리뷰 수를 조회하세요. 판매/리뷰가 없는 상품도 0으로 표시합니다.


??? tip "힌트"
    카디널리티 폭발 방지를 위해 판매 수량과 리뷰 수를 각각 서브쿼리로 집계한 뒤 LEFT JOIN합니다. `COALESCE(값, 0)`으로 NULL을 0으로 변환.


??? success "정답"
    ```sql
    SELECT
        p.name,
        p.price,
        COALESCE(sales.total_qty, 0) AS total_sold,
        COALESCE(rev.review_count, 0) AS review_count
    FROM products p
    LEFT JOIN (
        SELECT product_id, SUM(quantity) AS total_qty
        FROM order_items
        GROUP BY product_id
    ) sales ON p.id = sales.product_id
    LEFT JOIN (
        SELECT product_id, COUNT(*) AS review_count
        FROM reviews
        GROUP BY product_id
    ) rev ON p.id = rev.product_id
    WHERE p.is_active = 1
    ORDER BY total_sold DESC
    LIMIT 15;
    ```

    | name | price  | total_sold | review_count |
    |------|--------|------------|--------------|
    | ...  | ...    | ...        | ...          |


---


### 문제 13

**UNION + JOIN + GROUP BY:** 고객별 "활동 점수"를 계산하세요. 주문 1건=10점, 리뷰 1건=5점, 문의 1건=3점. 상위 10명을 조회합니다.


??? tip "힌트"
    각 활동별 점수를 UNION ALL로 합친 뒤, 외부에서 SUM으로 총점을 구합니다. `customers`와 JOIN하여 이름을 표시.


??? success "정답"
    ```sql
    SELECT
        c.name,
        c.grade,
        SUM(activity.score) AS total_score,
        SUM(CASE WHEN activity.type = '주문' THEN 1 ELSE 0 END) AS orders,
        SUM(CASE WHEN activity.type = '리뷰' THEN 1 ELSE 0 END) AS reviews,
        SUM(CASE WHEN activity.type = '문의' THEN 1 ELSE 0 END) AS complaints
    FROM (
        SELECT customer_id, '주문' AS type, 10 AS score FROM orders
        UNION ALL
        SELECT customer_id, '리뷰' AS type, 5 AS score FROM reviews
        UNION ALL
        SELECT customer_id, '문의' AS type, 3 AS score FROM complaints
    ) activity
    INNER JOIN customers c ON activity.customer_id = c.id
    GROUP BY activity.customer_id, c.name, c.grade
    ORDER BY total_score DESC
    LIMIT 10;
    ```

    | name | grade | total_score | orders | reviews | complaints |
    |------|-------|-------------|--------|---------|------------|
    | ...  | VIP   | ...         | ...    | ...     | ...        |


---


### 문제 14

**서브쿼리 + JOIN + 날짜 함수:** 가입 후 30일 이내에 첫 주문을 한 고객과, 30일이 지나서야 첫 주문을 한 고객의 수를 비교하세요.


??? tip "힌트"
    `MIN(ordered_at)`으로 고객별 첫 주문일을 구한 서브쿼리를 만들고, `julianday(first_order) - julianday(created_at)`으로 가입~첫 주문 간 일수를 계산합니다.


??? success "정답"
    ```sql
    SELECT
        CASE
            WHEN days_to_first_order <= 30 THEN '30일 이내'
            WHEN days_to_first_order <= 90 THEN '31~90일'
            ELSE '90일 초과'
        END AS segment,
        COUNT(*) AS customer_count,
        ROUND(AVG(days_to_first_order), 1) AS avg_days
    FROM (
        SELECT
            c.id,
            ROUND(julianday(MIN(o.ordered_at)) - julianday(c.created_at)) AS days_to_first_order
        FROM customers c
        INNER JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.created_at
    )
    GROUP BY segment
    ORDER BY MIN(days_to_first_order);
    ```

    | segment     | customer_count | avg_days |
    |-------------|----------------|----------|
    | 30일 이내   | ...            | ...      |
    | 31~90일     | ...            | ...      |
    | 90일 초과   | ...            | ...      |


---


### 문제 15

**다중 JOIN + CASE + GROUP BY:** 결제 방법별, 카드 발급사별 매출 현황을 조회하세요. 카드 결제가 아닌 경우 발급사는 '해당없음'으로 표시합니다.


??? tip "힌트"
    `payments JOIN orders`. `COALESCE(card_issuer, '해당없음')`으로 NULL 처리. `GROUP BY method, card_issuer`.


??? success "정답"
    ```sql
    SELECT
        CASE pay.method
            WHEN 'card' THEN '카드'
            WHEN 'bank_transfer' THEN '계좌이체'
            WHEN 'kakao_pay' THEN '카카오페이'
            WHEN 'naver_pay' THEN '네이버페이'
            ELSE pay.method
        END AS method_kr,
        COALESCE(pay.card_issuer, '해당없음') AS issuer,
        COUNT(*) AS payment_count,
        SUM(pay.amount) AS total_amount,
        ROUND(AVG(pay.amount)) AS avg_amount
    FROM payments pay
    WHERE pay.status = 'completed'
    GROUP BY pay.method, pay.card_issuer
    ORDER BY total_amount DESC
    LIMIT 15;
    ```

    | method_kr | issuer   | payment_count | total_amount | avg_amount |
    |-----------|----------|---------------|--------------|------------|
    | 카드      | 삼성카드 | ...           | ...          | ...        |
    | 카드      | 신한카드 | ...           | ...          | ...        |
    | ...       | ...      | ...           | ...          | ...        |


---


### 문제 16

**서브쿼리 + CASE + 날짜 함수:** 고객을 최근 주문일 기준으로 RFM의 R(Recency) 등급으로 분류하세요.

- 30일 이내 주문: Active
- 31~90일: Warm
- 91~180일: Cold
- 181일 이상 또는 주문 없음: Dormant


??? tip "힌트"
    `LEFT JOIN`으로 주문 없는 고객 포함. `MAX(ordered_at)`으로 최근 주문일 구한 뒤, `julianday('now') - julianday(last_order)`로 경과일 계산.


??? success "정답"
    ```sql
    SELECT
        recency_group,
        COUNT(*) AS customer_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM (
        SELECT
            c.id,
            CASE
                WHEN MAX(o.ordered_at) IS NULL THEN 'Dormant'
                WHEN julianday('now') - julianday(MAX(o.ordered_at)) <= 30 THEN 'Active'
                WHEN julianday('now') - julianday(MAX(o.ordered_at)) <= 90 THEN 'Warm'
                WHEN julianday('now') - julianday(MAX(o.ordered_at)) <= 180 THEN 'Cold'
                ELSE 'Dormant'
            END AS recency_group
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id
    )
    GROUP BY recency_group
    ORDER BY
        CASE recency_group
            WHEN 'Active' THEN 1
            WHEN 'Warm' THEN 2
            WHEN 'Cold' THEN 3
            ELSE 4
        END;
    ```

    | recency_group | customer_count | pct  |
    |---------------|----------------|------|
    | Active        | ...            | ...  |
    | Warm          | ...            | ...  |
    | Cold          | ...            | ...  |
    | Dormant       | ...            | ...  |


---


## 실전 (17~25): 복합 실무 시나리오


### 문제 17

**월간 매출 리포트:** 2024년 월별 매출, 주문 건수, 고유 고객 수, 건당 평균 결제금액, 전월 대비 매출 증감율을 조회하세요.


??? tip "힌트"
    `LAG()` 윈도우 함수로 전월 매출을 가져와 증감율을 계산합니다. SQLite 3.25+ 에서 지원됩니다.


??? success "정답"
    ```sql
    SELECT
        month,
        total_revenue,
        order_count,
        unique_customers,
        ROUND(total_revenue * 1.0 / order_count) AS avg_order_value,
        CASE
            WHEN prev_revenue IS NULL THEN '-'
            ELSE ROUND((total_revenue - prev_revenue) * 100.0 / prev_revenue, 1) || '%'
        END AS growth_rate
    FROM (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS month,
            SUM(total_amount) AS total_revenue,
            COUNT(*) AS order_count,
            COUNT(DISTINCT customer_id) AS unique_customers,
            LAG(SUM(total_amount)) OVER (ORDER BY SUBSTR(ordered_at, 1, 7)) AS prev_revenue
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    ORDER BY month;
    ```

    | month   | total_revenue | order_count | unique_customers | avg_order_value | growth_rate |
    |---------|---------------|-------------|------------------|-----------------|-------------|
    | 2024-01 | ...           | ...         | ...              | ...             | -           |
    | 2024-02 | ...           | ...         | ...              | ...             | ...%        |
    | ...     | ...           | ...         | ...              | ...             | ...%        |


---


### 문제 18

**고객 세그먼트 분석:** 고객 등급별로 평균 주문 금액, 평균 리뷰 평점, 반품율(반품 건수/주문 건수)을 조회하세요.


??? tip "힌트"
    각 지표를 서브쿼리로 따로 집계한 뒤 `customers`의 `grade`로 GROUP BY. 반품 건수는 `returns` 테이블에서 카운트합니다.


??? success "정답"
    ```sql
    SELECT
        c.grade,
        COUNT(DISTINCT c.id) AS customer_count,
        ROUND(AVG(order_stats.avg_amount)) AS avg_order_amount,
        ROUND(AVG(review_stats.avg_rating), 2) AS avg_rating,
        ROUND(100.0 * SUM(COALESCE(return_stats.return_count, 0))
            / NULLIF(SUM(COALESCE(order_stats.order_count, 0)), 0), 2) AS return_rate_pct
    FROM customers c
    LEFT JOIN (
        SELECT customer_id,
               COUNT(*) AS order_count,
               AVG(total_amount) AS avg_amount
        FROM orders
        GROUP BY customer_id
    ) order_stats ON c.id = order_stats.customer_id
    LEFT JOIN (
        SELECT customer_id, AVG(rating) AS avg_rating
        FROM reviews
        GROUP BY customer_id
    ) review_stats ON c.id = review_stats.customer_id
    LEFT JOIN (
        SELECT customer_id, COUNT(*) AS return_count
        FROM returns
        GROUP BY customer_id
    ) return_stats ON c.id = return_stats.customer_id
    GROUP BY c.grade
    ORDER BY
        CASE c.grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            WHEN 'BRONZE' THEN 4
        END;
    ```

    | grade  | customer_count | avg_order_amount | avg_rating | return_rate_pct |
    |--------|----------------|------------------|------------|-----------------|
    | VIP    | ...            | ...              | ...        | ...             |
    | GOLD   | ...            | ...              | ...        | ...             |
    | SILVER | ...            | ...              | ...        | ...             |
    | BRONZE | ...            | ...              | ...        | ...             |


---


### 문제 19

**재고 위험 상품 점검:** 현재 재고가 최근 30일 판매량보다 적은 상품을 찾으세요. 상품명, 현재 재고, 30일 판매량, 예상 소진일을 표시합니다.


??? tip "힌트"
    최근 30일 판매량은 `order_items JOIN orders`에서 `ordered_at >= date('now', '-30 days')`로 계산. `stock_qty / (30일 판매량 / 30)`으로 예상 소진일을 구합니다.


??? success "정답"
    ```sql
    SELECT
        p.name,
        p.stock_qty AS current_stock,
        COALESCE(sales.qty_30d, 0) AS sold_30d,
        CASE
            WHEN COALESCE(sales.qty_30d, 0) = 0 THEN '판매 없음'
            ELSE CAST(ROUND(p.stock_qty * 30.0 / sales.qty_30d) AS INTEGER) || '일'
        END AS est_days_left
    FROM products p
    LEFT JOIN (
        SELECT oi.product_id, SUM(oi.quantity) AS qty_30d
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        WHERE o.ordered_at >= date('now', '-30 days')
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    ) sales ON p.id = sales.product_id
    WHERE p.is_active = 1
      AND p.stock_qty < COALESCE(sales.qty_30d, 0)
    ORDER BY p.stock_qty ASC
    LIMIT 15;
    ```

    | name | current_stock | sold_30d | est_days_left |
    |------|---------------|----------|---------------|
    | ...  | ...           | ...      | ...일         |


---


### 문제 20

**카테고리 계층 분석:** 대분류(depth=0)별로 소속 상품 수, 총 매출, 평균 리뷰 평점을 조회하세요. 중분류/소분류 상품도 대분류에 합산합니다.


??? tip "힌트"
    카테고리의 `parent_id`를 따라 올라가야 합니다. `categories`를 자기 자신과 JOIN하여 대분류를 찾으세요. depth=0이 대분류, depth=1이 중분류, depth=2가 소분류입니다.


??? success "정답"
    ```sql
    SELECT
        top_cat.name AS top_category,
        COUNT(DISTINCT p.id) AS product_count,
        COALESCE(SUM(sales.revenue), 0) AS total_revenue,
        ROUND(AVG(rev.avg_rating), 1) AS avg_rating
    FROM categories top_cat
    LEFT JOIN categories mid_cat ON mid_cat.parent_id = top_cat.id
    LEFT JOIN categories sub_cat ON sub_cat.parent_id = mid_cat.id
    LEFT JOIN products p ON p.category_id IN (top_cat.id, mid_cat.id, sub_cat.id)
    LEFT JOIN (
        SELECT product_id, SUM(subtotal) AS revenue
        FROM order_items
        GROUP BY product_id
    ) sales ON p.id = sales.product_id
    LEFT JOIN (
        SELECT product_id, AVG(rating) AS avg_rating
        FROM reviews
        GROUP BY product_id
    ) rev ON p.id = rev.product_id
    WHERE top_cat.depth = 0
    GROUP BY top_cat.id, top_cat.name
    ORDER BY total_revenue DESC;
    ```

    | top_category | product_count | total_revenue | avg_rating |
    |--------------|---------------|---------------|------------|
    | ...          | ...           | ...           | ...        |


---


### 문제 21

**공급업체 성과 비교:** 공급업체별 공급 상품 수, 총 매출, 평균 리뷰 평점, 반품률을 조회하세요. 매출 상위 10개 업체만.


??? tip "힌트"
    `suppliers JOIN products JOIN order_items`로 매출 집계. 반품은 `returns JOIN orders JOIN order_items`에서 `product_id`로 연결. 각 지표를 서브쿼리로 분리하면 깔끔합니다.


??? success "정답"
    ```sql
    SELECT
        s.company_name,
        COUNT(DISTINCT p.id) AS product_count,
        COALESCE(SUM(sales.revenue), 0) AS total_revenue,
        ROUND(AVG(rev.avg_rating), 1) AS avg_rating,
        ROUND(100.0 * COALESCE(SUM(ret.return_count), 0)
            / NULLIF(COALESCE(SUM(sales.sold_count), 0), 0), 2) AS return_rate_pct
    FROM suppliers s
    INNER JOIN products p ON p.supplier_id = s.id
    LEFT JOIN (
        SELECT product_id,
               SUM(subtotal) AS revenue,
               COUNT(*) AS sold_count
        FROM order_items
        GROUP BY product_id
    ) sales ON p.id = sales.product_id
    LEFT JOIN (
        SELECT product_id, AVG(rating) AS avg_rating
        FROM reviews
        GROUP BY product_id
    ) rev ON p.id = rev.product_id
    LEFT JOIN (
        SELECT oi.product_id, COUNT(DISTINCT r.id) AS return_count
        FROM returns r
        INNER JOIN orders o ON r.order_id = o.id
        INNER JOIN order_items oi ON o.id = oi.order_id
        GROUP BY oi.product_id
    ) ret ON p.id = ret.product_id
    GROUP BY s.id, s.company_name
    ORDER BY total_revenue DESC
    LIMIT 10;
    ```

    | company_name | product_count | total_revenue | avg_rating | return_rate_pct |
    |--------------|---------------|---------------|------------|-----------------|
    | ...          | ...           | ...           | ...        | ...             |


---


### 문제 22

**쿠폰 효과 분석:** 쿠폰 사용 주문과 미사용 주문의 평균 결제금액, 평균 상품 수, 완료율을 비교하세요.


??? tip "힌트"
    `orders LEFT JOIN coupon_usage`로 연결. `CASE WHEN cu.id IS NOT NULL THEN '사용' ELSE '미사용' END`로 구분.


??? success "정답"
    ```sql
    SELECT
        CASE WHEN cu.id IS NOT NULL THEN '쿠폰 사용' ELSE '쿠폰 미사용' END AS coupon_group,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(AVG(o.total_amount)) AS avg_amount,
        ROUND(AVG(item_stats.item_count), 1) AS avg_items,
        ROUND(100.0 * SUM(CASE WHEN o.status = 'confirmed' THEN 1 ELSE 0 END)
            / COUNT(DISTINCT o.id), 1) AS confirm_rate_pct
    FROM orders o
    LEFT JOIN coupon_usage cu ON o.id = cu.order_id
    LEFT JOIN (
        SELECT order_id, COUNT(*) AS item_count
        FROM order_items
        GROUP BY order_id
    ) item_stats ON o.id = item_stats.order_id
    GROUP BY CASE WHEN cu.id IS NOT NULL THEN '쿠폰 사용' ELSE '쿠폰 미사용' END;
    ```

    | coupon_group | order_count | avg_amount | avg_items | confirm_rate_pct |
    |--------------|-------------|------------|-----------|------------------|
    | 쿠폰 미사용 | ...         | ...        | ...       | ...              |
    | 쿠폰 사용   | ...         | ...        | ...       | ...              |


---


### 문제 23

**위시리스트 전환 분석:** 위시리스트에 등록된 상품 중 실제 구매로 이어진 비율(전환율)을 카테고리별로 조회하세요.


??? tip "힌트"
    `wishlists`의 `is_purchased` 칼럼으로 전환 여부를 파악. `products JOIN categories`로 카테고리 연결.


??? success "정답"
    ```sql
    SELECT
        cat.name AS category,
        COUNT(*) AS wishlist_count,
        SUM(w.is_purchased) AS purchased_count,
        ROUND(100.0 * SUM(w.is_purchased) / COUNT(*), 1) AS conversion_rate_pct
    FROM wishlists w
    INNER JOIN products p ON w.product_id = p.id
    INNER JOIN categories cat ON p.category_id = cat.id
    GROUP BY cat.id, cat.name
    HAVING COUNT(*) >= 5
    ORDER BY conversion_rate_pct DESC
    LIMIT 10;
    ```

    | category | wishlist_count | purchased_count | conversion_rate_pct |
    |----------|----------------|-----------------|---------------------|
    | ...      | ...            | ...             | ...                 |


---


### 문제 24

**고객 문의 응답 분석:** 문의 유형(category)별로 평균 해결 시간(created_at ~ resolved_at), 해결률, 에스컬레이션 비율을 조회하세요.


??? tip "힌트"
    `julianday(resolved_at) - julianday(created_at)`로 해결 시간. `CASE WHEN resolved_at IS NOT NULL`로 해결 건수 파악. `SUM(escalated)`로 에스컬레이션 집계.


??? success "정답"
    ```sql
    SELECT
        category,
        COUNT(*) AS total_count,
        ROUND(AVG(
            CASE WHEN resolved_at IS NOT NULL
                 THEN julianday(resolved_at) - julianday(created_at)
            END
        ), 1) AS avg_resolve_days,
        ROUND(100.0 * SUM(CASE WHEN resolved_at IS NOT NULL THEN 1 ELSE 0 END)
            / COUNT(*), 1) AS resolve_rate_pct,
        ROUND(100.0 * SUM(escalated) / COUNT(*), 1) AS escalation_rate_pct
    FROM complaints
    GROUP BY category
    ORDER BY total_count DESC;
    ```

    | category       | total_count | avg_resolve_days | resolve_rate_pct | escalation_rate_pct |
    |----------------|-------------|------------------|------------------|---------------------|
    | ...            | ...         | ...              | ...              | ...                 |


---


### 문제 25

**종합 대시보드 쿼리:** 다음 KPI를 한 번에 조회하세요. UNION ALL로 하나의 결과 테이블로 만듭니다.

1. 총 고객 수 / 활성 고객 수
2. 이번 달 매출 / 지난 달 매출
3. 평균 주문 금액
4. 평균 리뷰 평점
5. 미해결 문의 건수


??? tip "힌트"
    각 KPI를 `SELECT '지표명' AS metric, 값 AS value` 형태로 만들고 `UNION ALL`로 합칩니다. 이번 달/지난 달은 `strftime`으로 계산합니다.


??? success "정답"
    ```sql
    SELECT '총 고객 수' AS metric,
           CAST(COUNT(*) AS TEXT) AS value
    FROM customers

    UNION ALL

    SELECT '활성 고객 수',
           CAST(COUNT(*) AS TEXT)
    FROM customers
    WHERE is_active = 1

    UNION ALL

    SELECT '이번 달 매출',
           CAST(COALESCE(SUM(total_amount), 0) AS TEXT)
    FROM orders
    WHERE SUBSTR(ordered_at, 1, 7) = strftime('%Y-%m', 'now')
      AND status NOT IN ('cancelled')

    UNION ALL

    SELECT '지난 달 매출',
           CAST(COALESCE(SUM(total_amount), 0) AS TEXT)
    FROM orders
    WHERE SUBSTR(ordered_at, 1, 7) = strftime('%Y-%m', 'now', '-1 month')
      AND status NOT IN ('cancelled')

    UNION ALL

    SELECT '평균 주문 금액',
           CAST(ROUND(AVG(total_amount)) AS TEXT)
    FROM orders
    WHERE status NOT IN ('cancelled')

    UNION ALL

    SELECT '평균 리뷰 평점',
           CAST(ROUND(AVG(rating), 2) AS TEXT)
    FROM reviews

    UNION ALL

    SELECT '미해결 문의',
           CAST(COUNT(*) AS TEXT)
    FROM complaints
    WHERE status NOT IN ('resolved', 'closed');
    ```

    | metric         | value    |
    |----------------|----------|
    | 총 고객 수     | ...      |
    | 활성 고객 수   | ...      |
    | 이번 달 매출   | ...      |
    | 지난 달 매출   | ...      |
    | 평균 주문 금액 | ...      |
    | 평균 리뷰 평점 | ...      |
    | 미해결 문의    | ...      |
