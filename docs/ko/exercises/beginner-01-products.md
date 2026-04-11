# 상품 데이터 탐색

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `products` (280행) --- 상품 정보 (이름, 가격, 재고, 브랜드 등)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT`, 별칭(`AS`)

</div>

!!! info "시작하기 전에"
    이 연습은 **입문 1~2강**(SELECT, WHERE)에서 배운 내용만 사용합니다.
    JOIN, 서브쿼리, GROUP BY, 집계 함수는 사용하지 않습니다.

---

## 기초 (1~10)

한 가지 개념씩 연습합니다.

---

### 문제 1

**상품 테이블의 전체 데이터를 조회하세요.**

??? tip "힌트"
    `SELECT *`를 사용하면 모든 칼럼을 한꺼번에 조회할 수 있습니다.

??? success "정답"
    ```sql
    SELECT *
    FROM products;
    ```

    **결과 (상위 5행):**

    | id | category_id | supplier_id | name | brand | price | stock_qty | is_active |
    |----|-------------|-------------|------|-------|-------|-----------|-----------|
    | 1 | 7 | 20 | Razer Blade 18 블랙 | Razer | 2987500 | 107 | 1 |
    | 2 | 28 | 27 | MSI GeForce RTX 4070 Ti Super GAMING X | MSI | 1744000 | 499 | 1 |
    | 3 | 21 | 1 | 삼성 DDR4 32GB PC4-25600 | 삼성전자 | 49100 | 359 | 1 |
    | 4 | 11 | 31 | Dell U2724D | Dell | 853600 | 337 | 1 |
    | 5 | 22 | 48 | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | G.SKILL | 130700 | 59 | 1 |

    > 실제 결과에는 18개 칼럼이 모두 표시됩니다. 총 280행이 반환됩니다.

---

### 문제 2

**상품의 이름(`name`), 가격(`price`), 재고 수량(`stock_qty`)만 조회하세요.**

??? tip "힌트"
    `SELECT` 뒤에 원하는 칼럼명을 쉼표로 구분하여 나열합니다.

??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products;
    ```

    **결과 (상위 5행):**

    | name | price | stock_qty |
    |------|-------|-----------|
    | Razer Blade 18 블랙 | 2987500 | 107 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 | 499 |
    | 삼성 DDR4 32GB PC4-25600 | 49100 | 359 |
    | Dell U2724D | 853600 | 337 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 130700 | 59 |

---

### 문제 3

**브랜드가 'ASUS'인 상품의 이름과 가격을 조회하세요.**

??? tip "힌트"
    `WHERE` 절에서 `=` 연산자로 정확히 일치하는 값을 필터링합니다. 문자열은 작은따옴표로 감쌉니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE brand = 'ASUS';
    ```

    **결과 (상위 5행):**

    | name | price |
    |------|-------|
    | ASUS ROG Strix G16CH 화이트 | 2988700 |
    | ASUS TUF Gaming RTX 5080 화이트 | 3812000 |
    | ASUS ROG Strix Scar 16 실버 | 1586000 |
    | ASUS ExpertBook B5 화이트 | 2126600 |
    | ASUS PCE-BE92BT | 48800 |

---

### 문제 4

**가격이 1,000,000원을 초과하는 상품의 이름과 가격을 조회하세요.**

??? tip "힌트"
    `WHERE` 절에서 `>` (초과) 비교 연산자를 사용합니다. 숫자는 따옴표 없이 씁니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > 1000000;
    ```

    **결과 (상위 5행):**

    | name | price |
    |------|-------|
    | Razer Blade 18 블랙 | 2987500 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
    | ASUS ROG Strix G16CH 화이트 | 2988700 |
    | ASUS TUF Gaming RTX 5080 화이트 | 3812000 |
    | ASUS ROG Strix Scar 16 실버 | 1586000 |

---

### 문제 5

**판매 중단된 상품(`is_active = 0`)의 이름, 가격, 단종일(`discontinued_at`)을 조회하세요.**

