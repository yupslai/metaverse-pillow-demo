import streamlit as st
import plotly.graph_objects as go
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import json
import base64
import os

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
    
    # 시간대 매핑
    time_mapping = {
        "아침": "morning",
        "오후": "afternoon",
        "밤": "night"
    }
    
    # 시간대 보너스 (최대 20점)
    time_bonus = {
        'night': 20,
        'morning': 10,
        'afternoon': 5
    }.get(time_mapping.get(st.session_state.time_of_day, 'night'), 0)
    
    # 질감 매핑
    texture_mapping = {
        "부드러운": "smooth",
        "거친": "rough",
        "패턴": "pattern"
    }
    
    # 질감 보너스 (최대 10점)
    texture_bonus = {
        'smooth': 10,
        'rough': 5,
        'pattern': 7
    }.get(texture_mapping.get(st.session_state.pillow_texture, 'smooth'), 0)
    
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

# GLB 파일을 base64로 인코딩하는 함수
def get_glb_base64(model_path):
    try:
        with open(model_path, 'rb') as f:
            model_data = f.read()
        return base64.b64encode(model_data).decode('utf-8')
    except Exception as e:
        st.error(f"모델 로드 중 오류 발생: {str(e)}")
        return None

# Three.js HTML 템플릿
THREE_JS_TEMPLATE = """
<div id="scene-container" style="width: 100%; height: 600px;"></div>
<script>
    try {
        // Three.js 초기화
        const container = document.getElementById('scene-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        
        // 렌더러 설정
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setClearColor(0xffffff);
        container.appendChild(renderer.domElement);

        // 조명 설정
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 5, 5);
        scene.add(directionalLight);

        // 컨트롤 설정
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        camera.position.set(2, 2, 2);
        controls.update();

        // GLB 로더
        const loader = new THREE.GLTFLoader();

        // 캐릭터 모델 로드
        const characterData = '{character_data}';
        const characterBlob = new Blob([Uint8Array.from(atob(characterData), c => c.charCodeAt(0))], { type: 'model/gltf-binary' });
        const characterUrl = URL.createObjectURL(characterBlob);
        loader.load(characterUrl, 
            (gltf) => {
                scene.add(gltf.scene);
            },
            undefined,
            (error) => {
                console.error('캐릭터 모델 로드 중 오류:', error);
            }
        );

        // 베게 모델 로드
        const pillowData = '{pillow_data}';
        const pillowBlob = new Blob([Uint8Array.from(atob(pillowData), c => c.charCodeAt(0))], { type: 'model/gltf-binary' });
        const pillowUrl = URL.createObjectURL(pillowBlob);
        loader.load(pillowUrl, 
            (gltf) => {
                gltf.scene.position.y = -0.5;
                scene.add(gltf.scene);
            },
            undefined,
            (error) => {
                console.error('베게 모델 로드 중 오류:', error);
            }
        );

        // 애니메이션 루프
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        // 반응형 처리
        window.addEventListener('resize', () => {
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        });
    } catch (error) {
        console.error('Three.js 초기화 중 오류:', error);
    }
</script>
"""

# 3D 씬 생성 함수
def create_3d_scene():
    try:
        # GLB 파일 로드 및 base64 인코딩
        character_data = get_glb_base64("models/character.glb")
        pillow_data = get_glb_base64("models/pillow.glb")
        
        if not character_data or not pillow_data:
            return None
            
        # Three.js HTML 생성
        html = f"""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
        {THREE_JS_TEMPLATE.format(
            character_data=character_data,
            pillow_data=pillow_data
        )}
        """
        
        return html
    except Exception as e:
        st.error(f"3D 씬 생성 중 오류 발생: {str(e)}")
        return None

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
    st.session_state.pillow_texture = texture
    
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
    # 3D 씬 표시
    html = create_3d_scene()
    if html is not None:
        st.components.v1.html(html, height=600)
    else:
        st.warning("3D 씬을 표시할 수 없습니다. 모델 파일을 확인해주세요.")

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