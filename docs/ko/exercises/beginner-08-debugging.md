# SQL 오류 찾기 -- 초급

!!! info "사용 테이블"
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `customers` — 고객 (등급, 포인트, 가입채널)  
    `orders` — 주문 (상태, 금액, 일시)  
    `reviews` — 리뷰 (평점, 내용)  
    `payments` — 결제 (방법, 금액, 상태)  

!!! abstract "학습 범위"
    입문 1~7강의 문법/논리 오류 찾기 및 수정

## 기초 (1~10)

구문(Syntax) 오류를 찾습니다.

---

### 문제 1

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT name price brand
FROM products
LIMIT 5;
```

??? tip "힌트"
    SELECT 절에서 칼럼을 나열할 때 필요한 구분 기호를 확인하세요.

??? success "정답"
    **오류:** 칼럼 사이에 쉼표(`,`)가 빠져 있습니다.

    **수정:**
    ```sql
    SELECT name, price, brand
    FROM products
    LIMIT 5;
    ```

---

### 문제 2

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT name, price
FROM products
WHERE brand = "ASUS";
```

??? tip "힌트"
    SQL 표준에서 문자열 리터럴에 사용하는 따옴표 종류를 확인하세요. SQLite에서는 동작할 수 있지만 표준 SQL 관점에서 문제가 있습니다.

??? success "정답"
    **오류:** SQL 표준에서 문자열 리터럴은 작은따옴표(`'`)를 사용합니다. 큰따옴표(`"`)는 식별자(칼럼명, 테이블명) 용도입니다. SQLite에서는 큰따옴표도 문자열로 허용되지만, 다른 DB에서는 에러가 발생합니다.

    **수정:**
    ```sql
    SELECT name, price
    FROM products
    WHERE brand = 'ASUS';
    ```

---

### 문제 3

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELCET name, email
FROM customers
WHERE grade = 'VIP';
```

??? tip "힌트"
    SQL 키워드의 철자를 확인하세요.

??? success "정답"
    **오류:** `SELCET`는 오타입니다. 올바른 키워드는 `SELECT`입니다.

    **수정:**
    ```sql
    SELECT name, email
    FROM customers
    WHERE grade = 'VIP';
    ```

---

### 문제 4

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT name, price
FROM products
WHERE price BETWEEN 100000 AND 500000
ORDER BY price
LIMIT 10;
```

??? tip "힌트"
    이 쿼리는 사실 문법적으로 올바릅니다. `ORDER BY price`의 기본 정렬 방향을 생각해보세요. 의도가 "비싼 순"이라면?

??? success "정답"
    **오류:** 문법 오류는 없지만, `ORDER BY price`는 기본 오름차순(ASC)입니다. 비싼 순으로 정렬하려면 `DESC`가 필요합니다. 의도에 따라 올바를 수 있습니다.

    **수정 (비싼 순 의도인 경우):**
    ```sql
    SELECT name, price
    FROM products
    WHERE price BETWEEN 100000 AND 500000
    ORDER BY price DESC
    LIMIT 10;
    ```

---

### 문제 5

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT name, email, grade
FROM customers
WHERE grade = 'VIP'
ORDER name;
```

??? tip "힌트"
    정렬에 사용하는 키워드를 정확히 확인하세요.

??? success "정답"
    **오류:** `ORDER name`은 잘못된 문법입니다. `ORDER BY name`이 올바릅니다.

    **수정:**
    ```sql
    SELECT name, email, grade
    FROM customers
    WHERE grade = 'VIP'
    ORDER BY name;
    ```

---

### 문제 6

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT name, price
FROM products
WHERE name LIKE '%게이밍'%;
```

??? tip "힌트"
    LIKE 패턴의 따옴표 위치를 확인하세요. `%`가 문자열 안에 있어야 합니다.

??? success "정답"
    **오류:** `'%게이밍'%`에서 닫는 따옴표 위치가 잘못되었습니다. `%`가 문자열 밖에 있습니다.

    **수정:**
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%게이밍%';
    ```

---

### 문제 7

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT name, price, stock_qty
FROM products
WHERE price > 100000
  AND stock_qty > 0
ORDER BY price DESC
LIMIT 10
WHERE is_active = 1;
```

??? tip "힌트"
    SQL 절의 순서를 확인하세요. WHERE는 어디에 위치해야 하나요?

