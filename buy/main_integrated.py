# 修改后的main.py - 集成自动化交易系统
"""
这是一个完整的示例，展示如何将自动化交易系统集成到你现有的程序中
"""

from backtest import run_backtest
from data_fetcher import fetch_fund_rankings, fetch_index_valuation
from strategy import select_best_funds
from monitor import check_signals, load_holdings_info

# 新增：导入自动化模块
from integration import MonitorIntegration, setup_auto_trading_system
from auto_agent import create_auto_agent
from scheduler import DailyScheduler
from virtual_trading import VirtualTradingEngine
from strategy_evolution import AdaptiveStrategyOptimizer

import json
import datetime


def get_fund_list():
    """获取要监控的基金列表"""
    # 这是一个示例列表，请替换为你的实际基金列表
    return [
        '001001',  # 例子
        '001002',
        # ... 添加你的其他基金代码
    ]


def run_traditional_monitor():
    """运行传统的monitor逻辑"""
    print("\n" + "="*60)
    print("📊 运行传统Monitor程序...")
    print("="*60)
    
    fund_list = get_fund_list()
    held_info = load_holdings_info()
    
    # 调用你现有的check_signals函数
    results = check_signals(fund_list, held_info)
    
    return results


def convert_monitor_results_to_signals(results):
    """
    将monitor.py的结果转换为标准信号格式
    
    兼容DataFrame / list[dict] / dict / JSON字符串
    """
    def normalize_input(raw):
        if raw is None:
            return []
        # DataFrame -> records
        if hasattr(raw, "to_dict"):
            try:
                return raw.to_dict(orient="records")
            except Exception:
                return []
        # JSON字符串
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                return normalize_input(parsed)
            except Exception:
                return []
        # dict
        if isinstance(raw, dict):
            if "signals" in raw and isinstance(raw["signals"], list):
                return raw["signals"]
            return [raw]
        # list
        if isinstance(raw, list):
            return raw
        return []

    def infer_signal_type(suggestion_text, score_value):
        text = str(suggestion_text or "")
        if any(k in text for k in ["止盈", "减仓", "警戒", "卖", "风险", "超买"]):
            return "SELL"
        if any(k in text for k in ["买", "补仓", "捡漏", "趋势", "加仓", "抄底"]):
            return "BUY"
        # 根据评分兜底
        try:
            if float(score_value) >= 2:
                return "BUY"
        except Exception:
            pass
        return "HOLD"

    def parse_suggested_amount(raw_amount):
        if isinstance(raw_amount, (int, float)):
            return float(raw_amount)
        text = str(raw_amount or "")
        if "积极" in text:
            return 3.0
        if "稳健" in text:
            return 1.0
        if "轻仓" in text:
            return 0.5
        return 0.0

    signals = []
    records = normalize_input(results)

    for result in records:
        if not isinstance(result, dict):
            continue

        # 兼容monitor.py DataFrame字段
        fund_code = result.get('基金代码') or result.get('fund_code') or result.get('code')
        fund_name = result.get('基金名称') or result.get('基金简称') or result.get('fund_name') or result.get('name')
        suggestion = result.get('操作建议') or result.get('建议') or result.get('signal')
        score = result.get('综合评分') if '综合评分' in result else result.get('评分', 0)
        current_price = result.get('最新净值') or result.get('单位净值') or result.get('current_price', 0)
        suggested_amount = result.get('建议仓位') or result.get('建议买入', 0)

        signal = {
            'fund_code': fund_code,
            'fund_name': fund_name or "",
            'signal': infer_signal_type(suggestion, score),
            'score': score or 0,
            'current_price': current_price or 0,
            'suggested_amount': parse_suggested_amount(suggested_amount),
            'reason': suggestion or result.get('原因') or result.get('reason', '')
        }

        if signal['fund_code']:
            signals.append(signal)

    return {
        'date': datetime.date.today().strftime('%Y-%m-%d'),
        'signals': signals
    }


def print_agent_report(response):
    """打印智能体的报告"""
    print("\n" + "="*60)
    print("🤖 自动化智能体报告")
    print("="*60)
    
    # 性能指标
    metrics = response['performance_dashboard']['metrics']
    print(f"\n📈 性能指标:")
    print(f"   💰 总收益率: {metrics['total_return']:>8.2%}")
    print(f"   🎯 胜率: {metrics['win_rate']:>12.2%}")
    print(f"   ⚡ 夏普比率: {metrics['sharpe_ratio']:>9.2f}")
    print(f"   📉 最大回撤: {metrics['max_drawdown']:>9.2%}")
    print(f"   📊 执行率: {metrics['execution_rate']:>11.2%}")
    
    # 持仓信息
    print(f"\n💼 虚拟持仓:")
    print(f"   现金: ¥{metrics['current_cash']:,.2f}")
    print(f"   总资产: ¥{metrics['total_value']:,.2f}")
    
    # 智能体建议
    print(f"\n💡 智能体建议:")
    for action in response['next_actions']:
        print(f"   ✓ {action}")
    
    # 新的策略参数
    print(f"\n⚙️ 最新策略参数:")
    new_params = response['optimization_result']['new_params']
    for key, value in new_params.items():
        print(f"   {key}: {value}")


