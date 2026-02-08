# One-File Algorithmic Trading Backtester (Polygon API)

This project:
- Fetches historical daily prices from **Polygon API**
- Runs a **long-only, equal-weight** strategy (daily rebalance)
- Prints the **final balance** starting from $10,000
- Optionally saves `equity_curve.csv`

---

## Requirements

```bash
pip install -r requirements.txt
```

---

## Polygon API Key

Open `config.py` and set your API key:

```python
POLYGON_API_KEY = "YOUR_POLYGON_KEY_HERE"
```

---

## Run

From the project directory:

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
