"""
Performance Metrics Calculator
DSCI-560 Lab 4 - Performance Analysis

This module calculates comprehensive performance metrics for trading strategies:
- Annualized Returns
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- And more...
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


class PerformanceMetrics:
    """
    Calculate and display trading performance metrics
    """
    
    def __init__(self, risk_free_rate=0.02):
        """
        Initialize performance metrics calculator
        
        Parameters:
        -----------
        risk_free_rate : float
            Annual risk-free rate (default 2% = 0.02)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_all_metrics(self, portfolio_df, trades_df=None, initial_capital=100000):
        """
        Calculate all performance metrics
        
        Parameters:
        -----------
        portfolio_df : pd.DataFrame
            DataFrame with portfolio values over time
        trades_df : pd.DataFrame
            DataFrame with trade history (optional)
        initial_capital : float
            Initial investment amount
        
        Returns:
        --------
        dict
            Dictionary of all metrics
        """
        metrics = {}
        
        # Basic metrics
        metrics.update(self.calculate_returns(portfolio_df, initial_capital))
        
        # Risk metrics
        metrics.update(self.calculate_risk_metrics(portfolio_df))
        
        # Sharpe ratio
        metrics['sharpe_ratio'] = self.calculate_sharpe_ratio(portfolio_df)
        
        # Sortino ratio
        metrics['sortino_ratio'] = self.calculate_sortino_ratio(portfolio_df)
        
        # Maximum drawdown
        metrics['max_drawdown'], metrics['max_drawdown_pct'] = self.calculate_max_drawdown(portfolio_df)
        
        # Calmar ratio
        metrics['calmar_ratio'] = self.calculate_calmar_ratio(
            metrics['annualized_return'],
            metrics['max_drawdown_pct']
        )
        
        # Trading metrics (if trades provided)
        if trades_df is not None and not trades_df.empty:
            metrics.update(self.calculate_trading_metrics(trades_df))
        
        return metrics
    
    def calculate_returns(self, portfolio_df, initial_capital):
        """
        Calculate return metrics
        
        Returns:
        --------
        dict
            Return metrics including total, annualized, and cumulative returns
        """
        if 'portfolio_value' not in portfolio_df.columns:
            return {}
        
        # Total return
        final_value = portfolio_df['portfolio_value'].iloc[-1]
        total_return = final_value - initial_capital
        total_return_pct = (total_return / initial_capital) * 100
        
        # Calculate daily returns
        if 'returns' not in portfolio_df.columns:
            portfolio_df['returns'] = portfolio_df['portfolio_value'].pct_change()
        
        # Annualized return
        trading_days = len(portfolio_df)
        years = trading_days / 252  # Assuming 252 trading days per year
        
        if years > 0:
            annualized_return = ((final_value / initial_capital) ** (1 / years) - 1) * 100
        else:
            annualized_return = 0
        
        # Cumulative return
        cumulative_returns = (portfolio_df['portfolio_value'] / initial_capital - 1) * 100
        
        return {
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'annualized_return': annualized_return,
            'final_value': final_value,
            'cumulative_returns': cumulative_returns
        }
    
    def calculate_risk_metrics(self, portfolio_df):
        """
        Calculate risk-related metrics
        
        Returns:
        --------
        dict
            Risk metrics including volatility
        """
        if 'returns' not in portfolio_df.columns:
            portfolio_df['returns'] = portfolio_df['portfolio_value'].pct_change()
        
        # Daily volatility
        daily_volatility = portfolio_df['returns'].std()
        
        # Annualized volatility
        annualized_volatility = daily_volatility * np.sqrt(252) * 100
        
        # Downside deviation (for Sortino ratio)
        negative_returns = portfolio_df['returns'][portfolio_df['returns'] < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252) * 100
        
        return {
            'daily_volatility': daily_volatility * 100,
            'annualized_volatility': annualized_volatility,
            'downside_deviation': downside_deviation
        }
    
    def calculate_sharpe_ratio(self, portfolio_df):
        """
        Calculate Sharpe Ratio
        
        Sharpe Ratio = (Portfolio Return - Risk Free Rate) / Portfolio Volatility
        Higher is better (measures risk-adjusted returns)
        
        Returns:
        --------
        float
            Sharpe ratio
        """
        if 'returns' not in portfolio_df.columns:
            portfolio_df['returns'] = portfolio_df['portfolio_value'].pct_change()
        
        # Annualized metrics
        excess_returns = portfolio_df['returns'].mean() * 252 - self.risk_free_rate
        volatility = portfolio_df['returns'].std() * np.sqrt(252)
        
        if volatility == 0:
            return 0
        
        sharpe_ratio = excess_returns / volatility
        
        return sharpe_ratio
    
    def calculate_sortino_ratio(self, portfolio_df):
        """
        Calculate Sortino Ratio
        
        Similar to Sharpe but only considers downside volatility
        Better measure for strategies with asymmetric returns
        
        Returns:
        --------
        float
            Sortino ratio
        """
        if 'returns' not in portfolio_df.columns:
            portfolio_df['returns'] = portfolio_df['portfolio_value'].pct_change()
        
        # Annualized excess return
        excess_returns = portfolio_df['returns'].mean() * 252 - self.risk_free_rate
        
        # Downside deviation
        negative_returns = portfolio_df['returns'][portfolio_df['returns'] < 0]
        
        if len(negative_returns) == 0:
            return float('inf')  # No downside
        
        downside_deviation = negative_returns.std() * np.sqrt(252)
        
        if downside_deviation == 0:
            return 0
        
        sortino_ratio = excess_returns / downside_deviation
        
        return sortino_ratio
    
    def calculate_max_drawdown(self, portfolio_df):
        """
        Calculate Maximum Drawdown
        
        Maximum Drawdown = Largest peak-to-trough decline
        Measures worst-case loss from peak
        
        Returns:
        --------
        tuple
            (max_drawdown_value, max_drawdown_pct)
        """
        if 'portfolio_value' not in portfolio_df.columns:
            return 0, 0
        
        # Calculate running maximum
        portfolio_df['cummax'] = portfolio_df['portfolio_value'].cummax()
        
        # Calculate drawdown
        portfolio_df['drawdown'] = portfolio_df['portfolio_value'] - portfolio_df['cummax']
        portfolio_df['drawdown_pct'] = (portfolio_df['drawdown'] / portfolio_df['cummax']) * 100
        
        # Maximum drawdown
        max_drawdown = portfolio_df['drawdown'].min()
        max_drawdown_pct = portfolio_df['drawdown_pct'].min()
        
        return max_drawdown, max_drawdown_pct
    
    def calculate_calmar_ratio(self, annualized_return, max_drawdown_pct):
        """
        Calculate Calmar Ratio
        
        Calmar Ratio = Annualized Return / |Maximum Drawdown|
        Measures return per unit of downside risk
        
        Returns:
        --------
        float
            Calmar ratio
        """
        if max_drawdown_pct == 0:
            return 0
        
        calmar_ratio = annualized_return / abs(max_drawdown_pct)
        
        return calmar_ratio
    
    def calculate_trading_metrics(self, trades_df):
        """
        Calculate trading-specific metrics
        
        Parameters:
        -----------
        trades_df : pd.DataFrame
            DataFrame with trade history
        
        Returns:
        --------
        dict
            Trading metrics
        """
        if trades_df.empty:
            return {}
        
        # Separate buy and sell trades
        buy_trades = trades_df[trades_df['action'] == 'BUY']
        sell_trades = trades_df[trades_df['action'] == 'SELL']
        
        # Calculate wins and losses
        wins = 0
        losses = 0
        total_profit = 0
        total_loss = 0
        
        # Match buys with sells (simplified - assumes FIFO)
        for _, sell in sell_trades.iterrows():
            ticker = sell['ticker']
            sell_price = sell['price']
            
            # Find corresponding buy
            buy = buy_trades[buy_trades['ticker'] == ticker]
            if not buy.empty:
                buy_price = buy.iloc[0]['price']
                profit_loss = (sell_price - buy_price) * sell['shares']
                
                if profit_loss > 0:
                    wins += 1
                    total_profit += profit_loss
                else:
                    losses += 1
                    total_loss += abs(profit_loss)
        
        # Calculate metrics
        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = total_profit / wins if wins > 0 else 0
        avg_loss = total_loss / losses if losses > 0 else 0
        
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        return {
            'total_trades': len(trades_df),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'winning_trades': wins,
            'losing_trades': losses,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_profit': total_profit,
            'total_loss': total_loss
        }
    
    def print_metrics(self, metrics):
        """
        Print all metrics in a formatted way
        
        Parameters:
        -----------
        metrics : dict
            Dictionary of metrics
        """
        print("\n" + "=" * 70)
        print("PERFORMANCE METRICS SUMMARY")
        print("=" * 70)
        
        # Returns
        print("\n📈 RETURN METRICS:")
        print("-" * 70)
        if 'total_return' in metrics:
            print(f"Total Return:              ${metrics['total_return']:,.2f}")
        if 'total_return_pct' in metrics:
            print(f"Total Return %:            {metrics['total_return_pct']:.2f}%")
        if 'annualized_return' in metrics:
            print(f"Annualized Return:         {metrics['annualized_return']:.2f}%")
        if 'final_value' in metrics:
            print(f"Final Portfolio Value:     ${metrics['final_value']:,.2f}")
        
        # Risk metrics
        print("\n📊 RISK METRICS:")
        print("-" * 70)
        if 'annualized_volatility' in metrics:
            print(f"Annualized Volatility:     {metrics['annualized_volatility']:.2f}%")
        if 'max_drawdown' in metrics:
            print(f"Maximum Drawdown:          ${metrics['max_drawdown']:,.2f}")
        if 'max_drawdown_pct' in metrics:
            print(f"Maximum Drawdown %:        {metrics['max_drawdown_pct']:.2f}%")
        if 'downside_deviation' in metrics:
            print(f"Downside Deviation:        {metrics['downside_deviation']:.2f}%")
        
        # Risk-adjusted returns
        print("\n⚖️  RISK-ADJUSTED METRICS:")
        print("-" * 70)
        if 'sharpe_ratio' in metrics:
            print(f"Sharpe Ratio:              {metrics['sharpe_ratio']:.3f}")
            self._print_sharpe_interpretation(metrics['sharpe_ratio'])
        if 'sortino_ratio' in metrics:
            print(f"Sortino Ratio:             {metrics['sortino_ratio']:.3f}")
        if 'calmar_ratio' in metrics:
            print(f"Calmar Ratio:              {metrics['calmar_ratio']:.3f}")
        
        # Trading metrics
        if 'total_trades' in metrics and metrics['total_trades'] > 0:
            print("\n💼 TRADING METRICS:")
            print("-" * 70)
            print(f"Total Trades:              {metrics['total_trades']}")
            print(f"  Buy Trades:              {metrics.get('buy_trades', 0)}")
            print(f"  Sell Trades:             {metrics.get('sell_trades', 0)}")
            if 'winning_trades' in metrics:
                print(f"Winning Trades:            {metrics['winning_trades']}")
                print(f"Losing Trades:             {metrics['losing_trades']}")
                print(f"Win Rate:                  {metrics['win_rate']:.2f}%")
            if 'profit_factor' in metrics:
                print(f"Profit Factor:             {metrics['profit_factor']:.2f}")
            if 'avg_win' in metrics:
                print(f"Average Win:               ${metrics['avg_win']:,.2f}")
                print(f"Average Loss:              ${metrics['avg_loss']:,.2f}")
        
        print("\n" + "=" * 70)
    
    def _print_sharpe_interpretation(self, sharpe_ratio):
        """Print interpretation of Sharpe ratio"""
        if sharpe_ratio < 0:
            interpretation = "Poor (negative excess return)"
        elif sharpe_ratio < 1:
            interpretation = "Sub-optimal"
        elif sharpe_ratio < 2:
            interpretation = "Good"
        elif sharpe_ratio < 3:
            interpretation = "Very Good"
        else:
            interpretation = "Excellent"
        
        print(f"  Interpretation:          {interpretation}")
    
    def plot_performance(self, portfolio_df, initial_capital, save_path=None):
        """
        Create comprehensive performance plots
        
        Parameters:
        -----------
        portfolio_df : pd.DataFrame
            Portfolio value over time
        initial_capital : float
            Initial investment
        save_path : str
            Path to save plot (optional)
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Portfolio Value Over Time
        ax1 = axes[0, 0]
        ax1.plot(portfolio_df.index, portfolio_df['portfolio_value'], 
                linewidth=2, color='steelblue')
        ax1.axhline(y=initial_capital, color='red', linestyle='--', 
                   label='Initial Capital', alpha=0.7)
        ax1.set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Cumulative Returns
        ax2 = axes[0, 1]
        cumulative_returns = (portfolio_df['portfolio_value'] / initial_capital - 1) * 100
        ax2.plot(portfolio_df.index, cumulative_returns, 
                linewidth=2, color='green')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_title('Cumulative Returns (%)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Return (%)')
        ax2.grid(True, alpha=0.3)
        
        # 3. Drawdown
        ax3 = axes[1, 0]
        if 'drawdown_pct' in portfolio_df.columns:
            ax3.fill_between(portfolio_df.index, portfolio_df['drawdown_pct'], 0,
                           color='red', alpha=0.3)
            ax3.plot(portfolio_df.index, portfolio_df['drawdown_pct'],
                    linewidth=2, color='darkred')
        ax3.set_title('Drawdown (%)', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Drawdown (%)')
        ax3.grid(True, alpha=0.3)
        
        # 4. Daily Returns Distribution
        ax4 = axes[1, 1]
        if 'returns' in portfolio_df.columns:
            returns_pct = portfolio_df['returns'].dropna() * 100
            ax4.hist(returns_pct, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
            ax4.axvline(returns_pct.mean(), color='red', linestyle='--', 
                       linewidth=2, label=f'Mean: {returns_pct.mean():.3f}%')
            ax4.set_title('Daily Returns Distribution', fontsize=14, fontweight='bold')
            ax4.set_xlabel('Daily Return (%)')
            ax4.set_ylabel('Frequency')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Performance plots saved to: {save_path}")
        else:
            plt.show()


# ==========================================================================
# EXAMPLE USAGE
# ==========================================================================

def example_usage():
    """Demonstrate performance metrics calculation"""
    from backtester import Backtester
    
    print("=" * 70)
    print("PERFORMANCE METRICS DEMONSTRATION")
    print("=" * 70)
    
    # Run backtest
    backtester = Backtester(initial_capital=100000)
    results = backtester.backtest_single_stock(ticker='AAPL', strategy='HYBRID')
    
    if results is None:
        print("No results to analyze. Please ensure data is collected.")
        return
    
    # Calculate metrics
    metrics_calc = PerformanceMetrics(risk_free_rate=0.02)
    
    metrics = metrics_calc.calculate_all_metrics(
        portfolio_df=results['portfolio_df'],
        trades_df=results['trades_df'],
        initial_capital=100000
    )
    
    # Print metrics
    metrics_calc.print_metrics(metrics)
    
    # Plot performance
    metrics_calc.plot_performance(
        portfolio_df=results['portfolio_df'],
        initial_capital=100000,
        save_path='performance_analysis.png'
    )
    
    backtester.close()


if __name__ == "__main__":
    example_usage()
