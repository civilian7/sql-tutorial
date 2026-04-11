# Lesson 14: UNION

In [Lesson 13](13-utility-functions.md), we learned numeric, conversion, and conditional functions. So far we've queried data with a single SELECT. But sometimes you need to combine results from multiple queries, like "top 5 products + bottom 5 products". In this lesson, we learn how to combine results with UNION.

!!! note "Already familiar?"
    If you're comfortable with UNION, UNION ALL, INTERSECT, and EXCEPT, skip ahead to [Lesson 15: DML](15-dml.md).

`UNION` stacks the results of two or more `SELECT` statements vertically. Each query must return the same number of columns, and the corresponding column types must be compatible. Column names come from the first query.

```mermaid
flowchart LR
    subgraph "Query A"
        A["SELECT ...\nFROM complaints"]
    end
    subgraph "Query B"
        B["SELECT ...\nFROM reviews"]
    end
    A --> U["UNION\n(remove duplicates)"]
    B --> U
    U --> R["Combined\nResult"]
```

> UNION combines two query results vertically. Column count and types must match.

## UNION vs. UNION ALL

![UNION](../img/set-union.svg){ .off-glb width="280"  }

| Operator | Duplicate Handling | Speed |
|--------|-----------|------|
| `UNION` | Removed (acts like `DISTINCT`) | Slow -- requires sorting/hashing for dedup |
| `UNION ALL` | Kept | Fast -- no dedup step |

Use `UNION ALL` when you know there are no duplicates, or when you want to count all occurrences.

## Basic UNION

```sql
-- Combine VIP and GOLD customers into one list
-- (No duplicates possible from the same table, but UNION removes them just in case)
SELECT id, name, grade FROM customers WHERE grade = 'VIP'
UNION
SELECT id, name, grade FROM customers WHERE grade = 'GOLD'
ORDER BY name;
```

> This result is identical to `WHERE grade IN ('VIP', 'GOLD')`, but UNION's true power shows when combining different tables.

## Combining Different Tables

A typical UNION use case: creating a unified activity feed or report from multiple source tables.

=== "SQLite"
    ```sql
    -- Activity log combining a specific customer's orders and reviews
    SELECT
        'order'   AS activity_type,
        customer_id,
        ordered_at AS activity_date,
        CAST(total_amount AS TEXT) AS detail
    FROM orders
    WHERE customer_id = 42

    UNION ALL

    SELECT
        'review'  AS activity_type,
        customer_id,
        created_at AS activity_date,
        '별점: ' || CAST(rating AS TEXT) AS detail
    FROM reviews
    WHERE customer_id = 42

    ORDER BY activity_date DESC;
    ```

=== "MySQL"
    ```sql
    SELECT
        'order'   AS activity_type,
        customer_id,
        ordered_at AS activity_date,
        CAST(total_amount AS CHAR) AS detail
    FROM orders
    WHERE customer_id = 42

    UNION ALL

    SELECT
        'review'  AS activity_type,
        customer_id,
        created_at AS activity_date,
        CONCAT('별점: ', rating) AS detail
    FROM reviews
    WHERE customer_id = 42

    ORDER BY activity_date DESC;
    ```

=== "PostgreSQL"
    ```sql
    SELECT
        'order'   AS activity_type,
        customer_id,
        ordered_at AS activity_date,
        total_amount::text AS detail
    FROM orders
    WHERE customer_id = 42

    UNION ALL

    SELECT
        'review'  AS activity_type,
        customer_id,
        created_at AS activity_date,
        '별점: ' || rating::text AS detail
    FROM reviews
    WHERE customer_id = 42

    ORDER BY activity_date DESC;
    ```

**Result:**

| activity_type | customer_id | activity_date | detail |
|---------------|------------:|---------------|--------|
| order | 42 | 2024-11-18 | 299.99 |
| review | 42 | 2024-11-20 | 별점: 5 |
| order | 42 | 2024-09-03 | 89.99 |
| review | 42 | 2024-09-05 | 별점: 4 |
| ... | | | |

```sql
-- All 2024 complaint and return events
SELECT
    'complaint'         AS event_type,
    c.customer_id,
    c.created_at        AS event_date,
    c.subject           AS description
FROM complaints AS c
WHERE c.created_at LIKE '2024%'

UNION ALL

SELECT
    'return'            AS event_type,
    o.customer_id,
    r.created_at        AS event_date,
    r.reason            AS description
FROM returns AS r
INNER JOIN orders AS o ON r.order_id = o.id
WHERE r.created_at LIKE '2024%'

ORDER BY event_date DESC
LIMIT 10;
```

