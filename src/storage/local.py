from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from src.models.bar import OHLCVBar


class LocalStorage:
    """Parquet-backed local storage for normalized market bars.

    Incremental updates use the stored date range as a watermark rather than
    assuming every calendar day should contain a bar. That matters because
    trading calendars differ across equities, FX and crypto, and market
    holidays/weekends should not be treated as permanent data gaps.
    """

    def __init__(self, root: Path) -> None:
        self.root = root

    def path_for(self, group: str, symbol: str) -> Path:
        return self.root / group / f"{symbol}.parquet"

    def read(self, group: str, symbol: str) -> pd.DataFrame:
        path = self.path_for(group, symbol)
        if not path.exists():
            return pd.DataFrame()
        return pd.read_parquet(path)

    def covered_dates(self, group: str, symbol: str) -> set[date]:
        existing = self.read(group, symbol)
        if existing.empty or "date" not in existing.columns:
            return set()
        return set(pd.to_datetime(existing["date"]).dt.date.tolist())

    def missing_ranges(
        self, group: str, symbol: str, start: date, end: date
    ) -> list[tuple[date, date]]:
        """Return leading/trailing ranges that are outside stored coverage.

        Internal missing calendar dates are intentionally ignored because a
        generic data layer cannot know whether a date is a true gap, a weekend,
        or an exchange holiday for every asset class. A future provider-aware
        trading-calendar layer can add deeper gap repair.
        """
        if start > end:
            return []

        covered = self.covered_dates(group, symbol)
        if not covered:
            return [(start, end)]

        first_stored = min(covered)
        last_stored = max(covered)
        missing: list[tuple[date, date]] = []

        if start < first_stored:
            leading_end = min(end, first_stored - timedelta(days=1))
            if start <= leading_end:
                missing.append((start, leading_end))

        if end > last_stored:
            trailing_start = max(start, last_stored + timedelta(days=1))
            if trailing_start <= end:
                missing.append((trailing_start, end))

        return missing

    def upsert(self, group: str, symbol: str, bars: list[OHLCVBar]) -> Path:
        path = self.path_for(group, symbol)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not bars:
            return path

        new_df = pd.DataFrame([bar.to_dict() for bar in bars])
        existing = self.read(group, symbol)
        combined = (
            pd.concat([existing, new_df], ignore_index=True)
            if not existing.empty
            else new_df
        )
        combined["date"] = pd.to_datetime(combined["date"]).dt.date
        combined["fetched_at"] = pd.to_datetime(combined["fetched_at"], utc=True)
        combined = combined.sort_values(["symbol", "date", "fetched_at"])
        combined = combined.drop_duplicates(subset=["symbol", "date"], keep="last")
        combined = combined.sort_values("date").reset_index(drop=True)
        combined.to_parquet(path, index=False)
        return path
