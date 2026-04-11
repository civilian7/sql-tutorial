# 데이터베이스별 SQL 차이 — 치트시트

이 튜토리얼의 SQL은 SQLite 기준으로 작성되었습니다. 각 레슨에서 MySQL/PostgreSQL 탭으로 DB별 차이를 다루고 있으므로, 이 페이지는 **빠르게 훑어보는 종합 참조표** 역할을 합니다.

> 모든 DB에서 동작하는 SQL을 작성하는 것보다, **각 DB의 네이티브 문법**을 활용하는 것이 더 효율적입니다.

## 레슨별 DB 차이 가이드

각 레슨에서 SQLite/MySQL/PostgreSQL 탭으로 상세하게 다루는 주제입니다. 해당 레슨을 참고하세요.

| 주제 | 레슨 | 핵심 차이 |
|------|------|-----------|
| 페이징 | [03강](beginner/03-sort-limit.md) | LIMIT vs FETCH FIRST (ANSI) |
| NULL 처리 | [06강](beginner/06-null.md) | COALESCE(표준) vs IFNULL vs ISNULL vs NVL |
| CASE 표현식 | [07강](beginner/07-case.md) | IIF(SQLite) vs IF(MySQL) vs CASE(PG) |
| JOIN | [08~09강](intermediate/08-inner-join.md) | 문법은 동일, FULL OUTER JOIN 지원 여부 |
| 서브쿼리 | [10강](intermediate/10-subqueries.md) | 문법 거의 동일 |
| 날짜/시간 | [11강](intermediate/11-datetime.md) | SUBSTR vs YEAR() vs EXTRACT(), julianday vs DATEDIFF |
| 문자열 | [12강](intermediate/12-string.md) | `\|\|` vs CONCAT(), INSTR vs LOCATE vs POSITION |
| 숫자/변환/조건 | [13강](intermediate/13-utility-functions.md) | RANDOM vs RAND(), GREATEST/LEAST 지원 여부 |
| UNION/INTERSECT/EXCEPT | [14강](intermediate/14-union.md) | 문법 동일, EXCEPT vs MINUS(Oracle) |
| DML (UPSERT) | [15강](intermediate/15-dml.md) | ON CONFLICT vs ON DUPLICATE KEY |
| DDL | [16강](intermediate/16-ddl.md) | AUTOINCREMENT vs AUTO_INCREMENT vs GENERATED |
| 트랜잭션 | [17강](intermediate/17-transactions.md) | BEGIN vs START TRANSACTION |
| 윈도우 함수 | [18강](advanced/18-window.md) | 문법 동일, 최소 버전 차이 |
| CTE | [19강](advanced/19-cte.md) | WITH RECURSIVE(SQLite/MySQL/PG) vs WITH만(MSSQL/Oracle) |
| 뷰 | [22강](advanced/22-views.md) | CREATE OR REPLACE 지원 여부 |
| 인덱스 | [23강](advanced/23-indexes.md) | EXPLAIN 문법, 부분 인덱스 지원 |
| 트리거 | [24강](advanced/24-triggers.md) | SQLite: BEGIN...END, PG: 함수+트리거 분리 |
| JSON | [25강](advanced/25-json.md) | json_extract vs ->>, JSONB(PG) |
| 저장 프로시저 | [26강](advanced/26-stored-procedures.md) | SQLite 미지원, DELIMITER(MySQL), PL/pgSQL(PG) |

---

## 데이터 타입 대응표

