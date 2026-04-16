# Product Exploration

**Tables:** `categories`, `products`, `suppliers`

**Concepts:** SELECT, WHERE, ORDER BY, LIMIT, COUNT, AVG, MIN, MAX, GROUP BY, HAVING, LIKE, CASE WHEN, IS NOT NULL


---


### 1. Find the total number of registered products.


Find the total number of registered products.


**Hint 1:** Use the COUNT(*) aggregate function


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_products FROM products;
    ```


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


---
