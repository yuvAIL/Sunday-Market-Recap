from __future__ import annotations

from datetime import date

import pandas as pd


def moving_average_context(
    df: pd.DataFrame,
    *,
    symbol: str,
    end: date,
    windows: tuple[int, ...] = (20, 50, 150, 200),
) -> list[dict[str, str]]:
    """Return deterministic close-vs-SMA context using only stored daily bars."""
    if df.empty:
        return []

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"]).dt.date
    data = data[data["date"] <= end].sort_values("date")
    if data.empty:
        return []

    close = float(data.iloc[-1]["close"])
    result: list[dict[str, str]] = []
    for window in windows:
        if len(data) < window:
            continue
        sma = float(data["close"].astype(float).tail(window).mean())
        distance = (close / sma - 1.0) * 100.0
        result.append(
            {
                "label": f"{symbol} vs {window}D SMA",
                "value": f"{distance:+.2f}%",
            }
        )
    return result
