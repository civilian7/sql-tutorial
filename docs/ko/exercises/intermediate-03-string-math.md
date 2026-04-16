# 문자열/숫자 함수

!!! info "사용 테이블"

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `categories` — 카테고리 (부모-자식 계층)  

    `suppliers` — 공급업체 (업체명, 연락처)  



!!! abstract "학습 범위"

    `SUBSTR`, `LENGTH`, `UPPER`, `LOWER`, `REPLACE`, `TRIM`, `INSTR`, `GROUP_CONCAT`, `COALESCE`, `ROUND`, `ABS`, `CAST`, `NULLIF`, `IIF`, `CASE`, `printf`



### 1. 상품명의 글자 수를 구하세요. 이름이 가장 긴 상품 10개.


상품명의 글자 수를 구하세요. 이름이 가장 긴 상품 10개.


**힌트 1:** `LENGTH(name)`으로 문자열 길이를 구합니다. `ORDER BY LENGTH(name) DESC LIMIT 10`.


??? success "정답"
    ```sql
    SELECT
        name,
        LENGTH(name) AS name_length
    FROM products
    ORDER BY name_length DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | name_length |
    |---|---|
    | HP EliteBook 840 G10 블랙 [특별 한정판 에디션] ... | 64 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 61 |
    | ASUS ExpertBook B5 [특별 한정판 에디션] RGB 라... | 59 |
    | ASUS ExpertBook B5 [특별 한정판 에디션] 저소음 설... | 58 |
    | TeamGroup T-Force Delta RGB DDR5 32GB... | 48 |
    | CORSAIR Dominator Titanium DDR5 32GB ... | 47 |
    | Arctic Liquid Freezer III Pro 420 A-R... | 43 |


---


### 2. 브랜드명을 모두 대문자로 변환하여 고유한 브랜드 목록을 조회하세요.


브랜드명을 모두 대문자로 변환하여 고유한 브랜드 목록을 조회하세요.


**힌트 1:** `UPPER(brand)`로 대문자 변환, `DISTINCT`로 중복 제거합니다.


??? success "정답"
    ```sql
    SELECT DISTINCT UPPER(brand) AS brand_upper
    FROM products
    ORDER BY brand_upper;
    ```


    **실행 결과** (총 55행 중 상위 7행)

    | brand_upper |
    |---|
    | ADOBE |
    | AMD |
    | APC |
    | APPLE |
    | ARCTIC |
    | ASROCK |
    | ASUS |


---


### 3. 상품명에서 브랜드 부분을 제거하고 나머지 이름만 추출하세요.


상품명에서 브랜드 부분을 제거하고 나머지 이름만 추출하세요.


**힌트 1:** `SUBSTR(name, LENGTH(brand) + 2)`로 브랜드명 + 공백 이후의 문자열을 추출합니다.


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


    **실행 결과** (총 15행 중 상위 7행)

    | brand | name | model_name |
    |---|---|---|
    | AMD | AMD Ryzen 9 9900X | Ryzen 9 9900X |
    | AMD | AMD Ryzen 9 9900X | Ryzen 9 9900X |
    | APC | APC Back-UPS Pro Gaming BGM1500B 블랙 | Back-UPS Pro Gaming BGM1500B 블랙 |
    | ASRock | ASRock B850M Pro RS 블랙 | B850M Pro RS 블랙 |
    | ASRock | ASRock B850M Pro RS 실버 | B850M Pro RS 실버 |
    | ASRock | ASRock B850M Pro RS 화이트 | B850M Pro RS 화이트 |
    | ASRock | ASRock B860M Pro RS 실버 | B860M Pro RS 실버 |


---


### 4. 고객 이메일에서 '@' 앞의 아이디 부분만 추출하세요.


고객 이메일에서 '@' 앞의 아이디 부분만 추출하세요.


**힌트 1:** `SUBSTR(email, 1, INSTR(email, '@') - 1)`로 '@' 앞까지 자릅니다. `INSTR`은 문자열 내 특정 문자의 위치를 반환합니다.


??? success "정답"
    ```sql
    SELECT
        email,
        SUBSTR(email, 1, INSTR(email, '@') - 1) AS user_id
    FROM customers
    ORDER BY user_id
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | email | user_id |
    |---|---|
    | user1@testmail.kr | user1 |
    | user10@testmail.kr | user10 |
    | user100@testmail.kr | user100 |
    | user1000@testmail.kr | user1000 |
    | user1001@testmail.kr | user1001 |
    | user1002@testmail.kr | user1002 |
    | user1003@testmail.kr | user1003 |


