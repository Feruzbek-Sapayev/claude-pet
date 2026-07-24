@echo off
rem Claude desktop pet -- o'rnatish. Shu faylni ikki marta bosing.

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
    echo.
    echo Python topilmadi.
    echo https://python.org saytidan Python 3.8 yoki undan yangisini o'rnating.
    echo O'rnatishda "Add Python to PATH" katagini belgilashni unutmang.
    echo.
    pause
    exit /b 1
)

%PY% install.py
echo.
pause
