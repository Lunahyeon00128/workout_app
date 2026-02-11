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

# ★ [CSS 수정] 모바일에서 2개 컬럼이 세로로 쌓이지 않고 '무조건 가로'로 유지되게 함
st.markdown("""
    <style>
    /* 좁은 화면에서도 컬럼이 위아래로 쌓이지 않고 50:50으로 유지되게 강제 설정 */
    [data-testid="column"] {
        width: 50% !important;
        flex: 1 1 50% !important;
        min-width: 50% !important;
    }
    </style>
    """, unsafe_allow_html=True)

def get_kst_now():
    timezone = pytz.timezone('Asia/Seoul')
    return datetime.now(timezone)

# --- 구글 시트 연결 ---
def get_google_sheet():
    credentials_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("운동일지_DB").sheet1 
    return sheet

# --- 데이터 불러오기 ---
def load_data():
    default_cols = ["날짜", "요일", "시간", "몸무게", "운동종목", "무게(kg)", "횟수", "메모"]
    try:
        sheet = get_google_sheet()
        data = sheet.get_all_values()
        
        if len(data) > 1:
            headers = data[0]
            rows = data[1:]
            df = pd.DataFrame(rows, columns=headers)
            
            for col in default_cols:
                if col not in df.columns:
                    df[col] = ""
            
            df['row_id'] = range(2, 2 + len(rows))
            return df
        else:
            return pd.DataFrame(columns=default_cols)
    except Exception as e:
        return pd.DataFrame(columns=default_cols)

# --- 데이터 저장 ---
def save_data(row_data):
    try:
        sheet = get_google_sheet()
        sheet.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"저장 실패: {e}")
        return False

# --- 데이터 삭제 ---
def delete_data(row_id):
    try:
        sheet = get_google_sheet()
        sheet.delete_rows(row_id)
        return True
    except Exception as e:
        st.error(f"삭제 실패: {e}")
        return False

# --- 세션 초기화 ---
if 'exercise_index' not in st.session_state:
    st.session_state['exercise_index'] = 0
if 'last_selected_date' not in st.session_state:
    st.session_state['last_selected_date'] = None

st.subheader("💪 Lunahyeon's 운동일지")

tab1, tab2 = st.tabs(["✅ 기록 입력", "📅 캘린더 & 기록장"])

