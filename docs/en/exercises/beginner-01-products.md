# Product Data Exploration

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `products` --- product info (name, price, stock, brand, etc.)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    `SELECT`<br>
    `WHERE`<br>
    `ORDER BY`<br>
    `LIMIT`<br>
    `DISTINCT`<br>
    Aliases (`AS`)

</div>

!!! info "Before You Begin"
    This exercise uses only what you learned in **Beginner Lessons 1-2**(SELECT, WHERE).
    JOINs, subqueries, GROUP BY, and aggregate functions are not used.

---

## Basic (1~10)

Practice one concept at a time.

---

### Problem 1

**Retrieve all data from the products table.**

??? tip "Hint"
    Using `SELECT *` retrieves all columns at once.

??? success "Answer"
    ```sql
    SELECT *
    FROM products;
    ```

    **Result (top 5 rows):**

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

    > The actual result shows all 18 columns. A total of 280 rows are returned.

---

### Problem 2

**Retrieve only the name (`name`), price (`price`), and stock quantity (`stock_qty`) of products.**

??? tip "Hint"
    List the desired column names separated by commas after `SELECT`.

??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products;
    ```

    **Result (top 5 rows):**

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

### Problem 3

**Retrieve the name and price of products where the brand is 'ASUS'.**

??? tip "Hint"
    Use the `=` operator in the `WHERE` clause to filter for exact matches. Strings are enclosed in single quotes.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE brand = 'ASUS';
    ```

    **Result (top 5 rows):**

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

### Problem 4

**Retrieve the name and price of products with a price exceeding 1,000,000.**

??? tip "Hint"
    Use the `>` (greater than) comparison operator in the `WHERE` clause. Numbers are written without quotes.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > 1000000;
    ```

    **Result (top 5 rows):**

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

### Problem 5

**Retrieve the name, price, and discontinuation date (`discontinued_at`) of discontinued products (`is_active = 0`).**

??? tip "Hint"
    `is_active` is a column storing 1 (active) or 0 (discontinued). Filter with `WHERE is_active = 0`.

??? success "Answer"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE is_active = 0;
    ```

    **Result (top 5 rows):**

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

### Problem 6

**Retrieve the name and price of products priced between 500,000 and 1,000,000.**

??? tip "Hint"
    `BETWEEN A AND B` filters for values from A to B (inclusive).

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price BETWEEN 500000 AND 1000000;
    ```

    **Result (top 5 rows):**

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

### Problem 7

**Retrieve the name, brand, and price of products where the brand is 'ASUS', 'MSI', or 'Logitech'.**

??? tip "Hint"
    `IN (value1, value2, value3)` filters rows matching any of the listed values at once.

??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand IN ('ASUS', 'MSI', 'Logitech');
    ```

    **Result (top 5 rows):**

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

### Problem 8

**Retrieve the name and price of products containing 'Gaming' in their name.**

??? tip "Hint"
    `LIKE '%string%'` finds rows containing the string anywhere. `%` represents zero or more arbitrary characters.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%Gaming%';
    ```

    **Result (top 5 rows):**

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

### Problem 9

**Retrieve the name and price of all products sorted by price in descending order.**

??? tip "Hint"
    `ORDER BY column_name DESC` sorts in descending order (large → small).

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC;
    ```

    **Result (top 5 rows):**

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

### Problem 10

**Retrieve the name and price of the top 5 most expensive products.**

??? tip "Hint"
    After sorting with `ORDER BY`, append `LIMIT N` to get only the top N rows.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5;
    ```

    **Result:**

    | name | price |
    | ---------- | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 |
    | Razer Blade 16 블랙 | 5634900.0 |
    | Razer Blade 16 | 5518300.0 |
    | Razer Blade 16 화이트 | 5503500.0 |
    | Razer Blade 18 | 5450500.0 |
    | ... | ... |

---

## Applied (11~20)

Practice combining two concepts.

---

### Problem 11

**Retrieve the name and price of active products (`is_active = 1`) sorted by price in ascending order.**

??? tip "Hint"
    Apply a condition with `WHERE` and sort ascending with `ORDER BY column ASC`. ASC can be omitted.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE is_active = 1
    ORDER BY price ASC;
    ```

    **Result (top 5 rows):**

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

### Problem 12

**Retrieve the name and price of the 10 cheapest active products.**

