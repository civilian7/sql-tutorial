# NULL 처리

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `customers` — 고객 (등급, 포인트, 가입채널)<br>
    `orders` — 주문 (상태, 금액, 일시)<br>
    `products` — 상품 (이름, 가격, 재고, 브랜드)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    `IS NULL`<br>
    `IS NOT NULL`<br>
    `COALESCE`<br>
    `IFNULL`<br>
    NULL과 집계 함수<br>
    NULL 정렬

</div>

!!! info "시작하기 전에"
    이 연습은 **입문 1~6강**에서 배운 내용을 사용합니다.
    JOIN, 서브쿼리, CASE, 윈도우 함수는 사용하지 않습니다.

---

## 기초 (1~10)

IS NULL, IS NOT NULL, COALESCE의 기본 사용법을 연습합니다.

---

### 문제 1

**생년월일(`birth_date`)이 없는 고객의 이름과 이메일을 조회하세요.**

??? tip "힌트"
    NULL 값을 찾으려면 `= NULL`이 아니라 `IS NULL`을 사용해야 합니다.

??? success "정답"
    ```sql
    SELECT name, email
    FROM customers
    WHERE birth_date IS NULL;
    ```

---

### 문제 2

**성별(`gender`)이 입력되어 있는 고객의 수를 구하세요.**

??? tip "힌트"
    `IS NOT NULL`로 값이 있는 행만 필터링한 뒤 `COUNT(*)`로 셉니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS gender_filled_count
    FROM customers
    WHERE gender IS NOT NULL;
    ```

---

### 문제 3

**한 번도 로그인하지 않은(`last_login_at`이 NULL인) 고객의 이름, 등급, 가입일을 조회하세요.**

??? tip "힌트"
    `last_login_at IS NULL`로 로그인 기록이 없는 고객을 찾습니다.

??? success "정답"
    ```sql
    SELECT name, grade, created_at
    FROM customers
    WHERE last_login_at IS NULL;
    ```

---

### 문제 4

**배송 요청사항(`notes`)이 있는 주문의 주문번호와 요청사항을 최근 주문 순으로 10건 조회하세요.**

??? tip "힌트"
    `IS NOT NULL`로 notes가 비어있지 않은 주문만 필터링합니다.

??? success "정답"
    ```sql
    SELECT order_number, notes
    FROM orders
    WHERE notes IS NOT NULL
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```

---

### 문제 5

**취소된 주문(`cancelled_at`이 NULL이 아닌)의 수를 구하세요.**

??? tip "힌트"
    `cancelled_at IS NOT NULL`이면 취소 일시가 기록된, 즉 취소된 주문입니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS cancelled_count
    FROM orders
    WHERE cancelled_at IS NOT NULL;
    ```

---

### 문제 6

**상품의 사양 정보(`specs`)가 없는 상품의 이름과 브랜드를 조회하세요.**

??? tip "힌트"
    `specs IS NULL`로 사양 정보가 누락된 상품을 찾습니다.

??? success "정답"
    ```sql
    SELECT name, brand
    FROM products
    WHERE specs IS NULL;
    ```

---

### 문제 7

**고객의 이름과 성별을 조회하되, 성별이 NULL이면 '미입력'으로 표시하세요.**

??? tip "힌트"
    `COALESCE(칼럼, 대체값)`은 칼럼이 NULL일 때 대체값을 반환합니다.

??? success "정답"
    ```sql
    SELECT name, COALESCE(gender, '미입력') AS gender
    FROM customers;
    ```

---

### 문제 8

**주문의 주문번호와 배송 요청사항을 조회하되, 요청사항이 없으면 '없음'으로 표시하세요. 최근 10건만 조회합니다.**

??? tip "힌트"
    `IFNULL(notes, '없음')` 또는 `COALESCE(notes, '없음')`을 사용합니다. SQLite에서 둘 다 동작합니다.

??? success "정답"
    ```sql
    SELECT order_number, IFNULL(notes, '없음') AS notes
    FROM orders
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```

---

### 문제 9

**단종일(`discontinued_at`)이 있는 상품의 이름, 가격, 단종일을 조회하세요.**

??? tip "힌트"
    `discontinued_at IS NOT NULL`이면 단종된 상품입니다.

??? success "정답"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL;
    ```

---

### 문제 10

**구매 확정(`completed_at`)이 아직 되지 않은 주문 중 취소도 되지 않은 주문의 수를 구하세요.**

??? tip "힌트"
    `completed_at IS NULL AND cancelled_at IS NULL`로 두 칼럼 모두 NULL인 행을 찾습니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS pending_count
    FROM orders
    WHERE completed_at IS NULL
      AND cancelled_at IS NULL;
    ```

---

## 응용 (11~20)

COALESCE 활용, NULL과 집계 함수의 관계, NULL 정렬을 연습합니다.

