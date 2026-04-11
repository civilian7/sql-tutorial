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
    | ---------- | ----------: |
    | TeamGroup T-Force Delta RGB DDR5 32GB 6000MHz 화이트 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | 89 |
    | MSI MAG B850 TOMAHAWK MAX WIFI 화이트 [특별 한정판 에디션] 고급 알루미늄 합금 바디 적용, 프리미엄 패키지 구성 | 77 |
    | Microsoft Bluetooth Ergonomic Mouse 실버 [특별 한정판 에디션] 전문가 추천 모델, 업계 최고 성능 인증 획득 | 77 |
    | ASUS TUF Gaming RTX 4070 Ti Super 실버 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | 76 |
    | be quiet! Shadow Base 800 FX 블랙 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | 71 |
    | MSI MPG X870E CARBON WIFI 화이트 [특별 한정판 에디션] 무상 보증 3년 연장 + 전용 파우치 증정 이벤트 | 70 |
    | Intel Core Ultra 5 245K 화이트 [특별 한정판 에디션] 무상 보증 3년 연장 + 전용 파우치 증정 이벤트 | 68 |
    | Super Flower Leadex VII 1000W [특별 한정판 에디션] 전문가 추천 모델, 업계 최고 성능 인증 획득 | 68 |
    | ... | ... |

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
    | ---------- |
    | ADOBE |
    | AMD |
    | APC |
    | APPLE |
    | ARCTIC |
    | ASROCK |
    | ASUS |
    | BE QUIET! |
    | ... |

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
    | ---------- | ---------- | ---------- |
    | AMD | AMD Ryzen 5 9600X | Ryzen 5 9600X |
    | AMD | AMD Ryzen 7 7700X | Ryzen 7 7700X |
    | AMD | AMD Ryzen 7 7700X 블랙 | Ryzen 7 7700X 블랙 |
    | AMD | AMD Ryzen 7 7700X 블랙 | Ryzen 7 7700X 블랙 |
    | AMD | AMD Ryzen 7 7800X3D | Ryzen 7 7800X3D |
    | AMD | AMD Ryzen 7 7800X3D 실버 | Ryzen 7 7800X3D 실버 |
    | AMD | AMD Ryzen 7 9700X 블랙 | Ryzen 7 9700X 블랙 |
    | AMD | AMD Ryzen 7 9800X3D 실버 | Ryzen 7 9800X3D 실버 |
    | ... | ... | ... |

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
    | ---------- | ---------- |
    | user1@testmail.kr | user1 |
    | user10@testmail.kr | user10 |
    | user100@testmail.kr | user100 |
    | user1000@testmail.kr | user1000 |
    | user10000@testmail.kr | user10000 |
    | user10001@testmail.kr | user10001 |
    | user10002@testmail.kr | user10002 |
    | user10003@testmail.kr | user10003 |
    | ... | ... |

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
    | ---------- | ---------- |
    | AMD Ryzen 7 7700X 블랙 | AMD Ryzen 7 7700X |
    | AMD Ryzen 7 7700X 블랙 | AMD Ryzen 7 7700X |
    | AMD Ryzen 7 7800X3D 실버 | AMD Ryzen 7 7800X3D |
    | AMD Ryzen 7 9700X 블랙 | AMD Ryzen 7 9700X |
    | AMD Ryzen 7 9800X3D 실버 | AMD Ryzen 7 9800X3D |
    | AMD Ryzen 7 9800X3D 실버 [특별 한정판 에디션] RGB 라이팅 탑재, 소프트웨어 커스터마이징 지원 | AMD Ryzen 7 9800X3D  [특별 한정판 에디션] RGB 라이팅 탑재, 소프트웨어 커스터마이징 지원 |
    | AMD Ryzen 9 9900X 화이트 | AMD Ryzen 9 9900X |
    | AMD Ryzen 9 9950X3D 블랙 | AMD Ryzen 9 9950X3D |
    | ... | ... |

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
    | ---------- | ---------- | ---------- | ----------: |
    | 정준호 | 020-4964-6200 | 02049646200 | 11 |
    | 김경수 | 020-4423-5167 | 02044235167 | 11 |
    | 김민재 | 020-0806-0711 | 02008060711 | 11 |
    | 진정자 | 020-9666-8856 | 02096668856 | 11 |
    | 이정수 | 020-0239-9503 | 02002399503 | 11 |
    | 김준혁 | 020-0786-7765 | 02007867765 | 11 |
    | 김명자 | 020-4487-2922 | 02044872922 | 11 |
    | 성민석 | 020-8951-7989 | 02089517989 | 11 |
    | ... | ... | ... | ... |

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
    | ---------- | ---------- | ---------- |
    | AU-BOS-00184 | AU | 보스 SoundLink Flex 실버 |
    | AU-BOS-00306 | AU | 보스 QuietComfort Ultra 실버 |
    | AU-BOS-00322 | AU | 보스 QuietComfort Ultra Earbuds 실버 |
    | AU-BOS-00767 | AU | 보스 QuietComfort Ultra Earbuds 실버 |
    | AU-BOS-00810 | AU | 보스 QuietComfort Ultra |
    | AU-BOS-00883 | AU | 보스 QuietComfort Ultra Earbuds 블랙 |
    | AU-BOS-01085 | AU | 보스 QuietComfort Ultra |
    | AU-BOS-01090 | AU | 보스 QuietComfort 45 실버 |
    | ... | ... | ... |

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
    | ---------- | ---------- |
    | ASUS ROG STRIX RTX 5090 | 5090 |
    | MSI GeForce RTX 5090 SUPRIM X | 5090 |
    | MSI GeForce RTX 5090 SUPRIM X 실버 | 5090 |
    | MSI GeForce RTX 5090 SUPRIM X 화이트 | 5090 |
    | 기가바이트 RTX 5090 AERO OC | 5090 |
    | 기가바이트 RTX 5090 AERO OC | 5090 |
    | 기가바이트 RTX 5090 AERO OC | 5090 |
    | ASUS TUF Gaming RTX 5080 화이트 | 5080 |
    | ... | ... |

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
    | ---------- | ----------: | ----------: | ----------: |
    | ORD-20230408-248697 | 71906300.0 | 71906300.0 | 7190.63 |
    | ORD-20240218-293235 | 68948100.0 | 68948100.0 | 6894.81 |
    | ORD-20240822-323378 | 64332900.0 | 64332900.0 | 6433.29 |
    | ORD-20180516-26809 | 63466900.0 | 63466900.0 | 6346.69 |
    | ORD-20200429-82365 | 61889000.0 | 61889000.0 | 6188.9 |
    | ORD-20230626-259827 | 61811500.0 | 61811500.0 | 6181.15 |
    | ORD-20160730-03977 | 60810900.0 | 60810900.0 | 6081.09 |
    | ORD-20251230-417476 | 60038800.0 | 60038800.0 | 6003.88 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: | ----------: | ----------: |
    | Microsoft 365 Personal 실버 | 171000.0 | 62900.0 | 171.9 |
    | Adobe Creative Cloud 1년 화이트 | 657900.0 | 256500.0 | 156.5 |
    | V3 365 Clinic | 63300.0 | 25200.0 | 151.2 |
    | Adobe Photoshop 1년 | 313600.0 | 126500.0 | 147.9 |
    | Adobe Creative Cloud 1년 | 309100.0 | 125600.0 | 146.1 |
    | Razer Viper V3 HyperSpeed 블랙 | 99500.0 | 41000.0 | 142.7 |
    | Adobe Acrobat Pro 1년 | 389600.0 | 164600.0 | 136.7 |
    | Windows 11 Pro | 409600.0 | 176800.0 | 131.7 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: | ---------- |
    | ORD-20230408-248697 | 71906300.0 | 71,906,300원 |
    | ORD-20240218-293235 | 68948100.0 | 68,948,100원 |
    | ORD-20240822-323378 | 64332900.0 | 64,332,900원 |
    | ORD-20180516-26809 | 63466900.0 | 63,466,900원 |
    | ORD-20200429-82365 | 61889000.0 | 61,889,000원 |
    | ORD-20230626-259827 | 61811500.0 | 61,811,500원 |
    | ORD-20160730-03977 | 60810900.0 | 60,810,900원 |
    | ORD-20251230-417476 | 60038800.0 | 60,038,800원 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ---------- | ---------- |
    | Razer Blade 14 블랙 | 7495200.0 | 200만원 이상 | 고가 |
    | Razer Blade 16 블랙 | 5634900.0 | 200만원 이상 | 고가 |
    | Razer Blade 16 | 5518300.0 | 200만원 이상 | 고가 |
    | Razer Blade 18 | 5450500.0 | 200만원 이상 | 고가 |
    | Razer Blade 14 | 5339100.0 | 200만원 이상 | 고가 |
    | Razer Blade 16 실버 | 5127500.0 | 200만원 이상 | 고가 |
    | Razer Blade 18 화이트 | 4913500.0 | 200만원 이상 | 고가 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 4881500.0 | 200만원 이상 | 고가 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: | ---------- | ----------: | ---------- | ----------: |
    | Arctic Liquid Freezer III 240 | 500 | integer | 500.0 | real | 106100 |
    | Razer Viper V3 HyperSpeed 실버 | 500 | integer | 500.0 | real | 130200 |
    | Apple Magic Keyboard Touch ID 포함 | 500 | integer | 500.0 | real | 118500 |
    | ASUS PRIME Z790-A WIFI 화이트 | 500 | integer | 500.0 | real | 480400 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 499 | integer | 499.0 | real | 1744000 |
    | 시소닉 FOCUS GX-850 | 499 | integer | 499.0 | real | 172900 |
    | be quiet! Dark Power 13 1000W | 499 | integer | 499.0 | real | 90800 |
    | 로지텍 MX Anywhere 3S 블랙 | 499 | integer | 499.0 | real | 118800 |
    | ... | ... | ... | ... | ... | ... |

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
    | ---------- | ----------: | ---------- |
    | VIP | 5 | 김상철, 문영숙, 김도현, 박정수, 오영숙 |
    | SILVER | 5 | 김정순, 김현준, 정중수, 유현지, 황하은 |
    | GOLD | 5 | 한민재, 서성민, 한은영, 임민재, 김지훈 |
    | BRONZE | 5 | 이주원, 장승현, 이승민, 박예진, 우서영 |

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
    | ---------- | ---------- | ---------- | ----------: |
    | ORD-20251211-413965 | 20251211 | 2025-12-11 | 413965 |
    | ORD-20251226-416837 | 20251226 | 2025-12-26 | 416837 |
    | ORD-20251231-417734 | 20251231 | 2025-12-31 | 417734 |
    | ORD-20251231-417696 | 20251231 | 2025-12-31 | 417696 |
    | ORD-20251231-417737 | 20251231 | 2025-12-31 | 417737 |
    | ORD-20251231-417735 | 20251231 | 2025-12-31 | 417735 |
    | ORD-20251231-417677 | 20251231 | 2025-12-31 | 417677 |
    | ORD-20251231-417764 | 20251231 | 2025-12-31 | 417764 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: | ---------- |
    | Seagate BarraCuda 2TB 화이트 | 611900.0 | Seagate |
    | WD Red Plus 8TB | 586300.0 | WD |
    | WD Red Plus 4TB 실버 | 575900.0 | WD |
    | WD Red Plus 8TB 블랙 | 575600.0 | WD |
    | Seagate BarraCuda 2TB 실버 | 570500.0 | Seagate |
    | Seagate BarraCuda 2TB | 558500.0 | Seagate |
    | WD Red Plus 4TB | 558200.0 | WD |
    | WD Red Plus 4TB | 557500.0 | WD |
    | ... | ... | ... |

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
    | ---------- |
    | [Razer] Razer Blade 14 블랙 | 7,495,200원 | 재고: 171개 | 무게: 1.827kg |
    | [Razer] Razer Blade 16 블랙 | 5,634,900원 | 재고: 461개 | 무게: 2.716kg |
    | [Razer] Razer Blade 16 | 5,518,300원 | 재고: 494개 | 무게: 2.89kg |
    | [Razer] Razer Blade 18 | 5,450,500원 | 재고: 297개 | 무게: 2.23kg |
    | [Razer] Razer Blade 14 | 5,339,100원 | 재고: 190개 | 무게: 2.341kg |
    | ... |

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
    | ---------- | ---------- | ----------: |
    | search_ad | testmail.kr | 15289 |
    | social | testmail.kr | 14245 |
    | organic | testmail.kr | 11457 |
    | referral | testmail.kr | 7146 |
    | direct | testmail.kr | 4163 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
    | Razer Blade 14 블랙 | 고가 | 80.1% | 충분 | 판매중 | 7,495,200원 |
    | Razer Blade 16 블랙 | 고가 | 38.7% | 충분 | 판매중 | 5,634,900원 |
    | Razer Blade 16 | 고가 | 49.0% | 충분 | 판매중 | 5,518,300원 |
    | Razer Blade 16 화이트 | 고가 | 42.9% | 충분 | 단종 | 5,503,500원 |
    | Razer Blade 18 | 고가 | 42.9% | 충분 | 판매중 | 5,450,500원 |
    | Razer Blade 14 | 고가 | 42.9% | 충분 | 판매중 | 5,339,100원 |
    | Razer Blade 16 실버 | 고가 | 42.9% | 충분 | 판매중 | 5,127,500원 |
    | Razer Blade 16 블랙 | 고가 | 39.1% | 충분 | 단종 | 4,938,200원 |
    | ... | ... | ... | ... | ... | ... |

    > 여러 함수를 조합하여 한눈에 상품 상태를 파악할 수 있는 리포트를 만듭니다.
