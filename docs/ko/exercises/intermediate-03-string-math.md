# 문자열과 숫자 함수

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `products` — 상품 (이름, 가격, 재고, 브랜드)<br>
    `customers` — 고객 (등급, 포인트, 가입채널)<br>
    `orders` — 주문 (상태, 금액, 일시)<br>
    `order_items` — 주문 상세 (수량, 단가)<br>
    `categories` — 카테고리 (부모-자식 계층)<br>
    `suppliers` — 공급업체 (회사명, 연락처)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    `SUBSTR`<br>
    `LENGTH`<br>
    `UPPER`/`LOWER`<br>
    `REPLACE`<br>
    `TRIM`<br>
    `INSTR`<br>
    `GROUP_CONCAT`<br>
    `COALESCE`<br>
    `ROUND`<br>
    `ABS`<br>
    `CAST`<br>
    `NULLIF`<br>
    `IIF`/`CASE`<br>
    `printf`

</div>

!!! info "시작하기 전에"
    이 연습은 **중급 12~13강**(문자열 함수, 수학/유틸리티 함수)에서 배운 내용을 실전에 적용합니다.
    SQLite의 문자열/숫자 함수를 사용하여 데이터를 변환하고 포매팅합니다.

---

## 기초 (1~7)

기본 문자열 함수(LENGTH, UPPER, SUBSTR, REPLACE)를 연습합니다.

---

### 문제 1

**상품명의 글자 수를 구하세요. 이름이 가장 긴 상품 10개.**

??? tip "힌트"
    `LENGTH(name)`으로 문자열 길이를 구합니다. `ORDER BY LENGTH(name) DESC LIMIT 10`.

??? success "정답"
    ```sql
    SELECT
        name,
        LENGTH(name) AS name_length
    FROM products
    ORDER BY name_length DESC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | name | name_length |
    |------|------------|
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] ... | 48 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 38 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 42 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트 | 37 |
    | MSI Radeon RX 9070 XT GAMING X | 30 |

    > 실제 데이터에 따라 결과가 달라집니다.

---

### 문제 2

**브랜드명을 모두 대문자로 변환하여 고유한 브랜드 목록을 조회하세요.**

??? tip "힌트"
    `UPPER(brand)`로 대문자 변환, `DISTINCT`로 중복 제거합니다.

??? success "정답"
    ```sql
    SELECT DISTINCT UPPER(brand) AS brand_upper
    FROM products
    ORDER BY brand_upper;
    ```

    **결과 (상위 5행):**

    | brand_upper |
    |------------|
    | APC |
    | ASROCK |
    | ASUS |
    | CORSAIR |
    | DELL |

    > 대소문자가 통일되어 브랜드를 정확히 파악할 수 있습니다.

---

### 문제 3

**상품명에서 브랜드 부분을 제거하고 나머지 이름만 추출하세요.**

??? tip "힌트"
    `SUBSTR(name, LENGTH(brand) + 2)`로 브랜드명 + 공백 이후의 문자열을 추출합니다.

??? success "정답"
    ```sql
    SELECT
        brand,
        name,
        SUBSTR(name, LENGTH(brand) + 2) AS model_name
    FROM products
    WHERE name LIKE brand || ' %'
    ORDER BY brand, model_name
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | brand | name | model_name |
    |-------|------|-----------|
    | ASUS | ASUS ExpertBook B5 화이트 | ExpertBook B5 화이트 |
    | ASUS | ASUS PCE-BE92BT | PCE-BE92BT |
    | ASUS | ASUS ROG Strix G16CH 화이트 | ROG Strix G16CH 화이트 |
    | ASUS | ASUS ROG Strix GT35 | ROG Strix GT35 |
    | ASUS | ASUS ROG Strix Scar 16 실버 | ROG Strix Scar 16 실버 |

---

### 문제 4

**고객 이메일에서 '@' 앞의 아이디 부분만 추출하세요.**

??? tip "힌트"
    `SUBSTR(email, 1, INSTR(email, '@') - 1)`로 '@' 앞까지 자릅니다. `INSTR`은 문자열 내 특정 문자의 위치를 반환합니다.

