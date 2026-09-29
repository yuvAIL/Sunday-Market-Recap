from datetime import date, datetime, timezone
import importlib.util

import pytest

from src.models.bar import OHLCVBar
from src.storage.local import LocalStorage


def bar(symbol: str, day: date, close: float = 100.0) -> OHLCVBar:
    return OHLCVBar(
        symbol=symbol,
        asset_class="benchmark",
        provider="massive",
        provider_symbol=symbol,
        date=day,
        open=close - 1,
        high=close + 1,
        low=close - 2,
        close=close,
        volume=1_000_000.0,
        adjusted_close=close,
        currency="USD",
        fetched_at=datetime.now(timezone.utc),
    )


def test_missing_ranges_empty_storage(tmp_path):
    storage = LocalStorage(tmp_path)
    assert storage.missing_ranges(
        "benchmarks", "SPY", date(2026, 1, 1), date(2026, 1, 3)
    ) == [(date(2026, 1, 1), date(2026, 1, 3))]


def test_missing_ranges_uses_watermarks(tmp_path, monkeypatch):
    storage = LocalStorage(tmp_path)
    monkeypatch.setattr(
        storage,
        "covered_dates",
        lambda group, symbol: {date(2026, 1, 2), date(2026, 1, 5)},
    )

    assert storage.missing_ranges(
        "benchmarks", "SPY", date(2026, 1, 2), date(2026, 1, 5)
    ) == []


def test_missing_ranges_can_extend_both_sides(tmp_path, monkeypatch):
    storage = LocalStorage(tmp_path)
    monkeypatch.setattr(
        storage,
        "covered_dates",
        lambda group, symbol: {date(2026, 1, 5), date(2026, 1, 9)},
    )

    assert storage.missing_ranges(
        "benchmarks", "SPY", date(2026, 1, 1), date(2026, 1, 12)
    ) == [
        (date(2026, 1, 1), date(2026, 1, 4)),
        (date(2026, 1, 10), date(2026, 1, 12)),
    ]


@pytest.mark.skipif(
    importlib.util.find_spec("pyarrow") is None,
    reason="pyarrow is installed with project requirements",
)
def test_upsert_deduplicates_by_symbol_and_date(tmp_path):
    storage = LocalStorage(tmp_path)
    storage.upsert("benchmarks", "SPY", [bar("SPY", date(2026, 1, 5), 100.0)])
    storage.upsert("benchmarks", "SPY", [bar("SPY", date(2026, 1, 5), 105.0)])

    df = storage.read("benchmarks", "SPY")
    assert len(df) == 1
    assert float(df.iloc[0]["close"]) == 105.0
