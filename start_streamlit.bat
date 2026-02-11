@echo off
echo ========================================
echo   539 AI 預測大師 - Streamlit 啟動器
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\" (
    echo [INFO] 未偵測到虛擬環境，正在建立...
    python -m venv .venv
    echo [OK] 虛擬環境建立完成
)

REM Activate virtual environment
echo [INFO] 啟動虛擬環境...
call .venv\Scripts\activate.bat

REM Install/Update dependencies
echo [INFO] 檢查並安裝依賴套件...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo   正在啟動 Streamlit 應用...
echo   瀏覽器將自動開啟 http://localhost:8501
echo ========================================
echo.

REM Start Streamlit on port 8700
streamlit run app.py --server.port 8700

pause
