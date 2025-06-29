# 🎯 심플 목표 기반 배당 포트폴리오

Streamlit을 사용한 배당 포트폴리오 최적화 웹 애플리케이션입니다.

## 📋 기능

- **목표 설정**: 월 배당금 목표와 투자 기간 설정
- **종목 추천**: 배당수익률 기반 상위 5개 종목 추천
- **포트폴리오 최적화**: Markowitz 최적화를 통한 자산 배분
- **시각화**: 자산 성장 그래프와 포트폴리오 비중 파이 차트

## 🚀 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/yelim8902/dividend-portfolio-app.git
cd dividend-portfolio-app
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 애플리케이션 실행

```bash
streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 📦 주요 패키지

- **Streamlit**: 웹 애플리케이션 프레임워크
- **yfinance**: Yahoo Finance 데이터 수집
- **pandas**: 데이터 처리
- **numpy**: 수치 계산
- **scipy**: 최적화 알고리즘
- **altair**: 데이터 시각화

## 📁 프로젝트 구조

```
app/
├── data/
│   ├── __init__.py
│   └── fetch_data.py          # 주식 데이터 수집
├── portfolio/
│   ├── __init__.py
│   └── optimize.py            # 포트폴리오 최적화
├── utils/
│   └── __init__.py
├── streamlit_app.py           # 메인 애플리케이션
├── requirements.txt           # 패키지 의존성
└── README.md
```

## 💡 사용법

1. **목표 설정**: 원하는 월 배당금과 투자 기간을 입력
2. **종목 추천**: "📈 추천 배당 종목 뽑기" 버튼 클릭
3. **최적화 실행**: "▶️ 최적화 실행" 버튼으로 포트폴리오 최적화
4. **결과 확인**: 예상 자산, 필요 투자금, 달성 여부 확인

## 🔧 고급 설정

- **현재 자산**: 현재 보유한 투자금액
- **매달 투자금**: 월별 추가 투자금액
- **세율**: 배당소득세율 설정
- **무위험이자율**: 무위험 수익률 설정
- **위험 허용도**: 보수적/중립/공격적 선택

## 📊 추천 종목 풀

현재 다음 종목들을 대상으로 추천합니다:

- KO (Coca-Cola)
- O (Realty Income)
- T (AT&T)
- PG (Procter & Gamble)
- PEP (PepsiCo)
- VYM (Vanguard High Dividend Yield ETF)
- SCHD (Schwab US Dividend Equity ETF)

## ⚠️ 주의사항

- 이 애플리케이션은 교육 및 참고용입니다
- 실제 투자 결정은 전문가와 상담 후 진행하세요
- 과거 성과가 미래 수익을 보장하지 않습니다
- yfinance API의 데이터 정확성을 항상 확인하세요

## 📝 라이선스

MIT License
