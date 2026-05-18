import streamlit as st
import pandas as pd
import os
from typing import Dict, List, Tuple

# Load data
def load_schedule() -> pd.DataFrame:
    """Load schedule from CSV."""
    files = os.listdir('.')
    target = [f for f in files if '일정' in f and f.endswith('.csv')]
    if target:
        df = pd.read_csv(target[0], skiprows=3)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df
    return pd.DataFrame()

def load_roster() -> pd.DataFrame:
    """Load roster from CSV."""
    files = os.listdir('.')
    target = [f for f in files if '로스터' in f and f.endswith('.csv')]
    if target:
        df = pd.read_csv(target[0], skiprows=7)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.dropna(subset=['이름']) if '이름' in df.columns else df
        return df
    return pd.DataFrame()

# UI Components
def match_selector(label: str = "경기 선택", key: str = None):
    """Match selection dropdown from schedule."""
    df = load_schedule()
    if df.empty:
        st.warning("일정 데이터를 불러올 수 없습니다.")
        return ""
    
    # Create list of (match_id, display_name, opponent)
    options = []
    for _, row in df.iterrows():
        opp = row['상대'].replace('vs ', '').strip() if '상대' in row else 'TBD'
        date = row.get('날짜', '')
        match_id = f"match_{date.replace(' ', '_')}_{opp}"
        display_name = f"서초중 vs {opp} ({date})"
        options.append((match_id, display_name, opp))
    
    # Use session_state to store mapping if needed
    mapping_key = f'match_selector_mapping_{key if key else "default"}'
    if mapping_key not in st.session_state:
        st.session_state[mapping_key] = {dname: (mid, opp) for mid, dname, opp in options}
    
    display_names = [dname for _, dname, _ in options]
    selected_display = st.selectbox(label, display_names, index=0, key=key)
    
    if selected_display in st.session_state[mapping_key]:
        mid, opp = st.session_state[mapping_key][selected_display]
        # Store selected match_id and opponent in session_state for easy access
        st.session_state[f'selected_match_id_{key if key else "default"}'] = mid
        st.session_state[f'selected_opponent_{key if key else "default"}'] = opp
        return mid
    return ""

def score_inputs(label: str = "점수", home_label: str = "서초중", away_label: str = "상대팀",
                 value: Tuple[int, int] = (0, 0), disabled: bool = False, key: str = None):
    """Score input fields. Auto calculation is controlled by the page-level checkbox."""
    cols = st.columns(2)
    with cols[0]:
        st.subheader(home_label)
    with cols[1]:
        st.subheader(away_label)

    # Number inputs for scores; disabled based on the auto calculation flag passed from the page.
    home_score = st.number_input("홈 점수", min_value=0, max_value=99, value=value[0],
                                 disabled=disabled, key=f"home_score_{key}")
    away_score = st.number_input("원정 점수", min_value=0, max_value=99, value=value[1],
                                 disabled=disabled, key=f"away_score_{key}")
    return home_score, away_score

def lineup_popup(label: str = "라인업", key: str = None):
    """Lineup selection popup with checkboxes from roster."""
    session_key = f'lineup_selection_{key if key else "default"}'
    
    df = load_roster()
    if df.empty:
        st.warning("로스터 데이터를 불러올 수 없습니다.")
        return []
    
    # Get player names
    players = df['이름'].tolist()
    
    # Initialize session state for lineup
    if session_key not in st.session_state:
        st.session_state[session_key] = []
    
    # Use expander or modal
    with st.expander(f"{label} 펼치기"):
        checked = st.multiselect("선발 선수 선택 (최대 11명)", players, 
                                 default=st.session_state[session_key],
                                 format_func=lambda x: x,
                                 key=f"lineup_multiselect_{key}")
        st.session_state[session_key] = checked
        st.info(f"선택된 선수: {len(checked)}명")
    return checked

def timeline_editor(label: str = "타임라인 이벤트", initial_events: List[Dict] = None, key: str = None):
    """Timeline editor with dynamic rows."""
    session_key = f'timeline_events_{key if key else "default"}'
    
    # Initialize session state for timeline events
    if session_key not in st.session_state:
        st.session_state[session_key] = initial_events if initial_events else []
    
    # Event types
    event_types = [
        "골", "페널티골", "경고", "퇴장", "교체", "코너킥", "프리킥", "반칙", "휴식시간"
    ]
    
    # Team options
    teams = ["홈", "원정"]
    
    # Roster for player selection (only for home events)
    roster = load_roster()
    players = roster['이름'].tolist() if not roster.empty else []
    
    # Card types for card events
    card_types = ["옐로", "레드"]
    
    st.subheader(label)
    
    # Add button
    if st.button("이벤트 추가", type="primary", use_container_width=True, key=f"add_event_{key}"):
        st.session_state[session_key].append({
            'minute': 0,
            'team': 'home',
            'event_type': '골',
            'player': players[0] if players else '',
            'card_type': 'yellow'
        })
        st.rerun()
    
    # Display each event
    events = st.session_state[session_key]
    for i, event in enumerate(events):
        with st.container():
            cols = st.columns([1, 1, 2, 1, 1, 1])
            with cols[0]:
                minute = st.number_input(f"분 {i+1}", min_value=0, max_value=120, value=event.get('minute', 0), 
                                        key=f"minute_{i}_{key}", help="경기 시간 (분)", on_change=lambda: None)
            with cols[1]:
                team = st.selectbox(f"팀 {i+1}", teams, index=0 if event.get('team') == 'home' else 1, 
                                   key=f"team_{i}_{key}", help="이벤트 팀")
            with cols[2]:
                event_type = st.selectbox(f"이벤트 {i+1}", event_types, 
                                        index=event_types.index(event.get('event_type', '골')) if event.get('event_type') in event_types else 0, 
                                        key=f"event_type_{i}_{key}", help="이벤트 종류")
            
            # Only show player selection for home team events that involve a player
            if team == '홈' and event_type in ['골', '페널티골', '경고', '퇴장']:
                with cols[3]:
                    player = st.selectbox(f"선수 {i+1}", players, 
                                        index=players.index(event.get('player', '')) if event.get('player') in players else 0, 
                                        key=f"player_{i}_{key}", help="관련 선수")
            else:
                with cols[3]:
                    st.empty()  # Keep column alignment
            
            # Only show card type for card events
            if event_type in ['경고', '퇴장']:
                with cols[4]:
                    card_type = st.selectbox(f"카드 {i+1}", card_types, 
                                            index=0 if event.get('card_type') == 'yellow' else 1, 
                                            key=f"card_type_{i}_{key}", help="카드 색상")
            else:
                with cols[4]:
                    st.empty()
            
            # Remove button
            with cols[5]:
                if st.button("제거", type="secondary", key=f"remove_{i}_{key}"):
                    st.session_state[session_key].pop(i)
                    st.rerun()
        
        # Update event dict in session state
        st.session_state[session_key][i]['minute'] = minute
        st.session_state[session_key][i]['team'] = 'home' if team == '홈' else 'away'
        st.session_state[session_key][i]['event_type'] = event_type
        if team == '홈' and event_type in ['골', '페널티골', '경고', '퇴장']:
            st.session_state[session_key][i]['player'] = player
        if event_type in ['경고', '퇴장']:
            st.session_state[session_key][i]['card_type'] = card_type
    
    return st.session_state[session_key]

def instant_save_preview(details: Dict, key: str = None):
    """Show instant preview of current data."""
    with st.expander("📋 현재 입력 데이터 미리보기"):
        st.json(details)