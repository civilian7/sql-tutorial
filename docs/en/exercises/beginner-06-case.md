# CASE Expressions

!!! info "Tables"

    `products` — Products (name, price, stock, brand)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `reviews` — Reviews (rating, content)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `CASE WHEN THEN ELSE END`, `Simple CASE`, `Searched CASE`, `CASE + aggregation`, `CASE + sorting`



### 1. Query customer names and tiers, displaying the tier in Korea


Query customer names and tiers, displaying the tier in Korean. BRONZE='브론즈', SILVER='실버', GOLD='골드', VIP='VIP'


**Hint 1:** Simple CASE syntax: `CASE column WHEN value1 THEN result1 WHEN value2 THEN result2 ... END`


??? success "Answer"
    ```sql
    SELECT name,
           CASE grade
               WHEN 'BRONZE' THEN '브론즈'
               WHEN 'SILVER' THEN '실버'
               WHEN 'GOLD' THEN '골드'
               WHEN 'VIP' THEN 'VIP'
           END AS grade_kr
    FROM customers
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | grade_kr |
    |---|---|
    | Joshua Atkins | 브론즈 |
    | Danny Johnson | 골드 |
    | Adam Moore | VIP |
    | Virginia Steele | 골드 |
    | Jared Vazquez | 실버 |
    | Benjamin Skinner | 브론즈 |
    | Ashley Jones | 브론즈 |


---


### 2. Display the product name, price, and price tier. Under 100K=


Display the product name, price, and price tier. Under 100K='Budget', 100K-500K='Mid-low', 500K-1M='Mid', 1M+='Premium'


**Hint 1:** Searched CASE syntax: `CASE WHEN condition1 THEN result1 WHEN condition2 THEN result2 ... ELSE default END`. Conditions are evaluated top-to-bottom, so order matters.


??? success "Answer"
    ```sql
    SELECT name, price,
           CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier
    FROM products
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | price | price_tier |
    |---|---|---|
    | Razer Blade 18 Black | 2,987,500.00 | 고가 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | 고가 |
    | Samsung DDR4 32GB PC4-25600 | 43,500.00 | 저가 |
    | Dell U2724D | 894,100.00 | 중가 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 167,000.00 | 중저가 |
    | MSI Radeon RX 9070 VENTUS 3X White | 383,100.00 | 중저가 |
    | Samsung DDR5 32GB PC5-38400 | 211,800.00 | 중저가 |


---


### 3. Query order numbers and statuses, displaying the status in K


Query order numbers and statuses, displaying the status in Korean. pending='주문접수', paid='결제완료', preparing='준비중', shipped='배송중', delivered='배송완료', confirmed='구매확정', cancelled='취소', return_requested='반품요청', returned='반품완료'


**Hint 1:** Use simple CASE to convert status values to Korean.


??? success "Answer"
    ```sql
    SELECT order_number,
           CASE status
               WHEN 'pending' THEN '주문접수'
               WHEN 'paid' THEN '결제완료'
               WHEN 'preparing' THEN '준비중'
               WHEN 'shipped' THEN '배송중'
               WHEN 'delivered' THEN '배송완료'
               WHEN 'confirmed' THEN '구매확정'
               WHEN 'cancelled' THEN '취소'
               WHEN 'return_requested' THEN '반품요청'
               WHEN 'returned' THEN '반품완료'
           END AS status_kr
    FROM orders
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_number | status_kr |
    |---|---|
    | ORD-20251231-37555 | 주문접수 |
    | ORD-20251231-37543 | 주문접수 |
    | ORD-20251231-37552 | 주문접수 |
    | ORD-20251231-37548 | 주문접수 |
    | ORD-20251231-37542 | 주문접수 |
    | ORD-20251231-37546 | 주문접수 |
    | ORD-20251231-37547 | 주문접수 |


---


### 4. Display review ratings as text. 5='Excellent', 4='Good', 3='


Display review ratings as text. 5='Excellent', 4='Good', 3='Average', 2='Poor', 1='Terrible'


**Hint 1:** Use simple CASE: `CASE rating WHEN 5 THEN 'Excellent' ...`


??? success "Answer"
    ```sql
    SELECT rating,
           CASE rating
               WHEN 5 THEN '최고'
               WHEN 4 THEN '좋음'
               WHEN 3 THEN '보통'
               WHEN 2 THEN '별로'
               WHEN 1 THEN '최악'
           END AS rating_text,
           title
    FROM reviews
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | rating | rating_text | title |
    |---|---|---|
    | 2 | 별로 | Disappointing |
    | 5 | 최고 | Highly Recommend |
    | 4 | 좋음 | Satisfied |
    | 4 | 좋음 | Not Bad |
    | 5 | 최고 | NULL |
    | 3 | 보통 | It's Okay |
    | 4 | 좋음 | Recommended |


