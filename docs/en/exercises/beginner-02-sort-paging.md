# Sorting and Paging

!!! info "Tables"
    `products` — Products (name, price, stock, brand)  
    `customers` — Customers (grade, points, channel)  
    `orders` — Orders (status, amount, date)  
    `reviews` — Reviews (rating, content)  
    `payments` — Payments (method, amount, status)  

!!! abstract "Concepts"
    `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `OFFSET`, `DISTINCT`, Aliases (`AS`), arithmetic operations

Practice one concept at a time.

---

### Problem 1

**Sort the products in order of highest price and look up the name (`name`) and price (`price`).**

??? tip "Hint"
    Using `ORDER BY price DESC` sorts in descending order.

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

### Problem 2

**Sort products in descending order of price and search for name, brand (`brand`), and price.**

??? tip "Hint"
    Just using `ORDER BY price ASC` or `ORDER BY price` will result in ascending order (default).

??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    ORDER BY price ASC;
    ```

    **Result (top 5 rows):**

    | name | brand | price |
    | ---------- | ---------- | ----------: |
    | TP-Link TG-3468 Black | TP-Link | 18500.0 |
    | Samsung SPA-KFG0BUB Silver | Samsung | 21900.0 |
    | Arctic Freezer 36 A-RGB White | Arctic | 23000.0 |
    | Arctic Freezer 36 A-RGB White | Arctic | 29900.0 |
    | TP-Link Archer TBE400E White | TP-Link | 30200.0 |
    | Samsung SPA-KFG0BUB | Samsung | 30700.0 |
    | Logitech MK470 Black | Logitech | 31800.0 |
    | Logitech MX Anywhere 3S Black | Logitech | 33600.0 |
    | ... | ... | ... |

---

### Problem 3

**View the names and prices of the 5 most expensive products.**

??? tip "Hint"
    Sort by `ORDER BY` and then get only the top N by `LIMIT`.

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

### Problem 4

**View the name, price, and inventory quantity of the five products with the lowest inventory quantity (`stock_qty`).**

??? tip "Hint"
    If you sort by `ORDER BY stock_qty ASC` in ascending order, the inventory is low.

??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    ORDER BY stock_qty ASC
    LIMIT 5;
    ```

    **Result:**

    | name | price | stock_qty |
    | ---------- | ----------: | ----------: |
    | Arctic Freezer 36 A-RGB White | 23000.0 | 0 |
    | Samsung SPA-KFG0BUB | 30700.0 | 4 |
    | Samsung DDR4 32GB PC4-25600 | 91000.0 | 6 |
    | Norton AntiVirus Plus | 69700.0 | 8 |
    | Logitech G502 HERO Silver | 71100.0 | 8 |
    | ... | ... | ... |

---

### Problem 5

**Sort customers in order of sign-up date (`created_at`) to view the names, emails, ratings (`grade`), and sign-up dates of the five customers who signed up first.**

??? tip "Hint"
    Use `ORDER BY created_at ASC` to list the oldest subscription date first.

??? success "Answer"
    ```sql
    SELECT name, email, grade, created_at
    FROM customers
    ORDER BY created_at ASC
    LIMIT 5;
    ```

    **Result:**

    | name | email | grade | created_at |
    | ---------- | ---------- | ---------- | ---------- |
    | Alan Blair | user84@testmail.kr | BRONZE | 2016-01-03 19:49:46 |
    | Mary Jackson | user61@testmail.kr | BRONZE | 2016-01-04 14:11:21 |
    | Joseph Sellers | user90@testmail.kr | GOLD | 2016-01-05 22:02:29 |
    | Gabriel Walters | user98@testmail.kr | VIP | 2016-01-09 06:08:34 |
    | Lydia Lawrence | user15@testmail.kr | BRONZE | 2016-01-14 06:39:08 |
    | ... | ... | ... | ... |

---

### Problem 6

**Sort product names in alphabetical/alphabetical order to view the first 5 items.**

??? tip "Hint"
    When sorted by `ORDER BY name`, the English alphabet comes before the Korean alphabet.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY name
    LIMIT 5;
    ```

    **Result:**

    | name | price |
    | ---------- | ----------: |
    | AMD Ryzen 9 9900X | 335700.0 |
    | AMD Ryzen 9 9900X | 591800.0 |
    | APC Back-UPS Pro Gaming BGM1500B Black | 516300.0 |
    | ASRock B850M Pro RS Black | 201000.0 |
    | ASRock B850M Pro RS Silver | 665600.0 |
    | ... | ... |

