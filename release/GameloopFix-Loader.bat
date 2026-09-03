@echo off
setlocal EnableExtensions
title GameLoop Keymapping Fix
cd /d "%~dp0"

net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo   Run as Administrator.
    echo   Right-click this file -^> Run as administrator
    echo.
    pause
    exit /b 1
)

set "PS1=%TEMP%\GameloopFix-Install.ps1"
set "DL=https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/download/v2.0.0/Install-GameloopFix.ps1"

echo.
echo [1/2] Downloading installer script...
echo       %DL%
echo.

del /q "%PS1%" 2>nul
curl.exe -fL --retry 3 --retry-delay 2 -A "GameloopFix-Loader" -o "%PS1%" "%DL%"
if errorlevel 1 goto :download_fail

if not exist "%PS1%" goto :download_fail
for %%A in ("%PS1%") do set "PSIZE=%%~zA"
if %PSIZE% LSS 1000 goto :download_fail

echo.
echo [OK] Downloaded (%PSIZE% bytes)
echo.
echo [2/2] Starting installer...
echo.

REM Strip trailing backslash (fixes paths with spaces e.g. OneDrive\Gameloop Keymap\)
set "INSTALLROOT=%~dp0"
if "%INSTALLROOT:~-1%"=="\" set "INSTALLROOT=%INSTALLROOT:~0,-1%"
set "GAMEFIX_INSTALLROOT=%INSTALLROOT%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy -Scope Process -Bypass -Force" 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
set "ERR=%ERRORLEVEL%"

echo.
if %ERR% neq 0 echo Installer exited with error %ERR%.
pause
exit /b %ERR%

:download_fail
echo.
echo DOWNLOAD FAILED.
echo.
echo Try this in this same window:
echo   curl -fL -o "%%TEMP%%\test.ps1" "%DL%"
echo   dir "%%TEMP%%\test.ps1"
echo.
pause
exit /b 1
