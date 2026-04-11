# 정렬과 페이징

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `products` — 상품 (이름, 가격, 재고, 브랜드) · `customers` — 고객 (등급, 포인트, 가입채널) · `orders` — 주문 (상태, 금액, 일시) · `reviews` — 리뷰 (평점, 내용) · `payments` — 결제 (방법, 금액, 상태)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `OFFSET`, `DISTINCT`, 별칭(`AS`), 산술 연산

</div>

!!! info "시작하기 전에"
    이 연습은 **입문 1~3강**(SELECT, WHERE, ORDER BY, LIMIT, OFFSET)에서 배운 내용만 사용합니다.
    JOIN, 서브쿼리, GROUP BY, 집계 함수는 사용하지 않습니다.

---

## 기초 (1~10)

한 가지 개념씩 연습합니다.

---

### 문제 1

**상품을 가격이 비싼 순서대로 정렬하여 이름(`name`)과 가격(`price`)을 조회하세요.**

??? tip "힌트"
    `ORDER BY price DESC`를 사용하면 내림차순 정렬입니다.

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
    | ASUS Dual RTX 5070 Ti ... | 4226200 |
    | Razer Blade 18 블랙 | 4182100 |
    | Razer Blade 16 실버 | 4123800 |

---

### 문제 2

**상품을 가격이 저렴한 순서대로 정렬하여 이름, 브랜드(`brand`), 가격을 조회하세요.**

??? tip "힌트"
    `ORDER BY price ASC` 또는 `ORDER BY price`만 써도 오름차순(기본값)입니다.

??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    ORDER BY price ASC;
    ```

    **결과 (상위 5행):**

    | name | brand | price |
    |------|-------|-------|
    | TP-Link TG-3468 블랙 | TP-Link | 13100 |
    | 로지텍 MX Anywhere 3S 블랙 | 로지텍 | 18400 |
    | Microsoft Ergonomic Keyboard 실버 | Microsoft | 23000 |
    | TP-Link Archer TBE400E 화이트 | TP-Link | 23300 |
    | 삼성 SPA-KFG0BUB | 삼성전자 | 26200 |

---

### 문제 3

**가장 비싼 상품 5개의 이름과 가격을 조회하세요.**

??? tip "힌트"
    `ORDER BY`로 정렬한 뒤 `LIMIT`으로 상위 N개만 가져옵니다.

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
    | ASUS Dual RTX 5070 Ti ... | 4226200 |
    | Razer Blade 18 블랙 | 4182100 |
    | Razer Blade 16 실버 | 4123800 |

---

### 문제 4

**재고 수량(`stock_qty`)이 가장 적은 상품 5개의 이름, 가격, 재고 수량을 조회하세요.**

??? tip "힌트"
    `ORDER BY stock_qty ASC`로 오름차순 정렬하면 재고가 적은 순서입니다.

??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    ORDER BY stock_qty ASC
    LIMIT 5;
    ```

    **결과:**

    | name | price | stock_qty |
    |------|-------|-----------|
    | Arctic Freezer 36 A-RGB 화이트 | 31400 | 0 |
    | 삼성 SPA-KFG0BUB | 26200 | 4 |
    | 삼성 DDR4 32GB PC4-25600 | 114400 | 6 |
    | Norton AntiVirus Plus | 57000 | 8 |
    | 로지텍 G502 HERO 실버 | 47900 | 8 |

---

### 문제 5

**고객을 가입일(`created_at`) 순서대로 정렬하여 가장 먼저 가입한 고객 5명의 이름, 이메일, 등급(`grade`), 가입일을 조회하세요.**

??? tip "힌트"
    가장 오래된 가입일이 먼저 나오려면 `ORDER BY created_at ASC`를 사용합니다.

??? success "정답"
    ```sql
    SELECT name, email, grade, created_at
    FROM customers
    ORDER BY created_at ASC
    LIMIT 5;
    ```

    **결과:**

    | name | email | grade | created_at |
    |------|-------|-------|------------|
    | 양영진 | user84@testmail.kr | BRONZE | 2016-01-03 19:49:46 |
    | 이승민 | user61@testmail.kr | BRONZE | 2016-01-04 14:11:21 |
    | 유현지 | user90@testmail.kr | BRONZE | 2016-01-05 22:02:29 |
    | 이영자 | user98@testmail.kr | VIP | 2016-01-09 06:08:34 |
    | 강은서 | user15@testmail.kr | BRONZE | 2016-01-14 06:39:08 |

