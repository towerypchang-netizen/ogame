import streamlit as st
import pandas as pd
import requests

# 1. 網頁頁面配置
st.set_page_config(page_title="OGame TW 巨鱷動態情報站", page_icon="🪐", layout="wide")

st.markdown("### 🪐 OGame-TW 諸神黃昏：千億巨鱷動態情報站")
st.markdown("---")

# 2. 側邊欄：戰略主控台
st.sidebar.header("📡 情報控制中心")
target_universe = st.sidebar.selectbox("切換觀測新宇宙", ["全部宇宙", "Belinda (180)", "Cetus (181)", "Dione (182)"])
refresh_btn = st.sidebar.button("🔄 立即同步最新情報 (發動數據碰撞)")

# 3. 核心監控巨鱷名單基底 (已整合全新22位群鱷名單，並自動去重)
def get_monster_base_data():
    monsters = [
        # === Merkur 服 / SOS 陣列及其死盟 ===
        {"ID": "WindAngelX", "原宇宙": "Merkur", "威脅程度": "🔴 極高 (千億級)", "備註": "SOS 聯盟核心"},
        {"ID": "Satan", "原宇宙": "Merkur", "威脅程度": "🔴 極高", "備註": "老牌高軍分狼"},
        {"ID": "Musashi", "原宇宙": "Merkur", "威脅程度": "🟡 高", "備註": "武藏，破壞力強"},
        {"ID": "Coon", "原宇宙": "Merkur", "威脅程度": "🟡 高", "備註": "Merkur 指標戰力"},
        {"ID": "BabyShark dododo", "原宇宙": "Merkur", "威脅程度": "🟡 高", "備註": "Merkur 指標戰力"},
        {"ID": "Captain Teemo", "原宇宙": "Merkur", "威脅程度": "🔵 中高", "備註": "Merkur 核心編隊"},
        {"ID": "Lucifer", "原宇宙": "Merkur", "威脅程度": "🔵 中高", "備註": "Merkur 核心編隊"},
        {"ID": "TumaNaomi", "原宇宙": "Merkur", "威脅程度": "🔵 中高", "備註": "Merkur 核心編隊"},
        {"ID": "cotyledon", "原宇宙": "Merkur", "威脅程度": "🔵 中高", "備註": "Merkur 核心編隊"},
        {"ID": "tom12345", "原宇宙": "Merkur", "威脅程度": "🔵 中高", "備註": "Merkur 核心編隊"},
        {"ID": "yoshino", "原宇宙": "Merkur", "威脅程度": "🔵 中高", "備註": "Merkur 核心編隊"},
        {"ID": "Hambeard", "原宇宙": "Merkur", "威脅程度": "🔵 中高", "備註": "Merkur 核心編隊"},
        {"ID": "Slime", "原宇宙": "Merkur", "威脅程度": "🔵 中高", "備註": "Merkur 核心編隊"},
        
        # === Oberon 服 / 頂天神仙陣列 ===
        {"ID": "Paris", "原宇宙": "Oberon", "威脅程度": "🔴 極高 (千億級)", "備註": "Bug堆積疑慮天花板"},
        {"ID": "Glauconome", "原宇宙": "Oberon", "威脅程度": "🟡 高", "備註": "Oberon 指標核心"},
        {"ID": "CCTV77", "原宇宙": "Oberon", "威脅程度": "🟡 高", "備註": "Oberon 核心編隊"},
        {"ID": "Lord Patator", "原宇宙": "Oberon", "威脅程度": "🟡 高", "備註": "頂級高分玩家"},
        {"ID": "Thorfinn", "原宇宙": "Oberon", "威脅程度": "🟡 高", "備註": "戰力不可小覷"},
        
        # === Cosmos 服 / 頭號威脅陣列 ===
        {"ID": "ATRAGON", "原宇宙": "Cosmos", "威脅程度": "🔴 極高", "備註": "Cosmos 服頭號威脅"},
        {"ID": "Kinopio", "原宇宙": "Cosmos", "威脅程度": "🟡 高", "備註": "Cosmos 指標核心"},
        {"ID": "FUIYOH", "原宇宙": "Cosmos", "威脅程度": "🟡 高", "備註": "Cosmos 核心玩家"},
        {"ID": "Chief Halo", "原宇宙": "Cosmos", "威脅程度": "🔵 中高", "備註": "Cosmos 核心玩家"},
        {"ID": "President Zenith", "原宇宙": "Cosmos", "威脅程度": "🔵 中高", "備註": "Cosmos 核心玩家"}
    ]
    return pd.DataFrame(monsters)

