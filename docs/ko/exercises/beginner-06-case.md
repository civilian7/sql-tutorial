# CASE 표현식

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `products` (2,800행), `customers` (52,300행), `orders` (378,368행), `reviews` (86,806행), `payments` (378,368행)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    `CASE WHEN THEN ELSE END`, 단순 CASE, 검색 CASE, CASE + 집계/정렬

</div>

!!! info "시작하기 전에"
    이 연습은 **입문 1~7강**에서 배운 내용을 사용합니다.
    JOIN, 서브쿼리, 윈도우 함수는 사용하지 않습니다.

---

## 기초 (1~10)

단순 CASE와 검색 CASE의 기본 사용법을 연습합니다.

---

### 문제 1

**고객의 이름과 등급을 조회하되, 등급을 한글로 표시하세요. BRONZE='브론즈', SILVER='실버', GOLD='골드', VIP='VIP'**

??? tip "힌트"
    단순 CASE 문법: `CASE 칼럼 WHEN 값1 THEN 결과1 WHEN 값2 THEN 결과2 ... END`

??? success "정답"
    ```sql
    SELECT name,
           CASE grade
               WHEN 'BRONZE' THEN '브론즈'
               WHEN 'SILVER' THEN '실버'
               WHEN 'GOLD' THEN '골드'
               WHEN 'VIP' THEN 'VIP'
           END AS grade_kr
    FROM customers
    LIMIT 10;
    ```

---

### 문제 2

**상품의 이름과 가격, 그리고 가격대를 표시하세요. 10만원 미만='저가', 10만원~50만원='중저가', 50만원~100만원='중가', 100만원 이상='고가'**

??? tip "힌트"
    검색 CASE 문법: `CASE WHEN 조건1 THEN 결과1 WHEN 조건2 THEN 결과2 ... ELSE 기본값 END`. 조건은 위에서 아래로 평가되므로 순서에 주의하세요.

??? success "정답"
    ```sql
    SELECT name, price,
           CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier
    FROM products
    LIMIT 10;
    ```

---

### 문제 3

**주문의 주문번호와 상태를 조회하되, 상태를 한글로 표시하세요. pending='주문접수', paid='결제완료', preparing='준비중', shipped='배송중', delivered='배송완료', confirmed='구매확정', cancelled='취소', return_requested='반품요청', returned='반품완료'**

??? tip "힌트"
    단순 CASE를 사용하여 status 값을 한글로 변환합니다.

??? success "정답"
    ```sql
    SELECT order_number,
           CASE status
               WHEN 'pending' THEN '주문접수'
               WHEN 'paid' THEN '결제완료'
               WHEN 'preparing' THEN '준비중'
               WHEN 'shipped' THEN '배송중'
               WHEN 'delivered' THEN '배송완료'
               WHEN 'confirmed' THEN '구매확정'
               WHEN 'cancelled' THEN '취소'
               WHEN 'return_requested' THEN '반품요청'
               WHEN 'returned' THEN '반품완료'
           END AS status_kr
    FROM orders
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```

---

### 문제 4

**리뷰의 평점을 텍스트로 표시하세요. 5='최고', 4='좋음', 3='보통', 2='별로', 1='최악'**

??? tip "힌트"
    `CASE rating WHEN 5 THEN '최고' ...` 형태의 단순 CASE를 사용합니다.

??? success "정답"
    ```sql
    SELECT rating,
           CASE rating
               WHEN 5 THEN '최고'
               WHEN 4 THEN '좋음'
               WHEN 3 THEN '보통'
               WHEN 2 THEN '별로'
               WHEN 1 THEN '최악'
           END AS rating_text,
           title
    FROM reviews
    LIMIT 10;
    ```

---

### 문제 5

**상품의 재고 상태를 표시하세요. 재고 0='품절', 1~10='부족', 11~100='보통', 101 이상='충분'**

??? tip "힌트"
    검색 CASE에서 `stock_qty`의 범위를 조건으로 사용합니다.

??? success "정답"
    ```sql
    SELECT name, stock_qty,
           CASE
               WHEN stock_qty = 0 THEN '품절'
               WHEN stock_qty <= 10 THEN '부족'
               WHEN stock_qty <= 100 THEN '보통'
               ELSE '충분'
           END AS stock_status
    FROM products
    LIMIT 10;
    ```

---

### 문제 6

**결제 수단(`method`)을 한글로 표시하세요. card='신용카드', bank_transfer='계좌이체', virtual_account='가상계좌', kakao_pay='카카오페이', naver_pay='네이버페이', point='포인트'. 상위 10건만 조회합니다.**

