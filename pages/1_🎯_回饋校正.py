# -*- coding: utf-8 -*-
"""
回饋校正頁面 - 簡化版
"""
import streamlit as st
from datetime import datetime
from src.auzonet_crawler import fetch_auzonet_single_date
from src.prediction_history import PredictionHistory
from src.timezone_utils import get_taiwan_now

st.set_page_config(page_title="回饋校正", page_icon="🎯", layout="wide")

st.title("🎯 回饋校正")
st.markdown("### 輸入實際開獎號碼,幫助 AI 學習優化")

# 初始化 prediction history
prediction_history = PredictionHistory()

# 日期選擇
st.markdown("#### 📅 步驟 1: 選擇開獎日期")
col1, col2 = st.columns([3, 1])

# 檢查是否有待驗證的預測,並解析預測日期
pending_prediction = prediction_history.get_pending_prediction()
if pending_prediction:
    prediction_date_str = pending_prediction.get('prediction_date', '')
    try:
        # 假設格式為 "2026-01-30 週四" 或 "2026-01-30"
        date_part = prediction_date_str.split()[0]
        default_date = datetime.strptime(date_part, "%Y-%m-%d").date()
    except:
        default_date = get_taiwan_now().date()
else:
    default_date = get_taiwan_now().date()

with col1:
    feedback_date = st.date_input(
        "選擇開獎日期",
        value=default_date,  # 使用預測日期或當前日期
        label_visibility="collapsed"
    )
    st.caption("💡 提示: 每週日不開獎")

with col2:
    if st.button("🔍 獲取開獎號碼", use_container_width=True, type="primary"):
        date_str = feedback_date.strftime("%Y-%m-%d")
        st.write(f"正在查詢 {date_str}...")
        
        try:
            result = fetch_auzonet_single_date(date_str)
            if result:
                st.session_state.fetched_numbers = result
                st.success(f"✅ 成功! 號碼: {result}")
                st.rerun()
            else:
                st.error("❌ 找不到該日期的開獎記錄")
        except Exception as e:
            st.error(f"❌ 錯誤: {e}")

st.markdown("---")

# 號碼輸入
st.markdown("#### 🎱 步驟 2: 輸入實際開出號碼")

# 檢查是否有獲取的號碼
if 'fetched_numbers' in st.session_state and st.session_state.fetched_numbers:
    default_values = st.session_state.fetched_numbers
    st.info(f"已自動填入: {default_values}")
else:
    default_values = [None, None, None, None, None]

# 創建號碼輸入框
actual_numbers = []
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        # 設定預設值
        default_val = default_values[i] if (default_values[i] is not None and default_values[i] != 0) else 1
        
        num = st.number_input(
            f"號碼 {i+1}",
            min_value=1,
            max_value=39,
            value=default_val,
            step=1,
            key=f"actual_num_{i}",
            label_visibility="collapsed",
            help=f"請輸入第 {i+1} 個開獎號碼 (1-39)"
        )
        
        # 如果有獲取的號碼,使用獲取的值;否則使用輸入的值
        if 'fetched_numbers' in st.session_state and st.session_state.fetched_numbers and i < len(st.session_state.fetched_numbers):
            actual_numbers.append(st.session_state.fetched_numbers[i])
        elif num and num > 0:
            actual_numbers.append(num)

st.markdown("---")

# 檢查是否有待驗證的預測
pending_prediction = prediction_history.get_pending_prediction()

if pending_prediction:
    st.info(f"📋 您有一個待驗證的預測 ({pending_prediction.get('prediction_date')})")
    st.markdown(f"**預測號碼**: {pending_prediction.get('predicted_numbers')}")

# 提交按鈕
if st.button("✅ 提交回饋", use_container_width=True, type="primary"):
    if len(actual_numbers) != 5:
        st.error("❌ 請輸入 5 個號碼")
    elif len(set(actual_numbers)) != 5:
        st.error("❌ 號碼不能重複")
    else:
        # 如果有待驗證的預測,更新它
        if pending_prediction:
            # 使用 update_actual_result 方法
            prediction_history.update_actual_result(
                prediction_date=pending_prediction.get('prediction_date'),
                actual_numbers=actual_numbers
            )
            
            # 計算命中數顯示
            predicted_numbers = pending_prediction.get('predicted_numbers', [])
            hits = len(set(predicted_numbers) & set(actual_numbers))
            
            st.success(f"✅ 已驗證預測! 命中 {hits}/5 個號碼")
            if hits >= 3:
                st.balloons()
            
            # 🔥 新增: 將開獎資料追加到訓練集
            try:
                import pandas as pd
                from pathlib import Path
                
                train_file = Path('data/539_train.csv')
                if train_file.exists():
                    # 讀取現有訓練資料
                    df_train = pd.read_csv(train_file)
                    
                    # 解析日期
                    prediction_date_str = pending_prediction.get('prediction_date', '')
                    date_part = prediction_date_str.split()[0] if ' ' in prediction_date_str else prediction_date_str
                    
                    # 檢查是否已存在
                    if date_part not in df_train['date'].values:
                        # 創建新記錄
                        new_row = {
                            'date': date_part,
                            'numbers': ','.join([str(n) for n in sorted(actual_numbers)])
                        }
                        
                        # 追加到訓練集
                        df_train = pd.concat([df_train, pd.DataFrame([new_row])], ignore_index=True)
                        
                        # 按日期排序
                        df_train['date'] = pd.to_datetime(df_train['date'])
                        df_train = df_train.sort_values('date').reset_index(drop=True)
                        df_train['date'] = df_train['date'].dt.strftime('%Y-%m-%d')
                        
                        # 儲存
                        df_train.to_csv(train_file, index=False)
                        st.info(f"📊 已更新訓練集: {len(df_train)} 筆")
                    else:
                        st.info(f"📊 訓練集已包含此日期資料")
            except Exception as e:
                st.warning(f"⚠️ 訓練集更新失敗: {e}")
        else:
            # 沒有待驗證的預測,只是記錄開獎號碼
            st.success(f"✅ 已記錄開獎號碼: {sorted(actual_numbers)}")
        
        # 清除 session state
        if 'fetched_numbers' in st.session_state:
            del st.session_state.fetched_numbers
        
        st.rerun()

# 顯示說明
with st.expander("ℹ️ 使用說明"):
    st.markdown("""
    ### 如何使用回饋校正
    
    1. **選擇日期**: 選擇要回饋的開獎日期
    2. **獲取號碼**: 點擊「獲取開獎號碼」從官網自動抓取
    3. **確認號碼**: 檢查自動填入的號碼是否正確
    4. **提交回饋**: 點擊「提交回饋」完成
    
    ### 資料來源
    - 官網: https://lotto.auzonet.com/daily539
    - 自動更新: 每日開獎後即可查詢
    """)