??? tip "힌트"
    `is_active`는 1(판매 중) 또는 0(판매 중단)을 저장하는 칼럼입니다. `WHERE is_active = 0`으로 필터링합니다.

??? success "정답"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE is_active = 0;
    ```

    **결과 (상위 5행):**

    | name | price | discontinued_at |
    |------|-------|-----------------|
    | 소니 WH-CH720N 실버 | 249800 | 2023-09-21 01:03:38 |
    | WD Elements 2TB 블랙 | 265600 | 2024-08-25 09:29:10 |
    | JBL Quantum ONE 화이트 | 179400 | 2023-06-01 06:11:13 |
    | 주연 리오나인 i7 시스템 실버 | 1102700 | 2023-05-08 03:08:52 |
    | ASUS TUF Gaming RTX 5080 화이트 | 3812000 | 2017-05-15 20:10:25 |

---

### 문제 6

**가격이 500,000원 이상 1,000,000원 이하인 상품의 이름과 가격을 조회하세요.**

??? tip "힌트"
    `BETWEEN A AND B`는 A 이상 B 이하인 범위를 필터링합니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE price BETWEEN 500000 AND 1000000;
    ```

    **결과 (상위 5행):**

    | name | price |
    |------|-------|
    | Dell U2724D | 853600 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 584100 |
    | 넷기어 Nighthawk RS700S 블랙 | 503600 |
    | ASRock X670E Steel Legend 실버 | 508700 |
    | 보스 SoundLink Flex 블랙 | 516000 |

---

### 문제 7

**브랜드가 'ASUS', 'MSI', 'Logitech' 중 하나인 상품의 이름, 브랜드, 가격을 조회하세요.**

??? tip "힌트"
    `IN (값1, 값2, 값3)`을 사용하면 여러 값 중 하나와 일치하는 행을 한번에 필터링할 수 있습니다.

??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand IN ('ASUS', 'MSI', 'Logitech');
    ```

    **결과 (상위 5행):**

    | name | brand | price |
    |------|-------|-------|
    | MSI GeForce RTX 4070 Ti Super GAMING X | MSI | 1744000 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | MSI | 584100 |
    | MSI MAG X870E TOMAHAWK WIFI 화이트 | MSI | 469800 |
    | ASUS ROG Strix G16CH 화이트 | ASUS | 2988700 |
    | ASUS TUF Gaming RTX 5080 화이트 | ASUS | 3812000 |

---

### 문제 8

**상품명에 'Gaming'이 포함된 상품의 이름과 가격을 조회하세요.**

??? tip "힌트"
    `LIKE '%문자열%'`은 해당 문자열이 어디든 포함된 행을 찾습니다. `%`는 0개 이상의 임의 문자를 의미합니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%Gaming%';
    ```

    **결과 (상위 5행):**

    | name | price |
    |------|-------|
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
    | ASUS TUF Gaming RTX 5080 화이트 | 3812000 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트 | 1478100 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | 408800 |
    | MSI Radeon RX 9070 XT GAMING X | 1788500 |

---

### 문제 9

**모든 상품을 가격이 비싼 순서대로 정렬하여 이름과 가격을 조회하세요.**

??? tip "힌트"
    `ORDER BY 칼럼명 DESC`는 내림차순(큰 값 → 작은 값) 정렬입니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC;
    ```

    **결과 (상위 5행):**

    | name | price |
    |------|-------|
    | ASUS ROG Strix GT35 | 4314800 |
    | ASUS ROG Zephyrus G16 | 4284100 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] ... | 4226200 |
    | Razer Blade 18 블랙 | 4182100 |
    | Razer Blade 16 실버 | 4123800 |

---

### 문제 10

**가격이 가장 비싼 상위 5개 상품의 이름과 가격을 조회하세요.**

??? tip "힌트"
    `ORDER BY`로 정렬한 뒤 `LIMIT N`을 붙이면 상위 N개만 가져옵니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5;
    ```

    **결과:**

    | name | price |
    |------|-------|
    | ASUS ROG Strix GT35 | 4314800 |
    | ASUS ROG Zephyrus G16 | 4284100 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] ... | 4226200 |
    | Razer Blade 18 블랙 | 4182100 |
    | Razer Blade 16 실버 | 4123800 |

