# JOIN Master

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `orders` — Orders<br>
    `customers` — Customers<br>
    `order_items` — Order details<br>
    `products` — Products<br>
    `categories` — Categories<br>
    `suppliers` — Suppliers<br>
    `shipping` — Shipping<br>
    `reviews` — Reviews<br>
    `staff` — Staff<br>
    `wishlists` — Wishlists<br>
    `complaints` — Complaints<br>
    `product_tags` — Product tags<br>
    `tags` — Tags<br>
    `product_qna` — Product Q&A<br>
    `calendar` — Date reference

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    `INNER JOIN`<br>
    `LEFT JOIN`<br>
    anti-join<br>
    Multi-table JOIN<br>
    Self-JOIN<br>
    JOIN + `GROUP BY` + aggregation

</div>

!!! info "Before You Begin"
    This exercise applies what you learned in **Intermediate Lessons 8~9** (INNER JOIN, LEFT JOIN) to practical scenarios.
    GROUP BY, aggregate functions, ORDER BY, and LIMIT are also used together.

---

## Basic (1~8)

Practice two-table INNER JOIN.

---

### Problem 1

**Find each product's name, price, and category name. Top 10 by price descending.**

??? tip "Hint"
    `INNER JOIN` `products` and `categories` on `category_id`, then `ORDER BY price DESC LIMIT 10`.

??? success "Answer"
    ```sql
    SELECT p.name, p.price, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    ORDER BY p.price DESC
    LIMIT 10;
    ```

    **Result (10행):**

    | name | price | category |
    | ---------- | ----------: | ---------- |
    | MacBook Air 15 M3 Silver | 5481100.0 | MacBook |
    | ASUS TUF Gaming RTX 5080 White | 4526600.0 | NVIDIA |
    | ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 4496700.0 | NVIDIA |
    | Razer Blade 18 Black | 4353100.0 | Gaming Laptop |
    | Razer Blade 16 Silver | 3702900.0 | Gaming Laptop |
    | ASUS ROG Strix G16CH White | 3671500.0 | Custom Build |
    | ASUS ROG Zephyrus G16 | 3429900.0 | Gaming Laptop |
    | ASUS ROG Strix GT35 | 3296800.0 | Custom Build |
    | ... | ... | ... |

    > Only top 5 rows shown. 10 rows returned total.

---

### Problem 2

**Find product name, category name, and supplier name together. Top 20 sorted alphabetically by product name.**

??? tip "Hint"
    `INNER JOIN` both `categories` and `suppliers` from `products`. You can use JOIN twice in a single SELECT.

??? success "Answer"
    ```sql
    SELECT
        p.name AS product,
        cat.name AS category,
        s.company_name AS supplier
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    ORDER BY p.name
    LIMIT 20;
    ```

    **Result (top 5 rows):**

    | product | category | supplier |
    | ---------- | ---------- | ---------- |
    | AMD Ryzen 9 9900X | AMD | AMD Corp. |
    | AMD Ryzen 9 9900X | AMD | AMD Corp. |
    | APC Back-UPS Pro Gaming BGM1500B Black | UPS/Power | APC Corp. |
    | ASRock B850M Pro RS Black | AMD Socket | ASRock Corp. |
    | ASRock B850M Pro RS Silver | AMD Socket | ASRock Corp. |
    | ASRock B850M Pro RS White | AMD Socket | ASRock Corp. |
    | ASRock B860M Pro RS Silver | Intel Socket | ASRock Corp. |
    | ASRock B860M Pro RS White | Intel Socket | ASRock Corp. |
    | ... | ... | ... |

---

### Problem 3

**Find customer name and order amount per order. Most recent 10 orders only.**

??? tip "Hint"
    JOIN `orders` and `customers` on `customer_id`. `ORDER BY ordered_at DESC LIMIT 10`.

