# 01. 테이블

## 테이블(Table)이란?

테이블은 **데이터를 행(row)과 열(column)로 구조화하여 저장하는 단위**입니다. 엑셀의 시트 하나와 비슷하지만, 각 칼럼에 타입(정수, 문자열, 날짜 등)이 정해져 있고, 제약 조건(PK, FK, CHECK 등)으로 데이터 무결성을 보장합니다.

**테이블 설계에서 중요한 것:**

- **기본 키(PK)** — 각 행을 유일하게 식별하는 칼럼. 이 데이터베이스에서는 모든 테이블에 `id` 칼럼이 PK입니다
- **외래 키(FK)** — 다른 테이블의 행을 참조하는 칼럼. 예: `orders.customer_id → customers.id`
- **제약 조건** — NOT NULL, UNIQUE, CHECK 등으로 잘못된 데이터가 들어오는 것을 방지합니다
- **인덱스** — 자주 검색하는 칼럼에 인덱스를 설정하면 조회 속도가 향상됩니다

테이블 설계에 대한 상세 학습은 [16. DDL — 테이블 생성과 변경](../intermediate/16-ddl.md) 레슨에서 다룹니다.

## 테이블 목록

### categories — 상품 카테고리

3단계 계층 구조 (대분류 → 중분류 → 소분류). `parent_id`가 NULL이면 최상위.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 parent_id | INTEGER | O | → categories(id), NULL=최상위 (자기참조) |
| name | TEXT | - | 카테고리명 |
| slug | TEXT | - | UNIQUE — URL용 식별자 |
| depth | INTEGER | - | 0=대분류, 1=중분류, 2=소분류 |
| sort_order | INTEGER | - | 정렬 순서 |
| is_active | INTEGER | - | 활성 여부 (0/1) |
| created_at | TEXT | - | 생성 일시 |
| updated_at | TEXT | - | 수정 일시 |

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



### suppliers — 공급업체

상품을 공급하는 업체 정보 60개. 각 상품은 하나의 공급업체에 속합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| company_name | TEXT | - | 회사명 |
| business_number | TEXT | - | 사업자등록번호 (가상) |
| contact_name | TEXT | - | 담당자명 |
| phone | TEXT | - | 020-XXXX-XXXX (가상번호) |
| email | TEXT | - | contact@xxx.test.kr |
| address | TEXT | - | 사업장 주소 |
| is_active | INTEGER | - | 활성 여부 |
| created_at | TEXT | - | 생성 일시 |
| updated_at | TEXT | - | 수정 일시 |

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


### products — 상품

판매 중인 전자제품 2,800개 (medium). SKU 코드로 유일 식별. 가격, 원가, 재고, 단종 상태를 포함합니다.
`successor_id`로 단종 상품의 후속 모델을, `specs`로 JSON 형태의 상세 사양을 관리합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 category_id | INTEGER | - | → categories(id) |
| 🔗 supplier_id | INTEGER | - | → suppliers(id) |
| 🔗 successor_id | INTEGER | O | → products(id), 후속 모델 (자기참조, NULL=현행) |
| name | TEXT | - | 상품명 |
| sku | TEXT | - | UNIQUE — 재고관리코드 (예: LA-GEN-삼성-00001) |
| brand | TEXT | - | 브랜드명 |
| model_number | TEXT | - | 모델번호 |
| description | TEXT | O | 상품 설명 |
| specs | TEXT | O | JSON 상품 사양 (NULL 가능) |
| price | REAL | - | 현재 판매가 (원), CHECK >= 0 |
| cost_price | REAL | - | 원가 (원), CHECK >= 0 |
| stock_qty | INTEGER | - | 현재 재고 수량 |
| weight_grams | INTEGER | O | 배송 무게 (g) |
| is_active | INTEGER | - | 판매 중 여부 |
| discontinued_at | TEXT | O | 단종일 (NULL=판매중) |
| created_at | TEXT | - | 생성 일시 |
| updated_at | TEXT | - | 수정 일시 |

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



### product_images — 상품 이미지

