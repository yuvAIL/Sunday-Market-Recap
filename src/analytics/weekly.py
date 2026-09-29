from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class WeeklyStat:
    symbol: str
    start_close: float
    end_close: float
    return_pct: float
    baseline_date: date | None = None
    end_date: date | None = None


def weekly_return(df: pd.DataFrame, symbol: str, start: date, end: date) -> WeeklyStat:
    """Calculate standard week-over-week return.

    The preferred baseline is the last available close before ``start`` (normally
    the prior Friday close). The ending value is the last available close on or
    before ``end`` within the requested period. If historical data before
    ``start`` is unavailable, the function falls back to the first close inside
    the requested period and records that baseline date explicitly.
    """
    if df.empty:
        raise ValueError(f"No data available for {symbol}")

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"]).dt.date
    data = data.sort_values("date")

    period = data[(data["date"] >= start) & (data["date"] <= end)]
    if period.empty:
        raise ValueError(f"No rows for {symbol} between {start} and {end}")

    prior = data[data["date"] < start]
    baseline_row = prior.iloc[-1] if not prior.empty else period.iloc[0]
    end_row = period.iloc[-1]

    start_close = float(baseline_row["close"])
    end_close = float(end_row["close"])
    return WeeklyStat(
        symbol=symbol,
        start_close=start_close,
        end_close=end_close,
        return_pct=(end_close / start_close - 1.0) * 100.0,
        baseline_date=baseline_row["date"],
        end_date=end_row["date"],
    )


def rank_week(stats: Iterable[WeeklyStat]) -> list[WeeklyStat]:
    return sorted(stats, key=lambda item: item.return_pct, reverse=True)
