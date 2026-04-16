# 정렬과 페이징

!!! info "사용 테이블"
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `customers` — 고객 (등급, 포인트, 가입채널)  
    `orders` — 주문 (상태, 금액, 일시)  
    `reviews` — 리뷰 (평점, 내용)  
    `payments` — 결제 (방법, 금액, 상태)  

!!! abstract "학습 범위"
    `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `OFFSET`, `DISTINCT`, 별칭(`AS`), 산술 연산

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
    | ---------- | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 |
    | Razer Blade 16 블랙 | 5634900.0 |
    | Razer Blade 16 | 5518300.0 |
    | Razer Blade 16 화이트 | 5503500.0 |
    | Razer Blade 18 | 5450500.0 |
    | Razer Blade 14 | 5339100.0 |
    | Razer Blade 16 실버 | 5127500.0 |
    | Razer Blade 16 블랙 | 4938200.0 |
    | ... | ... |

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
    | ---------- | ---------- | ----------: |
    | TP-Link TL-SG108 실버 | TP-Link | 16500.0 |
    | 로지텍 M100r | 로지텍 | 17300.0 |
    | 넷기어 GS308 블랙 | 넷기어 | 17400.0 |
    | TP-Link TL-SG108E | TP-Link | 18000.0 |
    | 로지텍 G502 HERO [특별 한정판 에디션] 무상 보증 3년 연장 + 전용 파우치 증정 이벤트 | 로지텍 | 19400.0 |
    | TP-Link TG-3468 블랙 | TP-Link | 19800.0 |
    | TP-Link TL-SG108 | TP-Link | 20100.0 |
    | 삼성 무선 키보드 Trio 500 화이트 | 삼성전자 | 20300.0 |
    | ... | ... | ... |

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
    | ---------- | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 |
    | Razer Blade 16 블랙 | 5634900.0 |
    | Razer Blade 16 | 5518300.0 |
    | Razer Blade 16 화이트 | 5503500.0 |
    | Razer Blade 18 | 5450500.0 |
    | ... | ... |

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
    | ---------- | ----------: | ----------: |
    | Arctic Freezer 36 A-RGB 화이트 | 27400.0 | 0 |
    | 한컴오피스 2024 기업용 실버 | 391200.0 | 0 |
    | 삼성 DDR4 16GB PC4-25600 | 73600.0 | 0 |
    | WD My Passport 2TB 블랙 | 329100.0 | 0 |
    | 삼성 DDR5 32GB PC5-38400 실버 | 158000.0 | 0 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ---------- | ---------- |
    | 이주원 | user313@testmail.kr | BRONZE | 2016-01-01 00:00:52 |
    | 성미숙 | user133@testmail.kr | BRONZE | 2016-01-01 00:53:24 |
    | 오진호 | user584@testmail.kr | BRONZE | 2016-01-01 03:10:41 |
    | 노지민 | user387@testmail.kr | BRONZE | 2016-01-01 10:17:05 |
    | 장승현 | user690@testmail.kr | BRONZE | 2016-01-01 15:11:55 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: |
    | AMD Ryzen 5 9600X | 186400.0 |
    | AMD Ryzen 7 7700X | 691500.0 |
    | AMD Ryzen 7 7700X 블랙 | 1105200.0 |
    | AMD Ryzen 7 7700X 블랙 | 458300.0 |
    | AMD Ryzen 7 7800X3D | 750800.0 |
    | ... | ... |

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
    | ---------- | ----------: |
    | Razer Blade 14 | 5339100.0 |
    | Razer Blade 16 실버 | 5127500.0 |
    | Razer Blade 16 블랙 | 4938200.0 |
    | Razer Blade 18 화이트 | 4913500.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 4881500.0 |
    | ... | ... |

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
    | ---------- | ---------- | ----------: |
    | 박정수 | VIP | 6344986 |
    | 정유진 | VIP | 6255658 |
    | 이미정 | VIP | 5999946 |
    | 김상철 | VIP | 5406032 |
    | 문영숙 | VIP | 4947814 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ---------- |
    | ORD-20230408-248697 | 71906300.0 | 2023-04-08 16:24:03 |
    | ORD-20240218-293235 | 68948100.0 | 2024-02-18 20:53:49 |
    | ORD-20240822-323378 | 64332900.0 | 2024-08-22 13:20:32 |
    | ORD-20180516-26809 | 63466900.0 | 2018-05-16 06:29:52 |
    | ORD-20200429-82365 | 61889000.0 | 2020-04-29 21:21:06 |
    | ... | ... | ... |

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
    | ---------- |
    | AMD |
    | APC |
    | ASRock |
    | ASUS |
    | Adobe |
    | Apple |
    | Arctic |
    | BenQ |
    | ... |

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
    | ---------- | ---------- | ----------: |
    | Razer Blade 14 블랙 | Razer | 7495200.0 |
    | Razer Blade 16 블랙 | Razer | 5634900.0 |
    | Razer Blade 16 | Razer | 5518300.0 |
    | Razer Blade 16 화이트 | Razer | 5503500.0 |
    | Razer Blade 18 | Razer | 5450500.0 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ----------: |
    | LG 그램 17 블랙 | LG전자 | 3053700.0 |
    | LG 데스크톱 B80GV 블랙 | LG전자 | 2887600.0 |
    | LG 그램 14 화이트 | LG전자 | 2816400.0 |
    | LG 그램 프로 16 화이트 | LG전자 | 2797000.0 |
    | 삼성 올인원 DM530ABE 화이트 | 삼성전자 | 2743700.0 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ----------: |
    | 김상철 | VIP | 5406032 |
    | 김병철 | VIP | 4138149 |
    | 김성민 | VIP | 3710320 |
    | 김상현 | VIP | 3298043 |
    | 김경희 | VIP | 3155254 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ---------- |
    | 로지텍 G715 실버 | 100600.0 | 2025-12-27 19:50:12 |
    | 시소닉 FOCUS GM-750 실버 | 98900.0 | 2025-12-25 20:05:49 |
    | SteelSeries Arctis Nova 7 Wireless 실버 | 367300.0 | 2025-12-24 21:58:49 |
    | Dell Latitude 5540 실버 | 1113900.0 | 2025-12-17 22:47:10 |
    | 주연 리오나인 i9 하이엔드 실버 | 1663400.0 | 2025-12-15 15:04:20 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ---------- |
    | 불량품 | 1 | 2026-01-18 18:51:49 |
    | 최악 | 1 | 2026-01-17 08:02:24 |
    | 환불 원해요 | 1 | 2026-01-16 08:03:22 |
    | 환불 원해요 | 1 | 2026-01-11 18:10:03 |
    | 최악 | 1 | 2026-01-08 20:38:55 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ----------: |
    | 엡손 L15160 | 엡손 | 501700.0 |
    | 삼성 S24C360 블랙 | 삼성전자 | 503500.0 |
    | 넷기어 RAX70 실버 | 넷기어 | 506300.0 |
    | ASRock B860M Pro RS 화이트 | ASRock | 506700.0 |
    | 필립스 328E1CA 실버 | 필립스 | 507300.0 |
    | ... | ... | ... |

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
    | ----------: | ----------: | ---------- | ----------: |
    | 293235 | 68948100.0 | 삼성카드 | 24 |
    | 307025 | 47227200.0 | KB국민카드 | 24 |
    | 76585 | 46052600.0 | KB국민카드 | 24 |
    | 405306 | 46031200.0 | KB국민카드 | 24 |
    | 18938 | 44626000.0 | 롯데카드 | 24 |
    | ... | ... | ... | ... |

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
    | ---------- | ---------- |
    | 강미경 | user16965@testmail.kr |
    | 강미영 | user41074@testmail.kr |
    | 강미정 | user12237@testmail.kr |
    | 강민서 | user12355@testmail.kr |
    | 강민서 | user17719@testmail.kr |
    | ... | ... |

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
    | ---------- |
    | bank_transfer |
    | card |
    | kakao_pay |
    | naver_pay |
    | point |
    | virtual_account |
    | ... |

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
    | ---------- | ----------: | ----------: | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 | 4161000.0 | 3334200.0 |
    | MacBook Air 13 M4 | 4449200.0 | 2451900.0 | 1997300.0 |
    | Razer Blade 16 | 5518300.0 | 3703300.0 | 1815000.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 4881500.0 | 3168100.0 | 1713400.0 |
    | Razer Blade 18 화이트 | 4913500.0 | 3251900.0 | 1661600.0 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: | ---------- |
    | ORD-20191116-64149 | 43727700.0 | 2019-11-17 22:33:13 |
    | ORD-20190330-46537 | 38907900.0 | 2019-04-01 08:28:58 |
    | ORD-20191105-63133 | 33039100.0 | 2019-11-05 10:16:57 |
    | ORD-20211105-162659 | 32777300.0 | 2021-11-06 22:22:58 |
    | ORD-20230319-245317 | 30961500.0 | 2023-03-20 17:28:12 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ----------: |
    | 한컴오피스 2024 기업용 실버 | 391200.0 | 0 |
    | WD My Passport 2TB 블랙 | 329100.0 | 0 |
    | 삼성 DDR5 32GB PC5-38400 실버 | 158000.0 | 0 |
    | 삼성 DDR4 16GB PC4-25600 | 73600.0 | 0 |
    | Arctic Freezer 36 A-RGB 화이트 | 27400.0 | 0 |
    | Dell S2425HS 블랙 | 667900.0 | 1 |
    | Dell U2723QE 실버 | 396300.0 | 1 |
    | Arctic Liquid Freezer III 240 | 189300.0 | 1 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ---------- |
    | 김시우 | user337@testmail.kr | BRONZE |
    | 박민준 | user426@testmail.kr | BRONZE |
    | 오지후 | user172@testmail.kr | BRONZE |
    | 윤준영 | user25@testmail.kr | BRONZE |
    | 권지우 | user169@testmail.kr | BRONZE |
    | 정정희 | user918@testmail.kr | BRONZE |
    | 이영식 | user43@testmail.kr | BRONZE |
    | 전혜진 | user954@testmail.kr | BRONZE |
    | ... | ... | ... |

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
    | ---------- | ----------: | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 | 8244720.0 |
    | Razer Blade 16 블랙 | 5634900.0 | 6198390.0 |
    | Razer Blade 16 | 5518300.0 | 6070130.0 |
    | Razer Blade 16 화이트 | 5503500.0 | 6053850.0 |
    | Razer Blade 18 | 5450500.0 | 5995550.0 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ---------- |
    | ORD-20240218-293235 | 68948100.0 | 2024-02-18 20:53:49 |
    | ORD-20240822-323378 | 64332900.0 | 2024-08-22 13:20:32 |
    | ORD-20241013-332643 | 57772300.0 | 2024-10-13 19:57:10 |
    | ORD-20241209-344848 | 56012148.0 | 2024-12-09 18:50:12 |
    | ORD-20240206-291311 | 52034300.0 | 2024-02-06 15:17:20 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ----------: | ---------- |
    | ORD-20240913-327284 | 38829400.0 | 3737700.0 | 2024-09-13 01:31:44 |
    | ORD-20230922-270979 | 32947100.0 | 3097300.0 | 2023-09-22 14:55:31 |
    | ORD-20241231-350072 | 28566900.0 | 2878300.0 | 2024-12-31 20:04:20 |
    | ORD-20210923-155344 | 26679400.0 | 2634900.0 | 2021-09-23 20:27:26 |
    | ORD-20241209-344848 | 56012148.0 | 2305600.0 | 2024-12-09 18:50:12 |
    | ... | ... | ... | ... |

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
    | ----------: | ----------: | ---------- |
    | 3977 | 60810900.0 | 2016-07-30 19:21:23 |
    | 417476 | 60038800.0 | (NULL) |
    | 207504 | 56303700.0 | 2022-07-28 19:26:23 |
    | 344848 | 56012148.0 | 2024-12-09 19:12:12 |
    | 266880 | 49494600.0 | 2023-08-22 13:16:33 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ----------: | ---------- |
    | 강정식 | VIP | 348058 | 2025-03-21 04:25:02 |
    | 박영미 | VIP | 314830 | 2025-05-02 04:12:57 |
    | 권준혁 | VIP | 272576 | 2025-02-25 10:25:19 |
    | 서은서 | VIP | 262093 | 2025-01-03 09:53:15 |
    | 이순자 | VIP | 257309 | 2025-01-27 23:01:11 |
    | ... | ... | ... | ... |

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
    | ---------- | ---------- | ----------: |
    | Razer Blade 14 블랙 | Razer | 7495200.0 |
    | Razer Blade 16 블랙 | Razer | 5634900.0 |
    | Razer Blade 16 | Razer | 5518300.0 |
    | Razer Blade 16 화이트 | Razer | 5503500.0 |
    | Razer Blade 18 | Razer | 5450500.0 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ----------: | ----------: |
    | 한성 보스몬스터 DX7700 실버 | 19914 | 19.9 | 3230900.0 |
    | ASUS ROG Strix GT35 실버 | 19883 | 19.9 | 2553100.0 |
    | APC Back-UPS Pro BR1500G 실버 | 19791 | 19.8 | 340300.0 |
    | ASUS ROG Strix GT35 화이트 | 19598 | 19.6 | 1637500.0 |
    | ASUS ROG Strix GT35 | 19449 | 19.4 | 3296400.0 |
    | ... | ... | ... | ... |
