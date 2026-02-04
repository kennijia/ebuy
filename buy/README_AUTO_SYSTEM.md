# 自动化量化交易智能体系统

一个完全自动化的量化交易系统，能够：
- ✅ 每天14:30自动运行monitor程序
- ✅ 虚拟执行交易建议（记录每个信号）
- ✅ 自动评估策略表现（胜率、夏普比率等）
- ✅ 自动进化策略参数（基于历史表现调整）
- ✅ 生成每日智能体报告和建议

## 快速开始（3步）

### Step 1: 安装依赖
```bash
pip install schedule pandas numpy pytz
```

### Step 2: 使用集成的main.py
```bash
# 运行一次自动化流程
python main_integrated.py once

# 或启动连续模式（14:30自动执行）
python main_integrated.py continuous

# 查看虚拟账户状态
python main_integrated.py portfolio

# 查看策略演进历史
python main_integrated.py evolution
```

### Step 3: 定时运行（可选）
在Windows任务计划程序中设置每日14:30运行：
```
python main_integrated.py once
```

## 核心模块

| 模块 | 功能 |
|-----|------|
| `virtual_trading.py` | 虚拟交易记录和账户管理 |
| `strategy_evolution.py` | 策略性能评估和参数进化 |
| `scheduler.py` | 定时任务调度 |
| `auto_agent.py` | 自动化智能体（核心） |
| `integration.py` | 与monitor.py的集成适配器 |

## 关键概念

### 虚拟交易流程
```
14:30 → monitor生成信号
        ↓
记录信号到virtual_signals.json
        ↓
评估信号历史表现（胜率、夏普比率等）
        ↓
根据表现自动调整策略参数
        ↓
第二天 → 虚拟成交，计算盈亏
        ↓
继续进化...
```

### 性能指标
- **总收益率**: 累计收益 / 初始资金
- **胜率**: 正确信号 / 总信号
- **夏普比率**: 风险调整后的收益
- **最大回撤**: 最坏情况下的损失比例
- **执行率**: 已成交 / 总信号

## 性能示例

运行后会输出：
```
📈 性能指标:
   💰 总收益率:      12.50%
   🎯 胜率:         58.00%
   ⚡ 夏普比率:        1.25
   📉 最大回撤:      8.50%
   📊 执行率:       92.00%

💡 智能体建议:
   ✓ 策略运行良好，可加大投资力度
   ✓ 累计收益>10%，可考虑获利了结部分

⚙️ 最新策略参数:
   rsi_oversold: 28
   profit_take_threshold: 0.12
   loss_cut_threshold: -0.13
```

## 数据文件

系统自动生成的JSON文件：
- `virtual_signals.json` - 所有交易信号
- `virtual_positions.json` - 当前持仓
- `strategy_evolution.json` - 参数演进历史
- `scheduler_execution.json` - 执行日志
- `daily_results_*.json` - 每日报告

## 集成到现有程序

如果你想使用现有的main.py，在末尾添加：

```python
from integration import MonitorIntegration
from auto_agent import create_auto_agent

# 创建智能体和集成器
agent = create_auto_agent(initial_cash=100000)
integration = MonitorIntegration(agent)

# 获取monitor结果（你现有的逻辑）
monitor_results = check_signals(fund_list, held_info)

# 处理并自动优化
response = integration.process_monitor_results(monitor_results)

# 打印报告
for action in response['next_actions']:
    print(f"✓ {action}")
```

## 高级功能

### 自定义初始资金
```python
agent = create_auto_agent(initial_cash=500000)  # 50万初始资金
```

### 查看虚拟账户详情
```python
from virtual_trading import VirtualTradingEngine

engine = VirtualTradingEngine()
print(f"现金: ¥{engine.current_cash:,.2f}")
print(f"持仓: {engine.current_holdings}")
```

### 导出报告
```python
import json
from auto_agent import create_auto_agent

agent = create_auto_agent()
report = agent.get_daily_report()

with open('report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
```

## 常见问题

**Q: 虚拟交易与真实账户不一致？**
A: 虚拟账户是模拟账户，用于学习和评估策略。可以手动同步或导入真实持仓。

**Q: 如何暂停自动运行？**
A: 不运行`main_integrated.py continuous`，而是只运行`once`模式。

**Q: 多久进化一次参数？**
A: 每次运行monitor时都会评估和优化参数。

**Q: 可以实时交易吗？**
A: 当前是虚拟交易。集成真实交易需要连接到券商API。

## 详细文档

查看 `AUTO_SYSTEM_GUIDE.md` 了解完整的技术文档和高级配置。

## 许可证

MIT License