---

## 응용 (11~20)

두 가지 개념을 조합하여 연습합니다.

---

### 문제 11

**판매 중인 상품(`is_active = 1`)을 가격이 저렴한 순서대로 정렬하여 이름과 가격을 조회하세요.**

??? tip "힌트"
    `WHERE`로 조건을 걸고 `ORDER BY 칼럼 ASC`로 오름차순 정렬합니다. ASC는 생략 가능합니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE is_active = 1
    ORDER BY price ASC;
    ```

    **결과 (상위 5행):**

    | name | price |
    |------|-------|
    | TP-Link TG-3468 블랙 | 13100 |
    | Microsoft Ergonomic Keyboard 실버 | 23000 |
    | TP-Link Archer TBE400E 화이트 | 23300 |
    | 삼성 SPA-KFG0BUB | 26200 |
    | 삼성 SPA-KFG0BUB 실버 | 27500 |

---

### 문제 12

**판매 중인 상품 중 가장 저렴한 10개의 이름과 가격을 조회하세요.**

??? tip "힌트"
    `WHERE`로 판매 중인 상품을 필터링하고, `ORDER BY`로 가격 오름차순 정렬 후, `LIMIT 10`을 붙입니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE is_active = 1
    ORDER BY price ASC
    LIMIT 10;
    ```

    **결과:**

    | name | price |
    |------|-------|
    | TP-Link TG-3468 블랙 | 13100 |
    | Microsoft Ergonomic Keyboard 실버 | 23000 |
    | TP-Link Archer TBE400E 화이트 | 23300 |
    | 삼성 SPA-KFG0BUB | 26200 |
    | 삼성 SPA-KFG0BUB 실버 | 27500 |
    | V3 Endpoint Security 블랙 | 28500 |
    | Arctic Freezer 36 A-RGB 화이트 | 29800 |
    | Arctic Freezer 36 A-RGB 화이트 | 31400 |
    | Microsoft Ergonomic Keyboard 화이트 | 35400 |
    | 로지텍 G402 실버 | 36000 |

---

### 문제 13

**판매 중이면서 가격이 2,000,000원을 초과하는 상품의 이름과 가격을 비싼 순으로 조회하세요.**

??? tip "힌트"
    `AND`를 사용하면 두 조건을 **모두** 만족하는 행만 필터링합니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE is_active = 1 AND price > 2000000
    ORDER BY price DESC;
    ```

    **결과 (상위 5행):**

    | name | price |
    |------|-------|
    | ASUS ROG Strix GT35 | 4314800 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] ... | 4226200 |
    | Razer Blade 18 블랙 | 4182100 |
    | Razer Blade 16 실버 | 4123800 |
    | MacBook Air 15 M3 실버 | 3774700 |

---

### 문제 14

**브랜드가 'ASUS' 또는 'MSI'인 상품의 이름, 브랜드, 가격을 조회하세요.**

??? tip "힌트"
    `OR`는 두 조건 중 **하나라도** 만족하면 결과에 포함합니다.

??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand = 'ASUS' OR brand = 'MSI';
    ```

    **결과 (상위 5행):**

    | name | brand | price |
    |------|-------|-------|
    | MSI GeForce RTX 4070 Ti Super GAMING X | MSI | 1744000 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | MSI | 584100 |
    | MSI MAG X870E TOMAHAWK WIFI 화이트 | MSI | 469800 |
    | ASUS ROG Strix G16CH 화이트 | ASUS | 2988700 |
    | ASUS TUF Gaming RTX 5080 화이트 | ASUS | 3812000 |

---

### 문제 15

**단종되지 않은 상품(`discontinued_at`이 비어 있는)의 이름과 가격을 조회하세요.**

