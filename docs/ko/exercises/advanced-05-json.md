# JSON 활용

!!! info "사용 테이블"
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `categories` — 카테고리 (부모-자식 계층)  

!!! abstract "학습 범위"
    `JSON_EXTRACT`, `JSON_EACH`, `JSON_GROUP_ARRAY`, `JSON_GROUP_OBJECT`, JSON 경로 표현식, specs 칼럼 활용

25강 JSON 함수에서 배운 내용을 실습합니다.
products 테이블의 `specs` 칼럼에는 카테고리별 사양 정보가 JSON 문자열로 저장되어 있습니다.

!!! info "specs 칼럼 JSON 예시"
    - 노트북: `{"screen_size":"15.6 inch","cpu":"Intel Core i7-13700H","ram_gb":16,"storage_gb":512,"battery_hours":10}`
    - 데스크톱: `{"cpu":"AMD Ryzen 7 7700X","ram_gb":32,"storage_gb":1024,"gpu":"RTX 4070"}`
    - 모니터: `{"screen_size":"27 inch","resolution":"QHD","refresh_rate":144,"panel":"IPS"}`
    - GPU: `{"vram":"16GB","clock_mhz":2100,"tdp_watts":300}`
    - CPU: `{"cores":8,"threads":16,"base_clock_ghz":3.5,"boost_clock_ghz":5.1}`
    - 메모리: `{"capacity_gb":16,"speed_mhz":5600,"type":"DDR5"}`
    - 저장장치: `{"capacity_gb":1024,"interface":"NVMe","read_mbps":7000,"write_mbps":5000}`

---


### 문제 1. JSON 기본 추출 — 노트북 CPU 목록

노트북 카테고리의 모든 활성 상품에서 상품명과 CPU 사양을 추출하세요.
CPU 사양이 NULL인 상품은 제외합니다.


??? tip "힌트"
    - `json_extract(specs, '$.cpu')`로 JSON 내부 값을 추출합니다
    - `categories` 테이블과 JOIN하여 카테고리 필터링

??? success "정답"
    ```sql
    SELECT
        p.name        AS product_name,
        json_extract(p.specs, '$.cpu') AS cpu
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'laptop%'
      AND p.is_active = 1
      AND p.specs IS NOT NULL
    ORDER BY p.name;
    ```

    | product_name | cpu |
    |---|---|
    | (노트북 상품명) | Intel Core i7-13700H |
    | ... | ... |


---


### 문제 2. JSON 여러 필드 추출 — 노트북 스펙 시트

노트북 상품의 화면 크기, CPU, RAM(GB), 저장 용량(GB), 배터리(시간)를 한 번에 추출하여 스펙 시트를 만드세요.
가격 내림차순으로 정렬합니다.


??? tip "힌트"
    - `json_extract`를 여러 번 호출하여 각 필드를 별도 칼럼으로 추출
    - `$.screen_size`, `$.cpu`, `$.ram_gb`, `$.storage_gb`, `$.battery_hours`

??? success "정답"
    ```sql
    SELECT
        p.name                                     AS product_name,
        p.price,
        json_extract(p.specs, '$.screen_size')     AS screen_size,
        json_extract(p.specs, '$.cpu')             AS cpu,
        json_extract(p.specs, '$.ram_gb')          AS ram_gb,
        json_extract(p.specs, '$.storage_gb')      AS storage_gb,
        json_extract(p.specs, '$.battery_hours')   AS battery_hours
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'laptop%'
      AND p.is_active = 1
      AND p.specs IS NOT NULL
    ORDER BY p.price DESC
    LIMIT 20;
    ```

    | product_name | price | screen_size | cpu | ram_gb | storage_gb | battery_hours |
    |---|---|---|---|---|---|---|
    | (노트북명) | 2500000 | 16 inch | Intel Core i9-13900H | 32 | 1024 | 12 |
    | ... | ... | ... | ... | ... | ... | ... |


---


### 문제 3. specs가 NULL인 상품 파악

specs 정보가 없는(NULL) 상품의 카테고리별 분포를 확인하세요.
어떤 카테고리에 스펙 정보가 누락되어 있는지 파악하는 것이 목적입니다.


??? tip "힌트"
    - `WHERE p.specs IS NULL` 조건
    - `GROUP BY` 카테고리명으로 집계

??? success "정답"
    ```sql
    SELECT
        cat.name          AS category,
        COUNT(*)          AS no_specs_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE p.specs IS NULL
      AND p.is_active = 1
    GROUP BY cat.name
    ORDER BY no_specs_count DESC;
    ```

    | category | no_specs_count |
    |---|---|
    | (주변기기 카테고리) | 45 |
    | ... | ... |


---


### 문제 4. JSON 키 목록 나열 — json_each 활용

노트북 상품 하나를 골라, specs JSON에 포함된 모든 키(key) 목록을 나열하세요.
`json_each` 테이블 반환 함수를 사용합니다.