상품별 다각도 이미지. `is_primary`로 대표 이미지를 구분합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 product_id | INTEGER | - | → products(id) |
| image_url | TEXT | - | 이미지 경로/URL |
| file_name | TEXT | - | 파일명 (예: 42_1.jpg) |
| image_type | TEXT | - | main/angle/side/back/detail/package/lifestyle 등 |
| alt_text | TEXT | O | 대체 텍스트 |
| width | INTEGER | - | 이미지 너비 (px) |
| height | INTEGER | - | 이미지 높이 (px) |
| file_size | INTEGER | - | 파일 크기 (bytes) |
| sort_order | INTEGER | - | 표시 순서 |
| is_primary | INTEGER | - | 대표 이미지 여부 |
| created_at | TEXT | - | 생성 일시 |

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

!!! tip "실제 상품 이미지 다운로드"
    기본 생성 시 `image_url`은 [placehold.co](https://placehold.co) 플레이스홀더 URL입니다.
    SQL 학습에는 이 상태로 충분하지만, 실제 이미지가 필요하다면 **Pexels API**를 통해 카테고리별 실사 이미지를 다운로드할 수 있습니다.

    1. [pexels.com/api](https://www.pexels.com/api/)에서 무료 API 키 발급 (월 200회 제한)
    2. 생성기 실행 시 `--download-images` 옵션 추가:

        ```bash
        python -m src.cli.generate --download-images --pexels-key YOUR_API_KEY
        # 또는 환경 변수 사용
        export PEXELS_API_KEY=YOUR_API_KEY
        python -m src.cli.generate --download-images
        ```

    3. `output/images/` 디렉토리에 카테고리별 이미지가 저장되고, `image_url`이 로컬 경로로 갱신됩니다.

### product_prices — 가격 변경 이력

상품 가격 변동을 기록합니다. `ended_at`이 NULL이면 현재 적용 중인 가격입니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 product_id | INTEGER | - | → products(id) |
| price | REAL | - | 해당 기간 판매가 |
| started_at | TEXT | - | 적용 시작일 |
| ended_at | TEXT | O | 적용 종료일 (NULL=현재가) |
| change_reason | TEXT | - | regular/promotion/price_drop/cost_increase |

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


### customers — 고객

쇼핑몰 회원 52,300명 (medium). 등급제(BRONZE~VIP), 적립금, 활성/탈퇴 상태를 관리합니다.
`acquisition_channel`로 가입 경로를 추적합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| email | TEXT | - | UNIQUE — `user123@testmail.kr` |
| password_hash | TEXT | - | SHA-256 (가상) |
| name | TEXT | - | 고객명 |
| phone | TEXT | - | `020-XXXX-XXXX` (가상번호) |
| birth_date | TEXT | O | 생년월일 (~15% NULL) |
| gender | TEXT | O | M/F (NULL ~10%, M:65%) |
| grade | TEXT | - | CHECK: BRONZE/SILVER/GOLD/VIP |
| point_balance | INTEGER | - | 적립금 잔액, CHECK >= 0 |
| acquisition_channel | TEXT | O | organic/search_ad/social/referral/direct (NULL 가능) |
| is_active | INTEGER | - | 0=탈퇴, 1=활성 |
| last_login_at | TEXT | O | NULL = 한 번도 로그인 안 함 |
| created_at | TEXT | - | 가입일 |
| updated_at | TEXT | - | 수정일 |

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



### customer_addresses — 고객 배송지

고객별 다수 배송지. `is_default`로 기본 배송지를 구분합니다.
`updated_at`으로 주소 변경 이력을 추적합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 customer_id | INTEGER | - | → customers(id) |
| label | TEXT | - | 자택/회사/기타 |
| recipient_name | TEXT | - | 수령인 |
| phone | TEXT | - | 수령인 연락처 |
| zip_code | TEXT | - | 우편번호 |
| address1 | TEXT | - | 기본 주소 |
| address2 | TEXT | O | 상세 주소 |
| is_default | INTEGER | - | 기본 배송지 여부 |
| created_at | TEXT | - | 생성 일시 |
| updated_at | TEXT | O | 주소 변경일 (NULL 가능) |

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


### staff — 직원

쇼핑몰 운영 직원 50명 (medium). CS 담당자 배정, 문의 처리에 사용됩니다.
`manager_id`로 상위 관리자를 참조하는 자기 참조 구조를 가집니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 manager_id | INTEGER | O | → staff(id), 상위 관리자 (자기참조, NULL=최상위) |
| email | TEXT | - | UNIQUE — staffN@techshop-staff.kr |
| name | TEXT | - | 직원명 |
| phone | TEXT | - | 연락처 |
| department | TEXT | - | 영업/물류/CS/마케팅/개발/경영 |
| role | TEXT | - | admin/manager/staff |
| is_active | INTEGER | - | 활성 여부 |
| hired_at | TEXT | - | 입사일 |
| created_at | TEXT | - | 생성 일시 |

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


### orders — 주문

핵심 트랜잭션 테이블 (medium: 378,368건). 주문번호 `ORD-YYYYMMDD-NNNNN` 기반, 9단계 상태 관리.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| order_number | TEXT | - | UNIQUE — `ORD-20240315-00001` |
| 🔗 customer_id | INTEGER | - | → customers(id) |
| 🔗 address_id | INTEGER | - | → customer_addresses(id) |
| 🔗 staff_id | INTEGER | O | → staff(id), CS 없으면 NULL |
| status | TEXT | - | 아래 상태 흐름 참조 |
| total_amount | REAL | - | 최종 결제 금액 |
| discount_amount | REAL | - | 총 할인 금액 |
| shipping_fee | REAL | - | 배송비 (5만원 이상 무료) |
| point_used | INTEGER | - | 사용 적립금 |
| point_earned | INTEGER | - | 적립 예정 포인트 |
| notes | TEXT | O | 배송 요청사항 (~35%) |
| ordered_at | TEXT | - | 주문 일시 |
| completed_at | TEXT | O | 구매 확정일 |
| cancelled_at | TEXT | O | 취소일 |
| created_at | TEXT | - | 생성 일시 |
| updated_at | TEXT | - | 수정 일시 |

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



### order_items — 주문 상세

주문별 상품 목록. 주문 시점의 단가와 할인을 기록하여 가격 변동에 독립적입니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 order_id | INTEGER | - | → orders(id) |
| 🔗 product_id | INTEGER | - | → products(id) |
| quantity | INTEGER | - | 수량, CHECK > 0 |
| unit_price | REAL | - | 주문 시점 단가 |
| discount_amount | REAL | - | 아이템 할인 |
| subtotal | REAL | - | (단가 x 수량) - 할인 |

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



### payments — 결제

주문당 1건의 결제. 카드, 계좌이체, 간편결제 등 다양한 수단을 지원합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 order_id | INTEGER | - | → orders(id) |
| method | TEXT | - | card/bank_transfer/virtual_account/kakao_pay/naver_pay/point |
| amount | REAL | - | 결제 금액, CHECK >= 0 |
| status | TEXT | - | CHECK: pending/completed/failed/refunded |
| pg_transaction_id | TEXT | O | PG사 거래번호 (가상) |
| card_issuer | TEXT | O | 신한/삼성/KB국민/현대/롯데/하나/우리/NH농협/BC |
| card_approval_no | TEXT | O | 카드 승인번호 (8자리) |
| installment_months | INTEGER | O | 할부 개월 (0=일시불) |
| bank_name | TEXT | O | 은행명 (계좌이체/가상계좌) |
| account_no | TEXT | O | 가상계좌 번호 |
| depositor_name | TEXT | O | 입금자명 |
| easy_pay_method | TEXT | O | 간편결제 내부 수단 |
| receipt_type | TEXT | O | 소득공제/지출증빙 |
| receipt_no | TEXT | O | 현금영수증 번호 |
| paid_at | TEXT | O | 결제 완료 시각 |
| refunded_at | TEXT | O | 환불 시각 |
| created_at | TEXT | - | 생성 일시 |

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


### shipping — 배송

주문별 배송 추적. 택배사별 운송장 번호와 상태를 관리합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 order_id | INTEGER | - | → orders(id) |
| carrier | TEXT | - | CJ대한통운/한진택배/로젠택배/우체국택배 |
| tracking_number | TEXT | - | 운송장 번호 |
| status | TEXT | - | preparing/shipped/in_transit/delivered/returned |
| shipped_at | TEXT | O | 출고일 |
| delivered_at | TEXT | O | 배송완료일 |
| created_at | TEXT | - | 생성 일시 |
| updated_at | TEXT | - | 수정 일시 |

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


### reviews — 상품 리뷰

구매 인증 리뷰 86,806건 (medium). 1~5점 평점 (5점 40%, 4점 30%, 3점 15%, 2점 10%, 1점 5%).

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 product_id | INTEGER | - | → products(id) |
| 🔗 customer_id | INTEGER | - | → customers(id) |
| 🔗 order_id | INTEGER | - | → orders(id) |
| rating | INTEGER | - | 1~5점, CHECK BETWEEN 1 AND 5 |
| title | TEXT | O | 리뷰 제목 (~80%) |
| content | TEXT | - | 리뷰 본문 |
| is_verified | INTEGER | - | 구매 인증 여부 |
| created_at | TEXT | - | 작성 일시 |
| updated_at | TEXT | - | 수정 일시 |

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



### wishlists — 위시리스트

고객이 관심 상품으로 등록. 동일 고객-상품 조합은 UNIQUE.
`is_purchased`로 찜한 상품의 구매 전환 여부를 추적합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 customer_id | INTEGER | - | → customers(id) |
| 🔗 product_id | INTEGER | - | → products(id) |
| is_purchased | INTEGER | - | 구매 전환 여부 (0/1) |
| notify_on_sale | INTEGER | - | 가격 하락 알림 (0/1) |
| created_at | TEXT | - | 등록 일시 |

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


### complaints — 고객 문의/불만

CS 문의 접수 및 처리 37,953건 (medium). 7개 카테고리, 5개 채널, 4단계 우선순위.
`type` (inquiry/claim/report), `sub_category`, `compensation_type`, `compensation_amount`, `escalated`, `response_count` 칼럼으로 상세한 CS 분석이 가능합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 order_id | INTEGER | O | → orders(id), NULL=일반문의 |
| 🔗 customer_id | INTEGER | - | → customers(id) |
| 🔗 staff_id | INTEGER | - | → staff(id), 담당 CS 직원 |
| category | TEXT | - | product_defect/delivery_issue/wrong_item/refund_request/exchange_request/general_inquiry/price_inquiry |
| channel | TEXT | - | website/phone/email/chat/kakao |
| priority | TEXT | - | low/medium/high/urgent |
| status | TEXT | - | open/resolved/closed |
| title | TEXT | - | 문의 제목 |
| content | TEXT | - | 문의 내용 |
| resolution | TEXT | O | 처리 결과 (해결 시) |
| type | TEXT | - | inquiry/claim/report (문의 유형) |
| sub_category | TEXT | O | 상세 카테고리 (예: initial_defect/in_use_damage/misdelivery) |
| compensation_type | TEXT | O | refund/exchange/partial_refund/point_compensation/none |
| compensation_amount | REAL | O | 보상 금액 |
| escalated | INTEGER | - | 상위 관리자 에스컬레이션 (0/1) |
| response_count | INTEGER | - | 응대 횟수 |
| created_at | TEXT | - | 접수일 |
| resolved_at | TEXT | O | 해결일 |
| closed_at | TEXT | O | 종료일 |

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


### returns — 반품/교환

반품 또는 교환 요청 11,413건 (medium). 사유, 수거, 검수, 환불의 전 과정을 추적합니다.
`claim_id`(CS 불만에서 기원한 반품 연결), `exchange_product_id`(교환 대상 상품), `restocking_fee`(변심 반품 수수료) 칼럼이 포함됩니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 order_id | INTEGER | - | → orders(id) |
| 🔗 customer_id | INTEGER | - | → customers(id) |
| 🔗 claim_id | INTEGER | O | → complaints(id), CS 불만에서 기원 시 |
| 🔗 exchange_product_id | INTEGER | O | → products(id), 교환 대상 상품 |
| return_type | TEXT | - | refund/exchange |
| reason | TEXT | - | defective/wrong_item/change_of_mind/damaged_in_transit/not_as_described/late_delivery |
| reason_detail | TEXT | O | 상세 사유 설명 |
| status | TEXT | - | requested/pickup_scheduled/in_transit/completed |
| is_partial | INTEGER | - | 부분반품 여부 (~17%) |
| refund_amount | REAL | - | 환불 금액 |
| refund_status | TEXT | - | pending/refunded/exchanged/partial_refund |
| restocking_fee | REAL | - | 변심 반품 재입고 수수료 (기본 0) |
| carrier | TEXT | O | 수거 택배사 |
| tracking_number | TEXT | O | 수거 운송장 번호 |
| requested_at | TEXT | - | 반품 요청일 |
| pickup_at | TEXT | O | 수거 예정/완료일 |
| received_at | TEXT | O | 물류센터 입고일 |
| inspected_at | TEXT | O | 검수 완료일 |
| inspection_result | TEXT | O | good/opened_good/defective/unsellable |
| completed_at | TEXT | O | 처리 완료일 |
| created_at | TEXT | - | 생성 일시 |

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


### coupons — 쿠폰

할인 쿠폰 200종 (medium). 정율(percent) 또는 정액(fixed) 할인, 사용 한도, 유효기간을 관리합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| code | TEXT | - | UNIQUE — 쿠폰 코드 (CP2401001) |
| name | TEXT | - | 쿠폰명 |
| type | TEXT | - | percent/fixed |
| discount_value | REAL | - | 할인율(%) 또는 할인금액(원), CHECK > 0 |
| min_order_amount | REAL | O | 최소 주문금액 |
| max_discount | REAL | O | 최대 할인금액 (percent 타입) |
| usage_limit | INTEGER | O | 전체 사용 한도 |
| per_user_limit | INTEGER | O | 1인당 사용 한도 |
| is_active | INTEGER | - | 활성 여부 |
| started_at | TEXT | - | 유효기간 시작 |
| expired_at | TEXT | - | 유효기간 종료 |
| created_at | TEXT | - | 생성 일시 |

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


### coupon_usage — 쿠폰 사용 내역

쿠폰이 실제로 사용된 기록. 어떤 고객이 어떤 주문에서 얼마 할인받았는지 추적합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 coupon_id | INTEGER | - | → coupons(id) |
| 🔗 customer_id | INTEGER | - | → customers(id) |
| 🔗 order_id | INTEGER | - | → orders(id) |
| discount_amount | REAL | - | 실제 할인 금액 |
| used_at | TEXT | - | 사용 일시 |

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


### inventory_transactions — 재고 입출고

상품 재고 변동 이력. 입고(양수), 출고(음수), 반품, 조정을 기록합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 product_id | INTEGER | - | → products(id) |
| type | TEXT | - | inbound/outbound/return/adjustment |
| quantity | INTEGER | - | 양수=입고, 음수=출고 |
| reference_id | INTEGER | O | 관련 주문 ID |
| notes | TEXT | O | 초기입고/정기입고/반품입고 등 |
| created_at | TEXT | - | 발생 일시 |

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


### carts — 장바구니

고객별 장바구니. 주문 전환(converted), 포기(abandoned) 상태를 추적합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 customer_id | INTEGER | - | → customers(id) |
| status | TEXT | - | active/converted/abandoned |
| created_at | TEXT | - | 생성 일시 |
| updated_at | TEXT | - | 수정 일시 |

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


### cart_items — 장바구니 상품

장바구니에 담긴 개별 상품과 수량.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 cart_id | INTEGER | - | → carts(id) |
| 🔗 product_id | INTEGER | - | → products(id) |
| quantity | INTEGER | - | 수량 |
| added_at | TEXT | - | 추가 일시 |

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


### calendar — 날짜 차원 테이블

2016~2025년 전체 날짜를 포함하는 차원 테이블. CROSS JOIN, 날짜 갭 분석에 활용합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 date_key | TEXT | - | YYYY-MM-DD (PK) |
| year | INTEGER | - | 연도 |
| month | INTEGER | - | 월 |
| day | INTEGER | - | 일 |
| quarter | INTEGER | - | 분기 (1~4) |
| day_of_week | INTEGER | - | 0=월 ~ 6=일 |
| day_name | TEXT | - | Monday~Sunday |
| is_weekend | INTEGER | - | 주말 여부 (0/1) |
| is_holiday | INTEGER | - | 공휴일 여부 (0/1) |
| holiday_name | TEXT | O | 공휴일명 |

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


### customer_grade_history — 등급 변경 이력

고객 등급 변동을 기록합니다. SCD(Slowly Changing Dimension) Type 2 패턴 학습에 활용됩니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 customer_id | INTEGER | - | → customers(id) |
| old_grade | TEXT | O | 이전 등급 (NULL=최초 가입) |
| new_grade | TEXT | - | 새 등급 |
| changed_at | TEXT | - | 변경 일시 |
| reason | TEXT | - | signup/upgrade/downgrade/yearly_review |

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


### tags / product_tags — 상품 태그

태그 80개 (medium)와 상품-태그 매핑. M:N 관계의 교차(bridge) 테이블 패턴을 보여줍니다.

**tags:**

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| name | TEXT | - | UNIQUE — 태그명 |
| category | TEXT | - | feature/use_case/target/spec |

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

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔗 product_id | INTEGER | - | → products(id), 복합 PK |
| 🔗 tag_id | INTEGER | - | → tags(id), 복합 PK |

### product_views — 상품 조회 로그

상품 페이지 조회 기록. 유입 경로, 디바이스, 체류 시간을 포함합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 customer_id | INTEGER | - | → customers(id) |
| 🔗 product_id | INTEGER | - | → products(id) |
| referrer_source | TEXT | - | direct/search/ad/recommendation/social/email |
| device_type | TEXT | - | desktop/mobile/tablet |
| duration_seconds | INTEGER | O | 페이지 체류 시간 (초) |
| viewed_at | TEXT | - | 조회 일시 |

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


### point_transactions — 포인트 거래

포인트 적립/사용/소멸 내역. `balance_after`로 잔액 추이를 추적합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 customer_id | INTEGER | - | → customers(id) |
| 🔗 order_id | INTEGER | O | → orders(id), NULL 가능 |
| type | TEXT | - | earn/use/expire |
| reason | TEXT | - | purchase/confirm/review/signup/use/expiry |
| amount | INTEGER | - | +적립, -사용/소멸 |
| balance_after | INTEGER | - | 거래 후 잔액 |
| expires_at | TEXT | O | 유효기한 (earn 거래) |
| created_at | TEXT | - | 거래 일시 |

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


### promotions / promotion_products — 프로모션

시즌별/플래시/카테고리 프로모션과 대상 상품을 관리합니다.

**promotions:**

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| name | TEXT | - | 프로모션명 |
| type | TEXT | - | seasonal/flash/category |
| discount_type | TEXT | - | percent/fixed |
| discount_value | REAL | - | 할인율/금액 |
| min_order_amount | REAL | O | 최소 주문금액 |
| started_at | TEXT | - | 시작일 |
| ended_at | TEXT | - | 종료일 |
| is_active | INTEGER | - | 활성 여부 |
| created_at | TEXT | - | 생성 일시 |

**promotion_products:**

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔗 promotion_id | INTEGER | - | → promotions(id), 복합 PK |
| 🔗 product_id | INTEGER | - | → products(id), 복합 PK |

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

| override_price | REAL | O | 플래시 세일 특가 (NULL=프로모션 할인 적용) |

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

### product_qna — 상품 Q&A

상품에 대한 질문과 답변. `parent_id`로 질문-답변 쌍을 자기 참조로 연결합니다.

| 칼럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| 🔑 id | INTEGER | - | 자동 증가 |
| 🔗 product_id | INTEGER | - | → products(id) |
| 🔗 customer_id | INTEGER | O | → customers(id), 고객 질문 (답변 시 NULL) |
| 🔗 staff_id | INTEGER | O | → staff(id), 직원 답변 (질문 시 NULL) |
| 🔗 parent_id | INTEGER | O | → product_qna(id), 답변→질문 (자기참조) |
| content | TEXT | - | 질문/답변 내용 |
| is_answered | INTEGER | - | 답변 완료 여부 |
| created_at | TEXT | - | 작성 일시 |

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

