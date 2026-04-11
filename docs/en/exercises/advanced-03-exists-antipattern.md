# EXISTS and Anti-Patterns

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    `customers` — Customer<br>
    `orders` — Order<br>
    `order_items` — Order Details<br>
    `products` — Product<br>
    `reviews` — Review<br>
    `wishlists` — Wishlist<br>
    `complaints` — File a complaint<br>
    `categories` — Category<br>
    `payments` — Payment

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    `EXISTS`<br>
    `NOT EXISTS`<br>
    Correlated subquery<br>
    Anti-join pattern<br>
    Universal Quantification

</div>

!!! info "Before You Begin"
    This exercise puts into practice what you learned in **Advanced Lesson 20** (EXISTS).
    `EXISTS` returns TRUE if there is at least one row as a result of the subquery.
    `NOT EXISTS` is the opposite — TRUE when there are no rows of results.

---

## Basic (1~5)

Practice the basic usage of EXISTS and NOT EXISTS.

---

### Problem 1

**Check only customers who have placed an order in 2024.**

Displays customer ID, name, level, and subscription date. Use `EXISTS`.

??? tip "Hint"
    `WHERE EXISTS (SELECT 1 FROM orders WHERE customer_id = c.id AND ...)`
    A subquery that references `c.id` of the outer query is a correlated subquery.

