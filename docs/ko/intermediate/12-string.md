# 12강: 문자열 함수

[11강](11-datetime.md)에서 날짜/시간 함수로 기간을 계산하고 포맷을 바꾸는 법을 배웠습니다. 데이터 분석에서 '이메일 도메인별 고객 수'나 '상품명에서 브랜드 추출'같은 작업이 자주 필요합니다. 문자열 함수로 텍스트를 자르고, 바꾸고, 합칠 수 있습니다.

!!! note "이미 알고 계신다면"
    SUBSTR, REPLACE, CONCAT, LENGTH, UPPER/LOWER, TRIM에 익숙하다면 [13강: 숫자·변환·조건 함수](13-utility-functions.md)로 건너뛰세요.

문자열 함수는 데이터베이스마다 이름이나 인자 순서가 다른 경우가 많습니다. 이 강의에서는 SQLite를 기본으로 하되, 차이가 있는 부분에서 MySQL과 PostgreSQL 탭을 함께 보여줍니다.

## SUBSTR — 문자열 일부 추출

`SUBSTR(string, start, length)` — `start`는 1부터 시작합니다. `length`를 생략하면 끝까지 반환합니다.

```sql
-- 주문 타임스탬프에서 날짜 부분 추출
SELECT
    order_number,
    ordered_at,
    SUBSTR(ordered_at, 1, 10) AS order_date,
    SUBSTR(ordered_at, 1, 7)  AS year_month
FROM orders
LIMIT 5;
```

**결과:**

| order_number       | ordered_at          | order_date | year_month |
| ------------------ | ------------------- | ---------- | ---------- |
| ORD-20160101-00001 | 2016-01-17 03:39:08 | 2016-01-17 | 2016-01    |
| ORD-20160102-00002 | 2016-01-11 05:08:34 | 2016-01-11 | 2016-01    |
| ORD-20160102-00003 | 2016-01-09 15:08:34 | 2016-01-09 | 2016-01    |
| ...                | ...                 | ...        | ...        |

```sql
-- 주문 번호에서 연·월·일 파싱: ORD-20240315-00001
SELECT
    order_number,
    SUBSTR(order_number, 5, 4)  AS order_year,
    SUBSTR(order_number, 9, 2)  AS order_month,
    SUBSTR(order_number, 11, 2) AS order_day
FROM orders
LIMIT 3;
```

## LENGTH

`LENGTH(string)`는 문자 수를 반환합니다.

```sql
-- 이름이 유독 짧거나 긴 상품 찾기
SELECT name, LENGTH(name) AS name_length
FROM products
ORDER BY name_length DESC
LIMIT 5;
```

**결과:**

| name                                                             | name_length |
| ---------------------------------------------------------------- | ----------: |
| HP EliteBook 840 G10 블랙 [특별 한정판 에디션] 무상 보증 3년 연장 + 전용 파우치 증정 이벤트 |          64 |
| ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장    |          61 |
| ...                                                              | ...         |

## UPPER와 LOWER

```sql
-- 이메일 소문자 정규화, 등급 대문자 표시
SELECT
    name,
    LOWER(email) AS email_lower,
    UPPER(grade) AS grade_display
FROM customers
LIMIT 5;
```

**결과:**

| name | email_lower       | grade_display |
| ---- | ----------------- | ------------- |
| 정준호  | user1@testmail.kr | BRONZE        |
| 김경수  | user2@testmail.kr | VIP           |
| ...  | ...               | ...           |

## REPLACE

`REPLACE(string, find, replacement)`는 모든 일치 항목을 대체합니다.

```sql
-- 전화번호 마스킹: 뒷 4자리만 표시
SELECT
    name,
    REPLACE(
        REPLACE(phone, SUBSTR(phone, 1, 9), '***-****-'),
        SUBSTR(phone, 1, 9), '***-****-'
    ) AS masked_phone
FROM customers
LIMIT 3;
```

```sql
-- 밑줄이 포함된 상태값을 읽기 쉽게 변환
SELECT DISTINCT
    status,
    REPLACE(status, '_', ' ') AS status_readable
FROM orders;
```

**결과:**