def run_auto_trading_system_once():
    """
    运行一次完整的自动化交易循环
    （适合每日定时执行）
    """
    print("\n" + "="*60)
    print("🚀 启动自动化交易系统 (单次执行)")
    print("="*60)
    
    try:
        # 1. 创建智能体
        agent = create_auto_agent(initial_cash=100000)
        integration = MonitorIntegration(agent)
        
        # 2. 运行传统monitor逻辑
        monitor_results = run_traditional_monitor()
        
        # 3. 转换格式
        signals = convert_monitor_results_to_signals(monitor_results)
        
        # 4. 通过集成器处理
        response = integration.process_monitor_results(signals)
        
        # 5. 打印报告
        print_agent_report(response)
        
        # 6. 保存结果
        save_daily_results(response)
        
        print("\n✅ 自动化流程完成")
        return response
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_auto_trading_system_continuous():
    """
    启动自动化交易系统（连续运行）
    系统会在每天14:30自动运行
    """
    print("\n" + "="*60)
    print("🚀 启动自动化交易系统 (连续模式)")
    print("="*60)
    
    # 创建智能体
    agent = create_auto_agent(initial_cash=100000)
    
    # 定义每日任务
    def daily_task():
        return run_auto_trading_system_once()
    
    # 设置定时任务
    scheduler = DailyScheduler()
    scheduler.schedule_daily_job(
        job_name="每日14:30自动化交易",
        time_str="14:30",
        job_func=daily_task
    )
    
    # 启动调度器
    print("✓ 系统已启动，等待14:30自动执行...")
    scheduler.start()  # 这会一直阻塞


def save_daily_results(response):
    """保存每日结果"""
    filename = f"daily_results_{datetime.date.today().strftime('%Y%m%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=2)
    print(f"✓ 结果已保存: {filename}")


def view_virtual_portfolio():
    """查看虚拟账户状态"""
    print("\n" + "="*60)
    print("📊 虚拟账户状态")
    print("="*60)
    
    engine = VirtualTradingEngine()
    
    print(f"\n持仓:")
    for code, shares in engine.current_holdings.items():
        print(f"   {code}: {shares:.2f}份")
    
    print(f"\n现金: ¥{engine.current_cash:,.2f}")
    
    print(f"\n已执行信号数: {len([s for s in engine.signals_history if s.execution_date])}")
    print(f"待执行信号数: {len([s for s in engine.signals_history if not s.execution_date])}")


def view_strategy_evolution():
    """查看策略演进历史"""
    print("\n" + "="*60)
    print("📈 策略参数演进历史")
    print("="*60)
    
    evolver = AdaptiveStrategyOptimizer().evolver
    
    for record in evolver.get_params_evolution()[-5:]:  # 显示最近5次
        print(f"\n时间: {record['timestamp']}")
        params = record['params']
        print(f"   RSI超卖: {params['rsi_oversold']}")
        print(f"   RSI超买: {params['rsi_overbought']}")
        print(f"   止盈: {params['profit_take_threshold']:.1%}")
        print(f"   止损: {params['loss_cut_threshold']:.1%}")


# 主程序
if __name__ == "__main__":
    import sys
    
    print("\n" 
          "╔════════════════════════════════════════════════════════════╗\n"
          "║  自动化量化交易智能体系统                                  ║\n"
          "║  Automated Quantitative Trading Agent System                ║\n"
          "╚════════════════════════════════════════════════════════════╝\n")
    
    # 菜单选项
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        print("使用方法:")
        print("  python main.py once      - 运行一次自动化流程")
        print("  python main.py continuous- 启动连续运行（14:30自动执行）")
        print("  python main.py portfolio - 查看虚拟账户")
        print("  python main.py evolution - 查看策略演进")
        print("  python main.py traditional - 运行传统monitor")
        print("")
        command = input("请选择操作 (once/continuous/portfolio/evolution/traditional): ").strip()
    
    if command == "once":
        # 运行一次自动化流程
        response = run_auto_trading_system_once()
    
    elif command == "continuous":
        # 启动连续运行
        run_auto_trading_system_continuous()
    
    elif command == "portfolio":
        # 查看虚拟账户
        view_virtual_portfolio()
    
    elif command == "evolution":
        # 查看策略演进
        view_strategy_evolution()
    
    elif command == "traditional":
        # 运行传统的monitor
        results = run_traditional_monitor()
        print("\n结果:")
        if hasattr(results, 'to_dict'):
            # DataFrame -> dict
            print(json.dumps(results.to_dict(orient='records'), ensure_ascii=False, indent=2))
        else:
            print(json.dumps(results, ensure_ascii=False, indent=2))
    
    else:
        # 默认：运行一次自动化流程
        print(f"未知命令: {command}")
        print("使用默认模式运行一次...")
        response = run_auto_trading_system_once()