??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer_name,
        o.total_amount,
        o.ordered_at
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    ORDER BY o.ordered_at DESC
    LIMIT 10;
    ```

    **Result (top 5 rows):**

    | order_number | customer_name | total_amount | ordered_at |
    | ---------- | ---------- | ----------: | ---------- |
    | ORD-20251231-37555 | Angel Jones | 74800.0 | 2025-12-31 22:25:39 |
    | ORD-20251231-37543 | Carla Watson | 134100.0 | 2025-12-31 21:40:27 |
    | ORD-20251231-37552 | Martin Hanson | 254300.0 | 2025-12-31 20:00:48 |
    | ORD-20251231-37548 | Lucas Johnson | 187700.0 | 2025-12-31 18:43:56 |
    | ORD-20251231-37542 | Adam Moore | 155700.0 | 2025-12-31 18:00:24 |
    | ORD-20251231-37546 | Justin Murphy | 198300.0 | 2025-12-31 15:43:23 |
    | ORD-20251231-37547 | Sara Hill | 335000.0 | 2025-12-31 15:33:05 |
    | ORD-20251231-37556 | David York | 153900.0 | 2025-12-31 15:08:54 |
    | ... | ... | ... | ... |

    > Actual names and amounts depend on the data.

---

### Problem 4

**Combine order details (order_items) with product info to find product name, quantity, and unit price per order item. Most recent 15.**

??? tip "Hint"
    JOIN `order_items` and `products` on `product_id`. `ORDER BY oi.id DESC LIMIT 15`.

??? success "Answer"
    ```sql
    SELECT
        oi.order_id,
        p.name AS product_name,
        p.brand,
        oi.quantity,
        oi.unit_price
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    ORDER BY oi.id DESC
    LIMIT 15;
    ```

    **Result (top 5 rows):**

    | order_id | product_name | brand | quantity | unit_price |
    | ----------: | ---------- | ---------- | ----------: | ----------: |
    | 37557 | NZXT H7 Flow Silver | NZXT | 1 | 248700.0 |
    | 37557 | TeamGroup T-Force Vulcan DDR5 32GB 5200MHz | TeamGroup | 1 | 139800.0 |
    | 37556 | Ducky One 3 Full Black | Ducky | 1 | 153900.0 |
    | 37555 | Norton AntiVirus Plus Silver | Norton | 1 | 74800.0 |
    | 37554 | ASUS PCE-BE92BT Black | ASUS | 1 | 74900.0 |
    | 37553 | Logitech G PRO X2 Superstrike Black | Logitech | 1 | 155700.0 |
    | 37553 | Netgear GS308 Silver | Netgear | 1 | 194800.0 |
    | 37552 | NZXT Kraken 240 Silver | NZXT | 1 | 120200.0 |
    | ... | ... | ... | ... | ... |

    > Actual results depend on the data.

---

### Problem 5

**Find order number, carrier, and delivery date for delivered orders. Top 10 by most recent delivery.**

??? tip "Hint"
    JOIN `shipping` and `orders` on `order_id`. `WHERE sh.status = 'delivered'`.

??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        sh.carrier,
        sh.delivered_at
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE sh.status = 'delivered'
    ORDER BY sh.delivered_at DESC
    LIMIT 10;
    ```

    **Result (top 5 rows):**

    | order_number | carrier | delivered_at |
    | ---------- | ---------- | ---------- |
    | ORD-20251225-37399 | USPS | 2026-01-01 23:36:22 |
    | ORD-20251225-37404 | UPS | 2026-01-01 22:02:51 |
    | ORD-20251225-37414 | FedEx | 2026-01-01 13:49:43 |
    | ORD-20251225-37413 | OnTrac | 2025-12-31 14:25:31 |
    | ORD-20251225-37412 | OnTrac | 2025-12-30 22:50:46 |
    | ORD-20251224-37387 | OnTrac | 2025-12-30 19:29:43 |
    | ORD-20251225-37401 | UPS | 2025-12-30 12:03:50 |
    | ORD-20251224-37396 | UPS | 2025-12-30 09:46:21 |
    | ... | ... | ... |

---

### Problem 6

**Combine reviews with product info to find product name, review title, and date for 5-star reviews. Most recent 10.**

??? tip "Hint"
    JOIN `reviews` and `products` on `product_id`. `WHERE r.rating = 5`.

??? success "Answer"
    ```sql
    SELECT
        p.name AS product_name,
        r.title AS review_title,
        r.rating,
        r.created_at
    FROM reviews AS r
    INNER JOIN products AS p ON r.product_id = p.id
    WHERE r.rating = 5
    ORDER BY r.created_at DESC
    LIMIT 10;
    ```

    **Result (top 5 rows):**

    | product_name | review_title | rating | created_at |
    | ---------- | ---------- | ----------: | ---------- |
    | Norton AntiVirus Plus Silver | Outstanding | 5 | 2026-01-13 12:09:18 |
    | Netgear GS308 Silver | Perfect | 5 | 2026-01-11 21:02:15 |
    | Arctic Liquid Freezer III Pro 420 A-RGB Silver | Best Value | 5 | 2026-01-07 20:55:20 |
    | ASUS Dual RTX 5070 Ti Silver | Outstanding | 5 | 2026-01-07 09:24:04 |
    | be quiet! Dark Power 13 1000W | (NULL) | 5 | 2026-01-06 21:29:23 |
    | TP-Link TL-SG108 | Best Value | 5 | 2026-01-06 15:27:04 |
    | Microsoft Ergonomic Keyboard Silver | Outstanding | 5 | 2026-01-04 18:00:26 |
    | Kingston FURY Renegade DDR5 32GB 7200MHz Black | Highly Recommend | 5 | 2026-01-03 10:58:26 |
    | ... | ... | ... | ... |

    > Review title may be NULL.

