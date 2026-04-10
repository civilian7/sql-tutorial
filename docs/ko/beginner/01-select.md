# 1강: SELECT 기초

`SELECT` 문은 SQL의 근간입니다. 하나 이상의 테이블에서 데이터를 조회하며, 어떤 칼럼을 반환할지, 어떻게 표시할지를 정밀하게 지정할 수 있습니다.

```mermaid
flowchart LR
    T["🗄️ Table\n(all rows, all columns)"] --> S["SELECT\ncolumn1, column2"] --> R["📋 Result\n(all rows, selected columns)"]
```

> **개념:** SELECT는 테이블에서 원하는 칼럼만 골라서 보여줍니다.

## 전체 칼럼 조회

`SELECT *`를 사용하면 테이블의 모든 칼럼을 가져옵니다. 데이터를 빠르게 훑어볼 때 유용합니다.

```sql
SELECT * FROM products;
```

**결과:**

| id | category_id | supplier_id | successor_id | name              | sku              | brand | model_number | description                             | specs                                                                                                                 | price   | cost_price | stock_qty | weight_grams | is_active | discontinued_at | created_at          | updated_at          |
| -: | ----------: | ----------: | -----------: | ----------------- | ---------------- | ----- | ------------ | --------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------: | ---------: | --------: | -----------: | --------: | --------------- | ------------------- | ------------------- |
|  1 |           7 |          20 |       (NULL) | Razer Blade 18 블랙 | LA-GAM-RAZ-00001 | Razer | RAZ-00001    | Razer Razer Blade 18 블랙 - 고성능, 최신 기술 탑재 | {"screen_size": "14 inch", "cpu": "Apple M3", "ram": "8GB", "storage": "256GB", "weight_kg": 1.7, "battery_hours": 6} | 2987500 |    3086700 |       107 |         2556 |         1 | (NULL)          | 2016-11-20 02:59:21 | 2016-11-20 02:59:21 |
| ... | ...         | ...         | ...          | ...               | ...              | ...   | ...          | ...                                     | ...                                                                                                                   | ...     | ...        | ...       | ...          | ...       | ...             | ...                 | ...                 |

> **팁:** `SELECT *`는 모든 칼럼을 가져오므로 대용량 테이블에서는 속도가 느릴 수 있습니다. 실제 운영 환경에서는 필요한 칼럼만 명시하는 것이 좋습니다.

## 특정 칼럼만 조회

칼럼 이름을 직접 나열하면 원하는 칼럼만 반환됩니다. 결과가 깔끔해지고 전송 데이터양도 줄어듭니다.

```sql
SELECT name, price, stock_qty
FROM products;
```

**결과:**

| name                                   | price   | stock_qty |
| -------------------------------------- | ------: | --------: |
| Razer Blade 18 블랙                      | 2987500 |       107 |
| MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |       499 |
| 삼성 DDR4 32GB PC4-25600                 |   49100 |       359 |
| ...                                    | ...     | ...       |

## 칼럼 별칭 (AS)

`AS`를 사용하면 결과에서 칼럼 이름을 바꿀 수 있습니다. 가독성을 높이고, 이름이 없는 계산식에 이름을 붙일 때 특히 유용합니다.

```sql
SELECT
    name        AS product_name,
    price       AS unit_price,
    stock_qty   AS in_stock
FROM products;
```

**결과:**

| product_name                           | unit_price | in_stock |
| -------------------------------------- | ---------: | -------: |
| Razer Blade 18 블랙                      |    2987500 |      107 |
| MSI GeForce RTX 4070 Ti Super GAMING X |    1744000 |      499 |
| 삼성 DDR4 32GB PC4-25600                 |      49100 |      359 |
| ...                                    | ...        | ...      |

계산식에도 별칭을 붙일 수 있습니다.

```sql
SELECT
    name,
    price * 1.1 AS price_with_tax
FROM products;
```

**결과:**

| name                                   | price_with_tax |
| -------------------------------------- | -------------: |
| Razer Blade 18 블랙                      |        3286250 |
| MSI GeForce RTX 4070 Ti Super GAMING X |        1918400 |
| ...                                    | ...            |

