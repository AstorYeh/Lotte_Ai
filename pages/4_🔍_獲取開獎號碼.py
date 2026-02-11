# -*- coding: utf-8 -*-
"""
快速獲取開獎號碼工具
"""
import streamlit as st
from datetime import datetime
from src.auzonet_crawler import fetch_auzonet_single_date
from src.timezone_utils import get_taiwan_now

st.set_page_config(page_title="獲取開獎號碼", page_icon="🔍", layout="centered")

st.title("🔍 獲取開獎號碼")
st.markdown("### 從官網快速查詢開獎號碼")

# 日期選擇
col1, col2 = st.columns([3, 1])

with col1:
    query_date = st.date_input(
        "選擇開獎日期",
        value=get_taiwan_now(),
        help="選擇要查詢的開獎日期"
    )
    st.caption("💡 提示: 每週日不開獎")

with col2:
    st.write("")  # 對齊
    fetch_button = st.button("🔍 查詢", use_container_width=True, type="primary")

if fetch_button:
    date_str = query_date.strftime("%Y-%m-%d")
    
    with st.spinner(f"正在查詢 {date_str}..."):
        try:
            result = fetch_auzonet_single_date(date_str)
            
            if result:
                st.success(f"✅ 查詢成功!")
                
                # 顯示號碼
                st.markdown("### 🎱 開獎號碼")
                cols = st.columns(5)
                for i, num in enumerate(result):
                    with cols[i]:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin: 5px;">
                            <h1 style="color: white; margin: 0; font-size: 48px;">{num:02d}</h1>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 複製用的文字
                st.markdown("---")
                numbers_str = ', '.join([str(n) for n in result])
                st.code(numbers_str, language=None)
                st.caption("👆 點擊上方可複製號碼")
                
            else:
                st.warning(f"⚠️ 找不到 {date_str} 的開獎記錄")
                st.info("""
                💡 **可能原因**:
                - 該日期尚未開獎
                - 週日不開獎
                - 網站暫時無法訪問
                """)
                
        except Exception as e:
            st.error(f"❌ 查詢失敗: {e}")
            with st.expander("查看詳細錯誤"):
                import traceback
                st.code(traceback.format_exc())

# 資料來源說明
st.markdown("---")
with st.expander("ℹ️ 資料來源"):
    st.markdown("""
    ### 資料來源
    
    **官方網站**: https://lotto.auzonet.com/daily539
    
    ### 開獎時間
    
    - **每週一至週六** 晚上 8:30 開獎
    - **每週日** 不開獎
    
    ### 使用說明
    
    1. 選擇要查詢的日期
    2. 點擊「查詢」按鈕
    3. 等待系統從官網抓取資料
    4. 查看開獎號碼並可複製使用
    """)

# 最近開獎記錄
st.markdown("---")
st.markdown("### 📅 快速查詢")

quick_dates = []
current = get_taiwan_now()
for i in range(7):
    check_date = datetime(current.year, current.month, current.day) - datetime.timedelta(days=i)
    if check_date.weekday() != 6:  # 不是週日
        quick_dates.append(check_date)
    if len(quick_dates) >= 5:
        break

cols = st.columns(5)
for i, qdate in enumerate(quick_dates):
    with cols[i]:
        if st.button(qdate.strftime("%m/%d"), use_container_width=True, key=f"quick_{i}"):
            st.session_state.query_date = qdate
            st.rerun()