---

### Problem 7

**Find product count per supplier. Sort by product count descending.**

??? tip "Hint"
    JOIN `suppliers` and `products`, then aggregate per supplier with `GROUP BY`. Count products with `COUNT(p.id)`.

??? success "Answer"
    ```sql
    SELECT
        s.company_name,
        COUNT(p.id) AS product_count
    FROM suppliers AS s
    INNER JOIN products AS p ON s.id = p.supplier_id
    GROUP BY s.id, s.company_name
    ORDER BY product_count DESC
    LIMIT 15;
    ```

    **Result (top 5 rows):**

    | company_name | product_count |
    | ---------- | ----------: |
    | ASUS Corp. | 26 |
    | Samsung Official Distribution | 25 |
    | Logitech Corp. | 17 |
    | MSI Corp. | 13 |
    | Seorin Systech | 12 |
    | LG Official Distribution | 11 |
    | TP-Link Corp. | 11 |
    | ASRock Corp. | 11 |
    | ... | ... |

    > Actual values depend on the data.

---

### Problem 8

**Find each category name and average price of its products. Top 10 by average price descending.**

??? tip "Hint"
    JOIN `categories` and `products`. Aggregate `AVG(p.price)` per category with `GROUP BY cat.id, cat.name`.

??? success "Answer"
    ```sql
    SELECT
        cat.name AS category,
        COUNT(p.id) AS product_count,
        ROUND(AVG(p.price), 0) AS avg_price
    FROM categories AS cat
    INNER JOIN products AS p ON cat.id = p.category_id
    GROUP BY cat.id, cat.name
    ORDER BY avg_price DESC
    LIMIT 10;
    ```

    **Result (top 5 rows):**

    | category | product_count | avg_price |
    | ---------- | ----------: | ----------: |
    | MacBook | 1 | 5481100.0 |
    | Gaming Laptop | 9 | 2684478.0 |
    | NVIDIA | 7 | 2406500.0 |
    | General Laptop | 10 | 1748820.0 |
    | Custom Build | 11 | 1719809.0 |
    | Professional Monitor | 6 | 1492983.0 |
    | 2-in-1 | 9 | 1458756.0 |
    | AMD | 8 | 1162400.0 |
    | ... | ... | ... |

    > Actual values depend on the data.

---

## Applied (9~16)

Practice LEFT JOIN, anti-join, 3-table JOIN, and JOIN + GROUP BY.

---

### Problem 9

**Find products with no reviews, showing name and price. Sort by price descending.**

??? tip "Hint"
    LEFT JOIN `products` with `reviews`, then find unmatched rows with `WHERE r.id IS NULL`. This is the **anti-join** pattern.

