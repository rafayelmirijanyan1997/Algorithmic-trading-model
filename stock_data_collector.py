"""
Stock Data Collection and Storage System using Polygon.io
DSCI-560 Lab 4 - Data Collection Module

This script collects real-time and historical stock data using Polygon.io API,
cleans the data, and stores it in a SQLite database for algorithmic trading analysis.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from polygon import RESTClient
import time
import json

class StockDataCollector:
    """
    Handles stock data collection, cleaning, and storage using Polygon.io API
    """
    
    def __init__(self, api_key, db_path='stock_data.db'):
        """
        Initialize the Stock Data Collector
        
        Parameters:
        -----------
        api_key : str
            Your Polygon.io API key
        db_path : str
            Path to SQLite database file
        """
        self.api_key = api_key
        self.client = RESTClient(api_key)
        self.db_path = db_path
        self.conn = None
        self.setup_database()
    
    def setup_database(self):
        """Create database tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create stock_prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                vwap REAL,
                transactions INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, date)
            )
        ''')
        
        # Create portfolio table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                shares REAL DEFAULT 0,
                avg_price REAL DEFAULT 0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker)
            )
        ''')
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                shares REAL NOT NULL,
                price REAL NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                total_value REAL
            )
        ''')
        
        self.conn.commit()
        print(f"✓ Database setup complete: {self.db_path}")
    
    def fetch_historical_data(self, ticker, start_date, end_date, timespan='day'):
        """
        Fetch historical stock data from Polygon.io
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol (e.g., 'AAPL')
        start_date : str
            Start date in format 'YYYY-MM-DD'
        end_date : str
            End date in format 'YYYY-MM-DD'
        timespan : str
            Time interval ('day', 'hour', 'minute')
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with stock price data
        """
        try:
            print(f"Fetching {ticker} data from {start_date} to {end_date}...")
            
            # Fetch aggregates (bars) data
            aggs = []
            for agg in self.client.list_aggs(
                ticker=ticker,
                multiplier=1,
                timespan=timespan,
                from_=start_date,
                to=end_date,
                limit=50000
            ):
                aggs.append(agg)
            
            if not aggs:
                print(f"⚠ No data found for {ticker}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for agg in aggs:
                data.append({
                    'ticker': ticker,
                    'date': datetime.fromtimestamp(agg.timestamp / 1000).strftime('%Y-%m-%d'),
                    'open': agg.open,
                    'high': agg.high,
                    'low': agg.low,
                    'close': agg.close,
                    'volume': agg.volume,
                    'vwap': agg.vwap if hasattr(agg, 'vwap') else None,
                    'transactions': agg.transactions if hasattr(agg, 'transactions') else None
                })
            
            df = pd.DataFrame(data)
            print(f"✓ Fetched {len(df)} records for {ticker}")
            
            # Respect API rate limits (5 calls/minute for free tier)
            time.sleep(12)  # Wait 12 seconds between calls
            
            return df
            
        except Exception as e:
            print(f"✗ Error fetching data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def clean_data(self, df):
        """
        Clean and preprocess stock data
        
        Parameters:
        -----------
        df : pd.DataFrame
            Raw stock data
        
        Returns:
        --------
        pd.DataFrame
            Cleaned stock data
        """
        if df.empty:
            return df
        
        print("Cleaning data...")
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['ticker', 'date'])
        
        # Sort by date
        df = df.sort_values('date')
        
        # Handle missing values
        # For price data, forward fill then backward fill
        price_columns = ['open', 'high', 'low', 'close', 'vwap']
        for col in price_columns:
            if col in df.columns:
                df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
        
        # Volume should not be negative
        if 'volume' in df.columns:
            df['volume'] = df['volume'].clip(lower=0)
        
        # Remove rows with all NaN price values
        df = df.dropna(subset=['close'])
        
        # Validate price data (close should be between high and low)
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            # Fix anomalies
            df.loc[df['close'] > df['high'], 'high'] = df['close']
            df.loc[df['close'] < df['low'], 'low'] = df['close']
            df.loc[df['open'] > df['high'], 'high'] = df['open']
            df.loc[df['open'] < df['low'], 'low'] = df['open']
        
        # Reset index
        df = df.reset_index(drop=True)
        
        print(f"✓ Data cleaned: {len(df)} valid records")
        return df
    
    def save_to_database(self, df):
        """
        Save stock data to SQLite database
        
        Parameters:
        -----------
        df : pd.DataFrame
            Cleaned stock data
        """
        if df.empty:
            print("⚠ No data to save")
            return
        
        try:
            # Insert or replace data
            df.to_sql('stock_prices', self.conn, if_exists='append', index=False)
            self.conn.commit()
            print(f"✓ Saved {len(df)} records to database")
            
        except sqlite3.IntegrityError:
            # Handle duplicates by updating existing records
            print("Some records already exist, updating...")
            for _, row in df.iterrows():
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_prices 
                    (ticker, date, open, high, low, close, volume, vwap, transactions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['ticker'], row['date'], row['open'], row['high'], 
                    row['low'], row['close'], row['volume'], 
                    row.get('vwap'), row.get('transactions')
                ))
            self.conn.commit()
            print(f"✓ Updated {len(df)} records in database")
    
    def get_data_from_db(self, ticker=None, start_date=None, end_date=None):
        """
        Retrieve stock data from database
        
        Parameters:
        -----------
        ticker : str, optional
            Stock ticker to filter
        start_date : str, optional
            Start date filter
        end_date : str, optional
            End date filter
        
        Returns:
        --------
        pd.DataFrame
            Stock price data
        """
        query = "SELECT * FROM stock_prices WHERE 1=1"
        params = []
        
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY ticker, date"
        
        df = pd.read_sql_query(query, self.conn, params=params)
        return df
    
    def get_latest_price(self, ticker):
        """Get the most recent price for a ticker"""
        df = self.get_data_from_db(ticker=ticker)
        if df.empty:
            return None
        return df.iloc[-1]['close']
    
    def get_data_summary(self):
        """Get summary statistics of stored data"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                ticker,
                COUNT(*) as record_count,
                MIN(date) as start_date,
                MAX(date) as end_date,
                MIN(close) as min_price,
                MAX(close) as max_price,
                AVG(close) as avg_price
            FROM stock_prices
            GROUP BY ticker
        ''')
        
        results = cursor.fetchall()
        df = pd.DataFrame(results, columns=[
            'ticker', 'record_count', 'start_date', 'end_date', 
            'min_price', 'max_price', 'avg_price'
        ])
        return df
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")


