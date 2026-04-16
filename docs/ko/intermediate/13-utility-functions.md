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

| avg_2dp | avg_int | avg_1000 |
| ----------: | ----------: | ----------: |
| 678774.85 | 678775.0 | 678775.0 |

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
|------|------|------

<!-- BEGIN_LESSON_EXERCISES -->

!!! note "레슨 복습 문제"
    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. 여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/index.md) 섹션을 참고하세요.

### 문제 1
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


    **실행 결과** (1행)

    | avg_price | max_price | min_price |
    |---|---|---|
    | 656,583.00 | 5,481,100.00 | 100.00 |

### 문제 2
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


    **실행 결과** (총 10행 중 상위 7행)

    | name | price | cost_price | margin |
    |---|---|---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 | 3,205,400.00 | 2,275,700.00 |
    | Razer Blade 18 블랙 | 4,353,100.00 | 3,047,200.00 | 1,305,900.00 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 | 3,296,400.00 | 1,200,300.00 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 | 2,480,900.00 | 1,190,600.00 |
    | ASUS Dual RTX 4060 Ti 블랙 | 2,674,800.00 | 1,562,700.00 | 1,112,100.00 |
    | ASUS ROG Strix Scar 16 | 2,452,500.00 | 1,561,200.00 | 891,300.00 |
    | ASUS ExpertBook B5 화이트 | 2,068,800.00 | 1,216,600.00 | 852,200.00 |

### 문제 3
홀수 ID 고객만 추출하여 `id`, `name`, `grade`를 반환하세요. 활성 고객만 대상으로 하고, 10행으로 제한하세요.

??? success "정답"
    ```sql
    SELECT id, name, grade
    FROM customers
    WHERE id % 2 = 1
    AND is_active = 1
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | id | name | grade |
    |---|---|---|
    | 3 | 김민재 | VIP |
    | 5 | 이정수 | SILVER |
    | 15 | 강은서 | BRONZE |
    | 19 | 김건우 | BRONZE |
    | 21 | 이서연 | GOLD |
    | 23 | 김영희 | BRONZE |
    | 25 | 윤준영 | BRONZE |

### 문제 4
활성 상품 중 랜덤으로 3개를 추출하여 `name`과 `price`를 반환하세요.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE is_active = 1
    ORDER BY RANDOM()
    LIMIT 3;
    ```


    **실행 결과** (3행)

    | name | price |
    |---|---|
    | 한컴오피스 2024 기업용 화이트 | 134,100.00 |
    | 삼성 갤럭시북5 360 블랙 | 1,179,900.00 |
    | AMD Ryzen 9 9900X | 591,800.00 |

### 문제 5
주문 번호(`order_number`)에서 마지막 5자리 일련번호를 정수로 변환하고, 주문 금액을 문자열로 변환하여 `'₩'`를 붙이세요. `order_number`, `seq_no`(정수), `amount_display`(문자열)를 반환하고 5행으로 제한하세요.

??? success "정답"
    ```sql
    SELECT
    order_number,
    CAST(SUBSTR(order_number, -5) AS INTEGER) AS seq_no,
    '₩' || CAST(total_amount AS TEXT)         AS amount_display
    FROM orders
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | order_number | seq_no | amount_display |
    |---|---|---|
    | ORD-20160101-00001 | 1 | ₩167000.0 |
    | ORD-20160102-00002 | 2 | ₩211800.0 |
    | ORD-20160102-00003 | 3 | ₩704800.0 |
    | ORD-20160103-00004 | 4 | ₩167000.0 |
    | ORD-20160103-00005 | 5 | ₩534490.0 |

### 문제 6
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


    **실행 결과** (1행)

    | total_orders | cancelled_orders | cancel_rate_pct |
    |---|---|---|
    | 37,557 | 1859 | 4.90 |

### 문제 7
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


    **실행 결과** (총 41행 중 상위 7행)

    | category_id | active_count | inactive_count | ratio |
    |---|---|---|---|
    | 2 | 3 | 2 | 1.50 |
    | 3 | 9 | 2 | 4.50 |
    | 4 | 1 | 1 | 1.00 |
    | 6 | 8 | 2 | 4.00 |
    | 7 | 6 | 3 | 2.00 |
    | 8 | 7 | 2 | 3.50 |
    | 9 | 1 | 0 | NULL |

### 문제 8
상품 가격을 100만 원 이상이면 `'고가'`, 아니면 `'일반'`으로 분류하세요. `IIF`(SQLite) 또는 `IF`(MySQL)를 사용합니다. `name`, `price`, `tier`를 반환하고, 가격 내림차순으로 10행까지 정렬하세요.

??? success "정답"
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


    **실행 결과** (총 10행 중 상위 7행)

    | name | price | tier |
    |---|---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 | 고가 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 | 고가 |
    | Razer Blade 18 블랙 | 4,353,100.00 | 고가 |
    | Razer Blade 16 실버 | 3,702,900.00 | 고가 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 | 고가 |
    | ASUS ROG Strix GT35 | 3,296,800.00 | 고가 |
    | Razer Blade 18 블랙 | 2,987,500.00 | 고가 |

### 문제 9
주문 금액이 50만 원 미만이면 50만 원으로, 500만 원 초과이면 500만 원으로 제한(capping)하세요. `order_number`, `total_amount`, `capped_amount`를 반환하고, 10행으로 제한하세요.

??? success "정답"
    ```sql
    SELECT
    order_number,
    total_amount,
    MIN(MAX(total_amount, 500000), 5000000) AS capped_amount
    FROM orders
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | total_amount | capped_amount |
    |---|---|---|
    | ORD-20160101-00001 | 167,000.00 | 500,000 |
    | ORD-20160102-00002 | 211,800.00 | 500,000 |
    | ORD-20160102-00003 | 704,800.00 | 704,800.00 |
    | ORD-20160103-00004 | 167,000.00 | 500,000 |
    | ORD-20160103-00005 | 534,490.00 | 534,490.00 |
    | ORD-20160104-00006 | 167,000.00 | 500,000 |
    | ORD-20160104-00007 | 687,400.00 | 687,400.00 |

### 문제 10
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


    **실행 결과** (총 10행 중 상위 7행)

    | name | price | cost_price | margin_pct |
    |---|---|---|---|
    | Norton AntiVirus Plus 실버 | 74,800.00 | 32,400.00 | 56.70 |
    | Windows 11 Pro 실버 | 423,000.00 | 198,800.00 | 53.00 |
    | 한컴오피스 2024 기업용 실버 | 241,400.00 | 116,400.00 | 51.80 |
    | FK 테스트 | 100.00 | 50.00 | 50.00 |
    | 로지텍 G502 HERO 실버 | 71,100.00 | 36,500.00 | 48.70 |
    | V3 Endpoint Security 블랙 | 46,500.00 | 24,200.00 | 48.00 |
    | Microsoft 365 Personal | 108,200.00 | 57,900.00 | 46.50 |

<!-- END_LESSON_EXERCISES -->
