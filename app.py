import streamlit as st
import plotly.graph_objects as go
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="메타버스 베게 데모",
    page_icon="🛏️",
    layout="wide"
)

# 상태 관리
if 'sleep_quality' not in st.session_state:
    st.session_state.sleep_quality = 85
if 'is_sleeping' not in st.session_state:
    st.session_state.is_sleeping = False
if 'time_of_day' not in st.session_state:
    st.session_state.time_of_day = 'night'
if 'pillow_color' not in st.session_state:
    st.session_state.pillow_color = '#4B0082'
if 'pillow_texture' not in st.session_state:
    st.session_state.pillow_texture = 'smooth'
if 'sleep_start_time' not in st.session_state:
    st.session_state.sleep_start_time = None
if 'sleep_history' not in st.session_state:
    st.session_state.sleep_history = []

def calculate_sleep_quality():
    if not st.session_state.sleep_start_time:
        return 0
    
    # 수면 시간 계산 (분 단위)
    sleep_duration = (datetime.now() - st.session_state.sleep_start_time).total_seconds() / 60
    
    # 기본 점수 (최대 70점)
    base_score = min(70, sleep_duration / 2)
    
    # 시간대 보너스 (최대 20점)
    time_bonus = {
        'night': 20,
        'morning': 10,
        'afternoon': 5
    }[st.session_state.time_of_day]
    
    # 질감 보너스 (최대 10점)
    texture_bonus = {
        'smooth': 10,
        'rough': 5,
        'pattern': 7
    }[st.session_state.pillow_texture]
    
    return min(100, int(base_score + time_bonus + texture_bonus))

def save_sleep_record():
    if st.session_state.sleep_start_time:
        sleep_duration = (datetime.now() - st.session_state.sleep_start_time).total_seconds() / 60
        quality = calculate_sleep_quality()
        
        record = {
            'date': datetime.now().date(),
            'start_time': st.session_state.sleep_start_time,
            'duration': sleep_duration,
            'quality': quality,
            'time_of_day': st.session_state.time_of_day,
            'pillow_texture': st.session_state.pillow_texture
        }
        
        st.session_state.sleep_history.append(record)
        # 최근 7일 기록만 유지
        st.session_state.sleep_history = st.session_state.sleep_history[-7:]

# 3D 베게 모델 생성
def create_pillow_model():
    # 간단한 3D 베게 모델 생성
    x = np.linspace(-1, 1, 100)
    y = np.linspace(-1, 1, 100)
    X, Y = np.meshgrid(x, y)
    
    # 질감에 따른 Z값 조정
    if st.session_state.pillow_texture == 'smooth':
        Z = 0.2 * np.sin(X * np.pi) * np.sin(Y * np.pi)
    elif st.session_state.pillow_texture == 'rough':
        Z = 0.2 * np.sin(X * np.pi * 2) * np.sin(Y * np.pi * 2)
    else:  # pattern
        Z = 0.2 * (np.sin(X * np.pi * 3) + np.sin(Y * np.pi * 3))
    
    # 시간대별 색상 조정
    base_color = st.session_state.pillow_color
    if st.session_state.time_of_day == 'night':
        # 밤에는 어두운 색상으로
        colorscale = [
            [0, base_color],
            [1, base_color]
        ]
    elif st.session_state.time_of_day == 'morning':
        # 아침에는 밝은 색상으로
        colorscale = [
            [0, base_color],
            [1, base_color]
        ]
    else:  # afternoon
        # 오후에는 중간 톤으로
        colorscale = [
            [0, base_color],
            [1, base_color]
        ]
    
    fig = go.Figure(data=[go.Surface(
        x=X, y=Y, z=Z,
        colorscale=colorscale,
        showscale=False
    )])
    
    # 시간대별 배경색 설정
    bg_color = {
        'night': 'rgb(20, 20, 40)',
        'morning': 'rgb(240, 240, 255)',
        'afternoon': 'rgb(255, 255, 240)'
    }[st.session_state.time_of_day]
    
    fig.update_layout(
        title='메타버스 베게',
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
            bgcolor=bg_color
        ),
        width=800,
        height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color
    )
    return fig

