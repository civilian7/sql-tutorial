# 상품 탐색

!!! info "사용 테이블"

    `categories` — 카테고리 (부모-자식 계층)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `suppliers` — 공급업체 (업체명, 연락처)  



!!! abstract "학습 범위"

    `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `COUNT`, `AVG`, `MIN`, `MAX`, `GROUP BY`, `HAVING`, `LIKE`, `CASE WHEN`, `IS NOT NULL`



### 1. 현재 등록된 전체 상품 수를 구하세요.


현재 등록된 전체 상품 수를 구하세요.


**힌트 1:** COUNT(*) 집계 함수를 사용하세요


??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_products FROM products;
    ```


    **실행 결과** (1행)

    | total_products |
    |---|
    | 280 |


---


### 2. 가격이 높은 순으로 상위 5개 상품의 이름과 가격을 조회하세요.


가격이 높은 순으로 상위 5개 상품의 이름과 가격을 조회하세요.


**힌트 1:** ORDER BY price DESC로 정렬하고 LIMIT 5로 상위 5개만 가져오세요


??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5;
    ```


    **실행 결과** (5행)

    | name | price |
    |---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 |
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 |
    | Razer Blade 18 블랙 | 4,353,100.00 |
    | Razer Blade 16 실버 | 3,702,900.00 |


---


### 3. 가격이 100,000원 이하인 상품의 이름, 브랜드, 가격을 가격 오름차순으로 조회하세요.


가격이 100,000원 이하인 상품의 이름, 브랜드, 가격을 가격 오름차순으로 조회하세요.


**힌트 1:** WHERE price <= 100000 조건과 ORDER BY price ASC를 사용하세요


??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price <= 100000
    ORDER BY price ASC;
    ```


    **실행 결과** (총 48행 중 상위 7행)

    | name | brand | price |
    |---|---|---|
    | TP-Link TG-3468 블랙 | TP-Link | 18,500.00 |
    | 삼성 SPA-KFG0BUB 실버 | 삼성전자 | 21,900.00 |
    | Arctic Freezer 36 A-RGB 화이트 | Arctic | 23,000.00 |
    | Arctic Freezer 36 A-RGB 화이트 | Arctic | 29,900.00 |
    | TP-Link Archer TBE400E 화이트 | TP-Link | 30,200.00 |
    | 삼성 SPA-KFG0BUB | 삼성전자 | 30,700.00 |
    | 로지텍 MK470 블랙 | 로지텍 | 31,800.00 |


---


### 4. 재고가 0인 상품의 이름과 SKU를 조회하세요.


재고가 0인 상품의 이름과 SKU를 조회하세요.


**힌트 1:** WHERE stock_qty = 0 조건으로 필터링하세요


??? success "정답"
    ```sql
    SELECT name, sku
    FROM products
    WHERE stock_qty = 0;
    ```


    **실행 결과** (1행)

    | name | sku |
    |---|---|
    | Arctic Freezer 36 A-RGB 화이트 | CO-AIR-ARC-00049 |


---


### 5. 브랜드별로 몇 개의 상품이 있는지 세고, 상품 수가 많은 순으로 정렬하세요.


브랜드별로 몇 개의 상품이 있는지 세고, 상품 수가 많은 순으로 정렬하세요.


**힌트 1:** GROUP BY brand로 그룹화하고 COUNT(*)로 세기. ORDER BY ... DESC로 정렬


??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    ORDER BY product_count DESC;
    ```


    **실행 결과** (총 55행 중 상위 7행)

    | brand | product_count |
    |---|---|
    | ASUS | 26 |
    | 삼성전자 | 25 |
    | 로지텍 | 17 |
    | MSI | 13 |
    | TP-Link | 11 |
    | LG전자 | 11 |
    | ASRock | 11 |


---


### 6. 단종일(discontinued_at)이 NULL이 아닌 상품의 이름, 가격, 단종일을 조회하세요.


단종일(discontinued_at)이 NULL이 아닌 상품의 이름, 가격, 단종일을 조회하세요.


**힌트 1:** IS NOT NULL로 NULL이 아닌 행만 필터링하세요


??? success "정답"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL
    ORDER BY discontinued_at DESC;
    ```


    **실행 결과** (총 62행 중 상위 7행)

    | name | price | discontinued_at |
    |---|---|---|
    | Dell XPS Desktop 8960 실버 | 1,249,400.00 | 2025-11-20 15:30:12 |
    | Kingston FURY Beast DDR4 16GB 화이트 | 91,200.00 | 2025-11-18 04:06:13 |
    | Intel Core Ultra 7 265K | 196,300.00 | 2025-11-16 21:11:33 |
    | 한성 보스몬스터 DX7700 화이트 | 1,579,400.00 | 2025-10-25 03:47:01 |
    | Intel Core Ultra 7 265K 화이트 | 170,200.00 | 2025-08-24 00:34:53 |
    | SAPPHIRE PULSE RX 7800 XT 실버 | 1,146,300.00 | 2025-08-01 06:10:51 |
    | SteelSeries Arctis Nova Pro Wireless 화이트 | 173,700.00 | 2025-06-27 12:36:27 |