??? success "정답"
    ```sql
    SELECT
        email,
        SUBSTR(email, 1, INSTR(email, '@') - 1) AS user_id
    FROM customers
    ORDER BY user_id
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | email | user_id |
    |-------|--------|
    | abc001@testmail.kr | abc001 |
    | abc002@testmail.kr | abc002 |
    | bear123@testmail.kr | bear123 |
    | blue456@testmail.kr | blue456 |
    | cat789@testmail.kr | cat789 |

    > 실제 데이터에 따라 결과가 달라집니다.

---

### 문제 5

**상품명에서 색상 정보('블랙', '화이트', '실버')를 제거하세요.**

??? tip "힌트"
    `REPLACE`를 중첩하여 여러 문자열을 제거합니다. `TRIM`으로 끝에 남은 공백을 정리합니다.

??? success "정답"
    ```sql
    SELECT
        name,
        TRIM(REPLACE(REPLACE(REPLACE(name, '블랙', ''), '화이트', ''), '실버', '')) AS name_no_color
    FROM products
    WHERE name LIKE '%블랙%' OR name LIKE '%화이트%' OR name LIKE '%실버%'
    ORDER BY name
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | name | name_no_color |
    |------|--------------|
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | APC Back-UPS Pro Gaming BGM1500B |
    | ASRock X670E Steel Legend 실버 | ASRock X670E Steel Legend |
    | ASUS ExpertBook B5 화이트 | ASUS ExpertBook B5 |
    | ASUS ROG Strix G16CH 화이트 | ASUS ROG Strix G16CH |
    | ASUS ROG Strix Scar 16 실버 | ASUS ROG Strix Scar 16 |

---

### 문제 6

**고객 전화번호에서 하이픈(-)을 제거한 번호를 만드세요.**

??? tip "힌트"
    `REPLACE(phone, '-', '')`로 하이픈을 빈 문자열로 치환합니다.

??? success "정답"
    ```sql
    SELECT
        name,
        phone,
        REPLACE(phone, '-', '') AS phone_no_dash,
        LENGTH(REPLACE(phone, '-', '')) AS digit_count
    FROM customers
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | name | phone | phone_no_dash | digit_count |
    |------|-------|--------------|------------|
    | 김** | 020-1234-5678 | 02012345678 | 11 |
    | 이** | 020-2345-6789 | 02023456789 | 11 |
    | 박** | 020-3456-7890 | 02034567890 | 11 |
    | 최** | 020-4567-8901 | 02045678901 | 11 |
    | 정** | 020-5678-9012 | 02056789012 | 11 |

    > 실제 데이터에 따라 결과가 달라집니다.

---

### 문제 7

**상품의 SKU 코드에서 카테고리 약어(첫 2글자)를 추출하세요.**

??? tip "힌트"
    `SUBSTR(sku, 1, 2)`로 SKU의 첫 2글자를 추출합니다. SKU 형식은 `LA-GEN-삼성-00001` 같은 구조입니다.

??? success "정답"
    ```sql
    SELECT
        sku,
        SUBSTR(sku, 1, 2) AS category_code,
        name
    FROM products
    ORDER BY category_code, sku
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | sku | category_code | name |
    |-----|--------------|------|
    | CA-ACC-... | CA | (케이스 악세서리) |
    | CA-FUL-... | CA | (풀타워 케이스) |
    | CA-MID-... | CA | (미들타워 케이스) |
    | DE-GAM-... | DE | (게이밍 데스크톱) |
    | DE-GEN-... | DE | (일반 데스크톱) |

    > SKU의 첫 2글자가 카테고리를 나타냅니다.

---

## 응용 (8~14)

GROUP_CONCAT, INSTR, NULLIF, CAST, ROUND를 연습합니다.

---

### 문제 8

**카테고리별 소속 브랜드를 쉼표로 나열하세요.**

??? tip "힌트"
    `GROUP_CONCAT(DISTINCT brand, ', ')`로 카테고리 내 고유 브랜드를 쉼표 구분 문자열로 합칩니다.

