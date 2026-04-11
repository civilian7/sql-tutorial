# Schema Inspection Queries

=== "SQLite"
    ```sql
    -- All tables with DDL
    SELECT name, sql FROM sqlite_master
    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
    ORDER BY name;

    -- All views
    SELECT name FROM sqlite_master WHERE type = 'view' ORDER BY name;

    -- Column info for a specific table
    PRAGMA table_info('orders');

    -- All indexes
    SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' ORDER BY tbl_name;

    -- All triggers
    SELECT name, tbl_name FROM sqlite_master WHERE type = 'trigger' ORDER BY name;
    ```

=== "MySQL"
    ```sql
    -- All tables
    SHOW TABLES;

    -- All views
    SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS
    WHERE TABLE_SCHEMA = DATABASE();

    -- Column info for a specific table
    DESCRIBE orders;

    -- All indexes
    SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    ORDER BY TABLE_NAME, INDEX_NAME;

    -- All triggers
    SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE, EVENT_MANIPULATION
    FROM INFORMATION_SCHEMA.TRIGGERS
    WHERE TRIGGER_SCHEMA = DATABASE();
    ```

=== "PostgreSQL"
    ```sql
    -- All tables
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public' ORDER BY tablename;

    -- All views
    SELECT viewname FROM pg_views
    WHERE schemaname = 'public' ORDER BY viewname;

    -- Column info for a specific table
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'orders' ORDER BY ordinal_position;

    -- All indexes
    SELECT indexname, tablename FROM pg_indexes
    WHERE schemaname = 'public' ORDER BY tablename;

    -- All triggers
    SELECT tgname, relname
    FROM pg_trigger t JOIN pg_class c ON t.tgrelid = c.oid
    WHERE NOT t.tgisinternal ORDER BY tgname;
    ```
