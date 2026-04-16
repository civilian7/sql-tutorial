# 1강: SELECT 기초

0강에서 `SELECT id, name, email, grade FROM customers LIMIT 3`를 실행해봤습니다. 이번 강에서는 `SELECT`를 본격적으로 배웁니다.

`SELECT`는 SQL에서 가장 많이 쓰는 명령입니다. **테이블에서 원하는 칼럼을 골라 조회**합니다.

```mermaid
flowchart LR
    T["테이블
    (모든 행, 모든 칼럼)"] --> S["SELECT
    칼럼1, 칼럼2"] --> R["결과
    (모든 행, 선택한 칼럼만)"]
```

!!! note "이미 알고 계신다면"
    SELECT, AS, DISTINCT를 이미 알고 있다면 [2강: WHERE로 필터링](02-where.md)으로 이동하세요.

---

## 전체 칼럼 조회 — SELECT *

`SELECT *`는 테이블의 **모든 칼럼**을 가져옵니다. 테이블에 어떤 데이터가 있는지 빠르게 훑어볼 때 유용합니다.

```sql
SELECT * FROM categories;
```

**결과:**

| id | parent_id | name | slug | depth | sort_order | is_active | created_at | updated_at |
| ----------: | ---------- | ---------- | ---------- | ----------: | ----------: | ----------: | ---------- | ---------- |
| 1 | (NULL) | 데스크톱 PC | desktop-pc | 0 | 1 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
| 2 | 1 | 완제품 | desktop-prebuilt | 1 | 1 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
| 3 | 1 | 조립PC | desktop-custom | 1 | 2 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
| 4 | 1 | 베어본 | desktop-barebone | 1 | 3 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
| 5 | (NULL) | 노트북 | laptop | 0 | 2 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
| 6 | 5 | 일반 노트북 | laptop-general | 1 | 1 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
| 7 | 5 | 게이밍 노트북 | laptop-gaming | 1 | 2 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
| 8 | 5 | 2in1 | laptop-2in1 | 1 | 3 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

!!! warning "SELECT *는 학습용"
    `SELECT *`는 모든 칼럼을 가져오므로 대용량 테이블에서는 느릴 수 있습니다. 실무에서는 **필요한 칼럼만 명시**하는 습관을 들이세요. 이 튜토리얼에서도 다음부터는 칼럼을 직접 지정합니다.

---

## 특정 칼럼만 조회

칼럼 이름을 직접 나열하면 **원하는 칼럼만** 깔끔하게 볼 수 있습니다.

0강에서 실행했던 쿼리를 다시 봅니다:

```sql
SELECT name, price, stock_qty
FROM products;
```

**결과:**

| name | price | stock_qty |
| ---------- | ----------: | ----------: |
| Razer Blade 18 블랙 | 3730900.0 | 107 |
| MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 | 499 |
| 삼성 DDR4 32GB PC4-25600 | 46100.0 | 359 |
| Dell U2724D | 865000.0 | 337 |
| G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 161900.0 | 59 |
| MSI Radeon RX 9070 VENTUS 3X 화이트 | 618800.0 | 460 |
| 삼성 DDR5 32GB PC5-38400 | 194700.0 | 340 |
| 로지텍 G715 화이트 | 254400.0 | 341 |
| ... | ... | ... |

`SELECT *`보다 결과가 훨씬 읽기 쉽습니다. **칼럼 순서도 SELECT에서 나열한 순서대로** 결과가 나옵니다.

```sql
-- 순서를 바꾸면 결과 순서도 바뀜
SELECT stock_qty, name, price
FROM products;
```

| stock_qty | name | price |
| --------: | ---- | ----: |
| 107 | Razer Blade 18 블랙 | 2987500 |
| ... | ... | ... |

---

## 칼럼 별칭 (AS)

### 왜 별칭이 필요한가

결과 칼럼의 이름이 `stock_qty`이면 코드를 모르는 사람은 무슨 뜻인지 알기 어렵습니다. `AS`를 사용하면 **결과에서 보이는 칼럼 이름을 바꿀 수 있습니다.**

```sql
SELECT
    name      AS 상품명,
    price     AS 판매가,
    stock_qty AS 재고수량
FROM products;
```

**결과:**

| 상품명 | 판매가 | 재고수량 |
| ---------- | ----------: | ----------: |
| Razer Blade 18 블랙 | 3730900.0 | 107 |
| MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 | 499 |
| 삼성 DDR4 32GB PC4-25600 | 46100.0 | 359 |
| Dell U2724D | 865000.0 | 337 |
| G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 161900.0 | 59 |
| MSI Radeon RX 9070 VENTUS 3X 화이트 | 618800.0 | 460 |
| 삼성 DDR5 32GB PC5-38400 | 194700.0 | 340 |
| 로지텍 G715 화이트 | 254400.0 | 341 |
| ... | ... | ... |

