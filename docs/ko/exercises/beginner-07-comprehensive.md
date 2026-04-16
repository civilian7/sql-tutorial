# 종합 문제

!!! info "사용 테이블"
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `customers` — 고객 (등급, 포인트, 가입채널)  
    `orders` — 주문 (상태, 금액, 일시)  
    `reviews` — 리뷰 (평점, 내용)  
    `payments` — 결제 (방법, 금액, 상태)  
    `categories` — 카테고리 (부모-자식 계층)  
    `suppliers` — 공급업체 (업체명, 연락처)  

!!! abstract "학습 범위"
    입문 전체: `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, 집계 함수, `GROUP BY`, `HAVING`, `IS NULL`, `COALESCE`, `CASE`

## 기초 (1~10)

2~3개의 개념을 조합하여 연습합니다.

---

### 문제 1

**판매 중인 상품(`is_active = 1`) 중 가격이 가장 비싼 상위 5개의 이름, 브랜드, 가격을 조회하세요.**

??? tip "힌트"
    `WHERE`로 필터링 + `ORDER BY DESC` + `LIMIT` 조합입니다.

??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE is_active = 1
    ORDER BY price DESC
    LIMIT 5;
    ```

---

### 문제 2

**VIP 등급 고객 중 마지막 로그인 기록이 있는 고객의 이름과 마지막 로그인일을 최근순으로 10건 조회하세요.**

??? tip "힌트"
    `WHERE grade = 'VIP' AND last_login_at IS NOT NULL`로 두 조건을 결합합니다.

??? success "정답"
    ```sql
    SELECT name, last_login_at
    FROM customers
    WHERE grade = 'VIP'
      AND last_login_at IS NOT NULL
    ORDER BY last_login_at DESC
    LIMIT 10;
    ```

---

### 문제 3

**2024년 취소된 주문의 주문번호, 주문 금액, 취소일을 최근 취소 순으로 10건 조회하세요.**

??? tip "힌트"
    `WHERE ordered_at LIKE '2024%' AND cancelled_at IS NOT NULL`로 조건을 결합합니다.

??? success "정답"
    ```sql
    SELECT order_number, total_amount, cancelled_at
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND cancelled_at IS NOT NULL
    ORDER BY cancelled_at DESC
    LIMIT 10;
    ```

---

### 문제 4

**평점 4점 이상인 리뷰 수와 평균 평점을 구하세요. 평균은 소수점 2자리까지 표시합니다.**

??? tip "힌트"
    `WHERE rating >= 4`로 필터링 후 `COUNT(*)`와 `ROUND(AVG(rating), 2)`를 사용합니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS high_rating_count,
           ROUND(AVG(rating), 2) AS avg_rating
    FROM reviews
    WHERE rating >= 4;
    ```

---

### 문제 5

**브랜드별 판매 중인 상품 수를 구하되, 10개 이상인 브랜드만 상품 수 내림차순으로 조회하세요.**

??? tip "힌트"
    `WHERE is_active = 1` + `GROUP BY brand` + `HAVING COUNT(*) >= 10` 조합입니다.

??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY product_count DESC;
    ```

---

### 문제 6

**고객 등급별 평균 적립금을 구하되, 등급을 한글로 표시하세요. 평균 적립금이 높은 순으로 정렬합니다.**

??? tip "힌트"
    `CASE`로 등급 변환 + `GROUP BY` + `AVG` + `ORDER BY` 조합입니다.

??? success "정답"
    ```sql
    SELECT CASE grade
               WHEN 'VIP' THEN 'VIP'
               WHEN 'GOLD' THEN '골드'
               WHEN 'SILVER' THEN '실버'
               WHEN 'BRONZE' THEN '브론즈'
           END AS grade_kr,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY grade
    ORDER BY avg_points DESC;
    ```

---

### 문제 7

**결제 수단별 총 결제 금액과 건수를 구하되, 총 금액이 10억 이상인 수단만 조회하세요.**

??? tip "힌트"
    `GROUP BY method` + `HAVING SUM(amount) >= 1000000000` 조합입니다.