## Creating Rollup Reports with UNION ALL

```sql
-- Category revenue + add total row
SELECT
    0 AS sort_key,
    cat.name AS category,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items AS oi
INNER JOIN products   AS p   ON oi.product_id = p.id
INNER JOIN categories AS cat ON p.category_id = cat.id
INNER JOIN orders     AS o   ON oi.order_id   = o.id
WHERE o.status IN ('delivered', 'confirmed')
  AND o.ordered_at LIKE '2024%'
GROUP BY cat.name

UNION ALL

SELECT
    1 AS sort_key,
    '합계' AS category,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items AS oi
INNER JOIN orders AS o ON oi.order_id = o.id
WHERE o.status IN ('delivered', 'confirmed')
  AND o.ordered_at LIKE '2024%'

ORDER BY sort_key, revenue DESC;
```

> **SQLite note:** `CASE` expressions cannot be used directly in `ORDER BY` with `UNION` / `UNION ALL`.
> Instead, adding a sort column (`sort_key`) to each `SELECT` as shown above is the most concise approach.

**Result (partial):**

| sort_key | category | revenue |
| ----------: | ---------- | ----------: |
| 0 | 게이밍 노트북 | 7252261700.0 |
| 0 | NVIDIA | 6049128000.0 |
| 0 | AMD | 5055980700.0 |
| 0 | 일반 노트북 | 4852629300.0 |
| 0 | 게이밍 모니터 | 3575676600.0 |
| 0 | 스피커/헤드셋 | 2473846600.0 |
| 0 | Intel 소켓 | 2265205100.0 |
| 0 | 2in1 | 2164737100.0 |
| ... | ... | ... |

## INTERSECT -- Intersection

`INTERSECT` returns only rows that exist in **both** query results.

```sql
-- Customers who both wrote reviews and filed complaints
SELECT customer_id FROM reviews
INTERSECT
SELECT customer_id FROM complaints;
```

> **SQLite note:** `INTERSECT` is supported in SQLite 3.34.0+ (2020-12). Also available in MySQL 8.0.31+ and all PostgreSQL versions.

```sql
-- Application: VIP customers who ordered in the last 6 months
SELECT id FROM customers WHERE grade = 'VIP'
INTERSECT
SELECT DISTINCT customer_id FROM orders
WHERE ordered_at >= DATE('now', '-6 months');
```

## EXCEPT / MINUS -- Set Difference

`EXCEPT` returns rows from the first query result that are **not in** the second query result. In Oracle, it's called `MINUS`.

```sql
-- Customers who wrote reviews but never filed complaints
SELECT customer_id FROM reviews
EXCEPT
SELECT customer_id FROM complaints;
```

```sql
-- Orders that were placed but shipping never started
SELECT id FROM orders WHERE status = 'confirmed'
EXCEPT
SELECT order_id FROM shipping;
```

> `EXCEPT` returns the same result as a `NOT IN` subquery or `LEFT JOIN ... IS NULL` anti-join, but the set operation syntax is more readable.

### Comparing UNION vs. INTERSECT vs. EXCEPT

| Operator | Meaning | Set Symbol |
|--------|------|:---------:|
| UNION | Union (A ∪ B) | ∪ |
| INTERSECT | Intersection (A ∩ B) | ∩ |
| EXCEPT | Difference (A − B) | − |

All three operations **remove duplicates**. To keep duplicates, use `UNION ALL`, `INTERSECT ALL`, `EXCEPT ALL` (support varies by database).

## Summary

| Concept | Description | Example |
|------|------|------|
| UNION | Combine results after removing duplicates | `SELECT ... UNION SELECT ...` |
| UNION ALL | Combine results keeping duplicates (faster) | `SELECT ... UNION ALL SELECT ...` |
| INTERSECT | Rows in both sides (intersection) | `SELECT ... INTERSECT SELECT ...` |
| EXCEPT | Rows only in the first (set difference) | `SELECT ... EXCEPT SELECT ...` |
| Column matching rule | Both SELECTs must have matching column count/types | Column names follow the first query |
| Combining different tables | Activity logs, feedback consolidation, etc. | Orders + Reviews -> Activity feed |
| Rollup reports | Add total row with UNION ALL | Control sorting with `sort_key` |
| ORDER BY placement | Once for entire result, at the very end | Written after the last SELECT |

!!! note "Lesson Review Problems"
    These are simple problems to immediately test the concepts from this lesson. For comprehensive practice combining multiple concepts, see the [Practice Problems](../exercises/index.md) section.

