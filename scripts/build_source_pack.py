from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reports.source_pack import render_notebooklm_source


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a NotebookLM-ready Markdown source pack from weekly report JSON.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    report = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_notebooklm_source(report), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
