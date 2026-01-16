# 每日行情监控与信号生成
import datetime
from data_fetcher import fetch_fund_data, fetch_fund_rankings
from strategy import ma_timing_strategy, select_best_funds
import pandas as pd

def check_signals(fund_list):
    """
    检查指定基金列表的买卖信号
    """
    results = []
    end_date = datetime.date.today().strftime('%Y-%m-%d')
    # 取过去一年的数据来计算均线
    start_date = (datetime.date.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    
    print(f"正在分析日期: {end_date} 的信号...")
    
    for fund_code in fund_list:
        try:
            df = fetch_fund_data(fund_code, start_date, end_date)
            if df.empty:
                continue
            
            # 使用均线策略计算
            # 我们只需要最后一行来看当前信号
            df_ma = ma_timing_strategy(df, invest_amount=1000, ma_window=20)
            
            latest_row = df_ma.iloc[-1]
            last_nav = latest_row['nav']
            ma_val = latest_row['ma']
            
            signal = "买入 (定投)" if last_nav > ma_val else "持币观望"
            
            results.append({
                "基金代码": fund_code,
                "最新净值": last_nav,
                "20日均线": f"{ma_val:.4f}",
                "操作建议": signal
            })
        except Exception as e:
            print(f"解析 {fund_code} 出错: {e}")
            
    return pd.DataFrame(results)

if __name__ == "__main__":
    # 1. 自动筛选当前最火的5只股票基金
    print("正在筛选优质基金...")
    rankings = fetch_fund_rankings("股票型")
    best_5 = select_best_funds(rankings, top_n=5)
    watch_list = best_5['基金代码'].tolist()
    
    # 2. 加上你手动关注的基金
    # watch_list += ["513500"] 
    
    signals = check_signals(watch_list)
    print("\n--- 今日实盘操作建议 ---")
    if not signals.empty:
        print(signals.to_markdown(index=False))
    else:
        print("未获取到有效信号。")