??? success "정답"
    ```sql
    SELECT
        cat.name AS category,
        COUNT(DISTINCT p.brand) AS brand_count,
        GROUP_CONCAT(DISTINCT p.brand, ', ') AS brands
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE p.is_active = 1
    GROUP BY cat.id, cat.name
    ORDER BY brand_count DESC
    LIMIT 10;
    ```

    **결과 (상위 3행):**

    | category | brand_count | brands |
    |----------|------------|--------|
    | 노트북 | 8 | ASUS, Dell, HP, LG, Lenovo, MSI, Razer, 삼성전자 |
    | 그래픽카드 | 5 | ASUS, EVGA, Gigabyte, MSI, ZOTAC |
    | 모니터 | 6 | ASUS, Dell, LG, MSI, 삼성전자, 벤큐 |

    > 실제 데이터에 따라 결과가 달라집니다.

---

### 문제 9

**상품명에 'RTX'가 포함된 상품에서 RTX 뒤의 모델 번호를 추출하세요.**

??? tip "힌트"
    `INSTR(name, 'RTX')`로 'RTX'의 위치를 찾고, `SUBSTR(name, INSTR(...) + 4, 4)`로 모델 번호 부분을 추출합니다.

??? success "정답"
    ```sql
    SELECT
        name,
        SUBSTR(name, INSTR(name, 'RTX') + 4, 4) AS rtx_model
    FROM products
    WHERE name LIKE '%RTX%'
    ORDER BY rtx_model DESC;
    ```

    **결과 (상위 5행):**

    | name | rtx_model |
    |------|----------|
    | ASUS TUF Gaming RTX 5090 | 5090 |
    | ASUS TUF Gaming RTX 5080 화이트 | 5080 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] ... | 5070 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 4070 |
    | Gigabyte RTX 4060 EAGLE | 4060 |

    > 실제 데이터에 따라 결과가 달라집니다.

---

### 문제 10

**주문 금액을 만원 단위로 반올림하세요. 금액이 큰 상위 10건.**

??? tip "힌트"
    `ROUND(total_amount, -4)`로 만원(10,000) 단위로 반올림합니다. 음수 자릿수는 정수 부분을 반올림합니다.

??? success "정답"
    ```sql
    SELECT
        order_number,
        total_amount,
        ROUND(total_amount, -4) AS rounded_10k,
        ROUND(total_amount, -4) / 10000 AS in_man_won
    FROM orders
    WHERE status NOT IN ('cancelled')
    ORDER BY total_amount DESC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | order_number | total_amount | rounded_10k | in_man_won |
    |--------------|-------------|------------|-----------|
    | ORD-2025... | 8765400 | 8770000 | 877 |
    | ORD-2025... | 7654300 | 7650000 | 765 |
    | ORD-2024... | 6543200 | 6540000 | 654 |
    | ORD-2024... | 5987600 | 5990000 | 599 |
    | ORD-2025... | 5432100 | 5430000 | 543 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

### 문제 11

**마진율이 0인 상품을 안전하게 처리하세요. NULLIF로 0 나누기를 방지합니다.**

??? tip "힌트"
    `NULLIF(cost_price, 0)`은 cost_price가 0이면 NULL을 반환합니다. NULL로 나누면 결과가 NULL이 되어 오류가 발생하지 않습니다.

??? success "정답"
    ```sql
    SELECT
        name,
        price,
        cost_price,
        ROUND(100.0 * (price - cost_price) / NULLIF(cost_price, 0), 1) AS margin_pct
    FROM products
    WHERE is_active = 1
    ORDER BY margin_pct DESC NULLS LAST
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | name | price | cost_price | margin_pct |
    |------|-------|-----------|-----------|
    | 삼성 DDR4 32GB PC4-25600 | 49100 | 24500 | 100.4 |
    | ASUS PCE-BE92BT | 48800 | 25600 | 90.6 |
    | Logitech G502 X 블랙 | 89700 | 48900 | 83.4 |
    | 커세어 RM850x 블랙 | 178200 | 98700 | 80.5 |
    | Dell U2724D | 853600 | 487600 | 75.0 |

    > `NULLIF`가 없으면 cost_price=0인 행에서 나누기 오류가 발생할 수 있습니다.

---

### 문제 12

**주문 금액을 텍스트 포맷('1,234,567원')으로 변환하세요.**

??? tip "힌트"
    `printf('%,d', total_amount)`로 천 단위 쉼표를 추가합니다. `||`로 '원' 단위를 붙입니다.

