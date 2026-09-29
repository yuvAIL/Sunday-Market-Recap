from pathlib import Path

from src.presentation.deck import build_deck


def test_build_deck_creates_pptx(tmp_path: Path):
    report = {
        "meta": {"start_date": "2026-09-21", "end_date": "2026-09-25"},
        "one_line_week": "QQQ led while IWM lagged.",
        "benchmarks": [
            {"symbol": "QQQ", "return_pct": 3.0},
            {"symbol": "SPY", "return_pct": 1.0},
            {"symbol": "IWM", "return_pct": -1.0},
        ],
        "highlights": ["Tech led.", "Small caps lagged."],
        "sources": ["Test source"],
        "final_takeaway": {
            "market_regime": "Mixed",
            "leadership": "Tech",
            "key_tension": "Breadth",
            "summary": "Test.",
        },
    }
    path = build_deck(report, tmp_path / "deck.pptx")
    assert path.exists()
    assert path.stat().st_size > 0
