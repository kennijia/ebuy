# 集成adapter - 将自动化系统与现有的monitor.py整合
import json
import datetime
from typing import Dict, List
from virtual_trading import TradeSignal
from auto_agent import AutoTradingAgent


class MonitorIntegration:
    """Monitor集成器 - 连接monitor.py和自动化系统"""
    
    def __init__(self, agent: AutoTradingAgent):
        """
        初始化集成器
        
        Args:
            agent: AutoTradingAgent实例
        """
        self.agent = agent
    
    def convert_monitor_output_to_signals(self, monitor_output: str) -> Dict:
        """
        将monitor.py的输出转换为标准信号格式
        
        Args:
            monitor_output: monitor.py的输出结果
            
        Returns:
            标准信号格式的字典
        """
        # 假设monitor.py输出的格式如下：
        # {
        #   'signals': [
        #       {
        #           'code': '001xxx',
        #           'name': '基金名称',
        #           'action': 'BUY',
        #           'score': 2.5,
        #           'current_nav': 1.234,
        #           'amount': 10000,
        #           'reason': '...'
        #       }
        #   ]
        # }
        
        try:
            if isinstance(monitor_output, str):
                monitor_output = json.loads(monitor_output)
            
            signals = []
            for sig in monitor_output.get('signals', []):
                signal = {
                    'fund_code': sig.get('code') or sig.get('fund_code'),
                    'fund_name': sig.get('name') or sig.get('fund_name'),
                    'signal': sig.get('action') or sig.get('signal'),
                    'score': sig.get('score', 0),
                    'current_price': sig.get('current_nav') or sig.get('current_price', 0),
                    'suggested_amount': sig.get('amount') or sig.get('suggested_amount', 0),
                    'reason': sig.get('reason', '')
                }
                signals.append(signal)
            
            return {
                'date': monitor_output.get('date', 
                       datetime.date.today().strftime('%Y-%m-%d')),
                'signals': signals
            }
        except Exception as e:
            print(f"错误：转换monitor输出失败 - {e}")
            return {'date': datetime.date.today().strftime('%Y-%m-%d'), 'signals': []}
    
    def process_monitor_results(self, monitor_output: Dict) -> Dict:
        """
        处理monitor结果并更新智能体
        
        Args:
            monitor_output: monitor程序的输出
            
        Returns:
            处理后的结果
        """
        # 1. 转换格式
        standardized = self.convert_monitor_output_to_signals(monitor_output)
        
        # 2. 传给智能体处理
        result = self.agent.on_monitor_completion(standardized)
        
        # 3. 生成报告
        self._generate_integration_report(standardized, result)
        
        return result
    
    def _generate_integration_report(self, signals: Dict, result: Dict):
        """生成集成报告"""
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'signals_received': len(signals['signals']),
            'optimization_result': result['optimization_result'],
            'next_actions': result['next_actions']
        }
        
        # 保存报告
        with open('integration_report.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(report, ensure_ascii=False) + '\n')


# 使用示例：如何修改你的monitor.py
def example_usage():
    """
    示例：在你的monitor.py的main函数最后添加以下代码
    """
    example_code = """
# 在monitor.py的最后，在main函数或check_signals函数执行完后添加：

from integration import MonitorIntegration
from auto_agent import create_auto_agent

# 创建智能体和集成器
if __name__ == "__main__":
    agent = create_auto_agent(initial_cash=100000)
    integration = MonitorIntegration(agent)
    
    # 获取monitor的结果（这是你现有的逻辑）
    monitor_results = check_signals(fund_list, held_info)
    
    # 处理results并更新智能体
    agent_response = integration.process_monitor_results(monitor_results)
    
    # 打印智能体的建议
    print("\\n===== 智能体建议 =====")
    for action in agent_response['next_actions']:
        print(f"- {action}")
    
    # 关键性能指标
    metrics = agent_response['performance_dashboard']['metrics']
    print(f"\\n累计收益: {metrics['total_return']:.2%}")
    print(f"胜率: {metrics['win_rate']:.2%}")
    print(f"执行率: {metrics['execution_rate']:.2%}")
    """
    
    return example_code


# 工具函数：设置自动化
def setup_auto_trading_system():
    """
    一键设置自动化交易系统
    """
    from auto_agent import create_auto_agent
    
    # 创建智能体
    agent = create_auto_agent(initial_cash=100000)
    
    # 设置自动化
    agent.setup_daily_automation()
    
    print("✓ 自动化交易系统已配置")
    print("✓ 系统将在每日14:30自动运行")
    
    return agent


if __name__ == "__main__":
    print("集成模块已加载")
    print("\n使用示例:")
    print(example_usage())