??? success "정답"
    ```sql
    SELECT
        order_number,
        total_amount,
        printf('%,d', CAST(total_amount AS INTEGER)) || '원' AS formatted_amount
    FROM orders
    WHERE status NOT IN ('cancelled')
    ORDER BY total_amount DESC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | order_number | total_amount | formatted_amount |
    |--------------|-------------|-----------------|
    | ORD-2025... | 8765400 | 8,765,400원 |
    | ORD-2025... | 7654300 | 7,654,300원 |
    | ORD-2024... | 6543200 | 6,543,200원 |
    | ORD-2024... | 5987600 | 5,987,600원 |
    | ORD-2025... | 5432100 | 5,432,100원 |

    > `printf`는 SQLite 전용 함수입니다.

---

### 문제 13

**상품 가격을 구간별 라벨로 분류하세요. IIF 또는 CASE를 사용합니다.**

??? tip "힌트"
    `IIF(조건, 참, 거짓)`은 SQLite의 간단한 조건 함수입니다. 다중 조건에는 `CASE WHEN`이 더 적합합니다.

??? success "정답"
    ```sql
    SELECT
        name,
        price,
        CASE
            WHEN price < 100000 THEN '10만원 미만'
            WHEN price < 500000 THEN '10~50만원'
            WHEN price < 1000000 THEN '50~100만원'
            WHEN price < 2000000 THEN '100~200만원'
            ELSE '200만원 이상'
        END AS price_range,
        IIF(price >= 1000000, '고가', '일반') AS price_class
    FROM products
    WHERE is_active = 1
    ORDER BY price DESC
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | name | price | price_range | price_class |
    |------|-------|------------|------------|
    | ASUS ROG Strix GT35 | 4314800 | 200만원 이상 | 고가 |
    | ASUS ROG Zephyrus G16 | 4284100 | 200만원 이상 | 고가 |
    | Razer Blade 18 블랙 | 4182100 | 200만원 이상 | 고가 |
    | Razer Blade 16 실버 | 4123800 | 200만원 이상 | 고가 |
    | ASUS ROG Strix G16CH 화이트 | 2988700 | 200만원 이상 | 고가 |

---

### 문제 14

**문자열로 저장된 숫자를 정수/실수로 변환하세요. 재고 수량의 타입 변환.**

??? tip "힌트"
    `CAST(값 AS INTEGER)` 또는 `CAST(값 AS REAL)`로 타입을 변환합니다. `TYPEOF()`로 현재 타입을 확인할 수 있습니다.

