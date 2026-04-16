# Sorting and Paging

!!! info "Tables"

    `products` — Products (name, price, stock, brand)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `reviews` — Reviews (rating, content)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `OFFSET`, `DISTINCT`, `AS`, `arithmetic operations`



### 1. Sort the products in order of highest price and look up the 


Sort the products in order of highest price and look up the name (`name`) and price (`price`).


**Hint 1:** Using ORDER BY price DESC sorts in descending order


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC;
    ```


    **Result** (top 7 of 280 rows)

    | name | price |
    |---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 |
    | Razer Blade 18 Black | 4,353,100.00 |
    | Razer Blade 16 Silver | 3,702,900.00 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 |


---


### 2. Sort products in descending order of price and search for na


Sort products in descending order of price and search for name, brand (`brand`), and price.


**Hint 1:** Just using ORDER BY price ASC or ORDER BY price will result in ascending order (default)


??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    ORDER BY price ASC;
    ```


    **Result** (top 7 of 280 rows)

    | name | brand | price |
    |---|---|---|
    | TP-Link TG-3468 Black | TP-Link | 18,500.00 |
    | Samsung SPA-KFG0BUB Silver | Samsung | 21,900.00 |
    | Arctic Freezer 36 A-RGB White | Arctic | 23,000.00 |
    | Arctic Freezer 36 A-RGB White | Arctic | 29,900.00 |
    | TP-Link Archer TBE400E White | TP-Link | 30,200.00 |
    | Samsung SPA-KFG0BUB | Samsung | 30,700.00 |
    | Logitech MK470 Black | Logitech | 31,800.00 |


---


### 3. View the names and prices of the 5 most expensive products.


View the names and prices of the 5 most expensive products.


**Hint 1:** Sort by ORDER BY and then get only the top N by LIMIT


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | price |
    |---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 |
    | Razer Blade 18 Black | 4,353,100.00 |
    | Razer Blade 16 Silver | 3,702,900.00 |


---


### 4. View the name, price, and inventory quantity of the five pro


View the name, price, and inventory quantity of the five products with the lowest inventory quantity (`stock_qty`).


**Hint 1:** If you sort by ORDER BY stock_qty ASC in ascending order, the inventory is low


??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    ORDER BY stock_qty ASC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | price | stock_qty |
    |---|---|---|
    | Arctic Freezer 36 A-RGB White | 23,000.00 | 0 |
    | Samsung SPA-KFG0BUB | 30,700.00 | 4 |
    | Samsung DDR4 32GB PC4-25600 | 91,000.00 | 6 |
    | Norton AntiVirus Plus | 69,700.00 | 8 |
    | Logitech G502 HERO Silver | 71,100.00 | 8 |


---


### 5. Sort customers in order of sign-up date (`created_at`) to vi


Sort customers in order of sign-up date (`created_at`) to view the names, emails, ratings (`grade`), and sign-up dates of the five customers who signed up first.


**Hint 1:** Use ORDER BY created_at ASC to list the oldest subscription date first


??? success "Answer"
    ```sql
    SELECT name, email, grade, created_at
    FROM customers
    ORDER BY created_at ASC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | email | grade | created_at |
    |---|---|---|---|
    | Alan Blair | user84@testmail.kr | BRONZE | 2016-01-03 19:49:46 |
    | Mary Jackson | user61@testmail.kr | BRONZE | 2016-01-04 14:11:21 |
    | Joseph Sellers | user90@testmail.kr | GOLD | 2016-01-05 22:02:29 |
    | Gabriel Walters | user98@testmail.kr | VIP | 2016-01-09 06:08:34 |
    | Lydia Lawrence | user15@testmail.kr | BRONZE | 2016-01-14 06:39:08 |


---


### 6. Sort product names in alphabetical/alphabetical order to vie


Sort product names in alphabetical/alphabetical order to view the first 5 items.


**Hint 1:** When sorted by ORDER BY name, the English alphabet comes before the Korean alphabet


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY name
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | price |
    |---|---|
    | AMD Ryzen 9 9900X | 335,700.00 |
    | AMD Ryzen 9 9900X | 591,800.00 |
    | APC Back-UPS Pro Gaming BGM1500B Black | 516,300.00 |
    | ASRock B850M Pro RS Black | 201,000.00 |
    | ASRock B850M Pro RS Silver | 665,600.00 |


---


### 7. View the top 6-10 most expensive products (i.e. skip the top


View the top 6-10 most expensive products (i.e. skip the top 5 and go to the next 5).


**Hint 1:** OFFSET skips the specified number of rows. Fetch from the 6th with LIMIT 5 OFFSET 5


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5 OFFSET 5;
    ```


    **Result** (5 rows)

    | name | price |
    |---|---|
    | ASUS ROG Strix G16CH White | 3,671,500.00 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 |
    | ASUS ROG Strix GT35 | 3,296,800.00 |
    | Razer Blade 18 Black | 2,987,500.00 |
    | ASUS Dual RTX 4060 Ti Black | 2,674,800.00 |


