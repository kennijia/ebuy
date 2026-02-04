# 快速参考卡片 - 自动化交易系统

## 🚀 3秒快速开始

```bash
# Step 1: 安装依赖
pip install schedule pandas numpy pytz akshare

# Step 2: 运行一次
python main_integrated.py once

# Step 3: 启动连续模式
python main_integrated.py continuous
```

---

## 📋 常用命令

```bash
# 运行一次自动化流程（用于测试）
python main_integrated.py once

# 启动连续运行（14:30自动执行）
python main_integrated.py continuous

# 查看虚拟账户状态
python main_integrated.py portfolio

# 查看策略参数演进历史
python main_integrated.py evolution

# 打印性能仪表板
python dashboard.py

# 运行完整测试
python test_system.py

# 查看虚拟持仓和盈亏
python -c "
from virtual_trading import VirtualTradingEngine
e = VirtualTradingEngine()
print('持仓:', e.current_holdings)
print('现金:', e.current_cash)
print('信号数:', len(e.signals_history))
"
```

---

## 📊 关键指标速查

| 指标 | 计算公式 | 目标值 | 含义 |
|-----|---------|--------|------|
| 总收益率 | (当前资产-初始资产)/初始资产 | >10% | 赚了多少钱 |
| 胜率 | 赚钱信号/总信号 | >55% | 决策有多准 |
| 夏普比率 | 超额收益/波动率 | >1.0 | 风险下的收益 |
| 最大回撤 | 最大跌幅/历史最高 | <20% | 最坏情况损失 |
| 执行率 | 已成交/总信号 | >80% | 有多少信号执行了 |

---

## 🎛️ 参数调整指南

**如果胜率太低 (<50%)**
```python
# config.py 中调整
'rsi_oversold': 40,      # 提高超卖点，减少买入
'rsi_overbought': 85,    # 提高超买点，减少卖出
'profit_take_threshold': 0.05,  # 降低止盈目标
```

**如果回撤太大 (>20%)**
```python
# config.py 中调整
'loss_cut_threshold': -0.10,  # 更激进的止损
'dca_loss_threshold': -0.05,  # 更容易补仓
```

**如果想赚更多**
```python
# config.py 中调整
'rsi_oversold': 20,      # 降低超卖点，更激进买入
'profit_take_threshold': 0.15,  # 提高止盈目标
```

---

## 📁 关键文件说明

| 文件 | 功能 | 查看方法 |
|-----|------|---------|
| `virtual_signals.json` | 所有交易信号 | `cat virtual_signals.json` |
| `virtual_positions.json` | 当前持仓 | `cat virtual_positions.json` |
| `strategy_evolution.json` | 参数演进历史 | `python main_integrated.py evolution` |
| `scheduler_execution.json` | 执行日志 | `tail -20 scheduler_execution.json` |
| `daily_results_*.json` | 每日报告 | 在结果目录查看 |

---

## 🔍 诊断命令

```bash
# 检查系统是否正常运行
python test_system.py

# 查看最后一次执行的结果
ls -lt daily_results_*.json | head -1

# 查看最近的执行日志
tail -20 scheduler_execution.json

# 检查是否有错误信号
grep -i error scheduler_execution.json

# 查看参数演进情况
python -c "
import json
with open('strategy_evolution.json') as f:
    data = json.load(f)
    for timestamp, params in data['history'][-3:]:
        print(f'{timestamp}: RSI={params[\"rsi_oversold\"]}, 止盈={params[\"profit_take_threshold\"]:.1%}')
"
```

---

## 💾 定期备份

```bash
# 备份重要数据
cp virtual_signals.json virtual_signals_backup_$(date +%Y%m%d).json
cp strategy_evolution.json strategy_evolution_backup_$(date +%Y%m%d).json
cp virtual_positions.json virtual_positions_backup_$(date +%Y%m%d).json
```

---

## 🐛 常见问题速解

**Q: 为什么没有信号？**
```
A: 检查monitor.py的结果是否返回了signals
   确保基金代码正确
   查看最近的执行日志
```

**Q: 持仓和账户不一致？**
```
A: 这是正常的，虚拟账户是独立的
   可以手动同步：
   engine.current_holdings = {'001001': 100}
   engine.save_to_file()
```

**Q: 如何暂停自动运行？**
```
A: 不要运行 continuous 模式
   改为只运行 once 模式
   或修改 MONITOR_TIME 为不存在的时间
```

**Q: 如何重置系统？**
```bash
# 删除所有数据，从头开始
rm virtual_signals.json virtual_positions.json strategy_evolution.json
python main_integrated.py once
```

---

## 📈 监控检查清单

每周检查一次：

- [ ] 胜率是否 > 50%
- [ ] 总收益是否为正
- [ ] 最大回撤是否 < 20%
- [ ] 执行率是否 > 80%
- [ ] 是否有错误信号
- [ ] 策略参数是否有异常变化
- [ ] 持仓是否需要调整
- [ ] 是否需要增加资金

---

## 🎯 优化建议

**初期（第1-2周）**
- 观察系统运行状态
- 记录关键指标
- 不要频繁调整参数

**中期（第3-4周）**
- 如果胜率 <50%，调整RSI阈值
- 如果回撤 >20%，调整止损
- 分析信号原因

**后期（第5周+）**
- 考虑加入其他技术指标
- 考虑多策略融合
- 考虑真实交易集成

---

## 🔗 相关文档

- 详细技术文档: `AUTO_SYSTEM_GUIDE.md`
- 系统架构: `SYSTEM_ARCHITECTURE.md`
- 快速入门: `README_AUTO_SYSTEM.md`
- 策略逻辑: `STRATEGY_LOGIC.md`

---

## 📞 技术支持

**问题排查步骤**：

1. 运行 `python test_system.py` 检查系统
2. 查看 `scheduler_execution.json` 日志
3. 检查 `daily_results_*.json` 最新报告
4. 运行 `python dashboard.py` 查看仪表板
5. 查看详细文档 `AUTO_SYSTEM_GUIDE.md`

---

## ✅ 检查清单 - 首次使用

- [ ] 安装了所有依赖包
- [ ] 修改了 config.py 中的初始资金（可选）
- [ ] 运行了 `python test_system.py` 通过所有测试
- [ ] 运行了 `python main_integrated.py once` 测试
- [ ] 查看了生成的 `daily_results_*.json` 报告
- [ ] 查看了 `dashboard.py` 的仪表板
- [ ] 配置了定时任务（可选）
- [ ] 备份了配置文件

---

**准备好开启自动化交易之旅了吗？** 🚀