| 용도 | SQLite | MySQL | PostgreSQL | SQL Server | Oracle |
|------|--------|-------|------------|------------|--------|
| 정수 | INTEGER | INT | INTEGER | INT | NUMBER(10) |
| 실수 | REAL | DECIMAL(12,2) | NUMERIC(12,2) | DECIMAL(12,2) | NUMBER(12,2) |
| 짧은 문자열 | TEXT | VARCHAR(200) | VARCHAR(200) | NVARCHAR(200) | VARCHAR2(200) |
| 긴 텍스트 | TEXT | TEXT | TEXT | NVARCHAR(MAX) | CLOB |
| 날짜/시간 | TEXT (ISO 8601) | DATETIME | TIMESTAMP | DATETIME2 | TIMESTAMP |
| 불리언 | INTEGER (0/1) | TINYINT(1) | BOOLEAN | BIT | NUMBER(1) |
| JSON | TEXT + json 함수 | JSON | JSONB | NVARCHAR(MAX) | CLOB |
| 바이너리 | BLOB | BLOB | BYTEA | VARBINARY(MAX) | BLOB |
| UUID | TEXT | CHAR(36) | UUID | UNIQUEIDENTIFIER | RAW(16) |

> SQLite는 동적 타입 시스템을 사용합니다. 위 타입 이름은 "타입 친화도(affinity)"를 나타내며, 실제로는 어떤 값이든 저장할 수 있습니다.

---

## 식별자 인용 (Quoting)

예약어나 공백이 포함된 식별자를 감쌀 때:

| DB | 문법 | 예시 |
|----|------|------|
| SQLite | 큰따옴표 또는 백틱 | `"order"` 또는 `` `order` `` |
| MySQL | 백틱 (기본) | `` `order` `` |
| PostgreSQL | 큰따옴표 | `"order"` (대소문자 구분 활성화) |
| SQL Server | 대괄호 | `[order]` |
| Oracle | 큰따옴표 | `"ORDER"` (대소문자 구분 주의) |

!!! tip "권장"
    가능하면 예약어를 식별자로 사용하지 마세요. `order` 대신 `orders`, `user` 대신 `users`처럼 복수형을 쓰면 인용 부호 없이도 안전합니다.

---

## 자동 증가 비교

| DB | 문법 | 비고 |
|----|------|------|
| SQLite | `INTEGER PRIMARY KEY AUTOINCREMENT` | ROWID 기반, AUTOINCREMENT은 선택 |
| MySQL | `INT AUTO_INCREMENT PRIMARY KEY` | 테이블당 하나, ENGINE=InnoDB |
| PostgreSQL | `INTEGER GENERATED ALWAYS AS IDENTITY` | SQL 표준. SERIAL은 레거시 |
| SQL Server | `INT IDENTITY(1,1) PRIMARY KEY` | |
| Oracle | `NUMBER GENERATED ALWAYS AS IDENTITY` | 12c+. 이전: SEQUENCE + TRIGGER |

자세한 내용: [16강 DDL](intermediate/16-ddl.md)

---

## MERGE 문

`MERGE`는 ANSI SQL 표준으로, 한 문장에서 INSERT/UPDATE/DELETE를 조건부로 수행합니다.

| DB | 지원 | 대체 문법 |
|----|------|-----------|
| SQLite | 미지원 | `ON CONFLICT` |
| MySQL | 미지원 | `ON DUPLICATE KEY UPDATE` |
| PostgreSQL | 15+ (부분) | `ON CONFLICT` 권장 |
| SQL Server | 2008+ | 완전 지원 |
| Oracle | 9i+ | 완전 지원 |

=== "SQL Server"

    ```sql
    MERGE INTO products AS target
    USING staging_products AS source
    ON target.sku = source.sku
    WHEN MATCHED AND source.is_active = 0 THEN
        DELETE
    WHEN MATCHED THEN
        UPDATE SET name = source.name, price = source.price
    WHEN NOT MATCHED THEN
        INSERT (sku, name, price)
        VALUES (source.sku, source.name, source.price);
    ```

=== "Oracle"

    ```sql
    MERGE INTO products target
    USING staging_products source
    ON (target.sku = source.sku)
    WHEN MATCHED THEN
        UPDATE SET name = source.name, price = source.price
    WHEN NOT MATCHED THEN
        INSERT (sku, name, price)
        VALUES (source.sku, source.name, source.price);
    ```