??? success "Answer"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id
    WHERE r.id IS NULL
    ORDER BY p.price DESC;
    ```

    **Result (top 5 rows):**

    | name | price |
    | ---------- | ----------: |
    | MSI Radeon RX 9070 XT GAMING X | 1896000.0 |
    | Hansung BossMonster DX5800 Black | 1129400.0 |

    > Only products with 0 reviews. Many may be discontinued.

---

### Problem 10

**Find customers who never placed an order, showing name and signup date. Sort by signup date ascending.**

??? tip "Hint"
    `customers LEFT JOIN orders` then filter with `WHERE o.id IS NULL` for customers without orders.

??? success "Answer"
    ```sql
    SELECT c.name, c.grade, c.created_at
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL
    ORDER BY c.created_at
    LIMIT 20;
    ```

    **Result (top 5 rows):**

    | name | grade | created_at |
    | ---------- | ---------- | ---------- |
    | Alan Blair | BRONZE | 2016-01-03 19:49:46 |
    | Dana Miles | BRONZE | 2016-01-15 19:21:20 |
    | Tracy Johnson | BRONZE | 2016-01-26 09:42:20 |
    | Tommy Kim | BRONZE | 2016-02-03 03:40:29 |
    | Sara Harvey | BRONZE | 2016-02-03 04:18:52 |
    | Duane Evans MD | BRONZE | 2016-02-09 18:54:54 |
    | Ashley Jones | BRONZE | 2016-02-17 13:41:08 |
    | Terry Miller DVM | BRONZE | 2016-02-23 17:09:54 |
    | ... | ... | ... |

    > Only customers with 0 orders. Most are BRONZE grade.

---

### Problem 11

**Find wishlisted but unpurchased products showing name, price, and wishlist count.**

??? tip "Hint"
    JOIN `wishlists` and `products`. Filter unpurchased with `WHERE w.is_purchased = 0`. Aggregate per product with `GROUP BY`.

??? success "Answer"
    ```sql
    SELECT
        p.name,
        p.price,
        COUNT(w.id) AS wishlist_count
    FROM wishlists AS w
    INNER JOIN products AS p ON w.product_id = p.id
    WHERE w.is_purchased = 0
    GROUP BY p.id, p.name, p.price
    ORDER BY wishlist_count DESC
    LIMIT 15;
    ```

    **Result (top 5 rows):**

    | name | price | wishlist_count |
    | ---------- | ----------: | ----------: |
    | MSI MAG X870E TOMAHAWK WIFI White | 425400.0 | 19 |
    | ASUS ROG Swift PG32UCDM Silver | 1890300.0 | 19 |
    | NZXT Kraken Elite 240 RGB Silver | 323500.0 | 16 |
    | TP-Link TL-SG108E | 101500.0 | 16 |
    | Ducky One 3 Full Black | 153900.0 | 16 |
    | Samsung SPA-KFG0BUB | 30700.0 | 15 |
    | HP Pavilion x360 14 Black | 1479700.0 | 15 |
    | Microsoft 365 Personal | 108200.0 | 14 |
    | ... | ... | ... |

    > Actual values depend on the data.

---

### Problem 12

**Find order number, customer name, product name, quantity, and unit price for the 5 most recent orders. (4-table JOIN)**

??? tip "Hint"
    Connect 4 tables with INNER JOIN: `orders` -> `customers`, `orders` -> `order_items` -> `products`.

??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer,
        p.name AS product,
        oi.quantity,
        oi.unit_price
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    ORDER BY o.ordered_at DESC
    LIMIT 5;
    ```

    **Result (5행):**

    | order_number | customer | product | quantity | unit_price |
    | ---------- | ---------- | ---------- | ----------: | ----------: |
    | ORD-20251231-37555 | Angel Jones | Norton AntiVirus Plus Silver | 1 | 74800.0 |
    | ORD-20251231-37543 | Carla Watson | Hancom Office 2024 Enterprise White | 1 | 134100.0 |
    | ORD-20251231-37552 | Martin Hanson | Hancom Office 2024 Enterprise White | 1 | 134100.0 |
    | ORD-20251231-37552 | Martin Hanson | NZXT Kraken 240 Silver | 1 | 120200.0 |
    | ORD-20251231-37548 | Lucas Johnson | Samsung 990 EVO Plus 1TB White | 1 | 187700.0 |
    | ... | ... | ... | ... | ... |

---

### Problem 13

**Find products with 5+ reviews showing name, avg rating, and review count. Sort by avg rating descending.**

??? tip "Hint"
    JOIN `products` with `reviews`, then filter with `GROUP BY` and `HAVING COUNT(r.id) >= 5`.

??? success "Answer"
    ```sql
    SELECT
        p.name,
        ROUND(AVG(r.rating), 2) AS avg_rating,
        COUNT(r.id) AS review_count
    FROM products AS p
    INNER JOIN reviews AS r ON p.id = r.product_id
    GROUP BY p.id, p.name
    HAVING COUNT(r.id) >= 5
    ORDER BY avg_rating DESC
    LIMIT 15;
    ```

    **Result (top 5 rows):**

    | name | avg_rating | review_count |
    | ---------- | ----------: | ----------: |
    | Samsung DM500TDA Silver | 4.8 | 5 |
    | LG 27UQ85R White | 4.6 | 5 |
    | LG 32UN880 Ergo White | 4.56 | 16 |
    | WD Elements 2TB Black | 4.53 | 19 |
    | Windows 11 Home Black | 4.52 | 21 |
    | Dell XPS Desktop 8960 Silver | 4.5 | 10 |
    | Arctic Liquid Freezer III Pro 420 A-RGB Silver | 4.45 | 22 |
    | Intel NUC 13 Pro Silver | 4.44 | 9 |
    | ... | ... | ... |

    > Actual values depend on the data.

---

### Problem 14

**Staff hierarchy (Self-JOIN): Find all staff with their manager's name.**

??? tip "Hint"
    LEFT JOIN `staff` with itself. `staff AS s LEFT JOIN staff AS m ON s.manager_id = m.id`. NULL indicates top-level manager.

??? success "Answer"
    ```sql
    SELECT
        s.id,
        s.name       AS staff_name,
        s.department,
        s.role,
        m.name       AS manager_name,
        m.department AS manager_department
    FROM staff AS s
    LEFT JOIN staff AS m ON s.manager_id = m.id
    ORDER BY s.department, s.name;
    ```

    **Result (top 5 rows):**

    | id | staff_name | department | role | manager_name | manager_department |
    | ----------: | ---------- | ---------- | ---------- | ---------- | ---------- |
    | 3 | Jonathan Smith | Management | admin | Michael Thomas | Management |
    | 2 | Michael Mcguire | Management | admin | Michael Thomas | Management |
    | 1 | Michael Thomas | Management | admin | (NULL) | (NULL) |
    | 5 | Nicole Hamilton | Marketing | manager | Jonathan Smith | Management |
    | 4 | Jaime Phelps | Sales | manager | Michael Thomas | Management |
    | ... | ... | ... | ... | ... | ... |

    > NULL manager_name indicates the top-level manager.