??? success "정답"
    ```sql
    SELECT
        name,
        stock_qty,
        TYPEOF(stock_qty) AS original_type,
        CAST(stock_qty AS REAL) AS stock_as_real,
        TYPEOF(CAST(stock_qty AS REAL)) AS converted_type,
        CAST(price AS INTEGER) AS price_int
    FROM products
    WHERE is_active = 1
    ORDER BY stock_qty DESC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | name | stock_qty | original_type | stock_as_real | converted_type | price_int |
    |------|----------|--------------|--------------|---------------|----------|
    | MSI GeForce RTX 4070 Ti... | 499 | integer | 499.0 | real | 1744000 |
    | 삼성 DDR4 32GB PC4-25600 | 359 | integer | 359.0 | real | 49100 |
    | Dell U2724D | 337 | integer | 337.0 | real | 853600 |
    | 커세어 RM850x 블랙 | 312 | integer | 312.0 | real | 178200 |
    | ASUS PCE-BE92BT | 298 | integer | 298.0 | real | 48800 |

    > `TYPEOF()`는 SQLite 전용 함수로 저장된 값의 실제 타입을 확인합니다.

---

## 실전 (15~20)

복합 포매팅, 데이터 변환, 패턴 매칭을 연습합니다.

---

### 문제 15

**고객 등급별 이름 목록을 만드세요. 각 등급의 처음 5명만 쉼표로 연결.**

??? tip "힌트"
    서브쿼리에서 `ROW_NUMBER()`로 등급 내 순번을 매기고, 5명까지만 필터한 뒤 `GROUP_CONCAT`으로 합칩니다.

??? success "정답"
    ```sql
    SELECT
        grade,
        COUNT(*) AS total_count,
        GROUP_CONCAT(name, ', ') AS sample_names
    FROM (
        SELECT
            name,
            grade,
            ROW_NUMBER() OVER (PARTITION BY grade ORDER BY created_at) AS rn
        FROM customers
        WHERE is_active = 1
    )
    WHERE rn <= 5
    GROUP BY grade
    ORDER BY total_count DESC;
    ```

    **결과:**

    | grade | total_count | sample_names |
    |-------|------------|-------------|
    | BRONZE | 5 | 김**, 이**, 박**, 최**, 정** |
    | SILVER | 5 | 한**, 조**, 윤**, 장**, 임** |
    | GOLD | 5 | 오**, 서**, 신**, 권**, 황** |
    | VIP | 5 | 안**, 송**, 전**, 홍**, 유** |

    > 각 등급에서 가장 오래된 5명의 이름이 표시됩니다. 실제 이름은 달라집니다.

---

### 문제 16

**주문번호에서 날짜와 일련번호를 분리하세요. 주문번호 형식: ORD-YYYYMMDD-NNNNN.**

??? tip "힌트"
    `SUBSTR(order_number, 5, 8)`로 날짜 부분(YYYYMMDD), `SUBSTR(order_number, 14)`로 일련번호를 추출합니다.

??? success "정답"
    ```sql
    SELECT
        order_number,
        SUBSTR(order_number, 5, 8) AS date_part,
        SUBSTR(order_number, 5, 4) || '-' || SUBSTR(order_number, 9, 2) || '-' || SUBSTR(order_number, 11, 2) AS formatted_date,
        CAST(SUBSTR(order_number, 14) AS INTEGER) AS sequence_no
    FROM orders
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | order_number | date_part | formatted_date | sequence_no |
    |--------------|----------|---------------|------------|
    | ORD-20251231-00089 | 20251231 | 2025-12-31 | 89 |
    | ORD-20251231-00088 | 20251231 | 2025-12-31 | 88 |
    | ORD-20251231-00087 | 20251231 | 2025-12-31 | 87 |
    | ORD-20251230-00156 | 20251230 | 2025-12-30 | 156 |
    | ORD-20251230-00155 | 20251230 | 2025-12-30 | 155 |

    > 실제 데이터에 따라 일련번호가 달라집니다.

---

### 문제 17

**상품명에서 용량/크기 정보(숫자+GB/TB/MHz/W)를 포함하는 상품만 조회하세요.**

??? tip "힌트"
    `GLOB`은 대소문자를 구분하는 패턴 매칭입니다. `*[0-9]GB*`, `*[0-9]TB*` 등으로 숫자 뒤 단위가 오는 패턴을 찾습니다.