---

### Problem 7

**View the top 6-10 most expensive products** (i.e. skip the top 5 and go to the next 5)

??? tip "Hint"
    `OFFSET` skips the specified number of rows. Fetch from the 6th with `LIMIT 5 OFFSET 5`.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5 OFFSET 5;
    ```

    **Result:**

    | name | price |
    | ---------- | ----------: |
    | ASUS ROG Strix G16CH White | 3671500.0 |
    | ASUS ROG Zephyrus G16 | 3429900.0 |
    | ASUS ROG Strix GT35 | 3296800.0 |
    | Razer Blade 18 Black | 2987500.0 |
    | ASUS Dual RTX 4060 Ti Black | 2674800.0 |
    | ... | ... |

---

### Problem 8

**View the names, levels, and points of the 5 customers with the most points (`point_balance`).**

??? tip "Hint"
    Sort in descending order with `ORDER BY point_balance DESC` and then apply `LIMIT 5`.

??? success "Answer"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    ORDER BY point_balance DESC
    LIMIT 5;
    ```

    **Result:**

    | name | grade | point_balance |
    | ---------- | ---------- | ----------: |
    | Allen Snyder | VIP | 3955828 |
    | Jason Rivera | VIP | 3518880 |
    | Brenda Garcia | VIP | 2450166 |
    | Courtney Huff | VIP | 2383491 |
    | James Banks | VIP | 2297542 |
    | ... | ... | ... |

---

### Problem 9

**Look up the order number (`order_number`), order amount, and order date (`ordered_at`) of the five orders with the largest order amount (`total_amount`).**

??? tip "Hint"
    Use `ORDER BY total_amount DESC LIMIT 5` in table `orders`.

??? success "Answer"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 5;
    ```

    **Result:**

    | order_number | total_amount | ordered_at |
    | ---------- | ----------: | ---------- |
    | ORD-20201121-08810 | 50867500.0 | 2020-11-21 12:04:42 |
    | ORD-20250305-32265 | 46820024.0 | 2025-03-05 09:01:08 |
    | ORD-20230523-22331 | 46094971.0 | 2023-05-23 08:50:55 |
    | ORD-20200209-05404 | 43677500.0 | 2020-02-09 23:36:36 |
    | ORD-20221231-20394 | 43585700.0 | 2022-12-31 21:35:59 |
    | ... | ... | ... |

---

### Problem 10

**View the list of brands registered in the product table in alphabetical order without duplication.**

??? tip "Hint"
    Remove duplicates with `SELECT DISTINCT brand` and sort with `ORDER BY brand`.

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

Practice combining multiple concepts.

---

### Problem 11

** Sort products with a price of 1 million won or more in descending order of price and search for name, brand, and price. Prints only the top 5.**

??? tip "Hint"
    Filter by `WHERE price >= 1000000` and then apply `ORDER BY price DESC LIMIT 5`.

??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price >= 1000000
    ORDER BY price DESC
    LIMIT 5;
    ```

    **Result:**

    | name | brand | price |
    | ---------- | ---------- | ----------: |
    | MacBook Air 15 M3 Silver | Apple | 5481100.0 |
    | ASUS TUF Gaming RTX 5080 White | ASUS | 4526600.0 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | ASUS | 4496700.0 |
    | Razer Blade 18 Black | Razer | 4353100.0 |
    | Razer Blade 16 Silver | Razer | 3702900.0 |
    | ... | ... | ... |

---

### Problem 12

** Sort Samsung Electronics or LG Electronics brand products in descending price order to search for name, brand, and price. Prints only the top 5.**

??? tip "Hint"
    Filter the two brands by `WHERE brand IN ('삼성전자', 'LG전자')`.

