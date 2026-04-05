# 5강: GROUP BY와 HAVING

`GROUP BY`는 행을 그룹으로 나누고, 각 그룹에 집계 함수를 따로 적용합니다. `HAVING`은 그 그룹들을 다시 필터링합니다. 집계된 결과에 대한 `WHERE`라고 이해하면 됩니다.

## GROUP BY — 단일 컬럼

```sql
-- 멤버십 등급별 고객 수
SELECT
    grade,
    COUNT(*) AS customer_count
FROM customers
GROUP BY grade;
```

**결과:**

| grade | customer_count |
|-------|----------------|
| BRONZE | 2614 |
| SILVER | 1569 |
| GOLD | 785 |
| VIP | 262 |

데이터베이스는 `grade` 값이 같은 행들을 하나의 버킷에 모은 뒤, 버킷별로 행 수를 셉니다.

```sql
-- 주문 상태별 건수와 매출 합계
SELECT
    status,
    COUNT(*)           AS order_count,
    SUM(total_amount)  AS total_revenue
FROM orders
GROUP BY status
ORDER BY total_revenue DESC;
```

**결과:**

| status | order_count | total_revenue |
|--------|-------------|---------------|
| confirmed | 8423 | 7291847.20 |
| delivered | 6812 | 5904329.10 |
| shipped | 4103 | 3287650.88 |
| cancelled | 3891 | 0.00 |
| ... | | |

## GROUP BY — 다중 컬럼

두 개 이상의 컬럼으로 그룹화하면 더 세밀하게 세분화할 수 있습니다.

```sql
-- 등급과 성별로 고객 수 집계
SELECT
    grade,
    gender,
    COUNT(*) AS cnt
FROM customers
WHERE gender IS NOT NULL
GROUP BY grade, gender
ORDER BY grade, gender;
```

**결과:**

| grade | gender | cnt |
|-------|--------|-----|
| BRONZE | F | 922 |
| BRONZE | M | 1580 |
| GOLD | F | 271 |
| GOLD | M | 494 |
| SILVER | F | 543 |
| SILVER | M | 990 |
| VIP | F | 91 |
| VIP | M | 163 |

## 월별 주문 집계

SQLite의 날짜 문자열(`YYYY-MM-DD HH:MM:SS` 형식)에서 앞부분을 추출하면 월별로 그룹화할 수 있습니다.

```sql
-- 2024년 월별 주문 건수와 매출
SELECT
    SUBSTR(ordered_at, 1, 7) AS year_month,
    COUNT(*)                 AS order_count,
    SUM(total_amount)        AS monthly_revenue
FROM orders
WHERE ordered_at LIKE '2024%'
GROUP BY SUBSTR(ordered_at, 1, 7)
ORDER BY year_month;
```

**결과:**

| year_month | order_count | monthly_revenue |
|------------|-------------|-----------------|
| 2024-01 | 312 | 178432.50 |
| 2024-02 | 289 | 162890.20 |
| 2024-03 | 405 | 238741.90 |
| ... | | |

## HAVING

`HAVING`은 그룹화 이후에 필터링하며, 집계 값을 조건으로 사용합니다. 그룹에 대한 `WHERE`라고 생각하면 됩니다.

```sql
-- 고객 수가 500명 초과인 등급만 조회
SELECT
    grade,
    COUNT(*) AS customer_count
FROM customers
GROUP BY grade
HAVING COUNT(*) > 500;
```

**결과:**

| grade | customer_count |
|-------|----------------|
| BRONZE | 2614 |
| SILVER | 1569 |

```sql
-- 판매 중인 상품이 10개 이상이고 평균 가격이 $100 초과인 카테고리
SELECT
    category_id,
    COUNT(*)   AS product_count,
    AVG(price) AS avg_price
FROM products
WHERE is_active = 1
GROUP BY category_id
HAVING COUNT(*) >= 10
   AND AVG(price) > 100
ORDER BY avg_price DESC;
```

**결과:**

| category_id | product_count | avg_price |
|-------------|---------------|-----------|
| 3 | 22 | 987.45 |
| 5 | 18 | 412.30 |
| 2 | 15 | 248.90 |
| ... | | |

## WHERE vs. HAVING

| 절 | 필터 대상 | 적용 시점 |
|----|-----------|-----------|
| `WHERE` | 개별 행 | 그룹화 전 |
| `HAVING` | 그룹 | 그룹화 후 |

```sql
-- WHERE로 행 필터 후, HAVING으로 그룹 필터
SELECT
    grade,
    AVG(point_balance) AS avg_points
FROM customers
WHERE is_active = 1          -- 비활성 고객 제외 (행 수준)
GROUP BY grade
HAVING AVG(point_balance) > 500;  -- 평균 포인트가 500 초과인 등급만
```

## 연습 문제

### 문제 1
`status`별 주문 건수를 집계하세요. 건수가 1,000 초과인 상태만 표시하고, 건수 내림차순으로 정렬하세요.

??? success "정답"
    ```sql
    SELECT
        status,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY status
    HAVING COUNT(*) > 1000
    ORDER BY order_count DESC;
    ```

### 문제 2
`payments` 테이블에서 결제 수단(`method`)별로 수집된 총 금액과 거래 건수를 구하세요. 총 금액 내림차순으로 정렬하세요.

??? success "정답"
    ```sql
    SELECT
        method,
        COUNT(*)       AS transaction_count,
        SUM(amount)    AS total_collected
    FROM payments
    WHERE status = 'completed'
    GROUP BY method
    ORDER BY total_collected DESC;
    ```

### 문제 3
2023년과 2024년의 `orders` 데이터에서 월 매출이 50만 달러를 초과한 달을 찾으세요. `year_month`와 `monthly_revenue`를 날짜순으로 반환하세요.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS year_month,
        SUM(total_amount)        AS monthly_revenue
    FROM orders
    WHERE ordered_at BETWEEN '2023-01-01' AND '2024-12-31 23:59:59'
      AND status NOT IN ('cancelled', 'returned')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    HAVING SUM(total_amount) > 500000
    ORDER BY year_month;
    ```

---
다음: [6강: NULL 다루기](06-null.md)