---

### Problem 15

**Find total revenue and units sold per category. Exclude cancelled orders.**

??? tip "Hint"
    JOIN `order_items` -> `products` -> `categories`, also JOIN `orders` to exclude cancelled. 4-table JOIN + GROUP BY.

??? success "Answer"
    ```sql
    SELECT
        cat.name AS category,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue
    FROM order_items AS oi
    INNER JOIN orders AS o ON oi.order_id = o.id
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY cat.name
    ORDER BY revenue DESC;
    ```

    **Result (top 5 rows):**

    | category | units_sold | revenue |
    | ---------- | ----------: | ----------: |
    | Gaming Laptop | 1691 | 4982099000.0 |
    | AMD | 4016 | 3124984300.0 |
    | NVIDIA | 1661 | 2814694400.0 |
    | Gaming Monitor | 2464 | 2781055700.0 |
    | General Laptop | 1365 | 2429349600.0 |
    | 2-in-1 | 1301 | 1944050200.0 |
    | Intel Socket | 3406 | 1556580900.0 |
    | AMD Socket | 3325 | 1531232500.0 |
    | ... | ... | ... |

    > Actual values depend on the data.

---

### Problem 16

**Find days with no orders: Use the calendar table to find dates in 2024 with zero orders.**

??? tip "Hint"
    `calendar` LEFT JOIN order dates (subquery). Filter with `WHERE o.order_date IS NULL`.

??? success "Answer"
    ```sql
    SELECT
        cal.date_key,
        cal.day_name,
        cal.is_weekend,
        cal.is_holiday,
        cal.holiday_name
    FROM calendar AS cal
    LEFT JOIN (
        SELECT DISTINCT SUBSTR(ordered_at, 1, 10) AS order_date
        FROM orders
    ) AS od ON cal.date_key = od.order_date
    WHERE cal.year = 2024
      AND od.order_date IS NULL
    ORDER BY cal.date_key;
    ```

    **Result (top 5 rows):**

    | date_key | day_name | is_weekend | is_holiday | holiday_name |
    |----------|----------|-----------|-----------|-------------|
    | 2024-01-01 | 월요일 | 0 | 1 | 신정 |
    | 2024-02-09 | 금요일 | 0 | 1 | 설날 연휴 |
    | 2024-02-10 | 토요일 | 1 | 1 | 설날 |
    | 2024-02-11 | 일요일 | 1 | 1 | 설날 연휴 |
    | 2024-02-12 | 월요일 | 0 | 1 | 대체공휴일 |

    > Days without orders often fall on holidays. Actual results depend on the data.

---

## Practical (17~25)

Practice 4+ table JOINs and complex business queries.

---

### Problem 17

**Find each customer's name, grade, order count, and total spending. Top 10 by total spending. Exclude cancelled.**

??? tip "Hint"
    JOIN `customers` with `orders` then aggregate with `GROUP BY`. Use `COUNT` and `SUM` with `WHERE o.status NOT IN ('cancelled')`.

??? success "Answer"
    ```sql
    SELECT
        c.name,
        c.grade,
        COUNT(o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```

    **Result (top 5 rows):**

    | name | grade | order_count | total_spent |
    | ---------- | ---------- | ----------: | ----------: |
    | Allen Snyder | VIP | 312 | 409734279.0 |
    | Jason Rivera | VIP | 352 | 382314874.0 |
    | Ronald Arellano | VIP | 225 | 266184349.0 |
    | Brenda Garcia | VIP | 250 | 254525838.0 |
    | Courtney Huff | VIP | 226 | 248498783.0 |
    | Gabriel Walters | VIP | 290 | 248168491.0 |
    | James Banks | VIP | 236 | 244859844.0 |
    | Sandra Callahan | GOLD | 178 | 213212640.0 |
    | ... | ... | ... | ... |

    > Actual values depend on the data.

---

### Problem 18

**Find shipment count, delivered count, and delivery rate (%) per carrier.**

??? tip "Hint"
    `GROUP BY carrier`. Conditional aggregation with `SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)`. Rate is `100.0 * delivered / total`.

??? success "Answer"
    ```sql
    SELECT
        carrier,
        COUNT(*) AS total,
        SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered,
        ROUND(100.0 * SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) / COUNT(*), 1) AS delivery_rate
    FROM shipping
    GROUP BY carrier
    ORDER BY total DESC;
    ```

    **Result:**

    | carrier | total | delivered | delivery_rate |
    | ---------- | ----------: | ----------: | ----------: |
    | FedEx | 10507 | 10198 | 97.1 |
    | UPS | 8993 | 8729 | 97.1 |
    | USPS | 7227 | 6990 | 96.7 |
    | DHL | 5356 | 5184 | 96.8 |
    | OnTrac | 3533 | 3417 | 96.7 |
    | ... | ... | ... | ... |

    > Actual values depend on the data.

