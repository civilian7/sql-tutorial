# 03. Generate Data

The data generator is written in Python. Install Python and run the generator to create the learning database.

## Install Python

Python **3.10 or higher** is required, with **Python 3.14** as the recommended version (used for development and testing of this tutorial).

**Check if it's already installed:**

=== "Windows"

    In Command Prompt:
    ```
    python --version
    ```

=== "macOS / Linux"

    In Terminal:
    ```bash
    python3 --version
    ```

If `Python 3.10.x` or higher is displayed, skip to [Install Dependencies](#install-dependencies).

---

### How to Install Python

=== "Windows"

    #### 1. Download

    Click the **Download Python 3.x.x** button at [python.org/downloads](https://www.python.org/downloads/). The 64-bit Windows version is automatically selected.

    #### 2. Install

    !!! warning "Most Important Step"
        You **must** check the **"Add python.exe to PATH"** checkbox at the bottom of the first installation screen. If you miss this, the `python` command won't work in the terminal.

    Click **Install Now** to proceed. If **"Disable path length limit"** appears on the completion screen, click it (prevents long path issues).

    #### 3. Verify Installation

    Open **Command Prompt**:

    !!! info "How to Open Command Prompt"
        - Search for `cmd` in the Start menu, or
        - ++win+r++ → type `cmd` → ++enter++

    ```
    python --version
    ```

    If `Python 3.12.x` or similar is displayed, the installation was successful.

    !!! warning "If `python` Cannot Be Found"
        - You may have missed "Add to PATH" during installation. **Uninstall and reinstall** Python, making sure to check the checkbox.
        - Or try `py --version`. If the Windows Python Launcher is installed, you can also run with the `py` command. In this case, use `py` instead of `python` in subsequent commands.

=== "macOS"

    #### 1. Check Homebrew

    ```bash
    brew --version
    ```

    If not installed, install it first:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

    #### 2. Install Python

    ```bash
    brew install python@3.12
    ```

    #### 3. Verify Installation

    ```bash
    python3 --version
    ```

    !!! info "Use `python3`"
        On macOS, use `python3` instead of `python`. Also use `pip3` instead of `pip` in subsequent commands.

=== "Linux (Ubuntu/Debian)"

    #### 1. Install

    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv
    ```

    #### 2. Verify Installation

    ```bash
    python3 --version
    ```

    !!! info "Use `python3`"
        On Linux, use `python3` instead of `python`.

---

## Command Line Basics { #cli-basics }

From this step onward, you'll enter commands in a **terminal** (or Command Prompt). Even if you're not familiar, just **copy and paste** the commands below exactly as shown.

| Command | Meaning | Example |
|---------|---------|---------|
| `cd folder_name` | Navigate to the folder | `cd sql-tutorial` |
| `ls` (macOS/Linux) / `dir` (Windows) | List files in the current folder | |
| ++enter++ | Execute the command | |

**How to paste:**

- Windows Command Prompt: **Right-click**
- macOS Terminal: ++cmd+v++
- Linux Terminal: ++ctrl+shift+v++

---

## Install Dependencies { #install-dependencies }

Navigate to the project folder and install the required libraries:

```bash
cd sql-tutorial
pip install -r requirements.txt
```

!!! tip "Use `pip3` on macOS/Linux"
    If you get `pip: command not found`, use `pip3` instead:
    ```bash
    pip3 install -r requirements.txt
    ```

!!! info "What is a Virtual Environment (venv)?"
    A virtual environment creates an isolated Python package space for each project. It's safe because it doesn't affect the system Python. Use it when you encounter `Permission denied` errors or want to avoid conflicts with system packages.

    ```bash
    python -m venv .venv

    # Windows
    .venv\Scripts\activate

    # macOS / Linux
    source .venv/bin/activate

    # Install in activated environment
    pip install -r requirements.txt
    ```

    When the virtual environment is activated, `(.venv)` appears before your prompt.

---

## Generate Data

=== "SQLite (Default)"

    ```bash
    python generate.py --size small
    ```

    Creates `output/ecommerce-ko.db` (~80MB, 680K rows). Takes about 20 seconds.

=== "MySQL"

    ```bash
    python generate.py --size small --target mysql
    ```

    Creates `schema.sql`, `data.sql`, and `procedures.sql` in the `output/mysql/` directory.

    To apply directly to the server:

    ```bash
    python generate.py --size small --target mysql --apply --ask-password
    ```

    Enter the root password you set in step 02.

=== "PostgreSQL"

    ```bash
    python generate.py --size small --target postgresql
    ```

    Creates `schema.sql`, `data.sql`, and `procedures.sql` in the `output/postgresql/` directory.

    To apply directly to the server:

    ```bash
    python generate.py --size small --target postgresql --apply --ask-password
    ```

    Enter the postgres password you set in step 02.

=== "All (At Once)"

    ```bash
    python generate.py --size small --all
    ```

    Generates SQLite DB + MySQL SQL + PostgreSQL SQL all at once.

!!! info "Use `python3` on macOS/Linux"
    If you get `python: command not found`, run `python3 generate.py --size small` instead.

### Verify Generation

When completed successfully, you'll see output like this:

```
Data generation complete: 696,771 total records (12.8s)
Exporting to SQLite...
  -> ./output/ecommerce-ko.db (80.7 MB)
Export complete (11.2s)
Total elapsed time: 24.0s
```

Check that files were created in the `output/` folder:

=== "Windows"

    ```
    dir output
    ```

=== "macOS / Linux"

    ```bash
    ls -la output/
    ```

!!! tip "If You Need More Options"
    Advanced options for changing data size, generating English data, adding noise, custom config files, etc. are covered in [Advanced Generator Options](04-generate-advanced.md).

---

## Manual Application for MySQL / PostgreSQL

If you generated SQL files without `--apply`, apply them to the server manually:

=== "MySQL"

    ```bash
    mysql -u root -p < output/mysql/schema.sql
    mysql -u root -p ecommerce < output/mysql/data.sql
    mysql -u root -p ecommerce < output/mysql/procedures.sql
    ```

    Enter the root password for each command.

=== "PostgreSQL"

    ```bash
    psql -U postgres -f output/postgresql/schema.sql
    psql -U postgres ecommerce -f output/postgresql/data.sql
    psql -U postgres ecommerce -f output/postgresql/procedures.sql
    ```

---

## Troubleshooting

!!! warning "Common Issues"

    **`python`/`pip` Command Not Found**

    - Windows: Try `py` or `py -3`
    - macOS/Linux: Use `python3`, `pip3`
    - If PATH isn't set: Reinstall Python and check "Add to PATH"

    **`ModuleNotFoundError`**

    You haven't run `pip install -r requirements.txt`, or the virtual environment is deactivated.

    **Out of Memory During Generation**

    `--size medium` requires about 4GB of memory. Start with `--size small`.

    **Connection Error with MySQL/PG `--apply`**

    Check if the DB server is running:
    ```bash
    # MySQL
    mysql -u root -p -e "SELECT 1"

    # PostgreSQL
    psql -U postgres -c "SELECT 1"
    ```

[← 02. Install the Database](02-database.md){ .md-button }
[05. Verify and First Query →](05-verify.md){ .md-button .md-button--primary }
