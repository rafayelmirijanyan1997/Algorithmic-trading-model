# One-File Algorithmic Trading Backtester (Polygon API, No DB, No .env, No Fees)

This project is a **single Python file** that:
- Fetches historical daily prices from **Polygon API**
- Runs a **long-only, equal-weight** strategy (daily rebalance)
- Prints the **final balance** starting from **$10,000**
- Saves an optional `equity_curve.csv`

✅ No database  
✅ No `.env` file  
✅ No environment variables  
✅ No fees / slippage  
✅ No extra modules/files needed (besides dependencies)

---

## 1) Requirements

Install dependencies:

```bash
pip install polygon-api-client pandas numpy
```

---

## 2) Get a Polygon API key

Create an account and get your key from Polygon.

---

## 3) Put your API key inside the script (NO .env)

Open your Python file (example name: `one_file_backtest.py`) and edit this line:

```python
POLYGON_API_KEY = "PUT_YOUR_POLYGON_KEY_HERE"
```

Replace with your real key:

```python
POLYGON_API_KEY = "YOUR_REAL_KEY"
```

⚠️ **Important**  
If your GitHub repo is public, **do NOT commit your real API key**.  
Use a placeholder before pushing.

---

## 4) Run

From the same folder as your script:

```bash
python one_file_backtest.py
```

---

## 5) Output

You will see something like:

```
===== BACKTEST RESULT =====
Initial Capital: $10,000.00
Final Balance:   $XX,XXX.XX
Net Profit:      $X,XXX.XX
Total Return:    XX.XX%
===========================
```

The **Final Balance** is the actual end portfolio value.

---

## 6) What the backtest is doing

- **Data:** daily OHLCV from Polygon
- **Price used:** daily **close**
- **Positioning:** long-only (either hold a ticker or be in cash)
- **Allocation:** equal weight across tickers that have a bullish signal
- **Rebalancing:** every day
- **Costs:** none (no fees, no slippage)

---

## 7) Optional cache + equity curve files

If caching is enabled in the script:
- A folder like `data_cache/` may be created to store downloaded CSVs
- The script saves `equity_curve.csv` with portfolio value by date

You can delete these anytime — it won’t break the code.

---

## Troubleshooting

### “ERROR: Missing POLYGON_API_KEY”
You didn’t paste your key into the script.

### “No Polygon data returned…”
Your ticker/date range may be invalid, or your API plan may limit the range.

### “ModuleNotFoundError: polygon”
Install dependencies again:
```bash
pip install polygon-api-client
```

---

## License
Educational / personal use.
