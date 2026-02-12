# 当前项目分析与三 Agent 开发式 MVP 方案

## 1. 当前项目分析

当前仓库只有架构文档，尚未进入可执行阶段。

### 现有文件
- `travel-saas-agent-architecture.md`：业务架构已定义
- `three-agent-mvp-plan.md`：本文件（开发实施计划）

### 关键结论
- 业务方向明确，但缺少可运行代码
- 缺少“需求 -> 开发 -> 验证”的协作流水线
- 需要先做工程 MVP，再逐步接入真实供应商与支付

## 2. 三 Agent 分工（开发协作，不是产品内三 Agent）

本方案将 3 个 Agent 用于“开发过程协作”，而不是把产品运行时拆成 3 个智能体。

## 2.1 Agent-1：Product/Architect Agent

### 目标
- 产出 MVP 范围、输入输出契约、验收标准

### 交付物
- `dev_agents/agent_1_product_prd.md`

## 2.2 Agent-2：Engineer Agent

### 目标
- 基于契约实现最小可运行代码（CLI + 规则引擎）

### 交付物
- `mvp_travel_agent/engine.py`
- `mvp_travel_agent/cli.py`
- `mvp_travel_agent/models.py`

## 2.3 Agent-3：QA/Release Agent

### 目标
- 验证功能正确性、边界行为和回归风险

### 交付物
- `tests/test_engine.py`
- `dev_agents/agent_3_qa_report.md`

## 3. Agent 间交接协议

1. Agent-1 定义请求字段：`destination`, `days`, `travelers`, `budget_cny`, `preferences`
2. Agent-2 必须保证输出结构稳定：
   - `status`
   - `itinerary`
   - `price_breakdown`
   - `risk_flags`
   - `handoff_to_human`
3. Agent-3 根据契约做自动化检查，不允许手工口头验收

## 4. 本次 MVP 实现范围

### In Scope
- 国内游单城市规划
- 固定规则估价（交通/酒店/门票/餐饮/服务费）
- 预算风险提示与人工接管判定
- CLI 演示与单元测试

### Out of Scope
- 实时机酒库存
- 真支付/退款
- 多租户权限系统

## 5. 运行方式

### 运行示例
```bash
python3 -m mvp_travel_agent.cli --input mvp_travel_agent/sample_request.json
```

### 运行测试
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## 6. 结论

该 MVP 已采用“多智能体开发协作”方式落地：  
Agent-1 负责需求与契约、Agent-2 负责实现、Agent-3 负责质量门禁。  
这能直接支持你们团队后续扩展到真实供应商、支付闭环和小程序接入。
