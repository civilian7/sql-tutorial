# 그룹화와 필터

!!! info "사용 테이블"
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `customers` — 고객 (등급, 포인트, 가입채널)  
    `orders` — 주문 (상태, 금액, 일시)  
    `reviews` — 리뷰 (평점, 내용)  
    `payments` — 결제 (방법, 금액, 상태)  
    `complaints` — 고객 불만 (유형, 우선순위)  

!!! abstract "학습 범위"
    `GROUP BY`, `HAVING`, 집계 함수 + `GROUP BY`, 다중 그룹화

### 문제 1. 상품 브랜드별 상품 수를 구하세요.

브랜드(brand)별로 등록된 상품이 몇 개인지 조회하세요. 상품 수가 많은 순으로 정렬합니다.

??? tip "힌트"
    GROUP BY brand와 COUNT(*)를 사용하세요.

??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    ORDER BY product_count DESC;
    ```

---

### 문제 2. 고객 등급별 인원 수를 구하세요.

고객 등급(grade)별 고객 수를 조회하세요.

??? tip "힌트"
    GROUP BY grade와 COUNT(*)를 사용하세요.

??? success "정답"
    ```sql
    SELECT grade, COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade
    ORDER BY customer_count DESC;
    ```

---

### 문제 3. 주문 상태별 총 매출을 구하세요.

주문 상태(status)별로 주문 건수와 총 매출(total_amount 합계)을 조회하세요.

??? tip "힌트"
    GROUP BY status, COUNT(*), SUM(total_amount)를 함께 사용하세요.

??? success "정답"
    ```sql
    SELECT
        status,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 0) AS total_revenue
    FROM orders
    GROUP BY status
    ORDER BY total_revenue DESC;
    ```

---

### 문제 4. 리뷰 별점별 리뷰 수를 구하세요.

별점(rating) 1~5점별로 리뷰가 몇 건인지 조회하세요. 별점순으로 정렬합니다.

??? tip "힌트"
    GROUP BY rating과 COUNT(*)를 사용하세요.

??? success "정답"
    ```sql
    SELECT rating, COUNT(*) AS review_count
    FROM reviews
    GROUP BY rating
    ORDER BY rating;
    ```

---

### 문제 5. 결제 수단별 총 결제 금액을 구하세요.

결제 수단(method)별로 결제 건수와 총 금액(amount 합계)을 조회하세요. 총 금액이 큰 순으로 정렬합니다.

??? tip "힌트"
    GROUP BY method와 SUM(amount)를 사용하세요.

??? success "정답"
    ```sql
    SELECT
        method,
        COUNT(*) AS payment_count,
        ROUND(SUM(amount), 0) AS total_amount
    FROM payments
    GROUP BY method
    ORDER BY total_amount DESC;
    ```

---

### 문제 6. 불만 접수 채널별 건수를 구하세요.

불만 접수 채널(channel)별로 접수 건수를 조회하세요. 건수가 많은 순으로 정렬합니다.

??? tip "힌트"
    complaints 테이블의 channel 칼럼을 GROUP BY로 그룹화하세요.

??? success "정답"
    ```sql
    SELECT channel, COUNT(*) AS complaint_count
    FROM complaints
    GROUP BY channel
    ORDER BY complaint_count DESC;
    ```

---

### 문제 7. 고객 가입 채널별 평균 포인트 잔액을 구하세요.

가입 경로(acquisition_channel)별로 고객 수와 평균 포인트 잔액(point_balance)을 조회하세요.

??? tip "힌트"
    GROUP BY acquisition_channel과 AVG(point_balance)를 사용하세요. acquisition_channel이 NULL인 경우도 하나의 그룹으로 표시됩니다.

??? success "정답"
    ```sql
    SELECT
        acquisition_channel,
        COUNT(*) AS customer_count,
        ROUND(AVG(point_balance), 0) AS avg_points
    FROM customers
    GROUP BY acquisition_channel
    ORDER BY avg_points DESC;
    ```

---

### 문제 8. 연도별 주문 건수와 매출을 구하세요.

주문일(ordered_at)에서 연도를 추출하여 연도별 주문 건수와 총 매출을 조회하세요.

??? tip "힌트"
    SUBSTR(ordered_at, 1, 4)로 연도를 추출하고 GROUP BY로 그룹화하세요.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 0) AS total_revenue
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```

