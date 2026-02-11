@echo off
REM 539 AI 自動化系統 - 啟動腳本
echo ========================================
echo 539 AI Automation System
echo ========================================
echo.

cd /d %~dp0

REM 檢查 Python 是否存在
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b 1
)

REM 檢查虛擬環境
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM 啟動自動化系統
echo [INFO] Starting automation system...
echo.
python auto_main.py

REM 如果程式異常退出,暫停以便查看錯誤
if errorlevel 1 (
    echo.
    echo [ERROR] System exited with error code %errorlevel%
    pause
)
