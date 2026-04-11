# Sorting and Paging

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `products` — products (name, price, stock, brand)<br>
    `customers` — customers (tier, points, signup channel)<br>
    `orders` — orders (status, amount, date/time)<br>
    `reviews` — reviews (rating, content)<br>
    `payments` — payments (method, amount, status)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    `SELECT`<br>
    `WHERE`<br>
    `ORDER BY`<br>
    `LIMIT`<br>
    `OFFSET`<br>
    `DISTINCT`<br>
    Aliases (`AS`)<br>
    arithmetic operations

</div>

!!! info "Before You Begin"
    This exercise uses only what you learned in **Introductory Lessons 1-3** (SELECT, WHERE, ORDER BY, LIMIT, OFFSET).
    JOINs, subqueries, GROUP BY, and aggregate functions are not used.

---

## Basic (1~10)

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
    | TP-Link TL-SG108 실버 | TP-Link | 16500.0 |
    | 로지텍 M100r | 로지텍 | 17300.0 |
    | 넷기어 GS308 블랙 | 넷기어 | 17400.0 |
    | TP-Link TL-SG108E | TP-Link | 18000.0 |
    | 로지텍 G502 HERO [특별 한정판 에디션] 무상 보증 3년 연장 + 전용 파우치 증정 이벤트 | 로지텍 | 19400.0 |
    | TP-Link TG-3468 블랙 | TP-Link | 19800.0 |
    | TP-Link TL-SG108 | TP-Link | 20100.0 |
    | 삼성 무선 키보드 Trio 500 화이트 | 삼성전자 | 20300.0 |
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
    | Razer Blade 14 블랙 | 7495200.0 |
    | Razer Blade 16 블랙 | 5634900.0 |
    | Razer Blade 16 | 5518300.0 |
    | Razer Blade 16 화이트 | 5503500.0 |
    | Razer Blade 18 | 5450500.0 |
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
    | Arctic Freezer 36 A-RGB 화이트 | 27400.0 | 0 |
    | 한컴오피스 2024 기업용 실버 | 391200.0 | 0 |
    | 삼성 DDR4 16GB PC4-25600 | 73600.0 | 0 |
    | WD My Passport 2TB 블랙 | 329100.0 | 0 |
    | 삼성 DDR5 32GB PC5-38400 실버 | 158000.0 | 0 |
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
    | 이주원 | user313@testmail.kr | BRONZE | 2016-01-01 00:00:52 |
    | 성미숙 | user133@testmail.kr | BRONZE | 2016-01-01 00:53:24 |
    | 오진호 | user584@testmail.kr | BRONZE | 2016-01-01 03:10:41 |
    | 노지민 | user387@testmail.kr | BRONZE | 2016-01-01 10:17:05 |
    | 장승현 | user690@testmail.kr | BRONZE | 2016-01-01 15:11:55 |
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
    | AMD Ryzen 5 9600X | 186400.0 |
    | AMD Ryzen 7 7700X | 691500.0 |
    | AMD Ryzen 7 7700X 블랙 | 1105200.0 |
    | AMD Ryzen 7 7700X 블랙 | 458300.0 |
    | AMD Ryzen 7 7800X3D | 750800.0 |
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
    | Razer Blade 14 | 5339100.0 |
    | Razer Blade 16 실버 | 5127500.0 |
    | Razer Blade 16 블랙 | 4938200.0 |
    | Razer Blade 18 화이트 | 4913500.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 4881500.0 |
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
    | 박정수 | VIP | 6344986 |
    | 정유진 | VIP | 6255658 |
    | 이미정 | VIP | 5999946 |
    | 김상철 | VIP | 5406032 |
    | 문영숙 | VIP | 4947814 |
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
    | ORD-20230408-248697 | 71906300.0 | 2023-04-08 16:24:03 |
    | ORD-20240218-293235 | 68948100.0 | 2024-02-18 20:53:49 |
    | ORD-20240822-323378 | 64332900.0 | 2024-08-22 13:20:32 |
    | ORD-20180516-26809 | 63466900.0 | 2018-05-16 06:29:52 |
    | ORD-20200429-82365 | 61889000.0 | 2020-04-29 21:21:06 |
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
    | Apple |
    | Arctic |
    | BenQ |
    | ... |