---


### 5. 상품명에서 색상 정보('블랙', '화이트', '실버')를 제거하세요.


상품명에서 색상 정보('블랙', '화이트', '실버')를 제거하세요.


**힌트 1:** `REPLACE`를 중첩하여 여러 문자열을 제거합니다. `TRIM`으로 끝에 남은 공백을 정리합니다.


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


    **실행 결과** (총 15행 중 상위 7행)

    | name | name_no_color |
    |---|---|
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | APC Back-UPS Pro Gaming BGM1500B |
    | ASRock B850M Pro RS 블랙 | ASRock B850M Pro RS |
    | ASRock B850M Pro RS 실버 | ASRock B850M Pro RS |
    | ASRock B850M Pro RS 화이트 | ASRock B850M Pro RS |
    | ASRock B860M Pro RS 실버 | ASRock B860M Pro RS |
    | ASRock B860M Pro RS 화이트 | ASRock B860M Pro RS |
    | ASRock B860M Pro RS 화이트 | ASRock B860M Pro RS |


---


### 6. 고객 전화번호에서 하이픈(-)을 제거한 번호를 만드세요.


고객 전화번호에서 하이픈(-)을 제거한 번호를 만드세요.


**힌트 1:** `REPLACE(phone, '-', '')`로 하이픈을 빈 문자열로 치환합니다.


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


    **실행 결과** (총 10행 중 상위 7행)

    | name | phone | phone_no_dash | digit_count |
    |---|---|---|---|
    | 정준호 | 020-4964-6200 | 02049646200 | 11 |
    | 김경수 | 020-4423-5167 | 02044235167 | 11 |
    | 김민재 | 020-0806-0711 | 02008060711 | 11 |
    | 진정자 | 020-9666-8856 | 02096668856 | 11 |
    | 이정수 | 020-0239-9503 | 02002399503 | 11 |
    | 김준혁 | 020-0786-7765 | 02007867765 | 11 |
    | 김명자 | 020-4487-2922 | 02044872922 | 11 |


---


### 7. 상품의 SKU 코드에서 카테고리 약어(첫 2글자)를 추출하세요.


상품의 SKU 코드에서 카테고리 약어(첫 2글자)를 추출하세요.


**힌트 1:** `SUBSTR(sku, 1, 2)`로 SKU의 첫 2글자를 추출합니다. SKU 형식은 `LA-GEN-삼성-00001` 같은 구조입니다.


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


    **실행 결과** (총 15행 중 상위 7행)

    | sku | category_code | name |
    |---|---|---|
    | AU-BOS-00256 | AU | 보스 SoundLink Flex 블랙 |
    | AU-JBL-00019 | AU | JBL Quantum ONE 화이트 |
    | AU-JBL-00055 | AU | JBL Flip 6 화이트 |
    | AU-JBL-00070 | AU | JBL Pebbles 2 블랙 |
    | AU-JBL-00096 | AU | JBL Flip 6 블랙 |
    | AU-RAZ-00253 | AU | Razer Kraken V4 블랙 |
    | AU-SNY-00009 | AU | 소니 WH-CH720N 실버 |


---


### 8. 카테고리별 소속 브랜드를 쉼표로 나열하세요.


카테고리별 소속 브랜드를 쉼표로 나열하세요.


**힌트 1:** `GROUP_CONCAT(DISTINCT brand, ', ')`로 카테고리 내 고유 브랜드를 쉼표 구분 문자열로 합칩니다.


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


---


### 9. 상품명에 'RTX'가 포함된 상품에서 RTX 뒤의 모델 번호를 추출하세요.


상품명에 'RTX'가 포함된 상품에서 RTX 뒤의 모델 번호를 추출하세요.


**힌트 1:** `INSTR(name, 'RTX')`로 'RTX'의 위치를 찾고, `SUBSTR(name, INSTR(...) + 4, 4)`로 모델 번호 부분을 추출합니다.


