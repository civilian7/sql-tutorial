# Beginner Exercise: Product Exploration

Uses the `products`, `categories`, and `suppliers` tables. 15 problems using a single table or simple JOINs.

---

### 1. Total Number of Products

Find the total number of registered products.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_products FROM products;
    ```

---

### 2. Top 5 Most Expensive Products

Retrieve the names and prices of the top 5 products by price in descending order.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5;
    ```

---

### 3. Products Under 100,000 KRW

Retrieve the name, brand, and price of products priced at 100,000 KRW or less, sorted by price ascending.

??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price <= 100000
    ORDER BY price ASC;
    ```

---

### 4. Out-of-Stock Products

Retrieve the name and SKU of products with zero stock.

??? success "Answer"
    ```sql
    SELECT name, sku
    FROM products
    WHERE stock_qty = 0;
    ```

---

### 5. Product Count by Brand

Count the number of products per brand and sort by product count in descending order.

??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    ORDER BY product_count DESC;
    ```

---

### 6. Discontinued Products

Retrieve the name, price, and discontinuation date of products where `discontinued_at` is not NULL.

??? success "Answer"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL
    ORDER BY discontinued_at DESC;
    ```

---

### 7. Average Price

Find the average, minimum, and maximum price of all products.

??? success "Answer"
    ```sql
    SELECT
        ROUND(AVG(price), 2) AS avg_price,
        ROUND(MIN(price), 2) AS min_price,
        ROUND(MAX(price), 2) AS max_price
    FROM products;
    ```

---

### 8. Samsung Products

Retrieve the name, price, and stock quantity of products with the brand 'Samsung'.

??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE brand = 'Samsung'
    ORDER BY price DESC;
    ```

---

### 9. Products Containing "Gaming"

Retrieve products whose name contains "Gaming".

??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE name LIKE '%Gaming%'
    ORDER BY price DESC;
    ```

---

### 10. Low Stock Products (10 or Fewer)

Retrieve the name, stock quantity, and price of active products (`is_active = 1`) with stock of 10 or fewer.

??? success "Answer"
    ```sql
    SELECT name, stock_qty, price
    FROM products
    WHERE stock_qty <= 10
      AND is_active = 1
    ORDER BY stock_qty ASC;
    ```

---

### 11. Category List

Retrieve only the top-level categories (depth = 0) sorted by display order.

??? success "Answer"
    ```sql
    SELECT id, name, slug
    FROM categories
    WHERE depth = 0
    ORDER BY sort_order;
    ```

---

### 12. Product Count by Price Range

Divide products into ranges — under 100K, 100K–500K, 500K–1M, and 1M+ KRW — and count the products in each range.

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

### 13. Supplier List

Retrieve the company name and contact person of active suppliers (`is_active = 1`).

??? success "Answer"
    ```sql
    SELECT company_name, contact_name, email
    FROM suppliers
    WHERE is_active = 1
    ORDER BY company_name;
    ```

---

### 14. Margin Rate Calculation

Calculate the margin rate (`(price - cost_price) / price * 100`) for each product and retrieve the top 10 by margin rate.

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

### 15. Average Price and Product Count by Brand

For brands with 3 or more products, find the average price and product count.

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
