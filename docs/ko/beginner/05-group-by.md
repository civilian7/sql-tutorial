# 5강: GROUP BY와 HAVING

4강에서 COUNT, SUM, AVG 등으로 전체 데이터를 요약했습니다. 하지만 '등급별 고객 수'나 '월별 매출'처럼 그룹 단위로 집계하고 싶다면? GROUP BY를 사용합니다.

!!! note "이미 알고 계신다면"
    GROUP BY, 다중 칼럼 그룹화, HAVING을 이미 알고 있다면 [6강: NULL 처리](06-null.md)로 건너뛰세요.

```mermaid
flowchart LR
    T["All\nRows"] --> G["GROUP BY\ncategory"] --> GR["Groups\n🔵🔵 | 🟢🟢🟢 | 🔴"]  --> A["Aggregate\nper group"] --> R["Summary\nper group"]
```

> **개념:** GROUP BY는 행을 그룹으로 묶고, 각 그룹에 집계 함수를 적용합니다.

## GROUP BY — 단일 칼럼

```sql
-- 멤버십 등급별 고객 수
SELECT
    grade,
    COUNT(*) AS customer_count
FROM customers
GROUP BY grade;
```

**결과:**

| grade  | customer_count |
| ------ | -------------: |
| BRONZE |           3962 |
| GOLD   |            484 |
| SILVER |            469 |
| VIP    |            315 |

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

| status           | order_count | total_revenue |
| ---------------- | ----------: | ------------: |
| confirmed        |       32053 |   32304050388 |
| cancelled        |        1754 |    1749179196 |
| return_requested |         477 |     721313512 |
| returned         |         459 |     634631268 |
| ...              | ...         | ...           |

## GROUP BY — 다중 칼럼

두 개 이상의 칼럼으로 그룹화하면 더 세밀하게 세분화할 수 있습니다.

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

| grade  | gender | cnt  |
| ------ | ------ | ---: |
| BRONZE | F      | 1332 |
| BRONZE | M      | 2194 |
| GOLD   | F      |  136 |
| GOLD   | M      |  316 |
| SILVER | F      |  126 |
| SILVER | M      |  306 |
| VIP    | F      |   76 |
| VIP    | M      |  221 |

## 월별 주문 집계

날짜 칼럼에서 연-월을 추출하면 월별로 그룹화할 수 있습니다.

=== "SQLite"
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

=== "MySQL"
    ```sql
    -- 2024년 월별 주문 건수와 매출
    SELECT
        DATE_FORMAT(ordered_at, '%Y-%m') AS year_month,
        COUNT(*)                         AS order_count,
        SUM(total_amount)                AS monthly_revenue
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at <  '2025-01-01'
    GROUP BY DATE_FORMAT(ordered_at, '%Y-%m')
    ORDER BY year_month;
    ```

=== "PostgreSQL"
    ```sql
    -- 2024년 월별 주문 건수와 매출
    SELECT
        TO_CHAR(ordered_at, 'YYYY-MM') AS year_month,
        COUNT(*)                       AS order_count,
        SUM(total_amount)              AS monthly_revenue
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at <  '2025-01-01'
    GROUP BY TO_CHAR(ordered_at, 'YYYY-MM')
    ORDER BY year_month;
    ```

**결과:**

| year_month | order_count | monthly_revenue |
|------------|------------:|----------------:|
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
|-------|---------------:|
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
| ----------: | ------------: | --------: |
|          12 |            10 |   1184410 |
|          18 |            10 |    508150 |
|          30 |            11 | 249681.82 |
| ...         | ...           | ...       |

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

## 정리

| 문법 | 설명 | 예시 |
|------|------|------|
| `GROUP BY 칼럼` | 단일 칼럼으로 그룹화 | `GROUP BY grade` |
| `GROUP BY 칼럼1, 칼럼2` | 다중 칼럼으로 세분화 | `GROUP BY grade, gender` |
| `HAVING 조건` | 그룹화 후 필터링 (집계 값 기준) | `HAVING COUNT(*) > 500` |
| `WHERE` vs `HAVING` | WHERE는 행 필터(그룹화 전), HAVING은 그룹 필터(그룹화 후) | |

!!! note "레슨 복습 문제"
    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. 여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/index.md) 섹션을 참고하세요.

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

    **결과 (예시):**

    | status    | order_count |
    | --------- | ----------: |
    | confirmed |       32053 |
    | cancelled |        1754 |


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

    **결과 (예시):**

    | method        | transaction_count | total_collected |
    | ------------- | ----------------: | --------------: |
    | card          |             14522 |     14526925164 |
    | kakao_pay     |              6359 |      6652523392 |
    | naver_pay     |              4835 |      4563329993 |
    | bank_transfer |              3194 |      3243186244 |
    | point         |              1623 |      1743665807 |
    | ...           | ...               | ...             |


