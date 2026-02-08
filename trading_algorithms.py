"""
  signal == 1  -> eligible to hold
  signal <= 0  -> do not hold (sell / stay in cash)
"""
from __future__ import annotations
import numpy as np
import pandas as pd

def sma_crossover(close: pd.Series, fast: int = 20, slow: int = 50) -> pd.Series:
    f = close.rolling(fast).mean()
    s = close.rolling(slow).mean()
    sig = (f > s).astype(int)
    return sig.replace({0: -1})

def rsi_signal(close: pd.Series, period: int = 14, oversold: float = 30, overbought: float = 70) -> pd.Series:
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs = gain / (loss + 1e-12)
    rsi = 100 - (100 / (1 + rs))
    sig = pd.Series(0, index=close.index, dtype=int)
    sig[rsi < oversold] = 1
    sig[rsi > overbought] = -1
   
    return sig

def macd_signal(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_sig = macd.ewm(span=signal, adjust=False).mean()
    sig = (macd > macd_sig).astype(int)
    return sig.replace({0: -1})

def bollinger_signal(close: pd.Series, window: int = 20, n_std: float = 2.0) -> pd.Series:
    ma = close.rolling(window).mean()
    sd = close.rolling(window).std()
    upper = ma + n_std * sd
    lower = ma - n_std * sd
    sig = pd.Series(0, index=close.index, dtype=int)
    sig[close < lower] = 1
    sig[close > upper] = -1
    return sig

def hybrid_signal(close: pd.Series) -> pd.Series:
    # Vote across indicators
    s1 = sma_crossover(close)
    s2 = rsi_signal(close)
    s3 = macd_signal(close)
    s4 = bollinger_signal(close)

    vote = s1.add(s2, fill_value=0).add(s3, fill_value=0).add(s4, fill_value=0)
    # If votes positive -> 1, else 0 (stay out). keep it long-only for simplicity.
    return (vote > 0).astype(int)

def make_signal(close: pd.Series, strategy: str) -> pd.Series:
    strategy = strategy.upper().strip()
    if strategy == "SMA":
        return (sma_crossover(close) == 1).astype(int)
    if strategy == "RSI":
        return (rsi_signal(close) == 1).astype(int)
    if strategy == "MACD":
        return (macd_signal(close) == 1).astype(int)
    if strategy == "BBANDS":
        return (bollinger_signal(close) == 1).astype(int)
    if strategy == "HYBRID":
        return hybrid_signal(close)
    raise ValueError(f"Unknown strategy: {strategy}")
