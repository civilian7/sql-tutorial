# Product Exploration

!!! info "Tables"

    `categories` — Categories (parent-child hierarchy)  

    `products` — Products (name, price, stock, brand)  

    `suppliers` — Suppliers (company, contact)  



!!! abstract "Concepts"

    `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `COUNT`, `AVG`, `MIN`, `MAX`, `GROUP BY`, `HAVING`, `LIKE`, `CASE WHEN`, `IS NOT NULL`



### 1. Find the total number of registered products.


Find the total number of registered products.


**Hint 1:** Use the COUNT(*) aggregate function


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_products FROM products;
    ```


    **Result** (1 rows)

    | total_products |
    |---|
    | 280 |


---


### 2. Retrieve the names and prices of the top 5 products by price


Retrieve the names and prices of the top 5 products by price in descending order.


**Hint 1:** Sort with ORDER BY price DESC and retrieve only the top 5 with LIMIT 5


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


### 3. Retrieve the name, brand, and price of products priced at 10


Retrieve the name, brand, and price of products priced at 100,000 KRW or less, sorted by price ascending.


**Hint 1:** Use the WHERE price <= 100000 condition and ORDER BY price ASC


??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price <= 100000
    ORDER BY price ASC;
    ```


    **Result** (top 7 of 48 rows)

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


### 4. Retrieve the name and SKU of products with zero stock.


Retrieve the name and SKU of products with zero stock.


**Hint 1:** Filter with the WHERE stock_qty = 0 condition


??? success "Answer"
    ```sql
    SELECT name, sku
    FROM products
    WHERE stock_qty = 0;
    ```


    **Result** (1 rows)

    | name | sku |
    |---|---|
    | Arctic Freezer 36 A-RGB White | CO-AIR-ARC-00049 |


---


### 5. Count the number of products per brand and sort by product c


Count the number of products per brand and sort by product count in descending order.


**Hint 1:** Group with GROUP BY brand and count with COUNT(*). Sort with ORDER BY ... DESC


??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    ORDER BY product_count DESC;
    ```


    **Result** (top 7 of 55 rows)

    | brand | product_count |
    |---|---|
    | ASUS | 26 |
    | Samsung | 25 |
    | Logitech | 17 |
    | MSI | 13 |
    | TP-Link | 11 |
    | LG | 11 |
    | ASRock | 11 |


---


### 6. Retrieve the name, price, and discontinuation date of produc


Retrieve the name, price, and discontinuation date of products where discontinued_at is not NULL.


**Hint 1:** Use IS NOT NULL to filter only rows that are not NULL


??? success "Answer"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL
    ORDER BY discontinued_at DESC;
    ```


    **Result** (top 7 of 62 rows)

    | name | price | discontinued_at |
    |---|---|---|
    | Dell XPS Desktop 8960 Silver | 1,249,400.00 | 2025-11-20 15:30:12 |
    | Kingston FURY Beast DDR4 16GB White | 91,200.00 | 2025-11-18 04:06:13 |
    | Intel Core Ultra 7 265K | 196,300.00 | 2025-11-16 21:11:33 |
    | Hansung BossMonster DX7700 White | 1,579,400.00 | 2025-10-25 03:47:01 |
    | Intel Core Ultra 7 265K White | 170,200.00 | 2025-08-24 00:34:53 |
    | SAPPHIRE PULSE RX 7800 XT Silver | 1,146,300.00 | 2025-08-01 06:10:51 |
    | SteelSeries Arctis Nova Pro Wireless ... | 173,700.00 | 2025-06-27 12:36:27 |


---


### 7. Find the average, minimum, and maximum price of all products


Find the average, minimum, and maximum price of all products.


**Hint 1:** Use the AVG(), MIN(), and MAX() aggregate functions together. Use ROUND() to format decimals


??? success "Answer"
    ```sql
    SELECT
        ROUND(AVG(price), 2) AS avg_price,
        ROUND(MIN(price), 2) AS min_price,
        ROUND(MAX(price), 2) AS max_price
    FROM products;
    ```


    **Result** (1 rows)

    | avg_price | min_price | max_price |
    |---|---|---|
    | 649,272.50 | 18,500.00 | 5,481,100.00 |


---


### 8. Retrieve the name, price, and stock quantity of products wit


Retrieve the name, price, and stock quantity of products with the brand 'Samsung'.


**Hint 1:** Use the WHERE brand = 'Samsung' condition. Strings are enclosed in single quotes


??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE brand = 'Samsung'
    ORDER BY price DESC;
    ```


    **Result** (top 7 of 25 rows)

    | name | price | stock_qty |
    |---|---|---|
    | Samsung Odyssey G5 27 Black | 1,833,000.00 | 372 |
    | Samsung Galaxy Book5 Pro Black | 1,739,900.00 | 362 |
    | Samsung Galaxy Book4 360 Black | 1,388,600.00 | 261 |
    | Samsung Galaxy Book4 360 Black | 1,267,000.00 | 153 |
    | Samsung Odyssey OLED G8 | 1,205,700.00 | 254 |
    | Samsung Odyssey OLED G8 | 1,199,600.00 | 241 |
    | Samsung Galaxy Book5 360 Black | 1,179,900.00 | 216 |


---


### 9. Retrieve products whose name contains "Gaming".


Retrieve products whose name contains "Gaming".


**Hint 1:** Use LIKE '%Gaming%' to search for a substring. % represents any sequence of characters


