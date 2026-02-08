"""
A minimal, readable portfolio backtester.

- Uses daily close prices.
- Long-only: holds tickers with signal==1, otherwise cash.
- Allocates equally across eligible tickers each day.
- Rebalances daily (simple + deterministic).

Output:
- Equity curve (history DataFrame)
- final_value
- total_return_pct
"""

from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

from trading_algorithms import make_signal


@dataclass
class BacktestResult:
    history: pd.DataFrame
    final_value: float
    total_return_pct: float


def backtest_equal_weight_long_only(
    all_data: dict[str, pd.DataFrame],
    initial_capital: float,
    strategy: str,
) -> BacktestResult:
    # Align all tickers on common dates (inner join)
    closes = []
    for ticker, df in all_data.items():
        if "close" not in df.columns:
            raise ValueError(f"{ticker} is missing 'close' column")
        closes.append(df[["close"]].rename(columns={"close": ticker}))

    close_df = pd.concat(closes, axis=1, join="inner").dropna().sort_index()
    if close_df.empty:
        raise ValueError("No overlapping dates across tickers (check your date range).")

    # Signals (0/1)
    sig_df = pd.DataFrame(index=close_df.index)
    for ticker in close_df.columns:
        sig_df[ticker] = (
            make_signal(close_df[ticker], strategy=strategy)
            .reindex(close_df.index)
            .fillna(0)
            .astype(int)
        )

    cash = float(initial_capital)
    shares = {ticker: 0.0 for ticker in close_df.columns}

    rows = []

    for dt, prices in close_df.iterrows():
        # Which tickers do we want to hold today?
        eligible = [t for t in close_df.columns if sig_df.loc[dt, t] == 1]

        # Current portfolio value at market prices
        holdings_value = sum(shares[t] * prices[t] for t in close_df.columns)
        port_value = cash + holdings_value

        # Target: equal weight across eligible, else all cash
        target_shares = {t: 0.0 for t in close_df.columns}
        if eligible:
            target_value_each = port_value / len(eligible)
            for t in eligible:
                target_shares[t] = target_value_each / prices[t]

        # Rebalance: trade to target (NO fees/slippage)
        for t in close_df.columns:
            delta = target_shares[t] - shares[t]
            if abs(delta) < 1e-12:
                continue

            if delta > 0:
                # BUY
                cost = delta * prices[t]
                if cost > cash:
                    # Scale buy down to available cash
                    delta = cash / prices[t]
                    cost = delta * prices[t]
                cash -= cost
                shares[t] += delta
            else:
                # SELL
                proceeds = (-delta) * prices[t]
                cash += proceeds
                shares[t] += delta  # delta is negative

        # Record end-of-day portfolio value
        holdings_value = sum(shares[t] * prices[t] for t in close_df.columns)
        port_value = cash + holdings_value

        rows.append(
            {
                "date": dt,
                "cash": cash,
                "holdings_value": holdings_value,
                "portfolio_value": port_value,
                "num_positions": sum(1 for t in close_df.columns if shares[t] > 1e-12),
            }
        )

    hist = pd.DataFrame(rows).set_index("date")

    final_value = float(hist["portfolio_value"].iloc[-1])
    total_return_pct = (final_value / initial_capital - 1.0) * 100.0

    return BacktestResult(history=hist, final_value=final_value, total_return_pct=total_return_pct)