??? tip "힌트"
    값이 비어 있는(NULL) 행을 찾으려면 `= NULL`이 아니라 `IS NULL`을 사용해야 합니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE discontinued_at IS NULL;
    ```

    **결과 (상위 5행):**

    | name | price |
    |------|-------|
    | Razer Blade 18 블랙 | 2987500 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
    | 삼성 DDR4 32GB PC4-25600 | 49100 |
    | Dell U2724D | 853600 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 130700 |

---

### 문제 16

**상품명에 'RTX'가 포함된 상품의 이름과 가격을 비싼 순으로 조회하세요.**

??? tip "힌트"
    `LIKE`로 패턴 매칭 후 `ORDER BY`로 정렬합니다. 두 절을 함께 사용할 수 있습니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%RTX%'
    ORDER BY price DESC;
    ```

    **결과 (상위 5행):**

    | name | price |
    |------|-------|
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] ... | 4226200 |
    | ASUS TUF Gaming RTX 5080 화이트 | 3812000 |
    | ASUS Dual RTX 4060 Ti 블랙 | 2003500 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
    | 기가바이트 RTX 4090 AERO OC 화이트 | 1357300 |

---

### 문제 17

**가격이 1,000,000원~3,000,000원인 상품을 재고 수량이 많은 순으로 상위 10개만 조회하세요.**

??? tip "힌트"
    `BETWEEN`으로 가격 범위를 지정하고, `ORDER BY stock_qty DESC`로 재고 많은 순 정렬, `LIMIT 10`으로 제한합니다.

