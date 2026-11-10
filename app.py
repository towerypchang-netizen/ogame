import streamlit as st
import pandas as pd
import requests
import re
import os
import base64
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urljoin, quote
import json
import hashlib
import hmac
import time
import threading
from io import BytesIO
from PIL import Image, ImageDraw

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
            background-image: linear-gradient(rgba(14, 17, 23, 0.75), rgba(14, 17, 23, 0.75)), url(data:image/jpeg;base64,{encoded_bg});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)


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

# mmorpg 網站選單已核對的來源編號；舊設定 151、160 會落到其他宇宙。
SOURCE_UNIVERSES = {"139": "Merkur", "141": "Oberon", "155": "Cosmos"}
NEW_UNIVERSES = {"180": "Belinda", "181": "Cetus", "182": "Dione"}


# 管理者認證與手動遷徙資料；公開訪客沒有寫入權限。
DESTINATION_OPTIONS = ["Belinda", "Cetus", "Dione"]


def setting(name, default=""):
    try:
        return str(st.secrets.get(name, os.environ.get(name, default)))
    except (FileNotFoundError, KeyError):
        return str(os.environ.get(name, default))


def is_admin():
    password = setting("ADMIN_PASSWORD")
    ticket = st.session_state.get("_admin_ticket", {})
    fingerprint = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return bool(password and ticket.get("expires", 0) > time.time()
                and hmac.compare_digest(ticket.get("fingerprint", ""), fingerprint))


def login_admin():
    attempt = st.session_state.pop("_admin_password", "")
    if st.session_state.get("_admin_locked_until", 0) > time.time():
        st.session_state["_admin_error"] = "嘗試次數過多，請稍後再試。"
        return
    expected = setting("ADMIN_PASSWORD")
    if expected and hmac.compare_digest(attempt.encode("utf-8"), expected.encode("utf-8")):
        st.session_state["_admin_ticket"] = {
            "fingerprint": hashlib.sha256(expected.encode("utf-8")).hexdigest(),
            "expires": time.time() + 8 * 60 * 60,
        }
        st.session_state.pop("_admin_error", None)
        st.session_state["_admin_failures"] = 0
    else:
        failures = st.session_state.get("_admin_failures", 0) + 1
        st.session_state["_admin_failures"] = failures
        if failures >= 5:
            st.session_state["_admin_locked_until"] = time.time() + 60
            st.session_state["_admin_failures"] = 0
        st.session_state["_admin_error"] = "密碼不正確。"


def logout_admin():
    st.session_state.pop("_admin_ticket", None)
    st.session_state.pop("_destination_snapshot", None)


def admin_controls():
    with st.sidebar.expander("管理者", expanded=is_admin()):
        if is_admin():
            st.success("已登入管理者")
            st.button("登出", on_click=logout_admin)
        elif not setting("ADMIN_PASSWORD"):
            st.caption("尚未設定管理者密碼，目前僅供檢視。")
        else:
            with st.form("admin_login"):
                st.text_input("管理者密碼", type="password", key="_admin_password")
                st.form_submit_button("登入", on_click=login_admin)
            if st.session_state.get("_admin_error"):
                st.error(st.session_state["_admin_error"])


def validate_destinations(data):
    if not isinstance(data, dict):
        raise ValueError("遷徙資料格式不正確。")
    valid_players = set(get_monster_base_data()["ID"])
    cleaned = {}
    for player, destination in data.items():
        if player not in valid_players or destination not in DESTINATION_OPTIONS:
            raise ValueError("遷徙資料包含未知玩家或不允許的新宇宙。")
        cleaned[player] = destination
    return cleaned


def github_store():
    repo = setting("DESTINATIONS_GITHUB_REPO")
    token = setting("DESTINATIONS_GITHUB_TOKEN")
    if not repo and not token:
        return None
    if not repo or not token or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("請完整設定 GitHub 儲存庫與權杖。")
    path = setting("DESTINATIONS_GITHUB_PATH", "player_destinations.json")
    branch = setting("DESTINATIONS_GITHUB_BRANCH", "main")
    url = f"https://api.github.com/repos/{repo}/contents/{quote(path, safe='/')}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    return url, headers, branch


