from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.analytics.weekly import WeeklyStat, weekly_return
from src.config.loader import load_config
from src.config.symbols import SymbolRegistry
from src.presentation.deck import build_deck
from src.reports.payload import build_weekly_payload
from src.storage.local import LocalStorage


def previous_completed_week(today: date) -> tuple[date, date]:
    days_since_friday = (today.weekday() - 4) % 7
    if days_since_friday == 0:
        days_since_friday = 7
    friday = today - timedelta(days=days_since_friday)
    monday = friday - timedelta(days=4)
    return monday, friday


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate weekly recap JSON + PowerPoint from stored Parquet data.")
    parser.add_argument("--start", type=date.fromisoformat)
    parser.add_argument("--end", type=date.fromisoformat)
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--output-dir", default="output")
    return parser.parse_args()


def collect_stats(storage: LocalStorage, registry: SymbolRegistry, group: str, start: date, end: date) -> list[WeeklyStat]:
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
    if not benchmark_stats:
        raise SystemExit("No benchmark data found for the requested week. Run the data puller first.")

    payload = build_weekly_payload(
        start=start,
        end=end,
        benchmark_stats=benchmark_stats,
        equity_stats=equity_stats,
        sources=[f"{config.provider.title()} API"],
    )

    out_dir = Path(args.output_dir) / f"{start.isoformat()}_to_{end.isoformat()}"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "weekly_report.json"
    pptx_path = out_dir / "weekly_recap.pptx"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    build_deck(payload, pptx_path)

    print(json_path)
    print(pptx_path)


if __name__ == "__main__":
    main()
