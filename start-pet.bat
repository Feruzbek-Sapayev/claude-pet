@echo off
rem Claude desktop pet -- konsolsiz ishga tushiradi.
rem Papka qayerda bo'lsa ham ishlaydi (%~dp0 = shu faylning papkasi).

setlocal

rem 1) Windows Python ishga tushirgichi (pyw) -- konsolsiz, eng ishonchli
pyw -3 --version >nul 2>&1
if not errorlevel 1 (
    start "" pyw -3 "%~dp0pet.py"
    exit /b 0
)

rem 2) PATH dagi pythonw
pythonw --version >nul 2>&1
if not errorlevel 1 (
    start "" pythonw "%~dp0pet.py"
    exit /b 0
)

rem 3) oddiy python (konsol oynasi ko'rinishi mumkin)
python --version >nul 2>&1
if not errorlevel 1 (
    start "" /min python "%~dp0pet.py"
    exit /b 0
)

echo Python topilmadi. https://python.org saytidan Python 3.8+ o'rnating.
pause
exit /b 1