??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand IN ('삼성전자', 'LG전자')
    ORDER BY price DESC
    LIMIT 5;
    ```

    **Result:**

    | name | brand | price |
    | ---------- | ---------- | ----------: |
    | LG 그램 17 블랙 | LG전자 | 3053700.0 |
    | LG 데스크톱 B80GV 블랙 | LG전자 | 2887600.0 |
    | LG 그램 14 화이트 | LG전자 | 2816400.0 |
    | LG 그램 프로 16 화이트 | LG전자 | 2797000.0 |
    | 삼성 올인원 DM530ABE 화이트 | 삼성전자 | 2743700.0 |
    | ... | ... | ... |

---

### Problem 13

** Among VIP level customers, sort the customers with the last name 'Kim' in order of the highest amount of points and view the names, levels, and points of only 5 people.**

??? tip "Hint"
    Apply both conditions simultaneously with `WHERE grade = 'VIP' AND name LIKE '김%'`.

??? success "Answer"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    WHERE grade = 'VIP'
      AND name LIKE '김%'
    ORDER BY point_balance DESC
    LIMIT 5;
    ```

    **Result:**

    | name | grade | point_balance |
    | ---------- | ---------- | ----------: |
    | 김상철 | VIP | 5406032 |
    | 김병철 | VIP | 4138149 |
    | 김성민 | VIP | 3710320 |
    | 김상현 | VIP | 3298043 |
    | 김경희 | VIP | 3155254 |
    | ... | ... | ... |

---

### Problem 14

**Sort discontinued products (products where `discontinued_at` is not NULL) in the most recent order based on the discontinuation date to view only 5 names, prices, and discontinuation dates.**

??? tip "Hint"
    Filter only discontinued products with `WHERE discontinued_at IS NOT NULL`.

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

### Problem 15

**Sort reviews with a review rating (`rating`) of 1 in the most recent order and view the 5 titles (`title`), rating, and creation date (`created_at`).**

??? tip "Hint"
    In table `reviews`, filter by `WHERE rating = 1` and sort by `ORDER BY created_at DESC`.

??? success "Answer"
    ```sql
    SELECT title, rating, created_at
    FROM reviews
    WHERE rating = 1
    ORDER BY created_at DESC
    LIMIT 5;
    ```

    **Result:**

    | title | rating | created_at |
    | ---------- | ----------: | ---------- |
    | (NULL) | 1 | 2026-01-05 20:37:52 |
    | (NULL) | 1 | 2025-12-21 21:52:59 |
    | Never Again | 1 | 2025-12-20 11:53:58 |
    | (NULL) | 1 | 2025-12-19 08:58:30 |
    | Defective | 1 | 2025-12-14 10:07:24 |
    | ... | ... | ... |

---

### Problem 16

**Sort products priced between 500,000 won and 1 million won or less in ascending order of price and search for 5 names, brands, and prices.**

??? tip "Hint"
    Specify the range with `WHERE price BETWEEN 500000 AND 1000000`.

