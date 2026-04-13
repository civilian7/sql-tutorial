# 2강: WHERE로 데이터 필터링

1강에서 SELECT로 원하는 칼럼을 조회했습니다. 하지만 모든 행이 나왔죠? WHERE를 사용하면 조건에 맞는 행만 골라낼 수 있습니다.

!!! note "이미 알고 계신다면"
    WHERE, 비교연산자, AND/OR, IN, BETWEEN, LIKE, IS NULL을 이미 알고 있다면 [3강: 정렬과 페이징](03-sort-limit.md)으로 건너뛰세요.

`WHERE` 절은 조건을 만족하는 행만 결과에 포함시킵니다. `WHERE`가 없으면 테이블의 모든 행이 반환됩니다. 실무에서 의미 있는 데이터를 뽑아내려면 `WHERE` 사용이 필수입니다.

```mermaid
flowchart LR
    T["🗄️ All Rows\n(5,230)"] --> W["WHERE\ncondition"] --> R["📋 Filtered\n(127 rows)"]
```

> **개념:** WHERE는 조건에 맞는 행만 걸러냅니다. 전체 5,230명 중 VIP 127명만 추출하는 것과 같습니다.

## 비교 연산자

| 연산자 | 의미 |
|--------|------|
| `=` | 같다 |
| `<>` 또는 `!=` | 같지 않다 |
| `<`, `<=` | 미만, 이하 |
| `>`, `>=` | 초과, 이상 |

```sql
-- = : VIP 등급 고객만 조회
SELECT name, grade FROM customers
WHERE grade = 'VIP';
```

```sql
-- <> : VIP가 아닌 고객 (!=도 같은 뜻)
SELECT name, grade FROM customers
WHERE grade <> 'VIP';
```

```sql
-- > : 가격이 100만 원 초과인 상품
SELECT name, price FROM products
WHERE price > 1000000;
```

```sql
-- >= : 재고가 500개 이상인 상품
SELECT name, stock_qty FROM products
WHERE stock_qty >= 500;
```

```sql
-- < : 가격이 5만 원 미만인 저가 상품
SELECT name, price FROM products
WHERE price < 50000;
```

```sql
-- <= : 포인트 잔액이 0 이하인 고객
SELECT name, point_balance FROM customers
WHERE point_balance <= 0;
```

**`>` 결과 예시:**

| name | price |
| ---- | ----: |
| Razer Blade 18 블랙 | 2987500 |
| MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
| ... | ... |

!!! tip "가장 많이 쓰는 연산자"
    실무에서는 `=`(특정 값 필터)와 `<>`(특정 값 제외)가 가장 흔합니다. 예: `WHERE status = 'confirmed'`, `WHERE status <> 'cancelled'`

---

## AND / OR

`AND`는 두 조건이 모두 참일 때, `OR`는 하나라도 참일 때 행을 포함합니다.

```sql
-- 판매 중이고 가격이 10만~50만 원인 상품
SELECT name, price
FROM products
WHERE is_active = 1
  AND price >= 100000
  AND price <= 500000;
```

**결과:**

| name | price |
| ---------- | ----------: |
| G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 161900.0 |
| 삼성 DDR5 32GB PC5-38400 | 194700.0 |
| 로지텍 G715 화이트 | 254400.0 |
| be quiet! Light Base 900 | 161100.0 |
| MSI MAG X870E TOMAHAWK WIFI 화이트 | 473800.0 |
| NZXT Kraken Elite 240 RGB 실버 | 349200.0 |
| TP-Link Archer AX55 블랙 | 331900.0 |
| be quiet! Pure Power 12 M 850W 화이트 | 350200.0 |
| ... | ... |

```sql
-- VIP 또는 GOLD 등급 고객
SELECT name, email, grade
FROM customers
WHERE grade = 'VIP'
   OR grade = 'GOLD';
```

> **팁:** `AND`와 `OR`를 함께 사용할 때는 괄호로 우선순위를 명확히 하세요.
> `WHERE (grade = 'VIP' OR grade = 'GOLD') AND is_active = 1`

## IN

`IN`은 같은 칼럼에 대한 여러 `OR` 조건을 간결하게 표현합니다.

