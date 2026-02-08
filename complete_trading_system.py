import pandas as pd
import numpy as np
from datetime import datetime
import config
from stock_data_collector import StockDataCollector
from trading_algorithms import TradingAlgorithms
from backtester import Backtester
from performance_metrics import PerformanceMetrics
import matplotlib.pyplot as plt


class AlgorithmicTradingSystem:

    
    def __init__(self):

        self.collector = StockDataCollector(api_key=config.POLYGON_API_KEY)
        self.algorithms = TradingAlgorithms()
        self.backtester = Backtester()
        self.metrics_calc = PerformanceMetrics()
        
        print("=" * 70)
        print("ALGORITHMIC TRADING SYSTEM")

        print("=" * 70)
    
    def run_complete_analysis(self, ticker='AAPL', strategies=None):
        """
        Run complete analysis on a single stock with multiple strategies
        
        Parameters:
        -----------
        ticker : str
            Stock ticker to analyze
        strategies : list
            List of strategies to test (default: all)
        
        Returns:
        --------
        dict
            Results for all strategies
        """
        if strategies is None:
            strategies = ['SMA', 'RSI', 'MACD', 'BB', 'HYBRID']
        
        print(f"\n{'=' * 70}")
        print(f"ANALYZING {ticker} WITH MULTIPLE STRATEGIES")
        print('=' * 70)
        
        # Verify data exists
        df = self.collector.get_data_from_db(ticker=ticker)
        if df.empty:
            print(f" No data found for {ticker}")
            print("Please run data collection first:")
            print("  python stock_data_collector.py")
            return None
        
        print(f"\n✓ Data loaded: {len(df)} records from {df['date'].min()} to {df['date'].max()}")
        
        # Test each strategy
        all_results = {}
        
        for strategy in strategies:
            print(f"\n{'─' * 70}")
            print(f"Testing {strategy} Strategy")
            print('─' * 70)
            
            # Run backtest
            results = self.backtester.backtest_single_stock(
                ticker=ticker,
                strategy=strategy
            )
            
            if results:
                # Calculate metrics
                metrics = self.metrics_calc.calculate_all_metrics(
                    portfolio_df=results['portfolio_df'],
                    trades_df=results['trades_df'],
                    initial_capital=config.INITIAL_CAPITAL
                )
                
                results['metrics'] = metrics
                all_results[strategy] = results
                
                # Print summary
                print(f"\n{strategy} Strategy Results:")
                print(f"  Final Value: ${results['final_value']:,.2f}")
                print(f"  Return: {results['total_return_pct']:.2f}%")
                print(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
                print(f"  Max Drawdown: {metrics.get('max_drawdown_pct', 0):.2f}%")
                print(f"  Trades: {results['num_trades']}")
        
        # Compare strategies
        self._compare_strategies(all_results, ticker)
        
        return all_results
    
    def run_portfolio_analysis(self, tickers=None, strategy='HYBRID'):
        """
        Run portfolio analysis with multiple stocks
        
        Parameters:
        -----------
        tickers : list
            List of stock tickers (default from config)
        strategy : str
            Strategy to use
        
        Returns:
        --------
        dict
            Portfolio backtest results
        """
        if tickers is None:
            tickers = config.STOCK_TICKERS
        
        print(f"\n{'=' * 70}")
        print(f"PORTFOLIO ANALYSIS - {strategy} Strategy")
        print(f"Stocks: {', '.join(tickers)}")
        print('=' * 70)
        
        # Run portfolio backtest
        results = self.backtester.backtest_portfolio(
            tickers=tickers,
            strategy=strategy
        )
        
        if results:
            # Calculate metrics
            metrics = self.metrics_calc.calculate_all_metrics(
                portfolio_df=results['portfolio_df'],
                trades_df=results['trades_df'],
                initial_capital=config.INITIAL_CAPITAL
            )
            
            results['metrics'] = metrics
            
            # Print results
            print("\nPORTFOLIO RESULTS:")
            self.backtester.print_results(results)
            self.metrics_calc.print_metrics(metrics)
            
            # Create visualizations
            self.metrics_calc.plot_performance(
                portfolio_df=results['portfolio_df'],
                initial_capital=config.INITIAL_CAPITAL,
                save_path=f'portfolio_{strategy}_performance.png'
            )
        
        return results
    
    def _compare_strategies(self, all_results, ticker):
        """
        Compare performance of different strategies
        
        Parameters:
        -----------
        all_results : dict
            Results from all strategies
        ticker : str
            Stock ticker
        """
        print(f"\n{'=' * 70}")
        print("STRATEGY COMPARISON")
        print('=' * 70)
        
        # Create comparison table
        comparison_data = []
        
        for strategy, results in all_results.items():
            metrics = results['metrics']
            comparison_data.append({
                'Strategy': strategy,
                'Final Value': f"${results['final_value']:,.2f}",
                'Return %': f"{results['total_return_pct']:.2f}%",
                'Sharpe Ratio': f"{metrics.get('sharpe_ratio', 0):.3f}",
                'Max Drawdown': f"{metrics.get('max_drawdown_pct', 0):.2f}%",
                'Trades': results['num_trades'],
                'Win Rate': f"{metrics.get('win_rate', 0):.1f}%"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        print("\n" + comparison_df.to_string(index=False))
        
        # Determine best strategy
        best_return = max(all_results.items(), 
                         key=lambda x: x[1]['total_return_pct'])
        best_sharpe = max(all_results.items(),
                         key=lambda x: x[1]['metrics'].get('sharpe_ratio', 0))
        
        print(f"\n🏆 Best Return: {best_return[0]} ({best_return[1]['total_return_pct']:.2f}%)")
        print(f"🏆 Best Sharpe: {best_sharpe[0]} ({best_sharpe[1]['metrics'].get('sharpe_ratio', 0):.3f})")
        
        # Plot comparison
        self._plot_strategy_comparison(all_results, ticker)
    
    def _plot_strategy_comparison(self, all_results, ticker):
        """Create comparison plots for all strategies"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Portfolio value comparison
        ax1 = axes[0, 0]
        for strategy, results in all_results.items():
            portfolio_df = results['portfolio_df']
            ax1.plot(portfolio_df.index, portfolio_df['portfolio_value'],
                    label=strategy, linewidth=2)
        
        ax1.axhline(y=config.INITIAL_CAPITAL, color='black', 
                   linestyle='--', alpha=0.5, label='Initial')
        ax1.set_title(f'{ticker} - Portfolio Value by Strategy', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Returns comparison
        ax2 = axes[0, 1]
        returns_data = []
        for strategy, results in all_results.items():
            returns_data.append({
                'Strategy': strategy,
                'Return %': results['total_return_pct']
            })
        
        returns_df = pd.DataFrame(returns_data)
        bars = ax2.bar(returns_df['Strategy'], returns_df['Return %'], 
                      color='steelblue', alpha=0.7)
        
        # Color bars based on positive/negative
        for i, bar in enumerate(bars):
            if returns_df.iloc[i]['Return %'] < 0:
                bar.set_color('red')
            else:
                bar.set_color('green')
        
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_title('Total Returns by Strategy', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Return (%)')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Sharpe ratio comparison
        ax3 = axes[1, 0]
        sharpe_data = []
        for strategy, results in all_results.items():
            sharpe_data.append({
                'Strategy': strategy,
                'Sharpe': results['metrics'].get('sharpe_ratio', 0)
            })
        
        sharpe_df = pd.DataFrame(sharpe_data)
        ax3.bar(sharpe_df['Strategy'], sharpe_df['Sharpe'], 
               color='purple', alpha=0.7)
        ax3.axhline(y=1, color='orange', linestyle='--', 
                   alpha=0.7, label='Good (>1)')
        ax3.axhline(y=2, color='green', linestyle='--', 
                   alpha=0.7, label='Very Good (>2)')
        ax3.set_title('Sharpe Ratio by Strategy', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Sharpe Ratio')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Max drawdown comparison
        ax4 = axes[1, 1]
        drawdown_data = []
        for strategy, results in all_results.items():
            drawdown_data.append({
                'Strategy': strategy,
                'Drawdown': results['metrics'].get('max_drawdown_pct', 0)
            })
        
        drawdown_df = pd.DataFrame(drawdown_data)
        ax4.bar(drawdown_df['Strategy'], drawdown_df['Drawdown'], 
               color='red', alpha=0.7)
        ax4.set_title('Maximum Drawdown by Strategy', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Drawdown (%)')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(f'{ticker}_strategy_comparison.png', dpi=300, bbox_inches='tight')
        print(f"\n✓ Comparison plots saved: {ticker}_strategy_comparison.png")
    
    def close(self):
        """Close all connections"""
        self.collector.close()
        self.backtester.close()
        print("\n✓ System closed")


# ==========================================================================
# MAIN EXECUTION
# ==========================================================================

def main():
    """Main execution function"""
    system = AlgorithmicTradingSystem()
    
    print("\n" + "=" * 70)
    print("SELECT ANALYSIS TYPE")
    print("=" * 70)

    
    print("\n" + "=" * 70)
    print("RUNNING FULL DEMO")
    print("=" * 70)
        

    print("\n📊 PART 1: Single Stock Analysis (AAPL)")
    system.run_complete_analysis(ticker='AAPL')
        

    print("\n PART 2: Portfolio Analysis")
    system.run_portfolio_analysis(
        tickers=config.STOCK_TICKERS[:3],  # Use first 3 stocks
        strategy='HYBRID'
        )
        

    
    system.close()
    
    print("\n" + "=" * 70)
    print("✓ ANALYSIS COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  • Performance charts (PNG files)")
    print("  • Strategy comparison plots")
    print("=" * 70)


if __name__ == "__main__":
    main()
