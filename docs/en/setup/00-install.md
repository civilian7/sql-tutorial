# 00. Download the Project

This project manages all source code, the data generator, and documentation on [GitHub](https://github.com/civilian7/sql-tutorial).

Since the documentation is updated frequently, **we recommend using Git to always stay up to date**. If you're new to Git, refer to the instructions below.

## What is Git?

**Git** is a version control system that tracks changes to files. For this tutorial, you only need to know two things:

- `git clone` — Copy the project to your computer
- `git pull` — Get subsequent updates with a single command

!!! info "How to Install Git (click to expand)"

    === "Windows"

        Download and install from [git-scm.com](https://git-scm.com/download/win). Keep the default options during installation.

        After installation, verify in **Command Prompt** or **Git Bash**:

        ```
        git --version
        ```

    === "macOS"

        In **Terminal**:

        ```bash
        # Included with Xcode command line tools (usually already installed)
        git --version

        # If not available, install with Homebrew
        brew install git
        ```

    === "Linux (Ubuntu/Debian)"

        ```bash
        sudo apt update && sudo apt install git
        git --version
        ```

## Download Methods

=== "Git (Recommended)"

    ```bash
    git clone https://github.com/civilian7/sql-tutorial.git
    cd sql-tutorial
    ```

    When updates are available later:

    ```bash
    git pull
    ```

=== "Git GUI (GitHub Desktop)"

    If the command line is difficult, you can use [GitHub Desktop](https://desktop.github.com/).

    1. Install and launch GitHub Desktop
    2. Select **File > Clone repository**
    3. In the URL tab, enter `https://github.com/civilian7/sql-tutorial.git`
    4. Specify a local path and click **Clone**
    5. For updates: Click **Fetch origin** at the top, then **Pull origin**

=== "ZIP Download"

    You can start immediately without Git, but you'll need to re-download each time to get updates.

    1. [Download ZIP from GitHub](https://github.com/civilian7/sql-tutorial/archive/refs/heads/main.zip)
    2. Extract the downloaded file
    3. Navigate to the extracted folder (`sql-tutorial-main`)

    !!! warning "ZIP Limitations"
        ZIP is a snapshot from the time of download. You won't receive updates such as new lessons or bug fixes.

## Verify the Download

If you see the following files in the project folder, everything is correct:

```
sql-tutorial/
├── requirements.txt     ← Python dependencies
├── config.yaml          ← Generation config
├── src/                 ← Generator, verifier, and utility source code
├── data/                ← Product/category master data
├── docs/                ← Tutorial documents
└── output/              ← (After generation) DB/SQL output
```

[← Getting Started](index.md){ .md-button }
[01. Choose a Database →](01-choose-db.md){ .md-button .md-button--primary }
