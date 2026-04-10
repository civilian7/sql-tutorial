# Lesson 1: SELECT Basics

The `SELECT` statement is the foundation of SQL. It retrieves data from one or more tables, letting you specify exactly which columns to return and how they appear.

```mermaid
flowchart LR
    T["🗄️ Table\n(all rows, all columns)"] --> S["SELECT\ncolumn1, column2"] --> R["📋 Result\n(all rows, selected columns)"]
```

> **Concept:** SELECT picks only the columns you want from a table.

## SELECT All Columns

Use `SELECT *` to fetch every column from a table. This is great for quick exploration.

```sql
SELECT * FROM products;
```

**Result:**

| id | category_id | supplier_id | successor_id | name              | sku              | brand | model_number | description                             | specs                                                                                                                 | price   | cost_price | stock_qty | weight_grams | is_active | discontinued_at | created_at          | updated_at          |
| -: | ----------: | ----------: | -----------: | ----------------- | ---------------- | ----- | ------------ | --------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------: | ---------: | --------: | -----------: | --------: | --------------- | ------------------- | ------------------- |
|  1 |           7 |          20 |       (NULL) | Razer Blade 18 블랙 | LA-GAM-RAZ-00001 | Razer | RAZ-00001    | Razer Razer Blade 18 블랙 - 고성능, 최신 기술 탑재 | {"screen_size": "14 inch", "cpu": "Apple M3", "ram": "8GB", "storage": "256GB", "weight_kg": 1.7, "battery_hours": 6} | 2987500 |    3086700 |       107 |         2556 |         1 | (NULL)          | 2016-11-20 02:59:21 | 2016-11-20 02:59:21 |
| ... | ...         | ...         | ...          | ...               | ...              | ...   | ...          | ...                                     | ...                                                                                                                   | ...     | ...        | ...       | ...          | ...       | ...             | ...                 | ...                 |

> **Tip:** `SELECT *` pulls all columns, which can be slow on large tables. In production, list only the columns you need.

## SELECT Specific Columns

Listing column names returns only what you ask for — cleaner results, less data transferred.

```sql
SELECT name, price, stock_qty
FROM products;
```

**Result:**

| name                                   | price   | stock_qty |
| -------------------------------------- | ------: | --------: |
| Razer Blade 18 블랙                      | 2987500 |       107 |
| MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |       499 |
| 삼성 DDR4 32GB PC4-25600                 |   49100 |       359 |
| ...                                    | ...     | ...       |

## Column Aliases (AS)

Use `AS` to rename a column in the output. Aliases improve readability and are required when expressions would otherwise have no name.

```sql
SELECT
    name        AS product_name,
    price       AS unit_price,
    stock_qty   AS in_stock
FROM products;
```

**Result:**

| product_name                           | unit_price | in_stock |
| -------------------------------------- | ---------: | -------: |
| Razer Blade 18 블랙                      |    2987500 |      107 |
| MSI GeForce RTX 4070 Ti Super GAMING X |    1744000 |      499 |
| 삼성 DDR4 32GB PC4-25600                 |      49100 |      359 |
| ...                                    | ...        | ...      |

You can also alias expressions:

```sql
SELECT
    name,
    price * 1.1 AS price_with_tax
FROM products;
```

**Result:**

| name                                   | price_with_tax |
| -------------------------------------- | -------------: |
| Razer Blade 18 블랙                      |        3286250 |
| MSI GeForce RTX 4070 Ti Super GAMING X |        1918400 |
| ...                                    | ...            |

## DISTINCT

`DISTINCT` removes duplicate values from the result. Useful to see unique values in a column.

```sql
-- How many unique customer grades exist?
SELECT DISTINCT grade
FROM customers;
```

**Result:**

| grade  |
| ------ |
| BRONZE |
| VIP    |
| SILVER |
| GOLD   |

```sql
-- Unique gender values (including NULL)
SELECT DISTINCT gender
FROM customers;
```

**Result:**

| gender |
| ------ |
| M      |
| (NULL) |
| F      |

## Combining Techniques

```sql
-- Unique active/inactive statuses for customers
SELECT DISTINCT is_active AS status
FROM customers
ORDER BY is_active;
```

**Result:**

| status |
| -----: |
|      0 |
|      1 |

!!! note "Lesson Review"
    Quick exercises to check your understanding of this lesson. For comprehensive practice combining multiple concepts, see the [Exercises](../exercises/index.md) section.

## Practice Exercises

### Exercise 1
List every customer's `name`, `email`, and `grade`. Give the columns the aliases `full_name`, `email_address`, and `membership_tier`.

