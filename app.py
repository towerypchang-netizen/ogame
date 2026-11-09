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
        {"ID": "WindAngelX", "原宇宙": "Merkur", "備註": "SOS 聯盟核心，超兩千億終極暴龍"},
        {"ID": "Satan", "原宇宙": "Merkur", "備註": "老牌高軍分狼"},
        {"ID": "Musashi", "原宇宙": "Merkur", "備註": "武藏，破壞力強"},
        {"ID": "Coon", "原宇宙": "Merkur", "備註": "Merkur 指標戰力"},
        {"ID": "BabyShark dododo", "原宇宙": "Merkur", "備註": "Merkur 指標戰力"},
        {"ID": "Captain Teemo", "原宇宙": "Merkur", "備註": "Merkur 核心編隊"},
        {"ID": "Lucifer", "原宇宙": "Merkur", "備註": "Merkur 核心編隊"},
        {"ID": "TumaNaomi", "原宇宙": "Merkur", "備註": "Merkur 核心編隊"},
        {"ID": "cotyledon", "原宇宙": "Merkur", "備註": "Merkur 核心編隊"},
        {"ID": "tom12345", "原宇宙": "Merkur", "備註": "Merkur 核心編隊"},
        {"ID": "yoshino", "原宇宙": "Merkur", "備註": "Merkur 核心編隊"},
        {"ID": "Hambeard", "原宇宙": "Merkur", "備註": "Merkur 核心編隊"},
        {"ID": "Slime", "原宇宙": "Merkur", "備註": "Merkur 核心編隊"},
        {"ID": "Paris", "原宇宙": "Oberon", "備註": "Bug堆積疑慮天花板，兩千億大暴龍"},
        {"ID": "Glauconome", "原宇宙": "Oberon", "備註": "Oberon 指標核心"},
        {"ID": "CCTV77", "原宇宙": "Oberon", "備註": "Oberon 核心編隊"},
        {"ID": "Lord Patator", "原宇宙": "Oberon", "備註": "頂級高分玩家"},
        {"ID": "Thorfinn", "原宇宙": "Oberon", "備註": "戰力不可小覷"},
        {"ID": "ATRAGON", "原宇宙": "Cosmos", "備註": "Cosmos服二千八百億遠古殘暴龍"},
        {"ID": "Kinopio", "原宇宙": "Cosmos", "備註": "Cosmos 指標核心"},
        {"ID": "FUIYOH", "原宇宙": "Cosmos", "備註": "Cosmos 核心玩家"},
        {"ID": "Chief Halo", "原宇宙": "Cosmos", "備註": "Cosmos 核心玩家"},
        {"ID": "President Zenith", "原宇宙": "Cosmos", "備註": "Cosmos 核心玩家"}
    ]
    return pd.DataFrame(monsters)

