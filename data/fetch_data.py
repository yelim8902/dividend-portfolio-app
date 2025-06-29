import yfinance as yf
import pandas as pd
import streamlit as st
from typing import List, Dict, Any

@st.cache_data(ttl=3600)
def get_realtime_stock_data(tickers: List[str]) -> pd.DataFrame:
    """
    병렬로 yfinance에서 실시간 종목 데이터를 수집합니다.
    Args:
        tickers (List[str]): 종목 티커 리스트
    Returns:
        pd.DataFrame: 종목별 실시간 데이터
    """
    data = []
    progress = st.progress(0, text="실시간 종목 데이터 로딩 중...")
    def fetch_one(t: str) -> Dict[str, Any]:
        try:
            stock = yf.Ticker(t)
            price = stock.history(period='1d')['Close'].iloc[-1]
            div_yield = calc_dividend_yield(t)
            eps = stock.info.get('trailingEps', 1.0) or 1.0
            name = stock.info.get('shortName', t)
            return {
                '티커': t,
                '종목명': name,
                '현재가($)': price if price is not None else 'N/A',
                '배당수익률': div_yield,
                '배당수익률(%)': f"{div_yield*100:.2f}",
                'EPS': eps
            }
        except Exception as e:
            return {
                '티커': t,
                '종목명': t,
                '현재가($)': 'N/A',
                '배당수익률': 0.0,
                '배당수익률(%)': 'N/A',
                'EPS': 'N/A',
                '오류': str(e)
            }
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = []
        for i, res in enumerate(executor.map(fetch_one, tickers)):
            results.append(res)
            progress.progress((i+1)/len(tickers), text=f"{i+1}/{len(tickers)} 완료")
        data.extend(results)
    progress.empty()
    return pd.DataFrame(data)

@st.cache_data
def get_valuation_info(tickers: List[str]) -> pd.DataFrame:
    """
    주어진 티커 리스트에 대해 P/E, P/B 등 밸류에이션 정보를 반환합니다.
    Args:
        tickers (List[str]): 종목 티커 리스트
    Returns:
        pd.DataFrame: 각 종목별 밸류에이션 정보
    """
    data = []
    progress = st.progress(0, text="밸류에이션 데이터 로딩 중...")
    for i, t in enumerate(tickers):
        try:
            stock = yf.Ticker(t)
            pe = stock.info.get('trailingPE', None)
            pb = stock.info.get('priceToBook', None)
            data.append({'티커': t, 'P/E': pe, 'P/B': pb})
        except Exception:
            data.append({'티커': t, 'P/E': None, 'P/B': None})
        progress.progress((i+1)/len(tickers), text=f"{i+1}/{len(tickers)} 완료")
    progress.empty()
    return pd.DataFrame(data)

def calc_dividend_yield(ticker: str) -> float:
    """
    최근 1년간 실제 지급된 배당금 합계 ÷ 현재가로 배당수익률을 계산합니다.
    Args:
        ticker (str): 종목 티커
    Returns:
        float: 배당수익률
    """
    stock = yf.Ticker(ticker)
    try:
        divs = stock.history(period='1y')['Dividends'].sum()
        price = stock.history(period='1d')['Close'].iloc[-1]
        return divs / price if price and price > 0 else 0.0
    except Exception:
        return 0.0 