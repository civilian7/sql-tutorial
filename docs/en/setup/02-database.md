# 02. Install the Database

Install the DB you chose in [01. Choose a Database](01-choose-db.md).

!!! success "If Using SQLite Only"
    **Skip this page.** SQLite is built into Python, so no separate installation is needed. → [03. Generate Data](03-generate.md)

---

## MySQL / MariaDB

=== "Windows"

    ### 1. Download

    Download **mysql-installer-community** (~300MB) from [MySQL Installer](https://dev.mysql.com/downloads/installer/).

    !!! tip "Download Without Oracle Account"
        Click the **"No thanks, just start my download"** link at the bottom of the download page to download without logging in.

    ### 2. Install

    1. Setup Type: Select **Server only** (Workbench etc. can be installed separately later)
    2. **Config Type**: Development Computer (keep default)
    3. **Port**: 3306 (keep default)
    4. **Authentication**: Use Strong Password Encryption (keep default)
    5. **Root Password** — This password is used with the `--ask-password` option during data generation. **Make sure to remember it**

    ### 3. Verify Installation

    Open **Command Prompt**:

    ```
    mysql --version
    ```

    If the version is displayed, installation was successful. Also verify the connection:

    ```
    mysql -u root -p
    ```

    If the `mysql>` prompt appears after entering the password, everything is working. Type `exit` to quit.

    !!! warning "If `mysql` Cannot Be Found"
        MySQL is not in PATH. Add the following path to your system PATH environment variable:
        ```
        C:\Program Files\MySQL\MySQL Server 8.0\bin
        ```

    !!! info "To Use MariaDB Instead"
        Download the MSI package from [mariadb.org](https://mariadb.org/download/). It's compatible with MySQL, and this tutorial's MySQL SQL runs as-is on MariaDB. The installation process is nearly identical to MySQL.

=== "macOS"

    ### 1. Check Homebrew

    ```bash
    brew --version
    ```

    If Homebrew is not installed, install it first:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

    ### 2. Install and Start

    ```bash
    brew install mysql
    brew services start mysql
    ```

    ### 3. Security Setup

    Set the root password:

    ```bash
    mysql_secure_installation
    ```

    Follow the prompts to set a root password. Answer `Y` to the remaining questions.

    ### 4. Verify Connection

    ```bash
    mysql -u root -p
    ```

    If the `mysql>` prompt appears after entering the password, everything is working.

=== "Linux (Ubuntu/Debian)"

    ### 1. Install

    ```bash
    sudo apt update
    sudo apt install mysql-server
    ```

    ### 2. Start Service

    ```bash
    sudo systemctl start mysql
    sudo systemctl enable mysql   # Auto-start on boot
    ```

    ### 3. Security Setup

    ```bash
    sudo mysql_secure_installation
    ```

    Set a root password and answer `Y` to the remaining questions.

    ### 4. Verify Connection

    ```bash
    sudo mysql -u root -p
    ```

    If the `mysql>` prompt appears, everything is working.

---

## PostgreSQL

=== "Windows"

    ### 1. Download

    Download the **EDB installer** from [postgresql.org](https://www.postgresql.org/download/windows/).

    ### 2. Install

    1. Installation directory: Keep default
    2. **Component selection**: Check both PostgreSQL Server and pgAdmin 4
    3. **Data directory**: Keep default
    4. **Password** — This is the password for the `postgres` superuser. **Make sure to remember it**
    5. **Port**: 5432 (keep default)
    6. **Locale**: Korean, Korea or Default locale

    ### 3. Verify Installation

    Open **Command Prompt**:

    ```
    psql --version
    ```

    Verify the connection:

    ```
    psql -U postgres
    ```

    If the `postgres=#` prompt appears after entering the password, everything is working. Type `\q` to quit.

    !!! warning "If `psql` Cannot Be Found"
        Add the following path to your system PATH environment variable:
        ```
        C:\Program Files\PostgreSQL\16\bin
        ```

=== "macOS"

    ### 1. Check Homebrew

    ```bash
    brew --version
    ```

    If not installed: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

    ### 2. Install and Start

    ```bash
    brew install postgresql@16
    brew services start postgresql@16
    ```

    ### 3. Verify Connection

    ```bash
    psql postgres
    ```

    If the `postgres=#` prompt appears, everything is working. On macOS, connection without a password is the default.

=== "Linux (Ubuntu/Debian)"

    ### 1. Install

    ```bash
    sudo apt update
    sudo apt install postgresql postgresql-contrib
    ```

    ### 2. Start Service

    ```bash
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    ```

    ### 3. Verify Connection

    ```bash
    sudo -u postgres psql
    ```

    If the `postgres=#` prompt appears, everything is working. Type `\q` to quit.

    ### 4. Set Password (Optional)

    ```bash
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_password';"
    ```

---

## Troubleshooting

!!! warning "Common Issues"

    **Port Conflict**

    MySQL (3306) or PostgreSQL (5432) ports may already be in use:
    ```bash
    # Windows
    netstat -ano | findstr :3306
    netstat -ano | findstr :5432

    # macOS / Linux
    lsof -i :3306
    lsof -i :5432
    ```

    **Service Won't Start**

    ```bash
    # MySQL
    sudo systemctl status mysql

    # PostgreSQL
    sudo systemctl status postgresql
    ```

    **Permission Issues (Linux)**

    Forgetting `sudo` will cause permission errors. Most DB commands require `sudo`.

[← 01. Choose a Database](01-choose-db.md){ .md-button }
[03. Generate Data →](03-generate.md){ .md-button .md-button--primary }
