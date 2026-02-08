# Stock Data Collection System using Polygon.io
## DSCI-560 Lab 4 - Data Collection Module

### Overview
This system collects, cleans, and stores real-time stock market data using the Polygon.io API. It provides a foundation for implementing algorithmic trading strategies as required in Lab 4.

---

## Quick Start Guide

### Step 1: Get Your Free Polygon.io API Key

1. Go to [https://polygon.io/](https://polygon.io/)
2. Click "Get Free API Key"
3. Sign up with your email
4. Verify your email
5. Copy your API key from the dashboard

**Free Tier Limits:**
- 5 API calls per minute

### Step 2: Install Required Packages

```bash
pip install -r requirements.txt
```

Required packages:
- `polygon-api-client`: For accessing Polygon.io API
- `pandas`: For data manipulation
- `numpy`: For numerical operations
- `matplotlib`, `seaborn`: For visualization
- `ta`, `pandas-ta`: For technical analysis indicators

### Step 3: Configure Your API Key

Open `config.py` and replace:
```python
POLYGON_API_KEY = "YOUR_API_KEY_HERE"
```

With your actual API key:
```python
POLYGON_API_KEY = "your_actual_api_key_12345"
```

### Step 4: Customize Your Stock Portfolio

In `config.py`, modify the stock tickers:
```python
STOCK_TICKERS = [
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'GOOGL',  # Google
    'AMZN',   # Amazon
    'TSLA',   # Tesla
]
```

### Step 5: Run Data Collection

**Option A: Run the main collector**
```bash
python stock_data_collector.py
```

**Option B: Use the example script (Recommended)**
```bash
python example_usage.py
```
Then select option 5 for the full pipeline.

---

## Structure

```
lab4-stock-trading/
│
├── stock_data_collector.py   # Main data collection class
├── config.py                  # Configuration settings
├── example_usage.py           # Usage examples and demos
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
└── stock_data.db             # SQLite database (created automatically)
```

---

## Database Schema

The system creates 3 tables:

### 1. `stock_prices` Table
Stores historical price data:
- `ticker`: Stock symbol (e.g., 'AAPL')
- `date`: Trading date
- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price
- `volume`: Trading volume
- `vwap`: Volume-weighted average price
- `transactions`: Number of transactions

### 2. `portfolio` Table
Tracks your current holdings:
- `ticker`: Stock symbol
- `shares`: Number of shares owned
- `avg_price`: Average purchase price
- `last_updated`: Last update timestamp

### 3. `transactions` Table
Records all buy/sell operations:
- `ticker`: Stock symbol
- `transaction_type`: 'BUY' or 'SELL'
- `shares`: Number of shares
- `price`: Transaction price
- `timestamp`: When the transaction occurred
- `total_value`: Total transaction value

---

## Usage Examples

### Example 1: Basic Data Collection

```python
from stock_data_collector import StockDataCollector
from datetime import datetime, timedelta

# Initialize
collector = StockDataCollector(api_key="YOUR_API_KEY")

# Fetch Apple stock data for last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

df = collector.fetch_historical_data(
    ticker='AAPL',
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d')
)

# Clean and save
df = collector.clean_data(df)
collector.save_to_database(df)

collector.close()
```

### Example 2: Query Database

```python
from stock_data_collector import StockDataCollector

collector = StockDataCollector(api_key="YOUR_API_KEY")

# Get all Apple data from last 7 days
df = collector.get_data_from_db(
    ticker='AAPL',
    start_date='2025-01-01',
    end_date='2025-02-07'
)

print(df.head())

# Get latest price
latest_price = collector.get_latest_price('AAPL')
print(f"Latest price: ${latest_price}")

collector.close()
```

### Example 3: Data Analysis

```python
import pandas as pd
from stock_data_collector import StockDataCollector

collector = StockDataCollector(api_key="YOUR_API_KEY")

# Get data
df = collector.get_data_from_db(ticker='AAPL')
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')

# Calculate returns
df['daily_return'] = df['close'].pct_change() * 100

# Calculate moving average
df['SMA_20'] = df['close'].rolling(window=20).mean()

print(df[['close', 'daily_return', 'SMA_20']].tail())

collector.close()
```

---

## Data Cleaning Features

The system automatically:

1. **Removes duplicates**: Ensures no duplicate records for same ticker/date
2. **Sorts chronologically**: Orders data by date
3. **Handles missing values**: 
   - Forward fill then backward fill for price data
   - Ensures volume is non-negative
4. **Validates price data**: 
   - Ensures close price is between high and low
   - Fixes anomalies automatically
5. **Removes invalid records**: Drops rows with no close price

---

##  Next Steps

After collecting your data, you'll need to:

### 1. Algorithm Development
- Implement Moving Average Crossover strategy
- Calculate RSI (Relative Strength Index)
- Develop buy/sell signals

### 2. Mock Trading Environment
- Use the `portfolio` and `transactions` tables
- Implement paper trading logic
- Track portfolio performance

### 3. Performance Metrics
Calculate:
- Total portfolio value
- Annualized returns
- Sharpe ratio
- Maximum drawdown

---

## Troubleshooting

### Problem: "Rate limit exceeded"
**Solution**: The free tier allows 5 calls/minute. The script automatically waits 12 seconds between calls. If you still see this error, increase the wait time in `stock_data_collector.py`:
```python
time.sleep(15)  # Increase from 12 to 15 seconds
```

### Problem: "No data found for ticker"
**Solution**: 
- Check if ticker symbol is correct (use uppercase: 'AAPL' not 'aapl')
- Verify the date range is not too far in the past
- Ensure you're using valid trading days (not weekends/holidays)

### Problem: "Invalid API key"
**Solution**:
- Verify you copied the API key correctly
- Check for extra spaces in `config.py`
- Ensure you're using the API key from polygon.io dashboard

### Problem: "Database locked"
**Solution**:
- Close any other programs accessing the database
- Make sure you called `collector.close()` after previous runs
- Delete `stock_data.db` and restart

---

## References

### Technical Analysis Resources:
1. [Investopedia - Moving Averages](https://www.investopedia.com/terms/m/movingaverage.asp)
2. [Investopedia - RSI](https://www.investopedia.com/terms/r/rsi.asp)
3. [Polygon.io Documentation](https://polygon.io/docs/stocks)

### Python Libraries Documentation:
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [TA-Lib](https://github.com/mrjbq7/ta-lib)
- [Polygon Python Client](https://github.com/polygon-io/client-python)

---



---

##  Performance Tips

1. **Batch Processing**: Collect data for all stocks in one session
2. **Caching**: The database serves as a cache - don't re-download existing data
3. **Incremental Updates**: Only fetch new data since last collection
4. **Database Indexing**: The database has indexes on (ticker, date) for fast queries

---

## Example Output

```
==================================================================
Stock Data Collection System - Polygon.io
DSCI-560 Lab 4
==================================================================

Collecting data from 2024-08-07 to 2025-02-07
Tickers: AAPL, MSFT, GOOGL, AMZN, TSLA

==================================================================
Processing: AAPL
==================================================================
Fetching AAPL data from 2024-08-07 to 2025-02-07...
✓ Fetched 184 records for AAPL
Cleaning data...
✓ Data cleaned: 184 valid records
✓ Saved 184 records to database

==================================================================
DATA COLLECTION SUMMARY
==================================================================
 ticker  record_count  start_date    end_date  min_price  max_price  avg_price
   AAPL           184  2024-08-07  2025-02-06     210.45     245.67     228.94
   MSFT           184  2024-08-07  2025-02-06     405.12     445.89     425.33
  GOOGL           184  2024-08-07  2025-02-06     155.23     178.45     166.78
   AMZN           184  2024-08-07  2025-02-06     165.34     198.67     182.15
   TSLA           184  2024-08-07  2025-02-06     210.55     289.34     245.67

✓ Data collection complete!
✓ Database saved to: stock_data.db
```

---

## Support

If you encounter issues:
1. Check the troubleshooting section
2. Review example_usage.py for working examples
3. Consult Polygon.io documentation
4. Ask your team members
5. Contact the instructor during office hours

---

##  License

This code is provided for educational purposes for DSCI-560 Lab 4.

---


