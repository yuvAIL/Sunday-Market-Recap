from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.presentation.deck import build_deck


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Sunday Market Recap JSON as PowerPoint.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    report = json.loads(Path(args.input).read_text(encoding="utf-8"))
    build_deck(report, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
