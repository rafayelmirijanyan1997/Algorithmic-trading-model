import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
import config
from trading_algorithms import TradingAlgorithms


class Backtester:
    """
    Backtesting engine for algorithmic trading strategies
    """
    
    def __init__(self, initial_capital=None, db_path='stock_data.db'):
        """
        Initialize backtester
        
        Parameters:
        -----------
        initial_capital : float
            Starting capital (default is 10k)
        db_path : str
            Path to database
        """
        self.initial_capital = initial_capital or config.INITIAL_CAPITAL
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        
        # Portfolio state
        self.cash = self.initial_capital
        self.positions = {}  # {ticker: shares}
        self.portfolio_value_history = []
        self.trades = []
        
        # Algorithms
        self.algorithms = TradingAlgorithms()
    
    def backtest_single_stock(self, ticker, strategy='HYBRID', start_date=None, end_date=None):
        """
        Backtest a strategy on a single stock
        
        Parameters:
        -----------
        ticker : str
            Stock ticker
        strategy : str
            Strategy to use ('SMA', 'RSI', 'MACD', 'BB', 'HYBRID')
        start_date : str
            Start date for backtest
        end_date : str
            End date for backtest
        
        Returns:
        --------
        dict
            Backtest results
        """
        print(f"\n{'=' * 70}")
        print(f"BACKTESTING {ticker} - {strategy} Strategy")
        print('=' * 70)
        
        # Get data
        df = self._get_stock_data(ticker, start_date, end_date)
        
        if df.empty:
            print(f"No data available for {ticker}")
            return None
        
        # Calculate signals based on strategy
        df = self._apply_strategy(df, strategy)
        
        # Reset portfolio
        self.cash = self.initial_capital
        self.positions = {ticker: 0}
        self.portfolio_value_history = []
        self.trades = []
        
        # Run backtest
        position_col = f'{strategy}_position'
        
        for date, row in df.iterrows():
            # Check for buy/sell signals
            if position_col in row and not pd.isna(row[position_col]):
                signal = row[position_col]
                price = row['close']
                
                if signal > 0:  # BUY signal
                    self._execute_buy(ticker, price, date)
                elif signal < 0:  # SELL signal
                    self._execute_sell(ticker, price, date)
            
            # Record portfolio value
            portfolio_value = self._calculate_portfolio_value(df.loc[:date])
            self.portfolio_value_history.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'cash': self.cash,
                'positions_value': portfolio_value - self.cash,
                'shares': self.positions.get(ticker, 0)
            })
        
        # Calculate results
        results = self._calculate_results(ticker, df)
        
        return results
    
    def backtest_portfolio(self, tickers=None, strategy='HYBRID', start_date=None, end_date=None):
        """
        Backtest a strategy on multiple stocks (portfolio)
        
        Parameters:
        -----------
        tickers : list
            List of stock tickers (default from config)
        strategy : str
            Strategy to use
        start_date : str
            Start date for backtest
        end_date : str
            End date for backtest
        
        Returns:
        --------
        dict
            Portfolio backtest results
        """
        if tickers is None:
            tickers = config.STOCK_TICKERS
        
        print(f"\n{'=' * 70}")
        print(f"BACKTESTING PORTFOLIO - {strategy} Strategy")
        print(f"Tickers: {', '.join(tickers)}")
        print('=' * 70)
        
        # Reset portfolio
        self.cash = self.initial_capital
        self.positions = {ticker: 0 for ticker in tickers}
        self.portfolio_value_history = []
        self.trades = []
        
        # Get data for all stocks
        all_data = {}
        for ticker in tickers:
            df = self._get_stock_data(ticker, start_date, end_date)
            if not df.empty:
                df = self._apply_strategy(df, strategy)
                all_data[ticker] = df
        
        if not all_data:
            print("No data available for any ticker")
            return None
        
        # Get all unique dates
        all_dates = sorted(set().union(*[set(df.index) for df in all_data.values()]))
        
        # Run backtest day by day
        position_col = f'{strategy}_position'
        
        for date in all_dates:
            # Check each stock for signals
            for ticker, df in all_data.items():
                if date in df.index:
                    row = df.loc[date]
                    
                    if position_col in row and not pd.isna(row[position_col]):
                        signal = row[position_col]
                        price = row['close']
                        
                        if signal > 0:  # BUY signal
                            # Allocate portion of available cash
                            allocation = self.cash / len(tickers)
                            self._execute_buy(ticker, price, date, max_amount=allocation)
                        elif signal < 0:  # SELL signal
                            self._execute_sell(ticker, price, date)
            
            # Record portfolio value
            portfolio_value = self._calculate_portfolio_value_multi(all_data, date)
            

            positions_value = sum(
                self.positions.get(ticker, 0) * df.loc[date, 'close']
                for ticker, df in all_data.items()
                if date in df.index
            )

            
            self.portfolio_value_history.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'cash': self.cash,
                'positions_value': positions_value
            })
        
        # Calculate results
        results = self._calculate_portfolio_results(all_data)
        
        return results
    
    def _get_stock_data(self, ticker, start_date=None, end_date=None):
        """Get stock data from database"""
        query = "SELECT * FROM stock_prices WHERE ticker = ?"
        params = [ticker]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date"
        
        df = pd.read_sql_query(query, self.conn, params=params)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
        
        return df
    
    def _apply_strategy(self, df, strategy):
        """Apply trading strategy to data"""
        if strategy == 'SMA':
            return self.algorithms.calculate_sma(df)
        elif strategy == 'RSI':
            return self.algorithms.calculate_rsi(df)
        elif strategy == 'MACD':
            return self.algorithms.calculate_macd(df)
        elif strategy == 'BB':
            return self.algorithms.calculate_bollinger_bands(df)
        elif strategy == 'HYBRID':
            return self.algorithms.calculate_hybrid_strategy(df)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _execute_buy(self, ticker, price, date, max_amount=None):
        """Execute a buy order"""
        # Determine how much to buy
        if max_amount is None:
            available_cash = self.cash * 0.95  # Use 95% of cash, keep 5% reserve
        else:
            available_cash = min(max_amount * 0.95, self.cash * 0.95)
        
        if available_cash < price:  # Can't afford even 1 share
            return
        
        # Calculate shares to buy
        shares = int(available_cash / price)
        
        if shares < 1:
            return
        
        # Calculate cost including fees
        total_cost = shares * price

        
        # Check if we have enough cash
        if total_cost > self.cash:
            return
        
        # Execute trade
        self.cash -= total_cost
        self.positions[ticker] = self.positions.get(ticker, 0) + shares
        
        # Record trade
        self.trades.append({
            'date': date,
            'ticker': ticker,
            'action': 'BUY',
            'shares': shares,
            'price': price,

            'total_cost': total_cost
        })
    
    def _execute_sell(self, ticker, price, date):
        """Execute a sell order"""
        shares = self.positions.get(ticker, 0)
        
        if shares <= 0:  # No shares to sell
            return
        
        # Calculate proceeds
        total_proceeds = shares * price

        
        # Execute trade
        self.cash += total_proceeds
        self.positions[ticker] = 0
        
        # Record trade
        self.trades.append({
            'date': date,
            'ticker': ticker,
            'action': 'SELL',
            'shares': shares,
            'price': price,
            'total_proceeds': total_proceeds
        })
    
    def _calculate_portfolio_value(self, df):
        """Calculate total portfolio value for single stock"""
        if df.empty:
            return self.cash
        
        latest_price = df['close'].iloc[-1]
        ticker = df['ticker'].iloc[0] if 'ticker' in df.columns else list(self.positions.keys())[0]
        shares = self.positions.get(ticker, 0)
        
        return self.cash + (shares * latest_price)
    
    def _calculate_portfolio_value_multi(self, all_data, date):
        """Calculate total portfolio value for multiple stocks"""
        total_value = self.cash
        
        for ticker, df in all_data.items():
            if date in df.index:
                price = df.loc[date, 'close']
                shares = self.positions.get(ticker, 0)
                total_value += shares * price
        
        return total_value
    
    def _calculate_results(self, ticker, df):
        """Calculate backtest results for single stock"""
        # Portfolio value over time
        portfolio_df = pd.DataFrame(self.portfolio_value_history)
        portfolio_df['date'] = pd.to_datetime(portfolio_df['date'])
        portfolio_df = portfolio_df.set_index('date')
        
        # Calculate returns
        portfolio_df['returns'] = portfolio_df['portfolio_value'].pct_change()
        
        # Final values
        final_value = portfolio_df['portfolio_value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        
        # Calculate metrics
        num_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t['action'] == 'SELL' and 
                           any(buy['action'] == 'BUY' and buy['price'] < t['price'] 
                               for buy in self.trades))
        
        # Buy and hold comparison
        buy_hold_return = ((df['close'].iloc[-1] - df['close'].iloc[0]) / 
                          df['close'].iloc[0] * 100)
        
        results = {
            'ticker': ticker,
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return,
            'buy_hold_return_pct': buy_hold_return,
            'num_trades': num_trades,
            'winning_trades': winning_trades,
            'portfolio_df': portfolio_df,
            'trades_df': pd.DataFrame(self.trades)
        }
        
        return results
    
    def _calculate_portfolio_results(self, all_data):
        """Calculate backtest results for portfolio"""
        portfolio_df = pd.DataFrame(self.portfolio_value_history)
        portfolio_df['date'] = pd.to_datetime(portfolio_df['date'])
        portfolio_df = portfolio_df.set_index('date')
        
        portfolio_df['returns'] = portfolio_df['portfolio_value'].pct_change()
        
        final_value = portfolio_df['portfolio_value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        
        results = {
            'tickers': list(all_data.keys()),
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return,
            'num_trades': len(self.trades),
            'portfolio_df': portfolio_df,
            'trades_df': pd.DataFrame(self.trades)
        }
        
        return results
    
    def print_results(self, results):
        """Print backtest results"""
        print(f"\n{'=' * 70}")
        print("BACKTEST RESULTS")
        print('=' * 70)
        
        print(f"\nInitial Capital:        ${results['initial_capital']:,.2f}")
        print(f"Final Portfolio Value:  ${results['final_value']:,.2f}")
        print(f"Total Return:           ${results['final_value'] - results['initial_capital']:,.2f}")
        print(f"Return Percentage:      {results['total_return_pct']:.2f}%")
        
        if 'buy_hold_return_pct' in results:
            print(f"Buy & Hold Return:      {results['buy_hold_return_pct']:.2f}%")
            alpha = results['total_return_pct'] - results['buy_hold_return_pct']
            print(f"Alpha (vs Buy & Hold):  {alpha:.2f}%")
        
        print(f"\nTotal Trades:           {results['num_trades']}")
        
        if results['num_trades'] > 0 and 'winning_trades' in results:
            win_rate = (results['winning_trades'] / (results['num_trades'] / 2)) * 100
            print(f"Winning Trades:         {results['winning_trades']}")
            print(f"Win Rate:               {win_rate:.2f}%")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# ==========================================================================
# EXAMPLE USAGE
# ==========================================================================

def example_single_stock_backtest():
    """Example: Backtest single stock"""
    backtester = Backtester(initial_capital=100000)
    
    results = backtester.backtest_single_stock(
        ticker='AAPL',
        strategy='HYBRID'
    )
    
    if results:
        backtester.print_results(results)
        
        print("\nRecent Trades:")
        if not results['trades_df'].empty:
            print(results['trades_df'].tail(10))
    
    backtester.close()


def example_portfolio_backtest():
    """Example: Backtest portfolio"""
    backtester = Backtester(initial_capital=100000)
    
    results = backtester.backtest_portfolio(
        tickers=['AAPL', 'MSFT', 'GOOGL'],
        strategy='HYBRID'
    )
    
    if results:
        backtester.print_results(results)
    
    backtester.close()


if __name__ == "__main__":
    print("Choose example:")
    print("1. Single stock backtest")
    print("2. Portfolio backtest")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == '1':
        example_single_stock_backtest()
    elif choice == '2':
        example_portfolio_backtest()
    else:
        print("Invalid choice")