??? success "Answer"
    ```sql
    SELECT
        name        AS full_name,
        email       AS email_address,
        grade       AS membership_tier
    FROM customers;
    ```

    **Expected result:**

    | full_name | email_address     | membership_tier |
    | --------- | ----------------- | --------------- |
    | 정준호       | user1@testmail.kr | BRONZE          |
    | 김경수       | user2@testmail.kr | VIP             |
    | 김민재       | user3@testmail.kr | VIP             |
    | 진정자       | user4@testmail.kr | VIP             |
    | 이정수       | user5@testmail.kr | SILVER          |
    | ...       | ...               | ...             |


    **Expected result:**

    | full_name | email_address     | membership_tier |
    | --------- | ----------------- | --------------- |
    | 정준호       | user1@testmail.kr | BRONZE          |
    | 김경수       | user2@testmail.kr | VIP             |
    | 김민재       | user3@testmail.kr | VIP             |
    | 진정자       | user4@testmail.kr | VIP             |
    | 이정수       | user5@testmail.kr | SILVER          |
    | ...       | ...               | ...             |


### Exercise 2
Show all distinct `method` values from the `payments` table to find out which payment methods TechShop accepts.

??? success "Answer"
    ```sql
    SELECT DISTINCT method
    FROM payments;
    ```

    **Expected result:**

    | method        |
    | ------------- |
    | card          |
    | point         |
    | kakao_pay     |
    | bank_transfer |
    | naver_pay     |
    | ...           |


    **Expected result:**

    | method        |
    | ------------- |
    | card          |
    | point         |
    | kakao_pay     |
    | bank_transfer |
    | naver_pay     |
    | ...           |


### Exercise 3
Select `name`, `price`, and `stock_qty` from `products`. Add a computed column called `inventory_value` that equals `price * stock_qty`.

??? success "Answer"
    ```sql
    SELECT
        name,
        price,
        stock_qty,
        price * stock_qty AS inventory_value
    FROM products;
    ```

    **Expected result:**

    | name                                     | price   | stock_qty | inventory_value |
    | ---------------------------------------- | ------: | --------: | --------------: |
    | Razer Blade 18 블랙                        | 2987500 |       107 |       319662500 |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 |       499 |       870256000 |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 |       359 |        17626900 |
    | Dell U2724D                              |  853600 |       337 |       287663200 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 |        59 |         7711300 |
    | ...                                      | ...     | ...       | ...             |


    **Expected result:**

    | name                                     | price   | stock_qty | inventory_value |
    | ---------------------------------------- | ------: | --------: | --------------: |
    | Razer Blade 18 블랙                        | 2987500 |       107 |       319662500 |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 |       499 |       870256000 |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 |       359 |        17626900 |
    | Dell U2724D                              |  853600 |       337 |       287663200 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 |        59 |         7711300 |
    | ...                                      | ...     | ...       | ...             |


### Exercise 4
Retrieve all columns from the `categories` table.

??? success "Answer"
    ```sql
    SELECT * FROM categories;
    ```

    **Expected result:**

    | id | parent_id | name    | slug             | depth | sort_order | is_active | created_at          | updated_at          |
    | -: | --------: | ------- | ---------------- | ----: | ---------: | --------: | ------------------- | ------------------- |
    |  1 |    (NULL) | 데스크톱 PC | desktop-pc       |     0 |          1 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  2 |         1 | 완제품     | desktop-prebuilt |     1 |          1 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  3 |         1 | 조립PC    | desktop-custom   |     1 |          2 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  4 |         1 | 베어본     | desktop-barebone |     1 |          3 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  5 |    (NULL) | 노트북     | laptop           |     0 |          2 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    | ... | ...       | ...     | ...              | ...   | ...        | ...       | ...                 | ...                 |


    **Expected result:**

    | id | parent_id | name    | slug             | depth | sort_order | is_active | created_at          | updated_at          |
    | -: | --------: | ------- | ---------------- | ----: | ---------: | --------: | ------------------- | ------------------- |
    |  1 |    (NULL) | 데스크톱 PC | desktop-pc       |     0 |          1 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  2 |         1 | 완제품     | desktop-prebuilt |     1 |          1 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  3 |         1 | 조립PC    | desktop-custom   |     1 |          2 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  4 |         1 | 베어본     | desktop-barebone |     1 |          3 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    |  5 |    (NULL) | 노트북     | laptop           |     0 |          2 |         1 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
    | ... | ...       | ...     | ...              | ...   | ...        | ...       | ...                 | ...                 |


### Exercise 5
Select `name`, `department`, and `role` from the `staff` table, but rearrange the column order to `department`, `role`, `name`.

??? success "Answer"
    ```sql
    SELECT department, role, name
    FROM staff;
    ```

    **Expected result:**

    | department | role    | name |
    | ---------- | ------- | ---- |
    | 경영         | admin   | 한민재  |
    | 경영         | admin   | 장주원  |
    | 경영         | admin   | 박경수  |
    | 영업         | manager | 이준혁  |
    | 마케팅        | manager | 권영희  |


    **Expected result:**

    | department | role    | name |
    | ---------- | ------- | ---- |
    | 경영         | admin   | 한민재  |
    | 경영         | admin   | 장주원  |
    | 경영         | admin   | 박경수  |
    | 영업         | manager | 이준혁  |
    | 마케팅        | manager | 권영희  |


### Exercise 6
Find all distinct `status` values in the `orders` table.

