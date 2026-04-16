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

| order_number | ordered_at | order_date | year_month |
| ---------- | ---------- | ---------- | ---------- |
| ORD-20160101-00001 | 2016-01-31 22:16:37 | 2016-01-31 | 2016-01 |
| ORD-20160101-00002 | 2016-01-06 01:15:21 | 2016-01-06 | 2016-01 |
| ORD-20160101-00003 | 2016-01-11 08:08:34 | 2016-01-11 | 2016-01 |
| ORD-20160101-00004 | 2016-01-23 08:32:43 | 2016-01-23 | 2016-01 |
| ORD-20160101-00005 | 2016-01-11 07:08:34 | 2016-01-11 | 2016-01 |
| ... | ... | ... | ... |

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

| name | name_length |
| ---------- | ----------: |
| TeamGroup T-Force Delta RGB DDR5 32GB 6000MHz 화이트 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | 89 |
| MSI MAG B850 TOMAHAWK MAX WIFI 화이트 [특별 한정판 에디션] 고급 알루미늄 합금 바디 적용, 프리미엄 패키지 구성 | 77 |
| Microsoft Bluetooth Ergonomic Mouse 실버 [특별 한정판 에디션] 전문가 추천 모델, 업계 최고 성능 인증 획득 | 77 |
| ASUS TUF Gaming RTX 4070 Ti Super 실버 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | 76 |
| be quiet! Shadow Base 800 FX 블랙 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | 71 |
| ... | ... |

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

| name | email_lower | grade_display |
| ---------- | ---------- | ---------- |
| 정준호 | user1@testmail.kr | BRONZE |
| 김경수 | user2@testmail.kr | BRONZE |
| 김민재 | user3@testmail.kr | VIP |
| 진정자 | user4@testmail.kr | GOLD |
| 이정수 | user5@testmail.kr | BRONZE |
| ... | ... | ... |

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

| status | status_readable |
| ---------- | ---------- |
| cancelled | cancelled |
| confirmed | confirmed |
| delivered | delivered |
| paid | paid |
| pending | pending |
| preparing | preparing |
| return_requested | return requested |
| returned | returned |
| ... | ... |

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

## REGEXP — 정규표현식

LIKE의 `%`와 `_`만으로는 "영문자+숫자 조합", "이메일 형식 검증" 같은 복잡한 패턴을 표현하기 어렵습니다. 정규표현식(Regular Expression)을 사용하면 훨씬 정밀한 패턴 매칭이 가능합니다.

### DB별 지원 현황

=== "SQLite"
    SQLite에는 `REGEXP` 연산자가 문법으로 존재하지만, **기본 설치에는 구현이 없어** 사용하면 에러가 발생합니다. 확장(extension)을 로드해야 동작합니다.

    대안으로 `GLOB`을 사용합니다. GLOB은 대소문자를 구분하며, `*`(여러 문자)와 `?`(한 문자), `[...]`(문자 클래스)를 지원합니다.

    ```sql
    -- 상품명에 숫자가 포함된 상품 (GLOB 사용)
    SELECT name, price
    FROM products
    WHERE name GLOB '*[0-9]*'
    LIMIT 5;
    ```

    ```sql
    -- 대문자 영문으로 시작하는 상품
    SELECT name
    FROM products
    WHERE name GLOB '[A-Z]*'
    LIMIT 5;
    ```

=== "MySQL"
    MySQL은 `REGEXP` (또는 동의어 `RLIKE`) 연산자를 기본 지원합니다. MySQL 8.0+에서는 ICU 정규표현식 라이브러리를 사용합니다.

    ```sql
    -- 모델 번호 패턴: 영문자 뒤에 숫자가 오는 상품 (예: RTX 5070, DDR5 16GB)
    SELECT name, price
    FROM products
    WHERE name REGEXP '[A-Za-z]+[0-9]+'
    LIMIT 5;
    ```

    ```sql
    -- 이메일 기본 형식 검증 (@ 앞뒤로 문자가 있는지)
    SELECT name, email
    FROM customers
    WHERE email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
    LIMIT 5;
    ```