```sql
-- GOLD 또는 VIP 고객 조회 (IN 사용이 더 간결)
SELECT name, grade
FROM customers
WHERE grade IN ('GOLD', 'VIP');
```

**결과:**

| name | grade |
| ---------- | ---------- |
| 김민재 | VIP |
| 진정자 | GOLD |
| 성민석 | VIP |
| 박지훈 | GOLD |
| 강은서 | VIP |
| 김서준 | GOLD |
| 이영철 | VIP |
| 김선영 | GOLD |
| ... | ... |

```sql
-- 처리가 완료된 상태의 주문 조회
SELECT order_number, status, total_amount
FROM orders
WHERE status IN ('delivered', 'confirmed', 'returned');
```

## BETWEEN

`BETWEEN`은 양 끝값을 포함하는 범위 조건입니다. `>= 최솟값 AND <= 최댓값`과 동일합니다.

```sql
-- 가격이 5만~20만 원인 상품
SELECT name, price
FROM products
WHERE price BETWEEN 50000 AND 200000;
```

**결과:**

| name | price |
| ---------- | ----------: |
| G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 161900.0 |
| 삼성 DDR5 32GB PC5-38400 | 194700.0 |
| be quiet! Light Base 900 | 161100.0 |
| TP-Link TG-3468 실버 | 53600.0 |
| 로지텍 K580 | 50500.0 |
| Keychron Q1 Pro 실버 | 178600.0 |
| Seagate Fast SSD 1TB 실버 | 185300.0 |
| SteelSeries Prime Wireless 블랙 | 111200.0 |
| ... | ... |

```sql
-- 2024년 1분기에 접수된 주문
SELECT order_number, ordered_at, total_amount
FROM orders
WHERE ordered_at BETWEEN '2024-01-01' AND '2024-03-31 23:59:59';
```

## LIKE

`LIKE`는 텍스트 패턴을 매칭합니다. 두 가지 와일드카드를 사용합니다:

| 와일드카드 | 의미 | 예시 |
|:---------:|------|------|
| `%` | 0개 이상의 임의 문자 | `'%Gaming%'` → "Gaming"이 어디든 포함 |
| `_` | 정확히 한 글자 | `'_민재'` → 2글자 이름 중 "민재"로 끝나는 것 |

### % 예시 — 포함, 시작, 끝

```sql
-- 이름에 "Gaming"이 포함된 상품
SELECT name, price
FROM products
WHERE name LIKE '%Gaming%';
```

| name | price |
| ---- | ----: |
| MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
| ASUS TUF Gaming RTX 5080 화이트 | 3812000 |
| ... | ... |

```sql
-- testmail.kr 도메인으로 끝나는 이메일
SELECT name, email FROM customers
WHERE email LIKE '%@testmail.kr';
```

```sql
-- "삼성"으로 시작하는 상품
SELECT name, price FROM products
WHERE name LIKE '삼성%';
```

### _ 예시 — 정확히 한 글자

```sql
-- 이름이 정확히 3글자인 고객 (성 1글자 + 이름 2글자)
SELECT name, email FROM customers
WHERE name LIKE '___';
```

| name | email |
| ---- | ----- |
| 정준호 | jjh0001@testmail.kr |
| 김민재 | kmj0002@testmail.kr |
| ... | ... |

```sql
-- SKU 코드가 "LA-" 로 시작하고 그 뒤 3글자인 카테고리 코드를 가진 상품
SELECT name, sku FROM products
WHERE sku LIKE 'LA-___-%';
```

!!! tip "대소문자 구분"
    SQLite의 LIKE는 영문 대소문자를 구분하지 않습니다 (`'%gaming%'`과 `'%Gaming%'`이 같은 결과). MySQL은 기본적으로 구분하지 않고, PostgreSQL은 구분합니다. 대소문자를 무시하려면 PG에서는 `ILIKE`를 사용합니다.

---

## IS NULL / IS NOT NULL

NULL은 "알 수 없음" 또는 "없음"을 의미합니다. 0이나 빈 문자열과는 다릅니다. NULL 비교에는 `= NULL`이 아니라 반드시 `IS NULL`을 사용해야 합니다.

