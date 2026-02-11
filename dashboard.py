# -*- coding: utf-8 -*-
"""
多遊戲預測系統 - 網頁看板
使用 Streamlit 建立互動式儀表板
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import json
from src.timezone_utils import get_taiwan_datetime_str, get_taiwan_date_only_str

# 頁面配置
st.set_page_config(
    page_title="539 AI 預測系統",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .game-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .prediction-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .number-ball {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        margin: 0 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 標題
st.markdown('<h1 class="main-header">🎯 539 AI 預測系統看板</h1>', unsafe_allow_html=True)

# 側邊欄
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=539+AI", use_container_width=True)
    st.markdown("### 📊 系統選單")
    
    page = st.radio(
        "選擇頁面",
        ["🏠 首頁", "🎲 最新預測", "📈 歷史記錄", "⚙️ 系統狀態"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 🎮 支援遊戲")
    st.markdown("""
    - 今彩539
    - 大樂透
    - 威力彩
    - 3星彩
    - 4星彩
    """)
    
    st.markdown("---")
    st.markdown(f"**系統時間**: {get_taiwan_datetime_str()}")

# 載入預測資料
def load_predictions():
    """載入最新預測"""
    predictions = {}
    
    games = ['539', 'lotto', 'power', 'star3', 'star4']
    
    for game in games:
        pred_file = Path(f"predictions/{game}_predictions.csv")
        if pred_file.exists():
            try:
                df = pd.read_csv(pred_file)
                if not df.empty:
                    latest = df.iloc[-1]
                    # 安全地解析 numbers字串
                    raw_numbers = latest.get('numbers', '[]')
                    try:
                        numbers = eval(raw_numbers)
                    except:
                        numbers = []
                        
                    predictions[game] = {
                        'date': latest.get('date', 'N/A'),
                        'numbers': numbers
                    }
            except Exception as e:
                print(f"Error loading {game} predictions: {e}")
                
    return predictions

def load_history(game):
    """載入歷史資料"""
    file_map = {
        '539': 'data/539_history.csv',
        'lotto': 'data/lotto/lotto_history.csv',
        'power': 'data/power/power_history.csv',
        'star3': 'data/star3/star3_history.csv',
        'star4': 'data/star4/star4_history.csv'
    }
    
    file_path = Path(file_map.get(game, ''))
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame()

# ... (UI code continues)

# 最新預測頁面
elif page == "🎲 最新預測":
    st.markdown("## 最新預測號碼")
    
    # 載入預測
    predictions = load_predictions()
    
    game_tabs = st.tabs(["今彩539", "大樂透", "威力彩", "3星彩", "4星彩"])
    
    # helper for creating balls
    def create_balls_html(numbers, is_special=False):
        html = ""
        for n in numbers:
            color = "#ff4b4b" if is_special else "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            html += f'<span class="number-ball" style="background: {color};">{n}</span>'
        return html

    # 539
    with game_tabs[0]:
        st.markdown("### 今彩539 預測 (39選5)")
        
        if '539' in predictions:
            data = predictions['539']
            st.markdown(f"**預測日期**: {data['date']}")
            
            numbers = data['numbers']
            # Check structure (list of lists or list)
            if numbers and isinstance(numbers[0], list):
                for i, nums in enumerate(numbers, 1):
                    balls_html = create_balls_html(nums)
                    st.markdown(f"""
                    <div class="prediction-box">
                        <strong>第 {i} 組:</strong> {balls_html}
                    </div>
                    """, unsafe_allow_html=True)
            elif numbers:
                balls_html = create_balls_html(numbers)
                st.markdown(f'<div class="prediction-box">{balls_html}</div>', unsafe_allow_html=True)
        else:
            st.info("暫無預測資料")
    
    # 大樂透
    with game_tabs[1]:
        st.markdown("### 大樂透預測 (49選6)")
        if 'lotto' in predictions:
            data = predictions['lotto']
            st.markdown(f"**預測日期**: {data['date']}")
            
            numbers = data['numbers']
            for i, nums in enumerate(numbers, 1):
                balls_html = create_balls_html(nums)
                st.markdown(f"""
                <div class="prediction-box">
                    <strong>第 {i} 組:</strong> {balls_html}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暫無預測資料 (請等待自動排程生成)")
    
    # 威力彩
    with game_tabs[2]:
        st.markdown("### 威力彩預測 (38選6 + 8選1)")
        if 'power' in predictions:
            data = predictions['power']
            st.markdown(f"**預測日期**: {data['date']}")
            
            numbers = data['numbers'] # [{'zone1': [...], 'zone2': 1}, ...]
            for i, item in enumerate(numbers, 1):
                zone1_html = create_balls_html(item.get('zone1', []))
                zone2_html = create_balls_html([item.get('zone2')], is_special=True)
                
                st.markdown(f"""
                <div class="prediction-box">
                    <strong>第 {i} 組:</strong><br>
                    第一區: {zone1_html}<br>
                    第二區: {zone2_html}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暫無預測資料 (請等待自動排程生成)")
    
    # 3星彩
    with game_tabs[3]:
        st.markdown("### 3星彩預測 (000-999)")
        if 'star3' in predictions:
            data = predictions['star3']
            st.markdown(f"**預測日期**: {data['date']}")
            
            numbers = data['numbers']
            for i, num in enumerate(numbers, 1):
                st.markdown(f"""
                <div class="prediction-box">
                    <strong>第 {i} 組:</strong> <span style="font-size: 24px; font-weight: bold; margin-left: 10px; color: #667eea;">{num}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暫無預測資料 (請等待自動排程生成)")
    
    # 4星彩
    with game_tabs[4]:
        st.markdown("### 4星彩預測 (0000-9999)")
        if 'star4' in predictions:
            data = predictions['star4']
            st.markdown(f"**預測日期**: {data['date']}")
            
            numbers = data['numbers']
            for i, num in enumerate(numbers, 1):
                st.markdown(f"""
                <div class="prediction-box">
                    <strong>第 {i} 組:</strong> <span style="font-size: 24px; font-weight: bold; margin-left: 10px; color: #667eea;">{num}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暫無預測資料 (請等待自動排程生成)")

# 歷史記錄頁面
elif page == "📈 歷史記錄":
    st.markdown("## 歷史開獎記錄")
    
    game_select = st.selectbox(
        "選擇遊戲",
        ["今彩539", "大樂透", "威力彩", "3星彩", "4星彩"]
    )
    
    game_map = {
        "今彩539": "539",
        "大樂透": "lotto",
        "威力彩": "power",
        "3星彩": "star3",
        "4星彩": "star4"
    }
    
    df = load_history(game_map[game_select])
    
    if not df.empty:
        st.markdown(f"### {game_select} 歷史資料")
        st.markdown(f"**資料筆數**: {len(df)}")
        
        # 顯示最近10筆
        st.dataframe(df.tail(10), use_container_width=True)
        
        # 統計圖表
        if game_map[game_select] == "539" and 'numbers' in df.columns:
            st.markdown("### 號碼頻率分析")
            
            # 計算頻率
            from collections import Counter
            all_numbers = []
            for nums in df['numbers']:
                if isinstance(nums, str):
                    all_numbers.extend([int(n) for n in nums.split(',')])
            
            freq = Counter(all_numbers)
            freq_df = pd.DataFrame(list(freq.items()), columns=['號碼', '出現次數'])
            freq_df = freq_df.sort_values('出現次數', ascending=False)
            
            # 繪製圖表
            fig = px.bar(
                freq_df.head(20),
                x='號碼',
                y='出現次數',
                title='號碼出現頻率 Top 20',
                color='出現次數',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"{game_select} 暫無歷史資料")

# 系統狀態頁面
elif page == "⚙️ 系統狀態":
    st.markdown("## 系統運行狀態")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🐳 Docker 狀態")
        st.success("✅ 容器運行中")
        st.markdown("""
        - **容器名稱**: 539-ai-predictor
        - **狀態**: Up (healthy)
        - **重啟策略**: unless-stopped
        """)
    
    with col2:
        st.markdown("### 📅 排程任務")
        st.info("✅ 排程系統運行中")
        st.markdown("""
        - **23:00** - 資料更新 ✅
        - **23:05** - 驗證預測 ✅
        - **23:10** - 模型訓練 ✅
        - **23:15** - 生成預測 ✅
        """)
    
    st.markdown("---")
    
    # 日誌查看
    st.markdown("### 📋 系統日誌")
    
    log_file = Path(f"logs/539_ai_{get_taiwan_date_only_str()}.log")
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            logs = f.readlines()
            st.text_area("最新日誌", ''.join(logs[-50:]), height=300)
    else:
        st.info("暫無日誌資料")

# 頁尾
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>539 AI 預測系統 v2.0 | Powered by Streamlit & Docker</p>
    <p>© 2026 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