??? tip "힌트"
    단순 CASE로 method 값을 한글로 변환합니다.

??? success "정답"
    ```sql
    SELECT order_id,
           CASE method
               WHEN 'card' THEN '신용카드'
               WHEN 'bank_transfer' THEN '계좌이체'
               WHEN 'virtual_account' THEN '가상계좌'
               WHEN 'kakao_pay' THEN '카카오페이'
               WHEN 'naver_pay' THEN '네이버페이'
               WHEN 'point' THEN '포인트'
           END AS method_kr,
           amount
    FROM payments
    LIMIT 10;
    ```

---

### 문제 7

**고객의 활성 상태를 텍스트로 표시하세요. is_active가 1이면 '활성', 0이면 '탈퇴'**

??? tip "힌트"
    `CASE is_active WHEN 1 THEN '활성' WHEN 0 THEN '탈퇴' END` 또는 검색 CASE를 사용합니다.

??? success "정답"
    ```sql
    SELECT name, email,
           CASE is_active
               WHEN 1 THEN '활성'
               WHEN 0 THEN '탈퇴'
           END AS status
    FROM customers
    LIMIT 10;
    ```

---

### 문제 8

**주문 금액 구간을 표시하세요. 5만원 미만='소액', 5만원~20만원='일반', 20만원~100만원='고액', 100만원 이상='VIP급'. 최근 주문 10건에 대해 조회합니다.**

??? tip "힌트"
    검색 CASE로 `total_amount`의 범위를 구분합니다.

??? success "정답"
    ```sql
    SELECT order_number, total_amount,
           CASE
               WHEN total_amount < 50000 THEN '소액'
               WHEN total_amount < 200000 THEN '일반'
               WHEN total_amount < 1000000 THEN '고액'
               ELSE 'VIP급'
           END AS amount_tier
    FROM orders
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```

---

### 문제 9

**상품의 판매 상태를 종합적으로 표시하세요. is_active가 0이면 '단종', stock_qty가 0이면 '품절', 그 외는 '판매중'**

??? tip "힌트"
    CASE는 위에서 아래로 평가됩니다. 단종 여부를 먼저 체크하고, 그다음 품절을 체크합니다.

??? success "정답"
    ```sql
    SELECT name, price, is_active, stock_qty,
           CASE
               WHEN is_active = 0 THEN '단종'
               WHEN stock_qty = 0 THEN '품절'
               ELSE '판매중'
           END AS sale_status
    FROM products
    LIMIT 15;
    ```

---

### 문제 10

**고객의 적립금 수준을 표시하세요. 0='없음', 1~5000='소액', 5001~20000='보통', 20001 이상='고액'. 상위 10건만 조회합니다.**

??? tip "힌트"
    `point_balance`의 범위를 검색 CASE로 분류합니다.

??? success "정답"
    ```sql
    SELECT name, point_balance,
           CASE
               WHEN point_balance = 0 THEN '없음'
               WHEN point_balance <= 5000 THEN '소액'
               WHEN point_balance <= 20000 THEN '보통'
               ELSE '고액'
           END AS point_level
    FROM customers
    LIMIT 10;
    ```

---

## 응용 (11~20)

CASE + GROUP BY, CASE + ORDER BY, CASE + 집계 함수를 조합합니다.

---

### 문제 11

**상품을 가격대별로 분류하고, 각 가격대의 상품 수를 구하세요. 10만원 미만='저가', 10만원~50만원='중저가', 50만원~100만원='중가', 100만원 이상='고가'**

??? tip "힌트"
    CASE 표현식을 `SELECT`와 `GROUP BY` 모두에 사용합니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier,
           COUNT(*) AS product_count
    FROM products
    GROUP BY CASE
                 WHEN price < 100000 THEN '저가'
                 WHEN price < 500000 THEN '중저가'
                 WHEN price < 1000000 THEN '중가'
                 ELSE '고가'
             END
    ORDER BY product_count DESC;
    ```

---

### 문제 12

**주문을 진행 상태로 크게 3분류하고, 각각의 건수를 구하세요. pending/paid/preparing='처리중', shipped/delivered/confirmed='완료', cancelled/return_requested/returned='취소/반품'**

??? tip "힌트"
    `CASE WHEN status IN (...) THEN ...`으로 여러 값을 하나의 그룹으로 묶습니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN status IN ('pending', 'paid', 'preparing') THEN '처리중'
               WHEN status IN ('shipped', 'delivered', 'confirmed') THEN '완료'
               WHEN status IN ('cancelled', 'return_requested', 'returned') THEN '취소/반품'
           END AS status_group,
           COUNT(*) AS order_count
    FROM orders
    GROUP BY status_group
    ORDER BY order_count DESC;
    ```

