import streamlit as st
import pandas as pd
import os

# --- 檔案路徑設定 ---
HERB_DB = "tcm_price.xlsx"
GRANULE_DB = "tcm_granules.xlsx"

# --- 1. 讀取數據（快取優化） ---
@st.cache_data
def load_herb_data():
    if not os.path.exists(HERB_DB):
        df = pd.DataFrame({
            "藥名": ["黃柏", "黃芩", "當歸", "川芎", "熟地", "白芍"], 
            "單價": [0.4, 0.5, 0.8, 0.6, 0.7, 0.5]
        })
        df.to_excel(HERB_DB, index=False)
        return df
    return pd.read_excel(HERB_DB)

@st.cache_data
def load_granule_data():
    if not os.path.exists(GRANULE_DB):
        # 建立範例顆粒劑數據
        df = pd.DataFrame({
            "藥名/方劑": ["小柴胡湯", "桂枝湯", "參苓白朮散", "五味子"], 
            "每克單價(g)": [0.644, 0.476, 0.574, 0.784]
        })
        df.to_excel(GRANULE_DB, index=False)
        return df
    return pd.read_excel(GRANULE_DB)

# --- 介面初始化 ---
st.set_page_config(page_title="Samuel 醫師中藥智能計算器", layout="centered")
st.title("🌿 Samuel 醫師中藥智能計算器 (2026 版)")

# --- 2. 狀態與重置計數器初始化 (預設直開 10 行) ---
if 'herb_rows' not in st.session_state:
    st.session_state.herb_rows = 10
if 'granule_rows' not in st.session_state:
    st.session_state.granule_rows = 10

# 獨立的重置計數器，確保清空時畫面徹底刷白
if 'herb_clear' not in st.session_state:
    st.session_state.herb_clear = 0
if 'granule_clear' not in st.session_state:
    st.session_state.granule_clear = 0

# 建立頂部切換頁籤
tab1, tab2 = st.tabs(["🍵 草藥飲片代煎", "💊 濃縮方劑顆粒"])

# ==============================================================================
# 🍵 TAB 1: 草藥飲片代煎
# ==============================================================================
with tab1:
    df_herb = load_herb_data()
    herb_options = [""] + sorted(df_herb["藥名"].tolist())
    herb_price_dict = pd.Series(df_herb.單價.values, index=df_herb.藥名).to_dict()

    st.subheader("草藥處方內容")
    st.caption("💡 提示：輸入關鍵字可快速過濾飲片。")

    t_col1, t_col2, t_col3 = st.columns([4, 2, 2])
    with t_col1: st.markdown("**草藥名稱**")
    with t_col2: st.markdown("**克數 (g)**")
    with t_col3: st.markdown("**成本小計**")

    herb_total_cost = 0.0

    for i in range(st.session_state.herb_rows):
        c1, c2, c3 = st.columns([4, 2, 2])
        suffix = f"{i}_h{st.session_state.herb_clear}"
        
        with c1:
            selected_herb = st.selectbox(f"草藥_{i}", options=herb_options, key=f"herb_name_{suffix}", label_visibility="collapsed")
        with c2:
            gram = st.number_input(f"草藥克數_{i}", min_value=0.0, step=1.0, key=f"herb_gram_{suffix}", label_visibility="collapsed")
        
        if selected_herb and selected_herb in herb_price_dict:
            cost = herb_price_dict[selected_herb] * gram
            herb_total_cost += cost
            with c3: st.write(f"${cost:.2f}")
        else:
            with c3: st.write("$0.00")

    if st.button("➕ 增加草藥味數"):
        st.session_state.herb_rows += 1
        st.rerun()

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        herb_days = st.number_input("劑數 (貼)", min_value=1, value=1, step=1, key="herb_days")
    with col_b:
        st.write(" ")
        use_decoction = st.checkbox("需代煎 (每劑 +$14)", key="use_decoction")

    decoction_fee = 14 if use_decoction else 0
    herb_cost_final = (herb_total_cost + decoction_fee) * herb_days
    herb_retail_final = (herb_total_cost * 4 + decoction_fee) * herb_days

    st.markdown("### 💰 草藥報價結果")
    res1, res2 = st.columns(2)
    res1.metric("總成本 (Cost)", f"${herb_cost_final:.2f}")
    res2.metric("建議零售價 (Retail)", f"${herb_retail_final:.2f}", delta=f"利潤: ${herb_retail_final - herb_cost_final:.2f}")

    if st.button("🧹 清空草藥重填"):
        for key in list(st.session_state.keys()):
            if "herb_name_" in key or "herb_gram_" in key:
                del st.session_state[key]
        st.session_state.herb_rows = 10
        st.session_state.herb_clear += 1
        st.rerun()

# ==============================================================================
# 💊 TAB 2: 濃縮方劑顆粒
# ==============================================================================
with tab2:
    df_granule = load_granule_data()
    # 支援你新做的欄位名稱："藥名/方劑" 與 "每克單價(g)"
    granule_options = [""] + sorted(df_granule["藥名/方劑"].tolist())
    granule_price_dict = pd.Series(df_granule["每克單價(g)"].values, index=df_granule["藥名/方劑"]).to_dict()

    st.subheader("顆粒劑處方內容")
    st.caption("💡 提示：輸入關鍵字可快速過濾方劑或單味顆粒。")

    g_col1, g_col2, g_col3 = st.columns([4, 2, 2])
    with g_col1: st.markdown("**顆粒名稱/方劑**")
    with g_col2: st.markdown("**克數 (g)**")
    with g_col3: st.markdown("**成本小計**")

    granule_total_cost = 0.0

    for i in range(st.session_state.granule_rows):
        c1, c2, c3 = st.columns([4, 2, 2])
        suffix = f"{i}_g{st.session_state.granule_clear}"
        
        with c1:
            selected_granule = st.selectbox(f"顆粒_{i}", options=granule_options, key=f"granule_name_{suffix}", label_visibility="collapsed")
        with c2:
            g_gram = st.number_input(f"顆粒克數_{i}", min_value=0.0, step=1.0, key=f"granule_gram_{suffix}", label_visibility="collapsed")
        
        if selected_granule and selected_granule in granule_price_dict:
            cost = granule_price_dict[selected_granule] * g_gram
            granule_total_cost += cost
            with c3: st.write(f"${cost:.2f}")
        else:
            with c3: st.write("$0.00")

    if st.button("➕ 增加顆粒味數"):
        st.session_state.granule_rows += 1
        st.rerun()

    st.divider()
    # 顆粒劑通常計「天數」而非貼數
    granule_days = st.number_input("服用天數", min_value=1, value=1, step=1, key="granule_days")

    # 顆粒劑計價邏輯：總成本 = 每克成本 * 總克數 * 天數
    granule_cost_final = granule_total_cost * granule_days
    # 零售價維持 4 倍加成
    granule_retail_final = (granule_total_cost * 4) * granule_days

    st.markdown("### 💰 顆粒報價結果")
    gres1, gres2 = st.columns(2)
    gres1.metric("總成本 (Cost)", f"${granule_cost_final:.2f}")
    gres2.metric("建議零售價 (Retail)", f"${granule_retail_final:.2f}", delta=f"利潤: ${granule_retail_final - granule_cost_final:.2f}")

    if st.button("🧹 清空顆粒重填"):
        for key in list(st.session_state.keys()):
            if "granule_name_" in key or "granule_gram_" in key:
                del st.session_state[key]
        st.session_state.granule_rows = 10
        st.session_state.granule_clear += 1
        st.rerun()