def main():
    """
    Main function to demonstrate usage
    """
    print("=" * 60)
    print("Stock Data Collection System - Polygon.io")
    print("DSCI-560 Lab 4")
    print("=" * 60)
    
    # Configuration
    API_KEY = "pXfexlW5Gp_vfwuT1aDRFYFWQjMhmyKc"  # Replace with your API key
    
    # List of stocks to track (popular tech stocks)
    TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    # Date range (last 6 months for testing)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print(f"\nCollecting data from {start_date_str} to {end_date_str}")
    print(f"Tickers: {', '.join(TICKERS)}\n")
    
    # Initialize collector
    collector = StockDataCollector(api_key=API_KEY)
    
    # Collect data for each ticker
    for ticker in TICKERS:
        print(f"\n{'=' * 60}")
        print(f"Processing: {ticker}")
        print('=' * 60)
        
        # Fetch data
        df = collector.fetch_historical_data(
            ticker=ticker,
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        # Clean data
        if not df.empty:
            df = collector.clean_data(df)
            
            # Save to database
            collector.save_to_database(df)
        
        print()
    
    # Display summary
    print("\n" + "=" * 60)
    print("DATA COLLECTION SUMMARY")
    print("=" * 60)
    summary = collector.get_data_summary()
    print(summary.to_string(index=False))
    
    # Close connection
    collector.close()
    
    print("\n✓ Data collection complete!")
    print(f"✓ Database saved to: {collector.db_path}")


if __name__ == "__main__":
    main()
