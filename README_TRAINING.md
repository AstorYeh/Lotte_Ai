# 訓練與 GitHub 整合指南

## 方案 1: 本機訓練 + 自動推送 (推薦)

### 使用方式
```bash
# 設定 API Key
$env:GOOGLE_API_KEY="你的API金鑰"

# 執行訓練並自動推送
python auto_train_and_push.py
```

### 優點
- ✅ 本機執行,速度快
- ✅ 無時間限制
- ✅ 自動推送結果到 GitHub
- ✅ 完整的錯誤處理

### 流程
1. 執行完整訓練 (325期)
2. 更新 `config.json`
3. 自動 commit 並 push 到 GitHub

---

## 方案 2: GitHub Actions (可選)

### 設置步驟

1. **添加 Secret**
   - 前往 GitHub repo → Settings → Secrets
   - 新增 `GOOGLE_API_KEY`

2. **啟用 Workflow**
   - 編輯 `.github/workflows/daily-training.yml`
   - 取消註解 `schedule` 部分 (如需每日自動執行)

3. **手動觸發**
   - Actions → Daily Training → Run workflow

### 優點
- ✅ 完全自動化
- ✅ 無需本機運行
- ✅ 定時執行

### 限制
- ⚠️ 每月 2,000 分鐘限額
- ⚠️ 單次最長 6 小時
- ❌ 無 GPU 加速

---

## 方案 3: 混合模式

### 建議配置
- **每日訓練**: 使用本機 `auto_train_and_push.py`
- **備份/測試**: 使用 GitHub Actions 手動觸發

---

## 自動化排程 (Windows)

### 使用 Task Scheduler

1. 創建批次檔 `run_training.bat`:
```batch
@echo off
cd /d D:\539
set GOOGLE_API_KEY=你的API金鑰
python auto_train_and_push.py
```

2. 設定排程任務:
   - 開啟「工作排程器」
   - 建立基本工作
   - 觸發程序: 每天 23:10
   - 動作: 啟動程式 → `run_training.bat`

---

## 常見問題

### Q: 訓練需要多久?
A: 約 10-15 分鐘 (325期,使用 LLM)

### Q: 如何確認推送成功?
A: 檢查 GitHub repo 的 commit 歷史

### Q: 可以跳過推送嗎?
A: 可以,直接使用 `AutoTrainer().run_full_training()`

### Q: GitHub Actions 會消耗多少配額?
A: 每次約 15-20 分鐘,每月可執行約 100 次
