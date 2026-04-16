# String and Math Functions

!!! info "Tables"
    `products` — Products (name, price, stock, brand)  
    `customers` — Customers (grade, points, channel)  
    `orders` — Orders (status, amount, date)  
    `order_items` — Order items (qty, unit price)  
    `categories` — Categories (parent-child hierarchy)  
    `suppliers` — Suppliers (company, contact)  

!!! abstract "Concepts"
    `SUBSTR`, `LENGTH`, `UPPER`/`LOWER`, `REPLACE`, `TRIM`, `INSTR`, `GROUP_CONCAT`, `COALESCE`, `ROUND`, `ABS`, `CAST`, `NULLIF`, `IIF`/`CASE`, `printf`

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
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 113 |
    | HP EliteBook 840 G10 Black [Special Limited Edition] Extended 3-year warranty + exclusive carrying case included | 112 |
    | ASUS ExpertBook B5 [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 110 |
    | ASUS ExpertBook B5 [Special Limited Edition] RGB lighting equipped, software customization supported | 100 |
    | TeamGroup T-Force Delta RGB DDR5 32GB 6000MHz Silver | 52 |
    | CORSAIR Dominator Titanium DDR5 32GB 7200MHz Silver | 51 |
    | Arctic Liquid Freezer III Pro 420 A-RGB Silver | 46 |
    | Kingston FURY Renegade DDR5 32GB 7200MHz Black | 46 |
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
    | AHNLAB |
    | AMD |
    | APC |
    | APPLE |
    | ARCTIC |
    | ASROCK |
    | ASUS |
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
    | AMD | AMD Ryzen 9 9900X | Ryzen 9 9900X |
    | AMD | AMD Ryzen 9 9900X | Ryzen 9 9900X |
    | APC | APC Back-UPS Pro Gaming BGM1500B Black | Back-UPS Pro Gaming BGM1500B Black |
    | ASRock | ASRock B850M Pro RS Black | B850M Pro RS Black |
    | ASRock | ASRock B850M Pro RS Silver | B850M Pro RS Silver |
    | ASRock | ASRock B850M Pro RS White | B850M Pro RS White |
    | ASRock | ASRock B860M Pro RS Silver | B860M Pro RS Silver |
    | ASRock | ASRock B860M Pro RS White | B860M Pro RS White |
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
    | user1001@testmail.kr | user1001 |
    | user1002@testmail.kr | user1002 |
    | user1003@testmail.kr | user1003 |
    | user1004@testmail.kr | user1004 |
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
    | Joshua Atkins | 555-4964-6200 | 55549646200 | 11 |
    | Danny Johnson | 555-4423-5167 | 55544235167 | 11 |
    | Adam Moore | 555-0806-0711 | 55508060711 | 11 |
    | Virginia Steele | 555-9666-8856 | 55596668856 | 11 |
    | Jared Vazquez | 555-0239-9503 | 55502399503 | 11 |
    | Benjamin Skinner | 555-0786-7765 | 55507867765 | 11 |
    | Ashley Jones | 555-4487-2922 | 55544872922 | 11 |
    | Tyler Rodriguez | 555-8951-7989 | 55589517989 | 11 |
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
    | AU-BOS-00256 | AU | Bose SoundLink Flex Black |
    | AU-JBL-00019 | AU | JBL Quantum ONE White |
    | AU-JBL-00055 | AU | JBL Flip 6 White |
    | AU-JBL-00070 | AU | JBL Pebbles 2 Black |
    | AU-JBL-00096 | AU | JBL Flip 6 Black |
    | AU-RAZ-00253 | AU | Razer Kraken V4 Black |
    | AU-SNY-00009 | AU | Sony WH-CH720N Silver |
    | AU-STE-00122 | AU | SteelSeries Arctis Nova Pro Wireless White |
    | ... | ... | ... |

    > The first 2 characters of the SKU represent the category.

---

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
    | Gigabyte RTX 5090 AERO OC | 5090 |
    | ASUS TUF Gaming RTX 5080 White | 5080 |
    | ASUS Dual RTX 5070 Ti Silver | 5070 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 5070 |
    | Gigabyte RTX 4090 AERO OC White | 4090 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 4070 |
    | ASUS Dual RTX 4060 Ti Black | 4060 |
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
    | ORD-20201121-08810 | 50867500.0 | 50867500.0 | 5086.75 |
    | ORD-20250305-32265 | 46820024.0 | 46820024.0 | 4682.0024 |
    | ORD-20200209-05404 | 43677500.0 | 43677500.0 | 4367.75 |
    | ORD-20251218-37240 | 38626400.0 | 38626400.0 | 3862.64 |
    | ORD-20220106-15263 | 37987600.0 | 37987600.0 | 3798.76 |
    | ORD-20200820-07684 | 37518200.0 | 37518200.0 | 3751.82 |
    | ORD-20220224-15869 | 35397700.0 | 35397700.0 | 3539.77 |
    | ORD-20220509-16861 | 33823800.0 | 33823800.0 | 3382.38 |
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
    | Norton AntiVirus Plus Silver | 74800.0 | 32400.0 | 130.9 |
    | Windows 11 Pro Silver | 423000.0 | 198800.0 | 112.8 |
    | Hancom Office 2024 Enterprise Silver | 241400.0 | 116400.0 | 107.4 |
    | Logitech G502 HERO Silver | 71100.0 | 36500.0 | 94.8 |
    | V3 Endpoint Security Black | 46500.0 | 24200.0 | 92.1 |
    | Microsoft 365 Personal | 108200.0 | 57900.0 | 86.9 |
    | TP-Link Archer TBE400E White | 30200.0 | 16300.0 | 85.3 |
    | WD Gold 12TB | 541900.0 | 292600.0 | 85.2 |
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
    | ORD-20201121-08810 | 50867500.0 | 50,867,500원 |
    | ORD-20250305-32265 | 46820024.0 | 46,820,024원 |
    | ORD-20200209-05404 | 43677500.0 | 43,677,500원 |
    | ORD-20251218-37240 | 38626400.0 | 38,626,400원 |
    | ORD-20220106-15263 | 37987600.0 | 37,987,600원 |
    | ORD-20200820-07684 | 37518200.0 | 37,518,200원 |
    | ORD-20220224-15869 | 35397700.0 | 35,397,700원 |
    | ORD-20220509-16861 | 33823800.0 | 33,823,800원 |
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
    | MacBook Air 15 M3 Silver | 5481100.0 | 200만원 이상 | 고가 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 4496700.0 | 200만원 이상 | 고가 |
    | Razer Blade 18 Black | 4353100.0 | 200만원 이상 | 고가 |
    | Razer Blade 16 Silver | 3702900.0 | 200만원 이상 | 고가 |
    | ASUS ROG Strix G16CH White | 3671500.0 | 200만원 이상 | 고가 |
    | ASUS ROG Strix GT35 | 3296800.0 | 200만원 이상 | 고가 |
    | Razer Blade 18 Black | 2987500.0 | 200만원 이상 | 고가 |
    | ASUS Dual RTX 4060 Ti Black | 2674800.0 | 200만원 이상 | 고가 |
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
    | Arctic Liquid Freezer III 240 | 500 | integer | 500.0 | real | 98600 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 499 | integer | 499.0 | real | 1744000 |
    | Seasonic VERTEX GX-1200 Black | 498 | integer | 498.0 | real | 369800 |
    | ASRock B850M Pro RS Silver | 496 | integer | 496.0 | real | 665600 |
    | TP-Link Archer TX55E Black | 495 | integer | 495.0 | real | 64000 |
    | Epson L15160 | 493 | integer | 493.0 | real | 1019500 |
    | Samsung Odyssey G7 32 | 491 | integer | 491.0 | real | 355500 |
    | LG Gram 14 | 490 | integer | 490.0 | real | 1734000 |
    | ... | ... | ... | ... | ... | ... |

    > `TYPEOF()` is a SQLite-specific function that checks the actual type of stored values.

---

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
    | VIP | 5 | Gabriel Walters, Adam Moore, Terri Jones, Jason Rivera, Corey Carroll |
    | SILVER | 5 | Sara Williams, Jared Vazquez, Christopher Green, Leah Moore, Lynn Shelton |
    | GOLD | 5 | Joseph Sellers, Joseph Lewis, Richard Barker, Diana Ferguson, Nancy Smith |
    | BRONZE | 5 | Mary Jackson, Lydia Lawrence, Ashley Hogan, Michael Hutchinson, Victoria Patel |

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
    | ORD-20251231-37555 | 20251231 | 2025-12-31 | 37555 |
    | ORD-20251231-37543 | 20251231 | 2025-12-31 | 37543 |
    | ORD-20251231-37552 | 20251231 | 2025-12-31 | 37552 |
    | ORD-20251231-37548 | 20251231 | 2025-12-31 | 37548 |
    | ORD-20251231-37542 | 20251231 | 2025-12-31 | 37542 |
    | ORD-20251231-37546 | 20251231 | 2025-12-31 | 37546 |
    | ORD-20251231-37547 | 20251231 | 2025-12-31 | 37547 |
    | ORD-20251231-37556 | 20251231 | 2025-12-31 | 37556 |
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
    | Seagate IronWolf 4TB Black | 545400.0 | Seagate |
    | WD Gold 12TB | 541900.0 | WD |
    | be quiet! Straight Power 12 1000W Black | 331100.0 | be quiet! |
    | Seagate Exos 16TB Silver | 303300.0 | Seagate |
    | be quiet! Dark Power 13 1000W | 293000.0 | be quiet! |
    | Kingston FURY Renegade DDR5 32GB 7200MHz Black | 282300.0 | Kingston |
    | Kingston FURY Renegade DDR5 32GB 7200MHz Black | 276900.0 | Kingston |
    | SK hynix Platinum P41 1TB | 269200.0 | SK hynix |
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
    | [Apple] MacBook Air 15 M3 Silver | 5,481,100원 | 재고: 346개 | 무게: 2.087kg |
    | [ASUS] ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 4,496,700원 | 재고: 434개 | 무게: 1.277kg |
    | [Razer] Razer Blade 18 Black | 4,353,100원 | 재고: 287개 | 무게: 2.443kg |
    | [Razer] Razer Blade 16 Silver | 3,702,900원 | 재고: 323개 | 무게: 2.986kg |
    | [ASUS] ASUS ROG Strix G16CH White | 3,671,500원 | 재고: 201개 | 무게: 16.624kg |
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
    | search_ad | testmail.kr | 1543 |
    | social | testmail.kr | 1425 |
    | organic | testmail.kr | 1146 |
    | referral | testmail.kr | 708 |
    | direct | testmail.kr | 408 |
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
    | MacBook Air 15 M3 Silver | 고가 | 71.0% | 충분 | 판매중 | 5,481,100원 |
    | ASUS TUF Gaming RTX 5080 White | 고가 | 49.0% | 충분 | 단종 | 4,526,600원 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 고가 | 36.4% | 충분 | 판매중 | 4,496,700원 |
    | Razer Blade 18 Black | 고가 | 42.9% | 충분 | 판매중 | 4,353,100원 |
    | Razer Blade 16 Silver | 고가 | 28.3% | 충분 | 판매중 | 3,702,900원 |
    | ASUS ROG Strix G16CH White | 고가 | 48.0% | 충분 | 판매중 | 3,671,500원 |
    | ASUS ROG Zephyrus G16 | 고가 | 11.2% | 충분 | 단종 | 3,429,900원 |
    | ASUS ROG Strix GT35 | 고가 | 1.9% | 충분 | 판매중 | 3,296,800원 |
    | ... | ... | ... | ... | ... | ... |

    > Combines multiple functions to create a report showing product status at a glance.
