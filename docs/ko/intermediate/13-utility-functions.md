# 13강: 숫자·변환·조건 함수

[12강](12-string.md)에서 문자열 함수를 배웠습니다. SQL에는 날짜, 문자열 외에도 숫자를 다루는 수학 함수, 데이터 타입을 바꾸는 변환 함수, 조건에 따라 값을 선택하는 조건 함수가 있습니다. 이 세 가지를 한꺼번에 익히면 실무 쿼리의 표현력이 크게 높아집니다.

!!! note "이미 알고 계신다면"
    ROUND, ABS, CAST, NULLIF, GREATEST/LEAST에 익숙하다면 [14강: UNION](14-union.md)으로 건너뛰세요.

## 수학 함수

### ROUND — 반올림

`ROUND(value, digits)`는 소수점 이하를 지정한 자릿수로 반올림합니다. 4강에서 간단히 사용했지만, 여기서 체계적으로 정리합니다.

```sql
-- 평균 가격을 다양한 자릿수로
SELECT
    ROUND(AVG(price), 2)  AS avg_2dp,
    ROUND(AVG(price), 0)  AS avg_int,
    ROUND(AVG(price), -3) AS avg_1000
FROM products
WHERE is_active = 1;
```

**결과 (예시):**

| avg_2dp    | avg_int | avg_1000 |
| ---------: | ------: | -------: |
| 1037245.78 | 1037246 |  1037000 |

> `ROUND(value, -3)`은 천의 자리에서 반올림합니다. 보고서에서 "약 104만 원"처럼 표현할 때 유용합니다.

### ABS — 절댓값

```sql
-- 원가와 판매가의 차이 (음수 방지)
SELECT
    name,
    price,
    cost_price,
    ABS(price - cost_price) AS margin
FROM products
WHERE is_active = 1
ORDER BY margin DESC
LIMIT 5;
```

### CEIL / FLOOR — 올림과 내림

=== "SQLite"
    SQLite에는 `CEIL`/`FLOOR`가 없습니다. `CAST`와 `CASE`로 대체합니다.

    ```sql
    -- 올림: 배송비를 1000원 단위로 올림
    SELECT
        CASE
            WHEN total_amount % 1000 = 0
                THEN total_amount / 1000
            ELSE total_amount / 1000 + 1
        END AS shipping_units
    FROM orders
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    SELECT
        CEIL(4.2)  AS ceil_val,   -- 5
        FLOOR(4.8) AS floor_val;  -- 4

    -- 배송비를 1000원 단위로 올림
    SELECT
        total_amount,
        CEIL(total_amount / 1000.0) * 1000 AS rounded_up
    FROM orders
    LIMIT 5;
    ```

=== "PostgreSQL"
    ```sql
    SELECT
        CEIL(4.2)  AS ceil_val,   -- 5
        FLOOR(4.8) AS floor_val;  -- 4

    -- 배송비를 1000원 단위로 올림
    SELECT
        total_amount,
        CEIL(total_amount / 1000.0) * 1000 AS rounded_up
    FROM orders
    LIMIT 5;
    ```

### MOD — 나머지

```sql
-- 짝수 ID 고객만 추출 (A/B 테스트 그룹 분리)
SELECT id, name, grade
FROM customers
WHERE MOD(id, 2) = 0
  AND is_active = 1
LIMIT 10;
```

> SQLite에서는 `MOD(a, b)` 대신 `a % b` 연산자를 사용합니다.

### RANDOM — 랜덤 샘플링

=== "SQLite"
    ```sql
    -- 랜덤 상품 5개 추출
    SELECT name, price
    FROM products
    WHERE is_active = 1
    ORDER BY RANDOM()
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    -- 랜덤 상품 5개 추출
    SELECT name, price
    FROM products
    WHERE is_active = 1
    ORDER BY RAND()
    LIMIT 5;
    ```

=== "PostgreSQL"
    ```sql
    -- 랜덤 상품 5개 추출
    SELECT name, price
    FROM products
    WHERE is_active = 1
    ORDER BY RANDOM()
    LIMIT 5;
    ```

> **주의:** `ORDER BY RANDOM()`은 전체 행을 정렬하므로 대용량 테이블에서는 느립니다. 운영 환경에서는 다른 샘플링 기법을 사용하세요.

## 타입 변환 함수

### CAST — 타입 변환

`CAST(expression AS type)`으로 데이터 타입을 명시적으로 변환합니다. 12강에서 `CAST(SUBSTR(...) AS INTEGER)`로 이미 사용했습니다.