??? tip "Hint"
    Filter active products with `WHERE`, sort by price ascending with `ORDER BY`, then append `LIMIT 10`.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE is_active = 1
    ORDER BY price ASC
    LIMIT 10;
    ```

    **Result:**

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

### Problem 13

**Retrieve the name and price of active products priced over 2,000,000, sorted by price descending.**

??? tip "Hint"
    `AND` filters only rows that satisfy **both** conditions.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE is_active = 1 AND price > 2000000
    ORDER BY price DESC;
    ```

    **Result (top 5 rows):**

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

### Problem 14

**Retrieve the name, brand, and price of products where the brand is 'ASUS' or 'MSI'.**

??? tip "Hint"
    `OR` includes rows in the result if **either** condition is satisfied.

??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand = 'ASUS' OR brand = 'MSI';
    ```

    **Result (top 5 rows):**

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

### Problem 15

**Retrieve the name and price of products that have not been discontinued (`discontinued_at` is empty).**

??? tip "Hint"
    To find rows with empty (NULL) values, use `IS NULL` instead of `= NULL`.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE discontinued_at IS NULL;
    ```

    **Result (top 5 rows):**

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

### Problem 16

**Retrieve the name and price of products containing 'RTX' in their name, sorted by price descending.**

??? tip "Hint"
    Use `LIKE` for pattern matching and `ORDER BY` for sorting. Both clauses can be used together.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%RTX%'
    ORDER BY price DESC;
    ```

    **Result (top 5 rows):**

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

### Problem 17

**Retrieve the top 10 products priced between 1,000,000 and 3,000,000, sorted by stock quantity descending.**

??? tip "Hint"
    Specify a price range with `BETWEEN`, sort by stock descending with `ORDER BY stock_qty DESC`, and limit with `LIMIT 10`.

??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE price BETWEEN 1000000 AND 3000000
    ORDER BY stock_qty DESC
    LIMIT 10;
    ```

    **Result:**

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

### Problem 18

**Retrieve the name, category ID, and price of products in category IDs 1, 2, or 3.**

??? tip "Hint"
    `IN` works with numbers as well as strings. Filter with `category_id IN (1, 2, 3)`.

??? success "Answer"
    ```sql
    SELECT name, category_id, price
    FROM products
    WHERE category_id IN (1, 2, 3);
    ```

    **Result (top 5 rows):**

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

    > Category 1=Desktop PC, 2=Pre-built, 3=Custom-built PC.

---

### Problem 19

**Retrieve each product's name, selling price (`price`), cost price (`cost_price`), and margin (`price - cost_price`). Alias the margin column as `margin`.**

??? tip "Hint"
    You can perform arithmetic operations (`+`, `-`, `*`, `/`) in the `SELECT` clause. Use `AS alias` to name the column.

??? success "Answer"
    ```sql
    SELECT name, price, cost_price, price - cost_price AS margin
    FROM products;
    ```

    **Result (top 5 rows):**

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

    > Products with negative margin are sold below cost (negative margin).

---

### Problem 20

**Retrieve a list of unique brands registered in the products table.**

??? tip "Hint"
    Placing `DISTINCT` right after `SELECT` removes duplicate values.

??? success "Answer"
    ```sql
    SELECT DISTINCT brand
    FROM products
    ORDER BY brand;
    ```

    **Result (top 10 rows):**

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

## Practical (21~30)

Complex problems combining multiple concepts.

---

### Problem 21

**Retrieve the top 10 active products priced over 1,000,000, sorted by price descending. Display name and price.**

??? tip "Hint"
    Combine two conditions with `AND` in `WHERE`, then add `ORDER BY` and `LIMIT` in sequence.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE is_active = 1 AND price > 1000000
    ORDER BY price DESC
    LIMIT 10;
    ```

    **Result:**

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

### Problem 22

**Retrieve the name, brand, and price of products where the brand is 'ASUS' or 'MSI' and price exceeds 2,000,000, sorted by price descending.**

??? tip "Hint"
    Wrap `OR` conditions in **parentheses** for correct combination with `AND`. Use the form `(A OR B) AND C`.

??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE (brand = 'ASUS' OR brand = 'MSI') AND price > 2000000
    ORDER BY price DESC;
    ```

    **Result (top 5 rows):**

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

### Problem 23

**Retrieve the name and price of active products whose name does not contain 'white' (white), sorted by price descending.**

??? tip "Hint"
    `NOT LIKE` allows you to **exclude** specific patterns.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE name NOT LIKE '%화이트%' AND is_active = 1
    ORDER BY price DESC;
    ```

    **Result (top 5 rows):**

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

### Problem 24

**Retrieve the name and price of products priced 500,000-2,000,000 containing 'RTX' in their name, sorted by price descending.**

??? tip "Hint"
    Combine `BETWEEN` and `LIKE` with `AND`. All three conditions must be satisfied.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price BETWEEN 500000 AND 2000000
      AND name LIKE '%RTX%'
    ORDER BY price DESC;
    ```

    **Result:**

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

