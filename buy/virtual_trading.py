# 虚拟交易系统 - 记录并追踪策略的历史建议
import json
import os
import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import pandas as pd


@dataclass
class TradeSignal:
    """单个交易信号"""
    date: str  # 信号生成日期
    fund_code: str  # 基金代码
    fund_name: str  # 基金名称
    signal_type: str  # BUY / SELL / HOLD
    signal_score: float  # 信号强度 (0-3)
    nav_price: float  # 当前净值
    suggested_amount: float  # 建议买入金额
    reason: str  # 信号原因
    
    # 后续实际执行情况
    execution_date: Optional[str] = None  # 实际执行日期
    execution_price: Optional[float] = None  # 实际执行价格
    execution_amount: Optional[float] = None  # 实际执行金额
    execution_shares: Optional[float] = None  # 实际得到份额
    

@dataclass
class PortfolioSnapshot:
    """持仓快照 - 记录虚拟账户状态"""
    date: str
    holdings: Dict[str, float]  # {fund_code: shares_amount}
    cash: float
    total_asset: float  # 现金 + 持仓市值
    market_prices: Dict[str, float]  # {fund_code: nav_price}


class VirtualTradingEngine:
    """虚拟交易引擎"""
    
    def __init__(self, initial_cash: float = 100000):
        """
        初始化虚拟账户
        
        Args:
            initial_cash: 初始现金
        """
        self.initial_cash = initial_cash
        self.signals_history: List[TradeSignal] = []
        self.portfolio_snapshots: List[PortfolioSnapshot] = []
        
        # 虚拟账户当前状态
        self.current_holdings: Dict[str, float] = {}  # {code: shares}
        self.current_cash = initial_cash
        
        self.signals_file = "virtual_signals.json"
        self.snapshots_file = "virtual_snapshots.json"
        self.positions_file = "virtual_positions.json"
        
        self.load_from_file()
    
    def load_from_file(self):
        """从文件加载历史数据"""
        if os.path.exists(self.signals_file):
            try:
                with open(self.signals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.signals_history = [
                        TradeSignal(**d) for d in data.get('signals', [])
                    ]
            except:
                pass
        
        if os.path.exists(self.positions_file):
            try:
                with open(self.positions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_holdings = data.get('holdings', {})
                    self.current_cash = data.get('cash', self.initial_cash)
            except:
                pass
    
    def save_to_file(self):
        """保存数据到文件"""
        # 保存信号历史
        with open(self.signals_file, 'w', encoding='utf-8') as f:
            json.dump({
                'signals': [asdict(s) for s in self.signals_history],
                'timestamp': datetime.datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        # 保存虚拟持仓
        with open(self.positions_file, 'w', encoding='utf-8') as f:
            json.dump({
                'holdings': self.current_holdings,
                'cash': self.current_cash,
                'timestamp': datetime.datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def add_signal(self, signal: TradeSignal) -> None:
        """
        添加新的交易信号
        
        Args:
            signal: TradeSignal对象
        """
        self.signals_history.append(signal)
        self.save_to_file()
    
    def execute_signal(self, signal: TradeSignal, execution_date: str, 
                      execution_price: float) -> bool:
        """
        执行信号（虚拟成交）
        
        Args:
            signal: 要执行的信号
            execution_date: 成交日期
            execution_price: 成交价格
            
        Returns:
            是否成交成功
        """
        # 找到对应的信号
        for s in self.signals_history:
            if (s.date == signal.date and s.fund_code == signal.fund_code 
                and s.signal_type == signal.signal_type):
                
                if signal.signal_type == "BUY":
                    # 买入：使用建议金额
                    spend = min(signal.suggested_amount, self.current_cash)
                    if spend > 0:
                        shares = spend / execution_price
                        self.current_holdings[signal.fund_code] = (
                            self.current_holdings.get(signal.fund_code, 0) + shares
                        )
                        self.current_cash -= spend
                        
                        s.execution_date = execution_date
                        s.execution_price = execution_price
                        s.execution_amount = spend
                        s.execution_shares = shares
                        
                        self.save_to_file()
                        return True
                
                elif signal.signal_type == "SELL":
                    # 卖出：卖出所有持仓
                    if signal.fund_code in self.current_holdings:
                        shares = self.current_holdings[signal.fund_code]
                        proceeds = shares * execution_price
                        
                        del self.current_holdings[signal.fund_code]
                        self.current_cash += proceeds
                        
                        s.execution_date = execution_date
                        s.execution_price = execution_price
                        s.execution_amount = proceeds
                        s.execution_shares = shares
                        
                        self.save_to_file()
                        return True
        
        return False
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        计算当前虚拟账户总资产
        
        Args:
            current_prices: 当前各基金价格 {code: price}
            
        Returns:
            总资产
        """
        holdings_value = sum(
            shares * current_prices.get(code, 0)
            for code, shares in self.current_holdings.items()
        )
        return self.current_cash + holdings_value
    
    def get_performance_report(self, current_prices: Dict[str, float]) -> Dict:
        """
        获取虚拟账户性能报告
        
        Returns:
            包含收益率、胜率、最大回撤等指标的报告
        """
        total_value = self.get_portfolio_value(current_prices)
        total_return = (total_value - self.initial_cash) / self.initial_cash
        
        # 计算已成交信号的胜率
        executed_signals = [s for s in self.signals_history if s.execution_date]
        
        if executed_signals:
            winning_trades = sum(1 for s in executed_signals 
                               if s.signal_type == "BUY" and 
                               s.execution_price and s.nav_price and
                               s.nav_price > s.execution_price)
            win_rate = winning_trades / len(executed_signals)
        else:
            win_rate = 0.0
        
        return {
            'total_return': total_return,
            'total_value': total_value,
            'win_rate': win_rate,
            'executed_signals': len(executed_signals),
            'pending_signals': len([s for s in self.signals_history 
                                   if not s.execution_date]),
            'current_holdings': self.current_holdings,
            'current_cash': self.current_cash
        }
    
    def get_unrealized_pnl(self, current_prices: Dict[str, float]) -> Dict[str, Dict]:
        """
        获取未实现盈亏
        
        Returns:
            {code: {shares, cost, current_price, pnl, pnl_percent}}
        """
        result = {}
        
        # 查找买入成本
        buy_prices = {}
        for s in self.signals_history:
            if (s.signal_type == "BUY" and s.execution_date and 
                s.execution_price and s.fund_code not in buy_prices):
                buy_prices[s.fund_code] = s.execution_price
        
        for code, shares in self.current_holdings.items():
            cost_price = buy_prices.get(code, 0)
            current_price = current_prices.get(code, 0)
            cost = shares * cost_price if cost_price > 0 else 0
            current_value = shares * current_price
            pnl = current_value - cost
            pnl_percent = pnl / cost if cost > 0 else 0
            
            result[code] = {
                'shares': shares,
                'cost_price': cost_price,
                'current_price': current_price,
                'total_cost': cost,
                'current_value': current_value,
                'pnl': pnl,
                'pnl_percent': pnl_percent
            }
        
        return result
