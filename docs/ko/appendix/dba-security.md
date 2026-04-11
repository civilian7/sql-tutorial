# DBA 기초 --- 권한과 보안

SQL을 배우다 보면 "이 사용자에게는 읽기만 허용하고 싶다"는 상황을 만나게 됩니다. 이때 사용하는 것이 **DCL(Data Control Language)** --- `GRANT`와 `REVOKE`입니다.

!!! warning "SQLite는 해당 없음"
    SQLite는 파일 기반 데이터베이스로, 사용자/권한 개념이 없습니다. 파일 시스템의 읽기/쓰기 권한이 곧 접근 제어입니다. 이 부록은 **MySQL**과 **PostgreSQL** 기준으로 설명합니다.

---

## 사용자 생성

=== "MySQL"

    ```sql
    -- 모든 호스트에서 접속 가능한 사용자
    CREATE USER 'app_user'@'%' IDENTIFIED BY 'SecurePass123!';

    -- 특정 IP에서만 접속 가능한 사용자
    CREATE USER 'app_user'@'192.168.1.%' IDENTIFIED BY 'SecurePass123!';
    ```

    MySQL은 `'사용자명'@'호스트'` 형식으로 접속 범위를 제한할 수 있습니다.

=== "PostgreSQL"

    ```sql
    CREATE USER app_user WITH PASSWORD 'SecurePass123!';

    -- 또는 CREATE ROLE (LOGIN 옵션 추가)
    CREATE ROLE app_user WITH LOGIN PASSWORD 'SecurePass123!';
    ```

    PostgreSQL에서 `USER`와 `ROLE WITH LOGIN`은 동일합니다.

---

## 권한 부여 (GRANT)

특정 테이블에 대한 권한을 부여합니다.

```sql
-- 읽기 전용
GRANT SELECT ON customers TO app_user;

-- 읽기 + 쓰기
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;

-- 삭제까지 포함
GRANT SELECT, INSERT, UPDATE, DELETE ON order_items TO app_user;
```

### 데이터베이스/스키마 단위 권한

=== "MySQL"

    ```sql
    -- 특정 데이터베이스의 모든 테이블에 전체 권한
    GRANT ALL PRIVILEGES ON techshop.* TO 'app_user'@'%';

    -- 특정 데이터베이스의 모든 테이블에 읽기 권한
    GRANT SELECT ON techshop.* TO 'analyst'@'%';
    ```

=== "PostgreSQL"

    ```sql
    -- 스키마 내 모든 테이블에 전체 권한
    GRANT ALL ON ALL TABLES IN SCHEMA public TO app_user;

    -- 스키마 내 모든 테이블에 읽기 권한
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;
    ```

### 실전 예시: TechShop 사용자 설계

| 사용자 | 용도 | 권한 |
|---|---|---|
| `ts_admin` | DB 관리자 | `ALL PRIVILEGES` |
| `ts_app` | 웹 애플리케이션 | `SELECT, INSERT, UPDATE, DELETE` (주요 테이블) |
| `ts_analyst` | 데이터 분석가 | `SELECT` (전체 테이블) |
| `ts_cs` | 고객센터 상담원 | `SELECT` (`customers`, `orders`, `order_items`만) |

```sql
-- MySQL 예시: 고객센터 상담원 계정
CREATE USER 'ts_cs'@'%' IDENTIFIED BY 'CsTeam2024!';
GRANT SELECT ON techshop.customers TO 'ts_cs'@'%';
GRANT SELECT ON techshop.orders TO 'ts_cs'@'%';
GRANT SELECT ON techshop.order_items TO 'ts_cs'@'%';
```

---

## 권한 회수 (REVOKE)

부여한 권한을 다시 제거합니다. 문법은 `GRANT`와 대칭입니다.

```sql
-- 특정 권한 회수
REVOKE INSERT ON orders FROM app_user;

-- 모든 권한 회수
REVOKE ALL PRIVILEGES ON techshop.* FROM 'app_user'@'%';  -- MySQL
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM app_user;   -- PostgreSQL
```

---

## 역할 (ROLE)

사용자마다 개별 권한을 부여하면 관리가 어렵습니다. **역할(Role)**을 만들어 권한을 묶고, 사용자에게 역할을 할당하는 것이 실무에서 권장되는 방식입니다.

