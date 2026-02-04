# 测试脚本 - 演示自动化交易系统的工作流程
import json
import datetime
from virtual_trading import VirtualTradingEngine, TradeSignal
from strategy_evolution import StrategyEvaluator, StrategyEvolver
from auto_agent import AutoTradingAgent
from dashboard import generate_full_dashboard


def test_virtual_trading():
    """测试虚拟交易引擎"""
    print("\n" + "="*60)
    print("测试1: 虚拟交易引擎")
    print("="*60)
    
    engine = VirtualTradingEngine(initial_cash=100000)
    
    # 模拟信号
    signals = [
        TradeSignal(
            date='2025-01-25',
            fund_code='001001',
            fund_name='测试基金1',
            signal_type='BUY',
            signal_score=2.5,
            nav_price=1.234,
            suggested_amount=10000,
            reason='RSI低位+大跌'
        ),
        TradeSignal(
            date='2025-01-26',
            fund_code='001002',
            fund_name='测试基金2',
            signal_type='BUY',
            signal_score=1.8,
            nav_price=2.567,
            suggested_amount=5000,
            reason='布林带下轨'
        ),
    ]
    
    # 添加信号
    for signal in signals:
        engine.add_signal(signal)
    
    print(f"✓ 已添加 {len(signals)} 个交易信号")
    
    # 虚拟成交
    current_prices = {'001001': 1.220, '001002': 2.580}
    
    for signal in signals:
        if signal.signal_type == 'BUY':
            engine.execute_signal(
                signal,
                execution_date=datetime.date.today().strftime('%Y-%m-%d'),
                execution_price=current_prices[signal.fund_code]
            )
    
    print(f"✓ 已虚拟成交所有信号")
    
    # 查看账户
    report = engine.get_performance_report(current_prices)
    print(f"\n账户状态:")
    print(f"  总资产: ¥{report['total_value']:,.2f}")
    print(f"  现金: ¥{engine.current_cash:,.2f}")
    print(f"  持仓: {engine.current_holdings}")


