# 项目入口
from backtest import run_backtest
from data_fetcher import fetch_fund_rankings, fetch_index_valuation
from strategy import select_best_funds

if __name__ == "__main__":
    # 1. 示例：获取基金排行并筛选
    print("--- 基金排行筛选 (前5名股票型) ---")
    rankings = fetch_fund_rankings(symbol="股票型")
    if rankings is not None and not rankings.empty:
        best_funds = select_best_funds(rankings, top_n=5)
        print(best_funds[['基金代码', '基金简称', '单位净值', '近1年']])

    # 2. 示例：获取指数估值
    print("\n--- 指数估值数据 ---")
    valuation = fetch_index_valuation(symbol="沪深300")
    if valuation is not None and not valuation.empty:
        print(valuation.tail())

    # 3. 示例：回测定投策略
    print("\n--- 基金定投回测 ---")
    fund_code = "000001"  # 华夏成长混合
    start = "2023-01-01"
    end = "2023-12-31"
    invest_amount = 1000.0
    
    print("运行简单定投策略:")
    run_backtest(fund_code, start, end, invest_amount, strategy_type='simple')
    
    print("\n运行均线择时策略:")
    run_backtest(fund_code, start, end, invest_amount, strategy_type='ma')
