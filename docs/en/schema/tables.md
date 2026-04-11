# Table Details

### categories -- Product Categories

3-level hierarchy (top -> mid -> sub). `parent_id` is NULL for top-level categories.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: parent_id | INTEGER | -> categories(id), NULL = top-level (self-ref) |
| name | TEXT | Category name |
| slug | TEXT | UNIQUE -- URL-friendly identifier |
| depth | INTEGER | 0=top, 1=mid, 2=sub |
| sort_order | INTEGER | Display order |
| is_active | INTEGER | Active flag (0/1) |
| created_at, updated_at | TEXT | Timestamps |

=== "SQLite"

    ```sql
    CREATE TABLE categories (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id       INTEGER NULL REFERENCES categories(id),  -- parent category (NULL=root)
        name            TEXT NOT NULL,                           -- category name
        slug            TEXT NOT NULL UNIQUE,                    -- URL-safe identifier
        depth           INTEGER NOT NULL DEFAULT 0,              -- 0=top, 1=mid, 2=sub
        sort_order      INTEGER NOT NULL DEFAULT 0,              -- display order
        is_active       INTEGER NOT NULL DEFAULT 1,              -- active flag (0/1)
        created_at      TEXT NOT NULL,
        updated_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE categories (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        parent_id       INT NULL,
        name            VARCHAR(100) NOT NULL,
        slug            VARCHAR(100) NOT NULL UNIQUE,
        depth           INT NOT NULL DEFAULT 0,
        sort_order      INT NOT NULL DEFAULT 0,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        created_at      DATETIME NOT NULL,
        updated_at      DATETIME NOT NULL,
        CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE categories (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        parent_id       INT NULL REFERENCES categories(id),
        name            VARCHAR(100) NOT NULL,
        slug            VARCHAR(100) NOT NULL UNIQUE,
        depth           INT NOT NULL DEFAULT 0,
        sort_order      INT NOT NULL DEFAULT 0,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    
    -- =============================================
    -- Suppliers
    -- =============================================
    CREATE TABLE suppliers (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        company_name    VARCHAR(200) NOT NULL,
        business_number VARCHAR(20) NOT NULL,
        contact_name    VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        email           VARCHAR(200) NOT NULL,
        address         VARCHAR(500) NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    
    -- =============================================
    -- Products
    -- =============================================
    CREATE TABLE products (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        category_id     INT NOT NULL REFERENCES categories(id),
        supplier_id     INT NOT NULL REFERENCES suppliers(id),
        successor_id    INT NULL REFERENCES products(id),
        name            VARCHAR(500) NOT NULL,
        sku             VARCHAR(50) NOT NULL UNIQUE,
        brand           VARCHAR(100) NOT NULL,
        model_number    VARCHAR(50) NULL,
        description     TEXT NULL,
        specs           JSONB NULL,
        price           NUMERIC(12,2) NOT NULL CHECK (price >= 0),
        cost_price      NUMERIC(12,2) NOT NULL CHECK (cost_price >= 0),
        stock_qty       INT NOT NULL DEFAULT 0,
        weight_grams    INT NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        discontinued_at TIMESTAMP NULL,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    
    -- =============================================
    -- Product images
    -- =============================================
    CREATE TABLE product_images (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product_id      INT NOT NULL REFERENCES products(id),
        image_url       VARCHAR(500) NOT NULL,
        file_name       VARCHAR(200) NOT NULL,
        image_type      image_type NOT NULL,
        alt_text        VARCHAR(500) NULL,
        width           INT NULL,
        height          INT NULL,
        file_size       INT NULL,
        sort_order      INT NOT NULL DEFAULT 1,
        is_primary      BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      TIMESTAMP NOT NULL
    );
    
    -- =============================================
    -- Product price history
    -- =============================================
    CREATE TABLE product_prices (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product_id      INT NOT NULL REFERENCES products(id),
        price           NUMERIC(12,2) NOT NULL,
        started_at      TIMESTAMP NOT NULL,
        ended_at        TIMESTAMP NULL,
        change_reason   change_reason_type NULL
    );
    
    -- =============================================
    -- Customers
    -- =============================================
    CREATE TABLE customers (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        email           VARCHAR(200) NOT NULL UNIQUE,
        password_hash   VARCHAR(64) NOT NULL,
        name            VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        birth_date      DATE NULL,
        gender          gender_type NULL,
        grade           customer_grade NOT NULL DEFAULT 'BRONZE',
        point_balance   INT NOT NULL DEFAULT 0 CHECK (point_balance >= 0),
        acquisition_channel acquisition_channel NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        last_login_at   TIMESTAMP NULL,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    
    -- =============================================
    -- Customer addresses
    -- =============================================
    CREATE TABLE customer_addresses (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        customer_id     INT NOT NULL REFERENCES customers(id),
        label           VARCHAR(50) NOT NULL,
        recipient_name  VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        zip_code        VARCHAR(10) NOT NULL,
        address1        VARCHAR(300) NOT NULL,
        address2        VARCHAR(300) NULL,
        is_default      BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NULL
    );
    
    -- =============================================
    -- Staff
    -- =============================================
    CREATE TABLE staff (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        manager_id      INT NULL REFERENCES staff(id),
        email           VARCHAR(200) NOT NULL UNIQUE,
        name            VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        department      VARCHAR(50) NOT NULL,
        role            staff_role NOT NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        hired_at        TIMESTAMP NOT NULL,
        created_at      TIMESTAMP NOT NULL
    );
    
    -- =============================================
    -- Orders (partitioned by year on ordered_at)
    -- =============================================
    CREATE TABLE orders (
        id              INT GENERATED ALWAYS AS IDENTITY,
        order_number    VARCHAR(30) NOT NULL UNIQUE,
        customer_id     INT NOT NULL,
        address_id      INT NOT NULL,
        staff_id        INT NULL,
        status          order_status NOT NULL,
        total_amount    NUMERIC(12,2) NOT NULL,
        discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
        shipping_fee    NUMERIC(12,2) NOT NULL DEFAULT 0,
        point_used      INT NOT NULL DEFAULT 0,
        point_earned    INT NOT NULL DEFAULT 0,
        notes           TEXT NULL,
        ordered_at      TIMESTAMP NOT NULL,
        completed_at    TIMESTAMP NULL,
        cancelled_at    TIMESTAMP NULL,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL,
        PRIMARY KEY (id, ordered_at)
    ) PARTITION BY RANGE (ordered_at);
    ```



### suppliers -- Product Vendors

60 companies that supply products. Each product belongs to exactly one supplier.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| company_name | TEXT | Company name |
| business_number | TEXT | Business registration number (fictitious) |
| contact_name | TEXT | Contact person |
| phone | TEXT | 020-XXXX-XXXX (fictitious number) |
| email | TEXT | contact@xxx.test.kr |
| address | TEXT | Business address |
| is_active | INTEGER | Active flag |
| created_at, updated_at | TEXT | Timestamps |

=== "SQLite"

    ```sql
    CREATE TABLE suppliers (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name    TEXT NOT NULL,                           -- company name
        business_number TEXT NOT NULL,                           -- business registration number (fictional)
        contact_name    TEXT NOT NULL,                           -- contact person
        phone           TEXT NOT NULL,                           -- 020-XXXX-XXXX (fictional number)
        email           TEXT NOT NULL,                           -- contact@xxx.test.kr
        address         TEXT,                                    -- business address
        is_active       INTEGER NOT NULL DEFAULT 1,
        created_at      TEXT NOT NULL,
        updated_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE suppliers (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        company_name    VARCHAR(200) NOT NULL,
        business_number VARCHAR(20) NOT NULL,
        contact_name    VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        email           VARCHAR(200) NOT NULL,
        address         VARCHAR(500) NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        created_at      DATETIME NOT NULL,
        updated_at      DATETIME NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE suppliers (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        company_name    VARCHAR(200) NOT NULL,
        business_number VARCHAR(20) NOT NULL,
        contact_name    VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        email           VARCHAR(200) NOT NULL,
        address         VARCHAR(500) NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    ```


### products -- Products

2,800 electronics products. Identified by unique SKU codes. Includes price, cost, stock, discontinuation status.
**v2.0**: `successor_id` links discontinued products to their replacements; `specs` stores JSON product specifications.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: category_id | INTEGER | -> categories(id) |
| :link: supplier_id | INTEGER | -> suppliers(id) |
| :link: successor_id | INTEGER | -> products(id), successor model (self-ref, NULL = current) |
| name | TEXT | Product name |
| sku | TEXT | UNIQUE -- stock keeping unit (e.g. LA-GEN-Samsung-00001) |
| brand | TEXT | Brand name |
| model_number | TEXT | Model number |
| description | TEXT | Product description |
| specs | TEXT | JSON product specifications (nullable) |
| price | REAL | Current selling price (KRW), CHECK >= 0 |
| cost_price | REAL | Cost price (KRW), CHECK >= 0 |
| stock_qty | INTEGER | Current stock quantity |
| weight_grams | INTEGER | Shipping weight (g) |
| is_active | INTEGER | On-sale flag |
| discontinued_at | TEXT | Discontinuation date (NULL = active) |
| created_at, updated_at | TEXT | Timestamps |

