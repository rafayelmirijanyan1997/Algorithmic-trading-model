

from __future__ import annotations

import config
from data_fetcher import fetch_all
from backtester import backtest_equal_weight_long_only


def main() -> int:
    # Read key directly from config.py
    if (not getattr(config, "POLYGON_API_KEY", None)) or ("PUT_YOUR_POLYGON_KEY_HERE" in str(config.POLYGON_API_KEY)):
        print("POLYGON_API_KEY is missing. Set it in config.py")
        return 2

    all_data = fetch_all(
        tickers=config.TICKERS,
        start=config.START_DATE,
        end=config.END_DATE,
        api_key=config.POLYGON_API_KEY,
        timespan=config.TIMESPAN,
        multiplier=config.MULTIPLIER,
        cache_dir=config.CACHE_DIR,
        use_cache=config.USE_CACHE,
    )

    res = backtest_equal_weight_long_only(
        all_data=all_data,
        initial_capital=config.INITIAL_CAPITAL,
        strategy=config.STRATEGY,
    )

    print("\n____BACKTEST RESULT____")
    print(f"Strategy:        {config.STRATEGY}")
    print(f"Tickers:         {', '.join(config.TICKERS)}")
    print(f"Date range:      {config.START_DATE} → {config.END_DATE}")
    print(f"Initial Capital: ${config.INITIAL_CAPITAL:,.2f}")
    print(f"Final Balance:   ${res.final_value:,.2f}")
    print(f"Net Profit:      ${res.final_value - config.INITIAL_CAPITAL:,.2f}")
    print(f"Total Return:    {res.total_return_pct:.2f}%")
    print("_______________\n")

    # Optional: save equity curve for inspection
    res.history.to_csv("equity_curve.csv")
    print("Saved equity curve to equity_curve.csv")

    # Optional: save a trade blotter (one row per executed buy/sell)
    res.trades.to_csv("trades.csv", index=False)
    print("Saved trade blotter to trades.csv")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())



import pandas as pd

