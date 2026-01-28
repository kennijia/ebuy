# 投资策略库
import pandas as pd
import numpy as np

def simple_dca_strategy(fund_data: pd.DataFrame, invest_amount: float):
    """
    简单定投策略：每期定投固定金额
    fund_data: 包含 date, nav 的 DataFrame,按时间升序排列
    invest_amount: 每期定投金额
    返回:DataFrame,包含每期日期、买入份额、累计份额、累计投入、当前市值、收益率
    """
    fund_data = fund_data.sort_values('date').reset_index(drop=True)
    shares = []
    total_shares = 0
    total_invest = 0
    market_values = []
    returns = []
    for i, row in fund_data.iterrows():
        nav = row['nav']
        buy_share = invest_amount / nav
        total_shares += buy_share
        total_invest += invest_amount
        market_value = total_shares * nav
        ret = (market_value - total_invest) / total_invest if total_invest > 0 else 0
        shares.append(total_shares)
        market_values.append(market_value)
        returns.append(ret)
    result = fund_data.copy()
    result['total_shares'] = shares
    result['total_invest'] = invest_amount * (result.index + 1)
    result['market_value'] = market_values
    result['return'] = returns
    return result

def ma_timing_strategy(fund_data: pd.DataFrame, invest_amount: float, ma_window: int = 20):
    """
    均线择时定投：价格 > MA 时定投，否则观望
    """
    df = fund_data.sort_values('date').copy().reset_index(drop=True)
    df['ma'] = df['nav'].rolling(window=ma_window).mean()
    shares_list = []
    total_shares = 0
    total_invest_list = []
    total_invest = 0
    market_values = []
    returns = []
    
    for i, row in df.iterrows():
        nav = row['nav']
        ma = row['ma']
        
        # 价格 > 均线时进行定投，若 ma 只有 NaN 则观望
        if not pd.isna(ma) and nav > ma:
            buy_share = invest_amount / nav
            total_shares += buy_share
            total_invest += invest_amount
            
        current_value = total_shares * nav
        ret = (current_value - total_invest) / total_invest if total_invest > 0 else 0
        
        shares_list.append(total_shares)
        total_invest_list.append(total_invest)
        market_values.append(current_value)
        returns.append(ret)
        
    df['total_shares'] = shares_list
    df['total_invest'] = total_invest_list
    df['market_value'] = market_values
    df['return'] = returns
    return df

def calculate_rsi(df: pd.DataFrame, window: int = 14):
    """
    计算RSI指标
    """
    delta = df['nav'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

def calculate_bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: int = 2):
    """
    计算布林带
    """
    df['bb_mid'] = df['nav'].rolling(window=window).mean()
    df['bb_std'] = df['nav'].rolling(window=window).std()
    df['bb_upper'] = df['bb_mid'] + (df['bb_std'] * num_std)
    df['bb_lower'] = df['bb_mid'] - (df['bb_std'] * num_std)
    return df

def composite_signal_strategy(df: pd.DataFrame):
    """
    综合信号策略：结合MA、RSI和布林带
    返回带有建议的最新一行
    """
    df = df.sort_values('date').copy()
    df['ma20'] = df['nav'].rolling(window=20).mean()
    df = calculate_rsi(df)
    df = calculate_bollinger_bands(df)
    
    # 最近一天的数据
    latest = df.iloc[-1]
    nav = latest['nav']
    rsi = latest['rsi']
    bb_lower = latest['bb_lower']
    ma20 = latest['ma20']

    score = 0
    # 趋势分析
    if nav > ma20: score += 1
    # 超卖分析
    if rsi < 30: score += 2  # 极度超卖，机会大
    elif rsi < 40: score += 1
    # 支撑位分析
    if nav < bb_lower: score += 2 # 跌破布林下轨，反弹概率大
    
    # 风险提示
    if rsi > 70: score -= 2 # 超买风险
    
    suggestion = "观望"
    if score >= 3:
        suggestion = "强烈推荐买入"
    elif score >= 1:
        suggestion = "建议买入/定投"
    elif score <= -1:
        suggestion = "建议卖出/减仓"
        
    return suggestion, score, rsi

def select_best_funds(rankings_df: pd.DataFrame, top_n: int = 10):
    """
    根据收益率和稳定性综合筛选优质基金 (Smart Select)
    """
    try:
        df = rankings_df.copy()
        # 转换收益率列为数值
        cols_to_fix = ['近1年', '近6月', '近3月', '近1月', '日增长率']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # 核心逻辑：加权得分 (避开只在某个时间点爆发的基金)
        # 1年权重40%, 6月30%, 3月20%, 1月10%
        df['rank_score'] = (df['近1年'] * 0.4 + 
                            df['近6月'] * 0.3 + 
                            df['近3月'] * 0.2 + 
                            df['近1月'] * 0.1)
        
        # 排除掉虽然涨得好，但在近3年表现极差（说明是周期性或投机）的逻辑可以以后加
        return df.sort_values('rank_score', ascending=False).head(top_n)
    except Exception as e:
        print(f"筛选筛选出错: {e}")
        return rankings_df.head(top_n)
