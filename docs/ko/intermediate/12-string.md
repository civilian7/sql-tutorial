# 12강: 문자열 함수

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

| order_number | ordered_at | order_date | year_month |
|--------------|------------|------------|------------|
| ORD-20150314-00001 | 2015-03-14 08:23:11 | 2015-03-14 | 2015-03 |
| ORD-20150314-00002 | 2015-03-14 11:47:33 | 2015-03-14 | 2015-03 |
| ORD-20150315-00003 | 2015-03-15 09:12:05 | 2015-03-15 | 2015-03 |

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
|------|-------------|
| Razer BlackWidow V3 Pro Wireless TKL Gaming Keyboard | 52 |
| ASUS ProArt PA329CRV 32" 4K HDR Professional Monitor | 51 |
| ... | |

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
|------|-------------|---------------|
| 김민수 | k.minsu@testmail.kr | VIP |
| 이지은 | l.jieun@testmail.kr | SILVER |

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
|--------|-----------------|
| pending | pending |
| return_requested | return requested |
| ... | |

## ||로 문자열 연결

`||`를 사용해 문자열을 이어 붙입니다.

```sql
-- 전체 연락처 정보 한 줄로 만들기
SELECT
    name,
    phone || ' — ' || email AS contact_info
FROM customers
LIMIT 5;
```

**결과:**

| name | contact_info |
|------|--------------|
| 김민수 | 020-1234-5678 — k.minsu@testmail.kr |
| 이지은 | 020-9876-5432 — l.jieun@testmail.kr |

```sql
-- 카테고리 접두어를 붙인 표시용 SKU 생성
SELECT
    p.name,
    cat.name || '-' || p.sku AS display_sku
FROM products AS p
INNER JOIN categories AS cat ON p.category_id = cat.id
LIMIT 5;
```

## 패턴 매칭 LIKE

2강에서 다뤘지만, 더 고급 패턴 예시를 소개합니다.

```sql
-- 이메일 도메인별 사용자 수 (@ 뒤 부분)
SELECT DISTINCT
    SUBSTR(email, INSTR(email, '@') + 1) AS domain,
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

## 연습 문제

### 연습 1
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

---
다음: [13강: UNION](13-union.md)