---

### Problem 19

**Find product count, avg price, and max price per supplier. Sort by product count descending.**

??? tip "Hint"
    JOIN `suppliers` with `products` then aggregate with `GROUP BY`. Use `COUNT`, `AVG`, `MAX`.

??? success "Answer"
    ```sql
    SELECT
        s.company_name,
        COUNT(p.id) AS product_count,
        ROUND(AVG(p.price), 0) AS avg_price,
        MAX(p.price) AS max_price
    FROM suppliers AS s
    INNER JOIN products AS p ON s.id = p.supplier_id
    GROUP BY s.id, s.company_name
    ORDER BY product_count DESC
    LIMIT 15;
    ```

    **Result (top 5 rows):**

    | company_name | product_count | avg_price | max_price |
    | ---------- | ----------: | ----------: | ----------: |
    | ASUS Corp. | 26 | 1683631.0 | 4526600.0 |
    | Samsung Official Distribution | 25 | 616008.0 | 1833000.0 |
    | Logitech Corp. | 17 | 111600.0 | 216800.0 |
    | MSI Corp. | 13 | 778431.0 | 1896000.0 |
    | Seorin Systech | 12 | 157908.0 | 269200.0 |
    | LG Official Distribution | 11 | 1346836.0 | 1828800.0 |
    | TP-Link Corp. | 11 | 128764.0 | 344000.0 |
    | ASRock Corp. | 11 | 477491.0 | 665600.0 |
    | ... | ... | ... | ... |

    > Actual values depend on the data.

---

### Problem 20

**Find avg delivery days (order -> delivery) per carrier for delivered orders.**

??? tip "Hint"
    JOIN `shipping` with `orders`. Calculate date difference with `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)`.

??? success "Answer"
    ```sql
    SELECT
        sh.carrier,
        COUNT(*) AS delivered_count,
        ROUND(AVG(JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at)), 1) AS avg_days,
        MIN(CAST(JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at) AS INTEGER)) AS min_days,
        MAX(CAST(JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at) AS INTEGER)) AS max_days
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE sh.status = 'delivered'
      AND sh.delivered_at IS NOT NULL
    GROUP BY sh.carrier
    ORDER BY avg_days;
    ```

    **Result:**

    | carrier | delivered_count | avg_days | min_days | max_days |
    | ---------- | ----------: | ----------: | ----------: | ----------: |
    | DHL | 5184 | 4.5 | 2 | 7 |
    | FedEx | 10198 | 4.5 | 2 | 7 |
    | OnTrac | 3417 | 4.5 | 2 | 7 |
    | UPS | 8729 | 4.5 | 2 | 7 |
    | USPS | 6990 | 4.5 | 2 | 7 |
    | ... | ... | ... | ... | ... |

    > Actual values depend on the data.

---

### Problem 21

**Find products tagged "Gaming" showing name, brand, price, and category. (M:N JOIN)**

??? tip "Hint"
    Filter tag name via `product_tags` -> `tags`, get product/category info via `product_tags` -> `products` -> `categories`.

??? success "Answer"
    ```sql
    SELECT
        p.name AS product_name,
        p.brand,
        p.price,
        cat.name AS category
    FROM product_tags AS pt
    INNER JOIN tags AS t ON pt.tag_id = t.id
    INNER JOIN products AS p ON pt.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE t.name = 'Gaming'
      AND p.is_active = 1
    ORDER BY p.price DESC;
    ```

    **Result (top 5 rows):**

    | product_name | brand | price | category |
    | ---------- | ---------- | ----------: | ---------- |
    | Razer Blade 18 Black | Razer | 4353100.0 | Gaming Laptop |
    | Razer Blade 16 Silver | Razer | 3702900.0 | Gaming Laptop |
    | Razer Blade 18 Black | Razer | 2987500.0 | Gaming Laptop |
    | Razer Blade 18 White | Razer | 2483600.0 | Gaming Laptop |
    | ASUS ROG Strix Scar 16 | ASUS | 2452500.0 | Gaming Laptop |
    | ASUS ROG Swift PG32UCDM Silver | ASUS | 1890300.0 | Gaming Monitor |
    | ASUS ROG Strix G16CH Silver | ASUS | 1879100.0 | Custom Build |
    | Jooyon Rionine i9 High-End | Jooyon Tech | 1849900.0 | Custom Build |
    | ... | ... | ... | ... |

    > Actual results depend on the data.

---

### Problem 22

**Q&A thread query (Self-JOIN): Show Q&A questions and answers in a single row.**

