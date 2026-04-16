# JSON Applications

!!! info "Tables"

    `products` — Products (name, price, stock, brand)  

    `categories` — Categories (parent-child hierarchy)  



!!! abstract "Concepts"

    `JSON_EXTRACT`, `JSON_EACH`, `JSON_GROUP_ARRAY`, `JSON_GROUP_OBJECT`, `json_set`, `json_remove`, `JSON Path Expression`



### 1. JSON Basic Extraction — Laptop CPU List


Extract product names and CPU specifications from all active products in the Laptop category.
Products with NULL CPU specifications are excluded.


**Hint 1:** - Extract JSON internal values ​​with `json_extract(specs, '$.cpu')`
- Filter categories by JOIN with `categories` table



??? success "Answer"
    ```sql
    SELECT
        p.name        AS product_name,
        json_extract(p.specs, '$.cpu') AS cpu
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'laptop%'
      AND p.is_active = 1
      AND p.specs IS NOT NULL
    ORDER BY p.name;
    ```


    **Result** (top 7 of 22 rows)

    | product_name | cpu |
    |---|---|
    | ASUS ExpertBook B5 White | Intel Core i5-13500H |
    | ASUS ExpertBook B5 [Special Limited E... | Intel Core i9-13900H |
    | ASUS ExpertBook B5 [Special Limited E... | Intel Core i9-13900H |
    | ASUS ROG Strix Scar 16 | AMD Ryzen 7 7735HS |
    | HP EliteBook 840 G10 Black [Special L... | AMD Ryzen 7 7735HS |
    | HP EliteBook 840 G10 Silver | Apple M3 Max |
    | HP Envy x360 15 Silver | AMD Ryzen 9 7945HX |


---


### 2. JSON Multiple Field Extraction — Notebook Spec Sheet


Create a spec sheet by extracting the screen size, CPU, RAM (GB), storage capacity (GB), and battery (hours) of your laptop product at once.
Sort by price descending.


**Hint 1:** - Call `json_extract` multiple times to extract each field into a separate column
- `$.screen_size`, `$.cpu`, `$.ram_gb`, `$.storage_gb`, `$.battery_hours`



??? success "Answer"
    ```sql
    SELECT
        p.name                                     AS product_name,
        p.price,
        json_extract(p.specs, '$.screen_size')     AS screen_size,
        json_extract(p.specs, '$.cpu')             AS cpu,
        json_extract(p.specs, '$.ram_gb')          AS ram_gb,
        json_extract(p.specs, '$.storage_gb')      AS storage_gb,
        json_extract(p.specs, '$.battery_hours')   AS battery_hours
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'laptop%'
      AND p.is_active = 1
      AND p.specs IS NOT NULL
    ORDER BY p.price DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | product_name | price | screen_size | cpu | ram_gb | storage_gb | battery_hours |
    |---|---|---|---|---|---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 | 16 inch | Intel Core i9-13900H | NULL | NULL | 9 |
    | Razer Blade 18 Black | 4,353,100.00 | 14 inch | Intel Core i7-13700H | NULL | NULL | 14 |
    | Razer Blade 16 Silver | 3,702,900.00 | 16 inch | AMD Ryzen 9 7945HX | NULL | NULL | 7 |
    | Razer Blade 18 Black | 2,987,500.00 | 14 inch | Apple M3 | NULL | NULL | 6 |
    | Razer Blade 18 White | 2,483,600.00 | 14 inch | Intel Core i9-13900H | NULL | NULL | 8 |
    | ASUS ROG Strix Scar 16 | 2,452,500.00 | 15.6 inch | AMD Ryzen 7 7735HS | NULL | NULL | 14 |
    | ASUS ExpertBook B5 [Special Limited E... | 2,121,600.00 | 15.6 inch | Intel Core i9-13900H | NULL | NULL | 8 |


---


### 3. Identifying products with NULL specs


Check the distribution by category of products without specs information (NULL).
The goal is to determine which categories are missing specification information.


**Hint 1:** - `WHERE p.specs IS NULL` condition
- Aggregated by `GROUP BY` Category name



??? success "Answer"
    ```sql
    SELECT
        cat.name          AS category,
        COUNT(*)          AS no_specs_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE p.specs IS NULL
      AND p.is_active = 1
    GROUP BY cat.name
    ORDER BY no_specs_count DESC;
    ```


    **Result** (top 7 of 22 rows)

    | category | no_specs_count |
    |---|---|
    | Power Supply (PSU) | 11 |
    | Intel Socket | 10 |
    | Case | 10 |
    | Speakers/Headsets | 9 |
    | AMD Socket | 9 |
    | Switch/Hub | 8 |
    | Mechanical | 8 |


---


### 4. List JSON keys — utilizing json_each


Pick a laptop product and list all the keys included in the specs JSON.
`json_each` uses table-valued functions.


**Hint 1:** - `json_each(specs)` returns each key-value pair in a JSON object as a row
- Return columns: `key`, `value`, `type`
- Select one product with `LIMIT 1` and send it to `json_each`



??? success "Answer"
    ```sql
    SELECT
        je.key,
        je.value,
        je.type
    FROM products AS p,
         json_each(p.specs) AS je
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'laptop%'
      AND p.specs IS NOT NULL
      AND p.id = (
          SELECT MIN(p2.id) FROM products AS p2
          INNER JOIN categories AS c2 ON p2.category_id = c2.id
          WHERE c2.slug LIKE 'laptop%' AND p2.specs IS NOT NULL
      );
    ```


    **Result** (6 rows)

    | key | value | type |
    |---|---|---|
    | screen_size | 14 inch | text |
    | cpu | Apple M3 | text |
    | ram | 8GB | text |
    | storage | 256GB | text |
    | weight_kg | 1.70 | real |
    | battery_hours | 6 | integer |


---


### 5. JSON Condition Filtering — Finding High-Performance Laptops


Look for a laptop with at least 32GB of RAM and at least 1024GB of storage.
Displays product name, price, RAM, and storage capacity.


**Hint 1:** - Use JSON value as condition in WHERE clause like `json_extract(specs, '$.ram_gb') >= 32`
- Values ​​extracted from JSON are automatically converted to the appropriate type.



??? success "Answer"
    ```sql
    SELECT
        p.name       AS product_name,
        p.price,
        json_extract(p.specs, '$.ram_gb')      AS ram_gb,
        json_extract(p.specs, '$.storage_gb')  AS storage_gb,
        json_extract(p.specs, '$.cpu')         AS cpu
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'laptop%'
      AND p.is_active = 1
      AND p.specs IS NOT NULL
      AND json_extract(p.specs, '$.ram_gb') >= 32
      AND json_extract(p.specs, '$.storage_gb') >= 1024
    ORDER BY p.price DESC;
    ```


---


### 6. JSON-based group aggregation — average price by CPU


Find the average price and number of products by CPU specification for laptops and desktops.
Shows only CPUs with 3 or more products.


**Hint 1:** - Use `json_extract(specs, '$.cpu')` for `GROUP BY`
- Exclude minority groups with `HAVING COUNT(*) >= 3`



??? success "Answer"
    ```sql
    SELECT
        json_extract(p.specs, '$.cpu')     AS cpu,
        COUNT(*)                           AS product_count,
        ROUND(AVG(p.price))                AS avg_price,
        MIN(p.price)                       AS min_price,
        MAX(p.price)                       AS max_price
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE (cat.slug LIKE 'laptop%' OR cat.slug LIKE 'desktop%')
      AND p.is_active = 1
      AND p.specs IS NOT NULL
    GROUP BY json_extract(p.specs, '$.cpu')
    HAVING COUNT(*) >= 3
    ORDER BY avg_price DESC;
    ```


    **Result** (5 rows)

    | cpu | product_count | avg_price | min_price | max_price |
    |---|---|---|---|---|
    | Intel Core i9-13900H | 6 | 2,500,767.00 | 1,179,900.00 | 5,481,100.00 |
    | AMD Ryzen 9 7945HX | 4 | 2,077,100.00 | 1,214,600.00 | 3,702,900.00 |
    | Apple M3 | 4 | 1,800,425.00 | 1,345,900.00 | 2,987,500.00 |
    | Intel Core i5-13600K | 3 | 1,581,033.00 | 1,093,200.00 | 1,849,900.00 |
    | AMD Ryzen 5 7600X | 4 | 1,532,125.00 | 739,900.00 | 3,671,500.00 |


---


### 7. JSON-based statistics — Analysis by monitor panel type


In the monitor category, tally the number of products, average price, and average refresh rate by panel type (IPS/VA/OLED).
Also check the resolution distribution of each panel type.


**Hint 1:** - Use `json_extract(specs, '$.panel')`, `json_extract(specs, '$.refresh_rate')`
- Resolution distribution is processed as a separate query or conditional aggregation (`CASE WHEN`)



??? success "Answer"
    ```sql
    SELECT
        json_extract(p.specs, '$.panel')          AS panel_type,
        COUNT(*)                                   AS product_count,
        ROUND(AVG(p.price))                        AS avg_price,
        ROUND(AVG(json_extract(p.specs, '$.refresh_rate'))) AS avg_refresh_rate,
        SUM(CASE WHEN json_extract(p.specs, '$.resolution') = 'FHD' THEN 1 ELSE 0 END) AS fhd_count,
        SUM(CASE WHEN json_extract(p.specs, '$.resolution') = 'QHD' THEN 1 ELSE 0 END) AS qhd_count,
        SUM(CASE WHEN json_extract(p.specs, '$.resolution') = '4K'  THEN 1 ELSE 0 END) AS uhd_4k_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'monitor%'
      AND p.is_active = 1
      AND p.specs IS NOT NULL
    GROUP BY json_extract(p.specs, '$.panel')
    ORDER BY avg_price DESC;
    ```


    **Result** (3 rows)

    | panel_type | product_count | avg_price | avg_refresh_rate | fhd_count | qhd_count | uhd_4k_count |
    |---|---|---|---|---|---|---|
    | VA | 6 | 1,668,967.00 | 135.00 | 0 | 3 | 3 |
    | OLED | 7 | 986,571.00 | 131.00 | 4 | 2 | 1 |
    | IPS | 8 | 785,600.00 | 114.00 | 3 | 4 | 1 |


---


### 8. Modifying JSON value with json_set (within SELECT)


Use SQLite's `json_set` function to check the result of adding the `"warranty_years": 3` field to the laptop product's specs.
Preview the converted JSON from a SELECT, not an actual UPDATE.


**Hint 1:** - `json_set(specs, '$.warranty_years', 3)` adds a new key to an existing JSON
- If the key already exists, the value is overwritten.
- It is checked only in SELECT, so the actual data is not changed



??? success "Answer"
    ```sql
    SELECT
        p.name         AS product_name,
        p.specs        AS original_specs,
        json_set(p.specs, '$.warranty_years', 3) AS modified_specs
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'laptop%'
      AND p.specs IS NOT NULL
    LIMIT 3;
    ```


    **Result** (3 rows)

    | product_name | original_specs | modified_specs |
    |---|---|---|
    | Razer Blade 18 Black | {"screen_size": "14 inch", "cpu": "Ap... | {"screen_size":"14 inch","cpu":"Apple... |
    | Razer Blade 18 White | {"screen_size": "14 inch", "cpu": "In... | {"screen_size":"14 inch","cpu":"Intel... |
    | HP Envy x360 15 Silver | {"screen_size": "15.6 inch", "cpu": "... | {"screen_size":"15.6 inch","cpu":"AMD... |


---


### 9. Removing a JSON key with json_remove (within a SELECT)


Compare the original with the result of removing the `tdp_watts` key from the GPU product's specs.
Use the `json_remove` function.


**Hint 1:** - `json_remove(specs, '$.tdp_watts')` returns JSON with the specified key removed
- Display `specs` and `json_remove(...)` results side by side for comparison with the original



??? success "Answer"
    ```sql
    SELECT
        p.name        AS product_name,
        p.specs       AS original_specs,
        json_remove(p.specs, '$.tdp_watts') AS specs_without_tdp
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE cat.slug LIKE 'gpu%'
      AND p.specs IS NOT NULL
    LIMIT 5;
    ```


    **Result** (5 rows)

    | product_name | original_specs | specs_without_tdp |
    |---|---|---|
    | MSI GeForce RTX 4070 Ti Super GAMING X | {"vram": "12GB", "clock_mhz": 2447, "... | {"vram":"12GB","clock_mhz":2447} |
    | MSI Radeon RX 9070 VENTUS 3X White | {"vram": "16GB", "clock_mhz": 1946, "... | {"vram":"16GB","clock_mhz":1946} |
    | ASUS TUF Gaming RTX 5080 White | {"vram": "24GB", "clock_mhz": 2177, "... | {"vram":"24GB","clock_mhz":2177} |
    | MSI Radeon RX 7900 XTX GAMING X White | {"vram": "12GB", "clock_mhz": 1587, "... | {"vram":"12GB","clock_mhz":1587} |
    | Gigabyte RTX 5090 AERO OC | {"vram": "8GB", "clock_mhz": 2283, "t... | {"vram":"8GB","clock_mhz":2283} |


---


### 10. Comprehensive JSON analysis — Specification comparison report by category


Analyze product specs for all categories to find a list of unique keys included in JSON for each category and the occurrence rate of each key.
This report allows you to see at a glance what specification information exists in which category.


**Hint 1:** - Spread all keys into rows with `json_each(specs)`, then GROUP BY with category + key combination
- Appearance rate = Number of products with that key / Total number of products in the category
- Step by step aggregation using CTEs



??? success "Answer"
    ```sql
    WITH spec_keys AS (
        SELECT
            cat.name       AS category,
            je.key,
            COUNT(*)       AS key_count
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id,
             json_each(p.specs) AS je
        WHERE p.specs IS NOT NULL
          AND p.is_active = 1
        GROUP BY cat.name, je.key
    ),
    category_totals AS (
        SELECT
            cat.name       AS category,
            COUNT(*)       AS total_products
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.specs IS NOT NULL
          AND p.is_active = 1
        GROUP BY cat.name
    )
    SELECT
        sk.category,
        sk.key               AS spec_key,
        sk.key_count,
        ct.total_products,
        ROUND(100.0 * sk.key_count / ct.total_products, 1) AS presence_pct
    FROM spec_keys AS sk
    INNER JOIN category_totals AS ct ON sk.category = ct.category
    ORDER BY sk.category, sk.key_count DESC;
    ```


    **Result** (top 7 of 68 rows)

    | category | spec_key | key_count | total_products | presence_pct |
    |---|---|---|---|---|
    | 2-in-1 | battery_hours | 7 | 7 | 100.00 |
    | 2-in-1 | cpu | 7 | 7 | 100.00 |
    | 2-in-1 | ram | 7 | 7 | 100.00 |
    | 2-in-1 | screen_size | 7 | 7 | 100.00 |
    | 2-in-1 | storage | 7 | 7 | 100.00 |
    | 2-in-1 | weight_kg | 7 | 7 | 100.00 |
    | AMD | clock_mhz | 6 | 8 | 75.00 |


---
