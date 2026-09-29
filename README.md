# Sunday Market Recap

A deterministic-first Python project for generating a weekly U.S. market recap from structured market data.

The core product principle is simple: **financial data and calculations come from APIs/code; AI is allowed later for wording, hierarchy and presentation — never for inventing numbers.**

The original product notes defined the long-term flow as:

```text
Data Puller → Structured Data → Analytics / Ranking → AI Summary → Newsletter → Presentation
```

The repository now implements the data layer, baseline weekly analytics, a structured report payload and a PowerPoint presentation renderer.

## What it does

- Pulls historical daily OHLCV data from the Massive API.
- Supports configurable benchmarks, crypto, FX, commodities and additional symbol groups.
- Normalizes all bars into one schema and stores them in Parquet.
- Supports incremental re-runs.
- Computes weekly returns deterministically.
- Builds a structured JSON presentation payload.
- Renders an 11-slide `.pptx` market recap.
- Includes a detailed master prompt for an optional AI/NotebookLM-style presentation editing layer.
- Runs automated tests through GitHub Actions.

## Architecture

```text
Massive API
    ↓
Data Puller
    ↓
Normalized Parquet Store
    ↓
Weekly Analytics
    ↓
Structured weekly_report.json
    ├──→ PowerPoint renderer → weekly_recap.pptx
    └──→ Presentation master prompt / future AI rendering layer
```

## Presentation structure

The renderer is designed around the original Sunday Market Recap vision:

1. Week at a Glance
2. Major Benchmarks
3. Leadership & Relative Performance
4. Top Movers
5. Sector Performance
6. Breadth / Participation
7. Macro & Cross-Asset Dashboard
8. Technical Context
9. What Drove the Week
10. Risks / What to Watch
11. Final Takeaway

Missing sections are explicitly labeled rather than guessed.

The reconstructed/expanded presentation prompt is stored at:

```text
prompts/presentation_master.md
```

## Project structure

```text
sunday-market-recap/
├── main.py
├── config.yaml
├── requirements.txt
├── .env.example
├── prompts/
│   └── presentation_master.md
├── sample/
│   └── weekly_report.sample.json
├── scripts/
│   ├── build_presentation.py
│   └── generate_weekly_recap.py
└── src/
    ├── analytics/
    ├── clients/
    ├── config/
    ├── models/
    ├── pipelines/
    ├── presentation/
    ├── reports/
    ├── storage/
    └── utils/
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then add your Massive API key to `.env`:

```text
MASSIVE_API_KEY=your_api_key_here
```

Never commit `.env`.

## 1. Pull market data

List configured symbols:

```bash
python main.py --list-groups
```

Pull all configured data:

```bash
python main.py
```

Or pull a selected group/symbol:

```bash
python main.py --group benchmarks
python main.py --symbol SPY --start 2026-01-01 --end 2026-03-31
```

## 2. Generate the weekly recap + PowerPoint

After the Parquet data exists:

```bash
python scripts/generate_weekly_recap.py --start 2026-09-21 --end 2026-09-25
```

This creates:

```text
output/2026-09-21_to_2026-09-25/
├── weekly_report.json
└── weekly_recap.pptx
```

When dates are omitted, the CLI selects the most recent completed Monday–Friday block.

## 3. Render any structured report JSON

```bash
python scripts/build_presentation.py \
  --input sample/weekly_report.sample.json \
  --output output/sample_recap.pptx
```

The sample payload demonstrates richer sections such as breadth, macro context, drivers and risks. Those fields should only be populated by verified data/research in a real run.

## Deterministic data rules

The project intentionally separates facts from narrative:

- Price/return calculations are code-driven.
- Rankings are code-driven.
- Daily and weekly moves must be labeled separately.
- Missing sector/breadth/technical data stays missing.
- Support/resistance is never inferred by the presentation renderer.
- AI may rewrite or compress verified text, but it should not change financial values.

## Current limitations

The configured universe is still relatively small. A full production weekly deck needs additional deterministic inputs for:

- broad stock-mover universe,
- sector returns,
- market breadth,
- moving-average/technical metrics,
- rates and selected macro series,
- verified news/event drivers.

The presentation architecture already supports these fields; the next engineering step is expanding the data/analytics layer that feeds them.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

GitHub Actions runs the test suite on pushes and pull requests.
