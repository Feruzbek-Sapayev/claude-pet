@echo off
rem Claude desktop pet -- o'chirish.

setlocal
cd /d "%~dp0"

set "PY="

py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"

if not defined PY (
    python --version >nul 2>&1
    if not errorlevel 1 set "PY=python"
)

if not defined PY (
    echo Python topilmadi -- qo'lda o'chirish yo'riqnomasi README.md da.
    pause
    exit /b 1
)

%PY% uninstall.py
echo.
pause