---

### 문제 9. 브랜드별 평균 가격과 평균 원가를 구하세요.

브랜드(brand)별로 평균 판매 가격(price)과 평균 원가(cost_price)를 조회하세요. 평균 가격이 높은 순으로 정렬합니다.

??? tip "힌트"
    GROUP BY brand와 AVG(price), AVG(cost_price)를 함께 사용하세요.

??? success "정답"
    ```sql
    SELECT
        brand,
        ROUND(AVG(price), 0) AS avg_price,
        ROUND(AVG(cost_price), 0) AS avg_cost
    FROM products
    GROUP BY brand
    ORDER BY avg_price DESC;
    ```

---

### 문제 10. 불만 유형별 건수와 평균 응대 횟수를 구하세요.

불만 카테고리(category)별로 접수 건수와 평균 응대 횟수(response_count)를 조회하세요.

??? tip "힌트"
    GROUP BY category와 AVG(response_count)를 사용하세요.

??? success "정답"
    ```sql
    SELECT
        category,
        COUNT(*) AS complaint_count,
        ROUND(AVG(response_count), 1) AS avg_responses
    FROM complaints
    GROUP BY category
    ORDER BY complaint_count DESC;
    ```

---

### 문제 11. 상품 수가 10개 이상인 브랜드를 조회하세요.

브랜드별 상품 수를 구한 후, 상품이 10개 이상 등록된 브랜드만 조회하세요.

??? tip "힌트"
    GROUP BY 이후 그룹을 필터링할 때는 WHERE가 아니라 HAVING을 사용합니다.

??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY product_count DESC;
    ```

---

### 문제 12. 평균 주문 금액이 300,000원 이상인 주문 상태를 구하세요.

주문 상태(status)별 평균 주문 금액을 구하고, 평균이 300,000원 이상인 상태만 조회하세요.

??? tip "힌트"
    HAVING AVG(total_amount) >= 300000 으로 필터링하세요.

??? success "정답"
    ```sql
    SELECT
        status,
        COUNT(*) AS order_count,
        ROUND(AVG(total_amount), 0) AS avg_amount
    FROM orders
    GROUP BY status
    HAVING AVG(total_amount) >= 300000
    ORDER BY avg_amount DESC;
    ```

---

### 문제 13. 2024년 월별 주문 건수를 구하되, 월 3,000건 이상인 달만 조회하세요.

2024년 월별 주문 건수를 집계하고, 주문이 3,000건 이상인 월만 조회하세요.

??? tip "힌트"
    WHERE로 2024년을 먼저 필터링하고, GROUP BY로 월별 집계 후, HAVING으로 건수를 필터링하세요.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS order_count
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    HAVING COUNT(*) >= 3000
    ORDER BY month;
    ```

---

### 문제 14. 불만 우선순위와 상태별 건수를 구하세요.

불만의 우선순위(priority)와 상태(status) 조합별로 건수를 조회하세요.

??? tip "힌트"
    GROUP BY에 여러 칼럼을 쉼표로 나열할 수 있습니다: GROUP BY priority, status

??? success "정답"
    ```sql
    SELECT
        priority,
        status,
        COUNT(*) AS cnt
    FROM complaints
    GROUP BY priority, status
    ORDER BY priority, status;
    ```

---

### 문제 15. 성별과 등급별 고객 수를 구하세요.

성별(gender)과 등급(grade) 조합별로 고객 수를 조회하세요. 고객 수가 많은 순으로 정렬합니다.

