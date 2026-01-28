# 每日行情监控与信号生成
import datetime
import json
import os
import re  # 引入正则模块
from data_fetcher import fetch_fund_data, fetch_fund_rankings, fetch_realtime_estimation
from strategy import ma_timing_strategy, select_best_funds, composite_signal_strategy
import pandas as pd

# ==========================================
# 📊 量化策略模型配置说明 (Quant Model Config)
# ------------------------------------------
# 核心逻辑: RSI均值回归 + 趋势跟踪 + 盈亏管理
#
# [1] 市场温度计 (RSI-14):
#     - 🧊 冰点区 (RSI < 30): 市场极度悲观 -> 潜在买点
#     - 🔥 沸点区 (RSI > 75): 市场极度贪婪 -> 潜在卖点
#
# [2] 买入信号 (Score评分制):
#     - 基础分: RSI低位、均线支撑等技术面好转
#     - 加分项: "大跌捡漏" (今日预估跌幅 > 1.5% 且 RSI < 40)
#     - 仓位输出: 3分=积极(2-3份), 2分=稳健(1份), 1分=轻仓(0.5份)
#
# [3] 卖出/止盈信号 (风控):
#     - 绝对止盈: 持仓盈利 > 10% 且 RSI > 70 (技术面过热) -> 落袋为安
#     - 风险警戒: RSI > 75 (严重超买) -> 无论盈亏，建议减仓避险
#     - 破位止损: 评分极低(<2) 且 今日大跌(<-2%) -> 防止深套
#
# [4] 补仓/摊薄策略 (DCA):
#     - 触发条件: 持仓亏损 > 10% 且 出现买入信号(Score>=2)
#     - 目的: 在低位拉低持仓均价，而非盲目补仓
# ==========================================

POSITIONS_FILE = "my_positions.json"
POSITIONS_TXT = "my_positions.txt"

def load_holdings_info():
    """
    读取持仓详细信息：代码、持仓成本(可选)、持有份额(可选)
    返回: dict { 'code': {'cost': float, 'amount': float}, ... }
    """
    holdings_map = {}
    
    # helper: 解析一行文本
    def parse_line(text):
        # 提取六位代码
        code_match = re.search(r'\d{6}', text)
        if not code_match: return
        code = code_match.group()
        
        # 尝试提取 "成本:1.234" 或 "均价 1.234"
        cost = 0.0
        cost_match = re.search(r'(?:成本|均价)[:\s]*(\d+\.?\d*)', text)
        if cost_match:
            cost = float(cost_match.group(1))
            
        holdings_map[code] = {'cost': cost}

    # 1. 优先尝试读取 TXT
    if os.path.exists(POSITIONS_TXT):
        try:
            with open(POSITIONS_TXT, 'r', encoding='utf-8') as f:
                for line in f:
                    parse_line(line)
            if holdings_map:
                return holdings_map
        except: pass

    # 2. 其次尝试读取 JSON
    if os.path.exists(POSITIONS_FILE):
        try:
            with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 兼容旧格式 list ['001', '002']
                raw_list = data.get("holdings", []) if isinstance(data, dict) else data
                if isinstance(raw_list, list):
                    for item in raw_list:
                        if isinstance(item, str):
                            holdings_map[item] = {'cost': 0.0}
                        elif isinstance(item, dict) and 'code' in item:
                            holdings_map[item['code']] = {'cost': item.get('cost', 0.0)}
                return holdings_map
        except: pass
    
    return {}

