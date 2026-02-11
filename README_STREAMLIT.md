# 539 AI 預測大師 - Streamlit Web 應用

## 🎯 專案簡介

這是一個基於 7 大機器學習模型的台灣 539 樂透預測系統，採用 Streamlit 打造的現代化 Web 介面。

## ✨ 核心功能

### 🤖 7 大 AI 模型
- **頻率分析 (Frequency)**: 統計近期號碼出現頻率
- **RSI 動能指標**: 分析號碼動能趨勢
- **線性回歸 (Linear Regression)**: 預測號碼趨勢走向
- **Markov 鏈**: 基於轉移概率的預測
- **KNN 相似度**: 尋找歷史相似開獎組合
- **SVM 分類器**: 機器學習分類預測
- **PCA 穩定性**: 分析號碼出現間隔穩定性

### 🎨 視覺化分析
- 📊 **雷達圖**: 多維度模型評分比較
- 🔥 **熱力圖**: 全號碼各模型評分總覽
- 📈 **回測驗證**: 上期預測準確度驗證
- 🤖 **AI 報告**: Google Gemini 深度分析

### 🎛️ 智能權重系統
- 動態權重調整介面
- 自動回測優化
- 根據命中率自動調整模型權重

## 🚀 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 設定環境變數

創建 `.env` 檔案並設定 Google API Key（選用，用於 AI 報告生成）:

```
GOOGLE_API_KEY=your_api_key_here
```

### 啟動應用

```bash
streamlit run app.py
```

應用將在瀏覽器中自動開啟，預設網址: `http://localhost:8501`

## 📖 使用說明

### 1. 更新資料
點擊側邊欄的「🔄 更新歷史資料」按鈕，系統會自動從網路抓取最新開獎資料。

### 2. 調整權重（選用）
在側邊欄調整各模型權重：
- 🔥 **熱門權重**: 偏重高頻號碼
- 📊 **穩定權重**: 偏重穩定趨勢
- ❄️ **冷門權重**: 偏重冷門補漲
- 🎲 **隨機權重**: 增加隨機性

### 3. 開始預測
點擊主畫面的「🚀 開始預測」按鈕，系統會：
1. 執行上期回測驗證
2. 根據回測結果自動調整權重
3. 運算 7 大模型評分
4. 生成本期推薦號碼
5. 產生 AI 深度分析報告

### 4. 查看結果
在四個分頁中查看詳細分析：
- **📊 模型分析**: 雷達圖與詳細評分表
- **🔥 熱力圖**: 全號碼熱力分析
- **📈 回測結果**: 上期預測驗證
- **🤖 AI 報告**: Gemini 生成的專業分析

## 🎨 介面特色

- 🌌 **暗黑漸層主題**: 科技感十足的視覺設計
- ✨ **動畫效果**: 流暢的懸停與脈衝動畫
- 📱 **響應式設計**: 支援各種螢幕尺寸
- 🎯 **號碼球視覺化**: 直觀的號碼呈現方式

## 📁 專案結構

```
539/
├── app.py                 # Streamlit 主應用
├── main.py               # CLI 版本主程式
├── config.json           # 權重配置檔
├── requirements.txt      # Python 依賴
├── src/
│   ├── crawler.py       # 資料爬蟲
│   ├── models.py        # 7 大模型實作
│   ├── strategy.py      # 策略引擎
│   └── reporter.py      # AI 報告生成器
└── data/
    ├── 539_history.csv  # 歷史資料
    ├── latest_scores.csv # 最新評分
    └── latest_report.txt # 最新報告
```

## ⚠️ 免責聲明

本系統僅供學習與娛樂參考使用，不構成任何投注建議。樂透具有隨機性，請理性投注，量力而為。

## 🔧 技術棧

- **Frontend**: Streamlit, Plotly, Custom CSS
- **Backend**: Python, Pandas, NumPy
- **Machine Learning**: scikit-learn
- **AI**: Google Gemini API
- **Data Source**: Web Scraping (BeautifulSoup)

## 📝 授權

MIT License

---

**🎯 539 AI 預測大師** | Powered by Machine Learning & Google Gemini
