import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import json
from datetime import datetime
import traceback
import time
from src.timezone_utils import get_taiwan_now

# Import project modules
from src.crawler import fetch_data
from src.models import FeatureEngine
from src.strategy import StrategyEngine
from src.reporter import GeminiReporter
from src.logger import logger

# Page configuration
st.set_page_config(
    page_title="539 AI 預測大師",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium dark theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Card-like containers */
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 255, 255, 0.2);
        border-color: rgba(0, 255, 255, 0.3);
    }
    
    /* Headers with glow effect */
    h1, h2, h3 {
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
    }
    
    /* Number balls styling */
    .number-ball {
        display: inline-block;
        width: 60px;
        height: 60px;
        line-height: 60px;
        text-align: center;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 24px;
        font-weight: 700;
        margin: 5px;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        color: #000;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 212, 255, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.5);
    }
    
    /* Info boxes */
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
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 600;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        color: #000;
    }
    
    /* Dataframe styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'predictions' not in st.session_state:
    st.session_state.predictions = None
if 'scores' not in st.session_state:
    st.session_state.scores = None
if 'backtest_result' not in st.session_state:
    st.session_state.backtest_result = None
if 'ai_report' not in st.session_state:
    st.session_state.ai_report = None
if 'prediction_date' not in st.session_state:
    st.session_state.prediction_date = None

# 從預測歷史載入上次預測 (如果有的話)
from src.prediction_history import prediction_history

if st.session_state.predictions is None:
    latest_prediction = prediction_history.get_latest_prediction()
    if latest_prediction and latest_prediction.get("status") == "pending":
        st.session_state.predictions = latest_prediction.get("predicted_numbers")
        st.session_state.prediction_date = latest_prediction.get("prediction_date")
        logger.info(f"從歷史載入預測: {latest_prediction.get('prediction_date')}")


# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ 系統設定")
    
    # API Key 設定區塊
    with st.expander("🔑 API Key 設定", expanded=False):
        from src.api_key_manager import api_key_manager
        
        st.markdown("### Google Gemini API Key")
        st.markdown("用於生成 AI 分析報告")
        
        # 檢查是否已設定
        has_key = api_key_manager.has_api_key("google_gemini")
        
        if has_key:
            st.success("✅ API Key 已設定")
            current_key = api_key_manager.load_api_key("google_gemini")
            masked_key = current_key[:8] + "..." + current_key[-4:] if len(current_key) > 12 else "***"
            st.code(masked_key)
            
            if st.button("🗑️ 刪除 API Key", use_container_width=True):
                api_key_manager.delete_api_key("google_gemini")
                st.success("API Key 已刪除")
                st.rerun()
        else:
            st.warning("⚠️ 尚未設定 API Key")
        
        # 輸入新的 API Key
        st.markdown("---")
        new_api_key = st.text_input(
            "輸入新的 API Key",
            type="password",
            placeholder="AIza...",
            help="請輸入您的 Google Gemini API Key"
        )
        
        if st.button("💾 儲存 API Key", use_container_width=True, type="primary"):
            if new_api_key and len(new_api_key) > 10:
                api_key_manager.save_api_key("google_gemini", new_api_key)
                # 同時設定環境變數
                os.environ["GOOGLE_API_KEY"] = new_api_key
                st.success("✅ API Key 已儲存!")
                st.rerun()
            else:
                st.error("請輸入有效的 API Key")
        
        st.markdown("---")
        st.markdown("""
        **如何取得 API Key?**
        1. 前往 [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. 登入 Google 帳號
        3. 點擊「Create API Key」
        4. 複製 API Key 並貼上
        """)
    
    st.markdown("---")
    
    # 更新資料按鈕
    if st.button("🔄 更新歷史資料", use_container_width=True):
        with st.spinner("正在抓取最新資料..."):
            result = fetch_data()
            if result:
                st.success("✅ 資料更新成功!")
                st.rerun()
            else:
                st.warning("⚠️ 無法從網站抓取資料,請使用測試資料生成器")
    
    # 資料統計
    if os.path.exists("data/539_train.csv"):
        df_info = pd.read_csv("data/539_train.csv")
        st.markdown("### 📊 資料統計")
        st.metric("訓練集筆數", len(df_info))
        if len(df_info) > 0:
            st.caption(f"最新日期: {df_info.iloc[-1]['date']}")
    
    st.markdown("---")
    
    # 權重調整
    st.markdown("### 🎛️ 策略權重")
    
    # Load current weights with safe defaults
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
    else:
        config = {}
    
    # 使用 .get() 方法提供預設值,避免 KeyError
    hot = st.slider("🔥 熱門號碼", 0.0, 1.0, config.get("hot_weight", 0.4), 0.05)
    stable = st.slider("📊 穩定號碼", 0.0, 1.0, config.get("stable_weight", 0.3), 0.05)
    cold = st.slider("❄️ 冷門號碼", 0.0, 1.0, config.get("cold_weight", 0.2), 0.05)
    random = st.slider("🎲 隨機號碼", 0.0, 1.0, config.get("random_weight", 0.1), 0.05)
    
    # Normalize weights
    total = hot + stable + cold + random
    if total > 0:
        config["hot_weight"] = hot / total
        config["stable_weight"] = stable / total
        config["cold_weight"] = cold / total
        config["random_weight"] = random / total
    
    if st.button("💾 儲存權重", use_container_width=True):
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        st.success("✅ 權重已儲存!")
        st.rerun()

# Main content
st.markdown("# 🎯 539 AI 預測大師")
st.markdown("### 運用 7 大 AI 模型，精準預測下期號碼")

# Main action button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # 檢查是否有待驗證的預測
    pending_prediction = prediction_history.get_pending_prediction()
    
    if pending_prediction:
        st.warning(f"⚠️ 您有一個待驗證的預測 ({pending_prediction.get('prediction_date')})")
        
        # 顯示待驗證的預測號碼
        # 顯示待驗證的預測號碼
        st.markdown("### 📋 待驗證的預測號碼")
        pending_numbers_data = pending_prediction.get('predicted_numbers', [])
        
        # 確保格式統一 (轉為 list of lists)
        if pending_numbers_data and isinstance(pending_numbers_data[0], list):
            prediction_sets = pending_numbers_data
        else:
            prediction_sets = [pending_numbers_data]
            
        for idx, p_set in enumerate(prediction_sets):
            balls_html = f'<div style="text-align: center; padding: 5px;">'
            if len(prediction_sets) > 1:
                balls_html += f'<div style="margin-bottom:5px; color:#aaa;">第 {idx+1} 組</div>'
            
            for num in p_set:
                balls_html += f'<div class="number-ball" style="display: inline-block; margin: 5px;">{num:02d}</div>'
            balls_html += '</div>'
            st.markdown(balls_html, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🎯 輸入實際開獎號碼")
        
        # 添加日期選擇和獲取按鈕
        col_date, col_fetch = st.columns([3, 1])
        with col_date:
            # 解析預測日期作為預設值
            prediction_date_str = pending_prediction.get('prediction_date', '')
            try:
                # 假設格式為 "2026-01-30 週四" 或 "2026-01-30"
                date_part = prediction_date_str.split()[0]
                default_date = datetime.strptime(date_part, "%Y-%m-%d").date()
            except:
                default_date = get_taiwan_now().date()
            
            fetch_date = st.date_input(
                "選擇開獎日期",
                value=default_date,  # 使用預測日期
                key="fetch_date_main"
            )
        with col_fetch:
            st.write("")  # 空行對齊
            if st.button("🔍 獲取開獎號碼", use_container_width=True, type="secondary", key="fetch_btn_main"):
                try:
                    from src.auzonet_crawler import fetch_auzonet_single_date
                    
                    date_str = fetch_date.strftime("%Y-%m-%d")
                    
                    # 直接調用,不使用 spinner
                    fetched_numbers = fetch_auzonet_single_date(date_str)
                    
                    if fetched_numbers:
                        # 格式化為逗號分隔的字串
                        numbers_str = ', '.join([str(n) for n in fetched_numbers])
                        st.session_state.fetched_numbers_str = numbers_str
                        st.success(f"✅ 已從官網獲取: {numbers_str}")
                        # 觸發頁面重新載入以更新輸入框
                        st.rerun()
                    else:
                        st.warning(f"⚠️ 官網找不到 {date_str} 的開獎記錄")
                        st.info("💡 可能原因: 該日期尚未開獎、週日不開獎、或網站暫時無法訪問")
                except Exception as e:
                    st.error(f"❌ 獲取失敗: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        
        st.caption("請輸入 5 個號碼 (1-39),用逗號或空格分隔")
        
        # 開獎號碼輸入 - 使用獲取的號碼作為預設值
        default_value = st.session_state.get('fetched_numbers_str', '')
        actual_input = st.text_input(
            "開獎號碼",
            value=default_value,
            placeholder="例如: 8, 15, 20, 25, 32 或 8 15 20 25 32",
            key="actual_numbers_input"
        )
        
        col_verify1, col_verify2 = st.columns(2)
        
        with col_verify1:
            if st.button("✅ 驗證並優化", use_container_width=True, type="primary"):
                # 解析輸入
                actual_numbers = []
                if actual_input:
                    # 支援逗號或空格分隔
                    input_clean = actual_input.replace(',', ' ')
                    try:
                        actual_numbers = [int(x) for x in input_clean.split() if x.strip()]
                    except ValueError:
                        st.error("❌ 請輸入有效的數字")
                
                if len(actual_numbers) != 5:
                    st.error("❌ 請輸入 5 個號碼")
                elif not all(1 <= n <= 39 for n in actual_numbers):
                    st.error("❌ 號碼必須在 1-39 之間")
                elif len(set(actual_numbers)) != 5:
                    st.error("❌ 號碼不能重複")
                else:
                    # 驗證預測
                    # 驗證預測 (計算最佳命中)
                    predicted_data = pending_prediction.get('predicted_numbers', [])
                    
                    if predicted_data and isinstance(predicted_data[0], list):
                        prediction_sets = predicted_data
                    else:
                        prediction_sets = [predicted_data]
                        
                    best_hits_count = 0
                    actual_set = set(actual_numbers)
                    
                    for p_set in prediction_sets:
                        p_set_clean = [int(x) for x in p_set]
                        current_hits = len(set(p_set_clean) & actual_set)
                        if current_hits > best_hits_count:
                            best_hits_count = current_hits
                    
                    hits = best_hits_count
                    
                    # 更新預測記錄
                    prediction_history.update_actual_result(
                        prediction_date=pending_prediction.get('prediction_date'),
                        actual_numbers=actual_numbers
                    )
                    
                    # 顯示結果
                    if hits >= 3:
                        st.success(f"🎉 恭喜!命中 {hits} 個號碼!")
                    else:
                        st.info(f"命中 {hits} 個號碼")
                    
                    # 清除 session state
                    if 'fetched_numbers_str' in st.session_state:
                        del st.session_state.fetched_numbers_str
                    
                    st.rerun()
        
        with col_verify2:
            if st.button("🗑️ 放棄此預測", use_container_width=True, type="secondary"):
                # 將預測狀態改為 expired
                history = prediction_history.load_all_predictions()
                for record in history:
                    if record.get('prediction_date') == pending_prediction.get('prediction_date'):
                        record['status'] = 'expired'
                        break
                
                # 儲存更新
                import json
                with open(prediction_history.history_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
                
                # 清除 session state
                if 'fetched_numbers_str' in st.session_state:
                    del st.session_state.fetched_numbers_str
                st.rerun()
        
        predict_button_disabled = True
    else:
        predict_button_disabled = False
    
    st.markdown("---")
    
    if st.button("🚀 開始預測", use_container_width=True, type="primary", disabled=predict_button_disabled):
        with st.spinner("🔮 AI 模型運算中..."):
            try:
                logger.section("Streamlit 預測流程")
                logger.info("使用者點擊開始預測按鈕")
                
                # Check data availability
                if not os.path.exists("data/539_history.csv"):
                    error_msg = "找不到歷史資料,請先更新資料"
                    logger.error(error_msg)
                    st.error(f"❌ {error_msg}")
                else:
                    # Backtest
                    logger.step(1, "執行回測驗證")
                    full_df = pd.read_csv("data/539_history.csv")
                    logger.info(f"載入完整資料: {len(full_df)} 筆")
                    
                    if len(full_df) > 100:
                        try:
                            eng_ver = FeatureEngine()
                            real_last_draw = eng_ver.df.iloc[-1]
                            real_last_nums = [int(n) for n in real_last_draw['numbers'].split(',')]
                            logger.info(f"回測目標: {real_last_draw['date']} - {real_last_nums}")
                            
                            eng_ver.df = eng_ver.df.iloc[:-1].reset_index(drop=True)
                            eng_ver.numbers_series = eng_ver.numbers_series[:-1]
                            
                            scores_ver = eng_ver.get_all_scores(
                                use_enhanced=True,      # 啟用增強模型
                                use_time_series=False   # 禁用時間序列特徵
                            )
                            strat_ver = StrategyEngine()
                            candidates_ver = strat_ver.partition_strategy(strat_ver.calculate_total_score(scores_ver))
                            
                            hits = set(candidates_ver).intersection(set(real_last_nums))
                            accuracy = len(hits) / 5.0
                            
                            logger.result("回測預測", candidates_ver)
                            logger.result("命中數", f"{len(hits)}/5")
                            logger.result("命中率", f"{accuracy:.0%}")
                            
                            st.session_state.backtest_result = {
                                'date': str(real_last_draw['date']),  # 轉換為字串避免 Timestamp 錯誤
                                'actual': real_last_nums,
                                'predicted': candidates_ver,
                                'hits': list(hits),
                                'accuracy': accuracy
                            }
                            
                            strat_ver.update_weights(accuracy)
                            logger.success("回測完成,權重已更新")
                        except Exception as e:
                            logger.error(f"回測過程發生錯誤: {e}")
                            logger.debug(traceback.format_exc())
                    
                    # Real prediction
                    logger.step(2, "執行本期預測")
                    eng = FeatureEngine()
                    strat = StrategyEngine()
                    
                    scores = eng.get_all_scores(
                        use_enhanced=True,      # 啟用增強模型
                        use_time_series=False   # 禁用時間序列特徵
                    )
                    final_scores = strat.calculate_total_score(scores)
                    candidates = strat.partition_strategy(final_scores)
                    
                    # 計算預測目標日期 (下一個開獎日)
                    from datetime import datetime, timedelta
                    last_date = pd.to_datetime(eng.df.iloc[-1]['date'])
                    next_date = last_date + timedelta(days=1)
                    
                    # 跳過週日 (weekday() == 6)
                    while next_date.weekday() == 6:
                        next_date += timedelta(days=1)
                    
                    # 格式化日期與星期
                    weekday_names = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
                    weekday = weekday_names[next_date.weekday()]
                    prediction_date = f"{next_date.strftime('%Y-%m-%d')} {weekday}"
                    
                    st.session_state.predictions = candidates
                    st.session_state.scores = final_scores
                    st.session_state.prediction_date = prediction_date  # 儲存預測日期
                    
                    logger.result("預測目標日期", prediction_date)
                    logger.result("推薦號碼", candidates)
                    
                    # 儲存預測結果到歷史記錄
                    logger.step(3, "儲存預測結果")
                    prediction_history.save_prediction(
                        prediction_date=prediction_date,
                        numbers=candidates,
                        backtest_result=st.session_state.backtest_result
                    )
                    
                    # Generate AI report
                    logger.step(4, "生成 AI 報告")
                    reporter = GeminiReporter()
                    report = reporter.generate_report(candidates, final_scores)
                    st.session_state.ai_report = report
                    logger.success("AI 報告生成完成")
                    
                    st.success("✅ 預測完成!")
                    st.balloons()
                    logger.success("預測流程完成")
                    
            except Exception as e:
                error_msg = f"預測過程發生錯誤: {e}"
                logger.critical(error_msg)
                logger.debug(f"錯誤堆疊:\n{traceback.format_exc()}")
                st.error(f"❌ {error_msg}")
                st.error("詳細錯誤請查看日誌檔案: logs/539_ai_YYYYMMDD.log")

# Display results
if st.session_state.predictions:
    st.markdown("---")
    
    # Prediction display with date
    prediction_date = st.session_state.get('prediction_date', '未知日期')
    st.markdown(f"## 🎲 本期推薦號碼 ({prediction_date})")
    
    # Create number balls
    balls_html = '<div style="text-align: center; padding: 20px;">'
    for num in st.session_state.predictions:
        balls_html += f'<div class="number-ball">{num:02d}</div>'
    balls_html += '</div>'
    st.markdown(balls_html, unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 模型分析", "🔥 熱力圖", "📈 回測結果", "🤖 AI 報告"])
    
    with tab1:
        st.markdown("### 各模型評分詳情")
        
        if st.session_state.scores is not None:
            # Filter scores for predicted numbers
            pred_scores = st.session_state.scores.loc[st.session_state.predictions].copy()
            
            # Create radar chart
            fig = go.Figure()
            
            for num in st.session_state.predictions:
                row = pred_scores.loc[num]
                fig.add_trace(go.Scatterpolar(
                    r=[row.get('freq', 0), row.get('rsi', 0), row.get('slope', 0), 
                       row.get('knn', 0), row.get('svm', 0), row.get('markov', 0), 
                       row.get('pca', 0), row.get('xgboost', 0), row.get('random_forest', 0)],
                    theta=['頻率', 'RSI', '趨勢', 'KNN', 'SVM', 'Markov', 'PCA', 'XGBoost', 'Random Forest'],
                    fill='toself',
                    name=f'號碼 {num:02d}'
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1]),
                    bgcolor='rgba(0,0,0,0)'
                ),
                showlegend=True,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed scores table
            st.markdown("### 詳細評分表")
            display_df = pred_scores.copy()
            display_df.index.name = '號碼'
            st.dataframe(display_df.style.background_gradient(cmap='viridis'), use_container_width=True)
    
    with tab2:
        st.markdown("### 全號碼熱力分析")
        
        if st.session_state.scores is not None:
            # Create heatmap for all numbers
            scores_matrix = st.session_state.scores.copy()
            
            # Reshape for heatmap (4 rows x 10 cols to fit 1-39)
            heatmap_data = []
            model_cols = ['freq', 'rsi', 'slope', 'knn', 'svm', 'markov', 'pca', 'xgboost', 'random_forest']
            
            for col in model_cols:
                row_data = scores_matrix[col].values
                # Pad to 40 for easier reshaping
                padded = np.pad(row_data, (0, 1), constant_values=0)
                heatmap_data.append(padded.reshape(4, 10))
            
            # Create subplots for each model (3x3 for 9 models)
            fig = make_subplots(
                rows=3, cols=3,
                subplot_titles=['頻率 (Freq)', 'RSI', '趨勢 (Slope)', 
                               'KNN', 'SVM', 'Markov', 
                               'PCA', 'XGBoost', 'Random Forest'],
                vertical_spacing=0.12,
                horizontal_spacing=0.08
            )
            
            positions = [(1,1), (1,2), (1,3), (2,1), (2,2), (2,3), (3,1), (3,2), (3,3)]
            
            for idx, (col, pos) in enumerate(zip(model_cols, positions)): # Changed from model_cols + ['total_score'] to model_cols
                # The 'total_score' subplot is removed as per the 3x3 layout for 9 models
                # if col == 'total_score':
                #     data = st.session_state.scores[col].values
                # else:
                data = scores_matrix[col].values
                
                padded = np.pad(data, (0, 1), constant_values=0)
                matrix = padded.reshape(4, 10)
                
                fig.add_trace(
                    go.Heatmap(
                        z=matrix,
                        colorscale='Viridis',
                        showscale=(idx == 0),
                        text=[[f'{i*10+j+1}' if i*10+j < 39 else '' for j in range(10)] for i in range(4)],
                        texttemplate='%{text}',
                        textfont={"size": 10}
                    ),
                    row=pos[0], col=pos[1]
                )
            
            fig.update_layout(
                height=800,  # 增加高度以容納 3x3 佈局
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 上期回測驗證")
        
        if st.session_state.backtest_result:
            result = st.session_state.backtest_result
            
            col1, col2, col3 = st.columns(3)
            with col1:
                # 將 Timestamp 轉換為字串
                date_str = str(result['date']) if not isinstance(result['date'], str) else result['date']
                st.metric("回測日期", date_str)
            with col2:
                st.metric("命中數", f"{len(result['hits'])}/5")
            with col3:
                st.metric("命中率", f"{result['accuracy']:.0%}")
            
            st.markdown("#### 實際開獎號碼")
            actual_html = '<div style="text-align: center;">'
            for num in result['actual']:
                color = '#00ff88' if num in result['hits'] else '#667eea'
                actual_html += f'<div class="number-ball" style="background: {color};">{num:02d}</div>'
            actual_html += '</div>'
            st.markdown(actual_html, unsafe_allow_html=True)
            
            st.markdown("#### AI 預測號碼")
            pred_html = '<div style="text-align: center;">'
            for num in result['predicted']:
                color = '#00ff88' if num in result['hits'] else '#667eea'
                pred_html += f'<div class="number-ball" style="background: {color};">{num:02d}</div>'
            pred_html += '</div>'
            st.markdown(pred_html, unsafe_allow_html=True)
            
            if result['hits']:
                st.markdown(f'<div class="success-box">✅ 命中號碼: {", ".join([f"{n:02d}" for n in result["hits"]])}</div>', 
                          unsafe_allow_html=True)
        else:
            st.info("尚無回測資料")
    
    with tab4:
        st.markdown("### AI 深度分析報告")
        
        if st.session_state.ai_report:
            st.markdown(f'<div class="info-box">{st.session_state.ai_report}</div>', 
                       unsafe_allow_html=True)
        else:
            st.info("AI 報告生成中或未啟用...")

else:
    # Welcome screen
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>🎯 9 大 AI 模型</h3>
            <p>基礎 7 模型 + 增強 2 模型 (XGBoost, Random Forest)</p>
            <p style="font-size: 14px; color: rgba(255,255,255,0.7); margin-top: 10px;">
              ✅ 命中率 20.65% | 平均命中 0.89 顆
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>🧠 智能權重</h3>
            <p>自動回測調整，根據歷史命中率動態優化模型權重</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box">
            <h3>📊 視覺化分析</h3>
            <p>雷達圖、熱力圖、趨勢圖，多維度呈現數據洞察</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.5); padding: 20px;">
    <p>🎯 539 AI 預測大師 | Powered by Machine Learning & Google Gemini</p>
    <p style="font-size: 12px;">本系統僅供娛樂參考，請理性投注</p>
</div>
""", unsafe_allow_html=True)