=== "PostgreSQL"
    PostgreSQL은 `~` 연산자(대소문자 구분)와 `~*` 연산자(대소문자 무시)를 사용합니다. POSIX 정규표현식을 지원합니다.

    ```sql
    -- 모델 번호 패턴: 영문자 뒤에 숫자가 오는 상품
    SELECT name, price
    FROM products
    WHERE name ~ '[A-Za-z]+[0-9]+'
    LIMIT 5;
    ```

    ```sql
    -- 대소문자 무시: 'gaming' 포함 상품 (~* 사용)
    SELECT name, price
    FROM products
    WHERE name ~* 'gaming'
    LIMIT 5;

    -- 이메일 기본 형식 검증
    SELECT name, email
    FROM customers
    WHERE email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    LIMIT 5;
    ```

### 문법 비교

| DB | 연산자 | 대소문자 무시 | 예시 |
|----|--------|:----------:|------|
| SQLite | GLOB (대안) | X | `WHERE name GLOB '*[0-9]*'` |
| MySQL | REGEXP / RLIKE | 기본 무시 | `WHERE name REGEXP '[0-9]+'` |
| PostgreSQL | `~` | `~*` 사용 | `WHERE name ~ '[0-9]+'` |

> **실무 팁:** REGEXP는 인덱스를 사용하지 못하므로, 대량 데이터에서는 LIKE로 먼저 범위를 좁힌 뒤 REGEXP로 정밀 필터링하는 것이 좋습니다.

## 정리

| 개념 | 설명 | 예시 |
|------|------|------

<!-- BEGIN_LESSON_EXERCISES -->

!!! note "레슨 복습 문제"
    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. 여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/index.md) 섹션을 참고하세요.

### 문제 1
고객 연락처 카드를 만드세요: 각 고객의 `name`, `phone`, `email`을 `"이름 | 전화번호 | 이메일"` 형식의 단일 문자열로 연결하세요. 활성 고객 전체의 `customer_id`, `contact_card`, `grade`를 반환하고, 10행으로 제한하세요.

??? success "정답"
    ```sql
    SELECT
    id AS customer_id,
    name || ' | ' || phone || ' | ' || email AS contact_card,
    grade
    FROM customers
    WHERE is_active = 1
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | customer_id | contact_card | grade |
    |---|---|---|
    | 2 | 김경수 | 020-4423-5167 | user2@testmail.kr | GOLD |
    | 3 | 김민재 | 020-0806-0711 | user3@testmail.kr | VIP |
    | 4 | 진정자 | 020-9666-8856 | user4@testmail.kr | GOLD |
    | 5 | 이정수 | 020-0239-9503 | user5@testmail.kr | SILVER |
    | 8 | 성민석 | 020-8951-7989 | user8@testmail.kr | SILVER |
    | 10 | 박지훈 | 020-1196-8263 | user10@testmail.kr | GOLD |
    | 12 | 장준서 | 020-0083-5468 | user12@testmail.kr | GOLD |

### 문제 2
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


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | sequence_no | total_amount |
    |---|---|---|
    | ORD-20251231-37557 | 37,557 | 388,500.00 |
    | ORD-20251231-37556 | 37,556 | 153,900.00 |
    | ORD-20251231-37555 | 37,555 | 74,800.00 |
    | ORD-20251231-37554 | 37,554 | 74,900.00 |
    | ORD-20251231-37553 | 37,553 | 350,500.00 |
    | ORD-20251231-37552 | 37,552 | 254,300.00 |
    | ORD-20251231-37551 | 37,551 | 417,000.00 |

### 문제 3
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


    **실행 결과** (5행)

    | name | name_length |
    |---|---|
    | 정준호 | 3 |
    | 김경수 | 3 |
    | 김민재 | 3 |
    | 진정자 | 3 |
    | 이정수 | 3 |

### 문제 4
주문 상태(`status`)의 밑줄(`_`)을 공백으로 바꾸고 대문자로 변환하세요. 고유한 상태값만 표시합니다. `status`(원본)와 `display_status`를 반환하세요.

??? success "정답"
    ```sql
    SELECT DISTINCT
    status,
    UPPER(REPLACE(status, '_', ' ')) AS display_status
    FROM orders;
    ```


    **실행 결과** (총 9행 중 상위 7행)

    | status | display_status |
    |---|---|
    | cancelled | CANCELLED |
    | confirmed | CONFIRMED |
    | delivered | DELIVERED |
    | paid | PAID |
    | pending | PENDING |
    | preparing | PREPARING |
    | return_requested | RETURN REQUESTED |

### 문제 5
상품 이름에 `'Gaming'`이라는 단어가 포함된 상품의 `name`, `price`를 가격 내림차순으로 조회하세요. LIKE 패턴을 사용하세요.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%Gaming%'
    ORDER BY price DESC;
    ```


    **실행 결과** (5행)

    | name | price |
    |---|---|
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 |
    | MSI Radeon RX 9070 XT GAMING X | 1,896,000.00 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트 | 1,517,600.00 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | 516,300.00 |

