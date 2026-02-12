# LangGraph 1.0 Notes (from Context7 MCP)

## Retrieval Log
- Date: 2026-02-13
- Context7 MCP calls executed:
  - `resolve-library-id` with `libraryName=langgraph`
  - `query-docs` (Context7 server当前工具名；等价于你要求的 `get-library-docs`)
- Selected library id: `/langchain-ai/langgraph`
- Other candidates returned:
  - `/websites/langchain_oss_python_langgraph`
  - `/llmstxt/langchain-ai_github_io_langgraph_llms-full_txt`

## Key Specs (to explicitly follow in implementation)

### 1) State
- Use typed state schema (e.g. `TypedDict`) as graph state contract.
- Prefer reducer-style fields for append/merge semantics where needed (example: message list reducers).
- Keep node outputs as partial state updates (`dict`) instead of mutating global state.

### 2) Graph
- Build graph with `StateGraph(StateSchema)`.
- Use `START`/`END` as explicit entry/exit boundaries.
- Compile graph before execution (`compiled = graph.compile(...)`).

### 3) Nodes
- Nodes are pure state transformers: input = state, output = partial state update dict.
- Keep node responsibilities single-purpose (validation, baseline generation, provider call, fallback, finalize).
- Complex tool execution should isolate error handling close to node boundary.

### 4) Routing
- Use `add_conditional_edges` for dynamic routing.
- Router functions decide branch key from state; mapping maps branch key to node or `END`.
- For retry/fallback flows, route by explicit state flags (`error`, `provider`, `status`) rather than exceptions leaking upward.

### 5) Persistence / Checkpointing
- Checkpointing is configured at compile time (`graph.compile(checkpointer=...)`).
- `InMemorySaver`/`MemorySaver` are valid for local dev.
- Resume/continuation relies on `config={"configurable":{"thread_id":"..."}}`.
- `checkpoint_id` can be used for targeted resume/time-travel style restore.

### 6) Streaming
- Use `graph.stream(...)` for incremental outputs.
- `stream_mode` supports value/message-style progressive updates (docs examples include `"values"` and message/value combinations).
- Streaming is suitable for observability/debug and progressive UI updates; synchronous `.invoke(...)` can remain for API compatibility.

### 7) Error Handling
- Node-level guarded execution (`try/except`) + state flagging is a recommended pattern.
- Route on error flags through conditional edges for retries/fallback instead of hard-failing the whole graph.
- Keep explicit termination guards (e.g. max iterations / retry bounds) to avoid infinite loops.
- Tool execution can use explicit error handlers (example shown with `ToolNode(handle_tool_errors=...)`).

## Source URLs Returned by Context7
- [https://context7.com/langchain-ai/langgraph/llms.txt](https://context7.com/langchain-ai/langgraph/llms.txt)
- [https://github.com/langchain-ai/langgraph/blob/main/README.md](https://github.com/langchain-ai/langgraph/blob/main/README.md)
- [https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint/README.md](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint/README.md)
- [https://github.com/langchain-ai/langgraph/blob/main/libs/prebuilt/README.md](https://github.com/langchain-ai/langgraph/blob/main/libs/prebuilt/README.md)
- [https://github.com/langchain-ai/langgraph/blob/main/examples/rag/langgraph_adaptive_rag.ipynb](https://github.com/langchain-ai/langgraph/blob/main/examples/rag/langgraph_adaptive_rag.ipynb)

