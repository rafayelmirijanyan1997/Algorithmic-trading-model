# Algorithmic Trading Backtester (Polygon API)

A lightweight Python backtester that:
- Fetches **daily** historical prices from the **Polygon.io API**
- Runs a simple **long-only, equal-weight** strategy (daily rebalance)
- Prints the **final balance** (starting from $10,000 by default)
- Optionally saves an `equity_curve.csv`

---

## Quick start

### 1) Create a virtual environment (recommended)
```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate  # Windows PowerShell
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Set your Polygon API key

**Option A (current code path):** edit `config.py`
```python
POLYGON_API_KEY = "YOUR_POLYGON_KEY_HERE"
```

**Option B (recommended):** use an environment variable (keeps secrets out of git)
```bash
export POLYGON_API_KEY="YOUR_POLYGON_KEY_HERE"   # macOS/Linux
setx POLYGON_API_KEY "YOUR_POLYGON_KEY_HERE"     # Windows (new terminal needed)
```

> Note: If you choose Option B, update `config.py` to read from env:
> ```python
> import os
> POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "PUT_YOUR_POLYGON_KEY_HERE")
> ```
> **Do not commit real API keys** to a public repo.

### 4) Run
```bash
python main.py
```

---

## Output

Example:
```
===== BACKTEST RESULT =====
Initial Capital: $10,000.00
Final Balance:   $XX,XXX.XX
Net Profit:      $X,XXX.XX
Total Return:    XX.XX%
===========================
```

The Final Balance is the end portfolio value.

If enabled, an `equity_curve.csv` file is written in the repo folder.

---

## Notes
- Data source: Polygon daily bars (OHLCV)
- Prices used: daily **close**
- Strategy: long-only, equal weight, daily rebalance (see `trading_algorithms.py`)
- This is for learning/testing—**not** investment advice.