### 문제 6
고객 이메일에서 `@` 앞의 사용자 ID 부분만 추출하세요. `name`, `email`, `user_id`를 반환하고 10행으로 제한하세요.

??? success "정답"
    ```sql
    SELECT
    name,
    email,
    SUBSTR(email, 1, INSTR(email, '@') - 1) AS user_id
    FROM customers
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | email | user_id |
    |---|---|---|
    | 정준호 | user1@testmail.kr | user1 |
    | 김경수 | user2@testmail.kr | user2 |
    | 김민재 | user3@testmail.kr | user3 |
    | 진정자 | user4@testmail.kr | user4 |
    | 이정수 | user5@testmail.kr | user5 |
    | 김준혁 | user6@testmail.kr | user6 |
    | 김명자 | user7@testmail.kr | user7 |

### 문제 7
상품 이름의 처음 20자만 잘라서 말줄임표(`...`)를 붙인 `short_name`을 만드세요. 이름이 20자 이하이면 원래 이름을 그대로 표시합니다. `name`, `short_name`을 반환하고, 이름이 긴 순서대로 10행을 표시하세요.

??? success "정답"
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


    **실행 결과** (총 10행 중 상위 7행)

    | name | short_name |
    |---|---|
    | HP EliteBook 840 G10 블랙 [특별 한정판 에디션] ... | HP EliteBook 840 G10... |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | ASUS Dual RTX 5070 T... |
    | ASUS ExpertBook B5 [특별 한정판 에디션] RGB 라... | ASUS ExpertBook B5 [... |
    | ASUS ExpertBook B5 [특별 한정판 에디션] 저소음 설... | ASUS ExpertBook B5 [... |
    | TeamGroup T-Force Delta RGB DDR5 32GB... | TeamGroup T-Force De... |
    | CORSAIR Dominator Titanium DDR5 32GB ... | CORSAIR Dominator Ti... |
    | Arctic Liquid Freezer III Pro 420 A-R... | Arctic Liquid Freeze... |

### 문제 8
고객의 등급(`grade`)을 소문자로, 이름(`name`)을 대문자로 변환하여 `"GRADE: grade - NAME"` 형식의 문자열을 만드세요. 예: `"VIP: vip - 김민수"` → `"VIP: vip - 김민수"`. `id`, `display_text`를 반환하고, 활성 고객 10행으로 제한하세요.

??? success "정답"
    ```sql
    SELECT
    id,
    UPPER(grade) || ': ' || LOWER(grade) || ' - ' || name AS display_text
    FROM customers
    WHERE is_active = 1
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | id | display_text |
    |---|---|
    | 2 | GOLD: gold - 김경수 |
    | 3 | VIP: vip - 김민재 |
    | 4 | GOLD: gold - 진정자 |
    | 5 | SILVER: silver - 이정수 |
    | 8 | SILVER: silver - 성민석 |
    | 10 | GOLD: gold - 박지훈 |
    | 12 | GOLD: gold - 장준서 |

### 문제 9
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


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | date_part | total_amount |
    |---|---|---|
    | ORD-20240101-25452 | 20240101 | 337,900.00 |
    | ORD-20240101-25453 | 20240101 | 160,400.00 |
    | ORD-20240101-25454 | 20240101 | 117,700.00 |
    | ORD-20240101-25455 | 20240101 | 42,600.00 |
    | ORD-20240101-25456 | 20240101 | 1,171,392.00 |
    | ORD-20240101-25457 | 20240101 | 616,200.00 |
    | ORD-20240101-25458 | 20240101 | 206,300.00 |

