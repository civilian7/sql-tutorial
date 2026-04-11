# DBA Basics -- Database Maintenance

Databases can gradually slow down with use. Deleted rows still occupy disk space, and outdated statistics cause the optimizer to choose inefficient execution plans. Learn how to maintain performance through regular maintenance.

---

## VACUUM -- Reclaiming Disk Space

Even after deleting rows with `DELETE`, most databases don't immediately return disk space. Deleted areas remain as "empty pages" and the file size doesn't shrink. `VACUUM` reclaims this empty space and compacts the file.

=== "SQLite"

    ```sql
    -- Reclaim deleted space (rewrites entire DB)
    VACUUM;

    -- Enable auto VACUUM (set at DB creation time)
    PRAGMA auto_vacuum = FULL;
    ```

    !!! warning "Caution"
        `VACUUM` copies the entire database to a new file. For large databases, this takes time and requires 2x the DB size in disk space during execution.

=== "MySQL"

    ```sql
    -- Optimize InnoDB table (reclaim space + rebuild indexes)
    OPTIMIZE TABLE orders;

    -- Multiple tables at once
    OPTIMIZE TABLE orders, order_items, payments;
    ```

    InnoDB internally recreates the table when `OPTIMIZE TABLE` is executed. This causes table locks during operation, so run during off-peak hours.

=== "PostgreSQL"

    ```sql
    -- Regular VACUUM (clean up dead tuples, no table lock)
    VACUUM orders;

    -- VACUUM FULL (reclaim disk space, requires exclusive lock)
    VACUUM FULL orders;

    -- Run with statistics update simultaneously
    VACUUM ANALYZE orders;
    ```

    PostgreSQL has the **autovacuum** daemon enabled by default, so manual execution is usually unnecessary. `VACUUM FULL` completely rewrites the table and requires an exclusive lock.

---

## ANALYZE -- Updating Statistics

The query optimizer determines execution plans based on **table statistics** (row counts, value distribution, index selectivity, etc.). After bulk INSERTs/DELETEs, outdated statistics can cause the optimizer to choose suboptimal plans.

=== "SQLite"

    ```sql
    -- Update statistics for entire DB
    ANALYZE;

    -- Specific table only
    ANALYZE orders;
    ```

    SQLite stores statistics in the `sqlite_stat1` table. After running `ANALYZE`, the query planner selects better indexes.

=== "MySQL"

    ```sql
    -- Update table statistics
    ANALYZE TABLE orders;

    -- Multiple tables
    ANALYZE TABLE orders, order_items, products;
    ```

=== "PostgreSQL"

    ```sql
    -- Update statistics for specific table
    ANALYZE orders;

    -- Entire DB
    ANALYZE;
    ```

    PostgreSQL's autovacuum automatically performs `ANALYZE` as well. Manual execution is useful immediately after bulk data changes.

---

## REINDEX -- Rebuilding Indexes

Indexes can become fragmented over time. After bulk deletes/updates, index pages may have excessive empty space, degrading performance.

=== "SQLite"

    ```sql
    -- Rebuild all indexes in the DB
    REINDEX;

    -- Specific table's indexes only
    REINDEX orders;

    -- Specific index only
    REINDEX idx_orders_customer_id;
    ```

=== "MySQL"

    ```sql
    -- InnoDB has no REINDEX command -> use ALTER TABLE instead
    ALTER TABLE orders FORCE;

    -- Or OPTIMIZE TABLE (includes index rebuild)
    OPTIMIZE TABLE orders;
    ```

=== "PostgreSQL"

    ```sql
    -- Rebuild specific index
    REINDEX INDEX idx_orders_customer_id;

    -- All indexes on a table
    REINDEX TABLE orders;

    -- Entire DB (requires admin privileges)
    REINDEX DATABASE mydb;

    -- Non-blocking rebuild during operation (PostgreSQL 12+)
    REINDEX INDEX CONCURRENTLY idx_orders_customer_id;
    ```

---

## Backup and Restore

Database backup is the most important maintenance task. Operating without regular backups is like driving without a seatbelt.