??? tip "힌트"
    - `json_each(specs)`는 JSON 객체의 각 key-value 쌍을 행으로 반환합니다
    - 반환 칼럼: `key`, `value`, `type`
    - `LIMIT 1`로 상품 하나를 선택한 뒤, `json_each`에 전달

??? success "정답"
    ```sql
    SELECT
        je.key,
        je.value,
        je.type
    FROM products AS p,
         json_each(p.specs) AS je
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'laptop%'
      AND p.specs IS NOT NULL
      AND p.id = (
          SELECT MIN(p2.id) FROM products AS p2
          INNER JOIN categories AS c2 ON p2.category_id = c2.id
          WHERE c2.slug LIKE 'laptop%' AND p2.specs IS NOT NULL
      );
    ```

    | key | value | type |
    |---|---|---|
    | screen_size | 15.6 inch | text |
    | cpu | Intel Core i7-13700H | text |
    | ram_gb | 16 | integer |
    | storage_gb | 512 | integer |
    | battery_hours | 10 | integer |


---


### 문제 5. JSON 조건 필터링 — 고성능 노트북 찾기

RAM이 32GB 이상이고 저장 용량이 1024GB 이상인 노트북을 찾으세요.
상품명, 가격, RAM, 저장 용량을 표시합니다.


??? tip "힌트"
    - `json_extract(specs, '$.ram_gb') >= 32`처럼 WHERE 절에서 JSON 값을 조건으로 사용
    - JSON에서 추출된 값은 자동으로 적절한 타입으로 변환됩니다

??? success "정답"
    ```sql
    SELECT
        p.name       AS product_name,
        p.price,
        json_extract(p.specs, '$.ram_gb')      AS ram_gb,
        json_extract(p.specs, '$.storage_gb')  AS storage_gb,
        json_extract(p.specs, '$.cpu')         AS cpu
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'laptop%'
      AND p.is_active = 1
      AND p.specs IS NOT NULL
      AND json_extract(p.specs, '$.ram_gb') >= 32
      AND json_extract(p.specs, '$.storage_gb') >= 1024
    ORDER BY p.price DESC;
    ```

    | product_name | price | ram_gb | storage_gb | cpu |
    |---|---|---|---|---|
    | (고사양 노트북) | 3200000 | 32 | 1024 | Intel Core i9-13900H |
    | ... | ... | ... | ... | ... |


---


### 문제 6. JSON 기반 그룹 집계 — CPU별 평균 가격

노트북과 데스크톱의 CPU 사양별 평균 가격과 상품 수를 구하세요.
상품 수가 3개 이상인 CPU만 표시합니다.


??? tip "힌트"
    - `json_extract(specs, '$.cpu')`를 `GROUP BY`에 사용
    - `HAVING COUNT(*) >= 3`으로 소수 그룹 제외

??? success "정답"
    ```sql
    SELECT
        json_extract(p.specs, '$.cpu')     AS cpu,
        COUNT(*)                           AS product_count,
        ROUND(AVG(p.price))                AS avg_price,
        MIN(p.price)                       AS min_price,
        MAX(p.price)                       AS max_price
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE (cat.slug LIKE 'laptop%' OR cat.slug LIKE 'desktop%')
      AND p.is_active = 1
      AND p.specs IS NOT NULL
    GROUP BY json_extract(p.specs, '$.cpu')
    HAVING COUNT(*) >= 3
    ORDER BY avg_price DESC;
    ```

    | cpu | product_count | avg_price | min_price | max_price |
    |---|---|---|---|---|
    | Intel Core i9-13900H | 5 | 2800000 | 2200000 | 3500000 |
    | AMD Ryzen 9 7950X | 4 | 2500000 | 2000000 | 3000000 |
    | ... | ... | ... | ... | ... |


---


### 문제 7. JSON 기반 통계 — 모니터 패널 타입별 분석

모니터 카테고리에서 패널 타입(IPS/VA/OLED)별로 상품 수, 평균 가격, 평균 주사율을 집계하세요.
각 패널 타입의 해상도 분포도 함께 확인합니다.


??? tip "힌트"
    - `json_extract(specs, '$.panel')`, `json_extract(specs, '$.refresh_rate')` 사용
    - 해상도 분포는 별도 쿼리 또는 조건부 집계(`CASE WHEN`)로 처리

