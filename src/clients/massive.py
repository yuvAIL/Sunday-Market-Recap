from __future__ import annotations

import time
from datetime import date, datetime, timezone
from typing import Any

import requests

from src.clients.base import BaseClient
from src.models.bar import OHLCVBar


class MassiveClient(BaseClient):
    provider_name = "massive"
    base_url = "https://api.massive.com"

    def __init__(self, api_key: str | None, *, timeout: int = 30, max_retries: int = 3) -> None:
        if not api_key:
            raise ValueError(
                "MASSIVE_API_KEY is missing. Copy .env.example to .env and add your key."
            )
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def _get_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(
                    url,
                    params={**params, "apiKey": self.api_key},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                payload = response.json()
                if payload.get("status") == "ERROR":
                    raise RuntimeError(payload.get("error") or payload.get("message") or "API error")
                return payload
            except (requests.RequestException, ValueError, RuntimeError) as exc:
                last_error = exc
                if attempt == self.max_retries:
                    break
                time.sleep(2 ** (attempt - 1))

        raise RuntimeError(f"Massive request failed after {self.max_retries} attempts: {last_error}")

    def fetch_daily_bars(
        self,
        *,
        canonical_symbol: str,
        provider_symbol: str,
        asset_class: str,
        currency: str | None,
        start: date,
        end: date,
    ) -> list[OHLCVBar]:
        path = (
            f"/v2/aggs/ticker/{provider_symbol}/range/1/day/"
            f"{start.isoformat()}/{end.isoformat()}"
        )
        payload = self._get_json(
            path,
            {"adjusted": "true", "sort": "asc", "limit": 50000},
        )

        fetched_at = datetime.now(timezone.utc)
        bars: list[OHLCVBar] = []
        for row in payload.get("results", []) or []:
            timestamp_ms = row.get("t")
            if timestamp_ms is None:
                continue
            bar_date = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).date()
            bars.append(
                OHLCVBar(
                    symbol=canonical_symbol,
                    asset_class=asset_class,
                    provider=self.provider_name,
                    provider_symbol=provider_symbol,
                    date=bar_date,
                    open=float(row["o"]),
                    high=float(row["h"]),
                    low=float(row["l"]),
                    close=float(row["c"]),
                    volume=float(row["v"]) if row.get("v") is not None else None,
                    adjusted_close=float(row["c"]),
                    currency=currency,
                    fetched_at=fetched_at,
                )
            )
        return bars
