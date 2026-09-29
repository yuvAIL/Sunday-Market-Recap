from __future__ import annotations

from datetime import date

from src.analytics.weekly import WeeklyStat, rank_week


def render_markdown(start: date, end: date, stats: list[WeeklyStat]) -> str:
    ranked = rank_week(stats)
    lines = [
        f"# Sunday Market Recap | {start.isoformat()} → {end.isoformat()}",
        "",
        "## Market snapshot",
        "",
        "| Symbol | Start close | End close | Weekly return |",
        "|---|---:|---:|---:|",
    ]
    for stat in ranked:
        lines.append(
            f"| {stat.symbol} | {stat.start_close:.2f} | {stat.end_close:.2f} | "
            f"{stat.return_pct:+.2f}% |"
        )

    if ranked:
        lines.extend(
            [
                "",
                "## What stood out",
                "",
                f"- Leader: **{ranked[0].symbol}** ({ranked[0].return_pct:+.2f}%).",
                f"- Laggard: **{ranked[-1].symbol}** ({ranked[-1].return_pct:+.2f}%).",
            ]
        )
    return "\n".join(lines) + "\n"
