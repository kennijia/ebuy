# 性能仪表板 - 实时显示系统状态
import json
import os
import datetime
from typing import Dict, List
from virtual_trading import VirtualTradingEngine
from strategy_evolution import StrategyEvaluator


def print_header(title: str):
    """打印标题"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_metrics_table(metrics: Dict):
    """打印性能指标表"""
    print("\n📊 关键性能指标 (KPI)")
    print("-" * 70)
    
    rows = [
        ("总收益率", f"{metrics['total_return']:.2%}", 
         "✅" if metrics['total_return'] > 0.10 else "⚠️" if metrics['total_return'] > 0 else "❌"),
        ("胜率", f"{metrics['win_rate']:.2%}", 
         "✅" if metrics['win_rate'] > 0.55 else "⚠️" if metrics['win_rate'] > 0.50 else "❌"),
        ("夏普比率", f"{metrics['sharpe_ratio']:.2f}", 
         "✅" if metrics['sharpe_ratio'] > 1.0 else "⚠️" if metrics['sharpe_ratio'] > 0 else "❌"),
        ("最大回撤", f"{metrics['max_drawdown']:.2%}", 
         "✅" if metrics['max_drawdown'] < 0.10 else "⚠️" if metrics['max_drawdown'] < 0.20 else "❌"),
        ("执行率", f"{metrics['execution_rate']:.2%}", 
         "✅" if metrics['execution_rate'] > 0.80 else "⚠️" if metrics['execution_rate'] > 0.50 else "❌"),
        ("总资产", f"¥{metrics['total_value']:,.0f}", ""),
    ]
    
    for metric, value, status in rows:
        print(f"  {metric:.<15} {value:>15}  {status}")


def print_holdings(engine: VirtualTradingEngine, current_prices: Dict[str, float]):
    """打印持仓情况"""
    print("\n💼 虚拟持仓详情")
    print("-" * 70)
    
    if not engine.current_holdings:
        print("  （无持仓）")
        return
    
    unrealized_pnl = engine.get_unrealized_pnl(current_prices)
    
    print(f"  {'基金代码':<10} {'持仓份数':<12} {'成本价':<8} {'当前价':<8} {'盈亏额':<12} {'盈亏率':<10}")
    print("  " + "-" * 65)
    
    for code, info in unrealized_pnl.items():
        pnl_status = "🟢" if info['pnl'] > 0 else "🔴" if info['pnl'] < 0 else "⚪"
        print(f"  {code:<10} {info['shares']:>10.2f}份 {info['cost_price']:>7.3f} "
              f"{info['current_price']:>7.3f} {info['pnl']:>10.0f}¥ {info['pnl_percent']:>8.2%} {pnl_status}")


def print_signal_summary(engine: VirtualTradingEngine):
    """打印信号摘要"""
    print("\n📈 交易信号统计")
    print("-" * 70)
    
    all_signals = engine.signals_history
    buy_signals = [s for s in all_signals if s.signal_type == "BUY"]
    sell_signals = [s for s in all_signals if s.signal_type == "SELL"]
    executed = [s for s in all_signals if s.execution_date]
    pending = [s for s in all_signals if not s.execution_date]
    
    print(f"  总信号数: {len(all_signals)}")
    print(f"  ├─ BUY信号: {len(buy_signals)}")
    print(f"  ├─ SELL信号: {len(sell_signals)}")
    print(f"  ├─ 已执行: {len(executed)}")
    print(f"  └─ 待执行: {len(pending)}")
    
    # 最近5个信号
    if all_signals:
        print(f"\n  最近5个信号:")
        print(f"  {'日期':<12} {'基金':<8} {'类型':<6} {'强度':<6} {'状态':<10}")
        print("  " + "-" * 50)
        
        for signal in all_signals[-5:]:
            status = "✅已执行" if signal.execution_date else "⏳待执行"
            print(f"  {signal.date:<12} {signal.fund_code:<8} {signal.signal_type:<6} "
                  f"{signal.signal_score:<6.1f} {status:<10}")


def print_cash_status(engine: VirtualTradingEngine, total_value: float):
    """打印现金状态"""
    print("\n💰 资金状态")
    print("-" * 70)
    
    cash_percent = engine.current_cash / total_value if total_value > 0 else 0
    position_percent = 1 - cash_percent
    
    print(f"  现金: ¥{engine.current_cash:>12,.0f}  ({cash_percent:>6.2%})")
    print(f"  持仓: ¥{total_value - engine.current_cash:>12,.0f}  ({position_percent:>6.2%})")
    print(f"  合计: ¥{total_value:>12,.0f}")


def print_recent_logs(log_file: str = "scheduler_execution.json", num_lines: int = 5):
    """打印最近的执行日志"""
    if not os.path.exists(log_file):
        return
    
    print("\n📋 最近执行日志")
    print("-" * 70)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        for log in logs[-num_lines:]:
            status_emoji = "✅" if log['status'] == "成功" else "❌"
            print(f"  {log['timestamp']:<20} {log['job_name']:<20} {status_emoji} {log['status']}")
    except:
        pass


def print_strategy_params(params: Dict):
    """打印策略参数"""
    print("\n⚙️ 当前策略参数")
    print("-" * 70)
    
    important_params = [
        ('rsi_window', 'RSI周期'),
        ('rsi_oversold', 'RSI超卖点'),
        ('rsi_overbought', 'RSI超买点'),
        ('buy_score_threshold', '买入评分门槛'),
        ('profit_take_threshold', '止盈目标'),
        ('loss_cut_threshold', '止损目标'),
        ('dca_loss_threshold', '补仓亏损度'),
    ]
    
    for param_key, param_name in important_params:
        value = params.get(param_key, 'N/A')
        if isinstance(value, float):
            display_value = f"{value:.2%}" if value < 1 else f"{value:.2f}"
        else:
            display_value = str(value)
        print(f"  {param_name}:<20 {display_value:>15}")


def print_evolution_history(evolution_log: str = "strategy_evolution.json", num_records: int = 3):
    """打印参数演进历史"""
    if not os.path.exists(evolution_log):
        return
    
    print("\n📊 策略参数演进历史")
    print("-" * 70)
    
    try:
        with open(evolution_log, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        history = data.get('history', [])
        if not history:
            print("  （无演进记录）")
            return
        
        for timestamp, params in history[-num_records:]:
            print(f"\n  {timestamp}")
            print(f"    RSI超卖点: {params.get('rsi_oversold', 'N/A')}")
            print(f"    止盈目标: {params.get('profit_take_threshold', 'N/A'):.2%}")
            print(f"    止损目标: {params.get('loss_cut_threshold', 'N/A'):.2%}")
    except:
        pass


def generate_full_dashboard(current_prices: Dict[str, float] = None):
    """生成完整仪表板"""
    if current_prices is None:
        current_prices = {}
    
    # 加载数据
    engine = VirtualTradingEngine()
    
    print_header("🤖 自动化交易智能体 - 性能仪表板")
    print(f"更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 计算指标
    metrics = StrategyEvaluator.calculate_metrics(engine, current_prices)
    
    # 打印各部分
    print_metrics_table(metrics)
    print_cash_status(engine, metrics['total_value'])
    print_holdings(engine, current_prices)
    print_signal_summary(engine)
    
    # 加载策略参数
    from strategy_evolution import StrategyEvolver
    evolver = StrategyEvolver()
    current_params = evolver.get_current_params()
    print_strategy_params(current_params)
    
    print_evolution_history()
    print_recent_logs()
    
    # 总结
    print_header("📝 总体评价")
    
    if metrics['total_return'] > 0.15 and metrics['win_rate'] > 0.60:
        print("  ✅ 策略表现优秀，建议继续执行并可考虑增加投入")
    elif metrics['total_return'] > 0 and metrics['win_rate'] > 0.55:
        print("  ✅ 策略表现良好，继续监控")
    elif metrics['total_return'] > -0.10 and metrics['win_rate'] > 0.50:
        print("  ⚠️ 策略表现一般，系统正在优化参数")
    else:
        print("  ❌ 策略需要改进，请检查市场环境或调整参数")
    
    if metrics['max_drawdown'] > 0.25:
        print("  ⚠️ 最大回撤较大，建议降低仓位或增加止损")
    
    if metrics['execution_rate'] < 0.50:
        print("  ⚠️ 信号执行率低，可能是资金不足或市场波动")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # 示例用法
    print("\n自动化交易系统 - 性能仪表板\n")
    print("用法: python dashboard.py [prices_json]")
    print("  例: python dashboard.py '{\"001001\": 1.234}'")
    print()
    
    # 可选：从命令行读取当前价格
    import sys
    current_prices = {}
    
    if len(sys.argv) > 1:
        try:
            current_prices = json.loads(sys.argv[1])
        except:
            print("错误：价格JSON格式不正确")
    
    # 生成仪表板
    generate_full_dashboard(current_prices)
