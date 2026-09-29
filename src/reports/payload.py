from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from src.analytics.weekly import WeeklyStat, rank_week


def _rows(stats: list[WeeklyStat] | None) -> list[dict[str, Any]]:
    return [
        {
            "symbol": stat.symbol,
            "start_close": stat.start_close,
            "end_close": stat.end_close,
            "return_pct": stat.return_pct,
        }
        for stat in rank_week(stats or [])
    ]


def build_weekly_payload(
    *,
    start: date,
    end: date,
    benchmark_stats: list[WeeklyStat],
    equity_stats: list[WeeklyStat] | None = None,
    sector_stats: list[WeeklyStat] | None = None,
    macro_stats: list[WeeklyStat] | None = None,
    technical: list[dict[str, str]] | None = None,
    drivers: list[dict[str, str]] | None = None,
    risks: list[dict[str, str]] | None = None,
    extra_sources: list[str] | None = None,
    sources: list[str] | None = None,
) -> dict[str, Any]:
    ranked_benchmarks = rank_week(benchmark_stats)
    benchmark_rows = _rows(ranked_benchmarks)

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

    breadth: dict[str, Any] = {}
    breadth_notes: list[str] = []
    if equities:
        advancers = sum(stat.return_pct > 0 for stat in equities)
        decliners = sum(stat.return_pct < 0 for stat in equities)
        unchanged = len(equities) - advancers - decliners
        breadth = {
            "advancers": advancers,
            "decliners": decliners,
            "unchanged": unchanged,
            "positive_pct": (advancers / len(equities)) * 100.0,
            "universe_size": len(equities),
        }
        breadth_notes.append(
            f"Configured equity universe: {advancers} advancers, {decliners} decliners, {unchanged} unchanged."
        )
        breadth_notes.append(
            "This breadth measure covers the configured equity universe, not the full U.S. market."
        )

    sector_rows = _rows(sector_stats)
    sector_notes: list[str] = []
    if sector_rows:
        sector_notes = [
            f"Sector leader: {sector_rows[0]['symbol']} ({float(sector_rows[0]['return_pct']):+.2f}%).",
            f"Sector laggard: {sector_rows[-1]['symbol']} ({float(sector_rows[-1]['return_pct']):+.2f}%).",
        ]

    macro_rows: list[dict[str, Any]] = []
    for stat in rank_week(macro_stats or []):
        macro_rows.append(
            {
                "symbol": stat.symbol,
                "label": stat.symbol,
                "start_close": stat.start_close,
                "end_close": stat.end_close,
                "display_value": f"{stat.end_close:,.2f}",
                "change_pct": stat.return_pct,
            }
        )

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

    positive_benchmarks = sum(stat.return_pct > 0 for stat in ranked_benchmarks)
    if ranked_benchmarks and positive_benchmarks == len(ranked_benchmarks):
        regime = "All configured benchmarks positive"
    elif ranked_benchmarks and positive_benchmarks == 0:
        regime = "All configured benchmarks negative"
    else:
        regime = "Mixed benchmark performance"

    all_sources = list(sources or ["Massive API"])
    for source in extra_sources or []:
        if source not in all_sources:
            all_sources.append(source)

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
        "sectors": sector_rows,
        "sector_notes": sector_notes,
        "breadth": breadth,
        "breadth_title": "Breadth / participation",
        "breadth_notes": breadth_notes,
        "macro": macro_rows,
        "macro_notes": [
            "Cross-asset changes use the same first-available-close to last-available-close method."
        ] if macro_rows else [],
        "technical": technical or [],
        "technical_notes": [
            "Moving-average distances are calculated from stored daily closes; no support/resistance levels are inferred."
        ] if technical else [],
        "drivers": drivers or [],
        "risks": risks or [],
        "sources": all_sources,
        "final_takeaway": {
            "market_regime": regime,
            "leadership": one_line,
            "key_tension": "Broader context depends on the configured universe and verified research inputs",
            "summary": "The presentation keeps market calculations deterministic and leaves unavailable fields explicit rather than filling them with generated data.",
        },
    }