---


### 7. 전체 상품의 평균 가격과 중간 가격대를 구하세요.


전체 상품의 평균 가격과 중간 가격대를 구하세요.


**힌트 1:** AVG(), MIN(), MAX() 집계 함수를 함께 사용하세요. ROUND()로 소수점 정리


??? success "정답"
    ```sql
    SELECT
        ROUND(AVG(price), 2) AS avg_price,
        ROUND(MIN(price), 2) AS min_price,
        ROUND(MAX(price), 2) AS max_price
    FROM products;
    ```


    **실행 결과** (1행)

    | avg_price | min_price | max_price |
    |---|---|---|
    | 649,272.50 | 18,500.00 | 5,481,100.00 |


---


### 8. 브랜드가 'Samsung'인 상품의 이름, 가격, 재고를 조회하세요.


브랜드가 'Samsung'인 상품의 이름, 가격, 재고를 조회하세요.


**힌트 1:** WHERE brand = 'Samsung' 조건을 사용하세요. 문자열은 작은따옴표로 감싸기


??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE brand = 'Samsung'
    ORDER BY price DESC;
    ```


---


### 9. 상품명에 "Gaming"이 포함된 상품을 조회하세요.


상품명에 "Gaming"이 포함된 상품을 조회하세요.


**힌트 1:** LIKE '%Gaming%'으로 부분 문자열을 검색하세요. %는 임의의 문자열을 의미


??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE name LIKE '%Gaming%'
    ORDER BY price DESC;
    ```


    **실행 결과** (5행)

    | name | brand | price |
    |---|---|---|
    | ASUS TUF Gaming RTX 5080 화이트 | ASUS | 4,526,600.00 |
    | MSI Radeon RX 9070 XT GAMING X | MSI | 1,896,000.00 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | MSI | 1,744,000.00 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트 | MSI | 1,517,600.00 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | APC | 516,300.00 |


---


### 10. 재고가 10개 이하이고 판매 중(is_active = 1)인 상품의 이름, 재고, 가격을 조회하세요.


재고가 10개 이하이고 판매 중(is_active = 1)인 상품의 이름, 재고, 가격을 조회하세요.


**힌트 1:** WHERE 절에서 AND로 두 조건을 결합하세요: stock_qty <= 10 AND is_active = 1


??? success "정답"
    ```sql
    SELECT name, stock_qty, price
    FROM products
    WHERE stock_qty <= 10
      AND is_active = 1
    ORDER BY stock_qty ASC;
    ```


    **실행 결과** (3행)

    | name | stock_qty | price |
    |---|---|---|
    | Arctic Freezer 36 A-RGB 화이트 | 0 | 23,000.00 |
    | 삼성 SPA-KFG0BUB | 4 | 30,700.00 |
    | 로지텍 G502 HERO 실버 | 8 | 71,100.00 |


---


### 11. 최상위 카테고리(depth = 0)만 이름순으로 조회하세요.


최상위 카테고리(depth = 0)만 이름순으로 조회하세요.


**힌트 1:** categories 테이블에서 WHERE depth = 0으로 필터링하세요


??? success "정답"
    ```sql
    SELECT id, name, slug
    FROM categories
    WHERE depth = 0
    ORDER BY sort_order;
    ```


    **실행 결과** (총 18행 중 상위 7행)

    | id | name | slug |
    |---|---|---|
    | 1 | 데스크톱 PC | desktop-pc |
    | 5 | 노트북 | laptop |
    | 10 | 모니터 | monitor |
    | 14 | CPU | cpu |
    | 17 | 메인보드 | motherboard |
    | 20 | 메모리(RAM) | ram |
    | 23 | 저장장치 | storage |


---


### 12. 10만원 미만, 10~50만원, 50~100만원, 100만원 이상으로 나누어 각 구간의 상품 수를 구하세요.


10만원 미만, 10~50만원, 50~100만원, 100만원 이상으로 나누어 각 구간의 상품 수를 구하세요.


**힌트 1:** CASE WHEN으로 가격 구간을 분류한 뒤 GROUP BY와 COUNT(*)로 집계하세요


