from datetime import date

from src.analytics.weekly import WeeklyStat
from src.reports.payload import build_weekly_payload


def test_payload_builds_relative_spreads_and_movers():
    payload = build_weekly_payload(
        start=date(2026, 9, 21),
        end=date(2026, 9, 25),
        benchmark_stats=[
            WeeklyStat("SPY", 100, 101, 1.0),
            WeeklyStat("QQQ", 100, 103, 3.0),
            WeeklyStat("IWM", 100, 99, -1.0),
        ],
        equity_stats=[
            WeeklyStat("AAA", 100, 110, 10.0),
            WeeklyStat("BBB", 100, 90, -10.0),
        ],
    )
    spreads = {row["label"]: row["value_pct"] for row in payload["relative_performance"]}
    assert spreads["QQQ vs SPY"] == 2.0
    assert payload["movers"]["gainers"][0]["symbol"] == "AAA"
    assert payload["movers"]["losers"][0]["symbol"] == "BBB"