UPSERT 상세: [15강 DML](intermediate/15-dml.md)

---

## 기능 지원 버전 매트릭스

| 기능 | SQLite | MySQL | PostgreSQL | SQL Server | Oracle |
|------|--------|-------|------------|------------|--------|
| 윈도우 함수 | 3.25+ | 8.0+ | 8.4+ | 2005+ | 8i+ |
| CTE (WITH) | 3.8.3+ | 8.0+ | 8.4+ | 2005+ | 11gR2+ |
| 재귀 CTE | 3.8.3+ | 8.0+ | 8.4+ | 2005+ | 11gR2+ |
| JSON 함수 | 3.38+ | 5.7+ | 9.2+ | 2016+ | 12c+ |
| FULL OUTER JOIN | 3.39+ | 미지원 | 지원 | 지원 | 지원 |
| INTERSECT/EXCEPT | 3.34+ | 8.0.31+ | 지원 | 지원 | 지원 (MINUS) |
| 부분 인덱스 | 3.8+ | 미지원 | 지원 | 지원 (필터) | 미지원 |
| UPSERT | 3.24+ | 지원 | 9.5+ | MERGE | MERGE |
| 저장 프로시저 | 미지원 | 지원 | 지원 | 지원 | 지원 |
| 트리거 | 지원 | 지원 | 지원 | 지원 | 지원 |
| SEQUENCE | 미지원 | 미지원 | 지원 | 지원 | 지원 |

---

## 튜토리얼 SQL 변환 체크리스트

이 튜토리얼의 SQLite 쿼리를 다른 DB에서 실행할 때 확인할 항목:

| # | 확인 사항 | SQLite 원본 | MySQL | PostgreSQL | SQL Server |
|--:|-----------|-------------|-------|------------|------------|
| 1 | 행 제한 | `LIMIT 10` | 동일 | 동일 | `FETCH NEXT 10 ROWS ONLY` |
| 2 | 날짜 추출 | `SUBSTR(col, 1, 7)` | `DATE_FORMAT(col, '%Y-%m')` | `TO_CHAR(col, 'YYYY-MM')` | `FORMAT(col, 'yyyy-MM')` |
| 3 | 경과 일수 | `JULIANDAY(a) - JULIANDAY(b)` | `DATEDIFF(a, b)` | `a::date - b::date` | `DATEDIFF(DAY, b, a)` |
| 4 | 날짜 더하기 | `DATE('now', '+30 days')` | `DATE_ADD(NOW(), INTERVAL 30 DAY)` | `CURRENT_DATE + INTERVAL '30 days'` | `DATEADD(DAY, 30, GETDATE())` |
| 5 | NULL 대체 | `IFNULL(x, y)` | `IFNULL(x, y)` | `COALESCE(x, y)` | `ISNULL(x, y)` |
| 6 | 문자열 연결 | `a \|\| b` | `CONCAT(a, b)` | `a \|\| b` | `CONCAT(a, b)` |
| 7 | 불리언 | `is_active = 1` | 동일 | `is_active = TRUE` | 동일 |
| 8 | 타입 변환 | `CAST(x AS INTEGER)` | `CAST(x AS SIGNED)` | `x::integer` | `CAST(x AS INT)` |
| 9 | 현재 시각 | `datetime('now')` | `NOW()` | `NOW()` | `GETDATE()` |
| 10 | AUTOINCREMENT | `INTEGER PRIMARY KEY` | `INT AUTO_INCREMENT` | `GENERATED ALWAYS AS IDENTITY` | `INT IDENTITY(1,1)` |
| 11 | 랜덤 | `RANDOM()` | `RAND()` | `RANDOM()` | `NEWID()` |
| 12 | 정규표현식 | `GLOB '*[0-9]*'` | `REGEXP '[0-9]'` | `~ '[0-9]'` | `LIKE '%[0-9]%'` |
