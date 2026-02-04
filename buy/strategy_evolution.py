# 策略进化引擎 - 根据历史表现自动优化策略参数
import json
import os
import datetime
from typing import Dict, List, Tuple
import numpy as np
from virtual_trading import VirtualTradingEngine


class StrategyEvaluator:
    """策略评估器 - 计算策略表现"""
    
    @staticmethod
    def calculate_metrics(engine: VirtualTradingEngine, 
                         current_prices: Dict[str, float]) -> Dict:
        """
        计算策略性能指标
        
        Args:
            engine: 虚拟交易引擎
            current_prices: 当前价格
            
        Returns:
            包含多个性能指标的字典
        """
        report = engine.get_performance_report(current_prices)
        
        # 总体收益率
        total_return = report['total_return']
        
        # 信号胜率
        win_rate = report['win_rate']
        
        # 信号执行率 (已执行信号 / 总信号)
        total_signals = len(engine.signals_history)
        executed = report['executed_signals']
        execution_rate = executed / total_signals if total_signals > 0 else 0
        
        # 计算夏普比率 (简化版：基于月度收益)
        monthly_returns = StrategyEvaluator._get_monthly_returns(engine)
        sharpe_ratio = StrategyEvaluator._calculate_sharpe(monthly_returns)
        
        # 最大回撤
        max_drawdown = StrategyEvaluator._calculate_max_drawdown(engine, current_prices)
        
        return {
            'total_return': total_return,
            'win_rate': win_rate,
            'execution_rate': execution_rate,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_signals': total_signals,
            'executed_signals': executed,
            'total_value': report['total_value'],
            'current_cash': engine.current_cash,
            'current_holdings': engine.current_holdings
        }
    
    @staticmethod
    def _get_monthly_returns(engine: VirtualTradingEngine) -> List[float]:
        """计算月度收益率"""
        monthly_data = {}
        
        for signal in engine.signals_history:
            month = signal.date[:7]  # YYYY-MM
            if month not in monthly_data:
                monthly_data[month] = {'buy': 0, 'sell': 0, 'count': 0}
            
            if signal.execution_date and signal.execution_price:
                if signal.signal_type == "BUY":
                    monthly_data[month]['buy'] += signal.execution_amount or 0
                elif signal.signal_type == "SELL":
                    monthly_data[month]['sell'] += signal.execution_amount or 0
                monthly_data[month]['count'] += 1
        
        returns = []
        for month in sorted(monthly_data.keys()):
            data = monthly_data[month]
            if data['buy'] > 0:
                monthly_return = (data['sell'] - data['buy']) / data['buy']
                returns.append(monthly_return)
        
        return returns
    
    @staticmethod
    def _calculate_sharpe(returns: List[float], risk_free_rate: float = 0.03) -> float:
        """计算夏普比率"""
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate / 12
        
        mean_return = np.mean(excess_returns)
        std_return = np.std(excess_returns)
        
        if std_return == 0:
            return 0.0
        
        sharpe = mean_return / std_return * np.sqrt(12)  # 年化
        return float(sharpe)
    
    @staticmethod
    def _calculate_max_drawdown(engine: VirtualTradingEngine, 
                               current_prices: Dict[str, float]) -> float:
        """计算最大回撤"""
        # 简化版：基于当前持仓的未实现亏损
        unrealized = engine.get_unrealized_pnl(current_prices)
        
        max_loss = 0
        for code, info in unrealized.items():
            if info['pnl'] < 0:
                max_loss = min(max_loss, info['pnl'])
        
        total_value = engine.get_portfolio_value(current_prices)
        if total_value > 0:
            return max(0, -max_loss / total_value)
        
        return 0.0


