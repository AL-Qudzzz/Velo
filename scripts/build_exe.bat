@echo off
REM ============================================
REM AutoBlast - Command-Line Build Script
REM Builds executable using PyInstaller directly
REM ============================================

echo.
echo ========================================
echo   AutoBlast - Building Executable
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
echo [1/4] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install PyInstaller
echo.
echo [2/4] Installing PyInstaller...
pip install --upgrade pyinstaller

REM Clean previous builds
echo.
echo [3/4] Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec

REM Build executable
echo.
echo [4/4] Building executable...
echo This may take several minutes...
echo.

pyinstaller --name="AutoBlast" ^
    --onefile ^
    --windowed ^
    --add-data "src;src" ^
    --hidden-import=selenium ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=webdriver_manager ^
    --hidden-import=colorama ^
    --hidden-import=pyperclip ^
    --hidden-import=tkinter ^
    --collect-all selenium ^
    --collect-all webdriver_manager ^
    main.py

echo.
echo ========================================
echo Build completed!
echo ========================================
echo.

if exist "dist\AutoBlast.exe" (
    echo SUCCESS! Executable created at:
    echo dist\AutoBlast.exe
    echo.
    echo File size:
    dir dist\AutoBlast.exe | find "AutoBlast.exe"
    echo.
    echo You can now distribute this .exe file to users!
) else (
    echo [ERROR] Build failed! Check the output above for errors.
)

echo.
echo ========================================
pause