??? success "정답"
    ```sql
    SELECT name, price, brand
    FROM products
    WHERE name GLOB '*[0-9]GB*'
       OR name GLOB '*[0-9]TB*'
       OR name GLOB '*[0-9]MHz*'
       OR name GLOB '*[0-9]W*'
    ORDER BY price DESC
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | name | price | brand |
    |------|-------|-------|
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 130700 | G.SKILL |
    | 삼성 DDR4 32GB PC4-25600 | 49100 | 삼성전자 |
    | WD Elements 2TB 블랙 | 265600 | WD |
    | 커세어 RM850x 블랙 | 178200 | Corsair |
    | 삼성 990 PRO 2TB | 234500 | 삼성전자 |

    > `GLOB`은 SQLite 전용입니다. `LIKE`와 달리 대소문자를 구분합니다.

---

### 문제 18

**상품 요약 카드: 상품 정보를 한 줄 문자열로 포맷팅하세요.**

??? tip "힌트"
    `||`(문자열 연결)과 `COALESCE`, `printf`를 조합하여 포맷팅합니다. NULL 값은 `COALESCE`로 기본값 처리.

??? success "정답"
    ```sql
    SELECT
        '[' || brand || '] ' || name
        || ' | ' || printf('%,d', CAST(price AS INTEGER)) || '원'
        || ' | 재고: ' || stock_qty || '개'
        || ' | ' || COALESCE('무게: ' || (weight_grams / 1000.0) || 'kg', '무게 미정')
        AS product_card
    FROM products
    WHERE is_active = 1
    ORDER BY price DESC
    LIMIT 5;
    ```

    **결과:**

    | product_card |
    |-------------|
    | [ASUS] ASUS ROG Strix GT35 \| 4,314,800원 \| 재고: 245개 \| 무게: 12.5kg |
    | [ASUS] ASUS ROG Zephyrus G16 \| 4,284,100원 \| 재고: 178개 \| 무게: 2.1kg |
    | [Razer] Razer Blade 18 블랙 \| 4,182,100원 \| 재고: 107개 \| 무게: 2.8kg |
    | [Razer] Razer Blade 16 실버 \| 4,123,800원 \| 재고: 134개 \| 무게: 2.2kg |
    | [ASUS] ASUS ROG Strix G16CH 화이트 \| 2,988,700원 \| 재고: 89개 \| 무게: 9.8kg |

    > 실제 데이터에 따라 결과가 달라집니다. weight_grams가 NULL이면 '무게 미정'이 표시됩니다.

---

### 문제 19

**고객 가입 채널별 이메일 도메인 분석: 가입 채널과 이메일 도메인의 교차 집계.**

??? tip "힌트"
    `SUBSTR(email, INSTR(email, '@') + 1)`로 도메인을 추출합니다. `COALESCE(acquisition_channel, '미확인')`으로 NULL 처리.

??? success "정답"
    ```sql
    SELECT
        COALESCE(acquisition_channel, '미확인') AS channel,
        SUBSTR(email, INSTR(email, '@') + 1) AS domain,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY COALESCE(acquisition_channel, '미확인'),
             SUBSTR(email, INSTR(email, '@') + 1)
    ORDER BY customer_count DESC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | channel | domain | customer_count |
    |---------|--------|---------------|
    | organic | testmail.kr | 1876 |
    | search_ad | testmail.kr | 1234 |
    | social | testmail.kr | 987 |
    | referral | testmail.kr | 654 |
    | direct | testmail.kr | 432 |

    > 모든 이메일이 testmail.kr 도메인이므로 채널별 고객 수 분포를 확인하는 데 의미가 있습니다.

---

### 문제 20

**상품별 종합 리포트: 가격 구간, 마진율, 재고 상태, 판매 활성도를 하나의 문자열로 요약하세요.**

??? tip "힌트"
    여러 함수(`CASE`, `ROUND`, `IIF`, `printf`, `COALESCE`, `||`)를 조합하여 종합 리포트를 생성합니다.

??? success "정답"
    ```sql
    SELECT
        name,
        CASE
            WHEN price < 100000 THEN '저가'
            WHEN price < 500000 THEN '중가'
            WHEN price < 1000000 THEN '중고가'
            ELSE '고가'
        END AS price_tier,
        printf('%.1f%%', 100.0 * (price - cost_price) / NULLIF(cost_price, 0)) AS margin_pct,
        CASE
            WHEN stock_qty = 0 THEN '품절'
            WHEN stock_qty < 10 THEN '부족'
            WHEN stock_qty < 50 THEN '보통'
            ELSE '충분'
        END AS stock_status,
        IIF(is_active = 1, '판매중', '단종') AS sale_status,
        printf('%,d원', CAST(price AS INTEGER)) AS display_price
    FROM products
    ORDER BY price DESC
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | name | price_tier | margin_pct | stock_status | sale_status | display_price |
    |------|-----------|-----------|-------------|------------|--------------|
    | ASUS ROG Strix GT35 | 고가 | 35.2% | 충분 | 판매중 | 4,314,800원 |
    | ASUS ROG Zephyrus G16 | 고가 | 28.7% | 충분 | 판매중 | 4,284,100원 |
    | Razer Blade 18 블랙 | 고가 | 31.4% | 충분 | 판매중 | 4,182,100원 |
    | Razer Blade 16 실버 | 고가 | 29.8% | 충분 | 판매중 | 4,123,800원 |
    | ASUS ROG Strix G16CH 화이트 | 고가 | 33.1% | 충분 | 판매중 | 2,988,700원 |

    > 여러 함수를 조합하여 한눈에 상품 상태를 파악할 수 있는 리포트를 만듭니다.
