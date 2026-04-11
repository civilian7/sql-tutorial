# Database Schema

## Overview

This section covers the complete structure of the **TechShop** database. You can review the ERD, table list, column details, views, triggers, stored procedures, and schema query reference.

> This data is deterministic, generated with seed value 42. The same queries will always return the same results. For more details on seeds, see [Advanced Generator Options > Seeds and Reproducibility](../setup/04-generate-advanced.md#seeds-and-reproducibility).

## Entity Relationship Diagram (ERD)

### Order Flow — Customer → Order → Payment/Shipping

```mermaid
erDiagram
    customers ||--o{ customer_addresses : "customer_id"
    customers ||--o{ orders : "customer_id"
    orders ||--o{ order_items : "order_id"
    order_items }o--|| products : "product_id"
    orders ||--|| payments : "order_id"
    orders ||--o| shipping : "order_id"
    staff ||--o{ orders : "staff_id"
    staff ||--o| staff : "manager_id"
```

```mermaid
flowchart LR
    A[Customer] -->|Orders| B[Orders]
    B -->|Contains| C[Order Items]
    C -->|References| D[Products]
    B -->|Payment| E[Payments]
    B -->|Shipping| F[Shipping]
```

### Product Catalog — Categories, Suppliers, Images, Prices

```mermaid
erDiagram
    categories ||--o{ products : "category_id"
    suppliers ||--o{ products : "supplier_id"
    products ||--o{ product_images : "product_id"
    products ||--o{ product_prices : "product_id"
    categories ||--o{ categories : "parent_id"
    products ||--o| products : "successor_id"
```

```mermaid
flowchart LR
    A[Category] -->|Classifies| B[Product]
    C[Supplier] -->|Supplies| B
    B -->|Has| D[Images]
    B -->|Change history| E[Price History]
    B -.->|Successor model| B
```

### Customer Engagement — Reviews, Wishlists

```mermaid
erDiagram
    customers ||--o{ reviews : "customer_id"
    orders ||--o{ reviews : "order_id"
    products ||--o{ reviews : "product_id"
    customers ||--o{ wishlists : "customer_id"
    products ||--o{ wishlists : "product_id"
```

```mermaid
flowchart LR
    A[Customer] -->|After purchase| B[Write Review]
    B -->|For| C[Product]
    A -->|Adds to| D[Wishlist]
    D -->|For| C
```

### Customer Support — Complaints, Returns, Coupons

```mermaid
erDiagram
    customers ||--o{ complaints : "customer_id"
    orders ||--o{ complaints : "order_id"
    staff ||--o{ complaints : "staff_id"
    complaints ||--o{ returns : "claim_id"
    orders ||--o{ returns : "order_id"
    products ||--o{ returns : "exchange_product_id"
    customers ||--o{ coupon_usage : "customer_id"
    orders ||--o{ coupon_usage : "order_id"
    coupons ||--o{ coupon_usage : "coupon_id"
```

```mermaid
flowchart LR
    A[Customer] -->|Inquiry| B[Complaint]
    B -->|Assigned to| C[CS Staff]
    B -->|Results in| D[Return/Exchange]
    D -->|Exchange product| E[Product]
    F[Coupon] -->|Used in| G[Coupon Usage]
    G -->|Applied to| H[Order]
```

### Cart and Customer Activity — 6 Tables

```mermaid
erDiagram
    customers ||--o{ carts : "customer_id"
    carts ||--o{ cart_items : "cart_id"
    products ||--o{ cart_items : "product_id"
    customers ||--o{ product_views : "customer_id"
    products ||--o{ product_views : "product_id"
    customers ||--o{ point_transactions : "customer_id"
    customers ||--o{ customer_grade_history : "customer_id"
```

```mermaid
flowchart LR
    A[Customer] -->|Views| B[View Log]
    A -->|Adds to| C[Cart]
    C -->|Contains| D[Cart Items]
    A -->|Earns/Uses| E[Point Transactions]
    A -->|Tier change| F[Tier History]
```

### Product Supplementary and Promotions (Catalog & Promo) — 5 Tables

```mermaid
erDiagram
    products ||--o{ inventory_transactions : "product_id"
    products ||--o{ product_tags : "product_id"
    tags ||--o{ product_tags : "tag_id"
    products ||--o{ promotion_products : "product_id"
    promotions ||--o{ promotion_products : "promotion_id"
    products ||--o{ product_qna : "product_id"
    product_qna ||--o{ product_qna : "parent_id"
```

```mermaid
flowchart LR
    A[Product] -->|In/Out| B[Inventory Transactions]
    A -->|Classified by| C[Tags]
    D[Promotion] -->|Targets| A
    A -->|Q&A| E[Q&A]
    E -.->|Reply| E
```

> `calendar` is an independent dimension table used for CROSS JOINs without FK relationships to other tables.

### Relationship Type Summary

| Type | Example | Description |
|------|---------|-------------|
| 1:1 | orders → payments | One payment per order |
| 1:N | customers → orders | One customer, many orders |
| M:N | products ↔ tags (product_tags) | Many-to-many via junction table |
| Self-reference | categories.parent_id, staff.manager_id, products.successor_id, product_qna.parent_id | Hierarchy/links within the same table |
| Nullable FK | orders.staff_id → staff.id | Assigned only to orders needing CS handling |
| Cross-table FK | returns.claim_id → complaints.id | Returns originating from CS complaints |

---

## Data Size by Scale

Row counts per table based on the generator's `--size` option. Medium/Large are estimates based on Small.

<div class="table-data-size" markdown>

| Table | Small (0.1x) | Medium (1x) | Large (5x) |
|-------|-------------:|-------------:|-------------:|
| `customers` | 5,230 | ~52,300 | ~261,500 |
| `orders` | 34,908 | ~349,080 | ~1,745,400 |
| `order_items` | 84,270 | ~842,700 | ~4,213,500 |
| `product_views` | 299,792 | ~2,997,920 | ~14,989,600 |
| `point_transactions` | 130,149 | ~1,301,490 | ~6,507,450 |
| `payments` | 34,908 | ~349,080 | ~1,745,400 |
| `shipping` | 33,107 | ~331,070 | ~1,655,350 |
| `inventory_transactions` | 14,331 | ~143,310 | ~716,550 |
| `customer_grade_history` | 10,273 | ~102,730 | ~513,650 |
| `cart_items` | 9,037 | ~90,370 | ~451,850 |
| `customer_addresses` | 8,554 | ~85,540 | ~427,700 |
| `reviews` | 7,945 | ~79,450 | ~397,250 |
| `promotion_products` | 6,871 | ~68,710 | ~343,550 |
| `calendar` | 3,469 | ~34,690 | ~173,450 |
| `complaints` | 3,477 | ~34,770 | ~173,850 |
| `carts` | 3,000 | ~30,000 | ~150,000 |
| `wishlists` | 1,999 | ~19,990 | ~99,950 |
| `product_tags` | 1,288 | ~12,880 | ~64,400 |
| `product_qna` | 946 | ~9,460 | ~47,300 |
| `returns` | 936 | ~9,360 | ~46,800 |
| `product_prices` | 829 | ~8,290 | ~41,450 |
| `product_images` | 748 | ~7,480 | ~37,400 |
| `products` | 280 | ~2,800 | ~14,000 |
| `promotions` | 129 | ~1,290 | ~6,450 |
| `coupon_usage` | 111 | ~1,110 | ~5,550 |
| `suppliers` | 60 | ~600 | ~3,000 |
| `categories` | 53 | ~530 | ~2,650 |
| `tags` | 46 | ~460 | ~2,300 |
| `coupons` | 20 | ~200 | ~1,000 |
| `staff` | 5 | ~50 | ~250 |
| **Total** | **~697K** | **~6.97M** | **~34.8M** |

</div>

!!! info "File Size"
    | Size | SQLite DB | MySQL SQL | PG SQL | Generation Time |
    |------|----------:|----------:|-------:|----------------:|
    | Small | ~80 MB | ~62 MB | ~62 MB | ~20 sec |
    | Medium | ~800 MB | ~620 MB | ~620 MB | ~3 min |
    | Large | ~4 GB | ~3.1 GB | ~3.1 GB | ~15 min |

---

## Table List

### Core Commerce — 12 Tables

| # | Table | Rows (small) | Description |
|--:|-------|-------------:|-------------|
| 1 | categories | 53 | Product categories (3-level hierarchy) |
| 2 | suppliers | 60 | Suppliers |
| 3 | products | 280 | Products (JSON specs, successor references) |
| 4 | product_images | 748 | Product images |
| 5 | product_prices | 829 | Price change history |
| 6 | customers | 5,230 | Customers (tier, signup channel) |
| 7 | customer_addresses | 8,554 | Customer shipping addresses |
| 8 | staff | 5 | Staff (manager self-reference) |
| 9 | orders | 34,908 | Orders |
| 10 | order_items | 84,270 | Order details |
| 11 | payments | 34,908 | Payments |
| 12 | shipping | 33,107 | Shipping |

### Engagement & Support — 6 Tables

| # | Table | Rows (small) | Description |
|--:|-------|-------------:|-------------|
| 13 | reviews | 7,945 | Product reviews |
| 14 | wishlists | 1,999 | Wishlists (purchase conversion tracking) |
| 15 | complaints | 3,477 | Customer inquiries/complaints (type/compensation/escalation) |
| 16 | returns | 936 | Returns/exchanges (complaint link, exchange product, restocking fee) |
| 17 | coupons | 20 | Coupons |
| 18 | coupon_usage | 111 | Coupon usage records |

### Analytics & Rewards — 12 Tables

| # | Table | Rows (small) | Description |
|--:|-------|-------------:|-------------|
| 19 | inventory_transactions | 14,331 | Inventory in/out history |
| 20 | carts | 3,000 | Carts |
| 21 | cart_items | 9,037 | Cart items |
| 22 | calendar | 3,469 | Date dimension (CROSS JOIN practice) |
| 23 | customer_grade_history | 10,273 | Tier change history (SCD Type 2) |
| 24 | tags | 46 | Product tags |
| 25 | product_tags | 1,288 | Product-tag mapping (M:N) |
| 26 | product_views | 299,792 | Product view log (funnel/cohort) |
| 27 | point_transactions | 130,149 | Points earn/use/expire |
| 28 | promotions | 129 | Promotions/sale events |
| 29 | promotion_products | 6,871 | Promotion target products |
| 30 | product_qna | 946 | Product Q&A (self-reference) |

---