# 메인 레이아웃
st.title("🛏️ 메타버스 베게 데모")

# 사이드바 설정
with st.sidebar:
    st.header("설정")
    
    # 시간대 선택
    time_of_day = st.radio(
        "시간대 선택",
        ["아침", "오후", "밤"],
        index=2
    )
    st.session_state.time_of_day = time_of_day
    
    # 베게 색상 선택
    pillow_color = st.color_picker("베게 색상", "#4B0082")
    st.session_state.pillow_color = pillow_color
    
    # 베게 질감 선택
    texture = st.selectbox(
        "베게 질감",
        ["부드러운", "거친", "패턴"]
    )
    st.session_state.pillow_texture = texture.lower()
    
    # 수면 시작/종료 버튼
    if st.button("수면 시작" if not st.session_state.is_sleeping else "깨우기", 
                 use_container_width=True):
        st.session_state.is_sleeping = not st.session_state.is_sleeping
        if st.session_state.is_sleeping:
            st.session_state.sleep_start_time = datetime.now()
        else:
            save_sleep_record()
        st.rerun()

# 메인 컨텐츠
col1, col2 = st.columns([3, 2])

with col1:
    # 3D 베게 모델 표시
    fig = create_pillow_model()
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})

with col2:
    # 수면 통계
    st.subheader("수면 통계")
    
    # 수면 품질 게이지
    sleep_quality = calculate_sleep_quality()
    st.metric("수면 품질", f"{sleep_quality}%")
    
    # 수면 품질 게이지 차트
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sleep_quality,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "purple"},
               'steps': [
                   {'range': [0, 50], 'color': "red"},
                   {'range': [50, 80], 'color': "yellow"},
                   {'range': [80, 100], 'color': "green"}
               ]}
    ))
    gauge.update_layout(
        height=200,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(gauge, use_container_width=True, config={'responsive': True})
    
    # 수면 상태 표시
    if st.session_state.is_sleeping:
        current_quality = calculate_sleep_quality()
        st.success("캐릭터가 베게에서 자고 있습니다.")
        st.info(f"현재 수면 품질: {current_quality}%")
    else:
        st.warning("캐릭터가 깨어있습니다.")

# 수면 기록
st.subheader("수면 기록")
if st.session_state.sleep_history:
    sleep_data = pd.DataFrame(st.session_state.sleep_history)
    sleep_data['date'] = pd.to_datetime(sleep_data['date'])
    sleep_data = sleep_data.set_index('date')
    
    # 반응형 차트
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sleep_data.index,
        y=sleep_data['quality'],
        mode='lines+markers',
        name='수면 품질'
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_title='날짜',
        yaxis_title='수면 품질 (%)'
    )
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
    
    # 상세 기록 표시 (탭으로 구분)
    tab1, tab2 = st.tabs(["차트 보기", "상세 기록"])
    
    with tab1:
        st.line_chart(sleep_data['quality'])
    
    with tab2:
        for record in reversed(st.session_state.sleep_history):
            st.write(f"""
            - 날짜: {record['date']}
            - 수면 시간: {int(record['duration'])}분
            - 수면 품질: {record['quality']}%
            - 시간대: {record['time_of_day']}
            - 베게 질감: {record['pillow_texture']}
            ---
            """)
else:
    st.info("아직 수면 기록이 없습니다. 수면을 시작해보세요!")

# 설명
st.markdown("""
### 사용 방법
1. 사이드바에서 시간대를 선택하세요 (아침/오후/밤)
2. 베게의 색상과 질감을 커스터마이징하세요
3. '수면 시작' 버튼을 눌러 캐릭터를 재우세요
4. 수면 품질과 통계를 확인하세요
""") 