??? success "정답"
    ```sql
    SELECT
        CASE
            WHEN price < 100000 THEN '10만원 미만'
            WHEN price < 500000 THEN '10~50만원'
            WHEN price < 1000000 THEN '50~100만원'
            ELSE '100만원 이상'
        END AS price_range,
        COUNT(*) AS product_count
    FROM products
    GROUP BY price_range
    ORDER BY MIN(price);
    ```


    **실행 결과** (4행)

    | price_range | product_count |
    |---|---|
    | 10만원 미만 | 47 |
    | 10~50만원 | 130 |
    | 50~100만원 | 38 |
    | 100만원 이상 | 65 |


---


### 13. 활성(is_active = 1) 공급업체의 회사명과 담당자명을 조회하세요.


활성(is_active = 1) 공급업체의 회사명과 담당자명을 조회하세요.


**힌트 1:** suppliers 테이블에서 WHERE is_active = 1로 필터링하세요


??? success "정답"
    ```sql
    SELECT company_name, contact_name, email
    FROM suppliers
    WHERE is_active = 1
    ORDER BY company_name;
    ```


    **실행 결과** (총 56행 중 상위 7행)

    | company_name | contact_name | email |
    |---|---|---|
    | AMD코리아 | 강중수 | contact@amd.test.kr |
    | APC코리아 | 박성현 | contact@apc.test.kr |
    | ASRock코리아 | 안예준 | contact@asrock.test.kr |
    | HP코리아 | 김하윤 | contact@hp.test.kr |
    | LG전자 공식 유통 | 김예준 | contact@lg.test.kr |
    | MSI코리아 | 김채원 | contact@msi.test.kr |
    | NZXT코리아 | 이경숙 | contact@nzxt.test.kr |


---


### 14. 각 상품의 마진율((price - cost_price) / price * 100)을 계산하고, 마진율이 높은


각 상품의 마진율((price - cost_price) / price * 100)을 계산하고, 마진율이 높은 순으로 10개를 조회하세요.


**힌트 1:** SELECT 절에서 산술 연산으로 마진율을 계산하세요. ROUND()로 소수점 정리, price > 0 조건으로 0 나눗셈 방지


??? success "정답"
    ```sql
    SELECT
        name,
        price,
        cost_price,
        ROUND((price - cost_price) / price * 100, 1) AS margin_pct
    FROM products
    WHERE price > 0
    ORDER BY margin_pct DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | price | cost_price | margin_pct |
    |---|---|---|---|
    | Norton AntiVirus Plus | 69,700.00 | 28,200.00 | 59.50 |
    | Norton AntiVirus Plus 실버 | 74,800.00 | 32,400.00 | 56.70 |
    | Adobe Creative Cloud 1년 실버 | 327,300.00 | 147,300.00 | 55.00 |
    | Windows 11 Pro 실버 | 423,000.00 | 198,800.00 | 53.00 |
    | 한컴오피스 2024 기업용 실버 | 241,400.00 | 116,400.00 | 51.80 |
    | Microsoft Office 2024 Home | 114,300.00 | 57,200.00 | 50.00 |
    | 로지텍 G502 HERO 실버 | 71,100.00 | 36,500.00 | 48.70 |


---


### 15. 상품이 3개 이상인 브랜드만 대상으로, 평균 가격과 상품 수를 구하세요.


상품이 3개 이상인 브랜드만 대상으로, 평균 가격과 상품 수를 구하세요.


**힌트 1:** GROUP BY brand 후 HAVING COUNT(*) >= 3으로 그룹을 필터링하세요. HAVING은 집계 후 조건


??? success "정답"
    ```sql
    SELECT
        brand,
        COUNT(*) AS product_count,
        ROUND(AVG(price), 2) AS avg_price,
        ROUND(MIN(price), 2) AS min_price,
        ROUND(MAX(price), 2) AS max_price
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 3
    ORDER BY avg_price DESC;
    ```


    **실행 결과** (총 34행 중 상위 7행)

    | brand | product_count | avg_price | min_price | max_price |
    |---|---|---|---|---|
    | Razer | 9 | 1,764,888.89 | 52,500.00 | 4,353,100.00 |
    | ASUS | 26 | 1,683,630.77 | 47,200.00 | 4,526,600.00 |
    | 레노버 | 5 | 1,597,760.00 | 1,389,800.00 | 1,866,100.00 |
    | HP | 6 | 1,479,016.67 | 895,000.00 | 2,080,300.00 |
    | 주연테크 | 4 | 1,413,550.00 | 810,300.00 | 1,849,900.00 |
    | LG전자 | 11 | 1,346,836.36 | 308,900.00 | 1,828,800.00 |
    | 한성컴퓨터 | 4 | 1,104,075.00 | 739,900.00 | 1,579,400.00 |


---
