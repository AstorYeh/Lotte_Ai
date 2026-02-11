# -*- coding: utf-8 -*-
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="系統配置 - 539 AI",
    page_icon="⚙️",
    layout="wide"
)

# Custom CSS (same as main app)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    h1, h2, h3 {
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    .config-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin: 15px 0;
    }
    
    .model-badge {
        display: inline-block;
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        margin: 5px;
        font-size: 14px;
        font-weight: 600;
    }
    
    .enhanced-badge {
        background: linear-gradient(90deg, #f093fb, #f5576c);
    }
    
    .info-box {
        background: rgba(0, 212, 255, 0.1);
        border-left: 4px solid #00d4ff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .success-box {
        background: rgba(0, 255, 136, 0.1);
        border-left: 4px solid #00ff88;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .warning-box {
        background: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.markdown("# ⚙️ 系統配置")
st.markdown("### 當前最優配置 (方案 A)")

st.markdown('<div class="success-box">', unsafe_allow_html=True)
st.markdown("""
**🎉 經過 7 次完整訓練驗證,方案 A 為最優配置**

總提升: 15.74% → 20.65% = **+31.2%**
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 配置資訊
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("### 📊 性能指標")
    st.markdown("""
    | 指標 | 數值 | 說明 |
    |------|------|------|
    | **2+ 顆命中率** | **20.65%** | 打平或賺錢的機率 |
    | **平均命中數** | **0.89** | 每期平均命中數量 |
    | **賺錢率 (3+)** | **1.31%** | 3 顆以上命中率 |
    | **虧損率 (0-1)** | **79.34%** | 0-1 顆命中率 |
    | **訓練期數** | **305** | 歷史訓練數據量 |
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 配置參數")
    st.markdown("""
    | 參數 | 設定值 | 說明 |
    |------|--------|------|
    | **選號數量** | **6-7 顆** | 每期推薦號碼數量 |
    | **群組平衡** | **✅ 啟用** | 確保號碼分布均衡 |
    | **增強模型** | **✅ 啟用** | XGBoost + Random Forest |
    | **時間序列** | **❌ 禁用** | 已證實引入噪音 |
    | **默認值** | **0.5** | 增強模型默認評分 |
    """)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 模型列表
st.markdown("### 🤖 啟用的模型 (9 個)")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("#### 基礎模型 (1-4)")
    st.markdown("""
    <div class="model-badge">1. freq - 頻率分析</div>
    <div class="model-badge">2. rsi - RSI 指標</div>
    <div class="model-badge">3. slope - 線性趨勢</div>
    <div class="model-badge">4. knn - K 近鄰</div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("#### 基礎模型 (5-7)")
    st.markdown("""
    <div class="model-badge">5. svm - 支持向量機</div>
    <div class="model-badge">6. markov - 馬可夫鏈</div>
    <div class="model-badge">7. pca - PCA 變異數</div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("#### 增強模型 (8-9)")
    st.markdown("""
    <div class="model-badge enhanced-badge">8. xgboost - XGBoost</div>
    <div class="model-badge enhanced-badge">9. random_forest - Random Forest</div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 優化歷程
st.markdown("### 📈 優化歷程")

st.markdown("""
| 階段 | 配置 | 模型數 | 2+命中率 | 變化 | 結論 |
|------|------|--------|----------|------|------|
| 修復前 | 5顆,無平衡,0/1 | 9 | 15.74% | - | 起點 |
| 階段1 | 5顆,無平衡,0.15 | 9 | 16.73% | +6.3% | 改進默認值有效 ✅ |
| 階段2 | 6-7顆,平衡,0.15 | 9 | 19.67% | +17.6% | 原始配置核心優勢 ✅ |
| **方案A** | **6-7顆,平衡,0.5** | **9** | **20.65%** | **+5.0%** | **最優解** 🥇 |
| 方案B | 6-7顆,平衡,0.5,TS | 13 | 18.69% | -9.5% | 時間序列特徵失敗 ❌ |
| 禁用增強 | 5顆,無平衡,禁用 | 7 | 17.38% | - | 增強模型有效 ✅ |
| 原始基準 | 6-7顆,平衡,0.5 | 9 | 20.65% | - | 與方案A完全相同 ✅ |
""")

st.markdown('<div class="success-box">', unsafe_allow_html=True)
st.markdown("""
**關鍵發現**:
- ✅ 方案 A = 原始基準線 (完全相同配置)
- ✅ 總提升: 15.74% → 20.65% = **+31.2%**
- ❌ 時間序列特徵: **-9.5%** (有害,已禁用)
- ✅ 增強模型: **有效** (XGBoost + Random Forest)
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 為什麼這是最優配置
st.markdown("### 💡 為什麼這是最優配置?")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    #### ✅ 優勢
    
    1. **經過充分驗證**
       - 7 次完整 305 期訓練
       - 所有優化嘗試都回到此配置
       - 與原始基準線完全相同
    
    2. **平衡的模型組合**
       - 基礎 7 模型提供穩定基礎
       - 增強 2 模型提升準確度
       - 9 個模型不多不少剛好
    
    3. **最優的參數設定**
       - 6-7 顆選號平衡風險與收益
       - 群組平衡確保號碼分布
       - 默認值 0.5 避免極端評分
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    #### ⚠️ 已驗證的失敗嘗試
    
    1. **時間序列特徵 (方案 B)**
       - 添加 4 個時間序列特徵
       - 模型數量: 9 → 13
       - 結果: 20.65% → 18.69% (-9.5%)
       - 結論: 引入噪音,降低性能 ❌
    
    2. **禁用增強模型**
       - 只使用基礎 7 模型
       - 結果: 17.38%
       - 結論: 增強模型確實有效 ✅
    
    3. **其他配置調整**
       - 所有嘗試都無法超越 20.65%
       - 結論: 當前配置已達極限 🎯
    """)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 技術細節
with st.expander("🔧 技術細節", expanded=False):
    st.markdown("""
    ### 模型評分機制
    
    ```python
    # 獲取所有模型評分
    scores = eng.get_all_scores(
        use_enhanced=True,      # 啟用增強模型
        use_time_series=False   # 禁用時間序列
    )
    
    # 模型列表
    models = [
        'freq', 'rsi', 'slope', 'knn', 'svm', 'markov', 'pca',  # 基礎 7 個
        'xgboost', 'random_forest'  # 增強 2 個
    ]
    ```
    
    ### 選號策略
    
    ```python
    # 群組平衡策略
    target_count = (6, 7)  # 6-7 顆選號
    enable_group_balance = True  # 啟用群組平衡
    
    # 四個群組
    group1 = [1-10]
    group2 = [11-20]
    group3 = [21-30]
    group4 = [31-39]
    
    # 每組選 1-2 顆,確保分布均衡
    ```
    
    ### 增強模型配置
    
    ```python
    # XGBoost
    n_estimators = 50
    default_value = 0.5  # 未見過的號碼默認評分
    
    # Random Forest
    n_estimators = 50
    default_value = 0.5  # 未見過的號碼默認評分
    ```
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.5); padding: 20px;">
    <p>⚙️ 系統配置 | 539 AI 預測大師</p>
    <p style="font-size: 12px;">方案 A - 最優配置 | 命中率 20.65%</p>
</div>
""", unsafe_allow_html=True)
