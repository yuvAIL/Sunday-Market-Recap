from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv()

from src.analytics.technical import moving_average_context
from src.analytics.weekly import WeeklyStat, weekly_return
from src.config.loader import load_config
from src.config.symbols import SymbolRegistry
from src.presentation.deck import build_deck
from src.reports.payload import build_weekly_payload
from src.reports.source_pack import render_notebooklm_source
from src.storage.local import LocalStorage


def previous_completed_week(today: date) -> tuple[date, date]:
    """Return Monday-Friday dates for the latest completed U.S. market week block."""
    days_since_friday = (today.weekday() - 4) % 7
    if days_since_friday == 0:
        days_since_friday = 7
    friday = today - timedelta(days=days_since_friday)
    monday = friday - timedelta(days=4)
    return monday, friday


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate weekly recap JSON, NotebookLM source pack and PowerPoint from stored Parquet data."
    )
    parser.add_argument("--start", type=date.fromisoformat)
    parser.add_argument("--end", type=date.fromisoformat)
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument(
        "--context",
        default=None,
        help="Optional verified context JSON with drivers, risks and extra_sources.",
    )
    return parser.parse_args()


def collect_stats(
    storage: LocalStorage,
    registry: SymbolRegistry,
    group: str,
    start: date,
    end: date,
) -> list[WeeklyStat]:
    stats: list[WeeklyStat] = []
    if group not in registry.groups():
        return stats
    for entry in registry.for_group(group):
        df = storage.read(entry.group, entry.canonical)
        if df.empty:
            continue
        try:
            stats.append(weekly_return(df, entry.canonical, start, end))
        except ValueError:
            continue
    return stats


def load_context(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    context = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(context, dict):
        raise SystemExit("Context JSON must contain an object at the top level.")
    return context


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    registry = SymbolRegistry(config)
    storage = LocalStorage(config.output_dir)

    start, end = (args.start, args.end)
    if start is None or end is None:
        start, end = previous_completed_week(date.today())
    if start > end:
        raise SystemExit("start must be <= end")

    benchmark_stats = collect_stats(storage, registry, "benchmarks", start, end)
    equity_stats = collect_stats(storage, registry, "equities", start, end)
    sector_stats = collect_stats(storage, registry, "sectors", start, end)

    macro_stats: list[WeeklyStat] = []
    for group in ("crypto", "fx", "commodities", "macro"):
        macro_stats.extend(collect_stats(storage, registry, group, start, end))

    if not benchmark_stats:
        raise SystemExit(
            "No benchmark data found for the requested week. Run the data puller first."
        )

    technical: list[dict[str, str]] = []
    try:
        spy = registry.for_symbol("SPY")
        spy_df = storage.read(spy.group, spy.canonical)
        technical = moving_average_context(spy_df, symbol="SPY", end=end)
    except ValueError:
        pass

    context = load_context(args.context)
    payload = build_weekly_payload(
        start=start,
        end=end,
        benchmark_stats=benchmark_stats,
        equity_stats=equity_stats,
        sector_stats=sector_stats,
        macro_stats=macro_stats,
        technical=technical,
        drivers=context.get("drivers", []),
        risks=context.get("risks", []),
        extra_sources=context.get("extra_sources", []),
        sources=[f"{config.provider.title()} API"],
    )

    out_dir = Path(args.output_dir) / f"{start.isoformat()}_to_{end.isoformat()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "weekly_report.json"
    pptx_path = out_dir / "weekly_recap.pptx"
    source_path = out_dir / "notebooklm_source.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    source_path.write_text(render_notebooklm_source(payload), encoding="utf-8")
    build_deck(payload, pptx_path)

    print(json_path)
    print(source_path)
    print(pptx_path)


if __name__ == "__main__":
    main()