---


### 5. Display the stock status of products. Stock 0='Out of stock'


Display the stock status of products. Stock 0='Out of stock', 1-10='Low', 11-100='Normal', 101+='Sufficient'


**Hint 1:** Use the `stock_qty` range as conditions in a searched CASE.


??? success "Answer"
    ```sql
    SELECT name, stock_qty,
           CASE
               WHEN stock_qty = 0 THEN '품절'
               WHEN stock_qty <= 10 THEN '부족'
               WHEN stock_qty <= 100 THEN '보통'
               ELSE '충분'
           END AS stock_status
    FROM products
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | stock_qty | stock_status |
    |---|---|---|
    | Razer Blade 18 Black | 107 | 충분 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 499 | 충분 |
    | Samsung DDR4 32GB PC4-25600 | 359 | 충분 |
    | Dell U2724D | 337 | 충분 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 59 | 보통 |
    | MSI Radeon RX 9070 VENTUS 3X White | 460 | 충분 |
    | Samsung DDR5 32GB PC5-38400 | 340 | 충분 |


---


### 6. Display the payment method (`method`) in Korean. card='신용카드'


Display the payment method (`method`) in Korean. card='신용카드', bank_transfer='계좌이체', virtual_account='가상계좌', kakao_pay='카카오페이', naver_pay='네이버페이', point='포인트'. Show only the top 10 rows.


**Hint 1:** Use simple CASE to convert method values to Korean.


??? success "Answer"
    ```sql
    SELECT order_id,
           CASE method
               WHEN 'card' THEN '신용카드'
               WHEN 'bank_transfer' THEN '계좌이체'
               WHEN 'virtual_account' THEN '가상계좌'
               WHEN 'kakao_pay' THEN '카카오페이'
               WHEN 'naver_pay' THEN '네이버페이'
               WHEN 'point' THEN '포인트'
           END AS method_kr,
           amount
    FROM payments
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_id | method_kr | amount |
    |---|---|---|
    | 1 | 신용카드 | 167,000.00 |
    | 2 | 신용카드 | 211,800.00 |
    | 3 | 신용카드 | 704,800.00 |
    | 4 | 신용카드 | 167,000.00 |
    | 5 | 카카오페이 | 534,490.00 |
    | 6 | 신용카드 | 167,000.00 |
    | 7 | 신용카드 | 687,400.00 |


---


### 7. Display the customer active status as text. is_active 1='Act


Display the customer active status as text. is_active 1='Active', 0='Withdrawn'


**Hint 1:** Use `CASE is_active WHEN 1 THEN 'Active' WHEN 0 THEN 'Withdrawn' END` or a searched CASE.