# 4. 核心功能：實時總積分、狀態、新舊宇宙雙重自動打撈模組
def fetch_and_collide_data():
    base_df = get_monster_base_data()
    
    status_dict = {m: "未確認" for m in base_df["ID"].tolist()}
    player_mode_dict = {m: "未確認" for m in base_df["ID"].tolist()}
    score_dict = {m: 0 for m in base_df["ID"].tolist()}
    
    # 新目標宇宙映射
    new_uni_mapping = {
        "180": "Belinda (180)",
        "181": "Cetus (181)",
        "182": "Dione (182)"
    }
    
    # 舊母服宇宙代碼映射 (用於新服查不到時的「原宇宙保底機制」)
    # 根據 OGame 官方編號：Merkur=165, Oberon=167, Cosmos=168 (或對應的多國聯合服代碼)
    old_uni_mapping = {
        "Merkur": "_1165",
        "Oberon": "_1167",
        "Cosmos": "_1168"
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # === 🚀 第一階段：優先清查新宇宙 ===
    for uni_id, uni_name in new_uni_mapping.items():
        try:
            url = f"https://mmorpg-stat.eu{uni_id}&pays=11&stat=0"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.find_all('tr')
                for row in rows:
                    row_text = row.get_text()
                    for m_id in status_dict.keys():
                        if m_id in row_text:
                            status_dict[m_id] = uni_name
                            if f"{m_id}(v)" in row_text.replace(" ", ""):
                                player_mode_dict[m_id] = "🏖️ 假期 (v)"
                            elif f"{m_id}(i)" in row_text.replace(" ", ""):
                                player_mode_dict[m_id] = "💤 不活躍 (i)"
                            else:
                                player_mode_dict[m_id] = "🟢 線上/正常"
                            
                            numbers = re.findall(r'\d[\d\s\.]{5,}', row_text)
                            for num_str in numbers:
                                clean_num = int(re.sub(r'[\s\.]', '', num_str))
                                if clean_num > 100000000 and clean_num > score_dict[m_id]:
                                    score_dict[m_id] = clean_num
        except Exception:
            pass

    # === 🦖 第二階段：原宇宙保底防機制 (若新宇宙沒分，直接去舊服抓分) ===
    for m_id in score_dict.keys():
        if score_dict[m_id] == 0:  # 新服還查不到資料
            try:
                # 找出這隻恐龍的原宇宙名
                m_row = base_df[base_df["ID"] == m_id].iloc[0]
                old_uni_name = m_row["原宇宙"]
                old_uni_code = old_uni_mapping.get(old_uni_name, "_1165")
                
                # 爬取 mmorpg-stat 舊宇宙歷史存檔排行
                url = f"https://mmorpg-stat.eu{old_uni_code}&pays=11&stat=0"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    rows = soup.find_all('tr')
                    for row in rows:
                        row_text = row.get_text()
                        if m_id in row_text:
                            if status_dict[m_id] == "未確認":
                                status_dict[m_id] = f"未確認 (原宇宙)"
                            
                            if player_mode_dict[m_id] == "未確認":
                                if f"{m_id}(v)" in row_text.replace(" ", ""):
                                    player_mode_dict[m_id] = "🏖️ 假期 (v)"
                                elif f"{m_id}(i)" in row_text.replace(" ", ""):
                                    player_mode_dict[m_id] = "💤 不活躍 (i)"
                                else:
                                    player_mode_dict[m_id] = "🟢 線上/正常"
                            
                            numbers = re.findall(r'\d[\d\s\.]{5,}', row_text)
                            for num_str in numbers:
                                clean_num = int(re.sub(r'[\s\.]', '', num_str))
                                if clean_num > 100000000 and clean_num > score_dict[m_id]:
                                    score_dict[m_id] = clean_num
            except Exception:
                pass
                
    return status_dict, player_mode_dict, score_dict

# 5. 初始化與狀態記憶
if "current_status" not in st.session_state:
    base_df = get_monster_base_data()
    st.session_state.current_status = {m: "未確認" for m in base_df["ID"].tolist()}
    st.session_state.player_modes = {m: "未確認" for m in base_df["ID"].tolist()}
    st.session_state.player_scores = {m: 0 for m in base_df["ID"].tolist()}

# 按鈕觸發
if refresh_btn:
    with st.spinner("正在啟動雙重嗅探：優先抓取新服排行，未確認者將自動打撈舊宇宙歷史數據保底..."):
        latest_status, latest_modes, latest_scores = fetch_and_collide_data()
        st.session_state.current_status = latest_status
        st.session_state.player_modes = latest_modes
        st.session_state.player_scores = latest_scores
        st.success("巨獸天梯數據打撈完畢！")

# 整合最新動態情報
df_monsters = get_monster_base_data()
df_monsters["目前落腳新宇宙"] = df_monsters["ID"].apply(lambda x: st.session_state.current_status.get(x, "未確認"))
df_monsters["當前玩家狀態"] = df_monsters["ID"].apply(lambda x: st.session_state.player_modes.get(x, "未確認"))
df_monsters["實時總積分"] = df_monsters["ID"].apply(lambda x: st.session_state.player_scores.get(x, 0))

# 根據分數動態劃分四大恐龍階級
def dynamic_threat_level(score):
    if score >= 200000000000:
        return "Rex 2千億級暴龍"
    elif score >= 100000000000:
        return "Gorilla 千億級金剛"
    elif score >= 10000000000:
        return "Crocodile 百億級巨鱷"
    elif score >= 1000000000:
        return "Shark 近百億對手"
    elif score > 0:
         return "Hatching_Chick 孵化中幼體"
    else:
        return "White_Circle 等待數據同步"

df_monsters["威脅程度"] = df_monsters["實時總積分"].apply(dynamic_threat_level)

# 執行側邊欄篩選
if target_universe != "全部宇宙":
    df_filtered = df_monsters[df_monsters["目前落腳新宇宙"] == target_universe]
else:
    df_filtered = df_monsters

# 依據實時總積分由大到小絕對排序
df_filtered = df_filtered.sort_values(by='實時總積分', ascending=False)
df_filtered["實時總積分"] = df_filtered["實時總積分"].apply(lambda x: f"{x:,}" if x > 0 else "0")

# 重排表格
df_filtered = df_filtered[["ID", "原宇宙", "目前落腳新宇宙", "當前玩家狀態", "實時總積分", "威脅程度", "備註"]]

# 6. 上半部：實時戰略儀表板
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
    count_d = len(df_monsters[df_monsters['currently_status'] == 'Dione (182)'] if 'currently_status' in locals() else df_monsters[df_monsters['目前落腳新宇宙'] == 'Dione (182)'])
    count_d = len(df_monsters[df_monsters['目前落腳新宇宙'] == 'Dione (182)'])
    st.markdown(f'<div style="text-align: left;"><span style="font-size: 13px; color: #b0b3b8;">已進駐 Dione (182)</span><br><span style="font-size: 22px; font-weight: 700; color: white;">{count_d} 員</span></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 7. 中半部：即時情報管理表格
st.markdown("### 🪟 即時監控情報管理表")
st.dataframe(df_filtered, use_container_width=True, hide_index=True)

# 8. 下半部：情報備忘與外部聯結
st.markdown("---")
