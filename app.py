import streamlit as st

import pandas as pd

import plotly.express as px

import os
import datetime
import base64

import urllib.parse

def get_base64_image(image_path):

    if os.path.exists(image_path):

        with open(image_path, "rb") as f:

            return base64.b64encode(f.read()).decode()

    return None


# 1. 페이지 설정
logo_b64 = get_base64_image("image_4ba137.png")
st.set_page_config(page_title="2026 서초중 축구부", page_icon="⚽", layout="wide")

# --- [상단 네비바] ---
query_params = st.query_params
menu_key = query_params.get("menu", ["home"])[0] if query_params else "home"
if menu_key not in ["home", "roster", "report"]:
    menu_key = "home"

menu = "🏠 홈 (MATCHDAY)"
if menu_key == "roster":
    menu = "🏃 선수단 명단"
elif menu_key == "report":
    menu = "📊 성적 분석"

nav_html = f"""
    <style>
    .top-navbar {{ display: flex; justify-content: center; gap: 16px; padding: 16px 0; background: #003399; position: sticky; top: 0; z-index: 999; box-shadow: 0 3px 12px rgba(0,0,0,0.12); margin-bottom: 24px; }}
    .top-navbar a {{ color: #ffffff; text-decoration: none; padding: 12px 22px; border-radius: 999px; font-size: 1rem; font-weight: 700; transition: all 0.18s ease; border: 1px solid transparent; }}
    .top-navbar a:hover {{ background: rgba(255,255,255,0.14); }}
    .top-navbar a.active {{ background: #ffffff; color: #003399; border-color: rgba(255,255,255,0.4); }}
    </style>
    <div class="top-navbar">
        <a class="{'active' if menu_key == 'home' else ''}" href="?menu=home">🏠 홈 (MATCHDAY)</a>
        <a class="{'active' if menu_key == 'roster' else ''}" href="?menu=roster">🏃 선수단 명단</a>
        <a class="{'active' if menu_key == 'report' else ''}" href="?menu=report">📊 성적 분석</a>
    </div>
"""

st.markdown(nav_html, unsafe_allow_html=True)

# --- [신규 추가] 상단 헤더 (로고 및 타이틀) ---
header_logo_html = f'data:image/png;base64,{logo_b64}' if logo_b64 else "https://cdn-icons-png.flaticon.com/512/53/53283.png"

st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 20px; padding: 10px 0px 30px 0px; border-bottom: 1px solid #eee; margin-bottom: 40px;">
        <img src="{header_logo_html}" style="width: 70px; height: 70px; object-fit: contain;">
        <div>
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 900; color: #1a1a1a; letter-spacing: -1px;">
                SEOCHO <span style="color: #003399;">MIDDLE SCHOOL</span>
            </h1>
            <p style="margin: 0; color: #888; font-weight: 500; font-size: 1rem; letter-spacing: 2px;">
                2026 서초중학교 축구부 통합 관리 시스템
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# 2. 로고 처리를 위한 함수