---


### 8. View the names, levels, and points of the 5 customers with t


View the names, levels, and points of the 5 customers with the most points (`point_balance`).


**Hint 1:** Sort in descending order with ORDER BY point_balance DESC and then apply LIMIT 5


??? success "Answer"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    ORDER BY point_balance DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | grade | point_balance |
    |---|---|---|
    | Allen Snyder | VIP | 3,955,828 |
    | Jason Rivera | VIP | 3,518,880 |
    | Brenda Garcia | VIP | 2,450,166 |
    | Courtney Huff | VIP | 2,383,491 |
    | James Banks | VIP | 2,297,542 |


---


### 9. Look up the order number (`order_number`), order amount, and


Look up the order number (`order_number`), order amount, and order date (`ordered_at`) of the five orders with the largest order amount (`total_amount`).


**Hint 1:** Use ORDER BY total_amount DESC LIMIT 5 in table orders


??? success "Answer"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | order_number | total_amount | ordered_at |
    |---|---|---|
    | ORD-20201121-08810 | 50,867,500.00 | 2020-11-21 12:04:42 |
    | ORD-20250305-32265 | 46,820,024.00 | 2025-03-05 09:01:08 |
    | ORD-20230523-22331 | 46,094,971.00 | 2023-05-23 08:50:55 |
    | ORD-20200209-05404 | 43,677,500.00 | 2020-02-09 23:36:36 |
    | ORD-20221231-20394 | 43,585,700.00 | 2022-12-31 21:35:59 |


---


### 10. View the list of brands registered in the product table in a


View the list of brands registered in the product table in alphabetical order without duplication.


**Hint 1:** Remove duplicates with SELECT DISTINCT brand and sort with ORDER BY brand


??? success "Answer"
    ```sql
    SELECT DISTINCT brand
    FROM products
    ORDER BY brand;
    ```


    **Result** (top 7 of 55 rows)

    | brand |
    |---|
    | AMD |
    | APC |
    | ASRock |
    | ASUS |
    | Adobe |
    | AhnLab |
    | Apple |


---


### 11. Sort products with a price of 1 million won or more in desce


Sort products with a price of 1 million won or more in descending order of price and search for name, brand, and price. Prints only the top 5.


**Hint 1:** Filter by WHERE price >= 1000000 and then apply ORDER BY price DESC LIMIT 5


??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price >= 1000000
    ORDER BY price DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | brand | price |
    |---|---|---|
    | MacBook Air 15 M3 Silver | Apple | 5,481,100.00 |
    | ASUS TUF Gaming RTX 5080 White | ASUS | 4,526,600.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | ASUS | 4,496,700.00 |
    | Razer Blade 18 Black | Razer | 4,353,100.00 |
    | Razer Blade 16 Silver | Razer | 3,702,900.00 |


---


### 12. Sort Samsung Electronics or LG Electronics brand products in


Sort Samsung Electronics or LG Electronics brand products in descending price order to search for name, brand, and price. Prints only the top 5.


**Hint 1:** Filter the two brands by WHERE brand IN ('삼성전자', 'LG전자')


