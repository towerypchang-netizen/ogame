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
        {"ID": "Chief Halo", "原宇宙": "Cosmos", "保底積分": 5500000000, "備註": "Cosmos 核心玩家鯊魚"},
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
                                    
        except (requests.RequestException, ValueError, TypeError) as exc:
            fetch_errors.append(f"{uni_name}：{type(exc).__name__}：{exc}")
            
    return status_dict, player_mode_dict, score_dict, fetch_errors

def dynamic_threat_level(score):
    if score >= 200000000000: return '<span style="color:#ff4b4b;">●</span> 2千億級暴龍'
    elif score >= 100000000000: return '<span style="color:#ff4b4b;">●</span> 千億級金剛'
    elif score >= 10000000000: return '<span style="color:#ffa500;">●</span> 百億級巨鱷'
    elif score >= 1000000000: return '<span style="color:#00c0f2;">●</span> 近百億對手'
    else: return '<span style="color:#00f900;">●</span> 孵化中幼體'


# 先建立畫面，再讀取網站，避免等待期間只看到背景。
st.markdown(
    f'<div style="display:flex;align-items:center;flex-wrap:wrap;gap:12px;">'
    f'{logo_html}<h2 style="color:white;">諸神黃昏：u10-TW FazoR 併服情報站</h2></div>',
    unsafe_allow_html=True,
)
st.caption("資料依統計網站更新；未取得積分時顯示預設值。正常狀態不代表目前在線。")
if st_autorefresh is None:
    st.caption("未安裝 streamlit-autorefresh，目前使用手動更新。")
left_column, right_column = st.columns([1, 6])
with left_column:
    if st.button("立即重新整理"):
        fetch_and_collide_data.clear()
monitor_slot = left_column.empty()
table_slot = right_column.empty()
notice_slot = st.empty()


def render_monitor_table(frame):
    with monitor_slot.container():
        for universe in ("Belinda (180)", "Cetus (181)", "Dione (182)"):
            count = int((frame["落腳新宇宙"] == universe).sum())
            st.markdown(
                '<div class="universe-monitor-box-vertical">'
                f'<div class="universe-title-fixed">{escape(universe.split()[0])}</div>'
                f'<div class="universe-count-fixed">已確認 <span class="universe-num-fixed">{count}</span> 員</div>'
                '</div>', unsafe_allow_html=True,
            )
    columns = ["ID", "原宇宙", "落腳新宇宙", "當前玩家狀態", "實時總積分", "積分來源", "威脅程度", "備註"]
    display_frame = frame.sort_values("實時總積分", ascending=False)[columns].copy()
    display_frame["實時總積分"] = display_frame["實時總積分"].map(lambda score: f"{score:,}")
    for column in columns:
        if column != "威脅程度":
            display_frame[column] = display_frame[column].map(lambda value: escape(str(value)))
    table = display_frame.to_html(index=False, escape=False, classes="ogame-final-universe-table", border=0)
    html = (
        f'<div style="color:white;">管制共 {len(frame)} 員</div>'
        '<h3 style="color:white;">即時監控情報管理表</h3>'
        f'<div class="monitor-table-container-scroll">{table}</div>'
    )
    table_slot.markdown("".join(line.strip() for line in html.splitlines()), unsafe_allow_html=True)


fallback = get_monster_base_data()
fallback["落腳新宇宙"] = "未確認"
fallback["當前玩家狀態"] = "未確認"
fallback["實時總積分"] = fallback["保底積分"]
fallback["積分來源"] = "預設保底（非即時）"
fallback["威脅程度"] = fallback["實時總積分"].apply(dynamic_threat_level)
render_monitor_table(fallback)
notice_slot.info("正在讀取統計網站；表格已先載入預設資料。")

# 取得資料後更新表格
latest_status, latest_modes, latest_scores = {}, {}, {}
try:
    latest_status, latest_modes, latest_scores, fetch_errors = fetch_and_collide_data()
except Exception as exc:
    fetch_errors = [f"資料讀取失敗，使用預設保底資料：{type(exc).__name__}：{exc}"]

df_monsters = get_monster_base_data()

# 🎯 核心業務邏輯：找不到人時，狀態設定為「已遷徙或不明」
df_monsters["落腳新宇宙"] = df_monsters["ID"].apply(lambda x: latest_status.get(x, "未確認"))
df_monsters["當前玩家狀態"] = df_monsters["ID"].apply(lambda x: latest_modes.get(x, "未確認"))
df_monsters["實時總積分"] = df_monsters.apply(lambda r: int(latest_scores.get(r["ID"], r["保底積分"])), axis=1).astype('int64')

# 純 HTML 實心指示燈，修正回歸自訂 Table 機制
df_monsters["積分來源"] = df_monsters["ID"].apply(
    lambda player: "網站擷取（待核對）" if player in latest_scores else "預設保底（非即時）"
)
df_monsters["威脅程度"] = df_monsters["實時總積分"].apply(dynamic_threat_level)

render_monitor_table(df_monsters)
if fetch_errors:
    notice_slot.warning("部分統計資料讀取失敗，未取得的積分顯示預設值。已確認人數不代表實際進駐總人數。")
    with st.expander("查看資料讀取錯誤"):
        for error in fetch_errors:
            st.text(error)
elif not latest_status:
    notice_slot.warning("網站請求完成，但未辨識到追蹤玩家；目前顯示預設資料，無法據此判斷遷徙狀態。")
else:
    notice_slot.info("網站擷取結果仍需核對；未確認的位置不代表玩家尚未遷入。")
