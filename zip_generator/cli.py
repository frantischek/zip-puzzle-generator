import argparse
import json
import sys

from .generator import generate_puzzle


def parse_stdin_payload() -> dict:
    payload = sys.stdin.read()
    if not payload.strip():
        return {}
    return json.loads(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Zip puzzles.")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"])
    parser.add_argument("--seed", type=int)
    parser.add_argument(
        "--stdin-json",
        action="store_true",
        help="Read input as JSON from stdin. Expected keys: difficulty, seed.",
    )
    args = parser.parse_args()

    try:
        if args.stdin_json:
            data = parse_stdin_payload()
            difficulty = data.get("difficulty", "medium")
            seed = data.get("seed")
        else:
            difficulty = args.difficulty or "medium"
            seed = args.seed

        result = generate_puzzle(difficulty=difficulty, seed=seed)
        print(json.dumps(result))
        return 0 if not result.get("error") else 1
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": True, "message": f"Invalid JSON input: {exc}"}))
        return 2
    except ValueError as exc:
        print(json.dumps({"error": True, "message": str(exc)}))
        return 3
    except Exception as exc:
        print(json.dumps({"error": True, "message": f"Unhandled error: {exc}"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