??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE price BETWEEN 1000000 AND 3000000
    ORDER BY stock_qty DESC
    LIMIT 10;
    ```

    **결과:**

    | name | price | stock_qty |
    |------|-------|-----------|
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 | 499 |
    | SAPPHIRE PULSE RX 7800 XT 실버 | 1311600 | 490 |
    | LG 그램 14 | 2164900 | 490 |
    | MSI Radeon RX 9070 XT GAMING X | 1788500 | 482 |
    | HP Slim Desktop S01 화이트 | 1255100 | 481 |
    | Razer Blade 18 | 2349600 | 460 |
    | ASUS Dual RX 9070 실버 | 1515100 | 454 |
    | LG 27UQ85R | 2140600 | 440 |
    | HP Z2 Mini G1a 블랙 | 1166400 | 430 |
    | HP EliteBook 840 G10 실버 | 1231800 | 429 |

---

### 문제 18

**카테고리 ID가 1, 2, 3에 속하는 상품의 이름, 카테고리 ID, 가격을 조회하세요.**

??? tip "힌트"
    `IN`은 문자열뿐 아니라 숫자에도 사용할 수 있습니다. `category_id IN (1, 2, 3)`으로 필터링합니다.

??? success "정답"
    ```sql
    SELECT name, category_id, price
    FROM products
    WHERE category_id IN (1, 2, 3);
    ```

    **결과 (상위 5행):**

    | name | category_id | price |
    |------|-------------|-------|
    | LG 일체형PC 27V70Q 실버 | 2 | 1292200 |
    | HP Slim Desktop S01 화이트 | 2 | 1255100 |
    | Dell XPS Desktop 8960 실버 | 2 | 1249400 |
    | HP Z2 Mini G1a 블랙 | 2 | 1166400 |
    | 삼성 DM500TDA 실버 | 2 | 1035200 |

    > 카테고리 1=데스크톱 PC, 2=완제품, 3=조립PC에 해당합니다.

---

### 문제 19

**각 상품의 이름, 판매가(`price`), 원가(`cost_price`), 마진(`price - cost_price`)을 조회하세요. 마진 칼럼에는 `margin`이라는 별칭을 붙이세요.**

??? tip "힌트"
    `SELECT` 절에서 산술 연산(`+`, `-`, `*`, `/`)을 할 수 있습니다. `AS 별칭`으로 칼럼 이름을 지정합니다.

??? success "정답"
    ```sql
    SELECT name, price, cost_price, price - cost_price AS margin
    FROM products;
    ```

    **결과 (상위 5행):**

    | name | price | cost_price | margin |
    |------|-------|------------|--------|
    | Razer Blade 18 블랙 | 2987500 | 3086700 | -99200 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 | 1360300 | 383700 |
    | 삼성 DDR4 32GB PC4-25600 | 49100 | 37900 | 11200 |
    | Dell U2724D | 853600 | 565700 | 287900 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 130700 | 121400 | 9300 |

    > 마진이 음수인 상품은 원가보다 싸게 판매하는 것입니다 (역마진).

---

### 문제 20

**상품 테이블에 등록된 브랜드 목록을 중복 없이 조회하세요.**

??? tip "힌트"
    `DISTINCT`를 `SELECT` 바로 뒤에 붙이면 중복된 값을 제거합니다.

??? success "정답"
    ```sql
    SELECT DISTINCT brand
    FROM products
    ORDER BY brand;
    ```

    **결과 (상위 10행):**

    | brand |
    |-------|
    | AMD |
    | APC |
    | ASRock |
    | ASUS |
    | Adobe |
    | Apple |
    | Arctic |
    | BenQ |
    | CORSAIR |
    | Crucial |

---

## 실전 (21~30)

여러 개념을 조합하는 복합 문제입니다.

---

### 문제 21

**판매 중이면서 가격이 1,000,000원을 초과하는 상품을 비싼 순으로 상위 10개만 조회하세요. 이름과 가격을 출력합니다.**

??? tip "힌트"
    `WHERE`에 `AND`로 두 조건을 결합하고, `ORDER BY`와 `LIMIT`를 차례로 붙입니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE is_active = 1 AND price > 1000000
    ORDER BY price DESC
    LIMIT 10;
    ```

    **결과:**

    | name | price |
    |------|-------|
    | ASUS ROG Strix GT35 | 4314800 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] ... | 4226200 |
    | Razer Blade 18 블랙 | 4182100 |
    | Razer Blade 16 실버 | 4123800 |
    | MacBook Air 15 M3 실버 | 3774700 |
    | MSI GeForce RTX 5090 SUPRIM | 3672500 |
    | ASUS ROG Strix G16CH 화이트 | 2988700 |
    | MacBook Air 13 M3 블랙 | 2888300 |
    | ASUS ExpertBook B5 화이트 | 2126600 |
    | BenQ PD3225U | 2500400 |

---

### 문제 22

**브랜드가 'ASUS' 또는 'MSI'이면서 가격이 2,000,000원을 초과하는 상품의 이름, 브랜드, 가격을 비싼 순으로 조회하세요.**

??? tip "힌트"
    `OR` 조건을 **괄호**로 묶어야 `AND`와 올바르게 결합됩니다. `(A OR B) AND C` 형태입니다.

??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE (brand = 'ASUS' OR brand = 'MSI') AND price > 2000000
    ORDER BY price DESC;
    ```

    **결과 (상위 5행):**

    | name | brand | price |
    |------|-------|-------|
    | ASUS ROG Strix GT35 | ASUS | 4314800 |
    | ASUS ROG Zephyrus G16 | ASUS | 4284100 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] ... | ASUS | 4226200 |
    | ASUS TUF Gaming RTX 5080 화이트 | ASUS | 3812000 |
    | ASUS ROG Strix G16CH 화이트 | ASUS | 2988700 |

---

### 문제 23

**상품명에 '화이트'가 포함되지 않는 판매 중인 상품의 이름과 가격을 비싼 순으로 조회하세요.**

??? tip "힌트"
    `NOT LIKE`를 사용하면 특정 패턴을 **제외**할 수 있습니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE name NOT LIKE '%화이트%' AND is_active = 1
    ORDER BY price DESC;
    ```

    **결과 (상위 5행):**

    | name | price |
    |------|-------|
    | ASUS ROG Strix GT35 | 4314800 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] ... | 4226200 |
    | Razer Blade 18 블랙 | 4182100 |
    | Razer Blade 16 실버 | 4123800 |
    | MacBook Air 15 M3 실버 | 3774700 |

