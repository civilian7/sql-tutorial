# String and Math Functions

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `products` — Products (name, price, stock, brand)<br>
    `customers` — Customers (tier, points, signup channel)<br>
    `orders` — Orders (status, amount, date/time)<br>
    `order_items` — Order details (quantity, unit price)<br>
    `categories` — Categories (parent-child hierarchy)<br>
    `suppliers` — Suppliers (company name, contact)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

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

!!! info "Before You Begin"
    This exercise applies what you learned in **Intermediate Lessons 12~13** (string functions, math/utility functions) to practical scenarios.
    Transform and format data using SQLite string/math functions.

---

## Basic (1~7)

Practice basic string functions (LENGTH, UPPER, SUBSTR, REPLACE).

---

### Problem 1

**Find the character count of product names. Top 10 longest names.**

??? tip "Hint"
    Get string length with `LENGTH(name)`. `ORDER BY LENGTH(name) DESC LIMIT 10`.

??? success "Answer"
    ```sql
    SELECT
        name,
        LENGTH(name) AS name_length
    FROM products
    ORDER BY name_length DESC
    LIMIT 10;
    ```

    **Result (top 5 rows):**

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

    > Actual results depend on the data.

---

### Problem 2

**Convert all brand names to uppercase and list unique brands.**

??? tip "Hint"
    Convert to uppercase with `UPPER(brand)`, remove duplicates with `DISTINCT`.

??? success "Answer"
    ```sql
    SELECT DISTINCT UPPER(brand) AS brand_upper
    FROM products
    ORDER BY brand_upper;
    ```

    **Result (top 5 rows):**

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

    > With unified case, brands can be identified accurately.

---

### Problem 3

**Remove the brand portion from product names and extract only the remaining name.**

??? tip "Hint"
    Extract the string after brand name + space with `SUBSTR(name, LENGTH(brand) + 2)`.

??? success "Answer"
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

    **Result (top 5 rows):**

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

### Problem 4

**Extract only the ID portion before '@' from customer emails.**

??? tip "Hint"
    `SUBSTR(email, 1, INSTR(email, '@') - 1)` cuts to before '@'. `INSTR` returns the position of a specific character in a string.

??? success "Answer"
    ```sql
    SELECT
        email,
        SUBSTR(email, 1, INSTR(email, '@') - 1) AS user_id
    FROM customers
    ORDER BY user_id
    LIMIT 15;
    ```

    **Result (top 5 rows):**

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

    > Actual results depend on the data.

---

### Problem 5

**Remove color information ('블랙', '화이트', '실버') from product names.**

??? tip "Hint"
    Nest `REPLACE` to remove multiple strings. Clean up trailing spaces with `TRIM`.

??? success "Answer"
    ```sql
    SELECT
        name,
        TRIM(REPLACE(REPLACE(REPLACE(name, '블랙', ''), '화이트', ''), '실버', '')) AS name_no_color
    FROM products
    WHERE name LIKE '%블랙%' OR name LIKE '%화이트%' OR name LIKE '%실버%'
    ORDER BY name
    LIMIT 15;
    ```

    **Result (top 5 rows):**

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

### Problem 6

**Create phone numbers with hyphens (-) removed.**

??? tip "Hint"
    Replace hyphens with empty string using `REPLACE(phone, '-', '')`.

??? success "Answer"
    ```sql
    SELECT
        name,
        phone,
        REPLACE(phone, '-', '') AS phone_no_dash,
        LENGTH(REPLACE(phone, '-', '')) AS digit_count
    FROM customers
    LIMIT 10;
    ```

    **Result (top 5 rows):**

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

    > Actual results depend on the data.

---

### Problem 7

**Extract the category abbreviation (first 2 characters) from product SKU codes.**

??? tip "Hint"
    Extract the first 2 characters of SKU with `SUBSTR(sku, 1, 2)`. SKU format is like `LA-GEN-삼성-00001`.

??? success "Answer"
    ```sql
    SELECT
        sku,
        SUBSTR(sku, 1, 2) AS category_code,
        name
    FROM products
    ORDER BY category_code, sku
    LIMIT 15;
    ```

    **Result (top 5 rows):**

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

    > The first 2 characters of the SKU represent the category.

---

## Applied (8~14)

Practice GROUP_CONCAT, INSTR, NULLIF, CAST, ROUND.

---

### Problem 8

**List brands per category, separated by commas.**

??? tip "Hint"
    Combine unique brands within a category into a comma-separated string with `GROUP_CONCAT(DISTINCT brand, ', ')`.

??? success "Answer"
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

    **Result (top 3 rows):**

    | category | brand_count | brands |
    |----------|------------|--------|
    | 노트북 | 8 | ASUS, Dell, HP, LG, Lenovo, MSI, Razer, 삼성전자 |
    | 그래픽카드 | 5 | ASUS, EVGA, Gigabyte, MSI, ZOTAC |
    | 모니터 | 6 | ASUS, Dell, LG, MSI, 삼성전자, 벤큐 |

    > Actual results depend on the data.

---

### Problem 9

**Extract the model number after RTX from products containing 'RTX' in their name.**

??? tip "Hint"
    Find the position of 'RTX' with `INSTR(name, 'RTX')`, then extract the model number with `SUBSTR(name, INSTR(...) + 4, 4)`.

??? success "Answer"
    ```sql
    SELECT
        name,
        SUBSTR(name, INSTR(name, 'RTX') + 4, 4) AS rtx_model
    FROM products
    WHERE name LIKE '%RTX%'
    ORDER BY rtx_model DESC;
    ```

    **Result (top 5 rows):**

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

    > Actual results depend on the data.

---

### Problem 10