!!! info "별칭은 결과에만 영향"
    `AS`는 테이블의 실제 칼럼 이름을 바꾸는 것이 아닙니다. **결과 화면에 보이는 이름만** 바꿉니다.

### 계산식에 별칭 붙이기

별칭은 계산 결과에 이름을 붙일 때 특히 유용합니다. 별칭이 없으면 칼럼 이름이 `price * 0.9` 같은 식 자체가 됩니다.

```sql
SELECT
    name,
    price,
    price * 0.9 AS 할인가
FROM products;
```

**결과:**

| name | price | 할인가 |
| ---------- | ----------: | ----------: |
| Razer Blade 18 블랙 | 3730900.0 | 3357810.0 |
| MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 | 1569600.0 |
| 삼성 DDR4 32GB PC4-25600 | 46100.0 | 41490.0 |
| Dell U2724D | 865000.0 | 778500.0 |
| G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 161900.0 | 145710.0 |
| MSI Radeon RX 9070 VENTUS 3X 화이트 | 618800.0 | 556920.0 |
| 삼성 DDR5 32GB PC5-38400 | 194700.0 | 175230.0 |
| 로지텍 G715 화이트 | 254400.0 | 228960.0 |
| ... | ... | ... |

### 문자열 리터럴 칼럼

실제 테이블에 없는 **고정 값**을 결과에 추가할 수도 있습니다:

```sql
SELECT
    name,
    price,
    'KRW' AS 통화
FROM products;
```

| name | price | 통화 |
| ---- | ----: | --- |
| Razer Blade 18 블랙 | 2987500 | KRW |
| ... | ... | ... |

## 테이블 별칭

`AS`는 칼럼뿐 아니라 **테이블에도** 별칭을 붙일 수 있습니다. 지금은 테이블 하나만 쓰니 필요 없어 보이지만, 7강(JOIN)에서 여러 테이블을 합칠 때 반드시 사용합니다.

```sql
-- products 테이블에 p라는 별칭을 붙임
SELECT p.name, p.price
FROM products AS p;
```

`products.name` 대신 `p.name`으로 짧게 쓸 수 있습니다. `AS`는 생략해도 됩니다:

```sql
-- AS 생략 (같은 결과)
SELECT p.name, p.price
FROM products p;
```

!!! tip "미리 알아두기"
    7강에서 `SELECT p.name, c.name FROM products p JOIN categories c ON ...`처럼 쓰게 됩니다. 두 테이블 모두 `name` 칼럼이 있으면 `p.name`과 `c.name`으로 구분해야 합니다. 지금은 "테이블에도 별칭을 붙일 수 있다"는 것만 기억하세요.

---

## 산술 연산

SELECT 안에서 사칙연산을 할 수 있습니다. 결과에만 나타나며, 원본 데이터는 변경되지 않습니다.

| 연산자 | 의미 | 예시 |
|:------:|------|------|
| `+` | 더하기 | `price + shipping_fee` |
| `-` | 빼기 | `price - cost_price` |
| `*` | 곱하기 | `price * 1.1` (10% 인상) |
| `/` | 나누기 | `price / 1000` (천 원 단위) |
| `%` | 나머지 | `id % 2` (홀짝 구분) |

```sql
SELECT
    name,
    price,
    cost_price,
    price - cost_price AS 마진
FROM products;
```

| name | price | cost_price | 마진 |
| ---- | ----: | ---------: | ---: |
| Razer Blade 18 블랙 | 2987500 | 3086700 | -99200 |
| MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 | 1360300 | 383700 |
| 삼성 DDR4 32GB PC4-25600 | 49100 | 37900 | 11200 |
| ... | ... | ... | ... |

> 첫 번째 상품의 마진이 **음수**(-99200)입니다. 원가가 판매가보다 높은 경우도 현실 데이터에는 존재합니다.

---

## DISTINCT — 중복 제거

### 언제 쓸까

"이 칼럼에 어떤 값들이 존재하는지" 알고 싶을 때 사용합니다. 예를 들어, 테크샵 고객의 등급 종류를 알고 싶다면:

```sql
SELECT DISTINCT grade
FROM customers;
```

**결과:**

| grade |
| ---------- |
| BRONZE |
| VIP |
| GOLD |
| SILVER |

4가지 등급이 있다는 것을 알 수 있습니다. DISTINCT가 없으면 5,230행이 모두 출력됩니다.