---

### 문제 11

**고객의 이름, 생년월일, 성별을 조회하되 생년월일은 NULL이면 '정보없음', 성별은 NULL이면 '미선택'으로 표시하세요. 상위 20건만 조회합니다.**

??? tip "힌트"
    `COALESCE`를 각 칼럼에 개별 적용합니다.

??? success "정답"
    ```sql
    SELECT name,
           COALESCE(birth_date, '정보없음') AS birth_date,
           COALESCE(gender, '미선택') AS gender
    FROM customers
    LIMIT 20;
    ```

---

### 문제 12

**상품의 이름, 무게를 조회하되 무게(`weight_grams`)가 NULL이면 0으로 대체하세요. 무게가 무거운 순으로 10건만 조회합니다.**

??? tip "힌트"
    `COALESCE(weight_grams, 0)`으로 NULL을 0으로 대체한 뒤 정렬합니다.

??? success "정답"
    ```sql
    SELECT name, COALESCE(weight_grams, 0) AS weight_grams
    FROM products
    ORDER BY weight_grams DESC
    LIMIT 10;
    ```

---

### 문제 13

**전체 고객 수와 생년월일이 입력된 고객 수를 함께 조회하세요.**

??? tip "힌트"
    `COUNT(*)`는 모든 행을 세고, `COUNT(칼럼)`은 해당 칼럼이 NULL이 아닌 행만 셉니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_customers,
           COUNT(birth_date) AS has_birth_date
    FROM customers;
    ```

    > `COUNT(birth_date)`는 birth_date가 NULL인 행을 자동으로 제외합니다.

---

### 문제 14

**전체 주문 수, 배송 요청사항이 있는 주문 수, 구매 확정된 주문 수를 한 번에 조회하세요.**

??? tip "힌트"
    `COUNT(notes)`, `COUNT(completed_at)`처럼 각 칼럼에 `COUNT`를 적용하면 NULL이 아닌 행만 셉니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_orders,
           COUNT(notes) AS has_notes,
           COUNT(completed_at) AS completed
    FROM orders;
    ```

---

### 문제 15

**고객을 마지막 로그인일 기준 최근 순으로 정렬하되, 로그인 기록이 없는(NULL) 고객은 맨 뒤에 표시하세요. 상위 20건만 조회합니다.**

??? tip "힌트"
    SQLite에서 `ORDER BY 칼럼 DESC`를 사용하면 NULL이 맨 뒤로 갑니다. 또는 `ORDER BY 칼럼 IS NULL, 칼럼 DESC`로 명시적으로 제어합니다.

??? success "정답"
    ```sql
    SELECT name, last_login_at
    FROM customers
    ORDER BY last_login_at IS NULL, last_login_at DESC
    LIMIT 20;
    ```

    > `last_login_at IS NULL`은 NULL이면 1, 아니면 0을 반환합니다. 0이 먼저 정렬되므로 NULL이 아닌 행이 위에 옵니다.

---

### 문제 16

**상품을 단종일 기준 오래된 순으로 정렬하되, 단종되지 않은 상품(NULL)은 맨 뒤에 표시하세요. 상위 10건만 조회합니다.**

??? tip "힌트"
    `ORDER BY discontinued_at IS NULL, discontinued_at ASC`로 NULL을 뒤로 보냅니다.

