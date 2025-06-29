import numpy as np
import pandas as pd
import yfinance as yf
from typing import List, Tuple

def get_return_risk_cov(tickers: List[str], years: int = 3) -> Tuple[pd.Series, pd.Series, pd.DataFrame]:
    """
    과거 가격 데이터로 기대수익률, 변동성, 공분산 계산
    Args:
        tickers (List[str]): 종목 티커 리스트
        years (int): 과거 데이터 연수
    Returns:
        Tuple[pd.Series, pd.Series, pd.DataFrame]: (기대수익률, 변동성, 공분산행렬)
    """
    end = pd.Timestamp.today()
    start = end - pd.DateOffset(years=years)
    price_df = yf.download(tickers, start=start, end=end)["Adj Close"]
    price_df = price_df.dropna(axis=0, how='any')
    returns = price_df.pct_change().dropna()
    mean_returns = returns.mean() * 252  # 연환산
    cov_matrix = returns.cov() * 252     # 연환산
    std_devs = returns.std() * np.sqrt(252)
    return mean_returns, std_devs, cov_matrix

def future_value(current: float, monthly: float, years: float, r: float) -> float:
    """
    미래가치 계산 함수 (복리, 적립식)
    Args:
        current (float): 현재 자산
        monthly (float): 매달 투자금
        years (float): 투자 기간(년)
        r (float): 연 수익률
    Returns:
        float: 미래 자산 가치
    """
    n = years
    fv_lump = current * (1 + r) ** n
    fv_saving = monthly * 12 * (((1 + r) ** n - 1) / r) if r > 0 else monthly * 12 * n
    return fv_lump + fv_saving

def yearly_asset_growth(current: float, monthly: float, years: int, r: float) -> pd.DataFrame:
    """
    연도별 자산 성장 시뮬레이션
    Args:
        current (float): 현재 자산
        monthly (float): 매달 투자금
        years (int): 투자 기간(년)
        r (float): 연 수익률
    Returns:
        pd.DataFrame: 연도별 자산 성장
    """
    values = []
    for y in range(1, years+1):
        v = future_value(current, monthly, y, r)
        values.append({'연도': y, '예상 자산': v})
    return pd.DataFrame(values)

def monthly_asset_growth(current: float, monthly: float, years: int, r: float) -> pd.DataFrame:
    """
    월별 자산 성장 시뮬레이션
    Args:
        current (float): 현재 자산
        monthly (float): 매달 투자금
        years (int): 투자 기간(년)
        r (float): 연 수익률
    Returns:
        pd.DataFrame: 월별 자산 성장
    """
    values = []
    for m in range(1, years*12+1):
        n = m / 12
        v = future_value(current, monthly, n, r)
        values.append({'월': m, '예상 자산': v})
    return pd.DataFrame(values) 