---

### 문제 6

**상품 이름을 알파벳/가나다 순서대로 정렬하여 처음 5개를 조회하세요.**

??? tip "힌트"
    `ORDER BY name`으로 정렬하면 영문 알파벳이 한글보다 먼저 옵니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY name
    LIMIT 5;
    ```

    **결과:**

    | name | price |
    |------|-------|
    | AMD Ryzen 9 9900X | 244800 |
    | AMD Ryzen 9 9900X | 647800 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | 408800 |
    | ASRock B850M Pro RS 블랙 | 201900 |
    | ASRock B850M Pro RS 실버 | 533600 |

---

### 문제 7

**가격이 비싼 상품 상위 6~10위를 조회하세요.** (즉, 상위 5개를 건너뛰고 다음 5개)

??? tip "힌트"
    `OFFSET`은 지정한 행 수만큼 건너뜁니다. `LIMIT 5 OFFSET 5`로 6번째부터 가져옵니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5 OFFSET 5;
    ```

    **결과:**

    | name | price |
    |------|-------|
    | ASUS TUF Gaming RTX 5080 화이트 | 3812000 |
    | MacBook Air 15 M3 실버 | 3774700 |
    | Razer Blade 18 화이트 | 3320700 |
    | ASUS ROG Strix G16CH 화이트 | 2988700 |
    | Razer Blade 18 블랙 | 2987500 |

---

### 문제 8

**적립금(`point_balance`)이 가장 많은 고객 5명의 이름, 등급, 적립금을 조회하세요.**

??? tip "힌트"
    `ORDER BY point_balance DESC`로 내림차순 정렬 후 `LIMIT 5`를 적용합니다.

??? success "정답"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    ORDER BY point_balance DESC
    LIMIT 5;
    ```

    **결과:**

    | name | grade | point_balance |
    |------|-------|---------------|
    | 박정수 | VIP | 3341740 |
    | 강명자 | VIP | 2908232 |
    | 김병철 | VIP | 2818474 |
    | 이영자 | VIP | 2772254 |
    | 이미정 | VIP | 2282481 |

---

### 문제 9

**주문 금액(`total_amount`)이 가장 큰 주문 5건의 주문번호(`order_number`), 주문 금액, 주문일(`ordered_at`)을 조회하세요.**

??? tip "힌트"
    `orders` 테이블에서 `ORDER BY total_amount DESC LIMIT 5`를 사용합니다.

??? success "정답"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 5;
    ```

    **결과:**

    | order_number | total_amount | ordered_at |
    |--------------|-------------|------------|
    | ORD-20210628-12574 | 58039800 | 2021-06-28 12:36:22 |
    | ORD-20230809-24046 | 55047300 | 2023-08-09 13:49:22 |
    | ORD-20210321-11106 | 48718000 | 2021-03-21 07:27:22 |
    | ORD-20200605-07165 | 47954000 | 2020-06-05 12:25:59 |
    | ORD-20231020-25036 | 46945700 | 2023-10-20 13:57:47 |

---

### 문제 10

**상품 테이블에 등록된 브랜드 목록을 중복 없이 알파벳 순서대로 조회하세요.**

??? tip "힌트"
    `SELECT DISTINCT brand`로 중복을 제거하고, `ORDER BY brand`로 정렬합니다.

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

## 응용 (11~20)

여러 개념을 조합하여 연습합니다.

---

### 문제 11

**가격이 100만 원 이상인 상품을 비싼 순서대로 정렬하여 이름, 브랜드, 가격을 조회하세요. 상위 5개만 출력합니다.**

??? tip "힌트"
    `WHERE price >= 1000000`으로 필터링한 뒤 `ORDER BY price DESC LIMIT 5`를 적용합니다.