def test_strategy_evaluation():
    """测试策略评估"""
    print("\n" + "="*60)
    print("测试2: 策略评估")
    print("="*60)
    
    engine = VirtualTradingEngine(initial_cash=100000)
    
    # 添加一些虚拟数据
    for i in range(10):
        signal = TradeSignal(
            date=f'2025-01-{20+i:02d}',
            fund_code='001001',
            fund_name='测试基金',
            signal_type='BUY' if i % 2 == 0 else 'SELL',
            signal_score=2.0 + i * 0.1,
            nav_price=1.200 + i * 0.01,
            suggested_amount=10000,
            reason='测试'
        )
        
        # 添加一些已执行的信号
        if i < 5:
            signal.execution_date = f'2025-01-{21+i:02d}'
            signal.execution_price = 1.210 + i * 0.01
            signal.execution_amount = 10000
            signal.execution_shares = 10000 / (1.210 + i * 0.01)
        
        engine.signals_history.append(signal)
    
    current_prices = {'001001': 1.250}
    
    # 评估
    metrics = StrategyEvaluator.calculate_metrics(engine, current_prices)
    
    print(f"✓ 策略评估完成:")
    print(f"  总收益率: {metrics['total_return']:.2%}")
    print(f"  胜率: {metrics['win_rate']:.2%}")
    print(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
    print(f"  最大回撤: {metrics['max_drawdown']:.2%}")


def test_strategy_evolution():
    """测试策略进化"""
    print("\n" + "="*60)
    print("测试3: 策略进化")
    print("="*60)
    
    evolver = StrategyEvolver()
    
    # 获取初始参数
    initial_params = evolver.get_current_params()
    print(f"✓ 初始参数:")
    print(f"  RSI超卖: {initial_params['rsi_oversold']}")
    print(f"  RSI超买: {initial_params['rsi_overbought']}")
    
    # 模拟高胜率的评估结果
    metrics = {
        'win_rate': 0.70,  # 70%胜率
        'sharpe_ratio': 1.5,
        'max_drawdown': 0.08
    }
    
    # 进化参数
    new_params = evolver.evolve_parameters(metrics)
    
    print(f"\n✓ 进化后的参数:")
    print(f"  RSI超卖: {new_params['rsi_oversold']}")
    print(f"  RSI超买: {new_params['rsi_overbought']}")
    print(f"  止盈目标: {new_params['profit_take_threshold']:.1%}")


def test_agent_workflow():
    """测试智能体工作流"""
    print("\n" + "="*60)
    print("测试4: 自动化智能体工作流")
    print("="*60)
    
    # 创建智能体
    agent = AutoTradingAgent(initial_cash=100000)
    
    # 模拟monitor结果
    monitor_results = {
        'date': datetime.date.today().strftime('%Y-%m-%d'),
        'signals': [
            {
                'fund_code': '001001',
                'fund_name': '易方达消费行业',
                'signal': 'BUY',
                'score': 2.5,
                'current_price': 1.234,
                'suggested_amount': 15000,
                'reason': '极度超卖'
            },
            {
                'fund_code': '001002',
                'fund_name': '南方中证500',
                'signal': 'HOLD',
                'score': 1.0,
                'current_price': 2.567,
                'suggested_amount': 0,
                'reason': '位置中性'
            }
        ]
    }
    
    # 处理信号
    response = agent.on_monitor_completion(monitor_results)
    
    print(f"✓ 智能体处理完成:")
    print(f"  处理信号数: {len(response['processed_signals'])}")
    print(f"  建议数量: {len(response['next_actions'])}")
    
    print(f"\n  建议内容:")
    for action in response['next_actions']:
        print(f"    - {action}")


def test_complete_dashboard():
    """测试完整仪表板"""
    print("\n" + "="*60)
    print("测试5: 完整仪表板")
    print("="*60)
    
    # 创建测试数据
    engine = VirtualTradingEngine(initial_cash=100000)
    
    # 添加一些测试信号
    test_signals = [
        TradeSignal(
            date='2025-01-20',
            fund_code='001001',
            fund_name='基金1',
            signal_type='BUY',
            signal_score=2.5,
            nav_price=1.200,
            suggested_amount=10000,
            reason='低位'
        ),
        TradeSignal(
            date='2025-01-21',
            fund_code='001002',
            fund_name='基金2',
            signal_type='BUY',
            signal_score=2.0,
            nav_price=2.500,
            suggested_amount=5000,
            reason='补仓'
        ),
    ]
    
    # 添加并执行信号
    for signal in test_signals:
        engine.add_signal(signal)
        engine.execute_signal(
            signal,
            execution_date=datetime.date.today().strftime('%Y-%m-%d'),
            execution_price=signal.nav_price * 0.99
        )
    
    # 生成仪表板
    current_prices = {'001001': 1.250, '001002': 2.550}
    print("\n✓ 生成仪表板:")
    generate_full_dashboard(current_prices)


def run_all_tests():
    """运行所有测试"""
    print("\n"
          "╔════════════════════════════════════════════════════════╗\n"
          "║   自动化交易智能体系统 - 完整测试套件                 ║\n"
          "╚════════════════════════════════════════════════════════╝\n")
    
    try:
        test_virtual_trading()
        test_strategy_evaluation()
        test_strategy_evolution()
        test_agent_workflow()
        test_complete_dashboard()
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！系统准备好投入使用")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "test1":
            test_virtual_trading()
        elif test_name == "test2":
            test_strategy_evaluation()
        elif test_name == "test3":
            test_strategy_evolution()
        elif test_name == "test4":
            test_agent_workflow()
        elif test_name == "test5":
            test_complete_dashboard()
        else:
            print("未知测试名称")
    else:
        run_all_tests()