??? tip "힌트"
    GROUP BY gender, grade로 두 칼럼을 함께 그룹화하세요. gender가 NULL인 경우도 하나의 그룹으로 나타납니다.

??? success "정답"
    ```sql
    SELECT
        gender,
        grade,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY gender, grade
    ORDER BY customer_count DESC;
    ```

---

### 문제 16. 결제 완료(completed)된 건만 대상으로, 수단별 평균 결제 금액이 200,000원 이상인 수단을 구하세요.

결제 상태가 'completed'인 건만 필터링하고, 결제 수단(method)별 평균 금액이 200,000원 이상인 수단을 조회하세요.

??? tip "힌트"
    WHERE로 status = 'completed'를 먼저 필터링하고, GROUP BY + HAVING으로 평균 금액을 필터링하세요.

??? success "정답"
    ```sql
    SELECT
        method,
        COUNT(*) AS payment_count,
        ROUND(AVG(amount), 0) AS avg_amount
    FROM payments
    WHERE status = 'completed'
    GROUP BY method
    HAVING AVG(amount) >= 200000
    ORDER BY avg_amount DESC;
    ```

---

### 문제 17. 활성 상품만 대상으로, 브랜드별 총 재고 수량이 100개 이상인 브랜드를 조회하세요.

판매 중(is_active = 1)인 상품만 대상으로, 브랜드별 총 재고(stock_qty 합계)가 100개 이상인 브랜드를 조회하세요.

??? tip "힌트"
    WHERE is_active = 1로 활성 상품만 필터링한 후, GROUP BY brand + HAVING SUM(stock_qty) >= 100을 적용하세요.

??? success "정답"
    ```sql
    SELECT
        brand,
        COUNT(*) AS product_count,
        SUM(stock_qty) AS total_stock
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING SUM(stock_qty) >= 100
    ORDER BY total_stock DESC;
    ```

---

### 문제 18. 연도별, 주문 상태별 건수를 구하세요.

주문일에서 연도를 추출하여 연도와 상태(status) 조합별 주문 건수를 조회하세요.

