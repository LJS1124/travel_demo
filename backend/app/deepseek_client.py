import json
from typing import Any

import httpx

from .settings import Settings


class DeepSeekClientError(RuntimeError):
    """Raised when DeepSeek API returns unexpected output."""


def _build_endpoint(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def _extract_json(content: str) -> dict[str, Any]:
    text = content.strip()
    if "```" in text:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
    return json.loads(text)


def _is_valid_plan(payload: dict[str, Any]) -> bool:
    required_top = ["status", "request_summary", "itinerary", "price_breakdown", "risk_flags", "handoff_to_human"]
    return all(key in payload for key in required_top)


def _build_messages(request_payload: dict[str, Any], baseline_plan: dict[str, Any]) -> list[dict[str, str]]:
    schema = {
        "status": "ok",
        "request_summary": {
            "destination": "string",
            "days": 3,
            "travelers": 2,
            "budget_cny": 9000,
            "preferences": ["美食", "轻松节奏"],
        },
        "itinerary": [
            {"day": 1, "morning": "景点A", "afternoon": "景点B", "evening": "活动C"}
        ],
        "price_breakdown": {
            "transport": 0,
            "hotel": 0,
            "tickets": 0,
            "meals": 0,
            "service_fee": 0,
            "total": 0,
        },
        "risk_flags": ["budget_exceeded"],
        "handoff_to_human": False,
    }

    system_prompt = (
        "你是旅游规划SaaS后端助手。"
        "必须仅返回JSON对象，不要解释、不要markdown代码块。"
        "输出字段必须严格匹配给定schema，金额使用CNY数字。"
        "行程节奏要合理，避免不现实的跨城安排。"
    )
    user_prompt = (
        "请根据请求生成可售卖行程结果。\n"
        f"请求:\n{json.dumps(request_payload, ensure_ascii=False)}\n"
        f"可参考的基线方案:\n{json.dumps(baseline_plan, ensure_ascii=False)}\n"
        f"返回schema:\n{json.dumps(schema, ensure_ascii=False)}"
    )
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]


def generate_with_deepseek(
    request_payload: dict[str, Any],
    baseline_plan: dict[str, Any],
    settings: Settings,
) -> dict[str, Any]:
    if not settings.deepseek_api_key:
        raise DeepSeekClientError("DEEPSEEK_API_KEY is empty.")

    endpoint = _build_endpoint(settings.deepseek_api_base, settings.deepseek_chat_path)
    body = {
        "model": settings.deepseek_model,
        "temperature": 0.2,
        "messages": _build_messages(request_payload, baseline_plan),
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {settings.deepseek_api_key}", "Content-Type": "application/json"}

    try:
        response = httpx.post(endpoint, json=body, headers=headers, timeout=settings.deepseek_timeout_seconds)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise DeepSeekClientError(f"DeepSeek request failed: {exc.__class__.__name__}") from exc

    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
        parsed = _extract_json(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise DeepSeekClientError("DeepSeek response parsing failed.") from exc

    if not _is_valid_plan(parsed):
        raise DeepSeekClientError("DeepSeek response missing required fields.")

    parsed["provider"] = "deepseek"
    return parsed

