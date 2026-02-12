# Travel SaaS MVP（前后端分离）

本项目已升级为前后端分离架构：

- 后端：FastAPI（`/api/health`, `/api/plan`）
- 前端：独立静态页面（`frontend/`），通过 HTTP 调用后端
- 核心规划逻辑：`mvp_travel_agent/engine.py`
- 编排层：LangGraph 1.0（`backend/app/plan_graph.py`）

## 目录结构

- `backend/app/main.py`：FastAPI 应用入口
- `backend/app/schemas.py`：请求模型
- `backend/app/plan_graph.py`：LangGraph 编排图
- `frontend/index.html`：前端入口
- `frontend/styles.css`：UI 样式（按 ui-ux-pro-max 设计系统）
- `frontend/app.js`：前端交互逻辑
- `tests/test_engine.py`：引擎测试
- `tests/test_api.py`：API 合约测试
- `tests/test_plan_graph.py`：图编排路径测试

## 启动后端

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

默认地址：`http://127.0.0.1:8000`

## 环境变量（DeepSeek）

项目使用根目录 `.env` 管理 DeepSeek 配置，后端启动时自动加载：

- `PLAN_PROVIDER=deepseek`
- `PLAN_GRAPH_DEBUG_STREAM=false`（开启后使用 LangGraph stream 调试执行）
- `PLAN_GRAPH_USE_CHECKPOINTER=false`（仅调试建议开启，启用 InMemorySaver）
- `PLAN_GRAPH_DEBUG_THREAD_ID=`（可选；开启 checkpointer 时用于固定线程）
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_API_BASE=https://api.deepseek.com`
- `DEEPSEEK_CHAT_PATH=/chat/completions`
- `DEEPSEEK_MODEL=deepseek-chat`

若需要临时关闭大模型调用并使用本地规则引擎，可设置：

```bash
PLAN_PROVIDER=local
```

## 启动前端

```bash
python3 -m http.server 5500 --directory frontend
```

打开：`http://127.0.0.1:5500`

## 运行测试

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## 多智能体开发协作

本次实现采用“开发过程三 Agent”模式：

1. Agent-1（Product/Architect）定义接口契约与验收标准
2. Agent-2（Engineer）实现后端 API 和前端页面
3. Agent-3（QA）补测试并执行验证

详见：`dev_agents/multi-agent-dev-log.md`

## LangGraph 迁移文档

- `/Users/liangjinshan/jaosn_project/codex_test/docs/langgraph-notes.md`
- `/Users/liangjinshan/jaosn_project/codex_test/docs/langgraph-phase0-scan.md`
- `/Users/liangjinshan/jaosn_project/codex_test/docs/langgraph-phase1-design-draft.md`
- `/Users/liangjinshan/jaosn_project/codex_test/docs/langgraph-migration-plan.md`
- `/Users/liangjinshan/jaosn_project/codex_test/docs/langgraph-migration-guide.md`