??? tip "힌트"
    GROUP BY SUBSTR(ordered_at, 1, 4), status로 두 기준을 함께 그룹화하세요.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        status,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4), status
    ORDER BY year, order_count DESC;
    ```

---

### 문제 19. 리뷰가 50건 이상 등록된 상품 ID를 조회하세요.

상품(product_id)별 리뷰 수를 집계하고, 50건 이상인 상품만 조회하세요.

??? tip "힌트"
    GROUP BY product_id + HAVING COUNT(*) >= 50을 사용하세요.

??? success "정답"
    ```sql
    SELECT
        product_id,
        COUNT(*) AS review_count
    FROM reviews
    GROUP BY product_id
    HAVING COUNT(*) >= 50
    ORDER BY review_count DESC;
    ```

---

### 문제 20. 고객 등급별로 가입 채널 분포를 구하되, 조합당 100명 이상인 경우만 조회하세요.

등급(grade)과 가입 채널(acquisition_channel) 조합별 고객 수를 구하고, 100명 이상인 조합만 조회하세요.

??? tip "힌트"
    GROUP BY grade, acquisition_channel 후 HAVING COUNT(*) >= 100으로 필터링하세요.

??? success "정답"
    ```sql
    SELECT
        grade,
        acquisition_channel,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade, acquisition_channel
    HAVING COUNT(*) >= 100
    ORDER BY grade, customer_count DESC;
    ```

---

### 문제 21. 2024년 분기별 매출과 평균 주문 금액을 구하세요.

2024년 주문을 분기별로 나누어 주문 건수, 총 매출, 평균 주문 금액을 조회하세요. 분기는 월을 기준으로 구분합니다.

??? tip "힌트"
    SUBSTR(ordered_at, 6, 2)로 월을 추출한 뒤, (월 - 1) / 3 + 1로 분기를 계산할 수 있습니다. SQLite에서는 CAST를 사용하여 문자열을 정수로 변환하세요.

??? success "정답"
    ```sql
    SELECT
        (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) - 1) / 3 + 1 AS quarter,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 0) AS total_revenue,
        ROUND(AVG(total_amount), 0) AS avg_amount
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) - 1) / 3 + 1
    ORDER BY quarter;
    ```

---

### 문제 22. 불만 카테고리별 에스컬레이션 비율을 구하고, 비율이 10% 이상인 카테고리만 조회하세요.

불만 카테고리(category)별로 전체 건수, 에스컬레이션(escalated = 1) 건수, 에스컬레이션 비율(%)을 구하세요. 비율이 10% 이상인 카테고리만 조회합니다.

??? tip "힌트"
    SUM(escalated)으로 에스컬레이션 건수를 구하고, 100.0 * SUM(escalated) / COUNT(*)로 비율을 계산하세요. HAVING으로 비율을 필터링합니다.

??? success "정답"
    ```sql
    SELECT
        category,
        COUNT(*) AS total_count,
        SUM(escalated) AS escalated_count,
        ROUND(100.0 * SUM(escalated) / COUNT(*), 1) AS escalation_rate
    FROM complaints
    GROUP BY category
    HAVING 100.0 * SUM(escalated) / COUNT(*) >= 10
    ORDER BY escalation_rate DESC;
    ```

---

### 문제 23. 결제 수단과 카드 발급사별 총 결제 금액을 구하세요.

카드 결제(method = 'card')만 대상으로, 카드 발급사(card_issuer)별 결제 건수와 총 금액을 조회하세요. 총 금액이 큰 순으로 정렬합니다.

??? tip "힌트"
    WHERE method = 'card'로 카드 결제만 필터링한 후, GROUP BY card_issuer로 집계하세요.

??? success "정답"
    ```sql
    SELECT
        card_issuer,
        COUNT(*) AS payment_count,
        ROUND(SUM(amount), 0) AS total_amount
    FROM payments
    WHERE method = 'card'
    GROUP BY card_issuer
    ORDER BY total_amount DESC;
    ```

---

### 문제 24. 별점 평균이 3.0 미만인 상품 ID를 구하되, 리뷰가 5건 이상인 상품만 대상으로 하세요.

상품별 리뷰 평균 별점을 구하고, 리뷰가 5건 이상이면서 평균 별점이 3.0 미만인 상품을 조회하세요.

??? tip "힌트"
    HAVING에 조건을 2개 쓸 수 있습니다: HAVING COUNT(*) >= 5 AND AVG(rating) < 3.0

??? success "정답"
    ```sql
    SELECT
        product_id,
        COUNT(*) AS review_count,
        ROUND(AVG(rating), 2) AS avg_rating
    FROM reviews
    GROUP BY product_id
    HAVING COUNT(*) >= 5 AND AVG(rating) < 3.0
    ORDER BY avg_rating;
    ```

---

### 문제 25. 2023년과 2024년 각각의 월별 주문 건수를 비교하세요.

연도와 월 조합별로 주문 건수를 조회하되, 2023년과 2024년 데이터만 대상으로 하세요. 연도, 월 순으로 정렬합니다.

??? tip "힌트"
    WHERE로 2023년과 2024년을 필터링하고, GROUP BY SUBSTR(ordered_at, 1, 4), SUBSTR(ordered_at, 6, 2)로 연도+월 그룹화하세요.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        SUBSTR(ordered_at, 6, 2) AS month,
        COUNT(*) AS order_count
    FROM orders
    WHERE SUBSTR(ordered_at, 1, 4) IN ('2023', '2024')
    GROUP BY SUBSTR(ordered_at, 1, 4), SUBSTR(ordered_at, 6, 2)
    ORDER BY year, month;
    ```