??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand IN ('삼성전자', 'LG전자')
    ORDER BY price DESC
    LIMIT 5;
    ```


---


### 13. Among VIP level customers, sort the customers with the last 


Among VIP level customers, sort the customers with the last name 'Kim' in order of the highest amount of points and view the names, levels, and points of only 5 people.


**Hint 1:** Apply both conditions simultaneously with WHERE grade = 'VIP' AND name LIKE '김%'


??? success "Answer"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    WHERE grade = 'VIP'
      AND name LIKE '김%'
    ORDER BY point_balance DESC
    LIMIT 5;
    ```


---


### 14. Sort discontinued products (products where `discontinued_at`


Sort discontinued products (products where `discontinued_at` is not NULL) in the most recent order based on the discontinuation date to view only 5 names, prices, and discontinuation dates.


**Hint 1:** Filter only discontinued products with WHERE discontinued_at IS NOT NULL


??? success "Answer"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL
    ORDER BY discontinued_at DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | price | discontinued_at |
    |---|---|---|
    | Dell XPS Desktop 8960 Silver | 1,249,400.00 | 2025-11-20 15:30:12 |
    | Kingston FURY Beast DDR4 16GB White | 91,200.00 | 2025-11-18 04:06:13 |
    | Intel Core Ultra 7 265K | 196,300.00 | 2025-11-16 21:11:33 |
    | Hansung BossMonster DX7700 White | 1,579,400.00 | 2025-10-25 03:47:01 |
    | Intel Core Ultra 7 265K White | 170,200.00 | 2025-08-24 00:34:53 |


---


### 15. Sort reviews with a review rating (`rating`) of 1 in the mos


Sort reviews with a review rating (`rating`) of 1 in the most recent order and view the 5 titles (`title`), rating, and creation date (`created_at`).


**Hint 1:** In table reviews, filter by WHERE rating = 1 and sort by ORDER BY created_at DESC


??? success "Answer"
    ```sql
    SELECT title, rating, created_at
    FROM reviews
    WHERE rating = 1
    ORDER BY created_at DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | title | rating | created_at |
    |---|---|---|
    | NULL | 1 | 2026-01-05 20:37:52 |
    | NULL | 1 | 2025-12-21 21:52:59 |
    | Never Again | 1 | 2025-12-20 11:53:58 |
    | NULL | 1 | 2025-12-19 08:58:30 |
    | Defective | 1 | 2025-12-14 10:07:24 |


---


### 16. Sort products priced between 500,000 won and 1 million won o


Sort products priced between 500,000 won and 1 million won or less in ascending order of price and search for 5 names, brands, and prices.


**Hint 1:** Specify the range with WHERE price BETWEEN 500000 AND 1000000


??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price BETWEEN 500000 AND 1000000
    ORDER BY price ASC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | brand | price |
    |---|---|---|
    | CyberPower BRG1500AVRLCD Silver | CyberPower | 508,100.00 |
    | APC Back-UPS Pro Gaming BGM1500B Black | APC | 516,300.00 |
    | Philips 27E1N5300AE White | Philips | 518,700.00 |
    | Gigabyte Z790 AORUS MASTER | Gigabyte | 520,400.00 |
    | Epson L3260 | Epson | 525,400.00 |


---


### 17. Among card payments (`method = 'card'`), search for 5 cases 


Among card payments (`method = 'card'`), search for 5 cases where the number of installment months (`installment_months`) is greater than 0 by sorting them in descending order of the number of installment months and descending order of payment amount (`amount`). Prints order ID, payment amount, card company (`card_issuer`), and number of installment months.


**Hint 1:** Multiple sorting occurs if you separate the columns after ORDER BY with a comma. Sort by the second column when the first column is the same


??? success "Answer"
    ```sql
    SELECT order_id, amount, card_issuer, installment_months
    FROM payments
    WHERE method = 'card'
      AND installment_months > 0
    ORDER BY installment_months DESC, amount DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | order_id | amount | card_issuer | installment_months |
    |---|---|---|---|
    | 14,056 | 22,995,900.00 | Visa | 24 |
    | 37,522 | 13,678,700.00 | Visa | 24 |
    | 2471 | 13,669,032.00 | Mastercard | 24 |
    | 3789 | 9,690,532.00 | Mastercard | 24 |
    | 20,271 | 6,484,600.00 | American Express | 24 |


