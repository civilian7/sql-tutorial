# 고객 분석

!!! info "사용 테이블"

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `customer_addresses` — 배송지 (주소, 기본 여부)  

    `orders` — 주문 (상태, 금액, 일시)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `tags` — 태그 (이름, 카테고리)  

    `product_tags` — 상품-태그 연결  



!!! abstract "학습 범위"

    `SELECT`, `WHERE`, `GROUP BY`, `COUNT`, `AVG`, `MAX`, `COALESCE`, `SUBSTR`, `INSTR`, `JOIN`, `HAVING`, `LIKE`, `IN`, `CASE WHEN`



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


    **실행 결과** (2행)

    | is_active | customer_count |
    |---|---|
    | 0 | 1570 |
    | 1 | 3660 |


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


    **실행 결과** (4행)

    | grade | cnt |
    |---|---|
    | BRONZE | 3859 |
    | GOLD | 524 |
    | SILVER | 479 |
    | VIP | 368 |


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


    **실행 결과** (총 368행 중 상위 7행)

    | name | email | point_balance |
    |---|---|---|
    | 박정수 | user226@testmail.kr | 3,955,828 |
    | 김병철 | user97@testmail.kr | 3,518,880 |
    | 강명자 | user162@testmail.kr | 2,450,166 |
    | 정유진 | user356@testmail.kr | 2,383,491 |
    | 김성민 | user227@testmail.kr | 2,297,542 |
    | 이미정 | user549@testmail.kr | 2,276,622 |
    | 이영자 | user98@testmail.kr | 2,218,590 |


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


    **실행 결과** (총 10행 중 상위 7행)

    | name | created_at | grade |
    |---|---|---|
    | 이은지 | 2025-12-30 20:49:59 | BRONZE |
    | 박성호 | 2025-12-30 18:50:02 | BRONZE |
    | 김서연 | 2025-12-30 10:18:14 | BRONZE |
    | 김영순 | 2025-12-30 06:02:53 | BRONZE |
    | 문하은 | 2025-12-30 05:59:32 | BRONZE |
    | 한윤서 | 2025-12-30 05:43:21 | BRONZE |
    | 강성진 | 2025-12-29 17:18:36 | BRONZE |


---


### 5. 성별(gender)별 고객 수와 비율(%)을 구하세요. NULL도 포함합니다.


성별(gender)별 고객 수와 비율(%)을 구하세요. NULL도 포함합니다.


**힌트 1:** COALESCE(gender, '미입력')으로 NULL 처리. 비율은 100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers)로 계산


