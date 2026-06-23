import streamlit as st
import pandas as pd
import os

# --- 讀取價格數據 ---
DB_PATH = "tcm_price.xlsx"

def load_data():
    if not os.path.exists(DB_PATH):
        # 建立範例數據，供你參考格式
        df = pd.DataFrame({
            "藥名": ["黃柏", "黃芩", "當歸", "川芎", "熟地", "白芍"], 
            "單價": [0.4, 0.5, 0.8, 0.6, 0.7, 0.5]
        })
        df.to_excel(DB_PATH, index=False)
        return df
    return pd.read_excel(DB_PATH)

st.set_page_config(page_title="Samuel 醫師代煎計算器", layout="centered")
st.title("🍵 中央藥房代煎報價工具 (快速搜尋版)")

df_price = load_data()
# 取得所有藥名清單，並加入一個空選項放在最前面
herb_options = [""] + sorted(df_price["藥名"].tolist())
# 轉成字典方便快速查詢價格
price_dict = pd.Series(df_price.單價.values, index=df_price.藥名).to_dict()

# --- 介面設計 ---
if 'rows' not in st.session_state:
    st.session_state.rows = 10

st.subheader("處方內容")
st.caption("💡 提示：在輸入框直接打字（如「黃」），即可快速過濾藥材。")

total_cost = 0.0

# 建立輸入列表
for i in range(st.session_state.rows):
    c1, c2, c3 = st.columns([4, 2, 2])
    with c1:
        # 使用 selectbox 代替 text_input，實現模糊搜尋功能
        selected_herb = st.selectbox(
            f"藥材 {i+1}", 
            options=herb_options, 
            key=f"herb_{i}",
            label_visibility="collapsed" # 隱藏標籤令介面更簡潔
        )
    with c2:
        gram = st.number_input(f"克數", min_value=0.0, step=1.0, key=f"gram_{i}", label_visibility="collapsed")
    
    # 計算該味藥成本
    if selected_herb and selected_herb in price_dict:
        unit_price = price_dict[selected_herb]
        cost = unit_price * gram
        total_cost += cost
        with c3:
            st.write(f"成本: ${cost:.1f}")

if st.button("➕ 增加藥味"):
    st.session_state.rows += 1
    st.rerun()

st.divider()

# --- 總數計算 ---
col_a, col_b = st.columns(2)
with col_a:
    days = st.number_input("劑數 (貼)", min_value=1, value=1)
with col_b:
    st.write("") # 調整對齊
    use_decoction = st.checkbox("需代煎 (每劑 +$14)")

# 計算邏輯
decoction_fee = 14 if use_decoction else 0
# 藥材總成本
total_herb_cost = total_cost * days
# 零售總價 = (藥材成本 * 4 + 代煎費) * 劑數
grand_total_retail = (total_cost * 4 + decoction_fee) * days
# 總成本 = (藥材成本 + 代煎費) * 劑數
grand_total_cost = (total_cost + decoction_fee) * days

# --- 顯示結果 ---
st.markdown("---")
res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric("總成本 (Cost)", f"${grand_total_cost:.1f}")
with res_col2:
    st.metric("建議零售價 (Retail)", f"${grand_total_retail:.1f}", delta=f"利潤: ${grand_total_retail - grand_total_cost:.1f}")

if st.button("🧹 清空重填"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
        st.session_state.rows = 10 # 確保重置後依然維持預設的 10 列
    st.rerun()
