@echo off
setlocal EnableExtensions
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
echo   Downloading installer script...

REM Try curl first (Windows 10+)
where curl >nul 2>&1
if %errorlevel% equ 0 (
    curl.exe -fsSL --retry 3 --retry-delay 2 -A "GameloopFix-Loader" -o "%PS1%" "%DL%"
    if %errorlevel% equ 0 goto :verify
)

REM Fallback: PowerShell with TLS 1.2
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; ^
   $ProgressPreference = 'SilentlyContinue'; ^
   try { ^
     Invoke-WebRequest -Uri '%DL%' -OutFile '%PS1%' -UseBasicParsing -UserAgent 'GameloopFix-Loader'; ^
     exit 0 ^
   } catch { ^
     Write-Host $_.Exception.Message -Fore Red; exit 1 ^
   }"
if errorlevel 1 goto :fail

:verify
if not exist "%PS1%" goto :fail
for %%A in ("%PS1%") do if %%~zA LSS 1000 goto :fail

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -InstallRoot "%~dp0"
set "ERR=%ERRORLEVEL%"
del /q "%PS1%" 2>nul
exit /b %ERR%

:fail
echo.
echo   Failed to download Install-GameloopFix.ps1
echo   URL: %DL%
echo   Try: check internet, firewall, or VPN.
echo.
pause
exit /b 1