def check_signals(fund_list, held_info=None):
    """
    检查指定基金列表的买卖信号
    held_info: dict {code: {cost: ...}} 用于计算盈亏给出针对性建议
    """
    if held_info is None: held_info = {}
    held_codes = list(held_info.keys())
    
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
            
            # === 新增: 趋势追踪策略 (防止踏空白银等主升浪) ===
            # 计算简单均线
            if len(df) >= 20: # 确保数据够长
                ma5 = df['nav'].rolling(window=5).mean().iloc[-1]
                ma10 = df['nav'].rolling(window=10).mean().iloc[-1]
                ma20 = df['nav'].rolling(window=20).mean().iloc[-1]
                curr_nav = df['nav'].iloc[-1]
                
                # 判定: 多头排列 (均线向上发散)
                # 价格 > 20日线 说明大趋势向上
                if curr_nav > ma20 and ma5 > ma10 > ma20:
                    # 如果 RSI 处于 50-70 的强势区间 (还没过热)，给予“追涨分”
                    # 原有策略只做反转(低位买)，这里补充趋势(高位买)
                    if 50 <= rsi <= 73: 
                        score += 2   # 既然是确认的趋势，直接给2分
                        # 如果原来是观望，现在改为追涨
                        if "持仓" not in suggestion and score >= 2:
                            suggestion = "🔥 趋势主升浪(追涨)"
            # ===============================================

            # 融合实时估值
            est_change = "N/A"
            est_val = 0.0
            fund_name = "-"

            if not rt_df.empty:
                matches = rt_df[rt_df['基金代码'] == fund_code]
                if not matches.empty:
                    val = matches.iloc[0]['估算涨跌幅']
                    # 获取基金名称
                    if '基金名称' in matches.columns:
                        fund_name = matches.iloc[0]['基金名称']
                    
                    est_change = f"{val}%"
                    try: 
                        est_val = float(val)
                    except: pass
                    # 如果今日大跌且历史处于低位，评分增加
                    try:
                        if float(val) < -1.5 and rsi < 40:
                            score += 1
                            suggestion = "大跌捡漏机会"
                    except: pass
            
            # 尝试兜底获取名称 (如果实时数据里没有)
            if fund_name == "-" and not df.empty and 'name' in df.columns:
                 # 假设fetch_fund_data返回的df可能包含name列(具体取决于API实现，这里做一种可能性兼容)
                 # 如果API没返回name，这行不起作用
                 pass
                 
            latest_row = df.iloc[-1]
            last_nav = latest_row['nav']
            
            # === 优化逻辑: 买多少? 卖不卖? ===
            is_held = fund_code in held_codes
            buy_amt = "-"
            profit_pct_str = "-"
            
            # 针对持仓: 检查卖出信号
            if is_held:
                # 计算持仓收益率
                cost = held_info[fund_code].get('cost', 0.0)
                profit_pct = 0.0
                if cost > 0:
                    # 如果有今日估值，用估值算更准，否则用昨日净值
                    current_val = last_nav * (1 + est_val/100) if (est_val != 0) else last_nav
                    profit_pct = (current_val - cost) / cost * 100
                    profit_pct_str = f"{profit_pct:+.2f}%"

                # 基础建议
                reason = ""
                if rsi > 75: 
                    reason = "严重超买"
                    score = -1 
                elif rsi > 70 and est_val > 0.5:
                    reason = "高位震荡"
                elif score < 2 and est_val < -2.0:
                    reason = "破位大跌"
                elif suggestion == "大跌捡漏机会":
                    reason = "补仓机会"

                # 结合盈亏修正建议
                if cost > 0:
                    if profit_pct > 10 and rsi > 70:
                        suggestion = f"💰 止盈落袋 (盈{profit_pct:.1f}%)"
                    elif profit_pct < -10 and reason == "补仓机会":
                        suggestion = f"📉 深跌摊薄 (亏{profit_pct:.1f}%)"
                    elif profit_pct < -15:
                         suggestion = f"🚑 深度被套 (亏{profit_pct:.1f}%)"
                    elif reason:
                        suggestion = f"持仓({reason})"
                    else:
                        suggestion = "持仓观望"
                else:
                    # 无成本数据时的默认逻辑
                    if reason == "严重超买": suggestion = "⚠️ 建议止盈"
                    elif reason == "高位震荡": suggestion = "⚠️ 考虑减仓"
                    elif reason == "破位大跌": suggestion = "🛑 警戒"
                    elif reason == "补仓机会": suggestion = "💰 补仓"
                    else: suggestion = "持仓"
            
            # 针对新机会: 给出仓位建议
            else:
                if score >= 3:
                    buy_amt = "积极 (2-3份)" # 重仓
                elif score >= 2:
                    buy_amt = "稳健 (1份)"   # 标准
                elif score >= 1:
                    buy_amt = "轻仓 (0.5份)" # 试探
            
            results.append({
                "基金代码": fund_code,
                "基金名称": fund_name,
                "类型": "★持仓" if is_held else "观察",
                "最新净值": last_nav,
                "持仓成本": held_info.get(fund_code, {}).get('cost', 0) if is_held else "-", 
                "预估盈亏": profit_pct_str,
                "今日估值": est_change,
                "RSI(14)": f"{rsi:.1f}",
                "综合评分": score,
                "操作建议": suggestion,
                "建议仓位": buy_amt
            })
        except Exception as e:
            print(f"解析 {fund_code} 出错: {e}")
            
    return pd.DataFrame(results)