??? success "정답"
    **오류:** `WHERE`절이 두 번 사용되었고, `LIMIT` 뒤에 올 수 없습니다. 모든 조건은 하나의 `WHERE`절에 `AND`로 결합해야 합니다.

    **수정:**
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE price > 100000
      AND stock_qty > 0
      AND is_active = 1
    ORDER BY price DESC
    LIMIT 10;
    ```

---

### 문제 8

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT name AS 상품명 price AS 가격
FROM products
LIMIT 5;
```

??? tip "힌트"
    SELECT 절에서 칼럼 별칭을 지정할 때도 칼럼 사이에 필요한 것이 있습니다.

??? success "정답"
    **오류:** `상품명`과 `price` 사이에 쉼표(`,`)가 빠져 있습니다.

    **수정:**
    ```sql
    SELECT name AS 상품명, price AS 가격
    FROM products
    LIMIT 5;
    ```

---

### 문제 9

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT name, price
FROM products
WHERE brand IN ('ASUS' 'MSI' 'Dell');
```

??? tip "힌트"
    `IN` 목록 안의 값 구분 기호를 확인하세요.

??? success "정답"
    **오류:** `IN` 목록의 값들 사이에 쉼표가 빠져 있습니다. `('ASUS' 'MSI' 'Dell')`은 문자열 연결로 해석될 수 있습니다.

    **수정:**
    ```sql
    SELECT name, price
    FROM products
    WHERE brand IN ('ASUS', 'MSI', 'Dell');
    ```

---

### 문제 10

다음 쿼리의 오류를 찾고 수정하세요.

```sql
SELECT COUNT(*) AS total,
       AVG(price) AS avg_price
       SUM(price) AS total_price
FROM products;
```

??? tip "힌트"
    SELECT 목록의 칼럼 사이를 확인하세요.

??? success "정답"
    **오류:** `AVG(price) AS avg_price`와 `SUM(price) AS total_price` 사이에 쉼표가 빠져 있습니다.

    **수정:**
    ```sql
    SELECT COUNT(*) AS total,
           AVG(price) AS avg_price,
           SUM(price) AS total_price
    FROM products;
    ```

---

## 응용 (11~20)

논리(Logic) 오류를 찾습니다.

---

### 문제 11

다음 쿼리는 생년월일이 없는 고객을 찾으려 합니다. 결과가 0행입니다. 왜일까요?

```sql
SELECT name, email
FROM customers
WHERE birth_date = NULL;
```

??? tip "힌트"
    SQL에서 NULL은 "알 수 없는 값"입니다. `=` 연산자로 비교하면 항상 어떤 결과가 나올까요?

??? success "정답"
    **오류:** `NULL = NULL`은 TRUE가 아니라 NULL(UNKNOWN)을 반환합니다. NULL 비교에는 `= NULL` 대신 `IS NULL`을 사용해야 합니다.

    **수정:**
    ```sql
    SELECT name, email
    FROM customers
    WHERE birth_date IS NULL;
    ```

---

### 문제 12

다음 쿼리는 브랜드별 상품 수를 구하려 합니다. 에러가 납니다.

```sql
SELECT brand, COUNT(*) AS product_count
FROM products;
```

??? tip "힌트"
    집계 함수와 비집계 칼럼을 함께 SELECT할 때 필요한 절이 있습니다.

??? success "정답"
    **오류:** `COUNT(*)`는 집계 함수인데 `brand`는 비집계 칼럼입니다. `GROUP BY` 절이 없으면 어떤 브랜드의 값을 표시할지 알 수 없습니다.

    **수정:**
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand;
    ```

---

### 문제 13

다음 쿼리는 상품 수가 10개 이상인 브랜드만 조회하려 합니다. 에러가 납니다.

```sql
SELECT brand, COUNT(*) AS product_count
FROM products
WHERE COUNT(*) >= 10
GROUP BY brand;
```

??? tip "힌트"
    `WHERE`절에서 집계 함수를 사용할 수 있을까요?

