# 초급 연습: 주문 기초

`orders`, `payments` 테이블을 사용합니다. 날짜 필터, 상태 조건, 기본 집계를 연습하는 15문제입니다.

---

### 1. 전체 주문 수

전체 주문 수와 총 매출을 구하세요.

??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS total_orders,
        ROUND(SUM(total_amount), 2) AS total_revenue
    FROM orders;
    ```

---

### 2. 주문 상태별 건수

주문 상태(status)별 건수를 구하세요.

??? success "정답"
    ```sql
    SELECT status, COUNT(*) AS cnt
    FROM orders
    GROUP BY status
    ORDER BY cnt DESC;
    ```

---

### 3. 2024년 주문

2024년에 접수된 주문 수와 총 매출을 구하세요.

??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%';
    ```

---

### 4. 취소된 주문

취소(cancelled) 상태의 주문 수와 취소율(%)을 구하세요.

??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS cancelled_count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 2) AS cancel_rate
    FROM orders
    WHERE status = 'cancelled';
    ```

---

### 5. 가장 큰 주문

주문 금액이 가장 큰 상위 10건의 주문번호, 금액, 주문일을 조회하세요.

??? success "정답"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 10;
    ```

---

### 6. 월별 주문 수 (2024)

2024년 월별 주문 수와 매출을 구하세요.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```

---

### 7. 평균 주문 금액

전체 평균 주문 금액과 취소 제외 평균을 비교하세요.

??? success "정답"
    ```sql
    SELECT
        ROUND(AVG(total_amount), 2) AS avg_all,
        ROUND(AVG(CASE
            WHEN status NOT IN ('cancelled') THEN total_amount
        END), 2) AS avg_excl_cancelled
    FROM orders;
    ```

---

### 8. 무료 배송 주문 비율

배송비(shipping_fee)가 0인 주문의 비율을 구하세요.

??? success "정답"
    ```sql
    SELECT
        SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) AS free_shipping,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct
    FROM orders;
    ```

---

### 9. 적립금 사용 주문

적립금(point_used)을 사용한 주문의 수와 평균 사용 금액을 구하세요.

??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS orders_with_points,
        ROUND(AVG(point_used), 0) AS avg_points_used,
        MAX(point_used) AS max_points_used
    FROM orders
    WHERE point_used > 0;
    ```

---

### 10. 결제 수단별 현황

결제 수단(method)별 건수와 총 결제 금액을 구하세요.

??? success "정답"
    ```sql
    SELECT
        method,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS total_amount
    FROM payments
    GROUP BY method
    ORDER BY total_amount DESC;
    ```

---

### 11. 카드 할부 분석

카드 결제 중 할부(installment_months > 0) 비율과 평균 할부 개월을 구하세요.

??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS card_payments,
        SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) AS installment_count,
        ROUND(100.0 * SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS installment_pct,
        ROUND(AVG(CASE WHEN installment_months > 0 THEN installment_months END), 1) AS avg_months
    FROM payments
    WHERE method = 'card';
    ```

---

### 12. 요일별 주문 수

요일별(월~일) 주문 수를 구하세요.

??? success "정답"
    ```sql
    SELECT
        CASE CAST(STRFTIME('%w', ordered_at) AS INTEGER)
            WHEN 0 THEN '일'
            WHEN 1 THEN '월'
            WHEN 2 THEN '화'
            WHEN 3 THEN '수'
            WHEN 4 THEN '목'
            WHEN 5 THEN '금'
            WHEN 6 THEN '토'
        END AS day_name,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY STRFTIME('%w', ordered_at)
    ORDER BY STRFTIME('%w', ordered_at);
    ```

---

### 13. 배송 메모가 있는 주문

배송 메모(notes)가 있는 주문의 비율을 구하세요.

??? success "정답"
    ```sql
    SELECT
        SUM(CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END) AS with_notes,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct
    FROM orders;
    ```

---

### 14. 연도별 매출 추이

연도별 주문 수, 총 매출, 평균 주문 금액을 구하세요. 취소 주문은 제외합니다.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 2) AS revenue,
        ROUND(AVG(total_amount), 2) AS avg_order
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```

---

### 15. 환불된 결제

환불(refunded) 상태의 결제 건수와 총 환불 금액을 구하세요.

??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS refund_count,
        ROUND(SUM(amount), 2) AS total_refunded
    FROM payments
    WHERE status = 'refunded';
    ```
