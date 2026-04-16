# 고객 분석

#### :material-database: 사용 테이블


`customers` — 고객 (등급, 포인트, 가입채널)<br>

`customer_addresses` — 배송지 (주소, 기본 여부)<br>

`orders` — 주문 (상태, 금액, 일시)<br>

`products` — 상품 (이름, 가격, 재고, 브랜드)<br>

`tags` — 태그 (이름, 카테고리)<br>

`product_tags` — 상품-태그 연결<br>



**:material-book-open-variant: 학습 범위:** `SELECT`, `WHERE`, `GROUP BY`, `COUNT`, `AVG`, `MAX`, `COALESCE`, `SUBSTR`, `INSTR`, `JOIN`, `HAVING`, `LIKE`, `IN`, `CASE WHEN`


---


### 1. 활성 고객과 비활성 고객 수를 각각 구하세요.


활성 고객과 비활성 고객 수를 각각 구하세요.


**힌트 1:** GROUP BY is_active로 그룹화하고 COUNT(*)로 각 그룹의 수를 세세요


??? success "정답"
    ```sql
    SELECT
        is_active,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY is_active;
    ```


---


### 2. 고객 등급(grade)별 인원 수를 구하세요.


고객 등급(grade)별 인원 수를 구하세요.


**힌트 1:** GROUP BY grade와 COUNT(*)를 사용하세요


??? success "정답"
    ```sql
    SELECT grade, COUNT(*) AS cnt
    FROM customers
    GROUP BY grade
    ORDER BY cnt DESC;
    ```


---


### 3. VIP 등급 고객의 이름, 이메일, 적립금을 적립금 내림차순으로 조회하세요.


VIP 등급 고객의 이름, 이메일, 적립금을 적립금 내림차순으로 조회하세요.


**힌트 1:** WHERE grade = 'VIP'로 필터링하고 ORDER BY point_balance DESC로 정렬


??? success "정답"
    ```sql
    SELECT name, email, point_balance
    FROM customers
    WHERE grade = 'VIP'
    ORDER BY point_balance DESC;
    ```


---


### 4. 가장 최근에 가입한 고객 10명의 이름, 가입일, 등급을 조회하세요.


가장 최근에 가입한 고객 10명의 이름, 가입일, 등급을 조회하세요.


**힌트 1:** ORDER BY created_at DESC로 최신순 정렬 후 LIMIT 10


??? success "정답"
    ```sql
    SELECT name, created_at, grade
    FROM customers
    ORDER BY created_at DESC
    LIMIT 10;
    ```


---


### 5. 성별(gender)별 고객 수와 비율(%)을 구하세요. NULL도 포함합니다.


성별(gender)별 고객 수와 비율(%)을 구하세요. NULL도 포함합니다.


**힌트 1:** COALESCE(gender, '미입력')으로 NULL 처리. 비율은 100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()로 계산


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


### 6. 적립금(point_balance)이 가장 많은 상위 20명의 이름, 등급, 적립금을 조회하세요.


적립금(point_balance)이 가장 많은 상위 20명의 이름, 등급, 적립금을 조회하세요.


**힌트 1:** ORDER BY point_balance DESC와 LIMIT 20을 사용하세요. 활성 고객만 대상


