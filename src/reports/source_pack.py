from __future__ import annotations

from typing import Any


def _table(rows: list[dict[str, Any]], columns: list[tuple[str, str]]) -> list[str]:
    if not rows:
        return ["Not available in this run.", ""]
    lines = [
        "| " + " | ".join(label for _, label in columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    for row in rows:
        values: list[str] = []
        for key, _ in columns:
            value = row.get(key, "")
            if isinstance(value, float):
                value = f"{value:.2f}"
            values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    lines.append("")
    return lines


def render_notebooklm_source(report: dict[str, Any]) -> str:
    """Render one authoritative Markdown source for NotebookLM/LLM presentation tools."""
    meta = report.get("meta", {})
    lines = [
        "# Sunday Market Recap — Authoritative Source Pack",
        "",
        f"**Report period:** {meta.get('start_date', '')} → {meta.get('end_date', '')}",
        f"**Calculation method:** {meta.get('calculation_method', 'Not specified')}",
        "",
        "> DATA RULE: Numbers and rankings in this file are authoritative. Do not invent missing values, change timeframes, or infer technical levels that are not explicitly supplied.",
        "",
        "## Week in one line",
        "",
        str(report.get("one_line_week", "Not available")),
        "",
        "## Benchmarks",
        "",
    ]
    lines += _table(
        report.get("benchmarks", []) or [],
        [("symbol", "Symbol"), ("start_close", "Start close"), ("end_close", "End close"), ("return_pct", "Return %")],
    )

    sections = [
        ("Highlights", report.get("highlights", [])),
        ("Leadership notes", report.get("leadership_notes", [])),
        ("Sector notes", report.get("sector_notes", [])),
        ("Breadth notes", report.get("breadth_notes", [])),
        ("Macro notes", report.get("macro_notes", [])),
        ("Technical notes", report.get("technical_notes", [])),
    ]
    for heading, items in sections:
        lines += [f"## {heading}", ""]
        if items:
            lines += [f"- {item}" for item in items]
        else:
            lines.append("Not available in this run.")
        lines.append("")

    movers = report.get("movers", {}) or {}
    lines += ["## Top gainers", ""]
    lines += _table(movers.get("gainers", []) or [], [("symbol", "Symbol"), ("return_pct", "Return %"), ("catalyst", "Verified catalyst")])
    lines += ["## Top losers", ""]
    lines += _table(movers.get("losers", []) or [], [("symbol", "Symbol"), ("return_pct", "Return %"), ("catalyst", "Verified catalyst")])

    lines += ["## Sector performance", ""]
    lines += _table(report.get("sectors", []) or [], [("symbol", "Sector"), ("return_pct", "Return %")])

    breadth = report.get("breadth", {}) or {}
    lines += ["## Breadth", ""]
    if breadth:
        for key, value in breadth.items():
            lines.append(f"- **{key}:** {value}")
    else:
        lines.append("Not available in this run.")
    lines.append("")

    lines += ["## Macro & cross-asset", ""]
    lines += _table(report.get("macro", []) or [], [("label", "Asset"), ("display_value", "End value"), ("change_pct", "Period change %")])

    lines += ["## Technical context", ""]
    technical = report.get("technical", []) or []
    if technical:
        for row in technical:
            lines.append(f"- **{row.get('label', 'Metric')}:** {row.get('value', 'Not available')}")
    else:
        lines.append("Not available in this run.")
    lines.append("")

    for heading, key in [("Verified drivers", "drivers"), ("Risks / things to watch", "risks")]:
        lines += [f"## {heading}", ""]
        items = report.get(key, []) or []
        if items:
            for item in items:
                lines.append(f"- **{item.get('title', '')}:** {item.get('detail', '')}")
        else:
            lines.append("Not available in this run.")
        lines.append("")

    final = report.get("final_takeaway", {}) or {}
    lines += [
        "## Final takeaway",
        "",
        f"- **Market regime:** {final.get('market_regime', 'Not available')}",
        f"- **Leadership:** {final.get('leadership', 'Not available')}",
        f"- **Key tension:** {final.get('key_tension', 'Not available')}",
        f"- **Summary:** {final.get('summary', 'Not available')}",
        "",
        "## Sources",
        "",
    ]
    sources = report.get("sources", []) or []
    lines += [f"- {source}" for source in sources] if sources else ["Not supplied."]
    lines.append("")
    return "\n".join(lines)