??? success "Answer"
    ```sql
    SELECT DISTINCT status
    FROM orders;
    ```

    **Expected result:**

    | status    |
    | --------- |
    | cancelled |
    | confirmed |
    | delivered |
    | paid      |
    | pending   |
    | ...       |


    **Expected result:**

    | status    |
    | --------- |
    | cancelled |
    | confirmed |
    | delivered |
    | paid      |
    | pending   |
    | ...       |


### Exercise 7
List product `name` and `price` from `products`, and add a column `discounted_price` that shows the price after a 10% discount.

??? success "Answer"
    ```sql
    SELECT
        name,
        price,
        price * 0.9 AS discounted_price
    FROM products;
    ```

    **Expected result:**

    | name                                     | price   | discounted_price |
    | ---------------------------------------- | ------: | ---------------: |
    | Razer Blade 18 블랙                        | 2987500 |          2688750 |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 |          1569600 |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 |            44190 |
    | Dell U2724D                              |  853600 |           768240 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 |           117630 |
    | ...                                      | ...     | ...              |


    **Expected result:**

    | name                                     | price   | discounted_price |
    | ---------------------------------------- | ------: | ---------------: |
    | Razer Blade 18 블랙                        | 2987500 |          2688750 |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 |          1569600 |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 |            44190 |
    | Dell U2724D                              |  853600 |           768240 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 |           117630 |
    | ...                                      | ...     | ...              |


### Exercise 8
Select `name` and `price` from `products`, and add a string literal `'KRW'` as a column aliased `currency` on every row.

??? success "Answer"
    ```sql
    SELECT
        name,
        price,
        'KRW' AS currency
    FROM products;
    ```

    **Expected result:**

    | name                                     | price   | currency |
    | ---------------------------------------- | ------: | -------- |
    | Razer Blade 18 블랙                        | 2987500 | KRW      |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 | KRW      |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 | KRW      |
    | Dell U2724D                              |  853600 | KRW      |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 | KRW      |
    | ...                                      | ...     | ...      |


    **Expected result:**

    | name                                     | price   | currency |
    | ---------------------------------------- | ------: | -------- |
    | Razer Blade 18 블랙                        | 2987500 | KRW      |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 | KRW      |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 | KRW      |
    | Dell U2724D                              |  853600 | KRW      |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 | KRW      |
    | ...                                      | ...     | ...      |


### Exercise 9
Find all distinct combinations of `contact_name` and `company_name` from the `suppliers` table. (Use DISTINCT with multiple columns.)

??? success "Answer"
    ```sql
    SELECT DISTINCT contact_name, company_name
    FROM suppliers;
    ```

    **Expected result:**

    | contact_name | company_name |
    | ------------ | ------------ |
    | 김수민          | 삼성전자 공식 유통   |
    | 김예준          | LG전자 공식 유통   |
    | 이상현          | 인텔코리아        |
    | 강중수          | AMD코리아       |
    | 이정남          | 엔비디아코리아      |
    | ...          | ...          |


    **Expected result:**

    | contact_name | company_name |
    | ------------ | ------------ |
    | 김수민          | 삼성전자 공식 유통   |
    | 김예준          | LG전자 공식 유통   |
    | 이상현          | 인텔코리아        |
    | 강중수          | AMD코리아       |
    | 이정남          | 엔비디아코리아      |
    | ...          | ...          |


### Exercise 10
From `products`, select `name`, `price`, and `cost_price`. Add a computed column `margin` (`price - cost_price`) and another `margin_pct` (`(price - cost_price) / price * 100`).

??? success "Answer"
    ```sql
    SELECT
        name,
        price,
        cost_price,
        price - cost_price                    AS margin,
        (price - cost_price) / price * 100    AS margin_pct
    FROM products;
    ```

    **Expected result:**

    | name                                     | price   | cost_price | margin | margin_pct |
    | ---------------------------------------- | ------: | ---------: | -----: | ---------: |
    | Razer Blade 18 블랙                        | 2987500 |    3086700 | -99200 |      -3.32 |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 |    1360300 | 383700 |         22 |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 |      37900 |  11200 |      22.81 |
    | Dell U2724D                              |  853600 |     565700 | 287900 |      33.73 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 |     121400 |   9300 |       7.12 |
    | ...                                      | ...     | ...        | ...    | ...        |


    **Expected result:**

    | name                                     | price   | cost_price | margin | margin_pct |
    | ---------------------------------------- | ------: | ---------: | -----: | ---------: |
    | Razer Blade 18 블랙                        | 2987500 |    3086700 | -99200 |      -3.32 |
    | MSI GeForce RTX 4070 Ti Super GAMING X   | 1744000 |    1360300 | 383700 |         22 |
    | 삼성 DDR4 32GB PC4-25600                   |   49100 |      37900 |  11200 |      22.81 |
    | Dell U2724D                              |  853600 |     565700 | 287900 |      33.73 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz 화이트 |  130700 |     121400 |   9300 |       7.12 |
    | ...                                      | ...     | ...        | ...    | ...        |


---
Next: [Lesson 2: Filtering with WHERE](02-where.md)