??? success "정답"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    WHERE is_active = 1
    ORDER BY point_balance DESC
    LIMIT 20;
    ```


---


### 7. 생년월일(birth_date)이 NULL인 고객 수를 구하세요.


생년월일(birth_date)이 NULL인 고객 수를 구하세요.


**힌트 1:** WHERE birth_date IS NULL로 NULL을 확인하세요. = NULL은 동작하지 않음


??? success "정답"
    ```sql
    SELECT COUNT(*) AS no_birthdate
    FROM customers
    WHERE birth_date IS NULL;
    ```


---


### 8. 가입 연도별 신규 고객 수를 구하세요.


가입 연도별 신규 고객 수를 구하세요.


**힌트 1:** SUBSTR(created_at, 1, 4)로 연도를 추출하고 GROUP BY로 그룹화


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


### 9. last_login_at이 NULL인 고객 수와 전체 대비 비율을 구하세요.


last_login_at이 NULL인 고객 수와 전체 대비 비율을 구하세요.


**힌트 1:** 비율은 서브쿼리 (SELECT COUNT(*) FROM customers)로 전체 수를 구해서 나누세요


??? success "정답"
    ```sql
    SELECT
        COUNT(*) AS never_logged_in,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct
    FROM customers
    WHERE last_login_at IS NULL;
    ```


---


### 10. 등급별 평균 적립금과 최대 적립금을 구하세요.


등급별 평균 적립금과 최대 적립금을 구하세요.


**힌트 1:** GROUP BY grade와 AVG(point_balance), MAX(point_balance)를 함께 사용하세요


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


### 11. 고객 이메일의 도메인(@뒤)별 고객 수를 구하세요.


고객 이메일의 도메인(@뒤)별 고객 수를 구하세요.


**힌트 1:** SUBSTR(email, INSTR(email, '@') + 1)로 @ 뒤의 도메인을 추출하세요


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


### 12. 배송지를 2개 이상 등록한 고객의 이름과 배송지 수를 조회하세요.


배송지를 2개 이상 등록한 고객의 이름과 배송지 수를 조회하세요.


**힌트 1:** customers와 customer_addresses를 JOIN하고, HAVING COUNT(...) >= 2로 필터링


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


### 13. 2024년에 가입한 고객 중 등급이 VIP 또는 GOLD인 고객의 이름, 가입일, 등급을 조회하세요.


2024년에 가입한 고객 중 등급이 VIP 또는 GOLD인 고객의 이름, 가입일, 등급을 조회하세요.


**힌트 1:** LIKE '2024%'로 연도 필터링, IN ('VIP', 'GOLD')로 등급 필터링. 두 조건을 AND로 결합


??? success "정답"
    ```sql
    SELECT name, created_at, grade
    FROM customers
    WHERE created_at LIKE '2024%'
      AND grade IN ('VIP', 'GOLD')
    ORDER BY created_at;
    ```


---


### 14. 2024년 월별 가입자 수를 구하세요.


2024년 월별 가입자 수를 구하세요.


**힌트 1:** SUBSTR(created_at, 1, 7)로 'YYYY-MM' 형태를 추출하고 GROUP BY로 월별 집계


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


### 15. 적립금을 0, 1~1000, 1001~5000, 5001~10000, 10001 이상으로 나누어 각 구간의 


적립금을 0, 1~1000, 1001~5000, 5001~10000, 10001 이상으로 나누어 각 구간의 고객 수를 구하세요.


**힌트 1:** CASE WHEN으로 적립금 구간을 분류한 뒤 GROUP BY와 COUNT(*)로 집계. ORDER BY MIN(point_balance)로 구간 순 정렬


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


---


### 16. 다중 태그 상품 (GROUP BY HAVING)


태그가 3개 이상 달린 상품을 찾으세요.
상품명과 태그 목록(쉼표 구분)을 보여주세요.


**힌트 1:** `product_tags` GROUP BY `product_id`. `HAVING COUNT(*) >= 3`. `GROUP_CONCAT(t.name, ', ')`로 태그 목록 표시.


??? success "정답"

    === "SQLite"
        ```sql
        SELECT
        p.name AS product_name,
        p.brand,
        COUNT(pt.tag_id) AS tag_count,
        GROUP_CONCAT(t.name, ', ') AS tags
    FROM product_tags AS pt
    INNER JOIN products AS p ON pt.product_id = p.id
    INNER JOIN tags     AS t ON pt.tag_id     = t.id
    GROUP BY p.id, p.name, p.brand
    HAVING COUNT(pt.tag_id) >= 3
    ORDER BY tag_count DESC
    LIMIT 20;
        ```

    === "MySQL"
        ```sql
        SELECT
        p.name AS product_name,
        p.brand,
        COUNT(pt.tag_id) AS tag_count,
        GROUP_CONCAT(t.name SEPARATOR ', ') AS tags
    FROM product_tags AS pt
    INNER JOIN products AS p ON pt.product_id = p.id
    INNER JOIN tags     AS t ON pt.tag_id     = t.id
    GROUP BY p.id, p.name, p.brand
    HAVING COUNT(pt.tag_id) >= 3
    ORDER BY tag_count DESC
    LIMIT 20;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
        p.name AS product_name,
        p.brand,
        COUNT(pt.tag_id) AS tag_count,
        STRING_AGG(t.name, ', ') AS tags
    FROM product_tags AS pt
    INNER JOIN products AS p ON pt.product_id = p.id
    INNER JOIN tags     AS t ON pt.tag_id     = t.id
    GROUP BY p.id, p.name, p.brand
    HAVING COUNT(pt.tag_id) >= 3
    ORDER BY tag_count DESC
    LIMIT 20;
        ```

    === "Oracle"
        ```sql
        SELECT
        p.name AS product_name,
        p.brand,
        COUNT(pt.tag_id) AS tag_count,
        LISTAGG(t.name, ', ') WITHIN GROUP (ORDER BY t.name) AS tags
    FROM product_tags pt
    INNER JOIN products p ON pt.product_id = p.id
    INNER JOIN tags     t ON pt.tag_id     = t.id
    GROUP BY p.id, p.name, p.brand
    HAVING COUNT(pt.tag_id) >= 3
    ORDER BY tag_count DESC
    FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        SELECT TOP 20
        p.name AS product_name,
        p.brand,
        COUNT(pt.tag_id) AS tag_count,
        STRING_AGG(t.name, ', ') AS tags
    FROM product_tags AS pt
    INNER JOIN products AS p ON pt.product_id = p.id
    INNER JOIN tags     AS t ON pt.tag_id     = t.id
    GROUP BY p.id, p.name, p.brand
    HAVING COUNT(pt.tag_id) >= 3
    ORDER BY tag_count DESC;
        ```


---


### 17. 가입 경로별 고객 분포


고객의 가입 경로(acquisition_channel)별로 고객 수, 비율, 평균 구매 금액을 보여주세요.


**힌트 1:** `customers.acquisition_channel` 사용 (NULL 가능). `COALESCE`로 NULL을 '미분류'로 표시. LEFT JOIN `orders`로 구매 금액 계산.


??? success "정답"
    ```sql
    WITH channel_stats AS (
        SELECT
            COALESCE(c.acquisition_channel, 'unknown') AS channel,
            COUNT(DISTINCT c.id) AS customer_count,
            COUNT(o.id) AS order_count,
            ROUND(COALESCE(SUM(o.total_amount), 0), 0) AS total_revenue
        FROM customers AS c
        LEFT JOIN orders AS o
            ON c.id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY COALESCE(c.acquisition_channel, 'unknown')
    )
    SELECT
        channel,
        customer_count,
        ROUND(100.0 * customer_count / SUM(customer_count) OVER (), 1) AS pct,
        order_count,
        CASE WHEN customer_count > 0
            THEN ROUND(1.0 * total_revenue / customer_count, 0)
            ELSE 0
        END AS avg_revenue_per_customer
    FROM channel_stats
    ORDER BY customer_count DESC;
    ```


---