---


### 18. Sort GOLD level customers alphabetically by name to view the


Sort GOLD level customers alphabetically by name to view the names and emails of customers 11-15.


**Hint 1:** OFFSET 10 (skip 10) to start with the 11th, LIMIT 5 to get 5 people


??? success "Answer"
    ```sql
    SELECT name, email
    FROM customers
    WHERE grade = 'GOLD'
    ORDER BY name
    LIMIT 5 OFFSET 10;
    ```


    **Result** (5 rows)

    | name | email |
    |---|---|
    | Alexandra Thomas | user3908@testmail.kr |
    | Alice Reese DVM | user4988@testmail.kr |
    | Alicia Wiggins | user4089@testmail.kr |
    | Alison Gilmore | user3138@testmail.kr |
    | Allen West | user2493@testmail.kr |


---


### 19. Check the type of payment method (`method`) without duplicat


Check the type of payment method (`method`) without duplicates.


**Hint 1:** Use SELECT DISTINCT method FROM payments


??? success "Answer"
    ```sql
    SELECT DISTINCT method
    FROM payments
    ORDER BY method;
    ```


    **Result** (6 rows)

    | method |
    |---|
    | bank_transfer |
    | card |
    | kakao_pay |
    | naver_pay |
    | point |
    | virtual_account |


---


### 20. Search 5 items by sorting the product name, price, cost (`co


Search 5 items by sorting the product name, price, cost (`cost_price`), and margin (price - cost) in order of largest margin. Add the alias `margin` to the margin column.


**Hint 1:** You can create a calculated column as price - cost_price AS margin in the SELECT clause


??? success "Answer"
    ```sql
    SELECT name, price, cost_price, price - cost_price AS margin
    FROM products
    ORDER BY margin DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | price | cost_price | margin |
    |---|---|---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 | 3,205,400.00 | 2,275,700.00 |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 | 3,037,100.00 | 1,489,500.00 |
    | Razer Blade 18 Black | 4,353,100.00 | 3,047,200.00 | 1,305,900.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 | 3,296,400.00 | 1,200,300.00 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 | 2,480,900.00 | 1,190,600.00 |


---


### 21. Out of the canceled orders (`status = 'cancelled'`), look up


Out of the canceled orders (`status = 'cancelled'`), look up the order number, order amount, and cancellation date (`cancelled_at`) of the five orders with the largest order amount.


**Hint 1:** Filter by WHERE status = 'cancelled' and sort by ORDER BY total_amount DESC


??? success "Answer"
    ```sql
    SELECT order_number, total_amount, cancelled_at
    FROM orders
    WHERE status = 'cancelled'
    ORDER BY total_amount DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | order_number | total_amount | cancelled_at |
    |---|---|---|
    | ORD-20230523-22331 | 46,094,971.00 | 2023-05-24 05:50:55 |
    | ORD-20221231-20394 | 43,585,700.00 | 2023-01-02 16:35:59 |
    | ORD-20211112-14229 | 20,640,700.00 | 2021-11-14 07:35:09 |
    | ORD-20250307-32312 | 18,229,600.00 | 2025-03-09 07:13:31 |
    | ORD-20250924-35599 | 14,735,700.00 | 2025-09-25 13:46:38 |


---


### 22. For products with less than 10 items in stock, sort them in 


For products with less than 10 items in stock, sort them in ascending order of stock or descending price to view the name, price, and quantity in stock.


**Hint 1:** Filter by WHERE stock_qty <= 10 and multi-sort by ORDER BY stock_qty ASC, price DESC