??? success "정답"
    **오류:** `WHERE`절에서는 집계 함수를 사용할 수 없습니다. 그룹화 후 필터링은 `HAVING`을 사용해야 합니다.

    **수정:**
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10;
    ```

---

### 문제 14

다음 쿼리는 'ASUS'가 아닌 상품을 찾으려 합니다. 그런데 brand가 NULL인 상품이 누락됩니다.

```sql
SELECT name, brand
FROM products
WHERE brand != 'ASUS';
```

??? tip "힌트"
    `NULL != 'ASUS'`의 결과는 TRUE일까요? NULL과의 비교는 항상 NULL(UNKNOWN)입니다.

??? success "정답"
    **오류:** `brand`가 NULL인 행에서 `NULL != 'ASUS'`는 NULL(UNKNOWN)을 반환하므로 결과에서 제외됩니다. NULL인 행도 포함하려면 명시적으로 처리해야 합니다.

    **수정:**
    ```sql
    SELECT name, brand
    FROM products
    WHERE brand != 'ASUS' OR brand IS NULL;
    ```

    > products 테이블에서 brand는 NOT NULL이므로 실제로는 이 문제가 발생하지 않지만, NULL 허용 칼럼에서는 주의가 필요합니다.

---

### 문제 15

다음 쿼리는 주문 금액 상위 10건을 구하려 합니다. ORDER BY의 위치가 잘못되었습니다.

```sql
SELECT order_number, total_amount
FROM orders
LIMIT 10
ORDER BY total_amount DESC;
```

??? tip "힌트"
    SQL 절의 실행 순서를 생각해보세요. LIMIT과 ORDER BY 중 어느 것이 먼저 와야 할까요?

??? success "정답"
    **오류:** `LIMIT`이 `ORDER BY` 앞에 있습니다. SQL에서 `ORDER BY`는 `LIMIT`보다 먼저 와야 합니다. 이 쿼리는 정렬 없이 아무 10건을 가져온 후 정렬하므로 상위 10건이 아닙니다.

    **수정:**
    ```sql
    SELECT order_number, total_amount
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 10;
    ```

---

### 문제 16

다음 쿼리는 등급별 평균 적립금이 높은 순으로 조회합니다. ORDER BY에 별칭을 사용했는데 동작하지 않는 경우가 있습니다.

```sql
SELECT grade,
       AVG(point_balance) AS avg_points
