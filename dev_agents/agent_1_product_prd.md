# Agent-1 Product/Architect 交付（MVP PRD）

## 背景
- 服务对象：大型旅行公司内部及合作旅行社
- 目标：快速验证“需求输入 -> 行程生成 -> 预算评估 -> 风险提示”的可运行链路

## MVP 用户故事
1. 作为门店顾问，我输入目的地、天数、人数、预算后，系统能生成基础行程草案
2. 作为销售，我能看到成本估算与预算匹配状态
3. 作为运营，我能识别哪些请求应转人工复核

## 输入契约
- `destination`：字符串，必填
- `days`：整数，必填，>= 1
- `travelers`：整数，必填，>= 1
- `budget_cny`：数字，必填，> 0
- `preferences`：字符串列表，选填

## 输出契约
- `status`：`ok` 或 `need_more_info`
- `missing_fields`：当缺字段时返回
- `itinerary`：按天行程
- `price_breakdown`：成本明细
- `risk_flags`：风险标签列表
- `handoff_to_human`：是否转人工

## 验收标准
- 缺字段时，准确返回 `missing_fields`
- 有效输入时，返回稳定 JSON 结构
- 预算超限时，必须标记风险并建议人工介入