## Practice Problems
### Problem 1
Combine VIP grade customers' names and grades with GOLD grade customers' names and grades using `UNION` into a single list. Sort by name.

??? success "Answer"
    ```sql
    SELECT name, grade FROM customers WHERE grade = 'VIP'
    UNION
    SELECT name, grade FROM customers WHERE grade = 'GOLD'
    ORDER BY name;
    ```

    **Result (example):**

| name | grade |
| ---------- | ---------- |
| 강건우 | VIP |
| 강경수 | GOLD |
| 강경숙 | GOLD |
| 강경숙 | VIP |
| 강경자 | VIP |
| 강경희 | VIP |
| 강광수 | GOLD |
| 강광수 | VIP |
| ... | ... |


### Problem 2
Combine all active product (`is_active = 1`) names and all category names using `UNION` to create a deduplicated name list. The result column should be `name`.

??? success "Answer"
    ```sql
    SELECT name FROM products WHERE is_active = 1
    UNION
    SELECT name FROM categories
    ORDER BY name;
    ```

    **Result (example):**

| name |
| ---------- |
| 2in1 |
| AMD |
| AMD Ryzen 5 9600X |
| AMD Ryzen 7 7700X |
| AMD Ryzen 7 7700X 블랙 |
| AMD Ryzen 7 7800X3D 실버 |
| AMD Ryzen 7 9700X 블랙 |
| AMD Ryzen 7 9800X3D 실버 |
| ... |


### Problem 3
Create a "negative events" list combining cancelled and returned orders from 2023-2024. Use `UNION ALL` with `event_type` ('cancellation' or 'return'), `order_number`, `customer_id`, `event_date` (use `cancelled_at` for cancellations, `completed_at` for returns). Sort by `event_date` descending.

??? success "Answer"
    ```sql
    SELECT
        'cancellation'  AS event_type,
        order_number,
        customer_id,
        cancelled_at    AS event_date
    FROM orders
    WHERE status = 'cancelled'
      AND cancelled_at BETWEEN '2023-01-01' AND '2024-12-31 23:59:59'

    UNION ALL

    SELECT
        'return'        AS event_type,
        order_number,
        customer_id,
        completed_at    AS event_date
    FROM orders
    WHERE status = 'returned'
      AND completed_at BETWEEN '2023-01-01' AND '2024-12-31 23:59:59'

    ORDER BY event_date DESC;
    ```

    **Result (example):**

| event_type | order_number | customer_id | event_date |
| ---------- | ---------- | ----------: | ---------- |
| cancellation | ORD-20241231-350177 | 32033 | 2024-12-31 23:28:31 |
| cancellation | ORD-20241231-350116 | 3334 | 2024-12-31 23:20:07 |
| cancellation | ORD-20241231-350157 | 18367 | 2024-12-31 21:03:00 |
| cancellation | ORD-20241231-350139 | 12807 | 2024-12-31 20:48:41 |
| cancellation | ORD-20241229-349718 | 37593 | 2024-12-31 14:26:02 |
| cancellation | ORD-20241229-349755 | 42467 | 2024-12-31 13:21:15 |
| cancellation | ORD-20241229-349736 | 16388 | 2024-12-31 11:04:21 |
| cancellation | ORD-20241231-350057 | 12488 | 2024-12-31 09:51:04 |
| ... | ... | ... | ... |



### Problem 4
Create a "customer feedback" list combining 2024 reviews and 2024 product Q&A (questions only, `parent_id IS NULL`). Use `UNION ALL` with `feedback_type` ('review' or 'qna'), `product_id`, `customer_id`, `created_at`. Sort by `created_at` descending, showing only the top 20.

??? success "Answer"
    ```sql
    SELECT
        'review' AS feedback_type,
        product_id,
        customer_id,
        created_at
    FROM reviews
    WHERE created_at LIKE '2024%'

    UNION ALL

    SELECT
        'qna' AS feedback_type,
        product_id,
        customer_id,
        created_at
    FROM product_qna
    WHERE parent_id IS NULL
      AND created_at LIKE '2024%'

    ORDER BY created_at DESC
    LIMIT 20;
    ```

    **Result (example):**

| feedback_type | product_id | customer_id | created_at |
| ---------- | ----------: | ----------: | ---------- |
| review | 2482 | 26230 | 2024-12-31 22:49:53 |
| review | 2445 | 38978 | 2024-12-31 22:48:10 |
| review | 1842 | 37715 | 2024-12-31 22:44:19 |
| review | 870 | 19358 | 2024-12-31 22:35:38 |
| review | 2345 | 15403 | 2024-12-31 22:29:15 |
| review | 1469 | 14808 | 2024-12-31 22:19:15 |
| review | 2093 | 15646 | 2024-12-31 21:58:54 |
| review | 1913 | 29231 | 2024-12-31 21:50:02 |
| ... | ... | ... | ... |