FROM customers
GROUP BY grade
ORDER BY avg_points DESC;
```

??? tip "힌트"
    이 쿼리는 SQLite에서는 정상 동작합니다. 하지만 일부 DB에서는 `ORDER BY`에서 별칭 사용에 제한이 있습니다. 어떤 대안이 있을까요?

??? success "정답"
    **오류:** SQLite에서는 문제없지만, 일부 데이터베이스(특히 구버전)에서는 `ORDER BY`에서 SELECT 별칭을 인식하지 못합니다.

    **수정 (이식성 높은 버전):**
    ```sql
    SELECT grade,
           AVG(point_balance) AS avg_points
    FROM customers
    GROUP BY grade
    ORDER BY AVG(point_balance) DESC;
    ```

---

### 문제 17

다음 쿼리는 성별이 NULL이 아닌 고객만 조회하려 합니다. 논리가 잘못되었습니다.

```sql
SELECT name, gender
FROM customers
WHERE gender != NULL;
```

??? tip "힌트"
    문제 11과 같은 원리입니다. NULL과의 `!=` 비교도 결과가 NULL입니다.

??? success "정답"
    **오류:** `gender != NULL`은 항상 NULL(UNKNOWN)을 반환하므로 결과가 0행입니다. `IS NOT NULL`을 사용해야 합니다.

    **수정:**
    ```sql
    SELECT name, gender
    FROM customers
    WHERE gender IS NOT NULL;
    ```

---

### 문제 18

다음 쿼리는 주문 상태별 건수를 구하고, HAVING으로 필터링합니다. 하지만 의도와 다릅니다.

```sql
SELECT status, COUNT(*) AS order_count
FROM orders
GROUP BY status
HAVING status = 'confirmed';
```

??? tip "힌트"
    `HAVING`은 집계 결과를 필터링하는 용도입니다. 단순 칼럼 값 필터링에는 어떤 절을 써야 할까요?

??? success "정답"
    **오류:** `HAVING status = 'confirmed'`는 동작은 하지만, `HAVING`은 집계 함수 조건에 사용하는 것이 맞습니다. 단순 값 필터링은 `WHERE`가 적절합니다. `WHERE`를 사용하면 그룹화 전에 필터링되어 성능이 더 좋습니다.

    **수정:**
    ```sql
    SELECT status, COUNT(*) AS order_count
    FROM orders
    WHERE status = 'confirmed'
    GROUP BY status;
    ```

---

### 문제 19

다음 쿼리는 가격이 100만원 이상인 상품의 브랜드별 수를 구합니다. GROUP BY에 문제가 있습니다.

```sql
SELECT brand, name, COUNT(*) AS cnt
FROM products
WHERE price >= 1000000
GROUP BY brand;
```

??? tip "힌트"
    SELECT에 있는 비집계 칼럼은 모두 GROUP BY에 포함되어야 합니다. `name`은 어떤가요?

??? success "정답"
    **오류:** `name`이 SELECT에 있지만 `GROUP BY`에 포함되지 않았습니다. 브랜드별로 그룹화하면 각 그룹에 여러 name이 있으므로 어떤 name을 표시할지 알 수 없습니다. SQLite에서는 임의의 값이 선택되어 에러 없이 실행되지만 결과가 무의미합니다.

    **수정 (브랜드별 수만 필요한 경우):**
    ```sql
    SELECT brand, COUNT(*) AS cnt
    FROM products
    WHERE price >= 1000000
    GROUP BY brand;
    ```

---

### 문제 20

다음 쿼리는 연도별 주문 수를 구합니다. 결과가 이상합니다.

```sql
SELECT ordered_at AS year, COUNT(*) AS order_count
FROM orders
GROUP BY ordered_at;
```

??? tip "힌트"
    `ordered_at`에는 날짜와 시간이 함께 저장되어 있습니다. 연도별로 그룹화하려면?

??? success "정답"
    **오류:** `ordered_at`은 `2024-03-15 14:30:00` 같은 전체 타임스탬프입니다. 이것으로 GROUP BY하면 거의 모든 행이 별도의 그룹이 됩니다. 연도만 추출해야 합니다.

    **수정:**
    ```sql
    SELECT SUBSTR(ordered_at, 1, 4) AS year, COUNT(*) AS order_count
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```

---

## 실전 (21~30)

미묘한(Subtle) 오류를 찾습니다.

---

### 문제 21

다음 쿼리는 상품의 마진율(%)을 구합니다. 일부 상품에서 마진율이 0%로 나옵니다.

```sql
SELECT name, price, cost_price,
       (price - cost_price) / price * 100 AS margin_pct
FROM products
WHERE is_active = 1
LIMIT 10;
```

??? tip "힌트"
    SQLite에서 정수끼리 나누면 결과가 어떻게 되나요?

??? success "정답"
    **오류:** SQLite에서 정수 나눗셈은 소수점을 버립니다. `price`와 `cost_price`가 정수인 경우, `(price - cost_price) / price`가 0이 될 수 있습니다. 예: `(100 - 80) / 100 = 0` (정수 나눗셈).

    **수정:**
    ```sql
    SELECT name, price, cost_price,
           ROUND((price - cost_price) * 100.0 / price, 1) AS margin_pct
    FROM products
    WHERE is_active = 1
    LIMIT 10;
    ```

    > `100.0`을 곱하거나 `* 1.0`을 붙여 실수 연산을 강제합니다.

---

### 문제 22

다음 쿼리는 CASE 표현식에서 ELSE가 빠져 있습니다. 어떤 문제가 발생할까요?

```sql
SELECT name, price,
       CASE
           WHEN price < 100000 THEN '저가'
           WHEN price < 500000 THEN '중저가'
           WHEN price < 1000000 THEN '중가'
       END AS price_tier
FROM products;
```

??? tip "힌트"
    가격이 100만원 이상인 상품은 어떤 값이 될까요?

??? success "정답"
    **오류:** `ELSE`가 없으면 어떤 `WHEN` 조건에도 해당하지 않는 행은 `NULL`이 반환됩니다. 가격이 100만원 이상인 상품의 `price_tier`가 `NULL`이 됩니다.

    **수정:**
    ```sql
    SELECT name, price,
           CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier
    FROM products;
    ```

---

### 문제 23

다음 쿼리는 HAVING에서 별칭을 사용합니다. 에러가 발생할 수 있습니다.

```sql
SELECT brand, COUNT(*) AS cnt
FROM products
GROUP BY brand
HAVING cnt >= 10;
```

??? tip "힌트"
    SQLite에서는 HAVING에서 별칭을 사용할 수 있지만, MySQL, PostgreSQL 등에서는?

??? success "정답"
    **오류:** SQLite에서는 동작하지만, 대부분의 데이터베이스(MySQL, PostgreSQL, SQL Server)에서는 `HAVING`절에서 SELECT 별칭을 인식하지 못합니다. `HAVING`에서는 집계 함수를 직접 사용해야 합니다.

    **수정:**
    ```sql
    SELECT brand, COUNT(*) AS cnt
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10;
    ```

---

### 문제 24

다음 쿼리는 주문에서 할인율을 계산합니다. 0으로 나누는 오류가 발생할 수 있습니다.

```sql
SELECT order_number,
       total_amount,
       discount_amount,
       ROUND(discount_amount * 100.0 / total_amount, 1) AS discount_rate