??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE stock_qty <= 10
    ORDER BY stock_qty ASC, price DESC;
    ```


    **Result** (5 rows)

    | name | price | stock_qty |
    |---|---|---|
    | Arctic Freezer 36 A-RGB White | 23,000.00 | 0 |
    | Samsung SPA-KFG0BUB | 30,700.00 | 4 |
    | Samsung DDR4 32GB PC4-25600 | 91,000.00 | 6 |
    | Logitech G502 HERO Silver | 71,100.00 | 8 |
    | Norton AntiVirus Plus | 69,700.00 | 8 |


---


### 23. View 10 customers who have never logged in (`last_login_at` 


View 10 customers who have never logged in (`last_login_at` is NULL) by name, email, and rating by sorting them in order of sign-up date.


**Hint 1:** NULL is checked with IS NULL, not = NULL


??? success "Answer"
    ```sql
    SELECT name, email, grade
    FROM customers
    WHERE last_login_at IS NULL
    ORDER BY created_at ASC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | email | grade |
    |---|---|---|
    | Sara Harvey | user25@testmail.kr | BRONZE |
    | Terry Miller DVM | user43@testmail.kr | BRONZE |
    | Tony Jones | user77@testmail.kr | BRONZE |
    | Russell Castillo | user66@testmail.kr | BRONZE |
    | Amy Smith | user80@testmail.kr | BRONZE |
    | James Booker | user172@testmail.kr | BRONZE |
    | Jennifer Love | user169@testmail.kr | BRONZE |


---


### 24. Check the product name, price, and price including VAT. Calc


Check the product name, price, and price including VAT. Calculate the price including VAT as `price * 1.1` and add the aliases `price_with_tax`. Only 5 items will be printed in order of highest price including VAT.


**Hint 1:** You can get neat results by organizing the decimal points with ROUND(price * 1.1)


??? success "Answer"
    ```sql
    SELECT name, price, ROUND(price * 1.1) AS price_with_tax
    FROM products
    ORDER BY price_with_tax DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | price | price_with_tax |
    |---|---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 | 6,029,210.00 |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 | 4,979,260.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 | 4,946,370.00 |
    | Razer Blade 18 Black | 4,353,100.00 | 4,788,410.00 |
    | Razer Blade 16 Silver | 3,702,900.00 | 4,073,190.00 |


---


### 25. Look up the order number, order amount, and order date of th


Look up the order number, order amount, and order date of the five orders with the largest order amount among orders received in 2024 (`ordered_at` is 2024).


**Hint 1:** Specify the range to 2024 with WHERE ordered_at >= '2024-01-01' AND ordered_at < '2025-01-01'


??? success "Answer"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at < '2025-01-01'
    ORDER BY total_amount DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | order_number | total_amount | ordered_at |
    |---|---|---|
    | ORD-20240519-27622 | 33,762,000.00 | 2024-05-19 22:17:20 |
    | ORD-20240920-29424 | 30,446,100.00 | 2024-09-20 12:04:46 |
    | ORD-20240425-27274 | 25,694,900.00 | 2024-04-25 10:44:48 |
    | ORD-20241101-30141 | 21,201,100.00 | 2024-11-01 20:47:38 |
    | ORD-20240112-25581 | 18,265,900.00 | 2024-01-12 08:33:51 |


---


### 26. Order orders with a discount amount (`discount_amount`) grea


Order orders with a discount amount (`discount_amount`) greater than 0 in descending order of discount amount, and view 5 order numbers, order amount, discount amount, and order date.


**Hint 1:** Filter only orders with a discount applied to WHERE discount_amount > 0


??? success "Answer"
    ```sql
    SELECT order_number, total_amount, discount_amount, ordered_at
    FROM orders
    WHERE discount_amount > 0
    ORDER BY discount_amount DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | order_number | total_amount | discount_amount | ordered_at |
    |---|---|---|---|
    | ORD-20221108-19517 | 33,599,000.00 | 3,837,300.00 | 2022-11-08 05:28:41 |
    | ORD-20220713-17752 | 32,950,400.00 | 3,126,300.00 | 2022-07-13 16:06:23 |
    | ORD-20180910-01979 | 32,615,814.00 | 2,690,000.00 | 2018-09-10 15:12:37 |
    | ORD-20230930-23961 | 27,295,300.00 | 2,248,800.00 | 2023-09-30 20:13:24 |
    | ORD-20220224-15869 | 35,397,700.00 | 1,924,100.00 | 2022-02-24 23:01:50 |