??? success "정답"
    ```sql
    SELECT
        name,
        SUBSTR(name, INSTR(name, 'RTX') + 4, 4) AS rtx_model
    FROM products
    WHERE name LIKE '%RTX%'
    ORDER BY rtx_model DESC;
    ```


    **실행 결과** (7행)

    | name | rtx_model |
    |---|---|
    | 기가바이트 RTX 5090 AERO OC | 5090 |
    | ASUS TUF Gaming RTX 5080 화이트 | 5080 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 5070 |
    | ASUS Dual RTX 5070 Ti 실버 | 5070 |
    | 기가바이트 RTX 4090 AERO OC 화이트 | 4090 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 4070 |
    | ASUS Dual RTX 4060 Ti 블랙 | 4060 |


---


### 10. 주문 금액을 만원 단위로 반올림하세요. 금액이 큰 상위 10건.


주문 금액을 만원 단위로 반올림하세요. 금액이 큰 상위 10건.


**힌트 1:** `ROUND(total_amount, -4)`로 만원(10,000) 단위로 반올림합니다. 음수 자릿수는 정수 부분을 반올림합니다.


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


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | total_amount | rounded_10k | in_man_won |
    |---|---|---|---|
    | ORD-20201121-08810 | 50,867,500.00 | 50,867,500.00 | 5,086.75 |
    | ORD-20250305-32265 | 46,820,024.00 | 46,820,024.00 | 4,682.00 |
    | ORD-20200209-05404 | 43,677,500.00 | 43,677,500.00 | 4,367.75 |
    | ORD-20251218-37240 | 38,626,400.00 | 38,626,400.00 | 3,862.64 |
    | ORD-20220106-15263 | 37,987,600.00 | 37,987,600.00 | 3,798.76 |
    | ORD-20200820-07684 | 37,518,200.00 | 37,518,200.00 | 3,751.82 |
    | ORD-20220224-15869 | 35,397,700.00 | 35,397,700.00 | 3,539.77 |


---


### 11. 마진율이 0인 상품을 안전하게 처리하세요. NULLIF로 0 나누기를 방지합니다.


마진율이 0인 상품을 안전하게 처리하세요. NULLIF로 0 나누기를 방지합니다.


**힌트 1:** `NULLIF(cost_price, 0)`은 cost_price가 0이면 NULL을 반환합니다. NULL로 나누면 결과가 NULL이 되어 오류가 발생하지 않습니다.


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


    **실행 결과** (총 15행 중 상위 7행)

    | name | price | cost_price | margin_pct |
    |---|---|---|---|
    | Norton AntiVirus Plus 실버 | 74,800.00 | 32,400.00 | 130.90 |
    | Windows 11 Pro 실버 | 423,000.00 | 198,800.00 | 112.80 |
    | 한컴오피스 2024 기업용 실버 | 241,400.00 | 116,400.00 | 107.40 |
    | 로지텍 G502 HERO 실버 | 71,100.00 | 36,500.00 | 94.80 |
    | V3 Endpoint Security 블랙 | 46,500.00 | 24,200.00 | 92.10 |
    | Microsoft 365 Personal | 108,200.00 | 57,900.00 | 86.90 |
    | TP-Link Archer TBE400E 화이트 | 30,200.00 | 16,300.00 | 85.30 |


---


### 12. 주문 금액을 텍스트 포맷('1,234,567원')으로 변환하세요.


주문 금액을 텍스트 포맷('1,234,567원')으로 변환하세요.


**힌트 1:** `printf('%,d', total_amount)`로 천 단위 쉼표를 추가합니다. `||`로 '원' 단위를 붙입니다.


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


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | total_amount | formatted_amount |
    |---|---|---|
    | ORD-20201121-08810 | 50,867,500.00 | 50,867,500원 |
    | ORD-20250305-32265 | 46,820,024.00 | 46,820,024원 |
    | ORD-20200209-05404 | 43,677,500.00 | 43,677,500원 |
    | ORD-20251218-37240 | 38,626,400.00 | 38,626,400원 |
    | ORD-20220106-15263 | 37,987,600.00 | 37,987,600원 |
    | ORD-20200820-07684 | 37,518,200.00 | 37,518,200원 |
    | ORD-20220224-15869 | 35,397,700.00 | 35,397,700원 |


---


### 13. 상품 가격을 구간별 라벨로 분류하세요. IIF 또는 CASE를 사용합니다.


상품 가격을 구간별 라벨로 분류하세요. IIF 또는 CASE를 사용합니다.


