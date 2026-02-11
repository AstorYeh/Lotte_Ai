#!/bin/bash
# Docker 快速部署腳本

echo "=========================================="
echo "539 AI 預測系統 - Docker 部署"
echo "=========================================="

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "錯誤: Docker 未安裝"
    echo "請先安裝 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 檢查 Docker Compose 是否安裝
if ! command -v docker-compose &> /dev/null; then
    echo "錯誤: Docker Compose 未安裝"
    echo "請先安裝 Docker Compose"
    exit 1
fi

# 檢查配置檔案
if [ ! -f "config/auto_config.json" ]; then
    echo "警告: 配置檔案不存在,使用預設配置"
    mkdir -p config
    cp config/auto_config.json.example config/auto_config.json 2>/dev/null || true
fi

# 建立必要目錄
echo "建立目錄..."
mkdir -p data logs config/backups predictions
mkdir -p data/lotto data/power data/star3 data/star4

# 停止舊容器
echo "停止舊容器..."
docker-compose down

# 建立映像
echo "建立 Docker 映像..."
docker-compose build

# 啟動容器
echo "啟動容器..."
docker-compose up -d

# 等待容器啟動
sleep 5

# 檢查狀態
echo ""
echo "=========================================="
echo "部署完成!"
echo "=========================================="
docker-compose ps

echo ""
echo "查看日誌: docker-compose logs -f"
echo "停止系統: docker-compose down"
echo "重啟系統: docker-compose restart"
