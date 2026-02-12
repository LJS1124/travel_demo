from typing import Any

from .plan_graph import run_plan_graph
from .settings import get_settings


def generate_plan(payload: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    return run_plan_graph(
        payload,
        debug_stream=settings.plan_graph_debug_stream,
        use_checkpointer=settings.plan_graph_use_checkpointer,
        thread_id=settings.plan_graph_debug_thread_id or None,
    )
