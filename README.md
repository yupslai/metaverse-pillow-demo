# 메타버스 베게 데모

Streamlit을 활용한 인터랙티브한 메타버스 베게 데모 애플리케이션입니다.

## 주요 기능

- 3D 베게 모델 시각화
- 시간대별 환경 변화 (아침/오후/밤)
- 베게 커스터마이징 (색상, 질감)
- 수면 품질 측정 및 통계
- 수면 기록 시각화

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/yourusername/metaverse-pillow-demo.git
cd metaverse-pillow-demo
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
streamlit run app.py
```

## 사용 방법

1. 사이드바에서 시간대를 선택하세요 (아침/오후/밤)
2. 베게의 색상과 질감을 커스터마이징하세요
3. '수면 시작' 버튼을 눌러 캐릭터를 재우세요
4. 수면 품질과 통계를 확인하세요

## 기술 스택

- Streamlit
- Plotly
- NumPy
- Pandas
- Pillow

## 라이선스

MIT License 