??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price BETWEEN 500000 AND 1000000
    ORDER BY price ASC
    LIMIT 5;
    ```

    **Result:**

    | name | brand | price |
    | ---------- | ---------- | ----------: |
    | CyberPower BRG1500AVRLCD Silver | CyberPower | 508100.0 |
    | APC Back-UPS Pro Gaming BGM1500B Black | APC | 516300.0 |
    | Philips 27E1N5300AE White | Philips | 518700.0 |
    | Gigabyte Z790 AORUS MASTER | Gigabyte | 520400.0 |
    | Epson L3260 | Epson | 525400.0 |
    | ... | ... | ... |

---

### Problem 17

** Among card payments (`method = 'card'`), search for 5 cases where the number of installment months (`installment_months`) is greater than 0 by sorting them in descending order of the number of installment months and descending order of payment amount (`amount`). Prints order ID, payment amount, card company (`card_issuer`), and number of installment months.**

??? tip "Hint"
    Multiple sorting occurs if you separate the columns after `ORDER BY` with a comma. Sort by the second column when the first column is the same.

??? success "Answer"
    ```sql
    SELECT order_id, amount, card_issuer, installment_months
    FROM payments
    WHERE method = 'card'
      AND installment_months > 0
    ORDER BY installment_months DESC, amount DESC
    LIMIT 5;
    ```

    **Result:**

    | order_id | amount | card_issuer | installment_months |
    | ----------: | ----------: | ---------- | ----------: |
    | 14056 | 22995900.0 | Visa | 24 |
    | 37522 | 13678700.0 | Visa | 24 |
    | 2471 | 13669032.0 | Mastercard | 24 |
    | 3789 | 9690532.0 | Mastercard | 24 |
    | 20271 | 6484600.0 | American Express | 24 |
    | ... | ... | ... | ... |

---

### Problem 18

**Sort GOLD level customers alphabetically by name to view the names and emails of customers 11-15.**

??? tip "Hint"
    `OFFSET 10` (skip 10) to start with the 11th, `LIMIT 5` to get 5 people.

??? success "Answer"
    ```sql
    SELECT name, email
    FROM customers
    WHERE grade = 'GOLD'
    ORDER BY name
    LIMIT 5 OFFSET 10;
    ```

    **Result:**

    | name | email |
    | ---------- | ---------- |
    | Alexandra Thomas | user3908@testmail.kr |
    | Alice Reese DVM | user4988@testmail.kr |
    | Alicia Wiggins | user4089@testmail.kr |
    | Alison Gilmore | user3138@testmail.kr |
    | Allen West | user2493@testmail.kr |
    | ... | ... |

---

### Problem 19

**Check the type of payment method (`method`) without duplicates.**

??? tip "Hint"
    Use `SELECT DISTINCT method FROM payments`.

??? success "Answer"
    ```sql
    SELECT DISTINCT method
    FROM payments
    ORDER BY method;
    ```

    **Result:**

    | method |
    | ---------- |
    | bank_transfer |
    | card |
    | kakao_pay |
    | naver_pay |
    | point |
    | virtual_account |
    | ... |

---

### Problem 20

**Search 5 items by sorting the product name, price, cost (`cost_price`), and margin (price - cost) in order of largest margin. Add the alias `margin` to the margin column.**

??? tip "Hint"
    You can create a calculated column as `price - cost_price AS margin` in the `SELECT` clause.

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

Utilize multiple tables and complex conditions.

---

### Problem 21

**Out of the canceled orders (`status = 'cancelled'`), look up the order number, order amount, and cancellation date (`cancelled_at`) of the five orders with the largest order amount.**

??? tip "Hint"
    Filter by `WHERE status = 'cancelled'` and sort by `ORDER BY total_amount DESC`.

??? success "Answer"
    ```sql
    SELECT order_number, total_amount, cancelled_at
    FROM orders
    WHERE status = 'cancelled'
    ORDER BY total_amount DESC
    LIMIT 5;
    ```

    **Result:**

    | order_number | total_amount | cancelled_at |
    | ---------- | ----------: | ---------- |
    | ORD-20230523-22331 | 46094971.0 | 2023-05-24 05:50:55 |
    | ORD-20221231-20394 | 43585700.0 | 2023-01-02 16:35:59 |
    | ORD-20211112-14229 | 20640700.0 | 2021-11-14 07:35:09 |
    | ORD-20250307-32312 | 18229600.0 | 2025-03-09 07:13:31 |
    | ORD-20250924-35599 | 14735700.0 | 2025-09-25 13:46:38 |
    | ... | ... | ... |

---

### Problem 22

**For products with less than 10 items in stock, sort them in ascending order of stock or descending price to view the name, price, and quantity in stock.**

??? tip "Hint"
    Filter by `WHERE stock_qty <= 10` and multi-sort by `ORDER BY stock_qty ASC, price DESC`.

??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE stock_qty <= 10
    ORDER BY stock_qty ASC, price DESC;
    ```

    **Result (top 5 rows):**

    | name | price | stock_qty |
    | ---------- | ----------: | ----------: |
    | Arctic Freezer 36 A-RGB White | 23000.0 | 0 |
    | Samsung SPA-KFG0BUB | 30700.0 | 4 |
    | Samsung DDR4 32GB PC4-25600 | 91000.0 | 6 |
    | Logitech G502 HERO Silver | 71100.0 | 8 |
    | Norton AntiVirus Plus | 69700.0 | 8 |
    | ... | ... | ... |

---

### Problem 23

**View 10 customers who have never logged in (`last_login_at` is NULL) by name, email, and rating by sorting them in order of sign-up date.**

??? tip "Hint"
    NULL is checked with `IS NULL`, not `= NULL`.

