import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import calendar
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# --- 설정: 페이지 및 한국 시간 ---
st.set_page_config(page_title="Lunahyeon's Workout", layout="centered")

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

def get_kst_now():
    return datetime.now(KST)

# [스타일] 버튼 배치 및 모바일 최적화
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stPills"] { display: flex; flex-wrap: wrap; gap: 5px; justify-content: center; }
    [data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; min-width: 50% !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 구글 시트 연결 ---
def get_google_sheet():
    credentials_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("운동일지_DB").sheet1 
    return sheet

def load_data():
    default_cols = ["날짜", "요일", "시간", "몸무게", "운동종목", "무게(kg)", "횟수", "메모"]
    try:
        sheet = get_google_sheet()
        data = sheet.get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            for col in default_cols:
                if col not in df.columns: df[col] = ""
            df['row_id'] = range(2, 2 + len(df))
            return df
        return pd.DataFrame(columns=default_cols)
    except:
        return pd.DataFrame(columns=default_cols)

def save_data(row_data):
    try:
        sheet = get_google_sheet()
        sheet.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"저장 실패: {e}")
        return False

# --- 세션 초기화 ---
if 'exercise_index' not in st.session_state:
    st.session_state['exercise_index'] = 0
if 'last_selected_date' not in st.session_state:
    st.session_state['last_selected_date'] = get_kst_now().date()

st.subheader("💪 Lunahyeon's 운동일지")

tab1, tab2 = st.tabs(["✅ 기록 입력", "📅 캘린더 & 기록장"])

# ==========================================
# 탭 1: 운동 기록 입력
# ==========================================
with tab1:
    kst_now = get_kst_now()
    
    # 1. 날짜 및 시간 입력 (한국 시간 기준)
    col1, col2 = st.columns(2)
    with col1:
        # date_input의 기본값을 한국 현재 날짜로 설정
        date = st.date_input("날짜", kst_now.date(), label_visibility="collapsed")
    with col2:
        current_time_str = kst_now.strftime("%H:%M")
        arrival_time = st.text_input("시간", value=current_time_str, label_visibility="collapsed")
    
    # 2. 요일 계산 (입력된 날짜 기준)
    weekdays_kor = ["월", "화", "수", "목", "금", "토", "일"]
    today_yoil = weekdays_kor[date.weekday()]

    st.markdown(f"### 📅 {date.strftime('%Y-%m-%d')} <span style='color:#FF4B4B'>({today_yoil}요일)</span>", unsafe_allow_html=True)

    weight = st.number_input("오늘 몸무게 (kg)", value=46.0, step=0.1, format="%.1f")

    # 루틴 설정 (화/목 루틴 vs 월/수/금 루틴)
    routine_A = ["시티드 체스트 프레스", "하이폴리", "롱풀", "소미핏", "러닝/걷기", "사이드 레터럴 레이즈", "스쿼트", "레그프레스", "힙 어덕터 & 어브덕터", "업도미널", "기타"]
    routine_B = ["스쿼트", "레그프레스", "힙 어덕터 & 어브덕터", "업도미널", "러닝/걷기", "시티드 체스트 프레스", "하이폴리", "롱풀", "소미핏", "사이드 레터럴 레이즈", "기타"]

    if date.weekday() in [1, 3]: # 화(1), 목(3)
        exercise_list = routine_B
        routine_name = "🔥 하체 / 전신 루틴 (화/목)"
        style_color = "#FF4B4B" 
    else:
        exercise_list = routine_A
        routine_name = "💪 상체 집중 루틴 (월/수/금)"
        style_color = "#1E90FF" 

    # 날짜가 바뀌면 운동 순서 리셋
    if st.session_state['last_selected_date'] != date:
        st.session_state['exercise_index'] = 0
        st.session_state['last_selected_date'] = date
        st.rerun()

    st.markdown("---")
    st.markdown(f"<div style='background-color: {style_color}; padding: 10px; border-radius: 5px; color: white; text-align: center; margin-bottom: 10px;'>{routine_name}</div>", unsafe_allow_html=True)
    
    current_index = st.session_state['exercise_index']
    if current_index >= len(exercise_list):
        current_index = 0

    selected_exercise = st.selectbox("현재 운동 종목", exercise_list, index=current_index)

    with st.form("workout_form", clear_on_submit=True):
        sets_done = []
        save_reps_str = ""
        save_weight_val = 0

        # 운동별 입력창 (소미핏/러닝/일반 등 - 기존 로직 유지)
        if selected_exercise == "소미핏":
            is_somifit_done = st.checkbox("✅ 소미핏 완료!", value=False)
            if is_somifit_done:
                sets_done = ["Completed"]; save_reps_str = "완료"
        elif selected_exercise == "러닝/걷기":
            c1, c2, c3 = st.columns(3)
            with c1: run_min = st.number_input("분", 30, step=5)
            with c2: run_spd = st.number_input("속도", 1.0, 10.0, 5.6, 0.1)
            with c3: run_inc = st.number_input("경사", 0, 9, 0, 1)
            sets_done = ["Done"]; save_weight_val = run_spd; save_reps_str = f"{run_min}분 (경사 {run_inc})"
        else:
            c1, c2 = st.columns(2)
            with c1: ex_weight = st.number_input("무게 (kg)", 0, step=5, value=10)
            with c2: base_reps = st.number_input("목표 횟수", value=15, step=1)
            pills_opts = [f"{base_reps}", f"{base_reps} ", f"{base_reps}  ", f"{base_reps}   "] 
            selected_pills = st.pills("세트 체크", options=pills_opts, selection_mode="multi", label_visibility="collapsed")
            if selected_pills:
                for _ in selected_pills: sets_done.append(str(base_reps))
            save_weight_val = ex_weight; save_reps_str = " ".join(sets_done)

        memo = st.text_area("메모", placeholder="특이사항 없음", height=70)
        
        # 버튼 분리
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            # 저장 안 하고 다음 종목으로만 이동
            next_btn = st.form_submit_button("⏭️ 다음 운동으로", use_container_width=True)
        with btn_col2:
            # 현재 운동 저장 (기록 완료용)
            save_btn = st.form_submit_button("💾 시트에 저장", type="primary", use_container_width=True)

    if save_btn:
        if not sets_done:
            st.warning("⚠️ 세트 수를 체크해주세요!")
        else:
            row_data = [date.strftime('%Y-%m-%d'), today_yoil, arrival_time, weight, selected_exercise, save_weight_val, save_reps_str, memo]
            if save_data(row_data):
                st.success(f"✅ {selected_exercise} 저장 완료!")
                time.sleep(1)

    if next_btn:
        st.session_state['exercise_index'] = (current_index + 1) % len(exercise_list)
        st.rerun()

# [탭 2: 캘린더 로직은 이전과 동일하므로 생략하거나 기존 코드 유지]