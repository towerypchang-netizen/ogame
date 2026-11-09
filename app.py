import streamlit as st
import pandas as pd
import requests
import re
import os
import base64
from streamlit_autorefresh import st_autorefresh

# 1. 網頁頁面配置與官方星際底圖注入
st.set_page_config(page_title="OGame TW FazoR 情報站", page_icon="🪐", layout="wide")

# 💡 注入專屬黑框白字「星域監控艙」的 CSS 樣式律令
st.markdown("""
    <style>
    /* 物理消滅 Streamlit 預設多餘間距，讓左右雙軌靠得更緊湊 */
    [data-testid="stHorizontalBlock"] {
        gap: 25px !important;
    }
    /* 🎯 專屬打造老大截圖中的黑框白字星域監控艙外殼 */
    .universe-monitor-box {
        border: 2px solid #ffffff !important;
        background-color: rgba(14, 17, 23, 0.9) !important;
        padding: 15px 10px !important;
        border-radius: 4px !important;
        text-align: center !important;
        width: 125px !important;
        margin-bottom: 20px !important;
    }
    .universe-title {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        font-family: 'Courier New', Courier, monospace !important;
        margin-bottom: 8px !important;
    }
    .universe-count {
        font-size: 12px !important;
        color: #ffffff !important;
    }
    .universe-num {
        font-size: 15px !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 注入 orion.jpg 背景底圖
if os.path.exists("orion.jpg"):
    with open("orion.jpg", "rb") as image_file:
        encoded_bg = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(14, 17, 23, 0.85), rgba(14, 17, 23, 0.85)), url(data:image/jpeg;base64,{encoded_bg});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)

# 核心進化：啟動 60 秒全自動天網重新整理內核
st_autorefresh(interval=60000, key="datarefresh")

# 將 logo.png 轉化為 base64 碼以達成 HTML 完美並列不換行
logo_html = ""
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as logo_file:
        encoded_logo = base64.b64encode(logo_file.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" style="height: 65px; margin-right: 20px; vertical-align: middle;">'

# 🎯 利用 Flexbox 讓官方 Logo 與 FazoR 專屬戰略標題在同一行完美合體
st.markdown(f"""
    <div style="display: flex; flex-direction: row; justify-content: flex-start; align-items: center; margin-top: 10px; margin-bottom: 10px;">
        {logo_html}
        <span style="font-size: 26px; font-weight: bold; color: white; font-family: Microsoft JhengHei, sans-serif;">
            諸神黃昏：u10-TW FazoR 併服情報站
        </span>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# 💡 依照指示移上來的「戰略備忘錄警示列」：焊死在標題正下方！
st.markdown('<span style="font-size: 14px; font-weight: bold; color: #ffffff;">🚀 戰略備忘錄：系統每分鐘自動更新，當這群怪物在全新宇宙遷徙並上線後，新服位置將會即時點亮！</span>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

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

# 4. 核心功能：新宇宙動態嗅探
def fetch_and_collide_data():
    base_df = get_monster_base_data()
    status_dict = {}
    player_mode_dict = {}
    score_dict = {}
    
    uni_mapping = {"180": "Belinda (180)", "181": "Cetus (181)", "182": "Dione (182)"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for uni_id, uni_name in uni_mapping.items():
        try:
            url = f"https://mmorpg-stat.eu{uni_id}&pays=11&stat=0"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                lines = response.text.split('\n')
                for line in lines:
                    for monster_id in base_df["ID"].tolist():
                        if monster_id in line:
                            status_dict[monster_id] = uni_name
                            if f"{monster_id}(v)" in line.replace(" ", ""):
                                player_mode_dict[monster_id] = "🏖️ 假期 (v)"
                            elif f"{monster_id}(i)" in line.replace(" ", ""):
                                player_mode_dict[monster_id] = "💤 不活躍 (i)"
                            else:
                                player_mode_dict[monster_id] = "🟢 線上/正常"
                                
                            numbers = re.findall(r'\d[\d\s\.]{5,}', line)
                            for num_str in numbers:
                                clean_num = int(re.sub(r'[\s\.]', '', num_str))
                                if clean_num > 100000000:
                                    score_dict[monster_id] = clean_num
        except Exception:
            pass
    return status_dict, player_mode_dict, score_dict

# 5. 背景自動執行打撈
latest_status, latest_modes, latest_scores = fetch_and_collide_data()

df_monsters = get_monster_base_data()
df_monsters["落腳新宇宙"] = df_monsters["ID"].apply(lambda x: latest_status.get(x, "未確認"))
df_monsters["當前玩家狀態"] = df_monsters["ID"].apply(lambda x: latest_modes.get(x, "未確認"))
df_monsters["實時總積分"] = df_monsters.apply(lambda r: latest_scores.get(r["ID"], r["保底積分"]), axis=1)

# 純 HTML 實心圓點指示燈，白字鎖定
def dynamic_threat_level(score):
    if score >= 200000000000: return '<span style="color:#ff4b4b;">●</span> <span style="color:#ffffff; font-weight:bold;">2千億級暴龍</span>'
    elif score >= 100000000000: return '<span style="color:#ff4b4b;">●</span> <span style="color:#ffffff; font-weight:bold;">千億級金剛</span>'
    elif score >= 10000000000: return '<span style="color:#ffa500;">●</span> <span style="color:#ffffff; font-weight:bold;">百億級巨鱷</span>'
    elif score >= 1000000000: return '<span style="color:#00c0f2;">●</span> <span style="color:#ffffff; font-weight:bold;">近百億對手</span>'
    elif score > 0: return '<span style="color:#00f900;">●</span> <span style="color:#ffffff; font-weight:bold;">孵化中幼體</span>'
    else: return '<span style="color:#ffffff;">○</span> <span style="color:#ffffff;">等待數據同步</span>'

df_monsters["威脅程度"] = df_monsters["實時總積分"].apply(dynamic_threat_level)

# 全螢幕預設全部顯示排序
df_filtered = df_monsters.sort_values(by='實時總積分', ascending=False)
df_filtered["實時總積分"] = df_filtered["實時總積分"].apply(lambda x: f"{x:,}" if x > 0 else "0")
df_filtered = df_filtered[["ID", "原宇宙", "落腳新宇宙", "當前玩家狀態", "實時總積分", "威脅程度", "備註"]]

# 計算各新宇宙進駐人數
count_b = len(df_monsters[df_monsters['落腳新宇宙'] == 'Belinda (180)'])
count_c = len(df_monsters[df_monsters['落腳新宇宙'] == 'Cetus (181)'])
count_d = len(df_monsters[df_monsters['落腳新宇宙'] == 'Dione (182)'])

# 6. 核心佈局：發動 雙軌黃金比例並列流
left_panel, right_panel = st.columns()

# === 🧱 左側軌道：黑框白字直列監控艙 ===
with left_panel:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class="universe-monitor-box">
            <div class="universe-title">Belinda</div>
            <div class="universe-count">已進駐 <span class="universe-num">{count_b}</span> 員</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class="universe-monitor-box">
            <div class="universe-title">Cetus</div>
            <div class="universe-count">已進駐 <span class="universe-num">{count_c}</span> 員</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class="universe-monitor-box">
            <div class="universe-title">Dione</div>
            <div class="universe-count">已進駐 <span class="universe-num">{count_d}</span> 員</div>
        </div>
    """, unsafe_allow_html=True)

# === 📊 右側主軌道：天梯情報管理大表格 ===
with right_panel:
    # 管制共 23 員計數
    st.markdown(f'<span style="color:#b0b3b8; font-size:14px; font-weight:bold;">管制共 {len(df_monsters)} 員</span>', unsafe_allow_html=True)
    
    # 中半部：即時情報管理表格 (HTML 強制高亮渲染)
    st.markdown("### 🪟 即時監控情報管理表")