??? success "Answer"
    ```sql
    SELECT name, email, grade
    FROM customers
    WHERE last_login_at IS NULL
    ORDER BY created_at ASC
    LIMIT 10;
    ```

    **Result (top 5 rows):**

    | name | email | grade |
    | ---------- | ---------- | ---------- |
    | Sara Harvey | user25@testmail.kr | BRONZE |
    | Terry Miller DVM | user43@testmail.kr | BRONZE |
    | Tony Jones | user77@testmail.kr | BRONZE |
    | Russell Castillo | user66@testmail.kr | BRONZE |
    | Amy Smith | user80@testmail.kr | BRONZE |
    | James Booker | user172@testmail.kr | BRONZE |
    | Jennifer Love | user169@testmail.kr | BRONZE |
    | Tonya Torres | user101@testmail.kr | BRONZE |
    | ... | ... | ... |

---

### Problem 24

**Check the product name, price, and price including VAT. Calculate the price including VAT as `price * 1.1` and add the aliases `price_with_tax`. Only 5 items will be printed in order of highest price including VAT.**

??? tip "Hint"
    You can get neat results by organizing the decimal points with `ROUND(price * 1.1)`.

??? success "Answer"
    ```sql
    SELECT name, price, ROUND(price * 1.1) AS price_with_tax
    FROM products
    ORDER BY price_with_tax DESC
    LIMIT 5;
    ```

    **Result:**

    | name | price | price_with_tax |
    | ---------- | ----------: | ----------: |
    | MacBook Air 15 M3 Silver | 5481100.0 | 6029210.0 |
    | ASUS TUF Gaming RTX 5080 White | 4526600.0 | 4979260.0 |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 4496700.0 | 4946370.0 |
    | Razer Blade 18 Black | 4353100.0 | 4788410.0 |
    | Razer Blade 16 Silver | 3702900.0 | 4073190.0 |
    | ... | ... | ... |

---

### Problem 25

**Look up the order number, order amount, and order date of the five orders with the largest order amount among orders received in 2024 (`ordered_at` is 2024).**

??? tip "Hint"
    Specify the range to 2024 with `WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'`.

