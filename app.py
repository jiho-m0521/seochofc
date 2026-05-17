import base64
import datetime
import os
import urllib.parse
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# Google Sheet Configuration
SHEET_ID = "1n1a2Pceu9zMXTgVdIE2sKLh3f7_3I_EjgUQaa0Wua84"
RATINGS_INFO = {
    "m3": {"gid": "477587476", "skip": 3, "label": "3월"},
    "m4": {"gid": "1104693136", "skip": 3, "label": "4월"},
    "m5": {"gid": "492415984", "skip": 1, "label": "5월"},
}

# Color Constants
COLOR_PRIMARY = "#003399"
COLOR_SECONDARY = "#001a4d"
COLOR_ACCENT_GOLD = "#FFD700"
COLOR_ACCENT_RED = "#CC0000"
COLOR_TEXT_DARK = "#1a1a1a"
COLOR_TEXT_GRAY = "#888888"
COLOR_TEXT_LIGHT = "#ffffff"
COLOR_SUCCESS = "#28a745"
COLOR_ERROR = "#ff4b4b"

# UI Constants
LOGO_PATH = "image_4ba137.png"
FALLBACK_LOGO_URL = "https://cdn-icons-png.flaticon.com/512/53/53283.png"
FALLBACK_OPPONENT_LOGO_URL = "https://cdn-icons-png.flaticon.com/512/1163/1163063.png"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

import json

def get_base64_image(image_path: str) -> Optional[str]:
    """Convert an image file to base64 encoded string.
    
    Args:
        image_path: Path to the image file.
        
    Returns:
        Base64 encoded string if file exists, None otherwise.
    """
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# ---------------------------------------------------------------------------
# Data storage utilities
# ---------------------------------------------------------------------------