---

### 문제 24

**가격이 500,000원~2,000,000원이고 상품명에 'RTX'가 포함된 상품의 이름과 가격을 비싼 순으로 조회하세요.**

??? tip "힌트"
    `BETWEEN`과 `LIKE`를 `AND`로 결합합니다. 세 조건 모두 만족해야 합니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE price BETWEEN 500000 AND 2000000
      AND name LIKE '%RTX%'
    ORDER BY price DESC;
    ```

    **결과:**

    | name | price |
    |------|-------|
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
    | 기가바이트 RTX 4090 AERO OC 화이트 | 1357300 |
    | 기가바이트 RTX 5090 AERO OC | 1209600 |
    | ASUS Dual RTX 5070 Ti 실버 | 1043900 |

---

### 문제 25

**각 상품의 마진(판매가 - 원가)을 계산하고, 마진이 큰 순서대로 상위 5개를 조회하세요. 이름, 판매가, 원가, 마진을 출력합니다.**

??? tip "힌트"
    `ORDER BY`에서 별칭(alias)을 사용할 수 있습니다. `ORDER BY margin DESC`처럼 씁니다.

??? success "정답"
    ```sql
    SELECT name, price, cost_price, price - cost_price AS margin
    FROM products
    ORDER BY margin DESC
    LIMIT 5;
    ```

    **결과:**

    | name | price | cost_price | margin |
    |------|-------|------------|--------|
    | Razer Blade 16 실버 | 4123800 | 2886700 | 1237100 |
    | ASUS ROG Zephyrus G16 | 4284100 | 3084600 | 1199500 |
    | BenQ PD3225U | 2500400 | 1312500 | 1187900 |
    | Razer Blade 18 블랙 | 4182100 | 3047200 | 1134900 |
    | ASUS ROG Strix GT35 | 4314800 | 3236100 | 1078700 |

---

### 문제 26

**단종된 상품(`discontinued_at`이 비어 있지 않은)의 이름, 가격, 단종일을 최근 단종 순으로 상위 5개 조회하세요.**

??? tip "힌트"
    `IS NOT NULL`은 값이 비어 있지 않은 행을 필터링합니다. `IS NULL`의 반대입니다.

??? success "정답"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL
    ORDER BY discontinued_at DESC
    LIMIT 5;
    ```

    **결과:**

    | name | price | discontinued_at |
    |------|-------|-----------------|
    | Dell XPS Desktop 8960 실버 | 1249400 | 2025-11-20 15:30:12 |
    | Kingston FURY Beast DDR4 16GB 화이트 | 82700 | 2025-11-18 04:06:13 |
    | Intel Core Ultra 7 265K | 201900 | 2025-11-16 21:11:33 |
    | 한성 보스몬스터 DX7700 화이트 | 1624400 | 2025-10-25 03:47:01 |
    | Intel Core Ultra 7 265K 화이트 | 186800 | 2025-08-24 00:34:53 |

---

### 문제 27

**재고가 0개이면서 아직 판매 중(`is_active = 1`)인 상품의 이름, 가격, 재고 수량을 조회하세요.**

??? tip "힌트"
    `stock_qty = 0`과 `is_active = 1`을 `AND`로 결합합니다. 재고가 바닥났지만 아직 내려지지 않은 상품입니다.

