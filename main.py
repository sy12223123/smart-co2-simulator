import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="스마트 교실 공기질 예측기", layout="centered")

st.title("스마트 교실 공기질 예측 & 환기 도우미")
st.markdown("교실 상황을 입력하면, 실내 CO₂ 농도를 예측하고 환기 타이밍을 안내해드립니다.")

# 입력 폼
with st.form("input_form"):
    st.subheader("교실 정보 입력")

    num_students = st.number_input("학생 수", min_value=1, max_value=50, value=30)
    class_duration = st.slider("수업 시간 (분)", min_value=10, max_value=120, value=50)
    area = st.number_input("교실 면적 (m²)", min_value=10, max_value=100, value=50)
    window_state = st.selectbox("창문 상태", ["닫힘", "틈 열기", "완전 열기"])
    heating_state = st.selectbox("냉난방 중인가요?", ["없음", "냉방 중", "난방 중"])
    outside_temp = st.number_input("외부 온도 (°C)", min_value=-20, max_value=50, value=15)
    now_time = datetime.now().strftime("%H:%M")

    submitted = st.form_submit_button("예측하기")

# CO₂ 계산 함수
def predict_co2(students, duration, area, window):
    generation_rate = 0.3  # L/min per student
    window_factor = {
        "닫힘": 0.1,
        "틈 열기": 0.3,
        "완전 열기": 0.6
    }
    ventilation = window_factor[window]
    volume = area * 2.5  # 교실 높이 2.5m 가정
    total_generated = students * generation_rate * duration  # L
    concentration_ppm = (total_generated / (volume * 1000)) * 1_000_000 / (ventilation + 0.01)
    return round(concentration_ppm, 2)

# 결과 출력
if submitted:
    st.success("입력이 완료되었습니다.")
    st.write(f"현재 시각: {now_time}")
    st.write(f"학생 수: {num_students}명, 수업 시간: {class_duration}분")
    st.write(f"창문 상태: {window_state}, 냉난방: {heating_state}")

    predicted_ppm = predict_co2(num_students, class_duration, area, window_state)
    st.subheader("예측 결과")
    st.write(f"예상 CO₂ 농도: **{predicted_ppm} ppm**")

    if predicted_ppm >= 1500:
        st.error("위험 수준입니다! 지금 바로 창문을 열어 환기하세요.")
    elif predicted_ppm >= 1000:
        st.warning("보통 수준입니다. 환기하는 것이 좋습니다.")
    else:
        st.success("공기질이 양호합니다. 현재 상태를 유지하세요.")

    # 누적 농도 시뮬레이션
    time_list = []
    co2_list = []
    for t in range(1, class_duration + 1):
        co2 = predict_co2(num_students, t, area, window_state)
        time_list.append(t)
        co2_list.append(co2)

    # 그래프 출력
    st.subheader("CO₂ 농도 변화 그래프")
    fig, ax = plt.subplots()
    ax.plot(time_list, co2_list, label='예상 CO₂ 농도', color='green')
    ax.axhline(y=1000, color='orange', linestyle='--', label='환기 권장 기준 (1000ppm)')
    ax.axhline(y=1500, color='red', linestyle='--', label='위험 기준 (1500ppm)')
    ax.set_xlabel("Time Elapsed (min)")
    ax.set_ylabel("CO₂ Concentration (ppm)")
    ax.set_title("CO₂ Level During Clas")
    ax.legend()
    st.pyplot(fig)

    # 누적 배출량 출력
    co2_per_min = num_students * 0.3  # L/min
    total_co2 = round(co2_per_min * class_duration, 1)
    st.subheader("누적 CO₂ 배출량")
    st.write(f"수업 동안 예상 누적 CO₂ 배출량: **{total_co2} L**")
    st.subheader("Heat Loss Simulation")

    target_temp = 24 if heating_state == "냉방 중" else 22 if heating_state == "난방 중" else None

    if target_temp:
        temp_diff = abs(outside_temp - target_temp)
        window_factor = {
            "닫힘": 0.1,
            "틈 열기": 0.3,
            "완전 열기": 0.6
        }
        ventilation = window_factor[window_state]
        heat_loss_index = round(temp_diff * ventilation * class_duration, 2)

        st.write(f"실내/외 온도 차: **{temp_diff}°C**")
        st.write(f"예상 열 손실 지수: **{heat_loss_index} 단위**")

        # 해석 문장
        if heat_loss_index > 100:
            st.warning("지금 상태로는 냉난방 손실이 상당히 클 수 있어요.")
            st.info("가능하다면 창문을 틈 열기 수준으로 조절하거나, 10분 뒤에 환기하는 것을 추천해요.")
        elif heat_loss_index > 50:
            st.info("냉난방 손실이 다소 있을 수 있지만, 공기질이 나쁘면 환기해도 괜찮아요.")
        else:
            st.success("냉난방 손실이 거의 없어요. 지금 창문 상태로 환기해도 괜찮아요.")
    else:
        st.info("냉난방이 꺼져 있는 상태에서는 열 손실이 발생하지 않습니다.")
        st.subheader("Recommended Eco-Friendly Ventilation Routine")


        # 단순 환기 루틴 제안 로직
        st.subheader("Recommended Eco-Friendly Ventilation Routine")

        if heating_state == "없음":
            st.info("냉난방이 꺼져 있으니 공기질 위주로 환기 루틴을 추천할게요.")
            st.write("→ 매 20분마다 3분간 창문 열기")
        elif heating_state in ["냉방 중", "난방 중"]:
            if window_state == "완전 열기":
                st.warning("냉난방 중에는 완전 열기보다 짧고 간헐적인 환기가 더 효율적이에요.")
                st.write("→ 매 30분마다 2분간 창문 틈 열기 추천")
            elif window_state == "틈 열기":
                st.success("현재 창문 상태가 에너지 효율도 좋고, 환기에도 적절해요!")
                st.write("→ 25분 수업 후 2분 환기 유지 추천")
            else:
                st.info("창문이 닫혀 있다면, 최소 40분마다 3분은 꼭 환기해주세요.")
