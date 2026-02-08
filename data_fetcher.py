
from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

def _to_df(aggs) -> pd.DataFrame:
    rows = []
    for a in aggs:
        rows.append({
            "date": datetime.utcfromtimestamp(a.timestamp / 1000.0),
            "open": float(a.open),
            "high": float(a.high),
            "low": float(a.low),
            "close": float(a.close),
            "volume": float(a.volume),
        })
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df = df.set_index("date").sort_index()
    return df

def fetch_polygon_ohlcv(
    ticker: str,
    start: str,
    end: str,
    api_key: str,
    timespan: str = "day",
    multiplier: int = 1,
) -> pd.DataFrame:
    try:
        from polygon import RESTClient
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "polygon-api-client is not installed. Run: pip install polygon-api-client"
        ) from e

    client = RESTClient(api_key)
    aggs = client.get_aggs(
        ticker=ticker,
        multiplier=multiplier,
        timespan=timespan,
        from_=start,
        to=end,
        limit=50000,
    )
    if not aggs:
        raise ValueError(f"No Polygon data returned for {ticker} between {start} and {end}")
    return _to_df(aggs)

def fetch_all(
    tickers: list[str],
    start: str,
    end: str,
    api_key: str,
    timespan: str = "day",
    multiplier: int = 1,
    cache_dir: str = "data_cache",
    use_cache: bool = True,
) -> dict[str, pd.DataFrame]:
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    out: dict[str, pd.DataFrame] = {}

    for t in tickers:
        cache_path = Path(cache_dir) / f"{t}_{start}_{end}_{multiplier}{timespan}.csv"
        if use_cache and cache_path.exists():
            df = pd.read_csv(cache_path, parse_dates=["date"]).set_index("date").sort_index()
            out[t] = df
            continue

        df = fetch_polygon_ohlcv(
            ticker=t,
            start=start,
            end=end,
            api_key=api_key,
            timespan=timespan,
            multiplier=multiplier,
        )
        if use_cache:
            df.reset_index().to_csv(cache_path, index=False)
        out[t] = df

    return out