```sql
-- 문자열 → 숫자
SELECT CAST('12345' AS INTEGER) AS num_val;

-- 숫자 → 문자열 (연결용)
SELECT 'Order #' || CAST(id AS TEXT) AS label
FROM orders
LIMIT 3;
```

=== "SQLite"
    ```sql
    -- SQLite 타입: INTEGER, REAL, TEXT, BLOB, NUMERIC
    SELECT
        CAST(price AS INTEGER) AS int_price,
        CAST(id AS TEXT)       AS text_id,
        TYPEOF(price)          AS price_type
    FROM products
    LIMIT 3;
    ```

    > `TYPEOF(expr)`는 SQLite 전용 함수로, 값의 실제 저장 타입을 반환합니다.

=== "MySQL"
    ```sql
    -- MySQL 변환 타입: SIGNED, UNSIGNED, CHAR, DATE, DECIMAL 등
    SELECT
        CAST(price AS SIGNED)       AS int_price,
        CAST(id AS CHAR)            AS text_id,
        CAST('2024-03-15' AS DATE)  AS date_val
    FROM products
    LIMIT 3;
    ```

=== "PostgreSQL"
    ```sql
    -- PostgreSQL은 :: 단축 문법도 지원
    SELECT
        price::integer    AS int_price,
        id::text          AS text_id,
        '2024-03-15'::date AS date_val
    FROM products
    LIMIT 3;
    ```

### 정수 나눗셈 함정

4강에서도 다뤘지만, 가장 흔한 변환 실수이므로 다시 강조합니다.

```sql
-- 정수 ÷ 정수 = 정수 (소수점 버림!)
SELECT 7 / 2 AS wrong;    -- 3 (3.5가 아님!)

-- 해결: 한쪽을 실수로 변환
SELECT 7 / 2.0 AS correct;           -- 3.5
SELECT CAST(7 AS REAL) / 2 AS also;  -- 3.5
SELECT 7 * 1.0 / 2 AS trick;         -- 3.5
```

```sql
-- 실전: 주문 대비 취소율
SELECT
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
    ROUND(
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        1
    ) AS cancel_rate_pct
FROM orders;
```

## 조건 함수

### NULLIF — 0으로 나누기 방지

`NULLIF(a, b)` — a와 b가 같으면 NULL, 다르면 a를 반환합니다. 0으로 나누는 오류를 방지하는 데 가장 많이 쓰입니다.

```sql
-- 0으로 나누기 방지
SELECT
    category_id,
    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_count,
    SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive_count,
    ROUND(
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) * 100.0
        / NULLIF(SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END), 0),
        1
    ) AS active_to_inactive_ratio
FROM products
GROUP BY category_id
LIMIT 5;
```

> `NULLIF(분모, 0)` — 분모가 0이면 NULL을 반환하여 오류 대신 NULL이 됩니다.

### IIF / IF — 간단한 조건 분기

CASE 표현식의 축약형입니다. 조건이 하나뿐일 때 간결하게 쓸 수 있습니다.

=== "SQLite"
    ```sql
    -- IIF(condition, true_value, false_value) — SQLite 3.32.0+
    SELECT
        name,
        price,
        IIF(price >= 1000000, '고가', '일반') AS price_tier
    FROM products
    WHERE is_active = 1
    LIMIT 10;
    ```

=== "MySQL"
    ```sql
    -- IF(condition, true_value, false_value)
    SELECT
        name,
        price,
        IF(price >= 1000000, '고가', '일반') AS price_tier
    FROM products
    WHERE is_active = 1
    LIMIT 10;
    ```

=== "PostgreSQL"
    ```sql
    -- PostgreSQL에는 IIF/IF가 없음 → CASE 사용
    SELECT
        name,
        price,
        CASE WHEN price >= 1000000 THEN '고가' ELSE '일반' END AS price_tier
    FROM products
    WHERE is_active = 1
    LIMIT 10;
    ```

### GREATEST / LEAST — 여러 값 중 최대/최소

행 안에서 여러 칼럼의 값을 비교할 때 사용합니다. `MAX`/`MIN`은 행 간 집계이고, `GREATEST`/`LEAST`는 칼럼 간 비교입니다.

