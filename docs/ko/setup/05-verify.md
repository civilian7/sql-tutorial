# 05. 확인 및 첫 쿼리

데이터베이스가 정상적으로 생성되었는지 확인합니다.

## SQL 도구에서 열기

여러 DB를 하나의 도구에서 사용하고 싶다면 **[DBeaver](https://dbeaver.io/download/)**(무료, 오픈소스)를 추천합니다. SQLite, MySQL, PostgreSQL, Oracle, SQL Server를 모두 지원합니다.

!!! tip "ezQuery 출시 예정"
    현재 개발 중인 **ezQuery**가 출시되면 이 튜토리얼의 공식 추천 도구가 될 예정입니다. 튜토리얼 데이터베이스를 샘플로 내장하여, 설치 후 바로 실습을 시작할 수 있습니다.

=== "SQLite"

    | 도구 | 열기 |
    |------|------|
    | **DBeaver** (추천) | 새 연결 > SQLite > `output/ecommerce-ko.db` 파일 선택 |
    | DB Browser for SQLite | [sqlitebrowser.org](https://sqlitebrowser.org/dl/) > 데이터베이스 열기 > ecommerce-ko.db |
    | 명령줄 | `sqlite3 output/ecommerce-ko.db` |

=== "MySQL"

    | 도구 | 접속 |
    |------|------|
    | **DBeaver** (추천) | 새 연결 > MySQL > localhost:3306 > ecommerce |
    | MySQL Workbench | [dev.mysql.com](https://dev.mysql.com/downloads/workbench/) > 새 연결 > localhost:3306 |
    | 명령줄 | `mysql -u root -p ecommerce` |

=== "PostgreSQL"

    | 도구 | 접속 |
    |------|------|
    | **DBeaver** (추천) | 새 연결 > PostgreSQL > localhost:5432 > ecommerce |
    | pgAdmin | [pgadmin.org](https://www.pgadmin.org/download/) > 서버 추가 > localhost:5432 |
    | 명령줄 | `psql -U postgres ecommerce` |

## 커맨드라인에서 빠른 확인

GUI 도구를 열지 않고, 터미널에서 바로 확인할 수 있습니다.

=== "SQLite"

    ```bash
    sqlite3 output/ecommerce-ko.db "SELECT COUNT(*) FROM customers;"
    ```

    `5230`이 출력되면 정상입니다.

=== "MySQL"

    ```bash
    mysql -u root -p -e "SELECT COUNT(*) FROM ecommerce.customers;"
    ```

=== "PostgreSQL"

    ```bash
    psql -U postgres -d ecommerce -c "SELECT COUNT(*) FROM customers;"
    ```

## 첫 쿼리 실행

SQL 도구에서 아래 쿼리를 입력하고 실행하세요.

### 테이블 목록 확인

=== "SQLite"

    ```sql
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
    ORDER BY name;
    ```

=== "MySQL"

    ```sql
    SHOW TABLES;
    ```

=== "PostgreSQL"

    ```sql
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename;
    ```

테이블 목록이 표시되면 정상입니다.

### 데이터 확인

세 DB 모두 동일한 쿼리입니다:

```sql
-- 고객 데이터 맛보기
SELECT name, email, grade, point_balance
FROM customers
LIMIT 5;
```

```sql
-- 전체 데이터 규모
SELECT
    (SELECT COUNT(*) FROM customers) AS 고객수,
    (SELECT COUNT(*) FROM products) AS 상품수,
    (SELECT COUNT(*) FROM orders) AS 주문수,
    (SELECT COUNT(*) FROM reviews) AS 리뷰수;
```

결과가 정상적으로 나오면 준비 완료입니다.

## 자동 검증 스크립트

수동 확인 대신 검증 스크립트를 실행하면 연결, 테이블, 뷰, 트리거, 데이터 건수, FK 무결성을 한번에 확인할 수 있습니다.

=== "SQLite"

    ```bash
    python verify.py
    ```

=== "MySQL"

    ```bash
    python verify.py --target mysql
    ```

=== "PostgreSQL"

    ```bash
    python verify.py --target postgresql
    ```

=== "전체"

    ```bash
    python verify.py --all
    ```

정상이면 다음과 같이 출력됩니다:

```
==================================================
[VERIFY] SQL 튜토리얼 환경 검증
==================================================
  [OK] Python 3.12.x
  [OK] 파일 존재 (80.7 MB)
  [OK] 연결 성공
  [OK] 테이블 30개 확인
  [OK] 뷰 18개 확인
  [OK] 트리거 5개 확인
  [OK] customers: 5,230행
  [OK] orders: 34,908행
  ...
  [OK] FK 무결성 확인 (orders → customers)

==================================================
[OK] 검증 완료: 13/13 통과
==================================================
```

!!! warning "검증 실패 시"
    `[FAIL]` 항목이 있으면 해당 단계로 돌아가서 확인하세요:

    - 파일을 찾을 수 없음 → [03. 데이터 생성](03-generate.md)에서 `generate.py` 실행
    - 연결 실패 → [02. 데이터베이스 설치](02-database.md)에서 서버 상태 확인
    - 테이블/뷰 누락 → SQL 파일 수동 적용 여부 확인

[← 04. 생성기 고급 옵션](04-generate-advanced.md){ .md-button }
[00강: SQL 소개 →](../beginner/00-introduction.md){ .md-button .md-button--primary }
