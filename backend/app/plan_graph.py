from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import logging
from typing import Any, Literal, TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from mvp_travel_agent.engine import generate_plan as generate_plan_local

from .deepseek_client import DeepSeekClientError, generate_with_deepseek
from .settings import get_settings

LOGGER = logging.getLogger(__name__)


class PlanGraphState(TypedDict, total=False):
    request: dict[str, Any]
    provider_mode: str
    local_plan: dict[str, Any]
    use_deepseek: bool
    deepseek_error: str
    final_plan: dict[str, Any]


def _load_provider_mode(_: PlanGraphState) -> dict[str, Any]:
    settings = get_settings()
    return {"provider_mode": settings.plan_provider}


def _build_local_baseline(state: PlanGraphState) -> dict[str, Any]:
    local_plan = generate_plan_local(state["request"])
    use_deepseek = local_plan.get("status") == "ok" and state.get("provider_mode") != "local"
    return {"local_plan": local_plan, "use_deepseek": use_deepseek}


def _route_after_baseline(state: PlanGraphState) -> Literal["call_deepseek", "finalize_local"]:
    local_plan = state["local_plan"]
    if local_plan.get("status") != "ok":
        return "finalize_local"
    if not state.get("use_deepseek", False):
        return "finalize_local"
    return "call_deepseek"


def _call_deepseek(state: PlanGraphState) -> dict[str, Any]:
    settings = get_settings()
    try:
        result = generate_with_deepseek(state["request"], state["local_plan"], settings)
        return {"final_plan": result, "deepseek_error": ""}
    except DeepSeekClientError as exc:
        return {"deepseek_error": str(exc)}


def _route_after_deepseek(state: PlanGraphState) -> Literal["fallback_local", "finish"]:
    final_plan = state.get("final_plan")
    if isinstance(final_plan, dict) and final_plan.get("provider") == "deepseek":
        return "finish"
    return "fallback_local"


def _fallback_local(state: PlanGraphState) -> dict[str, Any]:
    local_plan = deepcopy(state["local_plan"])
    local_plan["provider"] = "local_fallback"
    return {"final_plan": local_plan}


def _finalize_local(state: PlanGraphState) -> dict[str, Any]:
    local_plan = deepcopy(state["local_plan"])
    local_plan["provider"] = "local"
    return {"final_plan": local_plan}


def _finish(_: PlanGraphState) -> dict[str, Any]:
    return {}


@lru_cache(maxsize=1)
def _get_inmemory_saver():
    return InMemorySaver()


@lru_cache(maxsize=2)
def get_plan_graph(use_checkpointer: bool = False):
    builder = StateGraph(PlanGraphState)
    builder.add_node("load_provider_mode", _load_provider_mode)
    builder.add_node("build_local_baseline", _build_local_baseline)
    builder.add_node("call_deepseek", _call_deepseek)
    builder.add_node("fallback_local", _fallback_local)
    builder.add_node("finalize_local", _finalize_local)
    builder.add_node("finish", _finish)

    builder.add_edge(START, "load_provider_mode")
    builder.add_edge("load_provider_mode", "build_local_baseline")

    builder.add_conditional_edges(
        "build_local_baseline",
        _route_after_baseline,
        {
            "call_deepseek": "call_deepseek",
            "finalize_local": "finalize_local",
        },
    )

    builder.add_conditional_edges(
        "call_deepseek",
        _route_after_deepseek,
        {
            "fallback_local": "fallback_local",
            "finish": "finish",
        },
    )

    builder.add_edge("fallback_local", "finish")
    builder.add_edge("finalize_local", END)
    builder.add_edge("finish", END)
    if use_checkpointer:
        return builder.compile(checkpointer=_get_inmemory_saver())
    return builder.compile()


def _build_graph_config(use_checkpointer: bool, thread_id: str | None) -> dict[str, Any] | None:
    if not use_checkpointer:
        return None
    chosen = thread_id or f"plan-graph-{uuid4()}"
    return {"configurable": {"thread_id": chosen}}


def _run_with_stream(
    initial_state: PlanGraphState,
    *,
    use_checkpointer: bool,
    config: dict[str, Any] | None,
) -> PlanGraphState:
    last_state: PlanGraphState | None = None
    graph = get_plan_graph(use_checkpointer=use_checkpointer)
    stream_iter = graph.stream(initial_state, config=config, stream_mode="values") if config else graph.stream(initial_state, stream_mode="values")
    for index, state in enumerate(stream_iter):
        if isinstance(state, dict):
            last_state = state
            LOGGER.debug("plan_graph.stream step=%s keys=%s", index, sorted(state.keys()))
        else:
            LOGGER.debug("plan_graph.stream step=%s type=%s", index, type(state).__name__)
    if last_state is None:
        raise RuntimeError("LangGraph stream did not yield state.")
    return last_state


def run_plan_graph(
    payload: dict[str, Any],
    *,
    debug_stream: bool = False,
    use_checkpointer: bool = False,
    thread_id: str | None = None,
) -> dict[str, Any]:
    config = _build_graph_config(use_checkpointer=use_checkpointer, thread_id=thread_id)
    if debug_stream:
        result_state = _run_with_stream(
            {"request": payload},
            use_checkpointer=use_checkpointer,
            config=config,
        )
    else:
        graph = get_plan_graph(use_checkpointer=use_checkpointer)
        result_state = graph.invoke({"request": payload}, config=config) if config else graph.invoke({"request": payload})

    final_plan = result_state.get("final_plan")
    if not isinstance(final_plan, dict):
        raise RuntimeError("LangGraph execution did not produce final_plan.")
    return final_plan