if __name__ == "__main__":
    # 0. 读取持仓
    my_holdings_map = load_holdings_info()
    my_holdings_codes = list(my_holdings_map.keys())
    print(f"当前持仓监控: {len(my_holdings_codes)} 只基金")

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
    watch_list = list(set(watch_list + my_holdings_codes))
    print(f"海选完成：共有 {len(watch_list)} 只基金进入深度分析池。")
    
    # 2. 进行深度信号分析
    signals = check_signals(watch_list, held_info=my_holdings_map)
    
    print("\n" + "="*50)
    print("--- 每日资金体检报告 ---")
    if not signals.empty:
        # 分组数据
        held_df = signals[signals['类型'] == "★持仓"]
        # 市场机会：排除持仓，且分数较高或者RSI超跌的
        market_opps = signals[(signals['类型'] == "观察") & ((signals['综合评分'] >= 1) | (signals['RSI(14)'].astype(float) < 35))]
        
        # === 报告 1: 持仓根据地分析 ===
        print("\n" + "#"*40)
        print("📋 REPORT 1: 我的持仓操作建议 (卖出/补仓)")
        print("#"*40)
        
        if not held_df.empty:
            # 动态调整显示的列
            cols = ['基金代码', '基金名称', '今日估值', 'RSI(14)', '综合评分', '操作建议']
            if any(held_df['持仓成本'] != "-"): # 如果有成本数据才显示
                cols.extend(['持仓成本', '预估盈亏'])
            print(held_df[cols].sort_values('综合评分').to_markdown(index=False))
            print(f"\n>> 持仓小结: 当前监控 {len(held_df)} 只持仓。请重点关注“止盈”或“深跌”提示。")
        else:
            print("（暂无持仓信息，请在 my_positions.txt 中添加）")

        # === 报告 2: 全市场机会扫描 ===
        print("\n\n" + "#"*40)
        print("🔭 REPORT 2: 市场捡漏推荐 (新机会挖掘)")
        print("#"*40)
        
        if not market_opps.empty:
            print(market_opps[['基金代码', '基金名称', '今日估值', 'RSI(14)', '综合评分', '操作建议', '建议仓位']].sort_values('综合评分', ascending=False).head(10).to_markdown(index=False))
            print(f"\n>> 市场小结: 已为您从全市场筛选出 {len(market_opps)} 个潜在机会，以上是 Top 10。")
        else:
            print("当前市场情绪平静，未发现高胜率的抄底机会，建议观望。")
            if held_df.empty:
                print("（显示前10条普通数据供参考）")
                print(signals.head(10).to_markdown(index=False))
    else:
        print("未获取到有效信号。")
    print("="*50)
