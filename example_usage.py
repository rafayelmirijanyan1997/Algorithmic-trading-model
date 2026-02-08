
from stock_data_collector import StockDataCollector
from datetime import datetime, timedelta
import pandas as pd
import config

def example_1_basic_collection():
    
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Data Collection")
    print("=" * 70)
    
    # Initialize collector with API key
    collector = StockDataCollector(api_key=config.POLYGON_API_KEY)
    
    # Fetch data for Apple stock (last 30 days)
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
    
    print("\nSample data:")
    print(df.head())
    
    collector.close()


def example_2_multiple_stocks():
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multiple Stock Collection")
    print("=" * 70)
    
    collector = StockDataCollector(api_key=config.POLYGON_API_KEY)
    
    # Use tickers from config
    tickers = config.STOCK_TICKERS[:3]  # First 3 stocks to respect API limits
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=config.HISTORICAL_DAYS)
    
    for ticker in tickers:
        print(f"\nProcessing {ticker}...")
        df = collector.fetch_historical_data(
            ticker=ticker,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        if not df.empty:
            df = collector.clean_data(df)
            collector.save_to_database(df)
    
    # Show summary
    print("\n" + "-" * 70)
    summary = collector.get_data_summary()
    print("\nData Summary:")
    print(summary)
    
    collector.close()


def example_3_query_database():
    """Example 3: Query data from the database"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Querying Database")
    print("=" * 70)
    
    collector = StockDataCollector(api_key=config.POLYGON_API_KEY)
    
    # Get all Apple data
    print("\nApple Stock Data (Last 10 days):")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    
    df = collector.get_data_from_db(
        ticker='AAPL',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    print(df[['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']])
    
    # Get latest price
    latest_price = collector.get_latest_price('AAPL')
    print(f"\nLatest AAPL price: ${latest_price:.2f}")
    
    collector.close()


def example_4_data_analysis():
    
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Basic Data Analysis")
    print("=" * 70)
    
    collector = StockDataCollector(api_key=config.POLYGON_API_KEY)
    
    # Get data for analysis
    df = collector.get_data_from_db(ticker='AAPL')
    
    if not df.empty:
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # Calculate basic statistics
        print("\nPrice Statistics:")
        print(f"Mean Close Price: ${df['close'].mean():.2f}")
        print(f"Std Deviation: ${df['close'].std():.2f}")
        print(f"Min Price: ${df['close'].min():.2f}")
        print(f"Max Price: ${df['close'].max():.2f}")
        
        # Calculate daily returns
        df['daily_return'] = df['close'].pct_change() * 100
        
        print("\nReturn Statistics:")
        print(f"Average Daily Return: {df['daily_return'].mean():.2f}%")
        print(f"Volatility (Std Dev): {df['daily_return'].std():.2f}%")
        
        # Calculate simple moving average
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        
        print("\nMoving Average (Last 5 days):")
        print(df[['close', 'SMA_20']].tail())
    else:
        print("No data available. Please run data collection first.")
    
    collector.close()


def example_5_full_pipeline():
   
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Full Data Collection Pipeline")
    print("=" * 70)
    
    print("\nThis is the recommended workflow for your team:\n")
    
    # Step 1: Initialize
    print("Step 1: Initializing database...")
    collector = StockDataCollector(
        api_key=config.POLYGON_API_KEY,
        db_path=config.DATABASE_PATH
    )
    
    # Step 2: Configure date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=config.HISTORICAL_DAYS)
    
    print(f"Step 2: Date range set: {start_date.date()} to {end_date.date()}")
    
    # Step 3: Collect data for all tickers
    print(f"Step 3: Collecting data for {len(config.STOCK_TICKERS)} stocks...")
    print(f"Tickers: {', '.join(config.STOCK_TICKERS)}\n")
    
    for i, ticker in enumerate(config.STOCK_TICKERS, 1):
        print(f"[{i}/{len(config.STOCK_TICKERS)}] Fetching {ticker}...")
        
        df = collector.fetch_historical_data(
            ticker=ticker,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            timespan=config.TIMESPAN
        )
        
        if not df.empty:
            df = collector.clean_data(df)
            collector.save_to_database(df)
            print(f"    ✓ {ticker}: {len(df)} records saved")
        else:
            print(f"    ✗ {ticker}: No data retrieved")
    
    # Step 4: Generate summary report
    print("\n" + "=" * 70)
    print("FINAL SUMMARY REPORT")
    print("=" * 70)
    
    summary = collector.get_data_summary()
    print(summary.to_string(index=False))
    
    print("\n✓ Data collection pipeline complete!")
    print(f"✓ Database saved to: {config.DATABASE_PATH}")
    print("\nNext steps:")
    print("  1. Review the data in the database")
    print("  2. Implement your trading algorithms")
    print("  3. Backtest strategies using this historical data")
    
    collector.close()


if __name__ == "__main__":
    print("=" * 70)
    print("STOCK DATA COLLECTION - EXAMPLE USAGE")
    print("DSCI-560 Lab 4")
    print("=" * 70)
    
    print("\nAvailable examples:")
    print("1. Basic data collection (single stock)")
    print("2. Multiple stock collection")
    print("3. Query database")
    print("4. Basic data analysis")
    print("5. Full pipeline (RECOMMENDED FOR YOUR TEAM)")
    
    choice = input("\nSelect example to run (1-5): ")
    
    if choice == '1':
        example_1_basic_collection()
    elif choice == '2':
        example_2_multiple_stocks()
    elif choice == '3':
        example_3_query_database()
    elif choice == '4':
        example_4_data_analysis()
    elif choice == '5':
        example_5_full_pipeline()
    else:
        print("Invalid choice. Running full pipeline...")
        example_5_full_pipeline()