??? success "Answer"
    ```sql
    SELECT name, email,
           CASE is_active
               WHEN 1 THEN '활성'
               WHEN 0 THEN '탈퇴'
           END AS status
    FROM customers
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | email | status |
    |---|---|---|
    | Joshua Atkins | user1@testmail.kr | 탈퇴 |
    | Danny Johnson | user2@testmail.kr | 활성 |
    | Adam Moore | user3@testmail.kr | 활성 |
    | Virginia Steele | user4@testmail.kr | 활성 |
    | Jared Vazquez | user5@testmail.kr | 활성 |
    | Benjamin Skinner | user6@testmail.kr | 탈퇴 |
    | Ashley Jones | user7@testmail.kr | 탈퇴 |


---


### 8. Display the order amount tier. Under 50K='Small', 50K-200K='


Display the order amount tier. Under 50K='Small', 50K-200K='Regular', 200K-1M='Large', 1M+='VIP-level'. Show the 10 most recent orders.


**Hint 1:** Use searched CASE to categorize `total_amount` ranges.


??? success "Answer"
    ```sql
    SELECT order_number, total_amount,
           CASE
               WHEN total_amount < 50000 THEN '소액'
               WHEN total_amount < 200000 THEN '일반'
               WHEN total_amount < 1000000 THEN '고액'
               ELSE 'VIP급'
           END AS amount_tier
    FROM orders
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_number | total_amount | amount_tier |
    |---|---|---|
    | ORD-20251231-37555 | 74,800.00 | 일반 |
    | ORD-20251231-37543 | 134,100.00 | 일반 |
    | ORD-20251231-37552 | 254,300.00 | 고액 |
    | ORD-20251231-37548 | 187,700.00 | 일반 |
    | ORD-20251231-37542 | 155,700.00 | 일반 |
    | ORD-20251231-37546 | 198,300.00 | 일반 |
    | ORD-20251231-37547 | 335,000.00 | 고액 |


---


### 9. Display the comprehensive sale status of products. If is_act


Display the comprehensive sale status of products. If is_active is 0, show 'Discontinued'; if stock_qty is 0, show 'Out of stock'; otherwise show 'On sale'


**Hint 1:** CASE evaluates conditions top-to-bottom. Check discontinuation first, then out-of-stock.


??? success "Answer"
    ```sql
    SELECT name, price, is_active, stock_qty,
           CASE
               WHEN is_active = 0 THEN '단종'
               WHEN stock_qty = 0 THEN '품절'
               ELSE '판매중'
           END AS sale_status
    FROM products
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | price | is_active | stock_qty | sale_status |
    |---|---|---|---|---|
    | Razer Blade 18 Black | 2,987,500.00 | 1 | 107 | 판매중 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | 1 | 499 | 판매중 |
    | Samsung DDR4 32GB PC4-25600 | 43,500.00 | 1 | 359 | 판매중 |
    | Dell U2724D | 894,100.00 | 1 | 337 | 판매중 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 167,000.00 | 1 | 59 | 판매중 |
    | MSI Radeon RX 9070 VENTUS 3X White | 383,100.00 | 1 | 460 | 판매중 |
    | Samsung DDR5 32GB PC5-38400 | 211,800.00 | 1 | 340 | 판매중 |


---


### 10. Display the customer points level. 0='None', 1-5000='Low', 5


Display the customer points level. 0='None', 1-5000='Low', 5001-20000='Medium', 20001+='High'. Show only the top 10 rows.


**Hint 1:** Classify `point_balance` ranges using searched CASE.


??? success "Answer"
    ```sql
    SELECT name, point_balance,
           CASE
               WHEN point_balance = 0 THEN '없음'
               WHEN point_balance <= 5000 THEN '소액'
               WHEN point_balance <= 20000 THEN '보통'
               ELSE '고액'
           END AS point_level
    FROM customers
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | point_balance | point_level |
    |---|---|---|
    | Joshua Atkins | 0 | 없음 |
    | Danny Johnson | 664,723 | 고액 |
    | Adam Moore | 1,564,015 | 고액 |
    | Virginia Steele | 930,784 | 고액 |
    | Jared Vazquez | 963,430 | 고액 |
    | Benjamin Skinner | 0 | 없음 |
    | Ashley Jones | 0 | 없음 |


---


### 11. Classify products by price tier and find the product count p


Classify products by price tier and find the product count per tier. Under 100K='Budget', 100K-500K='Mid-low', 500K-1M='Mid', 1M+='Premium'


