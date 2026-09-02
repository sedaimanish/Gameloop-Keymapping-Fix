@echo off
title GameLoop Keymapping Fix
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-GameloopFix.ps1"
exit /b %ERRORLEVEL%
