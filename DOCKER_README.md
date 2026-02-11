# 539 AI 預測系統 - Docker 部署指南

## 🐳 Docker 自動化部署

本系統已完全容器化,可 24/7 自動運行。

### 快速啟動

```bash
# 1. 建立並啟動容器
docker-compose up -d

# 2. 查看日誌
docker-compose logs -f

# 3. 停止容器
docker-compose down
```

### 系統架構

```
539-ai-predictor (Docker Container)
├── 自動排程系統
│   ├── 23:00 - 抓取開獎資料
│   ├── 23:05 - 驗證預測結果
│   ├── 23:10 - 執行模型訓練
│   └── 23:15 - 生成新預測
├── Discord 推送
└── 日誌記錄
```

### 資料持久化

以下目錄會掛載到主機,確保資料不會遺失:
- `./data` - 訓練資料與歷史記錄
- `./logs` - 系統日誌
- `./config` - 配置檔案
- `./predictions` - 預測記錄

### 配置

編輯 `config/auto_config.json`:
```json
{
  "discord": {
    "webhook_url": "YOUR_DISCORD_WEBHOOK_URL",
    "enable_notifications": true
  },
  "schedule": {
    "data_update_time": "23:00",
    "verification_time": "23:05",
    "training_time": "23:10",
    "prediction_time": "23:15"
  }
}
```

### 管理命令

```bash
# 重啟容器
docker-compose restart

# 查看容器狀態
docker-compose ps

# 進入容器
docker-compose exec lottery-predictor bash

# 查看即時日誌
docker-compose logs -f --tail=100

# 更新系統
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 自動啟動

Docker 容器設定為 `restart: unless-stopped`,會在以下情況自動重啟:
- 系統重開機
- 容器異常退出
- Docker 服務重啟

### 監控

查看系統健康狀態:
```bash
docker-compose ps
docker inspect 539-ai-predictor | grep Health
```

### 故障排除

#### 容器無法啟動
```bash
# 查看詳細日誌
docker-compose logs

# 檢查配置檔案
cat config/auto_config.json
```

#### Discord 推送失敗
- 檢查 webhook URL 是否正確
- 確認網路連線正常

#### 預測失敗
- 檢查訓練資料是否存在
- 查看日誌中的錯誤訊息

### 備份

定期備份以下目錄:
```bash
# 備份資料
tar -czf backup_$(date +%Y%m%d).tar.gz data/ config/ predictions/
```

### 效能優化

調整 Docker 資源限制:
```yaml
services:
  lottery-predictor:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 🚀 開始使用

1. 確保 Docker 和 Docker Compose 已安裝
2. 配置 `config/auto_config.json`
3. 執行 `docker-compose up -d`
4. 系統將自動運行,每晚推送預測到 Discord

**完全自動化,無需人工介入!** 🎯
