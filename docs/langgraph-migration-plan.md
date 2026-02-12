# LangGraph 1.0 Migration Plan (Phased)

## Phase 0 - Scan & Risks
- Inventory current modules, dependencies, runtime path, hidden couplings.
- Collect LangGraph 1.0 practices from Context7 and document them.

### DoD
- Codebase scan completed
- Risk list completed
- `/Users/liangjinshan/jaosn_project/codex_test/docs/langgraph-notes.md` created

## Phase 1 - Architecture Design
- Define `StateGraph` state schema, nodes, conditional routing, error strategy, checkpoint policy.
- Ensure one-to-one mapping from existing orchestration behavior.

### DoD
- Graph design doc completed
- External API contract preservation rules documented

## Phase 2 - Minimal Functional Migration
- Introduce LangGraph runtime in backend service path.
- Migrate core planning orchestration from imperative function to graph invocation.
- Keep endpoint and payload schema unchanged.
- Status: completed

### DoD
- App runnable locally
- Existing behavior equivalent on key paths (ok / need_more_info / deepseek fallback)
- Tests pass

## Phase 3 - Tests & Runbook
- Add unit tests for graph nodes and routers.
- Add integration tests for `POST /api/plan` with provider success/failure routing.
- Provide one-command local verification.
- Status: completed

### DoD
- Unit + integration tests all green
- Reproducible local test command in README

## Phase 4 - Cleanup & Docs
- Remove obsolete orchestration code paths.
- Write migration guide and developer-oriented graph documentation.
- Keep diffs focused, avoid unrelated style churn.
- Status: completed

### DoD
- No dead code in replaced path
- README/docs updated
- Clear git diff with migration rationale