??? success "Answer"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at < '2025-01-01'
    ORDER BY total_amount DESC
    LIMIT 5;
    ```

    **Result:**

    | order_number | total_amount | ordered_at |
    | ---------- | ----------: | ---------- |
    | ORD-20240519-27622 | 33762000.0 | 2024-05-19 22:17:20 |
    | ORD-20240920-29424 | 30446100.0 | 2024-09-20 12:04:46 |
    | ORD-20240425-27274 | 25694900.0 | 2024-04-25 10:44:48 |
    | ORD-20241101-30141 | 21201100.0 | 2024-11-01 20:47:38 |
    | ORD-20240112-25581 | 18265900.0 | 2024-01-12 08:33:51 |
    | ... | ... | ... |

---

### Problem 26

**Order orders with a discount amount (`discount_amount`) greater than 0 in descending order of discount amount, and view 5 order numbers, order amount, discount amount, and order date.**

??? tip "Hint"
    Filter only orders with a discount applied to `WHERE discount_amount > 0`.

??? success "Answer"
    ```sql
    SELECT order_number, total_amount, discount_amount, ordered_at
    FROM orders
    WHERE discount_amount > 0
    ORDER BY discount_amount DESC
    LIMIT 5;
    ```

    **Result:**

    | order_number | total_amount | discount_amount | ordered_at |
    | ---------- | ----------: | ----------: | ---------- |
    | ORD-20221108-19517 | 33599000.0 | 3837300.0 | 2022-11-08 05:28:41 |
    | ORD-20220713-17752 | 32950400.0 | 3126300.0 | 2022-07-13 16:06:23 |
    | ORD-20180910-01979 | 32615814.0 | 2690000.0 | 2018-09-10 15:12:37 |
    | ORD-20230930-23961 | 27295300.0 | 2248800.0 | 2023-09-30 20:13:24 |
    | ORD-20220224-15869 | 35397700.0 | 1924100.0 | 2022-02-24 23:01:50 |
    | ... | ... | ... | ... |

---

### Problem 27

** Sort the items paid with Kakao Pay (`method = 'kakao_pay'`) in order of largest payment amount and search for 5 items including order ID (`order_id`), payment amount, and payment date (`paid_at`).**

??? tip "Hint"
    Filter by `WHERE method = 'kakao_pay'` in table `payments`.

??? success "Answer"
    ```sql
    SELECT order_id, amount, paid_at
    FROM payments
    WHERE method = 'kakao_pay'
    ORDER BY amount DESC
    LIMIT 5;
    ```

    **Result:**

    | order_id | amount | paid_at |
    | ----------: | ----------: | ---------- |
    | 1979 | 32615814.0 | 2018-09-10 15:34:37 |
    | 37004 | 31985600.0 | 2025-12-07 23:36:41 |
    | 15027 | 28836100.0 | 2021-12-23 20:02:54 |
    | 25227 | 27440200.0 | 2023-12-15 11:44:54 |
    | 14074 | 22470000.0 | 2021-11-02 15:36:38 |
    | ... | ... | ... |

---

### Problem 28

**Find 5 customers who signed up in 2025 who are GOLD or VIP level in order of highest accumulated points. Prints name, level, points, and membership date.**

??? tip "Hint"
    Combine conditions with `WHERE created_at >= '2025-01-01' AND grade IN ('GOLD', 'VIP')`.

??? success "Answer"
    ```sql
    SELECT name, grade, point_balance, created_at
    FROM customers
    WHERE created_at >= '2025-01-01'
      AND grade IN ('GOLD', 'VIP')
    ORDER BY point_balance DESC
    LIMIT 5;
    ```

    **Result:**

    | name | grade | point_balance | created_at |
    | ---------- | ---------- | ----------: | ---------- |
    | Sandra Williams | VIP | 323554 | 2025-10-24 12:23:58 |
    | Ronald Smith | VIP | 263155 | 2025-03-03 21:41:00 |
    | Alison Kelly | VIP | 126048 | 2025-03-05 01:34:09 |
    | Lauren Dunn | VIP | 122578 | 2025-02-07 19:27:08 |
    | Danielle Roberts | VIP | 109984 | 2025-03-11 13:39:02 |
    | ... | ... | ... | ... |

---

### Problem 29

**View 5 non-ASUS brand products (`brand != 'ASUS'`) excluding Samsung Electronics, LG Electronics, and MSI in descending order of price. Prints name, brand, and price.**

??? tip "Hint"
    `NOT IN` allows you to exclude multiple values ​​at once.

??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand NOT IN ('ASUS', '삼성전자', 'LG전자', 'MSI')
    ORDER BY price DESC
    LIMIT 5;
    ```

    **Result:**

    | name | brand | price |
    | ---------- | ---------- | ----------: |
    | MacBook Air 15 M3 Silver | Apple | 5481100.0 |
    | Razer Blade 18 Black | Razer | 4353100.0 |
    | Razer Blade 16 Silver | Razer | 3702900.0 |
    | Razer Blade 18 Black | Razer | 2987500.0 |
    | Razer Blade 18 White | Razer | 2483600.0 |
    | ... | ... | ... |

---

### Problem 30

**Look up the names, weights (grams), and prices of the five heaviest products among products with recorded weight (`weight_grams`). Also print the `weight_kg` column, which converts the weight to kilograms.**

??? tip "Hint"
    Filter only products with weight by `WHERE weight_grams IS NOT NULL`. Calculate kilograms with `weight_grams / 1000.0`.

??? success "Answer"
    ```sql
    SELECT name,
           weight_grams,
           ROUND(weight_grams / 1000.0, 1) AS weight_kg,
           price
    FROM products
    WHERE weight_grams IS NOT NULL
    ORDER BY weight_grams DESC
    LIMIT 5;
    ```

    **Result:**

    | name | weight_grams | weight_kg | price |
    | ---------- | ----------: | ----------: | ----------: |
    | ASUS ROG Strix GT35 | 19449 | 19.4 | 3296800.0 |
    | Hansung BossMonster DX7700 White | 19250 | 19.3 | 1579400.0 |
    | ASUS ROG Strix G16CH White | 16624 | 16.6 | 3671500.0 |
    | Hansung BossMonster DX9900 Silver | 14892 | 14.9 | 739900.0 |
    | ASUS ROG Strix G16CH Silver | 14308 | 14.3 | 1879100.0 |
    | ... | ... | ... | ... |