### 문제 3
`customers` 테이블에서 `grade`별로 평균 포인트(`point_balance`)를 구하세요. 평균 포인트 내림차순으로 정렬하세요.

??? success "정답"
    ```sql
    SELECT
        grade,
        AVG(point_balance) AS avg_points
    FROM customers
    GROUP BY grade
    ORDER BY avg_points DESC;
    ```

    **결과 (예시):**

    | grade  | avg_points |
    | ------ | ---------: |
    | VIP    |  423073.75 |
    | GOLD   |  158543.32 |
    | SILVER |   85614.41 |
    | BRONZE |   16542.43 |


### 문제 4
`customers` 테이블에서 `grade`와 `gender` 두 칼럼으로 그룹화하여 고객 수를 구하세요. `gender`가 NULL인 행도 포함하세요.

??? success "정답"
    ```sql
    SELECT
        grade,
        gender,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade, gender
    ORDER BY grade, gender;
    ```

    **결과 (예시):**

    | grade  | gender | customer_count |
    | ------ | ------ | -------------: |
    | BRONZE | (NULL) |            436 |
    | BRONZE | F      |           1332 |
    | BRONZE | M      |           2194 |
    | GOLD   | (NULL) |             32 |
    | GOLD   | F      |            136 |
    | ...    | ...    | ...            |


### 문제 5
`reviews` 테이블에서 `rating`별 리뷰 건수를 구하세요. 리뷰가 100건 이상인 평점만 표시하고, `rating` 순으로 정렬하세요.

??? success "정답"
    ```sql
    SELECT
        rating,
        COUNT(*) AS review_count
    FROM reviews
    GROUP BY rating
    HAVING COUNT(*) >= 100
    ORDER BY rating;
    ```

    **결과 (예시):**

    | rating | review_count |
    | -----: | -----------: |
    |      1 |          395 |
    |      2 |          774 |
    |      3 |         1193 |
    |      4 |         2362 |
    |      5 |         3221 |


### 문제 6
`orders` 테이블에서 활성 주문(`status NOT IN ('cancelled', 'returned')`)만을 대상으로, `status`별 건수와 평균 금액(소수점 0자리)을 구하세요. 평균 금액이 300 초과인 상태만 표시하세요.

??? success "정답"
    ```sql
    SELECT
        status,
        COUNT(*)                    AS order_count,
        ROUND(AVG(total_amount), 0) AS avg_amount
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned')
    GROUP BY status
    HAVING AVG(total_amount) > 300
    ORDER BY avg_amount DESC;
    ```

    **결과 (예시):**

    | status           | order_count | avg_amount |
    | ---------------- | ----------: | ---------: |
    | return_requested |         477 |    1512188 |
    | preparing        |           7 |    1208178 |
    | confirmed        |       32053 |    1007832 |
    | pending          |          47 |     922266 |
    | delivered        |          77 |     876186 |
    | ...              | ...         | ...        |


### 문제 7
2023년과 2024년의 `orders` 데이터에서 월 매출이 50만 달러를 초과한 달을 찾으세요. `year_month`와 `monthly_revenue`를 날짜순으로 반환하세요.

??? success "정답"
    === "SQLite"
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

        **결과 (예시):**

        | year_month | monthly_revenue |
        | ---------- | --------------: |
        | 2023-01    |       287003017 |
        | 2023-02    |       247903157 |
        | 2023-03    |       464329421 |
        | 2023-04    |       292003281 |
        | 2023-05    |       456140850 |
        | ...        | ...             |


    === "MySQL"
        ```sql
        SELECT
            DATE_FORMAT(ordered_at, '%Y-%m') AS year_month,
            SUM(total_amount)                AS monthly_revenue
        FROM orders
        WHERE ordered_at >= '2023-01-01'
          AND ordered_at <  '2025-01-01'
          AND status NOT IN ('cancelled', 'returned')
        GROUP BY DATE_FORMAT(ordered_at, '%Y-%m')
        HAVING SUM(total_amount) > 500000
        ORDER BY year_month;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            TO_CHAR(ordered_at, 'YYYY-MM') AS year_month,
            SUM(total_amount)              AS monthly_revenue
        FROM orders
        WHERE ordered_at >= '2023-01-01'
          AND ordered_at <  '2025-01-01'
          AND status NOT IN ('cancelled', 'returned')
        GROUP BY TO_CHAR(ordered_at, 'YYYY-MM')
        HAVING SUM(total_amount) > 500000
        ORDER BY year_month;
        ```