**Hint 1:** Use the CASE expression in both `SELECT` and `GROUP BY`.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier,
           COUNT(*) AS product_count
    FROM products
    GROUP BY CASE
                 WHEN price < 100000 THEN '저가'
                 WHEN price < 500000 THEN '중저가'
                 WHEN price < 1000000 THEN '중가'
                 ELSE '고가'
             END
    ORDER BY product_count DESC;
    ```


    **Result** (4 rows)

    | price_tier | product_count |
    |---|---|
    | 중저가 | 130 |
    | 고가 | 65 |
    | 저가 | 47 |
    | 중가 | 38 |


---


### 12. Classify orders into 3 major status groups and find the coun


Classify orders into 3 major status groups and find the count for each. pending/paid/preparing='Processing', shipped/delivered/confirmed='Completed', cancelled/return_requested/returned='Cancelled/Returned'


**Hint 1:** Use `CASE WHEN status IN (...) THEN ...` to group multiple values into a single category.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN status IN ('pending', 'paid', 'preparing') THEN '처리중'
               WHEN status IN ('shipped', 'delivered', 'confirmed') THEN '완료'
               WHEN status IN ('cancelled', 'return_requested', 'returned') THEN '취소/반품'
           END AS status_group,
           COUNT(*) AS order_count
    FROM orders
    GROUP BY status_group
    ORDER BY order_count DESC;
    ```


    **Result** (3 rows)

    | status_group | order_count |
    |---|---|
    | 완료 | 34,569 |
    | 취소/반품 | 2859 |
    | 처리중 | 129 |


---


### 13. Classify reviews as Positive (4-5 stars), Neutral (3 stars),


Classify reviews as Positive (4-5 stars), Neutral (3 stars), or Negative (1-2 stars) and find the count for each group.


**Hint 1:** Use searched CASE to divide the rating range into 3 groups.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN rating >= 4 THEN '긍정'
               WHEN rating = 3 THEN '보통'
               ELSE '부정'
           END AS sentiment,
           COUNT(*) AS review_count
    FROM reviews
    GROUP BY sentiment
    ORDER BY review_count DESC;
    ```


    **Result** (3 rows)

    | sentiment | review_count |
    |---|---|
    | 긍정 | 6008 |
    | 부정 | 1273 |
    | 보통 | 1265 |


---


### 14. Classify products by price tier and find the average stock q


Classify products by price tier and find the average stock quantity per tier. Round to no decimal places.


**Hint 1:** Classify the price tier with CASE and calculate the average stock with `AVG(stock_qty)`.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier,
           COUNT(*) AS product_count,
           ROUND(AVG(stock_qty)) AS avg_stock
    FROM products
    GROUP BY price_tier
    ORDER BY avg_stock DESC;
    ```


    **Result** (4 rows)

    | price_tier | product_count | avg_stock |
    |---|---|---|
    | 중가 | 38 | 282.00 |
    | 중저가 | 130 | 277.00 |
    | 고가 | 65 | 271.00 |
    | 저가 | 47 | 267.00 |


---


### 15. Classify customers by gender, displaying NULL as 'Not entere


Classify customers by gender, displaying NULL as 'Not entered', and find the count per group.