### NULL도 하나의 값으로 취급

```sql
SELECT DISTINCT gender
FROM customers;
```

| gender |
| ------ |
| M |
| (NULL) |
| F |

0강에서 배운 NULL이 여기서 나타납니다. 성별을 입력하지 않은 고객이 있으므로 NULL이 하나의 고유값으로 포함됩니다.

### 여러 칼럼에 DISTINCT

DISTINCT는 **나열된 칼럼의 조합**에 대해 중복을 제거합니다:

```sql
SELECT DISTINCT grade, gender
FROM customers;
```

| grade | gender |
| ----- | ------ |
| BRONZE | M |
| BRONZE | F |
| BRONZE | (NULL) |
| SILVER | M |
| SILVER | F |
| ... | ... |

`grade`와 `gender`의 **조합**이 고유한 행만 남습니다.

---

## 정리

| 문법 | 의미 | 예시 |
|------|------|------|
| `SELECT *` | 모든 칼럼 조회 | `SELECT * FROM products` |
| `SELECT 칼럼1, 칼럼2` | 특정 칼럼만 조회 | `SELECT name, price FROM products` |
| `AS 별칭` | 결과 칼럼 이름 변경 | `SELECT name AS 상품명` |
| `FROM 테이블 AS t` | 테이블 별칭 (JOIN 시 필수) | `FROM products p` |
| 산술 연산 | 계산 결과를 칼럼으로 | `SELECT price * 0.9 AS 할인가` |
| `DISTINCT` | 중복 제거 | `SELECT DISTINCT grade FROM customers` |

---

<!-- BEGIN_LESSON_EXERCISES -->

!!! note "레슨 복습 문제"
    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. 여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/index.md) 섹션을 참고하세요.

### 문제 1
`categories` 테이블의 모든 칼럼을 조회하세요.

??? success "정답"
    ```sql
    SELECT * FROM categories;
    ```


    **실행 결과** (총 53행 중 상위 7행)

    | id | parent_id | name | slug | depth | sort_order | is_active | created_at | updated_at |
    |---|---|---|---|---|---|---|---|---|
    | 1 | NULL | 데스크톱 PC | desktop-pc | 0 | 1 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    | 2 | 1 | 완제품 | desktop-prebuilt | 1 | 1 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    | 3 | 1 | 조립PC | desktop-custom | 1 | 2 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    | 4 | 1 | 베어본 | desktop-barebone | 1 | 3 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    | 5 | NULL | 노트북 | laptop | 0 | 2 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    | 6 | 5 | 일반 노트북 | laptop-general | 1 | 1 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    | 7 | 5 | 게이밍 노트북 | laptop-gaming | 1 | 2 | 1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |

### 문제 2
`products` 테이블에서 `name`과 `price`만 조회하세요.

??? success "정답"
    ```sql
    SELECT name, price FROM products;
    ```


    **실행 결과** (총 281행 중 상위 7행)

    | name | price |
    |---|---|
    | Razer Blade 18 블랙 | 2,987,500.00 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 |
    | 삼성 DDR4 32GB PC4-25600 | 43,500.00 |
    | Dell U2724D | 894,100.00 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 167,000.00 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 383,100.00 |
    | 삼성 DDR5 32GB PC5-38400 | 211,800.00 |

### 문제 3
`staff` 테이블에서 `department`, `role`, `name` 순서로 조회하세요.

??? success "정답"
    ```sql
    SELECT department, role, name FROM staff;
    ```


    **실행 결과** (5행)

    | department | role | name |
    |---|---|---|
    | 경영 | admin | 한민재 |
    | 경영 | admin | 장주원 |
    | 경영 | admin | 박경수 |
    | 영업 | manager | 이준혁 |
    | 마케팅 | manager | 권영희 |

### 문제 4
`customers` 테이블에서 `name`, `email`, `grade`를 조회하되 별칭을 `고객명`, `이메일`, `등급`으로 붙이세요.

??? success "정답"
    ```sql
    SELECT
        name  AS 고객명,
        email AS 이메일,
        grade AS 등급
    FROM customers;
    ```


    **실행 결과** (총 5,230행 중 상위 7행)

    | 고객명 | 이메일 | 등급 |
    |---|---|---|
    | 정준호 | user1@testmail.kr | BRONZE |
    | 김경수 | user2@testmail.kr | GOLD |
    | 김민재 | user3@testmail.kr | VIP |
    | 진정자 | user4@testmail.kr | GOLD |
    | 이정수 | user5@testmail.kr | SILVER |
    | 김준혁 | user6@testmail.kr | BRONZE |
    | 김명자 | user7@testmail.kr | BRONZE |

