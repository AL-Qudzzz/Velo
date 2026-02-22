@echo off
title AutoBlast — WhatsApp Blaster
echo.
echo  ╔════════════════════════════════════╗
echo  ║     AutoBlast - WhatsApp Blaster   ║
echo  ╚════════════════════════════════════╝
echo.

REM ── Check virtual environment ────────────────────────────────────────────────
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run setup first:
    echo   scripts\setup_venv.bat
    echo.
    pause
    exit /b 1
)

REM ── Activate venv and launch ─────────────────────────────────────────────────
call .venv\Scripts\activate.bat
python main.py
