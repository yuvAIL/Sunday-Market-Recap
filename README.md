# Sunday Market Recap — Data Puller

A Python prototype for the deterministic data layer behind a weekly U.S. market recap. I built it as an AI-assisted/vibe-coding project with Claude, with a deliberate separation between factual market data and any later LLM-generated narrative.

## What it does

The project pulls historical daily OHLCV data from the Massive API for a configurable universe of benchmarks, crypto, FX, commodities and other instruments. It normalizes the data into one schema, stores it as Parquet, and supports re-runnable incremental updates.

The design principle is simple: **data and calculations should come from APIs/code; AI should be used later for summarization and presentation.**

## Architecture

```text
config.yaml → SymbolRegistry → DataPuller → MassiveClient → LocalStorage
                                      ↕
                              incremental gap logic
```

```text
sunday-market-recap/
├── main.py
├── config.yaml
├── requirements.txt
├── .env.example
└── src/
    ├── clients/      # provider abstraction + Massive implementation
    ├── config/       # config loader + symbol registry
    ├── models/       # normalized OHLCV model
    ├── pipelines/    # fetch/orchestration logic
    ├── storage/      # Parquet storage + gap detection
    └── utils/        # logging
```

## Normalized schema

Each daily bar stores:

`symbol`, `asset_class`, `provider`, `provider_symbol`, `date`, `open`, `high`, `low`, `close`, `volume`, `adjusted_close`, `currency`, `fetched_at`.

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

## Usage

List configured symbols without making an API request:

```bash
python main.py --list-groups
```

Pull everything:

```bash
python main.py
```

Pull one group or symbol:

```bash
python main.py --group benchmarks
python main.py --symbol SPY --start 2026-01-01 --end 2026-03-31
```

## Why I built it this way

My first instinct was to let the AI do too much of the market recap directly. That made reliability the weak point: financial values can vary by source, timeframe or interpretation, and an LLM can fill gaps too confidently.

I moved the factual layer into code and an external market-data API. The LLM belongs later in the pipeline, where it can turn already-validated structured data into summaries and presentation copy.

## Current scope / limitations

This repository is the **data-ingestion prototype**, not the complete newsletter product. It intentionally stops before analytics, LLM rendering and scheduled delivery. Some provider symbols and asset classes may require plan-specific Massive support or config changes.

Planned next layers:

1. Analytics: period returns, gainers/losers, shock moves and benchmark comparisons.
2. AI rendering: generate a concise weekly narrative from structured JSON.
3. Presentation: HTML/PDF market report.
4. Delivery: scheduled Sunday run and email/newsletter output.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

The repository also includes a small GitHub Actions workflow that runs the test suite on pushes and pull requests.