---

### 문제 26. 고객 등급별 활성/비활성 고객 수와 평균 포인트를 구하세요.

등급(grade)과 활성 여부(is_active) 조합별로 고객 수와 평균 포인트 잔액을 조회하세요. 등급순, 활성 여부순으로 정렬합니다.

??? tip "힌트"
    GROUP BY grade, is_active로 두 기준을 조합하세요.

??? success "정답"
    ```sql
    SELECT
        grade,
        is_active,
        COUNT(*) AS customer_count,
        ROUND(AVG(point_balance), 0) AS avg_points
    FROM customers
    GROUP BY grade, is_active
    ORDER BY grade, is_active DESC;
    ```

---

### 문제 27. 불만 접수 채널과 우선순위 조합 중, 건수가 50건 이상이고 평균 응대 횟수가 2회 이상인 조합을 구하세요.

채널(channel)과 우선순위(priority) 조합별로 건수와 평균 응대 횟수를 조회하되, 건수 50건 이상이면서 평균 응대 횟수 2회 이상인 조합만 표시하세요.

??? tip "힌트"
    HAVING에 AND로 두 조건을 결합하세요: HAVING COUNT(*) >= 50 AND AVG(response_count) >= 2

??? success "정답"
    ```sql
    SELECT
        channel,
        priority,
        COUNT(*) AS complaint_count,
        ROUND(AVG(response_count), 1) AS avg_responses
    FROM complaints
    GROUP BY channel, priority
    HAVING COUNT(*) >= 50 AND AVG(response_count) >= 2
    ORDER BY avg_responses DESC;
    ```

---

### 문제 28. 브랜드별 평균 마진율(%)을 구하고, 마진율이 높은 상위 5개 브랜드를 조회하세요.

마진율은 (price - cost_price) / price * 100으로 계산합니다. 활성 상품(is_active = 1)만 대상으로 하세요.

??? tip "힌트"
    AVG((price - cost_price) / price * 100)으로 브랜드별 평균 마진율을 계산하세요. ORDER BY + LIMIT으로 상위 5개를 추출합니다.

??? success "정답"
    ```sql
    SELECT
        brand,
        COUNT(*) AS product_count,
        ROUND(AVG((price - cost_price) / price * 100), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    ORDER BY avg_margin_pct DESC
    LIMIT 5;
    ```

---

### 문제 29. 할부 개월 수별 카드 결제 건수와 평균 금액을 구하되, 건수가 100건 이상인 경우만 조회하세요.

카드 결제(method = 'card')를 대상으로 할부 개월 수(installment_months)별 결제 건수와 평균 금액을 구하세요. 100건 이상인 할부 구간만 표시합니다.

??? tip "힌트"
    WHERE method = 'card'로 필터링 후, GROUP BY installment_months + HAVING COUNT(*) >= 100을 적용하세요.

??? success "정답"
    ```sql
    SELECT
        installment_months,
        COUNT(*) AS payment_count,
        ROUND(AVG(amount), 0) AS avg_amount
    FROM payments
    WHERE method = 'card'
    GROUP BY installment_months
    HAVING COUNT(*) >= 100
    ORDER BY installment_months;
    ```

---

### 문제 30. 연도별 고객 가입자 수를 구하고, 전년 대비 증가 추세를 확인하세요.

고객의 가입일(created_at)에서 연도를 추출하여 연도별 신규 가입자 수를 조회하세요. 가입자가 100명 이상인 연도만 표시합니다.

??? tip "힌트"
    SUBSTR(created_at, 1, 4)로 연도를 추출하고, GROUP BY + HAVING COUNT(*) >= 100으로 필터링하세요.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 4) AS year,
        COUNT(*) AS new_customers
    FROM customers
    GROUP BY SUBSTR(created_at, 1, 4)
    HAVING COUNT(*) >= 100
    ORDER BY year;
    ```