??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE name LIKE '%Gaming%'
    ORDER BY price DESC;
    ```


    **Result** (5 rows)

    | name | brand | price |
    |---|---|---|
    | ASUS TUF Gaming RTX 5080 White | ASUS | 4,526,600.00 |
    | MSI Radeon RX 9070 XT GAMING X | MSI | 1,896,000.00 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | MSI | 1,744,000.00 |
    | MSI Radeon RX 7900 XTX GAMING X White | MSI | 1,517,600.00 |
    | APC Back-UPS Pro Gaming BGM1500B Black | APC | 516,300.00 |


---


### 10. Retrieve the name, stock quantity, and price of active produ


Retrieve the name, stock quantity, and price of active products (is_active = 1) with stock of 10 or fewer.


**Hint 1:** Combine two conditions in the WHERE clause with AND: stock_qty <= 10 AND is_active = 1


??? success "Answer"
    ```sql
    SELECT name, stock_qty, price
    FROM products
    WHERE stock_qty <= 10
      AND is_active = 1
    ORDER BY stock_qty ASC;
    ```


    **Result** (3 rows)

    | name | stock_qty | price |
    |---|---|---|
    | Arctic Freezer 36 A-RGB White | 0 | 23,000.00 |
    | Samsung SPA-KFG0BUB | 4 | 30,700.00 |
    | Logitech G502 HERO Silver | 8 | 71,100.00 |


---


### 11. Retrieve only the top-level categories (depth = 0) sorted by


Retrieve only the top-level categories (depth = 0) sorted by display order.


**Hint 1:** Filter with WHERE depth = 0 from the categories table


??? success "Answer"
    ```sql
    SELECT id, name, slug
    FROM categories
    WHERE depth = 0
    ORDER BY sort_order;
    ```


    **Result** (top 7 of 18 rows)

    | id | name | slug |
    |---|---|---|
    | 1 | Desktop PC | desktop-pc |
    | 5 | Laptop | laptop |
    | 10 | Monitor | monitor |
    | 14 | CPU | cpu |
    | 17 | Motherboard | motherboard |
    | 20 | Memory (RAM) | ram |
    | 23 | Storage | storage |


---


### 12. Divide products into ranges -- under 100K, 100K-500K, 500K-1


Divide products into ranges -- under 100K, 100K-500K, 500K-1M, and 1M+ KRW -- and count the products in each range.


**Hint 1:** Classify price ranges with CASE WHEN, then aggregate with GROUP BY and COUNT(*)


??? success "Answer"
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


    **Result** (4 rows)

    | price_range | product_count |
    |---|---|
    | 10만원 미만 | 47 |
    | 10~50만원 | 130 |
    | 50~100만원 | 38 |
    | 100만원 이상 | 65 |


---


### 13. Retrieve the company name and contact person of active suppl


Retrieve the company name and contact person of active suppliers (is_active = 1).


**Hint 1:** Filter with WHERE is_active = 1 from the suppliers table


??? success "Answer"
    ```sql
    SELECT company_name, contact_name, email
    FROM suppliers
    WHERE is_active = 1
    ORDER BY company_name;
    ```


    **Result** (top 7 of 56 rows)

    | company_name | contact_name | email |
    |---|---|---|
    | ABKO | Barry Hensley | contact@supplier15.test.com |
    | ADATA Corp. | Heather Chavez | contact@supplier38.test.com |
    | AMD Corp. | Michael Miles | contact@amd.test.com |
    | APC Corp. | Christopher Parker | contact@apc.test.com |
    | ASRock Corp. | Adam Ballard | contact@asrock.test.com |
    | ASUS Corp. | Carrie Carroll | contact@supplier25.test.com |
    | Absolute Technology | Katherine Davis | contact@supplier45.test.com |


---


### 14. Calculate the margin rate ((price - cost_price) / price * 10


Calculate the margin rate ((price - cost_price) / price * 100) for each product and retrieve the top 10 by margin rate.


**Hint 1:** Calculate the margin rate using arithmetic in the SELECT clause. Use ROUND() for decimal formatting and price > 0 to prevent division by zero


??? success "Answer"
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


    **Result** (top 7 of 10 rows)

    | name | price | cost_price | margin_pct |
    |---|---|---|---|
    | Norton AntiVirus Plus | 69,700.00 | 28,200.00 | 59.50 |
    | Norton AntiVirus Plus Silver | 74,800.00 | 32,400.00 | 56.70 |
    | Adobe Creative Cloud 1-Year Silver | 327,300.00 | 147,300.00 | 55.00 |
    | Windows 11 Pro Silver | 423,000.00 | 198,800.00 | 53.00 |
    | Hancom Office 2024 Enterprise Silver | 241,400.00 | 116,400.00 | 51.80 |
    | Microsoft Office 2024 Home | 114,300.00 | 57,200.00 | 50.00 |
    | Logitech G502 HERO Silver | 71,100.00 | 36,500.00 | 48.70 |


---


### 15. For brands with 3 or more products, find the average price a


For brands with 3 or more products, find the average price and product count.


**Hint 1:** After GROUP BY brand, use HAVING COUNT(*) >= 3 to filter groups. HAVING filters after aggregation


??? success "Answer"
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


    **Result** (top 7 of 34 rows)

    | brand | product_count | avg_price | min_price | max_price |
    |---|---|---|---|---|
    | Razer | 9 | 1,764,888.89 | 52,500.00 | 4,353,100.00 |
    | ASUS | 26 | 1,683,630.77 | 47,200.00 | 4,526,600.00 |
    | Lenovo | 5 | 1,597,760.00 | 1,389,800.00 | 1,866,100.00 |
    | HP | 6 | 1,479,016.67 | 895,000.00 | 2,080,300.00 |
    | Jooyon Tech | 4 | 1,413,550.00 | 810,300.00 | 1,849,900.00 |
    | LG | 11 | 1,346,836.36 | 308,900.00 | 1,828,800.00 |
    | Hansung Computer | 4 | 1,104,075.00 | 739,900.00 | 1,579,400.00 |


---