| status    | status_readable |
| --------- | --------------- |
| cancelled | cancelled       |
| confirmed | confirmed       |
| ...       | ...             |

## 문자열 연결

=== "SQLite / PostgreSQL"
    ```sql
    -- Build a contact info string with ||
    SELECT
        name,
        phone || ' — ' || email AS contact_info
    FROM customers
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    -- Build a contact info string with CONCAT()
    SELECT
        name,
        CONCAT(phone, ' — ', email) AS contact_info
    FROM customers
    LIMIT 5;
    ```

**결과:**

| name | contact_info |
|------|--------------|
| 김민수 | 020-1234-5678 — k.minsu@testmail.kr |
| 이지은 | 020-9876-5432 — l.jieun@testmail.kr |

=== "SQLite / PostgreSQL"
    ```sql
    -- Display SKU with category prefix
    SELECT
        p.name,
        cat.name || '-' || p.sku AS display_sku
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    -- Display SKU with category prefix
    SELECT
        p.name,
        CONCAT(cat.name, '-', p.sku) AS display_sku
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LIMIT 5;
    ```

## 패턴 매칭 LIKE

2강에서 다뤘지만, 더 고급 패턴 예시를 소개합니다.

=== "SQLite"
    ```sql
    -- Users per email domain (after @)
    SELECT DISTINCT
        SUBSTR(email, INSTR(email, '@') + 1) AS domain,
        COUNT(*) AS users
    FROM customers
    GROUP BY domain
    ORDER BY users DESC
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    -- Users per email domain (after @)
    SELECT
        SUBSTRING(email, LOCATE('@', email) + 1) AS domain,
        COUNT(*) AS users
    FROM customers
    GROUP BY domain
    ORDER BY users DESC
    LIMIT 5;
    ```

=== "PostgreSQL"
    ```sql
    -- Users per email domain (after @)
    SELECT
        SUBSTRING(email FROM POSITION('@' IN email) + 1) AS domain,
        COUNT(*) AS users
    FROM customers
    GROUP BY domain
    ORDER BY users DESC
    LIMIT 5;
    ```

```sql
-- 모델 번호에 숫자가 포함된 상품
SELECT name
FROM products
WHERE name LIKE '%[0-9]%'   -- 표준 SQL 문법
-- SQLite에서는 문자 클래스에 GLOB 사용:
-- WHERE name GLOB '*[0-9]*'
LIMIT 5;
```

## TRIM, LTRIM, RTRIM

앞뒤의 공백(또는 지정한 문자)을 제거합니다.

```sql
-- 상품명의 실수로 들어간 공백 정리
SELECT
    name,
    TRIM(name)   AS cleaned_name,
    LENGTH(name) - LENGTH(TRIM(name)) AS extra_chars
FROM products
WHERE LENGTH(name) != LENGTH(TRIM(name));
```

## NULL과 문자열 연결

문자열 연결에서 가장 흔한 실수: **한쪽이 NULL이면 결과 전체가 NULL**입니다.

```sql
-- birth_date가 NULL인 고객이면 contact_info도 NULL!
SELECT
    name || ' (' || birth_date || ')' AS contact_info
FROM customers
LIMIT 5;
```

| contact_info         |
| -------------------- |
| 정준호 (1988-03-15)    |
| (NULL)               |
| 김민재 (1995-07-22)    |
| ...                  |

`COALESCE`로 NULL을 대체 문자열로 바꿔야 합니다.

=== "SQLite / PostgreSQL"
    ```sql
    SELECT
        name || ' (' || COALESCE(birth_date, '미입력') || ')' AS contact_info
    FROM customers
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    -- MySQL의 CONCAT()은 NULL이 있어도 NULL을 반환
    SELECT
        CONCAT(name, ' (', COALESCE(birth_date, '미입력'), ')') AS contact_info
    FROM customers
    LIMIT 5;

    -- CONCAT_WS()는 NULL을 건너뜀 (구분자 지정)
    SELECT
        CONCAT_WS(' | ', name, phone, email) AS contact_info
    FROM customers
    LIMIT 5;
    ```

> **규칙:** 문자열 연결 시 NULL이 될 수 있는 칼럼에는 항상 `COALESCE(col, '기본값')`을 씌우세요. MySQL의 `CONCAT_WS()`는 NULL을 자동으로 건너뛰므로 편리합니다.