class StrategyEvolver:
    """策略进化器 - 根据表现自动调整参数"""
    
    def __init__(self, base_params: Dict = None):
        """
        初始化策略进化器
        
        Args:
            base_params: 基础策略参数
        """
        self.base_params = base_params or self._get_default_params()
        self.params_history: List[Tuple[str, Dict]] = []
        self.evolution_log = "strategy_evolution.json"
        
        self.load_evolution_history()
    
    @staticmethod
    def _get_default_params() -> Dict:
        """获取默认策略参数"""
        return {
            'rsi_window': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 75,
            'ma_window': 20,
            'buy_score_threshold': 1,
            'sell_threshold': 70,
            'profit_take_threshold': 0.10,  # 10%盈利止盈
            'loss_cut_threshold': -0.15,    # 15%亏损止损
            'dca_loss_threshold': -0.10,    # 10%亏损时补仓
        }
    
    def load_evolution_history(self):
        """加载进化历史"""
        if os.path.exists(self.evolution_log):
            try:
                with open(self.evolution_log, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.params_history = data.get('history', [])
            except:
                pass
    
    def save_evolution_history(self):
        """保存进化历史"""
        with open(self.evolution_log, 'w', encoding='utf-8') as f:
            json.dump({
                'history': self.params_history,
                'timestamp': datetime.datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def evolve_parameters(self, metrics: Dict) -> Dict:
        """
        根据性能指标进化策略参数
        
        Args:
            metrics: 策略性能指标
            
        Returns:
            新的策略参数
        """
        new_params = self.base_params.copy()
        
        # 根据胜率调整 RSI 阈值
        win_rate = metrics.get('win_rate', 0.5)
        if win_rate > 0.6:
            # 胜率好：扩大交易范围，降低超卖阈值
            new_params['rsi_oversold'] = max(20, self.base_params['rsi_oversold'] - 2)
        elif win_rate < 0.4:
            # 胜率差：收紧交易范围，提高超卖阈值
            new_params['rsi_oversold'] = min(40, self.base_params['rsi_oversold'] + 2)
        
        # 根据夏普比率调整利润止盈
        sharpe = metrics.get('sharpe_ratio', 0)
        if sharpe > 1.0:
            # 风险调整收益好：提高止盈目标
            new_params['profit_take_threshold'] = min(0.20, 
                self.base_params['profit_take_threshold'] + 0.02)
        elif sharpe < 0.5:
            # 风险调整收益差：降低止盈目标
            new_params['profit_take_threshold'] = max(0.05,
                self.base_params['profit_take_threshold'] - 0.02)
        
        # 根据最大回撤调整止损
        max_dd = metrics.get('max_drawdown', 0)
        if max_dd > 0.20:
            # 回撤太大：更激进的止损
            new_params['loss_cut_threshold'] = max(-0.25, 
                self.base_params['loss_cut_threshold'] + 0.05)
        elif max_dd < 0.05:
            # 回撤很小：可以更宽松
            new_params['loss_cut_threshold'] = min(-0.05,
                self.base_params['loss_cut_threshold'] - 0.05)
        
        # 记录演进
        timestamp = datetime.datetime.now().isoformat()
        self.params_history.append([timestamp, new_params])
        
        # 更新基础参数用于下一轮演进
        self.base_params = new_params
        self.save_evolution_history()
        
        return new_params
    
    def get_current_params(self) -> Dict:
        """获取当前策略参数"""
        if self.params_history:
            return self.params_history[-1][1]
        return self.base_params
    
    def get_params_evolution(self) -> List[Dict]:
        """获取参数演进历史"""
        return [
            {
                'timestamp': hist[0],
                'params': hist[1]
            }
            for hist in self.params_history
        ]


class AdaptiveStrategyOptimizer:
    """自适应策略优化器 - 综合评估和进化"""
    
    def __init__(self):
        self.engine = VirtualTradingEngine()
        self.evolver = StrategyEvolver()
        self.evaluation_history = []
    
    def run_daily_optimization(self, current_prices: Dict[str, float]) -> Dict:
        """
        每日运行一次策略优化
        
        Args:
            current_prices: 当前基金价格
            
        Returns:
            包含评估结果和新参数的字典
        """
        # 1. 评估当前策略
        metrics = StrategyEvaluator.calculate_metrics(self.engine, current_prices)
        
        # 2. 进化策略参数
        new_params = self.evolver.evolve_parameters(metrics)
        
        # 3. 记录
        evaluation_record = {
            'date': datetime.datetime.now().isoformat(),
            'metrics': metrics,
            'new_params': new_params
        }
        self.evaluation_history.append(evaluation_record)
        
        return {
            'metrics': metrics,
            'new_params': new_params,
            'recommendation': self._get_recommendation(metrics)
        }
    
    def _get_recommendation(self, metrics: Dict) -> str:
        """根据指标生成建议"""
        recommendations = []
        
        if metrics['win_rate'] > 0.65:
            recommendations.append("✓ 策略运行良好，可加大投资力度")
        elif metrics['win_rate'] < 0.40:
            recommendations.append("⚠ 策略胜率较低，建议调整参数或观望")
        
        if metrics['total_return'] > 0.10:
            recommendations.append("✓ 累计收益>10%，可考虑获利了结部分")
        elif metrics['total_return'] < -0.10:
            recommendations.append("⚠ 累计亏损>10%，建议补仓或止损")
        
        if metrics['max_drawdown'] > 0.25:
            recommendations.append("⚠ 最大回撤超过25%，风险较高")
        
        if not recommendations:
            recommendations.append("继续执行当前策略，持续监控")
        
        return " | ".join(recommendations)
    
    def get_performance_dashboard(self, current_prices: Dict[str, float]) -> Dict:
        """
        获取性能仪表板
        
        Returns:
            包含所有关键信息的字典
        """
        metrics = StrategyEvaluator.calculate_metrics(self.engine, current_prices)
        current_params = self.evolver.get_current_params()
        unrealized_pnl = self.engine.get_unrealized_pnl(current_prices)
        
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'metrics': metrics,
            'current_params': current_params,
            'unrealized_pnl': unrealized_pnl,
            'params_evolution': self.evolver.get_params_evolution()[-5:],  # 最近5次演进
        }