=== "SQLite"
    SQLite에는 `GREATEST`/`LEAST`가 없습니다. `MAX()`/`MIN()`이 같은 역할을 합니다.

    ```sql
    -- 주문 금액과 100만 원 중 큰 값 (최소 보장 금액)
    SELECT
        order_number,
        total_amount,
        MAX(total_amount, 1000000) AS guaranteed_min
    FROM orders
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    SELECT
        order_number,
        total_amount,
        GREATEST(total_amount, 1000000) AS guaranteed_min,
        LEAST(total_amount, 5000000)    AS capped_max
    FROM orders
    LIMIT 5;
    ```

=== "PostgreSQL"
    ```sql
    SELECT
        order_number,
        total_amount,
        GREATEST(total_amount, 1000000) AS guaranteed_min,
        LEAST(total_amount, 5000000)    AS capped_max
    FROM orders
    LIMIT 5;
    ```

> **MAX vs GREATEST:** `MAX(col)`은 여러 **행**에서 최대값, `GREATEST(a, b, c)`는 한 **행** 안에서 여러 **값** 중 최대값입니다.

## 정리

| 개념 | 설명 | 예시 |
|------|------|------|
| ROUND | 반올림 (음수 자릿수 가능) | `ROUND(price, -3)` |
| ABS | 절댓값 | `ABS(price - cost_price)` |
| CEIL / FLOOR | 올림 / 내림 | `CEIL(4.2)` → 5 |
| MOD (%) | 나머지 | `MOD(id, 2)` = 짝수 필터 |
| RANDOM | 랜덤 정렬 | `ORDER BY RANDOM()` |
| CAST | 타입 변환 | `CAST('123' AS INTEGER)` |
| TYPEOF | 타입 확인 (SQLite) | `TYPEOF(price)` |
| 정수 나눗셈 | 정수÷정수=정수 함정 | `* 1.0`으로 실수 변환 |
| NULLIF | 같으면 NULL | `NULLIF(분모, 0)` |
| IIF / IF | 간단 조건 분기 | `IIF(cond, true, false)` |
| GREATEST / LEAST | 칼럼 간 최대·최소 | `GREATEST(a, b, c)` |

!!! note "레슨 복습 문제"
    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. 여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/index.md) 섹션을 참고하세요.

## 연습 문제

### 연습 1
활성 상품의 평균 가격, 최대 가격, 최소 가격을 각각 천의 자리에서 반올림하여 표시하세요. `avg_price`, `max_price`, `min_price`를 반환하세요.

??? success "정답"
    ```sql
    SELECT
        ROUND(AVG(price), -3) AS avg_price,
        ROUND(MAX(price), -3) AS max_price,
        ROUND(MIN(price), -3) AS min_price
    FROM products
    WHERE is_active = 1;
    ```


### 연습 2
상품의 판매가(`price`)와 원가(`cost_price`)의 차이(마진)를 절댓값으로 구하세요. `name`, `price`, `cost_price`, `margin`을 반환하고, 마진이 큰 순으로 10행까지 정렬하세요.

??? success "정답"
    ```sql
    SELECT
        name,
        price,
        cost_price,
        ABS(price - cost_price) AS margin
    FROM products
    WHERE is_active = 1
    ORDER BY margin DESC
    LIMIT 10;
    ```


### 연습 3
홀수 ID 고객만 추출하여 `id`, `name`, `grade`를 반환하세요. 활성 고객만 대상으로 하고, 10행으로 제한하세요.

??? success "정답"
    ```sql
    SELECT id, name, grade
    FROM customers
    WHERE id % 2 = 1
      AND is_active = 1
    LIMIT 10;
    ```


### 연습 4
활성 상품 중 랜덤으로 3개를 추출하여 `name`과 `price`를 반환하세요.

??? success "정답"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT name, price
        FROM products
        WHERE is_active = 1
        ORDER BY RANDOM()
        LIMIT 3;
        ```

    === "MySQL"
        ```sql
        SELECT name, price
        FROM products
        WHERE is_active = 1
        ORDER BY RAND()
        LIMIT 3;
        ```


### 연습 5
주문 번호(`order_number`)에서 마지막 5자리 일련번호를 정수로 변환하고, 주문 금액을 문자열로 변환하여 `'₩'`를 붙이세요. `order_number`, `seq_no`(정수), `amount_display`(문자열)를 반환하고 5행으로 제한하세요.

??? success "정답"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT
            order_number,
            CAST(SUBSTR(order_number, -5) AS INTEGER) AS seq_no,
            '₩' || CAST(total_amount AS TEXT)         AS amount_display
        FROM orders
        LIMIT 5;
        ```

    === "MySQL"
        ```sql
        SELECT
            order_number,
            CAST(SUBSTRING(order_number, -5) AS SIGNED) AS seq_no,
            CONCAT('₩', CAST(total_amount AS CHAR))     AS amount_display
        FROM orders
        LIMIT 5;
        ```