**힌트 1:** `IIF(조건, 참, 거짓)`은 SQLite의 간단한 조건 함수입니다. 다중 조건에는 `CASE WHEN`이 더 적합합니다.


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


    **실행 결과** (총 15행 중 상위 7행)

    | name | price | price_range | price_class |
    |---|---|---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 | 200만원 이상 | 고가 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 | 200만원 이상 | 고가 |
    | Razer Blade 18 블랙 | 4,353,100.00 | 200만원 이상 | 고가 |
    | Razer Blade 16 실버 | 3,702,900.00 | 200만원 이상 | 고가 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 | 200만원 이상 | 고가 |
    | ASUS ROG Strix GT35 | 3,296,800.00 | 200만원 이상 | 고가 |
    | Razer Blade 18 블랙 | 2,987,500.00 | 200만원 이상 | 고가 |


---


### 14. 문자열로 저장된 숫자를 정수/실수로 변환하세요. 재고 수량의 타입 변환.


문자열로 저장된 숫자를 정수/실수로 변환하세요. 재고 수량의 타입 변환.


**힌트 1:** `CAST(값 AS INTEGER)` 또는 `CAST(값 AS REAL)`로 타입을 변환합니다. `TYPEOF()`로 현재 타입을 확인할 수 있습니다.


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


    **실행 결과** (총 10행 중 상위 7행)

    | name | stock_qty | original_type | stock_as_real | converted_type | price_int |
    |---|---|---|---|---|---|
    | Arctic Liquid Freezer III 240 | 500 | integer | 500.00 | real | 98,600 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 499 | integer | 499.00 | real | 1,744,000 |
    | 시소닉 VERTEX GX-1200 블랙 | 498 | integer | 498.00 | real | 369,800 |
    | ASRock B850M Pro RS 실버 | 496 | integer | 496.00 | real | 665,600 |
    | TP-Link Archer TX55E 블랙 | 495 | integer | 495.00 | real | 64,000 |
    | 엡손 L15160 | 493 | integer | 493.00 | real | 1,019,500 |
    | 삼성 오디세이 G7 32 | 491 | integer | 491.00 | real | 355,500 |


---


### 15. 고객 등급별 이름 목록을 만드세요. 각 등급의 처음 5명만 쉼표로 연결.


고객 등급별 이름 목록을 만드세요. 각 등급의 처음 5명만 쉼표로 연결.


**힌트 1:** 서브쿼리에서 `ROW_NUMBER()`로 등급 내 순번을 매기고, 5명까지만 필터한 뒤 `GROUP_CONCAT`으로 합칩니다.


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


    **실행 결과** (4행)

    | grade | total_count | sample_names |
    |---|---|---|
    | VIP | 5 | 이영자, 김민재, 이영철, 김병철, 한승민 |
    | SILVER | 5 | 홍경희, 이정수, 노도현, 김성진, 이미정 |
    | GOLD | 5 | 유현지, 서경숙, 박중수, 배종수, 박서윤 |
    | BRONZE | 5 | 이승민, 강은서, 김건우, 윤정남, 남예준 |


---


### 16. 주문번호에서 날짜와 일련번호를 분리하세요. 주문번호 형식: ORD-YYYYMMDD-NNNNN.


주문번호에서 날짜와 일련번호를 분리하세요. 주문번호 형식: ORD-YYYYMMDD-NNNNN.


**힌트 1:** `SUBSTR(order_number, 5, 8)`로 날짜 부분(YYYYMMDD), `SUBSTR(order_number, 14)`로 일련번호를 추출합니다.


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


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | date_part | formatted_date | sequence_no |
    |---|---|---|---|
    | ORD-20251231-37555 | 20251231 | 2025-12-31 | 37,555 |
    | ORD-20251231-37543 | 20251231 | 2025-12-31 | 37,543 |
    | ORD-20251231-37552 | 20251231 | 2025-12-31 | 37,552 |
    | ORD-20251231-37548 | 20251231 | 2025-12-31 | 37,548 |
    | ORD-20251231-37542 | 20251231 | 2025-12-31 | 37,542 |
    | ORD-20251231-37546 | 20251231 | 2025-12-31 | 37,546 |
    | ORD-20251231-37547 | 20251231 | 2025-12-31 | 37,547 |


---


