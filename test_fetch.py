# -*- coding: utf-8 -*-
"""
測試獲取開獎號碼功能
"""
import streamlit as st
from datetime import datetime
from src.auzonet_crawler import fetch_auzonet_single_date

st.title("🧪 測試獲取開獎號碼")

# 日期選擇
test_date = st.date_input(
    "選擇日期",
    value=datetime.now()
)

# 獲取按鈕
if st.button("🔍 測試獲取", type="primary"):
    st.write(f"開始查詢 {test_date}...")
    
    try:
        date_str = test_date.strftime("%Y-%m-%d")
        st.write(f"日期字串: {date_str}")
        
        # 調用 crawler
        st.write("正在調用 crawler...")
        result = fetch_auzonet_single_date(date_str)
        
        st.write(f"Crawler 返回: {result}")
        
        if result:
            st.success(f"✅ 成功! 號碼: {result}")
            # 存儲到 session state
            st.session_state.test_numbers = result
        else:
            st.error("❌ 未找到號碼")
            
    except Exception as e:
        st.error(f"❌ 錯誤: {e}")
        import traceback
        st.code(traceback.format_exc())

# 顯示 session state
st.write("---")
st.write("Session State:")
st.write(st.session_state)
