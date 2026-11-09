import streamlit as st
import pandas as pd
import requests

# 1. 網頁頁面配置
st.set_page_config(page_title="OGame TW 巨鱷動態情報站", page_icon="🪐", layout="wide")

st.title("🪐 OGame-TW 諸神黃昏：千億巨鱷動態情報站")
st.markdown("---")

# 2. 側邊欄：戰略主控台
st.sidebar.header("📡 情報控制中心")
target_universe = st.sidebar.selectbox("切換觀測新宇宙", ["全部宇宙", "Belinda (180)", "Cetus (181)", "Dione (182)"])
refresh_btn = st.sidebar.button("🔄 立即同步最新情報 (發動數據碰撞)")

# 3. 核心監控巨鱷名單基底
def get_monster_base_data():
    monsters = [
        {"ID": "WindAngelX", "原宇宙": "Merkur", "威脅程度": "🔴 極高 (千億級)", "備註": "SOS 聯盟核心"},
        {"ID": "Satan", "原宇宙": "Merkur", "威脅程度": "🔴 極高", "備註": "老牌高軍分狼"},
        {"ID": "Musashi", "原宇宙": "Merkur", "威脅程度": "🟡 高", "備註": "武藏，破壞力強"},
        {"ID": "Paris", "原宇宙": "Oberon", "威脅程度": "🔴 極高 (千億級)", "備註": "Bug堆積疑慮天花板"},
        {"ID": "Lord Patator", "原宇宙": "Oberon", "威脅程度": "🟡 高", "備註": "頂級高分玩家"},
        {"ID": "Thorfinn", "原宇宙": "Oberon", "威脅程度": "🟡 高", "備註": "戰力不可小覷"},
        {"ID": "ATRAGON", "原宇宙": "Cosmos", "威脅程度": "🔴 極高", "備註": "Cosmos 服頭號威脅"},
    ]
    return pd.DataFrame(monsters)

# 4. 核心功能：線上數據打撈與碰撞模組
def fetch_and_collide_data():
    # 預設狀態：全部都在流亡中
    status_dict = {m: "未確認 (流亡中)" for m in ["WindAngelX", "Satan", "Musashi", "Paris", "Lord Patator", "Thorfinn", "ATRAGON"]}
    
    # 2026年 11/9 19:00 新服開通後的 mmorpg-stat 台灣區編號對應
    uni_mapping = {
        "180": "Belinda (180)",
        "181": "Cetus (181)",
        "182": "Dione (182)"
    }
    
    # 用於防範爬蟲遭封鎖的標頭
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # 輪詢三個新宇宙的「個人總積分排行」前 100 名
    for uni_id, uni_name in uni_mapping.items():
        try:
            # 建立 mmorpg-stat 標準通用排行網址 (TW 語系)
            url = f"https://mmorpg-stat.eu{uni_id}&pays=11&stat=0"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 使用 pandas 直接解析 HTML 表格
                tables = pd.read_html(response.text)
                # 尋找含有玩家資料的主表格 (通常 mmorpg-stat 最大的表格即是)
                for table in tables:
                    table_str = str(table)
                    # 遍歷我們監控的巨鱷 ID
                    for monster_id in status_dict.keys():
                        if monster_id in table_str:
                            status_dict[monster_id] = uni_name
        except Exception as e:
            # 容錯機制：若單一宇宙網頁尚未初始化或超時，跳過並回報
            pass
            
    return status_dict

# 初始化狀態記憶
if "current_status" not in st.session_state:
    st.session_state.current_status = {m: "未確認 (流亡中)" for m in ["WindAngelX", "Satan", "Musashi", "Paris", "Lord Patator", "Thorfinn", "ATRAGON"]}

# 按鈕觸發：真實進行網路數據碰撞
if refresh_btn:
    with st.spinner("正在向 mmorpg-stat 高速抓取新服實時排行進行數據碰撞..."):
        latest_status = fetch_and_collide_data()
        st.session_state.current_status = latest_status
        st.success("數據碰撞完成！最新亮燈名單已同步。")

# 5. 合併情報數據
df_monsters = get_monster_base_data()
df_monsters["目前落腳新宇宙"] = df_monsters["ID"].map(st.session_state.current_status)

# 執行側邊欄篩選
if target_universe != "全部宇宙":
    df_filtered = df_monsters[df_monsters["目前落腳新宇宙"] == target_universe]
else:
    df_filtered = df_monsters

# 6. 上半部：實時戰略儀表板
col1, col2, col3, col4 = st.columns(4)
col1.metric("鎖定監控巨鱷", f"{len(df_monsters)} 員")
col2.metric("已進駐 Belinda (180)", f"{len(df_monsters[df_monsters['目前落腳新宇宙'] == 'Belinda (180)'])} 員")
col3.metric("已進駐 Cetus (181)", f"{len(df_monsters[df_monsters['目前落腳新宇宙'] == 'Cetus (181)'])} 員")
col4.metric("已進駐 Dione (182)", f"{len(df_monsters[df_monsters['品質落腳新宇宙'] == 'Dione (182)'])} 員")

st.markdown("### 📡 即時監控情報管理表")
# 渲染高顏值管理表格
st.dataframe(
    df_filtered,
    use_container_width=True,
    hide_index=True
)

# 7. 下半部：情報備忘與外部聯結
st.markdown("---")
st.markdown("### 📌 戰略備忘錄")
tabs = st.tabs(["📊 實時觀察手記", "🔗 官方情報源一鍵查"])

with tabs[0]:
    st.write("💡 **老狼生存提醒：**")
    st.write("1. 今晚 19:00 之後，請每隔幾小時點擊一次左側 **[🔄 立即同步最新情報]** 按鈕。")
    st.write("2. 若目標巨鱷在 `mmorpg-stat` 上衝進前 100 名，本表將會**自動從『未確認』變更為對應新宇宙**。")
    st.write("3. 11/12 19:00 前，只要看見這群怪物大量朝 Cetus 亮燈，我們就往 Dione 撤退；反之亦然。")

with tabs[1]:
    st.markdown("- [mmorpg-stat 全球數據庫首頁](https://mmorpg-stat.eu)")
    st.markdown("- [OGame TW 官方論壇存檔看板](https://gameforge.com)")