---

## Applied (11~20)

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
    | Razer Blade 14 블랙 | Razer | 7495200.0 |
    | Razer Blade 16 블랙 | Razer | 5634900.0 |
    | Razer Blade 16 | Razer | 5518300.0 |
    | Razer Blade 16 화이트 | Razer | 5503500.0 |
    | Razer Blade 18 | Razer | 5450500.0 |
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
    | 로지텍 G715 실버 | 100600.0 | 2025-12-27 19:50:12 |
    | 시소닉 FOCUS GM-750 실버 | 98900.0 | 2025-12-25 20:05:49 |
    | SteelSeries Arctis Nova 7 Wireless 실버 | 367300.0 | 2025-12-24 21:58:49 |
    | Dell Latitude 5540 실버 | 1113900.0 | 2025-12-17 22:47:10 |
    | 주연 리오나인 i9 하이엔드 실버 | 1663400.0 | 2025-12-15 15:04:20 |
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
    | 불량품 | 1 | 2026-01-18 18:51:49 |
    | 최악 | 1 | 2026-01-17 08:02:24 |
    | 환불 원해요 | 1 | 2026-01-16 08:03:22 |
    | 환불 원해요 | 1 | 2026-01-11 18:10:03 |
    | 최악 | 1 | 2026-01-08 20:38:55 |
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
    | 엡손 L15160 | 엡손 | 501700.0 |
    | 삼성 S24C360 블랙 | 삼성전자 | 503500.0 |
    | 넷기어 RAX70 실버 | 넷기어 | 506300.0 |
    | ASRock B860M Pro RS 화이트 | ASRock | 506700.0 |
    | 필립스 328E1CA 실버 | 필립스 | 507300.0 |
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
    | 293235 | 68948100.0 | 삼성카드 | 24 |
    | 307025 | 47227200.0 | KB국민카드 | 24 |
    | 76585 | 46052600.0 | KB국민카드 | 24 |
    | 405306 | 46031200.0 | KB국민카드 | 24 |
    | 18938 | 44626000.0 | 롯데카드 | 24 |
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
    | 강미경 | user16965@testmail.kr |
    | 강미영 | user41074@testmail.kr |
    | 강미정 | user12237@testmail.kr |
    | 강민서 | user12355@testmail.kr |
    | 강민서 | user17719@testmail.kr |
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
    | Razer Blade 14 블랙 | 7495200.0 | 4161000.0 | 3334200.0 |
    | MacBook Air 13 M4 | 4449200.0 | 2451900.0 | 1997300.0 |
    | Razer Blade 16 | 5518300.0 | 3703300.0 | 1815000.0 |
    | MSI GeForce RTX 5070 Ti VENTUS 3X 실버 | 4881500.0 | 3168100.0 | 1713400.0 |
    | Razer Blade 18 화이트 | 4913500.0 | 3251900.0 | 1661600.0 |
    | ... | ... | ... | ... |

---