### 연습 6
전체 주문 대비 취소율을 계산하세요. 정수 나눗셈 함정을 피하여 소수점 1자리까지 표시합니다. `total_orders`, `cancelled_orders`, `cancel_rate_pct`를 반환하세요.

??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        ROUND(
            SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
            1
        ) AS cancel_rate_pct
    FROM orders;
    ```


### 연습 7
카테고리별 활성 상품 비율을 구하되, 비활성 상품이 0개인 카테고리에서 0으로 나누기 오류가 발생하지 않도록 `NULLIF`를 사용하세요. `category_id`, `active_count`, `inactive_count`, `ratio`를 반환하세요.

??? success "정답"
    ```sql
    SELECT
        category_id,
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_count,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive_count,
        ROUND(
            SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) * 1.0
            / NULLIF(SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END), 0),
            2
        ) AS ratio
    FROM products
    GROUP BY category_id;
    ```


### 연습 8
상품 가격을 100만 원 이상이면 `'고가'`, 아니면 `'일반'`으로 분류하세요. `IIF`(SQLite) 또는 `IF`(MySQL)를 사용합니다. `name`, `price`, `tier`를 반환하고, 가격 내림차순으로 10행까지 정렬하세요.

??? success "정답"
    === "SQLite"
        ```sql
        SELECT
            name,
            price,
            IIF(price >= 1000000, '고가', '일반') AS tier
        FROM products
        WHERE is_active = 1
        ORDER BY price DESC
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT
            name,
            price,
            IF(price >= 1000000, '고가', '일반') AS tier
        FROM products
        WHERE is_active = 1
        ORDER BY price DESC
        LIMIT 10;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            name,
            price,
            CASE WHEN price >= 1000000 THEN '고가' ELSE '일반' END AS tier
        FROM products
        WHERE is_active = 1
        ORDER BY price DESC
        LIMIT 10;
        ```


### 연습 9
주문 금액이 50만 원 미만이면 50만 원으로, 500만 원 초과이면 500만 원으로 제한(capping)하세요. `order_number`, `total_amount`, `capped_amount`를 반환하고, 10행으로 제한하세요.

??? success "정답"
    === "SQLite"
        ```sql
        SELECT
            order_number,
            total_amount,
            MIN(MAX(total_amount, 500000), 5000000) AS capped_amount
        FROM orders
        LIMIT 10;
        ```

    === "MySQL / PostgreSQL"
        ```sql
        SELECT
            order_number,
            total_amount,
            LEAST(GREATEST(total_amount, 500000), 5000000) AS capped_amount
        FROM orders
        LIMIT 10;
        ```


### 연습 10
상품별 마진율(`(price - cost_price) / price * 100`)을 구하되, 가격이 0인 상품에서 오류가 발생하지 않도록 처리하세요. `name`, `price`, `cost_price`, `margin_pct`(소수점 1자리)를 반환하고, 마진율이 높은 순으로 10행까지 정렬하세요.

??? success "정답"
    ```sql
    SELECT
        name,
        price,
        cost_price,
        ROUND(
            (price - cost_price) * 100.0 / NULLIF(price, 0),
            1
        ) AS margin_pct
    FROM products
    WHERE is_active = 1
    ORDER BY margin_pct DESC
    LIMIT 10;
    ```


### 채점 가이드

| 점수 | 다음 단계 |
|:----:|----------|
| **9~10개** | [14강: UNION](14-union.md)으로 이동 |
| **7~8개** | 틀린 문제 해설을 복습한 뒤 다음강으로 |
| **절반 이하** | 이 강의를 다시 읽어보세요 |
| **3개 이하** | [12강: 문자열 함수](12-string.md)부터 다시 시작하세요 |

**문제별 영역:**

| 영역 | 해당 문제 |
|------|:--------:|
| ROUND (반올림) | 1 |
| ABS (절댓값) | 2 |
| MOD (나머지) | 3 |
| RANDOM (랜덤) | 4 |
| CAST (타입 변환) | 5 |
| 정수 나눗셈 함정 | 6 |
| NULLIF (0 나누기 방지) | 7, 10 |
| IIF / IF (간단 조건) | 8 |
| GREATEST / LEAST (칼럼 간 비교) | 9 |

---
다음: [14강: UNION](14-union.md)
