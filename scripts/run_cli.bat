@echo off
echo ========================================
echo Velo Bot - CLI Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run scripts\setup_venv.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting Velo Bot CLI...
python -m src.whatsapp_bot %*

pause
