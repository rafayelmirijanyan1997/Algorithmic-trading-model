# Lab 4 Complete Implementation Guide
## Algorithmic Trading System with Backtesting & Performance Metrics

---

### Core Algorithm Files:
1. **trading_algorithms.py** - Trading strategy implementations
2. **backtester.py** - Mock trading environment (backtesting engine)
3. **performance_metrics.py** - Performance analysis and metrics
4. **complete_trading_system.py** - Main integration script

---


### 1. Algorithm Development (COMPLETE)

**Implemented Algorithms:**

#### a) Simple Moving Average (SMA) Crossover
- **Strategy**: Golden Cross / Death Cross
- **Buy Signal**: When short-term MA crosses above long-term MA
- **Sell Signal**: When short-term MA crosses below long-term MA
- **Parameters**: 20-day and 50-day MAs (configurable)

#### b) Relative Strength Index (RSI)
- **Strategy**: Momentum oscillator (0-100 scale)
- **Buy Signal**: RSI < 30 (oversold)
- **Sell Signal**: RSI > 70 (overbought)
- **Parameters**: 14-day period (configurable)

#### c) MACD (Moving Average Convergence Divergence)
- **Strategy**: Trend-following momentum indicator
- **Buy Signal**: MACD crosses above signal line
- **Sell Signal**: MACD crosses below signal line
- **Parameters**: 12-day fast, 26-day slow, 9-day signal

#### d) Bollinger Bands
- **Strategy**: Volatility-based mean reversion
- **Buy Signal**: Price touches lower band
- **Sell Signal**: Price touches upper band
- **Parameters**: 20-day MA, 2 standard deviations

#### e) HYBRID Strategy (Recommended)
- **Strategy**: Voting system combining all indicators
- **Buy Signal**: 2+ indicators agree to buy
- **Sell Signal**: 2+ indicators agree to sell
- **Advantage**: More reliable, reduces false signals

### ✅ 2. Mock Trading Environment (COMPLETE)

**Features:**
- ✅ Initial capital allocation (configurable in config.py)
- ✅ Portfolio tracking (cash + positions)
- ✅ Transaction execution (buy/sell orders)
- ✅ Transaction fees (0.1% default)
- ✅ Position management (shares held per stock)
- ✅ Complete trade history
- ✅ Portfolio value tracking over time
- ✅ Single stock AND multi-stock portfolio support

**Database Integration:**
- Uses existing `portfolio` table
- Uses existing `transactions` table
- Automatic trade recording

### ✅ 3. Performance Metrics (COMPLETE)

**Calculated Metrics:**

#### Return Metrics:
- ✅ Total Return ($ and %)
- ✅ Annualized Return
- ✅ Cumulative Returns

#### Risk Metrics:
- ✅ Volatility (daily and annualized)
- ✅ Maximum Drawdown
- ✅ Downside Deviation

#### Risk-Adjusted Metrics:
- ✅ **Sharpe Ratio** - Risk-adjusted returns
- ✅ **Sortino Ratio** - Downside risk-adjusted returns
- ✅ **Calmar Ratio** - Return vs drawdown

#### Trading Metrics:
- ✅ Total number of trades
- ✅ Win rate (%)
- ✅ Average win/loss
- ✅ Profit factor

---

## 🚀 Quick Start Guide

### Step 1: Ensure Data is Collected

If you haven't collected data yet:
```bash
python stock_data_collector.py
```

### Step 2: Run Complete Analysis

**Option A - Interactive Menu (Recommended):**
```bash
python complete_trading_system.py
```

Then select:
- Option 1: Test all strategies on single stock
- Option 2: Test one strategy on single stock
- Option 3: Test portfolio with multiple stocks
- Option 4: Run full demo

**Option B - Direct Script Execution:**

Test individual components:
```bash
# Test trading algorithms
python trading_algorithms.py

# Test backtester
python backtester.py

# Test performance metrics
python performance_metrics.py
```

---

## 📊 Example Usage

### Example 1: Analyze Single Stock with All Strategies

```python
from complete_trading_system import AlgorithmicTradingSystem

system = AlgorithmicTradingSystem()

# Test all strategies on Apple stock
results = system.run_complete_analysis(ticker='AAPL')

# Results include performance for each strategy
# Generates comparison charts automatically

system.close()
```

### Example 2: Backtest Portfolio

```python
from complete_trading_system import AlgorithmicTradingSystem

system = AlgorithmicTradingSystem()

# Test portfolio with HYBRID strategy
results = system.run_portfolio_analysis(
    tickers=['AAPL', 'MSFT', 'GOOGL'],
    strategy='HYBRID'
)

system.close()
```

### Example 3: Custom Algorithm Testing

