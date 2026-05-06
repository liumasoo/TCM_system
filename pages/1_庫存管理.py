import streamlit as st
import pandas as pd
import os

# --- 設定本地數據庫路徑 ---
DB_PATH = "tcm_data.xlsx"

def load_data():
    if not os.path.exists(DB_PATH):
        # 如果檔案不存在，建立初始數據
        df = pd.DataFrame(columns=["藥名", "單價_每克", "目前庫存", "安全水位"])
        df.to_excel(DB_PATH, index=False)
        return df
    return pd.read_excel(DB_PATH)

def save_data(df):
    df.to_excel(DB_PATH, index=False)

# --- 介面設計 ---
st.set_page_config(page_title="Samuel 醫師助手", layout="wide")
st.title("🌿 中醫診所成本與庫存助手")

df_inv = load_data()

col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. 診症開方計算")
    # 選擇藥材（支援多選）
    selected_herbs = st.multiselect("選擇藥材", df_inv["藥名"].tolist())
    
    prescription = {}
    total_cost = 0.0
    
    for herb in selected_herbs:
        herb_info = df_inv[df_inv["藥名"] == herb].iloc[0]
        gram = st.number_input(f"{herb} (g)", min_value=0.0, step=1.0, key=herb)
        cost = gram * herb_info["單價_每克"]
        total_cost += cost
        prescription[herb] = gram
        st.caption(f"庫存剩餘: {herb_info['目前庫存']}g | 本項成本: ${cost:.2f}")

    st.subheader(f"💰 總藥費成本: ${total_cost:.2f}")
    
    days = st.number_input("劑數 (貼/日)", min_value=1, value=1)
    st.info(f"總處方成本 (共 {days} 劑): ${total_cost * days:.2f}")

    if st.button("確認處方並扣減庫存"):
        for herb, gram in prescription.items():
            total_reduction = gram * days
            df_inv.loc[df_inv["藥名"] == herb, "目前庫存"] -= total_reduction
        save_data(df_inv)
        st.success("✅ 庫存已更新！")
        st.rerun()

with col2:
    st.header("2. 庫存概覽與警報")
    
    # 自動偵測欄位名稱 (防止 "目前庫存" vs "庫存" 導致崩潰)
    stock_col = "目前庫存" if "目前庫存" in df_inv.columns else "庫存"
    
    # 顯示低庫存警告
    if stock_col in df_inv.columns and "安全水位" in df_inv.columns:
        low_stock = df_inv[df_inv[stock_col] <= df_inv["安全水位"]]
        if not low_stock.empty:
            st.warning("⚠️ 以下藥材庫存不足，請及時補貨：")
            st.table(low_stock[["藥名", stock_col, "安全水位"]])
    
    st.subheader("完整庫存表")
    st.dataframe(df_inv, use_container_width=True)

    # 簡單的藥價/庫存更新功能
    with st.expander("📝 快速修改藥價或補貨"):
        target_herb = st.selectbox("選取藥名", df_inv["藥名"].tolist(), key="update")
        new_price = st.number_input("新單價 (每克)", value=float(df_inv.loc[df_inv["藥名"] == target_herb, "單價_每克"].iloc[0]))
        add_stock = st.number_input("補貨量 (g)", value=0.0)
        
        if st.button("更新數據"):
            df_inv.loc[df_inv["藥名"] == target_herb, "單價_每克"] = new_price
            df_inv.loc[df_inv["藥名"] == target_herb, "目前庫存"] += add_stock
            save_data(df_inv)
            st.success(f"{target_herb} 更新成功")
            st.rerun()