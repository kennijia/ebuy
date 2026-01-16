# 回测系统框架
import pandas as pd
from strategy import simple_dca_strategy, ma_timing_strategy
from data_fetcher import fetch_fund_data

def run_backtest(fund_code: str, start: str, end: str, invest_amount: float, strategy_type: str = 'simple'):
    fund_data = fetch_fund_data(fund_code, start, end)
    
    if strategy_type == 'simple':
        results = simple_dca_strategy(fund_data, invest_amount)
    elif strategy_type == 'ma':
        results = ma_timing_strategy(fund_data, invest_amount)
    else:
        print(f"未知策略类型: {strategy_type}")
        return

    # print(results)
    # 可根据需要输出收益率等汇总信息
    if not results.empty:
        print(f"策略类型: {strategy_type}")
        print(f"累计投入: {results['total_invest'].iloc[-1]:.2f}")
        print(f"期末市值: {results['market_value'].iloc[-1]:.2f}")
        print(f"总收益率: {results['return'].iloc[-1]*100:.2f}%")

if __name__ == "__main__":
    fund_code = "513500"  # 纳指100ETF
    start = "2024-01-01"
    end = "2024-12-31"
    invest_amount = 1000.0
    run_backtest(fund_code, start, end, invest_amount, strategy_type='ma')
