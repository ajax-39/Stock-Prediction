@echo off
REM ============================================================================
REM run.bat — Quick Terminal Command for Reliance BDA Platform
REM ============================================================================
cd /d "%~dp0"
python run.py %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Process exited with error code %ERRORLEVEL%.
    pause
)
