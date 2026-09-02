@echo off
title GameLoop Keymapping Fix
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo   Run GameloopFix-Loader.cmd as Administrator.
    echo   Right-click -^> Run as administrator
    echo.
    pause
    exit /b 1
)

set "PS1=%TEMP%\GameloopFix-Install.ps1"
set "DL=https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/latest/download/Install-GameloopFix.ps1"

echo.
echo   Downloading installer...
powershell -NoProfile -Command ^
  "try { Invoke-WebRequest -Uri '%DL%' -OutFile '%PS1%' -UseBasicParsing } catch { exit 1 }"
if errorlevel 1 (
    echo   Failed to download Install-GameloopFix.ps1
    echo   Check internet or try again later.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -InstallRoot "%~dp0"
set "ERR=%ERRORLEVEL%"
del /q "%PS1%" 2>nul
exit /b %ERR%
