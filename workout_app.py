import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pytz # 한국 시간 계산용
import calendar # 달력 생성용

# --- 설정: 한국 시간(KST) 가져오기 함수 ---
def get_kst_now():
    timezone = pytz.timezone('Asia/Seoul')
    return datetime.now(timezone)

# 모바일 화면 설정
st.set_page_config(page_title="Lunahyeon's Workout", layout="centered")

# --- 1. 세션 상태 초기화 ---
if 'exercise_index' not in st.session_state:
    st.session_state['exercise_index'] = 0
if 'last_selected_date' not in st.session_state:
    st.session_state['last_selected_date'] = None

st.subheader("💪 Lunahyeon's 운동일지")

# 탭 구성
tab1, tab2 = st.tabs(["✅ 기록 입력", "📅 캘린더 & 기록장"])

# ==========================================
# 탭 1: 운동 기록 입력
# ==========================================
with tab1:
    # 1. 상단에 날짜/요일을 보여줄 빈 공간(Placeholder) 생성
    header_placeholder = st.empty() 
    
    # 한국 시간으로 오늘 날짜 기본값 설정
    kst_now = get_kst_now()
    
    col1, col2 = st.columns(2)
    with col1:
        # 날짜 입력 (라벨 숨김, 실제로는 안보임)
        date = st.date_input("날짜", kst_now, label_visibility="collapsed")
    with col2:
        # 시간 입력
        current_time_str = kst_now.strftime("%H:%M")
        arrival_time = st.text_input("시간", value=current_time_str, label_visibility="collapsed")
    
    # --- 요일 계산 및 상단 헤더 업데이트 ---
    weekday = date.weekday() # 0:월, 1:화 ... 6:일
    weekdays_kor = ["월", "화", "수", "목", "금", "토", "일"]
    today_yoil = weekdays_kor[weekday]

    # ★ 날짜와 요일을 아주 잘 보이게 표시
    with header_placeholder:
        st.markdown(f"### 📅 {date.strftime('%Y-%m-%d')} <span style='color:#FF4B4B'>({today_yoil}요일)</span>", unsafe_allow_html=True)

    weight = st.number_input("오늘 몸무게 (kg)", value=46.0, step=0.1, format="%.1f")

    # --- 요일별 루틴 설정 (자동 변경) ---
    # 루틴 A (월, 수, 금, 주말)
    routine_A = [
        "시티드 체스트 프레스", "하이폴리", "롱풀", "소미핏", 
        "러닝/걷기", "사이드 레터럴 레이즈", 
        "스쿼트", "레그프레스", "힙 어덕터 & 어브덕터", "업도미널", 
        "기타"
    ]
    
    # 루틴 B (화, 목)
    routine_B = [
        "스쿼트", "레그프레스", "힙 어덕터 & 어브덕터", "업도미널", 
        "러닝/걷기", 
        "시티드 체스트 프레스", "하이폴리", "롱풀", "소미핏", "사이드 레터럴 레이즈", 
        "기타"
    ]

    # 화(1), 목(3)은 루틴 B, 나머지는 루틴 A
    if weekday in [1, 3]: 
        exercise_list = routine_B
        routine_name = "🔥 하체 / 전신 루틴 (화/목)"
        style_color = "#FF4B4B" # 빨강
    else:
        exercise_list = routine_A
        routine_name = "💪 상체 집중 루틴 (월/수/금)"
        style_color = "#1E90FF" # 파랑

    # 날짜가 바뀌면 운동 순서 0번(처음)으로 초기화
    if st.session_state['last_selected_date'] != date:
        st.session_state['exercise_index'] = 0
        st.session_state['last_selected_date'] = date
        st.rerun()

    st.markdown("---")
    # 루틴 이름 표시 박스
    st.markdown(f"<div style='background-color: {style_color}; padding: 10px; border-radius: 5px; color: white; text-align: center; margin-bottom: 10px;'>{routine_name}</div>", unsafe_allow_html=True)
    
    # ★ 핵심 로직: 세션 상태(index)를 통해 자동으로 선택값이 바뀜
    # 하지만 사용자가 드롭박스를 눌러서 수동으로 바꿀 수도 있음
    current_index = st.session_state['exercise_index']
    
    # 인덱스가 리스트 범위를 넘어가면 0으로 초기화 (한 바퀴 돌았을 때)
    if current_index >= len(exercise_list):
        current_index = 0
        st.session_state['exercise_index'] = 0

    selected_exercise = st.selectbox(
        "운동 종목 (저장하면 자동으로 넘어갑니다)", 
        exercise_list, 
        index=current_index
    )

    # --- 영상 링크 매핑 ---
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

    # --- 입력 폼 ---
    with st.form("workout_form", clear_on_submit=True):
        
        sets_done = []
        save_reps_str = ""
        save_weight_val = 0

        # [CASE 1] 소미핏
        if selected_exercise == "소미핏":

            is_somifit_done = st.checkbox("✅ 오늘 소미핏 완료!", value=False)
            if is_somifit_done:
                sets_done = ["Completed"]
                save_reps_str = "완료"
        
        # [CASE 2] 러닝/걷기
        elif selected_exercise == "러닝/걷기":
            st.markdown("🏃‍♀️ **유산소 설정**")
            c1, c2, c3 = st.columns(3)
            with c1:
                run_minutes = st.number_input("시간(분)", min_value=1, value=30, step=5)
            with c2:
                run_speed = st.number_input("속도", min_value=1.0, max_value=10.0, value=5.6, step=0.1, format="%.1f")
            with c3:
                run_incline = st.number_input("경사", min_value=0, max_value=9, value=0, step=1)
            
            sets_done = ["Completed"]
            save_weight_val = run_speed
            save_reps_str = f"{run_minutes}분 (경사 {run_incline})"

        # [CASE 3] 일반 근력 운동
        else:
            c1, c2 = st.columns([1, 1])
            with c1:
                exercise_weight = st.number_input("무게 (kg)", min_value=0, step=5, value=10)
            with c2:
                base_reps = st.number_input("목표 횟수", value=15, step=1)

            st.write("👇 **세트 수행 체크**")
            
            # 가로로 체크박스 배치
            check_cols = st.columns(4)
            for i in range(4):
                with check_cols[i]:
                    if st.checkbox(f"{base_reps}회", key=f"set_{i}"):
                        sets_done.append(str(base_reps))
            
            save_weight_val = exercise_weight
            save_reps_str = " ".join(sets_done)

        st.markdown("---")
        memo = st.text_area("메모", placeholder="특이사항 없음", height=70)
        
        # 저장 버튼
        submit_btn = st.form_submit_button("💾 저장 및 다음 운동으로 (Next)", use_container_width=True)

    if submit_btn:
        if not sets_done:
            st.warning("⚠️ 수행한 내용을 체크해주세요!")
        else:
            # 1. 요일 기록 (YYYY-MM-DD (월) 형식)
            date_str = f"{date.strftime('%Y-%m-%d')} ({today_yoil})"
            
            new_data = {
                "날짜": [date_str],
                "시간": [arrival_time],
                "몸무게": [weight],
                "운동종목": [selected_exercise],
                "무게(kg)": [save_weight_val], 
                "횟수": [save_reps_str],       
                "메모": [memo]
            }
            
            df = pd.DataFrame(new_data)
            file_name = 'my_workout_log.csv'
            
            # 파일 저장 로직
            if not os.path.exists(file_name):
                df.to_csv(file_name, index=False, encoding='utf-8-sig')
            else:
                df.to_csv(file_name, mode='a', header=False, index=False, encoding='utf-8-sig')
            
            # ★ 자동 순서 넘기기 로직 (핵심) ★
            # 현재 선택된 운동이 리스트의 몇 번째인지 찾습니다.
            # (만약 사용자가 드롭박스를 수동으로 바꿨을 수도 있으니까요)
            try:
                now_index = exercise_list.index(selected_exercise)
            except ValueError:
                now_index = 0
            
            # 다음 인덱스 계산
            next_index = now_index + 1
            st.session_state['exercise_index'] = next_index
            
            # 성공 메시지와 함께 페이지 새로고침(Rerun) -> 그러면 다음 운동이 뜸
            st.success(f"[{selected_exercise}] 저장 완료! 다음 운동으로 넘어갑니다.")
            st.rerun()