??? success "정답"
    ```sql
    SELECT method,
           COUNT(*) AS payment_count,
           ROUND(SUM(amount)) AS total_amount
    FROM payments
    GROUP BY method
    HAVING SUM(amount) >= 1000000000
    ORDER BY total_amount DESC;
    ```

---

### 문제 8

**가입 경로가 NULL인 고객의 등급별 수를 구하세요. CASE로 등급 순서를 지정하여 VIP부터 표시합니다.**

??? tip "힌트"
    `WHERE acquisition_channel IS NULL` + `GROUP BY grade` + `ORDER BY CASE` 조합입니다.

??? success "정답"
    ```sql
    SELECT grade, COUNT(*) AS customer_count
    FROM customers
    WHERE acquisition_channel IS NULL
    GROUP BY grade
    ORDER BY CASE grade
                 WHEN 'VIP' THEN 1
                 WHEN 'GOLD' THEN 2
                 WHEN 'SILVER' THEN 3
                 WHEN 'BRONZE' THEN 4
             END;
    ```

---

### 문제 9

**주문 상태별 건수와 평균 주문 금액을 구하되, 배송 요청사항의 입력률(%)도 함께 표시하세요. 건수가 많은 순으로 정렬합니다.**

??? tip "힌트"
    `COUNT(notes) * 100.0 / COUNT(*)`로 입력률을 계산합니다. NULL과 집계 함수의 관계를 활용합니다.

??? success "정답"
    ```sql
    SELECT status,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(COUNT(notes) * 100.0 / COUNT(*), 1) AS notes_rate_pct
    FROM orders
    GROUP BY status
    ORDER BY order_count DESC;
    ```

---

### 문제 10

**상품을 재고 상태(품절/부족/보통/충분)로 분류하고, 각 그룹의 상품 수와 평균 가격을 구하세요. 판매 중인 상품만 대상입니다.**

??? tip "힌트"
    `WHERE is_active = 1` + `CASE`로 재고 분류 + `GROUP BY` + 집계 함수 조합입니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN stock_qty = 0 THEN '품절'
               WHEN stock_qty <= 10 THEN '부족'
               WHEN stock_qty <= 100 THEN '보통'
               ELSE '충분'
           END AS stock_status,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price
    FROM products
    WHERE is_active = 1
    GROUP BY stock_status
    ORDER BY product_count DESC;
    ```

---

## 응용 (11~20)

3~4개의 개념을 조합한 비즈니스 시나리오입니다.

---

### 문제 11

**브랜드별 판매 중인 상품 수, 평균 가격, 평균 마진율(%)을 구하세요. 상품 수가 5개 이상인 브랜드만 평균 마진율이 높은 순으로 조회합니다.**

??? tip "힌트"
    마진율 = `(price - cost_price) * 100.0 / price`. `WHERE` + `GROUP BY` + `HAVING` + `ORDER BY` 조합입니다.

??? success "정답"
    ```sql
    SELECT brand,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price,
           ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 5
    ORDER BY avg_margin_pct DESC;
    ```

---

### 문제 12

**연도별 주문 건수, 총 매출, 평균 주문 금액, 취소 건수를 구하세요. 취소 건수는 cancelled_at이 NULL이 아닌 행의 수입니다.**

??? tip "힌트"
    `SUBSTR(ordered_at, 1, 4)`로 연도 추출. `COUNT(cancelled_at)`은 NULL이 아닌 행만 셉니다.

??? success "정답"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 4) AS year,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue,
           ROUND(AVG(total_amount)) AS avg_amount,
           COUNT(cancelled_at) AS cancelled_count
    FROM orders
    GROUP BY year
    ORDER BY year;
    ```

---

### 문제 13

**가입 경로별 고객 수, VIP 비율(%), 평균 적립금을 구하세요. 경로가 NULL이면 '미분류'로 표시하고, 고객 수가 많은 순으로 정렬합니다.**

??? tip "힌트"
    `COALESCE`로 NULL 대체 + `SUM(CASE WHEN grade = 'VIP' THEN 1 ELSE 0 END)`로 VIP 수 집계 + `GROUP BY` 조합입니다.

