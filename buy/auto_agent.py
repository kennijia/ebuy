# 自动化交易智能体 - 主程序
import datetime
import json
from typing import Dict, List
from virtual_trading import VirtualTradingEngine, TradeSignal
from strategy_evolution import AdaptiveStrategyOptimizer
from scheduler import DailyScheduler, schedule_monitor_task


class AutoTradingAgent:
    """自动化交易智能体"""
    
    def __init__(self, initial_cash: float = 100000):
        """
        初始化智能体
        
        Args:
            initial_cash: 初始资金
        """
        self.engine = VirtualTradingEngine(initial_cash)
        self.optimizer = AdaptiveStrategyOptimizer()
        self.scheduler = DailyScheduler()
        self.signal_log = "agent_signals.json"
    
    def on_monitor_completion(self, monitor_results: Dict) -> Dict:
        """
        监控程序完成时的回调函数
        
        Args:
            monitor_results: monitor.py返回的结果，应包含交易信号
                            格式: {
                                'date': '2025-01-29',
                                'signals': [
                                    {
                                        'fund_code': '001',
                                        'fund_name': '基金1',
                                        'signal': 'BUY',
                                        'score': 2.5,
                                        'current_price': 1.234,
                                        'suggested_amount': 10000,
                                        'reason': '买入原因'
                                    },
                                    ...
                                ]
                            }
        
        Returns:
            包含处理结果的字典
        """
        signal_date = monitor_results.get('date', 
                                         datetime.date.today().strftime('%Y-%m-%d'))
        
        # 1. 处理从monitor获得的信号
        processed_signals = []
        
        for signal_data in monitor_results.get('signals', []):
            # 创建TradeSignal对象
            signal = TradeSignal(
                date=signal_date,
                fund_code=signal_data['fund_code'],
                fund_name=signal_data.get('fund_name', ''),
                signal_type=signal_data['signal'].upper(),  # BUY/SELL/HOLD
                signal_score=signal_data.get('score', 0),
                nav_price=signal_data.get('current_price', 0),
                suggested_amount=signal_data.get('suggested_amount', 0),
                reason=signal_data.get('reason', '')
            )
            
            # 添加到虚拟引擎
            self.engine.add_signal(signal)
            processed_signals.append({
                'code': signal.fund_code,
                'type': signal.signal_type,
                'score': signal.signal_score,
                'amount': signal.suggested_amount
            })
        
        # 2. 执行虚拟交易
        # 这一步通常在第二天执行，因为今天生成的信号，明天才能真正成交
        
        # 3. 更新当前价格并获取虚拟账户价值
        current_prices = self._extract_prices(monitor_results)
        
        # 4. 运行策略优化
        optimization_result = self.optimizer.run_daily_optimization(current_prices)
        
        # 5. 获取性能仪表板
        dashboard = self.optimizer.get_performance_dashboard(current_prices)
        
        return {
            'status': 'success',
            'signal_date': signal_date,
            'processed_signals': processed_signals,
            'optimization_result': optimization_result,
            'performance_dashboard': dashboard,
            'next_actions': self._generate_actions(dashboard)
        }
    
    def _extract_prices(self, monitor_results: Dict) -> Dict[str, float]:
        """从monitor结果中提取基金价格"""
        prices = {}
        
        for signal in monitor_results.get('signals', []):
            code = signal['fund_code']
            price = signal.get('current_price', 0)
            if price > 0:
                prices[code] = price
        
        return prices
    
    def _generate_actions(self, dashboard: Dict) -> List[str]:
        """根据仪表板生成建议行动"""
        actions = []
        metrics = dashboard['metrics']
        
        # 基于胜率的行动
        if metrics['win_rate'] > 0.65:
            actions.append("✓ 策略运行良好，可加大投资力度")
        elif metrics['win_rate'] < 0.40:
            actions.append("⚠ 策略胜率偏低，建议观望")
        
        # 基于收益的行动
        if metrics['total_return'] > 0.15:
            actions.append("💰 累计收益>15%，建议部分获利了结")
        elif metrics['total_return'] < -0.15:
            actions.append("❌ 累计亏损>15%，请评估是否需要调整策略")
        
        # 基于执行率的行动
        if metrics['execution_rate'] < 0.5:
            actions.append("📊 交易执行率低，可能是资金不足")
        
        if not actions:
            actions.append("继续执行当前策略，持续监控")
        
        return actions
    
    def execute_pending_signals(self, execution_prices: Dict[str, float]) -> Dict:
        """
        执行待执行的交易信号
        这通常在第二天调用，执行昨天生成的信号
        
        Args:
            execution_prices: 成交价格
            
        Returns:
            执行结果
        """
        executed = []
        failed = []
        
        for signal in self.engine.signals_history:
            if not signal.execution_date:  # 未执行的信号
                if signal.fund_code in execution_prices:
                    success = self.engine.execute_signal(
                        signal,
                        execution_date=datetime.date.today().strftime('%Y-%m-%d'),
                        execution_price=execution_prices[signal.fund_code]
                    )
                    
                    if success:
                        executed.append({
                            'code': signal.fund_code,
                            'type': signal.signal_type,
                            'price': execution_prices[signal.fund_code]
                        })
                    else:
                        failed.append(signal.fund_code)
        
        return {
            'executed_count': len(executed),
            'executed': executed,
            'failed': failed
        }
    
    def get_daily_report(self) -> Dict:
        """获取每日报告"""
        current_prices = {}  # 这里你需要实际获取当前价格
        dashboard = self.optimizer.get_performance_dashboard(current_prices)
        
        return {
            'date': datetime.datetime.now().isoformat(),
            'performance': dashboard['metrics'],
            'current_holdings': self.engine.current_holdings,
            'cash': self.engine.current_cash,
            'total_assets': self.engine.get_portfolio_value(current_prices)
        }
    
    def setup_daily_automation(self):
        """设置每日自动化"""
        # 安排每天14:30运行monitor+优化
        self.scheduler.schedule_daily_job(
            job_name="每日14:30 策略执行",
            time_str="14:30",
            job_func=self.run_daily_cycle
        )
        
        # 安排每天15:00执行虚拟成交（模拟第二天的成交价）
        self.scheduler.schedule_daily_job(
            job_name="虚拟交易执行",
            time_str="15:00",
            job_func=self.execute_daily_trades
        )
    
    def run_daily_cycle(self) -> Dict:
        """运行每日周期（需要与你的monitor整合）"""
        print(f"[{datetime.datetime.now()}] 开始每日循环...")
        
        # 这里需要调用你的monitor函数获取结果
        # 示例：
        # from monitor import check_signals, load_holdings_info
        # held_info = load_holdings_info()
        # monitor_results = check_signals(fund_list, held_info)
        
        # 临时返回示例数据
        return {
            'status': 'pending',
            'message': '需要集成实际的monitor函数'
        }
    
    def execute_daily_trades(self) -> Dict:
        """执行每日交易"""
        print(f"[{datetime.datetime.now()}] 执行虚拟交易...")
        
        # 这里执行前一天生成的信号
        # execution_prices需要从实际数据获取
        execution_prices = {}
        
        return self.execute_pending_signals(execution_prices)


# 集成脚本 - 将此代码添加到你的main.py中
def create_auto_agent(initial_cash: float = 100000) -> AutoTradingAgent:
    """创建自动化交易智能体"""
    return AutoTradingAgent(initial_cash)


def integrate_with_monitor(agent: AutoTradingAgent, monitor_results: Dict):
    """将monitor结果集成到智能体"""
    return agent.on_monitor_completion(monitor_results)


# 示例：如何在main.py中使用
if __name__ == "__main__":
    # 创建智能体
    agent = create_auto_agent(initial_cash=100000)
    
    # 设置自动化任务
    agent.setup_daily_automation()
    
    # 启动定时调度器
    print("正在启动自动化交易系统...")
    agent.scheduler.start()
