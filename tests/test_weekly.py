from datetime import date

import pandas as pd

from src.analytics.weekly import rank_week, weekly_return
from src.reports.weekly import render_markdown


def test_weekly_return_uses_first_and_last_available_close():
    df = pd.DataFrame(
        [
            {"date": "2026-09-21", "close": 100.0},
            {"date": "2026-09-23", "close": 103.0},
            {"date": "2026-09-25", "close": 105.0},
        ]
    )
    stat = weekly_return(df, "TEST", date(2026, 9, 21), date(2026, 9, 25))
    assert stat.start_close == 100.0
    assert stat.end_close == 105.0
    assert round(stat.return_pct, 2) == 5.00


def test_rank_and_render():
    a = weekly_return(
        pd.DataFrame([{"date": "2026-09-21", "close": 100}, {"date": "2026-09-25", "close": 110}]),
        "AAA",
        date(2026, 9, 21),
        date(2026, 9, 25),
    )
    b = weekly_return(
        pd.DataFrame([{"date": "2026-09-21", "close": 100}, {"date": "2026-09-25", "close": 95}]),
        "BBB",
        date(2026, 9, 21),
        date(2026, 9, 25),
    )
    assert [x.symbol for x in rank_week([b, a])] == ["AAA", "BBB"]
    report = render_markdown(date(2026, 9, 21), date(2026, 9, 25), [a, b])
    assert "Leader: **AAA**" in report
    assert "Laggard: **BBB**" in report