??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price >= 1000000
    ORDER BY price DESC
    LIMIT 5;
    ```

    **결과:**

    | name | brand | price |
    |------|-------|-------|
    | ASUS ROG Strix GT35 | ASUS | 4314800 |
    | ASUS ROG Zephyrus G16 | ASUS | 4284100 |
    | ASUS Dual RTX 5070 Ti ... | ASUS | 4226200 |
    | Razer Blade 18 블랙 | Razer | 4182100 |
    | Razer Blade 16 실버 | Razer | 4123800 |

---

### 문제 12

**삼성전자 또는 LG전자 브랜드 상품을 가격 내림차순으로 정렬하여 이름, 브랜드, 가격을 조회하세요. 상위 5개만 출력합니다.**

??? tip "힌트"
    `WHERE brand IN ('삼성전자', 'LG전자')`로 두 브랜드를 필터링합니다.

??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand IN ('삼성전자', 'LG전자')
    ORDER BY price DESC
    LIMIT 5;
    ```

    **결과:**

    | name | brand | price |
    |------|-------|-------|
    | 삼성 오디세이 G5 27 블랙 | 삼성전자 | 2561600 |
    | LG 그램 17 실버 | LG전자 | 2336200 |
    | LG 그램 14 | LG전자 | 2164900 |
    | LG 27UQ85R | LG전자 | 2140600 |
    | 삼성 갤럭시북4 360 블랙 | 삼성전자 | 1857600 |

---

### 문제 13

**VIP 등급 고객 중 성이 '김'인 고객을 적립금이 많은 순서대로 정렬하여 이름, 등급, 적립금을 5명만 조회하세요.**

??? tip "힌트"
    `WHERE grade = 'VIP' AND name LIKE '김%'`로 두 조건을 동시에 적용합니다.

??? success "정답"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    WHERE grade = 'VIP'
      AND name LIKE '김%'
    ORDER BY point_balance DESC
    LIMIT 5;
    ```

    **결과:**

    | name | grade | point_balance |
    |------|-------|---------------|
    | 김병철 | VIP | 2818474 |
    | 김성민 | VIP | 2182561 |
    | 김동현 | VIP | 1393337 |
    | 김경희 | VIP | 1230186 |
    | 김정순 | VIP | 1210600 |

---

### 문제 14

**판매 중단된 상품(`discontinued_at`이 NULL이 아닌 상품)을 중단일 기준 최신순으로 정렬하여 이름, 가격, 중단일을 5개만 조회하세요.**

??? tip "힌트"
    `WHERE discontinued_at IS NOT NULL`로 판매 중단 상품만 필터링합니다.

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

### 문제 15

**리뷰 평점(`rating`)이 1점인 리뷰를 최신순으로 정렬하여 제목(`title`), 평점, 작성일(`created_at`)을 5개 조회하세요.**

??? tip "힌트"
    `reviews` 테이블에서 `WHERE rating = 1`로 필터링하고 `ORDER BY created_at DESC`로 정렬합니다.

??? success "정답"
    ```sql
    SELECT title, rating, created_at
    FROM reviews
    WHERE rating = 1
    ORDER BY created_at DESC
    LIMIT 5;
    ```

    **결과:**

    | title | rating | created_at |
    |-------|--------|------------|
    | 불량품 | 1 | 2025-06-13 17:57:53 |
    | 환불 원해요 | 1 | 2025-06-09 17:21:03 |
    | 다신 안삽니다 | 1 | 2025-06-05 20:27:31 |
    | 환불 원해요 | 1 | 2025-05-29 13:16:06 |
    | 최악 | 1 | 2025-05-27 21:05:41 |

---

### 문제 16

**가격이 50만 원 이상 100만 원 이하인 상품을 가격 오름차순으로 정렬하여 이름, 브랜드, 가격을 5개 조회하세요.**

??? tip "힌트"
    `WHERE price BETWEEN 500000 AND 1000000`으로 범위를 지정합니다.

??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price BETWEEN 500000 AND 1000000
    ORDER BY price ASC
    LIMIT 5;
    ```

    **결과:**

    | name | brand | price |
    |------|-------|-------|
    | 넷기어 Nighthawk RS700S 블랙 | 넷기어 | 503600 |
    | ASRock X670E Steel Legend 실버 | ASRock | 508700 |
    | 보스 SoundLink Flex 블랙 | 보스 | 516000 |
    | 삼성 ViewFinity S8 | 삼성전자 | 518400 |
    | MSI MAG Z890 TOMAHAWK WIFI 블랙 | MSI | 526900 |

---

### 문제 17

**카드 결제(`method = 'card'`) 중 할부 개월 수(`installment_months`)가 0보다 큰 건을 할부 개월 수 내림차순, 결제 금액(`amount`) 내림차순으로 정렬하여 5건 조회하세요. 주문 ID, 결제 금액, 카드사(`card_issuer`), 할부 개월 수를 출력합니다.**

??? tip "힌트"
    `ORDER BY` 뒤에 칼럼을 쉼표로 구분하면 다중 정렬이 됩니다. 첫 번째 칼럼이 같을 때 두 번째 칼럼으로 정렬합니다.

