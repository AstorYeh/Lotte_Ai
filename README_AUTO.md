# 539 AI 預測系統 - 自動化使用說明

## 🎯 系統概述

本自動化系統實現了 539 彩票預測的完全自動化流程:
- **每日 23:00** - 自動抓取開獎資料
- **每日 23:05** - 自動驗證預測結果
- **每日 23:10** - 自動執行模型訓練優化
- **每日 23:15** - 自動生成新預測並推送到 Discord

所有操作結果都會自動推送到您的 Discord 頻道!

---

## 🚀 快速開始

### 1. 安裝依賴套件

```bash
cd d:\539
pip install -r requirements.txt
```

### 2. 配置 Discord Webhook

Discord Webhook URL 已設定在 `config/auto_config.json` 中。

如需修改,請編輯該檔案的 `discord.webhook_url` 欄位。

### 3. 啟動自動化系統

**方法一: 使用啟動腳本 (推薦)**
```bash
start_auto.bat
```

**方法二: 直接執行**
```bash
python auto_main.py
```

### 4. 停止系統

按 `Ctrl+C` 即可優雅關閉系統。

---

## ⚙️ 配置說明

### 配置檔案: `config/auto_config.json`

```json
{
  "discord": {
    "webhook_url": "您的 Discord Webhook URL",
    "enable_notifications": true,
    "notification_types": {
      "prediction": true,      // 預測結果通知
      "verification": true,    // 驗證結果通知
      "training": true,        // 訓練報告通知
      "error": true            // 異常警報通知
    }
  },
  "schedule": {
    "data_update_time": "23:00",     // 資料更新時間
    "verification_time": "23:05",    // 驗證時間
    "training_time": "23:10",        // 訓練時間
    "prediction_time": "23:15",      // 預測時間
    "training_frequency": "daily"    // 訓練頻率 (daily/weekly)
  },
  "training": {
    "auto_trigger_threshold": 10,    // 自動訓練觸發閾值
    "use_llm": true,                 // 使用 LLM 顧問
    "use_enhanced_models": true      // 使用增強模型
  },
  "retry": {
    "max_attempts": 3,               // 最大重試次數
    "interval_minutes": 5            // 重試間隔 (分鐘)
  }
}
```

---

## 📊 LOG 系統

系統會自動記錄所有操作到 `logs/` 目錄:

- **execution_errors.log** - 執行異常與堆疊追蹤
- **modifications.log** - 配置與權重變更記錄
- **operations.log** - 自動任務執行狀態
- **backups.log** - 備份操作記錄
- **analysis.log** - 分析結果記錄

---

## 🔔 Discord 通知類型

系統會自動推送以下類型的通知到 Discord:

### 1. 預測結果通知
- 預測日期
- 推薦號碼 (Emoji 球視覺化)
- 回測驗證結果

### 2. 驗證結果通知
- 預測號碼 vs 實際開獎號碼
- 命中數與命中率
- 命中號碼列表

### 3. 訓練報告通知
- 訓練期數
- 平均命中率
- 優化成果

### 4. 異常警報通知
- 異常類型
- 錯誤訊息
- 堆疊追蹤

---

## 🛠️ 故障排除

### 問題 1: Discord 推送失敗

**解決方法**:
1. 檢查 `config/auto_config.json` 中的 Webhook URL 是否正確
2. 測試 Discord 推送:
   ```bash
   python -c "from src.discord_notifier import DiscordNotifier; DiscordNotifier().send_test_message()"
   ```

### 問題 2: 排程任務未執行

**解決方法**:
1. 檢查系統時間是否正確
2. 查看 `logs/operations.log` 確認任務執行狀態
3. 確認系統持續運行 (未被關閉)

### 問題 3: 資料更新失敗

**解決方法**:
1. 檢查網路連線
2. 查看 `logs/execution_errors.log` 確認錯誤原因
3. 手動測試爬蟲:
   ```bash
   python -c "from src.auzonet_crawler import fetch_auzonet_single_date; print(fetch_auzonet_single_date('2026-02-10'))"
   ```

---

## 📝 開機自動啟動 (選用)

### Windows 工作排程器設定

1. 開啟「工作排程器」
2. 建立基本工作
3. 設定觸發條件: 「電腦啟動時」
4. 設定動作: 「啟動程式」
   - 程式: `d:\539\start_auto.bat`
   - 起始位置: `d:\539`
5. 完成設定

---

## ✅ 驗證系統運作

### 檢查清單

- [ ] Discord 推送測試成功
- [ ] 排程任務已註冊
- [ ] LOG 檔案正常生成
- [ ] 資料更新功能正常
- [ ] 預測驗證功能正常

### 測試指令

```bash
# 測試 Discord 推送
python src\discord_notifier.py

# 測試結構化 LOG
python src\structured_logger.py

# 測試資料更新
python src\auto_updater.py

# 測試自動預測
python src\auto_predictor.py
```

---

## 📞 技術支援

如遇到問題,請查看:
1. `logs/execution_errors.log` - 異常日誌
2. Discord 頻道 - 系統通知
3. `logs/operations.log` - 運行日誌

---

**祝您使用愉快!** 🎉
