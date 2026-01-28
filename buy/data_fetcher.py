# 用于获取基金数据
import pandas as pd
import akshare as ak
import requests
import json
import re

def fetch_fund_data(fund_code: str, start: str, end: str) -> pd.DataFrame:
    """获取基金历史净值"""
    df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
    df['净值日期'] = pd.to_datetime(df['净值日期'])
    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)
    df = df[(df['净值日期'] >= start_dt) & (df['净值日期'] <= end_dt)]
    df = df.rename(columns={'净值日期': 'date', '单位净值': 'nav'})
    df = df[['date', 'nav']].reset_index(drop=True)
    return df

def fetch_fund_rankings(symbol: str = "股票型") -> pd.DataFrame:
    """
    获取基金排行榜
    symbol: "全部", "股票型", "混合型", "债券型", "指数型", "QDII", "LOF", "FOF"
    """
    df = ak.fund_open_fund_rank_em(symbol=symbol)
    return df

def fetch_index_valuation(symbol: str = "沪深300") -> pd.DataFrame:
    """
    获取主流指数估值数据
    """
    # 获取指数估值数据
    df = ak.index_value_hist_funddb(symbol=symbol, indicator="等权市盈率")
    return df

def fetch_realtime_estimation(fund_list: list) -> pd.DataFrame:
    """
    高效获取指定基金列表的实时估值 (极速版)
    """
    results = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for code in fund_list:
        try:
            url = f"http://fundgz.1234567.com.cn/js/{code}.js"
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                match = re.search(r'jsonpgz\((.*)\);', response.text)
                if match:
                    data = json.loads(match.group(1))
                    results.append({
                        "基金代码": data['fundcode'],
                        "基金名称": data['name'],
                        "估算涨跌幅": data['gszzl']
                    })
        except Exception:
            pass
    return pd.DataFrame(results)

if __name__ == "__main__":
    # 示例：测试获取某只基金的历史净值
    fund_code = "015145"  # 替换为实际基金代码
    start = "2025-12-08"
    end = "2026-1-6"
    df = fetch_fund_data(fund_code, start, end)
    # 显示前5行
    # print(df.head()) 
    print(df)