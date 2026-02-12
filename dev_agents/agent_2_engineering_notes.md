# Agent-2 Engineer 交付（实现说明）

## 实现目标
- 用 Python 标准库实现最小可运行 MVP
- 提供 CLI 入口便于演示
- 输出结构严格遵循 PRD 契约

## 实现内容
- `mvp_travel_agent/models.py`：请求与输出数据结构
- `mvp_travel_agent/engine.py`：核心规则引擎
- `mvp_travel_agent/cli.py`：命令行入口
- `mvp_travel_agent/sample_request.json`：演示输入

## 关键规则
- 成本构成：交通 + 酒店 + 门票 + 餐饮 + 服务费
- 风险规则：
  - 总价 > 预算 => `budget_exceeded`
  - 天数 <= 1 => `tight_schedule`
  - 人数 >= 8 => `large_group_manual_review`
- 人工接管：
  - 预算超 20% 或大团（>=8 人）自动转人工

