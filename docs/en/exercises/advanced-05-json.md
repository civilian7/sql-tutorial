# JSON Applications

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `products` — products (name, price, stock, brand)<br>
    `categories` — Category (parent-child hierarchy)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    `JSON_EXTRACT`<br>
    `JSON_EACH`<br>
    `JSON_GROUP_ARRAY`<br>
    `JSON_GROUP_OBJECT`<br>
    JSON path expression<br>
    Using the specs column

</div>

Practice what you learned in Lecture 25, JSON Function.
The `specs` column of the products table stores specification information for each category as a JSON string.

!!! info "specs column JSON example"
    - Laptop: `{"screen_size":"15.6 inch","cpu":"Intel Core i7-13700H","ram_gb":16,"storage_gb":512,"battery_hours":10}`
    - Desktop: `{"cpu":"AMD Ryzen 7 7700X","ram_gb":32,"storage_gb":1024,"gpu":"RTX 4070"}`
    - Monitor: `{"screen_size":"27 inch","resolution":"QHD","refresh_rate":144,"panel":"IPS"}`
    - GPU: `{"vram":"16GB","clock_mhz":2100,"tdp_watts":300}`
    - CPU: `{"cores":8,"threads":16,"base_clock_ghz":3.5,"boost_clock_ghz":5.1}`
    - Memory: `{"capacity_gb":16,"speed_mhz":5600,"type":"DDR5"}`
    - Storage device: `{"capacity_gb":1024,"interface":"NVMe","read_mbps":7000,"write_mbps":5000}`

---


### Problem 1. JSON Basic Extraction — Laptop CPU List

Extract product names and CPU specifications from all active products in the Laptop category.
Products with NULL CPU specifications are excluded.


??? tip "Hint"
    - Extract JSON internal values ​​with `json_extract(specs, '$.cpu')`
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

    | product_name | cpu |
    |---|---|
    | (laptop product name) | Intel Core i7-13700H |
    | ... | ... |


---


### Problem 2. JSON Multiple Field Extraction — Notebook Spec Sheet

Create a spec sheet by extracting the screen size, CPU, RAM (GB), storage capacity (GB), and battery (hours) of your laptop product at once.
Sort by price descending.


??? tip "Hint"
    - Call `json_extract` multiple times to extract each field into a separate column
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

    | product_name | price | screen_size | cpu | ram_gb | storage_gb | battery_hours |
    |---|---|---|---|---|---|---|
    | (laptop name) | 2500000 | 16 inch | Intel Core i9-13900H | 32 | 1024 | 12 |
    | ... | ... | ... | ... | ... | ... | ... |


---


### Problem 3. Identifying products with NULL specs

Check the distribution by category of products without specs information (NULL).
The goal is to determine which categories are missing specification information.


??? tip "Hint"
    - `WHERE p.specs IS NULL` condition
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

    | category | no_specs_count |
    |---|---|
    | (peripheral category) | 45 |
    | ... | ... |


---


### Problem 4. List JSON keys — utilizing json_each

Pick a laptop product and list all the keys included in the specs JSON.
`json_each` uses table-valued functions.


??? tip "Hint"
    - `json_each(specs)` returns each key-value pair in a JSON object as a row
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

    | key | value | type |
    |---|---|---|
    | screen_size | 15.6 inch | text |
    | cpu | Intel Core i7-13700H | text |
    | ram_gb | 16 | integer |
    | storage_gb | 512 | integer |
    | battery_hours | 10 | integer |


---


### Problem 5. JSON Condition Filtering — Finding High-Performance Laptops

Look for a laptop with at least 32GB of RAM and at least 1024GB of storage.
Displays product name, price, RAM, and storage capacity.


??? tip "Hint"
    - Use JSON value as condition in WHERE clause like `json_extract(specs, '$.ram_gb') >= 32`
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

    | product_name | price | ram_gb | storage_gb | cpu |
    |---|---|---|---|---|
    | (high-spec laptop) | 3200000 | 32 | 1024 | Intel Core i9-13900H |
    | ... | ... | ... | ... | ... |


---


### Problem 6. JSON-based group aggregation — average price by CPU

Find the average price and number of products by CPU specification for laptops and desktops.
Shows only CPUs with 3 or more products.


??? tip "Hint"
    - Use `json_extract(specs, '$.cpu')` for `GROUP BY`
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

    | cpu | product_count | avg_price | min_price | max_price |
    |---|---|---|---|---|
    | Intel Core i9-13900H | 5 | 2800000 | 2200000 | 3500000 |
    | AMD Ryzen 9 7950X | 4 | 2500000 | 2000000 | 3000000 |
    | ... | ... | ... | ... | ... |


---


### Problem 7. JSON-based statistics — Analysis by monitor panel type

In the monitor category, tally the number of products, average price, and average refresh rate by panel type (IPS/VA/OLED).
Also check the resolution distribution of each panel type.


??? tip "Hint"
    - Use `json_extract(specs, '$.panel')`, `json_extract(specs, '$.refresh_rate')`
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

    | panel_type | product_count | avg_price | avg_refresh_rate | fhd_count | qhd_count | uhd_4k_count |
    |---|---|---|---|---|---|---|
    | OLED | 8 | 950000 | 165 | 0 | 3 | 5 |
    | IPS | 25 | 450000 | 120 | 8 | 10 | 7 |
    | VA | 12 | 380000 | 100 | 5 | 5 | 2 |


---


### Problem 8. Modifying JSON value with json_set (within SELECT)

Use SQLite's `json_set` function to check the result of adding the `"warranty_years": 3` field to the laptop product's specs.
Preview the converted JSON from a SELECT, not an actual UPDATE.


??? tip "Hint"
    - `json_set(specs, '$.warranty_years', 3)` adds a new key to an existing JSON
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

    | product_name | original_specs | modified_specs |
    |---|---|---|
    | (laptop name) | {"screen_size":"15.6 inch",...} | {"screen_size":"15.6 inch",...,"warranty_years":3} |


---


### Problem 9. Removing a JSON key with json_remove (within a SELECT)

Compare the original with the result of removing the `tdp_watts` key from the GPU product's specs.
Use the `json_remove` function.


??? tip "Hint"
    - `json_remove(specs, '$.tdp_watts')` returns JSON with the specified key removed
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

    | product_name | original_specs | specs_without_tdp |
    |---|---|---|
    | (GPU name) | {"vram":"16GB","clock_mhz":2100,"tdp_watts":300} | {"vram":"16GB","clock_mhz":2100} |


---


### Problem 10. Comprehensive JSON analysis — Specification comparison report by category

Analyze product specs for all categories to find a list of unique keys included in JSON for each category and the occurrence rate of each key.
This report allows you to see at a glance what specification information exists in which category.


??? tip "Hint"
    - Spread all keys into rows with `json_each(specs)`, then GROUP BY with category + key combination
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

    | category | spec_key | key_count | total_products | presence_pct |
    |---|---|---|---|---|
    | Laptop | cpu | 50 | 50 | 100.0 |
    | Laptop | ram_gb | 50 | 50 | 100.0 |
    | Laptop | screen_size | 50 | 50 | 100.0 |
    | Monitor | panel | 45 | 45 | 100.0 |
    | Monitor | resolution | 45 | 45 | 100.0 |
    | ... | ... | ... | ... | ... |
