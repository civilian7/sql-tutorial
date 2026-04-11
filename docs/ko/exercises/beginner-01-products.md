# 상품 데이터 탐색

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `products` --- 상품 정보 (이름, 가격, 재고, 브랜드 등)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    `SELECT`<br>
    `WHERE`<br>
    `ORDER BY`<br>
    `LIMIT`<br>
    `DISTINCT`<br>
    별칭(`AS`)

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

    | id | category_id | supplier_id | successor_id | name | sku | brand | model_number | description | specs | price | cost_price | stock_qty | weight_grams | is_active | discontinued_at | created_at | updated_at |
    | ----------: | ----------: | ----------: | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ----------: | ----------: | ----------: | ----------: | ----------: | ---------- | ---------- | ---------- |
    | 1 | 7 | 20 | (NULL) | Razer Blade 18 블랙 | LA-GAM-RAZ-00001 | Razer | RAZ-00001 | Razer Razer Blade 18 블랙 - 고성능, 최신 기술 탑재 | {"screen_size": "14 inch", "cpu": "Apple M3", "ram": "8GB", "storage": "256GB", "weight_kg": 1.7, "battery_hours": 6} | 3730900.0 | 3086700.0 | 107 | 2556 | 1 | (NULL) | 2016-11-20 02:59:21 | 2016-11-20 02:59:21 |
    | 2 | 28 | 27 | (NULL) | MSI GeForce RTX 4070 Ti Super GAMING X | GP-NVI-MSI-00002 | MSI | MSI-00002 | MSI MSI GeForce RTX 4070 Ti Super GAMING X - 고성능, 최신 기술 탑재 | {"vram": "12GB", "clock_mhz": 2447, "tdp_watts": 271} | 1744000.0 | 1360300.0 | 499 | 1632 | 1 | (NULL) | 2016-08-05 10:29:33 | 2016-08-05 10:29:33 |
    | 3 | 21 | 1 | (NULL) | 삼성 DDR4 32GB PC4-25600 | RA-DDR-SAM-00003 | 삼성전자 | 삼성전-00003 | 삼성전자 삼성 DDR4 32GB PC4-25600 - 고성능, 최신 기술 탑재 | {"capacity_gb": 32, "speed_mhz": 5600, "type": "DDR5"} | 46100.0 | 37900.0 | 359 | 40 | 1 | (NULL) | 2016-12-25 00:50:46 | 2016-12-25 00:50:46 |
    | 4 | 11 | 31 | (NULL) | Dell U2724D | MO-GEN-DEL-00004 | Dell | DEL-00004 | Dell Dell U2724D - 고성능, 최신 기술 탑재 | {"screen_size": "27 inch", "resolution": "QHD", "refresh_rate": 144, "panel": "IPS"} | 865000.0 | 565700.0 | 337 | 4817 | 1 | (NULL) | 2016-03-27 09:13:57 | 2016-03-27 09:13:57 |
    | 5 | 22 | 48 | (NULL) | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | RA-DDR-GSK-00005 | G.SKILL | G.S-00005 | G.SKILL G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 - 고성능, 최신 기술 탑재 | {"capacity_gb": 32, "speed_mhz": 6400, "type": "DDR5"} | 161900.0 | 121400.0 | 59 | 60 | 1 | (NULL) | 2016-01-27 23:02:53 | 2016-01-27 23:02:53 |
    | 6 | 29 | 27 | (NULL) | MSI Radeon RX 9070 VENTUS 3X 화이트 | GP-AMD-MSI-00006 | MSI | MSI-00006 | MSI MSI Radeon RX 9070 VENTUS 3X 화이트 - 고성능, 최신 기술 탑재 | {"vram": "16GB", "clock_mhz": 1946, "tdp_watts": 411} | 618800.0 | 431800.0 | 460 | 1789 | 1 | (NULL) | 2016-08-19 16:26:49 | 2016-08-19 16:26:49 |
    | 7 | 22 | 1 | (NULL) | 삼성 DDR5 32GB PC5-38400 | RA-DDR-SAM-00007 | 삼성전자 | 삼성전-00007 | 삼성전자 삼성 DDR5 32GB PC5-38400 - 고성능, 최신 기술 탑재 | {"capacity_gb": 64, "speed_mhz": 3200, "type": "DDR4"} | 194700.0 | 151900.0 | 340 | 46 | 1 | (NULL) | 2016-01-01 15:45:49 | 2016-01-01 15:45:49 |
    | 8 | 36 | 19 | (NULL) | 로지텍 G715 화이트 | KE-MEC-LOG-00008 | 로지텍 | 로지텍-00008 | 로지텍 로지텍 G715 화이트 - 고성능, 최신 기술 탑재 | (NULL) | 254400.0 | 135700.0 | 341 | 1168 | 1 | (NULL) | 2016-02-18 09:35:31 | 2016-02-18 09:35:31 |
    | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

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
    | ---------- | ----------: |
    | ASUS ROG Strix G16CH 화이트 | 3307900.0 |
    | ASUS TUF Gaming RTX 5080 화이트 | 3994200.0 |
    | ASUS ROG Strix Scar 16 실버 | 1511700.0 |
    | ASUS ExpertBook B5 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | 1629100.0 |
    | ASUS PCE-BE92BT | 50800.0 |
    | ASUS Dual RTX 4060 Ti 블랙 | 1271700.0 |
    | ASUS Dual RX 9070 실버 | 747200.0 |
    | ASUS PRIME Z890-A WIFI 실버 | 463900.0 |
    | ... | ... |

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
    | ---------- | ----------: |
    | Razer Blade 18 블랙 | 3730900.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 |
    | LG 일체형PC 27V70Q 실버 | 1028600.0 |
    | Razer Blade 18 화이트 | 3879900.0 |
    | ASUS ROG Strix G16CH 화이트 | 3307900.0 |
    | 한성 보스몬스터 DX5800 블랙 | 1189600.0 |
    | ASUS TUF Gaming RTX 5080 화이트 | 3994200.0 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트 | 1409500.0 |
    | ... | ... |

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
    | ---------- | ----------: | ---------- |
    | 소니 WH-CH720N 실버 | 378900.0 | 2023-09-21 01:03:38 |
    | WD Elements 2TB 블랙 | 239700.0 | 2024-08-25 09:29:10 |
    | JBL Quantum ONE 화이트 | 294800.0 | 2023-06-01 06:11:13 |
    | 주연 리오나인 i7 시스템 실버 | 744100.0 | 2023-05-08 03:08:52 |
    | ASUS TUF Gaming RTX 5080 화이트 | 3994200.0 | 2017-05-15 20:10:25 |
    | 로지텍 G713 실버 | 139200.0 | 2020-05-02 13:07:12 |
    | 삼성 DDR4 32GB PC4-25600 | 113700.0 | 2017-08-03 21:40:45 |
    | ASUS ROG Strix Scar 16 실버 | 1511700.0 | 2019-11-12 00:23:31 |
    | ... | ... | ... |

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
    | ---------- | ----------: |
    | Dell U2724D | 865000.0 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 618800.0 |
    | 넷기어 Nighthawk RS700S 블랙 | 605400.0 |
    | 한성 보스몬스터 DX9900 실버 | 763600.0 |
    | 주연 리오나인 i7 시스템 실버 | 744100.0 |
    | HP Envy x360 15 실버 | 883400.0 |
    | ASRock B850M Pro RS 실버 | 607200.0 |
    | 넷기어 Orbi 970 블랙 | 865300.0 |
    | ... | ... |

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
    | ---------- | ---------- | ----------: |
    | MSI GeForce RTX 4070 Ti Super GAMING X | MSI | 1744000.0 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | MSI | 618800.0 |
    | MSI MAG X870E TOMAHAWK WIFI 화이트 | MSI | 473800.0 |
    | ASUS ROG Strix G16CH 화이트 | ASUS | 3307900.0 |
    | ASUS TUF Gaming RTX 5080 화이트 | ASUS | 3994200.0 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트 | MSI | 1409500.0 |
    | ASUS ROG Strix Scar 16 실버 | ASUS | 1511700.0 |
    | ASUS ExpertBook B5 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | ASUS | 1629100.0 |
    | ... | ... | ... |

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
    | ---------- | ----------: |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 |
    | ASUS TUF Gaming RTX 5080 화이트 | 3994200.0 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트 | 1409500.0 |
    | APC Back-UPS Pro Gaming BGM1500B 화이트 | 449500.0 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | 624300.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 4624100.0 |
    | ASUS TUF Gaming RX 9070 XT OC 블랙 | 1199500.0 |
    | ASUS TUF Gaming RX 9070 XT OC 실버 | 829400.0 |
    | ... | ... |

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
    | ---------- | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 |
    | Razer Blade 16 블랙 | 5634900.0 |
    | Razer Blade 16 | 5518300.0 |
    | Razer Blade 16 화이트 | 5503500.0 |
    | Razer Blade 18 | 5450500.0 |
    | ... | ... |

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
    | ---------- | ----------: |
    | TP-Link TL-SG108 실버 | 16500.0 |
    | TP-Link TG-3468 블랙 | 19800.0 |
    | 삼성 무선 키보드 Trio 500 화이트 | 20300.0 |
    | TP-Link TL-SG1016D 화이트 | 20300.0 |
    | 로지텍 G502 HERO 실버 | 20300.0 |
    | Razer Cobra 실버 | 20300.0 |
    | TP-Link Archer TX55E 실버 | 20500.0 |
    | 로지텍 G402 | 20500.0 |
    | ... | ... |

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
    | ---------- | ----------: |
    | TP-Link TL-SG108 실버 | 16500.0 |
    | TP-Link TG-3468 블랙 | 19800.0 |
    | 삼성 무선 키보드 Trio 500 화이트 | 20300.0 |
    | TP-Link TL-SG1016D 화이트 | 20300.0 |
    | 로지텍 G502 HERO 실버 | 20300.0 |
    | Razer Cobra 실버 | 20300.0 |
    | TP-Link Archer TX55E 실버 | 20500.0 |
    | 로지텍 G402 | 20500.0 |
    | ... | ... |

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
    | ---------- | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 |
    | Razer Blade 16 블랙 | 5634900.0 |
    | Razer Blade 16 | 5518300.0 |
    | Razer Blade 18 | 5450500.0 |
    | Razer Blade 14 | 5339100.0 |
    | Razer Blade 16 실버 | 5127500.0 |
    | Razer Blade 18 화이트 | 4913500.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 4881500.0 |
    | ... | ... |

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
    | ---------- | ---------- | ----------: |
    | MSI GeForce RTX 4070 Ti Super GAMING X | MSI | 1744000.0 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | MSI | 618800.0 |
    | MSI MAG X870E TOMAHAWK WIFI 화이트 | MSI | 473800.0 |
    | ASUS ROG Strix G16CH 화이트 | ASUS | 3307900.0 |
    | ASUS TUF Gaming RTX 5080 화이트 | ASUS | 3994200.0 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트 | MSI | 1409500.0 |
    | ASUS ROG Strix Scar 16 실버 | ASUS | 1511700.0 |
    | ASUS ExpertBook B5 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | ASUS | 1629100.0 |
    | ... | ... | ... |

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
    | ---------- | ----------: |
    | Razer Blade 18 블랙 | 3730900.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 |
    | 삼성 DDR4 32GB PC4-25600 | 46100.0 |
    | Dell U2724D | 865000.0 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 161900.0 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 618800.0 |
    | 삼성 DDR5 32GB PC5-38400 | 194700.0 |
    | 로지텍 G715 화이트 | 254400.0 |
    | ... | ... |

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
    | ---------- | ----------: |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 4881500.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 4624100.0 |
    | ASUS Dual RTX 4060 Ti 실버 | 4294000.0 |
    | 기가바이트 RTX 5080 GAMING OC 화이트 | 4229900.0 |
    | 기가바이트 RTX 4060 EAGLE OC 실버 | 4218800.0 |
    | ASUS Dual RTX 4060 Ti | 4214800.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 블랙 | 4194600.0 |
    | 기가바이트 RTX 4090 AERO OC | 4177400.0 |
    | ... | ... |

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
    | ---------- | ----------: | ----------: |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 | 499 |
    | ASUS ROG Strix G16 실버 | 2272200.0 | 499 |
    | HP Slim Desktop S01 | 1712800.0 | 497 |
    | 삼성 오디세이 G7 32 화이트 | 2479000.0 | 495 |
    | Dell XPS Desktop 8960 실버 | 1282100.0 | 494 |
    | 레노버 ThinkCentre M70q 화이트 [특별 한정판 에디션] 고급 알루미늄 합금 바디 적용, 프리미엄 패키지 구성 | 1570900.0 | 494 |
    | LG 그램 프로 16 화이트 | 2797000.0 | 492 |
    | ASUS ROG Swift PG32UCDM 화이트 | 1719300.0 | 492 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ----------: |
    | LG 일체형PC 27V70Q 실버 | 2 | 1028600.0 |
    | 삼성 DM500TEA 블랙 | 2 | 2598300.0 |
    | HP Slim Desktop S01 화이트 | 2 | 1644700.0 |
    | Dell XPS Desktop 8960 실버 | 2 | 1282100.0 |
    | Dell Inspiron Desktop | 2 | 1153400.0 |
    | HP Slim Desktop S01 | 2 | 1712800.0 |
    | 삼성 DM500TDA | 2 | 2332400.0 |
    | 삼성 DM500TDA 화이트 | 2 | 2159500.0 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ----------: | ----------: |
    | Razer Blade 18 블랙 | 3730900.0 | 3086700.0 | 644200.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 | 1360300.0 | 383700.0 |
    | 삼성 DDR4 32GB PC4-25600 | 46100.0 | 37900.0 | 8200.0 |
    | Dell U2724D | 865000.0 | 565700.0 | 299300.0 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 | 161900.0 | 121400.0 | 40500.0 |
    | MSI Radeon RX 9070 VENTUS 3X 화이트 | 618800.0 | 431800.0 | 187000.0 |
    | 삼성 DDR5 32GB PC5-38400 | 194700.0 | 151900.0 | 42800.0 |
    | 로지텍 G715 화이트 | 254400.0 | 135700.0 | 118700.0 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 |
    | Razer Blade 16 블랙 | 5634900.0 |
    | Razer Blade 16 | 5518300.0 |
    | Razer Blade 18 | 5450500.0 |
    | Razer Blade 14 | 5339100.0 |
    | Razer Blade 16 실버 | 5127500.0 |
    | Razer Blade 18 화이트 | 4913500.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 4881500.0 |
    | ... | ... |

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
    | ---------- | ---------- | ----------: |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | MSI | 4881500.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | MSI | 4624100.0 |
    | ASUS ROG Strix GT35 실버 | ASUS | 4621600.0 |
    | MSI Katana HX 실버 | MSI | 4429800.0 |
    | ASUS ROG Strix Scar 16 블랙 | ASUS | 4362900.0 |
    | ASUS Dual RTX 4060 Ti 실버 | ASUS | 4294000.0 |
    | ASUS TUF Gaming A15 화이트 | ASUS | 4280800.0 |
    | ASUS Dual RTX 4060 Ti | ASUS | 4214800.0 |
    | ... | ... | ... |

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
    | ---------- | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 |
    | Razer Blade 16 블랙 | 5634900.0 |
    | Razer Blade 16 | 5518300.0 |
    | Razer Blade 18 | 5450500.0 |
    | Razer Blade 14 | 5339100.0 |
    | Razer Blade 16 실버 | 5127500.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 4881500.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 4624100.0 |
    | ... | ... |

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
    | ---------- | ----------: |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 1986400.0 |
    | MSI GeForce RTX 5080 GAMING X TRIO 화이트 | 1879100.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 |
    | MSI GeForce RTX 5070 GAMING X 블랙 | 1608400.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X 블랙 | 1510200.0 |
    | 기가바이트 RTX 5090 AERO OC | 1453600.0 |
    | ASUS ROG STRIX RTX 5070 화이트 | 1432600.0 |
    | ASUS Dual RTX 4060 Ti 블랙 | 1271700.0 |
    | ... | ... |

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
    | ---------- | ----------: | ----------: | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 | 4161000.0 | 3334200.0 |
    | MacBook Air 13 M4 | 4449200.0 | 2451900.0 | 1997300.0 |
    | Razer Blade 16 | 5518300.0 | 3703300.0 | 1815000.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 4881500.0 | 3168100.0 | 1713400.0 |
    | Razer Blade 18 화이트 | 4913500.0 | 3251900.0 | 1661600.0 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: | ---------- |
    | 로지텍 G715 실버 | 100600.0 | 2025-12-27 19:50:12 |
    | 시소닉 FOCUS GM-750 실버 | 98900.0 | 2025-12-25 20:05:49 |
    | SteelSeries Arctis Nova 7 Wireless 실버 | 367300.0 | 2025-12-24 21:58:49 |
    | Dell Latitude 5540 실버 | 1113900.0 | 2025-12-17 22:47:10 |
    | 주연 리오나인 i9 하이엔드 실버 | 1663400.0 | 2025-12-15 15:04:20 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ----------: |
    | Arctic Freezer 36 A-RGB 화이트 | 27400.0 | 0 |
    | 삼성 DDR4 16GB PC4-25600 | 73600.0 | 0 |
    | WD My Passport 2TB 블랙 | 329100.0 | 0 |
    | 삼성 DDR5 32GB PC5-38400 실버 | 158000.0 | 0 |

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
    | ---------- | ----------: | ----------: |
    | 엡손 L15160 | 501700.0 | 323 |
    | 삼성 S24C360 블랙 | 503500.0 | 355 |
    | 넷기어 RAX70 실버 | 506300.0 | 221 |
    | ASRock B860M Pro RS 화이트 | 506700.0 | 390 |
    | 필립스 328E1CA 실버 | 507300.0 | 128 |
    | HP DeskJet 2820 | 508800.0 | 376 |
    | 엡손 L3260 블랙 | 509200.0 | 314 |
    | ASRock Z790 Steel Legend | 511000.0 | 226 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ----------: |
    | 한성 보스몬스터 DX7700 실버 | 19914 | 3230900.0 |
    | ASUS ROG Strix GT35 실버 | 19883 | 2553100.0 |
    | APC Back-UPS Pro BR1500G 실버 | 19791 | 340300.0 |
    | ASUS ROG Strix GT35 화이트 | 19598 | 1637500.0 |
    | ASUS ROG Strix GT35 | 19449 | 3296400.0 |
    | 한성 보스몬스터 DX7700 화이트 | 19250 | 1607700.0 |
    | APC Back-UPS Pro BR1500G 블랙 | 19212 | 217000.0 |
    | 한성 프리워크 P5700 블랙 | 19165 | 3917100.0 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ----------: | ----------: |
    | Microsoft 365 Personal 실버 | 171000.0 | 62900.0 | 63.2 |
    | Adobe Creative Cloud 1년 화이트 | 657900.0 | 256500.0 | 61.0 |
    | V3 365 Clinic | 63300.0 | 25200.0 | 60.2 |
    | Adobe Photoshop 1년 | 313600.0 | 126500.0 | 59.7 |
    | Adobe Creative Cloud 1년 | 309100.0 | 125600.0 | 59.4 |
    | Razer Viper V3 HyperSpeed 블랙 | 99500.0 | 41000.0 | 58.8 |
    | Adobe Acrobat Pro 1년 | 389600.0 | 164600.0 | 57.8 |
    | Windows 11 Pro | 409600.0 | 176800.0 | 56.8 |
    | ... | ... | ... | ... |

    > 소프트웨어(Norton, 한컴오피스)는 물리적 원가가 낮아 마진율이 높습니다.