## Practical (21~30)

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
    | ORD-20191116-64149 | 43727700.0 | 2019-11-17 22:33:13 |
    | ORD-20190330-46537 | 38907900.0 | 2019-04-01 08:28:58 |
    | ORD-20191105-63133 | 33039100.0 | 2019-11-05 10:16:57 |
    | ORD-20211105-162659 | 32777300.0 | 2021-11-06 22:22:58 |
    | ORD-20230319-245317 | 30961500.0 | 2023-03-20 17:28:12 |
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
    | 한컴오피스 2024 기업용 실버 | 391200.0 | 0 |
    | WD My Passport 2TB 블랙 | 329100.0 | 0 |
    | 삼성 DDR5 32GB PC5-38400 실버 | 158000.0 | 0 |
    | 삼성 DDR4 16GB PC4-25600 | 73600.0 | 0 |
    | Arctic Freezer 36 A-RGB 화이트 | 27400.0 | 0 |
    | Dell S2425HS 블랙 | 667900.0 | 1 |
    | Dell U2723QE 실버 | 396300.0 | 1 |
    | Arctic Liquid Freezer III 240 | 189300.0 | 1 |
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
    | 김시우 | user337@testmail.kr | BRONZE |
    | 박민준 | user426@testmail.kr | BRONZE |
    | 오지후 | user172@testmail.kr | BRONZE |
    | 윤준영 | user25@testmail.kr | BRONZE |
    | 권지우 | user169@testmail.kr | BRONZE |
    | 정정희 | user918@testmail.kr | BRONZE |
    | 이영식 | user43@testmail.kr | BRONZE |
    | 전혜진 | user954@testmail.kr | BRONZE |
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
    | Razer Blade 14 블랙 | 7495200.0 | 8244720.0 |
    | Razer Blade 16 블랙 | 5634900.0 | 6198390.0 |
    | Razer Blade 16 | 5518300.0 | 6070130.0 |
    | Razer Blade 16 화이트 | 5503500.0 | 6053850.0 |
    | Razer Blade 18 | 5450500.0 | 5995550.0 |
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
    | ORD-20240218-293235 | 68948100.0 | 2024-02-18 20:53:49 |
    | ORD-20240822-323378 | 64332900.0 | 2024-08-22 13:20:32 |
    | ORD-20241013-332643 | 57772300.0 | 2024-10-13 19:57:10 |
    | ORD-20241209-344848 | 56012148.0 | 2024-12-09 18:50:12 |
    | ORD-20240206-291311 | 52034300.0 | 2024-02-06 15:17:20 |
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
    | ORD-20240913-327284 | 38829400.0 | 3737700.0 | 2024-09-13 01:31:44 |
    | ORD-20230922-270979 | 32947100.0 | 3097300.0 | 2023-09-22 14:55:31 |
    | ORD-20241231-350072 | 28566900.0 | 2878300.0 | 2024-12-31 20:04:20 |
    | ORD-20210923-155344 | 26679400.0 | 2634900.0 | 2021-09-23 20:27:26 |
    | ORD-20241209-344848 | 56012148.0 | 2305600.0 | 2024-12-09 18:50:12 |
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
    | 3977 | 60810900.0 | 2016-07-30 19:21:23 |
    | 417476 | 60038800.0 | (NULL) |
    | 207504 | 56303700.0 | 2022-07-28 19:26:23 |
    | 344848 | 56012148.0 | 2024-12-09 19:12:12 |
    | 266880 | 49494600.0 | 2023-08-22 13:16:33 |
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
    | 강정식 | VIP | 348058 | 2025-03-21 04:25:02 |
    | 박영미 | VIP | 314830 | 2025-05-02 04:12:57 |
    | 권준혁 | VIP | 272576 | 2025-02-25 10:25:19 |
    | 서은서 | VIP | 262093 | 2025-01-03 09:53:15 |
    | 이순자 | VIP | 257309 | 2025-01-27 23:01:11 |
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
    | Razer Blade 14 블랙 | Razer | 7495200.0 |
    | Razer Blade 16 블랙 | Razer | 5634900.0 |
    | Razer Blade 16 | Razer | 5518300.0 |
    | Razer Blade 16 화이트 | Razer | 5503500.0 |
    | Razer Blade 18 | Razer | 5450500.0 |
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
    | 한성 보스몬스터 DX7700 실버 | 19914 | 19.9 | 3230900.0 |
    | ASUS ROG Strix GT35 실버 | 19883 | 19.9 | 2553100.0 |
    | APC Back-UPS Pro BR1500G 실버 | 19791 | 19.8 | 340300.0 |
    | ASUS ROG Strix GT35 화이트 | 19598 | 19.6 | 1637500.0 |
    | ASUS ROG Strix GT35 | 19449 | 19.4 | 3296400.0 |
    | ... | ... | ... | ... |