=== "SQLite"

    ```bash
    # Method 1: .backup command (recommended -- safe even while running)
    sqlite3 ecommerce-ko.db ".backup backup_20260411.db"

    # Method 2: File copy (safe only when DB is not being written to)
    cp ecommerce-ko.db ecommerce_backup.db

    # Restore: Copy backup file to original location
    cp backup_20260411.db ecommerce-ko.db
    ```

=== "MySQL"

    ```bash
    # Full DB backup
    mysqldump -u root -p ecommerce > backup_20260411.sql

    # Specific tables only
    mysqldump -u root -p ecommerce orders order_items > orders_backup.sql

    # Schema only (no data)
    mysqldump -u root -p --no-data ecommerce > schema_only.sql

    # Restore
    mysql -u root -p ecommerce < backup_20260411.sql
    ```

=== "PostgreSQL"

    ```bash
    # Custom format backup (compressed, selective restore possible)
    pg_dump -Fc ecommerce > backup_20260411.dump

    # SQL text backup
    pg_dump ecommerce > backup_20260411.sql

    # Restore (custom format)
    pg_restore -d ecommerce backup_20260411.dump

    # Restore (SQL text)
    psql ecommerce < backup_20260411.sql
    ```

!!! tip "Backup Rules"
    - Store backups in a **different physical location** (same disk is meaningless)
    - Regularly perform **restore tests** (a backup that can't be restored isn't a backup)
    - Include the **date in backup filenames**

---

## Monitoring Basics

Detecting problems before they occur is the essence of maintenance.

### Finding Slow Queries

=== "MySQL"

    ```ini
    # Enable slow query log in my.cnf
    slow_query_log = 1
    slow_query_log_file = /var/log/mysql/slow.log
    long_query_time = 1    # Log queries taking over 1 second
    ```

    ```sql
    -- Check running queries
    SHOW PROCESSLIST;

    -- Check table status
    SHOW TABLE STATUS FROM ecommerce;
    ```

=== "PostgreSQL"

    ```sql
    -- Enable pg_stat_statements extension (postgresql.conf)
    -- shared_preload_libraries = 'pg_stat_statements'

    -- Top 10 slowest queries
    SELECT query, calls, mean_exec_time, total_exec_time
    FROM pg_stat_statements
    ORDER BY mean_exec_time DESC
    LIMIT 10;

    -- Sequential scan count per table (determine if index is needed)
    SELECT relname, seq_scan, idx_scan
    FROM pg_stat_user_tables
    ORDER BY seq_scan DESC;
    ```

=== "SQLite"

    SQLite has no built-in monitoring tools, but you can measure query execution time in your application.

    ```sql
    -- Detect inefficient queries with execution plan
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 100;
    -- "SCAN" -> no index, "SEARCH" -> index used
    ```

### Key Monitoring Metrics

| Metric | Normal Range | Action |
|--------|-------------|--------|
| Disk usage | Under 80% | Free space or add disk |
| Slow query count | Steady level | Add indexes or optimize queries |
| Connection count | Under 70% of max | Adjust connection pool settings |
| Cache hit ratio | Over 90% | Increase memory (buffer pool) |

---

## Summary Table

| Task | SQLite | MySQL | PostgreSQL |
|------|--------|-------|------------|
| Reclaim space | `VACUUM` | `OPTIMIZE TABLE t` | `VACUUM FULL t` |
| Update statistics | `ANALYZE` | `ANALYZE TABLE t` | `ANALYZE t` |
| Rebuild indexes | `REINDEX` | `ALTER TABLE t FORCE` | `REINDEX TABLE t` |
| Backup | `.backup` / file copy | `mysqldump` | `pg_dump` |
| Restore | File copy | `mysql < dump.sql` | `pg_restore` |
| Slow queries | `EXPLAIN QUERY PLAN` | slow query log | `pg_stat_statements` |
| Auto maintenance | None | Event scheduler | autovacuum |

!!! note "Maintenance Schedule Guide"
    - **Daily**: Backup, check monitoring metrics
    - **Weekly**: Review slow query logs
    - **Monthly**: `ANALYZE` (update statistics), check disk usage
    - **Quarterly**: `REINDEX` / `VACUUM FULL` (as needed)
