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


def weekly_return(df: pd.DataFrame, symbol: str, start: date, end: date) -> WeeklyStat:
    if df.empty:
        raise ValueError(f"No data available for {symbol}")

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"]).dt.date
    data = data[(data["date"] >= start) & (data["date"] <= end)].sort_values("date")
    if data.empty:
        raise ValueError(f"No rows for {symbol} between {start} and {end}")

    start_close = float(data.iloc[0]["close"])
    end_close = float(data.iloc[-1]["close"])
    return WeeklyStat(
        symbol=symbol,
        start_close=start_close,
        end_close=end_close,
        return_pct=(end_close / start_close - 1.0) * 100.0,
    )


def rank_week(stats: Iterable[WeeklyStat]) -> list[WeeklyStat]:
    return sorted(stats, key=lambda item: item.return_pct, reverse=True)