??? success "정답"
    ```sql
    SELECT order_id, amount, card_issuer, installment_months
    FROM payments
    WHERE method = 'card'
      AND installment_months > 0
    ORDER BY installment_months DESC, amount DESC
    LIMIT 5;
    ```

    **결과:**

    | order_id | amount | card_issuer | installment_months |
    |----------|--------|-------------|-------------------|
    | 2801 | 22989000 | 삼성카드 | 24 |
    | 31726 | 19078632 | 우리카드 | 24 |
    | 24756 | 16629700 | 우리카드 | 24 |
    | 30337 | 12353000 | KB국민카드 | 24 |
    | 34373 | 5704256 | 신한카드 | 24 |

---

### 문제 18

**GOLD 등급 고객을 이름 가나다순으로 정렬하여 11~15번째 고객의 이름과 이메일을 조회하세요.**

??? tip "힌트"
    11번째부터 시작하려면 `OFFSET 10` (10개를 건너뜀), 5명을 가져오려면 `LIMIT 5`입니다.

??? success "정답"
    ```sql
    SELECT name, email
    FROM customers
    WHERE grade = 'GOLD'
    ORDER BY name
    LIMIT 5 OFFSET 10;
    ```

    **결과:**

    | name | email |
    |------|-------|
    | 강지원 | user1690@testmail.kr |
    | 강지은 | user1433@testmail.kr |
    | 강지훈 | user1228@testmail.kr |
    | 강진호 | user1619@testmail.kr |
    | 강현준 | user4072@testmail.kr |

---

### 문제 19

**결제 수단(`method`)의 종류를 중복 없이 조회하세요.**

??? tip "힌트"
    `SELECT DISTINCT method FROM payments`를 사용합니다.

??? success "정답"
    ```sql
    SELECT DISTINCT method
    FROM payments
    ORDER BY method;
    ```

    **결과:**

    | method |
    |--------|
    | bank_transfer |
    | card |
    | kakao_pay |
    | naver_pay |
    | point |
    | virtual_account |

---

### 문제 20

**상품의 이름, 가격, 원가(`cost_price`), 마진(가격 - 원가)을 마진이 큰 순서대로 정렬하여 5개 조회하세요. 마진 칼럼에는 `margin`이라는 별칭을 붙이세요.**

??? tip "힌트"
    `SELECT` 절에서 `price - cost_price AS margin`으로 계산 칼럼을 만들 수 있습니다.

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

## 실전 (21~30)

여러 테이블과 복합 조건을 활용합니다.

---

### 문제 21

**취소된 주문(`status = 'cancelled'`) 중 주문 금액이 가장 큰 5건의 주문번호, 주문 금액, 취소일(`cancelled_at`)을 조회하세요.**

??? tip "힌트"
    `WHERE status = 'cancelled'`로 필터링하고 `ORDER BY total_amount DESC`로 정렬합니다.

??? success "정답"
    ```sql
    SELECT order_number, total_amount, cancelled_at
    FROM orders
    WHERE status = 'cancelled'
    ORDER BY total_amount DESC
    LIMIT 5;
    ```

    **결과:**

    | order_number | total_amount | cancelled_at |
    |--------------|-------------|--------------|
    | ORD-20220923-19607 | 14400000 | 2022-09-25 11:20:19 |
    | ORD-20250309-33168 | 13528400 | 2025-03-11 03:03:24 |
    | ORD-20190726-03947 | 11884300 | 2019-07-28 19:12:23 |
    | ORD-20210209-10411 | 10628200 | 2021-02-11 14:57:57 |
    | ORD-20220511-17633 | 9794160 | 2022-05-12 20:35:15 |

---

### 문제 22

**재고가 10개 이하인 상품을 재고 오름차순, 가격 내림차순으로 정렬하여 이름, 가격, 재고 수량을 조회하세요.**

??? tip "힌트"
    `WHERE stock_qty <= 10`으로 필터링하고 `ORDER BY stock_qty ASC, price DESC`로 다중 정렬합니다.

