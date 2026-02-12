import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    plan_provider: str
    plan_graph_debug_stream: bool
    plan_graph_use_checkpointer: bool
    plan_graph_debug_thread_id: str
    deepseek_api_key: str
    deepseek_api_base: str
    deepseek_chat_path: str
    deepseek_model: str
    deepseek_timeout_seconds: float


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        plan_provider=os.environ.get("PLAN_PROVIDER", "deepseek").strip().lower(),
        plan_graph_debug_stream=_to_bool(os.environ.get("PLAN_GRAPH_DEBUG_STREAM"), default=False),
        plan_graph_use_checkpointer=_to_bool(os.environ.get("PLAN_GRAPH_USE_CHECKPOINTER"), default=False),
        plan_graph_debug_thread_id=os.environ.get("PLAN_GRAPH_DEBUG_THREAD_ID", "").strip(),
        deepseek_api_key=os.environ.get("DEEPSEEK_API_KEY", "").strip(),
        deepseek_api_base=os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com").strip(),
        deepseek_chat_path=os.environ.get("DEEPSEEK_CHAT_PATH", "/chat/completions").strip(),
        deepseek_model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat").strip(),
        deepseek_timeout_seconds=float(os.environ.get("DEEPSEEK_TIMEOUT_SECONDS", "30")),
    )
