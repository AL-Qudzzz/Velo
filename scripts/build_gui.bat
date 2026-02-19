@echo off
REM ============================================
REM AutoBlast - GUI Build Tool Launcher
REM Launches auto-py-to-exe for easy executable creation
REM ============================================

echo.
echo ========================================
echo   AutoBlast - GUI Build Tool
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run scripts\setup_venv.bat first.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/upgrade auto-py-to-exe
echo.
echo [2/3] Installing auto-py-to-exe...
pip install --upgrade auto-py-to-exe pyinstaller

REM Launch auto-py-to-exe
echo.
echo [3/3] Launching auto-py-to-exe...
echo.
echo ========================================
echo INSTRUCTIONS:
echo ========================================
echo 1. Script Location: Select "main.py" from this folder
echo 2. One File: Select "One File" option
echo 3. Console Window: Select "Window Based" (no console)
echo 4. Icon: (Optional) Select an icon file if you have one
echo 5. Additional Files: Add "src" folder
echo 6. Click "CONVERT .PY TO .EXE"
echo ========================================
echo.
echo Press ENTER to continue...
pause >nul

auto-py-to-exe

echo.
echo ========================================
echo Build completed!
echo Check the "output" folder for your .exe file
echo ========================================
echo.
pause