### 문제 10
상품 이름에서 `@` 기호의 위치를 찾아보세요 (존재하지 않으면 0). 이름에 공백이 포함된 상품만 대상으로 `name`, `space_pos`(첫 번째 공백 위치)를 반환하고, 10행으로 제한하세요.

??? success "정답"
    ```sql
    SELECT
    name,
    INSTR(name, ' ') AS space_pos
    FROM products
    WHERE INSTR(name, ' ') > 0
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | space_pos |
    |---|---|
    | AMD Ryzen 9 9900X | 4 |
    | AMD Ryzen 9 9900X | 4 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | 4 |
    | ASRock B850M Pro RS 블랙 | 7 |
    | ASRock B850M Pro RS 실버 | 7 |
    | ASRock B850M Pro RS 화이트 | 7 |
    | ASRock B860M Pro RS 실버 | 7 |

### 문제 11
고객의 `name`과 `phone`을 연결하되, 전화번호가 NULL인 경우 `'번호 없음'`으로 표시하세요. `customer_id`, `contact`를 반환하고 10행으로 제한하세요.

??? success "정답"
    ```sql
    SELECT
    id AS customer_id,
    name || ' — ' || COALESCE(phone, '번호 없음') AS contact
    FROM customers
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | customer_id | contact |
    |---|---|
    | 1 | 정준호 — 020-4964-6200 |
    | 2 | 김경수 — 020-4423-5167 |
    | 3 | 김민재 — 020-0806-0711 |
    | 4 | 진정자 — 020-9666-8856 |
    | 5 | 이정수 — 020-0239-9503 |
    | 6 | 김준혁 — 020-0786-7765 |
    | 7 | 김명자 — 020-4487-2922 |

### 문제 12
고객 ID를 6자리 0-패딩으로 포맷하고, `'C-'` 접두어를 붙인 `customer_code`를 만드세요. 예: ID 42 → `'C-000042'`. `customer_code`, `name`, `grade`를 반환하고 10행으로 제한하세요.

??? success "정답"
    ```sql
    SELECT
    'C-' || printf('%06d', id) AS customer_code,
    name,
    grade
    FROM customers
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | customer_code | name | grade |
    |---|---|---|
    | C-000001 | 정준호 | BRONZE |
    | C-000002 | 김경수 | GOLD |
    | C-000003 | 김민재 | VIP |
    | C-000004 | 진정자 | GOLD |
    | C-000005 | 이정수 | SILVER |
    | C-000006 | 김준혁 | BRONZE |
    | C-000007 | 김명자 | BRONZE |

### 문제 13
카테고리별로 해당 카테고리에 속한 활성 상품의 이름을 콤마로 연결하여 한 행으로 표시하세요. `category_name`, `product_list`, `product_count`를 반환하고, 상품 수가 많은 순으로 5행까지 정렬하세요.

??? success "정답"
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


    **실행 결과** (5행)

    | category_name | product_list | product_count |
    |---|---|---|
    | 파워서플라이(PSU) | be quiet! Pure Power 12 M 850W 화이트, S... | 11 |
    | 케이스 | be quiet! Light Base 900, be quiet! L... | 10 |
    | 게이밍 모니터 | 삼성 오디세이 G7 32 화이트, 삼성 오디세이 OLED G8, 삼... | 10 |
    | Intel 소켓 | MSI MAG Z790 TOMAHAWK WIFI, MSI MEG Z... | 10 |
    | 조립PC | 한성 보스몬스터 DX9900 실버, ASUS ROG Strix G1... | 9 |

### 문제 14
상품 이름에서 모델 번호 패턴(영문자 뒤에 숫자가 바로 붙는 형태, 예: `RTX5070`, `DDR5`)이 포함된 상품을 찾으세요. `name`, `price`를 가격 내림차순으로 10행까지 반환하세요.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE name GLOB '*[A-Za-z][0-9]*'
    ORDER BY price DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | price |
    |---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 |
    | ASUS ROG Strix GT35 | 3,296,800.00 |
    | ASUS ExpertBook B5 [특별 한정판 에디션] RGB 라... | 2,121,600.00 |
    | HP EliteBook 840 G10 블랙 [특별 한정판 에디션] ... | 2,080,300.00 |
    | ASUS ExpertBook B5 화이트 | 2,068,800.00 |

<!-- END_LESSON_EXERCISES -->