---

### 문제 13

**리뷰를 긍정(4~5점)/보통(3점)/부정(1~2점)으로 분류하고, 각 그룹의 리뷰 수를 구하세요.**

??? tip "힌트"
    검색 CASE로 rating 범위를 3개 그룹으로 나눕니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN rating >= 4 THEN '긍정'
               WHEN rating = 3 THEN '보통'
               ELSE '부정'
           END AS sentiment,
           COUNT(*) AS review_count
    FROM reviews
    GROUP BY sentiment
    ORDER BY review_count DESC;
    ```

---

### 문제 14

**상품을 가격대별로 분류하고, 각 가격대의 평균 재고 수량을 구하세요. 소수점 없이 반올림합니다.**

??? tip "힌트"
    CASE로 가격대를 분류하고 `AVG(stock_qty)`로 평균 재고를 구합니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier,
           COUNT(*) AS product_count,
           ROUND(AVG(stock_qty)) AS avg_stock
    FROM products
    GROUP BY price_tier
    ORDER BY avg_stock DESC;
    ```

---

### 문제 15

**고객을 성별로 분류하되, NULL은 '미입력'으로 표시하고 각 그룹의 수를 구하세요.**

??? tip "힌트"
    `CASE WHEN gender IS NULL THEN '미입력' WHEN gender = 'M' THEN '남성' ...`처럼 NULL을 먼저 처리합니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN gender IS NULL THEN '미입력'
               WHEN gender = 'M' THEN '남성'
               WHEN gender = 'F' THEN '여성'
           END AS gender_kr,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY gender_kr
    ORDER BY customer_count DESC;
    ```

---

### 문제 16

**결제 수단별 건수와 평균 결제 금액을 구하되, 결제 수단을 한글로 표시하세요. 평균 금액은 원 단위로 반올림합니다.**

??? tip "힌트"
    CASE로 method를 한글로 변환한 뒤 GROUP BY와 집계 함수를 함께 사용합니다.

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
           ROUND(AVG(amount)) AS avg_amount
    FROM payments
    GROUP BY method
    ORDER BY payment_count DESC;
    ```

---

### 문제 17

**상품을 정렬하되, 품절 상품(stock_qty=0)을 맨 아래로, 나머지는 가격이 저렴한 순으로 정렬하세요. 상위 15건만 조회합니다.**

??? tip "힌트"
    `ORDER BY`에 CASE를 사용하면 커스텀 정렬이 가능합니다. 품절이면 1, 아니면 0을 반환하여 품절을 뒤로 보냅니다.

??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE is_active = 1
    ORDER BY CASE WHEN stock_qty = 0 THEN 1 ELSE 0 END,
             price ASC
    LIMIT 15;
    ```

---

### 문제 18

**고객 등급을 커스텀 순서(VIP > GOLD > SILVER > BRONZE)로 정렬하여 등급별 고객 수를 조회하세요.**

??? tip "힌트"
    `ORDER BY CASE grade WHEN 'VIP' THEN 1 WHEN 'GOLD' THEN 2 ...`로 원하는 순서를 지정합니다.

??? success "정답"
    ```sql
    SELECT grade, COUNT(*) AS customer_count
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

### 문제 19

**주문 금액 구간별로 건수와 총 매출을 구하세요. 구간: 5만원 미만, 5~20만원, 20~100만원, 100만원 이상**

??? tip "힌트"
    CASE로 금액 구간을 분류한 뒤 `COUNT(*)`와 `SUM(total_amount)`를 함께 집계합니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN total_amount < 50000 THEN '5만원 미만'
               WHEN total_amount < 200000 THEN '5~20만원'
               WHEN total_amount < 1000000 THEN '20~100만원'
               ELSE '100만원 이상'
           END AS amount_tier,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue
    FROM orders
    GROUP BY amount_tier
    ORDER BY total_revenue DESC;
    ```

---

### 문제 20

**리뷰를 평점 그룹별(긍정/보통/부정)로 분류하고, 제목(`title`)이 있는 리뷰의 비율(%)을 구하세요.**

??? tip "힌트"
    `COUNT(title) * 100.0 / COUNT(*)`로 title이 NULL이 아닌 비율을 구합니다. CASE로 평점 그룹화 후 GROUP BY합니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN rating >= 4 THEN '긍정'
               WHEN rating = 3 THEN '보통'
               ELSE '부정'
           END AS sentiment,
           COUNT(*) AS review_count,
           ROUND(COUNT(title) * 100.0 / COUNT(*), 1) AS title_rate_pct
    FROM reviews
    GROUP BY sentiment
    ORDER BY review_count DESC;
    ```