=== "PostgreSQL"

    ```sql
    -- 1. 역할 생성
    CREATE ROLE analyst_role;

    -- 2. 역할에 권한 부여
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst_role;

    -- 3. 사용자에게 역할 할당
    GRANT analyst_role TO kim_analyst;
    GRANT analyst_role TO lee_analyst;
    ```

    PostgreSQL은 처음부터 역할 기반으로 설계되어 `ROLE`과 `USER`가 본질적으로 같습니다.

=== "MySQL (8.0+)"

    ```sql
    -- 1. 역할 생성
    CREATE ROLE 'analyst_role';

    -- 2. 역할에 권한 부여
    GRANT SELECT ON techshop.* TO 'analyst_role';

    -- 3. 사용자에게 역할 할당
    GRANT 'analyst_role' TO 'kim_analyst'@'%';
    GRANT 'analyst_role' TO 'lee_analyst'@'%';

    -- 4. 기본 역할 설정 (로그인 시 자동 활성화)
    SET DEFAULT ROLE 'analyst_role' TO 'kim_analyst'@'%';
    ```

    MySQL은 8.0부터 역할을 지원합니다. `SET DEFAULT ROLE`을 하지 않으면 로그인 후 `SET ROLE`로 수동 활성화해야 합니다.

### TechShop 역할 설계 예시

```
admin_role ─── ALL PRIVILEGES
app_role ───── SELECT, INSERT, UPDATE, DELETE (주요 테이블)
analyst_role ─ SELECT (전체)
cs_role ────── SELECT (customers, orders, order_items)
```

---

## 최소 권한 원칙

!!! tip "Principle of Least Privilege"
    각 사용자에게는 **업무에 필요한 최소한의 권한만** 부여합니다.

이 원칙이 중요한 이유:

- **사고 방지**: 분석가가 실수로 `DELETE FROM customers`를 실행해도, `SELECT`만 있으면 에러로 끝납니다
- **보안 강화**: 계정이 탈취되더라도 피해 범위가 제한됩니다
- **감사 용이**: 누가 어떤 작업을 할 수 있는지 명확합니다

### TechShop 시나리오

> CS팀이 고객 주문을 조회해야 합니다. "편하게 전체 권한을 줄까?" --- 절대 안 됩니다.

```sql
-- 나쁜 예: 전체 권한
GRANT ALL PRIVILEGES ON techshop.* TO 'ts_cs'@'%';

-- 좋은 예: 필요한 테이블에 읽기만
GRANT SELECT ON techshop.customers TO 'ts_cs'@'%';
GRANT SELECT ON techshop.orders TO 'ts_cs'@'%';
GRANT SELECT ON techshop.order_items TO 'ts_cs'@'%';
```

CS팀은 `products`, `suppliers`, `inventory` 등에 접근할 이유가 없습니다.

---

## 정리 표

| 명령 | 설명 | MySQL | PostgreSQL |
|---|---|---|---|
| `CREATE USER` | 사용자 생성 | `'user'@'host' IDENTIFIED BY 'pw'` | `user WITH PASSWORD 'pw'` |
| `DROP USER` | 사용자 삭제 | `'user'@'host'` | `user` |
| `GRANT` | 권한 부여 | `ON db.table TO 'user'@'host'` | `ON table TO user` |
| `REVOKE` | 권한 회수 | `ON db.table FROM 'user'@'host'` | `ON table FROM user` |
| `CREATE ROLE` | 역할 생성 | 8.0+ 지원 | 기본 지원 |
| `GRANT role TO user` | 역할 할당 | `SET DEFAULT ROLE` 필요 | 즉시 적용 |
| `SHOW GRANTS` | 권한 조회 | `SHOW GRANTS FOR 'user'@'host'` | `\du` 또는 `pg_roles` 뷰 |

---

!!! note "본 튜토리얼로 돌아가기"
    이 부록은 참고 자료입니다. 튜토리얼 본문에서는 SQLite를 사용하므로 DCL 실습 없이도 모든 강의를 진행할 수 있습니다. [교재 소개](../index.md)로 돌아가서 학습을 계속하세요.