??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE stock_qty = 0 AND is_active = 1;
    ```

    **결과:**

    | name | price | stock_qty |
    |------|-------|-----------|
    | Arctic Freezer 36 A-RGB 화이트 | 31400 | 0 |

    > 현재 1개 상품만 해당합니다. 실제 쇼핑몰에서는 품절 상품 관리가 중요합니다.

---

### 문제 28

**판매 중이고, 가격이 500,000원~2,000,000원이며, 재고가 20개를 초과하는 상품을 가격 오름차순으로 조회하세요. 이름, 가격, 재고 수량을 출력합니다.**

??? tip "힌트"
    `AND`로 여러 조건을 연결합니다. 조건이 3개 이상이어도 `AND`를 계속 이어 붙이면 됩니다.

??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE is_active = 1
      AND price BETWEEN 500000 AND 2000000
      AND stock_qty > 20
    ORDER BY price;
    ```

    **결과 (상위 5행):**

    | name | price | stock_qty |
    |------|-------|-----------|
    | 넷기어 Nighthawk RS700S 블랙 | 503600 | 352 |
    | ASRock X670E Steel Legend 실버 | 508700 | 402 |
    | 보스 SoundLink Flex 블랙 | 516000 | 134 |
    | 삼성 ViewFinity S8 | 518400 | 354 |
    | MSI MAG Z890 TOMAHAWK WIFI 블랙 | 526900 | 394 |

---

### 문제 29

**무게(`weight_grams`)가 5,000g을 초과하는 상품의 이름, 무게, 가격을 무게가 무거운 순으로 조회하세요.**

??? tip "힌트"
    `weight_grams > 5000`으로 필터링하고 `ORDER BY weight_grams DESC`로 정렬합니다.

??? success "정답"
    ```sql
    SELECT name, weight_grams, price
    FROM products
    WHERE weight_grams > 5000
    ORDER BY weight_grams DESC;
    ```

    **결과 (상위 5행):**

    | name | weight_grams | price |
    |------|-------------|-------|
    | ASUS ROG Strix GT35 | 19449 | 4314800 |
    | 한성 보스몬스터 DX7700 화이트 | 19250 | 1624400 |
    | ASUS ROG Strix G16CH 화이트 | 16624 | 2988700 |
    | 한성 보스몬스터 DX9900 실버 | 14892 | 818900 |
    | ASUS ROG Strix G16CH 실버 | 14308 | 1609400 |

    > 5kg 이상의 제품은 대부분 데스크톱 PC입니다.

---

### 문제 30

**판매 중인 상품 중 마진율이 30%를 초과하는 상품을 마진율이 높은 순으로 상위 10개 조회하세요. 이름, 판매가, 원가, 마진율(%)을 출력합니다.**

??? tip "힌트"
    마진율(%) 공식: `(price - cost_price) * 100.0 / price`입니다. `WHERE` 절에서도 이 산술식을 직접 사용할 수 있습니다. `ROUND()` 함수로 소수점 자릿수를 정리하세요.

??? success "정답"
    ```sql
    SELECT name,
           price,
           cost_price,
           ROUND((price - cost_price) * 100.0 / price, 1) AS margin_pct
    FROM products
    WHERE is_active = 1
      AND (price - cost_price) * 100.0 / price > 30
    ORDER BY margin_pct DESC
    LIMIT 10;
    ```

    **결과:**

    | name | price | cost_price | margin_pct |
    |------|-------|------------|------------|
    | Norton AntiVirus Plus 실버 | 71600 | 32400 | 54.7 |
    | 한컴오피스 2024 기업용 실버 | 234100 | 116400 | 50.3 |
    | LG 27UQ85R 블랙 | 1582800 | 811300 | 48.7 |
    | BenQ PD3225U | 2500400 | 1312500 | 47.5 |
    | Razer Kraken V4 블랙 | 171500 | 91500 | 46.6 |
    | 한컴오피스 2024 기업용 화이트 | 162800 | 89500 | 45.0 |
    | 보스 SoundLink Flex 블랙 | 516000 | 283600 | 45.0 |
    | HP Z2 Mini G1a 블랙 | 1166400 | 656800 | 43.7 |
    | CyberPower OR1500LCDRT2U 블랙 | 361200 | 206100 | 42.9 |
    | JBL Pebbles 2 블랙 | 112900 | 65500 | 42.0 |

    > 소프트웨어(Norton, 한컴오피스)는 물리적 원가가 낮아 마진율이 높습니다.