??? success "정답"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    ORDER BY discontinued_at IS NULL, discontinued_at ASC
    LIMIT 10;
    ```

---

### 문제 17

**등급별 고객 수와 생년월일 입력률(%)을 구하세요. 입력률은 소수점 1자리까지 반올림합니다.**

??? tip "힌트"
    `COUNT(birth_date) * 100.0 / COUNT(*)`로 NULL이 아닌 비율을 계산합니다. `GROUP BY grade`로 등급별 집계합니다.

??? success "정답"
    ```sql
    SELECT grade,
           COUNT(*) AS total,
           COUNT(birth_date) AS has_birth,
           ROUND(COUNT(birth_date) * 100.0 / COUNT(*), 1) AS birth_rate_pct
    FROM customers
    GROUP BY grade
    ORDER BY birth_rate_pct DESC;
    ```

---

### 문제 18

**가입 경로(`acquisition_channel`)별 고객 수를 구하되, NULL인 경우 '미분류'로 표시하세요.**

??? tip "힌트"
    `COALESCE(acquisition_channel, '미분류')`를 SELECT와 GROUP BY 모두에 사용합니다.

??? success "정답"
    ```sql
    SELECT COALESCE(acquisition_channel, '미분류') AS channel,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY COALESCE(acquisition_channel, '미분류')
    ORDER BY customer_count DESC;
    ```

---

### 문제 19

**주문 상태별로 주문 수와 배송 요청사항 입력 비율(%)을 구하세요.**

??? tip "힌트"
    `COUNT(notes) * 100.0 / COUNT(*)`로 notes가 NULL이 아닌 비율을 계산합니다.

??? success "정답"
    ```sql
    SELECT status,
           COUNT(*) AS order_count,
           ROUND(COUNT(notes) * 100.0 / COUNT(*), 1) AS notes_rate_pct
    FROM orders
    GROUP BY status
    ORDER BY order_count DESC;
    ```

---

### 문제 20

**상품의 이름, 가격, 무게를 조회하되, 무게가 NULL이면 가격 기준 100g당 1,000원으로 추정한 무게(`price / 10`)를 표시하세요. 칼럼명은 `estimated_weight`로 지정합니다.**

??? tip "힌트"
    `COALESCE(weight_grams, 다른_계산식)`으로 NULL일 때만 대체 계산을 적용합니다.

??? success "정답"
    ```sql
    SELECT name,
           price,
           COALESCE(weight_grams, CAST(price / 10 AS INTEGER)) AS estimated_weight
    FROM products
    ORDER BY estimated_weight DESC
    LIMIT 10;
    ```

    > 실제 운영에서는 이런 추정치를 사용할 때 별도의 플래그 칼럼으로 추정값 여부를 구분합니다.

---

## 실전 (21~30)

NULL 분석, 데이터 품질 점검, NULL 안전 비교를 연습합니다.

---

### 문제 21

**고객 테이블에서 각 칼럼의 NULL 수를 한 번에 조회하세요. birth_date, gender, last_login_at, acquisition_channel의 NULL 수를 구합니다.**

??? tip "힌트"
    `COUNT(*) - COUNT(칼럼)`으로 해당 칼럼의 NULL 수를 계산합니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) - COUNT(birth_date) AS birth_null,
           COUNT(*) - COUNT(gender) AS gender_null,
           COUNT(*) - COUNT(last_login_at) AS login_null,
           COUNT(*) - COUNT(acquisition_channel) AS channel_null
    FROM customers;
    ```

---

### 문제 22

**고객 테이블에서 각 NULL 허용 칼럼의 결측률(%)을 구하세요. 소수점 1자리까지 표시합니다.**

??? tip "힌트"
    `(COUNT(*) - COUNT(칼럼)) * 100.0 / COUNT(*)`로 결측률을 계산합니다.

??? success "정답"
    ```sql
    SELECT ROUND((COUNT(*) - COUNT(birth_date)) * 100.0 / COUNT(*), 1) AS birth_missing_pct,
           ROUND((COUNT(*) - COUNT(gender)) * 100.0 / COUNT(*), 1) AS gender_missing_pct,
           ROUND((COUNT(*) - COUNT(last_login_at)) * 100.0 / COUNT(*), 1) AS login_missing_pct,
           ROUND((COUNT(*) - COUNT(acquisition_channel)) * 100.0 / COUNT(*), 1) AS channel_missing_pct
    FROM customers;
    ```

---

### 문제 23

**주문 테이블에서 notes, completed_at, cancelled_at 각각의 NULL 비율(%)을 구하세요.**

??? tip "힌트"
    문제 22와 동일한 패턴을 orders 테이블에 적용합니다.

??? success "정답"
    ```sql
    SELECT ROUND((COUNT(*) - COUNT(notes)) * 100.0 / COUNT(*), 1) AS notes_missing_pct,
           ROUND((COUNT(*) - COUNT(completed_at)) * 100.0 / COUNT(*), 1) AS completed_missing_pct,
           ROUND((COUNT(*) - COUNT(cancelled_at)) * 100.0 / COUNT(*), 1) AS cancelled_missing_pct
    FROM orders;
    ```

---

### 문제 24

**성별이 NULL인 고객의 등급별 분포를 구하세요. 등급별 수와 비율(%)을 표시합니다.**

??? tip "힌트"
    `WHERE gender IS NULL`로 필터링 후 `GROUP BY grade`로 집계합니다. 비율은 전체 NULL 고객 대비입니다.

??? success "정답"
    ```sql
    SELECT grade,
           COUNT(*) AS cnt,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM customers
    WHERE gender IS NULL
    GROUP BY grade
    ORDER BY cnt DESC;
    ```

    > 윈도우 함수를 아직 배우지 않았다면, 아래처럼 전체 수를 따로 계산해도 됩니다:

    ```sql
    SELECT grade,
           COUNT(*) AS cnt
    FROM customers
    WHERE gender IS NULL
    GROUP BY grade
    ORDER BY cnt DESC;
    ```

---

### 문제 25

**생년월일과 성별이 모두 NULL인 고객의 수를 구하세요. 그리고 생년월일 또는 성별 중 하나라도 NULL인 고객의 수도 함께 구하세요.**