??? success "정답"
    ```sql
    SELECT
        json_extract(p.specs, '$.panel')          AS panel_type,
        COUNT(*)                                   AS product_count,
        ROUND(AVG(p.price))                        AS avg_price,
        ROUND(AVG(json_extract(p.specs, '$.refresh_rate'))) AS avg_refresh_rate,
        SUM(CASE WHEN json_extract(p.specs, '$.resolution') = 'FHD' THEN 1 ELSE 0 END) AS fhd_count,
        SUM(CASE WHEN json_extract(p.specs, '$.resolution') = 'QHD' THEN 1 ELSE 0 END) AS qhd_count,
        SUM(CASE WHEN json_extract(p.specs, '$.resolution') = '4K'  THEN 1 ELSE 0 END) AS uhd_4k_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'monitor%'
      AND p.is_active = 1
      AND p.specs IS NOT NULL
    GROUP BY json_extract(p.specs, '$.panel')
    ORDER BY avg_price DESC;
    ```

    | panel_type | product_count | avg_price | avg_refresh_rate | fhd_count | qhd_count | uhd_4k_count |
    |---|---|---|---|---|---|---|
    | OLED | 8 | 950000 | 165 | 0 | 3 | 5 |
    | IPS | 25 | 450000 | 120 | 8 | 10 | 7 |
    | VA | 12 | 380000 | 100 | 5 | 5 | 2 |


---


### 문제 8. json_set으로 JSON 값 수정 (SELECT 내)

SQLite의 `json_set` 함수를 사용하여, 노트북 상품의 specs에 `"warranty_years": 3` 필드를 추가한 결과를 확인하세요.
실제 UPDATE가 아닌 SELECT에서 변환된 JSON을 미리보기합니다.


??? tip "힌트"
    - `json_set(specs, '$.warranty_years', 3)`은 기존 JSON에 새 키를 추가합니다
    - 이미 존재하는 키라면 값을 덮어씁니다
    - SELECT에서만 확인하므로 실제 데이터는 변경되지 않습니다

??? success "정답"
    ```sql
    SELECT
        p.name         AS product_name,
        p.specs        AS original_specs,
        json_set(p.specs, '$.warranty_years', 3) AS modified_specs
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'laptop%'
      AND p.specs IS NOT NULL
    LIMIT 3;
    ```

    | product_name | original_specs | modified_specs |
    |---|---|---|
    | (노트북명) | {"screen_size":"15.6 inch",...} | {"screen_size":"15.6 inch",...,"warranty_years":3} |


---


### 문제 9. json_remove로 JSON 키 제거 (SELECT 내)

GPU 상품의 specs에서 `tdp_watts` 키를 제거한 결과와 원본을 비교하세요.
`json_remove` 함수를 사용합니다.


??? tip "힌트"
    - `json_remove(specs, '$.tdp_watts')`는 지정한 키를 삭제한 JSON을 반환합니다
    - 원본과 비교하기 위해 `specs`와 `json_remove(...)` 결과를 나란히 표시

??? success "정답"
    ```sql
    SELECT
        p.name        AS product_name,
        p.specs       AS original_specs,
        json_remove(p.specs, '$.tdp_watts') AS specs_without_tdp
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'gpu%'
      AND p.specs IS NOT NULL
    LIMIT 5;
    ```

    | product_name | original_specs | specs_without_tdp |
    |---|---|---|
    | (GPU명) | {"vram":"16GB","clock_mhz":2100,"tdp_watts":300} | {"vram":"16GB","clock_mhz":2100} |


---


### 문제 10. 종합 JSON 분석 — 카테고리별 스펙 비교 리포트

모든 카테고리의 상품 specs를 분석하여, 카테고리별로 JSON에 포함된 고유 키 목록과 각 키의 출현 비율을 구하세요.
어떤 카테고리에 어떤 스펙 정보가 존재하는지 한눈에 파악하는 리포트입니다.


??? tip "힌트"
    - `json_each(specs)`로 모든 키를 행으로 펼친 뒤, 카테고리+키 조합으로 GROUP BY
    - 출현 비율 = 해당 키가 있는 상품 수 / 카테고리 전체 상품 수
    - CTE를 사용하여 단계적으로 집계

??? success "정답"
    ```sql
    WITH spec_keys AS (
        SELECT
            cat.name       AS category,
            je.key,
            COUNT(*)       AS key_count
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id,
             json_each(p.specs) AS je
        WHERE p.specs IS NOT NULL
          AND p.is_active = 1
        GROUP BY cat.name, je.key
    ),
    category_totals AS (
        SELECT
            cat.name       AS category,
            COUNT(*)       AS total_products
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.specs IS NOT NULL
          AND p.is_active = 1
        GROUP BY cat.name
    )
    SELECT
        sk.category,
        sk.key               AS spec_key,
        sk.key_count,
        ct.total_products,
        ROUND(100.0 * sk.key_count / ct.total_products, 1) AS presence_pct
    FROM spec_keys AS sk
    INNER JOIN category_totals AS ct ON sk.category = ct.category
    ORDER BY sk.category, sk.key_count DESC;
    ```

    | category | spec_key | key_count | total_products | presence_pct |
    |---|---|---|---|---|
    | 노트북 | cpu | 50 | 50 | 100.0 |
    | 노트북 | ram_gb | 50 | 50 | 100.0 |
    | 노트북 | screen_size | 50 | 50 | 100.0 |
    | 모니터 | panel | 45 | 45 | 100.0 |
    | 모니터 | resolution | 45 | 45 | 100.0 |
    | ... | ... | ... | ... | ... |