FROM orders
ORDER BY discount_rate DESC
LIMIT 10;
```

??? tip "힌트"
    `total_amount`가 0인 주문이 있다면 어떻게 될까요?

??? success "정답"
    **오류:** `total_amount`가 0이면 0으로 나누기(division by zero) 오류가 발생합니다. SQLite에서는 에러 대신 NULL을 반환하지만, 의도치 않은 결과입니다.

    **수정:**
    ```sql
    SELECT order_number,
           total_amount,
           discount_amount,
           CASE
               WHEN total_amount = 0 THEN 0
               ELSE ROUND(discount_amount * 100.0 / total_amount, 1)
           END AS discount_rate
    FROM orders
    ORDER BY discount_rate DESC
    LIMIT 10;
    ```

---

### 문제 25

다음 쿼리는 2024년 주문의 월별 통계를 구합니다. 월 정렬이 이상합니다.

```sql
SELECT SUBSTR(ordered_at, 6, 2) AS month,
       COUNT(*) AS order_count
FROM orders
WHERE ordered_at LIKE '2024%'
GROUP BY month
ORDER BY order_count DESC;
```

??? tip "힌트"
    "월별 통계"라면 1월부터 12월까지 시간 순서로 보는 것이 자연스럽습니다. 현재 정렬 기준은?

??? success "정답"
    **오류:** `ORDER BY order_count DESC`로 건수 기준 내림차순 정렬하고 있습니다. 월별 추이를 보려면 월 순서대로 정렬해야 합니다.

    **수정:**
    ```sql
    SELECT SUBSTR(ordered_at, 6, 2) AS month,
           COUNT(*) AS order_count
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```

---

### 문제 26

다음 쿼리는 고객 등급별 평균 적립금과 총 적립금을 구합니다. ROUND가 한 곳에만 적용되어 있습니다.

```sql
SELECT grade,
       ROUND(AVG(point_balance)) AS avg_points,
       SUM(point_balance) AS total_points,
       COUNT(*) AS customer_count,
       AVG(point_balance) AS avg_points_raw
FROM customers
GROUP BY grade;
```

??? tip "힌트"
    같은 값(`AVG(point_balance)`)을 두 번 조회하면서 하나는 ROUND, 하나는 원본입니다. 이것 자체는 오류가 아니지만, `avg_points_raw`에 소수점 이하 긴 숫자가 표시됩니다.

??? success "정답"
    **오류:** `avg_points_raw`가 불필요한 중복이며, 반올림 없이 표시됩니다. 같은 칼럼을 두 번 계산하는 것은 비효율적이고 혼란을 줍니다.

    **수정:**
    ```sql
    SELECT grade,
           ROUND(AVG(point_balance)) AS avg_points,
           SUM(point_balance) AS total_points,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade;
    ```

---

### 문제 27

다음 쿼리는 상품명에 '블랙'이나 '화이트'가 포함된 상품을 찾습니다. 결과가 예상보다 많습니다.

```sql
SELECT name, price
FROM products
WHERE name LIKE '%블랙%'
   OR name LIKE '%화이트%'
   AND price > 500000;
