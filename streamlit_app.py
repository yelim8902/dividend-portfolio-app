import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from scipy.optimize import minimize
from data.fetch_data import get_realtime_stock_data
from portfolio.optimize import get_return_risk_cov, future_value, yearly_asset_growth

st.set_page_config(page_title="심플 배당 포트폴리오", layout="centered")
st.title("🎯 심플 목표 기반 배당 포트폴리오")

# --- 1) 목표 설정 ---
st.header("1️⃣ 목표 설정")
col1, col2 = st.columns(2)
goal = col1.number_input("목표 월 배당금(원)", value=200_000, step=10_000)
years = col2.number_input("투자 기간(년)", value=5, step=1)
risk = st.selectbox("위험 허용도", ["보수적","중립","공격적"])

with st.expander("⚙️ 고급 설정 (선택)"):
    current = st.number_input("현재 자산(원)", value=0, step=100_000)
    monthly = st.number_input("매달 투자금(원)", value=100_000, step=10_000)
    tax = st.slider("세율(%)", 0.0, 30.0, 15.4) / 100
    rf = st.slider("무위험이자율(%)", 0.0, 10.0, 3.0) / 100

# --- 2) 종목 추천 ---
st.header("2️⃣ 종목 추천")
if "tickers" not in st.session_state:
    if st.button("📈 추천 배당 종목 뽑기"):
        all_pool = ['KO','O','T','PG','PEP','VYM','SCHD']
        df = get_realtime_stock_data(all_pool)
        st.write('DEBUG: 추천 종목 원본 데이터프레임', df)
        st.write('DEBUG: 컬럼명', df.columns)
        st.write('DEBUG: 데이터 타입', df.dtypes)
        df = df[df["배당수익률"]>0]
        if df.empty:
            st.error("배당수익률이 0보다 큰 종목이 없습니다. 데이터 또는 네트워크 문제일 수 있습니다.")
        else:
            df["배당수익률"] = pd.Series(pd.to_numeric(df["배당수익률"], errors='coerce')).fillna(0.0)
            top5 = df.sort_values(by=str("배당수익률"), ascending=False).head(5)["티커"].to_numpy(dtype=str).tolist()  # type: ignore
            st.session_state.tickers = top5
            st.success("추천 종목: " + ", ".join(top5))
else:
    st.write("▶️ 선택된 종목 풀:", st.session_state.tickers)

# --- 3) 결과 보기 ---
st.header("3️⃣ 결과 보기")
def markowitz_opt(mr, cov, risk, rf, max_weight=0.4):
    n = len(mr)
    init = np.ones(n)/n
    bounds = tuple((0, max_weight) for _ in range(n))
    cons = {'type':'eq', 'fun': lambda w: np.sum(w)-1}
    if risk == "보수적":
        obj = lambda w: np.sqrt(np.dot(w.T, np.dot(cov, w)))
    elif risk == "공격적":
        obj = lambda w: -np.dot(w, mr)
    else:
        obj = lambda w: -(np.dot(w, mr)-rf)/(np.sqrt(np.dot(w.T, np.dot(cov, w)))+1e-8)
    res = minimize(obj, init, bounds=bounds, constraints=cons)
    return res.x

if st.button("▶️ 최적화 실행", key="run"):
    tickers = st.session_state.get("tickers", [])
    if not tickers:
        st.warning("먼저 종목을 추천받아주세요!")
    else:
        df = get_realtime_stock_data(tickers)
        st.write('DEBUG: 최적화용 데이터프레임', df)
        st.write('DEBUG: 컬럼명', df.columns)
        st.write('DEBUG: 데이터 타입', df.dtypes)
        mr, sd, cov = get_return_risk_cov(tickers, years=3)
        st.write('DEBUG: mr', mr)
        st.write('DEBUG: cov', cov)
        if df.empty:
            st.error("배당수익률이 0보다 큰 종목이 없습니다. 데이터 또는 네트워크 문제일 수 있습니다.")
        else:
            df["배당수익률"] = pd.Series(pd.to_numeric(df["배당수익률"], errors='coerce')).fillna(0.0)
            top5 = df.sort_values(by=str("배당수익률"), ascending=False).head(5)["티커"].to_numpy(dtype=str).tolist()  # type: ignore
            st.session_state.tickers = top5
            st.success("추천 종목: " + ", ".join(top5))
        weights = markowitz_opt(mr.values, cov.values, risk, rf, max_weight=0.4)
        st.write('DEBUG: weights', weights)
        port_yield = float(np.dot(weights, df["배당수익률"].to_numpy(dtype=float)))
        port_return = float(np.dot(weights, mr.values))
        st.write('DEBUG: port_yield', port_yield)
        st.write('DEBUG: port_return', port_return)
        est_asset = future_value(current, monthly, years, port_return)
        required = (goal*12)/(1-tax) / port_yield if port_yield>0 else None

        c1, c2, c3 = st.columns(3)
        c1.metric("예상 자산", f"{est_asset:,.0f}원")
        if required:
            c2.metric("필요 투자금", f"{required:,.0f}원")
            c3.metric("달성 여부", "✅" if est_asset>=required else "❌")
        else:
            c2.metric("필요 투자금", "계산 불가")
            c3.metric("달성 여부", "❌")

        growth_df = yearly_asset_growth(current, monthly, years, port_return)
        line = alt.Chart(growth_df).mark_line(point=True).encode(
            x="연도:O", y=alt.Y("예상 자산:Q", title="자산(원)"),
            tooltip=[alt.Tooltip("연도"), alt.Tooltip("예상 자산", format=",")]
        )
        pie = alt.Chart(pd.DataFrame({
            "종목": df["티커"], "비중": weights*100
        })).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("비중", type="quantitative"),
            color="종목:N",
            tooltip=["종목", alt.Tooltip("비중", format='.1f')]
        )
        left, right = st.columns(2)
        left.altair_chart(line, use_container_width=True)
        right.altair_chart(pie, use_container_width=True) 