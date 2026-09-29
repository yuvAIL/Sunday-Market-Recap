from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from src.analytics.weekly import WeeklyStat, rank_week


def build_weekly_payload(
    *,
    start: date,
    end: date,
    benchmark_stats: list[WeeklyStat],
    equity_stats: list[WeeklyStat] | None = None,
    sources: list[str] | None = None,
) -> dict[str, Any]:
    ranked_benchmarks = rank_week(benchmark_stats)
    benchmark_rows = [
        {
            "symbol": stat.symbol,
            "start_close": stat.start_close,
            "end_close": stat.end_close,
            "return_pct": stat.return_pct,
        }
        for stat in ranked_benchmarks
    ]

    lookup = {row["symbol"]: row for row in benchmark_rows}
    relative: list[dict[str, Any]] = []
    if "SPY" in lookup:
        spy = float(lookup["SPY"]["return_pct"])
        for symbol in ("QQQ", "MAGS", "IWM", "DIA"):
            if symbol in lookup:
                relative.append(
                    {
                        "label": f"{symbol} vs SPY",
                        "value_pct": float(lookup[symbol]["return_pct"]) - spy,
                    }
                )

    equities = rank_week(equity_stats or [])
    gainers = [
        {"symbol": stat.symbol, "return_pct": stat.return_pct}
        for stat in equities[:5]
        if stat.return_pct > 0
    ]
    losers = [
        {"symbol": stat.symbol, "return_pct": stat.return_pct}
        for stat in sorted(equities, key=lambda item: item.return_pct)[:5]
        if stat.return_pct < 0
    ]

    one_line = "Weekly market leadership was mixed."
    notes: list[str] = []
    if ranked_benchmarks:
        leader = ranked_benchmarks[0]
        laggard = ranked_benchmarks[-1]
        one_line = f"{leader.symbol} led configured benchmarks while {laggard.symbol} lagged."
        notes = [
            f"Best configured benchmark: {leader.symbol} ({leader.return_pct:+.2f}%).",
            f"Weakest configured benchmark: {laggard.symbol} ({laggard.return_pct:+.2f}%).",
        ]

    return {
        "meta": {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "calculation_method": "first available close to last available close in requested period",
        },
        "one_line_week": one_line,
        "benchmarks": benchmark_rows,
        "highlights": notes,
        "benchmark_takeaways": notes,
        "relative_performance": relative,
        "leadership_title": "Leadership & relative performance",
        "leadership_notes": [
            "Relative spreads are calculated deterministically from benchmark returns.",
            "Sector, breadth and mover conclusions appear only when those inputs exist.",
        ],
        "movers": {"gainers": gainers, "losers": losers, "shock_moves": []},
        "sectors": [],
        "sector_notes": [],
        "breadth": {},
        "breadth_notes": [],
        "macro": [],
        "macro_notes": [],
        "technical": [],
        "technical_notes": [],
        "drivers": [],
        "risks": [],
        "sources": sources or ["Massive API"],
        "final_takeaway": {
            "market_regime": "Data-driven weekly snapshot",
            "leadership": one_line,
            "key_tension": "Breadth / macro context depends on configured data coverage",
            "summary": "The presentation renderer never fills missing financial data with AI-generated numbers.",
        },
    }
