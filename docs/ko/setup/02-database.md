# 02. 데이터베이스 설치

[01. 데이터베이스 선택](01-choose-db.md)에서 고른 DB를 설치합니다.

!!! success "SQLite를 선택했다면"
    **이 페이지를 건너뛰세요.** SQLite는 Python에 내장되어 있어 별도 설치가 필요 없습니다. → [03. 데이터 생성](03-generate.md)

---

## MySQL / MariaDB

=== "Windows"

    ### 1. 다운로드

    [MySQL Installer](https://dev.mysql.com/downloads/installer/)에서 **mysql-installer-community** (약 300MB)를 다운로드합니다.

    !!! tip "Oracle 계정 없이 다운로드"
        다운로드 페이지 하단의 **"No thanks, just start my download"** 링크를 클릭하면 로그인 없이 받을 수 있습니다.

    ### 2. 설치

    1. 설치 유형: **Server only** 선택 (Workbench 등은 나중에 별도 설치 가능)
    2. **Config Type**: Development Computer (기본값 유지)
    3. **Port**: 3306 (기본값 유지)
    4. **Authentication**: Use Strong Password Encryption (기본값 유지)
    5. **Root Password 설정** — 이 비밀번호는 데이터 생성 시 `--ask-password` 옵션에서 사용합니다. **반드시 기억하세요**

    ### 3. 설치 확인

    **명령 프롬프트**를 열고:

    ```
    mysql --version
    ```

    버전이 출력되면 설치 성공입니다. 접속도 확인합니다:

    ```
    mysql -u root -p
    ```

    비밀번호 입력 후 `mysql>` 프롬프트가 나타나면 정상입니다. `exit`로 나옵니다.

    !!! warning "`mysql`을 찾을 수 없다면"
        MySQL이 PATH에 등록되지 않은 것입니다. 다음 경로를 시스템 환경 변수 PATH에 추가하세요:
        ```
        C:\Program Files\MySQL\MySQL Server 8.0\bin
        ```

    !!! info "MariaDB를 사용하려면"
        [mariadb.org](https://mariadb.org/download/)에서 MSI 패키지를 다운로드합니다. MySQL과 호환되며, 이 튜토리얼의 MySQL SQL이 그대로 동작합니다. 설치 과정은 MySQL과 거의 동일합니다.

=== "macOS"

    ### 1. Homebrew 확인

    ```bash
    brew --version
    ```

    Homebrew가 없으면 먼저 설치합니다:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

    ### 2. 설치 및 시작

    ```bash
    brew install mysql
    brew services start mysql
    ```

    ### 3. 보안 설정

    root 비밀번호를 설정합니다:

    ```bash
    mysql_secure_installation
    ```

    안내에 따라 root 비밀번호를 설정하세요. 나머지 질문은 모두 `Y`로 답하면 됩니다.

    ### 4. 접속 확인

    ```bash
    mysql -u root -p
    ```

    비밀번호 입력 후 `mysql>` 프롬프트가 나타나면 정상입니다.

=== "Linux (Ubuntu/Debian)"

    ### 1. 설치

    ```bash
    sudo apt update
    sudo apt install mysql-server
    ```

    ### 2. 서비스 시작

    ```bash
    sudo systemctl start mysql
    sudo systemctl enable mysql   # 부팅 시 자동 시작
    ```

    ### 3. 보안 설정

    ```bash
    sudo mysql_secure_installation
    ```

    root 비밀번호를 설정하고 나머지 질문은 `Y`로 답합니다.

    ### 4. 접속 확인

    ```bash
    sudo mysql -u root -p
    ```

    `mysql>` 프롬프트가 나타나면 정상입니다.

---

## PostgreSQL

=== "Windows"

    ### 1. 다운로드

    [postgresql.org](https://www.postgresql.org/download/windows/)에서 **EDB installer**를 다운로드합니다.

    ### 2. 설치

    1. 설치 디렉토리: 기본값 유지
    2. **컴포넌트 선택**: PostgreSQL Server, pgAdmin 4 모두 체크
    3. **데이터 디렉토리**: 기본값 유지
    4. **Password 설정** — `postgres` 슈퍼유저의 비밀번호입니다. **반드시 기억하세요**
    5. **Port**: 5432 (기본값 유지)
    6. **Locale**: Korean, Korea 또는 Default locale

    ### 3. 설치 확인

    **명령 프롬프트**를 열고:

    ```
    psql --version
    ```

    접속 확인:

    ```
    psql -U postgres
    ```

    비밀번호 입력 후 `postgres=#` 프롬프트가 나타나면 정상입니다. `\q`로 나옵니다.

    !!! warning "`psql`을 찾을 수 없다면"
        다음 경로를 시스템 환경 변수 PATH에 추가하세요:
        ```
        C:\Program Files\PostgreSQL\16\bin
        ```

=== "macOS"

    ### 1. Homebrew 확인

    ```bash
    brew --version
    ```

    없으면: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

    ### 2. 설치 및 시작

    ```bash
    brew install postgresql@16
    brew services start postgresql@16
    ```

    ### 3. 접속 확인

    ```bash
    psql postgres
    ```

    `postgres=#` 프롬프트가 나타나면 정상입니다. macOS에서는 기본적으로 비밀번호 없이 접속됩니다.

=== "Linux (Ubuntu/Debian)"

    ### 1. 설치

    ```bash
    sudo apt update
    sudo apt install postgresql postgresql-contrib
    ```

    ### 2. 서비스 시작

    ```bash
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    ```

    ### 3. 접속 확인

    ```bash
    sudo -u postgres psql
    ```

    `postgres=#` 프롬프트가 나타나면 정상입니다. `\q`로 나옵니다.

    ### 4. 비밀번호 설정 (선택)

    ```bash
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD '비밀번호';"
    ```

---

## 설치 문제 해결

!!! warning "자주 발생하는 문제들"

    **포트 충돌**

    MySQL(3306)이나 PostgreSQL(5432) 포트가 이미 사용 중일 수 있습니다:
    ```bash
    # Windows
    netstat -ano | findstr :3306
    netstat -ano | findstr :5432

    # macOS / Linux
    lsof -i :3306
    lsof -i :5432
    ```

    **서비스가 시작되지 않음**

    ```bash
    # MySQL
    sudo systemctl status mysql

    # PostgreSQL
    sudo systemctl status postgresql
    ```

    **권한 문제 (Linux)**

    `sudo`를 빼먹으면 권한 오류가 발생합니다. DB 명령은 대부분 `sudo`가 필요합니다.

[← 01. 데이터베이스 선택](01-choose-db.md){ .md-button }
[03. 데이터 생성 →](03-generate.md){ .md-button .md-button--primary }
