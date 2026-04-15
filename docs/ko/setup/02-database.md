# 02. 데이터베이스 설치

[01. 데이터베이스 선택](01-choose-db.md)에서 고른 DB를 설치합니다.

!!! success "SQLite를 선택했다면"
    **이 페이지를 건너뛰세요.** SQLite는 Python에 내장되어 있어 별도 설치가 필요 없습니다. → [03. 데이터 생성](03-generate.md)

=== "Docker (추천)"

    ## Docker란?

    **Docker**는 소프트웨어를 **컨테이너**라는 격리된 환경에서 실행하는 도구입니다. 컴퓨터에 MySQL이나 PostgreSQL을 직접 설치하는 대신, Docker가 알아서 필요한 환경을 만들어주고, 필요 없으면 깔끔하게 삭제할 수 있습니다.

    !!! tip "왜 Docker인가?"
        - **한 줄 명령**으로 DB 서버 설치 완료
        - MySQL, PostgreSQL, Oracle, SQL Server를 **동시에** 실행 가능
        - 문제 생기면 컨테이너를 삭제하고 다시 만들면 끝 — 시스템이 오염되지 않음
        - 실무에서도 Docker 기반 개발 환경이 표준

    ---

    ## 1단계: WSL 2 설치 (Windows만 해당)

    !!! info "macOS / Linux 사용자"
        이 단계를 건너뛰고 바로 [2단계: Docker Desktop 설치](#2-docker-desktop)로 이동하세요.

    **WSL (Windows Subsystem for Linux)**은 Windows 안에서 Linux를 실행하는 기능입니다. Docker Desktop이 내부적으로 WSL 2를 사용하므로, Docker를 쓰려면 WSL 2가 먼저 설치되어 있어야 합니다.

    ### WSL 2 설치

    **PowerShell을 관리자 권한으로 실행**하고 다음 명령을 입력합니다:

    ```powershell
    wsl --install
    ```

    이 한 줄로 WSL 2 + **Ubuntu** (기본 배포판)가 자동 설치됩니다. 완료 후 **재부팅**합니다.

    !!! tip "추천 배포판: Ubuntu"
        `wsl --install`은 기본으로 **Ubuntu**를 설치합니다. Ubuntu는 Docker 공식 문서, Stack Overflow, 각종 튜토리얼에서 가장 많이 사용되는 배포판이라, 문제가 생겼을 때 검색으로 해결하기 가장 쉽습니다. 특별한 이유가 없다면 Ubuntu를 그대로 사용하세요.

        다른 배포판을 원한다면:
        ```powershell
        wsl --list --online              # 설치 가능한 배포판 목록
        wsl --install -d Debian          # Debian 설치
        wsl --install -d Ubuntu-24.04    # 특정 Ubuntu 버전
        ```

    ### 재부팅 후 초기 설정

    재부팅하면 Ubuntu 터미널이 자동으로 열리며, **Linux 사용자 이름**과 **비밀번호**를 설정하라고 합니다. 이 계정은 Linux 내부에서만 사용되며, Windows 계정과 별개입니다.

    ```
    Enter new UNIX username: tutorial
    New password: ********
    ```

    ### WSL 2 설치 확인

    PowerShell에서:

    ```powershell
    wsl --list --verbose
    ```

    다음과 비슷한 출력이 나오면 성공입니다:

    ```
      NAME      STATE    VERSION
    * Ubuntu    Running  2
    ```

    `VERSION`이 **2**인지 확인하세요. 만약 1이라면:

    ```powershell
    wsl --set-version Ubuntu 2
    ```

    !!! warning "WSL 설치가 안 되는 경우"
        - **BIOS에서 가상화 활성화**: 재부팅 후 BIOS 설정에서 **Intel VT-x** 또는 **AMD-V**를 켜세요
        - **Windows 버전 확인**: Windows 10 버전 2004 이상 또는 Windows 11 필요
        - **Windows 기능 켜기**: `제어판 > 프로그램 > Windows 기능 켜기/끄기`에서 "Linux용 Windows 하위 시스템"과 "가상 머신 플랫폼" 체크

    ### Ubuntu 설치 후 필수 작업

    Ubuntu 터미널을 열고 (시작 메뉴에서 "Ubuntu" 검색) 다음을 순서대로 실행합니다.

    **1. 시스템 업데이트**

    설치 직후의 패키지는 오래된 버전일 수 있습니다. 반드시 업데이트하세요:

    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

    **2. 기본 도구 설치**

    자주 쓰이는 도구를 미리 설치합니다:

    ```bash
    sudo apt install -y curl wget git unzip
    ```

    **3. Windows Terminal 사용 (강력 추천)**

    Windows 기본 콘솔 대신 **[Windows Terminal](https://aka.ms/terminal)**을 사용하면 Ubuntu, PowerShell, 명령 프롬프트를 탭으로 전환할 수 있습니다. Windows 11에는 기본 설치되어 있고, Windows 10은 Microsoft Store에서 무료로 받을 수 있습니다.

    설치 후 Windows Terminal을 열면 드롭다운에 **Ubuntu**가 자동으로 나타납니다.

    **4. 파일 시스템 접근 방법**

    | 방향 | 경로 | 설명 |
    |------|------|------|
    | WSL → Windows | `/mnt/c/Users/사용자명/` | C: 드라이브가 `/mnt/c`에 마운트 |
    | Windows → WSL | `\\wsl$\Ubuntu\home\사용자명\` | 파일 탐색기 주소창에 입력 |

    ```bash
    # 예: Windows 바탕화면의 파일 확인
    ls /mnt/c/Users/$USER/Desktop/
    ```

    !!! tip "프로젝트 파일 위치"
        이 튜토리얼의 프로젝트 폴더는 **Windows 쪽**에 두는 것을 권장합니다. WSL에서 `/mnt/c/...` 경로로 접근하면 됩니다. WSL 내부(`/home/...`)에 두면 Windows IDE에서 접근이 번거로울 수 있습니다.

    ---

    ## 2단계: Docker Desktop 설치 { #2-docker-desktop }

    ### 다운로드

    [Docker Desktop](https://www.docker.com/products/docker-desktop/) 공식 사이트에서 운영체제에 맞는 버전을 다운로드합니다.

    | OS | 다운로드 |
    |----|---------|
    | Windows | [Docker Desktop for Windows](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe) |
    | macOS (Intel) | [Docker Desktop for Mac (Intel)](https://desktop.docker.com/mac/main/amd64/Docker.dmg) |
    | macOS (Apple Silicon) | [Docker Desktop for Mac (Apple Silicon)](https://desktop.docker.com/mac/main/arm64/Docker.dmg) |
    | Linux | [Docker Desktop for Linux](https://docs.docker.com/desktop/install/linux/) |

    ### Windows 설치 시 참고

    1. 설치 중 **"Use WSL 2 instead of Hyper-V"** 옵션이 체크되어 있는지 확인합니다
    2. 설치 완료 후 **재부팅**이 필요할 수 있습니다
    3. 재부팅 후 Docker Desktop이 자동 시작되며, 시스템 트레이에 고래 아이콘이 나타납니다

    ### 설치 확인

    터미널(명령 프롬프트, PowerShell, 또는 macOS/Linux 터미널)을 열고:

    ```bash
    docker --version
    ```

    `Docker version 27.x.x` 같은 출력이 나오면 성공입니다.

    ```bash
    docker run hello-world
    ```

    `Hello from Docker!` 메시지가 나오면 정상 동작합니다.

    ---

    ## 3단계: 알아두면 좋은 Docker 기본 명령

    이 튜토리얼에서 사용하는 명령만 정리했습니다.

    | 명령 | 설명 | 예시 |
    |------|------|------|
    | `docker run` | 새 컨테이너 생성 + 실행 | `docker run -d --name mysql ...` |
    | `docker ps` | 실행 중인 컨테이너 목록 | `docker ps` |
    | `docker ps -a` | 모든 컨테이너 (중지 포함) | `docker ps -a` |
    | `docker stop` | 컨테이너 중지 | `docker stop mysql` |
    | `docker start` | 중지된 컨테이너 재시작 | `docker start mysql` |
    | `docker rm` | 컨테이너 삭제 | `docker rm mysql` |
    | `docker logs` | 컨테이너 로그 확인 | `docker logs mysql` |

    !!! info "Docker Desktop GUI"
        명령어가 익숙하지 않다면, **Docker Desktop** 앱에서 동일한 작업을 마우스로 할 수 있습니다.

        - **Containers** 탭: 실행 중인 컨테이너 목록, 시작/중지/삭제 버튼
        - **Logs** 탭: 컨테이너의 실시간 로그

    ---

    ## 4단계: 데이터베이스 컨테이너 실행

    선택한 DB의 명령만 실행하세요. 여러 DB를 동시에 실행해도 됩니다.

    ### MySQL

    ```bash
    docker run -d \
      --name mysql \
      -p 3306:3306 \
      -e MYSQL_ROOT_PASSWORD=tutorial \
      -v mysql-data:/var/lib/mysql \
      mysql:8.0
    ```

    접속 확인:

    ```bash
    docker exec -it mysql mysql -u root -ptutorial -e "SELECT VERSION();"
    ```

    | 항목 | 값 |
    |------|-----|
    | 호스트 | `localhost` |
    | 포트 | `3306` |
    | 사용자 | `root` |
    | 비밀번호 | `tutorial` |

    ### MariaDB

    MySQL 대신 MariaDB를 사용하려면 아래 명령을 사용합니다. MySQL과 호환되며, 이 튜토리얼의 MySQL SQL이 그대로 동작합니다.

    !!! warning "MySQL과 동시 실행 불가"
        MySQL과 MariaDB는 같은 포트(3306)를 사용합니다. **둘 중 하나만** 실행하세요. 이미 MySQL 컨테이너를 실행했다면 이 단계를 건너뛰세요.

    ```bash
    docker run -d \
      --name mariadb \
      -p 3306:3306 \
      -e MARIADB_ROOT_PASSWORD=tutorial \
      -v mariadb-data:/var/lib/mysql \
      mariadb:11
    ```

    접속 확인:

    ```bash
    docker exec -it mariadb mariadb -u root -ptutorial -e "SELECT VERSION();"
    ```

    | 항목 | 값 |
    |------|-----|
    | 호스트 | `localhost` |
    | 포트 | `3306` |
    | 사용자 | `root` |
    | 비밀번호 | `tutorial` |

    ### PostgreSQL

    ```bash
    docker run -d \
      --name postgres \
      -p 5432:5432 \
      -e POSTGRES_PASSWORD=tutorial \
      -v postgres-data:/var/lib/postgresql/data \
      postgres:16
    ```

    접속 확인:

    ```bash
    docker exec -it postgres psql -U postgres -c "SELECT version();"
    ```

    | 항목 | 값 |
    |------|-----|
    | 호스트 | `localhost` |
    | 포트 | `5432` |
    | 사용자 | `postgres` |
    | 비밀번호 | `tutorial` |

    ### SQL Server

    ```bash
    docker run -d \
      --name mssql \
      -p 1433:1433 \
      -e ACCEPT_EULA=Y \
      -e MSSQL_SA_PASSWORD=Tutorial1! \
      -v mssql-data:/var/opt/mssql \
      mcr.microsoft.com/mssql/server:2022-latest
    ```

    !!! warning "SQL Server 비밀번호 정책"
        비밀번호는 **8자 이상**, **대문자 + 소문자 + 숫자 + 특수문자** 중 3종류 이상을 포함해야 합니다. 위 예시의 `Tutorial1!`은 이 조건을 만족합니다.

    접속 확인:

    ```bash
    docker exec -it mssql /opt/mssql-tools18/bin/sqlcmd \
      -S localhost -U sa -P "Tutorial1!" -C -Q "SELECT @@VERSION;"
    ```

    | 항목 | 값 |
    |------|-----|
    | 호스트 | `localhost` |
    | 포트 | `1433` |
    | 사용자 | `sa` |
    | 비밀번호 | `Tutorial1!` |

    ### Oracle

    ```bash
    docker run -d \
      --name oracle \
      -p 1521:1521 \
      -e ORACLE_PASSWORD=tutorial \
      -v oracle-data:/opt/oracle/oradata \
      container-registry.oracle.com/database/express:latest
    ```

    !!! note "Oracle 초기화 시간"
        Oracle 컨테이너는 **첫 실행 시 3~5분** 정도 초기화 시간이 필요합니다. `docker logs -f oracle`로 진행 상황을 확인할 수 있으며, `DATABASE IS READY TO USE!` 메시지가 나타나면 사용 가능합니다.

    접속 확인:

    ```bash
    docker exec -it oracle sqlplus system/tutorial@//localhost:1521/XEPDB1
    ```

    `SQL>` 프롬프트가 나타나면 `EXIT`로 나옵니다.

    | 항목 | 값 |
    |------|-----|
    | 호스트 | `localhost` |
    | 포트 | `1521` |
    | 사용자 | `system` |
    | 비밀번호 | `tutorial` |
    | 서비스명 | `XEPDB1` |

    ---

    ## 5단계: 컨테이너 관리

    ### 시작 / 중지

    컴퓨터를 끄거나 Docker Desktop을 종료하면 컨테이너도 중지됩니다. 다시 시작하려면:

    ```bash
    docker start mysql postgres mssql oracle   # 필요한 것만 선택
    ```

    학습이 끝나면 중지:

    ```bash
    docker stop mysql postgres mssql oracle
    ```

    ### 데이터는 유지됩니다

    위 `docker run` 명령에 `-v` 옵션(볼륨)을 넣었기 때문에, 컨테이너를 삭제(`docker rm`)해도 **데이터는 보존**됩니다. 같은 이름으로 다시 만들면 이전 데이터가 그대로 남아있습니다.

    ### 전체 정리

    튜토리얼을 완전히 끝내고 Docker 환경을 깨끗이 지우려면:

    ```bash
    # 컨테이너 중지 + 삭제
    docker stop mysql postgres mssql oracle
    docker rm mysql postgres mssql oracle

    # 데이터 볼륨도 삭제 (되돌릴 수 없음)
    docker volume rm mysql-data postgres-data mssql-data oracle-data
    ```

    ---

    ## 데이터 생성 시 접속 정보

    [03. 데이터 생성](03-generate.md)에서 `--apply` 옵션을 사용할 때 위 표의 접속 정보를 입력합니다. 대화형 모드를 사용하면 단계별로 안내됩니다:

    ```bash
    python -m src.cli.generate
    ```

=== "직접 설치"

    DB 서버를 시스템에 직접 설치하는 방법입니다. Docker보다 설정이 복잡하지만, 이미 설치된 환경이 있거나 Docker를 사용할 수 없는 경우에 사용합니다.

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
        5. **Root Password 설정** - 이 비밀번호는 데이터 생성 시 `--ask-password` 옵션에서 사용합니다. **반드시 기억하세요**

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

    === "macOS"

        ```bash
        brew install mysql
        brew services start mysql
        mysql_secure_installation    # root 비밀번호 설정
        mysql -u root -p             # 접속 확인
        ```

    === "Linux"

        ```bash
        sudo apt update && sudo apt install mysql-server
        sudo systemctl start mysql && sudo systemctl enable mysql
        sudo mysql_secure_installation
        sudo mysql -u root -p
        ```

    ---

    ## PostgreSQL

    === "Windows"

        [postgresql.org](https://www.postgresql.org/download/windows/)에서 **EDB installer**를 다운로드하여 설치합니다. 설치 중 `postgres` 슈퍼유저의 비밀번호를 설정합니다.

        ```
        psql -U postgres    # 접속 확인
        ```

    === "macOS"

        ```bash
        brew install postgresql@16
        brew services start postgresql@16
        psql postgres        # 접속 확인
        ```

    === "Linux"

        ```bash
        sudo apt update && sudo apt install postgresql postgresql-contrib
        sudo systemctl start postgresql && sudo systemctl enable postgresql
        sudo -u postgres psql    # 접속 확인
        ```

    ---

    ## SQL Server

    === "Windows"

        [SQL Server Express](https://www.microsoft.com/ko-kr/sql-server/sql-server-downloads)를 다운로드합니다. Express 에디션은 무료입니다. 설치 후 SQL Server Management Studio (SSMS)도 함께 설치하세요.

    === "Linux"

        [Microsoft 공식 문서](https://learn.microsoft.com/ko-kr/sql/linux/sql-server-linux-setup)를 참고하세요.

    ---

    ## Oracle

    === "Windows"

        [Oracle Database Express Edition (XE)](https://www.oracle.com/database/technologies/xe-downloads.html)를 다운로드합니다. XE는 무료이며 학습용으로 충분합니다.

    === "Linux"

        [Oracle 공식 문서](https://docs.oracle.com/en/database/oracle/oracle-database/23/xeinl/)를 참고하세요.

---

## 설치 문제 해결

!!! warning "자주 발생하는 문제들"

    **포트 충돌**

    다른 프로그램이 같은 포트를 사용하고 있을 수 있습니다:
    ```bash
    # Windows
    netstat -ano | findstr :3306
    netstat -ano | findstr :5432

    # macOS / Linux
    lsof -i :3306
    lsof -i :5432
    ```

    **Docker 컨테이너가 시작되지 않음**

    ```bash
    docker logs 컨테이너이름    # 에러 로그 확인
    docker ps -a               # 상태 확인
    ```

    **Docker Desktop이 시작되지 않음 (Windows)**

    1. Windows 업데이트를 최신으로 유지하세요
    2. BIOS에서 가상화(VT-x/AMD-V)가 활성화되어 있는지 확인하세요
    3. WSL 2가 정상 설치되었는지 확인: `wsl --list --verbose`

[← 01. 데이터베이스 선택](01-choose-db.md){ .md-button }
[03. 데이터 생성 →](03-generate.md){ .md-button .md-button--primary }