??? success "정답"
    ```sql
    SELECT
        COALESCE(gender, '미입력') AS gender,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct
    FROM customers
    GROUP BY gender;
    ```


    **실행 결과** (3행)

    | gender | cnt | pct |
    |---|---|---|
    | 미입력 | 529 | 10.10 |
    | F | 1669 | 31.90 |
    | M | 3032 | 58.00 |


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


    **실행 결과** (총 20행 중 상위 7행)

    | name | grade | point_balance |
    |---|---|---|
    | 박정수 | VIP | 3,955,828 |
    | 김병철 | VIP | 3,518,880 |
    | 강명자 | VIP | 2,450,166 |
    | 정유진 | VIP | 2,383,491 |
    | 김성민 | VIP | 2,297,542 |
    | 이미정 | VIP | 2,276,622 |
    | 이영자 | VIP | 2,218,590 |


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


    **실행 결과** (1행)

    | no_birthdate |
    |---|
    | 738 |


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


    **실행 결과** (총 10행 중 상위 7행)

    | join_year | new_customers |
    |---|---|
    | 2016 | 100 |
    | 2017 | 180 |
    | 2018 | 300 |
    | 2019 | 450 |
    | 2020 | 700 |
    | 2021 | 800 |
    | 2022 | 650 |


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


    **실행 결과** (1행)

    | never_logged_in | pct |
    |---|---|
    | 281 | 5.40 |


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


    **실행 결과** (4행)

    | grade | cnt | avg_points | max_points |
    |---|---|---|---|
    | VIP | 368 | 407,015.00 | 3,955,828 |
    | GOLD | 524 | 147,711.00 | 2,007,717 |
    | SILVER | 479 | 95,042.00 | 1,266,757 |
    | BRONZE | 3859 | 16,779.00 | 956,983 |


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


    **실행 결과** (1행)

    | domain | cnt |
    |---|---|
    | testmail.kr | 5230 |


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


    **실행 결과** (총 20행 중 상위 7행)

    | name | address_count |
    |---|---|
    | 정준호 | 3 |
    | 김경수 | 3 |
    | 김민재 | 3 |
    | 장준서 | 3 |
    | 윤유진 | 3 |
    | 박수빈 | 3 |
    | 윤명자 | 3 |


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


    **실행 결과** (총 140행 중 상위 7행)

    | name | created_at | grade |
    |---|---|---|
    | 이도현 | 2024-01-05 14:23:16 | GOLD |
    | 성영환 | 2024-01-07 05:39:40 | GOLD |
    | 박민재 | 2024-01-07 12:17:28 | VIP |
    | 이중수 | 2024-01-07 19:33:43 | VIP |
    | 이정숙 | 2024-01-11 06:40:22 | GOLD |
    | 임정순 | 2024-01-16 06:45:22 | GOLD |
    | 이종수 | 2024-01-23 05:29:21 | VIP |


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


    **실행 결과** (총 12행 중 상위 7행)

    | month | signups |
    |---|---|
    | 2024-01 | 52 |
    | 2024-02 | 48 |
    | 2024-03 | 71 |
    | 2024-04 | 53 |
    | 2024-05 | 43 |
    | 2024-06 | 68 |
    | 2024-07 | 62 |


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


    **실행 결과** (5행)

    | point_range | cnt |
    |---|---|
    | 없음 | 2506 |
    | 1~1,000 | 137 |
    | 1,001~5,000 | 344 |
    | 5,001~10,000 | 148 |
    | 10,001 이상 | 2095 |


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


    **실행 결과** (총 20행 중 상위 7행)

    | product_name | brand | tag_count | tags |
    |---|---|---|---|
    | Razer Blade 16 실버 | Razer | 8 | 방수/방진, 에르고노믹, 게이밍, 그래픽디자인, 서버/NAS, 휴대... |
    | Razer Blade 18 블랙 | Razer | 8 | USB-C, 터치스크린, 게이밍, 학생용, 서버/NAS, 휴대용, ... |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | ASUS | 7 | 저소음, QHD, FHD, DDR5, 휴대용, 하이엔드, 한정판 |
    | ASUS Dual RX 9070 실버 | ASUS | 7 | 블루투스, DDR5, 에르고노믹, 게이밍, 프리미엄, 오버클럭, 듀얼채널 |
    | ASUS ExpertBook B5 화이트 | ASUS | 7 | 모듈러, PCIe 5.0, 영상편집, 휴대용, 전문가용, 하이엔드,... |
    | ASUS ROG Swift OLED PG27AQDM 실버 | ASUS | 7 | 유선, 게이밍, 프로그래밍, 그래픽디자인, 입문자용, 하이엔드, 멀티코어 |
    | ASUS ROG Swift PG32UCDM 실버 | ASUS | 7 | USB-C, 4K, 핫스왑, 게이밍, 스트리밍, 전문가용, 프리미엄 |


---


### 17. 가입 경로별 고객 수와 비율


고객의 가입 경로(acquisition_channel)별로 고객 수와 비율(%)을 구하세요. NULL은 '미분류'로 표시합니다.


**힌트 1:** `COALESCE(acquisition_channel, '미분류')`로 NULL 처리. 비율은 `(SELECT COUNT(*) FROM customers)`로 전체 수를 구해 계산.


??? success "정답"
    ```sql
    SELECT
        COALESCE(acquisition_channel, '미분류') AS channel,
        COUNT(*) AS customer_count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct
    FROM customers
    GROUP BY COALESCE(acquisition_channel, '미분류')
    ORDER BY customer_count DESC;
    ```


    **실행 결과** (5행)

    | channel | customer_count | pct |
    |---|---|---|
    | search_ad | 1543 | 29.50 |
    | social | 1425 | 27.20 |
    | organic | 1146 | 21.90 |
    | referral | 708 | 13.50 |
    | direct | 408 | 7.80 |


---