**Hint 1:** Handle NULL first: `CASE WHEN gender IS NULL THEN 'Not entered' WHEN gender = 'M' THEN 'Male' ...`


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN gender IS NULL THEN '미입력'
               WHEN gender = 'M' THEN '남성'
               WHEN gender = 'F' THEN '여성'
           END AS gender_kr,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY gender_kr
    ORDER BY customer_count DESC;
    ```


    **Result** (3 rows)

    | gender_kr | customer_count |
    |---|---|
    | 남성 | 3032 |
    | 여성 | 1669 |
    | 미입력 | 529 |


---


### 16. Find the count and average payment amount per payment method


Find the count and average payment amount per payment method, displaying the method in Korean. Round the average amount to the nearest won.


**Hint 1:** Convert method to Korean with CASE, then use GROUP BY and aggregate functions together.


??? success "Answer"
    ```sql
    SELECT CASE method
               WHEN 'card' THEN '신용카드'
               WHEN 'bank_transfer' THEN '계좌이체'
               WHEN 'virtual_account' THEN '가상계좌'
               WHEN 'kakao_pay' THEN '카카오페이'
               WHEN 'naver_pay' THEN '네이버페이'
               WHEN 'point' THEN '포인트'
           END AS method_kr,
           COUNT(*) AS payment_count,
           ROUND(AVG(amount)) AS avg_amount
    FROM payments
    GROUP BY method
    ORDER BY payment_count DESC;
    ```


    **Result** (6 rows)

    | method_kr | payment_count | avg_amount |
    |---|---|---|
    | 신용카드 | 16,841 | 1,009,735.00 |
    | 카카오페이 | 7486 | 1,010,397.00 |
    | 네이버페이 | 5715 | 1,049,665.00 |
    | 계좌이체 | 3718 | 1,009,454.00 |
    | 포인트 | 1921 | 1,015,809.00 |
    | 가상계좌 | 1876 | 1,018,848.00 |


---


### 17. Sort products with out-of-stock items (stock_qty=0) at the b


Sort products with out-of-stock items (stock_qty=0) at the bottom, and the rest by price ascending. Show only the top 15 rows.


**Hint 1:** Using CASE in `ORDER BY` enables custom sorting. Return 1 for out-of-stock and 0 otherwise to push out-of-stock items to the bottom.


??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE is_active = 1
    ORDER BY CASE WHEN stock_qty = 0 THEN 1 ELSE 0 END,
             price ASC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | price | stock_qty |
    |---|---|---|
    | TP-Link TG-3468 Black | 18,500.00 | 353 |
    | Samsung SPA-KFG0BUB Silver | 21,900.00 | 488 |
    | Arctic Freezer 36 A-RGB White | 29,900.00 | 346 |
    | TP-Link Archer TBE400E White | 30,200.00 | 393 |
    | Samsung SPA-KFG0BUB | 30,700.00 | 4 |
    | TP-Link TL-SG1016D Silver | 36,100.00 | 275 |
    | Microsoft Bluetooth Keyboard White | 36,800.00 | 369 |


---


### 18. Sort customer tiers in custom order (VIP > GOLD > SILVER > B


Sort customer tiers in custom order (VIP > GOLD > SILVER > BRONZE) and show the customer count per tier.


**Hint 1:** Use `ORDER BY CASE grade WHEN 'VIP' THEN 1 WHEN 'GOLD' THEN 2 ...` to specify the desired order.


??? success "Answer"
    ```sql
    SELECT grade, COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade
    ORDER BY CASE grade
                 WHEN 'VIP' THEN 1
                 WHEN 'GOLD' THEN 2
                 WHEN 'SILVER' THEN 3
                 WHEN 'BRONZE' THEN 4
             END;
    ```


    **Result** (4 rows)

    | grade | customer_count |
    |---|---|
    | VIP | 368 |
    | GOLD | 524 |
    | SILVER | 479 |
    | BRONZE | 3859 |


---


### 19. Find the order count and total revenue per order amount tier


Find the order count and total revenue per order amount tier. Tiers: under 50K, 50K-200K, 200K-1M, 1M+


**Hint 1:** Classify the amount tier with CASE, then aggregate with `COUNT(*)` and `SUM(total_amount)` together.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN total_amount < 50000 THEN '5만원 미만'
               WHEN total_amount < 200000 THEN '5~20만원'
               WHEN total_amount < 1000000 THEN '20~100만원'
               ELSE '100만원 이상'
           END AS amount_tier,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue
    FROM orders
    GROUP BY amount_tier
    ORDER BY total_revenue DESC;
    ```


    **Result** (4 rows)

    | amount_tier | order_count | total_revenue |
    |---|---|---|
    | 100만원 이상 | 12,860 | 31,080,780,277.00 |
    | 20~100만원 | 12,513 | 5,858,099,764.00 |
    | 5~20만원 | 9865 | 1,161,433,506.00 |
    | 5만원 미만 | 2319 | 83,181,516.00 |


