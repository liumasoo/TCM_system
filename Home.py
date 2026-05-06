import streamlit as st

# 設定網頁標題
st.set_page_config(page_title="Samuel 醫師診所管理系統", layout="wide")

st.title("🌿 Samuel 醫師診所管理系統")
st.write("---")
st.info("👋 歡迎，Samuel 醫師。請使用左側邊欄切換不同的功能模組。")

# 這裡可以放一些簡單的診所資訊或今日提醒
st.subheader("診所概況")
col1, col2 = st.columns(2)
with col1:
    st.metric("當前狀態", "執業中")
with col2:
    st.metric("數據存儲", "本地 Excel (去中心化)")