def read_destinations():
    remote = github_store()
    if remote:
        url, headers, branch = remote
        response = requests.get(url, headers=headers, params={"ref": branch}, timeout=(3, 8))
        if response.status_code == 404:
            # 先確認儲存庫與分支存在，避免把權限／設定錯誤當成空白資料。
            repo = setting("DESTINATIONS_GITHUB_REPO")
            check = requests.get(f"https://api.github.com/repos/{repo}/branches/{quote(branch, safe='')}", headers=headers, timeout=(3, 8))
            if check.status_code != 200:
                raise ValueError("GitHub 儲存庫、分支或讀取權限設定不正確。")
            return {}, None
        if response.status_code != 200:
            raise ValueError(f"GitHub 資料讀取失敗（HTTP {response.status_code}）。")
        payload = response.json()
        data = json.loads(base64.b64decode(payload["content"]).decode("utf-8"))
        return validate_destinations(data), payload["sha"]
    path = ASSET_DIR / "data" / "player_destinations.json"
    if not path.exists():
        return {}, None
    content = path.read_bytes()
    return validate_destinations(json.loads(content.decode("utf-8"))), hashlib.sha256(content).hexdigest()


@st.cache_resource
def destination_write_lock():
    return threading.Lock()


def save_destinations(data, expected_revision):
    # 寫入端再次驗證，不依賴前端 disabled 或隱藏欄位當作權限控制。
    if not is_admin():
        raise PermissionError("僅管理者可以修改落腳新宇宙。")
    cleaned = validate_destinations(data)
    content = (json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with destination_write_lock():
        _, revision = read_destinations()
        if revision != expected_revision:
            raise ValueError("資料已被其他管理者更新，請重新載入後再修改。")
        remote = github_store()
        if remote:
            url, headers, branch = remote
            body = {"message": "Update player destination universes", "branch": branch,
                    "content": base64.b64encode(content).decode("ascii")}
            if revision:
                body["sha"] = revision
            response = requests.put(url, headers=headers, json=body, timeout=(3, 12))
            if response.status_code not in (200, 201):
                raise ValueError(f"GitHub 儲存失敗（HTTP {response.status_code}），資料尚未儲存。")
        else:
            path = ASSET_DIR / "data" / "player_destinations.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(".tmp")
            try:
                temporary.write_bytes(content)
                os.replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)


def save_edited_destinations(edited, original, revision):
    if not is_admin():
        raise PermissionError("管理者登入已失效，請重新登入。")
    if len(edited) != len(original) or edited["_player_id"].tolist() != original["_player_id"].tolist():
        raise ValueError("玩家資料順序或識別碼不符，請重新載入。")
    data = {}
    for player, value in zip(edited["_player_id"], edited["落腳新宇宙"]):
        if pd.isna(value) or value == "":
            continue
        data[player] = value
    save_destinations(data, revision)



def universe_url(uni_id):
    return f"https://www.mmorpg-stat.eu/?pagex=1&univers=_{uni_id}&pays=11"


