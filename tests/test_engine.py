import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mvp_travel_agent.engine import generate_plan


class TestTravelMVP(unittest.TestCase):
    def test_missing_fields(self) -> None:
        result = generate_plan({"destination": "北京"})
        self.assertEqual(result["status"], "need_more_info")
        self.assertIn("days", result["missing_fields"])
        self.assertIn("travelers", result["missing_fields"])
        self.assertIn("budget_cny", result["missing_fields"])

    def test_valid_request_generates_plan(self) -> None:
        request = {
            "destination": "上海",
            "days": 2,
            "travelers": 2,
            "budget_cny": 8000,
            "preferences": ["亲子"],
        }
        result = generate_plan(request)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["itinerary"]), 2)
        self.assertIn("total", result["price_breakdown"])
        self.assertFalse(result["handoff_to_human"])

    def test_budget_exceeded_handoff(self) -> None:
        request = {
            "destination": "北京",
            "days": 5,
            "travelers": 4,
            "budget_cny": 6000,
            "preferences": ["深度游"],
        }
        result = generate_plan(request)
        self.assertEqual(result["status"], "ok")
        self.assertIn("budget_exceeded", result["risk_flags"])
        self.assertTrue(result["handoff_to_human"])


if __name__ == "__main__":
    unittest.main()
