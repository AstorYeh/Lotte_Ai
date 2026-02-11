# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from pathlib import Path

# Import project modules
from src.prediction_history import prediction_history

# Page configuration
st.set_page_config(
    page_title="性能追蹤 - 539 AI",
    page_icon="📊",
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
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
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
</style>
""", unsafe_allow_html=True)

# Main content
st.markdown("# 📊 性能追蹤")
st.markdown("### 追蹤 AI 模型的歷史表現")

# 載入歷史記錄
history = prediction_history.get_all_predictions()

# 輔助函數:將 hits 轉換為數字
def get_hits_count(prediction):
    """取得命中數,處理列表和數字兩種格式"""
    hits = prediction.get('hits', 0)
    if isinstance(hits, list):
        return len(hits)
    elif isinstance(hits, int):
        return hits
    else:
        return 0

if history:
    # 統計數據
    total = len(history)
    verified = len([p for p in history if p.get('status') == 'verified'])
    pending = len([p for p in history if p.get('status') == 'pending'])
    
    # 計算統計指標
    if verified > 0:
        verified_predictions = [p for p in history if p.get('status') == 'verified']
        total_hits = sum(get_hits_count(p) for p in verified_predictions)
        avg_hits = total_hits / verified
        
        # 計算 2+ 命中率
        hit_2plus = len([p for p in verified_predictions if get_hits_count(p) >= 2])
        hit_2plus_rate = hit_2plus / verified * 100
        
        # 計算 3+ 命中率 (賺錢率)
        hit_3plus = len([p for p in verified_predictions if get_hits_count(p) >= 3])
        hit_3plus_rate = hit_3plus / verified * 100
    else:
        avg_hits = 0
        hit_2plus_rate = 0
        hit_3plus_rate = 0
    
    # 顯示統計卡片
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("總預測次數", total)
    
    with col2:
        st.metric("已驗證", verified, delta=f"{pending} 待驗證")
    
    with col3:
        st.metric("平均命中數", f"{avg_hits:.2f}")
    
    with col4:
        st.metric("2+ 命中率", f"{hit_2plus_rate:.1f}%", 
                 delta=f"目標: 20.65%", 
                 delta_color="normal" if hit_2plus_rate >= 20.65 else "inverse")
    
    with col5:
        st.metric("賺錢率 (3+)", f"{hit_3plus_rate:.1f}%",
                 delta=f"目標: 1.31%",
                 delta_color="normal" if hit_3plus_rate >= 1.31 else "inverse")
    
    st.markdown("---")
    
    # 性能對比
    st.markdown("### 🎯 性能對比")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("#### 📈 當前表現")
        st.markdown(f"""
        - **2+ 命中率**: {hit_2plus_rate:.2f}%
        - **平均命中數**: {avg_hits:.2f}
        - **賺錢率**: {hit_3plus_rate:.2f}%
        - **已驗證期數**: {verified}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("#### 🎯 目標基準 (方案 A)")
        st.markdown("""
        - **2+ 命中率**: 20.65%
        - **平均命中數**: 0.89
        - **賺錢率**: 1.31%
        - **訓練期數**: 305
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 歷史記錄表
    st.markdown("### 📋 歷史預測記錄")
    
    # 準備顯示數據
    display_data = []
    for p in history:
        display_data.append({
            '日期': p.get('prediction_date', 'N/A'),
            '預測號碼': ', '.join([f"{n:02d}" for n in p.get('predicted_numbers', [])]),
            '實際號碼': ', '.join([f"{n:02d}" for n in p.get('actual_numbers', [])]) if p.get('actual_numbers') else '待開獎',
            '命中數': get_hits_count(p) if p.get('status') == 'verified' else 'N/A',
            '狀態': '✅ 已驗證' if p.get('status') == 'verified' else '⏳ 待驗證'
        })
    
    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # 趨勢圖
    if verified > 0:
        st.markdown("### 📈 命中率趨勢")
        
        verified_history = [p for p in history if p.get('status') == 'verified']
        dates = [p.get('prediction_date') for p in verified_history]
        hits = [get_hits_count(p) for p in verified_history]
        
        # 創建趨勢圖
        fig = go.Figure()
        
        # 命中數折線圖
        fig.add_trace(go.Scatter(
            x=dates,
            y=hits,
            mode='lines+markers',
            name='命中數',
            line=dict(color='#00d4ff', width=3),
            marker=dict(size=10, symbol='circle')
        ))
        
        # 添加平均線
        fig.add_hline(
            y=avg_hits, 
            line_dash="dash", 
            line_color="#00ff88",
            annotation_text=f"平均: {avg_hits:.2f}",
            annotation_position="right"
        )
        
        # 添加目標線
        fig.add_hline(
            y=0.89,  # 方案 A 的平均命中數
            line_dash="dot",
            line_color="rgba(255,255,255,0.3)",
            annotation_text="目標: 0.89",
            annotation_position="left"
        )
        
        fig.update_layout(
            title="命中數趨勢分析",
            xaxis_title="預測日期",
            yaxis_title="命中數",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500,
            hovermode='x unified',
            yaxis=dict(range=[0, 5])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 命中分布圖
        st.markdown("### 📊 命中數分布")
        
        hit_counts = [0, 0, 0, 0, 0, 0]  # 0-5 顆
        for p in verified_history:
            hit_count = get_hits_count(p)
            if 0 <= hit_count <= 5:
                hit_counts[hit_count] += 1
        
        fig2 = go.Figure()
        
        colors = ['#ff6b6b', '#ffa500', '#ffeb3b', '#4caf50', '#2196f3', '#9c27b0']
        
        fig2.add_trace(go.Bar(
            x=['0 顆', '1 顆', '2 顆', '3 顆', '4 顆', '5 顆'],
            y=hit_counts,
            marker=dict(
                color=colors,
                line=dict(color='rgba(255,255,255,0.3)', width=1)
            ),
            text=[f"{count} ({count/verified*100:.1f}%)" if verified > 0 else "0" for count in hit_counts],
            textposition='outside'
        ))
        
        fig2.update_layout(
            title="命中數分布統計",
            xaxis_title="命中數",
            yaxis_title="次數",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 📝 尚無歷史預測記錄
    
    開始使用主頁面的預測功能,系統會自動記錄每次預測結果。
    
    **如何開始**:
    1. 返回主頁面
    2. 點擊「🚀 開始預測」
    3. 驗證預測結果
    4. 回到此頁面查看統計
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.5); padding: 20px;">
    <p>📊 性能追蹤 | 539 AI 預測大師</p>
</div>
""", unsafe_allow_html=True)
