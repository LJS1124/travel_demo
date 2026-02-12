import argparse
import json
from pathlib import Path

from .engine import generate_plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Travel SaaS MVP CLI")
    parser.add_argument("--input", required=True, help="Path to request JSON file")
    args = parser.parse_args()

    input_path = Path(args.input)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    result = generate_plan(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