??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE stock_qty <= 10
    ORDER BY stock_qty ASC, price DESC;
    ```

    **결과 (상위 5행):**

    | name | price | stock_qty |
    |------|-------|-----------|
    | Arctic Freezer 36 A-RGB 화이트 | 31400 | 0 |
    | 삼성 SPA-KFG0BUB | 26200 | 4 |
    | 삼성 DDR4 32GB PC4-25600 | 114400 | 6 |
    | Norton AntiVirus Plus | 57000 | 8 |
    | 로지텍 G502 HERO 실버 | 47900 | 8 |

---

### 문제 23

**한 번도 로그인하지 않은 고객(`last_login_at`이 NULL)을 가입일 순서대로 정렬하여 이름, 이메일, 등급을 10명 조회하세요.**

??? tip "힌트"
    NULL 여부는 `= NULL`이 아니라 `IS NULL`로 확인합니다.

??? success "정답"
    ```sql
    SELECT name, email, grade
    FROM customers
    WHERE last_login_at IS NULL
    ORDER BY created_at ASC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | name | email | grade |
    |------|-------|-------|
    | 윤준영 | user25@testmail.kr | BRONZE |
    | 이영식 | user43@testmail.kr | BRONZE |
    | 김지우 | user77@testmail.kr | BRONZE |
    | 송서준 | user66@testmail.kr | BRONZE |
    | 박아름 | user80@testmail.kr | BRONZE |

---

### 문제 24

**상품의 이름, 가격, 부가세 포함 가격을 조회하세요. 부가세 포함 가격은 `price * 1.1`로 계산하고 `price_with_tax`라는 별칭을 붙이세요. 부가세 포함 가격이 비싼 순서대로 5개만 출력합니다.**

??? tip "힌트"
    `ROUND(price * 1.1)`로 소수점을 정리하면 깔끔한 결과를 얻을 수 있습니다.

??? success "정답"
    ```sql
    SELECT name, price, ROUND(price * 1.1) AS price_with_tax
    FROM products
    ORDER BY price_with_tax DESC
    LIMIT 5;
    ```

    **결과:**

    | name | price | price_with_tax |
    |------|-------|----------------|
    | ASUS ROG Strix GT35 | 4314800 | 4746280 |
    | ASUS ROG Zephyrus G16 | 4284100 | 4712510 |
    | ASUS Dual RTX 5070 Ti ... | 4226200 | 4648820 |
    | Razer Blade 18 블랙 | 4182100 | 4600310 |
    | Razer Blade 16 실버 | 4123800 | 4536180 |

---

### 문제 25

**2024년에 접수된 주문(`ordered_at`이 2024년) 중 주문 금액이 가장 큰 5건의 주문번호, 주문 금액, 주문일을 조회하세요.**

??? tip "힌트"
    `WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'`로 2024년 범위를 지정합니다.