# 3. 전체 스타일 커스텀 (수정 버전)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* 1. 기본 폰트 설정 (아이콘 폰트 제외) */
    :not(i):not(.material-icons):not([class*="lucide"]) {
        font-family: 'Pretendard', sans-serif !important;
    }

    /* 2. 스트림릿 내부 아이콘 클래스 강제 복구 */
    .st-emotion-cache-16ids0d, .st-emotion-cache-15494f6, [data-testid="stIcon"] {
        font-family: "lucide-icons" !important;
        font-style: normal;
        font-weight: normal;
        font-variant: normal;
        text-transform: none;
        line-height: 1;
        -webkit-font-smoothing: antialiased;
    }

    /* --- 이하 기존 스타일 유지 --- */
    .player-card {
        background: repeating-linear-gradient(90deg, #003399, #003399 20px, #1a1a1a 20px, #1a1a1a 40px);
        padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-bottom: 4px solid #CC0000; text-align: center; margin-bottom: 20px; color: white;
    }
    .gk-card {
        background: linear-gradient(135deg, #FFD700 0%, #FF8C00 100%);
        padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-bottom: 4px solid #CC0000; text-align: center; margin-bottom: 20px; color: #1a1a1a;
    }
    .player-number { font-size: 1.5rem; font-weight: 800; margin-bottom: 5px; }
    .player-name { font-size: 1.2rem; font-weight: 600; margin: 5px 0; }
    .player-pos {
        font-size: 0.8rem; padding: 2px 10px; border-radius: 5px;
        background: rgba(255,255,255,0.2); color: inherit; border: 1px solid rgba(255,255,255,0.3);
    }
    </style>
    """, unsafe_allow_html=True)



# 4. 데이터 로드 (로스터/일정은 로컬 파일 유지, 평점은 구글 시트로 변경)
@st.cache_data(ttl=600)
def load_data():
    files = os.listdir('.')
    data = {}
    
    # [1] 로컬 파일 로드 (기존 유지)
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

    # [2] 구글 시트 로드 (한글 인코딩 문제 해결)
    SHEET_ID = "1n1a2Pceu9zMXTgVdIE2sKLh3f7_3I_EjgUQaa0Wua84" 
    ratings_info = {
        "m3": {"gid": "477587476", "skip": 3, "label": "3월"},
        "m4": {"gid": "1104693136", "skip": 3, "label": "4월"},
        "m5": {"gid": "492415984", "skip": 1, "label": "5월"}
    }

    for k, info in ratings_info.items():
        # URL에 한글이나 특수문자가 들어갈 경우를 대비해 quote 처리
        safe_gid = urllib.parse.quote(str(info['gid']))
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={safe_gid}"
        
        try:
            # encoding='utf-8'을 명시적으로 추가하여 한글 깨짐 방지
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

df_all = load_data()

# 5. 내비게이션


if menu == "🏠 홈 (MATCHDAY)": 
    st.markdown("<h2 style='font-weight:700; color:#1a1a1a;'>STADIUM NEWS</h2>", unsafe_allow_html=True)
    sched = df_all['schedule']
    if not sched.empty:
        next_m = sched.dropna(subset=['상대']).iloc[0]
        opp = next_m['상대'].replace('vs ', '').strip()
        
        # 1. 날짜 형식 수정 (YYYY/MM/DD) 
        try:
            raw_date = str(next_m['날짜'])
            formatted_date = pd.to_datetime(raw_date).strftime('2026년/%m월/%d일')
        except:
            formatted_date = str(next_m['날짜'])

        logo_html = f'data:image/png;base64,{logo_b64}' if logo_b64 else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
        opp_logo_b64 = get_base64_image(f"{opp}.png")
        opp_logo_html = f'data:image/png;base64,{opp_logo_b64}' if opp_logo_b64 else "https://cdn-icons-png.flaticon.com/512/1163/1163063.png"

        st.markdown(f"""
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
        """, unsafe_allow_html=True)

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


# --- [선수단 명단 페이지 수정됨] ---
elif menu == "🏃 선수단 명단":
    st.markdown("<h1 style='font-weight:800; margin-bottom:30px;'>SQUAD ROSTER</h1>", unsafe_allow_html=True)
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


# --- 평점 리포트 ---
elif menu == "📊 성적 분석":
    st.markdown("<h1 style='font-weight:800; color:#1a1a1a;'>PERFORMANCE REPORT</h1>", unsafe_allow_html=True)
    
    # 상단 탭 구성 (월간 요약 vs 경기별 상세)
    tab1, tab2 = st.tabs(["📅 월간 평균 리포트", "🏟️ 경기별 상세 평점"])

    month = st.selectbox("📅 분석 기간 선택", ["5월", "4월", "3월"])
    m_key = {"5월": "m5", "4월": "m4", "3월": "m3"}[month]
    col_name = f"{month} 평균평점"
    
    df_roster = df_all['roster'].copy()
    df_m = df_all[m_key].copy()

    # --- TAB 1: 기존 월간 평균 리스트 (기존 디자인 유지) ---
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
            # ... (기존에 제공해주신 리스트 렌더링 코드와 동일)
            for i, (idx, row) in enumerate(df_final.iterrows()):
                score = row[col_name]
                if pd.isna(score) or score == 0: tier, color, score_display = "-", "#888888", "N/A"
                elif score >= 7.0: tier, color, score_display = "A", "#ff4b4b", f"{score:.2f}"
                elif score >= 6.5: tier, color, score_display = "B", "#003399", f"{score:.2f}"
                else: tier, color, score_display = "C", "#555555", f"{score:.2f}"
                
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

                # 5. 개별 선수 명단 리스트 (등급 배지 추가)
                st.markdown(f"#### 📋 개별 선수 랭킹")
                
                if not df_match.empty:
                    m_cols = st.columns(2)
                    for idx, (i, row) in enumerate(df_match.iterrows()):
                        p_name = row['이름']
                        p_score = pd.to_numeric(row[selected_date], errors='coerce')
                        
                        if pd.notna(p_score):
                            # --- 등급 판정 로직 (월간 리포트와 동일 기준) ---
                            if p_score >= 7.0: tier, color = "A", "#ff4b4b"
                            elif p_score >= 6.5: tier, color = "B", "#003399"
                            else: tier, color = "C", "#555555"

                            with m_cols[idx % 2]:
                                st.markdown(f"""
                                    <div style="background: white; padding: 15px 20px; border-radius: 12px; border: 1px solid #eee; 
                                                margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; 
                                                box-shadow: 0 2px 5px rgba(0,0,0,0.02); border-left: 4px solid {color};">
                                        <div style="display:flex; align-items:center; gap:12px;">
                                            <span style="color:#ccc; font-weight:800; font-size:1.1rem;">{idx+1}</span>
                                            <div>
                                                <div style="font-weight: 700; color:#1a1a1a; font-size:1.05rem; display:flex; align-items:center; gap:8px;">
                                                    {p_name}
                                                    <span style="background:{color}; color:white; font-size:0.7rem; padding:1px 6px; border-radius:4px;">{tier}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div style="background: #f0f2f6; color: #003399; padding: 5px 15px; border-radius: 20px; font-weight: 800; font-size: 1rem;">
                                            {float(p_score):.1f}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)