# ==========================================
# 탭 1: 운동 기록 입력
# ==========================================
with tab1:
    header_placeholder = st.empty() 
    kst_now = get_kst_now()
    
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", kst_now, label_visibility="collapsed")
    with col2:
        current_time_str = kst_now.strftime("%H:%M")
        arrival_time = st.text_input("시간", value=current_time_str, label_visibility="collapsed")
    
    weekday = date.weekday()
    weekdays_kor = ["월", "화", "수", "목", "금", "토", "일"]
    today_yoil = weekdays_kor[weekday]

    with header_placeholder:
        st.markdown(f"### 📅 {date.strftime('%Y-%m-%d')} <span style='color:#FF4B4B'>({today_yoil}요일)</span>", unsafe_allow_html=True)

    weight = st.number_input("오늘 몸무게 (kg)", value=46.0, step=0.1, format="%.1f")

    # 루틴 설정
    routine_A = [
        "시티드 체스트 프레스", "하이폴리", "롱풀", "소미핏", 
        "러닝/걷기", "사이드 레터럴 레이즈", 
        "스쿼트", "레그프레스", "힙 어덕터 & 어브덕터", "업도미널", 
        "기타"
    ]
    routine_B = [
        "스쿼트", "레그프레스", "힙 어덕터 & 어브덕터", "업도미널", 
        "러닝/걷기", 
        "시티드 체스트 프레스", "하이폴리", "롱풀", "소미핏", "사이드 레터럴 레이즈", 
        "기타"
    ]

    if weekday in [1, 3]: 
        exercise_list = routine_B
        routine_name = "🔥 하체 / 전신 루틴 (화/목)"
        style_color = "#FF4B4B" 
    else:
        exercise_list = routine_A
        routine_name = "💪 상체 집중 루틴 (월/수/금)"
        style_color = "#1E90FF" 

    if st.session_state['last_selected_date'] != date:
        st.session_state['exercise_index'] = 0
        st.session_state['last_selected_date'] = date
        st.rerun()

    st.markdown("---")
    st.markdown(f"<div style='background-color: {style_color}; padding: 10px; border-radius: 5px; color: white; text-align: center; margin-bottom: 10px;'>{routine_name}</div>", unsafe_allow_html=True)
    
    current_index = st.session_state['exercise_index']
    if current_index >= len(exercise_list):
        current_index = 0
        st.session_state['exercise_index'] = 0

    selected_exercise = st.selectbox(
        "운동 종목 (저장 시 자동 넘어감)", 
        exercise_list, 
        index=current_index
    )

    video_links = {
        "시티드 체스트 프레스": "https://youtube.com/shorts/AKzdQPAEGMQ?si=MVTrPeUXfvs2aJR9",
        "하이폴리": "https://youtube.com/shorts/5UPOD0he724?si=SahBffFfYiOmS-Vn",
        "롱풀": "https://youtube.com/shorts/t6edD5c7QWw?si=R0X5k8scgPocC-pv",
        "소미핏": "https://youtu.be/tZbTY9j_L9o?si=8kCxZvj8b3tZy_4J",
        "스쿼트": "https://youtu.be/urOSaROmTIk?si=rnS-BkOKbb4EGZc-",
        "레그프레스": "https://youtube.com/shorts/FcHwWI2sulg?si=BQL8nCtplDJprZLa",
        "업도미널": "https://youtube.com/shorts/6O0YQY8u-Io?si=mGkzGrR4L0jKi57N"
    }

    if selected_exercise in video_links:
        st.markdown(f"👉 **[{selected_exercise} 자세 영상 보기 (YouTube)]({video_links[selected_exercise]})**")

    with st.form("workout_form", clear_on_submit=True):
        sets_done = []
        save_reps_str = ""
        save_weight_val = 0

        if selected_exercise == "소미핏":
            is_somifit_done = st.checkbox("✅ 소미핏 완료!", value=False)
            if is_somifit_done:
                sets_done = ["Completed"]
                save_reps_str = "완료"
        
        elif selected_exercise == "러닝/걷기":
            c1, c2, c3 = st.columns(3)
            with c1: run_minutes = st.number_input("시간(분)", 30, step=5)
            with c2: run_speed = st.number_input("속도", 1.0, 10.0, 5.6, 0.1, "%.1f")
            with c3: run_incline = st.number_input("경사", 0, 9, 0, 1)
            sets_done = ["Completed"]
            save_weight_val = run_speed
            save_reps_str = f"{run_minutes}분 (경사 {run_incline})"

        else:
            c1, c2 = st.columns([1, 1])
            with c1: exercise_weight = st.number_input("무게 (kg)", 0, step=5, value=10)
            with c2: base_reps = st.number_input("목표 횟수", value=15, step=1)
            
            st.write("👇 **세트 수행 체크**")
            
            # ★ 수정됨: 2x2 격자 배치 (완벽한 반응형) ★
            # 1행 (1, 2세트)
            row1_1, row1_2 = st.columns(2)
            with row1_1:
                if st.checkbox(f"{base_reps}", key="s1"): sets_done.append(str(base_reps))
            with row1_2:
                if st.checkbox(f"{base_reps}", key="s2"): sets_done.append(str(base_reps))
                
            # 2행 (3, 4세트)
            row2_1, row2_2 = st.columns(2)
            with row2_1:
                if st.checkbox(f"{base_reps}", key="s3"): sets_done.append(str(base_reps))
            with row2_2:
                if st.checkbox(f"{base_reps}", key="s4"): sets_done.append(str(base_reps))

            save_weight_val = exercise_weight
            save_reps_str = " ".join(sets_done)

        st.markdown("---")
        memo = st.text_area("메모", placeholder="특이사항 없음", height=70)
        submit_btn = st.form_submit_button("💾 구글 시트에 저장 & 다음 (Next)", use_container_width=True)

    if submit_btn:
        if not sets_done:
            st.warning("⚠️ 수행한 내용을 체크해주세요!")
        else:
            date_str = date.strftime('%Y-%m-%d')
            row_data = [
                date_str, today_yoil, arrival_time, weight,
                selected_exercise, save_weight_val, save_reps_str, memo
            ]
            
            if save_data(row_data):
                try: now_index = exercise_list.index(selected_exercise)
                except: now_index = 0
                st.session_state['exercise_index'] = now_index + 1
                
                st.success(f"[{selected_exercise}] 저장 완료! 다음 운동으로 넘어갑니다.")
                time.sleep(1)
                st.rerun()

# ==========================================
# 탭 2: 캘린더 & 기록장
# ==========================================
with tab2:
    st.subheader("📊 구글 시트 데이터 로딩 중...")
    df = load_data()
    
    if not df.empty and '날짜' in df.columns:
        df['dt_obj'] = pd.to_datetime(df['날짜'], errors='coerce')
        df = df.dropna(subset=['dt_obj'])
        
        if not df.empty:
            st.success("데이터 로드 완료!")
            df['day'] = df['dt_obj'].dt.day
            
            now = get_kst_now()
            selected_year = st.selectbox("연도", [now.year, now.year-1], index=0)
            selected_month = st.selectbox("월", range(1, 13), index=now.month-1)
            
            mask = (df['dt_obj'].dt.year == selected_year) & (df['dt_obj'].dt.month == selected_month)
            workout_days = df[mask]['day'].unique()
            
            cal = calendar.monthcalendar(selected_year, selected_month)
            table_html = """
            <style>
                .calendar-table {width: 100%; text-align: center; border-collapse: collapse;}
                .calendar-table th {background-color: #f0f2f6; padding: 10px; border: 1px solid #ddd;}
                .calendar-table td {height: 80px; vertical-align