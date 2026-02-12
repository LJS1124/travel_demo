"""main 模块测试。"""

import unittest

from src.main import get_welcome_message


class TestMain(unittest.TestCase):
    """测试入口逻辑。"""

    def test_get_welcome_message(self) -> None:
        self.assertEqual(get_welcome_message(), "Welcome to travel_demo!")


if __name__ == "__main__":
    unittest.main()