---

## 실전 (21~30)

비즈니스 분류, 복합 조건, CASE 응용을 연습합니다.

---

### 문제 21

**상품을 마진율 구간으로 분류하세요. 마진율 = (price - cost_price) / price * 100. 10% 미만='저마진', 10~20%='표준', 20~30%='고마진', 30% 이상='프리미엄'. 판매 중인 상품(`is_active = 1`)만 대상으로, 구간별 상품 수와 평균 마진율을 구하세요.**

??? tip "힌트"
    마진율 계산식을 CASE의 조건에 그대로 사용합니다. `(price - cost_price) * 100.0 / price`로 계산합니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN (price - cost_price) * 100.0 / price < 10 THEN '저마진'
               WHEN (price - cost_price) * 100.0 / price < 20 THEN '표준'
               WHEN (price - cost_price) * 100.0 / price < 30 THEN '고마진'
               ELSE '프리미엄'
           END AS margin_tier,
           COUNT(*) AS product_count,
           ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1
    GROUP BY margin_tier
    ORDER BY avg_margin_pct DESC;
    ```

---

### 문제 22

**고객을 가입 연도별, 등급별로 분류하여 수를 구하세요. 가입 연도는 SUBSTR(created_at, 1, 4)로 추출합니다. 최근 3년(2023, 2024, 2025)만 대상으로 합니다.**

??? tip "힌트"
    `GROUP BY`에 `SUBSTR(created_at, 1, 4)`와 `grade`를 함께 사용합니다. `HAVING`이 아닌 `WHERE`로 연도를 필터링합니다.

??? success "정답"
    ```sql
    SELECT SUBSTR(created_at, 1, 4) AS join_year,
           grade,
           COUNT(*) AS customer_count
    FROM customers
    WHERE SUBSTR(created_at, 1, 4) IN ('2023', '2024', '2025')
    GROUP BY join_year, grade
    ORDER BY join_year, CASE grade
                            WHEN 'VIP' THEN 1
                            WHEN 'GOLD' THEN 2
                            WHEN 'SILVER' THEN 3
                            WHEN 'BRONZE' THEN 4
                        END;
    ```

---

### 문제 23

**배송비 정책을 분석하세요. 주문 금액 5만원 미만은 배송비 부과, 5만원 이상은 무료배송입니다. 2024년 주문에서 유료/무료배송 각각의 건수, 평균 주문 금액, 총 배송비를 구하세요.**

??? tip "힌트"
    `CASE WHEN total_amount < 50000 THEN '유료배송' ELSE '무료배송' END`로 분류합니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN total_amount < 50000 THEN '유료배송'
               ELSE '무료배송'
           END AS shipping_type,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(SUM(shipping_fee)) AS total_shipping_fee
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY shipping_type;
    ```

---

### 문제 24

**결제 상태별로 건수를 구하되, 상태를 한글로 표시하고 '완료' 건의 비율(%)도 함께 표시하세요.**

??? tip "힌트"
    전체 건수 대비 특정 조건의 비율은 `SUM(CASE WHEN ... THEN 1 ELSE 0 END) * 100.0 / COUNT(*)`로 계산합니다.

??? success "정답"
    ```sql
    SELECT CASE status
               WHEN 'completed' THEN '완료'
               WHEN 'pending' THEN '대기'
               WHEN 'failed' THEN '실패'
               WHEN 'refunded' THEN '환불'
           END AS status_kr,
           COUNT(*) AS payment_count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM payments
    GROUP BY status
    ORDER BY payment_count DESC;
    ```

    > 윈도우 함수를 아직 배우지 않았다면, 비율은 생략하고 건수만 구해도 됩니다.

---

### 문제 25

**고객을 활동 상태로 3단계 분류하세요. 탈퇴(is_active=0), 휴면(is_active=1이지만 last_login_at이 NULL), 활동(나머지). 각 그룹의 고객 수를 구하세요.**