```

??? tip "힌트"
    `AND`와 `OR`의 연산자 우선순위를 확인하세요. `OR`과 `AND` 중 어느 것이 먼저 평가되나요?

??? success "정답"
    **오류:** `AND`가 `OR`보다 우선순위가 높습니다. 따라서 이 쿼리는 `name LIKE '%블랙%'` OR (`name LIKE '%화이트%'` AND `price > 500000`)으로 해석됩니다. '블랙' 상품은 가격과 관계없이 모두 포함됩니다.

    **수정 (두 조건 모두 50만원 초과):**
    ```sql
    SELECT name, price
    FROM products
    WHERE (name LIKE '%블랙%' OR name LIKE '%화이트%')
      AND price > 500000;
    ```

---

### 문제 28

다음 쿼리는 NULL을 포함한 칼럼의 합계를 구합니다. 결과가 예상과 다릅니다.

```sql
SELECT COUNT(*) AS total_orders,
       SUM(discount_amount) + SUM(shipping_fee) AS extra_charges,
       AVG(discount_amount + shipping_fee) AS avg_extra
FROM orders;
```

??? tip "힌트"
    `discount_amount`이나 `shipping_fee`가 NULL인 행이 있다면, `SUM`은 NULL을 무시하지만 `discount_amount + shipping_fee`는?

??? success "정답"
    **오류:** `SUM`은 NULL을 무시하지만, `discount_amount + shipping_fee`에서 어느 한쪽이 NULL이면 결과가 NULL이 됩니다. `AVG(discount_amount + shipping_fee)`는 해당 행을 건너뛰게 됩니다. 또한 `SUM(A) + SUM(B)`와 `SUM(A + B)`는 NULL 처리가 다릅니다.

    **수정:**
    ```sql
    SELECT COUNT(*) AS total_orders,
           SUM(COALESCE(discount_amount, 0)) + SUM(COALESCE(shipping_fee, 0)) AS extra_charges,
           AVG(COALESCE(discount_amount, 0) + COALESCE(shipping_fee, 0)) AS avg_extra
    FROM orders;
    ```

---

### 문제 29

다음 쿼리는 가격대별 상품 수를 구합니다. CASE 조건 순서에 문제가 있습니다.

```sql
SELECT CASE
           WHEN price >= 0 THEN '저가'
           WHEN price >= 100000 THEN '중저가'
           WHEN price >= 500000 THEN '중가'
           WHEN price >= 1000000 THEN '고가'
       END AS price_tier,
       COUNT(*) AS cnt
FROM products
GROUP BY price_tier;
```

??? tip "힌트"
    CASE는 위에서 아래로 순서대로 평가되며, 첫 번째로 TRUE인 조건에서 멈춥니다. 모든 상품의 가격은 0 이상입니다.

??? success "정답"
    **오류:** `price >= 0`이 모든 상품에 대해 TRUE이므로 모든 상품이 '저가'로 분류됩니다. CASE 조건은 큰 값부터 또는 범위를 명확히 지정해야 합니다.

    **수정:**
    ```sql
    SELECT CASE
               WHEN price >= 1000000 THEN '고가'
               WHEN price >= 500000 THEN '중가'
               WHEN price >= 100000 THEN '중저가'
               ELSE '저가'
           END AS price_tier,
           COUNT(*) AS cnt
    FROM products
    GROUP BY price_tier;
    ```

---

### 문제 30

다음 쿼리는 고객의 가입 연도별 데이터를 분석합니다. WHERE와 HAVING이 혼동되어 있습니다.

```sql
SELECT SUBSTR(created_at, 1, 4) AS join_year,
       grade,
       COUNT(*) AS customer_count,
       ROUND(AVG(point_balance)) AS avg_points
FROM customers
HAVING grade IN ('GOLD', 'VIP')
GROUP BY join_year, grade
HAVING COUNT(*) >= 50
ORDER BY join_year, grade;
```

??? tip "힌트"
    HAVING이 두 번 사용되었고, SQL 절의 순서도 틀렸습니다. 개별 행 필터링과 그룹 필터링을 구분하세요.

??? success "정답"
    **오류:** 세 가지 문제가 있습니다.
    1. `HAVING`이 `GROUP BY` 앞에 있습니다 (절 순서 오류).
    2. `HAVING`이 두 번 사용되었습니다.
    3. `grade IN ('GOLD', 'VIP')`는 개별 행 필터링이므로 `WHERE`를 사용해야 합니다.

    **수정:**
    ```sql
    SELECT SUBSTR(created_at, 1, 4) AS join_year,
           grade,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    WHERE grade IN ('GOLD', 'VIP')
    GROUP BY join_year, grade
    HAVING COUNT(*) >= 50
    ORDER BY join_year, grade;
    ```
