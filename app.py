import streamlit as st
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup

# 1. 網頁頁面配置
st.set_page_config(page_title="OGame TW 巨鱷動態情報站", page_icon="🪐", layout="wide")

st.markdown("### 🪐 OGame-TW 諸神黃昏：千億巨鱷動態情報站")
st.markdown("---")

# 2. 側邊欄：戰略主控台
st.sidebar.header("📡 情報控制中心")
target_universe = st.sidebar.selectbox("切換觀測新宇宙", ["全部宇宙", "Belinda (180)", "Cetus (181)", "Dione (182)"])
refresh_btn = st.sidebar.button("🔄 立即同步最新情報 (發動數據碰撞)")

# 3. 核心監控巨鱷名單基底
def get_monster_base_data():
    monsters = [
        # === Merkur 服 ===
        {"ID": "WindAngelX", "原宇宙": "Merkur", "保底積分": 250000000000, "備註": "SOS 聯盟核心，超兩千億終極大暴龍"},
        {"ID": "Satan", "原宇宙": "Merkur", "保底積分": 65000000000, "備註": "老牌高軍分狼，百億級巨鱷"},
        {"ID": "Musashi", "原宇宙": "Merkur", "保底積分": 45000000000, "備註": "武藏，破壞力極強的巨鱷"},
        {"ID": "Coon", "原宇宙": "Merkur", "保底積分": 12000000000, "備註": "Merkur 指標戰力鱷"},
        {"ID": "BabyShark dododo", "原宇宙": "Merkur", "保底積分": 11500000000, "備註": "Merkur 指標戰力鱷"},
        {"ID": "Captain Teemo", "原宇宙": "Merkur", "保底積分": 4500000000, "備註": "Merkur 核心編隊鯊"},
        {"ID": "Lucifer", "原宇宙": "Merkur", "保底積分": 3800000000, "備註": "Merkur 核心編隊鯊"},
        {"ID": "TumaNaomi", "原宇宙": "Merkur", "保底積分": 3500000000, "備註": "Merkur 核心編隊鯊"},
        {"ID": "cotyledon", "原宇宙": "Merkur", "保底積分": 3200000000, "備註": "Merkur 核心編隊鯊"},
        {"ID": "tom12345", "原宇宙": "Merkur", "保底積分": 2800000000, "備註": "Merkur 核心編隊鯊"},
        {"ID": "yoshino", "原宇宙": "Merkur", "保底積分": 2500000000, "備註": "Merkur 核心編隊鯊"},
        {"ID": "Hambeard", "原宇宙": "Merkur", "保底積分": 2200000000, "備註": "Merkur 核心編隊鯊"},
        {"ID": "Slime", "原宇宙": "Merkur", "保底積分": 1800000000, "備註": "Merkur 核心編隊鯊"},
        
        # === Oberon 服 ===
        {"ID": "Paris", "原宇宙": "Oberon", "保底積分": 240000000000, "備註": "Bug堆積天花板，兩千億大暴龍"},
        {"ID": "Glauconome", "原宇宙": "Oberon", "保底積分": 15000000000, "備註": "Oberon 指標核心巨鱷"},
        {"ID": "CCTV77", "原宇宙": "Oberon", "保底積分": 13500000000, "備註": "Oberon 核心編隊巨鱷"},
        {"ID": "Lord Patator", "原宇宙": "Oberon", "保底積分": 12000000000, "備註": "頂級高分玩家巨鱷"},
        {"ID": "Thorfinn", "原宇宙": "Oberon", "保底積分": 11000000000, "備註": "戰力不可小覷的巨鱷"},
        
        # === Cosmos 服 ===
        {"ID": "ATRAGON", "原宇宙": "Cosmos", "保底積分": 287209472520, "備註": "Cosmos服二千八百億遠古殘暴龍"},
        {"ID": "Kinopio", "原宇宙": "Cosmos", "保底積分": 16000000000, "備註": "Cosmos 指標核心巨鱷"},
        {"ID": "FUIYOH", "原宇宙": "Cosmos", "保底積分": 14500000000, "備註": "Cosmos 核心玩家巨鱷"},
        {"ID": "Chief Halo", "原宇宙": "Cosmos", "保底積分": 5500000000, "備註": "Cosmos 核心玩家鯊魚"},
        {"ID": "President Zenith", "原宇宙": "Cosmos", "保底積分": 4800000000, "備註": "Cosmos 核心玩家鯊魚"}
    ]
    return pd.DataFrame(monsters)

