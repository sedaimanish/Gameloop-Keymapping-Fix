@echo off
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
    echo Python 3 is required for the maintainer build script.
    echo Install from https://www.python.org/ and re-run.
    pause
    exit /b 1
)
python build_patched.py
pause