## DISTINCT

`DISTINCT`는 결과에서 중복 값을 제거합니다. 칼럼에 어떤 값들이 존재하는지 확인할 때 유용합니다.

```sql
-- 고객 등급에 어떤 값들이 있는지 확인
SELECT DISTINCT grade
FROM customers;
```

**결과:**

| grade  |
| ------ |
| BRONZE |
| VIP    |
| SILVER |
| GOLD   |

```sql
-- 성별 고유값 조회 (NULL 포함)
SELECT DISTINCT gender
FROM customers;
```

**결과:**

| gender |
| ------ |
| M      |
| (NULL) |
| F      |

## 기법 조합

```sql
-- 고객의 활성/비활성 상태 고유값 조회
SELECT DISTINCT is_active AS status
FROM customers
ORDER BY is_active;
```

**결과:**

| status |
| -----: |
|      0 |
|      1 |

!!! note "레슨 복습 문제"
    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. 여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/index.md) 섹션을 참고하세요.

## 연습 문제

### 문제 1
모든 고객의 `name`, `email`, `grade`를 조회하세요. 각 칼럼에 `full_name`, `email_address`, `membership_tier`라는 별칭을 붙이세요.

??? success "정답"
    ```sql
    SELECT
        name        AS full_name,
        email       AS email_address,
        grade       AS membership_tier
    FROM customers;
    ```

    **결과 (예시):**

    | full_name | email_address     | membership_tier |
    | --------- | ----------------- | --------------- |
    | 정준호       | user1@testmail.kr | BRONZE          |
    | 김경수       | user2@testmail.kr | VIP             |
    | 김민재       | user3@testmail.kr | VIP             |
    | 진정자       | user4@testmail.kr | VIP             |
    | 이정수       | user5@testmail.kr | SILVER          |
    | ...       | ...               | ...             |


### 문제 2
`payments` 테이블에서 `method` 칼럼의 고유값을 모두 조회하여 TechShop이 지원하는 결제 수단을 확인하세요.

??? success "정답"
    ```sql
    SELECT DISTINCT method
    FROM payments;
    ```

    **결과 (예시):**

    | method        |
    | ------------- |
    | card          |
    | point         |
    | kakao_pay     |
    | bank_transfer |
    | naver_pay     |
    | ...           |


### 문제 3
`products` 테이블에서 `name`, `price`, `stock_qty`를 조회하세요. 그리고 `price * stock_qty`로 계산된 `inventory_value`라는 칼럼을 추가하세요.

??? success "정답"
    ```sql
    SELECT
        name,
        price,
        stock_qty,
        price * stock_qty AS inventory_value
    FROM products;
    ```

    **결과 (예시):**

    | name                                     | price   | stock_qty | inventory_value |
    | ---------------------------------------- | ------: | --------: | --------------: |
    | Razer Blade 18 블랙                        | 2987500 |       107 |       319662500 |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 |       499 |       870256000 |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 |       359 |        17626900 |
    | Dell U2724D                              |  853600 |       337 |       287663200 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 |        59 |         7711300 |
    | ...                                      | ...     | ...       | ...             |


### 문제 4
`categories` 테이블의 모든 칼럼을 조회하세요.

??? success "정답"
    ```sql
    SELECT * FROM categories;
    ```

    **결과 (예시):**

    | id | parent_id | name    | slug             | depth | sort_order | is_active | created_at          | updated_at          |
    | -: | --------: | ------- | ---------------- | ----: | ---------: | --------: | ------------------- | ------------------- |
    |  1 |    (NULL) | 데스크톱 PC | desktop-pc       |     0 |          1 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  2 |         1 | 완제품     | desktop-prebuilt |     1 |          1 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  3 |         1 | 조립PC    | desktop-custom   |     1 |          2 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  4 |         1 | 베어본     | desktop-barebone |     1 |          3 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  5 |    (NULL) | 노트북     | laptop           |     0 |          2 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    | ... | ...       | ...     | ...              | ...   | ...        | ...       | ...                 | ...                 |