??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        c.created_at AS signup_date
    FROM customers AS c
    WHERE EXISTS (
        SELECT 1
        FROM orders AS o
        WHERE o.customer_id = c.id
          AND o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    ORDER BY c.id
    LIMIT 20;
    ```

    **Result example (top 5 rows):**

    | id | name | grade | signup_date |
    | ----------: | ---------- | ---------- | ---------- |
    | 2 | 김경수 | BRONZE | 2016-08-17 12:29:34 |
    | 3 | 김민재 | VIP | 2016-02-11 19:59:38 |
    | 4 | 진정자 | GOLD | 2016-09-18 15:29:45 |
    | 5 | 이정수 | BRONZE | 2016-02-28 11:34:16 |
    | 8 | 성민석 | VIP | 2016-09-24 06:49:22 |
    | 10 | 박지훈 | GOLD | 2016-12-20 04:06:43 |
    | 12 | 장준서 | SILVER | 2016-12-30 06:48:08 |
    | 14 | 윤순옥 | BRONZE | 2016-06-05 10:37:50 |
    | ... | ... | ... | ... |

    > Returns the same results as the `IN` subquery, but `EXISTS` is more efficient for large data.

---

### Problem 2

**Find customers who have never placed an order.**

This is a customer who has only registered but has no order history. Use `NOT EXISTS`.

??? tip "Hint"
    `WHERE NOT EXISTS (SELECT 1 FROM orders WHERE customer_id = c.id)`
    At this time, canceled/returned orders are also considered “placed” (no status filter).

??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        c.created_at AS signup_date,
        ROUND(JULIANDAY('2025-12-31') - JULIANDAY(c.created_at), 0) AS days_since_signup
    FROM customers AS c
    WHERE NOT EXISTS (
        SELECT 1
        FROM orders AS o
        WHERE o.customer_id = c.id
    )
    ORDER BY c.created_at
    LIMIT 20;
    ```

    **Result example (top 5 rows):**

    | id | name | grade | signup_date | days_since_signup |
    | ----------: | ---------- | ---------- | ---------- | ----------: |
    | 133 | 성미숙 | BRONZE | 2016-01-01 00:53:24 | 3652.0 |
    | 584 | 오진호 | BRONZE | 2016-01-01 03:10:41 | 3652.0 |
    | 387 | 노지민 | BRONZE | 2016-01-01 10:17:05 | 3652.0 |
    | 84 | 양영진 | BRONZE | 2016-01-03 19:49:46 | 3649.0 |
    | 707 | 김지아 | BRONZE | 2016-01-05 08:33:42 | 3648.0 |
    | 641 | 김민준 | BRONZE | 2016-01-05 21:52:07 | 3647.0 |
    | 516 | 최유진 | BRONZE | 2016-01-06 00:09:48 | 3647.0 |
    | 951 | 이미정 | BRONZE | 2016-01-06 05:24:42 | 3647.0 |
    | ... | ... | ... | ... | ... |

---

### Problem 3

**Find verified customers who have not left a review.**

Customers who have orders with an order status of 'confirmed' but who have not written a single review.

??? tip "Hint"
    Combine 2 conditions:
    `EXISTS (... orders WHERE status = 'confirmed')` AND
    `NOT EXISTS (... reviews WHERE customer_id = c.id)`.

??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(o.id) AS confirmed_orders
    FROM customers AS c
    INNER JOIN orders AS o
        ON c.id = o.customer_id
       AND o.status = 'confirmed'
    WHERE NOT EXISTS (
        SELECT 1
        FROM reviews AS r
        WHERE r.customer_id = c.id
    )
    GROUP BY c.id, c.name, c.grade
    ORDER BY confirmed_orders DESC
    LIMIT 15;
    ```

    **Result example (top 3 rows):**

    | id | name | grade | confirmed_orders |
    | ----------: | ---------- | ---------- | ----------: |
    | 27069 | 김예준 | VIP | 25 |
    | 31228 | 고영희 | GOLD | 20 |
    | 1342 | 노광수 | SILVER | 18 |
    | 15336 | 조영식 | GOLD | 18 |
    | 1676 | 하서연 | BRONZE | 17 |
    | 17111 | 나은서 | BRONZE | 16 |
    | 29619 | 김준영 | SILVER | 16 |
    | 2268 | 강현준 | SILVER | 15 |
    | ... | ... | ... | ... |

    > You can use them as target customers for review writing campaigns.

---

### Problem 4

**Find product-customer combinations that have been added to their wishlist but have not yet been purchased.**

Among the `is_purchased = 0` items in the wishlist, the customer has never actually ordered the product.

??? tip "Hint"
    Based on `wishlists`, create a subquery combining `order_items` and `orders` with `NOT EXISTS`.
    Subquery condition: equal to `customer_id` and equal to `product_id`.

??? success "Answer"
    ```sql
    SELECT
        w.customer_id,
        c.name     AS customer_name,
        w.product_id,
        p.name     AS product_name,
        p.price,
        w.created_at AS wishlisted_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products  AS p ON w.product_id  = p.id
    WHERE w.is_purchased = 0
      AND NOT EXISTS (
          SELECT 1
          FROM order_items AS oi
          INNER JOIN orders AS o ON oi.order_id = o.id
          WHERE o.customer_id = w.customer_id
            AND oi.product_id = w.product_id
            AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    ORDER BY w.created_at DESC
    LIMIT 15;
    ```

    **Result example (top 3 rows):**

    | customer_id | customer_name | product_id | product_name | price | wishlisted_at |
    |---|---|---|---|---|---|
    | 45 | 한... | 12 | MacBook Air M3 | 1590000 | 2025-11-20 ... |
    | 112 | 송... | 78 | LG 울트라기어 32GP850 | 720000 | 2025-10-15 ... |
    | 203 | 강... | 5 | 삼성 Galaxy Tab S9 | 890000 | 2025-09-08 ... |

    > This is where the marketing team will send shopping cart abandonment notifications or discount coupons.

---

### Problem 5

**Find the top 10 customers by order amount who have never received a CS inquiry.**

Identify “blue-chip customers” who consistently purchase without making a claim.

??? tip "Hint"
    Filter customers with no inquiry history with `NOT EXISTS (SELECT 1 FROM complaints WHERE customer_id = c.id)`,
    Extract the top 10 users by total purchase amount with `SUM(total_amount)`.

??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      AND NOT EXISTS (
          SELECT 1
          FROM complaints AS cp
          WHERE cp.customer_id = c.id
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```

    **Result example (top 3 rows):**

    | id | name | grade | order_count | total_spent |
    | ----------: | ---------- | ---------- | ----------: | ----------: |
    | 12486 | 민민재 | GOLD | 52 | 110159678.0 |
    | 3059 | 윤유진 | BRONZE | 5 | 73560400.0 |
    | 35583 | 고광수 | GOLD | 18 | 70057482.0 |
    | 26131 | 손준호 | VIP | 27 | 65757868.0 |
    | 41328 | 최순옥 | VIP | 12 | 64954495.0 |
    | 19776 | 박수빈 | BRONZE | 26 | 63290909.0 |
    | 13716 | 주경숙 | VIP | 18 | 62181751.0 |
    | 24264 | 권성진 | VIP | 47 | 61953072.0 |
    | ... | ... | ... | ... | ... |

---

## Applied (6~10)

Covers complex EXISTS conditions combining correlated subqueries and aggregates.

---

### Problem 6

**Find customers who purchased products from 3 or more different categories**

EXISTS uses aggregates internally.

??? tip "Hint"
    Use `GROUP BY customer_id HAVING COUNT(DISTINCT category_id) >= 3` within `EXISTS`.
    Alternatively, you can count the number of categories with a correlated subquery.

??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade
    FROM customers AS c
    WHERE EXISTS (
        SELECT 1
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.customer_id = c.id
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY o.customer_id
        HAVING COUNT(DISTINCT p.category_id) >= 3
    )
    ORDER BY c.grade DESC, c.name
    LIMIT 20;
    ```

    **Result example (top 5 rows):**

    | id | name | grade |
    | ----------: | ---------- | ---------- |
    | 39877 | 강건우 | VIP |
    | 3645 | 강경숙 | VIP |
    | 43164 | 강경숙 | VIP |
    | 9195 | 강경자 | VIP |
    | 15102 | 강경자 | VIP |
    | 37003 | 강경자 | VIP |
    | 37522 | 강경희 | VIP |
    | 49065 | 강광수 | VIP |
    | ... | ... | ... |

    > Customers who purchase multiple categories are valuable targets for cross-selling.

---

### Problem 7

**Only view orders for which all payments have been completed successfully.**

There may be multiple payments in one order. Find orders that do not have any failed (`failed`) or refunded (`refunded`) payments.

??? tip "Hint"
    "Failure/No refund" = `NOT EXISTS (... payments WHERE status IN ('failed', 'refunded') AND order_id = o.id)`.
    Additionally, at least one payment must exist (`EXISTS`).

??? success "Answer"
    ```sql
    SELECT
        o.id,
        o.order_number,
        o.total_amount,
        o.ordered_at,
        o.status
    FROM orders AS o
    WHERE EXISTS (
        SELECT 1
        FROM payments AS p
        WHERE p.order_id = o.id
          AND p.status = 'completed'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM payments AS p
        WHERE p.order_id = o.id
          AND p.status IN ('failed', 'refunded')
    )
    AND o.ordered_at LIKE '2024%'
    ORDER BY o.ordered_at DESC
    LIMIT 15;
    ```

    **Result example (top 3 rows):**

    | id | order_number | total_amount | ordered_at | status |
    | ----------: | ---------- | ----------: | ---------- | ---------- |
    | 350088 | ORD-20241231-350088 | 128500.0 | 2024-12-31 23:56:35 | confirmed |
    | 350011 | ORD-20241231-350011 | 6344900.0 | 2024-12-31 23:37:34 | confirmed |
    | 350033 | ORD-20241231-350033 | 107500.0 | 2024-12-31 23:35:44 | confirmed |
    | 350197 | ORD-20241231-350197 | 122900.0 | 2024-12-31 23:33:09 | confirmed |
    | 350203 | ORD-20241231-350203 | 304800.0 | 2024-12-31 23:32:29 | confirmed |
    | 350178 | ORD-20241231-350178 | 3994300.0 | 2024-12-31 23:25:59 | confirmed |
    | 350092 | ORD-20241231-350092 | 475600.0 | 2024-12-31 22:58:39 | confirmed |
    | 350094 | ORD-20241231-350094 | 3481000.0 | 2024-12-31 22:56:33 | confirmed |
    | ... | ... | ... | ... | ... |

---

### Problem 8

**Find products that are frequently purchased together with a specific product (ID=1) (simultaneous purchase analysis).**

In orders containing product 1, items other than product 1 are sorted in order of frequency of simultaneous purchase.

??? tip "Hint"
    The outer query aggregates items from `order_items` to `product_id != 1`.
    `EXISTS` checks whether “the order contains product 1”.

??? success "Answer"
    ```sql
    SELECT
        p.id    AS product_id,
        p.name  AS product_name,
        p.price,
        COUNT(DISTINCT oi.order_id) AS co_purchase_count
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    WHERE oi.product_id != 1
      AND EXISTS (
          SELECT 1
          FROM order_items AS oi2
          WHERE oi2.order_id   = oi.order_id
            AND oi2.product_id = 1
      )
    GROUP BY p.id, p.name, p.price
    ORDER BY co_purchase_count DESC
    LIMIT 10;
    ```

    **Result example (top 3 rows):**

    | product_id | product_name | price | co_purchase_count |
    | ----------: | ---------- | ----------: | ----------: |
    | 354 | 소니 WH-1000XM5 화이트 | 344300.0 | 9 |
    | 256 | Microsoft Bluetooth Ergonomic Mouse 화이트 | 88200.0 | 8 |
    | 70 | JBL Pebbles 2 블랙 | 96300.0 | 7 |
    | 131 | SteelSeries Arctis Nova Pro Wireless 실버 | 215500.0 | 7 |
    | 96 | JBL Flip 6 블랙 | 345400.0 | 6 |
    | 122 | SteelSeries Arctis Nova Pro Wireless 화이트 | 150300.0 | 6 |
    | 242 | 로지텍 G PRO X2 Superstrike 블랙 | 151000.0 | 6 |
    | 309 | Razer Basilisk V3 Pro 35K 블랙 | 71900.0 | 6 |
    | ... | ... | ... | ... |

    > This data serves as the basis for related product recommendation (cross-selling) strategies.

---

### Problem 9

**Find “customers who ordered every month” (12 months to 2024).**

Customers with at least 1 order in any 12 months in 2024.

??? tip "Hint"
    Combines `NOT EXISTS` with a recursive CTE (or a hardcoded list of months).
    “Every month has orders” = “There is no month without orders” (NOT EXISTS).

??? success "Answer"
    ```sql
    WITH RECURSIVE months AS (
        SELECT '2024-01' AS ym
        UNION ALL
        SELECT SUBSTR(DATE(ym || '-01', '+1 month'), 1, 7)
        FROM months
        WHERE ym < '2024-12'
    )
    SELECT
        c.id,
        c.name,
        c.grade
    FROM customers AS c
    WHERE NOT EXISTS (
        -- 주문이 없는 월이 하나라도 있으면 제외
        SELECT 1
        FROM months AS m
        WHERE NOT EXISTS (
            SELECT 1
            FROM orders AS o
            WHERE o.customer_id = c.id
              AND SUBSTR(o.ordered_at, 1, 7) = m.ym
              AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        )
    )
    ORDER BY c.grade DESC, c.name;
    ```

    **Result example:**

    | id | name | grade |
    | ----------: | ---------- | ---------- |
    | 26258 | 고숙자 | VIP |
    | 14356 | 김광수 | VIP |
    | 19872 | 김성진 | VIP |
    | 12387 | 김영진 | VIP |
    | 16387 | 류미숙 | VIP |
    | 774 | 박성진 | VIP |
    | 17840 | 박성현 | VIP |
    | 31645 | 서영일 | VIP |
    | ... | ... | ... |

    > This query is a **Double Negation** pattern:
    > "Customers with **non-existent** months without orders" = "Customers who placed orders in all months".
    > This is the SQL expression corresponding to division in relational algebra.

---

### Problem 10

**Look for “churn customers” who ordered in 2024 but not in 2025.**

Combines two EXISTS/NOT EXISTS conditions.

??? tip "Hint"
    `EXISTS (... 2024년 주문)` AND `NOT EXISTS (... 2025년 주문)`.
    It would be useful to also display the churn customer's last order date in 2024 and their total purchase amount.

??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order_date,
        COUNT(o.id) AS orders_in_2024,
        ROUND(SUM(o.total_amount), 0) AS spent_in_2024
    FROM customers AS c
    INNER JOIN orders AS o
        ON c.id = o.customer_id
       AND o.ordered_at LIKE '2024%'
       AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    WHERE NOT EXISTS (
        SELECT 1
        FROM orders AS o2
        WHERE o2.customer_id = c.id
          AND o2.ordered_at LIKE '2025%'
          AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    GROUP BY c.id, c.name, c.grade
    ORDER BY spent_in_2024 DESC
    LIMIT 15;
    ```

    **Result example (top 3 rows):**

    | id | name | grade | last_order_date | orders_in_2024 | spent_in_2024 |
    | ----------: | ---------- | ---------- | ---------- | ----------: | ----------: |
    | 40080 | 김민재 | BRONZE | 2024-12-05 21:44:31 | 4 | 48780714.0 |
    | 15138 | 홍현우 | BRONZE | 2024-06-28 20:14:39 | 2 | 36524600.0 |
    | 10379 | 조상호 | BRONZE | 2024-12-23 17:38:51 | 1 | 34017000.0 |
    | 14103 | 박병철 | BRONZE | 2024-10-28 13:30:35 | 2 | 30716888.0 |
    | 28456 | 성현주 | BRONZE | 2024-08-29 17:11:52 | 4 | 26156500.0 |
    | 7439 | 이지현 | BRONZE | 2024-08-02 23:02:56 | 2 | 25655500.0 |
    | 19071 | 김정식 | BRONZE | 2024-11-20 10:22:07 | 4 | 24627600.0 |
    | 18822 | 최영수 | BRONZE | 2024-09-25 16:25:34 | 1 | 24601700.0 |
    | ... | ... | ... | ... | ... | ... |

---

## Practical (11~15)

Covers advanced scenarios such as universal qualification, compound NOT EXISTS, and anti-patterns.

---

### Problem 11

**Find customers who only paid by card on all orders**

This is a customer who has never used a payment method other than a card (kakao_pay, naver_pay, bank_transfer, etc.).

??? tip "Hint"
    Nickname only: "All payments are by card" = "No non-card payments **exist**".
    Use `NOT EXISTS (... payments WHERE method != 'card' ...)`.
    Only customers with an order history are eligible.

??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      -- 카드가 아닌 결제가 한 건도 없어야 함
      AND NOT EXISTS (
          SELECT 1
          FROM payments AS p
          INNER JOIN orders AS o2 ON p.order_id = o2.id
          WHERE o2.customer_id = c.id
            AND p.method != 'card'
      )
      -- 결제 이력이 있어야 함
      AND EXISTS (
          SELECT 1
          FROM payments AS p
          INNER JOIN orders AS o3 ON p.order_id = o3.id
          WHERE o3.customer_id = c.id
            AND p.method = 'card'
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 15;
    ```

    **Result example (top 3 rows):**

    | id | name | grade | order_count | total_spent |
    | ----------: | ---------- | ---------- | ----------: | ----------: |
    | 52222 | 백옥자 | VIP | 1 | 23186800.0 |
    | 35894 | 성준영 | VIP | 4 | 17874181.0 |
    | 41858 | 박상현 | VIP | 1 | 15873100.0 |
    | 50823 | 양영자 | VIP | 1 | 15597600.0 |
    | 9029 | 이명자 | VIP | 6 | 13717400.0 |
    | 43150 | 이재현 | BRONZE | 1 | 13294600.0 |
    | 6250 | 이정순 | GOLD | 6 | 13025500.0 |
    | 22631 | 박민준 | BRONZE | 2 | 12257400.0 |
    | ... | ... | ... | ... | ... |

---

### Problem 12

**Find customers who have experienced “all types of inquiry categories”**

Customers who have submitted at least one inquiry for every `category` value in the `complaints` table.

??? tip "Hint"
    Double negation pattern for prequalification:
    "There are inquiries in all categories" = "There is **no category** in which there are no inquiries."
    `NOT EXISTS (SELECT category FROM (SELECT DISTINCT category FROM complaints) WHERE NOT EXISTS (... 해당 고객의 해당 카테고리 문의))`.

??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        (SELECT COUNT(DISTINCT cp.category) FROM complaints AS cp WHERE cp.customer_id = c.id) AS category_count
    FROM customers AS c
    WHERE NOT EXISTS (
        -- 문의가 없는 카테고리가 하나라도 있으면 제외
        SELECT DISTINCT cp_all.category
        FROM complaints AS cp_all
        WHERE NOT EXISTS (
            SELECT 1
            FROM complaints AS cp
            WHERE cp.customer_id = c.id
              AND cp.category = cp_all.category
        )
    )
    ORDER BY c.name;
    ```

    **Result example:**

    | id | name | grade | category_count |
    |---|---|---|---|
    | 45 | 김... | SILVER | 7 |
    | 203 | 박... | BRONZE | 7 |

    > Very few customers leave inquiries in all categories. You may be subject to special management from the CS team.

---

### Problem 13

**Find customers who “only purchased products priced over 1 million won”**

These are premium customers who have never purchased a low-priced product.

??? tip "Hint"
    “There is no purchase of products under 1 million won”:
    `NOT EXISTS (... order_items JOIN products WHERE price < 1000000 AND customer_id = c.id)`.
    At the same time, there must be an order history (`EXISTS`).

??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent,
        ROUND(AVG(o.total_amount), 0) AS avg_order_value
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      -- 100만원 미만 상품 구매가 없어야 함
      AND NOT EXISTS (
          SELECT 1
          FROM order_items AS oi
          INNER JOIN orders AS o2 ON oi.order_id = o2.id
          INNER JOIN products AS p ON oi.product_id = p.id
          WHERE o2.customer_id = c.id
            AND p.price < 1000000
            AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```

    **Result example (top 3 rows):**

    | id | name | grade | order_count | total_spent | avg_order_value |
    | ----------: | ---------- | ---------- | ----------: | ----------: | ----------: |
    | 45794 | 윤영희 | GOLD | 1 | 4429800.0 | 4429800.0 |
    | 40213 | 민지아 | BRONZE | 1 | 3507900.0 | 3507900.0 |
    | 48896 | 김성수 | GOLD | 1 | 3180600.0 | 3180600.0 |
    | 36900 | 남명숙 | BRONZE | 1 | 3076656.0 | 3076656.0 |
    | 34926 | 강상현 | GOLD | 1 | 2833200.0 | 2833200.0 |
    | 32669 | 박지훈 | BRONZE | 1 | 2360300.0 | 2360300.0 |
    | 37945 | 김지원 | BRONZE | 1 | 2317800.0 | 2317800.0 |
    | 37770 | 김보람 | BRONZE | 1 | 2283400.0 | 2283400.0 |
    | ... | ... | ... | ... | ... | ... |

---

### Problem 14

**Find repeat product pairs — where the same customer has purchased the same product more than once in different orders.**

EXISTS checks for “same customer, same product, different orders”.

??? tip "Hint"
    Based on `order_items`, `EXISTS` is the same as `product_id`, and `customer_id` is the same.
    Check if there is another record with `order_id`.
    Counts the number of repeat purchases by customer-product combination.

??? success "Answer"
    ```sql
    SELECT
        c.name     AS customer_name,
        p.name     AS product_name,
        COUNT(DISTINCT oi.order_id) AS purchase_count,
        SUM(oi.quantity) AS total_qty
    FROM order_items AS oi
    INNER JOIN orders    AS o ON oi.order_id   = o.id
    INNER JOIN customers AS c ON o.customer_id = c.id
    INNER JOIN products  AS p ON oi.product_id = p.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      AND EXISTS (
          -- 같은 고객이 같은 상품을 다른 주문에서 구매
          SELECT 1
          FROM order_items AS oi2
          INNER JOIN orders AS o2 ON oi2.order_id = o2.id
          WHERE o2.customer_id = o.customer_id
            AND oi2.product_id = oi.product_id
            AND oi2.order_id   != oi.order_id
            AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    GROUP BY c.id, c.name, p.id, p.name
    ORDER BY purchase_count DESC
    LIMIT 15;
    ```

    **Result example (top 3 rows):**

    | customer_name | product_name | purchase_count | total_qty |
    |---|---|---|---|
    | 김... | 삼성 DDR4 32GB | 4 | 8 |
    | 박... | Logitech MX Keys Mini | 3 | 3 |
    | 이... | Samsung EVO 970 Plus 1TB | 3 | 5 |

    > Consumables or products with a high possibility of additional purchase appear mainly.

---

### Problem 15

**Compare "NOT EXISTS vs LEFT JOIN IS NULL" anti-join patterns.**

Look for products that haven't left reviews in 2024 in two ways and see if the results are the same.

??? tip "Hint"
    Method 1: `NOT EXISTS (SELECT 1 FROM reviews WHERE product_id = p.id AND created_at LIKE '2024%')`.
    Method 2: `LEFT JOIN reviews ON ... WHERE r.id IS NULL`.
    If you compare two queries with `EXCEPT`, the difference must be empty.

??? success "Answer"
    ```sql
    -- 방법 1: NOT EXISTS
    SELECT p.id, p.name
    FROM products AS p
    WHERE p.is_active = 1
      AND NOT EXISTS (
          SELECT 1
          FROM reviews AS r
          WHERE r.product_id = p.id
            AND r.created_at LIKE '2024%'
      )
    ORDER BY p.id;
    ```

    ```sql
    -- 방법 2: LEFT JOIN ... IS NULL
    SELECT p.id, p.name
    FROM products AS p
    LEFT JOIN reviews AS r
        ON r.product_id = p.id
       AND r.created_at LIKE '2024%'
    WHERE p.is_active = 1
      AND r.id IS NULL
    ORDER BY p.id;
    ```

    ```sql
    -- 동일성 검증: 차집합이 비어야 함
    SELECT p.id, p.name
    FROM products AS p
    WHERE p.is_active = 1
      AND NOT EXISTS (
          SELECT 1 FROM reviews AS r
          WHERE r.product_id = p.id AND r.created_at LIKE '2024%'
      )

    EXCEPT

    SELECT p.id, p.name
    FROM products AS p
    LEFT JOIN reviews AS r
        ON r.product_id = p.id AND r.created_at LIKE '2024%'
    WHERE p.is_active = 1
      AND r.id IS NULL;
    ```

    **Verification result:**

    | id | name |
    |---|---|
    | *(빈 결과)* | |

    > Both methods return logically identical results.
    > `NOT EXISTS` is good for readability, and `LEFT JOIN ... IS NULL` is advantageous for utilizing additional columns.
    > You can see the performance difference by comparing execution plans (EXPLAIN).
