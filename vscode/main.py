# 项目入口
from backtest import run_backtest
from data_fetcher import fetch_fund_rankings, fetch_index_valuation
from strategy import select_best_funds

if __name__ == "__main__":
    # 1. 示例：多维度基金筛选
    print("--- 基金深度筛选 (尝试寻找高潜力基金) ---")
    # 建议不仅看股票型，也可以看指数型，因为场外长线往往指数更稳
    rankings = fetch_fund_rankings(symbol="指数型") 
    if rankings is not None and not rankings.empty:
        best_funds = select_best_funds(rankings, top_n=5)
        # 展示更多维度帮助决策
        print(best_funds[['基金代码', '基金简称', '单位净值', '日增长率', '近1年', '近3月']])

    # 2. 示例：大盘温度计 (估值逻辑)
    # 提高赚钱概率的核心：在指数低估时多买，高估时少买或不买
    print("\n--- 市场大盘估值 (定投核心参考) ---")
    val_indices = ["沪深300", "创业板指", "中证500"]
    for idx_name in val_indices:
        try:
            val_df = fetch_index_valuation(symbol=idx_name)
            if not val_df.empty:
                latest = val_df.iloc[-1]
                print(f"{idx_name}: PE={latest['估值']}, 历史分位数={latest['分位数']}%")
        except: pass

    # 3. 示例：回测
    print("\n--- 策略有效性验证 ---")
    # ... 原有回测逻辑 ...