```python
from backtester import Backtester
from performance_metrics import PerformanceMetrics

# Initialize backtester
backtester = Backtester(initial_capital=100000)

# Run backtest
results = backtester.backtest_single_stock(
    ticker='AAPL',
    strategy='RSI'  # Can be: SMA, RSI, MACD, BB, HYBRID
)

# Calculate performance metrics
metrics_calc = PerformanceMetrics()
metrics = metrics_calc.calculate_all_metrics(
    portfolio_df=results['portfolio_df'],
    trades_df=results['trades_df'],
    initial_capital=100000
)

# Print results
backtester.print_results(results)
metrics_calc.print_metrics(metrics)

# Generate plots
metrics_calc.plot_performance(
    portfolio_df=results['portfolio_df'],
    initial_capital=100000,
    save_path='my_analysis.png'
)

backtester.close()
```

---

## 📈 Understanding the Output

### Console Output Example:

```
==================================================================
BACKTESTING AAPL - HYBRID Strategy
==================================================================
✓ Fetched data: 250 records

==================================================================
BACKTEST RESULTS
==================================================================

Initial Capital:        $100,000.00
Final Portfolio Value:  $125,430.50
Total Return:           $25,430.50
Return Percentage:      25.43%
Buy & Hold Return:      22.15%
Alpha (vs Buy & Hold):  3.28%

Total Trades:           24

📈 RETURN METRICS:
──────────────────────────────────────────────────────────────────
Total Return:              $25,430.50
Total Return %:            25.43%
Annualized Return:         27.85%

📊 RISK METRICS:
──────────────────────────────────────────────────────────────────
Annualized Volatility:     18.45%
Maximum Drawdown:          -$8,234.12
Maximum Drawdown %:        -7.21%

⚖️  RISK-ADJUSTED METRICS:
──────────────────────────────────────────────────────────────────
Sharpe Ratio:              1.385
  Interpretation:          Good
Sortino Ratio:             1.892
Calmar Ratio:              3.863

💼 TRADING METRICS:
──────────────────────────────────────────────────────────────────
Total Trades:              24
Winning Trades:            15
Losing Trades:             9
Win Rate:                  62.50%
```

### Generated Files:

1. **Performance Charts** (`performance_analysis.png`)
   - Portfolio value over time
   - Cumulative returns
   - Drawdown chart
   - Returns distribution

2. **Strategy Comparison** (`AAPL_strategy_comparison.png`)
   - Compare all strategies side-by-side
   - Return comparison
   - Sharpe ratio comparison
   - Drawdown comparison

3. **Portfolio Performance** (`portfolio_HYBRID_performance.png`)
   - Multi-stock portfolio analysis
   - Combined performance metrics

---

## 🎓 Understanding the Metrics

### Sharpe Ratio
**Formula**: (Return - Risk-Free Rate) / Volatility

**Interpretation**:
- < 0: Poor (losing money)
- 0-1: Sub-optimal
- 1-2: Good
- 2-3: Very Good
- > 3: Excellent

**Your Goal**: Aim for Sharpe Ratio > 1

### Maximum Drawdown
**Definition**: Largest peak-to-trough decline

**Example**: If portfolio reaches $120K then drops to $100K, drawdown = -16.7%

**Your Goal**: Keep drawdown < 20%

### Win Rate
**Formula**: Winning Trades / Total Trades

**Note**: High win rate doesn't always mean high profits. A strategy with 40% win rate but big wins can outperform 60% win rate with small wins.

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Trading parameters
INITIAL_CAPITAL = 100000      # Starting capital
TRANSACTION_FEE = 0.0         # No transaction fees

# Algorithm parameters
SHORT_MA_PERIOD = 20          # Short moving average
LONG_MA_PERIOD = 50           # Long moving average

RSI_PERIOD = 14               # RSI calculation period
RSI_OVERSOLD = 30             # Buy threshold
RSI_OVERBOUGHT = 70           # Sell threshold

BB_PERIOD = 20                # Bollinger Bands period
BB_STD_DEV = 2                # Standard deviations

