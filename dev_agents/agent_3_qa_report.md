# Agent-3 QA/Release 交付（测试报告）

## 测试范围
- 输入校验
- 正常行程生成
- 预算超限风险标记
- FastAPI 接口健康检查
- FastAPI 接口规划合约

## 自动化测试用例
- `tests/test_engine.py::test_missing_fields`
- `tests/test_engine.py::test_valid_request_generates_plan`
- `tests/test_engine.py::test_budget_exceeded_handoff`
- `tests/test_api.py::test_health`
- `tests/test_api.py::test_plan_contract`

## 当前结论
- 测试时间：2026-02-13
- 执行命令：`.venv/bin/python -m unittest discover -s tests -p "test_*.py"`
- 结果：`Ran 5 tests ... OK`
- 冒烟验证：`.venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8001` + `curl /api/health` + `curl /api/plan`
- 风险说明：当前为规则引擎演示版，未接入真实供应商动态价格，报价偏差属于已知范围
