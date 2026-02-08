"""
Data Visualization and Analysis Script
DSCI-560 Lab 4

This script provides visualization tools to analyze your collected stock data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from stock_data_collector import StockDataCollector
import config
import numpy as np
from datetime import datetime

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


class StockDataVisualizer:
    """Visualize stock data for analysis"""
    
    def __init__(self, api_key, db_path='stock_data.db'):
        self.collector = StockDataCollector(api_key, db_path)
    
    def plot_price_history(self, ticker, save_path=None):
        """Plot price history with volume"""
        df = self.collector.get_data_from_db(ticker=ticker)
        
        if df.empty:
            print(f"No data found for {ticker}")
            return
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # Create subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                        gridspec_kw={'height_ratios': [3, 1]})
        
        # Price plot
        ax1.plot(df.index, df['close'], label='Close Price', linewidth=2)
        ax1.fill_between(df.index, df['low'], df['high'], 
                         alpha=0.3, label='High-Low Range')
        ax1.set_title(f'{ticker} Price History', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # Volume plot
        ax2.bar(df.index, df['volume'], alpha=0.7, color='steelblue')
        ax2.set_title('Trading Volume', fontsize=14)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Volume', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
    
    def plot_moving_averages(self, ticker, short_window=20, long_window=50, save_path=None):
        """Plot price with moving averages"""
        df = self.collector.get_data_from_db(ticker=ticker)
        
        if df.empty:
            print(f"No data found for {ticker}")
            return
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # Calculate moving averages
        df[f'SMA_{short_window}'] = df['close'].rolling(window=short_window).mean()
        df[f'SMA_{long_window}'] = df['close'].rolling(window=long_window).mean()
        
        # Plot
        plt.figure(figsize=(14, 8))
        plt.plot(df.index, df['close'], label='Close Price', linewidth=2, alpha=0.7)
        plt.plot(df.index, df[f'SMA_{short_window}'], 
                label=f'{short_window}-Day SMA', linewidth=2, linestyle='--')
        plt.plot(df.index, df[f'SMA_{long_window}'], 
                label=f'{long_window}-Day SMA', linewidth=2, linestyle='--')
        
        # Identify crossovers (potential buy/sell signals)
        df['signal'] = 0
        df.loc[df[f'SMA_{short_window}'] > df[f'SMA_{long_window}'], 'signal'] = 1
        df['position'] = df['signal'].diff()
        
        # Plot buy signals
        plt.plot(df[df['position'] == 1].index, 
                df[f'SMA_{short_window}'][df['position'] == 1],
                '^', markersize=12, color='green', label='Buy Signal')
        
        # Plot sell signals
        plt.plot(df[df['position'] == -1].index,
                df[f'SMA_{short_window}'][df['position'] == -1],
                'v', markersize=12, color='red', label='Sell Signal')
        
        plt.title(f'{ticker} - Moving Average Crossover Strategy', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price ($)', fontsize=12)
        plt.legend(loc='best')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
    
    def plot_returns_distribution(self, ticker, save_path=None):
        """Plot distribution of daily returns"""
        df = self.collector.get_data_from_db(ticker=ticker)
        
        if df.empty:
            print(f"No data found for {ticker}")
            return
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # Calculate daily returns
        df['daily_return'] = df['close'].pct_change() * 100
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Histogram
        ax1.hist(df['daily_return'].dropna(), bins=50, 
                alpha=0.7, color='steelblue', edgecolor='black')
        ax1.axvline(df['daily_return'].mean(), color='red', 
                   linestyle='--', linewidth=2, label='Mean')
        ax1.set_title(f'{ticker} Daily Returns Distribution', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('Daily Return (%)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Box plot
        ax2.boxplot(df['daily_return'].dropna(), vert=True)
        ax2.set_title(f'{ticker} Returns Box Plot', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Daily Return (%)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
    
    def plot_portfolio_comparison(self, tickers=None, save_path=None):
        """Compare multiple stocks"""
        if tickers is None:
            tickers = config.STOCK_TICKERS[:5]  # First 5 stocks
        
        plt.figure(figsize=(14, 8))
        
        for ticker in tickers:
            df = self.collector.get_data_from_db(ticker=ticker)
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                
                # Normalize to 100 for comparison
                df['normalized'] = (df['close'] / df['close'].iloc[0]) * 100
                
                plt.plot(df.index, df['normalized'], label=ticker, linewidth=2)
        
        plt.title('Portfolio Stocks Performance (Normalized to 100)', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Normalized Price', fontsize=12)
        plt.legend(loc='best')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
    
    def plot_correlation_matrix(self, tickers=None, save_path=None):
        """Plot correlation matrix of stock returns"""
        if tickers is None:
            tickers = config.STOCK_TICKERS[:5]
        
        # Collect close prices for all tickers
        data = {}
        for ticker in tickers:
            df = self.collector.get_data_from_db(ticker=ticker)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                data[ticker] = df['close']
        
        # Create DataFrame
        prices_df = pd.DataFrame(data)
        
        # Calculate returns
        returns_df = prices_df.pct_change().dropna()
        
        # Calculate correlation
        correlation = returns_df.corr()
        
        # Plot
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation, annot=True, cmap='coolwarm', 
                   center=0, vmin=-1, vmax=1, square=True,
                   linewidths=1, cbar_kws={'label': 'Correlation'})
        plt.title('Stock Returns Correlation Matrix', 
                 fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
    
    def generate_summary_statistics(self, ticker):
        """Generate comprehensive statistics for a stock"""
        df = self.collector.get_data_from_db(ticker=ticker)
        
        if df.empty:
            print(f"No data found for {ticker}")
            return None
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # Calculate returns
        df['daily_return'] = df['close'].pct_change()
        
        # Calculate statistics
        stats = {
            'Ticker': ticker,
            'Start Date': df.index.min().strftime('%Y-%m-%d'),
            'End Date': df.index.max().strftime('%Y-%m-%d'),
            'Trading Days': len(df),
            'Current Price': f"${df['close'].iloc[-1]:.2f}",
            'Min Price': f"${df['close'].min():.2f}",
            'Max Price': f"${df['close'].max():.2f}",
            'Avg Price': f"${df['close'].mean():.2f}",
            'Price Std Dev': f"${df['close'].std():.2f}",
            'Total Return': f"{((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100):.2f}%",
            'Avg Daily Return': f"{(df['daily_return'].mean() * 100):.4f}%",
            'Daily Volatility': f"{(df['daily_return'].std() * 100):.4f}%",
            'Annualized Return': f"{(df['daily_return'].mean() * 252 * 100):.2f}%",
            'Annualized Volatility': f"{(df['daily_return'].std() * np.sqrt(252) * 100):.2f}%",
            'Sharpe Ratio (Rf=0)': f"{(df['daily_return'].mean() / df['daily_return'].std() * np.sqrt(252)):.2f}",
        }
        
        return stats
    
    def close(self):
        """Close database connection"""
        self.collector.close()


def main():
    """Main function to generate all visualizations"""
    print("=" * 70)
    print("STOCK DATA VISUALIZATION")
    print("DSCI-560 Lab 4")
    print("=" * 70)
    
    # Initialize visualizer
    viz = StockDataVisualizer(api_key=config.POLYGON_API_KEY)
    
    # Check available stocks
    summary = viz.collector.get_data_summary()
    
    if summary.empty:
        print("\n⚠ No data found in database!")
        print("Please run data collection first:")
        print("  python stock_data_collector.py")
        viz.close()
        return
    
    print("\nAvailable stocks:")
    print(summary[['ticker', 'record_count']].to_string(index=False))
    
    # Select a ticker for demonstration
    ticker = summary.iloc[0]['ticker']
    print(f"\nGenerating visualizations for {ticker}...")
    
    # Generate plots
    print("\n1. Price History...")
    viz.plot_price_history(ticker, save_path=f'{ticker}_price_history.png')
    
    print("2. Moving Averages...")
    viz.plot_moving_averages(ticker, save_path=f'{ticker}_moving_averages.png')
    
    print("3. Returns Distribution...")
    viz.plot_returns_distribution(ticker, save_path=f'{ticker}_returns.png')
    
    if len(summary) > 1:
        print("4. Portfolio Comparison...")
        viz.plot_portfolio_comparison(save_path='portfolio_comparison.png')
        
        print("5. Correlation Matrix...")
        viz.plot_correlation_matrix(save_path='correlation_matrix.png')
    
    # Generate statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    
    for ticker in summary['ticker']:
        stats = viz.generate_summary_statistics(ticker)
        if stats:
            print(f"\n{ticker}:")
            for key, value in stats.items():
                if key != 'Ticker':
                    print(f"  {key:.<25} {value}")
    
    viz.close()
    
    print("\n✓ Visualization complete!")
    print("✓ Charts saved to current directory")


if __name__ == "__main__":
    main()