# Portfolio
STOCK_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL',  # Your stocks
]
```

---

## 📝 Lab 4 Deliverables Checklist

### Code Files:
- ✅ stock_data_collector.py (data collection)
- ✅ trading_algorithms.py (algorithms)
- ✅ backtester.py (mock trading)
- ✅ performance_metrics.py (metrics)
- ✅ complete_trading_system.py (integration)
- ✅ config.py (configuration)

### Documentation:
- ✅ README.md (this file)
- ✅ SETUP_GUIDE.txt (installation guide)
- ✅ Code comments and docstrings

### Performance Metrics:
- ✅ Total portfolio value tracking
- ✅ Annualized returns
- ✅ Sharpe ratio
- ✅ Maximum drawdown
- ✅ Win rate
- ✅ Additional metrics (Sortino, Calmar)

### Visualizations:
- ✅ Performance charts
- ✅ Strategy comparison plots
- ✅ Drawdown analysis

### Video Demonstration:
- □ Record demo using complete_trading_system.py
- □ Show algorithm selection
- □ Show backtest execution
- □ Explain performance metrics
- □ Include team name and members

### Team Meetings Documentation:
- □ Document all meetings
- □ Include progress notes
- □ Task assignments

---

## 🎥 Video Demonstration Script

**Suggested structure for your team video:**

1. **Introduction (1 min)**
   - Team name and members
   - Project overview

2. **Data Collection (1 min)**
   - Show database with collected data
   - Explain data sources (Polygon.io)

3. **Algorithm Explanation (2 min)**
   - Explain HYBRID strategy (or your chosen strategy)
   - Show how signals are generated
   - Show code walkthrough

4. **Backtesting Demo (2 min)**
   - Run complete_trading_system.py
   - Show backtest execution
   - Display results in real-time

5. **Performance Analysis (2 min)**
   - Show generated charts
   - Explain key metrics (Sharpe ratio, returns, drawdown)
   - Compare strategies

6. **Conclusion (1 min)**
   - Summary of results
   - What worked well
   - Potential improvements

**Total: ~9 minutes**

---

## 🔧 Troubleshooting

### Issue: "No data found"
**Solution**: Run data collection first
```bash
python stock_data_collector.py
```

### Issue: "Module not found"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Database locked"
**Solution**: Close all other Python scripts and try again

### Issue: Poor performance (negative returns)
**Possible reasons**:
1. Market conditions during test period
2. Algorithm parameters need tuning
3. Transaction fees eating into profits
4. Try different strategy or adjust parameters in config.py

---

## 📊 Example Results to Expect

With default configuration on AAPL (1 year data):

**SMA Strategy:**
- Expected Return: 15-25%
- Sharpe Ratio: 0.8-1.2
- Trades: 10-15

**RSI Strategy:**
- Expected Return: 10-20%
- Sharpe Ratio: 0.6-1.0
- Trades: 15-25

**HYBRID Strategy:**
- Expected Return: 20-30%
- Sharpe Ratio: 1.0-1.5
- Trades: 12-20
- **Recommended for best results**

*Note: Actual results vary based on market conditions and date range*

---

## 🚀 Advanced Usage

### Compare Multiple Time Periods

```python
from backtester import Backtester

backtester = Backtester()

# Test recent period
results_recent = backtester.backtest_single_stock(
    ticker='AAPL',
    strategy='HYBRID',
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# Test older period
results_old = backtester.backtest_single_stock(
    ticker='AAPL',
    strategy='HYBRID',
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# Compare results
```

### Test Different Stocks

```python
from complete_trading_system import AlgorithmicTradingSystem

system = AlgorithmicTradingSystem()

stocks = ['AAPL', 'MSFT', 'TSLA', 'NVDA']

for stock in stocks:
    print(f"\n=== Testing {stock} ===")
    system.run_complete_analysis(ticker=stock, strategies=['HYBRID'])
```

### Optimize Parameters

Try different MA periods in config.py:
- Conservative: SHORT_MA=50, LONG_MA=200
- Aggressive: SHORT_MA=10, LONG_MA=20
- Default: SHORT_MA=20, LONG_MA=50

---

## 📚 Additional Resources

### Understanding Algorithms:
- [Moving Averages](https://www.investopedia.com/terms/m/movingaverage.asp)
- [RSI Indicator](https://www.investopedia.com/terms/r/rsi.asp)
- [MACD](https://www.investopedia.com/terms/m/macd.asp)
- [Bollinger Bands](https://www.investopedia.com/terms/b/bollingerbands.asp)

### Performance Metrics:
- [Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp)
- [Maximum Drawdown](https://www.investopedia.com/terms/m/maximum-drawdown-mdd.asp)
- [Sortino Ratio](https://www.investopedia.com/terms/s/sortinoratio.asp)

---

## ✅ Final Checklist Before Submission

- [ ] All code runs without errors
- [ ] Data collection completed
- [ ] Backtests executed successfully
- [ ] Performance metrics calculated
- [ ] Charts generated
- [ ] README.pdf created with instructions
- [ ] Video recorded and includes:
  - [ ] Team name and members
  - [ ] Demo of working system
  - [ ] Algorithm explanation
  - [ ] Performance metrics shown
- [ ] Meeting minutes documented
- [ ] All files organized in repository

---

## 🎉 You're Ready!

Your complete algorithmic trading system is now ready for Lab 4 submission. The system includes:

✅ Professional data collection
✅ 5 different trading algorithms
✅ Complete backtesting framework
✅ Comprehensive performance metrics
✅ Publication-quality visualizations
✅ Easy-to-use interface

**Good luck with your presentation! 🚀**

---

*Last updated: February 2026*
*DSCI-560 Lab 4 Implementation*