=== "SQLite"

    ```sql
    CREATE TABLE products (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id     INTEGER NOT NULL REFERENCES categories(id),
        supplier_id     INTEGER NOT NULL REFERENCES suppliers(id),
        successor_id    INTEGER NULL REFERENCES products(id),   -- next-generation replacement product
        name            TEXT NOT NULL,                           -- product name
        sku             TEXT NOT NULL UNIQUE,                    -- stock keeping unit (e.g. LA-GEN-Samsung-00001)
        brand           TEXT NOT NULL,                           -- brand name
        model_number    TEXT,                                    -- model number
        description     TEXT,                                    -- product description
        specs           TEXT NULL,                               -- JSON product specifications
        price           REAL NOT NULL CHECK(price >= 0),           -- current selling price (KRW)
        cost_price      REAL NOT NULL CHECK(cost_price >= 0),    -- cost price (KRW)
        stock_qty  INTEGER NOT NULL DEFAULT 0,              -- current stock quantity
        weight_grams    INTEGER,                                 -- shipping weight (g)
        is_active       INTEGER NOT NULL DEFAULT 1,              -- on sale flag
        discontinued_at TEXT NULL,                               -- discontinuation date (NULL=active)
        created_at      TEXT NOT NULL,
        updated_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE products (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        category_id     INT NOT NULL,
        supplier_id     INT NOT NULL,
        successor_id    INT NULL,
        name            VARCHAR(500) NOT NULL,
        sku             VARCHAR(50) NOT NULL UNIQUE,
        brand           VARCHAR(100) NOT NULL,
        model_number    VARCHAR(50) NULL,
        description     TEXT NULL,
        specs           JSON NULL COMMENT 'JSON product specifications',
        price           DECIMAL(12,2) NOT NULL CHECK (price >= 0),
        cost_price      DECIMAL(12,2) NOT NULL CHECK (cost_price >= 0),
        stock_qty       INT NOT NULL DEFAULT 0,
        weight_grams    INT NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        discontinued_at DATETIME NULL,
        created_at      DATETIME NOT NULL,
        updated_at      DATETIME NOT NULL,
        CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id),
        CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
        CONSTRAINT fk_products_successor FOREIGN KEY (successor_id) REFERENCES products(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE products (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        category_id     INT NOT NULL REFERENCES categories(id),
        supplier_id     INT NOT NULL REFERENCES suppliers(id),
        successor_id    INT NULL REFERENCES products(id),
        name            VARCHAR(500) NOT NULL,
        sku             VARCHAR(50) NOT NULL UNIQUE,
        brand           VARCHAR(100) NOT NULL,
        model_number    VARCHAR(50) NULL,
        description     TEXT NULL,
        specs           JSONB NULL,
        price           NUMERIC(12,2) NOT NULL CHECK (price >= 0),
        cost_price      NUMERIC(12,2) NOT NULL CHECK (cost_price >= 0),
        stock_qty       INT NOT NULL DEFAULT 0,
        weight_grams    INT NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        discontinued_at TIMESTAMP NULL,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    ```



### product_images -- Product Images