??? success "정답"
    ```sql
    SELECT COALESCE(acquisition_channel, '미분류') AS channel,
           COUNT(*) AS customer_count,
           ROUND(SUM(CASE WHEN grade = 'VIP' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS vip_rate_pct,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY COALESCE(acquisition_channel, '미분류')
    ORDER BY customer_count DESC;
    ```

---

### 문제 14

**2024년 월별 주문 건수와 평균 주문 금액을 구하되, 계절(봄/여름/가을/겨울)도 함께 표시하세요.**

??? tip "힌트"
    `SUBSTR`로 월 추출 + `CASE`로 계절 분류 + `GROUP BY` + 집계 조합입니다.

??? success "정답"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 7) AS month,
           CASE
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (3, 4, 5) THEN '봄'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (6, 7, 8) THEN '여름'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (9, 10, 11) THEN '가을'
               ELSE '겨울'
           END AS season,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```

---

### 문제 15

**리뷰를 평점별로 집계하되, 각 평점의 한글 라벨, 건수, 전체 대비 비율(%), 제목 입력률(%)을 함께 표시하세요. 평점 높은 순으로 정렬합니다.**

??? tip "힌트"
    `CASE`로 평점 라벨 + `COUNT(*)` + 비율 계산 + `COUNT(title)` 조합입니다.

??? success "정답"
    ```sql
    SELECT rating,
           CASE rating
               WHEN 5 THEN '최고'
               WHEN 4 THEN '좋음'
               WHEN 3 THEN '보통'
               WHEN 2 THEN '별로'
               WHEN 1 THEN '최악'
           END AS rating_label,
           COUNT(*) AS review_count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct,
           ROUND(COUNT(title) * 100.0 / COUNT(*), 1) AS title_rate_pct
    FROM reviews
    GROUP BY rating
    ORDER BY rating DESC;
    ```

    > 윈도우 함수(`OVER()`)를 아직 배우지 않았다면, 비율 칼럼은 생략해도 됩니다.

---

### 문제 16

**상품의 가격대(저가/중저가/중가/고가)별로 상품 수, 평균 재고, 단종률(%)을 구하세요. 단종률은 is_active=0인 비율입니다.**

??? tip "힌트"
    `CASE`로 가격대 분류 + `SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END)`로 단종 수 집계 + `GROUP BY` 조합입니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier,
           COUNT(*) AS product_count,
           ROUND(AVG(stock_qty)) AS avg_stock,
           ROUND(SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS discontinued_pct
    FROM products
    GROUP BY price_tier
    ORDER BY product_count DESC;
    ```

---

### 문제 17

**등급별 고객 수, 평균 적립금, 성별 입력률(%), 로그인 경험률(%)을 한 번에 조회하세요. 등급 순서는 VIP > GOLD > SILVER > BRONZE입니다.**

??? tip "힌트"
    `COUNT(gender)`로 성별 입력 수, `COUNT(last_login_at)`으로 로그인 경험 수를 구합니다. `ORDER BY CASE`로 등급 순서를 지정합니다.

??? success "정답"
    ```sql
    SELECT grade,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points,
           ROUND(COUNT(gender) * 100.0 / COUNT(*), 1) AS gender_rate_pct,
           ROUND(COUNT(last_login_at) * 100.0 / COUNT(*), 1) AS login_rate_pct
    FROM customers
    GROUP BY grade
    ORDER BY CASE grade
                 WHEN 'VIP' THEN 1
                 WHEN 'GOLD' THEN 2
                 WHEN 'SILVER' THEN 3
                 WHEN 'BRONZE' THEN 4
             END;
    ```

---

### 문제 18

**주문 상태를 3그룹(처리중/완료/취소반품)으로 분류하고, 각 그룹의 건수, 총 매출, 평균 배송비, 포인트 사용 건수를 구하세요.**

