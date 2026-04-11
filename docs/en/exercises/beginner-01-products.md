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
    | 1 | 7 | 20 | (NULL) | Razer Blade 18 Black | LA-GAM-RAZ-00001 | Razer | RAZ-00001 | Razer Razer Blade 18 Black - High performance, latest technology | {"screen_size": "14 inch", "cpu": "Apple M3", "ram": "8GB", "storage": "256GB", "weight_kg": 1.7, "battery_hours": 6} | 2987500.0 | 3086700.0 | 107 | 2556 | 1 | (NULL) | 2016-11-20 02:59:21 | 2016-11-20 02:59:21 |
    | 2 | 28 | 27 | (NULL) | MSI GeForce RTX 4070 Ti Super GAMING X | GP-NVI-MSI-00002 | MSI | MSI-00002 | MSI MSI GeForce RTX 4070 Ti Super GAMING X - High performance, latest technology | {"vram": "12GB", "clock_mhz": 2447, "tdp_watts": 271} | 1744000.0 | 1360300.0 | 499 | 1632 | 1 | (NULL) | 2016-08-05 10:29:33 | 2016-08-05 10:29:33 |
    | 3 | 21 | 1 | (NULL) | Samsung DDR4 32GB PC4-25600 | RA-DDR-SAM-00003 | Samsung | 삼성전-00003 | Samsung Samsung DDR4 32GB PC4-25600 - High performance, latest technology | {"capacity_gb": 32, "speed_mhz": 5600, "type": "DDR5"} | 43500.0 | 37900.0 | 359 | 40 | 1 | (NULL) | 2016-12-25 00:50:46 | 2016-12-25 00:50:46 |
    | 4 | 11 | 31 | (NULL) | Dell U2724D | MO-GEN-DEL-00004 | Dell | DEL-00004 | Dell Dell U2724D - High performance, latest technology | {"screen_size": "27 inch", "resolution": "QHD", "refresh_rate": 144, "panel": "IPS"} | 894100.0 | 565700.0 | 337 | 4817 | 1 | (NULL) | 2016-03-27 09:13:57 | 2016-03-27 09:13:57 |
    | 5 | 22 | 48 | (NULL) | G.SKILL Trident Z5 DDR5 64GB 6000MHz White | RA-DDR-GSK-00005 | G.SKILL | G.S-00005 | G.SKILL G.SKILL Trident Z5 DDR5 64GB 6000MHz White - High performance, latest technology | {"capacity_gb": 32, "speed_mhz": 6400, "type": "DDR5"} | 167000.0 | 121400.0 | 59 | 60 | 1 | (NULL) | 2016-01-27 23:02:53 | 2016-01-27 23:02:53 |
    | 6 | 29 | 27 | (NULL) | MSI Radeon RX 9070 VENTUS 3X White | GP-AMD-MSI-00006 | MSI | MSI-00006 | MSI MSI Radeon RX 9070 VENTUS 3X White - High performance, latest technology | {"vram": "16GB", "clock_mhz": 1946, "tdp_watts": 411} | 383100.0 | 431800.0 | 460 | 1789 | 1 | (NULL) | 2016-08-19 16:26:49 | 2016-08-19 16:26:49 |
    | 7 | 22 | 1 | (NULL) | Samsung DDR5 32GB PC5-38400 | RA-DDR-SAM-00007 | Samsung | 삼성전-00007 | Samsung Samsung DDR5 32GB PC5-38400 - High performance, latest technology | {"capacity_gb": 64, "speed_mhz": 3200, "type": "DDR4"} | 211800.0 | 151900.0 | 340 | 46 | 1 | (NULL) | 2016-01-01 15:45:49 | 2016-01-01 15:45:49 |
    | 8 | 36 | 19 | (NULL) | Logitech G715 White | KE-MEC-LOG-00008 | Logitech | 로지텍-00008 | Logitech Logitech G715 White - High performance, latest technology | (NULL) | 131500.0 | 135700.0 | 341 | 1168 | 1 | (NULL) | 2016-02-18 09:35:31 | 2016-02-18 09:35:31 |
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
    | Razer Blade 18 Black | 2987500.0 | 107 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 | 499 |
    | Samsung DDR4 32GB PC4-25600 | 43500.0 | 359 |
    | Dell U2724D | 894100.0 | 337 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz White | 167000.0 | 59 |
    | MSI Radeon RX 9070 VENTUS 3X White | 383100.0 | 460 |
    | Samsung DDR5 32GB PC5-38400 | 211800.0 | 340 |
    | Logitech G715 White | 131500.0 | 341 |
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
    | ASUS ROG Strix G16CH White | 3671500.0 |
    | ASUS TUF Gaming RTX 5080 White | 4526600.0 |
    | ASUS ROG Strix Scar 16 Silver | 1598100.0 |
    | ASUS ExpertBook B5 [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 2041000.0 |
    | ASUS PCE-BE92BT | 47200.0 |
    | ASUS Dual RTX 4060 Ti Black | 2674800.0 |
    | ASUS Dual RX 9070 Silver | 1344800.0 |
    | ASUS PRIME Z890-A WIFI Silver | 727700.0 |
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
    | Razer Blade 18 Black | 2987500.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 |
    | LG All-in-One PC 27V70Q Silver | 1093200.0 |
    | Razer Blade 18 White | 2483600.0 |
    | ASUS ROG Strix G16CH White | 3671500.0 |
    | Hansung BossMonster DX5800 Black | 1129400.0 |
    | ASUS TUF Gaming RTX 5080 White | 4526600.0 |
    | HP Envy x360 15 Silver | 1214600.0 |
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
    | Sony WH-CH720N Silver | 445700.0 | 2023-09-21 01:03:38 |
    | WD Elements 2TB Black | 247100.0 | 2024-08-25 09:29:10 |
    | JBL Quantum ONE White | 239900.0 | 2023-06-01 06:11:13 |
    | Jooyon Rionine i7 System Silver | 810300.0 | 2023-05-08 03:08:52 |
    | ASUS TUF Gaming RTX 5080 White | 4526600.0 | 2017-05-15 20:10:25 |
    | Logitech G713 Silver | 151000.0 | 2021-05-03 13:07:12 |
    | Samsung DDR4 32GB PC4-25600 | 91000.0 | 2018-08-03 21:40:45 |
    | ASUS ROG Strix Scar 16 Silver | 1598100.0 | 2020-11-11 00:23:31 |
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
    | Dell U2724D | 894100.0 |
    | Netgear Nighthawk RS700S Black | 629300.0 |
    | Hansung BossMonster DX9900 Silver | 739900.0 |
    | Jooyon Rionine i7 System Silver | 810300.0 |
    | Samsung Odyssey G7 32 White | 537800.0 |
    | ASRock B850M Pro RS Silver | 665600.0 |
    | Netgear Orbi 970 Black | 762500.0 |
    | ASUS PRIME Z890-A WIFI Silver | 727700.0 |
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
    | MSI Radeon RX 9070 VENTUS 3X White | MSI | 383100.0 |
    | Logitech G715 White | Logitech | 131500.0 |
    | MSI MAG X870E TOMAHAWK WIFI White | MSI | 425400.0 |
    | ASUS ROG Strix G16CH White | ASUS | 3671500.0 |
    | Logitech K580 | Logitech | 67800.0 |
    | ASUS TUF Gaming RTX 5080 White | ASUS | 4526600.0 |
    | MSI Radeon RX 7900 XTX GAMING X White | MSI | 1517600.0 |
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
    | ASUS TUF Gaming RTX 5080 White | 4526600.0 |
    | MSI Radeon RX 7900 XTX GAMING X White | 1517600.0 |
    | APC Back-UPS Pro Gaming BGM1500B Black | 516300.0 |
    | MSI Radeon RX 9070 XT GAMING X | 1896000.0 |
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
    | MacBook Air 15 M3 Silver | 5481100.0 |
    | ASUS TUF Gaming RTX 5080 White | 4526600.0 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 4496700.0 |
    | Razer Blade 18 Black | 4353100.0 |
    | Razer Blade 16 Silver | 3702900.0 |
    | ASUS ROG Strix G16CH White | 3671500.0 |
    | ASUS ROG Zephyrus G16 | 3429900.0 |
    | ASUS ROG Strix GT35 | 3296800.0 |
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
    | MacBook Air 15 M3 Silver | 5481100.0 |
    | ASUS TUF Gaming RTX 5080 White | 4526600.0 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 4496700.0 |
    | Razer Blade 18 Black | 4353100.0 |
    | Razer Blade 16 Silver | 3702900.0 |
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
    | TP-Link TG-3468 Black | 18500.0 |
    | Samsung SPA-KFG0BUB Silver | 21900.0 |
    | Arctic Freezer 36 A-RGB White | 23000.0 |
    | Arctic Freezer 36 A-RGB White | 29900.0 |
    | TP-Link Archer TBE400E White | 30200.0 |
    | Samsung SPA-KFG0BUB | 30700.0 |
    | TP-Link TL-SG1016D Silver | 36100.0 |
    | Microsoft Bluetooth Keyboard White | 36800.0 |
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
    | TP-Link TG-3468 Black | 18500.0 |
    | Samsung SPA-KFG0BUB Silver | 21900.0 |
    | Arctic Freezer 36 A-RGB White | 23000.0 |
    | Arctic Freezer 36 A-RGB White | 29900.0 |
    | TP-Link Archer TBE400E White | 30200.0 |
    | Samsung SPA-KFG0BUB | 30700.0 |
    | TP-Link TL-SG1016D Silver | 36100.0 |
    | Microsoft Bluetooth Keyboard White | 36800.0 |
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
    | MacBook Air 15 M3 Silver | 5481100.0 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 4496700.0 |
    | Razer Blade 18 Black | 4353100.0 |
    | Razer Blade 16 Silver | 3702900.0 |
    | ASUS ROG Strix G16CH White | 3671500.0 |
    | ASUS ROG Strix GT35 | 3296800.0 |
    | Razer Blade 18 Black | 2987500.0 |
    | ASUS Dual RTX 4060 Ti Black | 2674800.0 |
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
    | MSI Radeon RX 9070 VENTUS 3X White | MSI | 383100.0 |
    | MSI MAG X870E TOMAHAWK WIFI White | MSI | 425400.0 |
    | ASUS ROG Strix G16CH White | ASUS | 3671500.0 |
    | ASUS TUF Gaming RTX 5080 White | ASUS | 4526600.0 |
    | MSI Radeon RX 7900 XTX GAMING X White | MSI | 1517600.0 |
    | ASUS ROG Strix Scar 16 Silver | ASUS | 1598100.0 |
    | ASUS ExpertBook B5 [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | ASUS | 2041000.0 |
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
    | Razer Blade 18 Black | 2987500.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 |
    | Samsung DDR4 32GB PC4-25600 | 43500.0 |
    | Dell U2724D | 894100.0 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz White | 167000.0 |
    | MSI Radeon RX 9070 VENTUS 3X White | 383100.0 |
    | Samsung DDR5 32GB PC5-38400 | 211800.0 |
    | Logitech G715 White | 131500.0 |
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
    | ASUS TUF Gaming RTX 5080 White | 4526600.0 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 4496700.0 |
    | ASUS Dual RTX 4060 Ti Black | 2674800.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 |
    | Gigabyte RTX 4090 AERO OC White | 1280900.0 |
    | Gigabyte RTX 5090 AERO OC | 1136100.0 |
    | ASUS Dual RTX 5070 Ti Silver | 986400.0 |
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
    | Epson L15160 | 1019500.0 | 493 |
    | SAPPHIRE PULSE RX 7800 XT Silver | 1146300.0 | 490 |
    | LG Gram 14 | 1734000.0 | 490 |
    | MSI Radeon RX 9070 XT GAMING X | 1896000.0 | 482 |
    | HP Slim Desktop S01 White | 1708400.0 | 481 |
    | Razer Blade 18 | 1806800.0 | 460 |
    | ASUS Dual RX 9070 Silver | 1344800.0 | 454 |
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
    | LG All-in-One PC 27V70Q Silver | 2 | 1093200.0 |
    | HP Slim Desktop S01 White | 2 | 1708400.0 |
    | Dell XPS Desktop 8960 Silver | 2 | 1249400.0 |
    | HP Z2 Mini G1a Black | 2 | 895000.0 |
    | Samsung DM500TDA Silver | 2 | 822100.0 |
    | Hansung BossMonster DX9900 Silver | 3 | 739900.0 |
    | ASUS ROG Strix G16CH White | 3 | 3671500.0 |
    | Jooyon Rionine i7 System Silver | 3 | 810300.0 |
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
    | Razer Blade 18 Black | 2987500.0 | 3086700.0 | -99200.0 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 | 1360300.0 | 383700.0 |
    | Samsung DDR4 32GB PC4-25600 | 43500.0 | 37900.0 | 5600.0 |
    | Dell U2724D | 894100.0 | 565700.0 | 328400.0 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz White | 167000.0 | 121400.0 | 45600.0 |
    | MSI Radeon RX 9070 VENTUS 3X White | 383100.0 | 431800.0 | -48700.0 |
    | Samsung DDR5 32GB PC5-38400 | 211800.0 | 151900.0 | 59900.0 |
    | Logitech G715 White | 131500.0 | 135700.0 | -4200.0 |
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
    | AhnLab |
    | Apple |
    | Arctic |
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
    | MacBook Air 15 M3 Silver | 5481100.0 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 4496700.0 |
    | Razer Blade 18 Black | 4353100.0 |
    | Razer Blade 16 Silver | 3702900.0 |
    | ASUS ROG Strix G16CH White | 3671500.0 |
    | ASUS ROG Strix GT35 | 3296800.0 |
    | Razer Blade 18 Black | 2987500.0 |
    | ASUS Dual RTX 4060 Ti Black | 2674800.0 |
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
    | ASUS TUF Gaming RTX 5080 White | ASUS | 4526600.0 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | ASUS | 4496700.0 |
    | ASUS ROG Strix G16CH White | ASUS | 3671500.0 |
    | ASUS ROG Zephyrus G16 | ASUS | 3429900.0 |
    | ASUS ROG Strix GT35 | ASUS | 3296800.0 |
    | ASUS Dual RTX 4060 Ti Black | ASUS | 2674800.0 |
    | ASUS ROG Strix Scar 16 | ASUS | 2452500.0 |
    | ASUS ExpertBook B5 [Special Limited Edition] RGB lighting equipped, software customization supported | ASUS | 2121600.0 |
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
    | MacBook Air 15 M3 Silver | 5481100.0 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 4496700.0 |
    | Razer Blade 18 Black | 4353100.0 |
    | Razer Blade 16 Silver | 3702900.0 |
    | ASUS ROG Strix G16CH White | 3671500.0 |
    | ASUS ROG Strix GT35 | 3296800.0 |
    | Razer Blade 18 Black | 2987500.0 |
    | ASUS Dual RTX 4060 Ti Black | 2674800.0 |
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
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 |
    | Gigabyte RTX 4090 AERO OC White | 1280900.0 |
    | Gigabyte RTX 5090 AERO OC | 1136100.0 |
    | ASUS Dual RTX 5070 Ti Silver | 986400.0 |

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
    | MacBook Air 15 M3 Silver | 5481100.0 | 3205400.0 | 2275700.0 |
    | ASUS TUF Gaming RTX 5080 White | 4526600.0 | 3037100.0 | 1489500.0 |
    | Razer Blade 18 Black | 4353100.0 | 3047200.0 | 1305900.0 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 4496700.0 | 3296400.0 | 1200300.0 |
    | ASUS ROG Strix G16CH White | 3671500.0 | 2480900.0 | 1190600.0 |
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
    | Dell XPS Desktop 8960 Silver | 1249400.0 | 2025-11-20 15:30:12 |
    | Kingston FURY Beast DDR4 16GB White | 91200.0 | 2025-11-18 04:06:13 |
    | Intel Core Ultra 7 265K | 196300.0 | 2025-11-16 21:11:33 |
    | Hansung BossMonster DX7700 White | 1579400.0 | 2025-10-25 03:47:01 |
    | Intel Core Ultra 7 265K White | 170200.0 | 2025-08-24 00:34:53 |
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
    | Arctic Freezer 36 A-RGB White | 23000.0 | 0 |

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
    | CyberPower BRG1500AVRLCD Silver | 508100.0 | 230 |
    | APC Back-UPS Pro Gaming BGM1500B Black | 516300.0 | 393 |
    | Philips 27E1N5300AE White | 518700.0 | 397 |
    | Gigabyte Z790 AORUS MASTER | 520400.0 | 339 |
    | Samsung Odyssey G7 32 White | 537800.0 | 425 |
    | WD Gold 12TB | 541900.0 | 430 |
    | ASRock X870E Taichi Silver | 543100.0 | 411 |
    | Gigabyte X870 AORUS ELITE AX Silver | 545100.0 | 48 |
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
    | ASUS ROG Strix GT35 | 19449 | 3296800.0 |
    | Hansung BossMonster DX7700 White | 19250 | 1579400.0 |
    | ASUS ROG Strix G16CH White | 16624 | 3671500.0 |
    | Hansung BossMonster DX9900 Silver | 14892 | 739900.0 |
    | ASUS ROG Strix G16CH Silver | 14308 | 1879100.0 |
    | CyberPower OR1500LCDRT2U Black | 14045 | 252900.0 |
    | Jooyon Rionine Mini PC | 13062 | 1194000.0 |
    | LG All-in-One PC 27V70Q Silver | 12700 | 1093200.0 |
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
    | Norton AntiVirus Plus Silver | 74800.0 | 32400.0 | 56.7 |
    | Windows 11 Pro Silver | 423000.0 | 198800.0 | 53.0 |
    | Hancom Office 2024 Enterprise Silver | 241400.0 | 116400.0 | 51.8 |
    | Logitech G502 HERO Silver | 71100.0 | 36500.0 | 48.7 |
    | V3 Endpoint Security Black | 46500.0 | 24200.0 | 48.0 |
    | Microsoft 365 Personal | 108200.0 | 57900.0 | 46.5 |
    | TP-Link Archer TBE400E White | 30200.0 | 16300.0 | 46.0 |
    | WD Gold 12TB | 541900.0 | 292600.0 | 46.0 |
    | ... | ... | ... | ... |

    > Software products (Norton, Hancom Office) have low physical costs, resulting in high margin rates.