---


### 20. Classify reviews by rating group (Positive/Neutral/Negative)


Classify reviews by rating group (Positive/Neutral/Negative) and find the percentage (%) of reviews with a title.


**Hint 1:** Calculate the non-NULL title ratio with `COUNT(title) * 100.0 / COUNT(*)`. Group by rating with CASE, then GROUP BY.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN rating >= 4 THEN '긍정'
               WHEN rating = 3 THEN '보통'
               ELSE '부정'
           END AS sentiment,
           COUNT(*) AS review_count,
           ROUND(COUNT(title) * 100.0 / COUNT(*), 1) AS title_rate_pct
    FROM reviews
    GROUP BY sentiment
    ORDER BY review_count DESC;
    ```


    **Result** (3 rows)

    | sentiment | review_count | title_rate_pct |
    |---|---|---|
    | 긍정 | 6008 | 80.70 |
    | 부정 | 1273 | 80.40 |
    | 보통 | 1265 | 80.10 |


---


### 21. Classify products by margin rate tier. Margin rate = (price 


Classify products by margin rate tier. Margin rate = (price - cost_price) / price * 100. Under 10%='Low margin', 10-20%='Standard', 20-30%='High margin', 30%+='Premium'. For active products only (is_active = 1), find the product count and average margin rate per tier.


**Hint 1:** Use the margin rate formula directly in the CASE conditions. Calculate with `(price - cost_price) * 100.0 / price`.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN (price - cost_price) * 100.0 / price < 10 THEN '저마진'
               WHEN (price - cost_price) * 100.0 / price < 20 THEN '표준'
               WHEN (price - cost_price) * 100.0 / price < 30 THEN '고마진'
               ELSE '프리미엄'
           END AS margin_tier,
           COUNT(*) AS product_count,
           ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1
    GROUP BY margin_tier
    ORDER BY avg_margin_pct DESC;
    ```


    **Result** (4 rows)

    | margin_tier | product_count | avg_margin_pct |
    |---|---|---|
    | 프리미엄 | 71 | 37.20 |
    | 고마진 | 75 | 25.80 |
    | 표준 | 44 | 15.00 |
    | 저마진 | 28 | -0.9 |


---


### 22. Classify customers by signup year and tier, and find the cou


Classify customers by signup year and tier, and find the count. Extract the signup year with SUBSTR(created_at, 1, 4). Only include the last 3 years (2023, 2024, 2025).


**Hint 1:** Use both `SUBSTR(created_at, 1, 4)` and `grade` in `GROUP BY`. Filter years with `WHERE`, not `HAVING`.


??? success "Answer"
    ```sql
    SELECT SUBSTR(created_at, 1, 4) AS join_year,
           grade,
           COUNT(*) AS customer_count
    FROM customers
    WHERE SUBSTR(created_at, 1, 4) IN ('2023', '2024', '2025')
    GROUP BY join_year, grade
    ORDER BY join_year, CASE grade
                            WHEN 'VIP' THEN 1
                            WHEN 'GOLD' THEN 2
                            WHEN 'SILVER' THEN 3
                            WHEN 'BRONZE' THEN 4
                        END;
    ```


    **Result** (top 7 of 12 rows)

    | join_year | grade | customer_count |
    |---|---|---|
    | 2023 | VIP | 58 |
    | 2023 | GOLD | 67 |
    | 2023 | SILVER | 54 |
    | 2023 | BRONZE | 421 |
    | 2024 | VIP | 57 |
    | 2024 | GOLD | 83 |
    | 2024 | SILVER | 73 |


---


### 23. Analyze the shipping fee policy. Orders under 50K are charge


Analyze the shipping fee policy. Orders under 50K are charged shipping, orders 50K+ get free shipping. For 2024 orders, find the count, average order amount, and total shipping fee for paid/free shipping.