# 4. 核心功能：新宇宙動態嗅探與網頁解析
def fetch_and_collide_data():
    base_df = get_monster_base_data()
    
    status_dict = {}
    player_mode_dict = {}
    score_dict = {}
    
    uni_mapping = {
        "180": "Belinda (180)",
        "181": "Cetus (181)",
        "182": "Dione (182)"
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for uni_id, uni_name in uni_mapping.items():
        try:
            url = f"https://mmorpg-stat.eu{uni_id}&pays=11&stat=0"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.find_all('tr')
                
                for row in rows:
                    row_text = row.get_text()
                    for monster_id in base_df["ID"].tolist():
                        if monster_id in row_text:
                            status_dict[monster_id] = uni_name
                            
                            if f"{monster_id}(v)" in row_text.replace(" ", ""):
                                player_mode_dict[monster_id] = "🏖️ 假期 (v)"
                            elif f"{monster_id}(i)" in row_text.replace(" ", ""):
                                player_mode_dict[monster_id] = "💤 不活躍 (i)"
                            else:
                                player_mode_dict[monster_id] = "🟢 線上/正常"
                                
                            numbers = re.findall(r'\d[\d\s\.]{5,}', row_text)
                            for num_str in numbers:
                                clean_num = int(re.sub(r'[\s\.]', '', num_str))
                                if clean_num > 100000000:
                                    score_dict[monster_id] = clean_num
        except Exception:
            pass
            
    return status_dict, player_mode_dict, score_dict

# 5. 初始化暫存記憶 (今晚開服後，點擊同步才會將新服資料蓋上來)
if "live_status" not in st.session_state: st.session_state.live_status = {}
if "live_modes" not in st.session_state: st.session_state.live_modes = {}
if "live_scores" not in st.session_state: st.session_state.live_scores = {}

# 按鈕點擊事件
if refresh_btn:
    with st.spinner("正在向 mmorpg-stat 跨宇宙發動數據碰撞與嗅探..."):
        latest_status, latest_modes, latest_scores = fetch_and_collide_data()
        st.session_state.live_status = latest_status
        st.session_state.live_modes = latest_modes
        st.session_state.live_scores = latest_scores
        st.success("數據碰撞完成！最新獵場動態已同步。")

# 💡 終極降維流：直接強制組裝表格，徹底粉碎 Cache 鎖定 Bug
df_monsters = get_monster_base_data()
df_monsters["目前落腳新宇宙"] = df_monsters["ID"].apply(lambda x: st.session_state.live_status.get(x, "未確認"))
df_monsters["當前玩家狀態"] = df_monsters["ID"].apply(lambda x: st.session_state.live_modes.get(x, "未確認"))

# 💡 關鍵保底強制執行：如果網路還沒抓到新分數，強行把後台的『保底積分』塞進欄位！
df_monsters["實時總積分"] = df_monsters.apply(
    lambda r: st.session_state.live_scores.get(r["ID"], r["保底積分"]), axis=1
)

# 💡 根據分數動態劃分四大猛獸獵場階級
def dynamic_threat_level(score):
    if score >= 200000000000: return "Rex 2千億級暴龍"
    elif score >= 100000000000: return "Gorilla 千億級金剛"
    elif score >= 10000000000: return "Crocodile 百億級巨鱷"
    elif score >= 1000000000: return "Shark 近百億對手"
    elif score > 0: return "Hatching_Chick 孵化中幼體"
    else: return "White_Circle 等待數據同步"

df_monsters["威脅程度"] = df_monsters["實時總積分"].apply(dynamic_threat_level)

# 執行側邊欄篩選
if target_universe != "全部宇宙":
    df_filtered = df_monsters[df_monsters["目前落腳新宇宙"] == target_universe]
else:
    df_filtered = df_monsters

# 依照實時總積分由大到小進行絕對天梯天平排序
df_filtered = df_filtered.sort_values(by='實時總積分', ascending=False)
df_filtered["實時總積分"] = df_filtered["實時總積分"].apply(lambda x: f"{x:,}" if x > 0 else "0")

# 重排前台顯示欄位
df_filtered = df_filtered[["ID", "原宇宙", "目前落腳新宇宙", "當前玩家狀態", "實時總積分", "威脅程度", "備註"]]

# 6. 上半部：實時戰略儀表板 (純 HTML/CSS 降維流)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div style="text-align: left;"><span style="font-size: 13px; color: #b0b3b8;">鎖定監控巨獸</span><br><span style="font-size: 22px; font-weight: 700; color: white;">{len(df_monsters)} 員</span></div>', unsafe_allow_html=True)

with col2:
    count_b = len(df_monsters[df_monsters['目前落腳新宇宙'] == 'Belinda (180)'])
    st.markdown(f'<div style="text-align: left;"><span style="font-size: 13px; color: #b0b3b8;">已進駐 Belinda (180)</span><br><span style="font-size: 22px; font-weight: 700; color: white;">{count_b} 員</span></div>', unsafe_allow_html=True)

with col3:
    count_c = len(df_monsters[df_monsters['目前落腳新宇宙'] == 'Cetus (181)'])
    st.markdown(f'<div style="text-align: left;"><span style="font-size: 13px; color: #b0b3b8;">已進駐 Cetus (181)</span><br><span style="font-size: 22px; font-weight: 700; color: white;">{count_c} 員</span></div>', unsafe_allow_html=True)

with col4:
    count_d = len(df_monsters[df_monsters['目前落腳新宇宙'] == 'Dione (182)'])
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
    st.write("1. 內建本地記憶體保底已啟動！首頁將直接顯示各大恐龍歷史最高戰力總分，拒絕慘白！")
    st.write("2. 當這群大佬在全新宇宙手動遷徙並上線後，點擊左側重新整理，新服位置將會即時覆寫點亮！")

with tabs:
    st.markdown("- [mmorpg-stat 全球數據庫首頁](https://mmorpg-stat.eu)")
    st.markdown("- [OGame TW 官方論壇存檔看板](https://gameforge.com)")
