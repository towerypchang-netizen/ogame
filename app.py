import streamlit as st
import pandas as pd
import requests
import re
import os
import base64
from pathlib import Path
from html import escape

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

ASSET_DIR = Path(__file__).resolve().parent

# 1. 網頁頁面配置與官方星際底圖注入
st.set_page_config(page_title="OGame TW FazoR 情報站", page_icon="🪐", layout="wide")

# 💡 注入專屬黑框白字「星域監控艙」的純 CSS 樣式律令
st.markdown("""
    <style>
    .monitor-top-row {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 20px !important;
        flex-wrap: wrap !important;
        margin-bottom: 25px !important;
    }
    .universe-monitor-box {
        border: 2px solid #ffffff !important;
        background-color: rgba(14, 17, 23, 0.9) !important;
        padding: 10px 15px !important;
        border-radius: 4px !important;
        text-align: center !important;
        min-width: 125px !important;
    }
    .universe-title {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        font-family: 'Courier New', Courier, monospace !important;
        margin-bottom: 4px !important;
    }
    .universe-count {
        font-size: 12px !important;
        color: #ffffff !important;
    }
    .universe-num {
        font-size: 15px !important;
        font-weight: bold !important;
    }
    .monitor-table-scroll { 
        overflow-x: auto !important; 
        width: 100% !important; 
        margin-top: 10px !important;
    }
    .ogame-custom-table {
        width: 100% !important;
        min-width: 1000px !important;
        color: white !important;
        border-collapse: collapse !important;
    }
    .ogame-custom-table th, .ogame-custom-table td {
        padding: 12px 10px !important;
        text-align: left !important;
        border-bottom: 1px solid rgba(255,255,255,0.1) !important;
    }
    div.stButton > button {
        height: 62px !important;
        width: 150px !important;
        background-color: rgba(14, 17, 23, 0.9) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        font-size: 15px !important;
    }
    div.stButton > button:hover {
        background-color: #ffffff !important;
        color: black !important;
        border: 2px solid #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 注入 orion.jpg 背景底圖
if (ASSET_DIR / "orion.jpg").exists():
    with open(ASSET_DIR / "orion.jpg", "rb") as image_file:
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

# 核心自動重新整理
if st_autorefresh is not None:
    st_autorefresh(interval=60000, key="datarefresh")

logo_html = ""
if (ASSET_DIR / "logo.png").exists():
    with open(ASSET_DIR / "logo.png", "rb") as logo_file:
        encoded_logo = base64.b64encode(logo_file.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" style="height: 65px; margin-right: 20px; vertical-align: middle;">'

def get_monster_base_data():
    return pd.DataFrame([
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
    ])

def fetch_and_collide_data():
    base_df = get_monster_base_data()
    status_dict, player_mode_dict, score_dict = {}, {}, {}
    
    uni_mapping = {
        "139": "Merkur (139)", "151": "Oberon (151)", "160": "Cosmos (160)",
        "180": "Belinda (180)", "181": "Cetus (181)", "182": "Dione (182)"
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for uni_id, uni_name in uni_mapping.items():
        try:
            url = "https://mmorpg-stat.eu"
            response = requests.get(url, params={"univers": f"_{uni_id}", "pays": 11, "stat": 0}, headers=headers, timeout=(2, 3))
            if response.status_code == 403:
                continue
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
                                player_mode_dict[monster_id] = "🟢 正常"
                            numbers = re.findall(r'\d[\d\s\.]{5,}', line)
                            for num_str in numbers:
                                clean_num = int(re.sub(r'[\s\.]', '', num_str))
                                if clean_num > 100000000: 
                                    score_dict[monster_id] = clean_num
        except Exception:
            pass
    return status_dict, player_mode_dict, score_dict

# 🛡️ 執行最安全的資料抓取與保底映射
try:
    latest_status, latest_modes, latest_scores = fetch_and_collide_data()
except Exception:
    latest_status, latest_modes, latest_scores = {}, {}, {}

df_monsters = get_monster_base_data()
df_monsters["落腳新宇宙"] = df_monsters["ID"].apply(lambda x: latest_status.get(x, "未確認"))
df_monsters["當前玩家狀態"] = df_monsters["ID"].apply(lambda x: latest_modes.get(x, "已遷徙或不明"))
df_monsters["實時總積分"] = df_monsters.apply(lambda r: int(latest_scores.get(r["ID"], r["保底積分"])), axis=1).astype('int64')

def dynamic_threat_level(score):
    if score >= 200000000000: return '<span style="color:#ff4b4b;">●</span> <span style="color:#ffffff; font-weight:bold;">2千億級暴龍</span>'
    elif score >= 100000000000: return '<span style="color:#ff4b4b;">●</span> <span style="color:#ffffff; font-weight:bold;">千億級金剛</span>'
    elif score >= 10000000000: return '<span style="color:#ffa500;">●</span> <span style="color:#ffffff; font-weight:bold;">百億級巨鱷</span>'
    elif score >= 1000000000: return '<span style="color:#00c0f2;">●</span> <span style="color:#ffffff; font-weight:bold;">近百億對手</span>'
    else: return '<span style="color:#00f900;">●</span> <span style="color:#ffffff; font-weight:bold;">孵化中幼體</span>'

df_monsters["積分來源"] = df_monsters["ID"].apply(lambda x: "網站擷取" if x in latest_scores else "預設保底")
df_monsters["威脅程度"] = df_monsters["實時總積分"].apply(dynamic_threat_level)

df_filtered = df_monsters.sort_values(by='實時總積分', ascending=False)
df_filtered["實時總積分"] = df_filtered["實時總積分"].apply(lambda x: f"{x:,}")
df_filtered = df_filtered[["ID", "原宇宙", "落腳新宇宙", "當前玩家狀態", "實時總積分", "積分來源", "威脅程度", "備註"]]

count_b = len(df_monsters[df_monsters['落腳新宇宙'].str.contains('Belinda', na=False)])
count_c = len(df_monsters[df_monsters['落腳新宇宙'].str.contains('Cetus', na=False)])
count_d = len(df_monsters[df_monsters['落腳新宇宙'].str.contains('Dione', na=False)])

# === 🧱 網頁渲染 ===
st.markdown(f'<div style="display: flex; flex-direction: row; align-items: center; margin-top: 10px;">{logo_html}<span style="font-size: 26px; font-weight: bold; color: white;">諸神黃昏：u10-TW FazoR 併服情報站</span></div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown('<span style="font-size: 14px; font-weight: bold; color: #ffffff;">🚀 戰略備忘錄：資料依統計網站更新進度同步；找不到玩家代表已遷徙或刪號，狀態將標記為已遷徙。</span>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 📊 橫向頂部工具列