class RankingParser(HTMLParser):
    """依玩家所在的表格列取值，不從整行 HTML 猜測積分。"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.cells = None
        self.cell = None
        self.links = []
        self.link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self.cells, self.links = [], []
        elif tag in ("td", "th") and self.cells is not None:
            self.cell = []
        elif tag == "a" and self.cell is not None:
            self.link = {"href": attrs.get("href", ""), "text": []}

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)
        if self.link is not None:
            self.link["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.link is not None:
            self.links.append((self.link["href"], "".join(self.link["text"]).strip()))
            self.link = None
        elif tag in ("td", "th") and self.cell is not None:
            self.cells.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.cells is not None:
            self.rows.append((self.cells, self.links))
            self.cells, self.cell, self.link = None, None, None


@st.cache_data(ttl=60, show_spinner=False)
def fetch_and_collide_data():
    base = get_monster_base_data()
    origin_by_player = dict(zip(base["ID"], base["原宇宙"]))
    destinations, modes, scores, player_urls, alliances = {}, {}, {}, {}, {}
    errors, connections = [], []
    universes = dict(SOURCE_UNIVERSES)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for uni_id, name in universes.items():
        url = universe_url(uni_id)
        report = {"宇宙": f"{name} ({uni_id})", "結果": "讀取中", "連線狀態": "", "符合追蹤玩家": 0, "來源": url}
        try:
            response = requests.get(url, headers=headers, timeout=(3, 6))
            response.raise_for_status()
            if 'cf-chl' in response.text or '<title>Just a moment' in response.text:
                raise ValueError("網站要求瀏覽器驗證")
            title = re.search(r"<title>(.*?)</title>", response.text, re.I | re.S)
            actual_title = title.group(1).strip() if title else "缺少標題"
            if not re.search(rf"Universe\s+{re.escape(name)}\s+TW\b", actual_title, re.I):
                raise ValueError(f"回傳宇宙不符：{actual_title}")
            parser = RankingParser()
            parser.feed(response.text)
            ranking_rows = 0
            for cells, links in parser.rows:
                player_links = [(href, text) for href, text in links if re.search(r"[?&]ftr=\d+\.dat(?:&|$)", href)]
                if not player_links or len(cells) < 5:
                    continue
                ranking_rows += 1
                href, player = player_links[0]
                if player not in origin_by_player:
                    continue
                if uni_id in SOURCE_UNIVERSES and origin_by_player[player] != name:
                    continue
                raw_score = re.sub(r"[\s.,\u00a0\u202f]", "", cells[4])
                if not raw_score.isdecimal():
                    raise ValueError(f"{player} 的積分欄位格式無法辨識")
                score = int(raw_score)
                if score > 9223372036854775807:
                    raise ValueError(f"{player} 的積分超出可處理範圍")
                scores[player] = score
                player_urls[player] = urljoin(url, href)
                alliance_links = [text for link, text in links if re.search(r"[?&]ftr=\d+\.all(?:&|$)", link)]
                alliances[player] = alliance_links[0] if alliance_links else (cells[3].strip() or "無聯盟")
                # 狀態標記在玩家欄，而非積分或整列其他欄位。
                status = re.search(r"\(([^)]*)\)", cells[2][len(player):])
                flags = status.group(1).lower() if status else ""
                modes[player] = "🏖️ 假期 (v)" if "v" in flags else "💤 不活躍 (i)" if "i" in flags else "🟢 正常"
                report["符合追蹤玩家"] += 1
            if not ranking_rows:
                raise ValueError("HTTP 200，但找不到可辨識的玩家排名列")
            report["結果"] = "讀取成功"
            report["連線狀態"] = f"HTTP {response.status_code}；宇宙與排名頁已核對"
        except (requests.RequestException, ValueError, TypeError) as exc:
            error_response = getattr(exc, "response", None)
            status_code = error_response.status_code if error_response is not None else None
            refused = status_code in (401, 403, 429) or any(
                marker in str(exc).lower()
                for marker in ("瀏覽器驗證", "connection refused", "actively refused", "10061", "econnrefused")
            )
            report["結果"] = "連線拒絕" if refused else "連線失敗"
            report["連線狀態"] = f"讀取失敗：{exc}"
            errors.append(f"{name} ({uni_id})：{exc}")
        connections.append(report)
    return destinations, modes, scores, errors, connections, player_urls, alliances


def dynamic_threat_level(score):
    if score >= 200000000000: return "二千億暴龍"
    elif score >= 100000000000: return "千億級金剛"
    elif score >= 10000000000: return "百億級巨鱷"
    elif score >= 1000000000: return "百億內對手"
    else: return "孵化中幼體"


def threat_color(score):
    if score >= 200000000000: return "#6A0DAD"  # 深紫色
    elif score >= 100000000000: return "#FF2438"  # 亮紅色
    elif score >= 10000000000: return "#804000"  # 深棕色
    elif score >= 1000000000: return "#FFB000"  # 橘黃色
    else: return "#00E640"


@st.cache_data(show_spinner=False)
def threat_lamp(color):
    # 透明背景的純色圓燈，不加外光暈或描邊。
    scale = 4
    image = Image.new("RGBA", (24 * scale, 24 * scale))
    draw = ImageDraw.Draw(image)
    draw.ellipse((5*scale, 5*scale, 19*scale, 19*scale), fill=color)
    image = image.resize((24, 24), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


# 先建立畫面，再讀取網站，避免等待期間只看到背景。
st.markdown(
    f'<div style="display:flex;align-items:center;flex-wrap:wrap;gap:12px;">'
    f'{logo_html}<h2 style="color:white;">諸神黃昏：u10-TW FazoR 併服情報站</h2></div>',
    unsafe_allow_html=True,
)
st.caption("資料依統計網站更新；未取得積分時顯示預設值。正常狀態不代表目前在線。")
if st_autorefresh is None:
    st.caption("未安裝 streamlit-autorefresh，目前使用手動更新。")
admin_controls()
# 管理者編輯時暫停自動重整，避免中斷尚未送出的修改。
if st_autorefresh is not None and not is_admin():
    st_autorefresh(interval=60000, key="datarefresh")
left_column, right_column = st.columns([1, 6])
with left_column:
    if st.button("立即重新整理"):
        fetch_and_collide_data.clear()
        st.session_state.pop("_destination_snapshot", None)
        st.session_state["_destination_generation"] = st.session_state.get("_destination_generation", 0) + 1
monitor_slot = left_column.empty()
table_slot = right_column.empty()
notice_slot = st.empty()
try:
    manual_destinations, destination_revision = read_destinations()
    destination_load_error = ""
except (requests.RequestException, ValueError, KeyError, OSError) as exc:
    manual_destinations, destination_revision = {}, None
    destination_load_error = f"手動遷徙資料讀取失敗：{exc}"
    st.error(destination_load_error)
if is_admin() and not (setting("DESTINATIONS_GITHUB_REPO") or setting("DESTINATIONS_GITHUB_TOKEN")):
    st.warning("目前使用伺服器本機儲存；雲端重啟或重新部署可能遺失。請依設定說明啟用 GitHub 永久儲存。")
if st.session_state.pop("_destination_saved", False):
    st.success("落腳新宇宙已儲存，所有訪客都能看到更新。")


def render_monitor_table(frame, player_urls=None, initial=False):
    player_urls = player_urls or {}
    with monitor_slot.container():
        universe_labels = {"Belinda": "戰術宇宙", "Cetus": "平衡宇宙", "Dione": "農夫宇宙"}
        for name in DESTINATION_OPTIONS:
            st.markdown(
                '<div class="universe-monitor-box-vertical">'
                f'<div class="universe-title-fixed">{name}</div>'
                f'<div class="universe-count-fixed">{universe_labels[name]}</div></div>', unsafe_allow_html=True,
            )
    editing = is_admin() and not initial and not destination_load_error
    if editing:
        if "_destination_snapshot" not in st.session_state:
            st.session_state["_destination_snapshot"] = (frame.copy(), dict(player_urls), destination_revision)
        frame, player_urls, edit_revision = st.session_state["_destination_snapshot"]
    columns = ["ID", "原宇宙", "落腳新宇宙", "當前玩家狀態", "實時總積分", "積分來源", "威脅程度", "備註"]
    display_frame = frame.sort_values("實時總積分", ascending=False)[columns].copy()
    display_frame.insert(display_frame.columns.get_loc("威脅程度"), "威脅燈號",
                         display_frame["實時總積分"].map(lambda score: threat_lamp(threat_color(score))))
    # 連結的片段保存顯示名稱；網址仍指向原本的玩家／宇宙來源頁。
    for index, row in frame.iterrows():
        origin_id = next(key for key, name in SOURCE_UNIVERSES.items() if name == row["原宇宙"])
        origin_url = universe_url(origin_id)
        display_frame.at[index, "原宇宙"] = f'{origin_url}#{row["原宇宙"]}'
        player_url = player_urls.get(row["ID"], origin_url).split("#", 1)[0]
        display_frame.at[index, "ID"] = f'{player_url}#{row["ID"]}'
    display_frame["_player_id"] = frame.loc[display_frame.index, "ID"]
    display_frame = display_frame.reset_index(drop=True)
    if not editing:
        display_frame["落腳新宇宙"] = display_frame["落腳新宇宙"].fillna("待確認")
    with table_slot.container():
        st.caption(f"管制共 {len(frame)} 員")
        st.subheader("即時監控情報管理表")
        st.caption("拖曳欄位標題右側邊界，即可調整欄寬。")
        column_config = {
                "_player_id": None,
                "ID": st.column_config.LinkColumn("ID", display_text=r"#(.*)$", width=175),
                "原宇宙": st.column_config.LinkColumn("原宇宙", display_text=r"#(.*)$", width=110),
                "落腳新宇宙": st.column_config.SelectboxColumn(options=DESTINATION_OPTIONS, required=False, width=120, help="僅管理者可修改；空白代表尚未指定。"),
                "當前玩家狀態": st.column_config.TextColumn(width=140),
                "實時總積分": st.column_config.NumberColumn(format="%,d", width=165),
                "積分來源": st.column_config.TextColumn(width=100),
                "威脅燈號": st.column_config.ImageColumn("燈號", width=50, help="深紫：二千億；亮紅：千億；深棕：百億；橘黃：百億內。"),
                "威脅程度": st.column_config.TextColumn(width=150),
                "備註": st.column_config.TextColumn("備註", help="mmorpg 排名頁所列聯盟；未取得玩家資料時顯示未確認。", width=130),
            }
        if editing:
            st.caption("管理者模式：雙擊「落腳新宇宙」選擇新宇宙，完成後按儲存。其他欄位僅供檢視。")
            with st.form("destination_editor_form"):
                edited = st.data_editor(
                    display_frame, hide_index=True, width="stretch", height=880,
                    column_config=column_config, num_rows="fixed",
                    disabled=[column for column in display_frame.columns if column != "落腳新宇宙"],
                    key=f"destination_editor_{st.session_state.get('_destination_generation', 0)}",
                )
                submitted = st.form_submit_button("儲存新宇宙")
            if submitted:
                try:
                    save_edited_destinations(edited, display_frame, edit_revision)
                except (PermissionError, ValueError, OSError, requests.RequestException) as exc:
                    st.error(f"儲存失敗：{exc}")
                else:
                    st.session_state.pop("_destination_snapshot", None)
                    st.session_state["_destination_generation"] = st.session_state.get("_destination_generation", 0) + 1
                    st.session_state["_destination_saved"] = True
                    st.rerun()
            if st.button("重新載入手動資料"):
                st.session_state.pop("_destination_snapshot", None)
                st.session_state["_destination_generation"] = st.session_state.get("_destination_generation", 0) + 1
                st.rerun()
        else:
            st.dataframe(display_frame, hide_index=True, width="stretch", height=880,
                         key="player_monitor_initial" if initial else "player_monitor_table",
                         column_config=column_config)


fallback = get_monster_base_data()
fallback["落腳新宇宙"] = fallback["ID"].map(manual_destinations).astype("object").where(lambda series: series.notna(), None)
fallback["當前玩家狀態"] = "讀取中"
fallback["實時總積分"] = fallback["保底積分"]
fallback["積分來源"] = "非即時"
fallback["備註"] = "未確認"
fallback["威脅程度"] = fallback["實時總積分"].apply(dynamic_threat_level)
render_monitor_table(fallback, initial=True)
notice_slot.info("正在讀取統計網站；表格已先載入預設資料。")

# 取得資料後更新表格
latest_status, latest_modes, latest_scores = {}, {}, {}
connections, player_urls, latest_alliances = [], {}, {}
try:
    latest_status, latest_modes, latest_scores, fetch_errors, connections, player_urls, latest_alliances = fetch_and_collide_data()
except Exception as exc:
    fetch_errors = [f"資料讀取失敗，使用預設保底資料：{type(exc).__name__}：{exc}"]

df_monsters = get_monster_base_data()

# 🎯 核心業務邏輯：找不到人時，狀態設定為「已遷徙或不明」
df_monsters["落腳新宇宙"] = df_monsters["ID"].map(manual_destinations).astype("object").where(lambda series: series.notna(), None)
# 只在原宇宙排名讀取成功而未找到玩家時，依設定標示已遷徙。
# 拒絕存取或一般連線錯誤不套用遷徙狀態。
origin_results = {report["宇宙"].split()[0]: report["結果"] for report in connections}


def player_status(row):
    if row["ID"] in latest_modes:
        return latest_modes[row["ID"]]
    result = origin_results.get(row["原宇宙"], "連線失敗")
    return "已遷徙" if result == "讀取成功" else result


df_monsters["當前玩家狀態"] = df_monsters.apply(player_status, axis=1)
df_monsters["實時總積分"] = df_monsters.apply(lambda r: int(latest_scores.get(r["ID"], r["保底積分"])), axis=1).astype('int64')

# 純 HTML 實心指示燈，修正回歸自訂 Table 機制
df_monsters["積分來源"] = "非即時"
df_monsters["備註"] = df_monsters["ID"].map(lambda player: latest_alliances.get(player, "未確認"))
df_monsters["威脅程度"] = df_monsters["實時總積分"].apply(dynamic_threat_level)

render_monitor_table(df_monsters, player_urls)
if fetch_errors:
    notice_slot.warning("部分統計資料讀取失敗，未取得的積分顯示預設值。已確認人數不代表實際進駐總人數。")
    with st.expander("查看資料讀取錯誤"):
        for error in fetch_errors:
            st.text(error)
elif not latest_scores:
    notice_slot.warning("網站請求完成，但未辨識到追蹤玩家；目前顯示預設資料，無法據此判斷遷徙狀態。")
else:
    notice_slot.info(f"原宇宙排名頁已讀取；取得 {len(latest_scores)} / {len(df_monsters)} 名玩家積分。未列出的玩家保留預設值。")

with st.expander("mmorpg 原宇宙連線狀態", expanded=True):
    for report in connections:
        st.markdown(f"[{report['宇宙']}]({report['來源']})：{report['連線狀態']}；找到 {report['符合追蹤玩家']} 名追蹤玩家")
    st.caption("落腳新宇宙由管理者手動指定；不查詢新三服。")
