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

def select_best_funds(rankings_df: pd.DataFrame, top_n: int = 10):
    """
    根据收益率筛选优质基金
    """
    try:
        # 尝试根据'近1年'收益率排序
        for col in ['近1年', '近6月', '近3月', '日增长率']:
            if col in rankings_df.columns:
                rankings_df[col] = pd.to_numeric(rankings_df[col], errors='coerce')
                return rankings_df.sort_values(col, ascending=False).head(top_n)
        return rankings_df.head(top_n)
    except Exception:
        return rankings_df.head(top_n)
