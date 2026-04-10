# 12강: 문자열 함수

문자열 함수는 데이터베이스마다 이름이나 인자 순서가 다른 경우가 많습니다. 이 강의에서는 SQLite를 기본으로 하되, 차이가 있는 부분에서 MySQL과 PostgreSQL 탭을 함께 보여줍니다.

SQLite는 텍스트 조작에 유용한 함수들을 제공합니다. 데이터 정제, 출력 형식 지정, 저장된 문자열 파싱, 검색 조건 구성 등에 필수적입니다.

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

### 연습 4
주문 상태(`status`)의 밑줄(`_`)을 공백으로 바꾸고 대문자로 변환하세요. 고유한 상태값만 표시합니다. `status`(원본)와 `display_status`를 반환하세요.

??? success "정답"
    ```sql
    SELECT DISTINCT
        status,
        UPPER(REPLACE(status, '_', ' ')) AS display_status
    FROM orders;
    ```

### 연습 5
상품 이름에 `'Gaming'`이라는 단어가 포함된 상품의 `name`, `price`를 가격 내림차순으로 조회하세요. LIKE 패턴을 사용하세요.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%Gaming%'
    ORDER BY price DESC;
    ```

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

---
다음: [13강: UNION](13-union.md)
