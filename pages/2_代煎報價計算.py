import streamlit as st
import pandas as pd
import os

# --- 讀取價格數據 ---
DB_PATH = "tcm_price.xlsx"

@st.cache_data
def load_data():
    if not os.path.exists(DB_PATH):
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
herb_options = [""] + sorted(df_price["藥名"].tolist())
price_dict = pd.Series(df_price.單價.values, index=df_price.藥名).to_dict()

# --- 狀態與重置計數器初始化 ---
if 'rows' not in st.session_state:
    st.session_state.rows = 10

# 💡 引入一個重置版本號，用來強制刷清 UI 元件
if 'clear_counter' not in st.session_state:
    st.session_state.clear_counter = 0

st.subheader("處方內容")
st.caption("💡 提示：在輸入框直接打字（如「黃」），即可快速過濾藥材。")

# 建立表格欄位標題
t_col1, t_col2, t_col3 = st.columns([4, 2, 2])
with t_col1: st.markdown("**藥材名稱**")
with t_col2: st.markdown("**克數 (g)**")
with t_col3: st.markdown("**成本小計**")

total_cost = 0.0

# 建立輸入列表
for i in range(st.session_state.rows):
    c1, c2, c3 = st.columns([4, 2, 2])
    
    # 💡 透過在 key 後面綁定 clear_counter，只要 counter 變動，元件就會徹底重置
    current_key_suffix = f"{i}_v{st.session_state.clear_counter}"
    
    with c1:
        selected_herb = st.selectbox(
            f"藥材 {i+1}", 
            options=herb_options, 
            key=f"herb_{current_key_suffix}",
            label_visibility="collapsed"
        )
    with c2:
        gram = st.number_input(
            f"克數_{i}", 
            min_value=0.0, 
            step=1.0, 
            key=f"gram_{current_key_suffix}", 
            label_visibility="collapsed"
        )
    
    # 計算該味藥成本
    if selected_herb and selected_herb in price_dict:
        unit_price = price_dict[selected_herb]
        cost = unit_price * gram
        total_cost += cost
        with c3:
            st.write(f"${cost:.2f}")
    else:
        with c3:
            st.write("$0.00")

if st.button("➕ 增加藥味"):
    st.session_state.rows += 1
    st.rerun()

st.divider()

# --- 總數計算 ---
col_a, col_b = st.columns(2)
with col_a:
    days = st.number_input("劑數 (貼)", min_value=1, value=1, step=1)
with col_b:
    st.write(" ") 
    use_decoction = st.checkbox("需代煎 (每劑 +$14)")

# 計算邏輯
decoction_fee = 14 if use_decoction else 0
grand_total_cost = (total_cost + decoction_fee) * days
grand_total_retail = (total_cost * 4 + decoction_fee) * days
profit = grand_total_retail - grand_total_cost

# --- 顯示結果 ---
st.markdown("### 💰 報價結果")
res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric("總成本 (Cost)", f"${grand_total_cost:.2f}")
with res_col2:
    st.metric("建議零售價 (Retail)", f"${grand_total_retail:.2f}", delta=f"利潤: ${profit:.2f}")

# --- 清空重填按鈕（徹底修復版） ---
if st.button("🧹 清空重填"):
    # 1. 清除所有舊的輸入資料
    for key in list(st.session_state.keys()):
        if key not in ['clear_counter']: # 保留計數器本身
            del st.session_state[key]
            
    # 2. 重新固定初始列數為 10 行
    st.session_state.rows = 10 
    
    # 3. 💡 將計數器加 1，強制讓下一次渲染時的所有輸入框完全變回全新空白
    st.session_state.clear_counter += 1
    st.rerun()