??? tip "힌트"
    CASE 조건 순서가 중요합니다. `is_active = 0`을 먼저, 그다음 `last_login_at IS NULL`을 체크합니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN is_active = 0 THEN '탈퇴'
               WHEN last_login_at IS NULL THEN '휴면'
               ELSE '활동'
           END AS activity_status,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY activity_status
    ORDER BY customer_count DESC;
    ```

---

### 문제 26

**2024년 월별 주문 건수를 구하되, 계절도 함께 표시하세요. 3~5월='봄', 6~8월='여름', 9~11월='가을', 12~2월='겨울'**

??? tip "힌트"
    `CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER)`로 월을 추출합니다. CASE로 계절을 분류합니다.

??? success "정답"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 7) AS month,
           CASE
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (3, 4, 5) THEN '봄'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (6, 7, 8) THEN '여름'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (9, 10, 11) THEN '가을'
               ELSE '겨울'
           END AS season,
           COUNT(*) AS order_count
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```

---

### 문제 27

**브랜드별 상품 수와 평균 가격을 구하되, 상품 수가 10개 이상인 브랜드만 조회하세요. 평균 가격에 따라 '프리미엄 브랜드'(100만원 이상), '대중 브랜드'(30만원~100만원), '보급형 브랜드'(30만원 미만)로 분류하세요.**

??? tip "힌트"
    `GROUP BY brand` + `HAVING COUNT(*) >= 10`으로 필터링 후, `CASE`로 평균 가격을 분류합니다.

??? success "정답"
    ```sql
    SELECT brand,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price,
           CASE
               WHEN AVG(price) >= 1000000 THEN '프리미엄 브랜드'
               WHEN AVG(price) >= 300000 THEN '대중 브랜드'
               ELSE '보급형 브랜드'
           END AS brand_tier
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY avg_price DESC;
    ```

---

### 문제 28

**포인트 사용 분석: 주문에서 포인트를 사용한 건과 사용하지 않은 건을 분류하고, 각각의 건수, 평균 주문 금액, 평균 할인 금액을 구하세요.**

??? tip "힌트"
    `CASE WHEN point_used > 0 THEN '사용' ELSE '미사용' END`로 분류합니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN point_used > 0 THEN '포인트 사용'
               ELSE '포인트 미사용'
           END AS point_usage,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(AVG(discount_amount)) AS avg_discount
    FROM orders
    GROUP BY point_usage;
    ```

---

### 문제 29

**상품을 단종 여부와 재고 상태로 4분류하세요. (단종+재고있음, 단종+재고없음, 판매중+재고있음, 판매중+재고없음) 각 그룹의 상품 수와 평균 가격을 구하세요.**

??? tip "힌트"
    두 개의 조건(is_active, stock_qty)을 조합하여 CASE로 4가지를 분류합니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN is_active = 0 AND stock_qty > 0 THEN '단종+재고있음'
               WHEN is_active = 0 AND stock_qty = 0 THEN '단종+재고없음'
               WHEN is_active = 1 AND stock_qty > 0 THEN '판매중+재고있음'
               WHEN is_active = 1 AND stock_qty = 0 THEN '판매중+품절'
           END AS status_group,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price
    FROM products
    GROUP BY status_group
    ORDER BY product_count DESC;
    ```

---

### 문제 30

**카드 결제의 할부 분석: 결제 수단이 'card'인 건에서 할부 구간별(일시불, 2~3개월, 4~6개월, 7개월 이상, 정보없음) 건수와 평균 결제 금액을 구하세요. 일시불은 installment_months가 0인 경우입니다.**

??? tip "힌트"
    `WHERE method = 'card'`로 카드 결제만 필터링합니다. `installment_months`가 NULL인 경우도 고려해야 합니다.

??? success "정답"
    ```sql
    SELECT CASE
               WHEN installment_months IS NULL THEN '정보없음'
               WHEN installment_months = 0 THEN '일시불'
               WHEN installment_months <= 3 THEN '2~3개월'
               WHEN installment_months <= 6 THEN '4~6개월'
               ELSE '7개월 이상'
           END AS installment_tier,
           COUNT(*) AS payment_count,
           ROUND(AVG(amount)) AS avg_amount
    FROM payments
    WHERE method = 'card'
    GROUP BY installment_tier
    ORDER BY payment_count DESC;
    ```

    > 할부 개월이 길수록 평균 결제 금액이 높은 경향이 있습니다. 이는 고가 상품 구매 시 할부를 선호하는 소비 패턴을 반영합니다.