## LPAD, RPAD — 고정 폭 패딩

문자열을 지정한 길이로 맞추고, 부족한 부분을 특정 문자로 채웁니다. 주문번호 포맷팅, 리포트 정렬 등에 유용합니다.

=== "SQLite"
    SQLite에는 `LPAD`/`RPAD` 함수가 없습니다. `printf()`로 대체합니다.

    ```sql
    -- 고객 ID를 5자리 0-패딩
    SELECT
        id,
        printf('%05d', id) AS padded_id,
        name
    FROM customers
    LIMIT 5;
    ```

    | id | padded_id | name |
    | -: | --------- | ---- |
    |  1 | 00001     | 정준호  |
    |  2 | 00002     | 김경수  |
    | ...| ...       | ...  |

=== "MySQL"
    ```sql
    -- 고객 ID를 5자리 0-패딩
    SELECT
        id,
        LPAD(id, 5, '0') AS padded_id,
        name
    FROM customers
    LIMIT 5;

    -- 상품명을 30자 고정폭으로 (오른쪽 공백 채움)
    SELECT RPAD(name, 30, ' ') AS fixed_name, price
    FROM products
    LIMIT 5;
    ```

=== "PostgreSQL"
    ```sql
    -- 고객 ID를 5자리 0-패딩
    SELECT
        id,
        LPAD(id::text, 5, '0') AS padded_id,
        name
    FROM customers
    LIMIT 5;

    -- 상품명을 30자 고정폭으로
    SELECT RPAD(name, 30, ' ') AS fixed_name, price
    FROM products
    LIMIT 5;
    ```

> `LPAD(값, 총길이, 채울문자)`는 **왼쪽**을 채우고, `RPAD`는 **오른쪽**을 채웁니다. 값이 총길이보다 길면 MySQL/PG에서는 잘립니다.

## GROUP_CONCAT / STRING_AGG — 그룹별 문자열 집계

여러 행의 문자열을 하나로 합칩니다. "카테고리별 상품 목록", "고객별 주문번호 나열" 등에 매우 자주 쓰이는 함수입니다.

=== "SQLite"
    ```sql
    -- 공급업체별 상품명 목록
    SELECT
        s.company_name,
        GROUP_CONCAT(p.name, ', ') AS product_list,
        COUNT(*)                   AS product_count
    FROM products AS p
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    WHERE p.is_active = 1
    GROUP BY s.company_name
    ORDER BY product_count DESC
    LIMIT 3;
    ```

    > SQLite의 `GROUP_CONCAT(col, 구분자)` — 구분자 기본값은 `','`(콤마)입니다.

=== "MySQL"
    ```sql
    -- 공급업체별 상품명 목록
    SELECT
        s.company_name,
        GROUP_CONCAT(p.name ORDER BY p.name SEPARATOR ', ') AS product_list,
        COUNT(*) AS product_count
    FROM products AS p
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    WHERE p.is_active = 1
    GROUP BY s.company_name
    ORDER BY product_count DESC
    LIMIT 3;
    ```

    > MySQL의 `GROUP_CONCAT`은 `ORDER BY`와 `SEPARATOR`를 지원합니다. 기본 최대 길이는 1024바이트(`group_concat_max_len`)입니다.

=== "PostgreSQL"
    ```sql
    -- 공급업체별 상품명 목록
    SELECT
        s.company_name,
        STRING_AGG(p.name, ', ' ORDER BY p.name) AS product_list,
        COUNT(*) AS product_count
    FROM products AS p
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    WHERE p.is_active = 1
    GROUP BY s.company_name
    ORDER BY product_count DESC
    LIMIT 3;
    ```

    > PostgreSQL은 `STRING_AGG(col, 구분자 ORDER BY ...)` 형식입니다. 길이 제한이 없습니다.

**결과 (예시):**

| company_name | product_list                              | product_count |
| ------------ | ----------------------------------------- | ------------: |
| 에이수스코리아      | ASUS Dual RTX 5070 Ti ..., ASUS PCE-BE92BT ... | 21 |
| 삼성전자 공식 유통   | 삼성 DDR4 32GB ..., 삼성 DDR5 16GB ...         | 21 |
| ...          | ...                                       | ...           |

