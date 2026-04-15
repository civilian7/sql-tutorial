# 02. Install the Database

Install the DB you chose in [01. Choose a Database](01-choose-db.md).

!!! success "If Using SQLite Only"
    **Skip this page.** SQLite is built into Python, so no separate installation is needed. → [03. Generate Data](03-generate.md)

=== "Docker (Recommended)"

    ## What is Docker?

    **Docker** is a tool that runs software in isolated environments called **containers**. Instead of installing MySQL or PostgreSQL directly on your computer, Docker creates the necessary environment for you, and you can cleanly remove it when you're done.

    !!! tip "Why Docker?"
        - Install a DB server with a **single command**
        - Run MySQL, PostgreSQL, Oracle, and SQL Server **simultaneously**
        - If something goes wrong, delete the container and recreate it - your system stays clean
        - Docker-based development environments are the industry standard

    ---

    ## Step 1: Install WSL 2 (Windows Only)

    !!! info "macOS / Linux Users"
        Skip this step and go directly to [Step 2: Install Docker Desktop](#step-2-install-docker-desktop).

    **WSL (Windows Subsystem for Linux)** lets you run Linux inside Windows. Docker Desktop uses WSL 2 internally, so WSL 2 must be installed before Docker.

    ### Install WSL 2

    Open **PowerShell as Administrator** and run:

    ```powershell
    wsl --install
    ```

    This single command installs WSL 2 + **Ubuntu** (default distro). **Reboot** when complete.

    !!! tip "Recommended Distro: Ubuntu"
        `wsl --install` installs **Ubuntu** by default. Ubuntu is the most widely used distro in Docker docs, Stack Overflow, and tutorials, making it the easiest to troubleshoot. Use Ubuntu unless you have a specific reason not to.

        For a different distro:
        ```powershell
        wsl --list --online              # List available distros
        wsl --install -d Debian          # Install Debian
        wsl --install -d Ubuntu-24.04    # Specific Ubuntu version
        ```

    ### Post-Reboot Setup

    After reboot, an Ubuntu terminal opens automatically, asking you to set a **Linux username** and **password**. This account is only used inside Linux and is separate from your Windows account.

    ```
    Enter new UNIX username: tutorial
    New password: ********
    ```

    ### Verify WSL 2

    In PowerShell:

    ```powershell
    wsl --list --verbose
    ```

    Output like this means success:

    ```
      NAME      STATE    VERSION
    * Ubuntu    Running  2
    ```

    Make sure `VERSION` is **2**. If it shows 1:

    ```powershell
    wsl --set-version Ubuntu 2
    ```

    !!! warning "If WSL Installation Fails"
        - **Enable virtualization in BIOS**: Reboot and enable **Intel VT-x** or **AMD-V** in BIOS settings
        - **Check Windows version**: Windows 10 version 2004+ or Windows 11 required
        - **Enable Windows features**: `Control Panel > Programs > Turn Windows features on or off` - check "Windows Subsystem for Linux" and "Virtual Machine Platform"

    ---

    ## Step 2: Install Docker Desktop { #step-2-install-docker-desktop }

    ### Download

    Download the version for your OS from the [Docker Desktop](https://www.docker.com/products/docker-desktop/) official site.

    | OS | Download |
    |----|---------|
    | Windows | [Docker Desktop for Windows](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe) |
    | macOS (Intel) | [Docker Desktop for Mac (Intel)](https://desktop.docker.com/mac/main/amd64/Docker.dmg) |
    | macOS (Apple Silicon) | [Docker Desktop for Mac (Apple Silicon)](https://desktop.docker.com/mac/main/arm64/Docker.dmg) |
    | Linux | [Docker Desktop for Linux](https://docs.docker.com/desktop/install/linux/) |

    ### Windows Installation Notes

    1. Verify **"Use WSL 2 instead of Hyper-V"** is checked during installation
    2. A **reboot** may be required after installation
    3. After reboot, Docker Desktop starts automatically and a whale icon appears in the system tray

    ### Verify Installation

    Open a terminal (Command Prompt, PowerShell, or macOS/Linux terminal):

    ```bash
    docker --version
    ```

    Output like `Docker version 27.x.x` means success.

    ```bash
    docker run hello-world
    ```

    If you see `Hello from Docker!`, everything is working.

    ---

    ## Step 3: Essential Docker Commands

    Only the commands used in this tutorial:

    | Command | Description | Example |
    |---------|-------------|---------|
    | `docker run` | Create + start a container | `docker run -d --name mysql ...` |
    | `docker ps` | List running containers | `docker ps` |
    | `docker ps -a` | List all containers (including stopped) | `docker ps -a` |
    | `docker stop` | Stop a container | `docker stop mysql` |
    | `docker start` | Restart a stopped container | `docker start mysql` |
    | `docker rm` | Delete a container | `docker rm mysql` |
    | `docker logs` | View container logs | `docker logs mysql` |

    !!! info "Docker Desktop GUI"
        If you're not comfortable with commands, you can do the same things in the **Docker Desktop** app with your mouse.

        - **Containers** tab: List of running containers with start/stop/delete buttons
        - **Logs** tab: Real-time container logs

    ---

    ## Step 4: Run Database Containers

    Run only the commands for your chosen DB. You can run multiple DBs simultaneously.

    ### MySQL

    ```bash
    docker run -d \
      --name mysql \
      -p 3306:3306 \
      -e MYSQL_ROOT_PASSWORD=tutorial \
      -v mysql-data:/var/lib/mysql \
      mysql:8.0
    ```

    Verify:

    ```bash
    docker exec -it mysql mysql -u root -ptutorial -e "SELECT VERSION();"
    ```

    | Setting | Value |
    |---------|-------|
    | Host | `localhost` |
    | Port | `3306` |
    | User | `root` |
    | Password | `tutorial` |

    ### PostgreSQL

    ```bash
    docker run -d \
      --name postgres \
      -p 5432:5432 \
      -e POSTGRES_PASSWORD=tutorial \
      -v postgres-data:/var/lib/postgresql/data \
      postgres:16
    ```

    Verify:

    ```bash
    docker exec -it postgres psql -U postgres -c "SELECT version();"
    ```

    | Setting | Value |
    |---------|-------|
    | Host | `localhost` |
    | Port | `5432` |
    | User | `postgres` |
    | Password | `tutorial` |

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

    !!! warning "SQL Server Password Policy"
        The password must be **at least 8 characters** and include **3 of 4 types**: uppercase, lowercase, numbers, and special characters. The example `Tutorial1!` satisfies this requirement.

    Verify:

    ```bash
    docker exec -it mssql /opt/mssql-tools18/bin/sqlcmd \
      -S localhost -U sa -P "Tutorial1!" -C -Q "SELECT @@VERSION;"
    ```

    | Setting | Value |
    |---------|-------|
    | Host | `localhost` |
    | Port | `1433` |
    | User | `sa` |
    | Password | `Tutorial1!` |

    ### Oracle

    ```bash
    docker run -d \
      --name oracle \
      -p 1521:1521 \
      -e ORACLE_PASSWORD=tutorial \
      -v oracle-data:/opt/oracle/oradata \
      container-registry.oracle.com/database/express:latest
    ```

    !!! note "Oracle Initialization Time"
        The Oracle container needs **3-5 minutes** for first-time initialization. Check progress with `docker logs -f oracle`. When you see `DATABASE IS READY TO USE!`, it's ready.

    Verify:

    ```bash
    docker exec -it oracle sqlplus system/tutorial@//localhost:1521/XEPDB1
    ```

    If the `SQL>` prompt appears, type `EXIT` to quit.

    | Setting | Value |
    |---------|-------|
    | Host | `localhost` |
    | Port | `1521` |
    | User | `system` |
    | Password | `tutorial` |
    | Service | `XEPDB1` |

    ---

    ## Step 5: Managing Containers

    ### Start / Stop

    Containers stop when you shut down your computer or close Docker Desktop. To restart:

    ```bash
    docker start mysql postgres mssql oracle   # choose what you need
    ```

    When done studying:

    ```bash
    docker stop mysql postgres mssql oracle
    ```

    ### Data is Preserved

    The `-v` option (volume) in the `docker run` commands means your **data is preserved** even if you delete the container (`docker rm`). Recreating with the same volume name restores the previous data.

    ### Full Cleanup

    To completely remove the Docker environment after finishing the tutorial:

    ```bash
    # Stop + remove containers
    docker stop mysql postgres mssql oracle
    docker rm mysql postgres mssql oracle

    # Remove data volumes too (cannot be undone)
    docker volume rm mysql-data postgres-data mssql-data oracle-data
    ```

    ---

    ## Connection Info for Data Generation

    Use the connection info from the tables above when running `--apply` in [03. Generate Data](03-generate.md). The interactive mode guides you step by step:

    ```bash
    python -m src.cli.generate
    ```

=== "Native Installation"

    Install DB servers directly on your system. More complex than Docker, but useful if you already have an existing setup or can't use Docker.

    ---

    ## MySQL / MariaDB

    === "Windows"

        Download **mysql-installer-community** (~300MB) from [MySQL Installer](https://dev.mysql.com/downloads/installer/).

        1. Setup Type: **Server only**
        2. **Port**: 3306, **Authentication**: Strong Password
        3. Set **Root Password** - remember this for data generation

        Verify: `mysql -u root -p`

    === "macOS"

        ```bash
        brew install mysql
        brew services start mysql
        mysql_secure_installation    # Set root password
        mysql -u root -p             # Verify
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

        Download the **EDB installer** from [postgresql.org](https://www.postgresql.org/download/windows/). Set the `postgres` superuser password during installation.

        Verify: `psql -U postgres`

    === "macOS"

        ```bash
        brew install postgresql@16
        brew services start postgresql@16
        psql postgres
        ```

    === "Linux"

        ```bash
        sudo apt update && sudo apt install postgresql postgresql-contrib
        sudo systemctl start postgresql && sudo systemctl enable postgresql
        sudo -u postgres psql
        ```

    ---

    ## SQL Server

    === "Windows"

        Download [SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads) (free). Also install SQL Server Management Studio (SSMS).

    === "Linux"

        See the [Microsoft official docs](https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-setup).

    ---

    ## Oracle

    === "Windows"

        Download [Oracle Database Express Edition (XE)](https://www.oracle.com/database/technologies/xe-downloads.html). XE is free and sufficient for learning.

    === "Linux"

        See the [Oracle official docs](https://docs.oracle.com/en/database/oracle/oracle-database/23/xeinl/).

---

## Troubleshooting

!!! warning "Common Issues"

    **Port Conflict**

    Another program may be using the same port:
    ```bash
    # Windows
    netstat -ano | findstr :3306
    netstat -ano | findstr :5432

    # macOS / Linux
    lsof -i :3306
    lsof -i :5432
    ```

    **Docker Container Won't Start**

    ```bash
    docker logs container_name    # Check error logs
    docker ps -a                  # Check status
    ```

    **Docker Desktop Won't Start (Windows)**

    1. Keep Windows updated
    2. Verify virtualization (VT-x/AMD-V) is enabled in BIOS
    3. Check WSL 2 is properly installed: `wsl --list --verbose`

[← 01. Choose a Database](01-choose-db.md){ .md-button }
[03. Generate Data →](03-generate.md){ .md-button .md-button--primary }