??? tip "Hint"
    Questions: `parent_id IS NULL`. Answers: `parent_id` references the question `id`. Question(q) LEFT JOIN Answer(a) ON `a.parent_id = q.id`.

??? success "Answer"
    ```sql
    SELECT
        p.name        AS product_name,
        q.content     AS question,
        c.name        AS asked_by,
        q.created_at  AS asked_at,
        a.content     AS answer,
        s.name        AS answered_by,
        a.created_at  AS answered_at
    FROM product_qna AS q
    INNER JOIN products AS p ON q.product_id = p.id
    LEFT JOIN customers AS c ON q.customer_id = c.id
    LEFT JOIN product_qna AS a ON a.parent_id = q.id
    LEFT JOIN staff AS s ON a.staff_id = s.id
    WHERE q.parent_id IS NULL
    ORDER BY q.created_at DESC
    LIMIT 20;
    ```

    **Result (top 3 rows):**

    | product_name | question | asked_by | asked_at | answer | answered_by | answered_at |
    | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
    | SK hynix Platinum P41 2TB Silver | What are the exact dimensions? | Robert Simmons | 2025-12-30 23:10:22 | (NULL) | (NULL) | (NULL) |
    | ASRock B850M Pro RS White | What PSU wattage do you recommend for this? | Kathleen Stewart | 2025-12-30 23:01:05 | (NULL) | (NULL) | (NULL) |
    | Dell U2724D | What PSU wattage do you recommend for this? | Jill Reed | 2025-12-30 17:53:24 | Yes, it works with both Windows and Mac. | Jaime Phelps | 2025-12-30 20:53:24 |
    | ASRock X870E Taichi Silver | Is this product new or refurbished? | Cory Salazar | 2025-12-30 14:27:52 | (NULL) | (NULL) | (NULL) |
    | Fractal Design North | What are the exact dimensions? | Daniel Murphy | 2025-12-30 13:30:22 | (NULL) | (NULL) | (NULL) |
    | MSI MEG Ai1300P PCIE5 White | Does this come with cables included? | Tracey Johnston | 2025-12-29 19:22:36 | Yes, all necessary cables are included in the package. | Nicole Hamilton | 2025-12-30 21:22:36 |
    | TP-Link TG-3468 Black | Can I use this with a Mac? | John Moss | 2025-12-29 10:01:52 | We expect restock within 2 weeks. You can set a notification. | Nicole Hamilton | 2025-12-29 11:01:52 |
    | Brother MFC-L2750DW Black | Does this come with cables included? | Terry James | 2025-12-29 08:43:06 | We expect restock within 2 weeks. You can set a notification. | Michael Thomas | 2025-12-30 03:43:06 |
    | ... | ... | ... | ... | ... | ... | ... |

    > Questions without answers have NULL for answer/answered_by.

---

### Problem 23

**Customer complaint details: Find customer name, order number, assigned staff, and complaint category. Most recent 15.**

??? tip "Hint"
    LEFT JOIN `complaints` with `customers`, `orders` (nullable), and `staff` (nullable). Include general inquiries without orders.

??? success "Answer"
    ```sql
    SELECT
        cpl.id,
        c.name AS customer_name,
        o.order_number,
        s.name AS staff_name,
        cpl.category,
        cpl.priority,
        cpl.status,
        cpl.created_at
    FROM complaints AS cpl
    INNER JOIN customers AS c ON cpl.customer_id = c.id
    LEFT JOIN orders AS o ON cpl.order_id = o.id
    LEFT JOIN staff AS s ON cpl.staff_id = s.id
    ORDER BY cpl.created_at DESC
    LIMIT 15;
    ```

    **Result (top 5 rows):**

    | id | customer_name | order_number | staff_name | category | priority | status | created_at |
    | ----------: | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
    | 3050 | Dorothy Nelson | ORD-20251231-37541 | Jaime Phelps | product_defect | medium | closed | 2026-01-13 20:27:26 |
    | 3046 | Timothy Ward | ORD-20251228-37483 | Michael Mcguire | general_inquiry | low | closed | 2026-01-11 05:32:28 |
    | 3051 | Lucas Johnson | ORD-20251231-37548 | Michael Thomas | refund_request | urgent | closed | 2026-01-10 08:43:56 |
    | 3043 | Jacob Smith | ORD-20251228-37466 | Nicole Hamilton | product_defect | urgent | closed | 2026-01-08 10:26:57 |
    | 3039 | Samantha Sampson | ORD-20251227-37453 | Michael Thomas | general_inquiry | medium | closed | 2026-01-08 08:28:26 |
    | 3044 | Charles Patterson | ORD-20251228-37467 | Michael Mcguire | general_inquiry | urgent | closed | 2026-01-05 13:56:10 |
    | 3040 | Janet Manning | ORD-20251227-37454 | Michael Mcguire | exchange_request | low | resolved | 2026-01-04 21:17:27 |
    | 3030 | Sarah Li | ORD-20251222-37348 | Jaime Phelps | delivery_issue | high | closed | 2026-01-04 14:42:16 |
    | ... | ... | ... | ... | ... | ... | ... | ... |

    > NULL order_number indicates a general inquiry (not order-related).

