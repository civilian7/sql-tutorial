# 초급 연습: 고객 분석

`customers`, `customer_addresses` 테이블을 사용합니다. 필터링, 집계, GROUP BY를 연습하는 15문제입니다.

---

### 1. 전체 고객 수

활성 고객과 비활성 고객 수를 각각 구하세요.

**힌트:** `GROUP BY is_active`로 그룹화하고 `COUNT(*)`로 각 그룹의 수를 세세요.

??? success "정답"
    ```sql
    SELECT
        is_active,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY is_active;
    ```

---

### 2. 등급별 고객 수

고객 등급(grade)별 인원 수를 구하세요.

**힌트:** `GROUP BY grade`와 `COUNT(*)`를 사용하세요.

??? success "정답"
    ```sql
    SELECT grade, COUNT(*) AS cnt
    FROM customers
    GROUP BY grade
    ORDER BY cnt DESC;
    ```

---

### 3. VIP 고객

VIP 등급 고객의 이름, 이메일, 적립금을 적립금 내림차순으로 조회하세요.

**힌트:** `WHERE grade = 'VIP'`로 필터링하고 `ORDER BY point_balance DESC`로 정렬.

??? success "정답"
    ```sql
    SELECT name, email, point_balance
    FROM customers
    WHERE grade = 'VIP'
    ORDER BY point_balance DESC;
    ```

---

### 4. 최근 가입 고객 10명

가장 최근에 가입한 고객 10명의 이름, 가입일, 등급을 조회하세요.

**힌트:** `ORDER BY created_at DESC`로 최신순 정렬 후 `LIMIT 10`.

??? success "정답"
    ```sql
    SELECT name, created_at, grade
    FROM customers
    ORDER BY created_at DESC
    LIMIT 10;
    ```

---

### 5. 성별 비율

성별(gender)별 고객 수와 비율(%)을 구하세요. NULL도 포함합니다.

**힌트:** `COALESCE(gender, '미입력')`으로 NULL 처리. 비율은 `100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()`로 계산.

??? success "정답"
    ```sql
    SELECT
        COALESCE(gender, '미입력') AS gender,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM customers
    GROUP BY gender;
    ```

---

### 6. 적립금 상위 20명

적립금(point_balance)이 가장 많은 상위 20명의 이름, 등급, 적립금을 조회하세요.

**힌트:** `ORDER BY point_balance DESC`와 `LIMIT 20`을 사용하세요. 활성 고객만 대상.

??? success "정답"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    WHERE is_active = 1
    ORDER BY point_balance DESC
    LIMIT 20;
    ```

---

### 7. 생년월일 미입력 고객

생년월일(birth_date)이 NULL인 고객 수를 구하세요.

**힌트:** `WHERE birth_date IS NULL`로 NULL을 확인하세요. `= NULL`은 동작하지 않음.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS no_birthdate
    FROM customers
    WHERE birth_date IS NULL;
    ```

---

### 8. 연도별 가입자 수

가입 연도별 신규 고객 수를 구하세요.

**힌트:** `SUBSTR(created_at, 1, 4)`로 연도를 추출하고 `GROUP BY`로 그룹화.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 4) AS join_year,
        COUNT(*) AS new_customers
    FROM customers
    GROUP BY SUBSTR(created_at, 1, 4)
    ORDER BY join_year;
    ```

---

### 9. 한 번도 로그인하지 않은 고객

`last_login_at`이 NULL인 고객 수와 전체 대비 비율을 구하세요.

**힌트:** 비율은 서브쿼리 `(SELECT COUNT(*) FROM customers)`로 전체 수를 구해서 나누세요.

??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS never_logged_in,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct
    FROM customers
    WHERE last_login_at IS NULL;
    ```

---

### 10. 등급별 평균 적립금

등급별 평균 적립금과 최대 적립금을 구하세요.

**힌트:** `GROUP BY grade`와 `AVG(point_balance)`, `MAX(point_balance)`를 함께 사용하세요.

??? success "정답"
    ```sql
    SELECT
        grade,
        COUNT(*) AS cnt,
        ROUND(AVG(point_balance), 0) AS avg_points,
        MAX(point_balance) AS max_points
    FROM customers
    GROUP BY grade
    ORDER BY avg_points DESC;
    ```

---

### 11. 이메일 도메인 분석

고객 이메일의 도메인(@뒤)별 고객 수를 구하세요.

**힌트:** `SUBSTR(email, INSTR(email, '@') + 1)`로 `@` 뒤의 도메인을 추출하세요.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(email, INSTR(email, '@') + 1) AS domain,
        COUNT(*) AS cnt
    FROM customers
    GROUP BY domain
    ORDER BY cnt DESC
    LIMIT 10;
    ```

---

### 12. 배송지가 여러 개인 고객

배송지를 2개 이상 등록한 고객의 이름과 배송지 수를 조회하세요.

**힌트:** `customers`와 `customer_addresses`를 `JOIN`하고, `HAVING COUNT(...) >= 2`로 필터링.

??? success "정답"
    ```sql
    SELECT
        c.name,
        COUNT(a.id) AS address_count
    FROM customers AS c
    INNER JOIN customer_addresses AS a ON c.id = a.customer_id
    GROUP BY c.id, c.name
    HAVING COUNT(a.id) >= 2
    ORDER BY address_count DESC
    LIMIT 20;
    ```

---

### 13. 2024년 가입 고객 중 VIP/GOLD

2024년에 가입한 고객 중 등급이 VIP 또는 GOLD인 고객의 이름, 가입일, 등급을 조회하세요.

**힌트:** `LIKE '2024%'`로 연도 필터링, `IN ('VIP', 'GOLD')`로 등급 필터링. 두 조건을 `AND`로 결합.

??? success "정답"
    ```sql
    SELECT name, created_at, grade
    FROM customers
    WHERE created_at LIKE '2024%'
      AND grade IN ('VIP', 'GOLD')
    ORDER BY created_at;
    ```

---

### 14. 월별 가입 추이 (2024)

2024년 월별 가입자 수를 구하세요.

**힌트:** `SUBSTR(created_at, 1, 7)`로 'YYYY-MM' 형태를 추출하고 `GROUP BY`로 월별 집계.

??? success "정답"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 7) AS month,
        COUNT(*) AS signups
    FROM customers
    WHERE created_at LIKE '2024%'
    GROUP BY SUBSTR(created_at, 1, 7)
    ORDER BY month;
    ```

---

### 15. 적립금 구간별 분포

적립금을 0, 1~1000, 1001~5000, 5001~10000, 10001 이상으로 나누어 각 구간의 고객 수를 구하세요.

**힌트:** `CASE WHEN`으로 적립금 구간을 분류한 뒤 `GROUP BY`와 `COUNT(*)`로 집계. `ORDER BY MIN(point_balance)`로 구간 순 정렬.

??? success "정답"
    ```sql
    SELECT
        CASE
            WHEN point_balance = 0 THEN '없음'
            WHEN point_balance <= 1000 THEN '1~1,000'
            WHEN point_balance <= 5000 THEN '1,001~5,000'
            WHEN point_balance <= 10000 THEN '5,001~10,000'
            ELSE '10,001 이상'
        END AS point_range,
        COUNT(*) AS cnt
    FROM customers
    GROUP BY point_range
    ORDER BY MIN(point_balance);
    ```
