# LangGraph Migration Guide (for Developers)

## Scope
- Objective: migrate orchestration to LangGraph 1.0 without changing `/api/plan` external behavior.
- Non-goal: redesign response schema or frontend rendering logic.

## Old vs New

### Old orchestration
- File: `/Users/liangjinshan/jaosn_project/codex_test/backend/app/plan_service.py`
- Style: imperative `if/try/except` chain

### New orchestration
- File: `/Users/liangjinshan/jaosn_project/codex_test/backend/app/plan_graph.py`
- Style: `StateGraph` with explicit nodes + conditional routing
- `plan_service` now only delegates: `run_plan_graph(payload)`

## Node Mapping
- `validate + baseline` -> `_build_local_baseline`
- `provider mode decision` -> `_route_after_baseline`
- `deepseek call` -> `_call_deepseek`
- `deepseek failure fallback` -> `_fallback_local`
- `local mode / invalid input finalize` -> `_finalize_local`

## Behavior Equivalence Rules
- Invalid request still returns:
  - `status=need_more_info`
  - `provider=local`
- `PLAN_PROVIDER=local` skips provider call:
  - `provider=local`
- DeepSeek call failure falls back:
  - `provider=local_fallback`
- Success path keeps provider output:
  - `provider=deepseek`

## Testing Strategy
- Unit/flow tests: `/Users/liangjinshan/jaosn_project/codex_test/tests/test_plan_graph.py`
- API integration tests: `/Users/liangjinshan/jaosn_project/codex_test/tests/test_api.py`
- Legacy deterministic planner tests retained:
  - `/Users/liangjinshan/jaosn_project/codex_test/tests/test_engine.py`

## Local Commands
- Install deps:
  - `pip install -r /Users/liangjinshan/jaosn_project/codex_test/backend/requirements.txt`
- Run tests:
  - `python -m unittest discover -s /Users/liangjinshan/jaosn_project/codex_test/tests -p "test_*.py"`
- Run API:
  - `uvicorn backend.app.main:app --reload`

## Known Constraints
- Current graph defaults to stateless execution (no checkpointer by default) to preserve behavior.
- `get_settings()` and `get_plan_graph()` are cached; tests must clear cache when changing env.
- `PLAN_GRAPH_DEBUG_STREAM=true` uses `graph.stream(..., stream_mode="values")` for debug observability but does not alter API response schema.
- Optional debug persistence:
  - `PLAN_GRAPH_USE_CHECKPOINTER=true` enables `InMemorySaver`
  - `PLAN_GRAPH_DEBUG_THREAD_ID` can pin a specific thread for replay/debug
