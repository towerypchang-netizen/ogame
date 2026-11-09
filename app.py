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

# 💡 注入專屬黑框白字「直列星域監控艙」的純 CSS 樣式律令（徹底排除死鎖，完美優化文字排版）
st.markdown("""
    <style>
    /* 🎯 左側直列監控艙一體化外殼外框 */
    .universe-monitor-box-vertical {
        border: 2px solid #ffffff !important;
        background-color: rgba(14, 17, 23, 0.9) !important;
        padding: 15px 12px !important;
        border-radius: 4px !important;
        text-align: center !important;
        width: 140px !important;
        margin-top: 10px !important;
        margin-bottom: 15px !important;
    }
    .universe-title-fixed {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        font-family: 'Courier New', Courier, monospace !important;
        margin-bottom: 6px !important;
    }
    .universe-count-fixed {
        font-size: 12px !important;
        color: #ffffff !important;
    }
    .universe-num-fixed {
        font-size: 15px !important;
        font-weight: bold !important;
    }
    
    /* 🖥️ 大天梯表格專屬溢出安全外殼 */
    .monitor-table-container-scroll { 
        overflow-x: auto !important; 
        width: 100% !important; 
    }
    
    /* 自訂極速網頁 Table 樣式定義，完美重現高對比星際感 */
    .ogame-final-universe-table {
        width: 100% !important;
        color: white !important;
        border-collapse: collapse !important;
        font-family: sans-serif !important;
    }
    .ogame-final-universe-table th {
        background-color: rgba(255, 255, 255, 0.05) !important;
        padding: 12px 10px !important;
        text-align: left !important;
        font-weight: bold !important;
        border-bottom: 2px solid #ffffff !important;
    }
    .ogame-final-universe-table td {
        padding: 12px 10px !important;
        text-align: left !important;
        border-bottom: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* 讓 Streamlit 原生重新整理按鈕完美適配左側直列寬度 */
    div.stButton > button {
        width: 140px !important;
        height: 50px !important;
        background-color: rgba(14, 17, 23, 0.9) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        font-size: 14px !important;
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

# 核心進化：啟動 60 秒全自動重新整理內核
if st_autorefresh is not None:
    st_autorefresh(interval=60000, key="datarefresh")

# 將 logo.png 轉化為 base64 碼以達成 HTML 完美並列不換行
logo_html = ""
if (ASSET_DIR / "logo.png").exists():
    with open(ASSET_DIR / "logo.png", "rb") as logo_file:
        encoded_logo = base64.b64encode(logo_file.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" style="height: 65px; margin-right: 20px; vertical-align: middle;">'

# 🎯 數據處理層 (共 23 員嚴密管制，欄位名完全正名)
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
        {"ID": "Chief Halo", "原宇宙": "Cosmos", "保底積分": 5500000000, "備鱷": "Cosmos 核心玩家鯊魚"},
        {"ID": "President Zenith", "原宇宙": "Cosmos", "保底積分": 4800000000, "備註": "Cosmos 核心玩家鯊魚"}
    ]
    return pd.DataFrame(monsters)

@st.cache_data(ttl=60, show_spinner=False)
def fetch_and_collide_data():
    base_df = get_monster_base_data()
    status_dict, player_mode_dict, score_dict = {}, {}, {}
    fetch_errors = []
    
    uni_mapping = {
        "139": "Merkur (139)", 
        "151": "Oberon (151)", 
        "160": "Cosmos (160)",
        "180": "Belinda (180)", 
        "181": "Cetus (181)", 
        "182": "Dione (182)"
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    for uni_id, uni_name in uni_mapping.items():
        try:
            url = "https://mmorpg-stat.eu"
            response = requests.get(
                url, params={"univers": f"_{uni_id}", "pays": 11, "stat": 0},
                headers=headers, timeout=(2, 3)
            )
            
            if response.status_code == 403:
                continue
                
            response.raise_for_status()
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
                                player_mode_dict[monster_id] = "🟢 正常（非在線判定）"
                                
                            numbers = re.findall(r'\d[\d\s\.]{5,}', line)
                            for num_str in numbers:
                                clean_num = int(re.sub(r'[\s\.]', '', num_str))
                                if clean_num > 100000000: 
                                    score_dict[monster_id] = clean_num
                                    
        except Exception as exc:
            if "180" not in uni_id and "181" not in uni_id and "182" not in uni_id:
                fetch_errors.append(f"{uni_name} 連線失敗 (使用保底數據)")
            
    return status_dict, player_mode_dict, score_dict, fetch_errors

# 🛡️ 啟動純函數級防護盾，阻絕緩存鎖死
latest_status, latest_modes, latest_scores = {}, {}, {}
try:
    latest_status, latest_modes, latest_scores, fetch_errors = fetch_and_collide_data()
except Exception:
    fetch_errors = ["天網核心快取隔離：已載入歷史保底戰力資料庫"]

df_monsters = get_monster_base_data()

# 🎯 核心業務邏輯：找不到人時，狀態設定為「已遷徙或不明」
df_monsters["落腳新宇宙"] = df_monsters["ID"].apply(lambda x: latest_status.get(x, "未確認"))
df_monsters["當前玩家狀態"] = df_monsters["ID"].apply(lambda x: latest_modes.get(x, "已遷徙或不明"))
df_monsters["實時總積分"] = df_monsters.apply(lambda r: int(latest_scores.get(r["ID"], r["保底積分"])), axis=1).astype('int64')

# 純 HTML 實心指示燈，修正回歸自訂 Table 機制
def dynamic_threat_level(score):
    if score >= 200000000000: return '<span style="color:#ff4b4b;">●</span> 2千億級暴龍'
    elif score >= 100000000000: return '<span style="color:#ff4b4b;">●</span> 千億級金剛'
    elif score >= 10000000000: return '<span style="color:#ffa500;">●</span> 百億級巨鱷'
    elif score >= 1000000000: return '<span style="color:#00c0f2;">●</span> 近百億對手'
    else: return '<span style="color:#00f900;">●</span> 孵化中幼體'

df_monsters["積分來源"] = df_monsters["ID"].apply(
    lambda player: "網站擷取" if player in latest_scores else "預設保底（非即時）"
)
df_monsters["威脅程度"] = df_monsters["實時總積分"].apply(dynamic_threat_level)

# 🧱 資料排序與千分位轉化
df_filtered = df_monsters.sort_values(by='實時總積分', ascending=False)
df_filtered["實時總積分"] = df_filtered["實時總積分"].apply(lambda x: f"{x:,}" if x > 0 else "0")
