@echo off
REM 啟動網頁看板

echo ==========================================
echo 539 AI 預測系統 - 網頁看板
echo ==========================================

echo.
echo 正在啟動看板...
echo 瀏覽器將自動開啟 http://localhost:8501
echo.
echo 按 Ctrl+C 停止看板
echo ==========================================
echo.

streamlit run dashboard.py