```sql
-- 고객 등급별 고객 이름 (상위 5명씩)
SELECT
    grade,
    GROUP_CONCAT(name, ', ') AS sample_names
FROM (
    SELECT grade, name, ROW_NUMBER() OVER (PARTITION BY grade ORDER BY id) AS rn
    FROM customers
    WHERE is_active = 1
) AS ranked
WHERE rn <= 5
GROUP BY grade;
```

## 정리

| 개념 | 설명 | 예시 |
|------|------|------|
| SUBSTR | 문자열 일부 추출 (1-based) | `SUBSTR(name, 1, 10)` |
| LENGTH | 문자 수 반환 | `LENGTH(name)` |
| UPPER / LOWER | 대소문자 변환 | `UPPER(grade)`, `LOWER(email)` |
| REPLACE | 문자열 치환 | `REPLACE(status, '_', ' ')` |
| 문자열 연결 | SQLite/PG: `\|\|`, MySQL: `CONCAT()` | `name \|\| ' - ' \|\| email` |
| NULL + 연결 | NULL이면 전체가 NULL → COALESCE 필수 | `COALESCE(col, '기본값')` |
| INSTR / LOCATE / POSITION | 문자 위치 찾기 (DB별 상이) | `INSTR(email, '@')` |
| TRIM / LTRIM / RTRIM | 앞뒤 공백·문자 제거 | `TRIM(name)` |
| LPAD / RPAD | 고정 폭 패딩 (SQLite: `printf`) | `LPAD(id, 5, '0')` |
| GROUP_CONCAT / STRING_AGG | 그룹별 문자열 합치기 | `GROUP_CONCAT(name, ', ')` |
| LIKE | 패턴 매칭 (`%`, `_` 와일드카드) | `WHERE name LIKE '%Gaming%'` |

!!! note "레슨 복습 문제"
    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. 여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/index.md) 섹션을 참고하세요.

## 연습 문제

### 연습 1
고객 연락처 카드를 만드세요: 각 고객의 `name`, `phone`, `email`을 `"이름 | 전화번호 | 이메일"` 형식의 단일 문자열로 연결하세요. 활성 고객 전체의 `customer_id`, `contact_card`, `grade`를 반환하고, 10행으로 제한하세요.