Multi-angle images per product. `is_primary` distinguishes the main image.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: product_id | INTEGER | -> products(id) |
| image_url | TEXT | Image path/URL |
| file_name | TEXT | Filename (e.g. 42_1.jpg) |
| image_type | TEXT | main/angle/side/back/detail/package/lifestyle |
| alt_text | TEXT | Alt text |
| width, height | INTEGER | Image dimensions (px) |
| file_size | INTEGER | File size (bytes) |
| sort_order | INTEGER | Display order |
| is_primary | INTEGER | Primary image flag |
| created_at | TEXT | Timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE product_images (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id      INTEGER NOT NULL REFERENCES products(id),
        image_url       TEXT NOT NULL,                           -- image path/URL
        file_name       TEXT NOT NULL,                           -- filename (e.g. 42_1.jpg)
        image_type      TEXT NOT NULL,                           -- main/angle/side/back/detail/package/lifestyle/accessory/size_comparison
        alt_text        TEXT,                                    -- alt text
        width           INTEGER,                                 -- image width (px)
        height          INTEGER,                                 -- image height (px)
        file_size       INTEGER,                                 -- file size (bytes, after download)
        sort_order      INTEGER NOT NULL DEFAULT 1,              -- display order
        is_primary      INTEGER NOT NULL DEFAULT 0,              -- primary image flag
        created_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE product_images (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        product_id      INT NOT NULL,
        image_url       VARCHAR(500) NOT NULL,
        file_name       VARCHAR(200) NOT NULL,
        image_type      ENUM('main','angle','side','back','detail','package','lifestyle','accessory','size_comparison') NOT NULL,
        alt_text        VARCHAR(500) NULL,
        width           INT NULL,
        height          INT NULL,
        file_size       INT NULL,
        sort_order      INT NOT NULL DEFAULT 1,
        is_primary      BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      DATETIME NOT NULL,
        CONSTRAINT fk_product_images_product FOREIGN KEY (product_id) REFERENCES products(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE product_images (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product_id      INT NOT NULL REFERENCES products(id),
        image_url       VARCHAR(500) NOT NULL,
        file_name       VARCHAR(200) NOT NULL,
        image_type      image_type NOT NULL,
        alt_text        VARCHAR(500) NULL,
        width           INT NULL,
        height          INT NULL,
        file_size       INT NULL,
        sort_order      INT NOT NULL DEFAULT 1,
        is_primary      BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      TIMESTAMP NOT NULL
    );
    ```

!!! tip "Downloading real product images"
    By default, `image_url` contains [placehold.co](https://placehold.co) placeholder URLs.
    This is sufficient for SQL practice, but if you need real images, the generator can download category-matched photos via the **Pexels API**.

    1. Get a free API key at [pexels.com/api](https://www.pexels.com/api/) (200 requests/month)
    2. Run the generator with the `--download-images` flag:

        ```bash
        python generate.py --download-images --pexels-key YOUR_API_KEY
        # or use an environment variable
        export PEXELS_API_KEY=YOUR_API_KEY
        python generate.py --download-images
        ```

    3. Images are saved to `output/images/` by category, and `image_url` is updated to the local path.

### product_prices -- Price History

Records of product price changes. `ended_at` is NULL for the currently active price.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: product_id | INTEGER | -> products(id) |
| price | REAL | Price during this period |
| started_at | TEXT | Effective start date |
| ended_at | TEXT | Effective end date (NULL = current price) |
| change_reason | TEXT | regular/promotion/price_drop/cost_increase |

=== "SQLite"

    ```sql
    CREATE TABLE product_prices (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id      INTEGER NOT NULL REFERENCES products(id),
        price           REAL NOT NULL,                           -- selling price for this period
        started_at      TEXT NOT NULL,                           -- effective start date
        ended_at        TEXT NULL,                               -- effective end date (NULL=current)
        change_reason   TEXT                                     -- regular/promotion/price_drop/cost_increase
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE product_prices (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        product_id      INT NOT NULL,
        price           DECIMAL(12,2) NOT NULL,
        started_at      DATETIME NOT NULL,
        ended_at        DATETIME NULL,
        change_reason   ENUM('regular','promotion','price_drop','cost_increase') NULL,
        CONSTRAINT fk_product_prices_product FOREIGN KEY (product_id) REFERENCES products(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE product_prices (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product_id      INT NOT NULL REFERENCES products(id),
        price           NUMERIC(12,2) NOT NULL,
        started_at      TIMESTAMP NOT NULL,
        ended_at        TIMESTAMP NULL,
        change_reason   change_reason_type NULL
    );
    ```


### customers -- Customers

52,300 registered members. Tiered grade system (BRONZE-VIP), point balance, active/deactivated status.
**v2.0**: `acquisition_channel` tracks how each customer signed up.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| email | TEXT | UNIQUE -- `user123@testmail.kr` |
| password_hash | TEXT | SHA-256 (fictitious) |
| name | TEXT | Full name |
| phone | TEXT | `020-XXXX-XXXX` (fictitious number) |
| birth_date | TEXT | Date of birth (~15% NULL) |
| gender | TEXT | M/F (NULL ~10%, M:65%) |
| grade | TEXT | CHECK: BRONZE/SILVER/GOLD/VIP |
| point_balance | INTEGER | Point balance, CHECK >= 0 |
| acquisition_channel | TEXT | organic/search_ad/social/referral/direct (nullable) |
| is_active | INTEGER | 0=deactivated, 1=active |
| last_login_at | TEXT | NULL = never logged in |
| created_at, updated_at | TEXT | Signup/update date |

=== "SQLite"

    ```sql
    CREATE TABLE customers (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        email           TEXT NOT NULL UNIQUE,                    -- email (fictional domain)
        password_hash   TEXT NOT NULL,                           -- SHA-256 hash (fictional)
        name            TEXT NOT NULL,                           -- customer name
        phone           TEXT NOT NULL,                           -- 020-XXXX-XXXX (fictional number)
        birth_date      TEXT NULL,                               -- birth date (YYYY-MM-DD, ~15% NULL)
        gender          TEXT NULL,                               -- M/F (NULL ~10%, male 65%)
        grade           TEXT NOT NULL DEFAULT 'BRONZE' CHECK(grade IN ('BRONZE','SILVER','GOLD','VIP')),
        point_balance   INTEGER NOT NULL DEFAULT 0 CHECK(point_balance >= 0),
        acquisition_channel TEXT NULL,                            -- organic/search_ad/social/referral/direct
        is_active       INTEGER NOT NULL DEFAULT 1,              -- active status (0=deactivated)
        last_login_at   TEXT NULL,                               -- last login (NULL=never logged in)
        created_at      TEXT NOT NULL,                           -- signup date
        updated_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE customers (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        email           VARCHAR(200) NOT NULL UNIQUE,
        password_hash   VARCHAR(64) NOT NULL,
        name            VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        birth_date      DATE NULL,
        gender          ENUM('M','F') NULL,
        grade           ENUM('BRONZE','SILVER','GOLD','VIP') NOT NULL DEFAULT 'BRONZE',
        point_balance   INT NOT NULL DEFAULT 0 CHECK (point_balance >= 0),
        acquisition_channel ENUM('organic','search_ad','social','referral','direct') NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        last_login_at   DATETIME NULL,
        created_at      DATETIME NOT NULL,
        updated_at      DATETIME NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE customers (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        email           VARCHAR(200) NOT NULL UNIQUE,
        password_hash   VARCHAR(64) NOT NULL,
        name            VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        birth_date      DATE NULL,
        gender          gender_type NULL,
        grade           customer_grade NOT NULL DEFAULT 'BRONZE',
        point_balance   INT NOT NULL DEFAULT 0 CHECK (point_balance >= 0),
        acquisition_channel acquisition_channel NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        last_login_at   TIMESTAMP NULL,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    ```



### customer_addresses -- Shipping Addresses

Multiple addresses per customer. `is_default` marks the primary shipping address.
**v2.0**: `updated_at` tracks address changes.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: customer_id | INTEGER | -> customers(id) |
| label | TEXT | Home/Office/Other |
| recipient_name | TEXT | Recipient |
| phone | TEXT | Recipient phone |
| zip_code | TEXT | Zip code |
| address1 | TEXT | Base address |
| address2 | TEXT | Detail address |
| is_default | INTEGER | Default address flag |
| created_at | TEXT | Timestamp |
| updated_at | TEXT | Address change date (nullable) |

=== "SQLite"

    ```sql
    CREATE TABLE customer_addresses (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id     INTEGER NOT NULL REFERENCES customers(id),
        label           TEXT NOT NULL,                           -- home/office/other
        recipient_name  TEXT NOT NULL,                           -- recipient
        phone           TEXT NOT NULL,                           -- recipient phone
        zip_code        TEXT NOT NULL,                           -- postal code
        address1        TEXT NOT NULL,                           -- base address
        address2        TEXT,                                    -- detailed address
        is_default      INTEGER NOT NULL DEFAULT 0,              -- default address flag
        created_at      TEXT NOT NULL,
        updated_at      TEXT NULL                                -- address change date
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE customer_addresses (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        customer_id     INT NOT NULL,
        label           VARCHAR(50) NOT NULL,
        recipient_name  VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        zip_code        VARCHAR(10) NOT NULL,
        address1        VARCHAR(300) NOT NULL,
        address2        VARCHAR(300) NULL,
        is_default      BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      DATETIME NOT NULL,
        updated_at      DATETIME NULL,
        CONSTRAINT fk_customer_addresses_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE customer_addresses (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        customer_id     INT NOT NULL REFERENCES customers(id),
        label           VARCHAR(50) NOT NULL,
        recipient_name  VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        zip_code        VARCHAR(10) NOT NULL,
        address1        VARCHAR(300) NOT NULL,
        address2        VARCHAR(300) NULL,
        is_default      BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NULL
    );
    ```


### staff -- Employees

50 store employees. Used for CS assignment and complaint handling.
**v2.0**: `manager_id` creates a self-referencing supervisor hierarchy.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: manager_id | INTEGER | -> staff(id), supervisor (self-ref, NULL = top-level) |
| email | TEXT | UNIQUE -- staffN@techshop-staff.kr |
| name | TEXT | Employee name |
| phone | TEXT | Phone |
| department | TEXT | sales/logistics/CS/marketing/dev/management |
| role | TEXT | admin/manager/staff |
| is_active | INTEGER | Active flag |
| hired_at | TEXT | Hire date |
| created_at | TEXT | Timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE staff (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        manager_id      INTEGER NULL REFERENCES staff(id),      -- supervisor (Self-Join / recursive CTE)
        email           TEXT NOT NULL UNIQUE,                    -- staffN@techshop-staff.kr
        name            TEXT NOT NULL,
        phone           TEXT NOT NULL,
        department      TEXT NOT NULL,                           -- sales/logistics/CS/marketing/dev/management
        role            TEXT NOT NULL,                           -- admin/manager/staff
        is_active       INTEGER NOT NULL DEFAULT 1,
        hired_at        TEXT NOT NULL,                           -- hire date
        created_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE staff (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        manager_id      INT NULL,
        email           VARCHAR(200) NOT NULL UNIQUE,
        name            VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        department      VARCHAR(50) NOT NULL,
        role            ENUM('admin','manager','staff') NOT NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        hired_at        DATETIME NOT NULL,
        created_at      DATETIME NOT NULL,
        CONSTRAINT fk_staff_manager FOREIGN KEY (manager_id) REFERENCES staff(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE staff (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        manager_id      INT NULL REFERENCES staff(id),
        email           VARCHAR(200) NOT NULL UNIQUE,
        name            VARCHAR(100) NOT NULL,
        phone           VARCHAR(20) NOT NULL,
        department      VARCHAR(50) NOT NULL,
        role            staff_role NOT NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        hired_at        TIMESTAMP NOT NULL,
        created_at      TIMESTAMP NOT NULL
    );
    ```


### orders -- Orders

Core transaction table (378,368 rows). Order number format: `ORD-YYYYMMDD-NNNNN`. 9-stage status tracking.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| order_number | TEXT | UNIQUE -- `ORD-20240315-00001` |
| :link: customer_id | INTEGER | -> customers(id) |
| :link: address_id | INTEGER | -> customer_addresses(id) |
| :link: staff_id | INTEGER | -> staff(id), NULL if no CS needed |
| status | TEXT | See status flow below |
| total_amount | REAL | Final payment amount |
| discount_amount | REAL | Total discount |
| shipping_fee | REAL | Free shipping if total >= 50,000 |
| point_used | INTEGER | Points redeemed |
| point_earned | INTEGER | Points to be earned |
| notes | TEXT | Delivery instructions (~35%) |
| ordered_at | TEXT | Order timestamp |
| completed_at | TEXT | Confirmation date |
| cancelled_at | TEXT | Cancellation date |
| created_at, updated_at | TEXT | Timestamps |

=== "SQLite"

    ```sql
    CREATE TABLE orders (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number    TEXT NOT NULL UNIQUE,                    -- ORD-YYYYMMDD-NNNNN
        customer_id     INTEGER NOT NULL REFERENCES customers(id),
        address_id      INTEGER NOT NULL REFERENCES customer_addresses(id),
        staff_id        INTEGER NULL REFERENCES staff(id),      -- CS agent (for cancellations/returns)
        status          TEXT NOT NULL,                           -- pending/paid/preparing/shipped/delivered/confirmed/cancelled/return_requested/returned
        total_amount    REAL NOT NULL,                           -- final payment amount
        discount_amount REAL NOT NULL DEFAULT 0,                 -- total discount
        shipping_fee    REAL NOT NULL DEFAULT 0,                 -- shipping fee (free over 50,000 KRW)
        point_used      INTEGER NOT NULL DEFAULT 0,              -- points used
        point_earned    INTEGER NOT NULL DEFAULT 0,              -- points to be earned
        notes           TEXT NULL,                               -- delivery memo (~35%)
        ordered_at      TEXT NOT NULL,                           -- order datetime
        completed_at    TEXT NULL,                               -- purchase confirmation date
        cancelled_at    TEXT NULL,                               -- cancellation date
        created_at      TEXT NOT NULL,
        updated_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE orders (
        id              INT NOT NULL AUTO_INCREMENT,
        order_number    VARCHAR(30) NOT NULL UNIQUE,
        customer_id     INT NOT NULL,
        address_id      INT NOT NULL,
        staff_id        INT NULL,
        status          ENUM('pending','paid','preparing','shipped','delivered','confirmed','cancelled','return_requested','returned') NOT NULL,
        total_amount    DECIMAL(12,2) NOT NULL,
        discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
        shipping_fee    DECIMAL(12,2) NOT NULL DEFAULT 0,
        point_used      INT NOT NULL DEFAULT 0,
        point_earned    INT NOT NULL DEFAULT 0,
        notes           TEXT NULL,
        ordered_at      DATETIME NOT NULL,
        completed_at    DATETIME NULL,
        cancelled_at    DATETIME NULL,
        created_at      DATETIME NOT NULL,
        updated_at      DATETIME NOT NULL,
        PRIMARY KEY (id, ordered_at),
        INDEX idx_orders_customer (customer_id),
        INDEX idx_orders_status (status),
        INDEX idx_orders_ordered_at (ordered_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    PARTITION BY RANGE (YEAR(ordered_at)) (
        PARTITION p2015 VALUES LESS THAN (2016),
        PARTITION p2016 VALUES LESS THAN (2017),
        PARTITION p2017 VALUES LESS THAN (2018),
        PARTITION p2018 VALUES LESS THAN (2019),
        PARTITION p2019 VALUES LESS THAN (2020),
        PARTITION p2020 VALUES LESS THAN (2021),
        PARTITION p2021 VALUES LESS THAN (2022),
        PARTITION p2022 VALUES LESS THAN (2023),
        PARTITION p2023 VALUES LESS THAN (2024),
        PARTITION p2024 VALUES LESS THAN (2025),
        PARTITION p2025 VALUES LESS THAN (2026),
        PARTITION pmax VALUES LESS THAN MAXVALUE
    );
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE orders (
        id              INT GENERATED ALWAYS AS IDENTITY,
        order_number    VARCHAR(30) NOT NULL UNIQUE,
        customer_id     INT NOT NULL,
        address_id      INT NOT NULL,
        staff_id        INT NULL,
        status          order_status NOT NULL,
        total_amount    NUMERIC(12,2) NOT NULL,
        discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
        shipping_fee    NUMERIC(12,2) NOT NULL DEFAULT 0,
        point_used      INT NOT NULL DEFAULT 0,
        point_earned    INT NOT NULL DEFAULT 0,
        notes           TEXT NULL,
        ordered_at      TIMESTAMP NOT NULL,
        completed_at    TIMESTAMP NULL,
        cancelled_at    TIMESTAMP NULL,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL,
        PRIMARY KEY (id, ordered_at)
    ) PARTITION BY RANGE (ordered_at);
    ```



### order_items -- Order Line Items

Individual products within each order. Captures unit price and discount at order time, independent of later price changes.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: order_id | INTEGER | -> orders(id) |
| :link: product_id | INTEGER | -> products(id) |
| quantity | INTEGER | Qty, CHECK > 0 |
| unit_price | REAL | Price at time of order |
| discount_amount | REAL | Item discount |
| subtotal | REAL | (unit_price x qty) - discount |

=== "SQLite"

    ```sql
    CREATE TABLE order_items (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id        INTEGER NOT NULL REFERENCES orders(id),
        product_id      INTEGER NOT NULL REFERENCES products(id),
        quantity        INTEGER NOT NULL CHECK(quantity > 0),     -- quantity
        unit_price      REAL NOT NULL CHECK(unit_price >= 0),    -- unit price at order time
        discount_amount REAL NOT NULL DEFAULT 0,                 -- item discount
        subtotal        REAL NOT NULL                            -- (unit_price x quantity) - discount
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE order_items (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        order_id        INT NOT NULL,
        product_id      INT NOT NULL,
        quantity        INT NOT NULL CHECK (quantity > 0),
        unit_price      DECIMAL(12,2) NOT NULL CHECK (unit_price >= 0),
        discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
        subtotal        DECIMAL(12,2) NOT NULL,
        INDEX idx_order_items_order (order_id),
        INDEX idx_order_items_product (product_id),
        CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE order_items (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        order_id        INT NOT NULL,
        product_id      INT NOT NULL REFERENCES products(id),
        quantity        INT NOT NULL CHECK (quantity > 0),
        unit_price      NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
        discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
        subtotal        NUMERIC(12,2) NOT NULL
    );
    
    CREATE INDEX idx_order_items_order ON order_items (order_id);
    CREATE INDEX idx_order_items_product ON order_items (product_id);
    
    -- =============================================
    -- Payments
    -- =============================================
    CREATE TABLE payments (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        order_id        INT NOT NULL,
        method          payment_method NOT NULL,
        amount          NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
        status          payment_status NOT NULL,
        pg_transaction_id VARCHAR(100) NULL,
        card_issuer     VARCHAR(50) NULL,
        card_approval_no VARCHAR(20) NULL,
        installment_months INT NULL,
        bank_name       VARCHAR(50) NULL,
        account_no      VARCHAR(50) NULL,
        depositor_name  VARCHAR(100) NULL,
        easy_pay_method VARCHAR(50) NULL,
        receipt_type    VARCHAR(20) NULL,
        receipt_no      VARCHAR(50) NULL,
        paid_at         TIMESTAMP NULL,
        refunded_at     TIMESTAMP NULL,
        created_at      TIMESTAMP NOT NULL
    );
    
    CREATE INDEX idx_payments_order ON payments (order_id);
    
    -- =============================================
    -- Shipping
    -- =============================================
    CREATE TABLE shipping (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        order_id        INT NOT NULL,
        carrier         VARCHAR(50) NOT NULL,
        tracking_number VARCHAR(50) NULL,
        status          shipping_status NOT NULL,
        shipped_at      TIMESTAMP NULL,
        delivered_at    TIMESTAMP NULL,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    
    CREATE INDEX idx_shipping_order ON shipping (order_id);
    
    -- =============================================
    -- Reviews
    -- =============================================
    CREATE TABLE reviews (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product_id      INT NOT NULL REFERENCES products(id),
        customer_id     INT NOT NULL REFERENCES customers(id),
        order_id        INT NOT NULL,
        rating          SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
        title           VARCHAR(200) NULL,
        content         TEXT NULL,
        is_verified     BOOLEAN NOT NULL DEFAULT TRUE,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    
    CREATE INDEX idx_reviews_product ON reviews (product_id);
    CREATE INDEX idx_reviews_customer ON reviews (customer_id);
    
    -- =============================================
    -- Inventory transactions
    -- =============================================
    CREATE TABLE inventory_transactions (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product_id      INT NOT NULL REFERENCES products(id),
        type            inventory_type NOT NULL,
        quantity        INT NOT NULL,
        reference_id    INT NULL,
        notes           VARCHAR(500) NULL,
        created_at      TIMESTAMP NOT NULL
    );
    
    -- =============================================
    -- Carts
    -- =============================================
    CREATE TABLE carts (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        customer_id     INT NOT NULL REFERENCES customers(id),
        status          cart_status NOT NULL DEFAULT 'active',
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    
    -- =============================================
    -- Cart items
    -- =============================================
    CREATE TABLE cart_items (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        cart_id         INT NOT NULL REFERENCES carts(id),
        product_id      INT NOT NULL REFERENCES products(id),
        quantity        INT NOT NULL DEFAULT 1,
        added_at        TIMESTAMP NOT NULL
    );
    
    -- =============================================
    -- Coupons
    -- =============================================
    CREATE TABLE coupons (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        code            VARCHAR(30) NOT NULL UNIQUE,
        name            VARCHAR(200) NOT NULL,
        type            coupon_type NOT NULL,
        discount_value  NUMERIC(12,2) NOT NULL CHECK (discount_value > 0),
        min_order_amount NUMERIC(12,2) NULL,
        max_discount    NUMERIC(12,2) NULL,
        usage_limit     INT NULL,
        per_user_limit  INT NOT NULL DEFAULT 1,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        started_at      TIMESTAMP NOT NULL,
        expired_at      TIMESTAMP NOT NULL,
        created_at      TIMESTAMP NOT NULL
    );
    
    -- =============================================
    -- Coupon usage
    -- =============================================
    CREATE TABLE coupon_usage (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        coupon_id       INT NOT NULL REFERENCES coupons(id),
        customer_id     INT NOT NULL REFERENCES customers(id),
        order_id        INT NOT NULL,
        discount_amount NUMERIC(12,2) NOT NULL,
        used_at         TIMESTAMP NOT NULL
    );
    
    -- =============================================
    -- Complaints
    -- =============================================
    CREATE TABLE complaints (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        order_id        INT NULL,
        customer_id     INT NOT NULL REFERENCES customers(id),
        staff_id        INT NULL REFERENCES staff(id),
        category        complaint_category NOT NULL,
        channel         complaint_channel NOT NULL,
        priority        priority_level NOT NULL,
        status          complaint_status NOT NULL,
        title           VARCHAR(300) NOT NULL,
        content         TEXT NOT NULL,
        resolution      TEXT NULL,
        type            complaint_type NOT NULL DEFAULT 'inquiry',
        sub_category    VARCHAR(100) NULL,
        compensation_type compensation_type NULL,
        compensation_amount NUMERIC(12,2) NULL DEFAULT 0,
        escalated       BOOLEAN NOT NULL DEFAULT FALSE,
        response_count  INT NOT NULL DEFAULT 1,
        created_at      TIMESTAMP NOT NULL,
        resolved_at     TIMESTAMP NULL,
        closed_at       TIMESTAMP NULL
    );
    
    CREATE INDEX idx_complaints_customer ON complaints (customer_id);
    CREATE INDEX idx_complaints_status ON complaints (status);
    
    -- =============================================
    -- Returns/exchanges
    -- =============================================
    CREATE TABLE returns (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        order_id        INT NOT NULL,
        customer_id     INT NOT NULL REFERENCES customers(id),
        return_type     return_type NOT NULL,
        reason          return_reason NOT NULL,
        reason_detail   TEXT NOT NULL,
        status          return_status NOT NULL,
        is_partial      BOOLEAN NOT NULL DEFAULT FALSE,
        refund_amount   NUMERIC(12,2) NOT NULL,
        refund_status   refund_status NOT NULL,
        carrier         VARCHAR(50) NOT NULL,
        tracking_number VARCHAR(50) NOT NULL,
        requested_at    TIMESTAMP NOT NULL,
        pickup_at       TIMESTAMP NOT NULL,
        received_at     TIMESTAMP NULL,
        inspected_at    TIMESTAMP NULL,
        inspection_result inspection_result NULL,
        completed_at    TIMESTAMP NULL,
        claim_id        INT NULL REFERENCES complaints(id),
        exchange_product_id INT NULL REFERENCES products(id),
        restocking_fee  NUMERIC(12,2) NOT NULL DEFAULT 0,
        created_at      TIMESTAMP NOT NULL
    );
    
    CREATE INDEX idx_returns_order ON returns (order_id);
    CREATE INDEX idx_returns_customer ON returns (customer_id);
    
    -- =============================================
    -- Wishlists
    -- =============================================
    CREATE TABLE wishlists (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        customer_id     INT NOT NULL REFERENCES customers(id),
        product_id      INT NOT NULL REFERENCES products(id),
        is_purchased    BOOLEAN NOT NULL DEFAULT FALSE,
        notify_on_sale  BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      TIMESTAMP NOT NULL,
        UNIQUE (customer_id, product_id)
    );
    
    -- =============================================
    -- Calendar dimension
    -- =============================================
    CREATE TABLE calendar (
        date_key        DATE NOT NULL PRIMARY KEY,
        year            INT NOT NULL,
        month           INT NOT NULL,
        day             INT NOT NULL,
        quarter         INT NOT NULL,
        day_of_week     INT NOT NULL,
        day_name        VARCHAR(20) NOT NULL,
        is_weekend      BOOLEAN NOT NULL DEFAULT FALSE,
        is_holiday      BOOLEAN NOT NULL DEFAULT FALSE,
        holiday_name    VARCHAR(100) NULL
    );
    
    CREATE INDEX idx_calendar_year_month ON calendar (year, month);
    
    -- =============================================
    -- Customer grade history
    -- =============================================
    CREATE TABLE customer_grade_history (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        customer_id     INT NOT NULL REFERENCES customers(id),
        old_grade       customer_grade NULL,
        new_grade       customer_grade NOT NULL,
        changed_at      TIMESTAMP NOT NULL,
        reason          grade_change_reason NOT NULL
    );
    
    CREATE INDEX idx_grade_history_customer ON customer_grade_history (customer_id);
    
    -- =============================================
    -- Tags
    -- =============================================
    CREATE TABLE tags (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name            VARCHAR(100) NOT NULL UNIQUE,
        category        tag_category NOT NULL
    );
    
    CREATE TABLE product_tags (
        product_id      INT NOT NULL REFERENCES products(id),
        tag_id          INT NOT NULL REFERENCES tags(id),
        PRIMARY KEY (product_id, tag_id)
    );
    
    -- =============================================
    -- Product views (partitioned by year)
    -- =============================================
    CREATE TABLE product_views (
        id              INT GENERATED ALWAYS AS IDENTITY,
        customer_id     INT NOT NULL,
        product_id      INT NOT NULL,
        referrer_source referrer_source NOT NULL,
        device_type     device_type NOT NULL,
        duration_seconds INT NOT NULL,
        viewed_at       TIMESTAMP NOT NULL,
        PRIMARY KEY (id, viewed_at)
    ) PARTITION BY RANGE (viewed_at);
    ```



### payments -- Payments

One payment per order. Supports card, bank transfer, virtual account, and e-wallet methods.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: order_id | INTEGER | -> orders(id) |
| method | TEXT | card/bank_transfer/virtual_account/kakao_pay/naver_pay/point |
| amount | REAL | Payment amount, CHECK >= 0 |
| status | TEXT | CHECK: pending/completed/failed/refunded |
| pg_transaction_id | TEXT | PG transaction ID (fictitious) |
| card_issuer | TEXT | Shinhan/Samsung/KB/Hyundai/Lotte/Hana/Woori/NH/BC |
| card_approval_no | TEXT | 8-digit card approval number |
| installment_months | INTEGER | Installment months (0=lump sum) |
| bank_name | TEXT | Bank name (for bank_transfer/virtual_account) |
| account_no | TEXT | Virtual account number |
| depositor_name | TEXT | Depositor name |
| easy_pay_method | TEXT | E-wallet internal method |
| receipt_type | TEXT | Tax Deduction / Business Expense |
| receipt_no | TEXT | Receipt number |
| paid_at | TEXT | Payment completion time |
| refunded_at | TEXT | Refund time |
| created_at | TEXT | Timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE payments (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id        INTEGER NOT NULL REFERENCES orders(id),
        method          TEXT NOT NULL,                           -- card/bank_transfer/virtual_account/kakao_pay/naver_pay/point
        amount          REAL NOT NULL CHECK(amount >= 0),         -- payment amount
        status          TEXT NOT NULL CHECK(status IN ('pending','completed','failed','refunded')),
        pg_transaction_id TEXT NULL,                             -- PG transaction ID (fictional)
        card_issuer     TEXT NULL,                               -- card issuer (Shinhan/Samsung/KB/Hyundai/Lotte/Hana/Woori/NH/BC)
        card_approval_no TEXT NULL,                              -- card approval number (8 digits)
        installment_months INTEGER NULL,                         -- installment months (0=lump sum)
        bank_name       TEXT NULL,                               -- bank name (bank transfer/virtual account)
        account_no      TEXT NULL,                               -- virtual account number
        depositor_name  TEXT NULL,                               -- depositor name (bank transfer)
        easy_pay_method TEXT NULL,                               -- easy payment sub-method (KakaoPay balance/linked card, etc.)
        receipt_type    TEXT NULL,                               -- income deduction/expense proof (cash receipt)
        receipt_no      TEXT NULL,                               -- cash receipt number
        paid_at         TEXT NULL,                               -- payment completion time
        refunded_at     TEXT NULL,                               -- refund time
        created_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE payments (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        order_id        INT NOT NULL,
        method          ENUM('card','bank_transfer','virtual_account','kakao_pay','naver_pay','point') NOT NULL,
        amount          DECIMAL(12,2) NOT NULL CHECK (amount >= 0),
        status          ENUM('pending','completed','failed','refunded') NOT NULL,
        pg_transaction_id VARCHAR(100) NULL,
        card_issuer     VARCHAR(50) NULL,
        card_approval_no VARCHAR(20) NULL,
        installment_months INT NULL,
        bank_name       VARCHAR(50) NULL,
        account_no      VARCHAR(50) NULL,
        depositor_name  VARCHAR(100) NULL,
        easy_pay_method VARCHAR(50) NULL,
        receipt_type    VARCHAR(20) NULL,
        receipt_no      VARCHAR(50) NULL,
        paid_at         DATETIME NULL,
        refunded_at     DATETIME NULL,
        created_at      DATETIME NOT NULL,
        INDEX idx_payments_order (order_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE payments (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        order_id        INT NOT NULL,
        method          payment_method NOT NULL,
        amount          NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
        status          payment_status NOT NULL,
        pg_transaction_id VARCHAR(100) NULL,
        card_issuer     VARCHAR(50) NULL,
        card_approval_no VARCHAR(20) NULL,
        installment_months INT NULL,
        bank_name       VARCHAR(50) NULL,
        account_no      VARCHAR(50) NULL,
        depositor_name  VARCHAR(100) NULL,
        easy_pay_method VARCHAR(50) NULL,
        receipt_type    VARCHAR(20) NULL,
        receipt_no      VARCHAR(50) NULL,
        paid_at         TIMESTAMP NULL,
        refunded_at     TIMESTAMP NULL,
        created_at      TIMESTAMP NOT NULL
    );
    ```


### shipping -- Delivery Tracking

Shipment tracking per order with carrier and status.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: order_id | INTEGER | -> orders(id) |
| carrier | TEXT | CJ Logistics / Hanjin / Logen / Korea Post |
| tracking_number | TEXT | Tracking number |
| status | TEXT | preparing/shipped/in_transit/delivered/returned |
| shipped_at | TEXT | Ship date |
| delivered_at | TEXT | Delivery date |
| created_at, updated_at | TEXT | Timestamps |

=== "SQLite"

    ```sql
    CREATE TABLE shipping (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id        INTEGER NOT NULL REFERENCES orders(id),
        carrier         TEXT NOT NULL,                           -- CJ Logistics/Hanjin/Logen/Korea Post
        tracking_number TEXT NULL,                               -- tracking number
        status          TEXT NOT NULL,                           -- preparing/shipped/in_transit/delivered/returned
        shipped_at      TEXT NULL,                               -- ship date
        delivered_at    TEXT NULL,                               -- delivery date (must be after shipped_at)
        created_at      TEXT NOT NULL,
        updated_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE shipping (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        order_id        INT NOT NULL,
        carrier         VARCHAR(50) NOT NULL,
        tracking_number VARCHAR(50) NULL,
        status          ENUM('preparing','shipped','in_transit','delivered','returned') NOT NULL,
        shipped_at      DATETIME NULL,
        delivered_at    DATETIME NULL,
        created_at      DATETIME NOT NULL,
        updated_at      DATETIME NOT NULL,
        INDEX idx_shipping_order (order_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE shipping (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        order_id        INT NOT NULL,
        carrier         VARCHAR(50) NOT NULL,
        tracking_number VARCHAR(50) NULL,
        status          shipping_status NOT NULL,
        shipped_at      TIMESTAMP NULL,
        delivered_at    TIMESTAMP NULL,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    ```


### reviews -- Product Reviews

86,806 purchase-verified reviews. Rating distribution: 5-star 40%, 4-star 30%, 3-star 15%, 2-star 10%, 1-star 5%.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: product_id | INTEGER | -> products(id) |
| :link: customer_id | INTEGER | -> customers(id) |
| :link: order_id | INTEGER | -> orders(id) |
| rating | INTEGER | 1-5, CHECK BETWEEN 1 AND 5 |
| title | TEXT | Review title (~80%) |
| content | TEXT | Review body |
| is_verified | INTEGER | Purchase verification flag |
| created_at, updated_at | TEXT | Timestamps |

=== "SQLite"

    ```sql
    CREATE TABLE reviews (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id      INTEGER NOT NULL REFERENCES products(id),
        customer_id     INTEGER NOT NULL REFERENCES customers(id),
        order_id        INTEGER NOT NULL REFERENCES orders(id),
        rating          INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),  -- 1~5 stars (5=40%, 1=5%)
        title           TEXT NULL,                               -- review title (~80%)
        content         TEXT NULL,                               -- review body
        is_verified     INTEGER NOT NULL DEFAULT 1,              -- verified purchase flag
        created_at      TEXT NOT NULL,
        updated_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE reviews (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        product_id      INT NOT NULL,
        customer_id     INT NOT NULL,
        order_id        INT NOT NULL,
        rating          TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
        title           VARCHAR(200) NULL,
        content         TEXT NULL,
        is_verified     BOOLEAN NOT NULL DEFAULT TRUE,
        created_at      DATETIME NOT NULL,
        updated_at      DATETIME NOT NULL,
        INDEX idx_reviews_product (product_id),
        INDEX idx_reviews_customer (customer_id),
        CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) REFERENCES products(id),
        CONSTRAINT fk_reviews_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE reviews (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product_id      INT NOT NULL REFERENCES products(id),
        customer_id     INT NOT NULL REFERENCES customers(id),
        order_id        INT NOT NULL,
        rating          SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
        title           VARCHAR(200) NULL,
        content         TEXT NULL,
        is_verified     BOOLEAN NOT NULL DEFAULT TRUE,
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    ```



### inventory_transactions -- Stock Movements

Product stock change history. Inbound (positive), outbound (negative), returns, and adjustments.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: product_id | INTEGER | -> products(id) |
| type | TEXT | inbound/outbound/return/adjustment |
| quantity | INTEGER | Positive = in, Negative = out |
| reference_id | INTEGER | Related order ID |
| notes | TEXT | Initial stock / regular restock / return, etc. |
| created_at | TEXT | Timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE inventory_transactions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id      INTEGER NOT NULL REFERENCES products(id),
        type            TEXT NOT NULL,                           -- inbound/outbound/return/adjustment
        quantity        INTEGER NOT NULL,                        -- positive=inbound, negative=outbound
        reference_id    INTEGER NULL,                            -- related order ID
        notes           TEXT NULL,                               -- initial_stock/regular_inbound/return_inbound
        created_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE inventory_transactions (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        product_id      INT NOT NULL,
        type            ENUM('inbound','outbound','return','adjustment') NOT NULL,
        quantity        INT NOT NULL,
        reference_id    INT NULL,
        notes           VARCHAR(500) NULL,
        created_at      DATETIME NOT NULL,
        CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE inventory_transactions (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product_id      INT NOT NULL REFERENCES products(id),
        type            inventory_type NOT NULL,
        quantity        INT NOT NULL,
        reference_id    INT NULL,
        notes           VARCHAR(500) NULL,
        created_at      TIMESTAMP NOT NULL
    );
    ```


### carts -- Shopping Carts

Per-customer carts. Tracks conversion (converted) and abandonment (abandoned) status.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: customer_id | INTEGER | -> customers(id) |
| status | TEXT | active/converted/abandoned |
| created_at, updated_at | TEXT | Timestamps |

=== "SQLite"

    ```sql
    CREATE TABLE carts (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id     INTEGER NOT NULL REFERENCES customers(id),
        status          TEXT NOT NULL DEFAULT 'active',          -- active/converted/abandoned
        created_at      TEXT NOT NULL,
        updated_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE carts (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        customer_id     INT NOT NULL,
        status          ENUM('active','converted','abandoned') NOT NULL DEFAULT 'active',
        created_at      DATETIME NOT NULL,
        updated_at      DATETIME NOT NULL,
        CONSTRAINT fk_carts_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE carts (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        customer_id     INT NOT NULL REFERENCES customers(id),
        status          cart_status NOT NULL DEFAULT 'active',
        created_at      TIMESTAMP NOT NULL,
        updated_at      TIMESTAMP NOT NULL
    );
    ```


### cart_items -- Cart Items

Individual products within a cart.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: cart_id | INTEGER | -> carts(id) |
| :link: product_id | INTEGER | -> products(id) |
| quantity | INTEGER | Quantity |
| added_at | TEXT | Added timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE cart_items (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id         INTEGER NOT NULL REFERENCES carts(id),
        product_id      INTEGER NOT NULL REFERENCES products(id),
        quantity        INTEGER NOT NULL DEFAULT 1,
        added_at        TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE cart_items (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        cart_id         INT NOT NULL,
        product_id      INT NOT NULL,
        quantity        INT NOT NULL DEFAULT 1,
        added_at        DATETIME NOT NULL,
        CONSTRAINT fk_cart_items_cart FOREIGN KEY (cart_id) REFERENCES carts(id),
        CONSTRAINT fk_cart_items_product FOREIGN KEY (product_id) REFERENCES products(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE cart_items (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        cart_id         INT NOT NULL REFERENCES carts(id),
        product_id      INT NOT NULL REFERENCES products(id),
        quantity        INT NOT NULL DEFAULT 1,
        added_at        TIMESTAMP NOT NULL
    );
    ```


### coupons -- Coupons

200 discount coupons. Percentage or fixed amount, with usage limits and validity periods.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| code | TEXT | UNIQUE -- coupon code (CP2401001) |
| name | TEXT | Coupon name |
| type | TEXT | percent/fixed |
| discount_value | REAL | Discount rate (%) or amount, CHECK > 0 |
| min_order_amount | REAL | Minimum order amount |
| max_discount | REAL | Maximum discount (percent type) |
| usage_limit | INTEGER | Total usage limit |
| per_user_limit | INTEGER | Per-user limit |
| is_active | INTEGER | Active flag |
| started_at | TEXT | Validity start |
| expired_at | TEXT | Validity end |
| created_at | TEXT | Timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE coupons (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        code            TEXT NOT NULL UNIQUE,                    -- coupon code (CP2401001)
        name            TEXT NOT NULL,                           -- coupon name
        type            TEXT NOT NULL,                           -- percent/fixed
        discount_value  REAL NOT NULL CHECK(discount_value > 0),  -- discount rate (%) or amount (KRW)
        min_order_amount REAL NULL,                              -- minimum order amount
        max_discount    REAL NULL,                               -- max discount amount (percent type)
        usage_limit     INTEGER NULL,                            -- total usage limit
        per_user_limit  INTEGER NOT NULL DEFAULT 1,              -- per-user usage limit
        is_active       INTEGER NOT NULL DEFAULT 1,
        started_at      TEXT NOT NULL,                           -- validity start
        expired_at      TEXT NOT NULL,                           -- validity end
        created_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE coupons (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        code            VARCHAR(30) NOT NULL UNIQUE,
        name            VARCHAR(200) NOT NULL,
        type            ENUM('percent','fixed') NOT NULL,
        discount_value  DECIMAL(12,2) NOT NULL CHECK (discount_value > 0),
        min_order_amount DECIMAL(12,2) NULL,
        max_discount    DECIMAL(12,2) NULL,
        usage_limit     INT NULL,
        per_user_limit  INT NOT NULL DEFAULT 1,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        started_at      DATETIME NOT NULL,
        expired_at      DATETIME NOT NULL,
        created_at      DATETIME NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE coupons (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        code            VARCHAR(30) NOT NULL UNIQUE,
        name            VARCHAR(200) NOT NULL,
        type            coupon_type NOT NULL,
        discount_value  NUMERIC(12,2) NOT NULL CHECK (discount_value > 0),
        min_order_amount NUMERIC(12,2) NULL,
        max_discount    NUMERIC(12,2) NULL,
        usage_limit     INT NULL,
        per_user_limit  INT NOT NULL DEFAULT 1,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        started_at      TIMESTAMP NOT NULL,
        expired_at      TIMESTAMP NOT NULL,
        created_at      TIMESTAMP NOT NULL
    );
    ```


### coupon_usage -- Coupon Usage Records

Records of actual coupon usage: which customer, which order, how much discount.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: coupon_id | INTEGER | -> coupons(id) |
| :link: customer_id | INTEGER | -> customers(id) |
| :link: order_id | INTEGER | -> orders(id) |
| discount_amount | REAL | Actual discount amount |
| used_at | TEXT | Usage timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE coupon_usage (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        coupon_id       INTEGER NOT NULL REFERENCES coupons(id),
        customer_id     INTEGER NOT NULL REFERENCES customers(id),
        order_id        INTEGER NOT NULL REFERENCES orders(id),
        discount_amount REAL NOT NULL,                           -- actual discount amount
        used_at         TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE coupon_usage (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        coupon_id       INT NOT NULL,
        customer_id     INT NOT NULL,
        order_id        INT NOT NULL,
        discount_amount DECIMAL(12,2) NOT NULL,
        used_at         DATETIME NOT NULL,
        CONSTRAINT fk_coupon_usage_coupon FOREIGN KEY (coupon_id) REFERENCES coupons(id),
        CONSTRAINT fk_coupon_usage_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE coupon_usage (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        coupon_id       INT NOT NULL REFERENCES coupons(id),
        customer_id     INT NOT NULL REFERENCES customers(id),
        order_id        INT NOT NULL,
        discount_amount NUMERIC(12,2) NOT NULL,
        used_at         TIMESTAMP NOT NULL
    );
    ```


### complaints -- Customer Inquiries/Complaints

37,953 CS inquiries. 7 categories, 5 channels, 4 priority levels.
**v2.0**: Added `type` (inquiry/claim/report), `sub_category`, `compensation_type`, `compensation_amount`, `escalated`, and `response_count` columns.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: order_id | INTEGER | -> orders(id), NULL = general inquiry |
| :link: customer_id | INTEGER | -> customers(id) |
| :link: staff_id | INTEGER | -> staff(id), assigned CS agent |
| category | TEXT | product_defect/delivery_issue/wrong_item/refund_request/exchange_request/general_inquiry/price_inquiry |
| channel | TEXT | website/phone/email/chat/kakao |
| priority | TEXT | low/medium/high/urgent |
| status | TEXT | open/resolved/closed |
| title | TEXT | Inquiry title |
| content | TEXT | Inquiry body |
| resolution | TEXT | Resolution detail (when resolved) |
| type | TEXT | inquiry/claim/report |
| sub_category | TEXT | Detailed category (e.g. initial_defect/in_use_damage/misdelivery) |
| compensation_type | TEXT | refund/exchange/partial_refund/point_compensation/none |
| compensation_amount | REAL | Compensation amount |
| escalated | INTEGER | Escalated to supervisor (0/1) |
| response_count | INTEGER | Number of responses |
| created_at | TEXT | Submitted date |
| resolved_at | TEXT | Resolved date |
| closed_at | TEXT | Closed date |

=== "SQLite"

    ```sql
    CREATE TABLE complaints (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id        INTEGER NULL REFERENCES orders(id),     -- order-related inquiry (NULL=general)
        customer_id     INTEGER NOT NULL REFERENCES customers(id),
        staff_id        INTEGER NULL REFERENCES staff(id),      -- assigned CS agent
        category        TEXT NOT NULL,                           -- product_defect/delivery_issue/wrong_item/refund_request/exchange_request/general_inquiry/price_inquiry
        channel         TEXT NOT NULL,                           -- website/phone/email/chat/kakao
        priority        TEXT NOT NULL,                           -- low/medium/high/urgent
        status          TEXT NOT NULL,                           -- open/resolved/closed
        title           TEXT NOT NULL,                           -- inquiry title
        content         TEXT NOT NULL,                           -- inquiry content
        resolution      TEXT NULL,                               -- resolution detail (when resolved)
        type            TEXT NOT NULL DEFAULT 'inquiry',         -- inquiry/claim/report
        sub_category    TEXT NULL,                               -- detailed category (e.g., initial_defect/in_use_damage/misdelivery)
        compensation_type TEXT NULL,                             -- refund/exchange/partial_refund/point_compensation/none
        compensation_amount REAL NULL DEFAULT 0,                 -- compensation amount
        escalated       INTEGER NOT NULL DEFAULT 0,             -- escalated to supervisor (0/1)
        response_count  INTEGER NOT NULL DEFAULT 1,             -- number of back-and-forth responses
        created_at      TEXT NOT NULL,                           -- submitted date
        resolved_at     TEXT NULL,                               -- resolved date
        closed_at       TEXT NULL                                -- closed date
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE complaints (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        order_id        INT NULL,
        customer_id     INT NOT NULL,
        staff_id        INT NULL,
        category        ENUM('product_defect','delivery_issue','wrong_item','refund_request','exchange_request','general_inquiry','price_inquiry') NOT NULL,
        channel         ENUM('website','phone','email','chat','kakao') NOT NULL,
        priority        ENUM('low','medium','high','urgent') NOT NULL,
        status          ENUM('open','resolved','closed') NOT NULL,
        title           VARCHAR(300) NOT NULL,
        content         TEXT NOT NULL,
        resolution      TEXT NULL,
        type            ENUM('inquiry','claim','report') NOT NULL DEFAULT 'inquiry',
        sub_category    VARCHAR(100) NULL,
        compensation_type ENUM('refund','exchange','partial_refund','point_compensation','none') NULL,
        compensation_amount DECIMAL(12,2) NULL DEFAULT 0,
        escalated       BOOLEAN NOT NULL DEFAULT FALSE,
        response_count  INT NOT NULL DEFAULT 1,
        created_at      DATETIME NOT NULL,
        resolved_at     DATETIME NULL,
        closed_at       DATETIME NULL,
        INDEX idx_complaints_customer (customer_id),
        INDEX idx_complaints_status (status),
        CONSTRAINT fk_complaints_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
        CONSTRAINT fk_complaints_staff FOREIGN KEY (staff_id) REFERENCES staff(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE complaints (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        order_id        INT NULL,
        customer_id     INT NOT NULL REFERENCES customers(id),
        staff_id        INT NULL REFERENCES staff(id),
        category        complaint_category NOT NULL,
        channel         complaint_channel NOT NULL,
        priority        priority_level NOT NULL,
        status          complaint_status NOT NULL,
        title           VARCHAR(300) NOT NULL,
        content         TEXT NOT NULL,
        resolution      TEXT NULL,
        type            complaint_type NOT NULL DEFAULT 'inquiry',
        sub_category    VARCHAR(100) NULL,
        compensation_type compensation_type NULL,
        compensation_amount NUMERIC(12,2) NULL DEFAULT 0,
        escalated       BOOLEAN NOT NULL DEFAULT FALSE,
        response_count  INT NOT NULL DEFAULT 1,
        created_at      TIMESTAMP NOT NULL,
        resolved_at     TIMESTAMP NULL,
        closed_at       TIMESTAMP NULL
    );
    ```


### returns -- Returns & Exchanges

11,413 return/exchange requests. Full lifecycle tracking from request to completion.
**v2.0**: Added `claim_id` (return originated from a CS complaint), `exchange_product_id` (replacement product), and `restocking_fee` (change-of-mind restocking fee).

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: order_id | INTEGER | -> orders(id) |
| :link: customer_id | INTEGER | -> customers(id) |
| :link: claim_id | INTEGER | -> complaints(id), linked CS complaint (nullable) |
| :link: exchange_product_id | INTEGER | -> products(id), replacement product (nullable) |
| return_type | TEXT | refund/exchange |
| reason | TEXT | defective/wrong_item/change_of_mind/damaged_in_transit/not_as_described/late_delivery |
| reason_detail | TEXT | Detailed reason |
| status | TEXT | requested/pickup_scheduled/in_transit/completed |
| is_partial | INTEGER | Partial return (~17%) |
| refund_amount | REAL | Refund amount |
| refund_status | TEXT | pending/refunded/exchanged/partial_refund |
| restocking_fee | REAL | Change-of-mind restocking fee (default 0) |
| carrier | TEXT | Pickup carrier |
| tracking_number | TEXT | Pickup tracking number |
| requested_at | TEXT | Request date |
| pickup_at | TEXT | Pickup date |
| received_at | TEXT | Warehouse receipt date |
| inspected_at | TEXT | Inspection date |
| inspection_result | TEXT | good/opened_good/defective/unsellable |
| completed_at | TEXT | Completion date |
| created_at | TEXT | Timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE returns (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id        INTEGER NOT NULL REFERENCES orders(id),
        customer_id     INTEGER NOT NULL REFERENCES customers(id),
        return_type     TEXT NOT NULL,                           -- refund/exchange
        reason          TEXT NOT NULL,                           -- defective/wrong_item/change_of_mind/damaged_in_transit/not_as_described/late_delivery
        reason_detail   TEXT NOT NULL,                           -- detailed reason description
        status          TEXT NOT NULL,                           -- requested/pickup_scheduled/in_transit/completed
        is_partial      INTEGER NOT NULL DEFAULT 0,              -- partial return flag (~17%)
        refund_amount   REAL NOT NULL,                           -- refund amount
        refund_status   TEXT NOT NULL,                           -- pending/refunded/exchanged/partial_refund
        carrier         TEXT NOT NULL,                           -- pickup carrier
        tracking_number TEXT NOT NULL,                           -- pickup tracking number
        requested_at    TEXT NOT NULL,                           -- return request date
        pickup_at       TEXT NOT NULL,                           -- pickup scheduled/completed date
        received_at     TEXT NULL,                               -- warehouse receipt date
        inspected_at    TEXT NULL,                               -- inspection completion date
        inspection_result TEXT NULL,                             -- good/opened_good/defective/unsellable
        completed_at    TEXT NULL,                               -- processing completion date
        claim_id        INTEGER NULL REFERENCES complaints(id), -- linked claim (if return originated from CS)
        exchange_product_id INTEGER NULL REFERENCES products(id), -- replacement product for exchanges
        restocking_fee  REAL NOT NULL DEFAULT 0,                 -- change-of-mind restocking fee
        created_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE returns (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        order_id        INT NOT NULL,
        customer_id     INT NOT NULL,
        return_type     ENUM('refund','exchange') NOT NULL,
        reason          ENUM('defective','wrong_item','change_of_mind','damaged_in_transit','not_as_described','late_delivery') NOT NULL,
        reason_detail   TEXT NOT NULL,
        status          ENUM('requested','pickup_scheduled','in_transit','completed') NOT NULL,
        is_partial      BOOLEAN NOT NULL DEFAULT FALSE,
        refund_amount   DECIMAL(12,2) NOT NULL,
        refund_status   ENUM('pending','refunded','exchanged','partial_refund') NOT NULL,
        carrier         VARCHAR(50) NOT NULL,
        tracking_number VARCHAR(50) NOT NULL,
        requested_at    DATETIME NOT NULL,
        pickup_at       DATETIME NOT NULL,
        received_at     DATETIME NULL,
        inspected_at    DATETIME NULL,
        inspection_result ENUM('good','opened_good','defective','unsellable') NULL,
        completed_at    DATETIME NULL,
        claim_id        INT NULL,
        exchange_product_id INT NULL,
        restocking_fee  DECIMAL(12,2) NOT NULL DEFAULT 0,
        created_at      DATETIME NOT NULL,
        INDEX idx_returns_order (order_id),
        INDEX idx_returns_customer (customer_id),
        CONSTRAINT fk_returns_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
        CONSTRAINT fk_returns_claim FOREIGN KEY (claim_id) REFERENCES complaints(id),
        CONSTRAINT fk_returns_exchange_product FOREIGN KEY (exchange_product_id) REFERENCES products(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE returns (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        order_id        INT NOT NULL,
        customer_id     INT NOT NULL REFERENCES customers(id),
        return_type     return_type NOT NULL,
        reason          return_reason NOT NULL,
        reason_detail   TEXT NOT NULL,
        status          return_status NOT NULL,
        is_partial      BOOLEAN NOT NULL DEFAULT FALSE,
        refund_amount   NUMERIC(12,2) NOT NULL,
        refund_status   refund_status NOT NULL,
        carrier         VARCHAR(50) NOT NULL,
        tracking_number VARCHAR(50) NOT NULL,
        requested_at    TIMESTAMP NOT NULL,
        pickup_at       TIMESTAMP NOT NULL,
        received_at     TIMESTAMP NULL,
        inspected_at    TIMESTAMP NULL,
        inspection_result inspection_result NULL,
        completed_at    TIMESTAMP NULL,
        claim_id        INT NULL REFERENCES complaints(id),
        exchange_product_id INT NULL REFERENCES products(id),
        restocking_fee  NUMERIC(12,2) NOT NULL DEFAULT 0,
        created_at      TIMESTAMP NOT NULL
    );
    ```


### wishlists -- Wish Lists

Customer product favorites. UNIQUE on (customer_id, product_id).
**v2.0**: `is_purchased` tracks whether a wishlisted product was eventually purchased.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: customer_id | INTEGER | -> customers(id) |
| :link: product_id | INTEGER | -> products(id) |
| is_purchased | INTEGER | Converted to purchase (0/1) |
| notify_on_sale | INTEGER | Price drop notification (0/1) |
| created_at | TEXT | Timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE wishlists (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id     INTEGER NOT NULL REFERENCES customers(id),
        product_id      INTEGER NOT NULL REFERENCES products(id),
        is_purchased    INTEGER NOT NULL DEFAULT 0,              -- converted to purchase flag (0/1)
        notify_on_sale  INTEGER NOT NULL DEFAULT 0,              -- price drop notification (0/1)
        created_at      TEXT NOT NULL,
        UNIQUE(customer_id, product_id)                          -- prevent duplicate customer-product pairs
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE wishlists (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        customer_id     INT NOT NULL,
        product_id      INT NOT NULL,
        is_purchased    BOOLEAN NOT NULL DEFAULT FALSE,
        notify_on_sale  BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      DATETIME NOT NULL,
        UNIQUE KEY uq_wishlist (customer_id, product_id),
        CONSTRAINT fk_wishlists_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
        CONSTRAINT fk_wishlists_product FOREIGN KEY (product_id) REFERENCES products(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE wishlists (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        customer_id     INT NOT NULL REFERENCES customers(id),
        product_id      INT NOT NULL REFERENCES products(id),
        is_purchased    BOOLEAN NOT NULL DEFAULT FALSE,
        notify_on_sale  BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      TIMESTAMP NOT NULL,
        UNIQUE (customer_id, product_id)
    );
    ```


### calendar -- Date Dimension Table

Covers the full date range (2016-2025). Used for CROSS JOIN and date gap analysis.

| Column | Type | Notes |
|--------|------|-------|
| :key: date_key | TEXT | YYYY-MM-DD (primary key) |
| year | INTEGER | Year |
| month | INTEGER | Month |
| day | INTEGER | Day |
| quarter | INTEGER | Quarter (1-4) |
| day_of_week | INTEGER | 0=Mon .. 6=Sun |
| day_name | TEXT | Monday-Sunday |
| is_weekend | INTEGER | Weekend flag (0/1) |
| is_holiday | INTEGER | Public holiday flag (0/1) |
| holiday_name | TEXT | Holiday name |

=== "SQLite"

    ```sql
    CREATE TABLE calendar (
        date_key        TEXT PRIMARY KEY,                        -- YYYY-MM-DD
        year            INTEGER NOT NULL,
        month           INTEGER NOT NULL,
        day             INTEGER NOT NULL,
        quarter         INTEGER NOT NULL,                        -- 1~4
        day_of_week     INTEGER NOT NULL,                        -- 0=Mon ~ 6=Sun
        day_name        TEXT NOT NULL,                           -- Monday~Sunday
        is_weekend      INTEGER NOT NULL DEFAULT 0,              -- Sat/Sun = 1
        is_holiday      INTEGER NOT NULL DEFAULT 0,              -- public holiday = 1
        holiday_name    TEXT NULL                                -- holiday name
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE calendar (
        date_key        DATE NOT NULL PRIMARY KEY,
        year            INT NOT NULL,
        month           INT NOT NULL,
        day             INT NOT NULL,
        quarter         INT NOT NULL,
        day_of_week     INT NOT NULL,
        day_name        VARCHAR(20) NOT NULL,
        is_weekend      BOOLEAN NOT NULL DEFAULT FALSE,
        is_holiday      BOOLEAN NOT NULL DEFAULT FALSE,
        holiday_name    VARCHAR(100) NULL,
        INDEX idx_calendar_year_month (year, month)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE calendar (
        date_key        DATE NOT NULL PRIMARY KEY,
        year            INT NOT NULL,
        month           INT NOT NULL,
        day             INT NOT NULL,
        quarter         INT NOT NULL,
        day_of_week     INT NOT NULL,
        day_name        VARCHAR(20) NOT NULL,
        is_weekend      BOOLEAN NOT NULL DEFAULT FALSE,
        is_holiday      BOOLEAN NOT NULL DEFAULT FALSE,
        holiday_name    VARCHAR(100) NULL
    );
    ```


### customer_grade_history -- Grade Change Audit

Tracks every customer grade change. Used to learn the SCD (Slowly Changing Dimension) Type 2 pattern.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: customer_id | INTEGER | -> customers(id) |
| old_grade | TEXT | Previous grade (NULL = initial signup) |
| new_grade | TEXT | New grade |
| changed_at | TEXT | Change datetime |
| reason | TEXT | signup/upgrade/downgrade/yearly_review |

=== "SQLite"

    ```sql
    CREATE TABLE customer_grade_history (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id     INTEGER NOT NULL REFERENCES customers(id),
        old_grade       TEXT NULL,                               -- previous grade (NULL on initial signup)
        new_grade       TEXT NOT NULL,                           -- new grade
        changed_at      TEXT NOT NULL,                           -- change datetime
        reason          TEXT NOT NULL                            -- signup/upgrade/downgrade/yearly_review
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE customer_grade_history (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        customer_id     INT NOT NULL,
        old_grade       ENUM('BRONZE','SILVER','GOLD','VIP') NULL,
        new_grade       ENUM('BRONZE','SILVER','GOLD','VIP') NOT NULL,
        changed_at      DATETIME NOT NULL,
        reason          ENUM('signup','upgrade','downgrade','yearly_review') NOT NULL,
        INDEX idx_grade_history_customer (customer_id),
        CONSTRAINT fk_grade_history_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE customer_grade_history (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        customer_id     INT NOT NULL REFERENCES customers(id),
        old_grade       customer_grade NULL,
        new_grade       customer_grade NOT NULL,
        changed_at      TIMESTAMP NOT NULL,
        reason          grade_change_reason NOT NULL
    );
    ```


### tags / product_tags -- Product Tags

80 tags and their product mappings. Demonstrates the M:N bridge table pattern.

**tags:**

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| name | TEXT | UNIQUE -- tag name |
| category | TEXT | feature/use_case/target/spec |

=== "SQLite"

    ```sql
    CREATE TABLE tags (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT NOT NULL UNIQUE,
        category        TEXT NOT NULL                            -- feature/use_case/target/spec
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE tags (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        name            VARCHAR(100) NOT NULL UNIQUE,
        category        VARCHAR(50) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE tags (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name            VARCHAR(100) NOT NULL UNIQUE,
        category        tag_category NOT NULL
    );
    ```


**product_tags:**

| Column | Type | Notes |
|--------|------|-------|
| :link: product_id | INTEGER | -> products(id), composite PK |
| :link: tag_id | INTEGER | -> tags(id), composite PK |

### product_views -- Page View Log

Product page view records. Includes referrer source, device type, and dwell time.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: customer_id | INTEGER | -> customers(id) |
| :link: product_id | INTEGER | -> products(id) |
| referrer_source | TEXT | direct/search/ad/recommendation/social/email |
| device_type | TEXT | desktop/mobile/tablet |
| duration_seconds | INTEGER | Page dwell time (seconds) |
| viewed_at | TEXT | View timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE product_views (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id     INTEGER NOT NULL REFERENCES customers(id),
        product_id      INTEGER NOT NULL REFERENCES products(id),
        referrer_source TEXT NOT NULL,                           -- direct/search/ad/recommendation/social/email
        device_type     TEXT NOT NULL,                           -- desktop/mobile/tablet
        duration_seconds INTEGER NOT NULL,                       -- page dwell time (seconds)
        viewed_at       TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE product_views (
        id              INT NOT NULL AUTO_INCREMENT,
        customer_id     INT NOT NULL,
        product_id      INT NOT NULL,
        referrer_source ENUM('direct','search','ad','recommendation','social','email') NOT NULL,
        device_type     ENUM('desktop','mobile','tablet') NOT NULL,
        duration_seconds INT NOT NULL,
        viewed_at       DATETIME NOT NULL,
        PRIMARY KEY (id, viewed_at),
        INDEX idx_views_customer (customer_id),
        INDEX idx_views_product (product_id),
        INDEX idx_views_viewed_at (viewed_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    PARTITION BY RANGE (YEAR(viewed_at)) (
        PARTITION p2015 VALUES LESS THAN (2016),
        PARTITION p2016 VALUES LESS THAN (2017),
        PARTITION p2017 VALUES LESS THAN (2018),
        PARTITION p2018 VALUES LESS THAN (2019),
        PARTITION p2019 VALUES LESS THAN (2020),
        PARTITION p2020 VALUES LESS THAN (2021),
        PARTITION p2021 VALUES LESS THAN (2022),
        PARTITION p2022 VALUES LESS THAN (2023),
        PARTITION p2023 VALUES LESS THAN (2024),
        PARTITION p2024 VALUES LESS THAN (2025),
        PARTITION p2025 VALUES LESS THAN (2026),
        PARTITION pmax VALUES LESS THAN MAXVALUE
    );
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE product_views (
        id              INT GENERATED ALWAYS AS IDENTITY,
        customer_id     INT NOT NULL,
        product_id      INT NOT NULL,
        referrer_source referrer_source NOT NULL,
        device_type     device_type NOT NULL,
        duration_seconds INT NOT NULL,
        viewed_at       TIMESTAMP NOT NULL,
        PRIMARY KEY (id, viewed_at)
    ) PARTITION BY RANGE (viewed_at);
    ```


### point_transactions -- Point Ledger

Point earn/use/expire history. `balance_after` tracks the running balance.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: customer_id | INTEGER | -> customers(id) |
| :link: order_id | INTEGER | -> orders(id), nullable |
| type | TEXT | earn/use/expire |
| reason | TEXT | purchase/confirm/review/signup/use/expiry |
| amount | INTEGER | + for earn, - for use/expire |
| balance_after | INTEGER | Running balance after this transaction |
| expires_at | TEXT | Expiry date (earn transactions) |
| created_at | TEXT | Timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE point_transactions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id     INTEGER NOT NULL REFERENCES customers(id),
        order_id        INTEGER NULL REFERENCES orders(id),
        type            TEXT NOT NULL,                           -- earn/use/expire
        reason          TEXT NOT NULL,                           -- purchase/confirm/review/signup/use/expiry
        amount          INTEGER NOT NULL,                        -- + for earn, - for use/expire
        balance_after   INTEGER NOT NULL,                        -- running balance after this transaction
        expires_at      TEXT NULL,                               -- expiry date for earn transactions
        created_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE point_transactions (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        customer_id     INT NOT NULL,
        order_id        INT NULL,
        type            ENUM('earn','use','expire') NOT NULL,
        reason          ENUM('purchase','confirm','review','signup','use','expiry') NOT NULL,
        amount          INT NOT NULL,
        balance_after   INT NOT NULL,
        expires_at      DATETIME NULL,
        created_at      DATETIME NOT NULL,
        INDEX idx_point_tx_customer (customer_id),
        INDEX idx_point_tx_type (type),
        CONSTRAINT fk_point_tx_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE point_transactions (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        customer_id     INT NOT NULL REFERENCES customers(id),
        order_id        INT NULL,
        type            VARCHAR(10) NOT NULL CHECK (type IN ('earn','use','expire')),
        reason          VARCHAR(20) NOT NULL CHECK (reason IN ('purchase','confirm','review','signup','use','expiry')),
        amount          INT NOT NULL,
        balance_after   INT NOT NULL,
        expires_at      TIMESTAMP NULL,
        created_at      TIMESTAMP NOT NULL
    );
    ```


### promotions / promotion_products -- Promotions

Seasonal, flash, and category-wide promotions with their target products.

**promotions:**

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| name | TEXT | Promotion name |
| type | TEXT | seasonal/flash/category |
| discount_type | TEXT | percent/fixed |
| discount_value | REAL | Discount rate or amount |
| min_order_amount | REAL | Minimum order amount |
| started_at | TEXT | Start date |
| ended_at | TEXT | End date |
| is_active | INTEGER | Active flag |
| created_at | TEXT | Timestamp |

**promotion_products:**

| Column | Type | Notes |
|--------|------|-------|
| :link: promotion_id | INTEGER | -> promotions(id), composite PK |
| :link: product_id | INTEGER | -> products(id), composite PK |

=== "SQLite"

    ```sql
    CREATE TABLE promotions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT NOT NULL,
        type            TEXT NOT NULL,                           -- seasonal/flash/category
        discount_type   TEXT NOT NULL,                           -- percent/fixed
        discount_value  REAL NOT NULL,
        min_order_amount REAL NULL,
        started_at      TEXT NOT NULL,
        ended_at        TEXT NOT NULL,
        is_active       INTEGER NOT NULL DEFAULT 1,
        created_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE promotions (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        name            VARCHAR(200) NOT NULL,
        type            ENUM('seasonal','flash','category') NOT NULL,
        discount_type   ENUM('percent','fixed') NOT NULL,
        discount_value  DECIMAL(12,2) NOT NULL,
        min_order_amount DECIMAL(12,2) NULL,
        started_at      DATETIME NOT NULL,
        ended_at        DATETIME NOT NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        created_at      DATETIME NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE promotions (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name            VARCHAR(200) NOT NULL,
        type            promo_type NOT NULL,
        discount_type   coupon_type NOT NULL,
        discount_value  NUMERIC(12,2) NOT NULL,
        min_order_amount NUMERIC(12,2) NULL,
        started_at      TIMESTAMP NOT NULL,
        ended_at        TIMESTAMP NOT NULL,
        is_active       BOOLEAN NOT NULL DEFAULT TRUE,
        created_at      TIMESTAMP NOT NULL
    );
    ```

| override_price | REAL | Flash sale special price (NULL = use promotion discount) |

=== "SQLite"

    ```sql
    CREATE TABLE promotion_products (
        promotion_id    INTEGER NOT NULL REFERENCES promotions(id),
        product_id      INTEGER NOT NULL REFERENCES products(id),
        override_price  REAL NULL,                               -- flash sale special price (NULL = use promotion discount)
        PRIMARY KEY (promotion_id, product_id)
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE promotion_products (
        promotion_id    INT NOT NULL,
        product_id      INT NOT NULL,
        override_price  DECIMAL(12,2) NULL,
        PRIMARY KEY (promotion_id, product_id),
        CONSTRAINT fk_promo_products_promo FOREIGN KEY (promotion_id) REFERENCES promotions(id),
        CONSTRAINT fk_promo_products_product FOREIGN KEY (product_id) REFERENCES products(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE promotion_products (
        promotion_id    INT NOT NULL REFERENCES promotions(id),
        product_id      INT NOT NULL REFERENCES products(id),
        override_price  NUMERIC(12,2) NULL,
        PRIMARY KEY (promotion_id, product_id)
    );
    ```

### product_qna -- Product Q&A

Questions and answers about products. `parent_id` links answers to their original questions via self-reference.

| Column | Type | Notes |
|--------|------|-------|
| :key: id | INTEGER | Auto-increment |
| :link: product_id | INTEGER | -> products(id) |
| :link: customer_id | INTEGER | -> customers(id), customer question (NULL for answers) |
| :link: staff_id | INTEGER | -> staff(id), staff answer (NULL for questions) |
| :link: parent_id | INTEGER | -> product_qna(id), answer -> question (self-ref) |
| content | TEXT | Question or answer text |
| is_answered | INTEGER | Has been answered (0/1) |
| created_at | TEXT | Timestamp |

=== "SQLite"

    ```sql
    CREATE TABLE product_qna (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id      INTEGER NOT NULL REFERENCES products(id),
        customer_id     INTEGER NULL REFERENCES customers(id),   -- NULL for staff answers
        staff_id        INTEGER NULL REFERENCES staff(id),       -- NULL for customer questions
        parent_id       INTEGER NULL REFERENCES product_qna(id), -- self-join: answer→question
        content         TEXT NOT NULL,
        is_answered     INTEGER NOT NULL DEFAULT 0,
        created_at      TEXT NOT NULL
    )
    ```

=== "MySQL"

    ```sql
    CREATE TABLE product_qna (
        id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        product_id      INT NOT NULL,
        customer_id     INT NULL,
        staff_id        INT NULL,
        parent_id       INT NULL,
        content         TEXT NOT NULL,
        is_answered     BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      DATETIME NOT NULL,
        INDEX idx_qna_product (product_id),
        CONSTRAINT fk_qna_product FOREIGN KEY (product_id) REFERENCES products(id),
        CONSTRAINT fk_qna_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
        CONSTRAINT fk_qna_staff FOREIGN KEY (staff_id) REFERENCES staff(id),
        CONSTRAINT fk_qna_parent FOREIGN KEY (parent_id) REFERENCES product_qna(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ```

=== "PostgreSQL"

    ```sql
    CREATE TABLE product_qna (
        id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product_id      INT NOT NULL REFERENCES products(id),
        customer_id     INT NULL REFERENCES customers(id),
        staff_id        INT NULL REFERENCES staff(id),
        parent_id       INT NULL REFERENCES product_qna(id),
        content         TEXT NOT NULL,
        is_answered     BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      TIMESTAMP NOT NULL
    );
    ```


---

