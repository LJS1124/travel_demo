import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from fastapi.testclient import TestClient

    from backend.app.deepseek_client import DeepSeekClientError
    from backend.app.main import app
    from backend.app.plan_graph import get_plan_graph
    from backend.app.settings import get_settings

    FASTAPI_READY = True
except Exception:
    FASTAPI_READY = False


@unittest.skipUnless(FASTAPI_READY, "fastapi/testclient not installed")
class TestAPI(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["PLAN_PROVIDER"] = "local"
        get_settings.cache_clear()
        get_plan_graph.cache_clear()
        self.client = TestClient(app)

    def test_health(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")

    def test_plan_contract(self) -> None:
        response = self.client.post(
            "/api/plan",
            json={
                "destination": "北京",
                "days": 2,
                "travelers": 2,
                "budget_cny": 8000,
                "preferences": ["文化"],
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("itinerary", payload)
        self.assertIn("price_breakdown", payload)

    @patch("backend.app.plan_graph.generate_with_deepseek")
    def test_plan_deepseek_fallback_contract(self, mock_generate) -> None:
        os.environ["PLAN_PROVIDER"] = "deepseek"
        get_settings.cache_clear()
        get_plan_graph.cache_clear()
        mock_generate.side_effect = DeepSeekClientError("provider down")

        response = self.client.post(
            "/api/plan",
            json={
                "destination": "北京",
                "days": 2,
                "travelers": 2,
                "budget_cny": 8000,
                "preferences": ["文化"],
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["provider"], "local_fallback")


if __name__ == "__main__":
    unittest.main()
