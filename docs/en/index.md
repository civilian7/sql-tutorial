# SQL Tutorial with E-Commerce Database

Welcome to the hands-on SQL tutorial! You'll learn SQL from basics to advanced topics using a **realistic e-commerce database** — a computer & peripherals online store with 10 years of business data.

## What You'll Learn

| Level | Topics | Lessons |
|-------|--------|---------|
| **Beginner** | SELECT, WHERE, ORDER BY, Aggregates, GROUP BY, NULL | 1-6 |
| **Intermediate** | JOINs, Subqueries, CASE, Date/String functions, DML | 7-14 |
| **Advanced** | Window Functions, CTE, EXISTS, Views, Indexes, Triggers | 15-20 |
| **Exercises** | Real-world business problems | 4 modules |

## The Database

This tutorial uses a fictional online store called **TechShop** that sells computers and peripherals. The database contains:

- **21 tables**: customers, products, orders, payments, shipping, reviews, and more
- **18 views**: pre-built queries demonstrating advanced SQL patterns
- **~230,000 rows** (small size) of realistic, interconnected data
- **10 years** of business history (2016-2025)

## How to Use This Tutorial

1. Open the sample database `tutorial.db` in your SQL tool
2. Follow each lesson in order — they build on each other
3. **Try every query yourself** before reading the result
4. Complete the practice exercises at the end of each lesson
5. Use the hint/answer toggles only when stuck

!!! tip "Learning Approach"
    Don't just read the queries — **type them out yourself**. Muscle memory matters in SQL just as it does in programming. Modify the queries, break them, fix them. That's how you learn.

## Database Quick Reference

### Core Tables

```
customers (5,230 rows)     — Registered users with grades, demographics
products (280 rows)        — Computer hardware & peripherals
orders (34,689 rows)       — Purchase orders with status tracking
order_items (74,513 rows)  — Items within each order
payments (34,689 rows)     — Payment details (card, bank, e-wallet)
```

### Supporting Tables

```
categories (53)            — Hierarchical product categories
suppliers (50)             — Product vendors
shipping (32,942)          — Delivery tracking
reviews (7,947)            — Product ratings & text reviews
wishlists (1,998)          — Customer favorites (M:N)
complaints (3,481)         — Customer service inquiries
returns (1,022)            — Return/exchange processing
```

Let's begin with [Lesson 1: SELECT Basics](beginner/01-select.md)!