??? tip "힌트"
    `AND`로 모두 NULL인 조건, `OR`로 하나라도 NULL인 조건을 만듭니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS total,
           SUM(CASE WHEN birth_date IS NULL AND gender IS NULL THEN 1 ELSE 0 END) AS both_null,
           SUM(CASE WHEN birth_date IS NULL OR gender IS NULL THEN 1 ELSE 0 END) AS any_null
    FROM customers;
    ```

    > CASE를 아직 배우지 않았다면 두 개의 쿼리로 나눠도 됩니다:

    ```sql
    -- 모두 NULL
    SELECT COUNT(*) AS both_null
    FROM customers
    WHERE birth_date IS NULL AND gender IS NULL;

    -- 하나라도 NULL
    SELECT COUNT(*) AS any_null
    FROM customers
    WHERE birth_date IS NULL OR gender IS NULL;
    ```

---

### 문제 26

**가입 경로가 NULL인 고객 중 VIP 등급의 수와, 가입 경로가 있는 고객 중 VIP 등급의 수를 비교하세요.**

??? tip "힌트"
    두 개의 `COUNT`에 각각 다른 `WHERE` 조건을 적용하거나, 하나의 쿼리에서 필터링된 COUNT를 사용합니다.

??? success "정답"
    ```sql
    SELECT '경로없음' AS channel_status,
           COUNT(*) AS vip_count
    FROM customers
    WHERE acquisition_channel IS NULL AND grade = 'VIP'
    UNION ALL
    SELECT '경로있음',
           COUNT(*)
    FROM customers
    WHERE acquisition_channel IS NOT NULL AND grade = 'VIP';
    ```

---

### 문제 27

**상품의 설명(`description`)과 사양(`specs`) 중 하나라도 NULL인 상품의 수를 구하고, 둘 다 NULL인 상품의 수도 함께 조회하세요.**

??? tip "힌트"
    `OR`와 `AND`를 조합하여 두 가지 조건을 만듭니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_products,
           SUM(CASE WHEN description IS NULL OR specs IS NULL THEN 1 ELSE 0 END) AS any_null,
           SUM(CASE WHEN description IS NULL AND specs IS NULL THEN 1 ELSE 0 END) AS both_null
    FROM products;
    ```

    > CASE를 아직 배우지 않았다면 별도의 쿼리로 실행하세요:

    ```sql
    SELECT COUNT(*) FROM products WHERE description IS NULL OR specs IS NULL;
    SELECT COUNT(*) FROM products WHERE description IS NULL AND specs IS NULL;
    ```

---

### 문제 28

**연도별 주문 수와 배송 요청사항 작성률(%)을 구하세요. `SUBSTR(ordered_at, 1, 4)`로 연도를 추출합니다.**

??? tip "힌트"
    `GROUP BY SUBSTR(ordered_at, 1, 4)`로 연도별 그룹화 후 `COUNT(notes) * 100.0 / COUNT(*)`로 작성률을 계산합니다.

??? success "정답"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 4) AS year,
           COUNT(*) AS order_count,
           ROUND(COUNT(notes) * 100.0 / COUNT(*), 1) AS notes_rate_pct
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```

    > 연도별 배송 요청사항 작성률 추이를 통해 고객 행동 변화를 파악할 수 있습니다.

---

### 문제 29

**상품 무게(`weight_grams`)가 NULL인 상품의 브랜드별 수를 구하고, 5개 이상인 브랜드만 조회하세요.**

??? tip "힌트"
    `WHERE weight_grams IS NULL`로 필터링 후 `GROUP BY brand`, `HAVING COUNT(*) >= 5`로 조건을 겁니다.

??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS null_weight_count
    FROM products
    WHERE weight_grams IS NULL
    GROUP BY brand
    HAVING COUNT(*) >= 5
    ORDER BY null_weight_count DESC;
    ```

---

### 문제 30

**고객의 데이터 완성도를 점수로 계산하세요. birth_date, gender, last_login_at, acquisition_channel 4개 칼럼 중 NULL이 아닌 칼럼 수를 세어 0~4점으로 표시합니다. 점수별 고객 수를 구하세요.**

??? tip "힌트"
    `(칼럼 IS NOT NULL)`은 SQLite에서 TRUE=1, FALSE=0을 반환합니다. 4개를 더하면 완성도 점수가 됩니다.

??? success "정답"
    ```sql
    SELECT (birth_date IS NOT NULL)
         + (gender IS NOT NULL)
         + (last_login_at IS NOT NULL)
         + (acquisition_channel IS NOT NULL) AS completeness_score,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY completeness_score
    ORDER BY completeness_score;
    ```

    > 점수가 0인 고객은 선택 정보를 하나도 입력하지 않은 것이고, 4인 고객은 모든 정보를 입력한 것입니다. 이 분석은 고객 프로필 보완 캠페인의 기초 자료로 활용됩니다.
