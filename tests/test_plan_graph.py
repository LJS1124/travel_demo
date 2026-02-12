import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.deepseek_client import DeepSeekClientError
from backend.app.plan_graph import get_plan_graph, run_plan_graph
from backend.app.settings import get_settings


def _valid_request() -> dict:
    return {
        "destination": "北京",
        "days": 2,
        "travelers": 2,
        "budget_cny": 8000,
        "preferences": ["文化"],
    }


class TestPlanGraph(unittest.TestCase):
    def setUp(self) -> None:
        get_settings.cache_clear()
        get_plan_graph.cache_clear()

    def test_invalid_request_returns_local_provider(self) -> None:
        os.environ["PLAN_PROVIDER"] = "deepseek"
        result = run_plan_graph({"destination": "北京"})
        self.assertEqual(result["status"], "need_more_info")
        self.assertEqual(result["provider"], "local")

    def test_local_provider_mode_skips_deepseek(self) -> None:
        os.environ["PLAN_PROVIDER"] = "local"
        result = run_plan_graph(_valid_request())
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["provider"], "local")

    def test_debug_stream_path_keeps_contract(self) -> None:
        os.environ["PLAN_PROVIDER"] = "local"
        result = run_plan_graph(_valid_request(), debug_stream=True)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["provider"], "local")

    def test_checkpointer_debug_path_keeps_contract(self) -> None:
        os.environ["PLAN_PROVIDER"] = "local"
        result = run_plan_graph(
            _valid_request(),
            debug_stream=True,
            use_checkpointer=True,
            thread_id="test-thread-1",
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["provider"], "local")

    @patch("backend.app.plan_graph.generate_with_deepseek")
    def test_deepseek_success_path(self, mock_generate) -> None:
        os.environ["PLAN_PROVIDER"] = "deepseek"
        mock_generate.return_value = {
            "status": "ok",
            "request_summary": {
                "destination": "北京",
                "days": 2,
                "travelers": 2,
                "budget_cny": 8000,
                "preferences": ["文化"],
            },
            "itinerary": [{"day": 1, "morning": "故宫", "afternoon": "天坛", "evening": "活动"}],
            "price_breakdown": {"transport": 1000, "hotel": 500, "tickets": 300, "meals": 300, "service_fee": 100, "total": 2200},
            "risk_flags": [],
            "handoff_to_human": False,
            "provider": "deepseek",
        }
        result = run_plan_graph(_valid_request())
        self.assertEqual(result["provider"], "deepseek")
        self.assertEqual(result["status"], "ok")

    @patch("backend.app.plan_graph.generate_with_deepseek")
    def test_deepseek_failure_fallback_local(self, mock_generate) -> None:
        os.environ["PLAN_PROVIDER"] = "deepseek"
        mock_generate.side_effect = DeepSeekClientError("mock failure")
        result = run_plan_graph(_valid_request())
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["provider"], "local_fallback")


if __name__ == "__main__":
    unittest.main()