??? success "정답"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at < '2025-01-01'
    ORDER BY total_amount DESC
    LIMIT 5;
    ```

    **결과:**

    | order_number | total_amount | ordered_at |
    |--------------|-------------|------------|
    | ORD-20240225-27030 | 36283600 | 2024-02-25 07:58:54 |
    | ORD-20240711-29111 | 26969600 | 2024-07-11 08:56:39 |
    | ORD-20240731-29379 | 20005700 | 2024-07-31 12:04:46 |
    | ORD-20241213-31726 | 19078632 | 2024-12-13 14:44:09 |
    | ORD-20240218-26919 | 16797600 | 2024-02-18 13:52:12 |

---

### 문제 26

**할인 금액(`discount_amount`)이 0보다 큰 주문을 할인 금액이 큰 순서대로 정렬하여 주문번호, 주문 금액, 할인 금액, 주문일을 5건 조회하세요.**

??? tip "힌트"
    `WHERE discount_amount > 0`으로 할인이 적용된 주문만 필터링합니다.

??? success "정답"
    ```sql
    SELECT order_number, total_amount, discount_amount, ordered_at
    FROM orders
    WHERE discount_amount > 0
    ORDER BY discount_amount DESC
    LIMIT 5;
    ```

    **결과:**

    | order_number | total_amount | discount_amount | ordered_at |
    |--------------|-------------|-----------------|------------|
    | ORD-20240225-27030 | 36283600 | 1931400 | 2024-02-25 07:58:54 |
    | ORD-20211028-14389 | 25098600 | 1673700 | 2021-10-28 18:08:16 |
    | ORD-20231020-25043 | 22030500 | 1022200 | 2023-10-20 06:41:21 |
    | ORD-20231220-26105 | 21445900 | 782000 | 2023-12-20 13:36:24 |
    | ORD-20210709-12698 | 27601900 | 767100 | 2021-07-09 13:44:55 |

---

### 문제 27

**카카오페이(`method = 'kakao_pay'`)로 결제된 건을 결제 금액이 큰 순서대로 정렬하여 주문 ID(`order_id`), 결제 금액, 결제일(`paid_at`)을 5건 조회하세요.**

??? tip "힌트"
    `payments` 테이블에서 `WHERE method = 'kakao_pay'`로 필터링합니다.

??? success "정답"
    ```sql
    SELECT order_id, amount, paid_at
    FROM payments
    WHERE method = 'kakao_pay'
    ORDER BY amount DESC
    LIMIT 5;
    ```

    **결과:**

    | order_id | amount | paid_at |
    |----------|--------|---------|
    | 25036 | 46945700 | 2023-10-20 14:25:47 |
    | 23646 | 44941000 | 2023-07-12 11:15:06 |
    | 532 | 41409100 | 2017-03-11 00:23:51 |
    | 13528 | 38915800 | 2021-09-04 20:16:11 |
    | 1416 | 32375000 | 2018-03-19 09:12:31 |

---

### 문제 28

**2025년에 가입한 고객 중 GOLD 또는 VIP 등급인 고객을 적립금이 많은 순서대로 5명 조회하세요. 이름, 등급, 적립금, 가입일을 출력합니다.**

??? tip "힌트"
    `WHERE created_at >= '2025-01-01' AND grade IN ('GOLD', 'VIP')`로 조건을 조합합니다.

??? success "정답"
    ```sql
    SELECT name, grade, point_balance, created_at
    FROM customers
    WHERE created_at >= '2025-01-01'
      AND grade IN ('GOLD', 'VIP')
    ORDER BY point_balance DESC
    LIMIT 5;
    ```

    **결과:**

    | name | grade | point_balance | created_at |
    |------|-------|---------------|------------|
    | 지수민 | VIP | 101137 | 2025-01-11 07:41:06 |
    | 김성수 | VIP | 82178 | 2025-02-07 11:33:08 |
    | 최명숙 | VIP | 65619 | 2025-05-20 01:26:30 |
    | 박은영 | VIP | 61183 | 2025-03-30 05:24:54 |
    | 유경희 | VIP | 60761 | 2025-01-10 17:17:19 |

---

### 문제 29

**ASUS 브랜드가 아닌 상품(`brand != 'ASUS'`) 중 삼성전자, LG전자, MSI도 제외한 상품을 가격 내림차순으로 5개 조회하세요. 이름, 브랜드, 가격을 출력합니다.**

??? tip "힌트"
    `NOT IN`을 사용하면 여러 값을 한꺼번에 제외할 수 있습니다.

??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand NOT IN ('ASUS', '삼성전자', 'LG전자', 'MSI')
    ORDER BY price DESC
    LIMIT 5;
    ```

    **결과:**

    | name | brand | price |
    |------|-------|-------|
    | Razer Blade 18 블랙 | Razer | 4182100 |
    | Razer Blade 16 실버 | Razer | 4123800 |
    | MacBook Air 15 M3 실버 | Apple | 3774700 |
    | Razer Blade 18 화이트 | Razer | 3320700 |
    | Razer Blade 18 블랙 | Razer | 2987500 |

---

### 문제 30

**무게(`weight_grams`)가 기록된 상품 중 가장 무거운 상품 5개의 이름, 무게(그램), 가격을 조회하세요. 무게를 킬로그램으로 환산한 `weight_kg` 칼럼도 함께 출력하세요.**

??? tip "힌트"
    `WHERE weight_grams IS NOT NULL`로 무게가 있는 상품만 필터링합니다. `weight_grams / 1000.0`으로 킬로그램을 계산합니다.

??? success "정답"
    ```sql
    SELECT name,
           weight_grams,
           ROUND(weight_grams / 1000.0, 1) AS weight_kg,
           price
    FROM products
    WHERE weight_grams IS NOT NULL
    ORDER BY weight_grams DESC
    LIMIT 5;
    ```

    **결과:**

    | name | weight_grams | weight_kg | price |
    |------|-------------|-----------|-------|
    | ASUS ROG Strix GT35 | 19449 | 19.4 | 4314800 |
    | 한성 보스몬스터 DX7700 화이트 | 19250 | 19.3 | 1624400 |
    | ASUS ROG Strix G16CH 화이트 | 16624 | 16.6 | 2988700 |
    | 한성 보스몬스터 DX9900 실버 | 14892 | 14.9 | 818900 |
    | ASUS ROG Strix G16CH 실버 | 14308 | 14.3 | 1609400 |
