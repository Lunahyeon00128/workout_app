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

# 한국 시간대(KST) 고정
KST = pytz.timezone('Asia/Seoul')

def get_kst_now():
    return datetime.now(KST)

# ★ [스타일 강화] 버튼 간격 및 패딩 대폭 확대 ★
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    
    /* 알약 버튼(Pills) 사이의 좌우 간격을 강제로 25px로 설정 */
    div[data-testid="stPills"] { 
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 25px !important; 
        justify-content: center !important;
        padding: 10px 0 !important;
    }
    
    /* 각 버튼 자체의 크기를 키워 터치하기 편하게 함 */
    div[data-testid="stPills"] button {
        padding: 10px 25px !important;
        min-width: 75px !important;
        border-radius: 20px !important;
    }

    /* 하단 저장/다음 버튼 가로 배치 유지 */
    [data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; min-width: 50% !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 구글 시트 연결 ---
def get_google_sheet():
    try:
        credentials_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("운동일지_DB").sheet1 
        return sheet
    except Exception as e:
        st.error(f"구글 시트 연결 실패: {e}")
        return None

# --- 데이터 로드 (에러 방지 강화) ---
def load_data():
    default_cols = ["날짜", "요일", "시간", "몸무게", "운동종목", "무게(kg)", "횟수", "메모"]
    sheet = get_google_sheet()
    if sheet is None: return pd.DataFrame(columns=default_cols)
    
    try:
        data = sheet.get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            # 필수 컬럼 확인 및 추가
            for col in default_cols:
                if col not in df.columns: df[col] = ""
            df['row_id'] = range(2, 2 + len(df))
            return df
        return pd.DataFrame(columns=default_cols)
    except:
        return pd.DataFrame(columns=default_cols)

def save_data(row_data):
    sheet = get_google_sheet()
    if sheet is None: return False
    try:
        sheet.append_row(row_data)
        return True
    except:
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
    
    col1, col2 = st.columns(2)
    with col1:
        # 한국 날짜 기준 기본값
        date = st.date_input("날짜", kst_now.date(), label_visibility="collapsed")
    with col2:
        current_time_str = kst_now.strftime("%H:%M")
        arrival_time = st.text_input("시간", value=current_time_str, label_visibility="collapsed")
    
    # 요일 계산 (KST 기준)
    weekdays_kor = ["월", "화", "수", "목", "금", "토", "일"]
    today_yoil = weekdays_kor[date.weekday()]

    st.markdown(f"### 📅 {date.strftime('%Y-%m-%d')} <span style='color:#FF4B4B'>({today_yoil}요일)</span>", unsafe_allow_html=True)

    weight = st.number_input("오늘 몸무게 (kg)", value=46.0, step=0.1, format="%.1f")

    routine_A = ["시티드 체스트 프레스", "하이폴리", "롱풀", "소미핏", "러닝/걷기", "사이드 레터럴 레이즈", "스쿼트", "레그프레스", "힙 어덕터 & 어브덕터", "업도미널", "기타"]
    routine_B = ["스쿼트", "레그프레스", "힙 어덕터 & 어브덕터", "업도미널", "러닝/걷기", "시티드 체스트 프레스", "하이폴리", "롱풀", "소미핏", "사이드 레터럴 레이즈", "기타"]

    if date.weekday() in [1, 3]: # 화, 목
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
    if current_index >= len(exercise_list): current_index = 0

    selected_exercise = st.selectbox("현재 운동 종목", exercise_list, index=current_index)

    with st.form("workout_form", clear_on_submit=True):
        sets_done = []
        save_reps_str = ""
        save_weight_val = 0

        if selected_exercise == "소미핏":
            is_somifit_done = st.checkbox("✅ 완료!", value=False)
            if is_somifit_done: sets_done = ["Completed"]; save_reps_str = "완료"
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
            
            # 넓어진 간격의 버튼들
            pills_opts = [f"{base_reps}", f"{base_reps} ", f"{base_reps}  ", f"{base_reps}   "] 
            selected_pills = st.pills("세트 체크", options=pills_opts, selection_mode="multi", label_visibility="collapsed")
            if selected_pills:
                for _ in selected_pills: sets_done.append(str(base_reps))
            save_weight_val = ex_weight; save_reps_str = " ".join(sets_done)

        memo = st.text_area("메모", placeholder="특이사항 없음", height=70)
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            next_btn = st.form_submit_button("⏭️ 다음으로", use_container_width=True)
        with btn_col2:
            save_btn = st.form_submit_button("💾 시트에 저장", type="primary", use_container_width=True)

    if save_btn:
        if not sets_done:
            st.warning("⚠️ 세트 체크를 해주세요!")
        else:
            row_data = [date.strftime('%Y-%m-%d'), today_yoil, arrival_time, weight, selected_exercise, save_weight_val, save_reps_str, memo]
            if save_data(row_data):
                st.success(f"✅ {selected_exercise} 저장됨!")
                time.sleep(1)

    if next_btn:
        st.session_state['exercise_index'] = (current_index + 1) % len(exercise_list)
        st.rerun()

# ==========================================
# 탭 2: 캘린더 & 기록장 (백지 현상 해결)
# ==========================================
with tab2:
    df = load_data()
    
    if not df.empty and '날짜' in df.columns:
        # 날짜 변환 에러 방지
        df['dt_obj'] = pd.to_datetime(df['날짜'], errors='coerce')
        df = df.dropna(subset=['dt_obj'])
        
        if not df.empty:
            st.subheader("📅 월별 운동 현황")
            df['day'] = df['dt_obj'].dt.day
            
            now_kst = get_kst_now()
            selected_year = st.selectbox("연도", [now_kst.year, now_kst.year-1], index=0)
            selected_month = st.selectbox("월", range(1, 13), index=now_kst.month-1)
            
            mask = (df['dt_obj'].dt.year == selected_year) & (df['dt_obj'].dt.month == selected_month)
            workout_days = df[mask]['day'].unique()
            
            cal = calendar.monthcalendar(selected_year, selected_month)
            table_html = """
            <style>
                .cal-table {width: 100%; text-align: center; border-collapse: collapse; font-size: 14px;}
                .cal-table th {background-color: #f0f2f6; padding: 8px; border: 1px solid #ddd;}
                .cal-table td {height: 60px; vertical-align: top; border: 1px solid #ddd; width: 14%; padding: 5px;}
                .sticker {display: block; margin: 3px auto; background-color: #FF4B4B; color: white; border-radius: 50%; width: 22px; height: 22px; line-height: 22px; font-size: 11px;}
            </style>
            <table class='cal-table'><thead><tr><th style='color:red'>일</th><th>월</th><th>화</th><th>수</th><th>목</th><th>금</th><th style='color:blue'>토</th></tr></thead><tbody>
            """
            for week in cal:
                table_html += "<tr>"
                for day in week:
                    if day == 0: table_html += "<td></td>"
                    else:
                        sticker = "<span class='sticker'>O</span>" if day in workout_days else ""
                        table_html += f"<td>{day}{sticker}</td>"
                table_html += "</tr>"
            table_html += "</tbody></table>"
            st.markdown(table_html, unsafe_allow_html=True)
            
            st.divider()
            st.subheader(f"📝 {selected_month}월 상세 기록")
            
            month_df = df[mask].sort_values(by=['dt_obj', '시간'], ascending=[False, True])
            unique_dates = month_df['날짜'].unique()
            
            for d in unique_dates:
                day_data = month_df[month_df['날짜'] == d]
                with st.expander(f"📌 {d} ({len(day_data)}개 종목)", expanded=False):
                    st.dataframe(day_data[['시간', '운동종목', '무게(kg)', '횟수', '메모']], use_container_width=True, hide_index=True)
        else:
            st.info("이 달에는 아직 기록이 없습니다.")
    else:
        st.info("구글 시트에 기록이 없습니다. 먼저 기록을 남겨보세요!")