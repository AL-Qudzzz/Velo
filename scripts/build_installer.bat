@echo off
REM ============================================
REM AutoBlast - Create Windows Installer
REM Membuat installer .exe menggunakan Inno Setup
REM ============================================

echo.
echo ========================================
echo   AutoBlast - Windows Installer Builder
echo ========================================
echo.

REM Step 1: Check if PyInstaller executable exists
if not exist "dist\AutoBlast.exe" (
    echo [ERROR] File AutoBlast.exe tidak ditemukan!
    echo.
    echo Anda harus build executable dulu dengan:
    echo   scripts\build_exe.bat
    echo.
    echo Atau gunakan auto-py-to-exe:
    echo   scripts\build_gui.bat
    echo.
    pause
    exit /b 1
)

echo [1/3] Executable found: dist\AutoBlast.exe
echo.

REM Step 2: Check if Inno Setup is installed
set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %INNO_PATH% (
    echo [WARNING] Inno Setup tidak ditemukan!
    echo.
    echo Silakan download dan install Inno Setup dari:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo Atau compile manual dengan membuka file:
    echo installer_config.iss
    echo.
    pause
    exit /b 1
)

echo [2/3] Inno Setup found
echo.

REM Step 3: Compile installer
echo [3/3] Building installer...
echo This may take a few minutes...
echo.

%INNO_PATH% "installer_config.iss"

echo.
echo ========================================
echo Build Completed!
echo ========================================
echo.

if exist "installer_output\AutoBlast_Setup_v1.0.0.exe" (
    echo SUCCESS! Installer created at:
    echo installer_output\AutoBlast_Setup_v1.0.0.exe
    echo.
    echo File size:
    dir "installer_output\AutoBlast_Setup_v1.0.0.exe" | find "AutoBlast_Setup"
    echo.
    echo Installer ini bisa didistribusikan ke user!
    echo User tinggal double-click untuk install.
) else (
    echo [ERROR] Installer build failed!
    echo Check the output above for errors.
)

echo.
echo ========================================
pause
