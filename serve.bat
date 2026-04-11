@echo off
setlocal

set LANG=%~1
if "%LANG%"=="" set LANG=all

if "%LANG%"=="all" (
    python "%~dp0docs\serve_all.py"
) else (
    cd /d "%~dp0docs"
    mkdocs serve -f mkdocs-%LANG%.yml -a localhost:8001
)