??? success "정답"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT
            id AS customer_id,
            name || ' | ' || phone || ' | ' || email AS contact_card,
            grade
        FROM customers
        WHERE is_active = 1
        LIMIT 10;
        ```

        **결과 (예시):**

        | customer_id | contact_card                            | grade  |
        | ----------: | --------------------------------------- | ------ |
        |           2 | 김경수 | 020-4423-5167 | user2@testmail.kr | VIP    |
        |           3 | 김민재 | 020-0806-0711 | user3@testmail.kr | VIP    |
        |           4 | 진정자 | 020-9666-8856 | user4@testmail.kr | VIP    |
        |           5 | 이정수 | 020-0239-9503 | user5@testmail.kr | SILVER |
        |           8 | 성민석 | 020-8951-7989 | user8@testmail.kr | BRONZE |
        | ...         | ...                                     | ...    |


    === "MySQL"
        ```sql
        SELECT
            id AS customer_id,
            CONCAT(name, ' | ', phone, ' | ', email) AS contact_card,
            grade
        FROM customers
        WHERE is_active = 1
        LIMIT 10;
        ```

### 연습 2
각 주문에서 일련번호(예: `ORD-20240315-00042`의 마지막 5자리 `00042`)를 추출하여 정수로 표시하세요. `order_number`, `sequence_no`(정수), `total_amount`를 반환하고, `sequence_no` 내림차순으로 10행까지 정렬하세요.

??? success "정답"
    ```sql
    SELECT
        order_number,
        CAST(SUBSTR(order_number, -5) AS INTEGER) AS sequence_no,
        total_amount
    FROM orders
    ORDER BY sequence_no DESC
    LIMIT 10;
    ```

    **결과 (예시):**

    | order_number       | sequence_no | total_amount |
    | ------------------ | ----------: | -----------: |
    | ORD-20250630-34908 |       34908 |       387900 |
    | ORD-20250630-34907 |       34907 |      4222961 |
    | ORD-20250630-34906 |       34906 |        52400 |
    | ORD-20250630-34905 |       34905 |       152600 |
    | ORD-20250630-34904 |       34904 |      1411900 |
    | ...                | ...         | ...          |


### 연습 3
고객 이름의 길이를 구하고, 이름이 가장 긴 상위 5명을 반환하세요. `name`, `name_length`를 `name_length` 내림차순으로 정렬하세요.

??? success "정답"
    ```sql
    SELECT
        name,
        LENGTH(name) AS name_length
    FROM customers
    ORDER BY name_length DESC
    LIMIT 5;
    ```

    **결과 (예시):**

    | name | name_length |
    | ---- | ----------: |
    | 정준호  |           3 |
    | 김경수  |           3 |
    | 김민재  |           3 |
    | 진정자  |           3 |
    | 이정수  |           3 |


### 연습 4
주문 상태(`status`)의 밑줄(`_`)을 공백으로 바꾸고 대문자로 변환하세요. 고유한 상태값만 표시합니다. `status`(원본)와 `display_status`를 반환하세요.

??? success "정답"
    ```sql
    SELECT DISTINCT
        status,
        UPPER(REPLACE(status, '_', ' ')) AS display_status
    FROM orders;
    ```

    **결과 (예시):**

    | status    | display_status |
    | --------- | -------------- |
    | cancelled | CANCELLED      |
    | confirmed | CONFIRMED      |
    | delivered | DELIVERED      |
    | paid      | PAID           |
    | pending   | PENDING        |
    | ...       | ...            |


### 연습 5
상품 이름에 `'Gaming'`이라는 단어가 포함된 상품의 `name`, `price`를 가격 내림차순으로 조회하세요. LIKE 패턴을 사용하세요.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%Gaming%'
    ORDER BY price DESC;
    ```

    **결과 (예시):**

    | name                                   | price   |
    | -------------------------------------- | ------: |
    | ASUS TUF Gaming RTX 5080 화이트           | 3812000 |
    | MSI Radeon RX 9070 XT GAMING X         | 1788500 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트    | 1478100 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙    |  408800 |


### 연습 6
고객 이메일에서 `@` 앞의 사용자 ID 부분만 추출하세요. `name`, `email`, `user_id`를 반환하고 10행으로 제한하세요.

??? success "정답"
    === "SQLite"
        ```sql
        SELECT
            name,
            email,
            SUBSTR(email, 1, INSTR(email, '@') - 1) AS user_id
        FROM customers
        LIMIT 10;
        ```

        **결과 (예시):**

        | name | email             | user_id |
        | ---- | ----------------- | ------- |
        | 정준호  | user1@testmail.kr | user1   |
        | 김경수  | user2@testmail.kr | user2   |
        | 김민재  | user3@testmail.kr | user3   |
        | 진정자  | user4@testmail.kr | user4   |
        | 이정수  | user5@testmail.kr | user5   |
        | ...  | ...               | ...     |


    === "MySQL"
        ```sql
        SELECT
            name,
            email,
            SUBSTRING(email, 1, LOCATE('@', email) - 1) AS user_id
        FROM customers
        LIMIT 10;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            name,
            email,
            SUBSTRING(email FROM 1 FOR POSITION('@' IN email) - 1) AS user_id
        FROM customers
        LIMIT 10;
        ```

### 연습 7
상품 이름의 처음 20자만 잘라서 말줄임표(`...`)를 붙인 `short_name`을 만드세요. 이름이 20자 이하이면 원래 이름을 그대로 표시합니다. `name`, `short_name`을 반환하고, 이름이 긴 순서대로 10행을 표시하세요.