# 4. 核心功能：線上數據打撈與碰撞模組
def fetch_and_collide_data():
    base_df = get_monster_base_data()
    status_dict = {m: "未確認 (流亡中)" for m in base_df["ID"].tolist()}
    
    uni_mapping = {
        "180": "Belinda (180)",
        "181": "Cetus (181)",
        "182": "Dione (182)"
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for uni_id, uni_name in uni_mapping.items():
        try:
            # 建立 mmorpg-stat 台灣區最新服排行網址
            url = f"https://mmorpg-stat.eu{uni_id}&pays=11&stat=0"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                tables = pd.read_html(response.text)
                for table in tables:
                    table_str = str(table)
                    for monster_id in status_dict.keys():
                        if monster_id in table_str:
                            status_dict[monster_id] = uni_name
        except Exception as e:
            pass
            
    return status_dict

# 5. 初始化與狀態記憶 (動態配對，防止名單去重漏抓)
if "current_status" not in st.session_state:
    base_df = get_monster_base_data()
    st.session_state.current_status = {m: "未確認 (流亡中)" for m in base_df["ID"].tolist()}

# 按鈕觸發：抓取新服實時數據
if refresh_btn:
    with st.spinner("正在向 mmorpg-stat 高速抓取新服實時排行進行數據碰撞..."):
        latest_status = fetch_and_collide_data()
        st.session_state.current_status = latest_status
        st.success("數據碰撞完成！最新亮燈名單已同步。")

# 整合最新動態情報
df_monsters = get_monster_base_data()
df_monsters["目前落腳新宇宙"] = df_monsters["ID"].map(st.session_state.current_status)

# 執行側邊欄篩選
if target_universe != "全部宇宙":
    df_filtered = df_monsters[df_monsters["目前落腳新宇宙"] == target_universe]
else:
    df_filtered = df_monsters

# 6. 上半部：實時戰略儀表板 (純 HTML/CSS 降維流，100% 精準縮小)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div style="text-align: left;"><span style="font-size: 13px; color: #b0b3b8;">鎖定監控巨鱷</span><br><span style="font-size: 22px; font-weight: 700; color: white;">{len(df_monsters)} 員</span></div>', unsafe_allow_html=True)

with col2:
    count_b = len(df_monsters[df_monsters['currently_status'] == 'Belinda (180)'] if 'currently_status' in locals() else df_monsters[df_monsters['目前落腳新宇宙'] == 'Belinda (180)'])
    st.markdown(f'<div style="text-align: left;"><span style="font-size: 13px; color: #b0b3b8;">已進駐 Belinda (180)</span><br><span style="font-size: 22px; font-weight: 700; color: white;">{count_b} 員</span></div>', unsafe_allow_html=True)

with col3:
    count_c = len(df_monsters[df_monsters['currently_status'] == 'Cetus (181)'] if 'currently_status' in locals() else df_monsters[df_monsters['目前落腳新宇宙'] == 'Cetus (181)'])
    st.markdown(f'<div style="text-align: left;"><span style="font-size: 13px; color: #b0b3b8;">已進駐 Cetus (181)</span><br><span style="font-size: 22px; font-weight: 700; color: white;">{count_c} 員</span></div>', unsafe_allow_html=True)

with col4:
    count_d = len(df_monsters[df_monsters['currently_status'] == 'Dione (182)'] if 'currently_status' in locals() else df_monsters[df_monsters['目前落腳新宇宙'] == 'Dione (182)'])
    st.markdown(f'<div style="text-align: left;"><span style="font-size: 13px; color: #b0b3b8;">已進駐 Dione (182)</span><br><span style="font-size: 22px; font-weight: 700; color: white;">{count_d} 員</span></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 7. 中半部：即時情報管理表格
st.markdown("### 🪟 即時監控情報管理表")
st.dataframe(
    df_filtered,
    use_container_width=True,
    hide_index=True
)

# 8. 下半部：情報備忘與外部聯結
st.markdown("---")
st.markdown("### 📌 戰略備忘錄")
tabs = st.tabs(["📊 實時觀察手記", "🔗 官方情報源一鍵查"])

with tabs:
    st.write("💡 **老狼生存提醒：**")
    st.write("1. 今晚 19:00 之後，請每隔幾小時點擊一次左側 **[🔄 立即同步最新情報]** 按鈕。")
    st.write("2. 若目標巨鱷在 `mmorpg-stat` 上衝進前 100 名，本表將會**自動從『未確認』變更為對應新宇宙**。")
    st.write("3. 11/12 19:00 前，只要看見這群怪物大量朝 Cetus 亮燈，我們就往 Dione 撤退；反之亦然。")

with tabs:
    st.markdown("- [mmorpg-stat 全球數據庫首頁](https://mmorpg-stat.eu)")
    st.markdown("- [OGame TW 官方論壇存檔看板](https://gameforge.com)")