---


### 27. Sort the items paid with Kakao Pay (`method = 'kakao_pay'`) 


Sort the items paid with Kakao Pay (`method = 'kakao_pay'`) in order of largest payment amount and search for 5 items including order ID (`order_id`), payment amount, and payment date (`paid_at`).


**Hint 1:** Filter by WHERE method = 'kakao_pay' in table payments


??? success "Answer"
    ```sql
    SELECT order_id, amount, paid_at
    FROM payments
    WHERE method = 'kakao_pay'
    ORDER BY amount DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | order_id | amount | paid_at |
    |---|---|---|
    | 1979 | 32,615,814.00 | 2018-09-10 15:34:37 |
    | 37,004 | 31,985,600.00 | 2025-12-07 23:36:41 |
    | 15,027 | 28,836,100.00 | 2021-12-23 20:02:54 |
    | 25,227 | 27,440,200.00 | 2023-12-15 11:44:54 |
    | 14,074 | 22,470,000.00 | 2021-11-02 15:36:38 |


---


### 28. Find 5 customers who signed up in 2025 who are GOLD or VIP l


Find 5 customers who signed up in 2025 who are GOLD or VIP level in order of highest accumulated points. Prints name, level, points, and membership date.


**Hint 1:** Combine conditions with WHERE created_at >= '2025-01-01' AND grade IN ('GOLD', 'VIP')


??? success "Answer"
    ```sql
    SELECT name, grade, point_balance, created_at
    FROM customers
    WHERE created_at >= '2025-01-01'
      AND grade IN ('GOLD', 'VIP')
    ORDER BY point_balance DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | grade | point_balance | created_at |
    |---|---|---|---|
    | Sandra Williams | VIP | 323,554 | 2025-10-24 12:23:58 |
    | Ronald Smith | VIP | 263,155 | 2025-03-03 21:41:00 |
    | Alison Kelly | VIP | 126,048 | 2025-03-05 01:34:09 |
    | Lauren Dunn | VIP | 122,578 | 2025-02-07 19:27:08 |
    | Danielle Roberts | VIP | 109,984 | 2025-03-11 13:39:02 |


---


### 29. View 5 non-ASUS brand products (`brand != 'ASUS'`) excluding


View 5 non-ASUS brand products (`brand != 'ASUS'`) excluding Samsung Electronics, LG Electronics, and MSI in descending order of price. Prints name, brand, and price.


**Hint 1:** NOT IN allows you to exclude multiple values at once


??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE brand NOT IN ('ASUS', '삼성전자', 'LG전자', 'MSI')
    ORDER BY price DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | brand | price |
    |---|---|---|
    | MacBook Air 15 M3 Silver | Apple | 5,481,100.00 |
    | Razer Blade 18 Black | Razer | 4,353,100.00 |
    | Razer Blade 16 Silver | Razer | 3,702,900.00 |
    | Razer Blade 18 Black | Razer | 2,987,500.00 |
    | Razer Blade 18 White | Razer | 2,483,600.00 |


---


### 30. Look up the names, weights (grams), and prices of the five h


Look up the names, weights (grams), and prices of the five heaviest products among products with recorded weight (`weight_grams`). Also print the `weight_kg` column, which converts the weight to kilograms.


**Hint 1:** Filter only products with weight by WHERE weight_grams IS NOT NULL. Calculate kilograms with weight_grams / 1000.0


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


    **Result** (5 rows)

    | name | weight_grams | weight_kg | price |
    |---|---|---|---|
    | ASUS ROG Strix GT35 | 19,449 | 19.40 | 3,296,800.00 |
    | Hansung BossMonster DX7700 White | 19,250 | 19.30 | 1,579,400.00 |
    | ASUS ROG Strix G16CH White | 16,624 | 16.60 | 3,671,500.00 |
    | Hansung BossMonster DX9900 Silver | 14,892 | 14.90 | 739,900.00 |
    | ASUS ROG Strix G16CH Silver | 14,308 | 14.30 | 1,879,100.00 |


---