??? success "정답"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT
            name,
            CASE
                WHEN LENGTH(name) > 20
                    THEN SUBSTR(name, 1, 20) || '...'
                ELSE name
            END AS short_name
        FROM products
        ORDER BY LENGTH(name) DESC
        LIMIT 10;
        ```

        **결과 (예시):**

        | name                                                             | short_name              |
        | ---------------------------------------------------------------- | ----------------------- |
        | HP EliteBook 840 G10 블랙 [특별 한정판 에디션] 무상 보증 3년 연장 + 전용 파우치 증정 이벤트 | HP EliteBook 840 G10... |
        | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장    | ASUS Dual RTX 5070 T... |
        | ASUS ExpertBook B5 [특별 한정판 에디션] RGB 라이팅 탑재, 소프트웨어 커스터마이징 지원      | ASUS ExpertBook B5 [... |
        | ASUS ExpertBook B5 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장       | ASUS ExpertBook B5 [... |
        | TeamGroup T-Force Delta RGB DDR5 32GB 6000MHz 실버                 | TeamGroup T-Force De... |
        | ...                                                              | ...                     |


    === "MySQL"
        ```sql
        SELECT
            name,
            CASE
                WHEN LENGTH(name) > 20
                    THEN CONCAT(SUBSTRING(name, 1, 20), '...')
                ELSE name
            END AS short_name
        FROM products
        ORDER BY LENGTH(name) DESC
        LIMIT 10;
        ```

### 연습 8
고객의 등급(`grade`)을 소문자로, 이름(`name`)을 대문자로 변환하여 `"GRADE: grade - NAME"` 형식의 문자열을 만드세요. 예: `"VIP: vip - 김민수"` → `"VIP: vip - 김민수"`. `id`, `display_text`를 반환하고, 활성 고객 10행으로 제한하세요.

??? success "정답"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT
            id,
            UPPER(grade) || ': ' || LOWER(grade) || ' - ' || name AS display_text
        FROM customers
        WHERE is_active = 1
        LIMIT 10;
        ```

        **결과 (예시):**

        | id | display_text         |
        | -: | -------------------- |
        |  2 | VIP: vip - 김경수       |
        |  3 | VIP: vip - 김민재       |
        |  4 | VIP: vip - 진정자       |
        |  5 | SILVER: silver - 이정수 |
        |  8 | BRONZE: bronze - 성민석 |
        | ... | ...                  |


    === "MySQL"
        ```sql
        SELECT
            id,
            CONCAT(UPPER(grade), ': ', LOWER(grade), ' - ', name) AS display_text
        FROM customers
        WHERE is_active = 1
        LIMIT 10;
        ```

### 연습 9
주문 번호(`order_number`)가 `'ORD-2024'`로 시작하는 주문 중, 주문 번호의 중간 날짜 부분(5~12번째 문자, 예: `20240315`)을 추출하세요. `order_number`, `date_part`, `total_amount`를 반환하고 10행으로 제한하세요.

??? success "정답"
    ```sql
    SELECT
        order_number,
        SUBSTR(order_number, 5, 8) AS date_part,
        total_amount
    FROM orders
    WHERE order_number LIKE 'ORD-2024%'
    LIMIT 10;
    ```

    **결과 (예시):**

    | order_number       | date_part | total_amount |
    | ------------------ | --------: | -----------: |
    | ORD-20240101-26304 |  20240101 |      3250600 |
    | ORD-20240101-26305 |  20240101 |      1465600 |
    | ORD-20240101-26306 |  20240101 |        82700 |
    | ORD-20240101-26307 |  20240101 |       419600 |
    | ORD-20240101-26308 |  20240101 |      2860850 |
    | ...                | ...       | ...          |


### 연습 10
상품 이름에서 `@` 기호의 위치를 찾아보세요 (존재하지 않으면 0). 이름에 공백이 포함된 상품만 대상으로 `name`, `space_pos`(첫 번째 공백 위치)를 반환하고, 10행으로 제한하세요.

??? success "정답"
    === "SQLite"
        ```sql
        SELECT
            name,
            INSTR(name, ' ') AS space_pos
        FROM products
        WHERE INSTR(name, ' ') > 0
        LIMIT 10;
        ```

        **결과 (예시):**

        | name                                | space_pos |
        | ----------------------------------- | --------: |
        | AMD Ryzen 9 9900X                   |         4 |
        | AMD Ryzen 9 9900X                   |         4 |
        | APC Back-UPS Pro Gaming BGM1500B 블랙 |         4 |
        | ASRock B850M Pro RS 블랙              |         7 |
        | ASRock B850M Pro RS 실버              |         7 |
        | ...                                 | ...       |


    === "MySQL"
        ```sql
        SELECT
            name,
            LOCATE(' ', name) AS space_pos
        FROM products
        WHERE LOCATE(' ', name) > 0
        LIMIT 10;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            name,
            POSITION(' ' IN name) AS space_pos
        FROM products
        WHERE POSITION(' ' IN name) > 0
        LIMIT 10;
        ```