def ensure_data_dir() -> None:
    """Create the data directory if it does not exist."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

def save_match_details(match_id: str, details: dict) -> None:
    """Save match details to a JSON file under the data directory.
    
    Args:
        match_id: Identifier for the match, used as filename.
        details: Dictionary containing match details (score, timeline, lineup).
    """
    ensure_data_dir()
    file_path = os.path.join(os.path.dirname(__file__), "data", f"{match_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)

def load_match_details(match_id: str) -> dict:
    """Load match details from JSON if available, otherwise fall back to hard‑coded data.
    
    Args:
        match_id: Identifier for the match.
    Returns:
        Dictionary with match details.
    """
    file_path = os.path.join(os.path.dirname(__file__), "data", f"{match_id}.json")
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        # If JSON is malformed, fall back to hard‑coded data
        pass
    # Fallback to hard‑coded MATCH_DETAILS if present (try both exact and prefixed key)
    if match_id in MATCH_DETAILS:
        return MATCH_DETAILS[match_id]
    # Also try full key format "서초중 vs {match_id}" if applicable
    full_key = f"서초중 vs {match_id}"
    return MATCH_DETAILS.get(full_key, {})


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

logo_b64 = get_base64_image(LOGO_PATH)
st.set_page_config(page_title="2026 서초중 축구부", page_icon="⚽", layout="wide")

header_logo_html = f'data:image/png;base64,{logo_b64}' if logo_b64 else FALLBACK_LOGO_URL

st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 20px; padding: 10px 0px 30px 0px; border-bottom: 1px solid #eee; margin-bottom: 40px;">
        <img src="{header_logo_html}" style="width: 70px; height: 70px; object-fit: contain;">
        <div>
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 900; color: inherit; letter-spacing: -1px;">
                SEOCHO <span style="color: {COLOR_PRIMARY};">MIDDLE SCHOOL</span>
            </h1>
            <p style="margin: 0; color: {COLOR_TEXT_GRAY}; font-weight: 500; font-size: 1rem; letter-spacing: 2px;">
                2026 서초중학교 축구부 통합 관리 시스템
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)


# ============================================================================
# CSS STYLES
# ============================================================================

def get_custom_css() -> str:
    """Return all custom CSS styles as a single string.
    
    Returns:
        Combined CSS styles for the application.
    """
    return f"""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* 전체 텍스트 기본 설정 */
    html, body, [data-testid="stWidgetLabel"] p {{
        font-family: 'Pretendard', sans-serif !important;
    }}
    * {{ font-family: 'Pretendard', sans-serif !important; }}

    /* 카드 베이스: 다크/라이트 공용 */
    .report-card {{
        display: flex; 
        align-items: center; 
        justify-content: space-between; 
        background: rgba(128, 128, 128, 0.08);
        padding: 15px 25px; 
        border-radius: 12px; 
        margin-bottom: 10px; 
        border: 1px solid rgba(128, 128, 128, 0.1);
        transition: transform 0.2s ease;
    }}

    /* 타임라인 스타일 */
    .timeline-container {{
        position: relative;
        max-width: 600px;
        margin: 0 auto;
        padding: 20px 0;
    }}
    .timeline-line {{
        position: absolute;
        left: 50%;
        width: 2px;
        background: #e0e0e0;
        top: 0;
        bottom: 0;
        transform: translateX(-50%);
    }}
    .timeline-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        width: 100%;
        position: relative;
    }}
    .timeline-content {{
        width: 42%;
        padding: 12px 15px;
        border-radius: 10px;
        background: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    .timeline-center {{
        width: 10%;
        text-align: center;
        z-index: 2;
    }}
    .timeline-time-badge {{
        background: {COLOR_PRIMARY};
        color: white;
        border-radius: 50%;
        width: 35px;
        height: 35px;
        line-height: 35px;
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 700;
    }}

    /* 글자색 강제 해제: 시스템 테마를 따라가도록 */
    .dynamic-text {{
        color: inherit !important;
    }}
    .sub-text {{
        color: {COLOR_TEXT_GRAY} !important;
    }}

    /* [일반 선수] 파검 세로 줄무늬 카드 */
    .player-card {{
        background: repeating-linear-gradient(
            90deg,
            {COLOR_PRIMARY},
            {COLOR_PRIMARY} 20px,
            {COLOR_TEXT_DARK} 20px,
            {COLOR_TEXT_DARK} 40px
        );
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-bottom: 4px solid {COLOR_ACCENT_RED};
        text-align: center;
        margin-bottom: 20px;
        color: white;
    }}
    :root {{
        --text-color: rgba(255, 255, 255, 0.9);
    }}
    .player-name, .player-number {{
        color: inherit !important; 
    }}
    .ranking-card-name {{
        color: var(--text-color);
    }}

    /* [골키퍼] 노랑+주황 그라데이션 카드 */
    .gk-card {{
        background: linear-gradient(135deg, #FFD700 0%, #FF8C00 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-bottom: 4px solid {COLOR_ACCENT_RED};
        text-align: center;
        margin-bottom: 20px;
        color: {COLOR_TEXT_DARK};
    }}

    /* [관리팀] 회색 그라데이션 카드 */
    .management-card {{
        background: linear-gradient(135deg, #666666 0%, #999999 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-bottom: 4px solid {COLOR_ACCENT_RED};
        text-align: center;
        margin-bottom: 20px;
        color: white;
    }}

    /* [일정] 녹색 그라데이션 카드 */
    .schedule-card {{
        background: linear-gradient(135deg, #228B22 0%, #32CD32 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-bottom: 4px solid {COLOR_ACCENT_RED};
        text-align: center;
        margin-bottom: 20px;
        color: white;
    }}

    .player-number {{ font-size: 1.5rem; font-weight: 800; margin-bottom: 5px; }}
    .player-name {{ font-size: 1.2rem; font-weight: 600; margin: 5px 0; }}

    /* 포지션 태그 가독성 조정 */
    .player-pos {{
        font-size: 0.8rem;
        padding: 2px 10px;
        border-radius: 5px;
        background: rgba(255,255,255,0.2);
        color: inherit;
        border: 1px solid rgba(255,255,255,0.3);
    }}

    /* TOP 3 카드 스타일 유지 */
    [data-testid="stMetric"] {{
        padding: 15px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stMetric"] {{ background: linear-gradient(135deg, #FFD700 0%, #FFB900 100%) !important; }}
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetric"] {{ background: linear-gradient(135deg, #E0E0E0 0%, #BDBDBD 100%) !important; }}
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetric"] {{ background: linear-gradient(135deg, #D2B48C 0%, #A0522D 100%) !important; }}
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {{ color: {COLOR_TEXT_DARK} !important; font-weight: 700 !important; }}

    .logo-img {{
        filter: drop-shadow(0 0 5px rgba(255,255,255,0.5));
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }}

    /* 내비게이션 컨테이너 */
    .nav-container {{
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 30px;
    }}
    /* 버튼 공통 스타일 */
    .stButton > button {{
        width: 100%;
        border-radius: 50px;
        border: 1px solid #eee;
        background-color: white;
        color: #555;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    /* 마우스 호버 효과 */
    .stButton > button:hover {{
        border-color: {COLOR_PRIMARY};
        color: {COLOR_PRIMARY};
        background-color: #f8faff;
    }}
    /* 활성화된 버튼 스타일 */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, {COLOR_SECONDARY} 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,51,153,0.3) !important;
    }}
    /* NEXT MATCH 카드 클릭 버튼에 텍스트 입히기 */
    button[key="next_match_click"] {{
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        background: transparent !important;
        border: none !important;
        cursor: pointer !important;
        z-index: 10 !important;
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        display: flex !important;
        align-items: flex-end !important;
        justify-content: center !important;
        padding-bottom: 15px !important;
        transition: all 0.3s ease !important;
    }}
    button[key="next_match_click"]:hover {{
        color: {COLOR_ACCENT_GOLD} !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }}
    </style>
    """


st.markdown(get_custom_css(), unsafe_allow_html=True)



# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data(ttl=600)
def load_data() -> Dict[str, pd.DataFrame]:
    """Load all data from local files and Google Sheets.
    
    Returns:
        Dictionary containing DataFrames for roster, schedule, management,
        and monthly ratings (m3, m4, m5).
    """
    files = os.listdir('.')
    data: Dict[str, pd.DataFrame] = {}
    
    # Load local files (roster, schedule)
    local_keys = {"roster": "로스터", "schedule": "일정"}
    for k, v in local_keys.items():
        target = [f for f in files if v in f and f.endswith('.csv')]
        if target:
            skip = 7 if "로스터" in target[0] else 3
            df = pd.read_csv(target[0], skiprows=skip)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df = df.dropna(subset=['이름']) if '이름' in df.columns else df
            data[k] = df
        else:
            data[k] = pd.DataFrame()

    # Add management data
    data['management'] = pd.DataFrame({
        '이름': ['장순현 선생님', '신예준'],
        '역할': ['체육안전부', '매니저 (3학년 1반)']
    })

    # Load Google Sheets data (monthly ratings)
    for k, info in RATINGS_INFO.items():
        safe_gid = urllib.parse.quote(str(info['gid']))
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={safe_gid}"
        
        try:
            df = pd.read_csv(url, skiprows=info['skip'], encoding='utf-8')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df = df.dropna(subset=['이름']) if '이름' in df.columns else df
            
            col = f"{info['label']} 평균평점"
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            data[k] = df
        except Exception as e:
            st.error(f"구글 시트 {info['label']} 로드 실패: {e}")
            data[k] = pd.DataFrame()
            
    return data


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_date(raw_date: str, year: int = 2026) -> str:
    """Format date string to Korean format.
    
    Args:
        raw_date: Raw date string (e.g., "May 15", "5.15", etc.)
        year: Year to use for formatting (default: 2026)
        
    Returns:
        Formatted date string in Korean format (e.g., "2026년 05월 15일")
    """
    try:
        if isinstance(raw_date, str) and raw_date.strip():
            parsed = pd.to_datetime(f"{year} {raw_date}", format="%Y %b %d")
            return parsed.strftime(f"{year}년 %m월 %d일")
        return str(raw_date)
    except:
        return str(raw_date)


def get_rating_tier(score: float) -> Tuple[str, str]:
    """Determine rating tier and color based on score.
    
    Args:
        score: Numeric rating score
        
    Returns:
        Tuple of (tier_label, color_hex)
    """
    if pd.isna(score) or score == 0:
        return "-", "#888888"
    elif score >= 7.0:
        return "A", COLOR_ERROR
    elif score >= 6.5:
        return "B", COLOR_PRIMARY
    else:
        return "C", "#555555"


def get_opponent_logo(opponent_name: str) -> str:
    """Get opponent logo as base64 or fallback URL.
    
    Args:
        opponent_name: Name of the opponent team
        
    Returns:
        Base64 data URL or fallback image URL
    """
    opp_logo_b64 = get_base64_image(f"{opponent_name}.png")
    return f'data:image/png;base64,{opp_logo_b64}' if opp_logo_b64 else FALLBACK_OPPONENT_LOGO_URL


# ============================================================================
# DATA INITIALIZATION
# ============================================================================

df_all = load_data()

# ============================================================================
# MATCH DETAILS DATA
# ============================================================================

MATCH_DETAILS = {
    '서초중 vs 방배중': {
        'formation': '4-3-3',
        'lineup': {
            'GK': ['주상현'],
            'DF': ['김시우', '민지호', '박준환', '고은성'],
            'MF': ['임종헌', '노하율', '조영규'],
            'FW': ['목정민', '김진우', '황지석']
        },
        'bench': ['김도훈', '김형준', '전현준', '정태공', '양승민'],
        'stats': {
            '서초중': {'shots': 12, 'passes': 245, 'possession': 55},
            '방배중': {'shots': 8, 'passes': 198, 'possession': 45}
        },
        'events': [
            {'time': '15\'', 'event': '⚽ 골 - 노하율 (서초중)', 'type': 'goal'},
            {'time': '30\'', 'event': '🔄 교체 - 김진우 OUT, 황지석 IN (서초중)', 'type': 'sub'},
            {'time': '45\'', 'event': '🟨 옐로카드 - 김시우 (서초중)', 'type': 'card'},
            {'time': '60\'', 'event': '⚽ 골 - 방배중 선수', 'type': 'goal'},
            {'time': '75\'', 'event': '🔄 교체 - 민지호 OUT, 김형준 IN (서초중)', 'type': 'sub'}
        ]
    },
    '서초중 vs 이수중': {
        'formation': '4-4-2',
        'lineup': {
            'GK': ['김도훈'],
            'DF': ['김형준', '전현준', '정태공', '양승민'],
            'MF': ['이기윤', '이새누엘', '유용준', '조하윤'],
            'FW': ['임종헌', '노하율']
        },
        'bench': ['주상현', '김시우', '민지호', '박준환', '고은성'],
        'stats': {
            '서초중': {'shots': 10, 'passes': 220, 'possession': 50},
            '이수중': {'shots': 9, 'passes': 215, 'possession': 50}
        },
        'events': [
            {'time': '10\'', 'event': '🟨 옐로카드 - 이수중 선수', 'type': 'card'},
            {'time': '25\'', 'event': '⚽ 골 - 임종헌 (서초중)', 'type': 'goal'},
            {'time': '50\'', 'event': '🔄 교체 - 유용준 OUT, 조영규 IN (서초중)', 'type': 'sub'},
            {'time': '70\'', 'event': '⚽ 골 - 이수중 선수', 'type': 'goal'},
            {'time': '85\'', 'event': '🔄 교체 - 노하율 OUT, 목정민 IN (서초중)', 'type': 'sub'}
        ]
    },
    '서초중 vs 내곡중': {
        'formation': '3-5-2',
        'lineup': {
            'GK': ['주상현'],
            'DF': ['김시우', '민지호', '박준환'],
            'MF': ['고은성', '임종헌', '노하율', '조영규', '김진우'],
            'FW': ['황지석', '목정민']
        },
        'bench': ['김도훈', '김형준', '전현준', '정태공', '양승민'],
        'stats': {
            '서초중': {'shots': 15, 'passes': 260, 'possession': 60},
            '내곡중': {'shots': 7, 'passes': 180, 'possession': 40}
        },
        'events': [
            {'time': '5\'', 'event': '⚽ 골 - 황지석 (서초중)', 'type': 'goal'},
            {'time': '20\'', 'event': '🔄 교체 - 김진우 OUT, 전현준 IN (서초중)', 'type': 'sub'},
            {'time': '40\'', 'event': '🟨 옐로카드 - 내곡중 선수', 'type': 'card'},
            {'time': '65\'', 'event': '⚽ 골 - 목정민 (서초중)', 'type': 'goal'},
            {'time': '80\'', 'event': '🔄 교체 - 조영규 OUT, 이기윤 IN (서초중)', 'type': 'sub'}
        ]
    },
    '서초중 vs 언남중': {
        'formation': '4-2-3-1',
        'lineup': {
            'GK': ['김도훈'],
            'DF': ['김형준', '전현준', '정태공', '양승민'],
            'MF': ['이기윤', '이새누엘', '유용준'],
            'FW': ['조하윤']
        },
        'bench': ['주상현', '김시우', '민지호', '박준환', '고은성'],
        'stats': {
            '서초중': {'shots': 8, 'passes': 200, 'possession': 48},
            '언남중': {'shots': 11, 'passes': 230, 'possession': 52}
        },
        'events': [
            {'time': '12\'', 'event': '🟨 옐로카드 - 양승민 (서초중)', 'type': 'card'},
            {'time': '35\'', 'event': '⚽ 골 - 언남중 선수', 'type': 'goal'},
            {'time': '55\'', 'event': '🔄 교체 - 이새누엘 OUT, 임종헌 IN (서초중)', 'type': 'sub'},
            {'time': '70\'', 'event': '⚽ 골 - 조하윤 (서초중)', 'type': 'goal'},
            {'time': '90\'', 'event': '🔄 교체 - 유용준 OUT, 노하율 IN (서초중)', 'type': 'sub'}
        ]
    }
}

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'menu_option' not in st.session_state:
    st.session_state.menu_option = "🏠 홈 (MATCHDAY)"
if 'selected_match' not in st.session_state:
    st.session_state.selected_match = None


# ============================================================================
# NAVIGATION
# ============================================================================

def render_navigation() -> str:
    """Render navigation buttons and return current menu option.
    
    Returns:
        Current selected menu option.
    """
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("🏠 MATCHDAY", use_container_width=True,
                     type="primary" if st.session_state.menu_option == "🏠 홈 (MATCHDAY)" else "secondary"):
            st.session_state.menu_option = "🏠 홈 (MATCHDAY)"
            st.rerun()
    with c2:
        if st.button("🏃 SQUAD", use_container_width=True,
                     type="primary" if st.session_state.menu_option == "🏃 선수단 명단" else "secondary"):
            st.session_state.menu_option = "🏃 선수단 명단"
            st.rerun()
    with c3:
        if st.button("📅 SCHEDULE", use_container_width=True,
                     type="primary" if st.session_state.menu_option == "📅 SCHEDULE" else "secondary"):
            st.session_state.menu_option = "📅 SCHEDULE"
            st.rerun()
    with c4:
        if st.button("📊 ANALYSIS", use_container_width=True,
                     type="primary" if st.session_state.menu_option == "📊 성적 분석" else "secondary"):
            st.session_state.menu_option = "📊 성적 분석"
            st.rerun()
    with c5:
        if st.button("데이터 입력", use_container_width=True,
                     type="primary" if st.session_state.menu_option == "데이터 입력" else "secondary"):
            st.session_state.menu_option = "데이터 입력"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    return st.session_state.menu_option


menu = render_navigation()


# ============================================================================
# PAGE RENDERING
# ============================================================================

# ============================================================================
# HOME PAGE (MATCHDAY)
# ============================================================================
if menu == "🏠 홈 (MATCHDAY)":
    st.markdown("<h2 style='font-weight:700; color:inherit;'>STADIUM NEWS</h2>", unsafe_allow_html=True)
    sched = df_all['schedule']
    if not sched.empty:
        next_m = sched.dropna(subset=['상대']).iloc[0]
        opp = next_m['상대'].replace('vs ', '').strip()
        
        formatted_date = format_date(str(next_m['날짜']))
        logo_html = f'data:image/png;base64,{logo_b64}' if logo_b64 else FALLBACK_LOGO_URL
        opp_logo_html = get_opponent_logo(opp)

        # 클릭 가능한 카드
        with st.container():
            st.markdown(f"""
                <div style="position: relative;">
                    <div style="background: linear-gradient(135deg, #1a1a1a 0%, #333 100%); padding: 40px 20px; border-radius: 25px; color: white; text-align: center;">
                        <p style="letter-spacing: 5px; color: #ff4b4b; font-weight: 600; font-size:0.9rem; margin-bottom:20px;">NEXT MATCH</p>
                        <div style="display: flex; align-items: center; justify-content: center; gap: 30px; flex-wrap: wrap;">
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <img src="{logo_html}" style="width:60px; height:60px; object-fit:contain;">
                                <h1 style="font-size: 2.5rem; font-weight: 800; margin:0; color:white;">서초중학교</h1>
                            </div>
                            <div style="font-size: 1.5rem; font-weight: 300; color: #888;">VS</div>
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <h1 style="font-size: 2.5rem; font-weight: 800; color: #bbb; margin:0;">{opp}</h1>
                                <img src="{opp_logo_html}" style="width:60px; height:60px; object-fit:contain;">
                            </div>
                        </div>
                        <div style="margin-top: 30px; display: flex; justify-content: center; gap: 15px;">
                            <span style="background: rgba(255,255,255,0.1); padding: 8px 20px; border-radius: 10px;">🗓️ {formatted_date} {next_m.get('시간', '')}</span>
                            <span style="background: rgba(255,255,255,0.1); padding: 8px 20px; border-radius: 10px;">📍 {next_m.get('장소', '')}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        if st.button("📅 경기 일정 보기", key="next_match_click", use_container_width=True):
            st.session_state.menu_option = "📅 SCHEDULE"
            st.rerun()

    # --- [2. 5월 우수 선수 TOP 3 출력 강화] --- 
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-weight:700;'>🌟 5월의 우수 선수 (TOP 3)</h3>", unsafe_allow_html=True)
    df5 = df_all['m5'].copy()
    
    if not df5.empty and '5월 평균평점' in df5.columns:
        # 평점 데이터를 확실하게 숫자로 변환 
        df5['5월 평균평점'] = pd.to_numeric(df5['5월 평균평점'], errors='coerce')
        top3 = df5.dropna(subset=['5월 평균평점']).nlargest(3, '5월 평균평점')
        
        if not top3.empty:
            cols = st.columns(3)
            medals = ["🥇 1st", "🥈 2nd", "🥉 3rd"]
            for i, (idx, row) in enumerate(top3.iterrows()):
                with cols[i]:
                    st.metric(
                        label=f"{medals[i]} - {row['포지션']}", 
                        value=f"{row['이름']}", 
                        delta=f"{row['5월 평균평점']:.2f} pts"
                    )
        else:
            st.info("TOP 3를 선정할 평점 데이터가 없습니다.")
    else:
        st.warning("5월 평점 데이터를 불러올 수 없습니다.")


# ============================================================================
# SCHEDULE PAGE
# ============================================================================
elif menu == "📅 SCHEDULE":
    st.markdown("<h1 style='font-weight:800; margin-bottom:30px;'>MATCH SCHEDULE</h1>", unsafe_allow_html=True)
    df_schedule = df_all['schedule']
    
    if not df_schedule.empty:
        cols = st.columns(2)
        for i, (idx, match) in enumerate(df_schedule.iterrows()):
            with cols[i % 2]:
                # 데이터 추출
                opp = match['상대'].replace('vs ', '').strip() if '상대' in match else 'TBD'
                formatted_date = format_date(match.get('날짜', 'TBD'))
                
                time = match.get('시간', 'TBD')
                venue = match.get('장소', 'TBD')
                stage = match.get('스테이지', 'TBD')
                
                # --- [수정 부분] 결과값 처리 ---
                result = match.get('결과', '')
                # 결과가 nan이거나 비어있으면 '킥오프 전'으로 표시
                if pd.isna(result) or str(result).lower() == 'nan' or not str(result).strip():
                    display_result = "킥오프 전"
                    result_color = "#FF0000" # 대기 중인 느낌의 빨간색
                else:
                    display_result = f"결과: {result}"
                    result_color = "#000000" # 결과가 있을 땐 강조색(검정)

                with st.container():
                    # 1. 디자인 카드
                    st.markdown(f"""
                        <div style="position: relative;">
                            <div class="schedule-card" style="padding-bottom: 60px; margin-bottom: 0px;">
                                <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 10px;">{opp}</div>
                                <div style="font-size: 0.9rem; margin-bottom: 5px;">📅 {formatted_date} {time}</div>
                                <div style="font-size: 0.9rem; margin-bottom: 5px;">📍 {venue}</div>
                                <div style="font-size: 0.8rem; margin-bottom: 5px;">🏆 {stage}</div>
                                <div style="font-size: 0.8rem; color: {result_color}; font-weight: 600;">{display_result}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # 2. 버튼 위에 텍스트 새기기
                    if st.button("상세 정보 확인 🔍", key=f"sched_btn_{i}", use_container_width=True):
                        st.session_state.selected_match = match.to_dict()
                        st.session_state.menu_option = "📋 DETAIL"
                        st.rerun()
    else:
        st.info("일정 데이터를 불러올 수 없습니다.")


# ============================================================================
# DATA ENTRY PAGE
# ============================================================================
elif menu == "데이터 입력":
    # Password protection for data input
    pwd_data = st.text_input("데이터 입력 비밀번호", type="password", key="pwd_data")
    if pwd_data != "sdata":
        st.warning("비밀번호가 올바르지 않습니다.")
        st.stop()
    st.markdown("<h1 style='font-weight:800; margin-bottom:30px;'>데이터 입력</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
            <p style="margin: 0; color: #555;">경기 상세 정보를 JSON 파일로 저장합니다. 아래 양식을 작성하세요.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Match ID 입력
    match_id = st.text_input("경기 ID (예: match_2026_06_05)", placeholder="match_YYYY_MM_DD 형식 추천")
    
    # Score 입력
    score = st.text_input("결과 (예: 2:1)", placeholder="서초중:상대점수 형식")
    
    # Timeline 입력
    timeline_input = st.text_area("타임라인 (한 줄에 하나씩, 형식: 분 - 내용)",
                                   placeholder="예:\n15 - 홍길동 선수가 골을 넣었다\n30 - 홍길동 선수가 교체 아웃되었습니다.",
                                   height=150)
    
    # Lineup 입력
    lineup_input = st.text_area("라인업 (한 줄에 하나씩)",
                                 placeholder="예:\n주상현\n김시우\n민지호",
                                 height=150)
    
    # Submit 버튼
    if st.button("💾 저장하기", use_container_width=True, type="primary"):
        # Validation
        errors = []
        if not match_id:
            errors.append("경기 ID를 입력해주세요.")
        if not score:
            errors.append("결과를 입력해주세요.")
        
        if errors:
            for err in errors:
                st.error(err)
        else:
            # Parse timeline
            timeline = []
            if timeline_input.strip():
                for line in timeline_input.strip().split('\n'):
                    if ' - ' in line:
                        parts = line.split(' - ', 1)
                        try:
                            minute = int(parts[0].strip())
                            event = parts[1].strip()
                            timeline.append({'minute': minute, 'event': event})
                        except ValueError:
                            st.warning(f"분을 숫자로 변환할 수 없습니다: {line}")
            
            # Parse lineup
            lineup = []
            if lineup_input.strip():
                lineup = [p.strip() for p in lineup_input.strip().split('\n') if p.strip()]
            
            # Build details dict
            details = {
                'score': score,
                'timeline': timeline,
                'lineup': lineup
            }
            
            # Save
            try:
                save_match_details(match_id, details)
                st.success(f"✅ {match_id} 데이터가 저장되었습니다!")
                st.json(details)
            except Exception as e:
                st.error(f"저장 중 오류가 발생했습니다: {e}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("데이터는 `data/` 디렉토리에 `<match_id>.json` 파일로 저장됩니다.")


# ============================================================================
# SQUAD ROSTER PAGE
# ============================================================================
elif menu == "🏃 선수단 명단":
    st.markdown("<h1 style='font-weight:800; margin-bottom:30px;'>SQUAD ROSTER</h1>", unsafe_allow_html=True)
    
    # Management 섹션
    st.markdown("<h2 style='font-weight:700; margin-bottom:20px;'>TEAM MANAGEMENT</h2>", unsafe_allow_html=True)
    df_management = df_all['management']
    if not df_management.empty:
        cols = st.columns(2)  # Management는 2명이라 2칼럼
        for i, (idx, member) in enumerate(df_management.iterrows()):
            with cols[i % 2]:
                st.markdown(f"""
                    <div class="management-card">
                        <div class="player-name">{member['이름']}</div>
                        <span class="player-pos">{member['역할']}</span>
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Roster 섹션
    st.markdown("<h2 style='font-weight:700; margin-bottom:20px;'>TEAM ROSTER</h2>", unsafe_allow_html=True)
    df_roster = df_all['roster']
    if not df_roster.empty:
        cols = st.columns(4)
        for i, (idx, player) in enumerate(df_roster.iterrows()):
            is_gk = player['포지션'] == 'GK'
            card_class = "gk-card" if is_gk else "player-card"
            
            # 선수 카드 렌더링
            with cols[i % 4]:
                st.markdown(f"""
                    <div class="{card_class}">
                        <div class="player-number">No.{int(player['등번호']) if '등번호' in player else '??'}</div>
                        <div class="player-name">{player['이름']}</div>
                        <span class="player-pos">{player['포지션']}</span>
                    </div>
                """, unsafe_allow_html=True)


# ============================================================================
# MATCH DETAIL PAGE
# ============================================================================
elif menu == "📋 DETAIL":
    # 선택된 경기 데이터 확인
    match = st.session_state.get('selected_match', None)
    
    if match is None:
        # 데이터가 없을 때의 예외 처리
        if not df_all['schedule'].empty:
            # 가장 가까운 경기를 기본값으로 세팅 (자동 복구)
            match = df_all['schedule'].iloc[0].to_dict()
            st.session_state.selected_match = match
        else:
            st.warning("표시할 경기 데이터가 없습니다. 일정 페이지에서 경기를 선택해주세요.")
            st.stop()

    if match:
        opp = match['상대'].replace('vs ', '').strip()
        # 뒤로가기 버튼
        if st.button("⬅ 일정 목록으로 돌아가기"):
            st.session_state.menu_option = "📅 SCHEDULE"
            st.rerun()

        # Load stored match details (fallback to hard‑coded)
        details = load_match_details(f"서초중 vs {opp}")

        # 1. 경기 요약 헤더 카드
        result_text = details.get('score', match.get('결과', ''))
        status_text = "킥오프 전" if pd.isna(result_text) or str(result_text).lower() == 'nan' or not str(result_text).strip() else f"결과: {result_text}"
        
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #003399 0%, #001a4d 100%);
                        padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px; text-align: center;">
                <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 10px;">{match.get('스테이지', 'MATCH DETAILS')}</div>
                <div style="font-size: 2rem; font-weight: 800; margin-bottom: 15px;">서초 FC vs {opp}</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #FFD700;">{status_text}</div>
                <div style="margin-top: 15px; font-size: 0.85rem; opacity: 0.9;">
                    📅 {match.get('날짜', '')} {match.get('시간', '')} | 📍 {match.get('장소', '')}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 2. 상세 정보 탭 구성 (라인업 / 경기 기록)
        tab1, tab2, tab3 = st.tabs(["🏃 LINEUP", "📊 STATS", "⏱️ TIMELINE"])

        with tab1:
            st.subheader("선발 명단")
            lineup = details.get('lineup', [])
            if lineup:
                lineup_html = "".join([f'<span style="background:#f0f2f6; padding:5px 12px; border-radius:15px; margin:5px; display:inline-block; font-weight:600; color:#003399;">{p}</span>' for p in lineup])
                st.markdown(lineup_html, unsafe_allow_html=True)
            else:
                st.info("등록된 라인업 정보가 없습니다.")

        with tab2:
            st.subheader("경기 통계")
            # Placeholder stats – can be extended later
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("득점", result_text.split(':')[0] if ':' in str(result_text) else "-")
            with col2:
                st.metric("실점", result_text.split(':')[1] if ':' in str(result_text) else "-")
            with col3:
                st.metric("장소", match.get('장소', '-'))

        with tab3:
            st.subheader("Match Timeline")
            timeline = details.get('timeline', [])
            # Convert to events list for rendering
            events = []
            for entry in timeline:
                minute = entry.get('minute')
                ev = entry.get('event', '')
                # Simple heuristic: assume home events contain "서초중" or no team indicator
                team = 'home' if '서초중' in ev else 'away'
                events.append((minute, team, ev, ''))
            events.sort(key=lambda x: x[0])
            
            st.markdown('<div class="timeline-container"><div class="timeline-line"></div>', unsafe_allow_html=True)
            for time, team, event, player in events:
                if team == 'home':
                    st.markdown(f"""
                        <div class="timeline-item">
                            <div class="timeline-content" style="text-align: right; border-right: 4px solid #003399;">
                                <div style="font-weight: 700; color: #28a745;">{event}</div>
                            </div>
                            <div class="timeline-center">
                                <span class="timeline-time-badge">{time}'</span>
                            </div>
                            <div style="width: 40%;"></div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="timeline-item">
                            <div style="width: 40%;"></div>
                            <div class="timeline-center">
                                <span class="timeline-time-badge" style="background: #ff4b4b;">{time}'</span>
                            </div>
                            <div class="timeline-content" style="text-align: left; border-left: 4px solid #ff4b4b;">
                                <div style="font-weight: 700; color: #ff4b4b;">{event}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 비고(Notes) 섹션
            notes = details.get('notes', match.get('비고', '-'))
            if notes and str(notes) != 'nan':
                st.write("---")
                st.markdown(f"**📝 매치 리포트**")
                st.info(notes)

    else:
        st.warning("경기를 선택해주세요. 'SCHEDULE' 메뉴에서 경기를 클릭하면 상세 내용을 볼 수 있습니다.")
        if st.button("일정 확인하러 가기"):
            st.session_state.menu_option = "📅 SCHEDULE"
            st.rerun()


# ============================================================================
# PERFORMANCE ANALYSIS PAGE
# ============================================================================
elif menu == "📊 성적 분석":
    # Password protection for analysis page
    pwd_analysis = st.text_input("분석 페이지 비밀번호", type="password", key="pwd_analysis")
    if pwd_analysis != "sratings":
        st.warning("비밀번호가 올바르지 않습니다.")
        st.stop()
    st.markdown("<h1 style='font-weight:800; color:inherit;'>PERFORMANCE REPORT</h1>", unsafe_allow_html=True)
    
    # [수정] 드롭다운을 분석 페이지 최상단에 배치 (디자인 일관성)
    # columns를 활용해 드롭다운 너비를 조절하면 더 깔끔합니다.
    sel_col1, sel_col2 = st.columns([1, 2])
    with sel_col1:
        month = st.selectbox("📅 분석 기간 선택", ["5월", "4월", "3월"], label_visibility="visible")
    
    # 데이터 매칭용 키 설정
    m_key = {"5월": "m5", "4월": "m4", "3월": "m3"}[month]
    col_name = f"{month} 평균평점"
    
    df_roster = df_all['roster'].copy()
    df_m = df_all[m_key].copy()

    # 상단 탭 구성 (월간 요약 vs 경기별 상세)
    tab1, tab2 = st.tabs(["📅 월간 평균 리포트", "🏟️ 경기별 상세 평점"])

    # --- TAB 1: 월간 평균 리스트 ---
    with tab1:
        if not df_roster.empty:
            if not df_m.empty and col_name in df_m.columns:
                df_final = pd.merge(df_roster[['이름', '포지션', '등번호']], 
                                    df_m[['이름', col_name]], 
                                    on='이름', how='left')
            else:
                df_final = df_roster[['이름', '포지션', '등번호']].copy()
                df_final[col_name] = None

            df_final = df_final.sort_values(col_name, ascending=False, na_position='last')
            
            st.markdown(f"### 📋 {month} 전체 스쿼드 시즌 평점")
            
            for i, (idx, row) in enumerate(df_final.iterrows()):
                score = row[col_name]
                tier, color = get_rating_tier(score)
                score_display = "N/A" if tier == "-" else f"{score:.2f}"
                
                st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; background: white; padding: 15px 25px; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 5px solid {color};">
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <span style="font-weight: 800; color: #bbb; width: 25px;">{i+1}</span>
                            <div>
                                <div style="font-weight: 700; font-size: 1.1rem; color: #1a1a1a;">{row['이름']} <span style="font-size: 0.8rem; color: #999; font-weight: 400;">No.{int(row['등번호']) if pd.notna(row['등번호']) else '??'}</span></div>
                                <div style="font-size: 0.8rem; color: #666;">{row['포지션']} | SEOCHO MIDDLE SCHOOL</div>
                            </div>
                        </div>
                        <div style="text-align: right; display: flex; align-items: center; gap: 15px;">
                            <div style="text-align: center;"><div style="font-size: 0.7rem; color: #999; margin-bottom: -3px;">RATING</div><div style="font-size: 1.3rem; font-weight: 900; color: {color};">{score_display}</div></div>
                            <div style="background: {color}; color: white; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1.2rem;">{tier}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # --- TAB 2: [신규 기능] 특정 일자별 상세 평점 ---
# --- TAB 2: 경기별 상세 평점 ---
    with tab2:
        if not df_m.empty:
            # 날짜 컬럼 추출
            date_cols = [c for c in df_m.columns if any(char.isdigit() for char in c) and '평균' not in c]
            
            if date_cols:
                # 1. 대상 날짜(오늘 또는 금요일) 계산
                today = datetime.datetime.now()
                weekday = today.weekday() # 5:토, 6:일
                
                if weekday == 5: target_dt = today - datetime.timedelta(days=1)
                elif weekday == 6: target_dt = today - datetime.timedelta(days=2)
                else: target_dt = today
                
                # 2. 매칭 시도 (다양한 형식 대응: 5.10, 5/10, 05.10 등)
                m = str(target_dt.month)
                d = str(target_dt.day)
                mm = target_dt.strftime('%m')
                dd = target_dt.strftime('%d')
                
                # 찾고자 하는 후보들
                targets = [f"{m}.{d}", f"{m}/{d}", f"{mm}.{dd}", f"{mm}/{dd}"]
                
                default_index = len(date_cols) - 1 # 매칭 실패 시 최신 날짜
                
                for idx, col in enumerate(date_cols):
                    # 컬럼명에 위 후보 중 하나라도 포함되어 있으면 선택
                    if any(t in col for t in targets):
                        default_index = idx
                        break
                
                # 3. 날짜 선택 UI
                selected_date = st.selectbox("📅 경기 일자 선택", date_cols, index=default_index)
                # 2. 데이터 분리 ('평균' 행 vs 일반 선수 행)
                avg_row = df_m[df_m['이름'].str.contains('평균', na=False)]
                df_players_only = df_m[~df_m['이름'].str.contains('평균', na=False)].copy()
                
                # 해당 날짜 데이터만 추출 및 정렬
                df_match = df_players_only[['이름', selected_date]].dropna(subset=[selected_date])
                df_match = df_match.sort_values(selected_date, ascending=False)

                # 3. 팀 전체 평균 표시 (최상단)
                if not avg_row.empty:
                    raw_avg = avg_row.iloc[0][selected_date]
                    total_avg_score = pd.to_numeric(raw_avg, errors='coerce')
                    
                    if pd.notna(total_avg_score):
                        st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #003399 0%, #1a1a1a 100%); 
                                        padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 25px; 
                                        box-shadow: 0 10px 20px rgba(0,0,0,0.2); border-bottom: 5px solid #CC0000;">
                                <p style="color: #FFD700; font-size: 1.1rem; font-weight: 700; margin-bottom: 10px; letter-spacing: 2px;">TEAM AVERAGE</p>
                                <h1 style="color: white; font-size: 3.5rem; font-weight: 900; margin: 0;">{float(total_avg_score):.2f}</h1>
                                <p style="color: rgba(255,255,255,0.6); margin-top: 10px;">{selected_date} 경기 팀 전체 퍼포먼스 수치</p>
                            </div>
                        """, unsafe_allow_html=True)

                # 4. 그래프 출력
                st.markdown(f"#### 📈 {selected_date} 선수별 평점 그래프")
                fig = px.bar(df_match, x='이름', y=selected_date, 
                             color=selected_date, 
                             color_continuous_scale='RdBu_r',
                             range_color=[5.5, 8.5],
                             text_auto='.1f')
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                    height=350, margin=dict(l=10, r=10, t=10, b=10),
                    xaxis_title=None, yaxis_title="Rating"
                )
                st.plotly_chart(fig, use_container_width=True)

                # 5. 개별 선수 명단 리스트 (한 줄 나열 + 평점 내림차순 정렬)
                st.markdown(f"#### 📋 개별 선수 랭킹")

                if not df_match.empty:
                    # --- 데이터 준비 및 내림차순 정렬 ---
                    rating_data = []
                    for i, row in df_match.iterrows():
                        p_name = row['이름']
                        p_score = pd.to_numeric(row[selected_date], errors='coerce')
                        
                        if pd.notna(p_score):
                            tier, color = get_rating_tier(p_score)
                            
                            rating_data.append({
                                'name': p_name,
                                'score': float(p_score),
                                'tier': tier,
                                'color': color
                            })

                    # 평점(score) 기준 내림차순 정렬
                    rating_data = sorted(rating_data, key=lambda x: x['score'], reverse=True)

                    # --- 일자로 쭉 나열 (st.columns를 사용하지 않음) ---
                    for idx, p in enumerate(rating_data):
                        st.markdown(f"""
                            <div style="background: white; padding: 15px 20px; border-radius: 12px; border: 1px solid #eee; 
                                        margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; 
                                        box-shadow: 0 2px 5px rgba(0,0,0,0.02); border-left: 5px solid {p['color']};">
                                <div style="display:flex; align-items:center; gap:12px;">
                                    <span style="color:#ccc; font-weight:800; font-size:1.1rem; width:25px;">{idx+1}</span>
                                    <div>
                                        <div style="font-weight: 700; color:#1a1a1a; font-size:1.05rem; display:flex; align-items:center; gap:8px;">
                                            {p['name']}
                                            <span style="background:{p['color']}; color:white; font-size:0.7rem; padding:1px 6px; border-radius:4px;">{p['tier']}</span>
                                        </div>
                                    </div>
                                </div>
                                <div style="background: #f0f2f6; color: #003399; padding: 5px 15px; border-radius: 20px; font-weight: 800; font-size: 1rem;">
                                    {p['score']:.1f}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("기록된 선수 평점이 없습니다.")