??? tip "힌트"
    `CASE WHEN status IN (...)`로 그룹 분류. `SUM(CASE WHEN point_used > 0 THEN 1 ELSE 0 END)`로 포인트 사용 건수를 셉니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN status IN ('pending', 'paid', 'preparing') THEN '처리중'
               WHEN status IN ('shipped', 'delivered', 'confirmed') THEN '완료'
               ELSE '취소/반품'
           END AS status_group,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue,
           ROUND(AVG(shipping_fee)) AS avg_shipping,
           SUM(CASE WHEN point_used > 0 THEN 1 ELSE 0 END) AS point_used_count
    FROM orders
    GROUP BY status_group
    ORDER BY order_count DESC;
    ```

---

### 문제 19

**카드 결제 중 카드사별 결제 건수, 평균 금액, 할부 이용률(%)을 구하세요. 카드사 정보가 NULL인 건은 제외하고, 건수가 100 이상인 카드사만 조회합니다.**

??? tip "힌트"
    `WHERE method = 'card' AND card_issuer IS NOT NULL`로 필터. `SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END)`로 할부 건수를 셉니다.

??? success "정답"
    ```sql
    SELECT card_issuer,
           COUNT(*) AS payment_count,
           ROUND(AVG(amount)) AS avg_amount,
           ROUND(SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS installment_rate_pct
    FROM payments
    WHERE method = 'card'
      AND card_issuer IS NOT NULL
    GROUP BY card_issuer
    HAVING COUNT(*) >= 100
    ORDER BY payment_count DESC;
    ```

---

### 문제 20

**공급업체별 상품 수와 활성 상품 비율(%)을 구하세요. 상품 수가 3개 이상인 공급업체만 대상이며, 활성 비율이 높은 순으로 정렬합니다. 공급업체는 supplier_id로 그룹화합니다.**

??? tip "힌트"
    `GROUP BY supplier_id` + `HAVING COUNT(*) >= 3` + `SUM(CASE WHEN is_active = 1 ...)`로 활성 비율 계산 + `ORDER BY` 조합입니다.

??? success "정답"
    ```sql
    SELECT supplier_id,
           COUNT(*) AS product_count,
           SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_count,
           ROUND(SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS active_rate_pct
    FROM products
    GROUP BY supplier_id
    HAVING COUNT(*) >= 3
    ORDER BY active_rate_pct DESC;
    ```

---

## 실전 (21~30)

4개 이상의 개념을 조합한 실무 분석 과제입니다.

---

### 문제 21

**브랜드별 활성 상품 수와 평균 가격을 구하되, 평균 가격 100만원 이상인 브랜드만 조회하세요. 가격대 분류(프리미엄/대중/보급형)도 함께 표시합니다.**

??? tip "힌트"
    `WHERE is_active = 1` + `GROUP BY brand` + `HAVING AVG(price) >= 1000000` + `CASE`로 가격대 분류 조합입니다.

??? success "정답"
    ```sql
    SELECT brand,
           COUNT(*) AS active_product_count,
           ROUND(AVG(price)) AS avg_price,
           CASE
               WHEN AVG(price) >= 2000000 THEN '프리미엄'
               WHEN AVG(price) >= 1000000 THEN '대중'
               ELSE '보급형'
           END AS brand_tier
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING AVG(price) >= 1000000
    ORDER BY avg_price DESC;
    ```

---

### 문제 22

**2024년 월별 매출 분석: 월별 주문 건수, 총 매출, 평균 주문 금액, 취소율(%), 무료배송 비율(%)을 구하세요.**

??? tip "힌트"
    다양한 집계를 조합합니다. 취소율 = `COUNT(cancelled_at) / COUNT(*)`. 무료배송 = `shipping_fee = 0`인 건의 비율입니다.

??? success "정답"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 7) AS month,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(COUNT(cancelled_at) * 100.0 / COUNT(*), 1) AS cancel_rate_pct,
           ROUND(SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS free_ship_pct
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```

---

### 문제 23

**고객 세그먼트 분석: 등급과 활동 상태(활동/휴면/탈퇴)를 조합하여 세그먼트별 고객 수와 평균 적립금을 구하세요. 고객 수 100명 이상인 세그먼트만 조회합니다.**

??? tip "힌트"
    `CASE`로 활동 상태(is_active=0이면 탈퇴, last_login_at IS NULL이면 휴면, 그 외 활동) 분류. `GROUP BY grade, activity_status` 조합입니다.

??? success "정답"
    ```sql
    SELECT grade,
           CASE
               WHEN is_active = 0 THEN '탈퇴'
               WHEN last_login_at IS NULL THEN '휴면'
               ELSE '활동'
           END AS activity_status,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY grade, activity_status
    HAVING COUNT(*) >= 100
    ORDER BY CASE grade
                 WHEN 'VIP' THEN 1
                 WHEN 'GOLD' THEN 2
                 WHEN 'SILVER' THEN 3
                 WHEN 'BRONZE' THEN 4
             END,
             customer_count DESC;
    ```

---

### 문제 24

**상품 데이터 품질 리포트: 브랜드별로 상품 수, 설명 누락률(%), 사양 누락률(%), 무게 누락률(%)을 구하세요. 상품 수 10개 이상인 브랜드만 대상이며, 전체 누락률(3개 평균)이 높은 순으로 정렬합니다.**

??? tip "힌트"
    `(COUNT(*) - COUNT(칼럼)) * 100.0 / COUNT(*)`로 각 칼럼의 누락률을 구합니다. 3개의 누락률 평균으로 정렬합니다.

??? success "정답"
    ```sql
    SELECT brand,
           COUNT(*) AS product_count,
           ROUND((COUNT(*) - COUNT(description)) * 100.0 / COUNT(*), 1) AS desc_missing_pct,
           ROUND((COUNT(*) - COUNT(specs)) * 100.0 / COUNT(*), 1) AS specs_missing_pct,
           ROUND((COUNT(*) - COUNT(weight_grams)) * 100.0 / COUNT(*), 1) AS weight_missing_pct
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY (
        (COUNT(*) - COUNT(description)) +
        (COUNT(*) - COUNT(specs)) +
        (COUNT(*) - COUNT(weight_grams))
    ) * 1.0 / COUNT(*) DESC;
    ```

---

### 문제 25

**연도별 고객 가입 분석: 가입 연도별 고객 수, 성별 비율(남/여/미입력), 평균 적립금을 구하세요.**

??? tip "힌트"
    `SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)`로 남성 비율을 구합니다. 성별 NULL도 별도 비율로 계산합니다.

??? success "정답"
    ```sql
    SELECT SUBSTR(created_at, 1, 4) AS join_year,
           COUNT(*) AS customer_count,
           ROUND(SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS male_pct,
           ROUND(SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS female_pct,
           ROUND(SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS unknown_pct,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY join_year
    ORDER BY join_year;
    ```

---

### 문제 26

**할인 분석: 2024년 주문에서 할인 적용 여부(할인있음/할인없음)와 금액 구간(소액/일반/고액/VIP급)을 조합하여 건수와 평균 주문 금액을 구하세요.**

??? tip "힌트"
    `CASE WHEN discount_amount > 0`로 할인 여부, `CASE WHEN total_amount < 50000`으로 금액 구간을 분류합니다. `GROUP BY`에 두 CASE를 모두 사용합니다.

??? success "정답"
    ```sql
    SELECT CASE WHEN discount_amount > 0 THEN '할인있음' ELSE '할인없음' END AS has_discount,
           CASE
               WHEN total_amount < 50000 THEN '소액'
               WHEN total_amount < 200000 THEN '일반'
               WHEN total_amount < 1000000 THEN '고액'
               ELSE 'VIP급'
           END AS amount_tier,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY has_discount, amount_tier
    ORDER BY has_discount, avg_amount DESC;
    ```

---

### 문제 27

**카테고리별 상품 현황: category_id별 전체 상품 수, 판매중 수, 단종 수, 품절 수, 평균 가격을 구하세요. 전체 상품 수가 5개 이상인 카테고리만 대상입니다.**

??? tip "힌트"
    `SUM(CASE WHEN 조건 THEN 1 ELSE 0 END)`로 각 상태의 수를 별도 칼럼으로 집계합니다.

??? success "정답"
    ```sql
    SELECT category_id,
           COUNT(*) AS total,
           SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_count,
           SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS discontinued_count,
           SUM(CASE WHEN stock_qty = 0 THEN 1 ELSE 0 END) AS out_of_stock,
           ROUND(AVG(price)) AS avg_price
    FROM products
    GROUP BY category_id
    HAVING COUNT(*) >= 5
    ORDER BY total DESC;
    ```

---

### 문제 28

**결제 수단 종합 분석: 수단별(한글 표시) 건수, 총 금액, 평균 금액, 환불 건수, 환불률(%)을 구하세요. 건수가 1,000건 이상인 수단만 대상입니다.**

??? tip "힌트"
    `CASE`로 수단 한글화 + `COUNT(refunded_at)`으로 환불 건수 + `HAVING` + `ORDER BY` 조합입니다.

??? success "정답"
    ```sql
    SELECT CASE method
               WHEN 'card' THEN '신용카드'
               WHEN 'bank_transfer' THEN '계좌이체'
               WHEN 'virtual_account' THEN '가상계좌'
               WHEN 'kakao_pay' THEN '카카오페이'
               WHEN 'naver_pay' THEN '네이버페이'
               WHEN 'point' THEN '포인트'
           END AS method_kr,
           COUNT(*) AS payment_count,
           ROUND(SUM(amount)) AS total_amount,
           ROUND(AVG(amount)) AS avg_amount,
           COUNT(refunded_at) AS refund_count,
           ROUND(COUNT(refunded_at) * 100.0 / COUNT(*), 1) AS refund_rate_pct
    FROM payments
    GROUP BY method
    HAVING COUNT(*) >= 1000
    ORDER BY total_amount DESC;
    ```

---

### 문제 29

**고객 프로필 완성도 분석: 완성도 점수(0~4점)별 고객 수, 비율(%), 평균 적립금, VIP 비율(%)을 구하세요. 완성도 = birth_date, gender, last_login_at, acquisition_channel 중 NULL이 아닌 수.**

??? tip "힌트"
    `(칼럼 IS NOT NULL)`은 SQLite에서 1 또는 0을 반환합니다. 4개를 더해 완성도 점수를 구합니다.

??? success "정답"
    ```sql
    SELECT (birth_date IS NOT NULL)
         + (gender IS NOT NULL)
         + (last_login_at IS NOT NULL)
         + (acquisition_channel IS NOT NULL) AS completeness,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points,
           ROUND(SUM(CASE WHEN grade = 'VIP' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS vip_rate_pct
    FROM customers
    GROUP BY completeness
    ORDER BY completeness;
    ```

    > 프로필 완성도가 높을수록 VIP 비율과 평균 적립금이 높은 경향이 있다면, 프로필 입력 유도 캠페인의 근거가 됩니다.

---

### 문제 30

**종합 대시보드: 상품 테이블에서 브랜드별 활성 상품 수, 평균 가격, 평균 마진율(%), 가격대 분류, 재고 부족 상품 수(stock_qty <= 10)를 구하세요. 활성 상품 5개 이상인 브랜드만 대상이며, 활성 상품 수 내림차순으로 상위 10개만 조회합니다.**

??? tip "힌트"
    여러 집계와 CASE를 동시에 사용합니다. `WHERE is_active = 1` + `GROUP BY brand` + `HAVING` + `ORDER BY` + `LIMIT` 조합입니다.

??? success "정답"
    ```sql
    SELECT brand,
           COUNT(*) AS active_count,
           ROUND(AVG(price)) AS avg_price,
           ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct,
           CASE
               WHEN AVG(price) >= 1000000 THEN '프리미엄'
               WHEN AVG(price) >= 300000 THEN '대중'
               ELSE '보급형'
           END AS brand_tier,
           SUM(CASE WHEN stock_qty <= 10 THEN 1 ELSE 0 END) AS low_stock_count
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 5
    ORDER BY active_count DESC
    LIMIT 10;
    ```

    > 이 유형의 쿼리는 실제 이커머스 운영에서 브랜드 포트폴리오를 평가할 때 사용됩니다. 마진율이 낮으면서 재고 부족 상품이 많은 브랜드는 수익성 개선이 필요합니다.
