# Phase 1 - LangGraph 1.0 Design Draft (Functional Equivalence First)

## Goal
- Replace imperative orchestration in `plan_service.generate_plan` with LangGraph graph execution.
- Preserve external behavior of `POST /api/plan` (same contract and fallback semantics).

## Graph State Schema (draft)

```python
class PlanGraphState(TypedDict, total=False):
    request: dict
    local_plan: dict
    final_plan: dict
    status: str
    provider: str
    use_deepseek: bool
    errors: list[str]
```

Notes:
- API response only returns `final_plan`.
- Internal fields (`errors`, routing flags) must never leak to external payload.

## Node Responsibilities

1. `validate_and_baseline_node`
- Input: `request`
- Action: run local planner once (current `generate_plan_local`)
- Output:
  - `local_plan`
  - `status`
  - `use_deepseek` (only when `status=="ok"` and provider mode allows)

2. `provider_decision_router` (conditional)
- If `status != "ok"`: route to `finalize_local_node`
- Else if provider forced local: route to `finalize_local_node`
- Else: route to `deepseek_node`

3. `deepseek_node`
- Input: `request`, `local_plan`
- Action: call `generate_with_deepseek`
- On success: set `final_plan` + `provider=deepseek`
- On failure: set error flag only (do not raise unhandled exception)

4. `fallback_router` (conditional)
- If deepseek success: `finalize_node`
- If deepseek failed: `fallback_local_node`

5. `fallback_local_node`
- Output: `final_plan = local_plan`, `provider=local_fallback`

6. `finalize_local_node`
- Output: `final_plan = local_plan`
- Provider:
  - `local` if provider mode local
  - `local` for validation failure path (same as current behavior)

7. `finalize_node`
- Ensure `final_plan` includes `provider`.
- Return to API caller.

## Graph Topology (text)
- `START -> validate_and_baseline_node`
- `validate_and_baseline_node -> (conditional provider_decision_router)`
- `provider_decision_router:`
  - `to_local_finalize -> finalize_local_node -> END`
  - `to_deepseek -> deepseek_node -> (conditional fallback_router)`
- `fallback_router:`
  - `deepseek_ok -> finalize_node -> END`
  - `deepseek_error -> fallback_local_node -> finalize_node -> END`

## Error Strategy (per Context7 notes)
- Node-level error handling, state-flag based routing.
- No uncaught provider exception crossing graph boundary.
- Single-attempt provider call in MVP (no hidden retry loops yet).

## Checkpoint Strategy
- Phase 2 MVP migration:
  - default checkpointer: none (strict stateless equivalence)
  - optional debug mode: `InMemorySaver` with explicit `thread_id`
- Phase 3+:
  - enable persistent checkpointer for audit/replay only when thread model is explicitly defined.

## Streaming Strategy
- Keep API contract synchronous via `invoke` for equivalence.
- Add optional internal debug path using `stream(..., stream_mode=\"values\")` for observability.

## Definition of Done for Phase 1
- Design maps each existing control-flow branch to explicit graph nodes/edges.
- External response contract unchanged.
- Error and fallback semantics explicitly encoded as graph routing rules.