**Hint 1:** Classify with `CASE WHEN total_amount < 50000 THEN 'Paid shipping' ELSE 'Free shipping' END`.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN total_amount < 50000 THEN '유료배송'
               ELSE '무료배송'
           END AS shipping_type,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(SUM(shipping_fee)) AS total_shipping_fee
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY shipping_type;
    ```


    **Result** (2 rows)

    | shipping_type | order_count | avg_amount | total_shipping_fee |
    |---|---|---|---|
    | 무료배송 | 5470 | 1,025,770.00 | 327,000.00 |
    | 유료배송 | 315 | 36,445.00 | 939,000.00 |


---


### 24. Find the count per payment status, displaying the status in 


Find the count per payment status, displaying the status in Korean, and also show the percentage (%) of 'completed' payments.


**Hint 1:** Calculate the ratio of a specific condition to the total with `SUM(CASE WHEN ... THEN 1 ELSE 0 END) * 100.0 / COUNT(*)`.


??? success "Answer"
    ```sql
    SELECT CASE status
               WHEN 'completed' THEN '완료'
               WHEN 'pending' THEN '대기'
               WHEN 'failed' THEN '실패'
               WHEN 'refunded' THEN '환불'
           END AS status_kr,
           COUNT(*) AS payment_count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM payments
    GROUP BY status
    ORDER BY payment_count DESC;
    ```


    **Result** (4 rows)

    | status_kr | payment_count | pct |
    |---|---|---|
    | 완료 | 34,616 | 92.20 |
    | 환불 | 1930 | 5.10 |
    | 실패 | 929 | 2.50 |
    | 대기 | 82 | 0.2 |


---


### 25. Classify customers into 3 activity levels. Withdrawn (is_act


Classify customers into 3 activity levels. Withdrawn (is_active=0), Dormant (is_active=1 but last_login_at is NULL), Active (the rest). Find the customer count per group.


**Hint 1:** The order of CASE conditions matters. Check `is_active = 0` first, then `last_login_at IS NULL`.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN is_active = 0 THEN '탈퇴'
               WHEN last_login_at IS NULL THEN '휴면'
               ELSE '활동'
           END AS activity_status,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY activity_status
    ORDER BY customer_count DESC;
    ```


    **Result** (3 rows)

    | activity_status | customer_count |
    |---|---|
    | 활동 | 3471 |
    | 탈퇴 | 1570 |
    | 휴면 | 189 |


---


### 26. Find the monthly order count for 2024, displaying the season


Find the monthly order count for 2024, displaying the season as well. Mar-May='Spring', Jun-Aug='Summer', Sep-Nov='Fall', Dec-Feb='Winter'


**Hint 1:** Extract the month with `CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER)`. Classify the season with CASE.