### 17. 상품명에서 용량/크기 정보(숫자+GB/TB/MHz/W)를 포함하는 상품만 조회하세요.


상품명에서 용량/크기 정보(숫자+GB/TB/MHz/W)를 포함하는 상품만 조회하세요.


**힌트 1:** `GLOB`은 대소문자를 구분하는 패턴 매칭입니다. `*[0-9]GB*`, `*[0-9]TB*` 등으로 숫자 뒤 단위가 오는 패턴을 찾습니다.


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


    **실행 결과** (총 15행 중 상위 7행)

    | name | price | brand |
    |---|---|---|
    | Seagate IronWolf 4TB 블랙 | 545,400.00 | Seagate |
    | WD Gold 12TB | 541,900.00 | WD |
    | be quiet! Straight Power 12 1000W 블랙 | 331,100.00 | be quiet! |
    | Seagate Exos 16TB 실버 | 303,300.00 | Seagate |
    | be quiet! Dark Power 13 1000W | 293,000.00 | be quiet! |
    | Kingston FURY Renegade DDR5 32GB 7200... | 282,300.00 | Kingston |
    | Kingston FURY Renegade DDR5 32GB 7200... | 276,900.00 | Kingston |


---


### 18. 상품 요약 카드: 상품 정보를 한 줄 문자열로 포맷팅하세요.


상품 요약 카드: 상품 정보를 한 줄 문자열로 포맷팅하세요.


**힌트 1:** `||`(문자열 연결)과 `COALESCE`, `printf`를 조합하여 포맷팅합니다. NULL 값은 `COALESCE`로 기본값 처리.


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


    **실행 결과** (5행)

    | product_card |
    |---|
    | [Apple] MacBook Air 15 M3 실버 | 5,481,... |
    | [ASUS] ASUS Dual RTX 5070 Ti [특별 한정판 ... |
    | [Razer] Razer Blade 18 블랙 | 4,353,100... |
    | [Razer] Razer Blade 16 실버 | 3,702,900... |
    | [ASUS] ASUS ROG Strix G16CH 화이트 | 3,6... |


---


### 19. 고객 가입 채널별 이메일 도메인 분석: 가입 채널과 이메일 도메인의 교차 집계.


고객 가입 채널별 이메일 도메인 분석: 가입 채널과 이메일 도메인의 교차 집계.


**힌트 1:** `SUBSTR(email, INSTR(email, '@') + 1)`로 도메인을 추출합니다. `COALESCE(acquisition_channel, '미확인')`으로 NULL 처리.


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


    **실행 결과** (5행)

    | channel | domain | customer_count |
    |---|---|---|
    | search_ad | testmail.kr | 1543 |
    | social | testmail.kr | 1425 |
    | organic | testmail.kr | 1146 |
    | referral | testmail.kr | 708 |
    | direct | testmail.kr | 408 |


---


### 20. 상품별 종합 리포트: 가격 구간, 마진율, 재고 상태, 판매 활성도를 하나의 문자열로 요약하세요.


상품별 종합 리포트: 가격 구간, 마진율, 재고 상태, 판매 활성도를 하나의 문자열로 요약하세요.


**힌트 1:** 여러 함수(`CASE`, `ROUND`, `IIF`, `printf`, `COALESCE`, `||`)를 조합하여 종합 리포트를 생성합니다.


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


    **실행 결과** (총 15행 중 상위 7행)

    | name | price_tier | margin_pct | stock_status | sale_status | display_price |
    |---|---|---|---|---|---|
    | MacBook Air 15 M3 실버 | 고가 | 71.0% | 충분 | 판매중 | 5,481,100원 |
    | ASUS TUF Gaming RTX 5080 화이트 | 고가 | 49.0% | 충분 | 단종 | 4,526,600원 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 고가 | 36.4% | 충분 | 판매중 | 4,496,700원 |
    | Razer Blade 18 블랙 | 고가 | 42.9% | 충분 | 판매중 | 4,353,100원 |
    | Razer Blade 16 실버 | 고가 | 28.3% | 충분 | 판매중 | 3,702,900원 |
    | ASUS ROG Strix G16CH 화이트 | 고가 | 48.0% | 충분 | 판매중 | 3,671,500원 |
    | ASUS ROG Zephyrus G16 | 고가 | 11.2% | 충분 | 단종 | 3,429,900원 |


---