### 문제 5
`staff` 테이블에서 `name`, `department`, `role`을 조회하되, 칼럼 순서를 `department`, `role`, `name`으로 바꿔서 출력하세요.

??? success "정답"
    ```sql
    SELECT department, role, name
    FROM staff;
    ```

    **결과 (예시):**

    | department | role    | name |
    | ---------- | ------- | ---- |
    | 경영         | admin   | 한민재  |
    | 경영         | admin   | 장주원  |
    | 경영         | admin   | 박경수  |
    | 영업         | manager | 이준혁  |
    | 마케팅        | manager | 권영희  |


### 문제 6
`orders` 테이블에서 고유한 `status` 값을 조회하세요.

??? success "정답"
    ```sql
    SELECT DISTINCT status
    FROM orders;
    ```

    **결과 (예시):**

    | status    |
    | --------- |
    | cancelled |
    | confirmed |
    | delivered |
    | paid      |
    | pending   |
    | ...       |


### 문제 7
`products` 테이블에서 `name`과 `price`를 조회하면서, 10% 할인된 가격을 `discounted_price`라는 별칭으로 함께 출력하세요.

??? success "정답"
    ```sql
    SELECT
        name,
        price,
        price * 0.9 AS discounted_price
    FROM products;
    ```

    **결과 (예시):**

    | name                                     | price   | discounted_price |
    | ---------------------------------------- | ------: | ---------------: |
    | Razer Blade 18 블랙                        | 2987500 |          2688750 |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 |          1569600 |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 |            44190 |
    | Dell U2724D                              |  853600 |           768240 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 |           117630 |
    | ...                                      | ...     | ...              |


### 문제 8
`products` 테이블에서 `name`과 `price`를 조회하면서, 모든 행에 `'KRW'`라는 문자열 리터럴을 `currency`라는 별칭의 칼럼으로 추가하세요.

??? success "정답"
    ```sql
    SELECT
        name,
        price,
        'KRW' AS currency
    FROM products;
    ```

    **결과 (예시):**

    | name                                     | price   | currency |
    | ---------------------------------------- | ------: | -------- |
    | Razer Blade 18 블랙                        | 2987500 | KRW      |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 | KRW      |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 | KRW      |
    | Dell U2724D                              |  853600 | KRW      |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 | KRW      |
    | ...                                      | ...     | ...      |


### 문제 9
`suppliers` 테이블에서 고유한 `contact_name`과 `company_name` 조합을 조회하세요. (DISTINCT를 여러 칼럼에 사용)

??? success "정답"
    ```sql
    SELECT DISTINCT contact_name, company_name
    FROM suppliers;
    ```

    **결과 (예시):**

    | contact_name | company_name |
    | ------------ | ------------ |
    | 김수민          | 삼성전자 공식 유통   |
    | 김예준          | LG전자 공식 유통   |
    | 이상현          | 인텔코리아        |
    | 강중수          | AMD코리아       |
    | 이정남          | 엔비디아코리아      |
    | ...          | ...          |


### 문제 10
`products` 테이블에서 `name`, `price`, `cost_price`를 조회하고, 마진(`price - cost_price`)을 `margin`으로, 마진율(`(price - cost_price) / price * 100`)을 `margin_pct`라는 별칭으로 함께 출력하세요.

??? success "정답"
    ```sql
    SELECT
        name,
        price,
        cost_price,
        price - cost_price                    AS margin,
        (price - cost_price) / price * 100    AS margin_pct
    FROM products;
    ```

    **결과 (예시):**

    | name                                     | price   | cost_price | margin | margin_pct |
    | ---------------------------------------- | ------: | ---------: | -----: | ---------: |
    | Razer Blade 18 블랙                        | 2987500 |    3086700 | -99200 |      -3.32 |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 |    1360300 | 383700 |         22 |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 |      37900 |  11200 |      22.81 |
    | Dell U2724D                              |  853600 |     565700 | 287900 |      33.73 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 |     121400 |   9300 |       7.12 |
    | ...                                      | ...     | ...        | ...    | ...        |


---
다음: [2강: WHERE로 데이터 필터링](02-where.md)