**Round order amounts to the nearest 10,000 won. Top 10 by amount.**

??? tip "Hint"
    `ROUND(total_amount, -4)` rounds to the nearest 10,000. Negative decimal places round the integer part.

??? success "Answer"
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

    **Result (top 5 rows):**

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

    > Actual values depend on the data.

---

### Problem 11

**Safely handle products with zero margin. Use NULLIF to prevent division by zero.**

??? tip "Hint"
    `NULLIF(cost_price, 0)` returns NULL if cost_price is 0. Dividing by NULL results in NULL, avoiding errors.

??? success "Answer"
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

    **Result (top 5 rows):**

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

    > Without `NULLIF`, division errors could occur on rows where cost_price=0.

---

### Problem 12

**Convert order amounts to text format ('1,234,567원').**

??? tip "Hint"
    Add thousands separators with `printf('%,d', total_amount)`. Append the unit with `||`.

??? success "Answer"
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

    **Result (top 5 rows):**

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

    > `printf` is a SQLite-specific function.

---

### Problem 13

**Classify product prices into range labels. Use IIF or CASE.**

??? tip "Hint"
    `IIF(condition, true, false)` is SQLite's simple conditional function. For multiple conditions, `CASE WHEN` is more suitable.

??? success "Answer"
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

    **Result (top 5 rows):**

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

### Problem 14

**Convert numbers stored as strings to integer/real. Type conversion of stock quantities.**

??? tip "Hint"
    Convert types with `CAST(value AS INTEGER)` or `CAST(value AS REAL)`. Check current type with `TYPEOF()`.

??? success "Answer"
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

    **Result (top 5 rows):**

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

    > `TYPEOF()` is a SQLite-specific function that checks the actual type of stored values.

---

## Practical (15~20)

Practice complex formatting, data transformation, and pattern matching.

---

### Problem 15

**Create a name list per customer grade. Only first 5 per grade, comma-separated.**

??? tip "Hint"
    Number within each grade with `ROW_NUMBER()` in a subquery, filter to 5, then combine with `GROUP_CONCAT`.

??? success "Answer"
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

    **Result:**

    | grade | total_count | sample_names |
    | ---------- | ----------: | ---------- |
    | VIP | 5 | 김상철, 문영숙, 김도현, 박정수, 오영숙 |
    | SILVER | 5 | 김정순, 김현준, 정중수, 유현지, 황하은 |
    | GOLD | 5 | 한민재, 서성민, 한은영, 임민재, 김지훈 |
    | BRONZE | 5 | 이주원, 장승현, 이승민, 박예진, 우서영 |

    > Shows the 5 oldest names from each grade. Actual names will differ.

---

### Problem 16

**Separate date and sequence number from order numbers. Format: ORD-YYYYMMDD-NNNNN.**

??? tip "Hint"
    Extract the date part (YYYYMMDD) with `SUBSTR(order_number, 5, 8)` and sequence number with `SUBSTR(order_number, 14)`.

??? success "Answer"
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

    **Result (top 5 rows):**

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

    > Actual sequence numbers depend on the data.

---

### Problem 17

**Find only products whose names contain capacity/size info (number+GB/TB/MHz/W).**

??? tip "Hint"
    `GLOB` is case-sensitive pattern matching. Find patterns with numbers followed by units like `*[0-9]GB*`, `*[0-9]TB*`.

??? success "Answer"
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

    **Result (top 5 rows):**

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

    > `GLOB` is SQLite-specific. Unlike `LIKE`, it is case-sensitive.

---

### Problem 18

**Product summary card: Format product info into a single-line string.**

??? tip "Hint"
    Combine `||` (string concatenation), `COALESCE`, and `printf` for formatting. Handle NULL values with `COALESCE`.

??? success "Answer"
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

    **Result:**

    | product_card |
    | ---------- |
    | [Razer] Razer Blade 14 블랙 | 7,495,200원 | 재고: 171개 | 무게: 1.827kg |
    | [Razer] Razer Blade 16 블랙 | 5,634,900원 | 재고: 461개 | 무게: 2.716kg |
    | [Razer] Razer Blade 16 | 5,518,300원 | 재고: 494개 | 무게: 2.89kg |
    | [Razer] Razer Blade 18 | 5,450,500원 | 재고: 297개 | 무게: 2.23kg |
    | [Razer] Razer Blade 14 | 5,339,100원 | 재고: 190개 | 무게: 2.341kg |
    | ... |

    > Actual results depend on the data. weight_grams가 NULL이면 '무게 미정'이 표시됩니다.

---

### Problem 19

**Email domain analysis by signup channel: Cross-tabulation of signup channel and email domain.**

??? tip "Hint"
    Extract domain with `SUBSTR(email, INSTR(email, '@') + 1)`. Handle NULL with `COALESCE(acquisition_channel, '미확인')`.

??? success "Answer"
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

    **Result (top 5 rows):**

    | channel | domain | customer_count |
    | ---------- | ---------- | ----------: |
    | search_ad | testmail.kr | 15289 |
    | social | testmail.kr | 14245 |
    | organic | testmail.kr | 11457 |
    | referral | testmail.kr | 7146 |
    | direct | testmail.kr | 4163 |
    | ... | ... | ... |

    > Since all emails use the testmail.kr domain, the meaningful insight is the customer count distribution by channel.

---

### Problem 20

**Comprehensive product report: Summarize price range, margin rate, stock status, and sales activity in one string.**

??? tip "Hint"
    Combine multiple functions (`CASE`, `ROUND`, `IIF`, `printf`, `COALESCE`, `||`) to generate a comprehensive report.

??? success "Answer"
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

    **Result (top 5 rows):**

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

    > Combines multiple functions to create a report showing product status at a glance.
