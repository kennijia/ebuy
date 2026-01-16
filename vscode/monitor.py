# 每日行情监控与信号生成
import datetime
from data_fetcher import fetch_fund_data, fetch_fund_rankings, fetch_realtime_estimation
from strategy import ma_timing_strategy, select_best_funds, composite_signal_strategy
import pandas as pd

def check_signals(fund_list):
    """
    检查指定基金列表的买卖信号 (结合历史深度分析与今日实时估值)
    """
    results = []
    end_date = datetime.date.today().strftime('%Y-%m-%d')
    start_date = (datetime.date.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    
    print(f"正在进行深度因子分析 (历史参考日期: {end_date})...")
    
    # 获实时估值数据
    print("1/2: 正在获取全市场实时估值数据 (请稍候)...")
    rt_df = fetch_realtime_estimation(fund_list)
    
    print(f"2/2: 开始分析具体基金 (共 {len(fund_list)} 只)...")
    for fund_code in fund_list:
        try:
            print(f"   -> 正在分析 {fund_code} ...", end="\r")
            df = fetch_fund_data(fund_code, start_date, end_date)
            if df.empty or len(df) < 30:
                continue
            
            # 综合历史信号
            suggestion, score, rsi = composite_signal_strategy(df)
            
            # 融合实时估值
            est_change = "N/A"
            if not rt_df.empty:
                matches = rt_df[rt_df['基金代码'] == fund_code]
                if not matches.empty:
                    val = matches.iloc[0]['估算涨跌幅']
                    est_change = f"{val}%"
                    # 如果今日大跌且历史处于低位，评分增加
                    try:
                        if float(val) < -1.5 and rsi < 40:
                            score += 1
                            suggestion = "大跌捡漏机会"
                    except: pass

            latest_row = df.iloc[-1]
            last_nav = latest_row['nav']
            
            results.append({
                "基金代码": fund_code,
                "最新净值": last_nav,
                "今日估值": est_change,
                "RSI(14)": f"{rsi:.1f}",
                "综合评分": score,
                "操作建议": suggestion
            })
        except Exception as e:
            print(f"解析 {fund_code} 出错: {e}")
            
    return pd.DataFrame(results)

if __name__ == "__main__":
    # 1. 扩大筛选池，涵盖多种类型，确保不遗漏
    print("正在从全市场挖掘潜力基金...")
    
    types = ["股票型", "指数型", "混合型"]
    watch_list = []
    
    for t in types:
        print(f"   -> 正在扫描 {t} 排行榜...")
        rankings = fetch_fund_rankings(t)
        # 每种类型选出前15名进入“海选池”
        best_of_type = select_best_funds(rankings, top_n=15)
        watch_list.extend(best_of_type['基金代码'].tolist())
    
    # 去重
    watch_list = list(set(watch_list))
    print(f"海选完成：共有 {len(watch_list)} 只基金进入深度分析池。")
    
    # 2. 进行深度信号分析
    signals = check_signals(watch_list)
    
    print("\n" + "="*50)
    print("--- 深度筛选报告：值得关注的捡漏机会 ---")
    if not signals.empty:
        # 仅展示评分较高的（评分 > 1）或者极低位的（RSI < 35）
        recommendations = signals[(signals['综合评分'] >= 2) | (signals['RSI(14)'].astype(float) < 35)]
        
        if not recommendations.empty:
            print(recommendations.sort_values('综合评分', ascending=False).to_markdown(index=False))
        else:
            print("当前市场整体水位较高，暂无深度捡漏机会。")
            print("以下是今日参与分析的所有基金概况 (前10只):")
            print(signals.head(10).to_markdown(index=False))
    else:
        print("未获取到有效信号。")
    print("="*50)