### Problem 5
Aggregate count by payment method, then add a total row with `UNION ALL`. Display `'Total'` for the total row's `method`. Target only payments where `status = 'completed'`.

??? success "Answer"
    ```sql
    SELECT
        0 AS sort_key,
        method,
        COUNT(*) AS tx_count
    FROM payments
    WHERE status = 'completed'
    GROUP BY method

    UNION ALL

    SELECT
        1 AS sort_key,
        '합계' AS method,
        COUNT(*) AS tx_count
    FROM payments
    WHERE status = 'completed'

    ORDER BY sort_key, tx_count DESC;
    ```

    **Result (example):**

| sort_key | method | tx_count |
| ----------: | ---------- | ----------: |
| 0 | card | 172644 |
| 0 | kakao_pay | 76533 |
| 0 | naver_pay | 57725 |
| 0 | bank_transfer | 38667 |
| 0 | point | 19247 |
| 0 | virtual_account | 19067 |
| 1 | 합계 | 383883 |
| ... | ... | ... |


### Problem 6
Aggregate count by customer grade, then add a grand total row (`'Total'`) with `UNION ALL`. Target only `is_active = 1` customers. Sort so the total row comes last.

??? success "Answer"
    ```sql
    SELECT
        0 AS sort_key,
        grade,
        COUNT(*) AS cnt
    FROM customers
    WHERE is_active = 1
    GROUP BY grade

    UNION ALL

    SELECT
        1 AS sort_key,
        '전체' AS grade,
        COUNT(*) AS cnt
    FROM customers
    WHERE is_active = 1

    ORDER BY sort_key, cnt DESC;
    ```

    **Result (example):**

| sort_key | grade | cnt |
| ----------: | ---------- | ----------: |
| 0 | BRONZE | 22615 |
| 0 | GOLD | 5159 |
| 0 | SILVER | 5105 |
| 0 | VIP | 3886 |
| 1 | 전체 | 36765 |
| ... | ... | ... |


### Problem 7
Create a customer engagement summary. Use `UNION ALL` to aggregate total orders, total reviews, and total complaints per customer. Wrap the union result as a subquery (derived table) to aggregate into one row per customer, and return the top 10 by total activity count.

??? success "Answer"
    ```sql
    SELECT
        customer_id,
        SUM(activity_count) AS total_activity
    FROM (
        SELECT customer_id, COUNT(*) AS activity_count
        FROM orders GROUP BY customer_id

        UNION ALL

        SELECT customer_id, COUNT(*) AS activity_count
        FROM reviews GROUP BY customer_id

        UNION ALL

        SELECT customer_id, COUNT(*) AS activity_count
        FROM complaints GROUP BY customer_id
    ) AS all_activity
    GROUP BY customer_id
    ORDER BY total_activity DESC
    LIMIT 10;
    ```

    **Result (example):**

| customer_id | total_activity |
| ----------: | ----------: |
| 226 | 934 |
| 840 | 760 |
| 356 | 751 |
| 1000 | 745 |
| 903 | 720 |
| 98 | 706 |
| 97 | 646 |
| 549 | 614 |
| ... | ... |


### Problem 8
Aggregate count and average amount by order status, then add a total row with `UNION ALL`. Wrap the result as a subquery to calculate `pct` (the percentage each status count represents of the total, to 1 decimal place).

??? success "Answer"
    ```sql
    SELECT
        status,
        order_count,
        avg_amount,
        ROUND(100.0 * order_count / SUM(order_count) OVER (), 1) AS pct
    FROM (
        SELECT
            0 AS sort_key,
            status,
            COUNT(*)            AS order_count,
            ROUND(AVG(total_amount), 2) AS avg_amount
        FROM orders
        GROUP BY status

        UNION ALL

        SELECT
            1 AS sort_key,
            '합계' AS status,
            COUNT(*)            AS order_count,
            ROUND(AVG(total_amount), 2) AS avg_amount
        FROM orders
    ) AS t
    ORDER BY sort_key, order_count DESC;
    ```

    **Result (example):**