### 문제 5
`products` 테이블에서 `name`, `price`를 조회하고, 10% 할인된 가격을 `할인가`라는 별칭으로 추가하세요.

??? success "정답"
    ```sql
    SELECT name, price, price * 0.9 AS 할인가
    FROM products;
    ```


    **실행 결과** (총 281행 중 상위 7행)

    | name | price | 할인가 |
    |---|---|---|
    | Razer Blade 18 블랙 | 2,987,500.00 | 2,688,750.00 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | 1,569,600.00 |
    | 삼성 DDR4 32GB PC4-25600 | 43,500.00 | 39,150.00 |
    | Dell U2724D | 894,100.00 | 804,690.00 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 167,000.00 | 150,300.00 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 383,100.00 | 344,790.00 |
    | 삼성 DDR5 32GB PC5-38400 | 211,800.00 | 190,620.00 |

### 문제 6
`products` 테이블에서 `name`, `price`, `cost_price`를 조회하고, 마진(`price - cost_price`)과 마진율(`(price - cost_price) * 100 / price`)을 별칭 `마진`, `마진율`로 추가하세요.

??? success "정답"
    ```sql
    SELECT
        name,
        price,
        cost_price,
        price - cost_price                  AS 마진,
        (price - cost_price) * 100 / price  AS 마진율
    FROM products;
    ```


    **실행 결과** (총 281행 중 상위 7행)

    | name | price | cost_price | 마진 | 마진율 |
    |---|---|---|---|---|
    | Razer Blade 18 블랙 | 2,987,500.00 | 3,086,700.00 | -99,200.00 | -3.32 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | 1,360,300.00 | 383,700.00 | 22.00 |
    | 삼성 DDR4 32GB PC4-25600 | 43,500.00 | 37,900.00 | 5,600.00 | 12.87 |
    | Dell U2724D | 894,100.00 | 565,700.00 | 328,400.00 | 36.73 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 167,000.00 | 121,400.00 | 45,600.00 | 27.31 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 383,100.00 | 431,800.00 | -48,700.00 | -12.71 |
    | 삼성 DDR5 32GB PC5-38400 | 211,800.00 | 151,900.00 | 59,900.00 | 28.28 |

### 문제 7
`orders` 테이블에서 고유한 `status` 값을 조회하세요.

??? success "정답"
    ```sql
    SELECT DISTINCT status FROM orders;
    ```


    **실행 결과** (총 9행 중 상위 7행)

    | status |
    |---|
    | cancelled |
    | confirmed |
    | delivered |
    | paid |
    | pending |
    | preparing |
    | return_requested |

### 문제 8
`payments` 테이블에서 고유한 `method` 값을 조회하여, 테크샵이 지원하는 결제 수단을 확인하세요.

??? success "정답"
    ```sql
    SELECT DISTINCT method FROM payments;
    ```


    **실행 결과** (6행)

    | method |
    |---|
    | card |
    | kakao_pay |
    | naver_pay |
    | bank_transfer |
    | point |
    | virtual_account |

### 문제 9
`products` 테이블에서 `name`, `price`, `stock_qty`를 조회하고, `price * stock_qty`를 `재고가치`라는 별칭으로 추가하세요.

??? success "정답"
    ```sql
    SELECT name, price, stock_qty, price * stock_qty AS 재고가치
    FROM products;
    ```


    **실행 결과** (총 281행 중 상위 7행)

    | name | price | stock_qty | 재고가치 |
    |---|---|---|---|
    | Razer Blade 18 블랙 | 2,987,500.00 | 107 | 319,662,500.00 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | 499 | 870,256,000.00 |
    | 삼성 DDR4 32GB PC4-25600 | 43,500.00 | 359 | 15,616,500.00 |
    | Dell U2724D | 894,100.00 | 337 | 301,311,700.00 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 167,000.00 | 59 | 9,853,000.00 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 383,100.00 | 460 | 176,226,000.00 |
    | 삼성 DDR5 32GB PC5-38400 | 211,800.00 | 340 | 72,012,000.00 |

### 문제 10
`reviews` 테이블에서 고유한 `(product_id, rating)` 조합을 조회하고, `rating` 내림차순으로 정렬한 뒤 20행만 보세요.

??? success "정답"
    ```sql
    SELECT DISTINCT product_id, rating
    FROM reviews
    ORDER BY rating DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | product_id | rating |
    |---|---|
    | 1 | 5 |
    | 2 | 5 |
    | 3 | 5 |
    | 4 | 5 |
    | 5 | 5 |
    | 6 | 5 |
    | 7 | 5 |

<!-- END_LESSON_EXERCISES -->
