# 自动化交易系统配置文件
import json
import os

class Config:
    """系统配置"""
    
    # 虚拟账户配置
    INITIAL_CASH = 100000  # 初始资金 (¥)
    
    # 策略参数（默认值）
    DEFAULT_STRATEGY_PARAMS = {
        'rsi_window': 14,              # RSI周期
        'rsi_oversold': 30,            # RSI超卖点
        'rsi_overbought': 75,          # RSI超买点
        'ma_window': 20,               # 均线周期
        'buy_score_threshold': 1,      # 买入评分门槛
        'sell_threshold': 70,          # 卖出RSI阈值
        'profit_take_threshold': 0.10, # 止盈目标 (10%)
        'loss_cut_threshold': -0.15,   # 止损目标 (-15%)
        'dca_loss_threshold': -0.10,   # 补仓亏损度 (-10%)
    }
    
    # 定时任务配置
    MONITOR_TIME = "14:30"             # 每日运行时间
    TIMEZONE = "Asia/Shanghai"         # 时区
    
    # 数据文件
    DATA_FILES = {
        'signals': 'virtual_signals.json',
        'positions': 'virtual_positions.json',
        'snapshots': 'virtual_snapshots.json',
        'evolution': 'strategy_evolution.json',
        'execution': 'scheduler_execution.json',
        'integration': 'integration_report.json',
    }
    
    # 报告配置
    KEEP_DAILY_REPORTS = 30          # 保留最近N天的日报告
    EVOLUTION_HISTORY_LIMIT = 100    # 参数演进历史记录数
    
    # 风险管理
    MAX_POSITION_SIZE = 0.50          # 单只基金最大持仓比例
    TOTAL_POSITION_LIMIT = 0.90       # 总仓位上限
    
    # 性能评估
    MIN_WIN_RATE_THRESHOLD = 0.45     # 最低胜率阈值
    MIN_SHARPE_THRESHOLD = 0.5        # 最低夏普比率
    
    @classmethod
    def load_from_file(cls, filepath: str = 'config.json'):
        """从JSON文件加载配置"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                    for key, value in config_dict.items():
                        setattr(cls, key, value)
                print(f"✓ 已加载配置文件: {filepath}")
            except Exception as e:
                print(f"⚠️ 加载配置文件失败: {e}")
    
    @classmethod
    def save_to_file(cls, filepath: str = 'config.json'):
        """将配置保存到JSON文件"""
        config_dict = {
            'INITIAL_CASH': cls.INITIAL_CASH,
            'DEFAULT_STRATEGY_PARAMS': cls.DEFAULT_STRATEGY_PARAMS,
            'MONITOR_TIME': cls.MONITOR_TIME,
            'TIMEZONE': cls.TIMEZONE,
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        print(f"✓ 已保存配置文件: {filepath}")
    
    @classmethod
    def get_all_settings(cls):
        """获取所有设置"""
        return {
            'initial_cash': cls.INITIAL_CASH,
            'strategy_params': cls.DEFAULT_STRATEGY_PARAMS,
            'monitor_time': cls.MONITOR_TIME,
            'timezone': cls.TIMEZONE,
            'data_files': cls.DATA_FILES,
        }


# 日志配置
class LogConfig:
    """日志配置"""
    
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
    LOG_FILE = "trading_system.log"
    
    @classmethod
    def setup_logging(cls):
        """设置日志"""
        import logging
        
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT,
            handlers=[
                logging.FileHandler(cls.LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )


# 数据库配置 (如果需要持久化)
class DatabaseConfig:
    """数据库配置 (可选)"""
    
    # SQLite配置
    DB_TYPE = "sqlite"  # 或 "mysql", "postgresql"
    DB_PATH = "trading_system.db"
    
    # MySQL配置 (如果使用)
    # DB_HOST = "localhost"
    # DB_PORT = 3306
    # DB_USER = "user"
    # DB_PASSWORD = "password"
    # DB_NAME = "trading_db"


if __name__ == "__main__":
    # 打印所有设置
    print("系统配置:")
    print(json.dumps(Config.get_all_settings(), ensure_ascii=False, indent=2))
    
    # 保存默认配置
    Config.save_to_file()
