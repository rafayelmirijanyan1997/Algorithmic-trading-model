



# Get your free API key at: https://polygon.io/

POLYGON_API_KEY = "pXfexlW5Gp_vfwuT1aDRFYFWQjMhmyKc"



# Database file path
DATABASE_PATH = "stock_data.db"



# List of stock tickers to track:
STOCK_TICKERS = [
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'GOOGL',  # Google
    'AMZN',   # Amazon
    'TSLA',   # Tesla
    'META',   # Meta (Facebook)
    'NVDA',   # NVIDIA
    'NFLX',   # Netflix
]

# Alternative portfolio options:
# Blue chip stocks:
# STOCK_TICKERS = ['AAPL', 'MSFT', 'JNJ', 'JPM', 'V', 'PG', 'UNH', 'HD']

# High volatility (for more trading signals):
# STOCK_TICKERS = ['TSLA', 'GME', 'AMC', 'PLTR', 'RIVN', 'LCID']




HISTORICAL_DAYS = 365  # 1 year



TIMESPAN = 'day'



# Initial investment amount
INITIAL_CAPITAL = 10000  


#TRANSACTION_FEE = 0.0  # No transaction fees


MIN_CASH_RESERVE = 5000  # $5,000



# Moving Average periods
SHORT_MA_PERIOD = 20   
LONG_MA_PERIOD = 50    

# RSI parameters
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Bollinger Bands
BB_PERIOD = 20
BB_STD_DEV = 2
