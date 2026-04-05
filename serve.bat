@echo off
setlocal

set LANG=%~1
if "%LANG%"=="" set LANG=ko

cd /d "%~dp0docs"
mkdocs serve -f mkdocs-%LANG%.yml -a localhost:8001
