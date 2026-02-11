@echo off
REM Docker 快速部署腳本 (Windows)

echo ==========================================
echo 539 AI 預測系統 - Docker 部署
echo ==========================================

REM 檢查 Docker 是否運行
docker info >nul 2>&1
if errorlevel 1 (
    echo 錯誤: Docker 未運行
    echo 請啟動 Docker Desktop
    pause
    exit /b 1
)

REM 建立必要目錄
echo 建立目錄...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist config mkdir config
if not exist predictions mkdir predictions
if not exist data\lotto mkdir data\lotto
if not exist data\power mkdir data\power
if not exist data\star3 mkdir data\star3
if not exist data\star4 mkdir data\star4

REM 停止舊容器
echo 停止舊容器...
docker-compose down

REM 建立映像
echo 建立 Docker 映像...
docker-compose build

REM 啟動容器
echo 啟動容器...
docker-compose up -d

REM 等待容器啟動
timeout /t 5 /nobreak >nul

REM 檢查狀態
echo.
echo ==========================================
echo 部署完成!
echo ==========================================
docker-compose ps

echo.
echo 查看日誌: docker-compose logs -f
echo 停止系統: docker-compose down
echo 重啟系統: docker-compose restart
echo.
pause