??? success "Answer"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 7) AS month,
           CASE
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (3, 4, 5) THEN '봄'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (6, 7, 8) THEN '여름'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (9, 10, 11) THEN '가을'
               ELSE '겨울'
           END AS season,
           COUNT(*) AS order_count
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```


    **Result** (top 7 of 12 rows)

    | month | season | order_count |
    |---|---|---|
    | 2024-01 | 겨울 | 346 |
    | 2024-02 | 겨울 | 465 |
    | 2024-03 | 봄 | 601 |
    | 2024-04 | 봄 | 506 |
    | 2024-05 | 봄 | 415 |
    | 2024-06 | 여름 | 415 |
    | 2024-07 | 여름 | 414 |


---


### 27. Find the product count and average price per brand, showing 


Find the product count and average price per brand, showing only brands with 10+ products. Classify brands by average price as 'Premium brand' (1M+), 'Mainstream brand' (300K-1M), or 'Budget brand' (under 300K).


**Hint 1:** Filter with `GROUP BY brand` + `HAVING COUNT(*) >= 10`, then classify the average price with `CASE`.


??? success "Answer"
    ```sql
    SELECT brand,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price,
           CASE
               WHEN AVG(price) >= 1000000 THEN '프리미엄 브랜드'
               WHEN AVG(price) >= 300000 THEN '대중 브랜드'
               ELSE '보급형 브랜드'
           END AS brand_tier
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY avg_price DESC;
    ```


    **Result** (6 rows)

    | brand | product_count | avg_price | brand_tier |
    |---|---|---|---|
    | ASUS | 21 | 1,589,552.00 | 프리미엄 브랜드 |
    | LG | 11 | 1,346,836.00 | 프리미엄 브랜드 |
    | MSI | 12 | 820,292.00 | 대중 브랜드 |
    | Samsung | 21 | 641,800.00 | 대중 브랜드 |
    | TP-Link | 11 | 128,764.00 | 보급형 브랜드 |
    | Logitech | 11 | 115,127.00 | 보급형 브랜드 |


---


### 28. Points usage analysis: Classify orders by whether points wer


Points usage analysis: Classify orders by whether points were used or not, and find the count, average order amount, and average discount amount for each.


**Hint 1:** Classify with `CASE WHEN point_used > 0 THEN 'Used' ELSE 'Not used' END`.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN point_used > 0 THEN '포인트 사용'
               ELSE '포인트 미사용'
           END AS point_usage,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(AVG(discount_amount)) AS avg_discount
    FROM orders
    GROUP BY point_usage;
    ```


    **Result** (2 rows)

    | point_usage | order_count | avg_amount | avg_discount |
    |---|---|---|---|
    | 포인트 미사용 | 33,817 | 1,015,426.00 | 9,359.00 |
    | 포인트 사용 | 3740 | 1,028,026.00 | 9,517.00 |


---


### 29. Classify products into 4 groups by discontinuation status an


Classify products into 4 groups by discontinuation status and stock status. (Discontinued+In stock, Discontinued+No stock, On sale+In stock, On sale+No stock) Find the product count and average price for each group.


**Hint 1:** Combine two conditions (is_active, stock_qty) in a CASE to classify into 4 categories.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN is_active = 0 AND stock_qty > 0 THEN '단종+재고있음'
               WHEN is_active = 0 AND stock_qty = 0 THEN '단종+재고없음'
               WHEN is_active = 1 AND stock_qty > 0 THEN '판매중+재고있음'
               WHEN is_active = 1 AND stock_qty = 0 THEN '판매중+품절'
           END AS status_group,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price
    FROM products
    GROUP BY status_group
    ORDER BY product_count DESC;
    ```


    **Result** (3 rows)

    | status_group | product_count | avg_price |
    |---|---|---|
    | 판매중+재고있음 | 217 | 662,528.00 |
    | 단종+재고있음 | 62 | 612,979.00 |
    | 판매중+품절 | 1 | 23,000.00 |


---


### 30. Card payment installment analysis: For card payments (method


Card payment installment analysis: For card payments (method = 'card'), find the count and average amount per installment tier (Lump sum, 2-3 months, 4-6 months, 7+ months, No info). Lump sum means installment_months is 0.


**Hint 1:** Filter card payments with `WHERE method = 'card'`. Also consider cases where `installment_months` is NULL.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN installment_months IS NULL THEN '정보없음'
               WHEN installment_months = 0 THEN '일시불'
               WHEN installment_months <= 3 THEN '2~3개월'
               WHEN installment_months <= 6 THEN '4~6개월'
               ELSE '7개월 이상'
           END AS installment_tier,
           COUNT(*) AS payment_count,
           ROUND(AVG(amount)) AS avg_amount
    FROM payments
    WHERE method = 'card'
    GROUP BY installment_tier
    ORDER BY payment_count DESC;
    ```


    **Result** (4 rows)

    | installment_tier | payment_count | avg_amount |
    |---|---|---|
    | 일시불 | 8713 | 430,180.00 |
    | 2~3개월 | 3049 | 997,908.00 |
    | 7개월 이상 | 2987 | 2,151,837.00 |
    | 4~6개월 | 2092 | 1,810,057.00 |


---
