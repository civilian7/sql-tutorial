# DBA 기초 — 데이터베이스 유지보수

데이터베이스는 사용하면서 점점 느려질 수 있습니다. 삭제된 행이 디스크 공간을 차지하고, 통계가 오래되면 옵티마이저가 비효율적인 실행 계획을 선택합니다. 정기적인 유지보수로 성능을 유지하는 방법을 알아봅니다.

---

## VACUUM — 디스크 공간 회수

`DELETE`로 행을 지워도 대부분의 데이터베이스는 디스크 공간을 즉시 반환하지 않습니다. 삭제된 영역은 "빈 페이지"로 남아 파일 크기가 줄지 않습니다. `VACUUM`은 이 빈 공간을 회수하여 파일을 압축합니다.

=== "SQLite"

    ```sql
    -- 삭제된 공간 회수 (전체 DB 재작성)
    VACUUM;

    -- 자동 VACUUM 활성화 (DB 생성 시 설정)
    PRAGMA auto_vacuum = FULL;
    ```

    !!! warning "주의"
        `VACUUM`은 전체 데이터베이스를 새 파일로 복사합니다. 대용량 DB에서는 시간이 걸리고, 실행 중 DB 크기의 2배 디스크 공간이 필요합니다.

=== "MySQL"

    ```sql
    -- InnoDB 테이블 최적화 (공간 회수 + 인덱스 재구축)
    OPTIMIZE TABLE orders;

    -- 여러 테이블 동시에
    OPTIMIZE TABLE orders, order_items, payments;
    ```

    InnoDB는 `OPTIMIZE TABLE` 실행 시 내부적으로 테이블을 재생성합니다. 운영 중에는 테이블 락이 발생하므로 비수기에 실행하세요.

=== "PostgreSQL"

    ```sql
    -- 일반 VACUUM (삭제된 튜플 정리, 테이블 락 없음)
    VACUUM orders;

    -- VACUUM FULL (디스크 공간 회수, 배타적 락 필요)
    VACUUM FULL orders;

    -- 통계 갱신과 동시 실행
    VACUUM ANALYZE orders;
    ```

    PostgreSQL은 **autovacuum** 데몬이 기본 활성화되어 있어 대부분 수동 실행이 불필요합니다. `VACUUM FULL`은 테이블을 완전히 재작성하므로 배타적 락이 걸립니다.

---

## ANALYZE — 통계 갱신

쿼리 옵티마이저는 **테이블 통계**(행 수, 값 분포, 인덱스 선택도 등)를 기반으로 실행 계획을 결정합니다. 대량 INSERT/DELETE 후 통계가 오래되면 옵티마이저가 잘못된 계획을 선택할 수 있습니다.

=== "SQLite"

    ```sql
    -- 전체 DB 통계 갱신
    ANALYZE;

    -- 특정 테이블만
    ANALYZE orders;
    ```

    SQLite는 `sqlite_stat1` 테이블에 통계를 저장합니다. `ANALYZE` 실행 후 쿼리 플래너가 더 나은 인덱스를 선택하게 됩니다.

=== "MySQL"

    ```sql
    -- 테이블 통계 갱신
    ANALYZE TABLE orders;

    -- 여러 테이블
    ANALYZE TABLE orders, order_items, products;
    ```

=== "PostgreSQL"

    ```sql
    -- 특정 테이블 통계 갱신
    ANALYZE orders;

    -- 전체 DB
    ANALYZE;
    ```

    PostgreSQL은 autovacuum이 자동으로 `ANALYZE`도 수행합니다. 대량 데이터 변경 직후에는 수동 실행이 유용합니다.

---

## REINDEX — 인덱스 재구축

인덱스는 시간이 지나면서 단편화(fragmentation)될 수 있습니다. 대량 삭제/업데이트 후 인덱스 페이지에 빈 공간이 많아지면 성능이 저하됩니다.

=== "SQLite"

    ```sql
    -- 전체 DB 인덱스 재구축
    REINDEX;

    -- 특정 테이블의 인덱스만
    REINDEX orders;

    -- 특정 인덱스만
    REINDEX idx_orders_customer_id;
    ```

=== "MySQL"

    ```sql
    -- InnoDB는 REINDEX 명령이 없음 → ALTER TABLE로 대체
    ALTER TABLE orders FORCE;

    -- 또는 OPTIMIZE TABLE (인덱스 재구축 포함)
    OPTIMIZE TABLE orders;
    ```

=== "PostgreSQL"

    ```sql
    -- 특정 인덱스 재구축
    REINDEX INDEX idx_orders_customer_id;

    -- 테이블의 모든 인덱스
    REINDEX TABLE orders;

    -- 전체 DB (관리자 권한 필요)
    REINDEX DATABASE mydb;

    -- 운영 중 무중단 재구축 (PostgreSQL 12+)
    REINDEX INDEX CONCURRENTLY idx_orders_customer_id;
    ```

---

## 백업과 복원

데이터베이스 백업은 가장 중요한 유지보수 작업입니다. 정기 백업 없이 운영하는 것은 안전벨트 없이 운전하는 것과 같습니다.