```sql
-- 생년월일이 등록되지 않은 고객
SELECT name, email
FROM customers
WHERE birth_date IS NULL;
```

**결과:**

| name | email |
| ---------- | ---------- |
| 김명자 | user7@testmail.kr |
| 김정식 | user13@testmail.kr |
| 윤순옥 | user14@testmail.kr |
| 이서연 | user21@testmail.kr |
| 강민석 | user24@testmail.kr |
| 김서준 | user27@testmail.kr |
| 윤지훈 | user36@testmail.kr |
| 박준영 | user38@testmail.kr |
| ... | ... |

```sql
-- 배송 메모가 있는 주문
SELECT order_number, notes
FROM orders
WHERE notes IS NOT NULL;
```

## 정리

| 키워드 | 설명 | 예시 |
|--------|------|------

<!-- BEGIN_LESSON_EXERCISES -->

!!! note "레슨 복습 문제"
    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. 여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/index.md) 섹션을 참고하세요.

### 문제 1
여성 고객(`gender = 'F'`) 중 SILVER 또는 GOLD 등급인 고객을 찾으세요. `name`, `grade`, `point_balance`를 반환하세요.

??? success "정답"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    WHERE gender = 'F'
    AND grade IN ('SILVER', 'GOLD');
    ```

### 문제 2
판매 중(`is_active = 1`)이고 가격이 20만~80만 원 사이인 상품을 조회하세요. `name`과 `price`를 반환하되, 가격 내림차순으로 정렬하세요.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE is_active = 1
    AND price BETWEEN 200000 AND 800000
    ORDER BY price DESC;
    ```

### 문제 3
성별이 알 수 없고(NULL) 마지막 로그인 기록도 없는(`last_login_at IS NULL`) 고객을 찾으세요. `name`과 `created_at`을 반환하세요.

??? success "정답"
    ```sql
    SELECT name, created_at
    FROM customers
    WHERE gender IS NULL
    AND last_login_at IS NULL;
    ```

### 문제 4
가격이 100만 원 이상인 상품의 `name`과 `price`를 조회하세요.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE price >= 1000000;
    ```

### 문제 5
재고가 0이 아닌 상품(`stock_qty <> 0`)의 `name`과 `stock_qty`를 조회하세요.

??? success "정답"
    ```sql
    SELECT name, stock_qty
    FROM products
    WHERE stock_qty <> 0;
    ```

### 문제 6
`customers` 테이블에서 포인트 잔액이 500에서 2000 사이인 GOLD 등급 고객의 `name`과 `point_balance`를 조회하세요.

??? success "정답"
    ```sql
    SELECT name, point_balance
    FROM customers
    WHERE grade = 'GOLD'
    AND point_balance BETWEEN 500 AND 2000;
    ```

### 문제 7
주문 상태가 `'pending'` 또는 `'processing'`인 주문의 `order_number`와 `status`를 조회하세요. `IN` 연산자를 사용하세요.

??? success "정답"
    ```sql
    SELECT order_number, status
    FROM orders
    WHERE status IN ('pending', 'processing');
    ```

### 문제 8
상품명이 "Keyboard"로 끝나는 상품의 `name`과 `price`를 조회하세요.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%Keyboard';
    ```

### 문제 9
`staff` 테이블에서 `department`가 `'Sales'`가 아닌 활성 직원(`is_active = 1`)의 `name`과 `department`를 조회하세요.

??? success "정답"
    ```sql
    SELECT name, department
    FROM staff
    WHERE is_active = 1
    AND department <> 'Sales';
    ```

### 문제 10
`customers` 테이블에서 VIP 등급이면서 비활성(`is_active = 0`)이거나, 포인트 잔액이 5000 이상인 고객의 `name`, `grade`, `point_balance`, `is_active`를 조회하세요. 괄호를 사용하여 조건 우선순위를 명확히 하세요.

??? success "정답"
    ```sql
    SELECT name, grade, point_balance, is_active
    FROM customers
    WHERE (grade = 'VIP' AND is_active = 0)
    OR point_balance >= 5000;
    ```

<!-- END_LESSON_EXERCISES -->