| status | order_count | avg_amount | pct |
| ---------- | ----------: | ----------: | ----------: |
| confirmed | 382081 | 1027607.87 | 45.7 |
| cancelled | 21018 | 1050491.89 | 2.5 |
| return_requested | 6125 | 1443121.76 | 0.7 |
| returned | 6071 | 1441435.9 | 0.7 |
| delivered | 1029 | 1088372.25 | 0.1 |
| pending | 706 | 1050719.36 | 0.1 |
| shipped | 453 | 1144727.89 | 0.1 |
| paid | 167 | 928779.1 | 0.0 |
| ... | ... | ... | ... |


### Problem 9
Aggregate active and inactive product counts per supplier separately, combine with `UNION ALL`, then wrap as a subquery to create one row per supplier (active count, inactive count). JOIN with the `suppliers` table to also display company name.

??? success "Answer"
    ```sql
    SELECT
        s.company_name,
        SUM(CASE WHEN t.status_type = 'active' THEN t.cnt ELSE 0 END) AS active_count,
        SUM(CASE WHEN t.status_type = 'inactive' THEN t.cnt ELSE 0 END) AS inactive_count
    FROM (
        SELECT supplier_id, 'active' AS status_type, COUNT(*) AS cnt
        FROM products WHERE is_active = 1
        GROUP BY supplier_id

        UNION ALL

        SELECT supplier_id, 'inactive' AS status_type, COUNT(*) AS cnt
        FROM products WHERE is_active = 0
        GROUP BY supplier_id
    ) AS t
    INNER JOIN suppliers AS s ON t.supplier_id = s.id
    GROUP BY s.company_name
    ORDER BY active_count DESC;
    ```

    **Result (example):**

| company_name | active_count | inactive_count |
| ---------- | ----------: | ----------: |
| 에이수스코리아 | 187 | 43 |
| 삼성전자 공식 유통 | 158 | 53 |
| MSI코리아 | 117 | 20 |
| 로지텍코리아 | 112 | 41 |
| 레이저코리아 | 105 | 19 |
| 서린시스테크 | 104 | 16 |
| 앱솔루트 테크놀로지 | 102 | 27 |
| LG전자 공식 유통 | 93 | 25 |
| ... | ... | ... |


### Problem 10
Combine the 'highest priced product' and 'lowest priced product' per supplier into one list. Use `UNION ALL` with `price_type` ('highest' or 'lowest'), `company_name`, `product_name`, `price`. Sort by `company_name`, `price_type`.

??? success "Answer"
    ```sql
    SELECT
        '최고가' AS price_type,
        s.company_name,
        p.name  AS product_name,
        p.price
    FROM products AS p
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    WHERE p.is_active = 1
      AND p.price = (
          SELECT MAX(p2.price)
          FROM products AS p2
          WHERE p2.supplier_id = p.supplier_id AND p2.is_active = 1
      )

    UNION ALL

    SELECT
        '최저가' AS price_type,
        s.company_name,
        p.name  AS product_name,
        p.price
    FROM products AS p
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    WHERE p.is_active = 1
      AND p.price = (
          SELECT MIN(p2.price)
          FROM products AS p2
          WHERE p2.supplier_id = p.supplier_id AND p2.is_active = 1
      )

    ORDER BY company_name, price_type;
    ```


### Problem 11
Find the **intersection** of customers who wrote reviews and customers who filed complaints. Use `INTERSECT` and count the resulting `customer_id`s.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS both_count
    FROM (
        SELECT customer_id FROM reviews
        INTERSECT
        SELECT customer_id FROM complaints
    ) AS both_active;
    ```


### Problem 12
Use `EXCEPT` to find customers who added products to their wishlist but never placed an order. Return `customer_id`, sorted ascending.

??? success "Answer"
    ```sql
    SELECT customer_id FROM wishlists
    EXCEPT
    SELECT DISTINCT customer_id FROM orders
    ORDER BY customer_id;
    ```


### Scoring Guide

| Score | Next Step |
|:----:|----------|
| **11-12** | Move on to [Lesson 15: DML](15-dml.md) |
| **8-10** | Review the explanations for incorrect answers, then proceed |
| **Half or fewer** | Re-read this lesson |
| **3 or fewer** | Start again from [Lesson 13: Numeric, Conversion, and Conditional Functions](13-utility-functions.md) |

**Problem Areas:**

| Area | Problems |
|------|:--------:|
| Basic UNION (dedup) | 1, 2 |
| UNION ALL + combining different tables | 3, 4 |
| UNION ALL + total row (rollup) | 5, 6 |
| UNION ALL + subquery aggregation | 7, 8, 9 |
| UNION ALL + correlated subquery | 10 |
| INTERSECT (intersection) | 11 |
| EXCEPT (set difference) | 12 |

---
Next: [Lesson 15: INSERT, UPDATE, DELETE](15-dml.md)