### Problem 25

**Calculate the margin (selling price - cost price) for each product and retrieve the top 5 by margin. Display name, selling price, cost price, and margin.**

??? tip "Hint"
    You can use aliases in `ORDER BY`. Write it like `ORDER BY margin DESC`.

??? success "Answer"
    ```sql
    SELECT name, price, cost_price, price - cost_price AS margin
    FROM products
    ORDER BY margin DESC
    LIMIT 5;
    ```

    **Result:**

    | name | price | cost_price | margin |
    | ---------- | ----------: | ----------: | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 | 4161000.0 | 3334200.0 |
    | MacBook Air 13 M4 | 4449200.0 | 2451900.0 | 1997300.0 |
    | Razer Blade 16 | 5518300.0 | 3703300.0 | 1815000.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 4881500.0 | 3168100.0 | 1713400.0 |
    | Razer Blade 18 화이트 | 4913500.0 | 3251900.0 | 1661600.0 |
    | ... | ... | ... | ... |

---

### Problem 26

**Retrieve the name, price, and discontinuation date of discontinued products (`discontinued_at` is not empty), top 5 by most recent discontinuation.**

??? tip "Hint"
    `IS NOT NULL` filters rows where the value is not empty. It's the opposite of `IS NULL`.

??? success "Answer"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL
    ORDER BY discontinued_at DESC
    LIMIT 5;
    ```

    **Result:**

    | name | price | discontinued_at |
    | ---------- | ----------: | ---------- |
    | 로지텍 G715 실버 | 100600.0 | 2025-12-27 19:50:12 |
    | 시소닉 FOCUS GM-750 실버 | 98900.0 | 2025-12-25 20:05:49 |
    | SteelSeries Arctis Nova 7 Wireless 실버 | 367300.0 | 2025-12-24 21:58:49 |
    | Dell Latitude 5540 실버 | 1113900.0 | 2025-12-17 22:47:10 |
    | 주연 리오나인 i9 하이엔드 실버 | 1663400.0 | 2025-12-15 15:04:20 |
    | ... | ... | ... |

---

### Problem 27

**Retrieve the name, price, and stock quantity of products with 0 stock that are still active (`is_active = 1`).**

??? tip "Hint"
    Combine `stock_qty = 0` and `is_active = 1` with `AND`. These are products that are out of stock but not yet deactivated.

??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE stock_qty = 0 AND is_active = 1;
    ```

    **Result:**

    | name | price | stock_qty |
    | ---------- | ----------: | ----------: |
    | Arctic Freezer 36 A-RGB 화이트 | 27400.0 | 0 |
    | 삼성 DDR4 16GB PC4-25600 | 73600.0 | 0 |
    | WD My Passport 2TB 블랙 | 329100.0 | 0 |
    | 삼성 DDR5 32GB PC5-38400 실버 | 158000.0 | 0 |

    > Currently only a few products match. In real online stores, out-of-stock product management is important.

---

### Problem 28

**Retrieve active products priced 500,000-2,000,000 with stock exceeding 20, sorted by price ascending. Display name, price, and stock quantity.**

??? tip "Hint"
    Connect multiple conditions with `AND`. Even with 3 or more conditions, just keep chaining `AND`.

??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE is_active = 1
      AND price BETWEEN 500000 AND 2000000
      AND stock_qty > 20
    ORDER BY price;
    ```

    **Result (top 5 rows):**

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

### Problem 29

**Retrieve the name, weight, and price of products weighing over 5,000g, sorted by weight descending.**

??? tip "Hint"
    Filter with `weight_grams > 5000` and sort with `ORDER BY weight_grams DESC`.

??? success "Answer"
    ```sql
    SELECT name, weight_grams, price
    FROM products
    WHERE weight_grams > 5000
    ORDER BY weight_grams DESC;
    ```

    **Result (top 5 rows):**

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

    > Products weighing 5kg or more are mostly desktop PCs.

---

### Problem 30

**Retrieve the top 10 active products with margin rate exceeding 30%, sorted by margin rate descending. Display name, selling price, cost price, and margin rate (%).**

??? tip "Hint"
    Margin rate (%) formula: `(price - cost_price) * 100.0 / price`. You can use this arithmetic expression directly in the `WHERE` clause as well. Use `ROUND()` to clean up decimal places.

??? success "Answer"
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

    **Result:**

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

    > Software products (Norton, Hancom Office) have low physical costs, resulting in high margin rates.