---

### Problem 24

**Product successor chain (Self-JOIN): Find discontinued products with their successor models.**

??? tip "Hint"
    `products.successor_id` references `id` in the same table. `products AS p JOIN products AS succ ON p.successor_id = succ.id`.

??? success "Answer"
    ```sql
    SELECT
        p.name        AS discontinued_product,
        p.price       AS old_price,
        p.discontinued_at,
        succ.name     AS successor_product,
        succ.price    AS new_price,
        ROUND(succ.price - p.price, 0) AS price_diff
    FROM products AS p
    INNER JOIN products AS succ ON p.successor_id = succ.id
    WHERE p.discontinued_at IS NOT NULL
    ORDER BY p.discontinued_at DESC
    LIMIT 20;
    ```

    **Result (top 5 rows):**

    | discontinued_product | old_price | discontinued_at | successor_product | new_price | price_diff |
    | ---------- | ----------: | ---------- | ---------- | ----------: | ----------: |
    | Dell XPS Desktop 8960 Silver | 1249400.0 | 2025-11-20 15:30:12 | HP Z2 Mini G1a Black | 895000.0 | -354400.0 |
    | Hansung BossMonster DX7700 White | 1579400.0 | 2025-10-25 03:47:01 | Jooyon Rionine i9 High-End | 1849900.0 | 270500.0 |
    | SAPPHIRE PULSE RX 7800 XT Silver | 1146300.0 | 2025-08-01 06:10:51 | MSI Radeon RX 9070 XT GAMING X | 1896000.0 | 749700.0 |
    | Logitech G715 | 187900.0 | 2025-04-16 06:47:20 | Ducky One 3 Full Black | 153900.0 | -34000.0 |
    | Razer Basilisk V3 Pro 35K White | 102100.0 | 2025-02-14 06:48:19 | Logitech G PRO X SUPERLIGHT 2 White | 120400.0 | 18300.0 |
    | Canon imageCLASS MF655Cdw Black | 278900.0 | 2024-09-20 15:47:07 | Epson L15160 | 1019500.0 | 740600.0 |
    | be quiet! Straight Power 12 1000W | 131800.0 | 2024-08-15 23:34:23 | be quiet! Dark Power 13 1000W | 293000.0 | 161200.0 |
    | Lian Li A4-H2O Black | 144000.0 | 2024-06-10 11:57:43 | CORSAIR iCUE 4000X | 113900.0 | -30100.0 |
    | ... | ... | ... | ... | ... | ... |

    > Actual results depend on the data.

---

### Problem 25

**Find revenue share by customer grade and payment method. Exclude cancelled.**

??? tip "Hint"
    JOIN 3 tables: `customers` -> `orders` -> `payments`. Cross-tabulate with `GROUP BY c.grade, pay.method` and calculate share within each grade.

??? success "Answer"
    ```sql
    SELECT
        c.grade,
        pay.method,
        COUNT(*) AS order_count,
        ROUND(SUM(pay.amount), 0) AS total_amount,
        ROUND(100.0 * SUM(pay.amount) / SUM(SUM(pay.amount)) OVER (PARTITION BY c.grade), 1) AS pct_in_grade
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    INNER JOIN payments AS pay ON o.id = pay.order_id
    WHERE o.status NOT IN ('cancelled')
      AND pay.status = 'completed'
    GROUP BY c.grade, pay.method
    ORDER BY c.grade, total_amount DESC;
    ```

    **Result (상위 8행):**

    | grade | method | order_count | total_amount | pct_in_grade |
    | ---------- | ---------- | ----------: | ----------: | ----------: |
    | BRONZE | card | 3419 | 2961337674.0 | 44.2 |
    | BRONZE | kakao_pay | 1540 | 1340082913.0 | 20.0 |
    | BRONZE | naver_pay | 1129 | 1013357950.0 | 15.1 |
    | BRONZE | bank_transfer | 769 | 683115099.0 | 10.2 |
    | BRONZE | virtual_account | 371 | 373375315.0 | 5.6 |
    | BRONZE | point | 380 | 324872725.0 | 4.9 |
    | GOLD | card | 3546 | 3596555538.0 | 45.2 |
    | GOLD | kakao_pay | 1505 | 1475781227.0 | 18.5 |
    | ... | ... | ... | ... | ... |

    > Actual values depend on the data. Uses window function `SUM() OVER()` for within-grade share.
