"""
Trading Algorithms Module

This module implements various trading algorithms:
1. Simple Moving Average (SMA) Crossover
2. Relative Strength Index (RSI)
3. MACD (Moving Average Convergence Divergence)
4. Bollinger Bands
5. Hybrid Strategy (Combination)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import config


class TradingAlgorithms:

    
    def __init__(self):

        self.signals_history = []
    

    
    def calculate_sma(self, df, short_window=None, long_window=None): # simple moving average
        """
        Calculate Simple Moving Average and generate signals
        
        Strategy:
        - BUY when short-term MA crosses above long-term MA (Golden Cross)
        - SELL when short-term MA crosses below long-term MA (Death Cross)
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with 'close' prices
        short_window : int
            Short-term moving average period (default from config)
        long_window : int
            Long-term moving average period (default from config)
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with SMA columns and signals
        """
        if short_window is None:
            short_window = config.SHORT_MA_PERIOD
        if long_window is None:
            long_window = config.LONG_MA_PERIOD
        
        df = df.copy()
        
        # Calculate moving averages
        df[f'SMA_{short_window}'] = df['close'].rolling(window=short_window).mean()
        df[f'SMA_{long_window}'] = df['close'].rolling(window=long_window).mean()
        
        # Generate signals
        df['SMA_signal'] = 0
        df.loc[df[f'SMA_{short_window}'] > df[f'SMA_{long_window}'], 'SMA_signal'] = 1  # BUY
        df.loc[df[f'SMA_{short_window}'] < df[f'SMA_{long_window}'], 'SMA_signal'] = -1  # SELL
        
        # Detect crossovers (position changes)
        df['SMA_position'] = df['SMA_signal'].diff()
        
        return df
    

    
    def calculate_ema(self, df, short_window=12, long_window=26):
        """
        Calculate Exponential Moving Average and generate signals
        
        EMA gives more weight to recent prices
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with 'close' prices
        short_window : int
            Short-term EMA period
        long_window : int
            Long-term EMA period
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with EMA columns and signals
        """
        df = df.copy()
        
        # Calculate EMAs
        df[f'EMA_{short_window}'] = df['close'].ewm(span=short_window, adjust=False).mean()
        df[f'EMA_{long_window}'] = df['close'].ewm(span=long_window, adjust=False).mean()
        
        # Generate signals
        df['EMA_signal'] = 0
        df.loc[df[f'EMA_{short_window}'] > df[f'EMA_{long_window}'], 'EMA_signal'] = 1
        df.loc[df[f'EMA_{short_window}'] < df[f'EMA_{long_window}'], 'EMA_signal'] = -1
        
        df['EMA_position'] = df['EMA_signal'].diff()
        
        return df
    
    
    def calculate_rsi(self, df, period=None, oversold=None, overbought=None):
        """
        Calculate Relative Strength Index (RSI)
        
        RSI measures momentum on a scale of 0-100
        - RSI < 30: Oversold (potential BUY)
        - RSI > 70: Overbought (potential SELL)
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with 'close' prices
        period : int
            RSI period (default from config)
        oversold : int
            Oversold threshold (default from config)
        overbought : int
            Overbought threshold (default from config)
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with RSI column and signals
        """
        if period is None:
            period = config.RSI_PERIOD
        if oversold is None:
            oversold = config.RSI_OVERSOLD
        if overbought is None:
            overbought = config.RSI_OVERBOUGHT
        
        df = df.copy()
        
        # Calculate price changes
        delta = df['close'].diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Generate signals
        df['RSI_signal'] = 0
        df.loc[df['RSI'] < oversold, 'RSI_signal'] = 1  # BUY (oversold)
        df.loc[df['RSI'] > overbought, 'RSI_signal'] = -1  # SELL (overbought)
        
        df['RSI_position'] = df['RSI_signal'].diff()
        
        return df
    
    
    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        """
        Calculate MACD indicator
        
        MACD = Fast EMA - Slow EMA
        Signal Line = EMA of MACD
        
        Strategy:
        - BUY when MACD crosses above signal line
        - SELL when MACD crosses below signal line
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with 'close' prices
        fast : int
            Fast EMA period
        slow : int
            Slow EMA period
        signal : int
            Signal line period
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with MACD columns and signals
        """
        df = df.copy()
        
        # Calculate EMAs
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        # Calculate MACD
        df['MACD'] = ema_fast - ema_slow
        df['MACD_signal_line'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal_line']
        
        # Generate signals
        df['MACD_trading_signal'] = 0
        df.loc[df['MACD'] > df['MACD_signal_line'], 'MACD_trading_signal'] = 1  # BUY
        df.loc[df['MACD'] < df['MACD_signal_line'], 'MACD_trading_signal'] = -1  # SELL
        
        df['MACD_position'] = df['MACD_trading_signal'].diff()
        
        return df
    

    
    def calculate_bollinger_bands(self, df, period=None, std_dev=None):
        """
        Calculate Bollinger Bands
        
        Bollinger Bands consist of:
        - Middle Band: SMA
        - Upper Band: SMA + (std_dev × standard deviation)
        - Lower Band: SMA - (std_dev × standard deviation)
        
        Strategy:
        - BUY when price touches lower band
        - SELL when price touches upper band
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with 'close' prices
        period : int
            Moving average period (default from config)
        std_dev : int
            Number of standard deviations (default from config)
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with Bollinger Bands and signals
        """
        if period is None:
            period = config.BB_PERIOD
        if std_dev is None:
            std_dev = config.BB_STD_DEV
        
        df = df.copy()
        
        # Calculate middle band (SMA)
        df['BB_middle'] = df['close'].rolling(window=period).mean()
        
        # Calculate standard deviation
        rolling_std = df['close'].rolling(window=period).std()
        
        # Calculate upper and lower bands
        df['BB_upper'] = df['BB_middle'] + (rolling_std * std_dev)
        df['BB_lower'] = df['BB_middle'] - (rolling_std * std_dev)
        
        # Calculate bandwidth
        df['BB_bandwidth'] = (df['BB_upper'] - df['BB_lower']) / df['BB_middle']
        
        # Generate signals
        df['BB_signal'] = 0
        df.loc[df['close'] <= df['BB_lower'], 'BB_signal'] = 1  # BUY (oversold)
        df.loc[df['close'] >= df['BB_upper'], 'BB_signal'] = -1  # SELL (overbought)
        
        df['BB_position'] = df['BB_signal'].diff()
        
        return df
    

    
    def calculate_hybrid_strategy(self, df):
        """
        Hybrid strategy combining multiple indicators
        
        This strategy uses a voting system:
        - Calculates all indicators
        - Aggregates signals
        - Makes decision based on consensus
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with 'close' prices
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with all indicators and hybrid signal
        """
        df = df.copy()
        
        # Calculate all indicators
        df = self.calculate_sma(df)
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        df = self.calculate_bollinger_bands(df)
        
        # Combine signals (voting system)
        df['signal_sum'] = (
            df['SMA_signal'] + 
            df['RSI_signal'] + 
            df['MACD_trading_signal'] + 
            df['BB_signal']
        )
        
        # Generate hybrid signal based on majority vote
        df['HYBRID_signal'] = 0
        df.loc[df['signal_sum'] >= 2, 'HYBRID_signal'] = 1  # BUY if 2+ indicators agree
        df.loc[df['signal_sum'] <= -2, 'HYBRID_signal'] = -1  # SELL if 2+ indicators agree
        
        df['HYBRID_position'] = df['HYBRID_signal'].diff()
        
        # Calculate signal strength
        df['signal_strength'] = df['signal_sum'].abs() / 4  # Normalize to 0-1
        
        return df


    
    def get_latest_signal(self, df, strategy='HYBRID'):
        """
        Get the most recent trading signal
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with signals
        strategy : str
            Strategy name ('SMA', 'RSI', 'MACD', 'BB', 'HYBRID')
        
        Returns:
        --------
        dict
            Latest signal information
        """
        if df.empty:
            return None
        
        signal_col = f'{strategy}_signal'
        position_col = f'{strategy}_position'
        
        latest = df.iloc[-1]
        
        signal_info = {
            'date': latest.name if isinstance(latest.name, str) else str(latest.name),
            'close': latest['close'],
            'signal': latest.get(signal_col, 0),
            'position': latest.get(position_col, 0),
            'action': self._signal_to_action(latest.get(position_col, 0))
        }
        
        return signal_info
    
    def _signal_to_action(self, position):
        """Convert position value to action string"""
        if position > 0:
            return 'BUY'
        elif position < 0:
            return 'SELL'
        else:
            return 'HOLD'
    
    def get_all_signals(self, df, strategy='HYBRID'):
        """
        Get all buy/sell signals from the strategy
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with signals
        strategy : str
            Strategy name
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with only buy/sell signals (position changes)
        """
        position_col = f'{strategy}_position'
        
        # Get only rows where position changed (buy or sell signals)
        signals = df[df[position_col] != 0].copy()
        signals['action'] = signals[position_col].apply(self._signal_to_action)
        
        return signals[['close', position_col, 'action']]
    
    def calculate_all_indicators(self, df):
        """
        Calculate all technical indicators at once
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with 'close' prices
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with all indicators
        """
        return self.calculate_hybrid_strategy(df)




def example_usage():

    print("=" * 70)
    print("TRADING ALGORITHMS DEMONSTRATION")
    print("=" * 70)
    
    from stock_data_collector import StockDataCollector
    
    # Initialize
    collector = StockDataCollector(api_key=config.POLYGON_API_KEY)
    algorithms = TradingAlgorithms()
    
    # Get data for a stock
    ticker = 'AAPL'
    print(f"\nAnalyzing {ticker}...\n")
    
    df = collector.get_data_from_db(ticker=ticker)
    
    if df.empty:
        print("No data found. Please run data collection first.")
        return
    
    # Convert date to datetime and set as index
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    
    # Calculate all indicators
    df = algorithms.calculate_all_indicators(df)
    
    # Show latest signals
    print("LATEST SIGNALS:")
    print("-" * 70)
    
    for strategy in ['SMA', 'RSI', 'MACD', 'BB', 'HYBRID']:
        signal = algorithms.get_latest_signal(df, strategy)
        if signal:
            print(f"{strategy:6s}: {signal['action']:4s} | "
                  f"Price: ${signal['close']:.2f} | "
                  f"Signal: {signal['signal']:2.0f}")
    
    # Show recent buy/sell signals for hybrid strategy
    print("\n" + "=" * 70)
    print("RECENT HYBRID STRATEGY SIGNALS:")
    print("=" * 70)
    
    recent_signals = algorithms.get_all_signals(df.tail(60), 'HYBRID')
    if not recent_signals.empty:
        print(recent_signals.tail(10))
    else:
        print("No signals in recent period")
    
    collector.close()


if __name__ == "__main__":
    example_usage()