### 연습 11
고객의 `name`과 `phone`을 연결하되, 전화번호가 NULL인 경우 `'번호 없음'`으로 표시하세요. `customer_id`, `contact`를 반환하고 10행으로 제한하세요.

??? success "정답"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT
            id AS customer_id,
            name || ' — ' || COALESCE(phone, '번호 없음') AS contact
        FROM customers
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT
            id AS customer_id,
            CONCAT(name, ' — ', COALESCE(phone, '번호 없음')) AS contact
        FROM customers
        LIMIT 10;
        ```


### 연습 12
고객 ID를 6자리 0-패딩으로 포맷하고, `'C-'` 접두어를 붙인 `customer_code`를 만드세요. 예: ID 42 → `'C-000042'`. `customer_code`, `name`, `grade`를 반환하고 10행으로 제한하세요.

??? success "정답"
    === "SQLite"
        ```sql
        SELECT
            'C-' || printf('%06d', id) AS customer_code,
            name,
            grade
        FROM customers
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT
            CONCAT('C-', LPAD(id, 6, '0')) AS customer_code,
            name,
            grade
        FROM customers
        LIMIT 10;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            'C-' || LPAD(id::text, 6, '0') AS customer_code,
            name,
            grade
        FROM customers
        LIMIT 10;
        ```


### 연습 13
카테고리별로 해당 카테고리에 속한 활성 상품의 이름을 콤마로 연결하여 한 행으로 표시하세요. `category_name`, `product_list`, `product_count`를 반환하고, 상품 수가 많은 순으로 5행까지 정렬하세요.

??? success "정답"
    === "SQLite"
        ```sql
        SELECT
            cat.name AS category_name,
            GROUP_CONCAT(p.name, ', ') AS product_list,
            COUNT(*) AS product_count
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
        GROUP BY cat.name
        ORDER BY product_count DESC
        LIMIT 5;
        ```

    === "MySQL"
        ```sql
        SELECT
            cat.name AS category_name,
            GROUP_CONCAT(p.name ORDER BY p.name SEPARATOR ', ') AS product_list,
            COUNT(*) AS product_count
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
        GROUP BY cat.name
        ORDER BY product_count DESC
        LIMIT 5;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            cat.name AS category_name,
            STRING_AGG(p.name, ', ' ORDER BY p.name) AS product_list,
            COUNT(*) AS product_count
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
        GROUP BY cat.name
        ORDER BY product_count DESC
        LIMIT 5;
        ```


### 채점 가이드

| 점수 | 다음 단계 |
|:----:|----------|
| **12~13개** | [13강: 숫자·변환·조건 함수](13-utility-functions.md)로 이동 |
| **9~11개** | 틀린 문제 해설을 복습한 뒤 다음강으로 |
| **절반 이하** | 이 강의를 다시 읽어보세요 |
| **3개 이하** | [11강: 날짜/시간 함수](11-datetime.md)부터 다시 시작하세요 |

**문제별 영역:**

| 영역 | 해당 문제 |
|------|:--------:|
| 문자열 연결 (&#124;&#124; / CONCAT) | 1, 8 |
| SUBSTR + CAST 추출 | 2, 9 |
| LENGTH | 3 |
| REPLACE + UPPER/LOWER | 4 |
| LIKE 패턴 매칭 | 5 |
| SUBSTR + INSTR 파싱 | 6, 10 |
| CASE + LENGTH + SUBSTR 조합 | 7 |
| NULL + 문자열 연결 (COALESCE) | 11 |
| LPAD / printf 패딩 | 12 |
| GROUP_CONCAT / STRING_AGG | 13 |

---
다음: [13강: 숫자·변환·조건 함수](13-utility-functions.md)
