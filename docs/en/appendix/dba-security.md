# DBA Basics --- Permissions and Security

As you learn SQL, you'll encounter situations like "I want to allow this user read-only access." This is where **DCL (Data Control Language)** comes in --- `GRANT` and `REVOKE`.

!!! warning "Not Applicable to SQLite"
    SQLite is a file-based database with no user/permission concepts. File system read/write permissions serve as access control. This appendix is based on **MySQL** and **PostgreSQL**.

---

## Creating Users

=== "MySQL"

    ```sql
    -- User accessible from all hosts
    CREATE USER 'app_user'@'%' IDENTIFIED BY 'SecurePass123!';

    -- User accessible only from specific IP
    CREATE USER 'app_user'@'192.168.1.%' IDENTIFIED BY 'SecurePass123!';
    ```

    MySQL uses the `'username'@'host'` format to restrict connection scope.

=== "PostgreSQL"

    ```sql
    CREATE USER app_user WITH PASSWORD 'SecurePass123!';

    -- Or CREATE ROLE (with LOGIN option)
    CREATE ROLE app_user WITH LOGIN PASSWORD 'SecurePass123!';
    ```

    In PostgreSQL, `USER` and `ROLE WITH LOGIN` are equivalent.

---

## Granting Permissions (GRANT)

Grant permissions on specific tables.

```sql
-- Read-only
GRANT SELECT ON customers TO app_user;

-- Read + write
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;

-- Including delete
GRANT SELECT, INSERT, UPDATE, DELETE ON order_items TO app_user;
```

### Database/Schema-Level Permissions

=== "MySQL"

    ```sql
    -- Full permissions on all tables in a specific database
    GRANT ALL PRIVILEGES ON techshop.* TO 'app_user'@'%';

    -- Read-only on all tables in a specific database
    GRANT SELECT ON techshop.* TO 'analyst'@'%';
    ```

=== "PostgreSQL"

    ```sql
    -- Full permissions on all tables in a schema
    GRANT ALL ON ALL TABLES IN SCHEMA public TO app_user;

    -- Read-only on all tables in a schema
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;
    ```

### Practical Example: TechShop User Design

| User | Purpose | Permissions |
|------|---------|-------------|
| `ts_admin` | DB administrator | `ALL PRIVILEGES` |
| `ts_app` | Web application | `SELECT, INSERT, UPDATE, DELETE` (main tables) |
| `ts_analyst` | Data analyst | `SELECT` (all tables) |
| `ts_cs` | Customer service agent | `SELECT` (`customers`, `orders`, `order_items` only) |

```sql
-- MySQL example: Customer service agent account
CREATE USER 'ts_cs'@'%' IDENTIFIED BY 'CsTeam2024!';
GRANT SELECT ON techshop.customers TO 'ts_cs'@'%';
GRANT SELECT ON techshop.orders TO 'ts_cs'@'%';
GRANT SELECT ON techshop.order_items TO 'ts_cs'@'%';
```

---

## Revoking Permissions (REVOKE)

Remove previously granted permissions. The syntax mirrors `GRANT`.

```sql
-- Revoke specific permission
REVOKE INSERT ON orders FROM app_user;

-- Revoke all permissions
REVOKE ALL PRIVILEGES ON techshop.* FROM 'app_user'@'%';  -- MySQL
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM app_user;   -- PostgreSQL
```

---

## Roles (ROLE)

Granting individual permissions to each user becomes hard to manage. The recommended practice is to create **roles** that bundle permissions, then assign roles to users.

=== "PostgreSQL"

    ```sql
    -- 1. Create role
    CREATE ROLE analyst_role;

    -- 2. Grant permissions to role
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst_role;

    -- 3. Assign role to users
    GRANT analyst_role TO kim_analyst;
    GRANT analyst_role TO lee_analyst;
    ```

    PostgreSQL is designed around roles from the start, so `ROLE` and `USER` are essentially the same.

=== "MySQL (8.0+)"

    ```sql
    -- 1. Create role
    CREATE ROLE 'analyst_role';

    -- 2. Grant permissions to role
    GRANT SELECT ON techshop.* TO 'analyst_role';

    -- 3. Assign role to users
    GRANT 'analyst_role' TO 'kim_analyst'@'%';
    GRANT 'analyst_role' TO 'lee_analyst'@'%';

    -- 4. Set default role (auto-activate on login)
    SET DEFAULT ROLE 'analyst_role' TO 'kim_analyst'@'%';
    ```

    MySQL supports roles from version 8.0. Without `SET DEFAULT ROLE`, you must manually activate with `SET ROLE` after login.

### TechShop Role Design Example

```
admin_role --- ALL PRIVILEGES
app_role ----- SELECT, INSERT, UPDATE, DELETE (main tables)
analyst_role - SELECT (all)
cs_role ------ SELECT (customers, orders, order_items)
```

---

## Principle of Least Privilege

!!! tip "Principle of Least Privilege"
    Each user should be granted **only the minimum permissions required for their job**.

Why this principle matters:

- **Accident prevention**: Even if an analyst accidentally runs `DELETE FROM customers`, it just errors out if they only have `SELECT`
- **Security hardening**: Even if an account is compromised, the damage scope is limited
- **Audit ease**: It's clear who can perform what actions

### TechShop Scenario

> The CS team needs to look up customer orders. "Should we just give them full access for convenience?" -- Absolutely not.

```sql
-- Bad example: Full permissions
GRANT ALL PRIVILEGES ON techshop.* TO 'ts_cs'@'%';

-- Good example: Read-only on needed tables
GRANT SELECT ON techshop.customers TO 'ts_cs'@'%';
GRANT SELECT ON techshop.orders TO 'ts_cs'@'%';
GRANT SELECT ON techshop.order_items TO 'ts_cs'@'%';
```

The CS team has no reason to access `products`, `suppliers`, `inventory`, etc.

---

## Summary Table

| Command | Description | MySQL | PostgreSQL |
|---------|-------------|-------|------------|
| `CREATE USER` | Create user | `'user'@'host' IDENTIFIED BY 'pw'` | `user WITH PASSWORD 'pw'` |
| `DROP USER` | Delete user | `'user'@'host'` | `user` |
| `GRANT` | Grant permission | `ON db.table TO 'user'@'host'` | `ON table TO user` |
| `REVOKE` | Revoke permission | `ON db.table FROM 'user'@'host'` | `ON table FROM user` |
| `CREATE ROLE` | Create role | 8.0+ supported | Natively supported |
| `GRANT role TO user` | Assign role | `SET DEFAULT ROLE` required | Immediately effective |
| `SHOW GRANTS` | View permissions | `SHOW GRANTS FOR 'user'@'host'` | `\du` or `pg_roles` view |

---

!!! note "Return to Tutorial"
    This appendix is reference material. Since the tutorial uses SQLite, you can proceed through all lessons without DCL practice. Go back to the [Tutorial Introduction](../index.md) to continue learning.