### 문제 8
`payments` 테이블에서 결제 수단(`method`)별 고유 주문 수를 `COUNT(DISTINCT order_id)`로 구하세요. 고유 주문 수 내림차순으로 정렬하세요.

??? success "정답"
    ```sql
    SELECT
        method,
        COUNT(DISTINCT order_id) AS unique_orders
    FROM payments
    GROUP BY method
    ORDER BY unique_orders DESC;
    ```

    **결과 (예시):**

    | method          | unique_orders |
    | --------------- | ------------: |
    | card            |         15728 |
    | kakao_pay       |          6902 |
    | naver_pay       |          5252 |
    | bank_transfer   |          3483 |
    | virtual_account |          1772 |
    | ...             | ...           |


### 문제 9
`orders` 테이블에서 연도별 주문 건수와 총 매출을 구하세요. 취소/반품 주문은 제외하세요.

??? success "정답"
    === "SQLite"
        ```sql
        SELECT
            SUBSTR(ordered_at, 1, 4) AS order_year,
            COUNT(*)                 AS order_count,
            SUM(total_amount)        AS yearly_revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned')
        GROUP BY SUBSTR(ordered_at, 1, 4)
        ORDER BY order_year;
        ```

        **결과 (예시):**

        | order_year | order_count | yearly_revenue |
        | ---------: | ----------: | -------------: |
        |       2016 |         399 |      306223187 |
        |       2017 |         608 |      628189049 |
        |       2018 |        1444 |     1390778028 |
        |       2019 |        2502 |     2419434488 |
        |       2020 |        4244 |     4773995795 |
        | ...        | ...         | ...            |


    === "MySQL"
        ```sql
        SELECT
            YEAR(ordered_at)  AS order_year,
            COUNT(*)          AS order_count,
            SUM(total_amount) AS yearly_revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned')
        GROUP BY YEAR(ordered_at)
        ORDER BY order_year;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            EXTRACT(YEAR FROM ordered_at)::int AS order_year,
            COUNT(*)                           AS order_count,
            SUM(total_amount)                  AS yearly_revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned')
        GROUP BY EXTRACT(YEAR FROM ordered_at)
        ORDER BY order_year;
        ```

### 문제 10
`products` 테이블에서 `category_id`별로 상품 수, 평균 가격(소수점 0자리), 총 재고(`stock_qty` 합계)를 구하세요. 상품 수가 5개 이상이고 평균 가격이 50 이상인 카테고리만 표시하고, 상품 수 내림차순으로 정렬하세요.

??? success "정답"
    ```sql
    SELECT
        category_id,
        COUNT(*)                 AS product_count,
        ROUND(AVG(price), 0)     AS avg_price,
        SUM(stock_qty)           AS total_stock
    FROM products
    GROUP BY category_id
    HAVING COUNT(*) >= 5
       AND AVG(price) >= 50
    ORDER BY product_count DESC;
    ```

    **결과 (예시):**

    | category_id | product_count | avg_price | total_stock |
    | ----------: | ------------: | --------: | ----------: |
    |          18 |            13 |    520038 |        3826 |
    |          30 |            13 |    227223 |        3812 |
    |          43 |            12 |    247892 |        3085 |
    |           3 |            11 |   1716582 |        2241 |
    |          31 |            11 |    146564 |        2681 |
    | ...         | ...           | ...       | ...         |


### 채점 가이드

| 점수 | 다음 단계 |
|:----:|----------|
| **9~10개** | [6강: NULL 처리](06-null.md)로 이동 |
| **7~8개** | 틀린 문제 해설을 복습한 뒤 6강으로 |
| **5개 이하** | 이 강의를 다시 읽어보세요 |
| **3개 이하** | [4강: 집계 함수](04-aggregates.md)부터 다시 시작하세요 |

**문제별 영역:**

| 영역 | 해당 문제 |
|------|:--------:|
| GROUP BY + HAVING | 1, 5 |
| GROUP BY 단일 칼럼 | 2, 3 |
| GROUP BY 다중 칼럼 | 4 |
| WHERE + GROUP BY + HAVING | 6 |
| GROUP BY + HAVING (기간 필터) | 7 |
| COUNT(DISTINCT) | 8 |
| GROUP BY (날짜 함수) + WHERE | 9 |
| HAVING 다중 조건 | 10 |

---
다음: [6강: NULL 다루기](06-null.md)
