import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 모바일 화면 설정
st.set_page_config(page_title="Lunahyeon's Workout", layout="centered")

# --- 1. 세션 상태 초기화 ---
if 'exercise_index' not in st.session_state:
    st.session_state['exercise_index'] = 0
if 'last_selected_date' not in st.session_state:
    st.session_state['last_selected_date'] = None

# 제목을 조금 더 심플하게 변경 (공간 절약)
st.subheader("💪 Lunahyeon's 운동일지")

# 탭 구성
tab1, tab2 = st.tabs(["✅ 기록 입력", "📊 주차별 기록 확인"])

with tab1:
    # ==========================================
    # ★ 수정된 부분: expander(접기) 제거하고 바로 보여주기
    # ==========================================
    st.caption("📅 날짜 및 신체 정보") # 작은 소제목으로 대체
    
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", datetime.now(), label_visibility="collapsed")
    with col2:
        current_time = datetime.now().strftime("%H:%M")
        arrival_time = st.text_input("시간", value=current_time, label_visibility="collapsed")
    
    # 체중 입력도 바로 아래에 배치
    weight = st.number_input("오늘 몸무게 (kg)", value=46.0, step=0.1, format="%.1f")

    # --- 2. 요일별 루틴 설정 ---
    weekday = date.weekday()
    
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

    if weekday in [1, 3]: # 화, 목
        exercise_list = routine_B
        routine_name = "🔥 하체 집중 루틴 (화/목)"
        style_color = "#FF4B4B" # 빨간색 포인트
    else:
        exercise_list = routine_A
        routine_name = "💪 상체/전신 루틴 (월/수/금)"
        style_color = "#1E90FF" # 파란색 포인트

    # 날짜 변경 시 루틴 초기화
    if st.session_state['last_selected_date'] != date:
        st.session_state['exercise_index'] = 0
        st.session_state['last_selected_date'] = date
        st.rerun()

    st.markdown("---")
    # 루틴 안내를 좀 더 예쁘게 (색상 적용)
    st.markdown(f"<div style='background-color: {style_color}; padding: 10px; border-radius: 5px; color: white; text-align: center; margin-bottom: 10px;'>{routine_name}</div>", unsafe_allow_html=True)
    
    st.subheader("🔥 운동 수행 체크")

    if st.session_state['exercise_index'] >= len(exercise_list):
        st.session_state['exercise_index'] = 0

    selected_exercise = st.selectbox(
        "운동 종목 (자동 순서 변경)", 
        exercise_list, 
        index=st.session_state['exercise_index']
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
    else:
        st.caption("이 운동은 등록된 영상이 없습니다.")

    # --- 입력 폼 ---
    with st.form("workout_form", clear_on_submit=True):
        
        # [CASE 1] 러닝/걷기
        if selected_exercise == "러닝/걷기":
            st.markdown("🏃‍♀️ **유산소 설정**")
            c1, c2, c3 = st.columns(3)
            with c1:
                run_minutes = st.number_input("시간(분)", min_value=1, value=30, step=5)
            with c2:
                run_speed = st.number_input("속도", min_value=1.0, max_value=10.0, value=5.6, step=0.1, format="%.1f")
            with c3:
                run_incline = st.number_input("경사", min_value=0, max_value=9, value=0, step=1)
            
            st.caption(f"설정: {run_minutes}분 / 속도 {run_speed} / 경사 {run_incline}")
            sets_done = ["Completed"] 

        # [CASE 2] 근력 운동
        else:
            c1, c2 = st.columns([1, 1])
            with c1:
                exercise_weight = st.number_input("무게 (kg)", min_value=0, step=5, value=10)
            with c2:
                base_reps = st.number_input("1세트당 횟수", value=15, step=1)

            st.write(f"👇 **{base_reps}회씩 수행했다면 체크하세요**")
            
            check_cols = st.columns(4)
            sets_done = []
            for i in range(4):
                with check_cols[i]:
                    if st.checkbox(f"{base_reps}", key=f"set_{i}"):
                        sets_done.append(str(base_reps))

        st.markdown("---")
        memo = st.text_area("메모", placeholder="특이사항 없음", height=70)
        
        submit_btn = st.form_submit_button("기록 저장 & 다음 운동으로 (+)", use_container_width=True)

    # 저장 로직
    if submit_btn:
        if selected_exercise != "러닝/걷기" and not sets_done:
            st.warning("⚠️ 수행한 칸을 하나 이상 체크해주세요!")
        else:
            weekdays = ["월", "화", "수", "목", "금", "토", "일"]
            day_name = weekdays[weekday]
            date_str = f"{date.strftime('%Y-%m-%d')} ({day_name})"
            
            if selected_exercise == "러닝/걷기":
                save_weight = run_speed       
                save_reps = f"{run_minutes}분" 
                full_memo = f"[경사: {run_incline}] {memo}" if memo else f"경사: {run_incline}"
            else:
                save_weight = exercise_weight
                save_reps = " ".join(sets_done)
                full_memo = memo

            new_data = {
                "날짜": [date_str],
                "시간": [arrival_time],
                "몸무게": [weight],
                "운동종목": [selected_exercise],
                "무게(kg)": [save_weight], 
                "횟수": [save_reps],       
                "메모": [full_memo]
            }
            
            df = pd.DataFrame(new_data)
            file_name = 'my_workout_log.csv'
            
            if not os.path.exists(file_name):
                df.to_csv(file_name, index=False, encoding='utf-8-sig')
            else:
                df.to_csv(file_name, mode='a', header=False, index=False, encoding='utf-8-sig')
            
            current_idx = st.session_state['exercise_index']
            next_idx = (current_idx + 1) % len(exercise_list)
            st.session_state['exercise_index'] = next_idx
            
            st.success(f"[{selected_exercise}] 저장 완료! 다음: [{exercise_list[next_idx]}]")
            st.rerun()

# --- 탭 2: 주차별 기록 확인 ---
with tab2:
    if os.path.exists('my_workout_log.csv'):
        df = pd.read_csv('my_workout_log.csv')
        df['temp_date'] = pd.to_datetime(df['날짜'].str.slice(0, 10))
        df['year_month'] = df['temp_date'].dt.strftime('%Y-%m')
        available_months = sorted(df['year_month'].unique(), reverse=True)
        
        st.subheader("📅 월별 기록 선택")
        if available_months:
            selected_month = st.selectbox("확인하고 싶은 달을 선택하세요", available_months)
            month_df = df[df['year_month'] == selected_month].copy()
            month_df['week_num'] = (month_df['temp_date'].dt.day - 1) // 7 + 1
            
            st.divider()
            has_record = False
            for week in range(1, 6):
                week_data = month_df[month_df['week_num'] == week]
                if not week_data.empty:
                    has_record = True
                    with st.expander(f"📌 {selected_month} - {week}주차 기록 보기", expanded=True):
                        display_cols = ['날짜', '운동종목', '무게(kg)', '횟수', '메모']
                        st.dataframe(week_data[display_cols], use_container_width=True, hide_index=True)
            if not has_record:
                st.info("선택하신 달에는 기록이 없습니다.")
        else:
            st.info("기록이 없습니다.")
    else:
        st.info("아직 저장된 기록이 없습니다.")