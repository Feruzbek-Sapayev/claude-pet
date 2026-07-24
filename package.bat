@echo off
rem Tarqatish uchun ZIP yasaydi -- do'stlaringizga shu faylni yuborasiz.

setlocal
cd /d "%~dp0"

set "OUT=%~dp0..\claude-pet.zip"
if exist "%OUT%" del "%OUT%"

powershell -NoProfile -Command ^
  "$src = Get-ChildItem -Path '%~dp0' -Exclude '__pycache__','*.zip','*.log','package.bat';" ^
  "Compress-Archive -Path $src -DestinationPath '%OUT%' -Force"

if errorlevel 1 (
    echo ZIP yasalmadi.
    pause
    exit /b 1
)

echo.
echo Tayyor: %OUT%
echo Do'stingiz uni yechib, install.bat ni ishga tushirsa bo'ldi.
echo.
pause