# ==========================================
# 탭 2: 캘린더 & 기록장 (기존 유지)
# ==========================================
with tab2:
    st.subheader("📊 월별 운동 캘린더")
    
    if os.path.exists('my_workout_log.csv'):
        df = pd.read_csv('my_workout_log.csv')
        
        df['dt_obj'] = pd.to_datetime(df['날짜'].str.slice(0, 10)) 
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
            .calendar-table td {height: 80px; vertical-align: top; border: 1px solid #ddd; width: 14%;}
            .workout-sticker {
                display: block; margin-top: 5px; 
                background-color: #FF4B4B; color: white; 
                border-radius: 50%; width: 24px; height: 24px; 
                line-height: 24px; margin-left: auto; margin-right: auto;
                font-size: 12px;
            }
            .date-num {font-weight: bold; display: block; margin-bottom: 5px;}
        </style>
        <table class="calendar-table">
            <thead>
                <tr>
                    <th style="color:red">일</th><th>월</th><th>화</th><th>수</th><th>목</th><th>금</th><th style="color:blue">토</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for week in cal:
            table_html += "<tr>"
            for day in week:
                if day == 0:
                    table_html += "<td></td>" 
                else:
                    sticker = ""
                    if day in workout_days:
                        sticker = "<span class='workout-sticker'>O</span>" 
                    
                    table_html += f"<td><span class='date-num'>{day}</span>{sticker}</td>"
            table_html += "</tr>"
        
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader(f"📝 {selected_month}월 상세 기록")
        
        month_df = df[mask].copy()
        month_df = month_df.sort_values(by=['dt_obj', '시간'], ascending=[False, True])
        
        unique_dates = month_df['날짜'].unique()
        
        if len(unique_dates) > 0:
            for d in unique_dates:
                day_data = month_df[month_df['날짜'] == d]
                
                with st.expander(f"📌 {d} (총 {len(day_data)}개 종목 수행)", expanded=False):
                    display_cols = ['시간', '운동종목', '무게(kg)', '횟수', '메모']
                    st.dataframe(day_data[display_cols], use_container_width=True, hide_index=True)
                    
                    if st.checkbox(f"🗑️ {d} 기록 삭제 모드", key=f"del_mode_{d}"):
                        to_delete = st.multiselect("삭제할 운동을 선택하세요", day_data['운동종목'].unique(), key=f"del_sel_{d}")
                        if st.button("선택한 운동 삭제", key=f"del_btn_{d}"):
                            rows_to_drop = df[
                                (df['날짜'] == d) & 
                                (df['운동종목'].isin(to_delete))
                            ].index
                            df.drop(rows_to_drop, inplace=True)
                            df.to_csv('my_workout_log.csv', index=False, encoding='utf-8-sig')
                            st.success("삭제되었습니다. 새로고침 됩니다.")
                            st.rerun()
        else:
            st.info(f"{selected_month}월에는 아직 기록이 없습니다.")

    else:
        st.info("아직 저장된 데이터가 없습니다. 첫 운동을 기록해보세요!")