# Phase 0 - Current System Scan & Risk List

## Current Modules
- API layer: `/Users/liangjinshan/jaosn_project/codex_test/backend/app/main.py`
- Planning service orchestration (current): `/Users/liangjinshan/jaosn_project/codex_test/backend/app/plan_service.py`
- LLM provider integration: `/Users/liangjinshan/jaosn_project/codex_test/backend/app/deepseek_client.py`
- Configuration: `/Users/liangjinshan/jaosn_project/codex_test/backend/app/settings.py`
- Core deterministic planner: `/Users/liangjinshan/jaosn_project/codex_test/mvp_travel_agent/engine.py`
- Frontend contract consumer: `/Users/liangjinshan/jaosn_project/codex_test/frontend/app.js`
- Tests: `/Users/liangjinshan/jaosn_project/codex_test/tests/test_engine.py`, `/Users/liangjinshan/jaosn_project/codex_test/tests/test_api.py`

## Dependencies (runtime)
- `fastapi`, `uvicorn`, `httpx`, `python-dotenv`
- No graph orchestration framework yet (LangGraph not introduced yet)

## Critical Runtime Path
1. Frontend posts to `POST /api/plan`.
2. API validates payload via `PlanRequest`.
3. `plan_service.generate_plan` always computes local baseline first.
4. If local baseline is valid and provider=deepseek, call DeepSeek for enriched plan.
5. On DeepSeek error, fallback to local baseline (`provider=local_fallback`).
6. Return JSON consumed directly by frontend renderer.

## Hidden Couplings
- Response shape is coupled across:
  - local engine output
  - DeepSeek response validator (`_is_valid_plan`)
  - frontend renderer (`renderSuccess`, `renderNeedMoreInfo`)
- `provider` field is optional in some paths historically; frontend currently tolerates this implicitly.
- Settings are cached (`@lru_cache`), so env var changes after import are not reflected unless process restarts.
- API tests force `PLAN_PROVIDER=local`, relying on import order behavior.

## Primary Migration Risks
- Behavioral drift: LangGraph migration may alter fallback ordering or status/provider semantics.
- Schema drift: adding graph state internals to API response by mistake would break frontend.
- Error path regressions: current flow swallows provider failures and returns local fallback; must remain equivalent.
- Checkpoint misuse: adding persistence without stable `thread_id` can create non-deterministic state carry-over.
- Test fragility: provider mode + env caching can make tests order-dependent.

## Phase 0 Definition of Done Check
- Current modules/dependencies/critical path enumerated
- Main hidden couplings and regression risks listed
- Context7-derived LangGraph notes documented in `/Users/liangjinshan/jaosn_project/codex_test/docs/langgraph-notes.md`