=== "SQLite"

    ```bash
    # 방법 1: .backup 명령 (권장 — 실행 중에도 안전)
    sqlite3 ecommerce-ko.db ".backup backup_20260411.db"

    # 방법 2: 파일 복사 (DB가 쓰기 중이 아닐 때만 안전)
    cp ecommerce-ko.db ecommerce_backup.db

    # 복원: 백업 파일을 원본 위치에 복사
    cp backup_20260411.db ecommerce-ko.db
    ```

=== "MySQL"

    ```bash
    # 전체 DB 백업
    mysqldump -u root -p ecommerce > backup_20260411.sql

    # 특정 테이블만
    mysqldump -u root -p ecommerce orders order_items > orders_backup.sql

    # 구조만 (데이터 제외)
    mysqldump -u root -p --no-data ecommerce > schema_only.sql

    # 복원
    mysql -u root -p ecommerce < backup_20260411.sql
    ```

=== "PostgreSQL"

    ```bash
    # 커스텀 포맷 백업 (압축, 선택적 복원 가능)
    pg_dump -Fc ecommerce > backup_20260411.dump

    # SQL 텍스트 백업
    pg_dump ecommerce > backup_20260411.sql

    # 복원 (커스텀 포맷)
    pg_restore -d ecommerce backup_20260411.dump

    # 복원 (SQL 텍스트)
    psql ecommerce < backup_20260411.sql
    ```

!!! tip "백업 규칙"
    - 백업은 **다른 물리적 장소**에 보관하세요 (같은 디스크는 의미 없음)
    - 정기적으로 **복원 테스트**를 하세요 (복원되지 않는 백업은 백업이 아닙니다)
    - 백업 파일명에 **날짜를 포함**하세요

---

## 모니터링 기초

문제가 발생하기 전에 미리 감지하는 것이 유지보수의 핵심입니다.

### 느린 쿼리 찾기

=== "MySQL"

    ```ini
    # my.cnf에서 슬로우 쿼리 로그 활성화
    slow_query_log = 1
    slow_query_log_file = /var/log/mysql/slow.log
    long_query_time = 1    # 1초 이상 걸리는 쿼리 기록
    ```

    ```sql
    -- 실행 중인 쿼리 확인
    SHOW PROCESSLIST;

    -- 테이블 상태 확인
    SHOW TABLE STATUS FROM ecommerce;
    ```

=== "PostgreSQL"

    ```sql
    -- pg_stat_statements 확장 활성화 (postgresql.conf)
    -- shared_preload_libraries = 'pg_stat_statements'

    -- 가장 느린 쿼리 TOP 10
    SELECT query, calls, mean_exec_time, total_exec_time
    FROM pg_stat_statements
    ORDER BY mean_exec_time DESC
    LIMIT 10;

    -- 테이블별 순차 스캔 횟수 (인덱스 필요 여부 판단)
    SELECT relname, seq_scan, idx_scan
    FROM pg_stat_user_tables
    ORDER BY seq_scan DESC;
    ```

=== "SQLite"

    SQLite는 내장 모니터링 도구가 없지만, 앱에서 쿼리 실행 시간을 측정할 수 있습니다.

    ```sql
    -- 실행 계획으로 비효율적 쿼리 탐지
    EXPLAIN QUERY PLAN
    SELECT * FROM orders WHERE customer_id = 100;
    -- "SCAN" → 인덱스 없음, "SEARCH" → 인덱스 사용
    ```

### 주요 모니터링 지표

| 지표 | 정상 범위 | 조치 |
|------|----------|------|
| 디스크 사용량 | 80% 미만 | 공간 확보 또는 디스크 추가 |
| 느린 쿼리 수 | 일정 수준 유지 | 인덱스 추가 또는 쿼리 최적화 |
| 연결 수 | 최대치의 70% 미만 | 커넥션 풀 설정 조정 |
| 캐시 적중률 | 90% 이상 | 메모리(버퍼 풀) 증설 |

---

## 정리 표

| 작업 | SQLite | MySQL | PostgreSQL |
|------|--------|-------|------------|
| 공간 회수 | `VACUUM` | `OPTIMIZE TABLE t` | `VACUUM FULL t` |
| 통계 갱신 | `ANALYZE` | `ANALYZE TABLE t` | `ANALYZE t` |
| 인덱스 재구축 | `REINDEX` | `ALTER TABLE t FORCE` | `REINDEX TABLE t` |
| 백업 | `.backup` / 파일 복사 | `mysqldump` | `pg_dump` |
| 복원 | 파일 복사 | `mysql < dump.sql` | `pg_restore` |
| 느린 쿼리 | `EXPLAIN QUERY PLAN` | slow query log | `pg_stat_statements` |
| 자동 유지보수 | 없음 | 이벤트 스케줄러 | autovacuum |

!!! note "유지보수 주기 가이드"
    - **매일**: 백업, 모니터링 지표 확인
    - **매주**: 느린 쿼리 로그 검토
    - **매월**: `ANALYZE` (통계 갱신), 디스크 사용량 점검
    - **분기별**: `REINDEX` / `VACUUM FULL` (필요 시)
