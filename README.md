# Sunday Market Recap

A deterministic-first Python project for generating a weekly U.S. market recap from structured market data.

The core product principle is simple: **financial data and calculations come from APIs/code; AI is allowed later for wording, hierarchy and presentation — never for inventing numbers.**

The original product notes defined the long-term flow as:

```text
Data Puller → Structured Data → Analytics / Ranking → AI Summary → Newsletter → Presentation
```

The repository now implements the data layer, weekly analytics, structured presentation payload, NotebookLM-ready source pack and PowerPoint renderer.

## What it does

- Pulls historical daily OHLCV data from the Massive API.
- Supports configurable benchmarks, equities, sectors, crypto, FX, commodities and macro symbols.
- Normalizes all bars into one schema and stores them in Parquet.
- Supports incremental re-runs.
- Computes weekly returns and relative benchmark spreads deterministically.
- Computes configured-universe breadth and SPY moving-average context when data exists.
- Builds a structured `weekly_report.json`.
- Builds an authoritative `notebooklm_source.md` for NotebookLM/LLM presentation workflows.
- Renders an 11-slide `.pptx` market recap directly from the same structured data.
- Accepts optional verified research context for drivers/risks without mixing it into market calculations.
- Includes a detailed presentation master prompt and automated tests.

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
    ├──→ Source-pack renderer → notebooklm_source.md
    └──→ Presentation master prompt / optional AI editing layer
```

## Presentation structure

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

```bash
python main.py --list-groups
python main.py
```

Or pull a selected group/symbol:

```bash
python main.py --group benchmarks
python main.py --symbol SPY --start 2026-01-01 --end 2026-03-31
```

## 2. Generate the weekly recap package

After Parquet data exists:

```bash
python scripts/generate_weekly_recap.py --start 2026-09-21 --end 2026-09-25
```

This creates:

```text
output/2026-09-21_to_2026-09-25/
├── weekly_report.json
├── notebooklm_source.md
└── weekly_recap.pptx
```

When dates are omitted, the CLI selects the most recent completed Monday–Friday block.

### Add verified news/event context

Keep market math deterministic and pass researched context separately:

```bash
python scripts/generate_weekly_recap.py \
  --start 2026-09-21 \
  --end 2026-09-25 \
  --context sample/verified_context.sample.json
```

The context file supports `drivers`, `risks` and `extra_sources`.

## 3. Render any structured report JSON

PowerPoint:

```bash
python scripts/build_presentation.py \
  --input sample/weekly_report.sample.json \
  --output output/sample_recap.pptx
```

NotebookLM source pack:

```bash
python scripts/build_source_pack.py \
  --input sample/weekly_report.sample.json \
  --output output/notebooklm_source.md
```

## Deterministic data rules

- Price/return calculations are code-driven.
- Rankings and benchmark spreads are code-driven.
- Daily and weekly moves must be labeled separately.
- Missing sector/breadth/technical data stays missing.
- Support/resistance is never inferred by the renderer.
- Moving-average context uses stored daily closes.
- AI may rewrite or compress verified text, but it should not change financial values.

## Current limitations

The presentation pipeline is in place, but the quality of a production weekly deck still depends on the configured data universe. Richer results require broader equity/sector coverage and verified research inputs for market drivers. The renderer intentionally exposes missing sections instead of fabricating them.

## Tests

```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
```

GitHub Actions runs the test suite on pushes and pull requests.
